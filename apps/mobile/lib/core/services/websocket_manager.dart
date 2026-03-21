/// SAHOOL WebSocket Manager
/// مدير WebSocket المحسن
///
/// Features:
/// - Centralized WebSocket connection management
/// - Auto-reconnection with exponential backoff
/// - Message routing based on event types
/// - Subscription management
/// - Connection state monitoring
/// - Heartbeat/ping-pong support
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../auth/secure_storage_service.dart';
import '../config/env_config.dart';
import '../utils/app_logger.dart';
import 'event_bus.dart';

/// WebSocket connection states
enum WebSocketConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
  error,
  disposed,
}

/// WebSocket message model
class WebSocketMessage {
  final String type;
  final String? eventType;
  final String? subject;
  final String? priority;
  final Map<String, dynamic>? data;
  final String? message;
  final String? messageAr;
  final DateTime timestamp;
  final String? correlationId;

  const WebSocketMessage({
    required this.type,
    this.eventType,
    this.subject,
    this.priority,
    this.data,
    this.message,
    this.messageAr,
    required this.timestamp,
    this.correlationId,
  });

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: json['type'] as String? ?? 'unknown',
      eventType: json['event_type'] as String?,
      subject: json['subject'] as String?,
      priority: json['priority'] as String?,
      data: json['data'] as Map<String, dynamic>?,
      message: json['message'] as String?,
      messageAr: json['message_ar'] as String?,
      timestamp: json['timestamp'] != null
          ? DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now()
          : DateTime.now(),
      correlationId: json['correlation_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'type': type,
        if (eventType != null) 'event_type': eventType,
        if (subject != null) 'subject': subject,
        if (priority != null) 'priority': priority,
        if (data != null) 'data': data,
        if (message != null) 'message': message,
        if (messageAr != null) 'message_ar': messageAr,
        'timestamp': timestamp.toIso8601String(),
        if (correlationId != null) 'correlation_id': correlationId,
      };

  bool get isHighPriority => priority == 'high' || priority == 'critical';
}

/// Subscription info
class WebSocketSubscription {
  final String topic;
  final DateTime subscribedAt;
  bool isActive;

  WebSocketSubscription({
    required this.topic,
    required this.subscribedAt,
    this.isActive = true,
  });
}

/// WebSocket Manager for real-time communication
/// مدير WebSocket للاتصال في الوقت الفعلي
class WebSocketManager {
  final Ref _ref;

  WebSocketChannel? _channel;
  WebSocketConnectionState _state = WebSocketConnectionState.disconnected;

  // Stream controllers
  final StreamController<WebSocketMessage> _messageController =
      StreamController<WebSocketMessage>.broadcast();
  final StreamController<WebSocketConnectionState> _stateController =
      StreamController<WebSocketConnectionState>.broadcast();

  // Reconnection settings
  Timer? _reconnectTimer;
  Timer? _heartbeatTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 10;
  static const Duration _baseReconnectDelay = Duration(seconds: 2);
  static const Duration _maxReconnectDelay = Duration(minutes: 2);
  static const Duration _heartbeatInterval = Duration(seconds: 30);

  // Subscription management
  final Map<String, WebSocketSubscription> _subscriptions = {};
  final Map<String, List<void Function(WebSocketMessage)>> _messageHandlers = {};

  // Message queue for offline support
  final List<Map<String, dynamic>> _pendingMessages = [];
  DateTime? _lastMessageTime;

  WebSocketManager(this._ref);

  /// Stream of WebSocket messages
  Stream<WebSocketMessage> get messages => _messageController.stream;

  /// Stream of connection state changes
  Stream<WebSocketConnectionState> get connectionState => _stateController.stream;

  /// Current connection state
  WebSocketConnectionState get state => _state;

  /// Is connected
  bool get isConnected => _state == WebSocketConnectionState.connected;

  /// Get subscriptions
  List<String> get activeSubscriptions =>
      _subscriptions.entries.where((e) => e.value.isActive).map((e) => e.key).toList();

  /// Connect to WebSocket server
  /// الاتصال بخادم WebSocket
  Future<void> connect() async {
    if (_state == WebSocketConnectionState.connected ||
        _state == WebSocketConnectionState.connecting) {
      AppLogger.d('Already connected or connecting', tag: 'WebSocket');
      return;
    }

    _updateState(WebSocketConnectionState.connecting);

    try {
      final secureStorage = _ref.read(secureStorageProvider);
      final token = await secureStorage.getAccessToken();
      final tenantId = await secureStorage.getTenantId();

      if (token == null || tenantId == null) {
        throw Exception('Authentication required for WebSocket connection');
      }

      // Build WebSocket URL
      final wsUrl = EnvConfig.wsGatewayUrl;
      final uri = Uri.parse('$wsUrl/ws?tenant_id=$tenantId');

      AppLogger.i('Connecting to WebSocket: ${uri.host}', tag: 'WebSocket');

      // Connect with authorization header
      final socket = await WebSocket.connect(
        uri.toString(),
        headers: {
          'Authorization': 'Bearer $token',
          'X-Tenant-Id': tenantId,
        },
      );

      _channel = IOWebSocketChannel(socket);

      // Listen for messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnect,
        cancelOnError: false,
      );

      _updateState(WebSocketConnectionState.connected);
      _reconnectAttempts = 0;

      // Start heartbeat
      _startHeartbeat();

      // Resubscribe to topics
      await _resubscribe();

      // Send pending messages
      await _sendPendingMessages();

      AppLogger.i('WebSocket connected successfully', tag: 'WebSocket');

      // Emit connection event to local event bus
      _ref.read(eventBusProvider).emit(
            AppEvent(
              type: EventType.connectionStateChanged,
              data: {'state': 'connected'},
            ),
          );
    } catch (e, stackTrace) {
      AppLogger.e('WebSocket connection failed', tag: 'WebSocket', error: e, stackTrace: stackTrace);
      _updateState(WebSocketConnectionState.error);
      _scheduleReconnect();
    }
  }

  /// Disconnect from WebSocket server
  /// قطع الاتصال من خادم WebSocket
  Future<void> disconnect() async {
    _reconnectTimer?.cancel();
    _heartbeatTimer?.cancel();
    _reconnectAttempts = 0;

    if (_channel != null) {
      await _channel!.sink.close(status.goingAway);
      _channel = null;
    }

    _updateState(WebSocketConnectionState.disconnected);
    AppLogger.i('WebSocket disconnected', tag: 'WebSocket');

    // Emit disconnection event
    _ref.read(eventBusProvider).emit(
          AppEvent(
            type: EventType.connectionStateChanged,
            data: {'state': 'disconnected'},
          ),
        );
  }

  /// Subscribe to a topic
  /// الاشتراك في موضوع
  Future<void> subscribe(String topic) async {
    if (_subscriptions.containsKey(topic) && _subscriptions[topic]!.isActive) {
      return; // Already subscribed
    }

    _subscriptions[topic] = WebSocketSubscription(
      topic: topic,
      subscribedAt: DateTime.now(),
      isActive: true,
    );

    if (isConnected) {
      await _sendMessage({
        'type': 'subscribe',
        'topics': [topic],
      });
      AppLogger.d('Subscribed to topic: $topic', tag: 'WebSocket');
    }
  }

  /// Subscribe to multiple topics
  /// الاشتراك في مواضيع متعددة
  Future<void> subscribeAll(List<String> topics) async {
    final newTopics = <String>[];

    for (final topic in topics) {
      if (!_subscriptions.containsKey(topic) || !_subscriptions[topic]!.isActive) {
        _subscriptions[topic] = WebSocketSubscription(
          topic: topic,
          subscribedAt: DateTime.now(),
          isActive: true,
        );
        newTopics.add(topic);
      }
    }

    if (isConnected && newTopics.isNotEmpty) {
      await _sendMessage({
        'type': 'subscribe',
        'topics': newTopics,
      });
      AppLogger.d('Subscribed to topics: $newTopics', tag: 'WebSocket');
    }
  }

  /// Unsubscribe from a topic
  /// إلغاء الاشتراك من موضوع
  Future<void> unsubscribe(String topic) async {
    if (!_subscriptions.containsKey(topic)) return;

    _subscriptions[topic]!.isActive = false;

    if (isConnected) {
      await _sendMessage({
        'type': 'unsubscribe',
        'topics': [topic],
      });
      AppLogger.d('Unsubscribed from topic: $topic', tag: 'WebSocket');
    }
  }

  /// Unsubscribe from all topics
  /// إلغاء الاشتراك من جميع المواضيع
  Future<void> unsubscribeAll() async {
    final activeTopics = activeSubscriptions;

    for (final topic in _subscriptions.keys) {
      _subscriptions[topic]!.isActive = false;
    }

    if (isConnected && activeTopics.isNotEmpty) {
      await _sendMessage({
        'type': 'unsubscribe',
        'topics': activeTopics,
      });
    }
  }

  /// Register message handler for specific event type
  /// تسجيل معالج رسائل لنوع حدث معين
  void onMessage(String eventType, void Function(WebSocketMessage) handler) {
    _messageHandlers[eventType] ??= [];
    _messageHandlers[eventType]!.add(handler);
  }

  /// Remove message handler
  /// إزالة معالج الرسائل
  void offMessage(String eventType, void Function(WebSocketMessage) handler) {
    _messageHandlers[eventType]?.remove(handler);
  }

  /// Send message to server
  /// إرسال رسالة للخادم
  Future<void> send(Map<String, dynamic> message) async {
    if (isConnected) {
      await _sendMessage(message);
    } else {
      // Queue message for later
      _pendingMessages.add(message);
      AppLogger.d('Message queued (offline)', tag: 'WebSocket');
    }
  }

  /// Send typing indicator
  /// إرسال مؤشر الكتابة
  Future<void> sendTyping(String roomId, bool isTyping) async {
    await send({
      'type': 'typing',
      'room': roomId,
      'typing': isTyping,
    });
  }

  /// Send read receipt
  /// إرسال إيصال القراءة
  Future<void> sendRead(String roomId, String messageId) async {
    await send({
      'type': 'read',
      'room': roomId,
      'message_id': messageId,
    });
  }

  /// Join a room
  /// الانضمام لغرفة
  Future<void> joinRoom(String roomId) async {
    await send({
      'type': 'join_room',
      'room': roomId,
    });
    await subscribe('room:$roomId');
  }

  /// Leave a room
  /// مغادرة الغرفة
  Future<void> leaveRoom(String roomId) async {
    await send({
      'type': 'leave_room',
      'room': roomId,
    });
    await unsubscribe('room:$roomId');
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Private Methods
  // ═══════════════════════════════════════════════════════════════════════════════

  void _handleMessage(dynamic rawMessage) {
    try {
      final data = jsonDecode(rawMessage as String) as Map<String, dynamic>;
      final message = WebSocketMessage.fromJson(data);

      _lastMessageTime = DateTime.now();

      // Handle system messages
      if (message.type == 'pong') {
        return; // Heartbeat response
      }

      if (message.type == 'error') {
        AppLogger.w('WebSocket error: ${message.message}', tag: 'WebSocket');
        return;
      }

      // Emit to stream
      _messageController.add(message);

      // Call registered handlers
      final eventType = message.eventType ?? message.type;
      if (_messageHandlers.containsKey(eventType)) {
        for (final handler in _messageHandlers[eventType]!) {
          try {
            handler(message);
          } catch (e) {
            AppLogger.e('Error in message handler', tag: 'WebSocket', error: e);
          }
        }
      }

      // Also emit to local event bus for cross-feature communication
      _emitToEventBus(message);

      // Log high priority messages
      if (message.isHighPriority) {
        AppLogger.i(
          'High priority message: ${message.eventType ?? message.type}',
          tag: 'WebSocket',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error parsing WebSocket message', tag: 'WebSocket', error: e, stackTrace: stackTrace);
    }
  }

  void _emitToEventBus(WebSocketMessage wsMessage) {
    final eventBus = _ref.read(eventBusProvider);

    // Map WebSocket message types to event bus events
    final eventType = _mapToEventType(wsMessage.eventType ?? wsMessage.type);

    if (eventType != null) {
      eventBus.emit(AppEvent(
        type: eventType,
        data: wsMessage.data ?? {},
        source: 'websocket',
      ));
    }
  }

  EventType? _mapToEventType(String wsType) {
    switch (wsType) {
      case 'field_updated':
        return EventType.fieldUpdated;
      case 'task_completed':
        return EventType.taskCompleted;
      case 'task_created':
        return EventType.taskCreated;
      case 'weather_alert':
        return EventType.weatherAlert;
      case 'irrigation_reminder':
        return EventType.irrigationReminder;
      case 'notification':
        return EventType.notificationReceived;
      case 'sync_required':
        return EventType.syncRequired;
      default:
        return null;
    }
  }

  void _handleError(dynamic error) {
    AppLogger.e('WebSocket error', tag: 'WebSocket', error: error);
    _updateState(WebSocketConnectionState.error);
    _scheduleReconnect();
  }

  void _handleDisconnect() {
    AppLogger.w('WebSocket disconnected unexpectedly', tag: 'WebSocket');
    _heartbeatTimer?.cancel();

    if (_state != WebSocketConnectionState.disconnected &&
        _state != WebSocketConnectionState.disposed) {
      _updateState(WebSocketConnectionState.disconnected);
      _scheduleReconnect();
    }
  }

  Future<void> _sendMessage(Map<String, dynamic> message) async {
    if (_channel == null) {
      throw Exception('WebSocket not connected');
    }

    final json = jsonEncode(message);
    _channel!.sink.add(json);
  }

  void _updateState(WebSocketConnectionState newState) {
    if (_state != newState) {
      _state = newState;
      _stateController.add(newState);
    }
  }

  void _scheduleReconnect() {
    if (_state == WebSocketConnectionState.disposed) return;

    if (_reconnectAttempts >= _maxReconnectAttempts) {
      AppLogger.e('Max reconnection attempts reached', tag: 'WebSocket');
      _updateState(WebSocketConnectionState.error);
      return;
    }

    _reconnectTimer?.cancel();
    _reconnectAttempts++;

    // Exponential backoff with jitter
    final baseDelay = _baseReconnectDelay.inMilliseconds * pow(2, _reconnectAttempts - 1);
    final jitter = Random().nextInt(1000);
    final delay = Duration(
      milliseconds: min(baseDelay + jitter, _maxReconnectDelay.inMilliseconds).toInt(),
    );

    AppLogger.i(
      'Scheduling reconnect in ${delay.inSeconds}s (attempt $_reconnectAttempts)',
      tag: 'WebSocket',
    );

    _updateState(WebSocketConnectionState.reconnecting);

    _reconnectTimer = Timer(delay, () {
      if (_state != WebSocketConnectionState.disposed) {
        connect();
      }
    });
  }

  Future<void> _resubscribe() async {
    final activeTopics = _subscriptions.entries
        .where((e) => e.value.isActive)
        .map((e) => e.key)
        .toList();

    if (activeTopics.isEmpty) return;

    AppLogger.d('Resubscribing to ${activeTopics.length} topics', tag: 'WebSocket');

    await _sendMessage({
      'type': 'subscribe',
      'topics': activeTopics,
    });
  }

  Future<void> _sendPendingMessages() async {
    if (_pendingMessages.isEmpty) return;

    AppLogger.d('Sending ${_pendingMessages.length} pending messages', tag: 'WebSocket');

    final messages = List<Map<String, dynamic>>.from(_pendingMessages);
    _pendingMessages.clear();

    for (final message in messages) {
      try {
        await _sendMessage(message);
      } catch (e) {
        AppLogger.e('Failed to send pending message', tag: 'WebSocket', error: e);
      }
    }
  }

  void _startHeartbeat() {
    _heartbeatTimer?.cancel();

    _heartbeatTimer = Timer.periodic(_heartbeatInterval, (timer) {
      if (isConnected) {
        _sendMessage({'type': 'ping'});
      } else {
        timer.cancel();
      }
    });
  }

  /// Dispose resources
  void dispose() {
    _updateState(WebSocketConnectionState.disposed);
    _reconnectTimer?.cancel();
    _heartbeatTimer?.cancel();
    _channel?.sink.close();
    _messageController.close();
    _stateController.close();
    _messageHandlers.clear();
    _subscriptions.clear();
    _pendingMessages.clear();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// WebSocket Manager Provider
final webSocketManagerProvider = Provider<WebSocketManager>((ref) {
  final manager = WebSocketManager(ref);
  ref.onDispose(() => manager.dispose());
  return manager;
});

/// WebSocket Connection State Provider
final webSocketStateProvider = StreamProvider<WebSocketConnectionState>((ref) {
  final manager = ref.watch(webSocketManagerProvider);
  return manager.connectionState;
});

/// WebSocket Messages Provider
final webSocketMessagesProvider = StreamProvider<WebSocketMessage>((ref) {
  final manager = ref.watch(webSocketManagerProvider);
  return manager.messages;
});

/// Is WebSocket Connected Provider
final isWebSocketConnectedProvider = Provider<bool>((ref) {
  final state = ref.watch(webSocketStateProvider);
  return state.whenOrNull(data: (s) => s == WebSocketConnectionState.connected) ?? false;
});

/// Active Subscriptions Provider
final activeWebSocketSubscriptionsProvider = Provider<List<String>>((ref) {
  final manager = ref.watch(webSocketManagerProvider);
  return manager.activeSubscriptions;
});
