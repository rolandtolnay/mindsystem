# Milestone Complete Routing

Reference for presenting "Next Up" guidance when all phases in a milestone are complete. Used by execute-phase, progress, execute-plan workflows.

## Purpose

Celebrate milestone completion and guide user toward audit or archive.

## Variables

From calling context:
- `{N}` — total number of phases in milestone
- `{name}` — milestone name (if known)

## Output Format

```markdown
---

## All Phases Complete

All {N} phases finished!

## ▶ Next Up

`/ms:audit-milestone` — verify requirements, cross-phase integration, E2E flows

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:verify-work` — manual acceptance testing
- `/ms:complete-milestone` — skip audit, archive directly
- `/ms:add-phase <description>` — add another phase first

---
```
