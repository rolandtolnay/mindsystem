---
name: ms:discuss-phase
description: Gather phase context through product-informed collaborative thinking before planning
argument-hint: "[phase]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - AskUserQuestion
  - Task
---

<objective>
Act as a collaborative product owner — loading milestone-level artifacts, surfacing assumptions, optionally researching competitors, and grounding every question in product analysis.

Purpose: Understand HOW the user imagines this phase working, informed by target audience, competitive landscape, and industry patterns. You're a thinking partner with product sense helping them crystallize their vision.

Output: {phase}-CONTEXT.md capturing the user's vision with reasoning-backed decisions
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/discuss-phase.md
</execution_context>

<context>
Phase number: $ARGUMENTS (required)

**Resolve phase:**
```bash
# ms-tools is on PATH — invoke directly, not as a script path
ms-tools find-phase "$ARGUMENTS"
```

**Load project state first:**
@.planning/STATE.md

**Load roadmap:**
@.planning/ROADMAP.md

**Load project context:**
@.planning/PROJECT.md
</context>

<process>
1. Validate phase number argument (error if missing or invalid)
2. Check if phase exists in roadmap
3. **Load milestone artifacts** — extract Who It's For, Core Value, How It's Different from PROJECT.md. Parse requirements mapped to this phase from REQUIREMENTS.md. Graceful if any artifact missing.
4. **Load prior knowledge** — determine relevant subsystem(s) by matching ROADMAP.md phase description against subsystem names in config.json. Load matching `.planning/knowledge/{subsystem}.md` files. If knowledge exists, present brief "What we know so far" summary.
5. Check if CONTEXT.md already exists (offer to update if yes)
6. **Assess and research** — evaluate if phase involves user-facing product decisions. If yes, offer product research via AskUserQuestion → spawn ms-product-researcher if accepted. Skip silently for backend/infra phases.
7. **Present briefing** — weave together: requirements for this phase, Claude's assumptions (approach, scope, risks with confidence levels), and research findings if available. Ask user to validate/correct assumptions.
8. **Informed discussion** — follow discuss-phase.md workflow. ALL questions use AskUserQuestion.
9. Create CONTEXT.md capturing their vision with reasoning-backed decisions
10. Present pre-work status: Read `~/.claude/mindsystem/references/prework-status.md` and show what's done vs still needed for this phase
11. **Update last command:** `ms-tools set-last-command "ms:discuss-phase $ARGUMENTS"`

**CRITICAL: ALL questions use AskUserQuestion. Never ask inline text questions.**
</process>

<success_criteria>

- Phase validated and milestone artifacts loaded (graceful if missing)
- Assumptions surfaced and validated before deep questioning
- Product research offered for user-facing phases
- Vision gathered through product-informed collaborative thinking (not interrogation)
- CONTEXT.md captures: how it works, what's essential, decisions with inline reasoning
- CONTEXT.md committed and STATE.md Last Command updated
- User knows next steps (research or plan the phase)
</success_criteria>
