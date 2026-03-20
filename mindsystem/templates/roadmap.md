# Roadmap Template

Template for `.planning/ROADMAP.md`.

## Initial Roadmap (Greenfield)

```markdown
# Roadmap: [Project Name]

## Overview

[One paragraph describing the journey from start to finish]

## Research Conclusions
[Present only when /ms:research-milestone informed the roadmap]

### Technology Stack
- [Technology]: [purpose] — [rationale]

### Key Constraints
- [Constraint and impact]

### Architecture Decisions
- [Decision and rationale]

### Risk Mitigations
- Phase [N]: [pitfall] — [prevention]

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: [Name]** - [One-line description]
- [ ] **Phase 2: [Name]** - [One-line description]
- [ ] **Phase 3: [Name]** - [One-line description]
- [ ] **Phase 4: [Name]** - [One-line description]

## Phase Details

### Phase 1: [Name]
**Goal**: [What this phase delivers]
**Depends on**: Nothing (first phase)
**Requirements**: [REQ-01, REQ-02, REQ-03]
**Success Criteria** (what must be TRUE):
  1. [Observable behavior from user perspective]
  2. [Observable behavior from user perspective]
  3. [Observable behavior from user perspective]
**Discuss**: Unlikely (mechanical setup, zero design decisions)
**Design**: Unlikely (backend only)
**Research**: Unlikely (established patterns)

### Phase 2: [Name]
**Goal**: [What this phase delivers]
**Depends on**: Phase 1
**Requirements**: [REQ-04, REQ-05]
**Success Criteria** (what must be TRUE):
  1. [Observable behavior from user perspective]
  2. [Observable behavior from user perspective]
**Discuss**: Likely (assumes email/password only, unclear if social login needed, session duration unspecified)
**Discuss topics**: [What to clarify]
**Design**: Likely (significant new UI)
**Design focus**: [What to design]
**Research**: Likely (new integration)
**Research topics**: [What needs investigating]

### Phase 2.1: Critical Fix (INSERTED)
**Goal**: [Outcome-focused goal derived during insertion]
**Depends on**: Phase 2
**Requirements**: [REQ-05, REQ-06]
**Success Criteria** (what must be TRUE):
  1. [Observable behavior from user perspective]
  2. [Observable behavior from user perspective]
**Discuss**: Likely (assumes X, unclear if Y)
**Discuss topics**: [What to clarify]
**Design**: Unlikely (backend fix)
**Research**: Unlikely (known patterns)

### Phase 3: [Name]
**Goal**: [What this phase delivers]
**Depends on**: Phase 2
**Requirements**: [REQ-06, REQ-07, REQ-08]
**Success Criteria** (what must be TRUE):
  1. [Observable behavior from user perspective]
  2. [Observable behavior from user perspective]
  3. [Observable behavior from user perspective]
**Discuss**: Likely (assumes standard REST patterns, error handling strategy unspecified, rate limiting approach unclear)
**Discuss topics**: [Integration scope, error UX, retry behavior]
**Design**: Unlikely (API only)
**Research**: Likely (external API)
**Research topics**: [What needs investigating]

### Phase 4: [Name]
**Goal**: [What this phase delivers]
**Depends on**: Phase 3
**Requirements**: [REQ-09, REQ-10]
**Success Criteria** (what must be TRUE):
  1. [Observable behavior from user perspective]
  2. [Observable behavior from user perspective]
**Discuss**: Likely (assumes priority ordering of requirements, unclear if batch processing needed, edge case handling unspecified)
**Discuss topics**: [Priority rules, batch vs individual, error recovery]
**Design**: Unlikely (backend only)
**Research**: Unlikely (internal patterns)

## Progress

**Execution Order:**
Phases execute in numeric order: 2 → 2.1 → 2.2 → 3 → 3.1 → 4

| Phase | Status | Completed |
|-------|--------|-----------|
| 1. [Name] | Not started | - |
| 2. [Name] | Not started | - |
| 3. [Name] | Not started | - |
| 4. [Name] | Not started | - |
```

<guidelines>
**Research Conclusions section:**
- Populated by roadmapper when MILESTONE-RESEARCH.md exists
- Downstream commands (plan-phase, discuss-phase, research-phase) consume this implicitly by reading ROADMAP.md
- Omitted entirely when no milestone research was performed

**Initial planning:**
- Phase count derived from actual work (not a target number)
- Each phase delivers something coherent
- Plans use naming: {phase}-{plan}-PLAN.md (e.g., 01-02-PLAN.md)
- No time estimates (this isn't enterprise PM)
- Progress table updated by execute workflow

**Success criteria:**
- 2-5 observable behaviors per phase (from user's perspective)
- Cross-checked against requirements during roadmap creation
- Flow downstream to `## Must-Haves` in plan-phase
- Verified by ms-verifier agent after execution
- Format: "User can [action]" or "[Thing] works/exists"

**Pre-work indicators** (all use Likely/Unlikely with parenthetical reason):
- `Discuss` - Default Likely. Surfaces Claude's assumptions before planning. Unlikely only for fully mechanical zero-decision work (version bump, rename-only refactor, config-only change, pure deletion/cleanup). When Likely, rationale enumerates 2-4 phase-specific assumptions or open questions.
- `Design` - Visual unknowns: significant new UI, novel interactions, multi-screen flows
- `Research` - Technical unknowns: external APIs, new libraries, architectural decisions
- Include topic/focus fields only when Likely
- Indicators are hints, not mandates - validate at planning time
- UI-facing phases often need both Discuss and Design (this is intentional)

**After milestones ship:**
- Collapse completed milestones in `<details>` tags
- Add new milestone sections for upcoming work
- Keep continuous phase numbering (never restart at 01)
</guidelines>

<status_values>
- `Not started` - Haven't begun
- `In progress` - Currently working
- `Complete` - Done (add completion date)
- `Deferred` - Pushed to later (with reason)
</status_values>

## Milestone-Grouped Roadmap

After first milestone ships, reorganize with milestone groupings. Read `templates/roadmap-milestone.md` for the milestone-grouped format.
