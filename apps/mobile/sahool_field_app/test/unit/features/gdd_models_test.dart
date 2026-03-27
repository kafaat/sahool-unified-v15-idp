import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/gdd/models/gdd_models.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // CropType enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('CropType', () {
    test('has exactly 10 values', () {
      expect(CropType.values.length, 10);
    });

    test('wheat has correct properties', () {
      expect(CropType.wheat.value, 'wheat');
      expect(CropType.wheat.nameAr, 'قمح');
      expect(CropType.wheat.nameEn, 'Wheat');
    });

    test('corn has correct properties', () {
      expect(CropType.corn.value, 'corn');
      expect(CropType.corn.nameAr, 'ذرة');
      expect(CropType.corn.nameEn, 'Corn');
    });

    test('coffee has correct properties', () {
      expect(CropType.coffee.value, 'coffee');
      expect(CropType.coffee.nameAr, 'بن');
      expect(CropType.coffee.nameEn, 'Coffee');
    });

    test('sorghum has correct properties', () {
      expect(CropType.sorghum.value, 'sorghum');
      expect(CropType.sorghum.nameAr, 'ذرة رفيعة');
      expect(CropType.sorghum.nameEn, 'Sorghum');
    });

    test('potato has correct properties', () {
      expect(CropType.potato.value, 'potato');
      expect(CropType.potato.nameAr, 'بطاطس');
      expect(CropType.potato.nameEn, 'Potato');
    });

    test('onion has correct properties', () {
      expect(CropType.onion.value, 'onion');
      expect(CropType.onion.nameAr, 'بصل');
      expect(CropType.onion.nameEn, 'Onion');
    });

    test('cotton has correct properties', () {
      expect(CropType.cotton.value, 'cotton');
      expect(CropType.cotton.nameAr, 'قطن');
      expect(CropType.cotton.nameEn, 'Cotton');
    });

    test('sesame has correct properties', () {
      expect(CropType.sesame.value, 'sesame');
      expect(CropType.sesame.nameAr, 'سمسم');
      expect(CropType.sesame.nameEn, 'Sesame');
    });

    test('millet has correct properties', () {
      expect(CropType.millet.value, 'millet');
      expect(CropType.millet.nameAr, 'دخن');
      expect(CropType.millet.nameEn, 'Millet');
    });

    test('tomato has correct properties', () {
      expect(CropType.tomato.value, 'tomato');
      expect(CropType.tomato.nameAr, 'طماطم');
      expect(CropType.tomato.nameEn, 'Tomato');
    });

    test('getName returns Arabic name for ar locale', () {
      expect(CropType.wheat.getName('ar'), 'قمح');
      expect(CropType.corn.getName('ar'), 'ذرة');
    });

    test('getName returns English name for en locale', () {
      expect(CropType.wheat.getName('en'), 'Wheat');
      expect(CropType.corn.getName('en'), 'Corn');
    });

    test('getName returns English for unknown locale', () {
      expect(CropType.tomato.getName('fr'), 'Tomato');
    });

    test('fromString returns correct CropType for each value', () {
      expect(CropType.fromString('wheat'), CropType.wheat);
      expect(CropType.fromString('corn'), CropType.corn);
      expect(CropType.fromString('tomato'), CropType.tomato);
      expect(CropType.fromString('coffee'), CropType.coffee);
      expect(CropType.fromString('sorghum'), CropType.sorghum);
      expect(CropType.fromString('potato'), CropType.potato);
      expect(CropType.fromString('onion'), CropType.onion);
      expect(CropType.fromString('cotton'), CropType.cotton);
      expect(CropType.fromString('sesame'), CropType.sesame);
      expect(CropType.fromString('millet'), CropType.millet);
    });

    test('fromString returns wheat for unknown value', () {
      expect(CropType.fromString('unknown'), CropType.wheat);
      expect(CropType.fromString(''), CropType.wheat);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GDDCalculationMethod enum
  // ═══════════════════════════════════════════════════════════════════════════
  group('GDDCalculationMethod', () {
    test('has exactly 3 values', () {
      expect(GDDCalculationMethod.values.length, 3);
    });

    test('average has correct properties', () {
      expect(GDDCalculationMethod.average.value, 'average');
      expect(GDDCalculationMethod.average.nameAr, 'متوسط');
      expect(GDDCalculationMethod.average.nameEn, 'Average Method');
    });

    test('sine has correct properties', () {
      expect(GDDCalculationMethod.sine.value, 'sine');
      expect(GDDCalculationMethod.sine.nameAr, 'موجة جيبية');
      expect(GDDCalculationMethod.sine.nameEn, 'Sine Wave Method');
    });

    test('modifiedAverage has correct properties', () {
      expect(GDDCalculationMethod.modifiedAverage.value, 'modified_average');
      expect(GDDCalculationMethod.modifiedAverage.nameAr, 'متوسط معدل');
      expect(GDDCalculationMethod.modifiedAverage.nameEn, 'Modified Average');
    });

    test('getName returns Arabic for ar locale', () {
      expect(GDDCalculationMethod.sine.getName('ar'), 'موجة جيبية');
    });

    test('getName returns English for en locale', () {
      expect(GDDCalculationMethod.sine.getName('en'), 'Sine Wave Method');
    });

    test('fromString returns correct method', () {
      expect(GDDCalculationMethod.fromString('average'),
          GDDCalculationMethod.average);
      expect(
          GDDCalculationMethod.fromString('sine'), GDDCalculationMethod.sine);
      expect(GDDCalculationMethod.fromString('modified_average'),
          GDDCalculationMethod.modifiedAverage);
    });

    test('fromString returns average for unknown value', () {
      expect(GDDCalculationMethod.fromString('unknown'),
          GDDCalculationMethod.average);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GrowthStage
  // ═══════════════════════════════════════════════════════════════════════════
  group('GrowthStage', () {
    GrowthStage makeStage({
      String stageId = 'stage-1',
      String stageName = 'Germination',
      String? stageNameAr = 'إنبات',
      int stageNumber = 1,
      double gddRequired = 100.0,
      double gddStart = 0.0,
      double gddEnd = 100.0,
      String? description = 'Seed germination phase',
      String? descriptionAr = 'مرحلة إنبات البذور',
      String? icon = 'seedling',
      bool isCompleted = false,
    }) {
      return GrowthStage(
        stageId: stageId,
        stageName: stageName,
        stageNameAr: stageNameAr,
        stageNumber: stageNumber,
        gddRequired: gddRequired,
        gddStart: gddStart,
        gddEnd: gddEnd,
        description: description,
        descriptionAr: descriptionAr,
        icon: icon,
        isCompleted: isCompleted,
      );
    }

    test('properties are assigned correctly', () {
      final stage = makeStage();
      expect(stage.stageId, 'stage-1');
      expect(stage.stageName, 'Germination');
      expect(stage.stageNameAr, 'إنبات');
      expect(stage.stageNumber, 1);
      expect(stage.gddRequired, 100.0);
      expect(stage.gddStart, 0.0);
      expect(stage.gddEnd, 100.0);
      expect(stage.description, 'Seed germination phase');
      expect(stage.descriptionAr, 'مرحلة إنبات البذور');
      expect(stage.icon, 'seedling');
      expect(stage.isCompleted, false);
    });

    test('isCompleted defaults to false', () {
      const s = GrowthStage(
        stageId: 's',
        stageName: 'S',
        stageNumber: 1,
        gddRequired: 50,
        gddStart: 0,
        gddEnd: 50,
      );
      expect(s.isCompleted, false);
    });

    test('getName returns Arabic when stageNameAr is set', () {
      final stage = makeStage();
      expect(stage.getName('ar'), 'إنبات');
    });

    test('getName returns English for en locale', () {
      final stage = makeStage();
      expect(stage.getName('en'), 'Germination');
    });

    test('getName returns English when stageNameAr is null', () {
      final stage = makeStage(stageNameAr: null);
      expect(stage.getName('ar'), 'Germination');
    });

    test('getDescription returns Arabic when descriptionAr is set', () {
      final stage = makeStage();
      expect(stage.getDescription('ar'), 'مرحلة إنبات البذور');
    });

    test('getDescription returns English for en locale', () {
      final stage = makeStage();
      expect(stage.getDescription('en'), 'Seed germination phase');
    });

    test('getDescription returns English when descriptionAr is null', () {
      final stage = makeStage(descriptionAr: null);
      expect(stage.getDescription('ar'), 'Seed germination phase');
    });

    test('getDescription returns null when both descriptions are null', () {
      final stage = makeStage(description: null, descriptionAr: null);
      expect(stage.getDescription('en'), isNull);
      expect(stage.getDescription('ar'), isNull);
    });

    test('fromJson creates correct instance with all fields', () {
      final json = {
        'stage_id': 'stg-1',
        'stage_name': 'Flowering',
        'stage_name_ar': 'إزهار',
        'stage_number': 3,
        'gdd_required': 500.0,
        'gdd_start': 300.0,
        'gdd_end': 800.0,
        'description': 'Flowering stage',
        'description_ar': 'مرحلة الإزهار',
        'icon': 'flower',
        'is_completed': true,
      };
      final s = GrowthStage.fromJson(json);
      expect(s.stageId, 'stg-1');
      expect(s.stageName, 'Flowering');
      expect(s.stageNameAr, 'إزهار');
      expect(s.stageNumber, 3);
      expect(s.gddRequired, 500.0);
      expect(s.gddStart, 300.0);
      expect(s.gddEnd, 800.0);
      expect(s.isCompleted, true);
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'stage_id': 'stg-2',
        'stage_name': 'Harvest',
        'stage_number': 5,
        'gdd_required': 1000.0,
        'gdd_start': 800.0,
        'gdd_end': 1000.0,
      };
      final s = GrowthStage.fromJson(json);
      expect(s.stageNameAr, isNull);
      expect(s.description, isNull);
      expect(s.descriptionAr, isNull);
      expect(s.icon, isNull);
      expect(s.isCompleted, false);
    });

    test('fromJson handles integer numeric values', () {
      final json = {
        'stage_id': 'stg-3',
        'stage_name': 'X',
        'stage_number': 1,
        'gdd_required': 100,
        'gdd_start': 0,
        'gdd_end': 100,
      };
      final s = GrowthStage.fromJson(json);
      expect(s.gddRequired, 100.0);
      expect(s.gddStart, 0.0);
      expect(s.gddEnd, 100.0);
    });

    test('toJson produces correct map', () {
      final stage = makeStage();
      final json = stage.toJson();
      expect(json['stage_id'], 'stage-1');
      expect(json['stage_name'], 'Germination');
      expect(json['stage_name_ar'], 'إنبات');
      expect(json['stage_number'], 1);
      expect(json['gdd_required'], 100.0);
      expect(json['gdd_start'], 0.0);
      expect(json['gdd_end'], 100.0);
      expect(json['description'], 'Seed germination phase');
      expect(json['description_ar'], 'مرحلة إنبات البذور');
      expect(json['icon'], 'seedling');
      expect(json['is_completed'], false);
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final stage = makeStage();
      final json = stage.toJson();
      final restored = GrowthStage.fromJson(json);
      expect(restored.stageId, stage.stageId);
      expect(restored.stageName, stage.stageName);
      expect(restored.stageNumber, stage.stageNumber);
      expect(restored.gddRequired, stage.gddRequired);
      expect(restored.isCompleted, stage.isCompleted);
    });

    test('copyWith no changes returns equivalent object', () {
      final stage = makeStage();
      final copy = stage.copyWith();
      expect(copy.stageId, stage.stageId);
      expect(copy.stageName, stage.stageName);
      expect(copy.stageNumber, stage.stageNumber);
      expect(copy.gddRequired, stage.gddRequired);
      expect(copy.isCompleted, stage.isCompleted);
      expect(copy.icon, stage.icon);
    });

    test('copyWith changes specific fields only', () {
      final stage = makeStage();
      final copy = stage.copyWith(
        stageId: 'new-id',
        isCompleted: true,
        gddRequired: 200.0,
      );
      expect(copy.stageId, 'new-id');
      expect(copy.isCompleted, true);
      expect(copy.gddRequired, 200.0);
      expect(copy.stageName, 'Germination');
    });

    test('copyWith can change stageNameAr', () {
      final stage = makeStage();
      final copy = stage.copyWith(stageNameAr: 'اسم جديد');
      expect(copy.stageNameAr, 'اسم جديد');
    });

    test('copyWith can change description fields', () {
      final stage = makeStage();
      final copy = stage.copyWith(
        description: 'new desc',
        descriptionAr: 'وصف جديد',
      );
      expect(copy.description, 'new desc');
      expect(copy.descriptionAr, 'وصف جديد');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // CropGDDRequirements
  // ═══════════════════════════════════════════════════════════════════════════
  group('CropGDDRequirements', () {
    test('fromJson creates instance with nested growth stages', () {
      final json = {
        'crop_type': 'wheat',
        'crop_name': 'Wheat',
        'crop_name_ar': 'قمح',
        'base_temperature': 5.0,
        'upper_threshold': 35.0,
        'total_gdd_required': 2000.0,
        'growth_stages': [
          {
            'stage_id': 's1',
            'stage_name': 'Germination',
            'stage_number': 1,
            'gdd_required': 100.0,
            'gdd_start': 0.0,
            'gdd_end': 100.0,
          },
          {
            'stage_id': 's2',
            'stage_name': 'Tillering',
            'stage_number': 2,
            'gdd_required': 400.0,
            'gdd_start': 100.0,
            'gdd_end': 500.0,
          },
        ],
        'metadata': {'region': 'yemen'},
      };
      final req = CropGDDRequirements.fromJson(json);
      expect(req.cropType, 'wheat');
      expect(req.cropName, 'Wheat');
      expect(req.cropNameAr, 'قمح');
      expect(req.baseTemperature, 5.0);
      expect(req.upperThreshold, 35.0);
      expect(req.totalGDDRequired, 2000.0);
      expect(req.growthStages.length, 2);
      expect(req.growthStages[0].stageId, 's1');
      expect(req.growthStages[1].stageName, 'Tillering');
      expect(req.metadata?['region'], 'yemen');
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'crop_type': 'corn',
        'crop_name': 'Corn',
        'base_temperature': 10,
        'upper_threshold': 30,
        'total_gdd_required': 2500,
        'growth_stages': <Map<String, dynamic>>[],
      };
      final req = CropGDDRequirements.fromJson(json);
      expect(req.cropNameAr, isNull);
      expect(req.metadata, isNull);
      expect(req.growthStages, isEmpty);
    });

    test('fromJson handles integer numeric values', () {
      final json = {
        'crop_type': 'corn',
        'crop_name': 'Corn',
        'base_temperature': 10,
        'upper_threshold': 30,
        'total_gdd_required': 2500,
        'growth_stages': <Map<String, dynamic>>[],
      };
      final req = CropGDDRequirements.fromJson(json);
      expect(req.baseTemperature, 10.0);
      expect(req.upperThreshold, 30.0);
      expect(req.totalGDDRequired, 2500.0);
    });

    test('getName returns Arabic when cropNameAr is set', () {
      const req = CropGDDRequirements(
        cropType: 'wheat',
        cropName: 'Wheat',
        cropNameAr: 'قمح',
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        totalGDDRequired: 2000.0,
        growthStages: [],
      );
      expect(req.getName('ar'), 'قمح');
      expect(req.getName('en'), 'Wheat');
    });

    test('getName returns English when cropNameAr is null', () {
      const req = CropGDDRequirements(
        cropType: 'wheat',
        cropName: 'Wheat',
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        totalGDDRequired: 2000.0,
        growthStages: [],
      );
      expect(req.getName('ar'), 'Wheat');
    });

    test('toJson produces correct map with empty stages', () {
      const req = CropGDDRequirements(
        cropType: 'tomato',
        cropName: 'Tomato',
        cropNameAr: 'طماطم',
        baseTemperature: 10.0,
        upperThreshold: 32.0,
        totalGDDRequired: 1500.0,
        growthStages: [],
      );
      final json = req.toJson();
      expect(json['crop_type'], 'tomato');
      expect(json['crop_name'], 'Tomato');
      expect(json['crop_name_ar'], 'طماطم');
      expect(json['base_temperature'], 10.0);
      expect(json['growth_stages'], isEmpty);
      expect(json['metadata'], isNull);
    });

    test('fromJson/toJson roundtrip with stages', () {
      final json = {
        'crop_type': 'wheat',
        'crop_name': 'Wheat',
        'crop_name_ar': 'قمح',
        'base_temperature': 5.0,
        'upper_threshold': 35.0,
        'total_gdd_required': 2000.0,
        'growth_stages': [
          {
            'stage_id': 's1',
            'stage_name': 'Germination',
            'stage_number': 1,
            'gdd_required': 100.0,
            'gdd_start': 0.0,
            'gdd_end': 100.0,
          },
        ],
      };
      final req = CropGDDRequirements.fromJson(json);
      final output = req.toJson();
      final restored = CropGDDRequirements.fromJson(output);
      expect(restored.cropType, req.cropType);
      expect(restored.growthStages.length, 1);
      expect(restored.growthStages[0].stageId, 's1');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GDDRecord
  // ═══════════════════════════════════════════════════════════════════════════
  group('GDDRecord', () {
    Map<String, dynamic> makeSampleJson() => {
          'record_id': 'rec-001',
          'field_id': 'fld-001',
          'date': '2025-06-15',
          't_min': 18.5,
          't_max': 32.0,
          't_avg': 25.25,
          'gdd_value': 15.25,
          'accumulated_gdd': 450.5,
          'calculation_method': 'average',
          'base_temperature': 10.0,
          'upper_threshold': 35.0,
          'source': 'weather_station',
          'created_at': '2025-06-15T12:00:00.000Z',
        };

    test('fromJson creates correct instance with all fields', () {
      final rec = GDDRecord.fromJson(makeSampleJson());
      expect(rec.recordId, 'rec-001');
      expect(rec.fieldId, 'fld-001');
      expect(rec.tMin, 18.5);
      expect(rec.tMax, 32.0);
      expect(rec.tAvg, 25.25);
      expect(rec.gddValue, 15.25);
      expect(rec.accumulatedGDD, 450.5);
      expect(rec.calculationMethod, GDDCalculationMethod.average);
      expect(rec.baseTemperature, 10.0);
      expect(rec.upperThreshold, 35.0);
      expect(rec.source, 'weather_station');
    });

    test('fromJson handles missing optional fields', () {
      final json = makeSampleJson();
      json.remove('upper_threshold');
      json.remove('source');
      final rec = GDDRecord.fromJson(json);
      expect(rec.upperThreshold, isNull);
      expect(rec.source, isNull);
    });

    test('fromJson parses sine calculation method', () {
      final json = makeSampleJson();
      json['calculation_method'] = 'sine';
      final rec = GDDRecord.fromJson(json);
      expect(rec.calculationMethod, GDDCalculationMethod.sine);
    });

    test('fromJson parses modified_average calculation method', () {
      final json = makeSampleJson();
      json['calculation_method'] = 'modified_average';
      final rec = GDDRecord.fromJson(json);
      expect(rec.calculationMethod, GDDCalculationMethod.modifiedAverage);
    });

    test('toJson produces correct map', () {
      final rec = GDDRecord.fromJson(makeSampleJson());
      final json = rec.toJson();
      expect(json['record_id'], 'rec-001');
      expect(json['field_id'], 'fld-001');
      expect(json['t_min'], 18.5);
      expect(json['t_max'], 32.0);
      expect(json['calculation_method'], 'average');
      expect(json['source'], 'weather_station');
    });

    test('toJson serializes dates as ISO 8601 strings', () {
      final rec = GDDRecord.fromJson(makeSampleJson());
      final json = rec.toJson();
      expect(json['date'], isA<String>());
      expect(json['created_at'], isA<String>());
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final rec = GDDRecord.fromJson(makeSampleJson());
      final output = rec.toJson();
      final restored = GDDRecord.fromJson(output);
      expect(restored.recordId, rec.recordId);
      expect(restored.gddValue, rec.gddValue);
      expect(restored.accumulatedGDD, rec.accumulatedGDD);
      expect(restored.calculationMethod, rec.calculationMethod);
      expect(restored.source, rec.source);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GDDAccumulation
  // ═══════════════════════════════════════════════════════════════════════════
  group('GDDAccumulation', () {
    final now = DateTime.utc(2025, 6, 1);

    Map<String, dynamic> stageJson(
        String id, String name, int num, double req, double start, double end) {
      return {
        'stage_id': id,
        'stage_name': name,
        'stage_number': num,
        'gdd_required': req,
        'gdd_start': start,
        'gdd_end': end,
      };
    }

    GDDAccumulation makeAccumulation({
      double totalGDD = 200.0,
      GrowthStage? currentStage,
      GrowthStage? nextStage,
    }) {
      return GDDAccumulation(
        fieldId: 'f1',
        startDate: now,
        totalGDD: totalGDD,
        baseTemperature: 10.0,
        calculationMethod: GDDCalculationMethod.average,
        daysCount: 30,
        averageGDDPerDay: 5.0,
        currentStage: currentStage,
        nextStage: nextStage,
        recentRecords: const [],
        calculatedAt: now,
      );
    }

    test('isActiveGrowth returns true when currentStage is set', () {
      final acc = makeAccumulation(
        currentStage: const GrowthStage(
          stageId: 's1',
          stageName: 'Tillering',
          stageNumber: 2,
          gddRequired: 200,
          gddStart: 100,
          gddEnd: 300,
        ),
      );
      expect(acc.isActiveGrowth, true);
    });

    test('isActiveGrowth returns false when currentStage is null', () {
      final acc = makeAccumulation();
      expect(acc.isActiveGrowth, false);
    });

    test('currentStageProgress returns null when no currentStage', () {
      final acc = makeAccumulation();
      expect(acc.currentStageProgress, isNull);
    });

    test('currentStageProgress calculates correctly at mid-stage', () {
      final acc = makeAccumulation(
        totalGDD: 200.0,
        currentStage: const GrowthStage(
          stageId: 's2',
          stageName: 'Tillering',
          stageNumber: 2,
          gddRequired: 200,
          gddStart: 100,
          gddEnd: 300,
        ),
      );
      // stageGDD = 200 - 100 = 100; stageRange = 300 - 100 = 200; 100/200 = 0.5
      expect(acc.currentStageProgress, 0.5);
    });

    test('currentStageProgress clamps to 1.0 when beyond stage end', () {
      final acc = makeAccumulation(
        totalGDD: 500.0,
        currentStage: const GrowthStage(
          stageId: 's2',
          stageName: 'Tillering',
          stageNumber: 2,
          gddRequired: 200,
          gddStart: 100,
          gddEnd: 300,
        ),
      );
      expect(acc.currentStageProgress, 1.0);
    });

    test('currentStageProgress clamps to 0.0 when below stage start', () {
      final acc = makeAccumulation(
        totalGDD: 50.0,
        currentStage: const GrowthStage(
          stageId: 's2',
          stageName: 'Tillering',
          stageNumber: 2,
          gddRequired: 200,
          gddStart: 100,
          gddEnd: 300,
        ),
      );
      expect(acc.currentStageProgress, 0.0);
    });

    test('currentStageProgress returns 0 when stageRange is zero', () {
      final acc = makeAccumulation(
        totalGDD: 100.0,
        currentStage: const GrowthStage(
          stageId: 's1',
          stageName: 'Point',
          stageNumber: 1,
          gddRequired: 0,
          gddStart: 100,
          gddEnd: 100,
        ),
      );
      expect(acc.currentStageProgress, 0);
    });

    test('gddToNextStage returns null when nextStage is null', () {
      final acc = makeAccumulation();
      expect(acc.gddToNextStage, isNull);
    });

    test('gddToNextStage calculates remaining GDD correctly', () {
      final acc = makeAccumulation(
        totalGDD: 200.0,
        nextStage: const GrowthStage(
          stageId: 's3',
          stageName: 'Heading',
          stageNumber: 3,
          gddRequired: 300,
          gddStart: 300,
          gddEnd: 500,
        ),
      );
      expect(acc.gddToNextStage, 100.0);
    });

    test('gddToNextStage clamps to 0 when past next stage start', () {
      final acc = makeAccumulation(
        totalGDD: 400.0,
        nextStage: const GrowthStage(
          stageId: 's3',
          stageName: 'Heading',
          stageNumber: 3,
          gddRequired: 300,
          gddStart: 300,
          gddEnd: 500,
        ),
      );
      expect(acc.gddToNextStage, 0.0);
    });

    test('fromJson creates correct instance with all fields', () {
      final json = {
        'field_id': 'f1',
        'field_name': 'Field 1',
        'crop_type': 'wheat',
        'start_date': '2025-01-01T00:00:00.000Z',
        'end_date': '2025-06-01T00:00:00.000Z',
        'total_gdd': 450.0,
        'base_temperature': 5.0,
        'upper_threshold': 35.0,
        'calculation_method': 'average',
        'days_count': 150,
        'average_gdd_per_day': 3.0,
        'current_stage': stageJson('s1', 'Tillering', 2, 200, 100, 300),
        'next_stage': stageJson('s2', 'Heading', 3, 300, 300, 500),
        'progress_percent': 75.0,
        'days_to_next_stage': 15,
        'recent_records': <Map<String, dynamic>>[],
        'calculated_at': '2025-06-01T12:00:00.000Z',
      };
      final acc = GDDAccumulation.fromJson(json);
      expect(acc.fieldId, 'f1');
      expect(acc.fieldName, 'Field 1');
      expect(acc.cropType, CropType.wheat);
      expect(acc.totalGDD, 450.0);
      expect(acc.daysCount, 150);
      expect(acc.currentStage, isNotNull);
      expect(acc.nextStage, isNotNull);
      expect(acc.progressPercent, 75.0);
      expect(acc.daysToNextStage, 15);
      expect(acc.endDate, isNotNull);
      expect(acc.upperThreshold, 35.0);
    });

    test('fromJson handles null optional fields', () {
      final json = {
        'field_id': 'f1',
        'start_date': '2025-01-01T00:00:00.000Z',
        'total_gdd': 100.0,
        'base_temperature': 10.0,
        'calculation_method': 'sine',
        'days_count': 20,
        'average_gdd_per_day': 5.0,
        'calculated_at': '2025-01-21T00:00:00.000Z',
      };
      final acc = GDDAccumulation.fromJson(json);
      expect(acc.fieldName, isNull);
      expect(acc.cropType, isNull);
      expect(acc.endDate, isNull);
      expect(acc.upperThreshold, isNull);
      expect(acc.currentStage, isNull);
      expect(acc.nextStage, isNull);
      expect(acc.progressPercent, isNull);
      expect(acc.daysToNextStage, isNull);
      expect(acc.recentRecords, isEmpty);
    });

    test('toJson produces correct map', () {
      final acc = GDDAccumulation(
        fieldId: 'f1',
        fieldName: 'Test Field',
        cropType: CropType.corn,
        startDate: now,
        totalGDD: 200.0,
        baseTemperature: 10.0,
        calculationMethod: GDDCalculationMethod.sine,
        daysCount: 40,
        averageGDDPerDay: 5.0,
        recentRecords: const [],
        calculatedAt: now,
      );
      final json = acc.toJson();
      expect(json['field_id'], 'f1');
      expect(json['field_name'], 'Test Field');
      expect(json['crop_type'], 'corn');
      expect(json['total_gdd'], 200.0);
      expect(json['calculation_method'], 'sine');
      expect(json['recent_records'], isEmpty);
    });

    test('toJson handles null crop_type', () {
      final acc = makeAccumulation();
      final json = acc.toJson();
      expect(json['crop_type'], isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GDDForecast
  // ═══════════════════════════════════════════════════════════════════════════
  group('GDDForecast', () {
    test('fromJson creates correct instance', () {
      final json = {
        'field_id': 'f1',
        'forecast_date': '2025-06-20T00:00:00.000Z',
        'forecast_gdd': 12.5,
        'cumulative_gdd': 463.0,
        't_min_forecast': 20.0,
        't_max_forecast': 35.0,
        'confidence': 0.85,
        'source': 'weather_api',
      };
      final f = GDDForecast.fromJson(json);
      expect(f.fieldId, 'f1');
      expect(f.forecastGDD, 12.5);
      expect(f.cumulativeGDD, 463.0);
      expect(f.tMinForecast, 20.0);
      expect(f.tMaxForecast, 35.0);
      expect(f.confidence, 0.85);
      expect(f.source, 'weather_api');
    });

    test('fromJson handles null source', () {
      final json = {
        'field_id': 'f1',
        'forecast_date': '2025-06-20T00:00:00.000Z',
        'forecast_gdd': 10.0,
        'cumulative_gdd': 400.0,
        't_min_forecast': 18.0,
        't_max_forecast': 30.0,
        'confidence': 0.7,
      };
      final f = GDDForecast.fromJson(json);
      expect(f.source, isNull);
    });

    test('fromJson handles integer numeric values', () {
      final json = {
        'field_id': 'f1',
        'forecast_date': '2025-06-20T00:00:00.000Z',
        'forecast_gdd': 10,
        'cumulative_gdd': 400,
        't_min_forecast': 18,
        't_max_forecast': 30,
        'confidence': 1,
      };
      final f = GDDForecast.fromJson(json);
      expect(f.forecastGDD, 10.0);
      expect(f.confidence, 1.0);
    });

    test('toJson produces correct map', () {
      final f = GDDForecast(
        fieldId: 'f2',
        forecastDate: DateTime.utc(2025, 7, 1),
        forecastGDD: 8.0,
        cumulativeGDD: 500.0,
        tMinForecast: 22.0,
        tMaxForecast: 38.0,
        confidence: 0.9,
        source: 'model_v2',
      );
      final json = f.toJson();
      expect(json['field_id'], 'f2');
      expect(json['forecast_gdd'], 8.0);
      expect(json['cumulative_gdd'], 500.0);
      expect(json['confidence'], 0.9);
      expect(json['source'], 'model_v2');
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final json = {
        'field_id': 'f1',
        'forecast_date': '2025-06-20T00:00:00.000Z',
        'forecast_gdd': 12.5,
        'cumulative_gdd': 463.0,
        't_min_forecast': 20.0,
        't_max_forecast': 35.0,
        'confidence': 0.85,
        'source': 'test',
      };
      final f = GDDForecast.fromJson(json);
      final output = f.toJson();
      final restored = GDDForecast.fromJson(output);
      expect(restored.fieldId, f.fieldId);
      expect(restored.forecastGDD, f.forecastGDD);
      expect(restored.confidence, f.confidence);
      expect(restored.source, f.source);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GDDSettings
  // ═══════════════════════════════════════════════════════════════════════════
  group('GDDSettings', () {
    test('fromJson creates correct instance with all fields', () {
      final json = {
        'field_id': 'f1',
        'crop_type': 'wheat',
        'base_temperature': 5.0,
        'upper_threshold': 35.0,
        'calculation_method': 'average',
        'planting_date': '2025-01-15T00:00:00.000Z',
        'harvest_date': '2025-06-15T00:00:00.000Z',
        'auto_calculate': true,
        'metadata': {'variety': 'Sakha95'},
      };
      final s = GDDSettings.fromJson(json);
      expect(s.fieldId, 'f1');
      expect(s.cropType, CropType.wheat);
      expect(s.baseTemperature, 5.0);
      expect(s.upperThreshold, 35.0);
      expect(s.calculationMethod, GDDCalculationMethod.average);
      expect(s.autoCalculate, true);
      expect(s.harvestDate, isNotNull);
      expect(s.metadata?['variety'], 'Sakha95');
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'field_id': 'f2',
        'crop_type': 'corn',
        'base_temperature': 10.0,
        'upper_threshold': 30.0,
        'calculation_method': 'sine',
        'planting_date': '2025-03-01T00:00:00.000Z',
      };
      final s = GDDSettings.fromJson(json);
      expect(s.harvestDate, isNull);
      expect(s.autoCalculate, true);
      expect(s.metadata, isNull);
    });

    test('fromJson autoCalculate explicitly false', () {
      final json = {
        'field_id': 'f1',
        'crop_type': 'wheat',
        'base_temperature': 5.0,
        'upper_threshold': 35.0,
        'calculation_method': 'average',
        'planting_date': '2025-01-15T00:00:00.000Z',
        'auto_calculate': false,
      };
      final s = GDDSettings.fromJson(json);
      expect(s.autoCalculate, false);
    });

    test('fromJson maps unknown crop_type to wheat', () {
      final json = {
        'field_id': 'f1',
        'crop_type': 'banana',
        'base_temperature': 5.0,
        'upper_threshold': 35.0,
        'calculation_method': 'average',
        'planting_date': '2025-01-15T00:00:00.000Z',
      };
      final s = GDDSettings.fromJson(json);
      expect(s.cropType, CropType.wheat);
    });

    test('toJson produces correct map', () {
      final s = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.tomato,
        baseTemperature: 10.0,
        upperThreshold: 32.0,
        calculationMethod: GDDCalculationMethod.modifiedAverage,
        plantingDate: DateTime.utc(2025, 4, 1),
        autoCalculate: false,
      );
      final json = s.toJson();
      expect(json['field_id'], 'f1');
      expect(json['crop_type'], 'tomato');
      expect(json['calculation_method'], 'modified_average');
      expect(json['auto_calculate'], false);
      expect(json['harvest_date'], isNull);
      expect(json['metadata'], isNull);
    });

    test('fromJson/toJson roundtrip preserves data', () {
      final json = {
        'field_id': 'f1',
        'crop_type': 'coffee',
        'base_temperature': 15.0,
        'upper_threshold': 30.0,
        'calculation_method': 'modified_average',
        'planting_date': '2025-02-01T00:00:00.000Z',
        'harvest_date': '2025-12-01T00:00:00.000Z',
        'auto_calculate': false,
        'metadata': {'notes': 'test'},
      };
      final s = GDDSettings.fromJson(json);
      final output = s.toJson();
      final restored = GDDSettings.fromJson(output);
      expect(restored.fieldId, s.fieldId);
      expect(restored.cropType, s.cropType);
      expect(restored.autoCalculate, s.autoCalculate);
      expect(restored.calculationMethod, s.calculationMethod);
      expect(restored.metadata?['notes'], 'test');
    });

    test('copyWith no changes returns equivalent object', () {
      final s = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.wheat,
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        calculationMethod: GDDCalculationMethod.average,
        plantingDate: DateTime.utc(2025, 1, 1),
      );
      final copy = s.copyWith();
      expect(copy.fieldId, s.fieldId);
      expect(copy.cropType, s.cropType);
      expect(copy.baseTemperature, s.baseTemperature);
      expect(copy.upperThreshold, s.upperThreshold);
      expect(copy.calculationMethod, s.calculationMethod);
    });

    test('copyWith changes specific fields only', () {
      final s = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.wheat,
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        calculationMethod: GDDCalculationMethod.average,
        plantingDate: DateTime.utc(2025, 1, 1),
        autoCalculate: true,
      );
      final copy = s.copyWith(
        cropType: CropType.corn,
        autoCalculate: false,
        baseTemperature: 10.0,
      );
      expect(copy.cropType, CropType.corn);
      expect(copy.autoCalculate, false);
      expect(copy.baseTemperature, 10.0);
      expect(copy.fieldId, 'f1');
      expect(copy.upperThreshold, 35.0);
    });

    test('copyWith can set harvestDate', () {
      final s = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.wheat,
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        calculationMethod: GDDCalculationMethod.average,
        plantingDate: DateTime.utc(2025, 1, 1),
      );
      final harvest = DateTime.utc(2025, 6, 1);
      final copy = s.copyWith(harvestDate: harvest);
      expect(copy.harvestDate, harvest);
    });

    test('copyWith can change calculationMethod', () {
      final s = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.wheat,
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        calculationMethod: GDDCalculationMethod.average,
        plantingDate: DateTime.utc(2025, 1, 1),
      );
      final copy =
          s.copyWith(calculationMethod: GDDCalculationMethod.modifiedAverage);
      expect(copy.calculationMethod, GDDCalculationMethod.modifiedAverage);
    });

    test('copyWith can set metadata', () {
      final s = GDDSettings(
        fieldId: 'f1',
        cropType: CropType.wheat,
        baseTemperature: 5.0,
        upperThreshold: 35.0,
        calculationMethod: GDDCalculationMethod.average,
        plantingDate: DateTime.utc(2025, 1, 1),
      );
      final copy = s.copyWith(metadata: {'key': 'value'});
      expect(copy.metadata, {'key': 'value'});
    });
  });
}
