---
name: integrate-rest-api
description: Integrates production-ready REST API infrastructure with Dio, Riverpod, and comprehensive error handling
---

<objective>
Provides production-ready REST API infrastructure patterns for Flutter apps using Dio, Riverpod, and json_serializable. Includes auth interceptors, exception hierarchy with localized messages, response parsing extensions, and mock API support for seamless development.
</objective>

<quick_start>
1. Add dependencies to pubspec.yaml (dio, riverpod_annotation, json_annotation, equatable)
2. Create Dio provider with interceptor chain (Auth, Logging, Error)
3. Define abstract API interface for your feature
4. Implement with response parsing extensions for type-safe responses
5. Use AsyncValue.guard in providers for error capture
6. Add listenOnError in widgets for centralized error display
</quick_start>

<success_criteria>
- Dio provider configured with auth, logging, and error interceptors in correct order
- API classes follow abstract interface pattern enabling mock substitution
- Errors classified into LocalizedException types with user-facing messages
- ExpectedException marker prevents expected errors from reaching crash reporting
- Provider errors display automatically via listenOnError extension
- All entities use json_serializable with Equatable for value equality
- Response parsing uses endpoint context for debugging failed parses
</success_criteria>

<overview>
A complete REST API infrastructure module for Flutter apps using Dio for HTTP, Riverpod for dependency injection, and json_serializable for type-safe serialization.

<domains>
- **API Infrastructure**: Dio configuration, auth interceptors, API class organization, response parsing
- **DTO/Entity**: json_serializable patterns, nullable handling, enums, nested objects, pagination
- **Error Handling**: Exception hierarchy, network error classification, provider observers, UI error display
</domains>

<dependencies>
- `dio`: ^5.9.0 (HTTP client with interceptor support)
- `riverpod_annotation`: ^2.x (Code-generated providers)
- `flutter_riverpod`: ^2.x (State management and DI)
- `json_annotation`: ^4.9.0 (Serialization annotations)
- `json_serializable`: ^6.11.0 (Code generation for JSON)
- `equatable`: ^2.0.7 (Value-based equality)
- `easy_localization`: ^3.x (Localized error messages)
- `flutter_secure_storage`: ^9.x (Secure token storage)
- `logging`: ^1.x (Structured logging)
</dependencies>
</overview>

<patterns>

<pattern name="Dio Configuration Provider">
Centralized Dio instance with keepAlive: true for singleton lifecycle. Configures base URL, timeouts, and interceptor chain (Auth -> Logging -> Error).
</pattern>

<pattern name="Auth Token Interceptor">
Automatically injects Bearer token for non-public routes using whitelist pattern. Clears token on 401 response to trigger re-authentication.
</pattern>

<pattern name="Abstract API Interface">
Each feature defines abstract API interface with concrete implementation. Enables mock substitution via Riverpod provider that checks mock mode from environment config.
</pattern>

<pattern name="Response Parsing Extensions">
Safe response parsing with context-aware error handling. Three strategies: parseSingle (object), parseWrapped (extract from DTO), parseList (partial failure tolerance).
</pattern>

<pattern name="Exception Hierarchy">
Multi-level exception inheritance with marker interfaces. LocalizedException provides UI text. ExpectedException marks errors to skip crash reporting.
</pattern>

<pattern name="Error Interceptor">
Final interceptor that transforms DioException into typed exceptions. Classifies errors by type (no internet, timeout, API error) and extracts server messages.
</pattern>

<pattern name="Provider Error Listener">
WidgetRef extension that centralizes error display. Shows toast with localized message. Supports ignoreIf predicate for conditional error suppression.
</pattern>

<pattern name="json_serializable Entity">
Standard serialization combining json_serializable with Equatable. Uses explicitToJson for nested objects and includeIfNull: false for optimized output.
</pattern>

<pattern name="Enum with JsonValue">
Enums use @JsonValue annotation for bidirectional string mapping. Provides type-safe conversion without manual switch statements.
</pattern>

<pattern name="Response DTO with Pagination">
API response wrapper with status, data, and optional pagination metadata. Thin wrapper around domain entities for response structure.
</pattern>

<pattern name="AsyncValue.guard Provider">
Wraps async operations with AsyncValue.guard() to capture errors in state. Invalidates related providers after successful mutations.
</pattern>

</patterns>

<validation>
<check name="Interceptor Order">
ApiErrorInterceptor must be last in the interceptor chain. Auth and Logging interceptors run first, then Error catches and transforms all exceptions.
</check>

<check name="Generated Files Missing">
Run `flutter pub run build_runner build --delete-conflicting-outputs` after adding or modifying @JsonSerializable classes or @riverpod providers.
</check>

<check name="401 Loops">
If experiencing infinite 401 loops, verify token storage provider is correctly configured and onUnauthorized callback properly clears the stored token.
</check>

<check name="Parsing Failures">
ParsingException includes endpoint and expectedType for debugging. Check API response structure matches expected DTO. Use parseList for graceful degradation on lists.
</check>

<check name="Error Not Displayed">
Ensure ref.listenOnError is called in widget build method before any async operations. Verify error implements LocalizedException for proper message extraction.
</check>

<check name="Mock Mode Not Working">
Verify envConfigProvider.isMockMode returns true. Check ENABLE_MOCK_MODE environment variable and kDebugMode flag in EnvConfig setup.
</check>
</validation>

<example name="Complete API Setup">
<scenario>Setting up API infrastructure for a new feature module</scenario>

<usage language="dart">
// 1. Define endpoints
class ApiEndpoint {
  const ApiEndpoint();
  String get products => '/api/products';
  String product(String id) => '/api/products/$id';
}

// 2. Define entity with json_serializable
@JsonSerializable(explicitToJson: true, includeIfNull: false)
class Product extends Equatable {
  const Product({required this.id, required this.name, this.price});
  factory Product.fromJson(Map<String, dynamic> json) => _$ProductFromJson(json);

  final String id;
  final String name;
  final double? price;

  Map<String, dynamic> toJson() => _$ProductToJson(this);

  @override
  List<Object?> get props => [id, name, price];
}

// 3. Define abstract API interface
abstract class ProductApi {
  Future<Product> getProduct(String id);
  Future<List<Product>> getProducts();
}

// 4. Implement with parsing extensions
class ProductApiImpl implements ProductApi {
  ProductApiImpl(this._dio);
  final Dio _dio;

  @override
  Future<Product> getProduct(String id) async {
    final response = await _dio.get<Map<String, dynamic>>('/api/products/$id');
    return response.parseSingle(fromJson: Product.fromJson, endpoint: 'getProduct');
  }

  @override
  Future<List<Product>> getProducts() async {
    final response = await _dio.get<Map<String, dynamic>>('/api/products');
    return response.parseWrapped(
      fromJson: ProductListResponse.fromJson,
      extract: (dto) => dto.data,
      endpoint: 'getProducts',
    );
  }
}

// 5. Provider with mock support
@riverpod
ProductApi productApi(Ref ref) {
  if (ref.read(envConfigProvider).isMockMode) {
    return ProductMockApi();
  }
  return ProductApiImpl(ref.watch(dioProvider));
}

// 6. Widget with error handling
class ProductScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listenOnError(productsProvider);

    return ref.watch(productsProvider).when(
      loading: () => const CircularProgressIndicator(),
      error: (e, _) => ErrorStateWidget(error: e, onRetry: () => ref.invalidate(productsProvider)),
      data: (products) => ProductList(products: products),
    );
  }
}
</usage>

<notes>
- Entity uses json_serializable with Equatable for value equality
- API interface enables mock substitution for development
- Response parsing uses extensions with endpoint context for debugging
- Provider checks mock mode for seamless development workflow
- Widget uses listenOnError for centralized error display
</notes>
</example>

<references>
<reference file="references/patterns.md">Complete pattern implementations with code and rationale</reference>
<reference file="references/api-infrastructure.md">HTTP client configuration, interceptors, API class patterns, response parsing</reference>
<reference file="references/dto-entity.md">JSON serialization patterns, nullable handling, enums, nested objects</reference>
<reference file="references/error-handling.md">Exception hierarchy, error classification, provider observers, UI display</reference>
</references>
