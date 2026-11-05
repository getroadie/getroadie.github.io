"""Assemble the app: template + handbook + verified questions + images.

Writes two builds:
  docs/index.html (+ docs/pages/*.webp)        web version for GitHub Pages (images load on demand)
  dist/Alberta_Learners_Practice.html          offline single file (also copied to docs/ for download)

usage: python build_app.py <repo root>
"""
import base64, glob, io, json, os, shutil, sys
from PIL import Image

ROOT = sys.argv[1]
D = os.path.join(ROOT, "data")
hb = json.load(open(os.path.join(D, "handbook.json"), encoding="utf-8"))

# reader content: drop the Contents pages and empty chapter-opener stubs
chapters = []
for c in hb["chapters"]:
    secs = [s for s in c["sections"] if s["title"] != "Contents" and sum(len(b["t"]) for b in s["blocks"]) > 20]
    chapters.append({k: c[k] for k in ("n", "title", "start", "end")} | {"sections": secs})
valid_secs = {s["id"] for c in chapters for s in c["sections"]}
HB = {"meta": hb["meta"], "chapters": [c | {"sections": [{k: s[k] for k in ("id", "title", "page", "end")} for s in c["sections"]]}
                                       for c in chapters]}
words = json.load(open(os.path.join(D, "words.json"), encoding="utf-8"))
vp = os.path.join(D, "videos.json")
VIDEOS = [{k: v.get(k) for k in ("ch", "id", "title", "channel", "minutes")} for v in json.load(open(vp, encoding="utf-8"))] if os.path.exists(vp) else []

# questions: all files, minus mechanical failures, minus verifier rejections
mech = {}
mp = os.path.join(D, "verify", "mechanical.json")
if os.path.exists(mp):
    mech = json.load(open(mp, encoding="utf-8"))
PREVIEW = "--preview" in sys.argv   # preview builds include questions not yet independently verified
approved, rejected = set(), set()
for f in glob.glob(os.path.join(D, "verify", "review_*.json")):
    for v in json.load(open(f, encoding="utf-8")):
        (approved if v.get("verdict") == "ok" else rejected).add(v["id"])
QS = []
for f in sorted(glob.glob(os.path.join(D, "questions", "*.json"))):
    for q in json.load(open(f, encoding="utf-8")):
        if q["id"] in mech or q["id"] in rejected or q["sec"] not in valid_secs:
            continue
        if q["id"] not in approved and not PREVIEW:
            continue
        QS.append({k: q.get(k) for k in ("id", "ch", "sec", "page", "type", "img", "q", "choices", "answer",
                                         "hint", "explain", "quote")})


def b64_webp(img, q=62):
    buf = io.BytesIO()
    img.save(buf, "WEBP", quality=q, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


SITE = os.path.join(ROOT, "docs")  # GitHub Pages serves /docs on main
os.makedirs(os.path.join(SITE, "pages"), exist_ok=True)
PAGES_INLINE, PAGES_WEB = {}, {}
for c in chapters:
    for p in range(c["start"], c["end"] + 1):
        fp = os.path.join(D, "pages", f"p{p:03d}.webp")
        if os.path.exists(fp):
            PAGES_INLINE[p] = "data:image/webp;base64," + base64.b64encode(open(fp, "rb").read()).decode()
            shutil.copyfile(fp, os.path.join(SITE, "pages", f"p{p:03d}.webp"))
            PAGES_WEB[p] = f"pages/p{p:03d}.webp"

FIGS = {}
for q in QS:
    if q["img"] and q["img"] not in FIGS:
        im = Image.open(os.path.join(D, "figs", q["img"] + ".png")).convert("RGB")
        if im.width > 480:
            im = im.resize((480, round(im.height * 480 / im.width)), Image.LANCZOS)
        FIGS[q["img"]] = b64_webp(im, 80)

bp_path = os.path.join(D, "blueprint.json")
BLUEPRINT = json.load(open(bp_path, encoding="utf-8")) if os.path.exists(bp_path) else {
    "signCount": 6, "chapterQuota": {"1": 3, "2": 4, "3": 3, "4": 5, "5": 2, "6": 2, "7": 2, "8": 4, "9": 4, "10": 1}}
LINKS = {"official": [], "other": []}
for key, fn in (("official", "links_official.json"), ("other", "links_other.json")):
    fp = os.path.join(D, fn)
    if os.path.exists(fp):
        LINKS[key] = json.load(open(fp, encoding="utf-8"))

import re as _re
JOKE_BANK, _seen = [], set()
for jf in ("jokes.json", "jokes2.json"):
    jp = os.path.join(D, jf)
    if os.path.exists(jp):
        for j in json.load(open(jp, encoding="utf-8")):
            k = _re.sub(r"[^a-z0-9]+", "", j.lower())
            if k and k not in _seen and "—" not in j:
                _seen.add(k); JOKE_BANK.append(j.replace("Mo the Moose", "Big Doug"))
sp = os.path.join(D, "supabase.json")
SUPA = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else None
DOUG = ("const BD_PLATE = " + json.dumps(json.load(open(os.path.join(D, "brand", "brand.json"), encoding="utf-8"))["plate"]) + ";\n"
        + open(os.path.join(ROOT, "src", "big_doug.js"), encoding="utf-8").read())
tpl = open(os.path.join(ROOT, "src", "app_template.html"), encoding="utf-8").read()
import urllib.parse
brand = json.load(open(os.path.join(D, "brand", "brand.json"), encoding="utf-8"))
tpl = tpl.replace("<!--PLATE-->", brand["plate"].replace(' xmlns="http://www.w3.org/2000/svg"', ""))
fav = "data:image/svg+xml," + urllib.parse.quote(brand["icon"])
ICONS_OFF = f'<link rel="icon" href="{fav}">'
ICONS_WEB = ICONS_OFF + '\n<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n<link rel="manifest" href="manifest.webmanifest">'
json.dump({"name": "Roadie: Alberta Learner's Test Prep", "short_name": "Roadie", "start_url": ".", "display": "standalone",
           "background_color": "#f4f6fa", "theme_color": "#12305b",
           "icons": [{"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
                     {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"}]},
          open(os.path.join(ROOT, "docs", "manifest.webmanifest"), "w", encoding="utf-8"))


WORDS = {"w": words["w"], "h": words["h"], "pages": {str(p): words["pages"][str(p)] for p in PAGES_WEB if str(p) in words["pages"]}}


def render(pages, offline):
    data = (("HB", HB), ("QS", QS), ("PAGES", pages), ("WORDS", WORDS), ("FIGS", FIGS), ("BLUEPRINT", BLUEPRINT),
            ("LINKS", LINKS), ("VIDEOS", VIDEOS), ("JOKE_BANK", JOKE_BANK), ("SUPA", None if offline else SUPA),
            ("OFFLINE", offline))
    js = "\n".join(f"const {k} = {json.dumps(v, ensure_ascii=False, separators=(',', ':'))};" for k, v in data)
    return (tpl.replace("<!--ICONS-->", ICONS_OFF if offline else ICONS_WEB)
               .replace("/*__DOUG__*/", DOUG.replace("</", "<\\/"))
               .replace("/*__DATA__*/", js.replace("</", "<\\/")))


os.makedirs(os.path.join(ROOT, "dist"), exist_ok=True)
off = render(PAGES_INLINE, True)
open(os.path.join(ROOT, "dist", "Alberta_Learners_Practice.html"), "w", encoding="utf-8").write(off)
open(os.path.join(SITE, "Alberta_Learners_Practice_offline.html"), "w", encoding="utf-8").write(off)
web = render(PAGES_WEB, False)
open(os.path.join(SITE, "index.html"), "w", encoding="utf-8").write(web)
open(os.path.join(SITE, ".nojekyll"), "w").close()
print(f"offline {len(off)/1e6:.1f} MB | web index {len(web)/1e6:.2f} MB | questions={len(QS)} "
      f"signs={sum(1 for q in QS if q['type']=='sign')} figs={len(FIGS)} pages={len(PAGES_WEB)}")
