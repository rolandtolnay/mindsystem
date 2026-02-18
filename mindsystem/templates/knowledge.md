# Knowledge Template

Template for `.planning/knowledge/{subsystem}.md` — per-subsystem knowledge files that persist across phases and milestones.

**Purpose:** Curated reference per domain area. Bridges phase-scoped execution artifacts to topic-scoped knowledge. Each file contains decisions, architecture, design, pitfalls, and key files for one subsystem.

**Created by:** `ms-consolidator` agent during `execute-phase`

**Referenced by:** All pre-planning phases (discuss-phase, design-phase, research-phase, plan-phase)

---

<template>

```markdown
# {subsystem}

> {One-line summary of what this subsystem does and the current approach.}

## Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| {choice in 5-10 words} | {reason in 5-10 words} | {vX.Y phase N} |

## Architecture

- {Structural pattern or flow description}
- {How components connect and interact}

## Design

- {Visual/UX spec, interaction pattern, or design token}
- {Component state, layout choice, or color value}

## Pitfalls

- **{Brief title}**: {What to watch out for and why}
- **{Brief title}**: {Operational pattern or known trap}

## Key Files

- `{path/to/file}` — {What it does}
- `{path/to/file}` — {What it does}
```

</template>

<guidelines>

## Section Purposes

| Section | Captures | Source Artifacts |
|---------|----------|-----------------|
| **Decisions** | Choices with rationale (the "because" part) | CONTEXT.md locked decisions, RESEARCH.md recommendations, PLAN.md approach rationale, SUMMARY.md key-decisions |
| **Architecture** | How the subsystem works, structural patterns | RESEARCH.md architecture patterns, PLAN.md implementation details, SUMMARY.md accomplishments |
| **Design** | Visual/UX specs, interaction patterns, design tokens | DESIGN.md wireframe layouts, states tables, behavior notes, design tokens |
| **Pitfalls** | What to watch out for, operational patterns | RESEARCH.md common pitfalls, SUMMARY.md issues/deviations, debug resolutions, adhoc learnings |
| **Key Files** | Important file paths for this subsystem | SUMMARY.md key-files, PLAN.md file targets |

## Format Rules

- **Omit empty sections.** A subsystem with no design work has no Design section.
- **No frontmatter.** Filename is the address (`knowledge/auth.md` = auth subsystem). The one-line summary under the heading provides orientation.
- **Decisions table is concise.** 5-10 words per cell. Extract the "because" — not a description of what was done.
- **Architecture and Design use prose bullets.** Describe how things work, not tables.
- **Pitfalls use bold titles** for scannability.
- **Key Files is a flat list.** No nesting, no grouping.
- **Rewrite semantics, not append.** Each consolidation produces the current state. Superseded decisions get updated. Outdated patterns get removed. The file is always current.

## Cross-Reference Pattern

When a subsystem's knowledge references another subsystem, add a parenthetical cross-reference:

```markdown
- JWT tokens validated by API middleware on all protected routes (see api subsystem)
```

The cross-reference is navigational, not essential. Each file is self-contained for its consumer.

## Good vs Bad Entries

**Good decision entries:**
- `jose over jsonwebtoken | Better TypeScript support, actively maintained | v1.0 phase 2`
- `httpOnly cookies over localStorage | XSS prevention | v1.0 phase 2`

**Bad decision entries:**
- `Use React | — | 1` (no rationale)
- `Implemented authentication | Users can log in | 2` (not a decision, just work done)

**Good pitfall entries:**
- **bcrypt cost factor**: Use 12, not 10. Cost factor 10 is brute-forceable on modern GPUs
- **JWT payload size**: Keep under 4KB — cookie size limits vary by browser

**Bad pitfall entries:**
- Fixed a bug in auth (description, not a reusable pattern)
- Missing import in login.ts (trivial, not worth persisting)

</guidelines>
