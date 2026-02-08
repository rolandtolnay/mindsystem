# Easy Localization Target Setup

This document describes the target localization implementation using `easy_localization` with embedded code generation. Use this as a specification for migrating any Flutter app to this setup.

---

## Package Dependencies

```yaml
# pubspec.yaml
dependencies:
  easy_localization: ^3.0.8
  intl: ^0.20.2

dev_dependencies:
  easy_logger: ^0.0.2  # Optional: control logging verbosity

flutter:
  assets:
    - assets/translations/
```

---

## File Structure

```
project/
├── assets/
│   └── translations/
│       ├── en.json        # English translations
│       ├── es.json        # Spanish translations (one file per language)
│       └── ...
├── lib/
│   └── generated/
│       └── translations/
│           ├── codegen_loader.g.dart   # Generated: embeds translations
│           └── locale_keys.g.dart      # Generated: type-safe key constants
```

---

## Translation JSON Format

Translations are stored in JSON files with hierarchical structure organized by feature.

### File: `assets/translations/en.json`

```json
{
  "app_name": "My App",
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "error": "Something went wrong",
    "loading": "Loading..."
  },
  "auth": {
    "sign_in": "Sign In",
    "sign_out": "Sign Out",
    "welcome_back": "Welcome back, {name}!",
    "resend_code_x_s": "Resend code ({}s)"
  },
  "account": {
    "x_members": {
      "one": "{} member",
      "other": "{} members"
    }
  },
  "invoice": {
    "x_days_past_due": {
      "one": "{} day past due",
      "other": "{} days past due"
    }
  }
}
```

### Key Naming Convention

- Use `snake_case` for all keys
- Organize hierarchically by feature: `feature.section.element`
- Prefix with `x_` for keys that take arguments: `x_members`, `resend_code_x_s`

### Interpolation Syntax

| Type | JSON Syntax | Dart Usage |
|------|-------------|------------|
| Positional | `"Hello, {}"` | `tr(key, args: ['World'])` |
| Named | `"Hello, {name}!"` | `tr(key, namedArgs: {'name': 'World'})` |

### Pluralization Syntax

Use nested objects with plural form keys:

```json
{
  "item_count": {
    "zero": "No items",
    "one": "{} item",
    "other": "{} items"
  }
}
```

Available plural keys: `zero`, `one`, `two`, `few`, `many`, `other`

---

## Code Generation

### Commands

Run after modifying any JSON translation file:

```bash
# Generate codegen_loader.g.dart (embeds all translations in compiled code)
fvm dart run easy_localization:generate \
  -S assets/translations \
  -O lib/generated/translations

# Generate locale_keys.g.dart (type-safe key constants)
fvm dart run easy_localization:generate \
  -S assets/translations \
  -O lib/generated/translations \
  -f keys \
  -o locale_keys.g.dart
```

### Generated: `locale_keys.g.dart`

```dart
// DO NOT EDIT. This is code generated via package:easy_localization/generate.dart
abstract class LocaleKeys {
  static const app_name = 'app_name';
  static const common_save = 'common.save';
  static const common_cancel = 'common.cancel';
  static const common_error = 'common.error';
  static const auth_sign_in = 'auth.sign_in';
  static const auth_welcome_back = 'auth.welcome_back';
  static const auth_resend_code_x_s = 'auth.resend_code_x_s';
  static const account_x_members = 'account.x_members';
  static const invoice_x_days_past_due = 'invoice.x_days_past_due';
}
```

Key transformation: JSON path `auth.welcome_back` → Dart constant `auth_welcome_back`

### Generated: `codegen_loader.g.dart`

```dart
// DO NOT EDIT. This is code generated via package:easy_localization/generate.dart
import 'package:easy_localization/easy_localization.dart';

class CodegenLoader extends AssetLoader {
  const CodegenLoader();

  @override
  Future<Map<String, dynamic>?> load(String path, Locale locale) {
    return Future.value(mapLocales[locale.languageCode]);
  }

  static const Map<String, dynamic> _en = {
    "app_name": "My App",
    "common": {"save": "Save", "cancel": "Cancel", ...},
    ...
  };

  static const Map<String, dynamic> _es = { ... };

  static const Map<String, Map<String, dynamic>> mapLocales = {
    "en": _en,
    "es": _es,
  };
}
```

---

## App Initialization

### Entry Point Setup

```dart
import 'package:easy_localization/easy_localization.dart';
import 'package:flutter/material.dart';
import 'package:intl/date_symbol_data_local.dart';

import '../../plugin/flutter-launchpad/patterns/generated/translations/codegen_loader.g.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize date formatting (required if using intl for dates)
  await initializeDateFormatting();

  // Suppress verbose logging (optional)
  EasyLocalization.logger.enableLevels = [
    LevelMessages.error,
    LevelMessages.warning,
  ];

  // Initialize easy_localization
  await EasyLocalization.ensureInitialized();

  runApp(
    EasyLocalization(
      supportedLocales: const [
        Locale('en'),
        Locale('es'),
      ],
      path: 'lib/generated/translations',
      assetLoader: const CodegenLoader(),
      fallbackLocale: const Locale('en'),
      useOnlyLangCode: true,
      child: const MyApp(),
    ),
  );
}
```

### MaterialApp Configuration

```dart
class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      // Required: wire up easy_localization
      localizationsDelegates: context.localizationDelegates,
      supportedLocales: context.supportedLocales,
      locale: context.locale,

      title: tr(LocaleKeys.app_name),
      home: const HomeScreen(),
    );
  }
}
```

---

## Usage Patterns

### Required Imports

```dart
import 'package:easy_localization/easy_localization.dart';
import 'package:myapp/generated/translations/locale_keys.g.dart';
```

### Simple Translation

```dart
Text(tr(LocaleKeys.common_save))

// Alternative extension syntax
Text(LocaleKeys.common_save.tr())
```

### Positional Arguments

For strings with `{}` placeholders:

```json
{ "resend_code_x_s": "Resend code ({}s)" }
```

```dart
tr(LocaleKeys.auth_resend_code_x_s, args: [remaining.toString()])
// Output: "Resend code (30s)"
```

### Named Arguments

For strings with `{name}` placeholders:

```json
{ "welcome_back": "Welcome back, {name}!" }
```

```dart
tr(LocaleKeys.auth_welcome_back, namedArgs: {'name': userName})
// Output: "Welcome back, John!"
```

### Pluralization

For plural forms:

```json
{
  "x_members": {
    "one": "{} member",
    "other": "{} members"
  }
}
```

```dart
plural(LocaleKeys.account_x_members, memberCount)
// Output: "1 member" or "5 members"
```

### Context-Free Usage

Unlike Flutter's built-in l10n, `tr()` works without `BuildContext`:

```dart
class PaymentService {
  String getErrorMessage() {
    return tr(LocaleKeys.common_error);  // No context needed
  }
}
```

---

## Language Switching

```dart
// Get current locale
final currentLocale = context.locale;

// Change locale
context.setLocale(const Locale('es'));

// Reset to device locale
context.resetLocale();
```

---

## Quick Reference

| Operation | Code |
|-----------|------|
| Simple text | `tr(LocaleKeys.key)` |
| With positional args | `tr(LocaleKeys.key, args: ['value'])` |
| With named args | `tr(LocaleKeys.key, namedArgs: {'name': 'value'})` |
| Pluralization | `plural(LocaleKeys.key, count)` |
| Get locale | `context.locale` |
| Set locale | `context.setLocale(Locale('en'))` |

---

## Summary

The target setup uses:
- **JSON files** in `assets/translations/` (one per language)
- **Embedded CodegenLoader** for zero-overhead runtime performance
- **Type-safe LocaleKeys** for compile-time key validation
- **Hierarchical key organization** by feature
- **Context-free `tr()` function** for translations anywhere in code
