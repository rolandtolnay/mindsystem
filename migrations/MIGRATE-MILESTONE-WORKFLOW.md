# Migration Guide: Milestone Workflow Improvements from v1.6.x

This guide migrates milestone-specific improvements from v1.6.x to your v1.5.17 fork while **preserving your separate commands**.

**What you get:**
1. **Phase Number Continuation** — New milestones continue phase numbering (phase 6, not phase 1)
2. **Stronger Milestone Research Prompts** — Explicit "don't re-research existing system" context
3. **discuss-milestone Improvements** — Better context presentation and questioning

**What you keep:**
- Separate `/gsd:discuss-milestone`, `/gsd:new-milestone`, `/gsd:research-project`, `/gsd:define-requirements`, `/gsd:create-roadmap` commands
- Modular workflow (can run steps independently)

---

## Prerequisites

- v1.5.17 fork installed
- MIGRATE-PROJECT-WORKFLOW.md applied (gsd-roadmapper agent installed)
- These commands exist:
  - `~/.claude/commands/gsd/new-milestone.md`
  - `~/.claude/commands/gsd/discuss-milestone.md`
  - `~/.claude/commands/gsd/create-roadmap.md`
  - `~/.claude/commands/gsd/research-project.md`

---

## Part 1: Phase Number Continuation

**Problem:** In v1.5.17, when you start milestone v1.1 after completing v1.0 (phases 1-5), the new roadmap starts at Phase 1 again. This creates conflicts with existing phase directories.

**Solution:** Calculate the highest existing phase number and pass it to gsd-roadmapper.

### Step 1.1: Update create-roadmap.md

Open `~/.claude/commands/gsd/create-roadmap.md` and find the `<step name="spawn_roadmapper">` section.

**Before the Task() call, add phase number calculation:**

Find this section (after applying MIGRATE-PROJECT-WORKFLOW.md):

```markdown
<step name="spawn_roadmapper">
Spawn gsd-roadmapper agent with full context:
```

Replace with:

```markdown
<step name="spawn_roadmapper">
**Calculate starting phase number:**

```bash
# Find highest existing phase number
LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '^[0-9]+' | head -1)

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

Spawn gsd-roadmapper agent with full context:
```

### Step 1.2: Update the Task() Prompt

In the same file, find the Task() prompt and add the starting phase number to the planning context.

Find:
```markdown
Task(
  subagent_type="gsd-roadmapper",
  prompt="""
<planning_context>

**Project:**
@.planning/PROJECT.md

**Requirements:**
@.planning/REQUIREMENTS.md
```

Replace with:
```markdown
Task(
  subagent_type="gsd-roadmapper",
  prompt="""
<planning_context>

**Project:**
@.planning/PROJECT.md

**Requirements:**
@.planning/REQUIREMENTS.md

**Starting phase number:** $START_PHASE
```

Also update the instructions section to mention it:

Find:
```markdown
<instructions>
Create roadmap:
1. Derive phases from requirements (don't impose structure)
```

Replace with:
```markdown
<instructions>
Create roadmap:
1. Derive phases from requirements (don't impose structure)
2. **Start phase numbering at $START_PHASE** (not 1, unless this is the first milestone)
```

### Step 1.3: Verify

```bash
grep -A 5 "Calculate starting phase number" ~/.claude/commands/gsd/create-roadmap.md
grep "Starting phase number" ~/.claude/commands/gsd/create-roadmap.md
```

You should see both the calculation logic and the context passing.

---

## Part 2: Stronger Milestone Research Prompts

v1.5.17's `research-project.md` already has milestone context awareness (greenfield vs subsequent), but the prompts can be strengthened with more explicit guidance.

### Step 2.1: Update Stack Research Prompt

Open `~/.claude/commands/gsd/research-project.md` and find the Stack research Task().

Find the `<milestone_context>` section:
```markdown
<milestone_context>
{greenfield OR subsequent}

Greenfield: Research the standard stack for building [domain] from scratch.
Subsequent: Research what's needed to add [target features] to an existing [domain] app. Don't re-research the existing system.
</milestone_context>
```

Replace with:
```markdown
<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
Research the standard stack for building [domain] from scratch. Full ecosystem investigation.

**Subsequent (v1.1+):**
Research what's needed to add [target features] to an existing [domain] app.

IMPORTANT for subsequent milestones:
- DON'T re-research the existing system (validated requirements already work)
- DON'T question established stack choices (they're proven)
- DO research new libraries/patterns needed for [target features] specifically
- DO investigate how [target features] integrate with the existing architecture
- DO surface any compatibility concerns with current stack
</milestone_context>
```

### Step 2.2: Update Features Research Prompt

Find the Features research Task() and update its `<milestone_context>`:

```markdown
<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
What features do [domain] products have? What's table stakes vs differentiating?

**Subsequent (v1.1+):**
How do [target features] typically work? What's expected behavior?

IMPORTANT for subsequent milestones:
- Focus ONLY on [target features] - the new capabilities being added
- DON'T list features the system already has (see Validated requirements)
- DO research user expectations for [target features] specifically
- DO identify table stakes vs differentiators within [target features] scope
</milestone_context>
```

### Step 2.3: Update Architecture Research Prompt

Find the Architecture research Task() and update its `<milestone_context>`:

```markdown
<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
How are [domain] systems typically structured? What are major components?

**Subsequent (v1.1+):**
How do [target features] integrate with existing [domain] architecture?

IMPORTANT for subsequent milestones:
- The existing architecture is KNOWN (from previous milestones)
- Research how [target features] should connect to existing components
- Identify which existing components need modification vs new components needed
- Surface any architectural concerns (scaling, coupling, migration)
</milestone_context>
```

### Step 2.4: Update Pitfalls Research Prompt

Find the Pitfalls research Task() and update its `<milestone_context>`:

```markdown
<milestone_context>
{greenfield OR subsequent}

**Greenfield (v1.0):**
What do [domain] projects commonly get wrong? Critical mistakes?

**Subsequent (v1.1+):**
What are common mistakes when adding [target features] to [domain]?

IMPORTANT for subsequent milestones:
- Focus on integration pitfalls, not greenfield mistakes
- Research upgrade/migration pitfalls (existing users, data migration)
- Identify feature interaction bugs (new features breaking existing ones)
- Surface performance concerns when [target features] are added to existing load
</milestone_context>
```

### Step 2.5: Verify

```bash
grep -A 10 "IMPORTANT for subsequent" ~/.claude/commands/gsd/research-project.md | head -20
```

You should see the strengthened subsequent milestone guidance.

---

## Part 3: discuss-milestone Improvements

Improve the context presentation and questioning flow in discuss-milestone.

### Step 3.1: Add "What Shipped" Presentation

Open `~/.claude/commands/gsd/discuss-milestone.md` and find the `<step name="milestone_context">` section.

Replace it with:
```markdown
<step name="milestone_context">
**Present what shipped (rich context for "what's next" decisions):**

```bash
# Load milestone history
cat .planning/MILESTONES.md 2>/dev/null

# Load validated requirements
grep -A 50 "## Validated" .planning/PROJECT.md 2>/dev/null

# Load pending todos
grep -A 20 "## Accumulated Context" .planning/STATE.md 2>/dev/null
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

**What's now validated:**
- [From PROJECT.md Validated section]

**Pending ideas/todos:**
- [From STATE.md accumulated context, if any]

**Stats:** [N] phases, [M] plans, [P] tasks completed

---
```

This gives users full context before asking "What do you want to build next?"
</step>
```

### Step 3.2: Improve Questioning Flow

Find the `<step name="intake_gate">` section. Add thread-following guidance after the initial question:

```markdown
<step name="intake_gate">
**CRITICAL: ALL questions use AskUserQuestion. Never ask inline text questions.**

**1. Open with context-aware options:**

Use AskUserQuestion:
- header: "Next"
- question: "What do you want to add, improve, or fix?"
- options:
  - [Pending todos from STATE.md if any, e.g., "Add dark mode (from todos)"]
  - "New features" — Something not built yet
  - "Improvements" — Enhance existing functionality
  - "Bug fixes / Tech debt" — Fix issues
  - "Let me describe" — I have something specific in mind

**2. Follow the thread (don't switch topics):**

Based on their response, dig deeper into THAT topic before moving on:

| They said | Follow-up |
|-----------|-----------|
| Named a feature | "What should [feature] do? What's the core behavior?" |
| "New features" | "What capability is missing? What would users do with it?" |
| "Improvements" | "Which existing feature needs improvement? What's the friction?" |
| "Bug fixes" | "What's broken? How does it manifest?" |

**3. Probe for edges:**

Once you understand the feature, probe:
- "What's the simplest version of this that would be useful?"
- "What would make this feel complete vs MVP?"
- "Any constraints I should know about?"

**4. Decision gate:**

When you could write MILESTONE-CONTEXT.md, use AskUserQuestion:
- header: "Ready?"
- question: "I think I understand: [one-sentence summary]. Ready to capture this?"
- options:
  - "Capture it" — Create MILESTONE-CONTEXT.md
  - "Keep exploring" — I want to add more or clarify
  - "Start over" — I described the wrong thing
</step>
```

### Step 3.3: Add Next Phase Number to Context

Update the MILESTONE-CONTEXT.md output to include next phase number:

Find where MILESTONE-CONTEXT.md is written and add:

```markdown
**Write MILESTONE-CONTEXT.md:**

```markdown
# Milestone Context: [Name]

## Target Features
- [Feature 1]: [description]
- [Feature 2]: [description]

## Scope Decisions
- [What's in]
- [What's explicitly out]

## Constraints
- [Any constraints mentioned]

## Starting Phase
Next phase number: [N] (calculated from existing phases)

## Gathered From
- discuss-milestone session on [date]
- User: [key decisions made]
```
```

### Step 3.4: Verify

```bash
grep -A 10 "Previous Milestone" ~/.claude/commands/gsd/discuss-milestone.md
grep "Follow the thread" ~/.claude/commands/gsd/discuss-milestone.md
```

---

## Part 4: Update new-milestone.md to Use Phase Number

The `new-milestone.md` command should also be aware of phase continuation when it routes to create-roadmap.

### Step 4.1: Add Phase Context to Routing

Open `~/.claude/commands/gsd/new-milestone.md` and find step 7 (or the final routing section).

Add before routing to `/gsd:research-project` or `/gsd:define-requirements`:

```markdown
**Calculate next phase for context:**

```bash
LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '^[0-9]+' | head -1)
if [ -n "$LAST_PHASE" ]; then
  NEXT_PHASE=$((10#$LAST_PHASE + 1))
else
  NEXT_PHASE=1
fi
echo "Next milestone phases will start at: Phase $NEXT_PHASE"
```

Include this in the routing message:

```
Milestone v[X.Y] initialized.

Next steps:
1. /gsd:research-project — Research [domain] (optional)
2. /gsd:define-requirements — Scope what's in v[X.Y]
3. /gsd:create-roadmap — Create phases (starting at Phase $NEXT_PHASE)
```
```

---

## Verification Checklist

After migration, verify:

- [ ] `create-roadmap.md` calculates starting phase number
- [ ] `create-roadmap.md` passes starting phase to gsd-roadmapper
- [ ] `research-project.md` has strengthened subsequent milestone prompts
- [ ] `discuss-milestone.md` presents "what shipped" context
- [ ] `discuss-milestone.md` has improved questioning flow
- [ ] `new-milestone.md` shows next phase number in routing

---

## Testing

### Test Phase Number Continuation

1. Create a test project with phases 1-3 in `.planning/phases/`
   ```bash
   mkdir -p .planning/phases/01-test .planning/phases/02-test .planning/phases/03-test
   ```

2. Run `/gsd:create-roadmap` (or just the calculation logic)

3. Verify output shows "New phases will start at: 4"

4. Clean up:
   ```bash
   rm -rf .planning/phases/*-test
   ```

### Test Milestone Research Context

1. Have a project with Validated requirements in PROJECT.md
2. Run `/gsd:research-project`
3. Check the agent prompts include "IMPORTANT for subsequent milestones" guidance
4. Verify research focuses on new features, not re-researching existing system

### Test discuss-milestone Presentation

1. Have MILESTONES.md with a completed milestone
2. Run `/gsd:discuss-milestone`
3. Verify you see "Previous Milestone" with accomplishments and validated requirements

---

## Rollback

To remove these improvements:

### Restore original create-roadmap.md:
```bash
npx get-shit-done-cc@1.5.17
# Choose to reinstall commands when prompted
```

### Restore original research-project.md:
```bash
npx get-shit-done-cc@1.5.17
```

### Restore original discuss-milestone.md:
```bash
npx get-shit-done-cc@1.5.17
```

Or manually restore from your fork's git history.

---

## Integration with Other Migration Guides

This guide builds on:

- **MIGRATE-PROJECT-WORKFLOW.md** — Required for gsd-roadmapper agent (Part 1 depends on this)
- **MIGRATE-RESEARCH-FEATURES.md** — Optional, adds CONTEXT.md integration and research synthesizer

**Recommended migration order:**
1. MIGRATE-RESEARCH-FEATURES.md (optional)
2. MIGRATE-PROJECT-WORKFLOW.md (required)
3. MIGRATE-MILESTONE-WORKFLOW.md (this guide)

---

## Summary

| Feature | What Changed | Benefit |
|---------|--------------|---------|
| Phase number continuation | Calculates highest existing phase, starts after it | No phase conflicts between milestones |
| Milestone research prompts | Explicit "don't re-research existing" guidance | Focused research, less wasted context |
| discuss-milestone presentation | Shows "what shipped" before questioning | Better context for "what's next" decisions |
| Thread-following questions | Dig deeper before switching topics | More thorough context gathering |

These improvements optimize the milestone workflow for your use case: multiple milestones on existing projects, where each feature cycle is a new milestone.
