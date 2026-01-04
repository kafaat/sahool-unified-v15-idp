import 'dart:convert';

/// SAHOOL PII Filter - Comprehensive Personally Identifiable Information Filter
/// نظام تصفية البيانات الشخصية الحساسة
///
/// Features:
/// - Phone number masking
/// - Email address masking
/// - National ID masking
/// - Credit card masking
/// - Token/Password removal
/// - Arabic name partial masking
/// - GPS coordinate precision reduction
/// - Request/Response sanitization
///
/// Usage:
/// ```dart
/// final sanitized = PiiFilter.sanitize('User phone: +966501234567');
/// // Output: 'User phone: +966****4567'
/// ```

class PiiFilter {
  // Patterns for PII detection
  static final RegExp _phonePattern = RegExp(
    r'(\+?966|0)?[5][0-9]{8}|'
    r'\+?\d{1,3}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',
  );

  static final RegExp _emailPattern = RegExp(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
  );

  static final RegExp _nationalIdPattern = RegExp(
    r'\b[12]\d{9}\b', // Saudi National ID: 10 digits starting with 1 or 2
  );

  static final RegExp _creditCardPattern = RegExp(
    r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
  );

  static final RegExp _gpsCoordinatePattern = RegExp(
    r'[-+]?([1-8]?\d(\.\d+)?|90(\.0+)?)\s*,\s*[-+]?(180(\.0+)?|((1[0-7]\d)|([1-9]?\d))(\.\d+)?)',
  );

  static final RegExp _arabicNamePattern = RegExp(
    r'[\u0600-\u06FF\s]{3,}', // Arabic characters, 3 or more
  );

  // Sensitive field names (case-insensitive)
  static final List<String> _sensitiveFieldNames = [
    'password',
    'token',
    'access_token',
    'refresh_token',
    'accessToken',
    'refreshToken',
    'authorization',
    'secret',
    'api_key',
    'apiKey',
    'private_key',
    'privateKey',
    'ssn',
    'social_security',
    'credit_card',
    'creditCard',
    'cvv',
    'pin',
    'otp',
    'verification_code',
    'verificationCode',
  ];

  // Header names to sanitize
  static final List<String> _sensitiveHeaders = [
    'authorization',
    'x-api-key',
    'x-auth-token',
    'cookie',
    'set-cookie',
  ];

  /// Main sanitization method - sanitizes any string or object
  static dynamic sanitize(dynamic input) {
    if (input == null) return null;

    if (input is String) {
      return _sanitizeString(input);
    } else if (input is Map) {
      return _sanitizeMap(input);
    } else if (input is List) {
      return _sanitizeList(input);
    }

    return input;
  }

  /// Sanitize string content
  static String _sanitizeString(String input) {
    if (input.isEmpty) return input;

    String sanitized = input;

    // 1. Remove tokens and passwords (complete removal)
    sanitized = _removeTokensAndPasswords(sanitized);

    // 2. Mask phone numbers
    sanitized = _maskPhoneNumbers(sanitized);

    // 3. Mask email addresses
    sanitized = _maskEmails(sanitized);

    // 4. Mask national IDs
    sanitized = _maskNationalIds(sanitized);

    // 5. Mask credit cards
    sanitized = _maskCreditCards(sanitized);

    // 6. Round GPS coordinates
    sanitized = _roundGpsCoordinates(sanitized);

    // 7. Mask Arabic names (partial masking)
    sanitized = _maskArabicNames(sanitized);

    return sanitized;
  }

  /// Sanitize map/object
  static Map<String, dynamic> _sanitizeMap(Map<dynamic, dynamic> input) {
    final Map<String, dynamic> sanitized = {};

    input.forEach((key, value) {
      final String keyStr = key.toString().toLowerCase();

      // Check if field is sensitive
      if (_isSensitiveField(keyStr)) {
        sanitized[key.toString()] = '[REDACTED]';
      } else if (value is String) {
        sanitized[key.toString()] = _sanitizeString(value);
      } else if (value is Map) {
        sanitized[key.toString()] = _sanitizeMap(value);
      } else if (value is List) {
        sanitized[key.toString()] = _sanitizeList(value);
      } else {
        sanitized[key.toString()] = value;
      }
    });

    return sanitized;
  }

  /// Sanitize list
  static List<dynamic> _sanitizeList(List<dynamic> input) {
    return input.map((item) {
      if (item is String) {
        return _sanitizeString(item);
      } else if (item is Map) {
        return _sanitizeMap(item);
      } else if (item is List) {
        return _sanitizeList(item);
      }
      return item;
    }).toList();
  }

  /// Check if field name is sensitive
  static bool _isSensitiveField(String fieldName) {
    return _sensitiveFieldNames.any(
      (sensitive) => fieldName.contains(sensitive.toLowerCase()),
    );
  }

  /// Remove tokens and passwords completely
  static String _removeTokensAndPasswords(String input) {
    // Remove JWT tokens (eyJ...)
    String result = input.replaceAll(
      RegExp(r'eyJ[A-Za-z0-9-_]+\.eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+'),
      '[TOKEN_REDACTED]',
    );

    // Remove Bearer tokens
    result = result.replaceAll(
      RegExp(r'Bearer\s+[A-Za-z0-9-_.]+', caseSensitive: false),
      'Bearer [REDACTED]',
    );

    // Remove API keys (common formats)
    result = result.replaceAll(
      RegExp(r'[A-Za-z0-9]{32,}'),
      (match) {
        // Only redact if it looks like a key (all alphanumeric, long)
        final str = match.group(0)!;
        if (str.length >= 32 && RegExp(r'^[A-Za-z0-9]+$').hasMatch(str)) {
          return '[KEY_REDACTED]';
        }
        return str;
      },
    );

    return result;
  }

  /// Mask phone numbers - show last 4 digits
  static String _maskPhoneNumbers(String input) {
    return input.replaceAllMapped(_phonePattern, (match) {
      final phone = match.group(0)!;
      if (phone.length < 4) return phone;

      final last4 = phone.substring(phone.length - 4);
      final prefix = phone.startsWith('+966')
          ? '+966'
          : phone.startsWith('966')
              ? '966'
              : phone.startsWith('0')
                  ? '0'
                  : '';

      return '$prefix****$last4';
    });
  }

  /// Mask email addresses - show first 2 chars + domain
  static String _maskEmails(String input) {
    return input.replaceAllMapped(_emailPattern, (match) {
      final email = match.group(0)!;
      final parts = email.split('@');

      if (parts.length != 2) return email;

      final username = parts[0];
      final domain = parts[1];

      if (username.length <= 2) {
        return '${username[0]}*@$domain';
      }

      return '${username.substring(0, 2)}****@$domain';
    });
  }

  /// Mask national IDs - show first 2 and last 2 digits
  static String _maskNationalIds(String input) {
    return input.replaceAllMapped(_nationalIdPattern, (match) {
      final id = match.group(0)!;
      if (id.length != 10) return id;

      return '${id.substring(0, 2)}******${id.substring(8)}';
    });
  }

  /// Mask credit cards - show last 4 digits
  static String _maskCreditCards(String input) {
    return input.replaceAllMapped(_creditCardPattern, (match) {
      final card = match.group(0)!.replaceAll(RegExp(r'[-\s]'), '');
      if (card.length < 13 || card.length > 19) return match.group(0)!;

      final last4 = card.substring(card.length - 4);
      return '****-****-****-$last4';
    });
  }

  /// Round GPS coordinates to reduce precision
  static String _roundGpsCoordinates(String input) {
    return input.replaceAllMapped(_gpsCoordinatePattern, (match) {
      final coords = match.group(0)!;
      final parts = coords.split(',');

      if (parts.length != 2) return coords;

      try {
        final lat = double.parse(parts[0].trim());
        final lng = double.parse(parts[1].trim());

        // Round to 3 decimal places (~111m precision)
        // This is enough for general location but not exact position
        final roundedLat = lat.toStringAsFixed(3);
        final roundedLng = lng.toStringAsFixed(3);

        return '$roundedLat, $roundedLng';
      } catch (e) {
        return coords;
      }
    });
  }

  /// Mask Arabic names - show first and last char only
  static String _maskArabicNames(String input) {
    return input.replaceAllMapped(_arabicNamePattern, (match) {
      final name = match.group(0)!.trim();

      // Skip if it's too short or looks like a common word
      if (name.length < 6) return name;

      // Get words
      final words = name.split(RegExp(r'\s+'));

      // Mask each word that looks like a name (3+ chars)
      final maskedWords = words.map((word) {
        if (word.length < 3) return word;

        final first = word[0];
        final last = word[word.length - 1];
        final stars = '*' * (word.length - 2);

        return '$first$stars$last';
      }).toList();

      return maskedWords.join(' ');
    });
  }

  /// Sanitize HTTP headers
  static Map<String, dynamic> sanitizeHeaders(Map<String, dynamic> headers) {
    final sanitized = <String, dynamic>{};

    headers.forEach((key, value) {
      final keyLower = key.toLowerCase();

      if (_sensitiveHeaders.any((h) => keyLower.contains(h))) {
        sanitized[key] = '[REDACTED]';
      } else {
        sanitized[key] = value;
      }
    });

    return sanitized;
  }

  /// Sanitize HTTP request body
  static dynamic sanitizeRequestBody(dynamic body) {
    if (body == null) return null;

    if (body is String) {
      try {
        // Try to parse as JSON
        final jsonBody = jsonDecode(body);
        return jsonEncode(_sanitizeMap(jsonBody));
      } catch (e) {
        // Not JSON, sanitize as string
        return _sanitizeString(body);
      }
    } else if (body is Map) {
      return _sanitizeMap(body);
    }

    return body;
  }

  /// Sanitize HTTP response body
  static dynamic sanitizeResponseBody(dynamic body) {
    return sanitizeRequestBody(body); // Same logic
  }

  /// Sanitize error messages
  static String sanitizeError(Object error) {
    return _sanitizeString(error.toString());
  }

  /// Check if a string contains PII
  static bool containsPii(String input) {
    if (input.isEmpty) return false;

    return _phonePattern.hasMatch(input) ||
        _emailPattern.hasMatch(input) ||
        _nationalIdPattern.hasMatch(input) ||
        _creditCardPattern.hasMatch(input) ||
        input.contains(RegExp(r'Bearer\s+[A-Za-z0-9-_.]+', caseSensitive: false)) ||
        input.contains(RegExp(r'eyJ[A-Za-z0-9-_]+'));
  }

  /// Get PII summary for debugging
  static Map<String, int> getPiiSummary(String input) {
    return {
      'phones': _phonePattern.allMatches(input).length,
      'emails': _emailPattern.allMatches(input).length,
      'nationalIds': _nationalIdPattern.allMatches(input).length,
      'creditCards': _creditCardPattern.allMatches(input).length,
      'tokens': RegExp(r'eyJ[A-Za-z0-9-_]+').allMatches(input).length,
      'arabicNames': _arabicNamePattern.allMatches(input).length,
    };
  }
}

/// Extension methods for easier PII filtering
extension StringPiiExtension on String {
  /// Sanitize this string
  String sanitizePii() => PiiFilter.sanitize(this);

  /// Check if contains PII
  bool containsPii() => PiiFilter.containsPii(this);
}

extension MapPiiExtension on Map<String, dynamic> {
  /// Sanitize this map
  Map<String, dynamic> sanitizePii() => PiiFilter.sanitize(this);
}
