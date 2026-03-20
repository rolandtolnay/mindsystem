# Phase Specification Derivation

Shared algorithm for deriving goal, success criteria, requirements, and pre-work flags from a user's phase description. Used by `add-phase` and `insert-phase`.

## Variables

Set by calling command before loading this reference:

- `{PHASE_ID}` — phase number (integer like `7` or decimal like `06.1`)
- `{PHASE_MARKER}` — empty for add-phase, `(INSERTED)` for insert-phase

## Input Assessment

Read `.planning/PROJECT.md` for vision and domain context (target audience, project scope).

Proceed directly when the user's description provides enough context to derive a confident specification — clear domain, identifiable user outcomes, enough scope to define 2-5 success criteria.

When scope is ambiguous or domain is unclear, ask targeted clarifying questions before deriving. Keep asking until confident.

Use AskUserQuestion with concrete options derived from PROJECT.md/ROADMAP.md context:
- header: "Phase Clarification"
- question: specific ambiguity identified
- options: 2-4 concrete interpretations plus "Something else"

Examples of when to ask:
- "Add notifications" → notifications for what? (new content, billing events, system alerts, all of these?)
- "Fix performance" → which user-facing flow? (page load, search, data export?)
- "Add settings" → which settings? (account, preferences, integrations?)

Examples of when to proceed directly:
- "Add dark mode toggle to settings page" → clear scope, clear UI, clear outcome
- "Add Stripe subscription billing with plan selection" → clear domain, clear integration

## Derivation Algorithm

### 1. Goal Statement

Transform the description into an outcome-focused goal:

- Good: "Users can manage subscription billing without edge-case failures"
- Good: "Content creators can schedule posts for future publication"
- Good: "Administrators can monitor system health through a real-time dashboard"
- Bad: "Fix subscription billing" (task, not outcome)
- Bad: "Add scheduling feature" (feature label, not user outcome)
- Bad: "Implement admin dashboard" (implementation task, not user value)

Use existing phase goals from ROADMAP.md as style reference.

### 2. Success Criteria (2-5)

Ask: "What must be TRUE for users when this phase completes?"

- Each criterion must be verifiable by a human using the application
- Observable user behaviors, not implementation tasks
- Good: "User sees correct prorated amount when changing plans mid-cycle"
- Good: "User receives email confirmation within 30 seconds of signup"
- Good: "Dark mode persists across browser sessions"
- Bad: "Billing calculation is fixed"
- Bad: "Email service is integrated"
- Bad: "CSS variables are used for theming"

### 3. Requirements with REQ-IDs

Create atomic, checkable requirements:

- Follow existing category patterns from REQUIREMENTS.md (e.g., if AUTH-01..AUTH-04 exist, continue with AUTH-05)
- If the work fits an existing category, reuse that prefix and continue numbering
- If the work introduces a new domain, create a new category prefix
- User-centric: "User can X" not "System does Y"
- Each requirement maps to Phase {PHASE_ID}

The calling command has already extracted existing REQ-ID categories and highest numbers from REQUIREMENTS.md — use that context.

### 4. Pre-work Flags

Analyze the description to determine:

**Discuss**: Default Likely — enumerate 2-4 assumptions or open questions specific
to the phase. Unlikely only for fully mechanical zero-decision work (version bump,
rename-only refactor, config-only change, pure deletion/cleanup).

**Design**: Likely when description involves UI work, visual elements, forms,
dashboards, or multi-screen flows. Unlikely for backend-only, API, infrastructure,
or established UI patterns.

**Research**: Likely when description mentions external APIs/services, new
libraries/frameworks, or unclear technical approach. Unlikely for established
internal patterns or well-documented conventions.

Use binary Likely/Unlikely with parenthetical reason. Include topics/focus only when Likely.

## Presentation & Approval

Present the full specification:

```
## Phase {PHASE_ID}: {Name} {PHASE_MARKER}

**Goal:** {proposed goal}

**Success Criteria:**
1. {criterion}
2. {criterion}
3. {criterion}

**New Requirements:**
- [ ] **{CAT}-{NN}**: {description}
- [ ] **{CAT}-{NN}**: {description}

**Pre-work:** Discuss {L/U} | Design {L/U} | Research {L/U}
```

Use AskUserQuestion:
- header: "Phase Specification"
- question: "Does this capture what Phase {PHASE_ID} should deliver?"
- options:
  - "Approve" — Proceed with this specification
  - "Adjust" — I want to refine the goal, criteria, or requirements
  - "Add context" — I need to provide more detail first

If "Adjust": Ask what to change, revise, re-present.
If "Add context": Get additional detail, re-derive, re-present.
Loop until approved.

## Requirements Update

Update REQUIREMENTS.md with the approved requirements:

1. Append new requirements under the appropriate category section in `## v1 Requirements`:
   - If category exists: add new requirements after the last requirement in that category
   - If new category: add new category section after last existing category

2. Update `## Traceability` table — append rows for each new requirement:
   ```
   | {REQ-ID} | Phase {PHASE_ID} | Pending |
   ```

3. Update coverage counts:
   ```
   - v1 requirements: {X + new count} total
   - Mapped to phases: {Y + new count}
   ```

4. Update `*Last updated:*` footer:
   ```
   *Last updated: {date} after Phase {PHASE_ID} addition*
   ```
