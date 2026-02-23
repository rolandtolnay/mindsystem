<required_reading>

**Read these files NOW:**

1. `.planning/STATE.md`
2. `.planning/PROJECT.md`
3. `.planning/ROADMAP.md`
4. Current phase's plan files (`*-PLAN.md`)
5. Current phase's summary files (`*-SUMMARY.md`)

</required_reading>

<purpose>

Mark current phase complete and advance to next. This is the natural point where progress tracking and PROJECT.md evolution happen.

"Planning next phase" = "current phase is done"

</purpose>

<process>

<step name="load_project_state" priority="first">

Before transition, read project state:

```bash
cat .planning/STATE.md 2>/dev/null
cat .planning/PROJECT.md 2>/dev/null
```

Parse current position to verify we're transitioning the right phase.
Note accumulated context that may need updating after transition.

</step>

<step name="verify_completion">

Check current phase has all plan summaries:

```bash
ls .planning/phases/XX-current/*-PLAN.md 2>/dev/null | sort
ls .planning/phases/XX-current/*-SUMMARY.md 2>/dev/null | sort
```

**Verification logic:**

- Count PLAN files
- Count SUMMARY files
- If counts match: all plans complete
- If counts don't match: incomplete

**If all plans complete:**

```
⚡ Auto-approved: Transition Phase [X] → Phase [X+1]
Phase [X] complete — all [Y] plans finished.

Proceeding to mark done and advance...
```

Proceed directly to cleanup_handoff step.

**If plans incomplete:**

**SAFETY RAIL: Skipping incomplete plans is destructive — always confirm.**

Present:

```
Phase [X] has incomplete plans:
- {phase}-01-SUMMARY.md ✓ Complete
- {phase}-02-SUMMARY.md ✗ Missing
- {phase}-03-SUMMARY.md ✗ Missing

⚠️ Safety rail: Skipping plans requires confirmation (destructive action)

Options:
1. Continue current phase (execute remaining plans)
2. Mark complete anyway (skip remaining plans)
3. Review what's left
```

Wait for user decision.

</step>

<step name="update_roadmap">

Update the roadmap file:

```bash
ROADMAP_FILE=".planning/ROADMAP.md"
```

Update the file:

- Mark current phase: `[x] Complete`
- Add completion date
- Update plan count to final (e.g., "3/3 plans complete")
- Update Progress table
- Keep next phase as `[ ] Not started`

**Example:**

```markdown
## Phases

- [x] Phase 1: Foundation (completed 2025-01-15)
- [ ] Phase 2: Authentication ← Next
- [ ] Phase 3: Core Features

## Progress

| Phase             | Plans Complete | Status      | Completed  |
| ----------------- | -------------- | ----------- | ---------- |
| 1. Foundation     | 3/3            | Complete    | 2025-01-15 |
| 2. Authentication | 0/2            | Not started | -          |
| 3. Core Features  | 0/1            | Not started | -          |
```

</step>

<step name="archive_prompts">

If prompts were generated for the phase, they stay in place.
The `completed/` subfolder pattern from create-meta-prompts handles archival.

</step>

<step name="evolve_project">

Evolve PROJECT.md to reflect learnings from completed phase.

**Read phase summaries:**

```bash
cat .planning/phases/XX-current/*-SUMMARY.md
```

**Assess requirement changes:**

1. **Requirements validated?**
   - Any requirements shipped in this phase?
   - Add to Validated with phase reference: `- ✓ [Requirement] — Phase X`

2. **Requirements invalidated?**
   - Any requirements discovered to be unnecessary or wrong?
   - Add to Out of Scope with reason: `- [Requirement] — [why invalidated]`

3. **Business context evolved?**
   - Has understanding of audience, problem, or differentiation changed?
   - Update Who It's For, Core Problem, or How It's Different if so
   - New key flows emerged? → Update Key User Flows

4. **Decisions to log?**
   - Extract decisions from SUMMARY.md files
   - Add to Key Decisions table with outcome if known

5. **"What This Is" still accurate?**
   - If the product has meaningfully changed, update the description
   - Keep it current and accurate

**Update PROJECT.md:**

Make the edits inline. Update "Last updated" footer:

```markdown
---
*Last updated: [date] after Phase [X]*
```

**Example evolution:**

Before:

```markdown
## Validated

- ✓ Canvas drawing tools — Phase 1

## Out of Scope

- OAuth2 — complexity not needed for v1
```

After (Phase 2 shipped JWT auth, discovered rate limiting needed):

```markdown
## Validated

- ✓ Canvas drawing tools — Phase 1
- ✓ JWT authentication — Phase 2

## Out of Scope

- OAuth2 — complexity not needed for v1
- Offline mode — real-time is core value, discovered Phase 2
```

**Step complete when:**

- [ ] Phase summaries reviewed for learnings
- [ ] Shipped requirements added to Validated
- [ ] Invalidated requirements added to Out of Scope with reason
- [ ] Business context sections reviewed (Who It's For, Core Problem, How It's Different, Key User Flows)
- [ ] New decisions logged with rationale
- [ ] "What This Is" updated if product changed
- [ ] "Last updated" footer reflects this transition

</step>

<step name="update_current_position_after_transition">

Update Current Position section in STATE.md to reflect phase completion and transition.

**Format:**

```markdown
Phase: [next] of [total] ([Next phase name])
Plan: Not started
Status: Ready to plan
Last activity: [today] — Phase [X] complete, transitioned to Phase [X+1]

Progress: [updated progress bar]
```

**Instructions:**

- Increment phase number to next phase
- Reset plan to "Not started"
- Set status to "Ready to plan"
- Update last activity to describe transition
- Recalculate progress bar based on completed plans

**Example — transitioning from Phase 2 to Phase 3:**

Before:

```markdown
## Current Position

Phase: 2 of 4 (Authentication)
Plan: 2 of 2 in current phase
Status: Phase complete
Last activity: 2025-01-20 — Completed 02-02-PLAN.md

Progress: ███████░░░ 60%
```

After:

```markdown
## Current Position

Phase: 3 of 4 (Core Features)
Plan: Not started
Status: Ready to plan
Last activity: 2025-01-20 — Phase 2 complete, transitioned to Phase 3

Progress: ███████░░░ 60%
```

**Step complete when:**

- [ ] Phase number incremented to next phase
- [ ] Plan status reset to "Not started"
- [ ] Status shows "Ready to plan"
- [ ] Last activity describes the transition
- [ ] Progress bar reflects total completed plans

</step>

<step name="update_project_reference">

Update Project Reference section in STATE.md.

```markdown
## Project Reference

See: .planning/PROJECT.md (updated [today])

**Core value:** [Current core value from PROJECT.md]
**Current focus:** [Next phase name]
```

Update the date and current focus to reflect the transition.

</step>

<step name="review_accumulated_context">

Review and update Accumulated Context section in STATE.md.

**Decisions:**

- Note recent decisions from this phase (3-5 max)
- Full log lives in PROJECT.md Key Decisions table

**Blockers/Concerns:**

- Review blockers from completed phase
- If addressed in this phase: Remove from list
- If still relevant for future: Keep with "Phase X" prefix
- Add any new concerns from completed phase's summaries

**Example:**

Before:

```markdown
### Blockers/Concerns

- ⚠️ [Phase 1] Database schema not indexed for common queries
- ⚠️ [Phase 2] WebSocket reconnection behavior on flaky networks unknown
```

After (if database indexing was addressed in Phase 2):

```markdown
### Blockers/Concerns

- ⚠️ [Phase 2] WebSocket reconnection behavior on flaky networks unknown
```

**Step complete when:**

- [ ] Recent decisions noted (full log in PROJECT.md)
- [ ] Resolved blockers removed from list
- [ ] Unresolved blockers kept with phase prefix
- [ ] New concerns from completed phase added

</step>

<step name="update_session_continuity_after_transition">

Update Session Continuity section in STATE.md to reflect transition completion.

**Format:**

```markdown
Last session: [today]
Stopped at: Phase [X] complete, ready to plan Phase [X+1]
```

**Step complete when:**

- [ ] Last session timestamp updated to current date and time
- [ ] Stopped at describes phase completion and next phase

</step>

<step name="offer_next_phase">

**MANDATORY: Verify milestone status before presenting next steps.**

**Step 1: Read ROADMAP.md and identify phases in current milestone**

Read the ROADMAP.md file and extract:
1. Current phase number (the phase just transitioned from)
2. All phase numbers in the current milestone section

To find phases, look for:
- Phase headers: lines starting with `### Phase` or `#### Phase`
- Phase list items: lines like `- [ ] **Phase X:` or `- [x] **Phase X:`

Count total phases and identify the highest phase number in the milestone.

State: "Current phase is {X}. Milestone has {N} phases (highest: {Y})."

**Step 2: Route based on milestone status**

| Condition | Meaning | Action |
|-----------|---------|--------|
| current phase < highest phase | More phases remain | Go to **Route A** |
| current phase = highest phase | Milestone complete | Go to **Route B** |

---

**Route A: More phases remain in milestone**

Read ROADMAP.md to get the next phase's name and goal.

**If next phase exists:**

```
Phase [X] marked complete.

Next: Phase [X+1] — [Name]

⚡ Auto-continuing: Plan Phase [X+1] in detail
```

Exit skill and invoke SlashCommand("/ms:plan-phase [X+1]")

---

**Route B: Milestone complete (all phases done)**

```
Phase {X} marked complete.

🎉 Milestone is 100% complete — all {N} phases finished!

⚡ Auto-continuing: Complete milestone and archive
```

Exit skill and invoke SlashCommand("/ms:complete-milestone")

</step>

</process>

<implicit_tracking>

Progress tracking is IMPLICIT:

- "Plan phase 2" → Phase 1 must be done (or ask)
- "Plan phase 3" → Phases 1-2 must be done (or ask)
- Transition workflow makes it explicit in ROADMAP.md

No separate "update progress" step. Forward motion IS progress.

</implicit_tracking>

<partial_completion>

If user wants to move on but phase isn't fully complete:

```
Phase [X] has incomplete plans:
- {phase}-02-PLAN.md (not executed)
- {phase}-03-PLAN.md (not executed)

Options:
1. Mark complete anyway (plans weren't needed)
2. Defer work to later phase
3. Stay and finish current phase
```

Respect user judgment — they know if work matters.

**If marking complete with incomplete plans:**

- Update ROADMAP: "2/3 plans complete" (not "3/3")
- Note in transition message which plans were skipped

</partial_completion>

<success_criteria>

Transition is complete when:

- [ ] Current phase plan summaries verified (all exist or user chose to skip)
- [ ] Any stale handoffs deleted
- [ ] ROADMAP.md updated with completion status and plan count
- [ ] PROJECT.md evolved (requirements, decisions, description if needed)
- [ ] STATE.md updated (position, project reference, context, session)
- [ ] Progress table updated
- [ ] User knows next steps

</success_criteria>
