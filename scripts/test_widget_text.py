#!/usr/bin/env python3
"""Tests for widget_text.py. Run after changing it.

It had its own copy of the "what is a widget" regex, which required newlines
around the config and scanned the raw file. So it missed every widget written
without them -- four of the nine in the shipped supply-and-demand file -- and a
semester swap skipped their captions in silence while reporting success.
"""
import io
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import widget_text as W

FAILS = []


def case(name, fn):
    try:
        ok = fn()
    except Exception as e:
        ok, name = False, "%s -- %s: %s" % (name, type(e).__name__, e)
    print("%-4s %s" % ("ok" if ok else "FAIL", name))
    if not ok:
        FAILS.append(name)


ONE = '{"title":"T","steps":["First.","Second."]}'
TIGHT = '<div class="sdg"><script type="application/json">%s</script></div>' % ONE
LOOSE = ('<div class="sdg"><script type="application/json">\n%s\n</script></div>'
         % json.dumps(json.loads(ONE), indent=1))
# The engine's header comment documents this markup, so a raw scan finds a
# widget inside the embedded engine and fails to parse it.
ENGINE = ('<script>/* Markup: <div class="sdg">'
          '<script type="application/json">{ ...config... }<\\/script></div> */</script>')


def listed(src):
    return dict(("w%d.%s" % (n, a), t)
                for n, (_, cfg) in enumerate(W.configs(src), 1)
                for a, t in W.visit_map(cfg))


case("a widget with no newlines around its config is found",
     lambda: "w1.steps[0]" in listed(TIGHT))
case("a widget with newlines is found too",
     lambda: "w1.steps[0]" in listed(LOOSE))
case("both shapes in one file are found",
     lambda: len(listed(TIGHT + "\n" + LOOSE)) == 6)
case("the engine's own header comment is not a widget",
     lambda: listed(ENGINE + TIGHT) == listed(TIGHT))


def roundtrip(src, edits=None):
    d = pathlib.Path(tempfile.mkdtemp())
    f, m = d / "n.html", d / "m.json"
    io.open(f, "w", encoding="utf-8").write(src)
    subprocess.check_call([sys.executable, str(HERE / "widget_text.py"),
                           str(f), "--json"], stdout=io.open(m, "wb"))
    if edits:
        got = json.loads(io.open(m, encoding="utf-8").read())
        got.update(edits)
        json.dump(got, io.open(m, "w", encoding="utf-8"), ensure_ascii=False)
    subprocess.check_call([sys.executable, str(HERE / "widget_text.py"),
                           str(f), "--apply", str(m)], stdout=subprocess.DEVNULL)
    return io.open(f, encoding="utf-8").read()


case("a no-op round-trip leaves a hand-written config byte for byte",
     lambda: roundtrip(TIGHT) == TIGHT)
case("a no-op round-trip leaves a generated config byte for byte",
     lambda: roundtrip(LOOSE) == LOOSE)
case("an edit lands, and only in the widget it names",
     lambda: "Rewritten." in roundtrip(TIGHT + "\n" + LOOSE,
                                       {"w1.steps[0]": "Rewritten."})
     and roundtrip(TIGHT + "\n" + LOOSE,
                   {"w1.steps[0]": "Rewritten."}).count("First.") == 1)

print("\n%d failing" % len(FAILS))
sys.exit(1 if FAILS else 0)
