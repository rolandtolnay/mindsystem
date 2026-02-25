---
type: prompt
name: ms:complete-milestone
description: Archive completed milestone and prepare for next milestone
argument-hint: "[name]"
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
---

<objective>
Mark milestone complete, archive to milestones/, and update ROADMAP.md and REQUIREMENTS.md.

Purpose: Create historical record of shipped milestone, archive milestone artifacts (roadmap + requirements), and prepare for next milestone.
Output: Milestone archived (roadmap + requirements), PROJECT.md evolved.
</objective>

<execution_context>
**Load these files NOW (before proceeding):**

- @~/.claude/mindsystem/workflows/complete-milestone.md (main workflow)
- @~/.claude/mindsystem/templates/milestone-archive.md (archive template)
  </execution_context>

<context>
**Project files:**
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/PROJECT.md`

**User input:**

- Milestone: $ARGUMENTS (optional — auto-detect from PROJECT.md `## Current Milestone:` header)
  </context>

<process>

**Follow complete-milestone.md workflow:**

0. **Resolve milestone identity:**

   - If argument provided: use as milestone name, generate slug
   - If no argument: parse milestone name from PROJECT.md `## Current Milestone:` header, generate slug
   - If neither found: error — ask user for milestone name

0.5. **Check for audit:**

   - Look for `.planning/MILESTONE-AUDIT.md`
   - If missing or stale: recommend `/ms:audit-milestone` first
   - If audit status is `gaps_found`: recommend addressing gaps via `/ms:adhoc` or `/ms:add-phase`
   - If audit status is `passed`: proceed to step 1

   ```markdown
   ## Pre-flight Check

   {If no MILESTONE-AUDIT.md:}
   ⚠ No milestone audit found. Run `/ms:audit-milestone` first to verify
   requirements coverage, cross-phase integration, and E2E flows.

   {If audit has gaps:}
   ⚠ Milestone audit found gaps. Address via `/ms:adhoc` (1-2 small fixes)
   or `/ms:add-phase` (larger remediation), or proceed anyway to accept as tech debt.

   {If audit passed:}
   ✓ Milestone audit passed. Proceeding with completion.
   ```

1. **Verify readiness and gather stats:**

   ```bash
   # ms-tools is on PATH — invoke directly, not as a script path
   ms-tools gather-milestone-stats $PHASE_START $PHASE_END
   ```

   - If NOT READY: stop and report incomplete plans
   - If READY: present readiness + stats summary, proceed

2. **Extract accomplishments:**

   - Read all phase SUMMARY.md files in milestone range
   - Extract 4-6 key accomplishments

3. **Create MILESTONES.md entry:**

   - Create or update `.planning/MILESTONES.md` using `templates/milestone.md`
   - Prepend new entry (reverse chronological order)

4. **Update PROJECT.md:**

   - Full evolution review (What This Is, Core Value, Requirements audit, **Deferred triage**, Key Decisions, Context)
   - Move all shipped requirements to Validated
   - Triage v2 requirements and CONTEXT.md deferred ideas (defer, exclude, or discard)
   - Update "Last updated" footer

5. **Archive milestone:**

   - Create `.planning/milestones/{{slug}}/` directory
   - Create `.planning/milestones/{{slug}}/ROADMAP.md` from template
   - Delete ROADMAP.md

6. **Archive requirements:**

   - Create `.planning/milestones/{{slug}}/REQUIREMENTS.md`
   - Mark all requirements as complete with outcomes
   - Delete `.planning/REQUIREMENTS.md`

7. **Archive milestone files:**

   ```bash
   ms-tools archive-milestone-files {{slug}}
   ```

8. **Archive and cleanup phases:**

   ```bash
   ms-tools archive-milestone-phases $PHASE_START $PHASE_END {{slug}}
   ```

9. **Update STATE.md:**

    - Update project reference with current core value and next focus
    - Reset current position for next milestone

10. **Commit:**

    - Stage: MILESTONES.md, PROJECT.md, STATE.md, archive files, deletions
    - Commit: `chore: archive {{name}} milestone`

11. **Offer next steps:**
    - `/ms:new-milestone` — discover goals and update PROJECT.md

12. **Update last command:** `ms-tools set-last-command "ms:complete-milestone $ARGUMENTS"`

</process>

<success_criteria>

- PROJECT.md full evolution review completed (What This Is, Core Value, Requirements, Key Decisions, Context)
- All shipped requirements moved to Validated in PROJECT.md
- Deferred items triaged (v2 requirements + CONTEXT.md deferred ideas)
- Key Decisions updated with outcomes
- Milestone archived to `.planning/milestones/{{slug}}/ROADMAP.md`
- Requirements archived to `.planning/milestones/{{slug}}/REQUIREMENTS.md`
- `.planning/REQUIREMENTS.md` deleted (fresh for next milestone)
  </success_criteria>

<critical_rules>

- **Verify completion:** All phases must have SUMMARY.md files
- **Archive before deleting:** Always create archive files (ROADMAP, REQUIREMENTS) before updating/deleting originals
- **One-line summary:** Collapsed milestone in ROADMAP.md should be single line with link
  </critical_rules>
