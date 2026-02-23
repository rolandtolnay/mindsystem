---
type: prompt
name: ms:complete-milestone
description: Archive completed milestone and prepare for next version
argument-hint: <version>
allowed-tools:
  - Read
  - Write
  - Bash
  - Task
---

<objective>
Mark milestone {{version}} complete, archive to milestones/, and update ROADMAP.md and REQUIREMENTS.md.

Purpose: Create historical record of shipped version, archive milestone artifacts (roadmap + requirements), and prepare for next milestone.
Output: Milestone archived (roadmap + requirements), PROJECT.md evolved, git tagged.
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

- Version: {{version}} (e.g., "1.0", "1.1", "2.0")
  </context>

<process>

**Follow complete-milestone.md workflow:**

0. **Check for audit:**

   - Look for `.planning/v{{version}}-MILESTONE-AUDIT.md`
   - If missing or stale: recommend `/ms:audit-milestone` first
   - If audit status is `gaps_found`: recommend `/ms:plan-milestone-gaps` first
   - If audit status is `passed`: proceed to step 1

   ```markdown
   ## Pre-flight Check

   {If no v{{version}}-MILESTONE-AUDIT.md:}
   ⚠ No milestone audit found. Run `/ms:audit-milestone` first to verify
   requirements coverage, cross-phase integration, and E2E flows.

   {If audit has gaps:}
   ⚠ Milestone audit found gaps. Run `/ms:plan-milestone-gaps` to create
   phases that close the gaps, or proceed anyway to accept as tech debt.

   {If audit passed:}
   ✓ Milestone audit passed. Proceeding with completion.
   ```

1. **Verify readiness and gather stats:**

   ```bash
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

   - Full evolution review (What This Is, Core Value, Requirements audit, Key Decisions, Context)
   - Move all shipped requirements to Validated
   - Update "Last updated" footer

5. **Archive milestone:**

   - Create `.planning/milestones/v{{version}}/` directory
   - Create `.planning/milestones/v{{version}}/ROADMAP.md` from template
   - Delete ROADMAP.md

6. **Archive requirements:**

   - Create `.planning/milestones/v{{version}}/REQUIREMENTS.md`
   - Mark all requirements as complete with outcomes
   - Delete `.planning/REQUIREMENTS.md`

7. **Archive milestone files:**

   ```bash
   ms-tools archive-milestone-files v{{version}}
   ```

8. **Archive and cleanup phases:**

   ```bash
   ms-tools archive-milestone-phases $PHASE_START $PHASE_END v{{version}}
   ```

9. **Update STATE.md:**

    - Update project reference with current core value and next focus
    - Reset current position for next milestone

10. **Commit and tag:**

    - Stage: MILESTONES.md, PROJECT.md, STATE.md, archive files, deletions
    - Commit: `chore: archive v{{version}} milestone`
    - Tag: `git tag -a v{{version}} -m "[milestone summary]"`
    - Ask about pushing tag

11. **Offer next steps:**
    - `/ms:new-milestone` — discover goals and update PROJECT.md

12. **Update last command:**
    - Format: `Last Command: ms:complete-milestone $ARGUMENTS | YYYY-MM-DD HH:MM`

</process>

<success_criteria>

- PROJECT.md full evolution review completed (What This Is, Core Value, Requirements, Key Decisions, Context)
- All shipped requirements moved to Validated in PROJECT.md
- Key Decisions updated with outcomes
- Milestone archived to `.planning/milestones/v{{version}}/ROADMAP.md`
- Requirements archived to `.planning/milestones/v{{version}}/REQUIREMENTS.md`
- `.planning/REQUIREMENTS.md` deleted (fresh for next milestone)
- Git tag v{{version}} created
  </success_criteria>

<critical_rules>

- **Verify completion:** All phases must have SUMMARY.md files
- **Archive before deleting:** Always create archive files (ROADMAP, REQUIREMENTS) before updating/deleting originals
- **One-line summary:** Collapsed milestone in ROADMAP.md should be single line with link
  </critical_rules>
