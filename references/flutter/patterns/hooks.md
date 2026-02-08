# Flutter Hooks Usage Guide

This guide documents how we use `flutter_hooks` in a production Flutter app, including a few “style rules” and helper hooks that reduce common bugs (frame timing issues, stale closures, leaked listeners). It’s written to be reusable in other projects regardless of folder structure.

## TL;DR for LLM Agents

When migrating `StatefulWidget` / `ConsumerStatefulWidget` to hooks:

1. Convert widget type → `HookWidget` / `HookConsumerWidget`.
2. Delete the `State` class.
3. Replace `initState` → `useInit()` or `useInitAsync()` (preferred) or `useEffect(..., const [])`.
4. Replace `dispose` → `useEffect` cleanup return.
5. Replace `setState` → `useState` (UI state) or `useRef` (non-UI state).
6. Replace controllers/focus/scroll/page/animation `late final` → `use*Controller()` / `useFocusNode()` / etc.
7. If you read `controller.text` in UI, add `useListenable(controller)`.
8. Always trim user-entered strings at capture time (`controller.text.trim()`).

## Setup

- Add `flutter_hooks` to `pubspec.yaml`.
- If you use Riverpod, add `hooks_riverpod` and prefer `HookConsumerWidget` for screens.

Imports:

```dart
import 'package:flutter_hooks/flutter_hooks.dart';
// If using Riverpod:
import 'package:hooks_riverpod/hooks_riverpod.dart';
```

## Widget Type Selection

- `HookWidget`: hooks, no Riverpod `ref`.
- `HookConsumerWidget`: hooks + Riverpod `WidgetRef` (default for screens).
- `HookBuilder`: use hooks in a small subtree (nice for incremental migration).

## Hook Rules (Non-Negotiable)

- Call hooks unconditionally at the top of `build` (no `if`, loops, early returns).
- Keep hook call order stable across rebuilds.
- Never call hooks inside callbacks (`onPressed`, `onTap`, builder lambdas, etc.).

## Conventions We Follow (Style Guidelines)

- **Keep `build` mostly pure**: UI composition + hook wiring + calling providers. Put business logic in providers/services.
- **Declare hooks first**: group `use*` calls at the top of `build`, then define callbacks, then return widgets.
- **Dependencies are explicit**: always supply dependencies for `useEffect`/`useMemoized` (avoid “runs every build”).
- **Prefer `const []`** for “run once” effects to make intent obvious.
- **Memoize unstable objects**: `GlobalKey`, `Tween`, expensive derived lists, and callbacks that should not change each rebuild.
- **Controllers are owned by hooks**: if a controller is created in `build`, it should come from a `use*Controller` hook.
- **Listeners always have cleanup**: any `addListener`/subscription must be paired with a cleanup return.
- **Input capture is sanitized**: `controller.text.trim()` (and other normalization) happens at the point of submission.
- **UI local state stays local**: don’t promote temporary UI state into global providers unless multiple screens need it.

## Migration Checklist (StatefulWidget → Hooks)

1. Convert `StatefulWidget` → `HookWidget` (or `ConsumerStatefulWidget` → `HookConsumerWidget`).
2. Move `initState` logic:
   - Sync “run once” setup → `useInit`.
   - Async “run once” setup → `useInitAsync` (preferred in this codebase).
3. Move `didUpdateWidget` logic → `useEffect` keyed on changed inputs.
4. Replace `setState`:
   - UI state → `useState<T>()`.
   - Mutable, non-visual state → `useRef<T>()`.
5. Replace manual disposal:
   - `TextEditingController` → `useTextEditingController`.
   - `AnimationController` → `useAnimationController`.
   - `ScrollController` → `useScrollController`.
   - `PageController` → `usePageController`.
   - `FocusNode` → `useFocusNode`.
6. Replace listeners:
   - `addListener` in `initState` → `useEffect` that returns cleanup.
7. Add memoization where needed:
   - `GlobalKey<FormState>` / `GlobalKey<NavigatorState>` → `useMemoized`.
   - Expensive transforms (sorting/filtering) → `useMemoized` keyed by inputs.

## Project Helper Hooks (Recommended to Keep)

These wrappers are used throughout the app. If you’re starting a new project, keep them (or equivalent) because they encode good defaults.

### `useInit`

Runs a callback synchronously once on mount.

```dart
useInit(() {
  trackScreenView('PaymentDetail');
});
```

Use when:
- You need “run once” setup that is safe to do synchronously.

### `useInitAsync`

Runs a callback once on mount, scheduled asynchronously (e.g., via `Future.microtask`).

```dart
useInitAsync(() async {
  await ref.read(someProvider.notifier).load();
});
```

Use when:
- You need to set controller values / state after first build.
- You want to avoid “setState during build” / frame timing issues.
- You’re calling provider notifiers that may synchronously emit state.

### `useAsyncEffect`

An async-friendly effect that re-runs when dependencies change.

```dart
useAsyncEffect(() async {
  if (customer == null) return;
  nameController.text = customer.name ?? '';
}, [customer]);
```

Use when:
- You must `await` inside the effect, or you want an explicit “async effect” abstraction.

### `useAsyncEffectDisposing`

Async effect that supports returning a cleanup function (including async setup that needs sync cleanup).

```dart
useAsyncEffectDisposing(() async {
  void listener() {}
  controller.addListener(listener);
  return () => controller.removeListener(listener);
}, [controller]);
```

Use when:
- You set up listeners/subscriptions and want a single pattern for async setup + cleanup.

## Standard Hooks We Use Most

Most widgets only need:
- Local state: `useState`, `useRef`, `useValueNotifier`.
- Owned resources: `useTextEditingController`, `useFocusNode`, `useScrollController`, `usePageController`, `useAnimationController`.
- Lifecycle: `useEffect` (plus `useInit` / `useInitAsync` for “run once”).
- Rebuild on changes: `useListenable` / `useValueListenable`.
- Stable instances: `useMemoized`.

Typical structure (hooks first, then callbacks, then UI):

```dart
class Example extends HookConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final formKey = useMemoized(GlobalKey<FormState>.new);
    final nameController = useTextEditingController();
    final submitting = useState(false);

    useListenable(nameController);

    useInitAsync(() async {
      final initial = await ref.read(initialDataProvider.future);
      nameController.text = initial.name ?? '';
    });

    Future<void> submit() async {
      submitting.value = true;
      try {
        await ref.read(saveProvider.notifier).save(name: nameController.text.trim());
      } finally {
        submitting.value = false;
      }
    }

    return Form(
      key: formKey,
      child: Column(
        children: [
          TextFormField(controller: nameController),
          ElevatedButton(
            onPressed: submitting.value ? null : submit,
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}
```

## Riverpod + Hooks (If Applicable)

- `ref.watch`/`ref.read`/`ref.listen` work the same in `HookConsumerWidget`.
- Keep side-effects (toasts, navigation, analytics) in one place via `ref.listen` (or a project helper like `ref.listenOnError` / `ref.listenForCondition` if available).
- When syncing provider values into controllers, use an effect keyed by the provider value.

```dart
final customer = ref.watch(customerProvider(id)).value;
final nameController = useTextEditingController();

useEffect(() {
  nameController.text = customer?.name ?? '';
  return null;
}, [customer]);
```

### Centralized Error Handling

Preferred (if your project defines it):

```dart
ref.listenOnError(createPaymentProvider);
```

Generic Riverpod fallback:

```dart
ref.listen(createPaymentProvider, (prev, next) {
  if (next.hasError && prev?.hasError != true) {
    showError(next.error);
  }
});
```

### Condition-Based Actions (Navigation, Toasts)

Preferred (if your project defines it):

```dart
ref.listenForCondition(
  createCustomerProvider,
  (state) => state.hasValue && state.value != null,
  (_) => Navigator.of(context).maybePop(),
);
```

Generic Riverpod fallback:

```dart
ref.listen(createCustomerProvider, (prev, next) {
  final didSucceed = next.hasValue && next.value != null;
  final justSucceeded = didSucceed && (prev?.hasValue != true);
  if (justSucceeded) Navigator.of(context).maybePop();
});
```

## Patterns by Category (Short Templates)

### Forms

- Use `useListenable(controller)` if button enabled-state reads `controller.text`.
- Use `useMemoized` for `GlobalKey`.
- Use `useInitAsync` for async prefill.
- Always `.trim()` on submit.

### Animations

```dart
final controller = useAnimationController(duration: const Duration(milliseconds: 250));
useInitAsync(() async => controller.forward());
```

If you add listeners, always return cleanup from `useEffect`.

### Lists (Derived Sorting/Filtering)

Prefer non-mutating transforms (don’t `..sort()` shared lists). If you have a `.sorted(...)` extension, use it:

```dart
final items = ref.watch(paymentListProvider).value ?? const <Payment>[];
final sorted = useMemoized(() => items.sorted((a, b) => b.createdAt.compareTo(a.createdAt)), [items]);
```

### PageView / Tabs

```dart
final pageController = usePageController();
final selectedIndex = useState(0);
final animating = useRef(false);

useAsyncEffect(() async {
  if (animating.value) return;
  animating.value = true;
  await pageController.animateToPage(
    selectedIndex.value,
    duration: const Duration(milliseconds: 250),
    curve: Curves.easeOut,
  );
  animating.value = false;
}, [selectedIndex.value]);
```

### Filter Toggles

Avoid mutating sets/lists in place; assign a new instance:

```dart
final filters = useState<Set<FilterType>>({...initialFilters});
void toggle(FilterType t) {
  final next = {...filters.value};
  next.contains(t) ? next.remove(t) : next.add(t);
  filters.value = next;
}
```

### Search Input (Clear Button + Optional External Focus)

```dart
final controller = useTextEditingController();
final focusNode = widgetFocusNode ?? useFocusNode();

useListenable(controller);

return TextField(
  controller: controller,
  focusNode: focusNode,
  decoration: InputDecoration(
    suffixIcon: controller.text.isNotEmpty
        ? IconButton(icon: const Icon(Icons.clear), onPressed: controller.clear)
        : null,
  ),
);
```

### Expand/Collapse Synced With an Input

```dart
final expanded = useState(widgetExpanded);

useEffect(() {
  expanded.value = widgetExpanded;
  return null;
}, [widgetExpanded]);
```

### Keep State Alive in Tabs/Pages

```dart
HookBuilder(
  builder: (context) {
    useAutomaticKeepAlive();
    return child;
  },
);
```

## Creating Custom Hooks

Prefer function-based custom hooks (composition of existing hooks):

```dart
T? usePrevious<T>(T value) {
  final ref = useRef<T?>(null);
  useEffect(() {
    ref.value = value;
    return null;
  }, [value]);
  return ref.value;
}
```

Use class-based `Hook`/`HookState` only when you must create/dispose a resource with custom semantics.

## Anti-Patterns to Avoid

- Conditional hook calls, hooks in callbacks, or changing hook order.
- Missing dependencies in `useEffect`/`useMemoized` (stale closures).
- Adding listeners/subscriptions without cleanup returns.
- Recreating `GlobalKey`/`Tween`/expensive objects every rebuild (use `useMemoized`).
- Mutating collections in place when using `useState` (assign a new instance).

## Quick Reference Table

| StatefulWidget pattern | Hook replacement |
|---|---|
| `late final TextEditingController c;` | `final c = useTextEditingController();` |
| `late final AnimationController c;` | `final c = useAnimationController(duration: ...);` |
| `late final FocusNode f;` | `final f = useFocusNode();` |
| `late final ScrollController s;` | `final s = useScrollController();` |
| `late final PageController p;` | `final p = usePageController();` |
| `bool flag = false;` + `setState` | `final flag = useState(false);` |
| “mutable but not visual” | `final x = useRef<T>(initial);` |
| `initState()` | `useInit()` / `useInitAsync()` / `useEffect(..., const [])` |
| `dispose()` | `useEffect` cleanup return |
| `didUpdateWidget()` | `useEffect` keyed by changed inputs |
