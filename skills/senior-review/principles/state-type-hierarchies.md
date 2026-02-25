---
title: Explicit Type Hierarchies
category: state
impact: HIGH
impactDescription: Centralizes decision logic
tags: factory, type-system, decision-logic, pattern-matching
---

## Explicit Type Hierarchies

Encode decision logic in the type system using factories, not scattered if/else chains across components.

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
