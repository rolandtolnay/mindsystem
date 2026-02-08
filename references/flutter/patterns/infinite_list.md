# Infinite List Pagination Guide

Cursor-based pagination for infinite scrolling lists using Riverpod. This pattern handles loading states, error recovery, pull-to-refresh, and filter integration.

## TL;DR for LLM Agents

When implementing paginated lists:

1. Create a **Result Model** with `List<T> items`, `String? nextPageToken`, `bool hasReachedMax`.
2. Create a **List Provider** with `@Riverpod(keepAlive: true)`, `build()` for initial fetch, `loadMore()` for pagination.
3. In `loadMore()`: guard against loading/max, use `.retainPrevious()`, combine items with spread operator.
4. In **Widget**: pass `isLoading`, `hasError`, `hasReachedMax` to `InfiniteList`, call `notifier.loadMore()` in `onFetchData`.
5. For **filters**: `ref.watch(filterProvider)` in `build()` triggers automatic refresh on filter change.
6. For **refresh**: call `ref.invalidate(listProvider)` to reset pagination.

---

## Result Model

The result model holds paginated data with cursor state.

```dart
class ItemListResult extends Equatable {
  final List<ItemEntity> items;
  final String? nextPageToken;
  final bool hasReachedMax;

  const ItemListResult({
    this.items = const [],
    this.nextPageToken,
    this.hasReachedMax = true,
  });

  /// Use nullable function wrapper to distinguish "set to null" vs "not provided"
  ItemListResult copyWith({
    List<ItemEntity>? items,
    String? Function()? nextPageToken,
    bool? hasReachedMax,
  }) {
    return ItemListResult(
      items: items ?? this.items,
      nextPageToken: nextPageToken != null ? nextPageToken() : this.nextPageToken,
      hasReachedMax: hasReachedMax ?? this.hasReachedMax,
    );
  }

  @override
  List<Object?> get props => [items, nextPageToken, hasReachedMax];
}
```

**Key points:**
- `nextPageToken`: Cursor for next page, `null` when no more pages
- `hasReachedMax`: Prevents further fetch attempts
- `copyWith` uses `String? Function()?` pattern for nullable field updates

---

## API Layer

The API fetches pages and determines if more data exists.

```dart
Future<ItemListResult> getItemList({
  required AccountEntity account,
  ItemFilterState? filter,
  int pageSize = 25,
  String? pageToken,
}) async {
  final request = ListItemsRequest(
    parent: account.id,
    filter: filter?.toDto(),
    pageSize: pageSize,
    pageToken: pageToken ?? '',
  );

  final response = await _client.listItems(request);

  return ItemListResult(
    items: response.items.map((e) => e.toEntity()).toList(),
    nextPageToken: response.nextPageToken.isEmpty ? null : response.nextPageToken,
    hasReachedMax: response.items.length < pageSize,
  );
}
```

**Key points:**
- `hasReachedMax` determined by: `response.items.length < pageSize`
- Empty `nextPageToken` from API converted to `null`
- Default `pageSize` of 10-25 items per page

---

## Provider Pattern

Use `@Riverpod(keepAlive: true)` to persist list state across navigation.

```dart
@Riverpod(keepAlive: true)
class ItemList extends _$ItemList {
  ItemApi get _api => ref.read(itemApiProvider);

  @override
  FutureOr<ItemListResult> build() async {
    final account = await ref.watch(selectedAccountProvider.future);
    if (account == null) return const ItemListResult();

    // Watch filter to auto-refresh on changes
    final filter = ref.watch(itemFilterProvider);

    return _api.getItemList(account: account, filter: filter);
  }

  Future<void> loadMore() async {
    // Guard: prevent concurrent loads
    if (state.isLoading) return;

    // Guard: no more pages
    if (state.value?.hasReachedMax ?? false) return;

    // Set loading state while retaining previous data
    state = const AsyncLoading<ItemListResult>().retainPrevious(
      state,
      isRefresh: false,
    );

    final account = await ref.read(selectedAccountProvider.future);
    if (account == null) {
      state = AsyncData(state.value ?? const ItemListResult());
      return;
    }

    // Fetch next page with automatic error handling
    state = await AsyncValue.guard(() async {
      final filter = ref.read(itemFilterProvider);
      final result = await _api.getItemList(
        account: account,
        filter: filter,
        pageToken: state.value?.nextPageToken,
      );

      // Combine existing items with new items
      return state.value!.copyWith(
        items: [...state.value!.items, ...result.items],
        nextPageToken: () => result.nextPageToken,
        hasReachedMax: result.hasReachedMax,
      );
    });
  }
}
```

**Key patterns:**
- `build()`: Initial fetch, watches dependencies for auto-refresh
- `loadMore()`: Pagination with guards and data merging
- `.retainPrevious()`: Shows existing data while loading
- `AsyncValue.guard()`: Automatic error state on exceptions
- Spread operator `[...existing, ...new]` for immutable list merge
- Use `ref.watch()` in `build()`, `ref.read()` in `loadMore()`

---

## AsyncLoading Extension

Add this extension to retain previous data during loading states.

```dart
// lib/common/extensions/async_value_loading_ext.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';

extension AsyncLoadingRetainPrevious<T> on AsyncLoading<T> {
  /// Retains previous value while in loading state.
  /// Set [isRefresh] to false for pagination (shows loading indicator at bottom).
  AsyncValue<T> retainPrevious(
    AsyncValue<T> previous, {
    bool isRefresh = true,
  }) {
    // ignore: invalid_use_of_internal_member
    return copyWithPrevious(previous, isRefresh: isRefresh);
  }
}
```

**Usage difference:**
- `isRefresh: true` - Full screen refresh (pull-to-refresh)
- `isRefresh: false` - Pagination (loading indicator at list bottom)

---

## Widget Usage

Connect the provider to `InfiniteList` widget.

```dart
class ItemInfiniteList extends HookConsumerWidget {
  const ItemInfiniteList({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(itemListProvider);
    final notifier = ref.watch(itemListProvider.notifier);

    // Sort items (use useMemoized to avoid re-sorting on every build)
    final items = useMemoized(
      () => (state.value?.items ?? []).sorted(
        (a, b) => b.createdAt.compareTo(a.createdAt),
      ),
      [state],
    );

    // Handle initial loading/error before data exists
    if (state.value == null) {
      return state.maybeWhen(
        skipLoadingOnRefresh: false,
        error: (error, _) => ErrorRetryWidget(
          error: error,
          onRetry: () => ref.invalidate(itemListProvider),
        ),
        orElse: () => const Center(child: AppLoadingIndicator()),
      );
    }

    return InfiniteList(
      elements: items,
      itemBuilder: (context, item) => ItemListTile(item: item),
      separator: const SizedBox(height: 8),
      isLoading: state.isLoading,
      hasError: state.hasError,
      hasReachedMax: state.value?.hasReachedMax ?? false,
      onFetchData: () => notifier.loadMore(),
      loadingBuilder: (_) => const Padding(
        padding: EdgeInsets.all(16),
        child: Center(child: AppLoadingIndicator()),
      ),
      errorBuilder: (context) => Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(tr(LocaleKeys.common_load_more_error)),
            const SizedBox(height: 8),
            AppGhostButton(
              title: tr(LocaleKeys.common_try_again),
              onPressed: () => notifier.loadMore(),
            ),
          ],
        ),
      ),
      emptyBuilder: (context) => _buildEmptyWidget(ref),
      centerEmpty: true,
      centerLoading: true,
      onRefresh: () async {
        ref.invalidate(itemListProvider);
      },
      padding: const EdgeInsets.only(bottom: kScrollEndPadding * 2),
    );
  }

  Widget _buildEmptyWidget(WidgetRef ref) {
    return Text(
      tr(LocaleKeys.items_empty),
      style: ref.context.typography.p.copyWith(
        color: ref.context.color.mutedForeground,
      ),
    );
  }
}
```

**Key patterns:**
- `useMemoized` for sorting to avoid redundant computation
- Guard `state.value == null` for initial load states
- Error builder includes retry button calling `loadMore()`
- `onRefresh` calls `ref.invalidate()` for pull-to-refresh

---

## InfiniteList Widget Interface

Reference for the `InfiniteList` widget parameters:

| Parameter      | Type                             | Required | Default         | Description                        |
|----------------|----------------------------------|----------|-----------------|------------------------------------|
| elements       | List\<T>                         | Yes      | -               | Items to display                   |
| itemBuilder    | Widget Function(BuildContext, T) | Yes      | -               | Builds each item                   |
| onFetchData    | void Function()                  | Yes      | -               | Called near bottom to load more    |
| isLoading      | bool                             | Yes      | -               | Loading state                      |
| hasError       | bool                             | Yes      | -               | Error state                        |
| hasReachedMax  | bool                             | Yes      | -               | No more pages available            |
| loadingBuilder | WidgetBuilder                    | Yes      | -               | Loading UI (initial & pagination)  |
| errorBuilder   | WidgetBuilder                    | Yes      | -               | Error UI (initial & pagination)    |
| emptyBuilder   | WidgetBuilder                    | Yes      | -               | Empty state UI                     |
| separator      | Widget?                          | No       | null            | Optional separator between items   |
| onRefresh      | Future\<void> Function()?        | No       | null            | Pull-to-refresh callback           |
| padding        | EdgeInsets                       | No       | EdgeInsets.zero | List padding                       |
| centerEmpty    | bool                             | No       | false           | Center empty widget                |
| centerLoading  | bool                             | No       | false           | Center loading widget              |
| fetchThreshold | double                           | No       | 200             | Distance to bottom before fetching |

---

## Filter Integration

Filters automatically trigger list refresh when watched in `build()`.

### Filter State

```dart
class ItemFilterState extends Equatable {
  final DateTimeRange? dateRange;
  final ItemStatus? status;

  const ItemFilterState({this.dateRange, this.status});

  int get filterCount => [dateRange, status].whereType<Object>().length;

  bool get hasFilters => filterCount > 0;

  @override
  List<Object?> get props => [dateRange, status];
}
```

### Filter Provider

```dart
@riverpod
class ItemFilter extends _$ItemFilter {
  @override
  ItemFilterState build() => const ItemFilterState();

  void setDateRange(DateTimeRange? range) {
    state = ItemFilterState(dateRange: range, status: state.status);
  }

  void setStatus(ItemStatus? status) {
    state = ItemFilterState(dateRange: state.dateRange, status: status);
  }

  void clearAll() {
    state = const ItemFilterState();
  }
}
```

### Integration in List Provider

```dart
@override
FutureOr<ItemListResult> build() async {
  // ...

  // Watching filter causes rebuild when filter changes
  final filter = ref.watch(itemFilterProvider);

  return _api.getItemList(account: account, filter: filter);
}
```

### Empty State with Filter Awareness

```dart
Widget _buildEmptyWidget(WidgetRef ref) {
  final filterState = ref.watch(itemFilterProvider);
  final hasFilters = filterState.filterCount > 0;

  return Column(
    mainAxisAlignment: MainAxisAlignment.center,
    children: [
      Text(
        hasFilters
            ? tr(LocaleKeys.items_empty_filtered)
            : tr(LocaleKeys.items_empty),
        style: ref.context.typography.p.copyWith(
          color: ref.context.color.mutedForeground,
        ),
      ),
      if (hasFilters) ...[
        const SizedBox(height: 16),
        AppGhostButton(
          title: tr(LocaleKeys.filter_clear_filters),
          onPressed: () => ref.read(itemFilterProvider.notifier).clearAll(),
        ),
      ],
    ],
  );
}
```

---

## Pull-to-Refresh

Reset pagination by invalidating the provider.

```dart
// In widget
onRefresh: () async {
  ref.invalidate(itemListProvider);
},

// Alternative: wait for new data before completing refresh
onRefresh: () async {
  ref.invalidate(itemListProvider);
  return ref.read(itemListProvider.future);
},
```

**Key difference:**
- `ref.invalidate()` alone: Refresh indicator dismisses immediately
- With `.future`: Refresh indicator waits for data to load

---

## Implementation Checklist

### Result Model
- [ ] Extends `Equatable` for proper equality checks
- [ ] Has `List<T> items`, `String? nextPageToken`, `bool hasReachedMax`
- [ ] `copyWith` uses `T? Function()?` pattern for nullable fields
- [ ] Default constructor has `items = const []`, `hasReachedMax = true`

### API Layer
- [ ] Accepts `pageSize` and `pageToken` parameters
- [ ] Returns `hasReachedMax = response.length < pageSize`
- [ ] Converts empty `nextPageToken` to `null`
- [ ] Performs proto/DTO to entity conversion

### Provider
- [ ] Uses `@Riverpod(keepAlive: true)` to persist across navigation
- [ ] `build()` fetches initial page, watches dependencies
- [ ] `loadMore()` has guards: `if (isLoading) return`, `if (hasReachedMax) return`
- [ ] Uses `.retainPrevious(state, isRefresh: false)` for loading state
- [ ] Uses `AsyncValue.guard()` for error handling
- [ ] Combines items with spread: `[...existing, ...new]`
- [ ] Uses `ref.read()` (not `watch`) in `loadMore()`

### Widget
- [ ] Handles `state.value == null` for initial loading/error
- [ ] Uses `useMemoized` for expensive transforms (sorting, filtering)
- [ ] Passes `state.isLoading`, `state.hasError`, `state.value?.hasReachedMax`
- [ ] Error builder includes retry calling `notifier.loadMore()`
- [ ] Empty builder is filter-aware when filters exist
- [ ] `onRefresh` calls `ref.invalidate(provider)`

### Filter Integration
- [ ] Filter state extends `Equatable`
- [ ] Filter provider has `clearAll()` method
- [ ] List provider watches filter in `build()` for auto-refresh
- [ ] Empty state shows "clear filters" when filters active
