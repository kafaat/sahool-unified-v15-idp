/// SSL Certificate Pinning - Integration Example
/// مثال على دمج تثبيت شهادات SSL
///
/// This file demonstrates how to integrate certificate pinning
/// into your SAHOOL Field App. Copy the relevant parts into your
/// actual app initialization code.

import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../http/api_client.dart';
import 'security_config.dart';
import 'certificate_pinning_service.dart';
import 'certificate_config.dart';
import 'certificate_monitor.dart';

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 1: Basic Setup
// ══════════════════════════════════════════════════════════════════════════════

/// Create ApiClient with certificate pinning enabled
ApiClient createSecureApiClient() {
  // Create security config with high security level
  final securityConfig = const SecurityConfig(level: SecurityLevel.high);

  // Create API client (certificate pinning auto-configured)
  final apiClient = ApiClient(
    securityConfig: securityConfig,
  );

  return apiClient;
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 2: Custom Certificate Configuration
// ══════════════════════════════════════════════════════════════════════════════

/// Create ApiClient with custom certificate pins
ApiClient createCustomSecureApiClient() {
  // Create custom certificate pinning service
  final pinningService = CertificatePinningService(
    certificatePins: {
      'api.sahool.app': [
        CertificatePin(
          type: PinType.sha256,
          value: 'your_actual_sha256_fingerprint_here',
          expiryDate: DateTime(2026, 12, 31),
          description: 'Production API certificate',
        ),
      ],
    },
    allowDebugBypass: kDebugMode, // Allow bypass in debug mode
    enforceStrict: true, // Strict validation
  );

  // Create API client with custom pinning service
  final apiClient = ApiClient(
    securityConfig: const SecurityConfig(level: SecurityLevel.high),
    certificatePinningService: pinningService,
  );

  return apiClient;
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 3: Environment-Based Configuration
// ══════════════════════════════════════════════════════════════════════════════

/// Create ApiClient based on environment
ApiClient createEnvironmentApiClient(String environment) {
  // Get pins for environment
  final pins = CertificateConfig.getPinsForEnvironment(environment);

  // Create pinning service
  final pinningService = CertificatePinningService(
    certificatePins: pins,
    allowDebugBypass: environment != 'production',
    enforceStrict: environment == 'production',
  );

  // Create API client
  return ApiClient(
    securityConfig: const SecurityConfig(level: SecurityLevel.high),
    certificatePinningService: pinningService,
  );
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 4: Riverpod Provider Integration
// ══════════════════════════════════════════════════════════════════════════════

/// Provider for certificate pinning service
final certificatePinningServiceProvider = Provider<CertificatePinningService?>((ref) {
  final securityConfig = ref.watch(securityConfigProvider);

  if (!securityConfig.enableCertificatePinning) {
    return null;
  }

  // Get environment (you'd determine this from your app config)
  const environment = String.fromEnvironment('ENV', defaultValue: 'development');

  return CertificatePinningService(
    certificatePins: CertificateConfig.getPinsForEnvironment(environment),
    allowDebugBypass: securityConfig.allowPinningDebugBypass,
    enforceStrict: securityConfig.strictCertificatePinning,
  );
});

/// Provider for API client with certificate pinning
final secureApiClientProvider = Provider<ApiClient>((ref) {
  final securityConfig = ref.watch(securityConfigProvider);
  final pinningService = ref.watch(certificatePinningServiceProvider);

  return ApiClient(
    securityConfig: securityConfig,
    certificatePinningService: pinningService,
  );
});

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 5: Certificate Status Monitoring
// ══════════════════════════════════════════════════════════════════════════════

/// Initialize certificate monitoring
/// Call this in your app initialization
void initializeCertificateMonitoring(ApiClient apiClient) {
  if (!kDebugMode) return;

  final statusService = CertificateStatusService(
    pinningService: apiClient.certificatePinningService,
    onExpiringPinsDetected: (pins) {
      debugPrint('⚠️ WARNING: ${pins.length} certificate(s) expiring soon!');
      for (final pin in pins) {
        debugPrint('  - ${pin.domain}: ${pin.daysUntilExpiry} days left');
      }
    },
    onValidationIssues: (issues) {
      debugPrint('❌ Certificate configuration issues:');
      for (final issue in issues) {
        debugPrint('  - $issue');
      }
    },
  );

  // Check status immediately
  statusService.checkStatus().then((status) {
    statusService.logStatus(status);
  });
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 6: Runtime Certificate Updates
// ══════════════════════════════════════════════════════════════════════════════

/// Update certificate pins at runtime
/// Useful for remote configuration or emergency updates
void updateCertificatePins(ApiClient apiClient) {
  // Add new pin for certificate rotation
  apiClient.updateCertificatePins('api.sahool.app', [
    // Keep existing pin
    CertificatePin(
      type: PinType.sha256,
      value: 'old_fingerprint',
      expiryDate: DateTime(2026, 6, 30),
    ),
    // Add new pin
    CertificatePin(
      type: PinType.sha256,
      value: 'new_fingerprint',
      expiryDate: DateTime(2027, 6, 30),
    ),
  ]);

  if (kDebugMode) {
    debugPrint('✅ Certificate pins updated for api.sahool.app');
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 7: Check Expiring Certificates
// ══════════════════════════════════════════════════════════════════════════════

/// Periodically check for expiring certificates
/// Call this daily or weekly
Future<void> checkExpiringCertificates(ApiClient apiClient) async {
  final expiringPins = apiClient.getExpiringPins(daysThreshold: 30);

  if (expiringPins.isEmpty) {
    if (kDebugMode) {
      debugPrint('✅ No certificates expiring in the next 30 days');
    }
    return;
  }

  // Log warning
  if (kDebugMode) {
    debugPrint('⚠️ ALERT: ${expiringPins.length} certificate(s) expiring soon:');
    for (final pin in expiringPins) {
      debugPrint('  - ${pin.domain}: ${pin.daysUntilExpiry} days remaining');
    }
  }

  // In production, you might want to:
  // - Send notification to admin
  // - Log to monitoring service
  // - Display in-app warning
  // - Fetch updated pins from server
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 8: Complete App Initialization
// ══════════════════════════════════════════════════════════════════════════════

/// Complete example of app initialization with certificate pinning
class SecureAppInitializer {
  static Future<void> initialize() async {
    // 1. Determine environment
    const environment = String.fromEnvironment('ENV', defaultValue: 'development');

    if (kDebugMode) {
      debugPrint('🔧 Initializing SAHOOL Field App');
      debugPrint('   Environment: $environment');
    }

    // 2. Validate certificate configuration
    final pins = CertificateConfig.getPinsForEnvironment(environment);
    final issues = CertificateRotationHelper.validatePinConfiguration(pins);

    if (issues.isNotEmpty && kDebugMode) {
      debugPrint('⚠️ Certificate configuration issues detected:');
      for (final issue in issues) {
        debugPrint('  - $issue');
      }
    }

    // 3. Create security config
    final securityConfig = environment == 'production'
        ? const SecurityConfig(level: SecurityLevel.high)
        : const SecurityConfig(level: SecurityLevel.medium);

    if (kDebugMode) {
      debugPrint('🔒 Security Configuration:');
      debugPrint('   Level: ${securityConfig.level.nameAr}');
      debugPrint('   Certificate Pinning: ${securityConfig.enableCertificatePinning}');
      debugPrint('   Strict Mode: ${securityConfig.strictCertificatePinning}');
      debugPrint('   Debug Bypass: ${securityConfig.allowPinningDebugBypass}');
    }

    // 4. Create API client (certificate pinning configured automatically)
    final apiClient = ApiClient(
      securityConfig: securityConfig,
    );

    // 5. Initialize certificate monitoring (debug only)
    if (kDebugMode) {
      initializeCertificateMonitoring(apiClient);
    }

    // 6. Schedule periodic certificate checks
    // You would use a timer or background task here
    if (environment == 'production') {
      // Check certificates daily
      // Timer.periodic(Duration(days: 1), (_) {
      //   checkExpiringCertificates(apiClient);
      // });
    }

    if (kDebugMode) {
      debugPrint('✅ App initialization complete');
    }
  }
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 9: Debug Tools Integration
// ══════════════════════════════════════════════════════════════════════════════

/// Debug helper to extract and print certificate fingerprints
/// Call this in debug mode to get actual certificates from servers
Future<void> debugExtractCertificates() async {
  if (!kDebugMode) return;

  // Import this at the top:
  // import 'certificate_tools.dart';

  debugPrint('\n╔════════════════════════════════════════════════════╗');
  debugPrint('║  Extracting Certificate Fingerprints              ║');
  debugPrint('╚════════════════════════════════════════════════════╝\n');

  // List of URLs to check
  final urls = [
    'https://api.sahool.app',
    'https://api-staging.sahool.app',
    'https://ws.sahool.app',
    'https://ws-staging.sahool.app',
  ];

  // Extract certificates (uncomment when using)
  // final results = await getCertificateInfoBatch(urls);
  // generateBulkConfiguration(results);
}

// ══════════════════════════════════════════════════════════════════════════════
// EXAMPLE 10: Testing Certificate Pinning
// ══════════════════════════════════════════════════════════════════════════════

/// Test certificate pinning functionality
Future<void> testCertificatePinning(ApiClient apiClient) async {
  if (!kDebugMode) return;

  debugPrint('\n═══ Testing Certificate Pinning ═══\n');

  // 1. Check if pinning is enabled
  if (!apiClient.isCertificatePinningEnabled) {
    debugPrint('❌ Certificate pinning is NOT enabled');
    return;
  }

  debugPrint('✅ Certificate pinning is enabled');

  // 2. Check for expiring pins
  final expiringPins = apiClient.getExpiringPins(daysThreshold: 60);
  if (expiringPins.isNotEmpty) {
    debugPrint('⚠️ Found ${expiringPins.length} expiring pin(s):');
    for (final pin in expiringPins) {
      debugPrint('  - ${pin.domain}: ${pin.daysUntilExpiry} days');
    }
  } else {
    debugPrint('✅ No pins expiring in next 60 days');
  }

  // 3. Validate configuration
  final pins = CertificateConfig.getProductionPins();
  final issues = CertificateRotationHelper.validatePinConfiguration(pins);
  if (issues.isNotEmpty) {
    debugPrint('⚠️ Configuration issues:');
    for (final issue in issues) {
      debugPrint('  - $issue');
    }
  } else {
    debugPrint('✅ Configuration is valid');
  }

  // 4. Print configuration status
  final status = CertificateRotationHelper.getConfigurationStatus(pins);
  debugPrint('\n$status');

  debugPrint('\n═══════════════════════════════════\n');
}

// ══════════════════════════════════════════════════════════════════════════════
// HOW TO USE THESE EXAMPLES
// ══════════════════════════════════════════════════════════════════════════════

/*

1. BASIC SETUP (Recommended for most cases):

   In your main app provider or initialization:

   ```dart
   final apiClient = createSecureApiClient();
   ```

2. RIVERPOD INTEGRATION:

   Add to your providers file:

   ```dart
   import 'core/security/certificate_pinning_example.dart';

   // Use the providers
   final apiClient = ref.watch(secureApiClientProvider);
   ```

3. APP INITIALIZATION:

   In your main.dart:

   ```dart
   void main() async {
     WidgetsFlutterBinding.ensureInitialized();

     // Initialize security
     await SecureAppInitializer.initialize();

     runApp(MyApp());
   }
   ```

4. CERTIFICATE MONITORING (Debug mode):

   In your debug settings screen:

   ```dart
   CertificateMonitorWidget(
     pinningService: apiClient.certificatePinningService,
   )
   ```

5. EXTRACT CERTIFICATES (First time setup):

   Create a temporary button in debug mode:

   ```dart
   ElevatedButton(
     onPressed: debugExtractCertificates,
     child: Text('Extract Certificates'),
   )
   ```

   Run the app, press the button, and copy the output to certificate_config.dart

6. PERIODIC CHECKS (Production):

   In your app lifecycle or background task:

   ```dart
   // Check daily
   Timer.periodic(Duration(days: 1), (_) {
     checkExpiringCertificates(apiClient);
   });
   ```

7. TESTING:

   In your debug menu:

   ```dart
   ElevatedButton(
     onPressed: () => testCertificatePinning(apiClient),
     child: Text('Test Certificate Pinning'),
   )
   ```

*/
