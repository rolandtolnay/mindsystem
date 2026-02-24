---
name: ms:plan-phase
description: Create detailed execution plan for a phase (PLAN.md)
argument-hint: "[phase] [--gaps]"
allowed-tools:
  - Read
  - Bash
  - Write
  - Glob
  - Grep
  - AskUserQuestion
  - WebFetch
  - mcp__context7__*
  - Task
  - Skill
---

<objective>
Create executable phase prompt with discovery, context injection, and task breakdown.

Purpose: Break down roadmap phases into concrete, executable PLAN.md files that Claude can execute.
Output: One or more PLAN.md files in the phase directory (.planning/phases/XX-name/{phase}-{plan}-PLAN.md)

**Gap closure mode (`--gaps` flag):**
When invoked with `--gaps`, plans address gaps identified by the verifier. Load VERIFICATION.md, create plans to close specific gaps.
</objective>

<execution_context>
@~/.claude/mindsystem/references/principles.md
@~/.claude/mindsystem/workflows/plan-phase.md
</execution_context>

<context>
Phase number: $ARGUMENTS (optional - auto-detects next unplanned phase if not provided)
Gap closure mode: `--gaps` flag triggers gap closure workflow

**Resolve phase if provided:**
```bash
# ms-tools is on PATH — invoke directly, not as a script path
PHASE_ARG=$(echo "$ARGUMENTS" | grep -oE '^[0-9]+' | head -1)
if [ -n "$PHASE_ARG" ]; then
  ms-tools find-phase "$PHASE_ARG"
fi
```

**Load project state first:**
@.planning/STATE.md

**Load roadmap:**
@.planning/ROADMAP.md

**Load requirements:**
@.planning/REQUIREMENTS.md

After loading, extract the requirements for the current phase:
1. Find the phase in ROADMAP.md, get its `Requirements:` list (e.g., "PROF-01, PROF-02, PROF-03")
2. Look up each REQ-ID in REQUIREMENTS.md to get the full description
3. Present the requirements this phase must satisfy:
   ```
   Phase [N] Requirements:
   - PROF-01: User can create profile with display name
   - PROF-02: User can upload avatar image
   - PROF-03: User can write bio (max 500 chars)
   ```

**Load phase context if exists (created by /ms:discuss-phase):**
Check for and read `.planning/phases/XX-name/{phase}-CONTEXT.md` - contains research findings, clarifications, and decisions from phase discussion.

**Load design specs if exists (created by /ms:design-phase):**
Check for and read `.planning/phases/XX-name/{phase}-DESIGN.md` - contains visual/UX specifications including layouts, components, flows, and verification criteria.

**Load tech debt if quality/cleanup phase:**
If phase name or roadmap goal contains "quality", "cleanup", "refactor", or "tech debt":
Check for and read `.planning/TECH-DEBT.md` — prioritized issues for scope selection during task breakdown.

**Load codebase context if exists:**
Check for `.planning/codebase/` and load relevant documents based on phase type.

**If --gaps flag present, also load:**
@.planning/phases/XX-name/{phase}-VERIFICATION.md — contains structured gaps in YAML frontmatter
</context>

<process>
1. Check .planning/ directory exists (error if not - user should run /ms:new-project)
2. Parse arguments: extract phase number and check for `--gaps` flag
3. If phase number provided, validate it exists in roadmap
4. If no phase number, detect next unplanned phase from roadmap

**Standard mode (no --gaps flag):**
5. Follow plan-phase.md workflow:
   - Load project state and accumulated decisions
   - Perform mandatory discovery (Level 0-3 as appropriate)
   - Scan project history via context scanner script (prior decisions, issues, debug resolutions, adhoc learnings, cross-milestone patterns)
   - Break phase into tasks
   - Propose plan grouping (plan boundaries, wave structure, budget estimates) for user review
   - Discover relevant project skills, confirm with user
   - Hand off tasks + proposed grouping + confirmed skills to plan-writer subagent
   - Create PLAN.md file(s) with executable structure

**Gap closure mode (--gaps flag):**
5. Follow plan-phase.md workflow with gap_closure_mode:
   - Load VERIFICATION.md and parse `gaps:` YAML from frontmatter
   - Read existing SUMMARYs to understand what's already built
   - Create tasks from gaps (each gap.missing item → task candidates)
   - Number plans sequentially after existing (if 01-03 exist, create 04, 05...)
   - Create PLAN.md file(s) focused on closing specific gaps

6. **Update last command**
   - Update `.planning/STATE.md` Last Command field
   - Format: `Last Command: ms:plan-phase $ARGUMENTS | YYYY-MM-DD HH:MM`

7. **Risk assessment** (skip if `--gaps` flag present)
   - Calculate risk score from context already loaded (task count, plan count, external services, CONTEXT.md, cross-cutting concerns, new deps, complex domains)
   - Present score + top factors via AskUserQuestion
   - Tier-based recommendation: Skip (0-39), Optional (40-69), Verify (70+)
   - If user chooses verify: spawn ms-plan-checker, surface results
   - If user chooses skip: proceed to next steps
</process>

<success_criteria>

- One or more PLAN.md files created in .planning/phases/XX-name/
- Each plan has: Context, Changes, Verification, Must-Haves (pure markdown format)
- Must-Haves derived as markdown checklist of user-observable truths
- Changes are specific enough for Claude to execute
- EXECUTION-ORDER.md created with wave groups and dependencies
- User knows next steps (execute plan or review/adjust)
  </success_criteria>
