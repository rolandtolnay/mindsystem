---
name: ms:add-todo
description: Capture idea or task as todo from current conversation context
argument-hint: [optional description]
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

<objective>
Capture an idea, task, or issue that surfaces during a Mindsystem session as a structured todo for later work.
</objective>

<process>

<step name="ensure_directory">
```bash
mkdir -p .planning/todos/done
```
</step>

<step name="extract_content">
**With arguments:** Use as the title/focus.
- `/ms:add-todo Add auth token refresh` -> title = "Add auth token refresh"

**Without arguments:** Analyze recent conversation to extract:
- The specific problem, idea, or task discussed
- Technical details (error messages, constraints)

Formulate:
- `title`: 3-10 word descriptive title (action verb preferred)
- `problem`: What's wrong or why this is needed — enough context for future Claude
- `solution`: Approach hints or "TBD" if just an idea
</step>

<step name="infer_metadata">
Infer priority, estimate, and subsystem from description and conversation context.

**Priority (1-4):**

| Priority | Label | Signal |
|----------|-------|--------|
| 1 | Urgent | Blocks other work, crash, data loss, security |
| 2 | High | Significant user impact, important bug, key feature gap |
| 3 | Normal | Standard work, moderate improvements |
| 4 | Low | Nice-to-have, minor polish, exploration |

**Estimate (XS/S/M/L/XL):**

| Size | Points | Typical scope |
|------|--------|---------------|
| XS | 1 | Config change, one-liner, typo fix |
| S | 2 | Single function/component, simple bug fix |
| M | 3 | Feature touching 2-3 files, moderate complexity |
| L | 5 | Multi-file feature, new subsystem area |
| XL | 8 | Cross-cutting concern, architectural change |

**Subsystem:** Read `ms-tools config-get subsystems`. Match against description and conversation context. Must match config.json vocabulary.
</step>

<step name="confirm">
Single AskUserQuestion showing inferred metadata. User confirms or adjusts.

- header: "Todo"
- question: "Confirm todo details:\n\n**{title}**\nPriority: {priority} | Estimate: {estimate} | Subsystem: {subsystem}"
- options:
  - "Looks good" — create as shown
  - "Adjust" — change priority, estimate, or subsystem

If user selects "Adjust", ask which fields to change and re-confirm.
</step>

<step name="create_file">
```bash
timestamp=$(date "+%Y-%m-%dT%H:%M")
date_prefix=$(date "+%Y-%m-%d")
```

Generate slug from title (lowercase, hyphens, no special chars).

Write to `.planning/todos/${date_prefix}-${slug}.md`:

```markdown
---
title: [title]
created: [YYYY-MM-DDTHH:MM]
priority: [1-4]
estimate: [XS|S|M|L|XL]
subsystem: [from config.json]
---

## Problem
[problem description — enough context for future Claude]

## Solution
[approach hints or "TBD"]
```
</step>

<step name="git_commit">
```bash
git add .planning/todos/[filename]
git commit -m "$(cat <<'EOF'
todo: [title] [subsystem|priority|estimate]
EOF
)"
```
</step>

<step name="confirm_output">
```
Todo saved: .planning/todos/[filename]

  [title]
  Subsystem: [subsystem] | Priority: [priority] | Estimate: [estimate]

Use /ms:adhoc to address todos anytime.
```
</step>

</process>

<anti_patterns>
- Don't create todos for work in current plan (that's deviation rule territory)
- Don't create elaborate solution sections — captures ideas, not plans
- Don't block on missing information — "TBD" is fine
</anti_patterns>

<success_criteria>
- [ ] Problem section has enough context for future Claude
- [ ] Subsystem matches config.json vocabulary
- [ ] Priority and estimate inferred from context, confirmed by user
- [ ] Todo committed to git
</success_criteria>
