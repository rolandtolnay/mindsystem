# Adhoc Summary Template

Template for `.planning/adhoc/{timestamp}-{slug}-SUMMARY.md` — documentation for small work items executed via `/ms:do-work`.

---

## File Template

```markdown
---
type: adhoc
description: [user's original description]
completed: [ISO timestamp]
duration: [X min]
related_phase: [current phase from STATE.md, or "none"]
subsystem: [from .planning/config.json subsystems list]
tags: [searchable keywords]
files_modified:
  - [path/to/file1.ts]
  - [path/to/file2.ts]
commit: [git hash]
patch_file: [path to .patch file, or empty if skipped]
learnings:
  - [optional: key insight from this work]
---

# Adhoc: [Description]

**[Substantive one-liner describing what was done]**

## What Was Done

- [Most important outcome]
- [Second accomplishment if applicable]

## Files Modified

- `[path/to/file.ts]`: [what changed]
- `[path/to/other.ts]`: [what changed]

## Verification

- [what was verified]: [result]
```

<purpose>

Adhoc summaries document small work items executed outside the normal phase workflow.

**Differences from phase SUMMARY.md:**
- Simplified frontmatter (no waves, depends_on, requires, provides, affects)
- No dependency graph (adhoc work is isolated by design)
- No "Next Phase Readiness" (not part of phase sequence)
- No deviations section (adhoc work is already unplanned)

**Purpose:**
- Audit trail for quick fixes
- Context for future sessions (what was done between phases)
- Git commit documentation

</purpose>

<frontmatter_fields>

| Field | Required | Description |
|-------|----------|-------------|
| type | Yes | Always "adhoc" |
| description | Yes | User's original work description |
| completed | Yes | ISO timestamp when work completed |
| duration | Yes | Time spent (e.g., "12 min") |
| related_phase | Yes | Current phase from STATE.md, or "none" if between phases |
| subsystem | Yes | From .planning/config.json subsystems list |
| tags | No | Searchable keywords from work context |
| files_modified | Yes | List of file paths changed |
| commit | Yes | Git commit hash |
| patch_file | No | Path to generated patch file (empty if no code changes) |
| learnings | No | Key insights from this work (only for non-obvious discoveries) |

</frontmatter_fields>

<one_liner_rules>

The one-liner MUST be substantive:

**Good:**
- "Added null check to prevent crash on empty user array"
- "Fixed auth token refresh by handling 401 in interceptor"
- "Added missing index on user_id for query performance"

**Bad:**
- "Fixed the bug"
- "Made it work"
- "Quick fix"

The one-liner should tell someone what actually changed.

</one_liner_rules>

<example>

```markdown
---
type: adhoc
description: Fix auth token not refreshing on 401
completed: 2026-01-20T14:32:00Z
duration: 8 min
related_phase: 03-user-dashboard
subsystem: auth
tags: [jwt, interceptor, token-refresh]
files_modified:
  - src/lib/api-client.ts
  - src/hooks/useAuth.ts
commit: abc123f
patch_file: .planning/adhoc/2026-01-20-fix-auth-token-not-refreshing-on-401.patch
learnings:
  - "401 interceptors must queue concurrent requests during token refresh to avoid race conditions"
---

# Adhoc: Fix auth token not refreshing on 401

**Added 401 response interceptor to trigger token refresh before retrying failed request**

## What Was Done

- Added response interceptor in api-client.ts to catch 401 errors
- Integrated with useAuth hook to call refresh token endpoint
- Added retry logic for original request after successful refresh

## Files Modified

- `src/lib/api-client.ts`: Added response interceptor with 401 handling
- `src/hooks/useAuth.ts`: Exposed refreshToken function for interceptor use

## Verification

- Manually tested: Token expires → 401 → refresh triggered → request succeeds
- No console errors during token refresh flow
```

</example>

<guidelines>

**When to create:**
- After completing adhoc work via `/ms:do-work`
- Required output from do-work workflow

**Size:**
- Keep brief — adhoc work is small by definition
- 1-2 accomplishments typical
- 1-3 files typical

**Commit reference:**
- Always include commit hash in frontmatter
- Hash links summary to actual code changes
- Enables `git show [hash]` for full diff

**Related phase:**
- If during phase execution: use current phase (e.g., "03-user-dashboard")
- If between phases: use "none"
- Helps contextualize when this work happened

**After creation:**
- STATE.md updated with entry in "Recent Adhoc Work"
- File remains in `.planning/adhoc/` for audit trail

</guidelines>
