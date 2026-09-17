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
