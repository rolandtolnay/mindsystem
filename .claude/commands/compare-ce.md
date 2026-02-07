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

## Step 3: Deep Exploration — Compound Engineering (3 parallel agents)

Launch 3 Explore agents in parallel to fully map how CE handles the area. Each agent covers one architectural layer so it can read files completely rather than skimming.

### Agent CE-1: Orchestration Layer
Prompt: "Explore references/compound-engineering/commands/ and references/compound-engineering/commands/workflows/ thoroughly for everything related to [AREA].

Read every command file that touches this area — including the full file, not just frontmatter. I need to understand:
1. What commands handle this area (list exact file paths)
2. How the command is triggered and what arguments it accepts
3. The full execution flow — what steps, what agents are spawned, what skills are referenced
4. Post-completion routing (what options are offered to the user after the command finishes)
5. Any notable patterns: auto-invoke triggers, preconditions XML, AskUserQuestion usage, parallel subagent orchestration

Return a structured analysis organized by command, with exact file paths and key excerpts."

### Agent CE-2: Agent Layer
Prompt: "Explore references/compound-engineering/agents/ thoroughly for everything related to [AREA]. Check all subdirectories: review/, research/, design/, workflow/, docs/.

Read the full system prompt of every agent that touches this area. I need to understand:
1. What agents handle this area (list exact file paths)
2. Each agent's role, expertise, methodology, and output format
3. How agents are specialized — what makes each one distinct from others in the same area
4. What tools each agent has access to
5. Any persona-based patterns (named reviewers, opinionated styles)
6. How agent outputs are structured and consumed by commands

Return a structured analysis organized by agent, with exact file paths and key excerpts from their system prompts."

### Agent CE-3: Skills/Knowledge Layer
Prompt: "Explore references/compound-engineering/skills/ thoroughly for everything related to [AREA]. Each skill lives in its own directory with SKILL.md as the entry point.

IMPORTANT: For each relevant skill, also read files inside its subdirectories — references/, templates/, scripts/, assets/. These contain the deep domain knowledge that makes skills effective.

I need to understand:
1. What skills handle this area (list exact file paths including subdirectory files)
2. The skill's core concepts and principles
3. What reference files, templates, and scripts support it
4. How the skill is invoked (by commands, by agents, or directly by the user)
5. The knowledge structure — how information is organized within the skill
6. Any file-based systems the skill creates or maintains (e.g., docs/solutions/, todos/)

Return a structured analysis organized by skill, with exact file paths for all files read."

**Wait for all 3 CE agents to complete before proceeding.**

## Step 4: Deep Exploration — Mindsystem (3 parallel agents, informed by CE findings)

Using the CE findings from Step 3, launch 3 Explore agents in parallel. Each agent's prompt references specific CE patterns discovered, directing them to find MS equivalents, alternatives, or gaps.

### Agent MS-1: Orchestration Layer
Prompt: "Explore commands/ms/ and mindsystem/workflows/ thoroughly for everything related to [AREA].

**CE context for targeted search:** [Insert specific CE commands and workflows found in Step 3 — e.g., 'CE uses /workflows:compound to capture solved problems, triggered by auto-invoke phrases like "that worked". Find everything in MS related to knowledge capture, learning workflows, or post-completion documentation.']

Read every command and workflow file that touches this area — full files, not just frontmatter. I need to understand:
1. What commands and workflows handle this area (list exact file paths)
2. The command → workflow delegation chain for each
3. How the workflow is structured (steps, priorities, bash examples)
4. User interaction model (AskUserQuestion usage, checkpoint types)
5. Post-completion routing (next-up format, available options)
6. Gaps: what aspects of the CE approach have no MS equivalent

Return a structured analysis organized by command/workflow, with exact file paths."

### Agent MS-2: Agent Layer
Prompt: "Explore agents/ thoroughly for everything related to [AREA].

**CE context for targeted search:** [Insert specific CE agents found in Step 3 — e.g., 'CE has 5 parallel research agents (framework-docs-researcher, best-practices-researcher, git-history-analyzer, learnings-researcher, repo-research-analyst). Find all MS agents that handle research, investigation, or knowledge gathering.']

Read the full definition of every agent that touches this area. I need to understand:
1. What agents handle this area (list exact file paths)
2. Each agent's role section, required_reading, and execution steps
3. What model and tools each agent uses
4. How agents are spawned (by which commands/workflows)
5. How agent outputs are structured (SUMMARY.md, VERIFICATION.md, etc.)
6. Gaps: what CE agent capabilities have no MS equivalent

Return a structured analysis organized by agent, with exact file paths."

### Agent MS-3: Knowledge Layer
Prompt: "Explore mindsystem/templates/, mindsystem/references/, .claude/commands/, and scripts/ thoroughly for everything related to [AREA].

**CE context for targeted search:** [Insert specific CE skills and knowledge systems found in Step 3 — e.g., 'CE has a compound-docs skill that maintains docs/solutions/{category}/ with YAML frontmatter for institutional knowledge. Find all MS templates, references, and scripts related to knowledge capture, documentation, or learning.']

I need to understand:
1. What templates, references, and scripts handle this area (list exact file paths)
2. Template structure — placeholders, expected output format
3. Reference content — principles, patterns, guidelines
4. How templates and references are consumed (which commands/workflows/agents reference them via @-paths)
5. Any project-specific commands in .claude/commands/ related to this area
6. Gaps: what CE knowledge structures have no MS equivalent

Return a structured analysis organized by file type, with exact file paths."

**Wait for all 3 MS agents to complete before proceeding.**

## Step 5: Synthesize Comparison

Using results from all 6 agents (3 CE + 3 MS) plus ms-meta knowledge, build a detailed comparison across these dimensions:

- **Workflow design**: How each system structures the process
- **Agent/subagent architecture**: How work is delegated and parallelized
- **Knowledge flow**: How information moves between components
- **User interaction model**: How the user participates and controls the process
- **Output artifacts**: What gets produced and how it's used downstream
- **Extensibility**: How easy it is to modify or extend

## Step 5: Pareto Evaluation

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

## Step 6: Write Proposal

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

## Step 7: Present Summary

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
