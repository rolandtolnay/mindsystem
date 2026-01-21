# Proposal: CLI-Based Research Tool for GSD

## Executive Summary

The gsd-researcher agent cannot use Context7 MCP tools due to a Claude Code bug preventing subagents from accessing MCP tools. This breaks access to authoritative library documentation during research.

This proposal introduces `gsd-research`, a Python CLI tool with two commands:
- **`docs`** — Query library documentation via Context7 API
- **`deep`** — Perform exhaustive multi-source research via Perplexity Research API

**Why not include web search?** Claude Code's built-in WebSearch is included free with Max subscription and works in subagents. Perplexity's basic search ($5/1k queries) doesn't justify the cost when WebSearch is free and adequate for ecosystem discovery.

**Key benefits:**
- Unblocks Context7 access for researcher agent (works around MCP bug)
- Adds deep research capability (unique — WebSearch can't do exhaustive synthesis)
- Reduces context consumption via response truncation
- Provides caching layer for repeated queries
- Simpler design (2 commands vs 3)

## Problem Statement

### Current Issues

1. **MCP Bug:** Claude Code subagents cannot access MCP tools — gsd-researcher's Context7 calls fail silently
2. **Missing Deep Research:** WebSearch finds sources but can't synthesize exhaustive multi-source reports
3. **No Control:** Cannot truncate or cache MCP responses when they do work

### Impact

- `/gsd:research-phase` and `/gsd:research-project` lack authoritative library documentation
- Research limited to WebSearch discovery without deep synthesis capability
- No workaround for Context7 access within current architecture

### What Works Fine

- **WebSearch:** Included free with Max subscription, works in subagents, adequate for ecosystem discovery
- **WebFetch:** Works for fetching specific URLs

## Proposed Solution

### High-Level Architecture

```
gsd-researcher agent
  ├── WebSearch (built-in) → Ecosystem discovery (free with Max)
  ├── WebFetch (built-in) → Specific URL content (free)
  └── Bash → gsd-research CLI
              ├── docs → Context7 REST API (library documentation)
              └── deep → Perplexity Research API (exhaustive synthesis)
```

### Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Abstraction level | Semantic commands | Fits researcher's intent patterns ("I need docs" vs "I need to call Context7") |
| Language | Python 3.11+ | GSD standard, excellent HTTP libraries, uv for packaging |
| CLI framework | typer | Better subcommand grouping than click, automatic help generation |
| HTTP client | httpx | Modern async support, connection pooling |
| Caching | diskcache | Simple file-based cache, survives process restarts |
| Output format | JSON | Machine-readable, parseable by agent |

## CLI Tool Design

### Commands

#### `gsd-research docs <library> "<query>"`

Query library documentation via Context7. Use for authoritative, version-aware API documentation.

```bash
# Example
gsd-research docs nextjs "app router setup"
gsd-research docs "react-three-fiber" "physics integration"
```

**Behavior:**
1. Resolve library name to Context7 library ID via `/v2/libs/search`
2. Query documentation via `/v2/context`
3. Truncate response to max tokens
4. Return JSON with snippets, sources, metadata

**When to use:** Library APIs, framework features, configuration options, version-specific behavior.

#### `gsd-research deep "<query>"`

Perform exhaustive multi-source research via Perplexity Research API. Use for comprehensive synthesis across many sources.

```bash
# Example
gsd-research deep "authentication patterns for SaaS applications"
gsd-research deep "WebGPU browser support and performance characteristics"
```

**Behavior:**
1. Call Perplexity research endpoint (sonar-deep-research model)
2. Strip `<think>` tags if present
3. Truncate response to max tokens
4. Return JSON with research findings, citations

**When to use:** Architecture decisions, technology comparisons, ecosystem surveys, best practices research.

**Cost:** $5/1k requests + token costs. Use sparingly for high-value research questions.

#### Not Included: Web Search

Basic web search uses Claude Code's built-in **WebSearch** tool, which:
- Is included free with Max subscription
- Works in subagents (no MCP bug)
- Is adequate for ecosystem discovery and trend research

**When to use WebSearch:** Finding what exists, community patterns, current trends, cross-referencing findings.

### Global Options

```bash
gsd-research --max-tokens 2000 docs nextjs "routing"  # Override default
gsd-research --no-cache deep "emerging technology"    # Skip cache
gsd-research --json-pretty docs react "hooks"         # Pretty-print JSON
gsd-research --version                                # Show version
```

### Output Format

All commands return JSON to stdout:

```json
{
  "success": true,
  "command": "docs",
  "query": "app router setup",
  "library": "nextjs",
  "results": [
    {
      "title": "App Router Getting Started",
      "content": "The App Router uses a file-system based router...",
      "source_url": "https://nextjs.org/docs/app/building-your-application/routing",
      "tokens": 450
    },
    {
      "title": "Defining Routes",
      "content": "Inside the app directory, folders define routes...",
      "source_url": "https://nextjs.org/docs/app/building-your-application/routing/defining-routes",
      "tokens": 380
    }
  ],
  "metadata": {
    "library_id": "/vercel/next.js",
    "total_available": 15,
    "returned": 3,
    "tokens_used": 830,
    "max_tokens": 2000,
    "cache_hit": false,
    "confidence": "HIGH",
    "backend": "context7"
  }
}
```

### Error Format

```json
{
  "success": false,
  "command": "docs",
  "error": {
    "code": "LIBRARY_NOT_FOUND",
    "message": "Could not resolve library 'nonexistent-lib'",
    "suggestions": ["react", "react-dom", "react-router"]
  }
}
```

### Caching Strategy

| Command | Cache TTL | Rationale |
|---------|-----------|-----------|
| `docs` | 24 hours | Library docs stable, Context7 already curated |
| `deep` | 6 hours | Research comprehensive but web sources change |

**Cache key:** `{command}:{query_hash}:{max_tokens}`

**Cache location:** `~/.cache/gsd-research/`

### Token Management

**Default max tokens:** 2000 per response

**Truncation strategy:**
1. Sort results by relevance (API already does this)
2. Include results until token budget exhausted
3. Set `metadata.total_available` to show more exists
4. Agent can re-query with higher `--max-tokens` if needed

**Token estimation:** `len(text.split()) * 1.3` (rough but fast)

## Updated Researcher Agent Design

### Changes to `agents/gsd-researcher.md`

**Before (tools line):**
```yaml
tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch, mcp__plugin_context7_context7__*
```

**After (tools line):**
```yaml
tools: Read, Write, Bash, Grep, Glob, WebSearch, WebFetch
```

**New `<tool_strategy>` section:**

```xml
<tool_strategy>

## Tool Selection Guide

| Need | Tool | Why |
|------|------|-----|
| Library API docs | `gsd-research docs` | Authoritative, version-aware, HIGH confidence |
| Ecosystem discovery | WebSearch | Free with Max, adequate for discovery |
| Deep synthesis | `gsd-research deep` | Exhaustive multi-source research |
| Specific URL content | WebFetch | Full page content |
| Project files | Read/Grep/Glob | Local codebase |

## gsd-research CLI

### Library Documentation (Context7)

```bash
gsd-research docs <library> "<query>"
```

Example:
```bash
gsd-research docs nextjs "app router file conventions"
gsd-research docs "react-three-fiber" "physics setup"
```

**When to use:** Library APIs, framework features, configuration options, version-specific behavior. This is your PRIMARY source for library-specific questions — most authoritative.

### Deep Research (Perplexity)

```bash
gsd-research deep "<query>"
```

Example:
```bash
gsd-research deep "authentication patterns for SaaS applications"
gsd-research deep "WebGPU browser support and production readiness 2026"
```

**When to use:** Architecture decisions, technology comparisons, comprehensive ecosystem surveys, best practices synthesis. Use for HIGH-VALUE research questions — this costs money.

**Cost awareness:** ~$0.005 per query + tokens. Budget for 5-10 deep queries per research session for important questions only.

## WebSearch (Built-in)

Use WebSearch for ecosystem discovery and trend research:

```
WebSearch("react state management libraries 2026")
WebSearch("nextjs vs remix comparison 2026")
```

**When to use:**
- Finding what exists when you don't know library names
- Current trends and community patterns
- Cross-referencing findings
- Any discovery where you need "what's out there"

**Always include current year** in queries for freshness.

**Why WebSearch over Perplexity search:** Free with Max subscription. Perplexity search costs $5/1k queries with marginal quality improvement for discovery tasks.

## Token Limit Strategy (for gsd-research)

**Default: 2000 tokens per response**

**Rationale:**
- The 50% rule: Research must complete before hitting 100k tokens
- At 2000 tokens/query, you can make ~50 queries
- Context7 returns results ranked by relevance — first 3-4 snippets are most important
- Query flexibility > per-query comprehensiveness

**When to increase (`--max-tokens 4000-6000`):**
- Comprehensive API documentation for a single feature
- Deep research on complex topics
- When `metadata.total_available` >> `metadata.returned` AND you need breadth

## Confidence Levels

| Source | Confidence | Use |
|--------|------------|-----|
| gsd-research docs | HIGH | State as fact |
| gsd-research deep | MEDIUM-HIGH | State with attribution |
| WebSearch verified | MEDIUM | State with source |
| WebSearch unverified | LOW | Flag for validation |

## Verification Protocol

```
1. Is confidence HIGH (from gsd-research docs)?
   YES → State as fact with source attribution
   NO → Continue

2. Can WebSearch or deep research verify?
   YES → Upgrade confidence one level
   NO → Mark as LOW, flag for validation

3. Do multiple sources agree?
   YES → Increase confidence
   NO → Note contradiction, investigate
```

</tool_strategy>
```

### Removed Sections

Remove references to MCP tools in:
- `<tool_strategy>` Context7 section (replaced above)
- Any examples showing `mcp__plugin_context7_context7__*` calls

### Updated Examples

**Before:**
```
1. Resolve library ID:
   mcp__plugin_context7_context7__resolve-library-id with libraryName: "[library name]"

2. Query documentation:
   mcp__plugin_context7_context7__query-docs with:
   - libraryId: [resolved ID]
   - query: "[specific question]"
```

**After:**
```
Query library documentation:
```bash
gsd-research docs "[library name]" "[specific question]"
```

The CLI handles library ID resolution automatically.
```

## Implementation Plan

### Phase 1: CLI Tool (`scripts/gsd-research/`)

**Deliverable:** Working CLI tool with `docs` and `deep` commands

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Initialize project structure with uv | `scripts/gsd-research/pyproject.toml` |
| 1.2 | Create CLI skeleton with typer | `scripts/gsd-research/gsd_research/cli.py` |
| 1.3 | Implement Context7 client | `scripts/gsd-research/gsd_research/backends/context7.py` |
| 1.4 | Implement Perplexity client | `scripts/gsd-research/gsd_research/backends/perplexity.py` |
| 1.5 | Implement caching layer | `scripts/gsd-research/gsd_research/cache.py` |
| 1.6 | Implement output formatting | `scripts/gsd-research/gsd_research/output.py` |
| 1.7 | Wire up `docs` command | `scripts/gsd-research/gsd_research/commands/docs.py` |
| 1.8 | Wire up `deep` command | `scripts/gsd-research/gsd_research/commands/deep.py` |
| 1.9 | Add error handling | All files |
| 1.10 | Test manually | - |

**Project structure:**
```
scripts/gsd-research/
├── pyproject.toml
├── README.md
└── gsd_research/
    ├── __init__.py
    ├── cli.py              # Main entry point
    ├── cache.py            # Caching layer
    ├── output.py           # JSON formatting
    ├── backends/
    │   ├── __init__.py
    │   ├── context7.py     # Context7 API client
    │   └── perplexity.py   # Perplexity API client
    └── commands/
        ├── __init__.py
        ├── docs.py         # docs command
        └── deep.py         # deep command
```

### Phase 2: Researcher Agent Update

**Deliverable:** Updated agent definition using CLI

| Task | Description | Files |
|------|-------------|-------|
| 2.1 | Update tools list (remove MCP) | `agents/gsd-researcher.md` |
| 2.2 | Replace tool_strategy section | `agents/gsd-researcher.md` |
| 2.3 | Update all examples | `agents/gsd-researcher.md` |
| 2.4 | Test with `/gsd:research-phase` | - |

### Phase 3: Integration & Documentation

**Deliverable:** Complete integration with GSD

| Task | Description | Files |
|------|-------------|-------|
| 3.1 | Add CLI to GSD install script | `scripts/install.sh` |
| 3.2 | Document environment variables | `README.md` or dedicated doc |
| 3.3 | Update research commands if needed | `commands/gsd/research-*.md` |
| 3.4 | End-to-end testing | - |

## API Requirements

### Environment Variables

```bash
# Required for docs command
export CONTEXT7_API_KEY="your-context7-api-key"

# Required for web and deep commands
export PERPLEXITY_API_KEY="your-perplexity-api-key"
```

**Get API keys:**
- Context7: https://context7.com/dashboard
- Perplexity: https://docs.perplexity.ai/

### API Endpoints Used

| API | Endpoint | Command |
|-----|----------|---------|
| Context7 | `GET /v2/libs/search` | `docs` (resolve library) |
| Context7 | `GET /v2/context` | `docs` (query docs) |
| Perplexity | Chat completions (sonar-deep-research) | `deep` |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limiting | Medium | Medium | Implement exponential backoff, aggressive caching |
| API key exposure | Low | High | Document secure handling, use env vars only |
| Context7 library not found | Medium | Low | Return suggestions, agent falls back to WebSearch |
| Perplexity deep response too large | Low | Medium | Aggressive truncation, strip `<think>` tags |
| Cache staleness | Low | Low | 24h TTL for docs, 6h for deep, `--no-cache` option |
| Perplexity cost overruns | Low | Low | Budget awareness in agent prompts, ~$0.005/query |

## Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Context7 access restored | `gsd-research docs nextjs "routing"` returns documentation |
| Deep research works | `gsd-research deep "auth patterns"` returns synthesis with citations |
| Researcher completes | `/gsd:research-phase 1` completes using hybrid tool strategy |
| Context efficiency | Typical research uses <60% context (vs current failures) |
| Response time | CLI calls complete in <10s (excluding cache miss) |
| Cache effectiveness | >50% cache hit rate in typical research session |
| Error clarity | All errors include actionable suggestions |

## Appendix: Full JSON Schema

### Success Response

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["success", "command", "query", "results", "metadata"],
  "properties": {
    "success": { "type": "boolean", "const": true },
    "command": { "type": "string", "enum": ["docs", "deep"] },
    "query": { "type": "string" },
    "library": { "type": "string", "description": "Only for docs command" },
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["title", "content", "tokens"],
        "properties": {
          "title": { "type": "string" },
          "content": { "type": "string" },
          "source_url": { "type": "string", "format": "uri" },
          "tokens": { "type": "integer" }
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": ["total_available", "returned", "tokens_used", "max_tokens", "cache_hit", "confidence", "backend"],
      "properties": {
        "library_id": { "type": "string" },
        "total_available": { "type": "integer" },
        "returned": { "type": "integer" },
        "tokens_used": { "type": "integer" },
        "max_tokens": { "type": "integer" },
        "cache_hit": { "type": "boolean" },
        "confidence": { "type": "string", "enum": ["HIGH", "MEDIUM", "LOW"] },
        "backend": { "type": "string", "enum": ["context7", "perplexity-deep-research"] }
      }
    }
  }
}
```

### Error Response

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["success", "command", "error"],
  "properties": {
    "success": { "type": "boolean", "const": false },
    "command": { "type": "string", "enum": ["docs", "deep"] },
    "error": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": { "type": "string" },
        "message": { "type": "string" },
        "suggestions": { "type": "array", "items": { "type": "string" } }
      }
    }
  }
}
```

---

**Proposal created:** 2026-01-21
**Updated:** 2026-01-21 (hybrid approach — removed `web` command, use built-in WebSearch instead)
**Status:** Ready for implementation
