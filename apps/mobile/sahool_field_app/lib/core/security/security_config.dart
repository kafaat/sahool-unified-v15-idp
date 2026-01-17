import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'screen_security_service.dart';

/// SAHOOL Security Configuration
/// إعدادات الأمان للتطبيق
///
/// Centralized security settings and configurations for the SAHOOL app
/// Features:
/// - Token refresh settings
/// - Biometric authentication settings
/// - Session timeout configuration
/// - Security level management
/// - Screen security and screenshot prevention

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
  // Static Security Feature Flags (Global Settings)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Enable SSL certificate pinning globally
  /// When enabled, all HTTPS connections will validate against pinned certificates
  /// CRITICAL: Must be enabled in production to prevent MITM attacks
  static const bool certificatePinningGloballyEnabled = true;

  /// Enable root/jailbreak detection
  /// When enabled, the app will detect and respond to rooted/jailbroken devices
  static const bool enableRootDetection = true;

  /// Enable app tampering detection
  /// When enabled, the app will detect modifications to the binary
  static const bool enableTamperDetection = true;

  /// Enable debug detection
  /// When enabled, the app will detect if a debugger is attached
  static const bool enableDebugDetection = true;

  /// Enable emulator detection
  /// When enabled, the app will detect if running on an emulator
  static const bool enableEmulatorDetection = true;

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

  /// Whether to enable SSL certificate pinning
  /// SECURITY: This now defaults to true for all security levels except low
  /// Certificate pinning is critical for preventing MITM attacks
  bool get enableCertificatePinning {
    // Check static flag first - if globally disabled, return false
    if (!SecurityConfig.certificatePinningGloballyEnabled) {
      return false;
    }
    // Enable for medium, high, and maximum levels (disable only for low/dev)
    return level != SecurityLevel.low;
  }

  /// Whether to enforce strict certificate pinning (fail if no match)
  bool get strictCertificatePinning {
    return level == SecurityLevel.maximum;
  }

  /// Whether root detection is enabled for this security level
  bool get enableRootDetectionForLevel {
    return SecurityConfig.enableRootDetection && level != SecurityLevel.low;
  }

  /// Whether tamper detection is enabled for this security level
  bool get enableTamperDetectionForLevel {
    return SecurityConfig.enableTamperDetection &&
        (level == SecurityLevel.high || level == SecurityLevel.maximum);
  }

  /// Whether to allow certificate pinning bypass in debug mode
  bool get allowPinningDebugBypass {
    return level != SecurityLevel.maximum;
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
  // Device Security
  // ═══════════════════════════════════════════════════════════════════════════

  /// Whether to check for root/jailbreak on startup
  bool get checkRootJailbreak {
    return level != SecurityLevel.low;
  }

  /// Whether to check for emulator/simulator
  bool get checkEmulator {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Whether to check for developer mode
  bool get checkDeveloperMode {
    return level == SecurityLevel.maximum;
  }

  /// Whether to block app on rooted/jailbroken device
  bool get blockOnRootJailbreak {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Whether to block app on emulator
  bool get blockOnEmulator {
    return level == SecurityLevel.maximum;
  }

  /// Whether to allow security bypass in debug mode
  bool get allowSecurityBypassInDebug {
    return level != SecurityLevel.maximum;
  }

  /// Whether to prevent screenshots
  bool get preventScreenshots {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Screen Security Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Enable screenshot prevention
  bool get screenSecurityEnabled {
    // Enable for medium and above security levels
    return level != SecurityLevel.low;
  }

  /// Enable app-wide screenshot protection
  bool get appWideScreenProtection {
    // Only enable app-wide for high and maximum levels
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Screen types that should be secured based on security level
  Set<SecuredScreenType> get securedScreenTypes {
    switch (level) {
      case SecurityLevel.low:
        // Low: No screen protection
        return {};
      case SecurityLevel.medium:
        // Medium: Protect sensitive financial and auth screens
        return {
          SecuredScreenType.authentication,
          SecuredScreenType.wallet,
        };
      case SecurityLevel.high:
        // High: Protect all sensitive screens
        return {
          SecuredScreenType.authentication,
          SecuredScreenType.wallet,
          SecuredScreenType.personalData,
          SecuredScreenType.evidencePhotos,
        };
      case SecurityLevel.maximum:
        // Maximum: Protect all screens app-wide
        return {
          SecuredScreenType.all,
        };
    }
  }

  /// Check if a specific screen type should be secured
  bool shouldSecureScreen(SecuredScreenType screenType) {
    final types = securedScreenTypes;
    // If 'all' is in the set, secure everything
    if (types.contains(SecuredScreenType.all)) return true;
    // Otherwise check if the specific type is in the set
    return types.contains(screenType);
  }

  /// Show warning message when screen security is active
  bool get showScreenSecurityWarning {
    switch (level) {
      case SecurityLevel.low:
        return false;
      case SecurityLevel.medium:
        return true; // Show once to educate users
      case SecurityLevel.high:
      case SecurityLevel.maximum:
        return false; // Users at this level are already aware
    }
  }

  /// Detect and warn about screen recording
  bool get detectScreenRecording {
    return level == SecurityLevel.high || level == SecurityLevel.maximum;
  }

  /// Warning messages for screen security
  String get screenSecurityWarningAr {
    switch (level) {
      case SecurityLevel.low:
        return '';
      case SecurityLevel.medium:
        return 'لا يمكن أخذ لقطات شاشة في بعض الصفحات لحماية بياناتك المالية';
      case SecurityLevel.high:
        return 'لا يمكن أخذ لقطات شاشة في الصفحات الحساسة لحماية بياناتك';
      case SecurityLevel.maximum:
        return 'لا يمكن أخذ لقطات شاشة في التطبيق لحماية بياناتك السرية';
    }
  }

  String get screenSecurityWarningEn {
    switch (level) {
      case SecurityLevel.low:
        return '';
      case SecurityLevel.medium:
        return 'Screenshots are disabled on financial screens to protect your data';
      case SecurityLevel.high:
        return 'Screenshots are disabled on sensitive screens to protect your data';
      case SecurityLevel.maximum:
        return 'Screenshots are disabled app-wide to protect your confidential data';
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
/// Default to SecurityLevel.high to ensure certificate pinning is enabled
/// This provides protection against MITM attacks in production
/// Use SecurityLevel.medium only for local development with explicit override
final securityConfigProvider = StateProvider<SecurityConfig>((ref) {
  // SECURITY: Always default to high security to enable certificate pinning
  // Certificate pinning is only enabled at high and maximum levels
  return const SecurityConfig(level: SecurityLevel.high);
});

/// Provider to get current security level
final securityLevelProvider = Provider<SecurityLevel>((ref) {
  return ref.watch(securityConfigProvider).level;
});
