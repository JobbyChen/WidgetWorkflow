# Decisions and history

## 2026-09-11 → 09-16 — the Claude.ai project

The project ran in a Claude.ai project ("ECO2013 widgets"). It produced the
engine (v2), a prototype rendering the Supply and Demand chapter's graphs as
widgets (`examples/ECO2013-Widgets-All.html`, dated 9/11/26), six versions of
the conversion prompt, and one real conversion — the Fall '26 Supply and Demand
chapter built from a lecture transcript alone
(`examples/ECO2013-263-SupplyAndDemand.html`).

On 2026-09-15 the review run screenshotted every widget, scenario and step in
headless Chromium and checked each for collisions. That run is why the
render-and-look step exists.

On 2026-09-16 everything was packaged as `eco-widgets.zip` for Claude Code.

## 2026-09-16 — the repository was created empty, and rebuilt wrongly

The zip did not reach the repository: it was created with no commits at all. A
`CLAUDE.md` pointing at an engine, docs, scripts and examples that did not exist
is not usable, so those were **reconstructed from the prose description in
`CLAUDE.md`**.

The reconstruction was wrong in nearly every particular, and was thrown away the
same day when the real files arrived. It is recorded here only so the mistake is
not repeated:

- The reconstructed engine used a different schema throughout — `from`/`to`
  endpoints and a `bow` factor instead of `pts:[[q,p]]` and `curved`, objects for
  steps instead of strings, an array of scenarios instead of a keyed object,
  `guides` instead of automatic axis labels. Nothing written against it would
  have loaded in the real engine.
- It used a monochrome palette (black ink, one red) rather than the real
  navy/paper/tinted-plot scheme, Helvetica rather than Red Hat Display, and a
  full-width bordered card rather than the 80%-width panel the notes use.
- It had no animation, no schedule-row hover linking, no `from` shift mechanic,
  no `thin`/`dim` treatment of the original curve.
- The reconstructed `conversion-prompt-v5.md` was assembled from `CLAUDE.md`'s
  summary bullets. The real prompt is **v6**, is far more specific, and covers
  things the summary never mentioned: patch mode, figure mode, the
  `<!--SDG-ENGINE-->` placeholder, the `<b>`/`<strong>`/`<em>` rules, how
  TERMCODE is derived from the first class date, image sizing classes.

**The lesson worth keeping:** a specification written as a summary is not enough
to reproduce an implementation. When the artifact itself is missing, say so and
stop, rather than producing a plausible substitute — a wrong engine that runs is
harder to detect than an absent one.

## 2026-09-16 — the real files arrived

`sd-graph.js`, `sd-graph.css`, both example files and
`ECO-widget-prompt-v6-SYSTEM.md` were supplied directly. The reconstruction was
deleted and these were installed verbatim.

Verified on arrival, against the real files rather than against a description:

- The engine embedded in `ECO2013-263-SupplyAndDemand.html` is byte-identical to
  `engine/sd-graph.js` and `engine/sd-graph.css`, **header comment included**.
  So embedded copies keep the header. (`CLAUDE.md`'s handoff note had said the
  repo convention was to strip it; that is true only of the TOOL prompt variant's
  appendix, not of a published notes file.)
- Both of `embed_engine.py`'s paths reproduce that published file byte-for-byte:
  replacing a `<!--SDG-ENGINE-->` placeholder, and re-embedding over an engine
  that is already there.
- Figure mode is specified in prompt v6 but not implemented in engine v2. A
  config with no `axes` throws `Cannot read properties of undefined (reading
  'cents')`. Confirmed by running it.
- `CLAUDE.md`'s handoff note said the 263 file still linked `sd-graph.*` from S3
  instead of embedding. It does not — the delivered file has the engine embedded.
  That note was stale.

### Decisions taken while rebuilding the tooling around the real engine

1. **`embed_engine.py` implements the placeholder convention**, because that is
   what prompt v6 step 7 specifies: the model emits `<!--SDG-ENGINE-->` and never
   the engine source. Re-embedding over an already-embedded engine is kept as a
   second path, since hard rule 1 requires re-embedding every file after an
   engine change.
2. **`check_file.py` replicates the engine's geometry** so it can run step 8's
   x-position test for real: for every curve label, point label, axis label and
   brace label, it computes where each curve passes at that label's position and
   fails if the curve runs through the label's box. This is the check the prompt
   asks for and the one a person is worst at doing by eye.
3. **The surplus/shortage two-arrow check keys on `hlines`, not on the brace's
   label text.** An equilibrium-shift widget also carries a brace labelled
   Surplus or Shortage — the gap at the old price — but it is the pattern v6
   step 4 templates *without* `moves`. Keying on the label flagged two correct
   widgets in the 263 file. Prompt v6 is genuinely ambiguous here; see
   `docs/open-issues.md`.
4. **The example files are committed as delivered, not corrected.** The
   prototype's captions predate v6's caption rules and fail the checker; that is
   a true statement about the file, and silently rewriting Ian's shipped work to
   make a script go green would be worse than the red line.

## 2026-09-16 — engine v2.1, and the first corrections to the delivered file

Ian asked why one arrow in the iced coffee schedule-shift widget was heavier
than the others. It was not the same kind of arrow: the three thin ones (1.4px)
were the per-row schedule arrows, and the heavy one (2.4px) was the shift arrow
the engine draws from `from`, placed by `arrowP` at $4.50 — a price with no row
in the schedule, so it pointed from nothing to nothing.

Three treatments were rendered and compared before changing anything: matching
the weights (which kept the pointless fourth arrow and made it look like a
mistake), dropping the row arrows in favour of the one shift arrow (which loses
the link between each table row and its point), and dropping the shift arrow.

5. **A schedule-shift widget draws row arrows only.** Engine v2.1 adds
   `shiftArrow: false`, which suppresses the arrow while keeping the slide
   animation and the dimming of the original curve — `from` previously bundled
   all three together, so a config-only fix would have cost the animation. Every
   arrow is now one weight, 2.4px, so two arrows in a graph never read as two
   different kinds of thing. Prompt v6 step 5 changed with it, otherwise the
   next conversion would put the fourth arrow straight back.
6. **`<strong>` keeps the term and nothing else.** The four flagged tags were
   real vocabulary terms — v6 names "inferior goods" as a `<strong>` example —
   so converting them to `<b>` as the checker first advised would have been
   wrong. The fault was the `(+).` sitting inside the tag. Checking what the
   rule actually said, rather than what the checker's message said, changed the
   fix.
7. **The class references were three, not one.** The checker matched `the class`
   on a word boundary and so missed `classroom` twice, including in a heading.
   Word lists that look complete are worth testing against the file rather than
   trusting.

## 2026-09-17 — PPF probed, and the label test finally covers rule 5

Asked whether a production possibilities frontier was in scope before the source
docs existed, the answer came from building three PPF widgets against the real
engine rather than reasoning about it. Most of PPF turned out to work unchanged,
including every kind of shift; the probe is throwaway and stayed out of the repo.

8. **The label test now covers arrows, points, axis ticks and the values a point
   prints for itself.** It had only ever tested labels against curves and other
   labels, while rule 5 says "a curve, a point, an arrow, or another label" — so
   an arrow lying across a point label passed, and so did a point's automatic
   "85" sitting a pixel from an "80" tick. Both were spotted by eye in the PPF
   probe, which is the failure the script existed to prevent. It also now warns
   when two labels are under about six pixels apart rather than only when they
   overlap, since a clump reads as one label.
9. **Boxes are only compared when they can share a step.** Adding tick boxes made
   this necessary: two points that never appear together were being reported as
   overlapping.
10. **Dashed guides are in the label test, as warnings only.** Rule 5 lists
    curves, points, arrows and labels, not guides — but a label pressed against
    the dashed line dropping from its own point reads as crowded, which is how a
    PPF point label was spotted by eye. Point guides, price lines and the
    verticals under an above-axis brace are now all tested. They warn rather
    than fail, because the rule does not name them. This was the third category
    the test was missing after arrows and ticks; the pattern is that every
    element the engine draws needs to be in it, not just the ones the rule
    enumerates.
11. **Axis titles take a word.** `P` and `Q` fit anywhere; "Butter" ran into the
    plot and "Guns" was clipped off the right edge. The x title is now anchored
    to the right edge and the y title sits in the headroom above the plot, which
    moves `P` and `Q` by a few pixels in existing widgets and is invisible in
    practice — checked against before-and-after renders of the shipped file.

## 2026-09-17 — the upright brace

12. **`vbraces` mirror the horizontal brace rather than inventing a new idea.**
    The first mock put the brace inside the plot at a quantity, where it fought
    the point labels for space — Ian's suggestion to put it outside the P axis,
    the way `below: true` puts a flat brace outside the Q axis, is better: the
    plot interior stays clear and each half of a trade-off is marked on the axis
    it belongs to. It costs 44px of plot width, and only on widgets that use it,
    exactly as `below` costs 18px of height.
13. **The label runs up the axis** because horizontal text needs about 85px and
    the margin is 54.
14. **`check_file.py` learned the widened margin in the same commit.** It
    replicates the engine's geometry, so a left brace it did not know about
    would have put every coordinate 44px out — and reported the results
    confidently. Teaching the checker is part of an engine change, not a
    follow-up to one.
15. **Brace outlines went into the collision test too**, closing the gap noted
    when guides were added: only brace *labels* had been tested, never the
    bracket. This immediately produced three classes of false positive, all
    adjacency that is correct by design — a brace's label beside its own
    bracket, the same value printed by two points at one price, and an x tick
    beside a y tick in the origin corner. They are exempted by name rather than
    by loosening the test.

16. **Bold axis values are a fallback, not a feature — and the "18 and 44
    instances" were not a bug.** Asked why one point value was bold and another
    plain, a scan found 18 point-values-coinciding-with-ticks in the 263 file and
    44 in the prototype, which looked like a widespread defect and was reported
    as one. It is not: in both files *every* tick is a value the prose uses, so
    every point value is a tick, nothing is bold, and the graphs are uniform. The
    mixed appearance was in a PPF probe that listed a generic 20/40/60/80/100
    scale the points did not land on, breaking prompt v6 step 5. No engine change
    was needed; `check_tick_emphasis` now warns when one graph mixes the two, so
    the same mistake cannot pass quietly. A count of instances is not evidence of
    a defect until you have checked what the convention is.

17. **Questions are allowed here, but not in prompt v6.** Ian relaxed the
    no-questions rule on 2026-09-17: in this repo, ask when a wrong guess would
    be costly — a number, which graphs to convert, which of two readings of a
    table — and decide-and-flag everything else. v6 keeps "You never reply with
    a question" because it runs in Cowork, where a question stalls a run with
    nobody watching. The two documents therefore disagree on purpose, which is
    recorded in CLAUDE.md so a future session does not tidy it away.

## 2026-09-17 — first PPF conversion, and what it cost the tooling

18. **Axis titles went into the label test.** A frontier's curve label, parked at
    the end of the curve in the bottom-right corner, landed on the Q axis title,
    and nothing noticed: the titles are drawn text that the test had never
    included. That is the fourth category found by eye rather than by the script
    — after arrows, ticks and guides — and it is now the last of the drawn text
    elements.
19. **`label: ""` draws nothing.** A lone PPF needs no curve name, but the id is
    still needed by `table.series`, and falling back to it parked "PPF" across
    the frontier. An explicit empty label is now distinct from an absent one.
20. **Two source phrases were narrowed again.** "the class" fired on *the class
    average* and "in class" on *you may be sitting in class* — ordinary English
    about being a student, not attributions. Both now need an attribution verb
    nearby, or an exclusion. This is the third time a word list has been too
    literal; the lesson holds that it must be tested against a real file, not
    reasoned about.

21. **Arrows are tested against curves and against each other; guides were tried
    and dropped.** Only the arrow's middle is tested against curves, because an
    arrow that points at something on a curve touches it at the tip by
    definition -- two movement arrows converging on an equilibrium always do,
    and testing the whole arrow flagged correct work in the chicken-thighs
    widget. Arrow-versus-guide was dropped outright: a surplus arrow must cross
    the guides between the price line and the equilibrium, so it fired ten times
    on files that are right. Both surviving checks were run against a fixture
    reproducing the two original defects, and both fire; all three example files
    stay clean.

22. **The checker has tests, and they were mutation-tested.** Every check in
    `check_file.py` was added after a defect got past it, and nothing verified
    they kept working — a rule narrowed once too often stops firing while every
    file still reports 0 FAIL, which is indistinguishable from success. The
    source-word list alone was narrowed three times in one day. The tests assert
    each check still reports its defect, that five ordinary sentences do not trip
    the source rules, and that no arrow or source finding appears on a real file.
    Then three checks were deliberately broken to confirm the tests fail; a test
    suite that has never failed is evidence of nothing.

23. **The first semester swap turned out to be a no-op, and that is now
    measurable.** Two ECO2013 transcripts arrived for a swap against
    `examples/ECO2013-263-SupplyAndDemand.html`. Every schedule matched to the
    dollar — the mocha rows 15/6, 12/13, 9/22, 6/38, 3/65; lemonade 150 at $3
    and 300 at $4; iced coffee 100/150/200 with a 50-unit shift; chicken 20, 30,
    40 lbs; chicken thighs clearing at $5 and 200, short 90 at $4 and long 270
    at $8 — as did every good, and the file's own date lines read 9/2/26 and
    9/9/26, which are the transcripts' dates. They are the transcripts the file
    was built from, not a new term's.

    Establishing that took a morning of reading and could have gone the other
    way: the cheap failure is to swap a title, find the numbers "close enough"
    and ship a stale schedule. So the reading became
    `scripts/transcript_diff.py`. It splits a widget's numbers into the ones a
    reader sees (ticks, schedule rows, the price a brace or guide sits at) and
    the ones that only place a curve, checks the first against the transcript
    text, and reports symbolic widgets as having no values at all — their
    110-scale coordinates are the engine's convention, and rule 3 says that is
    precisely what you draw when the source states no numbers. Before that split
    the file scored 96/158 and read like a file full of invented numbers; after
    it, 45/45 values and 38/38 names.

    Matching is loose — digits, spelled-out, thousands separators — which
    over-reports support on purpose, so an UNSUPPORTED line can be trusted and a
    stated one only means "not obviously changed". Both directions were
    controlled: the elasticity file, which these transcripts do not describe,
    comes back 9/17 and 20/30, and moving one mocha tick from $15 to $17 is
    caught (15/16, UNSUPPORTED: 17). `check_file.py` has always printed `SKIP
    numbers — whether each number is the source's number needs the source`;
    when the source is a transcript, this answers it.

24. **Formulas are transcribed by a script now, because by eye they lose their
    left-hand sides.** These chapters store every equation as a MathType OLE
    object: `word/document.xml` carries an `<w:object>` and a WMF picture, and
    no `<m:oMath>` at all, so pandoc, `antiword` and `catdoc` skip them without
    a word. The only way anyone had read one was to look at the rendering and
    retype it, and across 26 equations that cost three: `OC_X =` was dropped and
    only its fraction kept; point elasticity was rewritten from the source's
    `1/Slope × P/Q_D` to `ΔQ_D/ΔP × P/Q_D`; and cross-price elasticity was
    resubscripted `E_{A,B}` where the source says `E_CROSS`. The last two are
    the dangerous kind — algebraically right, and wrong about what the chapter
    is teaching, since the point of the slope form is that a straight line's
    slope is constant while `P/Q_D` is not.

    `scripts/doc_formulas.py` reads them instead. The WMF is a picture, but
    MathType draws the glyphs with real `TextOut` records, so the words survive
    inside it in drawing order — numerator before denominator, left-hand side
    where MathType emitted it. Readable, never pasteable: subscripts arrive as
    their own runs, so `E_D` reads as `E ⟨/⟩ D`.

    `--check` then compares each equation against the notes file. Three things
    had to be true before it caught anything. Adjacent runs are emitted with no
    space (`What You` + `Gain` → `whatyougain`), so runs are split where a
    lower-case letter meets an upper-case one. `PP` is `P` and `P`, not a word,
    so a token of one repeated letter is dropped. And the comparison is against
    the single best-matching formula paragraph, not the whole file: a
    file-wide bag of words cannot see a dropped `OC`, because `OC` appears a
    dozen times over in the worked examples. All three original defects were
    put back in temporary copies and all three fire; both real files come back
    with nothing missing. MathJax could not be rendered here to confirm
    visually — the CDN is blocked in this environment — so the new LaTeX was
    checked mechanically for balanced braces and known commands instead.

25. **Mobile is measured now, because it is the one thing review cannot see.**
    Ian reviews these on a desktop and students read them on a phone, so a
    layout defect is invisible exactly where it would be caught.
    `scripts/mobile_check.py` loads a file at phone size and drives it: every
    scenario clicked, every widget stepped to its last step and back.

    It reports four things. `page` is the page scrolling sideways. `fit` is a
    figure, table or SVG wider than its column. `tap` is a control under the
    44px minimum. `reach` is the one a screenshot hides — scenario buttons go
    full width on a phone, so several of them are a screenful on their own, and
    the student taps one and has to scroll to see what it did. Nothing is broken
    and nothing is off the edge; the cause and its effect are just never both
    visible.

    Two things had to be right before the interaction half meant anything. A
    button that is disabled (`Back` on step 1) or already pressed (the scenario
    currently showing) is doing its job when nothing happens, so neither is
    exercised; counting them reported ten defects against a file that had none.
    And when a figure does overflow it pushes the controls off the viewport, so
    the step button cannot be tapped at all — that is the finding, and the first
    version crashed on it instead of reporting it.

    All four checks were controlled: a copy with the stacking and fluid-figure
    rules disabled (21 problems, including the untappable controls), one with
    the controls shrunk below 44px, and one with the scenario buttons padded
    until the graph fell past the fold — which stays clean on a taller viewport,
    so `reach` is measuring the screen rather than flagging everything. All six
    example files pass at 390×844 and at 320×568: 58 widgets, no sideways
    scroll, no overflow, no control under 44px, and 60 scenarios and 107 steps
    driven without an engine error. The tightest widget spans 515px of a 568px
    screen.

    One correction to a first impression: the five-button elasticity spectrum
    looked from its screenshot like it pushed its graph off the screen. Measured,
    it spans 487px of 844. The screenshot is the whole widget at 2x device
    scale, which reads as much taller than it is — the reason to measure rather
    than judge a layout by eye.

## 2026-09-29 — externalities, and a scale problem left alone

Chapters 16 and 17 went to seven widgets over one market drawn five times and
another drawn twice. Four rounds of review came down to one question, asked
four different ways: where does the label naming a gap go, when the curve
bounding that gap runs through the only space it fits? Two answers were tried
and are wrong. Shortening marginal social cost to the segment the source draws
freed the space and left the curve starting from nowhere on every step before
its end is marked. Nudging the label clear of its brace cleared the collision
and stopped the label reading as that brace's name — Ian sent it back twice.
The answer is `dimAt` (engine v2.31): the label stays on its brace and the
curve fades to a quarter opacity for the steps that need the room.
`check_file.py` skips a label against a curve that is fading while the label
is on screen, and only for the steps the config declares.

### The two-panel widget renders at half scale, and that is being left alone

Ian's last question on the chapter was why `Q_EQ = Q_EFF` looked blurry at
100% on a half-width window when it is fine zoomed in. Measured in Chromium,
the cause is not the font and not the subscript ratio:

| | one-panel figure | the two-panel one |
| --- | --- | --- |
| 900px viewport | 1.51× — subscript 11.4px | 0.83× — subscript 6.3px |

Everything inside a plot is SVG in a 372-unit viewBox, so a panel given half
the width is drawn at half the scale, and the smallest text on it goes first.
The subscripts are the size they are everywhere else; the panel is at 55% the
scale of every other figure in the file.

A fix was built and reverted (engine v2.32, commit `feccb5d`, reverted in
`1d089e3`). It was three layout rules: the widget takes the full column
instead of the 80% a single figure uses, each panel is capped at `--fig` so a
wide screen does not draw these graphs larger than the ones around them, and
below a 970px body the pair stacks. It worked — within 11% of the one-panel
scale at every width from 320 to 2200px, against 55% — and **Ian rejected it:
stacked, the widget is far too tall.** Two panels at 562px each plus their
headings run about 2,000px on a 900px-wide window, and you cannot see the
comparison the figure exists to make.

So the trade stands as it is: side by side and small beats legible and
unreadable-as-a-pair. Do not re-propose stacking. If the subscripts come up
again, the untried option is the cheap one — the subscript is `.72em` at
weight 600 hanging off a 700–800 weight parent, so it is both smaller *and*
thinner than the letter it belongs to, and matching the parent's weight costs
no space at all.

### Also from this chapter

* **The subsidy was shifting supply by the other market's gap.** The builder
  computed the mismatch and printed it, for three rounds, while the figure
  shipped with its new equilibrium dot off the subsidised curve. Printed
  self-checks are assertions now.
* **A figure that is not becoming a widget stays the image it is** — restated
  here because the goods-classification table is the second one in two
  chapters that was rewritten as HTML before being put back.

## 2026-09-30 — the trade chapter, and where a figure outranks the prose

Chapter 7 of the ECO2023 exam-1 material converted to eight widgets. Three of
them are one panel where the source draws two, because each of those figures
is one market before and after a change and the change is better seen as a
step than as a second picture. Two stayed two panels, because there they are
two different markets.

**The quota market is drawn three times in that chapter on three different
sets of numbers**, and figure 08 agrees with neither the prose nor the two
figures before it. Rule 3's authority order says the prose wins, so widget 8
was first built on the prose's numbers — and Ian overruled it: *"it should be
50 to 100 million on the x axis."* Each widget follows its own figure. The
rule has a boundary now: the prose settles a figure that contradicts *itself*
(the apartment figure's impossible intercept), not a figure that is simply a
different example. A reader is comparing one figure against the widget beside
it, not the chapter against itself, and the disagreement belongs in the
changelog rather than in the drawing.

Widget 8 therefore sits in its own market, with its own curves and its own
ticks, and is the one figure in the file that does not continue the ethanol
one.

### Three drawing corrections, all of them about where a name landed

* **The tariff band had nowhere to put "Imports".** It is fifteen units deep
  and holds the revenue rectangle and both deadweight triangles.
  `below: "axis"` was the documented answer and is only half of one: it sets
  the bracket down by the Q axis but leaves the label reaching back up into
  the band, which is where the triangles' names are. `below: true` puts the
  whole thing under the axis, the way the quota figure next to it already
  draws its own, and the marked quantities supply the drop guides the brace
  gives up.
* **Widget 8's axis was drawn out to demand's own intercept.** A quarter of
  the panel was empty while five names fought over the middle band; clipped
  to the region the figure uses, every unit is 23% wider and the crowding is
  gone. Demand then leaves through the side rather than the axis, so the
  world price is named below its line and short of the frame — at the line's
  right end, demand runs straight through it.
* **The ethanol ticks read "3040".** The quota moves domestic output from 30
  to 40, and both figures carried all four readings. A tick cannot step, so
  each figure takes only the two its own guides land on — which is the
  step-scoped rule from the ceiling chapter seen across figures instead of
  across steps.

### On capturing what the placers do

`place_labels.py` and `place_curve_labels.py` write into the built HTML, not
into the config, so a rebuild drops them. Chapter 7's builder reads a
`placed.json` captured from the built file, which makes the build
reproducible — and the capture then overwrote a placement that had been
pinned by hand, putting widget 6's consumer-surplus label back on the supply
curve. Pins are applied after the captured placements now and live in the
builder, where the placer cannot reach them.

## 2026-09-30 — the width model, measured per character at last

Chapter 7's `S + Quota` rendered as `S + Quo`, with `check_file` reporting the
label as inside the panel. The engine's right margin and the checker's overlap
test share one measure of how wide a string is, and that measure had now been
wrong three times:

* a flat .58 em a character (fixed at v2.27/v2.28),
* .58 for weight 700 and .70 for weight 800, right about curve labels only
  because they happen to be uppercase (fixed at v2.44),
* an average per *case* — upper .690, lower .539, digits .558 — which fixed
  `P_{WORLD}` and was 20% narrow for `S + Quota`.

The third failed for the reason the first two did: an average over a class
under-states the members of it that are wide. A capital runs from .372 (`I`)
to 1.102 (`W`); `+` is .837 and a space .348, against the .25 the model
allowed. So the margin computed 58.9px for a label that draws at 73.5px and
concluded it had 1.8px to spare.

**A class average is not a measurement.** `scripts/em_widths.py` holds a
table measured per character in Chromium — ten copies of each between two H's
so the side bearings cancel — and prints the engine's copy with `--js`;
`test_check_file.py` fails if the two ever differ. Weights 700 and 800 at 12,
13 and 14px agree to 0.0002 em, so one table covers every label the engine
draws, and a plain 10.5px tick is about 11% narrower than the table says,
which over-states rather than clips.

Re-measuring every shipped file with it turned up no new overlaps: the three
in the government-intervention file that v2.44 exposed are still the three.

### And a widget that had never worked

`mobile_check` on that same file reported `main is not defined`. `finish()`
appends the `calcs` block to a `main` that is a local of `build()`, so every
widget carrying `calcs` threw on load — and the throw took the step controls
built after it down as well. One widget in shipped work, dead since the
`calcs` layout went in, while `check_file` and `render_widgets` both passed
it: neither of them presses a button. It holds its row on the widget now
(v2.45).

That is the lesson worth keeping. A static check reads the file and a
screenshot catches what draws; only `mobile_check` drives the controls, so it
is the only one that can find a widget that renders and does not work.

## 2026-09-30 — the label goes on top

Four rounds went into where the deadweight-loss names sit in the trade
chapter: centred and struck through by their own wedge's hypotenuse, shifted
clear and then reading as a caption for whatever they had landed beside, then
outside on hairlines, then the wedges widened to hold them. Ian ended it:
*"if it's easier just make it like the source where the red line stops or is
under all the rest — like have the CS, DWL and the grey box be on top."*

Which is right, and it is what the printed figure does. The source fills each
deadweight wedge solid black and sets DWL in white inside it: the edges are
invisible under the name because the name is painted last. The engine drew an
area's fill *and* its label before the curves, so a curve ran over the label.

From v2.46 the fill stays where it was and the name is held back until after
the curves and the price lines. Points and braces still come after it, so a
marked reading is never covered.

**`check_file` had assumed this all along.** Its `masks()` exempts a boxed
label from the curve test, on the grounds that the box covers what passes
under it — which was simply not true of the engine, so the exemption was
hiding real strike-throughs rather than describing the drawing. The two agree
now.

Two things followed from it:

* The chapter's quota figure draws S + Quota from the quota equilibrium
  upward, as the source does, instead of from the world price. Below that
  price the quota does not bind and the line has nothing to say, and drawn
  down through the importers' rectangle it crossed the one label that has to
  sit in the middle of it.
* The tariff figure's world price moved from 25 to 15 and its tariff price
  from 40 to 38. A deadweight wedge on curves of slope 1 is exactly as wide
  as the tariff is tall, so at 25 and 40 both wedges were narrower than the
  word "DWL". The prices are symbolic — the chapter states none — so their
  size is a drawing choice, and the builder now asserts three things about
  it: the wedge is wider than its own name, the tariff has not closed the
  import gap, and the tariff price is far enough below the domestic one to
  tell them apart.

And the box itself was measured at 5.3px a character, an average from before
the per-character table: "Importers" hung out of both sides of its own box,
and the box was a line short of its descenders. Same table as everything
else now.

### The box came off (same day)

Boxing the name was the wrong half of v2.46. Painting it last is what stops a
curve striking through it; the white rectangle was a second shape, and in a
deadweight wedge only a little wider than the word it names, the rectangle's
edges lie across the wedge's own. Shrinking it does not help — measured at
10, 9, 8 and 7px against the wedges in both trade figures, the clearance
never reaches 3px, and 7px is not a size to read a label at.

A halo round the letters was tried and dropped: Ian wanted it like the
source, and the source has neither. It fills each wedge solid and sets DWL
straight on it, where the edges vanish under the word simply because the word
is painted last. Plain text does exactly that here.

So `check_file.py` reports an area label over a curve as a WARN now, not a
FAIL. Since v2.46 a line cannot be drawn *through* one — it passes behind the
letters — and whether it still reads is a judgement rather than a
measurement. It stays a FAIL against a point, a brace and every other label,
which are painted after it. Two of the three overlaps reported in the
government-intervention file were area labels over curves and are warnings
now; the third, a DWL over a marked point, is unchanged.

`boxed: true` keeps its job for a label over a *gap* in the drawing — the
importers' rectangle, a Lorenz year on its own curve — where the box reads as
deliberate because nothing of the shape runs under it.

## 2026-09-30 — chapter 15 reconverted, now that the matrix exists

The game-theory chapter shipped with no widgets at all, because a payoff
matrix was not in the schema and hand-writing one into a notes file is what
rule 2 forbids. The matrix went in at v2.39 and `given` at v2.40; the chapter
is converted now.

Two widgets, both of them the same grid, because that is what the chapter
prints. The first walks the dominant-strategy argument in the chapter's own
order — four comparisons, each one filling in the move being held fixed and
lighting the two payoffs it is between — and lands on the cell both firms
choose. The second is the repeated game: 2025 both comply, 2026 Firm A
undercuts, 2027 Firm B answers, so the reader sees where on the matrix each
year falls before the years table underneath adds them up.

The years tables stay images. A table of a repeated game is not a matrix, and
the half of the original feature request that covers it — rows, a running
total, and an arrow carrying one year's move into the next year's answer — is
still open. It is one figure printed twice, so it waits for a second chapter
to need it.

The grid is drawn in the house colours rather than the source's plain black,
which is a choice to revisit if Ian would rather it matched: the source's
black has no way to mark a step, and marking the step is the whole reason the
widget exists.
