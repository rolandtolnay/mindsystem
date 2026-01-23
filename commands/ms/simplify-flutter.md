---
name: gsd:simplify-flutter
description: Simplify and refine Flutter/Dart code for clarity, consistency, and maintainability while preserving all functionality
argument-hint: [file path, feature name, or description of what to simplify]
---

<objective>
Simplify Flutter/Dart code to improve clarity, consistency, and maintainability while preserving exact functionality.

You are an expert code simplification specialist. Your expertise lies in making code easier to read, understand, and maintain without changing what it does. You prioritize readable, explicit code over overly compact solutions.

**Core principle:** Simplification means making code easier to reason about—not making it shorter at the cost of clarity.
</objective>

<context>
**User's simplification request:**
$ARGUMENTS

**Current git status:**
!`git status --short`
</context>

<process>

## Phase 1: Identify Target Code

### Step 1.1: Parse Arguments

Analyze `$ARGUMENTS` to determine what code to simplify:

- **File path provided** (e.g., `lib/features/home/home_screen.dart`) → Read and analyze that file
- **Feature/area named** (e.g., `home feature`, `authentication`) → Search for relevant files in that area
- **Description provided** (e.g., `the code I just wrote`) → Check recent git changes or conversation context
- **Empty or unclear** → Use AskUserQuestion:

```
Question: "What Flutter code should I simplify?"
Options:
- "Uncommitted changes" - Simplify files with uncommitted modifications
- "Specific file" - I'll provide a file path
- "Recent feature work" - Simplify files related to recent feature development
```

### Step 1.2: Gather Code

Based on the identified scope:
- Read the target file(s)
- For features, also read related files (widgets, providers, domain models)
- Understand the existing patterns and structure before making changes

## Phase 2: Analyze for Simplification Opportunities

Review the code looking for opportunities to improve clarity without changing behavior.

### What to Simplify

**Complexity reduction:**
- Deeply nested widget trees that could be extracted
- Complex conditionals that could use switch expressions or early returns
- Redundant null checks or unnecessary defensive code
- Overly clever one-liners that sacrifice readability

**Consistency improvements:**
- Inconsistent naming conventions
- Mixed patterns for similar operations
- Scattered logic that belongs together

**Clarity enhancements:**
- Unclear variable or method names
- Missing or misleading structure
- Business logic hidden in UI code that should be in domain/providers

### What NOT to Simplify

**Preserve these:**
- Helpful abstractions that improve organization
- Clear, intentional patterns even if verbose
- Code that would become harder to debug if condensed
- Working error handling and edge case coverage

**Avoid these anti-patterns:**
- Nested ternaries (prefer switch/if-else chains)
- Dense one-liners that require mental unpacking
- Combining unrelated concerns to reduce line count
- Removing comments that explain non-obvious "why"

### Flutter-Specific Guidance

**Widget Structure:**
- Large `build()` methods → extract into local variables (unconditional) or builder methods (conditional)
- Complex subtrees → separate widget files (no private widgets in same file)
- Keep build() order: providers → hooks → derived values → widget variables

**State & Providers:**
- Scattered boolean flags → sealed class variants with switch expressions
- Manual try-catch in providers → `AsyncValue.guard()` with centralized error handling
- Multiple loading states → single-action providers with derived `isLoading`
- Check `ref.mounted` after async operations

**Collections & Data:**
- Mutation patterns → immutable methods (`.sorted()`, `.where()`, etc.)
- Null-unsafe access → `firstWhereOrNull` with fallbacks
- Repeated enum switches → computed properties on the enum itself
- Presentation logic in widgets → domain extensions

**Code Organization:**
- Deep folder nesting → flat feature directories
- Barrel files that only re-export → direct imports
- Business rules scattered in UI → entity computed properties

## Phase 3: Apply Simplifications

For each identified opportunity:

1. **Verify preservation** - Confirm the change won't alter behavior
2. **Make the edit** - Apply the simplification
3. **Keep scope tight** - Only change what genuinely improves the code

**Edit principles:**
- One logical change at a time
- Preserve all public APIs
- Maintain existing test coverage expectations
- Don't introduce new dependencies

## Phase 4: Verify No Regressions

After completing simplifications, run verification:

### Step 4.1: Static Analysis

```bash
fvm flutter analyze
```

Fix any new analysis issues introduced by changes.

### Step 4.2: Run Tests

```bash
fvm flutter test
```

If tests fail:
1. Identify which simplification caused the failure
2. Revert or fix that specific change
3. Re-run tests until passing

### Step 4.3: Summary

Report what was simplified:

**If changes were made:**
```
## Simplification Summary

**Files modified:** [count]
**Changes applied:** [count]

### Changes

1. `path/to/file.dart`
   - [What was simplified and why]

2. `path/to/other.dart`
   - [What was simplified and why]

### Verification
- flutter analyze: [pass/fail]
- flutter test: [pass/fail]
```

**If no changes needed:**
```
## No Simplification Needed

Reviewed [files] and found no opportunities for simplification that would improve clarity without risking behavior changes.

The code already follows good patterns for:
- [Specific positive observation]
- [Another positive observation]
```

</process>

<success_criteria>
- Target code scope clarified (via arguments or AskUserQuestion)
- Code read and analyzed before any changes
- Only genuine simplifications applied (clarity improvement, not just shorter)
- All functionality preserved - no behavior changes
- `flutter analyze` passes after changes
- `flutter test` passes after changes
- Clear summary provided (changes made or "no changes needed")
</success_criteria>
