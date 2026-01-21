# Requirements: GSD Improvements

**Defined:** 2026-01-21
**Core Value:** Research commands must work reliably with controlled context consumption.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Research CLI

- [ ] **CLI-01**: User can query library documentation via `gsd-research docs <library> <query>`
- [ ] **CLI-02**: User can perform web search via `gsd-research web <query>`
- [ ] **CLI-03**: User can perform deep research via `gsd-research deep <query>`
- [ ] **CLI-04**: Responses are cached to reduce redundant API calls

### Agent Updates

- [ ] **AGENT-01**: gsd-researcher agent uses gsd-research CLI instead of MCP tools
- [ ] **AGENT-02**: Research queries enforce 2000 token default with override option
- [ ] **AGENT-03**: Agent handles research failures gracefully with fallback behavior
- [ ] **AGENT-04**: Code simplifier agent available for manual invocation post-execution

### Codebase Maintenance

- [ ] **MAINT-01**: Worktree script creates/manages live branch for comparison
- [ ] **MAINT-02**: Diff analysis documents changes between vanilla and live branches

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Code Simplifier

- **SIMP-01**: Auto-run code simplifier post-execute (integrated into execute-phase)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Cherry-pick from live branch | Proposals drafted from analysis, not direct cherry-pick |
| Verify-work rework | Deferred to future milestone |
| Centralized "Next Up" computation | Substantial undertaking, future milestone |
| TODO-s vs Insert phase consolidation | Evaluate after this work |
| Phase padding reliability fix | Quick fix, can do opportunistically |

## Traceability

Which phases cover which requirements. Updated by create-roadmap.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CLI-01 | — | Pending |
| CLI-02 | — | Pending |
| CLI-03 | — | Pending |
| CLI-04 | — | Pending |
| AGENT-01 | — | Pending |
| AGENT-02 | — | Pending |
| AGENT-03 | — | Pending |
| AGENT-04 | — | Pending |
| MAINT-01 | — | Pending |
| MAINT-02 | — | Pending |

**Coverage:**
- v1 requirements: 10 total
- Mapped to phases: 0
- Unmapped: 10 ⚠️

---
*Requirements defined: 2026-01-21*
*Last updated: 2026-01-21 after initial definition*
