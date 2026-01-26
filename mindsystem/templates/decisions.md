# Decisions Template

Template for `.planning/milestones/v{X.Y}-DECISIONS.md` — consolidated decisions from a milestone.

**Purpose:** Preserve decision rationale for future reference. When starting a new milestone, previous DECISIONS.md provides context for "why did we do it this way?"

**Created by:** `ms-consolidator` agent during `/ms:complete-milestone`

**Referenced by:** `/ms:new-milestone` during discovery mode

---

<template>

```markdown
# Milestone v{{VERSION}} Decisions

**Milestone:** {{NAME}}
**Phases:** {{PHASE_START}}-{{PHASE_END}}
**Consolidated:** {{DATE}}

---

## Technical Stack

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

## Architecture

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

## Data Model

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

## API Design

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

## UI/UX

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

## Security

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

## Performance

| Decision | Rationale | Phase |
|----------|-----------|-------|
| {{DECISION}} | {{RATIONALE}} | {{PHASE}} |

---

## Sources

Files consolidated from each phase:

| Phase | Files Found |
|-------|-------------|
| {{PHASE_NUM}} | {{FILES_LIST}} |

---

*Consolidated: {{DATE}} during v{{VERSION}} milestone completion*
```

</template>

<guidelines>

## What This File Captures

**Decisions = Choices + Rationale**

This template captures WHY decisions were made, not just WHAT was built. SUMMARY.md captures what was built. DECISIONS.md captures why it was built that way.

Decisions help future milestones by:
- Explaining why certain approaches were chosen
- Documenting rejected alternatives
- Preserving constraints that influenced choices
- Providing context for "why is it this way?" questions

## Categories Explained

| Category | Content |
|----------|---------|
| **Technical Stack** | Libraries, frameworks, versions, tools |
| **Architecture** | System structure, module boundaries, patterns |
| **Data Model** | Schema, relationships, storage approach |
| **API Design** | Endpoints, auth, errors, response format |
| **UI/UX** | Components, layouts, interactions |
| **Security** | Auth, authorization, data protection |
| **Performance** | Caching, optimization, loading patterns |

## Usage Rules

**Remove empty categories.** If no Security decisions were made, don't include the Security section.

**Keep entries concise.** Decision in 5-10 words. Rationale in 10-20 words.

**Include phase number.** Helps trace when decisions were made.

## Good vs Bad Entries

**Good decision entries:**
- "Use jose over jsonwebtoken | Better TypeScript support, actively maintained | 2"
- "Flat folder structure | Avoids premature abstraction, easier navigation | 1"
- "Server actions over API routes | Simpler data mutations for forms | 3"
- "Tailwind over styled-components | Team familiarity, smaller bundle | 1"

**Bad decision entries:**
- "Use React | — | 1" (no rationale)
- "Implemented authentication | Users can log in | 2" (not a decision, just work done)
- "Added tests | Testing is important | 3" (obvious, no real decision)

## Sources Appendix

The Sources section documents which files were consolidated from each phase:

```markdown
| Phase | Files Found |
|-------|-------------|
| 1 | PLAN.md, RESEARCH.md |
| 2 | PLAN.md, CONTEXT.md, DESIGN.md |
| 3 | PLAN.md |
| 4 | PLAN.md, RESEARCH.md, DESIGN.md |
```

This helps understand which phases had dedicated research, design, or context discussion.

</guidelines>
