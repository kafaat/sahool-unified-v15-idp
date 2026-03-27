/// Validators - Common Validation Utilities
/// المدققات - أدوات التحقق الشائعة
///
/// Provides comprehensive validation for common field types:
/// - Required fields
/// - Email format
/// - Phone numbers (Saudi, Yemen, international)
/// - Arabic text validation
/// - Field name format
/// - Password strength
///
/// All validation messages are bilingual (Arabic/English).
library;

/// Validation result model with bilingual support
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

  /// Create error result with bilingual messages
  factory ValidationResult.error(String message, String messageAr) {
    return ValidationResult(
      isValid: false,
      errorMessage: message,
      errorMessageAr: messageAr,
    );
  }

  /// Get message based on locale (defaults to Arabic for RTL support)
  String? getMessage({bool arabic = true}) {
    if (isValid) return null;
    return arabic ? errorMessageAr : errorMessage;
  }

  @override
  String toString() =>
      isValid ? 'ValidationResult.success' : 'ValidationResult.error($errorMessage)';
}

/// Common validators for the SAHOOL platform
class Validators {
  // ─────────────────────────────────────────────────────────────────────────────
  // Required Field Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate that a field is not empty
  static ValidationResult required(
    String? value, {
    String fieldName = 'Field',
    String fieldNameAr = 'الحقل',
  }) {
    if (value == null || value.trim().isEmpty) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوب',
      );
    }
    return ValidationResult.success;
  }

  /// Validate that a value is not null
  static ValidationResult requiredValue<T>(
    T? value, {
    String fieldName = 'Value',
    String fieldNameAr = 'القيمة',
  }) {
    if (value == null) {
      return ValidationResult.error(
        '$fieldName is required',
        '$fieldNameAr مطلوبة',
      );
    }
    return ValidationResult.success;
  }

  /// Validate that a list is not empty
  static ValidationResult requiredList<T>(
    List<T>? value, {
    String fieldName = 'List',
    String fieldNameAr = 'القائمة',
    int minItems = 1,
  }) {
    if (value == null || value.length < minItems) {
      return ValidationResult.error(
        '$fieldName must have at least $minItems item(s)',
        '$fieldNameAr يجب أن تحتوي على $minItems عنصر على الأقل',
      );
    }
    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Email Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// RFC 5322 compliant email regex pattern
  static final RegExp _emailRegex = RegExp(
    r"^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",
  );

  /// Validate email address format
  static ValidationResult email(String? value, {bool isRequired = true}) {
    // Check required
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Email is required',
          'البريد الإلكتروني مطلوب',
        );
      }
      return ValidationResult.success;
    }

    final email = value.trim().toLowerCase();

    // Check basic format
    if (!_emailRegex.hasMatch(email)) {
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

    // Check for valid TLD (at least 2 characters)
    final parts = email.split('@');
    if (parts.length == 2) {
      final domain = parts[1];
      final tldIndex = domain.lastIndexOf('.');
      if (tldIndex == -1 || domain.length - tldIndex - 1 < 2) {
        return ValidationResult.error(
          'Invalid email domain',
          'نطاق البريد الإلكتروني غير صالح',
        );
      }
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Phone Number Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate Saudi phone number format
  /// Saudi format: 05XXXXXXXX (10 digits starting with 05)
  /// Also accepts with country code: +966 5XXXXXXXX
  static ValidationResult saudiPhone(String? value, {bool isRequired = true}) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Phone number is required',
          'رقم الهاتف مطلوب',
        );
      }
      return ValidationResult.success;
    }

    // Remove spaces, dashes, parentheses
    String cleaned = value.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    // Handle country code variations
    if (cleaned.startsWith('+966')) {
      cleaned = '0${cleaned.substring(4)}';
    } else if (cleaned.startsWith('966')) {
      cleaned = '0${cleaned.substring(3)}';
    } else if (cleaned.startsWith('00966')) {
      cleaned = '0${cleaned.substring(5)}';
    }

    // Check if numeric only
    if (!RegExp(r'^\d+$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Phone number must contain only numbers',
        'رقم الهاتف يجب أن يحتوي على أرقام فقط',
      );
    }

    // Saudi format: 05XXXXXXXX (must start with 05)
    if (!RegExp(r'^05\d{8}$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Invalid Saudi phone format. Must start with 05 and be 10 digits',
        'صيغة رقم الهاتف السعودي غير صالحة. يجب أن يبدأ بـ 05 ويكون 10 أرقام',
      );
    }

    return ValidationResult.success;
  }

  /// Validate Yemen phone number format
  /// Yemen format: 7XXXXXXXX (9 digits starting with 7)
  /// Also accepts with country code: +967 7XXXXXXXX
  static ValidationResult yemenPhone(String? value, {bool isRequired = true}) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Phone number is required',
          'رقم الهاتف مطلوب',
        );
      }
      return ValidationResult.success;
    }

    // Remove spaces, dashes, parentheses
    String cleaned = value.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    // Handle country code variations
    if (cleaned.startsWith('+967')) {
      cleaned = cleaned.substring(4);
    } else if (cleaned.startsWith('967')) {
      cleaned = cleaned.substring(3);
    } else if (cleaned.startsWith('00967')) {
      cleaned = cleaned.substring(5);
    }

    // Check if numeric only
    if (!RegExp(r'^\d+$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Phone number must contain only numbers',
        'رقم الهاتف يجب أن يحتوي على أرقام فقط',
      );
    }

    // Yemen format: 7XXXXXXXX (9 digits starting with 7)
    if (!RegExp(r'^7\d{8}$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Invalid Yemen phone format. Must start with 7 and be 9 digits',
        'صيغة رقم الهاتف اليمني غير صالحة. يجب أن يبدأ بـ 7 ويكون 9 أرقام',
      );
    }

    return ValidationResult.success;
  }

  /// Validate phone number for a specific country
  static ValidationResult phone(
    String? value, {
    String countryCode = '+966',
    bool isRequired = true,
  }) {
    switch (countryCode) {
      case '+966':
        return saudiPhone(value, isRequired: isRequired);
      case '+967':
        return yemenPhone(value, isRequired: isRequired);
      default:
        return internationalPhone(value, isRequired: isRequired);
    }
  }

  /// Validate international phone number (generic format)
  static ValidationResult internationalPhone(
    String? value, {
    bool isRequired = true,
    int minDigits = 7,
    int maxDigits = 15,
  }) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Phone number is required',
          'رقم الهاتف مطلوب',
        );
      }
      return ValidationResult.success;
    }

    // Remove spaces, dashes, parentheses, but keep +
    final cleaned = value.replaceAll(RegExp(r'[\s\-\(\)]'), '');

    // Check format: optional + followed by digits
    if (!RegExp(r'^\+?\d+$').hasMatch(cleaned)) {
      return ValidationResult.error(
        'Phone number contains invalid characters',
        'رقم الهاتف يحتوي على أحرف غير صالحة',
      );
    }

    // Count digits only (without +)
    final digitsOnly = cleaned.replaceAll('+', '');
    if (digitsOnly.length < minDigits || digitsOnly.length > maxDigits) {
      return ValidationResult.error(
        'Phone number must be between $minDigits and $maxDigits digits',
        'رقم الهاتف يجب أن يكون بين $minDigits و $maxDigits رقم',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Text Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Arabic character range pattern (includes extended Arabic)
  static final RegExp _arabicRegex = RegExp(
    r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]',
  );

  /// Validate that text contains Arabic characters
  static ValidationResult arabicText(
    String? value, {
    bool isRequired = true,
    bool allowEnglish = true,
    bool allowNumbers = true,
    int minLength = 1,
    int maxLength = 1000,
  }) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Text is required',
          'النص مطلوب',
        );
      }
      return ValidationResult.success;
    }

    final text = value.trim();

    // Check length
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
    final hasArabic = _arabicRegex.hasMatch(text);

    if (!hasArabic && !allowEnglish) {
      return ValidationResult.error(
        'Text must contain Arabic characters',
        'النص يجب أن يحتوي على أحرف عربية',
      );
    }

    // Check for dangerous content (XSS prevention)
    if (_containsDangerousContent(text)) {
      return ValidationResult.error(
        'Text contains invalid characters',
        'النص يحتوي على أحرف غير صالحة',
      );
    }

    return ValidationResult.success;
  }

  /// Validate general text input
  static ValidationResult text(
    String? value, {
    bool isRequired = true,
    int minLength = 1,
    int maxLength = 1000,
    bool allowSpecialChars = true,
    String fieldName = 'Text',
    String fieldNameAr = 'النص',
  }) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          '$fieldName is required',
          '$fieldNameAr مطلوب',
        );
      }
      return ValidationResult.success;
    }

    final text = value.trim();

    // Check length
    if (text.length < minLength) {
      return ValidationResult.error(
        '$fieldName must be at least $minLength characters',
        '$fieldNameAr يجب أن يكون $minLength أحرف على الأقل',
      );
    }

    if (text.length > maxLength) {
      return ValidationResult.error(
        '$fieldName must not exceed $maxLength characters',
        '$fieldNameAr يجب ألا يتجاوز $maxLength حرف',
      );
    }

    // Check for special characters if not allowed
    if (!allowSpecialChars) {
      if (!RegExp(r'^[\p{L}\p{N}\s.,!?،؛:-]+$', unicode: true).hasMatch(text)) {
        return ValidationResult.error(
          '$fieldName contains invalid characters',
          '$fieldNameAr يحتوي على أحرف غير صالحة',
        );
      }
    }

    // Check for dangerous content
    if (_containsDangerousContent(text)) {
      return ValidationResult.error(
        '$fieldName contains invalid content',
        '$fieldNameAr يحتوي على محتوى غير صالح',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Field Name Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate field name format
  /// Allows Arabic, English letters, numbers, spaces, and hyphens
  static ValidationResult fieldName(
    String? value, {
    bool isRequired = true,
    int minLength = 2,
    int maxLength = 100,
  }) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Field name is required',
          'اسم الحقل مطلوب',
        );
      }
      return ValidationResult.success;
    }

    final name = value.trim();

    // Check length
    if (name.length < minLength) {
      return ValidationResult.error(
        'Field name must be at least $minLength characters',
        'اسم الحقل يجب أن يكون $minLength أحرف على الأقل',
      );
    }

    if (name.length > maxLength) {
      return ValidationResult.error(
        'Field name must not exceed $maxLength characters',
        'اسم الحقل يجب ألا يتجاوز $maxLength حرف',
      );
    }

    // Allow Arabic, English, numbers, spaces, hyphens, underscores
    if (!RegExp(r'^[\p{L}\p{N}\s\-_]+$', unicode: true).hasMatch(name)) {
      return ValidationResult.error(
        'Field name contains invalid characters',
        'اسم الحقل يحتوي على أحرف غير صالحة',
      );
    }

    // Check for dangerous content
    if (_containsDangerousContent(name)) {
      return ValidationResult.error(
        'Field name contains invalid content',
        'اسم الحقل يحتوي على محتوى غير صالح',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Password Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate password strength
  static ValidationResult password(
    String? value, {
    bool isRequired = true,
    int minLength = 8,
    int maxLength = 128,
    bool requireUppercase = true,
    bool requireLowercase = true,
    bool requireNumber = true,
    bool requireSpecialChar = false,
  }) {
    if (value == null || value.isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Password is required',
          'كلمة المرور مطلوبة',
        );
      }
      return ValidationResult.success;
    }

    // Check length
    if (value.length < minLength) {
      return ValidationResult.error(
        'Password must be at least $minLength characters',
        'كلمة المرور يجب أن تكون $minLength أحرف على الأقل',
      );
    }

    if (value.length > maxLength) {
      return ValidationResult.error(
        'Password is too long',
        'كلمة المرور طويلة جداً',
      );
    }

    // Check uppercase
    if (requireUppercase && !RegExp(r'[A-Z]').hasMatch(value)) {
      return ValidationResult.error(
        'Password must contain at least one uppercase letter',
        'كلمة المرور يجب أن تحتوي على حرف كبير على الأقل',
      );
    }

    // Check lowercase
    if (requireLowercase && !RegExp(r'[a-z]').hasMatch(value)) {
      return ValidationResult.error(
        'Password must contain at least one lowercase letter',
        'كلمة المرور يجب أن تحتوي على حرف صغير على الأقل',
      );
    }

    // Check number
    if (requireNumber && !RegExp(r'[0-9]').hasMatch(value)) {
      return ValidationResult.error(
        'Password must contain at least one number',
        'كلمة المرور يجب أن تحتوي على رقم على الأقل',
      );
    }

    // Check special character
    if (requireSpecialChar && !RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(value)) {
      return ValidationResult.error(
        'Password must contain at least one special character',
        'كلمة المرور يجب أن تحتوي على رمز خاص على الأقل',
      );
    }

    return ValidationResult.success;
  }

  /// Validate password confirmation matches
  static ValidationResult passwordMatch(
    String? password,
    String? confirmPassword, {
    bool isRequired = true,
  }) {
    if (password == null || password.isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Password is required',
          'كلمة المرور مطلوبة',
        );
      }
      return ValidationResult.success;
    }

    if (confirmPassword == null || confirmPassword.isEmpty) {
      return ValidationResult.error(
        'Please confirm your password',
        'الرجاء تأكيد كلمة المرور',
      );
    }

    if (password != confirmPassword) {
      return ValidationResult.error(
        'Passwords do not match',
        'كلمات المرور غير متطابقة',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Username Validation
  // ─────────────────────────────────────────────────────────────────────────────

  /// Validate username format
  static ValidationResult username(
    String? value, {
    bool isRequired = true,
    int minLength = 3,
    int maxLength = 30,
    bool allowArabic = true,
  }) {
    if (value == null || value.trim().isEmpty) {
      if (isRequired) {
        return ValidationResult.error(
          'Username is required',
          'اسم المستخدم مطلوب',
        );
      }
      return ValidationResult.success;
    }

    final username = value.trim();

    // Check length
    if (username.length < minLength) {
      return ValidationResult.error(
        'Username must be at least $minLength characters',
        'اسم المستخدم يجب أن يكون $minLength أحرف على الأقل',
      );
    }

    if (username.length > maxLength) {
      return ValidationResult.error(
        'Username must not exceed $maxLength characters',
        'اسم المستخدم يجب ألا يتجاوز $maxLength حرف',
      );
    }

    // Check format
    final pattern = allowArabic
        ? r'^[\p{L}\p{N}_]+$'
        : r'^[a-zA-Z0-9_]+$';

    if (!RegExp(pattern, unicode: true).hasMatch(username)) {
      return ValidationResult.error(
        'Username can only contain letters, numbers, and underscores',
        'اسم المستخدم يمكن أن يحتوي على أحرف وأرقام وشرطات سفلية فقط',
      );
    }

    // Cannot start with a number
    if (RegExp(r'^[0-9]').hasMatch(username)) {
      return ValidationResult.error(
        'Username cannot start with a number',
        'اسم المستخدم لا يمكن أن يبدأ برقم',
      );
    }

    return ValidationResult.success;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Security Helpers
  // ─────────────────────────────────────────────────────────────────────────────

  /// Check for dangerous HTML/script content
  static bool _containsDangerousContent(String text) {
    final lowerText = text.toLowerCase();

    final dangerousPatterns = [
      r'<script[^>]*>',
      r'</script>',
      r'javascript:',
      r'on\w+\s*=',
      r'<iframe',
      r'<object',
      r'<embed',
      r'<form',
      r'<input',
      r'eval\s*\(',
      r'document\.',
      r'window\.',
    ];

    for (final pattern in dangerousPatterns) {
      if (RegExp(pattern, caseSensitive: false).hasMatch(lowerText)) {
        return true;
      }
    }

    return false;
  }
}

/// Field-specific validators for SAHOOL agricultural platform
class FieldValidators {
  /// Validate field area in hectares
  ValidationResult validateArea(double? value) {
    if (value == null) {
      return ValidationResult.error(
        'Area is required',
        'المساحة مطلوبة',
      );
    }

    if (value <= 0) {
      return ValidationResult.error(
        'Area must be greater than 0',
        'المساحة يجب أن تكون أكبر من صفر',
      );
    }

    if (value > 10000) {
      return ValidationResult.error(
        'Area exceeds maximum allowed (10,000 hectares)',
        'المساحة تتجاوز الحد الأقصى المسموح (10,000 هكتار)',
      );
    }

    return ValidationResult.success;
  }

  /// Validate NDVI value (0.0 to 1.0)
  ValidationResult validateNdvi(double? value) {
    if (value == null) {
      return ValidationResult.success; // NDVI is optional
    }

    if (value < 0 || value > 1) {
      return ValidationResult.error(
        'NDVI must be between 0 and 1',
        'مؤشر NDVI يجب أن يكون بين 0 و 1',
      );
    }

    return ValidationResult.success;
  }

  /// Validate field name
  ValidationResult validateName(String? value) {
    return Validators.fieldName(value);
  }

  /// Validate crop type selection
  ValidationResult validateCropType(String? value) {
    if (value == null || value.trim().isEmpty) {
      return ValidationResult.error(
        'Please select a crop type',
        'الرجاء اختيار نوع المحصول',
      );
    }
    return ValidationResult.success;
  }
}
