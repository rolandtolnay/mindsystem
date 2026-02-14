# Research-Phase Redesign: Parallel Specialized Agents

## Problem

Research-phase uses a single generalist `ms-researcher` agent that handles all research dimensions — external documentation, codebase patterns, and best practices — in one context. This creates three problems:

1. **Source dilution** — The agent's context fills with codebase details when it should focus on external docs, and vice versa. Different research sources benefit from fundamentally different prompting strategies.
2. **No codebase awareness** — The researcher operates blind to existing project patterns, established libraries, and past failures. It may recommend solutions that conflict with what the project already does.
3. **No compound knowledge** — Learnings, prior summaries, and debug resolutions are only surfaced during planning, not during research. The "discover library X online but we already use library Y" problem goes undetected until planning.

## Competitive Analysis

Three systems analyzed: Mindsystem (current), Compound Engineering, HumanLayer.

### Mindsystem (Current State)

**Research-phase architecture:**
- Two entry points: `/ms:research-phase` (single phase, single agent) and `/ms:research-project` (project-wide, 4 parallel agents)
- Phase research spawns a single `ms-researcher` with configurable mode (ecosystem/feasibility/implementation/comparison)
- Tool hierarchy: Context7 → Official docs → Perplexity deep → WebSearch → Project files
- Output: single RESEARCH.md with sections (Standard Stack, Architecture Patterns, Don't Hand-Roll, Common Pitfalls, Code Examples, State of the Art)
- Source confidence levels: HIGH/MEDIUM/LOW with attribution
- Checkpoint mechanism for handling uncertainty (modal: stop → ask user → continuation agent)

**Strengths:**
- Strong context efficiency — fresh 200k per agent, orchestrator stays lean
- Verification protocol built into agent (checklist for pitfalls: deprecated APIs, single-source reliance, negative claims without evidence)
- Honest reporting culture — "I couldn't find X" and "LOW confidence" are valued outputs
- CONTEXT.md integration — respects locked user decisions from `/ms:discuss-phase`
- Research output is directly actionable in planning (prescriptive, not exploratory)

**Weaknesses:**
- Phase research is single-agent (no parallel investigators, no cross-validation)
- No feedback loop from planning back to research
- Verification is self-policing (no independent reviewer)
- No cross-phase research deduplication or shared cache
- Synthesizer (for research-project) uses Haiku — may miss nuanced trade-offs
- No research depth selection at command level
- Pitfall warnings not integrated into execution verification

### Compound Engineering

**Research architecture:**
- 5 specialized research agents: best-practices, framework-docs, git-history, learnings, repo-research
- 5-phase methodology: Check skills first → Deprecation check → Online research → Synthesize
- Research embedded in planning — `/workflows:plan` spawns parallel local research (repo-research-analyst + learnings-researcher), then conditionally spawns external research
- Compound knowledge loop: `/workflows:compound` captures solved problems → `docs/solutions/` → `learnings-researcher` surfaces them in future planning

**Key patterns worth studying:**
- **Source-type decomposition** — Agents split by what they look at (repo patterns, past solutions, external best practices, framework docs), not by what kind of answer they produce
- **Compound knowledge loop** — Solve once, document, surface forever. Genuine feedback loop that prevents repeating mistakes
- **Deprecation checks** — Mandatory during research. Prevents recommending dead APIs
- **Protected artifacts** — Plans and solutions never flagged for deletion (pipeline outputs)
- **Parallel specialists** — Security, performance, simplicity reviewers run simultaneously during code review

**Potential overkill for Mindsystem:**
- 5 separate research agents may be excessive — git-history-analyzer is niche, could fold into codebase analysis
- TeammateTool/swarm infrastructure is heavy — Mindsystem's simpler Task-based parallelism is sufficient
- Context window management under-specified (no 50% rule equivalent)

### HumanLayer

**Research architecture:**
- 6 specialized agents: codebase-locator, codebase-analyzer, codebase-pattern-finder, thoughts-locator, thoughts-analyzer, web-search-researcher
- All agents are **documentarians only** — "describe what IS, not what SHOULD BE"
- Research stored in `thoughts/shared/research/` with metadata and GitHub permalinks
- Parallel sub-agents per research session, Opus orchestrator with Sonnet workers

**Key patterns worth studying:**
- **Strict documentarian discipline** — Agents describe what exists, never suggest improvements. Clear role boundaries.
- **Method-based decomposition** — Agents split by investigation method (locate/analyze/pattern-find/search), not by source type
- **Verification-first planning** — Success criteria split into Automated vs Manual verification (mandatory)
- **Handoff system** — Session continuity via structured handoff documents
- **"No Open Questions in Final Plan"** — Planning stops if unresolved questions exist

**Gaps:**
- No skill/knowledge system (knowledge not reusable across sessions)
- No compound knowledge loop (learnings only captured via manual handoffs)
- No scope enforcement during execution

### Cross-System Comparison

| Dimension | Mindsystem | Compound Engineering | HumanLayer |
|-----------|-----------|---------------------|------------|
| Research parallelization | 4 parallel for project; single for phase | Parallel local + conditional external | Parallel sub-agents per session |
| Research agent count | 2 (researcher + synthesizer) | 5 specialized | 6 specialized |
| Knowledge persistence | LEARNINGS.md + SUMMARY.md frontmatter | `docs/solutions/` with learnings-researcher | `thoughts/` with sync |
| Feedback loop | One-way (research → planning) | Bidirectional (compound → learnings → planning) | Partial (handoffs only if created) |
| Context management | Explicit 50% rule, token budgets | Under-specified | Plans designed for ~50% context |
| Agent role clarity | Mode-based (ecosystem/feasibility/etc.) | Category-based (review/research/design) | Documentarian-only (strict) |
| Decomposition axis | Knowledge dimension (stack/features/arch/pitfalls) | Source type (repo/learnings/best-practices/docs) | Investigation method (locate/analyze/find) |

### Key Insight: Decomposition Strategies

The three systems split research differently:
- **Mindsystem** splits by knowledge dimension — what you want to know (Stack? Features? Architecture?)
- **CE** splits by source type — where you look (repo? past solutions? external docs? framework docs?)
- **HumanLayer** splits by investigation method — how you look (locate? analyze? pattern-find?)

For phase research, **source-type decomposition** (CE's approach) maps best to the problem. Different sources need different tools, different prompting, and different expertise. A codebase agent needs Grep/Glob/Read. An external docs agent needs Context7/WebSearch. A best practices agent needs Perplexity/WebSearch. Mixing these in one agent dilutes all three.

---

## First Principles Analysis

### Assumptions Challenged

| Assumption | Status | Why |
|------------|--------|-----|
| Single researcher handles all dimensions | **Breaks** | Different sources need different tools and prompting strategies. Mixing dilutes focus. |
| Research modes are the right decomposition | **Partially holds** | Modes describe what kind of answer you want (useful for framing), but don't address source diversity. |
| Tool hierarchy is correct | **Holds** | Context7 → Official → Perplexity → WebSearch is a good authority ranking for external knowledge. |
| Single RESEARCH.md output | **Holds** | Plan-phase consumes section-by-section. Single file simpler for downstream. Multiple agents contribute to one output via synthesis. |
| Minimal orchestrator | **Holds** | Core Mindsystem philosophy. |
| Research is primarily about external knowledge | **Breaks** | Codebase is a primary source. Existing patterns, libraries, past failures are as important as external docs. |
| Research and codebase analysis are separate | **Breaks** | They must inform each other. "Use library X" vs "we already use library Y" needs reconciliation. |
| Single mode per invocation | **Partially holds** | Most phases need multiple dimensions. Mode useful for synthesis framing, not agent selection. |
| Phase research doesn't need parallelism | **Breaks** | Convention, not necessity. Same latency, better coverage. |
| Learnings consumed during planning only | **Partially holds** | Plan-phase dependency scanning stays. But research benefits from lightweight pattern scanning to reconcile external vs existing. |
| Self-policed quality | **Partially holds** | Multiple specialized agents naturally cross-check by covering different ground. |

### Fundamental Truths

1. **LLMs have stale knowledge about external libraries.** The irreducible reason research exists. External tools (Context7, WebSearch, Perplexity) are the only bridge.

2. **Different research sources benefit from different prompting strategies.** An agent optimized for library documentation lookup is fundamentally different from one optimized for codebase pattern analysis.

3. **Research quality scales with source diversity, not single-source depth.** Three perspectives cover more ground than one agent going deeper on any single dimension.

4. **Parallel agent latency ≈ single agent latency.** Multiple sub-agents running simultaneously don't meaningfully increase wall-clock time.

5. **The codebase is a primary research source.** Existing patterns, libraries, past failures, and debug resolutions are as important as external documentation.

6. **Research output must be prescriptive, not exploratory.** Parallel research without synthesis is worse than serial research. Synthesis resolves "consider X or Y" into "use X because [evidence]."

7. **A cheap pre-scan dramatically improves agent targeting.** Reading dependency files and CONTEXT.md (5 seconds) enables much better agent prompts than generic "research this phase."

---

## Design Decisions

### Decision 1: Learnings Scanning — Both Scan Independently

**Options evaluated:**
- **A: Research absorbs it** — Codebase agent scans learnings, plan-phase drops scanning. Risk: data loss if research skipped.
- **B: Both scan independently** — Research scans for "what patterns exist" (tech choices). Planning scans for "what dependencies exist" (plan structure). Small overlap, different purposes.
- **C: Keep in planning only** — Simplest, but research can't reconcile external recommendations against existing patterns.

**Decision: Option B.**

Rationale: Research and planning scan learnings for genuinely different purposes. Research asks "what has this project already solved that's relevant to our tech choices?" Planning asks "what structural dependencies constrain how I build this plan?" The overlap is minimal. If research is skipped (lightweight phases), planning still catches everything.

### Decision 2: Synthesis — Orchestrator Does It

**Options evaluated:**
- **A: Orchestrator synthesizes** — Reads 3 agent outputs, resolves conflicts, writes RESEARCH.md, presents to user.
- **B: Synthesis agent** — 4th agent reconciles findings in fresh context.

**Decision: Option A.**

Rationale:
- Synthesis involves judgment calls ("external recommends X, codebase uses Y — which?") that belong in main context with the user
- Aligns with Mindsystem philosophy: "Main context for collaboration, subagents for autonomous execution"
- Research-phase runs in its own session (/clear between research and planning) — context doesn't compete with downstream work
- No additional spawn latency
- If the orchestrator identifies a hard conflict, it can ask the user directly via AskUserQuestion

### Decision 3: New Dedicated Codebase Agent

A new `ms-codebase-researcher` agent with Grep/Glob/Read tools, optimized for:
- Scanning existing project patterns and established libraries
- Checking LEARNINGS.md for relevant entries
- Reading SUMMARY.md frontmatter for tech/patterns in same subsystem
- Finding debug resolutions for prior failures
- Reporting what conventions and patterns already exist

---

## Proposed Architecture

### Three Parallel Agents with Orchestrator Synthesis

```
Orchestrator (pre-scan: dependency file, CONTEXT.md, phase scope)
    ├── ms-researcher [External Docs] ──────┐
    ├── ms-codebase-researcher [Patterns] ──┤── Orchestrator synthesizes → RESEARCH.md
    └── ms-researcher [Best Practices] ─────┘
```

### Agent Responsibilities

| Agent | Focus | Tools | Key Questions |
|-------|-------|-------|---------------|
| **External Docs** (ms-researcher) | Library documentation, APIs, version-specific behavior, code examples | Context7, WebSearch, WebFetch | What does the latest documentation say? How does this API work? What version constraints exist? |
| **Codebase Patterns** (ms-codebase-researcher) | Existing patterns, established libraries, past learnings, prior summaries | Grep, Glob, Read | What has this project already built that's relevant? What patterns are established? What failed before? |
| **Best Practices** (ms-researcher) | Community consensus, common pitfalls, proven approaches, SOTA, alternatives | Perplexity, WebSearch | What do practitioners recommend? Common mistakes? Current vs deprecated approaches? |

### How Agents Map to RESEARCH.md Sections

| RESEARCH.md Section | External Docs | Codebase Patterns | Best Practices |
|---------------------|--------------|-------------------|----------------|
| Standard Stack | What to use, versions, APIs | What we already use | Community recommendations |
| Architecture Patterns | Library-recommended patterns | Existing project patterns | Industry patterns |
| Don't Hand-Roll | Library solutions available | Internal solutions that exist | Known solved problems |
| Common Pitfalls | Library-specific gotchas | Past failures from learnings | Community war stories |
| Code Examples | Verified from docs | Existing project examples | Community examples |
| State of the Art | Latest versions, new APIs | — | Current vs deprecated |

### Orchestrator Flow

1. **Pre-scan** (5-10 seconds) — Read dependency file (pubspec.yaml/package.json), CONTEXT.md decisions, phase scope from ROADMAP.md. Extract: existing dependencies, locked decisions, phase goal.

2. **Determine research question** — Frame the research based on phase description + pre-scan context. Research modes (ecosystem/feasibility/implementation/comparison) shape question framing, not agent architecture.

3. **Spawn 3 agents in parallel** — Each receives pre-scan context + research question, framed for their specialty. All agents know what the project already uses.

4. **Wait for completion** — Same latency as current single agent.

5. **Synthesize** — Orchestrator reads all 3 outputs, reconciles conflicts. If a genuine conflict needs user input ("external recommends X but project uses Y"), ask via AskUserQuestion. Write unified prescriptive RESEARCH.md.

6. **Present & commit** — Show key findings to user, commit RESEARCH.md.

### Research Modes Survive as Synthesis Framing

All three agents always run. The mode affects:
- How the research question is framed for each agent
- Which RESEARCH.md sections get emphasized
- Whether the synthesizer focuses on "what to pick" (ecosystem) vs "can we do it" (feasibility) vs "how exactly" (implementation) vs "X or Y" (comparison)

### What This Preserves from Current Design

- RESEARCH.md format and section structure (plan-phase consumption unchanged)
- Confidence levels with source attribution
- CONTEXT.md integration (locked decisions respected)
- Verification protocol (carried forward into each agent)
- Checkpoint mechanism (if any agent needs clarification)
- Research modes (reframed as synthesis strategy)

### What Changes

| Current | Proposed |
|---------|----------|
| Single ms-researcher agent | 3 parallel specialized agents |
| Research blind to codebase | Codebase-patterns agent surfaces existing patterns, learnings, past failures |
| Mode selects agent behavior | Mode frames synthesis strategy |
| Self-policed quality | Cross-validation through source diversity |
| External knowledge only | External + internal knowledge reconciled |
| Agent writes RESEARCH.md | Orchestrator synthesizes and writes RESEARCH.md |

---

## Open Questions (To Resolve During Planning)

1. **ms-researcher reuse** — Should external-docs and best-practices be two instances of existing `ms-researcher` with different prompts, or should one/both be new agent types?
2. **Agent output contract** — What structured format should each agent return for optimal synthesis?
3. **Pre-scan depth** — How deep should the orchestrator's pre-scan go? Just dependency file, or also scan for import patterns?
4. **Mode selection UX** — Should the user still pick a mode, or should the orchestrator auto-detect based on phase description?
5. **Checkpoint handling** — With 3 parallel agents, how do checkpoints work? Wait for all, or handle per-agent?
6. **Existing ms-researcher prompt** — How much of the current researcher's verification protocol, tool strategy, and output format carries forward into the specialized agents?
