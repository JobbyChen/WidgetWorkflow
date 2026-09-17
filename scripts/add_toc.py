#!/usr/bin/env python3
"""Write the house table of contents into a notes file.

    python scripts/add_toc.py examples/ECO2023-263-ThePPF.html

The house script (content/sn25-v5.js, and studyguide/sn25-v2.js, which are the
same code apart from the emoji and where they insert) builds the table of
contents in the browser: a collapsed <details class="toc-box"> holding one
anchor per h1/h2/h3, h2s nested under their h1, inserted before the first <h1>.

content/sn25-v6.js, which every converted file loads, returns 403 from S3 -- it
is the only one of the five house assets that is not public -- so on a published
page nothing runs and no table of contents appears. Until that object's
permissions are fixed, the markup has to be in the file, so this writes exactly
what the script would have produced: the same element, the same classes and
inline styles, and ids computed by the same rule.

Run again after changing any heading; it replaces the block it wrote before.
"""

import argparse
import html
import io
import pathlib
import re
import sys

MARK_OPEN = '<details class="toc-box">'
MARK_END = "</details>"
EMOJI = "\U0001F4D8"          # the 'closed book' the current notes render


def slug(text, i):
    """The house script's id rule, character for character.

    heading.textContent.trim().toLowerCase()
        .replace(/\\s+/g, '-').replace(/[^\\w-]/g, '')

    JavaScript's \\w is [A-Za-z0-9_], so an ampersand or a curly apostrophe is
    dropped rather than replaced -- "Scarcity & Opportunity Cost" really does
    become "scarcity--opportunity-cost", with the two hyphens."""
    s = re.sub(r"\s+", "-", text.strip().lower())
    s = re.sub(r"[^A-Za-z0-9_-]", "", s)
    return s or ("section-%d" % i)


def headings(src):
    """(match, level, inner html, plain text) for every h1/h2/h3 in the body."""
    body_at = src.find("<body")
    out = []
    for m in re.finditer(r"<h([123])\b([^>]*)>(.*?)</h\1>", src, re.S | re.I):
        if m.start() < body_at:
            continue
        inner = m.group(3)
        text = html.unescape(re.sub(r"<[^>]+>", "", inner))
        out.append((m, int(m.group(1)), inner.strip(), " ".join(text.split())))
    return out


def build(src):
    hs = headings(src)
    if not hs:
        return src, 0

    # ids first, so the anchors and the headings cannot drift apart
    ids, edits = [], []
    for i, (m, lvl, inner, text) in enumerate(hs):
        have = re.search(r'\bid="([^"]*)"', m.group(2))
        hid = have.group(1) if have else slug(text, i)
        ids.append(hid)
        if not have:
            edits.append((m.start(), m.end(),
                          '<h%d id="%s"%s>%s</h%d>'
                          % (lvl, hid, m.group(2), inner, lvl)))
    for start, end, new in reversed(edits):
        src = src[:start] + new + src[end:]

    lines = ['<details class="toc-box">',
             "<summary><strong>%s Table of Contents</strong></summary>" % EMOJI,
             "<nav>", '<ul style="line-height: 1.8">']
    open_sub = False
    for (m, lvl, inner, text), hid in zip(hs, ids):
        link = '<a href="#%s"%s>%s</a>' % (
            hid, ' style="font-weight: bold"' if lvl == 1 else "", inner)
        if lvl == 1:
            if open_sub:
                lines += ["</ul>", "</li>"]
                open_sub = False
            else:
                if lines[-1].startswith("<li>"):
                    lines[-1] += "</li>"
            lines.append("<li>" + link)
        else:
            if not open_sub:
                lines.append("<ul>")
                open_sub = True
            lines.append("<li>" + link + "</li>")
    if open_sub:
        lines += ["</ul>", "</li>"]
    elif lines[-1].startswith("<li>"):
        lines[-1] += "</li>"
    lines += ["</ul>", "</nav>", MARK_END]
    toc = "\n".join(lines)

    # replace the block written last time, else insert before the first heading
    old = re.search(re.escape(MARK_OPEN) + r".*?" + re.escape(MARK_END) + r"\n*",
                    src, re.S)
    if old:
        return src[:old.start()] + toc + "\n\n" + src[old.end():], len(hs)
    first = re.search(r"<h1\b", src[src.find("<body"):], re.I)
    at = src.find("<body") + first.start()
    return src[:at] + toc + "\n\n" + src[at:], len(hs)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", nargs="+", type=pathlib.Path)
    a = ap.parse_args()
    for f in a.files:
        src = io.open(f, encoding="utf-8").read()
        out, n = build(src)
        if not n:
            print("%s: no h1/h2/h3 headings, nothing to do" % f)
            continue
        io.open(f, "w", encoding="utf-8").write(out)
        print("%s: table of contents over %d heading(s)" % (f, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
