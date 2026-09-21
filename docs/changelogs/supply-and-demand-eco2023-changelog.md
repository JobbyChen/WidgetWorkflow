ECO2023-263-SupplyAndDemand.html

Source: `03-ECO2023-Fall26-Exam1-SupplyDemand - Copy.doc` (document 3 of 4
covering Exam 1). Converted 2026-09-17.

## Mode

A legacy binary `.doc`, handled as mode (a). LibreOffice is installed here but
carries no Writer module (`libswlo.so` is absent), so it fails on every Word
file, `.doc` and `.docx` alike.

**This file needs two readers, and the first conversion used only one.**
`antiword` gives the body flow, and its PostScript output gives the formatting
that fixes heading levels (`scripts/doc_headings.py`): five centred
Helvetica-Bold 12 headings are `<h1>` and thirteen underlined Times-Bold ones
are `<h2>`. But **`antiword` silently drops every floating text box**, and in
this document that is where six exam tips, three worked examples and every
figure label live. `catdoc` reads them. The first version of this file was
missing all of it. The recovered content is:

- the chapter exam tip, and five more (the index card, the only factor that
  shifts both curves, the jet fuel example, The Pizza Question, and when one
  shift is bigger);
- **Example: The Demand for Pizza**, with a schedule — 23 million at $9, 20
  million at $11, 10 million at $13;
- **Example: The Demand for Pizza (Continued)**, the movement-along and
  income-shift discussion;
- **Example: The Market for Shoes**, three paragraphs;
- the From-the-Book box on relative price versus money price, whose opening
  sentence `catdoc` garbled and which was recovered from the raw stream.

## Most graphs are symbolic; the pizza pair is not

Outside the pizza example the document states no price or quantity, so those
graphs are symbolic: 110 × 110 axes, equilibrium at [50,50], P₁/Q₁ and P₂/Q₂
via `pl`/`ql`, and the D and S shapes the delivered
`ECO2013-263-SupplyAndDemand.html` uses. Those give p = 100 − q on demand and
p = q on supply, so a price of 70 has 30 demanded against 70 supplied and a
price of 30 is the mirror image — which is why the surplus and the shortage are
the same size. The equilibrium widget uses the source's own labels: P<sub>EQ</sub>,
P<sub>HI</sub>, P<sub>LO</sub>, Q<sub>S</sub> and Q<sub>D</sub>.

The pizza schedule is real data, so those two widgets are numeric.

## Graphs

Eleven inline figures and six floating ones became six widgets. `antiword`
reports inline pictures as `[pic]` and does not see floating drawings at all,
so the graphs were found in the prose (v6 step 1: "When the file has no images
at all, find the graphs in the prose instead").

| widget | replaces |
| --- | --- |
| The demand for pizza | the pizza schedule and its curve — numeric |
| Along the curve, and a shift of the curve | the movement-along and low/high income figures — numeric |
| The demand curve | the demand curve, plus movement-along versus shift |
| The supply curve | the supply curve, plus movement-along versus shift |
| Equilibrium, surplus, and shortage | the surplus/shortage/equilibrium comparison, as three buttons |
| Working through a shift of one curve | **all six** worked examples, as six buttons |
| One curve shifts: the four possibilities | the four-panel review figure, as four buttons |
| Both curves shift at once | **both** two-factor examples, plus the case where one shift is known to be larger |
| The Pizza Question: Figures A to D | the four labelled figures in that exam-tip box |

The six worked examples are six cases of one lesson, so hard rule 8 makes them
one widget with a button per market; each keeps its own heading and its own
four-step prose. Three of the six draw the same leftward supply shift, and the
captions carry what differs.

The two-curve summary table stayed a `<table>` — a 2×2 grid of outcomes is a
table, not a graph.

## Engine change: v2.7

These are the repo's first use of `preset:"shift"`, and it put its SHORTAGE /
SURPLUS brace above the axis, where the label landed squarely on whichever
curve crossed that price. The hand-written symbolic template always sets
`below: true` for exactly that reason, and the preset overwrites any `braces`
the config supplies, so this could not be worked around from the config.
Engine v2.7 makes the preset match the template. `docs/engine-reference.md` is
updated and every example re-embedded.

Worth noting why this survived until now: `check_file.py` **skips preset
widgets**, because the engine computes their geometry, so its label test never
saw them. Only `render_widgets.py` and a person catch this class of defect.

## Decisions taken, for review

- **Dr. Rush is named once**, for his description of equilibrium as "a
  situation in which there is no automatic tendency for change". Kept verbatim;
  `check_file.py` raises its one WARN on it.
- **"From-the-Book Topic Not Covered in Class" is retitled** "From the Textbook:
  Topic Not Covered". Hard rule 4 forbids student-facing text that points at the
  class, and `check_file.py` fails the original wording.
- **The two-curve table's arrows were reconstructed.** The source draws them in
  a symbol font that `antiword` renders as `(` and `?` indiscriminately, so the
  same glyph stands for both up and down. The four prose bullets immediately
  above the table state all four outcomes unambiguously, so the table was
  rebuilt from them: Q↓/P? and Q?/P↓ on the demand-left row, Q?/P↑ and Q↑/P? on
  the demand-right row. **Check this against the printed table.**
- **The class date of Wednesday, 9/2/26 falls in the middle of the supply
  factors list**, between "Prices of Substitutes and Complements in Production"
  and "Technology". The list is split at that point and resumed with
  `<ol start="3">`, so the date sits exactly where the source has it and the
  numbering still runs 1–6.
- The disequilibrium price line in the equilibrium widget is labelled P₂. The
  source labels it nothing, and P₂ is free in those three scenarios because
  none of them reaches a new equilibrium.
- Captions on the preset widgets are written, not generated. The preset's own
  captions end "Price up, quantity up", which hard rule 7 forbids.

## Checks

`check_file.py` → **0 FAIL, 1 WARN** (the Dr. Rush flag).
`render_widgets.py` → 53 screenshots, no engine errors, reviewed at every step.
