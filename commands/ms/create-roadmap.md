---
name: ms:create-roadmap
description: Create roadmap with phases for the project
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
  - Glob
  - Task
---

<objective>
Create project roadmap with phase breakdown.

Roadmaps define what work happens in what order. Phases map to requirements.

Run after `/ms:define-requirements`.

**Improvement:** Spawns ms-roadmapper agent for heavy lifting, presents roadmap for approval before committing.
</objective>

<execution_context>
@~/.claude/mindsystem/references/principles.md
@~/.claude/mindsystem/templates/roadmap.md
@~/.claude/mindsystem/templates/state.md
@~/.claude/mindsystem/references/goal-backward.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/config.json
@.planning/REQUIREMENTS.md
@.planning/research/SUMMARY.md (if exists)
</context>

<process>

<step name="validate">
```bash
# Verify project exists
[ -f .planning/PROJECT.md ] || { echo "ERROR: No PROJECT.md found. Run /ms:new-project first."; exit 1; }

# Verify requirements exist
[ -f .planning/REQUIREMENTS.md ] || { echo "ERROR: No REQUIREMENTS.md found. Run /ms:define-requirements first."; exit 1; }
```
</step>

<step name="check_existing">
Check if roadmap already exists:

```bash
[ -f .planning/ROADMAP.md ] && echo "ROADMAP_EXISTS" || echo "NO_ROADMAP"
```

**If ROADMAP_EXISTS:**
Use AskUserQuestion:
- header: "Roadmap exists"
- question: "A roadmap already exists. What would you like to do?"
- options:
  - "View existing" — Show current roadmap
  - "Replace" — Create new roadmap (will overwrite)
  - "Cancel" — Keep existing roadmap

If "View existing": `cat .planning/ROADMAP.md` and exit
If "Cancel": Exit
If "Replace": Continue
</step>

<step name="spawn_roadmapper">
**Calculate starting phase number:**

```bash
# Find highest existing phase number
LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '[0-9]+' | head -1)

if [ -n "$LAST_PHASE" ]; then
  # Remove leading zeros for arithmetic
  LAST_NUM=$((10#$LAST_PHASE))
  START_PHASE=$((LAST_NUM + 1))
  echo "Existing phases found. New phases will start at: $START_PHASE"
else
  START_PHASE=1
  echo "No existing phases. Starting at Phase 1"
fi
```

Spawn ms-roadmapper agent with full context:

```
Task(
  subagent_type="ms-roadmapper",
  prompt="""
<planning_context>

**Project:**
@.planning/PROJECT.md

**Requirements:**
@.planning/REQUIREMENTS.md

**Starting phase number:** $START_PHASE

**Research (if exists):**
@.planning/research/SUMMARY.md

**Config:**
@.planning/config.json

</planning_context>

<instructions>
Create roadmap:
1. Derive phases from requirements (don't impose structure)
2. **Start phase numbering at $START_PHASE** (not 1, unless this is the first milestone)
3. Map every v1 requirement to exactly one phase
4. Derive 2-5 success criteria per phase (observable user behaviors)
5. Validate 100% coverage
6. Write files immediately (ROADMAP.md, STATE.md, update REQUIREMENTS.md traceability)
7. Return ROADMAP CREATED with summary

Write files first, then return. This ensures artifacts persist even if context is lost.
</instructions>
""",
  description="Create roadmap"
)
```
</step>

<step name="handle_return">
**If `## ROADMAP BLOCKED`:**
- Present blocker information
- Work with user to resolve
- Re-spawn when resolved

**If `## ROADMAP CREATED`:**

Read the created ROADMAP.md and present it inline:

```
---

## Proposed Roadmap

**[N] phases** | **[X] requirements mapped** | All v1 requirements covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 1 | [Name] | [Goal] | [REQ-IDs] | [count] |
| 2 | [Name] | [Goal] | [REQ-IDs] | [count] |
...

### Phase Details

**Phase 1: [Name]**
Goal: [goal]
Requirements: [REQ-IDs]
Success criteria:
1. [criterion]
2. [criterion]
Pre-work: Research [Likely/Unlikely] | Discuss [Likely/Unlikely] | Design [Likely/Unlikely]
{If any Likely: topics/focus on next line}

**Phase 2: [Name]**
Goal: [goal]
Requirements: [REQ-IDs]
Success criteria:
1. [criterion]
2. [criterion]
Pre-work: Research [Likely/Unlikely] | Discuss [Likely/Unlikely] | Design [Likely/Unlikely]
{If any Likely: topics/focus on next line}

[... continue for all phases ...]

---
```
</step>

<step name="approval_gate">
**CRITICAL: Ask for approval before committing:**

Use AskUserQuestion:
- header: "Roadmap"
- question: "Does this roadmap structure work for you?"
- options:
  - "Approve" — Commit and continue
  - "Adjust phases" — Tell me what to change
  - "Review full file" — Show raw ROADMAP.md

**If "Approve":** Continue to commit step.

**If "Adjust phases":**
- Get user's adjustment notes (ask inline what they want to change)
- Re-spawn roadmapper with revision context:
  ```
  Task(
    subagent_type="ms-roadmapper",
    prompt="""
<revision>
User feedback on roadmap:
[user's notes]

Current ROADMAP.md: @.planning/ROADMAP.md

Update the roadmap based on feedback. Edit files in place.
Return ROADMAP REVISED with changes made.
</revision>
""",
    description="Revise roadmap"
  )
  ```
- Present revised roadmap
- Loop until user approves

**If "Review full file":** Display raw `cat .planning/ROADMAP.md`, then re-ask approval.
</step>

<step name="commit">
After user approval:

```bash
git add .planning/ROADMAP.md .planning/STATE.md .planning/REQUIREMENTS.md
git commit -m "$(cat <<'EOF'
docs: create roadmap ([N] phases)

Phases:
1. [phase-name]: [requirements covered]
2. [phase-name]: [requirements covered]
...

All v1 requirements mapped to phases.
EOF
)"
```
</step>

<step name="done">
```
Roadmap created:

- Roadmap: .planning/ROADMAP.md
- State: .planning/STATE.md
- [N] phases defined

---

## ▶ Next Up

**Phase 1: [Name]** — [Goal from ROADMAP.md]

`/ms:plan-phase 1`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:discuss-phase 1` — gather context first
- `/ms:research-phase 1` — investigate unknowns

---
```
</step>

<step name="update_last_command">
Update `.planning/STATE.md` Last Command field:
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:create-roadmap | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line
</step>

</process>

<success_criteria>
- [ ] PROJECT.md validated
- [ ] REQUIREMENTS.md validated
- [ ] ms-roadmapper spawned with context
- [ ] All v1 requirements mapped to phases (no orphans)
- [ ] Success criteria derived for each phase (2-5 observable behaviors)
- [ ] Roadmap presented to user for approval
- [ ] User feedback incorporated (if any)
- [ ] ROADMAP.md, STATE.md committed after approval
- [ ] REQUIREMENTS.md traceability section updated
</success_criteria>
