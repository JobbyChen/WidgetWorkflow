# Engine reference — `engine/sd-graph.js` v2

Everything a widget can do. If a graph cannot be expressed here, that is an
engine feature request (`docs/open-issues.md`), not a licence to hand-write SVG
in a notes file.

---

## How a widget gets on the page

```html
<div class="sdg"><script type="application/json">
{ ...config... }
</script></div>
```

The engine finds every `div.sdg` on `DOMContentLoaded` and renders it. A config
may also be the div's own text, but the `<script type="application/json">` form
is what conversions produce: it survives HTML escaping and keeps the JSON out of
the reading flow.

A config that throws replaces the widget with a red `.sdg-error` line naming the
problem, rather than leaving a blank space.

Public API: `SDGraph.version`, `SDGraph.render(node)`, `SDGraph.renderAll(root)`,
`SDGraph.presets`.

---

## Two coordinate systems

**Symbolic** — `P₁`/`Q₁` axes, no numbers. Axes run `0…110` on both sides with
the starting equilibrium near `[50, 50]`; curve endpoints are conventionally
`[8, 96] → [96, 8]` for demand and `[8, 12] → [96, 96]` for supply. Use this
whenever the source states no numbers.

**Numeric** — real prices and quantities from the source. Set `min`/`max` to the
range the source uses and give a tick per stated value. Curves are straight
(`"shape": "line"`) with hollow dots on each schedule row.

Nothing else changes between the two. `"mode"` is documentation for the next
person; the engine reads the axes.

---

## Steps and visibility

A widget is a sequence of steps. Each step is one caption plus whatever is
visible at that point.

```json
"steps": [
  {"caption": "One to three complete sentences."},
  {"caption": "..."}
]
```

**`at` and `until` always mean step indexes, everywhere in the schema**, and both
are 0-based. An item is drawn when `step >= at` and, if `until` is given,
`step <= until`. `at` defaults to 0 and `until` to never. They can go on a curve,
point, guide, arrow, brace, label, axis tick, schedule or schedule highlight.

Two keys are deliberately *not* called `at`, because they are not steps:
`label.pos` (position along a curve) and `tick.value` (a coordinate).

With one step the engine shows the caption and no controls; with more it adds
Back/Next and a step counter.

---

## Panels

One panel is written at the top level of the config. Two markets side by side go
in `"panels": [ {...}, {...} ]`, each with its own `label`, `axes` and contents.
Steps and scenarios stay at the top level and drive every panel at once.

---

## Panel contents

### `axes`

```json
"axes": {
  "x": {"label": "Q", "min": 0, "max": 110, "ticks": [...]},
  "y": {"label": "P", "min": 0, "max": 6,   "ticks": [...]}
}
```

`label` is the axis letter — `P` and `Q`, nothing else. A tick is
`{"value": 3, "text": "$3"}`, or `{"on": [...], "text": "P₂", "color": "red", "at": 2}`
to sit on a computed point (see **Solved positions**).

### `curves`

```json
{"id": "D1", "kind": "demand", "shape": "line", "bow": 0.12,
 "from": [8, 96], "to": [96, 8],
 "color": "red", "dash": false,
 "label": {"text": "D₁", "pos": "end", "dx": 8, "dy": 6, "anchor": "start"},
 "marker": {"n": 1, "pos": 0.3},
 "at": 1}
```

| key | meaning |
| --- | --- |
| `id` | needed if anything refers to this curve by name |
| `kind` | `demand` or `supply`; documentation, not geometry |
| `shape` | `line` for straight (numeric graphs); omit for curved (conceptual) |
| `bow` | how far the middle bends from the chord, as a fraction of its length. Default `0.12` curved, `0` straight |
| `color` | omit for the black original curve, `"red"` for the shifted one |
| `label.pos` | `"start"`, `"end"`, or a number `0`–`1` along the curve |
| `marker` | numbered disc on the curve, for conceptual graphs |

**Bow direction is fixed**: the middle of the curve is always displaced *downward
in price*. On demand that gives the convex-to-the-origin shape; on supply, the
rises-ever-faster shape. A negative `bow` flips it. (Choosing the side
geometrically is not stable — two supply curves a few units apart can fall on
opposite sides of such a test and bow opposite ways. That was a real bug.)

### `points`

```json
{"x": 50, "y": 50, "style": "hollow", "r": 4, "color": "red",
 "label": {"text": "E₁", "dx": 7, "dy": -13, "anchor": "start"}, "at": 2}
```

Hollow by default, which is what the printed artwork uses. `"style": "solid"`
fills it.

### `guides`

The dashed lines that drop from a point to the axes.

```json
{"y": 50, "from": 0, "to": 50}      // horizontal, from the P axis across
{"x": 50, "from": 0, "to": 50}      // vertical, from the Q axis up
```

`"dash": false` makes it solid; `"color": "red"` ties it to a shifted curve.

### `arrows` and `moves`

```json
{"from": [20, 74], "to": [38, 74], "curved": 0.14,
 "label": {"text": "..."}, "at": 1}
```

`moves` is drawn identically and exists only to say what an arrow means: `arrows`
for a shift, `moves` for movement along a curve. **Every arrow is red** — shift,
movement and schedule arrows alike. There is no colour option, on purpose.

`curved` bows the arrow; `true` uses a default bow.

### `braces`

For a surplus, a shortage, or the size of a gap.

```json
{"y": 82, "from": 28, "to": 72, "below": false, "depth": 7,
 "label": {"text": "Surplus"}, "at": 1}
```

Give `y` for a horizontal brace spanning quantities, or `x` for a vertical one
spanning prices. **`below` decides which side the label sits on — set it whenever
the near side already holds a curve or another label.** This is the single most
common cause of a colliding label.

### `labels`

Free text at a coordinate: `{"x": 70, "y": 90, "text": "...", "anchor": "start"}`.
Use it sparingly; a label attached to the thing it names is better.

---

## Solved positions

Hand-guessed coordinates are the main source of dots that sit *beside* an
intersection instead of on it, because a bowed curve does not pass through the
midpoint of its chord. Two keys let the engine work the position out instead.
Both are resolved once, before anything is drawn.

**`"on": ["D1", "S"]`** — the crossing of two curves, by `id`.

**`"onCurve": {"curve": "D", "y": 70}`** — the point on one curve at that price.
Use `"x"` instead for a quantity.

Either may go on a **point**, a **guide**, an **axis tick**, or an **arrow
endpoint** (in place of the `[x, y]` pair). On a guide, add `"axis": "h"` or
`"axis": "v"` to say which line you want; `to` then defaults to the point, so the
guide runs from the axis to the curve and stops.

```json
"points": [{"on": ["D2", "S"], "label": {"text": "E₂", "dx": 7, "dy": -13}}],
"guides": [{"on": ["D2", "S"], "axis": "h"}, {"on": ["D2", "S"], "axis": "v"}],
"moves":  [{"from": {"onCurve": {"curve": "D", "y": 70}},
            "to":   {"onCurve": {"curve": "D", "y": 40}}, "curved": 0.09}]
```

### Where an equilibrium label goes

At a crossing the curves occupy the diagonals — supply runs north-east to
south-west, demand north-west to south-east — so the four free wedges are due
north, south, east and west. Equilibrium labels use north and south, nudged
sideways to clear the dashed guide dropping from the point:

```json
"label": {"text": "E₁", "dx": 7,  "dy": -13, "anchor": "start"}   // north
"label": {"text": "E₂", "dx": -7, "dy": 21,  "anchor": "end"}     // south
```

The north-east and south-west diagonals look empty on a rough sketch and are not.

---

## Schedules

A price/quantity table beside the graph, with the dashed grid of the printed
artwork.

```json
"schedule": {
  "heading": "Quantity demanded, before and after",
  "head": ["Price", "Before", "After"],
  "rows": [["$5", "10", "20"], ["$4", "20", "30"]],
  "shiftColumn": 2,
  "arrows": ["up", "up"],
  "highlight": [{"row": 1, "at": 1}],
  "at": 0
}
```

`shiftColumn` is the 0-based index of the after column, printed red. `arrows`
gives one per row — `"up"`, `"down"`, `null`, or any string — in a borderless
red column; an array of nothing but nulls adds no column. `highlight` tints a row
on the steps you name. Several tables go in `"schedules": [...]`.

`heading` is a table label, not prose — the full-sentence rule is for step
captions only.

---

## Scenarios

The buttons that put several cases of one lesson in a single widget (four apple
shifts; surplus and shortage; an increase and a decrease of one schedule).

```json
"scenarios": [
  {"label": "Demand increases", "overlay": { ...config keys... }},
  {"label": "Demand decreases", "overlay": { ...config keys... }}
]
```

Each overlay is merged onto the base config: objects merge key by key, **arrays
and scalars replace wholesale**. So an overlay that changes one curve must list
every curve. Switching scenario returns to step 1.

---

## Presets

A preset is a config that starts `"preset": "shift"` and expands in the engine.
Any other key you write alongside it is merged over the expansion, so a preset is
a starting point, not a cage.

### `"preset": "shift"`

A routine one-curve shift on symbolic axes, in three steps.

```json
{"preset": "shift", "curve": "demand", "direction": "right", "magnitude": 18,
 "title": "...", "steps": [{"caption": "..."}, {"caption": "..."}, {"caption": "..."}]}
```

`curve` is `demand` or `supply`; `direction` is `right` or `left`; `magnitude`
defaults to 18 units. It emits both curves plus the other one, both equilibria
(solved with `on`, not guessed), their guides and ticks, and one red shift arrow.
Supply and demand are moved in the economically correct direction, so a right
shift of supply lowers the price and raises the quantity.

Write your own `steps` — the defaults are placeholders, and a caption must be
prose ending with the change in P and Q in words.

It emits **no brace**. The brace it used to emit lacked `below: true` and
collided with the other curve; rather than ship a preset that produces a
colliding label, it emits none and you add one when you want it.

### `"preset": "double"`

Two panels side by side with symbolic axes and a shared step list. You supply the
panels; the preset only fills in the axes defaults.

---

## Geometry, for placing labels by hand

The plot is drawn in a fixed `460 × 340` viewBox that scales to the column width.

| | |
| --- | --- |
| plot area | x `52 … 426`, y `22 … 296` (SVG units, y down) |
| margins | left 52, right 34, top 22, bottom 44 |
| symbolic axes | `0 … 110` → 374 px across, 274 px up |

So on symbolic axes one data unit is about 3.4 px across and 2.5 px up. `dx`/`dy`
on a label are SVG units, not data units, and `dy` is positive downward.

---

## What the engine does not do

- **Figure mode.** Hand-drawn SVG process diagrams with `data-at`/`data-until`
  are described in the conversion prompt but are not implemented. A config with
  no `axes` and no `panels` throws a clear error rather than rendering nothing.
- **Elasticity, surplus shading, tax wedges, kinked curves.** No area fills of
  any kind.
- **Three or more curves of the same kind** are fine to declare, but nothing
  helps you place their labels.
- **Automatic collision avoidance.** Labels go where you put them. That is what
  `scripts/render_widgets.py` and a human looking at the PNGs are for.
- **Responsive relayout.** Panels wrap at narrow widths; the plot itself only
  scales.
