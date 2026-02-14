# Smart Phase Consolidation: Subsystem Knowledge Files

> Per-subsystem knowledge files that grow across phases and milestones, replacing fragmented knowledge sources with a single curated reference per domain area.
> Generated: 2026-02-14 | Ticket: MIN-103

## Executive Summary

Replace the current milestone-level "extract decisions, delete everything" consolidation with **phase-level consolidation into per-subsystem knowledge files**. After each phase completes execution, a consolidator reads all phase artifacts and writes/updates curated knowledge files in `.planning/knowledge/`. These files become the single source of truth for cross-phase and cross-milestone knowledge compounding — consumed by discuss-phase, design-phase, research-phase, and plan-phase alike.

**Core insight:** Knowledge is generated per-phase but consumed per-topic. The consolidation step bridges this mismatch by reorganizing phase-scoped execution artifacts into topic-scoped knowledge assets.

**Key changes:**
- Consolidation moves from milestone-end to phase-end (after execute-phase, with lightweight update after verify-work)
- Per-subsystem knowledge files replace DECISIONS.md and LEARNINGS.md as the knowledge vehicle
- All pre-planning phases gain knowledge compounding (not just plan-phase)
- Milestone completion becomes lightweight cleanup instead of heavy consolidation

**Relationship to proposal 009 (Knowledge Compounding):** This proposal supersedes 009's recommendations #1 (expand plan-phase retrieval) and #4 (LEARNINGS.md cross-milestone index). The subsystem vocabulary design from 009 carries forward. The debug/adhoc frontmatter enrichment from 009 (#2, #3) is complementary and can be implemented independently.

---

## Problem

### What Happens Today

At milestone completion, `ms-consolidator` scans PLAN.md, CONTEXT.md, RESEARCH.md, DESIGN.md across all phases. It extracts **decisions with rationale** into a single `v{X.Y}-DECISIONS.md` table, then deletes the source files. SUMMARY.md, VERIFICATION.md, and UAT.md are preserved.

### What's Lost

| Artifact | What DECISIONS.md Captures | What's Discarded |
|----------|---------------------------|------------------|
| CONTEXT.md | Decisions with rationale | User vision, essential elements, deferred ideas, scope boundaries, discretionary areas |
| DESIGN.md | Layout/component decisions | Wireframes, component states, color values, spacing specs, UX flows, verification criteria |
| RESEARCH.md | Library selection decisions | Architecture patterns, don't-hand-roll solutions, common pitfalls, code examples |
| PLAN.md | Approach choices | Implementation rationale, verification strategy, must-haves reasoning |

### Why This Matters

The DECISIONS.md table format captures "what was chosen and why" but discards everything else. Product philosophy, design specifications, architectural pitfalls, and implementation patterns vanish. This forces re-clarification in future milestones and violates the principle: **each unit of engineering work should make subsequent units easier, not harder.**

### Additional Gap: Narrow Compounding

Knowledge compounding currently happens only during plan-phase via SUMMARY.md scanning. discuss-phase, design-phase, and research-phase operate largely in isolation:

| Phase | Prior Knowledge Loaded | Gap |
|-------|----------------------|-----|
| discuss-phase | ROADMAP, STATE | No prior decisions, design rationale, or research findings |
| design-phase | CONTEXT, PROJECT | No research findings, no prior design patterns, no tech constraints |
| research-phase | CONTEXT, DESIGN, STATE, REQUIREMENTS | Most knowledge-aware, but no cross-milestone retrieval |
| plan-phase | SUMMARY frontmatter + grep 5 sources | Fragmented: scans SUMMARY + DECISIONS + LEARNINGS + debug + adhoc |

---

## Design Principles

### Knowledge Has a Half-Life

Execution details (which file, which line, which commit) decay fast. Reasoning (why this pattern, what pitfall to avoid) persists. Consolidation separates durable knowledge from ephemeral execution detail.

### Signal Density Determines Compounding Effectiveness

Each token loaded into context either helps or hurts. A curated 100-line reference outperforms a raw 500-line dump. Humans stop reading long documents. Consolidation must curate, not dump.

### Knowledge Retrieval is by Topic, Not by Timeline

When planning authentication work, you need all auth knowledge — regardless of whether it came from phase 2 or phase 9. Per-subsystem organization matches how knowledge is consumed.

### Cross-Cutting Knowledge Decomposes into Subsystem Facets

There is no knowledge that is ONLY cross-cutting. "Auth affects API design" means auth knowledge says "JWT validation required on all endpoints" and api knowledge says "endpoints must validate JWT tokens." Each consumer gets the relevant facet. Duplication across subsystem files is consumer-optimized delivery, not waste.

### Consolidation Cost is Proportional to Knowledge Generated, Not Organization

A consolidator reading 5 files and writing 3 knowledge entries costs the same whether those entries go into one file or three. Per-subsystem structure adds no consolidation overhead.

---

## Solution: Phase-Level Subsystem Knowledge Files

### Overview

After each phase completes execution, a consolidator agent reads all phase artifacts and writes/updates per-subsystem knowledge files in `.planning/knowledge/`. These files are curated, human-readable, LLM-scannable, and grow richer with each phase.

### Directory Structure

```
.planning/
├── knowledge/                    # Subsystem knowledge files (persist across milestones)
│   ├── auth.md                   # Decisions, patterns, pitfalls, design, key files for auth
│   ├── api.md                    # Same structure for API subsystem
│   ├── ui.md                     # Same structure for UI subsystem
│   └── ...                       # One per active subsystem
├── phases/
│   ├── 01-foundation/
│   │   ├── 01-CONTEXT.md         # Kept until milestone-end (safety net)
│   │   ├── 01-DESIGN.md          # Kept until milestone-end (safety net)
│   │   ├── 01-RESEARCH.md        # Kept until milestone-end (safety net)
│   │   ├── 01-01-SUMMARY.md      # Kept until milestone-end (historical reference)
│   │   └── 01-01-PLAN.md         # DELETED after phase consolidation
│   └── ...
├── config.json                   # Subsystem vocabulary (existing)
├── STATE.md
├── ROADMAP.md
└── ...
```

### Knowledge File Format

Each subsystem file follows a consistent structure optimized for both human readers and LLM retrieval:

```markdown
# {subsystem}

> {One-line summary of what this subsystem does and the current approach.}

## Decisions

| Decision | Rationale | Source |
|----------|-----------|--------|
| jose over jsonwebtoken | Better TypeScript support, actively maintained | v1.0 phase 2 |
| httpOnly cookies over localStorage | XSS prevention | v1.0 phase 2 |

## Architecture

- Login flow: email + password -> bcrypt compare -> JWT with jose -> httpOnly cookie -> 200
- Refresh: queue concurrent requests during 401 interceptor, never parallel refresh calls
- Middleware validates JWT on all protected routes

## Design

- Login screen: email + password fields, "Forgot password" link, inline error messages
- Error states: invalid credentials -> inline error (no redirect), rate limited -> countdown timer
- Color tokens: primary-action (#2563EB), error-text (#DC2626)

## Pitfalls

- **bcrypt cost factor**: Use 12, not 10. Cost factor 10 is brute-forceable on modern GPUs
- **JWT payload size**: Keep under 4KB — cookie size limits vary by browser
- **Token expiry buffer**: Set refresh threshold 30s before expiry to avoid edge-case 401s

## Key Files

- `src/api/auth/login.ts` — Login endpoint
- `src/lib/crypto.ts` — Password comparison
- `src/middleware.ts` — JWT validation middleware
```

**Section purposes:**

| Section | Captures | Source Artifacts |
|---------|----------|-----------------|
| **Decisions** | Choices with rationale (the "because" part) | CONTEXT.md locked decisions, RESEARCH.md recommendations, PLAN.md approach rationale, SUMMARY.md key-decisions |
| **Architecture** | How the subsystem works, structural patterns | RESEARCH.md architecture patterns, PLAN.md implementation details, SUMMARY.md accomplishments |
| **Design** | Visual/UX specs, interaction patterns, design tokens | DESIGN.md component specs, UX flows, color/spacing values |
| **Pitfalls** | What to watch out for, operational patterns | RESEARCH.md common pitfalls, SUMMARY.md issues encountered/deviations, debug resolutions, adhoc learnings |
| **Key Files** | Important file paths for this subsystem | SUMMARY.md key-files, PLAN.md file targets |

**Format rules:**
- Sections with no content are omitted (a subsystem with no design work has no Design section)
- One-line summary under the heading provides instant orientation
- Decisions table is concise: 5-10 words per cell
- Architecture and Design use prose, not tables — they describe how things work
- Pitfalls use bold titles for scannability
- Key Files is a flat list — no nesting

### Cross-Cutting Concerns

When a phase touches multiple subsystems, the consolidator writes the relevant facet into each subsystem's knowledge file. Light cross-references provide navigation without forcing consumers to load unrelated knowledge.

Example — a phase adds JWT validation to API endpoints:

**`knowledge/auth.md` — Architecture section:**
```
- JWT tokens validated by API middleware on all protected routes (see api subsystem)
```

**`knowledge/api.md` — Architecture section:**
```
- All protected endpoints require JWT validation via auth middleware (see auth subsystem)
```

Each consumer gets the relevant perspective. The parenthetical cross-reference is navigational, not essential — the subsystem file is self-contained for its consumer.

### Rewrite Semantics (Not Append)

Knowledge files are **rewritten** each time the consolidator runs, not appended to. The consolidator reads the existing knowledge file + new phase artifacts and produces an updated version:

- Superseded decisions get updated (not duplicated)
- Outdated patterns get removed
- New knowledge gets added in the right sections
- The file is always current

This mirrors how experienced engineers update their mental model — they revise their understanding, not just stack new facts on top.

---

## Consolidation Triggers

### Primary: End of execute-phase

After all plans execute and SUMMARY.md files exist, the consolidator runs as the final step of execute-phase:

1. Reads phase artifacts: CONTEXT.md, DESIGN.md, RESEARCH.md, SUMMARY.md files
2. Reads existing knowledge files for affected subsystems
3. Produces updated knowledge files
4. Deletes PLAN.md files (zero future value — execution instructions consumed)
5. Keeps CONTEXT.md, DESIGN.md, RESEARCH.md as safety net (deleted at milestone-end)

### Secondary: End of verify-work (lightweight)

After UAT fixes are applied, a lightweight check runs:

1. Reads UAT.md for significant findings (severity=high issues that were fixed)
2. If significant patterns or pitfalls were discovered, appends them to the relevant subsystem knowledge file's Pitfalls section
3. If only minor fixes — skips (no update needed)

This is NOT a full re-consolidation. It reads only UAT.md and adds specific pitfall entries.

### Milestone Completion: Cleanup Only

Since knowledge files are already current from phase-level consolidation, milestone completion becomes lightweight:

1. Delete remaining raw artifacts: CONTEXT.md, DESIGN.md, RESEARCH.md, SUMMARY.md, UAT.md, VERIFICATION.md, EXECUTION-ORDER.md
2. Knowledge files in `.planning/knowledge/` persist (they ARE the milestone's knowledge output)
3. No ms-consolidator spawn needed — already done per-phase

---

## Raw Artifact Lifecycle

| Artifact | Created By | Deleted After | Rationale |
|----------|-----------|---------------|-----------|
| PLAN.md | plan-phase | Phase consolidation (execute-phase end) | Execution instructions — zero future value once executed |
| CONTEXT.md | discuss-phase | Milestone completion | Safety net — can verify consolidation quality |
| DESIGN.md | design-phase | Milestone completion | Safety net — specific values (colors, spacing) can be re-checked |
| RESEARCH.md | research-phase | Milestone completion | Safety net — can verify research findings were captured |
| SUMMARY.md | execute-phase | Milestone completion | Historical reference — plan-phase still scans frontmatter for within-milestone compounding |
| VERIFICATION.md | verify-work | Milestone completion | Execution record — minimal future value |
| UAT.md | verify-work | Milestone completion | Execution record — findings captured in knowledge files |
| EXECUTION-ORDER.md | plan-phase | Milestone completion | Orchestration metadata — zero post-execution value |

---

## Knowledge Compounding: All Phases

With per-subsystem knowledge files, ALL pre-planning phases gain compounding through the same mechanism: load relevant `knowledge/{subsystem}.md` file(s).

### How Each Phase Benefits

**discuss-phase** — Currently loads only ROADMAP + STATE.

With knowledge files: loads `knowledge/{subsystem}.md` for the phase's subsystem(s). Gains:
- Prior locked decisions → avoids re-discussing settled questions
- Design rationale → builds on established visual direction
- Architecture patterns → discussion is grounded in what exists
- Pitfalls → user is warned about known traps early

**design-phase** — Currently loads CONTEXT + PROJECT. No RESEARCH.md, no prior design patterns.

With knowledge files: loads `knowledge/{subsystem}.md`. Gains:
- Tech constraints from research → designs within feasibility
- Prior design patterns → maintains visual consistency
- Architecture decisions → component design aligns with system structure
- Key files → knows what exists to build upon

**research-phase** — Already the most knowledge-aware. Loads CONTEXT, DESIGN, STATE, REQUIREMENTS.

With knowledge files: loads `knowledge/{subsystem}.md`. Gains:
- Prior tech evaluations → avoids re-researching settled technology
- Known pitfalls → research focuses on unsolved problems
- Cross-milestone decisions → respects constraints from previous milestones

**plan-phase** — Currently scans N SUMMARY.md files + greps 5 sources (DECISIONS.md, LEARNINGS.md, debug docs, adhoc summaries, completed todos).

With knowledge files: loads `knowledge/{subsystem}.md` for cross-milestone context. SUMMARY.md scanning stays for within-milestone context only. Replaces fragmented grep across DECISIONS.md + LEARNINGS.md. Gains:
- Constant-cost retrieval (load 1-3 knowledge files vs scan N summaries)
- Curated cross-milestone context (decisions, patterns, pitfalls, design, architecture in one place)
- Simpler `read_project_history` step

### The Retrieval Pattern

All phases use the same retrieval:

1. Determine which subsystem(s) the phase touches (from ROADMAP.md phase description + config.json)
2. Load `knowledge/{subsystem}.md` for each relevant subsystem
3. Use the knowledge as grounding context for the phase's work

This is simpler than plan-phase's current mechanism and applies uniformly to all consumers.

### Within-Milestone vs Cross-Milestone

**Within a milestone:** Raw artifacts from earlier phases are still available. plan-phase scans SUMMARY.md frontmatter for dependency graphs, tech stack, and patterns — same as today. Knowledge files ALSO exist and contain curated context from those same phases.

**Across milestones:** Raw artifacts are cleaned up at milestone-end. Knowledge files persist. All phases load them. No gap at milestone boundaries.

The transition is seamless: phases always load knowledge files. Within-milestone phases get extra granularity from raw summaries. Cross-milestone phases get everything they need from knowledge files alone.

---

## Consolidator Agent Redesign

### Agent: ms-consolidator (rewrite)

**Current behavior:** Scans all phases at milestone-end, extracts decisions into DECISIONS.md table, deletes source files.

**New behavior:** Runs after each phase's execution. Reads phase artifacts + existing knowledge files. Produces updated per-subsystem knowledge files.

### Inputs

- Phase number and name (from execute-phase orchestrator)
- Phase artifacts: CONTEXT.md, DESIGN.md, RESEARCH.md, SUMMARY.md files
- Existing knowledge files: `.planning/knowledge/*.md` (may not exist for first phase)
- Subsystem vocabulary: `.planning/config.json`

### Process

1. **Determine affected subsystems.** Read phase SUMMARY.md frontmatter for `subsystem` field. Check if phase artifacts mention additional subsystems. Typically 1-2 subsystems per phase, occasionally 3.

2. **Read existing knowledge files** for affected subsystems (if they exist).

3. **Read phase artifacts.** For each artifact type, extract knowledge by section:
   - CONTEXT.md → locked decisions, vision elements that inform future work, deferred ideas (as scope notes)
   - DESIGN.md → component specs, design tokens, UX flows, verification criteria
   - RESEARCH.md → stack recommendations, architecture patterns, don't-hand-roll solutions, pitfalls
   - SUMMARY.md → accomplishments (architecture), key-decisions, patterns-established, issues encountered (pitfalls), key-files
   - Not all artifacts exist for every phase — handle missing files gracefully

4. **Merge into knowledge file sections.** For each affected subsystem:
   - Decisions: add new, update superseded, remove contradicted
   - Architecture: update structural description with new components/patterns
   - Design: add new specs, update changed specs
   - Pitfalls: add new, deduplicate with existing
   - Key Files: add new, remove renamed/deleted

5. **Write updated knowledge files.** One file per affected subsystem in `.planning/knowledge/`.

6. **Handle cross-cutting concerns.** If the phase touches multiple subsystems, write the relevant facet of shared decisions/patterns into each subsystem's file with light cross-references.

7. **Delete PLAN.md files.** Execution instructions consumed — zero future value.

8. **Return consolidation report** to execute-phase orchestrator.

### Output

Per-subsystem knowledge files following the format defined above, plus a consolidation report:

```markdown
## Phase Consolidation Complete

**Phase:** {number} - {name}
**Subsystems updated:** {list}

| Subsystem | Decisions | Architecture | Design | Pitfalls | Key Files |
|-----------|-----------|--------------|--------|----------|-----------|
| auth      | +2        | updated      | +3     | +1       | +2        |
| api       | +1        | updated      | —      | —        | +1        |

**Files deleted:** {list of PLAN.md files}
**Files preserved:** CONTEXT.md, DESIGN.md, RESEARCH.md, SUMMARY.md (safety net)
```

### Verify-Work Lightweight Update

After verify-work completes, a simpler process runs (not the full consolidator):

1. Read UAT.md — check for severity=high issues that were fixed
2. If significant findings exist: read relevant knowledge files, append pitfall entries
3. If no significant findings: skip

This can be inline logic in the verify-work workflow, not a separate agent spawn.

---

## Files Replaced

### DECISIONS.md — Eliminated

Decisions with rationale now live in each subsystem knowledge file's `## Decisions` section. The milestone-level cross-index is no longer needed because:
- plan-phase loads subsystem knowledge files directly (no grep needed)
- new-milestone can scan knowledge file frontmatter/headings for orientation
- The per-subsystem format is more useful than a flat cross-phase table

**Migration:** `ms-consolidator` agent rewritten. `decisions.md` template deleted. `complete-milestone` workflow updated to remove consolidation step. `new-milestone` command updated to load knowledge files instead of DECISIONS.md.

### LEARNINGS.md — Absorbed

Curated operational patterns (currently one-liner entries in LEARNINGS.md) belong in each subsystem knowledge file's `## Pitfalls` section. The consolidator captures these from:
- SUMMARY.md issues encountered and deviations
- Debug session resolutions (root_cause + resolution from frontmatter)
- Adhoc summary learnings (learnings array from frontmatter)

**Migration:** `learnings.md` template deleted. `complete-milestone` workflow's `extract_learnings` step removed. `plan-phase` workflow updated to load knowledge files instead of grepping LEARNINGS.md.

---

## Downstream Changes

### Files to Modify

| File | Change | Scope |
|------|--------|-------|
| `agents/ms-consolidator.md` | Full rewrite: phase-level consolidation into subsystem knowledge files | Major |
| `mindsystem/workflows/execute-phase.md` | Add consolidation step at end of execution | Moderate |
| `mindsystem/workflows/verify-phase.md` | Add lightweight knowledge update after UAT fixes | Small |
| `mindsystem/workflows/complete-milestone.md` | Remove consolidation step, simplify to cleanup only | Moderate |
| `commands/ms/complete-milestone.md` | Update process to reflect simplified milestone completion | Small |
| `mindsystem/workflows/discuss-phase.md` | Add knowledge file loading at start | Small |
| `commands/ms/discuss-phase.md` | Update context references | Small |
| `mindsystem/workflows/plan-phase.md` | Replace DECISIONS.md + LEARNINGS.md grep with knowledge file loading | Moderate |
| `commands/ms/design-phase.md` | Add knowledge file loading | Small |
| `commands/ms/research-phase.md` | Add knowledge file loading | Small |
| `commands/ms/new-milestone.md` | Load knowledge files instead of DECISIONS.md | Small |

### Files to Create

| File | Purpose |
|------|---------|
| `mindsystem/templates/knowledge.md` | Template for per-subsystem knowledge file format |

### Files to Delete

| File | Reason |
|------|--------|
| `mindsystem/templates/decisions.md` | Replaced by subsystem knowledge files |
| `mindsystem/templates/learnings.md` | Absorbed into subsystem knowledge files |

### Change Propagation

Per CLAUDE.md's change propagation table:
- Agent expected output changes → update `execute-phase.md` workflow (spawns consolidator)
- Template deleted (decisions.md) → update `ms-consolidator.md`, `complete-milestone.md`
- Template deleted (learnings.md) → update `complete-milestone.md`, `plan-phase.md`
- Command changes → update `help.md` if command descriptions change

---

## Scaling Characteristics

### Small Projects (1-2 milestones, 3-5 subsystems)

- 3-5 knowledge files of 20-50 lines each after first milestone
- Loading costs ~100-250 tokens — negligible
- Consolidator runs 2-6 times total (once per phase)
- No complexity overhead — system starts empty and grows naturally

### Medium Projects (3-5 milestones, 5-10 subsystems)

- 5-10 knowledge files of 50-150 lines each
- Loading costs ~500-1500 tokens for 1-3 relevant subsystems
- Knowledge files are rewritten each consolidation — stay current without pruning
- Cross-references between subsystems become more valuable

### Large Projects (5+ milestones, 10+ subsystems)

- 10+ knowledge files, some reaching 200+ lines
- Targeted loading (only relevant subsystems) keeps context cost manageable
- If needed: a dedicated knowledge retrieval subagent could scan all files and extract cross-subsystem patterns (future enhancement, not needed initially)
- Rewrite semantics prevent unbounded growth — each consolidation prunes outdated content

---

## Comparison: Before and After

### Before (Current System)

```
Phase executes → SUMMARY.md (raw)
...more phases execute → more SUMMARY.md files
Milestone completes → ms-consolidator extracts decisions → DECISIONS.md (table)
                    → extract_learnings → LEARNINGS.md (one-liners)
                    → delete CONTEXT/DESIGN/RESEARCH/PLAN

Next milestone plan-phase → scan N SUMMARY.md frontmatter
                          → grep DECISIONS.md
                          → grep LEARNINGS.md
                          → grep debug docs
                          → grep adhoc summaries
                          → grep completed todos
                          (5+ sources, growing scan cost)

discuss-phase → no prior knowledge
design-phase → no prior knowledge (except CONTEXT.md)
research-phase → CONTEXT + DESIGN + STATE (partial)
```

### After (Proposed System)

```
Phase executes → SUMMARY.md (raw)
              → consolidator reads artifacts → updates knowledge/{subsystem}.md
              → deletes PLAN.md

verify-work (optional) → lightweight pitfall update to knowledge files

Next phase (any type) → loads knowledge/{subsystem}.md (1-3 files, curated)
                      → within-milestone: also scans SUMMARY.md frontmatter

Milestone completes → cleanup: delete remaining raw artifacts
                    → knowledge files already current (no heavy consolidation)

Next milestone (any phase) → loads knowledge/{subsystem}.md (same mechanism)
```

### What Improves

| Dimension | Before | After |
|-----------|--------|-------|
| Knowledge sources | 5+ fragmented files | 1 per subsystem |
| Compounding phases | plan-phase only | All 4 pre-planning phases |
| Context cost at phase 6 | Growing (scan 15+ summaries) | Constant (load 1-3 knowledge files) |
| Milestone boundary | Heavy consolidation + knowledge loss | Lightweight cleanup, no loss |
| Human readability | DECISIONS.md table (sparse) | Subsystem files (rich, narrative) |
| Knowledge freshness | Curated at milestone-end only | Curated after every phase |

---

## Open Questions

1. **Knowledge file frontmatter.** Should subsystem knowledge files have YAML frontmatter for machine-readable metadata (subsystem name, last updated, source phases)? This would enable cheap scanning without reading full content. Trade-off: adds structural overhead to what should be a clean document.

2. **First phase of first milestone.** No knowledge files exist. All pre-planning phases gracefully handle missing `.planning/knowledge/` directory. Consolidator creates the directory on first run. No special cases needed — but worth verifying in implementation.

3. **Subsystem renaming.** If a subsystem is renamed in config.json (e.g., "auth" → "authentication"), the corresponding knowledge file needs renaming. Should the consolidator detect this, or is it a manual operation? Low frequency, manageable either way.

4. **Multiple subsystems per phase.** A phase touching 3 subsystems requires reading 3 existing knowledge files and writing 3 updated files. The consolidator must determine which knowledge belongs to which subsystem. The subsystem assignment comes from: SUMMARY.md frontmatter (primary subsystem), PLAN.md inline metadata, and consolidator judgment for cross-cutting content.
