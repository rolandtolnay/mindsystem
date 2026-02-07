---
description: Work on an existing Linear ticket — fetch, explore, clarify, plan, implement, commit, and close
argument-hint: "<ticket-id>"
---

<objective>
End-to-end workflow for implementing a Linear ticket. Gathers all context needed for planning (ticket details, codebase exploration, requirement clarification), then hands off to Claude Code's built-in plan mode for planning and execution. After implementation, prompts for commit and ticket state update.

**Prerequisite:** Enter plan mode in Claude Code before running this command.

Usage: `/work-ticket MIN-42`
</objective>

<context>
Ticket ID: $ARGUMENTS

Fetch ticket details:
```bash
uv run ~/.claude/skills/linear/scripts/linear.py get $ARGUMENTS --json-pretty
```
</context>

<process>

<step name="fetch_ticket">
Parse the ticket JSON response. Extract:
- **Title** and **description** (the core requirements)
- **Priority** and **estimate** (scope signal)
- **State** (confirm it's not already done)
- **Comments** (may contain clarifications)
- **Parent issue** (if sub-issue, fetch parent for broader context)
- **Relations** (blocking/blocked-by tickets)

If the ticket has comments, fetch them:
```bash
uv run ~/.claude/skills/linear/scripts/linear.py get $ARGUMENTS -c --json-pretty
```

Present a brief summary of the ticket to the user.
</step>

<step name="scan_skills">
Read available skill descriptions from the system context. Identify skills relevant to the ticket's domain:
- Flutter/Dart ticket → load `flutter-senior-review`, `flutter-code-quality`, `flutter-code-simplification`
- Debugging ticket → load `debug-like-expert`
- Mindsystem ticket → load `ms-meta`

If a relevant skill applies, invoke it with the Skill tool so its guidance is available during planning.
</step>

<step name="explore_codebase">
Launch parallel Explore agents to understand the areas the ticket touches. Base search terms on ticket title, description, and any file/component names mentioned.

Typical explorations (run in parallel):
1. **Architecture search** — Find files, modules, and patterns related to the ticket's domain
2. **Convention search** — Find existing patterns for the type of change described (e.g., how similar features are implemented)
3. **Dependency search** — Find code that depends on or is depended upon by the target area

Collect findings: relevant files, existing patterns, constraints, potential conflicts.
</step>

<step name="clarify_requirements">
Contrast ticket requirements against codebase findings. Identify gaps:
- Ambiguous acceptance criteria
- Missing technical details (which API, which component, which pattern to follow)
- Edge cases not addressed in the ticket
- Conflicts between ticket description and existing code

Use AskUserQuestion with concrete options to close each gap. Batch into a single call (max 4 questions). If no gaps exist, skip this step.
</step>

<step name="plan">
All context is now gathered. Write the implementation plan using the plan file and call ExitPlanMode for user approval. Claude Code's built-in planning handles format and structure.

Include the ticket ID ($ARGUMENTS) in the plan title for traceability.
</step>

<step name="implement">
After plan approval, Claude Code executes the plan. No special instructions — follow the approved plan.
</step>

<step name="prompt_commit">
After implementation, present a summary of all changes made.

Use AskUserQuestion:
- "Changes look good — ready to commit"
- "I want to make adjustments first"
- "Run additional verification"

If the user wants adjustments, iterate until satisfied. Do NOT proceed to commit until the user explicitly confirms.

Once confirmed, invoke `/commit-commands:commit`.
</step>

<step name="prompt_close_ticket">
After commit, ask the user before updating ticket state.

Use AskUserQuestion:
- "Mark $ARGUMENTS as done"
- "Change state to something else"
- "Leave ticket state as-is"

If user chooses done:
```bash
uv run ~/.claude/skills/linear/scripts/linear.py done $ARGUMENTS --json-pretty
```

If user chooses another state, execute the appropriate state change.
</step>

</process>

<success_criteria>
- Ticket details fetched and understood
- Relevant skills loaded based on ticket domain
- Codebase explored for context before planning
- Requirement gaps closed via user clarification
- Implementation plan approved via plan mode
- All changes implemented
- User confirmed changes before committing
- Commit created via /commit skill
- Ticket state updated per user choice
</success_criteria>
