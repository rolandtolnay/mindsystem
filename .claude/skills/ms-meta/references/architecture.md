<architecture>

<overview>
GSD's architecture follows a **progressive disclosure** pattern: commands delegate to workflows, workflows use templates and references. Each layer has a specific purpose.
</overview>

<directory_structure>
```
gsd/                              # Development repository
├── agents/                       # Subagent definitions
│   ├── gsd-executor.md              # Executes PLAN.md (core)
│   ├── gsd-verifier.md              # Verifies phase goals
│   ├── gsd-planner.md               # Creates PLAN.md files
│   ├── gsd-debugger.md              # Systematic debugging
│   ├── gsd-researcher.md            # Domain research
│   ├── gsd-research-synthesizer.md  # Combines research outputs
│   ├── gsd-roadmapper.md            # Creates ROADMAP.md
│   ├── gsd-codebase-mapper.md       # Analyzes existing codebases
│   ├── gsd-plan-checker.md          # Validates plans before execution
│   ├── gsd-milestone-auditor.md     # Audits milestone completion
│   └── gsd-integration-checker.md   # Verifies cross-phase integration
│
├── commands/gsd/                 # Slash commands
│   ├── new-project.md               # /gsd:new-project
│   ├── define-requirements.md       # /gsd:define-requirements
│   ├── create-roadmap.md            # /gsd:create-roadmap
│   ├── plan-phase.md                # /gsd:plan-phase
│   ├── execute-phase.md             # /gsd:execute-phase
│   ├── progress.md                  # /gsd:progress
│   ├── verify-work.md               # /gsd:verify-work
│   ├── debug.md                     # /gsd:debug
│   ├── help.md                      # /gsd:help
│   └── ... (20+ commands)
│
├── get-shit-done/                # Core system files
│   ├── workflows/                   # Step-by-step procedures
│   │   ├── execute-phase.md            # Orchestrates wave execution
│   │   ├── execute-plan.md             # Single plan execution
│   │   ├── plan-phase.md               # Creates plans from roadmap
│   │   ├── discovery-phase.md          # Gathers project context
│   │   ├── define-requirements.md      # Requirements workflow
│   │   ├── research-project.md         # Domain research
│   │   ├── research-phase.md           # Phase-specific research
│   │   ├── verify-phase.md             # Verification protocol
│   │   ├── complete-milestone.md       # Archive and prep next
│   │   ├── debug.md                    # Debugging workflow
│   │   └── ...
│   │
│   ├── templates/                   # Output structures
│   │   ├── project.md                  # PROJECT.md template
│   │   ├── requirements.md             # REQUIREMENTS.md template
│   │   ├── roadmap.md                  # ROADMAP.md template
│   │   ├── state.md                    # STATE.md template
│   │   ├── summary.md                  # SUMMARY.md template
│   │   ├── verification-report.md      # VERIFICATION.md template
│   │   ├── context.md                  # CONTEXT.md template
│   │   ├── phase-prompt.md             # Subagent prompt template
│   │   ├── codebase/                   # Brownfield analysis templates
│   │   │   ├── architecture.md
│   │   │   ├── stack.md
│   │   │   └── ...
│   │   └── research-project/           # Research output templates
│   │       ├── STACK.md
│   │       ├── FEATURES.md
│   │       └── ...
│   │
│   └── references/                  # Deep knowledge
│       ├── principles.md               # Core philosophy
│       ├── plan-format.md              # PLAN.md structure
│       ├── checkpoints.md              # Checkpoint types
│       ├── tdd.md                      # TDD plan format
│       ├── verification-patterns.md    # How to verify
│       ├── git-integration.md          # Commit conventions
│       ├── scope-estimation.md         # Task sizing
│       ├── goal-backward.md            # Verification philosophy
│       └── debugging/                  # Debugging references
│           ├── debugging-mindset.md
│           ├── hypothesis-testing.md
│           └── ...
│
├── scripts/                      # Shell scripts
│   └── generate-phase-patch.sh      # Creates diff patches
│
├── bin/                          # Installer
│   └── install.js                   # npx entry point
│
└── CLAUDE.md                     # Development instructions
```
</directory_structure>

<layer_purposes>
## Command Layer (`commands/gsd/*.md`)

**Purpose:** User interface. Thin wrappers that delegate to workflows.

**Structure:**
```yaml
---
name: gsd:command-name
description: One-line description
argument-hint: "<required>" or "[optional]"
allowed-tools: [Read, Write, Bash, Glob, Grep, AskUserQuestion]
---
```

**Key commands by category:**

| Category | Commands |
|----------|----------|
| Setup | `new-project`, `research-project`, `define-requirements`, `create-roadmap`, `map-codebase` |
| Execution | `plan-phase`, `execute-phase`, `progress` |
| Verification | `check-phase`, `verify-work`, `audit-milestone` |
| Milestones | `complete-milestone`, `discuss-milestone`, `new-milestone`, `plan-milestone-gaps` |
| Phase mgmt | `add-phase`, `insert-phase`, `remove-phase`, `discuss-phase`, `research-phase` |
| Session | `pause-work`, `resume-work` |
| Utilities | `add-todo`, `check-todos`, `debug`, `help`, `update`, `whats-new` |

## Workflow Layer (`get-shit-done/workflows/*.md`)

**Purpose:** Detailed procedures. Contains the actual logic.

**Key workflows:**

| Workflow | Spawns | Creates |
|----------|--------|---------|
| `execute-phase.md` | gsd-executor (parallel per plan), gsd-verifier | SUMMARY.md, VERIFICATION.md |
| `execute-plan.md` | None (runs in executor) | SUMMARY.md, commits |
| `plan-phase.md` | gsd-planner | PLAN.md files |
| `discovery-phase.md` | None | PROJECT.md |
| `define-requirements.md` | None | REQUIREMENTS.md |
| `research-project.md` | gsd-researcher (×4 parallel) | .planning/research/ |
| `map-codebase.md` | gsd-codebase-mapper (×4 parallel) | .planning/codebase/ |

## Template Layer (`get-shit-done/templates/*.md`)

**Purpose:** Define output structures. Claude copies and fills these.

**Key templates:**

| Template | Creates | When |
|----------|---------|------|
| `project.md` | PROJECT.md | After discovery |
| `requirements.md` | REQUIREMENTS.md | After define-requirements |
| `roadmap.md` | ROADMAP.md | After create-roadmap |
| `state.md` | STATE.md | With roadmap, updated constantly |
| `summary.md` | *-SUMMARY.md | After each plan execution |
| `verification-report.md` | *-VERIFICATION.md | After phase verification |

## Reference Layer (`get-shit-done/references/*.md`)

**Purpose:** Deep knowledge. Loaded when specific expertise needed.

**Key references:**

| Reference | Knowledge |
|-----------|-----------|
| `principles.md` | Core philosophy (solo dev, no enterprise) |
| `plan-format.md` | Complete PLAN.md specification |
| `checkpoints.md` | Checkpoint types and protocols |
| `tdd.md` | TDD plan structure |
| `scope-estimation.md` | How to size plans (2-3 tasks max) |
| `goal-backward.md` | Verification philosophy |

## Agent Layer (`agents/*.md`)

**Purpose:** Subagent definitions. Spawned via Task tool.

**Agent anatomy:**
```yaml
---
name: gsd-agent-name
description: What it does, when spawned
tools: Read, Write, Edit, Bash, Grep, Glob
color: yellow  # Terminal output color
---
```

**Key agents:**

| Agent | Spawned by | Purpose |
|-------|------------|---------|
| `gsd-executor` | execute-phase | Execute single PLAN.md |
| `gsd-verifier` | execute-phase | Verify phase goal achieved |
| `gsd-planner` | plan-phase | Create PLAN.md |
| `gsd-debugger` | debug | Systematic debugging |
| `gsd-researcher` | research-project/phase | Domain research |
| `gsd-codebase-mapper` | map-codebase | Analyze existing code |
</layer_purposes>

<data_flow>
## User Project Data Flow

```
/gsd:new-project
    ↓
  discovery-phase.md workflow
    ↓
  Creates: .planning/PROJECT.md
    ↓
/gsd:research-project (optional)
    ↓
  Spawns: 4× gsd-researcher (parallel)
    ↓
  Creates: .planning/research/{STACK,FEATURES,ARCHITECTURE,PITFALLS,SUMMARY}.md
    ↓
/gsd:define-requirements
    ↓
  define-requirements.md workflow
    ↓
  Creates: .planning/REQUIREMENTS.md
    ↓
/gsd:create-roadmap
    ↓
  Spawns: gsd-roadmapper
    ↓
  Creates: .planning/ROADMAP.md, .planning/STATE.md
    ↓
/gsd:plan-phase N
    ↓
  plan-phase.md workflow
    ↓
  Spawns: gsd-planner
    ↓
  Creates: .planning/phases/XX-name/XX-NN-PLAN.md
    ↓
/gsd:execute-phase N
    ↓
  execute-phase.md workflow (orchestrator)
    ↓
  Spawns: gsd-executor (parallel per wave)
    ↓
  Each executor:
    - Reads PLAN.md
    - Executes tasks
    - Commits per task
    - Creates SUMMARY.md
    - Updates STATE.md
    ↓
  Orchestrator:
    - Groups by wave
    - Handles checkpoints
    - Aggregates results
    ↓
  Spawns: gsd-verifier
    ↓
  Creates: XX-VERIFICATION.md
    ↓
  Updates: ROADMAP.md (marks complete)
```
</data_flow>

<file_locations>
## Where to Find Things

**Adding a new command:** `commands/gsd/new-command.md`

**Modifying execution logic:** `get-shit-done/workflows/execute-phase.md` or `execute-plan.md`

**Changing plan structure:** `get-shit-done/references/plan-format.md` and `templates/phase-prompt.md`

**Modifying an agent:** `agents/gsd-{agent-name}.md`

**Changing checkpoint behavior:** `get-shit-done/references/checkpoints.md`

**Updating templates:** `get-shit-done/templates/*.md`

**Core philosophy:** `get-shit-done/references/principles.md` and `CLAUDE.md`
</file_locations>

</architecture>
