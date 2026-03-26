/// Pivot Irrigation Models Tests - اختبارات نماذج الري المحوري
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/span_zone_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════
  // Enums
  // ═══════════════════════════════════════════════════════════════════

  group('Pivot Enums', () {
    test('PivotType has 4 values', () {
      expect(PivotType.values.length, 4);
      expect(PivotType.values, contains(PivotType.fullCircle));
      expect(PivotType.values, contains(PivotType.partialCircle));
      expect(PivotType.values, contains(PivotType.corner));
      expect(PivotType.values, contains(PivotType.linear));
    });

    test('RotationDirection has 2 values', () {
      expect(RotationDirection.values.length, 2);
    });

    test('PivotOperatingStatus has 6 values', () {
      expect(PivotOperatingStatus.values.length, 6);
      expect(PivotOperatingStatus.values, contains(PivotOperatingStatus.stopped));
      expect(PivotOperatingStatus.values, contains(PivotOperatingStatus.running));
      expect(PivotOperatingStatus.values, contains(PivotOperatingStatus.paused));
      expect(PivotOperatingStatus.values, contains(PivotOperatingStatus.fault));
      expect(PivotOperatingStatus.values, contains(PivotOperatingStatus.maintenance));
      expect(PivotOperatingStatus.values, contains(PivotOperatingStatus.scheduled));
    });

    test('PivotDirection has 3 values', () {
      expect(PivotDirection.values.length, 3);
    });

    test('PivotAlertType has 13 values', () {
      expect(PivotAlertType.values.length, 13);
    });

    test('AlertSeverity has 4 values', () {
      expect(AlertSeverity.values.length, 4);
      expect(AlertSeverity.values, contains(AlertSeverity.info));
      expect(AlertSeverity.values, contains(AlertSeverity.warning));
      expect(AlertSeverity.values, contains(AlertSeverity.critical));
      expect(AlertSeverity.values, contains(AlertSeverity.emergency));
    });

    test('ScheduleType has 4 values', () {
      expect(ScheduleType.values.length, 4);
    });

    test('RunStatus has 4 values', () {
      expect(RunStatus.values.length, 4);
    });

    test('PivotCommandType has 12 values', () {
      expect(PivotCommandType.values.length, 12);
    });

    test('VRIZoneType has 5 values', () {
      expect(VRIZoneType.values.length, 5);
    });

    test('NozzlePackage has 6 values', () {
      expect(NozzlePackage.values.length, 6);
    });

    test('PrescriptionType has 3 values', () {
      expect(PrescriptionType.values.length, 3);
    });

    test('PrescriptionSource has 6 values', () {
      expect(PrescriptionSource.values.length, 6);
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // PivotConfiguration
  // ═══════════════════════════════════════════════════════════════════

  group('PivotConfiguration', () {
    PivotConfiguration makeConfig({
      double lengthMeters = 400,
      double overhangMeters = 10,
      double areaHectares = 50,
      double centerLat = 15.5,
      double centerLng = 44.2,
    }) {
      return PivotConfiguration(
        id: 'pivot1',
        fieldId: 'field1',
        name: 'Pivot 1',
        nameAr: 'محوري 1',
        centerLat: centerLat,
        centerLng: centerLng,
        lengthMeters: lengthMeters,
        overhangMeters: overhangMeters,
        spansCount: 8,
        areaHectares: areaHectares,
        flowRateLph: 150000,
      );
    }

    test('construction with defaults', () {
      final c = makeConfig();
      expect(c.pivotType, PivotType.fullCircle);
      expect(c.rotationDirection, RotationDirection.clockwise);
      expect(c.startAngle, 0);
      expect(c.endAngle, 360);
      expect(c.operatingPressureBar, 2.5);
      expect(c.hasVRI, false);
      expect(c.hasEndGun, false);
      expect(c.hasCornerSystem, false);
      expect(c.sectors, isEmpty);
      expect(c.vriZones, isEmpty);
    });

    test('copyWith changes specific fields', () {
      final c = makeConfig();
      final c2 = c.copyWith(name: 'Updated');
      expect(c2.name, 'Updated');
      expect(c2.fieldId, 'field1'); // unchanged
    });
  });

  group('PivotConfigurationX extensions', () {
    PivotConfiguration makeConfig({
      double lengthMeters = 400,
      double overhangMeters = 10,
      double areaHectares = 50,
    }) {
      return PivotConfiguration(
        id: 'pivot1',
        fieldId: 'field1',
        name: 'Pivot 1',
        centerLat: 15.5,
        centerLng: 44.2,
        lengthMeters: lengthMeters,
        overhangMeters: overhangMeters,
        spansCount: 8,
        areaHectares: areaHectares,
        flowRateLph: 150000,
      );
    }

    test('center returns correct LatLng', () {
      final c = makeConfig();
      expect(c.center.latitude, 15.5);
      expect(c.center.longitude, 44.2);
    });

    test('totalRadiusMeters includes overhang', () {
      final c = makeConfig(lengthMeters: 400, overhangMeters: 10);
      expect(c.totalRadiusMeters, 410);
    });

    test('totalRadiusMeters with zero overhang', () {
      final c = makeConfig(lengthMeters: 400, overhangMeters: 0);
      expect(c.totalRadiusMeters, 400);
    });

    test('areaForAngleSpan full circle', () {
      final c = makeConfig(areaHectares: 50);
      expect(c.areaForAngleSpan(0, 360), closeTo(50.0, 0.01));
    });

    test('areaForAngleSpan half circle', () {
      final c = makeConfig(areaHectares: 50);
      expect(c.areaForAngleSpan(0, 180), closeTo(25.0, 0.01));
    });

    test('areaForAngleSpan quarter', () {
      final c = makeConfig(areaHectares: 100);
      expect(c.areaForAngleSpan(0, 90), closeTo(25.0, 0.01));
    });

    test('areaForAngleSpan zero span returns 0', () {
      final c = makeConfig(areaHectares: 50);
      expect(c.areaForAngleSpan(90, 90), 0.0);
    });

    test('areaForAngleSpan reversed angles uses abs', () {
      final c = makeConfig(areaHectares: 50);
      // (90 - 180).abs() / 360 * 50 = 90/360*50 = 12.5
      expect(c.areaForAngleSpan(180, 90), closeTo(12.5, 0.01));
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // PivotSector & Extension
  // ═══════════════════════════════════════════════════════════════════

  group('PivotSector', () {
    test('construction with defaults', () {
      final s = PivotSector(
        id: 's1',
        sectorNumber: 1,
        startAngle: 0,
        endAngle: 90,
      );
      expect(s.irrigationDepthMm, 25);
      expect(s.applicationRateMmHr, 6.0);
      expect(s.isEnabled, true);
      expect(s.speedPercent, 100);
      expect(s.color, '#4CAF50');
    });
  });

  group('PivotSectorX extensions', () {
    test('angleSpan calculates correctly', () {
      final s = PivotSector(id: 's1', sectorNumber: 1, startAngle: 0, endAngle: 90);
      expect(s.angleSpan, 90);
    });

    test('angleSpan with reversed angles uses abs', () {
      final s = PivotSector(id: 's1', sectorNumber: 1, startAngle: 270, endAngle: 0);
      expect(s.angleSpan, 270);
    });

    test('irrigationTimeMinutes full circle at 100% speed', () {
      final s = PivotSector(id: 's1', sectorNumber: 1, startAngle: 0, endAngle: 360, speedPercent: 100);
      expect(s.irrigationTimeMinutes(60), closeTo(60.0, 0.01));
    });

    test('irrigationTimeMinutes half circle at 100%', () {
      final s = PivotSector(id: 's1', sectorNumber: 1, startAngle: 0, endAngle: 180, speedPercent: 100);
      expect(s.irrigationTimeMinutes(60), closeTo(30.0, 0.01));
    });

    test('irrigationTimeMinutes at 50% speed doubles time', () {
      final s = PivotSector(id: 's1', sectorNumber: 1, startAngle: 0, endAngle: 360, speedPercent: 50);
      expect(s.irrigationTimeMinutes(60), closeTo(120.0, 0.01));
    });

    test('irrigationTimeMinutes quarter at 75% speed', () {
      final s = PivotSector(id: 's1', sectorNumber: 1, startAngle: 0, endAngle: 90, speedPercent: 75);
      // 60 * (90/360) * (100/75) = 60 * 0.25 * 1.333 = 20
      expect(s.irrigationTimeMinutes(60), closeTo(20.0, 0.01));
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // PivotStatus & Extension
  // ═══════════════════════════════════════════════════════════════════

  group('PivotStatusX extensions', () {
    PivotStatus makeStatus({
      PivotOperatingStatus operatingStatus = PivotOperatingStatus.stopped,
      double timerHours = 10,
      double elapsedMinutes = 0,
      List<PivotAlert>? alerts,
    }) {
      return PivotStatus(
        pivotId: 'p1',
        currentAngle: 0,
        operatingStatus: operatingStatus,
        direction: PivotDirection.forward,
        speedPercent: 100,
        timerHours: timerHours,
        elapsedMinutes: elapsedMinutes,
        currentFlowRateLph: 150000,
        currentPressureBar: 2.5,
        endGunActive: false,
        cornerSystemActive: false,
        waterAppliedM3: 0,
        energyConsumedKwh: 0,
        lastUpdated: DateTime(2026, 3, 20),
        activeAlerts: alerts ?? [],
      );
    }

    test('isIrrigating true when running', () {
      expect(makeStatus(operatingStatus: PivotOperatingStatus.running).isIrrigating, true);
    });

    test('isIrrigating false when stopped', () {
      expect(makeStatus(operatingStatus: PivotOperatingStatus.stopped).isIrrigating, false);
    });

    test('isIrrigating false when paused', () {
      expect(makeStatus(operatingStatus: PivotOperatingStatus.paused).isIrrigating, false);
    });

    test('hasAlerts true when alerts present', () {
      final alert = PivotAlert(
        id: 'a1',
        pivotId: 'p1',
        alertType: PivotAlertType.lowPressure,
        severity: AlertSeverity.warning,
        message: 'Low pressure',
        messageAr: 'ضغط منخفض',
        timestamp: DateTime(2026, 3, 20),
      );
      expect(makeStatus(alerts: [alert]).hasAlerts, true);
    });

    test('hasAlerts false when no alerts', () {
      expect(makeStatus(alerts: []).hasAlerts, false);
    });

    test('hasCriticalAlerts true for critical severity', () {
      final alert = PivotAlert(
        id: 'a1',
        pivotId: 'p1',
        alertType: PivotAlertType.powerFailure,
        severity: AlertSeverity.critical,
        message: 'Power failure',
        messageAr: 'انقطاع الكهرباء',
        timestamp: DateTime(2026, 3, 20),
      );
      expect(makeStatus(alerts: [alert]).hasCriticalAlerts, true);
    });

    test('hasCriticalAlerts true for emergency severity', () {
      final alert = PivotAlert(
        id: 'a1',
        pivotId: 'p1',
        alertType: PivotAlertType.pipelineLeak,
        severity: AlertSeverity.emergency,
        message: 'Leak!',
        messageAr: 'تسريب!',
        timestamp: DateTime(2026, 3, 20),
      );
      expect(makeStatus(alerts: [alert]).hasCriticalAlerts, true);
    });

    test('hasCriticalAlerts false for warning severity', () {
      final alert = PivotAlert(
        id: 'a1',
        pivotId: 'p1',
        alertType: PivotAlertType.lowPressure,
        severity: AlertSeverity.warning,
        message: 'Warning',
        messageAr: 'تحذير',
        timestamp: DateTime(2026, 3, 20),
      );
      expect(makeStatus(alerts: [alert]).hasCriticalAlerts, false);
    });

    test('progressPercent at start is 0', () {
      expect(makeStatus(timerHours: 10, elapsedMinutes: 0).progressPercent, 0);
    });

    test('progressPercent at halfway', () {
      // 300 min elapsed out of 10 hours (600 min) = 50%
      expect(makeStatus(timerHours: 10, elapsedMinutes: 300.0).progressPercent, closeTo(50, 0.01));
    });

    test('progressPercent at completion', () {
      expect(makeStatus(timerHours: 10, elapsedMinutes: 600.0).progressPercent, closeTo(100, 0.01));
    });

    test('progressPercent clamped to 100 when over', () {
      expect(makeStatus(timerHours: 10, elapsedMinutes: 1200.0).progressPercent, 100);
    });

    test('BUG: progressPercent with zero timerHours returns 0', () {
      expect(makeStatus(timerHours: 0, elapsedMinutes: 100.0).progressPercent, 0);
    });

    test('BUG: progressPercent with negative timer returns 0', () {
      expect(makeStatus(timerHours: -5, elapsedMinutes: 100.0).progressPercent, 0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // Span Zone Models
  // ═══════════════════════════════════════════════════════════════════

  group('SpanConfiguration', () {
    test('construction with defaults', () {
      final s = SpanConfiguration(
        id: 'span1',
        spanNumber: 1,
        distanceFromCenter: 50,
        spanLengthMeters: 45,
      );
      expect(s.nozzleCount, 10);
      expect(s.nozzlePackage, NozzlePackage.standard);
      expect(s.baseApplicationRateMmHr, 6.0);
      expect(s.isOperational, true);
      expect(s.zones, isEmpty);
    });
  });

  group('SpanConfigurationX extensions', () {
    test('arcLengthAt360 calculates 2*pi*r', () {
      final s = SpanConfiguration(id: 's1', spanNumber: 1, distanceFromCenter: 100, spanLengthMeters: 50);
      expect(s.arcLengthAt360, closeTo(2 * 3.14159 * 100, 0.1));
    });

    test('effectiveRateForAngle returns zone rate when matched', () {
      final zone = SpanZone(
        id: 'z1',
        spanNumber: 1,
        zoneNumber: 1,
        startAngle: 0,
        endAngle: 90,
        applicationRatePercent: 80,
      );
      final s = SpanConfiguration(
        id: 's1',
        spanNumber: 1,
        distanceFromCenter: 100,
        spanLengthMeters: 50,
        baseApplicationRateMmHr: 6.0,
        zones: [zone],
      );
      expect(s.effectiveRateForAngle(45), closeTo(4.8, 0.01)); // 6 * 80/100
    });

    test('effectiveRateForAngle returns base rate when no zone match', () {
      final s = SpanConfiguration(
        id: 's1',
        spanNumber: 1,
        distanceFromCenter: 100,
        spanLengthMeters: 50,
        baseApplicationRateMmHr: 6.0,
        zones: [],
      );
      expect(s.effectiveRateForAngle(45), 6.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // VRIZoneGrid & Extensions
  // ═══════════════════════════════════════════════════════════════════

  group('VRIZoneGridX extensions', () {
    late VRIZoneGrid grid;

    setUp(() {
      grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 2,
        angularDivisions: 4,
      );
    });

    test('uniform grid has correct structure', () {
      expect(grid.totalZones, 8); // 2 spans * 4 angles
      expect(grid.angularResolution, 90);
      expect(grid.grid.length, 2); // 2 spans
      expect(grid.grid[0].length, 4); // 4 zones per span
    });

    test('getZoneAt returns correct zone', () {
      final zone = grid.getZoneAt(0, 45);
      expect(zone, isNotNull);
      expect(zone!.startAngle, 0);
      expect(zone.endAngle, 90);
    });

    test('getZoneAt returns null for out of bounds span', () {
      expect(grid.getZoneAt(-1, 45), isNull);
      expect(grid.getZoneAt(5, 45), isNull);
    });

    test('getZoneAt returns null for unmatched angle', () {
      // All zones should cover 0-360 in a uniform grid, so this shouldn't happen
      // but let's verify boundary behavior
      final zone = grid.getZoneAt(0, 0); // Should match zone 0-90
      expect(zone, isNotNull);
    });

    test('getZonesAtAngle returns zones from all spans', () {
      final zones = grid.getZonesAtAngle(45);
      expect(zones.length, 2); // One zone per span at this angle
    });

    test('avgApplicationRateAtAngle for uniform grid', () {
      expect(grid.avgApplicationRateAtAngle(45), 100);
    });

    test('avgApplicationRateAtAngle returns 100 when no zones match', () {
      // At angle 360 exactly, no zone matches (zones use < endAngle)
      expect(grid.avgApplicationRateAtAngle(360), 100);
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // VRIZoneGridBuilder
  // ═══════════════════════════════════════════════════════════════════

  group('VRIZoneGridBuilder', () {
    test('createUniformGrid correct zone count', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 4,
        angularDivisions: 8,
      );
      expect(grid.totalZones, 32);
      expect(grid.spanCount, 4);
      expect(grid.angularDivisions, 8);
    });

    test('createUniformGrid zone angles are sequential', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 4,
      );
      expect(grid.grid[0][0].startAngle, 0);
      expect(grid.grid[0][0].endAngle, 90);
      expect(grid.grid[0][1].startAngle, 90);
      expect(grid.grid[0][1].endAngle, 180);
      expect(grid.grid[0][2].startAngle, 180);
      expect(grid.grid[0][2].endAngle, 270);
      expect(grid.grid[0][3].startAngle, 270);
      expect(grid.grid[0][3].endAngle, 360);
    });

    test('createFromNDVI low NDVI gets high rate (130)', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.2}, // Low NDVI
      );
      expect(grid.grid[0][0].applicationRatePercent, 130);
      expect(grid.grid[0][0].ndviValue, 0.2);
    });

    test('createFromNDVI moderate NDVI gets 115', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.4},
      );
      expect(grid.grid[0][0].applicationRatePercent, 115);
    });

    test('createFromNDVI normal NDVI gets 100', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.6},
      );
      expect(grid.grid[0][0].applicationRatePercent, 100);
    });

    test('createFromNDVI high NDVI gets low rate (85)', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.8},
      );
      expect(grid.grid[0][0].applicationRatePercent, 85);
    });

    test('BUG FOUND: createFromNDVI missing key defaults to 0.5 which maps to 100 not 115', () {
      // Default NDVI is 0.5, which is NOT < 0.5, so it falls into the < 0.7 bracket
      // This means missing data gets "normal" rate, which may under-irrigate stressed areas
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {}, // no key '0_0' → defaults to 0.5
      );
      // BUG: 0.5 is NOT < 0.5, so rate is 100 (normal) not 115 (moderate stress)
      // This is a boundary bug - missing NDVI data should be treated as moderate stress
      expect(grid.grid[0][0].applicationRatePercent, 100);
    });

    test('createFromNDVI boundary: NDVI exactly 0.3 → 115', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.3}, // 0.3 is NOT < 0.3, so goes to next bracket
      );
      expect(grid.grid[0][0].applicationRatePercent, 115);
    });

    test('createFromNDVI boundary: NDVI exactly 0.5 → 100', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.5},
      );
      expect(grid.grid[0][0].applicationRatePercent, 100);
    });

    test('createFromNDVI boundary: NDVI exactly 0.7 → 85', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 1,
        ndviValues: {'0_0': 0.7},
      );
      expect(grid.grid[0][0].applicationRatePercent, 85);
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // VRIZoneStatistics
  // ═══════════════════════════════════════════════════════════════════

  group('VRIZoneStatistics.fromGrid', () {
    test('uniform 100% grid stats', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 2,
        angularDivisions: 4,
        defaultApplicationRate: 100,
      );
      final stats = VRIZoneStatistics.fromGrid(grid);
      expect(stats.totalZones, 8);
      expect(stats.activeZones, 8);
      expect(stats.offZones, 0);
      expect(stats.avgApplicationRate, 100);
      expect(stats.minApplicationRate, 100);
      expect(stats.maxApplicationRate, 100);
      expect(stats.waterSavingsPercent, 0); // 100 - 100 = 0
    });

    test('NDVI-based grid stats show savings', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 4,
        ndviValues: {
          '0_0': 0.2, // 130
          '0_1': 0.4, // 115
          '0_2': 0.6, // 100
          '0_3': 0.8, // 85
        },
      );
      final stats = VRIZoneStatistics.fromGrid(grid);
      expect(stats.totalZones, 4);
      expect(stats.activeZones, 4);
      expect(stats.minApplicationRate, 85);
      expect(stats.maxApplicationRate, 130);
      // avg = (130+115+100+85)/4 = 107.5
      expect(stats.avgApplicationRate, closeTo(107.5, 0.01));
      // Water savings = 100 - 107.5 = -7.5, clamped to 0
      expect(stats.waterSavingsPercent, 0);
    });

    test('grid with below-100 avg shows water savings', () {
      final grid = VRIZoneGridBuilder.createFromNDVI(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 2,
        ndviValues: {
          '0_0': 0.8, // 85
          '0_1': 0.8, // 85
        },
      );
      final stats = VRIZoneStatistics.fromGrid(grid);
      // avg = 85, savings = 100 - 85 = 15
      expect(stats.waterSavingsPercent, closeTo(15.0, 0.01));
    });

    test('rate distribution counts correctly', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 4,
        defaultApplicationRate: 100,
      );
      final stats = VRIZoneStatistics.fromGrid(grid);
      expect(stats.rateDistribution['normal'], 4); // all at 100
      expect(stats.rateDistribution['off'], 0);
      expect(stats.rateDistribution['low'], 0);
      expect(stats.rateDistribution['high'], 0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════
  // Bug Detection Tests
  // ═══════════════════════════════════════════════════════════════════

  group('Bug Detection - Edge Cases', () {
    test('PivotSector with zero speedPercent causes division by zero', () {
      final s = PivotSector(
        id: 's1',
        sectorNumber: 1,
        startAngle: 0,
        endAngle: 90,
        speedPercent: 0,
      );
      // BUG: irrigationTimeMinutes divides by speedPercent which is 0!
      // This would return infinity
      expect(() => s.irrigationTimeMinutes(60), returnsNormally);
      // The result would be infinity since 100/0 = infinity
      expect(s.irrigationTimeMinutes(60), double.infinity);
    });

    test('PivotSector with very small speedPercent', () {
      final s = PivotSector(
        id: 's1',
        sectorNumber: 1,
        startAngle: 0,
        endAngle: 90,
        speedPercent: 0.001,
      );
      // Very large but not infinite
      expect(s.irrigationTimeMinutes(60).isFinite, true);
    });

    test('VRIZoneGrid getZoneAt at exact boundary (endAngle)', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 4,
      );
      // Zone 0: 0-90, Zone 1: 90-180. At angle=90, it should match zone 1 (not zone 0)
      // because the condition is angle >= startAngle && angle < endAngle
      final zone = grid.getZoneAt(0, 90);
      expect(zone, isNotNull);
      expect(zone!.startAngle, 90); // Should be in zone 1 (90-180)
    });

    test('BUG: VRIZoneGrid angle 359.99 matches last zone', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 4,
      );
      final zone = grid.getZoneAt(0, 359.99);
      expect(zone, isNotNull);
      expect(zone!.startAngle, 270); // Zone 3: 270-360
    });

    test('BUG: VRIZoneGrid angle exactly 360 returns null', () {
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'p1',
        spanCount: 1,
        angularDivisions: 4,
      );
      // At 360, no zone matches because all use < endAngle
      // Last zone is 270 <= angle < 360
      final zone = grid.getZoneAt(0, 360);
      expect(zone, isNull); // BUG: angle 360 should wrap to 0 or match last zone
    });

    test('SpanConfigurationX.effectiveRateForAngle at zone boundary', () {
      final zone1 = SpanZone(id: 'z1', spanNumber: 1, zoneNumber: 1, startAngle: 0, endAngle: 90, applicationRatePercent: 50);
      final zone2 = SpanZone(id: 'z2', spanNumber: 1, zoneNumber: 2, startAngle: 90, endAngle: 180, applicationRatePercent: 150);
      final s = SpanConfiguration(
        id: 's1',
        spanNumber: 1,
        distanceFromCenter: 100,
        spanLengthMeters: 50,
        baseApplicationRateMmHr: 6.0,
        zones: [zone1, zone2],
      );
      // At exactly 90, should match zone2 (angle >= 90 && angle < 180)
      expect(s.effectiveRateForAngle(90), closeTo(9.0, 0.01)); // 6 * 150/100
    });
  });
}
