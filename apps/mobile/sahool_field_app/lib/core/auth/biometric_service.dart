import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';
import '../utils/app_logger.dart';
import '../security/security_audit_service.dart';
import 'secure_storage_service.dart';

/// SAHOOL Biometric Authentication Service
/// خدمة المصادقة بالبصمة
///
/// Features:
/// - Fingerprint authentication
/// - Face ID support
/// - Fallback to device credentials
/// - Lockout handling after repeated failures
/// - Secure session validation
/// - Security audit logging for all attempts

final biometricServiceProvider = Provider<BiometricService>((ref) {
  return BiometricService(
    secureStorage: ref.read(secureStorageProvider),
    auditService: ref.read(securityAuditServiceProvider),
  );
});

/// Biometric authentication result
class BiometricResult {
  final bool success;
  final String? errorCode;
  final String? errorMessage;
  final int? remainingAttempts;
  final Duration? lockoutRemaining;

  const BiometricResult({
    required this.success,
    this.errorCode,
    this.errorMessage,
    this.remainingAttempts,
    this.lockoutRemaining,
  });

  factory BiometricResult.success() => const BiometricResult(success: true);

  factory BiometricResult.failed({
    required String code,
    required String message,
    int? remainingAttempts,
    Duration? lockoutRemaining,
  }) =>
      BiometricResult(
        success: false,
        errorCode: code,
        errorMessage: message,
        remainingAttempts: remainingAttempts,
        lockoutRemaining: lockoutRemaining,
      );
}

class BiometricService {
  final LocalAuthentication _localAuth = LocalAuthentication();
  final SecureStorageService secureStorage;
  final SecurityAuditService? auditService;

  // Maximum consecutive failures before lockout
  static const _maxFailures = 5;

  BiometricService({required this.secureStorage, this.auditService});

  // ═══════════════════════════════════════════════════════════════════════════
  // Availability Checks
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if biometric authentication is available on device
  Future<bool> isAvailable() async {
    try {
      // Check if device supports biometrics
      final canCheckBiometrics = await _localAuth.canCheckBiometrics;
      final isDeviceSupported = await _localAuth.isDeviceSupported();

      return canCheckBiometrics || isDeviceSupported;
    } on PlatformException catch (e) {
      AppLogger.e('Biometric availability check failed', error: e);
      return false;
    }
  }

  /// Get available biometric types
  Future<List<BiometricType>> getAvailableBiometrics() async {
    try {
      return await _localAuth.getAvailableBiometrics();
    } on PlatformException catch (e) {
      AppLogger.e('Failed to get available biometrics', error: e);
      return [];
    }
  }

  /// Check if fingerprint is available
  Future<bool> isFingerprintAvailable() async {
    final biometrics = await getAvailableBiometrics();
    return biometrics.contains(BiometricType.fingerprint);
  }

  /// Check if face ID is available
  Future<bool> isFaceIdAvailable() async {
    final biometrics = await getAvailableBiometrics();
    return biometrics.contains(BiometricType.face);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Enable/Disable
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if biometric login is enabled by user
  Future<bool> isEnabled() async {
    return secureStorage.isBiometricEnabled();
  }

  /// Enable biometric login
  Future<bool> enable() async {
    // First verify that biometric is available
    if (!await isAvailable()) {
      throw BiometricException('البصمة غير متاحة على هذا الجهاز');
    }

    // Authenticate to confirm user identity
    final authenticated = await authenticate(
      reason: 'قم بالتحقق لتفعيل تسجيل الدخول بالبصمة',
    );

    if (authenticated) {
      await secureStorage.setBiometricEnabled(true);
      AppLogger.i('Biometric login enabled');
      return true;
    }

    return false;
  }

  /// Disable biometric login
  Future<void> disable() async {
    await secureStorage.setBiometricEnabled(false);
    AppLogger.i('Biometric login disabled');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Authentication
  // ═══════════════════════════════════════════════════════════════════════════

  /// Authenticate with biometric (returns simple bool for backward compatibility)
  Future<bool> authenticate({
    required String reason,
    bool biometricOnly = false,
  }) async {
    final result = await authenticateWithResult(
      reason: reason,
      biometricOnly: biometricOnly,
    );

    if (!result.success && result.errorCode != null) {
      throw BiometricException(
        result.errorMessage ?? 'فشل التحقق من البصمة',
        code: result.errorCode,
      );
    }

    return result.success;
  }

  /// Authenticate with biometric (returns detailed result)
  Future<BiometricResult> authenticateWithResult({
    required String reason,
    bool biometricOnly = false,
  }) async {
    try {
      AppLogger.i('Biometric authentication requested', tag: 'BIOMETRIC');

      // Check for lockout first
      if (await secureStorage.isBiometricLockedOut()) {
        final remaining = await secureStorage.getBiometricLockoutRemaining();
        AppLogger.w('Biometric is locked out', tag: 'BIOMETRIC');
        // Log lockout attempt to security audit
        await auditService?.logBiometricLockout(
          lockoutDuration: remaining ?? const Duration(minutes: 30),
          failedAttempts: _maxFailures,
        );
        return BiometricResult.failed(
          code: 'LOCKED_OUT',
          message: 'تم قفل البصمة. حاول بعد ${_formatDuration(remaining)}',
          lockoutRemaining: remaining,
        );
      }

      final authenticated = await _localAuth.authenticate(
        localizedReason: reason,
        options: AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: biometricOnly,
          useErrorDialogs: true,
          sensitiveTransaction: true,
        ),
      );

      if (authenticated) {
        AppLogger.i('Biometric authentication successful', tag: 'BIOMETRIC');
        // Reset failure count on success
        await secureStorage.resetBiometricLockout();
        // Log success to security audit
        await auditService?.logBiometricAttempt(success: true);
        return BiometricResult.success();
      } else {
        AppLogger.w('Biometric authentication cancelled', tag: 'BIOMETRIC');
        // User cancelled - don't count as failure but log it
        await auditService?.logBiometricAttempt(
          success: false,
          errorCode: 'CANCELLED',
        );
        return BiometricResult.failed(
          code: 'CANCELLED',
          message: 'تم إلغاء التحقق من البصمة',
        );
      }
    } on PlatformException catch (e) {
      AppLogger.e('Biometric authentication error', tag: 'BIOMETRIC', error: e);

      // Record failure for lockout tracking
      final failureCount = await secureStorage.recordBiometricFailure();
      final remainingAttempts = _maxFailures - failureCount;

      // Log failure to security audit
      await auditService?.logBiometricAttempt(
        success: false,
        errorCode: e.code,
        remainingAttempts: remainingAttempts > 0 ? remainingAttempts : 0,
      );

      switch (e.code) {
        case 'NotAvailable':
          return BiometricResult.failed(
            code: 'NOT_AVAILABLE',
            message: 'البصمة غير متاحة',
          );
        case 'NotEnrolled':
          return BiometricResult.failed(
            code: 'NOT_ENROLLED',
            message: 'لم يتم تسجيل بصمة على هذا الجهاز',
          );
        case 'LockedOut':
          final remaining = await secureStorage.getBiometricLockoutRemaining();
          return BiometricResult.failed(
            code: 'LOCKED_OUT',
            message: 'تم قفل البصمة. حاول بعد ${_formatDuration(remaining)}',
            lockoutRemaining: remaining,
          );
        case 'PermanentlyLockedOut':
          return BiometricResult.failed(
            code: 'PERMANENTLY_LOCKED_OUT',
            message: 'تم قفل البصمة بشكل دائم. استخدم كلمة المرور',
          );
        default:
          // Check if we should lock out
          if (remainingAttempts <= 0) {
            final lockoutRemaining =
                await secureStorage.getBiometricLockoutRemaining();
            return BiometricResult.failed(
              code: 'LOCKED_OUT',
              message: 'تم قفل البصمة بعد محاولات فاشلة متعددة',
              lockoutRemaining: lockoutRemaining,
            );
          }

          return BiometricResult.failed(
            code: 'FAILED',
            message: remainingAttempts > 0
                ? 'فشل التحقق من البصمة. المحاولات المتبقية: $remainingAttempts'
                : 'فشل التحقق من البصمة',
            remainingAttempts: remainingAttempts > 0 ? remainingAttempts : null,
          );
      }
    }
  }

  /// Format duration for display
  String _formatDuration(Duration? duration) {
    if (duration == null) return 'بضع دقائق';

    final minutes = duration.inMinutes;
    if (minutes <= 1) return 'دقيقة واحدة';
    if (minutes < 10) return '$minutes دقائق';
    return '$minutes دقيقة';
  }

  /// Authenticate with fallback to device credentials
  Future<bool> authenticateWithFallback({
    required String reason,
  }) async {
    return authenticate(
      reason: reason,
      biometricOnly: false,
    );
  }

  /// Cancel authentication
  Future<void> cancelAuthentication() async {
    try {
      await _localAuth.stopAuthentication();
    } catch (e) {
      AppLogger.e('Failed to cancel authentication',
          error: e, tag: 'BIOMETRIC');
    }
  }

  /// Check if biometric is currently locked out
  Future<bool> isLockedOut() async {
    return secureStorage.isBiometricLockedOut();
  }

  /// Get remaining lockout time
  Future<Duration?> getLockoutRemaining() async {
    return secureStorage.getBiometricLockoutRemaining();
  }

  /// Reset lockout (call after successful password authentication)
  Future<void> resetLockout() async {
    await secureStorage.resetBiometricLockout();
    AppLogger.i('Biometric lockout reset', tag: 'BIOMETRIC');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get biometric type display name in Arabic
  String getBiometricTypeName(BiometricType type) {
    switch (type) {
      case BiometricType.fingerprint:
        return 'بصمة الإصبع';
      case BiometricType.face:
        return 'بصمة الوجه';
      case BiometricType.iris:
        return 'بصمة العين';
      case BiometricType.strong:
        return 'مصادقة قوية';
      case BiometricType.weak:
        return 'مصادقة ضعيفة';
    }
  }

  /// Get primary biometric type name
  Future<String> getPrimaryBiometricName() async {
    final biometrics = await getAvailableBiometrics();

    if (biometrics.contains(BiometricType.face)) {
      return 'بصمة الوجه';
    } else if (biometrics.contains(BiometricType.fingerprint)) {
      return 'بصمة الإصبع';
    } else if (biometrics.isNotEmpty) {
      return getBiometricTypeName(biometrics.first);
    }

    return 'البصمة';
  }

  /// Get biometric icon name
  Future<String> getBiometricIconName() async {
    final biometrics = await getAvailableBiometrics();

    if (biometrics.contains(BiometricType.face)) {
      return 'face';
    } else if (biometrics.contains(BiometricType.fingerprint)) {
      return 'fingerprint';
    }

    return 'security';
  }
}

/// Biometric exception
class BiometricException implements Exception {
  final String message;
  final String? code;

  BiometricException(this.message, {this.code});

  @override
  String toString() => message;
}
