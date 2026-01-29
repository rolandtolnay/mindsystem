### Widget Structure

- Extract complex nested widgets into private builder methods (`_buildHeader()`, `_buildContent()`)
- Early return for empty states: `if (items.isEmpty) return const SizedBox.shrink();`
- Keep build methods focused and readable by decomposing large widget trees
- IMPORTANT: Move callbacks inside `build()` when they need 4+ parameters from local scope (hooks, refs, notifiers): define `void handleSubmit() { ... }` inside build rather than `_handleSubmit(ref, controller, user, state)` outside

### Model Conversions

- Use factory constructors for domain-to-UI conversions: `WidgetState.fromDomainModel()`
- Encapsulate conversion logic instead of manual property mapping
- Prefer `.map()` with spread syntax for list conversions

### Defensive Programming

- Make callbacks optional with nullable types: `final VoidCallback? onDismiss;`
- IMPORTANT: Use null-safe invocation: `onDismiss?.call()` instead of direct calls
- Use `firstWhereOrNull` with fallbacks: `items.firstWhereOrNull((x) => x.isSelected) ?? items.first`
- Guard against empty collections at method entry points

### Hook Usage

- Prefer semantic project-specific hooks over generic ones: `useInitAsync()`, `useFormController()` instead of `useEffect()`
- Use `useMemoized` for simple derived values over creating single-use providers: `useMemoized(() => items.any((e) => e.isExpansion), [items])`

### Data Modeling

- Use structured types over primitives for domain concepts: `Address` instead of `street: String, city: String`
- Suffix data model classes consistently: `UserProfileData` for state containers
- Use nullable Function types in copyWith for optional updates: `Address? Function()? address`

### Input Handling

- YOU MUST sanitize text input on capture: `notifier.updateField(value: controller.text.trim())`
- Simplify state setters without conditional logic: always set state regardless of value
- Keep input controllers synchronized with state via useEffect listeners

### Form Design

- Use semantic spacing constants for hierarchy: `Spacing.section` between major sections
- Label optional fields explicitly: `'Email (optional)'` instead of asterisks
- Prefer framework-specific widgets: `CustomSlider` over generic `Slider` for design consistency
- Simplify placeholder text without redundant prefixes: `'Acme Corp'` instead of `'e.g. Acme Corp'`
- Apply consistent typography scales for form labels: `context.typography.heading` for section titles

### Form Validation

- YOU MUST centralize validation logic in Validator class methods: `validator.validateEmail(email)`
- Use feature-specific translation keys for validation messages: `LocaleKeys.validation_email_required`
- Extract complex validation conditions into named methods: `bool hasValidInput()`

### Factory Methods

- Provide fallback factory constructors for safe defaults: `DateModel.fallback()` when date might be null
- Remove unnecessary state from data models: eliminate derived properties if computed from other state

### Business Logic & Domain Design

- IMPORTANT: Encapsulate business rules in entity computed properties instead of scattering logic in UI/providers: `bool get canDelete => isOwner && !isArchived;`
- IMPORTANT: Return records from domain methods when multiple related values must stay in sync: `({int? multiplier, int reward}) applyBonus(int base)` prevents drift between multiplier value and computed result
- Use nullability as a feature flag in returned records: check `bonus?.multiplier != null` instead of separate `isPremium` boolean; enables future extension without API changes
- Centralize magic numbers in domain extensions rather than scattering across widgets: define `const premiumMultiplier = 2` once in `applyRewardBonus()` not in 4 widget files

### Error Handling

- IMPORTANT: Centralize error handling with `ref.listenOnError(provider)` at screen level; let providers use `AsyncValue.guard()` instead of manual try-catch in action methods
- Keep API layer methods simple: only use try/catch when converting to domain-specific errors; omit error handling entirely when no special conversion is needed and let errors propagate to providers

### Widget API Design

- Support flexible styling with fallback chains and both general/specific parameters: `iconColor ?? color ?? context.color.primary`
- Pass domain-computed records to widgets instead of raw flags: `bonus: user?.applyRewardBonus(baseReward)` not `isPremium: user?.premium ?? false`; keeps calculation logic out of widgets
- Design widget APIs with optional computed values for extensibility: `RewardModal({required int baseReward, int? boostedReward, int? multiplier})` allows future bonus types without breaking changes

### Code Organization

- Extract complex widget trees into separate files when they exceed ~100 lines or contain multiple related widgets
- Promote private widgets to public widgets in dedicated files: move `_DetailWidget` to `detail_widget.dart` with related components

### Collection Operations

- YOU MUST use immutable collection methods over mutation: `.sorted((a, b) => ...)` instead of `.toList()..sort((a, b) => ...)`
- Import `package:collection/collection.dart` for functional collection utilities like `sorted()`, `firstWhereOrNull()`, `groupBy()`
- Use `.divide()` extension to insert spacing between dynamically generated widgets: `items.map((e) => Widget()).divide(const SizedBox(width: 8))`

### Domain Property Usage

- Use entity computed properties over direct comparisons: `where((e) => e.isActive)` instead of `where((e) => e.status == Status.active)`
- IMPORTANT: Move presentation logic to domain extensions: `extension on Model { String get displayText => ... }` rather than private widget methods
- Add computed display properties directly on enums: `enum SortOrder { ...; String get label => switch (this) { ... }; }` instead of hardcoding labels in widget builders
- Map over `EnumType.values` to generate widgets dynamically: `SortOrder.values.map((e) => ChoiceChip(label: Text(e.label), ...))` instead of defining each widget individually
- Derive UI booleans from returned records in widgets: `final hasBonus = bonus?.multiplier != null;` rather than passing separate boolean props alongside data

### Project Structure

- Prefer flat feature directories over deep nesting: `lib/home/home_screen.dart` instead of `lib/features/home/presentation/home_screen.dart`
- Consolidate single-value constants into existing constant files: add to `app_constants.dart` instead of creating `payment_channel.dart`
- Eliminate barrel files that only re-export: import `app_info_provider.dart` directly instead of through a `home_providers.dart` re-export layer

### Provider Naming

- Prefix providers with feature scope when names could be ambiguous: `collectionExpansionVisibilityProvider` instead of generic `expansionVisibilityProvider`

### Theme & Styling

- YOU MUST use app color constants from `AppColors` instead of hardcoding hex values: `AppColors.gray400` not `const Color(0xFF9E9E9E)`; keeps colors centralized and maintains design consistency
- Extract color schemes and visual variants into dedicated theme classes with factory constructors: `PodiumTheme.fromRank(rank, brightness)` instead of scattered color constants
- Support light/dark modes in custom themes via factory methods accepting `Brightness`: `factory Theme.fromType(type, context.brightness)`
- Use switch expressions for variant-specific computed properties: `double get _height => switch (placement) { 1 => 192.0, 2 => 128.0, _ => 96.0 };`

### Widget Composition

- For simple, non-reusable child widgets, create named local variables instead of builder methods: `final bar = Container(...); return Column(children: [avatar, bar]);`
- Prefer concise single-line guard clauses in builder methods: `if (data == null) return const SizedBox(width: _kBarWidth);`
- IMPORTANT: Define modal/bottom sheet widgets with a static `show` method that encapsulates display logic: `static Future<void> show(BuildContext context, {...}) => showAppBottomSheet(builder: (_) => MyModal(...))`

### Animation Patterns

- Consolidate static and animated widget variants into a single widget with optional animation parameters: use `Animation<double>?` with fallback defaults `animation?.value ?? 1.0` instead of separate `StaticWidget` and `AnimatedWidget` classes
- Use `Listenable.merge()` to combine multiple animations into one AnimatedBuilder instead of nesting: `AnimatedBuilder(animation: Listenable.merge([anim1, anim2]), builder: ...)`

### Async Provider Patterns

- Use record destructuring with `.wait` to fetch multiple independent async values in parallel: `final (a, b, c) = await (ref.watch(aProvider.future), ref.watch(bProvider.future), ref.watch(cProvider.future)).wait;`
- IMPORTANT: Provider action methods should return `void` and never rethrow state errors; use `AsyncValue.guard()` and let state hold the error
- Prefer `.value` over `.asData?.value` for AsyncValue access: `asyncValue.value ?? []` instead of `asyncValue.asData?.value ?? []`

### Single-Action Provider Pattern

- IMPORTANT: Create dedicated providers for discrete async actions (`loginProvider`, `logoutProvider`, `saveProvider`) instead of adding methods to monolithic state providers; enables independent loading/error state per action
- IMPORTANT: Derive loading flags from provider state: `final isLoading = actionProvider.isLoading` instead of `useState<bool>(false)` with manual toggle
- Use `FutureOr<T?> build() => null;` for on-demand action providers so they only execute when explicitly triggered
- Handle action outcomes with `ref.listen` and `whenOrNull`: `ref.listen(provider, (_, next) { next.whenOrNull(data: (result) { if (result == null) return; /* success */ }, error: (e, _) => showError(e)); });`
- Avoid manual state transition detection (`didComplete = prev.isLoading && !next.isLoading`); let `whenOrNull` naturally fire only on data/error states

### Collection Operations (Advanced)

- Use `compactMap` instead of `map` + `whereType<T>()` for nullable transformations: `items.compactMap((e) => transform(e)).toList()` instead of `items.map((e) => nullable(e)).whereType<T>().toList()`

### File-Scoped Extensions

- Define private extensions for reusable computations local to a single file: `extension on Iterable<int> { int? get average => isNotEmpty ? reduce((a, b) => a + b) ~/ length : null; }`
- IMPORTANT: Move widget styling methods to type extensions when they operate on a single parameter: `extension on ButtonStyle { BoxDecoration buildDecoration(BuildContext context) => switch (this) { ... }; }` instead of `_buildDecoration(ButtonStyle style)` as a widget method

### State Modeling with Sealed Classes

- IMPORTANT: Replace multiple boolean flags with sealed class variants: `sealed class State {}` with `Loading`, `Ready`, `Error` subclasses instead of `bool _isLoading, bool _hasError`
- Use switch expressions for exhaustive state handling: `return switch (state) { Loading() => ..., Ready(:final data) => ..., Error(:final error) => ... };`
- Include relevant data in each sealed class variant: `class Ready { final Controller controller; }` rather than keeping data separate from state
- IMPORTANT: Define shared parameters in sealed class base constructor to avoid duplication: `sealed class Mode { const Mode({required this.id}); final String id; }` instead of declaring `id` in each subclass

### Async Resource Hooks

- Encapsulate async resource lifecycle in custom hooks: `useVideoPlayerController()` handles init, config, and disposal internally
- Use `useIsMounted()` to guard state updates after async operations: `if (!isMounted()) return;` before each `state.value =` assignment
- Store disposable resources in `useRef` for cleanup access: `final controllerRef = useRef<Controller?>(null);` with `useEffect(() => () => controllerRef.value?.dispose(), const []);`

### Localization & Dynamic Content

- Use translation placeholders for values that may change: `"{multiplier}x Premium Bonus!"` instead of hardcoded `"2x Premium Bonus!"`; enables future flexibility without translation file changes
- Remove unused translation keys when centralizing logic: delete `premium_multiplier` key when multiplier display becomes dynamic from code