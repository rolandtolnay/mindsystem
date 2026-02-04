---
name: ms-meta
description: Instant Mindsystem expert. Use when working on Mindsystem, asking how it works, or describing/discussing improvements to commands, agents, workflows, or the framework itself.
---

<objective>
Provides instant expertise about the Mindsystem framework for meta-discussions, diagnostics, and planning Mindsystem changes. Use when working on Mindsystem itself, diagnosing Mindsystem issues, or asking how Mindsystem works.
</objective>

<behavior>
**This is a domain knowledge skill, not a Q&A assistant.**

When invoked:
1. **Absorb** the essential knowledge below as context
2. **Continue** with your original task, informed by this Mindsystem expertise
3. **Do NOT** treat the invocation arguments as a question to answer

The arguments passed to this skill describe WHY you need Mindsystem knowledge. Use that context to apply the knowledge appropriately, but return to your primary task.

**Example:** If invoked during a CLI tool design task with "need to understand subagent patterns", absorb the subagent knowledge, then continue designing the CLI tool — don't write an essay about subagent patterns.
</behavior>

<essential_knowledge>

<what_mindsystem_is>
Mindsystem is a meta-prompting and context engineering system for Claude Code that solves **context rot** — the quality degradation that happens as Claude fills its context window.

**Core insight:** Claude's quality degrades predictably:
- 0-30% context: Peak quality
- 30-50%: Good quality
- 50-70%: Degrading ("I'll be more concise now" = cutting corners)
- 70%+: Poor quality

**The 50% rule:** Plans should complete within ~50% context usage. Stop BEFORE quality degrades, not at context limit.

**Solution:** Aggressive atomicity. Plans stay small (2-3 tasks max). Each plan executes in a fresh subagent with 200k tokens purely for implementation.
</what_mindsystem_is>

<philosophy>
**Solo developer + Claude workflow.** No enterprise patterns (sprint ceremonies, RACI matrices, stakeholder management). User is the visionary. Claude is the builder.

**Modularity over bundling.** Commands stay small, explicit, and composable. Avoid mega-flows. Users pick the depth they need (quick fix vs. new feature vs. UI-heavy system). Each command has a clear purpose — no consulting documentation to understand which to use.

**Main context for collaboration.** Planning, discussion, and back-and-forth happen with the user in the main conversation. Subagents are for autonomous execution, not for hiding key decisions or reasoning. This preserves conversational iteration, user ability to question and redirect, and visibility into Claude's thinking.

**Script + prompt hybrid.** Deterministic chores live in scripts (`scripts/`); language models do what they're good at: interpreting intent, making trade-offs, and writing code. Examples: patch generation extracted to shell scripts, file manipulation via dedicated tooling.

**User as collaborator.** Trust that users can contribute meaningfully. Maintain:
- **Control** — User decides when to proceed, what to skip
- **Granularity** — Separate commands for research, requirements, planning, execution
- **Transparency** — No hidden delegation or background orchestration

**Plans ARE prompts.** PLAN.md is not a document that gets transformed — it IS the executable prompt containing objective, context, tasks, and verification.

**Claude automates everything.** If it has CLI/API, Claude does it. Checkpoints are for verification (human confirms visual/UX) and decisions (human chooses direction), not manual work.

**Goal-backward planning.** Don't ask "what should we build?" — ask "what must be TRUE for the goal to be achieved?" This produces verifiable requirements, not vague task lists.
</philosophy>

<context_split>
Mindsystem deliberately separates where work happens:

**Main context (with user):**
- Project discovery (`/ms:new-project`)
- Requirements definition (`/ms:define-requirements`)
- Phase discussion (`/ms:discuss-phase`)
- Phase planning (`/ms:plan-phase`)
- Design decisions (`/ms:design-phase`)
- Verification review (`/ms:verify-work`)

**Fresh subagent contexts (autonomous):**
- Plan execution (`ms-executor`)
- Phase verification (`ms-verifier`)
- Research tasks (`ms-researcher`)
- Codebase mapping (`ms-codebase-mapper`)
- Debugging sessions (`ms-debugger`)

**Why this matters:**
- Collaboration benefits from user visibility and iteration
- Execution benefits from fresh context (200k tokens, peak quality)
- Planning stays editable; execution produces artifacts
</context_split>

<repository_structure>
```
mindsystem/
├── agents/               # Subagent definitions (Task tool configs)
│   ├── ms-executor.md       # Executes PLAN.md files
│   ├── ms-verifier.md       # Verifies phase goals achieved
│   ├── ms-debugger.md       # Systematic debugging
│   ├── ms-researcher.md     # Domain research
│   ├── ms-roadmapper.md     # Creates ROADMAP.md
│   ├── ms-designer.md       # UI/UX design specs
│   ├── ms-code-simplifier.md    # Post-execution code review (generic)
│   ├── ms-flutter-simplifier.md # Flutter-specific simplification
│   ├── ms-flutter-reviewer.md   # Flutter structural analysis (analyze-only)
│   ├── ms-codebase-mapper.md    # Brownfield codebase analysis
│   └── ...
├── commands/ms/         # Slash commands (/ms:*)
│   ├── new-project.md        # Initialize project
│   ├── plan-phase.md         # Create plans for phase
│   ├── execute-phase.md      # Execute all plans
│   ├── design-phase.md       # Generate UI/UX design spec
│   ├── verify-work.md        # UAT verification
│   ├── progress.md           # Where am I? What's next?
│   └── ...
├── mindsystem/          # Core system
│   ├── workflows/            # Step-by-step procedures
│   └── templates/            # Output structures (STATE.md, SUMMARY.md, etc.)
├── skills/               # Domain expertise skills
│   └── flutter-senior-review/   # Flutter code review principles
│       ├── SKILL.md             # Skill definition
│       ├── AGENTS.md            # Full compiled document for agents
│       └── principles/          # 12 principle files
└── scripts/              # Shell scripts for automation
    ├── generate-phase-patch.sh
    └── ms-lookup/            # Research tooling (Python)
```

**Installation:** `npx mindsystem-cc` copies to `~/.claude/` (global) or `.claude/` (local).
</repository_structure>

<user_project_files>
Mindsystem creates `.planning/` directory in user projects:

```
.planning/
├── PROJECT.md        # Vision, constraints, decisions
├── REQUIREMENTS.md   # Checkable requirements with traceability
├── ROADMAP.md        # Phases from start to finish
├── STATE.md          # Living memory (position, decisions, blockers)
├── config.json       # Execution preferences (see below)
├── research/         # Domain research (STACK.md, FEATURES.md, etc.)
├── codebase/         # Brownfield analysis (ARCHITECTURE.md, etc.)
├── todos/            # Captured ideas for later
└── phases/
    └── XX-name/
        ├── XX-01-PLAN.md
        ├── XX-01-SUMMARY.md
        ├── DESIGN.md          # If design-phase was run
        └── ...
```
</user_project_files>

<config_json>
`.planning/config.json` controls execution preferences:

```json
{
  "code_review": {
    "adhoc": "ms-flutter-simplifier",
    "phase": "ms-flutter-simplifier",
    "milestone": "ms-flutter-reviewer"
  }
}
```

**Code review levels:**
- `code_review.adhoc` — Runs after `/ms:do-work` (adhoc work review, falls back to `phase`)
- `code_review.phase` — Runs after `/ms:execute-phase` (per-phase review)
- `code_review.milestone` — Runs after `/ms:audit-milestone` (cross-phase review)

**Default values:**
- `adhoc` — Falls back to `phase` value, then `ms-code-simplifier`
- `phase` — `ms-code-simplifier`
- `milestone` — `ms-flutter-reviewer`

**Available values:**
- `"ms-flutter-simplifier"` — Flutter/Dart-specific reviewer (makes changes)
- `"ms-flutter-reviewer"` — Flutter structural analysis (analyze-only, reports findings)
- `"ms-code-simplifier"` — Generic code reviewer (makes changes)
- `"skip"` — Skip code review at this level

**Agent modes:**
- Default agents (simplifiers) make changes and commit
- Agents with `mode: analyze-only` in frontmatter report findings without modifying code
- For analyze-only reviewers at milestone level, user gets binary choice: create quality phase or accept as tech debt
</config_json>

<core_workflow>
1. `/ms:new-project` → Questions → PROJECT.md
2. `/ms:research-project` (optional) → .planning/research/
3. `/ms:define-requirements` → REQUIREMENTS.md
4. `/ms:create-roadmap` → ROADMAP.md + STATE.md
5. `/ms:discuss-phase N` (optional) → Gather context before planning
6. `/ms:design-phase N` (optional) → DESIGN.md for UI-heavy phases
7. `/ms:plan-phase N` → Creates PLAN.md files (main context, with user)
   - After planning: risk assessment (0-100 score) + optional verification via ms-plan-checker
   - Risk factors: task count, plan count, external services, CONTEXT.md, cross-cutting, new deps, complex domains
   - Skip `--gaps` mode skips risk assessment (gap closure plans don't need it)
8. `/ms:execute-phase N` → Subagents execute plans, create SUMMARY.md
9. `/ms:verify-work N` (optional) → UAT verification with inline fixing
</core_workflow>

<fork_features>
**Design phase.** `/ms:design-phase` generates a UI/UX spec (flows, components, wireframes) before implementation. Use for UI-heavy work.

**Automatic code review.** After phase execution (and optionally at milestone completion), a code review agent reviews code for clarity and maintainability. Stack-aware (Flutter gets specialized guidance via ms-flutter-simplifier) with generic fallback (ms-code-simplifier). Produces separate commit for easy review. Configure `code_review.phase` and `code_review.milestone` in config.json.

**Analyze-only reviewers.** Agents with `mode: analyze-only` (like ms-flutter-reviewer) report structural findings without modifying code. At milestone level, these offer binary choice: create quality phase or accept as tech debt.

**Skills distribution.** Bundled skills (like `flutter-senior-review`) provide domain-specific expertise. Installed to `~/.claude/skills/` and referenced by agents and workflows.

**Research tooling.** `scripts/ms-lookup/` provides standalone research capabilities. Can be used inside workflows or directly.

**Enhanced verification.** `/ms:verify-work` batches UAT items and can spawn subagents to investigate and fix issues found during manual testing.
</fork_features>

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
`/ms:execute-phase` groups plans by `wave` number:
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
| Commands | `ms:kebab-case` | `/ms:execute-phase` |
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
- Mega-flows that bundle unrelated commands
- Hidden delegation (subagents making key decisions without user visibility)
</anti_patterns>

</essential_knowledge>

<codebase_paths>
Key locations (relative to repo root):

| Type | Path |
|------|------|
| Commands | `commands/ms/` |
| Agents | `agents/` |
| Skills | `skills/` |
| Workflows | `mindsystem/workflows/` |
| Templates | `mindsystem/templates/` |
| Scripts | `scripts/` |
| Contributor guide | `CLAUDE.md` |
</codebase_paths>

<agents_index>
All in `agents/`:

| Agent | Purpose | Spawned by |
|-------|---------|------------|
| ms-executor | Execute single PLAN.md, commit per task | execute-phase |
| ms-verifier | Verify phase goal achievement | execute-phase |
| ms-debugger | Systematic debugging with persistent state | debug |
| ms-researcher | Domain research with citations | research-project, research-phase |
| ms-research-synthesizer | Combine parallel research outputs | research-project |
| ms-roadmapper | Create ROADMAP.md from requirements | create-roadmap |
| ms-designer | Create UI/UX design specifications | design-phase |
| ms-codebase-mapper | Analyze existing codebase structure | map-codebase |
| ms-code-simplifier | Post-execution code review (generic) | execute-phase |
| ms-flutter-simplifier | Post-execution code review (Flutter) | execute-phase |
| ms-flutter-reviewer | Flutter structural analysis (analyze-only) | audit-milestone |
| ms-plan-checker | Validate plans before execution | plan-phase (optional), check-phase |
| ms-milestone-auditor | Audit milestone completion | audit-milestone |
| ms-integration-checker | Verify cross-phase integration | audit-milestone |
| ms-mock-generator | Generate mocks for UAT testing | verify-work |
| ms-verify-fixer | Fix issues found during UAT | verify-work |
| ms-consolidator | Consolidate decisions during milestone completion | complete-milestone |
</agents_index>

<workflows_index>
Key workflows in `mindsystem/workflows/`:

| Workflow | Purpose |
|----------|---------|
| execute-phase.md | Orchestrate wave-based parallel plan execution |
| execute-plan.md | Execute single plan (runs in ms-executor) |
| plan-phase.md | Create PLAN.md files for a phase |
| verify-phase.md | Goal-backward verification protocol |
| verify-work.md | UAT verification with inline fixing |
| discovery-phase.md | Gather project context |
| define-requirements.md | Scope requirements with checkboxes |
| research-project.md | Domain research spawning |
| research-phase.md | Phase-specific research |
| map-codebase.md | Brownfield codebase analysis |
| debug.md | Systematic debugging workflow |
| complete-milestone.md | Archive and prep next milestone |
</workflows_index>

<reference_index>
Skill references in `.claude/skills/ms-meta/references/`:

| Reference | Purpose |
|-----------|---------|
| concepts.md | Plans as prompts, checkpoints, deviation rules, wave execution, state management, SUMMARY system, atomic commits, TDD |
| architecture.md | System architecture and component relationships |
| execution-model.md | How plan execution works in detail |
| verification-deep.md | Goal-backward verification patterns |
| scope-estimation.md | How to estimate plan scope and context usage |
</reference_index>

<success_criteria>
After loading this skill:
- Continue with the original task, now informed by Mindsystem expertise
- Apply Mindsystem principles and terminology naturally
- Reference specific Mindsystem files when relevant to the work
- Maintain Mindsystem's philosophy (modularity, main context collaboration, user as collaborator)
- Suggest concrete file paths when designing Mindsystem changes

**Do NOT:** Write a response "about" Mindsystem principles. Apply them to the work at hand.
</success_criteria>
