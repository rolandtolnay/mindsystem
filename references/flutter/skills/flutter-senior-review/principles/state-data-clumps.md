---
title: Data Clumps to Records
category: state
impact: MEDIUM-HIGH
impactDescription: Reduces parameter proliferation
tags: record, typedef, data-modeling, parameters
---

## Data Clumps to Records

Group parameters that travel together into typed objects (records or classes).

**Detection signals:**
- Same 3+ parameters appear in multiple function signatures
- Parameters are logically related (always used together)
- Adding a new related field requires updating many signatures
- Bugs from passing parameters in the wrong order

**Incorrect (repeated parameter groups):**

```dart
void showReward(int baseReward, int? boostedReward, int? multiplier) { ... }
void displayBadge(int baseReward, int? boostedReward, int? multiplier) { ... }
void logClaim(int baseReward, int? boostedReward, int? multiplier) { ... }

Widget buildReward({
  required int baseReward,
  int? boostedReward,
  int? multiplier,
}) { ... }
```

**Correct (typed record/class):**

```dart
// Record for simple data grouping
typedef RewardBonus = ({int base, int? boosted, int? multiplier});

// Or class if behavior is needed
class RewardCalculation {
  final int base;
  final int? boosted;
  final int? multiplier;

  bool get hasBonus => multiplier != null;
  int get displayAmount => boosted ?? base;
}

// Clean call sites
void showReward(RewardBonus bonus) { ... }
Widget buildReward({required RewardBonus bonus}) { ... }
```

**Why it matters:**
- Single place to add new related fields
- Impossible to pass parameters in wrong order
- Semantic meaning is clear
- Reduces parameter count everywhere

**Detection questions:**
- Do the same 3+ parameters appear in multiple function signatures?
- Are parameters logically related (always used together)?
- Would adding a new related field require updating many signatures?
- Are there bugs from passing parameters in the wrong order?
