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

## 2026-09-21 — the trade chapter, and the first area fill

25. **Areas went into the engine rather than around it.** Chapter 7 of the
    ECO2023 Exam 1 material arrived as house HTML with five figures, and every
    one of them is about the size of a shaded region: consumer and producer
    surplus without and with trade, the gains-from-trade triangle, and a
    tariff's revenue rectangle and deadweight-loss triangles. The engine had
    no fill of any kind, recorded twice in the open issues as "real work, only
    if the source shades it". The source shades it. Hard rule 2 rules out
    hand-drawn SVG, and captions describing a triangle nobody can see are not
    a widget, so v2.11 adds `areas`: a polygon in data units, solid, hatched or
    checked, drawn under everything else, with an optional label. It is a
    small addition once you accept that nothing computes the polygon — the
    author names its corners, which on a symbolic graph are all round numbers
    anyway. Every example was re-embedded and every one reports what it did
    before.

26. **The equilibrium point learned to draw half its guides.** The printed
    trade graphs mark P* on the price axis and nothing on the quantity axis,
    and a full drop from the equilibrium runs straight through the
    gains-from-trade triangle and its label. `guides:"p"` and `"q"` draw one
    line or the other. The checker follows: its guide segments are built the
    same way.

27. **The movement-arrow rule was firing on the wrong pattern.** It keyed on
    "any stepped widget with a price line", which was every trade widget: a
    world price is a level the market settles at, not one it converges from,
    and there is nothing to draw an arrow toward. It now needs the line *and*
    a brace labelled surplus or shortage. Narrowing a check is exactly what
    entry 22 warns about, so it went in with a test that the Exports case is
    clean and a run over every earlier file showing the same result as before.

28. **Two of the checker's findings were about its own defaults.** `color:
    "ink"` on a price line was reported as "left at its default" when the
    default for a line is red, so the schema scan now knows which lists are
    red by default. And an area label was landing on the world price line on
    the one step where the old surplus and the new line are both on screen —
    a real finding, fixed by putting the old and new labels in the same spot
    so nothing jumps.

29. **Ian's prose was left alone, with three exceptions.** The request was
    "create the widgets and leave everything else the same", so the body is
    the source's body apart from the five image blocks. The three edits are
    the ones the earlier ECO2023 conversions already made for hard rule 4: the
    textbook box's heading and opening line no longer say "in class", and
    "in the lecture after the exam" is "after the exam". Dr. Rush is named
    once and is listed in the changelog for Ian's call, as always.
