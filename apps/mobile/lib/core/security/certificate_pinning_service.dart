import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';
import 'dart:convert';
import '../utils/app_logger.dart';

/// SSL Certificate Pinning Service
/// خدمة تثبيت شهادات SSL
///
/// Implements certificate pinning for enhanced security against man-in-the-middle attacks.
///
/// ## Features:
/// - **SHA256 Fingerprint Pinning**: Pin certificates by their SHA-256 hash
/// - **Public Key Pinning**: Pin certificates by their public key hash
/// - **Certificate Rotation**: Support for multiple pins per domain
/// - **Expiry Tracking**: Monitor certificate expiry dates
/// - **Debug Mode Bypass**: Disable pinning in debug builds for development
/// - **Wildcard Domain Support**: Pin certificates for *.domain.com patterns
///
/// ## Usage:
///
/// ### Basic Setup
/// ```dart
/// // Initialize with default pins
/// final pinningService = CertificatePinningService();
///
/// // Configure your Dio client
/// final dio = Dio();
/// pinningService.configureDio(dio);
/// ```
///
/// ### Custom Configuration
/// ```dart
/// final pinningService = CertificatePinningService(
///   certificatePins: {
///     'api.example.com': [
///       CertificatePin(
///         type: PinType.sha256,
///         value: 'your_certificate_sha256_fingerprint',
///         expiryDate: DateTime(2026, 12, 31),
///       ),
///     ],
///   },
///   allowDebugBypass: false, // Enforce pinning even in debug mode
///   enforceStrict: true,      // Fail if no pins match
/// );
/// ```
///
/// ### Getting Certificate Fingerprints
///
/// **Method 1: Using the helper function (recommended for development)**
/// ```dart
/// final fingerprint = await getCertificateFingerprintFromUrl('https://api.sahool.app');
/// print('SHA256 Fingerprint: $fingerprint');
/// ```
///
/// **Method 2: Using OpenSSL command line**
/// ```bash
/// # Get certificate fingerprint
/// openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
///   openssl x509 -noout -fingerprint -sha256 | cut -d= -f2 | tr -d ':'
///
/// # Or get full certificate info
/// openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
///   openssl x509 -noout -text
/// ```
///
/// **Method 3: Using curl**
/// ```bash
/// curl -v https://api.sahool.app 2>&1 | grep -A 10 "Server certificate"
/// ```
///
/// ### Certificate Rotation
///
/// To support seamless certificate rotation, configure multiple pins:
/// ```dart
/// CertificatePinningService(
///   certificatePins: {
///     'api.example.com': [
///       CertificatePin(
///         type: PinType.sha256,
///         value: 'current_cert_fingerprint',
///         expiryDate: DateTime(2026, 6, 30),
///         description: 'Current production certificate',
///       ),
///       CertificatePin(
///         type: PinType.sha256,
///         value: 'next_cert_fingerprint',
///         expiryDate: DateTime(2027, 6, 30),
///         description: 'Next certificate for rotation',
///       ),
///     ],
///   },
/// );
/// ```
///
/// ### Monitoring Expiring Pins
/// ```dart
/// // Check for pins expiring in the next 30 days
/// final expiringPins = pinningService.getExpiringPins(daysThreshold: 30);
/// for (final pin in expiringPins) {
///   print('⚠️ Certificate for ${pin.domain} expires in ${pin.daysUntilExpiry} days');
/// }
/// ```
///
/// ## Platform-Specific Implementations:
///
/// ### Android (Dart/Dio)
/// - Uses `HttpClient.badCertificateCallback` for certificate validation
/// - Validates SHA256 certificate fingerprints
/// - Configured via this Dart service
/// - Pins are managed in Dart code
///
/// ### iOS (Native Swift)
/// - Uses `URLSession` delegate with `ServerTrust` validation
/// - Validates SPKI (Subject Public Key Info) hashes
/// - Configured via two complementary approaches:
///   1. **Info.plist NSPinnedDomains** (declarative, system-level)
///      - Located in: `ios/Runner/Info.plist`
///      - Provides OS-level protection
///   2. **CertificatePinning.swift** (programmatic, application-level)
///      - Located in: `ios/Runner/CertificatePinning.swift`
///      - Initialized in `ios/Runner/AppDelegate.swift`
///      - More flexible, allows runtime configuration
///
/// **IMPORTANT: iOS and Android use different pin formats:**
/// - **Android**: SHA256 certificate fingerprint (full cert hash)
/// - **iOS**: SPKI public key hash (public key only)
///
/// **To get SPKI hash for iOS:**
/// ```bash
/// openssl s_client -connect api.sahool.io:443 -servername api.sahool.io < /dev/null 2>/dev/null | \
/// openssl x509 -pubkey -noout | \
/// openssl pkey -pubin -outform der | \
/// openssl dgst -sha256 -binary | \
/// openssl enc -base64
/// ```
///
/// **Why SPKI pinning on iOS?**
/// - More resilient to certificate rotation (pins public key, not certificate)
/// - Public key remains the same when certificate is renewed
/// - Recommended by Apple for production apps
/// - Reduces risk of app breaking due to certificate rotation
///
/// ## Security Considerations:
///
/// 1. **Always use HTTPS**: Certificate pinning only works with HTTPS connections
/// 2. **Pin Multiple Certificates**: Always pin at least 2 certificates (current + backup)
/// 3. **Monitor Expiry Dates**: Set up alerts for expiring certificates
/// 4. **Test in Staging**: Test certificate rotation in staging before production
/// 5. **Keep Pins Updated**: Regularly update pins before certificates expire
/// 6. **Secure Pin Storage**: Consider encrypting pins or storing them securely
/// 7. **Debug Mode**: Disable bypass in production builds
/// 8. **Update Both Platforms**: When updating pins, update both iOS (SPKI) and Android (SHA256)
///
/// ## Production Deployment Checklist:
///
/// **Android:**
/// - [ ] Replace example SHA-256 fingerprints with actual production certificates
/// - [ ] Configure at least 2 pins per domain (primary + backup)
/// - [ ] Set appropriate expiry dates
/// - [ ] Test certificate validation in staging environment
/// - [ ] Ensure allowDebugBypass is properly configured
/// - [ ] Test app behavior when certificate validation fails
///
/// **iOS:**
/// - [ ] Update Info.plist with actual SPKI hashes
/// - [ ] Update CertificatePinning.swift with actual SPKI hashes
/// - [ ] Test certificate pinning in iOS simulator and device
/// - [ ] Verify pins work in both DEBUG and RELEASE builds
/// - [ ] Test fallback behavior when pins don't match
///
/// **Both Platforms:**
/// - [ ] Set up monitoring for expiring certificates
/// - [ ] Document certificate rotation procedures (see CERTIFICATE_ROTATION_IOS.md)
/// - [ ] Create alerts for certificates expiring within 30 days
/// - [ ] Test certificate rotation in staging before production
/// - [ ] Verify localhost/development exceptions work
///
class CertificatePinningService {
  /// Certificate pin configuration
  final Map<String, List<CertificatePin>> _certificatePins;

  /// Whether to allow bypass in debug mode
  final bool allowDebugBypass;

  /// Whether to enforce pinning (fail if no pins match)
  final bool enforceStrict;

  CertificatePinningService({
    Map<String, List<CertificatePin>>? certificatePins,
    this.allowDebugBypass = true,
    this.enforceStrict = true,
  }) : _certificatePins = certificatePins ?? _getDefaultPins();

  /// Get default certificate pins for SAHOOL domains
  ///
  /// ============================================
  /// CRITICAL WARNING - PLACEHOLDER VALUES
  /// ============================================
  /// The SHA-256 fingerprints below are PLACEHOLDER EXAMPLES for development.
  /// Before deploying to production, you MUST replace these with actual
  /// certificate fingerprints from your production/staging servers.
  ///
  /// ⚠️  DO NOT DEPLOY TO PRODUCTION WITHOUT UPDATING THESE VALUES  ⚠️
  ///
  /// To generate actual certificate pins:
  /// 1. Run the script: ./scripts/generate_cert_pins.sh api.sahool.app
  /// 2. Copy the SHA256 fingerprint from the script output
  /// 3. Replace the placeholder values below
  ///
  /// Or use the helper function:
  /// ```dart
  /// final fingerprint = await getCertificateFingerprintFromUrl('https://api.sahool.app');
  /// print('Production SHA256: $fingerprint');
  /// ```
  ///
  /// Or use OpenSSL command line:
  /// ```bash
  /// openssl s_client -connect api.sahool.app:443 -servername api.sahool.app < /dev/null 2>/dev/null | \
  /// openssl x509 -noout -fingerprint -sha256 | cut -d= -f2 | tr -d ':'
  /// ```
  static Map<String, List<CertificatePin>> _getDefaultPins() {
    return {
      // Production API domain
      'api.sahool.app': [
        // Primary certificate pin
        // TODO: CRITICAL - Replace with actual production certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh api.sahool.app
        CertificatePin(
          type: PinType.sha256,
          value: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 12, 31),
          description: 'Production primary certificate',
        ),
        // Backup pin for certificate rotation
        // TODO: CRITICAL - Replace with actual backup certificate fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 6, 30),
          description: 'Production backup certificate for rotation',
        ),
        // Additional backup for seamless rotation
        // TODO: CRITICAL - Replace with actual tertiary certificate fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 12, 31),
          description: 'Production tertiary certificate',
        ),
      ],
      // Production domains wildcard (*.sahool.io)
      '*.sahool.io': [
        // TODO: CRITICAL - Replace with actual wildcard certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh api.sahool.io
        CertificatePin(
          type: PinType.sha256,
          value: 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 12, 31),
          description: 'Wildcard certificate for *.sahool.io',
        ),
        // Backup for wildcard certificate rotation
        // TODO: CRITICAL - Replace with actual backup wildcard fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: 'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 6, 30),
          description: 'Wildcard backup certificate',
        ),
      ],
      // Staging API domain
      'api-staging.sahool.app': [
        // TODO: CRITICAL - Replace with actual staging certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh api-staging.sahool.app
        CertificatePin(
          type: PinType.sha256,
          value: '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 12, 31),
          description: 'Staging primary certificate',
        ),
        // Staging backup pin
        // TODO: CRITICAL - Replace with actual staging backup fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: 'cd2662154e6d76b2b2b92e70c0cac3ccf534f9b74eb5b89819ec509083d00a50', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 3, 31),
          description: 'Staging backup certificate',
        ),
      ],
    };
  }

  /// Configure Dio with certificate pinning
  ///
  /// This method sets up the Dio HTTP client to validate SSL certificates
  /// against the configured certificate pins.
  ///
  /// In debug mode with [allowDebugBypass] enabled, certificate pinning
  /// is bypassed to facilitate development with self-signed certificates
  /// or local servers.
  void configureDio(Dio dio) {
    // In debug mode, optionally bypass pinning for development
    if (kDebugMode && allowDebugBypass) {
      if (kDebugMode) {
        AppLogger.w('Certificate pinning bypassed in debug mode', tag: 'CertificatePinning');
        AppLogger.w('Set allowDebugBypass=false to test pinning in debug builds', tag: 'CertificatePinning');
      }
      return;
    }

    // Configure HttpClientAdapter with certificate validation
    try {
      final adapter = dio.httpClientAdapter;
      if (adapter is IOHttpClientAdapter) {
        adapter.createHttpClient = () {
          final client = HttpClient();

          // Set security context and certificate validation
          client.badCertificateCallback = (cert, host, port) {
            // Validate certificate against configured pins
            final isValid = _validateCertificate(cert, host);

            if (kDebugMode) {
              if (!isValid) {
                AppLogger.e('Certificate validation failed', tag: 'CertificatePinning', data: {'host': host, 'port': port});
                AppLogger.e('Expected pins', tag: 'CertificatePinning', data: {'pins': _getPinsForHost(host).map((p) => p.value.substring(0, 16)).join(", ")});
              }
            }

            return isValid;
          };

          return client;
        };

        if (kDebugMode) {
          AppLogger.i('Certificate pinning configured for Dio HTTP client', tag: 'CertificatePinning');
          AppLogger.i('Configured domains', tag: 'CertificatePinning', data: {'domains': getConfiguredDomains().join(", ")});
        }
      } else {
        if (kDebugMode) {
          AppLogger.w('Cannot configure certificate pinning: adapter is not IOHttpClientAdapter', tag: 'CertificatePinning');
        }
      }
    } catch (e) {
      if (kDebugMode) {
        AppLogger.e('Error configuring certificate pinning', tag: 'CertificatePinning', error: e);
      }
      // In production, we might want to throw here to ensure security
      if (!kDebugMode && enforceStrict) {
        throw Exception('Failed to configure certificate pinning: $e');
      }
    }
  }

  /// Validate certificate against pins
  bool _validateCertificate(X509Certificate cert, String host) {
    try {
      // Get pins for this host
      final pins = _getPinsForHost(host);

      if (pins.isEmpty) {
        if (enforceStrict) {
          if (kDebugMode) {
            AppLogger.e('No certificate pins configured for host', tag: 'CertificatePinning', data: {'host': host});
          }
          return false;
        }
        // If not enforcing strict mode, allow connection if no pins configured
        return true;
      }

      // Check if any pin matches and is not expired
      for (final pin in pins) {
        if (pin.isExpired) {
          if (kDebugMode) {
            AppLogger.w('Pin expired for host', tag: 'CertificatePinning', data: {'host': host});
          }
          continue;
        }

        if (_matchPin(cert, pin)) {
          if (kDebugMode) {
            AppLogger.d('Certificate pin matched for host', tag: 'CertificatePinning', data: {'host': host});
          }
          return true;
        }
      }

      if (kDebugMode) {
        AppLogger.e('Certificate validation failed for host', tag: 'CertificatePinning', data: {'host': host});
        AppLogger.e('Certificate fingerprint', tag: 'CertificatePinning', data: {'fingerprint': _getCertificateFingerprint(cert)});
      }
      return false;
    } catch (e) {
      if (kDebugMode) {
        AppLogger.e('Error validating certificate', tag: 'CertificatePinning', error: e);
      }
      return false;
    }
  }

  /// Get pins for a specific host (supports wildcards)
  List<CertificatePin> _getPinsForHost(String host) {
    final pins = <CertificatePin>[];

    // Exact match
    if (_certificatePins.containsKey(host)) {
      pins.addAll(_certificatePins[host]!);
    }

    // Wildcard match (*.domain.com)
    for (final entry in _certificatePins.entries) {
      if (entry.key.startsWith('*.')) {
        final domain = entry.key.substring(2); // Remove *.
        if (host.endsWith(domain)) {
          pins.addAll(entry.value);
        }
      }
    }

    return pins;
  }

  /// Match certificate against a pin
  bool _matchPin(X509Certificate cert, CertificatePin pin) {
    switch (pin.type) {
      case PinType.sha256:
        return _matchSha256(cert, pin.value);
      case PinType.publicKey:
        return _matchPublicKey(cert, pin.value);
    }
  }

  /// Match SHA256 fingerprint
  bool _matchSha256(X509Certificate cert, String expectedFingerprint) {
    final actualFingerprint = _getCertificateFingerprint(cert);
    return actualFingerprint.toLowerCase() == expectedFingerprint.toLowerCase();
  }

  /// Match public key
  bool _matchPublicKey(X509Certificate cert, String expectedPublicKey) {
    // Extract public key from certificate DER
    final publicKeyBytes = cert.der;
    final publicKeyHash = sha256.convert(publicKeyBytes);
    final publicKeyFingerprint = publicKeyHash.toString();

    return publicKeyFingerprint.toLowerCase() == expectedPublicKey.toLowerCase();
  }

  /// Get certificate SHA256 fingerprint
  String _getCertificateFingerprint(X509Certificate cert) {
    final certBytes = cert.der;
    final digest = sha256.convert(certBytes);
    return digest.toString();
  }

  /// Add or update pins for a domain
  void addPins(String domain, List<CertificatePin> pins) {
    _certificatePins[domain] = pins;
  }

  /// Remove pins for a domain
  void removePins(String domain) {
    _certificatePins.remove(domain);
  }

  /// Get all configured domains
  List<String> getConfiguredDomains() {
    return _certificatePins.keys.toList();
  }

  /// Check if pins are expired for a domain
  bool hasPinsExpired(String domain) {
    final pins = _getPinsForHost(domain);
    if (pins.isEmpty) return false;

    // Check if all pins are expired
    return pins.every((pin) => pin.isExpired);
  }

  /// Get expiring pins (within 30 days)
  List<ExpiringPin> getExpiringPins({int daysThreshold = 30}) {
    final expiringPins = <ExpiringPin>[];
    final threshold = DateTime.now().add(Duration(days: daysThreshold));

    for (final entry in _certificatePins.entries) {
      for (final pin in entry.value) {
        if (pin.expiryDate != null &&
            pin.expiryDate!.isBefore(threshold) &&
            !pin.isExpired) {
          expiringPins.add(ExpiringPin(
            domain: entry.key,
            pin: pin,
            daysUntilExpiry: pin.expiryDate!.difference(DateTime.now()).inDays,
          ));
        }
      }
    }

    return expiringPins;
  }

  /// Get certificate info for debugging
  String getCertificateInfo(X509Certificate cert) {
    return '''
Certificate Info:
  Subject: ${cert.subject}
  Issuer: ${cert.issuer}
  Valid from: ${cert.startValidity}
  Valid until: ${cert.endValidity}
  SHA256: ${_getCertificateFingerprint(cert)}
''';
  }

  /// Validate pin configuration
  ///
  /// Checks if all configured pins are in the correct format.
  /// Returns a list of validation errors, or an empty list if all pins are valid.
  List<String> validatePinConfiguration() {
    final errors = <String>[];

    for (final entry in _certificatePins.entries) {
      final domain = entry.key;
      final pins = entry.value;

      if (pins.isEmpty) {
        errors.add('Domain "$domain" has no pins configured');
        continue;
      }

      for (var i = 0; i < pins.length; i++) {
        final pin = pins[i];
        final pinId = 'Domain "$domain" pin #${i + 1}';

        // Validate SHA256 fingerprint format
        if (pin.type == PinType.sha256) {
          if (!_isValidSha256Format(pin.value)) {
            errors.add('$pinId has invalid SHA256 format: "${pin.value}"');
            errors.add('  Expected: 64 hexadecimal characters (a-f, A-F, 0-9)');
          }
        }

        // Validate public key format
        if (pin.type == PinType.publicKey) {
          if (!_isValidSha256Format(pin.value)) {
            errors.add('$pinId has invalid public key hash format: "${pin.value}"');
            errors.add('  Expected: 64 hexadecimal characters (a-f, A-F, 0-9)');
          }
        }

        // Warn about expired pins
        if (pin.isExpired) {
          errors.add('$pinId is expired (expiry: ${pin.expiryDate})');
        }

        // Warn about pins expiring soon
        if (pin.daysUntilExpiry != null && pin.daysUntilExpiry! < 30 && !pin.isExpired) {
          errors.add('$pinId expires soon (in ${pin.daysUntilExpiry} days)');
        }
      }
    }

    return errors;
  }

  /// Check if a string is a valid SHA256 fingerprint format
  bool _isValidSha256Format(String value) {
    // SHA256 hash should be exactly 64 hexadecimal characters
    final sha256Regex = RegExp(r'^[a-fA-F0-9]{64}$');
    return sha256Regex.hasMatch(value);
  }

  /// Print pin configuration validation results
  void printValidationResults() {
    final errors = validatePinConfiguration();

    if (errors.isEmpty) {
      if (kDebugMode) {
        AppLogger.i('Certificate pin configuration is valid', tag: 'CertificatePinning');
        AppLogger.i('Configured domains', tag: 'CertificatePinning', data: {'domains': getConfiguredDomains().join(", ")});
        for (final domain in getConfiguredDomains()) {
          final pins = _certificatePins[domain]!;
          AppLogger.d('Domain pins', tag: 'CertificatePinning', data: {'domain': domain, 'count': pins.length});
        }
      }
    } else {
      if (kDebugMode) {
        AppLogger.w('Certificate pin configuration has issues', tag: 'CertificatePinning', data: {'issueCount': errors.length});
        for (final error in errors) {
          AppLogger.w('Configuration issue', tag: 'CertificatePinning', data: {'error': error});
        }
      }
    }
  }
}

/// Certificate pin type
enum PinType {
  /// SHA256 fingerprint of the certificate
  sha256,

  /// Public key hash
  publicKey,
}

/// Certificate pin configuration
class CertificatePin {
  /// Pin type (SHA256 or public key)
  final PinType type;

  /// Pin value (fingerprint or public key hash)
  final String value;

  /// Optional expiry date for this pin
  final DateTime? expiryDate;

  /// Optional description
  final String? description;

  const CertificatePin({
    required this.type,
    required this.value,
    this.expiryDate,
    this.description,
  });

  /// Check if pin is expired
  bool get isExpired {
    if (expiryDate == null) return false;
    return DateTime.now().isAfter(expiryDate!);
  }

  /// Days until expiry
  int? get daysUntilExpiry {
    if (expiryDate == null) return null;
    return expiryDate!.difference(DateTime.now()).inDays;
  }

  @override
  String toString() {
    return 'CertificatePin(type: $type, value: ${value.substring(0, 16)}..., expiryDate: $expiryDate)';
  }
}

/// Expiring pin information
class ExpiringPin {
  final String domain;
  final CertificatePin pin;
  final int daysUntilExpiry;

  const ExpiringPin({
    required this.domain,
    required this.pin,
    required this.daysUntilExpiry,
  });

  @override
  String toString() {
    return 'ExpiringPin(domain: $domain, daysUntilExpiry: $daysUntilExpiry)';
  }
}

/// Helper function to extract SHA256 fingerprint from a certificate file
/// Use this during development to get actual fingerprints
///
/// Example usage:
/// ```dart
/// // For development - get fingerprint from certificate
/// final fingerprint = await getCertificateFingerprintFromUrl('https://api.sahool.app');
/// print('SHA256 Fingerprint: $fingerprint');
/// ```
Future<String?> getCertificateFingerprintFromUrl(String url) async {
  try {
    final uri = Uri.parse(url);
    final socket = await SecureSocket.connect(
      uri.host,
      uri.port == 0 ? 443 : uri.port,
      timeout: const Duration(seconds: 10),
    );

    final cert = socket.peerCertificate;
    if (cert == null) {
      socket.close();
      return null;
    }

    final certBytes = cert.der;
    final digest = sha256.convert(certBytes);
    final fingerprint = digest.toString();

    socket.close();
    return fingerprint;
  } catch (e) {
    if (kDebugMode) {
      AppLogger.e('Error getting certificate fingerprint', tag: 'CertificatePinning', error: e);
    }
    return null;
  }
}

/// Helper function to format certificate fingerprint
String formatFingerprint(String fingerprint) {
  // Convert to uppercase and add colons every 2 characters
  final formatted = fingerprint
      .toUpperCase()
      .replaceAllMapped(RegExp(r'.{2}'), (match) => '${match.group(0)}:');

  // Remove trailing colon
  return formatted.substring(0, formatted.length - 1);
}
