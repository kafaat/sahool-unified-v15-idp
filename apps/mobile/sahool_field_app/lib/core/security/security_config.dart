import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Device Integrity Policy
/// سياسة سلامة الجهاز
enum DeviceIntegrityPolicy {
  /// Disabled - no checks performed
  /// معطل - لا يتم إجراء أي فحوصات
  disabled,

  /// Log only - detect but don't block
  /// سجل فقط - اكتشف ولكن لا تحظر
  log,

  /// Warn user but allow usage
  /// تحذير المستخدم ولكن السماح بالاستخدام
  warn,

  /// Block compromised devices (root/jailbreak)
  /// حظر الأجهزة المخترقة (روت/جلبريك)
  block,

  /// Block all security issues (including emulators, debug mode)
  /// حظر جميع المشاكل الأمنية (بما في ذلك المحاكيات، وضع التطوير)
  blockAll,
}

/// Session Security Policy
/// سياسة أمان الجلسة
enum SessionSecurityPolicy {
  /// Disabled - no session timeout
  /// معطل - لا انتهاء للجلسة
  disabled,

  /// Relaxed - long session timeout (2 hours)
  /// مرن - انتهاء جلسة طويل
  relaxed,

  /// Standard - configurable session timeout (default 15 minutes)
  /// قياسي - انتهاء جلسة قابل للتخصيص
  standard,

  /// Strict - short session timeout (5 minutes)
  /// صارم - انتهاء جلسة قصير
  strict,
}

/// Screenshot Prevention Policy
/// سياسة منع لقطات الشاشة
enum ScreenshotPolicy {
  /// Disabled - screenshots allowed everywhere
  /// معطل - مسموح بلقطات الشاشة في كل مكان
  disabled,

  /// Sensitive screens only - prevent screenshots on sensitive screens
  /// الشاشات الحساسة فقط - منع لقطات الشاشة على الشاشات الحساسة
  sensitiveOnly,

  /// All screens - prevent screenshots everywhere
  /// كل الشاشات - منع لقطات الشاشة في كل مكان
  allScreens,
}

/// Security Level
/// مستوى الأمان
enum SecurityLevel {
  /// Low security
  low('low'),

  /// Medium security (default)
  medium('medium'),

  /// High security
  high('high'),

  /// Maximum security
  maximum('maximum');

  final String code;
  const SecurityLevel(this.code);
}

/// Security Configuration
/// إعدادات الأمان
///
/// Centralized security settings for the SAHOOL mobile app
/// Controls certificate pinning, device integrity, and other security features

class SecurityConfig {
  /// Whether to enable SSL certificate pinning
  final bool enableCertificatePinning;

  /// Whether to enforce strict certificate pinning (fail if no match)
  final bool strictCertificatePinning;

  /// Whether to allow certificate pinning bypass in debug mode
  final bool allowPinningDebugBypass;

  /// Request timeout duration
  final Duration requestTimeout;

  /// Device integrity policy
  /// سياسة سلامة الجهاز
  final DeviceIntegrityPolicy deviceIntegrityPolicy;

  /// Whether to enforce security checks in debug mode
  /// Normally security is bypassed in debug mode for development
  /// Set to true to test security features in debug builds
  final bool enforceSecurityInDebug;

  /// Whether to allow app usage on emulators/simulators
  final bool allowEmulators;

  /// Whether to log security events to analytics
  final bool logSecurityEvents;

  /// Whether to block mock locations
  /// حظر المواقع الوهمية
  final bool blockMockLocation;

  /// Session security policy
  /// سياسة أمان الجلسة
  final SessionSecurityPolicy sessionPolicy;

  /// Session timeout duration (used with SessionSecurityPolicy.standard)
  /// مدة انتهاء الجلسة
  final Duration sessionTimeout;

  /// Screenshot prevention policy
  /// سياسة منع لقطات الشاشة
  final ScreenshotPolicy screenshotPolicy;

  /// Security level (used by device security service)
  /// مستوى الأمان
  final SecurityLevel level;

  /// Whether to log authentication events
  /// تسجيل أحداث المصادقة
  final bool logAuthEvents;

  /// Whether to show screen security warning
  /// إظهار تحذير أمان الشاشة
  final bool showScreenSecurityWarning;

  const SecurityConfig({
    this.enableCertificatePinning = false,
    this.strictCertificatePinning = false,
    this.allowPinningDebugBypass = true,
    this.requestTimeout = const Duration(seconds: 30),
    this.deviceIntegrityPolicy = DeviceIntegrityPolicy.disabled,
    this.enforceSecurityInDebug = false,
    this.allowEmulators = true,
    this.logSecurityEvents = true,
    this.blockMockLocation = false,
    this.sessionPolicy = SessionSecurityPolicy.disabled,
    this.sessionTimeout = const Duration(minutes: 15),
    this.screenshotPolicy = ScreenshotPolicy.disabled,
    this.level = SecurityLevel.low,
    this.logAuthEvents = true,
    this.showScreenSecurityWarning = false,
  });

  /// Production security configuration
  /// Enables all security features for production builds
  /// تكوين الأمان للإنتاج - تمكين جميع ميزات الأمان
  static const production = SecurityConfig(
    enableCertificatePinning: true,
    strictCertificatePinning: true,
    allowPinningDebugBypass: false,
    requestTimeout: Duration(seconds: 20),
    deviceIntegrityPolicy: DeviceIntegrityPolicy.block,
    enforceSecurityInDebug: false,
    allowEmulators: false,
    logSecurityEvents: true,
    blockMockLocation: true,
    sessionPolicy: SessionSecurityPolicy.standard,
    sessionTimeout: Duration(minutes: 15),
    screenshotPolicy: ScreenshotPolicy.sensitiveOnly,
    level: SecurityLevel.high,
    logAuthEvents: true,
    showScreenSecurityWarning: true,
  );

  /// Staging security configuration
  /// Enables security with some flexibility for testing
  /// تكوين الأمان للمرحلة التجريبية
  static const staging = SecurityConfig(
    enableCertificatePinning: true,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    requestTimeout: Duration(seconds: 30),
    deviceIntegrityPolicy: DeviceIntegrityPolicy.warn,
    enforceSecurityInDebug: false,
    allowEmulators: true,
    logSecurityEvents: true,
    blockMockLocation: false,
    sessionPolicy: SessionSecurityPolicy.relaxed,
    sessionTimeout: Duration(minutes: 30),
    screenshotPolicy: ScreenshotPolicy.disabled,
    level: SecurityLevel.medium,
    logAuthEvents: true,
    showScreenSecurityWarning: false,
  );

  /// Development security configuration
  /// Disables certificate pinning and security checks for local development
  /// تكوين الأمان للتطوير - معطل للسماح بالتطوير على المحاكيات
  static const development = SecurityConfig(
    enableCertificatePinning: false,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    requestTimeout: Duration(seconds: 30),
    deviceIntegrityPolicy: DeviceIntegrityPolicy
        .disabled, // Disabled to prevent crash on emulators
    enforceSecurityInDebug: false,
    allowEmulators: true,
    logSecurityEvents: false,
    blockMockLocation: false,
    sessionPolicy: SessionSecurityPolicy.disabled,
    sessionTimeout: Duration(minutes: 15),
    screenshotPolicy: ScreenshotPolicy.disabled,
    level: SecurityLevel.low,
    logAuthEvents: false,
    showScreenSecurityWarning: false,
  );

  /// Get security configuration based on environment
  factory SecurityConfig.forEnvironment(String environment) {
    switch (environment.toLowerCase()) {
      case 'production':
      case 'prod':
        return SecurityConfig.production;
      case 'staging':
      case 'stage':
        return SecurityConfig.staging;
      case 'development':
      case 'dev':
      default:
        return SecurityConfig.development;
    }
  }

  /// Get security configuration based on build mode
  /// In release mode, uses production config
  /// In debug/profile mode, uses development config
  factory SecurityConfig.fromBuildMode() {
    if (kReleaseMode) {
      return SecurityConfig.production;
    } else {
      return SecurityConfig.development;
    }
  }

  /// Get effective session timeout based on policy
  /// الحصول على مهلة الجلسة الفعلية بناءً على السياسة
  Duration getEffectiveSessionTimeout() {
    switch (sessionPolicy) {
      case SessionSecurityPolicy.disabled:
        return const Duration(days: 365);
      case SessionSecurityPolicy.relaxed:
        return const Duration(hours: 2);
      case SessionSecurityPolicy.standard:
        return sessionTimeout;
      case SessionSecurityPolicy.strict:
        return const Duration(minutes: 5);
    }
  }

  /// Whether screenshot prevention is enabled
  /// هل منع لقطات الشاشة مفعل
  bool get isScreenshotPreventionEnabled =>
      screenshotPolicy != ScreenshotPolicy.disabled;

  /// Whether session timeout is enabled
  /// هل انتهاء الجلسة مفعل
  bool get isSessionTimeoutEnabled =>
      sessionPolicy != SessionSecurityPolicy.disabled;

  /// Copy configuration with updated values
  SecurityConfig copyWith({
    bool? enableCertificatePinning,
    bool? strictCertificatePinning,
    bool? allowPinningDebugBypass,
    Duration? requestTimeout,
    DeviceIntegrityPolicy? deviceIntegrityPolicy,
    bool? enforceSecurityInDebug,
    bool? allowEmulators,
    bool? logSecurityEvents,
    bool? blockMockLocation,
    SessionSecurityPolicy? sessionPolicy,
    Duration? sessionTimeout,
    ScreenshotPolicy? screenshotPolicy,
    SecurityLevel? level,
    bool? logAuthEvents,
    bool? showScreenSecurityWarning,
  }) {
    return SecurityConfig(
      enableCertificatePinning:
          enableCertificatePinning ?? this.enableCertificatePinning,
      strictCertificatePinning:
          strictCertificatePinning ?? this.strictCertificatePinning,
      allowPinningDebugBypass:
          allowPinningDebugBypass ?? this.allowPinningDebugBypass,
      requestTimeout: requestTimeout ?? this.requestTimeout,
      deviceIntegrityPolicy:
          deviceIntegrityPolicy ?? this.deviceIntegrityPolicy,
      enforceSecurityInDebug:
          enforceSecurityInDebug ?? this.enforceSecurityInDebug,
      allowEmulators: allowEmulators ?? this.allowEmulators,
      logSecurityEvents: logSecurityEvents ?? this.logSecurityEvents,
      blockMockLocation: blockMockLocation ?? this.blockMockLocation,
      sessionPolicy: sessionPolicy ?? this.sessionPolicy,
      sessionTimeout: sessionTimeout ?? this.sessionTimeout,
      screenshotPolicy: screenshotPolicy ?? this.screenshotPolicy,
      level: level ?? this.level,
      logAuthEvents: logAuthEvents ?? this.logAuthEvents,
      showScreenSecurityWarning:
          showScreenSecurityWarning ?? this.showScreenSecurityWarning,
    );
  }

  @override
  String toString() {
    return 'SecurityConfig('
        'certificatePinning: $enableCertificatePinning, '
        'strict: $strictCertificatePinning, '
        'debugBypass: $allowPinningDebugBypass, '
        'deviceIntegrity: $deviceIntegrityPolicy, '
        'enforceInDebug: $enforceSecurityInDebug'
        ')';
  }
}

/// Riverpod provider for security configuration
/// مزود Riverpod لإعدادات الأمان
final securityConfigProvider = StateProvider<SecurityConfig>((ref) {
  if (kReleaseMode) {
    return SecurityConfig.production;
  }
  return SecurityConfig.development;
});
