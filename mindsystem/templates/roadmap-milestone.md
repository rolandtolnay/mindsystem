# Milestone-Grouped Roadmap Template

Template for reorganizing `ROADMAP.md` after first milestone ships. Collapse completed milestones, expand current/future work.

```markdown
# Roadmap: [Project Name]

## Milestones

- ✅ **MVP** - Phases 1-4 (shipped YYYY-MM-DD)
- 🚧 **[Name]** - Phases 5-6 (in progress)
- 📋 **[Name]** - Phases 7-10 (planned)

## Phases

<details>
<summary>✅ MVP (Phases 1-4) - SHIPPED YYYY-MM-DD</summary>

### Phase 1: [Name]
**Goal**: [What this phase delivers]
**Plans**: 3 plans

Plans:
- [x] 01-01: [Brief description]
- [x] 01-02: [Brief description]
- [x] 01-03: [Brief description]

[... remaining phases ...]

</details>

### 🚧 [Name] (In Progress)

**Milestone Goal:** [What this milestone delivers]

#### Phase 5: [Name]
**Goal**: [What this phase delivers]
**Depends on**: Phase 4
**Plans**: 2 plans

Plans:
- [ ] 05-01: [Brief description]
- [ ] 05-02: [Brief description]

[... remaining phases ...]

### 📋 [Name] (Planned)

**Milestone Goal:** [What this milestone delivers]

[... phases ...]

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | MVP | 3/3 | Complete | YYYY-MM-DD |
| 2. Features | MVP | 2/2 | Complete | YYYY-MM-DD |
| 5. Security | Security & Polish | 0/2 | Not started | - |
```

**Notes:**
- Milestone emoji: ✅ shipped, 🚧 in progress, 📋 planned
- Completed milestones collapsed in `<details>` for readability
- Current/future milestones expanded
- Continuous phase numbering (01-99)
- Progress table includes milestone column
