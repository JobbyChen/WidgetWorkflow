ECO2013-263-TradeoffsComparativeAdvantageTheMarketSystem.html

Source: `1 - ECO2013 Fall 26 Tradeoffs Comparative Advantage The Market System.docx`
(document 1 of 4 covering Exam 1). Converted 2026-09-17.

## Mode

Notes supplied as a Word document. v6 lists Word only as a *transcript* format,
so this was handled as mode (a): the house-format HTML was built first, then
every graph converted. The body is a transcription, not a rewrite — every
paragraph, list item, table row, exam tip and date is the source's, in order.

The document's title block ("Module 1: Introduction to Economics" plus the Exam 1
topic list) sits in a Word text box and was treated as cover matter, not body
content.

## Graphs

Eight figures became seven widgets. The figures are Word VML shape groups, not
images, so axis orientation and every label was read from the shapes' own
coordinates rather than inferred.

| widget | replaces | numbers |
| --- | --- | --- |
| The production possibilities frontier | generic Good 1 / Good 2 figure with the A–E legend | 200, 400 and E = (200, 400) stated in the prose |
| Producing boxes of tissues and Lego sets | the tissues/Lego figure and its combinations table | complete, from the table |
| Opportunity cost along a straight-line frontier | the same frontier reused for the B→C→D costs | complete |
| A bowed-out frontier | chai lattes and burritos | A (20, 90), B (40, 80), C (60, 50) |
| Economic growth and shifts of the frontier | the three pizza/burritos panels | none stated — symbolic |
| Reducing unemployment does not shift the frontier | Good 1 / Good 2 with A inside and B on the frontier | none stated — symbolic |
| Gains from trade | **both** US/Mexico figures, merged | US 200/300, Mexico 150/100 |

The seven exam-tip call-outs became `.exam-tip` blocks; their `<h4>` titles are
written, not from the source, since the source's boxes carry no title.

## Decisions taken, for review

- **Dr. Knight is named 14 times** and content is attributed to him, including
  the house in Quito, the kitchen example and his husband. Kept verbatim, per
  instruction. `check_file.py` raises its one WARN on this.
- **The three-panel growth figure became one widget with three buttons.** The
  engine draws at most two panels, and rule 8 groups cases of one lesson. The
  printed figure's side-by-side comparison is lost; the buttons replace it.
- **The two US/Mexico figures became one widget with three steps** (produce,
  specialise, trade), because they are one lesson drawn twice. The prose that
  referred to the second figure now refers to the widget's final step.
- **The bowed-out frontier is drawn only between Points A and C.** Its axis
  intercepts are never stated, and drawing a curve to invented intercepts would
  break rule 3. The frontier therefore does not reach either axis.
- **Points C and D on the generic frontier carry no coordinates.** The source
  describes them by category, not by value, so they are positioned from the
  figure and print no numbers.
- **The combinations table lost its "Point" column.** The engine reads a table
  row as `[y value, x value, …]`, so the A–E letters could not be a column; they
  are point labels on the graph instead.
- **Two illustrative points carry no label.** At 10 Lego sets, the inefficient
  and unattainable points sit where Point B's guide and Point C's guide leave
  less room than the words need, so v6 step 5's last resort applies and the step
  captions name them.
- **Headings** were inferred from the source's own formatting: bold is `<h1>`,
  bold-and-underlined is `<h2>`. The source uses no heading styles.
- **Inline underlining** became `<b>`, per rule 6.
- **The 13 equations** are MathType objects; their text was read from the
  embedded objects and set with MathJax, which the head now loads.
- **Captions end with the economic conclusion**, not with a price and quantity
  change — rule 7's ending is specific to supply and demand and does not apply
  to a frontier.

## Nothing needs numbers

Every value in every widget is stated in the source or derived arithmetically
from stated values. The opportunity costs in the equations confirm the trade
figures independently: 300/200 = 1.5 and 100/150 = 0.67 match the text.

## Checks

`check_file.py`: 0 FAIL, 1 WARN (the Dr. Knight flag).
`render_widgets.py`: 24 screenshots, no engine errors, reviewed for collisions.

## Revision, same day

Six things found by eye in the rendered file, none of which the checker reports
because each is a near-miss rather than an overlap:

- The two movement arrows in the opportunity-cost widget abutted, reading as one
  long arrow with two heads. Each step now shows only its own arrow (`until`).
- The same fix applied to the bowed-out frontier, and Point C's label moved
  below its dot so the arrowhead no longer reaches it.
- `PPF₁` sat along its own line in the growth widget. Both frontier labels now
  sit at the end the other one does not use, off the line rather than on it.
- The movement arrow in the unemployment widget cut across the frontier and the
  guides. Its `offset` is now 0 and it runs between the two dots.
- Panel headings were smaller than the axis titles (engine v2.5).
- Every exam tip moved to follow the paragraph it reinforces, rather than
  leading the section.

## Correction

Point B in the unemployment widget was drawn **on** the frontier. The source says
reducing unemployment causes "a movement from a point within the PPF to a point
*closer to* the PPF", and its figure shows B inside. On the frontier, B would
mean unemployment had fallen to zero, which is a different claim from the one
the notes make. B is now inside, closer to the frontier than A, and the caption
says so.

No script could have caught this: it is a question of whether a coordinate means
what the source means, which `check_file.py` reports as SKIP ("whether each
number is the source's number needs the source").

## Second revision

The panel headings were still smaller than the axis titles on a wide screen.
Making them a fixed 1.05rem in v2.5 had not fixed it, because the axis titles are
SVG text that scales with the panel while the heading did not: at 1512px the
axis title reached 20.8px and the heading stayed at 16.8px. The heading is now
sized in container-width units (engine v2.6), so the order holds at every width:
heading, axis title, point label.

Checking that across widths turned up a separate bug. A two-panel widget with
`link: false` never stacked on a phone, because the `:not(:has(.sdg-between))`
rule that sets two columns is more specific than the mobile rule that sets one.
Each panel was about a third of a 390px screen. Fixed in the same version.

## Correction, 2026-09-21 — the opportunity cost formula lost its left-hand side

The definition under *The PPF and Opportunity Costs* was written as the bare
fraction. The source states it as an equation:

    OC_X = (# Units Lost of Good Y) / (# Units Gained of Good X)

Restored, as `\[\text{OC}_\text{X} = \frac{...}{...}\]`, which matches the two
other definitional formulas in the file and the ten worked ones.

All fourteen of the chapter's equations were then read out of the source and
compared line by line; the other thirteen were already exact, including the
Lego-set definition that the source genuinely states twice. `scripts/doc_formulas.py`
is what did the reading, and `--check` now reports this class of defect against
the file.

## Redo, 2026-10-05 — the seven widgets re-read against the source figures

Ian asked for this chapter to be done again. The prose, the heading levels, the
exam tips, the three date pills and the fourteen equations were left exactly as
they are; what changed is the seven widgets, re-read off the source document's
own shape groups (3, 4, 6, 7, 9, 10, and 13/15) and brought up to the drawing
conventions that have been settled since 17 September.

The file now reports **0 FAIL**. Its one WARN is the standing question of
whether the professor may be named — Ian's call every time, never a script's.

### What the source figures actually draw, and what was wrong

- **Dashed guides.** The figures draw an elbow only where a reading is worth
  marking: three in the tissues and Lego figure (B, C and D), three in the
  bowed-out one (A, B and C), none at all in the Good 1 / Good 2 figure or the
  unemployment one. The widgets drew one at every point, including at points
  whose values are suppressed, so five dashed lines ran to blank spots on an
  axis and two more ran down the axis lines themselves. Guides are now off at
  every intercept, off at both points of the unemployment figure, and off at C
  and D of the first figure. Only Point E keeps its elbow, because the pair of
  numbers it reads — 200 of Good 1 *and* 400 of Good 2 — is the combination the
  prose says the nation cannot have.
- **The bowed-out frontier was five typed points and a spline.** It is now
  seventeen samples from `curve_shapes.hug`, which keeps A, B and C exactly
  where the source's own guides put them and bows every chord outward, so the
  whole frontier is concave by construction — asserted in the builder rather
  than judged by eye. Its intercepts are the source's: about 95 chai lattes and
  about 71 burritos, against the 93 and 68 that were there. Dropping `curved`
  with the curve sampled this finely also stopped the spline overshooting below
  the quantity axis at the end, and means the checker measures the line that is
  actually drawn.
- **The growth panels are named in the source's words**, capitals included:
  "Increased Resources or Productivity for Both Pizza and Burritos", and the
  two pivots likewise. The buttons had been paraphrasing them.
- **The unemployment figure's two points moved** to where the source puts them,
  about (24, 24) and (37, 43). Both are inside the frontier — the earlier
  changelog's table says B is on it, which is wrong, and the step caption had
  it right all along.
- **Both trade panels carry each nation's intercepts and nothing else**, which
  is what the source's axes carry. The consumption coordinates were ticked from
  the opening state; they now come from the point that reads them, so they
  appear on the step that places it. The specialization dots sit on an axis, so
  they keep neither a guide nor a value of their own.
- **The origin is numbered** on the bowed-out figure, as the source numbers it.

### Captions

The two over the 200-character cap were rewritten, which is what being asked to
redo the chapter settles: rule 9 leaves pre-cap files alone *unless asked*. The
bowed-out figure's third step now carries the comparison that makes it worth
reading (1.5 chai lattes a burrito against 0.5 before), and the unemployment
figure's second step says the frontier does not move and B is still inside it,
in 186 characters instead of 279.

Two scenario captions ended "pizza becomes dearer", which is both the wrong
register and vaguer than the source: they now say what a pizza costs in
burritos, which is the sentence the chapter is making. Two British spellings
("specialisation", "specialises") are American now, as the source has them.

### Not changed, and why

- **The combinations table has no Point column.** The source's has one (A–E);
  the engine's schedule table is a price column plus one quantity column per
  series. The letters are on the graph beside their rows, and hovering a row
  still lights its dot.
- **The pizza-only pivot's arrow runs horizontally.** The source draws that one
  vertically, because what moves is the vertical intercept. A shift arrow is
  always horizontal in the engine, so this is an engine gap rather than
  something to hand-draw around; it is written up in `docs/open-issues.md` as
  `arrowQ`. The arrow still shows the shift and the caption names the intercept.
- **The exam-dates table overflows a 320px screen by 15px.** It is Ian's own
  prose table and the overflow is the house stylesheet's cell padding, not a
  widget; it was there before this redo and is unchanged by it. Every widget
  fits and stays usable at both 390px and 320px.

### Checks

`check_file.py` 0 FAIL / 1 WARN (the name). `render_widgets.py` 24 screenshots,
no engine errors, no arrow within reach of a curve or a guide, and every one
looked at. `mobile_check.py` 0 problems at 390px, and at 320px only the prose
table above. `doc_formulas.py --check` against the source: 14 equations, 0
words missing. `test_check_file.py` and `test_curve_shapes.py` 0 failing.

One tool fix came out of this: `render_widgets.py` slugged a scenario's
screenshots from the first 40 characters of its button label, and all three
growth buttons now agree for the first 44, so each scenario's shots overwrote
the last one's and the set looked complete at 24 files when it held 20. The
slug carries the scenario's number now.
