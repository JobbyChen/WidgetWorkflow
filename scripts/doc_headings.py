#!/usr/bin/env python3
"""List a Word file's headings and their level, so conversions stop guessing.

    python scripts/doc_headings.py notes.docx
    python scripts/doc_headings.py notes.doc

Heading level is a property of the source's formatting, not of how important a
section looks, and every heading in the output must be one this prints -- no
more, no fewer. Getting that wrong was a recurring defect: sections were
promoted to <h1> because they read like major topics.

The rule, verified against all four Fall '26 ECO documents:

  .docx   bold with no size override        -> h1
          bold + underline at sz 23 (11.5pt) -> h2

  .doc    Helvetica-Bold 12, centred        -> h1
          Times-Bold 11.5, underlined       -> h2

A .doc is read through antiword's PostScript output, because antiword's text
and DocBook output both drop the formatting -- and its floating text boxes
entirely, so run `catdoc` over a .doc as well and check nothing is missing.

Read the list before using it. Underlining is also how the source marks a
call-out box's title and the odd stressed word mid-sentence, and from
PostScript those are indistinguishable from a sub-heading. A box title
("Exam 1 Topics") belongs to its box, not to the heading outline.
"""

import io
import os
import pathlib
import re
import shutil
import subprocess
import sys
from xml.etree import ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
V = "{urn:schemas-microsoft-com:vml}"


def from_docx(path):
    import zipfile
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    parents = {c: p for p in root.iter() for c in p}

    def in_shape(el):
        p = parents.get(el)
        while p is not None:
            if p.tag in (V + "group", V + "shape", V + "textbox",
                         W + "txbxContent"):
                return True
            p = parents.get(p)
        return False

    def fmt(run):
        rpr = run.find(W + "rPr")
        if rpr is None or rpr.find(W + "b") is None:
            return None
        sz = rpr.find(W + "sz")
        return (rpr.find(W + "u") is not None,
                sz.get(W + "val") if sz is not None else None)

    out = []
    for para in root.iter(W + "p"):
        runs = [r for r in para.iter(W + "r")
                if not any(in_shape(t) for t in r.iter(W + "t"))]
        runs = [r for r in runs
                if "".join(t.text or "" for t in r.iter(W + "t")).strip()]
        if not runs:
            continue
        # A heading is the run span a paragraph opens with. The rest of the
        # paragraph may be anything -- in these files a heading often shares its
        # paragraph with an exam-tip box or a figure's labels.
        head = fmt(runs[0])
        if head is None:
            continue
        text = ""
        for r in runs:
            if fmt(r) != head:
                break
            text += "".join(t.text or "" for t in r.iter(W + "t"))
        text = " ".join(text.split())
        # An emphasised answer ("0.5") is bold and underlined too, so require
        # a heading to contain a letter.
        if not text or len(text) > 95 or not any(c.isalpha() for c in text):
            continue
        under, sz = head
        if under and sz == "23":
            out.append((2, text))
        elif not under and sz is None:
            out.append((1, text))
    return out


def from_doc(path):
    if not shutil.which("antiword"):
        sys.exit("antiword is needed to read a .doc (apt-get install antiword)")
    # antiword refuses PostScript under a UTF-8 locale, and PostScript is the
    # only one of its outputs that carries the formatting.
    env = dict(os.environ, LANG="C", LC_ALL="C")
    ps = subprocess.run(["antiword", "-p", "letter", str(path)],
                        capture_output=True, env=env).stdout.decode("latin-1")
    out, font = [], ("", "")
    for line in ps.split("\n"):
        line = line.strip()
        m = re.match(r"([\d.]+) /(\S+) /\S+ ChgFnt", line)
        if m:
            font = (m.group(1), m.group(2))
            continue
        m1 = re.match(r"\((.*)\) show$", line)
        m2 = re.match(r"\((.*)\) [\d.-]+ [\d.-]+ LineShow$", line)
        text = (m1 or m2) and (m1 or m2).group(1).replace("\\(", "(").replace("\\)", ")").strip()
        if not text or len(text) > 95:
            continue
        if m1 and font[1].startswith("Helvetica"):
            out.append((1, text))
        elif (m2 and font[1] == "Times-Bold" and text[:1].isupper()
              and " " in text):
            out.append((2, text))
    return out


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__.splitlines()[2].strip())
    path = pathlib.Path(sys.argv[1])
    rows = from_docx(path) if path.suffix.lower() in (".docx", ".dotx") else from_doc(path)
    for level, text in rows:
        print("h%d  %s%s" % (level, "    " * (level - 1), text))
    print("\n-- %d heading(s): %d h1, %d h2"
          % (len(rows), sum(1 for l, _ in rows if l == 1),
             sum(1 for l, _ in rows if l == 2)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
