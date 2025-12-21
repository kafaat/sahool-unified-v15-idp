import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';
import '../utils/app_logger.dart';

/// SAHOOL Error Boundary Widget
/// معالج الأخطاء الموحد للتطبيق
///
/// Usage:
/// ```dart
/// SahoolErrorBoundary(
///   child: MyWidget(),
///   onError: (error, stack) => reportError(error, stack),
/// )
/// ```

class SahoolErrorBoundary extends StatefulWidget {
  final Widget child;
  final Widget Function(Object error, VoidCallback retry)? errorBuilder;
  final void Function(Object error, StackTrace? stackTrace)? onError;

  const SahoolErrorBoundary({
    super.key,
    required this.child,
    this.errorBuilder,
    this.onError,
  });

  @override
  State<SahoolErrorBoundary> createState() => _SahoolErrorBoundaryState();
}

class _SahoolErrorBoundaryState extends State<SahoolErrorBoundary> {
  Object? _error;
  StackTrace? _stackTrace;

  @override
  void initState() {
    super.initState();
  }

  void _handleError(Object error, StackTrace? stackTrace) {
    AppLogger.e(
      'Error caught by ErrorBoundary',
      error: error,
      stackTrace: stackTrace,
    );

    widget.onError?.call(error, stackTrace);

    if (mounted) {
      setState(() {
        _error = error;
        _stackTrace = stackTrace;
      });
    }
  }

  void _retry() {
    setState(() {
      _error = null;
      _stackTrace = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_error != null) {
      return widget.errorBuilder?.call(_error!, _retry) ??
          SahoolErrorView(
            error: _error!,
            onRetry: _retry,
          );
    }

    return _ErrorCatcher(
      onError: _handleError,
      child: widget.child,
    );
  }
}

/// Internal error catcher widget
class _ErrorCatcher extends StatefulWidget {
  final Widget child;
  final void Function(Object, StackTrace?) onError;

  const _ErrorCatcher({
    required this.child,
    required this.onError,
  });

  @override
  State<_ErrorCatcher> createState() => _ErrorCatcherState();
}

class _ErrorCatcherState extends State<_ErrorCatcher> {
  @override
  Widget build(BuildContext context) {
    // Override error widget builder
    ErrorWidget.builder = (FlutterErrorDetails details) {
      // Schedule error handling after build
      WidgetsBinding.instance.addPostFrameCallback((_) {
        widget.onError(details.exception, details.stack);
      });

      // Return empty container during transition
      return const SizedBox.shrink();
    };

    return widget.child;
  }
}

/// Standard Error View Widget
/// عرض خطأ قياسي
class SahoolErrorView extends StatelessWidget {
  final Object error;
  final VoidCallback? onRetry;
  final String? customMessage;
  final bool showDetails;

  const SahoolErrorView({
    super.key,
    required this.error,
    this.onRetry,
    this.customMessage,
    this.showDetails = false,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Error Icon
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: SahoolColors.danger.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(
                Icons.error_outline_rounded,
                size: 64,
                color: SahoolColors.danger,
              ),
            ),

            const SizedBox(height: 24),

            // Error Title
            Text(
              'حدث خطأ غير متوقع',
              style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                  ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 12),

            // Error Message
            Text(
              customMessage ?? _getErrorMessage(error),
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: SahoolColors.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),

            // Error Details (debug only)
            if (showDetails) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  error.toString(),
                  style: const TextStyle(
                    fontSize: 12,
                    fontFamily: 'monospace',
                    color: Colors.grey,
                  ),
                  textAlign: TextAlign.start,
                ),
              ),
            ],

            const SizedBox(height: 32),

            // Retry Button
            if (onRetry != null)
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  String _getErrorMessage(Object error) {
    final message = error.toString().toLowerCase();

    if (message.contains('network') || message.contains('connection')) {
      return 'تعذر الاتصال بالخادم. تحقق من اتصالك بالإنترنت.';
    }

    if (message.contains('timeout')) {
      return 'انتهت مهلة الاتصال. حاول مرة أخرى.';
    }

    if (message.contains('unauthorized') || message.contains('401')) {
      return 'جلستك منتهية. يرجى تسجيل الدخول مرة أخرى.';
    }

    if (message.contains('forbidden') || message.contains('403')) {
      return 'ليس لديك صلاحية للوصول لهذا المحتوى.';
    }

    if (message.contains('not found') || message.contains('404')) {
      return 'المحتوى المطلوب غير موجود.';
    }

    if (message.contains('server') || message.contains('500')) {
      return 'حدث خطأ في الخادم. حاول لاحقاً.';
    }

    return 'حدث خطأ غير متوقع. حاول مرة أخرى.';
  }
}

/// Inline Error Widget (for smaller spaces)
/// عرض خطأ مضغوط
class SahoolInlineError extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;

  const SahoolInlineError({
    super.key,
    required this.message,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.danger.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: SahoolColors.danger.withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          const Icon(
            Icons.warning_amber_rounded,
            color: SahoolColors.danger,
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              message,
              style: const TextStyle(
                color: SahoolColors.danger,
                fontSize: 14,
              ),
            ),
          ),
          if (onRetry != null)
            IconButton(
              onPressed: onRetry,
              icon: const Icon(
                Icons.refresh_rounded,
                color: SahoolColors.danger,
              ),
              tooltip: 'إعادة المحاولة',
            ),
        ],
      ),
    );
  }
}

/// Network Error Widget
/// عرض خطأ الشبكة
class SahoolNetworkError extends StatelessWidget {
  final VoidCallback? onRetry;

  const SahoolNetworkError({
    super.key,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.wifi_off_rounded,
              size: 80,
              color: Colors.grey[400],
            ),
            const SizedBox(height: 24),
            Text(
              'لا يوجد اتصال بالإنترنت',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),
            Text(
              'تحقق من اتصالك بالإنترنت وحاول مرة أخرى',
              style: TextStyle(color: Colors.grey[600]),
              textAlign: TextAlign.center,
            ),
            if (onRetry != null) ...[
              const SizedBox(height: 32),
              OutlinedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh_rounded),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
