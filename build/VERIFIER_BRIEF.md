# Verifier brief: Alberta Class 7 practice questions

You are the independent second check on practice questions for teenagers studying for the Alberta Class 7 learner's knowledge test. Someone else wrote them. Your job is to catch anything that would teach a wrong rule or mark a right answer wrong. Be skeptical: assume nothing is correct until the guide text proves it.

**The only source of truth is the official Alberta Driver's Guide (June 15, 2026 edition).** Not your own knowledge of driving rules, not other provinces, not older editions.

Working folder: `C:/Users/BillyHarvey/Repos/learners-prep` (run commands from here).
- Guide text by chapter, with `=== Page N ===` markers: `data/text/chNN.txt`
- Page images (for diagrams and signs): `data/pages/pNNN.webp`; sign crops: `data/figs/<img>.png`
- Writer rules (what a good question looks like): `build/QUESTION_WRITER_BRIEF.md`

## For every question, check
1. **Answer is right.** The marked answer is clearly correct per the guide, read in context (not just the quoted sentence). Check the surrounding paragraph for exceptions and conditions the question ignores.
2. **Every distractor is wrong.** Each wrong choice must be contradicted by the guide, not merely "not mentioned" or "less good". If a distractor could be argued correct from the guide, that's a failure.
3. **One clear reading.** A careful 15-year-old could not reasonably read the question two ways. Watch for missing conditions (urban vs rural, posted vs default, learner vs full licence, divided vs undivided highway).
4. **Quote supports it.** The quote is on the cited page and actually proves the answer.
5. **Hint** is accurate, helps, and doesn't give the answer away.
6. **Explanation** is accurate and doesn't add facts that aren't in the guide.
7. **Sign questions:** open the crop image. It must show the right sign, only one sign, and no printed caption that reveals the answer.
8. Canadian spelling, no em dashes, plain language.
9. **Ambiguous guide passages:** if the guide's own wording is unclear on the point being tested, reject the question rather than guessing.

## What to do
- **Small, safe fix** (wording, a weak distractor replaced with one the guide clearly contradicts, hint or explanation tidy-up): edit the question in place in its JSON file, keep the same `id`, and record verdict `"ok"` with what you changed.
- **Anything wrong or arguable that you can't fix cleanly:** verdict `"reject"` with the reason. Don't delete it from the question file.
- After editing, run `python -I -X utf8 build/verify.py data data/questions/<file>.json` until it reports 0 problems.

Write your verdicts to `data/verify/review_<file name without .json>.json` as a JSON array covering EVERY question in the file:
```json
[{"id": "c09-001", "verdict": "ok", "note": ""},
 {"id": "c09-002", "verdict": "ok", "note": "fixed: distractor B was arguably correct; replaced"},
 {"id": "c09-003", "verdict": "reject", "note": "guide says X only applies to GDL drivers; question doesn't say so"}]
```
Questions without a verdict are treated as rejected, so cover them all.
