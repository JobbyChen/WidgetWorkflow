# ECO2013 / ECO2023 interactive graph widgets

Smokin' Notes publishes HTML course notes. The supply-and-demand chapters were
illustrated with static graph images, so every semester's new examples — a
different good, different numbers, a different shift — meant new artwork. This
repo replaces those images with widgets drawn from a JSON config, so a new
semester is a config edit, and students can step through a graph instead of
reading a finished picture.

**Start with `CLAUDE.md`**, then `docs/decisions-and-history.md` and
`docs/open-issues.md`.

## Layout

```
engine/sd-graph.js      the widget engine (v2). One copy. Everything renders from this.
engine/sd-graph.css     its stylesheet — all arrows red
docs/                   the conversion procedure, the JSON schema, history, open issues
examples/               engine test bed
scripts/                embed the engine, check a file, screenshot every widget state
reference-images/       the source PNGs (empty — see open issues)
.claude/commands/       /convert, /check, /render
```

## The workflow

Input is notes (PDF or HTML), a lecture transcript, or a message saying what
changed this semester. Follow `docs/conversion-prompt-v6.md` — it is the system
prompt, a step-numbered procedure, and every rule in it exists because something
went wrong without it. Output is one HTML file named `COURSE-TERMCODE-Topic.html`
(or a set of patches), plus a changelog.

```
python scripts/embed_engine.py  <file>   # replace <!--SDG-ENGINE--> with the engine
python scripts/check_file.py    <file>   # step 8: must be 0 FAIL
python scripts/render_widgets.py <file>  # then look at every PNG
```

The model never types the engine. It emits a single `<!--SDG-ENGINE-->` line in
the head and `embed_engine.py` fills it in — both that path and re-embedding over
an engine already in place reproduce the published file byte-for-byte.

`render_widgets.py` needs `pip install playwright`; it uses the Chromium already
on the machine rather than downloading one.

## Trying a config

Open `examples/ECO2013-Widgets-All.html` in a browser — the 9/11/26 prototype,
20 widgets carrying every shape the engine draws: schedule plus curve,
movement-along versus shift, schedule shift with per-row arrows,
surplus/shortage with a price line and brace, two-market panels, and the
symbolic presets. Copy those shapes rather than inventing new ones.

## Three rules worth knowing before you touch anything

1. **Never edit the engine casually.** Every published notes file embeds a
   verbatim copy, header comment included, and `check_file.py` verifies byte
   identity. If you change it: bump the version comment, update
   `docs/engine-reference.md`, and re-embed every file.
2. **Numbers come from the source.** Symbolic `P₁`/`Q₁` when the source states
   none; never an invented value.
3. **No label may touch a curve, a point, an arrow or another label.** The engine
   does not check this. `check_file.py` replicates the engine's geometry and
   tests every label against every curve, which catches the common cases; you
   still look at the PNGs.

## Status

The engine, prompt v6, both example files and the scripts are here and verified
against each other. `docs/open-issues.md` has what is outstanding — figure mode
is specified in the prompt but throws in the engine, and the checker found three
small things in the delivered files that are recorded rather than silently fixed.
