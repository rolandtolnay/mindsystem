<conventions>

<plan_anatomy>
## Plan Anatomy

```yaml
---
phase: XX-name
plan: NN
type: execute        # or "tdd"
wave: N              # Pre-computed execution wave
depends_on: []       # Prior plans this requires
files_modified: []   # Exclusive file ownership
---
```

```xml
<objective>What and why</objective>
<execution_context>@-references to workflows/templates</execution_context>
<context>@-references to project files</context>
<tasks>
  <task type="auto">
    <name>Task N: Name</name>
    <files>paths</files>
    <action>What to do, what to avoid and WHY</action>
    <verify>How to prove completion</verify>
    <done>Measurable acceptance criteria</done>
  </task>
</tasks>
<verification>Overall checks</verification>
<success_criteria>Completion criteria</success_criteria>
<output>SUMMARY.md specification</output>
```

**Task specificity test:** Can Claude read the plan and start implementing without asking clarifying questions? If not, task is too vague.
</plan_anatomy>

<wave_execution>
## Wave Execution

Plans have `wave` number in frontmatter (pre-computed during planning):

**Wave assignment rules:**
- Plans with no dependencies → Wave 1
- Plans depending on wave 1 plans → Wave 2
- Wave number = max(dependency wave numbers) + 1

**Execution flow:**
1. Orchestrator discovers all plans in phase
2. Groups by wave number
3. Wave N: Spawn all plans as parallel subagents
4. Wait for wave N to complete, then wave N+1
5. Each agent has fresh 200k context at peak quality
</wave_execution>

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

**Update triggers:** After each plan execution, phase transitions, decisions made, blockers discovered.
</state_management>

<summary_system>
## SUMMARY System

Created after each plan execution. Provides compressed history for future context.

**Machine-readable frontmatter:** phase, plan, subsystem, tags, requires, provides, affects, tech-stack, key-files, duration, completed.

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
