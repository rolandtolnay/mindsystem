---
title: Isolate Feature Responsibility (Wrapper Pattern)
category: structure
impact: HIGH
impactDescription: Features become removable
tags: wrapper, composition, feature-isolation, widget-extraction
---

## Isolate Feature Responsibility (Wrapper Pattern)

Extract optional feature logic into wrapper components. The wrapper owns all feature-specific state; the core component doesn't know the feature exists.

**Detection signals:**
- More than 30% of a widget's code dedicated to one optional feature
- Removing a feature requires deleting scattered lines throughout the file
- Multiple `if (featureEnabled)` checks spread across the widget
- State variables only used by one feature

**Incorrect (scattered feature logic):**

```dart
class QuestListScreen extends HookConsumerWidget {
  Widget build(context, ref) {
    // 50 lines of tutorial-specific state management
    final tutorialKey = useMemoized(GlobalKey.new);
    final overlayVisible = useState(true);
    final cutoutRect = useState<Rect?>(null);

    // Tutorial measurement logic mixed with list logic
    useEffect(() {
      if (isTutorialActive) {
        // 30 lines of tutorial position measurement
      }
    });

    // Main list rendering polluted with tutorial checks
    return Stack(
      children: [
        questList,
        if (showTutorialOverlay) TutorialOverlay(...),
      ],
    );
  }
}
```

**Correct (wrapper pattern):**

```dart
// Tutorial logic fully encapsulated
class TutorialQuestSpotlight extends HookConsumerWidget {
  final Widget Function(BuildContext, {GlobalKey? tutorialKey}) builder;

  Widget build(context, ref) {
    // All tutorial state lives here
    final tutorialKey = useMemoized(GlobalKey.new);
    final overlayVisible = useState(true);
    final cutoutRect = useState<Rect?>(null);

    // Core list doesn't know tutorials exist
    return Stack(
      children: [
        builder(context, tutorialKey: tutorialKey),
        if (overlayVisible.value) TutorialOverlay(cutoutRect: cutoutRect.value),
      ],
    );
  }
}

// Clean core component
class QuestListScreen extends HookConsumerWidget {
  Widget build(context, ref) {
    return TutorialQuestSpotlight(
      builder: (context, {tutorialKey}) => _buildQuestList(tutorialKey),
    );
  }
}
```

**Why it matters:**
- Feature can be disabled/removed by removing one wrapper
- Core component remains focused and testable
- Feature logic is cohesive and isolated
- Multiple features can compose without polluting each other

**Detection questions:**
- Is more than 30% of a widget's code dedicated to one optional feature?
- Would removing a feature require deleting scattered lines throughout the file?
- Are there multiple `if (featureEnabled)` checks spread across the widget?
- Does the widget have state variables only used by one feature?
