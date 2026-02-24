---
name: ms:audit-milestone
description: Audit milestone completion against original intent before archiving
argument-hint: "[name]"
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash
  - Task
  - Write
---

<objective>
Verify milestone achieved its definition of done. Check requirements coverage, cross-phase integration, and end-to-end flows.

**This command IS the orchestrator.** Reads existing VERIFICATION.md files (phases already verified during execute-phase), generates/updates `.planning/TECH-DEBT.md` as single source of truth for tech debt, then spawns integration checker for cross-phase wiring.
</objective>

<execution_context>
@~/.claude/mindsystem/references/principles.md
</execution_context>

<context>
Milestone: $ARGUMENTS (optional — defaults to current milestone from PROJECT.md)

**Original Intent:**
@.planning/PROJECT.md
@.planning/REQUIREMENTS.md

**Planned Work:**
@.planning/ROADMAP.md
@.planning/config.json (if exists)

**Completed Work:**
Glob: .planning/phases/*/*-SUMMARY.md
Glob: .planning/phases/*/*-VERIFICATION.md

**Tech Debt:**
@.planning/TECH-DEBT.md (if exists)
</context>

<process>

## 1. Determine Milestone Scope

```bash
# Get phases in milestone
ls -d .planning/phases/*/ | sort -V
```

- Parse version from arguments or detect current from ROADMAP.md
- Identify all phase directories in scope
- Extract milestone definition of done from ROADMAP.md
- Extract requirements mapped to this milestone from REQUIREMENTS.md

## 2. Read All Phase Verifications

For each phase directory, read the VERIFICATION.md:

```bash
cat .planning/phases/01-*/*-VERIFICATION.md
cat .planning/phases/02-*/*-VERIFICATION.md
# etc.
```

From each VERIFICATION.md, extract:
- **Status:** passed | gaps_found
- **Critical gaps:** (if any — these are blockers)
- **Non-critical gaps:** tech debt, deferred items, warnings
- **Anti-patterns found:** TODOs, stubs, placeholders
- **Requirements coverage:** which requirements satisfied/blocked

If a phase is missing VERIFICATION.md, flag it as "unverified phase" — this is a blocker.

## 2.5. Read UAT Files and Aggregate Assumptions

```bash
# Find all UAT files
find .planning/phases -name "*-UAT.md" -type f 2>/dev/null
```

For each UAT file, extract:
- **Assumptions section:** Tests skipped because required state couldn't be mocked

Aggregate assumptions by phase:
```yaml
assumptions:
  count: [N]
  by_phase:
    - phase: 04-comments
      items:
        - name: "Error state display"
          expected: "Shows error message when API fails"
          reason: "Can't mock API error responses"
    - phase: 05-auth
      items:
        - name: "Session timeout"
          expected: "User redirected to login after 30min"
          reason: "Can't manipulate time in tests"
```

## 3. Spawn Integration Checker

With phase context collected:

```
Task(
  prompt="Check cross-phase integration and E2E flows.

Phases: {phase_dirs}
Phase exports: {from SUMMARYs}
API routes: {routes created}

Verify cross-phase wiring and E2E user flows.",
  subagent_type="ms-integration-checker"
)
```

## 4. Collect Results

Combine:
- Phase-level gaps and tech debt (from step 2)
- Integration checker's report (wiring gaps, broken flows)

## 5. Check Requirements Coverage

For each requirement in REQUIREMENTS.md mapped to this milestone:
- Find owning phase
- Check phase verification status
- Determine: satisfied | partial | unsatisfied

## 6. Aggregate into MILESTONE-AUDIT.md

Create `.planning/MILESTONE-AUDIT.md` with:

```yaml
---
milestone: {name}
audited: {timestamp}
status: passed | gaps_found | tech_debt
scores:
  requirements: N/M
  phases: N/M
  integration: N/M
  flows: N/M
gaps:  # Critical blockers
  requirements: [...]
  integration: [...]
  flows: [...]
tech_debt: see .planning/TECH-DEBT.md
assumptions:  # Tests skipped during UAT
  count: [N]
  by_phase:
    - phase: 04-comments
      items:
        - name: "Error state display"
          expected: "Shows error message when API fails"
---
```

Plus full markdown report with tables for requirements, phases, integration, and assumptions. Tech debt tracked separately in `.planning/TECH-DEBT.md`.

**Assumptions section in markdown report:**

```markdown
## Untested Assumptions

{N} tests were skipped because required states couldn't be mocked:

| Phase | Test | Expected Behavior | Reason |
|-------|------|-------------------|--------|
| 04-comments | Error state display | Shows error message when API fails | Can't mock API errors |
| 04-comments | Empty state | Shows placeholder when no comments | Can't clear test data |
| 05-auth | Session timeout | Redirects to login after 30min | Can't manipulate time |

**Consider:** Plan test infrastructure work in next milestone to verify these assumptions.
```

**Status values:**
- `passed` — all requirements met, no critical gaps, minimal tech debt
- `gaps_found` — critical blockers exist
- `tech_debt` — no blockers but accumulated deferred items need review

## 7. Present Results

Route by status (see `<offer_next>`).

## 8. Code Review (Milestone)

Read code review agent from config:

```bash
CODE_REVIEW=$(cat .planning/config.json 2>/dev/null | jq -r '.code_review.milestone // empty')
```

**If CODE_REVIEW = "skip":**
Report: "Milestone code review skipped (config: skip)"
Proceed to next steps.

**If CODE_REVIEW = empty/null:**
Report: "No milestone reviewer configured. Run `/ms:config` to set one."
Skip code review step (proceed to next steps).

### Step 8.1: Get Changed Files

```bash
# Find first commit in milestone (first phase commit)
FIRST_PHASE=$(ls -d .planning/phases/*/ | sort -V | head -1 | xargs basename | cut -d- -f1)
FIRST_COMMIT=$(git log --oneline --grep="(${FIRST_PHASE}-" --format="%H" | tail -1)

# Get all implementation files changed since first commit
CHANGED_FILES=$(git diff --name-only ${FIRST_COMMIT}^..HEAD | grep -E '\.(dart|ts|tsx|js|jsx|swift|kt|py|go|rs)$')
```

### Step 8.2: Determine Agent Mode

```bash
# Read agent mode from frontmatter
AGENT_MODE=$(grep -A10 '^---' ~/.claude/agents/${CODE_REVIEW}.md | grep 'mode:' | awk '{print $2}')
```

---

### Path A: Analysis-Only Reviewers (mode: analyze-only)

For agents with `mode: analyze-only` (e.g., a report-only reviewer):

**A1. Spawn reviewer with read-only tools:**

```
Task(
  prompt="
  <objective>
  Analyze code from milestone {name} for structural issues.
  Report findings only — do NOT make changes.
  </objective>

  <scope>
  Files to analyze:
  {CHANGED_FILES}
  </scope>

  <output>
  Provide findings report with YAML summary block for parsing.
  </output>
  ",
  subagent_type="{CODE_REVIEW}"
)
```

**A2. Parse YAML findings from output:**

Extract the `code_review:` YAML block from the reviewer's response.

**A3. Add findings to MILESTONE-AUDIT.md:**

Append to the YAML frontmatter:

```yaml
code_review:
  agent: {CODE_REVIEW}
  files_analyzed: {N}
  findings_by_impact:
    high: {X}
    medium: {Y}
    low: {Z}
  findings: [...]
```

Add markdown section to report body:

```markdown
## Code Review Findings

**Agent:** {CODE_REVIEW}
**Files analyzed:** {N}

{Include full findings report from reviewer}
```

Code review findings flow into `.planning/TECH-DEBT.md` via Step 8.5 — do NOT add them to `tech_debt` YAML.

**A4. Present binary decision:**

```markdown
## Code Review Complete

**Findings:** {total} ({high} high, {medium} medium, {low} low)

### Options

**A. Create quality phase** — Add phase to address findings before completing milestone

**B. Accept as tech debt** — Document findings, proceed to complete milestone

---

Which would you like to do?
```

Use AskUserQuestion with options A and B.

**A5. Handle decision:**

**If user chooses "Create quality phase":**

1. Determine next phase number (append at end of current phases)
2. Create phase directory: `.planning/phases/{NN}-code-quality/`
3. Update ROADMAP.md with new phase:

```markdown
### Phase {N}: Code Quality (Generated)
**Goal:** Address structural improvements from milestone code review
**Scope:** High and Medium items from .planning/TECH-DEBT.md

Plans:
- [ ] {N}-01: High impact structural fixes
```

4. Report:
```markdown
## Quality Phase Created

**Phase {N}:** `.planning/phases/{NN}-code-quality/`
**Scope source:** `.planning/TECH-DEBT.md`

---

## ▶ Next Up

`/ms:plan-phase {N}` — plan the quality phase

<sub>`/clear` first → fresh context window</sub>
```

**If user chooses "Accept as tech debt":**

Findings are already tracked in `.planning/TECH-DEBT.md` via Step 8.5. Continue to offer_next section.

---

### Path B: Simplifier Agents (default)

For agents without `mode: analyze-only` (e.g., `ms-code-simplifier`):

**B1. Spawn code review agent:**

```
Task(
  prompt="
  <objective>
  Review code from milestone {name}.
  Focus on architectural patterns, cross-phase consistency, and structural improvements.
  Preserve all functionality. Make changes that improve clarity and maintainability.
  </objective>

  <scope>
  Files to analyze:
  {CHANGED_FILES}
  </scope>

  <output>
  After review, run static analysis and tests.
  Report what was improved and verification results.
  </output>
  ",
  subagent_type="{CODE_REVIEW}"
)
```

**B2. Commit if changes made:**

```bash
git add [modified files]
git commit -m "$(cat <<'EOF'
refactor(milestone): code review improvements

Reviewer: {agent_type}
Files reviewed: {count}
EOF
)"
```

Report: "Milestone code review complete."

## 8.5. Generate/Update TECH-DEBT.md

After code review (all sources now available), generate or update `.planning/TECH-DEBT.md`:

1. **Read existing** `.planning/TECH-DEBT.md` (if exists) — parse active items and dismissed list, note highest `TD-{N}` ID
2. **Read template** from `@~/.claude/mindsystem/templates/tech-debt.md`
3. **Collect tech debt** from all sources with severity mapping:
   - Integration checker bugs → **Critical**
   - Unfixed UAT issues (result: `issue`, fix_status ≠ `verified`) → **Critical** (blocker) / **High** (major) / **Medium** (minor) / **Low** (cosmetic)
   - Code review findings → pass through reviewer severity (**High** / **Medium** / **Low**)
   - Phase VERIFICATION.md anti-patterns → **Medium** or **Low** (blockers go to `gaps`, not tech debt)
   - Non-critical gaps from phase verifications → **Medium**
4. **De-duplicate** against existing active items AND dismissed items (match by location + description similarity)
5. **Assign `TD-{N}` IDs** continuing from highest existing ID
6. **Write/update** `.planning/TECH-DEBT.md` — group items under `## Critical`, `## High`, `## Medium`, `## Low` sections per template. Omit empty sections.

## 9. Commit Audit Report

```bash
git add .planning/MILESTONE-AUDIT.md .planning/TECH-DEBT.md
git commit -m "$(cat <<'EOF'
docs(milestone): complete {name} audit

Status: {status}
Scores: Requirements {N}/{M} | Phases {N}/{M} | Integration {N}/{M} | Flows {N}/{M}
EOF
)"
```

</process>

<offer_next>
Read `~/.claude/mindsystem/references/routing/audit-result-routing.md` and follow its instructions to present next steps based on the audit status (passed, gaps_found, or tech_debt).
</offer_next>

<success_criteria>
- [ ] Milestone scope identified
- [ ] All phase VERIFICATION.md files read
- [ ] All phase UAT.md files read for assumptions
- [ ] Tech debt collected into .planning/TECH-DEBT.md (de-duplicated, TD-{N} IDs assigned)
- [ ] Assumptions aggregated by phase
- [ ] Integration checker spawned for cross-phase wiring
- [ ] MILESTONE-AUDIT.md created with assumptions section
- [ ] Code review completed (or skipped if config says "skip")
- [ ] If analyze-only reviewer: YAML findings parsed and added to report
- [ ] If analyze-only reviewer: Binary decision presented (quality phase vs tech debt)
- [ ] If quality phase chosen: Phase directory created, ROADMAP updated with TECH-DEBT.md scope
- [ ] MILESTONE-AUDIT.md and TECH-DEBT.md committed to git
- [ ] Results presented with actionable next steps
</success_criteria>
