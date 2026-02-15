# Reconciling External Work with Planning Artifacts

When phases are implemented outside the Mindsystem workflow (manual coding, pair programming, team contributions), planning artifacts become stale. This document captures the process for validating completed work and bringing artifacts back into sync.

---

## When This Applies

- Phases were implemented manually (not via `ms:execute-phase`)
- A team member committed work that maps to roadmap phases
- Returning to a project after a gap where work happened outside the system
- Migrating an existing project into Mindsystem mid-development

---

## Process Overview

```
1. Review commit history for the period
    ↓
2. Validate each phase against its success criteria
    ↓
3. Update ROADMAP.md (phase checkboxes + progress table)
    ↓
4. Update REQUIREMENTS.md (requirement checkboxes + traceability table)
    ↓
5. Update STATE.md (current position, progress, decisions, session continuity)
    ↓
6. Log gaps as tickets (deviations from spec that are acceptable but worth tracking)
```

---

## Step 1: Review Commit History

Identify which commits map to which phases. Filter by date range and keywords:

```bash
# Full history since last known phase completion
git log --oneline --format="%h %ad %s" --date=short --since="YYYY-MM-DD"

# Filter for phase-specific keywords
git log --oneline --format="%h %ad %s" --date=short -- lib/feature_folder/

# Check specific file history
git log --oneline --format="%h %ad %s" --date=short -- path/to/key_file.dart
```

Establish a timeline: when did work on each phase start and end? Look for merge commits or PR merges as completion markers.

---

## Step 2: Validate Against Success Criteria

For each phase, read the success criteria from ROADMAP.md and verify against the codebase.

**Use parallel exploration agents** to validate multiple phases concurrently. Each agent should:

1. Read the phase's success criteria from the roadmap
2. Search for the implementing files (screens, providers, models, widgets)
3. Verify each criterion is met by examining the actual code
4. Note any **deviations** — where implementation differs from spec but is functionally acceptable

### Categorizing Deviations

| Category | Action |
|----------|--------|
| **Spec met differently** (e.g., toast instead of modal) | Mark as complete, log gap for future polish |
| **Spec partially met** (e.g., missing client-side validation) | Mark as complete if core flow works, log gap |
| **Spec not met** (e.g., entire screen missing) | Do NOT mark complete, phase needs more work |

The key question: **can a user accomplish the core task described by the success criteria?** If yes, the phase is complete. Deviations are polish work, not blockers.

---

## Step 3: Update ROADMAP.md

### Phase Checkboxes

Change `- [ ]` to `- [x]` for completed phases:

```markdown
- [x] **Phase 14: Profile Customization** - Equip/unequip avatar frames and badges
- [x] **Phase 15: Reward Codes** - Promotional code claim flow
```

### Progress Table

Update the progress table with completion dates. Use `Manual` for the Plans column since these weren't executed through the system:

```markdown
| 14. Profile Customization | v0.8.0 | Manual | Complete | 2026-02-13 |
| 15. Reward Codes | v0.8.0 | Manual | Complete | 2026-02-14 |
```

### Plans Field

Update each phase's `**Plans**:` field:

```markdown
**Plans**: Implemented manually (outside mindsystem workflow)
```

---

## Step 4: Update REQUIREMENTS.md

### Requirement Checkboxes

Check off all requirements that are satisfied:

```markdown
- [x] **CUST-01**: User can view Customization tab showing avatar frames and badges
- [x] **CODE-01**: User can navigate to reward code claim screen
```

### Traceability Table

Update status from `Pending` to `Complete` for each satisfied requirement:

```markdown
| CUST-01 | Phase 14 | Complete |
| CODE-01 | Phase 15 | Complete |
```

### Last Updated

Update the footer timestamp with a summary of what changed:

```markdown
*Last updated: 2026-02-15 — Phase 14 (CUST-01..07) and Phase 15 (CODE-01..04) marked complete*
```

---

## Step 5: Update STATE.md

This is the most involved update. STATE.md must reflect the new current position.

### Fields to Update

| Field | What to change |
|-------|---------------|
| **Current focus** | Advance to next incomplete phase |
| **Phase** | Update phase number and name |
| **Plan** | "Phase N complete, ready for Phase N+1" |
| **Status** | Note phases were implemented manually |
| **Last Command** | "Manual validation \| YYYY-MM-DD" |
| **Last activity** | Describe what was validated |
| **Progress bar** | Recalculate percentage and visual bar |
| **Performance Metrics** | Add timeline for manually completed phases |
| **Decisions** | Add any architectural decisions discovered during validation |
| **Session Continuity** | Update last session, stopped at, next action |

### Decisions Section

When validating external work, you'll discover implementation decisions that weren't recorded. Add them:

```markdown
- Phase 14: Profile customization implemented as standalone screen (not tab in My Items)
- Phase 14: AppUserAvatar widget extended with frameUrl/badgeUrl for app-wide display
- Phase 15: Claim reward screen accessible from Account settings (pre-existing implementation)
```

### Session Continuity

Point to the next phase and what it needs:

```markdown
Last session: 2026-02-15
Stopped at: Phase 14 and 15 validated as complete
Resume file: .planning/ROADMAP.md
Next: Phase 16 (Ad Rewards) — needs research + planning
```

---

## Step 6: Log Gaps

Deviations from spec are not failures — they're polish work. Track them so they don't get lost:

1. Collect all deviations identified during validation
2. Create a single ticket capturing all gaps for the phase
3. Categorize by severity (navigation gap, UI gap, validation gap)
4. Assign appropriate priority (typically Normal or Low — these are refinements, not broken features)

---

## Phase Artifact Directories

Phases executed via `ms:execute-phase` produce artifact directories (PLAN.md, SUMMARY.md, VERIFICATION.md, etc.) under `.planning/phases/`. Manually implemented phases will NOT have these.

**Do not retroactively create phase artifact directories for manual work.** The absence of artifacts is itself a signal that the phase was done outside the system. The ROADMAP progress table's `Manual` marker captures this.

---

## Checklist

Before marking reconciliation complete:

- [ ] Commit history reviewed and mapped to phases
- [ ] Each phase validated against success criteria (with parallel agents if multiple phases)
- [ ] ROADMAP.md: phase checkboxes, progress table, plans fields updated
- [ ] REQUIREMENTS.md: requirement checkboxes, traceability table, timestamp updated
- [ ] STATE.md: current position, progress, metrics, decisions, continuity updated
- [ ] Deviations logged as tickets for future polish
- [ ] No phase marked complete that doesn't satisfy its core success criteria
