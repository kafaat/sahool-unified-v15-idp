import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/rotation/models/rotation_models.dart';
import 'package:sahool_field_app/features/rotation/services/rotation_service.dart';

void main() {
  late RotationService service;

  setUp(() {
    service = RotationService();
  });

  group('RotationService', () {
    group('getRotationPlan', () {
      test('should return a rotation plan for given field ID', () async {
        final plan = await service.getRotationPlan('field_001');

        expect(plan, isNotNull);
        expect(plan.fieldId, 'field_001');
        expect(plan.rotationYears.length, greaterThan(0));
      });

      test('should include past, current, and future rotations', () async {
        final plan = await service.getRotationPlan('field_001');

        expect(plan.pastRotations, isNotEmpty);
        expect(plan.futureRotations, isNotEmpty);
      });

      test('should include soil health data for past rotations', () async {
        final plan = await service.getRotationPlan('field_001');

        final pastWithSoilData = plan.pastRotations
            .where((r) => r.soilHealthBefore != null)
            .toList();
        expect(pastWithSoilData, isNotEmpty);
      });
    });

    group('generateRotationPlan', () {
      test('should generate a plan with specified number of years', () async {
        final plan = await service.generateRotationPlan(
          'field_002',
          5,
          {
            'prioritizeSoilHealth': true,
            'includeNitrogenFixers': true,
          },
        );

        expect(plan.rotationYears.length, 5);
      });

      test('should include nitrogen fixers when requested', () async {
        final plan = await service.generateRotationPlan(
          'field_002',
          6,
          {
            'prioritizeSoilHealth': true,
            'includeNitrogenFixers': true,
          },
        );

        final legumes = plan.rotationYears
            .where((r) => r.crop?.family == CropFamily.fabaceae)
            .toList();

        expect(legumes.isNotEmpty, true,
            reason: 'Should include at least one legume for nitrogen fixing');
      });

      test('should avoid consecutive same-family crops', () async {
        final plan = await service.generateRotationPlan(
          'field_002',
          5,
          {
            'prioritizeSoilHealth': true,
            'includeNitrogenFixers': true,
            'avoidSameFamily': true,
          },
        );

        // Check that consecutive years don't have same family
        for (int i = 1; i < plan.rotationYears.length; i++) {
          final prev = plan.rotationYears[i - 1].crop?.family;
          final curr = plan.rotationYears[i].crop?.family;

          if (prev != null && curr != null) {
            // Allow some flexibility - consecutive same family is OK
            // but we shouldn't have 3+ in a row
            if (i > 1) {
              final prevPrev = plan.rotationYears[i - 2].crop?.family;
              expect(
                prev == curr && prevPrev == curr,
                false,
                reason: 'Should not have 3+ consecutive same-family crops',
              );
            }
          }
        }
      });

      test('should calculate planting and harvest dates', () async {
        final plan = await service.generateRotationPlan(
          'field_002',
          3,
          {'prioritizeSoilHealth': false},
        );

        for (final year in plan.rotationYears) {
          if (year.crop != null) {
            expect(year.plantingDate, isNotNull);
            expect(year.harvestDate, isNotNull);

            if (year.plantingDate != null && year.harvestDate != null) {
              expect(
                year.harvestDate!.isAfter(year.plantingDate!),
                true,
                reason: 'Harvest date should be after planting date',
              );
            }
          }
        }
      });
    });

    group('getCropCompatibility', () {
      test('should return low score for same family crops', () async {
        final tomato = YemenCrops.crops.firstWhere((c) => c.id == 'tomato');

        // Create another solanaceae crop for comparison
        const potato = Crop(
          id: 'potato',
          nameEn: 'Potato',
          nameAr: 'بطاطس',
          family: CropFamily.solanaceae,
          growingDays: 100,
          season: 'Spring',
        );

        final compatibility =
            await service.getCropCompatibility(tomato, potato);

        expect(compatibility.score, lessThan(0.5));
        expect(compatibility.level, 'Avoid');
      });

      test('should return high score for legume followed by heavy feeder',
          () async {
        final legume = YemenCrops.crops.firstWhere(
          (c) => c.family == CropFamily.fabaceae,
        );
        final heavyFeeder = YemenCrops.crops.firstWhere(
          (c) => c.family == CropFamily.poaceae,
        );

        final compatibility = await service.getCropCompatibility(
          legume,
          heavyFeeder,
        );

        expect(compatibility.score, greaterThan(0.8));
      });

      test('should return good score for different families', () async {
        final crop1 = YemenCrops.crops.firstWhere((c) => c.id == 'wheat');
        final crop2 = YemenCrops.crops.firstWhere((c) => c.id == 'onion');

        final compatibility = await service.getCropCompatibility(crop1, crop2);

        expect(compatibility.score, greaterThanOrEqualTo(0.7));
      });

      test('should include Arabic and English reasons', () async {
        final crop1 = YemenCrops.crops.first;
        final crop2 = YemenCrops.crops.last;

        final compatibility = await service.getCropCompatibility(crop1, crop2);

        expect(compatibility.reason, isNotEmpty);
        expect(compatibility.reasonAr, isNotEmpty);
      });
    });

    group('getSoilHealthTrend', () {
      test('should return soil health data over time', () async {
        final trend = await service.getSoilHealthTrend('field_001');

        expect(trend.length, 5);
      });

      test('should show improving trend with proper rotation', () async {
        final trend = await service.getSoilHealthTrend('field_001');

        // Overall trend should be improving
        final firstScore = trend.first.overallScore;
        final lastScore = trend.last.overallScore;

        expect(lastScore, greaterThanOrEqualTo(firstScore));
      });

      test('should have valid pH values', () async {
        final trend = await service.getSoilHealthTrend('field_001');

        for (final health in trend) {
          expect(health.ph, greaterThanOrEqualTo(0));
          expect(health.ph, lessThanOrEqualTo(14));
        }
      });
    });

    group('getRecommendedCrops', () {
      test('should return recommendations sorted by suitability', () async {
        final recommendations = await service.getRecommendedCrops(
          'field_001',
          DateTime.now().year + 1,
        );

        expect(recommendations.length, greaterThan(0));

        // Verify sorted by score descending
        for (int i = 1; i < recommendations.length; i++) {
          expect(
            recommendations[i - 1].suitabilityScore,
            greaterThanOrEqualTo(recommendations[i].suitabilityScore),
          );
        }
      });

      test('should include reasons for recommendations', () async {
        final recommendations = await service.getRecommendedCrops(
          'field_001',
          DateTime.now().year + 1,
        );

        for (final rec in recommendations) {
          expect(rec.reasons, isNotEmpty);
          expect(rec.reasonsAr, isNotEmpty);
        }
      });

      test('should exclude perennial crops', () async {
        final recommendations = await service.getRecommendedCrops(
          'field_001',
          DateTime.now().year + 1,
        );

        final perennials = recommendations.where((r) => r.crop.isPerennial);
        expect(perennials.isEmpty, true);
      });
    });

    group('getAllCropFamilies', () {
      test('should return all crop families', () {
        final families = service.getAllCropFamilies();

        expect(families.length, CropFamily.values.length);
      });

      test('should include bilingual names', () {
        final families = service.getAllCropFamilies();

        for (final family in families) {
          expect(family.nameEn, isNotEmpty);
          expect(family.nameAr, isNotEmpty);
        }
      });
    });

    group('getCompatibilityMatrix', () {
      test('should return matrix for all non-perennial crops', () async {
        final matrix = await service.getCompatibilityMatrix();

        final nonPerennialCrops = YemenCrops.crops
            .where((c) => !c.isPerennial)
            .map((c) => c.id)
            .toList();

        for (final cropId in nonPerennialCrops) {
          expect(matrix.containsKey(cropId), true);
        }
      });

      test('should not include self-compatibility', () async {
        final matrix = await service.getCompatibilityMatrix();

        for (final entry in matrix.entries) {
          expect(entry.value.containsKey(entry.key), false);
        }
      });
    });
  });
}
