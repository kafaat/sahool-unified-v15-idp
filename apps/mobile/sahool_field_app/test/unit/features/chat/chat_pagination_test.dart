/// Chat Pagination Tests
/// اختبارات ترقيم صفحات المحادثات
///
/// Tests for chat state management including loading state, unread count,
/// and state immutability via copyWith

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/chat/presentation/providers/chat_provider.dart';

void main() {
  group('ChatState', () {
    test('should have default values', () {
      const state = ChatState();

      expect(state.isLoading, isFalse);
      expect(state.unreadCount, 0);
      expect(state.conversations, isEmpty);
      expect(state.messagesMap, isEmpty);
      expect(state.activeConversationId, isNull);
      expect(state.error, isNull);
    });

    test('copyWith should update isLoading', () {
      const state = ChatState();
      final updated = state.copyWith(isLoading: true);

      expect(updated.isLoading, isTrue);
      expect(updated.unreadCount, 0); // unchanged
    });

    test('copyWith should update unreadCount', () {
      const state = ChatState();
      final updated = state.copyWith(unreadCount: 5);

      expect(updated.unreadCount, 5);
      expect(updated.isLoading, isFalse); // unchanged
    });

    test('copyWith should preserve other fields when updating', () {
      const state = ChatState(
        isLoading: true,
        unreadCount: 5,
      );
      final updated = state.copyWith(
        error: 'test error',
      );

      expect(updated.isLoading, isTrue);
      expect(updated.unreadCount, 5);
      expect(updated.error, 'test error');
    });

    test('copyWith should not mutate original state', () {
      const original = ChatState(
        isLoading: false,
        unreadCount: 0,
      );
      final copy = original.copyWith(
        isLoading: true,
        unreadCount: 10,
      );

      expect(original.isLoading, isFalse);
      expect(original.unreadCount, 0);
      expect(copy.isLoading, isTrue);
      expect(copy.unreadCount, 10);
    });

    test('copyWith with no args should return equivalent state', () {
      const state = ChatState(
        isLoading: true,
        unreadCount: 3,
      );
      final copy = state.copyWith();

      expect(copy.isLoading, state.isLoading);
      expect(copy.unreadCount, state.unreadCount);
      expect(copy.error, state.error);
    });
  });
}
