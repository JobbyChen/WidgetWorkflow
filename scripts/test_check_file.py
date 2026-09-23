#!/usr/bin/env python3
"""Tests for scripts/check_file.py.

    python scripts/test_check_file.py

Every check in check_file.py was added because a defect got past it and a person
spotted it. Nothing verified they keep working: a rule that has been narrowed
one time too many stops firing silently, and the example files still report
0 FAIL, which looks exactly like success.

So each case below is a widget or a sentence with one deliberate defect, and the
test asserts the matching check still reports it. The second half asserts the
opposite: that the real example files produce no label, arrow or source findings,
because a check that fires on correct work is as useless as one that never fires.

Run this after any change to check_file.py.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import check_file as C

ROOT = pathlib.Path(__file__).resolve().parent.parent


class Catch:
    """A Report that keeps what it was told."""

    def __init__(self):
        self.lines = []

    def ok(self, n, m):
        pass

    def skip(self, n, m):
        pass

    def warn(self, n, m):
        self.lines.append(("WARN", n, m))

    def fail(self, n, m):
        self.lines.append(("FAIL", n, m))

    def has(self, level, group, needle):
        return any(l == level and g == group and needle.lower() in m.lower()
                   for l, g, m in self.lines)


PPF = {"axes": {"x": "Q", "y": "P", "xmax": 110, "ymax": 110},
       "curves": [{"id": "D", "label": "D", "pts": [[8, 96], [96, 8]]}]}


def widget(**over):
    cfg = {k: (v[:] if isinstance(v, list) else v) for k, v in PPF.items()}
    cfg.update(over)
    return [(1, cfg, "")]


CASES = []


def case(name, fn):
    CASES.append((name, fn))


# ---- the label test, one case per category it has learned ------------------

case("label sitting on a curve", lambda r: C.check_labels(widget(
    points=[{"q": 50, "p": 50, "label": "E", "dx": 2, "dy": 2}]), r)
    or r.has("FAIL", "labels", "sits on curve"))

case("label overlapping another label", lambda r: C.check_labels(widget(
    points=[{"q": 30, "p": 80, "label": "AAAA", "dx": 10, "dy": 0},
            {"q": 31, "p": 80, "label": "BBBB", "dx": 10, "dy": 0}]), r)
    or r.has("FAIL", "labels", "overlaps"))

case("label sitting on a point", lambda r: C.check_labels(widget(
    points=[{"q": 30, "p": 80, "showP": False, "showQ": False},
            {"q": 60, "p": 40, "label": "X", "dx": -84, "dy": -62,
             "showP": False, "showQ": False}]), r)
    or r.has("FAIL", "labels", "sits on the point"))

case("label sitting on a movement arrow", lambda r: C.check_labels(widget(
    points=[{"q": 50, "p": 50, "label": "E", "dx": 6, "dy": -12,
             "showP": False, "showQ": False}],
    moves=[{"from": [30, 70], "to": [70, 30], "offset": -14}]), r)
    or r.has("FAIL", "labels", "sits on a movement arrow")
    or r.has("FAIL", "labels", "sits on the movement"))

case("axis title overlapping a tick", lambda r: C.check_labels(widget(
    axes={"x": "Boxes of Tissues", "y": "P", "xmax": 110, "ymax": 110,
          "xticks": [105], "yticks": [50]}), r)
    or r.has("FAIL", "labels", "axis title"))

case("two axis values crowded together", lambda r: C.check_labels(widget(
    points=[{"q": 50, "p": 50, "showQ": False},
            {"q": 60, "p": 58, "showQ": False}]), r)
    or r.has("WARN", "labels", "crowded"))

case("label pressed against a guide", lambda r: C.check_labels(widget(
    points=[{"q": 50, "p": 50, "label": "E", "dx": -18, "dy": 3}]), r)
    or r.has("WARN", "labels", "close to the guides"))

# ---- the arrow tests -------------------------------------------------------

case("two arrows abutting", lambda r: C.check_labels(widget(
    moves=[{"from": [10, 90], "to": [40, 60], "offset": -15},
           {"from": [40, 60], "to": [70, 30], "offset": -15}]), r)
    or r.has("WARN", "arrows", "read as one arrow"))

case("arrow lying across a curve", lambda r: C.check_labels(widget(
    moves=[{"from": [20, 60], "to": [80, 40], "offset": 0}]), r)
    or r.has("WARN", "arrows", "lies across curve"))

# ---- tick emphasis ---------------------------------------------------------

case("some point values ticked and others not", lambda r: C.check_tick_emphasis(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110, "xticks": [30], "yticks": [50]},
    points=[{"q": 30, "p": 50}, {"q": 70, "p": 50}]), r)
    or r.has("WARN", "ticks", "ticked (plain)"))

# ---- the surplus/shortage arrow rule --------------------------------------

case("surplus walkthrough with no movement arrows", lambda r: C.check_arrows(widget(
    hlines=[{"p": 70}],
    braces=[{"p": 70, "q1": 20, "q2": 80, "label": "Surplus"}],
    steps=["one.", "two."]), r)
    or r.has("FAIL", "arrows", "two movement arrows"))

# The other half of the same rule. A world price is an hline and a trade
# diagram has steps, but the market settles at that price and stays there --
# there is no movement back to equilibrium to draw, so demanding two arrows
# flagged all eight widgets of the trade chapter. The brace is what separates
# the two: a surplus/shortage walkthrough names the gap its price line opens.
# This case fails if that trigger is ever widened back to the price line alone.
case("a world-price line is not a surplus walkthrough", lambda r: C.check_arrows(widget(
    hlines=[{"p": 70, "label": "P\u1d42"}],
    braces=[{"p": 70, "q1": 20, "q2": 80, "label": "Exports"}],
    steps=["one.", "two."]), r)
    or not r.has("FAIL", "arrows", "two movement arrows"))

# ...and the equilibrium-shift widgets, which carry the brace without a line.
case("a Surplus brace with no price line is not a walkthrough",
     lambda r: C.check_arrows(widget(
         braces=[{"p": 70, "q1": 20, "q2": 80, "label": "Surplus"}],
         steps=["one.", "two."]), r)
     or not r.has("FAIL", "arrows", "two movement arrows"))

# ---- the text-box model ----------------------------------------------------

# An area label is the one label the engine centres on its anchor point
# (dominant-baseline:central, v2.13). Modelling it as baseline-anchored like
# every other label put it ~3px high here, which is exactly the margin between
# "centred in the wedge" and "lying across the wedge's edge" -- the $10 tariff
# label rendered 0.7px over its own price line while this file reported PASS.
def _box_centred(r):
    b = C.box(100.0, 50.0, "$10", 11, "middle", vcenter=True)
    mid = (b[1] + b[3]) / 2.0
    return abs(mid - 50.0) < 0.01


def _box_baseline(r):
    b = C.box(100.0, 50.0, "$10", 11, "middle")
    mid = (b[1] + b[3]) / 2.0
    return mid < 50.0 - 2.0          # hangs above the baseline


case("an area label's box is centred on its anchor", _box_centred)
case("every other label's box hangs above its baseline", _box_baseline)

# ---- captions --------------------------------------------------------------

case("'Before -' caption prefix", lambda r: C.check_captions(
    [(1, {"steps": ["Before – the original schedule."]}, "")], r)
    or r.has("FAIL", "caption", "before"))

case("'Price up, quantity up' shorthand", lambda r: C.check_captions(
    [(1, {"steps": ["It settles at $40. Price up, quantity up."]}, "")], r)
    or r.has("FAIL", "caption", "shorthand"))

# ---- the source-word rules, which have been narrowed three times -----------

for txt, tag in [("<p>built from a lecture recording alone.</p>", "a lecture recording"),
                 ("<p>as the transcript shows, demand rises.</p>", "the transcript"),
                 ("<p>he drew it on the board during the review.</p>", "on the board"),
                 ("<p>roughly 20% of the class said otherwise.</p>", "the class said"),
                 ("<p>he explained the model in class last week.</p>", "in class"),
                 ("<p>the professor said demand shifts right.</p>", "the professor said")]:
    case("source: %s" % tag,
         (lambda t: lambda r: C.check_source(t, [], r) or r.has("FAIL", "source", ""))(txt))

for txt, tag in [("<p>the class average was below 74.</p>", "the class average"),
                 ("<p>you may be sitting in class.</p>", "sitting in class"),
                 ("<p>the board of a firm sets the price.</p>", "the board of a firm"),
                 ("<p>one class of goods behaves differently.</p>", "a class of goods"),
                 ("<p>ask your professor which convention applies.</p>", "your professor")]:
    case("not a source: %s" % tag,
         (lambda t: lambda r: C.check_source(t, [], r) or not r.lines)(txt))

case("a named person is flagged, never failed", lambda r: (
    C.check_names("<p>Professor Chen drew the example.</p>", [], r)
    or (r.has("WARN", "names", "professor chen")
        and not any(l == "FAIL" for l, _, _ in r.lines))))

# ---- markup ----------------------------------------------------------------

case("the price-up punchline", lambda r: C.check_captions(widget(
     caption="The market settles at P\u2082 and Q\u2082. Price up, quantity up."), r)
     or r.has("FAIL", "caption", "shorthand"))
case("up or down inside a sentence", lambda r: C.check_captions(widget(
     caption="A surplus pushes the price down toward equilibrium, and the "
             "quantity supplied falls with it."), r)
     or not r.lines)

case("<u> in the body", lambda r: C.check_markup("<body><p>a <u>term</u></p></body>", r)
     or r.has("FAIL", "markup", "<u>"))
case("<h3> in the body", lambda r: C.check_markup("<body><h3>Sub</h3></body>", r)
     or r.has("FAIL", "markup", "<h3>"))
TOC_PAGE = ('<body><details class="toc-box"><nav><ul>'
            '<li><a href="#alpha">Alpha</a></li></ul></nav></details>'
            '<h1 id="alpha">Alpha</h1>')
case("a contents link pointing at no heading", lambda r: C.check_toc(
     TOC_PAGE.replace('id="alpha">Alpha</h1>', 'id="beta">Beta</h1>'), r)
     or r.has("FAIL", "toc", "point at no heading"))
case("a heading missing from the contents", lambda r: C.check_toc(
     TOC_PAGE + '<h1 id="gamma">Gamma</h1>', r)
     or r.has("FAIL", "toc", "missing from the contents"))
case("a heading with no id", lambda r: C.check_toc(
     TOC_PAGE + "<h2>Delta</h2>", r)
     or r.has("FAIL", "toc", "no id"))
case("no table of contents at all", lambda r: C.check_toc(
     "<body><h1 id=\"a\">A</h1>", r)
     or r.has("WARN", "toc", "no table of contents"))
case("a contents block in step with its headings", lambda r: C.check_toc(TOC_PAGE, r)
     or not r.lines)

HEAD_OK = ('<title>The PPF</title>'
           '<link rel="stylesheet" href="https://x/content/sn25-v6.css">'
           '<link href="https://fonts.googleapis.com/css2?family=Red+Hat+Display" rel="stylesheet">'
           '<script src="https://x/content/sn25-v6.js"></script>')
case("the font link placed before the house stylesheet", lambda r: C.check_head(
     HEAD_OK.replace('<link rel="stylesheet" href="https://x/content/sn25-v6.css">', '')
     + '<link rel="stylesheet" href="https://x/content/sn25-v6.css">', r)
     or r.has("WARN", "head", "stylesheet first"))
case("the current house head order", lambda r: C.check_head(HEAD_OK, r)
     or not r.has("WARN", "head", "stylesheet first"))


def main():
    bad = 0
    for name, fn in CASES:
        r = Catch()
        try:
            ok = bool(fn(r))
        except Exception as e:                      # a broken check is a failure
            ok, name = False, "%s (raised %s)" % (name, e)
        print("%-4s %s" % ("ok" if ok else "FAIL", name))
        bad += not ok

    # No check may fire on work that is correct.
    print()
    for f in sorted((ROOT / "examples").glob("*.html")):
        src = f.read_text(encoding="utf-8")
        r = Catch()
        cfgs = C.configs(src, r)
        C.check_labels(cfgs, r)
        C.check_tick_emphasis(cfgs, r)
        C.check_source(src, cfgs, r)
        noise = [m for l, g, m in r.lines if g in ("arrows", "source")]
        # The 9/11 prototype predates v6 and has recorded label failures; its
        # arrow and source lines must still be empty.
        #
        # The efficiency chapter is the exception, and it is a file-level one
        # rather than a narrowing of the rule. Its prose arrived written, with
        # "create the widgets and leave everything else the same", and it
        # carries a box headed "From-the-Book Topics NOT Covered in Class".
        # That is a real rule 4 hit and the checker is right to report it every
        # time the file is checked; whether to reword someone else's heading is
        # Ian's call, the same way a named professor is. Exempting the one
        # sentence here would switch the check off for every file that follows.
        if f.name == "ECO2023-263-AllocativeEfficiency.html":
            noise = [m for m in noise if "Covered in Class" not in m]
        print("%-4s no arrow or source findings in %s" % ("ok" if not noise else "FAIL", f.name))
        for m in noise:
            print("       " + m)
        bad += bool(noise)

    print("\n%d failing" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
