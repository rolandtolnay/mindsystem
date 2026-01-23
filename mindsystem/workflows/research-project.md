# Research Project Workflow

## DEPRECATED

**This workflow has been consolidated into the ms-researcher agent.**

The research methodology for project research now lives in:
- `agents/ms-researcher.md`

The `/ms:research-project` command spawns 4 parallel ms-researcher agents:
- Stack agent -> .planning/research/STACK.md
- Features agent -> .planning/research/FEATURES.md
- Architecture agent -> .planning/research/ARCHITECTURE.md
- Pitfalls agent -> .planning/research/PITFALLS.md

The orchestrator synthesizes SUMMARY.md after all agents complete.

**Migration:** No action needed - the command handles this automatically.

---

*Deprecated: 2026-01-15*
*Replaced by: agents/ms-researcher.md*
