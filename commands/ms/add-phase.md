---
name: ms:add-phase
description: Add phase to end of current milestone in roadmap
argument-hint: <description>
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Add a new integer phase to the end of the current milestone, fully specified with goal, success criteria, and requirements.

The phase is set up identically to phases created by the roadmapper — same ROADMAP.md entry format, same requirements in REQUIREMENTS.md with traceability mapping. Downstream commands (discuss-phase, plan-phase, execute-phase, verify-work) work without degradation.

Purpose: Add discovered work at the end of current milestone with full pipeline support.
</objective>

<execution_context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
</execution_context>

<process>

<step name="parse_arguments">
Parse the command arguments:
- All arguments become the phase description
- Example: `/ms:add-phase Add authentication` → description = "Add authentication"
- Example: `/ms:add-phase Fix critical performance issues` → description = "Fix critical performance issues"

If no arguments provided:

```
ERROR: Phase description required
Usage: /ms:add-phase <description>
Example: /ms:add-phase Add authentication system
```

Exit.
</step>

<step name="load_context">
Load project context:

```bash
if [ -f .planning/ROADMAP.md ]; then
  ROADMAP=".planning/ROADMAP.md"
else
  echo "ERROR: No roadmap found (.planning/ROADMAP.md)"
  exit 1
fi

if [ ! -f .planning/REQUIREMENTS.md ]; then
  echo "ERROR: No REQUIREMENTS.md found"
  exit 1
fi
```

If REQUIREMENTS.md is missing, display:

```
Phase addition requires an active milestone with requirements tracking.
No .planning/REQUIREMENTS.md found.

Instead, consider:
- `/ms:new-milestone` — start a new milestone with requirements
- `/ms:create-roadmap` — if milestone context exists but roadmap wasn't created yet
- `/ms:adhoc "<description>"` — for work that doesn't need milestone tracking
```

Exit command.

Read ROADMAP.md and REQUIREMENTS.md.

From REQUIREMENTS.md, extract:
- Existing REQ-ID categories and their prefixes (e.g., AUTH, SUB, CONTENT)
- Highest REQ-ID number per category (e.g., AUTH-04 → next is AUTH-05)
- Traceability table structure
</step>

<step name="find_current_milestone">
Parse the roadmap to find the current milestone section:

1. Locate the "## Current Milestone:" heading
2. Extract milestone name and version
3. Identify all phases under this milestone (before next "---" separator or next milestone heading)
4. Parse existing phase numbers (including decimals if present)

Example structure:

```
## Current Milestone: Foundation

### Phase 4: Focused Command System
### Phase 5: Path Routing & Validation
### Phase 6: Documentation & Distribution
```

</step>

<step name="calculate_next_phase">
Find the highest integer phase number in the current milestone:

1. Extract all phase numbers from phase headings (### Phase N:)
2. Filter to integer phases only (ignore decimals like 4.1, 4.2)
3. Find the maximum integer value
4. Add 1 to get the next phase number

Example: If phases are 4, 5, 5.1, 6 → next is 7

Format as two-digit: `printf "%02d" $next_phase`
</step>

<step name="derive_phase_specification">
Read `~/.claude/mindsystem/references/derive-phase-specification.md` and follow its algorithm.

Variables: `{PHASE_ID}` = `{N}`, `{PHASE_MARKER}` = (empty).

Input: user's description + project context (PROJECT.md, ROADMAP.md phases, REQUIREMENTS.md categories).
</step>

<step name="generate_slug">
Convert the phase description to a kebab-case slug:

```bash
# Example transformation:
# "Add authentication" → "add-authentication"
# "Fix critical performance issues" → "fix-critical-performance-issues"

slug=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
```

Phase directory name: `{two-digit-phase}-{slug}`
Example: `07-add-authentication`
</step>

<step name="create_phase_directory">
Create the phase directory structure:

```bash
phase_dir=".planning/phases/${phase_num}-${slug}"
mkdir -p "$phase_dir"
```

Confirm: "Created directory: $phase_dir"
</step>

<step name="update_requirements">
Follow the requirements update procedure in `~/.claude/mindsystem/references/derive-phase-specification.md`.

Use Phase `{N}` for traceability table references and footer dating.
</step>

<step name="update_roadmap">
Add the new phase entry to the roadmap:

**1. Update phase checklist** (under `## Phases`):

Find the last `- [ ]` or `- [x]` phase line in the current milestone and append:
```
- [ ] **Phase {N}: {Name}** - {One-line description}
```

**2. Add phase details** (under `## Phase Details`):

Find the insertion point (after last phase in current milestone, before "---" separator or `## Progress`).

Insert full phase entry matching roadmapper format:

```
### Phase {N}: {Name}
**Goal**: {approved goal}
**Depends on**: Phase {N-1}
**Requirements**: {REQ-IDs comma-separated}
**Success Criteria** (what must be TRUE):
  1. {criterion}
  2. {criterion}
  3. {criterion}
**Discuss**: {Likely (reason) | Unlikely (reason)}
**Discuss topics**: {topics} ← only if Likely
**Design**: {Likely (reason) | Unlikely (reason)}
**Design focus**: {focus} ← only if Likely
**Research**: {Likely (reason) | Unlikely (reason)}
**Research topics**: {topics} ← only if Likely
```

**3. Update progress table** — append row:
```
| {N}. {Name} | Not started | - |
```

Write updated roadmap back to file.

Preserve all other content exactly (formatting, spacing, other phases).
</step>

<step name="update_project_state">
Update STATE.md to reflect the new phase:

1. Read `.planning/STATE.md`
2. Under "## Current Position" → "**Next Phase:**" add reference to new phase
3. Under "## Accumulated Context" → "### Roadmap Evolution" add entry:
   ```
   - Phase {N} added: {description}
   ```

If "Roadmap Evolution" section doesn't exist, create it.
</step>

<step name="completion">
Present completion summary:

```
Phase {N} added to current milestone:
- Goal: {goal}
- Requirements: {REQ-IDs}
- Success criteria: {count}
- Directory: .planning/phases/{phase-num}-{slug}/
- Status: Not planned yet

Files updated:
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
```

Read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions
to present "Next Up" with pre-work context for Phase {N}.

After the "Next Up" section, add:
- `/ms:add-phase <description>` — add another phase
</step>

<step name="update_last_command">
```bash
ms-tools set-last-command "ms:add-phase $ARGUMENTS"
```
</step>

</process>

<anti_patterns>

- Don't modify phases outside current milestone
- Don't renumber existing phases
- Don't use decimal numbering (that's /ms:insert-phase)
- Don't create plans yet (that's /ms:plan-phase)
- Don't commit changes (user decides when to commit)
- Don't write skeletal "[To be planned]" entries — derive a real goal and success criteria
</anti_patterns>

<success_criteria>
Phase addition is complete when:

- [ ] Specification derived with outcome-focused goal and 2-5 observable success criteria
- [ ] Requirements derived with REQ-IDs and REQUIREMENTS.md updated with traceability mapping
- [ ] Phase directory and roadmap entry created at end of current milestone with correct sequential number
- [ ] Roadmap entry matches roadmapper format (Goal, Requirements, Success Criteria, pre-work flags)
- [ ] STATE.md updated with roadmap evolution note
- [ ] User approved specification before writing
- [ ] User informed of next steps
</success_criteria>
