# Pre-work Status

Reference for showing what pre-work is done vs still needed for the CURRENT phase. Used by discuss-phase, design-phase, and research-phase.

## Purpose

After completing one pre-work command, show what else is recommended before planning.

## Information to Extract

From ROADMAP.md, get the current phase details:

```bash
grep -A 25 "### Phase ${PHASE}:" .planning/ROADMAP.md
```

Extract:
- `**Research**: Likely/Unlikely (reason)`
- `**Discuss**: Likely/Unlikely (reason)`
- `**Design**: Likely/Unlikely (reason)`

Check what context files already exist:

```bash
PHASE_DIR=$(ls -d .planning/phases/${PHASE}-* 2>/dev/null | head -1)
[ -f "$PHASE_DIR"/*-CONTEXT.md ] && echo "CONTEXT_EXISTS"
[ -f "$PHASE_DIR"/*-DESIGN.md ] && echo "DESIGN_EXISTS"
[ -f "$PHASE_DIR"/*-RESEARCH.md ] && echo "RESEARCH_EXISTS"
```

## Routing Logic

Suggest the next incomplete Likely pre-work:

```
IF Discuss: Likely AND no CONTEXT.md:
  SUGGEST = discuss-phase
ELSE IF Design: Likely AND no DESIGN.md:
  SUGGEST = design-phase
ELSE IF Research: Likely AND no RESEARCH.md:
  SUGGEST = research-phase
ELSE:
  SUGGEST = plan-phase (ready to plan)
```

## Output Format

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
