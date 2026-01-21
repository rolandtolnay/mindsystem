# Roadmap: GSD Improvements

## Overview

This roadmap delivers reliable research functionality for GSD by replacing broken MCP tools with a CLI-based approach. First we build the `gsd-research` CLI tool, then update the researcher agent to use it, and finally add supporting infrastructure (code simplifier agent, branch comparison tooling). Three phases, each delivering independent value.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Research CLI** - Build gsd-research CLI tool with docs/web/deep commands
- [ ] **Phase 2: Agent Integration** - Update gsd-researcher agent to use CLI instead of MCP
- [ ] **Phase 3: Supporting Infrastructure** - Code simplifier agent and branch comparison tooling

## Phase Details

### Phase 1: Research CLI
**Goal**: User can perform library, web, and deep research queries via command line
**Depends on**: Nothing (first phase)
**Requirements**: CLI-01, CLI-02, CLI-03, CLI-04
**Success Criteria** (what must be TRUE):
  1. User can run `gsd-research docs typer "argument parsing"` and get relevant documentation
  2. User can run `gsd-research web "claude code mcp tools"` and get search results
  3. User can run `gsd-research deep "best practices for CLI caching"` and get comprehensive analysis
  4. Running the same query twice returns cached results (faster, no API call)
  5. All responses respect 2000 token default limit (overridable via flag)
**Research**: Likely (Context7 and Perplexity API patterns)
**Research topics**: Context7 API authentication and query format, Perplexity API request/response structure
**Plans**: TBD

Plans:
- [ ] 01-01: Project setup and CLI scaffolding
- [ ] 01-02: Context7 integration (docs command)
- [ ] 01-03: Perplexity integration (web/deep commands) and caching

### Phase 2: Agent Integration
**Goal**: gsd-researcher agent uses CLI tool reliably with controlled context consumption
**Depends on**: Phase 1
**Requirements**: AGENT-01, AGENT-02, AGENT-03
**Success Criteria** (what must be TRUE):
  1. gsd-researcher agent successfully calls gsd-research CLI (no MCP references remain)
  2. Research queries from agent default to 2000 tokens (subagent context protection)
  3. When CLI fails, agent gracefully degrades (logs issue, continues without crashing)
  4. Agent can request larger context when explicitly needed via override flag
**Research**: Unlikely (internal agent patterns)
**Plans**: TBD

Plans:
- [ ] 02-01: Update gsd-researcher agent to use CLI
- [ ] 02-02: Error handling and graceful degradation

### Phase 3: Supporting Infrastructure
**Goal**: Code simplifier agent available and branch comparison tooling functional
**Depends on**: Nothing (can run parallel to Phase 2, but sequenced for simplicity)
**Requirements**: AGENT-04, MAINT-01, MAINT-02
**Success Criteria** (what must be TRUE):
  1. User can invoke code simplifier agent manually after execution
  2. Worktree script creates and manages live branch comparison environment
  3. Diff analysis between vanilla and live branches is documented
**Research**: Unlikely (established git patterns, internal agent structure)
**Plans**: TBD

Plans:
- [ ] 03-01: Code simplifier agent
- [ ] 03-02: Worktree script and branch comparison

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Research CLI | 0/3 | Not started | - |
| 2. Agent Integration | 0/2 | Not started | - |
| 3. Supporting Infrastructure | 0/2 | Not started | - |
