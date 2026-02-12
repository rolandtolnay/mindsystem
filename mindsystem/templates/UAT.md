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
mocked_files: []
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

