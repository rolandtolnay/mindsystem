---
title: Module Cohesion
category: structure
impact: MEDIUM-HIGH
impactDescription: Changes stay contained to one module
tags: cohesion, boundaries, feature-folders, colocation
---

## Module Cohesion

Group related logic into cohesive module boundaries so that a single feature change touches one module, not many.

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
