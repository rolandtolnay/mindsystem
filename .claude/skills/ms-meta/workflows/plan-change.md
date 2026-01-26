# Workflow: Plan Mindsystem Change

<purpose>
Design a modification or extension to Mindsystem before implementing it.
</purpose>

<philosophy>
Mindsystem changes should follow the fork philosophy:

**Modularity over bundling.** Keep commands small and explicit. Don't create mega-flows. Each command should have a clear, singular purpose.

**Main context for collaboration.** Planning and discussion happen with the user. Subagents are for autonomous execution. Don't hide key decisions in subagents.

**Script + prompt hybrid.** Deterministic chores belong in scripts (`scripts/`). Language models handle judgment and reasoning.

**User as collaborator.** Trust that users can contribute. Maintain control, granularity, and transparency.
</philosophy>

<process>

## Step 1: Clarify the Change

**Ask:**
- What new capability or behavior is needed?
- Why is this needed? (user problem, missing feature, bug)
- What should happen after this change?

## Step 2: Identify Change Type

| Type | Examples | Scope |
|------|----------|-------|
| New command | `/ms:new-feature` | Command + maybe workflow |
| Modify command | Change behavior of existing | Command and/or workflow |
| New agent | New specialized executor | Agent definition |
| Modify agent | Change agent behavior | Agent definition |
| New template | New output format | Template file |
| Core workflow change | Execution, planning, etc. | Workflow + maybe agents |
| New script | Deterministic automation | `scripts/` directory |

## Step 3: Determine Context Split

**Ask:** Where should this work happen?

| If the work involves... | It belongs in... |
|------------------------|------------------|
| User collaboration, decisions, iteration | Main context (command/workflow) |
| Autonomous execution, heavy lifting | Subagent |
| Deterministic file manipulation, patching | Shell script |

**Examples:**
- Phase planning → Main context (user iterates)
- Plan execution → Subagent (fresh context, peak quality)
- Patch generation → Script (deterministic)

## Step 4: Map Affected Files

For each change type, identify all files that need modification:

**New command:**
```
commands/ms/{name}.md        # Create: command definition
mindsystem/workflows/{name}.md  # Create: if needs workflow
commands/ms/help.md          # Update: add to command list
```

**Modify existing behavior:**
```
# Read first to understand current:
commands/ms/{name}.md
mindsystem/workflows/{name}.md
agents/ms-{related}.md

# Determine what needs to change
```

**New agent:**
```
agents/ms-{name}.md          # Create: agent definition
# Update any workflows that should spawn it
```

**New script:**
```
scripts/{name}.sh            # Create: shell script
# Update workflows that should call it
```

**Template change:**
```
mindsystem/templates/{name}.md  # Modify or create
# Update workflows that use this template
```

## Step 5: Check Consistency Requirements

Mindsystem has consistency rules that must be maintained:

**Command ↔ Workflow sync:**
- Command's `<process>` steps must match workflow steps
- If workflow changes, update command summary

**Agent ↔ Workflow sync:**
- Workflow spawns agent with specific expectations
- Agent must produce what workflow expects

**Template ↔ Consumer sync:**
- Templates define structure
- All consumers (agents, workflows) must follow structure

**Config ↔ Workflow sync:**
- If adding config options, ensure workflows read them
- Document new options in SKILL.md or help

## Step 6: Consider Side Effects

**Will this change affect:**
- [ ] Other commands that use same workflow?
- [ ] Agents that depend on this output?
- [ ] Templates that need updates?
- [ ] STATE.md structure?
- [ ] SUMMARY.md frontmatter?
- [ ] Wave execution logic?
- [ ] Checkpoint handling?
- [ ] config.json options?
- [ ] The context split (main vs subagent)?

## Step 7: Design the Implementation

For each file:

**If creating new:**
- Follow existing patterns in that directory
- Use same XML structure as similar files
- Include all required sections

**If modifying:**
- Identify exact sections to change
- Preserve existing patterns
- Update related documentation

## Step 8: Summarize the Change

Before implementing, ensure you can articulate:
- What changes and why
- Which files to create/modify
- Implementation order (dependencies first)
- Whether it affects the context split

</process>

<patterns>
## Common Extension Patterns

### Adding a New Command

1. **Create command file:**
```yaml
---
name: ms:new-command
description: One-line description
argument-hint: "[optional]"
allowed-tools: [Read, Write, Bash, Glob, Grep, AskUserQuestion]
---

<objective>
What this command does and when to use it.
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/new-workflow.md (if needed)
</execution_context>

<process>
High-level steps (delegates to workflow)
</process>

<success_criteria>
How to know it worked
</success_criteria>
```

2. **Create workflow if needed**
3. **Add to help.md**

### Adding a New Agent

1. **Create agent file:**
```yaml
---
name: ms-new-agent
description: What it does, when spawned
tools: Read, Write, Edit, Bash, Grep, Glob
color: yellow
---

<role>
Who you are, what your job is
</role>

<execution_flow>
Step-by-step process
</execution_flow>

<success_criteria>
What defines completion
</success_criteria>
```

2. **Update workflow that spawns it**

### Adding a Script

1. **Create script file:**
```bash
#!/bin/bash
# scripts/new-script.sh
# Purpose: What this script does

set -euo pipefail

# Script logic here
```

2. **Update workflow that calls it**
3. **Make executable:** `chmod +x scripts/new-script.sh`

### Modifying Execution Flow

1. Read current workflow thoroughly
2. Identify exact step to modify
3. Make minimal change
4. Verify all references still work
5. Test full flow
</patterns>

<anti_patterns>
## What NOT to Do

- **Don't add enterprise patterns** (sprints, story points)
- **Don't add human time estimates** (hours, days)
- **Don't use generic XML tags** (`<section>`, `<item>`)
- **Don't break existing commands** without updating all consumers
- **Don't add checkpoints for automatable work**
- **Don't skip consistency updates** (help.md, related files)
- **Don't create mega-flows** that bundle unrelated commands
- **Don't hide key decisions in subagents** — keep collaboration in main context
- **Don't put judgment logic in scripts** — scripts are for deterministic operations
</anti_patterns>

<success_criteria>
Change plan complete when:
- All affected files identified
- Implementation order defined
- Consistency requirements checked
- Context split (main vs subagent) determined
- No enterprise patterns or mega-flows introduced
</success_criteria>
