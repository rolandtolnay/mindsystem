# Between Milestones Routing

Reference for presenting "Next Up" guidance when between milestones (ROADMAP.md missing, PROJECT.md exists). Used by progress command.

## Purpose

Guide user toward starting the next milestone cycle after a completed milestone was archived.

## Information to Extract

Read MILESTONES.md to find the last completed milestone version:

```bash
cat .planning/MILESTONES.md 2>/dev/null
```

Extract:
- `{name}` — last completed milestone name from MILESTONES.md

## Output Format

```markdown
---

## ✓ Milestone {name} Complete

Ready to plan the next milestone.

## ▶ Next Up

`/ms:new-milestone` — discover what to build, update PROJECT.md

<sub>`/clear` first → fresh context window</sub>

---

**Next milestone flow:**
1. `/ms:new-milestone` — discover what to build, update PROJECT.md
2. `/ms:research-project` — (optional) research ecosystem
3. `/ms:create-roadmap` — plan how to build it

---
```
