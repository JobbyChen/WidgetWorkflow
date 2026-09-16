---
description: Run the mechanical step-8 checks on a notes file
---

Run `python scripts/check_file.py $ARGUMENTS` and report the result.

If anything FAILs, fix it and run again until it is 0 FAIL. An embedded-engine
mismatch is fixed by re-running `python scripts/embed_engine.py` on the file, not
by editing the embedded copy.

Remember what this script cannot check: whether a number is the number the source
gave, and whether a label touches a curve. Those need the source material and
`/render`.
