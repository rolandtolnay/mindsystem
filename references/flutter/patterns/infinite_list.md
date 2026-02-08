# Infinite List Pagination

Cursor-based pagination for infinite scrolling using Riverpod.

## Overview

1. **Result Model**: `List<T> items`, `String? nextPageToken`, `bool hasReachedMax`
2. **List Provider**: `@Riverpod(keepAlive: true)`, `build()` for initial fetch, `loadMore()` for pagination
3. **`loadMore()`**: guard against loading/max, `.retainPrevious()`, combine items with spread
4. **Widget**: pass `isLoading`, `hasError`, `hasReachedMax` to `InfiniteList`, call `notifier.loadMore()` in `onFetchData`
5. **Filters**: `ref.watch(filterProvider)` in `build()` triggers auto-refresh on change
6. **Refresh**: `ref.invalidate(listProvider)` resets pagination

## Result Model

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

  /// Nullable function wrapper: distinguishes "set to null" vs "not provided"
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

## API Layer

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

- `hasReachedMax`: `response.items.length < pageSize`
- Empty `nextPageToken` from API → `null`

## Provider

```dart
@Riverpod(keepAlive: true)
class ItemList extends _$ItemList {
  ItemApi get _api => ref.read(itemApiProvider);

  @override
  FutureOr<ItemListResult> build() async {
    final account = await ref.watch(selectedAccountProvider.future);
    if (account == null) return const ItemListResult();

    final filter = ref.watch(itemFilterProvider);

    return _api.getItemList(account: account, filter: filter);
  }

  Future<void> loadMore() async {
    if (state.isLoading) return;
    if (state.value?.hasReachedMax ?? false) return;

    state = const AsyncLoading<ItemListResult>().retainPrevious(
      state,
      isRefresh: false,
    );

    final account = await ref.read(selectedAccountProvider.future);
    if (account == null) {
      state = AsyncData(state.value ?? const ItemListResult());
      return;
    }

    state = await AsyncValue.guard(() async {
      final filter = ref.read(itemFilterProvider);
      final result = await _api.getItemList(
        account: account,
        filter: filter,
        pageToken: state.value?.nextPageToken,
      );

      return state.value!.copyWith(
        items: [...state.value!.items, ...result.items],
        nextPageToken: () => result.nextPageToken,
        hasReachedMax: result.hasReachedMax,
      );
    });
  }
}
```

- `build()`: initial fetch, `ref.watch()` dependencies for auto-refresh
- `loadMore()`: guards → `.retainPrevious()` → `AsyncValue.guard()` → spread merge
- Use `ref.watch()` in `build()`, `ref.read()` in `loadMore()`

## AsyncLoading Extension

```dart
extension AsyncLoadingRetainPrevious<T> on AsyncLoading<T> {
  AsyncValue<T> retainPrevious(
    AsyncValue<T> previous, {
    bool isRefresh = true,
  }) {
    // ignore: invalid_use_of_internal_member
    return copyWithPrevious(previous, isRefresh: isRefresh);
  }
}
```

- `isRefresh: true` → full screen refresh (pull-to-refresh)
- `isRefresh: false` → pagination (loading indicator at list bottom)

## Widget

```dart
class ItemInfiniteList extends HookConsumerWidget {
  const ItemInfiniteList({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final state = ref.watch(itemListProvider);
    final notifier = ref.watch(itemListProvider.notifier);

    final items = useMemoized(
      () => (state.value?.items ?? []).sorted(
        (a, b) => b.createdAt.compareTo(a.createdAt),
      ),
      [state],
    );

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

## InfiniteList Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `elements` | `List<T>` | Yes | Items to display |
| `itemBuilder` | `Widget Function(BuildContext, T)` | Yes | Builds each item |
| `onFetchData` | `void Function()` | Yes | Called near bottom to load more |
| `isLoading` | `bool` | Yes | Loading state |
| `hasError` | `bool` | Yes | Error state |
| `hasReachedMax` | `bool` | Yes | No more pages |
| `loadingBuilder` | `WidgetBuilder` | Yes | Loading UI |
| `errorBuilder` | `WidgetBuilder` | Yes | Error UI |
| `emptyBuilder` | `WidgetBuilder` | Yes | Empty state UI |
| `separator` | `Widget?` | No | Separator between items |
| `onRefresh` | `Future<void> Function()?` | No | Pull-to-refresh callback |
| `padding` | `EdgeInsets` | No | List padding (default `EdgeInsets.zero`) |
| `centerEmpty` | `bool` | No | Center empty widget (default `false`) |
| `centerLoading` | `bool` | No | Center loading widget (default `false`) |
| `fetchThreshold` | `double` | No | Distance to bottom before fetching (default `200`) |

## Filter Integration

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

### Filter-Aware Empty State

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

## Pull-to-Refresh

```dart
// Dismiss immediately
onRefresh: () async {
  ref.invalidate(itemListProvider);
},

// Wait for data before dismissing
onRefresh: () async {
  ref.invalidate(itemListProvider);
  return ref.read(itemListProvider.future);
},
```

## Checklist

### Result Model
- Extends `Equatable`
- `copyWith` uses `T? Function()?` for nullable fields
- Default: `items = const []`, `hasReachedMax = true`

### API
- Accepts `pageSize` and `pageToken`
- `hasReachedMax = response.length < pageSize`
- Empty `nextPageToken` → `null`
- DTO/proto to entity conversion in API layer

### Provider
- `@Riverpod(keepAlive: true)`
- `build()` fetches initial page, watches dependencies for auto-refresh
- `loadMore()` guards: `isLoading`, `hasReachedMax`
- `.retainPrevious(state, isRefresh: false)` for loading state
- `AsyncValue.guard()` for error handling
- `[...existing, ...new]` for immutable merge
- `ref.read()` (not `watch`) in `loadMore()`

### Widget
- Guard `state.value == null` for initial loading/error
- Pass `state.isLoading`, `state.hasError`, `state.value?.hasReachedMax` to `InfiniteList`
- `useMemoized` for expensive transforms (sorting, filtering)
- Error builder retries via `notifier.loadMore()`
- Empty builder filter-aware when filters exist
- `onRefresh` → `ref.invalidate(provider)`

### Filters
- Filter state extends `Equatable`
- Filter provider has `clearAll()` method
- List provider watches filter in `build()` for auto-refresh
- Empty state shows "clear filters" when filters active
