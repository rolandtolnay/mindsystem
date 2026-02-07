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
- `{X.Y}` — last completed milestone version

## Output Format

```markdown
---

## ✓ Milestone v{X.Y} Complete

Ready to plan the next milestone.

## ▶ Next Up

**Discuss Next Milestone** — figure out what to build next

`/ms:discuss-milestone`

<sub>`/clear` first → fresh context window</sub>

---

**Next milestone flow:**
1. `/ms:discuss-milestone` — thinking partner, creates context file
2. `/ms:new-milestone` — update PROJECT.md with new goals
3. `/ms:research-project` — (optional) research ecosystem
4. `/ms:define-requirements` — scope what to build
5. `/ms:create-roadmap` — plan how to build it

---
```
