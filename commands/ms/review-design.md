---
name: ms:review-design
description: Review a screen's design like a designer friend would — focused, practical, high-impact
argument-hint: "[screenshot path, file path, feature name, or description]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Skill
  - AskUserQuestion
---

<objective>
Review the design of an existing screen or flow the way a designer friend would: understand what the screen is trying to do, simulate the user experience, and suggest the 3-5 highest-impact improvements.

Not a comprehensive audit. Not a redesign. A focused review that finds what matters most and fixes it.

**When to use:**
- A screen "feels off" but you can't pinpoint why
- After implementing a feature, before shipping
- Periodic quality pass on existing screens

**Input modes:**
- **Screenshot + code** (best): Provide a screenshot path. Visual input lets you reason about hierarchy, whitespace, and flow directly instead of reconstructing from code.
- **Code only** (good): Reconstruct the screen mentally from the widget/component tree and reason about the user experience from there.
</objective>

<context>
**User's review request:**
$ARGUMENTS

**Current git status:**
!`git status --short`
</context>

<process>

## Step 1: Identify Target

Parse `$ARGUMENTS`:

- **Screenshot path** (image file) → Read the image. Identify and read the corresponding code files.
- **File path** → Read that file and related files in the same feature (widgets, providers, models)
- **Feature/area name** → Search for relevant files
- **Phase number** → Find phase directory, read SUMMARY.md for implemented files
- **Description** → Check recent git changes or conversation context
- **Empty or unclear** → AskUserQuestion:

```
Question: "What should I review?"
Options:
- "I'll share a screenshot" - Paste or provide a path to a screenshot
- "Specific screen" - I'll provide a file path or feature name
- "Recent work" - Review files from recent commits
```

If no screenshot was provided, ask once:

```
Question: "Do you have a screenshot? It significantly improves review quality."
Options:
- "Yes, let me share it" - Paste or provide a path
- "No, review from code" - Analyze implementation files directly
```

Read all relevant code files for the target screen/flow.

## Step 2: Understand the Screen's Job

Before analyzing, establish what this screen is trying to accomplish.

**Load context:**
- Read `.planning/PROJECT.md` for product type, core value, target audience
- If phase-based, grep `.planning/ROADMAP.md` for phase requirements
- Glob for existing DESIGN.md in `.planning/phases/` for design intent
- Scan available skills in system-reminder for matches related to UI, design, or the screen's platform/framework. If matches found, present via AskUserQuestion with `multiSelect: true`: each matching skill is one option (label: skill name, description: what it provides), always include a "None — skip skill loading" option. User selects which to load, skips, or types a skill name in the free-text field. Load selected skills via Skill tool for existing patterns.

**State the screen's job in one sentence:**
> "This screen helps the user [accomplish X]."

This sentence filters every subsequent suggestion. An improvement that doesn't make the screen better at its job doesn't make the cut.

## Step 3: Experience Simulation

Walk through the screen as a user. This is the core analysis — a simulation, not a checklist. Do not organize findings by design categories.

**If screenshot available**, look at it and answer:
1. What draws my eye first? Is that the most important element on this screen?
2. Can I immediately tell what this screen wants me to do?
3. Where does my attention flow after the first element? Is the reading order clear?
4. What feels cluttered, or where are elements competing for attention that shouldn't be?
5. Is there enough breathing room around important content?
6. Does the text help me understand what to do, or is it vague/jargon-heavy?
7. Are unrelated elements sitting close enough to feel grouped, or related elements spread far enough apart to feel disconnected?
8. Does this feel like a native app screen, or like a web form wearing a native shell?
9. If I'm a new user, would I know how to complete the primary action?

**If code only**, reconstruct the screen from the widget/component tree, then answer the same questions. Pay special attention to:
- Widget nesting depth as proxy for visual complexity
- Padding/margin values for whitespace
- String literals for copy quality
- Button/action placement for flow
- Conditional rendering for state completeness (loading, empty, error)

## Step 4: Top 3-5 Improvements

From the simulation, select only the 3-5 changes with the highest user impact.

**Filtering question:** "If I could only change ONE thing, what would make the biggest difference to a user?" Then the next, then the next. Stop at 5.

**Priority order:**
1. **Flow friction** — user can't complete their primary task intuitively
2. **Hierarchy/attention** — wrong thing dominates, or user can't find what they need
3. **Density/whitespace** — screen feels cramped, overwhelming, or unbalanced
4. **Copy/labeling** — user doesn't understand what something means or what to do next
5. **Missing states** — user hits a dead end (no loading feedback, unhelpful empty state, cryptic error)

**Frame each as a user experience story:**

```markdown
### 1. [Brief description of what changes]

**What a user experiences:** [The friction or confusion from the user's perspective]

**Suggested fix:** [Specific, implementable change — layout shift, text rewrite, element repositioning, spacing adjustment, visual weight change]

**Files:** `path/to/file` (lines ~N-M)
```

Good framing: "The primary action button competes with 3 secondary actions at equal visual weight — a user has to read all four to find what they came here to do."

Bad framing: "Button color should be changed from gray to blue for better contrast."

## Step 5: Present and Confirm

```markdown
## Design Review: [Screen/Feature Name]

**Screen's job:** [one-sentence job]

**Top [N] improvements** (highest user impact first):

[improvements from Step 4]
```

Use AskUserQuestion:

```
Question: "Which improvements should I apply?"
Options:
- "Apply all" - Implement all suggested changes
- "Let me pick" - I'll specify which ones
- "Report only" - No code changes needed
```

## Step 6: Apply Approved Changes

For each approved improvement:
1. Read current file state
2. Apply the change via Edit tool
3. Log what changed

One logical change at a time. Preserve public APIs and test expectations.

## Step 7: Verify and Summarize

Run platform-appropriate static analysis and tests. If failures occur, identify which change caused it and offer to revert.

Present:

```markdown
## Review Complete

**Screen:** [name]
**Applied:** N improvements

### Changes
- `path/to/file`: [what changed]

### Next
Run the app and check this screen — [describe the expected visual difference in one sentence].
```

## Step 8: Update Last Command

```bash
ms-tools set-last-command "ms:review-design $ARGUMENTS"
```

</process>

<success_criteria>
- [ ] Improvements framed as user experience stories, not property changes
- [ ] Screen's job identified in one sentence — every suggestion filtered through it
- [ ] Experience simulation performed (screenshot or code-based walkthrough)
- [ ] Maximum 5 improvements, prioritized by user impact
- [ ] Approved changes applied and verified
</success_criteria>
