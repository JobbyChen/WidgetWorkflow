#!/usr/bin/env python3
"""Inline engine/sd-graph.css and engine/sd-graph.js into a notes file's <head>.

    python scripts/embed_engine.py examples/engine-testbed.html

This is step 7 of the conversion prompt. A published notes file must carry its
own copy of the engine -- no <link> or <script src> pointing at S3, because a
file that fetches the engine breaks the moment the engine moves.

The embedded copies sit between marker comments, so running this again after an
engine change replaces them in place instead of stacking copies. It also
replaces any <link>/<script src> that references sd-graph.css or sd-graph.js.

Repo convention: engine/sd-graph.js keeps its header comment; the embedded copy
drops it (the version line is carried by the marker comment instead). Run
scripts/check_file.py afterwards -- it verifies the embedded bytes match.
"""

import argparse
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSS_SRC = ROOT / "engine" / "sd-graph.css"
JS_SRC = ROOT / "engine" / "sd-graph.js"

BEGIN = "<!-- sd-graph engine %s (embedded from engine/sd-graph.%s) -->"
END = "<!-- /sd-graph engine %s -->"

LINK_RE = re.compile(r'[ \t]*<link[^>]*sd-graph\.css[^>]*>\s*\n?', re.I)
SCRIPT_RE = re.compile(r'[ \t]*<script[^>]*src=["\'][^"\']*sd-graph\.js["\'][^>]*>\s*</script>\s*\n?', re.I)
BLOCK_RE = r"<!-- sd-graph engine [^>]*sd-graph\.%s\) -->.*?<!-- /sd-graph engine %s -->\s*"


def engine_version():
    """The version comment at the top of engine/sd-graph.js, e.g. 'v2'."""
    head = JS_SRC.read_text(encoding="utf-8").split("\n", 1)[0]
    m = re.search(r"\b(v\d+)\b", head)
    return m.group(1) if m else "v?"


def strip_header(js):
    """Drop the leading /* ... */ header comment from the engine source."""
    if not js.lstrip().startswith("/*"):
        return js
    end = js.index("*/") + 2
    return js[end:].lstrip("\n")


def build_blocks(version):
    css = CSS_SRC.read_text(encoding="utf-8").rstrip("\n")
    js = strip_header(JS_SRC.read_text(encoding="utf-8")).rstrip("\n")
    css_block = "%s\n<style>\n%s\n</style>\n%s\n" % (
        BEGIN % (version, "css"), css, END % version)
    js_block = "%s\n<script>\n%s\n</script>\n%s\n" % (
        BEGIN % (version, "js"), js, END % version)
    return css_block, js_block


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="notes HTML file to embed into")
    ap.add_argument("-n", "--dry-run", action="store_true", help="report, do not write")
    args = ap.parse_args()

    path = pathlib.Path(args.file)
    if not path.exists():
        sys.exit("no such file: %s" % path)
    src = path.read_text(encoding="utf-8")
    version = engine_version()
    css_block, js_block = build_blocks(version)

    # Remove anything already there: previous embeds, and links to a hosted copy.
    out = re.sub(BLOCK_RE % ("css", r"[^>]*"), "", src, flags=re.S)
    out = re.sub(BLOCK_RE % ("js", r"[^>]*"), "", out, flags=re.S)
    removed_links = len(LINK_RE.findall(out)) + len(SCRIPT_RE.findall(out))
    out = LINK_RE.sub("", out)
    out = SCRIPT_RE.sub("", out)

    if "</head>" not in out:
        sys.exit("%s has no </head> to embed into" % path)
    out = out.replace("</head>", css_block + js_block + "</head>", 1)

    if args.dry_run:
        print("would embed engine %s into %s (%d external reference(s) removed)"
              % (version, path, removed_links))
        return 0
    if out == src:
        print("%s already up to date (engine %s)" % (path, version))
        return 0
    path.write_text(out, encoding="utf-8")
    print("embedded engine %s into %s (%d external reference(s) removed)"
          % (version, path, removed_links))
    return 0


if __name__ == "__main__":
    sys.exit(main())
