/// Irrigation Test Fixtures
/// بيانات اختبار الري
///
/// Provides test data for irrigation feature unit tests.
/// يوفر بيانات اختبار لوحدة اختبارات ميزة الري
library;

import 'package:sahool_field_app/features/advisor/data/models/irrigation_models.dart'
    hide IrrigationEvent, IrrigationCalculation, IrrigationSchedule; // Hide to avoid conflict with irrigation_api
import 'package:sahool_field_app/features/irrigation/data/remote/irrigation_api.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/pivot_models.dart';
import 'package:sahool_field_app/features/pivot_irrigation/domain/models/span_zone_models.dart';

/// Test fixtures for irrigation API models
class IrrigationApiFixtures {
  // ═══════════════════════════════════════════════════════════════════════════
  // Crops - المحاصيل
  // ═══════════════════════════════════════════════════════════════════════════

  static IrrigationCrop get wheatCrop => IrrigationCrop(
        id: 'wheat',
        nameAr: 'قمح',
        nameEn: 'Wheat',
        kc: 1.15,
        kcStages: {
          'initial': 0.35,
          'development': 0.75,
          'mid': 1.15,
          'late': 0.40,
        },
        rootDepthMm: 1500,
        madFraction: 0.55,
      );

  static IrrigationCrop get tomatoCrop => IrrigationCrop(
        id: 'tomato',
        nameAr: 'طماطم',
        nameEn: 'Tomato',
        kc: 1.15,
        kcStages: {
          'initial': 0.60,
          'development': 0.90,
          'mid': 1.15,
          'late': 0.80,
        },
        rootDepthMm: 1000,
        madFraction: 0.40,
      );

  static IrrigationCrop get datePalmCrop => IrrigationCrop(
        id: 'date_palm',
        nameAr: 'نخيل',
        nameEn: 'Date Palm',
        kc: 0.95,
        rootDepthMm: 2000,
        madFraction: 0.50,
      );

  static List<IrrigationCrop> get sampleCrops => [
        wheatCrop,
        tomatoCrop,
        datePalmCrop,
      ];

  static Map<String, dynamic> get wheatCropJson => {
        'id': 'wheat',
        'name_ar': 'قمح',
        'name_en': 'Wheat',
        'kc': 1.15,
        'kc_stages': {
          'initial': 0.35,
          'development': 0.75,
          'mid': 1.15,
          'late': 0.40,
        },
        'root_depth_mm': 1500,
        'mad_fraction': 0.55,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Methods - طرق الري
  // ═══════════════════════════════════════════════════════════════════════════

  static IrrigationMethod get dripMethod => IrrigationMethod(
        id: 'drip',
        nameAr: 'ري بالتنقيط',
        nameEn: 'Drip Irrigation',
        efficiency: 0.90,
        description: 'High efficiency localized irrigation',
      );

  static IrrigationMethod get sprinklerMethod => IrrigationMethod(
        id: 'sprinkler',
        nameAr: 'ري بالرش',
        nameEn: 'Sprinkler Irrigation',
        efficiency: 0.75,
        description: 'Overhead sprinkler system',
      );

  static IrrigationMethod get pivotMethod => IrrigationMethod(
        id: 'pivot',
        nameAr: 'ري محوري',
        nameEn: 'Center Pivot',
        efficiency: 0.85,
        description: 'Center pivot irrigation system',
      );

  static IrrigationMethod get floodMethod => IrrigationMethod(
        id: 'flood',
        nameAr: 'ري غمر',
        nameEn: 'Flood Irrigation',
        efficiency: 0.60,
        description: 'Surface flood irrigation',
      );

  static List<IrrigationMethod> get sampleMethods => [
        dripMethod,
        sprinklerMethod,
        pivotMethod,
        floodMethod,
      ];

  static Map<String, dynamic> get dripMethodJson => {
        'id': 'drip',
        'name_ar': 'ري بالتنقيط',
        'name_en': 'Drip Irrigation',
        'efficiency': 0.90,
        'description': 'High efficiency localized irrigation',
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Calculations - الحسابات
  // ═══════════════════════════════════════════════════════════════════════════

  static IrrigationCalculationRequest get sampleCalculationRequest =>
      IrrigationCalculationRequest(
        cropId: 'wheat',
        methodId: 'drip',
        areaHectares: 5.0,
        et0: 6.5,
        soilMoistureCurrent: 35.0,
        soilMoistureFieldCapacity: 45.0,
        growthStage: 'mid',
      );

  static IrrigationCalculation get sampleCalculation => IrrigationCalculation(
        waterNeedMm: 25.0,
        waterNeedLiters: 250000.0,
        waterNeedM3: 250.0,
        irrigationDurationMinutes: 180.0,
        etc: 7.48,
        recommendation: 'Apply 25mm irrigation today in the early morning',
        recommendationAr: 'قم بري 25 ملم اليوم في الصباح الباكر',
        nextIrrigationDate: DateTime.now().add(const Duration(days: 3)),
      );

  static Map<String, dynamic> get sampleCalculationJson => {
        'water_need_mm': 25.0,
        'water_need_liters': 250000.0,
        'water_need_m3': 250.0,
        'irrigation_duration_minutes': 180.0,
        'etc': 7.48,
        'recommendation': 'Apply 25mm irrigation today in the early morning',
        'recommendation_ar': 'قم بري 25 ملم اليوم في الصباح الباكر',
        'next_irrigation_date': DateTime.now()
            .add(const Duration(days: 3))
            .toIso8601String(),
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedule - الجدول
  // ═══════════════════════════════════════════════════════════════════════════

  static IrrigationSchedule get sampleSchedule => IrrigationSchedule(
        fieldId: 'field_001',
        events: sampleEvents,
        generatedAt: DateTime.now(),
      );

  static List<IrrigationEvent> get sampleEvents => [
        IrrigationEvent(
          scheduledAt: DateTime.now().add(const Duration(days: 1, hours: 6)),
          durationMinutes: 120.0,
          waterAmountLiters: 50000.0,
          status: 'pending',
          notes: 'Morning irrigation',
        ),
        IrrigationEvent(
          scheduledAt: DateTime.now().add(const Duration(days: 4, hours: 6)),
          durationMinutes: 120.0,
          waterAmountLiters: 50000.0,
          status: 'pending',
          notes: null,
        ),
        IrrigationEvent(
          scheduledAt: DateTime.now().add(const Duration(days: 7, hours: 6)),
          durationMinutes: 90.0,
          waterAmountLiters: 37500.0,
          status: 'pending',
          notes: null,
        ),
      ];

  static Map<String, dynamic> get sampleScheduleJson => {
        'field_id': 'field_001',
        'events': [
          {
            'scheduled_at': DateTime.now()
                .add(const Duration(days: 1, hours: 6))
                .toIso8601String(),
            'duration_minutes': 120.0,
            'water_amount_liters': 50000.0,
            'status': 'pending',
            'notes': 'Morning irrigation',
          },
          {
            'scheduled_at': DateTime.now()
                .add(const Duration(days: 4, hours: 6))
                .toIso8601String(),
            'duration_minutes': 120.0,
            'water_amount_liters': 50000.0,
            'status': 'pending',
            'notes': null,
          },
        ],
        'generated_at': DateTime.now().toIso8601String(),
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Sensor Readings - قراءات المستشعرات
  // ═══════════════════════════════════════════════════════════════════════════

  static Map<String, dynamic> get sampleSensorReading => {
        'field_id': 'field_001',
        'sensor_type': 'soil_moisture',
        'value': 38.5,
        'unit': '%',
        'timestamp': DateTime.now().toIso8601String(),
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Balance - التوازن المائي
  // ═══════════════════════════════════════════════════════════════════════════

  static Map<String, dynamic> get sampleWaterBalance => {
        'soil_moisture_percent': 38.5,
        'field_capacity': 45.0,
        'wilting_point': 15.0,
        'available_water': 23.5,
        'depletion_percent': 25.0,
        'status': 'optimal',
        'irrigation_needed': false,
        'recommended_water_mm': 0.0,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Efficiency - الكفاءة
  // ═══════════════════════════════════════════════════════════════════════════

  static Map<String, dynamic> get sampleEfficiency => {
        'efficiency_percent': 87.5,
        'applied_water_mm': 25.0,
        'consumed_water_mm': 21.875,
        'loss_mm': 3.125,
        'rating': 'good',
        'rating_ar': 'جيد',
      };
}

/// Test fixtures for advisor irrigation models (freezed)
class IrrigationModelFixtures {
  static IrrigationRequest get sampleRequest => const IrrigationRequest(
        cropType: 'wheat',
        growthStage: 'tillering',
        fieldArea: 5.0,
        soilType: 'loam',
        irrigationMethod: 'drip',
        currentSoilMoisture: 35.0,
        temperature: 28.0,
        humidity: 45.0,
        governorate: 'Sana\'a',
      );

  static IrrigationRequest get pivotRequest => const IrrigationRequest(
        cropType: 'wheat',
        growthStage: 'mid',
        fieldArea: 50.0,
        soilType: 'sandy_loam',
        irrigationMethod: 'pivot',
        currentSoilMoisture: 32.0,
        temperature: 30.0,
        humidity: 40.0,
        governorate: 'Marib',
      );

  static const sampleRequestJson = {
    'cropType': 'wheat',
    'growthStage': 'tillering',
    'fieldArea': 5.0,
    'soilType': 'loam',
    'irrigationMethod': 'drip',
    'currentSoilMoisture': 35.0,
    'temperature': 28.0,
    'humidity': 45.0,
    'governorate': 'Sana\'a',
  };

  static WaterBalance get optimalWaterBalance => const WaterBalance(
        soilMoisturePercent: 40.0,
        fieldCapacity: 45.0,
        wiltingPoint: 15.0,
        availableWater: 25.0,
        depletionPercent: 18.0,
        status: 'optimal',
        statusAr: 'مثالي',
        irrigationNeeded: false,
        recommendedWaterMm: 0.0,
      );

  static WaterBalance get lowWaterBalance => const WaterBalance(
        soilMoisturePercent: 22.0,
        fieldCapacity: 45.0,
        wiltingPoint: 15.0,
        availableWater: 7.0,
        depletionPercent: 65.0,
        status: 'low',
        statusAr: 'منخفض',
        irrigationNeeded: true,
        recommendedWaterMm: 18.0,
      );

  static WaterBalance get criticalWaterBalance => const WaterBalance(
        soilMoisturePercent: 18.0,
        fieldCapacity: 45.0,
        wiltingPoint: 15.0,
        availableWater: 3.0,
        depletionPercent: 85.0,
        status: 'critical',
        statusAr: 'حرج',
        irrigationNeeded: true,
        recommendedWaterMm: 25.0,
      );

  static SensorReading get soilMoistureReading => SensorReading(
        sensorId: 'sensor_001',
        sensorType: 'soil_moisture',
        value: 38.5,
        unit: '%',
        timestamp: DateTime.now(),
        fieldId: 'field_001',
        location: 'center',
      );

  static SensorReading get temperatureReading => SensorReading(
        sensorId: 'sensor_002',
        sensorType: 'temperature',
        value: 28.5,
        unit: 'C',
        timestamp: DateTime.now(),
        fieldId: 'field_001',
        location: 'north',
      );

  static List<SensorReading> get sampleReadings => [
        soilMoistureReading,
        temperatureReading,
        SensorReading(
          sensorId: 'sensor_003',
          sensorType: 'humidity',
          value: 45.0,
          unit: '%',
          timestamp: DateTime.now(),
          fieldId: 'field_001',
          location: 'center',
        ),
      ];

  static IrrigationMethodOption get dripOption => const IrrigationMethodOption(
        id: 'drip',
        name: 'Drip Irrigation',
        nameAr: 'ري بالتنقيط',
        efficiency: 90.0,
        description: 'High efficiency water delivery directly to plant roots',
        descriptionAr: 'توصيل مياه عالي الكفاءة مباشرة إلى جذور النباتات',
        suitableCrops: ['vegetables', 'fruit_trees', 'vines'],
        suitableCropsAr: ['خضروات', 'أشجار فاكهة', 'كروم'],
      );

  static CropWaterRequirement get wheatRequirement =>
      const CropWaterRequirement(
        cropId: 'wheat',
        cropName: 'Wheat',
        cropNameAr: 'قمح',
        stageRequirements: {
          'germination': 3.0,
          'tillering': 5.0,
          'stem_elongation': 6.0,
          'heading': 7.0,
          'grain_filling': 5.0,
          'maturity': 2.0,
        },
        kcInitial: 0.35,
        kcMid: 1.15,
        kcEnd: 0.40,
        rootDepthCm: 150,
        criticalDepletionFraction: 0.55,
      );
}

/// Test fixtures for pivot irrigation models
class PivotFixtures {
  // ═══════════════════════════════════════════════════════════════════════════
  // Pivot Configuration - إعدادات المحوري
  // ═══════════════════════════════════════════════════════════════════════════

  static PivotConfiguration get sampleFullCirclePivot => PivotConfiguration(
        id: 'pivot_001',
        fieldId: 'field_001',
        name: 'North Field Pivot',
        nameAr: 'محوري الحقل الشمالي',
        centerLat: 15.3694,
        centerLng: 44.1910,
        lengthMeters: 400.0,
        overhangMeters: 15.0,
        spansCount: 7,
        rotationDirection: RotationDirection.clockwise,
        areaHectares: 50.27,
        pivotType: PivotType.fullCircle,
        startAngle: 0,
        endAngle: 360,
        flowRateLph: 800000.0,
        operatingPressureBar: 2.5,
        hasVRI: false,
        hasEndGun: true,
        hasCornerSystem: false,
        sectors: sampleSectors,
        createdAt: DateTime.now().subtract(const Duration(days: 30)),
        updatedAt: DateTime.now(),
      );

  static PivotConfiguration get samplePartialPivot => PivotConfiguration(
        id: 'pivot_002',
        fieldId: 'field_002',
        name: 'South Field Pivot',
        nameAr: 'محوري الحقل الجنوبي',
        centerLat: 15.3500,
        centerLng: 44.1800,
        lengthMeters: 350.0,
        overhangMeters: 10.0,
        spansCount: 6,
        rotationDirection: RotationDirection.counterclockwise,
        areaHectares: 35.5,
        pivotType: PivotType.partialCircle,
        startAngle: 30,
        endAngle: 270,
        flowRateLph: 650000.0,
        operatingPressureBar: 2.3,
        hasVRI: true,
        hasEndGun: false,
        hasCornerSystem: false,
        sectors: [],
        vriZones: sampleVRIZones,
        createdAt: DateTime.now().subtract(const Duration(days: 60)),
        updatedAt: DateTime.now(),
      );

  static PivotConfiguration get smallPivot => PivotConfiguration(
        id: 'pivot_003',
        fieldId: 'field_003',
        name: 'Test Pivot',
        nameAr: 'محوري اختباري',
        centerLat: 15.4000,
        centerLng: 44.2000,
        lengthMeters: 200.0,
        overhangMeters: 0,
        spansCount: 4,
        rotationDirection: RotationDirection.clockwise,
        areaHectares: 12.57,
        pivotType: PivotType.fullCircle,
        flowRateLph: 400000.0,
        operatingPressureBar: 2.0,
        hasVRI: false,
        hasEndGun: false,
        hasCornerSystem: false,
        sectors: [],
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

  static Map<String, dynamic> get samplePivotConfigJson => {
        'id': 'pivot_001',
        'fieldId': 'field_001',
        'name': 'North Field Pivot',
        'nameAr': 'محوري الحقل الشمالي',
        'centerLat': 15.3694,
        'centerLng': 44.1910,
        'lengthMeters': 400.0,
        'overhangMeters': 15.0,
        'spansCount': 7,
        'rotationDirection': 'clockwise',
        'areaHectares': 50.27,
        'pivotType': 'full_circle',
        'startAngle': 0,
        'endAngle': 360,
        'flowRateLph': 800000.0,
        'operatingPressureBar': 2.5,
        'hasVRI': false,
        'hasEndGun': true,
        'hasCornerSystem': false,
        'sectors': [],
        'vriZones': [],
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Sectors - القطاعات
  // ═══════════════════════════════════════════════════════════════════════════

  static List<PivotSector> get sampleSectors => [
        const PivotSector(
          id: 'sector_001',
          sectorNumber: 1,
          name: 'Sector A',
          nameAr: 'قطاع أ',
          startAngle: 0,
          endAngle: 90,
          irrigationDepthMm: 25,
          applicationRateMmHr: 6.0,
          isEnabled: true,
          speedPercent: 100,
          cropType: 'wheat',
          soilType: 'loam',
          ndviValue: 0.72,
          soilMoisturePercent: 38.0,
          color: '#4CAF50',
        ),
        const PivotSector(
          id: 'sector_002',
          sectorNumber: 2,
          name: 'Sector B',
          nameAr: 'قطاع ب',
          startAngle: 90,
          endAngle: 180,
          irrigationDepthMm: 20,
          applicationRateMmHr: 6.0,
          isEnabled: true,
          speedPercent: 80,
          cropType: 'wheat',
          soilType: 'sandy_loam',
          ndviValue: 0.65,
          soilMoisturePercent: 32.0,
          color: '#FFC107',
        ),
        const PivotSector(
          id: 'sector_003',
          sectorNumber: 3,
          name: 'Sector C',
          nameAr: 'قطاع ج',
          startAngle: 180,
          endAngle: 270,
          irrigationDepthMm: 30,
          applicationRateMmHr: 6.0,
          isEnabled: true,
          speedPercent: 120,
          cropType: 'wheat',
          soilType: 'clay',
          ndviValue: 0.55,
          soilMoisturePercent: 28.0,
          color: '#FF9800',
        ),
        const PivotSector(
          id: 'sector_004',
          sectorNumber: 4,
          name: 'Sector D',
          nameAr: 'قطاع د',
          startAngle: 270,
          endAngle: 360,
          irrigationDepthMm: 25,
          applicationRateMmHr: 6.0,
          isEnabled: false,
          speedPercent: 100,
          cropType: 'fallow',
          soilType: 'loam',
          color: '#9E9E9E',
        ),
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // VRI Zones - مناطق VRI
  // ═══════════════════════════════════════════════════════════════════════════

  static List<VRIZone> get sampleVRIZones => [
        const VRIZone(
          id: 'vri_001',
          name: 'High Need Zone',
          nameAr: 'منطقة احتياج عالي',
          coordinates: [
            [15.35, 44.18],
            [15.36, 44.18],
            [15.36, 44.19],
            [15.35, 44.19],
          ],
          rateMultiplier: 1.3,
          targetSoilMoisturePercent: 65,
          zoneType: VRIZoneType.highNeed,
          color: '#2196F3',
          isActive: true,
        ),
        const VRIZone(
          id: 'vri_002',
          name: 'Normal Zone',
          nameAr: 'منطقة عادية',
          coordinates: [
            [15.34, 44.17],
            [15.35, 44.17],
            [15.35, 44.18],
            [15.34, 44.18],
          ],
          rateMultiplier: 1.0,
          targetSoilMoisturePercent: 55,
          zoneType: VRIZoneType.normal,
          color: '#4CAF50',
          isActive: true,
        ),
        const VRIZone(
          id: 'vri_003',
          name: 'Low Need Zone',
          nameAr: 'منطقة احتياج منخفض',
          coordinates: [
            [15.33, 44.16],
            [15.34, 44.16],
            [15.34, 44.17],
            [15.33, 44.17],
          ],
          rateMultiplier: 0.7,
          targetSoilMoisturePercent: 45,
          zoneType: VRIZoneType.lowNeed,
          color: '#FFC107',
          isActive: true,
        ),
      ];

  // ═══════════════════════════════════════════════════════════════════════════
  // Pivot Status - حالة المحوري
  // ═══════════════════════════════════════════════════════════════════════════

  static PivotStatus get runningStatus => PivotStatus(
        pivotId: 'pivot_001',
        currentAngle: 145.5,
        operatingStatus: PivotOperatingStatus.running,
        direction: PivotDirection.forward,
        speedPercent: 85.0,
        timerHours: 8.0,
        elapsedMinutes: 195.0,
        currentFlowRateLph: 780000.0,
        currentPressureBar: 2.4,
        endGunActive: true,
        cornerSystemActive: false,
        waterAppliedM3: 2550.0,
        energyConsumedKwh: 125.5,
        estimatedCompletionTime: DateTime.now().add(const Duration(hours: 5)),
        lastUpdated: DateTime.now(),
        activeAlerts: [],
        armEndLat: 15.3730,
        armEndLng: 44.1950,
      );

  static PivotStatus get stoppedStatus => PivotStatus(
        pivotId: 'pivot_001',
        currentAngle: 0.0,
        operatingStatus: PivotOperatingStatus.stopped,
        direction: PivotDirection.stopped,
        speedPercent: 0.0,
        timerHours: 0.0,
        elapsedMinutes: 0.0,
        currentFlowRateLph: 0.0,
        currentPressureBar: 0.0,
        endGunActive: false,
        cornerSystemActive: false,
        waterAppliedM3: 0.0,
        energyConsumedKwh: 0.0,
        lastUpdated: DateTime.now(),
        activeAlerts: [],
      );

  static PivotStatus get faultStatus => PivotStatus(
        pivotId: 'pivot_001',
        currentAngle: 200.0,
        operatingStatus: PivotOperatingStatus.fault,
        direction: PivotDirection.stopped,
        speedPercent: 0.0,
        timerHours: 6.0,
        elapsedMinutes: 180.0,
        currentFlowRateLph: 0.0,
        currentPressureBar: 1.2,
        endGunActive: false,
        cornerSystemActive: false,
        waterAppliedM3: 1500.0,
        energyConsumedKwh: 75.0,
        lastUpdated: DateTime.now(),
        activeAlerts: [lowPressureAlert],
      );

  static PivotAlert get lowPressureAlert => PivotAlert(
        id: 'alert_001',
        pivotId: 'pivot_001',
        alertType: PivotAlertType.lowPressure,
        severity: AlertSeverity.critical,
        message: 'Low pressure detected - pump may have failed',
        messageAr: 'انخفاض الضغط - ربما تعطلت المضخة',
        towerNumber: 3,
        isAcknowledged: false,
        timestamp: DateTime.now(),
      );

  // ═══════════════════════════════════════════════════════════════════════════
  // Schedules - الجداول
  // ═══════════════════════════════════════════════════════════════════════════

  static PivotSchedule get dailySchedule => PivotSchedule(
        id: 'schedule_001',
        pivotId: 'pivot_001',
        name: 'Daily Morning Run',
        nameAr: 'تشغيل صباحي يومي',
        scheduleType: ScheduleType.daily,
        runs: [
          const ScheduledRun(
            id: 'run_001',
            startTime: '06:00',
            durationHours: 8.0,
            speedPercent: 80,
            direction: PivotDirection.forward,
            startAngle: 0,
            endAngle: 360,
            irrigationDepthMm: 25,
            isEnabled: true,
          ),
        ],
        isActive: true,
        createdAt: DateTime.now(),
      );

  static PivotSchedule get weeklySchedule => PivotSchedule(
        id: 'schedule_002',
        pivotId: 'pivot_001',
        name: 'Weekly Schedule',
        nameAr: 'جدول أسبوعي',
        scheduleType: ScheduleType.weekly,
        runs: [
          const ScheduledRun(
            id: 'run_002',
            dayOfWeek: 0, // Sunday
            startTime: '05:30',
            durationHours: 10.0,
            speedPercent: 75,
            direction: PivotDirection.forward,
            irrigationDepthMm: 30,
            isEnabled: true,
          ),
          const ScheduledRun(
            id: 'run_003',
            dayOfWeek: 3, // Wednesday
            startTime: '05:30',
            durationHours: 10.0,
            speedPercent: 75,
            direction: PivotDirection.forward,
            irrigationDepthMm: 30,
            isEnabled: true,
          ),
        ],
        isActive: true,
        createdAt: DateTime.now(),
      );

  // ═══════════════════════════════════════════════════════════════════════════
  // Control Commands - أوامر التحكم
  // ═══════════════════════════════════════════════════════════════════════════

  static PivotControlCommand get startCommand => PivotControlCommand(
        pivotId: 'pivot_001',
        commandType: PivotCommandType.start,
        speedPercent: 85,
        direction: PivotDirection.forward,
        timerHours: 8.0,
        issuedBy: 'user_001',
        timestamp: DateTime.now(),
      );

  static PivotControlCommand get stopCommand => PivotControlCommand(
        pivotId: 'pivot_001',
        commandType: PivotCommandType.stop,
        issuedBy: 'user_001',
        timestamp: DateTime.now(),
      );

  static PivotControlCommand get emergencyStopCommand => PivotControlCommand(
        pivotId: 'pivot_001',
        commandType: PivotCommandType.emergencyStop,
        issuedBy: 'user_001',
        timestamp: DateTime.now(),
      );

  static PivotControlCommand get setSpeedCommand => PivotControlCommand(
        pivotId: 'pivot_001',
        commandType: PivotCommandType.setSpeed,
        speedPercent: 70,
        issuedBy: 'user_001',
        timestamp: DateTime.now(),
      );

  // ═══════════════════════════════════════════════════════════════════════════
  // Run History - سجل التشغيل
  // ═══════════════════════════════════════════════════════════════════════════

  static PivotRunHistory get completedRun => PivotRunHistory(
        id: 'run_hist_001',
        pivotId: 'pivot_001',
        startTime: DateTime.now().subtract(const Duration(hours: 10)),
        endTime: DateTime.now().subtract(const Duration(hours: 2)),
        startAngle: 0,
        endAngle: 360,
        direction: PivotDirection.forward,
        avgSpeedPercent: 82.5,
        waterAppliedM3: 4000.0,
        energyConsumedKwh: 200.0,
        status: RunStatus.completed,
        alerts: [],
      );

  static PivotRunHistory get faultedRun => PivotRunHistory(
        id: 'run_hist_002',
        pivotId: 'pivot_001',
        startTime: DateTime.now().subtract(const Duration(hours: 5)),
        endTime: DateTime.now().subtract(const Duration(hours: 3)),
        startAngle: 0,
        endAngle: 180,
        direction: PivotDirection.forward,
        avgSpeedPercent: 75.0,
        waterAppliedM3: 1800.0,
        energyConsumedKwh: 90.0,
        status: RunStatus.faulted,
        stopReason: 'Low pressure fault at tower 3',
        alerts: [lowPressureAlert],
      );

  // ═══════════════════════════════════════════════════════════════════════════
  // Statistics - الإحصائيات
  // ═══════════════════════════════════════════════════════════════════════════

  static PivotStatistics get weeklyStats => PivotStatistics(
        pivotId: 'pivot_001',
        period: 'weekly',
        totalWaterM3: 28000.0,
        totalEnergyKwh: 1400.0,
        totalRunHours: 56.0,
        completeCircles: 7,
        avgIrrigationDepthMm: 25.0,
        avgSpeedPercent: 80.0,
        efficiencyPercent: 87.5,
        waterCost: 1400.0,
        energyCost: 700.0,
        faultCount: 1,
        downtimeHours: 2.0,
        periodStart: DateTime.now().subtract(const Duration(days: 7)),
        periodEnd: DateTime.now(),
      );

  static PivotStatistics get monthlyStats => PivotStatistics(
        pivotId: 'pivot_001',
        period: 'monthly',
        totalWaterM3: 112000.0,
        totalEnergyKwh: 5600.0,
        totalRunHours: 224.0,
        completeCircles: 28,
        avgIrrigationDepthMm: 24.5,
        avgSpeedPercent: 78.0,
        efficiencyPercent: 86.0,
        waterCost: 5600.0,
        energyCost: 2800.0,
        faultCount: 3,
        downtimeHours: 8.0,
        periodStart: DateTime.now().subtract(const Duration(days: 30)),
        periodEnd: DateTime.now(),
      );
}

/// Test fixtures for span zone models
class SpanZoneFixtures {
  static SpanConfiguration get sampleSpanConfig => SpanConfiguration(
        id: 'span_001',
        spanNumber: 1,
        distanceFromCenter: 60.0,
        spanLengthMeters: 55.0,
        nozzleCount: 12,
        nozzlePackage: NozzlePackage.standard,
        baseApplicationRateMmHr: 6.0,
        zones: [],
        isOperational: true,
        lastMaintenanceDate: DateTime.now().subtract(const Duration(days: 30)),
      );

  static List<SpanConfiguration> get allSpanConfigs => [
        sampleSpanConfig,
        const SpanConfiguration(
          id: 'span_002',
          spanNumber: 2,
          distanceFromCenter: 115.0,
          spanLengthMeters: 55.0,
          nozzleCount: 14,
          nozzlePackage: NozzlePackage.standard,
          baseApplicationRateMmHr: 6.5,
          isOperational: true,
        ),
        const SpanConfiguration(
          id: 'span_003',
          spanNumber: 3,
          distanceFromCenter: 170.0,
          spanLengthMeters: 55.0,
          nozzleCount: 16,
          nozzlePackage: NozzlePackage.lowPressure,
          baseApplicationRateMmHr: 7.0,
          isOperational: true,
        ),
        const SpanConfiguration(
          id: 'span_004',
          spanNumber: 4,
          distanceFromCenter: 225.0,
          spanLengthMeters: 55.0,
          nozzleCount: 18,
          nozzlePackage: NozzlePackage.lowPressure,
          baseApplicationRateMmHr: 7.5,
          isOperational: true,
        ),
      ];

  static VRIZoneGrid get uniformGrid =>
      VRIZoneGridBuilder.createUniformGrid(
        pivotId: 'pivot_001',
        spanCount: 4,
        angularDivisions: 8,
        defaultApplicationRate: 100,
      );

  static VRIZoneGrid get variableGrid {
    final ndviValues = <String, double>{
      '0_0': 0.72,
      '0_1': 0.68,
      '0_2': 0.45,
      '0_3': 0.55,
      '0_4': 0.80,
      '0_5': 0.75,
      '0_6': 0.62,
      '0_7': 0.70,
      '1_0': 0.65,
      '1_1': 0.58,
      '1_2': 0.42,
      '1_3': 0.48,
      '1_4': 0.78,
      '1_5': 0.72,
      '1_6': 0.60,
      '1_7': 0.68,
    };

    return VRIZoneGridBuilder.createFromNDVI(
      pivotId: 'pivot_001',
      spanCount: 2,
      angularDivisions: 8,
      ndviValues: ndviValues,
    );
  }

  static PrescriptionMap get irrigationPrescription => PrescriptionMap(
        id: 'prescription_001',
        pivotId: 'pivot_001',
        name: 'Summer Irrigation Map',
        nameAr: 'خريطة ري الصيف',
        prescriptionType: PrescriptionType.irrigation,
        source: PrescriptionSource.ndvi,
        zoneValues: {
          'zone_0_0': 100.0,
          'zone_0_1': 115.0,
          'zone_0_2': 130.0,
          'zone_1_0': 85.0,
          'zone_1_1': 100.0,
        },
        minValue: 0,
        maxValue: 150,
        unit: '%',
        validFrom: DateTime.now(),
        validUntil: DateTime.now().add(const Duration(days: 30)),
        isActive: true,
        createdAt: DateTime.now(),
        notes: 'Based on latest NDVI analysis',
        notesAr: 'بناءً على أحدث تحليل NDVI',
      );
}
