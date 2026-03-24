import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:web_socket_channel/io.dart';
import 'package:web_socket_channel/status.dart' as status;
import '../utils/app_logger.dart';

/// WebSocket connection states
/// حالات اتصال WebSocket
enum ConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
  error,
}

/// WebSocket event model
/// نموذج حدث WebSocket
class WebSocketEvent {
  final String type;
  final String? eventType;
  final String? priority;
  final String? message;
  final String? messageAr;
  final Map<String, dynamic>? data;
  final String? subject;
  final DateTime timestamp;

  WebSocketEvent({
    required this.type,
    this.eventType,
    this.priority,
    this.message,
    this.messageAr,
    this.data,
    this.subject,
    DateTime? timestamp,
  }) : timestamp = timestamp ?? DateTime.now();

  factory WebSocketEvent.fromJson(Map<String, dynamic> json) {
    return WebSocketEvent(
      type: json['type'] as String,
      eventType: json['event_type'] as String?,
      priority: json['priority'] as String?,
      message: json['message'] as String?,
      messageAr: json['message_ar'] as String?,
      data: json['data'] as Map<String, dynamic>?,
      subject: json['subject'] as String?,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : DateTime.now(),
    );
  }
}

/// WebSocket Service for real-time communication
/// خدمة WebSocket للاتصال في الوقت الفعلي
class WebSocketService {
  final String baseUrl;
  final String Function() getToken;
  final String Function() getTenantId;

  WebSocketChannel? _channel;
  WebSocket? _rawSocket;
  final StreamController<WebSocketEvent> _eventController =
      StreamController<WebSocketEvent>.broadcast();
  final StreamController<ConnectionState> _stateController =
      StreamController<ConnectionState>.broadcast();

  ConnectionState _state = ConnectionState.disconnected;
  Timer? _reconnectTimer;
  Timer? _pingTimer;
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 5;
  static const Duration _reconnectDelay = Duration(seconds: 3);
  static const Duration _pingInterval = Duration(seconds: 30);

  final Set<String> _subscribedRooms = {};

  WebSocketService({
    required this.baseUrl,
    required this.getToken,
    required this.getTenantId,
  });

  /// Stream of WebSocket events
  Stream<WebSocketEvent> get events => _eventController.stream;

  /// Stream of connection state changes
  Stream<ConnectionState> get connectionState => _stateController.stream;

  /// Current connection state
  ConnectionState get state => _state;

  /// Is connected
  bool get isConnected => _state == ConnectionState.connected;

  /// Connect to WebSocket server
  /// الاتصال بخادم WebSocket
  Future<void> connect() async {
    if (_state == ConnectionState.connected ||
        _state == ConnectionState.connecting) {
      AppLogger.i('Already connected or connecting');
      return;
    }

    _updateState(ConnectionState.connecting);

    try {
      final token = getToken();
      final tenantId = getTenantId();

      if (token.isEmpty || tenantId.isEmpty) {
        throw Exception('Token or tenant ID not available');
      }

      // Build WebSocket URL without token (security fix: token moved to header)
      final wsUrl = baseUrl.replaceFirst('http', 'ws');
      final uri = Uri.parse('$wsUrl/ws?tenant_id=$tenantId');

      AppLogger.i('Connecting to WebSocket: $uri');

      // Connect with Authorization header for security
      _rawSocket = await WebSocket.connect(
        uri.toString(),
        headers: {
          'Authorization': 'Bearer $token',
        },
      );

      _channel = IOWebSocketChannel(_rawSocket!);

      // Listen to messages
      _channel!.stream.listen(
        _handleMessage,
        onError: _handleError,
        onDone: _handleDisconnect,
      );

      _updateState(ConnectionState.connected);
      _reconnectAttempts = 0;

      // Start ping timer
      _startPingTimer();

      // Resubscribe to rooms
      await _resubscribeToRooms();

      AppLogger.i('WebSocket connected successfully');
    } catch (e) {
      AppLogger.e('WebSocket connection failed', error: e);
      _updateState(ConnectionState.error);
      _scheduleReconnect();
    }
  }

  /// Disconnect from WebSocket server
  /// قطع الاتصال من خادم WebSocket
  Future<void> disconnect() async {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();

    if (_channel != null) {
      await _channel!.sink.close(status.goingAway);
      _channel = null;
    }

    _subscribedRooms.clear();
    _updateState(ConnectionState.disconnected);
    AppLogger.i('WebSocket disconnected');
  }

  /// Subscribe to a room
  /// الاشتراك في غرفة
  Future<void> subscribeToRoom(String roomId) async {
    if (!isConnected) {
      AppLogger.w('Cannot subscribe to room: not connected');
      return;
    }

    _subscribedRooms.add(roomId);

    await _sendMessage({
      'type': 'join_room',
      'room': roomId,
    });

    AppLogger.i('Subscribed to room: $roomId');
  }

  /// Unsubscribe from a room
  /// إلغاء الاشتراك من غرفة
  Future<void> unsubscribeFromRoom(String roomId) async {
    if (!isConnected) {
      return;
    }

    _subscribedRooms.remove(roomId);

    await _sendMessage({
      'type': 'leave_room',
      'room': roomId,
    });

    AppLogger.i('Unsubscribed from room: $roomId');
  }

  /// Subscribe to multiple topics
  /// الاشتراك في عدة مواضيع
  Future<void> subscribe(List<String> topics) async {
    if (!isConnected) {
      AppLogger.w('Cannot subscribe: not connected');
      return;
    }

    _subscribedRooms.addAll(topics);

    await _sendMessage({
      'type': 'subscribe',
      'topics': topics,
    });

    AppLogger.i('Subscribed to topics: $topics');
  }

  /// Unsubscribe from topics
  /// إلغاء الاشتراك من مواضيع
  Future<void> unsubscribe(List<String> topics) async {
    if (!isConnected) {
      return;
    }

    _subscribedRooms.removeAll(topics);

    await _sendMessage({
      'type': 'unsubscribe',
      'topics': topics,
    });

    AppLogger.i('Unsubscribed from topics: $topics');
  }

  /// Broadcast message to a room
  /// بث رسالة إلى غرفة
  Future<void> broadcastToRoom(String roomId, Map<String, dynamic> message) async {
    if (!isConnected) {
      throw Exception('WebSocket not connected');
    }

    await _sendMessage({
      'type': 'broadcast',
      'room': roomId,
      'message': message,
    });
  }

  /// Send typing indicator
  /// إرسال مؤشر الكتابة
  Future<void> sendTyping(String roomId, bool isTyping) async {
    if (!isConnected) return;

    await _sendMessage({
      'type': 'typing',
      'room': roomId,
      'typing': isTyping,
    });
  }

  /// Send read receipt
  /// إرسال إيصال القراءة
  Future<void> sendRead(String roomId, String messageId) async {
    if (!isConnected) return;

    await _sendMessage({
      'type': 'read',
      'room': roomId,
      'message_id': messageId,
    });
  }

  /// Handle incoming message
  void _handleMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String) as Map<String, dynamic>;
      final event = WebSocketEvent.fromJson(data);

      _eventController.add(event);

      // Log important events
      if (event.priority == 'high' || event.priority == 'critical') {
        AppLogger.i('WebSocket event: ${event.eventType ?? event.type}');
      }
    } catch (e) {
      AppLogger.e('Error parsing WebSocket message', error: e);
    }
  }

  /// Handle connection error
  void _handleError(dynamic error) {
    AppLogger.e('WebSocket error', error: error);
    _updateState(ConnectionState.error);
    _scheduleReconnect();
  }

  /// Handle disconnection
  void _handleDisconnect() {
    AppLogger.w('WebSocket disconnected');
    _pingTimer?.cancel();

    if (_state != ConnectionState.disconnected) {
      _updateState(ConnectionState.disconnected);
      _scheduleReconnect();
    }
  }

  /// Send message to server
  Future<void> _sendMessage(Map<String, dynamic> message) async {
    if (_channel == null) {
      throw Exception('WebSocket not connected');
    }

    final json = jsonEncode(message);
    _channel!.sink.add(json);
  }

  /// Update connection state
  void _updateState(ConnectionState newState) {
    if (_state != newState) {
      _state = newState;
      _stateController.add(newState);
    }
  }

  /// Schedule reconnection
  void _scheduleReconnect() {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      AppLogger.e('Max reconnection attempts reached');
      _updateState(ConnectionState.error);
      return;
    }

    _reconnectTimer?.cancel();
    _reconnectAttempts++;

    final delay = _reconnectDelay * _reconnectAttempts;
    AppLogger.i('Scheduling reconnect in ${delay.inSeconds}s (attempt $_reconnectAttempts)');

    _updateState(ConnectionState.reconnecting);

    _reconnectTimer = Timer(delay, () {
      connect();
    });
  }

  /// Resubscribe to all rooms after reconnection
  Future<void> _resubscribeToRooms() async {
    if (_subscribedRooms.isEmpty) return;

    AppLogger.i('Resubscribing to ${_subscribedRooms.length} rooms');

    await subscribe(_subscribedRooms.toList());
  }

  /// Start ping timer to keep connection alive
  void _startPingTimer() {
    _pingTimer?.cancel();

    _pingTimer = Timer.periodic(_pingInterval, (timer) {
      if (isConnected) {
        _sendMessage({'type': 'ping'});
      } else {
        timer.cancel();
      }
    });
  }

  /// Dispose resources
  void dispose() {
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();
    _channel?.sink.close();
    _rawSocket?.close();
    _rawSocket = null;
    _eventController.close();
    _stateController.close();
  }
}
