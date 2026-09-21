ECO2023-263-AllocativeEfficiency.html

Chapter 5, from the supplied HTML. Eleven figures became nine widgets; the
prose, the head and the box structure are exactly as delivered.

## The engine had to grow first

The chapter is surplus and deadweight loss, which are *areas*, and
`docs/engine-reference.md` listed "area fills of any kind" among the things the
engine does not do. So this is an engine feature rather than hand-drawn SVG in a
notes file (rule 2): **v2.11 adds `areas`**, a shaded polygon named by its
corners, drawn after the axes and before the curves so a fill never hides a
line, a point or a label. `teal` for consumer surplus, `orange` for producer
surplus, `red` for a loss, all at 18% so the graph reads through the wash.

A polygon is enough here because demand and supply are straight lines in this
chapter. A region bounded by a `curved` pair still cannot be filled, and that
stays on the "does not do" list.

The engine is re-embedded in all six other example files, which are byte-identical
to `engine/` and unchanged in status.

## The eleven figures

| Source figure | Widget |
|---|---|
| 01 marginal benefit curve | 1 — $15 for the 4 millionth pizza, $12 for the 12 millionth |
| 02 marginal cost curve | 2 — $8 for the 2 millionth, $14 for the 6 millionth |
| 03 efficient quantity | 3 — symbolic; Q\* is both the efficient and the equilibrium quantity |
| 04 $8 surplus + 05 total surplus triangle | 4 — one four-step walkthrough |
| 06 consumer and producer surplus | 5 — CS then PS then both |
| 07 three elasticity panels | 6 — three scenario buttons |
| 08 Piesanos calculation | 7 — $21, $11, $1, 8 million; CS and PS each $40M |
| 09 three deadweight cases | 8 — three scenario buttons |
| 10 underproduction + 11 overproduction | 9 — two scenario buttons |

Decisions worth knowing about, none of which needed asking:

* **Merged figures sit at the *later* of their two slots**, so every "the
  diagram below" in your prose still points at a diagram. The earlier slot keeps
  its `<!-- IMAGE POSITION -->` comment, as rule 6 requires — all eleven are
  preserved.
* **Two three-panel figures became scenario buttons**, since the engine draws
  two panels at most (rule 8, the same restructuring the PPF chapter needed).
* **Figure 07 is drawn as three cases: demand less elastic, similar, demand more
  elastic.** The source figure states no numbers and its alt text says only
  "different elasticity conditions", so the three readings are mine. They follow
  the prose either side of it — the less elastic side of the market keeps the
  larger surplus.
* **Numbers are only where the prose states them.** Figures 3, 5, 6 and 8 carry
  none, so they are drawn symbolically with P\* and Q\*. Figure 9 has stated
  quantities (15, 10 and 20 million) but no prices, so its Q axis is numeric and
  its P axis symbolic. The crossing point in widget 4 carries no stated price or
  quantity and is labelled P\* and Q\* even though the $12 and $4 beside it are real.

## Four FAILs, all in text that arrived written

`check_file.py` reports 4 FAIL, 2 WARN. Every one is in the delivered file, and
"leave everything else the same" means none of them is mine to change:

* `<title>` is "ECO2023 Spring26 Exam1 - Allocative Efficiency"; rule 6 wants the
  chapter name alone. Note it also says **Spring26** while the date line says
  Monday, 9/14/26 — worth a look either way.
* The head loads `studyguide/sn25-v2.js`, not `content/sn25-v6.js`. If your
  current pipeline has moved on from v6, CLAUDE.md rule 6 is what is out of date,
  not the file — say so and I will update the rule and the checker.
* A box headed **"From-the-Book Topics NOT Covered in Class"** trips rule 4's ban
  on naming the source in student-facing text. Rewording someone else's heading
  is your call.
* **Dr. Rush is named** ("Dr. Rush emphasized that marginal analysis is very
  important…"), which is the standing WARN that always comes to you.

The remaining WARN is the missing table of contents; `scripts/add_toc.py` writes
one on request.

## What was verified

* 9 of 9 configs parse and validate; 112 labels tested against every curve,
  arrow, tick, guide and point — no collisions.
* 28 renders across every widget, scenario and step, with no engine errors and
  no arrow lying over a guide.
* Phone: 9/9 widgets fit with usable controls at both 390×844 and 320×568, with
  all 8 scenarios and 14 steps driven.
* `check_file.py` learned about area labels while this was built, and
  immediately caught three collisions that had passed inspection by eye —
  including a "CS" label sitting on the demand curve. `scripts/test_check_file.py`
  is 0 failing.
