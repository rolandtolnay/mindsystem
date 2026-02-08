# App Search Provider Guide

Client-side filtering for lists and picker sheets using `AppSearch` provider.

## Quick Start

### 1. Make Your Entity Searchable

Implement the `Searchable` interface with a `queryMatch` method:

```dart
class CustomerEntity extends Searchable {
  final String name;
  final String? email;

  @override
  int queryMatch(String query) {
    if (query.isEmpty) return 0;  // Return 0 when no query

    final q = query.toLowerCase();
    var result = 0;
    
    // Higher score = better match (shown first)
    if (name.toLowerCase().startsWith(q)) result = max(result, 4);
    if (email?.toLowerCase().startsWith(q) ?? false) result = max(result, 3);
    if (name.toLowerCase().contains(q)) result = max(result, 1);
    
    return result;  // 0 = no match (filtered out)
  }
}
```

### 2. Use in Widget

```dart
class MyListWidget extends HookConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final items = [...];  // Your list of Searchable items
    
    // Create provider instance with your items
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

## Match Score System

Return values indicate relevance (higher = shown first):

| Score | Meaning | Example |
|-------|---------|---------|
| 0 | No match | Filtered out |
| 1 | Weak match | Contains query |
| 2-3 | Medium match | Prefix starts with query |
| 4+ | Strong match | Exact match or primary field |

**Tip:** Use `max(result, score)` to accumulate the best match across multiple fields.

## Common Patterns

### Bottom Sheet Picker

For picker sheets where search is always active:

```dart
final searchProvider = appSearchProvider(countryList);
final filtered = ref.watch(searchProvider).items.cast<PhoneCountry>();

// Input triggers immediate filtering
ShadInput(
  autofocus: true,
  onChanged: (input) {
    ref.read(searchProvider.notifier).filterInput(input);
  },
)
```

### Searchable List with Toggle

For lists where search is optional:

```dart
final searchProvider = appSearchProvider(customers);
final filtered = ref.watch(searchProvider).items.cast<CustomerEntity>();

final searchController = useTextEditingController();
final searching = useState(false);

// Sync controller with provider
useAsyncEffectDisposing(() async {
  void updateQuery() {
    ref.read(searchProvider.notifier).filterInput(searchController.text);
  }
  searchController.addListener(updateQuery);
  return () => searchController.removeListener(updateQuery);
});

// Show filtered or full list based on search state
InfiniteList(
  itemCount: searching.value ? filtered.length : customers.length,
  itemBuilder: (_, index) {
    final item = searching.value ? filtered[index] : customers[index];
    return ItemTile(item: item);
  },
)
```

## Implementation Checklist

- [ ] Entity `extends Searchable` or `implements Searchable`
- [ ] `queryMatch` returns 0 for empty query (shows all items)
- [ ] `queryMatch` returns 0 for non-matches (filters out)
- [ ] `queryMatch` returns higher values for better matches
- [ ] Query is lowercased and trimmed before comparison
- [ ] Use `ref.watch(searchProvider)` for reactive updates
- [ ] Use `ref.read(searchProvider.notifier).filterInput()` to update filter

