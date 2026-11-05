import fitz, collections, sys
doc = fitz.open(sys.argv[1])
print("pages", doc.page_count)
sizes = collections.Counter()
for p in doc:
    for b in p.get_text("dict")["blocks"]:
        for l in b.get("lines", []):
            for s in l["spans"]:
                if s["text"].strip():
                    sizes[(round(s["size"],1), "Bold" in s["font"] or "bold" in s["font"].lower())] += len(s["text"])
for k,v in sorted(sizes.items(), key=lambda x:-x[0][0])[:25]:
    print(k, v)
imgs = [(p.number+1, len(p.get_images()), len(p.get_drawings())) for p in doc]
print("pages with images:", sum(1 for x in imgs if x[1]), "total imgs", sum(x[1] for x in imgs))
print([x for x in imgs if x[0] in range(20,45)])
