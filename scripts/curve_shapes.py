#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""The curve shapes these chapters keep needing, generated rather than typed.

Every function here exists because drawing the same shape by eye went wrong
at least once on the ECO2023 conversions:

* a marginal cost curve that missed the minimum of the average curve it is
  supposed to cut there,
* an indifference curve drawn *through* its budget line instead of touching
  it, which is the one thing a tangency figure exists to show,
* a basket placed on the formula behind a curve rather than on the curve, so
  it sat a little off the spline that was actually drawn,
* an equilibrium dot typed as a coordinate and left behind when the curves
  around it moved,
* a supply fan drawn as rays when the source draws it as e^x.

The rule they share: if a point has to lie on something, compute it from the
thing it lies on. A coordinate typed once and edited later is the failure
mode, and it is invisible in a screenshot.

    from curve_shapes import cost_family, cross, supply_fan
"""

import math

__all__ = ["cost_family", "cross", "hyperbola", "on_hyperbola",
           "tangent_to_hyperbola", "tangent_to_line", "supply_fan", "sample",
           "saturating", "cycle"]


def sample(f, xs):
    """f evaluated at each x, as [q, p] pairs the engine takes."""
    return [[x, round(f(x), 1)] for x in xs]


# ---- cost curves ----------------------------------------------------------

def cost_family(avc_min, atc_min, avc_a=0.018, atc_a=0.032,
                avc_xs=None, atc_xs=None, mc_xs=None, mc_vertex=None):
    """AVC, ATC and MC, with MC through the lowest point of each average.

    MC is not a shape anyone should choose: it is fixed by the two crossings
    it has to make. Solving for it means the dots where it cuts AVC and ATC
    sit on all three curves at once, which is what those figures are for.

    `avc_a` is deliberately gentler than `atc_a`: average fixed cost shrinks
    as output grows, so the two averages close on each other and their right
    arms end up running nearly parallel, which is how the artwork draws them.
    Returns (AVC, ATC, MC) point lists.
    """
    (ax, ay), (tx, ty) = avc_min, atc_min
    h = mc_vertex if mc_vertex is not None else ax - 16
    # a(ax-h)^2 + k = ay and a(tx-h)^2 + k = ty
    a = (ty - ay) / float((tx - h) ** 2 - (ax - h) ** 2)
    k = ay - a * (ax - h) ** 2

    avc = lambda x: avc_a * (x - ax) ** 2 + ay
    atc = lambda x: atc_a * (x - tx) ** 2 + ty
    mc = lambda x: a * (x - h) ** 2 + k

    avc_xs = avc_xs or [ax - 26, ax - 16, ax - 8, ax, ax + 10, ax + 18, ax + 26]
    atc_xs = atc_xs or [tx - 42, tx - 32, tx - 20, tx - 10, tx, tx + 12,
                        tx + 24, tx + 38]
    mc_xs = mc_xs or [h - 14, h - 6, h, h + 8, ax, ax + 8, tx, tx + 10, tx + 18]
    return sample(avc, avc_xs), sample(atc, atc_xs), sample(mc, mc_xs)


# ---- indifference curves and budget lines ---------------------------------

def hyperbola(k, xs):
    """y = k/x. One curve of a nested family; no member can leave the box."""
    return sample(lambda x: float(k) / x, xs)


def on_hyperbola(k, x):
    """The basket at x on curve k.

    Use an x that is in the curve's own sample list. A curve is a spline
    through samples, not the formula behind it, so a point taken from the
    formula between two samples sits just off the line that is drawn.
    """
    return [x, round(float(k) / x, 1)]


def tangent_to_hyperbola(k, t, x0, x1):
    """The short line that touches y = k/x at x = t, drawn from x0 to x1."""
    m = float(k) / (t * t)
    y = lambda x: k / float(t) - m * (x - t)
    return [[x0, round(y(x0), 1)], [x1, round(y(x1), 1)]]


def tangent_to_line(c, xint, t, xs):
    """A convex curve touching the line through (0, c) and (xint, 0) at x = t.

    y = k/x + b with k = m t^2 and b = c - 2mt has the line's slope at t and
    meets it there, so the tangency is arithmetic. Points whose y leaves the
    top of the box are dropped.
    """
    m = float(c) / xint
    k, b = m * t * t, c - 2.0 * m * t
    return [q for q in sample(lambda x: k / x + b, xs) if q[1] <= 106]


def around(t, lo=6, hi=108, shares=(0.45, 0.62, 0.8, 1.0, 1.4, 2.0, 3.0, 4.4, 6.0)):
    """Sampling points either side of t, in proportion to it and in order.

    A curve sampled a fixed distance either side of its tangency reads as
    beginning where it touches. Shares of t keep the upper branch tall and
    the tail long whether the basket sits at x = 14 or x = 62. Sorted after
    clamping, or a low tangency doubles the curve back on itself.
    """
    return sorted(set(round(min(hi, max(lo, t * f)), 1) for f in shares))


# ---- supply -------------------------------------------------------------

def supply_fan(top, k=3.0, ys=(0, 0.25, 0.45, 0.62, 0.76, 0.88, 1.0), pmax=100.0):
    """p = A(e^(kq) - 1): along the bottom, then almost vertical at `top`.

    The source's market-supply figure fans four of these out and lays a
    flatter one to the right of them all. Same k and a larger `top` puts a
    curve right of every other at every price, which is what the market
    curve has to do.
    """
    denom = math.exp(k) - 1.0
    return [[round(top * u, 1), round(pmax * (math.exp(k * u) - 1) / denom, 1)]
            for u in ys]


# ---- crossings ----------------------------------------------------------

def cross(a, b):
    """Where two straight two-point curves meet, as [q, p].

    Name the crossings and build the equilibrium dots from them. Typed as
    coordinates they get left behind the moment a curve moves, and a dot a
    few units off its crossing looks deliberate.
    """
    (x1, y1), (x2, y2) = a[0], a[-1]
    (x3, y3), (x4, y4) = b[0], b[-1]
    d = (x2 - x1) * (y4 - y3) - (y2 - y1) * (x4 - x3)
    if not d:
        raise ValueError("those two curves are parallel")
    t = ((x3 - x1) * (y4 - y3) - (y3 - y1) * (x4 - x3)) / d
    return [round(x1 + t * (x2 - x1), 1), round(y1 + t * (y2 - y1), 1)]


def exp_fit(y0, hit, top):
    """The function p = y0 + A(e^(kq) - 1) through (0, y0) and two more points.

    Returned as a callable so a crossing can be solved against the real curve
    and then handed back as a sample of it -- a dot solved against the polyline
    instead lands off the drawn spline, which is how chapter 12 shipped
    equilibrium markers beside their own crossings.
    """
    (q1, p1), (q2, p2) = hit, top
    want = (p2 - y0) / float(p1 - y0)
    lo, hi = 1e-6, 1.0
    for _ in range(200):                      # k is monotone in the ratio
        k = (lo + hi) / 2.0
        got = (math.exp(k * q2) - 1) / (math.exp(k * q1) - 1)
        if got < want:
            lo = k
        else:
            hi = k
    k = (lo + hi) / 2.0
    a = (p1 - y0) / (math.exp(k * q1) - 1)
    return lambda q: y0 + a * (math.exp(k * q) - 1)


def exp_through(y0, hit, top, qmax=None, n=9, through=()):
    """p = y0 + A(e^(kq) - 1), starting at the P axis and through two points.

    The chapter 13 marginal cost curve has to do three things at once: leave
    the price axis rather than the corner, pass exactly through the minimum of
    the average total cost curve it cuts, and climb out of the top of the plot.
    A parabola fitted to those three fell to a vertex inside the plot and came
    out of the axis sloping downwards, which is not what the figure draws; the
    exponential is the shape Ian asked for -- "more like e to the x" -- and is
    monotone by construction, so it cannot double back.

    `hit` is the point it must pass through (the average minimum) and `top` is
    where it should leave the plot. Every quantity in `through`, and `hit`'s
    own, is forced into the sample list, so a dot placed at one of them sits on
    the spline the engine draws rather than on the polyline through it.
    """
    f = exp_fit(y0, hit, top)
    end = top[0] if qmax is None else max(top[0], qmax)
    step = end / float(n - 1)
    keep = sorted(set([round(q, 4) for q in (hit[0],) + tuple(through)]))
    grid = [end * i / float(n - 1) for i in range(n)]
    xs = sorted([x for x in grid
                 if all(abs(x - q) > step / 2.0 for q in keep)] + keep)
    return sample(f, xs)


def mr(d_pts):
    """Marginal revenue for a straight demand curve: same intercept, twice the
    slope, stopped where it reaches zero.

    Drawn by eye it came out at some slope between once and twice, which is the
    one quantitative fact these figures exist to show.
    """
    (q1, p1), (q2, p2) = d_pts[0], d_pts[-1]
    m = (p2 - p1) / float(q2 - q1)
    c = p1 - m * q1
    return [[0.0, round(c, 1)], [round(-c / (2 * m), 1), 0.0]]


def lorenz(k, top=100.0, n=9):
    """A Lorenz curve: y = top*(x/top)**k, sampled from (0,0) to (top, top).

    Every Lorenz curve runs corner to corner and bows below the line of
    equality, and k alone says how far: k = 1 is the line itself, and larger
    is less equal. Typed as coordinates, two of them drawn for the same
    figure cross each other as often as not -- y = x**k cannot, for k above 1,
    so an ordering the figure exists to show is a property of the numbers
    rather than something to check by eye."""
    if k < 1:
        raise ValueError("a Lorenz curve cannot rise above the line of equality")
    return [[round(top * i / float(n - 1), 2),
             round(top * (i / float(n - 1)) ** k, 2)] for i in range(n)]


def hug(pts, sag=0.05, n=3):
    """A convex curve through every point given, hugging below the chords.

    A Lorenz curve plotted from a table is a spline through five readings, and
    a spline bows *above* the chord as often as below it -- which leaves the
    bottom early and arrives at the top corner gently, where the source does
    the opposite. This adds `n` samples inside each chord, pulled below it by
    a parabola that is `sag` of the chord's rise at its deepest.

    `sag` is small on purpose. One deep sample per chord bows each segment
    hard and leaves a kink at every reading, which is worse than the problem:
    several shallow ones read as one smooth curve. The stated readings are
    untouched, so the curve still passes exactly through all of them."""
    out = []
    for i in range(len(pts) - 1):
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        out.append([x0, y0])
        for k in range(1, n + 1):
            t = k / float(n + 1)
            out.append([round(x0 + (x1 - x0) * t, 2),
                        round(y0 + (y1 - y0) * t
                              - sag * (y1 - y0) * 4 * t * (1 - t), 2)])
    out.append(list(pts[-1]))
    return out


# ---- macro shapes ---------------------------------------------------------

def saturating(through, xmax, n=15, extra=()):
    """y = top*(1 - e**(-x/tau)) from the origin through two stated readings.

    The macroeconomic production function. Output rises with labour and every
    extra worker adds less than the one before, which is the law of
    diminishing returns the figure exists to show -- so the curve cannot be a
    spline through the readings alone: a spline through three points that lie
    on a concave curve bows the wrong way between them as readily as the right
    way, and the chapter's whole point is the shape between the readings.

    Two readings fix `top` and `tau` (bisection on tau; the curve through the
    origin is concave exactly when the second reading falls short of the
    straight line through the first). A third is checked against the fitted
    curve and raises rather than being fitted, because a chapter whose stated
    numbers do not lie on one curve is a thing to find out about, not to draw
    smooth. `extra` lists x values to force into the sample list, so a point
    the figure marks sits on one of the curve's own samples (v2.45's rule).
    """
    (x1, y1), (x2, y2) = through[0], through[1]
    if not (0 < x1 < x2) or not (0 < y1 < y2):
        raise ValueError("readings must rise, left to right")
    if y2 >= y1 * x2 / float(x1):
        raise ValueError("(%s, %s) is not below the ray through (%s, %s): "
                         "no concave curve fits" % (x2, y2, x1, y1))

    def miss(tau):
        return y1 * (1 - math.exp(-x2 / tau)) / (1 - math.exp(-x1 / tau)) - y2

    lo, hi = x1 * 1e-3, x1 * 1e6
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if miss(mid) > 0:
            hi = mid
        else:
            lo = mid
    tau = (lo + hi) / 2.0
    top = y1 / (1 - math.exp(-x1 / tau))

    def f(x):
        return top * (1 - math.exp(-x / tau))

    for x3, y3 in through[2:]:
        if abs(f(x3) - y3) > max(1.0, abs(y3) * 0.005):
            raise ValueError("(%s, %s) is not on the curve the first two fix "
                             "(it gives %.1f there)" % (x3, y3, f(x3)))

    xs = sorted(set([round(xmax * i / float(n - 1), 4) for i in range(n)]
                    + [float(x) for x, _ in through] + [float(x) for x in extra]))
    return sample(f, xs), top, tau


def cycle(trough, period, lo, hi, xmax, trend=0.0, n=49, x0=0.0):
    """A stylised business cycle, and its own turning points.

    y = mid + trend*x - amp*cos(2*pi*(x - trough)/period), so the first trough
    is where you put it and peaks and troughs alternate every half period. The
    turning points come back read off the **samples**, not off the formula: the
    engine draws a spline through the samples, so a peak marked from the
    formula between two of them sits just off the line that is drawn, and with
    a trend the drawn maximum is not quite where the cosine's is anyway.

    Returns (pts, peaks, troughs), each turning point one of `pts`.
    """
    mid, amp = (lo + hi) / 2.0, (hi - lo) / 2.0

    def f(x):
        return mid + trend * x - amp * math.cos(2 * math.pi * (x - trough) / period)

    xs = [x0 + (xmax - x0) * i / float(n - 1) for i in range(n)]
    pts = sample(f, xs)
    peaks, troughs = [], []
    for i in range(1, len(pts) - 1):
        a, b, c = pts[i - 1][1], pts[i][1], pts[i + 1][1]
        if b > a and b >= c:
            peaks.append(pts[i])
        if b < a and b <= c:
            troughs.append(pts[i])
    return pts, peaks, troughs
