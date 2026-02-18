# Phase Prompt Template

Process guidance for generating PLAN.md files. For format specification,
read `~/.claude/mindsystem/references/plan-format.md`.

**File naming:** `{phase}-{plan}-PLAN.md` (e.g., `01-02-PLAN.md` for Phase 1, Plan 2)

---

## Expected Outputs

1. **PLAN.md files** — pure markdown following plan-format.md spec
2. **EXECUTION-ORDER.md** — wave groups for parallel execution

---

## Scope Guidance

**Plan sizing — budget-based grouping:**

Each executor burns ~15-20% fixed overhead. Available budget per plan: ~30-35% marginal cost. Weight classifications (Light/Medium/Heavy) and marginal costs defined in scope-estimation.md.

Grouping rule: `sum(marginal_costs) <= 35%`. Target 25-35% per plan. Plans under ~15% marginal → consolidate with related same-wave work.

**When to split:**

- Different subsystems (auth vs API vs UI)
- Marginal cost sum exceeds 35%
- Risk of context overflow
- TDD candidates — separate plans (inherently heavy-weight)

**Vertical slices preferred:**

```
PREFER: Plan 01 = User (model + API + UI)
        Plan 02 = Product (model + API + UI)

AVOID:  Plan 01 = All models
        Plan 02 = All APIs
        Plan 03 = All UIs
```

---

## TDD Detection

**Heuristic:** Can you write `expect(fn(input)).toBe(output)` before writing `fn`?
- Yes: Create a TDD plan with `**Type:** tdd`
- No: Standard plan (type defaults to execute, omit from metadata line)

TDD features get dedicated plans. One feature per TDD plan.

See `~/.claude/mindsystem/references/tdd.md` for TDD plan structure (RED/GREEN/REFACTOR in ## Changes).

---

## Task Types

| Type | Use For |
|------|---------|
| `execute` | Everything Claude can do independently (default, can be omitted) |
| `tdd` | TDD features with RED → GREEN → REFACTOR cycle |

**Decisions:** Resolve during planning via AskUserQuestion, not during execution. For purely technical choices, make the decision and document it in the plan's ## Context.

---

## Learnings Integration

When expanding tasks into plan ## Changes subsections, check provided learnings for entries relevant to each change. Embed as directives within the change description:

```markdown
### 2. Create auth endpoint
**Files:** `src/api/auth/login.ts`

POST endpoint accepting {email, password}...

**From prior work:** CommonJS libraries fail silently in Edge runtime — verify ESM compat.
```

Rules:
- Maximum 2 learning directives per change (context budget)
- Only include learnings that change what the executor would do
- Phrase as imperative directives, not history
- If no learnings match a change, add nothing

---

## External Services

When a plan introduces external services requiring human configuration, describe them in the plan's ## Context section. The user handles external service setup (account creation, secret retrieval) based on plan context.

**The automation-first rule:** External service notes contain ONLY what Claude literally cannot do:
- Account creation (requires human signup)
- Secret retrieval (requires dashboard access)
- Dashboard configuration (requires human in browser)

**NOT included:** Package installs, code changes, file creation, CLI commands Claude can run.

---

## Anti-Patterns

**Bad: Reflexive dependency chaining**
Plan 02 does not depend on Plan 01 just because 01 comes first. Check actual needs/creates.

**Bad: Horizontal layer grouping**
```
Plan 01: All models
Plan 02: All APIs (depends on 01)
Plan 03: All UIs (depends on 02)
```

**Bad: Vague tasks**
```
### 1. Set up authentication
Implement auth.
```

Claude: "How? What type? What library? Where?" — plans must be specific enough for immediate implementation.

**Bad: Unnecessary SUMMARY references**
Independent plans need NO prior SUMMARY references. Only reference prior SUMMARYs if genuinely importing types/exports from them.
