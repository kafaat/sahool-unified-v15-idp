/// Input Validator
/// مدقق المدخلات - التحقق من صحة البيانات المدخلة
///
/// Provides comprehensive validation for user inputs including:
/// - OTP codes (format, length, numeric only)
/// - Phone numbers (Saudi, Yemen formats)
/// - Email addresses
/// - Arabic text validation
/// - SQL injection prevention for search queries

import 'package:flutter/services.dart';

/// Validation result model
class ValidationResult {
  final bool isValid;
  final String? errorMessage;
  final String? errorMessageAr;

  const ValidationResult({
    required this.isValid,
    this.errorMessage,
    this.errorMessageAr,
  });

  /// Successful validation result
  static const ValidationResult success = ValidationResult(isValid: true);

  /// Create error result
  static ValidationResult error(String message, String messageAr) {
    return ValidationResult(
      isValid: false,
      errorMessage: message,
      errorMessageAr: messageAr,
    );
  }
}

/// Input Validator Class
class InputValidator {
  // ─────────────────────────────────────────────────────────────────────────────
  // OTP Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate OTP code
  /// - Must be exactly 4 or 6 digits
  /// - Must contain only numeric characters
  /// - Must not contain spaces or special characters
  static ValidationResult validateOtp(String otp, {int length = 4}) {
    // Check if empty
    if (otp.isEmpty) {
      return ValidationResult.error(
        'OTP is required',
        'رمز التحقق مطلوب',
      );
    }

    // Check length
    if (otp.length != length) {
      return ValidationResult.error(
        'OTP must be $length digits',
        'رمز التحقق يجب أن يكون $length أرقام',
      );
    }

    // Check if numeric only
    if (!RegExp(r'^\d+$').hasMatch(otp)) {
      return ValidationResult.error(
        'OTP must contain only numbers',
        'رمز التحقق يجب أن يحتوي على أرقام فقط',
      );
    }

    // Check for sequential numbers (weak OTP)
    if (_isSequentialNumbers(otp)) {
      return ValidationResult.error(
        'Invalid OTP format',
        'رمز التحقق غير صالح',
      );
    }

    return ValidationResult.success;
  }

  /// Check if numbers are sequential (e.g., 1234, 4321)
  static bool _isSequentialNumbers(String numbers) {
    if (numbers.length < 3) return false;

    final digits = numbers.split('').map(int.parse).toList();

    // Check ascending sequence
    bool isAscending = true;
    for (int i = 0; i < digits.length - 1; i++) {
      if (digits[i + 1] != digits[i] + 1) {
        isAscending = false;
        break;
      }
    }
    if (isAscending) return true;

    // Check descending sequence
    bool isDescending = true;
    for (int i = 0; i < digits.length - 1; i++) {
      if (digits[i + 1] != digits[i] - 1) {
        isDescending = false;
        break;
      }
    }
    if (isDescending) return true;

    // Check all same digits
    if (digits.toSet().length == 1) return true;

    return false;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Phone Number Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate phone number (Saudi format)
  /// Saudi: 05XXXXXXXX (10 digits starting with 05)
  static ValidationResult validateSaudiPhone(String phone) {
    // Remove spaces and special characters
    final cleaned = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    if (cleaned.isEmpty) {
      return ValidationResult.error(
        'Phone number is required',
        'رقم الهاتف مطلوب',
      );
    }

    // Check if numeric only
    if (!RegExp(r'^\d+$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Phone number must contain only numbers',
        'رقم الهاتف يجب أن يحتوي على أرقام فقط',
      );
    }

    // Saudi format: 05XXXXXXXX
    if (!RegExp(r'^05\d{8}$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Invalid Saudi phone number format (must start with 05)',
        'صيغة رقم الهاتف السعودي غير صالحة (يجب أن يبدأ بـ 05)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate phone number (Yemen format)
  /// Yemen: 7XXXXXXXX (9 digits starting with 7)
  static ValidationResult validateYemenPhone(String phone) {
    // Remove spaces and special characters
    final cleaned = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    if (cleaned.isEmpty) {
      return ValidationResult.error(
        'Phone number is required',
        'رقم الهاتف مطلوب',
      );
    }

    // Check if numeric only
    if (!RegExp(r'^\d+$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Phone number must contain only numbers',
        'رقم الهاتف يجب أن يحتوي على أرقام فقط',
      );
    }

    // Yemen format: 7XXXXXXXX (9 digits)
    if (!RegExp(r'^7\d{8}$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Invalid Yemen phone number format (must start with 7)',
        'صيغة رقم الهاتف اليمني غير صالحة (يجب أن يبدأ بـ 7)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate international phone number with country code
  static ValidationResult validateInternationalPhone(
    String phone,
    String countryCode,
  ) {
    switch (countryCode) {
      case '+966':
        return validateSaudiPhone(phone);
      case '+967':
        return validateYemenPhone(phone);
      default:
        // Generic validation for other countries
        final cleaned = phone.replaceAll(RegExp(r'[\s\-\(\)]'), '');
        if (cleaned.isEmpty) {
          return ValidationResult.error(
            'Phone number is required',
            'رقم الهاتف مطلوب',
          );
        }
        if (!RegExp(r'^\d{7,15}$').hasMatch(cleaned)) {
          return ValidationResult.error(
            'Invalid phone number format',
            'صيغة رقم الهاتف غير صالحة',
          );
        }
        return ValidationResult.success;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Email Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate email address
  static ValidationResult validateEmail(String email) {
    if (email.isEmpty) {
      return ValidationResult.error(
        'Email is required',
        'البريد الإلكتروني مطلوب',
      );
    }

    // RFC 5322 compliant email regex
    final emailRegex = RegExp(
      r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
    );

    if (!emailRegex.hasMatch(email)) {
      return ValidationResult.error(
        'Invalid email format',
        'صيغة البريد الإلكتروني غير صالحة',
      );
    }

    // Additional checks
    final parts = email.split('@');
    if (parts.length != 2) {
      return ValidationResult.error(
        'Invalid email format',
        'صيغة البريد الإلكتروني غير صالحة',
      );
    }

    // Check for consecutive dots
    if (email.contains('..')) {
      return ValidationResult.error(
        'Invalid email format',
        'صيغة البريد الإلكتروني غير صالحة',
      );
    }

    // Check email length
    if (email.length > 254) {
      return ValidationResult.error(
        'Email is too long',
        'البريد الإلكتروني طويل جداً',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Text Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate Arabic text (allows Arabic characters, numbers, and common punctuation)
  static ValidationResult validateArabicText(
    String text, {
    int minLength = 1,
    int maxLength = 1000,
    bool allowEnglish = true,
  }) {
    if (text.isEmpty) {
      return ValidationResult.error(
        'Text is required',
        'النص مطلوب',
      );
    }

    if (text.length < minLength) {
      return ValidationResult.error(
        'Text must be at least $minLength characters',
        'النص يجب أن يكون $minLength أحرف على الأقل',
      );
    }

    if (text.length > maxLength) {
      return ValidationResult.error(
        'Text must not exceed $maxLength characters',
        'النص يجب ألا يتجاوز $maxLength حرف',
      );
    }

    // Check for Arabic characters
    final hasArabic = RegExp(r'[\u0600-\u06FF]').hasMatch(text);

    if (!hasArabic && !allowEnglish) {
      return ValidationResult.error(
        'Text must contain Arabic characters',
        'النص يجب أن يحتوي على أحرف عربية',
      );
    }

    // Check for dangerous HTML/script tags
    if (_containsHtmlTags(text)) {
      return ValidationResult.error(
        'Text contains invalid characters',
        'النص يحتوي على أحرف غير صالحة',
      );
    }

    return ValidationResult.success;
  }

  /// Validate general text input
  static ValidationResult validateText(
    String text, {
    int minLength = 1,
    int maxLength = 1000,
    bool allowSpecialChars = true,
  }) {
    if (text.isEmpty) {
      return ValidationResult.error(
        'Text is required',
        'النص مطلوب',
      );
    }

    if (text.length < minLength) {
      return ValidationResult.error(
        'Text must be at least $minLength characters',
        'النص يجب أن يكون $minLength أحرف على الأقل',
      );
    }

    if (text.length > maxLength) {
      return ValidationResult.error(
        'Text must not exceed $maxLength characters',
        'النص يجب ألا يتجاوز $maxLength حرف',
      );
    }

    if (!allowSpecialChars) {
      // Only allow letters, numbers, spaces, and basic punctuation
      if (!RegExp(r'^[\p{L}\p{N}\s.,!?،؛]+$', unicode: true).hasMatch(text)) {
        return ValidationResult.error(
          'Text contains invalid characters',
          'النص يحتوي على أحرف غير صالحة',
        );
      }
    }

    // Check for dangerous HTML/script tags
    if (_containsHtmlTags(text)) {
      return ValidationResult.error(
        'Text contains invalid characters',
        'النص يحتوي على أحرف غير صالحة',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Security Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Check for potential SQL injection patterns
  static bool containsSqlInjection(String text) {
    final sqlPatterns = [
      r"('|(\\'))",
      r'(--)',
      r'(;)',
      r'(\/\*)',
      r'(\*\/)',
      r'(xp_)',
      r'(union\s+select)',
      r'(drop\s+table)',
      r'(insert\s+into)',
      r'(delete\s+from)',
      r'(update\s+.*\s+set)',
      r'(exec\s*\()',
      r'(execute\s*\()',
    ];

    final lowerText = text.toLowerCase();
    for (final pattern in sqlPatterns) {
      if (RegExp(pattern, caseSensitive: false).hasMatch(lowerText)) {
        return true;
      }
    }

    return false;
  }

  /// Check for HTML/Script tags (XSS prevention)
  static bool _containsHtmlTags(String text) {
    final htmlPatterns = [
      r'<script[^>]*>.*?</script>',
      r'<iframe[^>]*>.*?</iframe>',
      r'<object[^>]*>.*?</object>',
      r'<embed[^>]*>',
      r'<img[^>]*onerror[^>]*>',
      r'javascript:',
      r'on\w+\s*=',
    ];

    final lowerText = text.toLowerCase();
    for (final pattern in htmlPatterns) {
      if (RegExp(pattern, caseSensitive: false, dotAll: true).hasMatch(lowerText)) {
        return true;
      }
    }

    return false;
  }

  /// Validate search query (prevent SQL injection)
  static ValidationResult validateSearchQuery(String query) {
    if (query.isEmpty) {
      return ValidationResult.success; // Empty search is valid
    }

    if (query.length > 200) {
      return ValidationResult.error(
        'Search query is too long',
        'استعلام البحث طويل جداً',
      );
    }

    // Check for SQL injection patterns
    if (containsSqlInjection(query)) {
      return ValidationResult.error(
        'Invalid search query',
        'استعلام البحث غير صالح',
      );
    }

    // Check for HTML/script tags
    if (_containsHtmlTags(query)) {
      return ValidationResult.error(
        'Invalid search query',
        'استعلام البحث غير صالح',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Input Formatters (for TextField)
  // ─────────────────────────────────────────────────────────────────────────────

  /// Text input formatter for OTP (digits only)
  static List<TextInputFormatter> otpFormatters({int length = 4}) {
    return [
      FilteringTextInputFormatter.digitsOnly,
      LengthLimitingTextInputFormatter(length),
      // Prevent spaces
      FilteringTextInputFormatter.deny(RegExp(r'\s')),
    ];
  }

  /// Text input formatter for phone numbers (digits only)
  static List<TextInputFormatter> phoneFormatters({int? maxLength}) {
    return [
      FilteringTextInputFormatter.digitsOnly,
      if (maxLength != null) LengthLimitingTextInputFormatter(maxLength),
      // Prevent spaces
      FilteringTextInputFormatter.deny(RegExp(r'\s')),
    ];
  }

  /// Text input formatter for Arabic text
  static List<TextInputFormatter> arabicTextFormatters({
    int? maxLength,
    bool allowEnglish = true,
  }) {
    return [
      if (maxLength != null) LengthLimitingTextInputFormatter(maxLength),
      // Allow Arabic, English (if enabled), numbers, spaces, and punctuation
      FilteringTextInputFormatter.allow(
        allowEnglish
            ? RegExp(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z0-9\s.,!?،؛]')
            : RegExp(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF0-9\s.,!?،؛]'),
      ),
    ];
  }

  /// Text input formatter for alphanumeric (no special characters)
  static List<TextInputFormatter> alphanumericFormatters({int? maxLength}) {
    return [
      if (maxLength != null) LengthLimitingTextInputFormatter(maxLength),
      FilteringTextInputFormatter.allow(RegExp(r'[a-zA-Z0-9\u0600-\u06FF]')),
    ];
  }
}
