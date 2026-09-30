#!/usr/bin/env python3
"""Re-measure the character-width table in `em_widths.py`, from a real page.

    python scripts/measure_em.py examples/ECO2013-263-SupplyAndDemand.html

Writes the table back into `scripts/em_widths.py`. Run it whenever the house
font changes, and never by hand.

**It refuses to measure until Red Hat Display has actually loaded.** The first
version of this table did not, and in this container the font comes from
Google Fonts through the agent proxy -- which the browser scripts did not use
until v2.47 -- so what it measured was the fallback. Every width in the table
was somewhere between 6% and 100% too wide, and `1` was recorded at the width
of a `0` because the fallback sets its digits tabular and Red Hat Display does
not. Margins sized from it were generous and overlap tests were pessimistic,
which is the safe direction and is why nothing looked wrong.
"""
import io
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from render_widgets import launch_kwargs                     # noqa: E402
from playwright.sync_api import sync_playwright              # noqa: E402

CHARS = ("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
         " +-=*/()[].,:;%$&'\"−×÷→≤≥?!#"
         "₀₁₂₃₄₅¹²³"
         "ᶜᶠᵂˢᵈₐ")

PROBE = r"""(chars) => {
  if (!document.fonts.check('700 13px "Red Hat Display"')) return {loaded: false};
  const svg = document.querySelector('.sdg svg');
  const NS = 'http://www.w3.org/2000/svg';
  const t = document.createElementNS(NS, 'text');
  t.setAttribute('class', 'clbl'); t.setAttribute('x', 0); t.setAttribute('y', 0);
  svg.appendChild(t);
  const at = s => { t.textContent = s; return t.getComputedTextLength(); };
  const row = {};
  // Ten copies between two H's, so the side bearings cancel and what is left
  // is the advance width.
  const base = at('HH');
  for (const c of chars) row[c] = ((at('H' + c.repeat(10) + 'H') - base) / 10) / 13;
  // A run of spaces collapses, so that one is measured against solid H's.
  row[' '] = ((at('H H H H H H H H H H H') - at('H'.repeat(11))) / 10) / 13;
  svg.removeChild(t);
  return {loaded: true, row};
}"""


def measure(path):
    with sync_playwright() as p:
        b = p.chromium.launch(**launch_kwargs())
        pg = b.new_page(viewport={"width": 1280, "height": 900}, ignore_https_errors=True)
        pg.goto(pathlib.Path(path).resolve().as_uri(), wait_until="networkidle")
        pg.evaluate("document.fonts.ready")
        pg.wait_for_timeout(1200)
        out = pg.evaluate(PROBE, CHARS)
        b.close()
    if not out.get("loaded"):
        raise SystemExit("Red Hat Display is not loaded in the browser -- measuring "
                         "now would record the fallback font, which is how the first "
                         "table went wrong. Check the proxy reaches fonts.googleapis.com.")
    return dict((k, round(v, 3)) for k, v in out["row"].items())


def write(tab):
    p = pathlib.Path(__file__).resolve().parent / "em_widths.py"
    s = io.open(p, encoding="utf-8").read()
    rows, cur = [], []
    for k in sorted(tab):
        cur.append("%r: %s" % (k, ("%.3f" % tab[k]).rstrip("0").rstrip(".") or "0"))
        if len(cur) == 6:
            rows.append(", ".join(cur)); cur = []
    if cur:
        rows.append(", ".join(cur))
    body = "{\n    " + ",\n    ".join(rows) + ",\n}"
    s = re.sub(r"EM = \{.*?\n\}", "EM = " + body, s, count=1, flags=re.S)
    fb = (max(v for k, v in tab.items() if k.isupper()),
          max(v for k, v in tab.items() if k.islower()),
          max(v for k, v in tab.items() if k.isdigit()),
          max(v for k, v in tab.items() if not k.isalnum() and k != " "))
    s = re.sub(r'EM_FALLBACK = \{[^}]*\}',
               'EM_FALLBACK = {"upper": %.3f, "lower": %.3f, "digit": %.3f, "other": %.3f}' % fb,
               s, count=1)
    io.open(p, "w", encoding="utf-8").write(s)
    print("wrote %d characters into scripts/em_widths.py" % len(tab))


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "examples/ECO2013-263-SupplyAndDemand.html"
    write(measure(src))
