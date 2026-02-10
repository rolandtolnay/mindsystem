---
name: flutter-code-quality
description: Flutter/Dart code quality, widget organization, and folder structure guidelines. Use when reviewing, refactoring, or cleaning up Flutter code after implementation.
license: MIT
metadata:
  author: Roland Tolnay
  version: "1.0.0"
  date: January 2026
  argument-hint: <file-or-pattern>
---

# Flutter Code Quality

Comprehensive guidelines for Flutter/Dart code quality, widget organization, and folder structure. Combines pattern-level rules (anti-patterns, idioms) with structural guidance (build method organization, folder conventions).

## How It Works

1. Fetch flutter-code-quality-guidelines.md from the gist URL below (always fresh)
2. Apply embedded widget organization and folder structure rules
3. Check files against all guidelines
4. Output findings in terse `file:line` format

## Code Quality Guidelines (Remote)

Fetch fresh guidelines before each review:

```bash
gh api /gists/edf9ea7d5adf218f45accb3411f0627c \
  --jq '.files["flutter-code-quality-guidelines.md"].content'
```

Never use WebFetch for gist content — it summarizes instead of returning raw text. Contains: anti-patterns, widget patterns, state management, collections, hooks, theme/styling, etc.

## Widget Organization Guidelines (Embedded)

### Build Method Structure

Order inside `build()`:
1. Providers (reads/watches)
2. Hooks (if using flutter_hooks)
3. Derived variables needed for rendering
4. Widget variables (in render order)

### When to Use What

| Scenario | Pattern |
|----------|---------|
| Widget always shown, no conditions | Local variable: `final header = Container(...);` |
| Widget depends on condition/null check | Builder function: `Widget? _buildContent() { if (data == null) return null; ... }` |
| Subtree is large, reusable, or has own state | Extract to standalone widget in own file |
| Function needs 3 or fewer params | Define outside `build()` as class method |
| Function needs 4+ params (esp. hooks) | Define inside `build()` to capture scope |

### Rules

- **No file-private widgets** - If big enough to be a widget, it gets its own file
- **Define local variables in render order** - Top-to-bottom matches screen layout
- **Extract non-trivial conditions** - `final canSubmit = isValid && !isLoading && selectedId != null;`
- **Pass `WidgetRef` only** when function needs both ref and context - Use `ref.context` inside

### Async UX Conventions

- **Button loading** - Watch provider state, not separate `useState<bool>`
- **Retriable errors** - Listen to provider, show toast on error, user retries by tapping again
- **First-load errors** - Render error view with retry button that invalidates provider

### Sorting/Filtering

- Simple options: Use enum with computed properties
- Options with behavior: Use sealed class
- Complex multi-field filtering: Dedicated `Filter` class

## Folder Structure Guidelines (Embedded)

### Core Rules

1. **Organize by feature** - Each feature gets its own folder
2. **Screens at feature root** - `account_screen.dart`, `edit_account_screen.dart`
3. **Create subfolders only when justified:**
   - `widgets/` when 2+ reusable widgets exist
   - `providers/` when 2+ provider files exist
   - `domain/` usually always (models, repositories)
4. **Split large features into subfeatures** - Each subfeature follows same rules

### Example

```
lib/features/
  account/
    account_screen.dart
    edit_account_screen.dart
    widgets/
      account_avatar.dart
      account_form.dart
    providers/
      account_provider.dart
    domain/
      account.dart
      account_repository.dart
```

## Application Priority

When reviewing code, apply in this order:

1. **Code Quality Patterns** (from fetched gist) - Anti-patterns, idioms, provider patterns
2. **Widget Organization** (above) - Build structure, extraction rules, async UX
3. **Folder Structure** (above) - File placement, feature boundaries

## Anti-Patterns Quick Reference

Flag these patterns (details in fetched guidelines):

- `useState<bool>` for loading states
- Manual try-catch in provider actions
- `.toList()..sort()` instead of `.sorted()`
- `_handleAction(ref, controller, user, state)` with 4+ params
- Hardcoded hex colors
- Deep `lib/features/x/presentation/` directories
- Barrel files that only re-export
- Boolean flags instead of sealed classes
- Magic numbers scattered across widgets
- `where((e) => e.status == Status.active)` instead of computed property
- Generic provider names like `expansionVisibilityProvider`
- `.asData?.value` instead of `.value`

## Output Format

Group by file. Use `file:line` format. Terse findings.

```text
## lib/home/home_screen.dart

lib/home/home_screen.dart:42 - useState for loading state -> use provider
lib/home/home_screen.dart:67 - .toList()..sort() -> .sorted()
lib/home/home_screen.dart:89 - hardcoded Color(0xFF...) -> context.color.*

## lib/models/user.dart

pass
```

State issue + location. Skip explanation unless fix non-obvious. No preamble.
