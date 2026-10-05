#!/usr/bin/env python3
"""Nudge every curve label that collides onto the nearest clear spot.

    python scripts/place_curve_labels.py notes.html            # report
    python scripts/place_curve_labels.py notes.html --apply    # write ldx/ldy in

Area labels have had `place_labels.py` since the trade chapter; curve labels
have not, and they are the ones that actually keep failing. A curve label sits
at its own end, which is exactly where the other curves converge: MR ends on
the Q axis with MC a few units above it, so the label has the axis line below
and another curve above and about nine pixels of room between them. Guessing
ldx/ldy there costs a render each time and usually trades one collision for
another -- MR came off MC and onto the axis on the first try.

So: score candidate offsets against check_file's own geometry, the way
place_labels does, and take the clear one nearest the engine's default. The
two can never disagree about the same drawing, and a search is 0.3s where a
round of eyeballing is a 30s render plus a look.

A label with nowhere clear to go is reported, not moved: that is a drawing to
change -- run the curve further, or anchor the label at its other end with
`lstart` -- and not something an offset can fix.
"""

import argparse
import copy
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_file as C
from place_labels import Catch, sentinel, slots

# A finding names the label that is out of place, then what it ran into --
# and what it ran into is often another label. Counting every finding that
# merely mentions the stand-in therefore blamed the label being scored for
# its neighbour's collision, and reported "nowhere clear" for a label that was
# never the problem. Only the subject counts.
# Every phrasing check_file uses between a label and what it ran into.
# " is crowded against" was missing, so a crowding WARN never had its
# subject trimmed: the whole message was tested, the stand-in matched
# wherever it appeared in it, and the label being scored was blamed for
# its neighbour's collision at every offset -- including the ones that
# would have cleared it. The one finding the placer exists to fix was
# the one it could not act on.
VERBS = (" sits on", " is close to", " overlaps", " is crowded against")


def findings_for(widget, mark, scn_label):
    r = Catch()
    try:
        C.check_labels([(1, widget, "")], r)
    except Exception:
        return 1
    n = 0
    for m in r.lines:
        if scn_label and "(%s)" % scn_label not in m:
            continue
        subject = m
        for v in VERBS:
            subject = subject.split(v)[0]
        # A finding prints the label with %r, so a wrapped one arrives with a
        # literal backslash-n where the stand-in has a real newline and never
        # matches. Every multi-line label then scored zero findings and every
        # placement for it came back clear.
        if mark in subject or repr(mark)[1:-1] in subject:
            n += 1
    return n


# Far enough to clear a neighbouring curve, near enough to still read as this
# curve's name. The engine's own defaults are +6 across and a few pixels up.
OFFSETS = [0, 4, -4, 8, -8, 12, -12, 16, -16, 20, -20, 26, -26, 32, -32,
           40, -40, 48, -48, 56, -56, 64, -64, 72, -72, 80, -80]
# The grid used to stop at 32px, which is fine for a label nudged off a
# neighbour but not for one that has to come inboard: a curve running to the
# right-hand edge of the plot leaves "D = MB = MSB" hanging 50px past the
# panel, and the only clear spot is well back along the curve. The score still
# prefers the smallest offset, so a label that fits close by stays close by.


def best_offset(widget, key, scn_label, ci, curve):
    """The clear (ldx, ldy) nearest the default, or None if there is none."""
    mark = sentinel(curve["label"])
    best = None
    for dx in OFFSETS:
        for dy in OFFSETS:
            trial = copy.deepcopy(widget)
            tgt = trial["scenarios"][key] if key else trial
            c = tgt["curves"][ci]
            c["label"], c["ldx"], c["ldy"] = mark, dx, dy
            if findings_for(trial, mark, scn_label):
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, dx, dy)
    return best[1:] if best else None


def panels_of(cfg):
    """Every panel of a widget, with a name for reporting."""
    for key, scn_label, target in slots(cfg):
        if target.get("panels"):
            for pi, pan in enumerate(target["panels"]):
                yield key, scn_label, pi, pan
        else:
            yield key, scn_label, None, target


def main():
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--apply", action="store_true",
                    help="write the ldx/ldy values back")
    a = ap.parse_args()

    path = pathlib.Path(a.file)
    src = path.read_text(encoding="utf-8")
    r = Catch()
    out, moved, stuck = src, 0, 0

    for idx, cfg, body in C.configs(src, r):
        raw = C.JSON_RE.findall(body)
        if not raw:
            continue
        before, changed = raw[0], False
        for key, scn_label, pi, panel in panels_of(cfg):
            for ci, curve in enumerate(panel.get("curves") or []):
                label = curve.get("label")
                if not label:
                    continue
                probe = copy.deepcopy(cfg)
                tgt = probe["scenarios"][key] if key else probe
                pan = tgt["panels"][pi] if pi is not None else tgt
                pan["curves"][ci]["label"] = sentinel(label)
                if not findings_for(probe, sentinel(label), scn_label):
                    continue                      # already clear
                where = "widget %d%s%s %r" % (
                    idx,
                    " (%s)" % scn_label if scn_label else "",
                    " panel %d" % (pi + 1) if pi is not None else "",
                    label)
                got = best_offset(cfg if pi is None else panel,
                                  key if pi is None else None,
                                  scn_label, ci, curve)
                if not got:
                    stuck += 1
                    print("  %-44s nowhere clear -- run the curve further, or "
                          "anchor the label at its other end with lstart" % where)
                    continue
                curve["ldx"], curve["ldy"] = got
                changed = True
                moved += 1
                print("  %-44s ldx %s, ldy %s" % (where, got[0], got[1]))
        if changed:
            out = out.replace(before, json.dumps(cfg, indent=1,
                                                 ensure_ascii=False))

    if not moved and not stuck:
        print("every curve label is already clear")
    if a.apply and moved:
        path.write_text(out, encoding="utf-8")
        print("\nwritten to %s" % path)
    elif moved:
        print("\n(report only; pass --apply to write these in)")
    return 1 if stuck else 0


if __name__ == "__main__":
    sys.exit(main())
