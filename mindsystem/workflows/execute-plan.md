<purpose>
Execute a plan prompt (PLAN.md) and create the outcome summary (SUMMARY.md).
</purpose>

<required_reading>
Read STATE.md before any operation to load project context.
</required_reading>

<process>

<step name="load_project_state" priority="first">
Read project state:

```bash
cat .planning/STATE.md 2>/dev/null
```

**If file exists:** Parse and internalize:
- Current position (phase, plan, status)
- Accumulated decisions (constraints on this execution)
- Blockers/concerns (things to watch for)

**If file missing but .planning/ exists:** Present options — reconstruct from artifacts or continue without state.

**If .planning/ doesn't exist:** Error — project not initialized.
</step>

<step name="load_plan">
Read the plan file provided in your prompt context.

Parse inline metadata from header: `**Subsystem:**` and `**Type:**` values.

Parse plan sections:
- Context (files to read, @-references)
- Changes (tasks with implementation details)
- Verification criteria
- Must-Haves checklist

**If plan references CONTEXT.md:** The CONTEXT.md file provides the user's vision for this phase — how they imagine it working, what's essential, and what's out of scope. Honor this context throughout execution.

**If plan references DESIGN.md:** The DESIGN.md provides visual/UX specifications — exact colors (hex), spacing (px), component states, and layouts. Use exact values from the spec, implement all component states, match wireframe layouts, include DESIGN.md verification criteria in task verification.

**If `**Type:** tdd`:** Read `~/.claude/mindsystem/references/tdd-execution.md` for RED-GREEN-REFACTOR execution flow.
</step>

<step name="execute">
Record start time: `PLAN_START_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ"); PLAN_START_EPOCH=$(date +%s)`

Execute each task in the plan. Deviations are normal — handle them using `<deviation_rules>` below.

For each task:
1. Read any @context files listed
2. Implement the task
3. **If CLI/API returns auth error (401, 403, "Not authenticated", "Please run X login"):** Use AskUserQuestion with exact auth steps and verification command. Wait, verify, resume. Document as normal flow, not deviation.
4. When you discover work not in plan: apply deviation rules automatically
5. Run task verification
6. Confirm done criteria met
7. Commit the task (see `<task_commit>`)
8. Track task completion and commit hash for summary

After all tasks:
- Run overall verification from plan's Verification section
- Confirm all Must-Haves met
</step>

<deviation_rules>

## Automatic Deviation Handling

**While executing tasks, you WILL discover work not in the plan.** Apply these rules automatically. Track all deviations for summary.

**RULE PRIORITY:**
1. If Rule 4 applies → STOP and ask user (architectural decision)
2. If Rules 1-3 apply → fix automatically, track for summary
3. If genuinely unsure → apply Rule 4 (stop and ask)

---

**RULE 1: Auto-fix bugs**

Trigger: Code doesn't work as intended (broken behavior, errors, crashes)

Action: Fix immediately, track for summary. No user permission needed.

Example: Logic error causing inverted condition — fix inline, add regression test, verify, track as `[Rule 1 - Bug]`.

---

**RULE 2: Auto-add missing critical functionality**

Trigger: Code missing essential features for correctness, security, or operation

Action: Add immediately, track for summary. No user permission needed.

Example: Auth middleware not checking token expiry — add exp validation, add test, track as `[Rule 2 - Missing Critical]`.

Boundary: "Add missing validation" = Rule 2. "Add new table" = Rule 4.

---

**RULE 3: Auto-fix blocking issues**

Trigger: Something prevents completing current task

Action: Fix to unblock, track for summary. No user permission needed.

Example: Missing dependency blocking import — install package, verify task proceeds, track as `[Rule 3 - Blocking]`.

---

**RULE 4: Ask about architectural changes**

Trigger: Fix/addition requires significant structural modification (new table, new service layer, framework switch, breaking API change)

Action: STOP. Present via AskUserQuestion: what found, proposed change, why, impact, alternatives. Wait for decision.

Example: Need to add new database table — STOP, present the architectural decision, wait for approval.

---

**Documentation format for summary:**

```markdown
## Deviations from Plan

### Auto-fixed Issues

**1. [Rule N - Category] Brief description**
- **Found during:** Task [N]
- **Issue:** [what was wrong]
- **Fix:** [what was done]
- **Files modified:** [files]
- **Commit:** [hash]
```

If no deviations: "None — plan executed exactly as written."

</deviation_rules>

<task_commit>

## Task Commit Protocol

After each task completes (verification passed, done criteria met), commit immediately.

**1. Stage only task-related files** (NEVER `git add .` or `git add -A`):

```bash
git status --short
git add src/specific/file.ts
```

**2. Determine commit type:**

| Type | When |
|------|------|
| `feat` | New feature, endpoint, component |
| `fix` | Bug fix, error correction |
| `test` | Test-only changes (TDD RED phase) |
| `refactor` | Code cleanup, no behavior change |
| `perf` | Performance improvement |
| `docs` | Documentation changes |
| `chore` | Config, tooling, dependencies |

**3. Commit with conventional format:**

```bash
git commit -m "$(cat <<'EOF'
{type}({phase}-{plan}): {concise task description}

- {key change 1}
- {key change 2}
EOF
)"
```

**4. Capture hash:**

```bash
TASK_COMMIT=$(git rev-parse --short HEAD)
```

Track commit hash for summary generation.

</task_commit>

<step name="verification_failure_gate">
If any task verification fails:

STOP. Do not continue to next task.

Present via AskUserQuestion:
- What failed (expected vs actual)
- Options: Retry, Skip (mark incomplete), Stop (investigate)

If user chose "Skip", note in summary under "Issues Encountered".
</step>

<step name="create_summary">
Record end time and calculate duration:

```bash
PLAN_END_TIME=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
PLAN_END_EPOCH=$(date +%s)
DURATION_SEC=$(( PLAN_END_EPOCH - PLAN_START_EPOCH ))
DURATION_MIN=$(( DURATION_SEC / 60 ))
```

Create `{phase}-{plan}-SUMMARY.md` in the plan's phase directory.

**Frontmatter fields — populate ALL:**

```yaml
---
phase: XX-name
plan: YY
subsystem: [from plan metadata or .planning/config.json subsystems]
tags: [searchable tech keywords: jwt, stripe, react, postgres]

requires:
  - phase: [prior phase this depends on]
    provides: [what that phase built that this uses]
provides:
  - [what this plan delivered]
affects: [phase names/keywords that will need this context]

tech-stack:
  added: [new libraries/tools from this plan]
  patterns: [architectural patterns established]

key-files:
  created: [important files created]
  modified: [important files modified]

key-decisions:
  - "Decision 1"
  - "Decision 2"

patterns-established:
  - "Pattern 1: description"

mock_hints:
  transient_states:
    - state: "[brief transient UI state description]"
      component: "[file path]"
      trigger: "[async call | animation | timer]"
  external_data:
    - source: "[API endpoint or data source]"
      data_type: "[what kind of data]"
      components: ["[file1]", "[file2]"]

duration: Xmin
completed: YYYY-MM-DD
---
```

**Subsystem:** Use inline `**Subsystem:**` metadata from plan header if present. Otherwise select from `jq -r '.subsystems[]' .planning/config.json`. If novel, append to config.json and log in decisions.

**Mock hints:** Reflect on what you built. If UI with transient states (loading, animations, async transitions) or external data dependencies, populate accordingly. If purely backend or no async UI, write `mock_hints: none  # reason`. Always populate.

**Body structure:**

```markdown
# Phase [X] Plan [Y]: [Name] Summary

**[Substantive one-liner — e.g., "JWT auth with refresh rotation using jose library"]**

## Performance
- **Duration:** [time]
- **Started:** [ISO timestamp]
- **Completed:** [ISO timestamp]
- **Tasks:** [count]
- **Files modified:** [count]

## Accomplishments
- [Most important outcome]
- [Second key accomplishment]

## Task Commits
1. **Task 1: [name]** - `hash` (type)
2. **Task 2: [name]** - `hash` (type)

## Files Created/Modified
- `path/file` - What it does

## Decisions Made
[Key decisions with rationale, or "None — followed plan as specified"]

## Deviations from Plan
[From deviation tracking, or "None — plan executed exactly as written."]

## Issues Encountered
[Problems during planned work, or "None"]

## Next Step
[Ready for next plan, or "Phase complete, ready for transition"]
```

**One-liner must be SUBSTANTIVE:**
- Good: "JWT auth with refresh rotation using jose library"
- Bad: "Authentication implemented"
</step>

<step name="return_to_orchestrator">
Do NOT commit the SUMMARY.md file. Do NOT update STATE.md or ROADMAP.md. The orchestrator handles all post-execution artifacts.

Return structured completion format:

```markdown
## PLAN COMPLETE

**Plan:** {phase}-{plan}
**Tasks:** {completed}/{total}
**Duration:** {duration}
**SUMMARY:** {path to SUMMARY.md}

**Commits:**
- {hash}: {message}
- {hash}: {message}

**Deviations:** {count} ({breakdown by rule, or "none"})
**Issues:** {count or "none"}
```
</step>

</process>

<success_criteria>
- All tasks from plan executed
- All verifications pass
- Each task committed individually with conventional format
- All deviations documented
- SUMMARY.md created with substantive content and ALL frontmatter fields
- Structured completion format returned to orchestrator
- No STATE.md updates (orchestrator responsibility)
- No ROADMAP.md updates (orchestrator responsibility)
- No SUMMARY commit (orchestrator responsibility)
</success_criteria>
