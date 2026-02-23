# Roadmap Template

Template for `.planning/ROADMAP.md`.

## Initial Roadmap (v1.0 Greenfield)

```markdown
# Roadmap: [Project Name]

## Overview

[One paragraph describing the journey from start to finish]

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
**Plans**: [Number of plans, e.g., "3 plans" or "TBD"]

Plans:
- [ ] 01-01: [Brief description of first plan]
- [ ] 01-02: [Brief description of second plan]
- [ ] 01-03: [Brief description of third plan]

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
**Plans**: [Number of plans]

Plans:
- [ ] 02-01: [Brief description]
- [ ] 02-02: [Brief description]

### Phase 2.1: Critical Fix (INSERTED)
**Goal**: [Urgent work inserted between phases]
**Depends on**: Phase 2
**Success Criteria** (what must be TRUE):
  1. [What the fix achieves]
**Plans**: 1 plan

Plans:
- [ ] 02.1-01: [Description]

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
**Plans**: [Number of plans]

Plans:
- [ ] 03-01: [Brief description]
- [ ] 03-02: [Brief description]

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
**Plans**: [Number of plans]

Plans:
- [ ] 04-01: [Brief description]

## Progress

**Execution Order:**
Phases execute in numeric order: 2 → 2.1 → 2.2 → 3 → 3.1 → 4

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. [Name] | 0/3 | Not started | - |
| 2. [Name] | 0/2 | Not started | - |
| 3. [Name] | 0/2 | Not started | - |
| 4. [Name] | 0/1 | Not started | - |
```

<guidelines>
**Initial planning (v1.0):**
- Phase count derived from actual work (not a target number)
- Each phase delivers something coherent
- Phases can have 1+ plans (split by orchestrator judgment — multiple subsystems, context budget, vertical slices)
- Plans use naming: {phase}-{plan}-PLAN.md (e.g., 01-02-PLAN.md)
- No time estimates (this isn't enterprise PM)
- Progress table updated by execute workflow
- Plan count can be "TBD" initially, refined during planning

**Success criteria:**
- 2-5 observable behaviors per phase (from user's perspective)
- Cross-checked against requirements during roadmap creation
- Flow downstream to `## Must-Haves` in plan-phase
- Verified by verify-phase after execution
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
