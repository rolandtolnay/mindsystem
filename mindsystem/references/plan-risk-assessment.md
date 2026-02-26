<plan_risk_assessment>
Optional verification step for plan-phase workflow. Calculates risk score from already-loaded context and prompts user to verify or skip.

<purpose>
Provide lightweight risk assessment after plan creation to help users decide whether to run plan verification before execution.

**Key principle:** All information is already in context from earlier workflow steps. No additional file reads or subagent spawns needed for scoring.
</purpose>

<skip_conditions>
Skip risk assessment entirely when:
- Zero plans created (error state)
</skip_conditions>

<risk_factors>

## Factor Weights

| Factor | Max Points | Source |
|--------|-----------|--------|
| Task count per plan (4+) | 15 | Plans just created |
| Total plan count (5+) | 15 | Plans just created |
| External services | 20 | user_setup in frontmatter |
| CONTEXT.md exists | 10 | gather_phase_context step |
| Cross-cutting concerns | 15 | Dependency graph analysis |
| New dependencies | 15 | Task actions |
| Complex domain keywords | 10 | Phase name/description |

**Maximum score:** 100 points

## Detection Logic

**Task count per plan:**
```
max_tasks = max(task_count for each plan)
if max_tasks >= 4:
  score += 15
  factors.append(f"Plan has {max_tasks} tasks")
```

**Total plan count:**
```
plan_count = number of PLAN.md files created
if plan_count >= 5:
  score += 15
  factors.append(f"{plan_count} plans in phase")
```

**External services:**
```
services = extract from user_setup frontmatter
# Common services: Stripe, SendGrid, Twilio, OpenAI, Supabase, Firebase, Auth0, etc.
if services:
  score += min(len(services) * 10, 20)
  factors.append(f"External services: {', '.join(services)}")
```

**CONTEXT.md exists:**
```
if CONTEXT.md was loaded in gather_phase_context:
  score += 10
  factors.append("CONTEXT.md with locked decisions")
```

**Cross-cutting concerns:**
```
# Files that appear in multiple plans' files_modified
shared_files = files appearing in 2+ plans
if shared_files:
  score += min(len(shared_files) * 5, 15)
  factors.append("Cross-cutting concerns detected")
```

**New dependencies:**
```
# Count packages mentioned in task actions: "npm install X", "add X to package.json"
new_deps = packages mentioned in task actions
if new_deps:
  score += min(len(new_deps) * 5, 15)
  factors.append(f"{len(new_deps)} new dependencies")
```

**Complex domain keywords:**
```
complex_domains = ["auth", "authentication", "payment", "billing", "migration",
                   "security", "encryption", "oauth", "webhook", "real-time",
                   "websocket", "distributed", "caching", "queue"]

phase_text = phase name + phase description (lowercase)
if any(keyword in phase_text for keyword in complex_domains):
  score += 10
  factors.append("Complex domain (auth/payments/etc)")
```

</risk_factors>

<thresholds>

| Score | Tier | Recommendation |
|-------|------|----------------|
| 0-39 | skip | "Execute now" listed first |
| 40-69 | optional | "Verify first" listed first |
| 70-100 | verify | "Verify first (recommended)" listed first |

**Threshold rationale:**
- 0-39: Simple phases with few plans, no external services, no locked decisions
- 40-69: Moderate complexity - verification helpful but not critical
- 70-100: High complexity - multiple risk factors compound, verification strongly recommended

</thresholds>

<ask_user_question_formats>

## Skip Tier (0-39)

```
header: "Plan Verification"
question: "Risk Score: {score}/100 — Low risk

Plans look straightforward. Verification optional."
options:
  - label: "Execute now"
    description: "Skip verification, proceed to execution"
  - label: "Verify anyway"
    description: "Run plan checker before execution"
```

## Optional Tier (40-69)

```
header: "Plan Verification"
question: "Risk Score: {score}/100 — Moderate complexity

Top factors:
- {factor_1}
- {factor_2}

Verification recommended but optional."
options:
  - label: "Verify first"
    description: "Run plan checker before execution"
  - label: "Execute now"
    description: "Skip verification, proceed directly"
  - label: "Review plans manually"
    description: "I'll review plans myself first"
```

## Verify Tier (70-100)

```
header: "Plan Verification Recommended"
question: "Risk Score: {score}/100 — Higher complexity

Top factors:
- {factor_1}
- {factor_2}
- {factor_3}

Verification strongly recommended."
options:
  - label: "Verify first (Recommended)"
    description: "Run plan checker before execution"
  - label: "Execute anyway"
    description: "Skip verification despite complexity"
  - label: "Review plans manually"
    description: "I'll review plans myself first"
```

</ask_user_question_formats>

<checker_invocation>

**When user chooses "Verify first":**

Spawn ms-plan-checker subagent:

```
Task(
  subagent_type: "ms-plan-checker"
  description: "Verify phase {PHASE} plans"
  prompt: """
Verify plans for phase {PHASE}.
Phase directory: {PHASE_DIR}

1. Read .planning/ROADMAP.md for phase goal
2. Read all *-PLAN.md files in {PHASE_DIR}
3. Read {PHASE}-CONTEXT.md if exists (for dimension 7)
4. Run all verification dimensions
5. Return PASSED or ISSUES FOUND
"""
)
```

</checker_invocation>

<result_handling>

## If PASSED

Continue to offer_next with verification status:

```markdown
Plans verified - All checks passed

Phase {X} planned: {N} plan(s) in {M} wave(s)

## Wave Structure
...
```

## If ISSUES FOUND

Present issues summary, then prompt:

```
header: "Verification Issues"
question: "{blocker_count} blocker(s), {warning_count} warning(s) found.

{issue_summary}

How would you like to proceed?"
options:
  - label: "Fix issues"
    description: "I'll edit the plans to address issues"
  - label: "Execute anyway"
    description: "Proceed despite issues"
  - label: "Re-verify"
    description: "Run checker again after fixes"
```

**If "Fix issues":** Return to editing - user will make changes and can re-run `/ms:plan-phase` or manually trigger verification.

**If "Execute anyway":** Continue to offer_next with warning note.

**If "Re-verify":** Re-spawn ms-plan-checker after user indicates fixes are complete.

</result_handling>

<manual_review_handling>

**When user chooses "Review plans manually":**

Show plan file paths and wait:

```markdown
## Plans to Review

{list of plan paths}

Review plans, then respond:
- "looks good" or "proceed" → continue to next steps
- "run verification" → spawn ms-plan-checker
- describe changes → I'll help edit plans
```

</manual_review_handling>

</plan_risk_assessment>
