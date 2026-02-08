# Milestone Context Template

Template for `.planning/MILESTONE-CONTEXT.md` — captures brainstorming context from `/ms:new-milestone` for downstream consumption by roadmap and planning commands.

<template>

```markdown
# Milestone Context: v[X.Y] [Name]

**Generated:** [date]
**Source:** /ms:new-milestone brainstorming session

## Vision
[One paragraph — WHY this milestone, what problem it solves, what success looks like.
Written in user's words as much as possible.]

## Features

### [Feature 1 Name]
**What:** [Description]
**Why:** [Rationale — what prompted this]
**Scope:** [Simplest useful version vs full vision, if discussed]

### [Feature 2 Name]
...

## External Context
[References to specs, docs, analytics, backend documentation, business requirements
shared during discussion. Include relevant details/summaries, not just filenames.]

## Scope Boundaries
**Explicitly excluded:**
- [What's NOT part of this milestone and why]

## Priorities
[What matters most to least. Must-have vs nice-to-have.]

## Open Questions
[Things that need research or clarification before implementation.
Empty section if none — that's fine.]
```

</template>

<guidelines>

**Vision:**
- Captures the "why" in the user's own framing
- One paragraph, not a bullet list
- Should answer: "If this milestone succeeds, what changed?"

**Features:**
- Include rationale, not just names — downstream commands need the "why"
- Scope field captures any discussion of MVP vs complete version
- Each feature is a section header for easy scanning

**External Context:**
- Preserves information that would otherwise be lost after `/clear`
- Include relevant details and summaries, not just filenames
- If user shared specs, API docs, or analytics, capture the key points here

**Scope Boundaries:**
- Prevent scope creep during roadmap creation
- "Explicitly excluded" framing forces concrete decisions
- Include reasoning so future phases don't re-add

**Priorities:**
- Must-have vs nice-to-have distinction feeds into roadmap phase ordering
- If user didn't express priorities, derive from emphasis during conversation

**Open Questions:**
- Feed into `/ms:research-project` if research is needed
- Empty section is fine — not every milestone has unknowns
- Questions should be specific enough to research

</guidelines>
