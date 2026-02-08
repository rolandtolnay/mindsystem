# Entity Search

Client-side filtering using `AppSearch` provider with `Searchable` interface.

## Make Entity Searchable

Implement `Searchable` with `queryMatch` returning relevance score (0 = no match, higher = shown first):

```dart
class CustomerEntity extends Searchable {
  final String name;
  final String? email;

  @override
  int queryMatch(String query) {
    if (query.isEmpty) return 0;

    final q = query.toLowerCase();
    var result = 0;

    if (name.toLowerCase().startsWith(q)) result = max(result, 4);
    if (email?.toLowerCase().startsWith(q) ?? false) result = max(result, 3);
    if (name.toLowerCase().contains(q)) result = max(result, 1);

    return result;
  }
}
```

## Match Scores

| Score | Meaning |
|-------|---------|
| 0 | No match (filtered out) |
| 1 | Weak (contains query) |
| 2-3 | Medium (field starts with query) |
| 4+ | Strong (primary field match) |

Use `max(result, score)` to accumulate best match across fields.

## Widget Usage

```dart
class MyListWidget extends HookConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items = [...];
    final searchProvider = appSearchProvider(items);
    final filtered = ref.watch(searchProvider).items.cast<MyEntity>();

    return Column(
      children: [
        ShadInput(
          onChanged: (input) {
            ref.read(searchProvider.notifier).filterInput(input);
          },
        ),
        Expanded(
          child: AppListView(items: filtered, ...),
        ),
      ],
    );
  }
}
```

## Patterns

### Bottom Sheet Picker

```dart
final searchProvider = appSearchProvider(countryList);
final filtered = ref.watch(searchProvider).items.cast<PhoneCountry>();

ShadInput(
  autofocus: true,
  onChanged: (input) {
    ref.read(searchProvider.notifier).filterInput(input);
  },
)
```

### Searchable List with Toggle

```dart
final searchProvider = appSearchProvider(customers);
final filtered = ref.watch(searchProvider).items.cast<CustomerEntity>();

final searchController = useTextEditingController();
final searching = useState(false);

useAsyncEffectDisposing(() async {
  void updateQuery() {
    ref.read(searchProvider.notifier).filterInput(searchController.text);
  }
  searchController.addListener(updateQuery);
  return () => searchController.removeListener(updateQuery);
});

InfiniteList(
  itemCount: searching.value ? filtered.length : customers.length,
  itemBuilder: (_, index) {
    final item = searching.value ? filtered[index] : customers[index];
    return ItemTile(item: item);
  },
)
```

## Checklist

- Entity implements `Searchable`
- `queryMatch` returns 0 for empty query and non-matches
- Higher scores for better matches
- Query lowercased before comparison
- `ref.watch(searchProvider)` for reactive updates
- `ref.read(searchProvider.notifier).filterInput()` to update filter
