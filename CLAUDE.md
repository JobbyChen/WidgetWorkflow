# CLAUDE.md — ECO2013 / ECO2023 interactive graph widgets

Smokin' Notes (Ian, ian@smokinnotes.com) publishes HTML course notes. This repo
turns the static supply-and-demand graph images in those notes into interactive
widgets, so a new semester's examples (different good, different numbers,
different shift) are a config edit rather than new artwork. The project began in
a Claude.ai project ("ECO2013 widgets", 2026-09-11 → 09-16) and moved here.

**Read this file, then `docs/decisions-and-history.md`, then
`docs/open-issues.md`.**

## What is in this repo

```
CLAUDE.md                     ← you are here
README.md                     ← short human-facing overview
engine/
  sd-graph.js                 ← the widget engine (v2). ONE copy. Everything renders from this.
  sd-graph.css                ← its stylesheet (all arrows red)
docs/
  project-brief.md            ← the brief + what got built against it
  conversion-prompt-v6.md     ← THE operating procedure (the system prompt), verbatim
  engine-reference.md         ← JSON schema, presets, geometry, and what the engine does NOT do
  decisions-and-history.md    ← timeline and decisions with reasons
  open-issues.md              ← bugs, gaps, next steps (checkboxes)
  changelogs/                 ← one changelog per conversion
  archive/                    ← prompt-variant conventions
examples/
  ECO2013-263-SupplyAndDemand.html ← FINISHED OUTPUT (Fall '26, transcript-only, 9 widgets)
  ECO2013-Widgets-All.html    ← the 9/11/26 prototype: 20 widgets, the JSON shape reference
reference-images/             ← the source PNGs (empty — see open issues)
scripts/
  embed_engine.py             ← inline engine/ into a notes file's <head> (prompt step 7)
  check_file.py               ← mechanical step-8 checks (JSON, </script>, head, engine identity…)
  render_widgets.py           ← Playwright: screenshot every widget × scenario × step for collision review
.claude/commands/             ← /convert, /check, /render
```

## The workflow in one paragraph

Input is one of: (a) notes PDF ± PNGs, (b) notes HTML ± PNGs, (c) a lecture
transcript (± notes), or (d) an existing widget file plus a message saying what
changed this semester. Follow `docs/conversion-prompt-v6.md` exactly — it is a
step-numbered procedure (0, 0T, 0C, 1–8) that was iterated over six versions,
and every rule in it exists because something went wrong without it. Output is
one HTML file carrying the house head, a `<!--SDG-ENGINE-->` placeholder, and a
`<div class="sdg">` JSON widget in place of every graph image (or, in mode d, a
set of REPLACE patches), plus a changelog
whose first line is the file name `COURSE-TERMCODE-Topic.html` (Fall 2026 →
`263`). Never ask the user a question during a conversion; carry values over and
flag them in the changelog.

## Hard rules (these override anything you'd otherwise do)

1. **Never edit `engine/sd-graph.js` or `.css` casually.** Every published notes
   file embeds a verbatim copy — header comment included — and step 8 checks
   byte-identity. If you change the engine: bump the version comment, update
   `docs/engine-reference.md`, and re-embed into every example with
   `scripts/embed_engine.py`. The model never types the engine: it emits
   `<!--SDG-ENGINE-->` and the script fills it in.
2. **Widgets are JSON, never bespoke code.** If a graph can't be expressed with
   the engine's schema, that is an engine feature request
   (`docs/open-issues.md`), not a reason to hand-write SVG/JS in a notes file.
   (Exception: "figure mode" for process diagrams is specified in the prompt but
   not implemented — see open issues before using it.)
3. **Numbers come from the source only.** Every coordinate, tick and caption
   number must be stated in the notes prose, the user's message, or the
   transcript. Symbolic drawing (P₁/Q₁) when numbers are missing; never invent
   one. Authority order: user message > notes prose > notes labels > transcript >
   image > alt text.
4. **Student-facing text never mentions its source.** No "the transcript", "the
   lecture", "the recording", "the board", "the slides", "the class", "the file"
   — in captions, labels, or prose. This is also Ian's standing preference for
   all study-guide work: paraphrase in original wording, never copy
   textbook/printed phrasing, and flag anything that closely mirrors a source.
5. **Match the printed artwork.** Black original curve, red shifted curve, every
   arrow red, curved D/S with numbered markers on conceptual graphs, straight
   lines with hollow dots on numeric ones, dashed grid on schedules, P and Q as
   axis labels, nothing else. No label may touch a curve, point, arrow, or
   another label (step 5 has the placement rules — read them before writing any
   config).
6. **House HTML format is fixed** (prompt step 0): `<title>` = chapter name only,
   with no course code, term code, season or year; the Red Hat Display font link,
   then `sn25-v6.css` and `sn25-v6.js` from
   `https://smokinnotes.s3.us-east-1.amazonaws.com/content/` (never v5), then
   `<!--SDG-ENGINE-->`; `<p class="date">` per class date, `<h1>`/`<h2>` only
   (never `<h3>`), `.exam-tip` with an `<h4>`, plain tables; `<strong>` for
   vocabulary terms only, `<b>` for emphasis and labels, never `<u>`; keep every
   `<!-- IMAGE POSITION: … -->` comment where the image was.
7. **Captions are prose:** 1–3 complete sentences ending with the P and Q change
   in words. No "Before –/After –", no fragments, no colon punchlines, no "Price
   up, quantity up".
8. **Group cases of one lesson into one widget with scenario buttons** (four
   apple shifts; surplus + shortage; increase + decrease of one schedule;
   substitutes + complements in production).

## Where things stand (2026-09-16)

The repository was created empty — `eco-widgets.zip` never reached it. The engine,
both example files and prompt v6 were later supplied directly and are installed
here verbatim. An earlier attempt to reconstruct them from this file's prose
description was wrong in nearly every particular and has been deleted;
`docs/decisions-and-history.md` records what it got wrong, and why a summary is
not enough to reproduce an implementation.

* **Verified against the real files:** the engine embedded in the 263 file is
  byte-identical to `engine/` (header comment included); both of
  `embed_engine.py`'s paths reproduce the delivered file byte-for-byte; all 20
  prototype widgets render with no engine errors; `check_file.py` runs the
  geometric label test over 74 labels in the 263 file with no overlaps.
* **Engine is v2.1.** `shiftArrow: false` drops the redundant shift arrow in a
  schedule-shift widget — the per-row arrows already say it once per row — while
  keeping the slide and the dimming, and every arrow is now one weight (2.4px).
  Prompt v6 step 5 changed with it.
* **`ECO2013-263-SupplyAndDemand.html` is 0 FAIL, 0 WARN.** Its three references
  to the class are reworded and its four term labels now keep only the term
  inside `<strong>`.
* **Left as delivered:** the 9/11 prototype's captions predate v6's caption
  rules, and its apples widget puts six brace labels on curves (`below:true`
  would fix it). Both are recorded in `docs/open-issues.md` rather than silently
  rewritten.
* **Still open:** figure mode is in the prompt and throws in the engine;
  `preset:"shift"` draws its gap brace above the axis where the hand-written
  template puts it below.
* **Unknowns to ask Ian:** where finished files get published (S3 path? LMS?);
  whether the professor's PDF for the Fall '26 chapter exists yet; and whether
  the rest of the zip (the 30 reference PNGs, the sample notes file, the earlier
  changelogs) still exists.

Full list with checkboxes: `docs/open-issues.md`.

## How to work here

* Before touching a widget, open `docs/engine-reference.md` for the schema and
  `examples/ECO2013-Widgets-All.html` for the canonical shapes (schedule+curve,
  movement-along vs shift, schedule shift with per-row arrows, surplus/shortage
  with hlines+braces+moves, two-market panels, symbolic presets). Copy those
  shapes; don't reinvent.
* Coordinates come from the source, never from guesswork, and curves pass exactly
  through every numbered point. A point's axis labels are automatic: it prints
  its own price and quantity unless they are already ticks, and `pl`/`ql` replace
  them with `P₁`/`Q₁` on symbolic graphs.
* After any change to a notes file: `python scripts/check_file.py <file>` (must
  be 0 FAIL) and, for anything visual, `python scripts/render_widgets.py <file>`
  and look at every PNG for collisions at every step.
* To test a config quickly, drop it into a copy of
  `examples/ECO2013-Widgets-All.html` and open it in a browser; it carries its
  own copy of the engine in its head.
* Prompt changes: edit `docs/conversion-prompt-v6.md` (bump to v7 in the file
  name and add a "what changed" line at the top). If a standalone tool prompt is
  needed, append the two engine files as Appendix A/B — see
  `docs/archive/README.md`.
* Commit messages: plain imperative. Don't commit `shots/` (screenshots) — it's
  in `.gitignore`.
* Ian is the only user. He reviews output by reading it and clicking through
  widgets; he does not want questions mid-conversion, he wants the file plus a
  changelog he can scan.

## Vocabulary

* **widget** — one `<div class="sdg">` block. **config** — its JSON. **preset** —
  a config that starts `"preset":"shift"|"double"` and expands in the engine.
* **symbolic graph** — P₁/Q₁ axes via `pl`/`ql`, no numbers, 110×110 coordinates
  with equilibrium at [50,50]. **numeric** — real prices/quantities from the
  source.
* **scenario** — a button whose overrides are merged shallowly over the base
  config. **step** — one caption string + visibility state, driven by `at` and
  `until` (`until` is exclusive).
* **schedule** — a price/quantity table; **schedule shift** — before/after
  columns with per-row arrows.
* **house format / sn25-v6** — Smokin' Notes' site stylesheet and script that
  every notes page loads.
* **TERMCODE** — YY + {1 spring, 2 summer, 3 fall}; Fall 2026 = 263.
* **patch mode** — mode (d)'s default output: `=== REPLACE / === WITH / === END`
  blocks instead of the whole file.
* **change-by-message / mode (d) / step 0C** — updating an existing widget file
  from a sentence like "this semester it's hotdogs, demand shifts right by 20".
