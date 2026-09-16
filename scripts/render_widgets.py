#!/usr/bin/env python3
"""Screenshot every widget x scenario x step in a notes file.

    python scripts/render_widgets.py examples/engine-testbed.html [-o shots]

Opens the file in headless Chromium, walks each <div class="sdg"> through every
scenario button and every step, and writes one PNG per state. The point is
collision review: open the PNGs and check that no label touches a curve, point,
arrow or another label (conversion prompt, step 5). Nothing here is automatic --
a human still looks at the pictures.

Exits non-zero if the page logged any JavaScript error or any widget rendered
the engine's .sdg-error message. shots/ is gitignored.
"""

import argparse
import pathlib
import sys

CHROMIUM_CANDIDATES = [
    "/opt/pw-browsers/chromium-1194/chrome-linux/chrome",
]


def find_chromium():
    for path in CHROMIUM_CANDIDATES:
        if pathlib.Path(path).exists():
            return path
    for path in sorted(pathlib.Path("/opt/pw-browsers").glob("chromium-*/chrome-linux/chrome")):
        return str(path)
    return None  # let Playwright use its own download


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="notes HTML file to render")
    ap.add_argument("-o", "--out", default="shots", help="output directory (default: shots)")
    ap.add_argument("--width", type=int, default=900)
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
        exe = find_chromium()
        browser = pw.chromium.launch(executable_path=exe, args=["--no-sandbox"])
        page = browser.new_page(viewport={"width": args.width, "height": 1000})
        page.on("pageerror", lambda e: problems.append("pageerror: %s" % e))
        # A failed resource fetch is the page's own assets (the house CSS/JS
        # lives on S3) not reaching the sandbox -- it says nothing about the
        # widgets, so it is not an engine problem.
        page.on("console", lambda m: problems.append("console: %s" % m.text)
                if m.type == "error" and "Failed to load resource" not in m.text else None)
        page.goto(src.as_uri())
        page.wait_for_timeout(500)

        widgets = page.query_selector_all("div.sdg")
        print("%d widget(s) in %s" % (len(widgets), src.name))

        for wi, widget in enumerate(widgets, 1):
            scenarios = widget.query_selector_all(".sdg-scenario") or [None]
            for si, scenario in enumerate(scenarios, 1):
                if scenario is not None:
                    scenario.click()
                    page.wait_for_timeout(120)
                    label = scenario.inner_text().strip() or "scenario%d" % si
                else:
                    label = "base"
                slug = "".join(c if c.isalnum() else "-" for c in label).strip("-").lower()

                step = 1
                while True:
                    page.wait_for_timeout(80)
                    name = "w%02d-%s-step%02d.png" % (wi, slug, step)
                    widget.screenshot(path=str(out / name))
                    shots += 1
                    nxt = widget.query_selector(".sdg-controls button:nth-of-type(2)")
                    if nxt is None or nxt.is_disabled():
                        break
                    nxt.click()
                    step += 1

            err = widget.query_selector(".sdg-error")
            if err:
                problems.append("widget %d: %s" % (wi, err.inner_text()))

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
