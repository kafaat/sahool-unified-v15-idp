import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/fields/domain/entities/field_entity.dart';

void main() {
  final now = DateTime(2026, 3, 1);

  group('FieldEntity', () {
    late FieldEntity entity;

    setUp(() {
      entity = FieldEntity(
        id: 'field-001',
        tenantId: 'tenant-001',
        name: 'حقل القمح',
        areaHectares: 5.5,
        cropType: 'wheat',
        healthScore: 0.75,
        ndviValue: 0.72,
        plantingDate: DateTime(2025, 11, 1),
        expectedHarvest: DateTime(2026, 4, 15),
        status: FieldStatus.active,
        createdAt: now,
        updatedAt: now,
      );
    });

    test('healthLabel returns correct Arabic label', () {
      expect(entity.healthLabel, 'جيد'); // 0.75

      final excellent = entity.copyWith(healthScore: 0.85);
      expect(excellent.healthLabel, 'ممتاز');

      final moderate = entity.copyWith(healthScore: 0.45);
      expect(moderate.healthLabel, 'متوسط');

      final poor = entity.copyWith(healthScore: 0.2);
      expect(poor.healthLabel, 'ضعيف');
    });

    test('cropEmoji returns wheat emoji', () {
      expect(entity.cropEmoji, '🌾');
    });

    test('cropEmoji returns correct emojis for various crops', () {
      expect(entity.copyWith(cropType: 'tomato').cropEmoji, '🍅');
      expect(entity.copyWith(cropType: 'طماطم').cropEmoji, '🍅');
      expect(entity.copyWith(cropType: 'corn').cropEmoji, '🌽');
      expect(entity.copyWith(cropType: 'palm').cropEmoji, '🌴');
      expect(entity.copyWith(cropType: 'potato').cropEmoji, '🥔');
      expect(entity.copyWith(cropType: 'onion').cropEmoji, '🧅');
      expect(entity.copyWith(cropType: 'unknown').cropEmoji, '🌱');
    });

    test('equality is based on id', () {
      final same = entity.copyWith(name: 'Different');
      expect(entity, same);

      final different = entity.copyWith(id: 'field-002');
      expect(entity, isNot(different));
    });

    test('hashCode is based on id', () {
      expect(entity.hashCode, 'field-001'.hashCode);
    });

    test('toString contains id and name', () {
      expect(entity.toString(), contains('field-001'));
      expect(entity.toString(), contains('حقل القمح'));
    });
  });

  group('FieldEntity fromJson/toJson', () {
    test('round-trip serialization', () {
      final json = {
        'id': 'field-100',
        'tenant_id': 'tenant-1',
        'name': 'Test Field',
        'area_hectares': 10.0,
        'crop_type': 'wheat',
        'health_score': 0.8,
        'ndvi_value': 0.72,
        'soil_type': 'Sandy Loam',
        'irrigation_type': 'drip',
        'status': 'active',
        'created_at': '2026-01-01T00:00:00.000',
        'updated_at': '2026-03-01T00:00:00.000',
      };

      final entity = FieldEntity.fromJson(json);
      expect(entity.id, 'field-100');
      expect(entity.areaHectares, 10.0);
      expect(entity.healthScore, 0.8);
      expect(entity.soilType, 'Sandy Loam');
      expect(entity.status, FieldStatus.active);

      final exported = entity.toJson();
      expect(exported['id'], 'field-100');
      expect(exported['area_hectares'], 10.0);
      expect(exported['status'], 'active');
    });

    test('fromJson handles optional fields', () {
      final json = {
        'id': 'f1',
        'tenant_id': 't1',
        'name': 'Minimal',
        'area_hectares': 1.0,
        'crop_type': 'wheat',
        'created_at': '2026-01-01T00:00:00.000',
        'updated_at': '2026-01-01T00:00:00.000',
      };

      final entity = FieldEntity.fromJson(json);
      expect(entity.farmId, isNull);
      expect(entity.ndviValue, isNull);
      expect(entity.soilType, isNull);
      expect(entity.healthScore, 0.0);
    });

    test('fromJson with center and boundary', () {
      final json = {
        'id': 'f2',
        'tenant_id': 't1',
        'name': 'Geo Field',
        'area_hectares': 5.0,
        'crop_type': 'tomato',
        'center': {'latitude': 15.369, 'longitude': 44.191},
        'boundary': [
          {'latitude': 15.369, 'longitude': 44.191},
          {'latitude': 15.370, 'longitude': 44.192},
        ],
        'created_at': '2026-01-01T00:00:00.000',
        'updated_at': '2026-01-01T00:00:00.000',
      };

      final entity = FieldEntity.fromJson(json);
      expect(entity.center, isNotNull);
      expect(entity.center!.latitude, 15.369);
      expect(entity.boundary, hasLength(2));
    });
  });

  group('FieldStatus', () {
    test('has 5 statuses', () {
      expect(FieldStatus.values, hasLength(5));
    });

    test('fromString resolves valid statuses', () {
      expect(FieldStatus.fromString('active'), FieldStatus.active);
      expect(FieldStatus.fromString('fallow'), FieldStatus.fallow);
      expect(FieldStatus.fromString('preparing'), FieldStatus.preparing);
      expect(FieldStatus.fromString('harvested'), FieldStatus.harvested);
      expect(FieldStatus.fromString('inactive'), FieldStatus.inactive);
    });

    test('fromString defaults to active for unknown', () {
      expect(FieldStatus.fromString('unknown'), FieldStatus.active);
    });

    test('has Arabic labels', () {
      expect(FieldStatus.active.arabicLabel, 'نشط');
      expect(FieldStatus.fallow.arabicLabel, 'بور');
      expect(FieldStatus.preparing.arabicLabel, 'تجهيز');
      expect(FieldStatus.harvested.arabicLabel, 'تم الحصاد');
      expect(FieldStatus.inactive.arabicLabel, 'غير نشط');
    });
  });

  group('GeoLocation', () {
    test('fromJson and toJson round-trip', () {
      const location = GeoLocation(latitude: 15.369, longitude: 44.191);
      final json = location.toJson();
      final restored = GeoLocation.fromJson(json);

      expect(restored.latitude, 15.369);
      expect(restored.longitude, 44.191);
      expect(restored, location);
    });

    test('equality works', () {
      const a = GeoLocation(latitude: 15.0, longitude: 44.0);
      const b = GeoLocation(latitude: 15.0, longitude: 44.0);
      const c = GeoLocation(latitude: 16.0, longitude: 44.0);

      expect(a, b);
      expect(a, isNot(c));
    });

    test('copyWith creates modified copy', () {
      const loc = GeoLocation(latitude: 15.0, longitude: 44.0);
      final moved = loc.copyWith(latitude: 16.0);
      expect(moved.latitude, 16.0);
      expect(moved.longitude, 44.0);
    });

    test('toString contains coordinates', () {
      const loc = GeoLocation(latitude: 15.369, longitude: 44.191);
      expect(loc.toString(), contains('15.369'));
      expect(loc.toString(), contains('44.191'));
    });
  });
}
