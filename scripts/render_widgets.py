#!/usr/bin/env python3
"""Screenshot every widget x scenario x step in a notes file.

    python scripts/render_widgets.py examples/ECO2013-Widgets-All.html [-o shots]

Opens the file in headless Chromium, walks each <div class="sdg"> through every
scenario button and every step, and writes one PNG per state. The point is
collision review: open the PNGs and check that no label touches a curve, point,
arrow or another label (conversion prompt, step 5). Nothing here is automatic --
a human still looks at the pictures.

Two things about the engine shape this script. Switching scenario rebuilds the
widget's whole subtree, so every element is re-queried by index rather than
held across a click. And shifts are animated (~0.6s), so each screenshot waits
for the transition to finish; otherwise curves are caught mid-slide.

Exits non-zero if the page logged a JavaScript error or a widget rendered the
engine's "Widget config error" message. shots/ is gitignored.
"""

import argparse
import pathlib
import sys

SETTLE_MS = 750          # longer than the .6s shift transition
CHROMIUM_GLOB = "chromium-*/chrome-linux/chrome"


def find_chromium():
    for path in sorted(pathlib.Path("/opt/pw-browsers").glob(CHROMIUM_GLOB)):
        return str(path)
    return None  # fall back to Playwright's own download



# The one defect a screenshot review keeps missing, because a 1px gap and a
# touch look identical at a glance: a shift or movement arrow grazing a curve.
# Measured off the rendered geometry, which is also the only way to catch it on
# a `curved` pair, where the drawn spline is nowhere near the polyline through
# its points.
MIN_ARROW_GAP = 4.0
# A schedule's per-row arrow spans two dots at one price and is inset only 6px,
# so it legitimately runs closer to its own curves than a shift arrow does.
MIN_ROW_GAP = 2.0
# Ian's rule: an arrow should not lie over the dashed guides either, unless
# there is genuinely nowhere else for it to go. Reported apart from the curve
# gap because the two are judged differently -- a guide crossing is sometimes
# unavoidable in a crowded panel, a curve crossing never is. Row arrows are
# exempt: they run between two schedule dots, across the grid, by construction.
MIN_GUIDE_GAP = 3.0

TOUCH_JS = """(n, args) => {
  var i = args[0], lim = args[1], rowLim = args[2], gLim = args[3], bad = [], w = n[i];
  w.querySelectorAll('svg').forEach(function (svg) {
    var arrows = [].slice.call(svg.querySelectorAll('path.arrow'))
      .filter(function (a) { return !a.closest('.off'); });
    arrows.forEach(function (a) {
      var mine = a.classList.contains('row') ? rowLim : lim;
      var L = a.getTotalLength(), pts = [];
      for (var k = 0; k <= 120; k++) { var q = a.getPointAtLength(L * k / 120); pts.push([q.x, q.y]); }
      function nearest(node) {
        var EL = node.getTotalLength(), best = 1e9;
        for (var m = 0; m <= 300; m++) {
          var q2 = node.getPointAtLength(EL * m / 300);
          for (var j = 0; j < pts.length; j++) {
            var d = Math.hypot(q2.x - pts[j][0], q2.y - pts[j][1]);
            if (d < best) best = d;
          }
        }
        return best;
      }
      svg.querySelectorAll('g.curve-g').forEach(function (g) {
        if (g.classList.contains('off')) return;
        var c = g.querySelector('path.curve'); if (!c) return;
        var best = nearest(c);
        if (best < mine) {
          var t = g.querySelector('text.clbl');
          bad.push([Math.round(best * 10) / 10, (t && t.textContent) || '?', 'curve']);
        }
      });
      if (!a.classList.contains('row')) {
        svg.querySelectorAll('.guide').forEach(function (gd) {
          if (gd.closest('.off')) return;
          var d = nearest(gd);
          if (d < gLim) {
            // Name the guide. "a dashed guide" sent three rounds of guesswork
            // into a panel with four of them; its endpoints in user units say
            // which one at a glance. The guide is a <path> or <line>, so read
            // whichever geometry it has and convert back through the viewBox.
            var b = gd.getBBox(), vb = svg.viewBox.baseVal;
            var vert = b.width < 1.5, horiz = b.height < 1.5;
            var where = vert ? 'vertical at x=' + Math.round(b.x)
                      : horiz ? 'horizontal at y=' + Math.round(b.y)
                      : 'bent, x ' + Math.round(b.x) + '-' + Math.round(b.x + b.width) +
                        ' y ' + Math.round(b.y) + '-' + Math.round(b.y + b.height);
            bad.push([Math.round(d * 10) / 10, 'the guide ' + where, 'guide']);
          }
        });
      }
    });
  });
  return bad;
}"""


def touching(page, wi):
    """Every arrow/curve pair closer than MIN_ARROW_GAP, in the current state."""
    return page.eval_on_selector_all("div.sdg", TOUCH_JS,
                                     [wi, MIN_ARROW_GAP, MIN_ROW_GAP,
                                      MIN_GUIDE_GAP])


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="notes HTML file to render")
    ap.add_argument("-o", "--out", default="shots", help="output directory (default: shots)")
    ap.add_argument("--width", type=int, default=1000)
    args = ap.parse_args()

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        sys.exit("playwright is not installed: pip install playwright")

    src = pathlib.Path(args.file).resolve()
    if not src.exists():
        sys.exit("no such file: %s" % src)
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    problems = []
    shots = 0

    with sync_playwright() as pw:
        browser = pw.chromium.launch(executable_path=find_chromium(), args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": args.width, "height": 1000})
        page.on("pageerror", lambda e: problems.append("pageerror: %s" % e))
        # A failed resource fetch is the page's own assets (the house CSS/JS and
        # the webfont live on S3) not reaching the sandbox. It says nothing
        # about the widgets, so it is not an engine problem.
        page.on("console", lambda m: problems.append("console: %s" % m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        page.goto(src.as_uri())
        page.wait_for_timeout(600)

        count = page.eval_on_selector_all("div.sdg", "n => n.length")
        print("%d widget(s) in %s" % (count, src.name))

        for wi in range(count):
            n_scen = page.eval_on_selector_all(
                "div.sdg", "(n, i) => n[i].querySelectorAll('.sdg-scen button').length", wi)

            for si in range(max(1, n_scen)):
                if n_scen:
                    page.eval_on_selector_all(
                        "div.sdg",
                        "(n, a) => n[a[0]].querySelectorAll('.sdg-scen button')[a[1]].click()",
                        [wi, si])
                    page.wait_for_timeout(200)
                    label = page.eval_on_selector_all(
                        "div.sdg",
                        "(n, a) => n[a[0]].querySelectorAll('.sdg-scen button')[a[1]].textContent",
                        [wi, si]).strip()
                else:
                    label = "base"
                slug = "".join(c if c.isalnum() else "-" for c in label).strip("-").lower()[:40] or "base"

                step = 1
                while True:
                    page.wait_for_timeout(SETTLE_MS)
                    widget = page.query_selector_all("div.sdg")[wi]
                    widget.screenshot(path=str(out / ("w%02d-%s-step%02d.png" % (wi + 1, slug, step))))
                    shots += 1
                    for gap, lbl, kind in touching(page, wi):
                        seen = "curve %s" % lbl if kind == "curve" else lbl
                        problems.append("widget %d (%s) step %d: an arrow comes "
                                        "within %.1fpx of %s"
                                        % (wi + 1, label, step, gap, seen))
                    # .sdg-ctrl is [Back, Next step, Start over]
                    more = page.eval_on_selector_all(
                        "div.sdg",
                        "(n, i) => { var b = n[i].querySelectorAll('.sdg-ctrl button')[1];"
                        "  if (!b || b.disabled) return false; b.click(); return true; }", wi)
                    if not more:
                        break
                    step += 1

            text = page.eval_on_selector_all("div.sdg", "(n, i) => n[i].textContent", wi)
            if "Widget config error" in text:
                problems.append("widget %d: %s" % (wi + 1, text.strip()[:120]))

        browser.close()

    print("%d screenshot(s) -> %s/" % (shots, out))
    if problems:
        print("\n%d problem(s):" % len(problems))
        for p in problems:
            print("  " + p)
        return 1
    print("no engine errors")
    return 0


if __name__ == "__main__":
    sys.exit(main())
