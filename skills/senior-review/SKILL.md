---
name: senior-review
description: Review code for architectural and structural design issues across any tech stack. Use when reviewing PRs, auditing component design, evaluating state management, or identifying problems that make code hard to evolve. Optimized for web/fullstack (Next.js, React, Node) but applicable to any language.
license: MIT
metadata:
  author: Roland Tolnay
  version: "1.0.0"
  date: February 2026
  abstract: Tech-agnostic code review framework focused on structural improvements that typical reviews miss. Uses 3 core lenses (State Modeling, Responsibility Boundaries, Abstraction Timing) backed by 11 detailed principles organized into 4 categories. Each principle includes detection signals and reasoning — no code examples, as the model already knows language patterns.
---

# Senior Review

Senior engineering principles for code across any tech stack. Apply when reviewing, refactoring, or writing code to identify structural improvements that make code evolvable, not just working.

## When to Apply

Reference these guidelines when:
- Reviewing code changes (commits, PRs, patches)
- Refactoring existing code
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

**Senior pattern:** Discriminated unions/enums where each variant is a valid state. Factory functions that encapsulate decision logic. Compiler-enforced exhaustive handling.

Related principles: `state-invalid-states.md`, `state-type-hierarchies.md`, `state-single-source-of-truth.md`

### Lens 2: Responsibility Boundaries

**Question:** If I remove/modify feature X, how many files change?

Look for:
- Optional feature logic scattered throughout a parent component
- Components/modules with 6+ parameters (doing too much)
- Deep callback chains passing flags through layers

**Senior pattern:** Wrapper/decorator components for optional features. Typed data objects instead of flag parades. Each module has one job.

Related principles: `structure-feature-isolation.md`, `structure-composition-over-config.md`, `structure-module-cohesion.md`

### Lens 3: Abstraction Timing

**Question:** Is this abstraction earned or speculative?

Look for:
- Interfaces with only one implementation
- Factories that create only one type
- "Flexible" config that's never varied
- BUT ALSO: Duplicated code that should be unified

**Senior pattern:** Abstract when you have 2-3 concrete cases, not before. Extract when duplication causes bugs or drift, not for aesthetics.

Related principles: `pragmatism-speculative-generality.md`, `dependencies-data-not-flags.md`

## Principle Categories

| Category | Principles | Focus |
|----------|------------|-------|
| State & Types | 1, 2, 3 | Invalid states, type hierarchies, single source of truth |
| Structure | 4, 5, 6 | Feature isolation, composition, module cohesion |
| Dependencies | 7, 8, 9 | Data flow, temporal coupling, API boundary design |
| Pragmatism | 10, 11 | Avoiding over-engineering, consistent error handling |

## Quick Reference

### State & Type Safety
- **invalid-states** - Replace boolean flag combinations with discriminated unions/enums
- **type-hierarchies** - Use factories to encapsulate decision logic in the type system
- **single-source-of-truth** - One owner per state, derive the rest

### Structure & Composition
- **feature-isolation** - Isolate optional feature logic into wrapper/decorator components
- **composition-over-config** - Small focused components over god components with many flags
- **module-cohesion** - Group related logic into cohesive module boundaries

### Dependencies & Flow
- **data-not-flags** - Pass typed data objects through layers, not boolean flag parades
- **temporal-coupling** - Enforce operation sequences via types, not documentation
- **api-boundary-design** - Typed request/response contracts with validation at boundaries

### Pragmatism
- **speculative-generality** - Don't abstract until 2-3 concrete cases exist
- **consistent-error-handling** - One strategy applied everywhere, not ad-hoc try/catch

## How to Use

Read individual principle files for detailed explanations:

```
principles/state-invalid-states.md
principles/structure-feature-isolation.md
principles/dependencies-api-boundary-design.md
```

Each principle file contains:
- Brief explanation of what to do instead
- Detection signals (what to look for)
- Why it matters (evolution impact)
- Senior pattern description
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

5. **Formulate concrete suggestions** - Name specific extractions, describe before/after for the highest-impact change

## Output Format

```markdown
## Senior Review: [Target]

### Summary
[1-2 sentences: Overall assessment and the single most important structural opportunity]

### Findings

#### High Impact: [Issue Name]
**What I noticed:** [Specific code pattern observed]
**Why it matters:** [How this will cause problems as code evolves]
**Suggestion:** [Concrete refactoring - name the types/modules to extract]

#### Medium Impact: [Issue Name]
[Same structure]

#### Low Impact: [Issue Name]
[Same structure]

### No Issues Found
[If a lens revealed no problems, briefly note: "State modeling: No boolean flag combinations or repeated decision logic detected."]

---

**What's your take on these suggestions? Any context I'm missing?**
```

After the markdown output, append a YAML summary block for orchestrator parsing:

```yaml
# review-summary
findings: [number of findings]
high_impact: [count]
medium_impact: [count]
low_impact: [count]
top_issue: "[one-line description of highest impact finding]"
verdict: "clean | minor_issues | needs_refactoring | structural_concerns"
```

## Success Criteria

- At least one finding per applicable lens (or explicit "no issues" statement)
- Each finding tied to evolution impact, not just "could be better"
- Suggestions are concrete: specific types/modules named, not vague advice
- No forced findings - if code is solid, say so
- User has opportunity to provide context before changes
- YAML summary block included for orchestrator parsing

