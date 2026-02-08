# Widget Style Guide

## Breaking Up `build()`

- Always-shown widget → local variable: `final header = Container(...);`
- Conditionally-shown widget → private builder: `_buildXyz(...)` (avoids null crashes, skips unused work)
- Define local widget variables in **screen order** (top to bottom)
- Extract to standalone widget (own file) when: subtree is large, reused, stateful, or a repeated list/grid item
- No file-private widget classes — extract → new widget → new file

## `build()` Internal Order

1. Providers (reads/watches)
2. Hooks
3. Derived variables
4. Widget variables (in render order)

- Extract non-trivial conditions: `final canSubmit = isValid && !isLoading && selectedId != null;`
- Define variables close to where they're used

## Function Placement

- Default: define helpers outside `build()` as class methods (`_buildHeader(...)`, `_onSubmit(...)`)
- 4+ parameters (especially hooks) → define inside `build()` to avoid noisy signatures
- Needs both `WidgetRef` and `BuildContext` → pass only `WidgetRef`, use `ref.context` inside

## Async UX

- Button loading: watch async provider state, not separate local flags
- Retriable user-action errors: `ref.listen` → toast/snackbar on error, user retaps to retry
- First-load errors: render error view with retry button, retry invalidates provider

## Sorting & Filtering

- Simple criteria → `enum`
- Options with properties/behavior → `sealed class`
- Multiple filter properties → dedicated `Filter` class

## Anti-Patterns (flag these)

- Private widget classes in same file (`class _MyHelper extends StatelessWidget`)
- `useState<bool>` for loading states (use provider async state)
- Widget variables defined out of screen order
- `_handleAction(ref, context, controller, user)` with 4+ params outside `build()` (move inside)
- Boolean soup for filtering (`isActive && !isArchived && type == 'premium'`) → typed filter class
