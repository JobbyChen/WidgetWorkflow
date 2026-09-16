# CLAUDE.md — ECO2013 / ECO2023 interactive graph widgets

Smokin' Notes (Ian, ian@smokinnotes.com) publishes HTML course notes. This repo
turns the static supply-and-demand graph images in those notes into interactive
widgets, so a new semester's examples (different good, different numbers,
different shift) are a config edit rather than new artwork. The project began in
a Claude.ai project ("ECO2013 widgets", 2026-09-11 → 09-16) and moved here.

**Read this file, then `docs/decisions-and-history.md`, then
`docs/open-issues.md`.** The second of those explains why several files named in
the original handoff are not here.

## What is in this repo

```
CLAUDE.md                     ← you are here
README.md                     ← short human-facing overview
engine/
  sd-graph.js                 ← the widget engine (v2). ONE copy. Everything renders from this.
  sd-graph.css                ← its stylesheet (all arrows red)
docs/
  project-brief.md            ← the brief + what got built against it
  conversion-prompt-v5.md     ← THE operating procedure: notes/PDF/transcript → widget HTML
  engine-reference.md         ← full JSON schema, presets, geometry, and what the engine does NOT do
  decisions-and-history.md    ← what is known of the timeline; decisions with reasons
  open-issues.md              ← bugs, gaps, next steps (checkboxes)
  changelogs/                 ← one changelog per conversion
  archive/                    ← prompt-variant conventions
examples/
  engine-testbed.html         ← six fixtures covering every shape the engine draws
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
changed this semester. Follow `docs/conversion-prompt-v5.md` exactly — it is a
step-numbered procedure (0, 0T, 0C, 1–9) that was iterated over five versions,
and every rule in it exists because something went wrong without it. Output is
always one self-contained HTML file (house head + engine embedded verbatim +
`<div class="sdg">` JSON widgets in place of every graph image) plus a changelog
whose first line is the file name `COURSE-TERMCODE-Topic.html` (Fall 2026 →
`263`). Never ask the user a question during a conversion; carry values over and
flag them in the changelog.

## Hard rules (these override anything you'd otherwise do)

1. **Never edit `engine/sd-graph.js` or `.css` casually.** Every published notes
   file embeds a verbatim copy and step 8 checks byte-identity. If you change the
   engine: bump the version comment, update `docs/engine-reference.md`, and
   re-embed into every example with `scripts/embed_engine.py`.
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
6. **House HTML format is fixed** (prompt step 0): `<title>` = chapter name only;
   `sn25-v6.css` and `sn25-v6.js` from
   `https://smokinnotes.s3.us-east-1.amazonaws.com/content/` (never v5);
   `<p class="date">`, `<h1>`/`<h2>` only, `.exam-tip`, plain tables; keep every
   `<!-- IMAGE POSITION: … -->` comment where the image was.
7. **Captions are prose:** 1–3 complete sentences ending with the P and Q change
   in words. No "Before –/After –", no fragments, no colon punchlines, no "Price
   up, quantity up".
8. **Group cases of one lesson into one widget with scenario buttons** (four
   apple shifts; surplus + shortage; increase + decrease of one schedule;
   substitutes + complements in production).

## Where things stand (2026-09-16)

The repository was created empty — the handoff zip (`eco-widgets.zip`) never
reached it. The engine, scripts, docs and test bed here were **rebuilt from the
specification in this file**; the finished notes file, the earlier examples, the
30 reference images and the original numbered history were not, because their
content came from source material this repo does not hold and rule 3 forbids
inventing it. `docs/decisions-and-history.md` says exactly what that means, and
`docs/open-issues.md` tracks it.

* **Done and verified end to end:** engine v2; `embed_engine` → `check_file` →
  `render_widgets` round trip on a house-format file (0 FAIL, widgets render);
  six-fixture test bed; prompt v5; `/convert`, `/check`, `/render`.
* **Fixed during the rebuild:** the `preset:"shift"` brace collision (the preset
  now emits no brace); equilibrium dots landing beside the crossing (`"on"` and
  `"onCurve"` make the engine solve them); an unstable bow direction that made
  two supply curves eighteen units apart draw over each other.
* **Still open:** figure mode is in the prompt and not in the engine; no
  automatic collision detection.
* **Unknowns to ask Ian:** where finished files get published (S3 path? LMS?);
  whether the professor's PDF for the Fall '26 chapter exists yet (the transcript
  build flagged two examples as "needs numbers"); and whether `eco-widgets.zip`
  still exists anywhere.

Full list with checkboxes: `docs/open-issues.md`.

## How to work here

* Before touching a widget, open `docs/engine-reference.md` for the schema and
  `examples/engine-testbed.html` for the canonical shapes (schedule+curve,
  schedule shift with scenarios, surplus/shortage with guides+brace+moves,
  two-market panels, symbolic single shift, movement along a curve). Copy those
  shapes; don't reinvent.
* Let the engine solve positions. `"on": ["D2", "S"]` for an equilibrium,
  `"onCurve": {"curve": "D", "y": 70}` for a point at a price. A bowed curve does
  not pass through the middle of its chord, so a typed coordinate lands beside
  the crossing.
* After any change to a notes file: `python scripts/check_file.py <file>` (must
  be 0 FAIL) and, for anything visual, `python scripts/render_widgets.py <file>`
  and look at every PNG for collisions at every step.
* To test a config quickly, drop it into `examples/engine-testbed.html` (which
  links `../engine/` directly) and open in a browser.
* Prompt changes: edit `docs/conversion-prompt-v5.md` (bump to v6 in the title
  and add a "what changed" line at the top, as v4 and v5 have). If a standalone
  tool prompt is needed, append the two engine files as Appendix A/B — see
  `docs/archive/README.md`.
* Commit messages: plain imperative. Don't commit `shots/` (screenshots) — it's
  in `.gitignore`.
* Ian is the only user. He reviews output by reading it and clicking through
  widgets; he does not want questions mid-conversion, he wants the file plus a
  changelog he can scan.

## Vocabulary

* **widget** — one `<div class="sdg">` block. **config** — its JSON. **preset** —
  a config that starts `"preset":"shift"|"double"` and expands in the engine.
* **symbolic graph** — P₁/Q₁ axes, no numbers, 110×110 coordinate system with
  equilibrium near [50,50]. **numeric** — real prices/quantities from the source.
* **scenario** — a button that overlays keys on the base config. **step** — one
  caption + visibility state, driven by `at`/`until`.
* **schedule** — a price/quantity table; **schedule shift** — before/after
  columns with per-row arrows.
* **house format / sn25-v6** — Smokin' Notes' site stylesheet and script that
  every notes page loads.
* **TERMCODE** — YY + {1 spring, 2 summer, 3 fall}; Fall 2026 = 263.
* **change-by-message / mode (d) / step 0C** — updating an existing widget file
  from a sentence like "this semester it's hotdogs, demand shifts right by 20".
