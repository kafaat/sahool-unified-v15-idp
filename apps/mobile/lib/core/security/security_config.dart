import 'package:flutter/foundation.dart';

/// Security Configuration
/// إعدادات الأمان
///
/// Centralized security settings for the SAHOOL mobile app
/// Controls certificate pinning, encryption, and other security features

class SecurityConfig {
  /// Whether to enable SSL certificate pinning
  final bool enableCertificatePinning;

  /// Whether to enforce strict certificate pinning (fail if no match)
  final bool strictCertificatePinning;

  /// Whether to allow certificate pinning bypass in debug mode
  final bool allowPinningDebugBypass;

  /// Request timeout duration
  final Duration requestTimeout;

  const SecurityConfig({
    this.enableCertificatePinning = false,
    this.strictCertificatePinning = false,
    this.allowPinningDebugBypass = true,
    this.requestTimeout = const Duration(seconds: 30),
  });

  /// Production security configuration
  /// Enables all security features for production builds
  static const production = SecurityConfig(
    enableCertificatePinning: true,
    strictCertificatePinning: true,
    allowPinningDebugBypass: false,
    requestTimeout: Duration(seconds: 20),
  );

  /// Staging security configuration
  /// Enables security with some flexibility for testing
  static const staging = SecurityConfig(
    enableCertificatePinning: true,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    requestTimeout: Duration(seconds: 30),
  );

  /// Development security configuration
  /// Disables certificate pinning for local development
  static const development = SecurityConfig(
    enableCertificatePinning: false,
    strictCertificatePinning: false,
    allowPinningDebugBypass: true,
    requestTimeout: Duration(seconds: 30),
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
  }) {
    return SecurityConfig(
      enableCertificatePinning: enableCertificatePinning ?? this.enableCertificatePinning,
      strictCertificatePinning: strictCertificatePinning ?? this.strictCertificatePinning,
      allowPinningDebugBypass: allowPinningDebugBypass ?? this.allowPinningDebugBypass,
      requestTimeout: requestTimeout ?? this.requestTimeout,
    );
  }

  @override
  String toString() {
    return 'SecurityConfig('
        'certificatePinning: $enableCertificatePinning, '
        'strict: $strictCertificatePinning, '
        'debugBypass: $allowPinningDebugBypass'
        ')';
  }
}
