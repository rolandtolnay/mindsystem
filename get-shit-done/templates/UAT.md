# UAT Template

Template for `.planning/phases/XX-name/{phase}-UAT.md` — persistent UAT session tracking.

---

## File Template

```markdown
---
status: testing | complete | diagnosed
phase: XX-name
source: [list of SUMMARY.md files tested]
started: [ISO timestamp]
updated: [ISO timestamp]
---

## Current Test
<!-- OVERWRITE each test - shows where we are -->

number: [N]
name: [test name]
expected: |
  [what user should observe]
awaiting: user response

## Tests

### 1. [Test Name]
expected: [observable behavior - what user should see]
result: [pending]

### 2. [Test Name]
expected: [observable behavior]
result: pass

### 3. [Test Name]
expected: [observable behavior]
result: issue
reported: "[verbatim user response]"
severity: major

### 4. [Test Name]
expected: [observable behavior]
result: blocked

### 5. [Test Name]
expected: [observable behavior]
result: skipped
reason: [why couldn't be tested]

...

## Summary

total: [N]
passed: [N]
issues: [N]
blocked: [N]
skipped: [N]
pending: [N]

## Gaps

<!-- YAML format for plan-phase --gaps consumption -->
- truth: "[expected behavior from test]"
  status: failed
  reason: "User reported: [verbatim response]"
  severity: blocker | major | minor | cosmetic
  test: [N]
  root_cause: ""     # Filled by diagnosis
  artifacts: []      # Filled by diagnosis
  missing: []        # Filled by diagnosis
  debug_session: ""  # Filled by diagnosis

## Assumptions

<!-- Tests skipped because required state couldn't be mocked -->
- test: [N]
  name: "[Test Name]"
  expected: "[what should happen]"
  reason: "[why it couldn't be tested]"
```

---

<section_rules>

**Frontmatter:**
- `status`: OVERWRITE - "testing" or "complete"
- `phase`: IMMUTABLE - set on creation
- `source`: IMMUTABLE - SUMMARY files being tested
- `started`: IMMUTABLE - set on creation
- `updated`: OVERWRITE - update on every change

**Current Test:**
- OVERWRITE entirely on each test transition
- Shows which test is active and what's awaited
- On completion: "[testing complete]"

**Tests:**
- Each test: OVERWRITE result field when user responds
- `result` values: [pending], pass, issue, blocked, skipped
- If issue: add `reported` (verbatim) and `severity` (inferred)
- If blocked: no additional fields (will be re-tested)
- If skipped: add `reason` (assumption - can't mock required state, or custom via "Other: Skip: {reason}")

**Summary:**
- OVERWRITE counts after each batch
- Tracks: total, passed, issues, blocked, skipped, pending

**Gaps:**
- APPEND only when issue found (YAML format)
- After diagnosis: fill `root_cause`, `artifacts`, `missing`, `debug_session`
- This section feeds directly into /gsd:plan-phase --gaps

**Assumptions:**
- APPEND when test is skipped (can't mock required state)
- Aggregated by /gsd:audit-milestone into MILESTONE-AUDIT.md
- Surfaced during /gsd:new-milestone discovery

</section_rules>

<diagnosis_lifecycle>

**After testing complete (status: complete), if gaps exist:**

1. User runs diagnosis (from verify-work offer or manually)
2. diagnose-issues workflow spawns parallel debug agents
3. Each agent investigates one gap, returns root cause
4. UAT.md Gaps section updated with diagnosis:
   - Each gap gets `root_cause`, `artifacts`, `missing`, `debug_session` filled
5. status → "diagnosed"
6. Ready for /gsd:plan-phase --gaps with root causes

**After diagnosis:**
```yaml
## Gaps

- truth: "Comment appears immediately after submission"
  status: failed
  reason: "User reported: works but doesn't show until I refresh the page"
  severity: major
  test: 2
  root_cause: "useEffect in CommentList.tsx missing commentCount dependency"
  artifacts:
    - path: "src/components/CommentList.tsx"
      issue: "useEffect missing dependency"
  missing:
    - "Add commentCount to useEffect dependency array"
  debug_session: ".planning/debug/comment-not-refreshing.md"
```

</diagnosis_lifecycle>

<lifecycle>

**Creation:** When /gsd:verify-work starts new session
- Extract tests from SUMMARY.md files
- Set status to "testing"
- All tests have result: [pending]

**During testing:**
- Present tests in batches of 4 using AskUserQuestion
- User responds to all tests in batch at once
- Update test results (pass/issue/blocked/skipped)
- Update Summary counts
- If issue: append to Gaps section, infer severity
- If skipped: append to Assumptions section
- Write to file after each batch (checkpoint)

**On completion:**
- status → "complete"
- Current Test → "[testing complete]"
- Commit file
- Present summary with next steps

**Resume behavior:**
- Tests with result: [pending] → presented in next batch
- Tests with result: blocked → ALSO presented in next batch (re-test after fixes)
- Tests with result: skipped → NOT re-presented (assumption stands)
- Tests with result: pass/issue → NOT re-presented (already processed)

</lifecycle>

<severity_guide>

Severity is INFERRED from user's natural language, never asked.

| User describes | Infer |
|----------------|-------|
| Crash, error, exception, fails completely, unusable | blocker |
| Doesn't work, nothing happens, wrong behavior, missing | major |
| Works but..., slow, weird, minor, small issue | minor |
| Color, font, spacing, alignment, visual, looks off | cosmetic |

Default: **major** (safe default, user can clarify if wrong)

</severity_guide>

<good_example>
```markdown
---
status: diagnosed
phase: 04-comments
source: 04-01-SUMMARY.md, 04-02-SUMMARY.md
started: 2025-01-15T10:30:00Z
updated: 2025-01-15T10:45:00Z
---

## Current Test

[testing complete]

## Tests

### 1. View Comments on Post
expected: Comments section expands, shows count and comment list
result: pass

### 2. Create Top-Level Comment
expected: Submit comment via rich text editor, appears in list with author info
result: issue
reported: "works but doesn't show until I refresh the page"
severity: major

### 3. Reply to a Comment
expected: Click Reply, inline composer appears, submit shows nested reply
result: blocked

### 4. Visual Nesting
expected: 3+ level thread shows indentation, left borders, caps at reasonable depth
result: pass

### 5. Delete Own Comment
expected: Click delete on own comment, removed or shows [deleted] if has replies
result: pass

### 6. Comment Count
expected: Post shows accurate count, increments when adding comment
result: pass

### 7. Error State Display
expected: Shows error message when comment submission fails
result: skipped
reason: "Can't mock API error responses"

### 8. Empty State
expected: Shows 'No comments yet' placeholder when no comments exist
result: skipped
reason: "Can't clear existing comments to test empty state"

## Summary

total: 8
passed: 4
issues: 1
blocked: 1
skipped: 2
pending: 0

## Gaps

- truth: "Comment appears immediately after submission in list"
  status: failed
  reason: "User reported: works but doesn't show until I refresh the page"
  severity: major
  test: 2
  root_cause: "useEffect in CommentList.tsx missing commentCount dependency"
  artifacts:
    - path: "src/components/CommentList.tsx"
      issue: "useEffect missing dependency"
  missing:
    - "Add commentCount to useEffect dependency array"
  debug_session: ".planning/debug/comment-not-refreshing.md"

## Assumptions

- test: 7
  name: "Error State Display"
  expected: "Shows error message when comment submission fails"
  reason: "Can't mock API error responses"

- test: 8
  name: "Empty State"
  expected: "Shows 'No comments yet' placeholder when no comments exist"
  reason: "Can't clear existing comments to test empty state"
```
</good_example>
