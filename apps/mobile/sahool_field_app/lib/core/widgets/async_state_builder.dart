import 'package:flutter/material.dart';
import 'error_boundary.dart';
import 'loading_states.dart';
import 'empty_states.dart';

/// SAHOOL Async State Builder
/// بناء موحد لحالات التحميل والخطأ والبيانات الفارغة
///
/// Provides a consistent pattern for handling async data states across
/// all feature screens. Supports:
/// - Loading state with shimmer skeletons
/// - Error state with retry capability
/// - Empty state with action button
/// - Data state with builder
///
/// Usage:
/// ```dart
/// AsyncStateBuilder<List<Field>>(
///   isLoading: state.isLoading,
///   error: state.error,
///   data: state.fields,
///   isEmpty: (data) => data.isEmpty,
///   loadingBuilder: () => const SahoolShimmerList(),
///   errorBuilder: (error, retry) => SahoolErrorView(error: error, onRetry: retry),
///   emptyBuilder: () => const NoFieldsEmptyState(),
///   dataBuilder: (data) => FieldsList(fields: data),
///   onRetry: () => controller.loadFields(),
/// )
/// ```
class AsyncStateBuilder<T> extends StatelessWidget {
  /// Whether data is currently loading
  final bool isLoading;

  /// Error message if loading failed
  final String? error;

  /// The data to display
  final T? data;

  /// Whether data should be considered empty
  final bool Function(T data)? isEmpty;

  /// Builder for the loading state (default: SahoolShimmerList)
  final Widget Function()? loadingBuilder;

  /// Builder for the error state
  final Widget Function(String error, VoidCallback? retry)? errorBuilder;

  /// Builder for the empty state
  final Widget Function()? emptyBuilder;

  /// Builder for the data state (required)
  final Widget Function(T data) dataBuilder;

  /// Callback when retry is pressed in error state
  final VoidCallback? onRetry;

  /// Whether to show loading indicator over existing data during refresh
  final bool isRefreshing;

  /// Whether to wrap the widget in a SahoolErrorBoundary
  final bool wrapWithErrorBoundary;

  const AsyncStateBuilder({
    super.key,
    required this.isLoading,
    this.error,
    this.data,
    this.isEmpty,
    this.loadingBuilder,
    this.errorBuilder,
    this.emptyBuilder,
    required this.dataBuilder,
    this.onRetry,
    this.isRefreshing = false,
    this.wrapWithErrorBoundary = true,
  });

  @override
  Widget build(BuildContext context) {
    Widget child = _buildContent(context);

    if (wrapWithErrorBoundary) {
      child = SahoolErrorBoundary(
        onError: (error, stackTrace) {
          // Log error for debugging
          debugPrint('AsyncStateBuilder error: $error');
        },
        errorBuilder: (error, retry) {
          return SahoolErrorView(
            error: error,
            onRetry: retry,
          );
        },
        child: child,
      );
    }

    return child;
  }

  Widget _buildContent(BuildContext context) {
    // Error state (only when no data available)
    if (error != null && (data == null || _isDataEmpty)) {
      return errorBuilder?.call(error!, onRetry) ??
          SahoolErrorView(
            error: error!,
            onRetry: onRetry,
          );
    }

    // Initial loading state (no data yet)
    if (isLoading && (data == null || _isDataEmpty)) {
      return loadingBuilder?.call() ?? const SahoolShimmerList();
    }

    // Data available
    if (data != null && !_isDataEmpty) {
      // Show refresh indicator over data
      if (isRefreshing) {
        return Stack(
          children: [
            dataBuilder(data as T),
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: LinearProgressIndicator(
                backgroundColor: Color(0xFFE8F5E9),
                valueColor: AlwaysStoppedAnimation(Color(0xFF367C2B)),
              ),
            ),
          ],
        );
      }
      return dataBuilder(data as T);
    }

    // Empty state
    return emptyBuilder?.call() ?? const NoDataEmptyState();
  }

  bool get _isDataEmpty {
    if (data == null) return true;
    if (isEmpty != null) return isEmpty!(data as T);
    if (data is List) return (data as List).isEmpty;
    if (data is Map) return (data as Map).isEmpty;
    if (data is Iterable) return (data as Iterable).isEmpty;
    return false;
  }
}

/// AsyncStateSliver - Sliver variant for use in CustomScrollView
///
/// Same as AsyncStateBuilder but returns sliver-compatible widgets
class AsyncStateSliver<T> extends StatelessWidget {
  final bool isLoading;
  final String? error;
  final T? data;
  final bool Function(T data)? isEmpty;
  final Widget Function()? loadingBuilder;
  final Widget Function(String error, VoidCallback? retry)? errorBuilder;
  final Widget Function()? emptyBuilder;
  final Widget Function(T data) dataBuilder;
  final VoidCallback? onRetry;

  const AsyncStateSliver({
    super.key,
    required this.isLoading,
    this.error,
    this.data,
    this.isEmpty,
    this.loadingBuilder,
    this.errorBuilder,
    this.emptyBuilder,
    required this.dataBuilder,
    this.onRetry,
  });

  @override
  Widget build(BuildContext context) {
    final isDataEmpty = _isDataEmpty;

    // Error state
    if (error != null && (data == null || isDataEmpty)) {
      return SliverFillRemaining(
        child: errorBuilder?.call(error!, onRetry) ??
            SahoolErrorView(error: error!, onRetry: onRetry),
      );
    }

    // Loading state
    if (isLoading && (data == null || isDataEmpty)) {
      return SliverFillRemaining(
        child: loadingBuilder?.call() ?? const SahoolShimmerList(),
      );
    }

    // Data state
    if (data != null && !isDataEmpty) {
      return dataBuilder(data as T);
    }

    // Empty state
    return SliverFillRemaining(
      child: emptyBuilder?.call() ?? const NoDataEmptyState(),
    );
  }

  bool get _isDataEmpty {
    if (data == null) return true;
    if (isEmpty != null) return isEmpty!(data as T);
    if (data is List) return (data as List).isEmpty;
    return false;
  }
}
