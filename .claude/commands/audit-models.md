---
description: Audit subagent model assignments for quality or budget optimization
argument-hint: "<quality|budget>"
---

<objective>
Audit all Mindsystem subagent model assignments against current model capability benchmarks. Recommend optimal model for each agent based on the audit mode:

- **quality** — Maximize output quality. Only downgrade where output is effectively identical.
- **budget** — Minimize cost. Keep larger models only where the quality gap impacts downstream results.
</objective>

<context>
- Audit mode: $ARGUMENTS
</context>

<process>

<step name="validate_mode">

Parse `$ARGUMENTS` as audit mode. Must be `quality` or `budget`.

If empty or invalid, use AskUserQuestion:
- header: "Audit mode"
- question: "Which audit mode should this analysis use?"
- options:
  - "Quality" — Optimize for output quality, minimize model downgrades
  - "Budget" — Optimize for cost savings, keep larger models only where critical

</step>

<step name="confirm_references">

Present the default model reference paths and confirm with user via AskUserQuestion:

- header: "Model refs"
- question: "These are the model reference documents that will be used for benchmark data. Are they current, or do you have updated versions?"
- options:
  - "Use defaults" — Read `references/models/claude-sonnet-4-6.md`, `references/models/claude-opus-4-6.md`, and `references/models/claude-haiku-4-5.md`
  - "I have updated references" — Provide new file paths or URLs

If user provides new paths or URLs, use those instead. If URLs, fetch content with WebFetch.

**Do NOT read the reference files yet.** Wait until confirmed.

</step>

<step name="read_references">

Read the confirmed model reference documents. For quality mode, read Sonnet and Opus. For budget mode, read all three (Sonnet, Opus, and Haiku).

Extract:

- Key benchmark comparisons (SWE-bench, Terminal-Bench, HLE, ARC-AGI-2, BrowseComp, tool use, etc.)
- Qualitative strengths per model (deep reasoning, design, instruction following, etc.)
- Areas where each model leads, matches, or trails
- Pricing per model for cost analysis

Summarize into comparison tables: Opus vs Sonnet gap, and (budget mode) Sonnet vs Haiku gap.

</step>

<step name="discover_agents">

Discover all current agents dynamically:

```bash
ls agents/ms-*.md
```

Count total agents and split into batches of ~7 for parallel exploration.

</step>

<step name="explore_agents">

Spawn parallel Explore agents (Task tool, `subagent_type: Explore`) — one per batch. Each agent reads its assigned agent files and extracts for EACH agent:

1. **Agent name** (filename without `.md`)
2. **Current model** (from YAML frontmatter `model:` field)
3. **Purpose** (1-2 sentences)
4. **Cognitive demand** — classify: deep reasoning/planning/judgment vs. analytical/structural vs. mechanical/templated.
5. **Tools available** (from frontmatter)
6. **Downstream impact** — what consumes this agent's output? Does quality here propagate to other artifacts?

Return a structured table per batch.

</step>

<step name="analyze_and_recommend">

Using the model benchmark data and agent profiles, analyze each agent and recommend a model assignment.

**Quality mode reasoning:**
- Default to the strongest model available (currently opus)
- Downgrade only where benchmarks show near-parity for the agent's specific workload
- Sonnet is appropriate when the task is primarily: tool use, pattern application, structured extraction, code modification within clear guidelines
- Opus is appropriate when the task requires: deep reasoning, novel problem-solving, architectural judgment, hypothesis-driven investigation, strategic synthesis

**Budget mode reasoning (3-tier evaluation):**
- Default to sonnet as the baseline cost-effective model
- Upgrade to opus only where the quality gap materially impacts downstream results (novel reasoning, hypothesis-driven investigation, creative synthesis)
- **Downgrade to haiku** for agents meeting ALL of these criteria:
  - Mechanical/templated or read-only work (no code generation requiring SWE-bench reliability)
  - Structured/prescribed output format (not creative or open-ended)
  - Prompt complexity within haiku's instruction-following budget (~150-250 instructions)
  - Failure is low-cost or easily caught (temporary artifacts, user-reviewed output, non-blocking)
- Consider downstream propagation: a synthesis agent feeding roadmap creation has higher stakes than a mock generator

Present a full audit table:

| Agent | Current | Recommended | Change? | Rationale |
|-------|---------|-------------|---------|-----------|

Include a summary section highlighting:
- Total agents audited
- Number of recommended changes
- Key reasoning for each change

</step>

<step name="confirm_changes">

If there are recommended changes, present them clearly and use AskUserQuestion:

- header: "Apply changes"
- question: "Apply these model assignment changes?"
- options:
  - "Apply all" — Update all recommended agents
  - "Let me pick" — I'll select which changes to apply
  - "No changes" — Review only, don't modify files

If "Let me pick": use AskUserQuestion (multiSelect) listing each recommended change.

If "No changes": end with the audit summary.

</step>

<step name="apply_changes">

For each confirmed change, edit the agent's YAML frontmatter `model:` field.

After all edits, show a summary of changes made.

</step>

</process>

<success_criteria>
- Each recommendation includes specific benchmark-backed rationale
- Quality vs. budget reasoning clearly differentiated
- Parallel explore agents used for agent analysis
- Model references confirmed with user before reading (lazy load)
- User confirms before any files are modified; changes applied only to confirmed agents
</success_criteria>
