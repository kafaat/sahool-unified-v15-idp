import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';

/// SAHOOL Pagination Provider
/// مزود التحميل الصفحي الموحد
///
/// Generic pagination state and controller for use with Riverpod.
/// Supports infinite scroll, pull-to-refresh, and error recovery.
///
/// Usage:
/// ```dart
/// final paginatedFieldsProvider = StateNotifierProvider<
///     PaginatedListController<Field>, PaginatedListState<Field>>((ref) {
///   return PaginatedListController(
///     fetchPage: (page, limit) async {
///       return await repo.getFields(page: page, limit: limit);
///     },
///   );
/// });
/// ```

/// Pagination state holding items, loading status, and page info
class PaginatedListState<T> {
  /// The list of items loaded so far
  final List<T> items;

  /// Whether the initial load is in progress
  final bool isLoading;

  /// Whether more items are being loaded
  final bool isLoadingMore;

  /// Whether a refresh is in progress
  final bool isRefreshing;

  /// Error message if any
  final String? error;

  /// Current page number (0-indexed)
  final int currentPage;

  /// Number of items per page
  final int pageSize;

  /// Whether there are more items to load
  final bool hasMore;

  /// Total count of items (if known from server)
  final int? totalCount;

  const PaginatedListState({
    this.items = const [],
    this.isLoading = false,
    this.isLoadingMore = false,
    this.isRefreshing = false,
    this.error,
    this.currentPage = 0,
    this.pageSize = 20,
    this.hasMore = true,
    this.totalCount,
  });

  PaginatedListState<T> copyWith({
    List<T>? items,
    bool? isLoading,
    bool? isLoadingMore,
    bool? isRefreshing,
    String? error,
    int? currentPage,
    int? pageSize,
    bool? hasMore,
    int? totalCount,
    bool clearError = false,
  }) {
    return PaginatedListState<T>(
      items: items ?? this.items,
      isLoading: isLoading ?? this.isLoading,
      isLoadingMore: isLoadingMore ?? this.isLoadingMore,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      error: clearError ? null : (error ?? this.error),
      currentPage: currentPage ?? this.currentPage,
      pageSize: pageSize ?? this.pageSize,
      hasMore: hasMore ?? this.hasMore,
      totalCount: totalCount ?? this.totalCount,
    );
  }

  /// Check if any operation is in progress
  bool get isBusy => isLoading || isLoadingMore || isRefreshing;

  /// Whether data is available
  bool get hasData => items.isNotEmpty;

  /// Whether the list is empty and not loading
  bool get isEmpty => items.isEmpty && !isLoading;
}

/// Result from a page fetch operation
class PageResult<T> {
  final List<T> items;
  final bool hasMore;
  final int? totalCount;

  const PageResult({
    required this.items,
    this.hasMore = true,
    this.totalCount,
  });
}

/// Generic paginated list controller
class PaginatedListController<T> extends StateNotifier<PaginatedListState<T>> {
  /// Function to fetch a page of items
  final Future<PageResult<T>> Function(int page, int limit) fetchPage;

  /// Number of items per page
  final int pageSize;

  PaginatedListController({
    required this.fetchPage,
    this.pageSize = 20,
  }) : super(PaginatedListState<T>(pageSize: pageSize)) {
    loadInitial();
  }

  /// Load the first page
  Future<void> loadInitial() async {
    if (state.isLoading) return;

    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final result = await fetchPage(0, pageSize);

      state = state.copyWith(
        isLoading: false,
        items: result.items,
        currentPage: 0,
        hasMore: result.hasMore && result.items.length >= pageSize,
        totalCount: result.totalCount,
      );

      AppLogger.d(
        'Initial page loaded: ${result.items.length} items',
        tag: 'PAGINATION',
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      AppLogger.e('Failed to load initial page', tag: 'PAGINATION', error: e);
    }
  }

  /// Load the next page (called on scroll)
  Future<void> loadMore() async {
    if (!state.hasMore || state.isLoadingMore || state.isLoading) return;

    state = state.copyWith(isLoadingMore: true);

    try {
      final nextPage = state.currentPage + 1;
      final result = await fetchPage(nextPage, pageSize);

      state = state.copyWith(
        isLoadingMore: false,
        items: [...state.items, ...result.items],
        currentPage: nextPage,
        hasMore: result.hasMore && result.items.length >= pageSize,
        totalCount: result.totalCount,
      );

      AppLogger.d(
        'Page $nextPage loaded: ${result.items.length} items, total: ${state.items.length}',
        tag: 'PAGINATION',
      );
    } catch (e) {
      state = state.copyWith(
        isLoadingMore: false,
        error: e.toString(),
      );
      AppLogger.e('Failed to load more items', tag: 'PAGINATION', error: e);
    }
  }

  /// Refresh the list (reload from first page)
  Future<void> refresh() async {
    if (state.isRefreshing) return;

    state = state.copyWith(isRefreshing: true, clearError: true);

    try {
      final result = await fetchPage(0, pageSize);

      state = state.copyWith(
        isRefreshing: false,
        items: result.items,
        currentPage: 0,
        hasMore: result.hasMore && result.items.length >= pageSize,
        totalCount: result.totalCount,
      );

      AppLogger.d(
        'Refreshed: ${result.items.length} items',
        tag: 'PAGINATION',
      );
    } catch (e) {
      state = state.copyWith(
        isRefreshing: false,
        error: e.toString(),
      );
      AppLogger.e('Failed to refresh', tag: 'PAGINATION', error: e);
    }
  }

  /// Clear error state
  void clearError() {
    state = state.copyWith(clearError: true);
  }
}
