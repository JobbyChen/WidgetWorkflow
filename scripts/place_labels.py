#!/usr/bin/env python3
"""Put every shaded area's label where it is clear, and centred.

    python scripts/place_labels.py notes.html            # report
    python scripts/place_labels.py notes.html --apply    # write the lp values in

An area label defaults to its polygon's centroid, which is right until a curve,
a guide, a price line or another label happens to run through that point. Then
it has to move, and moving it by eye is how labels end up looking deliberate
but wrong -- the importer's "Gain" sat left of its own wedge for a whole
revision because the spot dead-centre had been clear all along.

So: search the polygon on a grid, keep every candidate that collides with
nothing, and take the one NEAREST the centroid. If nothing inside is clear --
a deadweight wedge can be a dozen pixels across -- widen to a ring just outside
the shape, which is what the printed artwork does with its own slivers.

Scoring calls check_file's geometry directly rather than re-running the whole
file's checks per candidate, which is the difference between seconds and
minutes, and it means this script and the checker can never disagree.
"""

import argparse
import copy
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_file as C


class Catch:
    def __init__(self):
        self.lines = []

    def ok(self, n, m):
        pass

    def skip(self, n, m):
        pass

    def warn(self, n, m):
        self.lines.append(m)

    def fail(self, n, m):
        self.lines.append(m)


def inside(pts, q, p):
    n, ins = len(pts), False
    for i in range(n):
        x1, y1 = pts[i]
        x2, y2 = pts[(i + 1) % n]
        if (y1 > p) != (y2 > p):
            if x1 + (p - y1) * (x2 - x1) / float(y2 - y1) > q:
                ins = not ins
    return ins


SENTINEL = "❖❖"          # same everywhere, so two CS areas never score each other


def findings_for(widget, scn_label):
    r = Catch()
    try:
        C.check_labels([(1, widget, "")], r)
    except Exception:
        return 1
    return sum(1 for m in r.lines
               if SENTINEL in m and (not scn_label or "(%s)" % scn_label in m))


def slots(w):
    if w.get("scenarios"):
        return [(k, v.get("label"), v) for k, v in w["scenarios"].items()]
    return [(None, None, w)]


def best_lp(widget, key, scn_label, ai, area, steps=26):
    pts = area["pts"]
    qs = [x[0] for x in pts]
    ps = [x[1] for x in pts]
    cq = sum(qs) / float(len(qs))
    cp = sum(ps) / float(len(ps))
    for grow in (1.0, 2.6):
        best = None
        lo_q, hi_q = cq - (cq - min(qs)) * grow, cq + (max(qs) - cq) * grow
        lo_p, hi_p = cp - (cp - min(ps)) * grow, cp + (max(ps) - cp) * grow
        for i in range(1, steps):
            for j in range(1, steps):
                q = lo_q + (hi_q - lo_q) * i / float(steps)
                p = lo_p + (hi_p - lo_p) * j / float(steps)
                within = inside(pts, q, p)
                if (grow == 1.0) != within:
                    continue
                trial = copy.deepcopy(widget)
                tgt = trial["scenarios"][key] if key else trial
                tgt["areas"][ai]["lp"] = [round(q, 2), round(p, 2)]
                tgt["areas"][ai]["label"] = SENTINEL
                if findings_for(trial, scn_label):
                    continue
                d = ((q - cq) / max(1e-9, max(qs) - min(qs))) ** 2 + \
                    ((p - cp) / max(1e-9, max(ps) - min(ps))) ** 2
                if best is None or d < best[0]:
                    best = (d, round(q, 2), round(p, 2))
        if best:
            return best[1], best[2], grow > 1.0
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("--apply", action="store_true", help="write the lp values back")
    a = ap.parse_args()

    path = pathlib.Path(a.file)
    src = path.read_text(encoding="utf-8")
    r = Catch()
    cfgs = C.configs(src, r)
    out, moved, stuck = src, 0, 0

    for idx, cfg, body in cfgs:
        raw = C.JSON_RE.findall(body)
        if not raw:
            continue
        before = raw[0]
        changed = False
        for key, scn_label, panel in slots(cfg):
            for ai, area in enumerate(panel.get("areas") or []):
                if not area.get("label"):
                    continue
                probe = copy.deepcopy(cfg)
                tgt = probe["scenarios"][key] if key else probe
                tgt["areas"][ai]["label"] = SENTINEL
                if not findings_for(probe, scn_label):
                    continue           # already clear where it is
                got = best_lp(cfg, key, scn_label, ai, area)
                where = "widget %d%s %r" % (idx, " (%s)" % scn_label if scn_label else "",
                                            area["label"])
                if not got:
                    stuck += 1
                    print("  %-42s no clear spot -- drop the label and name it "
                          "in the caption" % where)
                    continue
                q, p, outside = got
                area["lp"] = [q, p]
                changed = moved = True
                print("  %-42s lp [%s, %s]%s" % (where, q, p, "  (beside the shape)"
                                                 if outside else ""))
        if changed:
            out = out.replace(before, json.dumps(cfg, indent=1, ensure_ascii=False))

    if not moved and not stuck:
        print("every area label is already clear and centred")
    if a.apply and moved:
        path.write_text(out, encoding="utf-8")
        print("\nwritten to %s -- re-run embed_engine.py if the engine was touched" % path)
    elif moved:
        print("\n(report only; pass --apply to write these in)")
    return 1 if stuck else 0


if __name__ == "__main__":
    sys.exit(main())
