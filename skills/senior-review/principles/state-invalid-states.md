---
title: Make Invalid States Unrepresentable
category: state
impact: CRITICAL
impactDescription: Eliminates entire class of bugs
tags: discriminated-union, boolean-flags, state-modeling, type-safety
---

## Make Invalid States Unrepresentable

Replace boolean flag combinations with discriminated unions/enums where each variant represents exactly one valid state.

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
