import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';

/// SAHOOL Error Boundary Widget
///
/// Catches errors in the widget tree and displays a user-friendly error UI
/// instead of crashing the app.
///
/// Usage:
/// ```dart
/// ErrorBoundary(
///   child: MyWidget(),
///   onError: (error, stackTrace) => logError(error, stackTrace),
/// )
/// ```
class ErrorBoundary extends StatefulWidget {
  /// The child widget to wrap
  final Widget child;

  /// Optional callback when an error occurs
  final void Function(Object error, StackTrace? stackTrace)? onError;

  /// Custom error widget builder
  final Widget Function(Object error, VoidCallback retry)? errorBuilder;

  /// Whether to show detailed error in debug mode
  final bool showDebugInfo;

  const ErrorBoundary({
    super.key,
    required this.child,
    this.onError,
    this.errorBuilder,
    this.showDebugInfo = true,
  });

  @override
  State<ErrorBoundary> createState() => _ErrorBoundaryState();
}

class _ErrorBoundaryState extends State<ErrorBoundary> {
  Object? _error;
  StackTrace? _stackTrace;

  @override
  void initState() {
    super.initState();
    // Set up Flutter error handler
    FlutterError.onError = _handleFlutterError;
  }

  void _handleFlutterError(FlutterErrorDetails details) {
    if (mounted) {
      setState(() {
        _error = details.exception;
        _stackTrace = details.stack;
      });
      widget.onError?.call(details.exception, details.stack);
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
      if (widget.errorBuilder != null) {
        return widget.errorBuilder!(_error!, _retry);
      }
      return _DefaultErrorWidget(
        error: _error!,
        stackTrace: _stackTrace,
        onRetry: _retry,
        showDebugInfo: widget.showDebugInfo && kDebugMode,
      );
    }

    return widget.child;
  }
}

/// Default error widget with Arabic/English support
class _DefaultErrorWidget extends StatelessWidget {
  final Object error;
  final StackTrace? stackTrace;
  final VoidCallback onRetry;
  final bool showDebugInfo;

  const _DefaultErrorWidget({
    required this.error,
    this.stackTrace,
    required this.onRetry,
    this.showDebugInfo = false,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return Container(
      color: theme.scaffoldBackgroundColor,
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // Error icon
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: Colors.red.shade50,
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  Icons.error_outline,
                  size: 48,
                  color: Colors.red.shade400,
                ),
              ),
              const SizedBox(height: 24),

              // Error title
              Text(
                isRtl ? 'حدث خطأ غير متوقع' : 'Something went wrong',
                style: theme.textTheme.headlineSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 12),

              // Error description
              Text(
                isRtl
                    ? 'نعتذر عن هذا الخطأ. يرجى المحاولة مرة أخرى.'
                    : 'We apologize for this error. Please try again.',
                style: theme.textTheme.bodyLarge?.copyWith(
                  color: Colors.grey.shade600,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 32),

              // Retry button
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text(isRtl ? 'إعادة المحاولة' : 'Try Again'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: theme.primaryColor,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Report button
              TextButton.icon(
                onPressed: () => _showErrorDetails(context),
                icon: const Icon(Icons.bug_report_outlined, size: 18),
                label: Text(
                  isRtl ? 'عرض التفاصيل' : 'View Details',
                  style: TextStyle(color: Colors.grey.shade600),
                ),
              ),

              // Debug info
              if (showDebugInfo) ...[
                const SizedBox(height: 24),
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Debug Info:',
                        style: theme.textTheme.labelSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        error.toString(),
                        style: theme.textTheme.bodySmall?.copyWith(
                          fontFamily: 'monospace',
                          fontSize: 10,
                        ),
                        maxLines: 5,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  void _showErrorDetails(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.3,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) => Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Handle
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Title
              Text(
                'Error Details',
                style: Theme.of(context).textTheme.titleLarge,
              ),
              const SizedBox(height: 16),

              // Error type
              _DetailRow(label: 'Type', value: error.runtimeType.toString()),
              const SizedBox(height: 8),

              // Error message
              _DetailRow(label: 'Message', value: error.toString()),
              const SizedBox(height: 16),

              // Stack trace
              Text(
                'Stack Trace:',
                style: Theme.of(context).textTheme.titleSmall,
              ),
              const SizedBox(height: 8),
              Expanded(
                child: Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.grey.shade100,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: SingleChildScrollView(
                    controller: scrollController,
                    child: Text(
                      stackTrace?.toString() ?? 'No stack trace available',
                      style: const TextStyle(
                        fontFamily: 'monospace',
                        fontSize: 11,
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Copy button
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: () {
                    // Copy to clipboard
                    final text =
                        'Error: $error\n\nStack Trace:\n$stackTrace';
                    // Clipboard.setData(ClipboardData(text: text));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('Error details copied')),
                    );
                  },
                  icon: const Icon(Icons.copy),
                  label: const Text('Copy Error Details'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final String label;
  final String value;

  const _DetailRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 80,
          child: Text(
            '$label:',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        Expanded(
          child: Text(value),
        ),
      ],
    );
  }
}

/// Global error handler setup
///
/// Call this in main() before runApp()
void setupGlobalErrorHandling({
  void Function(Object error, StackTrace stackTrace)? onError,
}) {
  // Handle Flutter framework errors
  FlutterError.onError = (FlutterErrorDetails details) {
    FlutterError.presentError(details);
    onError?.call(details.exception, details.stack ?? StackTrace.current);
  };

  // Handle errors outside of Flutter framework
  PlatformDispatcher.instance.onError = (error, stack) {
    debugPrint('Platform Error: $error');
    onError?.call(error, stack);
    return true;
  };
}

/// Async error boundary for FutureBuilder/StreamBuilder
class AsyncErrorBoundary extends StatelessWidget {
  final AsyncSnapshot snapshot;
  final Widget Function() builder;
  final Widget? loadingWidget;
  final Widget Function(Object error)? errorBuilder;

  const AsyncErrorBoundary({
    super.key,
    required this.snapshot,
    required this.builder,
    this.loadingWidget,
    this.errorBuilder,
  });

  @override
  Widget build(BuildContext context) {
    if (snapshot.connectionState == ConnectionState.waiting) {
      return loadingWidget ??
          const Center(child: CircularProgressIndicator());
    }

    if (snapshot.hasError) {
      return errorBuilder?.call(snapshot.error!) ??
          _DefaultErrorWidget(
            error: snapshot.error!,
            onRetry: () {},
            showDebugInfo: kDebugMode,
          );
    }

    return builder();
  }
}
