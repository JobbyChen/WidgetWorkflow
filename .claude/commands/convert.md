---
description: Turn notes, a PDF, a transcript or a change message into a widget HTML file
---

Convert the source material below into Smokin' Notes HTML with interactive
supply-and-demand widgets.

**Follow `docs/conversion-prompt-v7.md` exactly.** It is the system prompt for
this job: a step-numbered procedure (0, 0T, 0C, 1–8) iterated over six versions,
where every rule exists because something went wrong without it. Read it before
writing anything. Read `docs/engine-reference.md` for the schema, and copy the
config shapes in `examples/ECO2013-Widgets-All.html` rather than inventing new
ones.

The rules that override anything else:

- **Never ask a question.** If something you need is missing, keep the existing
  value, flag it in the changelog, and finish the output.
- **Numbers come from the source only**, in the authority order of step 2. If the
  source states none, the graph is symbolic (`pl`/`ql` giving P₁/Q₁) — never
  invent a value.
- **Student-facing text never names where the material came from** — no
  transcript, lecture, recording, board, class or file, in captions, labels or
  prose. Paraphrase in original wording; never reproduce a spoken sentence or
  printed phrasing.
- **Widgets are JSON.** Never hand-write SVG or JS in a notes file except in
  figure mode — and check `docs/open-issues.md` first, because figure mode is
  specified in the prompt and currently throws in the engine.
- **You never type the engine.** Emit `<!--SDG-ENGINE-->` once in the head,
  directly after the sn25-v6.js line.
- **No label may touch a curve, a point, an arrow or another label** (step 5).

Then run, in order:

```
python scripts/embed_engine.py <file>
python scripts/check_file.py <file>        # must be 0 FAIL
python scripts/render_widgets.py <file>    # then look at every PNG
```

Deliver the file (or the patch blocks) plus a changelog whose first line is
`COURSE-TERMCODE-Topic.html`.

Source material:

$ARGUMENTS
