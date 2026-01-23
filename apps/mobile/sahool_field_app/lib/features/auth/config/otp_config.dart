import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:riverpod_annotation/riverpod_annotation.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../core/di/providers.dart';
import '../../../core/http/api_client.dart';
import '../../../core/utils/app_logger.dart';
import '../ui/otp_verification_screen.dart';

part 'otp_config.g.dart';

/// SAHOOL OTP Configuration System
/// نظام تكوين رمز التحقق OTP
///
/// Features:
/// - Remote configuration via Firebase Remote Config or API
/// - Local caching for offline use
/// - Per-channel configuration (SMS, WhatsApp, Telegram, Email)
/// - Rate limiting settings
/// - Default fallback values
///
/// Usage:
/// ```dart
/// final config = await ref.read(otpConfigProvider.future);
/// final smsConfig = config.getChannelConfig(OTPChannel.sms);
/// ```

// =============================================================================
// OTP Channel Configuration
// تكوين قناة OTP
// =============================================================================

/// Configuration for individual OTP delivery channels
/// تكوين قنوات توصيل OTP الفردية
class OTPChannelConfig {
  /// Whether this channel is enabled
  /// هل القناة مفعلة
  final bool enabled;

  /// Display name for the channel
  /// اسم العرض للقناة
  final String displayName;

  /// Arabic display name
  /// الاسم بالعربية
  final String displayNameAr;

  /// Channel priority (lower = higher priority)
  /// أولوية القناة (أقل = أعلى أولوية)
  final int priority;

  /// Provider-specific settings
  /// إعدادات المزود الخاصة
  final Map<String, dynamic> providerSettings;

  /// Maximum retries for this channel
  /// أقصى عدد محاولات لهذه القناة
  final int maxRetries;

  /// Timeout for delivery (in seconds)
  /// مهلة التوصيل (بالثواني)
  final int deliveryTimeoutSeconds;

  /// Whether to show as primary option
  /// هل تظهر كخيار رئيسي
  final bool showAsPrimary;

  const OTPChannelConfig({
    required this.enabled,
    required this.displayName,
    required this.displayNameAr,
    this.priority = 0,
    this.providerSettings = const {},
    this.maxRetries = 3,
    this.deliveryTimeoutSeconds = 30,
    this.showAsPrimary = false,
  });

  /// Create from JSON
  factory OTPChannelConfig.fromJson(Map<String, dynamic> json) {
    return OTPChannelConfig(
      enabled: json['enabled'] as bool? ?? false,
      displayName: json['display_name'] as String? ?? '',
      displayNameAr: json['display_name_ar'] as String? ?? '',
      priority: json['priority'] as int? ?? 0,
      providerSettings:
          (json['provider_settings'] as Map<String, dynamic>?) ?? {},
      maxRetries: json['max_retries'] as int? ?? 3,
      deliveryTimeoutSeconds: json['delivery_timeout_seconds'] as int? ?? 30,
      showAsPrimary: json['show_as_primary'] as bool? ?? false,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'display_name': displayName,
      'display_name_ar': displayNameAr,
      'priority': priority,
      'provider_settings': providerSettings,
      'max_retries': maxRetries,
      'delivery_timeout_seconds': deliveryTimeoutSeconds,
      'show_as_primary': showAsPrimary,
    };
  }

  /// Copy with modifications
  OTPChannelConfig copyWith({
    bool? enabled,
    String? displayName,
    String? displayNameAr,
    int? priority,
    Map<String, dynamic>? providerSettings,
    int? maxRetries,
    int? deliveryTimeoutSeconds,
    bool? showAsPrimary,
  }) {
    return OTPChannelConfig(
      enabled: enabled ?? this.enabled,
      displayName: displayName ?? this.displayName,
      displayNameAr: displayNameAr ?? this.displayNameAr,
      priority: priority ?? this.priority,
      providerSettings: providerSettings ?? this.providerSettings,
      maxRetries: maxRetries ?? this.maxRetries,
      deliveryTimeoutSeconds:
          deliveryTimeoutSeconds ?? this.deliveryTimeoutSeconds,
      showAsPrimary: showAsPrimary ?? this.showAsPrimary,
    );
  }

  @override
  String toString() => 'OTPChannelConfig('
      'enabled: $enabled, '
      'displayName: $displayName, '
      'priority: $priority)';
}

// =============================================================================
// Rate Limiting Configuration
// تكوين تحديد المعدل
// =============================================================================

/// Rate limiting settings for OTP requests
/// إعدادات تحديد معدل طلبات OTP
class OTPRateLimitConfig {
  /// Maximum OTP requests per hour
  /// أقصى عدد طلبات OTP في الساعة
  final int maxRequestsPerHour;

  /// Maximum OTP requests per day
  /// أقصى عدد طلبات OTP في اليوم
  final int maxRequestsPerDay;

  /// Cooldown between requests (in seconds)
  /// فترة الانتظار بين الطلبات (بالثواني)
  final int cooldownSeconds;

  /// Progressive delay multiplier for repeated failures
  /// مضاعف التأخير التدريجي للفشل المتكرر
  final double progressiveDelayMultiplier;

  /// Maximum cooldown time (in seconds)
  /// أقصى فترة انتظار (بالثواني)
  final int maxCooldownSeconds;

  /// Account lockout threshold (failed attempts)
  /// حد قفل الحساب (المحاولات الفاشلة)
  final int lockoutThreshold;

  /// Lockout duration (in minutes)
  /// مدة القفل (بالدقائق)
  final int lockoutDurationMinutes;

  const OTPRateLimitConfig({
    this.maxRequestsPerHour = 5,
    this.maxRequestsPerDay = 10,
    this.cooldownSeconds = 60,
    this.progressiveDelayMultiplier = 1.5,
    this.maxCooldownSeconds = 300,
    this.lockoutThreshold = 5,
    this.lockoutDurationMinutes = 30,
  });

  /// Create from JSON
  factory OTPRateLimitConfig.fromJson(Map<String, dynamic> json) {
    return OTPRateLimitConfig(
      maxRequestsPerHour: json['max_requests_per_hour'] as int? ?? 5,
      maxRequestsPerDay: json['max_requests_per_day'] as int? ?? 10,
      cooldownSeconds: json['cooldown_seconds'] as int? ?? 60,
      progressiveDelayMultiplier:
          (json['progressive_delay_multiplier'] as num?)?.toDouble() ?? 1.5,
      maxCooldownSeconds: json['max_cooldown_seconds'] as int? ?? 300,
      lockoutThreshold: json['lockout_threshold'] as int? ?? 5,
      lockoutDurationMinutes: json['lockout_duration_minutes'] as int? ?? 30,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'max_requests_per_hour': maxRequestsPerHour,
      'max_requests_per_day': maxRequestsPerDay,
      'cooldown_seconds': cooldownSeconds,
      'progressive_delay_multiplier': progressiveDelayMultiplier,
      'max_cooldown_seconds': maxCooldownSeconds,
      'lockout_threshold': lockoutThreshold,
      'lockout_duration_minutes': lockoutDurationMinutes,
    };
  }

  /// Calculate progressive cooldown based on attempt number
  int calculateCooldown(int attemptNumber) {
    if (attemptNumber <= 1) return cooldownSeconds;

    final calculated =
        (cooldownSeconds * (progressiveDelayMultiplier * (attemptNumber - 1)))
            .round();
    return calculated > maxCooldownSeconds ? maxCooldownSeconds : calculated;
  }

  @override
  String toString() => 'OTPRateLimitConfig('
      'maxRequestsPerHour: $maxRequestsPerHour, '
      'cooldownSeconds: $cooldownSeconds)';
}

// =============================================================================
// Main OTP Configuration
// التكوين الرئيسي لـ OTP
// =============================================================================

/// Main OTP configuration class
/// فئة التكوين الرئيسية لـ OTP
class OTPConfig {
  /// Configuration version for cache invalidation
  /// إصدار التكوين لإبطال الذاكرة المؤقتة
  final int version;

  /// Last updated timestamp
  /// وقت آخر تحديث
  final DateTime lastUpdated;

  /// OTP code length
  /// طول رمز OTP
  final int otpLength;

  /// OTP expiration time (in seconds)
  /// مدة صلاحية OTP (بالثواني)
  final int expirationSeconds;

  /// Resend cooldown (in seconds)
  /// فترة انتظار إعادة الإرسال (بالثواني)
  final int resendCooldownSeconds;

  /// Maximum verification attempts
  /// أقصى عدد محاولات التحقق
  final int maxAttempts;

  /// Whether to auto-verify SMS OTP
  /// التحقق التلقائي من OTP عبر SMS
  final bool enableAutoVerify;

  /// Enable biometric fallback
  /// تفعيل البديل البيومتري
  final bool enableBiometricFallback;

  /// Channel-specific configurations
  /// تكوينات القنوات الخاصة
  final Map<String, OTPChannelConfig> channels;

  /// Rate limiting configuration
  /// تكوين تحديد المعدل
  final OTPRateLimitConfig rateLimit;

  /// Provider configurations (Twilio, Meta, Telegram)
  /// تكوينات المزودين
  final Map<String, Map<String, dynamic>> providerConfigs;

  /// Feature flags
  /// أعلام الميزات
  final Map<String, bool> featureFlags;

  const OTPConfig({
    this.version = 1,
    required this.lastUpdated,
    this.otpLength = 6,
    this.expirationSeconds = 300,
    this.resendCooldownSeconds = 60,
    this.maxAttempts = 3,
    this.enableAutoVerify = true,
    this.enableBiometricFallback = false,
    this.channels = const {},
    this.rateLimit = const OTPRateLimitConfig(),
    this.providerConfigs = const {},
    this.featureFlags = const {},
  });

  /// Default configuration
  /// التكوين الافتراضي
  factory OTPConfig.defaults() {
    return OTPConfig(
      version: 1,
      lastUpdated: DateTime.now(),
      otpLength: 6,
      expirationSeconds: 300,
      resendCooldownSeconds: 60,
      maxAttempts: 3,
      enableAutoVerify: true,
      enableBiometricFallback: false,
      channels: {
        'sms': const OTPChannelConfig(
          enabled: true,
          displayName: 'SMS',
          displayNameAr: 'رسالة نصية',
          priority: 1,
          showAsPrimary: true,
          providerSettings: {
            'provider': 'twilio',
            'sender_id': 'SAHOOL',
          },
        ),
        'whatsapp': const OTPChannelConfig(
          enabled: true,
          displayName: 'WhatsApp',
          displayNameAr: 'واتساب',
          priority: 2,
          showAsPrimary: true,
          providerSettings: {
            'provider': 'meta',
            'template_name': 'otp_verification',
            'language': 'ar',
          },
        ),
        'telegram': const OTPChannelConfig(
          enabled: true,
          displayName: 'Telegram',
          displayNameAr: 'تيليجرام',
          priority: 3,
          showAsPrimary: false,
          providerSettings: {
            'provider': 'telegram_bot',
            'bot_username': 'SahoolOTPBot',
          },
        ),
        'email': const OTPChannelConfig(
          enabled: true,
          displayName: 'Email',
          displayNameAr: 'البريد الإلكتروني',
          priority: 4,
          showAsPrimary: false,
          deliveryTimeoutSeconds: 60,
          providerSettings: {
            'provider': 'sendgrid',
            'template_id': 'otp_verification_template',
          },
        ),
      },
      rateLimit: const OTPRateLimitConfig(
        maxRequestsPerHour: 5,
        maxRequestsPerDay: 10,
        cooldownSeconds: 60,
        progressiveDelayMultiplier: 1.5,
        maxCooldownSeconds: 300,
        lockoutThreshold: 5,
        lockoutDurationMinutes: 30,
      ),
      providerConfigs: {
        'twilio': {
          'messaging_service_sid': '',
          'verify_service_sid': '',
          'fallback_enabled': true,
        },
        'meta': {
          'business_id': '',
          'phone_number_id': '',
          'access_token_env': 'META_WHATSAPP_TOKEN',
        },
        'telegram': {
          'bot_token_env': 'TELEGRAM_BOT_TOKEN',
          'webhook_enabled': true,
        },
        'sendgrid': {
          'api_key_env': 'SENDGRID_API_KEY',
          'from_email': 'noreply@sahool.app',
          'from_name': 'SAHOOL',
        },
      },
      featureFlags: {
        'enable_multi_channel': true,
        'enable_channel_preference': true,
        'enable_smart_retry': true,
        'enable_delivery_tracking': true,
        'enable_fraud_detection': true,
        'enable_geo_blocking': false,
      },
    );
  }

  /// Create from JSON
  factory OTPConfig.fromJson(Map<String, dynamic> json) {
    // Parse channels
    final channelsJson = json['channels'] as Map<String, dynamic>? ?? {};
    final channels = <String, OTPChannelConfig>{};
    channelsJson.forEach((key, value) {
      if (value is Map<String, dynamic>) {
        channels[key] = OTPChannelConfig.fromJson(value);
      }
    });

    // Parse provider configs
    final providerConfigsJson =
        json['provider_configs'] as Map<String, dynamic>? ?? {};
    final providerConfigs = <String, Map<String, dynamic>>{};
    providerConfigsJson.forEach((key, value) {
      if (value is Map<String, dynamic>) {
        providerConfigs[key] = value;
      }
    });

    // Parse feature flags
    final featureFlagsJson =
        json['feature_flags'] as Map<String, dynamic>? ?? {};
    final featureFlags = <String, bool>{};
    featureFlagsJson.forEach((key, value) {
      if (value is bool) {
        featureFlags[key] = value;
      }
    });

    return OTPConfig(
      version: json['version'] as int? ?? 1,
      lastUpdated: json['last_updated'] != null
          ? DateTime.parse(json['last_updated'] as String)
          : DateTime.now(),
      otpLength: json['otp_length'] as int? ?? 6,
      expirationSeconds: json['expiration_seconds'] as int? ?? 300,
      resendCooldownSeconds: json['resend_cooldown_seconds'] as int? ?? 60,
      maxAttempts: json['max_attempts'] as int? ?? 3,
      enableAutoVerify: json['enable_auto_verify'] as bool? ?? true,
      enableBiometricFallback: json['enable_biometric_fallback'] as bool? ?? false,
      channels: channels,
      rateLimit: json['rate_limit'] != null
          ? OTPRateLimitConfig.fromJson(json['rate_limit'] as Map<String, dynamic>)
          : const OTPRateLimitConfig(),
      providerConfigs: providerConfigs,
      featureFlags: featureFlags,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'version': version,
      'last_updated': lastUpdated.toIso8601String(),
      'otp_length': otpLength,
      'expiration_seconds': expirationSeconds,
      'resend_cooldown_seconds': resendCooldownSeconds,
      'max_attempts': maxAttempts,
      'enable_auto_verify': enableAutoVerify,
      'enable_biometric_fallback': enableBiometricFallback,
      'channels': channels.map((key, value) => MapEntry(key, value.toJson())),
      'rate_limit': rateLimit.toJson(),
      'provider_configs': providerConfigs,
      'feature_flags': featureFlags,
    };
  }

  /// Get channel configuration by OTPChannel enum
  OTPChannelConfig? getChannelConfig(OTPChannel channel) {
    final key = channel.name.toLowerCase();
    return channels[key];
  }

  /// Get enabled channels sorted by priority
  List<MapEntry<String, OTPChannelConfig>> getEnabledChannels() {
    final enabled = channels.entries
        .where((entry) => entry.value.enabled)
        .toList();
    enabled.sort((a, b) => a.value.priority.compareTo(b.value.priority));
    return enabled;
  }

  /// Get primary channels (for UI display)
  List<MapEntry<String, OTPChannelConfig>> getPrimaryChannels() {
    return getEnabledChannels()
        .where((entry) => entry.value.showAsPrimary)
        .toList();
  }

  /// Check if a feature is enabled
  bool isFeatureEnabled(String featureName) {
    return featureFlags[featureName] ?? false;
  }

  /// Get provider configuration
  Map<String, dynamic>? getProviderConfig(String provider) {
    return providerConfigs[provider];
  }

  /// Expiration duration
  Duration get expirationDuration => Duration(seconds: expirationSeconds);

  /// Resend cooldown duration
  Duration get resendCooldownDuration => Duration(seconds: resendCooldownSeconds);

  /// Copy with modifications
  OTPConfig copyWith({
    int? version,
    DateTime? lastUpdated,
    int? otpLength,
    int? expirationSeconds,
    int? resendCooldownSeconds,
    int? maxAttempts,
    bool? enableAutoVerify,
    bool? enableBiometricFallback,
    Map<String, OTPChannelConfig>? channels,
    OTPRateLimitConfig? rateLimit,
    Map<String, Map<String, dynamic>>? providerConfigs,
    Map<String, bool>? featureFlags,
  }) {
    return OTPConfig(
      version: version ?? this.version,
      lastUpdated: lastUpdated ?? this.lastUpdated,
      otpLength: otpLength ?? this.otpLength,
      expirationSeconds: expirationSeconds ?? this.expirationSeconds,
      resendCooldownSeconds:
          resendCooldownSeconds ?? this.resendCooldownSeconds,
      maxAttempts: maxAttempts ?? this.maxAttempts,
      enableAutoVerify: enableAutoVerify ?? this.enableAutoVerify,
      enableBiometricFallback:
          enableBiometricFallback ?? this.enableBiometricFallback,
      channels: channels ?? this.channels,
      rateLimit: rateLimit ?? this.rateLimit,
      providerConfigs: providerConfigs ?? this.providerConfigs,
      featureFlags: featureFlags ?? this.featureFlags,
    );
  }

  @override
  String toString() => 'OTPConfig('
      'version: $version, '
      'otpLength: $otpLength, '
      'expirationSeconds: $expirationSeconds, '
      'channels: ${channels.length}, '
      'lastUpdated: $lastUpdated)';
}

// =============================================================================
// OTP Configuration Repository
// مستودع تكوين OTP
// =============================================================================

/// Repository for managing OTP configuration
/// مستودع لإدارة تكوين OTP
class OTPConfigRepository {
  final ApiClient _apiClient;
  final SharedPreferences _prefs;

  static const String _cacheKey = 'otp_config_cache';
  static const String _cacheTimestampKey = 'otp_config_cache_timestamp';
  static const Duration _cacheExpiry = Duration(hours: 1);
  static const String _configEndpoint = '/api/v1/auth/otp/config';

  OTPConfigRepository({
    required ApiClient apiClient,
    required SharedPreferences prefs,
  })  : _apiClient = apiClient,
        _prefs = prefs;

  /// Fetch configuration from remote API
  /// جلب التكوين من الخادم البعيد
  Future<OTPConfig?> fetchRemoteConfig() async {
    try {
      final response = await _apiClient.get(_configEndpoint);

      if (response != null) {
        final data = response is Map<String, dynamic>
            ? response
            : (response as Map).cast<String, dynamic>();
        final config = OTPConfig.fromJson(data);

        // Cache the configuration
        await _cacheConfig(config);

        AppLogger.i('OTP config fetched from remote', tag: 'OTPConfig');
        return config;
      }
    } catch (e) {
      AppLogger.e('Failed to fetch OTP config from remote',
          error: e, tag: 'OTPConfig');
    }
    return null;
  }

  /// Get cached configuration
  /// الحصول على التكوين المخزن مؤقتاً
  Future<OTPConfig?> getCachedConfig() async {
    try {
      final cachedJson = _prefs.getString(_cacheKey);
      if (cachedJson == null) return null;

      final cacheTimestamp = _prefs.getInt(_cacheTimestampKey);
      if (cacheTimestamp != null) {
        final cacheTime =
            DateTime.fromMillisecondsSinceEpoch(cacheTimestamp);
        if (DateTime.now().difference(cacheTime) > _cacheExpiry) {
          AppLogger.d('OTP config cache expired', tag: 'OTPConfig');
          return null;
        }
      }

      final json = jsonDecode(cachedJson) as Map<String, dynamic>;
      return OTPConfig.fromJson(json);
    } catch (e) {
      AppLogger.e('Failed to read cached OTP config', error: e, tag: 'OTPConfig');
    }
    return null;
  }

  /// Cache configuration locally
  /// تخزين التكوين محلياً
  Future<void> _cacheConfig(OTPConfig config) async {
    try {
      final json = jsonEncode(config.toJson());
      await _prefs.setString(_cacheKey, json);
      await _prefs.setInt(
        _cacheTimestampKey,
        DateTime.now().millisecondsSinceEpoch,
      );
      AppLogger.d('OTP config cached locally', tag: 'OTPConfig');
    } catch (e) {
      AppLogger.e('Failed to cache OTP config', error: e, tag: 'OTPConfig');
    }
  }

  /// Clear cached configuration
  /// مسح التكوين المخزن مؤقتاً
  Future<void> clearCache() async {
    await _prefs.remove(_cacheKey);
    await _prefs.remove(_cacheTimestampKey);
    AppLogger.d('OTP config cache cleared', tag: 'OTPConfig');
  }

  /// Get configuration with fallback strategy
  /// الحصول على التكوين مع استراتيجية احتياطية
  ///
  /// Priority:
  /// 1. Remote config (if network available)
  /// 2. Cached config (if not expired)
  /// 3. Default config
  Future<OTPConfig> getConfig({bool forceRefresh = false}) async {
    // Try to get fresh config if force refresh or no cache
    if (forceRefresh) {
      final remoteConfig = await fetchRemoteConfig();
      if (remoteConfig != null) {
        return remoteConfig;
      }
    }

    // Try cached config first (faster)
    final cachedConfig = await getCachedConfig();
    if (cachedConfig != null && !forceRefresh) {
      // Fetch remote config in background for next time
      _fetchInBackground();
      return cachedConfig;
    }

    // Try remote config
    final remoteConfig = await fetchRemoteConfig();
    if (remoteConfig != null) {
      return remoteConfig;
    }

    // Fall back to cached config even if expired
    if (cachedConfig != null) {
      AppLogger.w('Using expired cached OTP config', tag: 'OTPConfig');
      return cachedConfig;
    }

    // Use default config
    AppLogger.i('Using default OTP config', tag: 'OTPConfig');
    return OTPConfig.defaults();
  }

  /// Fetch remote config in background without waiting
  void _fetchInBackground() {
    fetchRemoteConfig().then((_) {
      if (kDebugMode) {
        AppLogger.d('Background OTP config refresh completed', tag: 'OTPConfig');
      }
    }).catchError((e) {
      AppLogger.e('Background OTP config refresh failed',
          error: e, tag: 'OTPConfig');
    });
  }
}

// =============================================================================
// Riverpod Providers
// موفرو Riverpod
// =============================================================================

/// SharedPreferences provider
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError(
    'sharedPreferencesProvider must be overridden in main.dart',
  );
});

/// OTP Config Repository provider
final otpConfigRepositoryProvider = Provider<OTPConfigRepository>((ref) {
  final apiClient = ref.watch(apiClientProvider);
  final prefs = ref.watch(sharedPreferencesProvider);
  return OTPConfigRepository(
    apiClient: apiClient,
    prefs: prefs,
  );
});

/// Main OTP Configuration provider
/// موفر التكوين الرئيسي لـ OTP
@riverpod
class OTPConfigNotifier extends _$OTPConfigNotifier {
  @override
  Future<OTPConfig> build() async {
    final repository = ref.watch(otpConfigRepositoryProvider);
    return repository.getConfig();
  }

  /// Refresh configuration from remote
  Future<void> refresh() async {
    state = const AsyncLoading();
    try {
      final repository = ref.read(otpConfigRepositoryProvider);
      final config = await repository.getConfig(forceRefresh: true);
      state = AsyncData(config);
    } catch (e, st) {
      state = AsyncError(e, st);
    }
  }

  /// Clear cache and reload
  Future<void> clearCacheAndReload() async {
    final repository = ref.read(otpConfigRepositoryProvider);
    await repository.clearCache();
    await refresh();
  }
}

/// Channel-specific configuration provider
@riverpod
OTPChannelConfig? otpChannelConfig(Ref ref, OTPChannel channel) {
  final configAsync = ref.watch(otpConfigNotifierProvider);
  return configAsync.whenOrNull(
    data: (config) => config.getChannelConfig(channel),
  );
}

/// Enabled channels provider (sorted by priority)
@riverpod
List<MapEntry<String, OTPChannelConfig>> enabledOTPChannels(Ref ref) {
  final configAsync = ref.watch(otpConfigNotifierProvider);
  return configAsync.whenOrNull(
        data: (config) => config.getEnabledChannels(),
      ) ??
      [];
}

/// Primary channels provider (for UI display)
@riverpod
List<MapEntry<String, OTPChannelConfig>> primaryOTPChannels(Ref ref) {
  final configAsync = ref.watch(otpConfigNotifierProvider);
  return configAsync.whenOrNull(
        data: (config) => config.getPrimaryChannels(),
      ) ??
      [];
}

/// Rate limit configuration provider
@riverpod
OTPRateLimitConfig otpRateLimitConfig(Ref ref) {
  final configAsync = ref.watch(otpConfigNotifierProvider);
  return configAsync.whenOrNull(
        data: (config) => config.rateLimit,
      ) ??
      const OTPRateLimitConfig();
}

/// Feature flag provider
@riverpod
bool otpFeatureFlag(Ref ref, String featureName) {
  final configAsync = ref.watch(otpConfigNotifierProvider);
  return configAsync.whenOrNull(
        data: (config) => config.isFeatureEnabled(featureName),
      ) ??
      false;
}

// =============================================================================
// Extension for OTPChannel
// امتداد لـ OTPChannel
// =============================================================================

extension OTPChannelExtension on OTPChannel {
  /// Get display name based on config
  String getDisplayName(OTPConfig config, {bool arabic = false}) {
    final channelConfig = config.getChannelConfig(this);
    if (channelConfig == null) {
      return arabic ? _defaultDisplayNameAr : _defaultDisplayName;
    }
    return arabic ? channelConfig.displayNameAr : channelConfig.displayName;
  }

  String get _defaultDisplayName {
    switch (this) {
      case OTPChannel.sms:
        return 'SMS';
      case OTPChannel.whatsapp:
        return 'WhatsApp';
      case OTPChannel.telegram:
        return 'Telegram';
      case OTPChannel.email:
        return 'Email';
    }
  }

  String get _defaultDisplayNameAr {
    switch (this) {
      case OTPChannel.sms:
        return 'رسالة نصية';
      case OTPChannel.whatsapp:
        return 'واتساب';
      case OTPChannel.telegram:
        return 'تيليجرام';
      case OTPChannel.email:
        return 'البريد الإلكتروني';
    }
  }

  /// Get channel key for config lookup
  String get configKey => name.toLowerCase();
}

// =============================================================================
// Debug Helpers
// أدوات التصحيح
// =============================================================================

/// Print OTP configuration for debugging
void printOTPConfig(OTPConfig config) {
  if (!kDebugMode) return;

  final output = '''

  OTP Configuration
  ├── Version: ${config.version}
  ├── Last Updated: ${config.lastUpdated}
  ├── OTP Length: ${config.otpLength}
  ├── Expiration: ${config.expirationSeconds}s
  ├── Resend Cooldown: ${config.resendCooldownSeconds}s
  ├── Max Attempts: ${config.maxAttempts}
  ├── Auto Verify: ${config.enableAutoVerify}
  ├── Biometric Fallback: ${config.enableBiometricFallback}
  ├── Rate Limits:
  │   ├── Per Hour: ${config.rateLimit.maxRequestsPerHour}
  │   ├── Per Day: ${config.rateLimit.maxRequestsPerDay}
  │   └── Cooldown: ${config.rateLimit.cooldownSeconds}s
  └── Channels:
${config.channels.entries.map((e) => '      ├── ${e.key}: ${e.value.enabled ? "enabled" : "disabled"} (priority: ${e.value.priority})').join('\n')}

''';

  AppLogger.d(output, tag: 'OTPConfig');
}
