---
name: ms:new-milestone
description: Start a new milestone cycle — update PROJECT.md and route to requirements
argument-hint: "[milestone name, e.g., 'v1.1 Notifications']"
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Start a new milestone by updating PROJECT.md with new goals, then routing to the requirements → roadmap cycle.

This is the brownfield equivalent of new-project. The project exists, PROJECT.md has history. This command gathers "what's next" and updates PROJECT.md to reflect the new milestone's goals.

Output: Updated PROJECT.md, routes to research-project or define-requirements
</objective>

<execution_context>
@~/.claude/mindsystem/references/questioning.md
@~/.claude/mindsystem/templates/project.md
</execution_context>

<context>
Milestone name: $ARGUMENTS (optional - will prompt if not provided)

**Load project context:**
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/MILESTONES.md
@.planning/config.json

**For discovery mode (load if user selects "Help me figure it out"):**
@.planning/milestones/v{previous}-DECISIONS.md (if exists)
@.planning/milestones/v{previous}-MILESTONE-AUDIT.md (if exists)
</context>

<process>

1. **Load context:**
   - Read PROJECT.md (existing project, Validated requirements, decisions)
   - Read MILESTONES.md (what shipped previously)
   - Read STATE.md (pending todos, blockers)
   - Calculate previous milestone version for context files

2. **Present what shipped (if MILESTONES.md exists):**

   ```bash
   cat .planning/MILESTONES.md 2>/dev/null
   ```

   Format the presentation:

   ```
   ---

   ## Previous Milestone

   **Last milestone:** v[X.Y] [Name] (shipped [DATE])

   **Key accomplishments:**
   - [From MILESTONES.md accomplishments]
   - [From MILESTONES.md accomplishments]

   **Validated requirements:**
   - [From PROJECT.md Validated section]

   **Pending todos (if any):**
   - [From STATE.md accumulated context]

   ---
   ```

3. **Decision gate:**

   Use AskUserQuestion:
   - header: "New Milestone"
   - question: "How do you want to start?"
   - options:
     - "I know what to build" — proceed to goal gathering
     - "Help me figure it out" — enter discovery mode with previous context
     - "Show previous decisions first" — view DECISIONS.md and AUDIT.md, then decide

4. **Gather milestone goals:**

   **If "I know what to build":**
   - Ask directly: "What do you want to build next?"
   - Use AskUserQuestion to explore features
   - Probe for priorities, constraints, scope

   **If "Show previous decisions first":**
   - Load and present `.planning/milestones/v{previous}-DECISIONS.md`
   - Load and present `.planning/milestones/v{previous}-MILESTONE-AUDIT.md` assumptions
   - Return to decision gate (without this option)

   **If "Help me figure it out" (Discovery Mode):**
   - Load `.planning/milestones/v{previous}-DECISIONS.md` and `.planning/milestones/v{previous}-MILESTONE-AUDIT.md`
   - Surface untested assumptions from AUDIT.md:
     ```
     📋 Untested from v[previous]:
     - Error state displays
     - Empty state handling
     - [etc. from assumptions section]
     ```
   - Run AskUserQuestion-based discovery:
     - "What do you want to add, improve, or fix?"
     - Options: Address untested assumptions, New features, Improvements, Bug fixes, Let me describe
   - Follow up with probing questions
   - Continue until clear goals emerge

5. **Determine milestone version:**
   - Parse last version from MILESTONES.md
   - Suggest next version (v1.0 → v1.1, or v2.0 for major)
   - Confirm with user

6. **Update PROJECT.md:**

   Add/update these sections:

   ```markdown
   ## Current Milestone: v[X.Y] [Name]

   **Goal:** [One sentence describing milestone focus]

   **Target features:**
   - [Feature 1]
   - [Feature 2]
   - [Feature 3]
   ```

   Update Active requirements section with new goals.

   Update "Last updated" footer.

7. **Update STATE.md:**

   ```markdown
   ## Current Position

   Phase: Not started (run /ms:create-roadmap)
   Plan: —
   Status: Defining requirements
   Last activity: [today] — Milestone v[X.Y] started
   ```

8. **Git commit:**
   ```bash
   git add .planning/PROJECT.md .planning/STATE.md
   git commit -m "docs: start milestone v[X.Y] [Name]"
   ```

9. **Calculate next phase for context:**

   ```bash
   LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '[0-9]+' | head -1)
   if [ -n "$LAST_PHASE" ]; then
     NEXT_PHASE=$((10#$LAST_PHASE + 1))
   else
     NEXT_PHASE=1
   fi
   echo "Next milestone phases will start at: Phase $NEXT_PHASE"
   ```

10. **Route to next step:**

   ```
   Milestone v[X.Y] [Name] initialized.

   PROJECT.md updated with new goals.
   Phases will start at: Phase $NEXT_PHASE

   ---

   ## ▶ Next Up

   Choose your path:

   **Option A: Research first** (new domains/capabilities)
   Research ecosystem before scoping. Discovers patterns, expected features, architecture approaches.

   `/ms:research-project`

   **Option B: Define requirements directly** (familiar territory)
   Skip research, define requirements from what you know.

   `/ms:define-requirements`

   <sub>`/clear` first → fresh context window</sub>

   ---
   ```

</process>

<success_criteria>
- PROJECT.md updated with Current Milestone section
- Active requirements reflect new milestone goals
- STATE.md reset for new milestone
- Git commit made
- User routed to define-requirements (or research-project)
</success_criteria>
