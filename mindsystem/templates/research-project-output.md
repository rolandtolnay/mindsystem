# Project Research Output Template

Template for `.planning/research/` files — research before creating roadmap.

**Purpose:** Document ecosystem-level findings for a whole project, informing phase structure and technology choices.

**Created by:** `ms-researcher` agent during `/ms:research-project`

---

## Output Files

### SUMMARY.md

Executive summary synthesizing all research with roadmap implications.

```markdown
# Research Summary: [Project Name]

**Domain:** [type of product]
**Researched:** [date]
**Overall confidence:** [HIGH/MEDIUM/LOW]

## Executive Summary

[3-4 paragraphs synthesizing all findings]

## Key Findings

**Stack:** [one-liner from STACK.md]
**Architecture:** [one-liner from ARCHITECTURE.md]
**Critical pitfall:** [most important from PITFALLS.md]

## Implications for Roadmap

Based on research, suggested phase structure:

1. **[Phase name]** - [rationale]
   - Addresses: [features from FEATURES.md]
   - Avoids: [pitfall from PITFALLS.md]

2. **[Phase name]** - [rationale]
   ...

**Phase ordering rationale:**
- [Why this order based on dependencies]

**Research flags for phases:**
- Phase [X]: Likely needs deeper research (reason)
- Phase [Y]: Standard patterns, unlikely to need research

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | [level] | [reason] |
| Features | [level] | [reason] |
| Architecture | [level] | [reason] |
| Pitfalls | [level] | [reason] |

## Gaps to Address

- [Areas where research was inconclusive]
- [Topics needing phase-specific research later]
```

### STACK.md

Recommended technologies with versions and rationale.

### FEATURES.md

Feature landscape - table stakes, differentiators, anti-features.

### ARCHITECTURE.md

System structure patterns with component boundaries.

### PITFALLS.md

Common mistakes with prevention strategies.
