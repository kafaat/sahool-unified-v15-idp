import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'websocket_service.dart';
import '../auth/auth_service.dart';
import '../config/env_config.dart';
import '../utils/app_logger.dart';

/// WebSocket Service Provider
/// مزود خدمة WebSocket
final webSocketServiceProvider = Provider<WebSocketService>((ref) {
  final authState = ref.watch(authStateProvider);

  return WebSocketService(
    baseUrl: EnvConfig.wsGatewayUrl,
    getToken: () {
      // Get access token from auth state (cached in memory)
      final token = authState.accessToken;
      if (token == null || token.isEmpty) {
        AppLogger.w('WebSocket: No access token available', tag: 'WS');
        return '';
      }
      return token;
    },
    getTenantId: () {
      // Get tenant ID from current user
      final tenantId = authState.user?.tenantId;
      if (tenantId == null || tenantId.isEmpty) {
        AppLogger.w('WebSocket: No tenant ID available', tag: 'WS');
        return '';
      }
      return tenantId;
    },
  );
});

/// WebSocket connection state provider
/// مزود حالة اتصال WebSocket
final webSocketStateProvider = StreamProvider<ConnectionState>((ref) {
  final service = ref.watch(webSocketServiceProvider);
  return service.connectionState;
});

/// WebSocket events stream provider
/// مزود تدفق أحداث WebSocket
final webSocketEventsProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);
  return service.events;
});

/// Field-specific events provider
/// مزود أحداث خاصة بالحقل
final fieldEventsProvider = StreamProvider.family<WebSocketEvent, String>((ref, fieldId) {
  final service = ref.watch(webSocketServiceProvider);

  // Subscribe to field room
  service.subscribeToRoom('field:$fieldId');

  return service.events.where((event) {
    // Filter events for this field
    return event.data?['field_id'] == fieldId ||
        event.subject?.contains('fields.$fieldId') == true;
  });
});

/// Weather alerts provider
/// مزود تنبيهات الطقس
final weatherAlertsProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  // Subscribe to weather alerts
  service.subscribe(['weather', 'alerts']);

  return service.events.where((event) {
    return event.eventType == 'weather.alert' ||
        event.eventType == 'weather.updated';
  });
});

/// Chat messages provider for a specific room
/// مزود رسائل الدردشة لغرفة معينة
final chatMessagesProvider = StreamProvider.family<WebSocketEvent, String>((ref, roomId) {
  final service = ref.watch(webSocketServiceProvider);

  // Subscribe to chat room
  service.subscribeToRoom('chat:$roomId');

  return service.events.where((event) {
    return event.eventType?.startsWith('chat.') == true &&
        event.data?['room_id'] == roomId;
  });
});

/// Inventory alerts provider
/// مزود تنبيهات المخزون
final inventoryAlertsProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  return service.events.where((event) {
    return event.eventType == 'inventory.low_stock' ||
        event.eventType == 'inventory.out_of_stock';
  });
});

/// Crop health alerts provider
/// مزود تنبيهات صحة المحصول
final cropHealthAlertsProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  return service.events.where((event) {
    return event.eventType == 'crop.disease.detected' ||
        event.eventType == 'crop.pest.detected' ||
        event.eventType == 'crop.health.alert';
  });
});

/// Task updates provider
/// مزود تحديثات المهام
final taskUpdatesProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  return service.events.where((event) {
    return event.eventType?.startsWith('task.') == true;
  });
});

/// IoT sensor readings provider for a field
/// مزود قراءات المستشعرات لحقل معين
final iotReadingsProvider = StreamProvider.family<WebSocketEvent, String>((ref, fieldId) {
  final service = ref.watch(webSocketServiceProvider);

  // Subscribe to field's IoT events
  service.subscribeToRoom('field:$fieldId');

  return service.events.where((event) {
    return event.eventType?.startsWith('iot.') == true &&
        event.data?['field_id'] == fieldId;
  });
});

/// Satellite imagery updates provider
/// مزود تحديثات الصور الفضائية
final satelliteUpdatesProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  return service.events.where((event) {
    return event.eventType == 'satellite.ready' ||
        event.eventType == 'satellite.processing' ||
        event.eventType == 'satellite.failed';
  });
});

/// NDVI analysis updates provider
/// مزود تحديثات تحليل NDVI
final ndviUpdatesProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  return service.events.where((event) {
    return event.eventType == 'ndvi.updated' ||
        event.eventType == 'ndvi.analysis.ready';
  });
});

/// Spray timing alerts provider
/// مزود تنبيهات توقيت الرش
final sprayAlertsProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  return service.events.where((event) {
    return event.eventType == 'spray.window.optimal' ||
        event.eventType == 'spray.window.warning' ||
        event.eventType == 'spray.scheduled';
  });
});

/// All high-priority alerts provider
/// مزود جميع التنبيهات ذات الأولوية العالية
final highPriorityAlertsProvider = StreamProvider<WebSocketEvent>((ref) {
  final service = ref.watch(webSocketServiceProvider);

  // Subscribe to alerts room
  service.subscribe(['alerts']);

  return service.events.where((event) {
    return event.priority == 'high' || event.priority == 'critical';
  });
});

/// WebSocket connection manager
/// مدير اتصال WebSocket
class WebSocketConnectionNotifier extends StateNotifier<ConnectionState> {
  final WebSocketService _service;

  WebSocketConnectionNotifier(this._service) : super(ConnectionState.disconnected) {
    // Listen to connection state changes
    _service.connectionState.listen((newState) {
      state = newState;
    });
  }

  /// Connect to WebSocket
  Future<void> connect() async {
    await _service.connect();
  }

  /// Disconnect from WebSocket
  Future<void> disconnect() async {
    await _service.disconnect();
  }

  /// Reconnect to WebSocket
  /// Call this when the auth token is refreshed to reconnect with new credentials
  Future<void> reconnect() async {
    await _service.disconnect();
    await Future.delayed(const Duration(milliseconds: 500));
    await _service.connect();
  }

  /// Refresh connection after token update
  /// This method ensures the WebSocket uses the latest access token
  Future<void> refreshConnection() async {
    if (state == ConnectionState.connected) {
      AppLogger.i('Refreshing WebSocket connection with new token', tag: 'WS');
      await reconnect();
    }
  }
}

/// WebSocket connection manager provider
final webSocketConnectionProvider =
    StateNotifierProvider<WebSocketConnectionNotifier, ConnectionState>((ref) {
  final service = ref.watch(webSocketServiceProvider);
  final notifier = WebSocketConnectionNotifier(service);

  // Listen for auth state changes to handle token refresh
  String? lastToken;
  ref.listen<AuthState>(authStateProvider, (previous, next) {
    final newToken = next.accessToken;

    // If token changed and we have a connection, reconnect with new token
    if (lastToken != null &&
        newToken != null &&
        lastToken != newToken &&
        notifier.state == ConnectionState.connected) {
      AppLogger.i('Token refreshed, reconnecting WebSocket', tag: 'WS');
      notifier.refreshConnection();
    }

    lastToken = newToken;
  });

  return notifier;
});
