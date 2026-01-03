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

  const SecurityConfig({
    this.enableCertificatePinning = false,
    this.strictCertificatePinning = false,
    this.allowPinningDebugBypass = true,
    this.requestTimeout = const Duration(seconds: 30),
    this.deviceIntegrityPolicy = DeviceIntegrityPolicy.disabled,
    this.enforceSecurityInDebug = false,
    this.allowEmulators = true,
    this.logSecurityEvents = true,
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
  );

  /// Development security configuration
  /// Disables certificate pinning for local development
  /// تكوين الأمان للتطوير
  static const development = SecurityConfig(
    enableCertificatePinning: false,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    requestTimeout: Duration(seconds: 30),
    deviceIntegrityPolicy: DeviceIntegrityPolicy.log,
    enforceSecurityInDebug: false,
    allowEmulators: true,
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
  }) {
    return SecurityConfig(
      enableCertificatePinning: enableCertificatePinning ?? this.enableCertificatePinning,
      strictCertificatePinning: strictCertificatePinning ?? this.strictCertificatePinning,
      allowPinningDebugBypass: allowPinningDebugBypass ?? this.allowPinningDebugBypass,
      requestTimeout: requestTimeout ?? this.requestTimeout,
      deviceIntegrityPolicy: deviceIntegrityPolicy ?? this.deviceIntegrityPolicy,
      enforceSecurityInDebug: enforceSecurityInDebug ?? this.enforceSecurityInDebug,
      allowEmulators: allowEmulators ?? this.allowEmulators,
      logSecurityEvents: logSecurityEvents ?? this.logSecurityEvents,
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
