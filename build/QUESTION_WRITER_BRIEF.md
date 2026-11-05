# Question writer brief: Alberta Class 7 practice app

You are writing multiple-choice practice questions for teenagers (about 14 to 16) in Alberta who are studying for the Class 7 learner's knowledge test. The real test is 30 multiple-choice questions; 25 correct to pass.

**The only source of truth is the official Alberta Driver's Guide (June 15, 2026 edition).** A wrong question teaches a kid a wrong rule of the road. Accuracy beats volume every time.

Working folder: `C:/Users/BillyHarvey/Repos/learners-prep` (run commands from here).

## Inputs
- `data/text/chNN.txt`: the guide text for chapter NN, with `=== Page N ===` markers (N = PDF page number) and `## Section` headings. This is what you quote from.
- `data/text/sections.txt`: section ids (`s005` etc.), chapter, title, page range.
- `data/annot/pNNN.png`: page renders with red numbered boxes around every figure (signs, diagrams). Use the Read tool to look at them. Box number K on page NNN is figure id `pNNN_fK`; the crop is `data/figs/pNNN_fK.png`.
- `data/pages/pNNN.webp`: plain page renders, if you need to see a diagram.
- `data/research/topic_blueprint.md`: topics that third-party online practice tests ask about most often. Use it to decide WHAT to ask about (prioritize the high-frequency concepts your chapter covers). Never copy their wording. If the blueprint states a fact that differs from the 2026 guide, the guide wins. If the guide does not cover a concept, skip it.

## Hard rules
1. Every fact in the question, the correct answer, and the explanation must be stated in the guide. No outside knowledge, no "common sense" rules, no numbers from memory.
2. Each wrong choice must be clearly wrong according to the guide, not merely unmentioned. Best distractors are plausible misconceptions: a number the guide uses for a different situation, the rule for a different sign, the opposite action.
3. Exactly 4 choices. Never "all of the above", "none of the above", "both A and B" (choices get shuffled). Keep choices similar in length and style so the answer isn't obvious from its length.
4. At most 1 in 10 questions may be negative ("Which is NOT..."); bold nothing, write "NOT" in capitals.
5. Ask what a learner needs: rules of the road, signs, signals, pavement markings, right-of-way, speeds, distances, following/stopping, GDL rules, demerits, impaired driving laws, sharing the road, emergencies, safe-driving behaviour. Skip trivia (URLs, phone numbers, office procedures, form names, fees) unless the blueprint shows it's commonly tested.
6. One clear correct answer. If two choices could be argued correct from the guide's wording, rewrite.
7. Canadian spelling (licence as a noun, colour, centre, kilometres). Plain language, grade 8 reading level. No em dashes.
8. Don't make the question unanswerable without a picture unless it's a sign question with an image.

## Fields (JSON array of objects)
```json
{
  "id": "c04-017",                 // c{chapter 2 digits}-{3 digits}, unique
  "ch": 4,                         // chapter number
  "sec": "s061",                   // section id from sections.txt
  "page": 63,                      // PDF page (=== Page N === marker) where the quote is
  "type": "rule",                  // "rule" or "sign"
  "img": null,                     // figure id like "p029_f3" for sign questions, else null
  "q": "When approaching a roundabout, who must you yield to?",
  "choices": ["...", "...", "...", "..."],
  "answer": 2,                     // index of the correct choice
  "hint": "One sentence that nudges toward the idea without naming the answer.",
  "explain": "One or two plain sentences on why the answer is right.",
  "quote": "Exact sentence(s) copied from the chapter text that prove the answer.",
  "topic": "short concept label, ideally matching a blueprint concept"
}
```
- `quote` must be copied word-for-word from `data/text/chNN.txt` (a sentence or two, the minimum that proves the answer). Join two non-adjacent fragments with `...` only if both are needed. The checker rejects anything not found verbatim on the cited page or the page next to it.
- `hint`: must not contain the answer text and must not make three choices obviously silly. Good: "Think about who is already in the circle." Bad: "The answer is the vehicle on the left."

## Sign questions (type "sign")
- Look at the annotated pages, pick a box that shows exactly ONE sign, and open the crop `data/figs/pNNN_fK.png` to confirm. Skip crops that contain more than one sign, cut-off art, or printed text that gives away the meaning (a caption inside the crop). Sign text that is part of the sign itself (e.g. "ONE WAY", "STOP") is fine.
- Ask "What does this sign mean?" or "What should you do when you see this sign?" The correct answer is the guide's description/label for that sign; distractors are meanings of other signs in the guide.
- `quote` = the guide's label/description text for that sign.

## Self-check before you finish
Run `python -I -X utf8 build/verify.py data data/questions/<yourfile>.json` and fix every problem it prints until it reports 0 problems. Then re-read each question once more against the quote and ask: "Would a driver examiner agree this is the one right answer?"
