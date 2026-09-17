# Open issues

Checkboxes. Keep `CLAUDE.md`'s status paragraph in sync with this file.

---

## Found by running the checker on the delivered files

- [x] ~~`ECO2013-263-SupplyAndDemand.html` names the class in its prose.~~ Three
      references, not one: the section heading, the 15–20% sentence, and "the
      classroom curve". All reworded; the 15–20% figure survives. The checker
      had only caught one of the three because `the class` on a word boundary
      does not match `classroom`; `classroom` is now in its word list.
- [x] ~~Four `<strong>` in the same file are not vocabulary terms.~~ They *are*
      terms — v6 names "inferior goods" as a `<strong>` example. The fault was
      that `(+).` was inside the `<strong>`, so the glossary entry read "Normal
      goods (+).". Now `<strong>Normal goods</strong><b> (+).</b>`, matching the
      sibling `<b>Number of potential buyers (+).</b>`. The checker's advice was
      wrong and has been reworded.
- [ ] **`ECO2013-Widgets-All.html` fails v6's caption rules** — eight
      "Before – / After –" prefixes and four "Price up, quantity up" shorthands.
      Expected: the prototype is dated 9/11/26 and those rules came later. Left
      as delivered. Worth a pass if the prototype is ever published rather than
      kept as a reference.
- [ ] **The prototype's apples widget puts six brace labels on curves.** In four
      of its five scenarios, "Shortage of 80" / "Surplus of 80" sits above the
      price line where a curve runs through it. The fix is `below: true`, which
      is what the v6 step 4 template does for exactly this reason. Pre-existing;
      confirmed identical before and after the v2.1 change. Left as delivered
      along with the captions above.

## PPF (production possibilities frontier)

Docs not yet supplied. Probed against the real engine on 2026-09-17: the
frontier, the combinations table with dots on the curve, points on/inside/
outside, movement along the frontier, and **outward, inward and pivot shifts**
all work with no engine change — a shift of the frontier is the same `from`
mechanic as a shift of supply. What is missing:

- [x] ~~Axis titles are sized for one character, so "Butter" ran into the plot
      and "Guns" was clipped at the right edge.~~ Engine v2.2 anchors the x title
      to the right edge and puts the y title in the headroom above the plot.
- [x] ~~No vertical brace.~~ Engine v2.3 adds `vbraces`. `left: true` puts it
      outside the P axis, mirroring a horizontal brace's `below: true`, with the
      label running up the axis; without it the brace sits inside the plot at a
      quantity. This also gives supply and demand a way to mark the size of a
      price change, which is what `P₁`/`P₂` a pixel apart is standing in for
      today.
- [ ] **No label position along a curve.** Only the first or last point, nudged.
      Both frontiers terminate on the same two axes, so end labels crowd in a way
      D and S never do. Needs a "label at fraction t" option.
- [ ] **No `vlines`** (a vertical reference line at a quantity). Guides cover
      most of it; low priority.
- [ ] Area fills of any kind, so the attainable region cannot be shaded. This one
      is real work, not a small addition. Only needed if the source shades it.
- [ ] The schedule table's first column is always the y-axis good, because rows
      are read as `[price, q, …]`. A PPF table therefore lists the vertical good
      first. Documented rather than changed: renaming would break every config.
- [ ] Prompt v6 step 1 already lists PPF as a graph to convert, but step 3's
      pattern table, step 4's templates and step 5's drawing rules are all supply
      and demand, and hard rule 5 in `CLAUDE.md` still says "P and Q as axis
      labels". Those need PPF rows and a template — more writing than engine
      work.

**Authoring note for whoever writes the first PPF config:** tick the axes where
the combinations are *not*. Every PPF point is a round number, and a point prints
its own value, so a point at 85 beside an `80` tick gives two labels a pixel
apart. Set `showP:false`/`showQ:false` on illustrative points (an "inefficient"
or "unattainable" dot) whose exact coordinates are not the lesson.

## Prompt v6

- [ ] **A PPF's frontier cannot reach an axis unless the intercepts are
      stated.** The bowed-out chai/burrito frontier is drawn only between the
      stated points, so it floats rather than meeting either axis. Extending a
      *curve* to invented intercepts breaks rule 3; v6 permits extending a
      straight line along itself but says nothing about curves. Worth a ruling
      in v7.
- [ ] **Word is not a listed input.** v6's four modes are PDF, notes HTML,
      transcript (where Word *is* named) and change-by-message. Notes supplied as
      a .docx are not covered, and are being handled as mode (a). Worth adding
      properly in a v7, along with how to read a Word table and what to do with
      its inline images.
- [ ] **No PPF pattern or template.** Step 1 lists PPF as a graph to convert, but
      step 3's pattern table and step 4's templates are supply and demand only,
      so the first PPF configs are hand-written from the engine reference. Add a
      PPF row and a worked template in v7 so the next chapter is not hand-built.
- [ ] **v6 must keep forbidding questions** even though `CLAUDE.md` now allows
      them here — it runs unattended in Cowork. Deliberate divergence, recorded
      in `CLAUDE.md` under *Asking questions*.

- [ ] **Does the two-movement-arrow rule apply to an equilibrium-shift widget?**
      Step 5 says "every surplus or shortage walkthrough" ends with two movement
      arrows; step 3's pattern table lists "Surplus / shortage" (hlines + braces)
      and "Equilibrium shift" (shift + gap brace) as different patterns, and step
      4's symbolic template for the second has no `moves`. The checker currently
      reads the rule as applying to the first only. If that is wrong, the step 4
      template needs `moves` added and the 263 file has two widgets to fix.
- [ ] **Figure mode is specified but not implemented** (below). Either build it
      or cut it from the prompt, because a config written to that part of the
      prompt throws.

- [ ] **Prompt v6 step 0 specifies the wrong head order.** It lists the two
      preconnects and the font link before `sn25-v6.css`; the current house
      files put `sn25-v6.css` first, then the three font links on one line.
      Ian gave the correct block on 2026-09-17. `check_file.py` warns on the
      old order rather than failing it, because the delivered
      `ECO2013-263-SupplyAndDemand.html` still carries it.
- [ ] **`content/sn25-v6.js` returns 403 from S3** and is the only one of the
      five house assets that is not public (`content/sn25-v6.css`,
      `content/sn25-v5.js`, `studyguide/sn25-v2.js` and `studyguide/sn25-v2.css`
      all return 200). That script is what builds the table of contents and
      drives the sticky header, so while it 403s a published notes page gets
      neither. **One for Ian: check that object's permissions.** Until then
      `scripts/add_toc.py` writes the contents into the file.
- [ ] **Remove the written-in contents once that object is public.** The house
      script does not look for an existing block before inserting its own, so a
      page would then show two. `check_file.py`'s `toc` group reports the state
      either way.
- [ ] **Prompt v6 says nothing about the table of contents.** Step 0 should say
      where it comes from and, while the script is unreachable, that
      `scripts/add_toc.py` runs after step 7.
- [ ] **Neither house file carries `<div id="sticky-header">`**, which the house
      script needs before it will track the current heading. Worth asking
      whether published pages are meant to have one.
- [ ] **Reorder the head of `ECO2013-263-SupplyAndDemand.html`?** It is Ian's
      delivered file, so it is reported rather than rewritten. One for Ian.

## The label test

- [x] ~~Arrows are tested against labels, but not against curves or each
      other.~~ Added, and regression-tested against the two defects that
      prompted them: two arrows abutting into what looks like one, and an arrow
      lying across a frontier. Both warn.
- [ ] **Arrow-versus-guide was tried and dropped.** It fired ten times on
      correct work, because a surplus or shortage arrow has to cross the guides
      between the price line and the equilibrium. A check that fires on correct
      output teaches people to ignore it. Distinguishing "crosses a guide"
      (fine) from "runs along one" (not) needs a parallelism test, not a
      distance test.
- [x] ~~The checker has no tests of its own.~~ `scripts/test_check_file.py`: one
      deliberate defect per check, plus five sentences that must *not* trip the
      source rules, plus an assertion that no arrow or source finding appears on
      any example file. Verified by mutation — breaking the abut threshold, the
      source nouns and the curve test each makes it fail.

## Engine

- [x] ~~A schedule-shift widget draws four red arrows: one per schedule row at
      1.4px, plus a heavier 2.4px shift arrow at a price between rows.~~ Engine
      v2.1: `shiftArrow: false` drops the redundant arrow while keeping the
      slide and the dimming, and every arrow is now 2.4px. Both example files
      and prompt v6 step 5 updated.

- [ ] **Figure mode throws.** `buildPanel` reads `cfg.axes.cents` with no guard,
      so a figure-mode config (title + steps only, hand-written SVG) dies with
      `Cannot read properties of undefined (reading 'cents')` and renders
      nothing. The fix is small — skip panel building when there are no `axes`,
      and drive `data-at`/`data-until` on the div's own SVG from the step index —
      but it is an engine change, so it needs a version bump and a re-embed
      everywhere (hard rule 1).
- [x] `preset:"shift"` drew its gap brace with `below` unset, so the label sat
      above the axis and landed on whichever curve crossed that price. Fixed in
      engine v2.7: the preset now matches the hand-written template. Found by
      rendering the six worked examples in
      `examples/ECO2023-263-SupplyAndDemand.html`, which are the repo's first
      use of the preset -- `check_file.py` skips preset widgets, because the
      engine computes their geometry, so only a render catches this class of
      defect.
- [ ] No automatic collision detection in the engine. `check_file.py` now does
      the x-position test statically, which covers the common cases; genuinely
      overlapping text at render time still needs `render_widgets.py` and a
      person.
- [ ] Only two panels are supported. A four-panel figure (the prompt mentions
      `image-wide-85` for them) would need engine work.

- [ ] **A curve label can only sit at the first or last point.** Both ends of a
      full production possibilities frontier are on an axis, so a period label
      ("2026", "Senior") has to be nudged into open space by hand with `ldx`/
      `ldy` and re-rendered to check it. A way to anchor the label to a chosen
      point of `pts`, or to a data coordinate, would remove the guesswork.
- [ ] **Point labels are one line of SVG text.** The printed zone labels on a
      PPF are two lines ("Attainable &" / "Efficient"), so
      `ECO2023-263-ThePPF.html` shortens them to "Efficient" / "Inefficient" and
      puts the full wording in the caption.
- [ ] **A `moves` arrow spans the whole chord.** When the chord ends on an axis,
      an inside offset drops the arrow below the axis, and the only way to stop
      it short is to fake the `to` coordinate (the gumballs widget's D→E arrow
      ends at `[3.8, 0.9]`). An explicit trim or a `shorten` would be honest.

- [ ] **No area fill in the engine.** The total revenue figure in
      `ECO2023-263-Elasticity.html` shades the price-times-quantity rectangle
      under the demand curve; the widget marks the midpoint and shows the
      revenue hump beside it instead.
- [ ] **`check_file.py` skips preset widgets**, because the engine computes
      their geometry, so its label test never sees them. The v2.7 brace defect
      lived in the repo unnoticed for exactly that reason and only a render
      caught it. Either expand the preset in the checker, or make the render
      pass mandatory for any file that uses one.
- [ ] **LibreOffice here has no Writer module** (`libswlo.so` absent), so
      `soffice` fails on every Word file, `.doc` and `.docx` alike. `antiword`
      and `catdoc` read `.doc`; `.docx` is parsed directly. Worth installing
      the Writer module if figure rendering from Word is ever wanted.
- [ ] **Heading levels come from the source's run formatting**, not from
      structure: bold alone is `<h1>`, bold and underlined at size 23 is
      `<h2>`. A binary `.doc` gives no such spans through `antiword`, so
      document 3's levels were read from paragraph alignment (centred is
      `<h1>`). Prompt v6 step 0 should state the rule.
- [ ] **Exam tip titles are written, and go under the paragraph they belong
      to.** Ian's convention is a short topic phrase -- "Opportunity Costs
      Calculation", "PPF Shape" -- and the block sits *after* the paragraph it
      comments on, never before it. The source's boxes are headed only "Exam
      Tip". Prompt v6 step 0 should say both things.

## Workflow

- [ ] **No list of who may be named, by choice.** Hard rule 4 covers the policy:
      the checker raises a WARN on "Professor X" / "Dr. X" and never fails, and
      Ian decides each time. If that ever becomes too much traffic, the options
      already weighed were a committed names-only deny-list or a gitignored one;
      both were declined in favour of keeping the judgement manual.
- [ ] The name check only catches a title + name. Someone named by surname alone
      is indistinguishable from any other capitalised word without a list, so it
      passes silently.

- [ ] **Where do finished files get published?** An S3 path, the LMS, or
      somewhere else. Unknown — one for Ian.
- [ ] **Does the professor's PDF for the Fall '26 chapter exist yet?** The
      transcript build flagged examples as "needs numbers"; the PDF would settle
      them. Unknown — one for Ian.
- [ ] The rest of `eco-widgets.zip` never arrived: the 30 reference PNGs, the
      original `ECO2013-Sample.html`, the GEB3373 style precedent, the
      `transcript-test-changelog.md`, and the v4→v5 archive. The engine, both
      examples and prompt v6 are here, which is the part that matters.
- [ ] `scripts/render_widgets.py` needs `pip install playwright`. It uses the
      Chromium already under `/opt/pw-browsers/` rather than downloading one.

- [ ] **Is document 2 a different course from document 1?** `1 - ECO2013 …` is
      Dr. Knight's; `03-ECO2023-Fall26-Exam1-PPF.docx` is Dr. Rush's, with its
      own chapter numbering and its own examples, and the two overlap heavily on
      the PPF. They were described as four chapters of one exam. The output is
      named `ECO2023-263-ThePPF.html` from the file name, per v6 step 0; if that
      is wrong the file name has to change before publication. One for Ian.
- [ ] **The PPF document contradicts itself about the freshman → senior shift.**
      One paragraph says study skills improved more, the next says socializing
      skills did. The drawing says socializing, and the widget follows the
      drawing. Recorded in `docs/changelogs/the-ppf-changelog.md`. One for Ian.
