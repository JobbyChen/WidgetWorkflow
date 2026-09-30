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
  test_widget_text.py         ← tests for it. Run after changing it.
  transcript_diff.py          ← does a new term's transcript change this file? Run it BEFORE swapping.
  test_check_file.py          ← tests for check_file.py. Run after changing it.
  render_widgets.py           ← Playwright: screenshot every widget × scenario × step for collision review
  mobile_check.py             ← does it fit and still work on a phone? Drives every button at 390/320px
  place_labels.py             ← put every shaded area's label where it is clear, and centred
  place_curve_labels.py       ← the same for curve labels: the clear ldx/ldy nearest the default
  curve_shapes.py             ← cost families, tangencies, supply fans, crossings. Import, don't retype.
  test_curve_shapes.py        ← tests for it. Run after changing it.
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
9. **Captions are prose, and short:** 1–3 complete sentences ending with the P
   and Q change in words. No "Before –/After –", no fragments, no colon
   punchlines, no "Price up, quantity up".

   **200 characters is the ceiling** — about four lines at phone width, and
   40% above the median caption already here, so one written to the point is
   nowhere near it. `check_file.py` fails over it. The concise editions are
   produced by a pipeline that rewrites the prose and leaves widget captions
   exactly as they are, so a caption that runs long here runs long in every
   edition (Ian, 2026-09-28) — the baseline caption is the only place to fix
   it. **A caption showing its working gets 260** instead: three or more
   numbers, or a widget carrying a `calcs` block, and the length is carrying
   the arithmetic rather than padding it. Cutting the values going in, the
   step between them or the answer loses the reason the caption is there.

   **Files written before the rule are left as they are** (Ian, 2026-09-28),
   so `check_file.py` reports caption failures on the nine examples. That is
   known and recorded in `docs/open-issues.md` with the count per file; do not
   read it as those files being broken, and do not rewrite them without
   asking. Everything from ECO2023 chapter 14 onward obeys the cap.
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
* **A figure that is not becoming a widget stays the image it is.** Not a
  table, not a list, not prose. The natural-monopoly chapter's last figure is
  a ranking on two arrows rather than a graph, so it was rewritten as an HTML
  table — which reads well and was still wrong: the conversion replaces graphs
  with widgets and leaves everything else exactly as it was. (Ian,
  2026-09-28.) The `<img>` tag, its classes and its alt text carry over
  untouched, the same as any other part of the chapter.
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

  **`"axis"` sets the bracket down but leaves the label reaching back up**,
  which is only a fix where what crowds it is right against the price line.
  A tariff band holds the revenue rectangle and both deadweight triangles,
  and their names sit where that label lands — so the trade chapter's imports
  brace is `below: true`, fully under the Q axis, the same as the quota
  figure's. It gives up the brace's own drop guides, which the marked
  quantities already draw.
* **A brace's label sits at the brace's midpoint, beside it.** Not under the
  brace, not under the line it hangs off — Ian's call, 2026-09-29, and he gave
  it twice in one round ("the tax or fee should be at the point of the brace",
  then the same of the external benefit). A label pushed off its own brace
  stops reading as that brace's name and starts reading as a caption for
  whatever it has landed next to. Inside the plot it is set at 11px (v2.31)
  and wraps on `\n`, which is what makes a three-word name fit between two
  curves; where even that does not fit, the curve gives way — see the label
  rule below — never the label.
* **One guide per quantity, and the right leg.** An equilibrium gets the full
  elbow; a quantity read off a control price gets `guides:"q"`; a price whose
  quantity is not the point gets `guides:"p"`. Two points at one quantity draw
  the same dashed line twice, which is most of what makes a panel look busy.
* **A guide needs a number at its foot.** A dashed line running to a blank spot
  on the axis — because its price is suppressed, or cannot be written beside
  its neighbour — is clutter. Drop the guide and keep the dot; the reading is
  still marked, and the number appears in the panel whose answer depends on it. The
  exception is a line that is not marking a reading at all: the labor supply
  curve turns at a wage the chapter never names, and the source still draws a
  dotted line across it because that is where the two effects balance. Say so
  with `divider: true` on the point — declared, so the rule still fires
  everywhere else.
* **Draw the equilibrium's guide once per widget.** If a later step or panel
  does not move it, it does not need drawing again (Ian, 2026-09-23). It is the
  horizontal that goes — it only restates a price already established — while a
  vertical still marking a quantity that panel refers to stays.
* **One superscript letter after P, never four.** `Pᶜ`, `Pᶠ`, `Pᵂ` read at
  10.5px; `Pᶜᵉⁱˡ` is noise. The line says what it is in full through its `tag`.
  A `_{...}` subscript is the same rule: `P_{W}`, not `P_{WORLD}` — a word set
  in capitals on a price axis is the widest thing in the panel and reads as
  shouting. Ian, again, 2026-09-30. Where dropping to a letter leaves the line
  unexplained, give the line a `tag`, which is where its name belongs.
* **A dot wherever a price meets a curve, the control price included.** The
  artwork marks all of them, and Ian's call (2026-09-23) is to match it: every
  reading in a panel, not just the ones away from the ceiling. The same
  readings appear in every panel of a market, so a series does not change its
  markings figure to figure.
* **A shape's corners are marked on the shape's own step.** The engine rings
  what a step revealed, so the corners of a deadweight-loss wedge that came in
  earlier sit there unringed while the one that step added is highlighted —
  which reads as the other two belonging to something else. `hiAt` on each
  corner re-marks them all on the step that shades it (Ian, 2026-09-29). The
  same correction also moved the corner that is on no curve the reader has
  been asked about yet: it is the wedge's, so it appears with the wedge.
* **A value appears in the step it belongs to.** Ticks live in `axes` and
  cannot step, so a reading that belongs to a later step comes from its
  *point* instead — those take `at`/`until` like anything else. The textbook
  ceiling shows $100 and 500 while that is the subject, then hands the axis to
  $75, 375 and 562.5, which is also why 500 and 562.5 never have to share it.
  Carry the equilibrium's dot on a second, label-less point present from the
  start, or the engine rings it as newly revealed. (Ian, 2026-09-24.)
  **So a numeric figure with steps usually has no `xticks` at all.** Splitting
  the trade chapter's four quantities between its two quota figures stopped
  them colliding ("3040") and still put each figure's numbers on the axis
  from its opening state, before anything had marked them — the rule again,
  one level up. Every quantity comes from the point that reads it; the axis
  carries a tick only where no point does. (Ian, again, 2026-09-30.)
* **A caption must say something the paragraphs around it do not.** Vertical
  space is the scarce thing on these pages. `check_file.py` measures each
  caption against the prose on either side of its widget and reports one
  mostly contained in it; cut it to what it adds, or drop it. A title and a
  lede describe a figure on their own, so a widget left without a caption
  still passes the schema — and a caption that answers the question the
  chapter is about to ask should go whether or not it repeats anything. The
  rule measures captions only: a lede is one line, and naming what the figure
  shows is its job. (Ian, 2026-09-24.)
* **Show the working only where the artwork does.** `calcs` carries the
  formulas when they live inside the image — replacing the image would
  otherwise lose them. Where the chapter prints the same formula as text under
  the figure, a `calcs` block says it twice.
* **Clip the axis to the region the figure uses.** Drawn out to the full
  intercepts, ticks collide (24 and 30 rendered as "2430") and most of the
  plot is empty.
* **A label stays on the thing it names; the curve underneath gives way.**
  Where a measure is named at the quantity it is measured at and a curve runs
  through the only place the name fits, fade that curve for those steps
  (`dimAt`) rather than pushing the label off its own brace — Ian's call,
  2026-09-29, and he had to give it four times. A label nudged clear of its
  brace stops reading as that brace's name, and a curve shortened to make room
  starts from nowhere on the steps before its end is marked. Fade only the
  curve the label actually crosses: `check_file.py` names it, and fading the
  others greys out half the figure for no reason.
* **Place area labels with `scripts/place_labels.py`, never by eye.** It takes
  the clear point nearest the centroid, and falls back to just outside the
  shape for a wedge too small to hold a label — which is what the source does
  with its own slivers. **Read which of the two it did.** A deadweight-loss
  triangle with room to spare had its label parked outside it because the
  first clear candidate happened to be there, and outside is where a label
  stops naming its own shape. The fallback is for a sliver; anywhere else,
  centred is the answer and a label that is not centred is a drawing to fix.
* **An area's name is drawn over the curves, so let it be -- and leave the
  box off.** From v2.46 the name goes on top of the lines, which is how the
  printed figures name a deadweight wedge: solid fill, the word straight on
  it, the wedge's own edges running under the letters. So a wedge narrower
  than the word it is called keeps its name at its own centre, in plain text,
  rather than being pushed outside on a leader or shrunk to fit a box --
  Ian's call, 2026-09-30, after five rounds of the name being moved or
  resized. A box round it is a second shape whose edges lie across the
  wedge's own, and no size small enough to fit one in is big enough to read:
  measured at every size from 10px down to 7. `boxed: true` is for a label
  over a *gap* in the drawing -- the importers' rectangle, a Lorenz year --
  not over a wedge. `check_file.py` reports an area label over a curve as a
  WARN rather than a FAIL for the same reason: the line passes behind the
  letters, and whether it reads is a look, not a measurement. Outside on a
  hairline is still right where the source itself names a shape from outside
  (a legend swatch, a tariff's revenue band).
* **Where no gap is wide enough, box the label.** Three Lorenz curves converge
  on one corner, and at its widest the gap between two of them is about 27px
  against a 28px year — so there is nowhere between them a horizontal label
  can go, and hunting for one is wasted. `boxed: true` on a point gives the
  label a white background, which is what lets the source put each year on its
  own curve with a short leader, and what lets a name for a curve sit on the
  curve. Ian's call, 2026-09-29, from the reference artwork. Use it where the
  drawing genuinely has no gap, not to paper over a label that could move.
* **Place curve labels with `scripts/place_curve_labels.py`, never by eye.**
  A curve label sits at its own end, which is where the other curves converge:
  MR ends on the Q axis with MC a few units above it and an equilibrium's guide
  beside it, leaving about nine pixels of room. Guessed offsets trade one
  collision for another — MR came off MC and straight onto the axis on the
  first try — and each guess costs a render. The script scores candidates
  against `check_file`'s own geometry and takes the clear one nearest the
  engine's default. Where it reports *nowhere clear*, that is a drawing to
  change (run the curve further, or anchor the label at the other end with
  `lstart`), not an offset to keep hunting for. **One offset for a series:**
  where the same market is drawn in several figures, search for an offset clear
  in all of them at once, or the label moves about from figure to figure.
* **A curve stops where it leaves the plot, not at the far frame.** A cost
  curve run out to `xmax` when it exits through the *top* has its last point —
  and therefore its label — off the panel, so the curve is drawn with no name
  and nothing reports it. Sample to the edge it actually reaches.
* **Every class date in the source survives.** A `<p class="date">` carries no
  content, so condensing or restructuring a chapter drops it with nothing left
  looking wrong — concise editions of modules dated over three meetings were
  shipping with none. `check_file.py <file> --source <what it was built from>`
  fails on a lost one; run it with `--source` whenever there is one. The pill
  goes immediately before the heading or paragraph that day started with, and
  where the output merges two of the source's sections, it anchors to that
  paragraph rather than the merged heading. (Ian, 2026-09-24.)
* **Copy the source figure's own words, including its capitalisation and its
  subscripts.** A panel the source heads "The Entire Market" is not "The
  entire market", and a curve it labels `S_Market` is not `S`. Write the
  subscript as `_{...}` — `S_{Market}`, `d_{Firm} = MR` — which the engine
  sets smaller and lighter (v2.24); small capitals render at full weight and
  read as capitals. Where a curve reaches the axis in the source, draw it
  reaching the axis. (Ian, 2026-09-28.)
* **Generate a shape, never type it.** `scripts/curve_shapes.py` carries the
  shapes these chapters keep needing, and each function is there because
  drawing that shape by eye went wrong: `cost_family` solves MC from the two
  average minima it must cut, so the dots sit on all three curves at once;
  `tangent_to_line` and `tangent_to_hyperbola` touch rather than cross;
  `on_hyperbola` puts a basket on a sample point of its own curve, because a
  curve is a spline through samples and a point taken from the formula
  between two of them sits just off the line that is drawn; `supply_fan`
  gives the `p = A(e^(kq) − 1)` shape the market-supply figure needs, flat
  along the bottom and vertical at the end; `lorenz` gives `y = x**k`, which
  runs corner to corner and cannot cross the line of equality or another
  Lorenz curve, so an ordering a figure exists to show is a property of the
  numbers rather than something to check by eye; `hug` bows each chord of a curve plotted through a table's readings
  below itself, so the whole thing is convex -- a spline through the readings
  alone bows above the chord as often as below, which leaves the bottom early
  and arrives at the top corner gently, the opposite of what a Lorenz curve
  does. Several shallow samples per chord, not one deep one: one deep sample
  bows each segment hard and leaves a kink at every reading, which is more
  visible than the problem it fixes; `around` samples either side of a
  basket in proportion to it, sorted, so a low basket cannot double the curve
  back on itself. **`cross` is the important one**: name every crossing and
  build the equilibrium dots from it. Typed as coordinates they are left
  behind the moment a curve moves, and a dot a few units off its crossing
  looks deliberate. `python scripts/test_curve_shapes.py` must be 0 failing.
* **A curve runs to the edge of the plot, not to wherever it stopped.** The
  source draws every curve out to the frame, so a cost curve ending two
  thirds of the way across reads as truncated beside it — and cutting one
  short to make room for a label is the wrong fix, since running it further
  usually moves it clear of the label anyway. The exceptions are ends that
  mean something: a frontier stops at its intercept, a demand curve at the
  axis, a tangent is a stub by design. No checker for this — the meaningful
  ends and the truncated ones look identical to one, and a rule that flagged
  both would fire on every frontier in the PPF chapter. (Ian, 2026-09-28.)
* **A curve runs well past the point it is drawn for.** A curve sampled just
  either side of its tangency reads as beginning where it touches. Sample in
  proportion to the point — roughly 0.45× to 6× its x — so the upper branch is
  tall and the tail long whatever x the point sits at. (Ian, 2026-09-28.)
* **A point sits on one of its curve's own sample points.** A curve is a
  spline through samples, not the formula behind it, so a point placed from
  the formula at an x between two samples sits just off the drawn curve — and
  off any tangent through it. Put every marked basket in the sample list.
* **A tangency is arithmetic, never drawn by eye.** `y = k/x + b` with
  `k = m·t²` and `b = c − 2mt` touches the line through `(0,c)` and `(xint,0)`
  at `x = t`. Eyeballed, it crosses — which is the one thing a tangency figure
  exists to rule out. A tangent line is a short stub through its point, as the
  artwork draws it, not a full-width line.
* **Set the slopes so the lesson is visible.** The marginal-rate-of-
  substitution figure needs a steep basket and a nearly flat one (−3.0 against
  −0.2); on a gently bowed curve shared with other figures, both look the
  same. A figure whose subject is a slope gets its own curve.
* **Draw what the source draws, and no more.** Extra curves added to
  illustrate a point the artwork makes with one curve are clutter, and they
  crowd the labels that matter. **Dots count as drawing.** A shifted curve
  gets a dot where the source puts one, not one at every crossing a guide
  happens to make with it: the property-rights figure marks one reading on its
  new supply curve and the widget marked two, which reads as two answers to a
  question that has one. The ceiling convention above is the same rule seen
  from the other side — the artwork marks all of them there, so the widget
  does too.
* **A figure that is one market before and after a change is one panel with
  steps, not two panels.** The source prints "No Trade" beside "With Trade"
  because paper cannot animate; a widget can, and the surplus areas are then
  seen to move rather than compared across a gap. Two panels stay two panels
  where they are two *different* markets -- the net exporter beside the net
  importer. (Trade chapter, 2026-09-30; flag it in the changelog either way.)
* **Where the source figure and the source prose disagree, the prose wins**
  (rule 3's authority order) — and say so in the changelog. The apartment
  figure prints a demand intercept of 1,200 that contradicts its own
  equilibrium; the prose's numbers force 1,080.

  **That is for a figure that contradicts itself, not for one that is simply
  a different example.** The trade chapter draws the quota market three times
  on three sets of numbers, and the third was redrawn on the prose's — which
  Ian overruled on 2026-09-30: each widget follows its own figure, so that
  one gets its own market, its own curves and its own ticks. A reader looking
  from the page to the widget beside it is comparing one figure against one
  widget, not the chapter against itself. Say in the changelog that the
  figures disagree; do not resolve it by redrawing one of them.

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
* **Write a shared coordinate down once.** The upright brace's x lived in the
  checker twice, once for the brace and once for its label, so moving it in
  v2.33 fixed half the collision and left the other half warning. It is one
  function now. The same goes for the plot's width, which two places derived
  from a right margin that stopped being 36 at v2.28.
* **Score against the checker's own geometry, never a copy of it.** That is why
  `place_labels` takes 0.3s where a re-run-the-checks loop took three minutes,
  and why the two can never disagree about the same drawing.
  **The checker holds a copy of the engine's layout, and it goes stale.**
  `geom()` reproduces the engine's margins so it can turn data coordinates
  into pixels, so every margin change in the engine is two edits, not one --
  v2.27 shipped without the second and measured chapter 14's wide-label panel
  17px out. Change one, change the other, in the same commit.
* **Measure the drawing, do not estimate it.** The label box was 0.58em a
  character for everything, which is right for the 700-weight ticks and 17%
  narrow for the 800-weight curve labels. A label that overflowed its panel by
  15px was reported as fitting. Chromium's `getBBox` over a rendered file
  settles these in a minute; the constants now come from it. **And measure
  the right thing:** the second version split on weight, .58 against .70, and
  was right about the curve labels only by luck -- they are uppercase; the
  third went by *case* (upper .690, lower .539, digits .558), which fixed
  `P_{WORLD}` and was still 20% narrow for `S + Quota`, because a Q, a W or a
  + is half again an average capital. **A class average is not a
  measurement.** The table is per character now (`scripts/em_widths.py`,
  v2.45), the engine's copy is generated from it, and `test_check_file.py`
  fails on a drift. **And measure the font the reader gets.** That table was
  recorded before Red Hat Display had loaded -- the font comes from Google
  through the agent proxy, which the browser scripts did not use until v2.47
  -- so for eight versions it held the *fallback's* widths, 6% to 100% wide
  depending on the character, with `1` as broad as `0` because the fallback
  sets its digits tabular and Red Hat Display does not. Every margin was
  generous and every overlap test pessimistic, which is the safe direction
  and is exactly why nothing looked wrong. `scripts/measure_em.py` re-measures
  it and refuses to record anything until `document.fonts.check` says the font
  is there (v2.53). A measurement of the wrong thing is worse than an estimate,
  because it carries the authority of having been measured: re-measuring
  dropped four warnings from the government-intervention file, three from
  ECO2013 supply-and-demand and a failure from the 9/11 prototype, and added
  nothing anywhere.
* **Every place a panel writes on an axis has to be counted in its margin.**
  v2.27 sized the left margin to the ticks and the points; a price line writes
  there too, and `P_{WORLD}` came out as `WORLD` (v2.43). When a margin is
  sized to "the labels", enumerate what draws them rather than the ones in
  front of you.
* **Read the WARNs, not just the FAILs.** A curve label sitting on the Q axis
  was reported for a whole round as a warning while every re-check was
  grepped for `^FAIL`. Rule 5's severity was wrong — that is fixed — but the
  habit was worse than the bug.
* **A printed self-check is not a check.** The builder for the externalities
  chapter computed whether the subsidised supply curve met demand at the
  efficient quantity and printed the mismatch. It printed it for three rounds
  and the figure shipped with its equilibrium dot off the curve, because
  nothing in the build stopped and a passing build reads as a passing build.
  `assert` instead: the same arithmetic, in the same place, that cannot be
  scrolled past. Every relationship a figure depends on is worth one line.
* **Prove an edit landed.** Patching a config by string replacement fails
  silently when the text has moved on, and the build still succeeds, so the
  next render looks like the fix simply did not work. Assert the match count,
  and check the property afterwards: chapter 12 shipped equilibrium dots
  beside their crossings for three rounds because three patches in a row
  quietly matched nothing.
* **Render what the reader loads, stylesheet and all.** `render_widgets` and
  `mobile_check` launched Chromium with no proxy, so in this container the
  house stylesheet and script -- which every notes file pulls from S3 -- never
  arrived, and every screenshot taken here showed the engine's CSS alone. The
  house sheet styles `table:not(.financial)`: full width, 16px padding, a
  tinted first column, zebra striping. It had been painting over a schedule
  row's highlight in every column but the first, and over the navy behind a
  `given` label's white lettering so the label was simply invisible -- for
  weeks, with every check passing and every screenshot looking right. Both
  scripts pass the proxy through now. If a widget looks right here and wrong
  to Ian, this is the first thing to suspect.
* **A check that never drives the thing is not checking it.**
  `check_file` and `render_widgets` both passed a file whose every `calcs`
  widget threw on load and lost its step buttons with it, because neither
  presses a button; `mobile_check` found it a chapter later, since driving
  every control is what it does. Run it on anything interactive, not only on
  the question of whether a phone fits.
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
* **Engine is v2.54.** Since v2.6: `areas` shade a polygon (v2.11) with
  `edge` to outline it (v2.18) and labels centred on their anchor (v2.13);
  `dot:false` drops a marker but keeps the axis label (v2.12); points take
  `guides:"p"`/`"q"` for one leg of the elbow (v2.14); braces take
  `below:"in"` and `below:"axis"` (v2.14/v2.17) and wrap on `\n` (v2.17), as
  curve labels do (v2.19); `hlines` take `tag`/`tagdy`/`tagq` to name the line
  itself (v2.14/v2.16) and suppress a point's own price label only while both
  are on screen (v2.20); and `calcs` prints the working beside the plot in a
  widget 920px or wider -- where the plot then grows past `--fig` into the
  width the working is not using -- and under it in a narrower one
  (v2.15/v2.21/v2.22), scrolling sideways as a block where a formula is wider
  than the widget (v2.23); `_{...}` sets a word subscript in a label, a `tag`
  or a point's axis label (v2.24/v2.25); and an arrow's head scales with its
  length (v2.26), because a fixed 7×3.6 head made a short movement arrow --
  two firms sliding a few units along one cost curve -- read as a blot rather
  than a direction; and the left margin is sized to the widest price-axis
  label (v2.27), and the right margin to the curve labels (v2.28), because
  fixed margins cut `P* = ATC` down to `= ATC` and `D = MB = MSB` down to
  `D = M` -- the text was placed correctly and the panel simply had no room
  for it. `check_file.py` fails a label that runs outside the panel now, which
  is the check that would have caught both. An upright brace's label wraps on
  `\n` and takes `ldx`/`ldy` (v2.29/v2.30), because the externalities
  chapter's three-line `Marginal External Cost` could not be written on one
  line and could not be centred rigidly on its brace; it is set at 11px inside
  the plot; and `dimAt` fades a curve from a step so a label can be read over
  it (v2.31); and `hiAt` re-marks a point from a step on, whenever it
  arrived, so a shape a later step draws rings all of its corners rather than
  the one that step added (v2.32). Axis titles wrap on `\n` and a `left`
  upright brace sits outside the widest price-axis label (v2.33), both from
  the labor chapter: `Amount of Employment (L)` is two thirds of a panel on
  one line, and `CWD` was drawn straight through the two wages it spans. A
  wrapped price-axis title is anchored clear to the *left* of the axis, a
  point's `label` wraps on `\n`, and `divider: true` on a point says its guide
  separates two regions rather than marking a reading (v2.34). `pct: true`
  labels both axes as percentages and a wrapped axis title gets out of the
  tick rows' way -- the price title below the topmost tick, the quantity
  title below the whole row, with the panel grown to 268 to hold it (v2.35),
  both from the Lorenz-curve chapter, which plots a cumulative percent
  against a cumulative percent and names both axes in full. A point's label
  takes `boxed: true` (v2.36): a white box with its own border, so the label
  can be read over the curves it sits on, at 9.5px so the box covers as
  little of the curve as it can; and `leader: true` draws a curve as a 1px
  hairline, the weight of a line that points at the drawing rather than being
  part of it, and keeps that weight on the step it arrives (v2.37/v2.38). And a
  widget can be a **payoff matrix** rather than a plot (v2.39): a grid built
  as HTML, like the schedule table, whose steps mark a row, a column or one
  cell -- because the game-theory chapter argues through its matrix one
  comparison at a time, which is what a picture of the finished grid cannot
  show. A mark's `given` fills in the strategy label of the row or column
  being held fixed (v2.40): the argument is "*if* B complies, A does better
  cheating", and with the "if" half missing from the drawing the two lit
  payoffs read as the wrong cells -- which is how they were read. An area's
  label wraps on `\n` and takes `boxed` (v2.41); a price line can drop its
  axis price with `showP: false` (v2.42); and the left margin counts those
  price-line labels, which it never did -- `P_{WORLD}` rendered as `WORLD`
  (v2.43). A character's width comes from a per-character table measured in
  Chromium (v2.45), which `scripts/em_widths.py` holds and generates the
  engine's copy of: an average per *case* is 20% narrow for a capital-heavy
  label, so the margin sized for `S + Quota` cut it to `S + Quo`. And a
  widget's `calcs` block reaches the row it belongs in through the widget
  rather than a local of another function (v2.45) -- it threw `main is not
  defined` and took the step controls down with it, so every `calcs` widget
  was dead while `check_file` and `render_widgets` both passed. An area's
  *name* is drawn over the curves rather than under them (v2.46), so a boxed
  one masks what runs beneath it -- which is what `check_file` had always
  assumed and the engine had never done -- and a boxed area label's box is
  measured with the same table as everything else instead of 5.3px a
  character, which hung "Importers" out of both sides of its own box. And a
  widget's tables opt out of the house stylesheet's own table rules (v2.47),
  which had been painting white over a schedule row's highlight in every
  column but the first and over the navy behind a `given` label, so the label
  vanished; every box in a payoff matrix is one size now, so the same mark
  reads the same whether it heads a row or a column, and the weights the
  house sheet was thinning -- `td:first-child` is 500 there, which caught
  FIRM B and whichever row label started its row, so half the grid was a
  different weight from the other half -- are re-asserted. And a widget can
  be a **years table** (v2.48): the same game played year after year, a row
  at a time, with a red arrow carrying one year's move into the next year's
  answer, which is the whole of tit-for-tat and what the printed table has to
  state all at once. Its arrows run from where one cell's writing ends to
  where the next one's begins, measured off the text: set at a fraction of
  the cell instead they land on the closing bracket at one end and on the
  move at the other, and somewhere different again the moment an amount is a
  character longer. Its header is one navy band across the top, corner cell
  included, and `rowhead` names that corner (v2.49): the pale rule the other
  cells carry drew a line down the middle of the band and set the corner a
  pixel out of line with the two names. And a widget can be an **amortization
  explorer** (v2.50): the first one here that is a model rather than a
  drawing, because the share of a payment that is interest depends on the
  amount, the rate and the term at once and no table of points can hold all
  three. `pct:"y"` labels the price axis alone, and a quantity title starting
  with `\n` drops below the tick row, which is where a figure with a tick at
  the axis's own end has to put it. A `left` upright brace sits 12px clear of
  whatever the price axis writes rather than a fixed 32 (v2.51): on a panel
  that writes nothing there it stood out in empty space, away from the gap it
  measures, which is the one thing a brace has to be next to. The character
  table was re-measured at v2.53, with the web font actually loaded; the
  explorer is
  read by moving a mouse over the figure with nothing held down (v2.54), by
  dragging a finger, or by the arrow keys, and its year
  control counts months, which is what the schedule is indexed by -- set in
  months and written back in years, the thumb clamped at its own maximum and
  never moved (v2.52).

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
* **The examples report caption-length failures**, from before the cap existed
  (rule 9). Everything else about them is 0 FAIL, apart from the 9/11
  prototype. Counts per file are in `docs/open-issues.md`.
* **`ECO2013-263-SupplyAndDemand.html` is 0 FAIL** on everything but that. Three WARNs remain, all
  crowding: `P₁`/`P₂` are about a pixel apart in widgets 7 and 8, and `S₁`/`S₂`
  in widget 9's second panel. Readable, and moving them means moving equilibrium
  labels in shipped work, so they are reported rather than changed. Its three references
  to the class are reworded and its four term labels now keep only the term
  inside `<strong>`. Widget 5's lede and widget 6's equilibrium caption were
  trimmed on 2026-09-24: both restated the sentence introducing them, and the
  caption now says why nothing moves rather than re-reading the graph.
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
