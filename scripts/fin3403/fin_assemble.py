#!/usr/bin/env python3
# Copied from the 2026-10-16 FIN3403 build area; paths are relative to a folder
# holding the unpacked "Finance P1"/"Finance P2" zips (S/fin). See CLAUDE.md.
"""Build the FIN3403 delivery: every chapter's three editions with calculator widgets.

    python fin_assemble.py [--test] [--only ChapterKey ...]

Reads S/fin/maps/<ChapterKey>.json (written by fin_maps.py; absent = no calculator
images, the chapter is copied with only the TOC script swapped) and writes

    S/fin/deliver/FIN3403 Widgets/Exam N/<chapter folder without " - DONE">/
        UCF FIN3403-262-ExamN-Topic-widgets-{Full,Balanced,Concise}.html

With --test the files keep their data-expect attributes (for test_hp.py); without
it they are stripped. Then runs test_hp.py on every file that carries a widget.
"""
import json, pathlib, re, subprocess, sys, shutil

S = pathlib.Path(__file__).resolve().parent.parent          # S/fin
REPO = pathlib.Path("/home/user/WidgetWorkflow")
APPLY = REPO / "scripts" / "apply_widgets.py"
DELIVER = S / "deliver" / "FIN3403 Widgets"
MAPS = S / "maps"
EMPTY_MAP = MAPS / "_empty.json"


def chapters():
    out = {}
    for full in list(S.glob("p1/Finance P1/Exam */*/*-Full.html")) + list(S.glob("p2/Finance P2/Exam */*/*-Full.html")):
        if "Ignore" in full.name or "Ignore" in full.parent.name:
            continue
        m = re.match(r"UCF FIN3403-\d{3}-(Exam\d)-(.+)-Full\.html$", full.name)
        assert m, full.name
        out["%s-%s" % m.groups()] = full.parent
    return out


def main():
    args = sys.argv[1:]
    test = "--test" in args
    only = args[args.index("--only") + 1:] if "--only" in args else None
    MAPS.mkdir(exist_ok=True)
    EMPTY_MAP.write_text('{"images": {}}')
    if DELIVER.exists() and not only:
        shutil.rmtree(DELIVER)
    summary = []
    for key, folder in sorted(chapters().items()):
        if only and key not in only:
            continue
        exam = folder.parent.name                       # "Exam 2"
        dest = DELIVER / exam / folder.name.replace(" - DONE", "")
        dest.mkdir(parents=True, exist_ok=True)
        mp = MAPS / (key + ".json")
        if not mp.exists():
            # no calculator images: every picture stays, only the TOC script changes
            bases = set()
            for f in folder.glob("*.html"):
                if "Ignore" in f.name:
                    continue
                bases.update(re.findall(r'<img[^>]*?src="[^"]*/([^"/]+)"', f.read_text(encoding="utf-8")))
            mp = MAPS / ("_auto-" + key + ".json")
            mp.write_text(json.dumps({"images": {b: {"keep": "not a calculator screenshot"} for b in sorted(bases)}}, indent=1))
        for edition in ("Full", "Balanced", "Concise"):
            srcs = [f for f in folder.glob("*-%s.html" % edition) if "Ignore" not in f.name]
            assert len(srcs) == 1, (key, edition, srcs)
            src = srcs[0]
            out = dest / src.name.replace("-%s.html" % edition, "-widgets-%s.html" % edition)
            use = mp
            if edition == "Concise" and (MAPS / (key + "-concise.json")).exists():
                use = MAPS / (key + "-concise.json")
            cmd = [sys.executable, str(APPLY), str(src), str(use), str(out), "--toc"]
            if edition == "Concise":
                cmd.append("--anchors")
            if not test:
                cmd.append("--strip-expect")
            r = subprocess.run(cmd, capture_output=True, text=True)
            if r.returncode:
                summary.append("%-34s %-8s APPLY FAILED: %s" % (key, edition, (r.stdout + r.stderr).strip()[-400:]))
                continue
            n = int(re.search(r": (\d+) widgets", r.stdout).group(1))
            line = "%-34s %-8s %2d widgets" % (key, edition, n)
            if n and test:
                t = subprocess.run([sys.executable, str(S / "test" / "test_hp.py"), str(out)], capture_output=True, text=True)
                tail = t.stdout.strip().splitlines()
                line += "  " + (tail[-1] if tail else t.stderr.strip()[-200:])
                fails = [l for l in tail if l.startswith("FAIL") or l.startswith("  ERR")]
                if fails:
                    line += "\n" + "\n".join("      " + f for f in fails)
            summary.append(line)
    text = "\n".join(summary)
    (S / "deliver" / "summary.txt").write_text(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
