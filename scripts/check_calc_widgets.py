"""Drive every HP 10bII+ calculator widget on a page to its last step and compare the result against
an expected string. Usage: test_hp.py PAGE.html  (widgets carry data-expect="..."),
or test_hp.py PAGE.html --all-alts to also click through each data-alt button."""
import sys, re, json, pathlib, asyncio, os
sys.path.insert(0, '/home/user/WidgetWorkflow/scripts')
from mobile_check import launch_kwargs
from playwright.async_api import async_playwright

async def run(path, width=1100):
    url = pathlib.Path(path).resolve().as_uri()
    errors, results = [], []
    async with async_playwright() as p:
        b = await p.chromium.launch(**launch_kwargs())
        pg = await b.new_page(viewport={"width": width, "height": 900})
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" and "Failed to load resource" not in m.text else None)
        pg.on("pageerror", lambda e: errors.append(str(e)))
        await pg.goto(url)
        await pg.wait_for_timeout(300)
        n = await pg.evaluate("document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys').length")
        for i in range(n):
            info = await pg.evaluate("""(i) => {
              const el = document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i];
              const bar = el.previousElementSibling && el.previousElementSibling.classList.contains('hp-alts') ? el.previousElementSibling : null;
              return {kind: el.className.split(' ')[0], expect: el.getAttribute('data-expect') || '', alts: bar ? bar.children.length : 0,
                      altExpect: el.getAttribute('data-alt-expect') || '', keys: el.getAttribute('data-keys') || ''};
            }""", i)
            if info["kind"] == "hp10bii-keys":
                glow = await pg.evaluate("(i) => document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i].querySelectorAll('.hp-glow').length", i)
                results.append((i, "keys", info["keys"], "%d glowing" % glow, glow == len(info["keys"].split(","))))
                continue
            expects = [info["expect"]] if not info["alts"] else (info["altExpect"].split("|") if info["altExpect"] else [info["expect"]] * info["alts"])
            for a in range(max(1, info["alts"])):
                if info["alts"]:
                    await pg.evaluate("([a,i]) => document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i].previousElementSibling.children[a].click()", [a, i])
                    await pg.wait_for_timeout(50)
                # jump to the last step, wait for the key animation to finish
                nsteps = await pg.evaluate("(i) => document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i].querySelectorAll('.hp-grp').length", i)
                await pg.evaluate("(i) => { const el = document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i]; const g = el.querySelectorAll('.hp-grp'); g[g.length-1].click(); }", i)
                for _ in range(200):
                    await pg.wait_for_timeout(100)
                    done = await pg.evaluate("(i) => { const el = document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i]; return el.querySelector('.hp-prog').textContent.startsWith('Step'); }", i)
                    if done: break
                got = await pg.evaluate("(i) => { const el = document.querySelectorAll('.hp10bii,.hp10bii-cf,.hp10bii-amort,.hp10bii-stat,.hp10bii-keys')[i]; const r = el.querySelectorAll('.hp-res'); return {res: r.length ? r[r.length-1].textContent : '(none)', lcd: el.querySelector('[data-lcd]').textContent, cap: el.querySelector('.hp-caption').textContent.slice(0,160)}; }", i)
                exp = expects[a] if a < len(expects) else ""
                ok = (exp == "") or (exp in got["res"]) or (exp in got["lcd"])
                results.append((i, info["kind"] + (" alt%d" % a if info["alts"] else ""), exp, got["res"] + " / lcd " + got["lcd"], ok, nsteps))
        sw = await pg.evaluate("document.documentElement.scrollWidth")
        await b.close()
    return results, errors, sw

if __name__ == "__main__":
    path = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 1100
    res, errs, sw = asyncio.run(run(path, width))
    bad = 0
    for r in res:
        flag = "ok  " if r[4] else "FAIL"
        if not r[4]: bad += 1
        print(flag, *[str(x) for x in r[:4]], *(["steps=%d" % r[5]] if len(r) > 5 else []))
    print("widgets:", len(res), "failures:", bad, "console errors:", len(errs), "scrollWidth:", sw, "viewport:", width)
    for e in errs[:10]: print("  ERR", e[:200])
    sys.exit(1 if bad or errs else 0)
