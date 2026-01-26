<purpose>
Start a new milestone cycle by updating PROJECT.md with new goals.

This is the brownfield equivalent of new-project. The project exists and has history.
This workflow gathers "what's next" and updates PROJECT.md, then routes to the
requirements → roadmap cycle.
</purpose>

<required_reading>
**Read these files NOW:**

1. ~/.claude/mindsystem/references/questioning.md
2. ~/.claude/mindsystem/templates/project.md
3. `.planning/PROJECT.md`
4. `.planning/MILESTONES.md` (if exists)
5. `.planning/STATE.md`
</required_reading>

<process>

<step name="load_context">
Load project context:

```bash
cat .planning/PROJECT.md
cat .planning/MILESTONES.md 2>/dev/null || echo "No milestones file yet"
cat .planning/STATE.md
cat .planning/config.json 2>/dev/null
```

Extract:
- What shipped previously (from MILESTONES.md)
- Current Validated requirements (from PROJECT.md)
- Pending todos and blockers (from STATE.md)

**Calculate next milestone version:**
- Parse last version from MILESTONES.md
- If v1.0 → suggest v1.1 (minor) or v2.0 (major)
- If v1.3 → suggest v1.4 or v2.0

**Calculate previous milestone for context:**
- If v1.1 starting → previous is v1.0
- Check for: `.planning/milestones/v{previous}-DECISIONS.md`
- Check for: `.planning/milestones/v{previous}-MILESTONE-AUDIT.md`
</step>

<step name="gather_goals">
Present what shipped:
```
Last milestone: v[X.Y] [Name]
Key accomplishments:
- [From MILESTONES.md]

Validated so far:
- [From PROJECT.md Validated section]

Pending todos:
- [From STATE.md if any]
```

**Decision gate:**

Use AskUserQuestion:
```
header: "New Milestone"
question: "How do you want to start v[X.Y]?"
options:
  - "I know what to build" — proceed to goal gathering
  - "Help me figure it out" — enter discovery mode with previous context
  - "Show previous decisions first" — view DECISIONS.md and AUDIT.md, then decide
```

**If "I know what to build":**
- Ask directly: "What do you want to build in the next milestone?"
- Wait for response
- Proceed to confirm_goals

**If "Show previous decisions first":**
- Load and present `.planning/milestones/v{previous}-DECISIONS.md` (if exists)
- Load and present `.planning/milestones/v{previous}-MILESTONE-AUDIT.md` assumptions section (if exists)
- Then present decision gate again (without this option)

**If "Help me figure it out" (Discovery Mode):**
- Load `.planning/milestones/v{previous}-DECISIONS.md` (if exists)
- Load `.planning/milestones/v{previous}-MILESTONE-AUDIT.md` (if exists)

Surface untested assumptions (from AUDIT.md):
```
📋 Untested from v[previous]:
- Error state displays (couldn't mock API errors)
- Empty state handling (couldn't clear test data)
- [etc. from assumptions section]

These were skipped during UAT. Address them in this milestone?
```

Run AskUserQuestion-based feature discovery:
```
header: "What to build"
question: "What do you want to add, improve, or fix?"
options:
  - "Address untested assumptions" — add test infrastructure or fix gaps
  - "New features" — build something new
  - "Improvements" — enhance existing features
  - "Bug fixes" — fix known issues
  - "Let me describe" — freeform input
```

Continue with follow-up questions:
- Probe specific features mentioned
- Ask about priorities
- Surface constraints or dependencies
- Clarify scope boundaries

Use @~/.claude/mindsystem/workflows/discuss-milestone.md patterns for questioning.

Continue until you have clear milestone goals.
</step>

<step name="confirm_goals">
Present gathered goals:

```
Milestone: v[X.Y] [Name]

Goal: [One sentence focus]

Target features:
- [Feature 1]
- [Feature 2]
- [Feature 3]

Ready to update PROJECT.md? (yes / adjust)
```

If "adjust": return to gather_goals.
</step>

<step name="update_project">
Update `.planning/PROJECT.md`:

**Add Current Milestone section** (after Core Value, before Requirements):

```markdown
## Current Milestone: v[X.Y] [Name]

**Goal:** [One sentence describing milestone focus]

**Target features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]
```

**Update Active requirements:**
- Add new milestone goals to Active section
- Keep existing Active items that weren't addressed
- Don't remove anything from Validated

**Update footer:**
```markdown
---
*Last updated: [date] after v[X.Y] milestone start*
```
</step>

<step name="update_state">
Update `.planning/STATE.md`:

```markdown
## Current Position

Phase: Not started (run /ms:create-roadmap)
Plan: —
Status: Defining requirements
Last activity: [today] — Milestone v[X.Y] started

Progress: ░░░░░░░░░░ 0%
```

Keep Accumulated Context (decisions, blockers) from previous milestone.
</step>


<step name="git_commit">
```bash
git add .planning/PROJECT.md .planning/STATE.md
git commit -m "$(cat <<'EOF'
docs: start milestone v[X.Y] [Name]

Goal: [One sentence]
Target features: [count] features
EOF
)"
```
</step>

<step name="offer_next">
```
Milestone v[X.Y] [Name] initialized.

PROJECT.md updated with:
- Current Milestone section
- Target features in Active requirements

---

## ▶ Next Up

**Define Requirements** — scope v[X.Y] features into REQUIREMENTS.md

`/ms:define-requirements`

<sub>`/clear` first → fresh context window</sub>

---

**Or research first:**
- `/ms:research-project` — investigate ecosystem before scoping

**Full flow:**
1. `/ms:define-requirements` — create REQUIREMENTS.md
2. `/ms:create-roadmap` — create ROADMAP.md with phases
3. `/ms:plan-phase [N]` — start execution

---
```
</step>

</process>

<success_criteria>
- PROJECT.md updated with Current Milestone section
- Active requirements reflect new milestone goals
- STATE.md reset for new milestone (keeps accumulated context)
- Git commit made
- User routed to define-requirements (or research-project)
</success_criteria>
