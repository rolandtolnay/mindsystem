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

   Run the stats script to check readiness and collect milestone statistics:

   ```bash
   ~/.claude/mindsystem/scripts/gather-milestone-stats.sh $PHASE_START $PHASE_END
   ```

   - If NOT READY: stop and report incomplete plans
   - If READY: present readiness + stats summary, proceed

2. **Extract accomplishments:**

   - Read all phase SUMMARY.md files in milestone range
   - Extract 4-6 key accomplishments
   - Present for approval

3. **Archive milestone:**

   - Create `.planning/milestones/v{{version}}/` directory
   - Create `.planning/milestones/v{{version}}/ROADMAP.md`
   - Extract full phase details from ROADMAP.md
   - Fill milestone-archive.md template
   - Update ROADMAP.md to one-line summary with link

4. **Archive requirements:**

   - Create `.planning/milestones/v{{version}}/REQUIREMENTS.md`
   - Mark all v1 requirements as complete (checkboxes checked)
   - Note requirement outcomes (validated, adjusted, dropped)
   - Delete `.planning/REQUIREMENTS.md` (fresh one created for next milestone)

5. **Archive milestone files:**

   Archive optional files (audit, context, research) to milestone directory:

   ```bash
   ~/.claude/mindsystem/scripts/archive-milestone-files.sh v{{version}}
   ```

6. **Update PROJECT.md:**

   - Full evolution review (What This Is, Core Value, Requirements audit, Key Decisions)
   - Update "Last updated" footer

7. **Archive and cleanup phases:**

   Consolidate phase summaries, delete raw artifacts, and move phase directories to milestone archive. Runs after all steps that read summaries.

   ```bash
   ~/.claude/mindsystem/scripts/archive-milestone-phases.sh $PHASE_START $PHASE_END v{{version}}
   ```

8. **Commit and tag:**

   - Stage: MILESTONES.md, PROJECT.md, ROADMAP.md, STATE.md, archive files
   - Commit: `chore: archive v{{version}} milestone`
   - Tag: `git tag -a v{{version}} -m "[milestone summary]"`
   - Ask about pushing tag

9. **Offer next steps:**
   - `/ms:new-milestone` — discover goals and update PROJECT.md (includes optional discovery mode)

10. **Update last command**
    - Update `.planning/STATE.md` Last Command field
    - Format: `Last Command: ms:complete-milestone $ARGUMENTS | YYYY-MM-DD HH:MM`

</process>

<success_criteria>

- Milestone archived to `.planning/milestones/v{{version}}/ROADMAP.md`
- Requirements archived to `.planning/milestones/v{{version}}/REQUIREMENTS.md`
- Optional files archived (audit, context, research — whichever existed)
- Phase summaries consolidated, artifacts deleted, phase dirs moved to archive
- `.planning/phases/` clean for next milestone
- `.planning/REQUIREMENTS.md` deleted (fresh for next milestone)
- PROJECT.md full evolution review completed
- Git tag v{{version}} created
- Commit successful
- User knows next steps (/ms:new-milestone)
  </success_criteria>

<critical_rules>

- **Load workflow first:** Read complete-milestone.md before executing
- **Verify completion:** All phases must have SUMMARY.md files
- **User confirmation:** Wait for approval at verification gates
- **Archive before deleting:** Always create archive files (ROADMAP, REQUIREMENTS) before updating/deleting originals
- **One-line summary:** Collapsed milestone in ROADMAP.md should be single line with link
- **Context efficiency:** Archive keeps ROADMAP.md and REQUIREMENTS.md constant size per milestone
- **Fresh requirements:** Next milestone starts with `/ms:create-roadmap`, not reusing old file
  </critical_rules>
