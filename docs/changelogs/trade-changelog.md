ECO2023-263-Trade.html

Source: `ECO2023-263-Exam1-Chapter7-Full.html` (chapter 7, the last of the
Exam 1 material), house HTML with five S3 images. Converted 2026-09-21.

## Mode

Mode (b), an existing notes HTML file. The five PNGs were fetched from their
S3 `public/` URLs and used only to settle what the prose leaves open: straight
lines, which panel shades what, where the braces sit, black world price before
the tariff and red after. The request was to create the widgets and leave
everything else the same, so the body is the source's body apart from the
image blocks and the three edits listed under *Prose* below.

## Head

- `<title>` was `ECO2023 Spring26 Exam1 Trade`; now `Trade`, the chapter name
  alone (prompt step 0). The source's own title says Spring but its one class
  date is Monday 9/21/26, and the date decides the term code: **263**.
- The script line was `studyguide/sn25-v2.js`; now `content/sn25-v6.js`, then
  the engine placeholder.
- The MathJax config and loader were dropped: the chapter has no equation.
- The table of contents is written in by `scripts/add_toc.py` (9 headings), as
  in the other ECO2023 files, because `content/sn25-v6.js` still returns 403.

## Graphs

All five images are graphs; five images became five widgets. Every one is
symbolic — the chapter states no price or quantity — on the engine's 110 × 110
axes with the domestic equilibrium at [50, 50], demand from the P axis at 100
down to [92, 8] and supply from the origin to [100, 100], so the surplus
triangles close on the axes the way the printed ones do.

| widget | replaces | panels | steps |
| --- | --- | --- | --- |
| Net exporter or net importer? | image 1 | Net exporter / Net importer | 3 |
| Consumer and producer surplus when the country exports | image 2 | No trade / With trade | 4 |
| Consumer and producer surplus when the country imports | image 3 | No trade / With trade | 4 |
| The gains from trade | image 4 | Net exporter / Net importer | 2 |
| The effect of a tariff | image 5 | Before the tariff / After the tariff | 5 |

The world price is at 70 when the country exports (Qᴅ = 30, Qₛ = 70) and at
30 when it imports (Qₛ = 30, Qᴅ = 70). The tariff widget uses a world price of
26 and a tariffed price of 38 (Qₛ 26 → 38, Qᴅ 74 → 62), chosen so the
revenue rectangle is wide enough to carry its own label and the three price
labels on the axis are clear of each other. None of these numbers is shown to
the reader; the axes carry P*, Pᴡ, Pᴡ+T, Qᴅ and Qₛ only.

**This chapter needed an engine change.** Every figure is about a shaded area
and the engine had none. `areas` is new in v2.11 (`docs/engine-reference.md`);
the widgets use hatched ink for consumer surplus, solid orange for producer
surplus, teal for the gains triangle, a teal checkerboard for tariff revenue
and dark ink for the deadweight loss, matching the printed legends. Area
labels are `CS`, `PS`, `Gains` and `Revenue`, spelled out in each widget's
lede; the deadweight-loss triangles are too small for a label and are named in
the caption instead. The printed figures' legend rows are not reproduced: the
lede does that job.

Also new: `guides:"p"` on the equilibrium point draws only the dashed line to
P*, as the printed figures do, and keeps the drop to the Q axis out of the
gains triangle.

## Decisions taken, for review

- **Images 2 and 3 are two widgets, not one with scenario buttons.** They sit
  in different sections (*Focus on Exports*, *Focus on Imports*) with prose
  between them, so grouping would leave one section without its graph.
- **The no-trade panel of widgets 2 and 3 is static** while the with-trade
  panel steps: world price, then the new surplus, then the traded quantity.
  The old surplus label and the new one sit in the same spot so nothing jumps.
- **The Imports brace is under the Q axis** (`below:true`) and the Exports
  brace above the price line. Above the world price on an import graph, the
  demand curve runs through the brace and its label.
- **Widget 1 marks P* only**, with no Q* on the axis, as the printed figure
  does.
- **Dr. Rush is named once**, in the quotas paragraph ("Dr. Rush ran out of
  time…"). Kept verbatim; `check_file.py` raises its WARN. Ian's call.
- The closing "This is the end of the material for Exam 1" line is
  `<strong><em>…</em></strong>` in the source and raises the checker's other
  WARN. Left as delivered.
- The five `<strong>Impact on …</strong>` list labels are labels, not
  vocabulary, and prompt step 0 would make them `<b>`. Left as delivered
  because the request was to change nothing but the graphs.

## Prose

Three edits, all for hard rule 4 and all following the earlier ECO2023 files:

- `From-the-Book Topics NOT Covered in Class` → `From the Textbook: Topics Not
  Covered`.
- "Here are some concepts covered in the textbook but not covered in class:" →
  "Here are some concepts the textbook covers that are not covered here:".
- "He will revisit them in the lecture after the exam." → "He will revisit
  them after the exam."

Nothing else in the body changed. The five `<!-- IMAGE POSITION -->` comments
stay where they were.

## Checks

`check_file.py` → **0 FAIL, 2 WARN** (the Dr. Rush flag and the `<strong>`
line above). `render_widgets.py` → 18 screenshots, no engine errors, no arrow
within 4px of a curve or 3px of a guide, reviewed at every step.
`test_check_file.py` → 0 failing, with three new cases for this session's
checker changes. Every other example was re-embedded with v2.11 and reports
exactly what it did before.
