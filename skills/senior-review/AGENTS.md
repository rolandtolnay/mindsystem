# Senior Review

**Version 1.0.0**
Roland Tolnay
February 2026

> This document is optimized for AI agents and LLMs. Principles are organized by category and prioritized by structural impact. No code examples — detection signals and reasoning only.

---

## Abstract

Tech-agnostic code review framework focused on structural improvements that typical reviews miss. Uses 3 core lenses (State Modeling, Responsibility Boundaries, Abstraction Timing) backed by 11 detailed principles organized into 4 categories. Each principle includes detection signals, evolution impact reasoning, and self-review questions. Optimized for web/fullstack (Next.js, React, Node) but applicable to any language or stack.

---

## Table of Contents

1. [Core Lenses](#1-core-lenses)
   - 1.1 [State Modeling](#11-state-modeling)
   - 1.2 [Responsibility Boundaries](#12-responsibility-boundaries)
   - 1.3 [Abstraction Timing](#13-abstraction-timing)

2. [State & Type Safety](#2-state--type-safety) - **CRITICAL**
   - 2.1 [Make Invalid States Unrepresentable](#21-make-invalid-states-unrepresentable)
   - 2.2 [Explicit Type Hierarchies](#22-explicit-type-hierarchies)
   - 2.3 [Single Source of Truth](#23-single-source-of-truth)

3. [Structure & Composition](#3-structure--composition) - **HIGH**
   - 3.1 [Isolate Feature Responsibility](#31-isolate-feature-responsibility)
   - 3.2 [Composition Over Configuration](#32-composition-over-configuration)
   - 3.3 [Module Cohesion](#33-module-cohesion)

4. [Dependencies & Flow](#4-dependencies--flow) - **MEDIUM-HIGH**
   - 4.1 [Data Objects Over Flag Parades](#41-data-objects-over-flag-parades)
   - 4.2 [Temporal Coupling](#42-temporal-coupling)
   - 4.3 [API Boundary Design](#43-api-boundary-design)

5. [Pragmatism](#5-pragmatism) - **MEDIUM**
   - 5.1 [Speculative Generality](#51-speculative-generality)
   - 5.2 [Consistent Error Handling](#52-consistent-error-handling)

---

## Senior Mindset

Junior and mid-level engineers ask: **"Does this code work?"**
Senior engineers ask: **"How will this code change? What happens when requirements shift?"**

This distinction drives everything. Code that "works" today becomes a liability when:
- A new state is added and 5 files need coordinated updates
- A feature toggle requires touching code scattered across the codebase
- A bug fix in one place breaks assumptions elsewhere

Focus on **structural issues that compound over time** - the kind that turn "add a simple feature" into "refactor half the codebase first."

---

## 1. Core Lenses

Apply these three lenses to every review. They catch 80% of structural issues.

### 1.1 State Modeling

**Question:** Can this code represent invalid states?

Look for:
- Multiple boolean flags (2^n possible states, many invalid)
- Primitive obsession (stringly-typed status, magic numbers)
- Same decision logic repeated in multiple places

**Senior pattern:** Discriminated unions/enums where each variant is a valid state. Factory functions that encapsulate decision logic. Compiler-enforced exhaustive handling.

---

### 1.2 Responsibility Boundaries

**Question:** If I remove/modify feature X, how many files change?

Look for:
- Optional feature logic scattered throughout a parent component
- Components/modules with 6+ parameters (doing too much)
- Deep callback chains passing flags through layers

**Senior pattern:** Wrapper/decorator components for optional features. Typed data objects instead of flag parades. Each module has one job.

---

### 1.3 Abstraction Timing

**Question:** Is this abstraction earned or speculative?

Look for:
- Interfaces with only one implementation
- Factories that create only one type
- "Flexible" config that's never varied
- BUT ALSO: Duplicated code that should be unified

**Senior pattern:** Abstract when you have 2-3 concrete cases, not before. Extract when duplication causes bugs or drift, not for aesthetics.

---

## 2. State & Type Safety

**Impact: CRITICAL**

Issues with state modeling compound rapidly. Invalid state combinations cause bugs that are hard to reproduce and fix.

### 2.1 Make Invalid States Unrepresentable

**Impact: CRITICAL (Eliminates entire class of bugs)**

Multiple boolean flags that create 2^n possible states, where many combinations are invalid or nonsensical.

**Detection signals:**
- 3+ boolean parameters passed together
- Same boolean checks repeated in multiple places
- if/else chains checking flag combinations
- Some flag combinations would cause undefined behavior
- State represented as string literals compared with `===`

**Why it matters:**
- Compiler/type checker enforces exhaustive handling of all states
- New states are added explicitly, not as boolean combinations
- Impossible to create invalid state combinations at the type level
- Self-documenting: the union/enum shows all possible states in one place

**Senior pattern:** Define a discriminated union (TypeScript), enum with associated data (Rust/Swift), or sealed interface (Kotlin/Java) where each variant carries only the data relevant to that state. Use exhaustive pattern matching (switch/match) so the compiler flags unhandled cases when a new variant is added.

**Detection questions:**
- Are there 3+ boolean parameters being passed together?
- Do you see the same boolean checks repeated in multiple places?
- Are there if/else chains checking combinations of flags?
- Could some flag combinations cause undefined behavior?
- Would adding a new state require updating multiple scattered conditionals?

---

### 2.2 Explicit Type Hierarchies

**Impact: HIGH (Centralizes decision logic)**

Complex if/else chains determining behavior scattered across components rather than encoded in the type system.

**Detection signals:**
- Complex if/else chains determining which component to render or which path to take
- Same decision logic duplicated across multiple modules
- Components receive data they only use to make decisions (not to display or process)
- New requirement would add another boolean parameter
- Switch statements on string values or numeric codes

**Why it matters:**
- Decision logic lives in one place (the factory)
- Consumers receive pre-computed decisions, not raw data to interpret
- Adding new variants is explicit and type-checked
- Testing is clearer: test the factory, then test each variant's behavior

**Senior pattern:** Create a factory function or static method that takes raw inputs and returns a typed variant. The factory is the single place where decision logic lives. Consumers pattern-match on the result and handle each variant — they never inspect raw data to make decisions themselves.

**Detection questions:**
- Are there complex if/else chains determining behavior scattered across components?
- Is the same decision logic duplicated in multiple places?
- Do components receive data they only use to decide what to do?
- Would a new requirement add another boolean parameter to existing interfaces?

---

### 2.3 Single Source of Truth

**Impact: HIGH (Prevents stale data bugs)**

Same state tracked in multiple places — local component state duplicating global state, components caching derived values.

**Detection signals:**
- Same data stored in both global state and local component state
- Effect hooks syncing local state from global state
- Two sources of truth that could disagree
- Derived data being cached in state instead of computed on access
- Manual synchronization logic between stores or contexts

**Why it matters:**
- No "which value is authoritative?" confusion
- State updates propagate automatically through derivations
- Easier debugging: one place to inspect each piece of state
- Eliminates stale data bugs caused by desynchronized copies

**Senior pattern:** Identify the single authoritative owner for each piece of state. All other consumers read from that owner or derive values from it. Local component state is reserved for truly ephemeral UI concerns (focus, hover, animation progress) that no other component needs. If two components need the same state, lift it to a shared owner rather than syncing copies.

**Detection questions:**
- Is the same data stored in both a global store and local component state?
- Are there effect hooks whose sole purpose is syncing one state source to another?
- Could two sources of truth disagree? What happens when they do?
- Is derived data being cached in state instead of computed from the source?

---

## 3. Structure & Composition

**Impact: HIGH**

Structural issues make features hard to add, remove, or modify independently.

### 3.1 Isolate Feature Responsibility

**Impact: HIGH (Features become removable)**

A feature's logic is woven throughout a parent component rather than encapsulated.

**Detection signals:**
- More than 30% of a component's code dedicated to one optional feature
- Removing a feature requires deleting scattered lines throughout the file
- Multiple `if (featureEnabled)` checks spread across the component
- State variables only used by one feature mixed with core state
- Feature-specific imports polluting the core module

**Why it matters:**
- Feature can be disabled/removed by removing one wrapper
- Core component remains focused and testable
- Feature logic is cohesive and isolated in one place
- Multiple features compose without polluting each other

**Senior pattern:** Move all feature-specific state, effects, and rendering into a wrapper/decorator component that wraps the core. The wrapper provides feature context to the core through a render prop, slot, or composition pattern. The core component has zero awareness of the feature — it renders its own concern and accepts optional enhancement points.

**Detection questions:**
- Is more than 30% of a component's code dedicated to one optional feature?
- Would removing a feature require deleting scattered lines throughout the file?
- Are there multiple `if (featureEnabled)` checks spread across the component?
- Does the component have state variables only used by one feature?

---

### 3.2 Composition Over Configuration

**Impact: MEDIUM (Simplifies component APIs)**

Giant components with dozens of boolean flags — "god components" that handle every case through configuration.

**Detection signals:**
- Component has more than 6-8 parameters/props
- Boolean parameters that are mutually exclusive
- Component is really 3 different components pretending to be 1
- Adding a new variant would require another boolean flag
- Conditionals inside the component that render entirely different structures

**Why it matters:**
- Each component has one job and is easy to understand
- New variants don't bloat existing components
- Easier to test: focused inputs and outputs
- Flexible: compose for custom needs, use shortcuts for common ones

**Senior pattern:** Split the god component into focused units, each handling one variant or concern. Provide composition points (children/slots/render props) for flexibility. For common combinations, offer convenience wrappers that compose the focused units — but the building blocks remain available for custom needs.

**Detection questions:**
- Does this component have more than 6-8 parameters?
- Are there boolean parameters that are mutually exclusive?
- Is this component really multiple components pretending to be one?
- Would adding a new variant require another boolean flag?

---

### 3.3 Module Cohesion

**Impact: MEDIUM-HIGH (Changes stay contained to one module)**

Related logic spread across modules by technical layer rather than grouped by feature/domain.

**Detection signals:**
- A feature's logic is spread across 4+ directories by technical layer (routes/, models/, services/, utils/)
- Changing one feature requires touching files in many unrelated folders
- Related types, helpers, and constants live far from the code that uses them
- Shared utility files that grow unbounded because "everything needs it"
- Circular dependencies between modules

**Why it matters:**
- Feature changes are contained: one module to understand, one module to test
- Dependencies between modules are explicit and minimal
- Easier to extract, replace, or delete a feature entirely
- New developers can navigate by feature, not by guessing which technical layer holds what

**Senior pattern:** Organize by feature/domain first, technical layer second. Each feature module contains its types, logic, and tests colocated. Shared utilities exist only when genuinely used across 3+ features — otherwise the "utility" belongs in the feature that uses it. Module boundaries are enforced by explicit public APIs (barrel files, index exports) that hide internal structure.

**Detection questions:**
- Does changing one feature require touching files in many unrelated directories?
- Is related logic (types, helpers, constants) colocated with the code that uses it?
- Are there shared utility files that grow unbounded?
- Can you describe what each module "owns" in one sentence?

---

## 4. Dependencies & Flow

**Impact: MEDIUM-HIGH**

Coupling and dependency issues make code changes ripple unexpectedly.

### 4.1 Data Objects Over Flag Parades

**Impact: MEDIUM-HIGH (Stabilizes APIs between layers)**

Parent components/callers pass many flags and control parameters to children, creating tight coupling.

**Detection signals:**
- Functions/components have 4+ boolean or primitive parameters beyond core data
- Boolean flags being passed through multiple layers unchanged
- Changing a child's behavior requires changing every intermediate caller's signature
- Parameters that are only used in some conditions
- Same group of parameters appears in multiple function signatures

**Why it matters:**
- Consumer's API is stable even as internal requirements change
- Callers don't need to know the consumer's internal decision logic
- Data dependencies are explicit in the object's type
- Easier to test: create data objects directly without reconstructing call chains

**Senior pattern:** Group related parameters into a typed data object (interface, type, struct, record). The object carries everything the consumer needs to make its own decisions. The caller constructs the object from available context — if construction is complex, use a factory. The consumer's public API accepts the data object, not individual flags.

**Detection questions:**
- Are there 4+ boolean/primitive parameters being passed alongside core data?
- Are flags being threaded through multiple layers without being used in intermediate ones?
- Would changing a child's behavior require updating every caller's signature?
- Do the same parameter groups appear in multiple function signatures?

---

### 4.2 Temporal Coupling

**Impact: MEDIUM (Catches misuse at compile time)**

Operations must happen in a specific order, but nothing enforces that order.

**Detection signals:**
- Methods that must be called before others
- Comments like "must call X first" or "call after Y"
- Objects can be in an "invalid" state between operations
- Tests have setup steps that could be forgotten
- Init/setup methods that must run before the object is usable

**Why it matters:**
- Compiler catches misuse, not runtime errors
- Self-documenting: types show valid sequences
- Impossible to forget required steps
- Easier onboarding: the API guides you through the correct order

**Senior pattern:** Use the builder pattern (fluent API that accumulates required state before producing the final object) or the type-state pattern (each step returns a different type that only exposes the next valid operation). For simpler cases, require all necessary data in the constructor so an object is always valid from creation.

**Detection questions:**
- Are there methods that must be called before others?
- Are there comments like "must call X first" or "call after Y"?
- Can objects be in an "invalid" state between operations?
- Do tests have setup steps that could be forgotten?

---

### 4.3 API Boundary Design

**Impact: HIGH (Prevents invalid data from propagating)**

Loose API contracts where unvalidated data flows deep into the system before failing.

**Detection signals:**
- API handlers that accept `any` or untyped request bodies
- Validation logic scattered across business logic instead of at the boundary
- No shared type between client and server for the same endpoint
- Error responses that leak internal details (stack traces, database errors)
- Different endpoints handling the same entity with inconsistent field names

**Why it matters:**
- Invalid data is caught at the boundary before it reaches business logic
- Internal code operates on validated, typed data — no defensive checks everywhere
- Client and server stay in sync through shared types or generated contracts
- Error responses are consistent and safe for consumers

**Senior pattern:** Validate and parse at the boundary: incoming data is unknown until validated, then flows as typed objects through internal layers. Define request/response types explicitly (schema validation, codegen, or shared type packages). Internal functions receive validated types and trust them — they don't re-validate. Error responses follow a consistent shape with safe, user-facing messages.

**Detection questions:**
- Do API handlers accept untyped or `any` request bodies?
- Is validation scattered across business logic instead of concentrated at boundaries?
- Is there a shared type contract between client and server?
- Do error responses leak internal details like stack traces?

---

## 5. Pragmatism

**Impact: MEDIUM**

Over-engineering and inconsistency create unnecessary complexity.

### 5.1 Speculative Generality

**Impact: MEDIUM (Reduces unnecessary complexity)**

Abstractions added for hypothetical future needs that may never materialize.

**Detection signals:**
- Interface with only one implementation
- Factory that only creates one type
- Configuration options no one uses
- Abstraction added "in case we need it later"
- Generic type parameters that are always the same concrete type

**Why it matters:**
- Less code to maintain and less indirection to trace
- Abstractions based on real needs fit better than guesses
- Easier to understand: concrete code is simpler than abstract code
- When you do need the abstraction, you'll know the right shape because you have concrete examples

**Senior pattern:** Write concrete code for the first case. When the second or third case appears, you'll see the real variation axis and can extract the right abstraction. The refactoring from concrete to abstract is straightforward — but the reverse (removing a premature abstraction) is painful because code depends on the abstraction's shape.

**Detection questions:**
- Is there an interface with only one implementation?
- Is there a factory that only creates one type?
- Are there configuration options no one uses?
- Was this abstraction added "in case we need it later"?

---

### 5.2 Consistent Error Handling

**Impact: MEDIUM (Improves UX and debugging)**

Ad-hoc try/catch scattered across the codebase, inconsistent error UX.

**Detection signals:**
- Errors appear differently across screens (toasts vs dialogs vs inline vs nothing)
- try/catch blocks scattered in component/handler code with different recovery strategies
- Inconsistent error messaging (raw exceptions shown to users in some places)
- No standard retry mechanism
- Some code paths silently swallow errors with empty catch blocks

**Why it matters:**
- Users get a consistent experience when things go wrong
- Developers follow one pattern — no decision fatigue per error site
- Error states are explicit and testable, not hidden in catch blocks
- Debugging is faster: errors flow through a known path

**Senior pattern:** Establish a single error handling strategy for the project: errors flow through a known path (Result types, error boundaries, middleware, or global handlers) and surface to users through one consistent mechanism. Individual call sites don't decide how to present errors — they report them, and the strategy handles presentation. Empty catch blocks are banned; if an error is truly ignorable, document why.

**Detection questions:**
- Do errors appear differently across different screens or endpoints?
- Are try/catch blocks scattered with different recovery strategies?
- Are there empty catch blocks that silently swallow errors?
- Is there a standard, documented error handling strategy for the project?

---

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

---

## Analysis Process

1. **Read thoroughly** - Understand what the code does, not just its structure

2. **Apply the three lenses** - For each lens, note specific instances (or note "no issues found")

3. **Check for additional patterns** - If you notice issues beyond the core lenses, consult the principle sections for precise diagnosis

4. **Prioritize by evolution impact**:
   - High: Will cause cascading changes when requirements shift
   - Medium: Creates friction but contained to one area
   - Low: Suboptimal but won't compound

5. **Formulate concrete suggestions** - Name specific extractions, describe before/after for the highest-impact change

---

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

---

## Success Criteria

- At least one finding per applicable lens (or explicit "no issues" statement)
- Each finding tied to evolution impact, not just "could be better"
- Suggestions are concrete: specific types/modules named, not vague advice
- No forced findings - if code is solid, say so
- User has opportunity to provide context before changes
- YAML summary block included for orchestrator parsing
