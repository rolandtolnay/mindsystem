# Planning Pipeline Rework Proposal

## Problem Statement

Two issues drive this rework:

**Token waste (MIN-89):** A real executor trace showed 135k tokens, 9 minutes, 90 tool uses for ~500 lines of meaningful output. Breakdown: ~50% redundant context loading (executor re-reads files the plan already encoded), ~20-30% post-execution overhead (git ceremony, STATE updates, summary template compliance, mechanical must_haves verification), ~30% actual code writing. The execute-plan workflow is 1,200 lines + summary template 300 lines = 1,500 lines of instruction overhead loaded before the plan content.

**Plan verbosity (MIN-83):** Mindsystem plans use XML task structure (`<task><action><verify><done>`) and YAML frontmatter while Claude Code's native plans use simple markdown sections and achieve the same or better results. Plans carry orchestration metadata (waves, dependencies) mixed with execution content, forcing executors to load data they don't need.

**Root cause:** The plan serves two audiences (executor + orchestrator) without separating their concerns. The executor carries three jobs (write code + handle process ceremony + generate knowledge artifacts) when it should focus on one.

## Research Findings

### Claude Code Plans

Analyzed 12 native Claude Code plan files. Universal structure: H1 title → `## Context` → numbered `## Changes` sections → `## Verification`. No YAML frontmatter. No XML. ~90% actionable content, ~10% structure. Average plan ~110 lines. Smallest effective plan: 44 lines.

Key insight: plans are executable instructions, not machine-readable specifications. They optimize for a single intelligent reader executing in one context.

### Mindsystem Pipeline Audit

**Token budget per executor:** execute-plan.md (~4,850 tokens) + summary.md template (~1,175) + conditional sections loaded unconditionally (~875) = ~6,900 tokens of overhead before plan content.

**Frontmatter consumption audit (PLAN.md):**
- `wave:` — 12 mechanical refs in execute-phase. CRITICAL for parallelism.
- `must_haves:` — 2 refs in verifier. Drives verification loop.
- `subsystem_hint:` — 1 ref. Executor uses for summary population.
- `gap_closure:` — 0 refs. DEAD CODE.
- Others (`depends_on`, `files_modified`, `user_setup`) — 1 ref each, lightly consumed.

**Summary frontmatter audit:** Heavily consumed. `requires`/`provides`/`affects` (8 refs) powers context assembly in plan-phase. `patterns-established` (3 refs) ensures consistency. `mock_hints` drives verify-work. This is the knowledge compounding system (MIN-39) — genuinely valuable, not decorative.

**Execute-plan.md breakdown:** Core execution ~120 lines (essential), deviation rules 159 lines (essential but verbose), auth gates 95 lines (conditional — CLI tools only), TDD execution 55 lines (conditional), user setup 68 lines (conditional), agent tracking 46 lines (rarely used), offer_next 162 lines (essential).

### Claude Code System Prompts

Plans require three sections: Context (why), Implementation (what/how), Verification (validate). Key principle: "Concise enough to scan quickly, detailed enough to execute effectively." Plans use markdown headers, not XML. Single recommended approach, not alternatives.

## First-Principles Analysis

### Fundamental Truths

1. **Claude's quality degrades with context usage.** The 50% target is measured, not theoretical.
2. **Plans must be complete for autonomous execution.** But "complete" means what's needed to write code — not orchestration metadata.
3. **Independent work can be parallelized.** The mechanism (wave numbers vs dependency lists vs execution order) is flexible.
4. **Knowledge must compound across phases.** Summary frontmatter feeds future planning. This is valuable.
5. **Deterministic operations waste tokens when done by an LLM.** STATE.md updates, topological sorting — scripts are faster and cheaper.
6. **Every token loaded into an executor that doesn't improve code output is waste.**
7. **The plan IS the prompt.** Simpler plan = simpler execution = more context for code quality.
8. **The orchestrator must stay lean.** Lives in main context with the user.

### Key Insight: Separate Orchestration from Execution

The plan currently serves two audiences:
- **Executor:** needs Context, Changes, Verification, Must-Haves
- **Orchestrator:** needs wave grouping, dependencies, file conflicts

Mixing these means the executor loads orchestration metadata, and the orchestrator must scan all plans for metadata. Separating them improves both.

## Proposed Solution

### 1. New Plan Format: Pure Markdown

Replace XML task structure and YAML frontmatter with Claude Code-style markdown:

```markdown
# Plan 01: Create login endpoint with JWT

**Subsystem:** auth | **Type:** tdd

## Context
Why this work exists. Problem being solved. Approach chosen.

## Changes

### 1. Create auth route handler
**Files:** `src/api/auth/login.ts`

POST endpoint accepting {email, password}. Query User by email, compare
password with bcrypt. On match, create JWT with jose library, set as
httpOnly cookie. Return 200. On mismatch, return 401.

```typescript
// Key implementation detail or exact code when precision matters
export async function POST(req: Request) { ... }
```

### 2. Add password comparison utility
**Files:** `src/lib/crypto.ts`

[Changes with inline code blocks and line numbers where needed]

## Verification
```bash
curl -X POST localhost:3000/api/auth/login -d '{"email":"test@example.com","password":"test"}' -v
# Expect: 200 with Set-Cookie header
```
- `grep -r "comparePassword" src/lib/` returns match
- `npm test -- --grep auth` passes

## Must-Haves
- [ ] POST /api/auth/login returns 200 with Set-Cookie for valid credentials
- [ ] Invalid credentials return 401
- [ ] Passwords compared with bcrypt, never plaintext
```

**What changed:**
- No YAML frontmatter (wave, depends_on, files_modified removed from plans)
- No XML containers (`<task>`, `<action>`, `<verify>`, `<done>` gone)
- Subsystem and type as inline metadata (one line, not YAML block)
- Must-haves as markdown checklist (verifier reads this section)
- Changes as numbered markdown sections with inline file paths
- Tables, code blocks, line numbers used liberally (following Claude Code patterns)

**What's preserved:**
- Subsystem hint (for summary generation and knowledge compounding)
- Type indicator (for TDD routing — `tdd` triggers lazy-load of TDD reference)
- Must-haves (for verifier — moved from frontmatter to inline section)
- Full context, changes, verification structure
- Enough detail for autonomous execution

### 2. EXECUTION-ORDER.md: Separate Orchestration Artifact

The plan-writer outputs a separate file alongside plans:

```markdown
# Execution Order

## Wave 1 (parallel)
- 01-PLAN.md — Create user model and API endpoints
- 02-PLAN.md — Set up authentication middleware

## Wave 2 (after Wave 1)
- 03-PLAN.md — Build dashboard with protected routes
- 04-PLAN.md — Create admin panel

## Wave 3 (after Wave 2)
- 05-PLAN.md — Integration tests and E2E verification
```

**Benefits:**
- Plans are pure execution prompts — zero orchestration metadata
- Orchestrator reads one small file instead of scanning N plan frontmatters
- Human-readable, easy to override (user can reorder plans)
- Single source of truth for execution structure
- Replaces `wave:` and `depends_on:` in every plan

**Validation:** A shell script can validate the execution order (all plans listed, no missing references, no file conflicts within waves). This replaces the orchestrator reasoning about wave grouping.

### 3. Stripped Executor Workflow (~350 lines, down from 1,200)

**Keep (essential for every execution):**
- Core execution loop: read plan → execute changes → verify
- Simplified deviation rules (~30 lines, down from 159): 4 rules as concise bullets with one example each
- Task commit protocol (~50 lines): `git add <files> && git commit -m "message"`, capture hash from output
- Inline summary instructions (~20 lines): field list + prose summary, replaces 300-line template
- Offer-next flow (~80 lines)

**Remove entirely:**
- TDD execution section → lazy-load `tdd-execution.md` only when plan `Type: tdd`
- Auth gates section → handle dynamically (if CLI error, use AskUserQuestion)
- Agent tracking/resume → remove (rarely used, not worth 46 lines per executor)
- must_haves verification → verifier handles this (executor just wrote the code, no need to grep for it)
- STATE.md update instructions → orchestrator handles via script after executor returns
- 6x git status calls → one `git status` before first commit, capture hash inline

**Move to lazy-load references:**
- TDD execution: separate `tdd-execution.md` reference, loaded only for TDD plans
- Auth gate handling: 10-line inline instruction "If CLI/API returns auth error, use AskUserQuestion to ask user for credentials, then retry"

**Estimated savings:** ~4,500 tokens per executor = ~13,500 tokens per 3-plan phase.

### 4. Lightweight Summary Creation

Replace 300-line summary template with ~20 lines of inline instructions in executor workflow:

```
After all tasks complete, create SUMMARY.md:

---
subsystem: [from plan header]
provides: [what this plan created/enabled]
affects: [other subsystems impacted]
patterns-established: [new coding patterns introduced]
key-decisions: [technical choices made and why]
key-files:
  created: [new files]
  modified: [changed files]
mock_hints: [if UI work, list transient states and external data dependencies]
---

## Summary
[3-5 sentence prose: what was built, key technical approach, what it enables]
```

**What's preserved:** All fields consumed by the knowledge compounding system (requires/provides/affects graph, patterns-established, key-decisions, tech-stack, key-files, mock_hints).

**What's removed:** The 300-line template with examples, guidelines, formatting rules, and edge case handling. The executor is intelligent enough to fill structured fields from a simple list.

### 5. Script Extraction

**STATE.md update script** (`scripts/update-state.sh`):
- Input: phase number, plan number, status (complete/failed)
- Action: Find the plan entry in STATE.md, update status and timestamp
- Called by: execute-phase orchestrator after each executor returns
- Saves: ~200 tokens of executor instructions + ~150 tokens of executor reasoning per plan

**Execution order validation script** (`scripts/validate-execution-order.sh`):
- Input: phase directory path
- Action: Check all PLAN.md files are listed in EXECUTION-ORDER.md, no missing references, warn on potential file conflicts within waves
- Called by: execute-phase before launching executors
- Saves: ~100 tokens of orchestrator reasoning

**Viability assessment:** These scripts save moderate tokens individually (~300-500 per invocation) but their main value is removing ERROR-PRONE deterministic logic from LLM context. STATE.md updates done by the executor often had 3 separate edit operations and occasional formatting errors. A script does it correctly every time.

### 6. Task Limit Increase: 2 → 3 Per Plan

With executor overhead dropping from ~6,900 to ~2,400 tokens, there's ~4,500 tokens of headroom. At ~1,500-2,000 tokens per task description, the limit can safely increase from 2 to 3 tasks per plan while staying within the 50% context target.

**Impact:** Fewer plans per phase → fewer agent spin-ups → less orchestration overhead → faster phase completion. A 6-task phase goes from 3 plans to 2 plans.

## Impact Summary

| Metric | Current | Proposed | Improvement |
|--------|---------|----------|-------------|
| Executor workflow size | ~4,850 tokens | ~1,400 tokens | -71% |
| Summary template | ~1,175 tokens (separate file) | ~80 tokens (inline) | -93% |
| Total executor overhead | ~6,900 tokens | ~2,400 tokens | -65% |
| Per-phase overhead (3 plans) | ~20,700 tokens | ~7,200 tokens | -65% |
| Tasks per plan | 2 | 3 | +50% |
| Plans for 6-task phase | 3 | 2 | -33% |
| Plan format | YAML + XML + markdown | Pure markdown | Simpler |
| Orchestration metadata | In every plan (frontmatter) | One file (EXECUTION-ORDER.md) | Centralized |

## Downstream Effects

| Component | File(s) | Change | Scope |
|-----------|---------|--------|-------|
| Plan format reference | `mindsystem/references/plan-format.md` | Complete rewrite — new markdown format spec | M |
| Executor workflow | `mindsystem/workflows/execute-plan.md` | Strip from 1,200 to ~350 lines, inline summary | L |
| Summary template | `mindsystem/templates/summary.md` | Delete — replaced by inline instructions | XS |
| Plan-writer agent | `agents/ms-plan-writer.md` | New format output, execution order generation | M |
| Phase prompt template | `mindsystem/templates/phase-prompt.md` | Update plan format expectations | S |
| Execute-phase workflow | `mindsystem/workflows/execute-phase.md` | Read EXECUTION-ORDER.md, integrate STATE script | S |
| Plan-phase workflow | `mindsystem/workflows/plan-phase.md` | Adjusted handoff, execution order in flow | S |
| Verifier agent | `agents/ms-verifier.md` | Read ## Must-Haves from markdown | XS |
| Plan-checker agent | `agents/ms-plan-checker.md` | Read EXECUTION-ORDER.md for validation | XS |
| Scope estimation | `mindsystem/references/scope-estimation.md` | Update overhead estimates, increase task limit | XS |
| TDD reference | `mindsystem/references/tdd.md` | Extract executor-specific section for lazy-load | S |
| Scripts | `scripts/update-state.sh`, `scripts/validate-execution-order.sh` | New scripts | S |

## Risk Assessment

1. **Knowledge compounding regression** — Summary fields power cross-phase intelligence. Mitigation: preserve all consumed fields, only simplify the creation process (inline instructions vs template).
2. **Executor quality without detailed instructions** — The 1,200-line workflow included edge cases learned from experience. Mitigation: condense essential wisdom into fewer lines rather than removing it. Deviation rules become 30 lines instead of 159, not 0.
3. **Plan-writer drift with simpler format** — Less structure means more room for the plan-writer to produce inconsistent output. Mitigation: clear spec in plan-format.md with examples. Consider Opus for plan-writer (better judgment).
4. **Execution order maintenance** — EXECUTION-ORDER.md is a new artifact that must stay in sync with plans. Mitigation: validation script catches drift. Plan-writer generates both atomically.
5. **3-task limit pushes context** — More tasks per plan means more content. Mitigation: only increase to 3, not 4. Monitor context usage in first few phases.
