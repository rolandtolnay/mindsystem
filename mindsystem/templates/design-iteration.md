# Design Iteration Template

Template for structured feedback when refining a design. Use this for major redesigns or when multiple aspects need adjustment.

**When to use:**
- User requests significant changes to DESIGN.md
- Multiple feedback points need to be captured
- Context from previous iteration should be preserved

**When NOT to use:**
- Single small tweak (edit DESIGN.md directly)
- Typo or value correction (edit DESIGN.md directly)

---

## Iteration Prompt Structure

When spawning gsd-designer for a redesign, assemble this context:

```markdown
<iteration_context>
Product: [From PROJECT.md - What This Is]
Phase: [N]: [Phase name]
Iteration: v[N] (previous: v[N-1])
</iteration_context>

<previous_design>
[Include key sections from current DESIGN.md that are relevant to the changes]

Visual Identity:
[Current visual identity section]

Relevant screens/components:
[Sections being modified]
</previous_design>

<feedback_on_previous>
## What Worked Well (KEEP)

[List aspects that should be preserved - be specific]
- [Aspect 1]: [Why it works]
- [Aspect 2]: [Why it works]

## What Needs Improvement (FIX)

[List specific issues with actionable direction]
- [Issue 1]: [What's wrong] → [How to fix]
- [Issue 2]: [What's wrong] → [How to fix]

## New Requirements (ADD)

[List any new elements not in previous design]
- [New requirement 1]: [What and why]
- [New requirement 2]: [What and why]

If none: "No new requirements - this is refinement only."
</feedback_on_previous>

<specific_focus>
## Primary Focus for This Iteration

[The single most important thing that must improve]

This is the ONE thing that determines if this iteration succeeds.
</specific_focus>

<constraints>
## Constraints

- Preserve: [Aspects that must NOT change]
- Budget: [Any limitations on scope]
- Timeline: [If relevant]
</constraints>
```

---

## Example Usage

### Example 1: Color Refinement

```markdown
<iteration_context>
Product: Analytics Dashboard
Phase: 3: User Dashboard
Iteration: v2 (previous: v1)
</iteration_context>

<previous_design>
Visual Identity:
Professional analytics dashboard with dark mode. Deep navy background (#0a0f1a) with amber accent (#F59E0B).

Design System Colors:
- Primary: #0a0f1a
- Secondary: #1a1f2e
- Text: #ffffff
- Accent: #F59E0B
</previous_design>

<feedback_on_previous>
## What Worked Well (KEEP)

- Deep navy background (#0a0f1a): Distinctive, not generic black
- Overall layout structure: Information hierarchy is clear
- Component spacing (16px gaps): Feels intentional

## What Needs Improvement (FIX)

- Amber accent (#F59E0B): Too warm, clashes with navy → Try cooler accent (teal or cyan)
- Card backgrounds (#1a1f2e): Not enough contrast with primary → Increase lightness
- Text secondary (#8b95a8): Too muted, hard to read → Brighten to #a0aec0

## New Requirements (ADD)

No new requirements - this is refinement only.
</feedback_on_previous>

<specific_focus>
## Primary Focus for This Iteration

Fix the accent color. The amber feels disconnected from the cool navy palette. Find an accent that energizes without clashing.
</specific_focus>

<constraints>
## Constraints

- Preserve: Deep navy primary, overall layout structure
- Budget: Color changes only, no layout modifications
</constraints>
```

### Example 2: Layout Restructure

```markdown
<iteration_context>
Product: Task Management App
Phase: 5: Kanban Board
Iteration: v3 (previous: v2)
</iteration_context>

<previous_design>
Screen Layout (Kanban Board):
+------------------------------------------+
| [Header]                                 |
+------------------------------------------+
| [Col 1] | [Col 2] | [Col 3] | [Col 4]   |
| Card    | Card    | Card    | Card      |
| Card    | Card    |         |           |
+------------------------------------------+
</previous_design>

<feedback_on_previous>
## What Worked Well (KEEP)

- Card design: Clean, readable, good use of labels
- Column headers: Clear status indication
- Drag handles: Obvious affordance

## What Needs Improvement (FIX)

- Fixed 4-column layout: Doesn't scale on smaller screens → Make columns scrollable horizontally
- No column collapse: Too much visual noise → Add ability to collapse columns
- Cards too tall: Take too much vertical space → Compact mode option

## New Requirements (ADD)

- Swimlanes: Group cards by assignee (horizontal rows within columns)
- Quick add: Inline card creation without modal
</feedback_on_previous>

<specific_focus>
## Primary Focus for This Iteration

Make the board work on tablet (768px). Current fixed 4-column breaks completely.
</specific_focus>

<constraints>
## Constraints

- Preserve: Card visual design, drag-drop interaction
- Budget: Layout changes, no new visual styling
</constraints>
```

---

## Guidelines

**Feedback should be:**
- **Specific:** "Amber accent clashes" not "colors are wrong"
- **Actionable:** Include direction, not just criticism
- **Prioritized:** Primary focus identifies the ONE thing

**Preserve section is critical:**
- Explicitly list what must NOT change
- Prevents accidental regression of working aspects
- Designer knows boundaries

**Primary focus drives success:**
- If this ONE thing improves, iteration succeeds
- Keeps designer from getting lost in details
- Enables focused refinement

**After iteration:**
- Compare v[N] to v[N-1] against feedback
- Verify "what worked well" was preserved
- Verify "what needs improvement" was addressed
- Update design version in DESIGN.md frontmatter
