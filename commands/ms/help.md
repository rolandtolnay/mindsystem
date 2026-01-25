---
name: ms:help
description: Show available Mindsystem commands and usage guide
---

<objective>
Display the complete Mindsystem command reference.

Output ONLY the reference content below. Do NOT add:

- Project-specific analysis
- Git status or file context
- Next-step suggestions
- Any commentary beyond the reference
  </objective>

<reference>
# Mindsystem Command Reference

**Mindsystem** creates hierarchical project plans optimized for solo agentic development with Claude Code.

## Start Here

- If you already have `.planning/` in this repo: run `/ms:progress`.
- If you’re starting in an existing codebase (brownfield): run `/ms:map-codebase`, then `/ms:new-project`.
- Otherwise: run `/ms:new-project`.

## Quick Start

### Greenfield (new project)

1. `/ms:new-project` - Initialize project with brief
2. `/ms:research-project` - (optional) Research domain ecosystem
3. `/ms:define-requirements` - Scope v1/v2/out of scope
4. `/ms:create-roadmap` - Create roadmap and phases
5. `/ms:plan-phase 1` - Create detailed plan for first phase
6. `/ms:execute-phase 1` - Execute with parallel agents

### Brownfield (existing codebase)

1. `/ms:map-codebase` - Analyze existing code first
2. `/ms:new-project` - Questions focus on what you’re adding/changing
3. Continue with steps 2-6 above (codebase docs load automatically)

## Staying Updated

Mindsystem evolves fast. Check for updates periodically:

```
/ms:whats-new
```

Shows what changed since your installed version. Update with:

```bash
npx mindsystem-cc@latest
```

Or inside Claude Code:

```
/ms:update
```

## Core Workflow

```
Initialize → (Optional Research) → Requirements → Roadmap → Plan → Execute → Verify → Milestone
```

Common deviations:
- Existing repo: `/ms:map-codebase` before `/ms:new-project`
- Plan looks wrong: `/ms:list-phase-assumptions <phase>` or `/ms:check-phase <phase>`
- Unknown domain: `/ms:research-project` or `/ms:research-phase <phase>`
- UI-heavy phase: `/ms:design-phase <phase>` before `/ms:research-phase <phase>`
- Execution gaps: `/ms:plan-phase <phase> --gaps` then `/ms:execute-phase <phase>`
- New urgent work: `/ms:insert-phase <after> "<desc>"`
- New non-urgent work: `/ms:add-todo "<desc>"`

### Project Initialization

**`/ms:new-project`**
Initialize new project with brief and configuration.

- Use when: you want Mindsystem to set up `.planning/` and capture intent (new repo, or an existing repo where you're adding/changing work).
- Creates `.planning/PROJECT.md` (vision and requirements)
- Creates `.planning/config.json` (workflow settings)
- Commits initialization files to git

Usage: `/ms:new-project`

**`/ms:research-project`**
Research domain ecosystem before creating roadmap.

- Use when: you’re unsure about stack choices, common pitfalls, or “what good looks like” in this domain.
- Spawns parallel agents to investigate stack, features, architecture, pitfalls
- Creates `.planning/research/` with ecosystem knowledge
- Recommended for best results; skip only if you need speed over thoroughness

Usage: `/ms:research-project`

**`/ms:define-requirements`**
Define what "done" looks like with checkable requirements.

- Use when: you’re ready to lock v1 scope (and explicitly defer v2/out-of-scope).
- Scopes features as v1, v2, or out of scope
- Works with or without prior research
- Creates `.planning/REQUIREMENTS.md` with traceability

Usage: `/ms:define-requirements`

**`/ms:create-roadmap`**
Create roadmap and state tracking for initialized project.

- Use when: requirements are defined and you want phases mapped to them.
- Creates `.planning/ROADMAP.md` (phase breakdown)
- Creates `.planning/STATE.md` (project memory)
- Creates `.planning/phases/` directories

Usage: `/ms:create-roadmap`

**`/ms:map-codebase`**
Map an existing codebase for brownfield projects.

- Use when: you’re working in an existing repo and want Mindsystem to follow existing patterns (where files live, conventions, testing).
- Analyzes codebase with parallel Explore agents
- Creates `.planning/codebase/` with 7 focused documents
- Covers stack, architecture, structure, conventions, testing, integrations, concerns
- Use before `/ms:new-project` on existing codebases

Usage: `/ms:map-codebase`

### Phase Planning

**`/ms:discuss-phase <number>`**
Help articulate your vision for a phase before planning.

- Captures how you imagine this phase working
- Creates CONTEXT.md with your vision, essentials, and boundaries
- Use when you have ideas about how something should look/feel

Usage: `/ms:discuss-phase 2`

**`/ms:design-phase <number>`**
Create visual/UX design specifications for UI-heavy phases.

- Produces DESIGN.md with layouts, components, flows, verification criteria
- Applies quality-forcing patterns to prevent generic AI output
- Checks for existing implement-ui skill and harmonizes with codebase
- Use for phases with significant UI work, novel components, or cross-platform design

Usage: `/ms:design-phase 3`

**`/ms:review-design [scope]`**
Audit and improve design of already-implemented features.

- Reviews existing code against design quality criteria
- Creates retroactive DESIGN.md if none exists
- Presents improvements with benefits and trade-offs
- Applies user-approved changes, runs verification
- Use for features implemented before GSD, or periodic design audits

Usage: `/ms:review-design 4` (review phase 4)
Usage: `/ms:review-design lib/features/home/home_screen.dart`
Usage: `/ms:review-design authentication` (review feature area)

**`/ms:research-phase <number>`**
Comprehensive ecosystem research for niche/complex domains.

- Discovers standard stack, architecture patterns, pitfalls
- Creates RESEARCH.md with "how experts build this" knowledge
- Use for 3D, games, audio, shaders, ML, and other specialized domains
- Goes beyond "which library" to ecosystem knowledge

Usage: `/ms:research-phase 3`

**`/ms:list-phase-assumptions <number>`**
See what Claude is planning to do before it starts.

- Shows Claude's intended approach for a phase
- Lets you course-correct if Claude misunderstood your vision
- No files created - conversational output only

Usage: `/ms:list-phase-assumptions 3`

**`/ms:plan-phase [number] [--gaps]`**
Create detailed execution plan for a specific phase.

- Use when: you’re about to start a phase, or you need additional plans (including verifier-driven gap closure via `--gaps`).
- Generates `.planning/phases/XX-phase-name/XX-YY-PLAN.md`
- Breaks phase into concrete, actionable tasks
- Includes verification criteria and success measures
- Multiple plans per phase supported (XX-01, XX-02, etc.)

Usage: `/ms:plan-phase 1`
Usage: `/ms:plan-phase` (auto-detect next unplanned phase)
Result: Creates `.planning/phases/01-foundation/01-01-PLAN.md`

### Execution

**`/ms:execute-phase <phase-number>`**
Execute all unexecuted plans in a phase with wave-based parallelization.

- Use when: the phase has PLAN.md files and you want Mindsystem to run them (including verification and possible gap-closure loop).
- Spawns parallel agents for independent plans
- Handles checkpoints with user interaction
- Resumes automatically from interrupted execution
- Creates SUMMARY.md for each completed plan
- Respects max_concurrent_agents from config.json

Usage: `/ms:execute-phase 5`

Options (via `.planning/config.json` parallelization section):
- `max_concurrent_agents`: Limit parallel agents (default: 3)
- `skip_checkpoints`: Skip human checkpoints in background (default: true)
- `min_plans_for_parallel`: Minimum plans to trigger parallelization (default: 2)

### Verification

**`/ms:check-phase <number>`**
Verify phase plans before execution (optional quality gate).

- Use when: the phase is complex or risky and you want a “will this actually achieve the goal?” sanity check before executing.
- Spawns plan checker agent to analyze PLAN.md files
- Checks requirement coverage, task completeness, dependencies
- Use for complex phases before committing to execution

Usage: `/ms:check-phase 5`

**`/ms:verify-work [number]`**
User acceptance testing of phase or plan.

- Use when: you want manual confirmation from a user/workflow perspective before continuing to the next phase or milestone.
- Conversational UAT with persistent state
- Verifies features work as expected from user perspective
- Use after execution to validate before continuing

Usage: `/ms:verify-work 5`

**`/ms:audit-milestone [version]`**
Audit milestone completion against original intent.

- Use when: you think you’re “done” and want cross-phase integration + requirements coverage checked before archiving.
- Reads phase VERIFICATION.md files and aggregates results
- Spawns integration checker for cross-phase wiring
- Creates MILESTONE-AUDIT.md with gaps and tech debt

Usage: `/ms:audit-milestone 1.0.0`

### Roadmap Management

**`/ms:add-phase <description>`**
Add new phase to end of current milestone.

- Use when: you discovered additional work that belongs after the currently planned phases (not an urgent insertion).
- Appends to ROADMAP.md
- Uses next sequential number
- Updates phase directory structure

Usage: `/ms:add-phase "Add admin dashboard"`

**`/ms:insert-phase <after> <description>`**
Insert urgent work as decimal phase between existing phases.

- Use when: you discovered work that must happen before the next integer phase, but you don’t want to renumber the roadmap.
- Creates intermediate phase (e.g., 7.1 between 7 and 8)
- Useful for discovered work that must happen mid-milestone
- Maintains phase ordering

Usage: `/ms:insert-phase 7 "Fix critical auth bug"`
Result: Creates Phase 7.1

**`/ms:remove-phase <number>`**
Remove a future phase and renumber subsequent phases.

- Use when: you’re cutting future scope and want to keep a clean contiguous roadmap (only works on unstarted phases).
- Deletes phase directory and all references
- Renumbers all subsequent phases to close the gap
- Only works on future (unstarted) phases
- Git commit preserves historical record

Usage: `/ms:remove-phase 17`
Result: Phase 17 deleted, phases 18-20 become 17-19

### Milestone Management

**`/ms:discuss-milestone`**
Figure out what you want to build in the next milestone.

- Reviews what shipped in previous milestone
- Helps you identify features to add, improve, or fix
- Routes to /ms:new-milestone when ready

Usage: `/ms:discuss-milestone`

**`/ms:new-milestone <name>`**
Create a new milestone with phases for an existing project.

- Adds milestone section to ROADMAP.md
- Creates phase directories
- Updates STATE.md for new milestone

Usage: `/ms:new-milestone "v2.0 Features"`

**`/ms:complete-milestone <version>`**
Archive completed milestone and prepare for next version.

- Creates MILESTONES.md entry with stats
- Archives full details to milestones/ directory
- Creates git tag for the release
- Prepares workspace for next version

Usage: `/ms:complete-milestone 1.0.0`

**`/ms:plan-milestone-gaps`**
Create phases to close gaps identified by milestone audit.

- Reads MILESTONE-AUDIT.md and groups gaps into logical phases
- Prioritizes by requirement importance (must/should/nice)
- Creates phase entries in ROADMAP.md automatically

Usage: `/ms:plan-milestone-gaps`

### Progress Tracking

**`/ms:progress`**
Check project status and intelligently route to next action.

- Use when: you’re unsure what to run next, returning after a break, or switching contexts.
- Shows visual progress bar and completion percentage
- Summarizes recent work from SUMMARY files
- Displays current position and what's next
- Lists key decisions and open issues
- Offers to execute next plan or create it if missing
- Detects 100% milestone completion

Usage: `/ms:progress`

### Debugging

**`/ms:debug [issue description]`**
Systematic debugging with persistent state across context resets.

- Use when: you have a bug/incident and want a structured investigation that survives `/clear`.
- Gathers symptoms through adaptive questioning
- Creates `.planning/debug/[slug].md` to track investigation
- Investigates using scientific method (evidence → hypothesis → test)
- Survives `/clear` — run `/ms:debug` with no args to resume
- Archives resolved issues to `.planning/debug/resolved/`

Usage: `/ms:debug "login button doesn't work"`
Usage: `/ms:debug` (resume active session)

### Todo Management

**`/ms:add-todo [description]`**
Capture idea or task as todo from current conversation.

- Use when: you discover work that’s real but not the right thing to do right now.
- Extracts context from conversation (or uses provided description)
- Creates structured todo file in `.planning/todos/pending/`
- Infers area from file paths for grouping
- Checks for duplicates before creating
- Updates STATE.md todo count

Usage: `/ms:add-todo` (infers from conversation)
Usage: `/ms:add-todo Add auth token refresh`

**`/ms:check-todos [area]`**
List pending todos and select one to work on.

- Use when: you want to pick up deferred work and route it into the right place (do now vs schedule vs plan into a phase).
- Lists all pending todos with title, area, age
- Optional area filter (e.g., `/ms:check-todos api`)
- Loads full context for selected todo
- Routes to appropriate action (work now, add to phase, brainstorm)
- Moves todo to done/ when work begins

Usage: `/ms:check-todos`
Usage: `/ms:check-todos api`

### Adhoc Work

**`/ms:do-work <description>`**
Execute small discovered work without phase overhead (max 2 tasks).

- Use when: you discover small work mid-session that needs to be done now but doesn't warrant a full phase.
- Bridges the gap between `/ms:add-todo` (capture for later) and `/ms:insert-phase` (full planning)
- Maximum 2 tasks — refuses and suggests `/ms:insert-phase` for larger work
- Creates lightweight artifacts in `.planning/adhoc/` for audit trail
- Updates STATE.md with adhoc work entry
- Single git commit with all changes

Usage: `/ms:do-work Fix auth token not refreshing on 401`

### Utility Commands

**`/ms:help`**
Show this command reference.

**`/ms:whats-new`**
See what's changed since your installed version.

- Shows installed vs latest version comparison
- Displays changelog entries for versions you've missed
- Highlights breaking changes
- Provides update instructions when behind

Usage: `/ms:whats-new`

**`/ms:update`**
Update Mindsystem to latest version with changelog display.

- Checks npm for latest version
- Runs update if behind
- Shows what changed between versions
- Better UX than raw `npx mindsystem-cc`

Usage: `/ms:update`

## Files & Structure

```
.planning/
├── PROJECT.md            # Project vision
├── REQUIREMENTS.md       # Scoped v1/v2 requirements
├── ROADMAP.md            # Current phase breakdown
├── STATE.md              # Project memory & context
├── config.json           # Workflow settings
├── research/             # Domain ecosystem research
├── todos/                # Captured ideas and tasks
│   ├── pending/          # Todos waiting to be worked on
│   └── done/             # Completed todos
├── adhoc/                # Small work executed via /ms:do-work
│   ├── *-PLAN.md         # Lightweight plans
│   └── *-SUMMARY.md      # Completion summaries
├── debug/                # Active debug sessions
│   └── resolved/         # Archived resolved issues
├── codebase/             # Codebase map (brownfield projects)
│   ├── STACK.md          # Languages, frameworks, dependencies
│   ├── ARCHITECTURE.md   # Patterns, layers, data flow
│   ├── STRUCTURE.md      # Directory layout, key files
│   ├── CONVENTIONS.md    # Coding standards, naming
│   ├── TESTING.md        # Test setup, patterns
│   ├── INTEGRATIONS.md   # External services, APIs
│   └── CONCERNS.md       # Tech debt, known issues
└── phases/
    ├── 01-foundation/
    │   ├── 01-CONTEXT.md      # Vision from discuss-phase
    │   ├── 01-DESIGN.md       # UI/UX specs from design-phase
    │   ├── 01-RESEARCH.md     # Technical research
    │   ├── 01-01-PLAN.md
    │   └── 01-01-SUMMARY.md
    └── 02-core-features/
        ├── 02-01-PLAN.md
        └── 02-01-SUMMARY.md
```

## Common Workflows

**Starting a new project (greenfield):**

```
/ms:new-project                 # Extract your idea through questions
/ms:research-project            # (recommended) Research domain ecosystem
/ms:define-requirements         # Scope v1/v2/out of scope
/ms:create-roadmap              # Create phases mapped to requirements
/ms:plan-phase 1                # Create detailed plan
/ms:execute-phase 1             # Execute with parallel agents
```

**Starting with existing code (brownfield):**

```
/ms:map-codebase                # Step 1: Analyze existing code
/ms:new-project                 # Step 2: Questions focus on what you're adding/changing
/ms:research-project            # (optional) Research new domain areas
/ms:define-requirements         # Scope what's changing
/ms:create-roadmap              # Create roadmap
/ms:plan-phase 1                # Codebase docs load automatically
/ms:execute-phase 1             # Claude knows your patterns & conventions
```

**Not sure what to do next / returning after a break:**

```
/ms:progress  # See where you left off and continue
```

**Plan → execute loop (with optional quality gates):**

```
/ms:plan-phase 5                 # Create one or more PLAN.md files
/ms:check-phase 5                # (optional) Sanity check: plans will achieve goal
/ms:execute-phase 5              # Execute; produces SUMMARY + VERIFICATION
# If gaps found during verification:
/ms:plan-phase 5 --gaps          # Create additional plans to close verifier gaps
/ms:execute-phase 5              # Re-run until phase verifies cleanly
```

**Found a bug:**

```
/ms:debug "form submission fails silently"    # Systematic investigation (persists across /clear)
# Then decide where the fix belongs:
# - If it's small (1-2 tasks) and needed now:
/ms:do-work "Fix auth token refresh on 401"   # Quick fix with audit trail
# - If it's required to satisfy the current phase goal: add more plans to the current phase
/ms:plan-phase 5                              # (or: /ms:plan-phase 5 --gaps after verification)
/ms:execute-phase 5
# - If it's urgent but should happen before the next phase (and not worth renumbering):
/ms:insert-phase 5 "Fix critical auth bug"     # Creates 05.1
/ms:plan-phase 5.1
/ms:execute-phase 5.1
# - If it can wait:
/ms:add-todo "Fix modal z-index"
```

**Need to adjust scope (new info, new requirements, or a cut):**

Common options:
- If the current phase goal can’t be met: add more plans to the current phase (`/ms:plan-phase <current>` or `/ms:plan-phase <current> --gaps`) then `/ms:execute-phase <current>`
- Add work later: `/ms:add-phase "…"`
- Insert urgent work before the next phase: `/ms:insert-phase <after> "…"`
- Cut future work: `/ms:remove-phase <phase>`
- Re-scope v1/v2/out-of-scope: `/ms:define-requirements` (choose Replace) → `/ms:create-roadmap` (choose Replace)

**Implementing a new feature after shipping (new milestone):**

```
/ms:discuss-milestone                 # Clarify what’s next (optional but helpful)
/ms:new-milestone "v1.1 New feature"  # Update PROJECT.md for the next milestone
/ms:research-project                  # (optional) Domain / stack research
/ms:define-requirements               # Re-scope v1/v2 for this milestone
/ms:create-roadmap                    # New phases mapped to requirements
/ms:plan-phase                        # Auto-detect next unplanned phase
/ms:execute-phase <phase>
```

**Completing a milestone:**

```
/ms:audit-milestone 1.0.0       # Verify before completing
/ms:complete-milestone 1.0.0    # Archive and tag
/ms:discuss-milestone           # Gather context for next
/ms:new-milestone "v1.1 Features"
```

**Closing gaps from audit:**

```
/ms:audit-milestone 1.0.0       # Finds gaps
/ms:plan-milestone-gaps         # Creates phases to fix them
/ms:plan-phase 6                # Plan first gap closure phase
/ms:execute-phase 6
/ms:audit-milestone 1.0.0       # Re-audit when done
```

**Capturing ideas during work:**

```
/ms:add-todo                    # Capture from conversation context
/ms:add-todo Fix modal z-index  # Capture with explicit description
/ms:check-todos                 # Review and work on todos
/ms:check-todos api             # Filter by area
```

## Getting Help

- Read `.planning/PROJECT.md` for project vision
- Read `.planning/STATE.md` for current context
- Check `.planning/ROADMAP.md` for phase status
- Run `/ms:progress` to check where you're up to
  </reference>
