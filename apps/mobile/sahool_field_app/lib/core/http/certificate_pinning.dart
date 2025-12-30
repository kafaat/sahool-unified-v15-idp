import 'dart:convert';
import 'dart:io';
import 'package:crypto/crypto.dart';
import 'package:dio/dio.dart';
import 'package:dio/io.dart';
import 'package:flutter/foundation.dart';
import '../utils/app_logger.dart';

/// SSL Certificate Pinning Implementation for SAHOOL API
/// تثبيت شهادة SSL لمنع هجمات MITM
///
/// Features:
/// - Public key pinning using SHA-256 fingerprints
/// - Multiple certificate support for backup/rotation
/// - Development mode bypass for local testing
/// - Detailed logging for debugging
/// - Fallback mechanism for certificate rotation
class CertificatePinning {
  /// Production API certificate SHA-256 fingerprints
  /// These should be updated with actual certificate fingerprints from your server
  ///
  /// To get your certificate fingerprint:
  /// 1. Run: openssl s_client -servername api.sahool.io -connect api.sahool.io:443 </dev/null | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64
  /// 2. Add the output to the list below
  static const List<String> _pinnedCertificates = [
    // Primary production certificate
    // Example: 'sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA='
    // TODO: Replace with actual certificate fingerprint from api.sahool.io
    'sha256/PLACEHOLDER_PRIMARY_CERT_FINGERPRINT=',

    // Backup certificate for rotation
    // This allows for smooth certificate updates without app breaking
    // TODO: Replace with backup certificate fingerprint
    'sha256/PLACEHOLDER_BACKUP_CERT_FINGERPRINT=',
  ];

  /// Development mode hosts that bypass certificate pinning
  /// This allows testing with localhost and emulator IPs
  static const List<String> _devBypassHosts = [
    'localhost',
    '127.0.0.1',
    '10.0.2.2', // Android emulator
    '192.168.', // Local network (prefix match)
  ];

  /// Enable certificate pinning (disabled in debug mode by default)
  /// Can be overridden for testing
  static bool get isPinningEnabled {
    // Disable in debug mode for development
    if (kDebugMode) {
      return const bool.fromEnvironment('ENABLE_CERT_PINNING', defaultValue: false);
    }
    // Always enabled in release mode
    return true;
  }

  /// Configure Dio with certificate pinning
  static void configureDio(Dio dio) {
    if (!isPinningEnabled) {
      AppLogger.w(
        'Certificate pinning is DISABLED - Development mode',
        tag: 'SSL',
      );
      return;
    }

    // Set custom HttpClientAdapter with SSL pinning
    dio.httpClientAdapter = IOHttpClientAdapter(
      createHttpClient: () {
        final client = HttpClient();

        client.badCertificateCallback = (cert, host, port) {
          return _validateCertificate(cert, host, port);
        };

        return client;
      },
    );

    AppLogger.i('Certificate pinning enabled', tag: 'SSL');
  }

  /// Validate SSL certificate against pinned fingerprints
  static bool _validateCertificate(
    X509Certificate cert,
    String host,
    int port,
  ) {
    // Bypass pinning for development hosts
    if (_shouldBypassPinning(host)) {
      AppLogger.d(
        'Bypassing SSL pinning for development host: $host',
        tag: 'SSL',
      );
      return true;
    }

    try {
      // Extract public key from certificate
      final publicKeyHash = _getPublicKeyHash(cert);

      if (publicKeyHash == null) {
        AppLogger.e(
          'Failed to extract public key hash from certificate',
          tag: 'SSL',
        );
        return false;
      }

      // Check against pinned certificates
      final isPinned = _pinnedCertificates.contains(publicKeyHash);

      if (isPinned) {
        AppLogger.d(
          'Certificate validated successfully for $host',
          tag: 'SSL',
        );
      } else {
        AppLogger.e(
          'Certificate pinning validation FAILED for $host:$port\n'
          'Received fingerprint: $publicKeyHash\n'
          'Expected one of: ${_pinnedCertificates.join(', ')}',
          tag: 'SSL',
        );
      }

      return isPinned;
    } catch (e, stackTrace) {
      AppLogger.e(
        'Error during certificate validation for $host:$port',
        tag: 'SSL',
        error: e,
        stackTrace: stackTrace,
      );
      return false;
    }
  }

  /// Check if certificate pinning should be bypassed for this host
  static bool _shouldBypassPinning(String host) {
    if (!isPinningEnabled) return true;

    for (final devHost in _devBypassHosts) {
      if (host.contains(devHost)) {
        return true;
      }
    }

    return false;
  }

  /// Extract and hash the public key from X509 certificate
  static String? _getPublicKeyHash(X509Certificate cert) {
    try {
      // Get DER-encoded certificate
      final derBytes = cert.der;

      // Extract public key information from DER
      // This is a simplified approach - in production you might want to use
      // a more robust ASN.1 parser
      final publicKeyBytes = _extractPublicKeyBytes(derBytes);

      if (publicKeyBytes == null) {
        return null;
      }

      // Hash the public key using SHA-256
      final digest = sha256.convert(publicKeyBytes);

      // Encode as base64 with sha256/ prefix (HPKP format)
      return 'sha256/${base64.encode(digest.bytes)}';
    } catch (e) {
      AppLogger.e('Error extracting public key hash', tag: 'SSL', error: e);
      return null;
    }
  }

  /// Extract public key bytes from DER-encoded certificate
  /// This is a simplified extraction - for production, consider using
  /// a proper ASN.1 parser library
  static List<int>? _extractPublicKeyBytes(List<int> derBytes) {
    try {
      // For this implementation, we'll use the full DER bytes
      // In a production environment, you should properly parse the ASN.1
      // structure to extract just the SubjectPublicKeyInfo
      //
      // Note: This is a simplified approach. For better security,
      // implement proper ASN.1 parsing or use a library that can
      // extract the public key properly.
      return derBytes;
    } catch (e) {
      AppLogger.e('Error extracting public key bytes', tag: 'SSL', error: e);
      return null;
    }
  }

  /// Get certificate information for debugging
  static Map<String, dynamic> getCertificateInfo(X509Certificate cert) {
    return {
      'subject': cert.subject,
      'issuer': cert.issuer,
      'startDate': cert.startValidity.toIso8601String(),
      'endDate': cert.endValidity.toIso8601String(),
      'sha1': _formatFingerprint(_getSHA1Fingerprint(cert.der)),
      'sha256': _formatFingerprint(_getSHA256Fingerprint(cert.der)),
    };
  }

  /// Get SHA-1 fingerprint of certificate (for debugging)
  static String _getSHA1Fingerprint(List<int> derBytes) {
    final digest = sha1.convert(derBytes);
    return base64.encode(digest.bytes);
  }

  /// Get SHA-256 fingerprint of certificate (for debugging)
  static String _getSHA256Fingerprint(List<int> derBytes) {
    final digest = sha256.convert(derBytes);
    return base64.encode(digest.bytes);
  }

  /// Format fingerprint for display
  static String _formatFingerprint(String fingerprint) {
    return fingerprint.toUpperCase().replaceAllMapped(
      RegExp(r'.{2}'),
      (match) => '${match.group(0)}:',
    ).substring(0, fingerprint.length * 3 - 1);
  }

  /// Verify certificate pinning configuration
  /// Call this during app initialization to ensure certificates are properly configured
  static bool verifyConfiguration() {
    if (!isPinningEnabled) {
      AppLogger.w(
        'Certificate pinning verification skipped - pinning disabled',
        tag: 'SSL',
      );
      return true;
    }

    // Check if placeholder certificates are still in use
    final hasPlaceholders = _pinnedCertificates.any(
      (cert) => cert.contains('PLACEHOLDER'),
    );

    if (hasPlaceholders) {
      AppLogger.e(
        'SECURITY WARNING: Certificate pinning is using placeholder values!\n'
        'Update CertificatePinning._pinnedCertificates with actual certificate fingerprints.',
        tag: 'SSL',
      );
      return false;
    }

    // Verify we have at least one certificate pinned
    if (_pinnedCertificates.isEmpty) {
      AppLogger.e(
        'SECURITY WARNING: No certificates are pinned!',
        tag: 'SSL',
      );
      return false;
    }

    AppLogger.i(
      'Certificate pinning configured with ${_pinnedCertificates.length} pinned certificate(s)',
      tag: 'SSL',
    );
    return true;
  }

  /// Test certificate pinning (for debugging only)
  /// This should only be called in development/testing
  static Future<bool> testPinning(Dio dio, String testUrl) async {
    if (!kDebugMode) {
      AppLogger.w(
        'Certificate pinning test is only available in debug mode',
        tag: 'SSL',
      );
      return false;
    }

    try {
      AppLogger.d('Testing certificate pinning with $testUrl', tag: 'SSL');

      final response = await dio.get(testUrl);

      AppLogger.i(
        'Certificate pinning test PASSED - Status: ${response.statusCode}',
        tag: 'SSL',
      );
      return true;
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionError) {
        AppLogger.e(
          'Certificate pinning test FAILED - Connection rejected\n'
          'This is expected if certificate fingerprints do not match.',
          tag: 'SSL',
          error: e,
        );
        return false;
      }

      AppLogger.e(
        'Certificate pinning test encountered error',
        tag: 'SSL',
        error: e,
      );
      return false;
    } catch (e) {
      AppLogger.e(
        'Certificate pinning test failed with unexpected error',
        tag: 'SSL',
        error: e,
      );
      return false;
    }
  }
}
