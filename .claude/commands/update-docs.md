---
name: update-docs
description: Update README, help command, and ms-meta skill after implementing Mindsystem changes
allowed-tools:
  - Read
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Update Mindsystem documentation to reflect recently implemented changes.

After implementing a significant change to Mindsystem (new command, workflow modification, new agent, etc.), this command ensures all user-facing documentation stays in sync:
- README.md — Public-facing overview and command table
- commands/ms/help.md — Detailed command reference
- .claude/skills/ms-meta/SKILL.md — Claude's internal knowledge about Mindsystem

Not every change touches all three files. Determine which files and sections are relevant based on the routing table below, then propose changes and confirm with the user before applying.
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
1. **Classify the change and determine scope** — Not all changes need all files updated. Use the routing table below to determine which files and sections to touch.

2. **Draft proposed changes** — For each affected file, prepare the specific edits.

3. **Present changes to user for approval** — Use AskUserQuestion to show a summary of all proposed edits across files. Include which files will be changed and what content will be added/modified in each. Do not apply any edits until the user approves.

4. **Apply approved changes** — Make the edits the user approved.

5. **Verify consistency** — Check that all updated files tell the same story:
   - Command names match exactly across files
   - Descriptions are compatible (brief in README, detailed in help)
   - No contradictions between files
</process>

<routing>

## Which files and sections to update

Use this table to determine scope. A change may match multiple rows.

| Change type | README.md | help.md | ms-meta SKILL.md |
|---|---|---|---|
| **New command** | Command reference table | Full command entry (Use when, Creates, Usage/Result) | `<deep_dive_paths>` table |
| **New command in core lifecycle** | Command reference table + End-to-end walkthrough step | Full command entry + Quick Start sequence + Common Workflows if routing changes | `<deep_dive_paths>` + `<architecture>` Core Workflow section |
| **Modified command behavior** | Command reference table (if description changed) | Update existing command entry | Only if it changes artifact flow, propagation, or routing |
| **New agent** | Skip (agents are internal) | Skip (unless user-facing) | `<deep_dive_paths>` table, `<architecture>` Context Split table if relevant |
| **New workflow** | Skip (workflows are internal) | Skip | `<deep_dive_paths>` table |
| **New artifact type** | `.planning` directory tree if significant | Files & Structure tree | `<artifact_flow>` table |
| **New feature/capability** | Features section (if user-facing and significant) | Skip (features are README-only) | Skip (unless it changes architecture) |
| **Changed config options** | Configuration section | Relevant command entry | `<architecture>` if it changes component relationships |
| **Changed deferred work routing** | Skip | Choosing the Right Command tables + Common Workflows | `<architecture>` Deferred Work Routing table |
| **Changed setup/getting-started flow** | Quick start section | Quick Start sequences | Skip |
| **Changed propagation relationships** | Skip | Skip | `<change_propagation>` table |

**Key distinctions:**
- README "End-to-end walkthrough" is a narrative guide — only update for commands that join/leave the core lifecycle flow
- README "Features" section describes capabilities, not commands — only add genuinely new capabilities
- README "Quick start" rarely changes — only if the getting-started sequence itself changes
- help.md "Common Workflows" shows composition recipes — update when routing between commands changes
- ms-meta has no agents index or workflows index — use `<deep_dive_paths>` for discoverability
</routing>

<update_guidelines>

## README.md

- **Command reference table** — Brief user-focused description, under 70 chars, action verbs.
- **End-to-end walkthrough** — Narrative style matching existing steps.
- **Features** — Capability descriptions, not command documentation.
- **Quick start** — Minimal setup sequences.
- **Configuration** — Mirror config.json schema.
- **`.planning` directory tree** — Match existing tree format.

**Style:** No implementation details, no exhaustive options, no technical jargon.

## commands/ms/help.md

- **Individual command entry** — Description, "Use when:", files created/modified, Usage/Result examples.
- **Quick Start sequences** — Ordered command lists with brief annotations.
- **Choosing the Right Command tables** — Decision tables with "What you know | Best command | Why" format.
- **Common Workflows recipes** — Copy-paste command sequences with comments.
- **Files & Structure tree** — Match existing tree format.

**Style:** Complete reference — all options, variations, and examples with `Usage:` and `Result:` lines.

## .claude/skills/ms-meta/SKILL.md

- `<architecture>` — Core Workflow: numbered command sequence. Context Split: main vs subagent table. Component Model: component type list.
- `<artifact_flow>` — "Artifact | Produced by | Consumed by" table format.
- `<change_propagation>` — "When you change... | Also update..." table format.
- `<deep_dive_paths>` — "Topic | Read" table format.
- `<where_things_belong>` — "Question | Location" table format.
- `<anti_patterns>` / `<philosophy>` — Terse principle statements.

**Style:** Terse, structured for quick reference. Tables preferred over prose.

</update_guidelines>

<success_criteria>
- User approved all changes before they were applied
- Changes are minimal and targeted (don't rewrite unrelated content)
- Each file serves its purpose (overview vs. reference vs. knowledge) — no cross-duplication
- All updated files are consistent with each other
- Only relevant sections were touched per the routing table
</success_criteria>
