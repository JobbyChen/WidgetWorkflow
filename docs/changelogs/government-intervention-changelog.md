ECO2013-263-GovernmentIntervention.html

# Government Intervention — conversion record

Source: `2529b9c3-ECO2013-263-Exam1-Module2-Part1-Full.html` (21 images).
Instruction: replace only the images that need to be widgets, change nothing
else but the TOC.

## Images

| # | Figure | Outcome |
|---|---|---|
| 01 | City at night (rent control) | **kept as `<img>`** — a photograph |
| 02 | Textbook price ceiling | widget 1, 3 steps |
| 03 | Competitive vs binding ceiling | widget 2, 2 scenarios |
| 04 | Apartment market equilibrium | widget 3 |
| 05 | Equilibrium surplus areas | widget 4, with calcs |
| 06 | $300 ceiling shortage | widget 5 |
| 07 | Producer surplus under the ceiling | widget 6, with calc |
| 08 | Consumer surplus broken up | widget 7, two areas + calcs |
| 09 | Deadweight loss | widget 8, with calc |
| 10 | Hurricane generators | widget 9, 4 steps |
| 11 | Competitive vs binding floor | widget 10, 2 scenarios |
| 12 | Burrito market equilibrium | widget 11 |
| 13 | Burrito surplus areas | widget 12, with calcs |
| 14 | Surplus with a $7 floor | widget 13, with calcs |
| 15 | Deadweight loss from the floor | widget 14, with calc |
| 16 | Wage protest | **kept as `<img>`** — a photograph |
| 17 | Minimum wage in the labour market | widget 15 |
| 18 | Before/after the minimum wage | widget 16, 2 scenarios, with calcs |
| 19 | Competitive / floor / ceiling | widget 17, 3 scenarios |
| 20 | Beer and cigarettes | **kept as `<img>`** — a photograph |
| 21 | Before/after a $3 tax | widget 18, 2 scenarios, with calcs |

All 21 `<!-- IMAGE POSITION -->` comments are where they were.

## Numbers

Every curve is fixed by two values the chapter states, never drawn to taste:

* **Apartments** — the CS and PS formulas state the intercepts, so
  D = 900 − ⅚Q and S = 100 + Q/2, giving the equilibrium $400/600, the $300
  ceiling's 400 and 720, and $566.67 on demand at 400, all as printed.
* **Burritos** — D = 12 − 0.04Q, S = 3 + 0.02Q; equilibrium $6/150, the $7
  floor's 125 and 200, and $5.50 on supply at 125.
* **Labour** — demand W = 30 − 0.05L, supply W = 0.05L; $15 at 300 hours,
  $20 giving 200 and 400, and $10 on supply at 200.
* **Sushi** — D = 20 − Q/6, S = 5 + Q/3, S + tax = 8 + Q/3; $15 at 30, then
  $16 and $13 at 24.
* **Textbooks**, **figure 3** and **figure 11** are each fixed by their own
  labelled equilibrium and the two quantities their control price produces.
* **Figure 19** states no numbers, so it is drawn symbolically (P*, P_Floor,
  P_Ceiling on the house 110×110 grid) — rule 3.

## Decisions to review

* **Figure 8 is not a market diagram** — it is a trapezoid pulled apart into a
  triangle and a rectangle with arrows. Rather than hand-draw it (rule 2), the
  widget shows the same trapezoid on the apartment graph as two shaded pieces
  with the three sums under it. The teaching content is the same; the picture
  is not.
* **Axis titles on the labour figures** are `Wage` and `Hours`. The source
  writes "Wage $/hour" and "Labor (Hours)"; the engine never wraps an axis
  title and neither fits.
* **Curve names** are `D` and `S` throughout except the labour market, which
  keeps the source's `Labor Demand` / `Labor Supply` because the roles of firm
  and individual are reversed there, and figure 19, which keeps `Supply` and
  `Demand` as drawn.
* **500 is not written on figure 2's quantity axis.** It cannot sit beside
  562.5 on a 296px axis at any scale that keeps the rest of the panel intact,
  so that point keeps the guide to the price axis only. The lede and the
  caption both give it.
* **Two deadweight wedges carry no label**: figure 11's, where every side is
  taken by a curve, a guide or the brace, and figure 3's producer surplus
  sliver is labelled beside the shape rather than inside it. The captions name
  both. The source does the same with its own slivers.
* **Figure 2's shortage label wraps onto two lines**, as the source's does.
  On one line it is wider than the gap between the curves it sits in; the
  braces themselves stay against the price line, as everywhere else.
* **Burrito and sushi axes are clipped** to the region the figures use. Drawn
  to the full intercepts, 24 and 30 rendered as a single "2430".

* **Figures 12 and 15 carry the whole picture.** 12 is the reference diagram
  for the burrito question set, so it marks $12/$7/$6/$3 and 125/150/200 with a
  dot at each, as the source does; 15 shades consumer and producer surplus
  behind its deadweight wedge. ($5.50 sits seven pixels from $6 on a 0–12 axis
  and cannot be written beside it, so 12 shows $6 and the two floor figures
  show $5.50.)

* **Every reading carries a dot**, the control price included, matching the
  artwork — 44 of them across the two chapters, applied by one rule at the foot
  of the config rather than point by point, so no figure can drift from the
  rest. Figure 10 also takes the source's `1k`/`1.2k`/`1.4k` quantities, and
  figures 11 and 18 gained the supply reading each formula uses ($650 at 75
  units, $10 at 200 hours).

* **Guides follow the source panel by panel.** Figure 12 draws a horizontal
  from each price across to its reading; figure 15's equilibrium carries only a
  vertical, because the source draws no horizontal there; and figure 18's
  "after" panel drops the $15 guide and tick altogether, since the "before"
  panel has already established the market wage — which is what frees the room
  for the deadweight label to sit inside its wedge.
* **$5.50 has no label in figure 12.** It is half a dollar from $6 on an axis
  that must reach $12, which is under seven pixels; its guide is drawn but
  unlabelled there. Figures 14 and 15 drop $6 instead, so the number is written
  wherever an answer depends on it.

## Not changed

* `<strong>` wraps whole question sentences in 18 places (Ian's markup).
* The head loads the font before the stylesheet.
* The house script swapped `content/sn25-v5.js` → `studyguide/sn25-v2.js`,
  the TOC fix sanctioned on 2026-09-21. Nothing else in the head or prose.

## Later (2026-09-24)

* **Figure 10 reveals its readings with its steps.** $800 and 1,400 were drawn
  in step 1, before the storm that produces them. Each reading now arrives with
  the step it belongs to. Fixing that exposed an engine bug: a price line
  suppressed a point's own price label even in steps where the line is not yet
  drawn, which silently dropped $600 from step 1 (engine v2.20).
* **The working now sits beside the plot** where the column is wide enough for
  it, and underneath where it is not (engine v2.21). Figures 16 and 18 were
  spending five or six lines of height on their formulas; on a desktop they now
  spend none. Nothing to configure, and nothing changes on a phone.

## Checks

0 FAIL. 13 WARN, all listed above, caption-redundancy notes, or Ian's own
markup. Every widget renders with no engine errors, and all 18 fit with working
controls at 390px and 320px.
