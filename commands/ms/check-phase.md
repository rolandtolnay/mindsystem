---
name: ms:check-phase
description: Verify phase plans before execution (optional quality gate)
arguments: phase
allowed-tools:
  - Read
  - Bash
  - Glob
  - Grep
  - Task
---

<objective>
On-demand plan verification. Use when a plan seems large or complex and you want a structured review before executing.

This spawns ms-plan-checker to analyze your PLAN.md files against the phase goal.
</objective>

<what_it_checks>
1. **Requirement Coverage** — Does every phase requirement have tasks addressing it?
2. **Task Completeness** — Does every change have Files, implementation details, and verification?
3. **Dependency Correctness** — Are plan dependencies valid and acyclic?
4. **Key Links Planned** — Are artifacts wired together, not just created in isolation?
5. **Scope Sanity** — Will plans complete within context budget (target 25-45%)?
6. **Verification Derivation** — Are Must-Haves user-observable, not implementation-focused?
7. **Context Compliance** — Do plans honor decisions from CONTEXT.md?
</what_it_checks>

<process>

<step name="validate_phase">
Phase number from $ARGUMENTS (required).

```bash
PHASE=$ARGUMENTS
PADDED=$(printf "%02d" $PHASE 2>/dev/null || echo "$PHASE")
PHASE_DIR=$(ls -d .planning/phases/${PADDED}-* .planning/phases/${PHASE}-* 2>/dev/null | head -1)

if [ -z "$PHASE_DIR" ]; then
  echo "Error: Phase $PHASE not found in .planning/phases/"
  exit 1
fi

echo "Phase directory: $PHASE_DIR"
ls "$PHASE_DIR"/*-PLAN.md 2>/dev/null
```

If no PLAN.md files found, remind user to run `/ms:plan-phase` first.
</step>

<step name="spawn_checker">
Spawn the plan checker agent:

```
Task(
  subagent_type="ms-plan-checker",
  prompt="""
Verify plans for phase $ARGUMENTS.

1. Read .planning/ROADMAP.md to get the phase goal
2. Read all *-PLAN.md files in the phase directory
3. Read CONTEXT.md if it exists in the phase directory
4. Run all 7 verification dimensions (dimension 7 only if CONTEXT.md exists)
5. Return structured result

Phase directory: $PHASE_DIR
""",
  description="Verify phase $ARGUMENTS plans"
)
```
</step>

<step name="present_results">
Present the checker's findings clearly.

**Format for VERIFICATION PASSED:**

```
## Plan Verification: PASSED

Phase: [name] | Plans: [count] | Tasks: [total count]

All checks passed.

Ready to execute: `/ms:execute-phase $ARGUMENTS`
```

**Format for ISSUES FOUND:**

```
## Plan Verification: ISSUES FOUND

Phase: [name] | Plans: [count] | Issues: [X blockers, Y warnings]

### Blockers (must fix)

1. **[dimension]** [description]
   Plan: [which plan] | Fix: [specific fix hint]

### Warnings (should fix)

1. **[dimension]** [description]
   Fix: [hint]

---

Options:
- Fix the issues and run `/ms:check-phase $ARGUMENTS` again
- Proceed anyway: `/ms:execute-phase $ARGUMENTS` (not recommended if blockers exist)
```
</step>

</process>

<examples>
**Check before executing a complex phase:**
```
/ms:check-phase 5
```

**Typical workflow:**
```
/ms:plan-phase 5      # Interactive planning in main context
# ... review and iterate ...
/ms:check-phase 5      # Optional verification for complex plans
/ms:execute-phase 5   # Execute
```
</examples>

<success_criteria>
- Blockers and warnings presented distinctly — blockers have plan name and fix hint
- Output includes actionable next command (`/ms:execute-phase` or `/ms:check-phase` rerun)
- Checker agent spawned with correct phase directory path
</success_criteria>
