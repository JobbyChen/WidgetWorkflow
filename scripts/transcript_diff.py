#!/usr/bin/env python3
"""Which of a widget file's numbers and goods a transcript still supports.

    python scripts/transcript_diff.py examples/ECO2013-263-SupplyAndDemand.html t1.txt t2.txt
    python scripts/transcript_diff.py <file> <transcript>... --quiet   # only what is unsupported

A semester swap (prompt v6 mode d) is meant to change chart titles, axis titles
and values and leave the rest alone. Deciding which of those three actually
changed meant rereading every config against the new transcript by hand, which
is slow and, worse, easy to get wrong in the direction that ships a stale
number.

This does the mechanical half. For every widget it separates the numbers a
reader sees -- axis ticks, schedule rows, the prices a guide or brace is drawn
at -- from the coordinates that only place a curve, and reports which of the
first kind the transcripts state. Curve coordinates are listed apart and never
counted, because a line through two stated points needs endpoints nobody ever
said aloud; counting those buries the one number that matters. A symbolic
widget has no values at all: its 110-scale coordinates are a drawing
convention, so only its names are checked. Titles, axis titles and curve labels
are checked by the nouns they name.

Read the output as a question, never as an instruction. An UNSUPPORTED value
means the transcripts do not state it, which is either a value this semester
changed or one the notes prose carried instead -- the tool cannot tell those
apart, and CLAUDE.md rule 3 says a number comes from the source, so an
unsupported value is a thing to go look up, not a thing to edit. A file whose
values and names are all stated is a file these transcripts do not change.

Matching is deliberately loose: a number counts as stated if it appears as
digits anywhere in the transcript, spelled out, or written with a thousands
separator. Loose matching over-reports support, so a number that still comes
back unsupported is worth trusting.
"""

import argparse
import io
import json
import pathlib
import re
import sys

BLOCK = re.compile(r'(<script type="application/json">\n)(.*?)(\n</script>)', re.S)

ONES = ("zero one two three four five six seven eight nine ten eleven twelve "
        "thirteen fourteen fifteen sixteen seventeen eighteen nineteen").split()
TENS = {20: "twenty", 30: "thirty", 40: "forty", 50: "fifty",
        60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"}

# Words a title or label shares with every other title, so naming one proves
# nothing about which good a widget is about.
STOP = set("""a an the and or of for in on at to from with without by as is are was
were be been this that these those it its their there here what which when how
why not no than then so if but all any both each more most other some such only
own same too very can will just per every into over under up down left right
market markets price prices quantity quantities demand supply demanded supplied
curve curves shift shifts shifting shifted increase increases increased decrease
decreases decreased change changes changed equilibrium new original point points
schedule table graph widget step steps example examples case cases pick through
before after now still goods good service services firm firms consumer consumers
buy buys buying sell sells selling make makes making one two three four five""".split())


def spell(n):
    """A small set of English spellings for n, or () if we do not spell it."""
    if n < 0 or n != int(n):
        return ()
    n = int(n)
    if n < 20:
        return (ONES[n],)
    if n < 100:
        t, o = divmod(n, 10)
        base = TENS[t * 10]
        return (base,) if not o else (base + " " + ONES[o], base + "-" + ONES[o])
    return ()


def stated(value, hay):
    """Does the transcript text `hay` state this number, loosely?"""
    if value == int(value):
        n = int(value)
        forms = ["%d" % n]
        if n >= 1000:
            forms.append("{:,}".format(n))
        forms.extend(spell(n))
    else:
        forms = [("%g" % value), ("%.2f" % value)]
    return any(re.search(r"(?<![\d.])" + re.escape(f) + r"(?![\d])", hay)
               for f in forms)


def collect(node, out, tier="value"):
    """Split the numbers into what a reader sees and what only places a curve.

    `out` is {"value": [...], "draw": [...]}. Axis maxima, label nudges, arrow
    placement and step wiring are neither: they are headroom and bookkeeping the
    source never states, so they are dropped rather than reported as
    unsupported.
    """
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("at", "until", "ldx", "ldy", "lstart", "xmax", "ymax",
                     "arrowP", "offset", "marker", "moves", "lq", "lp", "opacity"):
                continue
            elif k == "pts":
                collect(v, out, "draw")
            elif k in ("xticks", "yticks", "rows", "hlines", "guides"):
                collect(v, out, "value")
            else:
                collect(v, out, tier)
    elif isinstance(node, list):
        for item in node:
            collect(item, out, tier)
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        out[tier].append(node)


def words(node, out):
    """The nouns a widget's title, axis titles and curve labels name."""
    if isinstance(node, dict):
        for k, v in node.items():
            if k in ("title", "label", "heading") and isinstance(v, str):
                out.extend(re.findall(r"[A-Za-z][A-Za-z'-]{2,}", v.lower()))
            elif k in ("x", "y") and isinstance(v, str):
                out.extend(re.findall(r"[A-Za-z][A-Za-z'-]{2,}", v.lower()))
            elif k == "cols" and isinstance(v, list):
                for c in v:
                    if isinstance(c, str):
                        out.extend(re.findall(r"[A-Za-z][A-Za-z'-]{2,}", c.lower()))
            else:
                words(v, out)
    elif isinstance(node, list):
        for item in node:
            words(item, out)


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", type=pathlib.Path)
    ap.add_argument("transcript", type=pathlib.Path, nargs="+")
    ap.add_argument("--quiet", action="store_true",
                    help="list only what the transcripts do not state")
    a = ap.parse_args()

    hay = "\n".join(io.open(t, encoding="utf-8", errors="replace").read()
                    for t in a.transcript)
    flat = re.sub(r"\s+", " ", hay).lower()
    src = io.open(a.file, encoding="utf-8").read()

    tot_v = tot_vs = tot_w = tot_wu = 0
    for n, m in enumerate(BLOCK.finditer(src), 1):
        body = m.group(2)
        cfg = json.loads(body)
        # No ticks and P1/Q1 labels means a symbolic graph: its coordinates are
        # the engine's 110-scale convention, and rule 3 says they are what you
        # draw precisely BECAUSE the source states no numbers.
        symbolic = not re.search(r'"[xy]ticks"', body) or bool(re.search(r'"[pq]l"', body))
        bins, wds = {"value": [], "draw": []}, []
        collect(cfg, bins)
        words(cfg, wds)
        vals = [] if symbolic else sorted(set(x for x in bins["value"] if x != 0))
        draw = [] if symbolic else sorted(set(x for x in bins["draw"] if x != 0) - set(vals))
        wds = sorted(set(w for w in wds if w not in STOP))

        miss_v = [x for x in vals if not stated(x, flat)]
        miss_d = [x for x in draw if not stated(x, flat)]
        miss_w = [w for w in wds if w not in flat and w.rstrip("s") not in flat]
        tot_v += len(vals); tot_vs += len(vals) - len(miss_v)
        tot_w += len(wds); tot_wu += len(wds) - len(miss_w)

        if a.quiet and not miss_v and not miss_w:
            continue
        title = (cfg.get("title") or cfg.get("lede") or "").strip()
        print("w%-2d %s" % (n, title[:78]))
        print("    values   %s%s"
              % ("none -- symbolic graph" if symbolic
                 else "%d/%d stated" % (len(vals) - len(miss_v), len(vals)),
                 "   UNSUPPORTED: " + ", ".join("%g" % x for x in miss_v)
                 if miss_v else ""))
        print("    names    %d/%d stated%s"
              % (len(wds) - len(miss_w), len(wds),
                 "   UNSUPPORTED: " + ", ".join(miss_w) if miss_w else ""))
        if miss_d and not a.quiet:
            print("    (curve coordinates not stated, as expected: %s)"
                  % ", ".join("%g" % x for x in miss_d[:12]))

    print("\n-- %d/%d values and %d/%d names stated across the transcripts"
          % (tot_vs, tot_v, tot_wu, tot_w))
    if tot_vs == tot_v and tot_wu == tot_w:
        print("-- nothing in this file is unsupported: these transcripts do not change it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
