library;

/// SAHOOL Error Handler Utilities
/// أدوات معالجة الأخطاء لتطبيق سهول
///
/// Provides:
/// - Centralized error handling
/// - Error recovery mechanisms
/// - User-facing error display helpers
/// - Error reporting integration

import 'dart:async';
import 'package:flutter/foundation.dart';
import '../utils/app_logger.dart';
import 'app_exceptions.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Error Handler Service
// ═══════════════════════════════════════════════════════════════════════════

/// Centralized error handler for the SAHOOL app
class ErrorHandler {
  static final ErrorHandler _instance = ErrorHandler._internal();
  factory ErrorHandler() => _instance;
  ErrorHandler._internal();

  /// Error listeners for reporting
  final List<void Function(AppException error, StackTrace? stackTrace)>
      _listeners = [];

  /// Register an error listener (e.g., for crash reporting)
  void addListener(
      void Function(AppException error, StackTrace? stackTrace) listener) {
    _listeners.add(listener);
  }

  /// Remove an error listener
  void removeListener(
      void Function(AppException error, StackTrace? stackTrace) listener) {
    _listeners.remove(listener);
  }

  /// Handle an error, convert to AppException, log, and notify listeners
  AppException handle(
    Object error, {
    StackTrace? stackTrace,
    String? tag,
    bool log = true,
    bool notifyListeners = true,
  }) {
    // Convert to AppException
    final appException = error is AppException
        ? error.copyWith(
            originalStackTrace: stackTrace ?? error.originalStackTrace)
        : error.toAppException().copyWith(originalStackTrace: stackTrace);

    // Log if requested
    if (log) {
      appException.log(tag: tag);
    }

    // Notify listeners
    if (notifyListeners) {
      for (final listener in _listeners) {
        try {
          listener(appException, stackTrace);
        } catch (e) {
          if (kDebugMode) {
            AppLogger.w('Error listener threw an exception',
                tag: 'ErrorHandler', data: {'error': e.toString()});
          }
        }
      }
    }

    return appException;
  }

  /// Execute a function with error handling
  Future<T> tryAsync<T>(
    Future<T> Function() action, {
    String? tag,
    T Function(AppException error)? onError,
    bool shouldRethrow = true,
  }) async {
    try {
      return await action();
    } catch (e, stackTrace) {
      final appException = handle(e, stackTrace: stackTrace, tag: tag);

      if (onError != null) {
        return onError(appException);
      }

      if (shouldRethrow) {
        throw appException;
      }

      // This shouldn't be reached, but Dart requires a return
      throw appException;
    }
  }

  /// Execute a function with retry capability
  Future<T> tryWithRetry<T>(
    Future<T> Function() action, {
    String? tag,
    int maxRetries = 3,
    Duration initialDelay = const Duration(seconds: 1),
    Duration maxDelay = const Duration(seconds: 30),
    bool Function(AppException)? shouldRetry,
  }) async {
    int attempt = 0;
    Duration delay = initialDelay;

    while (true) {
      try {
        return await action();
      } catch (e, stackTrace) {
        attempt++;
        final appException =
            handle(e, stackTrace: stackTrace, tag: tag, log: attempt == 1);

        // Check if we should retry
        final canRetry = attempt < maxRetries &&
            (shouldRetry?.call(appException) ?? appException.isRetryable);

        if (!canRetry) {
          throw appException;
        }

        // Log retry attempt
        AppLogger.w(
          'Retrying after error (attempt $attempt/$maxRetries)',
          tag: tag ?? 'ErrorHandler',
          data: {'error': appException.code, 'delayMs': delay.inMilliseconds},
        );

        // Wait before retrying (exponential backoff)
        await Future<void>.delayed(delay);
        delay = Duration(
            milliseconds:
                (delay.inMilliseconds * 2).clamp(0, maxDelay.inMilliseconds));
      }
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Recovery Strategies
// ═══════════════════════════════════════════════════════════════════════════

/// Recovery strategies for different error types
enum RecoveryStrategy {
  /// Retry the operation
  retry,

  /// Use cached/offline data
  useCache,

  /// Prompt user to log in again
  reAuthenticate,

  /// Show error and let user retry manually
  manualRetry,

  /// Navigate to a fallback screen
  navigateFallback,

  /// No recovery possible
  none,
}

/// Get recommended recovery strategy for an exception
RecoveryStrategy getRecoveryStrategy(AppException exception) {
  switch (exception.type) {
    case ErrorType.network:
      return exception.isRetryable
          ? RecoveryStrategy.retry
          : RecoveryStrategy.useCache;

    case ErrorType.server:
      return RecoveryStrategy.retry;

    case ErrorType.auth:
      if (exception.code == 'SESSION_EXPIRED' ||
          exception.code == 'UNAUTHORIZED') {
        return RecoveryStrategy.reAuthenticate;
      }
      return RecoveryStrategy.manualRetry;

    case ErrorType.timeout:
      return RecoveryStrategy.retry;

    case ErrorType.sync:
      return RecoveryStrategy.useCache;

    case ErrorType.rateLimit:
      return RecoveryStrategy.retry;

    case ErrorType.validation:
    case ErrorType.client:
      return RecoveryStrategy.manualRetry;

    case ErrorType.notFound:
      return RecoveryStrategy.navigateFallback;

    case ErrorType.security:
    case ErrorType.storage:
      return RecoveryStrategy.none;

    case ErrorType.unknown:
      return exception.isRetryable
          ? RecoveryStrategy.retry
          : RecoveryStrategy.manualRetry;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Result Pattern
// ═══════════════════════════════════════════════════════════════════════════

/// Result type for operations that can fail
/// This provides a safer alternative to try-catch
sealed class Result<T> {
  const Result();

  /// Map success value
  Result<R> map<R>(R Function(T value) transform) {
    return switch (this) {
      Success<T>(value: final v) => Success(transform(v)),
      Failure<T>(error: final e, stackTrace: final s) => Failure(e, s),
    };
  }

  /// Transform both success and failure
  R when<R>({
    required R Function(T value) success,
    required R Function(AppException error) failure,
  }) {
    return switch (this) {
      Success<T>(value: final v) => success(v),
      Failure<T>(error: final e) => failure(e),
    };
  }

  /// Get value or throw
  T getOrThrow() {
    return switch (this) {
      Success<T>(value: final v) => v,
      Failure<T>(error: final e) => throw e,
    };
  }

  /// Get value or default
  T getOrElse(T defaultValue) {
    return switch (this) {
      Success<T>(value: final v) => v,
      Failure<T>() => defaultValue,
    };
  }

  /// Get value or compute default
  T getOrElseCompute(T Function(AppException error) compute) {
    return switch (this) {
      Success<T>(value: final v) => v,
      Failure<T>(error: final e) => compute(e),
    };
  }

  /// Check if success
  bool get isSuccess => this is Success<T>;

  /// Check if failure
  bool get isFailure => this is Failure<T>;

  /// Get value if success
  T? get valueOrNull => switch (this) {
        Success<T>(value: final v) => v,
        Failure<T>() => null,
      };

  /// Get error if failure
  AppException? get errorOrNull => switch (this) {
        Success<T>() => null,
        Failure<T>(error: final e) => e,
      };
}

/// Success result
class Success<T> extends Result<T> {
  final T value;
  const Success(this.value);

  @override
  String toString() => 'Success($value)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Success<T> &&
          runtimeType == other.runtimeType &&
          value == other.value;

  @override
  int get hashCode => value.hashCode;
}

/// Failure result
class Failure<T> extends Result<T> {
  final AppException error;
  final StackTrace? stackTrace;

  const Failure(this.error, [this.stackTrace]);

  @override
  String toString() => 'Failure(${error.code}: ${error.message})';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Failure<T> &&
          runtimeType == other.runtimeType &&
          error.code == other.error.code;

  @override
  int get hashCode => error.code.hashCode;
}

/// Extension to wrap async operations in Result
extension ResultFuture<T> on Future<T> {
  /// Execute and wrap in Result
  Future<Result<T>> toResult({String? tag}) async {
    try {
      return Success(await this);
    } catch (e, stackTrace) {
      final appException =
          ErrorHandler().handle(e, stackTrace: stackTrace, tag: tag);
      return Failure(appException, stackTrace);
    }
  }
}

/// Execute a function and wrap in Result
Future<Result<T>> runCatching<T>(Future<T> Function() action,
    {String? tag}) async {
  try {
    return Success(await action());
  } catch (e, stackTrace) {
    final appException =
        ErrorHandler().handle(e, stackTrace: stackTrace, tag: tag);
    return Failure(appException, stackTrace);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Display Helpers
// ═══════════════════════════════════════════════════════════════════════════

/// Information for displaying an error to the user
class ErrorDisplayInfo {
  /// Title for the error dialog/snackbar
  final String title;

  /// Arabic title
  final String titleAr;

  /// Detailed message
  final String message;

  /// Arabic message
  final String messageAr;

  /// Icon to display
  final String? iconName;

  /// Whether to show a retry button
  final bool showRetry;

  /// Recovery action label
  final String? actionLabel;

  /// Arabic action label
  final String? actionLabelAr;

  /// Recovery strategy
  final RecoveryStrategy recoveryStrategy;

  const ErrorDisplayInfo({
    required this.title,
    required this.titleAr,
    required this.message,
    required this.messageAr,
    this.iconName,
    this.showRetry = false,
    this.actionLabel,
    this.actionLabelAr,
    this.recoveryStrategy = RecoveryStrategy.none,
  });

  /// Get title based on locale
  String getTitle({bool isArabic = true}) => isArabic ? titleAr : title;

  /// Get message based on locale
  String getMessage({bool isArabic = true}) => isArabic ? messageAr : message;

  /// Get action label based on locale
  String? getActionLabel({bool isArabic = true}) =>
      isArabic ? actionLabelAr : actionLabel;
}

/// Get display information for an exception
ErrorDisplayInfo getErrorDisplayInfo(AppException exception) {
  final strategy = getRecoveryStrategy(exception);

  // Determine title based on error type
  String title;
  String titleAr;
  String? iconName;

  switch (exception.type) {
    case ErrorType.network:
      title = 'Connection Error';
      titleAr = 'خطأ في الاتصال';
      iconName = 'wifi_off';
      break;
    case ErrorType.server:
      title = 'Server Error';
      titleAr = 'خطأ في الخادم';
      iconName = 'cloud_off';
      break;
    case ErrorType.auth:
      title = 'Authentication Required';
      titleAr = 'المصادقة مطلوبة';
      iconName = 'lock';
      break;
    case ErrorType.validation:
      title = 'Invalid Input';
      titleAr = 'إدخال غير صالح';
      iconName = 'warning';
      break;
    case ErrorType.notFound:
      title = 'Not Found';
      titleAr = 'غير موجود';
      iconName = 'search_off';
      break;
    case ErrorType.rateLimit:
      title = 'Please Slow Down';
      titleAr = 'يرجى التمهل';
      iconName = 'hourglass_empty';
      break;
    case ErrorType.security:
      title = 'Security Alert';
      titleAr = 'تنبيه أمني';
      iconName = 'security';
      break;
    case ErrorType.storage:
      title = 'Storage Error';
      titleAr = 'خطأ في التخزين';
      iconName = 'storage';
      break;
    case ErrorType.sync:
      title = 'Sync Issue';
      titleAr = 'مشكلة في المزامنة';
      iconName = 'sync_problem';
      break;
    case ErrorType.timeout:
      title = 'Request Timed Out';
      titleAr = 'انتهت مهلة الطلب';
      iconName = 'timer_off';
      break;
    case ErrorType.client:
    case ErrorType.unknown:
      title = 'Error';
      titleAr = 'خطأ';
      iconName = 'error_outline';
      break;
  }

  // Determine action label based on recovery strategy
  String? actionLabel;
  String? actionLabelAr;
  switch (strategy) {
    case RecoveryStrategy.retry:
    case RecoveryStrategy.manualRetry:
      actionLabel = 'Try Again';
      actionLabelAr = 'حاول مرة أخرى';
      break;
    case RecoveryStrategy.useCache:
      actionLabel = 'Use Offline Data';
      actionLabelAr = 'استخدم البيانات المحفوظة';
      break;
    case RecoveryStrategy.reAuthenticate:
      actionLabel = 'Log In';
      actionLabelAr = 'تسجيل الدخول';
      break;
    case RecoveryStrategy.navigateFallback:
      actionLabel = 'Go Back';
      actionLabelAr = 'العودة';
      break;
    case RecoveryStrategy.none:
      actionLabel = 'OK';
      actionLabelAr = 'حسنًا';
      break;
  }

  return ErrorDisplayInfo(
    title: title,
    titleAr: titleAr,
    message: exception.message,
    messageAr: exception.messageAr,
    iconName: iconName,
    showRetry: exception.isRetryable,
    actionLabel: actionLabel,
    actionLabelAr: actionLabelAr,
    recoveryStrategy: strategy,
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Global Error Handler Setup
// ═══════════════════════════════════════════════════════════════════════════

/// Set up global error handling for the app
void setupErrorHandling({
  void Function(AppException error, StackTrace? stackTrace)? onError,
}) {
  // Register error listener if provided
  if (onError != null) {
    ErrorHandler().addListener(onError);
  }

  // Handle uncaught async errors
  FlutterError.onError = (FlutterErrorDetails details) {
    final appException = ErrorHandler().handle(
      details.exception,
      stackTrace: details.stack,
      tag: 'Flutter',
    );

    // Present error in debug mode
    if (kDebugMode) {
      FlutterError.presentError(details);
    }

    // Notify listener
    onError?.call(appException, details.stack);
  };

  // Handle errors outside of Flutter framework
  PlatformDispatcher.instance.onError = (error, stack) {
    final appException = ErrorHandler().handle(
      error,
      stackTrace: stack,
      tag: 'Platform',
    );

    onError?.call(appException, stack);
    return true;
  };
}
