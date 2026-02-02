# Phase Context Template

Template for `.planning/phases/XX-name/{phase}-CONTEXT.md` - captures the user's vision for a phase.

**Purpose:** Document how the user imagines the phase working. This is vision context, not technical analysis. Technical details come from research.

---

## File Template

```markdown
# Phase [X]: [Name] - Context

**Gathered:** [date]
**Status:** [Ready for research / Ready for planning]

<vision>
## How This Should Work

[User's description of how they imagine this phase working. What happens when someone uses it? What does it look/feel like? This is the "pitch" version, not the technical spec.]

</vision>

<essential>
## What Must Be Nailed

[The core of this phase. If we only get one thing right, what is it? What's the non-negotiable that makes this phase successful?]

- [Essential thing 1]
- [Essential thing 2]
- [Essential thing 3 if applicable]

</essential>

<specifics>
## Specific Ideas

[Any particular things the user has in mind. References to existing products/features they like. Specific behaviors or interactions. "I want it to work like X" or "When you click Y, it should Z."]

[If none: "No specific requirements - open to standard approaches"]

</specifics>

<notes>
## Additional Context

[Anything else captured during the discussion that doesn't fit above. User's priorities, concerns mentioned, relevant background.]

[If none: "No additional notes"]

</notes>

<decisions>
## Decisions (Locked)

[Concrete implementation decisions made during discussion. These are NOT optional — plans must implement these exactly.]

- [Decision 1]
- [Decision 2]

### Claude's Discretion

[Areas where user explicitly said "you decide" or didn't express preference. Claude has freedom here.]

- [Area 1]
- [Area 2]

</decisions>

<deferred>
## Deferred Ideas

[Ideas mentioned during discussion but explicitly out of scope for this phase. Captured so they're not lost, but plans must NOT include these.]

[If none: "None — discussion stayed within phase scope"]

</deferred>

---

*Phase: XX-name*
*Context gathered: [date]*
```

<good_examples>
```markdown
# Phase 3: User Dashboard - Context

**Gathered:** 2025-01-20
**Status:** Ready for research

<vision>
## How This Should Work

When users log in, they land on a dashboard that shows them everything important at a glance. I imagine it feeling calm and organized - not overwhelming like Jira or cluttered like Notion.

The main thing is seeing their active projects and what needs attention. Think of it like a "what should I work on today" view. It should feel personal, not like enterprise software.

</vision>

<essential>
## What Must Be Nailed

- **At-a-glance clarity** - Within 2 seconds of landing, user knows what needs their attention
- **Personal feel** - This is YOUR dashboard, not a team dashboard. It should feel like opening your personal notebook.

</essential>

<specifics>
## Specific Ideas

- I like how Linear's home screen highlights what's assigned to you without noise
- Should show projects in a card format, not a list
- Maybe a "Today" section at the top with urgent stuff
- Dark mode is essential (already have this from Phase 2)

</specifics>

<notes>
## Additional Context

User mentioned they've abandoned several dashboards before because they felt too "corporate." The key differentiator is making it feel personal and calm.

Priority is clarity over features. Better to show less and make it obvious than show everything.

</notes>

<decisions>
## Decisions (Locked)

- Card layout for projects (not a list)
- "Today" section at top showing urgent items
- Dark mode support (already exists from Phase 2)

### Claude's Discretion

- Specific card dimensions and spacing
- How to determine what's "urgent"
- Animation/transition details

</decisions>

<deferred>
## Deferred Ideas

- Team dashboard view (user wants personal only for now)
- Customizable widgets (keep it simple first)

</deferred>

---

*Phase: 03-user-dashboard*
*Context gathered: 2025-01-20*
```
</good_examples>

<guidelines>
**This template serves dual purposes:**

1. **Vision sections** (`<vision>`, `<essential>`, `<specifics>`, `<notes>`) — for human understanding
2. **Decision sections** (`<decisions>`, `<deferred>`) — for downstream agent parsing

The user is the visionary. They know:
- How they imagine it working
- What it should feel like
- What's essential vs nice-to-have
- References to things they like

The user does NOT know (and shouldn't be asked):
- Codebase patterns (Claude reads the code)
- Technical risks (Claude identifies during research)
- Implementation constraints (Claude figures out)
- Success metrics (Claude infers from the work)

**Vision content should read like:**
- A founder describing their product vision
- "When you use this, it should feel like..."
- "The most important thing is..."
- "I don't want it to be like X, I want it to feel like Y"

**Decision content should be:**
- Concrete choices (not vague preferences)
- Checkable by downstream agents
- Clear about what's locked vs discretionary

**Content should NOT read like:**
- A technical specification
- Risk assessment matrix
- Success criteria checklist
- Codebase analysis

**After creation:**
- File lives in phase directory: `.planning/phases/XX-name/{phase}-CONTEXT.md`
- Research phase adds technical context (patterns, risks, constraints)
- Planning phase creates executable tasks informed by both vision AND research
- Plan checker verifies plans honor locked decisions and exclude deferred items
</guidelines>
