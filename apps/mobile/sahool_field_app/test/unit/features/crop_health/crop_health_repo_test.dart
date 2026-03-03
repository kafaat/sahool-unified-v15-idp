/// Crop Health Repository Unit Tests
/// اختبارات وحدات مستودع صحة المحاصيل
///
/// Tests CropHealthRepository methods including disease lookup, crop listing,
/// treatment retrieval, health check, and error handling.

import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/core/network/api_result.dart';
import 'package:sahool_field_app/features/crop_health/data/models/diagnosis_models.dart';
import 'package:sahool_field_app/features/crop_health/data/repositories/crop_health_repository.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════════

class MockHttpClient extends Mock implements http.Client {}

class FakeUri extends Fake implements Uri {}

/// Helper to create an http.Response with proper JSON content-type.
/// Without the content-type header, the http package defaults to latin1
/// encoding which cannot encode Arabic characters.
http.Response jsonResponse(String body, int statusCode) {
  return http.Response(
    body,
    statusCode,
    headers: {'content-type': 'application/json; charset=utf-8'},
  );
}

void main() {
  late CropHealthRepository repository;
  late MockHttpClient mockClient;

  setUpAll(() {
    registerFallbackValue(FakeUri());
  });

  setUp(() {
    mockClient = MockHttpClient();
    repository = CropHealthRepository(
      client: mockClient,
      authToken: 'test-token-123',
    );
  });

  tearDown(() {
    repository.dispose();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // getSupportedCrops
  // ═══════════════════════════════════════════════════════════════════════════

  group('getSupportedCrops', () {
    test('should return list of CropOption on success', () async {
      // Arrange
      final responseBody = json.encode([
        {
          'cropId': 'wheat',
          'name': 'Wheat',
          'nameAr': 'قمح',
          'icon': 'wheat_icon',
          'diseasesCount': 12,
        },
        {
          'cropId': 'barley',
          'name': 'Barley',
          'nameAr': 'شعير',
          'icon': 'barley_icon',
          'diseasesCount': 8,
        },
      ]);

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => jsonResponse(responseBody, 200));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isSuccess, isTrue);
      final crops = result.dataOrNull!;
      expect(crops, hasLength(2));
      expect(crops[0].cropId, 'wheat');
      expect(crops[0].name, 'Wheat');
      expect(crops[0].nameAr, 'قمح');
      expect(crops[1].cropId, 'barley');
    });

    test('should return empty list when server returns empty array', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('[]', 200));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isSuccess, isTrue);
      expect(result.dataOrNull, isEmpty);
    });

    test('should return Failure on server error 500', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer(
              (_) async => http.Response('Internal Server Error', 500));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 500);
      // Error message should be the Arabic server error message
      expect(failure.message, contains('خطأ في الخادم'));
    });

    test('should return Failure on 401 unauthorized', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Unauthorized', 401));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 401);
      expect(failure.message, contains('تسجيل الدخول'));
    });

    test('should return Failure on SocketException (no internet)', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(const SocketException('No internet'));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      expect(result.errorOrNull, contains('اتصال بالإنترنت'));
    });

    test('should return Failure on http.ClientException', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(http.ClientException('Connection refused'));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      expect(result.errorOrNull, contains('خطأ في الاتصال'));
    });

    test('should return Failure on FormatException', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('not json', 200));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // getDiseases
  // ═══════════════════════════════════════════════════════════════════════════

  group('getDiseases', () {
    test('should return list of DiseaseInfo on success', () async {
      // Arrange
      final responseBody = json.encode([
        {
          'diseaseId': 'leaf_rust',
          'name': 'Leaf Rust',
          'nameAr': 'صدأ الأوراق',
          'crop': 'wheat',
          'severity': 'high',
        },
        {
          'diseaseId': 'powdery_mildew',
          'name': 'Powdery Mildew',
          'nameAr': 'البياض الدقيقي',
          'crop': 'wheat',
          'severity': 'medium',
        },
      ]);

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => jsonResponse(responseBody, 200));

      // Act
      final result = await repository.getDiseases(cropType: 'wheat');

      // Assert
      expect(result.isSuccess, isTrue);
      final diseases = result.dataOrNull!;
      expect(diseases, hasLength(2));
      expect(diseases[0].diseaseId, 'leaf_rust');
      expect(diseases[0].name, 'Leaf Rust');
      expect(diseases[0].nameAr, 'صدأ الأوراق');
      expect(diseases[0].crop, 'wheat');
      expect(diseases[1].diseaseId, 'powdery_mildew');
    });

    test('should return diseases without crop filter', () async {
      // Arrange
      final responseBody = json.encode([
        {
          'diseaseId': 'rpw',
          'name': 'Red Palm Weevil',
          'nameAr': 'سوسة النخيل الحمراء',
          'crop': 'date_palm',
          'severity': 'critical',
        },
      ]);

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => jsonResponse(responseBody, 200));

      // Act
      final result = await repository.getDiseases();

      // Assert
      expect(result.isSuccess, isTrue);
      expect(result.dataOrNull, hasLength(1));
    });

    test('should return Failure on 404 not found', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Not Found', 404));

      // Act
      final result = await repository.getDiseases(cropType: 'unknown');

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<DiseaseInfo>>;
      expect(failure.statusCode, 404);
      expect(failure.message, contains('غير موجودة'));
    });

    test('should return Failure on network error', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(const SocketException('Network unreachable'));

      // Act
      final result = await repository.getDiseases();

      // Assert
      expect(result.isFailure, isTrue);
      expect(result.errorOrNull, contains('اتصال بالإنترنت'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // getTreatmentDetails
  // ═══════════════════════════════════════════════════════════════════════════

  group('getTreatmentDetails', () {
    test('should return treatment details on success', () async {
      // Arrange
      final responseBody = json.encode({
        'diseaseId': 'leaf_rust',
        'treatmentType': 'fungicide',
        'products': [
          {
            'name': 'Propiconazole',
            'nameAr': 'بروبيكونازول',
            'dosage': '0.5 L/ha',
          }
        ],
        'applicationMethod': 'Foliar spray',
        'frequency': 'Every 14 days',
      });

      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => jsonResponse(responseBody, 200));

      // Act
      final result = await repository.getTreatmentDetails('leaf_rust');

      // Assert
      expect(result.isSuccess, isTrue);
      final details = result.dataOrNull!;
      expect(details['diseaseId'], 'leaf_rust');
      expect(details['treatmentType'], 'fungicide');
      expect(details['products'], isList);
    });

    test('should return Failure when disease not found', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Not Found', 404));

      // Act
      final result = await repository.getTreatmentDetails('nonexistent');

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<Map<String, dynamic>>;
      expect(failure.statusCode, 404);
    });

    test('should return Failure on server error', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Error', 503));

      // Act
      final result = await repository.getTreatmentDetails('leaf_rust');

      // Assert
      expect(result.isFailure, isTrue);
      expect(result.errorOrNull, contains('خطأ في الخادم'));
    });

    test('should return Failure on network error', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(const SocketException('No route'));

      // Act
      final result = await repository.getTreatmentDetails('leaf_rust');

      // Assert
      expect(result.isFailure, isTrue);
      expect(result.errorOrNull, contains('اتصال بالإنترنت'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // isServiceAvailable (health check)
  // ═══════════════════════════════════════════════════════════════════════════

  group('isServiceAvailable', () {
    test('should return true when service is healthy', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer(
              (_) async => http.Response('{"status": "ok"}', 200));

      // Act
      final available = await repository.isServiceAvailable();

      // Assert
      expect(available, isTrue);
    });

    test('should return false when service returns non-200', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Service Unavailable', 503));

      // Act
      final available = await repository.isServiceAvailable();

      // Assert
      expect(available, isFalse);
    });

    test('should return false on SocketException', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(const SocketException('Connection refused'));

      // Act
      final available = await repository.isServiceAvailable();

      // Assert
      expect(available, isFalse);
    });

    test('should return false on any exception', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenThrow(Exception('Unexpected error'));

      // Act
      final available = await repository.isServiceAvailable();

      // Assert
      expect(available, isFalse);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Error handling edge cases
  // ═══════════════════════════════════════════════════════════════════════════

  group('Error handling', () {
    test('should handle 400 bad request', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Bad Request', 400));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 400);
      expect(failure.message, contains('طلب غير صحيح'));
    });

    test('should handle 403 forbidden', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Forbidden', 403));

      // Act
      final result = await repository.getDiseases();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<DiseaseInfo>>;
      expect(failure.statusCode, 403);
      expect(failure.message, contains('غير مصرح'));
    });

    test('should handle 408 timeout', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Request Timeout', 408));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 408);
      expect(failure.message, contains('مهلة'));
    });

    test('should handle 413 payload too large', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer(
              (_) async => http.Response('Payload Too Large', 413));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 413);
      expect(failure.message, contains('حجم الصورة'));
    });

    test('should handle 422 unprocessable entity', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer(
              (_) async => http.Response('Unprocessable Entity', 422));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 422);
      expect(failure.message, contains('صيغة الصورة'));
    });

    test('should handle 429 rate limit exceeded', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer(
              (_) async => http.Response('Too Many Requests', 429));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 429);
      expect(failure.message, contains('طلبات كثيرة'));
    });

    test('should handle unknown status code', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Unusual', 418));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result.isFailure, isTrue);
      final failure = result as Failure<List<CropOption>>;
      expect(failure.statusCode, 418);
      expect(failure.message, contains('خطأ في الاتصال'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Headers
  // ═══════════════════════════════════════════════════════════════════════════

  group('Request headers', () {
    test('should include auth token in headers when provided', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('[]', 200));

      // Act
      await repository.getSupportedCrops();

      // Assert
      final captured = verify(
        () => mockClient.get(any(), headers: captureAny(named: 'headers')),
      ).captured;

      final headers = captured.first as Map<String, String>;
      expect(headers['Authorization'], 'Bearer test-token-123');
      expect(headers['Accept'], 'application/json');
    });

    test('should omit auth header when no token provided', () async {
      // Arrange
      final repoNoAuth = CropHealthRepository(client: mockClient);
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('[]', 200));

      // Act
      await repoNoAuth.getSupportedCrops();

      // Assert
      final captured = verify(
        () => mockClient.get(any(), headers: captureAny(named: 'headers')),
      ).captured;

      final headers = captured.first as Map<String, String>;
      expect(headers.containsKey('Authorization'), isFalse);
      expect(headers['Accept'], 'application/json');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ApiResult type checks
  // ═══════════════════════════════════════════════════════════════════════════

  group('ApiResult types', () {
    test('Success result should have data accessible', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('[]', 200));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result, isA<Success<List<CropOption>>>());
      expect(result.dataOrNull, isNotNull);
      expect(result.errorOrNull, isNull);
    });

    test('Failure result should have error message accessible', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Error', 500));

      // Act
      final result = await repository.getSupportedCrops();

      // Assert
      expect(result, isA<Failure<List<CropOption>>>());
      expect(result.dataOrNull, isNull);
      expect(result.errorOrNull, isNotNull);
    });

    test('ApiResult.when should call correct branch for success', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('[]', 200));

      // Act
      final result = await repository.getSupportedCrops();
      final value = result.when(
        success: (data) => 'got ${data.length} crops',
        failure: (msg, code) => 'error: $msg',
      );

      // Assert
      expect(value, 'got 0 crops');
    });

    test('ApiResult.when should call correct branch for failure', () async {
      // Arrange
      when(() => mockClient.get(any(), headers: any(named: 'headers')))
          .thenAnswer((_) async => http.Response('Error', 500));

      // Act
      final result = await repository.getSupportedCrops();
      final value = result.when(
        success: (data) => 'got ${data.length} crops',
        failure: (msg, code) => 'error: $code',
      );

      // Assert
      expect(value, 'error: 500');
    });
  });
}
