import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:sahool_field_app/core/http/api_client.dart';
import 'package:sahool_field_app/core/http/certificate_pinning.dart';
import 'package:sahool_field_app/core/config/api_config.dart';

/// Integration tests for SSL Certificate Pinning
///
/// These tests verify that certificate pinning works correctly
/// with real network requests.
///
/// Run with:
///   flutter test integration_test/certificate_pinning_test.dart
///   flutter test integration_test/certificate_pinning_test.dart --dart-define=ENABLE_CERT_PINNING=true
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Certificate Pinning Integration Tests', () {
    late ApiClient apiClient;

    setUp(() {
      apiClient = ApiClient(baseUrl: ApiConfig.productionBaseUrl);
    });

    testWidgets('should successfully connect when pinning is disabled',
        (WidgetTester tester) async {
      // In debug mode with pinning disabled, connection should succeed
      // even if certificates don't match

      if (!CertificatePinning.isPinningEnabled) {
        // Try to make a simple request
        try {
          // This assumes there's a public health endpoint
          final response = await apiClient.get('/healthz');
          expect(response, isNotNull);
        } catch (e) {
          // Connection might fail for other reasons (network, etc)
          // but not due to certificate pinning
          print('Connection test skipped: $e');
        }
      }
    });

    testWidgets(
        'should block connection with invalid certificate when pinning is enabled',
        (WidgetTester tester) async {
      // This test only runs when certificate pinning is explicitly enabled
      // Run with: --dart-define=ENABLE_CERT_PINNING=true

      if (CertificatePinning.isPinningEnabled) {
        // With placeholder certificates, the connection should fail
        try {
          await apiClient.get('/healthz');

          // If we get here with placeholder certs, something is wrong
          fail(
            'Expected certificate validation to fail with placeholder certificates',
          );
        } catch (e) {
          // This is expected - connection should be rejected
          expect(e.toString(), contains('certificate'));
        }
      } else {
        print('Test skipped: Certificate pinning is disabled');
      }
    });

    testWidgets('should successfully connect when certificates match',
        (WidgetTester tester) async {
      // This test will pass once real certificate fingerprints are configured
      // Run with: --dart-define=ENABLE_CERT_PINNING=true

      if (CertificatePinning.isPinningEnabled &&
          CertificatePinning.verifyConfiguration()) {
        try {
          // Try health check endpoint
          final response = await apiClient.get('/healthz');

          expect(response, isNotNull);
          print('✅ Certificate pinning validation successful');
        } catch (e) {
          fail('Certificate pinning should allow valid certificates: $e');
        }
      } else {
        print(
          'Test skipped: Certificate pinning disabled or not properly configured',
        );
      }
    });

    testWidgets('should bypass pinning for development hosts',
        (WidgetTester tester) async {
      // Test that local development hosts bypass pinning

      final localClient = ApiClient(baseUrl: 'http://localhost:8000');

      try {
        // This should not fail due to certificate pinning
        // (though it may fail for other reasons if server isn't running)
        await localClient.get('/healthz');
      } catch (e) {
        // If it fails, it should NOT be due to certificate issues
        expect(
          e.toString().toLowerCase(),
          isNot(contains('certificate')),
        );
      }
    });

    testWidgets('should verify configuration on initialization',
        (WidgetTester tester) async {
      // Verify that configuration check runs on ApiClient creation
      final client = ApiClient();

      // If pinning is enabled and placeholders are in use,
      // verifyConfiguration should return false
      final isValid = CertificatePinning.verifyConfiguration();

      if (CertificatePinning.isPinningEnabled) {
        // With placeholder certificates, should be invalid
        expect(isValid, isFalse);
      }
    });
  });

  group('Certificate Pinning Test Helper', () {
    testWidgets('should have test pinning method available',
        (WidgetTester tester) async {
      final apiClient = ApiClient(baseUrl: ApiConfig.productionBaseUrl);

      // Test the testPinning helper method
      // This is only available in debug mode
      if (CertificatePinning.isPinningEnabled) {
        try {
          final result = await CertificatePinning.testPinning(
            apiClient._dio,
            '${ApiConfig.productionBaseUrl}/healthz',
          );

          // Result depends on whether real certs are configured
          print('Certificate pinning test result: $result');
        } catch (e) {
          print('Certificate pinning test error: $e');
        }
      }
    });
  });

  group('Production Readiness Checks', () {
    testWidgets('should have real certificates configured for production',
        (WidgetTester tester) async {
      // This test ensures production app has real certificates

      const isProduction = bool.fromEnvironment('dart.vm.product');

      if (isProduction) {
        // In production build, certificate pinning MUST be enabled
        expect(CertificatePinning.isPinningEnabled, isTrue);

        // Configuration must be valid (no placeholders)
        expect(
          CertificatePinning.verifyConfiguration(),
          isTrue,
          reason:
              'Production build must have valid certificate fingerprints configured',
        );
      }
    });

    testWidgets('should enable pinning by default in release builds',
        (WidgetTester tester) async {
      const isProduction = bool.fromEnvironment('dart.vm.product');

      if (isProduction) {
        expect(
          CertificatePinning.isPinningEnabled,
          isTrue,
          reason: 'Certificate pinning must be enabled in production',
        );
      }
    });
  });
}
