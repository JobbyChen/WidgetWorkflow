ECO2013-263-SupplyAndDemand.html

Source: the 9/2 and 9/9 lecture transcripts (mode c, transcript-only — there
are no notes and no artwork for this chapter). Built in the Claude.ai project
and installed here verbatim, so this is its first changelog.

## Redo, 2026-10-05 — nine widgets, and the first example file at 0 FAIL

Ian asked for the chapter again. The prose, headings, date pills and tables are
untouched; what changed is the widgets, brought up to the conventions settled
since the file was delivered.

It now reports **0 FAIL and 0 WARN** — the first example file in the repo to
report nothing at all. `transcript_diff.py` against the two transcripts is
45/45 values and 38/38 names, the same as before the redo: no number in this
file changed, and none could, since every one of them is the transcripts'.

### Captions

Five were over rule 9's 200-character cap, from before the cap existed; being
asked to redo the chapter is the asking that rule wants. Each was saying the
same thing twice rather than saying too much — "Whenever there is a shortage,
the price is expected to rise toward the equilibrium price" is one clause
written as two — so each lost the repetition and kept the arithmetic.

Widget 3's caption was the only one failing the overlap test instead: the
paragraph above it already gives both readings and the $2 intercept, so the
caption restated the paragraph in full. It now gives what the drawing adds and
the prose does not — the line's slope, 150 more cups for each extra dollar.

### What the drawings had wrong

- **Widget 6 put every scenario's numbers on the axes at once.** Five
  quantities and three prices were ticks, so a reader on the equilibrium button
  saw the two disequilibrium prices and the four quantities belonging to the
  other two. Every one of them is read by a point or by a price line that
  arrives at the step it belongs to, so the axes carry no ticks of their own
  now and each button shows only its own numbers.
- **Widgets 7 and 8 printed P₁ and P₂ about a pixel apart**, because the new
  equilibrium sat ten units from the old one on a 110-unit scale. Those
  coordinates are the engine's symbolic convention rather than anything the
  transcripts state, so the equilibrium moves further — which also reads more
  like the example in the prose, where the price moves by half. The quantity
  read at the old price and the brace spanning the gap moved with it, and both
  new equilibria come from `curve_shapes.cross` rather than being typed.
- **Widget 5's new equilibrium was typed as a coordinate.** Both panels draw
  splines, and the kerosene dot sat about two units to the right of where its
  two curves actually meet. The crossing of the *drawn* curves is now computed
  — the engine's own Catmull-Rom, sampled in data units — and inserted into
  both curves' sample lists, so the dot is a point of each rather than near
  both. The assertion that it is still the only place they meet runs in the
  builder.
- **Widget 9's S₁ and S₂ labels were crowded** where the supply shift is the
  small one and both curves run into the same corner. S₂'s label drops 4px in
  *both* panels: the panels sit side by side and differ only in which curve
  shifts by more, so a label that moved between them would read as a
  difference.
- **Widget 3's supply curve stopped on its second reading**, which parked the
  curve's name on that dot and left the right third of the panel empty. It runs
  to the frame now. Both readings are still exactly on it, and the prose
  already reads the line beyond its data in the other direction ("if the curve
  is a straight line through these two points, that intercept is $2").
- **Widget 6's two converging arrows grazed a dashed guide**, which
  `docs/open-issues.md` has carried since before v2.26 because fixing it meant
  moving arrows in shipped work. Searched against the rendered geometry rather
  than guessed: of 75 placements tried, raising both a fifth of a dollar
  further inside the box the guides fence off is the only one that clears. It
  clears by 3.2px against a 3px threshold, up from 0.1px — the panel is
  genuinely crowded, with three elbows, two curves and two arrows between them,
  and that is established from the measurement rather than from a glance.

### Checked and left alone

The shortage and surplus braces sit under the Q axis, where the drawing
conventions would put a shortage brace *inside* the plot and a surplus brace
above its price line. Both alternatives were measured: inside the plot the
shortage label runs into three sets of guides, above the line the surplus label
sits on S₁, and in widget 8 it sits on both D and S₂. Under the axis is the
only clean position in all three, which is the same trade the trade chapter's
imports brace makes. Measured, not guessed, so the next session need not
re-open it.

### Two tools were quietly reading less than they looked

- **`transcript_diff.py` was skipping four of the nine widgets.** Its own regex
  required a newline on both sides of a widget's JSON, and four blocks in this
  file are written on one line — so they were passed over in silence while the
  file still reported "nothing in this file is unsupported" having looked at
  five widgets. It uses `check_file`'s block finder now.
- **And it treated "no ticks" as "symbolic".** That stopped being true when the
  convention became that a numeric figure with steps usually has no `xticks` at
  all: moving widget 6's numbers onto its points filed the whole widget as
  symbolic and stopped checking any of them. A widget that writes dollars,
  carries a schedule, or ticks an axis is showing the source's values; what
  makes a graph symbolic is `pl`/`ql`. The fix also recovers three widgets of
  the 9/11 prototype that were mis-filed the same way.
- **`place_curve_labels.py` could not act on a crowding finding.** Its list of
  the phrasings `check_file` uses was missing " is crowded against", so the
  subject of such a finding was never trimmed out of the message and the label
  being scored was blamed for its neighbour's collision at every offset,
  including the ones that would have cleared it. The one finding the placer
  exists to fix was the one it could not fix. Adding the phrase changes no
  existing placement in any example file.

### Checks

`check_file.py` 0 FAIL, 0 WARN. `render_widgets.py` 39 screenshots, no engine
errors, no arrow within reach of a curve or a guide, every one looked at.
`mobile_check.py` 0 problems at 390px; at 320px only the chapter's own prose
table, which overflows by 63px on the house stylesheet's cell padding and did
so before this redo. `transcript_diff.py` 45/45 and 38/38. The three test
suites 0 failing.
