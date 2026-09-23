---
description: Screenshot every widget, scenario and step for collision review
---

Run `python scripts/render_widgets.py $ARGUMENTS` and then **look at every PNG**
it writes — each widget, at each scenario, at each step.

You are checking what the scripts cannot:

1. Does any label touch a curve, a point, an arrow or another label?
2. Does every curve pass exactly through its numbered points?
3. Do the shift and movement arrows read clearly — beside the curve, in open
   space, never crossing each other?
4. After a shift, do the original and shifted curve labels sit at the same end
   of their curves with the same offsets?

Fix by moving the geometry or using `ldx`/`ldy`/`lstart`/`dx`/`dy`/`arrowP`/
`offset`; the placement rules are step 5 of `docs/conversion-prompt-v7.md`.

The script waits out the engine's 0.6s shift animation before each shot, so a
curve caught mid-slide means the wait needs raising, not that the config is
wrong. `shots/` is gitignored — do not commit screenshots.
