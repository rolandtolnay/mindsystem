<purpose>
Help the user figure out what they want to build in the next milestone through collaborative thinking.

You're a thinking partner helping them crystallize their vision for what's next. Features first — everything else (scope, phases) derives from what they want to build.
</purpose>

<process>

<step name="check_state" priority="first">
Load project state:

```bash
cat .planning/STATE.md
cat .planning/ROADMAP.md
```

**If no active milestone (expected state after completing previous):**
Continue to milestone_context.

**If active milestone exists:**

```
Current milestone in progress: v[X.Y] [Name]
Phases [N]-[M], [P]% complete

Did you want to:
1. Complete current milestone first (/gsd:complete-milestone)
2. Add phases to current milestone (/gsd:add-phase)
3. Continue anyway - discuss next milestone scope

```

Wait for user response. If "Continue anyway", proceed to milestone_context.
</step>

<step name="milestone_context">
Present context from previous milestone:

```
Last completed: v[X.Y] [Name] (shipped [DATE])
Key accomplishments:
- [From MILESTONES.md or STATE.md]

Total phases delivered: [N]
Next phase number: [N+1]
```

Continue to intake_gate.
</step>

<step name="intake_gate">
**CRITICAL: ALL questions use AskUserQuestion. Never ask inline text questions.**

The primary question is: **What do you want to build/add/fix?**

Everything else (scope, priority, constraints) is secondary and derived from features.

Check for inputs:
- Pending todos from STATE.md (potential features)
- Untested assumptions from MILESTONE-AUDIT.md (potential infrastructure work)
- Known gaps or pain points from usage
- User's ideas for what's next

```bash
# Check for assumptions from previous milestone audit
ASSUMPTIONS=$(cat .planning/v*-MILESTONE-AUDIT.md 2>/dev/null | grep -c "assumptions:" || echo 0)
```

**1. Open with context-aware options:**

Use AskUserQuestion:
- header: "Next"
- question: "What do you want to add, improve, or fix in this milestone?"
- options:
  - [Pending todos from STATE.md if any]
  - [If ASSUMPTIONS > 0: "Address untested assumptions ({N} items)"]
  - "New features"
  - "Improvements to existing"
  - "Bug fixes"
  - "Let me describe"

**If user selects "Address untested assumptions":**

Present the assumptions list from MILESTONE-AUDIT.md:

```
## Untested Assumptions from v{X.Y}

These tests were skipped because required states couldn't be mocked:

| Phase | Test | Expected Behavior | Reason |
|-------|------|-------------------|--------|
| 04-comments | Error state display | Shows error message when API fails | Can't mock API errors |
| 04-comments | Empty state | Shows placeholder when no comments | Can't clear test data |
| 05-auth | Session timeout | Redirects to login after 30min | Can't manipulate time |

To verify these, you'd need:
- Error response mocking (API interceptor or mock server)
- State reset capabilities (clear data for empty states)
- Time manipulation (for timeout testing)
```

Then use AskUserQuestion:
- header: "Assumptions"
- question: "Which assumptions do you want to address?"
- options:
  - "All of them — plan test infrastructure"
  - "Just error states"
  - "Just empty states"
  - "None for now — they're low risk"

Continue to feature gathering based on selection.

**2. Follow the thread (don't switch topics):**

Based on their response, dig deeper into THAT topic before moving on:

| They said | Follow-up |
|-----------|-----------|
| Named a feature | "What should [feature] do? What's the core behavior?" |
| "New features" | "What capability is missing? What would users do with it?" |
| "Improvements" | "Which existing feature needs improvement? What's the friction?" |
| "Bug fixes" | "What's broken? How does it manifest?" |

**3. Probe for edges:**

Once you understand the feature, probe:
- "What's the simplest version of this that would be useful?"
- "What would make this feel complete vs MVP?"
- "Any constraints I should know about?"

**4. Explore features:**

Based on their response, use AskUserQuestion:

If they named specific features:
- header: "Feature Details"
- question: "Tell me more about [feature] - what should it do?"
- options: [Contextual options based on feature type + "Let me describe it"]

If they described a general direction:
- header: "Breaking It Down"
- question: "That could involve [A], [B], [C] - which matter most?"
- options: [Specific sub-features + "All of them" + "Something else"]

If they're not sure:
- header: "Starting Points"
- question: "What's been frustrating or missing?"
- options: [Pending todos from STATE.md + pain point categories + "Let me think about it"]

**5. Prioritize:**

Use AskUserQuestion:
- header: "Priority"
- question: "Which of these matters most?"
- options: [Features they mentioned + "All equally important" + "Let me prioritize"]

After gathering features, synthesize:

```
Based on what you described:

**Features:**
- [Feature 1]: [brief description]
- [Feature 2]: [brief description]
- [Feature 3]: [brief description]

**Estimated scope:** [N] phases
**Theme suggestion:** v[X.Y] [Name]
```

**6. Decision gate:**

Use AskUserQuestion:
- header: "Ready?"
- question: "Ready to create the milestone, or explore more?"
- options (ALL THREE REQUIRED):
  - "Create milestone" - Proceed to /gsd:new-milestone
  - "Ask more questions" - Help me think through this more
  - "Let me add context" - I have more to share

If "Ask more questions" → return to step 2 with new probes.
If "Let me add context" → receive input → return to step 2.
Loop until "Create milestone" selected.
</step>

<step name="write_context">
Write milestone context to file for handoff.

**File:** `.planning/MILESTONE-CONTEXT.md`

Use template from ~/.claude/get-shit-done/templates/milestone-context.md

**Calculate next phase number:**

```bash
# Find highest existing phase number
LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '[0-9]+' | head -1)

if [ -n "$LAST_PHASE" ]; then
  NEXT_PHASE=$((10#$LAST_PHASE + 1))
else
  NEXT_PHASE=1
fi
echo "Next phase number: $NEXT_PHASE"
```

Populate with:
- Features identified during discussion
- Suggested milestone name and theme
- Estimated phase count
- How features map to phases
- Any constraints or scope boundaries mentioned
- **Starting phase number** (calculated above)

```bash
# Write the context file
cat > .planning/MILESTONE-CONTEXT.md << 'EOF'
# Milestone Context

**Generated:** [today's date]
**Status:** Ready for /gsd:new-milestone

<features>
## Features to Build

- **[Feature 1]**: [description]
- **[Feature 2]**: [description]
- **[Feature 3]**: [description]

</features>

<scope>
## Scope

**Suggested name:** v[X.Y] [Theme Name]
**Estimated phases:** [N]
**Focus:** [One sentence theme/focus]

</scope>

<starting_phase>
## Starting Phase

Next phase number: $NEXT_PHASE (calculated from existing phases)

</starting_phase>

<constraints>
## Constraints

- [Any constraints mentioned]

</constraints>

<notes>
## Additional Context

[Anything else from discussion]

</notes>

---

*This file is temporary. It will be deleted after /gsd:new-milestone creates the milestone.*
EOF
```
</step>

<step name="handoff">
Present summary and hand off to create-milestone:

```
Milestone scope defined:

**Features:**
- [Feature 1]: [description]
- [Feature 2]: [description]
- [Feature 3]: [description]

**Suggested milestone:** v[X.Y] [Theme Name]

Context saved to `.planning/MILESTONE-CONTEXT.md`

---

## ▶ Next Up

**Create Milestone v[X.Y]** — [Theme Name]

`/gsd:new-milestone`

<sub>`/clear` first → fresh context window</sub>

---
```
</step>

</process>

<success_criteria>

- Project state loaded (STATE.md, MILESTONES.md)
- Previous milestone context presented
- **Features identified** - What to build/add/fix (the substance)
- Features explored with clarifying questions
- Scope synthesized from features (not asked abstractly)
- **MILESTONE-CONTEXT.md created** with features and scope
- Context handed off to /gsd:new-milestone
</success_criteria>
