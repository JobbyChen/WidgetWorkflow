#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for scripts/curve_shapes.py.

    python scripts/test_curve_shapes.py

Each case asserts the property the generator exists to guarantee. They are
cheap, and they are the difference between "MC looks like it cuts ATC at the
minimum" and knowing that it does.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import curve_shapes as C

FAILS = []


def check(name, ok, detail=""):
    print(("ok   " if ok else "FAIL ") + name + (" -- " + detail if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


# MC has to pass through the lowest point of each average curve
avc, atc, mc = C.cost_family([40, 18], [58, 50])
mcd = dict((x, y) for x, y in mc)
check("MC meets AVC at its minimum", mcd.get(40) == 18.0, str(mcd.get(40)))
check("MC meets ATC at its minimum", mcd.get(58) == 50.0, str(mcd.get(58)))
check("AVC stays below ATC where both are drawn",
      all(C.sample(lambda q: 0.018 * (q - 40) ** 2 + 18, [x])[0][1]
          < 0.032 * (x - 58) ** 2 + 50 for x, _ in avc))

# the two averages converge, so their right arms run nearly parallel -- at
# the same quantity, not at whichever x each curve's samples happen to end
x = min(avc[-1][0], atc[-1][0])
d_avc, d_atc = 2 * 0.018 * (x - 40), 2 * 0.032 * (x - 58)
check("the average curves' arms have similar slopes at the same quantity",
      abs(d_avc - d_atc) < max(d_avc, d_atc) / 2.0,
      "at q=%s: %.2f vs %.2f" % (x, d_avc, d_atc))
check("the gap between the averages narrows as output grows",
      (0.032 * (avc[-1][0] - 58) ** 2 + 50) - avc[-1][1]
      < (0.032 * (avc[0][0] - 58) ** 2 + 50) - avc[0][1])

# a tangency touches its line rather than crossing it
pts = C.tangent_to_line(92, 92, 46, C.around(46))
line = lambda x: 92 - x
check("the tangent curve meets the line at the chosen basket",
      abs(dict((x, y) for x, y in pts).get(46, 0) - line(46)) < 0.6)
check("the tangent curve stays above the line everywhere else",
      all(y >= line(x) - 0.6 for x, y in pts))

# sampling either side of a basket, in order, however low the basket sits
check("sampling around a low basket is in order",
      C.around(14) == sorted(C.around(14)), str(C.around(14)))
check("sampling around a basket reaches well past it",
      max(C.around(30)) > 3 * 30 and min(C.around(30)) < 30)

# the market's supply lies right of every firm's, at every price
firm, market = C.supply_fan(86), C.supply_fan(106)
check("the market supply curve is right of a firm's at every price",
      all(m[0] >= f[0] for m, f in zip(market, firm)))
check("supply leaves the origin flat and ends steep",
      firm[1][0] / 86.0 < 0.3 and firm[-1][1] == 100.0)

# a crossing is computed, not typed
check("a crossing lands where both lines meet",
      C.cross([[8, 8], [96, 96]], [[8, 92], [96, 4]]) == [50.0, 50.0])

print("\n%d failing" % len(FAILS))
sys.exit(1 if FAILS else 0)
