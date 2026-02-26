import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:flutter/foundation.dart';

import '../utils/app_logger.dart';

/// Certificate Pin Manager
/// مدير تثبيت الشهادات الرقمية
///
/// Provides comprehensive certificate pinning functionality for SAHOOL API gateway domains.
/// Implements proper validation, fallback mechanisms, and security event logging.
///
/// ## Features
/// - SHA256 certificate fingerprint pinning
/// - SPKI (Subject Public Key Info) pinning support
/// - Fallback pins for seamless certificate rotation
/// - Pin validation and integrity checking
/// - Security event logging and monitoring
/// - Production vs development mode handling
///
/// ## Usage
/// ```dart
/// final pinManager = CertificatePinManager();
///
/// // Validate a certificate
/// final result = await pinManager.validateCertificate(certificate, 'api.sahool.app');
/// if (!result.isValid) {
///   // Handle validation failure
///   print(result.errorMessage);
/// }
///
/// // Check pin health
/// final health = pinManager.checkPinHealth();
/// if (!health.isHealthy) {
///   print('Warning: ${health.warnings.join(', ')}');
/// }
/// ```
///
/// ## Security Event Logging
/// All security-relevant events are logged via AppLogger with the 'SECURITY' tag:
/// - Certificate validation failures
/// - Pin mismatches
/// - Expired pin usage attempts
/// - Placeholder pin detection
/// - Configuration errors
///
/// ## Important Notes
/// - ALWAYS replace placeholder pins with actual production certificate fingerprints
/// - Configure at least 2-3 pins per domain for certificate rotation support
/// - Monitor pin expiration dates and rotate before expiry
/// - Test thoroughly in staging before production deployment

// =============================================================================
// SECURITY CONSTANTS
// =============================================================================

/// Minimum number of pins required per domain for safe rotation
const int kMinPinsPerDomain = 2;

/// Warning threshold for expiring pins (days)
const int kExpiryWarningDays = 30;

/// Critical threshold for expiring pins (days)
const int kExpiryCriticalDays = 7;

// =============================================================================
// PIN TYPE ENUMERATION
// =============================================================================

/// Certificate pin type
/// نوع تثبيت الشهادة
enum CertificatePinType {
  /// SHA-256 hash of the full certificate DER encoding
  /// Used for Android certificate pinning via Dio/HttpClient
  sha256Certificate,

  /// SHA-256 hash of the Subject Public Key Info (SPKI)
  /// Used for iOS certificate pinning via URLSession
  /// More resilient to certificate renewal as public key remains same
  sha256Spki,

  /// SHA-256 hash of the public key only
  /// Alternative to SPKI pinning
  sha256PublicKey,
}

// =============================================================================
// PIN VALIDATION RESULT
// =============================================================================

/// Result of certificate pin validation
/// نتيجة التحقق من تثبيت الشهادة
class CertificatePinValidationResult {
  /// Whether the certificate is valid
  final bool isValid;

  /// The pin that matched (if valid)
  final CertificatePinEntry? matchedPin;

  /// Error message if validation failed
  final String? errorMessage;

  /// Error code for programmatic handling
  final CertificatePinError? errorCode;

  /// The actual certificate fingerprint
  final String? actualFingerprint;

  /// Validation timestamp
  final DateTime timestamp;

  const CertificatePinValidationResult._({
    required this.isValid,
    this.matchedPin,
    this.errorMessage,
    this.errorCode,
    this.actualFingerprint,
    required this.timestamp,
  });

  /// Create a successful validation result
  factory CertificatePinValidationResult.success({
    required CertificatePinEntry matchedPin,
    String? actualFingerprint,
  }) {
    return CertificatePinValidationResult._(
      isValid: true,
      matchedPin: matchedPin,
      actualFingerprint: actualFingerprint,
      timestamp: DateTime.now(),
    );
  }

  /// Create a failed validation result
  factory CertificatePinValidationResult.failure({
    required String errorMessage,
    required CertificatePinError errorCode,
    String? actualFingerprint,
  }) {
    return CertificatePinValidationResult._(
      isValid: false,
      errorMessage: errorMessage,
      errorCode: errorCode,
      actualFingerprint: actualFingerprint,
      timestamp: DateTime.now(),
    );
  }

  @override
  String toString() {
    if (isValid) {
      return 'CertificatePinValidationResult(valid, matched: ${matchedPin?.description})';
    }
    return 'CertificatePinValidationResult(invalid, error: $errorCode - $errorMessage)';
  }
}

/// Certificate pin validation error codes
/// رموز أخطاء التحقق من تثبيت الشهادة
enum CertificatePinError {
  /// No pins configured for the domain
  noPinsConfigured,

  /// Certificate fingerprint does not match any configured pin
  pinMismatch,

  /// All configured pins have expired
  allPinsExpired,

  /// Certificate extraction failed
  certificateExtractionFailed,

  /// Invalid certificate format
  invalidCertificateFormat,

  /// Placeholder pin detected in production
  placeholderPinDetected,

  /// Configuration error
  configurationError,

  /// Unknown error
  unknown,
}

// =============================================================================
// CERTIFICATE PIN ENTRY
// =============================================================================

/// A single certificate pin entry
/// إدخال تثبيت شهادة واحدة
class CertificatePinEntry {
  /// The type of pin (SHA256 certificate, SPKI, or public key)
  final CertificatePinType type;

  /// The pin value (64-character lowercase hexadecimal SHA256 hash)
  final String value;

  /// Human-readable description of this pin
  final String description;

  /// Expiry date after which this pin should not be used
  final DateTime? expiryDate;

  /// Whether this is a primary pin (vs backup/fallback)
  final bool isPrimary;

  /// When this pin was added to the configuration
  final DateTime? addedDate;

  const CertificatePinEntry({
    required this.type,
    required this.value,
    required this.description,
    this.expiryDate,
    this.isPrimary = false,
    this.addedDate,
  });

  /// Check if this pin has expired
  bool get isExpired {
    if (expiryDate == null) return false;
    return DateTime.now().isAfter(expiryDate!);
  }

  /// Days until this pin expires (null if no expiry date)
  int? get daysUntilExpiry {
    if (expiryDate == null) return null;
    return expiryDate!.difference(DateTime.now()).inDays;
  }

  /// Check if this pin is expiring soon (within warning threshold)
  bool get isExpiringSoon {
    final days = daysUntilExpiry;
    if (days == null) return false;
    return days <= kExpiryWarningDays && days > 0;
  }

  /// Check if this pin is critically close to expiring
  bool get isExpiryCritical {
    final days = daysUntilExpiry;
    if (days == null) return false;
    return days <= kExpiryCriticalDays && days > 0;
  }

  /// Validate the pin value format
  bool get isValidFormat {
    // SHA256 hash should be exactly 64 hexadecimal characters
    final sha256Regex = RegExp(r'^[a-f0-9]{64}$');
    return sha256Regex.hasMatch(value.toLowerCase());
  }

  @override
  String toString() {
    return 'CertificatePinEntry(type: $type, value: ${value.substring(0, 16)}..., '
        'description: $description, expired: $isExpired)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is CertificatePinEntry &&
        other.type == type &&
        other.value.toLowerCase() == value.toLowerCase();
  }

  @override
  int get hashCode => type.hashCode ^ value.toLowerCase().hashCode;
}

// =============================================================================
// PIN HEALTH CHECK
// =============================================================================

/// Health check result for pin configuration
/// نتيجة فحص صحة تكوين التثبيت
class PinHealthCheckResult {
  /// Overall health status
  final bool isHealthy;

  /// List of warnings (non-critical issues)
  final List<String> warnings;

  /// List of errors (critical issues)
  final List<String> errors;

  /// Domains with issues
  final Map<String, List<String>> domainIssues;

  /// Total number of configured pins
  final int totalPins;

  /// Number of valid (non-expired) pins
  final int validPins;

  /// Number of expiring pins (within warning threshold)
  final int expiringPins;

  const PinHealthCheckResult({
    required this.isHealthy,
    required this.warnings,
    required this.errors,
    required this.domainIssues,
    required this.totalPins,
    required this.validPins,
    required this.expiringPins,
  });

  @override
  String toString() {
    final buffer = StringBuffer();
    buffer.writeln('Pin Health Check Result');
    buffer.writeln('=======================');
    buffer.writeln('Status: ${isHealthy ? "HEALTHY" : "UNHEALTHY"}');
    buffer.writeln('Total Pins: $totalPins');
    buffer.writeln('Valid Pins: $validPins');
    buffer.writeln('Expiring Soon: $expiringPins');

    if (errors.isNotEmpty) {
      buffer.writeln('\nErrors:');
      for (final error in errors) {
        buffer.writeln('  - $error');
      }
    }

    if (warnings.isNotEmpty) {
      buffer.writeln('\nWarnings:');
      for (final warning in warnings) {
        buffer.writeln('  - $warning');
      }
    }

    return buffer.toString();
  }
}

// =============================================================================
// CERTIFICATE PIN MANAGER
// =============================================================================

/// Certificate Pin Manager
/// مدير تثبيت الشهادات
///
/// Manages certificate pins for SAHOOL API gateway domains with validation,
/// fallback support, and comprehensive security event logging.
class CertificatePinManager {
  /// Internal pin storage
  final Map<String, List<CertificatePinEntry>> _pins;

  /// Whether to enforce strict validation (fail if no match)
  final bool enforceStrict;

  /// Whether to allow debug bypass
  final bool allowDebugBypass;

  /// Security event callback for external monitoring
  final void Function(SecurityEvent)? onSecurityEvent;

  /// Known placeholder values that must be replaced before production
  static const Set<String> _knownPlaceholders = {
    // SHA256 of empty string
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    // Common test hashes
    '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae', // "foo"
    '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d', // "bar"
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', // "abc"
    'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9', // "baz"
    '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589', // "hello"
    'cd2662154e6d76b2b2b92e70c0cac3ccf534f9b74eb5b89819ec509083d00a50', // "world"
  };

  CertificatePinManager({
    Map<String, List<CertificatePinEntry>>? customPins,
    this.enforceStrict = true,
    this.allowDebugBypass = true,
    this.onSecurityEvent,
  }) : _pins = customPins ?? _getDefaultPins() {
    // Validate configuration on initialization
    _validateConfiguration();
  }

  // ===========================================================================
  // DEFAULT PIN CONFIGURATION
  // ===========================================================================

  /// Get default certificate pins for SAHOOL API gateway domains
  ///
  /// ============================================================================
  /// CRITICAL: PLACEHOLDER VALUES - MUST REPLACE BEFORE PRODUCTION
  /// ============================================================================
  ///
  /// The SHA-256 fingerprints below are EXAMPLE PLACEHOLDERS only.
  /// They are formatted correctly but contain fake values.
  ///
  /// BEFORE DEPLOYING TO PRODUCTION:
  /// 1. Generate actual certificate fingerprints using one of these methods:
  ///
  ///    Method A - OpenSSL CLI:
  ///    ```bash
  ///    openssl s_client -connect api.sahool.app:443 -servername api.sahool.app \
  ///      < /dev/null 2>/dev/null | \
  ///      openssl x509 -noout -fingerprint -sha256 | \
  ///      cut -d= -f2 | tr -d ':' | tr 'A-Z' 'a-z'
  ///    ```
  ///
  ///    Method B - Using getCertificateInfo() helper:
  ///    ```dart
  ///    final info = await getCertificateInfo('https://api.sahool.app');
  ///    print('SHA256: ${info?.sha256Fingerprint}');
  ///    ```
  ///
  /// 2. Replace the placeholder values below with actual fingerprints
  /// 3. Update expiry dates to match your certificates
  /// 4. Test in staging environment before production deployment
  ///
  /// ============================================================================
  static Map<String, List<CertificatePinEntry>> _getDefaultPins() {
    return {
      // ========================================================================
      // PRODUCTION API GATEWAY - api.sahool.app
      // ========================================================================
      'api.sahool.app': [
        // PRIMARY CERTIFICATE PIN
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
          description: 'Production API primary certificate',
          expiryDate: DateTime(2026, 12, 31),
          isPrimary: true,
          addedDate: DateTime(2025, 1, 1),
        ),

        // BACKUP/FALLBACK CERTIFICATE PIN #1
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
          description: 'Production API backup certificate #1',
          expiryDate: DateTime(2027, 6, 30),
          isPrimary: false,
          addedDate: DateTime(2025, 1, 1),
        ),

        // BACKUP/FALLBACK CERTIFICATE PIN #2
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              'ea0ed0d218a934de81ef856888b824493ec135dcfa320bdb80fb252f926272bd',
          description: 'Production API backup certificate #2',
          expiryDate: DateTime(2027, 12, 31),
          isPrimary: false,
          addedDate: DateTime(2025, 1, 1),
        ),
      ],

      // ========================================================================
      // PRODUCTION WEBSOCKET GATEWAY - ws.sahool.app
      // ========================================================================
      'ws.sahool.app': [
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              '7bfbf46c2b363df94bc6289a082fc007fd22a93cc45175736c1d8c18c31b1fa6',
          description: 'Production WebSocket primary certificate',
          expiryDate: DateTime(2026, 12, 31),
          isPrimary: true,
          addedDate: DateTime(2025, 1, 1),
        ),
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              '7bfbf46c2b363df94bc6289a082fc007fd22a93cc45175736c1d8c18c31b1fa6',
          description: 'Production WebSocket backup certificate',
          expiryDate: DateTime(2027, 6, 30),
          isPrimary: false,
          addedDate: DateTime(2025, 1, 1),
        ),
      ],

      // ========================================================================
      // WILDCARD CERTIFICATE - *.sahool.io
      // ========================================================================
      '*.sahool.io': [
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              '42f64a30d2849cb1e2eeb0ad9f2dbc6aeef30991dcb2fc29c47edd8d3ddfe5bc',
          description: 'Wildcard *.sahool.io primary certificate',
          expiryDate: DateTime(2026, 12, 31),
          isPrimary: true,
          addedDate: DateTime(2025, 1, 1),
        ),
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              '42f64a30d2849cb1e2eeb0ad9f2dbc6aeef30991dcb2fc29c47edd8d3ddfe5bc',
          description: 'Wildcard *.sahool.io backup certificate',
          expiryDate: DateTime(2027, 6, 30),
          isPrimary: false,
          addedDate: DateTime(2025, 1, 1),
        ),
      ],

      // ========================================================================
      // STAGING API GATEWAY - api-staging.sahool.app
      // ========================================================================
      // Staging pins use the same production certificates for now
      // TODO: Replace with actual staging certificate fingerprints when staging is deployed
      'api-staging.sahool.app': [
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
          description:
              'Staging API primary certificate (using production cert)',
          expiryDate: DateTime(2026, 12, 31),
          isPrimary: true,
          addedDate: DateTime(2025, 1, 1),
        ),
        CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value:
              'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
          description: 'Staging API backup certificate (using production cert)',
          expiryDate: DateTime(2027, 6, 30),
          isPrimary: false,
          addedDate: DateTime(2025, 1, 1),
        ),
      ],
    };
  }

  // ===========================================================================
  // CONFIGURATION VALIDATION
  // ===========================================================================

  /// Validate pin configuration on initialization
  void _validateConfiguration() {
    // Skip validation in debug mode if bypass is allowed
    if (kDebugMode && allowDebugBypass) {
      _logSecurityEvent(
        SecurityEventType.configValidation,
        'Pin validation skipped in debug mode',
        severity: SecurityEventSeverity.info,
      );
      return;
    }

    final errors = <String>[];
    final warnings = <String>[];

    for (final entry in _pins.entries) {
      final domain = entry.key;
      final pins = entry.value;

      // Check minimum pin count
      if (pins.length < kMinPinsPerDomain) {
        warnings.add(
          'Domain "$domain" has only ${pins.length} pins (recommended: $kMinPinsPerDomain+)',
        );
      }

      // Validate each pin
      for (final pin in pins) {
        // Check format
        if (!pin.isValidFormat) {
          errors.add(
              'Invalid pin format for "$domain": ${pin.value.substring(0, 16)}...');
        }

        // Check for known placeholders in release mode
        if (!kDebugMode && _isPlaceholderPin(pin.value)) {
          errors.add(
            'CRITICAL: Placeholder pin detected for "$domain" - '
            'must replace with actual certificate fingerprint before production',
          );
        }

        // Check expiry
        if (pin.isExpired) {
          warnings.add('Expired pin for "$domain": ${pin.description}');
        } else if (pin.isExpiryCritical) {
          warnings.add(
            'Pin expiring in ${pin.daysUntilExpiry} days for "$domain": ${pin.description}',
          );
        } else if (pin.isExpiringSoon) {
          warnings.add(
            'Pin expiring soon (${pin.daysUntilExpiry} days) for "$domain": ${pin.description}',
          );
        }
      }

      // Check if all pins are expired
      if (pins.every((p) => p.isExpired)) {
        errors.add('All pins expired for domain "$domain"');
      }
    }

    // Log validation results
    if (errors.isNotEmpty) {
      for (final error in errors) {
        _logSecurityEvent(
          SecurityEventType.configError,
          error,
          severity: SecurityEventSeverity.critical,
        );
      }

      // In release mode, throw exception for critical errors
      if (!kDebugMode) {
        throw CertificatePinConfigurationException(
          'Certificate pin configuration has critical errors:\n${errors.join('\n')}',
        );
      }
    }

    if (warnings.isNotEmpty) {
      for (final warning in warnings) {
        _logSecurityEvent(
          SecurityEventType.configWarning,
          warning,
          severity: SecurityEventSeverity.warning,
        );
      }
    }
  }

  /// Check if a pin value is a known placeholder
  bool _isPlaceholderPin(String value) {
    final normalized = value.toLowerCase();

    // Check against known placeholder hashes
    if (_knownPlaceholders.contains(normalized)) {
      return true;
    }

    // Check for obvious placeholder patterns
    if (normalized.contains('placeholder') ||
        normalized.contains('replace') ||
        normalized.contains('example') ||
        normalized.contains('aaaa') ||
        normalized.contains('bbbb') ||
        normalized.contains('0000000000000000')) {
      return true;
    }

    // Check for sequential/repeating patterns that indicate placeholder
    final uniqueChars = normalized.split('').toSet();
    if (uniqueChars.length < 8) {
      // Real SHA256 hashes have much higher entropy
      return true;
    }

    return false;
  }

  // ===========================================================================
  // CERTIFICATE VALIDATION
  // ===========================================================================

  /// Validate a certificate against configured pins
  ///
  /// Returns a [CertificatePinValidationResult] indicating success or failure
  /// with detailed information about the validation outcome.
  CertificatePinValidationResult validateCertificate(
    X509Certificate certificate,
    String host,
  ) {
    // Debug bypass
    if (kDebugMode && allowDebugBypass) {
      _logSecurityEvent(
        SecurityEventType.validationBypassed,
        'Certificate validation bypassed for $host in debug mode',
        severity: SecurityEventSeverity.info,
        data: {'host': host},
      );

      return CertificatePinValidationResult.success(
        matchedPin: CertificatePinEntry(
          type: CertificatePinType.sha256Certificate,
          value: 'debug-bypass',
          description: 'Debug bypass - no validation performed',
        ),
      );
    }

    try {
      // Get pins for this host
      final pins = getPinsForHost(host);

      if (pins.isEmpty) {
        final result = CertificatePinValidationResult.failure(
          errorMessage: 'No certificate pins configured for host: $host',
          errorCode: CertificatePinError.noPinsConfigured,
        );

        _logSecurityEvent(
          SecurityEventType.validationFailed,
          'No pins configured for host',
          severity: SecurityEventSeverity.error,
          data: {'host': host},
        );

        // If not enforcing strict mode, allow connection
        if (!enforceStrict) {
          return CertificatePinValidationResult.success(
            matchedPin: CertificatePinEntry(
              type: CertificatePinType.sha256Certificate,
              value: 'no-pins-non-strict',
              description: 'No pins configured (non-strict mode)',
            ),
          );
        }

        return result;
      }

      // Calculate certificate fingerprint
      final certFingerprint = _calculateCertificateFingerprint(certificate);

      // Check each pin (non-expired only)
      for (final pin in pins) {
        if (pin.isExpired) {
          _logSecurityEvent(
            SecurityEventType.expiredPinSkipped,
            'Skipping expired pin',
            severity: SecurityEventSeverity.warning,
            data: {
              'host': host,
              'pin': pin.description,
              'expiredDate': pin.expiryDate?.toIso8601String(),
            },
          );
          continue;
        }

        if (_matchesPin(certFingerprint, pin)) {
          _logSecurityEvent(
            SecurityEventType.validationSuccess,
            'Certificate validated successfully',
            severity: SecurityEventSeverity.info,
            data: {
              'host': host,
              'matchedPin': pin.description,
              'isPrimary': pin.isPrimary,
            },
          );

          return CertificatePinValidationResult.success(
            matchedPin: pin,
            actualFingerprint: certFingerprint,
          );
        }
      }

      // No match found - check if all pins were expired
      final nonExpiredPins = pins.where((p) => !p.isExpired).toList();
      if (nonExpiredPins.isEmpty) {
        _logSecurityEvent(
          SecurityEventType.allPinsExpired,
          'All configured pins have expired',
          severity: SecurityEventSeverity.critical,
          data: {
            'host': host,
            'totalPins': pins.length,
          },
        );

        return CertificatePinValidationResult.failure(
          errorMessage: 'All certificate pins for $host have expired',
          errorCode: CertificatePinError.allPinsExpired,
          actualFingerprint: certFingerprint,
        );
      }

      // Pin mismatch
      _logSecurityEvent(
        SecurityEventType.pinMismatch,
        'Certificate fingerprint does not match any configured pin',
        severity: SecurityEventSeverity.critical,
        data: {
          'host': host,
          'actualFingerprint': certFingerprint.substring(0, 16) + '...',
          'configuredPins': nonExpiredPins.length,
        },
      );

      return CertificatePinValidationResult.failure(
        errorMessage:
            'Certificate fingerprint does not match any configured pin for $host',
        errorCode: CertificatePinError.pinMismatch,
        actualFingerprint: certFingerprint,
      );
    } catch (e, stackTrace) {
      _logSecurityEvent(
        SecurityEventType.validationError,
        'Error during certificate validation',
        severity: SecurityEventSeverity.error,
        data: {
          'host': host,
          'error': e.toString(),
        },
      );

      AppLogger.e(
        'Certificate validation error',
        tag: 'SECURITY',
        error: e,
        stackTrace: stackTrace,
      );

      return CertificatePinValidationResult.failure(
        errorMessage: 'Certificate validation failed: $e',
        errorCode: CertificatePinError.unknown,
      );
    }
  }

  /// Calculate SHA256 fingerprint of certificate
  String _calculateCertificateFingerprint(X509Certificate certificate) {
    final certBytes = certificate.der;
    final digest = sha256.convert(certBytes);
    return digest.toString().toLowerCase();
  }

  /// Check if fingerprint matches a pin
  bool _matchesPin(String fingerprint, CertificatePinEntry pin) {
    return fingerprint.toLowerCase() == pin.value.toLowerCase();
  }

  // ===========================================================================
  // PIN RETRIEVAL
  // ===========================================================================

  /// Get pins for a specific host (supports wildcard matching)
  List<CertificatePinEntry> getPinsForHost(String host) {
    final pins = <CertificatePinEntry>[];

    // Exact match
    if (_pins.containsKey(host)) {
      pins.addAll(_pins[host]!);
    }

    // Wildcard match (*.domain.com)
    for (final entry in _pins.entries) {
      if (entry.key.startsWith('*.')) {
        final wildcardDomain = entry.key.substring(2);
        if (host.endsWith(wildcardDomain) && host != wildcardDomain) {
          pins.addAll(entry.value);
        }
      }
    }

    return pins;
  }

  /// Get all configured domains
  List<String> getConfiguredDomains() {
    return _pins.keys.toList();
  }

  /// Get pin count for a domain
  int getPinCountForDomain(String domain) {
    return getPinsForHost(domain).length;
  }

  // ===========================================================================
  // PIN MANAGEMENT
  // ===========================================================================

  /// Add a new pin for a domain
  void addPin(String domain, CertificatePinEntry pin) {
    _pins.putIfAbsent(domain, () => []);
    _pins[domain]!.add(pin);

    _logSecurityEvent(
      SecurityEventType.pinAdded,
      'New pin added',
      severity: SecurityEventSeverity.info,
      data: {
        'domain': domain,
        'description': pin.description,
        'expiryDate': pin.expiryDate?.toIso8601String(),
      },
    );
  }

  /// Remove expired pins from all domains
  int removeExpiredPins() {
    int removedCount = 0;

    for (final domain in _pins.keys.toList()) {
      final originalCount = _pins[domain]!.length;
      _pins[domain]!.removeWhere((pin) => pin.isExpired);
      removedCount += originalCount - _pins[domain]!.length;

      // Remove domain if no pins left
      if (_pins[domain]!.isEmpty) {
        _pins.remove(domain);
      }
    }

    if (removedCount > 0) {
      _logSecurityEvent(
        SecurityEventType.pinsRemoved,
        'Expired pins removed',
        severity: SecurityEventSeverity.info,
        data: {'removedCount': removedCount},
      );
    }

    return removedCount;
  }

  // ===========================================================================
  // HEALTH CHECK
  // ===========================================================================

  /// Perform a health check on pin configuration
  PinHealthCheckResult checkPinHealth() {
    final warnings = <String>[];
    final errors = <String>[];
    final domainIssues = <String, List<String>>{};
    int totalPins = 0;
    int validPins = 0;
    int expiringPins = 0;

    for (final entry in _pins.entries) {
      final domain = entry.key;
      final pins = entry.value;
      final issues = <String>[];

      totalPins += pins.length;

      // Count valid pins
      final nonExpiredPins = pins.where((p) => !p.isExpired).toList();
      validPins += nonExpiredPins.length;

      // Count expiring pins
      final soonExpiring = pins.where((p) => p.isExpiringSoon).toList();
      expiringPins += soonExpiring.length;

      // Check for issues
      if (pins.length < kMinPinsPerDomain) {
        issues.add(
            'Insufficient pins (has ${pins.length}, need $kMinPinsPerDomain)');
        warnings.add('$domain: Insufficient backup pins for safe rotation');
      }

      if (nonExpiredPins.isEmpty) {
        issues.add('All pins expired');
        errors.add('$domain: All pins have expired');
      }

      if (soonExpiring.isNotEmpty) {
        issues.add(
            '${soonExpiring.length} pin(s) expiring within $kExpiryWarningDays days');
        warnings.add('$domain: ${soonExpiring.length} pin(s) expiring soon');
      }

      // Check for placeholders
      final placeholders =
          pins.where((p) => _isPlaceholderPin(p.value)).toList();
      if (placeholders.isNotEmpty) {
        issues.add('${placeholders.length} placeholder pin(s) detected');
        errors.add('$domain: Contains placeholder pins that must be replaced');
      }

      if (issues.isNotEmpty) {
        domainIssues[domain] = issues;
      }
    }

    final isHealthy = errors.isEmpty;

    return PinHealthCheckResult(
      isHealthy: isHealthy,
      warnings: warnings,
      errors: errors,
      domainIssues: domainIssues,
      totalPins: totalPins,
      validPins: validPins,
      expiringPins: expiringPins,
    );
  }

  // ===========================================================================
  // SECURITY EVENT LOGGING
  // ===========================================================================

  /// Log a security event
  void _logSecurityEvent(
    SecurityEventType type,
    String message, {
    SecurityEventSeverity severity = SecurityEventSeverity.info,
    Map<String, dynamic>? data,
  }) {
    final event = SecurityEvent(
      type: type,
      message: message,
      severity: severity,
      data: data,
      timestamp: DateTime.now(),
    );

    // Log to AppLogger
    switch (severity) {
      case SecurityEventSeverity.critical:
        AppLogger.critical(
          '[CERT_PIN] $message',
          tag: 'SECURITY',
          data: data,
        );
        break;
      case SecurityEventSeverity.error:
        AppLogger.e(
          '[CERT_PIN] $message',
          tag: 'SECURITY',
          data: data,
        );
        break;
      case SecurityEventSeverity.warning:
        AppLogger.w(
          '[CERT_PIN] $message',
          tag: 'SECURITY',
          data: data,
        );
        break;
      case SecurityEventSeverity.info:
        AppLogger.i(
          '[CERT_PIN] $message',
          tag: 'SECURITY',
          data: data,
        );
        break;
    }

    // Notify external callback if provided
    onSecurityEvent?.call(event);
  }
}

// =============================================================================
// SECURITY EVENT TYPES
// =============================================================================

/// Security event type enumeration
enum SecurityEventType {
  configValidation,
  configError,
  configWarning,
  validationSuccess,
  validationFailed,
  validationBypassed,
  validationError,
  pinMismatch,
  allPinsExpired,
  expiredPinSkipped,
  pinAdded,
  pinsRemoved,
  placeholderDetected,
}

/// Security event severity levels
enum SecurityEventSeverity {
  info,
  warning,
  error,
  critical,
}

/// Security event record
class SecurityEvent {
  final SecurityEventType type;
  final String message;
  final SecurityEventSeverity severity;
  final Map<String, dynamic>? data;
  final DateTime timestamp;

  const SecurityEvent({
    required this.type,
    required this.message,
    required this.severity,
    this.data,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() => {
        'type': type.name,
        'message': message,
        'severity': severity.name,
        'data': data,
        'timestamp': timestamp.toIso8601String(),
      };

  @override
  String toString() {
    return 'SecurityEvent(${severity.name}: ${type.name} - $message)';
  }
}

// =============================================================================
// EXCEPTIONS
// =============================================================================

/// Exception thrown when certificate pin configuration is invalid
class CertificatePinConfigurationException implements Exception {
  final String message;

  const CertificatePinConfigurationException(this.message);

  @override
  String toString() => 'CertificatePinConfigurationException: $message';
}

/// Exception thrown when certificate validation fails
class CertificatePinValidationException implements Exception {
  final String message;
  final CertificatePinError errorCode;
  final String? host;
  final String? actualFingerprint;

  const CertificatePinValidationException({
    required this.message,
    required this.errorCode,
    this.host,
    this.actualFingerprint,
  });

  @override
  String toString() {
    return 'CertificatePinValidationException($errorCode): $message';
  }
}

// =============================================================================
// HELPER FUNCTIONS
// =============================================================================

/// Create a CertificatePinManager configured for the current environment
CertificatePinManager createPinManagerForEnvironment(String environment) {
  switch (environment.toLowerCase()) {
    case 'production':
    case 'prod':
      return CertificatePinManager(
        enforceStrict: true,
        allowDebugBypass: false,
      );
    case 'staging':
    case 'stage':
      return CertificatePinManager(
        enforceStrict: true,
        allowDebugBypass: true,
      );
    case 'development':
    case 'dev':
    default:
      return CertificatePinManager(
        enforceStrict: false,
        allowDebugBypass: true,
      );
  }
}

/// Validate a single pin value format
bool isValidPinFormat(String value) {
  final sha256Regex = RegExp(r'^[a-f0-9]{64}$');
  return sha256Regex.hasMatch(value.toLowerCase());
}

/// Format a fingerprint with colons for display
String formatFingerprintForDisplay(String fingerprint) {
  final normalized = fingerprint.toUpperCase();
  final buffer = StringBuffer();

  for (int i = 0; i < normalized.length; i += 2) {
    if (i > 0) buffer.write(':');
    buffer.write(normalized.substring(i, (i + 2).clamp(0, normalized.length)));
  }

  return buffer.toString();
}
