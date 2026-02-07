---
description: Compare Compound Engineering and Mindsystem approaches for a specific area, evaluate adoption opportunities
argument-hint: "<area to compare (e.g., knowledge compounding, planning workflow, code review)>"
allowed-tools: [Read, Glob, Grep, Task, AskUserQuestion, Write, Bash, Skill]
---

<objective>
Analyze how a specific engineering area works in Compound Engineering versus Mindsystem. Produce a comprehensive proposal document that:

1. Maps how the area works in each system (patterns, agents, commands, workflows)
2. Evaluates which Compound Engineering approaches would improve Mindsystem
3. Classifies recommendations as: port as-is, adapt for Mindsystem, or refactor existing Mindsystem artifacts
4. Estimates refactoring cost versus benefit for each recommendation

The user specifies an area to compare: $ARGUMENTS

Output: Single markdown file at `proposals/ce-<area-slug>.md`
</objective>

<execution_context>
Compound Engineering source: @references/compound-engineering/
Mindsystem knowledge: Invoke the `ms-meta` skill to gain deep understanding of Mindsystem practices, patterns, architecture, and design philosophy before analyzing
</execution_context>

<process>

## Step 1: Clarify Intent

Use AskUserQuestion to understand the problem the user is trying to solve. Ask questions one at a time. Adapt based on the area specified in $ARGUMENTS.

The user typically arrives with a broad area of interest (e.g., "knowledge compounding", "code review") and wants to understand what makes CE effective in that area, how MS currently handles it, and what improvements are possible. Implementation decisions (how aggressive, what constraints) come AFTER the user reads the proposal — do NOT ask about those upfront.

**First question — always ask:**
Confirm the specific area and understand what triggered the interest. Example: "You want to explore *knowledge compounding*. What prompted this — did you notice something specific in CE that caught your eye, or is this an area where you feel MS could be stronger?"

**Follow-up questions — ask only if the area is ambiguous or broad:**
- The area name maps to multiple distinct concerns — which aspect matters most? (e.g., "code review" could mean review quality, review workflow, reviewer personas, automated checks)
- Are there specific CE commands/agents/skills you've already noticed and want to make sure the analysis covers?
- What's the current experience like in MS for this area — what works, what feels lacking?
- Is there a related area that should be included in the same analysis? (e.g., "planning" might naturally include "brainstorming" or "research")

**Goal of clarification:**
Ensure the exploration agents search broadly enough to capture everything relevant, and the proposal covers all sub-areas the user cares about. The Pareto evaluation in the proposal will handle prioritization — the user decides on adoption after reading it.

**Stop asking when you know:**
- The scope of comparison (which sub-areas to include)
- What the user wants to understand (not what they want to implement — that comes later)

## Step 2: Gain Mindsystem Knowledge

Invoke the `ms-meta` skill to load deep knowledge about Mindsystem's architecture, patterns, and design philosophy. This ensures accurate comparison against Mindsystem's actual practices rather than assumptions.

## Step 3: Deep Exploration — Compound Engineering

Map how CE handles the area by exploring 3 architectural layers simultaneously.

**CRITICAL: Launch all 3 agents in a SINGLE message containing 3 parallel Task tool calls (subagent_type: Explore). Do NOT launch them one at a time.**

| Agent | Layer | Search Paths |
|-------|-------|-------------|
| CE-1 | Orchestration | `references/compound-engineering/commands/`, `references/compound-engineering/commands/workflows/` |
| CE-2 | Agents | `references/compound-engineering/agents/` and all subdirectories (`review/`, `research/`, `design/`, `workflow/`, `docs/`) |
| CE-3 | Skills/Knowledge | `references/compound-engineering/skills/` and all subdirectories (`references/`, `templates/`, `scripts/`, `assets/`) |

**Shared instructions for all 3 agents** — include in each prompt:
- Thoroughness: very thorough
- Read every file that touches [AREA] completely — full files, not just frontmatter
- Return a structured analysis with exact file paths and key excerpts
- Organize results by component (command, agent, or skill)

**Per-agent focus — append to each prompt:**

**CE-1** — For each command: trigger/arguments, full execution flow (steps, agents spawned, skills referenced), post-completion routing, notable patterns (auto-invoke triggers, preconditions XML, parallel subagent orchestration).

**CE-2** — For each agent: role/expertise/methodology, what makes it distinct from others in the area, tools available, persona-based patterns (named reviewers, opinionated styles), output format and how commands consume it.

**CE-3** — For each skill: core concepts/principles, all supporting files in subdirectories (these contain the deep domain knowledge), invocation method (by commands, agents, or user), knowledge organization structure, any file-based systems maintained (e.g., `docs/solutions/`, `todos/`).

**After dispatching all 3 agents in a single message, wait for all results before proceeding to Step 4. Do not start Step 4 until all 3 agents have returned.**

## Step 4: Deep Exploration — Mindsystem (informed by CE findings)

Using the CE findings from Step 3, explore Mindsystem's 3 architectural layers simultaneously. Each agent's prompt must reference specific CE patterns discovered in Step 3 to direct targeted search for MS equivalents, alternatives, or gaps.

**CRITICAL: Launch all 3 agents in a SINGLE message containing 3 parallel Task tool calls (subagent_type: Explore). Do NOT launch them one at a time.**

| Agent | Layer | Search Paths |
|-------|-------|-------------|
| MS-1 | Orchestration | `commands/ms/`, `mindsystem/workflows/` |
| MS-2 | Agents | `agents/` and all subdirectories |
| MS-3 | Knowledge | `mindsystem/templates/`, `mindsystem/references/`, `.claude/commands/`, `scripts/` |

**Shared instructions for all 3 agents** — include in each prompt:
- Thoroughness: very thorough
- Read every file that touches [AREA] completely — full files, not just frontmatter
- Return a structured analysis with exact file paths
- Explicitly identify gaps: what aspects of the CE approach have no MS equivalent
- **CE context for targeted search:** Include a summary of the specific CE patterns found in Step 3 relevant to this agent's layer, so it searches for equivalents rather than exploring generically

**Per-agent focus — append to each prompt:**

**MS-1** — For each command/workflow: the command → workflow delegation chain, workflow structure (steps, priorities, bash examples), user interaction model (AskUserQuestion usage, checkpoint types), post-completion routing (next-up format).

**MS-2** — For each agent: role section, required_reading, execution steps, model and tools used, which commands/workflows spawn it, output structure (SUMMARY.md, VERIFICATION.md, etc.).

**MS-3** — For each template/reference/script: template structure and placeholders, reference principles and patterns, how they're consumed (which commands/workflows/agents reference them via @-paths), any project-specific commands in `.claude/commands/` related to the area.

**After dispatching all 3 agents in a single message, wait for all results before proceeding to Step 5. Do not start Step 5 until all 3 agents have returned.**

## Step 5: Synthesize Comparison

Using results from all 6 agents (3 CE + 3 MS) plus ms-meta knowledge, build a detailed comparison across these dimensions:

- **Workflow design**: How each system structures the process
- **Agent/subagent architecture**: How work is delegated and parallelized
- **Knowledge flow**: How information moves between components
- **User interaction model**: How the user participates and controls the process
- **Output artifacts**: What gets produced and how it's used downstream
- **Extensibility**: How easy it is to modify or extend

## Step 6: Pareto Evaluation

Apply the Pareto principle: identify the 20% of Compound Engineering patterns that would deliver 80% of the improvement value if adopted in Mindsystem.

For each candidate pattern, evaluate:

**Adoption classification:**
- **Port as-is**: CE artifact (agent, command, skill) can be copied into Mindsystem with minimal changes (e.g., a standalone research agent)
- **Adapt for Mindsystem**: CE pattern is valuable but needs restructuring to fit Mindsystem's XML conventions, workflow delegation model, or progressive disclosure hierarchy
- **Refactor existing**: The CE approach reveals that an existing Mindsystem artifact should be refactored — guided by principles from CE but implemented in Mindsystem's idiom

**Cost-benefit for each:**
- **Refactoring cost**: What Mindsystem files change? How many? How deep are the changes? Does it break existing workflows?
- **Benefit**: What specific improvement does this bring? (better output quality, faster execution, less context waste, better user experience)
- **Risk**: What could go wrong? What existing functionality might break?
- **Dependencies**: Does this recommendation depend on other recommendations being adopted first?

## Step 7: Write Proposal

Create `proposals/ce-<area-slug>.md` with this structure:

```markdown
# CE Analysis: [Area Name]

> Comparing Compound Engineering and Mindsystem approaches to [area].
> Generated: [date]

## Executive Summary

[3-5 sentences: what was compared, key finding, top recommendation]

## How Compound Engineering Handles [Area]

### Overview
[High-level description of CE's approach]

### Key Components
[List of agents, commands, skills involved with file paths]

### Workflow
[Step-by-step process description]

### Distinctive Patterns
[What makes CE's approach notable]

## How Mindsystem Handles [Area]

### Overview
[High-level description of MS's approach]

### Key Components
[List of commands, agents, workflows, templates involved with file paths]

### Workflow
[Step-by-step process description]

### Current Limitations
[Gaps or pain points]

## Side-by-Side Comparison

| Dimension | Compound Engineering | Mindsystem | Assessment |
|-----------|---------------------|------------|------------|
| [dimension] | [CE approach] | [MS approach] | [which is stronger and why] |

## Recommendations

### High Impact (Adopt)

#### 1. [Recommendation Name]
- **Classification**: [Port as-is | Adapt | Refactor existing]
- **Source**: [CE file path(s)]
- **Target**: [MS file path(s) to create or modify]
- **What changes**: [Concrete description]
- **Cost**: [Low/Medium/High] — [explanation]
- **Benefit**: [Concrete improvement]
- **Dependencies**: [Other recommendations this depends on, or "None"]

### Medium Impact (Consider)
[Same structure]

### Low Impact (Optional)
[Same structure]

## Migration Considerations

### Breaking Changes
[Any recommendations that would break existing workflows]

### Incremental Adoption Path
[Suggested order of implementation to minimize risk]

### What NOT to Adopt
[CE patterns that don't fit Mindsystem's philosophy, with explanation]

## Open Questions
[Anything that needs further discussion before implementation]
```

## Step 8: Present Summary

Display a concise summary of the proposal:
- File location
- Number of recommendations by classification (port/adapt/refactor)
- Top 3 highest-impact recommendations
- Suggested next step: "Review the full proposal at `proposals/ce-<area-slug>.md`"

</process>

<success_criteria>
- User's intent fully clarified before analysis begins
- CE fully mapped first (3 parallel agents: orchestration, agents, skills) before MS exploration begins
- MS exploration informed by CE findings — agents search for specific equivalents, not generic patterns
- ms-meta skill invoked to ground Mindsystem analysis in actual architecture
- All 6 agents return structured analyses with exact file paths (not vague descriptions)
- Every recommendation classified as port/adapt/refactor with cost-benefit
- Pareto principle applied — recommendations prioritized by impact
- Proposal written to proposals/ as single comprehensive markdown file
- Cases where CE artifacts can be ported directly are clearly distinguished from those requiring adaptation or refactoring of existing Mindsystem artifacts
</success_criteria>
