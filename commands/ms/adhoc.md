---
name: ms:adhoc
description: Execute discovered work with knowledge-aware planning and execution
argument-hint: <description>
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>
Execute work discovered mid-session with knowledge-aware planning and execution.

Use when:
- Work is discovered mid-session (not pre-planned)
- Work can be completed in a single context window
- Work doesn't require multi-phase orchestration

For larger work requiring wave-based parallelization or multi-plan coordination, use `/ms:insert-phase`.
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/adhoc.md
@.planning/STATE.md
</execution_context>

<process>

<step name="parse_and_validate">
Parse work description from $ARGUMENTS.
Validate STATE.md exists (active Mindsystem project required).
If task_tracker configured and input matches ticket ID, lazy-load tracker reference and follow its detection process.
</step>

<step name="load_knowledge">
Read config.json subsystems, match relevant knowledge files to work description.
</step>

<step name="explore_codebase">
Spawn 1-3 parallel Explore agents based on work scope and loaded knowledge.
</step>

<step name="present_and_clarify">
Present briefing with assumptions marked by confidence (high/medium/low).
AskUserQuestion: always validate assumptions; add questions only for genuine behavioral ambiguity the user must resolve.
Guardrail: never ask about technical approach, error handling, or implementation details — only user intent, expected behavior, scope boundaries.
</step>

<step name="spawn_plan_writer">
Create execution directory, assemble context, spawn ms-adhoc-planner.
</step>

<step name="review_plan">
Read generated plan, show summary to user, allow edits.
</step>

<step name="spawn_executor">
Spawn ms-executor with plan path and SUMMARY output path.
</step>

<step name="code_review">
Per config.json `code_review.adhoc` setting — spawn code review agent or skip.
</step>

<step name="generate_patch">
Generate patch file from adhoc commits via `ms-tools generate-adhoc-patch`.
</step>

<step name="consolidate_knowledge">
Spawn ms-consolidator on execution directory to update knowledge files.
</step>

<step name="cleanup_and_report">
Commit artifacts, update STATE.md, report completion. When ticket detected, finalize per loaded tracker reference.
</step>

</process>

<success_criteria>
- [ ] Knowledge files updated via ms-consolidator
- [ ] STATE.md "Recent Adhoc Work" section updated with new entry
- [ ] Code review executed (or explicitly skipped per config)
- [ ] Patch file generated if adhoc commits exist
- [ ] `ms-tools set-last-command` called with adhoc command
- [ ] Phase-style SUMMARY.md created for consolidator compatibility
- [ ] All artifacts committed
- [ ] Ticket finalized when tracker configured (comment posted, commit attached, state → Done)
</success_criteria>
