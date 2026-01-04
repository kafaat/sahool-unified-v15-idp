/// Input Sanitizer
/// معقم المدخلات - تنظيف وتطهير البيانات المدخلة
///
/// Provides comprehensive sanitization for user inputs including:
/// - HTML entity encoding
/// - Script tag removal
/// - Special character escaping
/// - Log-safe string conversion
/// - Sensitive data filtering

/// Input Sanitizer Class
class InputSanitizer {
  // ─────────────────────────────────────────────────────────────────────────────
  // HTML Sanitization
  // ─────────────────────────────────────────────────────────────────────────────

  /// HTML entity map for encoding
  static const Map<String, String> _htmlEntities = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#x27;',
    '/': '&#x2F;',
  };

  /// Encode HTML entities to prevent XSS attacks
  static String encodeHtml(String text) {
    String result = text;
    _htmlEntities.forEach((key, value) {
      result = result.replaceAll(key, value);
    });
    return result;
  }

  /// Decode HTML entities back to original characters
  static String decodeHtml(String text) {
    String result = text;
    _htmlEntities.forEach((key, value) {
      result = result.replaceAll(value, key);
    });
    return result;
  }

  /// Remove all HTML tags from text
  static String stripHtmlTags(String text) {
    // Remove all HTML tags
    return text.replaceAll(RegExp(r'<[^>]*>'), '');
  }

  /// Remove script tags and their content
  static String removeScriptTags(String text) {
    // Remove script tags and content
    String result = text.replaceAll(
      RegExp(r'<script[^>]*>.*?</script>', caseSensitive: false, dotAll: true),
      '',
    );

    // Remove inline event handlers (onclick, onerror, etc.)
    result = result.replaceAll(
      RegExp(r'''\son\w+\s*=\s*["']?[^"']*["']?''', caseSensitive: false),
      '',
    );

    // Remove javascript: protocol
    result = result.replaceAll(
      RegExp(r'javascript:', caseSensitive: false),
      '',
    );

    return result;
  }

  /// Comprehensive HTML sanitization
  static String sanitizeHtml(String text) {
    String result = text;

    // Remove script tags first
    result = removeScriptTags(result);

    // Remove other dangerous tags
    final dangerousTags = [
      'iframe',
      'object',
      'embed',
      'link',
      'style',
      'form',
      'input',
      'button',
    ];

    for (final tag in dangerousTags) {
      result = result.replaceAll(
        RegExp('<$tag[^>]*>.*?</$tag>', caseSensitive: false, dotAll: true),
        '',
      );
      result = result.replaceAll(
        RegExp('<$tag[^>]*/?>', caseSensitive: false),
        '',
      );
    }

    // Encode remaining HTML entities
    result = encodeHtml(result);

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // SQL Injection Prevention
  // ─────────────────────────────────────────────────────────────────────────────

  /// Escape SQL special characters
  static String escapeSql(String text) {
    // Escape single quotes (most common SQL injection vector)
    String result = text.replaceAll("'", "''");

    // Escape backslashes
    result = result.replaceAll(r'\', r'\\');

    // Remove SQL comments
    result = result.replaceAll('--', '');
    result = result.replaceAll('/*', '');
    result = result.replaceAll('*/', '');

    // Remove semicolons (statement terminators)
    result = result.replaceAll(';', '');

    return result;
  }

  /// Sanitize search query for safe database operations
  static String sanitizeSearchQuery(String query) {
    String result = query.trim();

    // Remove SQL injection patterns
    final sqlPatterns = {
      r'union\s+select': '',
      r'drop\s+table': '',
      r'insert\s+into': '',
      r'delete\s+from': '',
      r'update\s+.*\s+set': '',
      r'exec\s*\(': '',
      r'execute\s*\(': '',
      r'xp_': '',
    };

    sqlPatterns.forEach((pattern, replacement) {
      result = result.replaceAll(
        RegExp(pattern, caseSensitive: false),
        replacement,
      );
    });

    // Escape remaining special characters
    result = escapeSql(result);

    // Limit length
    if (result.length > 200) {
      result = result.substring(0, 200);
    }

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Log Sanitization (Security)
  // ─────────────────────────────────────────────────────────────────────────────

  /// Patterns for sensitive data
  static final List<RegExp> _sensitivePatterns = [
    // Credit card numbers (basic pattern)
    RegExp(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
    // Email addresses
    RegExp(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
    // Phone numbers (international format)
    RegExp(r'\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}'),
    // Social security numbers (if applicable)
    RegExp(r'\b\d{3}-\d{2}-\d{4}\b'),
    // IP addresses
    RegExp(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
    // API keys/tokens (common patterns)
    RegExp(r'\b[A-Za-z0-9]{32,}\b'),
    // Password fields (common keywords)
    RegExp(r'(password|passwd|pwd|secret|token|key)[\s:=]+[^\s,]+', caseSensitive: false),
  ];

  /// Convert string to log-safe format (remove sensitive data)
  static String toLogSafe(String text, {String replacement = '[REDACTED]'}) {
    String result = text;

    // Replace sensitive patterns
    for (final pattern in _sensitivePatterns) {
      result = result.replaceAll(pattern, replacement);
    }

    // Limit length for logs
    if (result.length > 500) {
      result = '${result.substring(0, 500)}... [TRUNCATED]';
    }

    return result;
  }

  /// Sanitize message for logging (specific for chat messages)
  static String sanitizeForLog(String message) {
    // Remove sensitive data
    String result = toLogSafe(message);

    // Remove excessive whitespace
    result = result.replaceAll(RegExp(r'\s+'), ' ').trim();

    // Encode special characters that might break logs
    result = result.replaceAll('\n', r'\n');
    result = result.replaceAll('\r', r'\r');
    result = result.replaceAll('\t', r'\t');

    return result;
  }

  /// Redact sensitive fields from JSON/Map data for logging
  static Map<String, dynamic> sanitizeMapForLog(Map<String, dynamic> data) {
    final sanitized = <String, dynamic>{};

    final sensitiveKeys = {
      'password',
      'passwd',
      'pwd',
      'secret',
      'token',
      'apiKey',
      'api_key',
      'accessToken',
      'access_token',
      'refreshToken',
      'refresh_token',
      'creditCard',
      'credit_card',
      'ssn',
      'socialSecurity',
      'social_security',
    };

    data.forEach((key, value) {
      final lowerKey = key.toLowerCase();

      // Check if key is sensitive
      if (sensitiveKeys.any((s) => lowerKey.contains(s))) {
        sanitized[key] = '[REDACTED]';
      } else if (value is Map<String, dynamic>) {
        // Recursively sanitize nested maps
        sanitized[key] = sanitizeMapForLog(value);
      } else if (value is String) {
        // Sanitize string values
        sanitized[key] = toLogSafe(value);
      } else {
        sanitized[key] = value;
      }
    });

    return sanitized;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // General Text Sanitization
  // ─────────────────────────────────────────────────────────────────────────────

  /// Remove control characters (except newline, tab)
  static String removeControlCharacters(String text) {
    // Remove all control characters except \n, \r, \t
    return text.replaceAll(
      RegExp(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]'),
      '',
    );
  }

  /// Normalize whitespace
  static String normalizeWhitespace(String text) {
    // Replace multiple spaces with single space
    String result = text.replaceAll(RegExp(r'\s+'), ' ');

    // Remove leading/trailing whitespace
    result = result.trim();

    return result;
  }

  /// Remove zero-width characters (often used in obfuscation)
  static String removeZeroWidthCharacters(String text) {
    return text.replaceAll(
      RegExp(r'[\u200B-\u200D\uFEFF]'),
      '',
    );
  }

  /// Comprehensive text sanitization
  static String sanitizeText(String text, {
    bool removeHtml = true,
    bool normalizeSpaces = true,
    bool removeControls = true,
    bool removeZeroWidth = true,
  }) {
    String result = text;

    if (removeZeroWidth) {
      result = removeZeroWidthCharacters(result);
    }

    if (removeControls) {
      result = removeControlCharacters(result);
    }

    if (removeHtml) {
      result = sanitizeHtml(result);
    }

    if (normalizeSpaces) {
      result = normalizeWhitespace(result);
    }

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Special Character Escaping
  // ─────────────────────────────────────────────────────────────────────────────

  /// Escape special characters for JSON
  static String escapeJson(String text) {
    String result = text;

    // Escape backslash first
    result = result.replaceAll(r'\', r'\\');

    // Escape quotes
    result = result.replaceAll('"', r'\"');

    // Escape control characters
    result = result.replaceAll('\n', r'\n');
    result = result.replaceAll('\r', r'\r');
    result = result.replaceAll('\t', r'\t');
    result = result.replaceAll('\b', r'\b');
    result = result.replaceAll('\f', r'\f');

    return result;
  }

  /// Escape special characters for CSV
  static String escapeCsv(String text) {
    // If text contains comma, quote, or newline, wrap in quotes and escape quotes
    if (text.contains(',') || text.contains('"') || text.contains('\n')) {
      return '"${text.replaceAll('"', '""')}"';
    }
    return text;
  }

  /// Escape special characters for URLs
  static String escapeUrl(String text) {
    return Uri.encodeComponent(text);
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // File Path Sanitization
  // ─────────────────────────────────────────────────────────────────────────────

  /// Sanitize file name (remove path traversal attempts)
  static String sanitizeFileName(String fileName) {
    String result = fileName;

    // Remove path traversal patterns
    result = result.replaceAll('..', '');
    result = result.replaceAll('/', '');
    result = result.replaceAll(r'\', '');

    // Remove null bytes
    result = result.replaceAll('\x00', '');

    // Replace special characters with underscore
    result = result.replaceAll(RegExp(r'[<>:"|?*]'), '_');

    // Remove leading/trailing dots and spaces
    result = result.replaceAll(RegExp(r'^[\s.]+|[\s.]+$'), '');

    // Limit length
    if (result.length > 255) {
      final extension = result.split('.').last;
      final nameWithoutExt = result.substring(0, result.lastIndexOf('.'));
      result = '${nameWithoutExt.substring(0, 250)}.$extension';
    }

    return result;
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Utility Methods
  // ─────────────────────────────────────────────────────────────────────────────

  /// Truncate text to maximum length
  static String truncate(String text, int maxLength, {String suffix = '...'}) {
    if (text.length <= maxLength) {
      return text;
    }

    final truncatedLength = maxLength - suffix.length;
    return text.substring(0, truncatedLength) + suffix;
  }

  /// Clean phone number (remove all non-digits)
  static String cleanPhoneNumber(String phone) {
    return phone.replaceAll(RegExp(r'[^\d+]'), '');
  }

  /// Clean email (trim and lowercase)
  static String cleanEmail(String email) {
    return email.trim().toLowerCase();
  }

  /// Sanitize user input for display (prevent XSS in UI)
  static String sanitizeForDisplay(String text) {
    // Encode HTML entities
    String result = encodeHtml(text);

    // Remove zero-width characters
    result = removeZeroWidthCharacters(result);

    // Remove control characters
    result = removeControlCharacters(result);

    return result;
  }

  /// Sanitize user input for storage (comprehensive)
  static String sanitizeForStorage(String text) {
    String result = text;

    // Remove zero-width characters
    result = removeZeroWidthCharacters(result);

    // Remove control characters
    result = removeControlCharacters(result);

    // Remove script tags
    result = removeScriptTags(result);

    // Normalize whitespace
    result = normalizeWhitespace(result);

    // Trim
    result = result.trim();

    return result;
  }
}
