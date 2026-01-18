---
name: gsd:create-roadmap
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

Run after `/gsd:define-requirements`.

**Improvement:** Spawns gsd-roadmapper agent for heavy lifting, presents roadmap for approval before committing.
</objective>

<execution_context>
@~/.claude/get-shit-done/references/principles.md
@~/.claude/get-shit-done/templates/roadmap.md
@~/.claude/get-shit-done/templates/state.md
@~/.claude/get-shit-done/references/goal-backward.md
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
[ -f .planning/PROJECT.md ] || { echo "ERROR: No PROJECT.md found. Run /gsd:new-project first."; exit 1; }

# Verify requirements exist
[ -f .planning/REQUIREMENTS.md ] || { echo "ERROR: No REQUIREMENTS.md found. Run /gsd:define-requirements first."; exit 1; }
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
Spawn gsd-roadmapper agent with full context:

```
Task(
  subagent_type="gsd-roadmapper",
  prompt="""
<planning_context>

**Project:**
@.planning/PROJECT.md

**Requirements:**
@.planning/REQUIREMENTS.md

**Research (if exists):**
@.planning/research/SUMMARY.md

**Config:**
@.planning/config.json

</planning_context>

<instructions>
Create roadmap:
1. Derive phases from requirements (don't impose structure)
2. Map every v1 requirement to exactly one phase
3. Derive 2-5 success criteria per phase (observable user behaviors)
4. Validate 100% coverage
5. Write files immediately (ROADMAP.md, STATE.md, update REQUIREMENTS.md traceability)
6. Return ROADMAP CREATED with summary

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

**Phase 2: [Name]**
Goal: [goal]
Requirements: [REQ-IDs]
Success criteria:
1. [criterion]
2. [criterion]

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
    subagent_type="gsd-roadmapper",
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

`/gsd:plan-phase 1`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/gsd:discuss-phase 1` — gather context first
- `/gsd:research-phase 1` — investigate unknowns

---
```
</step>

</process>

<success_criteria>
- [ ] PROJECT.md validated
- [ ] REQUIREMENTS.md validated
- [ ] gsd-roadmapper spawned with context
- [ ] All v1 requirements mapped to phases (no orphans)
- [ ] Success criteria derived for each phase (2-5 observable behaviors)
- [ ] Roadmap presented to user for approval
- [ ] User feedback incorporated (if any)
- [ ] ROADMAP.md, STATE.md committed after approval
- [ ] REQUIREMENTS.md traceability section updated
</success_criteria>
