#!/usr/bin/env python3
"""Mechanical checks on a finished notes file (conversion prompt v6, step 8).

    python scripts/check_file.py examples/ECO2013-263-SupplyAndDemand.html

Groups, in order:

  head      house format -- <title> is the chapter name alone, the Red Hat
            Display link, sn25-v6.css and sn25-v6.js, nothing older
  engine    <!--SDG-ENGINE--> exactly once, or an engine already embedded whose
            bytes match engine/; and no <link>/<script src> to a hosted copy
  markup    no <u>, no <h3>, <strong> used for vocabulary terms only
  json      every <div class="sdg"> holds one parseable JSON config
  escape    no literal </script> inside a config
  schema    steps (>=2) or a caption or a static preset with scenarios; at/until
            point at steps that exist; no keys left at their defaults
  labels    step 5's x-position test -- for every label, where does each curve
            pass at that label's x? Plus label-on-label and point-on-point.
  arrows    every surplus/shortage walkthrough ends with two movement arrows
  caption   prose, not slide bullets: no "Before -/After -", no "Price up,
            quantity up", complete sentences
  source    no student-facing text names where the material came from
  images    <!-- IMAGE POSITION: ... --> comments preserved, no <img> left where
            a graph should be

Every line is PASS, WARN, FAIL or SKIP; exits non-zero on any FAIL.

It cannot check the one thing that matters most: whether a number is the number
the source gave. That needs the source and a person.
"""

import argparse
import json
import math
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_SRC = ROOT / "engine" / "sd-graph.css"
JS_SRC = ROOT / "engine" / "sd-graph.js"
PLACEHOLDER = "<!--SDG-ENGINE-->"

# Hard rule 4 / prompt v6 step 0T: student-facing text never names where the
# material came from. Two tiers, because some of these words have innocent uses.
# NOUNS match on their own, whatever article precedes them -- "a lecture
# recording" has to trip the same wire as "the recording". PHRASES are words
# that are only a giveaway in context: a "class" of goods and the "board" of a
# company are both ordinary economics.
#
# Naming a person is a different question from naming the source, and it is not
# a rule a script can settle: some professors are happy to be credited and
# others must never appear. So attributing content to whoever taught it is a
# FAIL here ("the professor said"), while a name itself is only ever a WARN --
# see check_names below and hard rule 4 in CLAUDE.md. "your professor" is left
# alone: it addresses the student rather than sourcing the material.
SOURCE_NOUNS = ["transcript", "lecture", "recording", "classroom"]
# "on the board" and not "the board": a company has one of those too, and the
# rule is about the classroom whiteboard. "the class" likewise skips "the class
# of goods", which is ordinary economics.
SOURCE_PHRASES = ["on the board", "at the board", "the slides",
                  "the handout", "the video", "the notes say", "the reading",
                  "he said", "she said", "they said in",
                  "the professor", "our professor", "the instructor",
                  "the lecturer"]
# "the class" and "in class" are ordinary English for a student -- a class
# average, sitting in class -- and only give the source away when something is
# attributed to what happened there.
SOURCE_GUARDED = [
    (r"the class\b(?!\s+(?:average|of\b))", "the class"),
    (r"(?:said|says|noted|explained|mentioned|covered|discussed|showed|drew|"
     r"went over)[^.]{0,40}\bin class\b", "in class"),
    (r"\bin class\b[^.]{0,40}(?:said|says|noted|explained|mentioned)", "in class"),
]

CSS_BLOCK = re.compile(r"<style>\s*\n(\.sdg \{.*?)\n</style>", re.S)
JS_BLOCK = re.compile(r"<script>\s*\n(/\* ===== sd-graph\.js.*?)\n</script>", re.S)
JSON_RE = re.compile(r'<script type="application/json">(.*?)</script>', re.S)


class Report:
    def __init__(self):
        self.fails = self.warns = 0

    def ok(self, n, m):
        print("PASS  %-8s %s" % (n, m))

    def warn(self, n, m):
        self.warns += 1
        print("WARN  %-8s %s" % (n, m))

    def fail(self, n, m):
        self.fails += 1
        print("FAIL  %-8s %s" % (n, m))

    def skip(self, n, m):
        print("SKIP  %-8s %s" % (n, m))


# ---------------------------------------------------------------- widgets ----

def blank_code(src):
    """Blank out <style> and non-JSON <script> bodies, keeping offsets.

    The engine's header comment documents the widget markup, so a raw scan for
    <div class="sdg"> otherwise finds one inside the embedded engine."""
    out = list(src)
    for m in re.finditer(r"<(script|style)\b([^>]*)>(.*?)</\1>", src, re.S | re.I):
        if "application/json" in m.group(2):
            continue
        for i in range(m.start(3), m.end(3)):
            if out[i] != "\n":
                out[i] = " "
    return "".join(out)


def widget_bodies(src):
    """Each <div class="sdg"> body, in document order (divs may nest an <svg>)."""
    out = []
    src = blank_code(src)
    for m in re.finditer(r'<div class="sdg"[^>]*>', src):
        i, depth = m.end(), 1
        while depth and i < len(src):
            o, c = src.find("<div", i), src.find("</div>", i)
            if c == -1:
                break
            if o != -1 and o < c:
                depth += 1
                i = o + 4
            else:
                depth -= 1
                i = c + 6
        out.append(src[m.end():i - 6])
    return out


def configs(src, r):
    out = []
    bodies = widget_bodies(src)
    for n, body in enumerate(bodies, 1):
        blocks = JSON_RE.findall(body)
        if not blocks:
            r.fail("json", "widget %d has no application/json block" % n)
            continue
        raw = blocks[0]
        if "</script>" in raw:
            r.fail("escape", "widget %d: literal </script> inside the config" % n)
        try:
            out.append((n, json.loads(raw), body))
        except ValueError as e:
            r.fail("json", "widget %d: %s" % (n, e))
    if bodies:
        r.ok("json", "%d of %d widget config(s) parse" % (len(out), len(bodies)))
    else:
        r.warn("json", 'no <div class="sdg"> widgets in this file')
    return out


def variants(cfg):
    """(label, merged config) for the base config or each scenario.

    The engine merges a scenario shallowly over the base, so a scenario that
    changes one curve replaces the whole curves array. This mirrors that."""
    sc = cfg.get("scenarios")
    if not sc:
        return [(None, cfg)]
    out = []
    for key, over in sc.items():
        merged = dict(cfg)
        merged.update(over)
        out.append((over.get("label", key), merged))
    return out


def panels(v):
    return v.get("panels") or [v]


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for x in node.values():
            walk(x, fn)
    elif isinstance(node, list):
        for x in node:
            walk(x, fn)


# ------------------------------------------------------------------- head ----

def check_head(src, r):
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    if not m or not m.group(1).strip():
        r.fail("head", "no <title>")
    else:
        t = m.group(1).strip()
        bad = re.search(r"\b(ECO\d{4}|\d{3}\b|spring|summer|fall|20\d\d)\b", t, re.I)
        if bad:
            r.fail("head", "<title> must be the chapter name alone; found %r in %r"
                   % (bad.group(0), t))
        else:
            r.ok("head", "<title> is %r" % t)

    for needle, what in [("Red+Hat+Display", "the Red Hat Display font link"),
                         ("sn25-v6.css", "sn25-v6.css"),
                         ("sn25-v6.js", "sn25-v6.js")]:
        (r.ok if needle in src else r.fail)("head", ("links %s" if needle in src else
                                                     "does not link %s") % what)
    old = re.findall(r"sn25-v[0-5]\.(?:css|js)", src)
    if old:
        r.fail("head", "references an older house asset: %s" % ", ".join(sorted(set(old))))


def check_engine(src, r):
    n = src.count(PLACEHOLDER)
    css_m, js_m = CSS_BLOCK.search(src), JS_BLOCK.search(src)

    if n == 1 and not (css_m or js_m):
        r.ok("engine", "%s placeholder present once, engine not yet inserted" % PLACEHOLDER)
    elif n:
        r.fail("engine", "%s appears %d time(s) alongside an embedded engine" % (PLACEHOLDER, n))
    elif css_m and js_m:
        for got, path, what in ((css_m.group(1), CSS_SRC, "sd-graph.css"),
                                (js_m.group(1), JS_SRC, "sd-graph.js")):
            want = path.read_text(encoding="utf-8").strip()
            if got.strip() == want:
                r.ok("engine", "embedded %s is byte-identical to engine/" % what)
            else:
                r.fail("engine", "embedded %s differs from engine/ -- re-run "
                                 "scripts/embed_engine.py" % what)
    else:
        r.fail("engine", "no %s placeholder and no embedded engine" % PLACEHOLDER)

    stray = re.findall(r'<link[^>]*sd-graph\.css[^>]*>', src, re.I)
    stray += re.findall(r'<script[^>]*src=["\'][^"\']*sd-graph\.js["\']', src, re.I)
    if stray:
        r.fail("engine", "%d reference(s) to a hosted engine copy remain" % len(stray))


def check_markup(src, r):
    body = src[src.find("<body"):] if "<body" in src else src
    if re.search(r"<u\b", body, re.I):
        r.fail("markup", "<u> is never used; the printed underline is <b>, or "
                         "<strong> when the word is a term")
    if re.search(r"<h3\b", body, re.I):
        r.fail("markup", "<h3> is not part of the house format; use <h2>")
    loose = [s for s in re.findall(r"<strong>(.*?)</strong>", body, re.S)
             if len(s.split()) > 6 or s.rstrip().endswith((".", ":"))]
    if loose:
        r.warn("markup", "%d <strong> swallows more than the term itself -- a "
                         "trailing marker or sentence belongs in <b> beside it, "
                         "not inside the glossary entry: %r"
               % (len(loose), loose[0][:50]))
    if not any(x for x in (loose,)) and "<strong>" in body:
        r.ok("markup", "<strong> used for short terms only")


# ----------------------------------------------------------------- schema ----

DEFAULTS = {"at": 0, "color": "ink", "guides": True, "curved": False,
            "thin": False, "dashed": False, "static": False, "grid": False}


def check_schema(cfgs, r):
    for n, cfg, _ in cfgs:
        has_steps = isinstance(cfg.get("steps"), list) and len(cfg["steps"]) >= 2
        static_preset = cfg.get("preset") and cfg.get("static") and cfg.get("scenarios")
        if not (has_steps or cfg.get("caption") or static_preset
                or any(v.get("caption") or (isinstance(v.get("steps"), list)
                                            and len(v["steps"]) >= 2)
                       for _, v in variants(cfg))):
            r.fail("schema", "widget %d has neither steps (>=2) nor a caption" % n)

        for label, v in variants(cfg):
            steps = v.get("steps") or []
            last = len(steps) - 1
            over = set()

            def scan(d):
                for k in ("at", "until"):
                    x = d.get(k)
                    if isinstance(x, int) and steps and x > last + (1 if k == "until" else 0):
                        over.add("%s=%d" % (k, x))
            walk({k: x for k, x in v.items() if k != "scenarios"}, scan)
            if over:
                where = "widget %d%s" % (n, " (%s)" % label if label else "")
                r.fail("schema", "%s: %s but there are only %d step(s)"
                       % (where, ", ".join(sorted(over)), len(steps)))

        defaulted = set()

        def scan_def(d):
            for k, val in DEFAULTS.items():
                if k in d and d[k] == val:
                    defaulted.add(k)
        walk(cfg, scan_def)
        if defaulted:
            r.warn("schema", "widget %d leaves key(s) at their default value: %s"
                   % (n, ", ".join(sorted(defaulted))))
    if cfgs:
        r.ok("schema", "%d config(s) checked against the schema" % len(cfgs))


# ----------------------------------------------------------------- labels ----
# Replicates the engine's geometry so a label can be tested against the curves
# exactly where it will be drawn.

W = 372.0


def geom(pn, ax):
    left = 62.0 if ax.get("cents") else (54.0 if ax.get("yticks") else 40.0)
    # A vbrace with left:true widens the engine's left margin. Miss this and
    # every coordinate below is off by 44px.
    if any(b.get("left") for b in (pn.get("vbraces") or [])):
        left += 44.0
    ox, oy = left, 205.0
    pw, ph = W - left - 36.0, 178.0
    xmax = float(ax.get("xmax") or 1)
    ymax = float(ax.get("ymax") or 1)
    return (lambda q: ox + (q / xmax) * pw,
            lambda p: oy - (p / ymax) * ph, ox, oy)


def fmt_p(v, ax):
    if not ax.get("money"):
        return str(v)
    if ax.get("cents"):
        return "$%.2f" % v
    return "$" + (str(int(v)) if float(v).is_integer() else "%.2f" % v)


def fmt_q(v, ax):
    if ax.get("k") and v >= 1000:
        return "%gk" % (v / 1000.0)
    return "{:,}".format(v)


def box(x, y, text, size, anchor="start"):
    w = 0.58 * size * max(1, len(str(text)))
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    return (x, y - size * 0.78, x + w, y + size * 0.22)


def inflate(bx, by):
    return (bx[0] - by, bx[1] - by, bx[2] + by, bx[3] + by)


def coexist(a, b):
    """Can these two ever be on screen at the same step?"""
    a0, a1 = a
    b0, b1 = b
    lo = max(a0 or 0, b0 or 0)
    hi = min(a1 if a1 is not None else 10 ** 6, b1 if b1 is not None else 10 ** 6)
    return lo < hi


def overlaps(a, b, inset=1.0):
    return not (a[2] - inset <= b[0] + inset or b[2] - inset <= a[0] + inset
                or a[3] - inset <= b[1] + inset or b[3] - inset <= a[1] + inset)


def poly_hits(bx, px, samples=160):
    """Does the polyline through these pixel points pass inside the box?"""
    for i in range(len(px) - 1):
        (x1, y1), (x2, y2) = px[i], px[i + 1]
        for s in range(samples + 1):
            t = s / samples
            x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
            if bx[0] < x < bx[2] and bx[1] < y < bx[3]:
                return True
    return False


def curve_hits(bx, pts, X, Y):
    return poly_hits(bx, [(X(q), Y(p)) for q, p in pts])


def dot_hits(bx, cx, cy, r):
    """Does a dot of radius r overlap the box?"""
    nx = min(max(cx, bx[0]), bx[2])
    ny = min(max(cy, bx[1]), bx[3])
    return (nx - cx) ** 2 + (ny - cy) ** 2 < r * r


def q_at(pts, p):
    """Quantity on a polyline at price p -- the engine's qAt, for shift arrows."""
    for i in range(len(pts) - 1):
        a, b = pts[i], pts[i + 1]
        if (p - a[1]) * (p - b[1]) <= 0 and a[1] != b[1]:
            return a[0] + (p - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
    a, b = pts[0], pts[-1]
    if a[1] == b[1]:
        return a[0]
    return a[0] + (p - a[1]) * (b[0] - a[0]) / (b[1] - a[1])


def arrow_segments(pn, X, Y):
    """Every arrow the engine will draw, as pixel endpoints with a description.

    Rule 5 forbids a label touching an arrow, not just a curve, so these have to
    be in the collision test too. Shift arrows are reconstructed the way the
    engine places them (at price arrowP, inset 8px at each end); `moves` are
    displaced perpendicular by `offset`, which is what puts them beside the
    curve rather than on it."""
    out = []
    byid = {c.get("id"): c for c in (pn.get("curves") or []) if c.get("id")}
    for c in pn.get("curves") or []:
        src = byid.get(c.get("from"))
        if not src or c.get("shiftArrow") is False:
            continue
        pts, spts = c.get("pts") or [], src.get("pts") or []
        if len(pts) < 2 or len(spts) < 2:
            continue
        ap = c["arrowP"] if c.get("arrowP") is not None else (pts[0][1] + pts[-1][1]) / 2.0
        q0, q1 = q_at(spts, ap), q_at(pts, ap)
        sgn = 1 if q1 > q0 else (-1 if q1 < q0 else 0)
        out.append((((X(q0) + sgn * 8, Y(ap)), (X(q1) - sgn * 8, Y(ap))),
                    "the %s shift arrow" % (c.get("label") or c.get("id"))))
    for m in pn.get("moves") or []:
        if not (isinstance(m.get("from"), list) and isinstance(m.get("to"), list)):
            continue
        x1, y1 = X(m["from"][0]), Y(m["from"][1])
        x2, y2 = X(m["to"][0]), Y(m["to"][1])
        off = m.get("offset", 14)
        ln = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / ln * off, (x2 - x1) / ln * off
        out.append((((x1 + nx, y1 + ny), (x2 + nx, y2 + ny)), "a movement arrow"))
    return out


def label_of(desc):
    """The quoted label inside a description, so a brace's own label can be told
    apart from someone else's."""
    m = re.search(r"'([^']*)'", desc)
    return m.group(1) if m else None


def same_spot(a, b, tol=1.5):
    return all(abs(a[i] - b[i]) <= tol for i in range(4))


def exempt(desc_a, desc_b, box_a=None, box_b=None):
    """Pairs that are adjacent by design, not by accident."""
    # A brace's label belongs beside its own bracket.
    if ("brace label" in desc_a and "brace" in desc_b) or \
       ("brace label" in desc_b and "brace" in desc_a):
        if label_of(desc_a) and label_of(desc_a) == label_of(desc_b):
            return True
    # The same value printed twice lands in the same place and reads as one
    # label -- two points at the same price both print it.
    if desc_a == desc_b and box_a and box_b and same_spot(box_a, box_b):
        return True
    # An x tick and a y tick only ever meet in the origin corner, where both
    # belong.
    if ("tick on Q" in desc_a and "tick on P" in desc_b) or \
       ("tick on P" in desc_a and "tick on Q" in desc_b):
        return True
    return False


def guide_segments(pn, X, Y, ox, oy):
    """Every dashed guide the engine draws, as pixel polylines.

    Rule 5 lists curves, points, arrows and labels -- not guides. But a label
    pressed against the dashed line dropping from its own point reads as
    crowded, so these are tested too, and only ever warn."""
    out = []
    pw = W - ox - 36.0
    for p in pn.get("points") or []:
        if p.get("guides") is False:
            continue
        out.append(([(ox, Y(p["p"])), (X(p["q"]), Y(p["p"])), (X(p["q"]), oy)],
                    "the guides from (%s, %s)" % (p["q"], p["p"]),
                    (p.get("at", 0), p.get("until"))))
    for h in pn.get("hlines") or []:
        out.append(([(ox, Y(h["p"])), (ox + pw + 8, Y(h["p"]))],
                    "the %s price line" % h.get("label", h["p"]),
                    (h.get("at", 0), h.get("until"))))
    for b in pn.get("braces") or []:
        win = (b.get("at", 0), b.get("until"))
        if not b.get("below"):
            for q in (b.get("q1"), b.get("q2")):
                if q is None:
                    continue
                out.append(([(X(q), Y(b["p"])), (X(q), oy)],
                            "a guide under the %r brace" % b.get("label"), win))
        # the bracket itself
        y = (oy + 22) if b.get("below") else (Y(b["p"]) - 8)
        d = 1 if b.get("below") else -1
        x1, x2 = X(min(b["q1"], b["q2"])), X(max(b["q1"], b["q2"]))
        m = (x1 + x2) / 2.0
        out.append(([(x1, y), (x1 + 7, y + d * 7), (m - 7, y + d * 7), (m, y + d * 14),
                     (m + 7, y + d * 7), (x2 - 7, y + d * 7), (x2, y)],
                    "the %r brace" % b.get("label"), win))
    for b in pn.get("vbraces") or []:
        win = (b.get("at", 0), b.get("until"))
        y1, y2 = Y(max(b["p1"], b["p2"])), Y(min(b["p1"], b["p2"]))
        x = (ox - 32) if b.get("left") else X(b["q"])
        d = -1 if (b.get("left") or b.get("side") == "left") else 1
        m = (y1 + y2) / 2.0
        out.append(([(x, y1), (x + d * 7, y1 + 7), (x + d * 7, m - 7), (x + d * 14, m),
                     (x + d * 7, m + 7), (x + d * 7, y2 - 7), (x, y2)],
                    "the %r brace" % b.get("label"), win))
    return out


def check_labels(cfgs, r):
    checked = skipped = 0
    for n, cfg, _ in cfgs:
        if cfg.get("preset"):
            skipped += 1
            continue
        for label, v in variants(cfg):
            if v.get("preset"):
                skipped += 1
                continue
            for pi, pn in enumerate(panels(v)):
                ax = pn.get("axes")
                if not ax:
                    continue
                X, Y, ox, oy = geom(pn, ax)
                where = "widget %d%s%s" % (
                    n, " (%s)" % label if label else "",
                    " panel %d" % (pi + 1) if len(panels(v)) > 1 else "")
                boxes = []
                # The axis titles are drawn text too. They were the last
                # category missing from this test, after arrows, ticks and
                # guides -- a curve label parked in the bottom-right corner
                # lands on the Q title, which nothing here used to notice.
                boxes.append((box(W - 2.0, oy + 16, ax.get("x") or "Q", 14, "end"),
                              "the %r axis title" % (ax.get("x") or "Q"), (0, None)))
                boxes.append((box(ox - 2.0, 11.0, ax.get("y") or "P", 14),
                              "the %r axis title" % (ax.get("y") or "P"), (0, None)))
                xt = [t for t in (ax.get("xticks") or [])]
                yt = [t for t in (ax.get("yticks") or [])]
                hl = [h.get("p") for h in (pn.get("hlines") or [])]

                # Axis ticks are always on screen, so anything landing near one
                # collides with it. These were missing from the test, which is
                # why "85" beside the "80" tick went unreported.
                for t in xt:
                    boxes.append((box(X(t), oy + 15, fmt_q(t, ax), 10.5, "middle"),
                                  "the %s tick on Q" % fmt_q(t, ax), (0, None)))
                for t in yt:
                    boxes.append((box(ox - 6, Y(t) + 4, fmt_p(t, ax), 10.5, "end"),
                                  "the %s tick on P" % fmt_p(t, ax), (0, None)))

                for c in pn.get("curves") or []:
                    pts = c.get("pts") or []
                    text = c.get("label") if c.get("label") is not None else c.get("id")
                    if len(pts) < 2 or not text:
                        continue
                    last = pts[-1]
                    up = last[1] > pts[0][1]
                    lp = pts[0] if c.get("lstart") else last
                    bx = box(X(lp[0]) + c.get("ldx", 6),
                             Y(lp[1]) + c.get("ldy", 2 if up else 6),
                             text, 13)
                    boxes.append((bx, "curve label %r" % text,
                                  (c.get("at", 0), c.get("until"))))

                for p in pn.get("points") or []:
                    win = (p.get("at", 0), p.get("until"))
                    if p.get("label"):
                        bx = box(X(p["q"]) + (p.get("dx") if p.get("dx") is not None else 9),
                                 Y(p["p"]) + (p.get("dy") if p.get("dy") is not None else -9),
                                 p["label"], 12)
                        boxes.append((bx, "point label %r" % p["label"], win))
                    # The engine prints a point's own price and quantity on the
                    # axes unless they are already ticks (or pl/ql override
                    # them), so those labels exist whether the author wrote them
                    # or not, and have to be tested.
                    pl = p.get("pl") or (fmt_p(p["p"], ax)
                                         if p.get("showP") is not False
                                         and p["p"] not in yt and p["p"] not in hl else None)
                    ql = p.get("ql") or (fmt_q(p["q"], ax)
                                         if p.get("showQ") is not False
                                         and p["q"] not in xt else None)
                    if pl:
                        boxes.append((box(ox - 6, Y(p["p"]) + 4, pl, 10.5, "end"),
                                      "axis label %r" % pl, win))
                    if ql:
                        boxes.append((box(X(p["q"]), oy + 15, ql, 10.5, "middle"),
                                      "axis label %r" % ql, win))

                for b in pn.get("braces") or []:
                    if not b.get("label"):
                        continue
                    y = (oy + 22) if b.get("below") else (Y(b["p"]) - 8)
                    d = 1 if b.get("below") else -1
                    m = (X(min(b["q1"], b["q2"])) + X(max(b["q1"], b["q2"]))) / 2
                    boxes.append((box(m, y + d * 14 + (12 if b.get("below") else -4),
                                      b["label"], 12, "middle"),
                                  "brace label %r" % b["label"],
                                  (b.get("at", 0), b.get("until"))))

                for b in pn.get("vbraces") or []:
                    if not b.get("label"):
                        continue
                    win = (b.get("at", 0), b.get("until"))
                    y1, y2 = Y(max(b["p1"], b["p2"])), Y(min(b["p1"], b["p2"]))
                    x = (ox - 32) if b.get("left") else X(b["q"])
                    d = -1 if (b.get("left") or b.get("side") == "left") else 1
                    m = (y1 + y2) / 2.0
                    if b.get("left"):
                        # rotated a quarter turn, so the box is tall and narrow
                        lx = x + d * 22
                        h = 0.58 * 12 * len(str(b["label"]))
                        bx = (lx - 7, m - h / 2, lx + 7, m + h / 2)
                    else:
                        bx = box(x + d * 20, m + 4, b["label"], 12,
                                 "start" if d > 0 else "end")
                    boxes.append((bx, "upright brace label %r" % b["label"], win))

                checked += len(boxes)

                arrows = arrow_segments(pn, X, Y)
                guides = guide_segments(pn, X, Y, ox, oy)

                for bx, what, win in boxes:
                    for gpx, gdesc, gwin in guides:
                        if not coexist(win, gwin) or exempt(what, gdesc):
                            continue
                        if poly_hits(inflate(bx, 3.0), gpx):
                            r.warn("labels", "%s: %s is close to %s"
                                   % (where, what, gdesc))
                    for c in pn.get("curves") or []:
                        pts = c.get("pts") or []
                        if len(pts) < 2:
                            continue
                        cid = c.get("label") or c.get("id")
                        if what.endswith("%r" % cid) and "curve label" in what:
                            continue  # a curve's own label sits at its end
                        if curve_hits(bx, pts, X, Y):
                            r.fail("labels", "%s: %s sits on curve %s" % (where, what, cid))
                    for seg, desc in arrows:
                        if poly_hits(bx, list(seg)):
                            r.fail("labels", "%s: %s sits on %s" % (where, what, desc))
                    for pt in pn.get("points") or []:
                        cx, cy = X(pt["q"]), Y(pt["p"])
                        rad = 6.0 if pt.get("marker") else 4.2
                        own = pt.get("label") and what == "point label %r" % pt["label"]
                        if not own and dot_hits(bx, cx, cy, rad):
                            r.fail("labels", "%s: %s sits on the point at (%s, %s)"
                                   % (where, what, pt["q"], pt["p"]))

                for i in range(len(boxes)):
                    for j in range(i + 1, len(boxes)):
                        if not coexist(boxes[i][2], boxes[j][2]):
                            continue
                        if exempt(boxes[i][1], boxes[j][1], boxes[i][0], boxes[j][0]):
                            continue
                        if overlaps(boxes[i][0], boxes[j][0]):
                            r.fail("labels", "%s: %s overlaps %s"
                                   % (where, boxes[i][1], boxes[j][1]))
                        elif overlaps(boxes[i][0], boxes[j][0], inset=-3.0):
                            # Not touching, but under ~6px apart reads as one
                            # clump rather than two values.
                            r.warn("labels", "%s: %s is crowded against %s"
                                   % (where, boxes[i][1], boxes[j][1]))

                seen = {}
                for p in pn.get("points") or []:
                    key = (round(float(p["q"]), 3), round(float(p["p"]), 3),
                           p.get("at", 0), p.get("until"))
                    if key in seen:
                        r.fail("labels", "%s: two points share position (%s, %s) "
                                         "on the same step" % (where, p["q"], p["p"]))
                    seen[key] = True

    if skipped:
        r.skip("labels", "%d preset config(s): the engine computes their geometry" % skipped)
    if checked:
        r.ok("labels", "%d label(s) tested against every curve, arrow and point"
              % checked)


def check_tick_emphasis(cfgs, r):
    """Point values should all be ticks, or none of them.

    The engine prints a point's own value in bold only when that value is not
    already a tick, so within one graph some point values can come out bold and
    others plain depending purely on which ticks the author listed. Prompt v6
    step 5 settles it -- "ticks are the values the prose uses, nothing extra" --
    which makes every point value a tick and the emphasis uniform. A widget that
    mixes the two reads as if the bold ones matter more."""
    mixed = 0
    for n, cfg, _ in cfgs:
        for label, v in variants(cfg):
            if v.get("preset"):
                continue
            for pi, pn in enumerate(panels(v)):
                ax = pn.get("axes")
                if not ax:
                    continue
                for key, tkey, skey, axis in (("q", "xticks", "showQ", "Q"),
                                              ("p", "yticks", "showP", "P")):
                    ticks = ax.get(tkey) or []
                    if not ticks:
                        continue
                    on, off = [], []
                    for pt in pn.get("points") or []:
                        if pt.get(skey) is False or pt.get("pl" if axis == "P" else "ql"):
                            continue
                        val = pt.get(key)
                        if val is None:
                            continue
                        (on if val in ticks else off).append(val)
                    if on and off:
                        mixed += 1
                        where = "widget %d%s%s" % (
                            n, " (%s)" % label if label else "",
                            " panel %d" % (pi + 1) if len(panels(v)) > 1 else "")
                        r.warn("ticks", "%s: on %s, %s %s ticked (plain) while %s %s not "
                               "(bold). Tick the values the prose uses, or none of them."
                               % (where, axis, sorted(set(on)),
                                  "is" if len(set(on)) == 1 else "are",
                                  sorted(set(off)),
                                  "is" if len(set(off)) == 1 else "are"))
    if cfgs and not mixed:
        r.ok("ticks", "point values are emphasised consistently")


def check_arrows(cfgs, r):
    n_checked = 0
    for n, cfg, _ in cfgs:
        for label, v in variants(cfg):
            if v.get("preset"):
                continue
            # The surplus/shortage pattern is the one with a disequilibrium
            # price line. An equilibrium-shift widget also carries a brace
            # labelled Surplus/Shortage -- the gap at the old price -- but it
            # is the pattern v6 step 4 templates without moves, so keying on
            # the brace label alone flags those wrongly.
            hlines = [h for pn in panels(v) for h in (pn.get("hlines") or [])]
            if not hlines or not v.get("steps"):
                continue
            n_checked += 1
            last = len(v["steps"]) - 1
            moves = []
            for pn in panels(v):
                moves += [m for m in (pn.get("moves") or [])
                          if m.get("at", 0) <= last and (m.get("until") is None
                                                         or m["until"] > last)]
            if len(moves) < 2:
                r.fail("arrows", "widget %d%s: a surplus/shortage walkthrough must end "
                                 "with two movement arrows, found %d"
                       % (n, " (%s)" % label if label else "", len(moves)))
    if n_checked:
        r.ok("arrows", "%d surplus/shortage walkthrough(s) end with two movement "
                       "arrows" % n_checked)


def check_captions(cfgs, r):
    bad = 0
    for n, cfg, _ in cfgs:
        texts = []
        walk(cfg, lambda d: texts.extend(
            [d["caption"]] if isinstance(d.get("caption"), str) else []))
        for _, v in variants(cfg):
            texts += [s for s in (v.get("steps") or []) if isinstance(s, str)]
        for c in texts:
            s = c.strip()
            if re.match(r"^(before|after)\s*[-–—:]", s, re.I):
                r.fail("caption", "widget %d: 'Before -/After -' prefix: %r" % (n, s[:60]))
                bad += 1
            elif re.search(r"\b(price|quantity)\s+(up|down)\b", s, re.I):
                r.fail("caption", "widget %d: shorthand instead of words: %r" % (n, s[-40:]))
                bad += 1
            elif not re.search(r"[.!?]$", s):
                r.warn("caption", "widget %d: not a complete sentence: %r" % (n, s[:60]))
    if cfgs and not bad:
        r.ok("caption", "captions are prose")


def visible_text(src, cfgs):
    parts = []
    for _, cfg, _ in cfgs:
        walk(cfg, lambda d: parts.extend(
            str(d[k]) for k in ("caption", "label", "title", "lede", "heading")
            if isinstance(d.get(k), str)))
        for _, v in variants(cfg):
            parts += [s for s in (v.get("steps") or []) if isinstance(s, str)]
    prose = re.sub(r"<(script|style)\b.*?</\1>", " ", src, flags=re.S | re.I)
    prose = re.sub(r"<!--.*?-->", " ", prose, flags=re.S)
    parts.append(re.sub(r"<[^>]+>", " ", prose))
    return parts


def check_source(src, cfgs, r):
    hits = {}
    for t in visible_text(src, cfgs):
        probes = ([(r"\b" + re.escape(w) + r"\w*\b", w) for w in SOURCE_NOUNS]
                  + [(r"\b" + re.escape(w) + r"\b", w) for w in SOURCE_PHRASES]
                  + [(r"\b" + pat, w) for pat, w in SOURCE_GUARDED])
        for pat, w in probes:
            m = re.search(pat, t, re.I)
            if m:
                i = max(0, m.start() - 40)
                hits.setdefault(w, t[i:m.end() + 40].strip())
    if hits:
        for w in sorted(hits):
            r.fail("source", "student-facing text names its source (%r): ...%s..."
                   % (w, " ".join(hits[w].split())))
    else:
        r.ok("source", "no student-facing text names its source")


NAME_RE = re.compile(r"\b(?:Professor|Prof\.|Dr\.|Mr\.|Mrs\.|Ms\.)\s+[A-Z][\w'\u2019-]+")


def check_names(src, cfgs, r):
    """Report people named in student-facing text. Never fails.

    Whether a given professor may be named is Ian's call, not a rule a script
    can hold, so this only ever raises a hand. It also only catches a name that
    carries a title -- a bare surname is indistinguishable from any other
    capitalised word, so a person named without one will pass silently."""
    found = {}
    for t in visible_text(src, cfgs):
        for m in NAME_RE.finditer(t):
            i = max(0, m.start() - 40)
            found.setdefault(m.group(0), " ".join(t[i:m.end() + 40].split()))
    if not found:
        r.ok("names", "no person is named with a title in student-facing text")
        return
    for who, ctx in sorted(found.items()):
        r.warn("names", "%r is named -- check whether this one may be: ...%s..."
               % (who, ctx))


def check_images(src, r):
    marks = re.findall(r"<!--\s*IMAGE POSITION:", src)
    if marks:
        r.ok("images", "%d IMAGE POSITION comment(s) preserved" % len(marks))
    else:
        r.warn("images", "no IMAGE POSITION comments")
    imgs = re.findall(r"<img\b[^>]*>", src, re.I)
    graphy = [i for i in imgs if re.search(
        r"curve|graph|shift|equilibrium|surplus|shortage|supply|demand|market",
        i, re.I)]
    if graphy:
        r.fail("images", "%d <img> still looks like a graph: %s"
               % (len(graphy), graphy[0][:80]))
    elif imgs:
        r.ok("images", "%d <img> remain, none of them graphs" % len(imgs))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    args = ap.parse_args()
    path = pathlib.Path(args.file)
    if not path.exists():
        sys.exit("no such file: %s" % path)
    src = path.read_text(encoding="utf-8")
    r = Report()

    print("checking %s\n" % path)
    check_head(src, r)
    check_engine(src, r)
    check_markup(src, r)
    cfgs = configs(src, r)
    check_schema(cfgs, r)
    check_labels(cfgs, r)
    check_tick_emphasis(cfgs, r)
    check_arrows(cfgs, r)
    check_captions(cfgs, r)
    check_source(src, cfgs, r)
    check_names(src, cfgs, r)
    check_images(src, r)
    r.skip("numbers", "whether each number is the source's number needs the source")

    print("\n%d FAIL, %d WARN" % (r.fails, r.warns))
    return 1 if r.fails else 0


if __name__ == "__main__":
    sys.exit(main())
