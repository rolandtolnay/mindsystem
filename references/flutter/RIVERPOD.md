## Riverpod Fundamentals
1. The `Ref` object is essential for accessing the provider system, reading or watching other providers, managing lifecycles, and handling dependencies in Riverpod.
2. In functional providers, obtain `Ref` as a parameter; in class-based providers, access it as a property of the Notifier.
3. The `@riverpod` annotation is used to define providers with code generation, where the function receives `ref` as its parameter.
4. Providers are lazy - network requests or logic inside a provider are only executed when the provider is first read.
5. Multiple widgets can listen to the same provider; the provider will only execute once and cache the result.

## Provider Patterns

**Example: Functional Provider** — for simple/computed values:
```dart
@riverpod
int example(Ref ref) {
  return 0;
}
```

**Example: Class-based Provider** — for stateful providers with methods:
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

### Ref.mounted (Async Safety)

Always check `ref.mounted` after async operations to prevent state updates on disposed providers:

```dart
Future<void> refresh() async {
  state = const AsyncLoading();
  final result = await api.fetch();
  if (!ref.mounted) return; // Provider was disposed during await
  state = AsyncData(result);
}
```

## Ref Object Usage
1. Use `ref.watch` to reactively depend on other providers; the provider will rebuild when dependencies change.
2. When using `ref.watch` with asynchronous providers, use `.future` to await the value if you need the resolved result.
3. Use `ref.listen` to perform side effects when a provider changes.
4. Use `ref.read` only when you cannot use `ref.watch`, such as inside Notifier methods or event handlers.
5. Be cautious with `ref.read`, as providers not being listened to may destroy their state if not actively watched.

## Mutation Patterns

After performing a side effect, update state by:
1. **Direct state update** — if the API returns the updated data
2. **`ref.invalidateSelf()`** — to refresh and re-fetch from source
3. **Manual cache update** — if API doesn't return new state

In UI event handlers, use `ref.read` to call Notifier methods:
```dart
onPressed: () => ref.read(authProvider.notifier).signOut()
```

## Disposal Rules

- Use `keepAlive: true` for providers that should persist (auth, user session, core entities)
- **Always use auto-dispose for providers with parameters** — prevents memory leaks
- Use `ref.onDispose` to register cleanup logic (cancel subscriptions, close streams)

## Provider Parameters

- Add parameters directly to the annotated function (after `ref`)
- **Parameters must override `==`** — use `equatable` package for custom objects
- **Never pass raw `List` or `Map`** as parameters — wrap in equatable class or use immutable collections
