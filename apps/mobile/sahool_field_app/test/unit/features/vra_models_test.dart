import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/vra/models/vra_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // VRAType enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('VRAType', () {
    test('has exactly 4 values', () {
      expect(VRAType.values.length, 4);
    });

    test('fertilizer has correct properties', () {
      expect(VRAType.fertilizer.value, 'fertilizer');
      expect(VRAType.fertilizer.nameAr, 'سماد');
      expect(VRAType.fertilizer.nameEn, 'Fertilizer');
    });

    test('seed has correct properties', () {
      expect(VRAType.seed.value, 'seed');
      expect(VRAType.seed.nameAr, 'بذور');
      expect(VRAType.seed.nameEn, 'Seed');
    });

    test('pesticide has correct properties', () {
      expect(VRAType.pesticide.value, 'pesticide');
      expect(VRAType.pesticide.nameAr, 'مبيد');
      expect(VRAType.pesticide.nameEn, 'Pesticide');
    });

    test('irrigation has correct properties', () {
      expect(VRAType.irrigation.value, 'irrigation');
      expect(VRAType.irrigation.nameAr, 'ري');
      expect(VRAType.irrigation.nameEn, 'Irrigation');
    });

    test('getName returns Arabic for ar locale', () {
      expect(VRAType.fertilizer.getName('ar'), 'سماد');
    });

    test('getName returns English for en locale', () {
      expect(VRAType.fertilizer.getName('en'), 'Fertilizer');
    });

    test('fromString returns correct type', () {
      expect(VRAType.fromString('fertilizer'), VRAType.fertilizer);
      expect(VRAType.fromString('seed'), VRAType.seed);
      expect(VRAType.fromString('pesticide'), VRAType.pesticide);
      expect(VRAType.fromString('irrigation'), VRAType.irrigation);
    });

    test('fromString returns fertilizer for unknown value', () {
      expect(VRAType.fromString('unknown'), VRAType.fertilizer);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PrescriptionStatus enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('PrescriptionStatus', () {
    test('has exactly 4 values', () {
      expect(PrescriptionStatus.values.length, 4);
    });

    test('draft has correct properties', () {
      expect(PrescriptionStatus.draft.value, 'draft');
      expect(PrescriptionStatus.draft.nameAr, 'مسودة');
      expect(PrescriptionStatus.draft.nameEn, 'Draft');
    });

    test('approved has correct properties', () {
      expect(PrescriptionStatus.approved.value, 'approved');
      expect(PrescriptionStatus.approved.nameAr, 'معتمد');
    });

    test('applied has correct properties', () {
      expect(PrescriptionStatus.applied.value, 'applied');
      expect(PrescriptionStatus.applied.nameAr, 'مطبق');
    });

    test('cancelled has correct properties', () {
      expect(PrescriptionStatus.cancelled.value, 'cancelled');
      expect(PrescriptionStatus.cancelled.nameAr, 'ملغي');
    });

    test('getName returns Arabic for ar locale', () {
      expect(PrescriptionStatus.draft.getName('ar'), 'مسودة');
    });

    test('getName returns English for en locale', () {
      expect(PrescriptionStatus.draft.getName('en'), 'Draft');
    });

    test('fromString returns correct status', () {
      expect(PrescriptionStatus.fromString('draft'), PrescriptionStatus.draft);
      expect(PrescriptionStatus.fromString('approved'),
          PrescriptionStatus.approved);
      expect(PrescriptionStatus.fromString('applied'),
          PrescriptionStatus.applied);
      expect(PrescriptionStatus.fromString('cancelled'),
          PrescriptionStatus.cancelled);
    });

    test('fromString returns draft for unknown value', () {
      expect(
          PrescriptionStatus.fromString('unknown'), PrescriptionStatus.draft);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ZoningMethod enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('ZoningMethod', () {
    test('has exactly 5 values', () {
      expect(ZoningMethod.values.length, 5);
    });

    test('manual has correct properties', () {
      expect(ZoningMethod.manual.value, 'manual');
      expect(ZoningMethod.manual.nameAr, 'يدوي');
      expect(ZoningMethod.manual.nameEn, 'Manual');
    });

    test('ndvi has correct properties', () {
      expect(ZoningMethod.ndvi.value, 'ndvi');
      expect(ZoningMethod.ndvi.nameEn, 'NDVI');
    });

    test('soilType has correct properties', () {
      expect(ZoningMethod.soilType.value, 'soil_type');
      expect(ZoningMethod.soilType.nameAr, 'نوع التربة');
    });

    test('elevation has correct properties', () {
      expect(ZoningMethod.elevation.value, 'elevation');
    });

    // ignore: deprecated_member_use
    test('yield has correct properties', () {
      // In Dart, 'yield' is used as an enum member name here.
      final yieldMethod = ZoningMethod.values
          .firstWhere((e) => e.value == 'yield');
      expect(yieldMethod.nameAr, 'الإنتاجية');
      expect(yieldMethod.nameEn, 'Yield');
    });

    test('fromString returns correct method', () {
      expect(ZoningMethod.fromString('manual'), ZoningMethod.manual);
      expect(ZoningMethod.fromString('ndvi'), ZoningMethod.ndvi);
      expect(ZoningMethod.fromString('soil_type'), ZoningMethod.soilType);
      expect(ZoningMethod.fromString('elevation'), ZoningMethod.elevation);
      expect(ZoningMethod.fromString('yield').value, 'yield');
    });

    test('fromString returns manual for unknown value', () {
      expect(ZoningMethod.fromString('unknown'), ZoningMethod.manual);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ManagementZone
  // ═══════════════════════════════════════════════════════════════════════════
  group('ManagementZone', () {
    Map<String, dynamic> makeZoneJson({String zoneId = 'z1'}) => {
          'zone_id': zoneId,
          'zone_number': 1,
          'name': 'Zone A',
          'name_ar': 'منطقة أ',
          'area': 5.0,
          'geometry': {
            'type': 'Polygon',
            'coordinates': [
              [
                [46.7, 24.7],
                [46.8, 24.7],
                [46.8, 24.8],
                [46.7, 24.7],
              ]
            ]
          },
          'average_ndvi': 0.65,
          'average_elevation': 120.5,
          'soil_type': 'Clay',
          'soil_type_ar': 'طينية',
          'properties': {'note': 'test'},
          'created_at': '2025-01-01T00:00:00.000Z',
          'updated_at': '2025-01-02T00:00:00.000Z',
        };

    test('fromJson creates correct instance', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      expect(zone.zoneId, 'z1');
      expect(zone.zoneNumber, 1);
      expect(zone.name, 'Zone A');
      expect(zone.nameAr, 'منطقة أ');
      expect(zone.area, 5.0);
      expect(zone.averageNdvi, 0.65);
      expect(zone.averageElevation, 120.5);
      expect(zone.soilType, 'Clay');
      expect(zone.soilTypeAr, 'طينية');
      expect(zone.properties, isNotNull);
    });

    test('getDisplayName returns Arabic for ar locale', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      expect(zone.getDisplayName('ar'), 'منطقة أ');
    });

    test('getDisplayName returns English for en locale', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      expect(zone.getDisplayName('en'), 'Zone A');
    });

    test('getDisplayName returns English when nameAr is null', () {
      final json = makeZoneJson();
      json.remove('name_ar');
      final zone = ManagementZone.fromJson(json);
      expect(zone.getDisplayName('ar'), 'Zone A');
    });

    test('getSoilType returns Arabic for ar locale', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      expect(zone.getSoilType('ar'), 'طينية');
    });

    test('getSoilType returns English for en locale', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      expect(zone.getSoilType('en'), 'Clay');
    });

    test('toJson produces correct map', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      final json = zone.toJson();
      expect(json['zone_id'], 'z1');
      expect(json['zone_number'], 1);
      expect(json['area'], 5.0);
    });

    test('fromJson/toJson roundtrip', () {
      final zone = ManagementZone.fromJson(makeZoneJson());
      final restored = ManagementZone.fromJson(zone.toJson());
      expect(restored.zoneId, zone.zoneId);
      expect(restored.area, zone.area);
      expect(restored.averageNdvi, zone.averageNdvi);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ApplicationRate
  // ═══════════════════════════════════════════════════════════════════════════
  group('ApplicationRate', () {
    Map<String, dynamic> makeRateJson({String zoneId = 'z1'}) => {
          'rate_id': 'r1',
          'zone_id': zoneId,
          'rate': 50.0,
          'unit': 'kg/ha',
          'unit_ar': 'كجم/هـ',
          'product_name': 'Urea',
          'product_name_ar': 'يوريا',
          'cost': 2.0,
          'notes': 'Apply morning',
          'notes_ar': 'تطبيق صباحي',
          'metadata': {'brand': 'AgriCo'},
        };

    test('fromJson creates correct instance', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.rateId, 'r1');
      expect(rate.zoneId, 'z1');
      expect(rate.rate, 50.0);
      expect(rate.unit, 'kg/ha');
      expect(rate.unitAr, 'كجم/هـ');
      expect(rate.productName, 'Urea');
      expect(rate.productNameAr, 'يوريا');
      expect(rate.cost, 2.0);
    });

    test('getTotalCost calculates correctly', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      // cost * rate * area = 2.0 * 50.0 * 5.0 = 500.0
      expect(rate.getTotalCost(5.0), 500.0);
    });

    test('getTotalCost returns null when cost is null', () {
      final json = makeRateJson();
      json.remove('cost');
      final rate = ApplicationRate.fromJson(json);
      expect(rate.getTotalCost(5.0), isNull);
    });

    test('getTotalCost with zero area returns zero', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getTotalCost(0.0), 0.0);
    });

    test('getProductName returns Arabic for ar locale', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getProductName('ar'), 'يوريا');
    });

    test('getProductName returns English for en locale', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getProductName('en'), 'Urea');
    });

    test('getUnit returns Arabic for ar locale', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getUnit('ar'), 'كجم/هـ');
    });

    test('getUnit returns English for en locale', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getUnit('en'), 'kg/ha');
    });

    test('getNotes returns Arabic for ar locale', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getNotes('ar'), 'تطبيق صباحي');
    });

    test('getNotes returns English for en locale', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      expect(rate.getNotes('en'), 'Apply morning');
    });

    test('toJson produces correct map', () {
      final rate = ApplicationRate.fromJson(makeRateJson());
      final json = rate.toJson();
      expect(json['rate_id'], 'r1');
      expect(json['rate'], 50.0);
      expect(json['cost'], 2.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VRAPrescription
  // ═══════════════════════════════════════════════════════════════════════════
  group('VRAPrescription', () {
    final zoneJson = {
      'zone_id': 'z1',
      'zone_number': 1,
      'name': 'Zone A',
      'area': 5.0,
      'geometry': {'type': 'Polygon', 'coordinates': []},
      'created_at': '2025-01-01T00:00:00.000Z',
      'updated_at': '2025-01-01T00:00:00.000Z',
    };

    final rateJson = {
      'rate_id': 'r1',
      'zone_id': 'z1',
      'rate': 50.0,
      'unit': 'kg/ha',
      'cost': 2.0,
    };

    Map<String, dynamic> makePrescriptionJson({
      String status = 'draft',
    }) =>
        {
          'prescription_id': 'p1',
          'tenant_id': 't1',
          'field_id': 'f1',
          'field_name': 'Field 1',
          'field_name_ar': 'حقل 1',
          'name': 'Spring Fertilizer',
          'name_ar': 'سماد الربيع',
          'vra_type': 'fertilizer',
          'status': status,
          'zoning_method': 'ndvi',
          'zones_count': 1,
          'total_area': 5.0,
          'zones': [zoneJson],
          'rates': [rateJson],
          'scheduled_date': '2025-04-01T00:00:00.000Z',
          'created_by': 'user1',
          'created_by_name': 'John',
          'notes': 'Spring application',
          'notes_ar': 'تطبيق الربيع',
          'created_at': '2025-01-01T00:00:00.000Z',
          'updated_at': '2025-01-02T00:00:00.000Z',
        };

    test('fromJson creates correct instance', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.prescriptionId, 'p1');
      expect(p.tenantId, 't1');
      expect(p.fieldId, 'f1');
      expect(p.fieldName, 'Field 1');
      expect(p.name, 'Spring Fertilizer');
      expect(p.vraType, VRAType.fertilizer);
      expect(p.status, PrescriptionStatus.draft);
      expect(p.zoningMethod, ZoningMethod.ndvi);
      expect(p.zonesCount, 1);
      expect(p.totalArea, 5.0);
      expect(p.zones.length, 1);
      expect(p.rates.length, 1);
    });

    test('isEditable returns true for draft status', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson(status: 'draft'));
      expect(p.isEditable, true);
    });

    test('isEditable returns false for approved status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'approved'));
      expect(p.isEditable, false);
    });

    test('isEditable returns false for applied status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'applied'));
      expect(p.isEditable, false);
    });

    test('isEditable returns false for cancelled status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'cancelled'));
      expect(p.isEditable, false);
    });

    test('canBeApproved returns true for draft status', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson(status: 'draft'));
      expect(p.canBeApproved, true);
    });

    test('canBeApproved returns false for approved status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'approved'));
      expect(p.canBeApproved, false);
    });

    test('canBeApplied returns true for approved status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'approved'));
      expect(p.canBeApplied, true);
    });

    test('canBeApplied returns false for draft status', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson(status: 'draft'));
      expect(p.canBeApplied, false);
    });

    test('canBeApplied returns false for applied status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'applied'));
      expect(p.canBeApplied, false);
    });

    test('isApplied returns true for applied status', () {
      final p =
          VRAPrescription.fromJson(makePrescriptionJson(status: 'applied'));
      expect(p.isApplied, true);
    });

    test('isApplied returns false for draft status', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson(status: 'draft'));
      expect(p.isApplied, false);
    });

    test('getTotalCost calculates from zones and rates', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      // rate=50, cost=2, area=5 => 2 * 50 * 5 = 500
      expect(p.getTotalCost(), 500.0);
    });

    test('getTotalCost returns 0 when rates have no cost', () {
      final json = makePrescriptionJson();
      (json['rates'] as List)[0] = {
        'rate_id': 'r1',
        'zone_id': 'z1',
        'rate': 50.0,
        'unit': 'kg/ha',
      };
      final p = VRAPrescription.fromJson(json);
      expect(p.getTotalCost(), 0.0);
    });

    test('getTotalQuantity calculates rate * area for all zones', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      // rate=50 * area=5 = 250
      expect(p.getTotalQuantity(), 250.0);
    });

    test('getAverageRate calculates totalQuantity / totalArea', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      // totalQuantity=250, totalArea=5 => 50
      expect(p.getAverageRate(), 50.0);
    });

    test('getAverageRate returns 0 when totalArea is 0', () {
      final json = makePrescriptionJson();
      json['total_area'] = 0;
      final p = VRAPrescription.fromJson(json);
      expect(p.getAverageRate(), 0.0);
    });

    test('getDisplayName returns Arabic for ar locale', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.getDisplayName('ar'), 'سماد الربيع');
    });

    test('getDisplayName returns English for en locale', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.getDisplayName('en'), 'Spring Fertilizer');
    });

    test('getFieldName returns Arabic for ar locale', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.getFieldName('ar'), 'حقل 1');
    });

    test('getFieldName returns English for en locale', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.getFieldName('en'), 'Field 1');
    });

    test('getNotes returns Arabic for ar locale', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.getNotes('ar'), 'تطبيق الربيع');
    });

    test('getNotes returns English for en locale', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      expect(p.getNotes('en'), 'Spring application');
    });

    test('toJson produces correct map', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      final json = p.toJson();
      expect(json['prescription_id'], 'p1');
      expect(json['vra_type'], 'fertilizer');
      expect(json['status'], 'draft');
      expect(json['zoning_method'], 'ndvi');
      expect(json['zones'], isA<List>());
      expect(json['rates'], isA<List>());
    });

    test('fromJson/toJson roundtrip', () {
      final p = VRAPrescription.fromJson(makePrescriptionJson());
      final json = p.toJson();
      final restored = VRAPrescription.fromJson(json);
      expect(restored.prescriptionId, p.prescriptionId);
      expect(restored.vraType, p.vraType);
      expect(restored.status, p.status);
      expect(restored.zones.length, p.zones.length);
      expect(restored.rates.length, p.rates.length);
    });

    test('fromJson handles missing optional dates', () {
      final json = makePrescriptionJson();
      json.remove('scheduled_date');
      json.remove('applied_date');
      json.remove('approved_at');
      final p = VRAPrescription.fromJson(json);
      expect(p.scheduledDate, isNull);
      expect(p.appliedDate, isNull);
      expect(p.approvedAt, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VRAStats
  // ═══════════════════════════════════════════════════════════════════════════
  group('VRAStats', () {
    test('fromJson creates correct instance', () {
      final json = {
        'total_prescriptions': 25,
        'draft_prescriptions': 5,
        'approved_prescriptions': 10,
        'applied_prescriptions': 10,
        'total_area_covered': 150.5,
        'total_cost': 75000.0,
        'by_type': {'fertilizer': 15, 'pesticide': 10},
      };
      final stats = VRAStats.fromJson(json);
      expect(stats.totalPrescriptions, 25);
      expect(stats.draftPrescriptions, 5);
      expect(stats.approvedPrescriptions, 10);
      expect(stats.appliedPrescriptions, 10);
      expect(stats.totalAreaCovered, 150.5);
      expect(stats.totalCost, 75000.0);
      expect(stats.byType['fertilizer'], 15);
      expect(stats.byType['pesticide'], 10);
    });

    test('fromJson handles empty byType map', () {
      final json = {
        'total_prescriptions': 0,
        'draft_prescriptions': 0,
        'approved_prescriptions': 0,
        'applied_prescriptions': 0,
        'total_area_covered': 0.0,
        'total_cost': 0.0,
        'by_type': <String, int>{},
      };
      final stats = VRAStats.fromJson(json);
      expect(stats.totalPrescriptions, 0);
      expect(stats.byType, isEmpty);
    });

    test('fromJson handles integer numeric values', () {
      final json = {
        'total_prescriptions': 10,
        'draft_prescriptions': 2,
        'approved_prescriptions': 3,
        'applied_prescriptions': 5,
        'total_area_covered': 100,
        'total_cost': 5000,
        'by_type': {'seed': 10},
      };
      final stats = VRAStats.fromJson(json);
      expect(stats.totalAreaCovered, 100.0);
      expect(stats.totalCost, 5000.0);
    });
  });
}
