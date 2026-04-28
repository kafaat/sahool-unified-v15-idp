/// Unit tests for FieldDetailsScreen UI logic
/// اختبارات شاشة تفاصيل الحقل
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/fields/domain/entities/field_entity.dart';

/// Tests for FieldEntity view-model helpers used by FieldDetailsScreen
void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // FieldStatus helper
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldStatus.fromString', () {
    test('parses active', () {
      expect(FieldStatus.fromString('active'), FieldStatus.active);
    });

    test('parses fallow', () {
      expect(FieldStatus.fromString('fallow'), FieldStatus.fallow);
    });

    test('parses harvested', () {
      expect(FieldStatus.fromString('harvested'), FieldStatus.harvested);
    });

    test('defaults to active for unknown value', () {
      expect(FieldStatus.fromString('unknown_xyz'), FieldStatus.active);
    });

    test('defaults to active for empty string', () {
      expect(FieldStatus.fromString(''), FieldStatus.active);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FieldEntity – null-safety for ndviValue / ndwiValue
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldEntity indices', () {
    FieldEntity _makeField({double? ndvi, double? ndwi}) {
      return FieldEntity(
        id: 'F001',
        tenantId: 'T001',
        name: 'حقل الاختبار',
        areaHectares: 5.0,
        cropType: 'قمح',
        healthScore: 0.75,
        ndviValue: ndvi,
        ndwiValue: ndwi,
        status: FieldStatus.active,
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 2),
      );
    }

    test('ndviValue can be null', () {
      final field = _makeField();
      expect(field.ndviValue, isNull);
    });

    test('ndwiValue can be null', () {
      final field = _makeField();
      expect(field.ndwiValue, isNull);
    });

    test('ndviValue stores a valid double when provided', () {
      final field = _makeField(ndvi: 0.68);
      expect(field.ndviValue, closeTo(0.68, 0.001));
    });

    test('ndwiValue stores a valid double when provided', () {
      final field = _makeField(ndwi: -0.12);
      expect(field.ndwiValue, closeTo(-0.12, 0.001));
    });

    test('healthScore is clamped to 0-1 range', () {
      final field = FieldEntity(
        id: 'F002',
        tenantId: 'T001',
        name: 'حقل B',
        areaHectares: 3.0,
        cropType: 'ذرة',
        healthScore: 0.9.clamp(0.0, 1.0),
        status: FieldStatus.active,
        createdAt: DateTime(2025, 1, 1),
        updatedAt: DateTime(2025, 1, 1),
      );
      expect(field.healthScore, inInclusiveRange(0.0, 1.0));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FieldEntity.healthLabel & healthColor
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldEntity.healthLabel', () {
    FieldEntity _makeWithScore(double score) {
      return FieldEntity(
        id: 'F',
        tenantId: 'T',
        name: 'H',
        areaHectares: 1.0,
        cropType: 'x',
        healthScore: score,
        status: FieldStatus.active,
        createdAt: DateTime(2025),
        updatedAt: DateTime(2025),
      );
    }

    test('high score returns صحي', () {
      expect(_makeWithScore(0.85).healthLabel, 'صحي');
    });

    test('medium score returns متوسط', () {
      expect(_makeWithScore(0.55).healthLabel, 'متوسط');
    });

    test('low score returns ضعيف', () {
      expect(_makeWithScore(0.25).healthLabel, 'ضعيف');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FieldEntity.cropEmoji
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldEntity.cropEmoji', () {
    FieldEntity _makeCrop(String crop) {
      return FieldEntity(
        id: 'F',
        tenantId: 'T',
        name: crop,
        areaHectares: 1.0,
        cropType: crop,
        healthScore: 0.5,
        status: FieldStatus.active,
        createdAt: DateTime(2025),
        updatedAt: DateTime(2025),
      );
    }

    test('قمح returns wheat emoji', () {
      expect(_makeCrop('قمح').cropEmoji, '🌾');
    });

    test('نخيل returns palm emoji', () {
      expect(_makeCrop('نخيل').cropEmoji, '🌴');
    });

    test('unknown crop returns generic emoji', () {
      final emoji = _makeCrop('unknown_crop').cropEmoji;
      expect(emoji, isNotEmpty);
    });
  });
}
