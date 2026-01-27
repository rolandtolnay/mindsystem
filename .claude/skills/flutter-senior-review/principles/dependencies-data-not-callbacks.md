---
title: Reduce Coupling Through Data
category: dependencies
impact: MEDIUM-HIGH
impactDescription: Stabilizes widget APIs
tags: coupling, parameters, typed-objects, widget-api
---

## Reduce Coupling Through Data, Not Callbacks

Pass typed objects, not callback parades. Child widgets receive a single typed object that encapsulates all the data they need.

**Detection signals:**
- Widgets have 4+ parameters beyond key and callbacks
- Boolean flags being passed through multiple widget layers
- Changing a child's behavior requires changing the parent's call site
- Parameters that are only used in some conditions

**Incorrect (flag parade):**

```dart
QuestClaimButton(
  quest: quest,
  onSuccess: onClaimSuccess,
  isExpired: isExpired,
  isTutorial: isTutorial,
  bonus: bonus,
  showMultiplier: showMultiplier,
  isPremiumUser: isPremiumUser,
)
```

**Correct (typed data object):**

```dart
// Data object encapsulates all context
sealed class QuestClaimMode {
  final QuestEntity quest;
  final RewardBonus? bonus;

  const QuestClaimMode({required this.quest, this.bonus});

  factory QuestClaimMode.fromContext({
    required QuestEntity quest,
    required UserEntity? user,
    required bool isTutorialQuest,
  }) {
    // Decision logic centralized here
    if (quest.isExpired) return QuestClaimModeExpired(quest: quest);
    if (isTutorialQuest) return QuestClaimModeTutorial(quest: quest);
    return QuestClaimModeNormal(
      quest: quest,
      bonus: user?.applyRewardBonus(quest.reward),
    );
  }
}

// Clean widget API
QuestClaimButton(
  mode: QuestClaimMode.fromContext(quest: quest, user: user, isTutorial: isTutorial),
  onSuccess: onClaimSuccess,
)
```

**Why it matters:**
- Child widget's API is stable even as requirements change
- Parent doesn't need to know child's internal decision logic
- Data dependencies are explicit in the mode type
- Easier to test: create mode objects directly

**Detection questions:**
- Do widgets have 4+ parameters beyond key and callbacks?
- Are boolean flags being passed through multiple widget layers?
- Does changing a child's behavior require changing the parent's call site?
- Are there parameters that are only used in some conditions?
