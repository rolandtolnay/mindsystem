---
title: Provider Tree Architecture
category: dependencies
impact: MEDIUM
impactDescription: Clarifies data flow
tags: riverpod, provider, architecture, dependencies
---

## Provider Tree Architecture

Root -> branch -> leaf hierarchy for providers. Clear mental model of which providers depend on which.

**Mental model:**
- **Root providers**: Match app lifecycle, never disposed. Hold core entities (user, games, quests). Referenced from many places. Use `keepAlive: true`.
- **Branch providers**: Combine/filter/transform core data. May become "core" as app grows (e.g., `squadQuestsProvider`).
- **Leaf providers**: Screen-specific or ephemeral. Depend on branches, rarely watched by other providers.

**Detection signals:**
- Can't draw the provider dependency graph as a tree
- Circular or confusing dependency chains
- "Leaf" providers being watched by other providers
- Provider doing too much (should split into root + branch)

**Incorrect (flat, tangled):**

```dart
// Hard to trace what depends on what
final userProvider = ...;
final questsProvider = ...; // watches userProvider
final gamesProvider = ...; // watches userProvider
final filteredQuestsProvider = ...; // watches questsProvider, gamesProvider, some other provider
final screenStateProvider = ...; // watches 5 different providers
```

**Correct (tree structure):**

```dart
// Root (core entities, keepAlive: true)
@Riverpod(keepAlive: true)
Future<User> user(Ref ref) => ref.watch(authProvider.future).then((auth) => auth.user);

@Riverpod(keepAlive: true)
Future<List<Quest>> quests(Ref ref) async {
  final user = await ref.watch(userProvider.future);
  if (user == null) return [];
  return ref.watch(questsApiProvider).fetchQuests(user.id);
}

// Branch (derived/filtered, may become core as app grows)
@riverpod
Future<List<Quest>> squadQuests(Ref ref) async {
  final quests = await ref.watch(questsProvider.future);
  return quests.where((q) => q.type == QuestType.squad).toList();
}

@riverpod
Future<List<Quest>> soloQuests(Ref ref) async {
  final quests = await ref.watch(questsProvider.future);
  return quests.where((q) => q.type == QuestType.solo).toList();
}

// Leaf (screen-specific, ephemeral)
@riverpod
class SquadQuestScreenState extends _$SquadQuestScreenState {
  @override
  FutureOr<ScreenState> build() async {
    // Only watches branch providers
    final quests = await ref.watch(squadQuestsProvider.future);
    return ScreenState(quests: quests);
  }
  // Never watched by other providers
}
```

**Why it matters:**
- Clear mental model of data flow
- Predictable rebuild scope
- Easier to add new derived providers
- Natural place for each piece of logic

**Detection questions:**
- Can you draw the provider dependency graph as a tree?
- Are there circular or confusing dependency chains?
- Are "leaf" providers being watched by other providers?
- Is a provider doing too much (should it split into root + branch)?
