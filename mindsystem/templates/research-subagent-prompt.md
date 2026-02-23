# Research Subagent Prompt Templates

Templates for the 3 parallel agents spawned by `/ms:research-phase`. The orchestrator constructs prompts inline. These templates serve as reference documentation.

---

## Common Context (injected into all 3 agents)

| Placeholder | Source |
|-------------|--------|
| `{existing_tech}` | Dependency file (pubspec.yaml / package.json / etc.) |
| `{phase_description}` | ROADMAP.md phase entry |
| `{requirements}` | REQUIREMENTS.md |
| `{locked_decisions}` | CONTEXT.md + STATE.md decisions |
| `{design_specs}` | DESIGN.md (if exists) |
| `{mode}` | Research mode: ecosystem / feasibility / implementation / comparison |
| `{framed_question}` | Mode + phase description combined into research question |
| `{scan_hints}` | Keywords extracted from phase description |

---

## Template 1: External Docs (ms-researcher)

**Focus:** Library documentation, APIs, verified code examples
**Tools emphasized:** ms-lookup docs, ms-lookup deep, WebSearch, WebFetch
**Returns:** Structured findings (not files)

```markdown
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
{existing_tech}
</existing_tech>

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
```

---

## Template 2: Codebase Patterns (ms-codebase-researcher)

**Focus:** Existing patterns, learnings, established conventions
**Tools emphasized:** Grep, Glob, Read
**Returns:** Structured findings (not files)

```markdown
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
{existing_tech}
</existing_tech>

<scan_hints>
{scan_hints}
</scan_hints>

<quality>
Complete your built-in success criteria checklist before returning findings.
</quality>
```

The agent's built-in `<what_to_scan>` section handles the systematic scan checklist (dependency file, source patterns, codebase docs, learnings, summaries, debug resolutions, adhoc summaries). The prompt only needs to provide context.

---

## Template 3: Best Practices (ms-researcher)

**Focus:** Community consensus, pitfalls, SOTA
**Tools emphasized:** ms-lookup deep, WebSearch
**Returns:** Structured findings (not files)

```markdown
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
{existing_tech}
</existing_tech>

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
```

---

## Continuation (for checkpoints)

If an agent returns a CHECKPOINT, spawn a fresh agent of the same type with:

`{partial_findings}` = the checkpointed agent's full text response (inline content, not a file reference). The orchestrator captures this from the Task result and injects it directly.

```markdown
<objective>
Continue research for Phase {N}: {name}
</objective>

<existing_tech>
{existing_tech}
</existing_tech>

<phase_context>
{phase_description, requirements, locked_decisions}
</phase_context>

<prior_state>
Research findings so far:
{partial_findings}
</prior_state>

<checkpoint_response>
**Type:** {checkpoint_type}
**Response:** {user_response}
</checkpoint_response>
```

---

**Note:** Research methodology, tool strategy (ms-lookup docs > Official > ms-lookup deep > WebSearch), verification protocols, and source confidence levels are baked into `ms-researcher`. Codebase scan methodology is baked into `ms-codebase-researcher`. These templates pass context only — and reinforce that built-in quality processes still apply.
