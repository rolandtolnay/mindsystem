# API Infrastructure Patterns

Comprehensive HTTP client configuration, interceptor implementations, API class organization, and response handling patterns for Dio + Riverpod.

## HTTP Client Configuration

### Dio Provider with Singleton Lifecycle

```dart
@Riverpod(keepAlive: true)
Dio dio(Ref ref) {
  final dio = Dio(
    BaseOptions(
      baseUrl: ref.read(envConfigProvider).apiBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ),
  );

  dio.interceptors.addAll([
    AuthInterceptor(
      getToken: () => ref.read(secureStorageProvider).read(key: StorageKeys.authToken),
      onUnauthorized: () async {
        await ref.read(secureStorageProvider).delete(key: StorageKeys.authToken);
        // Optionally trigger logout flow
      },
    ),
    LoggingDioInterceptor(
      requestBody: true,
      responseBody: true,
      requestHeader: false,
      errorLevel: Level.WARNING,
    ),
    ApiErrorInterceptor(), // Must be last
  ]);

  return dio;
}
```

**Key Points:**
- `keepAlive: true` ensures singleton lifecycle across app
- Base URL from environment config, not hardcoded
- 15-second timeouts appropriate for mobile networks
- Interceptor order matters: Auth → Logging → Error (error must be last)

### Environment Configuration

```dart
@riverpod
EnvConfig envConfig(Ref ref) {
  return EnvConfig(
    apiBaseUrl: dotenv.env['API_BASE_URL'] ?? 'https://api.example.com',
    isMockMode: kDebugMode && (dotenv.env['ENABLE_MOCK_MODE'] == 'true'),
  );
}

class EnvConfig {
  const EnvConfig({
    required this.apiBaseUrl,
    required this.isMockMode,
  });

  final String apiBaseUrl;
  final bool isMockMode;
}
```

## Interceptors

### Auth Token Interceptor

```dart
class AuthInterceptor extends Interceptor {
  AuthInterceptor({
    required this.getToken,
    required this.onUnauthorized,
  });

  final Future<String?> Function() getToken;
  final Future<void> Function() onUnauthorized;

  /// Routes that don't require authentication
  static const _publicRoutes = [
    '/auth/login',
    '/auth/register',
    '/auth/refresh',
    '/auth/google',
  ];

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final isPublicRoute = _publicRoutes.any(
      (route) => options.path.contains(route),
    );

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
      log.warning('401 received, clearing auth token');
      await onUnauthorized();
    }
    return handler.next(err);
  }
}
```

**Patterns:**
- Whitelist pattern for public routes (cleaner than blacklist)
- Token injection is non-blocking (null token = no header)
- 401 handling clears token, letting subsequent requests fail naturally
- Callback injection enables testing

### Logging Interceptor

```dart
class LoggingDioInterceptor extends Interceptor {
  LoggingDioInterceptor({
    this.requestHeader = false,
    this.requestBody = false,
    this.responseHeader = false,
    this.responseBody = false,
    this.shouldLogBody = _defaultShouldLog,
    this.errorLevel = Level.WARNING,
    this.requestLevel,
    this.responseLevel,
  });

  final bool requestHeader;
  final bool requestBody;
  final bool responseHeader;
  final bool responseBody;
  final bool Function(RequestOptions, Response?) shouldLogBody;
  final Level errorLevel;
  final Level? requestLevel;
  final Level? responseLevel;

  static bool _defaultShouldLog(RequestOptions _, Response? __) => true;

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) {
    log.log(
      requestLevel ?? Level.INFO,
      '>>> ${options.method} │ ${options.uri}',
    );

    if (requestHeader) {
      _logHeaders(options.headers, 'Request Headers');
    }

    if (requestBody && shouldLogBody(options, null)) {
      _prettyPrintJson(options.data, 'Request Body');
    }

    handler.next(options);
  }

  @override
  void onResponse(Response response, ResponseInterceptorHandler handler) {
    log.log(
      responseLevel ?? Level.INFO,
      '<<< ${response.statusCode} │ ${response.requestOptions.uri}',
    );

    if (responseBody && shouldLogBody(response.requestOptions, response)) {
      _prettyPrintJson(response.data, 'Response Body');
    }

    handler.next(response);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    log.log(
      errorLevel,
      '!!! ${err.response?.statusCode ?? 'ERROR'} │ ${err.requestOptions.uri}',
    );

    if (err.response?.data != null) {
      _prettyPrintJson(err.response?.data, 'Error Response');
    }

    handler.next(err);
  }

  void _prettyPrintJson(dynamic data, String label) {
    if (data == null) return;
    try {
      final encoder = JsonEncoder.withIndent('  ');
      final pretty = encoder.convert(data);
      log.fine('$label:\n$pretty');
    } catch (_) {
      log.fine('$label: $data');
    }
  }

  void _logHeaders(Map<String, dynamic> headers, String label) {
    if (headers.isEmpty) return;
    log.fine('$label: $headers');
  }
}
```

**Customization Points:**
- Toggle headers/body logging independently
- Filter body logging with `shouldLogBody` (e.g., skip binary data)
- Configurable log levels per phase

## API Class Organization

### Abstract Interface + Implementation

```dart
// lib/{feature}/domain/{entity}_api.dart

/// Abstract interface for {Entity} API operations
abstract class {Entity}Api {
  /// Fetches a single {entity} by ID
  Future<{Entity}> get{Entity}(String id);

  /// Fetches paginated list of {entities}
  Future<{Entity}ListResponse> get{Entities}({
    int page = 1,
    int limit = 20,
    String? search,
  });

  /// Creates a new {entity}
  Future<{Entity}> create{Entity}({Entity}Input input);

  /// Updates an existing {entity}
  Future<{Entity}> update{Entity}(String id, {Entity}Input input);

  /// Deletes an {entity}
  Future<void> delete{Entity}(String id);
}

/// Concrete implementation using Dio
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
  Future<{Entity}ListResponse> get{Entities}({
    int page = 1,
    int limit = 20,
    String? search,
  }) async {
    final response = await _dio.get<Map<String, dynamic>>(
      _api.{entities},
      queryParameters: {
        'page': page,
        'limit': limit,
        if (search != null && search.isNotEmpty) 'search': search,
      },
    );
    return response.parseSingle(
      fromJson: {Entity}ListResponse.fromJson,
      endpoint: 'get{Entities}',
    );
  }

  @override
  Future<{Entity}> create{Entity}({Entity}Input input) async {
    final response = await _dio.post<Map<String, dynamic>>(
      _api.{entities},
      data: input.toJson(),
    );
    return response.parseSingle(
      fromJson: {Entity}.fromJson,
      endpoint: 'create{Entity}',
    );
  }

  @override
  Future<{Entity}> update{Entity}(String id, {Entity}Input input) async {
    final response = await _dio.put<Map<String, dynamic>>(
      _api.{entity}(id),
      data: input.toJson(),
    );
    return response.parseSingle(
      fromJson: {Entity}.fromJson,
      endpoint: 'update{Entity}',
    );
  }

  @override
  Future<void> delete{Entity}(String id) async {
    await _dio.delete<void>(_api.{entity}(id));
  }
}
```

### Provider with Mock Support

```dart
@riverpod
{Entity}Api {entity}Api(Ref ref) {
  if (ref.read(envConfigProvider).isMockMode) {
    log.info('Using {Entity}MockApi');
    return {Entity}MockApi();
  }
  return {Entity}ApiImpl(ref.watch(dioProvider));
}
```

### Mock Implementation

```dart
// lib/{feature}/domain/mock/{entity}_mock_api.dart

class {Entity}MockApi implements {Entity}Api {
  @override
  Future<{Entity}> get{Entity}(String id) async {
    log.debug('[MOCK] get{Entity}($id)');
    await MockDataHelper.simulateNetworkDelay();

    return {Entity}(
      id: id,
      name: 'Mock {Entity}',
      createdAt: DateTime.now(),
    );
  }

  @override
  Future<{Entity}ListResponse> get{Entities}({
    int page = 1,
    int limit = 20,
    String? search,
  }) async {
    log.debug('[MOCK] get{Entities}(page: $page, limit: $limit, search: $search)');
    await MockDataHelper.simulateNetworkDelay();

    final items = List.generate(
      limit,
      (i) => {Entity}(
        id: '${page}_$i',
        name: 'Mock {Entity} ${(page - 1) * limit + i + 1}',
      ),
    );

    return {Entity}ListResponse(
      status: true,
      data: items,
      pagination: PaginationInfo(
        page: page,
        limit: limit,
        totalCount: 100,
        totalPages: 5,
      ),
    );
  }

  @override
  Future<{Entity}> create{Entity}({Entity}Input input) async {
    log.debug('[MOCK] create{Entity}(${input.name})');
    await MockDataHelper.simulateNetworkDelay();

    return {Entity}(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      name: input.name,
      createdAt: DateTime.now(),
    );
  }

  @override
  Future<{Entity}> update{Entity}(String id, {Entity}Input input) async {
    log.debug('[MOCK] update{Entity}($id, ${input.name})');
    await MockDataHelper.simulateNetworkDelay();

    return {Entity}(
      id: id,
      name: input.name,
      createdAt: DateTime.now(),
    );
  }

  @override
  Future<void> delete{Entity}(String id) async {
    log.debug('[MOCK] delete{Entity}($id)');
    await MockDataHelper.simulateNetworkDelay();
  }
}

class MockDataHelper {
  static Future<void> simulateNetworkDelay() async {
    await Future.delayed(const Duration(milliseconds: 300 + Random().nextInt(500)));
  }
}
```

## API Endpoint Organization

```dart
/// Centralized endpoint definitions
class ApiEndpoint {
  const ApiEndpoint();

  // Auth
  String get login => '/auth/login';
  String get register => '/auth/register';
  String get refresh => '/auth/refresh';

  // {Entities}
  String get {entities} => '/api/{entities}';
  String {entity}(String id) => '/api/{entities}/$id';

  // Nested resources
  String {entity}{SubEntities}(String {entity}Id) =>
      '/api/{entities}/${entity}Id/{subEntities}';
}
```

## Response Parsing Extensions

```dart
extension ResponseParsingEx<T> on Response<T> {
  /// Parse response body directly as single object
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
    } catch (e, st) {
      throw ParsingException(
        message: 'Failed to parse response',
        endpoint: endpoint,
        expectedType: '$R',
        rawJson: json,
        innerError: e,
      );
    }
  }

  /// Parse response to DTO then extract domain entity
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

  /// Parse list with partial failure tolerance
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
        // Continue processing other items
      }
    }
    return results;
  }
}
```

## Pagination Pattern

### Provider with Infinite Scroll

```dart
@riverpod
class {Entities} extends _{Entities} {
  {Entity}Api get _api => ref.read({entity}ApiProvider);

  @override
  FutureOr<{Entity}ListResult> build({
    String search = '',
    {Entity}SortBy sortBy = {Entity}SortBy.name,
  }) async {
    final response = await _api.get{Entities}(
      page: 1,
      limit: 20,
      search: search.isEmpty ? null : search,
    );

    return {Entity}ListResult(
      items: response.data,
      currentPage: 1,
      hasMore: response.pagination?.hasNextPage ?? false,
    );
  }

  Future<void> loadMore() async {
    final currentState = state.value;
    if (currentState == null || !currentState.hasMore) return;

    // Retain previous data during load
    state = const AsyncLoading<{Entity}ListResult>().copyWithPrevious(state);

    state = await AsyncValue.guard(() async {
      final response = await _api.get{Entities}(
        page: currentState.currentPage + 1,
        limit: 20,
      );

      return {Entity}ListResult(
        items: [...currentState.items, ...response.data],
        currentPage: currentState.currentPage + 1,
        hasMore: response.pagination?.hasNextPage ?? false,
      );
    });
  }
}

class {Entity}ListResult {
  const {Entity}ListResult({
    required this.items,
    required this.currentPage,
    required this.hasMore,
  });

  final List<{Entity}> items;
  final int currentPage;
  final bool hasMore;
}
```

## Secure Storage Integration

```dart
@Riverpod(keepAlive: true)
FlutterSecureStorage secureStorage(Ref ref) {
  return const FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );
}

class StorageKeys {
  static const authToken = 'auth_token';
  static const refreshToken = 'refresh_token';
  static const userId = 'user_id';
}

// Usage in auth flow
Future<void> saveTokens(String accessToken, String? refreshToken) async {
  final storage = ref.read(secureStorageProvider);
  await storage.write(key: StorageKeys.authToken, value: accessToken);
  if (refreshToken != null) {
    await storage.write(key: StorageKeys.refreshToken, value: refreshToken);
  }
}

Future<void> clearTokens() async {
  final storage = ref.read(secureStorageProvider);
  await storage.delete(key: StorageKeys.authToken);
  await storage.delete(key: StorageKeys.refreshToken);
}
```
