---
title: Explicit Type Hierarchies Over Implicit Conventions
category: state
impact: HIGH
impactDescription: Centralizes decision logic
tags: factory, sealed-class, decision-logic, type-safety
---

## Explicit Type Hierarchies Over Implicit Conventions

Use factories to encapsulate decision logic. Widgets receive pre-computed decisions, not raw data to interpret.

**Detection signals:**
- Complex if/else chains determining which widget to render
- Same decision logic duplicated across multiple widgets
- Widgets receive data they only use to make decisions (not to display)
- New requirement would add another boolean parameter

**Incorrect (scattered decision logic):**

```dart
Widget _buildTrailing(BuildContext context, {required bool isExpired, required bool isTutorial}) {
  if (quest.status.isClaimable && quest.isExpired) {
    return QuestClaimButton(quest: quest, isExpired: true);
  }
  if (quest.canClaim) {
    if (isTutorial) {
      return PulsingGlowWrapper(child: QuestClaimButton(quest: quest, isTutorial: true));
    }
    return QuestClaimButton(quest: quest);
  }
  return _buildRewardBadge(context);
}
```

**Correct (factory with type hierarchy):**

```dart
sealed class QuestClaimMode {
  factory QuestClaimMode.fromContext({
    required QuestEntity quest,
    required UserEntity? user,
    required bool isTutorialQuest,
  }) {
    if (quest.status.isClaimable && quest.isExpired) {
      return QuestClaimModeExpired(...);
    }
    if (quest.canClaim) {
      return isTutorialQuest
        ? QuestClaimModeTutorial(...)
        : QuestClaimModeNormal(...);
    }
    return QuestClaimModePending(...);
  }
}

// Widget becomes a simple switch
Widget _buildTrailing() => switch (claimMode) {
  QuestClaimModePending() => QuestRewardDisplay(...),
  QuestClaimModeTutorial() => _wrapWithTutorialEffects(QuestClaimButton(mode: claimMode)),
  QuestClaimModeNormal() || QuestClaimModeExpired() => QuestClaimButton(mode: claimMode),
};
```

**Why it matters:**
- Decision logic lives in one place (the factory)
- Widgets receive pre-computed decisions, not raw data to interpret
- Adding new modes is explicit and compiler-checked
- Testing is clearer: test the factory, then test each mode's rendering

**Detection questions:**
- Are there complex if/else chains determining which widget to render?
- Is the same decision logic duplicated across multiple widgets?
- Do widgets receive data they only use to make decisions (not to display)?
- Would a new requirement add another boolean parameter?
