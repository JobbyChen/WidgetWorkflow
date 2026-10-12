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

    def take(self, other):
        self.lines.extend(other.lines)
        return False

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

# ---- steps and what is on screen -------------------------------------------

# A label is only tested against what shares a step with it. The curve, arrow
# and point loops used to skip this check, so a walkthrough was flagged against
# the curve its next step replaces -- a collision never drawn and impossible to
# fix. Both directions matter: the same overlap in a shared step must still fail.
case("label over a curve that is gone by then", lambda r: C.check_labels(widget(
    curves=[{"id": "D1", "label": "D\u2081", "pts": [[0, 100], [100, 0]], "until": 1},
            {"id": "S", "label": "S", "pts": [[0, 0], [100, 100]]}],
    braces=[{"p": 50, "q1": 20, "q2": 80, "label": "Shortage of 400", "below": "in", "at": 3}],
    steps=["a.", "b.", "c.", "d."]), r)
    or not r.has("FAIL", "labels", "sits on curve D\u2081"))

case("label over a curve that is still there", lambda r: C.check_labels(widget(
    curves=[{"id": "D1", "label": "D\u2081", "pts": [[0, 100], [100, 0]]},
            {"id": "S", "label": "S", "pts": [[0, 0], [100, 100]]}],
    braces=[{"p": 50, "q1": 20, "q2": 80, "label": "Shortage of 400", "below": "in", "at": 3}],
    steps=["a.", "b.", "c.", "d."]), r)
    or r.has("FAIL", "labels", "sits on curve D\u2081"))

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

# A price control opens the same gap and never closes it: the price is held
# there by law, so nothing moves back and there are no arrows to demand. This
# fires on every ceiling, floor and minimum-wage figure if the rule keys on the
# gap alone -- a named line (tag) is what marks a policy rather than a passing
# disequilibrium price.
case("a named control price is not a surplus walkthrough", lambda r: C.check_arrows(widget(
    hlines=[{"p": 70, "tag": "Price floor"}],
    braces=[{"p": 70, "q1": 20, "q2": 80, "label": "Surplus of 75"}],
    steps=["one.", "two."]), r)
    or not r.has("FAIL", "arrows", "two movement arrows"))

# ...and the equilibrium-shift widgets, which carry the brace without a line.
case("a Surplus brace with no price line is not a walkthrough",
     lambda r: C.check_arrows(widget(
         braces=[{"p": 70, "q1": 20, "q2": 80, "label": "Surplus"}],
         steps=["one.", "two."]), r)
     or not r.has("FAIL", "arrows", "two movement arrows"))

# ---- place_labels agrees with this file ------------------------------------

# place_labels.py scores candidate positions by swapping the label for a marker
# and asking check_labels. The marker has to be the same LENGTH as the label it
# stands in for, because a text box is measured from its character count: a
# 2-character marker standing in for "DWL" passed a position that this file then
# failed, which is the two of them disagreeing about the same drawing.
def _sentinel_width(r):
    import place_labels as P
    return all(len(P.sentinel(x)) == len(x) for x in ("CS", "DWL", "Revenue", "Gain"))


case("place_labels measures a label at its own width", _sentinel_width)

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

# ---- duplicated guides ------------------------------------------------------
case("two guides down one quantity", lambda r: C.check_controls(widget(
    points=[{"q": 40, "p": 70, "guides": "q"}, {"q": 40, "p": 30, "guides": "q"}]), r)
    or r.has("WARN", "controls", "two guides run down"))

# A point on the axis has a vertical leg of zero length. Counting it flagged
# the endpoint of a frontier against the point above it in shipped work.
case("a point on the axis draws no second guide", lambda r: C.check_controls(widget(
    points=[{"q": 200, "p": 0, "label": "B"}, {"q": 200, "p": 400, "label": "E"}]), r)
    or not r.has("WARN", "controls", "two guides run down"))

case("one guide down each quantity", lambda r: C.check_controls(widget(
    points=[{"q": 40, "p": 70, "guides": "q"}, {"q": 60, "p": 30, "guides": "q"}]), r)
    or not r.has("WARN", "controls", "two guides run down"))

case("a guide running to a blank spot on the price axis", lambda r: C.check_controls(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110, "xticks": [40], "yticks": [70]},
    points=[{"q": 40, "p": 55, "guides": "p", "showP": False}]), r)
    or r.has("FAIL", "controls", "nothing written there"))

# ...and a point that carries its own name is identified without one: the
# guide leads the eye to "C" or "E2", which is how a symbolic figure marks a
# position. Every PPF point in shipped work is drawn that way.
case("a guide to a named point is fine", lambda r: C.check_controls(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110, "xticks": [40], "yticks": [70]},
    points=[{"q": 40, "p": 55, "label": "C", "showP": False, "showQ": False}]), r)
    or not r.has("FAIL", "controls", "nothing written there"))

case("a guide whose value is a tick is fine", lambda r: C.check_controls(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110, "xticks": [40], "yticks": [55]},
    points=[{"q": 40, "p": 55, "guides": "p", "showP": False}]), r)
    or not r.has("FAIL", "controls", "nothing written there"))

# A bare drawing still has to say what it is...
case("a widget with no caption and no steps", lambda r: C.check_schema(widget(), r)
     or r.has("FAIL", "schema", "neither steps"))

# ...but titled scenario buttons do say it, which is the shape a widget takes
# when the prose above it already explains the comparison.
case("titled scenarios need no caption", lambda r: C.check_schema(
    [(1, {"scenarios": {"a": {"label": "A", "title": "The first case"},
                        "b": {"label": "B", "title": "The second case"}}}, "")], r)
    or not r.has("FAIL", "schema", "neither steps"))

# ---- a caption against the prose above it ----------------------------------

_PROSE = ('<p>The demand curve shows the same information as the schedule, but '
          'graphically. Price goes on the vertical axis and quantity demanded '
          'on the horizontal axis.</p><div class="sdg"><script '
          'type="application/json">%s</script></div>')

# A figure introducing a worked question is followed by its answer, and the
# answer restates what the drawing shows.
_PROSE_AFTER = ('<div class="sdg"><script type="application/json">%s</script>'
                '</div><p>The equilibrium quantity is the one for which the '
                'quantity demanded equals the quantity supplied. Total surplus '
                'is maximized there. In the diagram the equilibrium price is '
                '$400 and the equilibrium quantity is 600 units.</p>')


def _prose_case(caption, shell=None):
    import json
    src = (shell or _PROSE) % json.dumps({"caption": caption})
    r = Catch()
    C.check_caption_prose(src, C.configs(src, Catch()), r)
    return r


# restating the paragraph above costs vertical space and adds nothing
case("a caption that restates the prose above it", lambda r: r.take(_prose_case(
    "The demand curve shows the same information as the schedule but "
    "graphically, with price on the vertical axis and quantity demanded on "
    "the horizontal axis."))
    or r.has("WARN", "prose", "already in the prose around it"))

# ...but one reading values off the drawing shares that vocabulary and is
# still the only place the values appear
case("a caption carrying numbers the prose lacks", lambda r: r.take(_prose_case(
    "At $15 only 6 drinks are demanded; as the price falls to $3, the "
    "quantity demanded rises to 65."))
    or not r.has("WARN", "prose", "already in the prose around it"))

case("a caption restated by the answer below it", lambda r: r.take(_prose_case(
    "The quantity demanded equals the quantity supplied at a rent of $400, "
    "where 600 apartments are let. That is the quantity at which total "
    "surplus is as large as it can be.", _PROSE_AFTER))
    or r.has("WARN", "prose", "already in the prose around it"))

# The engine's header comment quotes <div class="sdg"> verbatim, so a raw scan
# for the opening tag finds one widget too many and reads the prose belonging
# to the one before. Both prose checks locate widgets by their own body now.
# The matching paragraph sits beside the real widget and four paragraphs away
# from the decoy, so a scan that finds the decoy first reads filler and stays
# silent -- which is exactly how the shift hid itself.
_FILL = ("<p>Governments sometimes intervene in markets for reasons that have "
         "nothing to do with efficiency.</p>"
         "<p>Whether they succeed depends on how buyers and sellers respond "
         "afterwards.</p>")
_DECOY = (_FILL
          + '<script>/* Markup: <div class="sdg">...config...</div> */</script>'
          + _FILL + _PROSE)

case("a restating caption found past the engine's own markup comment",
     lambda r: r.take(_prose_case(
         "The demand curve shows the same information as the schedule but "
         "graphically, with price on the vertical axis and quantity demanded "
         "on the horizontal axis.", _DECOY))
     or r.has("WARN", "prose", "already in the prose around it"))


# ---- calcs: working the chapter prints itself ------------------------------

def _calcs_case(line, prose):
    import json
    src = ('<div class="sdg"><script type="application/json">%s</script></div>'
           '<p>%s</p>' % (json.dumps({"calcs": [line]}), prose))
    r = Catch()
    C.check_calcs(src, C.configs(src, Catch()), r)
    return r


case("working the chapter reprints as text", lambda r: r.take(_calcs_case(
    "TS = CS + PS = $150,000 + $90,000 = $240,000",
    r"Before the ceiling: \(TS = CS + PS = \$150,000 + \$90,000 = \$240,000\)"))
    or r.has("FAIL", "calcs", "printed again as prose"))

# ...but a chapter formula that merely contains this line's answer is not the
# same working. "TS = CS + PS = $173,333.33 + $40,000" holds the token CS and
# the total, while the trapezoid split that produced it appears nowhere.
# prose that states the result by name is worth a look, though not a failure
case("working the prose states in words", lambda r: r.take(_calcs_case(
    "Vertical intercept = Income ÷ P_B = $10 ÷ $0.50 = 20 loaves",
    "We can graph this budget line. The vertical intercept is 20 loaves of "
    "bread, which is how much bread the consumer could buy."))
    or r.has("WARN", "calcs", "states"))

case("working whose answer alone appears in a different formula",
     lambda r: r.take(_calcs_case(
         "CS = $66,666.67 + $106,666.67 = $173,333.33",
         r"After the ceiling: \(TS = CS + PS = \$173,333.33 + \$40,000 = "
         r"\$213,333.33\)"))
     or not r.has("FAIL", "calcs", "printed again as prose"))


# ---- the engine ------------------------------------------------------------

# a chapter with no graphs needs no engine, but one with a widget in it does
case("no engine in a file that has a widget", lambda r: C.check_engine(
    '<div class="sdg"><script type="application/json">{}</script></div>', r)
    or r.has("FAIL", "engine", "no <!--SDG-ENGINE--> placeholder"))

case("no engine in a file with no widget", lambda r: C.check_engine(
    "<h1>Cardinal Utility</h1><p>No graphs in this chapter.</p>", r)
    or not r.has("FAIL", "engine", "no <!--SDG-ENGINE--> placeholder"))


# a curve that runs down to the axis parks its label on it -- rule 5 lists the
# axis lines beside curves, so this fails rather than warns
case("curve label sitting on the Q axis", lambda r: C.check_labels(widget(
    curves=[{"id": "D", "label": "IC₁", "pts": [[10, 90], [100, 2]],
             "curved": True, "ldy": 14}]), r)
    or r.has("FAIL", "labels", "sits on the axis lines"))


# a subscript run is drawn at .72em and its braces are markup, so a label
# carrying one measures narrower than its raw string
def _sub_width(r):
    wide = C.box(0, 0, "S_George", 13)[2]
    sub = C.box(0, 0, "S_{George}", 13)[2]
    if not (C.box(0, 0, "S", 13)[2] < sub < wide):
        r.fail("labels", "a subscripted label measures %s, not between %s and %s"
               % (sub, C.box(0, 0, "S", 13)[2], wide))
    return r.has("FAIL", "labels", "measures")


case("a subscripted label is not measured at full width",
     lambda r: not _sub_width(r))


# ---- class dates -----------------------------------------------------------

_DATED = ('<p class="date">Tuesday, 9/22/26</p><h1>Culture</h1><p>Body.</p>'
          '<p class="date">Wednesday, 9/23/26</p><h2>Banking</h2>')


def _dates_case(src, source=None):
    r = Catch()
    C.check_dates(src, r, source)
    return r


# a condensed edition keeps the content and silently loses the dates, because
# they carry none of it
case("a class date the source has and the file does not", lambda r: r.take(
    _dates_case('<h1>Culture</h1><p>Body.</p><h2>Banking</h2>', _DATED))
    or r.has("FAIL", "dates", "does not carry it"))

case("every class date carried over", lambda r: r.take(
    _dates_case(_DATED, _DATED))
    or not r.has("FAIL", "dates", "does not carry it"))

case("a file with no class date at all", lambda r: r.take(
    _dates_case('<h1>Culture</h1><p>Body.</p>'))
    or r.has("WARN", "dates", "no <p class=\"date\"> line"))


# ---- captions --------------------------------------------------------------

case("'Before -' caption prefix", lambda r: C.check_captions(
    [(1, {"steps": ["Before – the original schedule."]}, "")], r)
    or r.has("FAIL", "caption", "before"))

case("'Price up, quantity up' shorthand", lambda r: C.check_captions(
    [(1, {"steps": ["It settles at $40. Price up, quantity up."]}, "")], r)
    or r.has("FAIL", "caption", "shorthand"))

case("a caption over the character cap", lambda r: C.check_captions(
    [(1, {"steps": ["x" * C.CAPTION_MAX + "."]}, "")], r)
    or r.has("FAIL", "caption", "characters"))

case("a caption right at the cap passes", lambda r: C.check_captions(
    [(1, {"steps": ["x" * (C.CAPTION_MAX - 1) + "."]}, "")], r)
    or not [l for l in r.lines if "characters" in l])

case("a static caption is measured too, not just steps", lambda r: C.check_captions(
    [(1, {"caption": "y" * C.CAPTION_MAX + "."}, "")], r)
    or r.has("FAIL", "caption", "characters"))

case("every scenario's steps are measured", lambda r: C.check_captions(
    [(1, {"scenarios": {"a": {"label": "A",
                              "steps": ["z" * C.CAPTION_MAX + "."]}}}, "")], r)
    or r.has("FAIL", "caption", "characters"))

case("a caption showing its working gets the wider cap", lambda r: C.check_captions(
    [(1, {"steps": ["Price falls from $21 to $19, a 10% fall on a $20 midpoint. "
                    + "w" * (C.CAPTION_MAX_WORKING - 90) + "."]}, "")], r)
    or not [l for l in r.lines if "characters" in l])

case("working does not excuse any length", lambda r: C.check_captions(
    [(1, {"steps": ["1 2 3 " + "w" * C.CAPTION_MAX_WORKING + "."]}, "")], r)
    or r.has("FAIL", "caption", "over %d" % C.CAPTION_MAX_WORKING))

case("two numbers is prose, not working", lambda r: C.check_captions(
    [(1, {"steps": ["from $8 to $9 " + "w" * C.CAPTION_MAX + "."]}, "")], r)
    or r.has("FAIL", "caption", "over %d" % C.CAPTION_MAX))

case("a calcs block makes every caption in the widget working", lambda r: C.check_captions(
    [(1, {"calcs": [{"label": "E", "expr": "x"}],
          "steps": ["no digits here at all " + "w" * (C.CAPTION_MAX + 10) + "."]}, "")], r)
    or not [l for l in r.lines if "characters" in l])

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
                 ("<p>a 14-year term on the Board of Governors.</p>", "on the Board of Governors"),
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
case("a long <strong> in prose is reported", lambda r: C.check_markup(
    "<body><p><strong>Tax Burden = 6% of the first $50,000 plus 30% of the rest.</strong></p></body>", r)
    or r.has("WARN", "markup", "swallows"))
case("a centred equation keeps its <strong>", lambda r: C.check_markup(
    '<body><p style="text-align: center;"><strong>Tax Burden = 6% of the first $50,000 plus 30% of the rest.</strong></p></body>', r)
    or not r.has("WARN", "markup", "swallows"))
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


def engine_carries_the_measured_table(r):
    """The engine's copy of the character-width table is the generated one.

    It has to carry its own, because it sizes its margins in the browser, and
    a table typed twice is a table that drifts. `em_widths.py --js` prints the
    literal; this fails if what is in the engine is not what it prints.
    """
    import em_widths
    js = em_widths.js_literal()
    src = (ROOT / "engine" / "sd-graph.js").read_text(encoding="utf-8")
    return ("var EMW = " + js + ";") in src


case("the engine's width table is the one em_widths.py generates",
     engine_carries_the_measured_table)


# ---- a tick ahead of its step ----------------------------------------------

case("a tick that is a later step's reading is reported", lambda r: C.check_tick_steps(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110, "yticks": [19], "xticks": []},
    points=[{"q": 0, "p": 19, "at": 4}]), r)
    or r.has("FAIL", "ticks", "arrives at step 4"))

case("a tick that is a step-0 reading is fine", lambda r: C.check_tick_steps(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110, "yticks": [7]},
    points=[{"q": 0, "p": 7}]), r)
    or not r.has("FAIL", "ticks", "arrives at step"))

case("a tick ahead of its step is found inside a scenario", lambda r: C.check_tick_steps(widget(
    scenarios={"a": {"label": "A", "axes": {"x": "Q", "y": "P", "xmax": 10, "ymax": 10, "xticks": [5]},
                     "points": [{"q": 5, "p": 5, "at": 1}]}}), r)
    or r.has("FAIL", "ticks", "(A)"))

# ---- arrows too short to read ----------------------------------------------

case("a stub of a movement arrow is reported", lambda r: C.check_short_arrows(widget(
    axes={"x": "Q", "y": "P", "xmax": 50, "ymax": 50},
    moves=[{"from": [5, 13.3], "to": [5, 15.3], "offset": 0}]), r)
    or r.has("WARN", "arrows", "almost all head"))

case("a movement arrow of ordinary length is not", lambda r: C.check_short_arrows(widget(
    axes={"x": "Q", "y": "P", "xmax": 110, "ymax": 110},
    moves=[{"from": [30, 70], "to": [70, 30]}]), r)
    or not r.has("WARN", "arrows", "almost all head"))

_SHIFT = [{"id": "S1", "label": "S1", "pts": [[8, 8], [100, 100]]},
          {"id": "S2", "label": "S2", "pts": [[38, 8], [110, 80]], "from": "S1"}]

case("a shift arrow above where its curve ends is reported",
     lambda r: C.check_short_arrows(widget(
         curves=[dict(_SHIFT[0]), dict(_SHIFT[1], arrowP=88)]), r)
     or r.has("WARN", "arrows", "past the curve's end"))

case("a shift arrow inside both curves is not",
     lambda r: C.check_short_arrows(widget(
         curves=[dict(_SHIFT[0]), dict(_SHIFT[1], arrowP=70)]), r)
     or not r.has("WARN", "arrows", "past the curve's end"))

# ---- images the conversion decided to keep ---------------------------------

_GRAPHY = ('<img src="x.png" alt="supply and demand in the market for eggs">')

case("an image that still looks like a graph is reported",
     lambda r: C.check_images("<body>%s</body>" % _GRAPHY, r)
     or r.has("FAIL", "images", "looks like a graph"))

case("a KEEP comment exempts the image under it",
     lambda r: C.check_images(
         "<body><!-- KEEP: a photograph -->%s</body>" % _GRAPHY, r)
     or not r.has("FAIL", "images", "looks like a graph"))

case("a KEEP comment exempts only the image under it",
     lambda r: C.check_images(
         "<body><!-- KEEP: a photograph -->%s\n%s</body>" % (_GRAPHY, _GRAPHY), r)
     or r.has("FAIL", "images", "looks like a graph"))


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
