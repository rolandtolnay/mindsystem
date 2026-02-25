---
name: ms:compound
description: Compound code changes into knowledge files
argument-hint: "[commit, file path, or description]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>
Compound code changes into the knowledge system. Use when work was done outside the Mindsystem pipeline and knowledge files need updating.

Input modes:
- **Git reference:** SHA, range (`HEAD~3..HEAD`), or any git ref
- **File path:** Path to a changed file
- **Description:** Free-text description of changes
- **No args:** Infer from current conversation context
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/compound.md
</execution_context>

<process>

<step name="parse_input">
Determine input mode from $ARGUMENTS: git ref, file path, description, or no-args (conversation context).
Validate active project: check `.planning/config.json` exists.
</step>

<step name="resolve_change_context">
Gather lightweight change context. Git mode: diff stats. File mode: recent git log. Description mode: spawn Explore agents to find relevant changes.
</step>

<step name="determine_subsystems">
Read config.json subsystems, match changes against subsystem names. Detect potential new subsystems.
</step>

<step name="confirm_with_user">
Present affected subsystems and change summary. AskUserQuestion to confirm, adjust, or cancel.
</step>

<step name="spawn_compounder">
Spawn ms-compounder with input mode, change reference, confirmed subsystems, and subsystem vocabulary.
</step>

<step name="finalize">
Update config.json if new subsystems confirmed. Commit knowledge file changes. Set last command.
</step>

</process>

<success_criteria>
- [ ] No knowledge files or full diffs read in main context
- [ ] User confirmed subsystem routing before compounder spawned
- [ ] config.json updated if new subsystems detected and confirmed
- [ ] Changes committed
- [ ] Knowledge files updated for confirmed subsystems
</success_criteria>
