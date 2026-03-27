import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/gdd/models/gdd_models.dart';

void main() {
  group('CropType enum', () {
    test('has 10 Yemen-specific crops', () {
      expect(CropType.values, hasLength(10));
    });

    test('getName returns Arabic for ar locale', () {
      expect(CropType.wheat.getName('ar'), 'قمح');
      expect(CropType.coffee.getName('ar'), 'بن');
      expect(CropType.sorghum.getName('ar'), 'ذرة رفيعة');
    });

    test('getName returns English for en locale', () {
      expect(CropType.wheat.getName('en'), 'Wheat');
      expect(CropType.coffee.getName('en'), 'Coffee');
    });

    test('fromString resolves known crops', () {
      expect(CropType.fromString('wheat'), CropType.wheat);
      expect(CropType.fromString('coffee'), CropType.coffee);
      expect(CropType.fromString('tomato'), CropType.tomato);
    });

    test('fromString defaults to wheat for unknown', () {
      expect(CropType.fromString('unknown'), CropType.wheat);
    });
  });

  group('GDDCalculationMethod enum', () {
    test('has 3 methods', () {
      expect(GDDCalculationMethod.values, hasLength(3));
    });

    test('getName returns bilingual names', () {
      expect(GDDCalculationMethod.average.getName('ar'), 'متوسط');
      expect(GDDCalculationMethod.average.getName('en'), 'Average Method');
      expect(GDDCalculationMethod.sine.getName('ar'), 'موجة جيبية');
      expect(GDDCalculationMethod.modifiedAverage.getName('ar'), 'متوسط معدل');
    });

    test('fromString resolves known methods', () {
      expect(
        GDDCalculationMethod.fromString('average'),
        GDDCalculationMethod.average,
      );
      expect(
        GDDCalculationMethod.fromString('sine'),
        GDDCalculationMethod.sine,
      );
      expect(
        GDDCalculationMethod.fromString('modified_average'),
        GDDCalculationMethod.modifiedAverage,
      );
    });

    test('fromString defaults to average for unknown', () {
      expect(
        GDDCalculationMethod.fromString('unknown'),
        GDDCalculationMethod.average,
      );
    });
  });

  group('GrowthStage', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'stage_id': 'germination',
        'stage_name': 'Germination',
        'stage_name_ar': 'الإنبات',
        'stage_number': 1,
        'gdd_required': 100.0,
        'gdd_start': 0.0,
        'gdd_end': 100.0,
        'description': 'Seed germination phase',
        'description_ar': 'مرحلة إنبات البذور',
        'is_completed': false,
      };

      final stage = GrowthStage.fromJson(json);
      expect(stage.stageId, 'germination');
      expect(stage.stageName, 'Germination');
      expect(stage.stageNameAr, 'الإنبات');
      expect(stage.stageNumber, 1);
      expect(stage.gddRequired, 100.0);
      expect(stage.isCompleted, false);

      final exported = stage.toJson();
      expect(exported['stage_id'], 'germination');
      expect(exported['gdd_required'], 100.0);
    });

    test('getName returns Arabic when available', () {
      const stage = GrowthStage(
        stageId: 's1',
        stageName: 'Tillering',
        stageNameAr: 'التفريع',
        stageNumber: 2,
        gddRequired: 200.0,
        gddStart: 100.0,
        gddEnd: 300.0,
      );
      expect(stage.getName('ar'), 'التفريع');
      expect(stage.getName('en'), 'Tillering');
    });

    test('getName falls back to English when Arabic is null', () {
      const stage = GrowthStage(
        stageId: 's1',
        stageName: 'Heading',
        stageNumber: 3,
        gddRequired: 300.0,
        gddStart: 300.0,
        gddEnd: 600.0,
      );
      expect(stage.getName('ar'), 'Heading');
    });

    test('copyWith creates modified copy', () {
      const stage = GrowthStage(
        stageId: 's1',
        stageName: 'Test',
        stageNumber: 1,
        gddRequired: 100.0,
        gddStart: 0.0,
        gddEnd: 100.0,
      );

      final completed = stage.copyWith(isCompleted: true);
      expect(completed.isCompleted, true);
      expect(completed.stageId, 's1');
    });
  });

  group('GDDRecord', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'record_id': 'rec-001',
        'field_id': 'field-001',
        'date': '2026-01-15T00:00:00.000',
        't_min': 5.0,
        't_max': 22.0,
        't_avg': 13.5,
        'gdd_value': 8.5,
        'accumulated_gdd': 150.0,
        'calculation_method': 'average',
        'base_temperature': 5.0,
        'upper_threshold': 30.0,
        'source': 'weather_station',
        'created_at': '2026-01-15T12:00:00.000',
      };

      final record = GDDRecord.fromJson(json);
      expect(record.recordId, 'rec-001');
      expect(record.fieldId, 'field-001');
      expect(record.tMin, 5.0);
      expect(record.tMax, 22.0);
      expect(record.tAvg, 13.5);
      expect(record.gddValue, 8.5);
      expect(record.accumulatedGDD, 150.0);
      expect(record.calculationMethod, GDDCalculationMethod.average);
      expect(record.baseTemperature, 5.0);

      final exported = record.toJson();
      expect(exported['record_id'], 'rec-001');
      expect(exported['gdd_value'], 8.5);
      expect(exported['calculation_method'], 'average');
    });
  });

  group('GDDAccumulation', () {
    test('isActiveGrowth returns true when currentStage is set', () {
      final acc = GDDAccumulation(
        fieldId: 'f1',
        startDate: DateTime(2026, 1, 1),
        totalGDD: 250.0,
        baseTemperature: 5.0,
        calculationMethod: GDDCalculationMethod.average,
        daysCount: 30,
        averageGDDPerDay: 8.3,
        currentStage: const GrowthStage(
          stageId: 's2',
          stageName: 'Tillering',
          stageNumber: 2,
          gddRequired: 200.0,
          gddStart: 100.0,
          gddEnd: 300.0,
        ),
        recentRecords: [],
        calculatedAt: DateTime(2026, 1, 31),
      );
      expect(acc.isActiveGrowth, true);
    });

    test('currentStageProgress calculates percentage', () {
      final acc = GDDAccumulation(
        fieldId: 'f1',
        startDate: DateTime(2026, 1, 1),
        totalGDD: 200.0, // midway through stage (100-300)
        baseTemperature: 5.0,
        calculationMethod: GDDCalculationMethod.average,
        daysCount: 20,
        averageGDDPerDay: 10.0,
        currentStage: const GrowthStage(
          stageId: 's2',
          stageName: 'Tillering',
          stageNumber: 2,
          gddRequired: 200.0,
          gddStart: 100.0,
          gddEnd: 300.0,
        ),
        recentRecords: [],
        calculatedAt: DateTime(2026, 1, 21),
      );
      // (200 - 100) / (300 - 100) = 0.5
      expect(acc.currentStageProgress, 0.5);
    });

    test('gddToNextStage calculates remaining GDD', () {
      final acc = GDDAccumulation(
        fieldId: 'f1',
        startDate: DateTime(2026, 1, 1),
        totalGDD: 250.0,
        baseTemperature: 5.0,
        calculationMethod: GDDCalculationMethod.average,
        daysCount: 25,
        averageGDDPerDay: 10.0,
        nextStage: const GrowthStage(
          stageId: 's3',
          stageName: 'Heading',
          stageNumber: 3,
          gddRequired: 300.0,
          gddStart: 300.0,
          gddEnd: 500.0,
        ),
        recentRecords: [],
        calculatedAt: DateTime(2026, 1, 26),
      );
      // nextStage.gddStart - totalGDD = 300 - 250 = 50
      expect(acc.gddToNextStage, 50.0);
    });

    test('gddToNextStage returns null when no next stage', () {
      final acc = GDDAccumulation(
        fieldId: 'f1',
        startDate: DateTime(2026, 1, 1),
        totalGDD: 1000.0,
        baseTemperature: 5.0,
        calculationMethod: GDDCalculationMethod.average,
        daysCount: 100,
        averageGDDPerDay: 10.0,
        recentRecords: [],
        calculatedAt: DateTime(2026, 4, 10),
      );
      expect(acc.gddToNextStage, isNull);
    });

    test('fromJson and toJson round-trip', () {
      final json = {
        'field_id': 'field-001',
        'field_name': 'حقل القمح',
        'crop_type': 'wheat',
        'start_date': '2026-01-01T00:00:00.000',
        'total_gdd': 350.0,
        'base_temperature': 5.0,
        'calculation_method': 'average',
        'days_count': 40,
        'average_gdd_per_day': 8.75,
        'recent_records': [],
        'calculated_at': '2026-02-10T00:00:00.000',
      };

      final acc = GDDAccumulation.fromJson(json);
      expect(acc.fieldId, 'field-001');
      expect(acc.fieldName, 'حقل القمح');
      expect(acc.cropType, CropType.wheat);
      expect(acc.totalGDD, 350.0);

      final exported = acc.toJson();
      expect(exported['field_id'], 'field-001');
      expect(exported['crop_type'], 'wheat');
    });
  });

  group('GDDForecast', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'field_id': 'f1',
        'forecast_date': '2026-02-01T00:00:00.000',
        'forecast_gdd': 12.5,
        'cumulative_gdd': 362.5,
        't_min_forecast': 8.0,
        't_max_forecast': 25.0,
        'confidence': 0.85,
        'source': 'weather_api',
      };

      final forecast = GDDForecast.fromJson(json);
      expect(forecast.forecastGDD, 12.5);
      expect(forecast.confidence, 0.85);

      final exported = forecast.toJson();
      expect(exported['forecast_gdd'], 12.5);
    });
  });

  group('GDDSettings', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'field_id': 'f1',
        'crop_type': 'wheat',
        'base_temperature': 5.0,
        'upper_threshold': 30.0,
        'calculation_method': 'average',
        'planting_date': '2026-01-01T00:00:00.000',
        'auto_calculate': true,
      };

      final settings = GDDSettings.fromJson(json);
      expect(settings.cropType, CropType.wheat);
      expect(settings.baseTemperature, 5.0);
      expect(settings.autoCalculate, true);

      final exported = settings.toJson();
      expect(exported['crop_type'], 'wheat');
    });

    test('copyWith creates modified copy', () {
      final settings = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.wheat,
        baseTemperature: 5.0,
        upperThreshold: 30.0,
        calculationMethod: GDDCalculationMethod.average,
        plantingDate: DateTime(2026, 1, 1),
      );

      final modified = settings.copyWith(
        cropType: CropType.tomato,
        baseTemperature: 10.0,
      );

      expect(modified.cropType, CropType.tomato);
      expect(modified.baseTemperature, 10.0);
      expect(modified.fieldId, 'f1'); // unchanged
    });
  });
}
