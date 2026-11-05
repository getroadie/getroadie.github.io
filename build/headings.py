import fitz, sys
doc = fitz.open(sys.argv[1])
for p in doc:
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            t = "".join(s["text"] for s in l["spans"]).strip()
            if not t: continue
            s = l["spans"][0]
            sz = round(s["size"],1)
            if sz >= 11.0 and sz != 12.0 or (sz==12.0 and False):
                print(p.number+1, sz, "B" if "Bold" in s["font"] else "-", hex(s["color"]), t[:70])
