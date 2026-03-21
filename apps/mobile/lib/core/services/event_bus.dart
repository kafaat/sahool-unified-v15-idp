/// SAHOOL Event Bus
/// ناقل الأحداث المحلي للتواصل بين الميزات
///
/// Features:
/// - Cross-feature communication
/// - Event type definitions
/// - Subscription management
/// - Event history (optional)
/// - Priority-based delivery
library;

import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';

/// Event types for the application
/// أنواع الأحداث في التطبيق
enum EventType {
  // Field Events - أحداث الحقول
  fieldCreated,
  fieldUpdated,
  fieldDeleted,
  fieldSelected,
  fieldSyncCompleted,

  // Task Events - أحداث المهام
  taskCreated,
  taskUpdated,
  taskCompleted,
  taskDeleted,
  taskReminder,

  // Weather Events - أحداث الطقس
  weatherUpdated,
  weatherAlert,
  forecastUpdated,

  // Irrigation Events - أحداث الري
  irrigationScheduled,
  irrigationCompleted,
  irrigationReminder,
  waterBalanceUpdated,

  // NDVI/Satellite Events - أحداث الأقمار الصناعية
  ndviUpdated,
  imageryAvailable,
  healthAssessmentReady,

  // Advisory Events - أحداث الاستشارات
  advisoryReceived,
  recommendationReady,
  diagnosisComplete,

  // Notification Events - أحداث الإشعارات
  notificationReceived,
  notificationRead,
  notificationsCleared,

  // Sync Events - أحداث المزامنة
  syncStarted,
  syncCompleted,
  syncFailed,
  syncRequired,
  offlineQueueUpdated,

  // Auth Events - أحداث المصادقة
  userLoggedIn,
  userLoggedOut,
  tokenRefreshed,
  sessionExpired,

  // Connection Events - أحداث الاتصال
  connectionStateChanged,
  networkAvailable,
  networkUnavailable,

  // Navigation Events - أحداث التنقل
  navigationRequested,
  deepLinkReceived,

  // Error Events - أحداث الأخطاء
  errorOccurred,
  criticalError,

  // Custom/Generic Events
  custom,
}

/// Event priority levels
enum EventPriority { low, normal, high, critical }

/// Application event model
/// نموذج حدث التطبيق
class AppEvent {
  final EventType type;
  final Map<String, dynamic> data;
  final DateTime timestamp;
  final String? source;
  final EventPriority priority;
  final String? correlationId;

  AppEvent({
    required this.type,
    this.data = const {},
    DateTime? timestamp,
    this.source,
    this.priority = EventPriority.normal,
    this.correlationId,
  }) : timestamp = timestamp ?? DateTime.now();

  /// Create a field event
  factory AppEvent.field({
    required EventType type,
    required String fieldId,
    Map<String, dynamic>? additionalData,
  }) {
    return AppEvent(
      type: type,
      data: {
        'field_id': fieldId,
        if (additionalData != null) ...additionalData,
      },
    );
  }

  /// Create a task event
  factory AppEvent.task({
    required EventType type,
    required String taskId,
    String? fieldId,
    Map<String, dynamic>? additionalData,
  }) {
    return AppEvent(
      type: type,
      data: {
        'task_id': taskId,
        if (fieldId != null) 'field_id': fieldId,
        if (additionalData != null) ...additionalData,
      },
    );
  }

  /// Create a notification event
  factory AppEvent.notification({
    required String notificationId,
    String? title,
    String? body,
    Map<String, dynamic>? additionalData,
  }) {
    return AppEvent(
      type: EventType.notificationReceived,
      data: {
        'notification_id': notificationId,
        if (title != null) 'title': title,
        if (body != null) 'body': body,
        if (additionalData != null) ...additionalData,
      },
    );
  }

  /// Create an error event
  factory AppEvent.error({
    required String message,
    Object? error,
    StackTrace? stackTrace,
    bool isCritical = false,
  }) {
    return AppEvent(
      type: isCritical ? EventType.criticalError : EventType.errorOccurred,
      priority: isCritical ? EventPriority.critical : EventPriority.high,
      data: {
        'message': message,
        if (error != null) 'error': error.toString(),
        if (stackTrace != null) 'stack_trace': stackTrace.toString(),
      },
    );
  }

  /// Create a sync event
  factory AppEvent.sync({
    required EventType type,
    int? itemCount,
    String? entityType,
    Map<String, dynamic>? additionalData,
  }) {
    return AppEvent(
      type: type,
      data: {
        if (itemCount != null) 'item_count': itemCount,
        if (entityType != null) 'entity_type': entityType,
        if (additionalData != null) ...additionalData,
      },
    );
  }

  @override
  String toString() => 'AppEvent($type, data: $data)';
}

/// Event subscription handle
class EventSubscription {
  final EventType type;
  final void Function(AppEvent) callback;
  final String id;
  bool _isActive = true;

  EventSubscription({
    required this.type,
    required this.callback,
    required this.id,
  });

  bool get isActive => _isActive;

  void cancel() {
    _isActive = false;
  }
}

/// Event Bus for cross-feature communication
/// ناقل الأحداث للتواصل بين الميزات
class EventBus {
  final Map<EventType, List<EventSubscription>> _subscriptions = {};
  final StreamController<AppEvent> _eventController = StreamController<AppEvent>.broadcast();

  // Event history (limited size)
  final List<AppEvent> _eventHistory = [];
  static const int _maxHistorySize = 100;
  bool _keepHistory = false;

  /// Stream of all events
  Stream<AppEvent> get events => _eventController.stream;

  /// Get event history
  List<AppEvent> get history => List.unmodifiable(_eventHistory);

  /// Enable/disable event history
  set keepHistory(bool value) => _keepHistory = value;

  /// Subscribe to an event type
  /// الاشتراك في نوع حدث
  EventSubscription subscribe(EventType type, void Function(AppEvent) callback) {
    final subscription = EventSubscription(
      type: type,
      callback: callback,
      id: '${type.name}_${DateTime.now().millisecondsSinceEpoch}',
    );

    _subscriptions[type] ??= [];
    _subscriptions[type]!.add(subscription);

    AppLogger.d('Subscribed to event: ${type.name}', tag: 'EventBus');

    return subscription;
  }

  /// Subscribe to multiple event types
  /// الاشتراك في أنواع أحداث متعددة
  List<EventSubscription> subscribeAll(
    List<EventType> types,
    void Function(AppEvent) callback,
  ) {
    return types.map((type) => subscribe(type, callback)).toList();
  }

  /// Unsubscribe from an event
  /// إلغاء الاشتراك من حدث
  void unsubscribe(EventSubscription subscription) {
    subscription.cancel();
    _subscriptions[subscription.type]?.remove(subscription);
    AppLogger.d('Unsubscribed from event: ${subscription.type.name}', tag: 'EventBus');
  }

  /// Unsubscribe all subscriptions for a type
  /// إلغاء جميع الاشتراكات لنوع معين
  void unsubscribeAll(EventType type) {
    final subs = _subscriptions[type];
    if (subs != null) {
      for (final sub in subs) {
        sub.cancel();
      }
      _subscriptions[type]!.clear();
    }
  }

  /// Emit an event
  /// إرسال حدث
  void emit(AppEvent event) {
    // Add to history if enabled
    if (_keepHistory) {
      _eventHistory.add(event);
      if (_eventHistory.length > _maxHistorySize) {
        _eventHistory.removeAt(0);
      }
    }

    // Emit to stream
    _eventController.add(event);

    // Call registered callbacks
    final subscriptions = _subscriptions[event.type];
    if (subscriptions != null) {
      // Sort by priority for critical/high priority events
      final sortedSubs = event.priority == EventPriority.critical ||
              event.priority == EventPriority.high
          ? subscriptions.toList()
          : subscriptions;

      for (final subscription in sortedSubs) {
        if (subscription.isActive) {
          try {
            subscription.callback(event);
          } catch (e, stackTrace) {
            AppLogger.e(
              'Error in event handler for ${event.type}',
              tag: 'EventBus',
              error: e,
              stackTrace: stackTrace,
            );
          }
        }
      }
    }

    // Log high priority events
    if (event.priority == EventPriority.high || event.priority == EventPriority.critical) {
      AppLogger.i('Event emitted: ${event.type.name}', tag: 'EventBus');
    }
  }

  /// Emit multiple events
  /// إرسال أحداث متعددة
  void emitAll(List<AppEvent> events) {
    for (final event in events) {
      emit(event);
    }
  }

  /// Get stream filtered by event type
  /// الحصول على تدفق مرشح حسب نوع الحدث
  Stream<AppEvent> on(EventType type) {
    return _eventController.stream.where((event) => event.type == type);
  }

  /// Get stream filtered by multiple event types
  /// الحصول على تدفق مرشح حسب أنواع أحداث متعددة
  Stream<AppEvent> onAny(List<EventType> types) {
    return _eventController.stream.where((event) => types.contains(event.type));
  }

  /// Get the last event of a specific type
  /// الحصول على آخر حدث من نوع معين
  AppEvent? getLastEvent(EventType type) {
    if (!_keepHistory) return null;

    for (int i = _eventHistory.length - 1; i >= 0; i--) {
      if (_eventHistory[i].type == type) {
        return _eventHistory[i];
      }
    }
    return null;
  }

  /// Get events of a specific type from history
  /// الحصول على أحداث من نوع معين من السجل
  List<AppEvent> getEvents(EventType type, {int? limit}) {
    if (!_keepHistory) return [];

    final events = _eventHistory.where((e) => e.type == type).toList();
    if (limit != null && events.length > limit) {
      return events.sublist(events.length - limit);
    }
    return events;
  }

  /// Clear event history
  /// مسح سجل الأحداث
  void clearHistory() {
    _eventHistory.clear();
  }

  /// Get subscription count for a type
  int getSubscriptionCount(EventType type) {
    return _subscriptions[type]?.where((s) => s.isActive).length ?? 0;
  }

  /// Dispose resources
  void dispose() {
    for (final subs in _subscriptions.values) {
      for (final sub in subs) {
        sub.cancel();
      }
    }
    _subscriptions.clear();
    _eventHistory.clear();
    _eventController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Event Bus Provider
final eventBusProvider = Provider<EventBus>((ref) {
  final eventBus = EventBus();
  ref.onDispose(() => eventBus.dispose());
  return eventBus;
});

/// All Events Stream Provider
final eventsStreamProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.events;
});

/// Filtered Events Stream Provider
final filteredEventsProvider = StreamProvider.family<AppEvent, EventType>((ref, type) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.on(type);
});

/// Field Events Stream Provider
final fieldEventsProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.onAny([
    EventType.fieldCreated,
    EventType.fieldUpdated,
    EventType.fieldDeleted,
    EventType.fieldSelected,
  ]);
});

/// Task Events Stream Provider
final taskEventsProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.onAny([
    EventType.taskCreated,
    EventType.taskUpdated,
    EventType.taskCompleted,
    EventType.taskDeleted,
  ]);
});

/// Notification Events Stream Provider
final notificationEventsProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.on(EventType.notificationReceived);
});

/// Sync Events Stream Provider
final syncEventsProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.onAny([
    EventType.syncStarted,
    EventType.syncCompleted,
    EventType.syncFailed,
    EventType.syncRequired,
  ]);
});

/// Error Events Stream Provider
final errorEventsProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.onAny([
    EventType.errorOccurred,
    EventType.criticalError,
  ]);
});

/// Connection Events Stream Provider
final connectionEventsProvider = StreamProvider<AppEvent>((ref) {
  final eventBus = ref.watch(eventBusProvider);
  return eventBus.onAny([
    EventType.connectionStateChanged,
    EventType.networkAvailable,
    EventType.networkUnavailable,
  ]);
});
