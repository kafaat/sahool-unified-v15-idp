/// Chat Provider
/// مزود المحادثات - إدارة الحالة باستخدام Riverpod
///
/// Features:
/// - Conversations list management
/// - Messages management
/// - Real-time updates via WebSocket
/// - Typing indicators
/// - Online status

import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/api_config.dart';
import '../../data/models/conversation_model.dart';
import '../../data/models/message_model.dart';
import '../../data/remote/chat_api.dart';
import '../../data/repositories/chat_repository.dart';

// =============================================================================
// State Classes
// =============================================================================

/// Chat State
class ChatState {
  final List<Conversation> conversations;
  final Map<String, List<Message>> messagesMap;
  final String? activeConversationId;
  final Map<String, bool> typingStatus;
  final int unreadCount;
  final bool isLoading;
  final String? error;

  const ChatState({
    this.conversations = const [],
    this.messagesMap = const {},
    this.activeConversationId,
    this.typingStatus = const {},
    this.unreadCount = 0,
    this.isLoading = false,
    this.error,
  });

  ChatState copyWith({
    List<Conversation>? conversations,
    Map<String, List<Message>>? messagesMap,
    String? activeConversationId,
    bool clearActiveConversation = false,
    Map<String, bool>? typingStatus,
    int? unreadCount,
    bool? isLoading,
    String? error,
    bool clearError = false,
  }) {
    return ChatState(
      conversations: conversations ?? this.conversations,
      messagesMap: messagesMap ?? this.messagesMap,
      activeConversationId: clearActiveConversation
          ? null
          : (activeConversationId ?? this.activeConversationId),
      typingStatus: typingStatus ?? this.typingStatus,
      unreadCount: unreadCount ?? this.unreadCount,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
    );
  }

  /// Get messages for active conversation
  List<Message> get activeMessages {
    if (activeConversationId == null) return [];
    return messagesMap[activeConversationId] ?? [];
  }

  /// Get active conversation
  Conversation? get activeConversation {
    if (activeConversationId == null) return null;
    try {
      return conversations.firstWhere((c) => c.id == activeConversationId);
    } catch (_) {
      return null;
    }
  }
}

// =============================================================================
// Notifier
// =============================================================================

/// Chat Notifier
class ChatNotifier extends StateNotifier<ChatState> {
  final ChatRepository _repository;
  final String _currentUserId;
  StreamSubscription? _messageSubscription;
  StreamSubscription? _typingSubscription;
  StreamSubscription? _onlineStatusSubscription;

  ChatNotifier({
    required ChatRepository repository,
    required String currentUserId,
  })  : _repository = repository,
        _currentUserId = currentUserId,
        super(const ChatState()) {
    _initialize();
  }

  /// Initialize
  void _initialize() {
    // Connect to WebSocket
    _repository.connect();

    // Listen to real-time events
    _setupListeners();

    // Load initial data
    loadConversations();
    loadUnreadCount();
  }

  /// Setup real-time listeners
  void _setupListeners() {
    // Listen for new messages
    _messageSubscription = _repository.messageStream.listen(
      (message) {
        _handleNewMessage(message);
      },
      onError: (error) {
        state = state.copyWith(
          error: 'خطأ في استقبال الرسائل: ${error.toString()}',
        );
      },
    );

    // Listen for typing indicators
    _typingSubscription = _repository.typingStream.listen(
      (data) {
        final conversationId = data['conversationId'] as String?;
        final isTyping = data['isTyping'] as bool? ?? true;

        if (conversationId != null) {
          _updateTypingStatus(conversationId, isTyping);
        }
      },
      onError: (error) {
        // Silent fail for typing indicators
      },
    );

    // Listen for online status updates
    _onlineStatusSubscription = _repository.onlineStatusStream.listen(
      (data) {
        final userId = data['userId'] as String?;
        final isOnline = data['isOnline'] as bool? ?? false;

        if (userId != null) {
          _repository.updateOnlineStatus(userId, isOnline);
          // Trigger state update to refresh UI
          state = state.copyWith(conversations: [...state.conversations]);
        }
      },
      onError: (error) {
        // Silent fail for online status updates
      },
    );
  }

  // ───────────────────────────────────────────────────────────────────────────
  // Conversations
  // ───────────────────────────────────────────────────────────────────────────

  /// Load conversations
  Future<void> loadConversations({bool forceRefresh = false}) async {
    if (!forceRefresh && state.conversations.isNotEmpty) return;

    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final conversations = await _repository.getConversations(
        forceRefresh: forceRefresh,
      );

      state = state.copyWith(
        conversations: conversations,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل المحادثات: ${e.toString()}',
      );
    }
  }

  /// Refresh conversations (pull to refresh)
  Future<void> refreshConversations() async {
    await loadConversations(forceRefresh: true);
  }

  /// Create a new conversation
  Future<Conversation?> createConversation({
    required String participantId,
    String? productId,
    String? orderId,
    String? initialMessage,
  }) async {
    try {
      final conversation = await _repository.createConversation(
        participantId: participantId,
        productId: productId,
        orderId: orderId,
        initialMessage: initialMessage,
      );

      // Add to state
      state = state.copyWith(
        conversations: [conversation, ...state.conversations],
      );

      return conversation;
    } catch (e) {
      state = state.copyWith(
        error: 'فشل في إنشاء المحادثة: ${e.toString()}',
      );
      return null;
    }
  }

  /// Mark conversation as read
  Future<void> markAsRead(String conversationId) async {
    try {
      await _repository.markAsRead(conversationId);

      // Update state
      final updatedConversations = state.conversations.map((c) {
        if (c.id == conversationId) {
          return c.copyWith(unreadCount: 0);
        }
        return c;
      }).toList();

      state = state.copyWith(conversations: updatedConversations);

      // Reload unread count
      loadUnreadCount();
    } catch (e) {
      // Silent fail
    }
  }

  /// Load unread count
  Future<void> loadUnreadCount() async {
    try {
      final count = await _repository.getUnreadCount();
      state = state.copyWith(unreadCount: count);
    } catch (e) {
      // Silent fail
    }
  }

  // ───────────────────────────────────────────────────────────────────────────
  // Messages
  // ───────────────────────────────────────────────────────────────────────────

  /// Open conversation (set as active and load messages)
  Future<void> openConversation(String conversationId) async {
    state = state.copyWith(
      activeConversationId: conversationId,
      isLoading: true,
      clearError: true,
    );

    try {
      // Join conversation room for real-time updates
      _repository.joinConversation(conversationId);

      // Load messages
      final messages = await _repository.getMessages(conversationId);

      // Update state
      final updatedMessagesMap = {...state.messagesMap};
      updatedMessagesMap[conversationId] = messages;

      state = state.copyWith(
        messagesMap: updatedMessagesMap,
        isLoading: false,
      );

      // Mark as read
      markAsRead(conversationId);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل في تحميل الرسائل: ${e.toString()}',
      );
    }
  }

  /// Close conversation
  void closeConversation() {
    if (state.activeConversationId != null) {
      _repository.leaveConversation(state.activeConversationId!);
    }

    state = state.copyWith(clearActiveConversation: true);
  }

  /// Load more messages (pagination)
  Future<void> loadMoreMessages(String conversationId) async {
    final existingMessages = state.messagesMap[conversationId] ?? [];
    if (existingMessages.isEmpty) return;

    final oldestMessage = existingMessages.last;

    try {
      final messages = await _repository.getMessages(
        conversationId,
        before: oldestMessage.id,
        limit: 20,
      );

      if (messages.isNotEmpty) {
        final updatedMessagesMap = {...state.messagesMap};
        updatedMessagesMap[conversationId] = [
          ...existingMessages,
          ...messages,
        ];

        state = state.copyWith(messagesMap: updatedMessagesMap);
      }
    } catch (e) {
      // Silent fail
    }
  }

  /// Send message
  Future<void> sendMessage(
    String conversationId, {
    required String content,
    MessageType type = MessageType.text,
    String? attachmentUrl,
    Map<String, dynamic>? metadata,
  }) async {
    if (content.trim().isEmpty && type == MessageType.text) return;

    try {
      // Create optimistic message
      final tempId = 'temp_${DateTime.now().millisecondsSinceEpoch}';
      final optimisticMessage = Message(
        id: tempId,
        conversationId: conversationId,
        senderId: _currentUserId,
        type: type,
        content: content,
        attachmentUrl: attachmentUrl,
        metadata: metadata,
        status: MessageStatus.sending,
        createdAt: DateTime.now(),
        isMine: true,
      );

      // Add to state immediately
      final updatedMessagesMap = {...state.messagesMap};
      final existingMessages = updatedMessagesMap[conversationId] ?? [];
      updatedMessagesMap[conversationId] = [optimisticMessage, ...existingMessages];

      state = state.copyWith(messagesMap: updatedMessagesMap);

      // Send to server
      final sentMessage = await _repository.sendMessage(
        conversationId,
        content: content,
        type: type,
        attachmentUrl: attachmentUrl,
        metadata: metadata,
      );

      // Replace optimistic message with real one
      final finalMessagesMap = {...state.messagesMap};
      final messages = finalMessagesMap[conversationId] ?? [];
      final index = messages.indexWhere((m) => m.id == tempId);

      if (index != -1) {
        messages[index] = sentMessage;
        finalMessagesMap[conversationId] = messages;
        state = state.copyWith(messagesMap: finalMessagesMap);
      }
    } catch (e) {
      // Mark message as failed
      final updatedMessagesMap = {...state.messagesMap};
      final messages = updatedMessagesMap[conversationId] ?? [];
      final failedMessages = messages.map((m) {
        if (m.status == MessageStatus.sending) {
          return m.copyWith(status: MessageStatus.failed);
        }
        return m;
      }).toList();

      updatedMessagesMap[conversationId] = failedMessages;
      state = state.copyWith(messagesMap: updatedMessagesMap);
    }
  }

  /// Handle new message from WebSocket
  void _handleNewMessage(Message message) {
    // Add to repository cache
    _repository.addMessageToCache(message);

    // Update state
    final updatedMessagesMap = {...state.messagesMap};
    final conversationMessages = updatedMessagesMap[message.conversationId] ?? [];

    // Check if message already exists
    final exists = conversationMessages.any((m) => m.id == message.id);
    if (!exists) {
      updatedMessagesMap[message.conversationId] = [message, ...conversationMessages];
    }

    // Update conversations list
    final updatedConversations = state.conversations.map((c) {
      if (c.id == message.conversationId) {
        return c.copyWith(
          lastMessage: message,
          updatedAt: DateTime.now(),
          unreadCount: message.isMine ? c.unreadCount : c.unreadCount + 1,
        );
      }
      return c;
    }).toList()
      ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));

    state = state.copyWith(
      messagesMap: updatedMessagesMap,
      conversations: updatedConversations,
    );

    // Reload unread count if message is not from current user
    if (!message.isMine) {
      loadUnreadCount();
    }
  }

  // ───────────────────────────────────────────────────────────────────────────
  // Typing Indicators
  // ───────────────────────────────────────────────────────────────────────────

  /// Send typing indicator
  void sendTyping(String conversationId, {required bool isTyping}) {
    _repository.sendTypingIndicator(conversationId, isTyping: isTyping);
  }

  /// Update typing status
  void _updateTypingStatus(String conversationId, bool isTyping) {
    _repository.updateTypingStatus(conversationId, isTyping);

    final updatedTypingStatus = {...state.typingStatus};
    updatedTypingStatus[conversationId] = isTyping;

    // Update conversation
    final updatedConversations = state.conversations.map((c) {
      if (c.id == conversationId) {
        return c.copyWith(isTyping: isTyping);
      }
      return c;
    }).toList();

    state = state.copyWith(
      typingStatus: updatedTypingStatus,
      conversations: updatedConversations,
    );
  }

  // ───────────────────────────────────────────────────────────────────────────
  // Cleanup
  // ───────────────────────────────────────────────────────────────────────────

  @override
  void dispose() {
    _messageSubscription?.cancel();
    _typingSubscription?.cancel();
    _onlineStatusSubscription?.cancel();
    _repository.dispose();
    super.dispose();
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// Current user ID provider
final chatUserIdProvider = StateProvider<String>((ref) => '');

/// Chat API provider
final chatApiProvider = Provider<ChatApi>((ref) {
  final userId = ref.watch(chatUserIdProvider);
  return ChatApi(
    baseUrl: ApiConfig.chatServiceUrl,
    currentUserId: userId,
  );
});

/// Chat repository provider
final chatRepositoryProvider = Provider<ChatRepository>((ref) {
  final api = ref.watch(chatApiProvider);
  return ChatRepository(api);
});

/// Chat notifier provider
final chatProvider = StateNotifierProvider<ChatNotifier, ChatState>((ref) {
  final repository = ref.watch(chatRepositoryProvider);
  final userId = ref.watch(chatUserIdProvider);

  return ChatNotifier(
    repository: repository,
    currentUserId: userId,
  );
});

/// Unread count provider
final unreadCountProvider = Provider<int>((ref) {
  return ref.watch(chatProvider).unreadCount;
});

/// Active conversation provider
final activeConversationProvider = Provider<Conversation?>((ref) {
  return ref.watch(chatProvider).activeConversation;
});

/// Active messages provider
final activeMessagesProvider = Provider<List<Message>>((ref) {
  return ref.watch(chatProvider).activeMessages;
});

/// Typing status for active conversation
final activeConversationTypingProvider = Provider<bool>((ref) {
  final state = ref.watch(chatProvider);
  if (state.activeConversationId == null) return false;
  return state.typingStatus[state.activeConversationId] ?? false;
});
