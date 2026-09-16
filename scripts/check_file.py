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

SOURCE_WORDS = [
    "the transcript", "the lecture", "the recording", "the board", "the slides",
    "the class", "the classroom", "classroom", "the video", "the professor",
    "the instructor", "in class",
    "the notes say", "the handout", "he said", "she said", "they said in",
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


def geom(v, ax):
    left = 62.0 if ax.get("cents") else (54.0 if ax.get("yticks") else 40.0)
    ox, oy = left, 205.0
    pw, ph = W - left - 36.0, 178.0
    xmax = float(ax.get("xmax") or 1)
    ymax = float(ax.get("ymax") or 1)
    return (lambda q: ox + (q / xmax) * pw,
            lambda p: oy - (p / ymax) * ph, ox, oy)


def box(x, y, text, size, anchor="start"):
    w = 0.58 * size * max(1, len(str(text)))
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    return (x, y - size * 0.78, x + w, y + size * 0.22)


def overlaps(a, b, inset=1.0):
    return not (a[2] - inset <= b[0] + inset or b[2] - inset <= a[0] + inset
                or a[3] - inset <= b[1] + inset or b[3] - inset <= a[1] + inset)


def curve_hits(bx, pts, X, Y, samples=160):
    """Does the polyline through pts pass inside the box?"""
    px = [(X(q), Y(p)) for q, p in pts]
    for i in range(len(px) - 1):
        (x1, y1), (x2, y2) = px[i], px[i + 1]
        for s in range(samples + 1):
            t = s / samples
            x, y = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
            if bx[0] < x < bx[2] and bx[1] < y < bx[3]:
                return True
    return False


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
                X, Y, ox, oy = geom(v, ax)
                where = "widget %d%s%s" % (
                    n, " (%s)" % label if label else "",
                    " panel %d" % (pi + 1) if len(panels(v)) > 1 else "")
                boxes = []

                for c in pn.get("curves") or []:
                    pts = c.get("pts") or []
                    if len(pts) < 2:
                        continue
                    last = pts[-1]
                    up = last[1] > pts[0][1]
                    lp = pts[0] if c.get("lstart") else last
                    bx = box(X(lp[0]) + c.get("ldx", 6),
                             Y(lp[1]) + c.get("ldy", 2 if up else 6),
                             c.get("label") or c.get("id") or "", 13)
                    boxes.append((bx, "curve label %r" % (c.get("label") or c.get("id"))))

                for p in pn.get("points") or []:
                    if p.get("label"):
                        bx = box(X(p["q"]) + (p.get("dx") if p.get("dx") is not None else 9),
                                 Y(p["p"]) + (p.get("dy") if p.get("dy") is not None else -9),
                                 p["label"], 12)
                        boxes.append((bx, "point label %r" % p["label"]))
                    if p.get("pl"):
                        boxes.append((box(ox - 6, Y(p["p"]) + 4, p["pl"], 10.5, "end"),
                                      "axis label %r" % p["pl"]))
                    if p.get("ql"):
                        boxes.append((box(X(p["q"]), oy + 15, p["ql"], 10.5, "middle"),
                                      "axis label %r" % p["ql"]))

                for b in pn.get("braces") or []:
                    if not b.get("label"):
                        continue
                    y = (oy + 22) if b.get("below") else (Y(b["p"]) - 8)
                    d = 1 if b.get("below") else -1
                    m = (X(min(b["q1"], b["q2"])) + X(max(b["q1"], b["q2"]))) / 2
                    boxes.append((box(m, y + d * 14 + (12 if b.get("below") else -4),
                                      b["label"], 12, "middle"),
                                  "brace label %r" % b["label"]))

                checked += len(boxes)

                for bx, what in boxes:
                    for c in pn.get("curves") or []:
                        pts = c.get("pts") or []
                        if len(pts) < 2:
                            continue
                        cid = c.get("label") or c.get("id")
                        if what.endswith("%r" % cid) and "curve label" in what:
                            continue  # a curve's own label sits at its end
                        if curve_hits(bx, pts, X, Y):
                            r.fail("labels", "%s: %s sits on curve %s" % (where, what, cid))

                for i in range(len(boxes)):
                    for j in range(i + 1, len(boxes)):
                        if overlaps(boxes[i][0], boxes[j][0]):
                            r.fail("labels", "%s: %s overlaps %s"
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
        r.ok("labels", "%d label(s) tested against every curve" % checked)


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
        for w in SOURCE_WORDS:
            m = re.search(r"\b" + re.escape(w) + r"\b", t, re.I)
            if m:
                i = max(0, m.start() - 40)
                hits.setdefault(w, t[i:m.end() + 40].strip())
    if hits:
        for w in sorted(hits):
            r.fail("source", "student-facing text names its source (%r): ...%s..."
                   % (w, " ".join(hits[w].split())))
    else:
        r.ok("source", "no student-facing text names its source")


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
    check_arrows(cfgs, r)
    check_captions(cfgs, r)
    check_source(src, cfgs, r)
    check_images(src, r)
    r.skip("numbers", "whether each number is the source's number needs the source")

    print("\n%d FAIL, %d WARN" % (r.fails, r.warns))
    return 1 if r.fails else 0


if __name__ == "__main__":
    sys.exit(main())
