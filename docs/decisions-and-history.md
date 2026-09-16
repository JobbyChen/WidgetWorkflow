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
