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
**Budget-aware grouping.** The orchestrator proposes plan boundaries using weight heuristics and contextual judgment.

| Weight | Cost | Examples |
|--------|------|----------|
| Light | 5% | One-line fixes, config changes, dead code removal, renaming |
| Medium | 10% | CRUD endpoints, widget extraction, single-file refactoring |
| Heavy | 20% | Complex business logic, architecture changes, multi-file integrations |

**For the orchestrator (grouping authority):** Use weight estimates as guidance when proposing plan boundaries. Target 25-45% per plan. Bias toward consolidation — fewer plans, less overhead. Consider that sequential-only work (no parallelism benefit from splitting) can be grouped more aggressively. A single light task alone wastes executor overhead — consolidate with related work.

**For the plan-writer (structural validation):** Classify weights for the grouping rationale table. Do NOT re-group based on budget math — the orchestrator already considered context budget with user input. Deviate only for structural issues (file conflicts, circular dependencies, missing dependency chains).
</task_rule>

<tdd_plans>
**TDD features get their own plans. Target ~40% context.**

TDD requires 2-3 execution cycles (RED → GREEN → REFACTOR), each with file reads, test runs, and potential debugging. This is fundamentally heavier than linear task execution. TDD features are inherently heavy-weight (~25-40% marginal) and are always isolated into dedicated plans.

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

**Good - Consolidated plans:**
```
Plan 1: "Auth Foundation" (models + config + middleware = ~35%)
Plan 2: "Auth Endpoints + UI" (API + forms + wiring = ~40%)
Each: within reasonable budget, peak quality, atomic commits
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
Weight estimates are heuristics for the orchestrator's grouping judgment, not mechanical constraints. Actual context usage depends on model, task complexity, file sizes, and context window. Calibrate from real execution data — when plans consistently finish with headroom, the orchestrator should group more aggressively.

The plan-writer uses weight classifications for the grouping rationale table (transparency), not as a reason to override the orchestrator's proposed boundaries.
</estimating_context>

<summary>
**Budget-aware consolidation, 50% context target:**
- All tasks: Peak quality
- Git: Atomic per-task commits
- Parallel by default: Fresh context per subagent

**The principle:** Fewer executors, same quality, less overhead. Bias toward consolidation.

**The rules:**
- Orchestrator proposes grouping using weight heuristics and contextual judgment (target 25-45%).
- Plan-writer validates structurally (file conflicts, circular deps) — deviates only for structural issues.
- Vertical slices over horizontal layers.
- Dependencies centralized in EXECUTION-ORDER.md.
- Autonomous plans get parallel execution.

**Commit rule:** Each plan produces 3-4 commits total (2-3 change commits + 1 docs commit).
</summary>
</scope_estimation>
