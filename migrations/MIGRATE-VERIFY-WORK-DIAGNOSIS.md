# Migration: Verify-Work Auto-Diagnosis

Adds automatic root cause diagnosis when UAT finds issues. Debug agents investigate each issue in parallel, then present diagnosed gaps ready for manual `/gsd:plan-phase --gaps`.

**Scope:** Diagnosis only. Planning remains manual (your interactive planning philosophy preserved).

---

## Prerequisites

- Vanilla fork at v1.5.17 or with previous migrations applied
- Familiarity with commands/gsd/verify-work.md and workflows/verify-work.md

---

## What This Migration Does

| Before | After |
|--------|-------|
| UAT finds issues → logged to UAT.md | UAT finds issues → logged to UAT.md |
| "Run /gsd:plan-phase --gaps" (you guess at causes) | Parallel debug agents investigate each issue |
| | UAT.md updated with root causes, artifacts, missing items |
| | "Run /gsd:plan-phase --gaps" (with precise diagnoses) |

**The improvement:** Fix plans are based on diagnosed root causes, not symptoms.

---

## Part 1: Add the gsd-debugger Agent

Create `~/.claude/agents/gsd-debugger.md`:

```bash
curl -sL https://raw.githubusercontent.com/glittercowboy/get-shit-done/main/agents/gsd-debugger.md \
  -o ~/.claude/agents/gsd-debugger.md
```

Verify:
```bash
head -10 ~/.claude/agents/gsd-debugger.md
```

Should show:
```yaml
---
name: gsd-debugger
description: Investigates bugs using scientific method...
```

---

## Part 2: Add the diagnose-issues Workflow

Create `~/.claude/get-shit-done/workflows/diagnose-issues.md`:

```bash
curl -sL https://raw.githubusercontent.com/glittercowboy/get-shit-done/main/get-shit-done/workflows/diagnose-issues.md \
  -o ~/.claude/get-shit-done/workflows/diagnose-issues.md
```

Verify:
```bash
head -5 ~/.claude/get-shit-done/workflows/diagnose-issues.md
```

Should show:
```xml
<purpose>
Orchestrate parallel debug agents to investigate UAT gaps and find root causes.
```

---

## Part 3: Update verify-work.md Command

In `~/.claude/commands/gsd/verify-work.md`:

### 3.1 Add Task to allowed-tools

```yaml
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Edit
  - Write
  - Task          # ← ADD THIS
```

### 3.2 Update objective output description

Find:
```markdown
Output: {phase}-UAT.md tracking all test results, gaps logged for /gsd:plan-phase --gaps
```

Replace with:
```markdown
Output: {phase}-UAT.md tracking all test results. If issues found: diagnosed gaps with root causes ready for /gsd:plan-phase --gaps
```

### 3.3 Update process step 7

Find:
```markdown
7. On completion: commit, present summary, offer next steps
```

Replace with:
```markdown
7. On completion: commit, present summary
8. If issues found:
   - Spawn parallel debug agents to diagnose root causes
   - Update UAT.md with diagnoses
   - Update STATE.md with blockers
   - Present next steps with `/gsd:plan-phase --gaps`
```

### 3.4 Update anti-patterns

Find:
```markdown
- Don't fix issues during testing — log as gaps for /gsd:plan-phase --gaps
```

Replace with:
```markdown
- Don't fix issues during testing — log as gaps, diagnose after all tests complete
```

### 3.5 Add execution_context reference

After the existing `<execution_context>` references, add:
```markdown
@~/.claude/get-shit-done/workflows/diagnose-issues.md
```

### 3.6 Update success_criteria

Find:
```markdown
- [ ] Clear next steps based on results
```

Replace with:
```markdown
- [ ] If issues: parallel debug agents diagnose root causes
- [ ] If issues: UAT.md updated with root_cause, artifacts, missing
- [ ] If issues: STATE.md updated with phase blockers
- [ ] Clear next steps: /gsd:plan-phase --gaps with diagnostic context
```

---

## Part 4: Update verify-work.md Workflow

In `~/.claude/get-shit-done/workflows/verify-work.md`:

### 4.1 Add reference after purpose

After the `</purpose>` tag, add:
```xml
<execution_context>
@~/.claude/get-shit-done/workflows/diagnose-issues.md
</execution_context>
```

### 4.2 Update the offer_gap_closure step

Find the `<step name="offer_gap_closure">` section and replace it entirely with:

```xml
<step name="diagnose_gaps">
**Auto-diagnose root causes:**

Display:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► DIAGNOSING ISSUES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Spawning {N} debug agents in parallel...
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

Proceed to offer_next_steps.
</step>

<step name="offer_next_steps">
**Present diagnosis and next steps:**

Display:
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 GSD ► DIAGNOSIS COMPLETE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

**Phase {X}: {Name}**

{N}/{M} tests passed
{X} issues diagnosed

### Diagnosed Gaps

| Gap | Root Cause | Files |
|-----|------------|-------|
| {truth 1} | {root_cause} | {files} |
| {truth 2} | {root_cause} | {files} |

Debug sessions: .planning/debug/

───────────────────────────────────────────────────────────────

## ▶ Next Up

**Plan fixes** — create fix plans from diagnosed gaps

`/gsd:plan-phase {phase} --gaps`

<sub>`/clear` first → fresh context window</sub>

───────────────────────────────────────────────────────────────

**Also available:**
- `cat .planning/phases/{phase_dir}/{phase}-UAT.md` — review full diagnosis
- `/gsd:debug {issue}` — investigate specific issue further

───────────────────────────────────────────────────────────────
```
</step>
```

### 4.3 Update success_criteria

Find:
```markdown
- [ ] Clear next steps based on results (plan-phase --gaps if issues)
```

Replace with:
```markdown
- [ ] If issues: parallel debug agents diagnose root causes
- [ ] If issues: UAT.md updated with root_cause, artifacts, missing
- [ ] If issues: STATE.md updated with phase blockers
- [ ] Clear next steps: /gsd:plan-phase --gaps with diagnostic context
```

---

## Part 5: Create .planning/debug Directory

The debug agents write session files to `.planning/debug/`. Add to your `.gitignore` if you want to exclude debug sessions from commits, or keep them for audit trail.

Optional `.gitignore` addition:
```bash
# Exclude active debug sessions (resolved ones are committed)
.planning/debug/*.md
!.planning/debug/resolved/
```

---

## Verification

1. Run UAT with a known failing test:
   ```
   /gsd:verify-work 3
   ```

2. Report an issue when prompted (describe something broken)

3. After all tests complete, verify:
   - Debug agents spawn in parallel
   - Each agent investigates and returns root cause
   - UAT.md is updated with `root_cause`, `artifacts`, `missing` fields
   - STATE.md shows blockers
   - Next step shows `/gsd:plan-phase 3 --gaps`

4. Check UAT.md structure:
   ```bash
   grep -A5 "root_cause:" .planning/phases/*-*/*-UAT.md
   ```

---

## Rollback

Remove the added files:
```bash
rm ~/.claude/agents/gsd-debugger.md
rm ~/.claude/get-shit-done/workflows/diagnose-issues.md
```

Revert command and workflow changes manually, or restore from git.

---

## How It Works

### Before (Vanilla)

```
User: "The comment doesn't refresh after posting"
     ↓
UAT.md logs: truth="Comment appears immediately" status=failed reason="doesn't refresh"
     ↓
"Run /gsd:plan-phase --gaps" (planner guesses at cause)
```

### After (With Auto-Diagnosis)

```
User: "The comment doesn't refresh after posting"
     ↓
UAT.md logs: truth="Comment appears immediately" status=failed reason="doesn't refresh"
     ↓
Debug agent spawns with symptoms pre-filled
     ↓
Agent investigates: reads code, forms hypotheses, tests
     ↓
Agent returns: "Root cause: useEffect missing commentCount dependency in CommentList.tsx"
     ↓
UAT.md updated:
  root_cause: "useEffect missing commentCount dependency"
  artifacts: [{path: "src/components/CommentList.tsx", issue: "missing dependency"}]
  missing: ["Add commentCount to useEffect dependency array"]
     ↓
"Run /gsd:plan-phase --gaps" (planner has precise diagnosis)
```

---

## UAT.md Gap Format (After Diagnosis)

```yaml
gaps:
  - truth: "Comment appears immediately after submission"
    status: diagnosed
    reason: "User reported: works but doesn't show until I refresh the page"
    severity: major
    test: 2
    root_cause: "useEffect in CommentList.tsx missing commentCount dependency"
    artifacts:
      - path: "src/components/CommentList.tsx"
        issue: "useEffect missing dependency"
    missing:
      - "Add commentCount to useEffect dependency array"
      - "Trigger re-render when new comment added"
    debug_session: .planning/debug/comment-not-refreshing.md
```

This enriched format gives `/gsd:plan-phase --gaps` precise information to create targeted fixes.

---

## Summary

| Component | Action |
|-----------|--------|
| `gsd-debugger.md` | ADD (new agent) |
| `diagnose-issues.md` | ADD (new workflow) |
| `verify-work.md` command | UPDATE (add Task tool, update process/criteria) |
| `verify-work.md` workflow | UPDATE (add diagnose_gaps step, update offer_next) |

**Result:** When UAT finds issues, debug agents automatically investigate root causes. You then run `/gsd:plan-phase --gaps` manually with precise diagnoses instead of guessing.
