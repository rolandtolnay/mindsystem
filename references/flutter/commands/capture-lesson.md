---
description: Capture lessons from Flutter/Dart refactorings into reusable docs for future LLM code writers. Use after completing a refactoring.
argument-hint: [refactoring-description] [commit_sha]
allowed-tools: [AskUserQuestion, Bash, Read, Grep, Glob, Write]
---

<objective>
Analyze Flutter/Dart code changes from a refactoring and distill lessons into a standalone reference file. The command (an LLM) derives lessons from the diff — the code changes were produced by an LLM, so diff analysis IS the primary source of insight.

Output: a `.md` file in `docs/lessons/` optimized for LLM consumption with enough clarity for human review.

Scope sits between `learn-flutter` (one-liner code quality rules) and `extract-pattern` (comprehensive playbooks). A lesson captures the "why" and "watch out for" from a specific refactoring — typically 2-4 insights with code examples.
</objective>

<context>
Refactoring description: $ARGUMENTS (may be empty if invoked mid-conversation with prior context)

Git state:
!`git status --porcelain | head -20`
!`git diff --stat | tail -5`
</context>

<developer_role>
The developer's involvement in the refactoring is directional — they spotted a problem, gave high-level instructions, and reviewed the LLM's output. They did NOT author individual line changes.

The developer uniquely knows:
- What looked wrong in the original code (the trigger)
- The high-level direction given
- Whether the result is satisfactory

The developer does NOT uniquely know:
- Why specific code patterns were chosen (the LLM decided)
- Trade-offs between approaches (the LLM evaluated)

Constrain all AskUserQuestion interactions to what the developer can actually answer. The command derives lessons from the diff; the developer provides framing and validation.
</developer_role>

<output_format_spec>
Lesson files are optimized for LLM consumption — terse, actionable, with concrete code.

**Principles:**
- Insights: 1-2 sentences stating the transformation + what's non-obvious, with `inline code`
- Code blocks show before/after — complete, copy-pasteable
- Rules distill insights into terse one-liners for quick reference (mechanically extractable for skill synthesis)
- Single Anti-Patterns section (merged pitfalls + bad patterns) with concrete bad code
- "Applies when" trigger for future injection decisions
- No filler: no "You should", "It is recommended", "Make sure to", "IMPORTANT:"

**Structure template:**
```markdown
# Lesson: Descriptive Title

One-line scope: what was refactored, what was wrong with the old approach.

**Domain:** state-management | navigation | error-handling | data-layer | ui-structure | forms | testing | etc.
**Applies when:** concrete trigger condition for when this lesson is relevant

## [Insight Title]

1-2 sentences: what the transformation is and what's non-obvious about it. Reference `specific classes` and `patterns`.

```dart
// Before: brief label
oldApproach();

// After: brief label
newApproach();
```

## [Another Insight]

...

## Rules

- Terse one-liner with `inline code` (distilled from insights above)
- Transformation: `old_pattern` → `new_pattern`

## Anti-Patterns (flag these)

- Bad pattern (`concrete.bad.code()`) → fix
- Pitfall: situation that causes subtle bugs → what to do instead
```

**Sizing:** A typical lesson file is 40-70 lines. 2-4 insight sections, 3-6 rules, 3-6 anti-patterns.
</output_format_spec>

<context_efficiency>
Write the lesson file directly — user reviews in their editor or via `git diff`.

- No "present draft in conversation" step — write the file, then ask for feedback
- Iterate via targeted edits, not full rewrites
</context_efficiency>

<process>

## 1. Establish Scope

### 1.1 Assess Available Context

Check three sources for refactoring context:
1. **$ARGUMENTS** — explicit description and optional commit SHA
2. **Conversation history** — prior messages may describe the refactoring, its motivation, and the user's vision
3. **Git state** — uncommitted changes or recent commits

Parse $ARGUMENTS for a commit SHA (7+ hex chars; verify with `git rev-parse --verify <sha>^{commit}`, treat as description text if verification fails).

If $ARGUMENTS and conversation history already describe what was refactored, skip to Step 1.2.

If the scope is unclear, use AskUserQuestion — phrase it around what the developer actually knows:
```
Question: "What did you notice was wrong with the code before this refactoring?"
Header: "Trigger"
Options: [2-4 concrete interpretations based on $ARGUMENTS and conversation context]
```

### 1.2 Determine Change Source

If there's an obvious target (commit SHA in arguments, or uncommitted changes present, or conversation indicates the source), use it directly.

Otherwise, use AskUserQuestion:
```
Question: "What code changes should I analyze?"
Header: "Changes"
Options:
- "Uncommitted changes" — Current work in progress (git diff)
- "Specific commits" — A commit or range (I'll provide refs)
- "All changes on branch" — Everything since branching from main
```

Gather changes based on source:
- Uncommitted: `git diff --cached` and `git diff`
- Specific commits: `git show <commit>` or `git diff <from>..<to>`
- Branch changes: `git diff main...HEAD`

For large diffs (20+ files), focus on files most relevant to the refactoring description. Skip auto-generated files, lock files, and config churn.

## 2. Analyze Changes

### 2.1 Read the Diff

Study the full diff. Identify:
- What patterns were replaced and with what
- Structural changes (file moves, class splits, inheritance changes)
- New abstractions introduced or old ones removed
- Error handling, state management, or API changes

### 2.2 Read Changed Files for Full Context

The diff shows deltas but not surrounding code. Read the current state of the 3-5 most significant changed files — prioritize:
- Files demonstrating the new pattern most clearly
- Files with the largest logical changes
- Files that had the most issues in the old approach

Use Grep/Glob to find related files if the diff references patterns, base classes, or utilities not in the changeset.

## 3. Derive Lessons

This is the core step. The command (an LLM) analyzes the before→after transformation to derive:

- **Insights**: What was the core improvement? What's non-obvious about the new approach? What would an LLM writing fresh code get wrong without this knowledge?
- **Rules**: Terse distillation for quick LLM reference
- **Anti-patterns**: What does the "bad" version look like? What pitfalls would an LLM fall into?
- **Trigger condition**: When should a future LLM apply these lessons?

Assign a **domain tag** matching the primary area of the refactoring.

Derive the filename slug from the refactoring description — $ARGUMENTS, conversation context, or the dominant theme in the diff (lowercase, hyphens, max 4-5 words).

## 4. Validate with Developer

Before writing the file, briefly present the proposed lessons in conversation — list each insight as a one-liner. Use AskUserQuestion:

```
Question: "I derived these lessons from the changes. Anything off or missing?"
Header: "Validate"
Options:
1. "Looks right" — Write the file
2. "Missing something" — I'll describe what's missing
3. "Something's wrong" — I'll point out what's off
```

This is a validation gate, not an authoring step. The developer confirms direction; they don't need to articulate the code-level details.

## 5. Write Lesson File

Create `docs/lessons/` directory if it doesn't exist:
```bash
mkdir -p docs/lessons
```

Write directly to `docs/lessons/{slug}.md`.

**Quality checks before writing:**
- Each insight is 1-2 sentences with `inline code` — states the transformation and the non-obvious part
- Code blocks show before/after with enough context to be copy-pasteable
- Rules section has terse one-liners distilled from the insights
- Anti-patterns section has concrete bad code (merged pitfalls + patterns)
- "Applies when" trigger is specific enough for future injection decisions
- No filler words, no emphasis markers, no `IMPORTANT:` prefixes
- All code blocks use ```dart fencing
- Domain tag and "Applies when" line are present
- One-line scope captures what was wrong with the old approach

Report: file path, line count, number of insights, domain tag.

## 6. Review

Use AskUserQuestion:
```
Question: "Lesson file written. Review in your editor — what's next?"
Header: "Review"
Options:
1. "Looks good" — Done
2. "Needs adjustments" — I'll describe what to change
3. "Too verbose" — Compress further
```

Apply targeted edits if changes needed.

</process>

<success_criteria>
- Lessons derived from diff analysis by the command, not dictated by the developer
- Developer validates direction (trigger, completeness) — not asked to explain code-level decisions
- "Applies when" trigger present and specific enough for future injection
- Insights are 1-2 sentences with `inline code` + before/after code blocks
- Rules section has terse one-liners mechanically extractable for skill synthesis
- Anti-patterns section merges pitfalls and bad patterns with concrete code
- File written directly to `docs/lessons/{slug}.md`
</success_criteria>
