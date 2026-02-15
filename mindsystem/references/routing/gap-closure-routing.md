# Gap Closure Routing

Reference for presenting "Next Up" guidance when phase verification found gaps. Used by execute-phase and progress commands.

## Purpose

Guide user toward planning gap closure when VERIFICATION.md reports gaps.

## Variables

From calling context:
- `{Z}` — current phase number
- `{Name}` — current phase name
- `{N}/{M}` — must-haves score from VERIFICATION.md
- `{phase_dir}` — phase directory path
- `{phase}` — phase identifier (e.g., "04")
- `{gap_summaries}` — extracted gap summaries from VERIFICATION.md

## Information to Extract

Read VERIFICATION.md for the phase:

```bash
cat .planning/phases/${phase_dir}/${phase}-VERIFICATION.md
```

Extract:
- Score (must-haves verified count)
- Gap summaries from gaps section

## Output Format

```markdown
---

## ⚠ Phase {Z}: {Name} — Gaps Found

**Score:** {N}/{M} must-haves verified
**Report:** .planning/phases/{phase_dir}/{phase}-VERIFICATION.md

### What's Missing

{gap_summaries}

---

## ▶ Next Up

`/ms:plan-phase {Z} --gaps` — create additional plans to complete the phase

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `cat .planning/phases/{phase_dir}/{phase}-VERIFICATION.md` — see full report
- `/ms:verify-work {Z}` — manual testing before planning

---
```

## Gap Closure Flow

After user runs `/ms:plan-phase {Z} --gaps`:
1. Planner reads VERIFICATION.md gaps
2. Creates plans 04, 05, etc. to close gaps
3. User runs `/ms:execute-phase {Z}` again
4. Execute-phase runs incomplete plans (04, 05...)
5. Verifier runs again — loop until passed
