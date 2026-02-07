---
name: ms:check-todos
description: List pending todos and select one to work on
argument-hint: [subsystem or priority filter]
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
---

<objective>
List all pending todos, allow selection, load full context for the selected todo, and route to appropriate action.

Enables reviewing captured ideas and deciding what to work on next.
</objective>

<context>
@.planning/STATE.md
@.planning/ROADMAP.md
</context>

<process>

<step name="check_exist">
```bash
TODO_COUNT=$(ls .planning/todos/pending/*.md 2>/dev/null | wc -l | tr -d ' ')
echo "Pending todos: $TODO_COUNT"
```

If count is 0:
```
No pending todos.

Todos are captured during work sessions with /ms:add-todo.

---

Would you like to:

1. Continue with current phase (/ms:progress)
2. Add a todo now (/ms:add-todo)
```

Exit.
</step>

<step name="parse_filter">
Support multi-field filtering:
- `/ms:check-todos` → show all
- `/ms:check-todos p1` → filter to priority:p1 only (matches `p[1-3]`)
- `/ms:check-todos api` → filter to subsystem or area matching "api"
</step>

<step name="list_todos">
```bash
for file in .planning/todos/pending/*.md; do
  created=$(grep "^created:" "$file" | cut -d' ' -f2)
  title=$(grep "^title:" "$file" | cut -d':' -f2- | xargs)
  priority=$(grep "^priority:" "$file" | cut -d' ' -f2)
  subsystem=$(grep "^subsystem:" "$file" | cut -d' ' -f2)
  area=$(grep "^area:" "$file" | cut -d' ' -f2)
  echo "${priority:-p3}|${subsystem:-${area:-general}}|$created|$title|$file"
done | sort
```

Old-format todos (missing priority/subsystem) default to `p3`/`general`.

Apply filter if specified:
- Priority filter (`p1`-`p3`): match priority field
- Subsystem/area filter: match either subsystem or area field

Priority-grouped display with sequential numbering across groups. Omit empty groups. Use subsystem label (fall back to area, then "general"):

```
Pending Todos (N):

### p1 — Urgent
  1. auth: Fix token refresh race condition (2d ago)
  2. api: Handle rate limit 429 responses (1d ago)

### p2 — Important
  3. ui: Add loading states to dashboard (5h ago)

### p3 — Ideas
  4. general: Explore caching strategy (3d ago)

---

Reply with a number to view details, or:
- `/ms:check-todos [subsystem]` to filter by subsystem
- `/ms:check-todos p1` to filter by priority
- `q` to exit
```

Format age as relative time.
</step>

<step name="handle_selection">
Wait for user to reply with a number.

If valid: load selected todo, proceed.
If invalid: "Invalid selection. Reply with a number (1-[N]) or `q` to exit."
</step>

<step name="load_context">
Read the todo file completely. Display:

```
## [title]

**Subsystem:** [subsystem] | **Priority:** [priority] | **Source:** [source]
**Phase Origin:** [phase_origin]
**Created:** [date] ([relative time] ago)
**Tags:** [tags or "None"]
**Files:** [list or "None"]

### Problem
[problem section content]

### Solution
[solution section content]
```

Gracefully omit missing fields for old-format todos.

If `files` field has entries, read and briefly summarize each.
</step>

<step name="check_roadmap">
```bash
ls .planning/ROADMAP.md 2>/dev/null && echo "Roadmap exists"
```

If roadmap exists:
1. Check if todo's subsystem or area matches an upcoming phase
2. Check if todo's files overlap with a phase's scope
3. Check if todo's tags match phase keywords
4. Note any match for action options
</step>

<step name="offer_actions">
**If todo maps to a roadmap phase:**

Use AskUserQuestion:
- header: "Action"
- question: "This todo relates to Phase [N]: [name]. What would you like to do?"
- options:
  - "Work on it now" — move to done, start working
  - "Add to phase plan" — include when planning Phase [N]
  - "Brainstorm approach" — think through before deciding
  - "Put it back" — return to list

**If no roadmap match:**

Use AskUserQuestion:
- header: "Action"
- question: "What would you like to do with this todo?"
- options:
  - "Work on it now" — move to done, start working
  - "Create a phase" — /ms:add-phase with this scope
  - "Brainstorm approach" — think through before deciding
  - "Put it back" — return to list
</step>

<step name="execute_action">
**Work on it now:**
```bash
mv ".planning/todos/pending/[filename]" ".planning/todos/done/"
```
Update STATE.md todo count. Present problem/solution context. Begin work or ask how to proceed.

**Add to phase plan:**
Note todo reference in phase planning notes. Keep in pending. Return to list or exit.

**Create a phase:**
Display: `/ms:add-phase [description from todo]`
Keep in pending. User runs command in fresh context.

**Brainstorm approach:**
Keep in pending. Start discussion about problem and approaches.

**Put it back:**
Return to list_todos step.
</step>

<step name="update_state">
After any action that changes todo count:

```bash
ls .planning/todos/pending/*.md 2>/dev/null | wc -l
```

Update STATE.md "### Pending Todos" section if exists.
</step>

<step name="git_commit">
If todo was moved to done/, commit the change:

```bash
git add .planning/todos/done/[filename]
git rm --cached .planning/todos/pending/[filename] 2>/dev/null || true
[ -f .planning/STATE.md ] && git add .planning/STATE.md
git commit -m "$(cat <<'EOF'
docs: start work on todo - [title]

Moved to done/, beginning implementation.
EOF
)"
```

Confirm: "Committed: docs: start work on todo - [title]"
</step>

</process>

<output>
- Moved todo to `.planning/todos/done/` (if "Work on it now")
- Updated `.planning/STATE.md` (if todo count changed)
</output>

<anti_patterns>
- Don't delete todos — move to done/ when work begins
- Don't start work without moving to done/ first
- Don't create plans from this command — route to /ms:plan-phase or /ms:add-phase
</anti_patterns>

<success_criteria>
- [ ] All pending todos listed grouped by priority (p1/p2/p3)
- [ ] Subsystem label displayed (with area/general fallback for old todos)
- [ ] Priority or subsystem filter applied if specified
- [ ] Selected todo's full context loaded (subsystem, priority, source, phase, tags)
- [ ] Old-format todos handled gracefully (missing fields omitted)
- [ ] Roadmap context checked for phase match (subsystem, area, files, tags)
- [ ] Appropriate actions offered
- [ ] Selected action executed
- [ ] STATE.md updated if todo count changed
- [ ] Changes committed to git (if todo moved to done/)
</success_criteria>
