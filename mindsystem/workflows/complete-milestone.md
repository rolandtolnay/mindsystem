<purpose>

Mark a shipped version (v1.0, v1.1, v2.0) as complete. This creates a historical record in MILESTONES.md, performs full PROJECT.md evolution review, archives ROADMAP.md and REQUIREMENTS.md, and tags the release in git.

</purpose>

<required_reading>

**Read these files NOW:**

1. templates/milestone.md
2. templates/milestone-archive.md
3. `.planning/ROADMAP.md`
4. `.planning/REQUIREMENTS.md`
5. `.planning/PROJECT.md`

</required_reading>

<archival_behavior>

When a milestone completes, this workflow:

1. Creates `.planning/milestones/v[X.Y]/` directory for all archive files
2. Extracts full milestone details to `.planning/milestones/v[X.Y]/ROADMAP.md`
3. Archives requirements to `.planning/milestones/v[X.Y]/REQUIREMENTS.md`
4. Archives milestone files via script (audit, context, research — whichever exist)
5. Consolidates phase summaries, deletes artifacts, moves phase dirs via script
6. Deletes REQUIREMENTS.md (fresh one created for next milestone)
7. Performs full PROJECT.md evolution review
8. Routes to `/ms:new-milestone` for next milestone

**Archive Format:**

**ROADMAP archive** uses `templates/milestone-archive.md` template with:
- Milestone header (status, phases, date)
- Full phase details from roadmap
- Milestone summary (decisions, issues, technical debt)

**PHASE-SUMMARIES** consolidates all `*-SUMMARY.md` files from phase directories, organized by phase and plan, before artifacts are deleted.

**phases/** contains the phase directories themselves (with remaining files like `.patch`, `mockups/`) moved from `.planning/phases/`.

**REQUIREMENTS archive** contains:
- All v1 requirements marked complete with outcomes
- Traceability table with final status
- Notes on any requirements that changed during milestone

</archival_behavior>

<process>

<step name="verify_readiness">

Read roadmap to determine milestone phase range (`PHASE_START`, `PHASE_END`) for the stats script:

```bash
cat .planning/ROADMAP.md
```

<config-check>

```bash
cat .planning/config.json 2>/dev/null
```

</config-check>

Run the stats script to get readiness status and git statistics:

```bash
~/.claude/mindsystem/scripts/gather-milestone-stats.sh $PHASE_START $PHASE_END
```

The script outputs:
- **Readiness:** Phase/plan counts, completeness, list of incomplete plans
- **Git Stats:** Commit range, timeline, diff stats

If status is NOT READY, stop and report which plans are incomplete.

If status is READY, present the combined output:

```
⚡ Auto-approved: Milestone scope verification

Milestone: [Name from ROADMAP.md]
[Script readiness output — phases, plans, completeness]
[Script git stats — range, timeline, changes]
```

Proceed directly to extract_accomplishments step.

</step>

<step name="extract_accomplishments">

Read all phase SUMMARY.md files in milestone range:

```bash
cat .planning/phases/01-*/01-*-SUMMARY.md
cat .planning/phases/02-*/02-*-SUMMARY.md
# ... for each phase in milestone
```

From summaries, extract 4-6 key accomplishments.

Present:

```
Key accomplishments for this milestone:
1. [Achievement from phase 1]
2. [Achievement from phase 2]
3. [Achievement from phase 3]
4. [Achievement from phase 4]
5. [Achievement from phase 5]
```

</step>

<step name="create_milestone_entry">

Create or update `.planning/MILESTONES.md`.

If file doesn't exist:

```markdown
# Project Milestones: [Project Name from PROJECT.md]

[New entry]
```

If exists, prepend new entry (reverse chronological order).

Use template from `templates/milestone.md`:

```markdown
## v[Version] [Name] (Shipped: YYYY-MM-DD)

**Delivered:** [One sentence from user]

**Phases completed:** [X-Y] ([Z] plans total)

**Key accomplishments:**

- [List from previous step]

**Stats:**

- [Files] files created/modified
- [LOC] lines of [language]
- [Phases] phases, [Plans] plans, [Tasks] tasks
- [Days] days from [start milestone or start project] to ship

**Git range:** `feat(XX-XX)` → `feat(YY-YY)`

**What's next:** [Ask user: what's the next goal?]

---
```

</step>

<step name="evolve_project_full_review">

Perform full PROJECT.md evolution review at milestone completion.

**Read all phase summaries in this milestone:**

```bash
cat .planning/phases/*-*/*-SUMMARY.md
```

**Full review checklist:**

1. **"What This Is" accuracy:**
   - Read current description
   - Compare to what was actually built
   - Update if the product has meaningfully changed

2. **Core Value check:**
   - Is the stated core value still the right priority?
   - Did shipping reveal a different core value?
   - Update if the ONE thing has shifted

3. **Requirements audit:**

   **Validated section:**
   - All requirements shipped in this milestone → Add to Validated
   - Format: `- ✓ [Requirement] — v[X.Y]`

   **Out of Scope audit:**
   - Review each item — is the reasoning still valid?
   - Remove items that are no longer relevant
   - Add any requirements invalidated during this milestone

4. **Business context review:**
   - Who It's For — has understanding of audience evolved?
   - Core Problem — still the right framing?
   - How It's Different — new competitors or differentiators?
   - Key User Flows — validated against what users actually do?

5. **Technical Context update:**
   - Current codebase state (LOC, tech stack)
   - User feedback themes (if any)
   - Known issues or technical debt to address

6. **Key Decisions audit:**
   - Extract all decisions from milestone phase summaries
   - Add to Key Decisions table with outcomes where known
   - Mark ✓ Good, ⚠️ Revisit, or — Pending for each

7. **Constraints check:**
   - Any constraints that changed during development?
   - Update as needed

**Update PROJECT.md:**

Make all edits inline. Update "Last updated" footer:

```markdown
---
*Last updated: [date] after v[X.Y] milestone*
```

**Example full evolution (v1.0 → v1.1 prep):**

Before:

```markdown
## What This Is

A real-time collaborative whiteboard for remote teams.

## Core Value

Real-time sync that feels instant.

## Who It's For

Remote teams who need to brainstorm visually during meetings.
Currently using Miro or physical whiteboards.

## Validated

(None yet — ship to validate)

## Out of Scope

- Mobile app — web-first approach
- Video chat — use external tools
```

After v1.0:

```markdown
## What This Is

A real-time collaborative whiteboard for remote teams with instant sync and drawing tools.

## Core Value

Real-time sync that feels instant.

## Who It's For

Remote teams (2-8 people) who brainstorm visually during meetings.
Currently using Miro but frustrated by complexity and latency.

## Validated

- ✓ Canvas drawing tools — v1.0
- ✓ Real-time sync < 500ms — v1.0 (achieved 200ms avg)
- ✓ User authentication — v1.0

## Out of Scope

- Mobile app — web-first approach, PWA works well
- Video chat — use external tools
- Offline mode — real-time is core value

## Technical Context

Shipped v1.0 with 2,400 LOC TypeScript.
Tech stack: Next.js, Supabase, Canvas API.
Initial user testing showed demand for shape tools.
```

**Step complete when:**

- [ ] "What This Is" reviewed and updated if needed
- [ ] Core Value verified as still correct
- [ ] All shipped requirements added to Validated
- [ ] Business context reviewed (Who It's For, Core Problem, How It's Different, Key User Flows)
- [ ] Out of Scope reasoning audited
- [ ] Technical Context updated with current state
- [ ] All milestone decisions added to Key Decisions
- [ ] "Last updated" footer reflects milestone completion

</step>

<step name="archive_milestone">

Extract completed milestone details and create archive file.

**Process:**

1. Create milestone directory and archive file:
   ```bash
   mkdir -p .planning/milestones/v[X.Y]
   ```
   Archive file path: `.planning/milestones/v[X.Y]/ROADMAP.md`

2. Read `~/.claude/mindsystem/templates/milestone-archive.md` template

3. Extract data from current ROADMAP.md:
   - All phases belonging to this milestone (by phase number range)
   - Full phase details (goals, plans, dependencies, status)
   - Phase plan lists with completion checkmarks

4. Extract data from PROJECT.md:
   - Key decisions made during this milestone
   - Requirements that were validated

5. Fill template {{PLACEHOLDERS}}:
   - {{VERSION}} — Milestone version (e.g., "1.0")
   - {{MILESTONE_NAME}} — From ROADMAP.md milestone header
   - {{DATE}} — Today's date
   - {{PHASE_START}} — First phase number in milestone
   - {{PHASE_END}} — Last phase number in milestone
   - {{TOTAL_PLANS}} — Count of all plans in milestone
   - {{MILESTONE_DESCRIPTION}} — From ROADMAP.md overview
   - {{PHASES_SECTION}} — Full phase details extracted
   - {{DECISIONS_FROM_PROJECT}} — Key decisions from PROJECT.md
   - {{ISSUES_RESOLVED_DURING_MILESTONE}} — From summaries

6. Write filled template to `.planning/milestones/v[X.Y]/ROADMAP.md`

7. Delete ROADMAP.md (fresh one created for next milestone):
   ```bash
   rm .planning/ROADMAP.md
   ```

8. Verify archive exists:
   ```bash
   ls .planning/milestones/v[X.Y]/ROADMAP.md
   ```

9. Confirm roadmap archive complete:

   ```
   ✅ v[X.Y] roadmap archived to milestones/v[X.Y]/ROADMAP.md
   ✅ ROADMAP.md deleted (fresh one for next milestone)
   ```

**Note:** Phase directories are moved to `milestones/v[X.Y]/phases/` by the archive_and_cleanup_phases step. After milestone completion, `.planning/phases/` contains only the next milestone's work. Phase numbering continues (v1.0 phases 1-4, v1.1 phases 5-8, etc.).

</step>

<step name="archive_requirements">

Archive requirements and prepare for fresh requirements in next milestone.

**Process:**

1. Read current REQUIREMENTS.md:
   ```bash
   cat .planning/REQUIREMENTS.md
   ```

2. Create archive file: `.planning/milestones/v[X.Y]/REQUIREMENTS.md`

3. Transform requirements for archive:
   - Mark all v1 requirements as `[x]` complete
   - Add outcome notes where relevant (validated, adjusted, dropped)
   - Update traceability table status to "Complete" for all shipped requirements
   - Add "Milestone Summary" section with:
     - Total requirements shipped
     - Any requirements that changed scope during milestone
     - Any requirements dropped and why

4. Write archive file with header:
   ```markdown
   # Requirements Archive: v[X.Y] [Milestone Name]

   **Archived:** [DATE]
   **Status:** ✅ SHIPPED

   This is the archived requirements specification for v[X.Y].
   For current requirements, see `.planning/REQUIREMENTS.md` (created for next milestone).

   ---

   [Full REQUIREMENTS.md content with checkboxes marked complete]

   ---

   ## Milestone Summary

   **Shipped:** [X] of [Y] v1 requirements
   **Adjusted:** [list any requirements that changed during implementation]
   **Dropped:** [list any requirements removed and why]

   ---
   *Archived: [DATE] as part of v[X.Y] milestone completion*
   ```

5. Delete original REQUIREMENTS.md:
   ```bash
   rm .planning/REQUIREMENTS.md
   ```

6. Confirm:
   ```
   ✅ Requirements archived to milestones/v[X.Y]/REQUIREMENTS.md
   ✅ REQUIREMENTS.md deleted (fresh one needed for next milestone)
   ```

**Important:** The next milestone workflow starts with `/ms:create-roadmap` to create a fresh REQUIREMENTS.md. PROJECT.md's Validated section carries the cumulative record across milestones.

</step>

<step name="archive_milestone_files">

Archive optional milestone files (audit, context, research) to the milestone directory:

```bash
~/.claude/mindsystem/scripts/archive-milestone-files.sh v[X.Y]
```

The script moves whichever files exist and reports what was archived. Files that don't exist are skipped silently.

</step>

<step name="archive_and_cleanup_phases">

Consolidate phase summaries, delete raw artifacts, and move phase directories to the milestone archive. This runs after all steps that read summaries (extract_accomplishments, evolve_project_full_review) and after archive_milestone creates the milestone directory.

```bash
~/.claude/mindsystem/scripts/archive-milestone-phases.sh $PHASE_START $PHASE_END v[X.Y]
```

Verify archive:

```bash
ls .planning/milestones/v[X.Y]/PHASE-SUMMARIES.md
ls .planning/milestones/v[X.Y]/phases/
```

Present:

```
✅ Phase summaries consolidated to milestones/v[X.Y]/PHASE-SUMMARIES.md
✅ Raw artifacts deleted from phase directories
✅ Phase directories moved to milestones/v[X.Y]/phases/
✅ .planning/phases/ clean for next milestone
```

Knowledge files in `.planning/knowledge/` persist (they ARE the milestone's knowledge output).

</step>

<step name="update_state">

Update STATE.md to reflect milestone completion.

**Project Reference:**

```markdown
## Project Reference

See: .planning/PROJECT.md (updated [today])

**Core value:** [Current core value from PROJECT.md]
**Current focus:** [Next milestone or "Planning next milestone"]
```

**Current Position:**

```markdown
Phase: [Next phase] of [Total] ([Phase name])
Plan: Not started
Status: Ready to plan
Last activity: [today] — v[X.Y] milestone complete

Progress: [updated progress bar]
```

**Accumulated Context:**

- Clear decisions summary (full log in PROJECT.md)
- Clear resolved blockers
- Keep open blockers for next milestone

</step>

<step name="git_tag">

Create git tag for milestone:

```bash
git tag -a v[X.Y] -m "$(cat <<'EOF'
v[X.Y] [Name]

Delivered: [One sentence]

Key accomplishments:
- [Item 1]
- [Item 2]
- [Item 3]

See .planning/MILESTONES.md for full details.
EOF
)"
```

Confirm: "Tagged: v[X.Y]"

Ask: "Push tag to remote? (y/n)"

If yes:

```bash
git push origin v[X.Y]
```

</step>

<step name="git_commit_milestone">

Commit milestone completion including archive files and deletions.

```bash
# Stage archive directory (covers ROADMAP, REQUIREMENTS, AUDIT, CONTEXT, research)
git add .planning/milestones/v[X.Y]/

# Stage updated files
git add .planning/MILESTONES.md
git add .planning/PROJECT.md
git add .planning/STATE.md

# Stage deletions (raw artifacts cleaned from phase directories, research dir removed)
git add -u .planning/

# Commit with descriptive message
git commit -m "$(cat <<'EOF'
chore: complete v[X.Y] milestone

Archived to milestones/v[X.Y]/:
- ROADMAP.md
- REQUIREMENTS.md
- PHASE-SUMMARIES.md (consolidated from phase directories)
- phases/ (phase directories moved from .planning/phases/)
- MILESTONE-AUDIT.md (if audit was run)
- CONTEXT.md (if milestone context existed)
- research/ (if research existed)

Cleaned:
- Raw phase artifacts deleted (CONTEXT, DESIGN, RESEARCH, SUMMARY, UAT, VERIFICATION, EXECUTION-ORDER)
- Phase directories moved to milestone archive
- Knowledge files persist in .planning/knowledge/

Deleted (fresh for next milestone):
- ROADMAP.md
- REQUIREMENTS.md
- .planning/research/ (archived to milestone)

Updated:
- MILESTONES.md (new entry)
- PROJECT.md (requirements → Validated)
- STATE.md (reset for next milestone)

Tagged: v[X.Y]
EOF
)"
```

Confirm: "Committed: chore: complete v[X.Y] milestone"

</step>

<step name="offer_next">

```
✅ Milestone v[X.Y] [Name] complete

Shipped:
- [N] phases ([M] plans, [P] tasks)
- [One sentence of what shipped]

Archived to milestones/v[X.Y]/:
- ROADMAP.md
- REQUIREMENTS.md
- research/ (if existed)

Summary: .planning/MILESTONES.md
Tag: v[X.Y]

---

## ▶ Next Up

`/ms:new-milestone` — define goals and requirements

<sub>`/clear` first → fresh context window</sub>

---

**Next milestone flow:**
1. `/ms:new-milestone` — discover what to build, update PROJECT.md with goals
2. `/ms:research-project` — (optional) research ecosystem
3. `/ms:create-roadmap` — define requirements and plan how to build it

---
```

</step>

</process>

<success_criteria>

Milestone completion is successful when (ordered by skip risk):

- [ ] PROJECT.md full evolution review completed (What This Is, Core Value, business context, Validated, Key Decisions, Technical Context)
- [ ] All shipped requirements moved to Validated in PROJECT.md
- [ ] Key Decisions updated with outcomes
- [ ] MILESTONES.md entry created with stats and accomplishments
- [ ] Roadmap archive created (milestones/v[X.Y]/ROADMAP.md)
- [ ] Requirements archive created (milestones/v[X.Y]/REQUIREMENTS.md)
- [ ] REQUIREMENTS.md deleted (fresh for next milestone)
- [ ] STATE.md updated with fresh project reference

</success_criteria>
