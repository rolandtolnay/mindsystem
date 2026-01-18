# Hybrid GSD Setup: v1.5.17 + On-Demand Plan Verification

This guide sets up GSD v1.5.17 (interactive planning) with the plan verification feature from v1.6.4 available on-demand.

---

## v2 Workflow Overview

### Greenfield (New Project)

```
/gsd:new-project              # Questions → PROJECT.md
    ↓
/gsd:research-project         # (Optional) Parallel agents research domain
    ↓
/gsd:define-requirements      # Scope v1/v2/out-of-scope → REQUIREMENTS.md
    ↓
/gsd:create-roadmap           # Phases mapped to requirements → ROADMAP.md + STATE.md
    ↓
/gsd:discuss-phase 1          # (Optional) Gather context before planning
    ↓
/gsd:plan-phase 1             # Interactive planning → PLAN.md files
    ↓
/gsd:check-phase 1             # (Optional) Verify plans before execution ← HYBRID ADDITION
    ↓
/gsd:execute-phase 1          # Parallel agents execute all plans
    ↓
/gsd:verify-work 1            # User acceptance testing
    ↓
... repeat for each phase ...
    ↓
/gsd:complete-milestone       # Archive, prep for next version
```

### Brownfield (Existing Codebase)

```
/gsd:map-codebase             # Analyze existing code → .planning/codebase/
    ↓
/gsd:new-project              # Questions (system knows your codebase)
    ↓
... continue as greenfield ...
```

---

## v1.5.17 Commands Reference

### Setup Commands

| Command | What it does |
|---------|--------------|
| `/gsd:new-project` | Extract your idea through questions → PROJECT.md |
| `/gsd:research-project` | Research domain ecosystem (stacks, features, pitfalls) |
| `/gsd:define-requirements` | Scope v1/v2/out-of-scope requirements |
| `/gsd:create-roadmap` | Create roadmap with phases mapped to requirements |
| `/gsd:map-codebase` | Map existing codebase for brownfield projects |

### Execution Commands

| Command | What it does |
|---------|--------------|
| `/gsd:discuss-phase [N]` | Gather context before planning (5 adaptive questions) |
| `/gsd:plan-phase [N]` | Generate task plans for phase (interactive, main context) |
| `/gsd:execute-phase <N>` | Execute all plans in phase with parallel agents |
| `/gsd:execute-plan` | Run single plan via subagent (interactive checkpoints) |
| `/gsd:progress` | Where am I? What's next? |

### Verification Commands

| Command | What it does |
|---------|--------------|
| `/gsd:verify-work [N]` | User acceptance test of phase or plan |
| `/gsd:check-phase [N]` | **HYBRID ADDITION** — On-demand plan verification |

### Phase Management

| Command | What it does |
|---------|--------------|
| `/gsd:add-phase` | Append phase to roadmap |
| `/gsd:insert-phase [N]` | Insert urgent work between phases |
| `/gsd:remove-phase [N]` | Remove future phase, renumber subsequent |
| `/gsd:research-phase [N]` | Deep research for unfamiliar domains (standalone) |
| `/gsd:list-phase-assumptions [N]` | See what Claude assumes before correcting |

### Milestone Commands

| Command | What it does |
|---------|--------------|
| `/gsd:complete-milestone` | Ship it, prep next version |
| `/gsd:discuss-milestone` | Gather context for next milestone |
| `/gsd:new-milestone [name]` | Create new milestone with phases |

### Session Commands

| Command | What it does |
|---------|--------------|
| `/gsd:pause-work` | Create handoff file when stopping mid-phase |
| `/gsd:resume-work` | Restore from last session |

### Utility Commands

| Command | What it does |
|---------|--------------|
| `/gsd:add-todo [desc]` | Capture idea or task for later |
| `/gsd:check-todos [area]` | List pending todos, select one to work on |
| `/gsd:debug [desc]` | Systematic debugging with persistent state |
| `/gsd:help` | Show all commands and usage guide |
| `/gsd:whats-new` | See what changed since your version |
| `/gsd:update` | Update to latest version |

---

## Why v1.5.17

| Feature | How it works in v1.5.17 |
|---------|-------------------------|
| **Planning** | Happens in your main context — you can chat, question, iterate |
| **Discuss-phase** | 5 adaptive questions that follow your energy, not rigid categories |
| **Research** | Fully standalone — research phase 5 while executing phase 3 |
| **Output** | Clean markdown, no heavy box-drawing or branded banners |

---

## Why This Setup

| Feature | v1.5.17 | v1.6.4 | This Hybrid |
|---------|---------|--------|-------------|
| Interactive planning (main context) | ✓ | ✗ | ✓ |
| Simple discuss-phase (5 questions) | ✓ | ✗ | ✓ |
| Clean output (no heavy formatting) | ✓ | ✗ | ✓ |
| Standalone research-phase | ✓ | ✗ | ✓ |
| On-demand plan verification | ✗ | ✓ | ✓ |

---

## Step 1: Install v1.5.17

```bash
npx get-shit-done-cc@1.5.17
```

Choose global or local install when prompted.

---

## Step 2: Add the Plan Checker Agent

Copy the plan-checker agent from the latest version:

```bash
curl -sL https://raw.githubusercontent.com/glittercowboy/get-shit-done/main/agents/gsd-plan-checker.md \
  -o ~/.claude/agents/gsd-plan-checker.md
```

Verify it was created:

```bash
head -10 ~/.claude/agents/gsd-plan-checker.md
```

You should see:
```
---
name: gsd-plan-checker
description: Verifies plans will achieve phase goal before execution...
```

---

## Step 3: Create the Check-Plan Command

Create the command file:

```bash
cat > ~/.claude/commands/gsd/check-phase.md << 'CMDEOF'
---
name: check-phase
description: Verify phase plans before execution (optional quality gate)
arguments: phase
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Task
---

<purpose>
On-demand plan verification. Use when a plan seems large or complex and you want a structured review before executing.

This spawns gsd-plan-checker to analyze your PLAN.md files against the phase goal.
</purpose>

<what_it_checks>
1. **Requirement Coverage** — Does every phase requirement have tasks addressing it?
2. **Task Completeness** — Does every task have files, action, verify, done?
3. **Dependency Correctness** — Are plan dependencies valid and acyclic?
4. **Key Links Planned** — Are artifacts wired together, not just created in isolation?
5. **Scope Sanity** — Will plans complete within context budget (2-3 tasks per plan)?
6. **Verification Derivation** — Are must_haves user-observable, not implementation-focused?
</what_it_checks>

<process>

<step name="validate_phase">
Phase number from $ARGUMENTS (required).

```bash
PHASE=$ARGUMENTS
PADDED=$(printf "%02d" $PHASE 2>/dev/null || echo "$PHASE")
PHASE_DIR=$(ls -d .planning/phases/${PADDED}-* .planning/phases/${PHASE}-* 2>/dev/null | head -1)

if [ -z "$PHASE_DIR" ]; then
  echo "Error: Phase $PHASE not found in .planning/phases/"
  exit 1
fi

echo "Phase directory: $PHASE_DIR"
ls "$PHASE_DIR"/*-PLAN.md 2>/dev/null
```

If no PLAN.md files found, remind user to run `/gsd:plan-phase` first.
</step>

<step name="load_context">
Read the phase goal from ROADMAP.md:

```bash
grep -A 15 "Phase ${PHASE}:" .planning/ROADMAP.md | head -20
```

Count plans and tasks:

```bash
for plan in "$PHASE_DIR"/*-PLAN.md; do
  echo "=== $(basename $plan) ==="
  grep -c "<task" "$plan" 2>/dev/null || echo "0 tasks"
done
```
</step>

<step name="spawn_checker">
Spawn the plan checker agent:

```
Task(
  subagent_type="gsd-plan-checker",
  prompt="""
Verify plans for phase $ARGUMENTS.

1. Read .planning/ROADMAP.md to get the phase goal
2. Read all *-PLAN.md files in the phase directory
3. Run all 6 verification dimensions
4. Return structured result

Phase directory: $PHASE_DIR
""",
  description="Verify phase $ARGUMENTS plans"
)
```
</step>

<step name="present_results">
Present the checker's findings clearly.

**Format for VERIFICATION PASSED:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PLAN VERIFICATION: PASSED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase: [name]
Plans: [count]
Tasks: [total count]

All checks passed:
✓ Requirement coverage complete
✓ All tasks have required fields
✓ Dependency graph valid
✓ Key links planned
✓ Scope within budget
✓ Verification criteria derived

Ready to execute: /gsd:execute-phase $ARGUMENTS
```

**Format for ISSUES FOUND:**

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 PLAN VERIFICATION: ISSUES FOUND
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase: [name]
Plans: [count]
Issues: [X blockers, Y warnings]

BLOCKERS (must fix):

1. [dimension] [description]
   Plan: [which plan]
   Fix: [specific fix hint]

2. [dimension] [description]
   Plan: [which plan]
   Fix: [specific fix hint]

WARNINGS (should fix):

1. [dimension] [description]
   Fix: [hint]

---

Options:
- Fix the issues and run /gsd:check-phase $ARGUMENTS again
- Proceed anyway: /gsd:execute-phase $ARGUMENTS (not recommended if blockers exist)
```
</step>

</process>

<examples>
**Check before executing a complex phase:**
```
/gsd:check-phase 5
```

**Typical workflow:**
```
/gsd:plan-phase 5      # Interactive planning in main context
# ... review and iterate ...
/gsd:check-phase 5      # Optional verification for complex plans
/gsd:execute-phase 5   # Execute
```
</examples>
CMDEOF
```

Verify it was created:

```bash
head -20 ~/.claude/commands/gsd/check-phase.md
```

---

## Step 4: Verify Installation

```bash
# Check agent exists
ls -la ~/.claude/agents/gsd-plan-checker.md

# Check command exists
ls -la ~/.claude/commands/gsd/check-phase.md

# Check v1.5.17 is installed
cat ~/.claude/get-shit-done/VERSION 2>/dev/null || echo "VERSION file not found"
```

---

## Usage

### Normal Workflow (Interactive Planning)

```
/gsd:plan-phase 5
```

Planning happens in your main context. You can:
- Chat and ask questions during planning
- Review tasks as they're created
- Iterate before committing

### When to Use Plan Verification

Use `/gsd:check-phase` when:
- Plan has 4+ tasks (scope concern)
- Phase is complex (auth, payments, data modeling)
- You want a structured second opinion
- Multiple plans with dependencies

```
/gsd:check-phase 5
```

The checker will analyze:
1. Does every requirement have covering tasks?
2. Are all task fields complete (files, action, verify, done)?
3. Are dependencies valid (no cycles, no missing refs)?
4. Are artifacts wired together (not just created)?
5. Is scope reasonable (2-3 tasks per plan)?
6. Are success criteria user-observable?

### Proceed or Fix

After checking:
- **PASSED** → `/gsd:execute-phase 5`
- **ISSUES** → Fix and re-check, or proceed anyway

---

## Updating the Checker

To get the latest plan-checker without upgrading GSD:

```bash
curl -sL https://raw.githubusercontent.com/glittercowboy/get-shit-done/main/agents/gsd-plan-checker.md \
  -o ~/.claude/agents/gsd-plan-checker.md
```

---

## Rollback

To remove the hybrid setup and go pure v1.5.17:

```bash
rm ~/.claude/agents/gsd-plan-checker.md
rm ~/.claude/commands/gsd/check-phase.md
```

---

## Quick Reference: Daily Workflow

### Starting a New Phase

```bash
# 1. See where you are
/gsd:progress

# 2. (Optional) Discuss if phase has UI/UX/behavior decisions
/gsd:discuss-phase 3

# 3. Plan interactively
/gsd:plan-phase 3
# ... chat, iterate, review plans as they're created ...

# 4. (Optional) Verify if plan looks complex
/gsd:check-phase 3

# 5. Execute
/gsd:execute-phase 3

# 6. Test
/gsd:verify-work 3
```

### Mid-Session Commands

```bash
# Capture an idea without losing focus
/gsd:add-todo "Add dark mode toggle"

# Check what's pending
/gsd:check-todos

# Stopping for the day
/gsd:pause-work

# Coming back
/gsd:resume-work
```

### When Things Go Wrong

```bash
# Systematic debugging
/gsd:debug "Login fails after form submit"

# Insert hotfix between phases
/gsd:insert-phase 3    # Creates phase 3.1
```

---

## Summary

You now have:
- **v1.5.17 core** — Interactive planning, simple discuss-phase, clean output
- **On-demand verification** — `/gsd:check-phase <phase>` when you want it

Best of both worlds.
