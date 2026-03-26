import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/fields/domain/entities/field_entity.dart';

void main() {
  // ===========================================================================
  // FieldStatus Enum
  // ===========================================================================
  group('FieldStatus', () {
    group('fromString', () {
      test('returns active for "active"', () {
        expect(FieldStatus.fromString('active'), FieldStatus.active);
      });

      test('returns fallow for "fallow"', () {
        expect(FieldStatus.fromString('fallow'), FieldStatus.fallow);
      });

      test('returns preparing for "preparing"', () {
        expect(FieldStatus.fromString('preparing'), FieldStatus.preparing);
      });

      test('returns harvested for "harvested"', () {
        expect(FieldStatus.fromString('harvested'), FieldStatus.harvested);
      });

      test('returns inactive for "inactive"', () {
        expect(FieldStatus.fromString('inactive'), FieldStatus.inactive);
      });

      test('defaults to active for unknown value', () {
        expect(FieldStatus.fromString('unknown'), FieldStatus.active);
      });

      test('defaults to active for empty string', () {
        expect(FieldStatus.fromString(''), FieldStatus.active);
      });

      test('is case-sensitive (Active does not match)', () {
        expect(FieldStatus.fromString('Active'), FieldStatus.active);
      });

      test('defaults to active for numeric string', () {
        expect(FieldStatus.fromString('123'), FieldStatus.active);
      });
    });

    group('value property', () {
      test('returns correct English string for each status', () {
        expect(FieldStatus.active.value, 'active');
        expect(FieldStatus.fallow.value, 'fallow');
        expect(FieldStatus.preparing.value, 'preparing');
        expect(FieldStatus.harvested.value, 'harvested');
        expect(FieldStatus.inactive.value, 'inactive');
      });
    });

    group('arabicLabel property', () {
      test('returns correct Arabic string for active', () {
        expect(FieldStatus.active.arabicLabel, 'نشط');
      });

      test('returns correct Arabic string for fallow', () {
        expect(FieldStatus.fallow.arabicLabel, 'بور');
      });

      test('returns correct Arabic string for preparing', () {
        expect(FieldStatus.preparing.arabicLabel, 'تجهيز');
      });

      test('returns correct Arabic string for harvested', () {
        expect(FieldStatus.harvested.arabicLabel, 'تم الحصاد');
      });

      test('returns correct Arabic string for inactive', () {
        expect(FieldStatus.inactive.arabicLabel, 'غير نشط');
      });
    });

    test('all enum values are covered (5 total)', () {
      expect(FieldStatus.values.length, 5);
    });
  });

  // ===========================================================================
  // GeoLocation
  // ===========================================================================
  group('GeoLocation', () {
    group('fromJson', () {
      test('creates instance from valid JSON with doubles', () {
        final json = {'latitude': 24.7136, 'longitude': 46.6753};
        final loc = GeoLocation.fromJson(json);
        expect(loc.latitude, 24.7136);
        expect(loc.longitude, 46.6753);
      });

      test('handles integer values as num', () {
        final json = {'latitude': 25, 'longitude': 47};
        final loc = GeoLocation.fromJson(json);
        expect(loc.latitude, 25.0);
        expect(loc.longitude, 47.0);
      });

      test('handles negative coordinates', () {
        final json = {'latitude': -33.8688, 'longitude': -151.2093};
        final loc = GeoLocation.fromJson(json);
        expect(loc.latitude, -33.8688);
        expect(loc.longitude, -151.2093);
      });

      test('handles zero coordinates', () {
        final json = {'latitude': 0, 'longitude': 0};
        final loc = GeoLocation.fromJson(json);
        expect(loc.latitude, 0.0);
        expect(loc.longitude, 0.0);
      });
    });

    group('toJson', () {
      test('produces correct map', () {
        const loc = GeoLocation(latitude: 24.7136, longitude: 46.6753);
        final json = loc.toJson();
        expect(json['latitude'], 24.7136);
        expect(json['longitude'], 46.6753);
      });

      test('produces map with exactly two keys', () {
        const loc = GeoLocation(latitude: 1.0, longitude: 2.0);
        final json = loc.toJson();
        expect(json.length, 2);
        expect(json.containsKey('latitude'), isTrue);
        expect(json.containsKey('longitude'), isTrue);
      });
    });

    group('roundtrip', () {
      test('fromJson then toJson preserves data', () {
        final original = {'latitude': 15.3694, 'longitude': 44.191};
        final loc = GeoLocation.fromJson(original);
        final result = loc.toJson();
        expect(result['latitude'], original['latitude']);
        expect(result['longitude'], original['longitude']);
      });
    });

    group('copyWith', () {
      test('latitude only', () {
        const loc = GeoLocation(latitude: 10.0, longitude: 20.0);
        final copy = loc.copyWith(latitude: 30.0);
        expect(copy.latitude, 30.0);
        expect(copy.longitude, 20.0);
      });

      test('longitude only', () {
        const loc = GeoLocation(latitude: 10.0, longitude: 20.0);
        final copy = loc.copyWith(longitude: 50.0);
        expect(copy.latitude, 10.0);
        expect(copy.longitude, 50.0);
      });

      test('both fields', () {
        const loc = GeoLocation(latitude: 10.0, longitude: 20.0);
        final copy = loc.copyWith(latitude: 1.0, longitude: 2.0);
        expect(copy.latitude, 1.0);
        expect(copy.longitude, 2.0);
      });

      test('no args returns equal copy', () {
        const loc = GeoLocation(latitude: 10.0, longitude: 20.0);
        final copy = loc.copyWith();
        expect(copy, loc);
      });
    });

    group('equality', () {
      test('same values are equal', () {
        const a = GeoLocation(latitude: 24.7, longitude: 46.6);
        const b = GeoLocation(latitude: 24.7, longitude: 46.6);
        expect(a, b);
      });

      test('different latitude are not equal', () {
        const a = GeoLocation(latitude: 24.7, longitude: 46.6);
        const b = GeoLocation(latitude: 25.0, longitude: 46.6);
        expect(a, isNot(b));
      });

      test('different longitude are not equal', () {
        const a = GeoLocation(latitude: 24.7, longitude: 46.6);
        const b = GeoLocation(latitude: 24.7, longitude: 47.0);
        expect(a, isNot(b));
      });

      test('hashCode same for equal instances', () {
        const a = GeoLocation(latitude: 24.7, longitude: 46.6);
        const b = GeoLocation(latitude: 24.7, longitude: 46.6);
        expect(a.hashCode, b.hashCode);
      });

      test('identical instance is equal to itself', () {
        const loc = GeoLocation(latitude: 10.0, longitude: 20.0);
        expect(loc == loc, isTrue);
      });

      test('not equal to a non-GeoLocation object', () {
        const loc = GeoLocation(latitude: 10.0, longitude: 20.0);
        // ignore: unrelated_type_equality_checks
        expect(loc == 'string', isFalse);
      });
    });

    test('toString contains coordinates', () {
      const loc = GeoLocation(latitude: 24.7, longitude: 46.6);
      expect(loc.toString(), contains('24.7'));
      expect(loc.toString(), contains('46.6'));
    });
  });

  // ===========================================================================
  // FieldEntity helpers
  // ===========================================================================
  FieldEntity _makeField({
    String id = 'field-001',
    String tenantId = 'tenant-001',
    String name = 'Test Field',
    double areaHectares = 10.0,
    String cropType = 'wheat',
    double healthScore = 0.7,
    double? ndviValue,
    double? ndwiValue,
    String? soilType,
    String? irrigationType,
    DateTime? lastIrrigation,
    DateTime? plantingDate,
    DateTime? expectedHarvest,
    FieldStatus status = FieldStatus.active,
    GeoLocation? center,
    List<GeoLocation>? boundary,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? farmId,
    String? farmName,
  }) {
    return FieldEntity(
      id: id,
      tenantId: tenantId,
      name: name,
      farmId: farmId,
      farmName: farmName,
      areaHectares: areaHectares,
      cropType: cropType,
      healthScore: healthScore,
      ndviValue: ndviValue,
      ndwiValue: ndwiValue,
      soilType: soilType,
      irrigationType: irrigationType,
      lastIrrigation: lastIrrigation,
      plantingDate: plantingDate,
      expectedHarvest: expectedHarvest,
      status: status,
      center: center,
      boundary: boundary,
      createdAt: createdAt ?? DateTime(2025, 1, 1),
      updatedAt: updatedAt ?? DateTime(2025, 1, 2),
    );
  }

  Map<String, dynamic> _minimalJson({
    String id = 'f1',
    String tenantId = 't1',
    String name = 'Field',
    num areaHectares = 5.0,
    String cropType = 'wheat',
  }) {
    return {
      'id': id,
      'tenant_id': tenantId,
      'name': name,
      'area_hectares': areaHectares,
      'crop_type': cropType,
      'created_at': '2025-01-01T00:00:00.000',
      'updated_at': '2025-01-02T00:00:00.000',
    };
  }

  // ===========================================================================
  // FieldEntity - fromJson / toJson
  // ===========================================================================
  group('FieldEntity.fromJson', () {
    test('parses minimal JSON correctly', () {
      final field = FieldEntity.fromJson(_minimalJson());
      expect(field.id, 'f1');
      expect(field.tenantId, 't1');
      expect(field.name, 'Field');
      expect(field.areaHectares, 5.0);
      expect(field.cropType, 'wheat');
      expect(field.healthScore, 0.0);
      expect(field.status, FieldStatus.active);
    });

    test('parses full JSON with all optional fields', () {
      final json = {
        ..._minimalJson(),
        'farm_id': 'farm-1',
        'farm_name': 'My Farm',
        'health_score': 0.85,
        'ndvi_value': 0.72,
        'ndwi_value': 0.45,
        'soil_type': 'clay',
        'irrigation_type': 'drip',
        'last_irrigation': '2025-06-01T08:00:00.000',
        'planting_date': '2025-01-15T00:00:00.000',
        'expected_harvest': '2025-06-15T00:00:00.000',
        'status': 'fallow',
        'center': {'latitude': 24.7, 'longitude': 46.6},
        'boundary': [
          {'latitude': 24.7, 'longitude': 46.6},
          {'latitude': 24.8, 'longitude': 46.7},
        ],
      };
      final field = FieldEntity.fromJson(json);
      expect(field.farmId, 'farm-1');
      expect(field.farmName, 'My Farm');
      expect(field.healthScore, 0.85);
      expect(field.ndviValue, 0.72);
      expect(field.ndwiValue, 0.45);
      expect(field.soilType, 'clay');
      expect(field.irrigationType, 'drip');
      expect(field.lastIrrigation, isNotNull);
      expect(field.plantingDate, DateTime(2025, 1, 15));
      expect(field.status, FieldStatus.fallow);
      expect(field.center, isNotNull);
      expect(field.center!.latitude, 24.7);
      expect(field.boundary, hasLength(2));
    });

    test('defaults healthScore to 0.0 when null in JSON', () {
      final json = _minimalJson();
      json['health_score'] = null;
      final field = FieldEntity.fromJson(json);
      expect(field.healthScore, 0.0);
    });

    test('defaults status to active when missing', () {
      final field = FieldEntity.fromJson(_minimalJson());
      expect(field.status, FieldStatus.active);
    });

    test('parses area_hectares from int', () {
      final json = _minimalJson(areaHectares: 10);
      final field = FieldEntity.fromJson(json);
      expect(field.areaHectares, 10.0);
    });

    test('parses null optional fields as null', () {
      final field = FieldEntity.fromJson(_minimalJson());
      expect(field.farmId, isNull);
      expect(field.farmName, isNull);
      expect(field.ndviValue, isNull);
      expect(field.ndwiValue, isNull);
      expect(field.soilType, isNull);
      expect(field.irrigationType, isNull);
      expect(field.lastIrrigation, isNull);
      expect(field.plantingDate, isNull);
      expect(field.expectedHarvest, isNull);
      expect(field.center, isNull);
      expect(field.boundary, isNull);
    });

    test('parses status "inactive" from JSON', () {
      final json = {..._minimalJson(), 'status': 'inactive'};
      final field = FieldEntity.fromJson(json);
      expect(field.status, FieldStatus.inactive);
    });

    test('parses empty boundary list', () {
      final json = {..._minimalJson(), 'boundary': <Map<String, dynamic>>[]};
      final field = FieldEntity.fromJson(json);
      expect(field.boundary, isNotNull);
      expect(field.boundary, isEmpty);
    });
  });

  group('FieldEntity.toJson', () {
    test('produces correct keys for minimal entity', () {
      final field = _makeField();
      final json = field.toJson();
      expect(json['id'], 'field-001');
      expect(json['tenant_id'], 'tenant-001');
      expect(json['name'], 'Test Field');
      expect(json['area_hectares'], 10.0);
      expect(json['crop_type'], 'wheat');
      expect(json['health_score'], 0.7);
      expect(json['status'], 'active');
    });

    test('includes null optional fields', () {
      final field = _makeField();
      final json = field.toJson();
      expect(json.containsKey('farm_id'), true);
      expect(json['farm_id'], isNull);
      expect(json['ndvi_value'], isNull);
    });

    test('serializes center when present', () {
      final field = _makeField(
        center: const GeoLocation(latitude: 24.7, longitude: 46.6),
      );
      final json = field.toJson();
      expect(json['center'], isA<Map>());
      expect(json['center']['latitude'], 24.7);
    });

    test('serializes boundary list when present', () {
      final field = _makeField(
        boundary: const [
          GeoLocation(latitude: 24.7, longitude: 46.6),
          GeoLocation(latitude: 24.8, longitude: 46.7),
        ],
      );
      final json = field.toJson();
      expect(json['boundary'], isA<List>());
      expect(json['boundary'], hasLength(2));
    });

    test('serializes dates as ISO8601 strings', () {
      final field = _makeField(
        lastIrrigation: DateTime(2025, 3, 15, 10, 30),
        plantingDate: DateTime(2025, 1, 10),
        expectedHarvest: DateTime(2025, 7, 20),
      );
      final json = field.toJson();
      expect(json['last_irrigation'], isA<String>());
      expect(json['planting_date'], isA<String>());
      expect(json['expected_harvest'], isA<String>());
    });

    test('roundtrip fromJson(toJson) preserves data', () {
      final original = _makeField(
        farmId: 'farm-1',
        farmName: 'Farm One',
        ndviValue: 0.65,
        soilType: 'sandy',
        irrigationType: 'pivot',
        center: const GeoLocation(latitude: 15.0, longitude: 44.0),
        boundary: const [
          GeoLocation(latitude: 15.0, longitude: 44.0),
          GeoLocation(latitude: 15.1, longitude: 44.1),
        ],
      );
      final json = original.toJson();
      final restored = FieldEntity.fromJson(json);
      expect(restored.id, original.id);
      expect(restored.name, original.name);
      expect(restored.farmId, original.farmId);
      expect(restored.ndviValue, original.ndviValue);
      expect(restored.soilType, original.soilType);
      expect(restored.center!.latitude, original.center!.latitude);
      expect(restored.boundary!.length, original.boundary!.length);
    });

    test('status serializes to its value string', () {
      final field = _makeField(status: FieldStatus.harvested);
      final json = field.toJson();
      expect(json['status'], 'harvested');
    });
  });

  // ===========================================================================
  // FieldEntity - healthLabel
  // ===========================================================================
  group('FieldEntity.healthLabel', () {
    test('returns ممتاز when healthScore >= 0.8', () {
      expect(_makeField(healthScore: 0.8).healthLabel, 'ممتاز');
    });

    test('returns ممتاز when healthScore is 1.0', () {
      expect(_makeField(healthScore: 1.0).healthLabel, 'ممتاز');
    });

    test('returns ممتاز when healthScore is 0.95', () {
      expect(_makeField(healthScore: 0.95).healthLabel, 'ممتاز');
    });

    test('returns جيد when healthScore is 0.6', () {
      expect(_makeField(healthScore: 0.6).healthLabel, 'جيد');
    });

    test('returns جيد when healthScore is 0.79', () {
      expect(_makeField(healthScore: 0.79).healthLabel, 'جيد');
    });

    test('returns جيد when healthScore is 0.7', () {
      expect(_makeField(healthScore: 0.7).healthLabel, 'جيد');
    });

    test('returns متوسط when healthScore is 0.4', () {
      expect(_makeField(healthScore: 0.4).healthLabel, 'متوسط');
    });

    test('returns متوسط when healthScore is 0.59', () {
      expect(_makeField(healthScore: 0.59).healthLabel, 'متوسط');
    });

    test('returns متوسط when healthScore is 0.5', () {
      expect(_makeField(healthScore: 0.5).healthLabel, 'متوسط');
    });

    test('returns ضعيف when healthScore is 0.39', () {
      expect(_makeField(healthScore: 0.39).healthLabel, 'ضعيف');
    });

    test('returns ضعيف when healthScore is 0.0', () {
      expect(_makeField(healthScore: 0.0).healthLabel, 'ضعيف');
    });

    test('returns ضعيف when healthScore is negative', () {
      expect(_makeField(healthScore: -0.1).healthLabel, 'ضعيف');
    });

    test('returns ضعيف when healthScore is 0.1', () {
      expect(_makeField(healthScore: 0.1).healthLabel, 'ضعيف');
    });
  });

  // ===========================================================================
  // FieldEntity - cropEmoji
  // ===========================================================================
  group('FieldEntity.cropEmoji', () {
    test('wheat returns grain emoji', () {
      expect(_makeField(cropType: 'wheat').cropEmoji, '🌾');
    });

    test('قمح (Arabic wheat) returns grain emoji', () {
      expect(_makeField(cropType: 'قمح').cropEmoji, '🌾');
    });

    test('barley returns grain emoji', () {
      expect(_makeField(cropType: 'barley').cropEmoji, '🌾');
    });

    test('شعير (Arabic barley) returns grain emoji', () {
      expect(_makeField(cropType: 'شعير').cropEmoji, '🌾');
    });

    test('alfalfa returns herb emoji', () {
      expect(_makeField(cropType: 'alfalfa').cropEmoji, '🌿');
    });

    test('برسيم (Arabic alfalfa) returns herb emoji', () {
      expect(_makeField(cropType: 'برسيم').cropEmoji, '🌿');
    });

    test('corn returns corn emoji', () {
      expect(_makeField(cropType: 'corn').cropEmoji, '🌽');
    });

    test('ذرة (Arabic corn) returns corn emoji', () {
      expect(_makeField(cropType: 'ذرة').cropEmoji, '🌽');
    });

    test('palm returns palm tree emoji', () {
      expect(_makeField(cropType: 'palm').cropEmoji, '🌴');
    });

    test('نخيل (Arabic palm) returns palm tree emoji', () {
      expect(_makeField(cropType: 'نخيل').cropEmoji, '🌴');
    });

    test('potato returns potato emoji', () {
      expect(_makeField(cropType: 'potato').cropEmoji, '🥔');
    });

    test('بطاطس (Arabic potato) returns potato emoji', () {
      expect(_makeField(cropType: 'بطاطس').cropEmoji, '🥔');
    });

    test('tomato returns tomato emoji', () {
      expect(_makeField(cropType: 'tomato').cropEmoji, '🍅');
    });

    test('طماطم (Arabic tomato) returns tomato emoji', () {
      expect(_makeField(cropType: 'طماطم').cropEmoji, '🍅');
    });

    test('cucumber returns cucumber emoji', () {
      expect(_makeField(cropType: 'cucumber').cropEmoji, '🥒');
    });

    test('خيار (Arabic cucumber) returns cucumber emoji', () {
      expect(_makeField(cropType: 'خيار').cropEmoji, '🥒');
    });

    test('pepper returns pepper emoji', () {
      expect(_makeField(cropType: 'pepper').cropEmoji, '🌶️');
    });

    test('فلفل (Arabic pepper) returns pepper emoji', () {
      expect(_makeField(cropType: 'فلفل').cropEmoji, '🌶️');
    });

    test('onion returns onion emoji', () {
      expect(_makeField(cropType: 'onion').cropEmoji, '🧅');
    });

    test('بصل (Arabic onion) returns onion emoji', () {
      expect(_makeField(cropType: 'بصل').cropEmoji, '🧅');
    });

    test('unknown crop returns seedling emoji', () {
      expect(_makeField(cropType: 'rice').cropEmoji, '🌱');
    });

    test('empty crop returns seedling emoji', () {
      expect(_makeField(cropType: '').cropEmoji, '🌱');
    });

    test('case-insensitive matching for Wheat', () {
      expect(_makeField(cropType: 'Wheat').cropEmoji, '🌾');
    });

    test('case-insensitive matching for CORN', () {
      expect(_makeField(cropType: 'CORN').cropEmoji, '🌽');
    });

    test('case-insensitive matching for TOMATO', () {
      expect(_makeField(cropType: 'TOMATO').cropEmoji, '🍅');
    });

    test('case-insensitive matching for Potato', () {
      expect(_makeField(cropType: 'Potato').cropEmoji, '🥔');
    });
  });

  // ===========================================================================
  // FieldEntity - daysSincePlanting / daysUntilHarvest
  // ===========================================================================
  group('FieldEntity.daysSincePlanting', () {
    test('returns null when plantingDate is null', () {
      expect(_makeField(plantingDate: null).daysSincePlanting, isNull);
    });

    test('returns positive days for past planting date', () {
      final pastDate = DateTime.now().subtract(const Duration(days: 30));
      final days = _makeField(plantingDate: pastDate).daysSincePlanting;
      expect(days, isNotNull);
      expect(days!, closeTo(30, 1));
    });

    test('returns 0 for today planting date', () {
      final today = DateTime.now();
      final days = _makeField(plantingDate: today).daysSincePlanting;
      expect(days, isNotNull);
      expect(days!, closeTo(0, 1));
    });

    test('returns positive for planting 100 days ago', () {
      final pastDate = DateTime.now().subtract(const Duration(days: 100));
      final days = _makeField(plantingDate: pastDate).daysSincePlanting;
      expect(days!, closeTo(100, 1));
    });
  });

  group('FieldEntity.daysUntilHarvest', () {
    test('returns null when expectedHarvest is null', () {
      expect(_makeField(expectedHarvest: null).daysUntilHarvest, isNull);
    });

    test('returns positive days for future harvest', () {
      final futureDate = DateTime.now().add(const Duration(days: 60));
      final days = _makeField(expectedHarvest: futureDate).daysUntilHarvest;
      expect(days, isNotNull);
      expect(days!, closeTo(60, 1));
    });

    test('returns negative days for past harvest', () {
      final pastDate = DateTime.now().subtract(const Duration(days: 10));
      final days = _makeField(expectedHarvest: pastDate).daysUntilHarvest;
      expect(days, isNotNull);
      expect(days!, closeTo(-10, 1));
    });

    test('returns 0 for harvest today', () {
      final today = DateTime.now();
      final days = _makeField(expectedHarvest: today).daysUntilHarvest;
      expect(days!, closeTo(0, 1));
    });
  });

  // ===========================================================================
  // FieldEntity - copyWith
  // ===========================================================================
  group('FieldEntity.copyWith', () {
    test('returns identical values when no args given', () {
      final field = _makeField();
      final copy = field.copyWith();
      expect(copy.id, field.id);
      expect(copy.name, field.name);
      expect(copy.cropType, field.cropType);
      expect(copy.healthScore, field.healthScore);
    });

    test('updates name', () {
      final copy = _makeField().copyWith(name: 'New Name');
      expect(copy.name, 'New Name');
    });

    test('updates healthScore', () {
      final copy = _makeField().copyWith(healthScore: 0.99);
      expect(copy.healthScore, 0.99);
    });

    test('updates status', () {
      final copy = _makeField().copyWith(status: FieldStatus.harvested);
      expect(copy.status, FieldStatus.harvested);
    });

    test('updates cropType', () {
      final copy = _makeField().copyWith(cropType: 'tomato');
      expect(copy.cropType, 'tomato');
    });

    test('updates areaHectares', () {
      final copy = _makeField().copyWith(areaHectares: 25.5);
      expect(copy.areaHectares, 25.5);
    });

    test('updates center', () {
      const newCenter = GeoLocation(latitude: 50.0, longitude: 60.0);
      final copy = _makeField().copyWith(center: newCenter);
      expect(copy.center, newCenter);
    });

    test('updates ndviValue', () {
      final copy = _makeField().copyWith(ndviValue: 0.88);
      expect(copy.ndviValue, 0.88);
    });

    test('preserves other fields when updating one', () {
      final original = _makeField(
        farmId: 'farm-x',
        soilType: 'loam',
      );
      final copy = original.copyWith(name: 'Changed');
      expect(copy.farmId, 'farm-x');
      expect(copy.soilType, 'loam');
      expect(copy.name, 'Changed');
    });
  });

  // ===========================================================================
  // FieldEntity - equality
  // ===========================================================================
  group('FieldEntity equality', () {
    test('two entities with same id are equal', () {
      final a = _makeField(id: 'same-id', name: 'A');
      final b = _makeField(id: 'same-id', name: 'B');
      expect(a, b);
    });

    test('two entities with different ids are not equal', () {
      final a = _makeField(id: 'id-1');
      final b = _makeField(id: 'id-2');
      expect(a, isNot(b));
    });

    test('hashCode is consistent for same id', () {
      final a = _makeField(id: 'abc');
      final b = _makeField(id: 'abc');
      expect(a.hashCode, b.hashCode);
    });

    test('entity is not equal to non-FieldEntity', () {
      final field = _makeField();
      expect(field == 'not a field', isFalse);
    });

    test('entity is equal to itself (identical)', () {
      final field = _makeField();
      expect(field, field);
    });

    test('hashCode differs for different ids', () {
      final a = _makeField(id: 'id-aaa');
      final b = _makeField(id: 'id-bbb');
      // hashCodes could theoretically collide, but for these distinct strings they should not
      expect(a.hashCode, isNot(b.hashCode));
    });
  });

  // ===========================================================================
  // FieldEntity - toString
  // ===========================================================================
  group('FieldEntity.toString', () {
    test('contains id and name', () {
      final field = _makeField(id: 'xyz', name: 'My Plot');
      final str = field.toString();
      expect(str, contains('xyz'));
      expect(str, contains('My Plot'));
    });

    test('contains area in string', () {
      final field = _makeField(areaHectares: 12.5);
      expect(field.toString(), contains('12.50'));
    });
  });
}
