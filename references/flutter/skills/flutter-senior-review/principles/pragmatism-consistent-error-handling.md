---
title: Consistent Error Handling
category: pragmatism
impact: MEDIUM
impactDescription: Improves UX and debugging
tags: error-handling, async-value, riverpod, toast
---

## Consistent Error Handling Strategy

One strategy applied everywhere, not ad-hoc try/catch. Use AsyncValue for state management and centralized error presentation.

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
// Providers handle errors uniformly with AsyncValue.guard
@riverpod
class SaveController extends _$SaveController {
  @override
  FutureOr<void> build() => null;

  Future<void> save(Data data) async {
    state = const AsyncLoading();
    state = await AsyncValue.guard(() => _repository.save(data));
    // Error stays in state, not thrown
    // Success navigates or shows confirmation
    if (state.hasValue) {
      ref.invalidate(dataProvider);
    }
  }
}

// Extension for centralized error listening
extension WidgetRefEx on WidgetRef {
  void listenOnError<T>(
    ProviderListenable<AsyncValue<T>> provider, {
    bool Function(Object error)? ignoreIf,
  }) {
    listen(provider, (_, next) {
      next.whenOrNull(
        error: (error, _) {
          if (ignoreIf?.call(error) == true) return;
          AppToast.showError(context, error.toString());
        },
      );
    });
  }
}

// Screens use consistent pattern
Widget build(context, ref) {
  // Centralized error listening - shows toast on any error
  ref.listenOnError(saveProvider);

  final saveState = ref.watch(saveProvider);

  return AppPrimaryButton(
    isLoading: saveState.isLoading,
    onPressed: () => ref.read(saveProvider.notifier).save(data),
    child: Text('Save'),
  );
}
```

**For first-load errors (need retry UI):**

```dart
Widget build(context, ref) {
  final dataState = ref.watch(dataProvider);

  return dataState.when(
    data: (data) => DataContent(data: data),
    loading: () => const AppLoadingIndicator(),
    error: (error, _) => Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: context.colorScheme.error),
          const SizedBox(height: 16),
          Text(LocaleKeys.common_error.tr()),
          const SizedBox(height: 16),
          FilledButton.icon(
            onPressed: () => ref.invalidate(dataProvider),
            icon: const Icon(Icons.refresh),
            label: Text(LocaleKeys.common_retry.tr()),
          ),
        ],
      ),
    ),
  );
}
```

**Why it matters:**
- Users get consistent experience
- Developers follow one pattern
- Error states are explicit and testable
- Retry logic is standardized

**Detection questions:**
- Do errors appear the same way across all screens?
- Are there try/catch blocks in widget code?
- Is error messaging consistent (toasts vs dialogs vs inline)?
- Is there a standard retry mechanism?
