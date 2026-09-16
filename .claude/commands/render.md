---
description: Screenshot every widget, scenario and step for collision review
---

Run `python scripts/render_widgets.py $ARGUMENTS` and then **look at every PNG**
it writes — each widget, at each scenario, at each step.

You are checking two things the scripts cannot:

1. Does any label touch a curve, a point, an arrow or another label?
2. Does every dot sit on the curve or crossing it belongs to?

Report what you find per image. For a fix, prefer moving the geometry or using
`"on"` / `"onCurve"` over nudging a label by a pixel or two; the placement rules
are in step 5 of `docs/conversion-prompt-v5.md`.

`shots/` is gitignored — do not commit screenshots.
