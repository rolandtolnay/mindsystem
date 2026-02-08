# Flutter Hooks

## Widget Types

- `HookWidget`: hooks, no Riverpod
- `HookConsumerWidget`: hooks + Riverpod `WidgetRef` (default for screens)
- `HookBuilder`: hooks in a small subtree (incremental migration)

## Hook Rules

- Call hooks unconditionally at top of `build()` — no `if`, loops, early returns
- Keep hook call order stable across rebuilds
- Never call hooks inside callbacks (`onPressed`, `onTap`, builder lambdas)

## Conventions

- Group `use*` calls at top of `build()`, then callbacks, then return widgets
- Always supply dependencies for `useEffect`/`useMemoized` — avoid "runs every build"
- `const []` for "run once" effects
- Controllers always from `use*Controller` hooks
- Listeners always have cleanup return
- Sanitize input at capture: `controller.text.trim()`
- Keep temporary UI state local — don't promote to providers unless multiple screens need it
- Business logic in providers/services, not in `build()`

## Migration: StatefulWidget → Hooks

| StatefulWidget | Hook replacement |
|---|---|
| `StatefulWidget` | `HookWidget` |
| `ConsumerStatefulWidget` | `HookConsumerWidget` |
| `late final TextEditingController` | `useTextEditingController()` |
| `late final AnimationController` | `useAnimationController(duration: ...)` |
| `late final FocusNode` | `useFocusNode()` |
| `late final ScrollController` | `useScrollController()` |
| `late final PageController` | `usePageController()` |
| `bool flag` + `setState` | `useState(false)` |
| Mutable non-visual state | `useRef<T>(initial)` |
| `initState()` sync | `useInit(() { ... })` |
| `initState()` async | `useInitAsync(() async { ... })` |
| `dispose()` | `useEffect` cleanup return |
| `didUpdateWidget()` | `useEffect` keyed by changed inputs |
| `addListener` in `initState` | `useEffect` returning cleanup |
| `GlobalKey` / expensive objects | `useMemoized(...)` |

## Project Helper Hooks

### `useInit` — sync run-once

```dart
useInit(() {
  trackScreenView('PaymentDetail');
});
```

### `useInitAsync` — async run-once (avoids frame timing issues)

```dart
useInitAsync(() async {
  await ref.read(someProvider.notifier).load();
});
```

Use when setting controller values after first build or calling notifiers that synchronously emit state.

### `useAsyncEffect` — async effect with dependencies

```dart
useAsyncEffect(() async {
  if (customer == null) return;
  nameController.text = customer.name ?? '';
}, [customer]);
```

### `useAsyncEffectDisposing` — async effect with cleanup

```dart
useAsyncEffectDisposing(() async {
  void listener() {}
  controller.addListener(listener);
  return () => controller.removeListener(listener);
}, [controller]);
```

## Standard Hooks

- Local state: `useState`, `useRef`, `useValueNotifier`
- Owned resources: `useTextEditingController`, `useFocusNode`, `useScrollController`, `usePageController`, `useAnimationController`
- Lifecycle: `useEffect`, `useInit`, `useInitAsync`
- Rebuild on changes: `useListenable`, `useValueListenable`
- Stable instances: `useMemoized`

## Typical Structure

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

## Riverpod + Hooks

- `ref.watch`/`ref.read`/`ref.listen` work the same in `HookConsumerWidget`
- Sync provider values into controllers via keyed effect:

```dart
final customer = ref.watch(customerProvider(id)).value;
final nameController = useTextEditingController();

useEffect(() {
  nameController.text = customer?.name ?? '';
  return null;
}, [customer]);
```

- Centralized error handling: `ref.listenOnError(provider)` or fallback:

```dart
ref.listen(createPaymentProvider, (prev, next) {
  if (next.hasError && prev?.hasError != true) {
    showError(next.error);
  }
});
```

- Condition-based actions: `ref.listenForCondition(provider, condition, action)` or fallback:

```dart
ref.listen(createCustomerProvider, (prev, next) {
  final didSucceed = next.hasValue && next.value != null;
  final justSucceeded = didSucceed && (prev?.hasValue != true);
  if (justSucceeded) Navigator.of(context).maybePop();
});
```

## Pattern Templates

### Forms

- `useListenable(controller)` if button state reads `controller.text`
- `useMemoized` for `GlobalKey`
- `useInitAsync` for async prefill
- `.trim()` on submit

### Animations

```dart
final controller = useAnimationController(duration: const Duration(milliseconds: 250));
useInitAsync(() async => controller.forward());
```

Listeners always return cleanup from `useEffect`.

### Lists (Sorting/Filtering)

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

```dart
final filters = useState<Set<FilterType>>({...initialFilters});
void toggle(FilterType t) {
  final next = {...filters.value};
  next.contains(t) ? next.remove(t) : next.add(t);
  filters.value = next;
}
```

### Search Input

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

### Sync External State

```dart
final expanded = useState(widgetExpanded);
useEffect(() {
  expanded.value = widgetExpanded;
  return null;
}, [widgetExpanded]);
```

### Keep Alive in Tabs

```dart
HookBuilder(
  builder: (context) {
    useAutomaticKeepAlive();
    return child;
  },
);
```

## Custom Hooks

Function-based composition preferred:

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

Class-based `Hook`/`HookState` only when custom resource create/dispose semantics required.

## Anti-Patterns (flag these)

- Conditional hook calls, hooks in callbacks, changing hook order
- Missing dependencies in `useEffect`/`useMemoized` (stale closures)
- Listeners without cleanup returns
- Recreating `GlobalKey`/`Tween`/expensive objects every build (use `useMemoized`)
- Mutating collections in place with `useState` (assign new instance)
