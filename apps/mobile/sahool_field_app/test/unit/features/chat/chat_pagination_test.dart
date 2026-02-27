/// Chat Pagination Tests
/// اختبارات ترقيم صفحات المحادثات
///
/// Tests for chat pagination, deduplication, and loading state management

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/chat/presentation/providers/chat_provider.dart';

void main() {
  group('ChatState', () {
    test('should have default values for pagination fields', () {
      const state = ChatState();

      expect(state.isLoadingMore, isFalse);
      expect(state.hasMoreMessages, isTrue);
      expect(state.isLoading, isFalse);
      expect(state.conversations, isEmpty);
      expect(state.messagesMap, isEmpty);
    });

    test('copyWith should update isLoadingMore', () {
      const state = ChatState();
      final updated = state.copyWith(isLoadingMore: true);

      expect(updated.isLoadingMore, isTrue);
      expect(updated.hasMoreMessages, isTrue); // unchanged
    });

    test('copyWith should update hasMoreMessages', () {
      const state = ChatState();
      final updated = state.copyWith(hasMoreMessages: false);

      expect(updated.hasMoreMessages, isFalse);
      expect(updated.isLoadingMore, isFalse); // unchanged
    });

    test('copyWith should preserve other fields when updating pagination', () {
      const state = ChatState(
        isLoading: true,
        unreadCount: 5,
      );
      final updated = state.copyWith(
        isLoadingMore: true,
        hasMoreMessages: false,
      );

      expect(updated.isLoading, isTrue);
      expect(updated.unreadCount, 5);
      expect(updated.isLoadingMore, isTrue);
      expect(updated.hasMoreMessages, isFalse);
    });

    test('copyWith should not mutate original state', () {
      const original = ChatState(
        isLoadingMore: false,
        hasMoreMessages: true,
      );
      final copy = original.copyWith(
        isLoadingMore: true,
        hasMoreMessages: false,
      );

      expect(original.isLoadingMore, isFalse);
      expect(original.hasMoreMessages, isTrue);
      expect(copy.isLoadingMore, isTrue);
      expect(copy.hasMoreMessages, isFalse);
    });

    test('copyWith with no args should return equivalent state', () {
      const state = ChatState(
        isLoadingMore: true,
        hasMoreMessages: false,
        unreadCount: 3,
      );
      final copy = state.copyWith();

      expect(copy.isLoadingMore, state.isLoadingMore);
      expect(copy.hasMoreMessages, state.hasMoreMessages);
      expect(copy.unreadCount, state.unreadCount);
    });
  });
}
