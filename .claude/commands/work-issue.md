---
description: Work on a GitHub issue — fetch, explore, reproduce, brainstorm, plan, implement, and close
argument-hint: "<issue-number>"
---

<objective>
End-to-end workflow for resolving a GitHub issue. Fetches the issue, explores the codebase for context, attempts reproduction for bugs, collaborates with the user on approach, plans the implementation, then comments and closes the issue.

Usage: `/work-issue 42`
</objective>

<context>
Issue number: $ARGUMENTS
Repository: !`git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]//' | sed 's/.git$//'`
</context>

<process>

<step name="load_project_context" priority="first">
Invoke the `ms-meta` skill via the Skill tool before proceeding. This loads Mindsystem's architecture, design principles, and conventions — required context for making correct decisions about any fix or feature.
</step>

<step name="fetch_issue">
Fetch the issue details using `gh`:

```bash
gh issue view $ARGUMENTS --json title,body,labels,state,comments,assignees
```

Extract and present:
- **Title** and **body** (the core problem or request)
- **Labels** (bug, enhancement, feature — determines workflow path)
- **State** (confirm it's open)
- **Comments** (may contain additional context, reproduction steps, or workarounds)
- **Assignees**

Present a brief summary to the user.

Classify the issue type based on labels and content:
- **Bug** — something is broken, crashes, or behaves incorrectly
- **Enhancement/Feature** — new functionality or improvement
- **Other** — documentation, chore, refactor, etc.
</step>

<step name="explore_codebase">
Launch 3 parallel Explore agents to understand the areas the issue touches. Base search terms on the issue title, body, and any file/component names mentioned.

Run in parallel:
1. **Impact search** — Find files, modules, and code paths related to the issue's domain. Trace the execution flow from entry point to the reported behavior.
2. **Pattern search** — Find existing patterns for the type of change described (how similar issues were solved, conventions in the affected area)
3. **Dependency search** — Find code that depends on or is depended upon by the target area. Identify blast radius of potential changes.

After agents return, read the key files yourself — do not rely solely on agent summaries.
</step>

<step name="reproduce">
**For bugs only.** Skip this step for enhancements, features, and non-bug issues.

Assess whether the bug is deterministic and reproducible in the current environment:
- Script failures, crashes, parse errors → attempt direct reproduction
- UI bugs, environment-specific issues, race conditions → note as not locally reproducible

If reproducible:
1. Set up minimal reproduction conditions based on the issue description
2. Run the failing code path and capture the output
3. Confirm the reported behavior matches what you observe
4. Note any additional context gained from reproduction (stack traces, exact error messages, edge cases)

Present reproduction results to the user. If you cannot reproduce, state why and proceed — the issue may still be valid.
</step>

<step name="brainstorm">
**Stop and collaborate with the user before planning.**

Present your findings:
1. **Issue understanding** — What the issue reports, verified against codebase exploration and any reproduction results
2. **Root cause** (for bugs) or **Current state** (for features) — What exists today and why the issue occurs
3. **Key files and code paths** — The specific files involved, with line references
4. **Proposed approaches** — 2-3 solution directions with trade-offs (effort, risk, maintainability, scope)

Use AskUserQuestion to get the user's direction. Iterate until the approach is confirmed.
</step>

<step name="plan">
Enter plan mode.

Include the issue number (#$ARGUMENTS) in the plan title for traceability.

Design the implementation based on the confirmed approach from brainstorming.

**The plan MUST include these final steps after all implementation steps (always present, always last):**

1. **Verify changes** — present a summary of all changes made
2. **Commit** — ask the user to confirm changes are ready, then invoke `/commit-commands:commit`. The commit message MUST reference `#$ARGUMENTS` (e.g., `fix: handle comma-separated phase lists (#1)`).
3. **Comment on issue with solution summary** — after the commit succeeds, post a comment using:
   ```bash
   gh issue comment $ARGUMENTS --body "$(cat <<'EOF'
   [Summary of solution: approach chosen, files changed, notable decisions]
   EOF
   )"
   ```
4. **Close the issue** — this is a SEPARATE step:
   ```bash
   gh issue close $ARGUMENTS
   ```
   Verify the close succeeded.
</step>

</process>

<success_criteria>
- Issue closed (explicitly verified, not assumed)
- Solution summary comment posted on the issue
- Commit message references #$ARGUMENTS for git-GitHub traceability
- Reproduction attempted for bug-type issues
- Solution direction confirmed by user before planning — requirement gaps surfaced and closed
</success_criteria>
