---
title: Make Invalid States Unrepresentable
category: state
impact: CRITICAL
impactDescription: Eliminates entire class of bugs
tags: sealed-class, boolean-flags, state-modeling, type-safety
---

## Make Invalid States Unrepresentable

Replace boolean flag combinations with sealed class hierarchies where each variant represents exactly one valid state.

**Detection signals:**
- 3+ boolean parameters passed together
- Same boolean checks repeated in multiple places
- if/else chains checking flag combinations
- Some flag combinations would cause undefined behavior

**Incorrect (boolean flag explosion):**

```dart
Widget build() {
  final isLoading = ...;
  final isExpired = ...;
  final isTutorial = ...;
  final hasBonus = ...;
  // What happens when isTutorial && isExpired?
  // What about isLoading && hasBonus && isTutorial?
}
```

**Correct (sealed class hierarchy):**

```dart
sealed class ItemMode {
  const ItemMode();
}
final class ItemModeNormal extends ItemMode { ... }
final class ItemModeTutorial extends ItemMode { ... }
final class ItemModeExpired extends ItemMode { ... }
```

**Why it matters:**
- Compiler enforces exhaustive handling via switch expressions
- New states added explicitly, not as boolean combinations
- Impossible to create invalid state combinations
- Self-documenting: sealed class shows all possible states

**Detection questions:**
- Are there 3+ boolean parameters being passed together?
- Do you see the same boolean checks repeated in multiple places?
- Are there if/else chains checking combinations of flags?
- Could some flag combinations cause undefined behavior?
