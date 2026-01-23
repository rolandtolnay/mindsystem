<purpose>
Validate built features through batched testing with mock support and inline fixing. Creates UAT.md that tracks test progress, supports mock generation for UI state testing, and fixes issues immediately while context is fresh.

Complete verify-and-fix session: by session end, everything verified, issues fixed, tests passing.
</purpose>

<execution_context>
@~/.claude/get-shit-done/workflows/generate-mocks.md
@~/.claude/get-shit-done/references/mock-patterns.md
</execution_context>

<template>
@~/.claude/get-shit-done/templates/UAT.md
</template>

<philosophy>
**Verify and fix in one session.**

Old flow: verify → log gaps → /clear → plan-phase --gaps → execute → verify again
New flow: verify → investigate → fix → re-test → continue

**Mocks enable testing unreachable states.**

Error displays, premium features, empty lists — all require specific backend conditions. Mocks let you toggle states and test immediately.

**Keep mocks and fixes separate.**

Mocks are uncommitted scaffolding. Fixes are clean commits. Git stash keeps them separated.

**Fix while context is hot.**

When you find an issue, you have the mock state active, the test fresh in mind, and the user ready to re-test. Fix it now, not later.
</philosophy>

<process>

<step name="check_dirty_tree" priority="first">
**Before anything else, check for uncommitted changes.**

```bash
git status --porcelain
```

**If output is non-empty (dirty tree):**

Present options via AskUserQuestion:
```
questions:
  - question: "You have uncommitted changes. How should I handle them before starting UAT?"
    header: "Git state"
    options:
      - label: "Stash changes"
        description: "git stash push -m 'pre-verify-work' — I'll restore them after UAT"
      - label: "Commit first"
        description: "Let me commit these changes before we start"
      - label: "Abort"
        description: "Cancel UAT, I'll handle my changes manually"
    multiSelect: false
```

**Handle response:**
- "Stash changes" → `git stash push -m "pre-verify-work"`, record `pre_work_stash: "pre-verify-work"` for later
- "Commit first" → Prompt user to commit, then continue
- "Abort" → Exit gracefully

**If clean tree:** Continue to next step.
</step>

<step name="check_active_session">
**Check for active UAT sessions:**

```bash
find .planning/phases -name "*-UAT.md" -type f 2>/dev/null | head -5
```

**If active sessions exist AND no $ARGUMENTS provided:**

Read each file's frontmatter (status, phase, current_batch) and present:

```
## Active UAT Sessions

| # | Phase | Status | Current Batch | Progress |
|---|-------|--------|---------------|----------|
| 1 | 04-comments | testing | 2 of 4 | 5/12 |
| 2 | 05-auth | testing | 1 of 3 | 0/8 |

Reply with a number to resume, or provide a phase number to start new.
```

Wait for user response.
- Number (1, 2) → Load that file, go to `resume_from_file`
- Phase number → Treat as new session

**If active sessions AND $ARGUMENTS provided:**
- Check if session exists for that phase
- If yes: offer to resume or restart
- If no: continue to `find_summaries`

**If no active sessions AND no $ARGUMENTS:**
```
No active UAT sessions.

Provide a phase number to start testing (e.g., /gsd:verify-work 4)
```

**If no active sessions AND $ARGUMENTS provided:** Continue to `find_summaries`
</step>

<step name="find_summaries">
**Find SUMMARY.md files for the phase:**

```bash
PHASE_DIR=$(ls -d .planning/phases/${PHASE_ARG}* 2>/dev/null | head -1)
ls "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null
```

Read each SUMMARY.md to extract testable deliverables.
</step>

<step name="extract_tests">
**Extract testable deliverables from SUMMARY.md files:**

Parse for:
1. **Accomplishments** — Features/functionality added
2. **User-facing changes** — UI, workflows, interactions

Focus on USER-OBSERVABLE outcomes, not implementation details.

For each deliverable, create test entry:
- name: Brief test name
- expected: Observable behavior (specific, what user should see)

**Examples:**
- Accomplishment: "Added comment threading with infinite nesting"
  → Test: "Reply to a Comment"
  → Expected: "Clicking Reply opens inline composer. Submitting shows reply nested under parent."

Skip internal/non-observable items (refactors, type changes, etc.).
</step>

<step name="classify_tests">
**Classify all tests by mock requirements:**

For each test, analyze the expected behavior to determine:
1. **mock_required**: Does this need special backend state?
2. **mock_type**: Freeform string describing needed state (e.g., "error_state", "premium_user", "empty_response")
3. **dependencies**: Other tests this depends on (infer from descriptions)

**Classification heuristics:**

| Expected behavior contains | Likely mock_type |
|---------------------------|------------------|
| "error", "fails", "invalid" | error_state |
| "premium", "pro", "paid", "subscription" | premium_user |
| "empty", "no results", "placeholder" | empty_response |
| "loading", "spinner", "skeleton" | loading_state |
| "offline", "no connection" | offline_state |
| Normal happy path | no mock needed |

**Dependency inference:**
- "Reply to comment" depends on "View comments"
- "Delete account" depends on "Login"
- Tests mentioning prior state depend on tests that create that state

Build classification list:
```yaml
tests:
  - name: "Login success"
    mock_required: false
    mock_type: null
    dependencies: []

  - name: "Login error message"
    mock_required: true
    mock_type: "error_state"
    dependencies: ["login_flow"]

  - name: "Premium badge display"
    mock_required: true
    mock_type: "premium_user"
    dependencies: ["login_flow"]
```
</step>

<step name="create_batches">
**Group tests into batches:**

**Rules:**
1. Group by mock_type (tests needing same mock state go together)
2. Respect dependencies (if B depends on A, A must be in same or earlier batch)
3. Max 4 tests per batch (AskUserQuestion limit)
4. No-mock tests first (run before any mock setup)
5. Order mock states logically: success → error → empty → loading

**Batch structure:**
```yaml
batches:
  - batch: 1
    name: "No Mocks Required"
    mock_type: null
    tests: [1, 2, 3]

  - batch: 2
    name: "Error States"
    mock_type: "error_state"
    tests: [4, 5, 6, 7]

  - batch: 3
    name: "Premium Features"
    mock_type: "premium_user"
    tests: [8, 9, 10]
```
</step>

<step name="create_uat_file">
**Create UAT file with full structure:**

```bash
mkdir -p "$PHASE_DIR"
```

Create file at `.planning/phases/XX-name/{phase}-UAT.md`:

```markdown
---
status: testing
phase: XX-name
source: [list of SUMMARY.md files]
started: [ISO timestamp]
updated: [ISO timestamp]
current_batch: 1
mock_stash: null
pre_work_stash: [from dirty tree handling, or null]
---

## Progress

total: [N]
tested: 0
passed: 0
issues: 0
fixing: 0
pending: [N]
skipped: 0

## Current Batch

batch: 1 of [total_batches]
name: "[batch name]"
mock_type: [mock_type or null]
tests: [test numbers]
status: pending

## Tests

### 1. [Test Name]
expected: [observable behavior]
mock_required: [true/false]
mock_type: [type or null]
result: [pending]

### 2. [Test Name]
...

## Fixes Applied

[none yet]

## Batches

### Batch 1: [Name]
tests: [1, 2, 3]
status: pending
mock_type: null

### Batch 2: [Name]
tests: [4, 5, 6, 7]
status: pending
mock_type: error_state

...

## Assumptions

[none yet]
```

Proceed to `execute_batch`.
</step>

<step name="execute_batch">
**Execute current batch:**

Read current batch from UAT.md.

**1. Handle mock generation (if needed):**

If `mock_type` is not null AND different from previous batch:
- Discard old mocks if any: `git stash drop` (if mock_stash exists)
- Go to `generate_mocks`

If `mock_type` is null or same as previous:
- Skip mock generation
- Go to `present_tests`

**2. Present tests:**
Go to `present_tests`
</step>

<step name="generate_mocks">
**Generate mocks for current batch:**

Present mock generation options:
```
## Batch [N]: [Name]

**Mock required:** [mock_type description]

This batch tests states that require mock data. Options:

1. Generate mocks (Recommended) — I'll create the override files
2. I'll set up mocks manually — Skip generation, you handle it
3. Skip this batch — Log all tests as assumptions
```

**If "Generate mocks":**

Spawn mock generator:
```
Task(
  prompt="""
Generate mocks for manual UAT testing.

Project: {from PROJECT.md}
Phase: {phase_name}
Mock type: {mock_type}

Tests requiring this mock:
{test list with expected behaviors}

Follow patterns from @~/.claude/get-shit-done/workflows/generate-mocks.md
""",
  subagent_type="gsd-mock-generator",
  description="Generate {mock_type} mocks"
)
```

After mock generator returns:

1. Update UAT.md: `mock_stash: null` (mocks are uncommitted, not stashed yet)
2. Present toggle instructions from mock generator
3. Ask user to confirm mocks are active:

```
questions:
  - question: "I've created the mock files. Have you enabled the mocks and verified they're working?"
    header: "Mocks ready"
    options:
      - label: "Yes, mocks are active"
        description: "I've toggled the flags and hot reloaded"
      - label: "Having trouble"
        description: "Something isn't working with the mocks"
    multiSelect: false
```

**If "I'll set up manually":**
- Present what mock state is needed
- Wait for user to confirm ready

**If "Skip this batch":**
- Prompt for reason: "Why are you skipping this batch?"
- Mark all tests in batch as `skipped` with user's reason
- Append to Assumptions section
- Proceed to next batch

Proceed to `present_tests`.
</step>

<step name="present_tests">
**Present batch tests via AskUserQuestion:**

Collect tests for current batch (only `[pending]` and `blocked` results).

Build AskUserQuestion with up to 4 questions:
```
questions:
  - question: "Test {N}: {name} — {expected}"
    header: "Test {N}"
    options:
      - label: "Pass"
        description: "Works as expected"
      - label: "Can't test"
        description: "Blocked by a previous failure"
      - label: "Skip"
        description: "Assume it works (can't test this state)"
    multiSelect: false
```

The "Other" option is auto-added for issue descriptions.

**Tip for users:** To skip with custom reason, select "Other" and start with `Skip:` — e.g., `Skip: Requires paid API key`.

Update Current Batch section:
```
## Current Batch

batch: [N] of [total]
name: "[name]"
mock_type: [type]
tests: [numbers]
status: testing
```

Wait for user responses.
Proceed to `process_batch_responses`.
</step>

<step name="process_batch_responses">
**Process batch responses:**

For each question:

| User Selected | Action |
|---------------|--------|
| "Pass" | result: pass |
| "Can't test" | result: blocked (re-test later) |
| "Skip" | result: skipped, add to Assumptions |
| "Other: Skip: {reason}" | result: skipped with custom reason, add to Assumptions |
| "Other: {text}" | result: issue, go to `investigate_issue` |

**Severity inference (for issues):**

| User description contains | Severity |
|---------------------------|----------|
| crash, error, exception, fails completely, unusable | blocker |
| doesn't work, nothing happens, wrong behavior, missing | major |
| slow, weird, off, minor, small | minor |
| color, font, spacing, alignment, visual | cosmetic |
| Default | major |

**Update UAT.md after processing all responses in batch:**
- Update each test's result
- Update Progress counts
- Update Batches section
- Update timestamp

**For each issue found:** Go to `investigate_issue` before processing next test.
</step>

<step name="investigate_issue">
**Investigate reported issue:**

**1. Lightweight investigation (2-3 tool calls):**

```
# Example investigation:
1. Grep for error message or component name
2. Read the most likely file (from test classification)
3. Check git log for recent changes to relevant files
```

**2. Determine if cause is found:**

**If cause found AND fix is simple (single file, straightforward change):**
- Propose fix in plain language:
  ```
  Found the issue. In `ErrorBanner.tsx` line 42, the error message is
  hardcoded to "Something went wrong" instead of using the actual error
  from the API response.

  I'll change it to use `error.message` from props.

  Apply this fix?
  ```
- Present options: [Yes / Let me see the code first / Different approach]
- If approved: Go to `apply_fix`

**If cause found BUT fix is complex (multiple files, architectural):**
- Report finding
- Spawn gsd-verify-fixer subagent (go to `escalate_to_fixer`)

**If cause NOT found after 2-3 checks:**
- Escalate to fixer subagent (go to `escalate_to_fixer`)
</step>

<step name="apply_fix">
**Apply fix inline:**

**1. Stash mocks (if active):**
```bash
git stash push -m "mocks-batch-{N}"
```
Update UAT.md: `mock_stash: "mocks-batch-{N}"`

**2. Make the fix:**
- Edit the file(s)
- Test that fix compiles/runs

**3. Commit with proper message:**
```bash
git add [specific files]
git commit -m "fix({phase}-uat): {description}"
```

**4. Record in UAT.md:**
- Update test: `fix_status: applied`, `fix_commit: {hash}`
- Append to Fixes Applied section:
  ```yaml
  - commit: {hash}
    test: {N}
    description: "{what was fixed}"
    files: [{changed files}]
  ```

**5. Restore mocks:**
```bash
git stash pop
```

**Handle stash conflict:**
```bash
# If conflict, take fix version
git checkout --theirs <conflicted-file>
git add <conflicted-file>
```
Log that mock was discarded for that file.

**6. Request re-test:**
```
Fix applied. Please re-test: {specific instruction}

[Pass / Still broken / New issue]
```

Go to `handle_retest`.
</step>

<step name="escalate_to_fixer">
**Spawn fixer subagent for complex issue:**

**1. Stash mocks (if active):**
```bash
git stash push -m "mocks-batch-{N}"
```

**2. Spawn gsd-verify-fixer:**
```
Task(
  prompt="""
You are a GSD verify-fixer. Investigate this issue, find the root cause, implement a fix, and commit it.

## Issue

**Test:** {test_name}
**Expected:** {expected_behavior}
**Actual:** {user_reported_behavior}
**Severity:** {inferred_severity}

## Context

**Phase:** {phase_name}
**Mock state active:** {mock_type or "none"}
**Relevant files (suspected):** {file_list}

## What was already checked

{lightweight_investigation_results}

## Your task

1. Investigate to find root cause
2. Implement minimal fix
3. Commit with message: fix({phase}-uat): {description}
4. Return FIX COMPLETE or INVESTIGATION INCONCLUSIVE

Mocks are stashed — working tree is clean.
""",
  subagent_type="gsd-verify-fixer",
  description="Fix: {test_name}"
)
```

**3. Handle fixer return:**

**If FIX COMPLETE:**
- Update UAT.md with fix details
- Restore mocks: `git stash pop`
- Handle conflicts as in `apply_fix`
- Request re-test

**If INVESTIGATION INCONCLUSIVE:**
- Restore mocks: `git stash pop`
- Present options:
  ```
  Investigation didn't find root cause.

  Options:
  1. Try different approach — I'll investigate from another angle
  2. Skip as assumption — Log and move on
  3. Manual investigation — You'll look into this yourself
  ```
- Handle response accordingly
</step>

<step name="handle_retest">
**Handle re-test result:**

Present re-test question:
```
questions:
  - question: "Re-test: {test_name} — Does it work now?"
    header: "Re-test"
    options:
      - label: "Pass"
        description: "Fixed! Works correctly now"
      - label: "Still broken"
        description: "Same issue persists"
      - label: "New issue"
        description: "Original fixed but found different problem"
    multiSelect: false
```

**If Pass:**
- Update test: `result: pass`, `fix_status: verified`
- Continue to next issue or next batch

**If Still broken (retry count < 2):**
- Increment retry count
- Go back to `investigate_issue` with new context

**If Still broken (retry count >= 2):**
- Present options:
  ```
  Fix didn't resolve the issue after 2 attempts.

  Options:
  1. Try different approach — Investigate from scratch
  2. Escalate to subagent — Fresh context might help
  3. Skip as assumption — Log and move on
  ```
- "Try different" → Reset investigation, try again
- "Escalate" → Go to `escalate_to_fixer`
- "Skip" → Mark as skipped assumption

**If New issue:**
- Mark original as pass
- Record new issue and go to `investigate_issue`
</step>

<step name="resume_from_file">
**Resume testing from UAT file:**

Read full UAT file.

Check `mock_stash` — if exists, offer to restore:
```
Found stashed mocks: {mock_stash}

1. Restore mocks — Continue where we left off
2. Discard mocks — Start batch fresh
```

Find current position:
- current_batch
- Tests with `[pending]` or `blocked` or `fixing` status

Announce:
```
Resuming: Phase {phase} UAT
Batch: {current} of {total}
Progress: {tested}/{total}
Issues being fixed: {fixing count}
```

If `fix_status: fixing` exists, go to `handle_retest` for that issue.
Otherwise, go to `execute_batch`.
</step>

<step name="batch_complete">
**Handle batch completion:**

Update Batches section:
```yaml
### Batch {N}: [Name]
tests: [...]
status: complete
mock_type: [...]
passed: {count}
issues: {count}
```

**If more batches remain:**
- Increment current_batch
- Check if next batch needs different mock_type
- If different: discard old mocks, generate new
- Go to `execute_batch`

**If all batches complete:**
- Go to `complete_session`
</step>

<step name="complete_session">
**Complete UAT session:**

**1. Discard mocks:**
```bash
git stash list | grep -q "mocks-batch" && git stash drop
```

**2. Generate UAT fixes patch (if fixes were made):**
```bash
~/.claude/get-shit-done/scripts/generate-phase-patch.sh ${PHASE_NUMBER} --suffix=uat-fixes
```
Output: `.planning/phases/{phase_dir}/{phase}-uat-fixes.patch`

**3. Restore user's pre-existing work (if stashed):**
```bash
git stash list | grep -q "pre-verify-work" && git stash pop
```

**4. Update UAT.md:**
- status: complete
- Clear current_batch, mock_stash
- Final Progress counts

**5. Commit UAT.md:**
```bash
git add ".planning/phases/XX-name/{phase}-UAT.md"
git commit -m "test({phase}): complete UAT - {passed} passed, {fixed} fixed, {skipped} assumptions"
```

**6. Present summary:**
```
## UAT Complete: Phase {phase}

| Result | Count |
|--------|-------|
| Passed | {N} |
| Fixed | {N} |
| Assumptions | {N} |

Fixes applied: {N} commits
Patch file: .planning/phases/{phase_dir}/{phase}-uat-fixes.patch

To review fixes: cat {patch_path}
```
</step>

</process>

<update_rules>
**Write UAT.md after:**
- Each batch of responses processed
- Each fix applied
- Each re-test completed
- Session complete

| Section | Rule | When |
|---------|------|------|
| Frontmatter.status | OVERWRITE | Phase transitions |
| Frontmatter.current_batch | OVERWRITE | Batch transitions |
| Frontmatter.mock_stash | OVERWRITE | Stash operations |
| Frontmatter.updated | OVERWRITE | Every write |
| Progress | OVERWRITE | After each test result |
| Current Batch | OVERWRITE | Batch transitions |
| Tests.{N}.result | OVERWRITE | When user responds |
| Tests.{N}.fix_status | OVERWRITE | During fix flow |
| Tests.{N}.fix_commit | OVERWRITE | After fix committed |
| Fixes Applied | APPEND | After each fix committed |
| Batches.{N}.status | OVERWRITE | Batch transitions |
| Assumptions | APPEND | When test skipped |
</update_rules>

<severity_inference>
**Infer severity from user's natural language:**

| User describes | Infer |
|----------------|-------|
| Crash, error, exception, fails completely, unusable | blocker |
| Doesn't work, nothing happens, wrong behavior, missing | major |
| Works but..., slow, weird, off, minor, small | minor |
| Color, font, spacing, alignment, looks off | cosmetic |

Default: **major** (safe default)

**Never ask "how severe is this?"** — just infer and move on.
</severity_inference>

<success_criteria>
- [ ] Dirty tree handled at start
- [ ] Tests classified by mock requirements
- [ ] Batches created respecting dependencies and mock types
- [ ] Mocks generated when needed with toggle instructions
- [ ] Tests presented in batches of 4
- [ ] Issues investigated with lightweight check (2-3 calls)
- [ ] Simple issues fixed inline with proper commit
- [ ] Complex issues escalated to fixer subagent
- [ ] Re-test retries (2 max) before offering options
- [ ] Stash conflicts auto-resolved to fix version
- [ ] Mocks discarded on completion
- [ ] UAT fixes patch generated
- [ ] User's pre-existing work restored
- [ ] UAT.md committed with final summary
</success_criteria>
