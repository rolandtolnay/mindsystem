---
title: Data Objects Over Flag Parades
category: dependencies
impact: MEDIUM-HIGH
impactDescription: Stabilizes APIs between layers
tags: data-objects, flags, coupling, api-design
---

## Data Objects Over Flag Parades

Pass typed data objects through layers instead of boolean flag parades that couple caller to implementation.

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
