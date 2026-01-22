## Riverpod Fundamentals
1. The `Ref` object is essential for accessing the provider system, reading or watching other providers, managing lifecycles, and handling dependencies in Riverpod.
2. In functional providers, obtain `Ref` as a parameter; in class-based providers, access it as a property of the Notifier.
3. In widgets, use `WidgetRef` (a subtype of `Ref`) to interact with providers.
4. The `@riverpod` annotation is used to define providers with code generation, where the function receives `ref` as its parameter.
5. Providers are lazy—network requests or logic inside a provider are only executed when the provider is first read.
6. Multiple widgets can listen to the same provider; the provider will only execute once and cache the result.
7. Obtain the `Ref` object as a parameter in provider functions (or `WidgetRef` in widgets) to access other providers and manage lifecycles.


**Example: Functional Provider with `@riverpod` annotation**
```dart
@riverpod
int example(Ref ref) {
 return 0;
}
```

**Example: Class-based Provider with `@Riverpod(keepAlive: true)` annotation**
```dart
@Riverpod(keepAlive: true)
class Auth extends _$Auth {
  AuthApi get _api => ref.read(authApiProvider);

  @override
  Future<AuthState> build() async {
    final authState = await _api.getAuthState();
    log.info('Auth state changed: $result');

    return authState;
  }

  Future<void> signOut() async {
    state = const AsyncValue.loading();

    try {
      await _api.signOut();
    } catch (e, st) {
      log.error('Error signing out: $e', e, st);
      ref.invalidateSelf();
    }
  }
}
```

## Riverpod 3.0 Changes

1. **Unified Ref**: Riverpod 3.0 uses a single `Ref` type instead of generic `Ref<T>`. No generic parameter needed.
2. **Async Safety**: The `Ref.mounted` property indicates if the provider is still active after async operations.
3. **Legacy Support**: Import from `package:riverpod/legacy.dart` for 2.x patterns during migration.

### Ref.mounted Pattern

Always check `ref.mounted` after async operations to prevent state updates on disposed providers:

```dart
@riverpod
class MyNotifier extends _$MyNotifier {
  @override
  FutureOr<Data> build() async {
    return fetchData();
  }

  Future<void> refresh() async {
    state = const AsyncLoading();
    final result = await api.fetch();
    if (!ref.mounted) return; // Provider was disposed during await
    state = AsyncData(result);
  }
}
```

## Ref Object Usage
1. Use `ref.watch` to reactively depend on other providers; the provider will rebuild when dependencies change.
2. When using `ref.watch` with asynchronous providers, use `.future` to await the value if you need the resolved result.
3. Use `ref.listen` to perform side effects when a provider changes.
4. Use `ref.read` only when you cannot use `ref.watch`, such as inside Notifier methods or event handlers.
5. Be cautious with `ref.read`, as providers not being listened to may destroy their state if not actively watched.

## State Management with Notifiers
1. Use Notifiers to expose methods for performing side effects and modifying provider state.
2. Expose public methods on Notifiers for UI to trigger state changes or side effects.
3. In UI event handlers (e.g., button `onPressed`), use `ref.read` to call Notifier methods.
4. After performing a side effect, update the UI state by:
   - Setting the new state directly if the server returns the updated data.
   - Calling `ref.invalidateSelf()` to refresh the provider and re-fetch data.
   - Manually updating the local cache if the server does not return the new state.
5. Always handle loading and error states in the UI when performing side effects.

## Auto Dispose & State Disposal
1. By default, with code generation, provider state is destroyed when the provider stops being listened to.
2. Opt out of automatic disposal by setting `keepAlive: true` 
3. Always enable automatic disposal for providers that receive parameters to prevent memory leaks.
4. Use `ref.onDispose` to register cleanup logic that runs when provider state is destroyed.

## Passing Arguments to Providers
1. Add parameters directly to the annotated function (excluding ref).
2. Always enable automatic disposal for providers that receive parameters to prevent memory leaks.
3. The equality (`==`) of provider parameters determines caching—ensure parameters have consistent equality using the `equatable` package.
4. Avoid passing objects that do not override `==` (such as plain `List` or `Map`) as provider parameters.