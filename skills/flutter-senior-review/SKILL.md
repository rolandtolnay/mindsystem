---
name: flutter-senior-review
description: Review Flutter/Dart code for architectural and structural design issues. Use when reviewing PRs, auditing widget design, evaluating state management, or identifying problems that make code hard to evolve.
license: MIT
metadata:
  author: Roland Tolnay
  version: "1.0.0"
  date: January 2026
  abstract: Code review framework focused on structural improvements that typical reviews miss. Uses 3 core lenses (State Modeling, Responsibility Boundaries, Abstraction Timing) backed by 12 detailed principles organized into 4 categories. Each principle includes detection signals, smell examples, senior solutions, and Dart-specific patterns.
---

# Flutter Senior Review

Senior engineering principles for Flutter/Dart code. Apply when reviewing, refactoring, or writing code to identify structural improvements that make code evolvable, not just working.

## When to Apply

Reference these guidelines when:
- Reviewing code changes (commits, PRs, patches)
- Refactoring existing Flutter/Dart code
- Writing new features or components
- Identifying why code feels hard to change
- Planning structural improvements

## Senior Mindset

Junior and mid-level engineers ask: **"Does this code work?"**
Senior engineers ask: **"How will this code change? What happens when requirements shift?"**

This distinction drives everything. Code that "works" today becomes a liability when:
- A new state is added and 5 files need coordinated updates
- A feature toggle requires touching code scattered across the codebase
- A bug fix in one place breaks assumptions elsewhere

Focus on **structural issues that compound over time** - the kind that turn "add a simple feature" into "refactor half the codebase first."

Do NOT look for:
- Style preferences or formatting
- Minor naming improvements
- "Nice to have" abstractions
- Issues already covered by linters/analyzers

## Core Lenses

Apply these three lenses to every review. They catch 80% of structural issues.

### Lens 1: State Modeling

**Question:** Can this code represent invalid states?

Look for:
- Multiple boolean flags (2^n possible states, many invalid)
- Primitive obsession (stringly-typed status, magic numbers)
- Same decision logic repeated in multiple places

**Senior pattern:** Sealed classes where each variant is a valid state. Factory methods that encapsulate decision logic. Compiler-enforced exhaustive handling.

Related principles: `state-invalid-states.md`, `state-type-hierarchies.md`, `state-single-source-of-truth.md`, `state-data-clumps.md`

### Lens 2: Responsibility Boundaries

**Question:** If I remove/modify feature X, how many files change?

Look for:
- Optional feature logic scattered throughout a parent component
- Widgets with 6+ parameters (doing too much)
- Deep callback chains passing flags through layers

**Senior pattern:** Wrapper components for optional features. Typed data objects instead of flag parades. Each widget has one job.

Related principles: `structure-wrapper-pattern.md`, `structure-shared-visual-patterns.md`, `structure-composition-over-config.md`

### Lens 3: Abstraction Timing

**Question:** Is this abstraction earned or speculative?

Look for:
- Interfaces with only one implementation
- Factories that create only one type
- "Flexible" config that's never varied
- BUT ALSO: Duplicated code that should be unified

**Senior pattern:** Abstract when you have 2-3 concrete cases, not before. Extract when duplication causes bugs or drift, not for aesthetics.

Related principles: `pragmatism-speculative-generality.md`, `dependencies-data-not-callbacks.md`

## Principle Categories

| Category | Principles | Focus |
|----------|------------|-------|
| State & Types | 1, 3, 6, 10 | Invalid states, type hierarchies, single source of truth, data clumps |
| Structure | 2, 4, 8 | Feature isolation, visual patterns, composition |
| Dependencies | 5, 7, 9 | Coupling, provider architecture, temporal coupling |
| Pragmatism | 11, 12 | Avoiding over-engineering, consistent error handling |

## Quick Reference

### State & Type Safety
- **invalid-states** - Replace boolean flag combinations with sealed class hierarchies
- **type-hierarchies** - Use factories to encapsulate decision logic
- **single-source-of-truth** - One owner per state, derive the rest via selectors
- **data-clumps** - Group parameters that travel together into typed objects

### Structure & Composition
- **wrapper-pattern** - Isolate optional feature logic into wrapper components
- **shared-visual-patterns** - Deduplicate UI with style variants
- **composition-over-config** - Small focused widgets over god widgets with many flags

### Dependencies & Flow
- **data-not-callbacks** - Pass typed objects, not callback parades
- **provider-tree** - Root -> branch -> leaf hierarchy for providers
- **temporal-coupling** - Enforce operation sequences via types, not documentation

### Pragmatism
- **speculative-generality** - Don't abstract until 2-3 concrete cases exist
- **consistent-error-handling** - One strategy applied everywhere, not ad-hoc try/catch

## How to Use

Read individual principle files for detailed explanations and code examples:

```
principles/state-invalid-states.md
principles/structure-wrapper-pattern.md
principles/dependencies-provider-tree.md
```

Each principle file contains:
- Brief explanation of why it matters
- Detection signals (what to look for)
- Incorrect code example with explanation
- Correct code example with explanation
- Why it matters section
- Detection questions for self-review

## Context Gathering

When asked to review code, first identify the target:

If target is unclear, ask:
- What code should be reviewed? (specific files, a feature folder, uncommitted changes, a commit, a patch file)
- Is there a specific concern or area of focus?

For the specified target, gather the relevant code:
- **Commit**: `git show <commit>`
- **Patch file**: Read the patch file
- **Uncommitted changes**: `git diff` and `git diff --cached`
- **Folder/feature**: Read the relevant files in that directory
- **Specific file**: Read that file and related files it imports/uses

## Analysis Process

1. **Read thoroughly** - Understand what the code does, not just its structure

2. **Apply the three lenses** - For each lens, note specific instances (or note "no issues found")

3. **Check for additional patterns** - If you notice issues beyond the core lenses, consult the principle files for precise diagnosis

4. **Prioritize by evolution impact**:
   - High: Will cause cascading changes when requirements shift
   - Medium: Creates friction but contained to one area
   - Low: Suboptimal but won't compound

5. **Formulate concrete suggestions** - Name specific extractions, show before/after for the highest-impact change

## Output Format

```markdown
## Senior Review: [Target]

### Summary
[1-2 sentences: Overall assessment and the single most important structural opportunity]

### Findings

#### High Impact: [Issue Name]
**What I noticed:** [Specific code pattern observed]
**Why it matters:** [How this will cause problems as code evolves]
**Suggestion:** [Concrete refactoring - name the types/widgets to extract]

#### Medium Impact: [Issue Name]
[Same structure]

#### Low Impact: [Issue Name]
[Same structure]

### No Issues Found
[If a lens revealed no problems, briefly note: "State modeling: No boolean flag combinations or repeated decision logic detected."]

---

**What's your take on these suggestions? Any context I'm missing?**
```

## Success Criteria

- At least one finding per applicable lens (or explicit "no issues" statement)
- Each finding tied to evolution impact, not just "could be better"
- Suggestions are concrete: specific types/widgets named, not vague advice
- No forced findings - if code is solid, say so
- User has opportunity to provide context before changes

## Full Compiled Document

For the complete guide with all principles expanded: `AGENTS.md`
