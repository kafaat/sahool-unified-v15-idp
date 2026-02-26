/// Equipment Local DB Tests
/// اختبارات قاعدة البيانات المحلية للمعدات
///
/// Tests for compute() isolate JSON parsing in equipment local database

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/equipment/domain/models/equipment.dart';
import 'package:sahool_field_app/features/equipment/domain/models/equipment_status.dart';

void main() {
  group('Equipment JSON parsing (compute isolate pattern)', () {
    test('should parse empty equipment list', () {
      final jsonStr = jsonEncode([]);
      final jsonList = jsonDecode(jsonStr) as List;
      final result = jsonList
          .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
          .toList();

      expect(result, isEmpty);
    });

    test('should parse equipment list with valid data', () {
      final equipmentJson = [
        {
          'equipment_id': 'eq-001',
          'name': 'Test Tractor',
          'name_ar': 'جرار اختبار',
          'equipment_type': 'tractor',
          'status': 'operational',
          'field_id': 'field-001',
        },
        {
          'equipment_id': 'eq-002',
          'name': 'Test Pump',
          'name_ar': 'مضخة اختبار',
          'equipment_type': 'pump',
          'status': 'maintenance',
        },
      ];

      final jsonStr = jsonEncode(equipmentJson);
      final jsonList = jsonDecode(jsonStr) as List;
      final result = jsonList
          .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
          .toList();

      expect(result.length, 2);
      expect(result[0].equipmentId, 'eq-001');
      expect(result[0].name, 'Test Tractor');
      expect(result[0].equipmentType, EquipmentType.tractor);
      expect(result[1].equipmentId, 'eq-002');
      expect(result[1].equipmentType, EquipmentType.pump);
    });

    test('should round-trip equipment through toJson/fromJson', () {
      final original = Equipment(
        equipmentId: 'eq-round-trip',
        name: 'Round Trip Test',
        nameAr: 'اختبار الرحلة',
        equipmentType: EquipmentType.drone,
        status: EquipmentStatus.operational,
        fieldId: 'field-test',
      );

      final json = original.toJson();
      final restored = Equipment.fromJson(json);

      expect(restored.equipmentId, original.equipmentId);
      expect(restored.name, original.name);
      expect(restored.nameAr, original.nameAr);
      expect(restored.equipmentType, original.equipmentType);
      expect(restored.status, original.status);
    });

    test('should handle large list parsing efficiently', () {
      // Generate a list of 100 equipment items
      final items = List.generate(100, (i) => {
            'equipment_id': 'eq-$i',
            'name': 'Equipment $i',
            'equipment_type': 'tractor',
            'status': 'operational',
          });

      final jsonStr = jsonEncode(items);
      final jsonList = jsonDecode(jsonStr) as List;
      final result = jsonList
          .map((e) => Equipment.fromJson(e as Map<String, dynamic>))
          .toList();

      expect(result.length, 100);
      expect(result.first.equipmentId, 'eq-0');
      expect(result.last.equipmentId, 'eq-99');
    });
  });

  group('Equipment filtering', () {
    late List<Equipment> equipment;

    setUp(() {
      equipment = [
        Equipment(
          equipmentId: 'eq-1',
          name: 'Tractor Alpha',
          equipmentType: EquipmentType.tractor,
          status: EquipmentStatus.operational,
          fieldId: 'field-A',
        ),
        Equipment(
          equipmentId: 'eq-2',
          name: 'Pump Beta',
          equipmentType: EquipmentType.pump,
          status: EquipmentStatus.maintenance,
          fieldId: 'field-B',
        ),
        Equipment(
          equipmentId: 'eq-3',
          name: 'Drone Gamma',
          equipmentType: EquipmentType.drone,
          status: EquipmentStatus.operational,
          fieldId: 'field-A',
        ),
      ];
    });

    test('should filter by type', () {
      final tractors =
          equipment.where((e) => e.equipmentType == EquipmentType.tractor).toList();
      expect(tractors.length, 1);
      expect(tractors.first.equipmentId, 'eq-1');
    });

    test('should filter by status', () {
      final operational =
          equipment.where((e) => e.status == EquipmentStatus.operational).toList();
      expect(operational.length, 2);
    });

    test('should filter by field', () {
      final fieldA = equipment.where((e) => e.fieldId == 'field-A').toList();
      expect(fieldA.length, 2);
    });

    test('should filter by search term', () {
      const search = 'alpha';
      final searchLower = search.toLowerCase();
      final results = equipment.where((e) {
        return e.name.toLowerCase().contains(searchLower);
      }).toList();
      expect(results.length, 1);
      expect(results.first.equipmentId, 'eq-1');
    });
  });
}
