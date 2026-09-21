#!/usr/bin/env python3
"""Every MathType equation in a Word file, as text, in reading order.

    python scripts/doc_formulas.py <the Word file>
    python scripts/doc_formulas.py <the Word file> --check <notes file>

These chapters carry their formulas as MathType OLE objects, not as Word's own
equations: `word/document.xml` has no <m:oMath> at all, just an <w:object> and a
WMF picture of the result. So a formula is invisible to every other reader here
-- pandoc, antiword and catdoc all skip it, and `doc_headings.py` never looks --
and the only way anyone had read one was to squint at the rendering and retype
it. That is how `OC_X = ` lost its left-hand side: the fraction was transcribed
and the thing it equals was not.

The WMF is a picture, but MathType draws the glyphs with real TextOut records,
so the words survive inside it. This pulls them out in drawing order, which puts
the numerator before the denominator and the left-hand side where MathType
happened to emit it -- readable, not typeset. Subscripts and superscripts arrive
as their own runs, so `E_D` reads as `E ⟨/⟩ D`: enough to check a formula
against, never enough to paste.

With --check it also reports which of those words are missing from a notes
file's LaTeX, which catches a dropped left-hand side without anyone rereading
the chapter.
"""

import argparse
import glob
import io
import os
import pathlib
import re
import struct
import sys
import zipfile

TEXTOUT, EXTTEXTOUT = 0x0521, 0x0A32


def wmf_records(data):
    off = 22 if data[:4] == b"\xd7\xcd\xc6\x9a" else 0   # placeable header
    off += 18                                            # METAHEADER
    while off + 6 <= len(data):
        size, func = struct.unpack_from("<IH", data, off)
        if size == 0:
            break
        yield func, data[off + 6: off + size * 2]
        off += size * 2


def wmf_text(data):
    """The glyph runs MathType drew, in the order it drew them."""
    out = []
    for func, p in wmf_records(data):
        try:
            if func == EXTTEXTOUT:
                n = struct.unpack_from("<hhh", p, 0)[2]
                opts = struct.unpack_from("<H", p, 6)[0]
                start = 8 + (8 if opts & 0x0006 else 0)
                out.append(p[start:start + n].decode("latin-1"))
            elif func == TEXTOUT:
                n = struct.unpack_from("<h", p, 0)[0]
                out.append(p[2:2 + n].decode("latin-1"))
        except Exception:
            pass                      # a record we do not model is not a formula
    return [s for s in out if s.strip()]


def equations(docx):
    """(picture name, the paragraph's own text, glyph runs) in reading order."""
    z = zipfile.ZipFile(docx)
    rels = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="media/([^"]+)"',
                           z.read("word/_rels/document.xml.rels").decode("utf-8")))
    doc = z.read("word/document.xml").decode("utf-8")
    seen, out = set(), []
    for m in re.finditer(r"<w:p\b[^>]*>(?:(?!<w:p\b).)*?</w:p>", doc, re.S):
        body = m.group(0)
        txt = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", body))
        for rid in re.findall(r'r:id="(rId\d+)"', body):
            name = rels.get(rid, "")
            if name.endswith(".wmf"):
                seen.add(name)
                out.append((name, txt.strip(),
                            wmf_text(z.read("word/media/" + name))))
    # A formula inside a floating text box sits in a nested <w:p> the scan above
    # steps over, and those boxes are where the exam tips live. Sweep the rest.
    for name in sorted(set(n for n in z.namelist() if n.endswith(".wmf")),
                       key=lambda n: int(re.search(r"\d+", os.path.basename(n)).group())):
        base = os.path.basename(name)
        if base not in seen:
            out.append((base, "(in a text box)", wmf_text(z.read(name))))
    return out


WORD = re.compile(r"[A-Za-z]{2,}")
# MathType writes adjacent glyph runs with nothing between them, so a run comes
# back as "YouGain", "ofUnits" or "SlopeQ". Splitting where a lower-case letter
# meets an upper-case one recovers the words without inventing any.
JOIN = re.compile(r"(?<=[a-z])(?=[A-Z])")


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("doc", type=pathlib.Path)
    ap.add_argument("--check", type=pathlib.Path, metavar="NOTES",
                    help="report words these equations use that the notes file's LaTeX does not")
    a = ap.parse_args()

    if a.doc.suffix.lower() != ".docx":
        print("%s: only .docx carries its equations where this can reach them; a "
              ".doc must be converted first" % a.doc, file=sys.stderr)
        return 2

    eqs = equations(a.doc)
    if not eqs:
        print("%s: no MathType equations" % a.doc)
        return 0

    paras = []
    if a.check:
        src = io.open(a.check, encoding="utf-8").read()
        # Every paragraph that carries a fraction, tags stripped -- not just the
        # LaTeX inside the delimiters. The worked examples put the left-hand
        # side in HTML (OC<sub>Lego Sets</sub> = \(...\)), so reading only the
        # math would report every one of them as missing its own name.
        paras = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", m.group(1))).lower()
                 for m in re.finditer(r"<p\b[^>]*>(.*?)</p>", src, re.S)
                 if "frac" in m.group(1)]

    miss_total = 0
    for name, txt, runs in eqs:
        print("%-14s %s" % (name, "  ⟨/⟩  ".join(runs)))
        if txt:
            print("%-14s   in: %s" % ("", txt[:96]))
        if a.check:
            words = sorted(set(w.lower() for r in runs
                               for part in JOIN.split(r)
                               for w in WORD.findall(part)
                               if len(set(w)) > 1))   # "PP" is P and P, not a word
            # Score each formula paragraph against this equation and check the
            # best one. A whole-file bag of words cannot see a dropped left-hand
            # side: "OC" is in the file a dozen times over, so the one equation
            # that lost it still matches.
            best = max(paras, key=lambda t: sum(w in t for w in words),
                       default="")
            miss = [w for w in words if w not in best]
            if miss:
                miss_total += len(miss)
                print("%-14s   NOT IN %s: %s"
                      % ("", a.check.name, ", ".join(miss)))
        print()

    print("-- %d equation(s)%s" % (len(eqs),
          ", %d word(s) not found in the notes file" % miss_total if a.check
          else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
