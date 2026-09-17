ECO2023-263-SupplyAndDemand.html

Source: `03-ECO2023-Fall26-Exam1-SupplyDemand - Copy.doc` (document 3 of 4
covering Exam 1). Converted 2026-09-17.

## Mode

A legacy binary `.doc`, handled as mode (a). LibreOffice is installed here but
carries no Writer module (`libswlo.so` is absent), so it fails on every Word
file, `.doc` and `.docx` alike; `antiword` reads this one. Its DocBook output
gives bold and italic spans but no heading levels, so heading levels were read
from the **alignment** in the fixed-width text dump: the five centred headings
are `<h1>` and every left-aligned one is `<h2>`. That puts "Shifts Due to a
Change in Two Factors" at `<h2>`, under "Illustrating Shifts of the Demand and
Supply Curves", which is where it belongs.

The body is a transcription. Two things could not be read from the binary and
were reconstructed from the prose instead, both recorded below.

## Every graph is symbolic

**The document states no price or quantity anywhere.** Hard rule 3 therefore
makes every graph symbolic: 110 × 110 axes, equilibrium at [50,50], P₁/Q₁ and
P₂/Q₂ via `pl`/`ql`, and the D and S shapes the delivered
`ECO2013-263-SupplyAndDemand.html` uses. Those give p = 100 − q on demand and
p = q on supply, so a price of 70 has 30 demanded against 70 supplied and a
price of 30 is the mirror image — which is why the surplus and the shortage are
the same size.

## Graphs

Eleven inline figures and six floating ones became six widgets. `antiword`
reports inline pictures as `[pic]` and does not see floating drawings at all,
so the graphs were found in the prose (v6 step 1: "When the file has no images
at all, find the graphs in the prose instead").

| widget | replaces |
| --- | --- |
| The demand curve | the demand curve, plus movement-along versus shift |
| The supply curve | the supply curve, plus movement-along versus shift |
| Equilibrium, surplus, and shortage | the surplus/shortage/equilibrium comparison, as three buttons |
| Working through a shift of one curve | **all six** worked examples, as six buttons |
| One curve shifts: the four possibilities | the four-panel review figure, as four buttons |
| Both curves shift at once | **both** two-factor examples, each as a two-panel comparison |

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
