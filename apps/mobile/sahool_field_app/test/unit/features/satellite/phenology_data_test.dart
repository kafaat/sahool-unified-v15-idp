import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/satellite/data/models/phenology_data.dart';

void main() {
  group('GrowthStage enum', () {
    test('has 7 growth stages', () {
      expect(GrowthStage.values, hasLength(7));
    });

    test('fromString parses valid values', () {
      expect(GrowthStage.fromString('germination'), GrowthStage.germination);
      expect(GrowthStage.fromString('vegetative'), GrowthStage.vegetative);
      expect(GrowthStage.fromString('flowering'), GrowthStage.flowering);
      expect(GrowthStage.fromString('fruit_development'), GrowthStage.fruitDevelopment);
      expect(GrowthStage.fromString('ripening'), GrowthStage.ripening);
      expect(GrowthStage.fromString('harvest'), GrowthStage.harvest);
    });

    test('fromString returns unknown for invalid', () {
      expect(GrowthStage.fromString('invalid'), GrowthStage.unknown);
    });

    test('has Arabic labels', () {
      expect(GrowthStage.germination.arabicLabel, 'إنبات');
      expect(GrowthStage.vegetative.arabicLabel, 'نمو خضري');
      expect(GrowthStage.flowering.arabicLabel, 'إزهار');
      expect(GrowthStage.harvest.arabicLabel, 'حصاد');
    });

    test('has color hex codes', () {
      expect(GrowthStage.germination.colorHex, '#8BC34A');
      expect(GrowthStage.harvest.colorHex, '#795548');
    });

    test('getLabel returns correct language', () {
      expect(GrowthStage.flowering.getLabel(true), 'إزهار');
      expect(GrowthStage.flowering.getLabel(false), 'flowering');
    });
  });

  group('GrowthStageInfo', () {
    test('fromJson and toJson round-trip', () {
      final json = {
        'stage': 'vegetative',
        'name': 'Vegetative Growth',
        'name_ar': 'النمو الخضري',
        'duration_days': 45,
        'start_date': '2026-01-15T00:00:00.000',
        'end_date': '2026-03-01T00:00:00.000',
        'is_completed': true,
        'is_current': false,
        'description': 'Leaf and stem development',
        'description_ar': 'نمو الأوراق والسيقان',
        'tasks': ['Apply nitrogen', 'Monitor growth'],
        'tasks_ar': ['تطبيق النيتروجين', 'مراقبة النمو'],
      };

      final info = GrowthStageInfo.fromJson(json);
      expect(info.stage, GrowthStage.vegetative);
      expect(info.name, 'Vegetative Growth');
      expect(info.nameAr, 'النمو الخضري');
      expect(info.durationDays, 45);
      expect(info.isCompleted, true);
      expect(info.isCurrent, false);
      expect(info.tasks, hasLength(2));
      expect(info.tasksAr, hasLength(2));

      final exported = info.toJson();
      expect(exported['stage'], 'vegetative');
      expect(exported['duration_days'], 45);
    });

    test('fromJson handles missing optional fields', () {
      final json = {
        'stage': 'flowering',
        'name': 'Flowering',
        'name_ar': 'إزهار',
        'duration_days': 20,
        'is_completed': false,
        'is_current': true,
      };

      final info = GrowthStageInfo.fromJson(json);
      expect(info.startDate, isNull);
      expect(info.endDate, isNull);
      expect(info.description, '');
      expect(info.tasks, isEmpty);
    });
  });

  group('PhenologyData', () {
    test('fromJson parses complete phenology data', () {
      final json = {
        'field_id': 'field-001',
        'crop_type': 'wheat',
        'crop_type_ar': 'قمح',
        'current_stage': 'vegetative',
        'days_in_current_stage': 15,
        'days_to_next_stage': 30,
        'days_to_harvest': 90,
        'planting_date': '2026-01-01T00:00:00.000',
        'expected_harvest_date': '2026-05-01T00:00:00.000',
        'stages': [
          {'stage': 'germination', 'name': 'Germination', 'name_ar': 'إنبات', 'duration_days': 10, 'is_completed': true, 'is_current': false},
          {'stage': 'vegetative', 'name': 'Vegetative', 'name_ar': 'نمو خضري', 'duration_days': 45, 'is_completed': false, 'is_current': true},
        ],
        'current_tasks': ['Monitor', 'Irrigate'],
        'current_tasks_ar': ['مراقبة', 'ري'],
        'completion_percentage': 25.5,
        'analyzed_at': '2026-03-01T00:00:00.000',
      };

      final data = PhenologyData.fromJson(json);
      expect(data.fieldId, 'field-001');
      expect(data.cropType, 'wheat');
      expect(data.cropTypeAr, 'قمح');
      expect(data.currentStage, GrowthStage.vegetative);
      expect(data.daysInCurrentStage, 15);
      expect(data.daysToNextStage, 30);
      expect(data.daysToHarvest, 90);
      expect(data.stages, hasLength(2));
      expect(data.currentTasks, hasLength(2));
      expect(data.currentTasksAr, hasLength(2));
      expect(data.completionPercentage, 25.5);
    });

    test('toJson produces correct output', () {
      final data = PhenologyData(
        fieldId: 'f1',
        cropType: 'wheat',
        cropTypeAr: 'قمح',
        currentStage: GrowthStage.flowering,
        daysInCurrentStage: 5,
        daysToHarvest: 60,
        plantingDate: DateTime(2026, 1, 1),
        completionPercentage: 50.0,
        analyzedAt: DateTime(2026, 3, 1),
      );

      final json = data.toJson();
      expect(json['field_id'], 'f1');
      expect(json['current_stage'], 'flowering');
      expect(json['completion_percentage'], 50.0);
    });

    test('fromJson handles camelCase keys', () {
      final json = {
        'fieldId': 'f2',
        'cropType': 'tomato',
        'cropTypeAr': 'طماطم',
        'currentStage': 'ripening',
        'daysInCurrentStage': 10,
        'daysToHarvest': 7,
        'plantingDate': '2026-01-01T00:00:00.000',
        'completionPercentage': 90.0,
        'analyzedAt': '2026-03-20T00:00:00.000',
      };

      final data = PhenologyData.fromJson(json);
      expect(data.fieldId, 'f2');
      expect(data.currentStage, GrowthStage.ripening);
      expect(data.completionPercentage, 90.0);
    });

    test('equality works with Equatable', () {
      final a = PhenologyData(fieldId: 'f1', cropType: 'wheat', cropTypeAr: 'قمح', currentStage: GrowthStage.vegetative, daysInCurrentStage: 10, plantingDate: DateTime(2026, 1, 1), completionPercentage: 25, analyzedAt: DateTime(2026, 3, 1));
      final b = PhenologyData(fieldId: 'f1', cropType: 'wheat', cropTypeAr: 'قمح', currentStage: GrowthStage.vegetative, daysInCurrentStage: 10, plantingDate: DateTime(2026, 1, 1), completionPercentage: 25, analyzedAt: DateTime(2026, 3, 1));
      expect(a, equals(b));
    });
  });
}
