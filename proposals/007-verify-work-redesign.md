# Verify-Work Redesign Proposal

## Problem Statement

The current `/gsd:verify-work` command has significant friction:

1. **Context switching loop**: verify → log gaps → `/clear` → `plan-phase --gaps` → execute → verify again. Users lose momentum and context across multiple sessions.

2. **No mock support**: Testing UI states requiring specific backend conditions (premium user, error states, empty states, loading states) requires manual setup outside the workflow.

3. **Deferred fixing**: Issues are diagnosed but not fixed in the same session. The user must context-switch to planning and execution phases before re-verifying.

4. **Batch inefficiency**: Tests are presented without regard for mock requirements, causing unnecessary mock churn.

## Goals

**Primary:** Run `/gsd:verify-work` and by session end, have everything verified, issues fixed, and tests passing — all in one flow.

**Secondary:**
- Support mock-assisted testing for UI state verification
- Fix issues immediately while relevant context (mocks, mental model) is active
- Minimize user decision points while maintaining control
- Preserve state persistence (UAT.md survives `/clear` for interruptions)
- Keep main context lean; delegate implementation work to subagents

## Non-Goals

- **Automated UI testing**: This remains manual user verification on device/emulator
- **Framework-specific patterns**: Design must work across Flutter, React Native, web, etc.
- **Replacing gsd-debugger**: Build on existing debugging patterns, don't rewrite
- **Changing test source**: Keep SUMMARY.md as source of truth for testables
- **Parallel batch execution**: Batches must be sequential (mock state is shared)

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│  MAIN CONTEXT (Orchestrator)                                    │
│                                                                 │
│  Responsibilities:                                              │
│  - Load SUMMARY.md, extract testables                           │
│  - Classify tests by mock requirements                          │
│  - Group into batches (by mock state, max 4 tests)              │
│  - Present batches via AskUserQuestion                          │
│  - Track state in UAT.md (survives /clear)                      │
│  - Lightweight investigation for simple issues                  │
│  - Orchestrate subagents for complex work                       │
│                                                                 │
│  Context budget: ~40% (orchestration only, no implementation)   │
└─────────────────────────────────────────────────────────────────┘
          │
          ├──▶ [Mock Generator Subagent]
          │    When: User confirms mock generation for a batch
          │    Input: Test requirements, mock type needed
          │    Output: Mock code + instructions for user
          │    Context: Fresh 200k
          │
          ├──▶ [Verify-Fixer Subagent] (one per complex issue)
          │    When: Issue fails lightweight investigation threshold
          │    Input: Issue description, relevant files, current mock state
          │    Output: Committed fix + verification instruction
          │    Context: Fresh 200k per issue
          │
          └──▶ [Cleanup] (main context, not subagent)
               When: All batches complete
               Action: git stash drop, final UAT.md update, summary
```

## Detailed Design

### Mock System

#### Philosophy

Mocks are temporary scaffolding to reach testable states. They exist only as uncommitted changes or stashed changes — never in commit history.

#### Mock Lifecycle (Git Stash Approach)

```
Phase 1: Setup
─────────────────────────────────────────────────────────
1. git stash push -m "pre-verify-work" (if dirty)  # Save any existing work
2. Mock Generator creates mock code (uncommitted)
3. User confirms mocks look correct

Phase 2: Test-Fix Loop (per batch)
─────────────────────────────────────────────────────────
4. User tests on device with mocks active
5. User reports results via AskUserQuestion
6. For each issue:
   a. git stash push -m "mocks-batch-N"    # Stash mocks, clean tree
   b. Fixer investigates and commits fix   # Clean commit, no mock code
   c. git stash pop                        # Restore mocks for re-test
   d. User re-tests specific item
   e. Repeat until fixed or escalate

Phase 3: Cleanup
─────────────────────────────────────────────────────────
7. git stash drop                          # Discard mocks permanently
8. Generate UAT fixes patch (if any fixes were made)
9. git stash pop (if had pre-existing)     # Restore user's original work
```

#### UAT Fixes Patch Generation

Reuse the existing patch generation pattern from `/gsd:execute-phase`:

```bash
# Generate patch for all UAT fix commits
~/.claude/get-shit-done/scripts/generate-phase-patch.sh ${PHASE_NUMBER} --suffix=uat-fixes
```

**Commit message convention for UAT fixes:**
```
fix({phase}-uat): {description}

# Examples:
fix(04-uat): display actual error message from API
fix(04-uat): add missing loading state to comment list
```

**Output:** `.planning/phases/{phase_dir}/{phase}-uat-fixes.patch`

This allows reviewing all UAT fixes after verify-work completes:
```bash
cat .planning/phases/04-auth/{phase}-uat-fixes.patch
```

#### Handling Stash Conflicts

If `git stash pop` conflicts (fix touched same file as mock):

```bash
# Conflict means fix modified mock code — take the fix version
git checkout --theirs <conflicted-file>
git add <conflicted-file>
# The mock for that file is no longer needed (fix replaced relevant code)
```

This is rare (mocks in data layer, fixes often in UI layer) and self-resolving.

#### Mock Implementation Pattern (Framework-Agnostic)

Mock Generator produces code following this pattern:

```
# Pattern: Additive override file + minimal production hooks

1. Create override file: lib/test_overrides.{ext}
   - Contains flags: forceLoading, forceError, forcePremium, forceEmpty
   - Contains mock data: mockErrorMessage, mockUserData, etc.
   - Has reset() function to clear all overrides

2. Add minimal hooks to relevant services/repositories:
   - Check override flags before real implementation
   - Return mock data when flag is set
   - Fall through to real implementation otherwise

3. Provide toggle instructions for user:
   - How to enable each mock state
   - Hot reload / restart requirements
```

The override file is the primary mock artifact. Production hooks are minimal (single if-check per mock point).

### Test Batching

#### Classification Phase

Before presenting tests, classify each by mock requirements:

```yaml
# Internal classification (not shown to user in full)
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

  - name: "Empty list placeholder"
    mock_required: true
    mock_type: "empty_response"
    dependencies: ["login_flow"]
```

#### Batching Rules

1. **Group by mock type**: Tests requiring same mock state go together
2. **Respect dependencies**: If test B depends on test A, A must be in same or earlier batch
3. **Max 4 per batch**: AskUserQuestion limit; keeps batches digestible
4. **No-mock tests first**: Run tests not requiring mocks before mock setup
5. **Order mock states logically**: success → error → empty → loading (typical flow)

#### Batch Presentation

```markdown
## Batch 1 of 4: No Mocks Required

These tests use real app state:

| # | Test | Expected |
|---|------|----------|
| 1 | Login success | Valid credentials → dashboard |
| 2 | Logout | Session cleared, back to login |
| 3 | Remember me | Checkbox persists login across restart |

Ready to test? Run the app and verify each item.
```

```markdown
## Batch 2 of 4: Error States

**Mock required:** Error responses from API

I'll generate mocks that make API calls return errors. You'll be able to toggle
which endpoint fails.

Options:
1. Generate mocks (I'll create the override file)
2. I'll set up mocks manually
3. Skip this batch (log as assumptions)
```

### Investigation & Fix Flow

#### Threshold-Based Investigation

When user reports an issue, main context does lightweight investigation first:

```
Lightweight checks (main context, ~2-3 tool calls):
1. Grep for error message in codebase
2. Read the most likely file (from test classification)
3. Check recent commits touching relevant files

If cause found → propose fix inline
If inconclusive after 3 checks → spawn Verify-Fixer subagent
```

#### Per-Issue Flow

```
1. User reports: "Error message shows wrong text"

2. Main context: Quick investigation
   - Grep "error" in relevant component → found ErrorBanner.tsx
   - Read file → see hardcoded string "Something went wrong"
   - Cause clear: wrong error message text

3. Main context: Propose fix (plain language explanation)

   "Found the issue. In `ErrorBanner.tsx` line 42, the error message is
   hardcoded to "Something went wrong" instead of using the actual error
   from the API response.

   I'll change it to use `error.message` from props so it displays the
   real error text.

   Apply this fix?"

   [Yes / Let me see the code first / Different approach]

4. User confirms → Apply fix
   - git stash push -m "mocks" (if mocks active)
   - Edit file, commit: "fix(04-uat): display actual error message"
   - git stash pop (restore mocks)

5. User re-tests
   "Please test the error message again. Does it show the correct text now?"

6. User confirms → Mark test as passed, continue
```

**Fix report format:** Plain language explanation — what's wrong, why, and how to fix it. Include file paths and line numbers naturally in the explanation. No diff preview; user can request to see the code if they want more detail before approving.

#### Escalation to Subagent

```
1. User reports: "Comments don't refresh after posting"

2. Main context: Quick investigation
   - Grep "comment" → 15 files
   - Read CommentList.tsx → no obvious issue
   - Read useComments hook → complex state logic
   - Still unclear after 3 checks

3. Main context: Escalate
   "This needs deeper investigation. Spawning debug agent..."

4. Spawn Verify-Fixer subagent with:
   - Issue: "Comments don't refresh after posting"
   - Expected: "New comment appears immediately in list"
   - Actual: "Must refresh page to see new comment"
   - Relevant files: [CommentList.tsx, useComments.ts, commentApi.ts]
   - Mock state: "standard_user" (for context)

5. Subagent investigates (fresh 200k context)
   - Uses gsd-debugger patterns (hypothesis testing, evidence gathering)
   - Finds root cause: useEffect missing dependency
   - Commits fix

6. Subagent returns:

   "Fixed. The issue was in `useComments.ts` line 34 — the useEffect was
   missing `commentCount` in its dependency array. React wasn't re-rendering
   when new comments were added because it didn't know the count changed.

   I added `commentCount` to the dependency array. Commit: abc123f

   Please re-test: post a comment, it should appear immediately now."

7. User re-tests → confirms fixed → continue
```

### State Management

#### UAT.md Structure (Revised)

```markdown
---
status: testing | fixing | complete
phase: XX-name
source: [SUMMARY.md files]
started: [ISO timestamp]
updated: [ISO timestamp]
current_batch: 2
mock_stash: "mocks-batch-2"  # Current stash reference
pre_work_stash: "pre-verify-work"  # User's original work if any
---

## Progress

total: 12
tested: 5
passed: 4
issues: 1
fixing: 1
pending: 7
skipped: 0

## Current Batch

batch: 2 of 4
name: "Error States"
mock_type: error_state
tests: [4, 5, 6, 7]
status: testing

## Tests

### 1. Login success
expected: Valid credentials → dashboard with user name
mock_required: false
result: pass

### 2. Logout
expected: Session cleared, redirected to login
mock_required: false
result: pass

### 3. Remember me checkbox
expected: Enabled checkbox persists login across app restart
mock_required: false
result: pass

### 4. Login error message
expected: Invalid credentials → "Invalid email or password" message
mock_required: true
mock_type: error_state
result: issue
reported: "Shows 'Something went wrong' instead of specific error"
severity: major
fix_status: fixing
fix_commit: null

### 5. Network error handling
expected: No connection → "Check your internet connection" with retry button
mock_required: true
mock_type: error_state
result: pending

...

## Fixes Applied

- commit: abc123f
  test: 4
  description: "Display actual error message from API response"
  files: [src/components/ErrorBanner.tsx]

## Batches

### Batch 1: No Mocks
tests: [1, 2, 3]
status: complete
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

#### Section Update Rules

| Section | Rule | When |
|---------|------|------|
| Frontmatter.status | OVERWRITE | Phase transitions |
| Frontmatter.current_batch | OVERWRITE | Batch transitions |
| Frontmatter.mock_stash | OVERWRITE | Stash operations |
| Progress | OVERWRITE | After each test result |
| Current Batch | OVERWRITE | Batch transitions |
| Tests.{N}.result | OVERWRITE | When user responds |
| Tests.{N}.fix_status | OVERWRITE | During fix flow |
| Tests.{N}.fix_commit | OVERWRITE | After fix committed |
| Fixes Applied | APPEND | After each fix committed |
| Batches.{N}.status | OVERWRITE | Batch transitions |
| Assumptions | APPEND | When test skipped |

#### Resume Behavior

On `/gsd:verify-work` with existing UAT.md:

1. Check `status` — if `complete`, offer to re-run or view results
2. Check `current_batch` — resume from that batch
3. Check `mock_stash` — if exists, `git stash list` to verify, offer to restore
4. Check tests with `result: fixing` — resume fix flow for those
5. Present remaining tests in current batch

### Completion Flow

After all batches complete:

```
1. Discard mocks
   git stash drop  # Remove mock stash permanently

2. Generate UAT fixes patch (if any fixes were made)
   ~/.claude/get-shit-done/scripts/generate-phase-patch.sh ${PHASE} --suffix=uat-fixes

   Output: .planning/phases/{phase_dir}/{phase}-uat-fixes.patch

3. Update UAT.md
   - status: complete
   - Clear current_batch, mock_stash
   - Final summary counts

4. Commit UAT completion
   git add .planning/phases/{phase_dir}/{phase}-UAT.md
   git commit -m "test({phase}): complete UAT - {passed} passed, {fixed} fixed, {skipped} assumptions"

5. Restore user's original work (if any)
   git stash pop  # Only if pre_work_stash exists

6. Present summary

   ## UAT Complete: Phase 04

   - **Passed:** 10
   - **Fixed:** 2 (commits: abc123f, def456a)
   - **Assumptions:** 1

   Patch file: `.planning/phases/04-auth/04-uat-fixes.patch`

   To review the fixes: `cat .planning/phases/04-auth/04-uat-fixes.patch`
```

### Subagent Specifications

#### Mock Generator Subagent

**Purpose:** Generate framework-appropriate mock code for a specific mock type.

**When spawned:** User confirms they want Claude to generate mocks for a batch.

**Prompt template:**

```markdown
You are generating test mocks for manual UI verification.

## Context

Project type: {detected_framework}  # Flutter, React, React Native, etc.
Phase: {phase_name}
Mock type needed: {mock_type}  # error_state, premium_user, empty_response, loading_state

## Tests requiring this mock

{test_list_with_expected_behavior}

## Requirements

1. Create an override file that doesn't require code changes to toggle:
   - Prefer: environment variables, debug flags, or dev-only files
   - Avoid: modifying production code paths extensively

2. If production hooks are needed, make them minimal:
   - Single if-check at service/repository layer
   - Clear comment marking it as test override

3. Provide clear toggle instructions:
   - How to enable each mock state
   - Hot reload / restart requirements
   - How to verify mock is active

4. Output format:
   - Files to create (with full content)
   - Files to modify (with specific edits)
   - User instructions (step by step)

## Constraints

- Mocks will be stashed/unstashed during fix cycles
- Must not interfere with git commit flow
- Should be easy to completely remove (single file delete ideally)
```

**Returns:**

```markdown
## Mock Implementation

### Files Created

**lib/test_overrides.dart**
```dart
{full file content}
```

### Files Modified

**lib/services/user_service.dart** (line 45)
```dart
// Add after imports:
import '../test_overrides.dart';

// Modify getUser():
Future<User> getUser() async {
  if (TestOverrides.forcePremium) {
    return User(isPremium: true, name: 'Test Premium User');
  }
  // ... existing implementation
}
```

### Toggle Instructions

1. Open `lib/test_overrides.dart`
2. Set `forcePremium = true` for premium user state
3. Hot reload the app
4. Verify: User badge shows "Premium" on profile screen
```

#### Verify-Fixer Subagent

**Purpose:** Investigate and fix a single issue that failed lightweight investigation.

**When spawned:** Main context couldn't identify cause in 2-3 checks.

**Prompt template:**

```markdown
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

1. **Investigate** using gsd-debugger patterns:
   - Form specific, falsifiable hypotheses
   - Test one hypothesis at a time
   - Document evidence in your reasoning

2. **When root cause found:**
   - Implement minimal fix
   - Commit with message: `fix({phase}): {description}`
   - Do NOT include mock code in commit

3. **Return format:**

```markdown
## FIX COMPLETE

**Root cause:** {specific cause with evidence}

**Fix applied:** {what was changed}

**Commit:** {hash}

**Files changed:**
- {file}: {change description}

**Re-test instruction:** {specific step for user to verify}
```

4. **If inconclusive after thorough investigation:**

```markdown
## INVESTIGATION INCONCLUSIVE

**Checked:**
- {area}: {finding}

**Remaining possibilities:**
- {hypothesis}

**Recommendation:** {next steps}
```

## Constraints

- Mocks are currently stashed (working tree is clean)
- Commit must be clean (no mock code)
- After you commit, mocks will be restored for user to re-test
- Apply deviation rules: auto-fix bugs, auto-add critical functionality, ask about architectural changes
```

### User Interaction Flow

#### Reduced Decision Points

Current flow has ~25+ decision points. Target: ~10-12.

**Clustered interactions:**

```
1. SETUP (one interaction)
   "Found 12 testables grouped into 4 batches:
    - Batch 1 (No mocks): 3 tests
    - Batch 2 (Error states): 4 tests — needs mock
    - Batch 3 (Premium features): 3 tests — needs mock
    - Batch 4 (Empty states): 2 tests — needs mock

    Start with Batch 1? [Yes / Show test details / Adjust batches]"

2. PER BATCH: Test presentation (one interaction per batch)
   "Batch 2: Error States

    | # | Test | Expected |
    |---|------|----------|
    | 4 | Login error | Shows 'Invalid email or password' |
    | 5 | Network error | Shows 'Check connection' + retry |
    | 6 | Server error | Shows 'Try again later' |
    | 7 | Rate limit | Shows 'Too many attempts' |

    Mock needed. Options:
    1. Generate mocks (Recommended)
    2. I'll set up mocks manually
    3. Skip batch (log as assumptions)"

3. PER BATCH: Results collection (one interaction)
   "Test each item and report results:"
   [AskUserQuestion with 4 questions, one per test]

4. PER ISSUE: Fix confirmation (one interaction per issue)
   "Found issue in ErrorBanner.tsx — hardcoded message.
    Fix: Use error.message from props.

    [Apply fix / Show me the code / Different approach]"

5. PER ISSUE: Re-test confirmation (one interaction)
   "Fix applied. Please re-test error message display.
    [Pass / Still broken / New issue]"

6. CLEANUP (one interaction)
   "All batches complete!
    - 11 passed
    - 1 assumption (skipped network error — couldn't simulate offline)

    Cleaning up mocks and finalizing...
    [Done / Review fixes first]"
```

## File Changes Required

### Commands

**`commands/gsd/verify-work.md`**

Changes:
- Update `<process>` to reflect new flow (classify → batch → mock → test → fix loop)
- Add mock lifecycle steps
- Add threshold-based investigation step
- Update success criteria

### Workflows

**`get-shit-done/workflows/verify-work.md`**

Major rewrite:
- Add `<step name="classify_tests">` for mock requirement analysis
- Add `<step name="create_batches">` for grouping logic
- Add `<step name="mock_lifecycle">` with stash protocol
- Replace `diagnose_issues` step with inline `investigate_issue` step
- Add `<step name="fix_issue">` with threshold-based escalation
- Add `<step name="cleanup">` for stash cleanup and summary

**`get-shit-done/workflows/generate-mocks.md`** (NEW)

New file:
- Mock generation patterns (framework-agnostic)
- Override file templates
- Production hook patterns (minimal)
- Toggle instruction templates

### Templates

**`get-shit-done/templates/UAT.md`**

Changes:
- Add `current_batch`, `mock_stash`, `pre_work_stash` to frontmatter
- Add `mock_required`, `mock_type` to test entries
- Add `fix_status`, `fix_commit` to test entries
- Add `Fixes Applied` section
- Add `Batches` section with per-batch status
- Update section rules

### Agents

**`agents/gsd-verify-fixer.md`** (NEW)

New agent:
- Inherits investigation patterns from gsd-debugger
- Focused on single-issue fix (not full debug session)
- Includes deviation rules (auto-fix bugs, ask about architecture)
- Returns structured fix result

**`agents/gsd-mock-generator.md`** (NEW)

New agent:
- Framework detection logic
- Mock pattern templates per framework
- Override file generation
- Production hook generation (minimal)

### References

**`get-shit-done/references/mock-patterns.md`** (NEW)

New reference:
- Mock philosophy (temporary scaffolding)
- Git stash lifecycle
- Framework-specific patterns (Flutter, React, React Native, web)
- Conflict resolution

### Scripts

**`scripts/generate-phase-patch.sh`**

Changes:
- Add optional `--suffix` parameter for UAT fixes variant
- When `--suffix=uat-fixes`: look for commits matching `({phase}-uat)` pattern
- Output to `{phase}-{suffix}.patch` instead of `{phase}-changes.patch`

Example usage:
```bash
# Existing behavior (all phase commits)
./scripts/generate-phase-patch.sh 04

# New: UAT fixes only
./scripts/generate-phase-patch.sh 04 --suffix=uat-fixes
```

## Migration Notes

### Backwards Compatibility

- Existing UAT.md files (old format) will be detected by missing `current_batch` field
- On detection: offer to migrate or start fresh
- Migration: add new fields with defaults, preserve existing test results

### Deprecation

- `get-shit-done/workflows/diagnose-issues.md` — no longer needed for verify-work (kept for standalone `/gsd:debug` use)
- Parallel debugger spawning replaced by inline investigation + single fixer escalation

### Testing the Redesign

Before release, test with:
1. Phase with no mock requirements (should skip mock flow entirely)
2. Phase with single mock type (one batch needs mocks)
3. Phase with multiple mock types (multiple batches need different mocks)
4. Issue that resolves with lightweight investigation
5. Issue that requires fixer subagent escalation
6. Context reset mid-batch (resume from UAT.md)
7. Stash conflict scenario (fix touches mock file)

## Resolved Design Decisions

1. **Framework detection**: Detect from PROJECT.md (already contains project description). No need to ask user.

2. **Batch reordering**: Not supported. Keep flow simple — batches execute in predetermined order.

3. **Partial batch completion**: No explicit support. UAT.md updates after each complete batch. Edge cases handled conversationally.

4. **Fix reporting**: Structured report (cause + suggested fix + file:line references), not a diff preview. User confirms before fix is applied.

---

## Summary

This redesign transforms verify-work from a logging-focused command into a complete verify-and-fix session:

| Aspect | Before | After |
|--------|--------|-------|
| Session count | 3+ (verify → plan → execute → verify) | 1 |
| Mock support | None | Built-in with git stash lifecycle |
| Fix timing | Deferred to separate phase | Immediate while mocks active |
| Investigation | Always spawn parallel debuggers | Threshold-based (quick check first) |
| Context usage | High (holds all issues) | Low (orchestration only, ~40%) |
| User decisions | ~25+ per phase | ~10-12 per phase |

The key insight: **keep mocks as uncommitted/stashed changes, fix in clean commits, restore mocks for re-testing**. This eliminates mock-in-commit complexity while enabling test-fix-retest loops.
