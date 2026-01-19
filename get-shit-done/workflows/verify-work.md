<purpose>
Validate built features through batched testing with persistent state. Creates UAT.md that tracks test progress, survives /clear, and feeds gaps into /gsd:plan-phase --gaps.

User tests in batches of 4 using AskUserQuestion. Optimized for the common case: most tests pass.
</purpose>

<execution_context>
@~/.claude/get-shit-done/workflows/diagnose-issues.md
</execution_context>

<philosophy>
**Batch verification for efficiency.**

Present up to 4 tests per AskUserQuestion call. Users respond to all at once.

Options for each test:
- "Pass" → verified working
- "Can't test" → blocked by prior failure (will re-test later)
- "Skip" → assumption, can't mock required state
- "Other" (custom text) → issue, severity inferred

Optimize for the common case: most tests pass. No severity questions — infer from description.
</philosophy>

<template>
@~/.claude/get-shit-done/templates/UAT.md
</template>

<process>

<step name="check_active_session">
**First: Check for active UAT sessions**

```bash
find .planning/phases -name "*-UAT.md" -type f 2>/dev/null | head -5
```

**If active sessions exist AND no $ARGUMENTS provided:**

Read each file's frontmatter (status, phase) and Current Test section.

Display inline:

```
## Active UAT Sessions

| # | Phase | Status | Current Test | Progress |
|---|-------|--------|--------------|----------|
| 1 | 04-comments | testing | 3. Reply to Comment | 2/6 |
| 2 | 05-auth | testing | 1. Login Form | 0/4 |

Reply with a number to resume, or provide a phase number to start new.
```

Wait for user response.

- If user replies with number (1, 2) → Load that file, go to `resume_from_file`
- If user replies with phase number → Treat as new session, go to `create_uat_file`

**If active sessions exist AND $ARGUMENTS provided:**

Check if session exists for that phase. If yes, offer to resume or restart.
If no, continue to `create_uat_file`.

**If no active sessions AND no $ARGUMENTS:**

```
No active UAT sessions.

Provide a phase number to start testing (e.g., /gsd:verify-work 4)
```

**If no active sessions AND $ARGUMENTS provided:**

Continue to `create_uat_file`.
</step>

<step name="find_summaries">
**Find what to test:**

Parse $ARGUMENTS as phase number (e.g., "4") or plan number (e.g., "04-02").

```bash
# Find phase directory
PHASE_DIR=$(ls -d .planning/phases/${PHASE_ARG}* 2>/dev/null | head -1)

# Find SUMMARY files
ls "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null
```

Read each SUMMARY.md to extract testable deliverables.
</step>

<step name="extract_tests">
**Extract testable deliverables from SUMMARY.md:**

Parse for:
1. **Accomplishments** - Features/functionality added
2. **User-facing changes** - UI, workflows, interactions

Focus on USER-OBSERVABLE outcomes, not implementation details.

For each deliverable, create a test:
- name: Brief test name
- expected: What the user should see/experience (specific, observable)

Examples:
- Accomplishment: "Added comment threading with infinite nesting"
  → Test: "Reply to a Comment"
  → Expected: "Clicking Reply opens inline composer below comment. Submitting shows reply nested under parent with visual indentation."

Skip internal/non-observable items (refactors, type changes, etc.).
</step>

<step name="create_uat_file">
**Create UAT file with all tests:**

```bash
mkdir -p "$PHASE_DIR"
```

Build test list from extracted deliverables.

Create file:

```markdown
---
status: testing
phase: XX-name
source: [list of SUMMARY.md files]
started: [ISO timestamp]
updated: [ISO timestamp]
---

## Current Test

[awaiting first batch]

## Tests

### 1. [Test Name]
expected: [observable behavior]
result: [pending]

### 2. [Test Name]
expected: [observable behavior]
result: [pending]

...

## Summary

total: [N]
passed: 0
issues: 0
blocked: 0
skipped: 0
pending: [N]

## Gaps

[none yet]

## Assumptions

[none yet]
```

Write to `.planning/phases/XX-name/{phase}-UAT.md`

Proceed to `present_test_batch`.
</step>

<step name="present_test_batch">
**Present batch of tests using AskUserQuestion:**

Collect all tests that need response:
- Tests with `result: [pending]`
- Tests with `result: blocked` (re-testing after previous run)

Group into batches of 4 (or fewer for last batch).

For each batch, build AskUserQuestion with up to 4 questions:

```
questions:
  - question: "Test {N}: {name} — {expected}"
    header: "Test {N}"
    options:
      - label: "Pass"
        description: "Works as expected"
      - label: "Can't test"
        description: "Blocked by a previous test failure"
      - label: "Skip"
        description: "Assume it works (can't mock required state)"
    multiSelect: false
  - question: "Test {N+1}: {name} — {expected}"
    header: "Test {N+1}"
    ...
```

The "Other" option is auto-added by AskUserQuestion for issue descriptions.

**Tip:** To skip with a custom reason, select "Other" and start with `Skip:` — e.g., `Skip: Requires paid API key`. This logs as assumption (not issue) with your reason.

Update Current Test section to show batch range:
```
## Current Test

batch: {batch_number} of {total_batches}
tests: {start_N} - {end_N}
awaiting: user response
```

Wait for user to respond to all questions in batch.
Proceed to `process_batch_responses`.
</step>

<step name="process_batch_responses">
**Process batch responses:**

For each question in the batch, parse the user's answer:

| User Selected | Result | Action |
|---------------|--------|--------|
| "Pass" | `pass` | Update test result |
| "Can't test" | `blocked` | Update test result (will re-test on next run) |
| "Skip" | `skipped` | Update test result, append to Assumptions |
| "Other: {text}" | Check prefix | See below |

**If user selected "Other":**

Check if response starts with "Skip:" (case-insensitive):
- "Skip: {reason}" → `skipped` with custom reason, append to Assumptions
- Otherwise → `issue`, infer severity, append to Gaps

**Severity inference** (for issues):
- Contains: crash, error, exception, fails, broken, unusable → blocker
- Contains: doesn't work, wrong, missing, can't → major
- Contains: slow, weird, off, minor, small → minor
- Contains: color, font, spacing, alignment, visual → cosmetic
- Default if unclear: major

**Update file after batch:**

Update Tests section with all results:
```
### {N}. {name}
expected: {expected}
result: {pass | issue | blocked | skipped}
[If issue: reported: "{text}", severity: {inferred}]
[If skipped: reason: "{reason}"]
```

If any issues in batch, append to Gaps section:
```yaml
- truth: "{expected behavior from test}"
  status: failed
  reason: "User reported: {verbatim response}"
  severity: {inferred}
  test: {N}
  artifacts: []  # Filled by diagnosis
  missing: []    # Filled by diagnosis
```

If any skipped in batch, append to Assumptions section:
```yaml
- test: {N}
  name: "{test name}"
  expected: "{expected behavior}"
  reason: "{reason or 'Can't mock required state'}"
```

Update Summary counts (total, passed, issues, blocked, skipped, pending).
Update frontmatter.updated timestamp.

**Write file** (batch checkpoint).

If more tests remain → Go to `present_test_batch`
If no more tests → Go to `complete_session`
</step>

<step name="resume_from_file">
**Resume testing from UAT file:**

Read the full UAT file.

Find all tests that need response:
- Tests with `result: [pending]`
- Tests with `result: blocked` (re-testing after previous run)

Calculate remaining count.

Announce:
```
Resuming: Phase {phase} UAT
Progress: {passed + issues + skipped}/{total}
Remaining: {pending_count} pending, {blocked_count} blocked (re-testing)
Issues found so far: {issues count}
Assumptions made: {skipped count}
```

Proceed to `present_test_batch`.
</step>

<step name="complete_session">
**Complete testing and commit:**

Update frontmatter:
- status: complete
- updated: [now]

Clear Current Test section:
```
## Current Test

[testing complete]
```

Commit the UAT file:
```bash
git add ".planning/phases/XX-name/{phase}-UAT.md"
git commit -m "test({phase}): complete UAT - {passed} passed, {issues} issues, {skipped} assumptions"
```

Present summary:
```
## UAT Complete: Phase {phase}

| Result | Count |
|--------|-------|
| Passed | {N}   |
| Issues | {N}   |
| Blocked | {N}  |
| Assumptions | {N} |

[If blocked > 0:]
### Blocked Tests

{N} tests couldn't be verified due to prior failures.
Run `/gsd:verify-work {phase}` again after fixing issues to re-test.

[If skipped > 0:]
### Assumptions Made

{N} tests were skipped — these are assumptions that couldn't be verified.
See Assumptions section in UAT file.

[If issues > 0:]
### Issues Found

[List from Issues section]
```

**If issues > 0:** Proceed to `diagnose_issues`

**If issues == 0 AND blocked == 0:**
```
All tests passed. Ready to continue.

- `/gsd:plan-phase {next}` — Plan next phase
- `/gsd:execute-phase {next}` — Execute next phase
```

**If issues == 0 AND blocked > 0:**
```
No new issues, but {blocked} tests still blocked.
Fix prior issues first, then run `/gsd:verify-work {phase}` to re-test.
```
</step>

<step name="diagnose_issues">
**Auto-diagnose root causes:**

```
{N} issues found. Diagnosing root causes...

Spawning parallel debug agents to investigate each issue.
```

Follow the diagnose-issues.md workflow:
1. Parse gaps from UAT.md
2. Spawn parallel gsd-debugger agents (one per gap)
3. Collect root causes
4. Update UAT.md gaps with diagnosis:
   - root_cause: The diagnosed cause
   - artifacts: Files involved
   - missing: What needs to be added/fixed
   - debug_session: Path to debug file

Commit updated UAT.md:
```bash
git add ".planning/phases/${PHASE_DIR}/${PHASE}-UAT.md"
git commit -m "docs(${PHASE}): diagnose UAT gaps"
```

Proceed to update_state.
</step>

<step name="update_state">
**Update STATE.md with blockers:**

Add phase blockers to STATE.md:
```markdown
### Blockers

| Phase | Issue | Root Cause | Severity |
|-------|-------|------------|----------|
| {phase} | {truth} | {root_cause} | {severity} |
```

Proceed to offer_gap_closure.
</step>

<step name="offer_gap_closure">
**Present diagnosis and next steps:**

```
## Diagnosis Complete

**Phase {X}: {Name}**

{N}/{M} tests passed
{X} issues diagnosed

### Diagnosed Gaps

| Gap | Root Cause | Files |
|-----|------------|-------|
| {truth 1} | {root_cause} | {files} |
| {truth 2} | {root_cause} | {files} |

Debug sessions: .planning/debug/

---

## Next Up

**Plan fixes** — create fix plans from diagnosed gaps

`/gsd:plan-phase {phase} --gaps`

`/clear` first for fresh context window

---

**Also available:**
- `cat .planning/phases/{phase_dir}/{phase}-UAT.md` — review full diagnosis
- `/gsd:debug {issue}` — investigate specific issue further
```
</step>

</process>

<update_rules>
**Write after each batch:**

Keep results in memory during batch. Write to file after user responds to full batch.

| Trigger | Action |
|---------|--------|
| Batch complete | Write all batch results |
| Session complete | Final write + commit |

| Section | Rule | When Written |
|---------|------|--------------|
| Frontmatter.status | OVERWRITE | Start, complete |
| Frontmatter.updated | OVERWRITE | After each batch |
| Current Test | OVERWRITE | After each batch |
| Tests.{N}.result | OVERWRITE | After each batch |
| Summary | OVERWRITE | After each batch |
| Gaps | APPEND | When issue found |
| Assumptions | APPEND | When test skipped |

On context reset: Resume from last written batch. Worst case: re-answer up to 3 questions.
</update_rules>

<severity_inference>
**Infer severity from user's natural language:**

| User says | Infer |
|-----------|-------|
| "crashes", "error", "exception", "fails completely" | blocker |
| "doesn't work", "nothing happens", "wrong behavior" | major |
| "works but...", "slow", "weird", "minor issue" | minor |
| "color", "spacing", "alignment", "looks off" | cosmetic |

Default to **major** if unclear. User can correct if needed.

**Never ask "how severe is this?"** - just infer and move on.
</severity_inference>

<success_criteria>
- [ ] UAT file created with all tests from SUMMARY.md
- [ ] Tests presented in batches of 4 using AskUserQuestion
- [ ] User responses processed as pass/issue/blocked/skipped
- [ ] Severity inferred from description (never asked)
- [ ] File written after each batch (checkpoint)
- [ ] Blocked tests re-presented on subsequent runs
- [ ] Skipped tests logged to Assumptions section
- [ ] Committed on completion
- [ ] If issues: parallel debug agents diagnose root causes
- [ ] If issues: UAT.md updated with root_cause, artifacts, missing
- [ ] If issues: STATE.md updated with phase blockers
- [ ] Clear next steps: /gsd:plan-phase --gaps with diagnostic context
</success_criteria>
