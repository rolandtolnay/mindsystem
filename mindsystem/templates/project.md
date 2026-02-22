# PROJECT.md Template

Template for `.planning/PROJECT.md` — the living project context document.

<template>

```markdown
# [Project Name]

## What This Is
[2-3 sentences. Product identity in plain language.]

## Core Value
[Single sentence: the ONE thing that cannot fail.]

## Who It's For
[Target audience — who they are, their context, how they work today. 2-4 sentences.]

## Core Problem
[Why this exists — what pain or desire drives it. 1-2 sentences.]

## How It's Different
[What makes this not another [category]. Include competitive context if relevant.]
- [Differentiator 1]
- [Differentiator 2]
- [Differentiator 3]

## Key User Flows
[The 2-3 core interactions users perform.]
- [Flow 1]
- [Flow 2]
- [Flow 3]

## Out of Scope
- [Exclusion 1] — [why]
- [Exclusion 2] — [why]

## Constraints
- **[Type]**: [What] — [Why]
- **[Type]**: [What] — [Why]

Common types: Tech stack, Timeline, Budget, Dependencies, Compatibility, Performance, Security

## Technical Context
[Tech stack, integrations, prior work, known issues/debt.]

## Validated
(None yet — ship to validate)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| [Choice] | [Why] | — Pending |

---
*Last updated: [date] after [trigger]*
```

</template>

<guidelines>

**What This Is:**
- Current accurate description of the product
- 2-3 sentences capturing what it does and who it's for
- Use the user's words and framing
- Update when the product evolves beyond this description

**Core Value:**
- The single most important thing
- Everything else can fail; this cannot
- Drives prioritization when tradeoffs arise
- Rarely changes; if it does, it's a significant pivot

**Who It's For:**
- Specific enough to find 10 of these people
- Include their context: what they do today, what tools they use, what frustrates them
- Avoid broad categories ("developers", "small businesses") — narrow to who needs this MOST
- Update as real user data replaces assumptions

**Core Problem:**
- The pain or desire that makes this product necessary
- Should explain why existing alternatives don't suffice
- One sentence is better than two — forces precision
- If you can't articulate the problem, the product isn't ready to build

**How It's Different:**
- 2-3 concrete differentiators, not marketing language
- Include what people use today instead (even manual workarounds)
- "Nothing else does this" is almost always wrong — probe alternatives
- Competitive context folds in here — no standalone section needed

**Key User Flows:**
- The 2-3 core interactions that make the product valuable
- One line each — verb-driven ("Log workout → view history → track progress")
- Bridges abstract identity and concrete architecture
- Update as flows are validated or new ones emerge

**Out of Scope:**
- Explicit boundaries on what we're not building
- Always include reasoning (prevents re-adding later)
- Includes: considered and rejected, deferred to future, explicitly excluded

**Constraints:**
- Hard limits on implementation choices
- Tech stack, timeline, budget, compatibility, dependencies
- Include the "why" — constraints without rationale get questioned

**Technical Context:**
- Background that informs implementation decisions
- Tech stack, integrations, prior work, known issues/debt
- Update as new technical context emerges
- Purely technical — business context lives in Layer 1 sections

**Validated:**
- Requirements that shipped and proved valuable
- Format: `- ✓ [Requirement] — [version/phase]`
- These are locked — changing them requires explicit discussion

**Key Decisions:**
- Significant choices that affect future work
- Add decisions as they're made throughout the project
- Track outcome when known:
  - ✓ Good — decision proved correct
  - ⚠️ Revisit — decision may need reconsideration
  - — Pending — too early to evaluate

**Last Updated:**
- Always note when and why the document was updated
- Format: `after Phase 2` or `after v1.0 milestone`
- Triggers review of whether content is still accurate

</guidelines>

<evolution>

PROJECT.md evolves throughout the project lifecycle.

**After each phase transition:**
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. Decisions to log? → Add to Key Decisions
4. "What This Is" still accurate? → Update if drifted
5. Has understanding of audience, problem, or differentiation evolved? → Update Who It's For, Core Problem, or How It's Different
6. New key flows emerged? → Update Key User Flows

**After each milestone:**
1. Full review of all sections including business context (Who It's For, Core Problem, How It's Different)
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Technical Context with current state (users, feedback, metrics)
5. Key User Flows — validated against what users actually do?

</evolution>

<brownfield>

For existing codebases:

1. **Map codebase first** via `/ms:map-codebase`

2. **Infer Validated requirements** from existing code:
   - What does the codebase actually do?
   - What patterns are established?
   - What's clearly working and relied upon?

3. **Initialize:**
   - Validated = inferred from existing code
   - Out of Scope = boundaries user specifies
   - Technical Context = populated from codebase map

</brownfield>

<state_reference>

STATE.md references PROJECT.md:

```markdown
## Project Reference

See: .planning/PROJECT.md (updated [date])

**Core value:** [One-liner from Core Value section]
**Current focus:** [Current phase name]
```

This ensures Claude reads current PROJECT.md context.

</state_reference>
