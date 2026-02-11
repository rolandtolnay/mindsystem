<tdd_execution>

## RED-GREEN-REFACTOR Cycle

Lazy-loaded by executor when plan metadata says `**Type:** tdd`.

### RED — Write failing test

1. Create test file following project conventions
2. Write test describing expected behavior (from plan's behavior specification)
3. Run test — MUST fail (if passes, feature exists or test is wrong — investigate)
4. Commit: `test({phase}-{plan}): add failing test for [feature]`

### GREEN — Implement to pass

1. Write minimal code to make test pass — no cleverness, no optimization
2. Run test — MUST pass
3. Commit: `feat({phase}-{plan}): implement [feature]`

### REFACTOR (if needed)

1. Clean up implementation if obvious improvements exist
2. Run tests — MUST still pass
3. Commit only if changes made: `refactor({phase}-{plan}): clean up [feature]`

Result: Each TDD plan produces 2-3 atomic commits (test/feat/refactor).

---

## Test Framework Setup

When no test framework is configured, set it up as part of the RED phase:

| Project | Framework | Install |
|---------|-----------|---------|
| Node.js | Jest | `npm install -D jest @types/jest ts-jest` |
| Node.js (Vite) | Vitest | `npm install -D vitest` |
| Python | pytest | `pip install pytest` |
| Go | testing | Built-in |
| Rust | cargo test | Built-in |
| Flutter/Dart | flutter_test | Built-in |

Detect project type from package.json / requirements.txt / go.mod / pubspec.yaml. Create config if needed. Verify with empty test run.

---

## Commit Pattern

TDD plans use dedicated commit types per phase:

```
test(08-02): add failing test for email validation
feat(08-02): implement email validation
refactor(08-02): extract regex to constant  # optional
```

Comparison: Standard plans produce 1 commit per task. TDD plans produce 2-3 commits for single feature.

---

## Error Handling

| Situation | Action |
|-----------|--------|
| Test doesn't fail in RED | Feature may exist or test is wrong — investigate before proceeding |
| Test doesn't pass in GREEN | Debug implementation, keep iterating until green |
| Tests fail in REFACTOR | Undo refactor — commit was premature, refactor in smaller steps |
| Unrelated tests break | Stop and investigate — may indicate coupling issue |

</tdd_execution>
