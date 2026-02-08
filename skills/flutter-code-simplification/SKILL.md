---
name: flutter-code-simplification
description: Flutter/Dart code simplification principles. Use when simplifying, refactoring, or cleaning up Flutter code for clarity and maintainability.
license: MIT
metadata:
  author: Roland Tolnay
  version: "1.0.0"
  date: January 2026
  argument-hint: <file-or-pattern>
---

# Flutter Code Simplification

Principles and patterns for simplifying Flutter/Dart code. Simplification means making code easier to reason about — not making it shorter at the cost of clarity.

## Core Philosophy

**Clarity over brevity.** Explicit code is often better than compact code. The goal is code that's easy to read, understand, and maintain without changing what it does.

## Principles

### 1. Preserve Functionality

Never change what the code does — only how it does it. All original features, outputs, and behaviors must remain intact.

### 2. Enhance Clarity

- Reduce unnecessary complexity and nesting
- Eliminate redundant code and abstractions
- Improve readability through clear naming
- Consolidate related logic and duplicates (DRY)
- Choose clarity over brevity — explicit code is often better than compact code

### 3. Maintain Balance

Avoid over-simplification that could:
- Create overly clever solutions that are hard to understand
- Combine too many concerns into single functions/components
- Remove helpful abstractions that improve code organization
- Prioritize "fewer lines" over readability
- Make code harder to debug or extend

### 4. Apply Judgment

Use expertise to determine what improves the code. These principles guide decisions — they are not a checklist. If a change doesn't clearly improve clarity while preserving behavior, don't make it.

## Flutter Patterns

Common opportunities in Flutter/Dart code. Apply when they genuinely improve clarity.

### State & Data

| Pattern | Simplification |
|---------|----------------|
| Scattered boolean flags | Sealed class variants with switch expressions (when it consolidates and clarifies) |
| Same parameters repeated across functions | Records or typed classes |
| Manual try-catch in providers | `AsyncValue.guard()` with centralized error handling |
| Async operations without mount check | Check `ref.mounted` after async operations |

### Widget Structure

| Pattern | Simplification |
|---------|----------------|
| Large `build()` methods | Extract into local variables or builder methods |
| Widgets with many boolean parameters | Consider composition or typed mode objects |
| Unordered build() | Keep order: providers → hooks → derived values → widget tree |

### Collections

| Pattern | Simplification |
|---------|----------------|
| Mutation patterns | Immutable methods (`.sorted()`, `.where()`, etc.) |
| Null-unsafe access | `firstWhereOrNull` with fallbacks |
| Repeated enum switches | Computed properties on the enum itself |

### Code Organization

| Pattern | Simplification |
|---------|----------------|
| Duplicated logic across files | Extract to shared location |
| Related methods scattered in class | Group by concern |
| Unnecessary indirection (factories creating one type, wrappers adding no behavior) | Use concrete types directly |

**Exception:** API layer interfaces with implementation in same file are intentional — interface provides at-a-glance documentation.

## Output Format

Group by file. Use `file:line` format. Terse findings.

```text
## lib/home/home_screen.dart

lib/home/home_screen.dart:42 - scattered booleans -> sealed class
lib/home/home_screen.dart:67 - .toList()..sort() -> .sorted()
lib/home/home_screen.dart:120 - large build() -> extract builder methods

## lib/models/user.dart

pass
```

State issue + location. Skip explanation unless fix non-obvious. No preamble.
