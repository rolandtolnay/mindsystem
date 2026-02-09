<purpose>
Generate framework-specific mock code for manual UAT testing. Creates override files with toggle flags and minimal production hooks.

Called by verify-work workflow when a test batch requires mock state.
</purpose>

<philosophy>
**Mocks are temporary scaffolding.**

They exist only as uncommitted changes during testing. They enable reaching UI states that require specific backend conditions (premium user, error states, empty lists, loading states).

**Principles:**
- Minimal footprint: One override file + minimal hooks
- Easy removal: Delete file, remove imports, done
- Framework-appropriate: Match project conventions
- User-controlled: Clear toggle instructions
</philosophy>

<framework_detection>

**Step 1: Read PROJECT.md**
```bash
cat .planning/PROJECT.md 2>/dev/null | head -50
```

**Step 2: Verify with config files**

| Check | Indicates |
|-------|-----------|
| `pubspec.yaml` exists | Flutter |
| `package.json` has `"react"` or `"next"` | React/Next.js |
| `package.json` has `"react-native"` | React Native |
| `package.json` has `"vue"` | Vue |

**Step 3: Determine file locations**

| Framework | Override File | Import Pattern |
|-----------|---------------|----------------|
| Flutter | `lib/test_overrides.dart` | `import 'package:{app}/test_overrides.dart';` |
| React/Next.js | `src/testOverrides.ts` | `import { testOverrides } from '@/testOverrides';` |
| React Native | `src/testOverrides.ts` | `import { testOverrides } from '../testOverrides';` |
| Vue | `src/testOverrides.ts` | `import { testOverrides } from '@/testOverrides';` |

</framework_detection>

<override_file_pattern>

**Structure:**

```
// Test Overrides - DELETE THIS FILE BEFORE COMMITTING
// Used for manual UAT testing only

// === STATE FLAGS ===
// Set to true to enable mock state

{flag declarations based on mock_type}

// === MOCK DATA ===
// Returned when flags are true

{mock data structures}

// === RESET ===
// Call to disable all overrides

{reset function}
```

**Flag naming convention:**
- `force{State}` for boolean flags (e.g., `forcePremiumUser`, `forceErrorState`)
- `mock{DataType}` for mock data (e.g., `mockUserData`, `mockErrorMessage`)

</override_file_pattern>

<production_hook_pattern>

**Minimal hooks at service/repository layer:**

```
// Check override BEFORE real implementation
if (testOverrides.force{State}) {
  return testOverrides.mock{Data};
}

// Real implementation continues here...
```

**Placement:**
- In services/repositories, not UI components
- At the data fetch point, not the render point
- Single if-check, no complex branching

**Marking:**
```
// TEST OVERRIDE - Remove before commit
if (testOverrides.forceError) {
  throw testOverrides.mockError;
}
```

</production_hook_pattern>

<mock_types>

Common mock types and what they enable:

| Mock Type | Enables Testing | Typical Flags |
|-----------|-----------------|---------------|
| `error_state` | Error messages, retry UI, fallback displays | `forceError`, `mockErrorMessage` |
| `premium_user` | Premium badges, gated features, upgrade prompts | `forcePremium`, `mockPremiumData` |
| `empty_response` | Empty states, placeholder UI, "no results" | `forceEmpty` |
| `loading_state` | Loading spinners, skeleton screens | `forceLoading`, `mockLoadingDelay` |
| `offline` | Offline UI, cached data, sync indicators | `forceOffline` |
| `transient_state` | Brief async states (loading skeletons, transitions) | `forceTransient`, `mockTransientDelay` |
| `external_data` | Features depending on API data that may not exist locally | `forceMockData`, `mockDataSet` |

</mock_types>

<transient_state_patterns>

**Transient states are UI states that appear briefly during async operations.** Loading skeletons, shimmer effects, transition animations — they resolve too fast to observe and test manually.

**Two mock strategies:**

**1. Extended delay strategy (default):**

Add a configurable delay before the real data returns. The transient state stays visible long enough to test.

```dart
// Flutter — Completer-based delay
Future<List<Recipe>> getRecipes() async {
  // TEST OVERRIDE - Extend loading state for testing
  if (TestOverrides.forceTransientState) {
    await Future.delayed(TestOverrides.mockTransientDelay); // default 5s
  }
  // Real implementation continues...
  final response = await _api.get('/recipes');
  return response.data.map((j) => Recipe.fromJson(j)).toList();
}
```

```typescript
// React/Next.js — Promise delay
async function getRecipes(): Promise<Recipe[]> {
  // TEST OVERRIDE - Extend loading state for testing
  if (testOverrides.forceTransientState) {
    await new Promise(resolve => setTimeout(resolve, testOverrides.mockTransientDelayMs));
  }
  // Real implementation continues...
  const response = await fetch('/api/recipes');
  return response.json();
}
```

**When to use:** Testing that the loading UI (skeleton, spinner) displays correctly while waiting.

**2. Never-resolve strategy:**

The async call never completes. The transient state stays permanently visible.

```dart
// Flutter — Completer that never completes
Future<List<Recipe>> getRecipes() async {
  // TEST OVERRIDE - Never resolve, keep loading state visible
  if (TestOverrides.forceTransientState && TestOverrides.mockTransientDelay == Duration.zero) {
    await Completer<void>().future; // Never completes
  }
  // Real implementation continues...
}
```

```typescript
// JS — Promise that never resolves
async function getRecipes(): Promise<Recipe[]> {
  // TEST OVERRIDE - Never resolve, keep loading state visible
  if (testOverrides.forceTransientState && testOverrides.mockTransientDelayMs === 0) {
    await new Promise(() => {}); // Never resolves
  }
  // Real implementation continues...
}
```

**When to use:** Testing that the loading UI itself is correct (layout, styling, animation) without it disappearing.

**Choosing between strategies:**
- Testing the transition (loading → loaded): Use extended delay (5s default)
- Testing the loading UI appearance: Use never-resolve (set delay to 0)

</transient_state_patterns>

<toggle_instructions_template>

**Format for each mock state:**

```markdown
**To enable {state_name}:**
1. Open `{override_file_path}`
2. Set `{flag_name} = true`
3. {Hot reload command or restart instruction}
4. Verify: {What user should see to confirm mock is active}

**To disable:**
1. Set `{flag_name} = false`
2. {Hot reload / restart}
```

**Framework-specific apply instructions:**

| Framework | Apply Changes |
|-----------|---------------|
| Flutter | Hot reload (r in terminal) or hot restart (R) |
| React/Next.js (dev) | Auto hot reload on save |
| React Native | Shake device → Reload, or `r` in Metro |
| Vue (dev) | Auto hot reload on save |

</toggle_instructions_template>

<spawn_mock_generator>

When verify-work needs mocks:

```
Task(
  prompt="""
You are generating test mocks for manual UI verification.

## Context

Project type: {detected_framework}
Phase: {phase_name}
Mock type needed: {mock_type}

## Tests requiring this mock

{test_list_with_expected_behavior}

## Requirements

1. Create override file at standard location for this framework
2. Add minimal hooks to relevant services (if needed)
3. Provide clear toggle instructions
4. Write all files to disk

Follow the patterns from @~/.claude/mindsystem/workflows/generate-mocks.md
""",
  subagent_type="ms-mock-generator",
  description="Generate {mock_type} mocks"
)
```

</spawn_mock_generator>

<success_criteria>
- [ ] Framework correctly detected
- [ ] Override file created at standard location
- [ ] Minimal hooks added (only if needed)
- [ ] Toggle instructions clear and complete
- [ ] Files written to disk (uncommitted)
- [ ] Easy to remove (clear cleanup path)
</success_criteria>
