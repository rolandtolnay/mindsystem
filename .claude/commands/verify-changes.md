---
name: verify-changes
description: Verify code changes actually achieve requirements/proposal using goal-backward verification
argument-hint: <what to verify - requirements, proposal, or goals>
---

<objective>
Verify that code changes actually achieve what was intended, not just that tasks were completed.

This command uses **goal-backward verification**: start from what SHOULD be true if requirements are met, then verify the code actually delivers it. This catches gaps where code exists but doesn't fulfill the goal.

**Core principle:** Task completion ≠ Goal achievement. A task "create login form" can be marked complete when the form is a placeholder. The task was done—a file was created—but the goal "user can log in" was not achieved.
</objective>

<context>
**User's verification request:**
$ARGUMENTS

**Current git status:**
!`git status --short`
</context>

<process>

## Phase 1: Establish Verification Scope

### Step 1.1: Clarify Change Scope

Use AskUserQuestion to determine what code changes to verify:

```
Question: "What code changes should I verify?"
Options:
- "Uncommitted changes" - Verify current uncommitted work (git diff)
- "Specific commits" - Verify a commit or range (ask for commit refs)
- "All changes on branch" - Verify all commits since branching from main
```

Based on user selection, gather the relevant changes:
- Uncommitted: `git diff` and `git diff --cached`
- Specific commits: `git show <commit>` or `git diff <from>..<to>`
- Branch changes: `git diff main...HEAD`

### Step 1.2: Clarify Requirements

Analyze the user's verification request (`$ARGUMENTS`). If any of these are unclear, use AskUserQuestion to clarify:

**Must be clear before proceeding:**
1. What is the goal/outcome being verified? (not tasks, but user-observable results)
2. What files or areas are expected to be affected?
3. Are there specific behaviors that must work?

**Keep asking until you can state:**
- 3-7 observable truths that must be TRUE for the goal to be achieved
- Each truth should be testable/verifiable

Example clarifying questions:
- "What should a user be able to DO after these changes?"
- "What specific behavior should work that didn't before?"
- "Are there edge cases or error states that must be handled?"

## Phase 2: Derive Must-Haves (Goal-Backward)

### Step 2.1: Derive Observable Truths

From the clarified requirements, derive observable truths:

**Ask:** "What must be TRUE for this goal to be achieved?"

List 3-7 truths from the user's perspective. Each truth should be:
- Observable (can be seen/tested by using the app)
- Specific (not vague like "works correctly")
- Testable (clear pass/fail criteria)

Example truths for "user authentication":
- "User can submit login form with email and password"
- "Valid credentials result in successful login"
- "Invalid credentials show error message"
- "Session persists across page refreshes"

### Step 2.2: Derive Required Artifacts

For each truth, ask: "What must EXIST for this truth to hold?"

Map truths to concrete files:
- Components, routes, utilities
- API endpoints
- Database schemas/migrations
- Configuration files

Be specific: `src/components/LoginForm.tsx`, not "login component"

### Step 2.3: Derive Key Links

For each artifact, ask: "What must be CONNECTED for this to function?"

Identify critical wiring:
- Component → API (fetch calls)
- API → Database (queries)
- Form → Handler (onSubmit)
- State → Render (data displayed)

**This is where stubs hide.** Pieces exist but aren't connected.

## Phase 3: Verify Against Codebase

Use Explore agents (Task tool with subagent_type=Explore) to locate and analyze code. Do NOT trust file existence alone.

### Step 3.1: Verify Artifacts (Three Levels)

For each required artifact:

**Level 1: Existence**
- Does the file exist?
- If MISSING → record and continue

**Level 2: Substantive**
- Is it a real implementation or a stub?
- Check minimum lines (component: 15+, API route: 10+, hook: 10+)
- Scan for stub patterns:
  - `TODO`, `FIXME`, `placeholder`, `not implemented`
  - `return null`, `return {}`, `return []`
  - `console.log` only implementations
  - Empty handlers: `onClick={() => {}}`

**Level 3: Wired**
- Is it imported and used?
- Is it connected to the system?
- Check: imports exist, component rendered, API called, handler connected

**Artifact status:**
| Exists | Substantive | Wired | Status |
|--------|-------------|-------|--------|
| ✓ | ✓ | ✓ | ✓ VERIFIED |
| ✓ | ✓ | ✗ | ⚠️ ORPHANED |
| ✓ | ✗ | - | ✗ STUB |
| ✗ | - | - | ✗ MISSING |

### Step 3.2: Verify Key Links

For each critical connection, verify it exists and functions:

**Component → API:**
- Fetch/axios call to the endpoint exists
- Response is awaited and used (not ignored)
- Data flows to state or render

**API → Database:**
- Query/mutation exists
- Result is returned (not static response)

**Form → Handler:**
- onSubmit connected to real handler
- Handler makes API call (not just console.log or preventDefault only)

**State → Render:**
- State variable exists
- State is displayed in JSX (not hardcoded placeholder)

### Step 3.3: Verify Observable Truths

For each truth from Step 2.1:
1. Identify which artifacts support it
2. Check artifact status from Step 3.1
3. Check link status from Step 3.2
4. Determine truth status:

- ✓ VERIFIED: All supporting artifacts pass all levels
- ✗ FAILED: One or more artifacts missing, stub, or unwired
- ? UNCERTAIN: Cannot verify programmatically (needs manual test)

## Phase 4: Anti-Pattern Scan

Scan all changed files for problematic patterns:

**Blockers (prevent goal achievement):**
- Placeholder renders: `return <div>Placeholder</div>`
- Empty handlers: `onSubmit={() => {}}`
- Hardcoded data where dynamic expected
- API returning static instead of query results

**Warnings (indicate incomplete):**
- TODO/FIXME comments
- console.log statements
- Commented-out code
- `any` types in TypeScript

**Categorize findings:**
- 🛑 Blocker: Prevents goal achievement
- ⚠️ Warning: Indicates incomplete
- ℹ️ Info: Notable but not problematic

## Phase 5: Determine Overall Status

**PASSED:** All truths verified, no blockers
**GAPS FOUND:** One or more truths failed or blockers found
**NEEDS MANUAL TEST:** Automated checks pass but some truths need human verification

</process>

<output_format>

## Verification Summary

**Scope:** [uncommitted changes | commits X..Y | branch changes]
**Requirements:** [brief summary of what was being verified]
**Status:** [PASSED | GAPS FOUND | NEEDS MANUAL TEST]
**Score:** [N/M truths verified]

---

## Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | [truth] | ✓/✗/? | [why] |

---

## Artifacts Verified

| Artifact | Exists | Substantive | Wired | Status |
|----------|--------|-------------|-------|--------|
| `path` | ✓/✗ | ✓/✗ | ✓/✗ | status |

---

## Key Links

| From | To | Status | Issue |
|------|----|--------|-------|
| Component | API | ✓/✗ | [if broken] |

---

## Anti-Patterns Found

| File | Line | Pattern | Severity |
|------|------|---------|----------|
| `path` | N | pattern | 🛑/⚠️/ℹ️ |

---

## Action Items (if gaps found)

Numbered list of specific things to fix:

1. **[Truth that failed]** — [reason]
   - [ ] [Specific action to take]
   - [ ] [Another specific action]

2. **[Another gap]** — [reason]
   - [ ] [What to do]

---

## Manual Testing Required (if applicable)

Things that need human verification:
- [ ] [What to test and expected behavior]

</output_format>

<success_criteria>
- Change scope clarified with user (uncommitted vs commits)
- Requirements clarified until 3-7 observable truths derived
- All truths verified at artifact level (exists, substantive, wired)
- Key links verified (component→API, API→DB, form→handler, state→render)
- Anti-patterns scanned in changed files
- Clear status determined (PASSED / GAPS FOUND / NEEDS MANUAL TEST)
- If gaps found: numbered action items provided
- User has clear understanding of what works and what doesn't
</success_criteria>
