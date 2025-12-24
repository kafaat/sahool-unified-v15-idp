import 'dart:convert';
import 'dart:math';
import 'package:crypto/crypto.dart';

/// SAHOOL Security Utilities
/// أدوات الأمان المساعدة
///
/// Utility functions for security operations:
/// - PIN hashing and validation
/// - Token validation
/// - Password strength checking
/// - Secure random generation

class SecurityUtils {
  SecurityUtils._();

  // ═══════════════════════════════════════════════════════════════════════════
  // PIN/Password Hashing
  // ═══════════════════════════════════════════════════════════════════════════

  /// Hash a PIN code using SHA-256
  /// تشفير رمز PIN باستخدام SHA-256
  static String hashPin(String pin, {String? salt}) {
    final saltToUse = salt ?? generateSalt();
    final bytes = utf8.encode(pin + saltToUse);
    final digest = sha256.convert(bytes);
    return '$saltToUse:${digest.toString()}';
  }

  /// Verify a PIN code against a hash
  /// التحقق من رمز PIN مع التشفير
  static bool verifyPin(String pin, String hashedPin) {
    try {
      final parts = hashedPin.split(':');
      if (parts.length != 2) return false;

      final salt = parts[0];
      final hash = parts[1];

      final newHash = hashPin(pin, salt: salt);
      return newHash == hashedPin;
    } catch (e) {
      return false;
    }
  }

  /// Generate a random salt for hashing
  /// توليد ملح عشوائي للتشفير
  static String generateSalt({int length = 16}) {
    final random = Random.secure();
    final values = List<int>.generate(length, (i) => random.nextInt(256));
    return base64Url.encode(values);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Password Strength
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check password strength
  /// فحص قوة كلمة المرور
  static PasswordStrength checkPasswordStrength(String password) {
    if (password.isEmpty) return PasswordStrength.empty;

    int score = 0;

    // Length check
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (password.length >= 16) score++;

    // Character variety
    if (password.contains(RegExp(r'[a-z]'))) score++; // lowercase
    if (password.contains(RegExp(r'[A-Z]'))) score++; // uppercase
    if (password.contains(RegExp(r'[0-9]'))) score++; // numbers
    if (password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'))) score++; // special

    // Determine strength
    if (score <= 2) return PasswordStrength.weak;
    if (score <= 4) return PasswordStrength.medium;
    if (score <= 6) return PasswordStrength.strong;
    return PasswordStrength.veryStrong;
  }

  /// Get password strength message in Arabic
  /// الحصول على رسالة قوة كلمة المرور بالعربية
  static String getPasswordStrengthMessage(PasswordStrength strength) {
    switch (strength) {
      case PasswordStrength.empty:
        return 'الرجاء إدخال كلمة مرور';
      case PasswordStrength.weak:
        return 'كلمة مرور ضعيفة - استخدم أحرف وأرقام ورموز';
      case PasswordStrength.medium:
        return 'كلمة مرور متوسطة - يمكن تحسينها';
      case PasswordStrength.strong:
        return 'كلمة مرور قوية';
      case PasswordStrength.veryStrong:
        return 'كلمة مرور قوية جداً';
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // PIN Validation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Validate PIN format (4-8 digits)
  /// التحقق من صيغة رمز PIN
  static bool isValidPin(String pin, {int minLength = 4, int maxLength = 8}) {
    if (pin.length < minLength || pin.length > maxLength) return false;
    return RegExp(r'^\d+$').hasMatch(pin);
  }

  /// Check if PIN contains sequential numbers
  /// فحص إذا كان رمز PIN يحتوي على أرقام متسلسلة
  static bool hasSequentialNumbers(String pin) {
    for (int i = 0; i < pin.length - 2; i++) {
      final a = int.tryParse(pin[i]) ?? -1;
      final b = int.tryParse(pin[i + 1]) ?? -1;
      final c = int.tryParse(pin[i + 2]) ?? -1;

      if (a + 1 == b && b + 1 == c) return true; // 123, 234, etc.
      if (a - 1 == b && b - 1 == c) return true; // 321, 210, etc.
    }
    return false;
  }

  /// Check if PIN contains repeated numbers
  /// فحص إذا كان رمز PIN يحتوي على أرقام متكررة
  static bool hasRepeatedNumbers(String pin) {
    if (pin.length < 3) return false;

    for (int i = 0; i < pin.length - 2; i++) {
      if (pin[i] == pin[i + 1] && pin[i + 1] == pin[i + 2]) {
        return true; // 111, 222, etc.
      }
    }
    return false;
  }

  /// Check if PIN is weak (common patterns)
  /// فحص إذا كان رمز PIN ضعيف
  static bool isWeakPin(String pin) {
    // Common weak PINs
    const weakPins = [
      '0000', '1111', '2222', '3333', '4444',
      '5555', '6666', '7777', '8888', '9999',
      '1234', '4321', '1212', '0123',
    ];

    if (weakPins.contains(pin)) return true;
    if (hasSequentialNumbers(pin)) return true;
    if (hasRepeatedNumbers(pin)) return true;

    return false;
  }

  /// Get PIN strength message in Arabic
  /// الحصول على رسالة قوة رمز PIN بالعربية
  static String getPinStrengthMessage(String pin) {
    if (!isValidPin(pin)) {
      return 'رمز PIN غير صالح';
    }

    if (isWeakPin(pin)) {
      return 'رمز PIN ضعيف - استخدم أرقام غير متسلسلة أو متكررة';
    }

    if (pin.length >= 6) {
      return 'رمز PIN قوي';
    }

    return 'رمز PIN مقبول';
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Token Validation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Validate JWT token format (basic check)
  /// التحقق من صيغة رمز JWT
  static bool isValidJwtFormat(String token) {
    final parts = token.split('.');
    if (parts.length != 3) return false;

    // Check if each part is valid base64
    try {
      for (final part in parts) {
        base64Url.decode(part);
      }
      return true;
    } catch (e) {
      return false;
    }
  }

  /// Extract JWT payload without verification
  /// استخراج محتوى JWT بدون التحقق
  static Map<String, dynamic>? extractJwtPayload(String token) {
    try {
      final parts = token.split('.');
      if (parts.length != 3) return null;

      final payload = parts[1];
      final normalized = base64Url.normalize(payload);
      final decoded = utf8.decode(base64Url.decode(normalized));
      return json.decode(decoded) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }

  /// Check if JWT token is expired
  /// فحص إذا كان رمز JWT منتهي الصلاحية
  static bool isJwtExpired(String token) {
    final payload = extractJwtPayload(token);
    if (payload == null) return true;

    final exp = payload['exp'] as int?;
    if (exp == null) return true;

    final expiry = DateTime.fromMillisecondsSinceEpoch(exp * 1000);
    return DateTime.now().isAfter(expiry);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Secure Random Generation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate a secure random string
  /// توليد نص عشوائي آمن
  static String generateSecureRandomString({int length = 32}) {
    final random = Random.secure();
    final values = List<int>.generate(length, (i) => random.nextInt(256));
    return base64Url.encode(values).substring(0, length);
  }

  /// Generate a secure random PIN
  /// توليد رمز PIN عشوائي آمن
  static String generateSecurePin({int length = 6}) {
    final random = Random.secure();
    final pin = List<int>.generate(length, (i) => random.nextInt(10)).join();

    // Ensure it's not a weak PIN
    if (isWeakPin(pin)) {
      return generateSecurePin(length: length); // Regenerate
    }

    return pin;
  }

  /// Generate a device fingerprint
  /// توليد بصمة الجهاز
  static String generateDeviceFingerprint(Map<String, dynamic> deviceInfo) {
    final infoString = json.encode(deviceInfo);
    final bytes = utf8.encode(infoString);
    final digest = sha256.convert(bytes);
    return digest.toString();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Time-based Security
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if enough time has passed since last attempt
  /// فحص إذا مر وقت كافي منذ آخر محاولة
  static bool hasEnoughTimePassed(
    DateTime? lastAttempt,
    Duration requiredDelay,
  ) {
    if (lastAttempt == null) return true;

    final timeSinceLast = DateTime.now().difference(lastAttempt);
    return timeSinceLast >= requiredDelay;
  }

  /// Calculate remaining lockout time
  /// حساب الوقت المتبقي للقفل
  static Duration getRemainingLockoutTime(
    DateTime lockoutStart,
    Duration lockoutDuration,
  ) {
    final unlockTime = lockoutStart.add(lockoutDuration);
    final now = DateTime.now();

    if (now.isAfter(unlockTime)) {
      return Duration.zero;
    }

    return unlockTime.difference(now);
  }

  /// Format duration in Arabic
  /// تنسيق المدة بالعربية
  static String formatDurationArabic(Duration duration) {
    if (duration.inHours > 0) {
      final hours = duration.inHours;
      return '$hours ${hours == 1 ? 'ساعة' : 'ساعات'}';
    } else if (duration.inMinutes > 0) {
      final minutes = duration.inMinutes;
      return '$minutes ${minutes == 1 ? 'دقيقة' : 'دقائق'}';
    } else {
      final seconds = duration.inSeconds;
      return '$seconds ${seconds == 1 ? 'ثانية' : 'ثواني'}';
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Enums
// ═══════════════════════════════════════════════════════════════════════════

/// Password strength levels
enum PasswordStrength {
  empty,
  weak,
  medium,
  strong,
  veryStrong,
}
