---
name: ms:doctor
description: Health check and fix project configuration
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - Task
  - AskUserQuestion
---

<objective>
Run comprehensive health checks on project configuration. Detect and fix structural drift across 6 categories: subsystem vocabulary, milestone directory structure, phase archival, knowledge files, phase summaries, and PLAN cleanup.

Idempotent — safe to run repeatedly.
</objective>

<context>
@.planning/config.json
@.planning/MILESTONES.md
</context>

<process>

<step name="check_planning_dir">
```bash
[ -d .planning ] && echo "EXISTS" || echo "MISSING"
```

If MISSING:

```
No .planning/ directory found.

Run `/ms:new-project` to initialize this project.
```

Exit.
</step>

<step name="ensure_config">
```bash
[ -f .planning/config.json ] && echo "EXISTS" || echo "MISSING"
```

If MISSING, create from template structure:

```json
{
  "subsystems": [],
  "code_review": {
    "adhoc": null,
    "phase": null,
    "milestone": null
  }
}
```

Write to `.planning/config.json`. Log: "Created config.json with empty subsystems."

Proceed to next step.
</step>

<step name="run_scan">
Run the diagnostic scan:

```bash
uv run ~/.claude/mindsystem/scripts/ms-tools.py doctor-scan
```

Capture the full output. Parse each check's Status (PASS/FAIL/SKIP) and detail lines.
</step>

<step name="present_results">
Display results as a markdown table:

```
## Doctor Report

| Check                    | Result | Details                          |
|--------------------------|--------|----------------------------------|
| Subsystem vocabulary     | PASS   | 9 subsystems, all artifacts OK   |
| Milestone directories    | FAIL   | 2 flat files need restructuring  |
| Phase archival           | FAIL   | 8 orphaned phase directories     |
| Knowledge files          | FAIL   | Directory missing                |
| Phase summaries          | FAIL   | 2 milestones missing summaries   |
| PLAN cleanup             | FAIL   | 9 leftover PLAN.md files         |
```

Populate Result and Details from scan output. Use concise detail summaries.

If all PASS → go to `report`.
If any FAIL → go to `confirm_action`.
</step>

<step name="confirm_action">
Use AskUserQuestion:
- header: "Fix issues"
- question: "How would you like to handle the failed checks?"
- options:
  - "Fix all" — apply all fixes in dependency order
  - "Review each" — present each failed check individually for decision
  - "Skip" — leave as-is, report only

If "Skip" → go to `report`.

If "Review each" → use AskUserQuestion for each failed check with its details and options: "Fix" / "Skip". Only run fixes for accepted checks.

Apply fixes in dependency order: fix_subsystems → fix_milestone_dirs → fix_phase_archival → fix_plan_cleanup → fix_knowledge. Skip any fix whose check passed or was skipped by user.
</step>

<step name="fix_subsystems">
**Only if Subsystem Vocabulary failed.**

If subsystems array is empty (State A):

1. Scan all artifacts for existing values:

```bash
uv run ~/.claude/mindsystem/scripts/ms-tools.py scan-artifact-subsystems --values-only
```

2. Read `.planning/PROJECT.md` and `.planning/ROADMAP.md`.

3. Derive 5-12 canonical subsystem identifiers from:
   - Unique values found in artifacts
   - Project domain from PROJECT.md
   - Phase structure from ROADMAP.md

   Rules:
   - Lowercase, single-word or hyphenated (e.g., "auth", "real-time", "ui")
   - Merge synonyms into one canonical value (pick shortest/most common)
   - Cover all existing usage plus obvious gaps
   - Include infrastructure-level subsystems if relevant (api, database, infra, testing)

4. Present the proposed list with merge mappings (e.g., "authentication" -> "auth").

5. Use AskUserQuestion:
   - header: "Subsystems"
   - question: "These subsystems were derived from your project. Look good?"
   - options:
     - "Looks good" — accept and apply
     - "Add/remove some" — iterate on the list
     - "Start over" — re-derive from scratch

6. After confirmation: update `config.json` (subsystems as first field), standardize existing artifact `subsystem:` fields using Edit tool.

If subsystems exist but artifacts have mismatches (State B):

1. Classify each artifact as OK/MISMATCH/MISSING.
2. For MISMATCH: propose closest canonical value.
3. For MISSING: propose based on artifact content/path.
4. Apply fixes using Edit tool.

Commit:

```bash
git add .planning/config.json
git add .planning/phases/*/*-SUMMARY.md 2>/dev/null
git add .planning/adhoc/*-SUMMARY.md 2>/dev/null
git add .planning/debug/*.md 2>/dev/null
git add .planning/debug/resolved/*.md 2>/dev/null
git add .planning/todos/pending/*.md 2>/dev/null
git add .planning/todos/done/*.md 2>/dev/null
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): fix subsystem vocabulary

Standardized subsystem configuration and artifact values.
EOF
)"
```
</step>

<step name="fix_milestone_dirs">
**Only if Milestone Directory Structure failed.**

For each flat file like `milestones/v0.1-ROADMAP.md`:

1. Extract version prefix (e.g., `v0.1`).
2. Create versioned directory if it doesn't exist: `mkdir -p .planning/milestones/v0.1`
3. `git mv` the file, stripping the version prefix from the filename:
   `git mv .planning/milestones/v0.1-ROADMAP.md .planning/milestones/v0.1/ROADMAP.md`

Commit:

```bash
git add .planning/milestones/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): restructure milestone directories

Moved flat milestone files into versioned directories.
EOF
)"
```
</step>

<step name="fix_phase_archival">
**Only if Phase Archival failed.**

Parse MILESTONES.md for completed milestones and their phase ranges (`**Phases completed:** X-Y`).

For each completed milestone with orphaned phases in `.planning/phases/`:

1. Determine the version and phase range from MILESTONES.md.
2. Ensure the milestone directory exists: `mkdir -p .planning/milestones/{version}`
3. Run the archive script:

```bash
uv run ~/.claude/mindsystem/scripts/ms-tools.py archive-milestone-phases <start> <end> <version>
```

This simultaneously:
- Consolidates PHASE-SUMMARIES.md (fixes Phase Summaries check)
- Deletes raw artifacts (CONTEXT, DESIGN, RESEARCH, SUMMARY, UAT, VERIFICATION)
- Moves phase directories to milestone archive

**If MILESTONES.md doesn't have parseable phase ranges:** Use AskUserQuestion to ask the user for the phase range for each milestone.

After archive completes, clean up leftover PLAN files in archived phases (fixes PLAN Cleanup check):

```bash
find .planning/milestones/*/phases/ -name "*-PLAN.md" -delete 2>/dev/null
```

Commit:

```bash
git add .planning/phases/ .planning/milestones/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): archive completed milestone phases

Consolidated summaries, deleted raw artifacts, moved phase directories.
EOF
)"
```
</step>

<step name="fix_plan_cleanup">
**Only if PLAN Cleanup failed AND fix_phase_archival did not already handle it.**

Delete leftover PLAN files in completed phase directories:

```bash
find .planning/milestones/*/phases/ -name "*-PLAN.md" -delete 2>/dev/null
```

For any leftover PLANs in `phases/` belonging to completed milestones (identified by the scan), delete those too.

Commit:

```bash
git add .planning/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): clean up leftover PLAN files

Removed PLAN files from completed phase directories.
EOF
)"
```
</step>

<step name="fix_knowledge">
**Only if Knowledge Files failed.**

Spawn a `general-purpose` subagent (Task tool) to generate knowledge files retroactively. Provide the subagent with:

- Subsystem vocabulary from config.json
- Instructions to read all PHASE-SUMMARIES.md from `milestones/*/PHASE-SUMMARIES.md` AND any remaining SUMMARY files in `phases/`
- The knowledge template at `~/.claude/mindsystem/templates/knowledge.md`
- Instructions to read any existing knowledge files and merge (rewrite semantics — current state, not append)
- Instructions to create `.planning/knowledge/` directory if missing
- Instructions to write `.planning/knowledge/{subsystem}.md` for each missing subsystem

After subagent completes, verify files exist:

```bash
ls .planning/knowledge/*.md
```

Commit:

```bash
git add .planning/knowledge/
```

```bash
git commit -m "$(cat <<'EOF'
chore(doctor): generate knowledge files

Created per-subsystem knowledge files from phase summaries.
EOF
)"
```
</step>

<step name="verify">
Re-run the diagnostic scan:

```bash
uv run ~/.claude/mindsystem/scripts/ms-tools.py doctor-scan
```

All checks should now PASS. If any still fail, report which checks remain and why.
</step>

<step name="report">
Final summary table:

```
## Doctor Report

| Check                    | Result | Details                          |
|--------------------------|--------|----------------------------------|
| Subsystem vocabulary     | PASS   | ...                              |
| Milestone directories    | PASS   | ...                              |
| Phase archival           | PASS   | ...                              |
| Knowledge files          | PASS   | ...                              |
| Phase summaries          | PASS   | ...                              |
| PLAN cleanup             | PASS   | ...                              |

All checks passed.
```

Include counts: checks total, passed, fixed during this run.
</step>

</process>

<success_criteria>
- [ ] Each fix group committed atomically
- [ ] Re-scan verifies all checks pass after fixes
- [ ] User confirms fix strategy before changes (Fix all / Review each / Skip)
- [ ] Fixes applied in dependency order: subsystems → dirs → archival → cleanup → knowledge
- [ ] Results displayed as markdown table before any action
- [ ] All 6 categories reported with PASS/FAIL/SKIP
- [ ] Clean project reports all PASS with no fix prompts
</success_criteria>
