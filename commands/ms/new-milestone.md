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
</context>

<process>

1. **Load context:**
   - Read PROJECT.md (existing project, Validated requirements, decisions)
   - Read MILESTONES.md (what shipped previously)
   - Read STATE.md (pending todos, blockers)
   - Calculate previous milestone version from MILESTONES.md (e.g., if last shipped was v1.0, previous=1.0)

2. **Strategic assessment (internal — do not output this step):**
   - Load PROJECT.md (vision, audience, USP, problem space)
   - Load MILESTONES.md (what shipped)
   - Load STATE.md (pending todos, blockers)
   - Check for previous milestone artifacts using the version calculated in step 1:
     - `.planning/milestones/v{VERSION}-DECISIONS.md` (if exists)
     - `.planning/milestones/v{VERSION}-MILESTONE-AUDIT.md` (if exists)
     - `.planning/TECH-DEBT.md` (if exists)
   - Identify outstanding tech debt, unaddressed requirements, high-impact gaps
   - This is background analysis — synthesize silently, surface through suggestions in step 3

3. **Present suggested directions:**

   Output a brief markdown summary:

   ```
   ## Suggested Directions

   - **[Direction 1]** — [brief rationale]
   - **[Direction 2]** — [brief rationale]
   - **[Direction 3]** — [brief rationale]
   ```

   Sources for suggestions:
   - High-impact tech debt from TECH-DEBT.md or MILESTONE-AUDIT.md
   - Unaddressed requirements from previous milestones
   - Strategic features inferred from PROJECT.md's problem/audience/USP

   Evaluate each by impact on user engagement, revenue, or growth.

   If no meaningful artifacts exist (first milestone after v1.0), base suggestions purely on PROJECT.md.

4. **Freeform opening:**

   Ask inline (freeform text, NOT AskUserQuestion):

   "What do you want to build next?"

   The user can pick from suggestions, combine them, or go a completely different direction.

5. **Follow threads:**
   - Based on what the user said, ask follow-up questions using AskUserQuestion
   - Challenge vagueness, make abstract concrete
   - Consult `questioning.md` for techniques
   - Weave in relevant previous context (tech debt, pending todos) as natural follow-ups when relevant, not as a wall of info upfront
   - Continue until clear goals emerge

6. **Decision gate:**

   Use AskUserQuestion:
   - header: "Ready?"
   - question: "I think I understand what you want to build. Ready to update PROJECT.md?"
   - options:
     - "Update PROJECT.md" — Let's move forward
     - "Keep exploring" — I want to share more / ask me more

   Loop until "Update PROJECT.md" selected.

7. **Determine milestone version:**
   - Parse last version from MILESTONES.md
   - Suggest next version (v1.0 → v1.1, or v2.0 for major)
   - Confirm with user

8. **Update PROJECT.md:**

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

9. **Update STATE.md:**

   ```markdown
   ## Current Position

   Phase: Not started (run /ms:create-roadmap)
   Plan: —
   Status: Defining requirements
   Last activity: [today] — Milestone v[X.Y] started
   ```

10. **Git commit:**
   ```bash
   git add .planning/PROJECT.md .planning/STATE.md
   git commit -m "docs: start milestone v[X.Y] [Name]"
   ```

11. **Calculate next phase for context:**

   ```bash
   LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '[0-9]+' | head -1)
   if [ -n "$LAST_PHASE" ]; then
     NEXT_PHASE=$((10#$LAST_PHASE + 1))
   else
     NEXT_PHASE=1
   fi
   echo "Next milestone phases will start at: Phase $NEXT_PHASE"
   ```

12. **Route to next step:**

    Based on the conversation, recommend ONE path. If unfamiliar domains or open technical questions surfaced, recommend `/ms:research-project`. Otherwise recommend `/ms:define-requirements`.

    ```
    Milestone v[X.Y] [Name] initialized.

    PROJECT.md updated with new goals.
    Phases will start at: Phase $NEXT_PHASE

    ---

    ## ▶ Next Up

    **[Recommended command name]** — [one-line reason from conversation]

    `/ms:[recommended-command]`

    `/clear` first — fresh context window

    ---

    **Also available:** `/ms:[alternative-command]`
    ```

13. **Update last command**
    - Update `.planning/STATE.md` Last Command field
    - Format: `Last Command: ms:new-milestone $ARGUMENTS | YYYY-MM-DD HH:MM`

</process>

<success_criteria>
- PROJECT.md updated with Current Milestone section
- Active requirements reflect new milestone goals
- STATE.md reset for new milestone
- Git commit made
- User routed to define-requirements (or research-project)
</success_criteria>
