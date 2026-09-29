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

# marginal revenue: the same intercept, exactly twice the slope
d = [[0.0, 100.0], [110.0, 12.0]]
m = C.mr(d)
check("marginal revenue starts where demand starts",
      m[0] == [0.0, 100.0], str(m))
check("marginal revenue falls exactly twice as fast as price",
      abs((m[1][1] - m[0][1]) / m[1][0] - 2 * (d[1][1] - d[0][1]) / d[1][0]) < 1e-6,
      str(m))

# the exponential marginal cost curve: leaves the price axis, passes through
# the average minimum it cuts, and never doubles back
mc = C.exp_through(13, (54, 51), (74, 110), through=(47.6,))
check("marginal cost leaves the price axis, not the corner",
      mc[0] == [0.0, 13.0], str(mc[0]))
check("marginal cost rises the whole way",
      all(b[1] > a[1] for a, b in zip(mc, mc[1:])), str(mc))
check("the average minimum is a sample of marginal cost, not a point between two",
      [54.0, 51.0] in mc, str(mc))
check("a quantity asked for is a sample too",
      any(abs(q - 47.6) < 1e-6 for q, _ in mc), str(mc))
check("no two samples crowd into one another",
      min(b[0] - a[0] for a, b in zip(mc, mc[1:])) > 1.0, str(mc))
f = C.exp_fit(13, (54, 51), (74, 110))
check("the fitted curve hits both points it was given",
      abs(f(54) - 51) < 1e-6 and abs(f(74) - 110) < 1e-6)

# --- lorenz: every Lorenz curve runs corner to corner and bows below the
# line of equality, and k alone says how far. Two typed by hand for one
# figure cross each other as often as not.
for _k in (1.0, 1.45, 2.1, 3.2):
    _p = C.lorenz(_k)
    check("lorenz(%s) starts at the origin" % _k,
          abs(_p[0][0]) < 1e-9 and abs(_p[0][1]) < 1e-9, str(_p[0]))
    check("lorenz(%s) reaches the far corner" % _k,
          abs(_p[-1][0] - 100) < 1e-9 and abs(_p[-1][1] - 100) < 1e-9, str(_p[-1]))
    check("lorenz(%s) never rises above the line of equality" % _k,
          all(y <= x + 1e-9 for x, y in _p),
          str([pt for pt in _p if pt[1] > pt[0] + 1e-9]))

_a, _b = C.lorenz(1.5), C.lorenz(3.0)
check("a bigger k is the less equal curve, at every household share",
      all(yb <= ya + 1e-9 for (_, ya), (_, yb) in zip(_a, _b)))
check("and it is a different curve, not the same one",
      any(yb < ya - 1e-6 for (_, ya), (_, yb) in zip(_a, _b)))

try:
    C.lorenz(0.8)
    check("lorenz refuses a k below 1", False, "0.8 was accepted")
except ValueError:
    check("lorenz refuses a k below 1", True)


# --- hug: a plotted Lorenz curve is convex, so it lies below every chord
# between two of its own readings. A spline through the readings alone bows
# above the chord as often as below.
_read = [[0, 0], [20, 5], [40, 15], [60, 30], [80, 55], [100, 100]]
_h = C.hug(_read)
check("hug keeps every reading it was given",
      all(r in [list(p) for p in _h] for r in _read))
check("hug adds three samples between each pair",
      len(_h) == 4 * (len(_read) - 1) + 1, str(len(_h)))
for _i in range(0, len(_h) - 1, 4):
    (_x0, _y0), (_x1, _y1) = _h[_i], _h[_i + 4]
    for _k in range(1, 4):
        _xm, _ym = _h[_i + _k]
        _t = (_xm - _x0) / float(_x1 - _x0)
        check("hug's sample at %s is below the chord" % _xm,
              _ym < _y0 + (_y1 - _y0) * _t + 1e-9)
check("hug stays monotone", all(_h[i][1] <= _h[i + 1][1] + 1e-9
                                for i in range(len(_h) - 1)))
check("hug stays below the line of equality",
      all(y <= x + 1e-9 for x, y in _h))

print("\n%d failing" % len(FAILS))
sys.exit(1 if FAILS else 0)
