---
name: ms:add-todo
description: Capture idea or task as todo from current conversation context
argument-hint: [optional description]
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
---

<objective>
Capture an idea, task, or issue that surfaces during a Mindsystem session as a structured todo for later work.

Enables "thought → capture → continue" flow without losing context or derailing current work.
</objective>

<context>
@.planning/STATE.md
</context>

<process>

<step name="ensure_directory">
```bash
mkdir -p .planning/todos/pending .planning/todos/done
```
</step>

<step name="check_existing_areas">
```bash
ls .planning/todos/pending/*.md 2>/dev/null | xargs -I {} grep "^area:\|^subsystem:\|^priority:" {} 2>/dev/null | sort -u
```

Note existing areas, subsystems, and priorities for consistency in infer_area step.
</step>

<step name="extract_content">
**With arguments:** Use as the title/focus.
- `/ms:add-todo Add auth token refresh` → title = "Add auth token refresh"

**Without arguments:** Analyze recent conversation to extract:
- The specific problem, idea, or task discussed
- Relevant file paths mentioned
- Technical details (error messages, line numbers, constraints)

Formulate:
- `title`: 3-10 word descriptive title (action verb preferred)
- `problem`: What's wrong or why this is needed
- `solution`: Approach hints or "TBD" if just an idea
- `files`: Relevant paths with line numbers from conversation
- `tags`: 2-5 searchable keywords from context (libraries, error types, concepts)
</step>

<step name="infer_area">
Infer area from file paths:

| Path pattern | Area |
|--------------|------|
| `src/api/*`, `api/*` | `api` |
| `src/components/*`, `src/ui/*` | `ui` |
| `src/auth/*`, `auth/*` | `auth` |
| `src/db/*`, `database/*` | `database` |
| `tests/*`, `__tests__/*` | `testing` |
| `docs/*` | `docs` |
| `.planning/*` | `planning` |
| `scripts/*`, `bin/*` | `tooling` |
| No files or unclear | `general` |

Use existing area from step 2 if similar match exists.

**Subsystem:** Read `jq -r '.subsystems[]' .planning/config.json 2>/dev/null`. Match against file paths and conversation context. Fall back to inferred `area` if no config.json or no match.

**Source (auto-infer from Last Command in STATE.md):**

| Last Command contains | Source |
|---|---|
| `ms:debug` | `debug` |
| `ms:verify-work` | `verify-work` |
| `ms:adhoc` | `adhoc` |
| `ms:audit-milestone` / `ms:plan-milestone-gaps` | `milestone-audit` |
| anything else / no STATE.md | `user-idea` |

**Priority (from conversation context + source-based defaults):**

| Signal | Priority |
|---|---|
| Bug, crash, error, broken, failing, regression keywords | `p1` |
| Enhancement, improvement, refactor, should, missing | `p2` |
| Idea, explore, maybe, consider, nice-to-have | `p3` |

Source-based fallbacks: debug → `p1`, verify-work → `p2`, others → `p3`.

**Phase origin:** Parse current phase from STATE.md `Phase:` line. Use `"none"` if no active phase.
</step>

<step name="check_duplicates">
```bash
grep -l -i "[key words from title]" .planning/todos/pending/*.md 2>/dev/null
```

If potential duplicate found:
1. Read the existing todo
2. Compare scope

If overlapping, use AskUserQuestion:
- header: "Duplicate?"
- question: "Similar todo exists: [title]. What would you like to do?"
- options:
  - "Skip" — keep existing todo
  - "Replace" — update existing with new context
  - "Add anyway" — create as separate todo
</step>

<step name="create_file">
```bash
timestamp=$(date "+%Y-%m-%dT%H:%M")
date_prefix=$(date "+%Y-%m-%d")
```

Generate slug from title (lowercase, hyphens, no special chars).

Write to `.planning/todos/pending/${date_prefix}-${slug}.md`:

```markdown
---
created: [timestamp]
title: [title]
subsystem: [from config.json or area fallback]
tags: [searchable keywords]
priority: p1 | p2 | p3
source: debug | verify-work | adhoc | user-idea | milestone-audit
phase_origin: [current phase or "none"]
area: [area]
files:
  - [file:lines]
---

## Problem

[problem description - enough context for future Claude to understand weeks later]

## Solution

[approach hints or "TBD"]
```
</step>

<step name="update_state">
If `.planning/STATE.md` exists:

1. Count todos: `ls .planning/todos/pending/*.md 2>/dev/null | wc -l`
2. Update "### Pending Todos" under "## Accumulated Context"
</step>

<step name="git_commit">
Commit the todo and any updated state:

```bash
git add .planning/todos/pending/[filename]
[ -f .planning/STATE.md ] && git add .planning/STATE.md
git commit -m "$(cat <<'EOF'
docs: capture todo - [title]

Subsystem: [subsystem] | Priority: [priority] | Source: [source]
EOF
)"
```

Confirm: "Committed: docs: capture todo - [title]"
</step>

<step name="confirm">
```
Todo saved: .planning/todos/pending/[filename]

  [title]
  Subsystem: [subsystem] | Priority: [priority] | Source: [source]
  Phase: [phase_origin]
  Files: [count] referenced

---

Would you like to:

1. Continue with current work
2. Add another todo
3. View all todos (/ms:check-todos)
```
</step>

<step name="update_last_command">
Update `.planning/STATE.md` Last Command field:
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:add-todo $ARGUMENTS | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line
</step>

</process>

<output>
- `.planning/todos/pending/[date]-[slug].md`
- Updated `.planning/STATE.md` (if exists)
</output>

<anti_patterns>
- Don't create todos for work in current plan (that's deviation rule territory)
- Don't create elaborate solution sections — captures ideas, not plans
- Don't block on missing information — "TBD" is fine
</anti_patterns>

<success_criteria>
- [ ] Directory structure exists
- [ ] Todo file created with valid frontmatter
- [ ] Problem section has enough context for future Claude
- [ ] No duplicates (checked and resolved)
- [ ] Subsystem matches config.json vocabulary (or area fallback)
- [ ] Priority auto-inferred from context
- [ ] Source auto-inferred from Last Command
- [ ] Phase origin populated from STATE.md
- [ ] STATE.md updated if exists
- [ ] Todo and state committed to git
</success_criteria>
