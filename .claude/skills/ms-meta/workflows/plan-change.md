# Workflow: Plan Mindsystem Change

<purpose>
Design a modification or extension to Mindsystem before implementing it.
</purpose>

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
| New reference | New deep knowledge | Reference file |
| Core workflow change | Execution, planning, etc. | Workflow + maybe agents |

## Step 3: Map Affected Files

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

**Template change:**
```
mindsystem/templates/{name}.md  # Modify or create
# Update workflows that use this template
```

## Step 4: Check Consistency Requirements

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

**Reference ↔ Implementation sync:**
- References describe how things work
- Implementation must match description

## Step 5: Consider Side Effects

**Will this change affect:**
- [ ] Other commands that use same workflow?
- [ ] Agents that depend on this output?
- [ ] Templates that need updates?
- [ ] STATE.md structure?
- [ ] SUMMARY.md frontmatter?
- [ ] Wave execution logic?
- [ ] Checkpoint handling?

## Step 6: Design the Implementation

For each file:

**If creating new:**
- Follow existing patterns in that directory
- Use same XML structure as similar files
- Include all required sections

**If modifying:**
- Identify exact sections to change
- Preserve existing patterns
- Update related documentation

## Step 7: Summarize the Change

Before implementing, ensure you can articulate:
- What changes and why
- Which files to create/modify
- Implementation order (dependencies first)

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
</anti_patterns>

<success_criteria>
Change plan complete when:
- All affected files identified
- Implementation order defined
- Consistency requirements checked
- No enterprise patterns introduced
</success_criteria>
