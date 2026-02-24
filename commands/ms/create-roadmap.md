---
name: ms:create-roadmap
description: Define requirements and create roadmap with phases
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
  - Glob
  - Task
---

<objective>
Define project requirements and create roadmap with phase breakdown.

Run after `/ms:new-milestone` or `/ms:new-project` + optional `/ms:research-project`.
</objective>

<execution_context>
@~/.claude/mindsystem/templates/state.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/MILESTONE-CONTEXT.md (if exists)
@.planning/research/FEATURES.md (if exists)
@.planning/research/SUMMARY.md (if exists)
</context>

<process>

<step name="validate">
```bash
# Verify project exists
[ -f .planning/PROJECT.md ] || { echo "ERROR: No PROJECT.md found. Run /ms:new-project first."; exit 1; }

# Detect available context
[ -f .planning/MILESTONE-CONTEXT.md ] && echo "HAS_MILESTONE_CONTEXT" || echo "NO_MILESTONE_CONTEXT"
[ -d .planning/research ] && echo "HAS_RESEARCH" || echo "NO_RESEARCH"
[ -f .planning/REQUIREMENTS.md ] && echo "REQUIREMENTS_EXISTS" || echo "NO_REQUIREMENTS"
[ -f .planning/ROADMAP.md ] && echo "ROADMAP_EXISTS" || echo "NO_ROADMAP"
```
</step>

<step name="check_existing">
Check if requirements or roadmap already exist:

**If REQUIREMENTS_EXISTS or ROADMAP_EXISTS:**
Use AskUserQuestion:
- header: "Files exist"
- question: "Existing planning files found. What would you like to do?"
- options:
  - "View existing" — Show current files
  - "Replace" — Define requirements and create roadmap fresh (will overwrite)
  - "Cancel" — Keep existing files

If "View existing": Read and display existing files, then exit
If "Cancel": Exit
If "Replace": Continue
</step>

<step name="gather_context">
**Thin path — only when no MILESTONE-CONTEXT.md and no research exist.**

**If MILESTONE-CONTEXT.md exists:** Skip (context ready for agent).

**If no MILESTONE-CONTEXT.md but HAS_RESEARCH:** Skip (research provides feature context).

**If neither exists (first milestone, no research):**

Lightweight questioning in main context to gather enough feature context for the agent:

1. Read PROJECT.md for core value and stated requirements/constraints
2. Ask inline: "What are the main things users need to do in v1?"
3. For each capability mentioned, probe for specifics with AskUserQuestion
4. Ask about scope boundaries: "Anything you explicitly want to exclude?"
5. Ask about priorities: "What's most important to get right first?"

Capture responses as gathered context to pass to the agent.

Use AskUserQuestion before spawning:
- header: "Ready?"
- question: "Ready to generate requirements and roadmap from this context?"
- options:
  - "Generate" — Spawn agent with gathered context
  - "Add more" — I want to share more details
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

**Milestone context:**
{If MILESTONE-CONTEXT.md exists: @.planning/MILESTONE-CONTEXT.md}
{If no MILESTONE-CONTEXT.md: gathered context from questioning step}

**Starting phase number:** $START_PHASE

**Research (if exists):**
@.planning/research/FEATURES.md
@.planning/research/SUMMARY.md

**Config:**
@.planning/config.json

</planning_context>

<instructions>
1. Derive REQUIREMENTS.md from milestone context (apply requirements_derivation process)
2. Derive phases from those requirements (don't impose structure)
3. **Start phase numbering at $START_PHASE** (not 1, unless this is the first milestone)
4. Map every v1 requirement to exactly one phase
5. Derive 2-5 success criteria per phase (observable user behaviors)
6. Validate 100% coverage
7. Write files immediately (REQUIREMENTS.md, ROADMAP.md, STATE.md)
8. Return ROADMAP CREATED with combined requirements + roadmap summary

Write files first, then return. This ensures artifacts persist even if context is lost.
</instructions>
""",
  description="Derive requirements and create roadmap"
)
```
</step>

<step name="handle_return">
**If `## ROADMAP BLOCKED`:**
- Present blocker information
- Work with user to resolve
- Re-spawn when resolved

**If `## ROADMAP CREATED`:**

Read the created REQUIREMENTS.md and ROADMAP.md and present both inline:

```
---

## Requirements & Roadmap

### v1 Requirements

**{X} requirements** across {N} categories

{For each category:}
**{Category}**
- [ ] **{REQ-ID}**: {description}
- [ ] **{REQ-ID}**: {description}

{If v2 requirements exist:}
**v2 (deferred):** {count} requirements
**Out of scope:** {count} exclusions

---

### Roadmap

**{M} phases** | All v1 requirements covered ✓

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

[... continue for all phases ...]

---
```
</step>

<step name="approval_gate">
**CRITICAL: Ask for approval before committing:**

Use AskUserQuestion:
- header: "Roadmap"
- question: "Do these requirements and roadmap work for you?"
- options:
  - "Approve" — Commit and continue
  - "Adjust requirements" — Change what's in/out of scope
  - "Adjust phases" — Change phase structure
  - "Review full files" — Show raw REQUIREMENTS.md and ROADMAP.md

**If "Approve":** Continue to commit step.

**If "Adjust requirements":**
- Get user's adjustment notes (ask inline what they want to change)
- Re-spawn roadmapper with revision context:
  ```
  Task(
    subagent_type="ms-roadmapper",
    prompt="""
<revision>
User feedback on requirements:
[user's notes]

Current REQUIREMENTS.md: @.planning/REQUIREMENTS.md
Current ROADMAP.md: @.planning/ROADMAP.md

Update requirements based on feedback, then re-derive phases if needed.
Edit files in place.
Return ROADMAP REVISED with changes made.
</revision>
""",
    description="Revise requirements and roadmap"
  )
  ```
- Present revised output
- Loop until user approves

**If "Adjust phases":**
- Get user's adjustment notes (ask inline what they want to change)
- Re-spawn roadmapper with revision context:
  ```
  Task(
    subagent_type="ms-roadmapper",
    prompt="""
<revision>
User feedback on roadmap phases:
[user's notes]

Current REQUIREMENTS.md: @.planning/REQUIREMENTS.md
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

**If "Review full files":** Display raw REQUIREMENTS.md and ROADMAP.md, then re-ask approval.
</step>

<step name="commit">
After user approval:

```bash
git add .planning/REQUIREMENTS.md .planning/ROADMAP.md .planning/STATE.md
git commit -m "$(cat <<'EOF'
docs: define requirements and create roadmap

[X] v1 requirements across [N] categories.
[M] phases mapped to requirements.

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
Requirements and roadmap created:

- Requirements: .planning/REQUIREMENTS.md
- Roadmap: .planning/ROADMAP.md
- State: .planning/STATE.md
- [X] v1 requirements, [M] phases defined

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
```bash
ms-tools set-last-command "ms:create-roadmap"
```
</step>

</process>

<success_criteria>
- [ ] All v1 requirements mapped to phases (no orphans)
- [ ] Success criteria derived for each phase (2-5 observable behaviors)
- [ ] User feedback incorporated (if any)
- [ ] Requirements and roadmap presented to user for approval
- [ ] ms-roadmapper spawned with full planning context
- [ ] REQUIREMENTS.md created with REQ-IDs and scope classification
- [ ] REQUIREMENTS.md, ROADMAP.md, STATE.md committed after approval
</success_criteria>
