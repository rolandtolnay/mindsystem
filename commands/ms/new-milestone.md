---
name: ms:new-milestone
description: Start a new milestone — discover what to build, update PROJECT.md, create context for downstream
argument-hint: "[milestone name, e.g., 'v1.1 Notifications']"
allowed-tools:
  - Read
  - Write
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Start a new milestone by helping the user discover what to build next, then updating PROJECT.md and creating MILESTONE-CONTEXT.md for downstream consumption.

Self-contained command — three phases: Orient (load context, present directions), Deepen (collaborative discovery), Commit (update files, route forward).

Output: Updated PROJECT.md, new MILESTONE-CONTEXT.md, routes to create-roadmap or research-project
</objective>

<execution_context>
@~/.claude/mindsystem/references/questioning.md
@~/.claude/mindsystem/templates/project.md
@~/.claude/mindsystem/templates/milestone-context.md
</execution_context>

<context>
Milestone name: $ARGUMENTS (optional — will emerge during discovery if not provided)

**Load project context:**
@.planning/PROJECT.md
@.planning/STATE.md
@.planning/MILESTONES.md
@.planning/config.json
</context>

<process>

## Phase 1: Orient

1. **Load context:**
   - Read PROJECT.md (existing project, validated requirements, decisions)
   - Read MILESTONES.md (what shipped previously)
   - Read STATE.md (pending todos, blockers)
   - Read config.json (project settings)
   - Calculate previous milestone version from MILESTONES.md (e.g., if last shipped was v1.0, previous=1.0)

2. **Check for active milestone:**

   If STATE.md or ROADMAP.md indicates a milestone is in progress:

   Use AskUserQuestion:
   - header: "Active milestone"
   - question: "There's a milestone in progress (v[X.Y]). What do you want to do?"
   - options:
     - "Complete it first" — run /ms:complete-milestone
     - "Add phases to it" — run /ms:add-phase
     - "Continue anyway" — discuss next milestone scope

   If "Complete it first" or "Add phases to it": present the relevant command and stop.
   If "Continue anyway": proceed.

3. **Strategic assessment (silent — do not output this step):**
   - Check for previous milestone artifacts using calculated version:
     - `.planning/knowledge/*.md` (subsystem knowledge files — persist across milestones)
     - `.planning/milestones/v{VERSION}/MILESTONE-AUDIT.md` (if exists)
     - `.planning/TECH-DEBT.md` (if exists)
   - Identify: outstanding tech debt, untested assumptions, high-impact gaps, unaddressed requirements
   - This is background analysis — synthesize silently, surface through suggestions in step 4

4. **Present brief context and suggested directions:**

   ```
   ## Last Milestone

   v[X.Y] [Name] — [key accomplishments, 1-2 lines]

   ## Suggested Directions

   - **[Direction 1]** — [brief rationale from tech debt, audit, or strategic gaps]
   - **[Direction 2]** — [brief rationale]
   - **[Direction 3]** — [brief rationale]
   ```

   Sources for suggestions:
   - Tech debt from TECH-DEBT.md, MILESTONE-AUDIT.md, or knowledge file Pitfalls sections
   - Settled decisions and patterns from knowledge files
   - Untested assumptions from previous audit
   - Unaddressed requirements from previous milestones
   - Strategic features inferred from PROJECT.md: Who It's For, Core Problem, How It's Different
   - Pending todos from STATE.md

   If no meaningful artifacts exist (first milestone after v1.0), base suggestions purely on PROJECT.md.

5. **Freeform opening:**

   Ask inline (freeform text, NOT AskUserQuestion):

   "What do you want to build next?"

   The user can pick a suggestion, combine them, describe their own idea, share external context (specs, docs, analytics), or ask for help thinking it through.

## Phase 2: Deepen

6. **Adaptive depth based on response clarity:**

   - **Clear, detailed response** → brief confirmation ("Sounds like you want X, Y, Z — let me confirm a few things"), then move toward Phase 3 quickly
   - **Vague response** → probe with AskUserQuestion, explore features, challenge vagueness
   - **External context shared** → integrate it, clarify implications, ask follow-ups

7. **Follow the thread:**
   - Dig into what they said before switching topics
   - Challenge vagueness, make abstract concrete (questioning.md techniques)
   - "When you say X, do you mean A or B?"
   - "Walk me through what that looks like"
   - "What's the simplest version of this that would be useful?"

8. **Probe for edges:**
   - Simplest useful version vs full vision
   - MVP vs complete — what can wait?
   - Constraints: technical, time, dependencies
   - What's explicitly NOT part of this milestone?

9. **Surface previous context organically:**
   - When relevant to what the user described, weave in tech debt, untested assumptions, pending todos
   - NOT as a wall of info upfront — only when it connects to their stated direction
   - "That relates to [tech debt item] from last milestone — want to address that too?"

10. **Synthesize periodically:**

    When you have a clear picture forming:

    ```
    Here's what I'm hearing:

    **Features:**
    - [Feature 1]: [brief description]
    - [Feature 2]: [brief description]

    **Priority:** [what matters most]
    **Scope boundary:** [what's NOT included]
    ```

11. **Decision gate:**

    Use AskUserQuestion:
    - header: "Ready?"
    - question: "Ready to create the milestone?"
    - options:
      - "Create milestone" — update PROJECT.md and generate context
      - "Keep exploring" — I want to share more or ask me more
      - "Let me add context" — I have specs/docs/details to share

    If "Keep exploring" or "Let me add context" → loop back to step 6.
    Loop until "Create milestone" selected.

## Phase 3: Commit

12. **Determine milestone version:**
    - Parse last version from MILESTONES.md
    - Suggest next version (v1.0 → v1.1, or v2.0 for major shifts)
    - Confirm with user via AskUserQuestion

13. **Present milestone summary:**

    ```
    ## Milestone Summary

    **Version:** v[X.Y] [Name]
    **Goal:** [One sentence]
    **Target features:**
    - [Feature 1]
    - [Feature 2]
    - [Feature 3]
    ```

    Use AskUserQuestion:
    - header: "Confirm"
    - question: "Look good?"
    - options:
      - "Looks good" — proceed
      - "Adjust" — let me change something

    If "Adjust" → ask what to change, update, re-confirm.

14. **Update PROJECT.md:**

    Add/update these sections:

    ```markdown
    ## Current Milestone: v[X.Y] [Name]

    **Goal:** [One sentence describing milestone focus]

    **Target features:**
    - [Feature 1]
    - [Feature 2]
    - [Feature 3]
    ```

    Update "Last updated" footer.
    Note: Milestone-specific goals live in MILESTONE-CONTEXT.md (step 15), not in PROJECT.md.

15. **Write MILESTONE-CONTEXT.md:**

    Create `.planning/MILESTONE-CONTEXT.md` using template from `~/.claude/mindsystem/templates/milestone-context.md`.

    Populate from the conversation:
    - Vision — the "why" in user's words
    - Features — with rationale and scope notes
    - External context — any specs, docs, or references shared
    - Scope boundaries — what's explicitly excluded
    - Priorities — must-have vs nice-to-have
    - Open questions — things needing research

16. **Update STATE.md:**

    ```markdown
    ## Current Position

    Phase: Not started (run /ms:create-roadmap)
    Plan: —
    Status: Defining requirements
    Last activity: [today] — Milestone v[X.Y] started

    Progress: ░░░░░░░░░░ 0%
    ```

    Keep Accumulated Context (decisions, blockers) from previous milestone.

17. **Git commit:**

    ```bash
    git add .planning/PROJECT.md .planning/STATE.md .planning/MILESTONE-CONTEXT.md
    git commit -m "$(cat <<'EOF'
    docs: start milestone v[X.Y] [Name]
    EOF
    )"
    ```

18. **Calculate next phase number:**

    ```bash
    LAST_PHASE=$(ls -d .planning/phases/[0-9]*-* 2>/dev/null | sort -V | tail -1 | grep -oE '[0-9]+' | head -1)
    if [ -n "$LAST_PHASE" ]; then
      NEXT_PHASE=$((10#$LAST_PHASE + 1))
    else
      NEXT_PHASE=1
    fi
    echo "Next milestone phases will start at: Phase $NEXT_PHASE"
    ```

19. **Route to next step:**

    Based on the conversation, recommend ONE path. If unfamiliar domains or open questions surfaced during discovery, recommend `/ms:research-project`. Otherwise recommend `/ms:create-roadmap`.

    ```
    Milestone v[X.Y] [Name] initialized.

    PROJECT.md updated with new goals.
    Context saved to MILESTONE-CONTEXT.md
    Phases will start at: Phase $NEXT_PHASE

    ---

    ## ▶ Next Up

    `/ms:[recommended-command]` — [one-line reason from conversation]

    <sub>`/clear` first → fresh context window</sub>

    ---

    **Also available:** `/ms:[alternative-command]` — [brief reason]

    ---
    ```

20. **Update last command:**
    - Update `.planning/STATE.md` Last Command field
    - Format: `Last Command: ms:new-milestone $ARGUMENTS | YYYY-MM-DD HH:MM`

</process>

<success_criteria>
- PROJECT.md updated with Current Milestone section
- MILESTONE-CONTEXT.md created with vision, features, scope, priorities
- STATE.md reset for new milestone
- Git commit made
- User routed to create-roadmap (or research-project if unknowns surfaced)
</success_criteria>
