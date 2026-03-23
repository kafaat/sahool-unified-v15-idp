/// Irrigation Controller Tests
/// اختبارات وحدة التحكم في الري
///
/// Comprehensive tests for irrigation API and controller functionality including:
/// - Crop and method retrieval
/// - Irrigation calculations
/// - Water balance calculations
/// - Efficiency calculations
/// - Schedule management
/// - Sensor data integration
/// - Error handling

import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:mocktail/mocktail.dart';
import 'package:sahool_mobile_core/features/irrigation/data/remote/irrigation_api.dart';

import 'irrigation_fixtures.dart';
import 'irrigation_mocks.dart';

void main() {
  late MockHttpClient mockHttpClient;
  late IrrigationApi irrigationApi;

  setUpAll(() {
    registerIrrigationFallbackValues();
  });

  setUp(() {
    mockHttpClient = MockHttpClient();
    irrigationApi = IrrigationApi(client: mockHttpClient, authToken: 'test_token');
  });

  tearDown(() {
    irrigationApi.dispose();
  });

  group('IrrigationApi', () {
    // ═══════════════════════════════════════════════════════════════════════
    // Crops API - API المحاصيل
    // ═══════════════════════════════════════════════════════════════════════

    group('getCrops', () {
      test('should return list of crops on successful response', () async {
        // Arrange
        final cropsJson = IrrigationApiFixtures.sampleCrops
            .map((c) => {
                  'id': c.id,
                  'name_ar': c.nameAr,
                  'name_en': c.nameEn,
                  'kc': c.kc,
                  'kc_stages': c.kcStages,
                  'root_depth_mm': c.rootDepthMm,
                  'mad_fraction': c.madFraction,
                })
            .toList();

        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'data': cropsJson}),
                  200,
                  headers: {'content-type': 'application/json; charset=utf-8'},
                ));

        // Act
        final crops = await irrigationApi.getCrops();

        // Assert
        expect(crops, isNotEmpty);
        expect(crops.length, 3);
        expect(crops.first.id, 'wheat');
        expect(crops.first.nameAr, 'قمح');
        expect(crops.first.kc, 1.15);
      });

      test('should throw IrrigationApiException on error response', () async {
        // Arrange
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'message': 'Server error'}),
                  500,
                ));

        // Act & Assert
        expect(
          () => irrigationApi.getCrops(),
          throwsA(isA<IrrigationApiException>()),
        );
      });

      test('should throw IrrigationApiException on network error', () async {
        // Arrange
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenThrow(Exception('Network error'));

        // Act & Assert
        expect(
          () => irrigationApi.getCrops(),
          throwsA(isA<Exception>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Methods API - API طرق الري
    // ═══════════════════════════════════════════════════════════════════════

    group('getMethods', () {
      test('should return list of irrigation methods on successful response', () async {
        // Arrange
        final methodsJson = IrrigationApiFixtures.sampleMethods
            .map((m) => {
                  'id': m.id,
                  'name_ar': m.nameAr,
                  'name_en': m.nameEn,
                  'efficiency': m.efficiency,
                  'description': m.description,
                })
            .toList();

        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'data': methodsJson}),
                  200,
                  headers: {'content-type': 'application/json; charset=utf-8'},
                ));

        // Act
        final methods = await irrigationApi.getMethods();

        // Assert
        expect(methods, isNotEmpty);
        expect(methods.length, 4);
        expect(methods.first.id, 'drip');
        expect(methods.first.efficiency, 0.90);
      });

      test('should throw IrrigationApiException on 404 response', () async {
        // Arrange
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'message': 'Not found'}),
                  404,
                ));

        // Act & Assert
        expect(
          () => irrigationApi.getMethods(),
          throwsA(isA<IrrigationApiException>().having(
            (e) => e.statusCode,
            'statusCode',
            404,
          )),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Calculate API - API الحسابات
    // ═══════════════════════════════════════════════════════════════════════

    group('calculate', () {
      test('should return irrigation calculation on successful response', () async {
        // Arrange
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((_) async => http.Response(
              jsonEncode({'data': IrrigationApiFixtures.sampleCalculationJson}),
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            ));

        // Act
        final calculation = await irrigationApi.calculate(
          IrrigationApiFixtures.sampleCalculationRequest,
        );

        // Assert
        expect(calculation.waterNeedMm, 25.0);
        expect(calculation.waterNeedLiters, 250000.0);
        expect(calculation.waterNeedM3, 250.0);
        expect(calculation.irrigationDurationMinutes, 180.0);
        expect(calculation.etc, 7.48);
        expect(calculation.recommendation, isNotEmpty);
        expect(calculation.recommendationAr, isNotEmpty);
      });

      test('should send correct request body', () async {
        // Arrange
        String? capturedBody;
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((invocation) async {
          capturedBody = invocation.namedArguments[const Symbol('body')] as String?;
          return http.Response(
            jsonEncode({'data': IrrigationApiFixtures.sampleCalculationJson}),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        });

        // Act
        await irrigationApi.calculate(IrrigationApiFixtures.sampleCalculationRequest);

        // Assert
        expect(capturedBody, isNotNull);
        final body = jsonDecode(capturedBody!);
        expect(body['crop_id'], 'wheat');
        expect(body['method_id'], 'drip');
        expect(body['area_hectares'], 5.0);
        expect(body['et0'], 6.5);
        expect(body['soil_moisture_current'], 35.0);
        expect(body['growth_stage'], 'mid');
      });

      test('should throw IrrigationApiException on validation error', () async {
        // Arrange
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((_) async => http.Response(
              jsonEncode({'message': 'Invalid crop ID'}),
              400,
            ));

        // Act & Assert
        expect(
          () => irrigationApi.calculate(IrrigationApiFixtures.sampleCalculationRequest),
          throwsA(isA<IrrigationApiException>().having(
            (e) => e.statusCode,
            'statusCode',
            400,
          )),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Water Balance API - API التوازن المائي
    // ═══════════════════════════════════════════════════════════════════════

    group('calculateWaterBalance', () {
      test('should return water balance data on successful response', () async {
        // Arrange
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'data': IrrigationApiFixtures.sampleWaterBalance}),
                  200,
                ));

        // Act
        final balance = await irrigationApi.calculateWaterBalance(
          fieldId: 'field_001',
          from: DateTime.now().subtract(const Duration(days: 7)),
          to: DateTime.now(),
        );

        // Assert
        expect(balance['soil_moisture_percent'], 38.5);
        expect(balance['field_capacity'], 45.0);
        expect(balance['wilting_point'], 15.0);
        expect(balance['status'], 'optimal');
        expect(balance['irrigation_needed'], false);
      });

      test('should include correct query parameters', () async {
        // Arrange
        Uri? capturedUri;
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((invocation) async {
          capturedUri = invocation.positionalArguments[0] as Uri;
          return http.Response(
            jsonEncode({'data': IrrigationApiFixtures.sampleWaterBalance}),
            200,
          );
        });

        final from = DateTime(2024, 1, 1);
        final to = DateTime(2024, 1, 8);

        // Act
        await irrigationApi.calculateWaterBalance(
          fieldId: 'field_001',
          from: from,
          to: to,
        );

        // Assert
        expect(capturedUri, isNotNull);
        expect(capturedUri!.queryParameters['field_id'], 'field_001');
        expect(capturedUri!.queryParameters['from'], from.toIso8601String());
        expect(capturedUri!.queryParameters['to'], to.toIso8601String());
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Efficiency API - API الكفاءة
    // ═══════════════════════════════════════════════════════════════════════

    group('calculateEfficiency', () {
      test('should return efficiency data on successful response', () async {
        // Arrange
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((_) async => http.Response(
              jsonEncode({'data': IrrigationApiFixtures.sampleEfficiency}),
              200,
              headers: {'content-type': 'application/json; charset=utf-8'},
            ));

        // Act
        final efficiency = await irrigationApi.calculateEfficiency(
          methodId: 'drip',
          appliedWaterMm: 25.0,
          consumedWaterMm: 21.875,
        );

        // Assert
        expect(efficiency['efficiency_percent'], 87.5);
        expect(efficiency['applied_water_mm'], 25.0);
        expect(efficiency['consumed_water_mm'], 21.875);
        expect(efficiency['rating'], 'good');
      });

      test('should send correct efficiency calculation body', () async {
        // Arrange
        String? capturedBody;
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((invocation) async {
          capturedBody = invocation.namedArguments[const Symbol('body')] as String?;
          return http.Response(
            jsonEncode({'data': IrrigationApiFixtures.sampleEfficiency}),
            200,
            headers: {'content-type': 'application/json; charset=utf-8'},
          );
        });

        // Act
        await irrigationApi.calculateEfficiency(
          methodId: 'drip',
          appliedWaterMm: 25.0,
          consumedWaterMm: 21.875,
        );

        // Assert
        expect(capturedBody, isNotNull);
        final body = jsonDecode(capturedBody!);
        expect(body['method_id'], 'drip');
        expect(body['applied_water_mm'], 25.0);
        expect(body['consumed_water_mm'], 21.875);
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Schedule API - API الجداول
    // ═══════════════════════════════════════════════════════════════════════

    group('getSchedule', () {
      test('should return irrigation schedule on successful response', () async {
        // Arrange
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'data': IrrigationApiFixtures.sampleScheduleJson}),
                  200,
                ));

        // Act
        final schedule = await irrigationApi.getSchedule('field_001');

        // Assert
        expect(schedule.fieldId, 'field_001');
        expect(schedule.events, isNotEmpty);
        expect(schedule.events.length, 2);
        expect(schedule.events.first.status, 'pending');
      });

      test('should throw on missing schedule', () async {
        // Arrange
        when(() => mockHttpClient.get(any(), headers: any(named: 'headers')))
            .thenAnswer((_) async => http.Response(
                  jsonEncode({'message': 'No schedule found'}),
                  404,
                ));

        // Act & Assert
        expect(
          () => irrigationApi.getSchedule('nonexistent_field'),
          throwsA(isA<IrrigationApiException>()),
        );
      });
    });

    group('generateSchedule', () {
      test('should create and return new schedule on successful response', () async {
        // Arrange
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((_) async => http.Response(
              jsonEncode({'data': IrrigationApiFixtures.sampleScheduleJson}),
              201,
            ));

        // Act
        final schedule = await irrigationApi.generateSchedule(
          fieldId: 'field_001',
          cropId: 'wheat',
          methodId: 'drip',
          days: 14,
        );

        // Assert
        expect(schedule.fieldId, 'field_001');
        expect(schedule.events, isNotEmpty);
      });

      test('should send correct schedule generation body', () async {
        // Arrange
        String? capturedBody;
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((invocation) async {
          capturedBody = invocation.namedArguments[const Symbol('body')] as String?;
          return http.Response(
            jsonEncode({'data': IrrigationApiFixtures.sampleScheduleJson}),
            200,
          );
        });

        // Act
        await irrigationApi.generateSchedule(
          fieldId: 'field_001',
          cropId: 'wheat',
          methodId: 'drip',
          days: 14,
        );

        // Assert
        expect(capturedBody, isNotNull);
        final body = jsonDecode(capturedBody!);
        expect(body['field_id'], 'field_001');
        expect(body['crop_id'], 'wheat');
        expect(body['method_id'], 'drip');
        expect(body['days'], 14);
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Sensor API - API المستشعرات
    // ═══════════════════════════════════════════════════════════════════════

    group('recordSensorReading', () {
      test('should successfully record sensor reading', () async {
        // Arrange
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((_) async => http.Response('', 201));

        // Act & Assert
        expect(
          irrigationApi.recordSensorReading(
            fieldId: 'field_001',
            sensorType: 'soil_moisture',
            value: 38.5,
            unit: '%',
          ),
          completes,
        );
      });

      test('should send correct sensor reading body', () async {
        // Arrange
        String? capturedBody;
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((invocation) async {
          capturedBody = invocation.namedArguments[const Symbol('body')] as String?;
          return http.Response('', 200);
        });

        // Act
        await irrigationApi.recordSensorReading(
          fieldId: 'field_001',
          sensorType: 'soil_moisture',
          value: 38.5,
          unit: '%',
        );

        // Assert
        expect(capturedBody, isNotNull);
        final body = jsonDecode(capturedBody!);
        expect(body['field_id'], 'field_001');
        expect(body['sensor_type'], 'soil_moisture');
        expect(body['value'], 38.5);
        expect(body['unit'], '%');
        expect(body['timestamp'], isNotNull);
      });

      test('should throw on sensor recording failure', () async {
        // Arrange
        when(() => mockHttpClient.post(
              any(),
              headers: any(named: 'headers'),
              body: any(named: 'body'),
            )).thenAnswer((_) async => http.Response(
              jsonEncode({'message': 'Invalid sensor type'}),
              400,
            ));

        // Act & Assert
        expect(
          () => irrigationApi.recordSensorReading(
            fieldId: 'field_001',
            sensorType: 'invalid_sensor',
            value: 38.5,
            unit: '%',
          ),
          throwsA(isA<IrrigationApiException>()),
        );
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Model Tests - اختبارات النماذج
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationCrop', () {
    test('should create from JSON correctly', () {
      final crop = IrrigationCrop.fromJson(IrrigationApiFixtures.wheatCropJson);

      expect(crop.id, 'wheat');
      expect(crop.nameAr, 'قمح');
      expect(crop.nameEn, 'Wheat');
      expect(crop.kc, 1.15);
      expect(crop.kcStages, isNotNull);
      expect(crop.kcStages!['mid'], 1.15);
      expect(crop.rootDepthMm, 1500);
      expect(crop.madFraction, 0.55);
    });

    test('should handle missing kc_stages', () {
      final json = Map<String, dynamic>.from(IrrigationApiFixtures.wheatCropJson);
      json.remove('kc_stages');

      final crop = IrrigationCrop.fromJson(json);

      expect(crop.kcStages, isNull);
    });
  });

  group('IrrigationMethod', () {
    test('should create from JSON correctly', () {
      final method = IrrigationMethod.fromJson(IrrigationApiFixtures.dripMethodJson);

      expect(method.id, 'drip');
      expect(method.nameAr, 'ري بالتنقيط');
      expect(method.nameEn, 'Drip Irrigation');
      expect(method.efficiency, 0.90);
      expect(method.description, isNotEmpty);
    });

    test('should handle missing description', () {
      final json = Map<String, dynamic>.from(IrrigationApiFixtures.dripMethodJson);
      json.remove('description');

      final method = IrrigationMethod.fromJson(json);

      expect(method.description, isEmpty);
    });
  });

  group('IrrigationCalculationRequest', () {
    test('should serialize to JSON correctly', () {
      final request = IrrigationApiFixtures.sampleCalculationRequest;
      final json = request.toJson();

      expect(json['crop_id'], 'wheat');
      expect(json['method_id'], 'drip');
      expect(json['area_hectares'], 5.0);
      expect(json['et0'], 6.5);
      expect(json['soil_moisture_current'], 35.0);
      expect(json['soil_moisture_field_capacity'], 45.0);
      expect(json['growth_stage'], 'mid');
    });

    test('should exclude null optional fields', () {
      final request = IrrigationCalculationRequest(
        cropId: 'wheat',
        methodId: 'drip',
        areaHectares: 5.0,
        et0: 6.5,
      );
      final json = request.toJson();

      expect(json.containsKey('soil_moisture_current'), isFalse);
      expect(json.containsKey('soil_moisture_field_capacity'), isFalse);
      expect(json.containsKey('growth_stage'), isFalse);
    });
  });

  group('IrrigationSchedule', () {
    test('should create from JSON correctly', () {
      final schedule =
          IrrigationSchedule.fromJson(IrrigationApiFixtures.sampleScheduleJson);

      expect(schedule.fieldId, 'field_001');
      expect(schedule.events, isNotEmpty);
      expect(schedule.events.length, 2);
      expect(schedule.generatedAt, isNotNull);
    });
  });

  group('IrrigationEvent', () {
    test('should create from JSON correctly', () {
      final eventJson = {
        'scheduled_at': DateTime.now().toIso8601String(),
        'duration_minutes': 120.0,
        'water_amount_liters': 50000.0,
        'status': 'pending',
        'notes': 'Morning irrigation',
      };

      final event = IrrigationEvent.fromJson(eventJson);

      expect(event.durationMinutes, 120.0);
      expect(event.waterAmountLiters, 50000.0);
      expect(event.status, 'pending');
      expect(event.notes, 'Morning irrigation');
    });

    test('should handle null notes', () {
      final eventJson = {
        'scheduled_at': DateTime.now().toIso8601String(),
        'duration_minutes': 120.0,
        'water_amount_liters': 50000.0,
        'status': 'pending',
        'notes': null,
      };

      final event = IrrigationEvent.fromJson(eventJson);

      expect(event.notes, isNull);
    });
  });

  group('IrrigationApiException', () {
    test('should format toString correctly', () {
      final exception = IrrigationApiException('Test error', statusCode: 404);

      expect(exception.toString(), contains('Test error'));
      expect(exception.toString(), contains('404'));
    });

    test('should handle null statusCode', () {
      final exception = IrrigationApiException('Test error');

      expect(exception.toString(), contains('Test error'));
      expect(exception.statusCode, isNull);
    });
  });
}
