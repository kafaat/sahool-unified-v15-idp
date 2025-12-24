import 'package:flutter_riverpod/flutter_riverpod.dart';

/// SAHOOL Security Configuration
/// إعدادات الأمان للتطبيق
///
/// Centralized security settings and configurations for the SAHOOL app
/// Features:
/// - Token refresh settings
/// - Biometric authentication settings
/// - Session timeout configuration
/// - Security level management

/// Security level enumeration
enum SecurityLevel {
  /// Low security - longer sessions, optional biometric
  low('low', 'منخفض'),

  /// Medium security - standard settings
  medium('medium', 'متوسط'),

  /// High security - short sessions, required biometric
  high('high', 'مرتفع'),

  /// Maximum security - very short sessions, always require biometric
  maximum('maximum', 'أقصى');

  final String code;
  final String nameAr;

  const SecurityLevel(this.code, this.nameAr);

  static SecurityLevel fromCode(String code) {
    return SecurityLevel.values.firstWhere(
      (level) => level.code == code,
      orElse: () => SecurityLevel.medium,
    );
  }
}

/// Security configuration class
class SecurityConfig {
  final SecurityLevel level;

  const SecurityConfig({
    this.level = SecurityLevel.medium,
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Token Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Token refresh buffer time before expiry
  Duration get tokenRefreshBuffer {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(minutes: 10);
      case SecurityLevel.medium:
        return const Duration(minutes: 5);
      case SecurityLevel.high:
        return const Duration(minutes: 3);
      case SecurityLevel.maximum:
        return const Duration(minutes: 1);
    }
  }

  /// Maximum token lifetime
  Duration get maxTokenLifetime {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(hours: 12);
      case SecurityLevel.medium:
        return const Duration(hours: 8);
      case SecurityLevel.high:
        return const Duration(hours: 4);
      case SecurityLevel.maximum:
        return const Duration(hours: 1);
    }
  }

  /// Token refresh retry attempts
  int get maxRefreshRetries {
    switch (level) {
      case SecurityLevel.low:
        return 5;
      case SecurityLevel.medium:
        return 3;
      case SecurityLevel.high:
        return 2;
      case SecurityLevel.maximum:
        return 1;
    }
  }

  /// Initial retry delay for token refresh
  Duration get initialRetryDelay {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(seconds: 3);
      case SecurityLevel.medium:
        return const Duration(seconds: 2);
      case SecurityLevel.high:
        return const Duration(seconds: 1);
      case SecurityLevel.maximum:
        return const Duration(milliseconds: 500);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Session Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Session timeout duration
  Duration get sessionTimeout {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(hours: 24);
      case SecurityLevel.medium:
        return const Duration(hours: 8);
      case SecurityLevel.high:
        return const Duration(hours: 2);
      case SecurityLevel.maximum:
        return const Duration(minutes: 30);
    }
  }

  /// Inactivity timeout (auto-logout)
  Duration get inactivityTimeout {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(hours: 2);
      case SecurityLevel.medium:
        return const Duration(minutes: 30);
      case SecurityLevel.high:
        return const Duration(minutes: 15);
      case SecurityLevel.maximum:
        return const Duration(minutes: 5);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Biometric Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether biometric authentication is required
  bool get biometricRequired {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Whether to allow PIN fallback
  bool get allowPinFallback {
    return level != SecurityLevel.maximum;
  }

  /// Biometric timeout duration
  Duration get biometricTimeout {
    switch (level) {
      case SecurityLevel.low:
      case SecurityLevel.medium:
        return const Duration(seconds: 60);
      case SecurityLevel.high:
        return const Duration(seconds: 30);
      case SecurityLevel.maximum:
        return const Duration(seconds: 15);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Network Security
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether to enforce HTTPS only
  bool get httpsOnly {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Whether to validate SSL certificates
  bool get validateSslCertificates {
    return level != SecurityLevel.low;
  }

  /// Request timeout duration
  Duration get requestTimeout {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(seconds: 60);
      case SecurityLevel.medium:
        return const Duration(seconds: 30);
      case SecurityLevel.high:
        return const Duration(seconds: 20);
      case SecurityLevel.maximum:
        return const Duration(seconds: 10);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Data Security
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether to encrypt local database
  bool get encryptLocalDatabase {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Whether to clear cache on logout
  bool get clearCacheOnLogout {
    return level != SecurityLevel.low;
  }

  /// Whether to require re-authentication for sensitive operations
  bool get requireReAuthForSensitiveOps {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Password/PIN Requirements
  // ═══════════════════════════════════════════════════════════════════════════

  /// Minimum PIN length
  int get minPinLength {
    switch (level) {
      case SecurityLevel.low:
        return 4;
      case SecurityLevel.medium:
        return 4;
      case SecurityLevel.high:
        return 6;
      case SecurityLevel.maximum:
        return 8;
    }
  }

  /// Maximum login attempts before lockout
  int get maxLoginAttempts {
    switch (level) {
      case SecurityLevel.low:
        return 10;
      case SecurityLevel.medium:
        return 5;
      case SecurityLevel.high:
        return 3;
      case SecurityLevel.maximum:
        return 3;
    }
  }

  /// Lockout duration after max attempts
  Duration get lockoutDuration {
    switch (level) {
      case SecurityLevel.low:
        return const Duration(minutes: 5);
      case SecurityLevel.medium:
        return const Duration(minutes: 15);
      case SecurityLevel.high:
        return const Duration(minutes: 30);
      case SecurityLevel.maximum:
        return const Duration(hours: 1);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Logging and Monitoring
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether to log authentication events
  bool get logAuthEvents {
    return true; // Always log auth events
  }

  /// Whether to log sensitive data (only in debug)
  bool get logSensitiveData {
    return false; // Never log sensitive data in production
  }

  /// Whether to track failed login attempts
  bool get trackFailedAttempts {
    return level != SecurityLevel.low;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Copy configuration with new level
  SecurityConfig copyWith({SecurityLevel? level}) {
    return SecurityConfig(
      level: level ?? this.level,
    );
  }

  /// Get configuration description in Arabic
  String get descriptionAr {
    switch (level) {
      case SecurityLevel.low:
        return 'مستوى أمان منخفض - مناسب للاستخدام الشخصي';
      case SecurityLevel.medium:
        return 'مستوى أمان متوسط - مناسب للاستخدام العام';
      case SecurityLevel.high:
        return 'مستوى أمان مرتفع - مناسب للبيانات الحساسة';
      case SecurityLevel.maximum:
        return 'مستوى أمان أقصى - مناسب للبيانات السرية';
    }
  }

  @override
  String toString() {
    return 'SecurityConfig(level: ${level.nameAr})';
  }
}

/// Provider for security configuration
final securityConfigProvider = StateProvider<SecurityConfig>((ref) {
  return const SecurityConfig(level: SecurityLevel.medium);
});

/// Provider to get current security level
final securityLevelProvider = Provider<SecurityLevel>((ref) {
  return ref.watch(securityConfigProvider).level;
});
