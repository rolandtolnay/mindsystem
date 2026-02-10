# CLAUDE.md

> **Contributor guidelines.** For Mindsystem concepts, architecture, and deep knowledge, invoke `ms-meta` skill.

This document contains rules that affect every output when developing Mindsystem.

## Core Philosophy

Mindsystem is a **meta-prompting system** where every file is both implementation and specification. Files teach Claude how to build software systematically. The system optimizes for:

- **Solo developer + Claude workflow** (no enterprise patterns)
- **Context engineering** (manage Claude's context window deliberately)
- **Plans as prompts** (PLAN.md files are executable, not documents to transform)

Design principles (modularity, main context for collaboration, script+prompt hybrid, user as collaborator) govern all Mindsystem decisions. Invoke `ms-meta` skill for the full philosophy.

---

## Development Context

**All changes happen in this repository.** Never modify user-scope files (`~/.claude/`).

Mindsystem is distributed via `npx mindsystem-cc`. During development, the user runs `npx` which symlinks to this repository. Changes made here are immediately available for testing.

| Location | Purpose |
|----------|---------|
| `agents/` | Subagent definitions (copied to `~/.claude/agents/` on install) |
| `commands/ms/` | Slash commands (copied to `~/.claude/commands/ms/` on install) |
| `mindsystem/` | Workflows, templates, references (copied to `~/.claude/mindsystem/` on install) |
| `scripts/` | Shell scripts (copied to `~/.claude/mindsystem/scripts/` on install) |

**Never write to `~/.claude/` directly.** Always modify files in this repository.

**WARNING:** The `.claude/` directory in the repo root contains tracked project-specific files (settings, custom commands). Do NOT delete it when testing local installations with `npx . --local`. Use a different test directory or restore with `git restore .claude/` if accidentally deleted.

---

## File Structure Conventions

### Slash Commands (`commands/ms/*.md`)

```yaml
---
name: ms:command-name
description: One-line description
argument-hint: "<required>" or "[optional]"
allowed-tools: [Read, Write, Bash, Glob, Grep, AskUserQuestion]
---
```

**Section order:**
1. `<objective>` — What/why/when (always present)
2. `<execution_context>` — @-references to workflows, templates, references
3. `<context>` — Dynamic content: `$ARGUMENTS`, bash output, @file refs
4. `<process>` or `<step>` elements — Implementation steps
5. `<success_criteria>` — Measurable completion checklist

**Commands are thin wrappers.** Delegate detailed logic to workflows.

**Keep command and workflow in sync.** When adding/removing steps in a workflow, update the corresponding command's `<process>` section to match. The command lists steps at a high level; the workflow contains the detailed implementation. Both must reflect the same steps.

### Workflows (`mindsystem/workflows/*.md`)

No YAML frontmatter. Structure varies by workflow.

**Common tags** (not all workflows use all of these):
- `<purpose>` — What this workflow accomplishes
- `<when_to_use>` or `<trigger>` — Decision criteria
- `<required_reading>` — Prerequisite files
- `<process>` — Container for steps
- `<step>` — Individual execution step

Some workflows use domain-specific tags like `<philosophy>`, `<references>`, `<planning_principles>`, `<decimal_phase_numbering>`.

**When using `<step>` elements:**
- `name` attribute: snake_case (e.g., `name="load_project_state"`)
- `priority` attribute: Optional ("first", "second")

**Key principle:** Match the style of the specific workflow you're editing.

### Templates (`mindsystem/templates/*.md`)

Structure varies. Common patterns:
- Most start with `# [Name] Template` header
- Many include a `<template>` block with the actual template content
- Some include examples or guidelines sections

**Placeholder conventions:**
- Square brackets: `[Project Name]`, `[Description]`
- Curly braces: `{phase}-{plan}-PLAN.md`

### References (`mindsystem/references/*.md`)

Typically use outer XML containers related to filename, but structure varies.

Examples:
- `principles.md` → `<principles>...</principles>`
- `plan-format.md` → `<overview>` then `<core_principle>`

Internal organization varies — semantic sub-containers, markdown headers within XML, code examples.

---

## XML Tag Conventions

### Semantic Containers Only

XML tags serve semantic purposes. Use Markdown headers for hierarchy within.

**DO:**
```xml
<objective>
## Primary Goal
Build authentication system

## Success Criteria
- Users can log in
- Sessions persist
</objective>
```

**DON'T:**
```xml
<section name="objective">
  <subsection name="primary-goal">
    <content>Build authentication system</content>
  </subsection>
</section>
```

### Task Structure

```xml
<task type="auto">
  <name>Task N: Action-oriented name</name>
  <files>src/path/file.ts, src/other/file.ts</files>
  <action>What to do, what to avoid and WHY</action>
  <verify>Command or check to prove completion</verify>
  <done>Measurable acceptance criteria</done>
</task>
```

**Task types:**
- `type="auto"` — Claude executes autonomously (default)
- `type="tdd"` — TDD features with RED → GREEN → REFACTOR cycle

**@-references are eagerly loaded** — all content injected upfront. For lazy loading, use read instructions during execution. @-reference files that are always essential; use read instructions for conditionally needed files.

---

## Language & Tone

### Imperative Voice

**DO:** "Execute tasks", "Create file", "Read STATE.md"

**DON'T:** "Execution is performed", "The file should be created"

### No Filler

Absent: "Let me", "Just", "Simply", "Basically", "I'd be happy to"

Present: Direct instructions, technical precision

### No Sycophancy

Absent: "Great!", "Awesome!", "Excellent!", "I'd love to help"

Present: Factual statements, verification results, direct answers

### Brevity with Substance

**Good one-liner:** "JWT auth with refresh rotation using jose library"

**Bad one-liner:** "Phase complete" or "Authentication implemented"

---

## Anti-Patterns to Avoid

### Enterprise Patterns (Banned)

- Story points, sprint ceremonies, RACI matrices
- Human dev time estimates (days/weeks)
- Team coordination, knowledge transfer docs
- Change management processes

### Temporal Language (Banned in Implementation Docs)

**DON'T:** "We changed X to Y", "Previously", "No longer", "Instead of"

**DO:** Describe current state only

**Exception:** CHANGELOG.md, MIGRATION.md, git commits

### Generic XML (Banned)

**DON'T:** `<section>`, `<item>`, `<content>`

**DO:** Semantic purpose tags: `<objective>`, `<verification>`, `<action>`

### Vague Tasks (Banned)

```xml
<!-- BAD -->
<task type="auto">
  <name>Add authentication</name>
  <action>Implement auth</action>
  <verify>???</verify>
</task>

<!-- GOOD -->
<task type="auto">
  <name>Create login endpoint with JWT</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>POST endpoint accepting {email, password}. Query User by email, compare password with bcrypt. On match, create JWT with jose library, set as httpOnly cookie. Return 200. On mismatch, return 401.</action>
  <verify>curl -X POST localhost:3000/api/auth/login returns 200 with Set-Cookie header</verify>
  <done>Valid credentials → 200 + cookie. Invalid → 401.</done>
</task>
```

---

## UX Patterns

### Simple, Conversational Style

Prefer simple markdown formatting over decorative banners. Avoid:
- Box-drawing characters (`━`, `═`, `╔`, `╚`)
- ASCII art headers
- Heavy visual separators

Use instead:
- Standard markdown headers (`##`, `###`)
- Simple `---` dividers
- Plain text with clear structure

### "Next Up" Format

```markdown
---

## ▶ Next Up

**{identifier}: {name}** — {one-line description}

`{copy-paste command}`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- Alternative option
- Another option

---
```

### Decision Gates

Always use AskUserQuestion with concrete options. Never plain text prompts.

Include escape hatch: "Something else", "Let me describe"

---

## Quick Rules

1. **XML for semantic structure, Markdown for content**
2. **@-references are eagerly loaded** — use read instructions for conditional files
3. **Imperative, brief, technical** — no filler, no sycophancy
4. **Solo developer + Claude** — no enterprise patterns
5. **Temporal language banned** — current state only
6. **Atomic commits** — Git history as context source
7. **AskUserQuestion for all exploration** — always options
8. **Verify after automation** — automate first, verify after
