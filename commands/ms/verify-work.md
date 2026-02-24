---
name: ms:verify-work
description: Validate built features through batched UAT with inline fixing
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
Validate built features through batched testing with mock support and inline fixing.

Purpose: Confirm what Claude built actually works from user's perspective. Tests presented in batches of 4 using AskUserQuestion. Issues can be fixed inline during the same session — no context switching to separate plan/execute phases.

Output: {phase}-UAT.md tracking all test results. Fixes committed with `fix({phase}-uat):` prefix. Patch file generated for all UAT fixes.
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/verify-work.md
@~/.claude/mindsystem/templates/UAT.md
</execution_context>

<context>
Phase: $ARGUMENTS (optional)
- If provided: Test specific phase (e.g., "4")
- If not provided: Check for active sessions or prompt for phase

@.planning/STATE.md
@.planning/ROADMAP.md
@.planning/PROJECT.md
</context>

<process>
1. **Check dirty tree** — If uncommitted changes, ask: stash / commit / abort
2. **Check for active UAT sessions** — Resume or start new
3. **Find SUMMARY.md files** for the phase
4. **Extract testable deliverables** from summaries
5. **Classify tests by mock requirements** — Use SUMMARY.md mock_hints when available; classify inline with keyword heuristics when absent. Confirm data availability with user before batching.
6. **Group into batches** — By mock type, max 4 per batch, no-mock tests first
   - If any tests require transient_state mocks: Read `~/.claude/mindsystem/references/mock-patterns.md` for delay strategies
7. **For each batch:**
   - If mock needed: Apply inline mocks (1-4 direct edits, 5+ via ms-mock-generator subagent), tell user to hot reload
   - Present tests via AskUserQuestion (Pass / Can't test / Skip / Other)
   - Process results, update UAT.md
   - **For each issue found:**
     - Lightweight investigation (2-3 tool calls)
     - If simple: Fix inline, commit, ask for re-test
     - If complex: Spawn ms-verify-fixer subagent
     - 2 retries on failed re-test, then offer options
8. **On batch transition:**
   - If new mock_type: Revert old mocks (`git checkout -- <mocked_files>`), apply new ones
   - If same mock_type: Keep mocks active
9. **On completion:**
   - Revert all mocks (`git checkout -- <mocked_files>`)
   - Generate UAT fixes patch
   - Restore user's pre-existing work (if stashed)
   - Commit UAT.md, present summary
   - **Update knowledge pitfalls** — if significant UAT issues (blocker/major) were fixed, append pitfall entries to relevant knowledge files

10. **Update last command:** `ms-tools set-last-command "ms:verify-work $ARGUMENTS"`

11. **Present next steps**
    - If this was the last phase in milestone: suggest `/ms:audit-milestone`
    - If more phases remain: Read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions to present "Next Up" with pre-work context for the next phase
</process>

<anti_patterns>
- Don't ask severity — infer from description
- Don't present more than 4 tests at a time
- Don't run automated tests — this is manual user validation
- Don't skip investigation — always try 2-3 tool calls before escalating
- Don't fix complex issues inline — spawn fixer subagent for multi-file or architectural changes
- Don't commit mock code — stash mocked files before fixing, restore after
- Don't re-present skipped tests — assumptions stand
</anti_patterns>

<success_criteria>
- [ ] Mocks stashed before fixing, restored after (git stash push/pop cycle)
- [ ] Stash conflicts auto-resolved to fix version (git checkout --theirs)
- [ ] Blocked tests re-presented after blocking issues resolved
- [ ] Failed re-tests get 2 retries then options (tracked via retry_count)
- [ ] All mocks reverted on completion (git checkout -- <mocked_files>)
- [ ] UAT fixes patch generated
- [ ] User's pre-existing work restored from stash
</success_criteria>
