ECO2023-263-Elasticity.html

Source: `04-ECO2023-Fall26-Exam1-Elasticity.docx` (document 4 of 4 covering
Exam 1). Converted 2026-09-17.

## Mode

Mode (a) from a `.docx`, read by parsing `word/document.xml` directly. Figures
are Word VML shape groups; the thirteen `media/` files are twelve MathType
equations as WMF plus one PNG, which is the exam-tip icon. Heading levels come
from the source's own run formatting, the same rule document 2 uses: bold alone
is `<h1>`, bold and underlined at size 23 is `<h2>`.

## Equations

Every formula is set in MathJax rather than kept as an image, so it scales and
is selectable. Each was recovered from the MathType WMF's embedded strings and
cross-checked against the prose, which states all of them in words.

**Nothing is condensed.** Each worked answer opens with the definition and then
substitutes, the midpoint formula is written in both halves the source gives it
in — the ratio of percentage changes, then the same thing in Q₂, Q₁ and the
midpoints — and the interval example is three displayed steps rather than three
expressions on one line.

The point-elasticity formula is the one the strings do not settle. It is
written as E_D = |(ΔQ_D/ΔP) × (P/Q_D)| because the document's own worked
numbers require it: on the straight line through ($9, 1), ($5, 5) and ($1, 9),
that formula gives exactly the 9, 1 and 1/9 the source prints. **Confirm it
against the printed equation.**

## Graphs

Seven figures became six widgets.

| widget | replaces | numbers |
| --- | --- | --- |
| The same shift, two different demand curves | the strong/weak responsiveness pair | none stated — symbolic |
| Why slope will not do as a measure | the dollars-versus-cents pair | $21 and $19, 2,100¢ and 1,900¢, at 8 and 12 |
| The spectrum of elasticities | **all five** spectrum panels, as five buttons | none stated — symbolic |
| The midpoint formula between two points | the A/B figure | A (8, $21), B (12, $19) |
| Elasticity falls as you move down a straight line | the three-point figure | $9, $5, $1 at 1, 5, 9 |
| The total revenue test | the demand-and-revenue pair | none stated — symbolic |

The responsiveness pair uses a supply shift of 36 and slopes of −0.5 and −3.
Every intersection is exact — flat demand meets the shifted supply at (26, 62)
and steep demand at (41, 77) — and the shift is that large because a smaller
one put P₁ and P₂ within a few pixels of each other.

## Decisions taken, for review

- **Dr. Rush is named once**, in the exam tip about the point-elasticity
  equation. Kept verbatim; `check_file.py` raises its one WARN on it.
- **The spectrum curves bow.** Only the two extremes are straight in the source:
  perfectly elastic is horizontal and perfectly inelastic vertical. The three
  between them are convex to the origin, and unit elastic is drawn as a true
  rectangular hyperbola (xy = 900), which is what unit elasticity means.
- **The demand panel of the total revenue pair carries all five labels** the
  source marks on it: E = ∞ at the vertical intercept, then E > 1, E = 1, E < 1,
  and E = 0 at the horizontal intercept.
- **Total revenue has no shaded rectangle.** The source shades the price-times-
  quantity rectangle under the demand curve; the engine has no area fill, so the
  widget marks the midpoint on demand and shows the revenue hump beside it
  instead. Logged as an engine request rather than hand-drawn.
- The revenue panel's vertical axis is titled TR and carries no tick values,
  because the source prints none and they would have had to be invented.
- **Three crowding WARNs remain**, all the same fact: $19 and $21 are two
  dollars apart on a scale that has to reach $21, so their tick labels sit about
  four pixels apart. The same holds for 1,900¢ and 2,100¢. Readable, and the
  alternative was squeezing the scale until the curve touched the frame.
- The exam-tip titles are written. The source's boxes are headed only "Exam
  Tip", and these follow the house convention of a short topic phrase:
  Midpoint Formula, Point Elasticity, Total Revenue Test.
- The in-text "Exam tip:" paragraph about remembering the total revenue test
  became an `.exam-tip` block, since it is one in substance.

## Checks

`check_file.py` → **0 FAIL, 4 WARN** (the three crowding lines and the Dr. Rush
flag). `render_widgets.py` → 21 screenshots, no engine errors, reviewed at every
step.

## Correction, 2026-09-21 — two formulas were rewritten rather than reiterated

Both were algebraically right and neither was what the source says.

* **Point elasticity.** Written as `E_D = |ΔQ_D/ΔP × P/Q_D|`. The source writes
  `E_D = |1/Slope × P/Q_D|`. The two are equal, which is exactly why the
  substitution reads as tidying rather than as a change — but the whole reason
  the source introduces that equation is that a straight line's slope is fixed
  while `P/Q_D` is not, and the rewrite hides the constant.
* **Cross-price elasticity.** Written with the subscript `E_{A,B}`. The source
  subscripts it `E_CROSS`, matching `E_INC` and `E_S` beside it.

The chapter's other ten equations were checked against the source and are
exact. Read by `scripts/doc_formulas.py`, whose `--check` now catches both of
these.
