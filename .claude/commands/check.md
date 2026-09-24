---
description: Run the mechanical step-8 checks on a notes file
---

Run `python scripts/check_file.py $ARGUMENTS` and report the result.

Fix what it finds and run again until it is 0 FAIL. An embedded-engine mismatch
is fixed by re-running `python scripts/embed_engine.py` on the file, never by
editing the embedded copy.

When the file was built from another file — a chapter as sent, a full edition
being condensed — pass it: `--source <that file>`. The class dates are the part
that goes missing, because they carry no content and nothing else notices.

Two things to keep in mind:

- It cannot check whether a number is the number the source gave. That needs the
  source and a person.
- Its label test replicates the engine's geometry to find labels sitting on
  curves. That catches the common cases, not all of them — `/render` and your own
  eyes are still step 8's second half.

If a finding is in `examples/`, check `docs/open-issues.md` before changing
anything: the delivered files are committed as they shipped, and their known
failures are recorded there on purpose.
