# Next Phase Routing

Reference for presenting "Next Up" guidance when moving to the next phase. Used by execute-phase and verify-work.

## Purpose

Help user decide between Discuss/Research/Design/Plan for the NEXT phase without referencing external files.

## Information to Extract

From ROADMAP.md, get the next phase details:

```bash
grep -A 25 "### Phase ${NEXT_PHASE}:" .planning/ROADMAP.md
```

Extract:
- Phase name and goal
- `**Research**: Likely/Unlikely (reason)`
- `**Research topics**: ...` (if Likely)
- `**Discuss**: Likely/Unlikely (reason)`
- `**Discuss topics**: ...` (if Likely)
- `**Design**: Likely/Unlikely (reason)`
- `**Design focus**: ...` (if Likely)

Check for existing context files:

```bash
PHASE_DIR=$(ls -d .planning/phases/${NEXT_PHASE}-* 2>/dev/null | head -1)
[ -f "$PHASE_DIR"/*-CONTEXT.md ] && echo "CONTEXT_EXISTS"
[ -f "$PHASE_DIR"/*-DESIGN.md ] && echo "DESIGN_EXISTS"
[ -f "$PHASE_DIR"/*-RESEARCH.md ] && echo "RESEARCH_EXISTS"
```

## Routing Logic

Determine primary suggestion (priority order):

```
IF Discuss: Likely AND no CONTEXT.md:
  PRIMARY = discuss-phase
  REASON = from Discuss parenthetical
ELSE IF Design: Likely AND no DESIGN.md:
  PRIMARY = design-phase
  REASON = from Design parenthetical
ELSE IF Research: Likely AND no RESEARCH.md:
  PRIMARY = research-phase
  REASON = from Research parenthetical
ELSE:
  PRIMARY = plan-phase
  REASON = "ready to plan"
```

## Output Format

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

`/ms:{primary} {N}` — {reason}

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
