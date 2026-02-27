/// Unit Tests for Equipment Feature - Extended Models
/// اختبارات وحدات المعدات - نماذج موسعة
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/equipment/domain/models/equipment.dart';
import 'package:sahool_field_app/features/equipment/domain/models/equipment_status.dart';
import 'package:sahool_field_app/features/equipment/domain/models/fuel_log.dart';
import 'package:sahool_field_app/features/equipment/domain/models/maintenance_record.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // Equipment Extended Tests (beyond existing equipment_models_test.dart)
  // ═══════════════════════════════════════════════════════════════════════════

  group('Equipment - Extended Tests', () {
    late Equipment equipment;

    setUp(() {
      equipment = Equipment(
        equipmentId: 'EQ001',
        tenantId: 'tenant-1',
        name: 'John Deere 8R',
        nameAr: 'جون دير 8R',
        equipmentType: EquipmentType.tractor,
        status: EquipmentStatus.operational,
        brand: 'John Deere',
        model: '8R 410',
        year: 2022,
        purchasePrice: 350000.0,
        currentFuelPercent: 75.0,
        currentHours: 1250.0,
        currentLat: 24.75,
        currentLon: 46.73,
        nextMaintenanceAt: DateTime.now().add(const Duration(days: 5)),
        createdAt: DateTime(2024, 1, 1),
        updatedAt: DateTime(2024, 6, 1),
      );
    });

    test('getFuelLevelCategory returns correct categories', () {
      // Full
      final full = equipment.copyWith(currentFuelPercent: 80.0);
      expect(full.getFuelLevelCategory('en'), 'Full');
      expect(full.getFuelLevelCategory('ar'), 'ممتلئ');

      // Good
      final good = equipment.copyWith(currentFuelPercent: 55.0);
      expect(good.getFuelLevelCategory('en'), 'Good');
      expect(good.getFuelLevelCategory('ar'), 'جيد');

      // Medium
      final medium = equipment.copyWith(currentFuelPercent: 30.0);
      expect(medium.getFuelLevelCategory('en'), 'Medium');
      expect(medium.getFuelLevelCategory('ar'), 'متوسط');

      // Low
      final low = equipment.copyWith(currentFuelPercent: 15.0);
      expect(low.getFuelLevelCategory('en'), 'Low');
      expect(low.getFuelLevelCategory('ar'), 'منخفض');

      // Critical
      final critical = equipment.copyWith(currentFuelPercent: 5.0);
      expect(critical.getFuelLevelCategory('en'), 'Critical');
      expect(critical.getFuelLevelCategory('ar'), 'حرج');
    });

    test('getFuelLevelCategory returns Unknown for null fuel', () {
      final noFuel = Equipment(
        equipmentId: 'EQ-NF',
        tenantId: 'tenant-1',
        name: 'Test',
        equipmentType: EquipmentType.sensor,
        status: EquipmentStatus.operational,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(noFuel.getFuelLevelCategory('en'), 'Unknown');
      expect(noFuel.getFuelLevelCategory('ar'), 'غير معروف');
    });

    test('hasLocation returns true when lat/lon set', () {
      expect(equipment.hasLocation, true);
    });

    test('hasLocation returns false when lat/lon null', () {
      final noLocation = Equipment(
        equipmentId: 'EQ-NL',
        tenantId: 'tenant-1',
        name: 'Test',
        equipmentType: EquipmentType.pump,
        status: EquipmentStatus.operational,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(noLocation.hasLocation, false);
    });

    test('locationString formats correctly', () {
      expect(equipment.locationString, '24.750000, 46.730000');
    });

    test('locationString returns empty for no location', () {
      final noLoc = Equipment(
        equipmentId: 'EQ-NL',
        tenantId: 'tenant-1',
        name: 'Test',
        equipmentType: EquipmentType.pump,
        status: EquipmentStatus.operational,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(noLoc.locationString, '');
    });

    test('ageInYears calculates correctly', () {
      expect(equipment.ageInYears, DateTime.now().year - 2022);
    });

    test('ageInYears returns non-null when year is set', () {
      // copyWith(year: null) retains the original value due to ?? operator
      expect(equipment.ageInYears, DateTime.now().year - 2022);
    });

    test('ageInYears returns null for equipment created without year', () {
      final noYear = Equipment(
        equipmentId: 'eq-no-year',
        tenantId: 'tenant-1',
        name: 'No Year Equipment',
        equipmentType: EquipmentType.pump,
        status: EquipmentStatus.operational,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(noYear.ageInYears, isNull);
    });

    test('currentValue calculates depreciation correctly', () {
      // Equipment bought in 2022, purchase price 350000, age varies
      final value = equipment.currentValue;
      expect(value, isNotNull);
      expect(value!, greaterThan(0));
      expect(value, lessThanOrEqualTo(350000.0));
    });

    test('currentValue returns null when created without price', () {
      final noPrice = Equipment(
        equipmentId: 'eq-no-price',
        tenantId: 'tenant-1',
        name: 'No Price Equipment',
        equipmentType: EquipmentType.pump,
        status: EquipmentStatus.operational,
        year: 2022,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(noPrice.currentValue, isNull);
    });

    test('isCriticalFuel returns true below 10%', () {
      final critical = equipment.copyWith(currentFuelPercent: 8.0);
      expect(critical.isCriticalFuel, true);
    });

    test('isCriticalFuel returns false at 10% or above', () {
      final ok = equipment.copyWith(currentFuelPercent: 10.0);
      expect(ok.isCriticalFuel, false);
    });

    test('isMaintenanceOverdue based on date', () {
      final overdue = equipment.copyWith(
        nextMaintenanceAt: DateTime.now().subtract(const Duration(days: 1)),
      );
      expect(overdue.isMaintenanceOverdue, true);

      final notOverdue = equipment.copyWith(
        nextMaintenanceAt: DateTime.now().add(const Duration(days: 30)),
      );
      expect(notOverdue.isMaintenanceOverdue, false);
    });

    test('isMaintenanceOverdue based on hours', () {
      // Create equipment without nextMaintenanceAt to test hours-based check
      final overdue = Equipment(
        equipmentId: 'eq-hours',
        tenantId: 'tenant-1',
        name: 'Hours Equipment',
        equipmentType: EquipmentType.pump,
        status: EquipmentStatus.operational,
        currentHours: 1500.0,
        nextMaintenanceHours: 1400.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );
      expect(overdue.isMaintenanceOverdue, true);
    });

    test('fromJson round-trips via toJson', () {
      final json = equipment.toJson();
      final roundTripped = Equipment.fromJson(json);

      expect(roundTripped.equipmentId, equipment.equipmentId);
      expect(roundTripped.name, equipment.name);
      expect(roundTripped.nameAr, equipment.nameAr);
      expect(roundTripped.equipmentType, equipment.equipmentType);
      expect(roundTripped.status, equipment.status);
      expect(roundTripped.currentFuelPercent, equipment.currentFuelPercent);
    });

    test('equality is based on equipmentId', () {
      final copy = equipment.copyWith(name: 'Different Name');
      expect(equipment, equals(copy));
    });

    test('hashCode is based on equipmentId', () {
      final copy = equipment.copyWith(name: 'Different');
      expect(equipment.hashCode, copy.hashCode);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EquipmentType Extended Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('EquipmentType - Extended', () {
    test('getName returns locale-appropriate name', () {
      expect(EquipmentType.tractor.getName('ar'), 'جرار');
      expect(EquipmentType.tractor.getName('en'), 'Tractor');
      expect(EquipmentType.drone.getName('ar'), 'طائرة مسيرة');
      expect(EquipmentType.drone.getName('en'), 'Drone');
    });

    test('iconName returns correct icon for each type', () {
      expect(EquipmentType.tractor.iconName, 'agriculture');
      expect(EquipmentType.pump.iconName, 'water');
      expect(EquipmentType.drone.iconName, 'flight');
      expect(EquipmentType.sensor.iconName, 'sensors');
      expect(EquipmentType.vehicle.iconName, 'local_shipping');
      expect(EquipmentType.iotDevice.iconName, 'router');
      expect(EquipmentType.other.iconName, 'build');
    });

    test('fromString handles all known types', () {
      expect(EquipmentType.fromString('tractor'), EquipmentType.tractor);
      expect(EquipmentType.fromString('pump'), EquipmentType.pump);
      expect(EquipmentType.fromString('drone'), EquipmentType.drone);
      expect(EquipmentType.fromString('harvester'), EquipmentType.harvester);
      expect(EquipmentType.fromString('sprayer'), EquipmentType.sprayer);
      expect(EquipmentType.fromString('pivot'), EquipmentType.pivot);
      expect(EquipmentType.fromString('sensor'), EquipmentType.sensor);
      expect(EquipmentType.fromString('vehicle'), EquipmentType.vehicle);
      expect(EquipmentType.fromString('iot_device'), EquipmentType.iotDevice);
    });

    test('fromString defaults to other for unknown', () {
      expect(EquipmentType.fromString('invalid'), EquipmentType.other);
      expect(EquipmentType.fromString(''), EquipmentType.other);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EquipmentStatus Extended Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('EquipmentStatus - Extended', () {
    test('isAvailable returns true for operational and standby', () {
      expect(EquipmentStatus.operational.isAvailable, true);
      expect(EquipmentStatus.standby.isAvailable, true);
    });

    test('isAvailable returns false for other statuses', () {
      expect(EquipmentStatus.maintenance.isAvailable, false);
      expect(EquipmentStatus.inactive.isAvailable, false);
      expect(EquipmentStatus.repair.isAvailable, false);
      expect(EquipmentStatus.inUse.isAvailable, false);
    });

    test('fromString handles all known statuses', () {
      expect(EquipmentStatus.fromString('operational'), EquipmentStatus.operational);
      expect(EquipmentStatus.fromString('maintenance'), EquipmentStatus.maintenance);
      expect(EquipmentStatus.fromString('inactive'), EquipmentStatus.inactive);
      expect(EquipmentStatus.fromString('repair'), EquipmentStatus.repair);
      expect(EquipmentStatus.fromString('standby'), EquipmentStatus.standby);
      expect(EquipmentStatus.fromString('in_use'), EquipmentStatus.inUse);
    });

    test('fromString defaults to inactive for unknown', () {
      expect(EquipmentStatus.fromString('invalid'), EquipmentStatus.inactive);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FuelType Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FuelType', () {
    test('getName returns locale-appropriate name', () {
      expect(FuelType.diesel.getName('ar'), 'ديزل');
      expect(FuelType.diesel.getName('en'), 'Diesel');
      expect(FuelType.electric.getName('ar'), 'كهربائي');
      expect(FuelType.electric.getName('en'), 'Electric');
    });

    test('fromString handles all types', () {
      expect(FuelType.fromString('diesel'), FuelType.diesel);
      expect(FuelType.fromString('gasoline'), FuelType.gasoline);
      expect(FuelType.fromString('electric'), FuelType.electric);
      expect(FuelType.fromString('hybrid'), FuelType.hybrid);
      expect(FuelType.fromString('lpg'), FuelType.lpg);
      expect(FuelType.fromString('none'), FuelType.none);
    });

    test('fromString defaults to diesel for unknown', () {
      expect(FuelType.fromString('unknown'), FuelType.diesel);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FuelOperationType Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FuelOperationType', () {
    test('getName returns locale-appropriate name', () {
      expect(FuelOperationType.refuel.getName('ar'), 'تعبئة');
      expect(FuelOperationType.refuel.getName('en'), 'Refuel');
      expect(FuelOperationType.consumption.getName('ar'), 'استهلاك');
      expect(FuelOperationType.leak.getName('ar'), 'تسرب');
    });

    test('fromString handles all types', () {
      expect(FuelOperationType.fromString('refuel'), FuelOperationType.refuel);
      expect(FuelOperationType.fromString('consumption'), FuelOperationType.consumption);
      expect(FuelOperationType.fromString('transfer'), FuelOperationType.transfer);
      expect(FuelOperationType.fromString('adjustment'), FuelOperationType.adjustment);
      expect(FuelOperationType.fromString('leak'), FuelOperationType.leak);
    });

    test('fromString defaults to refuel for unknown', () {
      expect(FuelOperationType.fromString('invalid'), FuelOperationType.refuel);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FuelLog Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FuelLog', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'log_id': 'FL-001',
        'equipment_id': 'EQ001',
        'operation_type': 'refuel',
        'fuel_type': 'diesel',
        'quantity': 150.0,
        'price_per_liter': 2.18,
        'total_cost': 327.0,
        'currency': 'SAR',
        'odometer_reading': 1250.0,
        'fuel_level_before': 10.0,
        'fuel_level_after': 75.0,
        'station_name': 'ARAMCO Station',
        'receipt_number': 'RCT-12345',
        'notes': 'Regular refuel',
        'notes_ar': 'تعبئة عادية',
        'timestamp': '2025-06-15T08:00:00Z',
        'created_at': '2025-06-15T08:00:00Z',
        'created_by': 'user-001',
        'lat': 24.75,
        'lon': 46.73,
      };

      // Act
      final log = FuelLog.fromJson(json);

      // Assert
      expect(log.logId, 'FL-001');
      expect(log.equipmentId, 'EQ001');
      expect(log.operationType, FuelOperationType.refuel);
      expect(log.fuelType, FuelType.diesel);
      expect(log.quantity, 150.0);
      expect(log.pricePerLiter, 2.18);
      expect(log.totalCost, 327.0);
      expect(log.currency, 'SAR');
      expect(log.stationName, 'ARAMCO Station');
      expect(log.hasLocation, true);
    });

    test('calculatedCost uses totalCost when present', () {
      final log = FuelLog(
        logId: 'FL-002',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.refuel,
        quantity: 100.0,
        pricePerLiter: 2.0,
        totalCost: 250.0, // Discounted
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.calculatedCost, 250.0);
    });

    test('calculatedCost calculates from price when no totalCost', () {
      final log = FuelLog(
        logId: 'FL-003',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.refuel,
        quantity: 100.0,
        pricePerLiter: 2.18,
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.calculatedCost, closeTo(218.0, 0.01));
    });

    test('calculatedCost returns 0 when no price info', () {
      final log = FuelLog(
        logId: 'FL-004',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.consumption,
        quantity: 50.0,
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.calculatedCost, 0);
    });

    test('formattedCost shows dash when zero', () {
      final log = FuelLog(
        logId: 'FL-005',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.consumption,
        quantity: 50.0,
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.formattedCost, '-');
    });

    test('formattedCost shows amount with currency', () {
      final log = FuelLog(
        logId: 'FL-006',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.refuel,
        quantity: 100.0,
        totalCost: 218.50,
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.formattedCost, '218.50 SAR');
    });

    test('formattedQuantity shows liters', () {
      final log = FuelLog(
        logId: 'FL-007',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.refuel,
        quantity: 150.5,
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.formattedQuantity, '150.5 L');
    });

    test('getNotes returns locale-appropriate notes', () {
      final log = FuelLog(
        logId: 'FL-008',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.refuel,
        quantity: 100.0,
        notes: 'Regular fill',
        notesAr: 'تعبئة عادية',
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.getNotes('ar'), 'تعبئة عادية');
      expect(log.getNotes('en'), 'Regular fill');
    });

    test('getNotes returns null when both notes are null', () {
      final log = FuelLog(
        logId: 'FL-009',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.refuel,
        quantity: 100.0,
        timestamp: DateTime.now(),
        createdAt: DateTime.now(),
      );

      expect(log.getNotes('ar'), isNull);
    });

    test('toJson round-trips via fromJson', () {
      final original = FuelLog(
        logId: 'FL-010',
        equipmentId: 'EQ001',
        operationType: FuelOperationType.transfer,
        fuelType: FuelType.gasoline,
        quantity: 80.0,
        pricePerLiter: 2.5,
        totalCost: 200.0,
        timestamp: DateTime.utc(2025, 6, 15),
        createdAt: DateTime.utc(2025, 6, 15),
      );

      final json = original.toJson();
      final restored = FuelLog.fromJson(json);

      expect(restored.logId, original.logId);
      expect(restored.operationType, original.operationType);
      expect(restored.fuelType, FuelType.gasoline);
      expect(restored.quantity, original.quantity);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FuelConsumptionSummary Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FuelConsumptionSummary', () {
    test('costPerHour calculates correctly', () {
      final summary = FuelConsumptionSummary(
        equipmentId: 'EQ001',
        totalFuelConsumed: 500.0,
        totalCost: 1090.0,
        averageConsumptionPerHour: 12.5,
        averagePricePerLiter: 2.18,
        refuelCount: 5,
        totalHoursOperated: 40.0,
        periodStart: DateTime(2025, 6, 1),
        periodEnd: DateTime(2025, 6, 30),
      );

      expect(summary.costPerHour, closeTo(27.25, 0.01));
    });

    test('costPerHour returns 0 when no hours operated', () {
      final summary = FuelConsumptionSummary(
        equipmentId: 'EQ001',
        totalFuelConsumed: 0,
        totalCost: 0,
        averageConsumptionPerHour: 0,
        averagePricePerLiter: 0,
        refuelCount: 0,
        totalHoursOperated: 0,
        periodStart: DateTime(2025, 6, 1),
        periodEnd: DateTime(2025, 6, 30),
      );

      expect(summary.costPerHour, 0);
    });

    test('efficiencyRating returns correct star rating', () {
      // 5 stars: <= 8 L/hr
      expect(
        FuelConsumptionSummary(
          equipmentId: 'EQ', totalFuelConsumed: 0, totalCost: 0,
          averageConsumptionPerHour: 7.0, averagePricePerLiter: 0,
          refuelCount: 0, totalHoursOperated: 0,
          periodStart: DateTime.now(), periodEnd: DateTime.now(),
        ).efficiencyRating,
        5,
      );

      // 4 stars: <= 12 L/hr
      expect(
        FuelConsumptionSummary(
          equipmentId: 'EQ', totalFuelConsumed: 0, totalCost: 0,
          averageConsumptionPerHour: 10.0, averagePricePerLiter: 0,
          refuelCount: 0, totalHoursOperated: 0,
          periodStart: DateTime.now(), periodEnd: DateTime.now(),
        ).efficiencyRating,
        4,
      );

      // 3 stars: <= 15 L/hr
      expect(
        FuelConsumptionSummary(
          equipmentId: 'EQ', totalFuelConsumed: 0, totalCost: 0,
          averageConsumptionPerHour: 14.0, averagePricePerLiter: 0,
          refuelCount: 0, totalHoursOperated: 0,
          periodStart: DateTime.now(), periodEnd: DateTime.now(),
        ).efficiencyRating,
        3,
      );

      // 2 stars: <= 20 L/hr
      expect(
        FuelConsumptionSummary(
          equipmentId: 'EQ', totalFuelConsumed: 0, totalCost: 0,
          averageConsumptionPerHour: 18.0, averagePricePerLiter: 0,
          refuelCount: 0, totalHoursOperated: 0,
          periodStart: DateTime.now(), periodEnd: DateTime.now(),
        ).efficiencyRating,
        2,
      );

      // 1 star: > 20 L/hr
      expect(
        FuelConsumptionSummary(
          equipmentId: 'EQ', totalFuelConsumed: 0, totalCost: 0,
          averageConsumptionPerHour: 25.0, averagePricePerLiter: 0,
          refuelCount: 0, totalHoursOperated: 0,
          periodStart: DateTime.now(), periodEnd: DateTime.now(),
        ).efficiencyRating,
        1,
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FuelAlert Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FuelAlert', () {
    test('isCritical returns true below 10%', () {
      final alert = FuelAlert(
        alertId: 'FA-001',
        equipmentId: 'EQ001',
        equipmentName: 'Tractor 1',
        currentFuelPercent: 8.0,
        threshold: 20.0,
        message: 'Critical fuel level',
        createdAt: DateTime.now(),
      );

      expect(alert.isCritical, true);
    });

    test('isCritical returns false at 10% or above', () {
      final alert = FuelAlert(
        alertId: 'FA-002',
        equipmentId: 'EQ001',
        equipmentName: 'Tractor 1',
        currentFuelPercent: 15.0,
        threshold: 20.0,
        message: 'Low fuel level',
        createdAt: DateTime.now(),
      );

      expect(alert.isCritical, false);
    });

    test('getMessage returns locale-appropriate message', () {
      final alert = FuelAlert(
        alertId: 'FA-003',
        equipmentId: 'EQ001',
        equipmentName: 'Tractor',
        currentFuelPercent: 5.0,
        threshold: 20.0,
        message: 'Fuel critical',
        messageAr: 'مستوى الوقود حرج',
        createdAt: DateTime.now(),
      );

      expect(alert.getMessage('ar'), 'مستوى الوقود حرج');
      expect(alert.getMessage('en'), 'Fuel critical');
    });

    test('fromJson round-trips via toJson', () {
      final json = {
        'alert_id': 'FA-004',
        'equipment_id': 'EQ001',
        'equipment_name': 'Tractor 1',
        'current_fuel_percent': 12.0,
        'threshold': 20.0,
        'message': 'Low fuel',
        'message_ar': 'وقود منخفض',
        'created_at': '2025-06-15T10:00:00Z',
        'is_acknowledged': true,
      };

      final alert = FuelAlert.fromJson(json);
      final roundTripped = FuelAlert.fromJson(alert.toJson());

      expect(roundTripped.alertId, 'FA-004');
      expect(roundTripped.currentFuelPercent, 12.0);
      expect(roundTripped.isAcknowledged, true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MaintenanceType Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MaintenanceType', () {
    test('fromString handles all known types', () {
      expect(MaintenanceType.fromString('oil_change'), MaintenanceType.oilChange);
      expect(MaintenanceType.fromString('filter_change'), MaintenanceType.filterChange);
      expect(MaintenanceType.fromString('tire_check'), MaintenanceType.tireCheck);
      expect(MaintenanceType.fromString('battery_check'), MaintenanceType.batteryCheck);
      expect(MaintenanceType.fromString('calibration'), MaintenanceType.calibration);
      expect(MaintenanceType.fromString('general_service'), MaintenanceType.generalService);
      expect(MaintenanceType.fromString('repair'), MaintenanceType.repair);
      expect(MaintenanceType.fromString('inspection'), MaintenanceType.inspection);
      expect(MaintenanceType.fromString('cleaning'), MaintenanceType.cleaning);
      expect(MaintenanceType.fromString('part_replacement'), MaintenanceType.partReplacement);
      expect(MaintenanceType.fromString('software_update'), MaintenanceType.softwareUpdate);
    });

    test('fromString defaults to other', () {
      expect(MaintenanceType.fromString('invalid'), MaintenanceType.other);
    });

    test('recommendedIntervalHours returns correct intervals', () {
      expect(MaintenanceType.oilChange.recommendedIntervalHours, 250);
      expect(MaintenanceType.filterChange.recommendedIntervalHours, 500);
      expect(MaintenanceType.tireCheck.recommendedIntervalHours, 100);
      expect(MaintenanceType.batteryCheck.recommendedIntervalHours, 200);
      expect(MaintenanceType.cleaning.recommendedIntervalHours, 50);
    });

    test('recommendedIntervalHours returns null for non-scheduled types', () {
      expect(MaintenanceType.repair.recommendedIntervalHours, isNull);
      expect(MaintenanceType.partReplacement.recommendedIntervalHours, isNull);
      expect(MaintenanceType.softwareUpdate.recommendedIntervalHours, isNull);
      expect(MaintenanceType.other.recommendedIntervalHours, isNull);
    });

    test('getName returns correct locale name', () {
      expect(MaintenanceType.oilChange.getName('ar'), 'تغيير زيت');
      expect(MaintenanceType.oilChange.getName('en'), 'Oil Change');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MaintenanceStatus Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MaintenanceStatus', () {
    test('fromString handles all statuses', () {
      expect(MaintenanceStatus.fromString('scheduled'), MaintenanceStatus.scheduled);
      expect(MaintenanceStatus.fromString('in_progress'), MaintenanceStatus.inProgress);
      expect(MaintenanceStatus.fromString('completed'), MaintenanceStatus.completed);
      expect(MaintenanceStatus.fromString('cancelled'), MaintenanceStatus.cancelled);
      expect(MaintenanceStatus.fromString('overdue'), MaintenanceStatus.overdue);
    });

    test('fromString defaults to scheduled', () {
      expect(MaintenanceStatus.fromString('invalid'), MaintenanceStatus.scheduled);
    });

    test('getName returns correct locale name', () {
      expect(MaintenanceStatus.inProgress.getName('ar'), 'قيد التنفيذ');
      expect(MaintenanceStatus.inProgress.getName('en'), 'In Progress');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MaintenanceRecord Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MaintenanceRecord', () {
    test('fromJson parses all fields', () {
      final json = {
        'record_id': 'MR-001',
        'equipment_id': 'EQ001',
        'maintenance_type': 'oil_change',
        'status': 'completed',
        'description': 'Oil and filter change',
        'description_ar': 'تغيير زيت وفلتر',
        'performed_by': 'Ahmed',
        'cost': 450.0,
        'currency': 'SAR',
        'notes': 'Used synthetic oil',
        'notes_ar': 'استخدم زيت صناعي',
        'parts_replaced': ['Oil filter', 'O-ring'],
        'parts_replaced_ar': ['فلتر زيت', 'حلقة مطاطية'],
        'hours_at_maintenance': 1250.0,
        'scheduled_at': '2025-06-10T08:00:00Z',
        'performed_at': '2025-06-15T08:00:00Z',
        'completed_at': '2025-06-15T10:00:00Z',
        'created_at': '2025-06-10T08:00:00Z',
        'updated_at': '2025-06-15T10:00:00Z',
      };

      final record = MaintenanceRecord.fromJson(json);

      expect(record.recordId, 'MR-001');
      expect(record.maintenanceType, MaintenanceType.oilChange);
      expect(record.status, MaintenanceStatus.completed);
      expect(record.cost, 450.0);
      expect(record.formattedCost, '450.00 SAR');
      expect(record.partsReplaced, hasLength(2));
    });

    test('isOverdue returns true for past scheduled maintenance', () {
      final record = MaintenanceRecord(
        recordId: 'MR-002',
        equipmentId: 'EQ001',
        maintenanceType: MaintenanceType.filterChange,
        status: MaintenanceStatus.scheduled,
        description: 'Filter change',
        scheduledAt: DateTime.now().subtract(const Duration(days: 1)),
        createdAt: DateTime(2025, 6, 1),
        updatedAt: DateTime(2025, 6, 1),
      );

      expect(record.isOverdue, true);
    });

    test('isOverdue returns true when status is overdue', () {
      final record = MaintenanceRecord(
        recordId: 'MR-003',
        equipmentId: 'EQ001',
        maintenanceType: MaintenanceType.inspection,
        status: MaintenanceStatus.overdue,
        description: 'Inspection',
        createdAt: DateTime(2025, 6, 1),
        updatedAt: DateTime(2025, 6, 1),
      );

      expect(record.isOverdue, true);
    });

    test('duration calculates time between performed and completed', () {
      final record = MaintenanceRecord(
        recordId: 'MR-004',
        equipmentId: 'EQ001',
        maintenanceType: MaintenanceType.generalService,
        description: 'Service',
        performedAt: DateTime(2025, 6, 15, 8, 0),
        completedAt: DateTime(2025, 6, 15, 10, 30),
        createdAt: DateTime(2025, 6, 15),
        updatedAt: DateTime(2025, 6, 15),
      );

      expect(record.duration, const Duration(hours: 2, minutes: 30));
    });

    test('duration returns null when dates missing', () {
      final record = MaintenanceRecord(
        recordId: 'MR-005',
        equipmentId: 'EQ001',
        maintenanceType: MaintenanceType.generalService,
        description: 'Service',
        createdAt: DateTime(2025, 6, 15),
        updatedAt: DateTime(2025, 6, 15),
      );

      expect(record.duration, isNull);
    });

    test('formattedCost returns dash when no cost', () {
      final record = MaintenanceRecord(
        recordId: 'MR-006',
        equipmentId: 'EQ001',
        maintenanceType: MaintenanceType.inspection,
        description: 'Inspection',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.formattedCost, '-');
    });

    test('getDescription returns locale-appropriate text', () {
      final record = MaintenanceRecord(
        recordId: 'MR-007',
        equipmentId: 'EQ001',
        maintenanceType: MaintenanceType.oilChange,
        description: 'Oil change',
        descriptionAr: 'تغيير الزيت',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.getDescription('ar'), 'تغيير الزيت');
      expect(record.getDescription('en'), 'Oil change');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MaintenancePriority Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('MaintenancePriority', () {
    test('level returns correct numeric level', () {
      expect(MaintenancePriority.low.level, 1);
      expect(MaintenancePriority.medium.level, 2);
      expect(MaintenancePriority.high.level, 3);
      expect(MaintenancePriority.critical.level, 4);
    });

    test('fromString defaults to low for unknown', () {
      expect(MaintenancePriority.fromString('invalid'), MaintenancePriority.low);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EquipmentAlert Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('EquipmentAlert', () {
    test('fromJson parses correctly', () {
      final json = {
        'alert_id': 'EA-001',
        'equipment_id': 'EQ001',
        'equipment_name': 'Tractor 1',
        'alert_type': 'maintenance',
        'priority': 'high',
        'title': 'Maintenance Due',
        'title_ar': 'موعد الصيانة',
        'message': 'Oil change overdue',
        'message_ar': 'تغيير الزيت متأخر',
        'is_read': false,
        'is_dismissed': false,
        'created_at': '2025-06-15T10:00:00Z',
      };

      final alert = EquipmentAlert.fromJson(json);

      expect(alert.alertId, 'EA-001');
      expect(alert.alertType, AlertType.maintenance);
      expect(alert.priority, MaintenancePriority.high);
      expect(alert.getTitle('ar'), 'موعد الصيانة');
      expect(alert.getMessage('ar'), 'تغيير الزيت متأخر');
      expect(alert.isRead, false);
    });

    test('copyWith updates read status', () {
      final alert = EquipmentAlert(
        alertId: 'EA-002',
        equipmentId: 'EQ001',
        equipmentName: 'Tractor',
        alertType: AlertType.fuel,
        priority: MaintenancePriority.medium,
        title: 'Low Fuel',
        message: 'Fuel below 20%',
        createdAt: DateTime.now(),
      );

      final read = alert.copyWith(isRead: true);
      expect(read.isRead, true);
      expect(read.alertId, alert.alertId); // Unchanged
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EquipmentHealthStatus Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('EquipmentHealthStatus', () {
    test('getGrade returns correct grade based on score', () {
      final excellent = EquipmentHealthStatus(
        equipmentId: 'EQ1', overallScore: 95, fuelScore: 90,
        maintenanceScore: 95, usageScore: 100, assessedAt: DateTime.now(),
      );
      expect(excellent.getGrade('en'), 'Excellent');
      expect(excellent.getGrade('ar'), 'ممتاز');

      final good = EquipmentHealthStatus(
        equipmentId: 'EQ1', overallScore: 80, fuelScore: 75,
        maintenanceScore: 85, usageScore: 80, assessedAt: DateTime.now(),
      );
      expect(good.getGrade('en'), 'Good');

      final fair = EquipmentHealthStatus(
        equipmentId: 'EQ1', overallScore: 55, fuelScore: 50,
        maintenanceScore: 60, usageScore: 55, assessedAt: DateTime.now(),
      );
      expect(fair.getGrade('en'), 'Fair');
      expect(fair.getGrade('ar'), 'متوسط');

      final poor = EquipmentHealthStatus(
        equipmentId: 'EQ1', overallScore: 30, fuelScore: 25,
        maintenanceScore: 35, usageScore: 30, assessedAt: DateTime.now(),
      );
      expect(poor.getGrade('en'), 'Poor');

      final critical = EquipmentHealthStatus(
        equipmentId: 'EQ1', overallScore: 20, fuelScore: 15,
        maintenanceScore: 25, usageScore: 20, assessedAt: DateTime.now(),
      );
      expect(critical.getGrade('en'), 'Critical');
      expect(critical.getGrade('ar'), 'حرج');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // EquipmentStats Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('EquipmentStats - Extended', () {
    test('operationalPercentage calculates correctly', () {
      final stats = EquipmentStats(
        total: 20,
        byType: {'tractor': 10, 'pump': 10},
        byStatus: {'operational': 16, 'maintenance': 4},
        operational: 16,
        maintenance: 4,
        inactive: 0,
      );

      expect(stats.operationalPercentage, 80.0);
    });

    test('operationalPercentage returns 0 when total is 0', () {
      final stats = EquipmentStats.empty();
      expect(stats.operationalPercentage, 0);
    });

    test('empty factory creates zeroed stats', () {
      final stats = EquipmentStats.empty();

      expect(stats.total, 0);
      expect(stats.byType, isEmpty);
      expect(stats.byStatus, isEmpty);
      expect(stats.operational, 0);
      expect(stats.maintenance, 0);
      expect(stats.inactive, 0);
    });

    test('fromJson parses extended fields', () {
      final json = {
        'total': 15,
        'by_type': {'tractor': 8, 'pump': 7},
        'by_status': {'operational': 12, 'maintenance': 3},
        'operational': 12,
        'maintenance': 3,
        'inactive': 0,
        'low_fuel': 2,
        'needs_maintenance': 4,
        'total_value': 2500000.0,
        'total_hours': 15000.0,
      };

      final stats = EquipmentStats.fromJson(json);

      expect(stats.lowFuel, 2);
      expect(stats.needsMaintenance, 4);
      expect(stats.totalValue, 2500000.0);
      expect(stats.totalHours, 15000.0);
    });
  });
}
