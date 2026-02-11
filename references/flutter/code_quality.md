---
description: Review Flutter/Dart code for quality and pattern compliance
argument-hint: <file-or-pattern>
---

# Flutter Code Quality

Review these files for compliance: $ARGUMENTS

Read files, check against rules below. Output concise but comprehensive—sacrifice grammar for brevity. High signal-to-noise.

## Rules

## Widget Structure

- Extract nested widgets into private builders: `_buildHeader()`, `_buildContent()`
- Early return for empty states: `if (items.isEmpty) return const SizedBox.shrink();`
- Callbacks needing 4+ local scope params → define inside `build()`: `void handleSubmit() { ... }` not `_handleSubmit(ref, controller, user, state)`
- Simple child widgets → named local variables: `final bar = Container(...);` not `_buildBar()`
- Single-line guard clauses: `if (data == null) return const SizedBox(width: _kBarWidth);`
- `HookWidget` over `StatefulWidget` when only managing animation controllers or simple state: `useAnimationController` replaces manual `State` lifecycle

## State & Providers

- Dedicated providers for discrete actions: `loginProvider`, `saveProvider` not methods on monolithic provider
- Loading flags from provider state: `final isLoading = actionProvider.isLoading` not `useState<bool>(false)`
- On-demand action providers: `FutureOr<T?> build() => null;`
- Action outcomes via `ref.listen` + `whenOrNull`: `next.whenOrNull(data: (result) => ..., error: (e, _) => showError(e))`
- Parallel async fetch: `final (a, b, c) = await (ref.watch(aProvider.future), ...).wait;`
- Provider actions return `void`, never rethrow; use `AsyncValue.guard()`
- Prefer `.value` over `.asData?.value`: `asyncValue.value ?? []`
- Error handling: `ref.listenOnError(provider)` at screen level; let errors propagate

## Sealed Classes

- Replace boolean flags with sealed variants: `sealed class State {}` with `Loading`, `Ready`, `Error`
- Switch expressions for exhaustive handling: `return switch (state) { Loading() => ..., Ready(:final data) => ... };`
- Shared params in base constructor: `sealed class Mode { const Mode({required this.id}); final String id; }`

## Domain & Business Logic

- Business rules in entity computed properties: `bool get canDelete => isOwner && !isArchived;`
- Records for multiple related values: `({int? multiplier, int reward}) applyBonus(int base)`
- Nullability as feature flag: check `bonus?.multiplier != null` not separate `isPremium` boolean
- Magic numbers in domain extensions, not scattered in widgets
- Presentation logic in domain extensions: `extension on Model { String get displayText => ... }`
- Computed properties on enums: `enum SortOrder { ...; String get label => switch (this) { ... }; }`
- Entity computed properties over comparisons: `where((e) => e.isActive)` not `where((e) => e.status == Status.active)`

## Collections

- Immutable methods: `.sorted((a, b) => ...)` not `.toList()..sort()`
- Import `package:collection/collection.dart` for `sorted()`, `firstWhereOrNull()`, `groupBy()`
- `compactMap` over `map` + `whereType<T>()`
- `.divide()` for spacing: `items.map((e) => Widget()).divide(const SizedBox(width: 8))`
- `firstWhereOrNull` with fallback: `items.firstWhereOrNull((x) => x.isSelected) ?? items.first`
- Map over `EnumType.values`: `SortOrder.values.map((e) => ChoiceChip(label: Text(e.label)))`

## Forms & Input

- Sanitize on capture: `notifier.updateField(value: controller.text.trim())`
- Validation in Validator class: `validator.validateEmail(email)`
- Feature-specific translation keys: `LocaleKeys.validation_email_required`
- Label optional fields explicitly: `'Email (optional)'`
- Semantic spacing: `Spacing.section` between major sections
- Framework widgets over generic: `CustomSlider` not `Slider`
- Clean placeholders: `'Acme Corp'` not `'e.g. Acme Corp'`

## Hooks

- Semantic project hooks: `useInitAsync()`, `useFormController()` not raw `useEffect()`
- `useMemoized` for derived values: `useMemoized(() => items.any((e) => e.isExpansion), [items])`
- `useIsMounted()` guard for async state updates
- Disposable resources in `useRef`: `final controllerRef = useRef<Controller?>(null);`
- `useAnimationController` for press/tap animations: replaces `StatefulWidget` + manual `AnimationController` lifecycle

## Model & Data

- Factory constructors for conversions: `WidgetState.fromDomainModel()`
- Fallback factories: `DateModel.fallback()` for nullable dates
- Nullable callbacks: `final VoidCallback? onDismiss;` with `onDismiss?.call()`
- Structured types over primitives: `Address` not `street: String, city: String`
- Nullable Function in copyWith: `Address? Function()? address`
- Suffix data classes: `UserProfileData`
- Value equality via `Equatable`: `extends Equatable` + `List<Object?> get props => [id]` not manual `operator ==`/`hashCode`

## Widget API

- Flexible styling with fallback chains: `iconColor ?? color ?? context.color.primary`
- Pass domain-computed records: `bonus: user?.applyRewardBonus(baseReward)` not raw flags
- Optional computed values for extensibility: `RewardModal({required int baseReward, int? boostedReward})`
- Derive UI booleans from records in widgets: `final hasBonus = bonus?.multiplier != null;`

## Animation

- Single widget with optional animation: `Animation<double>?` with `animation?.value ?? 1.0`
- `Listenable.merge()` over nested AnimatedBuilders
- Modal/sheet widgets with static `show`: `static Future<void> show(BuildContext context) => showAppBottomSheet(builder: (_) => MyModal())`
- Press feedback: `ScaleTransition` + `useAnimationController` over `AnimatedScale` + `setState(_isPressed)` — avoids gesture arena delays in scroll views
- Auto-reverse pattern: `addStatusListener((s) { if (s == AnimationStatus.completed) ctrl.reverse(); })` for one-shot press effects
- `HitTestBehavior.opaque` on `GestureDetector` for cards with transparent regions

## Theme & Styling

- App color constants: `context.color.gray400` not `const Color(0xFF9E9E9E)`
- Theme classes with factory constructors: `PodiumTheme.fromRank(rank, brightness)`
- Switch expressions for variants: `double get _height => switch (placement) { 1 => 192.0, 2 => 128.0, _ => 96.0 };`
- Light/dark via factory: `factory Theme.fromType(type, context.brightness)`

## Extensions

- Private extensions for file-local computations: `extension on UserEntity { ... }`
- Styling methods on type extensions in same file: `extension on ButtonStyle { BoxDecoration buildDecoration(context) => ... }`
- Display extensions by scope: multi-widget → model file; single-widget → `extension _FooDisplay` private in consuming widget file

## Project Structure

- Flat feature directories: `lib/home/home_screen.dart` not `lib/features/home/presentation/`
- Consolidate constants: add to `app_constants.dart` not new single-value files
- No barrel files that only re-export
- Scoped provider names: `collectionExpansionVisibilityProvider` not generic `expansionVisibilityProvider`
- Extract widgets >100 lines to separate files

## Localization

- Translation placeholders for dynamic values: `"{multiplier}x Premium Bonus!"`
- Remove unused keys when logic centralizes

## Anti-Patterns (flag these)

- `useState<bool>` for loading states (use provider state)
- Manual try-catch in provider actions (use `AsyncValue.guard()`)
- `.toList()..sort()` (use `.sorted()`)
- `_handleAction(ref, controller, user, state)` with 4+ params (move inside build)
- Hardcoded hex colors (use `context.color.*`)
- Deep feature directories `lib/features/x/presentation/`
- Barrel files that only re-export
- Boolean flags instead of sealed classes for complex state
- Magic numbers scattered across widgets
- `where((e) => e.status == Status.active)` (use computed property)
- Generic `expansionVisibilityProvider` names
- `.asData?.value` (use `.value`)
- Separate `isPremium` boolean alongside `multiplier` data
- `AnimatedScale` + `onTapDown`/`onTapUp`/`onTapCancel` for press feedback in scrollable lists (use `ScaleTransition` + `useAnimationController`)
- `StatefulWidget` for animation-only state (use `HookWidget` + `useAnimationController`)
- Manual `operator ==` / `hashCode` overrides (use `Equatable` with `props`)
- `extensions/` subdirectory for display logic (co-locate with model or widget instead)

## Output Format

Group by file. Use `file:line` format. Terse findings.

```text
## lib/home/home_screen.dart

lib/home/home_screen.dart:42 - useState for loading state → use provider
lib/home/home_screen.dart:67 - .toList()..sort() → .sorted()
lib/home/home_screen.dart:89 - hardcoded Color(0xFF...) → context.color.*

## lib/models/user.dart

✓ pass
```

State issue + location. Skip explanation unless fix non-obvious. No preamble.

