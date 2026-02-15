# Audit Result Routing

Reference for presenting next steps after milestone audit completes. Used by audit-milestone command.

## Purpose

Route user to appropriate next action based on audit status (passed, gaps_found, tech_debt).

## Variables

From calling context:
- `{version}` — milestone version
- `{N}/{M}` — requirements score
- `{status}` — audit result: passed | gaps_found | tech_debt
- `{assumptions_count}` — number of untested assumptions (from UAT)

## Routing Logic

Read the audit status and present the matching section below.

## If Passed

```markdown
## ✓ Milestone {version} — Audit Passed

**Score:** {N}/{M} requirements satisfied
**Report:** .planning/v{version}-MILESTONE-AUDIT.md

All requirements covered. Cross-phase integration verified. E2E flows complete.

{If assumptions_count > 0:}
### Untested Assumptions: {assumptions_count} items

These tests were skipped because required states couldn't be mocked.
See full list in MILESTONE-AUDIT.md. Consider addressing in next milestone.

---

## ▶ Next Up

`/ms:complete-milestone {version}` — archive and tag

<sub>`/clear` first → fresh context window</sub>
```

## If Gaps Found

```markdown
## ⚠ Milestone {version} — Gaps Found

**Score:** {N}/{M} requirements satisfied
**Report:** .planning/v{version}-MILESTONE-AUDIT.md

### Unsatisfied Requirements

{For each unsatisfied requirement:}
- **{REQ-ID}: {description}** (Phase {X})
  - {reason}

### Cross-Phase Issues

{For each integration gap:}
- **{from} → {to}:** {issue}

### Broken Flows

{For each flow gap:}
- **{flow name}:** breaks at {step}

---

## ▶ Next Up

`/ms:plan-milestone-gaps` — create phases to complete milestone

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `cat .planning/v{version}-MILESTONE-AUDIT.md` — see full report
- `/ms:complete-milestone {version}` — proceed anyway (accept tech debt)
```

## If Tech Debt (no blockers but accumulated debt)

```markdown
## ⚡ Milestone {version} — Tech Debt Review

**Score:** {N}/{M} requirements satisfied
**Report:** .planning/v{version}-MILESTONE-AUDIT.md

All requirements met. No critical blockers. Accumulated tech debt needs review.

**Tech debt tracked:** .planning/TECH-DEBT.md ({tech_debt_count} active items)

Address items using:
- `/ms:adhoc` — for small fixes (1-2 tasks)
- `/ms:insert-phase` — for larger remediation

{If assumptions_count > 0:}
### Untested Assumptions: {assumptions_count} items

These tests were skipped because required states couldn't be mocked.
See full list in MILESTONE-AUDIT.md. Consider addressing in next milestone.

---

## ▶ Options

- `/ms:complete-milestone {version}` — accept debt, track in backlog
- `/ms:plan-milestone-gaps` — address debt before completing

<sub>`/clear` first → fresh context window</sub>
```
