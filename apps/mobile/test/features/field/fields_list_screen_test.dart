/// Unit tests for FieldsListScreen logic helpers
/// اختبارات منطق شاشة قائمة الحقول
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/fields/domain/entities/field_entity.dart';

/// Helper to build a lightweight FieldEntity for tests
FieldEntity _field({
  required String id,
  required String cropType,
  String name = '',
  FieldStatus status = FieldStatus.active,
  double healthScore = 0.7,
  double ndvi = 0.6,
}) {
  return FieldEntity(
    id: id,
    tenantId: 'T001',
    name: name.isEmpty ? 'حقل $id' : name,
    areaHectares: 5.0,
    cropType: cropType,
    healthScore: healthScore,
    ndviValue: ndvi,
    status: status,
    createdAt: DateTime(2025, 1, 1),
    updatedAt: DateTime(2025, 1, 2),
  );
}

/// Mirrors the `_availableCropTypes` getter from FieldsListScreenState.
/// Extracted here to allow pure-unit testing without Flutter widgets.
Set<String> availableCropTypes(List<FieldEntity> fields) {
  return fields
      .map((f) => f.cropType)
      .where((c) => c.isNotEmpty && c != 'غير محدد')
      .toSet()
    ..removeAll(['']);
}

/// Mirrors the `_filteredFields` getter from FieldsListScreenState.
List<FieldEntity> filteredFields(
  List<FieldEntity> fields, {
  String searchQuery = '',
  String? selectedCrop,
  FieldStatus? selectedStatus,
}) {
  return fields.where((f) {
    final matchesSearch = searchQuery.isEmpty ||
        f.name.contains(searchQuery) ||
        f.cropType.contains(searchQuery);
    final matchesCrop = selectedCrop == null || f.cropType == selectedCrop;
    final matchesStatus = selectedStatus == null || f.status == selectedStatus;
    return matchesSearch && matchesCrop && matchesStatus;
  }).toList();
}

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // Dynamic crop filter chips
  // ═══════════════════════════════════════════════════════════════════════════

  group('_availableCropTypes', () {
    test('returns unique crop types from loaded fields', () {
      final fields = [
        _field(id: '1', cropType: 'قمح'),
        _field(id: '2', cropType: 'ذرة'),
        _field(id: '3', cropType: 'قمح'), // duplicate
      ];

      final crops = availableCropTypes(fields);

      expect(crops, hasLength(2));
      expect(crops, contains('قمح'));
      expect(crops, contains('ذرة'));
    });

    test('excludes غير محدد placeholder', () {
      final fields = [
        _field(id: '1', cropType: 'غير محدد'),
        _field(id: '2', cropType: 'قمح'),
      ];

      final crops = availableCropTypes(fields);

      expect(crops, isNot(contains('غير محدد')));
      expect(crops, contains('قمح'));
    });

    test('returns empty set for empty field list', () {
      expect(availableCropTypes([]), isEmpty);
    });

    test('returns empty set when all fields have غير محدد', () {
      final fields = [
        _field(id: '1', cropType: 'غير محدد'),
        _field(id: '2', cropType: 'غير محدد'),
      ];

      expect(availableCropTypes(fields), isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Search & filter logic
  // ═══════════════════════════════════════════════════════════════════════════

  group('_filteredFields – search', () {
    final fields = [
      _field(id: '1', cropType: 'قمح', name: 'حقل الشمال'),
      _field(id: '2', cropType: 'ذرة', name: 'حقل الجنوب'),
      _field(id: '3', cropType: 'نخيل', name: 'مزرعة النخيل'),
    ];

    test('empty query returns all fields', () {
      expect(filteredFields(fields), hasLength(3));
    });

    test('search by name returns matching field', () {
      final result = filteredFields(fields, searchQuery: 'شمال');
      expect(result, hasLength(1));
      expect(result.first.id, '1');
    });

    test('search by crop type returns matching fields', () {
      final result = filteredFields(fields, searchQuery: 'قمح');
      expect(result, hasLength(1));
      expect(result.first.id, '1');
    });

    test('no match returns empty list', () {
      expect(filteredFields(fields, searchQuery: 'xyz_no_match'), isEmpty);
    });
  });

  group('_filteredFields – crop filter', () {
    final fields = [
      _field(id: '1', cropType: 'قمح', name: 'حقل 1'),
      _field(id: '2', cropType: 'ذرة', name: 'حقل 2'),
      _field(id: '3', cropType: 'قمح', name: 'حقل 3'),
    ];

    test('null selectedCrop shows all fields', () {
      expect(filteredFields(fields, selectedCrop: null), hasLength(3));
    });

    test('selectedCrop filters to matching fields only', () {
      final result = filteredFields(fields, selectedCrop: 'قمح');
      expect(result, hasLength(2));
      expect(result.every((f) => f.cropType == 'قمح'), isTrue);
    });
  });

  group('_filteredFields – status filter', () {
    final fields = [
      _field(id: '1', cropType: 'قمح', status: FieldStatus.active),
      _field(id: '2', cropType: 'ذرة', status: FieldStatus.fallow),
      _field(id: '3', cropType: 'نخيل', status: FieldStatus.active),
    ];

    test('null status shows all fields', () {
      expect(filteredFields(fields, selectedStatus: null), hasLength(3));
    });

    test('active status shows only active fields', () {
      final result = filteredFields(fields, selectedStatus: FieldStatus.active);
      expect(result, hasLength(2));
    });

    test('fallow status shows only fallow fields', () {
      final result = filteredFields(fields, selectedStatus: FieldStatus.fallow);
      expect(result, hasLength(1));
      expect(result.first.id, '2');
    });
  });

  group('_filteredFields – combined search + crop filter', () {
    final fields = [
      _field(id: '1', cropType: 'قمح', name: 'الشمال'),
      _field(id: '2', cropType: 'قمح', name: 'الجنوب'),
      _field(id: '3', cropType: 'ذرة', name: 'الشمال'),
    ];

    test('applies both search and crop filter', () {
      final result = filteredFields(
        fields,
        searchQuery: 'شمال',
        selectedCrop: 'قمح',
      );
      expect(result, hasLength(1));
      expect(result.first.id, '1');
    });
  });
}
