<conventions>

<plan_anatomy>
## Plan Anatomy

Plans use pure markdown — no YAML frontmatter, no XML containers.

**Required sections:**

```markdown
# Plan NN: Action-oriented title

**Subsystem:** name | **Type:** execute (or tdd)

## Context
What and why — problem being solved, approach chosen, key constraints.

## Changes

### 1. Change name
**Files:** `exact/file/paths.ts`

Specific implementation instructions. What to do, what to avoid and WHY.
Include technology choices, data structures, behavior details, pitfalls.

### 2. Next change
**Files:** `other/file/paths.ts`

[Implementation details with inline code blocks where needed]

## Verification
- `command to prove completion`
- Observable behavior checks

## Must-Haves
- [ ] Measurable acceptance criterion 1
- [ ] Measurable acceptance criterion 2
```

**Inline metadata:** `**Subsystem:**` populates SUMMARY.md subsystem field. `**Type:** tdd` triggers lazy-load of TDD execution reference.

**Orchestration is separate:** Wave grouping and dependencies live in `EXECUTION-ORDER.md`, not in plans.

**Specificity test:** Can Claude read the plan and start implementing without asking clarifying questions? If not, the plan is too vague.
</plan_anatomy>

<execution_order>
## Execution Order

Wave grouping and dependencies live in a single `EXECUTION-ORDER.md` file per phase, separate from plans:

```markdown
# Execution Order

## Wave 1 (parallel)
- 01-PLAN.md — Create user model and API endpoints
- 02-PLAN.md — Set up authentication middleware

## Wave 2 (after Wave 1)
- 03-PLAN.md — Build dashboard with protected routes
- 04-PLAN.md — Create admin panel
```

**Benefits:**
- Plans are pure execution prompts — zero orchestration metadata
- Orchestrator reads one file instead of scanning N plan files
- Human-readable, easy to override

**Validation:** A shell script validates all plans are listed, no missing references, no file conflicts within waves.
</execution_order>

<deviation_rules>
## Deviation Rules

Executor handles unplanned discoveries automatically:

- **Rule 1: Auto-fix bugs** — Code doesn't work → fix immediately, track for SUMMARY
- **Rule 2: Auto-add missing critical** — Missing security/validation → add immediately
- **Rule 3: Auto-fix blocking issues** — Missing dep, wrong types → fix to unblock
- **Rule 4: Ask about architectural changes** — New tables, new services → STOP, report to orchestrator

**Priority:** If Rule 4 applies, STOP. Otherwise auto-fix with Rules 1-3.

**Edge cases:**
- "Missing validation" → Rule 2 (critical security)
- "Crashes on null" → Rule 1 (bug)
- "Need new table" → Rule 4 (architectural)
- "Need new column" → Rules 1-2 (depends on context)
</deviation_rules>

<state_management>
## State Management

**STATE.md** is the project's living memory. <100 lines — a digest, not an archive.

**Sections:** Project Reference, Current Position, Performance Metrics, Accumulated Context (Decisions, Pending Todos, Blockers/Concerns), Session Continuity.

**Update triggers:** After each plan execution (via script), phase transitions, decisions made, blockers discovered.
</state_management>

<summary_system>
## SUMMARY System

Created after each plan execution via inline instructions in the executor workflow (~20 lines, not a separate template).

**Machine-readable frontmatter:** subsystem, provides, affects, patterns-established, key-decisions, key-files, mock_hints.

**Subsystem vocabulary growth:** If plan work introduces a novel subsystem not in config.json, the executor appends it to the `subsystems` array, uses it in SUMMARY.md frontmatter, and logs the addition in the summary's decisions section. No blocking gate — append and log immediately. Future phases pick up the new subsystem automatically.

**Substantive one-liner:**
- Good: "JWT auth with refresh rotation using jose library"
- Bad: "Phase complete"

**Deviation documentation:** Each auto-fix gets a section with rule applied, trigger, issue, fix, files, commit.
</summary_system>

<atomic_commits>
## Atomic Commits

Each task gets its own commit immediately after completion.

**Format:** `{type}({phase}-{plan}): {concise description}`

**Types:** feat, fix, test, refactor, docs, chore

**Rules:**
- Stage files individually (never `git add .`)
- Commit immediately after task verification
- TDD tasks may have 2-3 commits (test/feat/refactor)
- Metadata commit after SUMMARY.md created
</atomic_commits>

</conventions>
