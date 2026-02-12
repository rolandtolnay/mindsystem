<overview>
Mock patterns for manual UAT testing. Mocks are temporary inline edits to service methods — hardcoded return values that let you reach testable UI states. They exist only as uncommitted changes, never in commit history.
</overview>

<classification_framework>

**Two-question framework for mock classification:**

For each test, ask two questions in order:

1. **Is the observable state transient?**
   - Does it appear briefly during async operations? (loading skeleton, spinner, transition animation)
   - Does it require precise timing to observe? (appears for <1s before real data loads)
   - If YES → `mock_type: "transient_state"` — needs delay/force mock strategy

2. **Does the test depend on external data?**
   - Does the feature fetch from an API, database, or external service?
   - Would the test fail without specific data existing locally?
   - If YES → `mock_type: "external_data"` — confirm data availability with user first

**Two-tier classification priority:**

| Priority | Source | When used |
|----------|--------|-----------|
| 1 | SUMMARY.md `mock_hints` | Executor captured hints at build time (including `none` for explicit no-mock) |
| 2 | Inline classification + keyword heuristics | No `mock_hints` key (legacy summaries) — classify in main context using two-question framework + keywords |

**Why keyword matching alone fails:**

Domain terms don't map reliably to mock types. "View recipe list" needs external_data mocks but contains no keywords. "Loading skeleton" is transient_state but keyword matching might miss the underlying async dependency. The two-question framework traces UI elements to their data sources instead of pattern-matching descriptions.

**Category examples:**

| Test | Classification | Reasoning |
|------|---------------|-----------|
| "Recipe list loading skeleton" | transient_state | Brief UI state during async fetch — resolves in <1s |
| "View recipe list" | external_data | Fetches from /api/recipes — data may not exist locally |
| "Login error message" | error_state | Error response from auth endpoint |
| "Empty favorites placeholder" | empty_response | Requires zero items in collection |
| "Premium badge display" | premium_user | Requires premium subscription state |
| "Offline sync indicator" | offline_state | Requires network disconnection |
| "Tap login button" | no mock needed | Happy path with available test credentials |

</classification_framework>

<mock_types>

| Mock Type | Enables Testing | Inline Pattern |
|-----------|-----------------|----------------|
| `error_state` | Error messages, retry UI, fallback displays | Throw exception before real implementation |
| `premium_user` | Premium badges, gated features, upgrade prompts | Return mock user object with premium fields |
| `empty_response` | Empty states, placeholder UI, "no results" | Return empty list/null before real implementation |
| `loading_state` | Loading spinners, skeleton screens | Add delay before real implementation |
| `offline` | Offline UI, cached data, sync indicators | Throw network error before real implementation |
| `transient_state` | Brief async states (loading skeletons, transitions) | Delay or never-resolve strategies (see below) |
| `external_data` | Features depending on API data that may not exist locally | Return hardcoded data objects |

</mock_types>

<inline_mock_patterns>

**Inline mocks edit service methods directly.** Add hardcoded return values BEFORE the real implementation. Mark with `// MOCK:` comment for cleanup tracking.

**Pattern:** Early return with mock comment
```
// MOCK: {description} — revert after UAT
{hardcoded return/throw}

// Real implementation below...
```

**By mock_type:**

**error_state** — Throw before real call:
```dart
// Before:
Future<User> login(String email, String password) async {
  final response = await _api.post('/auth/login', data: {'email': email, 'password': password});
  return User.fromJson(response.data);
}

// After:
Future<User> login(String email, String password) async {
  // MOCK: force login error — revert after UAT
  throw Exception('Invalid credentials');

  final response = await _api.post('/auth/login', data: {'email': email, 'password': password});
  return User.fromJson(response.data);
}
```

**empty_response** — Return empty collection:
```dart
// Before:
Future<List<Recipe>> getRecipes() async {
  final response = await _api.get('/recipes');
  return response.data.map((j) => Recipe.fromJson(j)).toList();
}

// After:
Future<List<Recipe>> getRecipes() async {
  // MOCK: force empty list — revert after UAT
  return [];

  final response = await _api.get('/recipes');
  return response.data.map((j) => Recipe.fromJson(j)).toList();
}
```

**premium_user / external_data** — Return hardcoded object:
```dart
// Before:
Future<User> getCurrentUser() async {
  final response = await _api.get('/user/me');
  return User.fromJson(response.data);
}

// After:
Future<User> getCurrentUser() async {
  // MOCK: force premium user — revert after UAT
  return User(id: 'mock-001', name: 'Test User', isPremium: true, tier: 'gold');

  final response = await _api.get('/user/me');
  return User.fromJson(response.data);
}
```

**TypeScript equivalents follow identical pattern** — early return/throw with `// MOCK:` comment before the real implementation.

</inline_mock_patterns>

<transient_state_patterns>

**Transient states are UI states that appear briefly during async operations.** Loading skeletons, shimmer effects, transition animations — they resolve too fast to observe and test manually.

**Two strategies:**

**1. Extended delay (default):**

Add a configurable delay before the real data returns. The transient state stays visible long enough to test.

```dart
// MOCK: extend loading state for testing — revert after UAT
await Future.delayed(const Duration(seconds: 5));

// Real implementation continues...
final response = await _api.get('/recipes');
return response.data.map((j) => Recipe.fromJson(j)).toList();
```

```typescript
// MOCK: extend loading state for testing — revert after UAT
await new Promise(resolve => setTimeout(resolve, 5000));

// Real implementation continues...
const response = await fetch('/api/recipes');
return response.json();
```

**When to use:** Testing that the loading UI (skeleton, spinner) displays correctly while waiting.

**2. Never-resolve:**

The async call never completes. The transient state stays permanently visible.

```dart
// MOCK: freeze loading state — revert after UAT
await Completer<void>().future; // Never completes

// Real implementation continues...
```

```typescript
// MOCK: freeze loading state — revert after UAT
await new Promise(() => {}); // Never resolves

// Real implementation continues...
```

**When to use:** Testing that the loading UI itself is correct (layout, styling, animation) without it disappearing.

**Choosing between strategies:**
- Testing the transition (loading → loaded): Use extended delay (5s default)
- Testing the loading UI appearance: Use never-resolve

</transient_state_patterns>

<git_stash_lifecycle>

**Why stash?**

Fixes must be clean commits (no mock code). But after fixing, mocks need to be restored to re-test. Git stash enables this:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Setup                                              │
├─────────────────────────────────────────────────────────────┤
│ 1. git stash push -m "pre-verify-work" (if dirty)          │
│ 2. Inline mocks applied to service methods (uncommitted)    │
│ 3. Mocked files tracked in UAT.md: mocked_files: [...]     │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Test-Fix Loop (per issue)                          │
├─────────────────────────────────────────────────────────────┤
│ 4. User tests on device with mocks active                   │
│ 5. User reports issue                                       │
│ 6. git stash push -m "mocks-batch-N" -- <mocked_files>     │
│ 7. Fixer investigates and commits fix  ← Clean commit      │
│ 8. git stash pop                       ← Restore mocks     │
│ 9. User re-tests specific item                             │
│ 10. Repeat until fixed or skip                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 3: Cleanup                                            │
├─────────────────────────────────────────────────────────────┤
│ 11. git checkout -- <mocked_files>     ← Revert mocks      │
│ 12. Generate UAT fixes patch                                │
│ 13. git stash pop (if pre-existing)    ← Restore user work │
└─────────────────────────────────────────────────────────────┘
```

**Stash naming convention:**
- `pre-verify-work` — User's original uncommitted work
- `mocks-batch-N` — Current mock state for batch N (stashed only during fix application)

</git_stash_lifecycle>

<conflict_resolution>

**When git stash pop conflicts:**

This happens when a fix modified the same file as a mock. Resolution:

```bash
# Conflict means fix touched mock code — take the fix version
git checkout --theirs <conflicted-file>
git add <conflicted-file>
```

**Why take fix version?**
- The fix is committed, intentional work
- The mock for that file is likely no longer needed (fix replaced relevant code)
- Regenerating mock for that specific file is easy if still needed

**This is rare.** Mocks typically live in data layer, fixes often in UI layer.

</conflict_resolution>
