---
title: Composition Over Configuration
category: structure
impact: MEDIUM
impactDescription: Simplifies widget APIs
tags: composition, widget-api, god-widget, parameters
---

## Composition Over Configuration

Small focused widgets over god widgets with many flags. Use builders and slots instead of boolean parameters.

**Detection signals:**
- Widget has more than 6-8 parameters
- Boolean parameters that are mutually exclusive
- Widget is really 3 different widgets pretending to be 1
- Adding a new variant would require another boolean flag

**Incorrect (god widget):**

```dart
AppButton(
  label: 'Submit',
  isPrimary: true,
  isSecondary: false,
  isDestructive: false,
  isLoading: false,
  isDisabled: false,
  showIcon: true,
  iconPosition: IconPosition.left,
  size: ButtonSize.medium,
  // ... 10 more parameters
)
```

**Correct (composed widgets):**

```dart
// Separate widgets for distinct purposes
class PrimaryButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget child;
  final bool isLoading;

  const PrimaryButton({
    super.key,
    required this.onPressed,
    required this.child,
    this.isLoading = false,
  });

  // ...
}

// Composition for custom layouts
PrimaryButton(
  onPressed: handleSubmit,
  child: Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Icon(Icons.check),
      SizedBox(width: 8),
      Text('Submit'),
    ],
  ),
)

// Or slot-based API for common patterns
PrimaryButton.icon(
  icon: Icons.check,
  label: 'Submit',
  onPressed: handleSubmit,
)
```

**Alternative: Use sealed class for mutually exclusive variants:**

```dart
sealed class ButtonVariant {
  const ButtonVariant();
}
class PrimaryVariant extends ButtonVariant { ... }
class SecondaryVariant extends ButtonVariant { ... }
class DestructiveVariant extends ButtonVariant { ... }

class AppButton extends StatelessWidget {
  final ButtonVariant variant;
  final Widget child;
  final VoidCallback? onPressed;

  // Single widget, but variants are explicit and exhaustive
}
```

**Why it matters:**
- Each widget has one job
- New variants don't bloat existing widgets
- Easier to understand and test
- Flexible: compose for custom needs, use shortcuts for common ones

**Detection questions:**
- Does this widget have more than 6-8 parameters?
- Are there boolean parameters that are mutually exclusive?
- Is this widget really 3 different widgets pretending to be 1?
- Would adding a new variant require another boolean flag?
