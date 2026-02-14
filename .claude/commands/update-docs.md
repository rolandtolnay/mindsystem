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
1. **Classify the change** — Determines which sections to update:
   - **New command** → add entries in all three files
   - **Modified workflow** → update existing entries in all three files
   - **New agent** → update ms-meta `<agents_index>`, help.md if user-facing

2. **Update README.md** — Command table entry and playbooks section per guidelines below

3. **Update commands/ms/help.md** — Full command documentation with usage examples per guidelines below

4. **Update .claude/skills/ms-meta/SKILL.md** — Relevant sections per guidelines below

5. **Verify consistency** — Check that all three files tell the same story:
   - Command names match exactly
   - Descriptions are compatible (brief in README, detailed in help)
   - No contradictions between files
</process>

<update_guidelines>

## README.md Best Practices

- User-focused descriptions, under 70 characters
- Action-oriented verbs ("Create", "Verify", "Update")
- No implementation details, no exhaustive options, no technical jargon
- Playbooks section: only if the change affects common workflows

## commands/ms/help.md Best Practices

- All command options, flags, and variations
- Multiple usage examples with `Usage:` and `Result:` lines
- What files get created/modified
- When to use vs. alternatives
- No playbook-style content duplicated from README

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

<success_criteria>
- Changes are minimal and targeted (don't rewrite unrelated content)
- Each file serves its purpose (overview vs. reference vs. knowledge) — no cross-duplication
- All three files are consistent with each other
- README.md command table updated with brief, user-focused description
- commands/ms/help.md has complete command documentation with usage examples
- .claude/skills/ms-meta/SKILL.md has updated workflow/agents/features sections
</success_criteria>
