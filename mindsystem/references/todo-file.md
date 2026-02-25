<todo_file>

## Todo Detection

When `$ARGUMENTS` matches a `.planning/todos/*.md` file path and the file exists:

Read the file and parse:
- **YAML frontmatter:** `title`, `subsystem`, `priority`, `estimate`
- **Body:** `## Problem` and `## Solution` sections

Use todo title as work description. Feed problem/solution as additional context.

If the file doesn't exist: treat `$ARGUMENTS` as free-text description. No error — proceed normally.

## Planner Context

When spawning the plan writer with todo context, include in the prompt:
- Todo title, subsystem, problem, and solution hints
- Instruct planner to use title format: `# Adhoc: {Todo Title}`
- Instruct planner to include todo problem/solution in the Context section
- Instruct planner to use todo's subsystem for plan inline metadata (`**Subsystem:**`)

## Executor Instructions

When spawning the executor with a todo, instruct it to include the todo filename (without path or extension) in commit message suffixes (e.g., `feat(adhoc-auth): description (2026-02-20-add-logout)`).

## Finalization

Run after knowledge consolidation. Move the todo file to `done/` and append an outcome section.

**Move to done:**
```bash
TODO_DIR=$(dirname "$TODO_PATH")
mkdir -p "${TODO_DIR}/done"
mv "$TODO_PATH" "${TODO_DIR}/done/$(basename "$TODO_PATH")"
```

**Append outcome:** Read SUMMARY.md and extract solution summary (key decisions, files modified). Append to the moved file:

```markdown

## Outcome
[Solution summary from SUMMARY.md — key decisions, files modified]
```

**Stage moved file:**
```bash
git add "${TODO_DIR}/done/$(basename "$TODO_PATH")"
```

## Commit Message Suffix

Append ` (todo-filename)` to the consolidation commit message when todo-driven, where `todo-filename` is the basename without `.md` extension.

## Report Additions

When todo was finalized, append to completion report:
```
**Todo:** [filename]
- Moved to: .planning/todos/done/[filename]
- Outcome appended: yes
```
</todo_file>
