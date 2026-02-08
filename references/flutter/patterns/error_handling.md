# Error Handling

## Core Principle

Every exception type has **distinct localized title and message** — user screenshots identify the error type and code path without logs.

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

| Exception | When | Crashlytics |
|-----------|------|-------------|
| `ApiException` | Server error response (4xx/5xx) | Report |
| `NoInternetException` | No connectivity (SocketException) | Skip |
| `NetworkException` | Timeouts, bad gateway | Skip |
| `ParsingException` | Null response, wrong JSON structure | Report |
| `ResultError` | Invalid frontend state | Report |
| `DomainException` | Expected business state | Skip |

## Base Interfaces

```dart
abstract class LocalizedException implements Exception {
  String? get localizedTitle;
  String get localizedMessage;
}

class ExpectedException implements Exception {}
```

## Network Exceptions

Wrap Dio errors, created by `ApiErrorInterceptor`:

```dart
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

class NoInternetException extends AppDioException
    implements LocalizedException, ExpectedException {
  NoInternetException({DioException? exception}) : super(exception);

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_no_internet_title);
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_no_internet_description);
}

class NetworkException extends AppDioException
    implements LocalizedException, ExpectedException {
  NetworkException({DioException? exception}) : super(exception);

  @override
  String get localizedTitle => tr(LocaleKeys.common_errors_network_title);
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_network_subtitle);
}
```

## ParsingException

Thrown on JSON contract mismatch. Captures context for Crashlytics debugging.

```dart
class ParsingException implements LocalizedException {
  const ParsingException({
    required this.message,
    this.endpoint,
    this.expectedType,
    this.rawJson,
    this.innerError,
  });

  final String message;
  final String? endpoint;
  final String? expectedType;
  final dynamic rawJson;
  final Object? innerError;

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

Throw when: response body null, JSON structure mismatch, required field missing/wrong type.

## ResultError

Frontend bugs — invalid state that shouldn't occur. Always reported to Crashlytics.

```dart
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

- Throw for: operations that should always succeed, required properties unexpectedly null, invalid frontend state
- Don't use for: API response issues → `ParsingException`, expected business states → `DomainException`

## Response Parsing Extensions

Keep API implementations lean while handling parsing errors:

```dart
extension ResponseParsingEx<T> on Response<T> {
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

  /// Logs individual item failures but continues parsing. Returns valid items only.
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

API usage:

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

## DomainException

Expected business logic errors. Implements both `LocalizedException` and `ExpectedException` (skips Crashlytics).

Create when: specific UI flow needed, feature-specific error copy, business rule violation tracking from screenshots. Don't create for errors that should use generic `ApiException` handling.

```dart
abstract class DomainException implements LocalizedException, ExpectedException {
  const DomainException();

  @override
  String? get localizedTitle => tr(LocaleKeys.common_errors_unexpected_title);
  @override
  String get localizedMessage => tr(LocaleKeys.common_errors_unexpected_subtitle);
}

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
```

## API Error Interceptor

Place as **last interceptor** in Dio chain:

```dart
class ApiErrorInterceptor extends Interceptor {
  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.error is SocketException) {
      handler.reject(NoInternetException(exception: err));
      return;
    }

    switch (err.response?.statusCode) {
      case HttpStatus.requestTimeout:
      case HttpStatus.badGateway:
      case HttpStatus.gatewayTimeout:
        handler.reject(NetworkException(exception: err));
        return;
    }

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

## UI Error Display

```dart
final localized = error is LocalizedException ? error : null;
final title = localized?.localizedTitle ?? tr(LocaleKeys.common_errors_uncaught_title);
final message = localized?.localizedMessage ?? tr(LocaleKeys.common_errors_uncaught_subtitle);
```

- **Error widgets** (`ErrorCard`): page initialization failures, include retry button
- **Toasts**: user-initiated action failures, retryable via same UI element
- **Dialogs**: errors requiring acknowledgment or additional context

## Crashlytics

```dart
extension ExceptionConvenience on Object {
  bool get shouldReportToCrashlytics =>
      !isRequestCancelled && this is! ExpectedException;
}

if (error.shouldReportToCrashlytics) {
  crashlytics.recordError(error, stackTrace);
}
```

## Localization Keys

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
