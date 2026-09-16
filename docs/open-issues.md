# Open issues

Checkboxes. Keep `CLAUDE.md`'s status paragraph in sync with this file.

---

## Found by running the checker on the delivered files

- [ ] **`ECO2013-263-SupplyAndDemand.html` names the class in its prose.**
      "…roughly 15% to 20% of the class said their answer would have been
      different." Prompt v6 step 0T: no paragraph may refer to the transcript,
      the lecture, the recording, the board, or the class. One sentence to
      reword; the economics survives without the attribution.
- [ ] **Four `<strong>` in the same file are not vocabulary terms** — "Normal
      goods (+)." and similar are list-item labels, which v6 makes `<b>`. The
      stylesheet renders `<strong>` blue, so these read as glossary entries.
- [ ] **`ECO2013-Widgets-All.html` fails v6's caption rules** — eight
      "Before – / After –" prefixes and four "Price up, quantity up" shorthands.
      Expected: the prototype is dated 9/11/26 and those rules came later. Left
      as delivered. Worth a pass if the prototype is ever published rather than
      kept as a reference.

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
