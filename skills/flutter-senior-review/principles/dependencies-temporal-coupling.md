---
title: Temporal Coupling
category: dependencies
impact: MEDIUM
impactDescription: Catches misuse at compile time
tags: builder-pattern, type-state, initialization, sequence
---

## Temporal Coupling (Enforce Sequences)

Enforce operation sequences via types, not documentation. Make it impossible to call methods in the wrong order.

**Detection signals:**
- Methods that must be called before others
- Comments like "must call X first" or "call after Y"
- Objects can be in an "invalid" state between operations
- Tests have setup steps that could be forgotten

**Incorrect (implicit sequence):**

```dart
class PaymentProcessor {
  void init() { ... }
  void setAmount(int amount) { ... }
  void setCustomer(Customer c) { ... }
  Future<void> process() { ... } // Must call init, setAmount, setCustomer first!
}

// Easy to misuse:
final processor = PaymentProcessor();
processor.process(); // Boom - forgot to init
```

**Correct (builder pattern):**

```dart
class PaymentBuilder {
  int? _amount;
  Customer? _customer;

  PaymentBuilder withAmount(int amount) {
    _amount = amount;
    return this;
  }

  PaymentBuilder withCustomer(Customer c) {
    _customer = c;
    return this;
  }

  Payment build() {
    assert(_amount != null && _customer != null);
    return Payment(amount: _amount!, customer: _customer!);
  }
}

// Usage is clear
final payment = PaymentBuilder()
    .withAmount(100)
    .withCustomer(customer)
    .build();
```

**Correct (type-state pattern):**

```dart
// Types enforce valid sequences
class UninitializedProcessor {
  InitializedProcessor init(Config config) => InitializedProcessor(config);
}

class InitializedProcessor {
  final Config _config;
  InitializedProcessor(this._config);

  Future<Result> process(int amount, Customer c) async {
    // Can only be called on initialized processor
    return _processPayment(amount, c);
  }
}

// Misuse is a compile error
final processor = UninitializedProcessor();
processor.process(100, customer); // Error: process is not defined on UninitializedProcessor
```

**Why it matters:**
- Compiler catches misuse, not runtime
- Self-documenting: types show valid sequences
- Impossible to forget required steps
- Easier onboarding for new developers

**Detection questions:**
- Are there methods that must be called before others?
- Are there comments like "must call X first" or "call after Y"?
- Can objects be in an "invalid" state between operations?
- Do tests have setup steps that could be forgotten?
