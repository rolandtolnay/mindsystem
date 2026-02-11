# TDD Reference for Plan Writers

TDD is about design quality, not coverage metrics. The red-green-refactor cycle forces you to think about behavior before implementation, producing cleaner interfaces and more testable code.

**Principle:** If you can describe the behavior as `expect(fn(input)).toBe(output)` before writing `fn`, TDD improves the result.

**Key insight:** TDD work is fundamentally heavier than standard tasks — it requires 2-3 execution cycles (RED -> GREEN -> REFACTOR), each with file reads, test runs, and potential debugging. TDD features get dedicated plans to ensure full context is available throughout the cycle.

---

## When TDD Improves Quality

**TDD candidates (create a TDD plan):**
- Business logic with defined inputs/outputs
- API endpoints with request/response contracts
- Data transformations, parsing, formatting
- Validation rules and constraints
- Algorithms with testable behavior
- State machines and workflows
- Utility functions with clear specifications

**Skip TDD (use standard plan):**
- UI layout, styling, visual components
- Configuration changes
- Glue code connecting existing components
- One-off scripts and migrations
- Simple CRUD with no business logic
- Exploratory prototyping

**Heuristic:** Can you write `expect(fn(input)).toBe(output)` before writing `fn`?
- Yes: Create a TDD plan
- No: Use standard plan, add tests after if needed

---

## TDD Plan Structure

Each TDD plan implements **one feature** through the full RED-GREEN-REFACTOR cycle. Use the same pure markdown format as all other plans:

```markdown
# Plan NN: Feature name

**Subsystem:** validation | **Type:** tdd

## Context
Why TDD benefits this feature. Clear inputs/outputs that make test-first
design valuable. Reference any prior work.

## Changes

### 1. RED — Write failing tests
**Files:** `src/lib/__tests__/validate-email.test.ts`

Test cases:
- Valid: `user@example.com`, `name+tag@domain.co.uk` -> returns true
- Invalid: `@domain.com`, `user@`, empty string -> returns false
- Edge: very long local part (>64 chars) -> returns false

Import `validateEmail` from `src/lib/validate-email.ts` (does not exist yet).
Run tests — all must fail with import/function error.

### 2. GREEN — Implement minimal validation
**Files:** `src/lib/validate-email.ts`

Export `validateEmail(email: string): boolean`. Use regex matching RFC 5322
simplified pattern. Handle null/undefined input by returning false. No
optimization — just make tests pass.

### 3. REFACTOR — Extract regex constant
**Files:** `src/lib/validate-email.ts`

Extract regex to `EMAIL_REGEX` constant at module level. Add JSDoc with
examples. Run tests — all must still pass. Only commit if changes improve
readability.

## Verification
- `npm test -- --grep "validate-email"` passes all cases
- Import works from other modules without errors

## Must-Haves
- [ ] Valid email addresses return true
- [ ] Invalid email addresses return false
- [ ] Edge cases (length limits, null input) handled correctly
```

**One feature per TDD plan.** If features are trivial enough to batch, they're trivial enough to skip TDD — use a standard plan and add tests after.

---

## Good Tests vs Bad Tests

**Test behavior, not implementation:**
- Good: "returns formatted date string"
- Bad: "calls formatDate helper with correct params"
- Tests should survive refactors

**One concept per test:**
- Good: Separate tests for valid input, empty input, malformed input
- Bad: Single test checking all edge cases with multiple assertions

**Descriptive names:**
- Good: "should reject empty email", "returns null for invalid ID"
- Bad: "test1", "handles error", "works correctly"

**No implementation details:**
- Good: Test public API, observable behavior
- Bad: Mock internals, test private methods, assert on internal state

---

## Context Budget

TDD plans target **~40% context usage** (lower than standard plans' ~50%).

Why lower:
- RED phase: write test, run test, potentially debug why it didn't fail
- GREEN phase: implement, run test, potentially iterate on failures
- REFACTOR phase: modify code, run tests, verify no regressions

Each phase involves reading files, running commands, analyzing output. The back-and-forth is inherently heavier than linear task execution.

Single feature focus ensures full quality throughout the cycle.
