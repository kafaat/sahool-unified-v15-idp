/// SAHOOL Analytics Service - Main analytics service with provider abstraction
/// خدمة التحليلات الرئيسية مع طبقة تجريد المزودين
///
/// Privacy-respecting analytics for tracking app usage and user behavior.
/// Supports multiple analytics providers with offline-first architecture.
///
/// Features:
/// - Multiple provider support (Firebase, custom backend, console)
/// - Offline event queuing
/// - Automatic PII filtering
/// - User property tracking
/// - Screen view tracking
/// - Custom event tracking
/// - Performance monitoring
library;

import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../sync/network_status.dart';
import '../utils/app_logger.dart';
import '../utils/pii_filter.dart';
import 'analytics_event.dart';
import 'user_properties.dart';
import 'offline_analytics_queue.dart';

// =============================================================================
// Analytics Provider Interface - واجهة مزود التحليلات
// =============================================================================

/// Abstract interface for analytics providers
///
/// Implement this interface to add support for different analytics services.
abstract class AnalyticsProvider {
  /// Provider name for identification
  String get name;

  /// Whether the provider is enabled
  bool get isEnabled;

  /// Initialize the provider
  Future<void> initialize();

  /// Log an analytics event
  Future<void> logEvent(AnalyticsEvent event);

  /// Log multiple events (batch)
  Future<void> logEvents(List<AnalyticsEvent> events);

  /// Set user properties
  Future<void> setUserProperties(AnalyticsUserProperties properties);

  /// Set user ID (anonymous)
  Future<void> setUserId(String? userId);

  /// Log screen view
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  });

  /// Enable/disable the provider
  Future<void> setEnabled(bool enabled);

  /// Reset analytics data
  Future<void> reset();
}

// =============================================================================
// Console Analytics Provider - مزود التحليلات للكونسول
// =============================================================================

/// Console-based analytics provider for development
class ConsoleAnalyticsProvider implements AnalyticsProvider {
  bool _enabled = true;

  @override
  String get name => 'Console';

  @override
  bool get isEnabled => _enabled;

  @override
  Future<void> initialize() async {
    debugPrint('[Analytics:Console] Initialized');
  }

  @override
  Future<void> logEvent(AnalyticsEvent event) async {
    if (!_enabled) return;
    debugPrint(
      '[Analytics:Console] Event: ${event.name} | '
      'Category: ${event.category.name} | '
      'Params: ${event.parameters}',
    );
  }

  @override
  Future<void> logEvents(List<AnalyticsEvent> events) async {
    for (final event in events) {
      await logEvent(event);
    }
  }

  @override
  Future<void> setUserProperties(AnalyticsUserProperties properties) async {
    if (!_enabled) return;
    debugPrint('[Analytics:Console] User properties set: ${properties.toMap()}');
  }

  @override
  Future<void> setUserId(String? userId) async {
    if (!_enabled) return;
    debugPrint('[Analytics:Console] User ID set: $userId');
  }

  @override
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  }) async {
    if (!_enabled) return;
    debugPrint('[Analytics:Console] Screen view: $screenName (class: $screenClass)');
  }

  @override
  Future<void> setEnabled(bool enabled) async {
    _enabled = enabled;
    debugPrint('[Analytics:Console] ${enabled ? 'Enabled' : 'Disabled'}');
  }

  @override
  Future<void> reset() async {
    debugPrint('[Analytics:Console] Reset');
  }
}

// =============================================================================
// Backend Analytics Provider - مزود التحليلات للخادم الخلفي
// =============================================================================

/// HTTP-based analytics provider for custom backend
///
/// Sends events to SAHOOL analytics backend service.
class BackendAnalyticsProvider implements AnalyticsProvider {
  final String baseUrl;
  bool _enabled = true;

  BackendAnalyticsProvider({
    this.baseUrl = '/api/v1/analytics',
  });

  @override
  String get name => 'Backend';

  @override
  bool get isEnabled => _enabled;

  @override
  Future<void> initialize() async {
    AppLogger.i('Backend analytics provider initialized', tag: 'ANALYTICS');
  }

  @override
  Future<void> logEvent(AnalyticsEvent event) async {
    if (!_enabled) return;

    // In production, send to backend API
    // For now, just log
    AppLogger.d('Backend event', tag: 'ANALYTICS', data: {
      'event': event.name,
      'params': event.parameters,
    });
  }

  @override
  Future<void> logEvents(List<AnalyticsEvent> events) async {
    if (!_enabled) return;

    // In production, batch send to backend API
    AppLogger.d('Backend batch events', tag: 'ANALYTICS', data: {
      'count': events.length,
    });
  }

  @override
  Future<void> setUserProperties(AnalyticsUserProperties properties) async {
    if (!_enabled) return;

    AppLogger.d('Backend user properties', tag: 'ANALYTICS', data: properties.toMap());
  }

  @override
  Future<void> setUserId(String? userId) async {
    if (!_enabled) return;

    AppLogger.d('Backend user ID', tag: 'ANALYTICS', data: {'user_id': userId});
  }

  @override
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
  }) async {
    if (!_enabled) return;

    AppLogger.d('Backend screen view', tag: 'ANALYTICS', data: {
      'screen': screenName,
      'class': screenClass,
    });
  }

  @override
  Future<void> setEnabled(bool enabled) async {
    _enabled = enabled;
  }

  @override
  Future<void> reset() async {
    AppLogger.i('Backend analytics reset', tag: 'ANALYTICS');
  }
}

// =============================================================================
// Analytics Service - خدمة التحليلات
// =============================================================================

/// Main analytics service singleton
///
/// Provides a unified interface for analytics tracking with:
/// - Multiple provider support
/// - Offline event queuing
/// - User property management
/// - PII filtering
class AnalyticsService {
  static AnalyticsService? _instance;
  static AnalyticsService get instance {
    _instance ??= AnalyticsService._();
    return _instance!;
  }

  AnalyticsService._();

  // Configuration
  static const String _prefsKeyEnabled = 'analytics_enabled';
  static const String _prefsKeyUserId = 'analytics_user_id';
  static const String _prefsKeySessionId = 'analytics_session_id';
  static const String _prefsKeyUserProps = 'analytics_user_props';

  // State
  bool _initialized = false;
  bool _enabled = true;
  String? _userId;
  String? _sessionId;
  AnalyticsUserProperties? _userProperties;

  // Providers
  final List<AnalyticsProvider> _providers = [];

  // Offline queue
  late OfflineAnalyticsQueue _offlineQueue;

  // Session tracking
  DateTime? _sessionStartTime;
  int _eventsThisSession = 0;

  // Stream controllers
  final _eventController = StreamController<AnalyticsEvent>.broadcast();

  /// Stream of logged events (for debugging/monitoring)
  Stream<AnalyticsEvent> get eventStream => _eventController.stream;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization - التهيئة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the analytics service
  ///
  /// [providers] - List of analytics providers to use
  /// [enableOfflineQueue] - Whether to enable offline event queuing
  Future<void> initialize({
    List<AnalyticsProvider>? providers,
    bool enableOfflineQueue = true,
  }) async {
    if (_initialized) {
      AppLogger.w('Analytics service already initialized', tag: 'ANALYTICS');
      return;
    }

    try {
      // Load saved preferences
      final prefs = await SharedPreferences.getInstance();
      _enabled = prefs.getBool(_prefsKeyEnabled) ?? true;
      _userId = prefs.getString(_prefsKeyUserId);

      // Generate or retrieve session ID
      _sessionId = _generateSessionId();
      _sessionStartTime = DateTime.now();

      // Load saved user properties
      final userPropsJson = prefs.getString(_prefsKeyUserProps);
      if (userPropsJson != null) {
        try {
          final propsMap = PiiFilter.sanitize(userPropsJson);
          if (propsMap is Map<String, dynamic>) {
            _userProperties = AnalyticsUserProperties.fromJson(propsMap);
          }
        } catch (e) {
          AppLogger.w('Failed to load user properties', tag: 'ANALYTICS', data: {'error': e.toString()});
        }
      }

      // Add providers
      if (providers != null && providers.isNotEmpty) {
        _providers.addAll(providers);
      } else {
        // Add default console provider in debug mode
        if (kDebugMode) {
          _providers.add(ConsoleAnalyticsProvider());
        }
        // Always add backend provider
        _providers.add(BackendAnalyticsProvider());
      }

      // Initialize providers
      for (final provider in _providers) {
        try {
          await provider.initialize();
          if (_userId != null) {
            await provider.setUserId(_userId);
          }
          if (_userProperties != null) {
            await provider.setUserProperties(_userProperties!);
          }
          AppLogger.i('Analytics provider initialized', tag: 'ANALYTICS', data: {
            'provider': provider.name,
          });
        } catch (e) {
          AppLogger.e('Failed to initialize analytics provider', tag: 'ANALYTICS', error: e);
        }
      }

      // Initialize offline queue
      if (enableOfflineQueue) {
        _offlineQueue = OfflineAnalyticsQueue(
          config: const OfflineAnalyticsQueueConfig(
            maxQueueSize: 1000,
            maxEventAgeDays: 7,
            batchSize: 50,
            autoProcessEnabled: true,
            autoProcessIntervalMinutes: 5,
          ),
          onSendEvents: _sendEventsToProviders,
        );
        await _offlineQueue.initialize();
      }

      _initialized = true;

      // Log app launch event
      await logEvent(AnalyticsEvent.create(
        name: PerformanceEvents.appLaunch,
        category: AnalyticsEventCategory.performance,
        sessionId: _sessionId,
      ));

      AppLogger.i('Analytics service initialized', tag: 'ANALYTICS', data: {
        'providers': _providers.map((p) => p.name).toList(),
        'enabled': _enabled,
        'offline_queue': enableOfflineQueue,
      });
    } catch (e) {
      AppLogger.e('Failed to initialize analytics service', tag: 'ANALYTICS', error: e);
    }
  }

  /// Dispose and clean up resources
  void dispose() {
    _eventController.close();
    _offlineQueue.dispose();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Event Logging - تسجيل الأحداث
  // ═══════════════════════════════════════════════════════════════════════════

  /// Log an analytics event
  Future<void> logEvent(AnalyticsEvent event) async {
    if (!_initialized || !_enabled) return;

    try {
      // Add session ID if not set
      final eventWithSession = event.sessionId == null
          ? AnalyticsEvent(
              id: event.id,
              name: event.name,
              category: event.category,
              parameters: event.parameters,
              timestamp: event.timestamp,
              sessionId: _sessionId,
            )
          : event;

      _eventsThisSession++;

      // Emit to stream for monitoring
      if (!_eventController.isClosed) {
        _eventController.add(eventWithSession);
      }

      // Check network status
      final isOnline = await NetworkStatus.instance.isConnected;

      if (isOnline) {
        // Send directly to providers
        await _sendEventToProviders(eventWithSession);
      } else {
        // Queue for later
        await _offlineQueue.enqueue(eventWithSession);
      }

      AppLogger.d('Event logged', tag: 'ANALYTICS', data: {
        'event': event.name,
        'online': isOnline,
      });
    } catch (e) {
      AppLogger.e('Failed to log event', tag: 'ANALYTICS', error: e);
    }
  }

  /// Log a screen view event
  Future<void> logScreenView({
    required String screenName,
    String? screenClass,
    Map<String, dynamic>? additionalParams,
  }) async {
    if (!_initialized || !_enabled) return;

    try {
      // Log to providers directly
      for (final provider in _providers) {
        if (provider.isEnabled) {
          await provider.logScreenView(
            screenName: screenName,
            screenClass: screenClass,
          );
        }
      }

      // Also log as event for offline queue
      await logEvent(AnalyticsEvent.screenView(
        screenName: screenName,
        screenClass: screenClass,
        additionalParams: additionalParams,
        sessionId: _sessionId,
      ));
    } catch (e) {
      AppLogger.e('Failed to log screen view', tag: 'ANALYTICS', error: e);
    }
  }

  /// Log a button tap event
  Future<void> logButtonTap({
    required String buttonId,
    String? buttonText,
    String? screenName,
  }) async {
    await logEvent(AnalyticsEvent.buttonTap(
      buttonId: buttonId,
      buttonText: buttonText,
      screenName: screenName,
      sessionId: _sessionId,
    ));
  }

  /// Log a form submission event
  Future<void> logFormSubmit({
    required String formName,
    bool? success,
    String? errorReason,
  }) async {
    await logEvent(AnalyticsEvent.formSubmit(
      formName: formName,
      success: success,
      errorReason: errorReason,
      sessionId: _sessionId,
    ));
  }

  /// Log a field viewed event
  Future<void> logFieldViewed({
    required String fieldId,
    String? cropType,
    double? areaHectares,
  }) async {
    await logEvent(AnalyticsEvent.fieldViewed(
      fieldId: fieldId,
      cropType: cropType,
      areaHectares: areaHectares,
      sessionId: _sessionId,
    ));

    // Update user properties - mark map feature as used
    await _updateFeatureUsage(usesMap: true);
  }

  /// Log a field created event
  Future<void> logFieldCreated({
    required String fieldId,
    String? cropType,
    double? areaHectares,
    bool? offlineCreated,
  }) async {
    await logEvent(AnalyticsEvent.fieldCreated(
      fieldId: fieldId,
      cropType: cropType,
      areaHectares: areaHectares,
      offlineCreated: offlineCreated,
      sessionId: _sessionId,
    ));

    if (offlineCreated == true) {
      await _updateFeatureUsage(usesOfflineMode: true);
    }
  }

  /// Log a weather checked event
  Future<void> logWeatherChecked({
    String? source,
    bool? isOfflineData,
  }) async {
    await logEvent(AnalyticsEvent.weatherChecked(
      source: source,
      isOfflineData: isOfflineData,
      sessionId: _sessionId,
    ));

    await _updateFeatureUsage(usesWeather: true);
    if (isOfflineData == true) {
      await _updateFeatureUsage(usesOfflineMode: true);
    }
  }

  /// Log an NDVI analyzed event
  Future<void> logNdviAnalyzed({
    required String fieldId,
    double? ndviValue,
    String? analysisType,
  }) async {
    await logEvent(AnalyticsEvent.ndviAnalyzed(
      fieldId: fieldId,
      ndviValue: ndviValue,
      analysisType: analysisType,
      sessionId: _sessionId,
    ));

    await _updateFeatureUsage(usesNdvi: true);
  }

  /// Log an irrigation scheduled event
  Future<void> logIrrigationScheduled({
    required String fieldId,
    String? irrigationType,
    double? waterAmount,
  }) async {
    await logEvent(AnalyticsEvent.irrigationScheduled(
      fieldId: fieldId,
      irrigationType: irrigationType,
      waterAmount: waterAmount,
      sessionId: _sessionId,
    ));

    await _updateFeatureUsage(usesIrrigation: true);
  }

  /// Log a map interaction event
  Future<void> logMapInteraction({
    required String interactionType,
    String? layerType,
    bool? isOffline,
  }) async {
    await logEvent(AnalyticsEvent.mapInteraction(
      interactionType: interactionType,
      layerType: layerType,
      isOffline: isOffline,
      sessionId: _sessionId,
    ));

    await _updateFeatureUsage(usesMap: true);
    if (isOffline == true) {
      await _updateFeatureUsage(usesOfflineMode: true);
    }
  }

  /// Log a sync completed event
  Future<void> logSyncCompleted({
    required int itemCount,
    required Duration duration,
    bool? hadConflicts,
  }) async {
    await logEvent(AnalyticsEvent.syncCompleted(
      itemCount: itemCount,
      duration: duration,
      hadConflicts: hadConflicts,
      sessionId: _sessionId,
    ));
  }

  /// Log a sync failed event
  Future<void> logSyncFailed({
    required String errorType,
    String? errorCode,
    int? retryCount,
  }) async {
    await logEvent(AnalyticsEvent.syncFailed(
      errorType: errorType,
      errorCode: errorCode,
      retryCount: retryCount,
      sessionId: _sessionId,
    ));
  }

  /// Log an error event
  Future<void> logError({
    required String errorType,
    String? errorCode,
    String? errorMessage,
    String? screenName,
    bool? isFatal,
  }) async {
    await logEvent(AnalyticsEvent.error(
      errorType: errorType,
      errorCode: errorCode,
      errorMessage: errorMessage,
      screenName: screenName,
      isFatal: isFatal,
      sessionId: _sessionId,
    ));
  }

  /// Log a performance event
  Future<void> logPerformance({
    required String operation,
    required Duration duration,
    bool? success,
  }) async {
    await logEvent(AnalyticsEvent.performance(
      operation: operation,
      duration: duration,
      success: success,
      sessionId: _sessionId,
    ));
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // User Properties - خصائص المستخدم
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set the anonymous user ID
  Future<void> setUserId(String? userId) async {
    _userId = userId;

    final prefs = await SharedPreferences.getInstance();
    if (userId != null) {
      await prefs.setString(_prefsKeyUserId, userId);
    } else {
      await prefs.remove(_prefsKeyUserId);
    }

    for (final provider in _providers) {
      if (provider.isEnabled) {
        await provider.setUserId(userId);
      }
    }

    AppLogger.i('User ID set', tag: 'ANALYTICS');
  }

  /// Set user properties
  Future<void> setUserProperties(AnalyticsUserProperties properties) async {
    _userProperties = properties;

    // Save to persistent storage
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_prefsKeyUserProps, properties.toJson().toString());

    // Update providers
    for (final provider in _providers) {
      if (provider.isEnabled) {
        await provider.setUserProperties(properties);
      }
    }

    AppLogger.i('User properties set', tag: 'ANALYTICS');
  }

  /// Update user properties with field statistics
  Future<void> updateFieldStats({
    required int fieldCount,
    required double totalArea,
    String? primaryCrop,
  }) async {
    if (_userProperties == null) return;

    final updated = _userProperties!.withFieldStats(
      fieldCount: fieldCount,
      totalArea: totalArea,
      primaryCrop: primaryCrop,
    );

    await setUserProperties(updated);
  }

  /// Get current user properties
  AnalyticsUserProperties? get userProperties => _userProperties;

  // ═══════════════════════════════════════════════════════════════════════════
  // Service Control - التحكم بالخدمة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Enable or disable analytics
  Future<void> setEnabled(bool enabled) async {
    _enabled = enabled;

    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_prefsKeyEnabled, enabled);

    for (final provider in _providers) {
      await provider.setEnabled(enabled);
    }

    AppLogger.i('Analytics ${enabled ? 'enabled' : 'disabled'}', tag: 'ANALYTICS');
  }

  /// Check if analytics is enabled
  bool get isEnabled => _enabled;

  /// Check if service is initialized
  bool get isInitialized => _initialized;

  /// Get current session ID
  String? get sessionId => _sessionId;

  /// Get events logged this session
  int get eventsThisSession => _eventsThisSession;

  /// Force process the offline queue
  Future<void> flushQueue() async {
    await _offlineQueue.processQueue();
  }

  /// Get offline queue statistics
  AnalyticsQueueStats getQueueStats() {
    return _offlineQueue.getStats();
  }

  /// Reset all analytics data
  Future<void> reset() async {
    _userId = null;
    _userProperties = null;
    _eventsThisSession = 0;

    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_prefsKeyUserId);
    await prefs.remove(_prefsKeyUserProps);

    await _offlineQueue.clear();

    for (final provider in _providers) {
      await provider.reset();
    }

    AppLogger.i('Analytics reset', tag: 'ANALYTICS');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Methods - طرق خاصة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate a unique session ID
  String _generateSessionId() {
    const uuid = Uuid();
    return uuid.v4();
  }

  /// Send event to all providers
  Future<void> _sendEventToProviders(AnalyticsEvent event) async {
    for (final provider in _providers) {
      if (provider.isEnabled) {
        try {
          await provider.logEvent(event);
        } catch (e) {
          AppLogger.e('Failed to send event to ${provider.name}', tag: 'ANALYTICS', error: e);
        }
      }
    }
  }

  /// Send events batch to all providers (for offline queue)
  Future<bool> _sendEventsToProviders(List<AnalyticsEvent> events) async {
    var success = true;

    for (final provider in _providers) {
      if (provider.isEnabled) {
        try {
          await provider.logEvents(events);
        } catch (e) {
          AppLogger.e('Failed to send batch to ${provider.name}', tag: 'ANALYTICS', error: e);
          success = false;
        }
      }
    }

    return success;
  }

  /// Update feature usage flags in user properties
  Future<void> _updateFeatureUsage({
    bool? usesOfflineMode,
    bool? usesNdvi,
    bool? usesIrrigation,
    bool? usesWeather,
    bool? usesVoice,
    bool? usesMap,
  }) async {
    if (_userProperties == null) return;

    final updated = _userProperties!.withFeatureUsage(
      offlineMode: usesOfflineMode,
      ndvi: usesNdvi,
      irrigation: usesIrrigation,
      weather: usesWeather,
      voice: usesVoice,
      map: usesMap,
    );

    await setUserProperties(updated);
  }
}

// =============================================================================
// Riverpod Providers - مزودو Riverpod
// =============================================================================

/// Analytics service provider
final analyticsServiceProvider = Provider<AnalyticsService>((ref) {
  return AnalyticsService.instance;
});

/// Offline analytics queue provider
final analyticsQueueProvider = Provider<OfflineAnalyticsQueue>((ref) {
  final service = ref.watch(analyticsServiceProvider);
  return service._offlineQueue;
});

/// Analytics queue stats provider (auto-dispose)
final analyticsQueueStatsProvider = StreamProvider.autoDispose<AnalyticsQueueStats>((ref) {
  final service = ref.watch(analyticsServiceProvider);
  return service._offlineQueue.statusStream;
});

/// Analytics event stream provider (auto-dispose)
final analyticsEventStreamProvider = StreamProvider.autoDispose<AnalyticsEvent>((ref) {
  final service = ref.watch(analyticsServiceProvider);
  return service.eventStream;
});

/// Analytics enabled state provider
final analyticsEnabledProvider = StateProvider<bool>((ref) {
  final service = ref.watch(analyticsServiceProvider);
  return service.isEnabled;
});

// =============================================================================
// Analytics Observer - مراقب التحليلات
// =============================================================================

/// Route observer for automatic screen view tracking
///
/// Add this to your MaterialApp navigatorObservers to automatically
/// track screen views when navigating.
///
/// Example:
/// ```dart
/// MaterialApp(
///   navigatorObservers: [AnalyticsRouteObserver()],
/// )
/// ```
class AnalyticsRouteObserver extends NavigatorObserver {
  final AnalyticsService _analytics = AnalyticsService.instance;

  @override
  void didPush(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPush(route, previousRoute);
    _logScreenView(route);
  }

  @override
  void didReplace({Route<dynamic>? newRoute, Route<dynamic>? oldRoute}) {
    super.didReplace(newRoute: newRoute, oldRoute: oldRoute);
    if (newRoute != null) {
      _logScreenView(newRoute);
    }
  }

  @override
  void didPop(Route<dynamic> route, Route<dynamic>? previousRoute) {
    super.didPop(route, previousRoute);
    if (previousRoute != null) {
      _logScreenView(previousRoute);
    }
  }

  void _logScreenView(Route<dynamic> route) {
    final screenName = route.settings.name;
    if (screenName != null && screenName.isNotEmpty) {
      _analytics.logScreenView(
        screenName: screenName,
        screenClass: route.runtimeType.toString(),
      );
    }
  }
}
