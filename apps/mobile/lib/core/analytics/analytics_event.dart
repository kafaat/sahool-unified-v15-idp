/// SAHOOL Analytics Events - Event models and types
/// نماذج وأنواع أحداث التحليلات
///
/// Privacy-respecting analytics events for tracking user interactions
/// without collecting personally identifiable information (PII).
///
/// Features:
/// - Predefined event types for common actions
/// - Parameter validation
/// - PII filtering
/// - Offline-first support
/// - Arabic/English bilingual events
library;

import '../utils/pii_filter.dart';

// =============================================================================
// Event Categories - فئات الأحداث
// =============================================================================

/// Main event categories for organizing analytics
enum AnalyticsEventCategory {
  /// Screen and navigation events - أحداث الشاشة والتنقل
  screen,

  /// User interaction events - أحداث تفاعل المستخدم
  userAction,

  /// Feature usage events - أحداث استخدام الميزات
  feature,

  /// Error and crash events - أحداث الأخطاء
  error,

  /// Sync and network events - أحداث المزامنة والشبكة
  sync,

  /// Performance events - أحداث الأداء
  performance,

  /// Engagement events - أحداث التفاعل
  engagement,

  /// Business events - أحداث الأعمال
  business,
}

// =============================================================================
// Predefined Event Names - أسماء الأحداث المحددة مسبقاً
// =============================================================================

/// Predefined screen view events
class ScreenEvents {
  static const String homeViewed = 'home_viewed';
  static const String fieldListViewed = 'field_list_viewed';
  static const String fieldDetailViewed = 'field_detail_viewed';
  static const String mapViewed = 'map_viewed';
  static const String weatherViewed = 'weather_viewed';
  static const String ndviViewed = 'ndvi_viewed';
  static const String irrigationViewed = 'irrigation_viewed';
  static const String settingsViewed = 'settings_viewed';
  static const String profileViewed = 'profile_viewed';
  static const String taskListViewed = 'task_list_viewed';
  static const String taskDetailViewed = 'task_detail_viewed';
  static const String notificationsViewed = 'notifications_viewed';
  static const String helpViewed = 'help_viewed';
  static const String reportViewed = 'report_viewed';
}

/// Predefined user action events
class UserActionEvents {
  // Field actions - إجراءات الحقول
  static const String fieldCreated = 'field_created';
  static const String fieldUpdated = 'field_updated';
  static const String fieldDeleted = 'field_deleted';
  static const String fieldViewed = 'field_viewed';
  static const String fieldBoundaryDrawn = 'field_boundary_drawn';
  static const String fieldShared = 'field_shared';

  // Task actions - إجراءات المهام
  static const String taskCreated = 'task_created';
  static const String taskCompleted = 'task_completed';
  static const String taskUpdated = 'task_updated';
  static const String taskDeleted = 'task_deleted';

  // Map actions - إجراءات الخريطة
  static const String mapInteraction = 'map_interaction';
  static const String mapZoom = 'map_zoom';
  static const String mapPan = 'map_pan';
  static const String mapLayerChanged = 'map_layer_changed';
  static const String mapDownloaded = 'map_downloaded';

  // Weather actions - إجراءات الطقس
  static const String weatherChecked = 'weather_checked';
  static const String weatherRefreshed = 'weather_refreshed';
  static const String weatherLocationChanged = 'weather_location_changed';

  // Button/form actions - إجراءات الأزرار والنماذج
  static const String buttonTapped = 'button_tapped';
  static const String formSubmitted = 'form_submitted';
  static const String formValidationError = 'form_validation_error';
  static const String searchPerformed = 'search_performed';
  static const String filterApplied = 'filter_applied';
  static const String sortApplied = 'sort_applied';

  // Navigation actions - إجراءات التنقل
  static const String tabSelected = 'tab_selected';
  static const String menuOpened = 'menu_opened';
  static const String backPressed = 'back_pressed';
  static const String deeplinkOpened = 'deeplink_opened';

  // Auth actions - إجراءات المصادقة
  static const String loginAttempt = 'login_attempt';
  static const String loginSuccess = 'login_success';
  static const String loginFailed = 'login_failed';
  static const String logoutPerformed = 'logout_performed';
  static const String sessionExpired = 'session_expired';
}

/// Predefined feature usage events
class FeatureEvents {
  // NDVI features - ميزات NDVI
  static const String ndviAnalyzed = 'ndvi_analyzed';
  static const String ndviHistoryViewed = 'ndvi_history_viewed';
  static const String ndviCompared = 'ndvi_compared';
  static const String ndviAlertSet = 'ndvi_alert_set';

  // Irrigation features - ميزات الري
  static const String irrigationScheduled = 'irrigation_scheduled';
  static const String irrigationCompleted = 'irrigation_completed';
  static const String irrigationCancelled = 'irrigation_cancelled';
  static const String irrigationRecommendationViewed = 'irrigation_recommendation_viewed';

  // Weather features - ميزات الطقس
  static const String forecastViewed = 'forecast_viewed';
  static const String alertsViewed = 'alerts_viewed';
  static const String radarViewed = 'radar_viewed';

  // Map features - ميزات الخريطة
  static const String offlineMapUsed = 'offline_map_used';
  static const String satelliteLayerUsed = 'satellite_layer_used';
  static const String measurementToolUsed = 'measurement_tool_used';
  static const String locationTracked = 'location_tracked';

  // Advisory features - ميزات الاستشارات
  static const String advisoryViewed = 'advisory_viewed';
  static const String advisoryFollowed = 'advisory_followed';
  static const String advisoryDismissed = 'advisory_dismissed';

  // Report features - ميزات التقارير
  static const String reportGenerated = 'report_generated';
  static const String reportExported = 'report_exported';
  static const String reportShared = 'report_shared';

  // Voice features - ميزات الصوت
  static const String voiceCommandUsed = 'voice_command_used';
  static const String voiceCommandSuccess = 'voice_command_success';
  static const String voiceCommandFailed = 'voice_command_failed';
}

/// Predefined sync events
class SyncEvents {
  static const String syncStarted = 'sync_started';
  static const String syncCompleted = 'sync_completed';
  static const String syncFailed = 'sync_failed';
  static const String syncConflict = 'sync_conflict';
  static const String syncConflictResolved = 'sync_conflict_resolved';
  static const String offlineQueueUpdated = 'offline_queue_updated';
  static const String dataDownloaded = 'data_downloaded';
  static const String dataUploaded = 'data_uploaded';
}

/// Predefined error events
class ErrorEvents {
  static const String appError = 'app_error';
  static const String networkError = 'network_error';
  static const String apiError = 'api_error';
  static const String databaseError = 'database_error';
  static const String authError = 'auth_error';
  static const String validationError = 'validation_error';
  static const String permissionDenied = 'permission_denied';
  static const String timeout = 'timeout';
  static const String crashDetected = 'crash_detected';
}

/// Predefined performance events
class PerformanceEvents {
  static const String appLaunch = 'app_launch';
  static const String screenLoadTime = 'screen_load_time';
  static const String apiResponseTime = 'api_response_time';
  static const String databaseQueryTime = 'database_query_time';
  static const String imageLoadTime = 'image_load_time';
  static const String memoryWarning = 'memory_warning';
  static const String frameDropped = 'frame_dropped';
}

// =============================================================================
// Analytics Event Model - نموذج حدث التحليلات
// =============================================================================

/// Analytics event with parameters
///
/// All events are sanitized to remove PII before being sent to analytics.
class AnalyticsEvent {
  /// Unique event ID (UUID)
  final String id;

  /// Event name (e.g., 'field_created', 'weather_checked')
  final String name;

  /// Event category for grouping
  final AnalyticsEventCategory category;

  /// Event parameters (sanitized)
  final Map<String, dynamic> parameters;

  /// Timestamp when event was created
  final DateTime timestamp;

  /// User session ID (anonymous)
  final String? sessionId;

  /// Whether event has been sent to analytics
  bool isSent;

  /// Number of retry attempts
  int retryCount;

  AnalyticsEvent({
    required this.id,
    required this.name,
    required this.category,
    Map<String, dynamic>? parameters,
    DateTime? timestamp,
    this.sessionId,
    this.isSent = false,
    this.retryCount = 0,
  })  : parameters = _sanitizeParameters(parameters ?? {}),
        timestamp = timestamp ?? DateTime.now();

  /// Factory constructor for creating events with auto-generated ID
  factory AnalyticsEvent.create({
    required String name,
    required AnalyticsEventCategory category,
    Map<String, dynamic>? parameters,
    String? sessionId,
  }) {
    return AnalyticsEvent(
      id: _generateEventId(),
      name: name,
      category: category,
      parameters: parameters,
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Screen View Events - أحداث عرض الشاشة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a screen view event
  factory AnalyticsEvent.screenView({
    required String screenName,
    String? screenClass,
    Map<String, dynamic>? additionalParams,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: 'screen_view',
      category: AnalyticsEventCategory.screen,
      parameters: {
        'screen_name': screenName,
        if (screenClass != null) 'screen_class': screenClass,
        ...?additionalParams,
      },
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // User Action Events - أحداث إجراءات المستخدم
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a button tap event
  factory AnalyticsEvent.buttonTap({
    required String buttonId,
    String? buttonText,
    String? screenName,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: UserActionEvents.buttonTapped,
      category: AnalyticsEventCategory.userAction,
      parameters: {
        'button_id': buttonId,
        if (buttonText != null) 'button_text': buttonText,
        if (screenName != null) 'screen_name': screenName,
      },
      sessionId: sessionId,
    );
  }

  /// Create a form submission event
  factory AnalyticsEvent.formSubmit({
    required String formName,
    bool? success,
    String? errorReason,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: UserActionEvents.formSubmitted,
      category: AnalyticsEventCategory.userAction,
      parameters: {
        'form_name': formName,
        if (success != null) 'success': success,
        if (errorReason != null) 'error_reason': errorReason,
      },
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Feature Usage Events - أحداث استخدام الميزات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a field viewed event
  factory AnalyticsEvent.fieldViewed({
    required String fieldId,
    String? cropType,
    double? areaHectares,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: UserActionEvents.fieldViewed,
      category: AnalyticsEventCategory.feature,
      parameters: {
        'field_id_hash': _hashId(fieldId),
        if (cropType != null) 'crop_type': cropType,
        if (areaHectares != null) 'area_range': _getAreaRange(areaHectares),
      },
      sessionId: sessionId,
    );
  }

  /// Create a field created event
  factory AnalyticsEvent.fieldCreated({
    required String fieldId,
    String? cropType,
    double? areaHectares,
    bool? offlineCreated,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: UserActionEvents.fieldCreated,
      category: AnalyticsEventCategory.feature,
      parameters: {
        'field_id_hash': _hashId(fieldId),
        if (cropType != null) 'crop_type': cropType,
        if (areaHectares != null) 'area_range': _getAreaRange(areaHectares),
        if (offlineCreated != null) 'offline_created': offlineCreated,
      },
      sessionId: sessionId,
    );
  }

  /// Create a weather checked event
  factory AnalyticsEvent.weatherChecked({
    String? source,
    bool? isOfflineData,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: UserActionEvents.weatherChecked,
      category: AnalyticsEventCategory.feature,
      parameters: {
        if (source != null) 'source': source,
        if (isOfflineData != null) 'is_offline_data': isOfflineData,
      },
      sessionId: sessionId,
    );
  }

  /// Create an NDVI analyzed event
  factory AnalyticsEvent.ndviAnalyzed({
    required String fieldId,
    double? ndviValue,
    String? analysisType,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: FeatureEvents.ndviAnalyzed,
      category: AnalyticsEventCategory.feature,
      parameters: {
        'field_id_hash': _hashId(fieldId),
        if (ndviValue != null) 'ndvi_range': _getNdviRange(ndviValue),
        if (analysisType != null) 'analysis_type': analysisType,
      },
      sessionId: sessionId,
    );
  }

  /// Create an irrigation scheduled event
  factory AnalyticsEvent.irrigationScheduled({
    required String fieldId,
    String? irrigationType,
    double? waterAmount,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: FeatureEvents.irrigationScheduled,
      category: AnalyticsEventCategory.feature,
      parameters: {
        'field_id_hash': _hashId(fieldId),
        if (irrigationType != null) 'irrigation_type': irrigationType,
        if (waterAmount != null) 'water_amount_range': _getWaterAmountRange(waterAmount),
      },
      sessionId: sessionId,
    );
  }

  /// Create a map interaction event
  factory AnalyticsEvent.mapInteraction({
    required String interactionType,
    String? layerType,
    bool? isOffline,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: UserActionEvents.mapInteraction,
      category: AnalyticsEventCategory.feature,
      parameters: {
        'interaction_type': interactionType,
        if (layerType != null) 'layer_type': layerType,
        if (isOffline != null) 'is_offline': isOffline,
      },
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sync Events - أحداث المزامنة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a sync completed event
  factory AnalyticsEvent.syncCompleted({
    required int itemCount,
    required Duration duration,
    bool? hadConflicts,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: SyncEvents.syncCompleted,
      category: AnalyticsEventCategory.sync,
      parameters: {
        'item_count_range': _getCountRange(itemCount),
        'duration_ms': duration.inMilliseconds,
        if (hadConflicts != null) 'had_conflicts': hadConflicts,
      },
      sessionId: sessionId,
    );
  }

  /// Create a sync failed event
  factory AnalyticsEvent.syncFailed({
    required String errorType,
    String? errorCode,
    int? retryCount,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: SyncEvents.syncFailed,
      category: AnalyticsEventCategory.sync,
      parameters: {
        'error_type': errorType,
        if (errorCode != null) 'error_code': errorCode,
        if (retryCount != null) 'retry_count': retryCount,
      },
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Error Events - أحداث الأخطاء
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create an error event
  factory AnalyticsEvent.error({
    required String errorType,
    String? errorCode,
    String? errorMessage,
    String? screenName,
    bool? isFatal,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: ErrorEvents.appError,
      category: AnalyticsEventCategory.error,
      parameters: {
        'error_type': errorType,
        if (errorCode != null) 'error_code': errorCode,
        // Sanitize error message to remove PII
        if (errorMessage != null) 'error_message': _sanitizeErrorMessage(errorMessage),
        if (screenName != null) 'screen_name': screenName,
        if (isFatal != null) 'is_fatal': isFatal,
      },
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Performance Events - أحداث الأداء
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a performance event
  factory AnalyticsEvent.performance({
    required String operation,
    required Duration duration,
    bool? success,
    String? sessionId,
  }) {
    return AnalyticsEvent.create(
      name: PerformanceEvents.apiResponseTime,
      category: AnalyticsEventCategory.performance,
      parameters: {
        'operation': operation,
        'duration_ms': duration.inMilliseconds,
        if (success != null) 'success': success,
      },
      sessionId: sessionId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Serialization - التسلسل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Convert to JSON map
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'category': category.name,
      'parameters': parameters,
      'timestamp': timestamp.toIso8601String(),
      if (sessionId != null) 'session_id': sessionId,
      'is_sent': isSent,
      'retry_count': retryCount,
    };
  }

  /// Create from JSON map
  factory AnalyticsEvent.fromJson(Map<String, dynamic> json) {
    return AnalyticsEvent(
      id: json['id'] as String,
      name: json['name'] as String,
      category: AnalyticsEventCategory.values.byName(json['category'] as String),
      parameters: Map<String, dynamic>.from(json['parameters'] as Map),
      timestamp: DateTime.tryParse(json['timestamp'] as String) ?? DateTime.now(),
      sessionId: json['session_id'] as String?,
      isSent: json['is_sent'] as bool? ?? false,
      retryCount: json['retry_count'] as int? ?? 0,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Helper Methods - طرق مساعدة خاصة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate unique event ID
  static String _generateEventId() {
    final now = DateTime.now();
    final random = now.microsecondsSinceEpoch.toRadixString(36);
    return 'evt_${now.millisecondsSinceEpoch}_$random';
  }

  /// Sanitize parameters to remove PII
  static Map<String, dynamic> _sanitizeParameters(Map<String, dynamic> params) {
    return PiiFilter.sanitize(params) as Map<String, dynamic>;
  }

  /// Hash ID for privacy (one-way hash)
  static String _hashId(String id) {
    // Simple hash - in production use proper crypto hash
    var hash = 0;
    for (var i = 0; i < id.length; i++) {
      hash = ((hash << 5) - hash) + id.codeUnitAt(i);
      hash = hash & 0x7FFFFFFF; // Convert to 32bit integer
    }
    return hash.toRadixString(16);
  }

  /// Get area range bucket for privacy
  static String _getAreaRange(double hectares) {
    if (hectares < 1) return '< 1 ha';
    if (hectares < 5) return '1-5 ha';
    if (hectares < 10) return '5-10 ha';
    if (hectares < 50) return '10-50 ha';
    if (hectares < 100) return '50-100 ha';
    return '> 100 ha';
  }

  /// Get NDVI range bucket for privacy
  static String _getNdviRange(double ndvi) {
    if (ndvi < 0.2) return 'very_low';
    if (ndvi < 0.4) return 'low';
    if (ndvi < 0.6) return 'medium';
    if (ndvi < 0.8) return 'high';
    return 'very_high';
  }

  /// Get water amount range bucket
  static String _getWaterAmountRange(double mm) {
    if (mm < 10) return '< 10 mm';
    if (mm < 25) return '10-25 mm';
    if (mm < 50) return '25-50 mm';
    if (mm < 100) return '50-100 mm';
    return '> 100 mm';
  }

  /// Get count range bucket
  static String _getCountRange(int count) {
    if (count < 5) return '1-5';
    if (count < 10) return '5-10';
    if (count < 25) return '10-25';
    if (count < 50) return '25-50';
    if (count < 100) return '50-100';
    return '> 100';
  }

  /// Sanitize error message to remove PII
  static String _sanitizeErrorMessage(String message) {
    final sanitized = PiiFilter.sanitize(message) as String;
    // Truncate to reasonable length
    if (sanitized.length > 200) {
      return '${sanitized.substring(0, 200)}...';
    }
    return sanitized;
  }

  @override
  String toString() {
    return 'AnalyticsEvent{name: $name, category: $category, timestamp: $timestamp}';
  }
}
