# Learnings Template

Template for `.planning/LEARNINGS.md` — curated cross-milestone index of reusable patterns.

**Purpose:** Persist operational learnings across milestone boundaries. When starting a new milestone, LEARNINGS.md surfaces past patterns that prevent repeated mistakes and reinforce proven approaches.

**Created by:** `complete-milestone` workflow during `/ms:complete-milestone`

**Referenced by:** `/ms:plan-phase` step 6e — grep-matched entries injected as `<learning type="curated">` in plan-writer handoff

---

**Distinct from:**

| File | Contains | Learnings does NOT contain |
|------|----------|---------------------------|
| `PROJECT.md` Key Decisions | Strategic choices with rationale | Decisions (use Key Decisions table) |
| `v{X.Y}-DECISIONS.md` | Milestone-scoped decision archive | Decision rationale or alternatives |
| `STATE.md` | Session restoration context | Status, blockers, current position |
| `SUMMARY.md` | Phase deliverables and outcomes | What was built or delivered |

**LEARNINGS.md contains:** Prescriptive one-liner patterns extracted from debug resolutions, adhoc discoveries, phase deviations, and recurring issues. Each entry is actionable ("always do X", "never do Y", "when Z, use W").

---

<template>

```markdown
# Project Learnings

Curated patterns from milestone work. Referenced by `/ms:plan-phase` for context-aware planning.

---

## v{{VERSION}} {{MILESTONE_NAME}}

### {{SUBSYSTEM}}

- **{{Brief title}}**: {{Prescriptive action}} → `{{source_ref}}`

---

*Last updated: {{DATE}} during v{{VERSION}} milestone completion*
```

</template>

<guidelines>

## What Belongs

Reusable patterns that prevent future mistakes or reinforce proven approaches:

- Root cause patterns from debug sessions
- Prevention rules discovered through investigation
- Non-obvious integration behaviors
- Performance or reliability patterns
- Workarounds for framework/library quirks

## What Does NOT Belong

| Category | Why excluded | Where it goes |
|----------|-------------|---------------|
| Decisions | Strategic choices with rationale | PROJECT.md Key Decisions, v{X.Y}-DECISIONS.md |
| Deliverables | What was built | SUMMARY.md |
| Status | Current project state | STATE.md |
| Trivial fixes | Typos, missing imports, obvious errors | Nowhere (not worth persisting) |
| One-time issues | Environment-specific, won't recur | Debug doc only |

## Extraction Sources

| Source | Path pattern | What to extract |
|--------|-------------|-----------------|
| Debug resolutions | `.planning/debug/resolved/*.md` | `root_cause` + `resolution` + `prevention` from frontmatter |
| Adhoc summaries | `.planning/adhoc/*-SUMMARY.md` | `learnings` array entries from frontmatter |
| Phase summaries | `.planning/phases/*/SUMMARY.md` | Deviations/Issues sections, patterns-established |
| Completed todos | `.planning/todos/done/*.md` | Reusable patterns only (lower priority) |

## Curation Rules

- **4-8 entries per milestone** — ruthlessly curate, not exhaustive
- **Group by subsystem** from `.planning/config.json` vocabulary
- **Deduplicate** — if two sources surface the same pattern, keep the more prescriptive version
- **Prefer prevention framing** — "Always validate X before Y" over "We found a bug in X"
- **Skip trivial fixes** — missing imports, typos, obvious config errors add no value
- **One line per entry** — if it needs a paragraph, it belongs in a debug doc or decision

## Entry Format

```
- **{Brief title}**: {Prescriptive action} → `{source_ref}`
```

- **Brief title**: 2-5 words identifying the pattern
- **Prescriptive action**: Imperative sentence — what to do or avoid
- **source_ref**: Path to the source artifact for full context

## Lifecycle

- **Append-only** — new milestone sections prepend (reverse chronological)
- **Not in STATE.md** — LEARNINGS.md is separate from session restoration
- **Survives milestone boundaries** — unlike ROADMAP.md and REQUIREMENTS.md, never deleted
- **Curated, not automated** — human-quality judgment applied during extraction

</guidelines>

<example>

```markdown
# Project Learnings

Curated patterns from milestone work. Referenced by `/ms:plan-phase` for context-aware planning.

---

## v1.1 Security

### auth

- **Token refresh race condition**: Queue concurrent requests during 401 interceptor refresh — don't fire parallel refresh calls → `.planning/debug/resolved/auth-token-race.md`
- **JWT expiry buffer**: Set token refresh threshold to 30s before expiry, not on-expiry — avoids edge-case 401s on slow connections → `.planning/adhoc/2026-01-20-fix-auth-token-SUMMARY.md`

### api

- **Rate limit headers**: Always read X-RateLimit-Remaining before retry logic — blind retries trigger API bans → `.planning/debug/resolved/api-rate-limit-ban.md`

### database

- **Migration rollback**: Test down-migrations before deploying up-migrations — broken rollbacks cause extended outages → `.planning/phases/06-hardening/06-02-SUMMARY.md`

---

## v1.0 MVP

### ui

- **Form state on navigation**: Reset form state on route change — stale form data causes phantom validation errors → `.planning/debug/resolved/form-stale-state.md`
- **Optimistic updates**: Always implement rollback UI for optimistic mutations — silent failures erode user trust → `.planning/phases/03-core/03-01-SUMMARY.md`

### data-layer

- **N+1 in list views**: Use dataloader pattern for any list endpoint hitting related records — N+1 queries surface at ~50 records → `.planning/debug/resolved/dashboard-slow-load.md`
- **Cache invalidation scope**: Invalidate by entity type + ID, not by endpoint — endpoint-scoped invalidation misses cross-view staleness → `.planning/phases/04-polish/04-01-SUMMARY.md`

---

*Last updated: 2026-02-01 during v1.1 milestone completion*
```

</example>
