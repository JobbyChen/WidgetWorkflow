#!/usr/bin/env python3
"""Does a notes file work on a phone? Measured, not eyeballed.

    python scripts/mobile_check.py examples/*.html
    python scripts/mobile_check.py <file> --width 320 --shots shots/mobile

Ian reads these on a desktop and students read them on a phone, so the whole
risk here is invisible from where the file gets reviewed. This loads each file
at phone widths and reports the four things that actually break:

  page      the page scrolls sideways (anything wider than the viewport)
  fit       a widget's figure, table or SVG is wider than the column
  tap       a scenario or step button is under the 44px Apple/Google minimum
  reach     the buttons and the graph cannot be on screen at the same time
  live      a scenario or step button does not respond, or the engine throws

`reach` is the one a screenshot hides. Scenario buttons go full width on a
phone, so five of them are a screenful on their own, and a student taps one and
then has to scroll to find out what it did. Nothing is broken and nothing is
off the edge; the cause and its effect are just never both visible.

It clicks every scenario and every step of every widget at that width, so
"interactive" is a measurement rather than an assumption.
"""

import argparse
import json
import pathlib
import sys

CHROMIUM_GLOB = "chromium-*/chrome-linux/chrome"
TAP_MIN = 44.0          # the smaller side of a control, in CSS px
SETTLE_MS = 750


def find_chromium():
    for path in sorted(pathlib.Path("/opt/pw-browsers").glob(CHROMIUM_GLOB)):
        return str(path)
    return None


PROBE = r"""
() => {
  const out = {page: {}, widgets: []};
  const de = document.documentElement;
  out.page.scrollW = de.scrollWidth;
  out.page.clientW = de.clientWidth;
  // The widest element that actually sticks out past the viewport, so an
  // overflow report names the thing to fix instead of just the page.
  let worst = null;
  for (const el of document.body.querySelectorAll('*')) {
    const r = el.getBoundingClientRect();
    if (r.width === 0) continue;
    const over = Math.round(r.right - de.clientWidth);
    if (over > 1 && (!worst || over > worst.over)) {
      worst = {over, tag: el.tagName.toLowerCase(),
               cls: (el.className && el.className.baseVal !== undefined
                     ? el.className.baseVal : el.className || '').toString().slice(0, 40)};
    }
  }
  out.page.worst = worst;
  document.querySelectorAll('.sdg').forEach((w, i) => {
    const box = w.getBoundingClientRect();
    const rec = {n: i + 1, w: Math.round(box.width), over: [], taps: []};
    const t = w.querySelector('.sdg-title, h3, .sdg-lede');
    rec.title = (t ? t.textContent : '').trim().slice(0, 52);
    for (const sel of ['figure', 'svg', 'table', '.sdg-body']) {
      w.querySelectorAll(sel).forEach(el => {
        const r = el.getBoundingClientRect();
        if (r.width - box.width > 1)
          rec.over.push(sel + ' +' + Math.round(r.width - box.width) + 'px');
        if (el.scrollWidth - el.clientWidth > 1 && sel === 'table')
          rec.over.push('table scrolls +' + (el.scrollWidth - el.clientWidth) + 'px');
      });
    }
    w.querySelectorAll('button').forEach(b => {
      const r = b.getBoundingClientRect();
      const small = Math.min(r.width, r.height);
      if (small < %TAP% && r.width > 0)
        rec.taps.push((b.textContent || '?').trim().slice(0, 22) + ' ' +
                      Math.round(r.width) + 'x' + Math.round(r.height));
    });
    // Can a student see the button they tap and the graph it changes at once?
    const fig = w.querySelector('figure'), scen = w.querySelector('.sdg-scen');
    if (fig && scen) {
      const f = fig.getBoundingClientRect(), c = scen.getBoundingClientRect();
      rec.span = Math.round(f.bottom - c.top);
    }
    rec.scenarios = w.querySelectorAll('.sdg-scen button').length;
    rec.steps = w.querySelectorAll('.sdg-ctrl button').length;
    rec.buttons = w.querySelectorAll('button').length;
    out.widgets.push(rec);
  });
  return out;
}
"""


def main():
    from playwright.sync_api import sync_playwright

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("files", type=pathlib.Path, nargs="+")
    ap.add_argument("--width", type=int, default=390, help="viewport width (default 390)")
    ap.add_argument("--height", type=int, default=844)
    ap.add_argument("--shots", type=pathlib.Path, help="save a screenshot per widget here")
    a = ap.parse_args()

    probe = PROBE.replace("%TAP%", str(TAP_MIN))
    problems = 0
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=find_chromium(), args=["--no-sandbox"])
        for f in a.files:
            pg = b.new_page(viewport={"width": a.width, "height": a.height},
                            device_scale_factor=2, is_mobile=True, has_touch=True)
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(f.absolute().as_uri())
            pg.wait_for_timeout(SETTLE_MS)
            r = pg.evaluate(probe)

            print("=== %s  @%dpx" % (f.name, a.width))
            if r["page"]["scrollW"] - r["page"]["clientW"] > 1:
                w = r["page"]["worst"]
                print("  page   scrolls sideways by %dpx%s"
                      % (r["page"]["scrollW"] - r["page"]["clientW"],
                         "  (widest: <%s class=%r>)" % (w["tag"], w["cls"]) if w else ""))
                problems += 1

            dead = []
            for rec in r["widgets"]:
                n = rec["n"]
                w = pg.locator(".sdg").nth(n - 1)
                # Drive the widget the way a student does: each scenario that is
                # not already showing, then Next to the last step and Back again.
                # A button that is disabled or already pressed is doing its job
                # when nothing happens, so neither is exercised.
                scen = w.locator(".sdg-scen button")
                targets = [k for k in range(scen.count())
                           if scen.nth(k).get_attribute("aria-pressed") != "true"]
                for k in targets:
                    before = w.inner_html()
                    try:
                        scen.nth(k).click(timeout=2500)
                        pg.wait_for_timeout(SETTLE_MS)
                    except Exception as e:
                        dead.append("w%d scenario %d: %s"
                                    % (n, k + 1, str(e).split("\n")[0][:56]))
                        continue
                    if w.inner_html() == before:
                        dead.append("w%d scenario %d (%s) changed nothing"
                                    % (n, k + 1, scen.nth(k).inner_text().strip()[:22]))
                ctrl = w.locator(".sdg-ctrl button")
                nxt = w.get_by_role("button", name="Next step")
                steps = 0
                while nxt.count() and nxt.is_enabled() and steps < 12:
                    # A two-panel widget has several <svg>, plus the little
                    # arrow icons, so compare the whole widget rather than one.
                    before = w.inner_html()
                    try:
                        nxt.click(timeout=2500)
                    except Exception as e:
                        # An overflowing figure pushes the controls off the
                        # viewport, and then the step button cannot be tapped
                        # at all. That is the finding, not a crash.
                        dead.append("w%d Next step not tappable at step %d: %s"
                                    % (n, steps + 1, str(e).split("\n")[0][:56]))
                        break
                    pg.wait_for_timeout(SETTLE_MS)
                    after = w.inner_html()
                    if after == before:
                        dead.append("w%d step %d drew nothing new" % (n, steps + 1))
                    steps += 1
                rec["stepped"] = steps
                back = w.get_by_role("button", name="Back")
                if steps and back.count() and back.is_enabled():
                    before = w.inner_html()
                    try:
                        back.click(timeout=2500)
                        pg.wait_for_timeout(SETTLE_MS)
                        if w.inner_html() == before:
                            dead.append("w%d Back changed nothing" % n)
                    except Exception as e:
                        dead.append("w%d Back not tappable: %s"
                                    % (n, str(e).split("\n")[0][:56]))
                elif steps and back.count():
                    dead.append("w%d Back still disabled after %d step(s)" % (n, steps))
                far = rec.get("span", 0) > a.height
                if rec["over"] or rec["taps"] or far:
                    print("  w%-2d %-52s %dpx wide" % (n, rec["title"], rec["w"]))
                if far:
                    print("      reach  %d scenario button(s) then the graph is "
                          "%dpx, past a %dpx screen by %d"
                          % (rec["scenarios"], rec["span"], a.height,
                             rec["span"] - a.height))
                    problems += 1
                    if rec["over"]:
                        print("      fit  %s" % "; ".join(sorted(set(rec["over"]))))
                        problems += 1
                    if rec["taps"]:
                        print("      tap  under %gpx: %s" % (TAP_MIN, "; ".join(rec["taps"])))
                        problems += 1
                if a.shots:
                    a.shots.mkdir(parents=True, exist_ok=True)
                    try:
                        el = pg.locator(".sdg").nth(n - 1)
                        el.scroll_into_view_if_needed()
                        el.screenshot(path=str(a.shots / ("%s-w%02d.png" % (f.stem, n))))
                    except Exception:
                        pass
            for d in dead:
                print("  live   %s" % d)
                problems += len(dead) and 1
            if errs:
                print("  live   %d engine error(s): %s" % (len(errs), errs[0][:80]))
                problems += 1
            tot = len(r["widgets"])
            clean = sum(1 for x in r["widgets"] if not x["over"] and not x["taps"]
                        and x.get("span", 0) <= a.height)
            print("  -- %d/%d widget(s) fit with usable controls; %d scenario(s) and "
                  "%d step(s) driven"
                  % (clean, tot, sum(x["scenarios"] for x in r["widgets"]),
                     sum(x.get("stepped", 0) for x in r["widgets"])))
            pg.close()
        b.close()
    print("\n== %d problem(s) at %dpx" % (problems, a.width))
    return 0


if __name__ == "__main__":
    sys.exit(main())
