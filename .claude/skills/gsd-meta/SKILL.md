---
name: gsd-meta
description: Instant GSD expert for diagnosing, understanding, and planning GSD framework changes. Use when working on GSD itself or asking how it works.
---

<objective>
Provides instant expertise about the GSD framework for meta-discussions, diagnostics, and planning GSD changes. Use when working on GSD itself, diagnosing GSD issues, or asking how GSD works.
</objective>

<intake>
What do you need help with?

1. Understand GSD concepts (how things work)
2. Diagnose an issue (something isn't working)
3. Plan a change (add/modify GSD features)
4. Just ask a question

**For options 1 & 4:** Ask directly — essential knowledge below covers most questions.
**For options 2 & 3:** Route to specific workflow.
</intake>

<routing>
| Response | Next Action |
|----------|-------------|
| 1, "understand", "how does", "what is", "explain" | Answer using essential_knowledge below |
| 2, "diagnose", "not working", "broken", "bug", "issue" | Read workflows/diagnose.md and follow it |
| 3, "plan", "add", "modify", "change", "extend", "new command", "new agent" | Read workflows/plan-change.md and follow it |
| 4, direct question | Answer using essential_knowledge, reference files if deeper context needed |

**Intent-based routing (if user provides clear intent without selecting):**
- "Why isn't X working?" → workflows/diagnose.md
- "How do I add a new command?" → workflows/plan-change.md
- "What is wave execution?" → Answer from essential_knowledge
- "Explain checkpoints" → Answer from essential_knowledge, deeper: references/concepts.md

**After reading a workflow, follow it exactly.**
</routing>

<essential_knowledge>

<what_gsd_is>
GSD (Get Shit Done) is a meta-prompting and context engineering system for Claude Code that solves **context rot** — the quality degradation that happens as Claude fills its context window.

**Core insight:** Claude's quality degrades predictably:
- 0-30% context: Peak quality
- 30-50%: Good quality
- 50-70%: Degrading ("I'll be more concise now" = cutting corners)
- 70%+: Poor quality

**The 50% rule:** Plans should complete within ~50% context usage. Stop BEFORE quality degrades, not at context limit.

**Solution:** Aggressive atomicity. Plans stay small (2-3 tasks max). Each plan executes in a fresh subagent with 200k tokens purely for implementation.
</what_gsd_is>

<philosophy>
**Solo developer + Claude workflow.** No enterprise patterns (sprint ceremonies, RACI matrices, stakeholder management). User is the visionary. Claude is the builder.

**Plans ARE prompts.** PLAN.md is not a document that gets transformed — it IS the executable prompt containing objective, context, tasks, and verification.

**Claude automates everything.** If it has CLI/API, Claude does it. Checkpoints are for verification (human confirms visual/UX) and decisions (human chooses direction), not manual work.

**Goal-backward planning.** Don't ask "what should we build?" — ask "what must be TRUE for the goal to be achieved?" This produces verifiable requirements, not vague task lists.

**Dream extraction, not requirements gathering.** Project initialization is collaborative thinking to help users discover and articulate what they want. Follow the thread, challenge vagueness, make abstract concrete.
</philosophy>

<repository_structure>
```
gsd/
├── agents/               # Subagent definitions (Task tool configs)
│   ├── gsd-executor.md       # Executes PLAN.md files
│   ├── gsd-verifier.md       # Verifies phase goals achieved
│   ├── gsd-planner.md        # Creates PLAN.md files
│   ├── gsd-debugger.md       # Systematic debugging
│   ├── gsd-researcher.md     # Domain research
│   └── ...
├── commands/gsd/         # Slash commands (/gsd:*)
│   ├── new-project.md        # Initialize project
│   ├── plan-phase.md         # Create plans for phase
│   ├── execute-phase.md      # Execute all plans
│   ├── progress.md           # Where am I? What's next?
│   └── ...
├── get-shit-done/        # Core system
│   ├── workflows/            # Step-by-step procedures
│   ├── templates/            # Output structures (STATE.md, SUMMARY.md, etc.)
│   └── references/           # Deep knowledge (plan-format.md, checkpoints.md)
└── scripts/              # Shell scripts for automation
```

**Installation:** `npx get-shit-done-cc` copies to `~/.claude/` (global) or `.claude/` (local).
</repository_structure>

<user_project_files>
GSD creates `.planning/` directory in user projects:

```
.planning/
├── PROJECT.md        # Vision, constraints, decisions
├── REQUIREMENTS.md   # Checkable requirements with traceability
├── ROADMAP.md        # Phases from start to finish
├── STATE.md          # Living memory (position, decisions, blockers)
├── config.json       # Execution preferences
├── research/         # Domain research (STACK.md, FEATURES.md, etc.)
├── codebase/         # Brownfield analysis (ARCHITECTURE.md, etc.)
├── todos/            # Captured ideas for later
└── phases/
    └── XX-name/
        ├── XX-01-PLAN.md
        ├── XX-01-SUMMARY.md
        ├── XX-02-PLAN.md
        └── ...
```
</user_project_files>

<core_workflow>
1. `/gsd:new-project` → Questions → PROJECT.md
2. `/gsd:research-project` (optional) → .planning/research/
3. `/gsd:define-requirements` → REQUIREMENTS.md
4. `/gsd:create-roadmap` → ROADMAP.md + STATE.md
5. `/gsd:plan-phase N` → Creates PLAN.md files
6. `/gsd:execute-phase N` → Subagents execute plans, create SUMMARY.md
</core_workflow>

<task_types>
```xml
<task type="auto">           <!-- Claude executes autonomously -->
<task type="checkpoint:human-verify">  <!-- Human confirms visual/UX -->
<task type="checkpoint:decision">      <!-- Human makes choice -->
<task type="checkpoint:human-action">  <!-- Truly unavoidable manual (rare) -->
```
</task_types>

<plan_anatomy>
```yaml
---
phase: XX-name
plan: NN
type: execute
wave: N           # Execution wave (pre-computed)
depends_on: []    # Prior plans this requires
files_modified: []
autonomous: true  # false if has checkpoints
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
</plan_anatomy>

<wave_execution>
`/gsd:execute-phase` groups plans by `wave` number:
- Wave 1: Independent plans run in parallel
- Wave 2: Plans depending on wave 1 run after
- Plans within each wave run simultaneously as subagents
</wave_execution>

<deviation_rules>
Executor handles unplanned discoveries automatically:
- **Rule 1:** Auto-fix bugs (no permission needed)
- **Rule 2:** Auto-add missing critical functionality (security, validation)
- **Rule 3:** Auto-fix blocking issues (missing deps, wrong types)
- **Rule 4:** Ask about architectural changes (stop, return checkpoint)
</deviation_rules>

<file_conventions>
| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `execute-phase.md` |
| Commands | `gsd:kebab-case` | `/gsd:execute-phase` |
| XML tags | kebab-case | `<execution_context>` |
| Step names | snake_case | `name="load_project_state"` |
| Bash vars | CAPS_UNDERSCORES | `PHASE_ARG` |
</file_conventions>

<anti_patterns>
**Banned:**
- Enterprise patterns (sprints, story points, stakeholders)
- Human dev time estimates (hours/days/weeks)
- Vague tasks ("Add authentication", "Handle edge cases")
- Temporal language in docs ("We changed X to Y" — describe current state only)
- Generic XML tags (`<section>`, `<item>` — use semantic tags)
</anti_patterns>

</essential_knowledge>

<codebase_paths>
Key locations (relative to repo root):

| Type | Path |
|------|------|
| Commands | `commands/gsd/` |
| Agents | `agents/` |
| Workflows | `get-shit-done/workflows/` |
| Templates | `get-shit-done/templates/` |
| References | `get-shit-done/references/` |
| Contributor guide | `CLAUDE.md` |
</codebase_paths>

<workflows_index>
All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| diagnose.md | Systematically investigate why something isn't working |
| plan-change.md | Design a modification or extension to GSD |
</workflows_index>

<reference_index>
All in `references/`:

| Reference | Purpose |
|-----------|---------|
| concepts.md | Deep dive on plans as prompts, checkpoints, deviation rules, wave execution, state management, SUMMARY system, atomic commits, TDD |
| architecture.md | System architecture and component relationships |
| execution-model.md | How plan execution works in detail |
| verification-deep.md | Goal-backward verification patterns |
| scope-estimation.md | How to estimate plan scope and context usage |
</reference_index>

<success_criteria>
A good GSD meta conversation:
- Answers questions without needing codebase exploration
- Uses precise GSD terminology (phases, plans, waves, checkpoints)
- References specific files when relevant
- Maintains GSD's philosophy (no enterprise patterns, Claude automates)
- Suggests concrete file paths for changes
</success_criteria>
