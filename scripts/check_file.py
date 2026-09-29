#!/usr/bin/env python3
"""Mechanical checks on a finished notes file (conversion prompt v6, step 8).

    python scripts/check_file.py examples/ECO2013-263-SupplyAndDemand.html

Groups, in order:

  steps     every step changes the drawing, not just the caption
  steady    a curve shared between scenarios keeps its label in one place
  head      house format -- a <title> exists, the Red Hat Display link,
            sn25-v6.css, and a current house script
  engine    <!--SDG-ENGINE--> exactly once, or an engine already embedded whose
            bytes match engine/; and no <link>/<script src> to a hosted copy
  markup    no <u>, no <h3>, <strong> used for vocabulary terms only
  toc       the house table of contents, and whether its links reach the
            headings -- unless studyguide/sn25-v2.js builds it in the browser
  json      every <div class="sdg"> holds one parseable JSON config
  escape    no literal </script> inside a config
  schema    steps (>=2) or a caption or a static preset with scenarios; at/until
            point at steps that exist; no keys left at their defaults
  labels    step 5's x-position test -- for every label, where does each curve
            pass at that label's x? Plus label-on-label and point-on-point.
  arrows    every surplus/shortage walkthrough ends with two movement arrows
  controls  one dashed guide per quantity, each ending at a number
  calcs     working is shown only where the chapter does not print it as prose
  prose     a caption says something the paragraph above it does not
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



# --------------------------------------------------------------- steady ----


def check_steady_labels(cfgs, r):
    """A curve that does not move between scenarios keeps its label still.

    Ian's rule: "make sure the D1 is in the same space ... it should be
    consistent." The demand-for-chicken widget drew the same D1 in both
    scenarios but gave its label an offset in one and the engine default in the
    other, so D1 jumped across the plot when you pressed the other button while
    the curve underneath it did not move.

    Nothing else notices: each scenario is checked on its own and both were
    fine, because the defect is the difference between them.
    """
    checked = flagged = 0
    for n, cfg, _ in cfgs:
        if cfg.get("preset"):
            continue
        scen = cfg.get("scenarios") or {}
        if len(scen) < 2:
            continue
        seen = {}
        for key, v in scen.items():
            if v.get("preset"):
                continue
            for c in v.get("curves") or []:
                cid = c.get("id")
                if cid is None:
                    continue
                place = (c.get("ldx"), c.get("ldy"), c.get("lstart"),
                         c.get("label"))
                seen.setdefault(cid, []).append((json.dumps(c.get("pts")), place, key))
        for cid, rows in seen.items():
            if len(rows) < 2:
                continue
            checked += 1
            if len({p for p, _, _ in rows}) == 1 and len({q for _, q, _ in rows}) > 1:
                flagged += 1
                r.fail("steady", "widget %d: curve %s is drawn identically in "
                                 "%s but its label is placed differently, so it "
                                 "jumps when the scenario changes"
                       % (n, cid, " and ".join(sorted(k for _, _, k in rows))))
    if checked and not flagged:
        r.ok("steady", "%d curve(s) shared between scenarios keep their labels "
                       "still" % checked)


# ------------------------------------------------------------------ steps ----

# Everything a step can reveal or retire. `table` is not here: its per-row
# arrows follow the curves that carry them, so a step that changes nothing else
# changes nothing there either.
STEPPABLE = ("curves", "areas", "points", "hlines", "braces", "vbraces", "moves")


def check_steps(cfgs, r):
    """Every step must change the drawing, not just the caption.

    Ian's rule, twice over: "steps should only exist when the graph changes"
    and "step 1 and 2 just change text". A caption that advances while the
    picture holds still reads as a broken button -- the student presses Next,
    watches nothing happen, and stops trusting the control.

    Off-by-one is the usual cause rather than carelessness. `at` is a step
    index and index 0 is the opening state, so a walkthrough written as
    "curves, then CS, then PS" needs at:1 and at:2; writing at:2 and at:3
    leaves step 2 showing exactly what step 1 showed.
    """
    checked = flagged = 0
    for n, cfg, _ in cfgs:
        if cfg.get("preset"):
            continue
        for label, v in variants(cfg):
            # A preset's curves, braces and points are built inside the engine,
            # so the raw config lists none of them and every step would look
            # identical here. Skipping them is the same trade check_labels
            # makes, for the same reason.
            if v.get("preset"):
                continue
            steps = v.get("steps") or []
            if len(steps) < 2:
                continue
            where = "widget %d%s" % (n, " (%s)" % label if label else "")
            checked += 1
            # One signature per step: which elements are on screen, across
            # every panel, identified by position in their own list.
            sigs = []
            for i in range(len(steps)):
                on = []
                for pi, pn in enumerate(panels(v)):
                    for key in STEPPABLE:
                        for ei, e in enumerate(pn.get(key) or []):
                            if not isinstance(e, dict):
                                continue
                            at = e.get("at", 0)
                            un = e.get("until")
                            if at <= i and (un is None or i < un):
                                on.append((pi, key, ei))
                sigs.append(tuple(sorted(on)))
            for i in range(1, len(sigs)):
                if sigs[i] == sigs[i - 1]:
                    flagged += 1
                    r.fail("steps", "%s: step %d changes nothing on the drawing "
                                    "that step %d did not already show"
                                    % (where, i + 1, i))
    if checked and not flagged:
        r.ok("steps", "every step of %d walkthrough(s) changes the drawing" % checked)


# ------------------------------------------------------------------- head ----

def check_head(src, r):
    # The title is not this script's business. Prompt v6 step 0 asked for the
    # chapter name alone, and this used to fail anything carrying a course code,
    # a term or a year -- but Ian's titles come from his boss, so the rule was
    # policing someone else's decision. A title has to exist; what it says is
    # not a defect. (2026-09-23)
    m = re.search(r"<title>(.*?)</title>", src, re.S)
    if not m or not m.group(1).strip():
        r.fail("head", "no <title>")
    else:
        r.ok("head", "<title> is %r" % m.group(1).strip())

    for needle, what in [("Red+Hat+Display", "the Red Hat Display font link"),
                         ("sn25-v6.css", "sn25-v6.css")]:
        (r.ok if needle in src else r.fail)("head", ("links %s" if needle in src else
                                                     "does not link %s") % what)

    # The house script lives under one of two paths, and they version
    # separately. This used to demand content/sn25-v6.js and fail anything
    # matching sn25-v[0-5], which failed studyguide/sn25-v2.js twice over --
    # once for being absent, once for looking old. It is neither: it is the
    # current study-guide script, it is what the chapter files Ian sends carry,
    # and on 2026-09-21 it was the one that answered. content/sn25-v6.js
    # returns 403 from S3, so a page carrying only that runs no house script at
    # all. Version numbers are compared inside a path, never across two.
    SCRIPTS = [("content/sn25-v", 6), ("studyguide/sn25-v", 2)]
    found = []
    for path, current in SCRIPTS:
        for v in re.findall(re.escape(path) + r"(\d+)\.js", src):
            found.append((path, int(v), current))
    if not found:
        r.fail("head", "links no house script (content/sn25-v%d.js or "
                       "studyguide/sn25-v%d.js)" % (SCRIPTS[0][1], SCRIPTS[1][1]))
    else:
        for path, v, current in found:
            if v < current:
                r.fail("head", "references an older house asset: %s%d.js "
                               "(current is v%d)" % (path, v, current))
            else:
                r.ok("head", "links %s%d.js" % (path, v))

    stale = re.findall(r"sn25-v[0-5]\.css", src)
    if stale:
        r.fail("head", "references an older house stylesheet: %s"
               % ", ".join(sorted(set(stale))))

    # Ian's instruction of 2026-09-17 puts the house stylesheet first and the
    # three font links after it, on one line, as the current notes files carry
    # them. The ECO2013 file delivered earlier has the opposite order, and so
    # does prompt v6 step 0, so this can only ever warn: failing it would fail
    # shipped work. Reordering a delivered file is Ian's call, not a script's.
    css_at, font_at = src.find("sn25-v6.css"), src.find("Red+Hat+Display")
    if css_at >= 0 and font_at >= 0:
        if css_at < font_at:
            r.ok("head", "the house stylesheet precedes the font link")
        else:
            r.warn("head", "the font link precedes sn25-v6.css; the current "
                           "house head has the stylesheet first")


def check_engine(src, r):
    n = src.count(PLACEHOLDER)
    css_m, js_m = CSS_BLOCK.search(src), JS_BLOCK.search(src)

    # A chapter with no graphs in it -- ECO2023 chapter 8 has none at all --
    # needs no engine, and 22KB of one it never calls is dead weight in every
    # copy of the page. The missing-widgets warning already says the file has
    # none, so this stays quiet rather than failing a correct file.
    if not n and not (css_m or js_m) and '<div class="sdg"' not in blank_code(src):
        r.ok("engine", "no widgets in this file, so no engine to embed")
        return

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


# -------------------------------------------------------------------- toc ----

def check_toc(src, r):
    """The table of contents, and whether its anchors reach the headings.

    The house script would build this in the browser, but content/sn25-v6.js
    returns 403 from S3 -- alone among the five house assets -- so on a
    published page nothing runs and no table of contents appears. Until that is
    fixed the markup lives in the file, written by scripts/add_toc.py, and what
    matters is that it stays in step with the headings: a renamed heading
    silently breaks its own link."""
    body = src[src.find("<body"):] if "<body" in src else src
    hs = [(int(m.group(1)), re.search(r'\bid="([^"]*)"', m.group(2)))
          for m in re.finditer(r"<h([123])\b([^>]*)>", body, re.I)]
    block = re.search(r'<details class="toc-box">(.*?)</details>', body, re.S)

    if not block:
        if hs and not re.search(r"studyguide/sn25-v\d+\.js", src):
            r.warn("toc", "no table of contents; the house script cannot supply "
                          "one while content/sn25-v6.js is not public "
                          "(run scripts/add_toc.py)")
        elif hs:
            # studyguide/sn25-v2.js builds the box on DOMContentLoaded -- the
            # same <details class="toc-box"> with the same summary that
            # add_toc.py writes -- and gives every heading an id on the way. A
            # page carrying it needs no markup in the file.
            r.ok("toc", "the study-guide script builds the table of contents "
                        "in the browser")
        return

    if re.search(r"studyguide/sn25-v\d+\.js", src):
        # The script builds its own box unconditionally, so a file that also
        # carries one written in renders two. Four files did, because add_toc.py
        # wrote them while content/sn25-v6.js was the head's only script and it
        # is 403 -- nothing built one, so one had to be written. Swapping to the
        # live script is what turns that into a duplicate.
        r.fail("toc", "a table of contents is written into the file AND "
                      "studyguide/sn25-v2.js builds one: the page renders two. "
                      "Remove the written-in <details class=\"toc-box\">.")
        return

    linked = re.findall(r'href="#([^"]*)"', block.group(1))
    ids = [m.group(1) for _, m in hs if m]
    missing = [a for a in linked if a not in ids]
    unlisted = [m.group(1) for _, m in hs if m and m.group(1) not in linked]
    noid = sum(1 for _, m in hs if not m)

    if missing:
        r.fail("toc", "%d contents link(s) point at no heading: %s"
               % (len(missing), ", ".join(missing[:3])))
    if noid:
        r.fail("toc", "%d heading(s) have no id, so nothing can link to them" % noid)
    if unlisted:
        r.fail("toc", "%d heading(s) are missing from the contents: %s"
               % (len(unlisted), ", ".join(unlisted[:3])))
    if not (missing or noid or unlisted):
        r.ok("toc", "%d contents link(s) reach their headings" % len(linked))


# ----------------------------------------------------------------- schema ----

DEFAULTS = {"at": 0, "color": "ink", "guides": True, "curved": False,
            "thin": False, "dashed": False, "static": False, "grid": False}


def check_schema(cfgs, r):
    for n, cfg, _ in cfgs:
        has_steps = isinstance(cfg.get("steps"), list) and len(cfg["steps"]) >= 2
        static_preset = cfg.get("preset") and cfg.get("static") and cfg.get("scenarios")
        # A scenario widget whose panels are each titled is described without a
        # caption: the buttons name the cases and the titles say what each one
        # shows. That is the shape a widget takes when the prose above it
        # already explains the comparison, and requiring a caption there forces
        # the restatement the prose check exists to remove.
        titled_scenarios = bool(cfg.get("scenarios")) and all(
            v.get("title") for _, v in variants(cfg))
        # A title and a lede describe a figure in one line each, which is what
        # a widget is left with once its caption turns out to restate the
        # paragraph beside it. Requiring a caption there would put the
        # restatement straight back.
        if not (has_steps or cfg.get("caption") or static_preset or titled_scenarios
                or cfg.get("lede")
                or any(v.get("caption") or (isinstance(v.get("steps"), list)
                                            and len(v["steps"]) >= 2)
                       for _, v in variants(cfg))):
            r.fail("schema", "widget %d has neither steps (>=2), a caption, nor "
                             "titled scenarios" % n)

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
            # A movement arrow's colour defaults to red, not ink, so "ink" on
            # one is a decision rather than a restatement -- the labor
            # chapter's supply figure draws its two arrows black because the
            # source does. Everything else takes ink by default.
            is_move = isinstance(d.get("from"), list) and isinstance(d.get("to"), list)
            for k, val in DEFAULTS.items():
                if k == "color" and is_move:
                    continue
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


def label_len(text):
    """A label's width in characters, counting a _{...} subscript at .72.

    Mirrors the engine's own measure, which sets a subscript at .72em.
    """
    text = str(text)
    subs = [0]

    def eat(m):
        subs[0] += len(m.group(1))
        return ""

    plain = re.sub(r"_\{([^}]*)\}", eat, text)
    return len(plain) + 0.72 * subs[0]


def panel_h(pn, ax=None):
    """The engine's viewBox height: 250, or 268 where something sits below.

    A brace with `below: true`, or (v2.35) a wrapped Q axis title, which drops
    beneath the tick row rather than running back across it."""
    if len(str((ax or {}).get("x") or "Q").split("\n")) > 1:
        return 268.0
    return 268.0 if any(b.get("below") is True
                        for b in (pn.get("braces") or [])) else 250.0


def widest_p(pn, ax):
    """The width of the widest label the price axis carries.

    Engine v2.27 sizes the left margin to it, and v2.33 puts a left-hand
    upright brace outside it, so this has to match -- it is a copy of the
    engine's layout, and a copy that falls behind puts every coordinate below
    in the wrong place. The panel drawing `P* = ATC` was measured 17px out
    until this matched."""
    widest = 0.0
    for t in (ax.get("yticks") or []):
        widest = max(widest, 6.1 * label_len(fmt_p(t, ax)))
    for pt in (pn.get("points") or []):
        if pt.get("showP") is False:
            continue
        lab = pt.get("pl")
        widest = max(widest, 6.1 * label_len(
            lab if lab is not None else fmt_p(pt.get("p"), ax)))
    return widest


def vbrace_x(b, pn, ax, ox, X):
    """Where the engine draws an upright brace's spine.

    `left` puts it outside the price axis -- and since v2.33, outside the
    widest label that axis carries, because the labor chapter's CWD brace
    spans two wages named W_{Alaska} and W_{Hawaii} and was drawn straight
    through both. This lives in one place because it was written down twice,
    once for the brace and once for its label, and the first fix moved one of
    them."""
    if not b.get("left"):
        return X(b["q"])
    return min(ox - 32.0, ox - 24.0 - widest_p(pn, ax))


def geom(pn, ax):
    base = 62.0 if ax.get("cents") else (54.0 if ax.get("yticks") else 40.0)
    widest = widest_p(pn, ax)
    # engine v2.34: a wrapped price-axis title sits left of the axis, anchored
    # the other way, and the margin carries it like a price label
    yrows = str(ax.get("y") or "P").split("\n")
    ytw = max(9.8 * len(rw) for rw in yrows) if len(yrows) > 1 else 0.0
    left = max(base, math.ceil(widest) + 12.0, math.ceil(ytw) + 22.0)
    # A vbrace with left:true widens the engine's left margin. Miss this and
    # every coordinate below is off by 44px.
    if any(b.get("left") for b in (pn.get("vbraces") or [])):
        left += 44.0
    xmax = float(ax.get("xmax") or 1)
    ymax = float(ax.get("ymax") or 1)
    # Engine v2.28 sizes the right margin to the curve labels, the same way
    # v2.27 sizes the left to the price labels, and for the same reason: a
    # label anchored at a curve's end had nowhere to go and was drawn cut off.
    # This has to follow it, or every x below is wrong on exactly the panels
    # the engine had to widen.
    right = 36.0
    for _pass in range(6):
        pw_try = W - left - right
        want = 36.0
        for c in (pn.get("curves") or []):
            pts = c.get("pts") or []
            if not pts or c.get("label") == "":
                continue
            lp = pts[0] if c.get("lstart") else pts[-1]
            text = c.get("label")
            text = c.get("id") if text is None else text
            chars = max(label_len(row) for row in str(text).split("\n"))
            ends = left + (lp[0] / xmax) * pw_try + (6 if c.get("ldx") is None
                                                     else c.get("ldx"))
            over = ends + 9.1 * chars + 4 - W
            if over > 0:
                want = max(want, right + over)
        if want <= right + 0.01:
            break
        right = want
    right = min(right, W - left - 120.0)
    ox, oy = left, 205.0
    pw, ph = W - left - right, 178.0
    return (lambda q: ox + (q / xmax) * pw,
            lambda p: oy - (p / ymax) * ph, ox, oy)


def fmt_p(v, ax):
    # engine v2.35: a percent axis, money's opposite number
    if ax.get("pct"):
        return "%s%%" % v
    if not ax.get("money"):
        return str(v)
    if ax.get("cents"):
        return "$%.2f" % v
    return "$" + (str(int(v)) if float(v).is_integer() else "%.2f" % v)


def fmt_q(v, ax):
    if ax.get("pct"):
        return "%s%%" % v
    if ax.get("k") and v >= 1000:
        return "%gk" % (v / 1000.0)
    return "{:,}".format(v)


def brace_y(b, Y, oy):
    """Where the engine puts a brace's bracket, and which way its curl points.

    Three positions since v2.14: outside under the Q axis (below:true), inside
    the plot just under its price line (below:"in"), or just above that line
    (the default). Modelling "in" as "outside" -- which a plain truth test does,
    since "in" is truthy -- puts the test's idea of the brace 100px below the
    drawing and it stops colliding with anything."""
    if b.get("below") is True:
        return oy + 22, 1
    if b.get("below") == "in":
        return Y(b["p"]) + 8, 1
    if b.get("below") == "axis":
        return oy - 12, -1
    return Y(b["p"]) - 8, -1


def box(x, y, text, size, anchor="start", vcenter=False, weight=700):
    """The rectangle a piece of SVG text occupies.

    `y` is the baseline, so the box hangs mostly above it -- except where the
    engine sets dominant-baseline:central, which centres the text on `y`
    instead. Area labels are the only ones drawn that way (v2.13); modelling
    them as baseline-anchored put this test's idea of them ~3px above where
    the browser actually draws them, which is the difference between a label
    centred in its wedge and one lying across the wedge's edge."""
    # _{...} is a subscript run: the engine sets it at .72em, and the braces
    # are markup rather than glyphs. Counting them at full width made a label
    # like S_{George} measure half again as wide as it is drawn, and reported
    # overlaps between names that sit clear of each other.
    t = str(text)
    plain = re.sub(r"_\{[^}]*\}", "", t)
    subs = "".join(re.findall(r"_\{([^}]*)\}", t))
    # Measured in the browser rather than guessed: the 700-weight text (ticks,
    # tags, brace labels) runs at .583 em a character, and the 800-weight curve
    # labels and axis titles at .646 to .690. One constant of .58 for both put
    # "D = MB = MSB" 15px narrower than Chromium draws it, which is exactly the
    # margin by which it ran off the panel while this reported it as fitting.
    em = 0.70 if weight >= 800 else 0.58
    w = em * size * max(1, len(plain) + 0.72 * len(subs))
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    if vcenter:
        return (x, y - size * 0.5, x + w, y + size * 0.5)
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


def sample(px, n=70):
    """n points spread along a polyline in pixel space."""
    out = []
    for i in range(len(px) - 1):
        (x1, y1), (x2, y2) = px[i], px[i + 1]
        for s in range(n + 1):
            t = s / n
            out.append((x1 + t * (x2 - x1), y1 + t * (y2 - y1)))
    return out


def min_gap(a, b):
    """Closest approach between two polylines, in pixels."""
    pa, pb = sample(a), sample(b)
    best = 1e9
    for x1, y1 in pa:
        for x2, y2 in pb:
            d = (x1 - x2) ** 2 + (y1 - y2) ** 2
            if d < best:
                best = d
    return math.sqrt(best)


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
                    "the %s shift arrow" % (c.get("label") or c.get("id")),
                    (c.get("at", 0), c.get("until"))))
    for m in pn.get("moves") or []:
        if not (isinstance(m.get("from"), list) and isinstance(m.get("to"), list)):
            continue
        x1, y1 = X(m["from"][0]), Y(m["from"][1])
        x2, y2 = X(m["to"][0]), Y(m["to"][1])
        off = m.get("offset", 14)
        ln = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / ln * off, (x2 - x1) / ln * off
        out.append((((x1 + nx, y1 + ny), (x2 + nx, y2 + ny)),
                    "the movement arrow %s\u2192%s" % (m["from"], m["to"]),
                    (m.get("at", 0), m.get("until"))))
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
    # An axis title sits on its own axis by design: the engine anchors the y
    # title at the top of the P axis and the x title at the right end of the Q
    # axis. Every panel ever drawn would report it.
    if ("axis title" in desc_a and "axis lines" in desc_b) or \
       ("axis title" in desc_b and "axis lines" in desc_a):
        return True
    # A tick number is printed just outside its own axis, for the same reason.
    if ("tick on" in desc_a and "axis lines" in desc_b) or \
       ("tick on" in desc_b and "axis lines" in desc_a):
        return True
    # An x tick and a y tick only ever meet in the origin corner, where both
    # belong.
    if ("tick on Q" in desc_a and "tick on P" in desc_b) or \
       ("tick on P" in desc_a and "tick on Q" in desc_b):
        return True
    return False


def guide_segments(pn, X, Y, ox, oy, ax):
    """Every dashed guide the engine draws, as pixel polylines.

    Rule 5 lists curves, points, arrows and labels -- not guides. But a label
    pressed against the dashed line dropping from its own point reads as
    crowded, so these are tested too, and only ever warn."""
    out = []
    # The plot's width comes from the mapping, not from a right margin written
    # down here: v2.28 made that margin depend on the curve labels, and a
    # constant 36 drew the Q axis line past where the engine draws it.
    pw = X(float(ax.get("xmax") or 1)) - ox
    # The two axis lines. They are solid, not dashed, and they were the last
    # thing drawn on every panel that nothing tested against: a curve label
    # parked at the end of a curve that runs down to the axis lands on the axis
    # itself, which is exactly where "D" sat in the Piesanos figure. Always on
    # screen, so no visibility window.
    out.append(([(ox, 14.0), (ox, oy), (ox + pw + 14, oy)], "the axis lines",
                (0, None)))
    for p in pn.get("points") or []:
        if p.get("guides") is False:
            continue
        # v2.14: "p" draws only the leg to the price axis, "q" only the leg to
        # the quantity axis. Testing the whole elbow either way invents a guide
        # that is not on the drawing, and misses nothing when it is.
        elbow = [(ox, Y(p["p"])), (X(p["q"]), Y(p["p"])), (X(p["q"]), oy)]
        leg = {"p": elbow[:2], "q": elbow[1:]}.get(p.get("guides"), elbow)
        out.append((leg, "the guides from (%s, %s)" % (p["q"], p["p"]),
                    (p.get("at", 0), p.get("until"))))
    for h in pn.get("hlines") or []:
        out.append(([(ox, Y(h["p"])), (ox + pw + 8, Y(h["p"]))],
                    "the %s price line" % h.get("label", h["p"]),
                    (h.get("at", 0), h.get("until"))))
    for b in pn.get("braces") or []:
        win = (b.get("at", 0), b.get("until"))
        # the engine draws the drop guides for every brace that is not outside
        # the axis -- below:"in" included
        if b.get("below") is not True:
            for q in (b.get("q1"), b.get("q2")):
                if q is None:
                    continue
                out.append(([(X(q), Y(b["p"])), (X(q), oy)],
                            "a guide under the %r brace" % b.get("label"), win))
        # the bracket itself
        y, d = brace_y(b, Y, oy)
        x1, x2 = X(min(b["q1"], b["q2"])), X(max(b["q1"], b["q2"]))
        m = (x1 + x2) / 2.0
        out.append(([(x1, y), (x1 + 7, y + d * 7), (m - 7, y + d * 7), (m, y + d * 14),
                     (m + 7, y + d * 7), (x2 - 7, y + d * 7), (x2, y)],
                    "the %r brace" % b.get("label"), win))
    for b in pn.get("vbraces") or []:
        win = (b.get("at", 0), b.get("until"))
        y1, y2 = Y(max(b["p1"], b["p2"])), Y(min(b["p1"], b["p2"]))
        x = vbrace_x(b, pn, ax, ox, X)
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
                # Both titles wrap on \n since engine v2.33, the Q title
                # stacking upward and the W title downward. And the Q title
                # follows the plot's right edge, not the panel's -- v2.31
                # moved it and this went on measuring it at W - 2.
                def title_box(text, x, y, anchor):
                    rows = str(text).split("\n")
                    bx = box(x, y, max(rows, key=label_len), 14, anchor,
                             weight=800)
                    return (bx[0], bx[1], bx[2], bx[3] + (len(rows) - 1) * 15)
                xt_ttl = ax.get("x") or "Q"
                yt_ttl = ax.get("y") or "P"
                pw = X(float(ax.get("xmax") or 1)) - ox
                _xw = len(str(xt_ttl).split("\n")) > 1
                boxes.append((title_box(xt_ttl, ox + pw + 34,
                                        oy + (36.0 if _xw else 16.0), "end"),
                              "the %r axis title" % xt_ttl, (0, None)))
                _yw = len(str(yt_ttl).split("\n")) > 1
                boxes.append((title_box(yt_ttl,
                                        ox - (12.0 if _yw else 2.0),
                                        52.0 if _yw else 11.0,
                                        "end" if _yw else "start"),
                              "the %r axis title" % yt_ttl, (0, None)))
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
                    # a wrapped curve label (v2.19) is as wide as its longest
                    # line and as tall as all of them, and it grows downward
                    crows = str(text).split("\n")
                    bx = box(X(lp[0]) + c.get("ldx", 6),
                             Y(lp[1]) + c.get("ldy", 2 if up else 6),
                             max(crows, key=len), 13, weight=800)
                    bx = (bx[0], bx[1], bx[2], bx[3] + (len(crows) - 1) * 14)
                    boxes.append((bx, "curve label %r" % text,
                                  (c.get("at", 0), c.get("until"))))

                for p in pn.get("points") or []:
                    win = (p.get("at", 0), p.get("until"))
                    if p.get("label"):
                        # wraps on \n since engine v2.34, as wide as its
                        # longest row and as tall as all of them
                        prows = str(p["label"]).split("\n")
                        bx = box(X(p["q"]) + (p.get("dx") if p.get("dx") is not None else 9),
                                 Y(p["p"]) + (p.get("dy") if p.get("dy") is not None else -9)
                                 - (len(prows) - 1) * 6.5,
                                 max(prows, key=label_len), 12)
                        bx = (bx[0], bx[1], bx[2], bx[3] + (len(prows) - 1) * 13)
                        boxes.append((bx, "point label %r" % p["label"], win))
                    # The engine prints a point's own price and quantity on the
                    # axes unless they are already ticks (or pl/ql override
                    # them), so those labels exist whether the author wrote them
                    # or not, and have to be tested.
                    pl = p.get("pl") or (fmt_p(p["p"], ax)
                                         if p.get("showP") is not False
                                         and p["p"] not in yt
                                         and not any(h["p"] == p["p"] and coexist(win, (h.get("at", 0), h.get("until")))
                                                     for h in (pn.get("hlines") or []))
                                         else None)
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
                    y, d = brace_y(b, Y, oy)
                    x1b, x2b = X(min(b["q1"], b["q2"])), X(max(b["q1"], b["q2"]))
                    m = (x1b + x2b) / 2
                    hh = max(2.5, min(7.0, (x2b - x1b) / 4.0))
                    # a wrapped label is as wide as its longest line and as
                    # tall as all of them; measuring the joined string instead
                    # invents a box three times too wide
                    rows = str(b["label"]).split("\n")
                    widest = max(rows, key=len)
                    ly = y + d * 2 * hh + (12 if d > 0 else -4)
                    if d < 0:
                        ly -= (len(rows) - 1) * 13
                    lb = box(m, ly, widest, 12, "middle")
                    lb = (lb[0], lb[1], lb[2], lb[3] + (len(rows) - 1) * 13)
                    boxes.append((lb, "brace label %r" % b["label"],
                                  (b.get("at", 0), b.get("until"))))

                # A price line can name itself at its right-hand end (v2.14).
                for hh_ in pn.get("hlines") or []:
                    if not hh_.get("tag"):
                        continue
                    boxes.append((box(X(hh_["tagq"]) if hh_.get("tagq") is not None else ox + (W - ox - 36.0) + 6,
                                      Y(hh_["p"]) + hh_.get("tagdy", -6), hh_["tag"], 12,
                                      "middle" if hh_.get("tagq") is not None else "end"),
                                  "price-line tag %r" % hh_["tag"],
                                  (hh_.get("at", 0), hh_.get("until"))))

                for b in pn.get("vbraces") or []:
                    if not b.get("label"):
                        continue
                    win = (b.get("at", 0), b.get("until"))
                    y1, y2 = Y(max(b["p1"], b["p2"])), Y(min(b["p1"], b["p2"]))
                    x = vbrace_x(b, pn, ax, ox, X)
                    d = -1 if (b.get("left") or b.get("side") == "left") else 1
                    m = (y1 + y2) / 2.0
                    if b.get("left"):
                        # rotated a quarter turn, so the box is tall and narrow
                        lx = x + d * 22
                        h = 0.58 * 12 * len(str(b["label"]))
                        bx = (lx - 7, m - h / 2, lx + 7, m + h / 2)
                    else:
                        # wraps on \n since engine v2.29, as wide as its
                        # longest line and as tall as all of them, and the
                        # block is centred on the brace
                        vrows = str(b["label"]).split("\n")
                        bx = box(x + d * 20 + b.get("ldx", 0),
                                 m + 4 - (len(vrows) - 1) * 6.5 + b.get("ldy", 0),
                                 max(vrows, key=label_len), 11,
                                 "start" if d > 0 else "end")
                        bx = (bx[0], bx[1], bx[2],
                              bx[3] + (len(vrows) - 1) * 13)
                    boxes.append((bx, "upright brace label %r" % b["label"], win))

                # An area's label is drawn text like any other, and it was the
                # one category this test did not know about: v2.11 added
                # `areas`, and a "Total surplus" label landed squarely on the
                # equilibrium guide with the whole file still reporting PASS.
                for a in pn.get("areas") or []:
                    if not a.get("label"):
                        continue
                    pts = a.get("pts") or []
                    if not pts:
                        continue
                    lp = a.get("lp") or [sum(q[0] for q in pts) / float(len(pts)),
                                         sum(q[1] for q in pts) / float(len(pts))]
                    boxes.append((box(X(lp[0]) + a.get("ldx", 0),
                                      Y(lp[1]) + a.get("ldy", 0),
                                      a["label"], 11, "middle", vcenter=True),
                                  "area label %r" % a["label"],
                                  (a.get("at", 0), a.get("until"))))

                checked += len(boxes)

                arrows = arrow_segments(pn, X, Y)
                guides = guide_segments(pn, X, Y, ox, oy, ax)

                for bx, what, win in boxes:
                    # A label placed correctly in a panel with no room for it
                    # is drawn cut in half, and nothing else here sees it:
                    # every other test asks what the label overlaps, and the
                    # edge of the panel is not a curve. `P* = ATC` rendered as
                    # `= ATC` and `D = MB = MSB` as `D = M`, both with the file
                    # reporting PASS. The panel is the engine's viewBox, so
                    # text in the margins is fine and text past them is not.
                    x0, y0, x1, y1 = bx
                    if x0 < -0.5 or x1 > W + 0.5 or \
                       y0 < -0.5 or y1 > panel_h(pn, ax) + 0.5:
                        r.fail("labels", "%s: %s runs outside the panel -- "
                               "shorten it, wrap it on \\n, or move it inboard"
                               % (where, what))
                    for gpx, gdesc, gwin in guides:
                        if not coexist(win, gwin) or exempt(what, gdesc):
                            continue
                        if poly_hits(inflate(bx, 3.0), gpx):
                            # Rule 5 names the axis lines alongside curves: a
                            # label parked on one is as struck through as a
                            # label on a curve, and IC₁ shipped sitting on the
                            # Q axis with the file reporting 0 FAIL, because
                            # the axis lines were reported at the dashed
                            # guides' severity. Guides stay a warning; the two
                            # solid axis lines fail.
                            if gdesc == "the axis lines":
                                r.fail("labels", "%s: %s sits on %s"
                                       % (where, what, gdesc))
                            else:
                                r.warn("labels", "%s: %s is close to %s"
                                       % (where, what, gdesc))
                    for c in pn.get("curves") or []:
                        pts = c.get("pts") or []
                        if len(pts) < 2:
                            continue
                        # A curve asked to fade from a step (dimAt, engine
                        # v2.31) is drawn at a quarter opacity precisely so a
                        # label can be read over it. Declared, not inferred:
                        # nothing is exempt unless the config says so, and it
                        # only counts while the label and the fading overlap.
                        _d = c.get("dimAt")
                        if _d is not None and win[0] >= _d:
                            continue
                        # Only against a curve that is on screen at the same
                        # time. The guides loop has always checked this; these
                        # three did not, so a walkthrough was tested against the
                        # curve its next step replaces -- a collision that is
                        # never drawn, and one the author cannot fix.
                        if not coexist(win, (c.get("at", 0), c.get("until"))):
                            continue
                        cid = c.get("label") or c.get("id")
                        # A curve's own label used to be skipped outright here,
                        # on the grounds that it sits at its own end. That is
                        # true of the default offset, which puts the text clear
                        # to the right of the last point, and false the moment
                        # ldx/ldy move it: a label pulled back along its own
                        # curve lands squarely on the line. "D = MB = MSB"
                        # shipped struck through by its own demand curve with
                        # this file reporting PASS, so nothing is exempt now --
                        # a line through your own name is still a line through
                        # your own name.
                        if curve_hits(bx, pts, X, Y):
                            r.fail("labels", "%s: %s sits on curve %s" % (where, what, cid))
                    for seg, desc, _aw in arrows:
                        if not coexist(win, _aw):
                            continue
                        if poly_hits(bx, list(seg)):
                            r.fail("labels", "%s: %s sits on %s" % (where, what, desc))
                    for pt in pn.get("points") or []:
                        # dot:false draws no marker (v2.12) -- only the axis
                        # label, which is boxed separately above. Testing the
                        # marker anyway invents an obstacle that is not there.
                        if pt.get("dot") is False:
                            continue
                        if not coexist(win, (pt.get("at", 0), pt.get("until"))):
                            continue
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

                # Rule 5 forbids a label touching an arrow, and says an arrow
                # showing a change must read clearly: drawn beside a curve, in
                # open space, not crossing another arrow. None of that is a
                # label-versus-label overlap, so it needs its own tests.
                curve_px = [([(X(q), Y(p)) for q, p in (c.get("pts") or [])],
                             c.get("label") or c.get("id") or "a curve",
                             (c.get("at", 0), c.get("until")))
                            for c in (pn.get("curves") or [])
                            if len(c.get("pts") or []) >= 2]

                for i, (segA, descA, winA) in enumerate(arrows):
                    pa = list(segA)
                    # An arrow that points AT something on a curve touches that
                    # curve at its tip by definition -- two movement arrows
                    # converging on an equilibrium always do. So only the
                    # arrow's middle is tested: lying across a curve is a
                    # defect, landing on one is the whole point.
                    (ax1, ay1), (ax2, ay2) = segA
                    mid = [(ax1 + t * (ax2 - ax1), ay1 + t * (ay2 - ay1))
                           for t in (0.18, 0.82)]
                    for cpx, cdesc, cwin in curve_px:
                        if not coexist(winA, cwin):
                            continue
                        if min_gap(mid, cpx) < 2.0:
                            r.warn("arrows", "%s: %s lies across curve %s"
                                   % (where, descA, cdesc))
                    # Guides are deliberately not tested. A surplus arrow has to
                    # cross the guides between the price line and the
                    # equilibrium, so flagging it fires on correct work.
                    for segB, descB, winB in arrows[i + 1:]:
                        if not coexist(winA, winB):
                            continue
                        if min_gap(pa, list(segB)) < 4.0:
                            r.warn("arrows", "%s: %s and %s touch, and read as "
                                   "one arrow" % (where, descA, descB))

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
    n_checked = n_bad = 0
    for n, cfg, _ in cfgs:
        for label, v in variants(cfg):
            if v.get("preset"):
                continue
            # The surplus/shortage pattern needs BOTH a disequilibrium price
            # line and a brace naming the gap it opens. Neither alone works:
            # an equilibrium-shift widget carries a Surplus/Shortage brace --
            # the gap at the old price -- without a line, and is the pattern v6
            # step 4 templates without moves, so the brace alone flags those
            # wrongly; a world price is an hline without such a brace, and a
            # market opened to trade settles away from equilibrium and stays
            # there, so the line alone flags the trade chapter wrongly. There
            # is no movement back to draw in either.
            hlines = [h for pn in panels(v) for h in (pn.get("hlines") or [])]
            gap = [b for pn in panels(v) for b in (pn.get("braces") or [])
                   if re.search(r"surplus|shortage", str(b.get("label", "")), re.I)]
            # ...and the price line must be a bare disequilibrium price, not a
            # policy the market cannot leave. A ceiling, a floor or a minimum
            # wage opens exactly the same gap and never closes it: the price
            # stays put because it is illegal to move, so there is no return to
            # equilibrium to draw and demanding the arrows flags every control
            # figure in the chapter. A named line (`tag`) is a policy line.
            named = [h for h in hlines if is_control(h)]
            if not hlines or named or not gap or not v.get("steps"):
                continue
            n_checked += 1
            last = len(v["steps"]) - 1
            moves = []
            for pn in panels(v):
                moves += [m for m in (pn.get("moves") or [])
                          if m.get("at", 0) <= last and (m.get("until") is None
                                                         or m["until"] > last)]
            if len(moves) < 2:
                n_bad += 1
                r.fail("arrows", "widget %d%s: a surplus/shortage walkthrough must end "
                                 "with two movement arrows, found %d"
                       % (n, " (%s)" % label if label else "", len(moves)))
    # Only claim a pass for the ones that actually passed -- reporting
    # "N walkthroughs end with two arrows" beside a FAIL for one of them
    # reads as a green check on a file that just failed.
    if n_checked - n_bad:
        r.ok("arrows", "%d surplus/shortage walkthrough(s) end with two movement "
                       "arrows" % (n_checked - n_bad))


def is_control(h):
    """Is this price line a policy the market cannot leave?

    A ceiling, a floor, a minimum wage, a world price, a world price plus a
    tariff -- as against a disequilibrium price the market is passing through.
    `tag` alone will not do: a tag is whether the line is NAMED on screen,
    which is a question of room, so a line says what it is with `control:true`.

    Only the arrow rule reads this now. A control price used to forbid a dot
    where a quantity meets it, on the grounds that the line already marks it;
    Ian's call (2026-09-23) is to match the artwork, which draws the dot.
    """
    return bool(h.get("control") or h.get("tag"))


def check_controls(cfgs, r):
    """Guides: one per quantity, and each ending at a number.

    Two points at the same quantity each draw their own vertical, one straight
    down the other: twice the ink, no more information, and it is most of what
    makes a busy panel look busy. And a dashed line running to a blank spot on
    an axis is one the reader cannot use -- the value is suppressed, or will not
    fit beside its neighbour -- so the guide goes and the dot stays.
    """
    dupes = dangling = n = 0
    for idx, cfg, _ in cfgs:
        for label, v in variants(cfg):
            if v.get("preset"):
                continue
            for pn in panels(v):
                where = "widget %d%s" % (idx, " (%s)" % label if label else "")
                n += 1
                ax = pn.get("axes") or {}
                yt = set(ax.get("yticks") or [])
                xt = set(ax.get("xticks") or [])
                hp = {h["p"] for h in (pn.get("hlines") or [])}   # windows checked below
                # A value is written on the axis if ANY point on the panel
                # writes it. The gap point in a shift walkthrough sits at the
                # old price, which the equilibrium has already labelled P1 --
                # its guide runs to a number, just not one it wrote itself.
                for _pt in pn.get("points") or []:
                    if _pt.get("pl") or _pt.get("showP") is not False:
                        yt.add(_pt["p"])
                    if _pt.get("ql") or _pt.get("showQ") is not False:
                        xt.add(_pt["q"])
                drops = {}
                for pt in pn.get("points") or []:
                    g = pt.get("guides", True)
                    # A dashed line has to end at a number. One running to a
                    # blank spot on an axis -- because the value is suppressed,
                    # or will not fit beside its neighbour -- is a line the
                    # reader cannot use. Drop the guide and keep the dot.
                    # A point carrying its own name is identified already:
                    # the guide leads the eye to "C" or "E2" rather than to a
                    # number, which is how a symbolic figure marks a position.
                    # What this catches is a guide to an anonymous point.
                    # `divider: true` says in the config what the drawing
                    # cannot: this dashed line separates two regions rather
                    # than marking a reading, so there is nothing to write at
                    # its foot. The labor chapter's supply curve turns at a
                    # wage the chapter never names, and the source still draws
                    # the line, because it is where the two effects balance.
                    # Declared, not inferred -- a guide without a number is
                    # still a defect everywhere it is not said to be one.
                    if g is not False and not pt.get("label") \
                            and not pt.get("divider"):
                        if g != "q" and not (pt.get("pl") or pt["p"] in yt or pt["p"] in hp
                                             or pt.get("showP") is not False):
                            dangling += 1
                            r.fail("controls", "%s: the guide from (%s, %s) reaches the price "
                                               "axis with nothing written there"
                                   % (where, pt["q"], pt["p"]))
                        if g != "p" and not (pt.get("ql") or pt["q"] in xt
                                             or pt.get("showQ") is not False):
                            dangling += 1
                            r.fail("controls", "%s: the guide from (%s, %s) reaches the quantity "
                                               "axis with nothing written there"
                                   % (where, pt["q"], pt["p"]))
                    # a point on the axis has a vertical leg of zero length,
                    # so it is not drawing a second line down anything
                    if g is not False and g != "p" and pt.get("p", 0) > 0:
                        drops.setdefault(pt["q"], []).append((pt.get("at", 0), pt.get("until")))
                for q, wins in drops.items():
                    for i in range(len(wins)):
                        for j in range(i + 1, len(wins)):
                            if coexist(wins[i], wins[j]):
                                dupes += 1
                                r.warn("controls", "%s: two guides run down q = %s at once"
                                       % (where, q))
                                break
    if n and not dupes and not dangling:
        r.ok("controls", "every guide ends at a number, and none is drawn twice")


FORMULA = re.compile(r"\\\(([^)]{0,400}?)\\\)", re.S)


NUM_RE = re.compile(r"\$?\d[\d,]*(?:\.\d+)?")


def check_calcs(src, cfgs, r):
    """A widget shows its working only where the chapter does not.

    Ian's rule: where the prose prints the formula as text under the figure,
    a `calcs` block says the same thing twice. Where the formulas live inside
    the artwork -- and are therefore lost the moment the image is replaced --
    the widget has to carry them. So a calc line is a duplicate when the same
    equation appears in the prose between this widget and the next.
    """
    dup = n = 0
    bodies = widget_starts(src, cfgs)
    for pos, (idx, cfg, _) in zip(bodies, cfgs):
        lines = []
        walk(cfg, lambda d: lines.extend(
            [c if isinstance(c, str) else c.get("text", "") for c in (d.get("calcs") or [])]))
        if not lines:
            continue
        n += 1
        nxt = next((b for b in bodies if b > pos), len(src))
        # from the end of this widget, not its start: the slice used to carry
        # the widget's own config, so the word scan found every calc line
        # quoted in its own JSON and failed the file against itself.
        after = JSON_RE.sub(" ", src[pos:nxt])
        for ln in lines:
            # A duplicate shows the same working, so it shows the same
            # numbers. Matching the result plus the left-hand side alone was
            # too loose: the chapter's own "TS = CS + PS = $173,333.33 +
            # $40,000" contains the token CS and the total, and failed a
            # widget whose working -- the trapezoid split into $66,666.67 and
            # $106,666.67 -- appears nowhere in the prose. Requiring every
            # number of the line keeps the rule on formulas the chapter
            # really does print twice.
            lhs = ln.split("=")[0].strip()
            res = ln.rsplit("=", 1)[-1].strip()
            nums = NUM_RE.findall(ln)
            if not lhs or not res:
                continue
            # The chapter often states the same working as a sentence
            # rather than a formula: "The vertical intercept is 20 loaves."
            # Matching only \( ... \) let a calcs block through that repeated
            # every number in the paragraph under it.
            prose_txt = re.sub(r"<[^>]+>", " ", after)
            flat_prose = re.sub(r"\s+", " ", prose_txt).replace(",", "")
            # The name and the result have to arrive together, as one
            # statement: "the vertical intercept is 20 loaves". Testing them
            # separately failed the trade chapter, whose prose happens to
            # contain both "total surplus" and the number 120 -- the latter
            # being units exported, not a surplus.
            lhs_words = [w for w in re.split(r"[^A-Za-z]+", lhs) if len(w) > 3]
            said = False
            if lhs_words and res:
                phrase = r".{0,40}?".join(re.escape(w) for w in lhs_words)
                phrase += r".{0,40}?" + re.escape(res.replace(",", ""))
                said = re.search(phrase, flat_prose, re.I | re.S) is not None
            if said:
                # Reported, not failed. A chapter that prints the same working
                # as a formula is a duplicate by construction; prose naming
                # the result is a judgement call -- the tax figure's prose
                # mentions "($9)" in passing while the working behind it
                # appears nowhere, and dropping that block would lose it.
                r.warn("calcs", "widget %d: the prose under the figure states "
                                "%r in words -- check whether the working is "
                                "still worth showing" % (idx, ln))
                break
            for m in FORMULA.finditer(after):
                body = m.group(1).replace("\\", "").replace("{", "").replace("}", "")
                flat = body.replace(",", "")
                if res.replace(",", "") in flat and lhs.split()[0] in body \
                        and all(x.replace(",", "") in flat for x in nums):
                    dup += 1
                    r.fail("calcs", "widget %d: %r is printed again as prose below the "
                                    "figure -- drop the calcs, the chapter already shows it"
                           % (idx, ln))
                    break
    if n and not dup:
        r.ok("calcs", "%d widget(s) show working the chapter does not print itself" % n)



STOP = set("""a an the and or but if of to in on at for from by with as is are was were be been
being it its this that these those there here them they their we you your our not no than then
so such into over under about which who whom whose what when where while each every both all any
some more most other another same can will would could should may might must do does did done
have has had how why very much many few less least also only just even still yet per""".split())
WORD = re.compile(r"[A-Za-z][A-Za-z'’-]+|\$?\d[\d,.]*")


def content(text):
    out = set()
    for w in WORD.findall(text or ""):
        w = w.lower().strip("'" + "\u2019-.,;:)")
        # a short token is noise unless it is a number: $3 and 65 are
        # two characters each and are the whole content of a caption
        if w in STOP or (len(w) < 3 and not any(c.isdigit() for c in w)):
            continue
        out.add(w)
    return out


def widget_starts(src, cfgs):
    """Where each config's widget sits in the file, in document order.

    Searching for the opening tag finds one more than there are widgets: the
    engine's header comment quotes the markup verbatim. That shifted every
    widget on to the paragraph before the previous one, so both checks that
    read the prose around a widget were reading the wrong prose. Locating each
    widget by its own body cannot drift that way.
    """
    starts, at = [], 0
    for _idx, _cfg, body in cfgs:
        i = src.find(body, at)
        starts.append(i if i >= 0 else at)
        at = max(at, i + len(body)) if i >= 0 else at
    return starts


def check_caption_prose(src, cfgs, r):
    """Does the caption say what the paragraph above it already said?

    Vertical space is the scarce thing on these pages, and a caption that
    restates the sentences around it costs a dozen lines a chapter for
    nothing. This measures the caption's content words against the paragraphs
    on either side of the widget: one almost entirely contained in them is a
    caption to cut down to whatever it adds, or drop.

    Both sides count. A figure introducing a worked question is followed by
    its answer, and the answer restates what the drawing shows, so a caption
    can be redundant with the paragraph after it as easily as the one before.

    It reports rather than fails, because what to keep is an editorial call --
    a caption that repeats the setup often still ends with the one sentence
    the prose does not have.
    """
    starts = widget_starts(src, cfgs)
    n = wordy = 0
    paras = [(m.start(), m.group(1)) for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", src, re.S)]
    for pos, (idx, cfg, _) in zip(starts, cfgs):
        # The paragraphs on either side, not just the ones before. A figure
        # that introduces a worked question is followed by its answer, and the
        # answer restates what the drawing shows -- which is where the rental
        # market's caption was being said a second time.
        before = [t for st, t in paras if st < pos][-2:]
        after = [t for st, t in paras if st > pos][:2]
        prose = re.sub(r"<[^>]+>", " ", " ".join(before + after))
        before = content(prose)
        if len(before) < 8:
            continue
        # Captions only. A lede is one line under the title and costs nothing
        # worth reclaiming, while its whole job -- naming what the figure
        # shows -- guarantees it shares vocabulary with the paragraph that
        # introduces it. Measuring ledes reported the summaries that were
        # working as intended.
        texts = []
        walk(cfg, lambda d: texts.extend(
            [d["caption"]] if isinstance(d.get("caption"), str) else []))
        for t in texts:
            words = content(t)
            if len(words) < 8:
                continue
            n += 1
            # A number the prose does not have is content, whatever the word
            # overlap says: a caption reading the values off the drawing shares
            # its vocabulary with the paragraph introducing it and is still the
            # only place those values appear.
            added = words - before
            new_numbers = {w for w in added if any(c.isdigit() for c in w)}
            frac = len(words & before) / float(len(words))
            # Both signals, because either alone misreads a caption. A ratio
            # alone misses a restatement that is paraphrased ("steep" for
            # "slope") and so scores lower than it reads; a count alone
            # punishes a short caption, which adds few words by being short.
            # A redundant one here does both: two thirds shared, and three to
            # five words of its own. A number the prose lacks exempts it
            # outright -- that is content the reader can get nowhere else.
            # A caption can restate the paragraph in fresh words and share
            # very little vocabulary with it while adding no fact at all. When
            # it carries numbers and every one of them is already in the
            # prose, that is what has happened, so the bar drops.
            numbers = {w for w in words if any(c.isdigit() for c in w)}
            restated = bool(numbers) and not new_numbers and frac >= 0.45
            if not new_numbers and (frac >= 0.75
                                    or (frac >= 0.6 and len(added) <= 5)
                                    or restated):
                wordy += 1
                r.warn("prose", "widget %d: %d%% of %r is already in the "
                                "prose around it -- cut it to what it adds"
                       % (idx, round(frac * 100),
                          t[:58] + ("..." if len(t) > 58 else "")))
    if n and not wordy:
        r.ok("prose", "%d caption(s) say something the prose above them does not" % n)


# About four lines at phone width, and 40% above the median caption already
# in this repo, so a caption written to the point is nowhere near it.
CAPTION_MAX = 200

# A caption that shows its working gets more room -- Ian's call, 2026-09-28.
# It still has to be concise, but the length is carrying the arithmetic rather
# than padding it: the numbers going in, the step between them, and the answer
# cannot be cut without losing the reason the caption is there.
CAPTION_MAX_WORKING = 260

NUMBER = re.compile(r"\d+(?:[.,]\d+)*")


def shows_working(text, has_calcs):
    """Whether a caption is doing arithmetic rather than describing a picture.

    Three numbers is the line, because that is what a worked step costs: the
    two values going in and the one coming out. Two is a before and after,
    which is prose. A widget carrying a `calcs` block is working by
    declaration, whatever its captions happen to say.
    """
    return has_calcs or len(NUMBER.findall(text)) >= 3


def _walk_has(cfg, key):
    found = []
    walk(cfg, lambda d: found.append(True) if d.get(key) is not None else None)
    return bool(found)


def check_captions(cfgs, r):
    bad = 0
    for n, cfg, _ in cfgs:
        texts = []
        walk(cfg, lambda d: texts.extend(
            [d["caption"]] if isinstance(d.get("caption"), str) else []))
        for _, v in variants(cfg):
            texts += [s for s in (v.get("steps") or []) if isinstance(s, str)]
        has_calcs = any(True for _ in [1] if _walk_has(cfg, "calcs"))
        for c in texts:
            s = c.strip()
            if re.match(r"^(before|after)\s*[-–—:]", s, re.I):
                r.fail("caption", "widget %d: 'Before -/After -' prefix: %r" % (n, s[:60]))
                bad += 1
            # The target is the slide-bullet punchline -- "Price up, quantity
            # up." -- not the words "up" and "down" wherever they appear. Bare
            # "price down" used as a clause of its own, or joined straight to
            # "and quantity", is shorthand; "pushes the price down toward
            # equilibrium" is a sentence, and failing it failed correct prose.
            elif re.search(r"\b(price|quantity)\s+(up|down)\b"
                           r"(?=\s*[,.;:]|\s*$|\s+and\s+(?:the\s+)?(?:price|quantity)\b)",
                           s, re.I):
                r.fail("caption", "widget %d: shorthand instead of words: %r" % (n, s[-40:]))
                bad += 1
            elif not re.search(r"[.!?]$", s):
                r.warn("caption", "widget %d: not a complete sentence: %r" % (n, s[:60]))
            # Vertical space is the scarce thing on these pages, and the
            # concise editions are produced by a pipeline that rewrites the
            # prose and leaves widget captions exactly as they are -- so a
            # caption that runs long here runs long in every edition. The
            # cap is the hard ceiling, not the target: the median caption in
            # this repo is 145 characters, which is where a good one sits.
            cap = (CAPTION_MAX_WORKING if shows_working(s, has_calcs)
                   else CAPTION_MAX)
            if len(s) > cap:
                r.fail("caption", "widget %d: caption is %d characters, over %d: %r"
                       % (n, len(s), cap, s[:60]))
                bad += 1
    if cfgs and not bad:
        r.ok("caption", "captions are prose, and none over %d characters "
                        "(%d where one shows its working)"
                        % (CAPTION_MAX, CAPTION_MAX_WORKING))


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


DATE_RE = re.compile(r'<p class="date">(.*?)</p>', re.S)


def check_dates(src, r, source=None):
    """Every class date in the source survives into the output.

    A chapter's date pills are the only record of which class covered what,
    and they are the easiest thing in the file to lose: they carry no content,
    so summarising, restructuring or rebuilding a chapter drops them without
    leaving a gap anyone notices. A concise edition of a module that its full
    edition dates over three class meetings, carrying none at all, still reads
    as a complete document.

    With no source to compare against, a file carrying no date line is worth a
    look but is not wrong -- a reference page or a prototype has no class
    behind it. Given the source with --source, a date that was in it and is
    not in the output is a defect, and fails.
    """
    mine = [t.strip() for t in DATE_RE.findall(src)]
    if source is None:
        if not mine:
            r.warn("dates", "no <p class=\"date\"> line in this file -- if it "
                            "covers a class meeting, its date is missing")
        else:
            r.ok("dates", "%d class date(s): %s" % (len(mine), "; ".join(mine)))
        return
    theirs = [t.strip() for t in DATE_RE.findall(source)]
    missing = [d for d in theirs if d not in mine]
    for d in missing:
        r.fail("dates", "the source dates a class %r and this file does not "
                        "carry it" % d)
    extra = [d for d in mine if d not in theirs]
    for d in extra:
        r.warn("dates", "%r is dated here but not in the source" % d)
    kept = [d for d in theirs if d in mine]
    if len(kept) > 1 and [d for d in mine if d in theirs] != kept:
        r.warn("dates", "the class dates appear in a different order than the "
                        "source has them")
    if not missing and not extra:
        r.ok("dates", "all %d class date(s) carried over from the source"
             % len(theirs))


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
    ap.add_argument("--source", metavar="PATH",
                    help="the file this one was built from (the full edition, "
                         "the chapter as sent). Its class dates must all "
                         "survive into FILE.")
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
    check_toc(src, r)
    cfgs = configs(src, r)
    check_schema(cfgs, r)
    check_labels(cfgs, r)
    check_tick_emphasis(cfgs, r)
    check_steps(cfgs, r)
    check_steady_labels(cfgs, r)
    check_arrows(cfgs, r)
    check_controls(cfgs, r)
    check_calcs(src, cfgs, r)
    check_captions(cfgs, r)
    check_caption_prose(src, cfgs, r)
    check_source(src, cfgs, r)
    check_names(src, cfgs, r)
    check_images(src, r)
    check_dates(src, r, pathlib.Path(args.source).read_text(encoding="utf-8")
                if args.source else None)
    r.skip("numbers", "whether each number is the source's number needs the source")

    print("\n%d FAIL, %d WARN" % (r.fails, r.warns))
    return 1 if r.fails else 0


if __name__ == "__main__":
    sys.exit(main())
