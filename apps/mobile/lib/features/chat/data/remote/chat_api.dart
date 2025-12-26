/// Chat API
/// طبقة الاتصال بخدمة المحادثات
///
/// Handles REST API calls and WebSocket connections

import 'dart:async';
import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:socket_io_client/socket_io_client.dart' as io;
import '../../../../core/config/api_config.dart';
import '../models/conversation_model.dart';
import '../models/message_model.dart';

/// Chat API Client
class ChatApi {
  final Dio _dio;
  final String _baseUrl;
  final String _socketUrl;
  io.Socket? _socket;
  String? _authToken;
  String? _currentUserId;

  // Stream controllers for real-time events
  final _messageStreamController = StreamController<Message>.broadcast();
  final _typingStreamController = StreamController<Map<String, dynamic>>.broadcast();
  final _onlineStatusStreamController = StreamController<Map<String, dynamic>>.broadcast();

  /// Stream of incoming messages
  Stream<Message> get messageStream => _messageStreamController.stream;

  /// Stream of typing indicators
  Stream<Map<String, dynamic>> get typingStream => _typingStreamController.stream;

  /// Stream of online status updates
  Stream<Map<String, dynamic>> get onlineStatusStream => _onlineStatusStreamController.stream;

  ChatApi({
    required String baseUrl,
    String? authToken,
    String? currentUserId,
  })  : _baseUrl = baseUrl,
        _socketUrl = ApiConfig.chatSocketUrl,
        _authToken = authToken,
        _currentUserId = currentUserId,
        _dio = Dio(BaseOptions(
          baseUrl: baseUrl,
          connectTimeout: const Duration(seconds: 30),
          receiveTimeout: const Duration(seconds: 30),
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
        )) {
    if (_authToken != null) {
      _dio.options.headers['Authorization'] = 'Bearer $_authToken';
    }
  }

  /// Set authentication token
  void setAuthToken(String token) {
    _authToken = token;
    _dio.options.headers['Authorization'] = 'Bearer $token';

    // Reconnect socket with new auth
    if (_socket?.connected ?? false) {
      _socket?.disconnect();
      _connectSocket();
    }
  }

  /// Set current user ID
  void setCurrentUserId(String userId) {
    _currentUserId = userId;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // REST API Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /// Get all conversations for current user
  Future<List<Conversation>> getConversations() async {
    try {
      final response = await _dio.get('/api/v1/conversations');
      final data = response.data as List<dynamic>;
      return data
          .map((json) => Conversation.fromJson(
                json as Map<String, dynamic>,
                currentUserId: _currentUserId,
              ))
          .toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get conversation by ID
  Future<Conversation> getConversation(String conversationId) async {
    try {
      final response = await _dio.get('/api/v1/conversations/$conversationId');
      return Conversation.fromJson(
        response.data as Map<String, dynamic>,
        currentUserId: _currentUserId,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get messages for a conversation
  Future<List<Message>> getMessages(
    String conversationId, {
    int? limit,
    String? before,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (limit != null) queryParams['limit'] = limit;
      if (before != null) queryParams['before'] = before;

      final response = await _dio.get(
        '/api/v1/conversations/$conversationId/messages',
        queryParameters: queryParams,
      );

      final data = response.data as List<dynamic>;
      return data
          .map((json) => Message.fromJson(
                json as Map<String, dynamic>,
                currentUserId: _currentUserId,
              ))
          .toList();
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Send a message
  Future<Message> sendMessage(
    String conversationId, {
    required String content,
    MessageType type = MessageType.text,
    String? attachmentUrl,
    Map<String, dynamic>? metadata,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/conversations/$conversationId/messages',
        data: {
          'content': content,
          'type': type.name,
          'attachmentUrl': attachmentUrl,
          'metadata': metadata,
        },
      );

      return Message.fromJson(
        response.data as Map<String, dynamic>,
        currentUserId: _currentUserId,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Create a new conversation
  Future<Conversation> createConversation({
    required String participantId,
    String? productId,
    String? orderId,
    String? initialMessage,
  }) async {
    try {
      final response = await _dio.post(
        '/api/v1/conversations',
        data: {
          'participantId': participantId,
          'productId': productId,
          'orderId': orderId,
          'initialMessage': initialMessage,
        },
      );

      return Conversation.fromJson(
        response.data as Map<String, dynamic>,
        currentUserId: _currentUserId,
      );
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Mark conversation as read
  Future<void> markAsRead(String conversationId) async {
    try {
      await _dio.put('/api/v1/conversations/$conversationId/read');
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  /// Get unread count
  Future<int> getUnreadCount() async {
    try {
      final response = await _dio.get('/api/v1/conversations/unread-count');
      return response.data['count'] as int? ?? 0;
    } on DioException catch (e) {
      throw _handleError(e);
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // WebSocket Methods (Socket.IO)
  // ─────────────────────────────────────────────────────────────────────────────

  /// Connect to Socket.IO server
  void _connectSocket() {
    if (_socket?.connected ?? false) {
      return; // Already connected
    }

    _socket = io.io(
      _socketUrl,
      io.OptionBuilder()
          .setTransports(['websocket'])
          .enableAutoConnect()
          .setAuth({
            'token': _authToken,
          })
          .build(),
    );

    _socket!.onConnect((_) {
      print('✅ Chat socket connected');
    });

    _socket!.onDisconnect((_) {
      print('❌ Chat socket disconnected');
    });

    _socket!.onConnectError((error) {
      print('❌ Chat socket connection error: $error');
    });

    // Listen for new messages
    _socket!.on('message', (data) {
      try {
        final message = Message.fromJson(
          data as Map<String, dynamic>,
          currentUserId: _currentUserId,
        );
        _messageStreamController.add(message);
      } catch (e) {
        print('❌ Error parsing message: $e');
      }
    });

    // Listen for typing indicators
    _socket!.on('typing', (data) {
      _typingStreamController.add(data as Map<String, dynamic>);
    });

    _socket!.on('stop_typing', (data) {
      _typingStreamController.add({
        ...data as Map<String, dynamic>,
        'isTyping': false,
      });
    });

    // Listen for online status updates
    _socket!.on('user_online', (data) {
      _onlineStatusStreamController.add({
        ...data as Map<String, dynamic>,
        'isOnline': true,
      });
    });

    _socket!.on('user_offline', (data) {
      _onlineStatusStreamController.add({
        ...data as Map<String, dynamic>,
        'isOnline': false,
      });
    });

    _socket!.connect();
  }

  /// Connect WebSocket
  void connect() {
    _connectSocket();
  }

  /// Disconnect WebSocket
  void disconnect() {
    _socket?.disconnect();
    _socket?.dispose();
    _socket = null;
  }

  /// Join a conversation room
  void joinConversation(String conversationId) {
    _socket?.emit('join_conversation', {'conversationId': conversationId});
  }

  /// Leave a conversation room
  void leaveConversation(String conversationId) {
    _socket?.emit('leave_conversation', {'conversationId': conversationId});
  }

  /// Send typing indicator
  void sendTypingIndicator(String conversationId, {required bool isTyping}) {
    final event = isTyping ? 'typing' : 'stop_typing';
    _socket?.emit(event, {'conversationId': conversationId});
  }

  /// Send message via socket (for instant delivery)
  void sendMessageViaSocket({
    required String conversationId,
    required String content,
    MessageType type = MessageType.text,
    String? attachmentUrl,
    Map<String, dynamic>? metadata,
  }) {
    _socket?.emit('send_message', {
      'conversationId': conversationId,
      'content': content,
      'type': type.name,
      'attachmentUrl': attachmentUrl,
      'metadata': metadata,
    });
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Error Handling
  // ─────────────────────────────────────────────────────────────────────────────

  Exception _handleError(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return ChatApiException(
          code: 'TIMEOUT',
          message: 'انتهت مهلة الاتصال',
          isNetworkError: true,
        );

      case DioExceptionType.connectionError:
        return ChatApiException(
          code: 'NO_CONNECTION',
          message: 'لا يوجد اتصال بالإنترنت',
          isNetworkError: true,
        );

      case DioExceptionType.badResponse:
        final statusCode = e.response?.statusCode ?? 0;
        final data = e.response?.data;
        String message = 'حدث خطأ غير متوقع';

        if (data is Map) {
          message = data['message'] ?? data['error'] ?? message;
        }

        return ChatApiException(
          code: 'HTTP_$statusCode',
          message: message,
          statusCode: statusCode,
        );

      default:
        return ChatApiException(
          code: 'UNKNOWN',
          message: 'حدث خطأ غير متوقع',
        );
    }
  }

  /// Dispose resources
  void dispose() {
    disconnect();
    _messageStreamController.close();
    _typingStreamController.close();
    _onlineStatusStreamController.close();
  }
}

/// Chat API Exception
class ChatApiException implements Exception {
  final String code;
  final String message;
  final int? statusCode;
  final bool isNetworkError;

  ChatApiException({
    required this.code,
    required this.message,
    this.statusCode,
    this.isNetworkError = false,
  });

  @override
  String toString() => 'ChatApiException($code): $message';
}
