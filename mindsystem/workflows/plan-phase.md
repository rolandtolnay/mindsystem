<decimal_phase_numbering>
Decimal phases enable urgent work insertion without renumbering:

- Integer phases (1, 2, 3) = planned milestone work
- Decimal phases (2.1, 2.2) = urgent insertions between integers

**Rules:**
- Decimals between consecutive integers (2.1 between 2 and 3)
- Filesystem sorting works automatically (2 < 2.1 < 2.2 < 3)
- Directory format: `02.1-description/`, Plan format: `02.1-01-PLAN.md`

**Validation:** Integer X must exist and be complete, X+1 must exist, decimal X.Y must not exist, Y >= 1
</decimal_phase_numbering>

<required_reading>
**Read these files NOW:**

1. .planning/ROADMAP.md
2. .planning/PROJECT.md

**Note:** Heavy references (phase-prompt.md, plan-format.md, scope-estimation.md, goal-backward.md, plan-risk-assessment.md) are loaded by the ms-plan-writer subagent, not main context. Lighter references (tdd.md) are loaded on demand during task breakdown.
</required_reading>

<purpose>
Create executable phase prompts (PLAN.md files) from task breakdown.

**Two-stage workflow:**
1. **Main context:** Task identification + grouping (steps 1-9) - collaborative, keeps user in loop
2. **Subagent (ms-plan-writer):** Plan writing (structural validation, PLAN.md files, risk scoring) - autonomous, heavy lifting

**Default: single plan per phase.** All tasks go into Plan 01, Wave 1. No dependency analysis or user confirmation needed. This is optimal for 1M context windows where phases already scope work tightly.

**Multi-plan mode** (`multi_plan: true` in config): Restores full multi-plan breakdown with dependency analysis, wave grouping, budget estimation, and user confirmation. Enable for phases with genuinely independent work streams that benefit from parallel subagent execution.
</purpose>

<planning_principles>
**Parallel by default:** Think in dependency graphs, not sequential lists. Ask "what does this need?" not "what comes next?"

**Vertical slices over horizontal layers:** Group by feature (User: model + API + UI) not by type (all models → all APIs → all UIs).

**Explicit dependencies:** EXECUTION-ORDER.md centralizes dependency and parallelism tracking. Plans with no dependencies = parallel candidates.
</planning_principles>

<process>

<step name="load_project_state" priority="first">
Read `.planning/STATE.md` and parse:
- Current position (which phase we're planning)
- Accumulated decisions (constraints on this phase)
- Pending todos from `.planning/todos/` (candidates for inclusion)
- Blockers/concerns (things this phase may address)
- Brief alignment status

If STATE.md missing but .planning/ exists, offer to reconstruct or continue without.
</step>

<step name="load_codebase_context">
Check for codebase map:

```bash
ls .planning/codebase/*.md 2>/dev/null
```

**If .planning/codebase/ exists:** Load relevant documents based on phase type:

| Phase Keywords | Load These |
|----------------|------------|
| UI, frontend, components | CONVENTIONS.md, STRUCTURE.md |
| API, backend, endpoints | ARCHITECTURE.md, CONVENTIONS.md |
| database, schema, models | ARCHITECTURE.md, STACK.md |
| testing, tests | TESTING.md, CONVENTIONS.md |
| integration, external API | INTEGRATIONS.md, STACK.md |
| refactor, cleanup, quality, tech debt | CONCERNS.md, ARCHITECTURE.md |
| setup, config | STACK.md, STRUCTURE.md |
| (default) | STACK.md, ARCHITECTURE.md |

Track extracted constraints for PLAN.md context section.
</step>

<step name="identify_phase">
Check roadmap and existing phases:

```bash
cat .planning/ROADMAP.md
ls .planning/phases/
```

If multiple phases available, ask which one to plan. If obvious (first incomplete phase), proceed.

**Phase number parsing:** Regex `^(\d+)(?:\.(\d+))?$` - Group 1: integer, Group 2: decimal (optional)

**If decimal phase:** Validate integer X exists and is complete, X+1 exists in roadmap, decimal X.Y doesn't exist, Y >= 1.

Read any existing PLAN.md or DISCOVERY.md in the phase directory.

</step>

<step name="mandatory_discovery">
**Discovery is MANDATORY unless you can prove current context exists.**

<discovery_decision>
**Level 0 - Skip** (pure internal work, existing patterns only)
- ALL work follows established codebase patterns (grep confirms)
- No new external dependencies
- Pure internal refactoring or feature extension
- Examples: Add delete button, add field to model, create CRUD endpoint

**Level 1 - Quick Verification** (2-5 min)
- Single known library, confirming syntax/version
- Low-risk decision (easily changed later)
- Action: Context7 resolve-library-id + query-docs, no DISCOVERY.md needed

**Level 2 - Standard Research** (15-30 min)
- Choosing between 2-3 options
- New external integration (API, service)
- Medium-risk decision
- Action: Route to workflows/discovery-phase.md depth=standard, produces DISCOVERY.md

**Level 3 - Deep Dive** (1+ hour)
- Architectural decision with long-term impact
- Novel problem without clear patterns
- High-risk, hard to change later
- Action: Route to workflows/discovery-phase.md depth=deep, full DISCOVERY.md

**Depth indicators:**
- Level 2+: New library not in package.json, external API, "choose/select/evaluate" in description, roadmap marked Research: Yes
- Level 3: "architecture/design/system", multiple external services, data modeling, auth design, real-time/distributed
</discovery_decision>

If roadmap flagged `Research: Likely`, Level 0 (skip) is not available.

For niche domains (3D, games, audio, shaders, ML), suggest `/ms:research-phase` before plan-phase.
</step>

<step name="read_project_history">
**Intelligent context assembly via scanner script + selective reading:**

**1. Determine scanner arguments** from prior steps:

- Phase number from identify_phase step
- Subsystem from `.planning/config.json` if available
- Phase name from ROADMAP.md phase description

```bash
SUBSYSTEM=$(ms-tools config-get subsystems.0)
PHASE_NAME=$(grep -A2 "Phase ${PHASE}:" .planning/ROADMAP.md 2>/dev/null | head -1 | sed 's/.*Phase [0-9]*: *//')
```

**2. Run context scanner:**

```bash
ms-tools scan-planning-context \
  --phase "${PHASE}" \
  --phase-name "${PHASE_NAME}" \
  ${SUBSYSTEM:+--subsystem="${SUBSYSTEM}"}
```

The scanner outputs formatted markdown with sections for patterns, learnings,
summaries, knowledge files, and pending todos. Each section is omitted if empty.
If the script fails, fall back to manual scanning.

**3. Conditionally read full summaries** — from "Summaries Needing Full Read" section, read each file. For "Other Relevant Summaries", read full body only if frontmatter context isn't sufficient (judgment).

**4. Read knowledge files** — from "Knowledge Files to Read" section, read each file.

**5. Assess pending todos** — from "Pending Todos" section, assess relevance. Read full body for relevant ones.

**From STATE.md:** Decisions → constrain approach. Pending todos → candidates. Blockers → may need to address.

**Answer before proceeding:**
- Q1: What decisions from previous phases constrain this phase?
- Q2: Are there pending todos that should become tasks?
- Q3: Are there concerns from "Next Phase Readiness" that apply?
- Q4: Given all context, does the roadmap's description still make sense?

**Track for handoff to ms-plan-writer:**
- Which summaries were selected (for @context references)
- Tech stack available (from formatted output)
- Established patterns (from formatted output)
- Key files to reference (from formatted output)
- Applicable decisions (from formatted output + full summary reads)
- Todos being addressed (from pending todos)
- Concerns being verified (from "Next Phase Readiness" in full reads)
- Matched learnings (from formatted output + knowledge files)
</step>

<step name="gather_phase_context">
Understand:
- Phase goal (from roadmap)
- What exists already (scan codebase if mid-project)
- Dependencies met (previous phases complete?)
- Any {phase}-RESEARCH.md (from /ms:research-phase)
- Any DISCOVERY.md (from mandatory discovery)
- Any {phase}-CONTEXT.md (from /ms:discuss-phase)
- Any {phase}-DESIGN.md (from /ms:design-phase)

```bash
# If mid-project, understand current state
ls -la src/ 2>/dev/null
cat package.json 2>/dev/null | head -20

# Check for ecosystem research (from /ms:research-phase)
cat .planning/phases/XX-name/${PHASE}-RESEARCH.md 2>/dev/null

# Check for phase context (from /ms:discuss-phase)
cat .planning/phases/XX-name/${PHASE}-CONTEXT.md 2>/dev/null

# Check for design specs (from /ms:design-phase)
cat .planning/phases/XX-name/${PHASE}-DESIGN.md 2>/dev/null
```

**If RESEARCH.md exists:** Use standard_stack (these libraries), architecture_patterns (follow in task structure), dont_hand_roll (NEVER custom solutions for listed problems), common_pitfalls (inform verification), code_examples (reference in actions).

**If CONTEXT.md exists:** Honor vision, prioritize essential, respect boundaries, incorporate specifics. Track that CONTEXT.md exists for risk scoring.

**If DESIGN.md exists:**
- Tasks reference specific screens from design (wireframe + states + behavior + hints)
- Verification criteria inferred from States tables, Behavior notes, and token values
- Must-Haves include design-specified observable behaviors
- Task actions specify exact values (colors, spacing) from Design Tokens table

**If none exist:** Suggest /ms:research-phase for niche domains, /ms:discuss-phase for simpler domains, or proceed with roadmap only.
</step>

<step name="break_into_tasks">
Decompose phase into tasks. **Think dependencies first, not sequence.**

**Pattern consistency:** If established patterns were surfaced in step 4b, ensure tasks follow those patterns. Reference specific patterns in action_hints where relevant.

For each potential task, ask:
1. **What does this task NEED?** (files, types, APIs that must exist)
2. **What does this task CREATE?** (files, types, APIs others might need)
3. **Can this run independently?** (no dependencies = Wave 1 candidate)

**Standard tasks need:**
- **Type**: auto
- **Task name**: Clear, action-oriented
- **Files**: Which files created/modified
- **Action hint**: Brief implementation guidance
- **Verify hint**: How to prove it worked
- **Done hint**: Acceptance criteria

**TDD detection:** Can you write `expect(fn(input)).toBe(output)` before writing `fn`?
→ Yes (business logic, validation, data transforms, algorithms): tdd_candidate=true
→ No (UI layout, config, glue code, simple CRUD): standard task

**If any tasks were marked tdd_candidate=true:** Read `~/.claude/mindsystem/references/tdd.md` for TDD plan structure guidance.

**If no TDD candidates:** Skip — the heuristic above is sufficient for detection.

**Decisions:** If you identify a task that requires choosing between approaches (which auth provider, which database, etc.), use AskUserQuestion to resolve it now. Don't defer decisions to execution. For purely technical choices where the user hasn't expressed preference, make the decision and document it in the plan's objective.

**Critical:** If external resource has CLI/API (Vercel, Stripe, etc.), use type="auto" to automate.

**User setup detection:** For tasks involving external services, identify human-required configuration:

External service indicators:
- New SDK: `stripe`, `@sendgrid/mail`, `twilio`, `openai`, `@supabase/supabase-js`
- Webhook handlers: Files in `**/webhooks/**` or `**/webhook*`
- OAuth integration: Social login, third-party auth
- API keys: Code referencing `process.env.SERVICE_*` patterns

Note external services for risk scoring.

<output_format>
**Present a concise numbered task summary for the user:**

### Tasks Identified

1. **Create User model** → `src/models/user.ts` (no dependencies)
2. **Create login endpoint** → `src/app/api/auth/login/route.ts` (needs: Task 1) [TDD]

Format: numbered list with task name, key files, dependency hint, and `[TDD]` flag if applicable. No XML.

**Retain full task details internally.** For each task, maintain in your analysis: id, name, type, needs, creates, tdd_candidate, action_hint, verify_hint, done_hint. These are needed for the handoff step — they just don't need to be displayed.
</output_format>

**Task quality check:** If you can't specify Files + Action + Verify + Done, the task is too vague.

**Good:** "Create POST /api/auth/login endpoint with bcrypt validation"
**Bad:** "Set up authentication" / "Make it secure" / "Handle edge cases"
</step>

<step name="propose_grouping">
**Determine plan boundaries before handing off to the plan-writer.**

```bash
MULTI_PLAN=$(ms-tools config-get multi_plan --default "false")
```

**If `false` (default) — single plan mode:**

All tasks go into Plan 01, Wave 1. No dependency analysis, clustering, or budget estimation.

**Confirm task breakdown via AskUserQuestion:**
- header: "Tasks Identified"
- question: "Ready to write the plan with these tasks?"
- Options: "Looks good, write the plan", "I want to adjust"

**"Looks good, write the plan":** Proceed to load_skills.
**"I want to adjust":** User describes changes in free-text. Apply adjustments, re-present tasks, and confirm again.

**If `true` — multi-plan mode:**

After presenting the task list, analyze dependencies and propose how tasks should group into plans. This is a collaborative planning decision — the user sees it and can adjust.

**Process:**
1. Map task dependencies from needs/creates
2. Identify independent task clusters (parallel candidates = Wave 1)
3. Group by vertical feature affinity (not horizontal layers)
4. Estimate context budget per group using weight heuristics (L ~5%, M ~10%, H ~20%)
5. Target 25-45% per plan, bias toward fewer plans

**Present to user:**

```markdown
### Proposed Plan Structure

**Plan 01: {title}** (~{budget}%)
Tasks: {task_ids} — {brief rationale}

**Plan 02: {title}** (~{budget}%)
Tasks: {task_ids} — {brief rationale}

**Waves:** {wave structure}
```

**TDD plans are always standalone** — propose them as dedicated plans regardless of budget.

**Confirm via AskUserQuestion:**
- header: "Plan Structure"
- question: "Does this plan structure look good?"
- Options: "Looks good, proceed", "Adjust grouping"

**"Looks good, proceed":** Continue to load_skills.
**"Adjust grouping":** User describes changes in free-text. Apply adjustments, re-present, and confirm again.
</step>

<step name="load_skills">
**Load configured skills for planning.**

```bash
PLAN_SKILLS=$(ms-tools config-get skills.plan --default "[]")
```

**If skills configured (non-empty array):** Invoke each via the Skill tool. These provide implementation conventions, code patterns, and framework best practices that must influence the resulting plans.

After loading, extract implementation-relevant content:
- Code patterns and conventions (naming, structure, architecture rules)
- Framework-specific best practices (routing patterns, state management, data fetching)
- Anti-patterns to avoid
- Quality criteria specific to the domain

Distill into a `<skill_context>` block (aim for high signal density — conventions that change what code looks like, not general advice). This block will be passed to the plan-writer.

**If no skills configured:**

```
Tip: Configuring plan skills in /ms:config can improve plan quality — conventions get encoded directly into plans. Run /ms:config to set them up.
```

Non-blocking. Continue with empty `<skill_context>`.
</step>

<step name="handoff_to_writer">
**Spawn ms-plan-writer subagent with task list and context.**

**Subsystem determination:** Read config.json subsystems list via `ms-tools config-get subsystems`. Select best match for this phase based on phase goal and task analysis.

**Learnings assembly:** Collect matched learnings from step 6 into `<learnings>` section. Omit section entirely if no matches. Include source paths for attribution.

Assemble handoff payload:

```xml
<task_list>
  {Construct full task XML from your analysis. Each task needs: id, name, type, needs, creates, tdd_candidate, action_hint, verify_hint, done_hint. Use the same XML schema the plan-writer expects.}
</task_list>

<proposed_grouping>
  <plan id="01" title="{title}" budget="{estimated_%}" wave="{wave_number}">
    <tasks>{comma-separated task IDs}</tasks>
    <rationale>{why these tasks belong together}</rationale>
  </plan>
  <!-- More plans... -->
</proposed_grouping>

<phase_context>
  <!-- Extract phase_goal from ROADMAP.md line after "Phase N:" and REQ-IDs from "Requirements:" field -->
  <phase_number>{PHASE}</phase_number>
  <phase_name>{PHASE_NAME}</phase_name>
  <phase_dir>.planning/phases/{PHASE}-{PHASE_NAME}</phase_dir>
  <phase_goal>{goal from ROADMAP}</phase_goal>
  <requirements>{REQ-IDs from ROADMAP}</requirements>
  <subsystem_hint>{best-match subsystem from config.json}</subsystem_hint>
</phase_context>

<project_refs>
  <project_md>.planning/PROJECT.md</project_md>
  <roadmap_md>.planning/ROADMAP.md</roadmap_md>
  <state_md>.planning/STATE.md</state_md>
  <context_md>{path if CONTEXT.md exists}</context_md>
  <design_md>{path if DESIGN.md exists}</design_md>
  <research_md>{path if RESEARCH.md exists}</research_md>
  <prior_summaries>
    {paths to selected relevant SUMMARYs}
  </prior_summaries>
  <codebase_docs>
    {paths to relevant .planning/codebase/*.md files}
  </codebase_docs>
</project_refs>

<external_services>
  {list of services detected in task breakdown}
</external_services>

<skill_context>
{Distilled implementation conventions from loaded skills. Code patterns, framework best practices, anti-patterns, quality criteria. Omit if no skills loaded.}
</skill_context>

<learnings>
  <!-- Flat list from read_project_history step 6. Omit if no matches found. -->
  <learning type="debug" source=".planning/debug/resolved/{slug}.md">{root_cause} — fix: {resolution}</learning>
  <learning type="adhoc" source=".planning/adhoc/{file}.md">{learnings entry}</learning>
  <learning type="pattern" source=".planning/phases/{path}">{patterns-established entry}</learning>
  <learning type="knowledge" source=".planning/knowledge/{subsystem}.md">{decisions, architecture, pitfalls from knowledge files}</learning>
</learnings>
```

**Spawn subagent:**

```
Task(
  subagent_type: "ms-plan-writer"
  description: "Write PLAN.md files for phase {PHASE}"
  prompt: "{assembled handoff payload}"
)
```

The subagent handles:
- Building dependency graph from needs/creates
- Validating proposed grouping (file conflicts, circular deps, missing dependency chains)
- Applying proposed plan boundaries (deviates only for structural issues, not budget math)
- Assigning wave numbers
- Deriving Must-Haves (goal-backward)
- Estimating scope (informational, for grouping rationale)
- Writing PLAN.md files + EXECUTION-ORDER.md
- Git commit
- Calculating risk score
</step>

<step name="receive_results">
**Parse subagent return.**

The ms-plan-writer returns structured markdown:

```markdown
## PLANS CREATED

**Phase:** 03-authentication
**Plans:** 3 plan(s) in 2 wave(s)
**Commit:** a1b2c3d

### Wave Structure
| Wave | Plans | Dependency |
|------|-------|------------|
| 1 | 01, 02 | None (parallel) |
| 2 | 03 | Waits for 01, 02 |

### Risk Assessment
**Score:** 45/100 (optional)
**Top Factors:**
- CONTEXT.md with locked decisions
- Complex domain (auth)

### Files Created
- `.planning/phases/03-authentication/03-01-PLAN.md`
- `.planning/phases/03-authentication/03-02-PLAN.md`
- `.planning/phases/03-authentication/03-03-PLAN.md`
```

Extract:
- `plan_count`: Number of plans created
- `wave_count`: Number of waves
- `wave_structure`: Wave-to-plan mapping
- `grouping_rationale`: Optional table showing task weights and consolidation notes
- `risk_score`: 0-100
- `risk_tier`: "skip" | "optional" | "verify"
- `risk_factors`: Top contributing factors
- `plan_paths`: List of created PLAN.md files
- `commit_hash`: Git commit reference
</step>

<step name="risk_decision">
**MANDATORY gate — present risk score via AskUserQuestion. Do not skip or inline with other output.**

After parsing the plan-writer results, present the risk assessment as a standalone AskUserQuestion before showing anything else. Do not combine this with the "Next Up" block or any other output.

**Present via AskUserQuestion based on tier from subagent:**

| Tier | Score | Default option | Message |
|------|-------|----------------|---------|
| Skip | 0-39 | "Skip verification" | "Low risk. Verification optional." |
| Optional | 40-69 | "Verify plans" | "Moderate complexity. Verification recommended." |
| Verify | 70-100 | "Verify plans (Recommended)" | "Higher complexity. Verification strongly recommended." |

Include top risk factors for Optional/Verify tiers. Optional/Verify tiers also offer "Review plans manually".

**Handle response:**

**"Skip verification":**
Continue to offer_next.

**"Verify plans":**
Spawn ms-plan-checker:

```
Task(
  subagent_type: "ms-plan-checker"
  description: "Verify phase ${PHASE} plans"
  prompt: """
Verify plans for phase ${PHASE}.
Phase directory: ${PHASE_DIR}

1. Read .planning/ROADMAP.md for phase goal
2. Read all *-PLAN.md files in ${PHASE_DIR}
3. Read ${PHASE}-CONTEXT.md if exists (for dimension 7)
4. Run all verification dimensions
5. Return PASSED or ISSUES FOUND
"""
)
```

If **PASSED:** Continue to offer_next with "Plans verified ✓"

If **ISSUES FOUND:** Present issues, then AskUserQuestion:
- "Fix issues — I'll edit the plans"
- "Execute anyway — proceed despite issues"
- "Re-verify — check again after fixes"

**"Review plans manually":**
Show plan paths, wait for user response:
- "looks good" / "proceed" → continue to offer_next
- "run verification" → spawn ms-plan-checker
- Describes changes → help edit plans
</step>

<step name="offer_next">

**Single plan mode** (default):

```
Phase {X} planned: 1 plan

---

## Next Up

**Phase {X}: [Phase Name]**

`/ms:execute-phase {X}`

<sub>`/clear` first - fresh context window</sub>

---

**Also available:**
- Review/adjust plan before executing
- View plan: `cat .planning/phases/XX-name/XX-01-PLAN.md`

---
```

**Multi-plan mode:**

```
Phase {X} planned: {N} plan(s) in {M} wave(s)

## Wave Structure
Wave 1 (parallel): {plan-01}, {plan-02}
Wave 2: {plan-03}
...

{If grouping_rationale present, insert here:}

## Grouping Notes
{grouping_rationale table from plan-writer}

---

## Next Up

**Phase {X}: [Phase Name]** - {N} plan(s) in {M} wave(s)

`/ms:execute-phase {X}`

<sub>`/clear` first - fresh context window</sub>

---

**Also available:**
- Review/adjust plans before executing
- View all plans: `ls .planning/phases/XX-name/*-PLAN.md`

---
```
</step>

</process>

<anti_patterns>
- No story points or hour estimates
- No sub-sub-sub tasks
- **No reflexive sequential chaining** (Plan 02 depends on 01 "just because")
Tasks are instructions for Claude, not Jira tickets.
</anti_patterns>

<success_criteria>
Phase planning complete when:
- [ ] Prior decisions, issues, concerns synthesized
- [ ] Tasks identified with needs/creates dependencies
- [ ] Plan grouping determined (auto-grouped or user-confirmed)
- [ ] Task list + proposed grouping + skill context handed off to ms-plan-writer
- [ ] PLAN files + EXECUTION-ORDER.md created (pure markdown, Must-Haves, follows proposed grouping)
- [ ] Plans committed with maximized wave parallelism
- [ ] Risk assessment presented and user decision captured (verify/skip)
- [ ] User knows next steps and wave structure
</success_criteria>
