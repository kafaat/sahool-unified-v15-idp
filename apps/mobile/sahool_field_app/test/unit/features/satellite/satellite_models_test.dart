import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/satellite/data/models/ndvi_data.dart';
import 'package:sahool_field_app/features/satellite/data/models/field_health.dart';
import 'package:sahool_field_app/features/satellite/data/models/phenology_data.dart';
import 'package:sahool_field_app/features/satellite/data/models/weather_data.dart';

void main() {
  // =========================================================================
  // NdviDataPoint
  // =========================================================================

  group('NdviDataPoint', () {
    test('should create instance with required parameters', () {
      // Arrange & Act
      final point = NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        source: 'sentinel-2',
        cloudCoverage: 10.0,
      );

      // Assert
      expect(point.value, 0.72);
      expect(point.source, 'sentinel-2');
      expect(point.cloudCoverage, 10.0);
    });

    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final point = NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        source: 'sentinel-2',
        cloudCoverage: 15.5,
      );

      // Act
      final json = point.toJson();
      final restored = NdviDataPoint.fromJson(json);

      // Assert
      expect(restored.date, point.date);
      expect(restored.value, point.value);
      expect(restored.source, point.source);
      expect(restored.cloudCoverage, point.cloudCoverage);
    });

    test('fromJson should handle alternative key names', () {
      // Arrange
      final json = {
        'timestamp': '2026-02-27T00:00:00.000',
        'ndvi': 0.65,
        'source': 'landsat-8',
        'cloudCoverage': 20.0,
      };

      // Act
      final point = NdviDataPoint.fromJson(json);

      // Assert
      expect(point.value, 0.65);
      expect(point.cloudCoverage, 20.0);
    });

    test('fromJson should use defaults for missing optional fields', () {
      // Arrange
      final json = {
        'date': '2026-02-27T00:00:00.000',
        'value': 0.55,
      };

      // Act
      final point = NdviDataPoint.fromJson(json);

      // Assert
      expect(point.source, 'sentinel-2'); // default
      expect(point.cloudCoverage, 0.0); // default
    });

    test('should support Equatable comparison', () {
      // Arrange
      final point1 = NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        source: 'sentinel-2',
      );
      final point2 = NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        source: 'sentinel-2',
      );
      final point3 = NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.65,
        source: 'sentinel-2',
      );

      // Assert
      expect(point1, equals(point2));
      expect(point1, isNot(equals(point3)));
    });

    test('should handle list of NdviDataPoints from JSON', () {
      // Arrange
      final jsonList = [
        {
          'date': '2026-02-01T00:00:00.000',
          'value': 0.60,
          'source': 'sentinel-2',
        },
        {
          'date': '2026-02-15T00:00:00.000',
          'value': 0.68,
          'source': 'sentinel-2',
        },
        {
          'date': '2026-02-27T00:00:00.000',
          'value': 0.72,
          'source': 'sentinel-2',
        },
      ];

      // Act
      final points = jsonList
          .map((j) => NdviDataPoint.fromJson(j))
          .toList();

      // Assert
      expect(points.length, 3);
      expect(points.first.value, 0.60);
      expect(points.last.value, 0.72);
    });

    test('copyWith should override specified fields only', () {
      // Arrange
      final original = NdviDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        source: 'sentinel-2',
        cloudCoverage: 10.0,
      );

      // Act
      final modified = original.copyWith(value: 0.80, cloudCoverage: 5.0);

      // Assert
      expect(modified.value, 0.80);
      expect(modified.cloudCoverage, 5.0);
      expect(modified.source, 'sentinel-2'); // unchanged
    });
  });

  // =========================================================================
  // NdviAnalysis
  // =========================================================================

  group('NdviAnalysis', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final analysis = NdviAnalysis(
        fieldId: 'field_001',
        currentNdvi: 0.72,
        previousNdvi: 0.68,
        changeRate: 5.9,
        health: VegetationHealth.good,
        timeSeries: [
          NdviDataPoint(
            date: DateTime(2026, 2, 20),
            value: 0.68,
            source: 'sentinel-2',
          ),
          NdviDataPoint(
            date: DateTime(2026, 2, 27),
            value: 0.72,
            source: 'sentinel-2',
          ),
        ],
        analyzedAt: DateTime(2026, 2, 27, 10, 0),
        imageUrl: 'https://example.com/ndvi.png',
        indices: const {'NDVI': 0.72, 'NDWI': 0.35},
      );

      // Act
      final json = analysis.toJson();
      final restored = NdviAnalysis.fromJson(json);

      // Assert
      expect(restored.fieldId, 'field_001');
      expect(restored.currentNdvi, 0.72);
      expect(restored.previousNdvi, 0.68);
      expect(restored.changeRate, 5.9);
      expect(restored.health, VegetationHealth.good);
      expect(restored.timeSeries.length, 2);
      expect(restored.imageUrl, 'https://example.com/ndvi.png');
      expect(restored.indices?['NDVI'], 0.72);
    });

    test('fromJson should handle alternative key names', () {
      // Arrange
      final json = {
        'fieldId': 'field_002',
        'currentNdvi': 0.55,
        'previousNdvi': 0.50,
        'changeRate': 10.0,
        'healthStatus': 'fair',
        'timeSeries': <dynamic>[],
        'analyzedAt': '2026-02-27T00:00:00.000',
      };

      // Act
      final analysis = NdviAnalysis.fromJson(json);

      // Assert
      expect(analysis.fieldId, 'field_002');
      expect(analysis.currentNdvi, 0.55);
      expect(analysis.health, VegetationHealth.fair);
    });

    test('should handle null indices and imageUrl', () {
      // Arrange
      final json = {
        'field_id': 'field_003',
        'current_ndvi': 0.40,
        'previous_ndvi': 0.38,
        'change_rate': 5.3,
        'health_status': 'fair',
        'time_series': <dynamic>[],
        'analyzed_at': '2026-02-27T00:00:00.000',
      };

      // Act
      final analysis = NdviAnalysis.fromJson(json);

      // Assert
      expect(analysis.imageUrl, isNull);
      expect(analysis.indices, isNull);
    });

    test('should support Equatable comparison', () {
      // Arrange
      final a1 = NdviAnalysis(
        fieldId: 'field_001',
        currentNdvi: 0.72,
        previousNdvi: 0.68,
        changeRate: 5.9,
        health: VegetationHealth.good,
        timeSeries: const [],
        analyzedAt: DateTime(2026, 2, 27),
      );
      final a2 = NdviAnalysis(
        fieldId: 'field_001',
        currentNdvi: 0.72,
        previousNdvi: 0.68,
        changeRate: 5.9,
        health: VegetationHealth.good,
        timeSeries: const [],
        analyzedAt: DateTime(2026, 2, 27),
      );

      // Assert
      expect(a1, equals(a2));
    });
  });

  // =========================================================================
  // VegetationHealth enum
  // =========================================================================

  group('VegetationHealth', () {
    test('fromString should map known status strings', () {
      expect(VegetationHealth.fromString('excellent'),
          VegetationHealth.excellent);
      expect(VegetationHealth.fromString('good'), VegetationHealth.good);
      expect(VegetationHealth.fromString('fair'), VegetationHealth.fair);
      expect(VegetationHealth.fromString('poor'), VegetationHealth.poor);
      expect(
          VegetationHealth.fromString('critical'), VegetationHealth.critical);
    });

    test('fromString should return unknown for unrecognized values', () {
      expect(
          VegetationHealth.fromString('invalid'), VegetationHealth.unknown);
    });

    test('fromNdvi should classify based on thresholds', () {
      expect(VegetationHealth.fromNdvi(0.90), VegetationHealth.excellent);
      expect(VegetationHealth.fromNdvi(0.80), VegetationHealth.excellent);
      expect(VegetationHealth.fromNdvi(0.70), VegetationHealth.good);
      expect(VegetationHealth.fromNdvi(0.60), VegetationHealth.good);
      expect(VegetationHealth.fromNdvi(0.50), VegetationHealth.fair);
      expect(VegetationHealth.fromNdvi(0.30), VegetationHealth.poor);
      expect(VegetationHealth.fromNdvi(0.10), VegetationHealth.critical);
    });

    test('getLabel should return bilingual labels', () {
      expect(VegetationHealth.excellent.getLabel(false), 'excellent');
      expect(
          VegetationHealth.excellent.getLabel(true), '\u0645\u0645\u062a\u0627\u0632');
      expect(VegetationHealth.good.getLabel(false), 'good');
      expect(VegetationHealth.good.getLabel(true), '\u062c\u064a\u062f');
    });
  });

  // =========================================================================
  // VegetationIndex
  // =========================================================================

  group('VegetationIndex', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      const index = VegetationIndex(
        name: 'NDVI',
        nameAr:
            '\u0645\u0624\u0634\u0631 \u0627\u0644\u063a\u0637\u0627\u0621 \u0627\u0644\u0646\u0628\u0627\u062a\u064a',
        code: 'NDVI',
        value: 0.72,
        unit: '',
        description: 'Normalized Difference Vegetation Index',
        descriptionAr:
            '\u0645\u0624\u0634\u0631 \u0627\u0644\u0641\u0631\u0642 \u0627\u0644\u0645\u0639\u064a\u0627\u0631\u064a \u0644\u0644\u0646\u0628\u0627\u062a',
      );

      // Act
      final json = index.toJson();
      final restored = VegetationIndex.fromJson(json);

      // Assert
      expect(restored.code, 'NDVI');
      expect(restored.value, 0.72);
      expect(restored.name, 'NDVI');
    });
  });

  // =========================================================================
  // FieldHealth
  // =========================================================================

  group('FieldHealth', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final health = FieldHealth(
        fieldId: 'field_001',
        healthScore: 78.0,
        status: HealthStatus.good,
        ndvi: 0.72,
        ndwi: 0.35,
        evi: 0.55,
        soilMoisture: 42.0,
        alerts: [
          HealthAlert(
            id: 'ha_001',
            type: AlertType.waterStress,
            severity: AlertSeverity.warning,
            message: 'Low moisture',
            messageAr:
                '\u0631\u0637\u0648\u0628\u0629 \u0645\u0646\u062e\u0641\u0636\u0629',
            detectedAt: DateTime(2026, 2, 26),
            affectedZone: 'zone_B',
          ),
        ],
        recommendations: const [
          Recommendation(
            id: 'rec_001',
            type: RecommendationType.irrigation,
            title: 'Irrigate zone B',
            titleAr:
                '\u0631\u064a \u0627\u0644\u0645\u0646\u0637\u0642\u0629 \u0628',
            description: 'Apply 25mm',
            descriptionAr:
                '\u062a\u0637\u0628\u064a\u0642 25 \u0645\u0645',
            priority: RecommendationPriority.high,
          ),
        ],
        assessedAt: DateTime(2026, 2, 27, 8, 0),
        zoneScores: const {'zone_A': 85.0, 'zone_B': 62.0},
      );

      // Act
      final json = health.toJson();
      final restored = FieldHealth.fromJson(json);

      // Assert
      expect(restored.fieldId, 'field_001');
      expect(restored.healthScore, 78.0);
      expect(restored.status, HealthStatus.good);
      expect(restored.ndvi, 0.72);
      expect(restored.ndwi, 0.35);
      expect(restored.evi, 0.55);
      expect(restored.soilMoisture, 42.0);
      expect(restored.alerts.length, 1);
      expect(restored.recommendations.length, 1);
      expect(restored.zoneScores?['zone_A'], 85.0);
      expect(restored.zoneScores?['zone_B'], 62.0);
    });

    test('fromJson should handle null optional fields', () {
      // Arrange
      final json = {
        'field_id': 'field_002',
        'health_score': 65,
        'status': 'warning',
        'ndvi': 0.45,
        'ndwi': 0.20,
        'evi': 0.30,
        'alerts': <dynamic>[],
        'recommendations': <dynamic>[],
        'assessed_at': '2026-02-27T00:00:00.000',
      };

      // Act
      final health = FieldHealth.fromJson(json);

      // Assert
      expect(health.soilMoisture, isNull);
      expect(health.zoneScores, isNull);
    });

    test('should support Equatable comparison', () {
      // Arrange
      final h1 = FieldHealth(
        fieldId: 'field_001',
        healthScore: 78.0,
        status: HealthStatus.good,
        ndvi: 0.72,
        ndwi: 0.35,
        evi: 0.55,
        assessedAt: DateTime(2026, 2, 27),
      );
      final h2 = FieldHealth(
        fieldId: 'field_001',
        healthScore: 78.0,
        status: HealthStatus.good,
        ndvi: 0.72,
        ndwi: 0.35,
        evi: 0.55,
        assessedAt: DateTime(2026, 2, 27),
      );

      // Assert
      expect(h1, equals(h2));
    });
  });

  // =========================================================================
  // HealthStatus enum
  // =========================================================================

  group('HealthStatus', () {
    test('fromString should map known values', () {
      expect(HealthStatus.fromString('excellent'), HealthStatus.excellent);
      expect(HealthStatus.fromString('good'), HealthStatus.good);
      expect(HealthStatus.fromString('warning'), HealthStatus.warning);
      expect(HealthStatus.fromString('critical'), HealthStatus.critical);
    });

    test('fromString should return unknown for unrecognized value', () {
      expect(HealthStatus.fromString('invalid'), HealthStatus.unknown);
    });

    test('fromScore should classify based on score thresholds', () {
      expect(HealthStatus.fromScore(90.0), HealthStatus.excellent);
      expect(HealthStatus.fromScore(80.0), HealthStatus.excellent);
      expect(HealthStatus.fromScore(70.0), HealthStatus.good);
      expect(HealthStatus.fromScore(50.0), HealthStatus.warning);
      expect(HealthStatus.fromScore(30.0), HealthStatus.critical);
    });

    test('getLabel should return bilingual labels', () {
      expect(HealthStatus.excellent.getLabel(false), 'excellent');
      expect(HealthStatus.excellent.getLabel(true), '\u0645\u0645\u062a\u0627\u0632');
      expect(HealthStatus.critical.getLabel(false), 'critical');
      expect(HealthStatus.critical.getLabel(true), '\u062d\u0631\u062c');
    });
  });

  // =========================================================================
  // HealthAlert
  // =========================================================================

  group('HealthAlert', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final alert = HealthAlert(
        id: 'ha_001',
        type: AlertType.waterStress,
        severity: AlertSeverity.warning,
        message: 'Low soil moisture',
        messageAr:
            '\u0631\u0637\u0648\u0628\u0629 \u062a\u0631\u0628\u0629 \u0645\u0646\u062e\u0641\u0636\u0629',
        detectedAt: DateTime(2026, 2, 26, 14, 0),
        affectedZone: 'zone_B',
      );

      // Act
      final json = alert.toJson();
      final restored = HealthAlert.fromJson(json);

      // Assert
      expect(restored.id, 'ha_001');
      expect(restored.type, AlertType.waterStress);
      expect(restored.severity, AlertSeverity.warning);
      expect(restored.message, 'Low soil moisture');
      expect(restored.affectedZone, 'zone_B');
    });

    test('fromJson should handle null affectedZone', () {
      // Arrange
      final json = {
        'id': 'ha_002',
        'type': 'disease_risk',
        'severity': 'critical',
        'message': 'Rust risk detected',
        'message_ar': '\u062e\u0637\u0631 \u0635\u062f\u0623',
        'detected_at': '2026-02-27T00:00:00.000',
      };

      // Act
      final alert = HealthAlert.fromJson(json);

      // Assert
      expect(alert.type, AlertType.diseaseRisk);
      expect(alert.severity, AlertSeverity.critical);
      expect(alert.affectedZone, isNull);
    });
  });

  // =========================================================================
  // AlertType enum
  // =========================================================================

  group('AlertType', () {
    test('fromString should map known values', () {
      expect(AlertType.fromString('water_stress'), AlertType.waterStress);
      expect(AlertType.fromString('nutrient_deficiency'),
          AlertType.nutrientDeficiency);
      expect(AlertType.fromString('disease_risk'), AlertType.diseaseRisk);
      expect(AlertType.fromString('pest_risk'), AlertType.pestRisk);
      expect(AlertType.fromString('growth_anomaly'), AlertType.growthAnomaly);
    });

    test('fromString should return other for unknown value', () {
      expect(AlertType.fromString('xyz'), AlertType.other);
    });

    test('getLabel should return bilingual labels', () {
      expect(AlertType.waterStress.getLabel(false), 'water_stress');
      expect(AlertType.waterStress.getLabel(true),
          '\u0625\u062c\u0647\u0627\u062f \u0645\u0627\u0626\u064a');
    });
  });

  // =========================================================================
  // AlertSeverity enum (satellite model)
  // =========================================================================

  group('AlertSeverity (satellite)', () {
    test('fromString should map known values', () {
      expect(AlertSeverity.fromString('info'), AlertSeverity.info);
      expect(AlertSeverity.fromString('warning'), AlertSeverity.warning);
      expect(AlertSeverity.fromString('critical'), AlertSeverity.critical);
    });

    test('fromString should return info for unknown value', () {
      expect(AlertSeverity.fromString('unknown'), AlertSeverity.info);
    });

    test('getLabel should return bilingual labels', () {
      expect(AlertSeverity.critical.getLabel(false), 'critical');
      expect(AlertSeverity.critical.getLabel(true), '\u062d\u0631\u062c');
    });
  });

  // =========================================================================
  // Recommendation
  // =========================================================================

  group('Recommendation', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final rec = Recommendation(
        id: 'rec_001',
        type: RecommendationType.irrigation,
        title: 'Increase irrigation',
        titleAr: '\u0632\u064a\u0627\u062f\u0629 \u0627\u0644\u0631\u064a',
        description: 'Apply 25mm in the next 48 hours',
        descriptionAr:
            '\u062a\u0637\u0628\u064a\u0642 25 \u0645\u0645 \u062e\u0644\u0627\u0644 48 \u0633\u0627\u0639\u0629',
        priority: RecommendationPriority.high,
        dueDate: DateTime(2026, 3, 1),
      );

      // Act
      final json = rec.toJson();
      final restored = Recommendation.fromJson(json);

      // Assert
      expect(restored.id, 'rec_001');
      expect(restored.type, RecommendationType.irrigation);
      expect(restored.priority, RecommendationPriority.high);
      expect(restored.dueDate, DateTime(2026, 3, 1));
    });

    test('fromJson should handle null dueDate', () {
      // Arrange
      final json = {
        'id': 'rec_002',
        'type': 'monitoring',
        'title': 'Monitor field',
        'description': 'Check NDVI trends',
        'priority': 'low',
      };

      // Act
      final rec = Recommendation.fromJson(json);

      // Assert
      expect(rec.type, RecommendationType.monitoring);
      expect(rec.priority, RecommendationPriority.low);
      expect(rec.dueDate, isNull);
    });
  });

  // =========================================================================
  // RecommendationType enum
  // =========================================================================

  group('RecommendationType', () {
    test('fromString should map known values', () {
      expect(RecommendationType.fromString('irrigation'),
          RecommendationType.irrigation);
      expect(RecommendationType.fromString('fertilization'),
          RecommendationType.fertilization);
      expect(RecommendationType.fromString('pest_control'),
          RecommendationType.pestControl);
      expect(RecommendationType.fromString('disease_control'),
          RecommendationType.diseaseControl);
      expect(RecommendationType.fromString('monitoring'),
          RecommendationType.monitoring);
    });

    test('fromString should return general for unknown value', () {
      expect(
          RecommendationType.fromString('xyz'), RecommendationType.general);
    });
  });

  // =========================================================================
  // RecommendationPriority enum
  // =========================================================================

  group('RecommendationPriority', () {
    test('fromString should map known values', () {
      expect(RecommendationPriority.fromString('high'),
          RecommendationPriority.high);
      expect(RecommendationPriority.fromString('medium'),
          RecommendationPriority.medium);
      expect(
          RecommendationPriority.fromString('low'), RecommendationPriority.low);
    });

    test('fromString should return medium for unknown value', () {
      expect(RecommendationPriority.fromString('xyz'),
          RecommendationPriority.medium);
    });

    test('getLabel should return bilingual labels', () {
      expect(RecommendationPriority.high.getLabel(false), 'high');
      expect(
          RecommendationPriority.high.getLabel(true), '\u0639\u0627\u0644\u064a\u0629');
    });
  });

  // =========================================================================
  // PhenologyData
  // =========================================================================

  group('PhenologyData', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final phenology = PhenologyData(
        fieldId: 'field_001',
        cropType: 'wheat',
        cropTypeAr: '\u0642\u0645\u062d',
        currentStage: GrowthStage.flowering,
        daysInCurrentStage: 8,
        daysToNextStage: 12,
        daysToHarvest: 45,
        plantingDate: DateTime(2025, 11, 15),
        expectedHarvestDate: DateTime(2026, 4, 12),
        stages: [
          GrowthStageInfo(
            stage: GrowthStage.germination,
            name: 'Germination',
            nameAr: '\u0625\u0646\u0628\u0627\u062a',
            durationDays: 14,
            startDate: DateTime(2025, 11, 15),
            endDate: DateTime(2025, 11, 29),
            isCompleted: true,
            isCurrent: false,
            tasks: const ['Ensure adequate moisture'],
            tasksAr: const ['\u0636\u0645\u0627\u0646 \u0631\u0637\u0648\u0628\u0629 \u0643\u0627\u0641\u064a\u0629'],
          ),
        ],
        currentTasks: const ['Monitor pollination'],
        currentTasksAr: const [
          '\u0645\u0631\u0627\u0642\u0628\u0629 \u0627\u0644\u062a\u0644\u0642\u064a\u062d',
        ],
        completionPercentage: 65.0,
        analyzedAt: DateTime(2026, 2, 27, 9, 0),
      );

      // Act
      final json = phenology.toJson();
      final restored = PhenologyData.fromJson(json);

      // Assert
      expect(restored.fieldId, 'field_001');
      expect(restored.cropType, 'wheat');
      expect(restored.currentStage, GrowthStage.flowering);
      expect(restored.daysInCurrentStage, 8);
      expect(restored.daysToNextStage, 12);
      expect(restored.daysToHarvest, 45);
      expect(restored.completionPercentage, 65.0);
      expect(restored.stages.length, 1);
      expect(restored.currentTasks.length, 1);
      expect(restored.currentTasksAr.length, 1);
    });

    test('fromJson should handle null optional fields', () {
      // Arrange
      final json = {
        'field_id': 'field_002',
        'crop_type': 'barley',
        'crop_type_ar': '\u0634\u0639\u064a\u0631',
        'current_stage': 'vegetative',
        'days_in_current_stage': 15,
        'planting_date': '2025-12-01T00:00:00.000',
        'completion_percentage': 30.0,
        'analyzed_at': '2026-02-27T00:00:00.000',
      };

      // Act
      final phenology = PhenologyData.fromJson(json);

      // Assert
      expect(phenology.daysToNextStage, isNull);
      expect(phenology.daysToHarvest, isNull);
      expect(phenology.expectedHarvestDate, isNull);
      expect(phenology.stages, isEmpty);
      expect(phenology.currentTasks, isEmpty);
    });

    test('should support Equatable comparison', () {
      // Arrange
      final p1 = PhenologyData(
        fieldId: 'field_001',
        cropType: 'wheat',
        cropTypeAr: '\u0642\u0645\u062d',
        currentStage: GrowthStage.flowering,
        daysInCurrentStage: 8,
        plantingDate: DateTime(2025, 11, 15),
        completionPercentage: 65.0,
        analyzedAt: DateTime(2026, 2, 27),
      );
      final p2 = PhenologyData(
        fieldId: 'field_001',
        cropType: 'wheat',
        cropTypeAr: '\u0642\u0645\u062d',
        currentStage: GrowthStage.flowering,
        daysInCurrentStage: 8,
        plantingDate: DateTime(2025, 11, 15),
        completionPercentage: 65.0,
        analyzedAt: DateTime(2026, 2, 27),
      );

      // Assert
      expect(p1, equals(p2));
    });
  });

  // =========================================================================
  // GrowthStage enum
  // =========================================================================

  group('GrowthStage', () {
    test('fromString should map known values', () {
      expect(GrowthStage.fromString('germination'), GrowthStage.germination);
      expect(GrowthStage.fromString('vegetative'), GrowthStage.vegetative);
      expect(GrowthStage.fromString('flowering'), GrowthStage.flowering);
      expect(GrowthStage.fromString('fruit_development'),
          GrowthStage.fruitDevelopment);
      expect(GrowthStage.fromString('ripening'), GrowthStage.ripening);
      expect(GrowthStage.fromString('harvest'), GrowthStage.harvest);
    });

    test('fromString should return unknown for unrecognized value', () {
      expect(GrowthStage.fromString('xyz'), GrowthStage.unknown);
    });

    test('getLabel should return bilingual labels', () {
      expect(GrowthStage.germination.getLabel(false), 'germination');
      expect(
          GrowthStage.germination.getLabel(true), '\u0625\u0646\u0628\u0627\u062a');
      expect(GrowthStage.flowering.getLabel(false), 'flowering');
      expect(
          GrowthStage.flowering.getLabel(true), '\u0625\u0632\u0647\u0627\u0631');
    });

    test('should have associated color hex codes', () {
      expect(GrowthStage.germination.colorHex, '#8BC34A');
      expect(GrowthStage.flowering.colorHex, '#FFC107');
      expect(GrowthStage.harvest.colorHex, '#795548');
      expect(GrowthStage.unknown.colorHex, '#9E9E9E');
    });
  });

  // =========================================================================
  // GrowthStageInfo
  // =========================================================================

  group('GrowthStageInfo', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final info = GrowthStageInfo(
        stage: GrowthStage.vegetative,
        name: 'Vegetative Growth',
        nameAr: '\u0646\u0645\u0648 \u062e\u0636\u0631\u064a',
        durationDays: 30,
        startDate: DateTime(2025, 12, 1),
        endDate: DateTime(2025, 12, 31),
        isCompleted: true,
        isCurrent: false,
        description: 'Main growth phase',
        descriptionAr:
            '\u0645\u0631\u062d\u0644\u0629 \u0627\u0644\u0646\u0645\u0648 \u0627\u0644\u0631\u0626\u064a\u0633\u064a\u0629',
        tasks: const ['Apply nitrogen', 'Monitor pest'],
        tasksAr: const [
          '\u062a\u0637\u0628\u064a\u0642 \u0627\u0644\u0646\u064a\u062a\u0631\u0648\u062c\u064a\u0646',
          '\u0645\u0631\u0627\u0642\u0628\u0629 \u0627\u0644\u0622\u0641\u0627\u062a',
        ],
      );

      // Act
      final json = info.toJson();
      final restored = GrowthStageInfo.fromJson(json);

      // Assert
      expect(restored.stage, GrowthStage.vegetative);
      expect(restored.durationDays, 30);
      expect(restored.isCompleted, true);
      expect(restored.isCurrent, false);
      expect(restored.tasks.length, 2);
      expect(restored.tasksAr.length, 2);
    });

    test('fromJson should handle null dates', () {
      // Arrange
      final json = {
        'stage': 'ripening',
        'name': 'Ripening',
        'name_ar': '\u0646\u0636\u062c',
        'duration_days': 20,
        'is_completed': false,
        'is_current': false,
      };

      // Act
      final info = GrowthStageInfo.fromJson(json);

      // Assert
      expect(info.startDate, isNull);
      expect(info.endDate, isNull);
      expect(info.tasks, isEmpty);
    });
  });

  // =========================================================================
  // WeatherSummary (satellite model)
  // =========================================================================

  group('WeatherSummary', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final weather = WeatherSummary(
        fieldId: 'field_001',
        temperature: 28.0,
        minTemp: 18.0,
        maxTemp: 33.0,
        precipitation: 2.5,
        humidity: 55.0,
        et0: 5.2,
        condition: 'Partly Cloudy',
        conditionAr: '\u063a\u0627\u0626\u0645 \u062c\u0632\u0626\u064a\u0627',
        updatedAt: DateTime(2026, 2, 27, 10, 0),
        forecast: [
          DailyForecastSummary(
            date: DateTime(2026, 2, 28),
            tempMin: 17.0,
            tempMax: 31.0,
            precipitation: 0.0,
            condition: 'Sunny',
            conditionAr: '\u0645\u0634\u0645\u0633',
          ),
        ],
      );

      // Act
      final json = weather.toJson();
      final restored = WeatherSummary.fromJson(json);

      // Assert
      expect(restored.fieldId, 'field_001');
      expect(restored.temperature, 28.0);
      expect(restored.et0, 5.2);
      expect(restored.forecast.length, 1);
    });

    test('getIrrigationNeed should calculate correctly', () {
      // Arrange
      final weather = WeatherSummary(
        fieldId: 'field_001',
        temperature: 28.0,
        minTemp: 18.0,
        maxTemp: 33.0,
        precipitation: 7.0, // 7mm weekly = 1mm/day
        humidity: 55.0,
        et0: 5.2, // 5.2mm/day
        condition: 'Sunny',
        conditionAr: '\u0645\u0634\u0645\u0633',
        updatedAt: DateTime(2026, 2, 27),
      );

      // Act
      final need = weather.getIrrigationNeed();

      // Assert - ET0 - (precipitation / 7) = 5.2 - 1.0 = 4.2
      expect(need, closeTo(4.2, 0.01));
    });

    test('getIrrigationNeed should clamp to 0 when rain exceeds ET0',
        () {
      // Arrange
      final weather = WeatherSummary(
        fieldId: 'field_001',
        temperature: 20.0,
        minTemp: 15.0,
        maxTemp: 22.0,
        precipitation: 50.0, // heavy rain
        humidity: 80.0,
        et0: 3.0,
        condition: 'Rainy',
        conditionAr: '\u0645\u0645\u0637\u0631',
        updatedAt: DateTime(2026, 2, 27),
      );

      // Act
      final need = weather.getIrrigationNeed();

      // Assert - clamped to 0
      expect(need, 0.0);
    });
  });

  // =========================================================================
  // DailyForecastSummary (satellite model)
  // =========================================================================

  group('DailyForecastSummary', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final forecast = DailyForecastSummary(
        date: DateTime(2026, 2, 28),
        tempMin: 17.0,
        tempMax: 31.0,
        precipitation: 0.0,
        condition: 'Sunny',
        conditionAr: '\u0645\u0634\u0645\u0633',
        icon: '\u2600\ufe0f',
      );

      // Act
      final json = forecast.toJson();
      final restored = DailyForecastSummary.fromJson(json);

      // Assert
      expect(restored.tempMin, 17.0);
      expect(restored.tempMax, 31.0);
      expect(restored.precipitation, 0.0);
      expect(restored.icon, '\u2600\ufe0f');
    });

    test('fromJson should handle alternative keys', () {
      // Arrange
      final json = {
        'date': '2026-02-28T00:00:00.000',
        'tempMin': 15.0,
        'tempMax': 30.0,
        'rain': 3.5,
        'weather': 'Rainy',
        'conditionAr': '\u0645\u0645\u0637\u0631',
      };

      // Act
      final forecast = DailyForecastSummary.fromJson(json);

      // Assert
      expect(forecast.precipitation, 3.5);
      expect(forecast.condition, 'Rainy');
    });
  });

  // =========================================================================
  // WeatherAlertSummary (satellite model)
  // =========================================================================

  group('WeatherAlertSummary', () {
    test('should serialize to JSON and back (round-trip)', () {
      // Arrange
      final alert = WeatherAlertSummary(
        id: 'wa_001',
        type: WeatherAlertType.frost,
        severity: 'critical',
        message: 'Frost warning overnight',
        messageAr:
            '\u062a\u062d\u0630\u064a\u0631 \u0635\u0642\u064a\u0639 \u0644\u064a\u0644\u064a',
        startsAt: DateTime(2026, 2, 27, 22, 0),
        endsAt: DateTime(2026, 2, 28, 6, 0),
      );

      // Act
      final json = alert.toJson();
      final restored = WeatherAlertSummary.fromJson(json);

      // Assert
      expect(restored.id, 'wa_001');
      expect(restored.type, WeatherAlertType.frost);
      expect(restored.severity, 'critical');
      expect(restored.endsAt, DateTime(2026, 2, 28, 6, 0));
    });

    test('fromJson should handle null endsAt', () {
      // Arrange
      final json = {
        'id': 'wa_002',
        'type': 'heat',
        'severity': 'warning',
        'message': 'Heat wave',
        'message_ar': '\u0645\u0648\u062c\u0629 \u062d\u0631',
        'starts_at': '2026-02-27T06:00:00.000',
      };

      // Act
      final alert = WeatherAlertSummary.fromJson(json);

      // Assert
      expect(alert.type, WeatherAlertType.heat);
      expect(alert.endsAt, isNull);
    });
  });

  // =========================================================================
  // WeatherAlertType enum
  // =========================================================================

  group('WeatherAlertType', () {
    test('fromString should map known values', () {
      expect(
          WeatherAlertType.fromString('frost'), WeatherAlertType.frost);
      expect(WeatherAlertType.fromString('heat'), WeatherAlertType.heat);
      expect(
          WeatherAlertType.fromString('drought'), WeatherAlertType.drought);
      expect(WeatherAlertType.fromString('heavy_rain'),
          WeatherAlertType.heavyRain);
      expect(WeatherAlertType.fromString('wind'), WeatherAlertType.wind);
    });

    test('fromString should return general for unknown value', () {
      expect(
          WeatherAlertType.fromString('xyz'), WeatherAlertType.general);
    });

    test('getLabel should return bilingual labels', () {
      expect(WeatherAlertType.frost.getLabel(false), 'frost');
      expect(WeatherAlertType.frost.getLabel(true), '\u0635\u0642\u064a\u0639');
    });
  });
}
