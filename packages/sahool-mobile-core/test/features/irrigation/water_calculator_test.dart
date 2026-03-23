/// Water Calculator Tests
/// اختبارات حاسبة المياه
///
/// Comprehensive tests for water calculation functionality including:
/// - ETc calculations
/// - Water requirement conversions (mm, liters, m3)
/// - Irrigation duration calculations
/// - Pivot water volume calculations
/// - Sector area calculations
/// - Efficiency calculations
/// - Water balance calculations
/// - Irrigation scheduling calculations

import 'dart:math' as math;

import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/advisor/data/models/irrigation_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/span_zone_models.dart';

import 'irrigation_fixtures.dart';
import 'irrigation_mocks.dart';

void main() {
  late MockWaterCalculator mockCalculator;

  setUpAll(() {
    registerIrrigationFallbackValues();
  });

  setUp(() {
    mockCalculator = MockWaterCalculator();
    mockCalculator.setupDefaults();
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ETc Calculations - حسابات البخر-نتح
  // ═══════════════════════════════════════════════════════════════════════════

  group('ETc Calculations', () {
    test('should calculate ETc from ET0 and Kc', () {
      // Arrange
      const et0 = 6.5; // Reference evapotranspiration (mm/day)
      const kc = 1.15; // Crop coefficient for wheat mid-season

      // Act
      final etc = mockCalculator.calculateETc(et0, kc);

      // Assert
      expect(etc, closeTo(7.475, 0.001));
    });

    test('should calculate ETc for different growth stages', () {
      const et0 = 6.0;
      final crop = IrrigationApiFixtures.wheatCrop;

      // Initial stage
      final etcInitial = et0 * crop.kcStages!['initial']!;
      expect(etcInitial, closeTo(2.1, 0.01)); // 6.0 * 0.35

      // Development stage
      final etcDev = et0 * crop.kcStages!['development']!;
      expect(etcDev, closeTo(4.5, 0.01)); // 6.0 * 0.75

      // Mid-season stage
      final etcMid = et0 * crop.kcStages!['mid']!;
      expect(etcMid, closeTo(6.9, 0.01)); // 6.0 * 1.15

      // Late stage
      final etcLate = et0 * crop.kcStages!['late']!;
      expect(etcLate, closeTo(2.4, 0.01)); // 6.0 * 0.40
    });

    test('should handle zero ET0', () {
      // Act
      final etc = mockCalculator.calculateETc(0.0, 1.15);

      // Assert
      expect(etc, 0.0);
    });

    test('should handle crops without stage-specific Kc', () {
      final crop = IrrigationApiFixtures.datePalmCrop;

      // Use single Kc value
      const et0 = 7.0;
      final etc = et0 * crop.kc;

      expect(etc, closeTo(6.65, 0.01)); // 7.0 * 0.95
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Need Calculations - حسابات احتياجات المياه
  // ═══════════════════════════════════════════════════════════════════════════

  group('Water Need Calculations', () {
    test('should calculate gross water need considering efficiency', () {
      // Arrange
      const etc = 7.0; // mm/day
      const efficiency = 0.85; // 85% efficiency (pivot irrigation)

      // Act
      final grossWaterNeed = mockCalculator.calculateWaterNeedMm(etc, efficiency);

      // Assert
      // 7.0 / 0.85 = 8.24 mm
      expect(grossWaterNeed, closeTo(8.24, 0.01));
    });

    test('should calculate water need for different irrigation methods', () {
      const etc = 6.0;

      // Drip irrigation (90% efficiency)
      final dripNeed = etc / 0.90;
      expect(dripNeed, closeTo(6.67, 0.01));

      // Sprinkler irrigation (75% efficiency)
      final sprinklerNeed = etc / 0.75;
      expect(sprinklerNeed, closeTo(8.0, 0.01));

      // Flood irrigation (60% efficiency)
      final floodNeed = etc / 0.60;
      expect(floodNeed, closeTo(10.0, 0.01));

      // Pivot irrigation (85% efficiency)
      final pivotNeed = etc / 0.85;
      expect(pivotNeed, closeTo(7.06, 0.01));
    });

    test('should account for soil moisture deficit', () {
      // Arrange
      const etc = 6.0;
      const efficiency = 0.90;
      const soilMoistureDeficit = 15.0; // mm

      // Act - need to replenish deficit plus daily need
      final waterNeed = mockCalculator.calculateWaterNeedMm(
        etc,
        efficiency,
        soilMoistureDeficit: soilMoistureDeficit,
      );

      // Assert - should be greater than just ETc/efficiency
      expect(waterNeed, greaterThanOrEqualTo(etc / efficiency));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Unit Conversions - تحويل الوحدات
  // ═══════════════════════════════════════════════════════════════════════════

  group('Unit Conversions', () {
    test('should convert mm to liters for given area', () {
      // Arrange
      const depthMm = 25.0;
      const areaHectares = 5.0;

      // Act
      final liters = mockCalculator.convertMmToLiters(depthMm, areaHectares);

      // Assert
      // 1 mm on 1 hectare = 10,000 liters
      // 25 mm on 5 hectares = 25 * 5 * 10,000 = 1,250,000 liters
      expect(liters, closeTo(1250000, 1));
    });

    test('should convert liters to cubic meters', () {
      // Arrange
      const liters = 1250000.0;

      // Act
      final m3 = mockCalculator.convertLitersToM3(liters);

      // Assert
      expect(m3, closeTo(1250.0, 0.01));
    });

    test('should handle small area conversions', () {
      // 1 mm on 0.1 hectare = 1,000 liters
      final liters = mockCalculator.convertMmToLiters(1.0, 0.1);
      expect(liters, closeTo(1000, 1));
    });

    test('should handle large area conversions', () {
      // 50 mm on 100 hectares = 50,000,000 liters = 50,000 m3
      final liters = mockCalculator.convertMmToLiters(50.0, 100.0);
      final m3 = mockCalculator.convertLitersToM3(liters);
      expect(m3, closeTo(50000, 1));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Duration - مدة الري
  // ═══════════════════════════════════════════════════════════════════════════

  group('Irrigation Duration Calculations', () {
    test('should calculate irrigation duration from volume and flow rate', () {
      // Arrange
      const waterLiters = 250000.0; // 250 m3
      const flowRateLph = 50000.0; // 50 m3/hour

      // Act
      final durationMinutes = mockCalculator.calculateIrrigationDuration(
        waterLiters,
        flowRateLph,
      );

      // Assert
      // 250,000 / 50,000 = 5 hours = 300 minutes
      expect(durationMinutes, closeTo(300, 1));
    });

    test('should handle drip irrigation with low flow rate', () {
      // Arrange
      const waterLiters = 50000.0; // 50 m3
      const flowRateLph = 5000.0; // 5 m3/hour

      // Act
      final durationMinutes = mockCalculator.calculateIrrigationDuration(
        waterLiters,
        flowRateLph,
      );

      // Assert
      // 50,000 / 5,000 = 10 hours = 600 minutes
      expect(durationMinutes, closeTo(600, 1));
    });

    test('should handle pivot irrigation with high flow rate', () {
      // Arrange
      const waterLiters = 4000000.0; // 4,000 m3
      const flowRateLph = 800000.0; // 800 m3/hour

      // Act
      final durationMinutes = mockCalculator.calculateIrrigationDuration(
        waterLiters,
        flowRateLph,
      );

      // Assert
      // 4,000,000 / 800,000 = 5 hours = 300 minutes
      expect(durationMinutes, closeTo(300, 1));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Pivot Water Volume - حجم مياه المحوري
  // ═══════════════════════════════════════════════════════════════════════════

  group('Pivot Water Volume Calculations', () {
    test('should calculate water volume for full circle', () {
      // Arrange
      const radiusMeters = 400.0;
      const depthMm = 25.0;

      // Act
      final volumeLiters = mockCalculator.calculatePivotWaterVolume(
        radiusMeters: radiusMeters,
        depthMm: depthMm,
      );

      // Assert
      // Area = pi * r^2 = 3.14159 * 400^2 = 502,654.8 m2
      // Volume = Area * depth = 502,654.8 * 0.025 = 12,566.4 m3 = 12,566,400 liters
      expect(volumeLiters, closeTo(12566370, 1000));
    });

    test('should calculate water volume for partial circle', () {
      // Arrange
      const radiusMeters = 400.0;
      const depthMm = 25.0;

      // Act
      final volumeLiters = mockCalculator.calculatePivotWaterVolume(
        radiusMeters: radiusMeters,
        depthMm: depthMm,
        startAngle: 0,
        endAngle: 180, // Half circle
      );

      // Assert
      // Half of full circle
      expect(volumeLiters, closeTo(6283185, 1000));
    });

    test('should calculate water volume for quarter circle', () {
      // Arrange
      const radiusMeters = 400.0;
      const depthMm = 25.0;

      // Act
      final volumeLiters = mockCalculator.calculatePivotWaterVolume(
        radiusMeters: radiusMeters,
        depthMm: depthMm,
        startAngle: 0,
        endAngle: 90, // Quarter circle
      );

      // Assert
      // Quarter of full circle
      expect(volumeLiters, closeTo(3141593, 1000));
    });

    test('should handle small pivot', () {
      // Arrange
      const radiusMeters = 200.0;
      const depthMm = 20.0;

      // Act
      final volumeLiters = mockCalculator.calculatePivotWaterVolume(
        radiusMeters: radiusMeters,
        depthMm: depthMm,
      );

      // Assert
      // Area = pi * 200^2 = 125,663.7 m2
      // Volume = 125,663.7 * 0.020 = 2,513.3 m3 = 2,513,300 liters
      expect(volumeLiters, closeTo(2513274, 500));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Sector Area Calculations - حسابات مساحة القطاع
  // ═══════════════════════════════════════════════════════════════════════════

  group('Sector Area Calculations', () {
    test('should calculate quarter sector area', () {
      // Arrange
      const radiusMeters = 400.0;
      const startAngle = 0.0;
      const endAngle = 90.0;

      // Act
      final areaHectares = mockCalculator.calculateSectorArea(
        radiusMeters,
        startAngle,
        endAngle,
      );

      // Assert
      // Quarter of full circle area (50.27 ha) = 12.57 ha
      expect(areaHectares, closeTo(12.57, 0.1));
    });

    test('should calculate half sector area', () {
      // Arrange
      const radiusMeters = 400.0;
      const startAngle = 0.0;
      const endAngle = 180.0;

      // Act
      final areaHectares = mockCalculator.calculateSectorArea(
        radiusMeters,
        startAngle,
        endAngle,
      );

      // Assert
      expect(areaHectares, closeTo(25.13, 0.1));
    });

    test('should calculate arbitrary sector area', () {
      // Arrange
      const radiusMeters = 350.0;
      const startAngle = 30.0;
      const endAngle = 150.0; // 120 degree span

      // Act
      final areaHectares = mockCalculator.calculateSectorArea(
        radiusMeters,
        startAngle,
        endAngle,
      );

      // Assert
      // Full circle area = pi * 350^2 / 10000 = 38.48 ha
      // 120/360 = 1/3 of full circle = 12.83 ha
      expect(areaHectares, closeTo(12.83, 0.1));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Efficiency Calculations - حسابات الكفاءة
  // ═══════════════════════════════════════════════════════════════════════════

  group('Efficiency Calculations', () {
    test('should calculate irrigation efficiency', () {
      // Arrange
      const appliedMm = 25.0;
      const consumedMm = 21.25;

      // Act
      final efficiency = mockCalculator.calculateEfficiency(appliedMm, consumedMm);

      // Assert
      expect(efficiency, closeTo(85.0, 0.1));
    });

    test('should handle perfect efficiency', () {
      // Arrange
      const appliedMm = 25.0;
      const consumedMm = 25.0;

      // Act
      final efficiency = mockCalculator.calculateEfficiency(appliedMm, consumedMm);

      // Assert
      expect(efficiency, 100.0);
    });

    test('should handle low efficiency', () {
      // Arrange
      const appliedMm = 25.0;
      const consumedMm = 15.0; // 60% efficiency

      // Act
      final efficiency = mockCalculator.calculateEfficiency(appliedMm, consumedMm);

      // Assert
      expect(efficiency, closeTo(60.0, 0.1));
    });

    test('should validate efficiency ratings', () {
      // High efficiency (>85%)
      expect(mockCalculator.calculateEfficiency(25.0, 22.0), greaterThan(85));

      // Good efficiency (70-85%)
      expect(mockCalculator.calculateEfficiency(25.0, 19.0), inInclusiveRange(70, 85));

      // Low efficiency (<70%)
      expect(mockCalculator.calculateEfficiency(25.0, 15.0), lessThan(70));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Balance Calculations - حسابات التوازن المائي
  // ═══════════════════════════════════════════════════════════════════════════

  group('Water Balance Calculations', () {
    test('should return optimal balance when soil moisture is adequate', () {
      // Act
      final balance = mockCalculator.calculateWaterBalance(
        soilMoisture: 40.0,
        fieldCapacity: 45.0,
        wiltingPoint: 15.0,
        madFraction: 0.55,
        rootDepthMm: 1500,
      );

      // Assert
      expect(balance.status, 'optimal');
      expect(balance.irrigationNeeded, false);
    });

    test('should detect low water balance', () {
      // Arrange
      final balance = IrrigationModelFixtures.lowWaterBalance;

      // Assert
      expect(balance.status, 'low');
      expect(balance.irrigationNeeded, true);
      expect(balance.recommendedWaterMm, greaterThan(0));
      expect(balance.depletionPercent, greaterThan(50));
    });

    test('should detect critical water balance', () {
      // Arrange
      final balance = IrrigationModelFixtures.criticalWaterBalance;

      // Assert
      expect(balance.status, 'critical');
      expect(balance.irrigationNeeded, true);
      expect(balance.recommendedWaterMm, greaterThan(20));
      expect(balance.depletionPercent, greaterThan(80));
    });

    test('should calculate available water', () {
      // Arrange
      const soilMoisture = 38.0;
      const wiltingPoint = 15.0;

      // Act
      final availableWater = soilMoisture - wiltingPoint;

      // Assert
      expect(availableWater, 23.0);
    });

    test('should calculate depletion percentage', () {
      // Arrange
      const fieldCapacity = 45.0;
      const wiltingPoint = 15.0;
      const soilMoisture = 30.0;

      // Act
      final totalAvailable = fieldCapacity - wiltingPoint; // 30
      final current = soilMoisture - wiltingPoint; // 15
      final depletion = ((totalAvailable - current) / totalAvailable) * 100; // 50%

      // Assert
      expect(depletion, 50.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Date Calculations - حسابات تاريخ الري
  // ═══════════════════════════════════════════════════════════════════════════

  group('Next Irrigation Date Calculations', () {
    test('should calculate days until irrigation needed', () {
      // Arrange
      const currentSoilMoisture = 40.0;
      const fieldCapacity = 45.0;
      const dailyETc = 6.5;
      const madFraction = 0.55;
      const wiltingPoint = 15.0;

      // Act
      // Available water = 40 - 15 = 25
      // Total available = 45 - 15 = 30
      // MAD = 30 * 0.55 = 16.5 (maximum allowable depletion)
      // Current available above MAD threshold = 25 - (30 - 16.5) = 11.5
      // Days until irrigation = 11.5 / 6.5 = 1.77 days
      final daysUntilIrrigation = (currentSoilMoisture - wiltingPoint -
          (fieldCapacity - wiltingPoint) * (1 - madFraction)) / dailyETc;

      // Assert
      expect(daysUntilIrrigation, greaterThan(0));
    });

    test('should calculate next irrigation date', () {
      // Act
      final nextDate = mockCalculator.calculateNextIrrigationDate(
        currentSoilMoisture: 40.0,
        fieldCapacity: 45.0,
        dailyETc: 6.5,
        madFraction: 0.55,
      );

      // Assert
      expect(nextDate.isAfter(DateTime.now()), true);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // VRI Zone Grid Calculations - حسابات شبكة مناطق VRI
  // ═══════════════════════════════════════════════════════════════════════════

  group('VRI Zone Grid Calculations', () {
    test('should calculate zone statistics from uniform grid', () {
      // Arrange
      final grid = SpanZoneFixtures.uniformGrid;

      // Act
      final stats = VRIZoneStatistics.fromGrid(grid);

      // Assert
      expect(stats.totalZones, 32); // 4 spans * 8 divisions
      expect(stats.activeZones, 32);
      expect(stats.offZones, 0);
      expect(stats.avgApplicationRate, 100.0);
    });

    test('should calculate zone statistics from variable grid', () {
      // Arrange
      final grid = SpanZoneFixtures.variableGrid;

      // Act
      final stats = VRIZoneStatistics.fromGrid(grid);

      // Assert
      expect(stats.totalZones, greaterThan(0));
      expect(stats.rateDistribution, isNotEmpty);
    });

    test('should identify water savings from variable rates', () {
      // Arrange - grid with varied rates
      final grid = VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'test',
        spanCount: 4,
        angularDivisions: 8,
        defaultApplicationRate: 85, // 15% reduction
      );

      // Act
      final stats = VRIZoneStatistics.fromGrid(grid);

      // Assert
      expect(stats.waterSavingsPercent, closeTo(15.0, 0.1));
    });

    test('should get zone at specific angle and span', () {
      // Arrange
      final grid = SpanZoneFixtures.uniformGrid;

      // Act
      final zone = grid.getZoneAt(0, 45.0);

      // Assert
      expect(zone, isNotNull);
      expect(zone!.spanNumber, 1);
    });

    test('should calculate average rate at angle', () {
      // Arrange
      final grid = SpanZoneFixtures.uniformGrid;

      // Act
      final avgRate = grid.avgApplicationRateAtAngle(45.0);

      // Assert
      expect(avgRate, 100.0); // Uniform grid
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Span Configuration Calculations - حسابات تهيئة البرج
  // ═══════════════════════════════════════════════════════════════════════════

  group('Span Configuration Calculations', () {
    test('should calculate arc length at span distance', () {
      // Arrange
      final span = SpanZoneFixtures.sampleSpanConfig;

      // Act
      final arcLength = span.arcLengthAt360;

      // Assert
      // 2 * pi * 60 = 376.99 m
      expect(arcLength, closeTo(376.99, 0.1));
    });

    test('should get effective rate for angle without zones', () {
      // Arrange
      final span = SpanZoneFixtures.sampleSpanConfig.copyWith(zones: []);

      // Act
      final rate = span.effectiveRateForAngle(45.0);

      // Assert
      expect(rate, span.baseApplicationRateMmHr);
    });

    test('should get effective rate for angle with zones', () {
      // Arrange
      final span = SpanZoneFixtures.sampleSpanConfig.copyWith(
        zones: [
          SpanZone(
            id: 'zone_test',
            spanNumber: 1,
            zoneNumber: 1,
            startAngle: 0,
            endAngle: 90,
            applicationRatePercent: 120,
          ),
        ],
      );

      // Act
      final rate = span.effectiveRateForAngle(45.0);

      // Assert
      // Base rate * 120% = 6.0 * 1.2 = 7.2
      expect(rate, closeTo(7.2, 0.01));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Integration Scenarios - سيناريوهات التكامل
  // ═══════════════════════════════════════════════════════════════════════════

  group('Integration Scenarios', () {
    test('should calculate full irrigation requirement for wheat field', () {
      // Arrange
      final crop = IrrigationApiFixtures.wheatCrop;
      final method = IrrigationApiFixtures.dripMethod;
      const et0 = 6.5;
      const areaHectares = 5.0;
      const growthStage = 'mid';

      // Act
      final kc = crop.kcStages![growthStage]!;
      final etc = et0 * kc;
      final grossWaterNeedMm = etc / method.efficiency;
      final waterNeedLiters = grossWaterNeedMm * areaHectares * 10000;
      final waterNeedM3 = waterNeedLiters / 1000;

      // Assert
      expect(etc, closeTo(7.475, 0.01));
      expect(grossWaterNeedMm, closeTo(8.31, 0.01));
      expect(waterNeedLiters, closeTo(415277, 100));
      expect(waterNeedM3, closeTo(415.28, 0.5));
    });

    test('should calculate pivot irrigation cycle parameters', () {
      // Arrange
      final pivot = PivotFixtures.sampleFullCirclePivot;
      const depthMm = 25.0;
      const targetSpeedPercent = 80.0;

      // Act
      // Calculate water volume
      final areaM2 = math.pi * pivot.lengthMeters * pivot.lengthMeters;
      final volumeLiters = areaM2 * (depthMm / 1000) * 1000;
      final volumeM3 = volumeLiters / 1000;

      // Calculate duration at 80% speed
      final baseFlowRate = pivot.flowRateLph; // L/h
      final effectiveFlowRate = baseFlowRate * (targetSpeedPercent / 100);
      final durationHours = volumeLiters / effectiveFlowRate;
      final durationMinutes = durationHours * 60;

      // Assert
      expect(volumeM3, closeTo(12566.4, 10));
      expect(durationMinutes, greaterThan(0));
    });

    test('should compare water efficiency across methods', () {
      // Arrange
      const etc = 6.0; // Daily ETc

      // Act
      final dripWater = etc / IrrigationApiFixtures.dripMethod.efficiency;
      final sprinklerWater = etc / IrrigationApiFixtures.sprinklerMethod.efficiency;
      final pivotWater = etc / IrrigationApiFixtures.pivotMethod.efficiency;
      final floodWater = etc / IrrigationApiFixtures.floodMethod.efficiency;

      // Assert - drip uses least water, flood uses most
      expect(dripWater, lessThan(sprinklerWater));
      expect(sprinklerWater, lessThan(floodWater));
      expect(pivotWater, lessThan(floodWater));

      // Water savings compared to flood
      final dripSavings = ((floodWater - dripWater) / floodWater) * 100;
      expect(dripSavings, closeTo(33.3, 1)); // Drip saves ~33% vs flood
    });
  });
}
