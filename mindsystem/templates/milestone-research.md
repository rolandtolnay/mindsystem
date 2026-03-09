# Milestone Research Template

Template for `.planning/MILESTONE-RESEARCH.md` — milestone-scoped research between `/ms:new-milestone` and `/ms:create-roadmap`.

**Purpose:** Inform the roadmapper with technology decisions, product landscape, architecture constraints, and risk assessment. Each section maps to a specific roadmapper decision.

**Created by:** `/ms:research-milestone` command

**Consumed by:** `ms-roadmapper` agent during `/ms:create-roadmap`

---

## Template

```markdown
# Milestone Research: [Name]

**Generated:** [date]
**Source:** /ms:research-milestone

## Executive Summary
[2-3 paragraphs: what type of problem, recommended approach, key risks]

## Technology Decisions
### Recommended Stack
| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| [lib] | [ver] | [what it does] | [why this choice] |

### Alternatives Rejected
| Rejected | Reason | Use Instead |
|----------|--------|-------------|
| [lib] | [why not] | [recommendation] |

## Product Landscape
### Table Stakes
- [Feature]: [why users expect this]

### Differentiators
- [Feature]: [competitive advantage]

### Anti-Features
- [Feature]: [why deliberately excluded]

## Architecture & Dependencies
### Components
- [Component]: [responsibility]

### Build Order
1. [First]: [rationale — what it unblocks]
2. [Second]: [rationale]

### Integration Points
- [Integration]: [how components connect]

## Feasibility Assessment
### Feasible: [YES/CONDITIONALLY/NO]
### Constraints
- [Constraint and impact]

### Open Questions
- [Question needing resolution before or during implementation]

## Pitfalls & Risks
| Pitfall | Severity | Prevention | Affects |
|---------|----------|------------|---------|
| [risk] | [HIGH/MEDIUM/LOW] | [how to avoid] | [which phases/components] |

## Sources
### HIGH Confidence
- [Source]: [what it verified]

### MEDIUM Confidence
- [Source]: [what it informed]

### LOW Confidence
- [Source]: [what it suggested — needs validation]
```

## Section-to-Roadmapper Mapping

| Section | Roadmapper Decision |
|---------|-------------------|
| Technology Decisions | Phase content — what tools each phase uses |
| Product Landscape | Requirements derivation — table stakes = v1 candidates |
| Architecture & Dependencies | Phase ordering — build order drives phase sequence |
| Feasibility Assessment | Phase boundaries and constraints |
| Pitfalls & Risks | Pre-work Research indicators per phase |
| Open Questions | Per-phase Research topics |
