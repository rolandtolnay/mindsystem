<architecture>

<overview>
Mindsystem's architecture follows a **progressive disclosure** pattern with a clear **context split**: commands delegate to workflows, workflows use templates, and execution happens in fresh subagent contexts while collaboration stays in the main context.
</overview>

<context_split>
## Where Work Happens

Mindsystem deliberately separates collaborative work from autonomous execution:

**Main Context (with user):**
| Activity | Command/Workflow |
|----------|-----------------|
| Project discovery | `/ms:new-project` |
| Requirements definition | `/ms:define-requirements` |
| Phase discussion | `/ms:discuss-phase` |
| Phase planning | `/ms:plan-phase` |
| Design decisions | `/ms:design-phase` |
| Verification review | `/ms:verify-work` |

**Fresh Subagent Contexts (autonomous):**
| Activity | Agent |
|----------|-------|
| Plan execution | ms-executor |
| Phase verification | ms-verifier |
| Research tasks | ms-researcher |
| Codebase mapping | ms-codebase-mapper |
| Debugging | ms-debugger |
| Code review | ms-code-simplifier |

**Why this matters:**
- Collaboration benefits from user visibility and iteration
- Execution benefits from fresh 200k-token context (peak quality)
- Planning stays editable; execution produces artifacts
</context_split>

<directory_structure>
```
mindsystem/                              # Development repository
├── agents/                       # Subagent definitions
│   ├── ms-executor.md              # Executes PLAN.md (core)
│   ├── ms-verifier.md              # Verifies phase goals
│   ├── ms-debugger.md              # Systematic debugging
│   ├── ms-researcher.md            # Domain research
│   ├── ms-research-synthesizer.md  # Combines research outputs
│   ├── ms-roadmapper.md            # Creates ROADMAP.md
│   ├── ms-designer.md              # UI/UX design specs
│   ├── ms-codebase-mapper.md       # Analyzes existing codebases
│   ├── ms-code-simplifier.md       # Post-execution code review (generic)
│   ├── ms-flutter-simplifier.md    # Post-execution code review (Flutter)
│   ├── ms-plan-checker.md          # Validates plans before execution
│   ├── ms-milestone-auditor.md     # Audits milestone completion
│   ├── ms-integration-checker.md   # Verifies cross-phase integration
│   ├── ms-mock-generator.md        # Generate mocks for UAT
│   ├── ms-verify-fixer.md          # Fix UAT issues
│   └── ms-consolidator.md          # Consolidate decisions
│
├── commands/ms/                 # Slash commands
│   ├── new-project.md               # /ms:new-project
│   ├── define-requirements.md       # /ms:define-requirements
│   ├── create-roadmap.md            # /ms:create-roadmap
│   ├── plan-phase.md                # /ms:plan-phase
│   ├── execute-phase.md             # /ms:execute-phase
│   ├── design-phase.md              # /ms:design-phase
│   ├── verify-work.md               # /ms:verify-work
│   ├── progress.md                  # /ms:progress
│   ├── debug.md                     # /ms:debug
│   ├── help.md                      # /ms:help
│   └── ... (25+ commands)
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
│   │   ├── verify-work.md              # UAT with inline fixing
│   │   ├── map-codebase.md             # Brownfield analysis
│   │   ├── complete-milestone.md       # Archive and prep next
│   │   ├── debug.md                    # Debugging workflow
│   │   └── ...
│   │
│   └── templates/                   # Output structures
│       ├── project.md                  # PROJECT.md template
│       ├── requirements.md             # REQUIREMENTS.md template
│       ├── roadmap.md                  # ROADMAP.md template
│       ├── state.md                    # STATE.md template
│       ├── summary.md                  # SUMMARY.md template
│       ├── verification-report.md      # VERIFICATION.md template
│       ├── design.md                   # DESIGN.md template
│       ├── context.md                  # CONTEXT.md template
│       ├── phase-prompt.md             # Subagent prompt template
│       ├── codebase/                   # Brownfield analysis templates
│       │   ├── architecture.md
│       │   ├── stack.md
│       │   ├── conventions.md
│       │   └── ...
│       └── research-project/           # Research output templates
│           ├── STACK.md
│           ├── FEATURES.md
│           └── ...
│
├── scripts/                      # Shell scripts
│   ├── generate-phase-patch.sh      # Creates diff patches
│   ├── generate-adhoc-patch.sh      # Creates adhoc patches
│   └── ms-lookup/                   # Research tooling (Python)
│       ├── ms_lookup/
│       └── pyproject.toml
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
| Planning | `discuss-phase`, `design-phase`, `plan-phase`, `check-phase` |
| Execution | `execute-phase`, `adhoc` |
| Verification | `verify-work`, `review-design` |
| Debugging | `debug` |
| Milestones | `complete-milestone`, `discuss-milestone`, `new-milestone`, `audit-milestone`, `plan-milestone-gaps` |
| Phase mgmt | `add-phase`, `insert-phase`, `remove-phase`, `research-phase`, `list-phase-assumptions` |
| Utilities | `add-todo`, `check-todos`, `progress`, `help`, `update`, `whats-new` |

## Workflow Layer (`mindsystem/workflows/*.md`)

**Purpose:** Detailed procedures. Contains the actual logic.

**Key workflows:**

| Workflow | Context | Creates |
|----------|---------|---------|
| `execute-phase.md` | Main (orchestrator) | Spawns ms-executor per plan, ms-verifier |
| `execute-plan.md` | Subagent (ms-executor) | SUMMARY.md, commits |
| `plan-phase.md` | Main | PLAN.md files |
| `discovery-phase.md` | Main | PROJECT.md |
| `define-requirements.md` | Main | REQUIREMENTS.md |
| `research-project.md` | Main (spawns) | .planning/research/ via 4× ms-researcher |
| `map-codebase.md` | Main (spawns) | .planning/codebase/ via 4× ms-codebase-mapper |
| `verify-work.md` | Main | UAT results, spawns ms-verify-fixer |

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
| `design.md` | DESIGN.md | After design-phase |

## Agent Layer (`agents/*.md`)

**Purpose:** Subagent definitions. Spawned via Task tool for autonomous work.

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
| `ms-debugger` | debug | Systematic debugging |
| `ms-researcher` | research-project/phase | Domain research |
| `ms-designer` | design-phase | Create UI/UX specs |
| `ms-codebase-mapper` | map-codebase | Analyze existing code |
| `ms-code-simplifier` | execute-phase, audit-milestone | Post-execution code review (generic) |
| `ms-flutter-simplifier` | execute-phase, audit-milestone | Post-execution code review (Flutter) |
| `ms-roadmapper` | create-roadmap | Generate roadmap from requirements |
</layer_purposes>

<data_flow>
## User Project Data Flow

```
/ms:new-project (main context)
    ↓
  discovery-phase.md workflow
    ↓
  Creates: .planning/PROJECT.md
    ↓
/ms:research-project (main context, spawns agents)
    ↓
  Spawns: 4× ms-researcher (parallel subagents)
    ↓
  Creates: .planning/research/{STACK,FEATURES,ARCHITECTURE,PITFALLS,SUMMARY}.md
    ↓
/ms:define-requirements (main context)
    ↓
  define-requirements.md workflow
    ↓
  Creates: .planning/REQUIREMENTS.md
    ↓
/ms:create-roadmap (main context, spawns agent)
    ↓
  Spawns: ms-roadmapper
    ↓
  Creates: .planning/ROADMAP.md, .planning/STATE.md
    ↓
/ms:plan-phase N (main context — collaboration)
    ↓
  plan-phase.md workflow (runs in main context)
    ↓
  Creates: .planning/phases/XX-name/XX-NN-PLAN.md
    ↓
/ms:execute-phase N (main context, spawns agents)
    ↓
  execute-phase.md workflow (orchestrator)
    ↓
  Spawns: ms-executor (parallel per wave)
    ↓
  Each executor (fresh subagent context):
    - Reads PLAN.md
    - Executes tasks
    - Commits per task
    - Creates SUMMARY.md
    - Updates STATE.md
    ↓
  (Optional) Spawns: ms-code-simplifier (code review)
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

**Modifying plan structure:** `mindsystem/templates/phase-prompt.md`

**Modifying an agent:** `agents/ms-{agent-name}.md`

**Updating templates:** `mindsystem/templates/*.md`

**Core philosophy:** `CLAUDE.md`

**Adding shell scripts:** `scripts/`
</file_locations>

</architecture>
