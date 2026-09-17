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
- [ ] **No vertical brace.** `braces` span quantities at a price (`{p, q1, q2}`).
      The quantity gained can be braced; the quantity given up — the other half
      of every opportunity-cost lesson — cannot. Needs `{q, p1, p2}`.
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
- [ ] `preset:"shift"` draws its gap brace with `below` unset, so the label sits
      above the axis. In the symbolic template the step 4 prompt writes by hand,
      the brace is always `below:true` precisely so the label clears the curves.
      The preset should match the template.
- [ ] No automatic collision detection in the engine. `check_file.py` now does
      the x-position test statically, which covers the common cases; genuinely
      overlapping text at render time still needs `render_widgets.py` and a
      person.
- [ ] Only two panels are supported. A four-panel figure (the prompt mentions
      `image-wide-85` for them) would need engine work.

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
