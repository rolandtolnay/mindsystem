<objective>
Create a comprehensive proposal for migrating the gsd-researcher agent from MCP-based tools (Context7 MCP, Perplexity MCP) to a custom CLI tool that abstracts real-time data access.

**Why this matters:**
- Claude Code bug prevents subagents from accessing MCP tools — gsd-researcher currently cannot use Context7 at all
- MCP tool definitions consume significant context window just by existing
- Perplexity MCP returns outsized responses (15k+ tokens) that exhaust agent context
- CLI abstraction enables future extensibility and reusability across projects

**End goal:** A working proposal document that can be executed to build:
1. A Python CLI tool (`gsd-research`) that wraps Context7 and Perplexity APIs
2. An updated gsd-researcher agent that uses Bash calls to the CLI instead of MCP tools
3. Design decisions on abstraction level, command structure, and output formatting
</objective>

<execution_context>
This prompt orchestrates a multi-stage research and design process. Each stage builds on the previous.

**Reference files to load:**
- @proposals/beyond-mcp.md — High-level principles for MCP alternatives
- @agents/gsd-researcher.md — Current researcher implementation
- @docs/context7-api.md — Context7 REST API specification
- @CLAUDE.md — GSD contributor guidelines and principles
</execution_context>

<process>

<stage name="understand_gsd_principles">
## Stage 1: Understand GSD System Principles

**Action:** Invoke the gsd-meta skill to deeply understand:
- Subagent design patterns in GSD
- Context engineering principles (the 50% rule, context rot)
- How agents communicate with external tools
- Deviation rules and structured returns

**Prompt for gsd-meta:**
```
I need deep understanding of GSD principles for designing a CLI tool that gsd-researcher will use. Specifically:
1. How do subagents currently access external data?
2. What are the context preservation strategies?
3. How should tool output be structured to minimize context consumption?
4. What makes a good subagent tool interface?
```

**Capture:** Key principles that must guide CLI design.
</stage>

<stage name="analyze_current_implementation">
## Stage 2: Analyze Current Researcher Implementation

Read and analyze these files to understand the current system:

**Files to read:**
- `agents/gsd-researcher.md` — Full agent definition
- `commands/gsd/research-phase.md` — How researcher is spawned
- `commands/gsd/research-project.md` — Project-level research flow
- `get-shit-done/workflows/research-phase.md` — Research workflow details
- `get-shit-done/templates/research-subagent-prompt.md` — Prompt template

**Extract and document:**
1. Current tool usage patterns (which MCP tools, when, how)
2. Research modes (ecosystem, feasibility, implementation, comparison)
3. Source hierarchy (Context7 → Official docs → WebSearch)
4. Verification protocol (how findings are validated)
5. Output formats (RESEARCH.md structure, confidence levels)
6. What works well vs. what's problematic about current design

**Deliverable:** A "Current State Analysis" section documenting how the researcher works today.
</stage>

<stage name="research_cli_patterns">
## Stage 3: Research CLI Design Patterns

Using the Task tool, spawn a research agent to investigate:

**Research questions:**
1. What CLI design patterns work best for AI agent consumption?
2. How should multi-API CLIs structure their commands (thin wrapper vs semantic abstraction)?
3. What output formatting minimizes token usage while preserving information?
4. How do production CLI tools handle response truncation/summarization?

**Sources to check:**
- The beyond-mcp repository patterns (already read)
- Best practices for building CLI tools for LLM consumption
- How other projects abstract multiple APIs behind single interfaces

**Use Task tool with subagent_type="research-technical":**
```
Research CLI design patterns for LLM-consumed tools. Focus on:
1. Command structure patterns (thin wrapper vs semantic commands vs task-oriented)
2. Output formatting for minimal token usage
3. Response truncation/summarization strategies
4. Multi-API abstraction patterns

Context: Building a CLI that wraps Context7 (library docs) and Perplexity (web search) APIs for a research subagent.
```

**Deliverable:** "CLI Design Research" section with patterns and recommendations.
</stage>

<stage name="design_abstraction_level">
## Stage 4: Design CLI Abstraction Level

Based on research, evaluate three abstraction approaches:

**Option A: Thin Wrapper**
```bash
gsd-research context7 resolve "react"
gsd-research context7 query "/vercel/next.js" "app router setup"
gsd-research perplexity search "react state management 2026"
gsd-research perplexity research "best practices for..."
```
- Pros: Full control, transparent, matches MCP 1:1
- Cons: Agent must know which API to use, more calls

**Option B: Semantic Commands**
```bash
gsd-research docs "nextjs" "app router setup"     # Context7
gsd-research web "react state management 2026"    # Perplexity search
gsd-research deep "authentication best practices" # Perplexity research
```
- Pros: Simpler interface, clear intent
- Cons: Less flexibility, may not cover all use cases

**Option C: Research-Oriented Commands**
```bash
gsd-research library "nextjs" --topic "routing"   # Full library research
gsd-research verify "claim about X"               # Cross-reference claim
gsd-research compare "prisma" "drizzle"           # Compare two options
gsd-research ecosystem "react state management"   # Survey the landscape
```
- Pros: Matches researcher modes, high-level
- Cons: More complex implementation, may be over-engineered

**Analyze:**
- How does each option impact researcher agent effectiveness?
- Which aligns best with GSD principles (context preservation, simplicity)?
- What's the minimum viable interface that enables all research modes?

**Use AskUserQuestion** to present options with pros/cons and get user input on preferred approach.
</stage>

<stage name="design_output_format">
## Stage 5: Design Output Format

The CLI must output JSON that:
1. Minimizes token usage (no verbose prose)
2. Preserves essential information (sources, confidence indicators)
3. Is easily parseable by the researcher agent
4. Supports smart deduplication (cache identical queries)

**Design decisions to make:**
- Maximum response size (e.g., 2000 tokens per call?)
- Truncation strategy (most relevant first, with "more available" indicator?)
- Metadata to include (source URL, confidence score, token count?)
- Error format

**Example output structure:**
```json
{
  "query": "nextjs app router setup",
  "source": "context7",
  "library_id": "/vercel/next.js",
  "snippets": [
    {
      "title": "App Router Getting Started",
      "content": "...",
      "tokens": 450,
      "url": "https://..."
    }
  ],
  "total_available": 15,
  "returned": 3,
  "cache_hit": false
}
```

**Deliverable:** "Output Format Specification" section.
</stage>

<stage name="design_updated_researcher">
## Stage 6: Design Updated Researcher Agent

Based on all prior stages, design how the updated gsd-researcher agent will work:

**Changes to agent definition:**
- Remove MCP tools from `tools:` list
- Add Bash to tools (for CLI invocation)
- Update `<tool_strategy>` section with CLI usage patterns
- Update examples to show Bash calls instead of MCP

**New tool strategy section:**
```xml
<tool_strategy>
## gsd-research CLI: Primary Tool

The gsd-research CLI provides access to library documentation and web search.

**For library documentation:**
```bash
gsd-research docs <library> "<query>"
```

**For web search:**
```bash
gsd-research web "<query>"
```

**For deep research:**
```bash
gsd-research deep "<query>"
```

**Best practices:**
- Start with docs for library-specific questions
- Use web for ecosystem discovery
- Use deep for comprehensive research topics
- Parse JSON output, check `returned` vs `total_available`
- Cache-aware: identical queries return cached results
</tool_strategy>
```

**Deliverable:** "Updated Researcher Agent Design" section with full diff from current.
</stage>

<stage name="synthesize_proposal">
## Stage 7: Synthesize Implementation Proposal

Compile all findings into a proposal document at `.planning/proposals/cli-research-tool.md`:

**Proposal structure:**
```markdown
# Proposal: CLI-Based Research Tool for GSD

## Executive Summary
[2-3 paragraphs summarizing the change]

## Problem Statement
[Current issues with MCP approach]

## Proposed Solution
[High-level description of CLI tool + researcher changes]

## CLI Tool Design

### Commands
[Final command structure with examples]

### Output Format
[JSON schema and examples]

### Caching Strategy
[Deduplication approach]

### Error Handling
[Error format and retry strategy]

## Implementation Plan

### Phase 1: CLI Tool (scripts/gsd-research/)
- [ ] Project structure (Python with uv)
- [ ] Context7 integration
- [ ] Perplexity integration
- [ ] Output formatting
- [ ] Caching layer
- [ ] Error handling

### Phase 2: Researcher Agent Update
- [ ] Update agents/gsd-researcher.md
- [ ] Update tool_strategy section
- [ ] Update examples
- [ ] Test with /gsd:research-phase

### Phase 3: Documentation
- [ ] CLI usage documentation
- [ ] Migration notes for users

## API Requirements
- CONTEXT7_API_KEY environment variable
- PERPLEXITY_API_KEY environment variable

## Risk Assessment
[What could go wrong, mitigations]

## Success Criteria
[How we know this worked]
```
</stage>

</process>

<verification>
Before declaring the proposal complete, verify:
- [ ] All stages completed with documented findings
- [ ] User input gathered on key design decisions (abstraction level)
- [ ] CLI command structure finalized
- [ ] Output format specified with examples
- [ ] Updated researcher agent design documented
- [ ] Implementation plan is actionable (specific tasks, not vague)
- [ ] Proposal follows GSD principles (no enterprise patterns, context-aware)
</verification>

<success_criteria>
- Proposal document exists at `.planning/proposals/cli-research-tool.md`
- CLI design enables all current researcher modes (ecosystem, feasibility, implementation, comparison)
- Output format minimizes context consumption vs current MCP approach
- Updated researcher agent design is complete and ready to implement
- User has approved key design decisions
</success_criteria>

<output>
After completing all stages, present:

1. **Summary of key decisions made**
2. **Link to proposal document**
3. **Recommended next steps** (e.g., "Run /gsd:plan-phase to create implementation plans")
</output>
