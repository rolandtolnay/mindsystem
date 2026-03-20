---
name: ms:insert-phase
description: Insert urgent work as decimal phase (e.g., 72.1) between existing phases
argument-hint: <after> <description>
allowed-tools:
  - Read
  - Write
  - Bash
  - AskUserQuestion
---

<objective>
Insert a decimal phase for urgent work discovered mid-milestone that must be completed between existing integer phases, fully specified with goal, success criteria, and requirements.

Uses decimal numbering (72.1, 72.2, etc.) to preserve the logical sequence of planned phases while accommodating urgent insertions. The phase is set up identically to phases created by the roadmapper — downstream commands work without degradation.

Purpose: Handle urgent work discovered during execution without renumbering entire roadmap, with full pipeline support.
</objective>

<execution_context>
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/REQUIREMENTS.md
</execution_context>

<process>

<step name="parse_arguments">
Parse the command arguments:
- First argument: integer phase number to insert after
- Remaining arguments: phase description

Example: `/ms:insert-phase 72 Fix critical auth bug`
→ after = 72
→ description = "Fix critical auth bug"

Validation:

```bash
if [ $# -lt 2 ]; then
  echo "ERROR: Both phase number and description required"
  echo "Usage: /ms:insert-phase <after> <description>"
  echo "Example: /ms:insert-phase 72 Fix critical auth bug"
  exit 1
fi
```

Parse first argument as integer:

```bash
after_phase=$1
shift
description="$*"

# Validate after_phase is an integer
if ! [[ "$after_phase" =~ ^[0-9]+$ ]]; then
  echo "ERROR: Phase number must be an integer"
  exit 1
fi
```

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
Phase insertion requires an active milestone with requirements tracking.
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

<step name="verify_target_phase">
Verify that the target phase exists in the roadmap:

1. Search for "### Phase {after_phase}:" heading
2. If not found:

   ```
   ERROR: Phase {after_phase} not found in roadmap
   Available phases: [list phase numbers]
   ```

   Exit.

3. Verify phase is in current milestone (not completed/archived)
</step>

<step name="find_existing_decimals">
Find existing decimal phases after the target phase:

1. Search for all "### Phase {after_phase}.N:" headings
2. Extract decimal suffixes (e.g., for Phase 72: find 72.1, 72.2, 72.3)
3. Find the highest decimal suffix
4. Calculate next decimal: max + 1

Examples:

- Phase 72 with no decimals → next is 72.1
- Phase 72 with 72.1 → next is 72.2
- Phase 72 with 72.1, 72.2 → next is 72.3

Store as: `decimal_phase="$(printf "%02d" $after_phase).${next_decimal}"`
</step>

<step name="derive_phase_specification">
Read `~/.claude/mindsystem/references/derive-phase-specification.md` and follow its algorithm.

Variables: `{PHASE_ID}` = `{decimal_phase}`, `{PHASE_MARKER}` = `(INSERTED)`.

Input: user's description + project context (PROJECT.md, ROADMAP.md phases, REQUIREMENTS.md categories).
</step>

<step name="generate_slug">
Convert the phase description to a kebab-case slug:

```bash
slug=$(echo "$description" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//;s/-$//')
```

Phase directory name: `{decimal-phase}-{slug}`
Example: `06.1-fix-critical-auth-bug` (phase 6 insertion)
</step>

<step name="create_phase_directory">
Create the phase directory structure:

```bash
phase_dir=".planning/phases/${decimal_phase}-${slug}"
mkdir -p "$phase_dir"
```

Confirm: "Created directory: $phase_dir"
</step>

<step name="update_requirements">
Follow the requirements update procedure in `~/.claude/mindsystem/references/derive-phase-specification.md`.

Use Phase `{decimal_phase}` for traceability table references and footer dating.
</step>

<step name="update_roadmap">
Insert the new phase entry into the roadmap:

**1. Find insertion point:** immediately after Phase {after_phase}'s content (and any existing decimals), before next integer phase heading or "---".

**2. Add phase details:**

Insert full phase entry matching roadmapper format with (INSERTED) marker:

```
### Phase {decimal_phase}: {Name} (INSERTED)
**Goal**: {approved goal}
**Depends on**: Phase {after_phase}
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

**3. Update progress table** — insert row in correct position:
```
| {decimal_phase}. {Name} (INSERTED) | Not started | - |
```

Write updated roadmap back to file.

The "(INSERTED)" marker helps identify decimal phases as urgent insertions.

Preserve all other content exactly (formatting, spacing, other phases).
</step>

<step name="update_project_state">
Update STATE.md to reflect the inserted phase:

1. Read `.planning/STATE.md`
2. Under "## Accumulated Context" → "### Roadmap Evolution" add entry:
   ```
   - Phase {decimal_phase} inserted after Phase {after_phase}: {description} (URGENT)
   ```

If "Roadmap Evolution" section doesn't exist, create it.

Add note about insertion reason if appropriate.
</step>

<step name="completion">
Present completion summary:

```
Phase {decimal_phase} inserted after Phase {after_phase}:
- Goal: {goal}
- Requirements: {REQ-IDs}
- Success criteria: {count}
- Directory: .planning/phases/{decimal-phase}-{slug}/
- Status: Not planned yet
- Marker: (INSERTED) - indicates urgent work

Files updated:
- .planning/ROADMAP.md
- .planning/REQUIREMENTS.md
- .planning/STATE.md
```

Read `~/.claude/mindsystem/references/routing/next-phase-routing.md` and follow its instructions
to present "Next Up" with pre-work context for Phase {decimal_phase}.

After the "Next Up" section, add:
- Review insertion impact: Check if Phase {next_integer} dependencies still make sense
</step>

<step name="update_last_command">
```bash
ms-tools set-last-command "ms:insert-phase $ARGUMENTS"
```
</step>

</process>

<anti_patterns>

- Don't use this for planned work at end of milestone (use /ms:add-phase)
- Don't insert before Phase 1 (decimal 0.1 makes no sense)
- Don't renumber existing phases
- Don't modify the target phase content
- Don't create plans yet (that's /ms:plan-phase)
- Don't commit changes (user decides when to commit)
- Don't write skeletal "[To be planned]" entries — derive a real goal and success criteria
</anti_patterns>

<success_criteria>
Phase insertion is complete when:

- [ ] Specification derived with outcome-focused goal and 2-5 observable success criteria
- [ ] Requirements derived with REQ-IDs and REQUIREMENTS.md updated with traceability mapping
- [ ] Phase directory and roadmap entry created with (INSERTED) marker and correct decimal number
- [ ] Phase inserted after target phase, before next integer phase
- [ ] Roadmap entry matches roadmapper format (Goal, Requirements, Success Criteria, pre-work flags)
- [ ] STATE.md updated with roadmap evolution note
- [ ] User approved specification before writing
- [ ] User informed of next steps and dependency implications
</success_criteria>
