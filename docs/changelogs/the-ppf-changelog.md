ECO2023-263-ThePPF.html

Source: `03-ECO2023-Fall26-Exam1-PPF.docx` (document 2 of 4 covering Exam 1).
Converted 2026-09-17.

## Mode

Notes supplied as a Word document, handled as mode (a): the house-format HTML
was built first, then every graph converted. The body is a transcription, not a
rewrite — every paragraph, list item, bullet, exam tip and date is the source's,
in order, with the exceptions listed under "Decisions taken" below.

The figures are Word VML shape groups, not images, so axis orientation, every
label and every intercept was read from the shapes' own coordinates rather than
inferred. The three PNGs in the file are the exam-tip icon, a photograph of a
sushi roll and a book icon — decoration, not graphs, so none of them carries
into the output.

## The course code is ECO2023, not ECO2013

Document 1 was `1 - ECO2013 …` and taught by Dr. Knight; this one is
`03-ECO2023-…` and taught by Dr. Rush. The file name therefore starts ECO2023,
per v6 step 0 ("the course code is the first token of the file name"). If these
four documents really are one course, the file name needs changing before
publication — but nothing inside the document suggests they are: the chapter
numbering, the professor and the examples are all different from document 1.
The two files also cover overlapping material (both teach the PPF, opportunity
cost, bowed-out frontiers and shifts), which is consistent with two courses
rather than four chapters of one.

## Graphs

Seven figures became eight widgets.

| widget | replaces | numbers |
| --- | --- | --- |
| Attainable, efficient, and out of reach | steaks/hamburgers frontier with the three zone dots | none stated — conceptual |
| A student's frontier: grades and dates | GPA/dates frontier with the same three zones | 3.8 and 20 intercepts; 2.0 at 12 dates and 2.8 at 8 dates from the prose |
| The opportunity cost of a higher GPA | no figure — built from the prose that walks 12 dates/2.0 → 8 dates/2.8 | complete |
| Different people, different frontiers | **all three** student panels, merged into one widget with three buttons | none stated — conceptual |
| Economic growth shifts the frontier out | steaks/hamburgers 2026 → 2027 | none stated — conceptual |
| A student's frontier over four years | grades/dates freshman → senior | none stated — conceptual |
| Production-efficient is not the same as desirable | food/clothing frontier with Points A and B | none stated — conceptual |
| Gumballs, machines, and rising opportunity cost | the gumballs/machines frontier and its five-row table | complete: A (0,10) B (1,9) C (2,7) D (3,4) E (4,0) |

Every conceptual frontier is drawn as a quarter ellipse, because that is what
the source's arcs are (Word `v:rect` with an arc path override), and the
intercepts are the fraction of each drawn plot the arc covered. The three
student frontiers share one scale so the buttons are comparable, which is the
whole point of that figure.

The four exam-tip call-outs became `.exam-tip` blocks; their `<h4>` titles are
written, not from the source, since the source's boxes are titled only
"Exam Tip". The source's five tinted call-out boxes became `.example-box` (four
worked examples) and `.other-box` (the textbook-only topics), both of which the
house stylesheet defines; v6 step 0 does not mention either class, so this is a
format decision for review.

## Decisions taken, for review

- **Dr. Rush is named 8 times** and content is attributed to him: the "true
  cost" of an action, technology as a recipe, the gumballs-and-machines
  illustration, the "well-dressed corpses" line, and that he will never ask you
  to draw a PPF. Kept verbatim, per instruction. `check_file.py` raises its one
  WARN on this and does not fail the file. This is the judgement that costs the
  most if it goes the wrong way — decide it before publishing.
- **The source contradicts itself about the freshman → senior shift.** One
  passage says study skills improved more than socializing skills and that the
  gain was more pronounced for grades; a second passage, immediately after,
  says the opposite. The drawing settles it: dates (the vertical axis) grow
  from 52% to 88% of the plot while grades grow only from 57% to 69%, so
  socializing improved more. The widget and the surviving paragraph say that,
  and the contradicting sentence was dropped. **Check this** — if the intended
  lesson is the other way round, both the paragraph and the widget's second
  step need flipping.
- **"From-the-Book Topics Not Covered in Class"** is retitled "From the
  Textbook: Topics We Did Not Cover", and its lead-in reworded, because rule 4
  forbids student-facing text that points at the class. Its body says the
  concepts come from "Chapter 1 of the textbook" although this is Chapter 2;
  the reference to a chapter number was dropped rather than guessed at.
- Three other sentences were reworded for the same rule, with no change of
  content: "In class, Dr. Rush drew his first PPF…" → "Dr. Rush builds his
  first frontier…"; "Even attending this class has an opportunity cost—the
  stats class…" → "Even sitting in an economics course has an opportunity
  cost—the statistics course…"; "Dr. Rush said he will never ask you…" → "Dr.
  Rush will never ask you…".
- **The GPA example is two widgets, not one.** The zones (attainable,
  efficient, unattainable) and the movement along the frontier are two lessons
  on one drawing, several paragraphs apart, so each sits at its own paragraph.
  The steaks/hamburgers figure and the GPA figure teach the same three zones but
  stay separate widgets, because the source presents them as separate examples
  in separate sections.
- The prose mentions that the same example is worked with a 0-to-4.0 GPA and up
  to 24 one-hour dates. The widget uses the drawn version (3.8 and 20), which is
  what the figure and the surrounding paragraphs use.
- The zone dots on the two conceptual frontiers are labelled "Efficient",
  "Inefficient" and "Unattainable" rather than the source's two-line phrases
  ("Attainable & Efficient", "Attainable but Inefficient"): engine labels are
  single-line SVG text and the full phrases do not fit beside a dot. The full
  wording is in each step's caption instead.
- The gumballs table is "Machines / Gumballs", dropping the source's "Point"
  column, because `table.series` maps one quantity column to one curve id. The
  point letters A–E are on the graph instead, and hovering a row still
  highlights its dot.
- The `D → E` arrow in that widget stops just short of E. Its chord ends on the
  Q axis, so an arrow offset to the inside along the whole chord ran below the
  axis and through the 4 tick.
- **The table of contents is written into the file, by
  `scripts/add_toc.py`.** The house script would build it in the browser —
  `content/sn25-v5.js` and `studyguide/sn25-v2.js` are the same code and both
  insert a collapsed `<details class="toc-box">` of every `h1`/`h2`/`h3` before
  the first `<h1>` — but `content/sn25-v6.js`, which every converted file loads,
  returns **403** from S3, alone among the five house assets. So on a published
  page nothing runs and no contents appear. The script writes exactly what the
  house script would have produced: same element, same classes and inline
  styles, and ids from the same rule (which is why "Scarcity & Opportunity Cost"
  really becomes `scarcity--opportunity-cost`, with two hyphens). If that S3
  object is ever made public, the script will add a second one and this block
  should come out; `check_file.py` reports whether the links and the headings
  are still in step.
- The "Exam 1 Topics" list from the document's title block is dropped as cover
  matter, the same call made for document 1. It is a list of the seven exam
  chapters, not of this page, so it would read as a second contents block at
  the top. If it should appear, it needs a home that is not there.
- **The head order follows the current house files**: `sn25-v6.css` first, then
  the three font links on one line with `&amp;display=swap`. Note that the
  ECO2013 file delivered earlier, and prompt v6 step 0, both have the opposite
  order; document 1's output has been brought into line, and the delivered file
  is left alone and reported instead (it picks up one WARN).
- **A step exists only where the graph changes.** "Different people, different
  frontiers" therefore carries one caption per button instead of two steps, since
  nothing on the drawing moves within a scenario, and the food/clothing
  walkthrough reveals Point A on its second step and Point B on its third rather
  than drawing both from the start.
- The movement arrow on the GPA opportunity-cost widget sits on the **outside**
  of the frontier, up and to the right, not inside the attainable region.

## Numbers carried over or assumed

- Term code 263 from the only class date in the document, Wednesday 8/26/26.
- No number in any widget is invented. The interior and beyond-the-frontier
  dots on the conceptual graphs, and on the GPA graph, print no axis values
  (`showP`/`showQ` false) precisely because the source states none; their
  positions are illustrative and the captions say so in words.

## Checks

`python scripts/check_file.py examples/ECO2023-263-ThePPF.html` → **0 FAIL,
1 WARN** (the Dr. Rush flag above). The embedded engine is byte-identical to
`engine/`; 65 labels were tested against every curve, arrow and point with no
overlap; point values are emphasised consistently; all 8 IMAGE POSITION
comments are preserved.

`python scripts/render_widgets.py` → 25 screenshots (8 widgets × scenarios ×
steps), no engine errors, reviewed for collisions at every step.

## Engine

No engine change. This conversion runs on v2.6 as published.
