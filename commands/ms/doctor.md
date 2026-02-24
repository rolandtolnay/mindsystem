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
Run health checks on project configuration. Detect and fix structural drift across 8 categories: subsystem vocabulary, milestone directory structure, milestone naming convention, phase archival, knowledge files, phase summaries, PLAN cleanup, and CLI wrappers.

Idempotent.
</objective>

<execution_context>
@~/.claude/mindsystem/workflows/doctor-fixes.md
</execution_context>

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
# ms-tools is on PATH — invoke directly, not as a script path
ms-tools doctor-scan
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
| Milestone naming         | FAIL   | 2 version-prefixed dirs need migration |
| Phase archival           | FAIL   | 8 orphaned phase directories     |
| Knowledge files          | FAIL   | Directory missing                |
| Phase summaries          | FAIL   | 2 milestones missing summaries   |
| PLAN cleanup             | FAIL   | 9 leftover PLAN.md files         |
| CLI wrappers             | FAIL   | ms-tools not on PATH             |
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

Apply fixes in dependency order: fix_subsystems → fix_milestone_dirs → fix_milestone_naming → fix_phase_archival → fix_plan_cleanup → fix_knowledge. Skip any fix whose check passed or was skipped by user.

Phase summaries are resolved by fix_phase_archival. CLI wrappers require manual PATH configuration (no automated fix).
</step>

<step name="apply_fixes">
Execute fix steps from doctor-fixes workflow in dependency order. For "Fix all": run all
applicable steps. For "Review each": run only user-accepted steps. Skip any step whose
check passed.
</step>

<step name="verify">
Re-run the diagnostic scan:

```bash
ms-tools doctor-scan
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
| Milestone naming         | PASS   | ...                              |
| Phase archival           | PASS   | ...                              |
| Knowledge files          | PASS   | ...                              |
| Phase summaries          | PASS   | ...                              |
| PLAN cleanup             | PASS   | ...                              |
| CLI wrappers             | PASS   | ...                              |

All checks passed.
```

Include counts: checks total, passed, fixed during this run.
</step>

</process>

<success_criteria>
- [ ] User confirms fix strategy before changes (Fix all / Review each / Skip)
- [ ] Results displayed as markdown table before any action
- [ ] Re-scan verifies all checks pass after fixes
- [ ] Each fix group committed atomically
- [ ] Fixes applied in dependency order: subsystems → dirs → milestone naming → archival → cleanup → knowledge
- [ ] All 8 categories reported with PASS/FAIL/SKIP
- [ ] Clean project reports all PASS with no fix prompts
</success_criteria>
