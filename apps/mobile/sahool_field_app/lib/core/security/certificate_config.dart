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
  static Map<String, List<CertificatePin>> getProductionPins() {
    return {
      // Main Production API
      'api.sahool.app': [
        // Primary certificate (replace with actual fingerprint)
        CertificatePin(
          type: PinType.sha256,
          value: 'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA',
          expiryDate: DateTime(2026, 12, 31),
          description: 'Primary production certificate',
        ),
        // Backup certificate for rotation (replace with actual fingerprint)
        CertificatePin(
          type: PinType.sha256,
          value: 'BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB',
          expiryDate: DateTime(2027, 6, 30),
          description: 'Backup production certificate',
        ),
      ],

      // WebSocket production
      'ws.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: 'CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC',
          expiryDate: DateTime(2026, 12, 31),
          description: 'WebSocket production certificate',
        ),
      ],

      // Wildcard for *.sahool.io domains
      '*.sahool.io': [
        CertificatePin(
          type: PinType.sha256,
          value: 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD',
          expiryDate: DateTime(2026, 12, 31),
          description: 'Wildcard sahool.io certificate',
        ),
      ],
    };
  }

  /// Get staging certificate pins
  static Map<String, List<CertificatePin>> getStagingPins() {
    return {
      'api-staging.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: 'EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE',
          expiryDate: DateTime(2026, 6, 30),
          description: 'Staging API certificate',
        ),
      ],
      'ws-staging.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: 'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF',
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
