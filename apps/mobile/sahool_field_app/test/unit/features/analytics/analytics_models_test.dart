import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/analytics/data/models/analytics_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // FieldHealthScore Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldHealthScore', () {
    late DateTime testTime;

    setUp(() {
      testTime = DateTime(2026, 2, 27, 10, 0, 0);
    });

    FieldHealthScore createScore({
      double overallScore = 75.0,
      HealthTrend trend = HealthTrend.stable,
      List<HealthRecommendation> recommendations = const [],
    }) {
      return FieldHealthScore(
        fieldId: 'field-001',
        fieldName: 'Test Field',
        overallScore: overallScore,
        ndviScore: 80.0,
        soilHealthScore: 70.0,
        waterStressScore: 65.0,
        pestRiskScore: 85.0,
        nutrientScore: 72.0,
        trend: trend,
        calculatedAt: testTime,
        recommendations: recommendations,
      );
    }

    test('should create instance with all required fields', () {
      // Arrange & Act
      final score = createScore();

      // Assert
      expect(score.fieldId, 'field-001');
      expect(score.fieldName, 'Test Field');
      expect(score.overallScore, 75.0);
      expect(score.ndviScore, 80.0);
      expect(score.soilHealthScore, 70.0);
      expect(score.waterStressScore, 65.0);
      expect(score.pestRiskScore, 85.0);
      expect(score.nutrientScore, 72.0);
      expect(score.trend, HealthTrend.stable);
      expect(score.calculatedAt, testTime);
      expect(score.recommendations, isEmpty);
    });

    group('status calculation', () {
      test('should return excellent for score >= 80', () {
        final score = createScore(overallScore: 85.0);
        expect(score.status, HealthStatus.excellent);
      });

      test('should return excellent for score == 80', () {
        final score = createScore(overallScore: 80.0);
        expect(score.status, HealthStatus.excellent);
      });

      test('should return good for score >= 60 and < 80', () {
        final score = createScore(overallScore: 65.0);
        expect(score.status, HealthStatus.good);
      });

      test('should return moderate for score >= 40 and < 60', () {
        final score = createScore(overallScore: 45.0);
        expect(score.status, HealthStatus.moderate);
      });

      test('should return poor for score >= 20 and < 40', () {
        final score = createScore(overallScore: 25.0);
        expect(score.status, HealthStatus.poor);
      });

      test('should return critical for score < 20', () {
        final score = createScore(overallScore: 10.0);
        expect(score.status, HealthStatus.critical);
      });

      test('should return critical for score == 0', () {
        final score = createScore(overallScore: 0.0);
        expect(score.status, HealthStatus.critical);
      });
    });

    group('statusNameAr', () {
      test('should return Arabic name for excellent status', () {
        final score = createScore(overallScore: 90.0);
        expect(score.statusNameAr, 'ممتاز');
      });

      test('should return Arabic name for good status', () {
        final score = createScore(overallScore: 65.0);
        expect(score.statusNameAr, 'جيد');
      });

      test('should return Arabic name for moderate status', () {
        final score = createScore(overallScore: 50.0);
        expect(score.statusNameAr, 'متوسط');
      });

      test('should return Arabic name for poor status', () {
        final score = createScore(overallScore: 30.0);
        expect(score.statusNameAr, 'ضعيف');
      });

      test('should return Arabic name for critical status', () {
        final score = createScore(overallScore: 5.0);
        expect(score.statusNameAr, 'حرج');
      });
    });

    group('fromJson / toJson', () {
      test('should deserialize from JSON correctly', () {
        // Arrange
        final json = {
          'field_id': 'field-002',
          'field_name': 'Wheat Field',
          'overall_score': 72.5,
          'ndvi_score': 68.0,
          'soil_health_score': 55.0,
          'water_stress_score': 80.0,
          'pest_risk_score': 90.0,
          'nutrient_score': 60.0,
          'trend': 'improving',
          'calculated_at': '2026-02-27T10:00:00.000',
          'recommendations': [
            {
              'id': 'rec-001',
              'title': 'Apply Fertilizer',
              'title_ar': 'تطبيق السماد',
              'description': 'Apply nitrogen fertilizer',
              'description_ar': 'تطبيق سماد النيتروجين',
              'priority': 'high',
              'type': 'fertilizer',
            },
          ],
        };

        // Act
        final score = FieldHealthScore.fromJson(json);

        // Assert
        expect(score.fieldId, 'field-002');
        expect(score.fieldName, 'Wheat Field');
        expect(score.overallScore, 72.5);
        expect(score.ndviScore, 68.0);
        expect(score.soilHealthScore, 55.0);
        expect(score.waterStressScore, 80.0);
        expect(score.pestRiskScore, 90.0);
        expect(score.nutrientScore, 60.0);
        expect(score.trend, HealthTrend.improving);
        expect(score.recommendations.length, 1);
        expect(score.recommendations.first.id, 'rec-001');
      });

      test('should handle missing optional fields in JSON', () {
        // Arrange
        final json = {
          'field_id': 'field-003',
          'overall_score': 50.0,
          'calculated_at': '2026-02-27T10:00:00.000',
        };

        // Act
        final score = FieldHealthScore.fromJson(json);

        // Assert
        expect(score.fieldId, 'field-003');
        expect(score.fieldName, '');
        expect(score.ndviScore, 0.0);
        expect(score.soilHealthScore, 0.0);
        expect(score.waterStressScore, 0.0);
        expect(score.pestRiskScore, 0.0);
        expect(score.nutrientScore, 0.0);
        expect(score.trend, HealthTrend.stable);
        expect(score.recommendations, isEmpty);
      });

      test('should serialize to JSON and back correctly (roundtrip)', () {
        // Arrange
        final original = createScore(
          overallScore: 82.0,
          trend: HealthTrend.improving,
          recommendations: [
            const HealthRecommendation(
              id: 'rec-001',
              title: 'Irrigate',
              titleAr: 'ري',
              description: 'Water the field',
              descriptionAr: 'ري الحقل',
              priority: RecommendationPriority.high,
              type: RecommendationType.irrigation,
            ),
          ],
        );

        // Act
        final json = original.toJson();
        final restored = FieldHealthScore.fromJson(json);

        // Assert
        expect(restored.fieldId, original.fieldId);
        expect(restored.fieldName, original.fieldName);
        expect(restored.overallScore, original.overallScore);
        expect(restored.ndviScore, original.ndviScore);
        expect(restored.trend, original.trend);
        expect(restored.recommendations.length, 1);
        expect(restored.recommendations.first.id, 'rec-001');
      });

      test('should handle unknown trend value with fallback to stable', () {
        final json = {
          'field_id': 'field-004',
          'overall_score': 50.0,
          'trend': 'unknown_trend',
          'calculated_at': '2026-02-27T10:00:00.000',
        };

        final score = FieldHealthScore.fromJson(json);
        expect(score.trend, HealthTrend.stable);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HealthRecommendation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('HealthRecommendation', () {
    test('should create instance with all fields', () {
      const rec = HealthRecommendation(
        id: 'rec-001',
        title: 'Test Recommendation',
        titleAr: 'توصية تجريبية',
        description: 'Description',
        descriptionAr: 'الوصف',
        priority: RecommendationPriority.critical,
        type: RecommendationType.irrigation,
        actionUrl: '/action/001',
      );

      expect(rec.id, 'rec-001');
      expect(rec.title, 'Test Recommendation');
      expect(rec.titleAr, 'توصية تجريبية');
      expect(rec.priority, RecommendationPriority.critical);
      expect(rec.type, RecommendationType.irrigation);
      expect(rec.actionUrl, '/action/001');
    });

    test('should deserialize from JSON with fallback for missing Arabic fields',
        () {
      final json = {
        'id': 'rec-002',
        'title': 'Apply Fertilizer',
        'description': 'Apply nitrogen',
        'priority': 'high',
        'type': 'fertilizer',
      };

      final rec = HealthRecommendation.fromJson(json);

      expect(rec.title, 'Apply Fertilizer');
      expect(rec.titleAr, 'Apply Fertilizer'); // Falls back to title
      expect(rec.descriptionAr, 'Apply nitrogen'); // Falls back to description
      expect(rec.priority, RecommendationPriority.high);
      expect(rec.type, RecommendationType.fertilizer);
      expect(rec.actionUrl, isNull);
    });

    test('should use medium priority for unknown priority value', () {
      final json = {
        'id': 'rec-003',
        'title': 'Test',
        'description': 'Test',
        'priority': 'unknown_priority',
        'type': 'general',
      };

      final rec = HealthRecommendation.fromJson(json);
      expect(rec.priority, RecommendationPriority.medium);
    });

    test('should use general type for unknown type value', () {
      final json = {
        'id': 'rec-004',
        'title': 'Test',
        'description': 'Test',
        'priority': 'low',
        'type': 'unknown_type',
      };

      final rec = HealthRecommendation.fromJson(json);
      expect(rec.type, RecommendationType.general);
    });

    test('should roundtrip through JSON correctly', () {
      const original = HealthRecommendation(
        id: 'rec-005',
        title: 'Scout for Pests',
        titleAr: 'فحص الآفات',
        description: 'High pest risk',
        descriptionAr: 'خطر آفات عالي',
        priority: RecommendationPriority.medium,
        type: RecommendationType.pestControl,
        actionUrl: '/pests/scout',
      );

      final json = original.toJson();
      final restored = HealthRecommendation.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.title, original.title);
      expect(restored.titleAr, original.titleAr);
      expect(restored.priority, original.priority);
      expect(restored.type, original.type);
      expect(restored.actionUrl, original.actionUrl);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // YieldPrediction Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('YieldPrediction', () {
    late DateTime testHarvestDate;
    late DateTime testCalculatedAt;

    setUp(() {
      testHarvestDate = DateTime(2026, 6, 15);
      testCalculatedAt = DateTime(2026, 2, 27);
    });

    YieldPrediction createPrediction({
      double predictedYield = 3500.0,
      double confidence = 0.85,
    }) {
      return YieldPrediction(
        fieldId: 'field-001',
        cropType: 'wheat',
        cropTypeAr: 'قمح',
        predictedYield: predictedYield,
        minYield: predictedYield * 0.85,
        maxYield: predictedYield * 1.15,
        confidence: confidence,
        harvestDate: testHarvestDate,
        revenueEstimate: predictedYield * 800.0,
        factors: const [
          YieldFactor(
            name: 'NDVI Health',
            nameAr: 'صحة الغطاء النباتي',
            impact: 0.3,
            description: 'Vegetation health',
            descriptionAr: 'صحة الغطاء النباتي',
          ),
        ],
        calculatedAt: testCalculatedAt,
      );
    }

    test('should create instance with all required fields', () {
      final prediction = createPrediction();

      expect(prediction.fieldId, 'field-001');
      expect(prediction.cropType, 'wheat');
      expect(prediction.cropTypeAr, 'قمح');
      expect(prediction.predictedYield, 3500.0);
      expect(prediction.confidence, 0.85);
      expect(prediction.factors.length, 1);
    });

    group('quality assessment', () {
      test('should return excellent for yield >= 4000', () {
        final prediction = createPrediction(predictedYield: 4500.0);
        expect(prediction.quality, YieldQuality.excellent);
      });

      test('should return good for yield >= 3000 and < 4000', () {
        final prediction = createPrediction(predictedYield: 3500.0);
        expect(prediction.quality, YieldQuality.good);
      });

      test('should return average for yield >= 2000 and < 3000', () {
        final prediction = createPrediction(predictedYield: 2500.0);
        expect(prediction.quality, YieldQuality.average);
      });

      test('should return belowAverage for yield >= 1000 and < 2000', () {
        final prediction = createPrediction(predictedYield: 1500.0);
        expect(prediction.quality, YieldQuality.belowAverage);
      });

      test('should return poor for yield < 1000', () {
        final prediction = createPrediction(predictedYield: 500.0);
        expect(prediction.quality, YieldQuality.poor);
      });
    });

    group('fromJson / toJson', () {
      test('should deserialize from JSON correctly', () {
        final json = {
          'field_id': 'field-002',
          'crop_type': 'wheat',
          'crop_type_ar': 'قمح',
          'predicted_yield': 3200.0,
          'min_yield': 2800.0,
          'max_yield': 3600.0,
          'confidence': 0.82,
          'harvest_date': '2026-06-15T00:00:00.000',
          'revenue_estimate': 2560000.0,
          'factors': [
            {
              'name': 'Soil Moisture',
              'name_ar': 'رطوبة التربة',
              'impact': 0.2,
              'description': 'Water availability',
              'description_ar': 'توفر المياه',
            },
          ],
          'calculated_at': '2026-02-27T00:00:00.000',
        };

        final prediction = YieldPrediction.fromJson(json);

        expect(prediction.fieldId, 'field-002');
        expect(prediction.predictedYield, 3200.0);
        expect(prediction.confidence, 0.82);
        expect(prediction.factors.length, 1);
        expect(prediction.factors.first.name, 'Soil Moisture');
      });

      test('should handle missing optional fields in JSON', () {
        final json = {
          'field_id': 'field-003',
          'crop_type': 'sorghum',
          'predicted_yield': 1800.0,
          'min_yield': 1500.0,
          'max_yield': 2100.0,
          'confidence': 0.7,
          'harvest_date': '2026-06-15T00:00:00.000',
          'revenue_estimate': 1080000.0,
          'calculated_at': '2026-02-27T00:00:00.000',
        };

        final prediction = YieldPrediction.fromJson(json);

        expect(prediction.cropTypeAr, 'sorghum'); // Falls back to cropType
        expect(prediction.factors, isEmpty);
      });

      test('should roundtrip through JSON correctly', () {
        final original = createPrediction();
        final json = original.toJson();
        final restored = YieldPrediction.fromJson(json);

        expect(restored.fieldId, original.fieldId);
        expect(restored.cropType, original.cropType);
        expect(restored.predictedYield, original.predictedYield);
        expect(restored.confidence, original.confidence);
        expect(restored.factors.length, original.factors.length);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // YieldFactor Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('YieldFactor', () {
    test('should create instance with all fields', () {
      const factor = YieldFactor(
        name: 'NDVI Health',
        nameAr: 'صحة الغطاء النباتي',
        impact: 0.5,
        description: 'Positive vegetation impact',
        descriptionAr: 'تأثير إيجابي للغطاء النباتي',
      );

      expect(factor.name, 'NDVI Health');
      expect(factor.nameAr, 'صحة الغطاء النباتي');
      expect(factor.impact, 0.5);
    });

    test('should handle negative impact (reducing yield)', () {
      const factor = YieldFactor(
        name: 'Drought',
        nameAr: 'جفاف',
        impact: -0.4,
        description: 'Drought reduces yield',
        descriptionAr: 'الجفاف يقلل الإنتاجية',
      );

      expect(factor.impact, -0.4);
      expect(factor.impact, lessThan(0));
    });

    test('should roundtrip through JSON', () {
      const original = YieldFactor(
        name: 'Test Factor',
        nameAr: 'عامل تجريبي',
        impact: 0.15,
        description: 'Test description',
        descriptionAr: 'وصف تجريبي',
      );

      final json = original.toJson();
      final restored = YieldFactor.fromJson(json);

      expect(restored.name, original.name);
      expect(restored.nameAr, original.nameAr);
      expect(restored.impact, original.impact);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // RiskAssessment Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('RiskAssessment', () {
    late DateTime testTime;

    setUp(() {
      testTime = DateTime(2026, 2, 27, 10, 0, 0);
    });

    RiskAssessment createAssessment({
      double overallRiskScore = 55.0,
      List<Risk>? risks,
    }) {
      return RiskAssessment(
        fieldId: 'field-001',
        risks: risks ??
            [
              const Risk(
                id: 'risk-001',
                type: RiskType.drought,
                name: 'Drought Risk',
                nameAr: 'خطر الجفاف',
                description: 'Low rainfall',
                descriptionAr: 'قلة الأمطار',
                level: RiskLevel.high,
                probability: 0.7,
                potentialImpact: 70.0,
                mitigationSteps: ['Increase irrigation'],
                mitigationStepsAr: ['زيادة الري'],
              ),
            ],
        overallRiskScore: overallRiskScore,
        assessedAt: testTime,
      );
    }

    test('should create instance with risks', () {
      final assessment = createAssessment();

      expect(assessment.fieldId, 'field-001');
      expect(assessment.risks.length, 1);
      expect(assessment.overallRiskScore, 55.0);
      expect(assessment.assessedAt, testTime);
    });

    group('overallRiskLevel', () {
      test('should return critical for score >= 80', () {
        final assessment = createAssessment(overallRiskScore: 85.0);
        expect(assessment.overallRiskLevel, RiskLevel.critical);
      });

      test('should return high for score >= 60 and < 80', () {
        final assessment = createAssessment(overallRiskScore: 65.0);
        expect(assessment.overallRiskLevel, RiskLevel.high);
      });

      test('should return moderate for score >= 40 and < 60', () {
        final assessment = createAssessment(overallRiskScore: 45.0);
        expect(assessment.overallRiskLevel, RiskLevel.moderate);
      });

      test('should return low for score >= 20 and < 40', () {
        final assessment = createAssessment(overallRiskScore: 25.0);
        expect(assessment.overallRiskLevel, RiskLevel.low);
      });

      test('should return minimal for score < 20', () {
        final assessment = createAssessment(overallRiskScore: 10.0);
        expect(assessment.overallRiskLevel, RiskLevel.minimal);
      });
    });

    test('should deserialize from JSON with multiple risks', () {
      final json = {
        'field_id': 'field-002',
        'risks': [
          {
            'id': 'risk-001',
            'type': 'drought',
            'name': 'Drought Risk',
            'name_ar': 'خطر الجفاف',
            'description': 'Low rainfall',
            'description_ar': 'قلة الأمطار',
            'level': 'high',
            'probability': 0.7,
            'potential_impact': 70.0,
            'mitigation_steps': ['Irrigate more'],
            'mitigation_steps_ar': ['زيادة الري'],
          },
          {
            'id': 'risk-002',
            'type': 'pest',
            'name': 'Pest Outbreak',
            'name_ar': 'تفشي آفات',
            'description': 'High humidity',
            'description_ar': 'رطوبة عالية',
            'level': 'moderate',
            'probability': 0.5,
            'potential_impact': 50.0,
          },
        ],
        'overall_risk_score': 60.0,
        'assessed_at': '2026-02-27T10:00:00.000',
      };

      final assessment = RiskAssessment.fromJson(json);

      expect(assessment.fieldId, 'field-002');
      expect(assessment.risks.length, 2);
      expect(assessment.risks[0].type, RiskType.drought);
      expect(assessment.risks[1].type, RiskType.pest);
      expect(assessment.overallRiskScore, 60.0);
    });

    test('should roundtrip through JSON', () {
      final original = createAssessment();
      final json = original.toJson();
      final restored = RiskAssessment.fromJson(json);

      expect(restored.fieldId, original.fieldId);
      expect(restored.overallRiskScore, original.overallRiskScore);
      expect(restored.risks.length, original.risks.length);
      expect(restored.risks.first.type, original.risks.first.type);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Risk Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Risk', () {
    test('should handle unknown risk type with fallback to other', () {
      final json = {
        'id': 'risk-001',
        'type': 'unknown_risk_type',
        'name': 'Unknown Risk',
        'description': 'Something unknown',
        'level': 'moderate',
        'probability': 0.5,
        'potential_impact': 40.0,
      };

      final risk = Risk.fromJson(json);
      expect(risk.type, RiskType.other);
    });

    test('should handle unknown risk level with fallback to moderate', () {
      final json = {
        'id': 'risk-002',
        'type': 'drought',
        'name': 'Drought',
        'description': 'Low rainfall',
        'level': 'unknown_level',
        'probability': 0.6,
        'potential_impact': 55.0,
      };

      final risk = Risk.fromJson(json);
      expect(risk.level, RiskLevel.moderate);
    });

    test('should have empty mitigation steps when missing from JSON', () {
      final json = {
        'id': 'risk-003',
        'type': 'disease',
        'name': 'Disease',
        'description': 'Leaf rust detected',
        'level': 'high',
        'probability': 0.8,
        'potential_impact': 65.0,
      };

      final risk = Risk.fromJson(json);
      expect(risk.mitigationSteps, isEmpty);
      expect(risk.mitigationStepsAr, isEmpty);
    });

    test('should fallback to name for nameAr when missing', () {
      final json = {
        'id': 'risk-004',
        'type': 'frost',
        'name': 'Frost Damage',
        'description': 'Cold spell expected',
        'level': 'critical',
        'probability': 0.9,
        'potential_impact': 80.0,
      };

      final risk = Risk.fromJson(json);
      expect(risk.nameAr, 'Frost Damage');
      expect(risk.descriptionAr, 'Cold spell expected');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // AnalyticsSummary Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AnalyticsSummary', () {
    test('should create instance with all fields', () {
      final summary = AnalyticsSummary(
        totalFields: 10,
        averageHealthScore: 72.5,
        totalPredictedYield: 25000.0,
        totalRevenueEstimate: 15000000.0,
        highRiskFields: 2,
        fieldsNeedingAttention: 4,
        generatedAt: DateTime(2026, 2, 27),
      );

      expect(summary.totalFields, 10);
      expect(summary.averageHealthScore, 72.5);
      expect(summary.totalPredictedYield, 25000.0);
      expect(summary.totalRevenueEstimate, 15000000.0);
      expect(summary.highRiskFields, 2);
      expect(summary.fieldsNeedingAttention, 4);
      expect(summary.topPerformingFields, isEmpty);
      expect(summary.fieldsAtRisk, isEmpty);
    });

    test('should deserialize from JSON with nested field health scores', () {
      final json = {
        'total_fields': 5,
        'average_health_score': 68.0,
        'total_predicted_yield': 12500.0,
        'total_revenue_estimate': 7500000.0,
        'high_risk_fields': 1,
        'fields_needing_attention': 2,
        'top_performing_fields': [
          {
            'field_id': 'field-001',
            'field_name': 'Top Field',
            'overall_score': 90.0,
            'trend': 'improving',
            'calculated_at': '2026-02-27T10:00:00.000',
          },
        ],
        'fields_at_risk': [
          {
            'field_id': 'field-005',
            'field_name': 'At-risk Field',
            'overall_score': 30.0,
            'trend': 'declining',
            'calculated_at': '2026-02-27T10:00:00.000',
          },
        ],
        'generated_at': '2026-02-27T10:00:00.000',
      };

      final summary = AnalyticsSummary.fromJson(json);

      expect(summary.totalFields, 5);
      expect(summary.topPerformingFields.length, 1);
      expect(summary.topPerformingFields.first.overallScore, 90.0);
      expect(summary.fieldsAtRisk.length, 1);
      expect(summary.fieldsAtRisk.first.overallScore, 30.0);
    });

    test('should roundtrip through JSON', () {
      final original = AnalyticsSummary(
        totalFields: 3,
        averageHealthScore: 65.0,
        totalPredictedYield: 7500.0,
        totalRevenueEstimate: 4500000.0,
        highRiskFields: 1,
        fieldsNeedingAttention: 1,
        generatedAt: DateTime(2026, 2, 27),
      );

      final json = original.toJson();
      final restored = AnalyticsSummary.fromJson(json);

      expect(restored.totalFields, original.totalFields);
      expect(restored.averageHealthScore, original.averageHealthScore);
      expect(restored.totalPredictedYield, original.totalPredictedYield);
      expect(restored.highRiskFields, original.highRiskFields);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // HistoricalTrend and HistoricalDataPoint Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('HistoricalDataPoint', () {
    test('should create instance with required fields', () {
      final point = HistoricalDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
      );

      expect(point.date, DateTime(2026, 2, 27));
      expect(point.value, 0.72);
      expect(point.label, isNull);
    });

    test('should create instance with optional label', () {
      final point = HistoricalDataPoint(
        date: DateTime(2026, 2, 27),
        value: 0.72,
        label: 'Peak NDVI',
      );

      expect(point.label, 'Peak NDVI');
    });

    test('should roundtrip through JSON', () {
      final original = HistoricalDataPoint(
        date: DateTime(2026, 2, 27),
        value: 65.5,
        label: 'Test Label',
      );

      final json = original.toJson();
      final restored = HistoricalDataPoint.fromJson(json);

      expect(restored.value, original.value);
      expect(restored.label, original.label);
    });
  });

  group('HistoricalTrend', () {
    test('should create instance with data points', () {
      final trend = HistoricalTrend(
        metricName: 'ndvi',
        metricNameAr: 'مؤشر الغطاء النباتي',
        dataPoints: [
          HistoricalDataPoint(date: DateTime(2026, 2, 1), value: 0.60),
          HistoricalDataPoint(date: DateTime(2026, 2, 15), value: 0.68),
          HistoricalDataPoint(date: DateTime(2026, 2, 27), value: 0.72),
        ],
        changePercent: 20.0,
        trend: HealthTrend.improving,
      );

      expect(trend.metricName, 'ndvi');
      expect(trend.metricNameAr, 'مؤشر الغطاء النباتي');
      expect(trend.dataPoints.length, 3);
      expect(trend.changePercent, 20.0);
      expect(trend.trend, HealthTrend.improving);
    });

    test('should deserialize from JSON correctly', () {
      final json = {
        'metric_name': 'health_score',
        'metric_name_ar': 'درجة الصحة',
        'data_points': [
          {'date': '2026-02-01T00:00:00.000', 'value': 50.0},
          {'date': '2026-02-15T00:00:00.000', 'value': 55.0},
          {'date': '2026-02-27T00:00:00.000', 'value': 52.0},
        ],
        'change_percent': 4.0,
        'trend': 'stable',
      };

      final trend = HistoricalTrend.fromJson(json);

      expect(trend.metricName, 'health_score');
      expect(trend.metricNameAr, 'درجة الصحة');
      expect(trend.dataPoints.length, 3);
      expect(trend.changePercent, 4.0);
      expect(trend.trend, HealthTrend.stable);
    });

    test('should fallback metricNameAr to metricName when missing', () {
      final json = {
        'metric_name': 'custom_metric',
        'data_points': [
          {'date': '2026-02-01T00:00:00.000', 'value': 10.0},
        ],
        'change_percent': -5.0,
        'trend': 'declining',
      };

      final trend = HistoricalTrend.fromJson(json);
      expect(trend.metricNameAr, 'custom_metric');
    });

    test('should roundtrip through JSON', () {
      final original = HistoricalTrend(
        metricName: 'soil_moisture',
        metricNameAr: 'رطوبة التربة',
        dataPoints: [
          HistoricalDataPoint(date: DateTime(2026, 2, 1), value: 45.0),
          HistoricalDataPoint(date: DateTime(2026, 2, 27), value: 38.0),
        ],
        changePercent: -15.6,
        trend: HealthTrend.declining,
      );

      final json = original.toJson();
      final restored = HistoricalTrend.fromJson(json);

      expect(restored.metricName, original.metricName);
      expect(restored.dataPoints.length, original.dataPoints.length);
      expect(restored.changePercent, original.changePercent);
      expect(restored.trend, original.trend);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Enum Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('HealthStatus enum', () {
    test('should have all expected values', () {
      expect(HealthStatus.values.length, 5);
      expect(HealthStatus.values, contains(HealthStatus.excellent));
      expect(HealthStatus.values, contains(HealthStatus.good));
      expect(HealthStatus.values, contains(HealthStatus.moderate));
      expect(HealthStatus.values, contains(HealthStatus.poor));
      expect(HealthStatus.values, contains(HealthStatus.critical));
    });
  });

  group('HealthTrend enum', () {
    test('should have all expected values', () {
      expect(HealthTrend.values.length, 3);
      expect(HealthTrend.values, contains(HealthTrend.improving));
      expect(HealthTrend.values, contains(HealthTrend.stable));
      expect(HealthTrend.values, contains(HealthTrend.declining));
    });
  });

  group('RiskType enum', () {
    test('should have all expected values', () {
      expect(RiskType.values.length, 9);
      expect(RiskType.values, contains(RiskType.disease));
      expect(RiskType.values, contains(RiskType.pest));
      expect(RiskType.values, contains(RiskType.drought));
      expect(RiskType.values, contains(RiskType.flood));
      expect(RiskType.values, contains(RiskType.frost));
      expect(RiskType.values, contains(RiskType.heatWave));
      expect(RiskType.values, contains(RiskType.nutrientDeficiency));
      expect(RiskType.values, contains(RiskType.marketPrice));
      expect(RiskType.values, contains(RiskType.other));
    });
  });

  group('RiskLevel enum', () {
    test('should have all expected values', () {
      expect(RiskLevel.values.length, 5);
      expect(RiskLevel.values, contains(RiskLevel.minimal));
      expect(RiskLevel.values, contains(RiskLevel.low));
      expect(RiskLevel.values, contains(RiskLevel.moderate));
      expect(RiskLevel.values, contains(RiskLevel.high));
      expect(RiskLevel.values, contains(RiskLevel.critical));
    });
  });

  group('RecommendationPriority enum', () {
    test('should have all expected values', () {
      expect(RecommendationPriority.values.length, 4);
      expect(
          RecommendationPriority.values, contains(RecommendationPriority.critical));
      expect(RecommendationPriority.values, contains(RecommendationPriority.high));
      expect(
          RecommendationPriority.values, contains(RecommendationPriority.medium));
      expect(RecommendationPriority.values, contains(RecommendationPriority.low));
    });
  });

  group('RecommendationType enum', () {
    test('should have all expected values', () {
      expect(RecommendationType.values.length, 6);
      expect(
          RecommendationType.values, contains(RecommendationType.irrigation));
      expect(
          RecommendationType.values, contains(RecommendationType.fertilizer));
      expect(
          RecommendationType.values, contains(RecommendationType.pestControl));
      expect(RecommendationType.values, contains(RecommendationType.harvest));
      expect(RecommendationType.values, contains(RecommendationType.planting));
      expect(RecommendationType.values, contains(RecommendationType.general));
    });
  });

  group('YieldQuality enum', () {
    test('should have all expected values', () {
      expect(YieldQuality.values.length, 5);
      expect(YieldQuality.values, contains(YieldQuality.excellent));
      expect(YieldQuality.values, contains(YieldQuality.good));
      expect(YieldQuality.values, contains(YieldQuality.average));
      expect(YieldQuality.values, contains(YieldQuality.belowAverage));
      expect(YieldQuality.values, contains(YieldQuality.poor));
    });
  });
}
