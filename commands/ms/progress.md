---
name: ms:progress
description: Check project progress, show context, and route to next action (execute or plan)
allowed-tools:
  - Read
  - Bash
  - Grep
  - Glob
  - SlashCommand
---

<objective>
Check project progress, summarize recent work and what's ahead, then intelligently route to the next action - either executing an existing plan or creating the next one.

Provides situational awareness before continuing work.
</objective>


<process>

<step name="verify">
**Verify planning structure exists:**

If no `.planning/` directory:

```
No planning structure found.

Run /ms:new-project to start a new project.
```

Exit.

**If missing STATE.md but PROJECT.md or ROADMAP.md exist:**

Reconstruct STATE.md from artifacts:

1. Read PROJECT.md → Extract "What This Is" and Core Value
2. Read ROADMAP.md → Determine phases, find current position
3. Scan *-SUMMARY.md files → Extract recent decisions, concerns
4. Count pending todos in .planning/todos/pending/

Write reconstructed STATE.md, then proceed to "load" step.

```
"STATE.md missing. Reconstructing from artifacts..."
```

If missing both STATE.md and PROJECT.md/ROADMAP.md: suggest `/ms:new-project`.

**If ROADMAP.md missing but PROJECT.md exists:**

This means a milestone was completed and archived. Go to **Route F** (between milestones).

If missing both ROADMAP.md and PROJECT.md: suggest `/ms:new-project`.
</step>

<step name="check_version">
**Check for Mindsystem updates (non-blocking):**

```bash
# Installed version
cat "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/mindsystem/VERSION" 2>/dev/null || cat ./.claude/mindsystem/VERSION 2>/dev/null
```

```bash
# Latest from npm
npm view mindsystem-cc version 2>/dev/null
```

Compare versions. Store result for the report step. If npm fails or versions match, skip — do not block progress.
</step>

<step name="load">
**Load full project context:**

- Read `.planning/STATE.md` for living memory (position, decisions, issues)
- Read `.planning/ROADMAP.md` for phase structure and objectives
- Read `.planning/PROJECT.md` for current state (What This Is, Core Value, Requirements)
  </step>

<step name="recent">
**Gather recent work context:**

- Find the 2-3 most recent SUMMARY.md files
- Extract from each: what was accomplished, key decisions, any issues logged
- This shows "what we've been working on"
  </step>

<step name="position">
**Parse current position:**

- From STATE.md: current phase, plan number, status
- Calculate: total plans, completed plans, remaining plans
- Note any blockers or concerns
- Check for CONTEXT.md: For phases without PLAN.md files, check if `{phase}-CONTEXT.md` exists in phase directory
- Check for DESIGN.md: For UI-heavy phases, check if `{phase}-DESIGN.md` exists in phase directory
- Count pending todos: `ls .planning/todos/pending/*.md 2>/dev/null | wc -l`
- Check for active debug sessions: `ls .planning/debug/*.md 2>/dev/null | grep -v resolved | wc -l`
  </step>

<step name="report">
**Present rich status report:**

```
# [Project Name]

**Progress:** [████████░░] 8/10 plans complete

## Recent Work
- [Phase X, Plan Y]: [what was accomplished - 1 line]
- [Phase X, Plan Z]: [what was accomplished - 1 line]

## Current Position
Phase [N] of [total]: [phase-name]
Plan [M] of [phase-total]: [status]
CONTEXT: [✓ if CONTEXT.md exists | - if not]
DESIGN: [✓ if DESIGN.md exists | - if not]

## Key Decisions Made
- [decision 1 from STATE.md]
- [decision 2]

## Blockers/Concerns
- [any blockers or concerns from STATE.md]

## Pending Todos
- [count] pending — /ms:check-todos to review

## Active Debug Sessions
- [count] active — /ms:debug to continue
(Only show this section if count > 0)

## Update Available
⬆ v{installed} → v{latest} — run `/ms:update`
(Only show this section if installed < latest)

## What's Next
[Next phase/plan objective from ROADMAP]
```

</step>

<step name="route">
**Determine next action based on verified counts.**

**Step 1: Count plans, summaries, and issues in current phase**

List files in the current phase directory:

```bash
# ms-tools is on PATH — invoke directly, not as a script path
ms-tools list-artifacts [current-phase-number]
```

State: "This phase has {X} plans, {Y} summaries."

**Step 1.5: Check for unaddressed UAT gaps**

Check for UAT.md files with status "diagnosed" (has gaps needing fixes).

```bash
# Check for diagnosed UAT with gaps
grep -l "status: diagnosed" .planning/phases/[current-phase-dir]/*-UAT.md 2>/dev/null
```

Track:
- `uat_with_gaps`: UAT.md files with status "diagnosed" (gaps need fixing)

**Step 2: Route based on counts**

| Condition | Meaning | Action |
|-----------|---------|--------|
| uat_with_gaps > 0 | UAT gaps need fix plans | Go to **Route E** |
| summaries < plans | Unexecuted plans exist | Go to **Route A** |
| summaries = plans AND plans > 0 | Phase complete | Go to Step 3 |
| plans = 0 | Phase not yet planned | Go to **Route B** |

---

**Route A: Unexecuted plan exists**

Find the first PLAN.md without matching SUMMARY.md.
Read its `<objective>` section.

```
---

## ▶ Next Up

**Phase {N}: [Phase Name]** — [objective from ROADMAP.md]

`/ms:execute-phase {N}`

<sub>`/clear` first → fresh context window</sub>

---
```

---

**Route B: Phase needs planning**

Check if `{phase}-CONTEXT.md` exists in phase directory.

**If CONTEXT.md exists:**

```
---

## ▶ Next Up

**Phase {N}: {Name}** — {Goal from ROADMAP.md}
<sub>✓ Context gathered, ready to plan</sub>

`/ms:plan-phase {phase-number}`

<sub>`/clear` first → fresh context window</sub>

---
```

**If CONTEXT.md does NOT exist:**

```
---

## ▶ Next Up

**Phase {N}: {Name}** — {Goal from ROADMAP.md}

`/ms:plan-phase {phase}`

<sub>`/clear` first → fresh context window</sub>

---

**Also available:**
- `/ms:discuss-phase {phase}` — gather context first
- `/ms:design-phase {phase}` — create UI/UX specifications
- `/ms:research-phase {phase}` — investigate unknowns
- `/ms:discuss-phase {phase}` — gather context and validate assumptions

---
```

---

**Route E: UAT gaps need fix plans**

UAT.md exists with gaps (diagnosed issues). Read `~/.claude/mindsystem/references/routing/gap-closure-routing.md` and follow its instructions to present the gap closure section.

---

**Step 3: Check milestone status (only when phase complete)**

Read ROADMAP.md and identify:
1. Current phase number
2. All phase numbers in the current milestone section

Count total phases and identify the highest phase number.

State: "Current phase is {X}. Milestone has {N} phases (highest: {Y})."

**Route based on milestone status:**

| Condition | Meaning | Action |
|-----------|---------|--------|
| current phase < highest phase | More phases remain | Go to **Route C** |
| current phase = highest phase | Milestone complete | Go to **Route D** |

---

**Route C: Phase complete, more phases remain**

Show phase completion header, then read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions to present "Next Up" with pre-work context for the next phase.

After the "Next Up" section, add:
```
**Also available:**
- `/ms:verify-work {Z}` — user acceptance test before continuing
```

---

**Route D: Milestone complete**

Read `~/.claude/mindsystem/references/routing/milestone-complete-routing.md` and follow its instructions to present the milestone complete section.

---

**Route F: Between milestones (ROADMAP.md missing, PROJECT.md exists)**

A milestone was completed and archived. Read `~/.claude/mindsystem/references/routing/between-milestones-routing.md` and follow its instructions to present the between-milestones section.

</step>

<step name="edge_cases">
**Handle edge cases:**

- Phase complete but next phase not planned → offer `/ms:plan-phase [next]`
- All work complete → offer milestone completion
- Blockers present → highlight before offering to continue
  </step>

</process>

<success_criteria>

- [ ] Rich context provided (recent work, decisions, issues)
- [ ] Current position clear with visual progress
- [ ] What's next clearly explained
- [ ] Smart routing: /ms:execute-phase if plan exists, /ms:plan-phase if not
- [ ] User confirms before any action
- [ ] Seamless handoff to appropriate mindsystem command
      </success_criteria>
