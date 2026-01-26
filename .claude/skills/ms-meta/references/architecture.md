<architecture>

<overview>
Mindsystem's architecture follows a **progressive disclosure** pattern: commands delegate to workflows, workflows use templates and references. Each layer has a specific purpose.
</overview>

<directory_structure>
```
mindsystem/                              # Development repository
├── agents/                       # Subagent definitions
│   ├── ms-executor.md              # Executes PLAN.md (core)
│   ├── ms-verifier.md              # Verifies phase goals
│   ├── ms-planner.md               # Creates PLAN.md files
│   ├── ms-debugger.md              # Systematic debugging
│   ├── ms-researcher.md            # Domain research
│   ├── ms-research-synthesizer.md  # Combines research outputs
│   ├── ms-roadmapper.md            # Creates ROADMAP.md
│   ├── ms-codebase-mapper.md       # Analyzes existing codebases
│   ├── ms-plan-checker.md          # Validates plans before execution
│   ├── ms-milestone-auditor.md     # Audits milestone completion
│   └── ms-integration-checker.md   # Verifies cross-phase integration
│
├── commands/ms/                 # Slash commands
│   ├── new-project.md               # /ms:new-project
│   ├── define-requirements.md       # /ms:define-requirements
│   ├── create-roadmap.md            # /ms:create-roadmap
│   ├── plan-phase.md                # /ms:plan-phase
│   ├── execute-phase.md             # /ms:execute-phase
│   ├── progress.md                  # /ms:progress
│   ├── verify-work.md               # /ms:verify-work
│   ├── debug.md                     # /ms:debug
│   ├── help.md                      # /ms:help
│   └── ... (20+ commands)
│
├── mindsystem/                # Core system files
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
## Command Layer (`commands/ms/*.md`)

**Purpose:** User interface. Thin wrappers that delegate to workflows.

**Structure:**
```yaml
---
name: ms:command-name
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
| Utilities | `add-todo`, `check-todos`, `debug`, `help`, `update`, `whats-new` |

## Workflow Layer (`mindsystem/workflows/*.md`)

**Purpose:** Detailed procedures. Contains the actual logic.

**Key workflows:**

| Workflow | Spawns | Creates |
|----------|--------|---------|
| `execute-phase.md` | ms-executor (parallel per plan), ms-verifier | SUMMARY.md, VERIFICATION.md |
| `execute-plan.md` | None (runs in executor) | SUMMARY.md, commits |
| `plan-phase.md` | ms-planner | PLAN.md files |
| `discovery-phase.md` | None | PROJECT.md |
| `define-requirements.md` | None | REQUIREMENTS.md |
| `research-project.md` | ms-researcher (×4 parallel) | .planning/research/ |
| `map-codebase.md` | ms-codebase-mapper (×4 parallel) | .planning/codebase/ |

## Template Layer (`mindsystem/templates/*.md`)

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

## Reference Layer (`mindsystem/references/*.md`)

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
name: ms-agent-name
description: What it does, when spawned
tools: Read, Write, Edit, Bash, Grep, Glob
color: yellow  # Terminal output color
---
```

**Key agents:**

| Agent | Spawned by | Purpose |
|-------|------------|---------|
| `ms-executor` | execute-phase | Execute single PLAN.md |
| `ms-verifier` | execute-phase | Verify phase goal achieved |
| `ms-planner` | plan-phase | Create PLAN.md |
| `ms-debugger` | debug | Systematic debugging |
| `ms-researcher` | research-project/phase | Domain research |
| `ms-codebase-mapper` | map-codebase | Analyze existing code |
</layer_purposes>

<data_flow>
## User Project Data Flow

```
/ms:new-project
    ↓
  discovery-phase.md workflow
    ↓
  Creates: .planning/PROJECT.md
    ↓
/ms:research-project (optional)
    ↓
  Spawns: 4× ms-researcher (parallel)
    ↓
  Creates: .planning/research/{STACK,FEATURES,ARCHITECTURE,PITFALLS,SUMMARY}.md
    ↓
/ms:define-requirements
    ↓
  define-requirements.md workflow
    ↓
  Creates: .planning/REQUIREMENTS.md
    ↓
/ms:create-roadmap
    ↓
  Spawns: ms-roadmapper
    ↓
  Creates: .planning/ROADMAP.md, .planning/STATE.md
    ↓
/ms:plan-phase N
    ↓
  plan-phase.md workflow
    ↓
  Spawns: ms-planner
    ↓
  Creates: .planning/phases/XX-name/XX-NN-PLAN.md
    ↓
/ms:execute-phase N
    ↓
  execute-phase.md workflow (orchestrator)
    ↓
  Spawns: ms-executor (parallel per wave)
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
  Spawns: ms-verifier
    ↓
  Creates: XX-VERIFICATION.md
    ↓
  Updates: ROADMAP.md (marks complete)
```
</data_flow>

<file_locations>
## Where to Find Things

**Adding a new command:** `commands/ms/new-command.md`

**Modifying execution logic:** `mindsystem/workflows/execute-phase.md` or `execute-plan.md`

**Changing plan structure:** `mindsystem/references/plan-format.md` and `templates/phase-prompt.md`

**Modifying an agent:** `agents/ms-{agent-name}.md`

**Changing checkpoint behavior:** `mindsystem/references/checkpoints.md`

**Updating templates:** `mindsystem/templates/*.md`

**Core philosophy:** `mindsystem/references/principles.md` and `CLAUDE.md`
</file_locations>

</architecture>
