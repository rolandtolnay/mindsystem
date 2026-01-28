---
title: Speculative Generality
category: pragmatism
impact: MEDIUM
impactDescription: Reduces unnecessary complexity
tags: abstraction, yagni, over-engineering, interfaces
---

## Speculative Generality (Know When NOT to Abstract)

Don't abstract until 2-3 concrete cases exist. Build for today's requirements; extract abstractions when you have real examples.

**Detection signals:**
- Interface with only one implementation
- Factory that only creates one type
- Configuration options no one uses
- Abstraction added "in case we need it later"

**Incorrect (premature abstraction):**

```dart
// "We might need different storage backends someday"
abstract class StorageStrategy {
  Future<void> save(String key, String value);
  Future<String?> load(String key);
}

class LocalStorageStrategy implements StorageStrategy {
  @override
  Future<void> save(String key, String value) => _prefs.setString(key, value);

  @override
  Future<String?> load(String key) => _prefs.getString(key);
}

class StorageFactory {
  static StorageStrategy create(StorageType type) => switch (type) {
    StorageType.local => LocalStorageStrategy(), // Only one ever used
  };
}

// "We might need to support multiple payment providers"
abstract class PaymentProvider { ... }
class StripeProvider implements PaymentProvider { ... } // Only one exists
```

**Correct (direct usage):**

```dart
// Just use the thing directly
class LocalStorage {
  final SharedPreferences _prefs;

  LocalStorage(this._prefs);

  Future<void> save(String key, String value) => _prefs.setString(key, value);
  Future<String?> load(String key) async => _prefs.getString(key);
}

// When you ACTUALLY need a second implementation, THEN abstract
// The refactoring is straightforward and you'll know the right abstraction
// because you have concrete examples of the variation
```

**When TO abstract:**

```dart
// You have 2+ real implementations with actual differences
abstract class AuthProvider {
  Future<User> signIn();
  Future<void> signOut();
}

class GoogleAuthProvider implements AuthProvider { ... }
class AppleAuthProvider implements AuthProvider { ... }
class EmailAuthProvider implements AuthProvider { ... }

// The abstraction is earned - you know exactly what varies
```

**Why it matters:**
- Less code to maintain
- Abstractions based on real needs fit better
- Easier to understand: no indirection to trace
- YAGNI: You Aren't Gonna Need It

**Detection questions:**
- Is there an interface with only one implementation?
- Is there a factory that only creates one type?
- Are there configuration options no one uses?
- Was this abstraction added "in case we need it later"?
