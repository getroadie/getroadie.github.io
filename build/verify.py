"""Mechanical checks on question files. Every question must prove itself against the guide.

usage: python verify.py data            -> checks data/questions/*.json, writes data/verify/mechanical.json
       python verify.py data FILE.json  -> checks one file, prints problems (for question writers)
"""
import json, os, re, sys, glob, collections

DATA = sys.argv[1]
hb = json.load(open(os.path.join(DATA, "handbook.json"), encoding="utf-8"))
PAGE = {p["n"]: p["text"] for p in hb["pages"]}
SECS = {s["id"]: (c["n"], s) for c in hb["chapters"] for s in c["sections"]}
CHR = {c["n"]: (c["start"], c["end"]) for c in hb["chapters"]}
FIGS = {f["id"] for f in hb["figs"]}
BANNED = re.compile(r"\b(all of the above|none of the above|both (a|b)|a and b|all of these|none of these)\b", re.I)


def norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"[^a-z0-9]+", "", s)


def check(q):
    errs = []
    for k in ("id", "ch", "sec", "page", "type", "q", "choices", "answer", "hint", "explain", "quote"):
        if k not in q or q[k] in (None, ""):
            errs.append(f"missing {k}")
    if errs:
        return errs
    ch, page = q["ch"], q["page"]
    if ch not in CHR:
        errs.append(f"bad chapter {ch}")
    elif not (CHR[ch][0] <= page <= CHR[ch][1]):
        errs.append(f"page {page} outside chapter {ch} range {CHR[ch]}")
    if q["sec"] not in SECS:
        errs.append(f"unknown section {q['sec']}")
    else:
        sch, s = SECS[q["sec"]]
        if sch != ch:
            errs.append(f"section {q['sec']} is in chapter {sch}, not {ch}")
        if not (s["page"] - 1 <= page <= s["end"] + 1):
            errs.append(f"page {page} not within section {q['sec']} pages {s['page']}-{s['end']}")
    ch_ = q["choices"]
    if not isinstance(ch_, list) or len(ch_) != 4:
        errs.append("need exactly 4 choices")
    else:
        if len({norm(c) for c in ch_}) != 4:
            errs.append("duplicate choices")
        for c in ch_:
            if BANNED.search(c):
                errs.append(f"banned choice wording: {c!r} (choices are shuffled)")
        if not isinstance(q["answer"], int) or not 0 <= q["answer"] <= 3:
            errs.append("answer must be index 0-3")
    if q["type"] not in ("rule", "sign"):
        errs.append("type must be rule or sign")
    if q["type"] == "sign":
        if not q.get("img"):
            errs.append("sign question needs img")
        elif q["img"] not in FIGS:
            errs.append(f"unknown img {q['img']}")
    # the quote must exist verbatim (ignoring punctuation/spacing) on the cited page or a neighbour
    qn = norm(q["quote"])
    if len(qn) < (8 if q["type"] == "sign" else 25):
        errs.append("quote too short to prove anything")
    hay = norm(" ".join(PAGE.get(p, "") for p in (page - 1, page, page + 1)))
    if qn and qn not in hay:
        # allow ellipsis-joined fragments: every fragment must match
        frags = [norm(f) for f in re.split(r"\.\.\.|…", q["quote"]) if len(norm(f)) >= 12]
        if not frags or not all(f in hay for f in frags):
            errs.append("QUOTE NOT FOUND on cited page (+/-1): must be copied verbatim from the guide text")
    # answer text should not be leaked in the hint
    if isinstance(ch_, list) and len(ch_) == 4 and isinstance(q.get("answer"), int) and 0 <= q["answer"] <= 3:
        a = norm(ch_[q["answer"]])
        if len(a) >= 6 and a in norm(q["hint"]):
            errs.append("hint gives away the answer text")
    return errs


def run(files):
    allq, report, seen_text = [], {}, collections.defaultdict(list)
    for f in files:
        try:
            qs = json.load(open(f, encoding="utf-8"))
        except Exception as e:
            report[os.path.basename(f)] = [f"JSON error: {e}"]
            continue
        for q in qs:
            e = check(q)
            if e:
                report[q.get("id", "?")] = e
            seen_text[norm(q.get("q", "")) + "|" + str(q.get("img"))].append(q.get("id"))
            allq.append(q)
    ids = collections.Counter(q.get("id") for q in allq)
    for i, n in ids.items():
        if n > 1:
            report.setdefault(i, []).append("duplicate id")
    for k, v in seen_text.items():
        if len(v) > 1:
            for i in v[1:]:
                report.setdefault(i, []).append(f"duplicate question text of {v[0]}")
    return allq, report


if __name__ == "__main__":
    if len(sys.argv) > 2:
        allq, rep = run([sys.argv[2]])
        print(f"{len(allq)} questions, {len(rep)} with problems")
        for k, v in rep.items():
            print(k, "->", "; ".join(v))
    else:
        files = sorted(glob.glob(os.path.join(DATA, "questions", "*.json")))
        allq, rep = run(files)
        os.makedirs(os.path.join(DATA, "verify"), exist_ok=True)
        json.dump(rep, open(os.path.join(DATA, "verify", "mechanical.json"), "w", encoding="utf-8"), indent=1)
        byc = collections.Counter(q.get("ch") for q in allq)
        print(f"{len(allq)} questions, {len(rep)} failing mechanical checks")
        print("by chapter:", dict(sorted(byc.items())))
        print("signs:", sum(1 for q in allq if q.get("type") == "sign"))
        for k, v in list(rep.items())[:40]:
            print(k, "->", "; ".join(v))
