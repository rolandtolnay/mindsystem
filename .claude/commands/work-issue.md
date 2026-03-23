---
description: Work on a GitHub issue — fetch, explore, reproduce, brainstorm, plan, implement, and close
argument-hint: "<issue-number>"
---

<objective>
End-to-end workflow for resolving a GitHub issue. Progresses through four distinct phases — Orient, Understand, Solve, Execute — each with a clear purpose and decision point. The user always knows what phase they're in and what comes next.

Usage: `/work-issue 42`
</objective>

<context>
Issue number: $ARGUMENTS
Repository: !`git remote get-url origin 2>/dev/null | sed 's/.*github.com[:/]//' | sed 's/.git$//'`
</context>

<process>

<!-- ═══════════════════════════════════════════════════════ -->
<!-- PHASE 1: ORIENT                                        -->
<!-- Purpose: Gather context and set expectations            -->
<!-- ═══════════════════════════════════════════════════════ -->

<step name="load_project_context" priority="first">
Invoke the `ms-meta` skill via the Skill tool before proceeding. This loads Mindsystem's architecture, design principles, and conventions — required context for making correct decisions about any fix or feature.
</step>

<step name="fetch_issue">
Fetch the issue details using `gh`:

```bash
gh issue view $ARGUMENTS --json title,body,labels,state,comments,assignees
```

Extract:
- **Title** and **body** (the core problem or request)
- **Labels** (bug, enhancement, feature — determines workflow path)
- **State** (confirm it's open)
- **Comments** (may contain additional context, reproduction steps, or workarounds)
- **Assignees**

Classify the issue type based on labels and content:
- **Bug** — something is broken, crashes, or behaves incorrectly
- **Enhancement/Feature** — new functionality or improvement
- **Other** — documentation, chore, refactor, etc.
</step>

<step name="announce_workflow">
Present the issue summary, then announce the workflow phases so the user knows what to expect:

> **#$ARGUMENTS: [issue title]**
> [1-2 sentence summary of the issue]
>
> Here's how we'll work through this:
> 1. **Understand** — I'll explore the codebase [and reproduce the bug if applicable]. I'll check in with you on anything I'm unsure about.
> 2. **Solve** — I'll break down the problem and propose solution approaches for you to choose from.
> 3. **Execute** — Once we've agreed on an approach, I'll plan, implement, commit, and close the issue.
>
> Starting with exploration now.

This is informational — do not wait for confirmation. Proceed immediately.
</step>

<!-- ═══════════════════════════════════════════════════════ -->
<!-- PHASE 2: UNDERSTAND                                    -->
<!-- Purpose: Deep codebase knowledge + validated requirements -->
<!-- User decision: "Are the requirements right?"            -->
<!-- ═══════════════════════════════════════════════════════ -->

<step name="explore_codebase">
Launch parallel Explore agents to understand the areas the issue touches. Base search terms on the issue title, body, and any file/component names mentioned.

Run in parallel:
1. **Impact search** — Find files, modules, and code paths related to the issue's domain. Trace the execution flow from entry point to the reported behavior.
2. **Pattern search** — Find existing patterns for the type of change described (how similar issues were solved, conventions in the affected area)
3. **Dependency search** — Find code that depends on or is depended upon by the target area. Identify blast radius of potential changes.

After agents return, read the key files yourself — do not rely solely on agent summaries.
</step>

<step name="reproduce">
**For bugs only.** Skip this step for enhancements, features, and non-bug issues.

Assess whether the bug is deterministic and reproducible in the current environment:
- Script failures, crashes, parse errors -> attempt direct reproduction
- UI bugs, environment-specific issues, race conditions -> note as not locally reproducible

If reproducible:
1. Set up minimal reproduction conditions based on the issue description
2. Run the failing code path and capture the output
3. Confirm the reported behavior matches what you observe
4. Note any additional context gained from reproduction (stack traces, exact error messages, edge cases)

Present reproduction results to the user. If you cannot reproduce, state why and proceed — the issue may still be valid.
</step>

<step name="validate_requirements">
**Do NOT proceed to the Solve phase until you have 95% confidence that you know what to build or fix.**

Issues are written by humans for humans and almost always underspecify. Claude knows code, user knows intent. This step closes the information asymmetry gap.

**Present your understanding:**

> **Phase 2: Understand** — Here's what I found and what I think needs to happen.

- **For bugs:** Root cause analysis — what's actually broken and why, grounded in exploration and reproduction results
- **For features:** What the issue requires (your interpretation of acceptance criteria)
- High-confidence assumptions — state these as facts, not questions. Example: "This follows the existing pattern in `PhaseRunner`."
- Conflicts or gaps between issue description and existing code

**Resolve gaps actively:**

For each medium or low-confidence assumption, ask a **separate, focused AskUserQuestion**. Do not bundle multiple gaps into one question — each gap is its own decision.

Frame each question with the codebase context you discovered during exploration so the user has what they need to answer. Example:
> "The issue says 'improve error handling' but doesn't specify recovery behavior. The existing `PlanExecutor` retries once then fails hard. Should this new error path follow the same pattern, or did you have something different in mind?"

**Ask only about:** user intent, expected behavior, scope boundaries.
**Do not ask about** technical pattern selection or implementation details the user can't meaningfully influence.

**If no gaps exist** (all assumptions are high-confidence), present your understanding and ask a single confirmation:
> "I'm confident I understand the requirements. [1-2 sentence summary]. Does this match your expectations, or should I adjust anything before I move to proposing solutions?"

**On corrections:** Absorb user feedback. Do not re-present the full understanding — proceed with updated context.
</step>

<!-- ═══════════════════════════════════════════════════════ -->
<!-- PHASE 3: SOLVE                                         -->
<!-- Purpose: First-principles decomposition + solution options -->
<!-- User decision: "Which approach?" or "Here's my own"    -->
<!-- This is THE key decision point of the workflow          -->
<!-- ═══════════════════════════════════════════════════════ -->

<step name="design_solutions">
**Do NOT enter plan mode yet.** Decompose the problem to its fundamentals, then propose solutions.

> **Phase 3: Solve** — Now that requirements are clear, here's my analysis and proposed approaches.

**First-principles decomposition:**

1. **Irreducible requirements** — What must be true regardless of implementation approach? Strip away conventions and list as bullet points.

2. **Current situation** — What exists in the codebase today: relevant patterns, current behavior, key files. Note which existing patterns are load-bearing (must follow) vs. conventional (could depart from).

3. **Constraints** — Hard constraints (API contracts, data formats, backwards compatibility) vs. soft constraints (existing conventions, team preferences).

**Scale the number of proposals to actual decision space:**

- **One obvious approach** (clear bug fix, straightforward change): Present the single approach with a brief note on why alternatives were dismissed. Still frame it against the irreducible requirements to confirm coverage.

- **Genuine design latitude** (multiple valid paths): Present **2-3 approaches**, each structured as:
  - **Approach name** — one-line summary
  - **How it works** — concrete description of what changes where
  - **Tradeoffs** — what you gain and what you give up, evaluated against the irreducible requirements
  - **Convention vs. departure** — note where this follows existing patterns and where it breaks new ground, with rationale for departures

**For each approach, verify:** Does it satisfy every irreducible requirement? If not, flag the gap explicitly.

**After presenting approaches:**


> If you'd like to evaluate these through a specific lens, you can use a mental framework — for example `/consider:opportunity-cost`, `/consider:second-order`, or `/consider:via-negativa`.

Then ask the user to choose:
> Which approach would you like to go with? You can also propose a different direction entirely.

**This is a collaboration checkpoint** — wait for user input. The user may pick an approach, combine elements from multiple proposals, challenge the decomposition, or propose something entirely different. Engage fully; proceed to planning only when the user explicitly signals readiness.
</step>

<!-- ═══════════════════════════════════════════════════════ -->
<!-- PHASE 4: EXECUTE                                       -->
<!-- Purpose: Plan, implement, commit, close                -->
<!-- User decision: "Ready to commit?"                      -->
<!-- ═══════════════════════════════════════════════════════ -->

<step name="plan">
Enter plan mode.

> **Phase 4: Execute** — Implementing the agreed approach.

Include the issue number (#$ARGUMENTS) in the plan title for traceability.

Design the implementation based on the confirmed approach from the Solve phase.

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
- Requirements validated through active gap resolution before solution design
- Solution approach selected by user from first-principles-grounded proposals
- Issue closed (explicitly verified, not assumed)
- Solution summary comment posted on the issue
- Commit message references #$ARGUMENTS for git-GitHub traceability
- Reproduction attempted for bug-type issues
</success_criteria>
