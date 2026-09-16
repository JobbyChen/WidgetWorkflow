# Project brief

> The original brief is not in the repository; `docs/conversion-prompt-v6.md` is
> the operating procedure it became, and is authoritative. This page is the
> why behind it.

## The problem

Smokin' Notes publishes HTML course notes for ECO2013 / ECO2023. The
supply-and-demand chapters are illustrated with static graph images — thirty of
them in the Supply and Demand chapter alone. Every semester the examples change:
a different good, different numbers, a different shift. Under the old
arrangement that meant new artwork.

## What was built

A widget engine that draws those graphs from a JSON config, so a new semester's
examples are a config edit rather than new artwork — and, because the graphs are
now live, students can step through them instead of reading a finished picture.

The pieces:

- **`engine/sd-graph.js` + `.css`** — one copy, embedded verbatim into every
  published notes file.
- **`docs/conversion-prompt-v6.md`** — the step-numbered procedure that turns a
  PDF, an HTML file, a transcript, or a "this semester it's hotdogs" message into
  a finished notes file.
- **`scripts/`** — embed the engine, check the result mechanically, screenshot
  every widget state for collision review.

## What the output has to look like

The printed artwork, exactly: black original curve, red shifted curve, every
arrow red, curved D and S with numbered markers on conceptual graphs, straight
lines with hollow dots on numeric ones, dashed grid on schedules, `P` and `Q` as
axis labels, nothing else. No label touching a curve, a point, an arrow or
another label.

And the house format: `sn25-v6.css` / `sn25-v6.js`, `<title>` the chapter name
only, `<p class="date">`, `<h1>`/`<h2>`, `.exam-tip`, plain tables, every
`<!-- IMAGE POSITION: … -->` comment left where its image was.

## Constraints that shaped it

- **Numbers come from the source.** Symbolic `P₁`/`Q₁` when the source states
  none; never an invented value.
- **Student-facing text never names its source.** Paraphrase in original wording
  throughout; flag anything close to source phrasing.
- **No questions mid-conversion.** Carry values over, flag them in the changelog.
  The deliverable is a file plus a changelog that can be scanned.

## Status

The engine, the procedure, the scripts, the finished Fall '26 notes file and the
prototype are all here. The 30 reference images and the earlier changelogs are
not — see `docs/open-issues.md`.
