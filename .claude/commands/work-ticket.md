---
description: Work on an existing Linear ticket — fetch, explore, clarify, plan, implement, commit, and close
argument-hint: "<ticket-id>"
---

<objective>
End-to-end workflow for implementing a Linear ticket. Gathers all context needed for planning (ticket details, codebase exploration, requirement clarification), then writes a plan that includes implementation, commit, and ticket state update. The plan is self-contained — all steps survive the context reset between planning and execution.

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
**Thoroughness is more important than speed.** Do not rush to planning.

First, get a high-level project overview:
```bash
eza --tree --git-ignore -L 3
```

Then launch parallel Explore agents to deeply understand the areas the ticket touches. Base search terms on ticket title, description, and any file/component names mentioned.

Typical explorations (run in parallel):
1. **Architecture search** — Find files, modules, and patterns related to the ticket's domain
2. **Convention search** — Find existing patterns for the type of change described (e.g., how similar features are implemented)
3. **Dependency search** — Find code that depends on or is depended upon by the target area

After agents return, read the key files yourself. Do not rely solely on agent summaries — open and read the actual files you will need to modify or reference.

Collect findings: relevant files, existing patterns, constraints, potential conflicts.
</step>

<step name="clarify_requirements">
**Do NOT proceed to planning until you have 95% confidence that you know what to build.**

Contrast ticket requirements against codebase findings. Actively look for:
- Ambiguous acceptance criteria
- Missing technical details (which API, which component, which pattern to follow)
- Edge cases not addressed in the ticket
- Conflicts between ticket description and existing code
- Behavioral questions (what happens when X? should Y also change?)
- Scope boundaries (what is explicitly NOT part of this ticket?)

Use AskUserQuestion with concrete options to close each gap. Ask as many rounds of questions as needed — multiple calls to AskUserQuestion are expected and encouraged. Do not batch unrelated questions just to minimize calls.

**Default assumption: there ARE gaps.** Tickets are written by humans for humans and almost always underspecify implementation details. If you believe there are zero gaps, state your understanding of the requirements in detail and ask the user to confirm before proceeding.
</step>

<step name="plan">
All context is now gathered. Write the implementation plan using the plan file and call ExitPlanMode for user approval. Claude Code's built-in planning handles format and structure.

Include the ticket ID ($ARGUMENTS) in the plan title for traceability.

**The plan MUST include these final steps after all implementation steps:**

1. **Verify changes** — present a summary of all changes made
2. **Commit** — ask the user to confirm changes are ready, then invoke `/commit-commands:commit`
3. **Update ticket** — ask the user whether to mark $ARGUMENTS as done:
   - If done: `uv run ~/.claude/skills/linear/scripts/linear.py done $ARGUMENTS --json-pretty`
   - If another state: execute the appropriate state change
   - If leave as-is: skip

These steps survive the context reset because they are written into the plan itself.
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
