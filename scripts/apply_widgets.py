#!/usr/bin/env python3
"""Put widgets into a notes file from a map, without touching anything else.

    python scripts/apply_widgets.py SOURCE.html MAP.json OUT.html [--anchors] [--toc]

The job the UCF project asked for (2026-10-12): a copy of each Full, Balanced
and Concise chapter with widgets in place of its graph images and nothing
else changed. So this script does exactly three things and refuses to do a
fourth:

  1. Puts the `<!--SDG-ENGINE-->` placeholder on the line after the house
     script and embeds the engine there (scripts/embed_engine.py's blocks).
  2. Replaces each `<img>` whose src basename is in the map's `images` with
     that image's widget. The IMAGE POSITION comment beside it stays where
     it is; the tag's own attributes are gone with the tag.
  3. With --toc, swaps the head's house script for the live table-of-contents
     script, `studyguide/sn25-v2.js` (Ian, 2026-10-12: "one thing you can fix
     is the toc"). The UCF files carry `content/sn25-v5.js`, which puts its
     box above everything in <body>; the live script builds the same box
     before the first <h1>. No UCF file has a written-in TOC, so nothing is
     doubled.
  4. With --anchors, inserts a widget after an anchor element, for a file
     with no `<img>` (the Concise editions): each entry in `anchors` names a
     unique substring of the file and the widget goes after the block element
     containing it. Without the flag `anchors` is ignored, so one map serves
     all three editions of a chapter.

MAP.json:

    {"images": {"eco2023-market-equilibrium-04-price-ceiling-diagram.png":
                    {"title": "...", "axes": {...}, ...},
                "eco2023-ppf-08-circular-flow-diagram.png":
                    {"keep": "a flow diagram, not a plotted graph"}},
     "anchors": [{"after": "<b>Binding price ceiling</b>",
                  "image": "eco2023-market-equilibrium-04-price-ceiling-diagram.png"}]}

An image entry is a widget config or `{"keep": why}`. A kept image is left as
the tag it is -- no comment is added, because the file's other content is not
this script's to change -- and the reason goes in the changelog. `anchors`
reuse a config from `images` by name, or carry their own under `widget`.

Every `<img>` in the file must be in the map (a graph nobody decided about is
a mistake), every anchor must match exactly once, and every mapped config
must be used, or the script stops without writing. And before writing, the
script proves the claim in its first paragraph: with the engine, the widgets
and the comments it inserted taken back out of the output, and the replaced
`<img>` tags taken out of the source, the two are byte-identical.
"""

import argparse
import json
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import embed_engine  # noqa: E402

PLACEHOLDER = "<!--SDG-ENGINE-->"
IMG_RE = re.compile(r"<img\b[^>]*?>", re.S)
SRC_RE = re.compile(r'src="([^"]*)"')
HOUSE_SCRIPT_RE = re.compile(r'^[ \t]*<script[^>]*src="[^"]*sn25-v\d+\.js"[^>]*>\s*</script>[ \t]*\n',
                             re.M)
TOC_SCRIPT = "https://smokinnotes.s3.us-east-1.amazonaws.com/studyguide/sn25-v2.js"
OLD_SCRIPT_RE = re.compile(r'https://smokinnotes\.s3\.us-east-1\.amazonaws\.com/content/sn25-v\d+\.js')
BLOCK_OPEN_RE = re.compile(r"<(p|ul|ol|table|div|h[1-6]|li|tr|td|th|blockquote)\b", re.I)


def widget_html(cfg):
    text = json.dumps(cfg, ensure_ascii=False)
    if "</script" in text.lower():
        sys.exit("a config contains '</script' inside a string: %s" % text[:80])
    return '<div class="sdg"><script type="application/json">%s</script></div>' % text


def block_end(src, pos):
    """Index just after the block element that contains position `pos`."""
    # The nearest opening block tag before pos says what we are inside.
    opens = [m for m in BLOCK_OPEN_RE.finditer(src, 0, pos)]
    if not opens:
        return src.find("\n", pos) + 1
    tag = opens[-1].group(1).lower()
    if tag in ("li", "tr", "td", "th"):
        # inside a list item or table cell: the whole list or table is the block
        closers = ["</ul>", "</ol>"] if tag == "li" else ["</table>"]
        ends = [src.find(c, pos) for c in closers]
        ends = [e for e in ends if e >= 0]
        if not ends:
            sys.exit("no closing tag for the %s containing %r" % (tag, src[pos:pos + 40]))
        end = min(ends)
        return end + len(src[end:src.find(">", end) + 1])
    close = "</%s>" % tag
    end = src.find(close, pos)
    if end < 0:
        sys.exit("no %s after %r" % (close, src[pos:pos + 40]))
    return end + len(close)


def apply(src, m, name, use_anchors=False, toc=False):
    if toc:
        n = len(OLD_SCRIPT_RE.findall(src))
        if n != 1:
            sys.exit("%s: expected one content/sn25-v*.js script line, found %d" % (name, n))
        src = OLD_SCRIPT_RE.sub(TOC_SCRIPT, src)   # the proof below compares against this
    images = m.get("images", {})
    anchors = m.get("anchors", []) if use_anchors else []
    used = set()
    problems = []
    inserted = []      # every snippet this run put in, for the proof at the end
    removed = []       # every <img> tag it took out

    # 2. images
    def sub(match):
        tag = match.group(0)
        s = SRC_RE.search(tag)
        base = os.path.basename(s.group(1)) if s else ""
        if base not in images:
            problems.append("image not in the map: %s" % (base or tag[:60]))
            return tag
        entry = images[base]
        used.add(base)
        if isinstance(entry, dict) and "keep" in entry:
            return tag
        removed.append(tag)
        inserted.append(widget_html(entry))
        return inserted[-1]

    out = IMG_RE.sub(sub, src)

    # 3. anchors
    for a in anchors:
        needle = a["after"]
        n = out.count(needle)
        if n != 1:
            problems.append("anchor matches %d times, not once: %r" % (n, needle[:60]))
            continue
        cfg = a.get("widget")
        if cfg is None:
            cfg = images.get(a.get("image"))
            if cfg is None or "keep" in cfg:
                problems.append("anchor names no usable widget: %r" % needle[:60])
                continue
            used.add(a["image"])
        pos = out.find(needle)
        end = block_end(out, pos)
        comment = a.get("comment", "below-referenced paragraph")
        ins = "\n<!-- IMAGE POSITION: %s -->\n%s\n" % (comment, widget_html(cfg))
        inserted.append(ins)
        out = out[:end] + ins + out[end:]

    for base, entry in images.items():
        if base not in used and not (isinstance(entry, dict) and "keep" in entry):
            # an unused widget is only a problem in a file that has images at
            # all; a Concise file reaches them through anchors
            if IMG_RE.search(src):
                problems.append("mapped widget never used: %s" % base)

    if problems:
        sys.exit("%s:\n  " % name + "\n  ".join(problems))

    # 1. engine
    if '<div class="sdg"' not in out:
        return out, 0
    if PLACEHOLDER not in out and not embed_engine.CSS_BLOCK.search(out):
        hm = HOUSE_SCRIPT_RE.search(out)
        if hm:
            out = out[:hm.end()] + PLACEHOLDER + "\n" + out[hm.end():]
        else:
            out = out.replace("</head>", PLACEHOLDER + "\n</head>", 1)
    out = re.sub(r"[ \t]*" + re.escape(PLACEHOLDER) + r"[ \t]*\n?",
                 lambda _m: embed_engine.blocks(), out, count=1)

    # the proof: nothing but the engine and the widgets differs
    back = out.replace(embed_engine.blocks(), "", 1)
    for snippet in inserted:
        assert snippet in back, "an inserted snippet is not in the output"
        back = back.replace(snippet, "", 1)
    orig = src
    for tag in removed:
        orig = orig.replace(tag, "", 1)
    if back != orig:
        sys.exit("%s: the output differs from the source beyond the widgets "
                 "and the engine; not written" % name)
    return out, out.count('<div class="sdg"')


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("map")
    ap.add_argument("out")
    ap.add_argument("--anchors", action="store_true",
                    help="apply the map's anchors (the Concise edition)")
    ap.add_argument("--toc", action="store_true",
                    help="swap content/sn25-v*.js for the live TOC script")
    args = ap.parse_args()
    src = pathlib.Path(args.source).read_text(encoding="utf-8")
    m = json.loads(pathlib.Path(args.map).read_text(encoding="utf-8"))
    out, n = apply(src, m, args.source, args.anchors, args.toc)
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.out).write_text(out, encoding="utf-8")
    print("%s: %d widgets -> %s" % (os.path.basename(args.source), n, args.out))


if __name__ == "__main__":
    main()
