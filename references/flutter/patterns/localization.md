# Localization

`easy_localization` with embedded code generation.

## Dependencies

```yaml
# pubspec.yaml
dependencies:
  easy_localization: ^3.0.8
  intl: ^0.20.2

dev_dependencies:
  easy_logger: ^0.0.2

flutter:
  assets:
    - assets/translations/
```

## File Structure

```
assets/translations/
  en.json
  es.json
lib/generated/translations/
  codegen_loader.g.dart    # Generated: embeds translations
  locale_keys.g.dart       # Generated: type-safe key constants
```

## Translation JSON

```json
{
  "app_name": "My App",
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "error": "Something went wrong"
  },
  "auth": {
    "sign_in": "Sign In",
    "welcome_back": "Welcome back, {name}!",
    "resend_code_x_s": "Resend code ({}s)"
  },
  "account": {
    "x_members": {
      "one": "{} member",
      "other": "{} members"
    }
  }
}
```

### Key Naming

- `snake_case` for all keys
- Hierarchical by feature: `feature.section.element`
- Prefix `x_` for keys with arguments: `x_members`, `resend_code_x_s`

### Interpolation

| Type | JSON | Dart |
|------|------|------|
| Positional | `"Hello, {}"` | `tr(key, args: ['World'])` |
| Named | `"Hello, {name}!"` | `tr(key, namedArgs: {'name': 'World'})` |

### Pluralization

```json
{
  "item_count": {
    "zero": "No items",
    "one": "{} item",
    "other": "{} items"
  }
}
```

Available keys: `zero`, `one`, `two`, `few`, `many`, `other`

## Code Generation

```bash
# Generate codegen_loader.g.dart
fvm dart run easy_localization:generate \
  -S assets/translations \
  -O lib/generated/translations

# Generate locale_keys.g.dart
fvm dart run easy_localization:generate \
  -S assets/translations \
  -O lib/generated/translations \
  -f keys \
  -o locale_keys.g.dart
```

Generated `locale_keys.g.dart`:

```dart
abstract class LocaleKeys {
  static const app_name = 'app_name';
  static const common_save = 'common.save';
  static const auth_sign_in = 'auth.sign_in';
  static const auth_welcome_back = 'auth.welcome_back';
  static const account_x_members = 'account.x_members';
}
```

Key path: `auth.welcome_back` → constant `auth_welcome_back`

## App Initialization

```dart
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeDateFormatting();

  EasyLocalization.logger.enableLevels = [
    LevelMessages.error,
    LevelMessages.warning,
  ];

  await EasyLocalization.ensureInitialized();

  runApp(
    EasyLocalization(
      supportedLocales: const [Locale('en'), Locale('es')],
      path: 'lib/generated/translations',
      assetLoader: const CodegenLoader(),
      fallbackLocale: const Locale('en'),
      useOnlyLangCode: true,
      child: const MyApp(),
    ),
  );
}
```

```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      localizationsDelegates: context.localizationDelegates,
      supportedLocales: context.supportedLocales,
      locale: context.locale,
      title: tr(LocaleKeys.app_name),
      home: const HomeScreen(),
    );
  }
}
```

## Usage

```dart
import 'package:easy_localization/easy_localization.dart';
import 'package:myapp/generated/translations/locale_keys.g.dart';
```

| Operation | Code |
|-----------|------|
| Simple text | `tr(LocaleKeys.common_save)` |
| Positional args | `tr(LocaleKeys.key, args: ['value'])` |
| Named args | `tr(LocaleKeys.key, namedArgs: {'name': 'value'})` |
| Pluralization | `plural(LocaleKeys.key, count)` |
| Get locale | `context.locale` |
| Set locale | `context.setLocale(Locale('en'))` |
| Reset locale | `context.resetLocale()` |

`tr()` works without `BuildContext` — usable in services, models, etc.
