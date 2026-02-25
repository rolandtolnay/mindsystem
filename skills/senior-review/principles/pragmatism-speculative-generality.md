---
title: Speculative Generality
category: pragmatism
impact: MEDIUM
impactDescription: Reduces unnecessary complexity
tags: abstraction, yagni, over-engineering, interfaces
---

## Speculative Generality

Don't abstract until 2-3 concrete cases exist. Build for today's requirements; extract abstractions when you have real examples.

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
