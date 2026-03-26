/// Pivot Controller Tests
/// اختبارات وحدة التحكم في المحوري
///
/// Comprehensive tests for pivot irrigation control functionality including:
/// - Pivot configuration management
/// - Sector management and manipulation
/// - Control commands (start, stop, speed, direction)
/// - Status monitoring
/// - Run history and statistics
/// - VRI zone management
/// - Alert handling
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/span_zone_models.dart';

import 'irrigation_fixtures.dart';
import 'irrigation_mocks.dart';

void main() {
  late MockPivotController mockPivotController;
  late MockVRIZoneManager mockVRIZoneManager;

  setUpAll(() {
    registerIrrigationFallbackValues();
  });

  setUp(() {
    mockPivotController = MockPivotController();
    mockVRIZoneManager = MockVRIZoneManager();

    mockPivotController.setupDefaults();
    mockVRIZoneManager.setupDefaults();
  });

  group('PivotController', () {
    // ═══════════════════════════════════════════════════════════════════════
    // Configuration - التهيئة
    // ═══════════════════════════════════════════════════════════════════════

    group('getPivotConfiguration', () {
      test('should return pivot configuration for valid pivot ID', () async {
        // Act
        final config = await mockPivotController.getPivotConfiguration('pivot_001');

        // Assert
        expect(config, isNotNull);
        expect(config!.id, 'pivot_001');
        expect(config.name, 'North Field Pivot');
        expect(config.lengthMeters, 400.0);
        expect(config.spansCount, 7);
      });

      test('should return null for non-existent pivot', () async {
        // Arrange
        when(() => mockPivotController.getPivotConfiguration(any()))
            .thenAnswer((_) async => null);

        // Act
        final config = await mockPivotController.getPivotConfiguration('nonexistent');

        // Assert
        expect(config, isNull);
      });

      test('should throw on controller failure', () async {
        // Arrange
        mockPivotController.setFailureMode(true);

        // Act & Assert
        expect(
          () => mockPivotController.getPivotConfiguration('pivot_001'),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('getPivotStatus', () {
      test('should return running status when pivot is active', () async {
        // Arrange
        when(() => mockPivotController.getPivotStatus(any()))
            .thenAnswer((_) async => PivotFixtures.runningStatus);

        // Act
        final status = await mockPivotController.getPivotStatus('pivot_001');

        // Assert
        expect(status.operatingStatus, PivotOperatingStatus.running);
        expect(status.currentAngle, 145.5);
        expect(status.speedPercent, 85.0);
        expect(status.direction, PivotDirection.forward);
        expect(status.isIrrigating, true);
      });

      test('should return stopped status when pivot is idle', () async {
        // Arrange
        when(() => mockPivotController.getPivotStatus(any()))
            .thenAnswer((_) async => PivotFixtures.stoppedStatus);

        // Act
        final status = await mockPivotController.getPivotStatus('pivot_001');

        // Assert
        expect(status.operatingStatus, PivotOperatingStatus.stopped);
        expect(status.speedPercent, 0.0);
        expect(status.isIrrigating, false);
      });

      test('should return fault status with alerts', () async {
        // Arrange
        when(() => mockPivotController.getPivotStatus(any()))
            .thenAnswer((_) async => PivotFixtures.faultStatus);

        // Act
        final status = await mockPivotController.getPivotStatus('pivot_001');

        // Assert
        expect(status.operatingStatus, PivotOperatingStatus.fault);
        expect(status.hasAlerts, true);
        expect(status.hasCriticalAlerts, true);
        expect(status.activeAlerts.first.alertType, PivotAlertType.lowPressure);
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Sector Management - إدارة القطاعات
    // ═══════════════════════════════════════════════════════════════════════

    group('getSectors', () {
      test('should return list of sectors for pivot', () async {
        // Act
        final sectors = await mockPivotController.getSectors('pivot_001');

        // Assert
        expect(sectors, isNotEmpty);
        expect(sectors.length, 4);
        expect(sectors.first.sectorNumber, 1);
        expect(sectors.first.name, 'Sector A');
      });

      test('should return sectors with correct angle ranges', () async {
        // Act
        final sectors = await mockPivotController.getSectors('pivot_001');

        // Assert
        expect(sectors[0].startAngle, 0);
        expect(sectors[0].endAngle, 90);
        expect(sectors[1].startAngle, 90);
        expect(sectors[1].endAngle, 180);
        expect(sectors[2].startAngle, 180);
        expect(sectors[2].endAngle, 270);
        expect(sectors[3].startAngle, 270);
        expect(sectors[3].endAngle, 360);
      });

      test('should return sectors with irrigation settings', () async {
        // Act
        final sectors = await mockPivotController.getSectors('pivot_001');
        final sector = sectors.first;

        // Assert
        expect(sector.irrigationDepthMm, 25);
        expect(sector.applicationRateMmHr, 6.0);
        expect(sector.speedPercent, 100);
      });

      test('should identify disabled sectors', () async {
        // Act
        final sectors = await mockPivotController.getSectors('pivot_001');

        // Assert
        final disabledSectors = sectors.where((s) => !s.isEnabled).toList();
        expect(disabledSectors.length, 1);
        expect(disabledSectors.first.sectorNumber, 4);
        expect(disabledSectors.first.cropType, 'fallow');
      });
    });

    group('updateSector', () {
      test('should update sector successfully', () async {
        // Arrange
        final updatedSector = PivotFixtures.sampleSectors.first.copyWith(
          speedPercent: 90,
          irrigationDepthMm: 30,
        );

        // Act & Assert
        expect(
          mockPivotController.updateSector('pivot_001', updatedSector),
          completes,
        );
        verify(() => mockPivotController.updateSector('pivot_001', updatedSector)).called(1);
      });

      test('should handle update failure', () async {
        // Arrange
        mockPivotController.setFailureMode(true);
        final sector = PivotFixtures.sampleSectors.first;

        // Act & Assert
        expect(
          () => mockPivotController.updateSector('pivot_001', sector),
          throwsA(isA<Exception>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Control Commands - أوامر التحكم
    // ═══════════════════════════════════════════════════════════════════════

    group('sendCommand', () {
      test('should send start command successfully', () async {
        // Arrange
        final command = PivotFixtures.startCommand;

        // Act & Assert
        expect(
          mockPivotController.sendCommand(command),
          completes,
        );
        verify(() => mockPivotController.sendCommand(command)).called(1);
      });

      test('should send stop command successfully', () async {
        // Arrange
        final command = PivotFixtures.stopCommand;

        // Act & Assert
        expect(
          mockPivotController.sendCommand(command),
          completes,
        );
      });

      test('should send emergency stop command', () async {
        // Arrange
        final command = PivotFixtures.emergencyStopCommand;

        // Act & Assert
        expect(
          mockPivotController.sendCommand(command),
          completes,
        );
      });

      test('should send speed change command', () async {
        // Arrange
        final command = PivotFixtures.setSpeedCommand;

        // Act & Assert
        expect(
          mockPivotController.sendCommand(command),
          completes,
        );
      });

      test('should handle command failure', () async {
        // Arrange
        mockPivotController.setFailureMode(true);
        final command = PivotFixtures.startCommand;

        // Act & Assert
        expect(
          () => mockPivotController.sendCommand(command),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('startIrrigation', () {
      test('should start irrigation with specified parameters', () async {
        // Act & Assert
        expect(
          mockPivotController.startIrrigation(
            'pivot_001',
            speedPercent: 85,
            direction: PivotDirection.forward,
            timerHours: 8.0,
          ),
          completes,
        );
        verify(() => mockPivotController.startIrrigation(
          'pivot_001',
          speedPercent: 85,
          direction: PivotDirection.forward,
          timerHours: 8.0,
          startAngle: null,
          endAngle: null,
        )).called(1);
      });

      test('should start partial circle irrigation', () async {
        // Act & Assert
        expect(
          mockPivotController.startIrrigation(
            'pivot_001',
            speedPercent: 75,
            direction: PivotDirection.forward,
            startAngle: 0,
            endAngle: 180,
          ),
          completes,
        );
      });

      test('should start reverse direction irrigation', () async {
        // Act & Assert
        expect(
          mockPivotController.startIrrigation(
            'pivot_001',
            speedPercent: 80,
            direction: PivotDirection.reverse,
          ),
          completes,
        );
      });
    });

    group('stopIrrigation', () {
      test('should stop irrigation successfully', () async {
        // Act & Assert
        expect(
          mockPivotController.stopIrrigation('pivot_001'),
          completes,
        );
        verify(() => mockPivotController.stopIrrigation('pivot_001')).called(1);
      });
    });

    group('emergencyStop', () {
      test('should execute emergency stop', () async {
        // Act & Assert
        expect(
          mockPivotController.emergencyStop('pivot_001'),
          completes,
        );
        verify(() => mockPivotController.emergencyStop('pivot_001')).called(1);
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Schedule Management - إدارة الجداول
    // ═══════════════════════════════════════════════════════════════════════

    group('getSchedules', () {
      test('should return list of schedules for pivot', () async {
        // Act
        final schedules = await mockPivotController.getSchedules('pivot_001');

        // Assert
        expect(schedules, isNotEmpty);
        expect(schedules.length, 2);
        expect(schedules.any((s) => s.scheduleType == ScheduleType.daily), true);
        expect(schedules.any((s) => s.scheduleType == ScheduleType.weekly), true);
      });
    });

    group('createSchedule', () {
      test('should create new schedule', () async {
        // Arrange
        final schedule = PivotFixtures.dailySchedule;

        // Act & Assert
        expect(
          mockPivotController.createSchedule(schedule),
          completes,
        );
        verify(() => mockPivotController.createSchedule(schedule)).called(1);
      });
    });

    group('updateSchedule', () {
      test('should update existing schedule', () async {
        // Arrange
        final schedule = PivotFixtures.dailySchedule.copyWith(isActive: false);

        // Act & Assert
        expect(
          mockPivotController.updateSchedule(schedule),
          completes,
        );
        verify(() => mockPivotController.updateSchedule(schedule)).called(1);
      });
    });

    group('deleteSchedule', () {
      test('should delete schedule', () async {
        // Act & Assert
        expect(
          mockPivotController.deleteSchedule('schedule_001'),
          completes,
        );
        verify(() => mockPivotController.deleteSchedule('schedule_001')).called(1);
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // History and Statistics - السجل والإحصائيات
    // ═══════════════════════════════════════════════════════════════════════

    group('getRunHistory', () {
      test('should return run history for pivot', () async {
        // Act
        final history = await mockPivotController.getRunHistory('pivot_001');

        // Assert
        expect(history, isNotEmpty);
        expect(history.length, 2);
      });

      test('should include completed and faulted runs', () async {
        // Act
        final history = await mockPivotController.getRunHistory('pivot_001');

        // Assert
        expect(history.any((h) => h.status == RunStatus.completed), true);
        expect(history.any((h) => h.status == RunStatus.faulted), true);
      });

      test('should limit results based on parameter', () async {
        // Act
        await mockPivotController.getRunHistory('pivot_001', limit: 5);

        // Assert
        verify(() => mockPivotController.getRunHistory('pivot_001', limit: 5)).called(1);
      });
    });

    group('getStatistics', () {
      test('should return weekly statistics', () async {
        // Act
        final stats = await mockPivotController.getStatistics('pivot_001', 'weekly');

        // Assert
        expect(stats.period, 'weekly');
        expect(stats.totalWaterM3, 28000.0);
        expect(stats.totalEnergyKwh, 1400.0);
        expect(stats.completeCircles, 7);
        expect(stats.efficiencyPercent, 87.5);
      });

      test('should return monthly statistics', () async {
        // Act
        final stats = await mockPivotController.getStatistics('pivot_001', 'monthly');

        // Assert
        expect(stats.period, 'monthly');
        expect(stats.totalWaterM3, 112000.0);
        expect(stats.completeCircles, 28);
      });

      test('should include cost information', () async {
        // Act
        final stats = await mockPivotController.getStatistics('pivot_001', 'weekly');

        // Assert
        expect(stats.waterCost, greaterThan(0));
        expect(stats.energyCost, greaterThan(0));
      });

      test('should include downtime information', () async {
        // Act
        final stats = await mockPivotController.getStatistics('pivot_001', 'weekly');

        // Assert
        expect(stats.faultCount, greaterThanOrEqualTo(0));
        expect(stats.downtimeHours, greaterThanOrEqualTo(0));
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Status Monitoring - مراقبة الحالة
    // ═══════════════════════════════════════════════════════════════════════

    group('watchPivotStatus', () {
      test('should emit status updates', () async {
        // Act
        final stream = mockPivotController.watchPivotStatus('pivot_001');

        // Assert
        await expectLater(
          stream,
          emitsInOrder([
            isA<PivotStatus>(),
            isA<PivotStatus>(),
          ]),
        );
      });

      test('should emit error on connection failure', () async {
        // Arrange
        mockPivotController.setFailureMode(true);

        // Act
        final stream = mockPivotController.watchPivotStatus('pivot_001');

        // Assert
        await expectLater(stream, emitsError(isA<Exception>()));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VRI Zone Manager - مدير مناطق VRI
  // ═══════════════════════════════════════════════════════════════════════════

  group('VRIZoneManager', () {
    group('getZoneGrid', () {
      test('should return zone grid for pivot', () async {
        // Act
        final grid = await mockVRIZoneManager.getZoneGrid('pivot_001');

        // Assert
        expect(grid.pivotId, 'pivot_001');
        expect(grid.spanCount, 4);
        expect(grid.angularDivisions, 8);
        expect(grid.grid, isNotEmpty);
      });
    });

    group('createUniformGrid', () {
      test('should create uniform grid with specified dimensions', () async {
        // Act
        final grid = await mockVRIZoneManager.createUniformGrid('pivot_001', 6, 12);

        // Assert
        expect(grid.spanCount, 6);
        expect(grid.angularDivisions, 12);
        expect(grid.totalZones, 72);
      });
    });

    group('createGridFromNDVI', () {
      test('should create variable rate grid from NDVI data', () async {
        // Arrange
        final ndviValues = {'0_0': 0.72, '0_1': 0.45};

        // Act
        final grid = await mockVRIZoneManager.createGridFromNDVI('pivot_001', ndviValues);

        // Assert
        expect(grid, isNotNull);
        // Zones with low NDVI should have higher application rates
      });
    });

    group('updateZoneRate', () {
      test('should update zone application rate', () async {
        // Act & Assert
        expect(
          mockVRIZoneManager.updateZoneRate('pivot_001', 'zone_0_0', 115.0),
          completes,
        );
        verify(() => mockVRIZoneManager.updateZoneRate('pivot_001', 'zone_0_0', 115.0)).called(1);
      });
    });

    group('enableZone/disableZone', () {
      test('should enable zone', () async {
        // Act & Assert
        expect(
          mockVRIZoneManager.enableZone('pivot_001', 'zone_0_0'),
          completes,
        );
      });

      test('should disable zone', () async {
        // Act & Assert
        expect(
          mockVRIZoneManager.disableZone('pivot_001', 'zone_0_0'),
          completes,
        );
      });
    });

    group('createPrescription', () {
      test('should create irrigation prescription', () async {
        // Act
        final prescription = await mockVRIZoneManager.createPrescription(
          'pivot_001',
          PrescriptionType.irrigation,
        );

        // Assert
        expect(prescription.prescriptionType, PrescriptionType.irrigation);
        expect(prescription.pivotId, 'pivot_001');
        expect(prescription.zoneValues, isNotEmpty);
      });
    });

    group('getZoneStatistics', () {
      test('should return zone statistics', () async {
        // Act
        final stats = await mockVRIZoneManager.getZoneStatistics('pivot_001');

        // Assert
        expect(stats.totalZones, greaterThan(0));
        expect(stats.activeZones, greaterThanOrEqualTo(0));
        expect(stats.avgApplicationRate, greaterThan(0));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Pivot Model Tests - اختبارات نماذج المحوري
  // ═══════════════════════════════════════════════════════════════════════════

  group('PivotConfiguration Model', () {
    test('should have correct default values', () {
      final pivot = PivotFixtures.smallPivot;

      expect(pivot.pivotType, PivotType.fullCircle);
      expect(pivot.rotationDirection, RotationDirection.clockwise);
      expect(pivot.startAngle, 0);
      expect(pivot.endAngle, 360);
      expect(pivot.hasVRI, false);
      expect(pivot.hasEndGun, false);
      expect(pivot.hasCornerSystem, false);
    });

    test('should calculate total radius including overhang', () {
      final pivot = PivotFixtures.sampleFullCirclePivot;

      expect(pivot.totalRadiusMeters, 415.0); // 400 + 15
    });

    test('should calculate area for angle span', () {
      final pivot = PivotFixtures.sampleFullCirclePivot;

      // Full circle
      final fullArea = pivot.areaForAngleSpan(0, 360);
      expect(fullArea, closeTo(50.27, 0.01));

      // Half circle
      final halfArea = pivot.areaForAngleSpan(0, 180);
      expect(halfArea, closeTo(25.135, 0.01));

      // Quarter circle
      final quarterArea = pivot.areaForAngleSpan(0, 90);
      expect(quarterArea, closeTo(12.5675, 0.01));
    });

    test('should return center as LatLng', () {
      final pivot = PivotFixtures.sampleFullCirclePivot;

      expect(pivot.center.latitude, 15.3694);
      expect(pivot.center.longitude, 44.1910);
    });
  });

  group('PivotStatus Model', () {
    test('should indicate irrigating status correctly', () {
      expect(PivotFixtures.runningStatus.isIrrigating, true);
      expect(PivotFixtures.stoppedStatus.isIrrigating, false);
      expect(PivotFixtures.faultStatus.isIrrigating, false);
    });

    test('should detect alerts correctly', () {
      expect(PivotFixtures.runningStatus.hasAlerts, false);
      expect(PivotFixtures.faultStatus.hasAlerts, true);
      expect(PivotFixtures.faultStatus.hasCriticalAlerts, true);
    });

    test('should calculate progress percentage', () {
      final status = PivotFixtures.runningStatus;

      // 195 minutes elapsed out of 8 hours (480 minutes)
      final progress = status.progressPercent;
      expect(progress, closeTo(40.625, 0.01));
    });

    test('should handle zero timer for progress calculation', () {
      final status = PivotFixtures.stoppedStatus;

      expect(status.progressPercent, 0);
    });
  });

  group('PivotSector Model', () {
    test('should calculate angle span', () {
      final sector = PivotFixtures.sampleSectors.first;

      expect(sector.angleSpan, 90);
    });

    test('should calculate irrigation time', () {
      final sector = PivotFixtures.sampleSectors.first;
      const fullCircleMinutes = 480.0; // 8 hours

      final time = sector.irrigationTimeMinutes(fullCircleMinutes);

      // 90/360 * 480 * (100/100) = 120 minutes
      expect(time, closeTo(120, 0.1));
    });

    test('should adjust irrigation time for speed percentage', () {
      final sector = PivotFixtures.sampleSectors[1]; // 80% speed
      const fullCircleMinutes = 480.0;

      final time = sector.irrigationTimeMinutes(fullCircleMinutes);

      // 90/360 * 480 * (100/80) = 150 minutes
      expect(time, closeTo(150, 0.1));
    });
  });

  group('PivotAlert Model', () {
    test('should have correct alert properties', () {
      final alert = PivotFixtures.lowPressureAlert;

      expect(alert.alertType, PivotAlertType.lowPressure);
      expect(alert.severity, AlertSeverity.critical);
      expect(alert.towerNumber, 3);
      expect(alert.isAcknowledged, false);
    });

    test('should have bilingual messages', () {
      final alert = PivotFixtures.lowPressureAlert;

      expect(alert.message, isNotEmpty);
      expect(alert.messageAr, isNotEmpty);
      expect(alert.messageAr, contains('الضغط'));
    });
  });

  group('PivotControlCommand Model', () {
    test('should create start command correctly', () {
      final command = PivotFixtures.startCommand;

      expect(command.commandType, PivotCommandType.start);
      expect(command.speedPercent, 85);
      expect(command.direction, PivotDirection.forward);
      expect(command.timerHours, 8.0);
      expect(command.issuedBy, 'user_001');
    });

    test('should create stop command correctly', () {
      final command = PivotFixtures.stopCommand;

      expect(command.commandType, PivotCommandType.stop);
      expect(command.speedPercent, isNull);
      expect(command.direction, isNull);
    });

    test('should create emergency stop command correctly', () {
      final command = PivotFixtures.emergencyStopCommand;

      expect(command.commandType, PivotCommandType.emergencyStop);
    });
  });

  group('PivotStatistics Model', () {
    test('should have correct period information', () {
      final stats = PivotFixtures.weeklyStats;

      expect(stats.period, 'weekly');
      expect(stats.periodStart.isBefore(stats.periodEnd), true);
    });

    test('should have valid efficiency percentage', () {
      final stats = PivotFixtures.weeklyStats;

      expect(stats.efficiencyPercent, greaterThan(0));
      expect(stats.efficiencyPercent, lessThanOrEqualTo(100));
    });

    test('should track resource usage', () {
      final stats = PivotFixtures.weeklyStats;

      expect(stats.totalWaterM3, greaterThan(0));
      expect(stats.totalEnergyKwh, greaterThan(0));
      expect(stats.totalRunHours, greaterThan(0));
    });
  });
}
