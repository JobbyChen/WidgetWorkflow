# Engine reference — `engine/sd-graph.js` v2.6

Written from the engine source. The conversion prompt carries a shorter version
of this in its own "Engine reference" section; that one is what the model needs
to write a config, and this one adds the geometry and the behaviour you only
find by reading the code.

If a graph cannot be expressed here, that is an engine feature request
(`docs/open-issues.md`), not a licence to hand-write SVG in a notes file.

---

## Markup

```html
<div class="sdg"><script type="application/json">{ …config… }</script></div>
```

The engine mounts every `.sdg` on `DOMContentLoaded`. A config that fails to
parse replaces the widget with `Widget config error: …` rather than leaving a
blank space.

The engine is inserted into a notes file by `scripts/embed_engine.py`, which
replaces the `<!--SDG-ENGINE-->` line the model emits. The model never types it.

## Top level

| key | meaning |
| --- | --- |
| `title` | heading above the widget (`<h4>`) |
| `lede` | one intro line under the title |
| `caption` | static caption — used **only** when there are no steps |
| `steps` | array of caption **strings**; index 0 is the start state |
| `scenarios` | `{key: {label, …overrides}}` — one button each |
| `panels` | `[panelCfg, panelCfg]` for two markets side by side |
| `link` | `false` removes the arrow drawn between two panels |

With no `panels`, the panel keys live at the top level.

### Steps, `at` and `until`

An element is visible when `step >= at` and, if `until` is given,
`step < until`. **`until` is exclusive**: `at:2, until:3` shows the element on
step 2 only. `at` defaults to 0.

Steps are strings, not objects. The counter shows step 0 as "Step 1 of N", so no
caption should say "Start".

Controls appear only when `steps.length > 1`: Back, Next step, Start over.

### Scenarios

Overrides are merged **shallowly** over the base config, and switching scenario
rebuilds the widget from scratch. So a scenario that changes one curve must
restate the whole `curves` array. Anything the scenarios share must be written
identically in each, or it will appear to jump when the reader switches.

## Panel

`heading` titles a panel (two-panel widgets only). Text inside the plot is SVG
and scales with the panel's width, so the heading is sized in container-width
units to keep one order at every screen size: **heading, then axis title, then
point label**. Set in fixed pixels it was overtaken by the axis titles on a wide
screen.

### `axes`

```json
{"x": "Q", "y": "P", "xmax": 260, "ymax": 75,
 "xticks": [40, 80, 120], "yticks": [10, 20, 30],
 "money": true, "cents": true, "k": true, "grid": true, "bg": false}
```

`money` prefixes prices with `$`; `cents` forces two decimals; `k` renders
quantities of 1000+ as `12k`. `grid` draws the dashed gridlines at every tick —
the schedule-graph look. `bg:false` removes the tinted plot rectangle.

`x` and `y` are the axis **titles**, defaulting to `P` and `Q`, which is what
the printed artwork uses. A production possibilities frontier names its axes with
words instead ("Guns", "Butter"), so the x title is anchored to the right edge of
the box and the y title sits in the headroom above the plot. Keep them to a word
or two — nothing wraps them.

**A point prints its own price and quantity on the axes** (see `points` below),
so on any graph whose points sit at round numbers, choose ticks that those values
will not land beside. A point at 85 next to an `80` tick produces two labels a
pixel apart. `scripts/check_file.py` tests for this.

### `curves`

```json
{"id": "D2", "label": "D₂", "pts": [[104,16],[20,100]], "color": "red",
 "from": "D1", "arrowP": 88, "shiftArrow": false, "at": 1,
 "curved": true, "thin": true, "dashed": true,
 "lstart": true, "ldx": -26, "ldy": 15}
```

- `pts` are `[q, p]` pairs in data units. Two points fix a straight line; three
  or more with `curved:true` are smoothed into a Catmull-Rom-style spline — the
  conceptual, non-linear look.
- `from` names the curve this one shifts away from. It does three things: the
  new curve **animates** in from the old one's position, a red shift arrow is
  drawn between them at price `arrowP`, and the original curve is **dimmed**
  (thinner, slightly transparent) from that step onward.
- `shiftArrow: false` keeps the animation and the dimming but draws no arrow.
  Set it on any widget whose `table` has `arrows: true`: the per-row arrows
  already show the shift once per schedule row, and a fourth arrow at a price
  that is not in the schedule has no point at either end.
- `thin` draws the original curve of a shift pair; `dashed` dashes it.
- The label sits at the **last** point, or the first with `lstart:true`, nudged
  by `ldx`/`ldy` (defaults `+6` across, `+2` above an upward curve or `+6` below
  a downward one). **`label: ""` draws no label at all** — a lone frontier needs
  no name, since the axis titles already say what it is — while omitting `label`
  falls back to the `id`, which `table.series` still needs.

### `points`

```json
{"q": 120, "p": 30, "label": "Equilibrium", "marker": "1",
 "pl": "P₁", "ql": "Q₁", "color": "red", "at": 3,
 "dx": 13, "dy": 4, "guides": false, "showP": false, "showQ": false}
```

- Draws a hollow dot with dashed guides to both axes, unless `guides:false`.
- `marker:"1"`/`"2"` makes it a larger numbered circle — the Point 1 / Point 2
  convention of the conceptual graphs.
- **The axis labels are automatic.** Unless `showP:false`, the point prints its
  price on the P axis whenever that price is not already a `ytick` and no
  `hline` sits at it; `showQ` does the same on Q. `pl`/`ql` override the number
  with a symbol (`"P₁"`, `"Q₁"`) — which is how symbolic graphs get their axes.
- **A value the point prints for itself is bold; a tick is not.** That makes
  emphasis depend on which ticks you listed, not on what matters: a point at 85
  comes out bold, and the same point comes out plain the moment you add an `85`
  tick. Prompt v6 step 5 resolves it — "ticks are the values the prose uses,
  nothing extra" — so every point value is a tick, nothing is bold, and the dots
  and guides show which values are the points. Mix a generic scale with points
  that miss it and you get some bold and some plain in one graph, which reads as
  if the bold ones matter more. `check_file.py` warns on that mix.
- `label` is separate from the axis labels and is offset by `dx`/`dy`
  (defaults `+9`, `−9`).
- **The step a point belongs to shows on the drawing.** The engine rings
  whatever the current step revealed (`at` equal to the step) and fades back to
  45% whatever an earlier step revealed, so a walkthrough that keeps its earlier
  points on screen still says which one the caption is talking about. Hovering
  any point brings it forward and turns its label orange, the same way hovering
  a schedule row already highlighted its dots.

### `areas`

```json
{"pts": [[0,11],[0,21],[8,11]], "label": "CS", "color": "teal", "at": 2}
```

A shaded polygon, named by its corners in `[q, p]` like everything else. Added
in **v2.11**, because surplus and deadweight loss *are* areas and the engine
could not draw one.

A polygon is enough for this chapter: demand and supply are straight lines
here, so consumer surplus, producer surplus, total surplus and a deadweight
wedge all have straight edges. A region bounded by a `curved` pair is still not
possible — `pts` are joined with straight segments, never splines.

Areas draw **after the axes and before the curves**, so a fill never hides a
line, a point, a guide or a label. The wash is `opacity: .18`, which is why the
colour names matter more than usual: `teal` for consumer surplus, `orange` for
producer surplus, `red` for a loss. Default `ink`.

`label` goes at the polygon's centroid, which keeps it inside a triangle. A
thin wedge has no room for one, so `lp: [q, p]` places it by hand — outside the
shape if that is what fits — and `ldx`/`ldy` nudge it in pixels.

### `moves`

```json
{"from": [58,1.95], "to": [44,1.6], "at": 3, "color": "red", "offset": 14}
```

An arrow between two points, drawn `offset` px **beside** the line joining them
so it never lies on the curve. A negative `offset` puts it on the other side —
which side is correct depends on the geometry, so check it against a render.

### `hlines`

```json
{"p": 2, "label": "$2", "at": 1, "color": "red"}
```

A thick horizontal price line across the plot — a price floor or ceiling, or any
disequilibrium price. It prints its own label on the P axis when that price is
not already a tick. Red by default.

### `braces`

```json
{"p": 2, "q1": 20, "q2": 60, "label": "SURPLUS", "below": true, "at": 2}
```

A curly brace spanning `q1`→`q2` at price `p`. Red by default.

`below:true` puts it under the Q axis (and grows the panel from 250 to 268 units
tall to make room). `below:false` puts it just above the price line **and also
draws vertical guides** from each end down to the axis.

### `vbraces`

The same brace turned upright, spanning a **price** gap rather than a quantity
gap — the other half of an opportunity cost, or the size of a price change.

```json
{"p1": 70, "p2": 85, "label": "15 butter given up", "left": true, "at": 1}
{"p1": 70, "p2": 85, "q": 40, "label": "15 butter", "side": "left", "at": 1}
```

Both kinds of brace size their curl to the span they cover, so a brace across
two dollars on a twenty-five dollar axis is drawn small and clean rather than as
overlapping curves.

`left: true` is the mirror of a horizontal brace's `below: true`: it sits outside
the P axis, clear of the plot and of the tick numbers, and **widens the left
margin by 44px** to fit — the same trade a `below` brace makes for 18px of panel
height. Its label runs up the axis, because horizontal text does not fit in a
54px margin.

Without `left`, it sits inside the plot at quantity `q`, opening right unless
`side: "left"`. Inside the plot it competes with the curves for space, so prefer
`left` unless the gap has to be shown at a particular quantity.

### `table`

```json
{"cols": ["Price","Before","After"], "series": ["D1","D2"],
 "rows": [[5,225,300],[12.5,175,250]], "arrows": true}
```

A schedule beside the graph. `series` names one curve id per quantity column;
each row plots a dot on each series at that price, inheriting the curve's colour
and `at`. `arrows:true` draws a red arrow on the plot from each row's first
quantity to its second — the per-row shift arrows.

**Hovering a table row highlights its dots on the graph**, and vice versa. That
interaction is the point of putting the schedule next to the curve.

## Colours

`ink` (the default, a black-navy), `red` (shifted or new), `teal`, `orange`,
`grey`. Red is reserved: the shifted curve, every arrow, the disequilibrium
price line, its brace and the new equilibrium. Nothing else.

Every arrow is drawn at the same 2.4px weight — shift, movement and per-row
alike — so that two arrows in one graph never read as two different kinds of
thing.

## Presets

```json
{"preset": "shift", "shift": "D", "dir": "right", "size": 20,
 "good": "pasta", "event": "…", "why": "…", "static": true}

{"preset": "double", "demand": "right", "supply": "left",
 "dD": 40, "dS": 15, "arrowD": 20, "arrowS": 88, "note": "…", "static": true}

{"preset": "double", "demand": "right", "supply": "left", "compare": true,
 "big": 40, "small": 15, "headings": ["…", "…"]}
```

A preset expands into a full symbolic config on `110 × 110` axes with the
equilibrium at `[50,50]`. `shift` writes its own four step captions from `good`,
`event` and `why`, and draws the gap brace at the old price on step 2 only,
`below` the axis — above it the SHORTAGE/SURPLUS label lands on whichever curve
crosses that price.
`static:true` collapses everything to step 0 and draws **no brace**, which is
what makes the four-cases-in-one-widget scenario set work.

`arrowD` and `arrowS` move the two shift arrows of a `double`. A shift arrow is
inset from the pair it belongs to, but the *other* pair can still lie across it,
and the defaults (32 and 88) put the demand arrow through S₁ for some shift
sizes. `scripts/render_widgets.py` measures every arrow against every curve and
reports anything closer than 4px, which is how that gets caught.

Presets combine with `title`/`lede`/`caption`/`steps` overrides and with
scenarios, each scenario supplying its own `shift`/`dir`.

## Geometry, for placing labels by hand

| | |
| --- | --- |
| viewBox | `372 × 250`, or `372 × 268` when any brace is `below` |
| origin | `x = 40`, or `54` with `yticks`, or `62` with `cents`; `y = 205` |
| plot width | `372 − left − 36` |
| plot height | `178` |
| `X(q)` | `left + (q / xmax) × PW` |
| `Y(p)` | `205 − (p / ymax) × PH` |

`ldx`/`ldy`/`dx`/`dy`/`offset` are all in these SVG units, and `dy` is positive
downward. `scripts/check_file.py` replicates this geometry to test every label
against every curve, arrow, point dot, axis tick and the values a point prints
for itself — a real overlap fails, and a gap under about six pixels, or a label
pressed against a dashed guide, warns.

Animation: elements cross-fade over 0.45s and shifted curves slide over 0.6s,
both disabled under `prefers-reduced-motion`. A screenshot taken sooner than
that catches a curve mid-slide.

## What the engine does not do

- **Figure mode.** The prompt specifies hand-drawn SVG process diagrams with
  `data-at`/`data-until`, but the engine has no such path: a config with no
  `axes` throws `Cannot read properties of undefined (reading 'cents')` in
  `buildPanel`, and nothing renders. See `docs/open-issues.md`.
- **Collision avoidance.** Labels go where you put them.
- Elasticity and tax wedges. Surplus shading arrived in v2.11 — see `areas` —
  but only as straight-edged polygons: a region bounded by a `curved` pair
  still cannot be filled.
- Three or more panels. A three-panel figure becomes three scenario buttons
  (CLAUDE.md rule 8), which is how the efficiency chapter's elasticity
  comparison and its three deadweight cases are drawn.
