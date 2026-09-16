#!/usr/bin/env python3
"""Mechanical checks on a finished notes file (conversion prompt, step 8).

    python scripts/check_file.py examples/ECO2013-263-SupplyAndDemand.html

Checks, in order:

  head      house format -- a <title>, sn25-v6.css and sn25-v6.js from the
            Smokin' Notes bucket, and no lingering v5 reference
  engine    the engine is embedded in the file, and the embedded bytes are
            identical to engine/sd-graph.js and engine/sd-graph.css
  hosted    nothing still <link>s or <script src>es the engine from elsewhere
  json      every <div class="sdg"> holds one parseable JSON config
  escape    no literal </script> inside a JSON config (it would end the block)
  schema    each config has axes or panels, captions are prose, steps referenced
            by at/until exist
  source    no student-facing text names where the material came from
  images    <!-- IMAGE POSITION: ... --> comments are still present

A file that links ../engine/ directly is an engine test bed, not a notes file,
so the house-format, embedding and image checks are reported SKIP for it.

Every line is PASS, WARN or FAIL. The script exits non-zero if anything FAILs.
It cannot check the things that matter most -- whether a number is the number
the source gave, whether a label touches a curve. Those need the source and
scripts/render_widgets.py.
"""

import argparse
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_SRC = ROOT / "engine" / "sd-graph.css"
JS_SRC = ROOT / "engine" / "sd-graph.js"

# Words that give away where the material came from. Hard rule 4: student-facing
# text never mentions its source.
SOURCE_WORDS = [
    "the transcript", "the lecture", "the recording", "the board", "the slides",
    "the class", "the file", "the video", "the professor", "the instructor",
    "in class", "the notes say", "the reading", "the textbook", "the handout",
]

WIDGET_RE = re.compile(
    r'<div class="sdg"[^>]*>(.*?)</div>', re.S)
JSON_RE = re.compile(
    r'<script type="application/json">(.*?)</script>', re.S)


class Report:
    def __init__(self):
        self.fails = 0
        self.warns = 0

    def ok(self, name, msg):
        print("PASS  %-8s %s" % (name, msg))

    def warn(self, name, msg):
        self.warns += 1
        print("WARN  %-8s %s" % (name, msg))

    def fail(self, name, msg):
        self.fails += 1
        print("FAIL  %-8s %s" % (name, msg))

    def skip(self, name, msg):
        print("SKIP  %-8s %s" % (name, msg))


def strip_header(js):
    if not js.lstrip().startswith("/*"):
        return js
    return js[js.index("*/") + 2:].lstrip("\n")


def embedded(src, ext):
    m = re.search(
        r"<!-- sd-graph engine [^>]*sd-graph\.%s\) -->\s*<(?:style|script)>\n(.*?)\n"
        r"</(?:style|script)>\s*<!-- /sd-graph engine [^>]*-->" % ext, src, re.S)
    return m.group(1) if m else None


def is_testbed(src):
    """True for a file that links the engine out of engine/ instead of embedding
    it -- examples/engine-testbed.html and any scratch copy of it."""
    return bool(re.search(r'["\']\.\./engine/sd-graph\.(css|js)["\']', src))


def check_head(src, r):
    if re.search(r"<title>\s*</title>", src) or "<title>" not in src:
        r.fail("head", "no <title>")
    else:
        title = re.search(r"<title>(.*?)</title>", src, re.S).group(1).strip()
        if ":" in title or "|" in title:
            r.warn("head", "<title> should be the chapter name only: %r" % title)
        else:
            r.ok("head", "<title> is %r" % title)

    for asset in ("sn25-v6.css", "sn25-v6.js"):
        if asset in src:
            r.ok("head", "links %s" % asset)
        else:
            r.fail("head", "does not link %s" % asset)
    if re.search(r"sn25-v5\.(css|js)", src):
        r.fail("head", "still references sn25-v5 -- house format is v6")


def check_engine(src, r):
    for ext, path in (("css", CSS_SRC), ("js", JS_SRC)):
        got = embedded(src, ext)
        if got is None:
            r.fail("engine", "engine/sd-graph.%s is not embedded" % ext)
            continue
        want = path.read_text(encoding="utf-8")
        if ext == "js":
            want = strip_header(want)
        if got.rstrip("\n") == want.rstrip("\n"):
            r.ok("engine", "embedded sd-graph.%s is byte-identical to engine/" % ext)
        else:
            r.fail("engine", "embedded sd-graph.%s differs from engine/ -- "
                             "re-run scripts/embed_engine.py" % ext)


def check_hosted(src, r):
    stray = re.findall(r'<link[^>]*sd-graph\.css[^>]*>', src, re.I)
    stray += re.findall(r'<script[^>]*src=["\'][^"\']*sd-graph\.js["\']', src, re.I)
    if stray:
        r.fail("hosted", "%d reference(s) to a hosted engine copy remain" % len(stray))
    else:
        r.ok("hosted", "no hosted engine references")


def widget_bodies(src):
    """Each widget's raw JSON text, in document order."""
    out = []
    for m in re.finditer(r'<div class="sdg"[^>]*>', src):
        start = m.end()
        depth = 1
        i = start
        while depth and i < len(src):
            nxt_open = src.find("<div", i)
            nxt_close = src.find("</div>", i)
            if nxt_close == -1:
                break
            if nxt_open != -1 and nxt_open < nxt_close:
                depth += 1
                i = nxt_open + 4
            else:
                depth -= 1
                i = nxt_close + 6
        out.append(src[start:i - 6])
    return out


def check_widgets(src, r):
    bodies = widget_bodies(src)
    if not bodies:
        r.warn("json", "no <div class=\"sdg\"> widgets in this file")
        return []
    configs = []
    for n, body in enumerate(bodies, 1):
        blocks = JSON_RE.findall(body)
        raw = blocks[0] if blocks else body
        if "</script>" in raw:
            r.fail("escape", "widget %d: literal </script> inside the config" % n)
        try:
            cfg = json.loads(raw)
        except ValueError as e:
            r.fail("json", "widget %d: %s" % (n, e))
            continue
        configs.append((n, cfg))
    if configs:
        r.ok("json", "%d of %d widget config(s) parse" % (len(configs), len(bodies)))
    return configs


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def check_schema(configs, r):
    for n, cfg in configs:
        if not (cfg.get("axes") or cfg.get("panels") or cfg.get("preset")):
            r.fail("schema", "widget %d: no axes and no panels (figure mode is "
                             "not implemented)" % n)

        for label, variant in scenario_variants(cfg):
            steps = variant.get("steps") or []
            last = len(steps) - 1
            over = []

            def check_step(d):
                for key in ("at", "until", "at_step"):
                    v = d.get(key)
                    if isinstance(v, int) and steps and v > last:
                        over.append("%s=%d" % (key, v))
            walk({k: v for k, v in variant.items() if k != "scenarios"}, check_step)
            if over:
                where = "widget %d" % n + (" (%s)" % label if label else "")
                r.fail("schema", "%s: %s but there are only %d step(s)"
                       % (where, ", ".join(sorted(set(over))), len(steps)))

        captions = []
        walk(cfg, lambda d: captions.append(d["caption"])
             if isinstance(d.get("caption"), str) else None)
        for c in captions:
            if re.match(r"^\s*(before|after)\s*[-–—:]", c, re.I):
                r.fail("caption", "widget %d: 'Before -/After -' caption: %r" % (n, c[:60]))
            elif not re.search(r"[.!?]\s*$", c.strip()):
                r.warn("caption", "widget %d: caption is not a full sentence: %r"
                       % (n, c[:60]))
    if configs:
        r.ok("schema", "%d config(s) checked against the schema" % len(configs))


def scenario_variants(cfg):
    """(label, merged config) for the base config and each scenario overlay."""
    scenarios = cfg.get("scenarios") or []
    if not scenarios:
        return [(None, cfg)]
    out = []
    for sc in scenarios:
        merged = dict(cfg)
        merged.update(sc.get("overlay") or {})
        out.append((sc.get("label"), merged))
    return out


def visible_text(src):
    """Student-facing text: widget captions and labels, plus body prose."""
    parts = []
    for body in widget_bodies(src):
        blocks = JSON_RE.findall(body)
        raw = blocks[0] if blocks else body
        try:
            cfg = json.loads(raw)
        except ValueError:
            continue
        walk(cfg, lambda d: parts.extend(
            str(d[k]) for k in ("caption", "text", "title", "label")
            if isinstance(d.get(k), str)))
    prose = re.sub(r"<(script|style)\b.*?</\1>", " ", src, flags=re.S | re.I)
    prose = re.sub(r"<!--.*?-->", " ", prose, flags=re.S)
    prose = re.sub(r"<[^>]+>", " ", prose)
    parts.append(prose)
    return parts


def check_source_words(src, r):
    hits = []
    for text in visible_text(src):
        low = text.lower()
        for w in SOURCE_WORDS:
            if w in low:
                hits.append(w)
    if hits:
        for w in sorted(set(hits)):
            r.fail("source", "student-facing text names its source: %r" % w)
    else:
        r.ok("source", "no student-facing text names its source")


def check_images(src, r):
    marks = re.findall(r"<!--\s*IMAGE POSITION:", src)
    if marks:
        r.ok("images", "%d IMAGE POSITION comment(s) preserved" % len(marks))
    else:
        r.warn("images", "no IMAGE POSITION comments (expected if the source "
                         "had no graph images)")
    left = re.findall(r"<img\b[^>]*>", src, re.I)
    if left:
        r.warn("images", "%d <img> tag(s) remain -- every graph image should be "
                         "a widget" % len(left))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="notes HTML file to check")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        sys.exit("no such file: %s" % path)
    src = path.read_text(encoding="utf-8")
    r = Report()

    print("checking %s\n" % path)
    testbed = is_testbed(src)
    if testbed:
        r.skip("head", "engine test bed, not a notes file: house format not checked")
        r.skip("engine", "engine test bed: links ../engine/ on purpose")
    else:
        check_head(src, r)
        check_engine(src, r)
        check_hosted(src, r)
    configs = check_widgets(src, r)
    check_schema(configs, r)
    check_source_words(src, r)
    if not testbed:
        check_images(src, r)

    print("\n%d FAIL, %d WARN" % (r.fails, r.warns))
    return 1 if r.fails else 0


if __name__ == "__main__":
    sys.exit(main())
