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
Create executable phase prompts (PLAN.md files) optimized for parallel execution.

**Two-stage workflow:**
1. **Main context:** Task identification (steps 1-8) - collaborative, keeps user in loop
2. **Subagent (ms-plan-writer):** Plan writing (dependency graph, wave assignment, PLAN.md files, risk scoring) - autonomous, heavy lifting

PLAN.md IS the prompt that Claude executes. Plans are grouped into execution waves based on dependencies - independent plans run in parallel, dependent plans wait for predecessors.
</purpose>

<planning_principles>
**Parallel by default:** Think in dependency graphs, not sequential lists. Ask "what does this need?" not "what comes next?"

**Vertical slices over horizontal layers:** Group by feature (User: model + API + UI) not by type (all models → all APIs → all UIs).

**Explicit dependencies:** Every plan declares what it needs (`depends_on`) and what it touches (`files_modified`). Empty dependencies = parallel candidate.

**Secure by design:** Assume hostile input on every boundary. Validate, parameterize, authenticate, fail closed.

**Performance by design:** Assume production load, not demo conditions. Plan for efficient data access, appropriate caching, minimal round trips.

**Observable by design:** Plan to debug your own work. Include meaningful error messages, appropriate logging, and clear failure states.
</planning_principles>

<process>

<step name="load_project_state" priority="first">
Read `.planning/STATE.md` and parse:
- Current position (which phase we're planning)
- Accumulated decisions (constraints on this phase)
- Pending todos (candidates for inclusion)
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
| refactor, cleanup | CONCERNS.md, ARCHITECTURE.md |
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

**Check for --gaps flag:**
If `--gaps` present in arguments, switch to gap_closure_mode (see `<step name="gap_closure_mode">`).
</step>

<step name="gap_closure_mode">
**Triggered by `--gaps` flag.** Plans address verification gaps OR UAT gaps.

**1. Find gap sources:**

```bash
PHASE_DIR=$(ls -d .planning/phases/${PHASE_ARG}* 2>/dev/null | head -1)

# Check for VERIFICATION.md (code verification gaps)
ls "$PHASE_DIR"/*-VERIFICATION.md 2>/dev/null

# Check for UAT.md with diagnosed status (user testing gaps)
grep -l "status: diagnosed" "$PHASE_DIR"/*-UAT.md 2>/dev/null
```

**Priority:** If both exist, load both and combine gaps. UAT gaps (user-discovered) may overlap with verification gaps (code-discovered).

**2. Parse gaps:**

**From VERIFICATION.md** (if exists): Parse `gaps:` from YAML frontmatter.

**From UAT.md** (if exists with status: diagnosed): Parse gaps from `## Gaps` section (YAML format).

Each gap has:
- `truth`: The observable behavior that failed
- `reason`: Why it failed
- `artifacts`: Files with issues
- `missing`: Specific things to add/fix

**3. Load existing SUMMARYs:**

```bash
ls "$PHASE_DIR"/*-SUMMARY.md
```

Understand what's already built. Gap closure plans reference existing work.

**4. Find next plan number:**

```bash
# Get highest existing plan number
ls "$PHASE_DIR"/*-PLAN.md | sort -V | tail -1
```

If plans 01, 02, 03 exist, next is 04.

**5. Group gaps into plans:**

Cluster related gaps by:
- Same artifact (multiple issues in Chat.tsx → one plan)
- Same concern (fetch + render → one "wire frontend" plan)
- Dependency order (can't wire if artifact is stub → fix stub first)

**6. Create gap closure tasks:**

For each gap:
```xml
<task name="{fix_description}" type="auto">
  <files>{artifact.path}</files>
  <action>
    {For each item in gap.missing:}
    - {missing item}

    Reference existing code: {from SUMMARYs}
    Gap reason: {gap.reason}
  </action>
  <verify>{How to confirm gap is closed}</verify>
  <done>{Observable truth now achievable}</done>
</task>
```

**7. Write PLAN.md files:**

Use standard template but note gap closure context:

```yaml
---
phase: XX-name
plan: NN              # Sequential after existing
type: execute
wave: 1               # Gap closures typically single wave
depends_on: []        # Usually independent of each other
files_modified: [...]
gap_closure: true     # Flag for tracking
---
```

**9. Present gap closure summary:**

```markdown
## Gap Closure Plans Created

**Phase {X}: {Name}** — closing {N} gaps

| Plan | Gaps Addressed | Files |
|------|----------------|-------|
| {phase}-04 | {gap truths} | {files} |
| {phase}-05 | {gap truths} | {files} |

---

## ▶ Next Up

**Execute gap closure plans**

`/ms:execute-phase {X}`

<sub>`/clear` first → fresh context window</sub>

---
```

**Skip directly to git_commit step after creating plans.**
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
**Intelligent context assembly from frontmatter dependency graph:**

**1. Scan all summary frontmatter (cheap - first ~25 lines):**

```bash
for f in .planning/phases/*/*-SUMMARY.md; do
  # Extract frontmatter only (between first two --- markers)
  sed -n '1,/^---$/p; /^---$/q' "$f" | head -30
done
```

Parse YAML to extract: phase, subsystem, requires, provides, affects, tags, key-decisions, key-files

**2. Build dependency graph for current phase:**

- **Check affects field:** Which prior phases have current phase in their `affects` list? → Direct dependencies
- **Check subsystem:** Which prior phases share same subsystem? → Related work
- **Check requires chains:** If phase X requires phase Y, and we need X, we also need Y → Transitive dependencies
- **Check roadmap:** Any phases marked as dependencies in ROADMAP.md phase description?

**3. Select relevant summaries:**

Auto-select phases that match ANY of:
- Current phase name/number appears in prior phase's `affects` field
- Same `subsystem` value
- In `requires` chain (transitive closure)
- Explicitly mentioned in STATE.md decisions as affecting current phase

Typical selection: 2-4 prior phases (immediately prior + related subsystem work)

**4. Extract context from frontmatter (WITHOUT opening full summaries yet):**

From selected phases' frontmatter, extract:
- **Tech available:** Union of all tech-stack.added lists
- **Patterns established:** Union of all tech-stack.patterns and patterns-established
- **Key files:** Union of all key-files (for @context references)
- **Decisions:** Extract key-decisions from frontmatter

**4b. Present established patterns to user:**

If patterns-established entries were collected, display:

```
### Established Patterns to Maintain
- [Pattern: description] (from phase XX)
```

If no patterns collected, skip.

**5. Now read FULL summaries for selected phases:**

Only now open and read complete SUMMARY.md files for the selected relevant phases. Extract:
- Detailed "Accomplishments" section
- "Next Phase Readiness" warnings/blockers
- "Issues Encountered" that might affect current phase
- "Deviations from Plan" for patterns

**6. Search additional knowledge sources (cross-cutting retrieval):**

Use keywords already extracted: phase name, subsystem (from config.json), tags/tech terms from selected summaries.

**6a. Resolved debug docs:**

```bash
for f in .planning/debug/resolved/*.md; do
  sed -n '1,/^---$/p; /^---$/q' "$f" | head -20
done 2>/dev/null
```

Select docs matching: same `subsystem`, overlapping `tags`, or `phase` in dependency chain.
Extract: `root_cause` + `resolution` one-liners from frontmatter.

**If matched debug docs found, present warning to user:**

```
### Previous Debug Sessions in This Area
- **{slug}** ({subsystem}): {root_cause} — Fix: {resolution}
```

Awareness only — learnings still flow to `<learnings>` handoff.
If no matches, skip.

**6b. Adhoc summaries:**

```bash
for f in .planning/adhoc/*-SUMMARY.md; do
  sed -n '1,/^---$/p; /^---$/q' "$f" | head -20
done 2>/dev/null
```

Select matching: same `subsystem`, overlapping `tags`, or `related_phase` in dependency chain.
Extract: `learnings` array entries (skip if empty).

**6c. Completed todos:**

```bash
ls .planning/todos/done/*.md 2>/dev/null
```

If exists, grep body content for phase keywords or subsystem. Extract brief description of resolved items.

**6d. Milestone decisions:**

```bash
ls .planning/milestones/v*-DECISIONS.md 2>/dev/null
```

If exists, grep for entries matching current subsystem or phase keywords. Extract matched decision rows.

**6e. LEARNINGS.md (cross-milestone index):**

```bash
cat .planning/LEARNINGS.md 2>/dev/null
```

If exists, grep for entries matching phase keywords, subsystem, or tech terms. Extract matched one-liner entries with source references.

**Collect matched learnings for handoff** — assemble into flat list for `<learnings>` section.

**From STATE.md:** Decisions → constrain approach. Pending todos → candidates. Blockers → may need to address.

**From pending todos:**

```bash
ls .planning/todos/pending/*.md 2>/dev/null
```

Assess each pending todo - relevant to this phase? Natural to address now?

**Answer before proceeding:**
- Q1: What decisions from previous phases constrain this phase?
- Q2: Are there pending todos that should become tasks?
- Q3: Are there concerns from "Next Phase Readiness" that apply?
- Q4: Given all context, does the roadmap's description still make sense?

**Track for handoff to ms-plan-writer:**
- Which summaries were selected (for @context references)
- Tech stack available (from frontmatter)
- Established patterns (from frontmatter)
- Key files to reference (from frontmatter)
- Applicable decisions (from frontmatter + full summary)
- Todos being addressed (from pending todos)
- Concerns being verified (from "Next Phase Readiness")
- Matched learnings (from debug docs, adhoc summaries, patterns, decisions, LEARNINGS.md)
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
- Tasks reference specific screens/components from design
- Verification criteria include design verification items
- must_haves include design-specified observable behaviors
- Task actions specify exact values (colors, spacing) from design

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

**TDD detection:** For each potential task, evaluate TDD fit:

TDD candidates (create dedicated TDD plans):
- Business logic with defined inputs/outputs
- API endpoints with request/response contracts
- Data transformations, parsing, formatting
- Validation rules and constraints
- Algorithms with testable behavior
- State machines and workflows

Standard tasks (remain in standard plans):
- UI layout, styling, visual components
- Configuration changes
- Glue code connecting existing components
- One-off scripts and migrations
- Simple CRUD with no business logic

**Heuristic:** Can you write `expect(fn(input)).toBe(output)` before writing `fn`?
→ Yes: Mark as tdd_candidate=true
→ No: Standard task

Read `~/.claude/mindsystem/references/tdd.md` now for TDD criteria and plan structure.

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
</step>

<step name="handoff_to_writer">
**Spawn ms-plan-writer subagent with task list and context.**

**Subsystem determination:** Read config.json subsystems list via `jq -r '.subsystems[]' .planning/config.json`. Select best match for this phase based on phase goal and task analysis.

**Learnings assembly:** Collect matched learnings from step 6 into `<learnings>` section. Omit section entirely if no matches. Include source paths for attribution.

Assemble handoff payload:

```xml
<task_list>
  {Construct full task XML from your analysis. Each task needs: id, name, type, needs, creates, tdd_candidate, action_hint, verify_hint, done_hint. Use the same XML schema the plan-writer expects.}
</task_list>

<phase_context>
  <phase_number>{PHASE}</phase_number>
  <phase_name>{PHASE_NAME}</phase_name>
  <phase_dir>.planning/phases/{PHASE}-{PHASE_NAME}</phase_dir>
  <phase_goal>{goal from ROADMAP}</phase_goal>
  <requirements>{REQ-IDs from ROADMAP}</requirements>
  <depth>{from config.json or "standard"}</depth>
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

<learnings>
  <!-- Flat list from read_project_history step 6. Omit if no matches found. -->
  <learning type="debug" source=".planning/debug/resolved/{slug}.md">{root_cause} — fix: {resolution}</learning>
  <learning type="adhoc" source=".planning/adhoc/{file}.md">{learnings entry}</learning>
  <learning type="pattern" source=".planning/phases/{path}">{patterns-established entry}</learning>
  <learning type="decision" source=".planning/milestones/{file}">{decision}: {rationale}</learning>
  <learning type="curated" source="{source_ref from LEARNINGS.md}">{one-liner pattern}</learning>
</learnings>
```

**Spawn subagent:**

```
Task(
  subagent_type: "ms-plan-writer"
  model: "sonnet"
  description: "Write PLAN.md files for phase {PHASE}"
  prompt: "{assembled handoff payload}"
)
```

The subagent handles:
- Building dependency graph from needs/creates
- Assigning wave numbers
- Grouping tasks into plans (2-3 per plan)
- Deriving must_haves (goal-backward)
- Estimating scope, splitting if needed
- Writing PLAN.md files
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
- `risk_score`: 0-100
- `risk_tier`: "skip" | "optional" | "verify"
- `risk_factors`: Top contributing factors
- `plan_paths`: List of created PLAN.md files
- `commit_hash`: Git commit reference
</step>

<step name="risk_decision">
**Present risk score and handle user choice.**

**Skip this step if:** `--gaps` flag present (gap closure plans don't need risk assessment)

**Present via AskUserQuestion based on tier from subagent:**

**Skip tier (0-39):**
- header: "Plan Verification"
- question: "Risk Score: {score}/100 — Low risk\n\nPlans look straightforward. Verification optional."
- Options: "Execute now" (first), "Verify anyway"

**Optional tier (40-69):**
- header: "Plan Verification"
- question: "Risk Score: {score}/100 — Moderate complexity\n\nTop factors:\n- {factor_1}\n- {factor_2}\n\nVerification recommended but optional."
- Options: "Verify first" (first), "Execute now", "Review plans manually"

**Verify tier (70-100):**
- header: "Plan Verification Recommended"
- question: "Risk Score: {score}/100 — Higher complexity\n\nTop factors:\n- {factor_1}\n- {factor_2}\n- {factor_3}\n\nVerification strongly recommended."
- Options: "Verify first (Recommended)" (first), "Execute anyway", "Review plans manually"

**Handle response:**

**"Execute now" / "Execute anyway":**
Continue to offer_next.

**"Verify first" / "Verify anyway":**
Spawn ms-plan-checker:

```
Task(
  subagent_type: "ms-plan-checker"
  model: "sonnet"
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
```
Phase {X} planned: {N} plan(s) in {M} wave(s)

## Wave Structure
Wave 1 (parallel): {plan-01}, {plan-02}
Wave 2: {plan-03}
...

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

<task_quality>
**Good tasks:** Specific files, actions, verification
- "Add User model to Prisma schema with email, passwordHash, createdAt"
- "Create POST /api/auth/login endpoint with bcrypt validation"

**Bad tasks:** Vague, not actionable
- "Set up authentication" / "Make it secure" / "Handle edge cases"

If you can't specify Files + Action + Verify + Done, the task is too vague.

**TDD candidates get dedicated plans.** If "Create price calculator with discount rules" warrants TDD, mark as tdd_candidate=true. Refer to `~/.claude/mindsystem/references/tdd.md` (loaded during task breakdown) for TDD criteria.
</task_quality>

<anti_patterns>
- No story points or hour estimates
- No team assignments
- No acceptance criteria committees
- No sub-sub-sub tasks
- **No reflexive sequential chaining** (Plan 02 depends on 01 "just because")
Tasks are instructions for Claude, not Jira tickets.
</anti_patterns>

<success_criteria>
**Standard mode** — Phase planning complete when:
- [ ] STATE.md read, project history absorbed
- [ ] Mandatory discovery completed (Level 0-3)
- [ ] Prior decisions, issues, concerns synthesized
- [ ] Tasks identified with needs/creates dependencies
- [ ] Task list handed off to ms-plan-writer
- [ ] PLAN file(s) created by subagent with XML structure
- [ ] Each plan: depends_on, files_modified in frontmatter
- [ ] Each plan: must_haves derived (truths, artifacts, key_links)
- [ ] Each plan: 2-3 tasks (~50% context)
- [ ] Wave structure maximizes parallelism
- [ ] PLAN file(s) committed to git
- [ ] Risk assessment presented (score + top factors)
- [ ] User chose verify/skip (or verified if chosen)
- [ ] User knows next steps and wave structure

**Gap closure mode (`--gaps`)** — Planning complete when:
- [ ] VERIFICATION.md loaded and gaps parsed
- [ ] Existing SUMMARYs read for context
- [ ] Gaps clustered into focused plans
- [ ] Plan numbers sequential after existing (04, 05...)
- [ ] PLAN file(s) exist with gap_closure: true
- [ ] Each plan: tasks derived from gap.missing items
- [ ] PLAN file(s) committed to git
- [ ] User knows to run `/ms:execute-phase {X}` next
</success_criteria>
