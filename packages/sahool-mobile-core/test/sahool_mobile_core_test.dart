/// Smoke Test - SAHOOL Mobile Core Package
///
/// Verifies that the package and its key modules can be imported
/// without errors. This catches circular dependencies and missing
/// exports early.
///
/// Run with: flutter test test/sahool_mobile_core_test.dart

// ignore_for_file: unused_import

library;

import 'package:flutter_test/flutter_test.dart';

// Package top-level import
import 'package:sahool_mobile_core/sahool_mobile_core.dart';

// Core contracts
import 'package:sahool_mobile_core/core/contracts/service_ports.dart';
import 'package:sahool_mobile_core/core/contracts/error_codes.dart';

// Core validation
import 'package:sahool_mobile_core/core/validation/validators.dart';

void main() {
  group('sahool_mobile_core smoke tests', () {
    test('package can be imported', () {
      // If this test runs, the import of sahool_mobile_core succeeded.
      expect(true, isTrue);
    });

    test('ServicePorts class is accessible', () {
      // Verify the class and a known constant are reachable.
      expect(ServicePorts.fieldManagement, isA<int>());
    });

    test('ErrorCodes class is accessible', () {
      expect(ErrorCodes.networkError, isA<String>());
    });

    test('errorMessages map is populated', () {
      expect(errorMessages, isNotEmpty);
      expect(errorMessages.containsKey('UNKNOWN'), isTrue);
    });

    test('Validators class is accessible', () {
      final result = Validators.required('test');
      expect(result.isValid, isTrue);
    });

    test('ValidationResult.success is available', () {
      expect(ValidationResult.success.isValid, isTrue);
    });

    test('FieldValidators class is accessible', () {
      final fv = FieldValidators();
      expect(fv.validateNdvi(0.5).isValid, isTrue);
    });

    test('getServiceUrl helper works', () {
      final url = getServiceUrl(3000);
      expect(url, contains('3000'));
    });

    test('getErrorMessage helper works', () {
      final msg = getErrorMessage('UNKNOWN');
      expect(msg.code, 'UNKNOWN');
    });

    test('getLocalizedError helper works', () {
      final error = getLocalizedError('UNKNOWN', locale: 'en');
      expect(error, isNotEmpty);
    });
  });
}
