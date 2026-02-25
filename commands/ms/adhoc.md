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
Execute work discovered mid-session with knowledge-aware planning and execution — the key differentiator vs vanilla Claude plan mode.

Knowledge flows in both directions:
- **Input:** Prior decisions, established patterns, and pitfalls inform the plan
- **Output:** Learnings from execution feed back into knowledge files

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
</step>

<step name="load_knowledge">
Read config.json subsystems, match relevant knowledge files to work description.
</step>

<step name="explore_codebase">
Spawn 1-3 parallel Explore agents based on work scope and loaded knowledge.
</step>

<step name="present_and_clarify">
Synthesize exploration findings with knowledge context.
Present approach to user, AskUserQuestion for gaps or decisions.
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
Commit artifacts, update STATE.md, report completion.
</step>

</process>

<success_criteria>
Adhoc work is complete when:

- [ ] Knowledge files loaded before exploration
- [ ] Codebase explored with relevant findings
- [ ] PLAN.md created in per-execution subdirectory
- [ ] All tasks executed by ms-executor
- [ ] Phase-style SUMMARY.md created for consolidator compatibility
- [ ] Code review completed (or skipped per config)
- [ ] Patch file generated at `{exec_dir}/adhoc-01-changes.patch`
- [ ] Knowledge files updated via ms-consolidator
- [ ] STATE.md updated with adhoc entry
- [ ] Git commit with all changes
- [ ] User informed of completion
</success_criteria>
