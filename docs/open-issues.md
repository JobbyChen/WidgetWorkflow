# Open issues

Checkboxes. Newest section first. Keep `CLAUDE.md`'s status paragraph in sync
with this file.

---

## Blocking — the repository is missing the earlier work

The project was packaged as `eco-widgets.zip` and handed off on 2026-09-16, but
the zip never reached this repository: it was created empty, with no commits. The
engine, scripts, docs and test bed here were **rebuilt from the specification in
`CLAUDE.md`**. See `docs/decisions-and-history.md` for exactly what that means.

- [ ] **Locate `eco-widgets.zip`.** If it exists, it is the fuller record. Diff
      it against this repo before overwriting anything: the rebuilt engine has
      fixes the original does not (see the two bugs below), so the merge is not
      a straight replacement in either direction.
- [ ] **`examples/ECO2013-263-SupplyAndDemand.html` is missing.** The finished
      Fall '26 Supply and Demand build — nine widgets, transcript-only — is in
      the zip. It cannot be reconstructed here: its numbers and captions came
      from source material this repo does not hold, and inventing them would
      break the numbers-from-the-source rule. It has to come from the zip or be
      converted again from the transcript.
- [ ] **`examples/ECO2013-Sample.html`, `ECO2013-Widgets-All.html`,
      `03-GEB3373-Exam1-TradeRestrictions-FULL.html` are missing** — the input
      format, the 30-image prototype, and the pre-engine style precedent.
- [ ] **`reference-images/` is empty.** The 30 PNGs
      (`eco2013-spring26-supplydemand-NN-*.png`) are in the zip.
- [ ] **`docs/project-brief.md`, `decisions-and-history.md` and the 09-15
      changelog are stubs.** They record what `CLAUDE.md` states plus this
      rebuild. The original numbered decisions and the rejected approaches are
      only in the zip.

Until the zip turns up, `examples/engine-testbed.html` is the reference for
config shapes. It is fixtures with made-up numbers, clearly marked, and is not
for publication.

## Engine

- [x] ~~`preset:"shift"` brace lacks `below:true`, so the label collides with the
      other curve.~~ The preset now emits no brace at all rather than a
      colliding one, and `below` is documented as the thing to set. Reopen if a
      preset brace is wanted back.
- [x] ~~Equilibrium dots sit beside the crossing rather than on it.~~ `"on"` and
      `"onCurve"` make the engine solve the position.
- [x] ~~Bow direction chosen by a "nearest the origin" test flips sign for
      near-diagonal supply curves, so two supply curves a few units apart bowed
      opposite ways and appeared not to shift at all.~~ The bow now always
      displaces the curve downward in price.
- [ ] **Figure mode is specified but not implemented.** Hand-drawn SVG process
      diagrams with `data-at`/`data-until` are in the conversion prompt and not
      in the engine; a config with no `axes` and no `panels` throws a clear
      error. Either implement it or cut it from the prompt. Nothing in the repo
      needs it yet.
- [ ] No automatic collision detection. `scripts/render_widgets.py` produces the
      PNGs and a human looks at them. A crude overlap check on label bounding
      boxes would catch the common cases and could be added to the render script
      rather than the engine.
- [ ] Axis ticks that land within a few units of each other overlap. The engine
      does not nudge them; the author has to move the geometry.
- [ ] `intersect()` is an O(n²) scan over 240 samples per curve. Fine at this
      scale, visibly wasteful if a widget ever has many `on` references.

## Workflow

- [ ] **Where do finished files get published?** An S3 path, the LMS, or
      somewhere else. Unknown — one for Ian.
- [ ] **Does the professor's PDF for the Fall '26 chapter exist yet?** The
      transcript build flagged two examples as *needs numbers*; the PDF would
      settle them. Unknown — one for Ian.
- [ ] `scripts/render_widgets.py` needs `pip install playwright`. It finds the
      pre-installed Chromium under `/opt/pw-browsers/` and does not download a
      browser.
