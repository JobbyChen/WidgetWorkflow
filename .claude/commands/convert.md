---
description: Turn notes, a PDF, a transcript or a change message into a widget HTML file
---

Convert the source material below into one self-contained Smokin' Notes HTML
file with interactive supply-and-demand widgets.

Follow `docs/conversion-prompt-v5.md` exactly. It is a step-numbered procedure
(0, 0T, 0C, 1–9) and every rule in it exists because something went wrong
without it. Read `docs/engine-reference.md` for the schema before writing any
config, and copy the shapes in `examples/engine-testbed.html` rather than
inventing new ones.

The rules that override anything else:

- **Never ask a question during the conversion.** Carry values over, do the best
  available thing, and flag it in the changelog.
- **Numbers come from the source only.** No number appears in the output that is
  not stated in the user's message, the notes prose, the notes labels, the
  transcript, the image or the alt text — in that order of authority. If the
  source gives none, the graph is symbolic (`P₁`/`Q₁`).
- **Student-facing text never names where the material came from.** Paraphrase in
  original wording; never reproduce phrasing from a textbook or other printed
  source, and flag anything that stays close to one.
- **Widgets are JSON.** Never hand-written SVG or JS in a notes file. If the
  engine cannot express a graph, add it to `docs/open-issues.md`.
- **No label may touch a curve, a point, an arrow or another label** (step 5).

Finish by running, in order:

```
python scripts/embed_engine.py <file>
python scripts/check_file.py <file>        # must be 0 FAIL
python scripts/render_widgets.py <file>    # then look at every PNG
```

Deliver the file plus a changelog in `docs/changelogs/` whose first line is the
file name.

Source material:

$ARGUMENTS
