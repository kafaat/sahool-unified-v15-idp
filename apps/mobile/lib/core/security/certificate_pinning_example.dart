import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'certificate_pinning_service.dart';
import 'certificate_config.dart';
import 'security_config.dart';

/// Example: How to use Certificate Pinning in your app
///
/// This file demonstrates different ways to configure and use
/// the certificate pinning service.

// ═══════════════════════════════════════════════════════════════════════════
// Example 1: Basic Usage with Auto Configuration
// ═══════════════════════════════════════════════════════════════════════════

void example1_basicUsage() {
  // The simplest way - automatically uses production config in release mode
  final dio = Dio();

  // Security config is automatically determined by build mode
  final securityConfig = SecurityConfig.fromBuildMode();

  if (securityConfig.enableCertificatePinning) {
    final pinningService = CertificatePinningService(
      certificatePins: CertificateConfig.getProductionPins(),
      allowDebugBypass: securityConfig.allowPinningDebugBypass,
      enforceStrict: securityConfig.strictCertificatePinning,
    );

    pinningService.configureDio(dio);

    if (kDebugMode) {
      print('✅ Certificate pinning configured');
    }
  }

  // Use dio for API calls as normal
  // dio.get('https://api.sahool.app/api/v1/fields');
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 2: Manual Configuration for Specific Environment
// ═══════════════════════════════════════════════════════════════════════════

void example2_manualConfiguration() {
  final dio = Dio();

  // Manually specify environment
  const environment = 'production'; // or 'staging', 'development'

  final pins = CertificateConfig.getPinsForEnvironment(environment);
  final securityConfig = SecurityConfig.forEnvironment(environment);

  if (securityConfig.enableCertificatePinning) {
    final pinningService = CertificatePinningService(
      certificatePins: pins,
      allowDebugBypass: false, // Never bypass in production
      enforceStrict: true, // Always enforce strict mode
    );

    pinningService.configureDio(dio);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 3: Custom Certificate Pins
// ═══════════════════════════════════════════════════════════════════════════

void example3_customPins() {
  final dio = Dio();

  // Define custom certificate pins
  final customPins = {
    'api.mycompany.com': [
      CertificatePin(
        type: PinType.sha256,
        value: 'your_sha256_fingerprint_here',
        expiryDate: DateTime(2026, 12, 31),
        description: 'Primary certificate',
      ),
      // Always include a backup pin for rotation
      CertificatePin(
        type: PinType.sha256,
        value: 'backup_sha256_fingerprint_here',
        expiryDate: DateTime(2027, 6, 30),
        description: 'Backup certificate',
      ),
    ],
  };

  final pinningService = CertificatePinningService(
    certificatePins: customPins,
    allowDebugBypass: kDebugMode, // Allow bypass only in debug mode
    enforceStrict: !kDebugMode, // Strict only in release mode
  );

  pinningService.configureDio(dio);
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 4: Checking for Expiring Certificates
// ═══════════════════════════════════════════════════════════════════════════

void example4_checkExpiringCertificates() {
  final pins = CertificateConfig.getProductionPins();

  final pinningService = CertificatePinningService(
    certificatePins: pins,
  );

  // Check for certificates expiring in the next 30 days
  final expiringPins = pinningService.getExpiringPins(daysThreshold: 30);

  if (expiringPins.isNotEmpty) {
    if (kDebugMode) {
      print('⚠️ Warning: Certificate pins expiring soon:');
      for (final pin in expiringPins) {
        print('   ${pin.domain}: ${pin.daysUntilExpiry} days until expiry');
      }
    }

    // TODO: Send notification to admin or logging service
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 5: Getting Certificate Fingerprint from Server (Debug Only)
// ═══════════════════════════════════════════════════════════════════════════

Future<void> example5_getCertificateFingerprint() async {
  if (!kDebugMode) {
    print('⚠️ This should only be run in debug mode');
    return;
  }

  // Get fingerprint from production server
  final prodFingerprint = await getCertificateFingerprintFromUrl(
    'https://api.sahool.app',
  );

  if (prodFingerprint != null) {
    print('Production API Certificate Fingerprint:');
    print(formatFingerprint(prodFingerprint));
    print('\nAdd this to certificate_config.dart:');
    print('''
    CertificatePin(
      type: PinType.sha256,
      value: '$prodFingerprint',
      expiryDate: DateTime(2026, 12, 31),
      description: 'Production certificate',
    ),
    ''');
  }

  // Get fingerprint from staging server
  final stagingFingerprint = await getCertificateFingerprintFromUrl(
    'https://api-staging.sahool.app',
  );

  if (stagingFingerprint != null) {
    print('\nStaging API Certificate Fingerprint:');
    print(formatFingerprint(stagingFingerprint));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 6: Updating Certificate Pins at Runtime
// ═══════════════════════════════════════════════════════════════════════════

void example6_runtimeUpdate() {
  final dio = Dio();
  final pinningService = CertificatePinningService();

  pinningService.configureDio(dio);

  // Later, add new pins (e.g., after downloading updated config)
  final newPins = [
    CertificatePin(
      type: PinType.sha256,
      value: 'new_certificate_fingerprint',
      expiryDate: DateTime(2027, 12, 31),
      description: 'Updated certificate',
    ),
  ];

  pinningService.addPins('api.sahool.app', newPins);

  if (kDebugMode) {
    print('✅ Certificate pins updated');
    print('Configured domains: ${pinningService.getConfiguredDomains()}');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 7: Validating Certificate Configuration
// ═══════════════════════════════════════════════════════════════════════════

void example7_validateConfiguration() {
  final pins = CertificateConfig.getProductionPins();

  // Validate the configuration
  final issues = CertificateRotationHelper.validatePinConfiguration(pins);

  if (issues.isEmpty) {
    if (kDebugMode) {
      print('✅ Certificate configuration is valid');
    }
  } else {
    if (kDebugMode) {
      print('⚠️ Certificate configuration issues:');
      for (final issue in issues) {
        print('   - $issue');
      }
    }
  }

  // Print detailed status
  if (kDebugMode) {
    final status = CertificateRotationHelper.getConfigurationStatus(pins);
    print('\n$status');
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Example 8: Integration with API Client
// ═══════════════════════════════════════════════════════════════════════════

class ExampleApiClient {
  late final Dio _dio;
  late final CertificatePinningService? _pinningService;

  ExampleApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: 'https://api.sahool.app/api/v1',
    ));

    // Configure certificate pinning
    final securityConfig = SecurityConfig.fromBuildMode();

    if (securityConfig.enableCertificatePinning) {
      final pins = CertificateConfig.getProductionPins();

      _pinningService = CertificatePinningService(
        certificatePins: pins,
        allowDebugBypass: securityConfig.allowPinningDebugBypass,
        enforceStrict: securityConfig.strictCertificatePinning,
      );

      _pinningService!.configureDio(_dio);

      if (kDebugMode) {
        print('🔒 API Client initialized with certificate pinning');
      }
    } else {
      _pinningService = null;
      if (kDebugMode) {
        print('⚠️ API Client initialized without certificate pinning');
      }
    }
  }

  Future<void> fetchData() async {
    try {
      final response = await _dio.get('/fields');
      if (kDebugMode) {
        print('✅ Data fetched successfully');
      }
    } catch (e) {
      if (kDebugMode) {
        print('❌ Error fetching data: $e');
      }
    }
  }

  bool get isPinningEnabled => _pinningService != null;
}

// ═══════════════════════════════════════════════════════════════════════════
// Usage in main.dart
// ═══════════════════════════════════════════════════════════════════════════

/*
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // In debug mode, optionally check certificate fingerprints
  if (kDebugMode) {
    await example5_getCertificateFingerprint();
  }

  // Validate certificate configuration
  example7_validateConfiguration();

  // Initialize API client with certificate pinning
  final apiClient = ExampleApiClient();

  runApp(MyApp());
}
*/
