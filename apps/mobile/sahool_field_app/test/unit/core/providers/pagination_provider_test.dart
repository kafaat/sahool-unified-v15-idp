import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/providers/pagination_provider.dart';

void main() {
  group('PaginatedListState', () {
    test('should have correct defaults', () {
      const state = PaginatedListState<String>();

      expect(state.items, isEmpty);
      expect(state.isLoading, false);
      expect(state.isLoadingMore, false);
      expect(state.isRefreshing, false);
      expect(state.error, isNull);
      expect(state.currentPage, 0);
      expect(state.pageSize, 20);
      expect(state.hasMore, true);
      expect(state.totalCount, isNull);
    });

    test('isBusy should return true when loading', () {
      const state = PaginatedListState<String>(isLoading: true);
      expect(state.isBusy, true);
    });

    test('isBusy should return true when loading more', () {
      const state = PaginatedListState<String>(isLoadingMore: true);
      expect(state.isBusy, true);
    });

    test('isBusy should return true when refreshing', () {
      const state = PaginatedListState<String>(isRefreshing: true);
      expect(state.isBusy, true);
    });

    test('isBusy should return false when idle', () {
      const state = PaginatedListState<String>();
      expect(state.isBusy, false);
    });

    test('hasData should return true when items exist', () {
      const state = PaginatedListState<String>(items: ['a', 'b']);
      expect(state.hasData, true);
    });

    test('hasData should return false when items empty', () {
      const state = PaginatedListState<String>();
      expect(state.hasData, false);
    });

    test('isEmpty should return true when empty and not loading', () {
      const state = PaginatedListState<String>();
      expect(state.isEmpty, true);
    });

    test('isEmpty should return false when loading', () {
      const state = PaginatedListState<String>(isLoading: true);
      expect(state.isEmpty, false);
    });

    test('isEmpty should return false when items exist', () {
      const state = PaginatedListState<String>(items: ['a']);
      expect(state.isEmpty, false);
    });

    test('copyWith should update specified fields', () {
      const original = PaginatedListState<String>(
        items: ['a'],
        isLoading: false,
        currentPage: 0,
      );

      final updated = original.copyWith(
        items: ['a', 'b'],
        isLoading: true,
        currentPage: 1,
      );

      expect(updated.items, ['a', 'b']);
      expect(updated.isLoading, true);
      expect(updated.currentPage, 1);
      // Unchanged fields
      expect(updated.isLoadingMore, false);
      expect(updated.hasMore, true);
    });

    test('copyWith with clearError should set error to null', () {
      const state = PaginatedListState<String>(error: 'some error');
      final cleared = state.copyWith(clearError: true);

      expect(cleared.error, isNull);
    });

    test('copyWith should preserve error when not clearing', () {
      const state = PaginatedListState<String>(error: 'some error');
      final updated = state.copyWith(isLoading: true);

      expect(updated.error, 'some error');
    });
  });

  group('PageResult', () {
    test('should store items and metadata', () {
      const result = PageResult<String>(
        items: ['a', 'b', 'c'],
        hasMore: true,
        totalCount: 100,
      );

      expect(result.items, ['a', 'b', 'c']);
      expect(result.hasMore, true);
      expect(result.totalCount, 100);
    });

    test('should default hasMore to true', () {
      const result = PageResult<String>(items: ['a']);
      expect(result.hasMore, true);
    });

    test('should default totalCount to null', () {
      const result = PageResult<String>(items: []);
      expect(result.totalCount, isNull);
    });
  });

  group('PaginatedListController', () {
    test('should auto-load initial page on creation', () async {
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          return PageResult<String>(
            items: List.generate(5, (i) => 'item_$i'),
            hasMore: true,
            totalCount: 50,
          );
        },
        pageSize: 5,
      );

      // Wait for async init
      await Future.delayed(const Duration(milliseconds: 50));

      expect(controller.state.items.length, 5);
      expect(controller.state.currentPage, 0);
      expect(controller.state.hasMore, true);
      expect(controller.state.totalCount, 50);
      expect(controller.state.isLoading, false);

      controller.dispose();
    });

    test('should handle initial load error', () async {
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          throw Exception('Network error');
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));

      expect(controller.state.items, isEmpty);
      expect(controller.state.error, contains('Network error'));
      expect(controller.state.isLoading, false);

      controller.dispose();
    });

    test('loadMore should append items', () async {
      int callCount = 0;
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          callCount++;
          return PageResult<String>(
            items: List.generate(5, (i) => 'page${page}_item$i'),
            hasMore: page < 2,
          );
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));
      expect(controller.state.items.length, 5);
      expect(callCount, 1);

      await controller.loadMore();
      expect(controller.state.items.length, 10);
      expect(controller.state.currentPage, 1);
      expect(callCount, 2);

      controller.dispose();
    });

    test('loadMore should not load when hasMore is false', () async {
      int callCount = 0;
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          callCount++;
          return PageResult<String>(
            items: List.generate(3, (i) => 'item_$i'),
            hasMore: false,
          );
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));
      expect(callCount, 1);

      await controller.loadMore();
      // Should not have called fetchPage again
      expect(callCount, 1);

      controller.dispose();
    });

    test('loadMore should not load when already loading more', () async {
      int callCount = 0;
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          callCount++;
          if (page > 0) {
            await Future.delayed(const Duration(milliseconds: 100));
          }
          return PageResult<String>(
            items: List.generate(5, (i) => 'item_$i'),
            hasMore: true,
          );
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));

      // Trigger two concurrent loadMore calls
      controller.loadMore();
      controller.loadMore();

      await Future.delayed(const Duration(milliseconds: 200));

      // Should only have called fetchPage twice (initial + one loadMore)
      expect(callCount, 2);

      controller.dispose();
    });

    test('refresh should reload from first page', () async {
      int callCount = 0;
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          callCount++;
          return PageResult<String>(
            items: List.generate(5, (i) => 'call${callCount}_item$i'),
            hasMore: true,
          );
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));
      expect(controller.state.items.first, 'call1_item0');

      // Load more first
      await controller.loadMore();
      expect(controller.state.items.length, 10);
      expect(controller.state.currentPage, 1);

      // Refresh should reset to page 0
      await controller.refresh();
      expect(controller.state.items.length, 5);
      expect(controller.state.currentPage, 0);
      expect(controller.state.items.first, 'call3_item0');

      controller.dispose();
    });

    test('refresh should handle errors', () async {
      bool shouldFail = false;
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          if (shouldFail) throw Exception('Refresh failed');
          return PageResult<String>(
            items: ['item'],
            hasMore: false,
          );
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));
      expect(controller.state.items, ['item']);

      shouldFail = true;
      await controller.refresh();

      expect(controller.state.error, contains('Refresh failed'));
      expect(controller.state.isRefreshing, false);
      // Items should still be there from before
      expect(controller.state.items, ['item']);

      controller.dispose();
    });

    test('clearError should remove error message', () async {
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          throw Exception('Error');
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));
      expect(controller.state.error, isNotNull);

      controller.clearError();
      expect(controller.state.error, isNull);

      controller.dispose();
    });

    test('hasMore should be false when page has fewer items than pageSize',
        () async {
      final controller = PaginatedListController<String>(
        fetchPage: (page, limit) async {
          return PageResult<String>(
            items: List.generate(3, (i) => 'item_$i'), // 3 < pageSize(5)
            hasMore:
                true, // Even if server says hasMore, controller detects short page
          );
        },
        pageSize: 5,
      );

      await Future.delayed(const Duration(milliseconds: 50));

      // Should be false because items.length (3) < pageSize (5)
      expect(controller.state.hasMore, false);

      controller.dispose();
    });
  });
}
