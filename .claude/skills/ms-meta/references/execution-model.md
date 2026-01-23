<execution_model>

<overview>
Mindsystem uses wave-based parallel execution where the orchestrator stays lean while subagents execute with fresh context. This document explains the complete execution model.
</overview>

<orchestrator_role>
## Orchestrator Responsibilities

The orchestrator's job is **coordination, not execution**. It:
- Discovers plans in phase directory
- Groups plans by pre-computed wave number
- Spawns subagents (ms-executor) in parallel per wave
- Handles checkpoints between waves
- Collects results and updates state
- Runs verification after completion

**Context usage:** ~10-15% (minimal reads, logic, Task calls)

**Key principle:** Orchestrator never reads workflow internals. Just paths, frontmatter, and results.
</orchestrator_role>

<wave_computation>
## Wave Assignment (During Planning)

Wave numbers are pre-computed during `/ms:plan-phase`, not at execution time.

**Assignment rules:**
```
depends_on: []                    → Wave 1 (independent)
depends_on: ["03-01"]             → Wave after 03-01 completes
depends_on: ["03-01", "03-02"]    → Wave after BOTH complete
```

**File ownership:**
- `files_modified: [...]` declared in frontmatter
- No overlap → can run parallel
- If file appears in multiple plans → later plan waits

**Example frontmatter:**
```yaml
---
phase: 03-core-features
plan: 02
type: execute
wave: 1           # Pre-computed: no dependencies
depends_on: []
files_modified: [src/features/user/model.ts, src/features/user/api.ts]
autonomous: true  # No checkpoints
---
```
</wave_computation>

<parallel_execution>
## Parallel Execution Flow

```
execute-phase orchestrator
    │
    ├── Wave 1 (parallel) ─────────────────────────┐
    │   ├── Task(ms-executor) → plan-01           │
    │   ├── Task(ms-executor) → plan-02           │ All spawn simultaneously
    │   └── Task(ms-executor) → plan-03           │
    │       │                                      │
    │       └── [All agents block until complete] ─┘
    │
    ├── Wave 2 (parallel) ─────────────────────────┐
    │   ├── Task(ms-executor) → plan-04           │
    │   └── Task(ms-executor) → plan-05           │
    │       │                                      │
    │       └── [All agents block until complete] ─┘
    │
    └── verify_phase_goal
        └── Task(ms-verifier)
```

**Each subagent:**
- Gets fresh 200k context
- Loads full execute-plan workflow
- Loads relevant templates and references
- Executes with full capacity
- Creates SUMMARY.md, commits per task
- Returns result to orchestrator
</parallel_execution>

<subagent_prompt>
## Subagent Task Prompt

When spawning executors, orchestrator fills this template:

```xml
<objective>
Execute plan {plan_number} of phase {phase_number}-{phase_name}.

Commit each task atomically. Create SUMMARY.md. Update STATE.md.
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/execute-plan.md
@~/.claude/mindsystem/templates/summary.md
@~/.claude/mindsystem/references/checkpoints.md
@~/.claude/mindsystem/references/tdd.md
</execution_context>

<context>
Plan: @{plan_path}
Project state: @.planning/STATE.md
Config: @.planning/config.json (if exists)
</context>

<success_criteria>
- [ ] All tasks executed
- [ ] Each task committed individually
- [ ] SUMMARY.md created in plan directory
- [ ] STATE.md updated with position and decisions
</success_criteria>
```

**Key points:**
- Subagent loads its own context via @-references
- Orchestrator doesn't pass heavy content
- Each agent is self-contained
</subagent_prompt>

<checkpoint_in_parallel>
## Checkpoints in Parallel Context

Plans with `autonomous: false` have checkpoints requiring user interaction.

**Execution flow:**
1. Spawn agent as normal (even in parallel wave)
2. Agent runs until checkpoint
3. Agent returns with structured checkpoint state
4. Other parallel agents may complete while waiting
5. Orchestrator presents checkpoint to user
6. User responds
7. **Fresh agent** spawned with user response (NOT resume)
8. Continuation agent verifies prior commits exist
9. Agent continues from checkpoint
10. May hit more checkpoints (repeat)
11. Eventually completes

**Why fresh agent instead of resume:**
- Resume relies on serialization that breaks with parallel tool calls
- Fresh agents with explicit state are more reliable
- Continuation template captures all needed context
</checkpoint_in_parallel>

<checkpoint_return_format>
## Checkpoint Return Structure

When executor hits checkpoint, it returns structured state:

```markdown
## Checkpoint: {type}

### Completed Tasks
| # | Task | Commit | Files |
|---|------|--------|-------|
| 1 | Create user model | abc123f | src/models/user.ts |
| 2 | Add API endpoints | def456g | src/api/users.ts |

### Current Task
- **Number:** 3
- **Name:** Verify deployment
- **Status:** Blocked on checkpoint

### Checkpoint Details
{what-built / decision / action details}

### Awaiting
{resume-signal from plan}
```

Orchestrator extracts this and presents to user.
</checkpoint_return_format>

<continuation_prompt>
## Continuation Prompt Template

For continuing after checkpoint:

```xml
<objective>
Continue execution of plan {plan_number} from task {resume_task_number}.
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/execute-plan.md
@~/.claude/mindsystem/templates/summary.md
</execution_context>

<context>
Plan: @{plan_path}
State: @.planning/STATE.md
</context>

<completed_tasks>
{completed_tasks_table}
</completed_tasks>

<resume_from>
Task {resume_task_number}: {resume_task_name}
</resume_from>

<user_response>
{user_response}
</user_response>

<resume_instructions>
{based on checkpoint type:}
- human-verify: "User approved. Continue to next task."
- decision: "User selected {choice}. Implement accordingly."
- human-action: "User completed action. Verify and continue."
</resume_instructions>
```
</continuation_prompt>

<failure_handling>
## Failure Scenarios

**Subagent fails mid-plan:**
- SUMMARY.md won't exist
- Orchestrator detects missing SUMMARY
- Reports failure to user
- Options: retry, skip, abort

**Dependency chain breaks:**
- Wave 1 plan fails
- Wave 2 plans depending on it will likely fail
- Orchestrator can attempt them (user choice)
- Or skip dependent plans

**All agents in wave fail:**
- Systemic issue (git, permissions, etc.)
- Stop execution
- Report for investigation

**Checkpoint fails to resolve:**
- User can't approve or has repeated issues
- Options: "Skip plan?" or "Abort execution?"
- Partial progress recorded in STATE.md
</failure_handling>

<resumption>
## Resuming Interrupted Execution

If phase execution was interrupted:

1. Run `/ms:execute-phase {phase}` again
2. discover_plans finds completed SUMMARYs
3. Skips completed plans
4. Resumes from first incomplete plan
5. Continues wave-based execution

**STATE.md tracks:**
- Last completed plan
- Current wave
- Pending checkpoints
</resumption>

<verification_after_execution>
## Verification Phase

After all waves complete, orchestrator spawns ms-verifier:

```
Task(
  prompt="Verify phase {phase} goal achievement.

  Phase directory: {phase_dir}
  Phase goal: {goal from ROADMAP.md}

  Check must_haves against actual codebase. Create VERIFICATION.md.",
  subagent_type="ms-verifier"
)
```

**Verifier checks:**
- Must-have truths (observable behaviors)
- Required artifacts (files exist and are substantive)
- Key links (wiring between components)

**Status routing:**
| Status | Action |
|--------|--------|
| `passed` | Update roadmap, offer next phase |
| `human_needed` | Present items for human testing |
| `gaps_found` | Offer `/ms:plan-phase --gaps` |
</verification_after_execution>

<context_efficiency>
## Why This Model Works

**Orchestrator stays lean:**
- Reads frontmatter only (not full plans)
- Analyzes dependencies (logic, not heavy reads)
- Fills template strings
- Spawns Task calls
- Collects results

**Each subagent gets fresh context:**
- 200k tokens purely for implementation
- No accumulated context from previous plans
- Peak quality for every plan

**No polling:**
- Task tool blocks until completion
- No TaskOutput loops
- Synchronization is automatic

**No context bleed:**
- Orchestrator doesn't read workflow internals
- Just paths and results
- Clean separation of concerns
</context_efficiency>

<spawning_patterns>
## Agent Spawning Patterns

**Sequential:**
```
plan-phase → ms-planner → PLAN.md
```

**Parallel (same type):**
```
research-project → 4× ms-researcher (parallel)
                      ↓
                   ms-research-synthesizer
```

**Parallel (wave-based):**
```
execute-phase Wave 1 → ms-executor (plan-01)
                     → ms-executor (plan-02)
              Wave 2 → ms-executor (plan-03)
```

**Hierarchical:**
```
audit-milestone → ms-milestone-auditor
                    ↓
                  ms-verifier (per phase)
                  ms-integration-checker
```
</spawning_patterns>

</execution_model>
