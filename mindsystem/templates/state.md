# State Template

Template for `.planning/STATE.md` — the project's living memory.

---

## File Template

```markdown
# Project State

## Project Reference

See: .planning/PROJECT.md (updated [date])

**Core value:** [One-liner from PROJECT.md Core Value section]
**Current focus:** [Current phase name]

## Current Position

Phase: [X] of [Y] ([Phase name])
Plan: [A] of [B] in current phase
Status: [Ready to plan / Planning / Ready to execute / In progress / Phase complete]
Last activity: [YYYY-MM-DD] — [What happened]

Progress: [░░░░░░░░░░] 0%

## Performance Metrics

**Velocity:**
- Total plans completed: [N]
- Average duration: [X] min
- Total execution time: [X.X] hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| - | - | - | - |

**Recent Trend:**
- Last 5 plans: [durations]
- Trend: [Improving / Stable / Degrading]

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Phase X]: [Decision summary]
- [Phase Y]: [Decision summary]

### Pending Todos

[From .planning/todos/pending/ — ideas captured during sessions]

None yet.

### Recent Adhoc Work

[Small work items executed via /ms:do-work]

None yet.

*See `.planning/adhoc/` for full history*

### Blockers/Concerns

[Issues that affect future work]

None yet.
```

<purpose>

STATE.md is the project's short-term memory spanning all phases and sessions.

**Problem it solves:** Information is captured in summaries, issues, and decisions but not systematically consumed. Sessions start without context.

**Solution:** A single, small file that's:
- Read first in every workflow
- Updated after every significant action
- Contains digest of accumulated context
- Enables instant session restoration

</purpose>

<lifecycle>

**Creation:** After ROADMAP.md is created (during init)
- Reference PROJECT.md (read it for current context)
- Initialize empty accumulated context sections
- Set position to "Phase 1 ready to plan"

**Reading:** First step of every workflow
- progress: Present status to user
- plan: Inform planning decisions
- execute: Know current position
- transition: Know what's complete

**Writing:** After every significant action
- execute: After SUMMARY.md created
  - Update position (phase, plan, status)
  - Note new decisions (detail in PROJECT.md)
  - Add blockers/concerns
- transition: After phase marked complete
  - Update progress bar
  - Clear resolved blockers
  - Refresh Project Reference date
- do-work: After adhoc work completed
  - Add entry to "Recent Adhoc Work" section
  - Keep last 5 entries (older entries remain in .planning/adhoc/)

</lifecycle>

<sections>

### Project Reference
Points to PROJECT.md for full context. Includes:
- Core value (the ONE thing that matters)
- Current focus (which phase)
- Last update date (triggers re-read if stale)

Claude reads PROJECT.md directly for requirements, constraints, and decisions.

### Current Position
Where we are right now:
- Phase X of Y — which phase
- Plan A of B — which plan within phase
- Status — current state
- Last activity — what happened most recently
- Progress bar — visual indicator of overall completion

Progress calculation: (completed plans) / (total plans across all phases) × 100%

### Performance Metrics
Track velocity to understand execution patterns:
- Total plans completed
- Average duration per plan
- Per-phase breakdown
- Recent trend (improving/stable/degrading)

Updated after each plan completion.

### Accumulated Context

**Decisions:** Reference to PROJECT.md Key Decisions table, plus recent decisions summary for quick access. Full decision log lives in PROJECT.md.

**Pending Todos:** Ideas captured via /ms:add-todo
- Count of pending todos
- Reference to .planning/todos/pending/
- Brief list if few, count if many (e.g., "5 pending todos — see /ms:check-todos")

**Recent Adhoc Work:** Small fixes executed via /ms:do-work
- Last 5 adhoc work entries
- Format: `- [date]: [description] (.planning/adhoc/[file]-SUMMARY.md)`
- Full history remains in .planning/adhoc/ directory
- Older entries removed from STATE.md but files preserved

**Blockers/Concerns:** From "Next Phase Readiness" sections
- Issues that affect future work
- Prefix with originating phase
- Cleared when addressed

</sections>

<size_constraint>

Keep STATE.md under 100 lines.

It's a DIGEST, not an archive. If accumulated context grows too large:
- Keep only 3-5 recent decisions in summary (full log in PROJECT.md)
- Keep only active blockers, remove resolved ones

The goal is "read once, know where we are" — if it's too long, that fails.

</size_constraint>

<guidelines>

**When created:**
- During project initialization (after ROADMAP.md)
- Reference PROJECT.md (extract core value and current focus)
- Initialize empty sections

**When read:**
- Every workflow starts by reading STATE.md
- Then read PROJECT.md for full context
- Provides instant context restoration

**When updated:**
- After each plan execution (update position, note decisions, update issues/blockers)
- After phase transitions (update progress bar, clear resolved blockers, refresh project reference)
- After adhoc work via /ms:do-work (add entry to "Recent Adhoc Work")

**Size management:**
- Keep under 100 lines total
- Recent decisions only in STATE.md (full log in PROJECT.md)
- Keep only active blockers

**Sections:**
- Project Reference: Pointer to PROJECT.md with core value
- Current Position: Where we are now (phase, plan, status)
- Performance Metrics: Velocity tracking
- Accumulated Context: Recent decisions, pending todos, adhoc work, blockers

</guidelines>
