import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:local_auth/local_auth.dart';
import '../utils/app_logger.dart';
import 'secure_storage_service.dart';

/// SAHOOL Biometric Authentication Service
/// خدمة المصادقة بالبصمة
///
/// Features:
/// - Fingerprint authentication (بصمة الإصبع)
/// - Face ID/Face recognition support (التعرف على الوجه)
/// - Fallback to PIN/password (رمز المرور الاحتياطي)
/// - Full Arabic localization (الترجمة الكاملة للعربية)
/// - Platform-specific biometric handling

final biometricServiceProvider = Provider<BiometricService>((ref) {
  return BiometricService(
    secureStorage: ref.read(secureStorageProvider),
  );
});

class BiometricService {
  final LocalAuthentication _localAuth = LocalAuthentication();
  final SecureStorageService secureStorage;

  BiometricService({required this.secureStorage});

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

  /// Authenticate with biometric
  /// المصادقة باستخدام البصمة
  Future<bool> authenticate({
    required String reason,
    bool biometricOnly = false,
    bool useErrorDialogs = true,
  }) async {
    try {
      AppLogger.i('Biometric authentication requested', tag: 'BIOMETRIC');

      final authenticated = await _localAuth.authenticate(
        localizedReason: reason,
        options: AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: biometricOnly,
          useErrorDialogs: useErrorDialogs,
          sensitiveTransaction: true,
        ),
      );

      if (authenticated) {
        AppLogger.i('Biometric authentication successful', tag: 'BIOMETRIC');
      } else {
        AppLogger.w('Biometric authentication cancelled', tag: 'BIOMETRIC');
      }

      return authenticated;
    } on PlatformException catch (e) {
      AppLogger.e('Biometric authentication error', tag: 'BIOMETRIC', error: e);
      throw _handleBiometricError(e);
    }
  }

  /// Handle biometric errors with Arabic messages
  /// معالجة أخطاء البصمة مع رسائل عربية
  BiometricException _handleBiometricError(PlatformException e) {
    switch (e.code) {
      case 'NotAvailable':
        return BiometricException(
          'البصمة غير متاحة على هذا الجهاز',
          code: 'NOT_AVAILABLE',
        );
      case 'NotEnrolled':
        return BiometricException(
          'لم يتم تسجيل بصمة على هذا الجهاز. يرجى تفعيل البصمة من إعدادات الجهاز',
          code: 'NOT_ENROLLED',
        );
      case 'LockedOut':
        return BiometricException(
          'تم قفل البصمة مؤقتاً بسبب كثرة المحاولات الفاشلة. حاول مرة أخرى بعد قليل',
          code: 'LOCKED_OUT',
        );
      case 'PermanentlyLockedOut':
        return BiometricException(
          'تم قفل البصمة بشكل دائم. استخدم رمز المرور أو كلمة السر الخاصة بالجهاز',
          code: 'PERMANENTLY_LOCKED_OUT',
        );
      case 'PasscodeNotSet':
        return BiometricException(
          'لم يتم تعيين رمز مرور للجهاز. يرجى تعيين رمز مرور أولاً',
          code: 'PASSCODE_NOT_SET',
        );
      case 'BiometricOnlyNotSupported':
        return BiometricException(
          'البصمة فقط غير مدعومة. يمكنك استخدام رمز المرور كبديل',
          code: 'BIOMETRIC_ONLY_NOT_SUPPORTED',
        );
      default:
        return BiometricException(
          'حدث خطأ في التحقق من البصمة: ${e.message ?? 'خطأ غير معروف'}',
          code: e.code,
        );
    }
  }

  /// Authenticate with fallback to device credentials (PIN/Password)
  /// المصادقة مع الرجوع لرمز المرور عند الحاجة
  Future<bool> authenticateWithFallback({
    required String reason,
  }) async {
    return authenticate(
      reason: reason,
      biometricOnly: false,
      useErrorDialogs: true,
    );
  }

  /// Authenticate for sensitive transactions
  /// المصادقة للعمليات الحساسة
  Future<bool> authenticateForSensitiveOperation({
    String? customReason,
  }) async {
    final reason = customReason ?? 'تأكيد هويتك لإتمام هذه العملية الحساسة';
    return authenticate(
      reason: reason,
      biometricOnly: false,
      useErrorDialogs: true,
    );
  }

  /// Quick authentication (biometric only, no PIN fallback)
  /// مصادقة سريعة (البصمة فقط، بدون رمز المرور)
  Future<bool> quickAuthenticate({
    String? customReason,
  }) async {
    final reason = customReason ?? 'استخدم البصمة للمتابعة';
    return authenticate(
      reason: reason,
      biometricOnly: true,
      useErrorDialogs: false,
    );
  }

  /// Cancel authentication
  Future<void> cancelAuthentication() async {
    try {
      await _localAuth.stopAuthentication();
    } catch (e) {
      AppLogger.e('Failed to cancel authentication', error: e);
    }
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
