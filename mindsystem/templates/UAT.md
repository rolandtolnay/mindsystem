# UAT Template

Template for `.planning/phases/XX-name/{phase}-UAT.md` — persistent UAT session tracking with mock support and inline fixing.

---

## File Template

```markdown
---
status: testing | fixing | complete
phase: XX-name
source: [list of SUMMARY.md files tested]
started: [ISO timestamp]
updated: [ISO timestamp]
current_batch: [N]
mock_stash: [stash name or null]
pre_work_stash: [stash name or null]
---

## Progress

total: [N]
tested: [N]
passed: [N]
issues: [N]
fixing: [N]
pending: [N]
skipped: [N]

## Current Batch

batch: [N] of [total]
name: "[batch name]"
mock_type: [type or null]
tests: [list of test numbers]
status: pending | testing | complete

## Tests

### 1. [Test Name]
expected: [observable behavior - what user should see]
mock_required: [true/false]
mock_type: [type or null]
result: [pending]

### 2. [Test Name]
expected: [observable behavior]
mock_required: false
mock_type: null
result: pass

### 3. [Test Name]
expected: [observable behavior]
mock_required: true
mock_type: error_state
result: issue
reported: "[verbatim user response]"
severity: major
fix_status: [investigating | applied | verified]
fix_commit: [hash or null]
retry_count: [0-2]

### 4. [Test Name]
expected: [observable behavior]
mock_required: false
mock_type: null
result: blocked

### 5. [Test Name]
expected: [observable behavior]
mock_required: true
mock_type: premium_user
result: skipped
reason: [why couldn't be tested]

...

## Fixes Applied

- commit: [hash]
  test: [N]
  description: "[what was fixed]"
  files: [list of changed files]

- commit: [hash]
  test: [N]
  description: "[what was fixed]"
  files: [list of changed files]

## Batches

### Batch 1: No Mocks Required
tests: [1, 2, 3]
status: complete
mock_type: null
passed: 3
issues: 0

### Batch 2: Error States
tests: [4, 5, 6, 7]
status: in_progress
mock_type: error_state
passed: 1
issues: 1

### Batch 3: Premium Features
tests: [8, 9, 10]
status: pending
mock_type: premium_user

### Batch 4: Empty States
tests: [11, 12]
status: pending
mock_type: empty_response

## Assumptions

- test: [N]
  name: "[Test Name]"
  expected: "[what should happen]"
  reason: "[why it couldn't be tested]"

- test: [N]
  name: "[Test Name]"
  expected: "[what should happen]"
  reason: "[user-provided reason when skipping batch]"
```

---

<section_rules>

**Frontmatter:**
- `status`: OVERWRITE - "testing", "fixing", or "complete"
- `phase`: IMMUTABLE - set on creation
- `source`: IMMUTABLE - SUMMARY files being tested
- `started`: IMMUTABLE - set on creation
- `updated`: OVERWRITE - update on every change
- `current_batch`: OVERWRITE - current batch number
- `mock_stash`: OVERWRITE - name of stashed mocks or null
- `pre_work_stash`: OVERWRITE - user's pre-existing work stash or null

**Progress:**
- OVERWRITE after each test result or fix
- Tracks: total, tested, passed, issues, fixing, pending, skipped

**Current Batch:**
- OVERWRITE entirely on batch transitions
- Shows which batch is active

**Tests:**
- Each test: OVERWRITE result/fix fields when status changes
- `result` values: [pending], pass, issue, blocked, skipped
- If issue: add `reported` (verbatim), `severity` (inferred), `fix_status`, `fix_commit`, `retry_count`
- If blocked: no additional fields (will be re-tested)
- If skipped: add `reason`

**Fixes Applied:**
- APPEND only when fix committed
- Records commit hash, test number, description, files

**Batches:**
- Each batch: OVERWRITE status and counts as batch progresses
- Tracks: tests, status, mock_type, passed, issues

**Assumptions:**
- APPEND when test is skipped
- Records test number, name, expected behavior, reason

</section_rules>

<fix_lifecycle>

**When issue reported:**
1. result → "issue"
2. Add `reported`, `severity`
3. Add `fix_status: investigating`, `retry_count: 0`

**When fix committed:**
4. `fix_status: applied`
5. `fix_commit: {hash}`
6. Append to "Fixes Applied" section

**When re-test passes:**
7. result → "pass"
8. `fix_status: verified`

**When re-test fails:**
9. Increment `retry_count`
10. If `retry_count >= 2`: offer skip/escalate options
11. If user chooses skip: result → "skipped", add reason

</fix_lifecycle>

<mock_lifecycle>

**When batch needs mocks:**
1. Generate mock files (uncommitted)
2. User enables mocks
3. Testing proceeds

**When fix needed:**
1. `git stash push -m "mocks-batch-N"`
2. Update `mock_stash` in frontmatter
3. Fix applied, committed
4. `git stash pop` to restore mocks
5. Clear `mock_stash` if no conflicts

**On batch transition (different mock_type):**
1. Discard old mocks: `git stash drop`
2. Generate new mocks for new batch

**On session complete:**
1. Discard all mocks: `git stash drop`
2. Restore pre_work_stash if exists

</mock_lifecycle>

<resume_behavior>

On `/ms:verify-work` with existing UAT.md:

1. Check `status`:
   - "complete" → offer to re-run or view results
   - "testing" or "fixing" → resume

2. Check `mock_stash`:
   - If exists, offer to restore or discard

3. Check `current_batch`:
   - Resume from that batch

4. Check for tests with `fix_status: investigating` or `fix_status: applied`:
   - Resume fix/re-test flow for those

5. Present remaining tests in current batch

</resume_behavior>

<severity_guide>

Severity is INFERRED from user's natural language, never asked.

| User describes | Infer |
|----------------|-------|
| Crash, error, exception, fails completely, unusable | blocker |
| Doesn't work, nothing happens, wrong behavior, missing | major |
| Works but..., slow, weird, off, minor, small | minor |
| Color, font, spacing, alignment, looks off | cosmetic |

Default: **major** (safe default, user can clarify if wrong)

</severity_guide>

<good_example>
```markdown
---
status: fixing
phase: 04-comments
source: 04-01-SUMMARY.md, 04-02-SUMMARY.md
started: 2025-01-15T10:30:00Z
updated: 2025-01-15T11:15:00Z
current_batch: 2
mock_stash: mocks-batch-2
pre_work_stash: null
---

## Progress

total: 12
tested: 7
passed: 5
issues: 1
fixing: 1
pending: 5
skipped: 0

## Current Batch

batch: 2 of 4
name: "Error States"
mock_type: error_state
tests: [4, 5, 6, 7]
status: testing

## Tests

### 1. View Comments on Post
expected: Comments section expands, shows count and comment list
mock_required: false
mock_type: null
result: pass

### 2. Create Top-Level Comment
expected: Submit comment via rich text editor, appears in list with author info
mock_required: false
mock_type: null
result: pass

### 3. Reply to a Comment
expected: Click Reply, inline composer appears, submit shows nested reply
mock_required: false
mock_type: null
result: pass

### 4. Login Error Message
expected: Invalid credentials show "Invalid email or password" message
mock_required: true
mock_type: error_state
result: issue
reported: "Shows 'Something went wrong' instead of specific error"
severity: major
fix_status: applied
fix_commit: abc123f
retry_count: 0

### 5. Network Error Handling
expected: No connection shows "Check your internet connection" with retry button
mock_required: true
mock_type: error_state
result: [pending]

### 6. Server Error Display
expected: 500 error shows "Try again later" message
mock_required: true
mock_type: error_state
result: [pending]

### 7. Rate Limit Message
expected: Too many requests shows "Too many attempts" with countdown
mock_required: true
mock_type: error_state
result: [pending]

### 8. Premium Badge Display
expected: Premium users show gold badge on profile
mock_required: true
mock_type: premium_user
result: [pending]

### 9. Premium Feature Access
expected: Premium features accessible, non-premium shows upgrade prompt
mock_required: true
mock_type: premium_user
result: [pending]

### 10. Subscription Status
expected: Account page shows current subscription tier and expiry
mock_required: true
mock_type: premium_user
result: [pending]

### 11. Empty Comments List
expected: Post with no comments shows "No comments yet" placeholder
mock_required: true
mock_type: empty_response
result: [pending]

### 12. Empty Search Results
expected: Search with no matches shows "No results found" with suggestions
mock_required: true
mock_type: empty_response
result: [pending]

## Fixes Applied

- commit: abc123f
  test: 4
  description: "Display actual error message from API response"
  files: [src/components/ErrorBanner.tsx]

## Batches

### Batch 1: No Mocks Required
tests: [1, 2, 3]
status: complete
mock_type: null
passed: 3
issues: 0

### Batch 2: Error States
tests: [4, 5, 6, 7]
status: in_progress
mock_type: error_state
passed: 0
issues: 1

### Batch 3: Premium Features
tests: [8, 9, 10]
status: pending
mock_type: premium_user

### Batch 4: Empty States
tests: [11, 12]
status: pending
mock_type: empty_response

## Assumptions

[none yet]
```
</good_example>
