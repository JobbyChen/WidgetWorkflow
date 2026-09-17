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
