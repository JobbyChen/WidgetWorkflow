# Archive

> **Stub.** The archive — the v4 → v5 prompt diff, the notes on the two v5
> variants (PROJECT-INSTRUCTIONS and TOOL), and the older stylesheet — is in
> `eco-widgets.zip`, which never reached this repository. Nothing has been
> archived here yet.

What `CLAUDE.md` records about it, so the conventions are not lost:

- The conversion prompt went through five versions. v4 carried a "what changed"
  line at the top; v5 should have kept that habit, and a v6 must.
- There were two v5 variants. They differed in the engine source they embedded:
  the TOOL variant appended the two engine files as Appendix A and Appendix B and
  stripped the header comment from the JavaScript.
- **Repo convention:** `engine/sd-graph.js` keeps its header comment; embedded
  copies drop it. `scripts/embed_engine.py` does this, and
  `scripts/check_file.py` compares with the header stripped, so the two agree.
- If a standalone tool prompt is needed again, append the two engine files as
  Appendix A and B rather than pointing at `engine/`.
