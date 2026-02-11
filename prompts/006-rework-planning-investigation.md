<objective>
Investigate and brainstorm a comprehensive rework of how planning and execution work inside Mindsystem. This is a collaborative research session — gather evidence from three sources in parallel, synthesize findings, then work with the user to architect a new approach.

The three sources:
1. **Claude Code native plans** — analyze real plan files to extract what makes them effective
2. **Mindsystem planning pipeline** — map the current system end-to-end, identify waste and value
3. **Claude Code system prompts** — find how Claude Code instructs plan creation

After gathering evidence, present findings and collaborate with the user to redesign the format. This may break core assumptions: task limits per plan, the wave system, XML structure, YAML frontmatter, executor workflow weight, summary creation overhead. Everything is on the table.
</objective>

<context>
## Ticket Context

Two Linear tickets drive this work:

**MIN-83: Improve plan format using Claude Code plan principles**
- Mindsystem plans are verbose compared to Claude Code's native plans
- Goal: adopt conciseness while preserving Mindsystem-specific features (task types, verification, deviation handling)
- Key comment: reconstruct from first principles using 3 input sources (Claude Code prompts, generated plans, Mindsystem practices)
- Questions raised: Is YAML frontmatter needed? Who consumes it? Should plan-writer run on Opus?
- Proposed: relax 2-task limit to 3

**MIN-89: Executor inefficiency — 90k-135k tokens for minimal output**
- Case study: executor consumed 135k tokens, 9 minutes, 90 tool uses for ~500 lines of meaningful output
- Root cause breakdown:
  - **~50% tokens: Redundant context loading** — executor re-reads 20+ files that the plan already encoded. The plan's @context references serve the plan-writer, not the executor.
  - **~20-30% tokens: Post-execution overhead** — 6x git status, summary template compliance, STATE.md updates, mechanical must_haves verification
  - **~30% tokens: Actual work** — the code writing itself
- Key insight: "The plan is the prompt. If the plan is good enough, the executor should be a thin execution layer."
- The execute-plan workflow is 1200 lines + summary template 300 lines = 1500 lines of instruction overhead before the plan itself

## Current Pipeline (condensed)

The planning-to-execution flow:

```
/ms:plan-phase (main context, collaborative)
  → Identifies tasks, gathers context
  → Hands off to ms-plan-writer subagent (Sonnet)
      → Reads: phase-prompt.md, plan-format.md, scope-estimation.md, goal-backward.md, plan-risk-assessment.md
      → Builds dependency graph, assigns waves, groups into plans (2-3 tasks each)
      → Derives must_haves (goal-backward verification)
      → Writes PLAN.md files with YAML frontmatter + XML structure
      → Calculates risk score

/ms:execute-phase (orchestrator)
  → Groups plans by wave number from frontmatter
  → Spawns ms-executor subagents per plan
      → Executor loads: execute-plan.md (1200 lines) + summary.md template (300 lines)
      → Re-reads all @context files from the plan
      → Executes tasks, handles deviations, commits per task
      → Creates SUMMARY.md with heavy frontmatter
      → Updates STATE.md, ROADMAP.md
```

## Known Pain Points

1. **YAML frontmatter in PLAN.md** — contains wave, depends_on, files_modified, must_haves, subsystem_hint, user_setup. Question: does anything mechanically parse these fields? Or is it documentation masquerading as data?

2. **XML task structure** — `<task type="auto"><name><files><action><verify><done></task>`. Claude Code plans use simple numbered markdown steps instead.

3. **execute-plan.md bloat** — 1200 lines of workflow instructions loaded into every executor. Includes: deviation rules, commit protocol, authentication gates, summary creation, STATE.md updates, codebase map updates, routing logic.

4. **Double context loading** — plan-writer reads source files via @-references to understand the codebase, encodes knowledge into the plan. Executor then re-reads the same files.

5. **Summary creation overhead** — heavy frontmatter (subsystem, dependency graph, tech tracking, mock hints, patterns established) that enables automatic context assembly for future planning. But costs ~20-30% of executor tokens.

6. **must_haves mechanical verification** — executor greps for patterns it just wrote. The MIN-89 case study calls this "busywork."

7. **2-task limit per plan** — introduced to preserve context, but may be overly conservative, especially if plan format gets more concise.
</context>

<prerequisites>
## Step 0: Load Domain Knowledge and Ticket Details

**Load Mindsystem expertise first.** Invoke the `ms-meta` skill using the Skill tool so Mindsystem architecture, philosophy, and component model are available throughout this session.

**Fetch both tickets with comments.** Invoke the `linear` skill using the Skill tool with args: `Fetch MIN-83 with comments and MIN-89 with comments. Show me the full ticket details and all comments for both.`

Wait for both to complete before proceeding.
</prerequisites>

<parallel_investigation>
## Step 1: Launch Three Research Agents in Parallel

**CRITICAL: Launch all 3 agents in a SINGLE message containing 3 parallel Task tool calls. Do NOT launch them one at a time. Use subagent_type appropriate for each task.**

### Agent 1: Claude Code Plans Analyst (subagent_type: "Explore")

```
Analyze Claude Code's native plan files to extract the core principles that make them effective.

**Mission:**
1. List all files in ~/.claude/plans/ sorted by modification time (most recent first)
2. Read the 12 most recently modified plan files in full
3. For each plan, analyze:
   - Overall structure (headers, sections, ordering)
   - How context is provided (inline vs. references)
   - How tasks/steps are described (XML? numbered lists? prose?)
   - What metadata is included (frontmatter? none?)
   - How verification is specified
   - Token density: ratio of actionable content to total content
   - What's OMITTED that you might expect (and why omission works)

4. Synthesize across all plans:
   - Common structural patterns (what appears in every plan?)
   - Variations (what differs between plans?)
   - The "minimum viable plan" — what's the smallest effective plan look like?
   - Formatting conventions (markdown headers, code blocks, lists)

**Output format:**
## Claude Code Plan Principles

### Universal Structure
[What every plan has]

### Common Patterns
[Recurring elements across plans]

### What's Omitted
[What Mindsystem has that Claude Code plans don't — and why they don't need it]

### Token Density Analysis
[Average plan size, content-to-overhead ratio]

### Key Insight
[The single most important takeaway about what makes these plans effective]

### Raw Examples
[Include 2-3 representative plan excerpts showing different complexity levels]
```

### Agent 2: Mindsystem Pipeline Analyst (subagent_type: "Explore")

```
Map the complete Mindsystem planning pipeline and identify what's consumed mechanically vs. what's decorative.

**Mission:**

**Part A: Map the pipeline**
Read these files in the mindsystem repository (working directory):
- mindsystem/references/plan-format.md
- mindsystem/templates/phase-prompt.md
- mindsystem/templates/summary.md
- mindsystem/workflows/plan-phase.md
- mindsystem/workflows/execute-plan.md
- agents/ms-plan-writer.md
- agents/ms-executor.md (if exists, check with Glob first)
- mindsystem/workflows/execute-phase.md
- mindsystem/references/goal-backward.md
- mindsystem/references/scope-estimation.md

For each file, document:
- Purpose in the pipeline
- Who reads it (plan-writer? executor? orchestrator? user?)
- Token count estimate (line count * ~4 tokens/line)
- Key content that could be simplified or removed

**Part B: Frontmatter consumption audit**
Search the entire codebase for anything that mechanically parses PLAN.md frontmatter fields:
- Grep for: "wave:", "depends_on:", "files_modified:", "must_haves:", "subsystem_hint:", "user_setup:", "gap_closure:"
- For each match, determine: Is this READING the field to make a decision? Or just WRITING/templating it?
- Document which fields are consumed by code vs. only consumed by Claude reading prose

**Part C: Summary frontmatter consumption audit**
Same analysis for SUMMARY.md frontmatter fields:
- Grep for: "requires:", "provides:", "affects:", "tech-stack:", "key-files:", "key-decisions:", "patterns-established:", "mock_hints:"
- Who reads these? How?

**Part D: Execute-plan weight analysis**
For execute-plan.md specifically:
- Count lines per section (deviation rules, commit protocol, auth gates, summary creation, STATE updates, etc.)
- Identify which sections are essential for every execution vs. conditional
- Estimate: if the plan format improves, which sections become unnecessary?

**Output format:**
## Mindsystem Pipeline Map

### Pipeline Flow
[Diagram showing data flow between files]

### Token Budget
[Table: file, line count, estimated tokens, who loads it]

### Frontmatter Audit
[Table: field, written by, read by, mechanically parsed?, verdict (keep/remove/simplify)]

### Summary Frontmatter Audit
[Same table format]

### Execute-Plan Breakdown
[Table: section, lines, essential/conditional, candidates for removal]

### Waste Identification
[Top 5 sources of unnecessary token consumption in the pipeline]
```

### Agent 3: Claude Code System Prompts Researcher (subagent_type: "general-purpose")

```
Research the Claude Code system prompts repository to find ALL instructions related to planning, plan mode, and plan file creation.

**Mission:**

1. Clone the repository locally:
   ```bash
   cd /tmp && gh repo clone Piebald-AI/claude-code-system-prompts claude-code-prompts 2>/dev/null || (cd /tmp/claude-code-prompts && git pull)
   ```

2. Search the entire repository for planning-related content:
   - Grep for: "plan", "plan mode", "plan file", "planning", "EnterPlanMode", "ExitPlanMode", "plan_file"
   - Search file names containing "plan"
   - Read any files that appear to contain planning instructions

3. For each relevant section found, extract:
   - The exact instructions Claude Code receives about plan creation
   - Format requirements (what structure is mandated)
   - What Claude Code is told to include/exclude in plans
   - How plan mode is entered and exited
   - What happens with the plan file after creation

4. Cross-reference with the actual plan output (Agent 1's findings):
   - Do the system prompt instructions match what plans actually look like?
   - Are there instructions that plans don't follow?
   - Are there plan conventions that aren't in the system prompts?

**Output format:**
## Claude Code Planning Instructions

### System Prompt Excerpts
[Exact relevant text from system prompts, with file paths]

### Plan Mode Protocol
[How plan mode works: entry, creation, approval, execution]

### Plan Format Specification
[What the system prompts say about plan structure]

### Key Principles Encoded
[What values/principles the prompts encode about planning]

### Gap Analysis
[Instructions vs reality — what plans do that prompts don't mention, and vice versa]
```
</parallel_investigation>

<synthesis>
## Step 2: Synthesize Findings

After all 3 agents return, compile a structured comparison in the main context.

Present to the user:

```markdown
## Research Findings Summary

### 1. Claude Code Plans: What Works
[Key principles from Agent 1]

### 2. Mindsystem Pipeline: Where Tokens Go
[Token budget and waste analysis from Agent 2]

### 3. Claude Code System Prompts: What's Prescribed
[Planning instructions from Agent 3]

### 4. Cross-Source Insights
- What Claude Code plans do that Mindsystem plans don't (and vice versa)
- What the system prompts prescribe vs. what Mindsystem requires beyond that
- Where the evidence clearly points to changes
- Where the evidence is ambiguous and needs user judgment

### 5. Frontmatter Verdict
[Based on Agent 2's audit: which fields are mechanically consumed, which are decorative]

### 6. Execute-Plan Verdict
[Based on Agent 2's analysis: which sections could be stripped and estimated savings]
```

**After presenting findings, STOP and wait for user input.** Do not proceed to proposing solutions yet. Use AskUserQuestion:

- header: "Research complete"
- question: "I've presented all findings. What's your initial read? Which direction resonates?"
- options:
  - "Let's discuss findings first" — Walk through observations together before proposing changes
  - "I have a strong direction" — I know what I want, let me describe it
  - "Need more research" — There are gaps, let's investigate further
  - "Apply first-principles" — Let's use /consider:first-principles to reconstruct from fundamentals
</synthesis>

<collaboration>
## Step 3: Collaborative Design

This phase is iterative. Work WITH the user, not ahead of them.

**Principles for this phase:**
- Use AskUserQuestion for every major design decision — present concrete options with trade-offs
- When the user proposes an idea, explore it thoroughly before pushing back
- If research gaps surface, launch targeted agents to fill them (one question at a time)
- Build the new design incrementally — don't present a complete solution, build it together
- Reference specific findings from Step 2 when discussing options

**Key decisions to work through (order may vary based on user direction):**

1. **Plan format**: XML tasks vs. markdown steps vs. hybrid? YAML frontmatter vs. markdown headers vs. nothing?
2. **Plan scope**: 2 tasks vs. 3 vs. flexible? What's the right unit of work per plan?
3. **Context strategy**: How should plans provide context to executors? Inline everything? Minimal references? None?
4. **Executor weight**: Strip execute-plan.md to essentials? What's essential vs. noise?
5. **Summary format**: Keep heavy frontmatter for dependency graph? Simplify? Remove?
6. **must_haves**: Keep goal-backward verification? Lighter form? Move to a different phase?
7. **Wave system**: Keep parallel waves? Simplify? Change how dependencies work?
8. **Plan-writer model**: Sonnet vs. Opus? What evidence supports each?
9. **Pipeline changes**: Which files need rewriting? Which can be patched?

**For each decision, present:**
- Current state (what exists today and why)
- Evidence from research (what the findings suggest)
- Options with concrete trade-offs
- Your recommendation (if you have one based on evidence)

After each decision is made, capture it in a running decisions list.

## Step 4: Implementation Plan

Once all key decisions are made, compile them into an implementation plan:

```markdown
## Planning Rework — Implementation Plan

### Decisions Made
[Numbered list of all decisions from Step 3]

### Files to Change
[For each file: what changes, estimated scope]

### Migration Considerations
[Any backwards compatibility concerns, existing projects affected]

### Execution Order
[Which changes should land first, dependencies between changes]

### Risk Assessment
[What could go wrong, how to mitigate]
```

Use AskUserQuestion to confirm the plan before any implementation begins:
- header: "Implementation plan"
- question: "This is the complete implementation plan. Ready to proceed?"
- options:
  - "Looks good — let's implement" — Approve and begin
  - "Adjustments needed" — I want to change some decisions
  - "Save plan for later" — Write plan to a file, implement in a future session

If "Save plan for later", write the implementation plan to `./prompts/002-planning-rework-implementation.md` so it can be executed in a fresh context.
</collaboration>

<guidelines>
## Operating Guidelines

- **Patience over speed.** This is a design session, not a sprint. Spend time understanding before proposing.
- **Evidence over opinion.** When recommending, cite specific findings from the research agents.
- **User judgment is final.** Present options and recommendations, but the user decides. Don't argue past one pushback.
- **Incremental decisions.** Don't try to solve everything at once. Work through decisions one at a time.
- **Context awareness.** If the context window is getting heavy during brainstorming, suggest saving progress and continuing in a fresh window.
- **AskUserQuestion liberally.** Every fork in the road should be a question, not an assumption. The user explicitly wants collaborative exploration.
- **No premature implementation.** Do NOT edit any files during this session. This is research and design only. Implementation happens after the plan is approved.
</guidelines>

<success_criteria>
- ms-meta skill loaded, both tickets fetched via linear skill
- All 3 research agents launched in parallel and returned findings
- Findings synthesized and presented clearly
- User engaged in collaborative design via AskUserQuestion at every decision point
- All key decisions documented
- Implementation plan compiled and approved (or saved for later)
- No files modified — this is a research/design session only
</success_criteria>
