---
title: Temporal Coupling
category: dependencies
impact: MEDIUM
impactDescription: Catches misuse at compile time
tags: builder-pattern, type-state, initialization, sequence
---

## Temporal Coupling

Enforce operation sequences via types, not documentation. Make it impossible to call methods in the wrong order.

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
