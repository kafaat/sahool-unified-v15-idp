/// Chat Repository
/// مستودع المحادثات
///
/// Handles data operations and caching for chat feature

import 'dart:async';
import '../models/conversation_model.dart';
import '../models/message_model.dart';
import '../remote/chat_api.dart';

/// Chat Repository
class ChatRepository {
  final ChatApi _api;

  // Local cache
  final Map<String, Conversation> _conversationsCache = {};
  final Map<String, List<Message>> _messagesCache = {};

  ChatRepository(this._api);

  // ─────────────────────────────────────────────────────────────────────────────
  // Conversations
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get all conversations
  Future<List<Conversation>> getConversations({bool forceRefresh = false}) async {
    if (!forceRefresh && _conversationsCache.isNotEmpty) {
      return _conversationsCache.values.toList()
        ..sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    }

    final conversations = await _api.getConversations();

    // Update cache
    _conversationsCache.clear();
    for (var conversation in conversations) {
      _conversationsCache[conversation.id] = conversation;
    }

    return conversations;
  }

  /// Get conversation by ID
  Future<Conversation> getConversation(String conversationId) async {
    // Try cache first
    if (_conversationsCache.containsKey(conversationId)) {
      return _conversationsCache[conversationId]!;
    }

    final conversation = await _api.getConversation(conversationId);
    _conversationsCache[conversationId] = conversation;
    return conversation;
  }

  /// Create a new conversation
  Future<Conversation> createConversation({
    required String participantId,
    String? productId,
    String? orderId,
    String? initialMessage,
  }) async {
    final conversation = await _api.createConversation(
      participantId: participantId,
      productId: productId,
      orderId: orderId,
      initialMessage: initialMessage,
    );

    // Add to cache
    _conversationsCache[conversation.id] = conversation;

    return conversation;
  }

  /// Update conversation in cache
  void updateConversationInCache(Conversation conversation) {
    _conversationsCache[conversation.id] = conversation;
  }

  /// Mark conversation as read
  Future<void> markAsRead(String conversationId) async {
    await _api.markAsRead(conversationId);

    // Update cache
    if (_conversationsCache.containsKey(conversationId)) {
      final conversation = _conversationsCache[conversationId]!;
      _conversationsCache[conversationId] = conversation.copyWith(unreadCount: 0);
    }
  }

  /// Get unread count
  Future<int> getUnreadCount() async {
    return await _api.getUnreadCount();
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Messages
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get messages for a conversation
  Future<List<Message>> getMessages(
    String conversationId, {
    int? limit,
    String? before,
    bool forceRefresh = false,
  }) async {
    final cacheKey = conversationId;

    // Return cached messages if available and not forcing refresh
    if (!forceRefresh &&
        _messagesCache.containsKey(cacheKey) &&
        before == null) {
      return _messagesCache[cacheKey]!;
    }

    final messages = await _api.getMessages(
      conversationId,
      limit: limit,
      before: before,
    );

    // Update cache (only if not paginating)
    if (before == null) {
      _messagesCache[cacheKey] = messages;
    } else {
      // Append to existing cache
      if (_messagesCache.containsKey(cacheKey)) {
        _messagesCache[cacheKey] = [..._messagesCache[cacheKey]!, ...messages];
      } else {
        _messagesCache[cacheKey] = messages;
      }
    }

    return messages;
  }

  /// Send a message
  Future<Message> sendMessage(
    String conversationId, {
    required String content,
    MessageType type = MessageType.text,
    String? attachmentUrl,
    Map<String, dynamic>? metadata,
  }) async {
    final message = await _api.sendMessage(
      conversationId,
      content: content,
      type: type,
      attachmentUrl: attachmentUrl,
      metadata: metadata,
    );

    // Add to cache
    final cacheKey = conversationId;
    if (_messagesCache.containsKey(cacheKey)) {
      _messagesCache[cacheKey] = [message, ..._messagesCache[cacheKey]!];
    } else {
      _messagesCache[cacheKey] = [message];
    }

    // Update conversation's last message in cache
    if (_conversationsCache.containsKey(conversationId)) {
      final conversation = _conversationsCache[conversationId]!;
      _conversationsCache[conversationId] = conversation.copyWith(
        lastMessage: message,
        updatedAt: DateTime.now(),
      );
    }

    return message;
  }

  /// Add message to cache (from real-time update)
  void addMessageToCache(Message message) {
    final cacheKey = message.conversationId;

    if (_messagesCache.containsKey(cacheKey)) {
      // Check if message already exists
      final exists = _messagesCache[cacheKey]!.any((m) => m.id == message.id);
      if (!exists) {
        _messagesCache[cacheKey] = [message, ..._messagesCache[cacheKey]!];
      }
    } else {
      _messagesCache[cacheKey] = [message];
    }

    // Update conversation's last message in cache
    if (_conversationsCache.containsKey(message.conversationId)) {
      final conversation = _conversationsCache[message.conversationId]!;
      _conversationsCache[message.conversationId] = conversation.copyWith(
        lastMessage: message,
        updatedAt: DateTime.now(),
        unreadCount: message.isMine ? conversation.unreadCount : conversation.unreadCount + 1,
      );
    }
  }

  /// Update message status in cache
  void updateMessageStatus(String messageId, MessageStatus status) {
    // Find message in cache and update
    for (var messages in _messagesCache.values) {
      final index = messages.indexWhere((m) => m.id == messageId);
      if (index != -1) {
        messages[index] = messages[index].copyWith(status: status);
        break;
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // WebSocket Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /// Connect to WebSocket
  void connect() {
    _api.connect();
  }

  /// Disconnect from WebSocket
  void disconnect() {
    _api.disconnect();
  }

  /// Join conversation room
  void joinConversation(String conversationId) {
    _api.joinConversation(conversationId);
  }

  /// Leave conversation room
  void leaveConversation(String conversationId) {
    _api.leaveConversation(conversationId);
  }

  /// Send typing indicator
  void sendTypingIndicator(String conversationId, {required bool isTyping}) {
    _api.sendTypingIndicator(conversationId, isTyping: isTyping);
  }

  /// Update conversation typing status
  void updateTypingStatus(String conversationId, bool isTyping) {
    if (_conversationsCache.containsKey(conversationId)) {
      final conversation = _conversationsCache[conversationId]!;
      _conversationsCache[conversationId] = conversation.copyWith(isTyping: isTyping);
    }
  }

  /// Update participant online status
  void updateOnlineStatus(String userId, bool isOnline) {
    for (var conversation in _conversationsCache.values) {
      final participantIndex = conversation.participants.indexWhere(
        (p) => p.userId == userId,
      );

      if (participantIndex != -1) {
        final updatedParticipants = [...conversation.participants];
        updatedParticipants[participantIndex] = updatedParticipants[participantIndex].copyWith(
          isOnline: isOnline,
          lastSeen: isOnline ? null : DateTime.now(),
        );

        _conversationsCache[conversation.id] = conversation.copyWith(
          participants: updatedParticipants,
        );
      }
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Streams
  // ─────────────────────────────────────────────────────────────────────────────

  /// Stream of incoming messages
  Stream<Message> get messageStream => _api.messageStream;

  /// Stream of typing indicators
  Stream<Map<String, dynamic>> get typingStream => _api.typingStream;

  /// Stream of online status updates
  Stream<Map<String, dynamic>> get onlineStatusStream => _api.onlineStatusStream;

  // ─────────────────────────────────────────────────────────────────────────────
  // Cache Management
  // ─────────────────────────────────────────────────────────────────────────────

  /// Clear all caches
  void clearCache() {
    _conversationsCache.clear();
    _messagesCache.clear();
  }

  /// Clear messages cache for a conversation
  void clearMessagesCache(String conversationId) {
    _messagesCache.remove(conversationId);
  }

  /// Dispose resources
  void dispose() {
    _api.dispose();
    clearCache();
  }
}
