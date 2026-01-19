---
name: gsd:verify-work
description: Validate built features through batched UAT
argument-hint: "[phase number, e.g., '4']"
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Edit
  - Write
  - Task
  - AskUserQuestion
---

<objective>
Validate built features through batched testing with persistent state.

Purpose: Confirm what Claude built actually works from user's perspective. Tests presented in batches of 4 using AskUserQuestion. Optimized for the common case: most tests pass.

Output: {phase}-UAT.md tracking all test results. If issues found: diagnosed gaps with root causes ready for /gsd:plan-phase --gaps. If tests skipped: assumptions logged for milestone audit.
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/verify-work.md
@~/.claude/get-shit-done/templates/UAT.md
@~/.claude/get-shit-done/workflows/diagnose-issues.md
</execution_context>

<context>
Phase: $ARGUMENTS (optional)
- If provided: Test specific phase (e.g., "4")
- If not provided: Check for active sessions or prompt for phase

@.planning/STATE.md
@.planning/ROADMAP.md
</context>

<process>
1. Check for active UAT sessions (resume or start new)
2. Find SUMMARY.md files for the phase
3. Extract testable deliverables (user-observable outcomes)
4. Create {phase}-UAT.md with test list
5. Present tests in batches of 4 using AskUserQuestion:
   - Options: Pass / Can't test / Skip / Other (for issues)
   - "Pass" = verified, "Can't test" = blocked (re-test later)
   - "Skip" = assumption (logged), "Other" = issue (severity inferred)
6. Update UAT.md after each batch (checkpoint)
7. On completion: commit, present summary
8. If issues found:
   - Spawn parallel debug agents to diagnose root causes
   - Update UAT.md with diagnoses
   - Update STATE.md with blockers
   - Present next steps with `/gsd:plan-phase --gaps`
</process>

<anti_patterns>
- Don't ask severity — infer from description
- Don't present more than 4 tests at a time — batch in groups of 4
- Don't run automated tests — this is manual user validation
- Don't fix issues during testing — log as gaps, diagnose after all tests complete
- Don't re-present skipped tests — assumptions stand until explicitly revisited
</anti_patterns>

<success_criteria>
- [ ] UAT.md created with tests from SUMMARY.md
- [ ] Tests presented in batches of 4 using AskUserQuestion
- [ ] Responses processed: pass/issue/blocked/skipped
- [ ] Severity inferred, never asked
- [ ] File written after each batch (checkpoint)
- [ ] Blocked tests re-presented on subsequent runs
- [ ] Skipped tests logged to Assumptions section
- [ ] Committed on completion
- [ ] If issues: parallel debug agents diagnose root causes
- [ ] If issues: UAT.md updated with root_cause, artifacts, missing
- [ ] If issues: STATE.md updated with phase blockers
- [ ] Clear next steps: /gsd:plan-phase --gaps with diagnostic context
</success_criteria>
