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
