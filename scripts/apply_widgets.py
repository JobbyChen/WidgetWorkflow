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

An image entry is a widget config, `{"keep": why}`, or a **calculator widget**
for the FIN3403 set (2026-10-16): `{"hp": "tvm"|"cf"|"amort"|"stat"|"keys",
...attributes}`. Each remaining key becomes a `data-` attribute on a
`<div class="hp10bii…">` (`alt` is JSON-encoded into `data-alt`), the engine
for those is `engine/hp10bii.css` + `engine/hp10bii.js`, embedded as a
`<style>` and a `<script>` after the house script, and the original `<img>`
tag is kept inside a `<noscript>` so a reader without JavaScript still sees
the screenshot. `"occurrence": 2` replaces only the second use of an image
that the file carries twice and leaves the others as they are. `expect` and
`alt_expect` are test expectations for a harness; `--strip-expect` drops
them from the delivered file. A kept image is left as
the tag it is -- no comment is added, because the file's other content is not
this script's to change -- and the reason goes in the changelog. `anchors`
reuse a config from `images` by name, or carry their own under `widget`; an
anchor may instead carry `html`, a block of plain HTML (a `<table>` of the
figure's numbers) to insert in place of a widget where a Concise edition has
no room for one (Ian, 2026-10-12: a figure that is numbers the Concise text
lacks becomes a table of text, never a run of widgets back to back).

Every `<img>` in the file must be in the map (a graph nobody decided about is
a mistake), every anchor must match exactly once, and every mapped config
must be used, or the script stops without writing. And before writing, the
script proves the claim in its first paragraph: with the engine, the widgets
and the comments it inserted taken back out of the output, and the replaced
`<img>` tags taken out of the source, the two are byte-identical.
"""

import argparse
import html
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
HP_KINDS = {"tvm": "hp10bii", "cf": "hp10bii-cf", "keys": "hp10bii-keys",
            "amort": "hp10bii-amort", "stat": "hp10bii-stat"}
ENGINE_DIR = pathlib.Path(__file__).resolve().parent.parent / "engine"
STRIP_EXPECT = False


def hp_block():
    css = (ENGINE_DIR / "hp10bii.css").read_text(encoding="utf-8")
    js = (ENGINE_DIR / "hp10bii.js").read_text(encoding="utf-8")
    assert "</style" not in css and "</script" not in js
    return "<style>\n%s</style>\n<script>\n%s</script>\n" % (css, js)


def hp_html(cfg, img_tag=""):
    """<div class="hp10bii" data-...>[<noscript>img</noscript>]</div> from a map entry."""
    kind = HP_KINDS.get(cfg.get("hp"))
    if not kind:
        sys.exit("unknown calculator widget kind: %r" % cfg.get("hp"))
    attrs = []
    for k, v in cfg.items():
        if k in ("hp", "occurrence") or (STRIP_EXPECT and k in ("expect", "alt_expect")):
            continue
        name = "data-" + k.replace("_", "-")
        if k == "alt":
            text = json.dumps(v, ensure_ascii=False)
            if "'" in text:
                sys.exit("data-alt may not contain a single quote: %s" % text[:80])
            attrs.append("%s='%s'" % (name, text.replace("&", "&amp;").replace("<", "&lt;")))
        else:
            attrs.append('%s="%s"' % (name, html.escape(str(v), quote=True)))
    inner = "<noscript>%s</noscript>" % img_tag if img_tag else ""
    return '<div class="%s" %s>%s</div>' % (kind, " ".join(attrs), inner)


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
    removed = []       # (start, end) of every <img> tag it took out, in source order
    seen = {}          # basename -> how many times the file has used it so far

    # 2. images
    def sub(match):
        tag = match.group(0)
        s = SRC_RE.search(tag)
        base = os.path.basename(s.group(1)) if s else ""
        if base not in images:
            problems.append("image not in the map: %s" % (base or tag[:60]))
            return tag
        entry = images[base]
        seen[base] = seen.get(base, 0) + 1
        if isinstance(entry, dict) and "keep" in entry:
            used.add(base)
            return tag
        if isinstance(entry, dict) and "occurrence" in entry and entry["occurrence"] != seen[base]:
            return tag             # another use of the same picture stays a picture
        used.add(base)
        if isinstance(entry, dict) and "hp" in entry:
            # the calculator widget wraps the tag (kept for <noscript>); for the proof
            # the tag has left the source and come back inside the inserted snippet
            removed.append(match.span())
            inserted.append(hp_html(entry, tag))
            return inserted[-1]
        removed.append(match.span())
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
        if "html" in a:
            if "</script" in a["html"].lower() or '<div class="sdg"' in a["html"]:
                problems.append("an html anchor may not carry a script or a widget: %r" % needle[:60])
                continue
            if a.get("image"):
                used.add(a["image"])     # the figure this table stands in for
            body = a["html"].strip()
        else:
            cfg = a.get("widget")
            if cfg is None:
                cfg = images.get(a.get("image"))
                if cfg is None or "keep" in cfg:
                    problems.append("anchor names no usable widget: %r" % needle[:60])
                    continue
                used.add(a["image"])
            body = hp_html(cfg) if "hp" in cfg else widget_html(cfg)
        pos = out.find(needle)
        end = block_end(out, pos)
        comment = a.get("comment", "below-referenced paragraph")
        ins = "\n<!-- IMAGE POSITION: %s -->\n%s\n" % (comment, body)
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

    # 1. engine(s)
    n_sdg = out.count('<div class="sdg"')   # before the engine's own doc comment joins the file
    n_hp = sum(out.count('<div class="%s" ' % k) for k in HP_KINDS.values())
    n_widgets = n_sdg + n_hp
    if not n_widgets:
        return out, 0
    hpb = hp_block() if n_hp else ""
    if n_hp:
        hm = HOUSE_SCRIPT_RE.search(out)
        if hm:
            out = out[:hm.end()] + hpb + out[hm.end():]
        else:
            out = out.replace("</head>", hpb + "</head>", 1)
    if n_sdg:
        if PLACEHOLDER not in out and not embed_engine.CSS_BLOCK.search(out):
            hm = HOUSE_SCRIPT_RE.search(out)
            if hm:
                out = out[:hm.end()] + PLACEHOLDER + "\n" + out[hm.end():]
            else:
                out = out.replace("</head>", PLACEHOLDER + "\n</head>", 1)
        out = re.sub(r"[ \t]*" + re.escape(PLACEHOLDER) + r"[ \t]*\n?",
                     lambda _m: embed_engine.blocks(), out, count=1)

    # the proof: nothing but the engine(s) and the widgets differs
    back = out.replace(embed_engine.blocks(), "", 1) if n_sdg else out
    if n_hp:
        back = back.replace(hpb, "", 1)
    for snippet in inserted:
        assert snippet in back, "an inserted snippet is not in the output"
        back = back.replace(snippet, "", 1)
    # cut the replaced tags out of the source by position: a picture the file uses
    # twice is the same bytes twice, and replace() would take the wrong one
    orig, pos = [], 0
    for a, b in removed:
        orig.append(src[pos:a]); pos = b
    orig.append(src[pos:])
    orig = "".join(orig)
    if back != orig:
        sys.exit("%s: the output differs from the source beyond the widgets "
                 "and the engine; not written" % name)
    return out, n_widgets


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
    ap.add_argument("--strip-expect", action="store_true",
                    help="drop the calculator widgets' test expectations (the delivered file)")
    args = ap.parse_args()
    global STRIP_EXPECT
    STRIP_EXPECT = args.strip_expect
    src = pathlib.Path(args.source).read_text(encoding="utf-8")
    m = json.loads(pathlib.Path(args.map).read_text(encoding="utf-8"))
    out, n = apply(src, m, args.source, args.anchors, args.toc)
    pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.out).write_text(out, encoding="utf-8")
    print("%s: %d widgets -> %s" % (os.path.basename(args.source), n, args.out))


if __name__ == "__main__":
    main()
