# CLAUDE.md

> **Contributor guidelines.** For Mindsystem concepts, architecture, and deep knowledge, invoke `ms-meta` skill.

This document contains rules that affect every output when developing Mindsystem.

## Core Philosophy

Mindsystem is a **meta-prompting system** where every file is both implementation and specification. Files teach Claude how to build software systematically. The system optimizes for:

- **Solo developer + Claude workflow** (no enterprise patterns)
- **Context engineering** (manage Claude's context window deliberately)
- **Plans as prompts** (PLAN.md files are executable, not documents to transform)

---

## Fork Philosophy

This is a customized fork of Mindsystem with specific design principles that diverge from upstream.

### Modularity Over Bundling

Keep commands separated rather than unified into mega-flows. Each command has a clear purpose. Users should know exactly which command to use in each situation without consulting documentation.

### Main Context for Collaboration

Planning and interactive work stays in the main context rather than delegating to subagents. This preserves:
- Conversational iteration during planning
- User ability to question, redirect, and contribute
- Visibility into Claude's reasoning

Reserve subagents for autonomous execution work, not collaborative thinking.

### Script + Prompt Hybrid

Combine bash scripts with prompts where deterministic logic fits better in code than natural language. Examples:
- Patch generation extracted to shell scripts
- File manipulation via dedicated tooling
- Research capabilities moving toward CLI tools

Prompts handle reasoning and decisions; scripts handle mechanical operations.

### User as Collaborator

Trust that users can contribute meaningfully. Maintain:
- **Control** — User decides when to proceed, what to skip
- **Granularity** — Separate commands for research, requirements, planning, execution
- **Transparency** — No hidden delegation or background orchestration

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

---

## @-Reference Patterns

**Static references** (always load):
```
@~/.claude/mindsystem/workflows/execute-phase.md
@.planning/PROJECT.md
```

**Conditional references** (based on existence):
```
@.planning/DISCOVERY.md (if exists)
```

**@-references are eagerly loaded.** All referenced file content is injected into context upfront when the prompt is processed. For lazy loading, instruct Claude to read a file path during execution (e.g., "Read `.planning/DESIGN.md` if it exists"). Use @-references for files that are always essential; use read instructions for files that are conditionally needed.

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

## Progressive Disclosure

Information flows through layers:

1. **Command** — High-level objective, delegates to workflow
2. **Workflow** — Detailed process, references templates/references
3. **Template** — Concrete structure with placeholders
4. **Reference** — Deep dive on specific concept

Each layer answers different questions:
- Command: "Should I use this?"
- Workflow: "What happens?"
- Template: "What does output look like?"
- Reference: "Why this design?"

---

## Summary: Core Meta-Patterns

1. **XML for semantic structure, Markdown for content**
2. **@-references are eagerly loaded** — use read instructions for conditional files
3. **Commands delegate to workflows**
4. **Progressive disclosure hierarchy**
5. **Imperative, brief, technical** — no filler, no sycophancy
6. **Solo developer + Claude** — no enterprise patterns
7. **Context size as quality constraint** — split aggressively
8. **Temporal language banned** — current state only
9. **Plans ARE prompts** — executable, not documents
10. **Atomic commits** — Git history as context source
11. **AskUserQuestion for all exploration** — always options
12. **Verify after automation** — automate first, verify after
13. **Deviation rules are automatic** — no permission for bugs/critical
14. **Depth controls compression** — derive from actual work
15. **TDD gets dedicated plans** — cycle too heavy to embed
