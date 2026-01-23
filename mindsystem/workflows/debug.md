# Debug Workflow (DEPRECATED)

This workflow has been consolidated into the `ms-debugger` agent.

**Location:** `agents/ms-debugger.md`

**Reason:** The ms-debugger agent contains all debugging expertise. Loading a separate workflow into orchestrator context was wasteful.

**Migration:**
- `/ms:debug` now spawns `ms-debugger` agent directly
- All debugging methodology lives in the agent file
- Templates remain at `mindsystem/templates/DEBUG.md`

See `agents/ms-debugger.md` for debugging expertise.
