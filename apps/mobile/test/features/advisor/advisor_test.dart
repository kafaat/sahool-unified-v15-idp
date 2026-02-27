/// Unit Tests for Advisor Feature Models
/// اختبارات وحدات نماذج المستشار الزراعي
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/advisor/data/models/fertilizer_models.dart';
import 'package:sahool_field_app/features/advisor/data/models/irrigation_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // SoilAnalysis Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SoilAnalysis', () {
    test('fromJson parses all required and optional fields', () {
      // Arrange
      final json = {
        'ph': 7.2,
        'nitrogen': 25.0,
        'phosphorus': 15.0,
        'potassium': 180.0,
        'organicMatter': 2.5,
        'soilType': 'Sandy Loam',
        'soilTypeAr': 'رملي طميي',
      };

      // Act
      final analysis = SoilAnalysis.fromJson(json);

      // Assert
      expect(analysis.ph, 7.2);
      expect(analysis.nitrogen, 25.0);
      expect(analysis.phosphorus, 15.0);
      expect(analysis.potassium, 180.0);
      expect(analysis.organicMatter, 2.5);
      expect(analysis.soilType, 'Sandy Loam');
      expect(analysis.soilTypeAr, 'رملي طميي');
    });

    test('fromJson uses defaults for optional fields', () {
      // Arrange
      final json = {
        'ph': 6.8,
        'nitrogen': 18.0,
        'phosphorus': 12.0,
        'potassium': 150.0,
      };

      // Act
      final analysis = SoilAnalysis.fromJson(json);

      // Assert
      expect(analysis.organicMatter, 0);
      expect(analysis.soilType, '');
      expect(analysis.soilTypeAr, '');
    });

    test('copyWith preserves unchanged fields', () {
      // Arrange
      final analysis = const SoilAnalysis(
        ph: 7.0,
        nitrogen: 20.0,
        phosphorus: 14.0,
        potassium: 160.0,
      );

      // Act
      final modified = analysis.copyWith(ph: 6.5);

      // Assert
      expect(modified.ph, 6.5);
      expect(modified.nitrogen, 20.0); // Unchanged
    });

    test('equality works correctly', () {
      // Arrange
      const a = SoilAnalysis(ph: 7.0, nitrogen: 20.0, phosphorus: 14.0, potassium: 160.0);
      const b = SoilAnalysis(ph: 7.0, nitrogen: 20.0, phosphorus: 14.0, potassium: 160.0);

      // Assert
      expect(a, equals(b));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FertilizerRequest Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FertilizerRequest', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'cropType': 'wheat',
        'fieldArea': 10.5,
        'soilAnalysis': {
          'ph': 7.2,
          'nitrogen': 18.0,
          'phosphorus': 12.0,
          'potassium': 150.0,
        },
        'growthStage': 'tillering',
        'governorate': 'Riyadh',
        'irrigationType': 'drip',
      };

      // Act
      final request = FertilizerRequest.fromJson(json);

      // Assert
      expect(request.cropType, 'wheat');
      expect(request.fieldArea, 10.5);
      expect(request.soilAnalysis.ph, 7.2);
      expect(request.growthStage, 'tillering');
      expect(request.governorate, 'Riyadh');
      expect(request.irrigationType, 'drip');
    });

    test('uses defaults for optional fields', () {
      // Arrange
      final json = {
        'cropType': 'barley',
        'fieldArea': 5.0,
        'soilAnalysis': {
          'ph': 6.5,
          'nitrogen': 15.0,
          'phosphorus': 10.0,
          'potassium': 120.0,
        },
        'growthStage': 'seeding',
      };

      // Act
      final request = FertilizerRequest.fromJson(json);

      // Assert
      expect(request.governorate, '');
      expect(request.irrigationType, '');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NpkRecommendation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NpkRecommendation', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'nitrogenKg': 46.0,
        'phosphorusKg': 23.0,
        'potassiumKg': 15.0,
        'totalKgPerHectare': 84.0,
        'totalKgForField': 840.0,
        'applicationMethod': 'broadcast',
        'applicationMethodAr': 'بث',
        'timing': 'Before irrigation',
        'timingAr': 'قبل الري',
      };

      // Act
      final npk = NpkRecommendation.fromJson(json);

      // Assert
      expect(npk.nitrogenKg, 46.0);
      expect(npk.phosphorusKg, 23.0);
      expect(npk.potassiumKg, 15.0);
      expect(npk.totalKgPerHectare, 84.0);
      expect(npk.totalKgForField, 840.0);
      expect(npk.applicationMethod, 'broadcast');
      expect(npk.applicationMethodAr, 'بث');
      expect(npk.timing, 'Before irrigation');
      expect(npk.timingAr, 'قبل الري');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FertilizerProduct Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FertilizerProduct', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'productId': 'FERT-001',
        'name': 'Urea 46%',
        'nameAr': 'يوريا 46%',
        'npkRatio': '46-0-0',
        'quantityKg': 100.0,
        'pricePerKg': 1.5,
        'applicationNotes': 'Apply early morning',
        'applicationNotesAr': 'تطبيق في الصباح الباكر',
      };

      // Act
      final product = FertilizerProduct.fromJson(json);

      // Assert
      expect(product.productId, 'FERT-001');
      expect(product.name, 'Urea 46%');
      expect(product.nameAr, 'يوريا 46%');
      expect(product.npkRatio, '46-0-0');
      expect(product.quantityKg, 100.0);
      expect(product.pricePerKg, 1.5);
    });

    test('defaults pricePerKg to 0', () {
      // Arrange
      final json = {
        'productId': 'FERT-002',
        'name': 'DAP',
        'nameAr': 'داب',
        'npkRatio': '18-46-0',
        'quantityKg': 50.0,
      };

      // Act
      final product = FertilizerProduct.fromJson(json);

      // Assert
      expect(product.pricePerKg, 0);
      expect(product.applicationNotes, '');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FertilizerRecommendation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FertilizerRecommendation', () {
    test('fromJson parses full recommendation', () {
      // Arrange
      final json = {
        'recommendationId': 'REC-001',
        'fieldId': 'FIELD-001',
        'cropType': 'wheat',
        'cropTypeAr': 'قمح',
        'npkRecommendation': {
          'nitrogenKg': 46.0,
          'phosphorusKg': 23.0,
          'potassiumKg': 15.0,
          'totalKgPerHectare': 84.0,
          'totalKgForField': 840.0,
        },
        'suggestedProducts': [
          {
            'productId': 'P1',
            'name': 'Urea',
            'nameAr': 'يوريا',
            'npkRatio': '46-0-0',
            'quantityKg': 100.0,
          },
        ],
        'soilHealthStatus': 'fair',
        'soilHealthStatusAr': 'مقبول',
        'deficiencies': ['nitrogen'],
        'deficienciesAr': ['نيتروجين'],
        'warnings': ['Apply before rain'],
        'warningsAr': ['تطبيق قبل المطر'],
        'generatedAt': '2025-06-15T10:00:00Z',
        'seasonalNote': 'Winter planting season',
        'seasonalNoteAr': 'موسم زراعة شتوي',
      };

      // Act
      final rec = FertilizerRecommendation.fromJson(json);

      // Assert
      expect(rec.recommendationId, 'REC-001');
      expect(rec.fieldId, 'FIELD-001');
      expect(rec.cropType, 'wheat');
      expect(rec.cropTypeAr, 'قمح');
      expect(rec.npkRecommendation.nitrogenKg, 46.0);
      expect(rec.suggestedProducts, hasLength(1));
      expect(rec.soilHealthStatus, 'fair');
      expect(rec.soilHealthStatusAr, 'مقبول');
      expect(rec.deficiencies, ['nitrogen']);
      expect(rec.deficienciesAr, ['نيتروجين']);
      expect(rec.warnings, ['Apply before rain']);
      expect(rec.seasonalNote, 'Winter planting season');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DeficiencySymptom Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('DeficiencySymptom', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'nutrient': 'Nitrogen',
        'nutrientAr': 'نيتروجين',
        'severity': 'high',
        'visualSymptoms': ['Yellowing leaves', 'Stunted growth'],
        'visualSymptomsAr': ['اصفرار الأوراق', 'تقزم النمو'],
        'recommendation': 'Apply Urea 46 kg/ha',
        'recommendationAr': 'تطبيق يوريا 46 كجم/هكتار',
        'imageUrl': 'https://example.com/nitrogen.jpg',
      };

      // Act
      final symptom = DeficiencySymptom.fromJson(json);

      // Assert
      expect(symptom.nutrient, 'Nitrogen');
      expect(symptom.nutrientAr, 'نيتروجين');
      expect(symptom.severity, 'high');
      expect(symptom.visualSymptoms, hasLength(2));
      expect(symptom.visualSymptomsAr, hasLength(2));
      expect(symptom.recommendation, 'Apply Urea 46 kg/ha');
      expect(symptom.imageUrl, 'https://example.com/nitrogen.jpg');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SoilInterpretation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SoilInterpretation', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'overallHealth': 'good',
        'overallHealthAr': 'جيدة',
        'nutrientLevels': {'nitrogen': 'low', 'phosphorus': 'adequate'},
        'nutrientLevelsAr': {'nitrogen': 'منخفض', 'phosphorus': 'كاف'},
        'recommendations': ['Increase nitrogen application'],
        'recommendationsAr': ['زيادة تطبيق النيتروجين'],
        'fertilitySCore': 72.5,
      };

      // Act
      final interp = SoilInterpretation.fromJson(json);

      // Assert
      expect(interp.overallHealth, 'good');
      expect(interp.overallHealthAr, 'جيدة');
      expect(interp.nutrientLevels['nitrogen'], 'low');
      expect(interp.nutrientLevelsAr['nitrogen'], 'منخفض');
      expect(interp.recommendations, ['Increase nitrogen application']);
      expect(interp.fertilitySCore, 72.5);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropTypeOption Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropTypeOption', () {
    test('fromJson parses correctly with growth stages', () {
      // Arrange
      final json = {
        'id': 'wheat',
        'name': 'Wheat',
        'nameAr': 'قمح',
        'category': 'cereals',
        'categoryAr': 'حبوب',
        'growthStages': ['seeding', 'tillering', 'heading', 'ripening'],
        'growthStagesAr': ['بذر', 'تفريع', 'تسنبل', 'نضج'],
      };

      // Act
      final option = CropTypeOption.fromJson(json);

      // Assert
      expect(option.id, 'wheat');
      expect(option.name, 'Wheat');
      expect(option.nameAr, 'قمح');
      expect(option.category, 'cereals');
      expect(option.growthStages, hasLength(4));
      expect(option.growthStagesAr, hasLength(4));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IrrigationRequest Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationRequest', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'cropType': 'wheat',
        'growthStage': 'tillering',
        'fieldArea': 8.5,
        'soilType': 'loam',
        'irrigationMethod': 'drip',
        'currentSoilMoisture': 35.0,
        'temperature': 28.0,
        'humidity': 45.0,
        'governorate': 'Qassim',
      };

      // Act
      final request = IrrigationRequest.fromJson(json);

      // Assert
      expect(request.cropType, 'wheat');
      expect(request.growthStage, 'tillering');
      expect(request.fieldArea, 8.5);
      expect(request.soilType, 'loam');
      expect(request.irrigationMethod, 'drip');
      expect(request.currentSoilMoisture, 35.0);
      expect(request.temperature, 28.0);
      expect(request.humidity, 45.0);
      expect(request.governorate, 'Qassim');
    });

    test('defaults optional fields to 0 and empty', () {
      // Arrange
      final json = {
        'cropType': 'barley',
        'growthStage': 'heading',
        'fieldArea': 5.0,
        'soilType': 'clay',
        'irrigationMethod': 'flood',
      };

      // Act
      final request = IrrigationRequest.fromJson(json);

      // Assert
      expect(request.currentSoilMoisture, 0);
      expect(request.temperature, 0);
      expect(request.humidity, 0);
      expect(request.governorate, '');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IrrigationCalculation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationCalculation', () {
    test('fromJson parses all fields', () {
      // Arrange
      final json = {
        'waterRequirementMm': 5.5,
        'waterRequirementLiters': 55000.0,
        'totalWaterLiters': 467500.0,
        'etCrop': 4.8,
        'irrigationEfficiency': 90.0,
        'recommendedFrequency': 'Every 3 days',
        'recommendedFrequencyAr': 'كل 3 أيام',
        'durationMinutes': 120,
        'notes': 'Consider wind conditions',
        'notesAr': 'مراعاة ظروف الرياح',
      };

      // Act
      final calc = IrrigationCalculation.fromJson(json);

      // Assert
      expect(calc.waterRequirementMm, 5.5);
      expect(calc.waterRequirementLiters, 55000.0);
      expect(calc.totalWaterLiters, 467500.0);
      expect(calc.etCrop, 4.8);
      expect(calc.irrigationEfficiency, 90.0);
      expect(calc.recommendedFrequency, 'Every 3 days');
      expect(calc.recommendedFrequencyAr, 'كل 3 أيام');
      expect(calc.durationMinutes, 120);
      expect(calc.notes, 'Consider wind conditions');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // WaterBalance Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('WaterBalance', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'soilMoisturePercent': 45.0,
        'fieldCapacity': 35.0,
        'wiltingPoint': 15.0,
        'availableWater': 20.0,
        'depletionPercent': 50.0,
        'status': 'low',
        'statusAr': 'منخفض',
        'irrigationNeeded': true,
        'recommendedWaterMm': 25.0,
      };

      // Act
      final balance = WaterBalance.fromJson(json);

      // Assert
      expect(balance.soilMoisturePercent, 45.0);
      expect(balance.fieldCapacity, 35.0);
      expect(balance.wiltingPoint, 15.0);
      expect(balance.availableWater, 20.0);
      expect(balance.depletionPercent, 50.0);
      expect(balance.status, 'low');
      expect(balance.statusAr, 'منخفض');
      expect(balance.irrigationNeeded, true);
      expect(balance.recommendedWaterMm, 25.0);
    });

    test('recommendedWaterMm defaults to 0', () {
      // Arrange
      final json = {
        'soilMoisturePercent': 60.0,
        'fieldCapacity': 35.0,
        'wiltingPoint': 15.0,
        'availableWater': 20.0,
        'depletionPercent': 30.0,
        'status': 'optimal',
        'statusAr': 'مثالي',
        'irrigationNeeded': false,
      };

      // Act
      final balance = WaterBalance.fromJson(json);

      // Assert
      expect(balance.recommendedWaterMm, 0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IrrigationMethodOption Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationMethodOption', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'id': 'drip',
        'name': 'Drip Irrigation',
        'nameAr': 'ري بالتنقيط',
        'efficiency': 95.0,
        'description': 'Water delivered to root zone',
        'descriptionAr': 'توصيل المياه لمنطقة الجذور',
        'suitableCrops': ['tomato', 'cucumber'],
        'suitableCropsAr': ['طماطم', 'خيار'],
      };

      // Act
      final method = IrrigationMethodOption.fromJson(json);

      // Assert
      expect(method.id, 'drip');
      expect(method.name, 'Drip Irrigation');
      expect(method.nameAr, 'ري بالتنقيط');
      expect(method.efficiency, 95.0);
      expect(method.suitableCrops, hasLength(2));
      expect(method.suitableCropsAr, hasLength(2));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropWaterRequirement Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropWaterRequirement', () {
    test('fromJson parses Kc coefficients and root depth', () {
      // Arrange
      final json = {
        'cropId': 'wheat',
        'cropName': 'Wheat',
        'cropNameAr': 'قمح',
        'stageRequirements': {
          'initial': 3.0,
          'development': 4.5,
          'mid': 6.0,
          'late': 3.5,
        },
        'kcInitial': 0.4,
        'kcMid': 1.15,
        'kcEnd': 0.3,
        'rootDepthCm': 120,
        'criticalDepletionFraction': 0.55,
      };

      // Act
      final req = CropWaterRequirement.fromJson(json);

      // Assert
      expect(req.cropId, 'wheat');
      expect(req.cropName, 'Wheat');
      expect(req.cropNameAr, 'قمح');
      expect(req.kcInitial, 0.4);
      expect(req.kcMid, 1.15);
      expect(req.kcEnd, 0.3);
      expect(req.rootDepthCm, 120);
      expect(req.criticalDepletionFraction, 0.55);
      expect(req.stageRequirements['mid'], 6.0);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IrrigationSchedule & IrrigationEvent Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationSchedule', () {
    test('fromJson parses schedule with events', () {
      // Arrange
      final json = {
        'scheduleId': 'SCHED-001',
        'fieldId': 'FIELD-001',
        'events': [
          {
            'eventId': 'EVT-001',
            'scheduledTime': '2025-06-15T06:00:00Z',
            'durationMinutes': 60,
            'waterLiters': 5000.0,
            'status': 'pending',
            'statusAr': 'قيد الانتظار',
          },
          {
            'eventId': 'EVT-002',
            'scheduledTime': '2025-06-18T06:00:00Z',
            'durationMinutes': 90,
            'waterLiters': 7500.0,
            'status': 'completed',
            'statusAr': 'مكتملة',
          },
        ],
        'startDate': '2025-06-15T00:00:00Z',
        'endDate': '2025-07-15T00:00:00Z',
        'totalWaterPlanned': 50000.0,
        'notes': 'Summer schedule',
        'notesAr': 'جدول الصيف',
      };

      // Act
      final schedule = IrrigationSchedule.fromJson(json);

      // Assert
      expect(schedule.scheduleId, 'SCHED-001');
      expect(schedule.fieldId, 'FIELD-001');
      expect(schedule.events, hasLength(2));
      expect(schedule.events.first.eventId, 'EVT-001');
      expect(schedule.events.first.durationMinutes, 60);
      expect(schedule.events.first.waterLiters, 5000.0);
      expect(schedule.events.first.status, 'pending');
      expect(schedule.events.last.status, 'completed');
      expect(schedule.totalWaterPlanned, 50000.0);
      expect(schedule.notes, 'Summer schedule');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // IrrigationEfficiencyReport Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('IrrigationEfficiencyReport', () {
    test('fromJson parses correctly', () {
      // Arrange
      final json = {
        'reportId': 'RPT-001',
        'fieldId': 'FIELD-001',
        'period': 'weekly',
        'waterUsedLiters': 45000.0,
        'waterSavedLiters': 5000.0,
        'efficiencyPercent': 90.0,
        'costSaved': 250.0,
        'dailyUsage': {'2025-06-10': 7500.0, '2025-06-11': 6500.0},
        'recommendations': ['Optimize morning irrigation'],
        'recommendationsAr': ['تحسين الري الصباحي'],
        'generatedAt': '2025-06-15T10:00:00Z',
      };

      // Act
      final report = IrrigationEfficiencyReport.fromJson(json);

      // Assert
      expect(report.reportId, 'RPT-001');
      expect(report.period, 'weekly');
      expect(report.waterUsedLiters, 45000.0);
      expect(report.waterSavedLiters, 5000.0);
      expect(report.efficiencyPercent, 90.0);
      expect(report.costSaved, 250.0);
      expect(report.dailyUsage, hasLength(2));
      expect(report.recommendations, ['Optimize morning irrigation']);
      expect(report.recommendationsAr, ['تحسين الري الصباحي']);
    });
  });
}
