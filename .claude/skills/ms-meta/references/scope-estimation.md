<scope_estimation>

<task_rule>
## 2-3 Tasks Maximum Per Plan

| Task Complexity | Tasks/Plan | Context/Task | Total |
|-----------------|------------|--------------|-------|
| Simple (CRUD, config) | 3 | ~10-15% | ~30-45% |
| Complex (auth, payments) | 2 | ~20-30% | ~40-50% |
| Very complex (migrations, refactors) | 1-2 | ~30-40% | ~30-50% |

**When in doubt: Default to 2 tasks.** Better to have an extra plan than degraded quality.
</task_rule>

<split_signals>
## When to Split Plans

**Always split:**
- More than 3 tasks (even if tasks seem small)
- Multiple subsystems (DB + API + UI = separate plans)
- Any task with >5 file modifications
- Discovery + verification in separate plans (don't mix exploratory and implementation work)
- Discovery + implementation (DISCOVERY.md in one plan, implementation in another)

**Consider splitting:**
- Estimated >5 files modified total
- Complex domains (auth, payments, data modeling)
- Any uncertainty about approach
- Natural semantic boundaries (Setup → Core → Features)
</split_signals>

<splitting_strategies>
## How to Split

**Vertical slices (default):** Group by feature, not by layer.

```
PREFER: Plan 01 = User (model + API + UI)
        Plan 02 = Product (model + API + UI)
        Plan 03 = Order (model + API + UI)

AVOID:  Plan 01 = All models
        Plan 02 = All APIs (depends on 01)
        Plan 03 = All UIs (depends on 02)
```

Vertical slices maximize parallelism: [01, 02, 03] run simultaneously.
Horizontal layers force sequential execution: 01 → 02 → 03.

**By dependency:** Only when genuine dependencies exist.
```
Plan 01: Auth foundation (middleware, JWT utils)
Plan 02: Protected features (uses auth from 01)
```

**By complexity:** When one slice is much heavier.
```
Plan 01: Dashboard layout shell
Plan 02: Data fetching and state
Plan 03: Visualization components
```
</splitting_strategies>

<dependency_management>
## Dependency Declaration

Plans declare dependencies explicitly via frontmatter:

```yaml
# Independent plan (Wave 1 candidate)
depends_on: []
files_modified: [src/features/user/model.ts, src/features/user/api.ts]


# Dependent plan (later wave)
depends_on: ["03-01"]
files_modified: [src/integration/stripe.ts]

```

**Wave assignment rules:**
- `depends_on: []` + no file conflicts → Wave 1 (parallel)
- `depends_on: ["XX"]` → runs after plan XX completes
- Shared `files_modified` with sibling → sequential (by plan number)

**SUMMARY references:**
- Only reference prior SUMMARY if genuinely needed
- Independent plans need NO prior SUMMARY references
- Reflexive chaining (02 refs 01, 03 refs 02) is an anti-pattern
</dependency_management>

<file_ownership>
## Exclusive File Ownership

Prevents merge conflicts:

```yaml
# Plan 01 frontmatter
files_modified: [src/models/user.ts, src/api/users.ts, src/components/UserList.tsx]

# Plan 02 frontmatter
files_modified: [src/models/product.ts, src/api/products.ts, src/components/ProductList.tsx]
```

No overlap → can run parallel.

**If file appears in multiple plans:** Later plan depends on earlier.
**If file cannot be split:** Plans must be sequential for that file.
</file_ownership>

<depth_calibration>
## Depth Controls Compression, Not Inflation

| Depth | Typical Phases | Typical Plans/Phase | Tasks/Plan |
|-------|----------------|---------------------|------------|
| Quick | 3-5 | 1-3 | 2-3 |
| Standard | 5-8 | 3-5 | 2-3 |
| Comprehensive | 8-12 | 5-10 | 2-3 |

**Tasks/plan is CONSTANT at 2-3.** The 50% context rule applies universally.

**Key principle:** Derive from actual work. Depth determines how aggressively you combine things, not a target to hit.

- Comprehensive auth = 8 plans (because auth genuinely has 8 concerns)
- Comprehensive "add favicon" = 1 plan (because that's all it is)

Don't pad small work to hit a number. Don't compress complex work to look efficient.
</depth_calibration>

<anti_patterns>
## Anti-Patterns

**Bad - Comprehensive plan:**
```
Plan: "Complete Authentication System"
Tasks: 8 (models, migrations, API, JWT, middleware, hashing, login form, register form)
Result: Task 1-3 good, Task 4-5 degrading, Task 6-8 rushed
```

**Good - Atomic plans:**
```
Plan 1: "Auth Database Models" (2 tasks)
Plan 2: "Auth API Core" (3 tasks)
Plan 3: "Auth API Protection" (2 tasks)
Plan 4: "Auth UI Components" (2 tasks)
Each: 30-40% context, peak quality, atomic commits
```

**Bad - Horizontal layers (sequential):**
```
Plan 01: Create User model, Product model, Order model
Plan 02: Create /api/users, /api/products, /api/orders
Plan 03: Create UserList UI, ProductList UI, OrderList UI
```
Result: 02 depends on 01, 03 depends on 02
Waves: [01] → [02] → [03] (fully sequential)

**Good - Vertical slices (parallel):**
```
Plan 01: User feature (model + API + UI)
Plan 02: Product feature (model + API + UI)
Plan 03: Order feature (model + API + UI)
```
Result: Each plan self-contained, no file overlap
Waves: [01, 02, 03] (all parallel)
</anti_patterns>

<summary>
## The Principle

**Aggressive atomicity.** More plans, smaller scope, consistent quality.

**The rules:**
- If in doubt, split. Quality over consolidation.
- Depth increases plan COUNT, never plan SIZE.
- Vertical slices over horizontal layers.
- Explicit dependencies via `depends_on` frontmatter.
- Autonomous plans get parallel execution.
- Each plan: 2-3 tasks, ~50% context, peak quality.

**Commit rule:** Each plan produces 3-4 commits total (2-3 task commits + 1 docs commit).
</summary>

</scope_estimation>
