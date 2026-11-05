"""Extract the Alberta Driver's Guide PDF into structured data for the app.

Outputs (under data/):
  handbook.json      chapters -> sections (text) + per-page text, for reader + search
  text/chNN.txt      plain text per chapter with page markers, for question writers
  pages/pNNN.webp    rendered page images for the reader's "original page" view
  figs/pNNN_fK.png   cropped figure clusters (signs, diagrams)
  annot/pNNN.png     page render with numbered boxes around each figure crop
"""
import fitz, json, os, re, sys
from PIL import Image, ImageDraw, ImageFont

PDF = sys.argv[1]
OUT = sys.argv[2]
ORANGE = 0xC88A11
PAGE_ZOOM = 2.0
FIG_ZOOM = 4.0

doc = fitz.open(PDF)
for sub in ("text", "pages", "figs", "annot"):
    os.makedirs(os.path.join(OUT, sub), exist_ok=True)

PUA = re.compile("[-]")


def clean(t):
    t = PUA.sub("", t)
    t = t.replace("­", "").replace(" ", " ")
    return re.sub(r"[ \t]+", " ", t).strip()


def line_text(line):
    return clean("".join(s["text"] for s in line["spans"]))


def is_heading(line):
    s = line["spans"][0]
    return 15.0 <= s["size"] <= 17.0 and s["color"] == ORANGE


def is_chapter_title(line):
    s = line["spans"][0]
    return s["size"] >= 29 and s["color"] == 0xFFFFFF


def block_items(page):
    """Return reading-ordered list of (kind, text, bbox) for a page."""
    H = page.rect.height
    mid = page.rect.width / 2
    blocks = [b for b in page.get_text("dict")["blocks"] if b.get("lines")]
    # two-column reading order: column by x0, then top-down
    def key(b):
        x0, y0, x1, y1 = b["bbox"]
        full = (x1 - x0) > page.rect.width * 0.6
        col = 0 if (full or x0 < mid - 10) else 1
        return (col, y0)
    blocks.sort(key=key)
    items = []
    for b in blocks:
        lines = [l for l in b["lines"] if line_text(l)]
        if not lines:
            continue
        # drop running footer / page number
        if b["bbox"][1] > H - 30:
            continue
        cur_kind, cur = None, []
        def flush():
            if cur:
                txt = ""
                for t in cur:
                    if not txt:
                        txt = t
                    elif txt.endswith("-") and t[:1].islower():
                        txt += t
                    else:
                        txt += " " + t
                items.append((cur_kind, txt, b["bbox"]))
        for l in lines:
            t = line_text(l)
            if is_chapter_title(l):
                k = "chapter"
            elif is_heading(l):
                k = "heading"
            elif t.startswith("•"):
                k = "bullet"
                t = t.lstrip("• ").strip()
            else:
                k = "para"
            if k == "bullet" or k != cur_kind or (k == "para" and cur_kind == "bullet"):
                if not (k == "para" and cur_kind == "bullet"):
                    flush()
                    cur_kind, cur = k, [t]
                    continue
                # continuation line of a bullet
                cur.append(t)
                continue
            cur.append(t)
        flush()
    return items


# ---- chapters from the Contents + opener pages ---------------------------
CHAPTERS = [
    (1, "Licensing Information"), (2, "Traffic Control"), (3, "The Basics of Driving"),
    (4, "Intersections and Turns"), (5, "Highways and Freeways"),
    (6, "Emergency Situations and Challenging Conditions"), (7, "Responsible Driving"),
    (8, "Sharing the Road"), (9, "Driving within the Law"), (10, "Towing a Trailer"),
]
openers = {}
for p in doc:
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            s = l["spans"][0]
            t = line_text(l)
            if s["size"] >= 47 and t.isdigit() and p.number + 1 > 9:
                openers[int(t)] = p.number + 1
assert len(openers) == 10, openers

chapters = []
for n, title in CHAPTERS:
    start = openers[n]
    end = openers[n + 1] - 1 if n < 10 else doc.page_count
    chapters.append({"n": n, "title": title, "start": start, "end": end, "sections": []})

# Front matter (Introduction etc.) kept as chapter 0 for the reader only
front = {"n": 0, "title": "Introduction", "start": 4, "end": openers[1] - 1, "sections": []}

pages_out = []
sec_counter = 0
for ch in [front] + chapters:
    cur = None
    for pno in range(ch["start"], ch["end"] + 1):
        page = doc[pno - 1]
        items = block_items(page)
        ptext = []
        pending_heading = None
        for kind, txt, bbox in items:
            if kind == "chapter":
                continue
            if kind == "heading":
                # merge multi-line headings that arrive as consecutive items
                if pending_heading is not None:
                    pending_heading += " " + txt
                else:
                    pending_heading = txt
                continue
            if pending_heading is not None:
                sec_counter += 1
                title = re.sub(r"\s+", " ", pending_heading).strip().rstrip(":")
                title = title[0].upper() + title[1:].replace("licenCe", "licence")
                cur = {"id": f"s{sec_counter:03d}", "title": title, "page": pno, "end": pno, "blocks": []}
                ch["sections"].append(cur)
                pending_heading = None
                ptext.append("## " + title)
            if cur is None:
                sec_counter += 1
                cur = {"id": f"s{sec_counter:03d}", "title": ch["title"] if ch["n"] else "Introduction",
                       "page": pno, "end": pno, "blocks": []}
                ch["sections"].append(cur)
            cur["end"] = pno
            cur["blocks"].append({"k": kind[0], "t": txt, "p": pno})
            ptext.append(("- " if kind == "bullet" else "") + txt)
        if pending_heading is not None:  # heading at very bottom of page
            sec_counter += 1
            title = re.sub(r"\s+", " ", pending_heading).strip().rstrip(":")
            cur = {"id": f"s{sec_counter:03d}", "title": title, "page": pno, "end": pno, "blocks": []}
            ch["sections"].append(cur)
            ptext.append("## " + title)
        pages_out.append({"n": pno, "ch": ch["n"], "text": "\n".join(ptext)})

# ---- per-chapter text files for question writers --------------------------
for ch in chapters:
    lines = [f"# Chapter {ch['n']}: {ch['title']}  (pages {ch['start']}-{ch['end']})", ""]
    for pg in pages_out:
        if pg["ch"] == ch["n"]:
            lines.append(f"=== Page {pg['n']} ===")
            lines.append(pg["text"])
            lines.append("")
    with open(os.path.join(OUT, "text", f"ch{ch['n']:02d}.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ---- page images ----------------------------------------------------------
for pno in range(1, doc.page_count + 1):
    pix = doc[pno - 1].get_pixmap(matrix=fitz.Matrix(PAGE_ZOOM, PAGE_ZOOM))
    img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    img.save(os.path.join(OUT, "pages", f"p{pno:03d}.webp"), "WEBP", quality=62, method=6)

# ---- figure clusters (signs / diagrams) -----------------------------------
figs = []
try:
    font = ImageFont.truetype("arialbd.ttf", 22)
except OSError:
    font = ImageFont.load_default()
for pno in range(openers[1], doc.page_count + 1):
    page = doc[pno - 1]
    W, H = page.rect.width, page.rect.height
    try:
        rects = page.cluster_drawings(x_tolerance=4, y_tolerance=4)
    except Exception:
        rects = []
    keep = []
    for r in rects:
        if r.width < 14 or r.height < 14:
            continue
        if r.width > W * 0.92 or r.height > H * 0.8:
            continue
        if r.y0 > H - 32:  # footer art
            continue
        keep.append(r)
    for img in page.get_image_info():
        r = fitz.Rect(img["bbox"])
        if r.width >= 14 and r.height >= 14 and r.width < W * 0.92:
            keep.append(r)
    if not keep:
        continue
    keep.sort(key=lambda r: (0 if r.x0 < W / 2 - 10 else 1, r.y0))
    pix = page.get_pixmap(matrix=fitz.Matrix(PAGE_ZOOM, PAGE_ZOOM))
    ann = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
    dr = ImageDraw.Draw(ann)
    for k, r in enumerate(keep, 1):
        fid = f"p{pno:03d}_f{k}"
        clip = fitz.Rect(r.x0 - 5, r.y0 - 5, r.x1 + 5, r.y1 + 5) & page.rect
        fp = page.get_pixmap(matrix=fitz.Matrix(FIG_ZOOM, FIG_ZOOM), clip=clip)
        fp.save(os.path.join(OUT, "figs", fid + ".png"))
        figs.append({"id": fid, "page": pno, "bbox": [round(v, 1) for v in clip]})
        z = PAGE_ZOOM
        dr.rectangle([r.x0 * z, r.y0 * z, r.x1 * z, r.y1 * z], outline=(230, 0, 0), width=3)
        dr.rectangle([r.x0 * z, r.y0 * z - 24, r.x0 * z + 34, r.y0 * z], fill=(230, 0, 0))
        dr.text((r.x0 * z + 3, r.y0 * z - 24), str(k), fill=(255, 255, 255), font=font)
    ann.save(os.path.join(OUT, "annot", f"p{pno:03d}.png"))

meta = {
    "title": "Driver's Guide: Cars and Light Trucks",
    "publisher": "Government of Alberta, Transportation and Economic Corridors",
    "edition": "June 15, 2026",
    "source": "https://open.alberta.ca/publications/drivers-guide",
    "licence": "Open Government Licence - Alberta",
    "licence_url": "https://open.alberta.ca/licence",
    "pages": doc.page_count,
}
with open(os.path.join(OUT, "handbook.json"), "w", encoding="utf-8") as f:
    json.dump({"meta": meta, "chapters": [front] + chapters, "pages": pages_out, "figs": figs},
              f, ensure_ascii=False)
print("chapters", len(chapters), "sections", sum(len(c["sections"]) for c in [front] + chapters),
      "figs", len(figs))
