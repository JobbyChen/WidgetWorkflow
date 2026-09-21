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

## What the review round changed

Five defects, four of them mine, and the checker now catches every class of them.

* **A curve label struck through by its own curve.** `check_file.py` skipped a
  curve's label against its own curve, so "D = MB = MSB" shipped with a line
  through it and the file reporting PASS. The exemption is gone. Removing it
  flagged twelve labels here and **nothing in any other example**, which is the
  proof it was covering defects rather than preventing false alarms. Now a rule
  in CLAUDE.md.
* **Steps that only changed the caption.** `at` is a step index and index 0 is
  the opening state, so `at:2`/`at:3` against four captions left step 2 showing
  step 1's picture. Two widgets here and one in the shipped elasticity file.
  `check_file.py` gained a `steps` check that compares what is on screen at each
  step; it found all three and passes on every other file. Widget 3 is a single
  static diagram now, with a caption instead of steps.
* **Widget 3 abbreviated the source's equations** and had lost `P*` and
  `Qᴇꜰꜰ = Q*`. It reads `S = MC = MSC` and `D = MB = MSB` now, with both axis
  labels, matching the printed figure.
* **Widgets 1 and 2 had a full grid** on top of the guides each point already
  draws. The printed figures have only the guides, so the grid is off.

## The head was right and the checker was wrong

You confirmed both, and checking S3 settled it: `content/sn25-v6.js` returns
**403**, while `studyguide/sn25-v2.js` returns 200 — so the file's head is the
one that actually runs, and CLAUDE.md was out of date. Fixed in three places:

* `check_file.py` compares house-script versions **inside** a path rather than
  across two. Matching a bare `sn25-v[0-5]` had failed the current script twice,
  once for being absent and once for looking old.
* `studyguide/sn25-v2.js` **builds the table of contents in the browser** — the
  same `<details class="toc-box">` that `add_toc.py` writes — so that WARN was
  also wrong and is gone. Nothing needs writing into the file.
* CLAUDE.md rule 7 now records both paths and which one is live.

## One FAIL left, and one WARN, both in your text

* A box headed **"From-the-Book Topics NOT Covered in Class"** trips rule 4's ban
  on naming the source in student-facing text. Rewording your own heading is
  your call, so the file is untouched and the checker will keep saying so.
* **Dr. Rush is named**, which is the standing WARN that always comes to you.

`<title>` **was** changed, and it is the one piece of "everything else" I did
touch: it read "ECO2023 Spring26 Exam1 - Allocative Efficiency" when 263 is
Fall. It is now "Allocative Efficiency", which is rule 7's chapter-name-alone
and drops the wrong season with it. Say the word and I will put it back.

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
