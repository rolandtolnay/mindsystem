---
name: ms:research-phase
description: Research how to implement a phase before planning
argument-hint: "[phase]"
allowed-tools:
  - Read
  - Bash
  - Task
  - Write
  - AskUserQuestion
---

<objective>
Research how to implement a phase by spawning 3 parallel specialized agents, then synthesizing their findings into RESEARCH.md.

**Orchestrator role:** Parse phase, validate, pre-scan project context, spawn 3 agents (external docs, codebase patterns, best practices), synthesize findings, resolve conflicts, write RESEARCH.md.
</objective>

<context>
Phase number: $ARGUMENTS (required)

**Resolve phase:**
```bash
ms-tools find-phase "$ARGUMENTS"
```

Check for existing research:
```bash
ms-tools check-artifact "$ARGUMENTS" RESEARCH
```
</context>

<process>

## 1. Parse and Validate Phase

Use `find-phase` output from context. **If phase not found (dir is null):** Error and exit. **If found:** Extract phase number, name, description from ROADMAP.md.

## 2. Check Existing Research

```bash
ls .planning/phases/${PHASE}-*/RESEARCH.md 2>/dev/null
```

**If exists:** Offer: 1) Update research, 2) View existing, 3) Skip. Wait for response.

**If doesn't exist:** Continue.

## 3. Pre-scan Project Context

Gather baseline context that all agents need:

```bash
# Dependency file (first 100 lines)
cat pubspec.yaml package.json Gemfile requirements.txt go.mod pyproject.toml 2>/dev/null | head -100

# Phase context from roadmap
grep -A20 "Phase ${PHASE}:" .planning/ROADMAP.md

# Requirements
cat .planning/REQUIREMENTS.md 2>/dev/null

# Phase-specific context and design
cat .planning/phases/${PHASE}-*/${PHASE}-CONTEXT.md 2>/dev/null
cat .planning/phases/${PHASE}-*/${PHASE}-DESIGN.md 2>/dev/null

# Locked decisions
grep -A30 "### Decisions Made" .planning/STATE.md 2>/dev/null

# Prior knowledge — match subsystem(s) by comparing phase description against config.json names
jq -r '.subsystems[]' .planning/config.json 2>/dev/null
cat .planning/knowledge/{matched_subsystem}.md 2>/dev/null
```

Extract from pre-scan:
- `existing_tech`: Libraries already in the project (from dependency file)
- `phase_description`: What this phase aims to build
- `phase_requirements`: Specific requirements
- `locked_decisions`: From CONTEXT.md and STATE.md
- `design_specs`: From DESIGN.md if exists
- `prior_knowledge`: From `.planning/knowledge/{subsystem}.md` — prior decisions, known pitfalls, architecture patterns (so agents don't re-research settled decisions)

## 4. Determine Research Scope

Research modes:
- **ecosystem** (default): Survey available tools, libraries, and integration options
- **feasibility**: Assess whether current stack can support the requirements
- **implementation**: Concrete how-to patterns and step-by-step approaches
- **comparison**: Evaluate alternatives side-by-side with tradeoffs

Frame the research question based on mode + phase description. Present to user:

```
Research scope for Phase {N}: {name}

Mode: {mode}
Question: {framed_question}
Existing tech: {existing_tech_summary}

Spawning 3 parallel agents:
1. External Docs — library documentation, APIs, code examples
2. Codebase Patterns — existing patterns, learnings, established conventions
3. Best Practices — community consensus, pitfalls, SOTA

Proceed? (yes / adjust scope / change mode)
```

## 5. Spawn 3 Agents in Parallel

Announce: "Spawning 3 research agents in parallel..."

All 3 receive pre-scan context (existing tech, phase description, requirements, locked decisions, design specs if any). Spawn all 3 in a single message using the Task tool.

### Agent 1: External Docs (ms-researcher)

```
Task(
  prompt="
<research_type>
Phase Research — External Documentation focus.
</research_type>

<focus>
Library documentation, APIs, version-specific behavior, verified code examples.
Use the ms-lookup CLI for library docs and deep research:
  ms-lookup docs <library> '<query>'
  ms-lookup deep '<query>'
Use WebSearch for ecosystem discovery.
Focus on finding authoritative, current documentation for the libraries and tools
needed to implement this phase.
</focus>

<existing_tech>
{existing_tech from pre-scan — so agent knows what's already in the project}
</existing_tech>

<prior_knowledge>
{prior_decisions, known_pitfalls, architecture_patterns from knowledge files — so agents don't re-research settled decisions}
</prior_knowledge>

<objective>
Research external documentation for Phase {N}: {name}
Mode: {mode}
</objective>

<context>
{phase_description, requirements, locked_decisions, design_specs}
</context>

<downstream_consumer>
Your findings feed into orchestrator synthesis -> RESEARCH.md sections:
- Standard Stack (libraries, versions, install commands)
- Architecture Patterns (library-recommended patterns)
- Don't Hand-Roll (library solutions for common problems)
- Code Examples (verified from official docs)
- State of the Art (latest approaches, deprecated patterns)
Be prescriptive. Specific versions. Verified code.
</downstream_consumer>

<output>
Return findings as structured text. Do NOT write to filesystem.
Format:
## EXTERNAL DOCS FINDINGS
### Recommended Libraries (name, version, purpose, install)
### API Patterns & Code Examples (verified from docs)
### Architecture Recommendations (from library docs)
### Don't Hand-Roll (library solutions exist for these)
### Version Constraints & Compatibility
### Confidence (HIGH/MEDIUM/LOW per section with sources)
Complete your built-in verification protocol and quality checklist before returning findings.
</output>
",
  subagent_type="ms-researcher",
  description="External docs: Phase {N}"
)
```

### Agent 2: Codebase Patterns (ms-codebase-researcher)

```
Task(
  prompt="
<objective>
Analyze project codebase for patterns relevant to Phase {N}: {name}
</objective>

<research_question>
{framed_question}
</research_question>

<phase_context>
{phase_description, requirements, locked_decisions}
</phase_context>

<existing_tech>
{existing_tech from pre-scan}
</existing_tech>

<prior_knowledge>
{prior_decisions, known_pitfalls, architecture_patterns from knowledge files — so agents don't re-research settled decisions}
</prior_knowledge>

<scan_hints>
{keywords extracted from phase description for targeted scanning}
</scan_hints>

<quality>
Complete your built-in success criteria checklist before returning findings.
</quality>
",
  subagent_type="ms-codebase-researcher",
  description="Codebase patterns: Phase {N}"
)
```

### Agent 3: Best Practices (ms-researcher)

```
Task(
  prompt="
<research_type>
Phase Research — Best Practices & Community Consensus focus.
</research_type>

<focus>
Community consensus, common pitfalls, proven approaches, state of the art.
Use the ms-lookup CLI for deep research on high-value questions:
  ms-lookup deep '<query>'
Use WebSearch for community articles, blog posts, Stack Overflow patterns.
Focus on what practitioners recommend and what mistakes to avoid.
</focus>

<existing_tech>
{existing_tech from pre-scan}
</existing_tech>

<prior_knowledge>
{prior_decisions, known_pitfalls, architecture_patterns from knowledge files — so agents don't re-research settled decisions}
</prior_knowledge>

<objective>
Research best practices for Phase {N}: {name}
Mode: {mode}
</objective>

<context>
{phase_description, requirements, locked_decisions, design_specs}
</context>

<downstream_consumer>
Your findings feed into orchestrator synthesis -> RESEARCH.md sections:
- Common Pitfalls (community war stories, warning signs)
- State of the Art (current vs deprecated approaches)
- Architecture Patterns (industry patterns, not library-specific)
- Don't Hand-Roll (community-known solved problems)
- Alternatives Considered (why X over Y)
Be prescriptive. Cite sources. Flag confidence levels.
</downstream_consumer>

<output>
Return findings as structured text. Do NOT write to filesystem.
Format:
## BEST PRACTICES FINDINGS
### Recommended Approaches (community consensus)
### Common Pitfalls (what goes wrong, warning signs, prevention)
### State of the Art (current vs deprecated, when things changed)
### Alternative Approaches (what else exists, why not chosen)
### Industry Patterns (architecture, testing, deployment)
### Confidence (HIGH/MEDIUM/LOW per section with sources)
Complete your built-in verification protocol and quality checklist before returning findings.
</output>
",
  subagent_type="ms-researcher",
  description="Best practices: Phase {N}"
)
```

## 6. Synthesize Findings

After all 3 agents return, read their structured outputs. Map findings to RESEARCH.md sections:

| RESEARCH.md Section | External Docs | Codebase | Best Practices | Synthesis Rule |
|---------------------|--------------|----------|----------------|----------------|
| Summary | Key libraries found | What exists already | Community direction | 2-3 paragraph synthesis |
| Standard Stack | Recommended + versions | Already in project | Community recommended | Merge: keep existing when sufficient, add new when needed |
| Architecture Patterns | Library-recommended | Established project patterns | Industry patterns | Follow existing; adopt recommended for new capabilities |
| Don't Hand-Roll | Library solutions | Internal solutions | Solved problems | Union of all three |
| Common Pitfalls | Library-specific gotchas | Past failures/learnings | Community war stories | Union, deduplicate |
| Code Examples | From official docs | From project | From community | Prefer official docs; show project examples for "how we do it here" |
| State of the Art | Latest versions/APIs | — | Current vs deprecated | Combine external + community |

**Conflict resolution:** If external recommends library X but project already uses library Y for the same purpose, present conflict to user via AskUserQuestion:
- Options: "Keep existing [Y]" / "Switch to recommended [X]" / "Use both (different purposes)" / "Something else"
- Record decision in RESEARCH.md

**Source attribution:** In `<sources>` section, prefix findings with their agent origin: "From external docs:", "From codebase analysis:", "From best practices:"

Write RESEARCH.md to `.planning/phases/{phase}-{slug}/{phase}-RESEARCH.md` using the standard template structure (semantic XML tags: `<research_summary>`, `<standard_stack>`, `<architecture_patterns>`, `<dont_hand_roll>`, `<common_pitfalls>`, `<code_examples>`, `<sota_updates>`, `<open_questions>`, `<sources>`, `<metadata>`).

## 7. Commit and Present

```bash
git add .planning/phases/${PHASE}-*/*-RESEARCH.md
git commit -m "docs: complete research for phase ${PHASE}"
```

Display research summary. Read `~/.claude/mindsystem/references/prework-status.md` to show what's done vs still needed for this phase.

**Post-synthesis routing:**

Scan the synthesized RESEARCH.md for LOW confidence sections and significant open questions.

If all sections HIGH/MEDIUM confidence with no major gaps, use AskUserQuestion:
1. Proceed to planning
2. Dig deeper into specific area
3. Review full research

If any section has LOW confidence or significant open questions, flag the weak areas explicitly, then use AskUserQuestion:
1. Dig deeper into [specific LOW area] — re-run targeted agent
2. Try different research mode (e.g., ecosystem -> implementation)
3. Proceed to planning with caveats noted
4. Review full research

## 8. Update Last Command

Update `.planning/STATE.md` Last Command field:
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:research-phase $ARGUMENTS | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line

</process>

<checkpoint_handling>

**With parallel agents:**
- Wait for ALL 3 agents to complete before synthesizing
- If any agent returns CHECKPOINT: present all checkpoints after other agents finish, handle sequentially
- If any agent returns BLOCKED: report which failed, offer to retry that agent or proceed with 2/3 findings

**Continuation mechanics:**
When an agent returns CHECKPOINT, its text response contains partial findings. To continue:
1. Capture the checkpointed agent's full text response
2. Present the checkpoint reason to the user, get their input
3. Spawn a fresh agent of the same type, injecting the captured text as inline content in `<prior_state>`

The `{partial_findings}` placeholder in the continuation template is the agent's raw text response, not a file reference. Read `mindsystem/templates/research-subagent-prompt.md` Continuation section for the prompt template.

</checkpoint_handling>

<success_criteria>
- [ ] Conflicts reconciled (with user input if needed)
- [ ] RESEARCH.md synthesized and written
- [ ] 3 agents spawned in parallel (external-docs, codebase-patterns, best-practices)
- [ ] All 3 agent results received
- [ ] RESEARCH.md committed
- [ ] User knows next steps
</success_criteria>
