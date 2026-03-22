import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_atmosphere/models/field_model.dart';
import 'package:sahool_atmosphere/core/security/device_security.dart';

void main() {
  // ═════════════════════════════════════════════════════════════════════════════
  // FieldHealthStatus Enum Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldHealthStatus', () {
    test('has exactly 4 values', () {
      expect(FieldHealthStatus.values.length, 4);
    });

    test('contains healthy, stressed, critical, unknown', () {
      expect(FieldHealthStatus.values, contains(FieldHealthStatus.healthy));
      expect(FieldHealthStatus.values, contains(FieldHealthStatus.stressed));
      expect(FieldHealthStatus.values, contains(FieldHealthStatus.critical));
      expect(FieldHealthStatus.values, contains(FieldHealthStatus.unknown));
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // CropType Enum Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('CropType', () {
    test('has exactly 10 crop types', () {
      expect(CropType.values.length, 10);
    });

    test('wheat has correct bilingual names', () {
      expect(CropType.wheat.nameAr, 'قمح');
      expect(CropType.wheat.nameEn, 'Wheat');
      expect(CropType.wheat.emoji, '🌾');
    });

    test('tomato has correct bilingual names', () {
      expect(CropType.tomato.nameAr, 'طماطم');
      expect(CropType.tomato.nameEn, 'Tomato');
      expect(CropType.tomato.emoji, '🍅');
    });

    test('palm has correct bilingual names', () {
      expect(CropType.palm.nameAr, 'نخيل');
      expect(CropType.palm.nameEn, 'Palm');
      expect(CropType.palm.emoji, '🌴');
    });

    test('coffee has correct bilingual names', () {
      expect(CropType.coffee.nameAr, 'بن');
      expect(CropType.coffee.nameEn, 'Coffee');
      expect(CropType.coffee.emoji, '☕');
    });

    test('other is catch-all type', () {
      expect(CropType.other.nameAr, 'أخرى');
      expect(CropType.other.nameEn, 'Other');
    });

    test('every crop type has non-empty nameAr, nameEn, and emoji', () {
      for (final crop in CropType.values) {
        expect(crop.nameAr, isNotEmpty,
            reason: '${crop.name} should have non-empty Arabic name');
        expect(crop.nameEn, isNotEmpty,
            reason: '${crop.name} should have non-empty English name');
        expect(crop.emoji, isNotEmpty,
            reason: '${crop.name} should have non-empty emoji');
      }
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel Constructor Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel constructor', () {
    test('creates instance with all required fields', () {
      final field = FieldModel(
        id: 'field_001',
        nameAr: 'حقل القمح',
        nameEn: 'Wheat Field',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        ndviValue: 0.72,
        moisturePercent: 64,
        temperatureCelsius: 28,
        sunlightPercent: 85,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.id, 'field_001');
      expect(field.nameAr, 'حقل القمح');
      expect(field.nameEn, 'Wheat Field');
      expect(field.cropType, CropType.wheat);
      expect(field.areaHectares, 12.5);
      expect(field.ndviValue, 0.72);
      expect(field.moisturePercent, 64);
      expect(field.temperatureCelsius, 28);
      expect(field.sunlightPercent, 85);
    });

    test('defaults boundary to empty list', () {
      final field = FieldModel(
        id: 'field_001',
        nameAr: 'حقل',
        nameEn: 'Field',
        cropType: CropType.wheat,
        areaHectares: 10.0,
        ndviValue: 0.5,
        moisturePercent: 50,
        temperatureCelsius: 25,
        sunlightPercent: 70,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.boundary, isEmpty);
      expect(field.center, isNull);
      expect(field.hasAlerts, isFalse);
      expect(field.pendingTasks, 0);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel.healthStatus Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel.healthStatus', () {
    FieldModel createFieldWithNdvi(double ndvi) {
      return FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.wheat,
        areaHectares: 1.0,
        ndviValue: ndvi,
        moisturePercent: 50,
        temperatureCelsius: 25,
        sunlightPercent: 70,
        lastUpdated: DateTime(2026, 1, 20),
      );
    }

    test('returns healthy when NDVI >= 0.6', () {
      expect(createFieldWithNdvi(0.6).healthStatus, FieldHealthStatus.healthy);
      expect(createFieldWithNdvi(0.72).healthStatus, FieldHealthStatus.healthy);
      expect(createFieldWithNdvi(1.0).healthStatus, FieldHealthStatus.healthy);
    });

    test('returns stressed when NDVI >= 0.4 and < 0.6', () {
      expect(
          createFieldWithNdvi(0.4).healthStatus, FieldHealthStatus.stressed);
      expect(
          createFieldWithNdvi(0.5).healthStatus, FieldHealthStatus.stressed);
      expect(
          createFieldWithNdvi(0.59).healthStatus, FieldHealthStatus.stressed);
    });

    test('returns critical when NDVI > 0 and < 0.4', () {
      expect(
          createFieldWithNdvi(0.1).healthStatus, FieldHealthStatus.critical);
      expect(
          createFieldWithNdvi(0.39).healthStatus, FieldHealthStatus.critical);
    });

    test('returns unknown when NDVI == 0', () {
      expect(createFieldWithNdvi(0.0).healthStatus, FieldHealthStatus.unknown);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel.needsAttention Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel.needsAttention', () {
    test('returns true for critical NDVI', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.tomato,
        areaHectares: 5.0,
        ndviValue: 0.2,
        moisturePercent: 50,
        temperatureCelsius: 30,
        sunlightPercent: 80,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.needsAttention, isTrue);
    });

    test('returns true for stressed NDVI', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.tomato,
        areaHectares: 5.0,
        ndviValue: 0.45,
        moisturePercent: 50,
        temperatureCelsius: 30,
        sunlightPercent: 80,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.needsAttention, isTrue);
    });

    test('returns true when hasAlerts is true even with healthy NDVI', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.tomato,
        areaHectares: 5.0,
        ndviValue: 0.72,
        moisturePercent: 50,
        temperatureCelsius: 30,
        sunlightPercent: 80,
        lastUpdated: DateTime(2026, 1, 20),
        hasAlerts: true,
      );

      expect(field.needsAttention, isTrue);
    });

    test('returns false when healthy NDVI and no alerts', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        ndviValue: 0.72,
        moisturePercent: 64,
        temperatureCelsius: 28,
        sunlightPercent: 85,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.needsAttention, isFalse);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel computed properties Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel computed properties', () {
    test('healthPercent rounds NDVI to percentage', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        ndviValue: 0.72,
        moisturePercent: 64,
        temperatureCelsius: 28,
        sunlightPercent: 85,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.healthPercent, 72);
    });

    test('areaFormatted returns formatted string in Arabic', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        moisturePercent: 50,
        temperatureCelsius: 25,
        sunlightPercent: 70,
        ndviValue: 0.6,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.areaFormatted, '12.5 هكتار');
    });

    test('areaFormatted formats to 1 decimal place', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'اختبار',
        nameEn: 'Test',
        cropType: CropType.palm,
        areaHectares: 25.0,
        moisturePercent: 72,
        temperatureCelsius: 29,
        sunlightPercent: 78,
        ndviValue: 0.68,
        lastUpdated: DateTime(2026, 1, 20),
      );

      expect(field.areaFormatted, '25.0 هكتار');
    });

    test('toString returns readable representation', () {
      final field = FieldModel(
        id: 'field_001',
        nameAr: 'حقل القمح',
        nameEn: 'Wheat Field',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        ndviValue: 0.72,
        moisturePercent: 64,
        temperatureCelsius: 28,
        sunlightPercent: 85,
        lastUpdated: DateTime(2026, 1, 20),
      );

      final str = field.toString();
      expect(str, contains('field_001'));
      expect(str, contains('حقل القمح'));
      expect(str, contains('12.5'));
      expect(str, contains('0.72'));
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel.fromJson Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel.fromJson', () {
    test('parses complete JSON with all fields', () {
      final json = {
        'id': 'field_001',
        'name_ar': 'حقل القمح',
        'name_en': 'Wheat Field',
        'crop_type': 'wheat',
        'area_hectares': 12.5,
        'ndvi': 0.72,
        'moisture': 64,
        'temperature': 28,
        'sunlight': 85,
        'boundary': [
          [44.1910, 15.3694],
          [44.1920, 15.3700],
        ],
        'center': [44.1920, 15.3693],
        'updated_at': '2026-01-20T10:00:00Z',
        'has_alerts': true,
        'pending_tasks': 3,
      };

      final field = FieldModel.fromJson(json);

      expect(field.id, 'field_001');
      expect(field.nameAr, 'حقل القمح');
      expect(field.nameEn, 'Wheat Field');
      expect(field.cropType, CropType.wheat);
      expect(field.areaHectares, 12.5);
      expect(field.ndviValue, 0.72);
      expect(field.moisturePercent, 64);
      expect(field.temperatureCelsius, 28);
      expect(field.sunlightPercent, 85);
      expect(field.boundary.length, 2);
      expect(field.center, isNotNull);
      expect(field.hasAlerts, isTrue);
      expect(field.pendingTasks, 3);
    });

    test('parses boundary coordinates as [lon, lat] -> LatLng(lat, lon)', () {
      final json = {
        'id': 'field_001',
        'crop_type': 'wheat',
        'boundary': [
          [44.1910, 15.3694],
        ],
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      // boundary is [longitude, latitude] -> LatLng(latitude, longitude)
      expect(field.boundary[0].latitude, 15.3694);
      expect(field.boundary[0].longitude, 44.1910);
    });

    test('parses center coordinate as [lon, lat] -> LatLng(lat, lon)', () {
      final json = {
        'id': 'field_001',
        'crop_type': 'wheat',
        'center': [44.1920, 15.3693],
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.center!.latitude, 15.3693);
      expect(field.center!.longitude, 44.1920);
    });

    test('uses fallback name when name_ar/name_en missing', () {
      final json = {
        'id': 'field_001',
        'name': 'Fallback Name',
        'crop_type': 'wheat',
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.nameAr, 'Fallback Name');
      expect(field.nameEn, 'Fallback Name');
    });

    test('uses default names when no name fields present', () {
      final json = {
        'id': 'field_001',
        'crop_type': 'wheat',
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.nameAr, 'غير محدد');
      expect(field.nameEn, 'Unnamed');
    });

    test('uses CropType.other for unknown crop type', () {
      final json = {
        'id': 'field_001',
        'crop_type': 'mango_tree',
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.cropType, CropType.other);
    });

    test('handles null numeric fields with defaults', () {
      final json = {
        'id': 'field_001',
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.areaHectares, 0.0);
      expect(field.ndviValue, 0.0);
      expect(field.moisturePercent, 0);
      expect(field.temperatureCelsius, 0);
      expect(field.sunlightPercent, 0);
    });

    test('handles null boundary with empty list', () {
      final json = {
        'id': 'field_001',
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.boundary, isEmpty);
      expect(field.center, isNull);
    });

    test('handles null has_alerts and pending_tasks', () {
      final json = {
        'id': 'field_001',
        'updated_at': '2026-01-20T10:00:00Z',
      };

      final field = FieldModel.fromJson(json);

      expect(field.hasAlerts, isFalse);
      expect(field.pendingTasks, 0);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel.toJson Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel.toJson', () {
    test('produces correct map', () {
      final field = FieldModel(
        id: 'field_001',
        nameAr: 'حقل القمح',
        nameEn: 'Wheat Field',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        ndviValue: 0.72,
        moisturePercent: 64,
        temperatureCelsius: 28,
        sunlightPercent: 85,
        boundary: [const LatLng(15.3694, 44.1910)],
        center: const LatLng(15.3693, 44.1920),
        lastUpdated: DateTime.utc(2026, 1, 20, 10, 0),
        hasAlerts: true,
        pendingTasks: 3,
      );

      final json = field.toJson();

      expect(json['id'], 'field_001');
      expect(json['name_ar'], 'حقل القمح');
      expect(json['name_en'], 'Wheat Field');
      expect(json['crop_type'], 'wheat');
      expect(json['area_hectares'], 12.5);
      expect(json['ndvi'], 0.72);
      expect(json['moisture'], 64);
      expect(json['temperature'], 28);
      expect(json['sunlight'], 85);
      expect(json['has_alerts'], isTrue);
      expect(json['pending_tasks'], 3);
    });

    test('serializes boundary as [lon, lat] pairs', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'test',
        nameEn: 'test',
        cropType: CropType.wheat,
        areaHectares: 1.0,
        ndviValue: 0.5,
        moisturePercent: 50,
        temperatureCelsius: 25,
        sunlightPercent: 70,
        boundary: [const LatLng(15.3694, 44.1910)],
        lastUpdated: DateTime(2026, 1, 20),
      );

      final json = field.toJson();
      final boundary = json['boundary'] as List;

      expect(boundary[0], [44.1910, 15.3694]);
    });

    test('serializes null center as null', () {
      final field = FieldModel(
        id: 'test',
        nameAr: 'test',
        nameEn: 'test',
        cropType: CropType.wheat,
        areaHectares: 1.0,
        ndviValue: 0.5,
        moisturePercent: 50,
        temperatureCelsius: 25,
        sunlightPercent: 70,
        lastUpdated: DateTime(2026, 1, 20),
      );

      final json = field.toJson();

      expect(json['center'], isNull);
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final original = FieldModel(
        id: 'field_001',
        nameAr: 'حقل القمح',
        nameEn: 'Wheat Field',
        cropType: CropType.wheat,
        areaHectares: 12.5,
        ndviValue: 0.72,
        moisturePercent: 64,
        temperatureCelsius: 28,
        sunlightPercent: 85,
        lastUpdated: DateTime.utc(2026, 1, 20, 10, 0),
        hasAlerts: true,
        pendingTasks: 3,
      );

      final json = original.toJson();
      final restored = FieldModel.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.nameAr, original.nameAr);
      expect(restored.nameEn, original.nameEn);
      expect(restored.cropType, original.cropType);
      expect(restored.areaHectares, original.areaHectares);
      expect(restored.ndviValue, original.ndviValue);
      expect(restored.moisturePercent, original.moisturePercent);
      expect(restored.temperatureCelsius, original.temperatureCelsius);
      expect(restored.sunlightPercent, original.sunlightPercent);
      expect(restored.hasAlerts, original.hasAlerts);
      expect(restored.pendingTasks, original.pendingTasks);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // FieldModel.copyWith Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('FieldModel.copyWith', () {
    final original = FieldModel(
      id: 'field_001',
      nameAr: 'حقل القمح',
      nameEn: 'Wheat Field',
      cropType: CropType.wheat,
      areaHectares: 12.5,
      ndviValue: 0.72,
      moisturePercent: 64,
      temperatureCelsius: 28,
      sunlightPercent: 85,
      lastUpdated: DateTime(2026, 1, 20),
    );

    test('preserves unchanged fields', () {
      final copy = original.copyWith(ndviValue: 0.80);

      expect(copy.id, original.id);
      expect(copy.nameAr, original.nameAr);
      expect(copy.cropType, original.cropType);
      expect(copy.ndviValue, 0.80);
    });

    test('updates multiple fields at once', () {
      final copy = original.copyWith(
        moisturePercent: 40,
        temperatureCelsius: 35,
        hasAlerts: true,
      );

      expect(copy.moisturePercent, 40);
      expect(copy.temperatureCelsius, 35);
      expect(copy.hasAlerts, isTrue);
      expect(copy.ndviValue, original.ndviValue);
    });

    test('can change crop type', () {
      final copy = original.copyWith(cropType: CropType.tomato);

      expect(copy.cropType, CropType.tomato);
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SampleFields Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SampleFields', () {
    test('all returns 5 sample fields', () {
      expect(SampleFields.all.length, 5);
    });

    test('all fields have unique IDs', () {
      final ids = SampleFields.all.map((f) => f.id).toSet();
      expect(ids.length, 5);
    });

    test('all fields have boundary coordinates', () {
      for (final field in SampleFields.all) {
        expect(field.boundary, isNotEmpty,
            reason: '${field.id} should have boundary coordinates');
      }
    });

    test('all fields have center points', () {
      for (final field in SampleFields.all) {
        expect(field.center, isNotNull,
            reason: '${field.id} should have a center point');
      }
    });

    test('totalArea sums all field areas', () {
      final expectedTotal =
          SampleFields.all.fold(0.0, (sum, f) => sum + f.areaHectares);
      expect(SampleFields.totalArea, expectedTotal);
    });

    test('averageHealth computes correct average', () {
      final expectedAvg =
          SampleFields.all.fold(0.0, (sum, f) => sum + f.ndviValue) /
              SampleFields.all.length;
      expect(SampleFields.averageHealth, closeTo(expectedAvg, 0.001));
    });

    test('needingAttention returns fields that need attention', () {
      final needing = SampleFields.needingAttention;

      for (final field in needing) {
        expect(field.needsAttention, isTrue);
      }
    });

    test('needingAttention count matches manual filter', () {
      final manualCount =
          SampleFields.all.where((f) => f.needsAttention).length;
      expect(SampleFields.needingAttention.length, manualCount);
    });

    test('sample fields include different crop types', () {
      final cropTypes = SampleFields.all.map((f) => f.cropType).toSet();
      expect(cropTypes.length, greaterThan(1));
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SecurityThreatLevel Enum Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SecurityThreatLevel', () {
    test('has exactly 5 levels', () {
      expect(SecurityThreatLevel.values.length, 5);
    });

    test('contains all expected levels', () {
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.none));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.low));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.medium));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.high));
      expect(SecurityThreatLevel.values, contains(SecurityThreatLevel.unknown));
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // SecurityCheckResult Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('SecurityCheckResult', () {
    test('hasIssues returns true when threats list is non-empty', () {
      const result = SecurityCheckResult(
        isCompromised: false,
        isEmulator: false,
        isDebugMode: true,
        threatLevel: SecurityThreatLevel.low,
        threats: ['Debug mode active'],
        deviceInfo: {},
      );

      expect(result.hasIssues, isTrue);
    });

    test('hasIssues returns false when threats list is empty', () {
      const result = SecurityCheckResult(
        isCompromised: false,
        isEmulator: false,
        isDebugMode: false,
        threatLevel: SecurityThreatLevel.none,
        threats: [],
        deviceInfo: {},
      );

      expect(result.hasIssues, isFalse);
    });

    test('toString returns readable format', () {
      const result = SecurityCheckResult(
        isCompromised: true,
        isEmulator: false,
        isDebugMode: false,
        threatLevel: SecurityThreatLevel.high,
        threats: ['Device is rooted'],
        deviceInfo: {},
      );

      final str = result.toString();
      expect(str, contains('compromised: true'));
      expect(str, contains('emulator: false'));
      expect(str, contains('high'));
    });

    test('compromised device has correct fields', () {
      const result = SecurityCheckResult(
        isCompromised: true,
        isEmulator: false,
        isDebugMode: false,
        threatLevel: SecurityThreatLevel.high,
        threats: ['Device is rooted'],
        deviceInfo: {'platform': 'Android'},
      );

      expect(result.isCompromised, isTrue);
      expect(result.threatLevel, SecurityThreatLevel.high);
      expect(result.deviceInfo['platform'], 'Android');
    });
  });

  // ═════════════════════════════════════════════════════════════════════════════
  // DeviceSecurityService.getThreatMessage Tests
  // ═════════════════════════════════════════════════════════════════════════════

  group('DeviceSecurityService.getThreatMessage', () {
    late DeviceSecurityService service;

    setUp(() {
      service = DeviceSecurityService();
    });

    test('high threat returns Arabic warning by default', () {
      final msg = service.getThreatMessage(SecurityThreatLevel.high);
      expect(msg, contains('تحذير'));
      expect(msg, contains('روت'));
    });

    test('high threat returns English warning when arabic=false', () {
      final msg =
          service.getThreatMessage(SecurityThreatLevel.high, arabic: false);
      expect(msg, contains('Warning'));
      expect(msg, contains('Root'));
    });

    test('none threat returns secure message', () {
      final msgAr = service.getThreatMessage(SecurityThreatLevel.none);
      expect(msgAr, contains('آمن'));

      final msgEn =
          service.getThreatMessage(SecurityThreatLevel.none, arabic: false);
      expect(msgEn, contains('secure'));
    });

    test('low threat returns development mode message', () {
      final msgAr = service.getThreatMessage(SecurityThreatLevel.low);
      expect(msgAr, contains('التطوير'));

      final msgEn =
          service.getThreatMessage(SecurityThreatLevel.low, arabic: false);
      expect(msgEn, contains('Development'));
    });

    test('medium threat returns emulator message', () {
      final msgAr = service.getThreatMessage(SecurityThreatLevel.medium);
      expect(msgAr, contains('محاكي'));

      final msgEn =
          service.getThreatMessage(SecurityThreatLevel.medium, arabic: false);
      expect(msgEn, contains('emulator'));
    });

    test('unknown threat returns not checked message', () {
      final msgAr = service.getThreatMessage(SecurityThreatLevel.unknown);
      expect(msgAr, contains('لم يتم فحص'));

      final msgEn =
          service.getThreatMessage(SecurityThreatLevel.unknown, arabic: false);
      expect(msgEn, contains('not checked'));
    });

    test('every threat level has bilingual messages', () {
      for (final level in SecurityThreatLevel.values) {
        final arabic = service.getThreatMessage(level, arabic: true);
        final english = service.getThreatMessage(level, arabic: false);

        expect(arabic, isNotEmpty,
            reason: '${level.name} should have Arabic message');
        expect(english, isNotEmpty,
            reason: '${level.name} should have English message');
        expect(arabic, isNot(equals(english)),
            reason:
                '${level.name} Arabic and English messages should differ');
      }
    });
  });
}
