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
  conversion-prompt-v7.md     ← THE operating procedure (the system prompt), verbatim
  engine-reference.md         ← JSON schema, presets, geometry, and what the engine does NOT do
  decisions-and-history.md    ← timeline and decisions with reasons
  open-issues.md              ← bugs, gaps, next steps (checkboxes)
  changelogs/                 ← one changelog per conversion
  archive/                    ← prompt-variant conventions
examples/
  ECO2013-263-SupplyAndDemand.html ← FINISHED OUTPUT (Fall '26, transcript-only, 9 widgets)
  ECO2013-263-TradeoffsComparativeAdvantageTheMarketSystem.html ← FINISHED OUTPUT (Exam 1 ch. 1, 7 widgets)
  ECO2013-Widgets-All.html    ← the 9/11/26 prototype: 20 widgets, the JSON shape reference
reference-images/             ← the source PNGs (empty — see open issues)
scripts/
  embed_engine.py             ← inline engine/ into a notes file's <head> (prompt step 7)
  check_file.py               ← mechanical step-8 checks (JSON, </script>, head, engine identity…)
  doc_headings.py             ← a Word file's headings and their level. Run it BEFORE writing any.
  doc_formulas.py             ← a Word file's MathType equations as text; --check audits a notes file
  add_toc.py                  ← write the TOC in by hand. Only for a file WITHOUT the live script.
  widget_text.py              ← every renamable string in a file's widgets; --apply writes them back
  transcript_diff.py          ← does a new term's transcript change this file? Run it BEFORE swapping.
  test_check_file.py          ← tests for check_file.py. Run after changing it.
  render_widgets.py           ← Playwright: screenshot every widget × scenario × step for collision review
  mobile_check.py             ← does it fit and still work on a phone? Drives every button at 390/320px
  place_labels.py             ← put every shaded area's label where it is clear, and centred
.claude/commands/             ← /convert, /check, /render
```

## The workflow in one paragraph

Input is one of: (a) notes PDF ± PNGs, (b) notes HTML ± PNGs, (c) a lecture
transcript (± notes), or (d) an existing widget file plus a message saying what
changed this semester. Follow `docs/conversion-prompt-v7.md` exactly — it is a
step-numbered procedure (0, 0T, 0C, 1–8) that was iterated over six versions,
and every rule in it exists because something went wrong without it. Output is
one HTML file carrying the house head, a `<!--SDG-ENGINE-->` placeholder, and a
`<div class="sdg">` JSON widget in place of every graph image (or, in mode d, a
set of REPLACE patches), plus a changelog
whose first line is the file name `COURSE-TERMCODE-Topic.html` (Fall 2026 →
`263`). **Ask only when a wrong guess would be costly** — a number, which graphs
to convert, which of two readings of a table or figure. Everything else you
decide and flag in the changelog: heading levels, table markup, label placement,
how a scenario is grouped. See *Asking questions* below, and note that prompt v6
itself still forbids questions outright.

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
   lecture", "the recording", "on the board", "the slides", "the class", "the
   file" — in captions, labels, or prose. Attributing content to whoever taught
   it ("the professor said") is the same violation whoever they are. This is
   also Ian's standing preference for all study-guide work: paraphrase in
   original wording, never copy textbook/printed phrasing, and flag anything
   that closely mirrors a source.

   **Naming a person is a separate question, and it is Ian's call.** Some
   professors are happy to be credited; others must never appear in a published
   file, and getting that wrong costs more than any typo here. There is no list
   in this repo, by Ian's choice — so no script, and no session, should decide
   it. `scripts/check_file.py` raises a WARN on any "Professor X" / "Dr. X" in
   student-facing text and never fails the file; the judgement stays with Ian
   every time. If you are converting material that names someone, keep the name
   (prompt v6 step 0 transcribes named people exactly) and list it in the
   changelog so it is reviewed before publication. Note the checker only sees a
   name that carries a title: a person named by surname alone passes silently,
   so read the prose too.
5. **No label touches a curve, an axis line, or a curve's own name.**
   The axis lines were the last thing on a panel that nothing tested against,
   and a curve that runs down to the axis parks its label right on it — which
   is where `D` sat in the Piesanos figure. They are tested now; the axis
   *titles* are exempt, since the engine anchors each one to its own axis by
   design and every panel ever drawn would report it.

   The other half of the same rule:
   `check_file.py` used to skip a curve's label against its own curve, on the
   grounds that it sits at its own end. True of the default offset, false the
   moment `ldx`/`ldy` move it: pull a label back along its own line and the
   line runs straight through the text. "D = MB = MSB" shipped struck through
   by its own demand curve with the file reporting PASS. Nothing is exempt now,
   and removing the exemption flagged nothing in any other example — so it was
   covering defects, not preventing false alarms. Anchor a long label at the
   curve's other end with `lstart` when the near end has no room.
6. **Match the printed artwork.** Black original curve, red shifted curve, every
   arrow red, curved D/S with numbered markers on conceptual graphs, straight
   lines with hollow dots on numeric ones, dashed grid on schedules, P and Q as
   axis labels, nothing else. (Label placement is rule 5; the rest of the
   drawing conventions are settled below.)
7. **House HTML format is fixed** (prompt step 0), with one exception: **the
   `<title>` is not yours to set.** Prompt v6 step 0 asks for the chapter name
   alone, and `check_file.py` used to fail a title carrying a course code, term
   or year. Ian's titles come from his boss — "ECO2013 Fall '26 - International
   Trade Study Guide" is correct as written — so the checker now only requires
   that a title exist, and a title you are given is left exactly as it is.
   (Changed 2026-09-23.) The rest of the head: the Red Hat Display font link,
   `sn25-v6.css` from
   `https://smokinnotes.s3.us-east-1.amazonaws.com/content/`, the house script,
   then `<!--SDG-ENGINE-->`;

   **The house script lives under one of two paths, and they version
   separately.** `content/sn25-v6.js` is what this file used to demand, and it
   returns **403** from S3 — a page carrying only that runs no house script at
   all. `studyguide/sn25-v2.js` is live, is what the chapter files Ian sends
   carry, and is the one he confirmed correct on 2026-09-21. It builds the
   table of contents in the browser (the same `<details class="toc-box">` that
   `add_toc.py` writes) and gives every heading an id. So a chapter carrying it
   needs no TOC markup in the file — and must not also carry one written in,
   because the script builds its own unconditionally and the page then renders
   two. Four example files did, because `add_toc.py` wrote them while
   `content/sn25-v6.js` was the head's only script; swapping to the live script
   is what turned those into duplicates. `check_file.py` fails on the pair now.
   And `check_file.py` compares version
   numbers **inside** a path, never across the two — matching a bare
   `sn25-v[0-5]` failed the current script twice over, once for being absent
   and once for looking old.

   **The two scripts differ in three visible ways**, which is worth knowing
   before migrating a page: `content/sn25-v5.js` heads the box with 📖 OPEN
   BOOK and inserts it at the very top of `<body>` — above the `date` pill,
   which floats right and lands on the first paragraph. `studyguide/sn25-v2.js`
   uses 📘 BLUE BOOK and inserts before the first `<h1>`, so the date keeps its
   corner. Neither sets `open`; both say so in a comment, so a TOC that looks
   "open" is the emoji, not the `<details>`. Both list `h1`, `h2` *and* `h3`. `<p class="date">` per class date, `<h1>`/`<h2>` only
   (never `<h3>`), `.exam-tip` with an `<h4>`, plain tables; `<strong>` for
   vocabulary terms only, `<b>` for emphasis and labels, never `<u>`; keep every
   `<!-- IMAGE POSITION: … -->` comment where the image was.
8. **A step must change the drawing.** Ian's rule, and he has had to give it
   twice: a caption that advances while the picture holds still reads as a
   broken button. The usual cause is off-by-one rather than carelessness —
   `at` is a step index and index 0 is the opening state, so "curves, then CS,
   then PS" needs `at:1` and `at:2`; `at:2` and `at:3` leave step 2 showing
   step 1's picture. `check_file.py` now fails on it, and a figure that is
   genuinely one static diagram takes a `caption` instead of `steps`.
9. **Captions are prose:** 1–3 complete sentences ending with the P and Q change
   in words. No "Before –/After –", no fragments, no colon punchlines, no "Price
   up, quantity up".
10. **Group cases of one lesson into one widget with scenario buttons** (four
   apple shifts; surplus + shortage; increase + decrease of one schedule;
   substitutes + complements in production).

## Drawing conventions (settled — do not re-decide these per chapter)

Every one of these was a round of review. Follow them and the review is about
economics instead of label placement.

* **Fetch the source images and match them.** The `<img src>` URLs in the
  chapter resolve (200 from S3), so `curl` them and look. Match the *figure*,
  not the paragraph beside it: a figure showing consumer surplus, producer
  surplus and five ticks keeps all of it even where the text discusses one
  piece. Drawing only the piece under discussion throws the figure away.
* **Label every price and quantity the source names** — `P*`, the control
  price, `Qᴅ`/`Qꜱ`, and the intercepts. A dashed guide with no number at its
  foot is worse than no guide: drop the guide instead.
* **Shading**: consumer surplus teal, producer surplus orange, gains from
  trade teal, deadweight loss red, tax or tariff revenue navy. Two pieces of
  one surplus (a trapezoid split into a triangle and a rectangle) take
  `edge: true`, or they read as one wash.
* **Braces sit against their price line.** Above it for a surplus or exports,
  `below:"in"` for a shortage or imports, `below:"axis"` where the space under
  the line is taken (the tariff figures). Under the Q axis *only* where the
  source puts them there. A long label wraps with `\n` rather than moving the
  brace — that is what the artwork does.
* **One guide per quantity, and the right leg.** An equilibrium gets the full
  elbow; a quantity read off a control price gets `guides:"q"`; a price whose
  quantity is not the point gets `guides:"p"`. Two points at one quantity draw
  the same dashed line twice, which is most of what makes a panel look busy.
* **A guide needs a number at its foot.** A dashed line running to a blank spot
  on the axis — because its price is suppressed, or cannot be written beside
  its neighbour — is clutter. Drop the guide and keep the dot; the reading is
  still marked, and the number appears in the panel whose answer depends on it.
* **Draw the equilibrium's guide once per widget.** If a later step or panel
  does not move it, it does not need drawing again (Ian, 2026-09-23). It is the
  horizontal that goes — it only restates a price already established — while a
  vertical still marking a quantity that panel refers to stays.
* **One superscript letter after P, never four.** `Pᶜ`, `Pᶠ`, `Pᵂ` read at
  10.5px; `Pᶜᵉⁱˡ` is noise. The line says what it is in full through its `tag`.
* **A dot wherever a price meets a curve, the control price included.** The
  artwork marks all of them, and Ian's call (2026-09-23) is to match it: every
  reading in a panel, not just the ones away from the ceiling. The same
  readings appear in every panel of a market, so a series does not change its
  markings figure to figure.
* **A value appears in the step it belongs to.** Ticks live in `axes` and
  cannot step, so a reading that belongs to a later step comes from its
  *point* instead — those take `at`/`until` like anything else. The textbook
  ceiling shows $100 and 500 while that is the subject, then hands the axis to
  $75, 375 and 562.5, which is also why 500 and 562.5 never have to share it.
  Carry the equilibrium's dot on a second, label-less point present from the
  start, or the engine rings it as newly revealed. (Ian, 2026-09-24.)
* **A caption must say something the paragraph above it does not.** Vertical
  space is the scarce thing on these pages. `check_file.py` measures each
  caption against the prose running up to its widget and reports one that is
  three-quarters contained in it; cut it to what it adds, or drop it. A
  scenario widget whose panels are titled needs no caption at all — the
  buttons name the cases. (Ian, 2026-09-24.)
* **Show the working only where the artwork does.** `calcs` carries the
  formulas when they live inside the image — replacing the image would
  otherwise lose them. Where the chapter prints the same formula as text under
  the figure, a `calcs` block says it twice.
* **Clip the axis to the region the figure uses.** Drawn out to the full
  intercepts, ticks collide (24 and 30 rendered as "2430") and most of the
  plot is empty.
* **Place area labels with `scripts/place_labels.py`, never by eye.** It takes
  the clear point nearest the centroid, and falls back to just outside the
  shape for a wedge too small to hold a label — which is what the source does
  with its own slivers.
* **Where the source figure and the source prose disagree, the prose wins**
  (rule 3's authority order) — and say so in the changelog. The apartment
  figure prints a demand intercept of 1,200 that contradicts its own
  equilibrium; the prose's numbers force 1,080.

`check_file.py` enforces the guide, control-price and `calcs` rules, so they
fail the file rather than waiting for someone to notice.

**A rule is only worth having if it is cheap to obey.** When you add or change
one — here, in the prompt, or in a script — weigh what it costs on every future
run, not just whether it is correct:

* **Make it mechanical or make it brief.** A rule a script checks needs one
  line here; a rule a person has to remember needs to earn its paragraph. The
  label-placement arithmetic came out of the prompt when `check_file` and
  `place_labels` started doing it properly.
* **Declare, don't infer.** `control: true` on a price line replaced guessing
  from whether the line happened to be named, which was a drawing decision
  standing in for an economic one. A stated fact needs no heuristic and never
  drifts.
* **Score against the checker's own geometry, never a copy of it.** That is why
  `place_labels` takes 0.3s where a re-run-the-checks loop took three minutes,
  and why the two can never disagree about the same drawing.
* **Know what each step costs.** The whole static toolchain is under a second:
  `check_file` 0.2s, the test suite 0.8s, `place_labels` 0.3s, `embed_engine`
  0.05s — run those freely, and after every change. The browser steps are the
  expensive ones (`render_widgets` ~30s, `mobile_check` ~13s per width), so run
  them once the static checks are clean, not between edits.

## Where things stand (2026-09-23)

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
* **Engine is v2.18.** Since v2.6: `areas` shade a polygon (v2.11) with
  `edge` to outline it (v2.18) and labels centred on their anchor (v2.13);
  `dot:false` drops a marker but keeps the axis label (v2.12); points take
  `guides:"p"`/`"q"` for one leg of the elbow (v2.14); braces take
  `below:"in"` and `below:"axis"` (v2.14/v2.17) and wrap on `\n` (v2.17);
  `hlines` take `tag`/`tagdy`/`tagq` to name the line itself (v2.14/v2.16);
  and `calcs` prints the working under the plot (v2.15).

* **PPF works.** The first chapter of Exam 1 material converted to seven widgets
  with no engine gaps hit: frontiers, a combinations table, points on/inside/
  outside, opportunity cost with both braces, a bowed-out frontier, three growth
  cases as scenarios, and two-country gains from trade. Only three panels in one
  figure had to be restructured, into scenario buttons.
* **PPF is feasible without new architecture.** Probed against the real engine:
  the frontier, its combinations table, points on/inside/outside, movement along
  it, and outward/inward/pivot shifts all work unchanged — a frontier shift is
  the same `from` mechanic as a supply shift. Four small gaps and the prompt work
  are in `docs/open-issues.md`; the docs themselves have not arrived yet.
* **`ECO2013-263-SupplyAndDemand.html` is 0 FAIL.** Three WARNs remain, all
  crowding: `P₁`/`P₂` are about a pixel apart in widgets 7 and 8, and `S₁`/`S₂`
  in widget 9's second panel. Readable, and moving them means moving equilibrium
  labels in shipped work, so they are reported rather than changed. Its three references
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
* **Headings come from the source's formatting, not from what reads like a major
  topic.** Run `python scripts/doc_headings.py <the Word file>` and use exactly
  that list: bold alone is `<h1>`, bold + underline at size 23 is `<h2>`, and in
  a binary `.doc` centred Helvetica-Bold 12 is `<h1>` and underlined Times-Bold
  is `<h2>`. Never promote a section because it looks important, and never add a
  heading the source does not have. Box and exam-tip titles are not headings.
* **A formula is a third thing a Word reader cannot see.** These chapters carry
  their equations as MathType OLE objects, so `word/document.xml` has no
  `<m:oMath>` at all — just an `<w:object>` and a WMF picture — and pandoc,
  `antiword` and `catdoc` all skip them silently. Run `python
  scripts/doc_formulas.py <the Word file>` for the text inside those pictures,
  and `--check <notes file>` to be told which of their words the file's LaTeX
  does not carry. Reiterate each formula whole: keep the left-hand side, keep
  the source's subscript, and never substitute an equal expression. `OC_X =`
  went missing because the fraction was transcribed by eye and the thing it
  equals was not; point elasticity was rewritten from `1/Slope` to `ΔQ_D/ΔP`,
  which is the same number and loses the reason the equation is there.
* **A `.doc` needs two readers.** `antiword` gives the body flow and, via its
  PostScript output, the formatting; it silently drops every floating text box —
  which in these files is where the exam tips, the worked examples and the
  figure labels live. Always also run `catdoc` and reconcile the two, or the
  conversion will quietly lose whole sections.
* Coordinates come from the source, never from guesswork, and curves pass exactly
  through every numbered point. A point's axis labels are automatic: it prints
  its own price and quantity unless they are already ticks, and `pl`/`ql` replace
  them with `P₁`/`Q₁` on symbolic graphs.
* After any change to `scripts/check_file.py`: `python scripts/test_check_file.py`
  (must be 0 failing). Its checks have been narrowed repeatedly, and a rule
  narrowed once too often stops firing silently while every file still reports
  0 FAIL.
* After any change to a notes file: `python scripts/check_file.py <file>` (must
  be 0 FAIL) and, for anything visual, `python scripts/render_widgets.py <file>`
  and look at every PNG for collisions at every step. That script also measures
  every arrow against every curve and every dashed guide from the **rendered**
  geometry and must report no problems. Do not settle a "does that touch?"
  question by eye: a 1px gap and a touch look identical in a screenshot, and on
  a `curved` pair the drawn spline is nowhere near the polyline through its
  points, so the arithmetic misleads too.
* **A phone is where these get read, and a desktop is where they get
  reviewed.** `python scripts/mobile_check.py <file> --width 390` loads the file
  at phone size and reports four things: the page scrolling sideways, a figure
  or table wider than its column, a control under the 44px tap minimum, and the
  buttons and the graph not fitting on screen together. It drives every
  scenario and steps each widget to its last step, so "still interactive" is
  measured rather than assumed — a button that is disabled or already pressed is
  doing its job when nothing happens, so neither is counted against it. Run
  `--width 320 --height 568` too; that is the size everything is tightest at.
  All six example files pass at both, and the worst widget leaves 53px of
  headroom on the small screen.
* **An arrow does not lie over the dashed guides.** Ian's rule. A converging
  pair belongs *inside* the box the guides fence off, not across it, which
  usually means starting it a few units in from the point and keeping it short.
  Where a panel genuinely has nowhere else to put it, crossing a guide is
  allowed — but establish that from the measurement, not from a glance.
* **Before a semester swap, find out whether there is one.** `python
  scripts/transcript_diff.py <file> <transcript>...` reports, per widget,
  which of its ticks, schedule rows and brace prices the transcripts state and
  which of the nouns its titles and labels name they use. Symbolic widgets are
  reported as having no values at all, because their 110-scale coordinates are
  the engine's convention and rule 3 says that is exactly what you draw when the
  source states no numbers. Everything stated means the transcripts do not
  change the file, and the swap is finished before it starts — the delivered
  `ECO2013-263-SupplyAndDemand.html` against the 9/2 and 9/9 transcripts is
  45/45 values and 38/38 names, because those are the transcripts it was built
  from. Matching is loose on purpose, so it over-reports support: an UNSUPPORTED
  line is worth trusting, a stated one only means "not obviously changed". And
  read it as a question — an unsupported number is a number to go look up in the
  source, never one to edit to taste.
* **A semester swap is `scripts/widget_text.py`, not a rewrite.** It lists every
  title, lede, caption, step, axis title, button label and column header under
  an address like `w4.scenarios.sub.steps[2]`, and `--apply` writes an edited
  map back. Coordinates, ticks and step wiring are never listed and never
  touched, so a swap cannot move a curve by accident; a no-op round-trip is
  byte-identical. If the new semester also changes the *numbers*, that is a
  reconversion rather than a swap, because the drawing has to change with them.
* To test a config quickly, drop it into a copy of
  `examples/ECO2013-Widgets-All.html` and open it in a browser; it carries its
  own copy of the engine in its head.
* Prompt changes: edit `docs/conversion-prompt-v7.md` (bump the version in the file
  name and add a "what changed" line at the top). If a standalone tool prompt is
  needed, append the two engine files as Appendix A/B — see
  `docs/archive/README.md`.
* Commit messages: plain imperative. Don't commit `shots/` (screenshots) — it's
  in `.gitignore`.
* Ian is the only user. He reviews output by reading it and clicking through
  widgets, and wants the file plus a changelog he can scan.

### Asking questions

Ian changed this rule on 2026-09-17, and the change applies **here only**:

* **In this repo, ask when a wrong guess would be costly.** That means a number
  (rule 3), which graphs to convert, or which of two readings of a table or
  figure is intended. Batch them if there are several; do not ask one at a time.
* **Decide everything else and flag it.** Heading levels, table markup, `<b>` vs
  `<strong>`, label placement, scenario grouping, prose edits. A changelog line
  is the right place for those, not a question.
* **`docs/conversion-prompt-v7.md` still says "You never reply with a question",
  and that is deliberate — do not harmonise the two.** v6 runs in Claude Cowork,
  where a question stalls a run that nobody is watching, so it must always
  finish the output. This file governs work done here, with Ian present. If v6
  is ever given a question-asking step, it needs a bump to v7 and a note about
  unattended runs.

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
