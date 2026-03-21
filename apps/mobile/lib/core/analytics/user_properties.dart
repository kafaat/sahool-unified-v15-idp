/// SAHOOL Analytics User Properties - Privacy-respecting user properties
/// خصائص المستخدم للتحليلات مع احترام الخصوصية
///
/// Tracks anonymous user properties for analytics without collecting PII.
/// All properties are anonymized and focus on behavioral patterns.
///
/// Features:
/// - Anonymous user identification
/// - Device and app properties
/// - Usage patterns tracking
/// - Privacy-first design
/// - No PII collection

import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:package_info_plus/package_info_plus.dart';
import '../utils/pii_filter.dart';

// =============================================================================
// User Property Keys - مفاتيح خصائص المستخدم
// =============================================================================

/// Standard user property keys
class UserPropertyKeys {
  // App properties - خصائص التطبيق
  static const String appVersion = 'app_version';
  static const String buildNumber = 'build_number';
  static const String environment = 'environment';
  static const String firstOpenTime = 'first_open_time';
  static const String lastOpenTime = 'last_open_time';

  // Device properties - خصائص الجهاز
  static const String platform = 'platform';
  static const String osVersion = 'os_version';
  static const String deviceCategory = 'device_category';
  static const String screenDensity = 'screen_density';
  static const String locale = 'locale';
  static const String timezone = 'timezone';

  // User behavior properties - خصائص سلوك المستخدم
  static const String totalSessions = 'total_sessions';
  static const String totalFields = 'total_fields_range';
  static const String primaryCropType = 'primary_crop_type';
  static const String totalAreaRange = 'total_area_range';
  static const String userType = 'user_type';
  static const String preferredLanguage = 'preferred_language';

  // Feature adoption - اعتماد الميزات
  static const String usesOfflineMode = 'uses_offline_mode';
  static const String usesNdvi = 'uses_ndvi';
  static const String usesIrrigation = 'uses_irrigation';
  static const String usesWeather = 'uses_weather';
  static const String usesVoice = 'uses_voice';
  static const String usesMap = 'uses_map';

  // Engagement properties - خصائص التفاعل
  static const String engagementLevel = 'engagement_level';
  static const String daysSinceLastSync = 'days_since_last_sync';
  static const String notificationsEnabled = 'notifications_enabled';
}

// =============================================================================
// User Properties Model - نموذج خصائص المستخدم
// =============================================================================

/// User properties for analytics
///
/// All properties are anonymized and don't contain PII.
class AnalyticsUserProperties {
  /// Anonymous user ID (hashed, not reversible)
  final String anonymousId;

  /// Tenant ID (if applicable, hashed)
  final String? tenantIdHash;

  /// App properties
  final String appVersion;
  final String buildNumber;
  final String environment;
  final DateTime? firstOpenTime;
  final DateTime? lastOpenTime;

  /// Device properties
  final String platform;
  final String? osVersion;
  final String? deviceCategory;
  final String? screenDensity;
  final String locale;
  final String timezone;

  /// User behavior properties (all anonymized)
  final int totalSessions;
  final String? totalFieldsRange;
  final String? primaryCropType;
  final String? totalAreaRange;
  final String? userType;
  final String preferredLanguage;

  /// Feature adoption flags
  final bool usesOfflineMode;
  final bool usesNdvi;
  final bool usesIrrigation;
  final bool usesWeather;
  final bool usesVoice;
  final bool usesMap;

  /// Engagement properties
  final String? engagementLevel;
  final int? daysSinceLastSync;
  final bool notificationsEnabled;

  /// Custom properties (sanitized)
  final Map<String, dynamic> customProperties;

  AnalyticsUserProperties({
    required this.anonymousId,
    this.tenantIdHash,
    required this.appVersion,
    required this.buildNumber,
    required this.environment,
    this.firstOpenTime,
    this.lastOpenTime,
    required this.platform,
    this.osVersion,
    this.deviceCategory,
    this.screenDensity,
    required this.locale,
    required this.timezone,
    this.totalSessions = 0,
    this.totalFieldsRange,
    this.primaryCropType,
    this.totalAreaRange,
    this.userType,
    this.preferredLanguage = 'en',
    this.usesOfflineMode = false,
    this.usesNdvi = false,
    this.usesIrrigation = false,
    this.usesWeather = false,
    this.usesVoice = false,
    this.usesMap = false,
    this.engagementLevel,
    this.daysSinceLastSync,
    this.notificationsEnabled = false,
    Map<String, dynamic>? customProperties,
  }) : customProperties = _sanitizeCustomProperties(customProperties ?? {});

  // ═══════════════════════════════════════════════════════════════════════════
  // Factory Methods - طرق المصنع
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create initial user properties with device info
  static Future<AnalyticsUserProperties> createInitial({
    required String anonymousId,
    String? tenantId,
    String? environment,
  }) async {
    final packageInfo = await PackageInfo.fromPlatform();
    final deviceInfo = DeviceInfoPlugin();

    String? osVersion;
    String? deviceCategory;

    if (Platform.isAndroid) {
      final androidInfo = await deviceInfo.androidInfo;
      osVersion = 'Android ${androidInfo.version.release}';
      deviceCategory = _getDeviceCategory((androidInfo.data['displayMetrics']?['widthPx']?.toDouble() ?? 1080) as double);
    } else if (Platform.isIOS) {
      final iosInfo = await deviceInfo.iosInfo;
      osVersion = 'iOS ${iosInfo.systemVersion}';
      deviceCategory = _getDeviceCategoryIOS(iosInfo.model);
    }

    return AnalyticsUserProperties(
      anonymousId: anonymousId,
      tenantIdHash: tenantId != null ? _hashId(tenantId) : null,
      appVersion: packageInfo.version,
      buildNumber: packageInfo.buildNumber,
      environment: environment ?? (kDebugMode ? 'development' : 'production'),
      firstOpenTime: DateTime.now(),
      lastOpenTime: DateTime.now(),
      platform: Platform.operatingSystem,
      osVersion: osVersion,
      deviceCategory: deviceCategory,
      locale: Platform.localeName,
      timezone: DateTime.now().timeZoneName,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Update Methods - طرق التحديث
  // ═══════════════════════════════════════════════════════════════════════════

  /// Create a copy with updated session info
  AnalyticsUserProperties withSessionUpdate() {
    return copyWith(
      totalSessions: totalSessions + 1,
      lastOpenTime: DateTime.now(),
    );
  }

  /// Create a copy with updated field stats
  AnalyticsUserProperties withFieldStats({
    required int fieldCount,
    required double totalArea,
    String? primaryCrop,
  }) {
    return copyWith(
      totalFieldsRange: _getCountRange(fieldCount),
      totalAreaRange: _getAreaRange(totalArea),
      primaryCropType: primaryCrop,
    );
  }

  /// Create a copy with feature usage flags
  AnalyticsUserProperties withFeatureUsage({
    bool? offlineMode,
    bool? ndvi,
    bool? irrigation,
    bool? weather,
    bool? voice,
    bool? map,
  }) {
    return copyWith(
      usesOfflineMode: offlineMode ?? usesOfflineMode,
      usesNdvi: ndvi ?? usesNdvi,
      usesIrrigation: irrigation ?? usesIrrigation,
      usesWeather: weather ?? usesWeather,
      usesVoice: voice ?? usesVoice,
      usesMap: map ?? usesMap,
    );
  }

  /// Create a copy with engagement level
  AnalyticsUserProperties withEngagement({
    required int actionsThisWeek,
    int? daysSinceSync,
    bool? notifications,
  }) {
    return copyWith(
      engagementLevel: _calculateEngagementLevel(actionsThisWeek),
      daysSinceLastSync: daysSinceSync,
      notificationsEnabled: notifications ?? notificationsEnabled,
    );
  }

  /// Set a custom property
  AnalyticsUserProperties withCustomProperty(String key, dynamic value) {
    final newProperties = Map<String, dynamic>.from(customProperties);
    newProperties[key] = PiiFilter.sanitize(value);
    return copyWith(customProperties: newProperties);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Serialization - التسلسل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Convert to map for analytics
  Map<String, dynamic> toMap() {
    return {
      UserPropertyKeys.appVersion: appVersion,
      UserPropertyKeys.buildNumber: buildNumber,
      UserPropertyKeys.environment: environment,
      if (firstOpenTime != null)
        UserPropertyKeys.firstOpenTime: firstOpenTime!.toIso8601String(),
      if (lastOpenTime != null)
        UserPropertyKeys.lastOpenTime: lastOpenTime!.toIso8601String(),
      UserPropertyKeys.platform: platform,
      if (osVersion != null) UserPropertyKeys.osVersion: osVersion,
      if (deviceCategory != null) UserPropertyKeys.deviceCategory: deviceCategory,
      if (screenDensity != null) UserPropertyKeys.screenDensity: screenDensity,
      UserPropertyKeys.locale: locale,
      UserPropertyKeys.timezone: timezone,
      UserPropertyKeys.totalSessions: totalSessions,
      if (totalFieldsRange != null) UserPropertyKeys.totalFields: totalFieldsRange,
      if (primaryCropType != null) UserPropertyKeys.primaryCropType: primaryCropType,
      if (totalAreaRange != null) UserPropertyKeys.totalAreaRange: totalAreaRange,
      if (userType != null) UserPropertyKeys.userType: userType,
      UserPropertyKeys.preferredLanguage: preferredLanguage,
      UserPropertyKeys.usesOfflineMode: usesOfflineMode,
      UserPropertyKeys.usesNdvi: usesNdvi,
      UserPropertyKeys.usesIrrigation: usesIrrigation,
      UserPropertyKeys.usesWeather: usesWeather,
      UserPropertyKeys.usesVoice: usesVoice,
      UserPropertyKeys.usesMap: usesMap,
      if (engagementLevel != null) UserPropertyKeys.engagementLevel: engagementLevel,
      if (daysSinceLastSync != null)
        UserPropertyKeys.daysSinceLastSync: daysSinceLastSync,
      UserPropertyKeys.notificationsEnabled: notificationsEnabled,
      ...customProperties,
    };
  }

  /// Convert to JSON for storage
  Map<String, dynamic> toJson() {
    return {
      'anonymous_id': anonymousId,
      'tenant_id_hash': tenantIdHash,
      'app_version': appVersion,
      'build_number': buildNumber,
      'environment': environment,
      'first_open_time': firstOpenTime?.toIso8601String(),
      'last_open_time': lastOpenTime?.toIso8601String(),
      'platform': platform,
      'os_version': osVersion,
      'device_category': deviceCategory,
      'screen_density': screenDensity,
      'locale': locale,
      'timezone': timezone,
      'total_sessions': totalSessions,
      'total_fields_range': totalFieldsRange,
      'primary_crop_type': primaryCropType,
      'total_area_range': totalAreaRange,
      'user_type': userType,
      'preferred_language': preferredLanguage,
      'uses_offline_mode': usesOfflineMode,
      'uses_ndvi': usesNdvi,
      'uses_irrigation': usesIrrigation,
      'uses_weather': usesWeather,
      'uses_voice': usesVoice,
      'uses_map': usesMap,
      'engagement_level': engagementLevel,
      'days_since_last_sync': daysSinceLastSync,
      'notifications_enabled': notificationsEnabled,
      'custom_properties': customProperties,
    };
  }

  /// Create from JSON
  factory AnalyticsUserProperties.fromJson(Map<String, dynamic> json) {
    return AnalyticsUserProperties(
      anonymousId: json['anonymous_id'] as String,
      tenantIdHash: json['tenant_id_hash'] as String?,
      appVersion: json['app_version'] as String,
      buildNumber: json['build_number'] as String,
      environment: json['environment'] as String,
      firstOpenTime: json['first_open_time'] != null
          ? DateTime.parse(json['first_open_time'] as String)
          : null,
      lastOpenTime: json['last_open_time'] != null
          ? DateTime.parse(json['last_open_time'] as String)
          : null,
      platform: json['platform'] as String,
      osVersion: json['os_version'] as String?,
      deviceCategory: json['device_category'] as String?,
      screenDensity: json['screen_density'] as String?,
      locale: json['locale'] as String,
      timezone: json['timezone'] as String,
      totalSessions: json['total_sessions'] as int? ?? 0,
      totalFieldsRange: json['total_fields_range'] as String?,
      primaryCropType: json['primary_crop_type'] as String?,
      totalAreaRange: json['total_area_range'] as String?,
      userType: json['user_type'] as String?,
      preferredLanguage: json['preferred_language'] as String? ?? 'en',
      usesOfflineMode: json['uses_offline_mode'] as bool? ?? false,
      usesNdvi: json['uses_ndvi'] as bool? ?? false,
      usesIrrigation: json['uses_irrigation'] as bool? ?? false,
      usesWeather: json['uses_weather'] as bool? ?? false,
      usesVoice: json['uses_voice'] as bool? ?? false,
      usesMap: json['uses_map'] as bool? ?? false,
      engagementLevel: json['engagement_level'] as String?,
      daysSinceLastSync: json['days_since_last_sync'] as int?,
      notificationsEnabled: json['notifications_enabled'] as bool? ?? false,
      customProperties: json['custom_properties'] != null
          ? Map<String, dynamic>.from(json['custom_properties'] as Map)
          : null,
    );
  }

  /// Copy with modifications
  AnalyticsUserProperties copyWith({
    String? anonymousId,
    String? tenantIdHash,
    String? appVersion,
    String? buildNumber,
    String? environment,
    DateTime? firstOpenTime,
    DateTime? lastOpenTime,
    String? platform,
    String? osVersion,
    String? deviceCategory,
    String? screenDensity,
    String? locale,
    String? timezone,
    int? totalSessions,
    String? totalFieldsRange,
    String? primaryCropType,
    String? totalAreaRange,
    String? userType,
    String? preferredLanguage,
    bool? usesOfflineMode,
    bool? usesNdvi,
    bool? usesIrrigation,
    bool? usesWeather,
    bool? usesVoice,
    bool? usesMap,
    String? engagementLevel,
    int? daysSinceLastSync,
    bool? notificationsEnabled,
    Map<String, dynamic>? customProperties,
  }) {
    return AnalyticsUserProperties(
      anonymousId: anonymousId ?? this.anonymousId,
      tenantIdHash: tenantIdHash ?? this.tenantIdHash,
      appVersion: appVersion ?? this.appVersion,
      buildNumber: buildNumber ?? this.buildNumber,
      environment: environment ?? this.environment,
      firstOpenTime: firstOpenTime ?? this.firstOpenTime,
      lastOpenTime: lastOpenTime ?? this.lastOpenTime,
      platform: platform ?? this.platform,
      osVersion: osVersion ?? this.osVersion,
      deviceCategory: deviceCategory ?? this.deviceCategory,
      screenDensity: screenDensity ?? this.screenDensity,
      locale: locale ?? this.locale,
      timezone: timezone ?? this.timezone,
      totalSessions: totalSessions ?? this.totalSessions,
      totalFieldsRange: totalFieldsRange ?? this.totalFieldsRange,
      primaryCropType: primaryCropType ?? this.primaryCropType,
      totalAreaRange: totalAreaRange ?? this.totalAreaRange,
      userType: userType ?? this.userType,
      preferredLanguage: preferredLanguage ?? this.preferredLanguage,
      usesOfflineMode: usesOfflineMode ?? this.usesOfflineMode,
      usesNdvi: usesNdvi ?? this.usesNdvi,
      usesIrrigation: usesIrrigation ?? this.usesIrrigation,
      usesWeather: usesWeather ?? this.usesWeather,
      usesVoice: usesVoice ?? this.usesVoice,
      usesMap: usesMap ?? this.usesMap,
      engagementLevel: engagementLevel ?? this.engagementLevel,
      daysSinceLastSync: daysSinceLastSync ?? this.daysSinceLastSync,
      notificationsEnabled: notificationsEnabled ?? this.notificationsEnabled,
      customProperties: customProperties ?? this.customProperties,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Helper Methods - طرق مساعدة خاصة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Sanitize custom properties
  static Map<String, dynamic> _sanitizeCustomProperties(Map<String, dynamic> props) {
    return PiiFilter.sanitize(props) as Map<String, dynamic>;
  }

  /// Hash ID for privacy
  static String _hashId(String id) {
    var hash = 0;
    for (var i = 0; i < id.length; i++) {
      hash = ((hash << 5) - hash) + id.codeUnitAt(i);
      hash = hash & 0x7FFFFFFF;
    }
    return hash.toRadixString(16);
  }

  /// Get device category based on screen width
  static String _getDeviceCategory(double? width) {
    if (width == null) return 'unknown';
    if (width < 600) return 'phone';
    if (width < 1200) return 'tablet';
    return 'large_tablet';
  }

  /// Get device category for iOS
  static String _getDeviceCategoryIOS(String model) {
    if (model.contains('iPad')) return 'tablet';
    if (model.contains('iPhone')) return 'phone';
    return 'unknown';
  }

  /// Get count range bucket
  static String _getCountRange(int count) {
    if (count == 0) return '0';
    if (count < 5) return '1-5';
    if (count < 10) return '5-10';
    if (count < 25) return '10-25';
    if (count < 50) return '25-50';
    return '50+';
  }

  /// Get area range bucket
  static String _getAreaRange(double hectares) {
    if (hectares < 1) return '< 1 ha';
    if (hectares < 5) return '1-5 ha';
    if (hectares < 10) return '5-10 ha';
    if (hectares < 50) return '10-50 ha';
    if (hectares < 100) return '50-100 ha';
    return '> 100 ha';
  }

  /// Calculate engagement level based on weekly actions
  static String _calculateEngagementLevel(int actionsThisWeek) {
    if (actionsThisWeek == 0) return 'inactive';
    if (actionsThisWeek < 5) return 'low';
    if (actionsThisWeek < 15) return 'medium';
    if (actionsThisWeek < 30) return 'high';
    return 'power_user';
  }

  @override
  String toString() {
    return 'AnalyticsUserProperties{anonymousId: $anonymousId, appVersion: $appVersion, platform: $platform}';
  }
}
