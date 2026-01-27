# Flutter Senior Review

**Version 1.0.0**
Forgeblast
January 2026

> This document is optimized for AI agents and LLMs. Principles are organized by category and prioritized by structural impact.

---

## Abstract

Senior engineering principles for Flutter/Dart code reviews. Uses 3 core lenses (State Modeling, Responsibility Boundaries, Abstraction Timing) backed by 12 detailed principles organized into 4 categories. Each principle includes detection signals, smell examples, senior solutions, and Dart-specific patterns. Focus is on structural improvements that make code evolvable, not just working.

---

## Table of Contents

1. [Core Lenses](#1-core-lenses)
   - 1.1 [State Modeling](#11-state-modeling)
   - 1.2 [Responsibility Boundaries](#12-responsibility-boundaries)
   - 1.3 [Abstraction Timing](#13-abstraction-timing)

2. [State & Type Safety](#2-state--type-safety) - **CRITICAL**
   - 2.1 [Make Invalid States Unrepresentable](#21-make-invalid-states-unrepresentable)
   - 2.2 [Explicit Type Hierarchies](#22-explicit-type-hierarchies)
   - 2.3 [Single Source of Truth](#23-single-source-of-truth)
   - 2.4 [Data Clumps to Records](#24-data-clumps-to-records)

3. [Structure & Composition](#3-structure--composition) - **HIGH**
   - 3.1 [Isolate Feature Responsibility](#31-isolate-feature-responsibility)
   - 3.2 [Extract Shared Visual Patterns](#32-extract-shared-visual-patterns)
   - 3.3 [Composition Over Configuration](#33-composition-over-configuration)

4. [Dependencies & Flow](#4-dependencies--flow) - **MEDIUM-HIGH**
   - 4.1 [Reduce Coupling Through Data](#41-reduce-coupling-through-data)
   - 4.2 [Provider Tree Architecture](#42-provider-tree-architecture)
   - 4.3 [Temporal Coupling](#43-temporal-coupling)

5. [Pragmatism](#5-pragmatism) - **MEDIUM**
   - 5.1 [Speculative Generality](#51-speculative-generality)
   - 5.2 [Consistent Error Handling](#52-consistent-error-handling)

---

## Senior Mindset

Junior and mid-level engineers ask: **"Does this code work?"**
Senior engineers ask: **"How will this code change? What happens when requirements shift?"**

This distinction drives everything. Code that "works" today becomes a liability when:
- A new state is added and 5 files need coordinated updates
- A feature toggle requires touching code scattered across the codebase
- A bug fix in one place breaks assumptions elsewhere

Focus on **structural issues that compound over time** - the kind that turn "add a simple feature" into "refactor half the codebase first."

---

## 1. Core Lenses

Apply these three lenses to every review. They catch 80% of structural issues.

### 1.1 State Modeling

**Question:** Can this code represent invalid states?

Look for:
- Multiple boolean flags (2^n possible states, many invalid)
- Primitive obsession (stringly-typed status, magic numbers)
- Same decision logic repeated in multiple places

**Senior pattern:** Sealed classes where each variant is a valid state. Factory methods that encapsulate decision logic. Compiler-enforced exhaustive handling.

---

### 1.2 Responsibility Boundaries

**Question:** If I remove/modify feature X, how many files change?

Look for:
- Optional feature logic scattered throughout a parent component
- Widgets with 6+ parameters (doing too much)
- Deep callback chains passing flags through layers

**Senior pattern:** Wrapper components for optional features. Typed data objects instead of flag parades. Each widget has one job.

---

### 1.3 Abstraction Timing

**Question:** Is this abstraction earned or speculative?

Look for:
- Interfaces with only one implementation
- Factories that create only one type
- "Flexible" config that's never varied
- BUT ALSO: Duplicated code that should be unified

**Senior pattern:** Abstract when you have 2-3 concrete cases, not before. Extract when duplication causes bugs or drift, not for aesthetics.

---

## 2. State & Type Safety

**Impact: CRITICAL**

Issues with state modeling compound rapidly. Invalid state combinations cause bugs that are hard to reproduce and fix.

### 2.1 Make Invalid States Unrepresentable

**Impact: CRITICAL (Eliminates entire class of bugs)**

Multiple boolean flags that create 2^n possible states, where many combinations are invalid or nonsensical.

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

---

### 2.2 Explicit Type Hierarchies

**Impact: HIGH (Centralizes decision logic)**

Complex if/else chains determining behavior scattered across widgets rather than encoded in the type system.

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

---

### 2.3 Single Source of Truth

**Impact: HIGH (Prevents stale data bugs)**

Same state tracked in multiple places - local useState duplicating provider state, widgets caching derived values.

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

---

### 2.4 Data Clumps to Records

**Impact: MEDIUM-HIGH (Reduces parameter proliferation)**

Same 3-4 parameters appear together repeatedly across methods and constructors.

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
```

**Why it matters:**
- Single place to add new related fields
- Impossible to pass parameters in wrong order
- Semantic meaning is clear
- Reduces parameter count everywhere

---

## 3. Structure & Composition

**Impact: HIGH**

Structural issues make features hard to add, remove, or modify independently.

### 3.1 Isolate Feature Responsibility

**Impact: HIGH (Features become removable)**

A feature's logic is woven throughout a parent component rather than encapsulated.

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

    useEffect(() {
      if (isTutorialActive) {
        // 30 lines of tutorial position measurement
      }
    });

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
    // Core list doesn't know tutorials exist
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

---

### 3.2 Extract Shared Visual Patterns

**Impact: MEDIUM-HIGH (Guarantees consistency)**

Similar UI code duplicated across widgets with minor variations and subtle inconsistencies.

**Detection signals:**
- Similar Container/decoration patterns across multiple widgets
- Visual elements (colors, padding, borders) vary based on state
- Design change would require updating multiple files
- Subtle inconsistencies between similar UI elements

**Incorrect (duplicated patterns):**

```dart
// In QuestClaimButton
Container(
  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  decoration: BoxDecoration(
    color: isExpired ? AppColors.gray400 : AppColors.forge,
    borderRadius: BorderRadius.circular(20),
  ),
  child: Row(children: [Text('grape'), Text('$reward')]),
)

// In QuestListTile (slightly different)
Container(
  padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
  decoration: BoxDecoration(
    borderRadius: BorderRadius.circular(20),
    border: Border.all(color: ...),
  ),
  child: Row(children: [Text('grape'), Text('$reward')]),
)
```

**Correct (shared widget with variants):**

```dart
enum QuestRewardStyle { filled, outlined, disabled }

class QuestRewardDisplay extends StatelessWidget {
  final int reward;
  final QuestRewardStyle style;

  Widget build(context) {
    return Container(
      decoration: style.buildDecoration(context),
      child: Row(children: [Text('grape'), Text('$reward', style: style.buildTextStyle(context))]),
    );
  }
}

extension on QuestRewardStyle {
  BoxDecoration buildDecoration(BuildContext context) => switch (this) {
    QuestRewardStyle.filled => BoxDecoration(color: AppColors.forge, ...),
    QuestRewardStyle.outlined => BoxDecoration(border: Border.all(...), ...),
    QuestRewardStyle.disabled => BoxDecoration(color: AppColors.gray400, ...),
  };
}
```

**Why it matters:**
- Visual consistency is guaranteed
- Style changes propagate automatically
- New variants are added in one place
- Reduces widget file sizes significantly

---

### 3.3 Composition Over Configuration

**Impact: MEDIUM (Simplifies widget APIs)**

Giant widgets with dozens of boolean flags - "god widgets" that handle every case through configuration.

**Detection signals:**
- Widget has more than 6-8 parameters
- Boolean parameters that are mutually exclusive
- Widget is really 3 different widgets pretending to be 1
- Adding a new variant would require another boolean flag

**Incorrect (god widget):**

```dart
AppButton(
  label: 'Submit',
  isPrimary: true,
  isSecondary: false,
  isDestructive: false,
  isLoading: false,
  isDisabled: false,
  showIcon: true,
  iconPosition: IconPosition.left,
  size: ButtonSize.medium,
  // ... 10 more parameters
)
```

**Correct (composed widgets):**

```dart
// Composition of focused widgets
PrimaryButton(
  onPressed: handleSubmit,
  child: Row(
    children: [
      Icon(Icons.check),
      SizedBox(width: 8),
      Text('Submit'),
    ],
  ),
)

// Or slot-based API for common patterns
PrimaryButton.icon(
  icon: Icons.check,
  label: 'Submit',
  onPressed: handleSubmit,
)
```

**Why it matters:**
- Each widget has one job
- New variants don't bloat existing widgets
- Easier to understand and test
- Flexible: compose for custom needs, use shortcuts for common ones

---

## 4. Dependencies & Flow

**Impact: MEDIUM-HIGH**

Coupling and dependency issues make code changes ripple unexpectedly.

### 4.1 Reduce Coupling Through Data

**Impact: MEDIUM-HIGH (Stabilizes APIs)**

Parent widgets pass many callbacks and control flags to children, creating tight coupling.

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
)
```

**Correct (typed data object):**

```dart
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

---

### 4.2 Provider Tree Architecture

**Impact: MEDIUM (Clarifies data flow)**

Flat provider structure where many providers read from many others with no clear hierarchy.

**Mental model:**
- **Root providers**: Match app lifecycle, never disposed. Hold core entities (user, games, quests). Referenced from many places.
- **Branch providers**: Combine/filter/transform core data. May become "core" as app grows.
- **Leaf providers**: Screen-specific or ephemeral. Depend on branches, rarely watched by other providers.

**Detection signals:**
- Can't draw the provider dependency graph as a tree
- Circular or confusing dependency chains
- "Leaf" providers being watched by other providers
- Provider doing too much (should split into root + branch)

**Correct (tree structure):**

```dart
// Root (core entities, keepAlive: true)
@Riverpod(keepAlive: true)
Future<User> user(Ref ref) => ...;

@Riverpod(keepAlive: true)
Future<List<Quest>> quests(Ref ref) => ...;

// Branch (derived/filtered, may become core as app grows)
@riverpod
Future<List<Quest>> squadQuests(Ref ref) async {
  final quests = await ref.watch(questsProvider.future);
  return quests.where((q) => q.type == QuestType.squad).toList();
}

// Leaf (screen-specific, ephemeral)
@riverpod
class SquadQuestScreenState extends _$SquadQuestScreenState {
  // Only watches branch providers, never watched by others
}
```

**Why it matters:**
- Clear mental model of data flow
- Predictable rebuild scope
- Easier to add new derived providers
- Natural place for each piece of logic

---

### 4.3 Temporal Coupling

**Impact: MEDIUM (Catches misuse at compile time)**

Operations must happen in a specific order, but nothing enforces that order.

**Detection signals:**
- Methods that must be called before others
- Comments like "must call X first" or "call after Y"
- Objects can be in an "invalid" state between operations
- Tests have setup steps that could be forgotten

**Incorrect (implicit sequence):**

```dart
class PaymentProcessor {
  void init() { ... }
  void setAmount(int amount) { ... }
  void setCustomer(Customer c) { ... }
  Future<void> process() { ... } // Must call init, setAmount, setCustomer first!
}

// Easy to misuse:
final processor = PaymentProcessor();
processor.process(); // Boom - forgot to init
```

**Correct (type-enforced sequence):**

```dart
// Builder pattern enforces sequence
class PaymentBuilder {
  PaymentBuilder withAmount(int amount) => ...;
  PaymentBuilder withCustomer(Customer c) => ...;
  Payment build() => ...; // Only callable when all required fields set
}

// Or use types to enforce state
class UninitializedProcessor { InitializedProcessor init() => ...; }
class InitializedProcessor { Future<Result> process(int amount, Customer c) => ...; }
```

**Why it matters:**
- Compiler catches misuse, not runtime
- Self-documenting: types show valid sequences
- Impossible to forget required steps
- Easier onboarding for new developers

---

## 5. Pragmatism

**Impact: MEDIUM**

Over-engineering and inconsistency create unnecessary complexity.

### 5.1 Speculative Generality

**Impact: MEDIUM (Reduces unnecessary complexity)**

Abstractions added for hypothetical future needs that may never materialize.

**Detection signals:**
- Interface with only one implementation
- Factory that only creates one type
- Configuration options no one uses
- Abstraction added "in case we need it later"

**Incorrect (premature abstraction):**

```dart
// "We might need different storage backends someday"
abstract class StorageStrategy { ... }
class LocalStorageStrategy implements StorageStrategy { ... }
class StorageFactory {
  static StorageStrategy create(StorageType type) => switch (type) {
    StorageType.local => LocalStorageStrategy(), // Only one ever used
  };
}
```

**Correct (direct usage):**

```dart
// Just use the thing directly
class LocalStorage {
  Future<void> save(String key, String value) => ...;
  Future<String?> load(String key) => ...;
}

// When you ACTUALLY need a second implementation, THEN abstract
// The refactoring is straightforward and you'll know the right abstraction
```

**Why it matters:**
- Less code to maintain
- Abstractions based on real needs fit better
- Easier to understand: no indirection to trace
- YAGNI: You Aren't Gonna Need It

---

### 5.2 Consistent Error Handling

**Impact: MEDIUM (Improves UX and debugging)**

Ad-hoc try/catch scattered in screens, inconsistent error UX across the app.

**Detection signals:**
- Errors appear differently across screens (toasts vs dialogs vs inline)
- try/catch blocks scattered in widget code
- Inconsistent error messaging
- No standard retry mechanism

**Incorrect (ad-hoc handling):**

```dart
// Screen 1: Try/catch with toast
try {
  await ref.read(saveProvider.notifier).save();
} catch (e) {
  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
}

// Screen 2: Different pattern
final result = await ref.read(saveProvider.notifier).save();
if (result.isError) {
  showDialog(...); // Different error UI
}

// Screen 3: No error handling at all
await ref.read(saveProvider.notifier).save(); // Hope it works!
```

**Correct (consistent pattern):**

```dart
// Providers handle errors uniformly
@riverpod
class SaveController extends _$SaveController {
  Future<void> save() async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.save());
    // Error stays in state, not thrown
  }
}

// Screens use consistent pattern
Widget build(context, ref) {
  // Centralized error listening
  ref.listenOnError(saveProvider);

  final saveState = ref.watch(saveProvider);

  return AppPrimaryButton(
    isLoading: saveState.isLoading,
    onPressed: () => ref.read(saveProvider.notifier).save(),
    child: Text('Save'),
  );
}
```

**Why it matters:**
- Users get consistent experience
- Developers follow one pattern
- Error states are explicit and testable
- Retry logic is standardized

---

## Context Gathering

When asked to review code, first identify the target:

If target is unclear, ask:
- What code should be reviewed? (specific files, a feature folder, uncommitted changes, a commit, a patch file)
- Is there a specific concern or area of focus?

For the specified target, gather the relevant code:
- **Commit**: `git show <commit>`
- **Patch file**: Read the patch file
- **Uncommitted changes**: `git diff` and `git diff --cached`
- **Folder/feature**: Read the relevant files in that directory
- **Specific file**: Read that file and related files it imports/uses

---

## Analysis Process

1. **Read thoroughly** - Understand what the code does, not just its structure

2. **Apply the three lenses** - For each lens, note specific instances (or note "no issues found")

3. **Check for additional patterns** - If you notice issues beyond the core lenses, consult the principle sections for precise diagnosis

4. **Prioritize by evolution impact**:
   - High: Will cause cascading changes when requirements shift
   - Medium: Creates friction but contained to one area
   - Low: Suboptimal but won't compound

5. **Formulate concrete suggestions** - Name specific extractions, show before/after for the highest-impact change

---

## Output Format

```markdown
## Senior Review: [Target]

### Summary
[1-2 sentences: Overall assessment and the single most important structural opportunity]

### Findings

#### High Impact: [Issue Name]
**What I noticed:** [Specific code pattern observed]
**Why it matters:** [How this will cause problems as code evolves]
**Suggestion:** [Concrete refactoring - name the types/widgets to extract]

#### Medium Impact: [Issue Name]
[Same structure]

#### Low Impact: [Issue Name]
[Same structure]

### No Issues Found
[If a lens revealed no problems, briefly note: "State modeling: No boolean flag combinations or repeated decision logic detected."]

---

**What's your take on these suggestions? Any context I'm missing?**
```

---

## Success Criteria

- At least one finding per applicable lens (or explicit "no issues" statement)
- Each finding tied to evolution impact, not just "could be better"
- Suggestions are concrete: specific types/widgets named, not vague advice
- No forced findings - if code is solid, say so
- User has opportunity to provide context before changes
