import 'package:flutter/foundation.dart';

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

/// Screenshot Prevention Policy
/// سياسة منع لقطات الشاشة
enum ScreenshotPolicy {
  /// Allow screenshots everywhere
  /// السماح بلقطات الشاشة في كل مكان
  disabled,

  /// Prevent screenshots on sensitive screens only
  /// منع لقطات الشاشة في الشاشات الحساسة فقط
  sensitiveOnly,

  /// Prevent screenshots on all screens
  /// منع لقطات الشاشة في جميع الشاشات
  allScreens,
}

/// Session Security Policy
/// سياسة أمان الجلسة
enum SessionSecurityPolicy {
  /// No session timeout
  /// لا توجد مهلة للجلسة
  disabled,

  /// Extended timeout (2 hours)
  /// مهلة ممتدة
  relaxed,

  /// Standard timeout (15 minutes)
  /// مهلة قياسية
  standard,

  /// Strict timeout (5 minutes)
  /// مهلة صارمة
  strict,
}

/// Security Configuration
/// إعدادات الأمان
///
/// Centralized security settings for the SAHOOL mobile app
/// Controls certificate pinning, device integrity, session management,
/// screenshot prevention, and other security features.
///
/// إعدادات الأمان المركزية لتطبيق SAHOOL للهاتف المحمول
/// يتحكم في تثبيت الشهادات وسلامة الجهاز وإدارة الجلسات
/// ومنع لقطات الشاشة وميزات الأمان الأخرى

class SecurityConfig {
  // ═══════════════════════════════════════════════════════════════════════════
  // SSL/TLS Certificate Pinning - تثبيت شهادات SSL/TLS
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether to enable SSL certificate pinning
  final bool enableCertificatePinning;

  /// Whether to enforce strict certificate pinning (fail if no match)
  final bool strictCertificatePinning;

  /// Whether to allow certificate pinning bypass in debug mode
  final bool allowPinningDebugBypass;

  // ═══════════════════════════════════════════════════════════════════════════
  // Device Security - أمان الجهاز
  // ═══════════════════════════════════════════════════════════════════════════

  /// Device integrity policy (root/jailbreak detection)
  /// سياسة سلامة الجهاز (كشف الروت/الجلبريك)
  final DeviceIntegrityPolicy deviceIntegrityPolicy;

  /// Whether to enforce security checks in debug mode
  final bool enforceSecurityInDebug;

  /// Whether to allow app usage on emulators/simulators
  final bool allowEmulators;

  /// Whether to block on mock location detection
  final bool blockMockLocation;

  // ═══════════════════════════════════════════════════════════════════════════
  // Session Management - إدارة الجلسات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Session security policy
  final SessionSecurityPolicy sessionPolicy;

  /// Session timeout duration (for standard policy)
  final Duration sessionTimeout;

  /// Background lock threshold (how long in background before requiring re-auth)
  final Duration backgroundLockThreshold;

  /// Whether to require biometric re-authentication after background
  final bool requireBiometricAfterBackground;

  /// Whether to show session expiry warning
  final bool showSessionExpiryWarning;

  // ═══════════════════════════════════════════════════════════════════════════
  // Screenshot Prevention - منع لقطات الشاشة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Screenshot prevention policy
  final ScreenshotPolicy screenshotPolicy;

  /// Whether to blur app content when in background
  final bool blurOnBackground;

  /// Blur intensity (sigma) when app is in background
  final double backgroundBlurSigma;

  // ═══════════════════════════════════════════════════════════════════════════
  // Secure Input - الإدخال الآمن
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether to clear clipboard after paste in sensitive fields
  final bool clearClipboardAfterPaste;

  /// Delay before clearing clipboard (in seconds)
  final int clipboardClearDelay;

  /// Whether to disable autocomplete in sensitive fields
  final bool disableAutocompleteInSensitiveFields;

  // ═══════════════════════════════════════════════════════════════════════════
  // Network & Request Security - أمان الشبكة والطلبات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Request timeout duration
  final Duration requestTimeout;

  /// Whether to log security events to analytics
  final bool logSecurityEvents;

  const SecurityConfig({
    // Certificate pinning
    this.enableCertificatePinning = false,
    this.strictCertificatePinning = false,
    this.allowPinningDebugBypass = true,
    // Device security
    this.deviceIntegrityPolicy = DeviceIntegrityPolicy.disabled,
    this.enforceSecurityInDebug = false,
    this.allowEmulators = true,
    this.blockMockLocation = false,
    // Session management
    this.sessionPolicy = SessionSecurityPolicy.standard,
    this.sessionTimeout = const Duration(minutes: 15),
    this.backgroundLockThreshold = const Duration(minutes: 1),
    this.requireBiometricAfterBackground = true,
    this.showSessionExpiryWarning = true,
    // Screenshot prevention
    this.screenshotPolicy = ScreenshotPolicy.disabled,
    this.blurOnBackground = true,
    this.backgroundBlurSigma = 20.0,
    // Secure input
    this.clearClipboardAfterPaste = true,
    this.clipboardClearDelay = 30,
    this.disableAutocompleteInSensitiveFields = true,
    // Network
    this.requestTimeout = const Duration(seconds: 30),
    this.logSecurityEvents = true,
  });

  /// Production security configuration
  /// Enables all security features for production builds
  /// تكوين الأمان للإنتاج - تمكين جميع ميزات الأمان
  static const production = SecurityConfig(
    // Certificate pinning - strict
    enableCertificatePinning: true,
    strictCertificatePinning: true,
    allowPinningDebugBypass: false,
    // Device security - block rooted
    deviceIntegrityPolicy: DeviceIntegrityPolicy.block,
    enforceSecurityInDebug: false,
    allowEmulators: false,
    blockMockLocation: true,
    // Session management - standard timeout
    sessionPolicy: SessionSecurityPolicy.standard,
    sessionTimeout: Duration(minutes: 15),
    backgroundLockThreshold: Duration(seconds: 30),
    requireBiometricAfterBackground: true,
    showSessionExpiryWarning: true,
    // Screenshot prevention - sensitive screens
    screenshotPolicy: ScreenshotPolicy.sensitiveOnly,
    blurOnBackground: true,
    backgroundBlurSigma: 20.0,
    // Secure input - full protection
    clearClipboardAfterPaste: true,
    clipboardClearDelay: 30,
    disableAutocompleteInSensitiveFields: true,
    // Network
    requestTimeout: Duration(seconds: 20),
    logSecurityEvents: true,
  );

  /// Staging security configuration
  /// Enables security with some flexibility for testing
  /// تكوين الأمان للمرحلة التجريبية
  static const staging = SecurityConfig(
    // Certificate pinning - enabled but not strict
    enableCertificatePinning: true,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    // Device security - warn only
    deviceIntegrityPolicy: DeviceIntegrityPolicy.warn,
    enforceSecurityInDebug: false,
    allowEmulators: true,
    blockMockLocation: false,
    // Session management - relaxed
    sessionPolicy: SessionSecurityPolicy.relaxed,
    sessionTimeout: Duration(minutes: 30),
    backgroundLockThreshold: Duration(minutes: 2),
    requireBiometricAfterBackground: true,
    showSessionExpiryWarning: true,
    // Screenshot prevention - sensitive only
    screenshotPolicy: ScreenshotPolicy.sensitiveOnly,
    blurOnBackground: true,
    backgroundBlurSigma: 15.0,
    // Secure input
    clearClipboardAfterPaste: true,
    clipboardClearDelay: 60,
    disableAutocompleteInSensitiveFields: true,
    // Network
    requestTimeout: Duration(seconds: 30),
    logSecurityEvents: true,
  );

  /// Development security configuration
  /// Disables most security features for local development
  /// تكوين الأمان للتطوير - معطل للسماح بالتطوير على المحاكيات
  static const development = SecurityConfig(
    // Certificate pinning - disabled
    enableCertificatePinning: false,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    // Device security - disabled
    deviceIntegrityPolicy: DeviceIntegrityPolicy.disabled,
    enforceSecurityInDebug: false,
    allowEmulators: true,
    blockMockLocation: false,
    // Session management - disabled
    sessionPolicy: SessionSecurityPolicy.disabled,
    sessionTimeout: Duration(hours: 2),
    backgroundLockThreshold: Duration(minutes: 5),
    requireBiometricAfterBackground: false,
    showSessionExpiryWarning: false,
    // Screenshot prevention - disabled
    screenshotPolicy: ScreenshotPolicy.disabled,
    blurOnBackground: false,
    backgroundBlurSigma: 0,
    // Secure input - minimal
    clearClipboardAfterPaste: false,
    clipboardClearDelay: 120,
    disableAutocompleteInSensitiveFields: false,
    // Network
    requestTimeout: Duration(seconds: 30),
    logSecurityEvents: false,
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

  /// Get session timeout based on policy
  Duration getEffectiveSessionTimeout() {
    switch (sessionPolicy) {
      case SessionSecurityPolicy.disabled:
        return const Duration(days: 365); // Effectively never
      case SessionSecurityPolicy.relaxed:
        return const Duration(hours: 2);
      case SessionSecurityPolicy.standard:
        return sessionTimeout;
      case SessionSecurityPolicy.strict:
        return const Duration(minutes: 5);
    }
  }

  /// Check if screenshot prevention is enabled
  bool get isScreenshotPreventionEnabled =>
      screenshotPolicy != ScreenshotPolicy.disabled;

  /// Check if session timeout is enabled
  bool get isSessionTimeoutEnabled =>
      sessionPolicy != SessionSecurityPolicy.disabled;

  /// Copy configuration with updated values
  SecurityConfig copyWith({
    bool? enableCertificatePinning,
    bool? strictCertificatePinning,
    bool? allowPinningDebugBypass,
    DeviceIntegrityPolicy? deviceIntegrityPolicy,
    bool? enforceSecurityInDebug,
    bool? allowEmulators,
    bool? blockMockLocation,
    SessionSecurityPolicy? sessionPolicy,
    Duration? sessionTimeout,
    Duration? backgroundLockThreshold,
    bool? requireBiometricAfterBackground,
    bool? showSessionExpiryWarning,
    ScreenshotPolicy? screenshotPolicy,
    bool? blurOnBackground,
    double? backgroundBlurSigma,
    bool? clearClipboardAfterPaste,
    int? clipboardClearDelay,
    bool? disableAutocompleteInSensitiveFields,
    Duration? requestTimeout,
    bool? logSecurityEvents,
  }) {
    return SecurityConfig(
      enableCertificatePinning: enableCertificatePinning ?? this.enableCertificatePinning,
      strictCertificatePinning: strictCertificatePinning ?? this.strictCertificatePinning,
      allowPinningDebugBypass: allowPinningDebugBypass ?? this.allowPinningDebugBypass,
      deviceIntegrityPolicy: deviceIntegrityPolicy ?? this.deviceIntegrityPolicy,
      enforceSecurityInDebug: enforceSecurityInDebug ?? this.enforceSecurityInDebug,
      allowEmulators: allowEmulators ?? this.allowEmulators,
      blockMockLocation: blockMockLocation ?? this.blockMockLocation,
      sessionPolicy: sessionPolicy ?? this.sessionPolicy,
      sessionTimeout: sessionTimeout ?? this.sessionTimeout,
      backgroundLockThreshold: backgroundLockThreshold ?? this.backgroundLockThreshold,
      requireBiometricAfterBackground: requireBiometricAfterBackground ?? this.requireBiometricAfterBackground,
      showSessionExpiryWarning: showSessionExpiryWarning ?? this.showSessionExpiryWarning,
      screenshotPolicy: screenshotPolicy ?? this.screenshotPolicy,
      blurOnBackground: blurOnBackground ?? this.blurOnBackground,
      backgroundBlurSigma: backgroundBlurSigma ?? this.backgroundBlurSigma,
      clearClipboardAfterPaste: clearClipboardAfterPaste ?? this.clearClipboardAfterPaste,
      clipboardClearDelay: clipboardClearDelay ?? this.clipboardClearDelay,
      disableAutocompleteInSensitiveFields: disableAutocompleteInSensitiveFields ?? this.disableAutocompleteInSensitiveFields,
      requestTimeout: requestTimeout ?? this.requestTimeout,
      logSecurityEvents: logSecurityEvents ?? this.logSecurityEvents,
    );
  }

  @override
  String toString() {
    return 'SecurityConfig('
        'certificatePinning: $enableCertificatePinning, '
        'strict: $strictCertificatePinning, '
        'deviceIntegrity: $deviceIntegrityPolicy, '
        'sessionPolicy: $sessionPolicy, '
        'screenshotPolicy: $screenshotPolicy, '
        'enforceInDebug: $enforceSecurityInDebug'
        ')';
  }
}
