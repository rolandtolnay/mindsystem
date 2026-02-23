---
name: ms:execute-phase
description: Execute all plans in a phase with wave-based parallelization
argument-hint: "<phase-number>"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash
  - Task
  - TodoWrite
  - AskUserQuestion
---

<objective>
Execute all plans in a phase using wave-based parallel execution.

Orchestrator stays lean: discover plans, read execution order, spawn subagents in waves, collect results. Each subagent loads the full execute-plan context and handles its own plan.

Context budget: ~15% orchestrator, 100% fresh per subagent.
</objective>

<execution_context>
@~/.claude/mindsystem/references/principles.md
@~/.claude/mindsystem/workflows/execute-phase.md
</execution_context>

<context>
Phase: $ARGUMENTS

**Normalize phase number:**
```bash
PHASE_ARG="$ARGUMENTS"
PHASE=$(printf "%02d" "$PHASE_ARG" 2>/dev/null || echo "$PHASE_ARG")
```

@.planning/ROADMAP.md
@.planning/STATE.md
</context>

<process>
1. **Validate phase exists**
   - Find phase directory matching argument
   - Count PLAN.md files
   - Error if no plans found

2. **Discover plans**
   - List all *-PLAN.md files in phase directory
   - Check which have *-SUMMARY.md (already complete)
   - Verify EXECUTION-ORDER.md exists
   - Build list of incomplete plans

3. **Validate and read execution order**
   - Run `validate-execution-order.sh` on phase directory
   - Parse EXECUTION-ORDER.md wave structure
   - Report wave structure to user

4. **Execute waves**
   For each wave in order:
   - Spawn `ms-executor` for each plan in wave (parallel Task calls)
   - Wait for completion (Task blocks)
   - Verify SUMMARYs created
   - Run `update-state.sh` to update plan progress
   - Proceed to next wave

5. **Aggregate results**
   - Collect summaries from all plans
   - Report phase completion status

6. **Verify phase goal**
   - Spawn `ms-verifier` subagent with phase directory and goal
   - Verifier checks Must-Haves against actual codebase (not SUMMARY claims)
   - Creates VERIFICATION.md with detailed report
   - Route by status:
     - `passed` → continue to step 7
     - `human_needed` → present items, get approval or feedback
     - `gaps_found` → present gaps, offer `/ms:plan-phase {X} --gaps`

7. **Code review (optional)**
   - Read `code_review.phase` from config.json (default: `ms-code-simplifier`)
   - If `"skip"`: proceed to step 8
   - Spawn code review agent with phase file scope
   - If changes made: commit as `refactor({phase}): code review improvements`

8. **Generate phase patch**
   - Run: `~/.claude/mindsystem/scripts/generate-phase-patch.sh ${PHASE_NUMBER}`
   - Outputs to `.planning/phases/{phase_dir}/{phase}-changes.patch`
   - Verify: patch file exists OR skip message logged
   - Note: Patch captures all changes including simplifications

9. **Consolidate knowledge**
   - Spawn `ms-consolidator` with phase directory and number
   - Consolidator reads phase artifacts and existing knowledge files
   - Produces updated `.planning/knowledge/{subsystem}.md` files
   - Deletes PLAN.md files (execution instructions consumed)
   - Verify: knowledge files written to `.planning/knowledge/`

10. **Update roadmap and state**
    - Update ROADMAP.md, STATE.md

11. **Update requirements**
    Mark phase requirements as Complete:
    - Read ROADMAP.md, find this phase's `Requirements:` line (e.g., "AUTH-01, AUTH-02")
    - Read REQUIREMENTS.md traceability table
    - For each REQ-ID in this phase: change Status from "Pending" to "Complete"
    - Write updated REQUIREMENTS.md
    - Skip if: REQUIREMENTS.md doesn't exist, or phase has no Requirements line

12. **Commit phase completion**
    Bundle all phase metadata updates in one commit:
    - Stage: `git add .planning/ROADMAP.md .planning/STATE.md`
    - Stage knowledge files: `git add .planning/knowledge/*.md`
    - Stage PLAN.md deletions: `git add -u .planning/phases/{phase_dir}/*-PLAN.md`
    - Stage REQUIREMENTS.md if updated: `git add .planning/REQUIREMENTS.md`
    - Commit: `docs({phase}): complete {phase-name} phase`

13. **Offer next steps**
    - Route to next action (see `<offer_next>`)

14. **Update last command**
    - Update `.planning/STATE.md` Last Command field
    - Format: `Last Command: ms:execute-phase $ARGUMENTS | YYYY-MM-DD HH:MM`
</process>

<offer_next>
**MANDATORY: Present copy/paste-ready next command.**

After verification completes:

**First, surface user actions from all SUMMARYs:**

Extract `## User Actions Required` sections from all `*-SUMMARY.md` files in the phase directory. If any contain actions (not "None"), present before route-specific content:

```
## ⚠ Action Required

{Consolidated list from all SUMMARYs — deduplicate if overlapping}
```

Then route based on status:

| Status | Route |
|--------|-------|
| `gaps_found` | Route C (gap closure) |
| `human_needed` | Present checklist, then re-route based on approval |
| `passed` + more phases | Route A (next phase) |
| `passed` + last phase | Route B (milestone complete) |

---

**Route A: Phase verified, more phases remain**

1. Show phase completion summary:
```
## ✓ Phase {Z}: {Name} Complete

All {Y} plans finished. Phase goal verified.
```

2. Read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions to present the "Next Up" section with pre-work context for Phase {Z+1}.

3. After the "Next Up" section, add:
```
**Also available:**
- `/ms:verify-work {Z}` — manual acceptance testing before continuing
```

---

**Route B: Phase verified, milestone complete**

Show phase completion summary, then read `~/.claude/mindsystem/references/routing/milestone-complete-routing.md` and follow its instructions to present the milestone complete section.

---

**Route C: Gaps found — need additional planning**

Read `~/.claude/mindsystem/references/routing/gap-closure-routing.md` and follow its instructions to present the gap closure section.
</offer_next>

<wave_execution>
**Parallel spawning:**

Spawn all plans in a wave with a single message containing multiple Task calls:

```
Task(prompt="Execute plan at {plan_01_path}\n\nPlan: @{plan_01_path}\nProject state: @.planning/STATE.md", subagent_type="ms-executor")
Task(prompt="Execute plan at {plan_02_path}\n\nPlan: @{plan_02_path}\nProject state: @.planning/STATE.md", subagent_type="ms-executor")
Task(prompt="Execute plan at {plan_03_path}\n\nPlan: @{plan_03_path}\nProject state: @.planning/STATE.md", subagent_type="ms-executor")
```

All three run in parallel. Task tool blocks until all complete.

**No polling.** No background agents. No TaskOutput loops.
</wave_execution>

<deviation_rules>
During execution, handle discoveries automatically:

1. **Auto-fix bugs** - Fix immediately, document in Summary
2. **Auto-add critical** - Security/correctness gaps, add and document
3. **Auto-fix blockers** - Can't proceed without fix, do it and document
4. **Ask about architectural** - Major structural changes, stop and ask user

Only rule 4 requires user intervention.
</deviation_rules>

<commit_rules>
**Per-Task Commits:**

After each task completes:
1. Stage only files modified by that task
2. Commit with format: `{type}({phase}-{plan}): {task-name}`
3. Types: feat, fix, test, refactor, perf, chore
4. Record commit hash for SUMMARY.md

**Plan Metadata Commit:**

After all tasks in a plan complete:
1. Stage plan artifacts only: PLAN.md, SUMMARY.md
2. Commit with format: `docs({phase}-{plan}): complete [plan-name] plan`
3. NO code files (already committed per-task)

**Simplification Commit (if changes made):**

After code simplification step:
1. Stage only simplified files
2. Commit with format: `refactor({phase}): simplify phase code`
3. Include simplifier agent name and file count in commit body

**Phase Completion Commit:**

After all plans in phase complete:
1. Stage: ROADMAP.md, STATE.md, REQUIREMENTS.md (if updated), VERIFICATION.md
2. Stage knowledge files: `git add .planning/knowledge/*.md`
3. Stage PLAN.md deletions: `git add -u .planning/phases/{phase_dir}/*-PLAN.md`
4. Commit with format: `docs({phase}): complete {phase-name} phase`
5. Bundles all phase-level state updates in one commit

**NEVER use:**
- `git add .`
- `git add -A`
- `git add src/` or any broad directory

**Always stage files individually.**
</commit_rules>

<success_criteria>
- [ ] All incomplete plans in phase executed
- [ ] Code review completed (or skipped if config says "skip")
- [ ] Phase goal verified (Must-Haves checked against codebase)
- [ ] VERIFICATION.md created in phase directory
- [ ] Patch file generated OR explicitly skipped with message
- [ ] Knowledge files written to .planning/knowledge/ (consolidation complete)
- [ ] PLAN.md files deleted from phase directory
- [ ] STATE.md and ROADMAP.md reflect phase completion
- [ ] REQUIREMENTS.md updated (phase requirements marked Complete)
</success_criteria>
