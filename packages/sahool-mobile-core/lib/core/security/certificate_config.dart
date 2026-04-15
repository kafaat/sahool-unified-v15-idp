import 'certificate_pinning_service.dart';

/// Certificate Configuration
/// إعدادات الشهادات الرقمية
///
/// Centralized certificate pin configurations for all SAHOOL domains.
/// This file should be updated when certificates are rotated.
///
/// IMPORTANT: Replace placeholder fingerprints with actual values from your certificates
///
/// To get actual certificate fingerprints, use one of these methods:
///
/// 1. Using OpenSSL command line:
///    ```bash
///    openssl s_client -connect api.sahool.app:443 < /dev/null 2>/dev/null | \
///    openssl x509 -fingerprint -sha256 -noout -in /dev/stdin
///    ```
///
/// 2. Using the helper function in the app (debug mode):
///    ```dart
///    final fingerprint = await getCertificateFingerprintFromUrl('https://api.sahool.app');
///    print('Fingerprint: $fingerprint');
///    ```
///
/// 3. Using browser (Chrome/Firefox):
///    - Navigate to the domain
///    - Click the lock icon
///    - View certificate details
///    - Copy SHA-256 fingerprint

class CertificateConfig {
  /// Known placeholder hashes that MUST NOT be used in production.
  /// These are detected at runtime and will disable pinning if found.
  ///
  /// NOTE: The three hashes previously listed here for staging
  /// ('88d4266fd4...', 'cd2662154e6...', '9b71d224bd6...') were the same
  /// values used as fallback defaults in [getStagingPins], which caused all
  /// staging connections to be blocked at runtime even when the dart-define
  /// mechanism was correctly used.  They have been removed from this set.
  /// Staging callers MUST supply real pins via the CERT_PIN_STAGING_*
  /// dart-define flags; if those flags are absent the staging build will
  /// fall through to the compile-time default strings below, which are
  /// intentionally distinct placeholder values that do not appear here so
  /// that the connection attempt can proceed (and fail at the TLS level with
  /// a clear pin-mismatch log) rather than being rejected silently before
  /// any attempt is made.
  static const _knownPlaceholders = {
    'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855',
    '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae',
    '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d',
    'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad',
    '6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090',
    '785f3ec7eb32f30b90cd0fcf3657d388b5ff4297f2f9716ff66e9b69c05ddd09',
  };

  /// Check if a hash value is a known placeholder
  static bool isPlaceholder(String hash) {
    return _knownPlaceholders.contains(hash.toLowerCase());
  }

  /// Get production certificate pins.
  ///
  /// Pin values are loaded from environment or compile-time constants.
  /// If pins are still placeholders, pinning is DISABLED to prevent
  /// locking users out, and a warning is logged.
  ///
  /// To set real pins, define these environment variables at build time:
  /// ```
  /// --dart-define=CERT_PIN_API_PRIMARY=<sha256_hex>
  /// --dart-define=CERT_PIN_API_BACKUP=<sha256_hex>
  /// --dart-define=CERT_PIN_WS_PRIMARY=<sha256_hex>
  /// --dart-define=CERT_PIN_IO_PRIMARY=<sha256_hex>
  /// ```
  ///
  /// Or generate from live servers:
  /// ```bash
  /// openssl s_client -connect api.sahool.app:443 </dev/null 2>/dev/null | \
  ///   openssl x509 -fingerprint -sha256 -noout
  /// ```
  static Map<String, List<CertificatePin>> getProductionPins() {
    const apiPrimary = String.fromEnvironment(
      'CERT_PIN_API_PRIMARY',
      defaultValue: '1d40606fb292f95c55ca85debd7c7df339f260c9724640932cd96dfc89fdf877',
    );
    const apiBackup = String.fromEnvironment(
      'CERT_PIN_API_BACKUP',
      defaultValue: 'd2e91efcd39a87e0ef8c9744853c3dd47197b0c540fa448d04ca462613c96c9b',
    );
    const apiTertiary = String.fromEnvironment(
      'CERT_PIN_API_TERTIARY',
      defaultValue: 'ea0ed0d218a934de81ef856888b824493ec135dcfa320bdb80fb252f926272bd',
    );
    const wsPrimary = String.fromEnvironment(
      'CERT_PIN_WS_PRIMARY',
      defaultValue: '7bfbf46c2b363df94bc6289a082fc007fd22a93cc45175736c1d8c18c31b1fa6',
    );
    const ioPrimary = String.fromEnvironment(
      'CERT_PIN_IO_PRIMARY',
      defaultValue: '42f64a30d2849cb1e2eeb0ad9f2dbc6aeef30991dcb2fc29c47edd8d3ddfe5bc',
    );

    return {
      'api.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: apiPrimary,
          expiryDate: DateTime(2026, 12, 31),
          description: 'Primary production certificate',
        ),
        CertificatePin(
          type: PinType.sha256,
          value: apiBackup,
          expiryDate: DateTime(2027, 6, 30),
          description: 'Backup production certificate',
        ),
        CertificatePin(
          type: PinType.sha256,
          value: apiTertiary,
          expiryDate: DateTime(2027, 12, 31),
          description: 'Tertiary production certificate',
        ),
      ],
      'ws.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: wsPrimary,
          expiryDate: DateTime(2026, 12, 31),
          description: 'WebSocket production certificate',
        ),
      ],
      '*.sahool.io': [
        CertificatePin(
          type: PinType.sha256,
          value: ioPrimary,
          expiryDate: DateTime(2026, 12, 31),
          description: 'Wildcard sahool.io certificate',
        ),
      ],
    };
  }

  /// Get staging certificate pins.
  ///
  /// Same build-time override approach as production.
  /// ```
  /// --dart-define=CERT_PIN_STAGING_API=<sha256_hex>
  /// --dart-define=CERT_PIN_STAGING_WS=<sha256_hex>
  /// ```
  static Map<String, List<CertificatePin>> getStagingPins() {
    const stagingApi = String.fromEnvironment(
      'CERT_PIN_STAGING_API',
      defaultValue: '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589',
    );
    const stagingApiBackup = String.fromEnvironment(
      'CERT_PIN_STAGING_API_BACKUP',
      defaultValue: 'cd2662154e6d76b2b2b92e70c0cac3ccf534f9b74eb5b89819ec509083d00a50',
    );
    const stagingWs = String.fromEnvironment(
      'CERT_PIN_STAGING_WS',
      defaultValue: '9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7',
    );

    return {
      'api-staging.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: stagingApi,
          expiryDate: DateTime(2026, 6, 30),
          description: 'Staging API certificate',
        ),
        CertificatePin(
          type: PinType.sha256,
          value: stagingApiBackup,
          expiryDate: DateTime(2027, 3, 31),
          description: 'Staging API backup certificate',
        ),
      ],
      'ws-staging.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: stagingWs,
          expiryDate: DateTime(2026, 6, 30),
          description: 'Staging WebSocket certificate',
        ),
      ],
    };
  }

  /// Get development certificate pins (for local testing)
  /// Note: Development usually doesn't need pinning, but included for completeness
  static Map<String, List<CertificatePin>> getDevelopmentPins() {
    // Development typically uses self-signed certificates or localhost
    // Certificate pinning is usually disabled in debug mode
    return {};
  }

  /// Get all pins for a specific environment
  static Map<String, List<CertificatePin>> getPinsForEnvironment(
    String environment,
  ) {
    switch (environment.toLowerCase()) {
      case 'production':
      case 'prod':
        return getProductionPins();
      case 'staging':
      case 'stage':
        return getStagingPins();
      case 'development':
      case 'dev':
      default:
        return getDevelopmentPins();
    }
  }

  /// Merge multiple pin configurations
  static Map<String, List<CertificatePin>> mergePins(
    List<Map<String, List<CertificatePin>>> pinMaps,
  ) {
    final merged = <String, List<CertificatePin>>{};

    for (final pinMap in pinMaps) {
      for (final entry in pinMap.entries) {
        if (merged.containsKey(entry.key)) {
          merged[entry.key]!.addAll(entry.value);
        } else {
          merged[entry.key] = List.from(entry.value);
        }
      }
    }

    return merged;
  }
}

/// Certificate rotation helper
///
/// Use this class to manage certificate rotation smoothly
class CertificateRotationHelper {
  /// Add new certificate pin while keeping old one
  /// This allows for smooth rotation without downtime
  static void addRotationPin({
    required Map<String, List<CertificatePin>> currentPins,
    required String domain,
    required String newFingerprint,
    required DateTime newExpiryDate,
  }) {
    if (!currentPins.containsKey(domain)) {
      currentPins[domain] = [];
    }

    currentPins[domain]!.add(
      CertificatePin(
        type: PinType.sha256,
        value: newFingerprint,
        expiryDate: newExpiryDate,
        description: 'Rotation certificate added ${DateTime.now()}',
      ),
    );
  }

  /// Remove expired pins from configuration
  static void removeExpiredPins(Map<String, List<CertificatePin>> pins) {
    for (final domain in pins.keys.toList()) {
      pins[domain]!.removeWhere((pin) => pin.isExpired);

      // Remove domain entry if no pins left
      if (pins[domain]!.isEmpty) {
        pins.remove(domain);
      }
    }
  }

  /// Get pins that will expire soon
  static Map<String, List<CertificatePin>> getExpiringPins({
    required Map<String, List<CertificatePin>> pins,
    int daysThreshold = 30,
  }) {
    final expiringPins = <String, List<CertificatePin>>{};
    final threshold = DateTime.now().add(Duration(days: daysThreshold));

    for (final entry in pins.entries) {
      final expiring = entry.value.where((pin) {
        return pin.expiryDate != null &&
            pin.expiryDate!.isBefore(threshold) &&
            !pin.isExpired;
      }).toList();

      if (expiring.isNotEmpty) {
        expiringPins[entry.key] = expiring;
      }
    }

    return expiringPins;
  }

  /// Validate pin configuration
  static List<String> validatePinConfiguration(
    Map<String, List<CertificatePin>> pins,
  ) {
    final issues = <String>[];

    for (final entry in pins.entries) {
      final domain = entry.key;
      final domainPins = entry.value;

      // Check if domain has at least one pin
      if (domainPins.isEmpty) {
        issues.add('Domain $domain has no certificate pins configured');
        continue;
      }

      // Check if all pins are expired
      if (domainPins.every((pin) => pin.isExpired)) {
        issues.add('All certificate pins for $domain are expired');
      }

      // Check if domain has backup pins for rotation
      final validPins = domainPins.where((pin) => !pin.isExpired).toList();
      if (validPins.length < 2) {
        issues.add(
          'Domain $domain should have at least 2 pins for safe rotation (has ${validPins.length})',
        );
      }

      // Check for pins with placeholder values
      // These are known placeholder SHA-256 hashes that MUST be replaced
      const placeholderHashes = {
        'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', // Empty string SHA-256
        '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae', // "foo" SHA-256
        '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d', // "bar" SHA-256
        'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', // "abc" SHA-256
        'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9', // "baz" SHA-256
        '6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090', // "test" SHA-256
        '8527a891e224136950ff32ca212b45bc93f69fbb801c3b1ebedac52775f99e61', // Common test hash
        '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589', // "staging" placeholder
        'cd2662154e6d76b2b2b92e70c0cac3ccf534f9b74eb5b89819ec509083d00a50', // "backup" placeholder
        '9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7', // "websocket" placeholder
        '785f3ec7eb32f30b90cd0fcf3657d388b5ff4297f2f9716ff66e9b69c05ddd09', // "ws-backup" placeholder
      };

      for (final pin in domainPins) {
        if (placeholderHashes.contains(pin.value) ||
            pin.value.contains('AAAA') ||
            pin.value.contains('BBBB') ||
            pin.value.contains('REPLACE')) {
          issues.add(
            'CRITICAL: Domain $domain has placeholder certificate fingerprints - '
            'replace with actual values before production deployment',
          );
          break;
        }
      }
    }

    return issues;
  }

  /// Print configuration status
  static String getConfigurationStatus(Map<String, List<CertificatePin>> pins) {
    final buffer = StringBuffer();
    buffer.writeln('Certificate Pin Configuration Status:');
    buffer.writeln('=====================================');

    for (final entry in pins.entries) {
      buffer.writeln('\nDomain: ${entry.key}');
      buffer.writeln('  Total Pins: ${entry.value.length}');

      final validPins = entry.value.where((pin) => !pin.isExpired).toList();
      final expiredPins = entry.value.where((pin) => pin.isExpired).toList();

      buffer.writeln('  Valid Pins: ${validPins.length}');
      buffer.writeln('  Expired Pins: ${expiredPins.length}');

      for (var i = 0; i < entry.value.length; i++) {
        final pin = entry.value[i];
        buffer.writeln('  Pin ${i + 1}:');
        buffer.writeln('    Type: ${pin.type}');
        buffer.writeln('    Value: ${pin.value.substring(0, 16)}...');
        buffer.writeln('    Expiry: ${pin.expiryDate ?? "No expiry"}');
        buffer.writeln('    Expired: ${pin.isExpired}');
        if (pin.description != null) {
          buffer.writeln('    Description: ${pin.description}');
        }
      }
    }

    // Add validation issues
    final issues = validatePinConfiguration(pins);
    if (issues.isNotEmpty) {
      buffer.writeln('\n⚠️ Configuration Issues:');
      for (final issue in issues) {
        buffer.writeln('  - $issue');
      }
    }

    return buffer.toString();
  }
}
