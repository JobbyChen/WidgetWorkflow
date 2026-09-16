# Decisions and history

> **This file is a stub.** The full record — the 2026-09-11 → 09-16 timeline, the
> numbered decisions with their reasons, and the approaches that were tried and
> rejected — was written in the Claude.ai project "ECO2013 widgets" and packaged
> into `eco-widgets.zip`. That zip never reached this repository. What follows is
> what can be stated from `CLAUDE.md` plus what happened here, and nothing else.
> Recording a detailed timeline that cannot be verified would be worse than
> leaving it short.

---

## What `CLAUDE.md` records of the original work

- 2026-09-11 → 09-16: the project ran in a Claude.ai project. It produced the
  engine (v2), a prototype rendering all 30 graph images as widgets, five
  iterations of the conversion prompt, and one real conversion — the Fall '26
  Supply and Demand chapter, built from a transcript alone, saved as
  `examples/ECO2013-263-SupplyAndDemand.html`.
- 2026-09-15: the stylesheet was changed so that **all** arrows are red.
- 2026-09-15: a review run screenshotted every widget, scenario and step in
  headless Chromium and checked each for collisions. 39 screenshots, no engine
  errors. That run is the reason the render-and-look step exists.
- 2026-09-16: everything was packaged as a git-ready folder for Claude Code, with
  five findings recorded (see `docs/open-issues.md`).

Decisions that `CLAUDE.md` states as settled, with the reason given:

| decision | reason given |
| --- | --- |
| Widgets are JSON, never bespoke code | a graph the schema cannot express is an engine gap, not a licence to hand-write SVG in a notes file |
| One engine copy, embedded verbatim | every published file carries its own; byte-identity is checked |
| Numbers come from the source only | symbolic `P₁`/`Q₁` when the source states none |
| Student-facing text never names its source | also Ian's standing rule for all study-guide work |
| Cases of one lesson group into one widget with scenario buttons | one lesson, one widget |
| Captions are prose, 1–3 sentences, ending with the change in P and Q | no `Before –/After –`, no fragments |
| Never ask a question mid-conversion | carry the value over and flag it in the changelog |

Rejected approaches are **not** recoverable from `CLAUDE.md`. They are in the
zip.

---

## 2026-09-16 — repository rebuilt from the specification

The repository was found empty: no commits, no branches, no zip anywhere on disk.
A `CLAUDE.md` pointing at an engine, docs, scripts and examples that do not exist
is not usable, so the parts that could be derived from the specification were
rebuilt.

**Rebuilt, and working:**

- `engine/sd-graph.js` + `sd-graph.css` — a v2 engine written against the hard
  rules in `CLAUDE.md`: black original and red shifted curves, every arrow red,
  curved conceptual curves with numbered markers, straight numeric lines with
  hollow dots, dashed-grid schedules, `P`/`Q` axes, symbolic 110×110 coordinates,
  scenario buttons, `at`/`until` steps, the `shift` and `double` presets.
- `scripts/embed_engine.py`, `check_file.py`, `render_widgets.py` — step 7, step
  8 and the collision-review render.
- `docs/engine-reference.md` — written from the implementation, so it is
  accurate for this engine.
- `docs/conversion-prompt-v5.md` — the procedure reassembled from the rules
  `CLAUDE.md` enumerates.
- `examples/engine-testbed.html` — six fixtures covering every shape the engine
  draws.
- `.claude/commands/` — `/convert`, `/check`, `/render`.

**Not rebuilt, on purpose:** the finished notes file, the sample and prototype
files, the 30 reference PNGs, and the original history. The notes file's numbers
and captions came from source material this repo does not have, and the
numbers-from-the-source rule forbids inventing them. See `docs/open-issues.md`.

**The rebuilt engine is not byte-identical to the original**, so any notes file
produced by the original engine will fail `check_file.py`'s byte-identity check
until it is re-embedded. That is the expected behaviour of that check, not a bug
in it.

### Decisions taken during the rebuild

1. **`at` and `until` mean step indexes everywhere.** The first draft also used
   `at` for a tick's coordinate and for a label's position along a curve. One key
   with three meanings made `check_file.py` unable to tell a coordinate from a
   step, and it reported nine false failures on the test bed. Renamed to
   `tick.value` and `label.pos`.
2. **Bow direction is fixed, not computed.** Choosing the side by "which
   perpendicular points nearer the origin" is unstable: for a supply curve the
   dot product sits near zero, so two supply curves eighteen units apart landed
   on opposite sides and the shifted one drew back over the original — the two
   equilibria resolved to the same point. The bow now always displaces the curve
   downward in price, which gives the printed shape for both demand and supply,
   and a negative `bow` flips it.
3. **The engine solves positions; authors do not type them.** `"on"` for a
   crossing, `"onCurve"` for a point at a price. Added after every hand-placed
   equilibrium dot in the first test bed landed beside its intersection, because
   a bowed curve does not pass through the midpoint of its chord.
4. **The `shift` preset emits no brace.** The known `below:true` bug was a
   colliding label; a preset that reliably produces a collision is worse than a
   preset that leaves the brace to the author.
5. **`check_file.py` recognises an engine test bed** (a file linking
   `../engine/`) and skips the house-format and embedding checks for it, instead
   of reporting five failures on a file that is correct for what it is.
6. **The test bed's fixtures are labelled as fixtures** — made-up numbers, not
   course notes, not for publication. The alternative, a plausible-looking notes
   file with invented prices, would violate the numbers-from-the-source rule and
   could be mistaken for real material.
