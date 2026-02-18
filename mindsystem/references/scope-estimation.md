<scope_estimation>
Plans must maintain consistent quality from first task to last. This requires understanding quality degradation and splitting aggressively.

<quality_insight>
Claude degrades when it *perceives* context pressure and enters "completion mode."

| Context Usage | Quality | Claude's State |
|---------------|---------|----------------|
| 0-30% | PEAK | Thorough, comprehensive |
| 30-50% | GOOD | Confident, solid work |
| 50-70% | DEGRADING | Efficiency mode begins |
| 70%+ | POOR | Rushed, minimal |

**The 40-50% inflection point:** Claude sees context mounting and thinks "I'd better conserve now." Result: "I'll complete the remaining tasks more concisely" = quality crash.

**The rule:** Stop BEFORE quality degrades, not at context limit.
</quality_insight>

<context_target>
**Plans should complete within ~50% of context usage.**

Why 50% not 80%?
- No context anxiety possible
- Quality maintained start to finish
- Room for unexpected complexity
- If you target 80%, you've already spent 40% in degradation mode
</context_target>

<task_rule>
**Budget-based grouping. Each executor burns ~15-20% fixed overhead (prompt, workflow, project refs, shared file reads). Available budget per plan: ~30-35% marginal cost.**

| Weight | Marginal Cost | Examples |
|--------|---------------|----------|
| Light | ~5-8% | One-line fixes, config changes, dead code removal, renaming |
| Medium | ~10-15% | CRUD endpoints, widget extraction, single-file refactoring |
| Heavy | ~20-25% | Complex business logic, architecture changes, multi-file integrations |

**Grouping rule:** `sum(marginal_costs) <= 30-35%`. Pack tasks by feature affinity until budget full.

**Minimum plan threshold:** Plans under ~15% marginal cost → consolidate with related work in the same wave. A single light task alone wastes executor overhead.
</task_rule>

<tdd_plans>
**TDD features get their own plans. Target ~40% context.**

TDD requires 2-3 execution cycles (RED → GREEN → REFACTOR), each with file reads, test runs, and potential debugging. This is fundamentally heavier than linear task execution. TDD features are inherently heavy-weight (~25-40% marginal) and naturally get dedicated plans through budget calculation.

| TDD Feature Complexity | Context Usage |
|------------------------|---------------|
| Simple utility function | ~25-30% |
| Business logic with edge cases | ~35-40% |
| Complex algorithm | ~40-50% |

**One feature per TDD plan.** If features are trivial enough to batch, they're trivial enough to skip TDD.

**Why TDD plans are separate:**
- TDD consumes 40-50% context for a single feature
- Dedicated plans ensure full quality throughout RED-GREEN-REFACTOR
- Each TDD feature gets fresh context, peak quality

See `~/.claude/mindsystem/references/tdd.md` for TDD plan structure.
</tdd_plans>

<split_signals>

<always_split>
- **Marginal cost sum exceeds 35%** - Budget overflow regardless of task count
- **Multiple subsystems** - DB + API + UI = separate plans
- **Any task with >5 file modifications** - Split by file groups
- **Discovery + verification in separate plans** - Don't mix exploratory and implementation work
- **Discovery + implementation** - DISCOVERY.md in one plan, implementation in another
</always_split>

<consider_splitting>
- Estimated >5 files modified total
- Complex domains (auth, payments, data modeling)
- Any uncertainty about approach
- Natural semantic boundaries (Setup -> Core -> Features)
</consider_splitting>
</split_signals>

<splitting_strategies>
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

<dependency_awareness>
**Dependencies centralized in EXECUTION-ORDER.md.**

```markdown
## Wave 1 (parallel)
- 03-01-PLAN.md — User feature
- 03-02-PLAN.md — Product feature

## Wave 2
- 03-03-PLAN.md — Integration (after: 01, 02)
```

Plans declare files in `**Files:**` lines within `## Changes` subsections. EXECUTION-ORDER.md tracks wave groups and dependencies.

**Wave assignment rules:**
- No dependencies + no file conflicts with other Wave 1 plans → Wave 1 (parallel)
- Depends on earlier plan → later wave (runs after dependency completes)
- Shared files with sibling plan → sequential (by plan number)

**SUMMARY references:**
- Only reference prior SUMMARY if genuinely needed (imported types, decisions affecting this plan)
- Independent plans need NO prior SUMMARY references
- Reflexive chaining (02 refs 01, 03 refs 02) is an anti-pattern
</dependency_awareness>

<file_ownership>
**Exclusive file ownership prevents conflicts.**

File ownership is determined from `**Files:**` lines in each plan's `## Changes` section and validated in EXECUTION-ORDER.md wave assignments.

```markdown
# Plan 01 Changes
### 1. Create User model
**Files:** `src/models/user.ts`, `src/api/users.ts`, `src/components/UserList.tsx`

# Plan 02 Changes
### 1. Create Product model
**Files:** `src/models/product.ts`, `src/api/products.ts`, `src/components/ProductList.tsx`
```

No overlap → can run parallel (same wave in EXECUTION-ORDER.md).

**If file appears in multiple plans:** Later plan depends on earlier (by plan number).
**If file cannot be split:** Plans must be sequential for that file.
</file_ownership>

<anti_patterns>
**Bad - Comprehensive plan:**
```
Plan: "Complete Authentication System"
Tasks: 8 (models, migrations, API, JWT, middleware, hashing, login form, register form)
Result: Task 1-3 good, Task 4-5 degrading, Task 6-8 rushed
```

**Good - Budget-aware plans:**
```
Plan 1: "Auth Database + Config" (3L+1M = ~28% marginal)
Plan 2: "Auth API Core" (2M = ~25% marginal)
Plan 3: "Auth API Protection" (1H = ~22% marginal)
Plan 4: "Auth UI Components" (2M = ~25% marginal)
Each: marginal within 30-35%, peak quality, atomic commits
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

<estimating_context>
**Budget math:** Fixed overhead (~15-20%) + sum(marginal costs) = total context usage. Target total under 50%.

| Scenario | Tasks | Marginal | Fixed | Total |
|----------|-------|----------|-------|-------|
| 4 light fixes | 4L | ~24% | ~18% | ~42% |
| 2 medium tasks | 2M | ~25% | ~18% | ~43% |
| 1 heavy + 1 light | H+L | ~28% | ~18% | ~46% |
| 3 medium tasks | 3M | ~35% | ~18% | ~53% (risky) |
| 2 heavy tasks | 2H | ~45% | ~18% | ~63% (split) |

**Executor overhead:** ~2,400 tokens (down from ~6,900 in previous versions), freeing ~4,500 tokens per plan for code quality.
</estimating_context>

<summary>
**Budget-based grouping, 50% context target:**
- All tasks: Peak quality
- Git: Atomic per-task commits
- Parallel by default: Fresh context per subagent

**The principle:** Budget-aware consolidation. Fewer executors, same quality, less overhead.

**The rules:**
- Group by marginal cost budget (sum <= 30-35%), not by fixed task count.
- Consolidate plans under ~15% marginal with related same-wave work.
- Split when marginal cost sum exceeds 35%.
- Vertical slices over horizontal layers.
- Dependencies centralized in EXECUTION-ORDER.md.
- Autonomous plans get parallel execution.

**Commit rule:** Each plan produces 3-4 commits total (2-3 change commits + 1 docs commit).
</summary>
</scope_estimation>
