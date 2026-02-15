<purpose>
Execute all plans in a phase using wave-based parallel execution. Orchestrator stays lean by delegating plan execution to subagents.
</purpose>

<core_principle>
The orchestrator's job is coordination, not execution. Each subagent loads the full execute-plan context itself. Orchestrator discovers plans, reads execution order from EXECUTION-ORDER.md, spawns agents in waves, collects results.
</core_principle>

<required_reading>
Read STATE.md before any operation to load project context.
</required_reading>

<process>

<step name="load_project_state" priority="first">
Before any operation, read project state:

```bash
cat .planning/STATE.md 2>/dev/null
```

**If file exists:** Parse and internalize:
- Current position (phase, plan, status)
- Accumulated decisions (constraints on this execution)
- Blockers/concerns (things to watch for)

**If file missing but .planning/ exists:**
```
STATE.md missing but planning artifacts exist.
Options:
1. Reconstruct from existing artifacts
2. Continue without project state (may lose accumulated context)
```

**If .planning/ doesn't exist:** Error - project not initialized.
</step>

<step name="validate_phase">
Confirm phase exists and has plans:

```bash
PHASE_DIR=$(ls -d .planning/phases/${PHASE_ARG}* 2>/dev/null | head -1)
if [ -z "$PHASE_DIR" ]; then
  echo "ERROR: No phase directory matching '${PHASE_ARG}'"
  exit 1
fi

PLAN_COUNT=$(ls -1 "$PHASE_DIR"/*-PLAN.md 2>/dev/null | wc -l | tr -d ' ')
if [ "$PLAN_COUNT" -eq 0 ]; then
  echo "ERROR: No plans found in $PHASE_DIR"
  exit 1
fi
```

Report: "Found {N} plans in {phase_dir}"
</step>

<step name="discover_plans">
List all plans and check completion:

```bash
# Get all plans
ls -1 "$PHASE_DIR"/*-PLAN.md 2>/dev/null | sort

# Get completed plans (have SUMMARY.md)
ls -1 "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null | sort

# Verify EXECUTION-ORDER.md exists
ls "$PHASE_DIR"/EXECUTION-ORDER.md
```

Build plan inventory:
- Plan path
- Plan ID (e.g., "03-01")
- Completion status (SUMMARY exists = complete)

Skip completed plans. If all complete, report "Phase already executed" and exit.
</step>

<step name="validate_execution_order">
Run validation before launching executors:

```bash
~/.claude/mindsystem/scripts/validate-execution-order.sh "$PHASE_DIR"
```

If validation fails (exit 1), stop execution and report the mismatch to user.
If validation passes, proceed with wave execution.
</step>

<step name="read_execution_order">
Read EXECUTION-ORDER.md and parse wave structure:

Parse `## Wave N` headers with `- {phase}-XX-PLAN.md` items under each. Build wave groups:

```
waves = {
  1: [plan-01, plan-02],
  2: [plan-03, plan-04],
  3: [plan-05]
}
```

Filter out completed plans (those with existing SUMMARY.md).

**Wave assignments come from EXECUTION-ORDER.md**, produced during `/ms:plan-phase`.

Report wave structure with context:
```
## Execution Plan

**Phase {X}: {Name}** — {total_plans} plans across {wave_count} waves

| Wave | Plans | What it builds |
|------|-------|----------------|
| 1 | 01-01, 01-02 | {from plan objectives} |
| 2 | 01-03 | {from plan objectives} |
| 3 | 01-04 | {from plan objectives} |

```

The "What it builds" column comes from skimming plan names/objectives. Keep it brief (3-8 words).
</step>

<step name="execute_waves">
Execute each wave in sequence. Autonomous plans within a wave run in parallel.

**For each wave:**

1. **Describe what's being built (BEFORE spawning):**

   Read each plan's `## Context` section. Extract what's being built and why it matters.

   **Output:**
   ```
   ---

   ## Wave {N}

   **{Plan ID}: {Plan Name}**
   {2-3 sentences: what this builds, key technical approach, why it matters in context}

   **{Plan ID}: {Plan Name}** (if parallel)
   {same format}

   Spawning {count} agent(s)...

   ---
   ```

   **Examples:**
   - Bad: "Executing terrain generation plan"
   - Good: "Procedural terrain generator using Perlin noise — creates height maps, biome zones, and collision meshes. Required before vehicle physics can interact with ground."

2. **Spawn executor agents:**

   Pass paths only — executors read files themselves with their fresh 200k context.
   This keeps orchestrator context lean (~10-15%).

   ```
   Task(
     subagent_type="ms-executor",
     prompt="Execute plan at {plan_path}\n\nPlan: @{plan_path}\nProject state: @.planning/STATE.md"
   )
   ```

2. **Wait for all agents in wave to complete:**

   Task tool blocks until each agent finishes. All parallel agents return together.

3. **Report completion and what was built:**

   For each completed agent:
   - Verify SUMMARY.md exists at expected path
   - Read SUMMARY.md to extract what was built
   - Note any issues or deviations

   **Output:**
   ```
   ---

   ## Wave {N} Complete

   **{Plan ID}: {Plan Name}**
   {What was built — from SUMMARY.md deliverables}
   {Notable deviations or discoveries, if any}

   **{Plan ID}: {Plan Name}** (if parallel)
   {same format}

   {If more waves: brief note on what this enables for next wave}

   ---
   ```

   **Examples:**
   - Bad: "Wave 2 complete. Proceeding to Wave 3."
   - Good: "Terrain system complete — 3 biome types, height-based texturing, physics collision meshes. Vehicle physics (Wave 3) can now reference ground surfaces."

4. **Update state:**

   After reporting wave completion, update STATE.md with progress:
   ```bash
   ~/.claude/mindsystem/scripts/update-state.sh {completed_count} {total_count}
   ```

5. **Handle failures:**

   If any agent in wave fails:
   - Report which plan failed and why
   - Ask user: "Continue with remaining waves?" or "Stop execution?"
   - If continue: proceed to next wave (dependent plans may also fail)
   - If stop: exit with partial completion report

6. **Proceed to next wave**

</step>

<step name="aggregate_results">
After all waves complete, aggregate results:

```markdown
## Phase {X}: {Name} Execution Complete

**Waves executed:** {N}
**Plans completed:** {M} of {total}

### Wave Summary

| Wave | Plans | Status |
|------|-------|--------|
| 1 | plan-01, plan-02 | ✓ Complete |
| CP | plan-03 | ✓ Verified |
| 2 | plan-04 | ✓ Complete |
| 3 | plan-05 | ✓ Complete |

### Plan Details

1. **03-01**: [one-liner from SUMMARY.md]
2. **03-02**: [one-liner from SUMMARY.md]
...

### Issues Encountered
[Aggregate from all SUMMARYs, or "None"]
```
</step>

<step name="code_review">
Read code review agent name from config:

```bash
CODE_REVIEW=$(cat .planning/config.json 2>/dev/null | jq -r '.code_review.phase // empty')
```

**If CODE_REVIEW = "skip":**
Report: "Code review skipped (config: skip)"
Proceed to verify_phase_goal.

**If CODE_REVIEW = empty/null:**
Use default: `CODE_REVIEW="ms-code-simplifier"`

**Otherwise:**
Use CODE_REVIEW value directly as agent name.

1. **Gather changed files:**
   ```bash
   # Get all files changed in this phase's commits
   PHASE_COMMITS=$(git log --oneline --grep="(${PHASE_NUMBER}-" --format="%H")
   CHANGED_FILES=$(git diff --name-only $(echo "$PHASE_COMMITS" | tail -1)^..HEAD | grep -E '\.(dart|ts|tsx|js|jsx|swift|kt|py|go|rs)$')
   ```

2. **Spawn code review agent (from config):**
   ```
   Task(
     prompt="
     <objective>
     Review code modified in phase {phase_number}.
     Preserve all functionality. Improve clarity and consistency.
     </objective>

     <scope>
     Files to analyze:
     {CHANGED_FILES}
     </scope>

     <output>
     After review and simplifications, run static analysis and tests.
     Report what was improved and verification results.
     </output>
     ",
     subagent_type="{CODE_REVIEW}"
   )
   ```

3. **Handle result:**
   - If changes made: Stage and commit
   - If no changes: Report "No improvements needed"

4. **Commit review changes (if any):**
   ```bash
   git add [modified files]
   git commit -m "$(cat <<'EOF'
   refactor({phase}): code review improvements

   Reviewer: {agent_type}
   Files reviewed: {count}
   EOF
   )"
   ```

Report: "Code review complete. Proceeding to verification."
</step>

<step name="verify_phase_goal">
Verify phase achieved its GOAL, not just completed its TASKS.

**Spawn verifier:**

```
Task(
  prompt="Verify phase {phase_number} goal achievement.

Phase directory: {phase_dir}
Phase goal: {goal from ROADMAP.md}

Check Must-Haves against actual codebase. Create VERIFICATION.md.
Verify what actually exists in the code.",
  subagent_type="ms-verifier"
)
```

**Read verification status:**

```bash
grep "^status:" "$PHASE_DIR"/*-VERIFICATION.md | cut -d: -f2 | tr -d ' '
```

**Route by status:**

| Status | Action |
|--------|--------|
| `passed` | Continue to update_roadmap |
| `human_needed` | Present items to user, get approval or feedback |
| `gaps_found` | Present gap summary, offer `/ms:plan-phase {phase} --gaps` |

**If passed:**

Phase goal verified. Proceed to update_roadmap.

**If human_needed:**

```markdown
## ✓ Phase {X}: {Name} — Human Verification Required

All automated checks passed. {N} items need human testing:

### Human Verification Checklist

{Extract from VERIFICATION.md human_verification section}

---

**After testing:**
- "approved" → continue to update_roadmap
- Report issues → will route to gap closure planning
```

If user approves → continue to update_roadmap.
If user reports issues → treat as gaps_found.

**If gaps_found:**

Present gaps and offer next command:

```markdown
## ⚠ Phase {X}: {Name} — Gaps Found

**Score:** {N}/{M} must-haves verified
**Report:** {phase_dir}/{phase}-VERIFICATION.md

### What's Missing

{Extract gap summaries from VERIFICATION.md gaps section}

---

## ▶ Next Up

`/ms:plan-phase {X} --gaps` — create additional plans to complete the phase

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `cat {phase_dir}/{phase}-VERIFICATION.md` — see full report
- `/ms:verify-work {X}` — manual testing before planning
```

User runs `/ms:plan-phase {X} --gaps` which:
1. Reads VERIFICATION.md gaps
2. Creates additional plans (04, 05, etc.) to close gaps
3. User then runs `/ms:execute-phase {X}` again
4. Execute-phase runs incomplete plans (04-05)
5. Verifier runs again after new plans complete

User stays in control at each decision point.
</step>

<step name="generate_phase_patch">
Generate a patch file with all implementation changes from this phase.

**Run the patch generation script:**
```bash
~/.claude/mindsystem/scripts/generate-phase-patch.sh ${PHASE_NUMBER}
```

The script will:
- Find all commits matching `({PHASE_NUMBER}-` pattern
- Generate diff from base commit to HEAD
- Exclude: `.planning`, generated files (Flutter, Next.js, TypeScript), build artifacts
- Output to `.planning/phases/{phase_dir}/{PHASE_NUMBER}-changes.patch`
- Skip with message if no phase commits or no implementation changes

**Verify patch generation completed:**
```bash
# Check for either: patch file exists OR skip was logged
PATCH_FILE=$(ls "$PHASE_DIR"/${PHASE_NUMBER}-changes.patch 2>/dev/null)
if [ -n "$PATCH_FILE" ]; then
  echo "✓ Patch generated: $PATCH_FILE"
else
  echo "✓ Patch skipped (no implementation changes)"
fi
```

**Note:** Patch is NOT committed — left for manual review. User can:
- Review: `cat .planning/phases/{phase_dir}/{phase}-changes.patch`
- Apply elsewhere: `git apply {patch_file}`
- Discard: `rm {patch_file}`
</step>

<step name="consolidate_knowledge">
Consolidate phase knowledge into per-subsystem knowledge files.

**Spawn ms-consolidator:**

```
Task(
  prompt="Consolidate knowledge from phase {phase_number}.
  Phase directory: {phase_dir}
  Phase number: {phase_number}
  Read SUMMARY.md files for affected subsystems, then read phase artifacts
  and existing knowledge files. Produce updated knowledge files and delete
  PLAN.md files.",
  subagent_type="ms-consolidator"
)
```

**Verify consolidation:**

```bash
ls .planning/knowledge/*.md 2>/dev/null
```

Report the consolidation summary returned by ms-consolidator.

**Handle failure:** If consolidation fails, ask user:
- "Continue without consolidation" → proceed to update_roadmap
- "Stop execution" → exit with partial completion report

Knowledge consolidation is not a blocking gate — phase execution succeeded regardless.
</step>

<step name="update_roadmap">
Update ROADMAP.md to reflect phase completion:

```bash
# Mark phase complete
# Update completion date
# Update status
```

Commit phase completion (roadmap, state, verification):
```bash
git add .planning/ROADMAP.md .planning/STATE.md .planning/phases/{phase_dir}/*-VERIFICATION.md .planning/phases/{phase_dir}/*-SUMMARY.md
git add .planning/knowledge/*.md
git add -u .planning/phases/{phase_dir}/*-PLAN.md
git add .planning/REQUIREMENTS.md  # if updated
git commit -m "docs(phase-{X}): complete phase execution"
```
</step>

<step name="update_codebase_map">
**If `.planning/codebase/` exists:**

Check what changed during this phase:

```bash
# Get all source changes from this phase's commits
PHASE_COMMITS=$(git log --oneline --grep="({phase_number}-" --format="%H" | head -20)
if [ -n "$PHASE_COMMITS" ]; then
  FIRST=$(echo "$PHASE_COMMITS" | tail -1)
  git diff --name-only ${FIRST}^..HEAD 2>/dev/null | grep -v "^\.planning/"
fi
```

**Update only if structural changes occurred:**

| Change Detected | Update Action |
|-----------------|---------------|
| New directory in src/ | STRUCTURE.md: Add to directory layout |
| package.json deps changed | STACK.md: Add/remove from dependencies list |
| New file pattern (e.g., first .test.ts) | CONVENTIONS.md: Note new pattern |
| New external API client | INTEGRATIONS.md: Add service entry |
| Config file added/changed | STACK.md: Update configuration section |

**Skip update if only:** Code changes within existing files, bug fixes, content changes.

Make single targeted edits — add a bullet, update a path, remove a stale entry.

```bash
git add .planning/codebase/*.md
git commit -m "docs: update codebase map after phase {X}"
```
</step>

<step name="offer_next">
Present next steps based on milestone status.

**If more phases remain:**

Read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions to present "Next Up" with pre-work context for the next phase.

After the "Next Up" section, add:
```markdown
**Also available:**
- `/ms:verify-work {Z}` — manual acceptance testing before continuing
```

**If milestone complete:**

Read `~/.claude/mindsystem/references/routing/milestone-complete-routing.md` and follow its instructions to present the milestone complete section.
</step>

</process>

<context_efficiency>
**Why this works:**

Orchestrator context usage: ~10-15%
- Read EXECUTION-ORDER.md (one small file)
- Parse wave structure
- Spawn Task calls
- Collect results

Each subagent: Fresh 200k context
- Loads full execute-plan workflow
- Loads templates, references
- Executes plan with full capacity
- Creates SUMMARY (orchestrator commits)

**No polling.** Task tool blocks until completion. No TaskOutput loops.

**No context bleed.** Orchestrator never reads workflow internals. Just paths and results.
</context_efficiency>

<failure_handling>
**Subagent fails mid-plan:**
- SUMMARY.md won't exist
- Orchestrator detects missing SUMMARY
- Reports failure, asks user how to proceed

**Dependency chain breaks:**
- Wave 1 plan fails
- Wave 2 plans depending on it will likely fail
- Orchestrator can still attempt them (user choice)
- Or skip dependent plans entirely

**All agents in wave fail:**
- Something systemic (git issues, permissions, etc.)
- Stop execution
- Report for manual investigation

</failure_handling>

<resumption>
**Resuming interrupted execution:**

If phase execution was interrupted (context limit, user exit, error):

1. Run `/ms:execute-phase {phase}` again
2. discover_plans finds completed SUMMARYs
3. Skips completed plans
4. Resumes from first incomplete plan
5. Continues wave-based execution

**STATE.md tracks:**
- Last completed plan
- Completed plans (via SUMMARY.md existence)
</resumption>
