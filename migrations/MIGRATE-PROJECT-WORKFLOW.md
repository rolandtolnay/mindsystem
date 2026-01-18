# Migration Guide: Project Workflow Improvements from v1.6.x

This guide migrates workflow improvements from v1.6.x to your v1.5.17 fork while **preserving your separate commands** (the unified flow is NOT migrated).

**What you get:**
1. **Roadmap Approval Gate** — User reviews roadmap before commit
2. **gsd-roadmapper Agent** — Offloads heavy lifting (coverage validation, goal-backward)
3. **Atomic Commits** — Crash recovery for each workflow stage
4. **new-milestone Context Presentation** — Shows "what shipped" before asking "what's next"

**What you keep:**
- Separate `/gsd:research-project`, `/gsd:define-requirements`, `/gsd:create-roadmap` commands
- Modular workflow (can run steps independently)

---

## Prerequisites

- v1.5.17 fork installed
- These commands exist:
  - `~/.claude/commands/gsd/new-project.md`
  - `~/.claude/commands/gsd/new-milestone.md`
  - `~/.claude/commands/gsd/define-requirements.md`
  - `~/.claude/commands/gsd/create-roadmap.md`
  - `~/.claude/commands/gsd/research-project.md`

---

## Part 1: Fetch gsd-roadmapper Agent

The roadmapper agent handles the heavy lifting of roadmap creation:
- Derives phases from requirements (not arbitrary structure)
- Validates 100% requirement coverage
- Applies goal-backward thinking for success criteria
- Writes files immediately (crash recovery)

### Step 1.1: Fetch the Agent

```bash
curl -sL https://raw.githubusercontent.com/glittercowboy/get-shit-done/main/agents/gsd-roadmapper.md \
  -o ~/.claude/agents/gsd-roadmapper.md
```

### Step 1.2: Verify Installation

```bash
head -15 ~/.claude/agents/gsd-roadmapper.md
```

You should see:
```
---
name: gsd-roadmapper
description: Creates project roadmaps with phase breakdown, requirement mapping, success criteria derivation, and coverage validation...
tools: Read, Write, Bash, Glob, Grep
---
```

### Step 1.3: Update Agent Description (Optional)

The agent says "Spawned by /gsd:new-project orchestrator" but in your fork it will be spawned by `/gsd:create-roadmap`. You can update this if you want clarity:

Open `~/.claude/agents/gsd-roadmapper.md` and find the `<role>` section. Change:

```markdown
You are spawned by:

- `/gsd:new-project` orchestrator (unified project initialization)
```

To:

```markdown
You are spawned by:

- `/gsd:create-roadmap` command
- `/gsd:new-milestone` command (for subsequent milestones)
```

---

## Part 2: Update create-roadmap.md

Replace the in-context roadmap creation with agent-based creation plus approval gate.

### Step 2.1: Locate Your Command

```bash
cat ~/.claude/commands/gsd/create-roadmap.md | head -30
```

You should see the v1.5.17 version that delegates to `workflows/create-roadmap.md`.

### Step 2.2: Replace create-roadmap.md

Replace the entire file with this updated version:

```bash
cat > ~/.claude/commands/gsd/create-roadmap.md << 'CMDEOF'
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
CMDEOF
```

### Step 2.3: Verify

```bash
grep -A 5 "spawn_roadmapper" ~/.claude/commands/gsd/create-roadmap.md
grep "approval_gate" ~/.claude/commands/gsd/create-roadmap.md
```

You should see the new step names.

---

## Part 3: Add Atomic Commits to define-requirements.md

v1.5.17's `define-requirements.md` commits at the end. Add commit immediately after REQUIREMENTS.md is created.

### Step 3.1: Locate the Commit Section

```bash
grep -n "commit" ~/.claude/commands/gsd/define-requirements.md
```

### Step 3.2: Add Explicit Commit Step

Open `~/.claude/commands/gsd/define-requirements.md` and find the `<step name="execute">` section. After requirements are generated, add an explicit commit:

Find where it says something like "Generate REQUIREMENTS.md" or the end of the execute step, and add:

```markdown
**Commit immediately after writing:**

```bash
git add .planning/REQUIREMENTS.md
git commit -m "$(cat <<'EOF'
docs: define v1 requirements

[X] requirements across [N] categories
[Y] requirements deferred to v2
EOF
)"
```

This ensures requirements persist even if context is lost before roadmap creation.
```

**Note:** If your v1.5.17 already has a commit at the end, you can leave it as-is. The key is ensuring the commit happens right after REQUIREMENTS.md is written, not bundled with other operations.

---

## Part 4: Add Atomic Commits to research-project.md

### Step 4.1: Check Current Behavior

```bash
grep -n "commit" ~/.claude/commands/gsd/research-project.md
```

### Step 4.2: Add Commit Behavior

If using the research synthesizer from MIGRATE-RESEARCH-FEATURES.md, the synthesizer handles commits. If not using synthesizer, ensure each research agent or the orchestrator commits after all research files are written:

Open `~/.claude/commands/gsd/research-project.md` and add after all 4 agents complete:

```markdown
**Commit research files:**

```bash
git add .planning/research/
git commit -m "$(cat <<'EOF'
docs: complete project research

Files:
- STACK.md
- FEATURES.md
- ARCHITECTURE.md
- PITFALLS.md

Key findings:
- Stack: [one-liner from agent results]
- Domain: [one-liner]
EOF
)"
```
```

---

## Part 5: Update new-milestone.md Context Presentation

Add the "what shipped" presentation before asking "what's next".

### Step 5.1: Locate the Context Loading Section

```bash
grep -n "Load context" ~/.claude/commands/gsd/new-milestone.md
```

### Step 5.2: Add Context Presentation

Open `~/.claude/commands/gsd/new-milestone.md` and find step 1 or 2 (after loading context, before questioning). Add this presentation section:

```markdown
<step name="present_context">
**Present what shipped (if MILESTONES.md exists):**

```bash
cat .planning/MILESTONES.md 2>/dev/null
```

Format the presentation:

```
---

## Previous Milestone

**Last milestone:** v[X.Y] [Name] (shipped [DATE])

**Key accomplishments:**
- [From MILESTONES.md accomplishments]
- [From MILESTONES.md accomplishments]
- [From MILESTONES.md accomplishments]

**Validated requirements:**
- [From PROJECT.md Validated section]

**Pending todos (if any):**
- [From STATE.md accumulated context]

---
```

This gives users context before asking what they want to build next.
</step>
```

### Step 5.3: Add Atomic Commit After PROJECT.md Update

Find where PROJECT.md is updated with new milestone goals and ensure there's a commit immediately after:

```markdown
**Commit milestone start immediately:**

```bash
git add .planning/PROJECT.md .planning/STATE.md
git commit -m "$(cat <<'EOF'
docs: start milestone v[X.Y] [Name]

[One-liner describing milestone focus]
EOF
)"
```

This ensures milestone start is recorded even if context is lost before requirements.
```

---

## Part 6: Update new-project.md Atomic Commits (Optional)

Your v1.5.17 new-project.md already commits PROJECT.md and config.json at the end. For crash recovery, you can split this into two commits:

### Step 6.1: Commit PROJECT.md Immediately

After PROJECT.md is written (before workflow preferences):

```markdown
**Commit PROJECT.md immediately:**

```bash
mkdir -p .planning
git add .planning/PROJECT.md
git commit -m "$(cat <<'EOF'
docs: initialize project

[One-liner from PROJECT.md What This Is section]
EOF
)"
```
```

### Step 6.2: Commit config.json Separately

After config.json is created:

```markdown
**Commit config.json:**

```bash
git add .planning/config.json
git commit -m "$(cat <<'EOF'
chore: add project config

Mode: [chosen mode]
Depth: [chosen depth]
Parallelization: [enabled/disabled]
EOF
)"
```
```

This creates two commits instead of one, but provides crash recovery between steps.

---

## Verification Checklist

After migration, verify:

- [ ] `gsd-roadmapper.md` exists in `~/.claude/agents/`
- [ ] `create-roadmap.md` spawns gsd-roadmapper agent
- [ ] `create-roadmap.md` has approval gate before commit
- [ ] `define-requirements.md` commits immediately after REQUIREMENTS.md
- [ ] `research-project.md` commits research files (or synthesizer handles this)
- [ ] `new-milestone.md` presents "what shipped" before questioning
- [ ] `new-milestone.md` commits after PROJECT.md update
- [ ] (Optional) `new-project.md` has atomic commits per stage

---

## Testing

### Test Roadmap Approval Gate

1. Run `/gsd:define-requirements` to create requirements
2. Run `/gsd:create-roadmap`
3. Verify you see the roadmap summary
4. Verify you're asked "Does this roadmap structure work for you?"
5. Test "Adjust phases" — should allow iteration
6. Test "Approve" — should commit

### Test Atomic Commits

1. Run `/gsd:new-project`
2. After PROJECT.md is created but before config.json, check `git log`
3. You should see the PROJECT.md commit already exists

### Test new-milestone Presentation

1. Have a completed milestone (or create MILESTONES.md manually)
2. Run `/gsd:new-milestone`
3. Verify you see "Previous Milestone" with accomplishments before being asked "What do you want to build next?"

---

## Rollback

To remove these improvements:

### Remove gsd-roadmapper agent:
```bash
rm ~/.claude/agents/gsd-roadmapper.md
```

### Restore original create-roadmap.md:
```bash
npx get-shit-done-cc@1.5.17
# Choose to reinstall commands when prompted
```

Or manually restore from your fork's git history.

---

## Summary

| Feature | What Changed | Benefit |
|---------|--------------|---------|
| gsd-roadmapper agent | New agent handles heavy lifting | Offloads complexity, better coverage validation |
| Roadmap approval gate | User sees roadmap before commit | Prevents accidental commits, enables iteration |
| Atomic commits | Commit after each stage | Crash recovery, artifacts persist |
| new-milestone presentation | Shows "what shipped" first | Better context for "what's next" decisions |

These are surgical improvements that enhance your workflow without consolidating your separate commands.
