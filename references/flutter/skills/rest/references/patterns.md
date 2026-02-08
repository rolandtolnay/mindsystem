# REST API Pattern Implementations

Complete pattern implementations for Dio + Riverpod REST API infrastructure. Each pattern includes implementation code and rationale.

## Dio Configuration Provider

Centralized Dio instance provided via Riverpod with `keepAlive: true` for singleton lifecycle. Configures base URL from environment, timeouts, and interceptor chain.

```dart
@Riverpod(keepAlive: true)
Dio dio(Ref ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: ref.read(envConfigProvider).apiBaseUrl,
      connectTimeout: const Duration(seconds: {timeout}),
      receiveTimeout: const Duration(seconds: {timeout}),
      headers: {'Content-Type': 'application/json'},
    ),
  );

  dio.interceptors.addAll([
    AuthInterceptor(
      getToken: () => ref.read(secureStorageProvider).read(key: StorageKeys.authToken),
      onUnauthorized: () => ref.read(secureStorageProvider).delete(key: StorageKeys.authToken),
    ),
    LoggingDioInterceptor(requestBody: true, responseBody: true),
    ApiErrorInterceptor(), // Must be last
  ]);

  return dio;
}
```

**Rationale:** Single instance shared across app. Interceptor order matters: Auth adds token, Logging captures traffic, Error transforms exceptions (must run last to catch all errors).

---

## Auth Token Interceptor

Automatically injects Bearer token for non-public routes. Clears token on 401 response. Uses whitelist pattern for public endpoints.

```dart
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.getToken,
    required this.onUnauthorized,
  });

  final Future<String?> Function() getToken;
  final Future<void> Function() onUnauthorized;

  static const _publicRoutes = ['/auth/login', '/auth/register', '/auth/refresh'];

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final isPublicRoute = _publicRoutes.any((route) => options.path.contains(route));

    if (!isPublicRoute) {
      final token = await getToken();
      if (token != null) {
        options.headers['Authorization'] = 'Bearer $token';
      }
    }

    return handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    if (err.response?.statusCode == 401) {
      await onUnauthorized();
    }
    return handler.next(err);
  }
}
```

**Rationale:** Decouples auth from API calls. Whitelist pattern keeps public routes simple. Auto-clearing token on 401 triggers re-authentication flow naturally.

---

## Abstract API Interface

Each feature defines abstract API interface with concrete implementation. Enables mock substitution via Riverpod provider that checks mock mode.

```dart
// Abstract interface
abstract class {Entity}Api {
  Future<{Entity}> get{Entity}(String id);
  Future<List<{Entity}>> get{Entities}({int page = 1, int limit = 20});
  Future<{Entity}> create{Entity}({Entity}Input input);
  Future<{Entity}> update{Entity}(String id, {Entity}Input input);
  Future<void> delete{Entity}(String id);
}

// Concrete implementation
class {Entity}ApiImpl implements {Entity}Api {
  {Entity}ApiImpl(this._dio, [this._api = const ApiEndpoint()]);

  final Dio _dio;
  final ApiEndpoint _api;

  @override
  Future<{Entity}> get{Entity}(String id) async {
    final response = await _dio.get<Map<String, dynamic>>(
      _api.{entity}(id),
    );
    return response.parseSingle(
      fromJson: {Entity}.fromJson,
      endpoint: 'get{Entity}',
    );
  }

  @override
  Future<List<{Entity}>> get{Entities}({int page = 1, int limit = 20}) async {
    final response = await _dio.get<Map<String, dynamic>>(
      _api.{entities},
      queryParameters: {'page': page, 'limit': limit},
    );
    return response.parseWrapped(
      fromJson: {Entity}ListResponse.fromJson,
      extract: (dto) => dto.data,
      endpoint: 'get{Entities}',
    );
  }
}

// Provider with mock support
@riverpod
{Entity}Api {entity}Api(Ref ref) {
  if (ref.read(envConfigProvider).isMockMode) {
    return {Entity}MockApi();
  }
  return {Entity}ApiImpl(ref.watch(dioProvider));
}
```

**Rationale:** Abstract interface enables testing without HTTP. Mock mode controlled by environment. Providers resolve dependencies automatically via Riverpod graph.

---

## Response Parsing Extensions

Safe response parsing with context-aware error handling. Three strategies: parseSingle (object), parseWrapped (extract from DTO), parseList (partial failure tolerance).

```dart
extension ResponseParsingEx<T> on Response<T> {
  /// Parses response body directly as a single object
  R parseSingle<R>({
    required R Function(Map<String, dynamic>) fromJson,
    String? endpoint,
  }) {
    final json = data;
    if (json == null) {
      throw ParsingException(
        message: 'Response body is null',
        endpoint: endpoint,
        expectedType: '$R',
      );
    }
    try {
      return fromJson(json as Map<String, dynamic>);
    } catch (e) {
      throw ParsingException(
        message: 'Failed to parse response',
        endpoint: endpoint,
        expectedType: '$R',
        rawJson: json,
        innerError: e,
      );
    }
  }

  /// Parses response to DTO then extracts domain entity
  E parseWrapped<Dto, E>({
    required Dto Function(Map<String, dynamic>) fromJson,
    required E Function(Dto) extract,
    String? endpoint,
  }) {
    final dto = parseSingle(fromJson: fromJson, endpoint: endpoint);
    try {
      return extract(dto);
    } catch (e) {
      throw ParsingException(
        message: 'Failed to extract from DTO',
        endpoint: endpoint,
        expectedType: '$E',
        innerError: e,
      );
    }
  }

  /// Parses list with partial failure tolerance - logs and skips bad items
  List<E> parseList<Dto, E>({
    required Dto Function(Map<String, dynamic>) fromJson,
    required E Function(Dto) toEntity,
    String? endpoint,
  }) {
    final list = data as List<dynamic>?;
    if (list == null) return [];

    final results = <E>[];
    for (final item in list) {
      try {
        final dto = fromJson(item as Map<String, dynamic>);
        results.add(toEntity(dto));
      } catch (e) {
        log.warning('Failed to parse list item at $endpoint: $e');
      }
    }
    return results;
  }
}
```

**Rationale:** Eliminates repetitive error handling. Endpoint context aids debugging. List parsing logs but doesn't fail on single item errors, enabling graceful degradation.

---

## Exception Hierarchy

Multi-level exception inheritance with marker interfaces. LocalizedException provides UI text. ExpectedException marks errors to skip crash reporting.

```dart
/// Marker interface for exceptions that provide localized UI messages
abstract class LocalizedException implements Exception {
  String? get localizedTitle;
  String get localizedMessage;
}

/// Marker interface for expected errors that shouldn't be reported to Crashlytics
abstract class ExpectedException implements Exception {}

/// Base class for Dio exceptions with localization support
abstract class {App}DioException extends DioException implements LocalizedException {
  {App}DioException(DioException? exception)
      : super(
          requestOptions: exception?.requestOptions ?? RequestOptions(),
          response: exception?.response,
          type: exception?.type ?? DioExceptionType.unknown,
          error: exception?.error,
        );
}

/// No internet connection
class NoInternetException extends {App}DioException implements ExpectedException {
  NoInternetException({DioException? exception}) : super(exception);

  @override
  String? get localizedTitle => LocaleKeys.errors_no_internet_title.tr();

  @override
  String get localizedMessage => LocaleKeys.errors_no_internet_message.tr();
}

/// Network timeout or server unavailable
class NetworkException extends {App}DioException implements ExpectedException {
  NetworkException({DioException? exception}) : super(exception);

  @override
  String? get localizedTitle => LocaleKeys.errors_network_title.tr();

  @override
  String get localizedMessage => LocaleKeys.errors_network_message.tr();
}

/// API returned an error response
class ApiException extends {App}DioException {
  ApiException({this.serverMessage, DioException? exception}) : super(exception);

  final String? serverMessage;

  int? get statusCode => response?.statusCode;

  @override
  String? get localizedTitle => LocaleKeys.errors_server_title.tr();

  @override
  String get localizedMessage =>
      serverMessage ?? LocaleKeys.errors_server_message.tr();
}

/// JSON parsing failed
class ParsingException implements LocalizedException {
  ParsingException({
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
  String? get localizedTitle => null;

  @override
  String get localizedMessage => LocaleKeys.errors_parsing_message.tr();

  @override
  String toString() =>
      'ParsingException($endpoint): $message [expected: $expectedType]';
}

/// Business logic exception (expected, don't report)
abstract class DomainException implements LocalizedException, ExpectedException {}

/// Extension for crash reporting decisions
extension ExceptionReportingEx on Object {
  bool get shouldReportToCrashlytics {
    if (this is ExpectedException) return false;
    if (this is DioException &&
        (this as DioException).type == DioExceptionType.cancel) return false;
    return true;
  }
}
```

**Rationale:** Separates concerns: Dio wrapping, UI localization, crash reporting. Marker interfaces enable flexible error handling without instanceof chains.

---

## Error Interceptor

Final interceptor that transforms DioException into typed exceptions. Classifies errors by type (no internet, timeout, API error) and extracts server messages.

```dart
class ApiErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    if (_isNoInternet(err)) {
      handler.reject(NoInternetException(exception: err));
      return;
    }

    if (_isNetworkError(err)) {
      handler.reject(NetworkException(exception: err));
      return;
    }

    final serverMessage = _extractServerMessage(err.response);
    handler.reject(ApiException(serverMessage: serverMessage, exception: err));
  }

  bool _isNoInternet(DioException err) {
    if (err.error is SocketException) return true;
    if (err.type == DioExceptionType.connectionError) return true;
    return false;
  }

  bool _isNetworkError(DioException err) {
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout) {
      return true;
    }

    final statusCode = err.response?.statusCode;
    if (statusCode == HttpStatus.requestTimeout ||
        statusCode == HttpStatus.badGateway ||
        statusCode == HttpStatus.serviceUnavailable) {
      return true;
    }

    return false;
  }

  String? _extractServerMessage(Response? response) {
    final data = response?.data;
    if (data is Map<String, dynamic>) {
      return data['message'] as String? ?? data['error'] as String?;
    }
    return null;
  }
}
```

**Rationale:** Must run last in interceptor chain. Centralizes error classification. Server message extraction handles common API response formats.

---

## Provider Error Listener

WidgetRef extension that centralizes error display. Shows toast with localized message. Supports ignoreIf predicate for conditional error suppression.

```dart
extension WidgetRefExtension on WidgetRef {
  /// Listen to provider errors and display toast automatically
  void listenOnError<T>(
    ProviderListenable<T> provider, {
    void Function(Object)? onError,
    bool Function(Object)? ignoreIf,
  }) {
    listen(provider, (previous, next) {
      if (next is! AsyncValue) return;

      next.whenOrNull(
        error: (e, _) {
          if (ignoreIf?.call(e) ?? false) return;
          onError?.call(e);
          AppToast.showError(context, error: e);
        },
      );
    });
  }
}

/// Toast helper that extracts localized messages
class AppToast {
  static void showError(BuildContext context, {required Object error}) {
    final title = error is LocalizedException ? error.localizedTitle : null;
    final message = error is LocalizedException
        ? error.localizedMessage
        : LocaleKeys.errors_unknown.tr();

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (title != null) Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
            Text(message),
          ],
        ),
        backgroundColor: context.colorScheme.error,
      ),
    );
  }
}
```

**Rationale:** Eliminates boilerplate error handling in screens. Error filtering prevents noise from user-cancelled actions. LocalizedException provides consistent UI.

---

## json_serializable Entity

Standard serialization pattern combining json_serializable with Equatable. Uses explicitToJson for nested objects and includeIfNull: false to optimize output.

```dart
@JsonSerializable(explicitToJson: true, includeIfNull: false)
class {Entity} extends Equatable {
  const {Entity}({
    required this.id,
    required this.name,
    this.description,
    this.createdAt,
    this.metadata,
  });

  factory {Entity}.fromJson(Map<String, dynamic> json) => _${Entity}FromJson(json);

  final String id;
  final String name;
  final String? description;

  @JsonKey(name: 'created_at')
  final DateTime? createdAt;

  final Map<String, dynamic>? metadata;

  Map<String, dynamic> toJson() => _${Entity}ToJson(this);

  /// Computed property - not serialized
  bool get hasDescription => description?.isNotEmpty ?? false;

  {Entity} copyWith({
    String? id,
    String? name,
    String? description,
    DateTime? createdAt,
    Map<String, dynamic>? metadata,
  }) {
    return {Entity}(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      createdAt: createdAt ?? this.createdAt,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  List<Object?> get props => [id, name, description, createdAt, metadata];
}
```

**Rationale:** Type-safe serialization with minimal boilerplate. Equatable provides value equality. @JsonKey maps snake_case API fields. Computed properties stay in domain layer.

---

## Enum with JsonValue

Enums use @JsonValue annotation for bidirectional string mapping. Provides type-safe conversion without manual switch statements.

```dart
@JsonEnum(valueField: 'value')
enum {Entity}Type {
  @JsonValue('type_a')
  typeA('type_a'),

  @JsonValue('type_b')
  typeB('type_b'),

  @JsonValue('type_c')
  typeC('type_c');

  const {Entity}Type(this.value);

  final String value;

  /// Display label for UI
  String get label => switch (this) {
    typeA => 'Type A',
    typeB => 'Type B',
    typeC => 'Type C',
  };
}
```

**Rationale:** Bidirectional JSON mapping handled by json_serializable. Display labels stay on enum for single source of truth. No manual parsing needed.

---

## Response DTO with Pagination

API response wrapper with status, data, and optional pagination metadata. Thin wrapper around domain entities for response structure.

```dart
@JsonSerializable()
class {Entity}ListResponse {
  const {Entity}ListResponse({
    required this.status,
    required this.data,
    this.pagination,
    this.message,
  });

  factory {Entity}ListResponse.fromJson(Map<String, dynamic> json) =>
      _${Entity}ListResponseFromJson(json);

  final bool status;
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

  bool get hasNextPage => hasMore ?? (page < totalPages);

  Map<String, dynamic> toJson() => _$PaginationInfoToJson(this);
}
```

**Rationale:** Standardized envelope for list endpoints. Pagination metadata kept separate and reusable. Computed hasNextPage handles API variations.

---

## AsyncValue.guard Provider

Wraps async operations with AsyncValue.guard() to capture errors in state. Invalidates related providers after successful mutations.

```dart
@riverpod
class Create{Entity} extends _$Create{Entity} {
  @override
  FutureOr<{Entity}?> build() => null;

  Future<void> create({Entity}Input input) async {
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final api = ref.read({entity}ApiProvider);
      final created = await api.create{Entity}(input);
      log.info('{Entity} ${created.id} created');
      return created;
    });

    // Invalidate list provider on success
    if (state.hasValue && state.value != null) {
      ref.invalidate({entities}Provider);
    }
  }
}

// In widget:
class Create{Entity}Screen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen for errors
    ref.listenOnError(create{Entity}Provider);

    final isLoading = ref.watch(create{Entity}Provider).isLoading;

    return ElevatedButton(
      onPressed: isLoading ? null : () => _onCreate(ref),
      child: isLoading
          ? const CircularProgressIndicator()
          : const Text('Create'),
    );
  }

  void _onCreate(WidgetRef ref) async {
    await ref.read(create{Entity}Provider.notifier).create(input);

    if (ref.read(create{Entity}Provider).hasError) return;

    // Success - navigate away
    context.router.pop();
  }
}
```

**Rationale:** Errors captured in state, not thrown. Loading state derived from provider. Error display centralized via listenOnError. Success check before navigation.
