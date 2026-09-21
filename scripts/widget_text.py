#!/usr/bin/env python3
"""Every student-visible string in a notes file's widgets, addressed for editing.

    python scripts/widget_text.py examples/ECO2023-263-ThePPF.html
    python scripts/widget_text.py <file> --json > semester.json
    python scripts/widget_text.py <file> --apply semester.json

A new semester usually changes the same thing everywhere: the good, the market,
the story. Prompt v6 step 0C calls this mode (d) -- "when a symbolic widget's
good changes, only the title and captions change; the drawing is fixed" -- but
nothing here made the wording easy to see apart from the geometry, so a swap
meant rereading every config and hoping.

This lists exactly the strings a semester swap may touch, each under an address
like `w4.scenarios.sub.steps[2]`, and writes an edited set back. Coordinates,
ticks and step wiring are never listed and never touched, so a swap cannot move
a curve by accident. Numbers inside a caption are not touched either: if the new
semester changes them, that is a reconversion, not a swap, because the drawing
has to change with them.

Round-trip is exact: dumping and applying with nothing edited leaves the file
byte for byte as it was.
"""

import argparse
import io
import json
import pathlib
import re
import sys

BLOCK = re.compile(r'(<script type="application/json">\n)(.*?)(\n</script>)', re.S)

# What a semester can rename. Anything not on this list is geometry or wiring.
KEYS = ("title", "lede", "caption", "heading", "label")


def visit(node, path, out):
    """Collect (address, text) for every renamable string under node."""
    if isinstance(node, dict):
        for k, v in node.items():
            here = "%s.%s" % (path, k) if path else k
            if k == "steps" and isinstance(v, list):
                for i, step in enumerate(v):
                    if isinstance(step, str):
                        out.append(("%s[%d]" % (here, i), step))
            elif k == "cols" and isinstance(v, list):
                for i, col in enumerate(v):
                    if isinstance(col, str):
                        out.append(("%s[%d]" % (here, i), col))
            elif k in ("x", "y") and path.endswith("axes") and isinstance(v, str):
                out.append((here, v))
            elif k in KEYS and isinstance(v, str):
                out.append((here, v))
            else:
                visit(v, here, out)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            visit(item, "%s[%d]" % (path, i), out)


def put(node, path, value):
    """Write value at an address produced by visit()."""
    parts = re.findall(r"[^.\[\]]+|\[\d+\]", path)
    for p in parts[:-1]:
        node = node[int(p[1:-1])] if p.startswith("[") else node[p]
    last = parts[-1]
    if last.startswith("["):
        node[int(last[1:-1])] = value
    else:
        node[last] = value


def configs(src):
    return [(m, json.loads(m.group(2))) for m in BLOCK.finditer(src)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("--json", action="store_true", help="machine-readable map")
    ap.add_argument("--apply", type=pathlib.Path, metavar="MAP",
                    help="write an edited map back into the file")
    a = ap.parse_args()
    src = io.open(a.file, encoding="utf-8").read()
    blocks = configs(src)

    if a.apply:
        edits = json.loads(io.open(a.apply, encoding="utf-8").read())
        out, at, changed = [], 0, 0
        for n, (m, cfg) in enumerate(blocks, 1):
            for addr, text in edits.items():
                w, _, rest = addr.partition(".")
                if w != "w%d" % n:
                    continue
                cur = dict(visit_map(cfg))
                if rest in cur and cur[rest] != text:
                    put(cfg, rest, text)
                    changed += 1
            body = json.dumps(cfg, indent=1, ensure_ascii=False)
            out.append(src[at:m.start(2)]); out.append(body); at = m.end(2)
        out.append(src[at:])
        io.open(a.file, "w", encoding="utf-8").write("".join(out))
        print("%s: %d string(s) replaced" % (a.file, changed))
        return 0

    rows = []
    for n, (_, cfg) in enumerate(blocks, 1):
        for addr, text in visit_map(cfg):
            rows.append(("w%d.%s" % (n, addr), text))
    if a.json:
        print(json.dumps(dict(rows), indent=1, ensure_ascii=False))
    else:
        for addr, text in rows:
            print("%-42s %s" % (addr, text if len(text) < 96 else text[:93] + "..."))
        print("\n-- %d string(s) across %d widget(s)" % (len(rows), len(blocks)))
    return 0


def visit_map(cfg):
    out = []
    visit(cfg, "", out)
    return out


if __name__ == "__main__":
    sys.exit(main())
