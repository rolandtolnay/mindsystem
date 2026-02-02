---
name: ms:review-design
description: Audit and improve design of already-implemented features using quality-forcing principles
argument-hint: "[phase, file path, feature name, or description]"
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
  - AskUserQuestion
---

<objective>
Review and improve the design of already-implemented features, applying the same quality-forcing principles used in `/ms:design-phase`.

**When to use:**
- Features implemented before Mindsystem was added (no DESIGN.md exists)
- Features where `/ms:design-phase` was skipped
- Periodic design quality audits on existing code
- After receiving user feedback that UI "feels off"

**What this does:**
1. Identifies target code from arguments
2. Analyzes against design quality criteria
3. Presents improvements with benefits and trade-offs
4. Applies user-approved changes
5. Runs platform-specific verification
6. Creates DESIGN-REVIEW.md report

**Not a replacement for:** `/ms:design-phase` — use that BEFORE implementing new features.
</objective>

<context>
**User's review request:**
$ARGUMENTS

**Current git status:**
!`git status --short`
</context>

<process>

## Phase 1: Identify Target Code

### Step 1.1: Parse Arguments

Analyze `$ARGUMENTS` to determine what code to review:

- **Phase number** (e.g., `4`, `04`) → Find phase directory, read SUMMARY.md files for implemented code
- **File path** (e.g., `lib/features/home/home_screen.dart`) → Read and analyze that file
- **Feature/area name** (e.g., `home feature`, `authentication`) → Search for relevant files in that area
- **Description** (e.g., `the code I just wrote`) → Check recent git changes or conversation context
- **Empty or unclear** → Use AskUserQuestion:

```
Question: "What code should I review for design improvements?"
Options:
- "Uncommitted changes" - Review files with uncommitted modifications
- "Specific file" - I'll provide a file path
- "Recent feature work" - Review files from recent commits
- "Mindsystem phase" - Review all code from a specific phase
```

### Step 1.2: Resolve Phase Directory (if phase-based)

```bash
# Find phase directory
PHASE_DIR=$(ls -d .planning/phases/${PHASE_ARG}-* 2>/dev/null | head -1)

# Find SUMMARY files to identify implemented code
ls "$PHASE_DIR"/*-SUMMARY.md 2>/dev/null
```

Parse SUMMARY.md files to extract:
- Files created/modified
- Features implemented
- Components added

### Step 1.3: Gather Target Files

Based on scope:
- Read target file(s)
- For features, also read related files (widgets, providers, models)
- For phases, collect all files mentioned in SUMMARY.md

Store file list for analysis.

## Phase 2: Load Context Chain

### Step 2.1: Mandatory Context

```bash
# Load PROJECT.md for product context
cat .planning/PROJECT.md 2>/dev/null

# Load ROADMAP.md for phase requirements (if phase-based)
grep -A30 "Phase ${PHASE_ARG}:" .planning/ROADMAP.md 2>/dev/null
```

Extract from PROJECT.md:
- What This Is (product type → determines commercial benchmark)
- Core Value (design must serve this)
- Context (target audience)
- Constraints (platform, technical limits)

### Step 2.2: Check for Existing DESIGN.md

```bash
# Check for existing design
ls .planning/phases/${PHASE_ARG}-*/*-DESIGN.md 2>/dev/null
```

**If exists:** Load as baseline for comparison
**If not exists:** Flag for retroactive creation

### Step 2.3: Optional Context

**implement-ui skill (if exists):**
```bash
ls .claude/skills/*implement-ui* 2>/dev/null
```

If exists, load as authoritative source for existing patterns.

**Codebase analysis:**
- Detect platform (Flutter, React, etc.)
- Find existing component/theme files
- Document discovered patterns

## Phase 3: Analyze for Design Improvements

Review target code against these quality dimensions:

### 3.1: Visual Quality

Apply quality-forcing patterns from `ai-driven-ui-design-system.md`:

**Commercial benchmark check:**
> "Does this look like a commercial $50-200 [product type] — intentional decisions, not defaults?"

**Anti-pattern detection:**
- Generic dark gray with blue accents (unless specifically requested)
- Default spacing with no intentional rhythm
- Controls that look like styled HTML inputs
- Typography using only system fonts without spacing compensation
- Elements that appear positioned without thought

**Check for:**
- Color palette character (distinctive vs generic)
- Intentional spacing (consistent scale vs arbitrary)
- Visual hierarchy (size/weight/contrast differentiation)
- Refined controls (proper states, sizing, polish)

### 3.2: UX Flows

**Check for:**
- Complete user journeys (entry → action → feedback → completion)
- Loading states (skeleton, spinner, or progressive)
- Error states (clear messages, recovery path)
- Empty states (helpful guidance when no data)
- Edge cases (offline, timeout, validation)

### 3.3: Platform Compliance

**Flutter/Mobile:**
- Touch targets ≥ 48dp (Android) / 44pt (iOS)
- Safe area insets respected
- Text sizes ≥ 16sp for body text
- Contrast ratios meet WCAG AA (4.5:1 body, 3:1 large)

**Web:**
- Touch targets ≥ 44px for interactive elements
- Keyboard navigation functional
- Focus states visible
- Responsive breakpoints defined

### 3.4: Code Organization

**Flutter-specific (from simplify-flutter patterns):**
- Large `build()` methods → extract to local variables or builder methods
- Complex subtrees → separate widget files
- Scattered boolean flags → sealed class variants
- Manual try-catch → `AsyncValue.guard()`
- Mutation patterns → immutable methods

**General:**
- Consistent naming conventions
- Related logic grouped together
- Clear separation of concerns

### 3.5: Pattern Alignment

If implement-ui skill or codebase patterns exist:
- Check for consistent color usage
- Check for consistent component patterns
- Check for consistent spacing scale
- Identify deviations that should be aligned

## Phase 4: Create Retroactive DESIGN.md (If Missing)

**If no existing DESIGN.md:**

Document current implementation patterns:

```bash
mkdir -p "$PHASE_DIR"
```

Create `{phase}-DESIGN.md` following the standard template:

1. **Visual Identity** — Extract philosophy from implemented code
2. **Screen Layouts** — Create ASCII wireframes from actual screens
3. **Component Specifications** — Document existing component patterns
4. **UX Flows** — Map current user journeys
5. **Design System Decisions** — Extract colors, typography, spacing with rationale
6. **Platform-Specific Notes** — Document current responsive/platform handling
7. **Verification Criteria** — Define observable behaviors

Write to: `.planning/phases/{phase}-{slug}/{phase}-DESIGN.md`

## Phase 5: Present Improvements

For each identified improvement, document:

### Improvement Format

```markdown
### [Category]: [Brief Description]

**Current state:**
[What exists now]

**Proposed change:**
[What should change]

**Benefits:**
- [Benefit 1]
- [Benefit 2]

**Trade-offs:**
- [Any functionality lost or changed]
- [Migration effort if significant]
- [Risk factors]

**Affected files:**
- [file1.dart]
- [file2.dart]

**Effort:** [low | medium | high]
```

### Categories

Group improvements by:
1. **Visual Quality** — Color, spacing, typography, hierarchy
2. **UX Completeness** — States, flows, error handling
3. **Platform Compliance** — Touch targets, accessibility
4. **Code Organization** — Widget extraction, pattern consistency
5. **Pattern Alignment** — Consistency with existing design system

### Present to User

Display all improvements with summary:

```markdown
## Design Review: [Scope]

Found **N improvements** across M files.

### Summary

| Category | Count | Effort |
|----------|-------|--------|
| Visual Quality | X | [avg effort] |
| UX Completeness | X | [avg effort] |
| Platform Compliance | X | [avg effort] |
| Code Organization | X | [avg effort] |
| Pattern Alignment | X | [avg effort] |

### Improvements

[List all improvements with full details]
```

### User Selection

Use AskUserQuestion to confirm scope:

```
Question: "Which improvements should I apply?"
Options:
- "All improvements" - Apply everything identified
- "Visual + UX only" - Focus on user-facing changes
- "Platform compliance only" - Fix accessibility/sizing issues
- "Let me select" - I'll specify which ones
```

If "Let me select": Present numbered list, ask for comma-separated numbers.

## Phase 6: Apply Approved Changes

For each approved improvement:

1. **Read current file state**
2. **Apply the change** using Edit tool
3. **Log what was changed** for summary

**Apply principles:**
- One logical change at a time
- Preserve all public APIs
- Maintain existing test coverage expectations
- Don't introduce new dependencies without flagging

## Phase 7: Run Verification

### Step 7.1: Detect Platform

```bash
# Flutter
if [ -f "pubspec.yaml" ]; then
  echo "Platform: Flutter"
fi

# Web (Node/npm)
if [ -f "package.json" ]; then
  echo "Platform: Web"
fi
```

### Step 7.2: Run Platform-Specific Checks

**Flutter:**
```bash
flutter analyze
flutter test
```

**Web (React/Next/etc.):**
```bash
npm run lint 2>/dev/null || npx eslint . 2>/dev/null
npm test 2>/dev/null || echo "No test script"
```

### Step 7.3: Handle Failures

If verification fails:
1. Identify which change caused the failure
2. Offer to revert that specific change
3. Re-run verification

## Phase 8: Write Design Review Report

Write to: `.planning/phases/{phase}-{slug}/{phase}-DESIGN-REVIEW.md`

```markdown
---
status: complete
phase: XX-name
reviewed: [ISO timestamp]
scope: [files/features reviewed]
---

# Design Review: Phase [X] - [Name]

**Reviewed:** [date]
**Scope:** [what was reviewed]
**Platform:** [detected platform]

## Review Summary

| Category | Found | Applied | Skipped |
|----------|-------|---------|---------|
| Visual Quality | X | X | X |
| UX Completeness | X | X | X |
| Platform Compliance | X | X | X |
| Code Organization | X | X | X |
| Pattern Alignment | X | X | X |

**Total:** X improvements identified, Y applied, Z skipped

## Changes Applied

### 1. [Category]: [Description]

**File:** `path/to/file`
**Change:** [what was changed]
**Rationale:** [why this improves design]

### 2. [Next change...]

## Improvements Skipped

[If any were skipped by user choice]

### 1. [Category]: [Description]

**Reason skipped:** [user's reason or "Not selected"]

## Verification Results

- **flutter analyze:** [pass/fail]
- **flutter test:** [pass/fail]

[If failures, document what was reverted]

## Remaining Recommendations

[Any improvements that couldn't be auto-applied or need manual attention]

## Retroactive Documentation

[If DESIGN.md was created]
- Created: `.planning/phases/{phase}-{slug}/{phase}-DESIGN.md`
- Documents current implementation patterns for future reference

---

*Review completed: [timestamp]*
```

## Phase 9: Present Results

```markdown
## Design Review Complete

**Scope:** [what was reviewed]
**Improvements:** X applied, Y skipped

### Verification
- flutter analyze: [pass/fail]
- flutter test: [pass/fail]

### Files Modified
- [list of files changed]

### Report
`.planning/phases/{phase}-{slug}/{phase}-DESIGN-REVIEW.md`

---

## Next Steps

- Review changes in editor
- Run app to verify visual changes
- Commit when satisfied: `git add . && git commit -m "design: apply review improvements"`
```

## Phase 10: Update Last Command

Update `.planning/STATE.md` Last Command field:
- Find line starting with `Last Command:` in Current Position section
- Replace with: `Last Command: ms:review-design $ARGUMENTS | YYYY-MM-DD HH:MM`
- If line doesn't exist, add it after `Status:` line

</process>

<quality_forcing>
Apply these patterns throughout the review:

**Commercial Benchmark:**
> "This must look like a commercial $50-200 [product type] — intentional decisions, not defaults."

**Pre-emptive Criticism:**
> "Assume someone will say 'This looks like generic AI output.' Does the current design prove them wrong?"

**Accountability Check:**
> "Could a professional designer look at this and say it's skilled work?"

**Explicit Anti-Patterns:**
- Generic dark gray + blue accents
- Default spacing with no rhythm
- Controls that look like styled HTML inputs
- Same-sized everything (no hierarchy)
- Centered everything (lazy layout)
</quality_forcing>

<success_criteria>
- [ ] Target code scope clarified (via arguments or AskUserQuestion)
- [ ] Context chain loaded (PROJECT.md, DESIGN.md if exists, implement-ui skill)
- [ ] Code analyzed across all quality dimensions
- [ ] Retroactive DESIGN.md created if missing
- [ ] Improvements presented with benefits AND trade-offs
- [ ] User selected which improvements to apply
- [ ] Approved changes applied to code
- [ ] Platform-specific verification run (analyze/test)
- [ ] Failures handled (revert problematic changes)
- [ ] DESIGN-REVIEW.md report written to phase directory
- [ ] Clear summary provided with next steps
</success_criteria>
