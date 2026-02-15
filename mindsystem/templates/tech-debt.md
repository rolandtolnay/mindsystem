# Tech Debt Template

Template for `.planning/TECH-DEBT.md` — single source of truth for all tech debt items across milestones.

---

## Usage

Created and updated by `/ms:audit-milestone`. Items persist across milestones. Users reference items manually via `/ms:adhoc` (small fixes) or `/ms:insert-phase` (larger remediation). Loaded automatically by `/ms:plan-phase` for quality/cleanup phases.

**Item IDs** use `TD-{N}` format — monotonically increasing, never reused. New items continue from highest existing ID.

**Sources:** Phase verifications (anti-patterns, non-critical gaps), code review findings, integration checker bugs.

---

## File Template

<template>
```markdown
# Tech Debt

> Single source of truth for tech debt. Updated by `/ms:audit-milestone`.
> Address items via `/ms:adhoc` (1-2 tasks) or `/ms:insert-phase` (larger work).

## {Severity}
<!-- Sections in order: Critical, High, Medium, Low. Omit empty sections. -->

### TD-{N}: {Title}
- **Location:** {file:line or component}
- **Impact:** {what this causes and why it matters}
- **Fix:** {how to address}
- <sub>Phase {source phase} | {verification | integration-check | code-review} | v{milestone}</sub>

---

## Dismissed

> Resolved, deferred, or accepted items. One line each.

- **TD-{N}:** {one-line description} | {location} | v{milestone} | {reason dismissed}
```
</template>

---

## Guidelines

**Severity levels:**
- `Critical` — Breaks behavior or risks data loss. Integration checker bugs (broken cross-phase wiring, failed E2E flows) always map here.
- `High` — Causes cascading changes if left unaddressed. Fragile patterns that spread to new code, missing abstractions forcing workarounds.
- `Medium` — Contained friction. TODOs, missing validation, incomplete error handling. Impact stays local.
- `Low` — Won't compound. Style inconsistencies, minor naming issues, improvement opportunities.

**Severity mapping from sources:**
- Integration checker bugs → Critical
- Code review findings → pass through reviewer severity (High/Medium/Low)
- Phase verification anti-patterns → Medium or Low (blockers go to `gaps`, not tech debt)
- Non-critical verification gaps → Medium

**Empty sections:** Omit severity sections with no items. Keep only sections that contain entries.

**De-duplication:** Match by location + description similarity. An item in Dismissed is never re-added as Active — if the same issue recurs, note it as a new item referencing the original.

**Dismissal reasons:** resolved (fixed), deferred (consciously postponed), accepted (won't fix), superseded (replaced by different approach).
