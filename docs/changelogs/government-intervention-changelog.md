ECO2023-263-GovernmentIntervention.html

Source: `ECO2023-263-Exam1-Chapter6-Full.html` (chapter 6 of the Exam 1
material), house HTML with fourteen S3 images. Converted 2026-09-21.

## Mode

Mode (b), an existing notes HTML file. The fourteen PNGs were fetched from
their S3 `public/` URLs and used to settle what the prose leaves open: which
regions are shaded, where the braces and the tax arrow sit, and what images 13
and 14 actually show. The request was to create the widgets and leave
everything else the same, so the body is the source's body apart from the
image blocks and the three edits under *Prose* below.

## Head

- `<title>` was `ECO2023 Spring26 Exam1 Chapter 6 - Government Intervention`;
  now `Government Intervention`. The source's title says Spring but its class
  date is Wednesday 9/16/26, and the date decides the term code: **263**.
- The script line was `studyguide/sn25-v2.js`; now `content/sn25-v6.js`, then
  the engine placeholder. The MathJax config and loader were dropped: the
  chapter has no equation.
- The table of contents is written in by `scripts/add_toc.py` (8 headings).

## Graphs

All fourteen images are graphs. Fourteen images became twelve widgets: images
6 and 7 (the pizza tax, then the same graph with revenue and deadweight loss)
are one five-step walkthrough, and images 11 and 12 (sale illegal, purchase
illegal) are two scenarios of one widget. Both merged images keep their
`<!-- IMAGE POSITION -->` comments.

| widget | replaces | kind | steps |
| --- | --- | --- | --- |
| A binding price ceiling | image 1 | symbolic | 4 |
| A rent ceiling of $1,500 | image 2 | symbolic, $2,000 and $1,500 as axis labels | 4 |
| A binding price floor | image 3 | symbolic | 4 |
| The minimum wage as a price floor | image 4 | symbolic, $13 and $6 as axis labels, W/L axes, LS/LD | 4 |
| A per-unit tax shifts supply up by the tax | image 5 | symbolic, Pᴏʟᴅ/Pɴᴇᴡ/Pᴏʟᴅ+Tax as in the prose | 3 |
| A $1 tax on pizza | images 6 + 7 | **numeric**: $12.00 → $12.50 and $11.50, 5,000 → 4,000, tax $1 | 5 |
| Consumer and producer surplus before and after a tax | image 8 | symbolic, two panels | 5 |
| Who pays the tax depends on the elasticity of demand | image 9 | symbolic, two panels | 3 |
| Who pays the tax depends on the elasticity of supply | image 10 | symbolic, two panels | 3 |
| Making a good illegal | images 11 + 12 | `preset:"shift"`, static, two scenarios | — |
| Penalties on both buyers and sellers | image 13 | symbolic, two panels (the step-4 double-shift template) | 4 |
| A subsidy and a production quota | image 14 | symbolic, two scenarios | 3 / 2 |

**Image filenames 13 and 14 are wrong on S3.** `…-13-subsidy-production-quota.png`
shows the big-demand-shift / big-supply-shift pair that the "penalty on both"
paragraph calls for, and `…-14-exam-tip-lightbulb-icon.png` shows the subsidy
and production quota pair. Both sit where the prose wants them; the widgets
follow the pictures.

**This chapter needed engine v2.12** (`docs/engine-reference.md`):

- `xmin`/`ymin`, because the pizza prices $11.50–$13.00 on a zero-based axis
  are eleven pixels a dollar and the tick labels overlap. The widget's P axis
  starts at $10 and its Q axis at 2,000, like the printed figure, which is not
  to scale either.
- An hline `name`, for PRICE CEILING / RENT CEILING / PRICE FLOOR above the
  line's right end (below it for the floors, where supply runs through the
  space above). A named line is a legal price the market is held at, so the
  checker no longer asks it for two converging movement arrows.
- A `label` on a movement arrow, for the "Tax" arrow between S and S + Tax.
- A margin that grows with the longest P-axis label, so `Pᴏʟᴅ+Tax` and
  `$2,000` fit.

## Numbers

Only the pizza widget and the two labelled controls carry numbers, and all
come from the prose: $12 before the tax, a $1 tax, $12.50 paid and $11.50 kept,
50 cents each side, 5,000 and 4,000 pizzas (the axis shows `5k` and `4k` as the
printed figure does); rent at $2,000 and a ceiling of $1,500; a $13 minimum
wage against a $6 equilibrium. The rent and minimum-wage widgets are drawn on
the symbolic 110-scale with those prices as axis labels, because the source
states two prices and no quantities. The tax revenue is described as "$1 on
each of the 4,000 pizzas" rather than as a product the source never states.

Everything else is symbolic: ceilings and floors at 25 and 75 on the 110
scale (the wider gap keeps the deadweight-loss triangle big enough to label),
a tax of 24–30 units, demand slopes of −3 and −1/3 for inelastic and elastic,
supply slopes of 3 and 1/3.

## Decisions taken, for review

- **Ceiling and floor are separate widgets**, as are the rent ceiling and the
  minimum wage, because each sits in its own section or box with its own
  prose. Grouping them as scenarios would have left three places without a
  graph.
- **The equilibrium is `P*`/`Q*`** where the printed figures write `P_EQ`/
  `Q_EQ`; the tax widgets use `P₁`/`Q₁`, `P₂`/`Q₂` as printed; the generic tax
  widget uses `Pᴏʟᴅ`, `Pɴᴇᴡ` and `Pᴏʟᴅ+Tax` because the prose beside it names
  them so. The subsidy's new equilibrium is `P₂`/`Q₂`, not the printed
  `P_Subsidy`/`Q_Subsidy`, which do not fit on an axis; the caption says which
  is which.
- **The rent-ceiling equilibrium draws only its price guide**, as printed; the
  other controls draw both.
- **The Shortage brace is under the axis and the Surplus brace above the
  line**, each where the demand curve does not run through it.
- **`DWL` is labelled in the four control widgets** and not in the three tax
  widgets, whose triangles are too small for the label once the equilibrium
  guide runs through them. Their captions and ledes name the black triangle.
- **The minimum-wage brace reads "Surplus (Unemployment)"**, as printed.
- **The tax arrow points up**, one head, where the printed figure draws a
  double-headed arrow. It sits to the right of Qᴏʟᴅ (or Q₁) so that it crosses
  no curve; the printed one crosses demand at the equilibrium.
- **The production quota is a red vertical `curve`** labelled "Quota" under the
  axis, since the engine has no `vlines` (open issue).
- **Two crowding WARNs are the economics**: with elastic demand, and with
  inelastic supply, the price barely rises, so P₁ and P₂ sit a pixel apart.
- **Dr. Rush is named once**, in the editor's note opening the illegal-goods
  section. Kept; `check_file.py` raises its WARN. Ian's call.
- Three `<strong>` blocks wrap whole sentences (the two tax-incidence rules and
  "quantity demanded" in the floor paragraph) and raise the markup WARN. Left
  as delivered, since the request was to change nothing but the graphs.

## Prose

Three edits, all for hard rule 4 and all following the earlier ECO2023 files:

- `Other From-the-Book Topics NOT Covered in Class` → `From the Textbook: Other
  Topics Not Covered`.
- "Here are some other concepts covered in the textbook but not in class:" →
  "Here are some other concepts the textbook covers that are not covered here:".
- "Dr. Rush did not cover the market for illegal goods in class." → "Dr. Rush
  did not cover the market for illegal goods."

"Also, in this class, we will focus on a per-unit tax" is left as written, as
the same phrase was in the Trade chapter. Nothing else in the body changed;
all fourteen `<!-- IMAGE POSITION -->` comments stay where they were.

## Checks

`check_file.py` → **0 FAIL, 4 WARN** (the two crowding lines, the `<strong>`
line and the Dr. Rush flag). `render_widgets.py` → 46 screenshots, no engine
errors, no arrow within 4px of a curve or 3px of a guide, reviewed at every
step. `test_check_file.py` → 0 failing, with four new cases for this session's
checker changes. Every other example was re-embedded with v2.12 and reports
exactly what it did before.
