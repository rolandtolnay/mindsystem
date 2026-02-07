# Tech Debt Template

Template for `.planning/TECH-DEBT.md` — single source of truth for all tech debt items across milestones.

---

## Usage

Created and updated by `/ms:audit-milestone`. Items persist across milestones. Users reference items manually via `/ms:adhoc` (small fixes) or `/ms:insert-phase` (larger remediation).

**Item IDs** use `TD-{N}` format — monotonically increasing, never reused. New items continue from highest existing ID.

**Sources:** Phase verifications (anti-patterns, non-critical gaps), code review findings.

---

## File Template

<template>
```markdown
# Tech Debt

> Single source of truth for tech debt. Updated by `/ms:audit-milestone`.
> Address items via `/ms:adhoc` (1-2 tasks) or `/ms:insert-phase` (larger work).

## Active Items

### TD-{N}: {Title}
- **Phase:** {source phase, e.g. 03-chat}
- **Source:** {verification | code-review | anti-pattern}
- **Severity:** {blocker | warning | info}
- **Location:** {file:line or component}
- **Impact:** {what this causes}
- **Suggested fix:** {how to address}
- **Related files:** {other affected files}
- **Identified:** v{milestone} | {YYYY-MM-DD}

---

## Dismissed

> Resolved, deferred, or accepted items. One line each.

- **TD-{N}:** {one-line description} | {location} | v{milestone} | {reason dismissed}
```
</template>

---

## Guidelines

**Severity levels:**
- `blocker` — Prevents future work or degrades reliability. Rare in tech debt (blockers usually go to `gaps`).
- `warning` — Indicates incomplete or fragile code. Common for TODOs, missing validation, stubs.
- `info` — Notable but low impact. Style issues, minor inconsistencies, improvement opportunities.

**De-duplication:** Match by location + description similarity. An item in Dismissed is never re-added as Active — if the same issue recurs, note it as a new item referencing the original.

**Dismissal reasons:** resolved (fixed), deferred (consciously postponed), accepted (won't fix), superseded (replaced by different approach).
