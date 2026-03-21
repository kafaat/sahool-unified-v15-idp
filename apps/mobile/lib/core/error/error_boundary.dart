/// SAHOOL Error Boundary Widget
/// حاجز الأخطاء - التقاط الأخطاء في شجرة الواجهات
///
/// A comprehensive error boundary widget that catches errors in the widget tree
/// and displays user-friendly fallback UI. Supports RTL layout for Arabic.
library;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'error_fallback.dart';
import 'error_messages.dart';
import 'error_reporter.dart';

/// Error boundary configuration
class ErrorBoundaryConfig {
  /// Whether to show debug information in error UI
  final bool showDebugInfo;

  /// Whether to report errors to crash reporting
  final bool reportErrors;

  /// Custom error message to display
  final ErrorMessage? errorMessage;

  /// Screen name for error context
  final String? screenName;

  /// Whether to allow retry
  final bool allowRetry;

  /// Whether to allow going back
  final bool allowGoBack;

  const ErrorBoundaryConfig({
    this.showDebugInfo = false,
    this.reportErrors = true,
    this.errorMessage,
    this.screenName,
    this.allowRetry = true,
    this.allowGoBack = true,
  });

  /// Debug mode configuration
  static const ErrorBoundaryConfig debug = ErrorBoundaryConfig(
    showDebugInfo: true,
    reportErrors: true,
    allowRetry: true,
    allowGoBack: true,
  );

  /// Production mode configuration
  static const ErrorBoundaryConfig production = ErrorBoundaryConfig(
    showDebugInfo: false,
    reportErrors: true,
    allowRetry: true,
    allowGoBack: true,
  );
}

/// Error boundary widget that catches errors in the widget tree
class ErrorBoundary extends StatefulWidget {
  /// The child widget to wrap
  final Widget child;

  /// Configuration for the error boundary
  final ErrorBoundaryConfig config;

  /// Optional callback when an error occurs
  final void Function(Object error, StackTrace? stackTrace)? onError;

  /// Custom error widget builder
  final Widget Function(
    BuildContext context,
    Object error,
    StackTrace? stackTrace,
    VoidCallback retry,
  )? errorBuilder;

  /// Callback when retry is pressed
  final VoidCallback? onRetry;

  /// Callback when go back is pressed
  final VoidCallback? onGoBack;

  const ErrorBoundary({
    super.key,
    required this.child,
    this.config = const ErrorBoundaryConfig(),
    this.onError,
    this.errorBuilder,
    this.onRetry,
    this.onGoBack,
  });

  /// Create error boundary with debug configuration
  factory ErrorBoundary.debug({
    Key? key,
    required Widget child,
    void Function(Object error, StackTrace? stackTrace)? onError,
    Widget Function(
      BuildContext context,
      Object error,
      StackTrace? stackTrace,
      VoidCallback retry,
    )? errorBuilder,
  }) {
    return ErrorBoundary(
      key: key,
      config: ErrorBoundaryConfig.debug,
      onError: onError,
      errorBuilder: errorBuilder,
      child: child,
    );
  }

  /// Create error boundary for a specific screen
  factory ErrorBoundary.screen({
    Key? key,
    required Widget child,
    required String screenName,
    void Function(Object error, StackTrace? stackTrace)? onError,
    VoidCallback? onRetry,
    VoidCallback? onGoBack,
  }) {
    return ErrorBoundary(
      key: key,
      config: ErrorBoundaryConfig(
        screenName: screenName,
        showDebugInfo: kDebugMode,
        allowRetry: true,
        allowGoBack: true,
      ),
      onError: onError,
      onRetry: onRetry,
      onGoBack: onGoBack,
      child: child,
    );
  }

  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  Object? _error;
  StackTrace? _stackTrace;
  int _retryCount = 0;
  static const int _maxRetries = 3;

  @override
  void initState() {
    super.initState();
    // Record breadcrumb for screen entry
    if (widget.config.screenName != null) {
      errorReporter.recordBreadcrumb(
        message: 'Entered screen: ${widget.config.screenName}',
        category: 'navigation',
      );
    }
  }

  /// Handle error caught by the error boundary
  void _handleError(Object error, StackTrace? stackTrace) {
    setState(() {
      _error = error;
      _stackTrace = stackTrace;
    });

    // Call user callback
    widget.onError?.call(error, stackTrace);

    // Report error if enabled
    if (widget.config.reportErrors) {
      errorReporter.reportError(
        error,
        stackTrace: stackTrace,
        severity: ReportSeverity.error,
        context: ErrorContext.current(
          screen: widget.config.screenName,
          widget: 'ErrorBoundary',
          recoverable: true,
        ),
      );
    }
  }

  /// Retry/reset the error state
  void _retry() {
    _retryCount++;

    if (_retryCount > _maxRetries) {
      // Too many retries, show permanent error
      errorReporter.recordBreadcrumb(
        message: 'Max retry attempts reached',
        category: 'error',
        data: {'retryCount': _retryCount},
      );
      return;
    }

    errorReporter.recordBreadcrumb(
      message: 'User retry attempt',
      category: 'user_action',
      data: {'retryCount': _retryCount},
    );

    setState(() {
      _error = null;
      _stackTrace = null;
    });

    widget.onRetry?.call();
  }

  /// Go back handler
  void _goBack() {
    errorReporter.recordBreadcrumb(
      message: 'User navigated back from error',
      category: 'user_action',
    );

    if (widget.onGoBack != null) {
      widget.onGoBack!();
    } else if (Navigator.of(context).canPop()) {
      Navigator.of(context).pop();
    }
  }

  @override
  Widget build(BuildContext context) {
    // If there's an error, show error UI
    if (_error != null) {
      // Use custom error builder if provided
      if (widget.errorBuilder != null) {
        return widget.errorBuilder!(
          context,
          _error!,
          _stackTrace,
          _retry,
        );
      }

      // Use default error fallback
      return ErrorFallbackScreen(
        error: _error!,
        stackTrace: _stackTrace,
        onRetry: widget.config.allowRetry && _retryCount < _maxRetries
            ? _retry
            : null,
        onGoBack: widget.config.allowGoBack ? _goBack : null,
        errorMessage: widget.config.errorMessage,
        showDebugInfo: widget.config.showDebugInfo || kDebugMode,
      );
    }

    // Wrap child in error catcher
    return _ErrorCatcher(
      onError: _handleError,
      child: widget.child,
    );
  }
}

/// Internal widget that catches errors using ErrorWidget.builder
class _ErrorCatcher extends StatefulWidget {
  final Widget child;
  final void Function(Object error, StackTrace? stackTrace) onError;

  const _ErrorCatcher({
    required this.child,
    required this.onError,
  });

  @override
  State<_ErrorCatcher> createState() => _ErrorCatcherState();
}

class _ErrorCatcherState extends State<_ErrorCatcher> {
  @override
  void initState() {
    super.initState();
    // Store the original ErrorWidget.builder
    _originalErrorBuilder = ErrorWidget.builder;
    // Set custom builder that notifies parent
    ErrorWidget.builder = _buildErrorWidget;
  }

  @override
  void dispose() {
    // Restore original ErrorWidget.builder
    if (_originalErrorBuilder != null) {
      ErrorWidget.builder = _originalErrorBuilder!;
    }
    super.dispose();
  }

  static Widget Function(FlutterErrorDetails)? _originalErrorBuilder;

  Widget _buildErrorWidget(FlutterErrorDetails details) {
    // Schedule error handling for after build
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        widget.onError(details.exception, details.stack);
      }
    });

    // Return empty container while handling error
    return const SizedBox.shrink();
  }

  @override
  Widget build(BuildContext context) {
    return widget.child;
  }
}

/// Riverpod-aware error boundary
class ConsumerErrorBoundary extends ConsumerStatefulWidget {
  /// The child widget to wrap
  final Widget child;

  /// Configuration for the error boundary
  final ErrorBoundaryConfig config;

  /// Optional callback when an error occurs
  final void Function(Object error, StackTrace? stackTrace)? onError;

  /// Custom error widget builder
  final Widget Function(
    BuildContext context,
    WidgetRef ref,
    Object error,
    StackTrace? stackTrace,
    VoidCallback retry,
  )? errorBuilder;

  /// Callback when retry is pressed
  final VoidCallback? onRetry;

  const ConsumerErrorBoundary({
    super.key,
    required this.child,
    this.config = const ErrorBoundaryConfig(),
    this.onError,
    this.errorBuilder,
    this.onRetry,
  });

  @override
  ConsumerState<ConsumerErrorBoundary> createState() =>
      _ConsumerErrorBoundaryState();
}

class _ConsumerErrorBoundaryState extends ConsumerState<ConsumerErrorBoundary> {
  Object? _error;
  StackTrace? _stackTrace;

  void _handleError(Object error, StackTrace? stackTrace) {
    setState(() {
      _error = error;
      _stackTrace = stackTrace;
    });

    widget.onError?.call(error, stackTrace);

    if (widget.config.reportErrors) {
      ref.read(errorReporterProvider).reportError(
            error,
            stackTrace: stackTrace,
            severity: ReportSeverity.error,
            context: ErrorContext.current(
              screen: widget.config.screenName,
              widget: 'ConsumerErrorBoundary',
            ),
          );
    }
  }

  void _retry() {
    setState(() {
      _error = null;
      _stackTrace = null;
    });
    widget.onRetry?.call();
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      if (widget.errorBuilder != null) {
        return widget.errorBuilder!(
          context,
          ref,
          _error!,
          _stackTrace,
          _retry,
        );
      }

      return ErrorFallbackScreen(
        error: _error!,
        stackTrace: _stackTrace,
        onRetry: _retry,
        showDebugInfo: widget.config.showDebugInfo,
      );
    }

    return _ErrorCatcher(
      onError: _handleError,
      child: widget.child,
    );
  }
}

/// Error boundary for async operations (FutureBuilder, StreamBuilder)
class AsyncErrorBoundary<T> extends StatelessWidget {
  /// The async snapshot to handle
  final AsyncSnapshot<T> snapshot;

  /// Builder for successful data
  final Widget Function(T data) builder;

  /// Loading widget
  final Widget? loadingWidget;

  /// Error widget builder
  final Widget Function(Object error)? errorBuilder;

  /// Callback when retry is pressed
  final VoidCallback? onRetry;

  /// Whether to show debug info
  final bool showDebugInfo;

  const AsyncErrorBoundary({
    super.key,
    required this.snapshot,
    required this.builder,
    this.loadingWidget,
    this.errorBuilder,
    this.onRetry,
    this.showDebugInfo = false,
  });

  @override
  Widget build(BuildContext context) {
    // Loading state
    if (snapshot.connectionState == ConnectionState.waiting) {
      return loadingWidget ??
          const Center(
            child: CircularProgressIndicator(),
          );
    }

    // Error state
    if (snapshot.hasError) {
      if (errorBuilder != null) {
        return errorBuilder!(snapshot.error!);
      }

      return ErrorFallbackWidget(
        error: snapshot.error!,
        stackTrace: snapshot.stackTrace,
        onRetry: onRetry,
      );
    }

    // Data state
    if (snapshot.hasData) {
      return builder(snapshot.data as T);
    }

    // No data state
    return const SizedBox.shrink();
  }
}

/// Widget-level error boundary for wrapping individual widgets
class WidgetErrorBoundary extends StatefulWidget {
  /// The child widget to wrap
  final Widget child;

  /// Fallback widget to show on error
  final Widget? fallback;

  /// Callback when error occurs
  final void Function(Object error, StackTrace? stackTrace)? onError;

  const WidgetErrorBoundary({
    super.key,
    required this.child,
    this.fallback,
    this.onError,
  });

  @override
  State<WidgetErrorBoundary> createState() => _WidgetErrorBoundaryState();
}

class _WidgetErrorBoundaryState extends State<WidgetErrorBoundary> {
  bool _hasError = false;
  Object? _error;

  @override
  Widget build(BuildContext context) {
    if (_hasError) {
      return widget.fallback ??
          ErrorFallbackWidget(
            error: _error ?? Exception('Unknown error'),
            compact: true,
            onRetry: () {
              setState(() {
                _hasError = false;
                _error = null;
              });
            },
          );
    }

    return _ErrorCatcher(
      onError: (error, stackTrace) {
        setState(() {
          _hasError = true;
          _error = error;
        });
        widget.onError?.call(error, stackTrace);
      },
      child: widget.child,
    );
  }
}

/// Global error handler setup for main.dart
class GlobalErrorHandler {
  GlobalErrorHandler._();

  /// Initialize global error handling
  /// Call this in main() before runApp()
  static void initialize({
    void Function(Object error, StackTrace stackTrace)? onError,
    bool reportErrors = true,
  }) {
    // Handle Flutter framework errors
    FlutterError.onError = (FlutterErrorDetails details) {
      // Log to console
      FlutterError.presentError(details);

      // Call custom handler
      onError?.call(details.exception, details.stack ?? StackTrace.current);

      // Report to error reporter
      if (reportErrors) {
        errorReporter.reportFlutterError(details);
      }
    };

    // Handle errors outside of Flutter framework (async errors)
    PlatformDispatcher.instance.onError = (error, stackTrace) {
      debugPrint('Platform Error: $error');

      // Call custom handler
      onError?.call(error, stackTrace);

      // Report to error reporter
      if (reportErrors) {
        errorReporter.reportPlatformError(error, stackTrace);
      }

      // Return true to prevent the error from propagating
      return true;
    };

    debugPrint('Global error handling initialized');
  }
}

/// Extension methods for easy error boundary wrapping
extension ErrorBoundaryExtension on Widget {
  /// Wrap widget with error boundary
  Widget withErrorBoundary({
    ErrorBoundaryConfig config = const ErrorBoundaryConfig(),
    void Function(Object error, StackTrace? stackTrace)? onError,
    VoidCallback? onRetry,
  }) {
    return ErrorBoundary(
      config: config,
      onError: onError,
      onRetry: onRetry,
      child: this,
    );
  }

  /// Wrap widget with screen error boundary
  Widget withScreenErrorBoundary({
    required String screenName,
    void Function(Object error, StackTrace? stackTrace)? onError,
    VoidCallback? onRetry,
    VoidCallback? onGoBack,
  }) {
    return ErrorBoundary.screen(
      screenName: screenName,
      onError: onError,
      onRetry: onRetry,
      onGoBack: onGoBack,
      child: this,
    );
  }

  /// Wrap widget with widget-level error boundary
  Widget withWidgetErrorBoundary({
    Widget? fallback,
    void Function(Object error, StackTrace? stackTrace)? onError,
  }) {
    return WidgetErrorBoundary(
      fallback: fallback,
      onError: onError,
      child: this,
    );
  }
}
