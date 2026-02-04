---
name: update-docs
description: Update README, help command, and ms-meta skill after implementing Mindsystem changes
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
---

<objective>
Update Mindsystem documentation to reflect recently implemented changes.

After implementing a significant change to Mindsystem (new command, workflow modification, new agent, etc.), this command ensures all user-facing documentation stays in sync:
- README.md — Public-facing overview and command table
- commands/ms/help.md — Detailed command reference
- .claude/skills/ms-meta/SKILL.md — Claude's internal knowledge about Mindsystem
</objective>

<context>
**Identify what changed:**
Review recent work in the conversation or examine git status:

```bash
git diff --name-only HEAD~5
git log --oneline -5
```

**Load current documentation:**
@README.md
@commands/ms/help.md
@.claude/skills/ms-meta/SKILL.md
</context>

<process>
1. **Understand the change** — Identify what was added/modified:
   - New command? New agent? Modified workflow?
   - What behavior changed?
   - What does the user need to know?

2. **Update README.md** — Public-facing, concise:
   - **Command table** (line ~333): One-line description, keep it brief
   - **Playbooks section**: Only if the change affects common workflows
   - **Style**: Marketing-friendly, focus on user value
   - **DON'T**: Add implementation details or exhaustive options

3. **Update commands/ms/help.md** — Detailed reference:
   - **Command section**: Full description with options and flags
   - **Usage examples**: Show common invocations
   - **Workflow sections**: Update if command fits into existing workflows
   - **Style**: Technical, complete, include all options
   - **DON'T**: Duplicate playbook-style content from README

4. **Update .claude/skills/ms-meta/SKILL.md** — Claude's knowledge:
   - **`<core_workflow>`**: Update if command sequence changed
   - **`<agents_index>`**: Add new agents or update spawn sources
   - **`<workflows_index>`**: Add new workflows
   - **`<fork_features>`**: Add significant new capabilities
   - **Style**: Concise, structured for Claude consumption
   - **DON'T**: Add verbose explanations (Claude reads the actual files)

5. **Verify consistency** — Check that all three files tell the same story:
   - Command names match exactly
   - Descriptions are compatible (brief in README, detailed in help)
   - No contradictions between files
</process>

<update_guidelines>

## README.md Best Practices

**Command table format:**
```markdown
| `/ms:command-name [args]` | Brief description (what it does for the user) |
```

**Keep descriptions:**
- User-focused (what they get, not how it works)
- Under 70 characters
- Action-oriented verbs ("Create", "Verify", "Update")

**Avoid:**
- Implementation details
- Listing all options/flags
- Technical jargon

## commands/ms/help.md Best Practices

**Command entry format:**
```markdown
**`/ms:command-name [args]`**
Description of what it does.

- Use when: specific situation or trigger
- Behavior detail 1
- Behavior detail 2
- Options: describe flags and variations

Usage: `/ms:command-name arg`
Usage: `/ms:command-name` (auto-detect mode)
Result: What gets created/modified
```

**Include:**
- All command options and flags
- Multiple usage examples
- What files get created/modified
- When to use vs. alternatives

## .claude/skills/ms-meta/SKILL.md Best Practices

**Keep sections updated:**
- `<core_workflow>`: Numbered command sequence with notes
- `<agents_index>`: Table with Agent | Purpose | Spawned by
- `<workflows_index>`: Table with Workflow | Purpose

**Style:**
- Terse, structured for quick reference
- Tables preferred over prose
- Include "spawned by" relationships for agents

</update_guidelines>

<verification>
After updating, verify:

1. **README command table** — New/changed command has correct one-liner
2. **help.md command section** — Command fully documented with usage examples
3. **ms-meta SKILL.md** — Relevant sections updated (workflow, agents, features)
4. **No contradictions** — All three files describe the same behavior
5. **No duplications** — Each file serves its purpose (overview vs. reference vs. knowledge)
</verification>

<success_criteria>
- README.md command table updated with brief, user-focused description
- commands/ms/help.md has complete command documentation with usage examples
- .claude/skills/ms-meta/SKILL.md has updated workflow/agents/features sections
- All three files are consistent with each other
- Changes are minimal and targeted (don't rewrite unrelated content)
</success_criteria>
