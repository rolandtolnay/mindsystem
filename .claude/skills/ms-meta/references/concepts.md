<concepts>

<plans_as_prompts>
## Plans ARE Prompts

PLAN.md is not a document that gets transformed into a prompt.
PLAN.md IS the prompt.

**What this means:**
- Write tasks as you want Claude to execute them
- Include exact commands, file paths, expected outputs
- @-references load context lazily
- Verification is executable, not descriptive

**Plan anatomy:**
```xml
<objective>
What to build and why
</objective>

<execution_context>
@~/.claude/get-shit-done/workflows/execute-plan.md
@~/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/STATE.md
@src/lib/db.ts  <!-- Only what's actually needed -->
</context>

<tasks>
<task type="auto">
  <name>Task 1: Create login endpoint</name>
  <files>src/app/api/auth/login/route.ts</files>
  <action>
    POST endpoint accepting {email, password}.
    Use jose for JWT (not jsonwebtoken — CommonJS issues).
    Return httpOnly cookie on success.
  </action>
  <verify>curl returns 200 with Set-Cookie header</verify>
  <done>Valid → 200 + cookie. Invalid → 401.</done>
</task>
</tasks>
```

**Task specificity levels:**

| Level | Example | Problem |
|-------|---------|---------|
| Too vague | "Add authentication" | Claude must guess what/how |
| Just right | "POST endpoint with JWT using jose library" | Claude can execute immediately |
| Too detailed | Actual code in action | Wastes context, trust Claude |

**The test:** Can Claude read the plan and start implementing without asking clarifying questions? If not, task is too vague.
</plans_as_prompts>

<checkpoint_system>
## Checkpoint System

**Core principle:** Claude automates everything with CLI/API. Checkpoints are for verification and decisions, not manual work.

**Checkpoint types (by frequency):**

| Type | Usage | Purpose |
|------|-------|---------|
| `checkpoint:human-verify` | 90% | Human confirms visual/UX after Claude built it |
| `checkpoint:decision` | 9% | Human makes architecture/technology choice |
| `checkpoint:human-action` | 1% | Truly unavoidable manual (email links, 2FA codes) |

**Human-verify example:**
```xml
<task type="auto">
  <name>Deploy to Vercel</name>
  <action>Run `vercel --yes`. Capture URL.</action>
  <verify>vercel ls shows deployment, curl returns 200</verify>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <what-built>Deployed to https://myapp.vercel.app</what-built>
  <how-to-verify>
    Visit URL. Confirm:
    - Homepage loads
    - No console errors
    - Navigation works
  </how-to-verify>
  <resume-signal>Type "approved" or describe issues</resume-signal>
</task>
```

**Decision example:**
```xml
<task type="checkpoint:decision" gate="blocking">
  <decision>Select authentication provider</decision>
  <context>Need user auth. Three options with different tradeoffs.</context>
  <options>
    <option id="supabase">
      <name>Supabase Auth</name>
      <pros>Built-in, free tier</pros>
      <cons>Less customizable</cons>
    </option>
    <!-- more options -->
  </options>
  <resume-signal>Select: supabase, clerk, or nextauth</resume-signal>
</task>
```

**Authentication gates:**

When Claude hits auth error during automation:
1. STOP (don't retry repeatedly)
2. Create checkpoint:human-action dynamically
3. User authenticates
4. Claude retries
5. Continues

This is NOT a failure — it's expected flow for first-time tool use.

**Anti-patterns:**
- Asking human to deploy (use CLI)
- Asking human to create .env (use Write tool)
- Checkpoint after every task (verification fatigue)
</checkpoint_system>

<deviation_rules>
## Deviation Rules

While executing, Claude discovers unplanned work. Rules determine what to do automatically.

**Rule 1: Auto-fix bugs**
- Trigger: Code doesn't work (wrong output, errors, security vulnerabilities)
- Action: Fix immediately, track for SUMMARY
- No permission needed

**Rule 2: Auto-add missing critical functionality**
- Trigger: Missing essential features (no error handling, no validation, no auth checks)
- Action: Add immediately, track for SUMMARY
- Critical = required for correct/secure/performant operation
- No permission needed

**Rule 3: Auto-fix blocking issues**
- Trigger: Can't complete task (missing dep, wrong types, broken imports)
- Action: Fix to unblock, track for SUMMARY
- No permission needed

**Rule 4: Ask about architectural changes**
- Trigger: Fix requires significant structural change (new tables, new services, changing patterns)
- Action: STOP, return checkpoint, wait for decision
- User decision required

**Priority:** If Rule 4 applies, STOP. Otherwise auto-fix with Rules 1-3.

**Edge cases:**
- "Missing validation" → Rule 2 (critical security)
- "Crashes on null" → Rule 1 (bug)
- "Need new table" → Rule 4 (architectural)
- "Need new column" → Rules 1-2 (depends on context)
</deviation_rules>

<wave_execution>
## Wave-Based Parallel Execution

Plans have `wave` number in frontmatter (pre-computed during planning):

```yaml
---
wave: 1           # First wave — no dependencies
depends_on: []
---
```

**Execution flow:**
1. Orchestrator discovers all plans in phase
2. Groups by wave number
3. Wave 1: Spawn all plans as parallel subagents
4. Wait for wave 1 to complete
5. Wave 2: Spawn all plans as parallel subagents
6. Repeat until all waves complete

**Wave assignment rules:**
- Plans with no dependencies → Wave 1
- Plans depending on wave 1 plans → Wave 2
- Plans depending on wave 2 plans → Wave 3
- Plans with `autonomous: false` → Normal wave but pause at checkpoints

**Benefits:**
- Independent work runs in parallel
- Each agent has fresh 200k context
- Orchestrator stays lean (<15% context)
- No polling — Task tool blocks until completion
</wave_execution>

<state_management>
## State Management

**STATE.md** is the project's living memory.

**Purpose:**
- Instant context restoration for new sessions
- Track position (phase, plan, status)
- Accumulate decisions and blockers
- Enable resumption after interruption

**Sections:**
```markdown
## Project Reference
See: .planning/PROJECT.md
Core value: [one-liner]
Current focus: [phase name]

## Current Position
Phase: X of Y (phase-name)
Plan: A of B
Status: [Ready to plan / In progress / Phase complete]
Progress: [░░░░░████░░] 40%

## Performance Metrics
Total plans: N
Average duration: X min
Trend: [Improving / Stable / Degrading]

## Accumulated Context
### Decisions
- [Phase X]: Used jose for JWT
- [Phase Y]: Chose Supabase for auth

### Pending Todos
3 pending — see /gsd:check-todos

### Blockers/Concerns
- [Phase 2]: Need API key before deployment

## Session Continuity
Last session: YYYY-MM-DD HH:MM
Stopped at: Completed plan 01-02
Resume file: None
```

**Size constraint:** <100 lines. It's a digest, not an archive.

**Update triggers:**
- After each plan execution
- After phase transitions
- When decisions are made
- When blockers discovered
</state_management>

<summary_system>
## SUMMARY.md System

Created after each plan execution. Provides compressed history for future context.

**Key features:**

1. **Machine-readable frontmatter:**
```yaml
---
phase: 01-foundation
plan: 02
subsystem: auth
tags: [jwt, jose, cookies]
requires:
  - phase: 01-foundation-01
    provides: User model
provides:
  - JWT authentication endpoints
affects: [dashboard, protected-routes]
tech-stack:
  added: [jose]
  patterns: [httpOnly cookies, refresh rotation]
key-files:
  created: [src/app/api/auth/login/route.ts]
  modified: [prisma/schema.prisma]
duration: 23min
completed: 2025-01-15
---
```

2. **Substantive one-liner:**
- Good: "JWT auth with refresh rotation using jose library"
- Bad: "Phase complete"

3. **Deviation documentation:**
```markdown
## Deviations from Plan

### Auto-fixed Issues
**1. [Rule 2 - Missing Critical] Added password hashing**
- Found during: Task 2
- Issue: Plan didn't specify hashing
- Fix: Added bcrypt with salt rounds 10
- Files: src/lib/auth.ts
- Commit: abc123f
```

4. **Next phase readiness:**
- What's ready
- Blockers for next phase
</summary_system>

<atomic_commits>
## Atomic Git Commits

Each task gets its own commit immediately after completion.

**Format:**
```
{type}({phase}-{plan}): {concise description}

- Key change 1
- Key change 2
```

**Types:**
| Type | When |
|------|------|
| `feat` | New feature |
| `fix` | Bug fix |
| `test` | Tests only (TDD RED) |
| `refactor` | No behavior change |
| `docs` | Documentation |
| `chore` | Config/deps |

**Benefits:**
- `git bisect` finds exact failing task
- Each task independently revertable
- Clear history for Claude in future sessions
- `git blame` traces lines to task context

**Rules:**
- Stage files individually (never `git add .`)
- Commit immediately after task verification
- TDD tasks may have 2-3 commits (test/feat/refactor)
- Metadata commit after SUMMARY.md created
</atomic_commits>

<tdd_integration>
## TDD Integration

TDD features get dedicated plans because the cycle (RED → GREEN → REFACTOR) is too heavy to embed in multi-task plans.

**Detection heuristic:**
> Can you write `expect(fn(input)).toBe(output)` before writing `fn`?

Yes → TDD plan (one feature per plan)
No → Standard plan (add tests after if needed)

**TDD plan structure:**
```yaml
---
type: tdd
---
```

```xml
<objective>
Implement [feature] using TDD
</objective>

<behavior>
Given [input], when [action], then [output]
</behavior>

<implementation>
How to make tests pass
</implementation>
```

**TDD commits:**
- RED: `test({phase}-{plan}): add failing test for [feature]`
- GREEN: `feat({phase}-{plan}): implement [feature]`
- REFACTOR: `refactor({phase}-{plan}): clean up [feature]` (if needed)
</tdd_integration>

</concepts>
