"""Word boxes + sharper page renders for the page-image reader.

data/words.json : {pdf_page: [[word, x0, y0, x1, y1], ...]} in PDF points, reading order
data/pages/pNNN.webp re-rendered at PAGE_ZOOM
"""
import fitz, json, os, re, sys
from PIL import Image

PDF, OUT = sys.argv[1], sys.argv[2]
PAGE_ZOOM = 2.5
doc = fitz.open(PDF)
W = doc[0].rect.width
PUA = re.compile("[-­]")
words = {}
for page in doc:
    n = page.number + 1
    if n < 4:
        continue
    H = page.rect.height
    ws = []
    for x0, y0, x1, y1, w, b, l, k in page.get_text("words"):
        w = PUA.sub("", w)
        if not w or y0 > H - 30:
            continue
        ws.append([w, round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)])
    words[n] = ws
    pix = page.get_pixmap(matrix=fitz.Matrix(PAGE_ZOOM, PAGE_ZOOM))
    Image.frombytes("RGB", (pix.width, pix.height), pix.samples).save(
        os.path.join(OUT, "pages", f"p{n:03d}.webp"), "WEBP", quality=60, method=6)
json.dump({"w": round(W, 1), "h": round(doc[0].rect.height, 1), "pages": words},
          open(os.path.join(OUT, "words.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("pages", len(words), "words", sum(len(v) for v in words.values()))
