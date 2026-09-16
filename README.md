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
changed this semester. Follow `docs/conversion-prompt-v5.md` — it is a
step-numbered procedure and every rule in it exists because something went wrong
without it. Output is one self-contained HTML file named
`COURSE-TERMCODE-Topic.html`, plus a changelog.

```
python scripts/embed_engine.py  <file>   # step 7: inline the engine
python scripts/check_file.py    <file>   # step 8: must be 0 FAIL
python scripts/render_widgets.py <file>  # then look at every PNG
```

`render_widgets.py` needs `pip install playwright`; it uses the Chromium already
on the machine rather than downloading one.

## Trying a config

Open `examples/engine-testbed.html` in a browser. It links `engine/` directly, so
edits show up on reload. Its six fixtures cover every shape the engine draws —
symbolic shift, schedule plus curve, schedule shift with scenarios,
surplus/shortage, two-market panels, and a movement along a curve. The numbers in
them are made up: they are fixtures, not course notes.

## Three rules worth knowing before you touch anything

1. **Never edit the engine casually.** Every published notes file embeds a
   verbatim copy and `check_file.py` verifies byte identity. If you change it:
   bump the version comment, update `docs/engine-reference.md`, and re-embed
   every file.
2. **Numbers come from the source.** Symbolic `P₁`/`Q₁` when the source states
   none; never an invented value.
3. **No label may touch a curve, a point, an arrow or another label.** The engine
   does not check this. You look at the PNGs.

## Status

The engine, procedure, scripts and test bed are here and work end to end. The
finished Fall '26 notes file, the earlier example files, the 30 reference images
and the original project history are not — they were packaged into
`eco-widgets.zip` which never reached this repository. `docs/open-issues.md` has
the details.
