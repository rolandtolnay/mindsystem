# Widget Refactor Style Guide

Use these rules when cleaning up or refactoring a Flutter widget so it becomes easier to read, maintain, and extend.

---

## 1) Breaking up a large `build()` method

### A. Use a **local variable** when there’s no conditional rendering

* If a widget is **always shown** (no `if`, no null checks), define it as a local variable.
* Define local widget variables in the **same order they appear on screen**.

**Why:** Keeps the “screen story” readable from top to bottom.

---

### B. Use a **function** when rendering depends on a condition

* If a widget is shown only when a condition is true (especially nullability checks), extract it into a function like `_buildXyz(...)`.
* This avoids:

  * Crashes from referencing null values too early
  * Building widgets that will never be shown

---

### C. Extract a **standalone widget** when a subtree is complex or reusable

Extract into its own widget when:

* The subtree is large enough to distract from the parent layout
* It’s reused in multiple places
* It manages its own state
* It’s a repeated item like:

  * list tiles in a `ListView`
  * cards in a grid

---

### D. No file-private widgets

* If something is big enough to become a widget, it must live in **its own file**.
* Don’t create “helper widgets” as private classes at the bottom of the same file.

**Rule of thumb:** extract → new widget → new file.

---

## 2) Preferred structure inside `build()`

Keep the top of `build()` consistent and predictable:

1. **Providers** (reads/watches)
2. **Hooks** (if using hooks)
3. **Derived variables** needed for rendering
4. **Widget variables** (in render order)

Additional rules:

* Define variables **as close to where they’re used as possible** (without making the method messy).
* If a condition is used inline and feels non-trivial, extract it into a well-named boolean.

**Example:**

```dart
final canSubmit = isValid && !isLoading && selectedId != null;
```

---

## 3) Where to define functions

### Default: define functions **outside** `build()`

* Helper methods like `_buildHeader(...)`, `_onSubmit(...)`, `_showErrorToast(...)` should usually be class methods, not nested inside `build()`.

### Exception: allow functions **inside** `build()` when parameter passing becomes unreasonable

* If a function would need lots of values passed in (especially multiple hooks), defining it inside `build()` is acceptable.

### Parameter rule

* If the function needs **3 parameters or fewer**, define it outside `build()`.
* More than 3 parameters can justify keeping it inside (if it would otherwise become noisy).

---

## 4) `WidgetRef` vs `BuildContext` parameters

* If a function needs both `WidgetRef` and `BuildContext`, **only pass `WidgetRef`**.
* Use `ref.context` to access the context inside the function.

**Goal:** reduce parameter clutter and keep call sites clean.

---

## 5) Async UX conventions

### A. Button loading states

* Implement loading indicators by watching the async provider state.
* Buttons should reflect loading directly from provider state (not separate local flags).

---

### B. Retriable errors triggered by a user action

If the user taps a button and it fails, and retrying is possible:

* Listen to the provider
* Show a toast/snackbar when it emits an error
* Let the user retry by tapping again

---

### C. Errors on first-load actions (non-retriable without UI)

If the action happens automatically on page load (e.g., fetching initial data) and you need a proper retry flow:

* Render an error view (empty/error state)
* Include a retry button
* Retry should invalidate the provider

---

## 6) Sorting and filtering rules

* Use an **enum** to represent sorting/filtering criteria when it’s simple.
* If each option needs additional properties/behavior, use a **sealed class** instead.
* For complex filtering:

  * Use a dedicated `Filter` class containing multiple filter properties.

**Goal:** keep filtering/sorting typed, explicit, and easy to extend without boolean soup.
