# Next Phase Routing

Reference for presenting "Next Up" guidance for a phase. Used by progress (current phase) and verify-work (next phase).

## Purpose

Help user decide between Discuss/Research/Design/Plan for a target phase using ROADMAP.md pre-work flags.

## Data

Run `ms-tools prework-status` to get phase info, pre-work status, and routing suggestion:

```bash
ms-tools prework-status "${TARGET_PHASE}"
```

Output includes phase name, goal, pre-work flags with status (done/not started), existing artifacts, and the suggested next command with reason.

## Output Format

Use the `prework-status` output to populate this template:

```markdown
---

## ▶ Next Up

**Phase {N}: {Name}** — {Goal}

### Pre-work Recommendations

{Show only flags that are Likely, with their topics/focus}

| Pre-work | Status | Topics/Focus |
|----------|--------|--------------|
| Discuss | Likely | {discuss topics} |
| Design | Likely | {design focus} |
| Research | Likely | {research topics} |

{If all Unlikely: "No pre-work flagged — ready to plan directly."}

{If any context files exist: "*Already have: CONTEXT.md*"}

### Suggested

`/ms:{suggested command} {N}` — {reason}

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
{List commands that are NOT the primary}
- `/ms:discuss-phase {N}` — clarify vision
- `/ms:design-phase {N}` — create UI/UX specs
- `/ms:research-phase {N}` — investigate approach
- `/ms:plan-phase {N}` — plan directly

---
```

## Example: UI-heavy phase

```markdown
## ▶ Next Up

**Phase 3: User Dashboard** — Users can view and manage their content

### Pre-work Recommendations

| Pre-work | Status | Topics/Focus |
|----------|--------|--------------|
| Discuss | Likely | dashboard layout, what metrics matter |
| Design | Likely | dashboard cards, navigation, empty states |

### Suggested

`/ms:discuss-phase 3` — assumes grid layout, unclear what metrics matter

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:design-phase 3` — create UI/UX specs
- `/ms:plan-phase 3` — plan directly
```

## Example: Backend phase with research

```markdown
## ▶ Next Up

**Phase 4: Payment Integration** — Users can purchase premium features

### Pre-work Recommendations

| Pre-work | Status | Topics/Focus |
|----------|--------|--------------|
| Discuss | Likely | assumes one-time payments only, unclear if subscriptions needed, refund policy unspecified |
| Research | Likely | Stripe API, webhook handling, idempotency |

### Suggested

`/ms:discuss-phase 4` — assumes one-time payments, subscription model unclear

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:research-phase 4` — external API integration
- `/ms:plan-phase 4` — plan directly
```

## Example: Ready to plan

```markdown
## ▶ Next Up

**Phase 2: Authentication** — Users can securely access accounts

### Pre-work Recommendations

No pre-work flagged — ready to plan directly.

*Already have: CONTEXT.md, RESEARCH.md*

### Suggested

`/ms:plan-phase 2` — ready to plan

<sub>`/clear` first → fresh context window</sub>
```
