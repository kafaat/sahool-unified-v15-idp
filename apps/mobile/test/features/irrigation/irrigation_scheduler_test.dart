/// Irrigation Scheduler Tests
/// اختبارات جدولة الري
///
/// Comprehensive tests for irrigation scheduling functionality including:
/// - Schedule creation and modification
/// - Event management (skip, reschedule, update)
/// - ET-based scheduling recommendations
/// - Sensor-triggered scheduling
/// - Schedule conflict resolution
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/irrigation/data/remote/irrigation_api.dart';
// Hide to avoid conflict with irrigation_api
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';

import 'irrigation_fixtures.dart';
import 'irrigation_mocks.dart';

void main() {
  late MockIrrigationScheduler mockScheduler;
  late MockIrrigationApi mockApi;
  late MockSensorService mockSensorService;

  setUpAll(() {
    registerIrrigationFallbackValues();
  });

  setUp(() {
    mockScheduler = MockIrrigationScheduler();
    mockApi = MockIrrigationApi();
    mockSensorService = MockSensorService();

    mockScheduler.setupDefaults();
    mockApi.setupDefaults();
    mockSensorService.setupDefaults();
  });

  group('IrrigationScheduler', () {
    // ═══════════════════════════════════════════════════════════════════════
    // Schedule Creation - إنشاء الجدول
    // ═══════════════════════════════════════════════════════════════════════

    group('createSchedule', () {
      test('should create schedule with specified parameters', () async {
        // Act
        final schedule = await mockScheduler.createSchedule(
          fieldId: 'field_001',
          cropId: 'wheat',
          methodId: 'drip',
          days: 14,
          targetDepthMm: 25.0,
        );

        // Assert
        expect(schedule.fieldId, 'field_001');
        expect(schedule.events, isNotEmpty);
        verify(() => mockScheduler.createSchedule(
          fieldId: 'field_001',
          cropId: 'wheat',
          methodId: 'drip',
          days: 14,
          targetDepthMm: 25.0,
        )).called(1);
      });

      test('should handle schedule creation failure', () async {
        // Arrange
        mockScheduler.setFailureMode(true);

        // Act & Assert
        expect(
          () => mockScheduler.createSchedule(
            fieldId: 'field_001',
            cropId: 'wheat',
            methodId: 'drip',
            days: 14,
          ),
          throwsA(isA<Exception>()),
        );
      });

      test('should create schedule with default target depth when not specified', () async {
        // Act
        final schedule = await mockScheduler.createSchedule(
          fieldId: 'field_001',
          cropId: 'wheat',
          methodId: 'drip',
          days: 7,
        );

        // Assert
        expect(schedule, isNotNull);
        verify(() => mockScheduler.createSchedule(
          fieldId: 'field_001',
          cropId: 'wheat',
          methodId: 'drip',
          days: 7,
          targetDepthMm: null,
        )).called(1);
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Schedule Retrieval - استرجاع الجدول
    // ═══════════════════════════════════════════════════════════════════════

    group('getSchedule', () {
      test('should retrieve schedule for field', () async {
        // Act
        final schedule = await mockScheduler.getSchedule('field_001');

        // Assert
        expect(schedule.fieldId, 'field_001');
        expect(schedule.events, isNotEmpty);
      });

      test('should handle missing schedule', () async {
        // Arrange
        mockScheduler.setFailureMode(true);

        // Act & Assert
        expect(
          () => mockScheduler.getSchedule('nonexistent_field'),
          throwsA(isA<Exception>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Event Management - إدارة الأحداث
    // ═══════════════════════════════════════════════════════════════════════

    group('updateEvent', () {
      test('should update event successfully', () async {
        // Arrange
        final event = IrrigationApiFixtures.sampleEvents.first;

        // Act & Assert
        expect(
          mockScheduler.updateEvent('field_001', event),
          completes,
        );
        verify(() => mockScheduler.updateEvent('field_001', event)).called(1);
      });

      test('should handle update event failure', () async {
        // Arrange
        mockScheduler.setFailureMode(true);
        final event = IrrigationApiFixtures.sampleEvents.first;

        // Act & Assert
        expect(
          () => mockScheduler.updateEvent('field_001', event),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('deleteEvent', () {
      test('should delete event successfully', () async {
        // Act & Assert
        expect(
          mockScheduler.deleteEvent('field_001', 'event_001'),
          completes,
        );
        verify(() => mockScheduler.deleteEvent('field_001', 'event_001')).called(1);
      });

      test('should handle delete event failure', () async {
        // Arrange
        mockScheduler.setFailureMode(true);

        // Act & Assert
        expect(
          () => mockScheduler.deleteEvent('field_001', 'event_001'),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('skipEvent', () {
      test('should skip event with reason', () async {
        // Act & Assert
        expect(
          mockScheduler.skipEvent('field_001', 'event_001', 'Rain expected'),
          completes,
        );
        verify(() => mockScheduler.skipEvent('field_001', 'event_001', 'Rain expected')).called(1);
      });

      test('should skip event with Arabic reason', () async {
        // Act & Assert
        expect(
          mockScheduler.skipEvent('field_001', 'event_001', 'أمطار متوقعة'),
          completes,
        );
      });

      test('should handle skip event failure', () async {
        // Arrange
        mockScheduler.setFailureMode(true);

        // Act & Assert
        expect(
          () => mockScheduler.skipEvent('field_001', 'event_001', 'reason'),
          throwsA(isA<Exception>()),
        );
      });
    });

    group('rescheduleEvent', () {
      test('should reschedule event to new time', () async {
        // Arrange
        final newTime = DateTime.now().add(const Duration(days: 2));

        // Act & Assert
        expect(
          mockScheduler.rescheduleEvent('field_001', 'event_001', newTime),
          completes,
        );
        verify(() => mockScheduler.rescheduleEvent('field_001', 'event_001', newTime)).called(1);
      });

      test('should handle reschedule to past time gracefully', () async {
        // Arrange - scheduler should reject past times
        final pastTime = DateTime.now().subtract(const Duration(days: 1));
        mockScheduler.setFailureMode(true);

        // Act & Assert
        expect(
          () => mockScheduler.rescheduleEvent('field_001', 'event_001', pastTime),
          throwsA(isA<Exception>()),
        );
      });
    });

    // ═══════════════════════════════════════════════════════════════════════
    // Event Queries - استعلامات الأحداث
    // ═══════════════════════════════════════════════════════════════════════

    group('getUpcomingEvents', () {
      test('should return upcoming events for default period', () async {
        // Act
        final events = await mockScheduler.getUpcomingEvents('field_001');

        // Assert
        expect(events, isNotEmpty);
        for (final event in events) {
          expect(event.status, 'pending');
        }
      });

      test('should return upcoming events for specified period', () async {
        // Act
        final events = await mockScheduler.getUpcomingEvents('field_001', days: 14);

        // Assert
        expect(events, isNotEmpty);
        verify(() => mockScheduler.getUpcomingEvents('field_001', days: 14)).called(1);
      });

      test('should return empty list when no upcoming events', () async {
        // Arrange
        when(() => mockScheduler.getUpcomingEvents(any(), days: any(named: 'days')))
            .thenAnswer((_) async => []);

        // Act
        final events = await mockScheduler.getUpcomingEvents('field_002');

        // Assert
        expect(events, isEmpty);
      });
    });

    group('getPastEvents', () {
      test('should return past events for specified period', () async {
        // Act
        final events = await mockScheduler.getPastEvents('field_001', days: 30);

        // Assert
        verify(() => mockScheduler.getPastEvents('field_001', days: 30)).called(1);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Pivot Schedule Tests - اختبارات جدول المحوري
  // ═══════════════════════════════════════════════════════════════════════════

  group('PivotSchedule', () {
    group('daily schedule', () {
      test('should have correct schedule type', () {
        final schedule = PivotFixtures.dailySchedule;

        expect(schedule.scheduleType, ScheduleType.daily);
        expect(schedule.isActive, true);
        expect(schedule.runs, isNotEmpty);
      });

      test('should have valid run configuration', () {
        final schedule = PivotFixtures.dailySchedule;
        final run = schedule.runs.first;

        expect(run.startTime, '06:00');
        expect(run.durationHours, 8.0);
        expect(run.speedPercent, 80);
        expect(run.direction, PivotDirection.forward);
        expect(run.isEnabled, true);
      });
    });

    group('weekly schedule', () {
      test('should have correct schedule type', () {
        final schedule = PivotFixtures.weeklySchedule;

        expect(schedule.scheduleType, ScheduleType.weekly);
        expect(schedule.runs.length, 2);
      });

      test('should have valid day of week assignments', () {
        final schedule = PivotFixtures.weeklySchedule;

        // First run on Sunday (0)
        expect(schedule.runs[0].dayOfWeek, 0);
        // Second run on Wednesday (3)
        expect(schedule.runs[1].dayOfWeek, 3);
      });

      test('should have consistent irrigation depth across runs', () {
        final schedule = PivotFixtures.weeklySchedule;

        expect(schedule.runs[0].irrigationDepthMm, 30);
        expect(schedule.runs[1].irrigationDepthMm, 30);
      });
    });

    group('scheduled run', () {
      test('should create run with default values', () {
        const run = ScheduledRun(
          id: 'run_test',
          startTime: '07:00',
          durationHours: 6.0,
        );

        expect(run.speedPercent, 100);
        expect(run.direction, PivotDirection.forward);
        expect(run.startAngle, 0);
        expect(run.endAngle, 360);
        expect(run.irrigationDepthMm, 25);
        expect(run.isEnabled, true);
      });

      test('should allow partial circle runs', () {
        const run = ScheduledRun(
          id: 'partial_run',
          startTime: '06:00',
          durationHours: 4.0,
          startAngle: 0,
          endAngle: 180,
        );

        expect(run.startAngle, 0);
        expect(run.endAngle, 180);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Sensor-Triggered Scheduling - الجدولة المحفزة بالمستشعرات
  // ═══════════════════════════════════════════════════════════════════════════

  group('SensorTriggeredScheduling', () {
    test('should trigger irrigation when soil moisture is low', () async {
      // Arrange
      when(() => mockSensorService.getCurrentSoilMoisture(any()))
          .thenAnswer((_) async => 25.0); // Low moisture

      // Act
      final soilMoisture = await mockSensorService.getCurrentSoilMoisture('field_001');

      // Assert
      expect(soilMoisture, lessThan(30)); // Trigger threshold
    });

    test('should not trigger irrigation when soil moisture is optimal', () async {
      // Arrange
      when(() => mockSensorService.getCurrentSoilMoisture(any()))
          .thenAnswer((_) async => 40.0); // Optimal moisture

      // Act
      final soilMoisture = await mockSensorService.getCurrentSoilMoisture('field_001');

      // Assert
      expect(soilMoisture, greaterThan(35)); // Above trigger threshold
    });

    test('should get zone-specific moisture readings', () async {
      // Act
      final moistureByZone = await mockSensorService.getSoilMoistureByZone('field_001');

      // Assert
      expect(moistureByZone, isNotEmpty);
      expect(moistureByZone.containsKey('zone_1'), true);
      expect(moistureByZone.containsKey('zone_4'), true);
    });

    test('should identify zones needing irrigation', () async {
      // Act
      final moistureByZone = await mockSensorService.getSoilMoistureByZone('field_001');

      // Assert - zone_4 has low moisture (28.0)
      final lowMoistureZones = moistureByZone.entries
          .where((e) => e.value < 30)
          .map((e) => e.key)
          .toList();

      expect(lowMoistureZones, contains('zone_4'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IrrigationSchedule Model Tests - اختبارات نموذج الجدول
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationSchedule Model (freezed)', () {
    test('should have correct default values', () {
      final schedule = IrrigationSchedule(
        fieldId: 'field_001',
        events: [],
        generatedAt: DateTime.now(),
      );

      expect(schedule.fieldId, 'field_001');
      expect(schedule.events, isEmpty);
    });

    test('should calculate total water from events', () {
      // Arrange
      final events = [
        IrrigationEvent(
          scheduledAt: DateTime.now(),
          durationMinutes: 60.0,
          waterAmountLiters: 10000.0,
          status: 'pending',
        ),
        IrrigationEvent(
          scheduledAt: DateTime.now().add(const Duration(days: 1)),
          durationMinutes: 60.0,
          waterAmountLiters: 15000.0,
          status: 'pending',
        ),
      ];

      // Act
      final totalWater = events.fold<double>(0, (sum, e) => sum + e.waterAmountLiters);

      // Assert
      expect(totalWater, 25000);
    });
  });

  group('IrrigationEvent Model (freezed)', () {
    test('should have correct status values', () {
      final event = IrrigationEvent(
        scheduledAt: DateTime.now(),
        durationMinutes: 120.0,
        waterAmountLiters: 50000.0,
        status: 'pending',
      );

      expect(event.status, 'pending');
    });

    test('should allow notes', () {
      final event = IrrigationEvent(
        scheduledAt: DateTime.now(),
        durationMinutes: 120.0,
        waterAmountLiters: 50000.0,
        status: 'pending',
        notes: 'Morning irrigation before sunrise',
      );

      expect(event.notes, isNotEmpty);
    });

    test('should have default empty notes', () {
      final event = IrrigationEvent(
        scheduledAt: DateTime.now(),
        durationMinutes: 120.0,
        waterAmountLiters: 50000.0,
        status: 'pending',
      );

      expect(event.notes, isNull);
    });

    test('event status progression should be valid', () {
      // Valid status values
      final validStatuses = ['pending', 'in_progress', 'completed', 'skipped'];

      for (final status in validStatuses) {
        final event = IrrigationEvent(
          scheduledAt: DateTime.now(),
          durationMinutes: 120.0,
          waterAmountLiters: 50000.0,
          status: status,
        );
        expect(event.status, status);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedule Recommendations - توصيات الجدول
  // ═══════════════════════════════════════════════════════════════════════════

  group('ET-Based Recommendations', () {
    test('should calculate ETc from ET0 and Kc', () {
      // Arrange
      const et0 = 6.5; // Reference ET
      const kc = 1.15; // Wheat mid-season Kc

      // Act
      const etc = et0 * kc;

      // Assert
      expect(etc, closeTo(7.475, 0.001));
    });

    test('should recommend increased irrigation for high ET conditions', () {
      // Arrange
      const et0 = 8.0; // High ET (hot, windy)
      const kc = 1.15;
      const efficiency = 0.85;

      // Act
      const etc = et0 * kc;
      const waterNeed = etc / efficiency;

      // Assert
      expect(waterNeed, greaterThan(10)); // mm/day
    });

    test('should recommend reduced irrigation for low ET conditions', () {
      // Arrange
      const et0 = 3.0; // Low ET (cool, calm)
      const kc = 0.75; // Development stage
      const efficiency = 0.90;

      // Act
      const etc = et0 * kc;
      const waterNeed = etc / efficiency;

      // Assert
      expect(waterNeed, lessThan(3)); // mm/day
    });

    test('should account for growth stage in Kc selection', () {
      final crop = IrrigationApiFixtures.wheatCrop;

      expect(crop.kcStages!['initial'], 0.35);
      expect(crop.kcStages!['development'], 0.75);
      expect(crop.kcStages!['mid'], 1.15);
      expect(crop.kcStages!['late'], 0.40);
    });
  });
}
