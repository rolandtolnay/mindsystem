---
title: Single Source of Truth
category: state
impact: HIGH
impactDescription: Prevents stale data bugs
tags: state-ownership, provider, derived-state, riverpod
---

## Single Source of Truth (State Ownership)

One owner per state, derive the rest via selectors. Push long-lived state up to providers; keep only ephemeral UI state local.

**Detection signals:**
- Same data stored in both a provider and local widget state
- useEffect hooks syncing local state from provider state
- Two sources of truth could disagree
- Derived data being cached instead of computed

**Incorrect (duplicated state):**

```dart
class ItemScreen extends HookConsumerWidget {
  Widget build(context, ref) {
    final items = ref.watch(itemsProvider);
    // Local state duplicating what provider knows
    final selectedItem = useState<Item?>(null);
    final isEditing = useState(false);

    // Widget caches a derived value
    final totalPrice = useState(0);
    useEffect(() {
      totalPrice.value = items.fold(0, (sum, i) => sum + i.price);
    }, [items]);
  }
}
```

**Correct (single owner, derived values):**

```dart
// Provider owns the state
@riverpod
class ItemsController extends _$ItemsController {
  Item? get selectedItem => state.value?.firstWhereOrNull((i) => i.isSelected);
  int get totalPrice => state.value?.fold(0, (sum, i) => sum + i.price) ?? 0;
}

// Widget only has ephemeral UI state
class ItemScreen extends HookConsumerWidget {
  Widget build(context, ref) {
    final items = ref.watch(itemsProvider);
    final selectedItem = ref.watch(itemsProvider.select((s) => s.selectedItem));
    final isTextFieldFocused = useState(false); // Truly ephemeral
  }
}
```

**Why it matters:**
- No "which value is authoritative?" confusion
- State updates propagate automatically
- Easier debugging: one place to inspect
- Prevents stale data bugs

**Detection questions:**
- Is the same data stored in both a provider and local widget state?
- Are there useEffect hooks syncing local state from provider state?
- Could two sources of truth disagree? What happens then?
- Is there derived data being cached instead of computed?
