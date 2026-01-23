import 'package:flutter/foundation.dart';
import 'env_config.dart';

/// SAHOOL Security Configuration
/// تكوين الأمان لتطبيق سهول
///
/// This class centralizes all security-related configuration options.
/// Security features are enabled by default in production and can be
/// customized via environment variables or dart-define.
///
/// ## Usage:
/// ```dart
/// if (SecurityConfig.enableCertificatePinning) {
///   certificatePinningService.configureDio(dio);
/// }
/// ```
///
/// ## Build with security options:
/// ```bash
/// flutter build apk --release \
///   --dart-define=ENABLE_CERTIFICATE_PINNING=true \
///   --dart-define=ENABLE_DEVICE_INTEGRITY=true
/// ```
class SecurityConfig {
  SecurityConfig._();

  // ═══════════════════════════════════════════════════════════════════════════
  // Core Security Features
  // ═══════════════════════════════════════════════════════════════════════════

  /// Enable SSL Certificate Pinning
  /// تفعيل تثبيت شهادات SSL
  ///
  /// When enabled, the app will validate SSL certificates against pinned
  /// fingerprints. This prevents man-in-the-middle attacks.
  ///
  /// Default: true in production, false in development
  static bool get enableCertificatePinning {
    // Check dart-define first
    const defined = bool.fromEnvironment(
      'ENABLE_CERTIFICATE_PINNING',
      defaultValue: false,
    );
    if (defined) return true;

    // In production, default to enabled
    if (EnvConfig.isProduction) return true;

    // In staging, also enable for testing
    if (EnvConfig.isStaging) return true;

    // In development, disable for easier testing
    return false;
  }

  /// Enable Device Integrity Checks
  /// تفعيل فحوصات سلامة الجهاز
  ///
  /// When enabled, the app will detect:
  /// - Jailbroken/Rooted devices
  /// - Running on emulators
  /// - Debugging tools (Frida, etc.)
  ///
  /// Default: true in production, false in development
  static bool get enableDeviceIntegrity {
    const defined = bool.fromEnvironment(
      'ENABLE_DEVICE_INTEGRITY',
      defaultValue: false,
    );
    if (defined) return true;

    if (EnvConfig.isProduction) return true;
    if (EnvConfig.isStaging) return true;

    return false;
  }

  /// Enable Biometric Authentication
  /// تفعيل المصادقة البيومترية
  ///
  /// When enabled, users can use Face ID, Touch ID, or fingerprint
  /// to authenticate instead of PIN/password.
  static bool get enableBiometricAuth {
    const defined = bool.fromEnvironment(
      'ENABLE_BIOMETRIC_AUTH',
      defaultValue: false,
    );
    if (defined) return true;

    // Enable by default in all environments
    return true;
  }

  /// Enable Secure Storage for Sensitive Data
  /// تفعيل التخزين الآمن للبيانات الحساسة
  ///
  /// Uses platform-specific secure storage:
  /// - iOS: Keychain
  /// - Android: EncryptedSharedPreferences / Keystore
  static bool get enableSecureStorage {
    // Always enabled - this is a baseline security requirement
    return true;
  }

  /// Enable Database Encryption
  /// تفعيل تشفير قاعدة البيانات
  ///
  /// Uses SQLCipher to encrypt the local SQLite database.
  /// This protects data at rest.
  static bool get enableDatabaseEncryption {
    const defined = bool.fromEnvironment(
      'ENABLE_DATABASE_ENCRYPTION',
      defaultValue: false,
    );
    if (defined) return true;

    // Enable by default in production/staging
    if (EnvConfig.isProduction || EnvConfig.isStaging) return true;

    // Disable in development for easier debugging
    return false;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Development/Debug Options
  // ═══════════════════════════════════════════════════════════════════════════

  /// Allow Debug Mode Bypass
  /// السماح بتجاوز وضع التصحيح
  ///
  /// When enabled and running in debug mode, security checks may be relaxed
  /// to facilitate development. NEVER enable in production builds.
  static bool get allowDebugBypass {
    // Never allow bypass in production
    if (EnvConfig.isProduction) return false;

    // Allow bypass in debug mode for development
    return kDebugMode;
  }

  /// Allow Insecure Connections (HTTP)
  /// السماح بالاتصالات غير الآمنة
  ///
  /// Only enabled in development for local testing.
  static bool get allowInsecureConnections {
    // Never in production
    if (EnvConfig.isProduction) return false;

    // Only in development
    return EnvConfig.isDevelopment;
  }

  /// Enable Security Debug Logging
  /// تفعيل سجلات تصحيح الأمان
  ///
  /// Logs security-related events for debugging.
  /// Automatically disabled in production.
  static bool get enableSecurityLogging {
    // Never log security details in production
    if (EnvConfig.isProduction) return false;

    return kDebugMode;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Token & Session Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Access Token Expiry (in minutes)
  /// مدة صلاحية رمز الوصول
  static int get accessTokenExpiryMinutes {
    const defined = int.fromEnvironment(
      'ACCESS_TOKEN_EXPIRY_MINUTES',
      defaultValue: 0,
    );
    if (defined > 0) return defined;

    // Default: 15 minutes
    return 15;
  }

  /// Refresh Token Expiry (in days)
  /// مدة صلاحية رمز التجديد
  static int get refreshTokenExpiryDays {
    const defined = int.fromEnvironment(
      'REFRESH_TOKEN_EXPIRY_DAYS',
      defaultValue: 0,
    );
    if (defined > 0) return defined;

    // Default: 7 days
    return 7;
  }

  /// Session Idle Timeout (in minutes)
  /// مهلة الخمول للجلسة
  static int get sessionIdleTimeoutMinutes {
    const defined = int.fromEnvironment(
      'SESSION_IDLE_TIMEOUT_MINUTES',
      defaultValue: 0,
    );
    if (defined > 0) return defined;

    // Default: 30 minutes
    return 30;
  }

  /// Maximum Failed Login Attempts
  /// الحد الأقصى لمحاولات تسجيل الدخول الفاشلة
  static int get maxFailedLoginAttempts {
    const defined = int.fromEnvironment(
      'MAX_FAILED_LOGIN_ATTEMPTS',
      defaultValue: 0,
    );
    if (defined > 0) return defined;

    // Default: 5 attempts
    return 5;
  }

  /// Lockout Duration (in minutes)
  /// مدة القفل بعد المحاولات الفاشلة
  static int get lockoutDurationMinutes {
    const defined = int.fromEnvironment(
      'LOCKOUT_DURATION_MINUTES',
      defaultValue: 0,
    );
    if (defined > 0) return defined;

    // Default: 15 minutes
    return 15;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // PIN & Password Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Minimum PIN Length
  /// الحد الأدنى لطول رمز PIN
  static int get minPinLength {
    const defined = int.fromEnvironment('MIN_PIN_LENGTH', defaultValue: 0);
    if (defined > 0) return defined;

    return 6;
  }

  /// Minimum Password Length
  /// الحد الأدنى لطول كلمة المرور
  static int get minPasswordLength {
    const defined = int.fromEnvironment('MIN_PASSWORD_LENGTH', defaultValue: 0);
    if (defined > 0) return defined;

    return 8;
  }

  /// Require Mixed Case in Password
  /// طلب أحرف كبيرة وصغيرة في كلمة المرور
  static bool get requireMixedCase {
    const defined = bool.fromEnvironment(
      'REQUIRE_MIXED_CASE',
      defaultValue: false,
    );
    if (defined) return true;

    // Require in production
    return EnvConfig.isProduction;
  }

  /// Require Numbers in Password
  /// طلب أرقام في كلمة المرور
  static bool get requireNumbers {
    return true;
  }

  /// Require Special Characters in Password
  /// طلب رموز خاصة في كلمة المرور
  static bool get requireSpecialChars {
    const defined = bool.fromEnvironment(
      'REQUIRE_SPECIAL_CHARS',
      defaultValue: false,
    );
    if (defined) return true;

    // Require in production
    return EnvConfig.isProduction;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Network Security Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Allowed API Hosts
  /// المضيفين المسموح بهم للـ API
  static List<String> get allowedHosts {
    return [
      'api.sahool.app',
      'api-staging.sahool.app',
      'api.sahool.io',
      '*.sahool.io',
      // Development hosts
      if (EnvConfig.isDevelopment) ...[
        'localhost',
        '127.0.0.1',
        '10.0.2.2', // Android Emulator
        '192.168.0.0/16', // Local network
      ],
    ];
  }

  /// Request Timeout (in seconds)
  /// مهلة الطلبات
  static int get requestTimeoutSeconds {
    const defined = int.fromEnvironment(
      'REQUEST_TIMEOUT_SECONDS',
      defaultValue: 0,
    );
    if (defined > 0) return defined;

    return 30;
  }

  /// Maximum Retry Attempts
  /// الحد الأقصى لمحاولات إعادة المحاولة
  static int get maxRetryAttempts {
    const defined = int.fromEnvironment('MAX_RETRY_ATTEMPTS', defaultValue: 0);
    if (defined > 0) return defined;

    return 3;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Debug Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all security configuration as a map (for debugging)
  static Map<String, dynamic> toDebugMap() {
    return {
      'environment': EnvConfig.environment.name,
      'features': {
        'certificatePinning': enableCertificatePinning,
        'deviceIntegrity': enableDeviceIntegrity,
        'biometricAuth': enableBiometricAuth,
        'secureStorage': enableSecureStorage,
        'databaseEncryption': enableDatabaseEncryption,
      },
      'debug': {
        'allowDebugBypass': allowDebugBypass,
        'allowInsecureConnections': allowInsecureConnections,
        'enableSecurityLogging': enableSecurityLogging,
      },
      'tokens': {
        'accessTokenExpiry': '${accessTokenExpiryMinutes}m',
        'refreshTokenExpiry': '${refreshTokenExpiryDays}d',
        'sessionIdleTimeout': '${sessionIdleTimeoutMinutes}m',
      },
      'auth': {
        'maxFailedAttempts': maxFailedLoginAttempts,
        'lockoutDuration': '${lockoutDurationMinutes}m',
        'minPinLength': minPinLength,
        'minPasswordLength': minPasswordLength,
      },
      'network': {
        'requestTimeout': '${requestTimeoutSeconds}s',
        'maxRetryAttempts': maxRetryAttempts,
        'allowedHosts': allowedHosts.take(3).join(', ') + '...',
      },
    };
  }

  /// Print security configuration (debug only)
  static void printConfig() {
    if (!kDebugMode) return;

    // ignore: avoid_print
    print('''

╔════════════════════════════════════════════════════════════╗
║              SAHOOL Security Configuration                  ║
╠════════════════════════════════════════════════════════════╣
║ Environment: ${EnvConfig.environment.name.padRight(45)}║
╠════════════════════════════════════════════════════════════╣
║ Features:                                                   ║
║   Certificate Pinning: ${(enableCertificatePinning ? "✓ Enabled" : "✗ Disabled").padRight(35)}║
║   Device Integrity: ${(enableDeviceIntegrity ? "✓ Enabled" : "✗ Disabled").padRight(38)}║
║   Biometric Auth: ${(enableBiometricAuth ? "✓ Enabled" : "✗ Disabled").padRight(40)}║
║   Database Encryption: ${(enableDatabaseEncryption ? "✓ Enabled" : "✗ Disabled").padRight(35)}║
╠════════════════════════════════════════════════════════════╣
║ Debug Options:                                              ║
║   Debug Bypass: ${(allowDebugBypass ? "⚠️ Allowed" : "✓ Blocked").padRight(42)}║
║   Insecure Connections: ${(allowInsecureConnections ? "⚠️ Allowed" : "✓ Blocked").padRight(34)}║
╚════════════════════════════════════════════════════════════╝
''');
  }
}
