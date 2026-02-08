# DTO/Entity Patterns

Comprehensive JSON serialization patterns using json_serializable, nullable handling, enum mapping, nested objects, and pagination response structures.

## Core Serialization Pattern

### json_serializable with Equatable

```dart
import 'package:equatable/equatable.dart';
import 'package:json_annotation/json_annotation.dart';

part '{entity}.g.dart';

@JsonSerializable(explicitToJson: true, includeIfNull: false)
class {Entity} extends Equatable {
  const {Entity}({
    required this.id,
    required this.name,
    this.description,
    this.createdAt,
    this.status = {Entity}Status.active,
  });

  factory {Entity}.fromJson(Map<String, dynamic> json) => _${Entity}FromJson(json);

  /// Unique identifier
  final String id;

  /// Display name
  final String name;

  /// Optional description
  final String? description;

  /// Creation timestamp (ISO 8601)
  @JsonKey(name: 'created_at')
  final DateTime? createdAt;

  /// Current status
  final {Entity}Status status;

  Map<String, dynamic> toJson() => _${Entity}ToJson(this);

  // Computed properties - not serialized
  bool get hasDescription => description?.isNotEmpty ?? false;
  bool get isActive => status == {Entity}Status.active;

  {Entity} copyWith({
    String? id,
    String? name,
    String? description,
    DateTime? createdAt,
    {Entity}Status? status,
  }) {
    return {Entity}(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      createdAt: createdAt ?? this.createdAt,
      status: status ?? this.status,
    );
  }

  @override
  List<Object?> get props => [id, name, description, createdAt, status];
}
```

**Key Annotations:**
- `explicitToJson: true` - Ensures nested objects call their toJson methods
- `includeIfNull: false` - Omits null fields from JSON output (smaller payloads)

## Field Name Mapping

### Snake Case to Camel Case

```dart
@JsonSerializable()
class User extends Equatable {
  const User({
    required this.id,
    required this.displayName,
    this.avatarUrl,
    this.createdAt,
    this.lastLoginAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);

  final String id;

  @JsonKey(name: 'display_name')
  final String displayName;

  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;

  @JsonKey(name: 'created_at')
  final DateTime? createdAt;

  @JsonKey(name: 'last_login_at')
  final DateTime? lastLoginAt;

  Map<String, dynamic> toJson() => _$UserToJson(this);

  @override
  List<Object?> get props => [id, displayName, avatarUrl, createdAt, lastLoginAt];
}
```

## DateTime Handling

### ISO 8601 (Default)

```dart
// json_serializable handles ISO 8601 natively
@JsonKey(name: 'created_at')
final DateTime? createdAt;

// Safe parsing in computed properties
DateTime? get verifiedAtDate => DateTime.tryParse(verifiedAt ?? '');
```

### Unix Timestamps

```dart
class TimestampConverter implements JsonConverter<DateTime?, int?> {
  const TimestampConverter();

  @override
  DateTime? fromJson(int? timestamp) {
    if (timestamp == null) return null;
    return DateTime.fromMillisecondsSinceEpoch(timestamp * 1000);
  }

  @override
  int? toJson(DateTime? date) {
    if (date == null) return null;
    return date.millisecondsSinceEpoch ~/ 1000;
  }
}

// Usage
@TimestampConverter()
@JsonKey(name: 'expires_at')
final DateTime? expiresAt;
```

## Enum Serialization

### @JsonValue Annotation

```dart
@JsonEnum(valueField: 'value')
enum {Entity}Status {
  @JsonValue('active')
  active('active'),

  @JsonValue('inactive')
  inactive('inactive'),

  @JsonValue('pending')
  pending('pending'),

  @JsonValue('archived')
  archived('archived');

  const {Entity}Status(this.value);

  final String value;

  /// Display label for UI
  String get label => switch (this) {
    active => 'Active',
    inactive => 'Inactive',
    pending => 'Pending',
    archived => 'Archived',
  };

  /// Icon for visual representation
  IconData get icon => switch (this) {
    active => Icons.check_circle,
    inactive => Icons.cancel,
    pending => Icons.hourglass_empty,
    archived => Icons.archive,
  };
}
```

### Unknown Value Handling

```dart
@JsonEnum(alwaysCreate: true)
enum Priority {
  @JsonValue('low')
  low,

  @JsonValue('medium')
  medium,

  @JsonValue('high')
  high,

  @JsonValue('unknown')
  unknown; // Fallback for unrecognized values
}

// In entity, handle gracefully:
factory Task.fromJson(Map<String, dynamic> json) {
  // Normalize unknown priority values
  final priorityValue = json['priority'] as String?;
  if (priorityValue != null && !['low', 'medium', 'high'].contains(priorityValue)) {
    json['priority'] = 'unknown';
  }
  return _$TaskFromJson(json);
}
```

## Nested Objects

### Single Nested Object

```dart
@JsonSerializable(explicitToJson: true)
class Order extends Equatable {
  const Order({
    required this.id,
    required this.customer,
    required this.items,
    this.shippingAddress,
  });

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);

  final String id;

  /// Nested object - requires explicitToJson
  final Customer customer;

  /// List of nested objects
  final List<OrderItem> items;

  /// Optional nested object
  @JsonKey(name: 'shipping_address')
  final Address? shippingAddress;

  Map<String, dynamic> toJson() => _$OrderToJson(this);

  // Computed properties
  double get total => items.fold(0, (sum, item) => sum + item.price * item.quantity);
  int get itemCount => items.fold(0, (sum, item) => sum + item.quantity);

  @override
  List<Object?> get props => [id, customer, items, shippingAddress];
}
```

### List of Primitives

```dart
@JsonSerializable()
class Tag extends Equatable {
  const Tag({
    required this.id,
    required this.name,
    this.aliases = const [],
  });

  factory Tag.fromJson(Map<String, dynamic> json) => _$TagFromJson(json);

  final String id;
  final String name;

  /// List of primitive strings - defaults to empty list
  final List<String> aliases;

  Map<String, dynamic> toJson() => _$TagToJson(this);

  @override
  List<Object?> get props => [id, name, aliases];
}
```

## Response DTOs

### Standard Response Wrapper

```dart
@JsonSerializable()
class {Entity}Response {
  const {Entity}Response({
    required this.success,
    required this.data,
    this.message,
  });

  factory {Entity}Response.fromJson(Map<String, dynamic> json) =>
      _${Entity}ResponseFromJson(json);

  final bool success;
  final {Entity} data;
  final String? message;

  Map<String, dynamic> toJson() => _${Entity}ResponseToJson(this);
}
```

### List Response with Pagination

```dart
@JsonSerializable()
class {Entity}ListResponse {
  const {Entity}ListResponse({
    required this.success,
    required this.data,
    this.pagination,
    this.message,
  });

  factory {Entity}ListResponse.fromJson(Map<String, dynamic> json) =>
      _${Entity}ListResponseFromJson(json);

  final bool success;
  final List<{Entity}> data;
  final PaginationInfo? pagination;
  final String? message;

  Map<String, dynamic> toJson() => _${Entity}ListResponseToJson(this);
}

@JsonSerializable()
class PaginationInfo {
  const PaginationInfo({
    required this.page,
    required this.limit,
    required this.totalCount,
    required this.totalPages,
    this.hasMore,
  });

  factory PaginationInfo.fromJson(Map<String, dynamic> json) =>
      _$PaginationInfoFromJson(json);

  final int page;
  final int limit;

  @JsonKey(name: 'total_count')
  final int totalCount;

  @JsonKey(name: 'total_pages')
  final int totalPages;

  @JsonKey(name: 'has_more')
  final bool? hasMore;

  /// Computed - handles APIs that don't provide hasMore
  bool get hasNextPage => hasMore ?? (page < totalPages);

  Map<String, dynamic> toJson() => _$PaginationInfoToJson(this);
}
```

## Nullable Handling

### Required vs Optional Fields

```dart
@JsonSerializable()
class Profile extends Equatable {
  const Profile({
    // Required - core identifiers
    required this.id,
    required this.email,

    // Optional - may not be set
    this.displayName,
    this.bio,
    this.avatarUrl,

    // Optional with default
    this.isVerified = false,
    this.tags = const [],
  });

  factory Profile.fromJson(Map<String, dynamic> json) => _$ProfileFromJson(json);

  final String id;
  final String email;
  final String? displayName;
  final String? bio;

  @JsonKey(name: 'avatar_url')
  final String? avatarUrl;

  @JsonKey(name: 'is_verified')
  final bool isVerified;

  final List<String> tags;

  Map<String, dynamic> toJson() => _$ProfileToJson(this);

  @override
  List<Object?> get props => [id, email, displayName, bio, avatarUrl, isVerified, tags];
}
```

### CopyWith with Nullable Setter Functions

```dart
/// Use function parameters when you need to explicitly set a field to null
Profile copyWith({
  String? id,
  String? email,
  String? Function()? displayName, // Can set to null
  String? Function()? bio,          // Can set to null
  String? Function()? avatarUrl,    // Can set to null
  bool? isVerified,
  List<String>? tags,
}) {
  return Profile(
    id: id ?? this.id,
    email: email ?? this.email,
    displayName: displayName != null ? displayName() : this.displayName,
    bio: bio != null ? bio() : this.bio,
    avatarUrl: avatarUrl != null ? avatarUrl() : this.avatarUrl,
    isVerified: isVerified ?? this.isVerified,
    tags: tags ?? this.tags,
  );
}

// Usage:
// Clear bio: profile.copyWith(bio: () => null)
// Keep bio:  profile.copyWith(bio: null) or profile.copyWith()
// Set bio:   profile.copyWith(bio: () => 'New bio')
```

## Custom Converters

### Flexible Type Converter

```dart
/// Handles fields that might come as string, int, or other types
class FlexibleStringConverter implements JsonConverter<String?, Object?> {
  const FlexibleStringConverter();

  @override
  String? fromJson(Object? value) {
    if (value == null) return null;
    if (value is String) return value;
    if (value is Map || value is List) return null; // Ignore complex types
    return value.toString();
  }

  @override
  Object? toJson(String? value) => value;
}

// Usage
@FlexibleStringConverter()
final String? externalId; // Handles "123" or 123
```

### List Converter with Filtering

```dart
/// Parses list, filtering out items that fail parsing
class SafeListConverter<T> implements JsonConverter<List<T>, List<dynamic>?> {
  const SafeListConverter(this.itemFromJson);

  final T Function(Map<String, dynamic>) itemFromJson;

  @override
  List<T> fromJson(List<dynamic>? json) {
    if (json == null) return [];
    return json
        .whereType<Map<String, dynamic>>()
        .map((item) {
          try {
            return itemFromJson(item);
          } catch (_) {
            return null;
          }
        })
        .whereType<T>()
        .toList();
  }

  @override
  List<dynamic>? toJson(List<T> object) => object;
}
```

## Factory Normalization

### Handling API Variations

```dart
factory Game.fromJson(Map<String, dynamic> json) {
  // Normalize API variations before generated parsing
  final normalizedJson = Map<String, dynamic>.from(json);

  // Handle field name variations
  normalizedJson['verified'] ??= normalizedJson['isVerified'];
  normalizedJson['type'] ??= normalizedJson['gameType'];

  // Handle missing required fields
  normalizedJson['name'] ??= 'Unknown';

  return _$GameFromJson(normalizedJson);
}
```

## Polymorphic Responses

### Dynamic Data Field

```dart
@JsonSerializable(explicitToJson: true, createToJson: false)
class SearchResponse {
  const SearchResponse({
    required this.success,
    required this.data,
    required this.resultType,
  });

  factory SearchResponse.fromJson(Map<String, dynamic> json) {
    final data = json['data'];
    final resultType = json['result_type'] as String;

    Object parsedData;
    switch (resultType) {
      case 'users':
        parsedData = (data as List)
            .map((e) => User.fromJson(e as Map<String, dynamic>))
            .toList();
        break;
      case 'products':
        parsedData = (data as List)
            .map((e) => Product.fromJson(e as Map<String, dynamic>))
            .toList();
        break;
      default:
        parsedData = data;
    }

    return SearchResponse(
      success: json['success'] as bool,
      data: parsedData,
      resultType: resultType,
    );
  }

  final bool success;
  final Object data;
  final String resultType;

  List<User> get users => resultType == 'users' ? data as List<User> : [];
  List<Product> get products => resultType == 'products' ? data as List<Product> : [];

  Map<String, dynamic> toJson() => {
    'success': success,
    'result_type': resultType,
    'data': data,
  };
}
```

## Input Models

### Separate Input/Output Types

```dart
/// Input for creating/updating - no id, no computed fields
@JsonSerializable(includeIfNull: false)
class {Entity}Input {
  const {Entity}Input({
    required this.name,
    this.description,
    this.tags = const [],
  });

  factory {Entity}Input.fromJson(Map<String, dynamic> json) =>
      _${Entity}InputFromJson(json);

  final String name;
  final String? description;
  final List<String> tags;

  Map<String, dynamic> toJson() => _${Entity}InputToJson(this);

  /// Create input from existing entity for editing
  factory {Entity}Input.fromEntity({Entity} entity) {
    return {Entity}Input(
      name: entity.name,
      description: entity.description,
      tags: entity.tags,
    );
  }
}
```

## Validation

### Separate Validator Class

```dart
class {Entity}Validators {
  /// Validate name field
  static String? validateName(String? value) {
    if (value == null || value.trim().isEmpty) {
      return LocaleKeys.validation_name_required.tr();
    }
    if (value.length < 2) {
      return LocaleKeys.validation_name_too_short.tr();
    }
    if (value.length > 100) {
      return LocaleKeys.validation_name_too_long.tr();
    }
    return null;
  }

  /// Validate email field
  static String? validateEmail(String? value) {
    if (value == null || value.trim().isEmpty) {
      return LocaleKeys.validation_email_required.tr();
    }
    final emailRegex = RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$');
    if (!emailRegex.hasMatch(value)) {
      return LocaleKeys.validation_email_invalid.tr();
    }
    return null;
  }

  /// Process and normalize inputs before submission
  static Map<String, String> processInputs(Map<String, String> inputs) {
    return inputs.map((key, value) => MapEntry(key, value.trim()));
  }
}
```

## Code Generation Commands

```bash
# Single build
fvm flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode for development
fvm flutter pub run build_runner watch --delete-conflicting-outputs
```

**Triggers for regeneration:**
- Adding/modifying `@JsonSerializable` classes
- Changing field types or annotations
- Adding new enum values with `@JsonValue`
