# Error Handling Patterns

Exception hierarchy, network error classification, provider error observers, centralized UI error display, and graceful degradation strategies.

## Exception Hierarchy

### Core Interfaces

```dart
/// Marker interface for exceptions that provide localized UI messages
abstract class LocalizedException implements Exception {
  /// Optional title for error dialogs/toasts
  String? get localizedTitle;

  /// Required message for user display
  String get localizedMessage;
}

/// Marker interface for expected errors that shouldn't be reported to Crashlytics
///
/// Examples: network issues, user cancellations, validation failures
abstract class ExpectedException implements Exception {}
```

### Dio Exception Wrapper

```dart
/// Base class for HTTP exceptions with localization support
abstract class {App}DioException extends DioException implements LocalizedException {
  {App}DioException(DioException? exception)
      : super(
          requestOptions: exception?.requestOptions ?? RequestOptions(),
          response: exception?.response,
          type: exception?.type ?? DioExceptionType.unknown,
          error: exception?.error,
        );
}
```

### Network Exceptions

```dart
/// No internet connection detected
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

  DioExceptionType? get networkType => type;

  @override
  String? get localizedTitle => LocaleKeys.errors_network_title.tr();

  @override
  String get localizedMessage => LocaleKeys.errors_network_message.tr();
}
```

### API Exception

```dart
/// API returned an error response (4xx, 5xx)
class ApiException extends {App}DioException {
  ApiException({
    this.serverMessage,
    DioException? exception,
  }) : super(exception);

  /// Error message from server response body
  final String? serverMessage;

  /// HTTP status code
  int? get statusCode => response?.statusCode;

  @override
  String? get localizedTitle => LocaleKeys.errors_server_title.tr();

  @override
  String get localizedMessage =>
      serverMessage ?? LocaleKeys.errors_server_message.tr();

  @override
  String toString() => 'ApiException [$statusCode]: $serverMessage';
}
```

### Parsing Exception

```dart
/// JSON parsing or type conversion failed
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
  String toString() {
    final buffer = StringBuffer('ParsingException');
    if (endpoint != null) buffer.write(' at $endpoint');
    buffer.write(': $message');
    if (expectedType != null) buffer.write(' [expected: $expectedType]');
    if (innerError != null) buffer.write('\nCaused by: $innerError');
    return buffer.toString();
  }
}
```

### Domain Exception

```dart
/// Business logic exception (expected, localized, don't report)
abstract class DomainException implements LocalizedException, ExpectedException {}

/// Example: Referral code not found
class ReferralCodeNotFoundException extends DomainException {
  const ReferralCodeNotFoundException();

  @override
  String? get localizedTitle => null;

  @override
  String get localizedMessage => LocaleKeys.errors_referral_not_found.tr();
}

/// Example: User cancelled authentication
class AuthCancelledException extends DomainException {
  const AuthCancelledException();

  @override
  String? get localizedTitle => null;

  @override
  String get localizedMessage => LocaleKeys.errors_auth_cancelled.tr();
}

/// Example: Business rule violation with server message
class VerificationIncompleteException extends DomainException {
  const VerificationIncompleteException({required this.serverMessage});

  final String serverMessage;

  @override
  String? get localizedTitle => LocaleKeys.errors_verification_title.tr();

  @override
  String get localizedMessage => serverMessage;

  @override
  String toString() => 'VerificationIncompleteException: $serverMessage';
}
```

### Crash Reporting Extension

```dart
extension ExceptionReportingEx on Object {
  /// Determines if this error should be reported to Crashlytics
  bool get shouldReportToCrashlytics {
    // Expected errors - don't report
    if (this is ExpectedException) return false;

    // User-cancelled requests - don't report
    if (this is DioException &&
        (this as DioException).type == DioExceptionType.cancel) {
      return false;
    }

    // Everything else - report
    return true;
  }
}
```

## Error Interceptor

```dart
/// Final interceptor that classifies and transforms Dio errors
class ApiErrorInterceptor extends Interceptor {
  @override
  void onError(DioException err, ErrorInterceptorHandler handler) {
    // Check for no internet first
    if (_isNoInternet(err)) {
      handler.reject(NoInternetException(exception: err));
      return;
    }

    // Check for network issues (timeouts, server unavailable)
    if (_isNetworkError(err)) {
      handler.reject(NetworkException(exception: err));
      return;
    }

    // Everything else is an API error
    final serverMessage = _extractServerMessage(err.response);
    handler.reject(ApiException(
      serverMessage: serverMessage,
      exception: err,
    ));
  }

  bool _isNoInternet(DioException err) {
    if (err.error is SocketException) return true;
    if (err.type == DioExceptionType.connectionError) return true;
    return false;
  }

  bool _isNetworkError(DioException err) {
    // Timeout errors
    if (err.type == DioExceptionType.connectionTimeout ||
        err.type == DioExceptionType.sendTimeout ||
        err.type == DioExceptionType.receiveTimeout) {
      return true;
    }

    // Server errors indicating infrastructure issues
    final statusCode = err.response?.statusCode;
    if (statusCode == HttpStatus.requestTimeout ||
        statusCode == HttpStatus.badGateway ||
        statusCode == HttpStatus.serviceUnavailable ||
        statusCode == HttpStatus.gatewayTimeout) {
      return true;
    }

    return false;
  }

  String? _extractServerMessage(Response? response) {
    final data = response?.data;
    if (data is Map<String, dynamic>) {
      // Try common error message fields
      return data['message'] as String? ??
          data['error'] as String? ??
          data['errorMessage'] as String?;
    }
    return null;
  }
}
```

## Provider Error Handling

### AsyncValue.guard Pattern

```dart
@riverpod
class Delete{Entity} extends _$Delete{Entity} {
  @override
  FutureOr<void> build() => null;

  Future<void> delete(String id) async {
    state = const AsyncLoading();

    state = await AsyncValue.guard(() async {
      final api = ref.read({entity}ApiProvider);
      await api.delete{Entity}(id);

      // Invalidate list provider on success
      ref.invalidate({entities}Provider);
    });
  }
}
```

### Centralized Error Listener

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
          // Apply ignore filter
          if (ignoreIf?.call(e) ?? false) return;

          // Custom error handler
          onError?.call(e);

          // Show toast with localized message
          AppToast.showError(context, error: e);
        },
      );
    });
  }
}
```

### Usage in Widget

```dart
class {Entity}Screen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen for errors from multiple providers
    ref.listenOnError(create{Entity}Provider);
    ref.listenOnError(
      delete{Entity}Provider,
      ignoreIf: (e) => e is AuthCancelledException, // Ignore user cancellations
    );

    final createState = ref.watch(create{Entity}Provider);
    final deleteState = ref.watch(delete{Entity}Provider);

    return Scaffold(
      body: /* ... */,
      floatingActionButton: FloatingActionButton(
        onPressed: createState.isLoading ? null : () => _onCreate(ref),
        child: createState.isLoading
            ? const CircularProgressIndicator()
            : const Icon(Icons.add),
      ),
    );
  }

  void _onCreate(WidgetRef ref) async {
    await ref.read(create{Entity}Provider.notifier).create(input);

    // Check for errors before proceeding
    if (ref.read(create{Entity}Provider).hasError) return;

    // Success - show confirmation and navigate
    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Created successfully')),
      );
      context.router.pop();
    }
  }
}
```

## Toast/Snackbar Display

```dart
class AppToast {
  /// Show error toast with localized message
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
            if (title != null)
              Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            Text(message),
          ],
        ),
        backgroundColor: Theme.of(context).colorScheme.error,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
        action: SnackBarAction(
          label: LocaleKeys.common_dismiss.tr(),
          textColor: Theme.of(context).colorScheme.onError,
          onPressed: () {
            ScaffoldMessenger.of(context).hideCurrentSnackBar();
          },
        ),
      ),
    );
  }

  /// Show success toast
  static void showSuccess(BuildContext context, {required String message}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.green,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 2),
      ),
    );
  }
}
```

## Provider Failure Observer

```dart
/// Observes all provider failures for logging and crash reporting
final class ProviderFailureObserver extends ProviderObserver {
  @override
  void providerDidFail(
    ProviderObserverContext context,
    Object error,
    StackTrace stackTrace,
  ) {
    final providerName =
        context.provider.name ?? context.provider.runtimeType.toString();

    if (error.shouldReportToCrashlytics) {
      log.error(
        'Provider [$providerName] threw ${error._debugMessage}',
        error,
        stackTrace,
      );

      // Report to Crashlytics
      FirebaseCrashlytics.instance.recordError(
        error,
        stackTrace,
        reason: 'Provider [$providerName] failure',
      );
    } else {
      log.warning(
        'Provider [$providerName] threw expected error: ${error._debugMessage}',
      );
    }
  }
}

extension on Object {
  String get _debugMessage {
    if (this is ApiException) {
      final e = this as ApiException;
      return 'ApiException [${e.statusCode}]: ${e.serverMessage}';
    }
    if (this is NoInternetException) return 'NoInternetException';
    if (this is NetworkException) {
      return 'NetworkException [${(this as NetworkException).networkType}]';
    }
    if (this is ParsingException) {
      final e = this as ParsingException;
      return 'ParsingException [${e.endpoint}]: ${e.message}';
    }
    return toString();
  }
}
```

### Registration

```dart
void main() {
  runApp(
    ProviderScope(
      observers: [ProviderFailureObserver()],
      child: const MyApp(),
    ),
  );
}
```

## Local Storage Error Handling

### Graceful Fallback Pattern

```dart
/// Read from cache with graceful fallback
Future<{Entity}?> getCached{Entity}() async {
  try {
    final json = _prefs.getString(_cacheKey);
    if (json == null) return null;

    final data = jsonDecode(json) as Map<String, dynamic>;
    return {Entity}.fromJson(data);
  } catch (e) {
    // Invalid cache data - clear it and return null
    log.warning('Failed to read cached {entity}, clearing cache', e);
    await clearCache();
    return null;
  }
}

/// Write to cache with error swallowing
Future<void> cache{Entity}({Entity} entity) async {
  try {
    final json = jsonEncode(entity.toJson());
    await _prefs.setString(_cacheKey, json);
  } catch (e) {
    // Non-critical - just log and continue
    log.warning('Failed to cache {entity}', e);
  }
}
```

### Self-Healing Cache

```dart
class CacheManager {
  /// Get cached status with automatic corruption handling
  static bool? getCachedStatus({
    required SharedPreferences prefs,
    required String userId,
    required String entityId,
  }) {
    try {
      final key = _cacheKey(userId, entityId);
      final json = prefs.getString(key);
      if (json == null) return null;

      final data = jsonDecode(json) as Map<String, dynamic>;
      final expiresAt = DateTime.tryParse(data['expiresAt'] as String? ?? '');

      // Check expiration
      if (expiresAt != null && DateTime.now().isAfter(expiresAt)) {
        prefs.remove(key);
        return null;
      }

      return data['status'] as bool?;
    } catch (e) {
      // Corrupted cache - clear and return null
      log.warning('Cache corrupted, clearing', e);
      prefs.remove(_cacheKey(userId, entityId));
      return null;
    }
  }

  static String _cacheKey(String userId, String entityId) =>
      'cache_${userId}_$entityId';
}
```

## Domain Error Mapping

### HTTP Status to Domain Exception

```dart
Future<void> validateCode(String code) async {
  try {
    final response = await _dio.post<Map<String, dynamic>>(
      _api.validate,
      data: {'code': code},
    );

    final success = response.data?['success'] == true;
    if (!success) {
      throw const CodeNotFoundException();
    }
  } on ApiException catch (e) {
    // Map specific HTTP errors to domain exceptions
    if (e.statusCode == 404) {
      throw const CodeNotFoundException();
    }
    if (e.statusCode == 429) {
      throw const RateLimitException();
    }
    rethrow; // Other errors propagate as-is
  }
}
```

## Structured Logging

```dart
final log = Logger.detached('{AppName}');

void initLogging() {
  log.level = kDebugMode ? Level.FINE : Level.INFO;

  log.onRecord.listen((record) {
    final timestamp = DateFormat('HH:mm:ss.S').format(record.time);
    final message = '$timestamp - ${record.message}';

    if (record.level >= Level.SEVERE) {
      // Red for errors
      dev.log('\x1B[31m${record.message}\x1B[0m');
      if (kDebugMode && record.stackTrace != null) {
        debugPrintStack(stackTrace: record.stackTrace);
      }
    } else if (record.level == Level.WARNING) {
      // Yellow for warnings
      dev.log('\x1B[33m${record.message}\x1B[0m');
    } else if (record.level == Level.INFO) {
      // Green for info
      dev.log('\x1B[32m${record.message}\x1B[0m');
    } else {
      // Blue for debug
      dev.log('\x1B[34m$message\x1B[0m');
    }
  });
}

extension LoggingUtility on Logger {
  void error(Object? message, [Object? error, StackTrace? stackTrace]) =>
      severe(message, error, stackTrace);

  void debug(Object? message, [Object? error, StackTrace? stackTrace]) =>
      fine(message, error, stackTrace);
}
```

## Error Recovery Patterns

### Check State After Async Action

```dart
void _onSubmit() async {
  await ref.read(submitProvider.notifier).submit(input);

  // Always check for errors before proceeding
  if (ref.read(submitProvider).hasError) return;

  // Check mounted before using context
  if (!context.mounted) return;

  // Success path
  context.router.pop(true);
}
```

### Retry Pattern

```dart
class RetryConfig {
  const RetryConfig({
    this.maxAttempts = 3,
    this.delay = const Duration(seconds: 1),
    this.backoff = 2.0,
  });

  final int maxAttempts;
  final Duration delay;
  final double backoff;
}

Future<T> withRetry<T>({
  required Future<T> Function() operation,
  RetryConfig config = const RetryConfig(),
  bool Function(Object)? shouldRetry,
}) async {
  var attempts = 0;
  var currentDelay = config.delay;

  while (true) {
    try {
      return await operation();
    } catch (e) {
      attempts++;

      // Don't retry expected errors
      if (e is ExpectedException) rethrow;

      // Check custom retry predicate
      if (shouldRetry != null && !shouldRetry(e)) rethrow;

      // Max attempts reached
      if (attempts >= config.maxAttempts) rethrow;

      // Wait before retry
      await Future.delayed(currentDelay);
      currentDelay *= config.backoff;
    }
  }
}
```

## Error UI Components

### Error State Widget

```dart
class ErrorStateWidget extends StatelessWidget {
  const ErrorStateWidget({
    required this.error,
    required this.onRetry,
    this.title,
    super.key,
  });

  final Object error;
  final VoidCallback onRetry;
  final String? title;

  @override
  Widget build(BuildContext context) {
    final message = error is LocalizedException
        ? (error as LocalizedException).localizedMessage
        : LocaleKeys.errors_unknown.tr();

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              _iconForError(error),
              size: 64,
              color: Theme.of(context).colorScheme.error,
            ),
            const SizedBox(height: 16),
            if (title != null)
              Text(
                title!,
                style: Theme.of(context).textTheme.titleLarge,
                textAlign: TextAlign.center,
              ),
            const SizedBox(height: 8),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: Text(LocaleKeys.common_retry.tr()),
            ),
          ],
        ),
      ),
    );
  }

  IconData _iconForError(Object error) {
    if (error is NoInternetException) return Icons.wifi_off;
    if (error is NetworkException) return Icons.cloud_off;
    return Icons.error_outline;
  }
}
```

### Usage in AsyncValue Builder

```dart
Widget build(BuildContext context, WidgetRef ref) {
  final state = ref.watch({entities}Provider);

  return state.when(
    loading: () => const Center(child: CircularProgressIndicator()),
    error: (error, _) => ErrorStateWidget(
      error: error,
      onRetry: () => ref.invalidate({entities}Provider),
      title: LocaleKeys.{entities}_load_error_title.tr(),
    ),
    data: (entities) => ListView.builder(
      itemCount: entities.length,
      itemBuilder: (context, index) => {Entity}Tile(entity: entities[index]),
    ),
  );
}
```
