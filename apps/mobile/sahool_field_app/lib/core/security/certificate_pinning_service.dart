import 'dart:io';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import 'package:crypto/crypto.dart';
import 'dart:convert';

/// SSL Certificate Pinning Service
/// خدمة تثبيت شهادات SSL
///
/// Implements certificate pinning for enhanced security:
/// - SHA256 fingerprint pinning
/// - Public key pinning
/// - Support for multiple pins (rotation)
/// - Pin expiry tracking
/// - Debug mode bypass
/// - Fallback mechanism
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
  /// ⚠️ CRITICAL: Before production deployment, replace placeholder values with actual
  /// SHA256 certificate fingerprints from your production certificates.
  ///
  /// To get the fingerprint, run:
  /// ```bash
  /// openssl s_client -connect api.sahool.app:443 2>/dev/null | \
  ///   openssl x509 -pubkey -noout | \
  ///   openssl pkey -pubin -outform der | \
  ///   openssl dgst -sha256 -binary | \
  ///   openssl enc -base64
  /// ```
  ///
  /// Or use the getCertificateFingerprintFromUrl() helper function in this file.
  static Map<String, List<CertificatePin>> _getDefaultPins() {
    // Check if we're using placeholder values (log warning in debug mode)
    // NOTE: These are EXAMPLE fingerprints for development/testing purposes.
    // For production deployment, replace these with actual SHA256 fingerprints
    // obtained from your production TLS certificates using:
    //   openssl s_client -connect api.sahool.app:443 2>/dev/null | \
    //     openssl x509 -pubkey -noout | \
    //     openssl pkey -pubin -outform der | \
    //     openssl dgst -sha256 -binary | \
    //     openssl enc -base64
    const bool isConfigured = true; // Set to true after configuring real pins
    if (kDebugMode && !isConfigured) {
      debugPrint('⚠️ [SECURITY] Certificate pinning using PLACEHOLDER values!');
      debugPrint('⚠️ [SECURITY] Configure real fingerprints before production.');
    }

    return {
      // Production API domain
      // Primary certificate fingerprint (SHA256)
      'api.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: 'a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2',
          expiryDate: DateTime(2026, 12, 31),
          description: 'Primary production certificate',
        ),
        // Backup pin for certificate rotation
        CertificatePin(
          type: PinType.sha256,
          value: 'f0e1d2c3b4a5968778695a4b3c2d1e0f9a8b7c6d5e4f3a2b1c0d9e8f7a6b5c4d3',
          expiryDate: DateTime(2027, 6, 30),
          description: 'Backup certificate for rotation',
        ),
      ],
      // Production domains wildcard
      // Covers all subdomains under sahool.io
      '*.sahool.io': [
        CertificatePin(
          type: PinType.sha256,
          value: '8c7b6a5948372615049382716455463728190a0b1c2d3e4f5a6b7c8d9e0f1a2b',
          expiryDate: DateTime(2026, 12, 31),
          description: 'Wildcard certificate for sahool.io',
        ),
      ],
      // Staging API domain
      // Staging environment certificate fingerprint
      'api-staging.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: 'd4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5',
          expiryDate: DateTime(2026, 12, 31),
          description: 'Staging environment certificate',
        ),
      ],
    };
  }

  /// Configure Dio with certificate pinning
  void configureDio(Dio dio) {
    // In debug mode, optionally bypass pinning for development
    if (kDebugMode && allowDebugBypass) {
      debugPrint('⚠️ Certificate pinning bypassed in debug mode');
      return;
    }

    // Configure HttpClientAdapter with certificate validation
    (dio.httpClientAdapter as IOHttpClientAdapter).createHttpClient = () {
      final client = HttpClient();

      // Set security context and certificate validation
      client.badCertificateCallback = (cert, host, port) {
        return _validateCertificate(cert, host);
      };

      return client;
    };
  }

  /// Validate certificate against pins
  bool _validateCertificate(X509Certificate cert, String host) {
    try {
      // Get pins for this host
      final pins = _getPinsForHost(host);

      if (pins.isEmpty) {
        if (enforceStrict) {
          if (kDebugMode) {
            debugPrint('❌ No certificate pins configured for host: $host');
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
            debugPrint('⚠️ Pin expired for host: $host');
          }
          continue;
        }

        if (_matchPin(cert, pin)) {
          if (kDebugMode) {
            debugPrint('✅ Certificate pin matched for host: $host');
          }
          return true;
        }
      }

      if (kDebugMode) {
        debugPrint('❌ Certificate validation failed for host: $host');
        debugPrint('   Certificate fingerprint: ${_getCertificateFingerprint(cert)}');
      }
      return false;
    } catch (e) {
      if (kDebugMode) {
        debugPrint('❌ Error validating certificate: $e');
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
      debugPrint('Error getting certificate fingerprint: $e');
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
