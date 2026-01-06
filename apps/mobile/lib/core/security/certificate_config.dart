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
  /// Get production certificate pins
  ///
  /// ============================================
  /// CRITICAL WARNING - PLACEHOLDER VALUES
  /// ============================================
  /// The SHA-256 fingerprints below are PLACEHOLDER EXAMPLES only.
  /// You MUST replace these with actual production certificate fingerprints
  /// before deploying to production.
  ///
  /// ⚠️  DO NOT DEPLOY TO PRODUCTION WITHOUT UPDATING THESE VALUES  ⚠️
  ///
  /// To generate actual certificate pins:
  /// 1. Run the script: ./scripts/generate_cert_pins.sh api.sahool.app
  /// 2. Copy the SHA256 fingerprint from the script output
  /// 3. Replace the placeholder values below
  ///
  /// Use the getCertificateFingerprintFromUrl() helper function or OpenSSL
  /// to obtain the real fingerprints from your production servers.
  static Map<String, List<CertificatePin>> getProductionPins() {
    return {
      // Main Production API
      'api.sahool.app': [
        // Primary certificate
        // TODO: CRITICAL - Replace with actual production certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh api.sahool.app
        CertificatePin(
          type: PinType.sha256,
          value: 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 12, 31),
          description: 'Primary production certificate',
        ),
        // Backup certificate for rotation
        // TODO: CRITICAL - Replace with actual backup certificate fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: '2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 6, 30),
          description: 'Backup production certificate',
        ),
        // Additional backup for seamless rotation
        // TODO: CRITICAL - Replace with actual tertiary certificate fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: '3e23e8160039594a33894f6564e1b1348bbd7a0088d42c4acb73eeaed59c009d', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 12, 31),
          description: 'Tertiary production certificate',
        ),
      ],

      // WebSocket production
      'ws.sahool.app': [
        // TODO: CRITICAL - Replace with actual WebSocket certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh ws.sahool.app
        CertificatePin(
          type: PinType.sha256,
          value: 'ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 12, 31),
          description: 'WebSocket production certificate',
        ),
        // Backup for WebSocket
        // TODO: CRITICAL - Replace with actual backup WebSocket fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: 'fcde2b2edba56bf408601fb721fe9b5c338d10ee429ea04fae5511b68fbf8fb9', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 6, 30),
          description: 'WebSocket backup certificate',
        ),
      ],

      // Wildcard for *.sahool.io domains
      '*.sahool.io': [
        // TODO: CRITICAL - Replace with actual wildcard certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh api.sahool.io
        CertificatePin(
          type: PinType.sha256,
          value: '6ca13d52ca70c883e0f0bb101e425a89e8624de51db2d2392593af6a84118090', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 12, 31),
          description: 'Wildcard sahool.io certificate',
        ),
        // Backup for wildcard
        // TODO: CRITICAL - Replace with actual backup wildcard fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: '8527a891e224136950ff32ca212b45bc93f69fbb801c3b1ebedac52775f99e61', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 6, 30),
          description: 'Wildcard backup certificate',
        ),
      ],
    };
  }

  /// Get staging certificate pins
  ///
  /// ============================================
  /// CRITICAL WARNING - PLACEHOLDER VALUES
  /// ============================================
  /// The SHA-256 fingerprints below are PLACEHOLDER EXAMPLES only.
  /// Replace these with actual staging certificate fingerprints.
  ///
  /// ⚠️  DO NOT DEPLOY TO STAGING WITHOUT UPDATING THESE VALUES  ⚠️
  ///
  /// To generate actual certificate pins:
  /// 1. Run the script: ./scripts/generate_cert_pins.sh api-staging.sahool.app
  /// 2. Copy the SHA256 fingerprint from the script output
  /// 3. Replace the placeholder values below
  static Map<String, List<CertificatePin>> getStagingPins() {
    return {
      'api-staging.sahool.app': [
        // TODO: CRITICAL - Replace with actual staging API certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh api-staging.sahool.app
        CertificatePin(
          type: PinType.sha256,
          value: '88d4266fd4e6338d13b845fcf289579d209c897823b9217da3e161936f031589', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 6, 30),
          description: 'Staging API certificate',
        ),
        // Staging backup
        // TODO: CRITICAL - Replace with actual staging backup fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: 'cd2662154e6d76b2b2b92e70c0cac3ccf534f9b74eb5b89819ec509083d00a50', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 3, 31),
          description: 'Staging API backup certificate',
        ),
      ],
      'ws-staging.sahool.app': [
        // TODO: CRITICAL - Replace with actual staging WebSocket certificate fingerprint
        // Generate using: ./scripts/generate_cert_pins.sh ws-staging.sahool.app
        CertificatePin(
          type: PinType.sha256,
          value: '9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca7', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2026, 6, 30),
          description: 'Staging WebSocket certificate',
        ),
        // Staging WebSocket backup
        // TODO: CRITICAL - Replace with actual staging WebSocket backup fingerprint
        CertificatePin(
          type: PinType.sha256,
          value: '785f3ec7eb32f30b90cd0fcf3657d388b5ff4297f2f9716ff66e9b69c05ddd09', // PLACEHOLDER - MUST REPLACE
          expiryDate: DateTime(2027, 3, 31),
          description: 'Staging WebSocket backup certificate',
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
      for (final pin in domainPins) {
        if (pin.value.contains('AAAA') ||
            pin.value.contains('BBBB') ||
            pin.value.contains('REPLACE')) {
          issues.add(
            'Domain $domain has placeholder certificate fingerprints - replace with actual values',
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
