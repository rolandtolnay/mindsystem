<overview>
Mock patterns for manual UAT testing. Mocks are temporary scaffolding to reach testable UI states. They exist only as uncommitted changes — never in commit history.
</overview>

<philosophy>
**Mocks enable testing states you can't easily reach.**

Without mocks, testing "error message display" requires actually triggering server errors. Testing "premium user badge" requires a premium account. Testing "empty list placeholder" requires deleting all data.

**With mocks:** Set a flag, hot reload, test the UI state.

**Core principles:**
1. **Temporary** — Mocks are stashed/discarded, never committed
2. **Minimal** — One override file, minimal production hooks
3. **Explicit** — Clear flags, clear toggle instructions
4. **Removable** — Delete file + remove imports = clean
</philosophy>

<git_stash_lifecycle>

**Why stash?**

Fixes must be clean commits (no mock code). But after fixing, we need mocks back to re-test. Git stash enables this:

```
┌─────────────────────────────────────────────────────────────┐
│ Phase 1: Setup                                              │
├─────────────────────────────────────────────────────────────┤
│ 1. git stash push -m "pre-verify-work" (if dirty)          │
│ 2. Mock Generator creates mock code (uncommitted)           │
│ 3. User confirms mocks look correct                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│ Phase 2: Test-Fix Loop (per issue)                          │
├─────────────────────────────────────────────────────────────┤
│ 4. User tests on device with mocks active                   │
│ 5. User reports issue                                       │
│ 6. git stash push -m "mocks-batch-N"  ← Stash mocks        │
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
│ 11. git stash drop                     ← Discard mocks     │
│ 12. Generate UAT fixes patch                                │
│ 13. git stash pop (if pre-existing)    ← Restore user work │
└─────────────────────────────────────────────────────────────┘
```

**Stash naming convention:**
- `pre-verify-work` — User's original uncommitted work
- `mocks-batch-N` — Current mock state for batch N

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

<flutter_example>

**Override file: `lib/test_overrides.dart`**

```dart
// Test Overrides - DELETE THIS FILE BEFORE COMMITTING
// Used for manual UAT testing only

class TestOverrides {
  // === STATE FLAGS ===
  static bool forcePremiumUser = false;
  static bool forceErrorState = false;
  static bool forceEmptyResponse = false;
  static bool forceLoadingState = false;

  // === MOCK DATA ===
  static String mockErrorMessage = 'Simulated error for testing';
  static Duration mockLoadingDelay = const Duration(seconds: 3);

  static Map<String, dynamic> mockPremiumUser = {
    'id': 'test-user-001',
    'name': 'Test Premium User',
    'isPremium': true,
    'subscriptionTier': 'gold',
  };

  // === RESET ===
  static void reset() {
    forcePremiumUser = false;
    forceErrorState = false;
    forceEmptyResponse = false;
    forceLoadingState = false;
  }
}
```

**Production hook: `lib/services/user_service.dart`**

```dart
import '../test_overrides.dart';

class UserService {
  Future<User> getCurrentUser() async {
    // TEST OVERRIDE - Remove before commit
    if (TestOverrides.forcePremiumUser) {
      return User.fromJson(TestOverrides.mockPremiumUser);
    }

    // Real implementation
    final response = await _api.get('/user/me');
    return User.fromJson(response.data);
  }

  Future<List<Item>> getItems() async {
    // TEST OVERRIDE - Remove before commit
    if (TestOverrides.forceEmptyResponse) {
      return [];
    }
    if (TestOverrides.forceErrorState) {
      throw Exception(TestOverrides.mockErrorMessage);
    }

    // Real implementation
    final response = await _api.get('/items');
    return (response.data as List).map((j) => Item.fromJson(j)).toList();
  }
}
```

**Toggle instructions:**

```
To enable Premium User state:
1. Open lib/test_overrides.dart
2. Set TestOverrides.forcePremiumUser = true
3. Hot reload (r in terminal)
4. Verify: User profile shows "Premium" badge

To enable Error State:
1. Open lib/test_overrides.dart
2. Set TestOverrides.forceErrorState = true
3. Hot reload (r in terminal)
4. Verify: Error message appears on relevant screens
```

</flutter_example>

<react_example>

**Override file: `src/testOverrides.ts`**

```typescript
// Test Overrides - DELETE THIS FILE BEFORE COMMITTING
// Used for manual UAT testing only

export const testOverrides = {
  // === STATE FLAGS ===
  forcePremiumUser: false,
  forceErrorState: false,
  forceEmptyResponse: false,
  forceLoadingState: false,

  // === MOCK DATA ===
  mockErrorMessage: 'Simulated error for testing',
  mockLoadingDelayMs: 3000,

  mockPremiumUser: {
    id: 'test-user-001',
    name: 'Test Premium User',
    isPremium: true,
    subscriptionTier: 'gold',
  },

  // === RESET ===
  reset() {
    this.forcePremiumUser = false;
    this.forceErrorState = false;
    this.forceEmptyResponse = false;
    this.forceLoadingState = false;
  },
};
```

**Production hook: `src/services/userService.ts`**

```typescript
import { testOverrides } from '../testOverrides';

export async function getCurrentUser(): Promise<User> {
  // TEST OVERRIDE - Remove before commit
  if (testOverrides.forcePremiumUser) {
    return testOverrides.mockPremiumUser as User;
  }

  // Real implementation
  const response = await fetch('/api/user/me');
  return response.json();
}

export async function getItems(): Promise<Item[]> {
  // TEST OVERRIDE - Remove before commit
  if (testOverrides.forceEmptyResponse) {
    return [];
  }
  if (testOverrides.forceErrorState) {
    throw new Error(testOverrides.mockErrorMessage);
  }

  // Real implementation
  const response = await fetch('/api/items');
  return response.json();
}
```

**Toggle instructions:**

```
To enable Premium User state:
1. Open src/testOverrides.ts
2. Set forcePremiumUser: true
3. Save file (auto hot reload in dev mode)
4. Verify: User profile shows "Premium" badge

To enable Error State:
1. Open src/testOverrides.ts
2. Set forceErrorState: true
3. Save file (auto hot reload)
4. Verify: Error message appears on relevant screens
```

</react_example>

<best_practices>

**Do:**
- Keep all flags in one file
- Use descriptive flag names (`forcePremiumUser` not `flag1`)
- Add comments marking test-only code
- Provide reset function
- Document toggle instructions clearly

**Don't:**
- Create complex mock infrastructure
- Add mocks in UI components (use service layer)
- Commit mock code (ever)
- Create multiple override files
- Add conditional compilation / build flags

**Signs you're over-engineering:**
- More than one override file
- Mock code in more than 3 production files
- Complex mock data generators
- Mocking at multiple layers simultaneously

</best_practices>

<cleanup>

**After UAT complete:**

1. `git stash drop` — Removes mock stash permanently
2. Delete override file if still present
3. Remove any imports/hooks still in production code

**Verification:**
```bash
git status  # Should show no mock-related files
grep -r "testOverrides" src/  # Should find nothing (or only the override file itself)
```

</cleanup>
