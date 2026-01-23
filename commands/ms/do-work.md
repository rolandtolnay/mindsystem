---
name: ms:do-work
description: Execute small discovered work without phase overhead (max 2 tasks)
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
Execute small work items discovered during verification or debugging without the overhead of phase insertion or todos.

Bridges the gap between "capture for later" (/ms:add-todo) and "full phase workflow" (/ms:insert-phase).

Use when:
- Work is small (1-2 tasks maximum)
- Work is discovered mid-session (not pre-planned)
- Work can be completed quickly
- Work doesn't require architectural changes
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/do-work.md
@.planning/STATE.md
</execution_context>

<process>

<step name="parse_and_validate">
Parse the work description from $ARGUMENTS.
Validate project has .planning/STATE.md (active Mindsystem project required).
</step>

<step name="analyze_scope">
Quick analysis of what tasks are needed.
If >2 tasks or architectural changes required: REFUSE with suggestion to use /ms:insert-phase.
</step>

<step name="create_lightweight_plan">
Create .planning/adhoc/{timestamp}-{slug}-PLAN.md with minimal structure.
</step>

<step name="execute_tasks">
Execute tasks inline (no subagent for small work).
Apply deviation rules 1-3 (auto-fix bugs, critical, blocking).
If Rule 4 triggered (architectural): STOP, suggest /ms:insert-phase.
</step>

<step name="verify_and_summarize">
Run verify commands from tasks.
Create .planning/adhoc/{timestamp}-{slug}-SUMMARY.md.
</step>

<step name="update_state_and_commit">
Add entry to STATE.md "Recent Adhoc Work" section.
Single git commit with all changes (code + PLAN.md + SUMMARY.md + STATE.md).
</step>

<step name="completion">
Report what was done, show commit hash and file paths.
</step>

</process>

<anti_patterns>
- Don't use for work requiring >2 tasks (use /ms:insert-phase)
- Don't use for work requiring architectural changes
- Don't use outside active Mindsystem projects (needs STATE.md)
- Don't create elaborate plans — this is for quick fixes
- Don't run full goal-backward verification — lightweight checks only
</anti_patterns>

<success_criteria>
Adhoc work is complete when:

- [ ] Work analyzed and confirmed ≤2 tasks
- [ ] .planning/adhoc/ directory exists
- [ ] PLAN.md created with tasks
- [ ] All tasks executed and verified
- [ ] SUMMARY.md created with outcomes
- [ ] STATE.md updated with adhoc entry
- [ ] Single git commit with all changes
- [ ] User informed of completion and commit hash
</success_criteria>
