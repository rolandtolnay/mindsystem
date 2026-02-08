# Flutter Error Handling Architecture Reference

A structured approach to error handling in Flutter apps using Dio.

## Core Principle: Unique Messages for Debugging

Every exception type must have **distinct localized title and message**. When users report issues via screenshots, unique error messages allow immediate identification of the error type and code path without requiring logs or reproduction steps.

## Exception Hierarchy

```
Exception
├── LocalizedException (interface)      → UI-displayable errors with title + message
├── ExpectedException (marker)          → Skip Crashlytics reporting
│
├── AppDioException (abstract)          → Network/API errors
│   ├── ApiException                    → Server errors (4xx/5xx)
│   ├── NoInternetException             → No connectivity
│   └── NetworkException                → Timeouts, bad gateway
│
├── ParsingException                    → Contract mismatch (JSON parsing failed)
├── ResultError                         → Frontend bugs (assertions that failed)
│
└── DomainException (abstract)          → Expected business logic errors
    ├── NoActiveBookingException
    └── [Feature]Exception
```

## Exception Types Overview

| Exception | When | Crashlytics | Example |
|-----------|------|-------------|---------|
| `ApiException` | Server error response | ✅ Report | 500 error, 4xx errors |
| `NoInternetException` | No connectivity | ❌ Expected | SocketException |
| `NetworkException` | Timeouts, gateway | ❌ Expected | 504 timeout |
| `ParsingException` | Contract mismatch | ✅ Report | Null response, wrong JSON structure |
| `ResultError` | Frontend bug | ✅ Report | Invalid state that shouldn't occur |
| `DomainException` | Expected business state | ❌ Expected | No active booking |

## Base Interfaces

```dart
/// Interface for exceptions that can be displayed in UI.
/// Implement this to provide user-friendly error messages.
abstract class LocalizedException implements Exception {
  /// Optional title for the error. Return null for single-line errors (e.g., toasts).
  String? get localizedTitle;
  String get localizedMessage;
}

/// Marker interface for expected errors that should NOT be reported to Crashlytics.
/// Use for known error states (no internet, domain validation failures).
class ExpectedException implements Exception {}
```

## Infrastructure Exceptions (Network Layer)

These wrap Dio errors and are created by the API error interceptor:

```dart
/// Base class for network exceptions. Wraps DioException for cleaner inheritance.
abstract class AppDioException extends DioException {
  AppDioException(DioException? exception)
      : super(
          requestOptions: exception?.requestOptions ?? RequestOptions(),
          error: exception?.error,
          response: exception?.response,
          message: exception?.message,
          type: exception?.type ?? DioExceptionType.unknown,
        );
}

/// Server returned an error response (4xx/5xx). Reports to Crashlytics.
class ApiException extends AppDioException implements LocalizedException {
  ApiException({this.apiResponse, this.dioResponse, DioException? exception}) 
      : super(exception);

  final ApiErrorResponse? apiResponse;
  final Response<dynamic>? dioResponse;

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_server_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_server_subtitle);
}

/// No network connectivity. Expected error - not reported to Crashlytics.
class NoInternetException extends AppDioException 
    implements LocalizedException, ExpectedException {
  NoInternetException({DioException? exception}) : super(exception);

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_no_internet_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_no_internet_description);
}

/// Network issues (timeouts, bad gateway). Expected error - not reported to Crashlytics.
class NetworkException extends AppDioException 
    implements LocalizedException, ExpectedException {
  NetworkException({DioException? exception}) : super(exception);

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_network_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_network_subtitle);
}
```

## Parsing Exception (Contract Mismatch)

Thrown when JSON parsing fails due to backend/frontend contract mismatch. **Always reported to Crashlytics** for investigation.

```dart
/// Exception thrown when JSON parsing fails.
/// Captures context for remote debugging via Crashlytics.
class ParsingException implements LocalizedException {
  const ParsingException({
    required this.message,
    this.endpoint,
    this.expectedType,
    this.rawJson,
    this.innerError,
  });

  final String message;
  final String? endpoint;       // API endpoint that returned the response
  final String? expectedType;   // Expected DTO/Entity type
  final dynamic rawJson;        // Raw JSON that failed to parse
  final Object? innerError;     // Underlying FormatException/TypeError

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_parsing_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_parsing_subtitle);
  
  @override
  String toString() => 'ParsingException: $message'
      '${endpoint != null ? ' [endpoint: $endpoint]' : ''}'
      '${expectedType != null ? ' [expected: $expectedType]' : ''}'
      '${innerError != null ? ' [error: $innerError]' : ''}';
}
```

**When to throw:**
- Response body is null when object expected
- JSON structure doesn't match DTO
- Required field missing or wrong type

## Result Error (Frontend Bug)

Thrown when frontend code reaches an invalid state that shouldn't occur if implementation is correct. **Always reported to Crashlytics** as these are bugs to fix.

```dart
/// Exception for frontend bugs - assertions that failed at runtime.
/// Use for invalid states that indicate implementation errors.
class ResultError implements LocalizedException {
  const ResultError(this.message);

  final String message;

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_unexpected_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_unexpected_subtitle);
  
  @override
  String toString() => 'ResultError: $message';
}
```

**When to throw:**
- Operation failed that should always succeed (e.g., `if (!success) throw ResultError(...)`)
- Required property is null when it shouldn't be (e.g., `if (url == null) throw ResultError(...)`)
- Invalid frontend state (e.g., `'No stored access token found'`)

**Don't use for:**
- API response issues → use `ParsingException`
- Expected business states → use `DomainException`

## Safe Response Parsing

Extensions to keep API implementations lean while handling parsing errors gracefully.

```dart
extension ResponseParsingEx<T> on Response<T> {
  /// Parse single object. Throws ParsingException if null or parsing fails.
  E parseSingle<Dto, E>({
    required Dto Function(Map<String, dynamic>) fromJson,
    required E Function(Dto) toEntity,
    String? endpoint,
  }) {
    final json = data;
    if (json == null) {
      throw ParsingException(
        message: 'Response body is null',
        endpoint: endpoint,
        expectedType: '$Dto',
      );
    }
    try {
      return toEntity(fromJson(json as Map<String, dynamic>));
    } catch (e) {
      throw ParsingException(
        message: 'Failed to parse response',
        endpoint: endpoint,
        expectedType: '$Dto',
        rawJson: json,
        innerError: e,
      );
    }
  }

  /// Parse list. Logs failures for individual items but continues parsing.
  /// Returns only successfully parsed items.
  List<E> parseList<Dto, E>({
    required Dto Function(Map<String, dynamic>) fromJson,
    required E Function(Dto) toEntity,
    String? endpoint,
    void Function(ParsingException)? onItemError,
  }) {
    final list = data as List<dynamic>?;
    if (list == null) return [];
    
    final results = <E>[];
    for (final item in list) {
      try {
        final dto = fromJson(item as Map<String, dynamic>);
        results.add(toEntity(dto));
      } catch (e) {
        final exception = ParsingException(
          message: 'Failed to parse list item',
          endpoint: endpoint,
          expectedType: '$Dto',
          rawJson: item,
          innerError: e,
        );
        onItemError?.call(exception);
      }
    }
    return results;
  }
}
```

**API implementation stays lean:**

```dart
class BookingApiImpl implements BookingApi {
  final Dio dio;

  @override
  Future<CustomerEntity> getCustomer() async {
    final response = await dio.get<Map<String, dynamic>>(api.endpoint(ApiEndpoint.customer));
    return response.parseSingle(
      fromJson: CustomerDto.fromJson,
      toEntity: (dto) => dto.toEntity(),
      endpoint: ApiEndpoint.customer.name,
    );
  }

  @override
  Future<List<BookingEntity>> getBookingList() async {
    final response = await dio.get<List<dynamic>>(api.endpoint(ApiEndpoint.booking));
    return response.parseList(
      fromJson: BookingDto.fromJson,
      toEntity: (dto) => dto.toEntity(),
      endpoint: ApiEndpoint.booking.name,
      onItemError: (e) => log.warning('Booking parse failed', e),
    );
  }
}
```

## Domain Exceptions (Business Logic)

### When to Create Domain Exceptions

Create a `DomainException` subclass when you need to:

1. **Handle errors differently** - Trigger specific UI flows (e.g., redirect to booking screen when no booking exists)
2. **Show contextual messages** - Display feature-specific error copy instead of generic messages
3. **Track specific failures** - Identify business rule violations in user screenshots

**Don't create domain exceptions** for errors that should use generic handling - let them propagate as `ApiException` for accurate Crashlytics reporting.

### DomainException Base Class

```dart
/// Base class for all domain/business logic exceptions.
/// 
/// - Implements [LocalizedException] for UI display
/// - Implements [ExpectedException] to skip Crashlytics (domain errors are expected states)
/// - Override [localizedTitle] and [localizedMessage] for feature-specific messages
abstract class DomainException implements LocalizedException, ExpectedException {
  const DomainException();
  
  @override
  String? get localizedTitle => tr(LocaleKeys.common_errors_unexpected_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_unexpected_subtitle);
}
```

### Feature Exception Examples

```dart
class NoActiveBookingException extends DomainException {
  final String? details;
  const NoActiveBookingException([this.details]);
  
  @override
  String? get localizedTitle => tr(LocaleKeys.booking_no_active_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.booking_no_active_message);
  
  @override
  String toString() => 'No active booking${details != null ? ': $details' : ''}';
}

class PhotoAccessDeniedException extends DomainException {
  const PhotoAccessDeniedException();
  
  @override
  String? get localizedTitle => tr(LocaleKeys.photo_access_denied_title);
  
  @override
  String get localizedMessage => tr(LocaleKeys.photo_access_denied_message);
}
```

## API Error Interceptor

Intercepts all Dio errors and transforms them to typed exceptions. Place as the **last interceptor** in the chain:

```dart
class ApiErrorInterceptor extends Interceptor {
  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    // 1. No internet
    if (err.error is SocketException) {
      handler.reject(NoInternetException(exception: err));
      return;
    }

    // 2. Network issues (timeouts, gateway errors)
    switch (err.response?.statusCode) {
      case HttpStatus.requestTimeout:
      case HttpStatus.badGateway:
      case HttpStatus.gatewayTimeout:
        handler.reject(NetworkException(exception: err));
        return;
    }

    // 3. API error - parse response if available
    try {
      final errorJson = err.response?.data as Map<String, dynamic>;
      final apiErrorResponse = ApiErrorResponse.fromJson(errorJson);
      handler.reject(ApiException(apiResponse: apiErrorResponse, exception: err));
    } catch (_) {
      handler.reject(ApiException(exception: err));
    }
  }
}
```

## UI Error Display Guidelines

All error display components should check for `LocalizedException` and extract localized title/message, falling back to generic error copy for unknown exceptions:

```dart
final localized = error is LocalizedException ? error : null;
final title = localized?.localizedTitle ?? tr(LocaleKeys.common_errors_uncaught_title);
final message = localized?.localizedMessage ?? tr(LocaleKeys.common_errors_uncaught_subtitle);

// For single-line displays (e.g., toasts), use message only:
final toastText = localized?.localizedMessage ?? tr(LocaleKeys.common_errors_uncaught_subtitle);
```

**When to use each pattern:**
- **Error widgets** (e.g., `ErrorCard`): For errors during page initialization where the entire content failed to load. Include a retry button that re-triggers the data fetch.
- **Toasts**: For errors during user-initiated actions (button taps) where the action can be retried via the same UI element.
- **Popups/Dialogs**: For errors requiring user acknowledgment before continuing, or when additional context/actions are needed.

## Crashlytics Integration

```dart
extension ExceptionConvenience on Object {
  bool get shouldReportToCrashlytics => 
      !isRequestCancelled && this is! ExpectedException;
}

// In logging/error handling:
if (error.shouldReportToCrashlytics) {
  crashlytics.recordError(error, stackTrace);
}
```

## Localization Keys Structure

```json
{
  "common": {
    "errors": {
      "server_title": "Server Error",
      "server_subtitle": "Something went wrong. Please try again.",
      "no_internet_title": "No Internet",
      "no_internet_description": "Check your connection and try again.",
      "network_title": "Connection Problem",
      "network_subtitle": "Unable to reach the server.",
      "parsing_title": "Data Error",
      "parsing_subtitle": "We couldn't load the data. Please try again.",
      "unexpected_title": "Unexpected Error",
      "unexpected_subtitle": "Something went wrong. Please try again.",
      "uncaught_title": "Oops!",
      "uncaught_subtitle": "Something unexpected happened."
    }
  }
}
```

## Summary

| Exception | Purpose | Crashlytics |
|-----------|---------|-------------|
| `ApiException` | Server error (4xx/5xx) | ✅ Report |
| `NoInternetException` | No connectivity | ❌ Expected |
| `NetworkException` | Timeouts, gateway errors | ❌ Expected |
| `ParsingException` | JSON contract mismatch | ✅ Report |
| `ResultError` | Frontend bug/invalid state | ✅ Report |
| `DomainException` | Expected business state | ❌ Expected |

**Key principles:**
1. **Unique messages** for each exception type enable debugging from user screenshots
2. **ParsingException** captures context (endpoint, expected type, raw JSON) for remote debugging
3. **ResultError** is for frontend bugs that shouldn't happen - assertions that failed
4. **DomainException** is for expected business states that need dedicated UI flows
5. **Response parsing extensions** keep API code lean while handling errors gracefully
6. **List parsing** continues on individual item failures, logging errors but returning valid items
