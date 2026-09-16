# Conversion prompt v5 — source material to widget HTML

**What changed in v5:** the engine is embedded in the output file rather than
linked (step 7), so a published file never depends on a hosted copy; step 8
became a script (`scripts/check_file.py`) instead of a checklist; the placement
rules in step 5 were written out after labels kept landing on curves; and modes
0T (transcript) and 0C (change-by-message) were added.

> **Reconstruction note.** This file was rewritten from the rules recorded in
> `CLAUDE.md` when the repository was created, because the original v5 text never
> reached the repo. The numbered procedure, the mode letters and every hard rule
> are as `CLAUDE.md` states them. If the original turns up, prefer it and fold
> anything useful from here into it. See `docs/decisions-and-history.md`.

---

This is an operating procedure, not advice. Work the steps in order.

**Never ask a question during a conversion.** If something is missing, carry the
value over, do the best available thing, and flag it in the changelog. A file
plus a changelog that can be scanned is the deliverable; a question is not.

---

## Step 0 — Identify the input and fix the house format

The input is one of:

| mode | input |
| --- | --- |
| **a** | notes PDF, with or without the graph PNGs |
| **b** | notes HTML, with or without the PNGs |
| **c** | a lecture transcript, with or without notes → **go to step 0T first** |
| **d** | an existing widget file plus a message saying what changed → **step 0C** |

The output file is always one self-contained HTML file named
`COURSE-TERMCODE-Topic.html` (`ECO2013-263-SupplyAndDemand.html`). TERMCODE is
YY + term digit, where 1 is spring, 2 summer, 3 fall: Fall 2026 is `263`.

The head is fixed:

- `<title>` is the chapter name only — no course code, no colon, no subtitle.
- `sn25-v6.css` and `sn25-v6.js`, both from
  `https://smokinnotes.s3.us-east-1.amazonaws.com/content/`. Never v5.
- `<p class="date">` for the term.
- `<h1>` and `<h2>` for structure. No `<h3>`.
- `.exam-tip` for exam tips, plain `<table>` for tables.
- Every `<!-- IMAGE POSITION: … -->` comment stays exactly where its image was,
  with the widget in its place.

## Step 0T — Transcript input

A transcript gives you the lesson order and the examples; it rarely gives you
numbers. Before anything else:

1. List every graph the material walks through, in the order it reaches them.
2. For each, write down the numbers actually stated. If none are stated, that
   graph is symbolic — `P₁`/`Q₁`, no invented values.
3. Note which examples are named (the good, the shock, the direction).
4. Anything that needs numbers the material never gives goes in the changelog as
   **needs numbers**, and ships symbolic.

Then continue at step 1.

## Step 0C — Change by message

The input is an existing widget file and a sentence like *"this semester it's
hotdogs, demand shifts right by 20"*.

1. Change only what the message names: the good, the numbers, the direction.
2. Everything else — captions, structure, scenario grouping, placement — carries
   over untouched.
3. Re-run steps 5 through 8 on the result. The placement that worked for apples
   may not work for hotdogs once a label gets longer.
4. The changelog lists what changed and what was carried over.

---

## Step 1 — Inventory the graphs

Walk the source front to back and list every graph image, in order, with the
`IMAGE POSITION` comment that marks it. One line per graph: what it shows, what
numbers it states, which lesson it belongs to.

## Step 2 — Group them

Cases of one lesson become **one widget with scenario buttons**, not several
widgets: the four apple shifts; surplus and shortage; the increase and the
decrease of one schedule; substitutes and complements in production.

Group when the graphs answer the same question with different inputs. Keep them
apart when they are different lessons that happen to look alike.

## Step 3 — Get the numbers

Every coordinate, tick and caption number must be stated in the source. Authority
order, highest first:

1. the user's message
2. the notes prose
3. the notes labels
4. the transcript
5. the image
6. the alt text

**Never invent a number.** If the source gives none, the graph is symbolic:
`P₁`/`Q₁` on the axes, `110 × 110` coordinates, equilibrium near `[50, 50]`.
A symbolic graph is correct; a graph with made-up numbers is not.

## Step 4 — Write the configs

JSON only, against `docs/engine-reference.md`. Never hand-written SVG or JS in a
notes file — if the engine cannot express it, that is an engine feature request
in `docs/open-issues.md`.

Copy the shapes that already exist rather than reinventing them:
schedule + curve, schedule shift with scenarios, surplus/shortage with guides and
a brace, two-market panels, symbolic single shift, two-panel double shift. They
are in `examples/engine-testbed.html`.

Match the printed artwork and nothing else:

- Black original curve, red shifted curve.
- **Every arrow red.**
- Conceptual graphs: curved D and S, numbered markers.
- Numeric graphs: straight lines, hollow dots.
- Schedules: the dashed grid.
- `P` and `Q` as axis labels.

Let the engine solve positions. Write `"on": ["D2", "S"]` for an equilibrium and
`"onCurve": {"curve": "D", "y": 70}` for a point at a price, rather than typing
coordinates — a bowed curve does not pass through the middle of its chord, and a
guessed dot lands beside the crossing.

## Step 5 — Place every label

**No label may touch a curve, a point, an arrow or another label.** Read this
before writing a config, not after.

- At a crossing the curves take the diagonals, so the free wedges are due north,
  south, east and west. Equilibrium labels go north (`dx 0, dy -14, anchor
  middle`) and south (`dx -7, dy 21, anchor end`) — due north is clear outright,
  while the south label has to step aside from the guide dropping to the axis.
  The north-east and south-west corners look empty on a sketch and are not.
- Curve labels sit at the end of the curve, outside the plot, offset away from
  the line: `{"pos": "end", "dx": 8, "dy": 6}` below a demand curve,
  `{"pos": "end", "dx": 8, "dy": -2}` above a supply curve. When two curve ends
  are close, move one to a `pos` partway along instead.
- A brace's label needs `below` set to the side that is free. This is the most
  common collision of all.
- Shift arrows go in the empty corner the shift moves away from, clear of both
  curves and of any marker.
- Tick labels that end up within a few units of each other will overlap; move the
  geometry, not the label.

## Step 6 — Write the captions

Captions are prose: **one to three complete sentences, ending with what happened
to P and Q, in words.**

Not allowed: `Before – / After –`, fragments, a colon and a punchline,
"Price up, quantity up".

**No caption, label or line of prose may name where the material came from.** No
"the transcript", "the lecture", "the recording", "the board", "the slides", "the
class", "the file". Paraphrase in original wording throughout — never reproduce
phrasing from a textbook or other printed source, and flag anything that stays
close to a source in the changelog.

## Step 7 — Embed the engine

```
python scripts/embed_engine.py <file>
```

The engine goes into the file's `<head>` verbatim, between marker comments. No
`<link>` or `<script src>` to a hosted copy survives this step — a published file
that fetches its engine breaks the moment the engine moves.

## Step 8 — Check, render, look

```
python scripts/check_file.py <file>        # must be 0 FAIL
python scripts/render_widgets.py <file>    # then open every PNG
```

`check_file.py` is mechanical: JSON parses, no literal `</script>`, the head is
right, the embedded engine is byte-identical to `engine/`, `at`/`until` point at
steps that exist, captions are sentences, nothing names its source, the
`IMAGE POSITION` comments survived.

It cannot check the two things that matter most. **You** check those, by looking
at every PNG at every scenario and every step:

1. Is every number the number the source gave?
2. Does any label touch a curve, a point, an arrow or another label?

## Step 9 — The changelog

First line is the file name. Then, so it can be scanned:

- one line per widget: what it shows, which source graphs it replaces
- every value carried over rather than taken from the source
- everything flagged **needs numbers**
- anything that stayed close to source wording
- what was grouped into scenarios, and what was deliberately left separate
