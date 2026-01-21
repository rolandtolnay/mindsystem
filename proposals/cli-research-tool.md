# Proposal: CLI-Based Research Tool for GSD

## Executive Summary

The gsd-researcher agent cannot use Context7 MCP tools due to a Claude Code bug preventing subagents from accessing MCP tools. Additionally, MCP tool definitions consume significant context window space, and Perplexity MCP returns outsized responses (15k+ tokens) that exhaust agent context before research completes.

This proposal introduces `gsd-research`, a Python CLI tool that wraps Context7 and Perplexity APIs with semantic commands (`docs`, `web`, `deep`). The CLI provides controlled output sizing, response caching, and consistent JSON output format. The gsd-researcher agent will invoke the CLI via Bash instead of MCP tools.

**Key benefits:**
- Unblocks researcher agent (works around MCP bug)
- Reduces context consumption by ~50% vs MCP (per beyond-mcp research)
- Enables response truncation and summarization
- Provides caching layer for repeated queries
- Establishes reusable pattern for future API integrations

## Problem Statement

### Current Issues

1. **MCP Bug:** Claude Code subagents cannot access MCP tools — gsd-researcher's Context7 calls fail silently
2. **Context Bloat:** MCP tool definitions consume context window just by existing
3. **Outsized Responses:** Perplexity MCP returns 15k+ tokens per research query, exhausting agent context
4. **No Control:** Cannot truncate, summarize, or cache MCP responses

### Impact

- `/gsd:research-phase` and `/gsd:research-project` commands effectively broken
- Research quality degrades as context fills with oversized API responses
- No workaround available within current architecture

## Proposed Solution

### High-Level Architecture

```
gsd-researcher agent
  ↓ (Bash tool)
gsd-research CLI (Python)
  ↓ (semantic routing)
├── docs → Context7 REST API
├── web → Perplexity Search API
└── deep → Perplexity Research API
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

Query library documentation via Context7.

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

#### `gsd-research web "<query>"`

Perform web search via Perplexity Search API.

```bash
# Example
gsd-research web "react state management best practices 2026"
gsd-research web "nextjs vs remix comparison"
```

**Behavior:**
1. Call Perplexity search endpoint
2. Truncate response to max tokens
3. Return JSON with search results, URLs, snippets

#### `gsd-research deep "<query>"`

Perform deep research via Perplexity Research API.

```bash
# Example
gsd-research deep "authentication patterns for SaaS applications"
gsd-research deep "WebGPU browser support and performance characteristics"
```

**Behavior:**
1. Call Perplexity research endpoint
2. Strip `<think>` tags if present
3. Truncate response to max tokens
4. Return JSON with research findings, citations

### Global Options

```bash
gsd-research --max-tokens 2000 docs nextjs "routing"  # Override default
gsd-research --no-cache web "breaking news topic"     # Skip cache
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
| `docs` | 6 hours | Library docs stable |
| `web` | 1 hour | Search results change |
| `deep` | 6 hours | Research comprehensive |

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

## gsd-research CLI: Primary Research Tool

The gsd-research CLI provides access to library documentation and web search with controlled output sizing.

**For library documentation (Context7):**
```bash
gsd-research docs <library> "<query>"
```

Example:
```bash
gsd-research docs nextjs "app router file conventions"
```

**For web search (Perplexity Search):**
```bash
gsd-research web "<query>"
```

Example:
```bash
gsd-research web "react state management best practices 2026"
```

**For deep research (Perplexity Research):**
```bash
gsd-research deep "<query>"
```

Example:
```bash
gsd-research deep "authentication patterns for SaaS applications"
```

**Best practices:**
1. Start with `docs` for library-specific questions — most authoritative
2. Use `web` for ecosystem discovery and current trends
3. Use `deep` for comprehensive research topics
4. Parse JSON output, check `metadata.returned` vs `metadata.total_available`
5. Trust `confidence` field: HIGH (use as fact), MEDIUM (verify), LOW (flag for validation)

## Token Limit Strategy

**Why 2000 tokens is the default:**
- The 50% rule: Research must complete before hitting 100k tokens (50% of 200k context)
- At 2000 tokens/query, you can make ~50 queries — enough for ecosystem survey + verification + implementation details
- Context7 returns results ranked by relevance — the first 3-4 snippets ARE the most important
- Query flexibility matters more than per-query comprehensiveness

**The tradeoff:** Every extra token per query is one fewer query you can make. More queries = more topics covered, more verification, more iteration.

**When to use default (2000 tokens):**
- Ecosystem discovery (many focused queries across different libraries)
- Verification queries (cross-referencing specific claims)
- Implementation patterns (looking up specific API usage)
- Any iterative research where you'll refine based on results

**When to proactively request more (`--max-tokens 4000-6000`):**
- Comprehensive API documentation for a single library feature
- Deep research on a complex topic (`deep` command)
- When `metadata.total_available` >> `metadata.returned` AND you need breadth
- Final "gather everything" query after focused exploration

**Escalation pattern:**
```bash
# Start focused (default 2000)
gsd-research docs nextjs "app router"

# If metadata shows 15 available but only 3 returned, AND you need more:
gsd-research --max-tokens 5000 docs nextjs "app router complete guide"
```

**Budget awareness:** Track approximate token usage. If you've made 30+ queries, stay with defaults. If you've made <10, you have room for 1-2 comprehensive queries.

**When NOT to use gsd-research:**
- Reading project files → Use Read tool
- Searching codebase → Use Grep/Glob tools
- General web pages → Use WebFetch tool (for specific URLs)

## WebSearch: Fallback Discovery

Use WebSearch for:
- Finding what exists when you don't know library names
- Cross-referencing gsd-research findings
- Discovering community patterns and discussions

**Always include current year** in WebSearch queries for freshness.

## Verification Protocol

```
For each finding from gsd-research:

1. Is confidence HIGH?
   YES → State as fact with source attribution
   NO → Continue to step 2

2. Can WebSearch verify?
   YES → Upgrade to MEDIUM confidence
   NO → Mark as LOW confidence, flag for validation

3. Do multiple sources agree?
   YES → Increase confidence one level
   NO → Note contradiction, investigate further
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

**Deliverable:** Working CLI tool with all three commands

| Task | Description | Files |
|------|-------------|-------|
| 1.1 | Initialize project structure with uv | `scripts/gsd-research/pyproject.toml` |
| 1.2 | Create CLI skeleton with typer | `scripts/gsd-research/gsd_research/cli.py` |
| 1.3 | Implement Context7 client | `scripts/gsd-research/gsd_research/backends/context7.py` |
| 1.4 | Implement Perplexity client | `scripts/gsd-research/gsd_research/backends/perplexity.py` |
| 1.5 | Implement caching layer | `scripts/gsd-research/gsd_research/cache.py` |
| 1.6 | Implement output formatting | `scripts/gsd-research/gsd_research/output.py` |
| 1.7 | Wire up `docs` command | `scripts/gsd-research/gsd_research/commands/docs.py` |
| 1.8 | Wire up `web` command | `scripts/gsd-research/gsd_research/commands/web.py` |
| 1.9 | Wire up `deep` command | `scripts/gsd-research/gsd_research/commands/deep.py` |
| 1.10 | Add error handling | All files |
| 1.11 | Test manually | - |

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
        ├── web.py          # web command
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
| Perplexity | Chat completions (sonar) | `web` |
| Perplexity | Chat completions (sonar-pro) | `deep` |

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| API rate limiting | Medium | Medium | Implement exponential backoff, aggressive caching |
| API key exposure | Low | High | Document secure handling, use env vars only |
| Context7 library not found | Medium | Low | Return suggestions, fallback to WebSearch |
| Perplexity response still too large | Low | Medium | Aggressive truncation, configurable max-tokens |
| Cache staleness | Low | Low | Reasonable TTLs, `--no-cache` option |

## Success Criteria

| Criterion | Measurement |
|-----------|-------------|
| Researcher works | `/gsd:research-phase 1` completes without MCP errors |
| Context reduction | Typical research uses <50% context (vs current >80%) |
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
    "command": { "type": "string", "enum": ["docs", "web", "deep"] },
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
        "backend": { "type": "string", "enum": ["context7", "perplexity-search", "perplexity-research"] }
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
    "command": { "type": "string", "enum": ["docs", "web", "deep"] },
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
**Status:** Ready for implementation
