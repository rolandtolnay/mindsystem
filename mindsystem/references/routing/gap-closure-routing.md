# Gap Closure Routing

Reference for triaging verification gaps by scope and routing to the appropriate primitive. Used by execute-phase and progress commands.

## Purpose

Analyze VERIFICATION.md gaps and recommend the best primitive based on scope and urgency.

## Variables

From calling context:
- `{Z}` — current phase number
- `{Name}` — current phase name
- `{N}/{M}` — must-haves score from VERIFICATION.md
- `{phase_dir}` — phase directory path
- `{phase}` — phase identifier (e.g., "04")

## Information to Extract

Read VERIFICATION.md for the phase:

```bash
cat .planning/phases/${phase_dir}/${phase}-VERIFICATION.md
```

Extract:
- Score (must-haves verified count)
- Gap count and severity (critical vs non-critical)
- Gap summaries from gaps section

## Triage Table

| Scope | Criteria | Route | Rationale |
|-------|----------|-------|-----------|
| Small | 1-2 gaps, localized files, quick fixes | `/ms:adhoc` | Single context window, no multi-plan overhead |
| Larger (blocking) | 3+ gaps OR cross-cutting, blocks next phase | `/ms:insert-phase` | Needs full plan-execute cycle, preserves phase numbering |
| Larger (non-blocking) | 3+ gaps OR cross-cutting, next phase can proceed | `/ms:add-phase` | Defers to end of milestone, no urgency |
| Minor | Cosmetic, non-functional, polish items | `/ms:add-todo` | Capture for later, not worth planning now |

**Judgment calls:**
- If all gaps share the same root cause, treat as small regardless of count
- If gaps span multiple subsystems, prefer insert-phase even if count is low
- Mix routes when gaps vary: adhoc for quick wins + insert-phase for larger items

## Output Format

Present gap summary, then route recommendation using standard "Next Up" format:

```markdown
---

## ⚠ Phase {Z}: {Name} — Gaps Found

**Score:** {N}/{M} must-haves verified
**Report:** .planning/phases/{phase_dir}/{phase}-VERIFICATION.md

### What's Missing

{gap_summaries}

---

## ▶ Next Up

{Primary recommendation based on triage:}

{If adhoc:}
`/ms:adhoc "Close phase {Z} gaps: {brief description}"` — fix {N} localized gaps in a single context

<sub>Reference: `.planning/phases/{phase_dir}/{phase}-VERIFICATION.md`</sub>

{If insert-phase:}
`/ms:insert-phase {Z} "Close verification gaps"` — plan and execute gap closure as phase {Z}.1

{If add-phase:}
`/ms:add-phase "Close phase {Z} verification gaps"` — defer gap closure to end of milestone

{If add-todo:}
`/ms:add-todo "Phase {Z} polish: {brief description}"` — capture for later

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `cat .planning/phases/{phase_dir}/{phase}-VERIFICATION.md` — see full report
- `/ms:verify-work {Z}` — manual testing before fixing
{Include other routes not chosen as alternatives}

---
```
