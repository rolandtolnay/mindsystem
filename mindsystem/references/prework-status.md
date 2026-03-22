# Pre-work Status

Reference for showing what pre-work is done vs still needed for the CURRENT phase. Used by discuss-phase, design-phase, and research-phase.

## Purpose

After completing one pre-work command, show what else is recommended before planning.

## Data

Run `ms-tools prework-status` to get pre-work flags, completion status, and routing suggestion:

```bash
ms-tools prework-status "${PHASE}"
```

Output includes phase name, goal, pre-work flags with status (done/not started), existing artifacts, and the suggested next command with reason.

## Output Format

Use the `prework-status` output to populate this template:

```markdown
---

## Pre-work Status: Phase {N}

| Pre-work | Recommended | Status |
|----------|-------------|--------|
| Discuss | {Likely/Unlikely} | {✓ Done / ✗ Not started / - Not needed} |
| Design | {Likely/Unlikely} | {✓ Done / ✗ Not started / - Not needed} |
| Research | {Likely/Unlikely} | {✓ Done / ✗ Not started / - Not needed} |

{If any Likely items are not done:}
### Suggested

`/ms:{next-prework} {N}` — {reason from roadmap}

{If all Likely items are done OR none were Likely:}
### Ready to Plan

`/ms:plan-phase {N}`

<sub>`/clear` first → fresh context window</sub>

---
```

## Example: After discuss-phase

```markdown
---

## Pre-work Status: Phase 3

| Pre-work | Recommended | Status |
|----------|-------------|--------|
| Discuss | Likely | ✓ Done |
| Design | Likely | ✗ Not started |
| Research | Unlikely | - |

### Suggested

`/ms:design-phase 3` — significant new UI

<sub>`/clear` first → fresh context window</sub>

---
```

## Example: All pre-work complete

```markdown
---

## Pre-work Status: Phase 4

| Pre-work | Recommended | Status |
|----------|-------------|--------|
| Discuss | Unlikely | ✓ Done |
| Design | Unlikely | - |
| Research | Likely | ✓ Done |

### Ready to Plan

`/ms:plan-phase 4`

<sub>`/clear` first → fresh context window</sub>

---
```
