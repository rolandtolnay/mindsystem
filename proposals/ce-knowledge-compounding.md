# CE Analysis: Knowledge Compounding

> Comparing Compound Engineering and Mindsystem approaches to making each unit of work improve future work.
> Generated: 2026-02-07 | Updated: 2026-02-07 (design decisions finalized)

## Executive Summary

Compound Engineering treats knowledge compounding as a **first-class workflow stage** — after every solved problem, a 7-step documentation pipeline captures the solution into a searchable `docs/solutions/` library with YAML frontmatter. During planning, a dedicated `learnings-researcher` agent grep-searches this library to surface relevant past solutions before new work begins.

Mindsystem already creates rich artifacts (SUMMARY.md with 14-field frontmatter, debug docs, UAT files, milestone archives) and has a sophisticated dependency graph for context assembly during planning. However, these artifacts serve **forward-looking context assembly** (what does phase N need from phase N-1?) rather than **cross-cutting knowledge retrieval** (what have we learned about this type of problem before?). The gap is not in capture — Mindsystem captures extensively — but in **retrieval and resurfacing** of past learnings when they're relevant to new work.

**Core architectural decision:** Adopt **problem-scoped retrieval without problem-scoped storage**. Keep Mindsystem's phase-scoped artifacts (SUMMARY.md, debug docs, adhoc summaries) as the source of truth, but extend frontmatter and retrieval to enable cross-cutting knowledge discovery. No separate `docs/solutions/` directory. Add a thin `LEARNINGS.md` curated index for cross-milestone persistence, distinct from PROJECT.md (decisions) and STATE.md (session restoration).

**Implementation approach:** Four high-impact changes — enrich debug doc frontmatter, add post-resolution learning capture, expand plan-phase retrieval to search all artifact types with a `<learnings>` handoff to ms-plan-writer, and create LEARNINGS.md as a curated cross-milestone index.

---

## How Compound Engineering Handles Knowledge Compounding

### Overview

CE implements a **capture → categorize → retrieve → apply** loop where solved problems become searchable institutional memory. The system has three layers: a capture workflow triggered after problem resolution, a categorized knowledge store with enum-validated metadata, and a retrieval agent that surfaces relevant learnings before new work begins.

### Key Components

| Component | Path | Role |
|-----------|------|------|
| `/workflows:compound` command | `commands/workflows/compound.md` | Orchestrates 7-step capture pipeline |
| `compound-docs` skill | `skills/compound-docs/SKILL.md` | Documentation engine with YAML validation |
| `learnings-researcher` agent | `agents/research/learnings-researcher.md` | Grep-first knowledge retrieval |
| `schema.yaml` | `skills/compound-docs/schema.yaml` | Enum definitions for categorization |
| `resolution-template.md` | `skills/compound-docs/assets/resolution-template.md` | Standard solution document format |
| `critical-pattern-template.md` | `skills/compound-docs/assets/critical-pattern-template.md` | Must-know pattern format |
| `/deepen-plan` command | `commands/deepen-plan.md` | Enriches plans with past learnings |

### Workflow

**Capture (after problem solved):**
1. Auto-trigger on phrases like "that worked", "it's fixed" — or manual `/workflows:compound`
2. 7 parallel subagents extract context, classify, and document
3. YAML frontmatter validated against enum schema (blocking gate)
4. Solution written to `docs/solutions/{category}/{symptom}-{module}-{date}.md`
5. Cross-reference check: 3+ similar → extract to `common-solutions.md`
6. Decision menu: promote to critical patterns, add to skill, or continue

**Retrieve (before new work):**
1. During `/workflows:plan`, `learnings-researcher` agent is spawned
2. Agent extracts keywords from phase goal/requirements
3. Grep-first filtering of `docs/solutions/` by frontmatter fields (tags, module, symptoms)
4. Reduces hundreds of files to 5-20 candidates before reading content
5. Returns distilled summaries with actionable insights
6. `/deepen-plan` spawns a subagent per relevant learning for deeper integration

### Distinctive Patterns

**Enum-validated categorization.** 13 problem types, 17 components, 16 root causes, 10 resolution types, 4 severity levels. Ensures consistent categorization and reliable grep-based retrieval.

**Grep-first efficiency.** The learnings-researcher never reads full documents upfront. Multiple parallel Grep calls filter by frontmatter fields, reducing the search space before any Read operations. Designed to surface learnings in <30 seconds.

**Auto-invoke triggers.** Capture happens at the moment of resolution, when context is freshest. No separate "documentation step" to forget.

**Critical pattern promotion.** User can promote solutions to `critical-patterns.md` — a required-reading file that all subagents check before code generation.

**Separate knowledge store.** `docs/solutions/` is distinct from workflow artifacts (plans, summaries). It's a permanent, growing library that survives milestone boundaries.

---

## How Mindsystem Handles Knowledge Compounding

### Overview

Mindsystem creates extensive artifacts throughout its workflow — SUMMARY.md files with 14-field frontmatter, debug session docs, UAT results, milestone archives, and a living STATE.md. These artifacts serve a **dependency graph** for context assembly: plan-phase scans SUMMARY frontmatter to determine which prior phases to load into context. Knowledge persists but is **phase-scoped** (what did phase 3 build?) rather than **problem-scoped** (how did we solve N+1 queries last time?).

### Key Components

| Component | Path | Role |
|-----------|------|------|
| SUMMARY.md template | `mindsystem/templates/summary.md` | Phase completion with 14-field frontmatter |
| STATE.md template | `mindsystem/templates/state.md` | Living project memory (<100 lines) |
| Debug session docs | `.planning/debug/{slug}.md` | Structured problem investigation |
| Todo docs | `.planning/todos/pending/*.md` | Captured ideas for later |
| Adhoc summaries | `.planning/adhoc/*.md` | Small work documentation |
| Milestone archive | `mindsystem/templates/milestone-archive.md` | Completed milestone preservation |
| Decisions template | `mindsystem/templates/decisions.md` | Consolidated milestone decisions |
| ms-consolidator agent | `agents/ms-consolidator.md` | Extracts decisions at milestone |
| plan-phase workflow | `mindsystem/workflows/plan-phase.md` | Context assembly via frontmatter graph |

### Workflow

**Capture (during work):**
1. ms-executor creates SUMMARY.md after each plan with frontmatter (subsystem, tags, requires, provides, affects, key-decisions, patterns-established)
2. ms-debugger writes `.planning/debug/{slug}.md` during debugging (symptoms, eliminated hypotheses, evidence, resolution)
3. `/ms:verify-work` creates UAT.md with test results and gaps
4. ms-verifier creates VERIFICATION.md with structured gap data
5. `/ms:complete-milestone` spawns ms-consolidator to extract decisions into `v{X.Y}-DECISIONS.md`
6. `/ms:add-todo` captures ideas in `.planning/todos/pending/`
7. `/ms:do-work` creates adhoc summaries in `.planning/adhoc/`

**Retrieve (before new work):**
1. plan-phase's `read_project_history` step scans all SUMMARY.md frontmatter (~25 lines each)
2. Builds dependency graph: `requires`/`provides`/`affects` fields
3. Selects relevant summaries by subsystem match, affects field, requires chain
4. Extracts tech stack, established patterns, key decisions from selected frontmatter
5. Reads full summaries only for selected phases
6. Checks STATE.md for accumulated decisions, pending todos, blockers
7. Loads codebase context (`.planning/codebase/*.md`) by phase keywords

### Current Limitations

**Phase-scoped, not problem-scoped.** SUMMARY.md answers "what did this phase build?" not "how did we solve this type of problem?" A performance fix in phase 2 is captured in `02-01-SUMMARY.md` with frontmatter, but finding it requires knowing it was phase 2 or matching subsystem tags.

**Debug docs are archived but not searched.** Debug sessions in `.planning/debug/` contain rich problem-solving knowledge (symptoms, failed hypotheses, root cause, resolution) but no workflow searches them before new work. They're write-once artifacts.

**No cross-milestone retrieval.** When a milestone completes, PLAN.md, CONTEXT.md, RESEARCH.md, and DESIGN.md files are deleted by ms-consolidator. SUMMARY.md files survive but the dependency graph restarts. Lessons from milestone 1 don't automatically surface during milestone 2 planning.

**No pattern extraction.** When the same type of problem is solved multiple times (e.g., N+1 queries in different phases), there's no mechanism to detect the pattern and extract a reusable solution.

**Todos lack categorization.** `.planning/todos/pending/*.md` files have minimal structure — timestamp and slug. No YAML frontmatter, no tags, no severity classification. Not searchable by domain.

---

## Side-by-Side Comparison

| Dimension | Compound Engineering | Mindsystem | Assessment |
|-----------|---------------------|------------|------------|
| **Capture trigger** | Auto-invoke on "that worked" phrases | Manual SUMMARY.md after each plan, manual `/ms:add-todo` | CE stronger — captures at moment of resolution |
| **Capture granularity** | One document per solved problem | One SUMMARY per plan (may contain multiple issues) | CE stronger — problem-scoped, not plan-scoped |
| **Categorization** | Enum-validated YAML (13 types, 17 components, 16 root causes) | SUMMARY frontmatter (subsystem, tags — free-form) | CE stronger — reliable grep-based retrieval |
| **Knowledge store** | Dedicated `docs/solutions/` directory | Scattered across SUMMARY, debug, adhoc, todos | CE stronger — single searchable location |
| **Retrieval mechanism** | Dedicated learnings-researcher agent with grep-first | plan-phase frontmatter scan (dependency graph) | **MS has better infrastructure** — just needs to search more |
| **Retrieval timing** | Before planning AND during plan deepening | Before planning only (via dependency graph) | CE stronger — two retrieval points |
| **Cross-milestone persistence** | Solutions directory survives all boundaries | SUMMARY.md survives, but PLANs/CONTEXT deleted | Comparable — both keep execution records |
| **Pattern detection** | 3+ similar → common-solutions.md extraction | None | CE stronger — active pattern recognition |
| **Critical pattern promotion** | User-driven promotion to required-reading file | None — patterns stay in individual artifacts | CE stronger — escalation path for important learnings |
| **Context assembly** | Spawn subagent per relevant learning | Frontmatter dependency graph + selective loading | **MS stronger** — machine-readable, transitive closure |
| **Efficiency at scale** | Grep-first filtering of solutions dir | Frontmatter scan (~25 lines per summary) | Comparable approaches — both avoid full reads |

---

## Design Decisions

Conclusions from analysis of both systems and discussion of tradeoffs.

### Keep Phase-Scoped Storage, Add Problem-Scoped Retrieval

CE needs a separate `docs/solutions/` directory because its workflow artifacts lack rich metadata — they're documents, not machine-readable stores. Mindsystem's SUMMARY.md frontmatter is already machine-readable with 14 fields enabling grep-based retrieval. Debug docs can gain the same frontmatter. Adhoc summaries can gain the same frontmatter.

**Decision:** Don't create a parallel problem-scoped knowledge store. Instead, make existing phase-scoped artifacts retrievable by problem characteristics (symptoms, root cause, tags, subsystem). This gives problem-scoped *retrieval* without problem-scoped *storage* — lighter, avoids fragmentation, fits the "modularity over bundling" philosophy.

The forward dependency graph (`requires`/`provides`/`affects`) remains the primary retrieval mechanism for phase-to-phase context. Keyword/tag matching against enriched frontmatter adds the cross-cutting dimension CE provides through its solutions directory.

### LEARNINGS.md: Curated Index, Not Knowledge Store

LEARNINGS.md is a **thin curated index with source references** — not a duplicate of content that lives in SUMMARY.md, debug docs, or adhoc summaries. Each entry is one line describing the pattern + a reference to the source artifact where full detail lives.

**What LEARNINGS.md is NOT:**
- Not a replacement for PROJECT.md Key Decisions (those are architectural *choices*, not problem-solving *patterns*)
- Not a replacement for STATE.md (that's session restoration, not knowledge)
- Not a replacement for v{X.Y}-DECISIONS.md (that's categorized decision rationale, not reusable learnings)

**The distinction that matters:**
- **Decision** (PROJECT.md): "Used jose over jsonwebtoken — ESM-native, Edge-compatible"
- **Learning** (LEARNINGS.md): "JWT libraries using CommonJS fail silently in Edge runtime — always verify ESM compatibility before choosing a crypto library"

Decisions constrain future work ("we chose X, so keep using X"). Learnings inform future work ("watch out for X when you're doing Y").

### Artifact Ownership (No Overlap)

| Artifact | Core Question | Type of Knowledge | Read When |
|----------|---------------|-------------------|-----------|
| **STATE.md** | "Where are we? What happened recently?" | Session restoration — position, velocity, recent activity | Every workflow start |
| **PROJECT.md** Key Decisions | "What did we choose and why?" | Architectural choices that constrain future work | Every planning session |
| **v{X.Y}-DECISIONS.md** | Same, categorized at milestone end | Archived decision rationale with phase traceability | Starting new milestone |
| **LEARNINGS.md** | "When you encounter X, here's what works" | Reusable problem-solving patterns with source refs | During `read_project_history` (keyword-matched) |
| **SUMMARY.md** frontmatter | "What did this phase build and what does it affect?" | Forward dependency metadata for context assembly | During `read_project_history` (graph-based) |

STATE.md stays under 100 lines. It does not reference LEARNINGS.md — that would waste context on learnings irrelevant to the current session. LEARNINGS.md is only consulted during planning, keyword-matched against the current phase goal.

### Intra-Milestone vs Cross-Milestone Retrieval

**Within a milestone:** The expanded `read_project_history` search handles learning retrieval directly — it searches debug docs, adhoc summaries, SUMMARY.md issues, and LEARNINGS.md (if it exists from prior milestones). Source artifacts are all still present.

**At milestone boundaries:** PLAN.md, CONTEXT.md, RESEARCH.md, DESIGN.md get deleted. SUMMARY.md survives, but the one-line curated entries in LEARNINGS.md are faster to scan and pre-filtered for actionable insights. LEARNINGS.md bridges milestones.

**Flow:**
1. **Intra-milestone**: `read_project_history` searches SUMMARY frontmatter + debug docs + adhoc summaries + LEARNINGS.md
2. **At milestone completion**: ms-consolidator extracts new learnings section, appends to LEARNINGS.md
3. **Next milestone**: LEARNINGS.md carries forward the curated cross-milestone index

### The `<learnings>` Handoff to ms-plan-writer

During `read_project_history`, after scanning all sources, emit a `<learnings>` section in the handoff payload to ms-plan-writer. This section combines:

- Keyword-matched entries from LEARNINGS.md (cross-milestone patterns)
- Relevant debug session resolutions (intra-milestone, from expanded search)
- Relevant adhoc summary learnings (intra-milestone)
- Matched `patterns-established` from SUMMARY frontmatter

This gives the planner a unified view of "here's what we've learned that's relevant to this phase" without duplicating source content. The planner can incorporate specific learnings into task actions and verification steps.

---

## Recommendations

### High Impact (Adopt)

#### 1. Expand plan-phase's `read_project_history` to search debug docs and adhoc summaries

- **Classification**: Refactor existing
- **Source**: CE's `learnings-researcher` grep-first pattern
- **Target**: `mindsystem/workflows/plan-phase.md` — `read_project_history` step
- **What changes**: After scanning SUMMARY.md frontmatter (existing behavior), also scan:
  - `.planning/debug/resolved/*.md` — Parse YAML frontmatter for symptoms, root_cause
  - `.planning/adhoc/*-SUMMARY.md` — Parse frontmatter for subsystem, tags, learnings
  - `.planning/todos/done/*.md` — Parse for patterns relevant to current phase
  - `.planning/milestones/v*-DECISIONS.md` — Grep for decisions in current domain
  - `.planning/LEARNINGS.md` — Grep for keyword-matched entries (if file exists)

  Use the same grep-first pattern: extract keywords from current phase goal, grep frontmatter of these additional sources, select relevant ones.

  **`<learnings>` handoff section:** Assemble matched learnings into a `<learnings>` section in the handoff payload for ms-plan-writer. This section combines:
  - Keyword-matched entries from LEARNINGS.md (cross-milestone patterns)
  - Relevant debug session resolutions (symptoms, root_cause, resolution from frontmatter)
  - Relevant adhoc summary learnings (learnings field from frontmatter)
  - Matched `patterns-established` from SUMMARY.md frontmatter

  The planner can incorporate specific learnings into task actions and verification steps — e.g., "Based on past learning: always add `includes()` for association chains to avoid N+1 queries."

- **Cost**: **Low** — Extends existing step with additional bash/grep calls. No new files, no new agents. The `read_project_history` step already has the infrastructure for frontmatter scanning.
- **Benefit**: Every debug session, adhoc fix, and resolved todo becomes visible during planning. Past mistakes surface before they're repeated.
- **Dependencies**: Recommendations #2 and #3 (debug frontmatter and learning capture) make this much more effective, but this works partially with existing SUMMARY.md data alone.

#### 2. Add YAML frontmatter to debug session docs

- **Classification**: Refactor existing
- **Source**: CE's `compound-docs` YAML schema concept
- **Target**: `mindsystem/templates/DEBUG.md` and `agents/ms-debugger.md`
- **What changes**: Add structured frontmatter to debug session files:

  ```yaml
  ---
  status: gathering | investigating | fixing | verifying | resolved
  trigger: "user description"
  created: ISO timestamp
  updated: ISO timestamp
  subsystem: [same enum as SUMMARY.md: auth, payments, ui, api, database, infra, testing]
  tags: [searchable keywords]
  symptoms: ["observable error 1", "observable error 2"]
  root_cause: "what caused it" (populated on resolution)
  resolution: "what fixed it" (populated on resolution)
  phase: "XX-name" (which phase this occurred in, if applicable)
  ---
  ```

  The `subsystem` and `tags` fields match SUMMARY.md's existing vocabulary, enabling unified grep searches. The `symptoms`, `root_cause`, and `resolution` fields are populated progressively as the debug session advances.

- **Cost**: **Low** — Template change + minor agent prompt update. Debug docs already have YAML frontmatter; this extends it.
- **Benefit**: Debug sessions become searchable by the same mechanism as SUMMARY.md. "Last time we debugged a database issue, what was the root cause?" becomes answerable via grep.
- **Dependencies**: None. Valuable on its own, enables Recommendation #1.

#### 3. Add post-resolution learning capture to debug and do-work workflows

- **Classification**: Adapt from CE
- **Source**: CE's `/workflows:compound` auto-invoke concept
- **Target**: `mindsystem/workflows/debug.md` and `mindsystem/workflows/do-work.md`
- **What changes**: After a debug session is resolved or adhoc work completes, add a brief capture step:

  **For debug (`ms-debugger` resolution):**
  When marking status as "resolved", ensure the resolution section includes:
  - `root_cause` in frontmatter (already captured in body, promote to frontmatter)
  - `resolution` in frontmatter (already captured in body, promote to frontmatter)
  - `prevention` section added to body: "How to avoid this in the future"

  **For do-work (adhoc summary):**
  Add `learnings` field to adhoc-summary frontmatter:
  ```yaml
  learnings:
    - "Key insight from this work"
    - "Pattern to remember"
  ```

  This is lighter than CE's 7-agent pipeline — no separate command, no schema validation, no decision menu. It's a natural extension of existing artifacts.

- **Cost**: **Low** — Template additions + minor workflow/agent updates. No new commands.
- **Benefit**: Learnings are captured at the moment of resolution (when context is freshest) rather than requiring a separate documentation step.
- **Dependencies**: Recommendation #2 (frontmatter for debug docs) should come first.

#### 4. Create LEARNINGS.md as curated cross-milestone index

- **Classification**: Adapt from CE
- **Source**: CE's `critical-patterns.md` concept — but as a curated index with source references, not a standalone knowledge store
- **Target**: New file `.planning/LEARNINGS.md` + new template `mindsystem/templates/learnings.md` + update to `mindsystem/workflows/complete-milestone.md`
- **What changes**: During `/ms:complete-milestone`, after ms-consolidator runs, add a step that:
  1. Scans all resolved debug docs (`.planning/debug/resolved/*.md`) — extract `root_cause`, `resolution`, `subsystem` from frontmatter
  2. Scans adhoc summaries with learnings (`.planning/adhoc/*-SUMMARY.md`) — extract `learnings` field
  3. Scans SUMMARY.md files for deviation auto-fixes and issues encountered
  4. Extracts patterns from todo resolutions
  5. Appends a new milestone section to `.planning/LEARNINGS.md`

  **Format — thin curated index with source references:**
  ```markdown
  # Project Learnings

  ## v1.0 Learnings

  ### Performance
  - **N+1 in email relationships**: Always add `includes()` for association chains → `debug/resolved/n-plus-one-brief.md`
  - **Slow list rendering >50 items**: Use cursor pagination, not offset → `adhoc/2026-01-15-dashboard-perf-SUMMARY.md`

  ### Edge Runtime
  - **CommonJS libraries fail silently**: Verify ESM compat before choosing crypto/auth libraries → `phases/01-foundation/01-01-SUMMARY.md` (Issues Encountered)

  ### Database
  - **Migration ordering**: Create indexes in same migration as column addition → `phases/03-data/03-01-SUMMARY.md` (Deviation #1)
  ```

  Each entry is: **one-line prescriptive pattern + source reference**. Detail lives in the original artifact, not duplicated here.

  **What LEARNINGS.md does NOT contain** (to prevent overlap):
  - Architectural decisions → those live in PROJECT.md Key Decisions and v{X.Y}-DECISIONS.md
  - What was built → that lives in SUMMARY.md
  - Current status → that lives in STATE.md
  - "We chose X" entries → only "Watch out for X when doing Y" entries

  **Lifecycle:**
  - Append-only (new milestone sections added, old preserved)
  - Read by `read_project_history` during planning — keyword-matched against current phase goal, not loaded in full
  - Not referenced by STATE.md (STATE stays under 100 lines, focused on session restoration)
  - Survives all milestone boundaries as permanent project memory

- **Cost**: **Medium** — New template, workflow step addition, extraction logic. The ms-consolidator already reads these source files, so the data is accessible.
- **Benefit**: Cross-milestone knowledge persistence. Within a milestone, the expanded `read_project_history` search finds learnings directly in debug docs and adhoc summaries. At milestone boundaries, LEARNINGS.md preserves the curated patterns that would otherwise require scanning many individual SUMMARY.md files.
- **Dependencies**: More effective with Recommendations #2 and #3 (richer source data), but works with existing artifacts.

---

### Medium Impact (Consider)

#### 5. Enhance todo docs with structured frontmatter

- **Classification**: Adapt from CE
- **Source**: CE's `file-todos` skill (YAML frontmatter, dependencies, work logs)
- **Target**: `commands/ms/add-todo.md` and `commands/ms/check-todos.md`
- **What changes**: Add structured frontmatter to todo docs:

  ```yaml
  ---
  title: "Clear problem statement"
  subsystem: auth | payments | ui | api | database | infra | testing
  tags: [searchable keywords]
  priority: p1 | p2 | p3
  source: debug | verify-work | adhoc | user-idea | milestone-audit
  phase_origin: "XX-name" (which phase spawned this)
  ---
  ```

  Update `check-todos` to display todos grouped by subsystem and priority. Update `add-todo` to populate frontmatter fields.

- **Cost**: **Medium** — Template change + command updates. Existing todos would need migration or could coexist with old format.
- **Benefit**: Todos become searchable during planning (by subsystem/tags match). `check-todos` can surface phase-relevant todos automatically. Source tracking shows where ideas come from.
- **Dependencies**: None. Enhances Recommendation #1 (more sources to search).

---

### Low Impact (Optional)

#### 6. Add patterns-established tracking to plan-phase output

- **Classification**: Refactor existing
- **Source**: CE's pattern deduplication concept
- **Target**: plan-phase's `read_project_history` step
- **What changes**: When scanning SUMMARY.md frontmatter, collect all `patterns-established` fields into a cumulative list. Present to user during task breakdown: "Established patterns to maintain: [list]". This ensures new work follows patterns from prior phases rather than inventing new approaches.
- **Cost**: **Low** — Minor addition to existing step.
- **Benefit**: Pattern consistency across phases. Currently patterns-established exists in frontmatter but isn't systematically surfaced.
- **Dependencies**: None.

#### 7. Auto-surface debug docs when planning related phases

- **Classification**: Adapt from CE
- **Source**: CE's auto-invoke concept applied to retrieval
- **Target**: plan-phase workflow
- **What changes**: During `read_project_history`, if any resolved debug docs have matching `subsystem` or `tags` to the current phase, surface them as warnings: "Previous debug sessions in this area: [list with root causes]". Not a full learning integration — just awareness.
- **Cost**: **Low** — Additional grep in existing step.
- **Benefit**: "We debugged a database issue in this subsystem before" → planner is aware and can plan defensively.
- **Dependencies**: Recommendation #2 (debug frontmatter).

---

## Migration Considerations

### Breaking Changes

None. All recommendations extend existing artifacts and workflows. Existing projects continue working — new frontmatter fields are additive (old debug docs without `subsystem` are simply not matched by grep searches).

### Incremental Adoption Path

**Phase 1 — Enrich sources (Recommendations #2, #3):**
Add frontmatter to debug docs and learning capture to do-work/debug. This enriches the data before building retrieval. Low risk, immediate value for manual review.

**Phase 2 — Enable retrieval (Recommendation #1):**
Expand plan-phase to search enriched sources. Add `<learnings>` section to ms-plan-writer handoff. This is the core compounding behavior — past work surfaces during future planning. Depends on Phase 1 for maximum value but provides partial value with existing SUMMARY.md data.

**Phase 3 — Create cross-milestone index (Recommendation #4):**
Add LEARNINGS.md template and extraction step to milestone completion. This bridges milestone boundaries with a curated index. Distinct from PROJECT.md decisions and STATE.md session state.

**Phase 4 — Enhance peripherals (Recommendations #5, #6, #7):**
Structured todos, pattern tracking, auto-surfacing. Polish that builds on the core loop.

### What NOT to Adopt

**CE's 7-parallel-agent capture pipeline.** Mindsystem's philosophy is modularity over bundling. Spawning 7 subagents to document a solved problem is overkill for a solo developer workflow. Instead, extend existing artifacts (debug docs, adhoc summaries) with richer frontmatter.

**CE's separate `docs/solutions/` directory.** Mindsystem already has a natural home for knowledge — `.planning/debug/`, `.planning/adhoc/`, and SUMMARY.md files. Creating a parallel knowledge store would fragment the information model. Instead, make existing stores searchable.

**CE's enum-validated YAML schema.** A blocking validation gate that rejects documentation until YAML passes adds friction to a solo developer workflow. Mindsystem's approach of using consistent-but-flexible vocabulary (subsystem field in SUMMARY.md) is better suited. Let the frontmatter guide retrieval without blocking capture.

**CE's `/deepen-plan` command.** Spawning a subagent per relevant learning to enrich plans is heavy. Mindsystem's plan-phase already has a collaborative planning model where the user participates. Surfacing relevant learnings as context (Recommendation #1) achieves the same goal without a separate command.

**CE's auto-invoke triggers.** Detecting "that worked" phrases to auto-trigger documentation is clever but fragile. Mindsystem's existing capture points (SUMMARY.md after execution, debug doc resolution) are more reliable because they're integrated into the workflow rather than triggered by conversational signals.

---

## Resolved Questions

1. **LEARNINGS.md granularity**: Flat markdown file with milestone-scoped sections. Each entry is one-line pattern + source reference. No YAML frontmatter — the file is small enough for grep-based keyword matching without structured metadata. Detail lives in source artifacts, not duplicated here.

2. **LEARNINGS.md vs PROJECT.md overlap**: No overlap. PROJECT.md Key Decisions captures architectural *choices* ("Used jose over jsonwebtoken"). LEARNINGS.md captures reusable problem-solving *patterns* ("CommonJS libraries fail silently in Edge runtime"). Decisions constrain; learnings inform. See Design Decisions section for full distinction.

3. **LEARNINGS.md as persistent artifact**: Read during `read_project_history` only — keyword-matched against current phase goal. Not loaded at every workflow start like STATE.md. Not referenced by STATE.md (which stays under 100 lines for session restoration).

4. **Problem-scoped vs phase-scoped storage**: Keep phase-scoped storage. Add problem-scoped *retrieval* by enriching frontmatter (subsystem, tags, symptoms, root_cause) and expanding the sources searched during planning. No separate `docs/solutions/` directory.

## Open Questions

1. **Subsystem enum enforcement**: SUMMARY.md uses free-form subsystem values. Should plan-phase validate against a known list (like CE's enum), or remain flexible? Flexibility works for diverse projects but makes grep matching less reliable.

2. **Debug doc lifecycle**: Currently debug docs move to `resolved/` subdirectory. Should resolved debug docs be co-located with the phase they occurred in (`.planning/phases/XX/debug/`) for better phase-scoped retrieval? Or stay centralized in `.planning/debug/resolved/` for cross-phase searching?

3. **Adhoc work integration**: Adhoc summaries in `.planning/adhoc/` are date-stamped but not phase-linked. Should they reference which phase was active when the work happened? This would enable "what adhoc fixes happened during phase 3?" queries.
