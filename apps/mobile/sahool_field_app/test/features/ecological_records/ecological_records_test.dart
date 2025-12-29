/// Unit Tests for Ecological Records
/// اختبارات وحدات السجلات الإيكولوجية
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/ecological_records/domain/entities/ecological_entities.dart';

void main() {
  group('BiodiversityRecord', () {
    test('calculatedScore returns habitatQualityScore when available', () {
      final record = BiodiversityRecord(
        id: 'test-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: DateTime.now(),
        surveyType: BiodiversitySurveyType.habitatAssessment,
        habitatQualityScore: 85.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedScore, 85.0);
    });

    test('calculatedScore calculates from speciesCount when no habitatQualityScore', () {
      final record = BiodiversityRecord(
        id: 'test-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: DateTime.now(),
        surveyType: BiodiversitySurveyType.speciesCount,
        speciesCount: 15,
        habitatQualityScore: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      // 15 * 5 = 75
      expect(record.calculatedScore, 75.0);
    });

    test('calculatedScore caps at 100 for high species count', () {
      final record = BiodiversityRecord(
        id: 'test-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: DateTime.now(),
        surveyType: BiodiversitySurveyType.speciesCount,
        speciesCount: 50, // 50 * 5 = 250, should be clamped to 100
        habitatQualityScore: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedScore, 100.0);
    });

    test('calculatedScore returns 0 when no data available', () {
      final record = BiodiversityRecord(
        id: 'test-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: DateTime.now(),
        surveyType: BiodiversitySurveyType.general,
        speciesCount: null,
        habitatQualityScore: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedScore, 0.0);
    });

    test('toJson produces valid JSON', () {
      final surveyDate = DateTime(2024, 1, 15);
      final createdAt = DateTime(2024, 1, 10);
      final updatedAt = DateTime(2024, 1, 15);

      final record = BiodiversityRecord(
        id: 'bio-001',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: surveyDate,
        surveyType: BiodiversitySurveyType.beneficialInsects,
        speciesCount: 12,
        beneficialInsectCount: 8,
        pollinatorCount: 5,
        speciesObserved: ['Bee', 'Butterfly', 'Ladybug'],
        habitatFeatures: ['Hedgerow', 'Wildflower patch'],
        diversityIndex: 0.85,
        habitatQualityScore: 78.5,
        notes: 'Good biodiversity',
        notesAr: 'تنوع بيولوجي جيد',
        synced: false,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );

      final json = record.toJson();

      expect(json['id'], 'bio-001');
      expect(json['farm_id'], 'farm-1');
      expect(json['tenant_id'], 'tenant-1');
      expect(json['survey_type'], 'beneficial_insects');
      expect(json['species_count'], 12);
      expect(json['beneficial_insect_count'], 8);
      expect(json['pollinator_count'], 5);
      expect(json['species_observed'], isA<List<String>>());
      expect(json['species_observed'].length, 3);
      expect(json['habitat_features'], isA<List<String>>());
      expect(json['habitat_features'].length, 2);
      expect(json['diversity_index'], 0.85);
      expect(json['habitat_quality_score'], 78.5);
      expect(json['notes'], 'Good biodiversity');
      expect(json['notes_ar'], 'تنوع بيولوجي جيد');
    });

    test('copyWith creates new instance with updated fields', () {
      final original = BiodiversityRecord(
        id: 'bio-001',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: DateTime.now(),
        surveyType: BiodiversitySurveyType.speciesCount,
        speciesCount: 10,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final updated = original.copyWith(
        speciesCount: 15,
        beneficialInsectCount: 8,
      );

      expect(updated.id, original.id);
      expect(updated.speciesCount, 15);
      expect(updated.beneficialInsectCount, 8);
      expect(updated.farmId, original.farmId);
    });
  });

  group('SoilHealthRecord', () {
    test('calculatedHealthScore returns healthScore when available', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 92.5,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedHealthScore, 92.5);
    });

    test('calculatedHealthScore calculates from soil properties', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        organicMatterPercent: 3.5, // +15
        earthwormCount: 12,         // +15
        phLevel: 6.8,               // +10
        healthScore: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      // Base 50 + 15 (organic) + 15 (worms) + 10 (pH) = 90
      expect(record.calculatedHealthScore, 90.0);
    });

    test('calculatedHealthScore uses defaults when no properties available', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      // Default base score is 50
      expect(record.calculatedHealthScore, 50.0);
    });

    test('calculatedHealthScore handles partial properties correctly', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        organicMatterPercent: 2.5, // +10 (>=2)
        earthwormCount: 3,          // +5 (>=1)
        phLevel: 8.5,               // +0 (out of ideal range)
        healthScore: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      // Base 50 + 10 (organic) + 5 (worms) + 0 (pH) = 65
      expect(record.calculatedHealthScore, 65.0);
    });

    test('calculatedStatus returns correct status based on score - excellent', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 85.0,
        status: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedStatus, SoilHealthStatus.excellent);
    });

    test('calculatedStatus returns correct status based on score - good', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 65.0,
        status: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedStatus, SoilHealthStatus.good);
    });

    test('calculatedStatus returns correct status based on score - fair', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 45.0,
        status: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedStatus, SoilHealthStatus.fair);
    });

    test('calculatedStatus returns correct status based on score - poor', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 30.0,
        status: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedStatus, SoilHealthStatus.poor);
    });

    test('calculatedStatus returns provided status when available', () {
      final record = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 30.0,
        status: SoilHealthStatus.excellent,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.calculatedStatus, SoilHealthStatus.excellent);
    });

    test('toJson produces valid JSON', () {
      final sampleDate = DateTime(2024, 1, 15);
      final createdAt = DateTime(2024, 1, 10);
      final updatedAt = DateTime(2024, 1, 15);

      final record = SoilHealthRecord(
        id: 'soil-001',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: sampleDate,
        sampleDepthCm: 30,
        organicMatterPercent: 3.2,
        soilTexture: 'loam',
        bulkDensity: 1.3,
        waterInfiltrationRate: 2.5,
        aggregateStability: 85.0,
        earthwormCount: 10,
        microbialBiomass: 450.0,
        respirationRate: 12.5,
        phLevel: 6.8,
        ecLevel: 0.5,
        cecLevel: 15.0,
        healthScore: 88.0,
        status: SoilHealthStatus.excellent,
        notes: 'Healthy soil',
        notesAr: 'تربة صحية',
        labReportUrl: 'https://example.com/report.pdf',
        synced: false,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );

      final json = record.toJson();

      expect(json['id'], 'soil-001');
      expect(json['field_id'], 'field-1');
      expect(json['tenant_id'], 'tenant-1');
      expect(json['sample_depth_cm'], 30);
      expect(json['organic_matter_percent'], 3.2);
      expect(json['soil_texture'], 'loam');
      expect(json['bulk_density'], 1.3);
      expect(json['water_infiltration_rate'], 2.5);
      expect(json['aggregate_stability'], 85.0);
      expect(json['earthworm_count'], 10);
      expect(json['microbial_biomass'], 450.0);
      expect(json['respiration_rate'], 12.5);
      expect(json['ph_level'], 6.8);
      expect(json['ec_level'], 0.5);
      expect(json['cec_level'], 15.0);
      expect(json['health_score'], 88.0);
      expect(json['status'], 'excellent');
      expect(json['notes'], 'Healthy soil');
      expect(json['notes_ar'], 'تربة صحية');
      expect(json['lab_report_url'], 'https://example.com/report.pdf');
    });

    test('copyWith creates new instance with updated fields', () {
      final original = SoilHealthRecord(
        id: 'soil-001',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 75.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final updated = original.copyWith(
        healthScore: 85.0,
        status: SoilHealthStatus.excellent,
      );

      expect(updated.id, original.id);
      expect(updated.healthScore, 85.0);
      expect(updated.status, SoilHealthStatus.excellent);
    });
  });

  group('WaterConservationRecord', () {
    test('isEfficient returns true when efficiency >= 70%', () {
      final record = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        efficiencyPercentage: 75.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.isEfficient, true);
    });

    test('isEfficient returns true when efficiency exactly 70%', () {
      final record = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        efficiencyPercentage: 70.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.isEfficient, true);
    });

    test('isEfficient returns false when efficiency < 70%', () {
      final record = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        efficiencyPercentage: 65.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.isEfficient, false);
    });

    test('isEfficient returns false when efficiency is null', () {
      final record = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        efficiencyPercentage: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.isEfficient, false);
    });

    test('savingsPercentage returns comparisonToBaseline', () {
      final record = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        comparisonToBaseline: 15.5,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.savingsPercentage, 15.5);
    });

    test('savingsPercentage returns 0 when null', () {
      final record = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        comparisonToBaseline: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.savingsPercentage, 0.0);
    });

    test('toJson produces valid JSON', () {
      final recordDate = DateTime(2024, 1, 15);
      final createdAt = DateTime(2024, 1, 10);
      final updatedAt = DateTime(2024, 1, 15);

      final record = WaterConservationRecord(
        id: 'water-001',
        farmId: 'farm-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        recordDate: recordDate,
        periodType: 'weekly',
        waterUsedLiters: 50000.0,
        waterSource: 'well',
        irrigationMethod: 'drip',
        waterPerHectare: 2500.0,
        efficiencyPercentage: 78.5,
        comparisonToBaseline: 12.5,
        mulchingApplied: true,
        dripIrrigationUsed: true,
        rainwaterHarvestedLiters: 5000.0,
        notes: 'Good water management',
        notesAr: 'إدارة مياه جيدة',
        synced: false,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );

      final json = record.toJson();

      expect(json['id'], 'water-001');
      expect(json['farm_id'], 'farm-1');
      expect(json['field_id'], 'field-1');
      expect(json['tenant_id'], 'tenant-1');
      expect(json['period_type'], 'weekly');
      expect(json['water_used_liters'], 50000.0);
      expect(json['water_source'], 'well');
      expect(json['irrigation_method'], 'drip');
      expect(json['water_per_hectare'], 2500.0);
      expect(json['efficiency_percentage'], 78.5);
      expect(json['comparison_to_baseline'], 12.5);
      expect(json['mulching_applied'], true);
      expect(json['drip_irrigation_used'], true);
      expect(json['rainwater_harvested_liters'], 5000.0);
      expect(json['notes'], 'Good water management');
      expect(json['notes_ar'], 'إدارة مياه جيدة');
    });

    test('copyWith creates new instance with updated fields', () {
      final original = WaterConservationRecord(
        id: 'water-001',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        efficiencyPercentage: 70.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final updated = original.copyWith(
        efficiencyPercentage: 80.0,
        mulchingApplied: true,
      );

      expect(updated.id, original.id);
      expect(updated.efficiencyPercentage, 80.0);
      expect(updated.mulchingApplied, true);
    });
  });

  group('FarmPracticeRecord', () {
    test('isCompleted returns true when status is implemented', () {
      final record = FarmPracticeRecord(
        id: 'practice-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        practiceId: 'p-1',
        practiceName: 'Composting',
        category: 'soil',
        status: PracticeStatus.implemented,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.isCompleted, true);
    });

    test('isCompleted returns false when status is not implemented', () {
      final statuses = [
        PracticeStatus.planned,
        PracticeStatus.inProgress,
        PracticeStatus.paused,
        PracticeStatus.abandoned,
      ];

      for (final status in statuses) {
        final record = FarmPracticeRecord(
          id: 'practice-1',
          farmId: 'farm-1',
          tenantId: 'tenant-1',
          practiceId: 'p-1',
          practiceName: 'Composting',
          category: 'soil',
          status: status,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(record.isCompleted, false);
      }
    });

    test('supportsGlobalGap returns true when control points exist', () {
      final record = FarmPracticeRecord(
        id: 'practice-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        practiceId: 'p-1',
        practiceName: 'Integrated Pest Management',
        category: 'pest_control',
        status: PracticeStatus.implemented,
        globalgapControlPoints: ['CB.5.1.1', 'CB.5.2.1'],
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.supportsGlobalGap, true);
    });

    test('supportsGlobalGap returns false when no control points', () {
      final record = FarmPracticeRecord(
        id: 'practice-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        practiceId: 'p-1',
        practiceName: 'Composting',
        category: 'soil',
        status: PracticeStatus.implemented,
        globalgapControlPoints: [],
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.supportsGlobalGap, false);
    });

    test('effectivenessPercentage calculates correctly', () {
      final testCases = [
        {'rating': 1, 'expected': 20},
        {'rating': 2, 'expected': 40},
        {'rating': 3, 'expected': 60},
        {'rating': 4, 'expected': 80},
        {'rating': 5, 'expected': 100},
      ];

      for (final testCase in testCases) {
        final record = FarmPracticeRecord(
          id: 'practice-1',
          farmId: 'farm-1',
          tenantId: 'tenant-1',
          practiceId: 'p-1',
          practiceName: 'Composting',
          category: 'soil',
          status: PracticeStatus.implemented,
          effectivenessRating: testCase['rating'] as int,
          createdAt: DateTime.now(),
          updatedAt: DateTime.now(),
        );

        expect(record.effectivenessPercentage, testCase['expected']);
      }
    });

    test('effectivenessPercentage returns 0 when rating is null', () {
      final record = FarmPracticeRecord(
        id: 'practice-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        practiceId: 'p-1',
        practiceName: 'Composting',
        category: 'soil',
        status: PracticeStatus.implemented,
        effectivenessRating: null,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      expect(record.effectivenessPercentage, 0);
    });

    test('toJson produces valid JSON', () {
      final startDate = DateTime(2024, 1, 1);
      final implementationDate = DateTime(2024, 1, 15);
      final createdAt = DateTime(2024, 1, 1);
      final updatedAt = DateTime(2024, 1, 15);

      final record = FarmPracticeRecord(
        id: 'practice-001',
        farmId: 'farm-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        practiceId: 'p-composting',
        practiceName: 'Composting',
        practiceNameAr: 'التسميد العضوي',
        category: 'soil_health',
        status: PracticeStatus.implemented,
        startDate: startDate,
        implementationDate: implementationDate,
        implementationNotes: 'Successfully implemented',
        implementationNotesAr: 'تم التنفيذ بنجاح',
        materialsUsed: ['Organic waste', 'Manure'],
        laborHours: 25.5,
        costEstimate: 500.0,
        observedBenefits: ['Better soil', 'Higher yields'],
        challenges: ['Initial setup time'],
        effectivenessRating: 4,
        globalgapControlPoints: ['CB.5.1.1'],
        synced: false,
        createdAt: createdAt,
        updatedAt: updatedAt,
      );

      final json = record.toJson();

      expect(json['id'], 'practice-001');
      expect(json['farm_id'], 'farm-1');
      expect(json['field_id'], 'field-1');
      expect(json['tenant_id'], 'tenant-1');
      expect(json['practice_id'], 'p-composting');
      expect(json['practice_name'], 'Composting');
      expect(json['practice_name_ar'], 'التسميد العضوي');
      expect(json['category'], 'soil_health');
      expect(json['status'], 'implemented');
      expect(json['implementation_notes'], 'Successfully implemented');
      expect(json['implementation_notes_ar'], 'تم التنفيذ بنجاح');
      expect(json['materials_used'], isA<List<String>>());
      expect(json['materials_used'].length, 2);
      expect(json['labor_hours'], 25.5);
      expect(json['cost_estimate'], 500.0);
      expect(json['observed_benefits'], isA<List<String>>());
      expect(json['observed_benefits'].length, 2);
      expect(json['challenges'], isA<List<String>>());
      expect(json['challenges'].length, 1);
      expect(json['effectiveness_rating'], 4);
      expect(json['globalgap_control_points'], isA<List<String>>());
      expect(json['globalgap_control_points'].length, 1);
    });

    test('copyWith creates new instance with updated fields', () {
      final original = FarmPracticeRecord(
        id: 'practice-001',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        practiceId: 'p-1',
        practiceName: 'Composting',
        category: 'soil',
        status: PracticeStatus.planned,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final updated = original.copyWith(
        status: PracticeStatus.implemented,
        effectivenessRating: 5,
      );

      expect(updated.id, original.id);
      expect(updated.status, PracticeStatus.implemented);
      expect(updated.effectivenessRating, 5);
    });
  });

  group('PracticeStatus', () {
    test('fromString parses all values correctly', () {
      expect(PracticeStatus.fromString('planned'), PracticeStatus.planned);
      expect(PracticeStatus.fromString('in_progress'), PracticeStatus.inProgress);
      expect(PracticeStatus.fromString('implemented'), PracticeStatus.implemented);
      expect(PracticeStatus.fromString('paused'), PracticeStatus.paused);
      expect(PracticeStatus.fromString('abandoned'), PracticeStatus.abandoned);
    });

    test('fromString returns default for invalid values', () {
      expect(PracticeStatus.fromString('invalid'), PracticeStatus.planned);
      expect(PracticeStatus.fromString(''), PracticeStatus.planned);
      expect(PracticeStatus.fromString('unknown'), PracticeStatus.planned);
    });

    test('value getter returns correct strings', () {
      expect(PracticeStatus.planned.value, 'planned');
      expect(PracticeStatus.inProgress.value, 'in_progress');
      expect(PracticeStatus.implemented.value, 'implemented');
      expect(PracticeStatus.paused.value, 'paused');
      expect(PracticeStatus.abandoned.value, 'abandoned');
    });
  });

  group('BiodiversitySurveyType', () {
    test('fromString parses all values correctly', () {
      expect(BiodiversitySurveyType.fromString('species_count'),
          BiodiversitySurveyType.speciesCount);
      expect(BiodiversitySurveyType.fromString('habitat_assessment'),
          BiodiversitySurveyType.habitatAssessment);
      expect(BiodiversitySurveyType.fromString('beneficial_insects'),
          BiodiversitySurveyType.beneficialInsects);
      expect(BiodiversitySurveyType.fromString('soil_organisms'),
          BiodiversitySurveyType.soilOrganisms);
      expect(BiodiversitySurveyType.fromString('general'),
          BiodiversitySurveyType.general);
    });

    test('fromString returns default for invalid values', () {
      expect(BiodiversitySurveyType.fromString('invalid'),
          BiodiversitySurveyType.general);
      expect(BiodiversitySurveyType.fromString(''),
          BiodiversitySurveyType.general);
    });

    test('value getter returns correct strings', () {
      expect(BiodiversitySurveyType.speciesCount.value, 'species_count');
      expect(BiodiversitySurveyType.habitatAssessment.value, 'habitat_assessment');
      expect(BiodiversitySurveyType.beneficialInsects.value, 'beneficial_insects');
      expect(BiodiversitySurveyType.soilOrganisms.value, 'soil_organisms');
      expect(BiodiversitySurveyType.general.value, 'general');
    });
  });

  group('SoilHealthStatus', () {
    test('fromString parses all values correctly', () {
      expect(SoilHealthStatus.fromString('poor'), SoilHealthStatus.poor);
      expect(SoilHealthStatus.fromString('fair'), SoilHealthStatus.fair);
      expect(SoilHealthStatus.fromString('good'), SoilHealthStatus.good);
      expect(SoilHealthStatus.fromString('excellent'), SoilHealthStatus.excellent);
    });

    test('fromString returns default for invalid values', () {
      expect(SoilHealthStatus.fromString('invalid'), SoilHealthStatus.fair);
      expect(SoilHealthStatus.fromString(''), SoilHealthStatus.fair);
    });

    test('value getter returns correct strings', () {
      expect(SoilHealthStatus.poor.value, 'poor');
      expect(SoilHealthStatus.fair.value, 'fair');
      expect(SoilHealthStatus.good.value, 'good');
      expect(SoilHealthStatus.excellent.value, 'excellent');
    });
  });

  group('EcologicalDashboardData', () {
    test('practiceImplementationRate calculates correctly', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 10,
        implementedPractices: 7,
        totalRecordsCount: 25,
      );

      expect(data.practiceImplementationRate, 70.0);
    });

    test('practiceImplementationRate returns 0 when no practices', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 0,
        implementedPractices: 0,
        totalRecordsCount: 0,
      );

      expect(data.practiceImplementationRate, 0.0);
    });

    test('practiceImplementationRate handles partial implementation', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 15,
        implementedPractices: 5,
        totalRecordsCount: 20,
      );

      // 5/15 * 100 = 33.333...
      expect(data.practiceImplementationRate, closeTo(33.33, 0.01));
    });

    test('practiceImplementationRate returns 100 for full implementation', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 8,
        implementedPractices: 8,
        totalRecordsCount: 24,
      );

      expect(data.practiceImplementationRate, 100.0);
    });

    test('isFresh returns true for recent data', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 10,
        implementedPractices: 7,
        totalRecordsCount: 25,
        lastUpdated: DateTime.now().subtract(const Duration(days: 5)),
      );

      expect(data.isFresh, true);
    });

    test('isFresh returns true for data exactly 30 days old', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 10,
        implementedPractices: 7,
        totalRecordsCount: 25,
        lastUpdated: DateTime.now().subtract(const Duration(days: 30)),
      );

      expect(data.isFresh, true);
    });

    test('isFresh returns false for old data', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 10,
        implementedPractices: 7,
        totalRecordsCount: 25,
        lastUpdated: DateTime.now().subtract(const Duration(days: 31)),
      );

      expect(data.isFresh, false);
    });

    test('isFresh returns false when lastUpdated is null', () {
      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 10,
        implementedPractices: 7,
        totalRecordsCount: 25,
        lastUpdated: null,
      );

      expect(data.isFresh, false);
    });

    test('includes latest records when provided', () {
      final bioRecord = BiodiversityRecord(
        id: 'bio-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        surveyDate: DateTime.now(),
        surveyType: BiodiversitySurveyType.speciesCount,
        speciesCount: 10,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final soilRecord = SoilHealthRecord(
        id: 'soil-1',
        fieldId: 'field-1',
        tenantId: 'tenant-1',
        sampleDate: DateTime.now(),
        healthScore: 85.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final waterRecord = WaterConservationRecord(
        id: 'water-1',
        farmId: 'farm-1',
        tenantId: 'tenant-1',
        recordDate: DateTime.now(),
        periodType: 'weekly',
        efficiencyPercentage: 75.0,
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

      final data = EcologicalDashboardData(
        overallScore: 75.0,
        biodiversityScore: 70.0,
        soilHealthScore: 80.0,
        waterEfficiencyScore: 75.0,
        totalPractices: 10,
        implementedPractices: 7,
        latestBiodiversityRecord: bioRecord,
        latestSoilHealthRecord: soilRecord,
        latestWaterRecord: waterRecord,
        totalRecordsCount: 25,
        lastUpdated: DateTime.now(),
      );

      expect(data.latestBiodiversityRecord, isNotNull);
      expect(data.latestBiodiversityRecord!.id, 'bio-1');
      expect(data.latestSoilHealthRecord, isNotNull);
      expect(data.latestSoilHealthRecord!.id, 'soil-1');
      expect(data.latestWaterRecord, isNotNull);
      expect(data.latestWaterRecord!.id, 'water-1');
    });
  });
}
