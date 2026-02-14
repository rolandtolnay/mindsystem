<purpose>
Validate built features through batched testing with mock support and inline fixing. Creates UAT.md that tracks test progress, supports mock generation for UI state testing, and fixes issues immediately while context is fresh.

Complete verify-and-fix session: by session end, everything verified, issues fixed, tests passing.
</purpose>

<execution_context>
<!-- mock-patterns.md loaded on demand for transient_state mocks (see generate_mocks step) -->
</execution_context>

<process>

<step name="check_dirty_tree" priority="first">
**Before anything else, check for uncommitted changes.**

```bash
git status --porcelain
```

**If output is non-empty (dirty tree):**

AskUserQuestion with options: Stash changes / Commit first / Abort

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

Provide a phase number to start testing (e.g., /ms:verify-work 4)
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
**Classify all tests by mock requirements using two-tier analysis:**

For each test, determine:
1. **mock_required**: Does this need special backend state?
2. **mock_type**: Classification (e.g., "transient_state", "external_data", "error_state", "premium_user", "empty_response")
3. **dependencies**: Other tests this depends on (infer from descriptions)

**Tier 1: SUMMARY.md mock_hints (primary)**

Check if SUMMARY.md files contain mock_hints frontmatter:
```bash
grep -l "mock_hints:" "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null
```

If found, check the value:

- **`mock_hints: none`** → Short-circuit: all tests start as `mock_required: false`. Apply keyword heuristics only as safety net (scan test descriptions for obvious mock signals like "error", "loading", "empty").

- **`mock_hints` with content** → Parse and match tests against hints:
  - Test relates to a `transient_states` entry → `mock_type: "transient_state"`, `mock_reason: "[from hint]"`
  - Test relates to an `external_data` entry → `mock_type: "external_data"`, `needs_user_confirmation: true`
  - Test doesn't match any hint → apply keyword heuristics below

**Tier 2: Inline classification (fallback for legacy summaries)**

When no `mock_hints` key found in any SUMMARY.md (legacy summaries written before executor populated this field):

Classify in main context using the two-question framework:

1. **Is the observable state transient?** — Does it appear briefly during async operations? (loading skeleton, spinner, transition animation). If YES → `mock_type: "transient_state"`

2. **Does the test depend on external data?** — Does the feature fetch from an API, database, or external service? Would the test fail without specific data existing? If YES → `mock_type: "external_data"`, `needs_user_confirmation: true`

Reason over SUMMARY.md content (accomplishments, files created/modified, decisions) to answer these questions. Supplement with keyword heuristics:

| Expected behavior contains | Likely mock_type |
|---------------------------|------------------|
| "error", "fails", "invalid", "retry" | error_state |
| "premium", "pro", "paid", "subscription" | premium_user |
| "empty", "no results", "placeholder" | empty_response |
| "loading", "spinner", "skeleton" | transient_state |
| "offline", "no connection" | offline_state |
| Normal happy path | no mock needed |

For tests that remain genuinely uncertain after both the two-question framework and keyword heuristics, AskUserQuestion per uncertain test: No mock needed / Needs mock.

**Dependency inference (both tiers):**
- "Reply to comment" depends on "View comments"
- "Delete account" depends on "Login"
- Tests mentioning prior state depend on tests that create that state

Build classification list with fields: name, mock_required, mock_type, mock_reason, dependencies, needs_user_confirmation.
</step>

<step name="create_batches">
**Group tests into batches:**

**If any tests have mock_required=true AND batch includes `transient_state` mocks:** Read `~/.claude/mindsystem/references/mock-patterns.md` for delay/never-resolve strategies.

**Rules:**
1. Group by mock_type (tests needing same mock state go together)
2. **User confirmation for external_data tests:** Before batching, collect all tests with `needs_user_confirmation: true`, grouped by data source. AskUserQuestion per data source: Yes, data exists / No, needs mock / Skip these tests. Handle responses: reclassify as `mock_required: false`, keep as mock, or mark `skipped`. Group by data source (not per-test) to stay within AskUserQuestion's 4-question limit.

3. **Separate transient_state batch:** Transient states use a different mock strategy (delay/force) than data mocks. Give them their own batch.
4. Respect dependencies (if B depends on A, A must be in same or earlier batch)
5. Max 4 tests per batch (AskUserQuestion limit)
6. Batch ordering: no-mock → external_data → error_state → empty_response → transient_state → premium_user → offline_state

Each batch has: batch number, name, mock_type, and test list.
</step>

<step name="create_uat_file">
**Create UAT file:**

```bash
mkdir -p "$PHASE_DIR"
```

Create file at `.planning/phases/XX-name/{phase}-UAT.md` following the template structure in context. Populate with classified tests and batch data from previous steps.

Proceed to `execute_batch`.
</step>

<step name="execute_batch">
**Execute current batch:**

Read current batch from UAT.md.

**1. Handle mock generation (if needed):**

If `mock_type` is not null AND different from previous batch:
- Revert old mocks if any (from `mocked_files` in UAT.md frontmatter):
  ```bash
  git checkout -- <mocked_files>
  ```
- Clear `mocked_files` in frontmatter
- Go to `generate_mocks`

If `mock_type` is null or same as previous:
- Skip mock generation
- Go to `present_tests`

**2. Present tests:**
Go to `present_tests`
</step>

<step name="generate_mocks">
**Generate mocks for current batch using inline approach:**

Count mock-requiring tests in this batch.

**Decision logic:**

| Count | Approach |
|-------|----------|
| 1-4   | Inline: edit service methods directly in main context |
| 5+    | Subagent: spawn ms-mock-generator for batch editing |

**Inline approach (1-4 mocks):**

For each test in the batch:
1. Identify the service/repository method that provides the data
2. Read the method
3. Edit to hardcode desired return value BEFORE the real implementation:
   ```
   // MOCK: {description} — revert after UAT
   {hardcoded return/throw}
   ```
4. For transient_state mocks: Read `~/.claude/mindsystem/references/mock-patterns.md` for delay/never-resolve strategies

**Subagent approach (5+ mocks):**

```
Task(
  prompt="""
Generate inline mocks for manual UAT testing.

Phase: {phase_name}

Tests requiring mocks:
{test list with mock_type and expected behaviors}

Mocked files from previous batches (avoid conflicts):
{mocked_files from UAT.md frontmatter}
""",
  subagent_type="ms-mock-generator",
  description="Generate {mock_type} mocks"
)
```

**After mocks applied (both approaches):**

1. Record mocked files in UAT.md frontmatter: `mocked_files: [file1.dart, file2.dart, ...]`
2. Tell user: "Mocks applied. Hot reload to test."
3. Proceed directly to `present_tests` — no user confirmation needed

**Skip option:**

If user has previously indicated they want to skip mock batches, or if mock generation fails:
- Mark all tests in batch as `skipped`
- Append to Assumptions section
- Proceed to next batch
</step>

<step name="present_tests">
**Present batch tests via AskUserQuestion:**

Collect tests for current batch (only `[pending]` and `blocked` results).

AskUserQuestion per test (up to 4): Pass / Can't test / Skip. "Other" auto-added for issue descriptions.

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
| "Other: {text}" | result: issue, add `fix_status: investigating`, `retry_count: 0`, go to `investigate_issue` |

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
- Spawn ms-verify-fixer subagent (go to `escalate_to_fixer`)

**If cause NOT found after 2-3 checks:**
- Escalate to fixer subagent (go to `escalate_to_fixer`)
</step>

<step name="apply_fix">
**Apply fix inline:**

**1. Stash mocks (if active):**
```bash
git stash push -m "mocks-batch-{N}" -- <mocked_files>
```
Use `mocked_files` list from UAT.md frontmatter.

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
# Conflict means fix touched a mocked file — take the fix version
git checkout --theirs <conflicted-file>
git add <conflicted-file>
```
Remove conflicted file from `mocked_files` list in UAT.md (mock no longer needed for that file).

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
git stash push -m "mocks-batch-{N}" -- <mocked_files>
```

**2. Spawn ms-verify-fixer:**
```
Task(
  prompt="""
You are a Mindsystem verify-fixer. Investigate this issue, find the root cause, implement a fix, and commit it.

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
  subagent_type="ms-verify-fixer",
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

AskUserQuestion: Pass / Still broken / New issue.

**If Pass:**
- Update test: `result: pass`, `fix_status: verified`
- Continue to next issue or next batch

**If Still broken (retry_count < 2):**
- Increment `retry_count` in UAT.md test entry
- Go back to `investigate_issue` with new context

**If Still broken (retry_count >= 2):**
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

Check `mocked_files` — if non-empty, verify mocks are still present:
```bash
git diff --name-only
```
If mocked files have uncommitted changes, mocks are still active — continue.
If mocked files are clean, mocks were lost — regenerate for current batch.

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

**1. Check for blocked tests that can now be retested:**

Before marking batch complete, check if any tests have `result: blocked`.
If blocked tests exist AND no issues remain in `fixing` status:
- Re-present the blocked tests via `present_tests`
- Blocked tests were waiting on other issues to be fixed first

**2. Update Batches section (when no blocked tests remain):**

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

**1. Revert mocks:**
```bash
git checkout -- <mocked_files>
```
Use `mocked_files` list from UAT.md frontmatter. Clear the list after reverting.

**2. Generate UAT fixes patch (if fixes were made):**
```bash
~/.claude/mindsystem/scripts/generate-phase-patch.sh ${PHASE_NUMBER} --suffix=uat-fixes
```
Output: `.planning/phases/{phase_dir}/{phase}-uat-fixes.patch`

**3. Restore user's pre-existing work (if stashed):**
```bash
# Find and pop the specific pre-work stash
PRE_WORK_STASH=$(git stash list | grep "pre-verify-work" | head -1 | cut -d: -f1)
[ -n "$PRE_WORK_STASH" ] && git stash pop "$PRE_WORK_STASH"
```

**4. Update UAT.md:**
- status: complete
- Clear current_batch, mocked_files
- Final Progress counts

**5. Commit UAT.md:**
```bash
git add ".planning/phases/XX-name/{phase}-UAT.md"
git commit -m "test({phase}): complete UAT - {passed} passed, {fixed} fixed, {skipped} assumptions"
```

**5.5. Update knowledge pitfalls (lightweight):**

```bash
# Check for significant findings
grep -c "severity: blocker\|severity: major" "$PHASE_DIR/${PHASE}-UAT.md" 2>/dev/null
```

If significant issues (blocker/major) were found AND fixed:
1. Determine affected subsystem(s) from the UAT.md test descriptions and config.json
2. Read relevant `knowledge/{subsystem}.md` files
3. Append new pitfall entries to the Pitfalls section (do not rewrite entire file — just append)
4. Commit knowledge file updates:
```bash
git add .planning/knowledge/*.md && git commit -m "docs: update pitfalls from UAT findings"
```

If no significant findings or no fixes: skip silently.

This is NOT a full re-consolidation. Read only UAT.md and add specific pitfall entries.

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

**7. Present next steps:**

Check if more phases remain in ROADMAP.md:
- If last phase in milestone: Suggest `/ms:audit-milestone` or `/ms:complete-milestone`
- If more phases remain: Read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions to present "Next Up" with pre-work context for the next phase
</step>

</process>

<update_rules>
**Immutable (set on creation, never overwrite):** phase, source, started
**Result values:** [pending], pass, issue, blocked, skipped
**Issue adds:** reported, severity, fix_status (investigating | applied | verified), fix_commit, retry_count
**Skipped adds:** reason

**Write UAT.md after:**
- Each batch of responses processed
- Each fix applied
- Each re-test completed
- Session complete

| Section | Rule | When |
|---------|------|------|
| Frontmatter.status | OVERWRITE | Phase transitions |
| Frontmatter.current_batch | OVERWRITE | Batch transitions |
| Frontmatter.mocked_files | OVERWRITE | Mock generation/cleanup |
| Frontmatter.pre_work_stash | OVERWRITE | Dirty tree handling |
| Frontmatter.updated | OVERWRITE | Every write |
| Progress | OVERWRITE | After each test result |
| Current Batch | OVERWRITE | Batch transitions |
| Tests.{N}.result | OVERWRITE | When user responds |
| Tests.{N}.fix_status | OVERWRITE | During fix flow |
| Tests.{N}.fix_commit | OVERWRITE | After fix committed |
| Tests.{N}.retry_count | OVERWRITE | On re-test failure |
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
- [ ] Mocks stashed before fixing, restored after (git stash push/pop cycle)
- [ ] Stash conflicts auto-resolved to fix version (git checkout --theirs)
- [ ] Blocked tests re-presented after blocking issues resolved
- [ ] Failed re-tests get 2 retries then options (tracked via retry_count)
- [ ] All mocks reverted on completion (git checkout -- <mocked_files>)
- [ ] UAT fixes patch generated
- [ ] User's pre-existing work restored from stash
</success_criteria>
