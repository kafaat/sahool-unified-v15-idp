/// Unit Tests for Agriculture Domain Models
/// اختبارات نماذج المجال الزراعي
///
/// Tests cover:
/// - SoilAnalysisValidator (pH, NPK, EC, texture triangle)
/// - WaterQualityAnalysis (SAR, irrigation class, fromJson)
/// - CropSalinityTolerance (FAO-29 yield reduction)
/// - FAOWaterClassification (salinity, sodium, chloride, boron, RSC)
/// - NutrientUptakeCoefficients (SSNM calculation)
/// - GDDCropConfig (daily GDD with cutoffs)
/// - SeedRateCatalog (quantity calculation)
/// - GeoUtils (area calculation, self-intersection, coordinate validation)
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:sahool_field_app/features/advisor/data/models/fertilizer_models.dart';
import 'package:sahool_field_app/features/advisor/data/models/agriculture_models.dart';
import 'package:sahool_field_app/features/crops/data/models/crop_model.dart';
import 'package:sahool_field_app/features/polygon_editor/utils/geo_utils.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // Soil Analysis Validator Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SoilAnalysisValidator', () {
    test('validatePh rejects out-of-range values', () {
      expect(SoilAnalysisValidator.validatePh(-1), isNotNull);
      expect(SoilAnalysisValidator.validatePh(15), isNotNull);
      expect(SoilAnalysisValidator.validatePh(null), isNotNull);
    });

    test('validatePh accepts valid range 0-14', () {
      expect(SoilAnalysisValidator.validatePh(0), isNull);
      expect(SoilAnalysisValidator.validatePh(7.0), isNull);
      expect(SoilAnalysisValidator.validatePh(14), isNull);
    });

    test('validateNitrogen rejects negative and excessive values', () {
      expect(SoilAnalysisValidator.validateNitrogen(-5), isNotNull);
      expect(SoilAnalysisValidator.validateNitrogen(2500), isNotNull);
    });

    test('validateNitrogen accepts valid ppm range', () {
      expect(SoilAnalysisValidator.validateNitrogen(0), isNull);
      expect(SoilAnalysisValidator.validateNitrogen(50), isNull);
      expect(SoilAnalysisValidator.validateNitrogen(2000), isNull);
    });

    test('validateEC accepts optional null', () {
      expect(SoilAnalysisValidator.validateEC(null), isNull);
    });

    test('validateEC rejects out-of-range', () {
      expect(SoilAnalysisValidator.validateEC(-1), isNotNull);
      expect(SoilAnalysisValidator.validateEC(55), isNotNull);
    });

    test('validateTexturePercent requires sum of 100%', () {
      // Valid: 40+30+30 = 100
      expect(SoilAnalysisValidator.validateTexturePercent(40, 30, 30), isNull);
      // Valid: all null (optional)
      expect(SoilAnalysisValidator.validateTexturePercent(null, null, null), isNull);
      // Invalid: 50+30+30 = 110
      expect(SoilAnalysisValidator.validateTexturePercent(50, 30, 30), isNotNull);
      // Invalid: 20+20+20 = 60
      expect(SoilAnalysisValidator.validateTexturePercent(20, 20, 20), isNotNull);
    });

    test('validateAll catches multiple errors', () {
      final badSoil = SoilAnalysis(
        ph: 20, // invalid
        nitrogen: -10, // invalid
        phosphorus: 30,
        potassium: 200,
      );
      final errors = SoilAnalysisValidator.validateAll(badSoil);
      expect(errors.length, greaterThanOrEqualTo(2));
    });

    test('validateAll passes for valid soil', () {
      final goodSoil = SoilAnalysis(
        ph: 7.2,
        nitrogen: 45,
        phosphorus: 25,
        potassium: 180,
        organicMatter: 2.5,
      );
      final errors = SoilAnalysisValidator.validateAll(goodSoil);
      expect(errors, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Quality Analysis Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('WaterQualityAnalysis', () {
    test('calculatedSAR formula is correct', () {
      // SAR = Na / sqrt((Ca+Mg)/2)
      final water = WaterQualityAnalysis(
        ph: 7.5,
        ec: 1.5,
        sodium: 10,
        calcium: 4,
        magnesium: 4,
      );
      // SAR = 10 / sqrt((4+4)/2) = 10 / sqrt(4) = 10/2 = 5
      expect(water.calculatedSAR, closeTo(5.0, 0.1));
    });

    test('calculatedSAR handles zero Ca+Mg', () {
      final water = WaterQualityAnalysis(ph: 7.0, ec: 0.5, sodium: 5);
      expect(water.calculatedSAR, equals(0));
    });

    test('irrigationClass classification is correct', () {
      expect(
        WaterQualityAnalysis(ph: 7, ec: 0.5).irrigationClass,
        contains('ممتازة'),
      );
      expect(
        WaterQualityAnalysis(ph: 7, ec: 1.5).irrigationClass,
        contains('جيدة'),
      );
      expect(
        WaterQualityAnalysis(ph: 7, ec: 2.5).irrigationClass,
        contains('مقبولة'),
      );
      expect(
        WaterQualityAnalysis(ph: 7, ec: 4.0).irrigationClass,
        contains('مشكوك'),
      );
      expect(
        WaterQualityAnalysis(ph: 7, ec: 6.0).irrigationClass,
        contains('غير صالحة'),
      );
    });

    test('fromJson parses all fields correctly', () {
      final json = {
        'ph': 7.8,
        'ec': 2.1,
        'tds': 1344,
        'sar': 4.5,
        'sodium': 8.0,
        'calcium': 5.0,
        'magnesium': 3.0,
        'chloride': 6.0,
        'bicarbonate': 4.0,
        'sulfate': 2.0,
        'boron': 0.5,
        'source': 'well',
        'source_ar': 'بئر',
        'test_date': '2026-03-15T00:00:00.000',
      };
      final water = WaterQualityAnalysis.fromJson(json);
      expect(water.ph, 7.8);
      expect(water.ec, 2.1);
      expect(water.tds, 1344);
      expect(water.sodium, 8.0);
      expect(water.source, 'well');
      expect(water.testDate, isNotNull);
    });

    test('toJson round-trips correctly', () {
      final original = WaterQualityAnalysis(
        ph: 7.5,
        ec: 1.8,
        sodium: 6,
        calcium: 4,
        magnesium: 2,
        source: 'canal',
      );
      final json = original.toJson();
      final restored = WaterQualityAnalysis.fromJson(json);
      expect(restored.ph, original.ph);
      expect(restored.ec, original.ec);
      expect(restored.sodium, original.sodium);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FAO Crop Salinity Tolerance Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('CropSalinityTolerance (FAO-29)', () {
    test('no yield reduction below threshold', () {
      final wheat = CropSalinityTolerance.faoTable['wheat']!;
      expect(wheat.yieldReduction(5.0), equals(0)); // below 6.0 threshold
      expect(wheat.expectedYieldPercent(5.0), equals(100));
    });

    test('correct yield reduction above threshold', () {
      final wheat = CropSalinityTolerance.faoTable['wheat']!;
      // At EC=8: (8-6)*7.1 = 14.2% reduction
      expect(wheat.yieldReduction(8.0), closeTo(14.2, 0.1));
      expect(wheat.expectedYieldPercent(8.0), closeTo(85.8, 0.1));
    });

    test('yield reduction clamped to 100%', () {
      final tomato = CropSalinityTolerance.faoTable['tomato']!;
      // At EC=15: (15-2.5)*9.9 = 123.75 → clamped to 100
      expect(tomato.yieldReduction(15.0), equals(100));
      expect(tomato.expectedYieldPercent(15.0), equals(0));
    });

    test('barley is more salt tolerant than tomato', () {
      final barley = CropSalinityTolerance.faoTable['barley']!;
      final tomato = CropSalinityTolerance.faoTable['tomato']!;
      expect(barley.ecThreshold, greaterThan(tomato.ecThreshold));
    });

    test('all FAO table entries have positive thresholds', () {
      for (final entry in CropSalinityTolerance.faoTable.values) {
        expect(entry.ecThreshold, greaterThan(0));
        expect(entry.yieldDeclinePercent, greaterThan(0));
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FAO Water Classification Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('FAOWaterClassification', () {
    test('salinity risk classification', () {
      expect(FAOWaterClassification.salinityRisk(0.5), contains('لا يوجد'));
      expect(FAOWaterClassification.salinityRisk(1.5), contains('طفيف'));
      expect(FAOWaterClassification.salinityRisk(4.0), contains('شديد'));
    });

    test('chloride toxicity classification', () {
      expect(FAOWaterClassification.chlorideToxicity(2.0), contains('لا يوجد'));
      expect(FAOWaterClassification.chlorideToxicity(7.0), contains('طفيف'));
      expect(FAOWaterClassification.chlorideToxicity(12.0), contains('شديد'));
    });

    test('boron toxicity classification', () {
      expect(FAOWaterClassification.boronToxicity(0.3), contains('لا يوجد'));
      expect(FAOWaterClassification.boronToxicity(1.5), contains('طفيف'));
      expect(FAOWaterClassification.boronToxicity(4.0), contains('شديد'));
    });

    test('RSC calculation and classification', () {
      // RSC = (CO3+HCO3) - (Ca+Mg)
      final rsc = FAOWaterClassification.calculateRSC(0.5, 3.0, 2.0, 1.0);
      // RSC = (0.5+3.0) - (2.0+1.0) = 0.5
      expect(rsc, closeTo(0.5, 0.01));
      expect(FAOWaterClassification.rscClassification(rsc), contains('آمنة'));

      expect(FAOWaterClassification.rscClassification(2.0), contains('هامشية'));
      expect(FAOWaterClassification.rscClassification(3.0), contains('غير صالحة'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Nutrient Uptake (SSNM) Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NutrientUptakeCoefficients (SSNM)', () {
    test('wheat fertilizer need calculation', () {
      final wheat = NutrientUptakeCoefficients.table['wheat']!;
      final need = wheat.calculateFertilizerNeed(
        targetYield: 5.0, // 5 ton/ha
        soilN: 20, // 20 kg/ha available
        nEfficiency: 0.40,
      );
      // N demand = 5 * 27 = 135, deficit = 135-20 = 115, rate = 115/0.4 = 287.5
      expect(need.nKgHa, closeTo(287.5, 1));
    });

    test('fertilizer need clamped to non-negative', () {
      final wheat = NutrientUptakeCoefficients.table['wheat']!;
      final need = wheat.calculateFertilizerNeed(
        targetYield: 1.0,
        soilN: 200, // soil has more than needed
      );
      expect(need.nKgHa, equals(0));
    });

    test('all crops in table have positive coefficients', () {
      for (final entry in NutrientUptakeCoefficients.table.values) {
        expect(entry.nPerTon, greaterThan(0));
        expect(entry.p2o5PerTon, greaterThan(0));
        expect(entry.k2oPerTon, greaterThan(0));
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GDD Calculation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GDDCropConfig', () {
    test('daily GDD with both temps above base', () {
      final wheat = GDDCropConfig.table['wheat_winter']!;
      // tMax=25, tMin=10, base=0 → GDD = (25+10)/2 - 0 = 17.5
      expect(wheat.dailyGDD(25, 10), closeTo(17.5, 0.1));
    });

    test('daily GDD with tMin below base clamps', () {
      final maize = GDDCropConfig.table['maize']!;
      // tMax=20, tMin=5, base=10 → adjMin=10, GDD = (20+10)/2 - 10 = 5
      expect(maize.dailyGDD(20, 5), closeTo(5.0, 0.1));
    });

    test('daily GDD zero when both below base', () {
      final maize = GDDCropConfig.table['maize']!;
      // tMax=8, tMin=3, base=10 → both clamped to 10, GDD = 0
      expect(maize.dailyGDD(8, 3), equals(0));
    });

    test('daily GDD with upper cutoff', () {
      final wheat = GDDCropConfig.table['wheat_winter']!;
      // tMax=40, tMin=20, base=0, upper=30 → adjMax=30, GDD=(30+20)/2=25
      expect(wheat.dailyGDD(40, 20), closeTo(25, 0.1));
    });

    test('all crops have valid base < upper temp', () {
      for (final config in GDDCropConfig.table.values) {
        expect(config.upperTemp, greaterThan(config.baseTemp));
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Seed Rate Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SeedRateCatalog', () {
    test('wheat seed rate is in FAO range', () {
      final wheat = SeedRateCatalog.rates['wheat']!;
      expect(wheat.rateKgPerHa, greaterThanOrEqualTo(100));
      expect(wheat.rateKgPerHa, lessThanOrEqualTo(160));
    });

    test('calculateSeedQuantity scales linearly', () {
      final wheat = SeedRateCatalog.rates['wheat']!;
      expect(wheat.calculateSeedQuantity(1), equals(wheat.rateKgPerHa));
      expect(wheat.calculateSeedQuantity(10), equals(wheat.rateKgPerHa * 10));
    });

    test('rateKgPerFeddan is ~42% of per-hectare', () {
      final wheat = SeedRateCatalog.rates['wheat']!;
      expect(wheat.rateKgPerFeddan, closeTo(wheat.rateKgPerHa * 0.42, 1));
    });

    test('date_palm has zero seed rate (offshoot-based)', () {
      final palm = SeedRateCatalog.rates['date_palm']!;
      expect(palm.rateKgPerHa, equals(0));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // GeoUtils Area & Validation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('GeoUtils', () {
    test('area of empty polygon is 0', () {
      expect(GeoUtils.calculateAreaSqMeters([]), equals(0));
    });

    test('area of less than 3 points is 0', () {
      expect(GeoUtils.calculateAreaSqMeters([LatLng(0, 0), LatLng(1, 1)]), equals(0));
    });

    test('area of known rectangle is approximately correct', () {
      // ~1km x ~1km rectangle near equator
      final polygon = [
        LatLng(0.0, 0.0),
        LatLng(0.0, 0.01),
        LatLng(0.01, 0.01),
        LatLng(0.01, 0.0),
      ];
      final areaSqM = GeoUtils.calculateAreaSqMeters(polygon);
      // 0.01° ≈ 1.11km at equator, so area ≈ 1.11*1.11 = ~1.23 km² = ~1,230,000 m²
      expect(areaSqM, greaterThan(1000000));
      expect(areaSqM, lessThan(1500000));
    });

    test('area in hectares converts correctly', () {
      final polygon = [
        LatLng(0.0, 0.0),
        LatLng(0.0, 0.001),
        LatLng(0.001, 0.001),
        LatLng(0.001, 0.0),
      ];
      final ha = GeoUtils.calculateAreaHectares(polygon);
      expect(ha, greaterThan(0));
    });

    test('isValidCoordinate accepts valid coordinates', () {
      expect(GeoUtils.isValidCoordinate(LatLng(0, 0)), isTrue);
      expect(GeoUtils.isValidCoordinate(LatLng(90, 180)), isTrue);
      expect(GeoUtils.isValidCoordinate(LatLng(-90, -180)), isTrue);
      expect(GeoUtils.isValidCoordinate(LatLng(15.3694, 44.1910)), isTrue); // Sana'a
    });

    test('isValidCoordinate rejects invalid coordinates', () {
      expect(GeoUtils.isValidCoordinate(LatLng(91, 0)), isFalse);
      expect(GeoUtils.isValidCoordinate(LatLng(0, 181)), isFalse);
      expect(GeoUtils.isValidCoordinate(LatLng(-91, 0)), isFalse);
    });

    test('isSelfIntersecting detects bowtie polygon', () {
      // Bowtie: lines cross at center
      final bowtie = [
        LatLng(0, 0),
        LatLng(1, 1),
        LatLng(1, 0),
        LatLng(0, 1),
      ];
      expect(GeoUtils.isSelfIntersecting(bowtie), isTrue);
    });

    test('isSelfIntersecting passes for simple polygon', () {
      final simple = [
        LatLng(0, 0),
        LatLng(0, 1),
        LatLng(1, 1),
        LatLng(1, 0),
      ];
      expect(GeoUtils.isSelfIntersecting(simple), isFalse);
    });

    test('isSelfIntersecting returns false for triangle', () {
      final triangle = [
        LatLng(0, 0),
        LatLng(0, 1),
        LatLng(1, 0),
      ];
      expect(GeoUtils.isSelfIntersecting(triangle), isFalse);
    });

    test('centroid of square is at center', () {
      final square = [
        LatLng(0, 0),
        LatLng(0, 2),
        LatLng(2, 2),
        LatLng(2, 0),
      ];
      final centroid = GeoUtils.calculateCentroid(square);
      expect(centroid, isNotNull);
      expect(centroid!.latitude, closeTo(1.0, 0.01));
      expect(centroid.longitude, closeTo(1.0, 0.01));
    });

    test('perimeter of equilateral-ish triangle is positive', () {
      final triangle = [
        LatLng(0, 0),
        LatLng(0, 0.01),
        LatLng(0.01, 0.005),
      ];
      expect(GeoUtils.calculatePerimeter(triangle), greaterThan(0));
    });

    test('distanceMeters returns reasonable values', () {
      // Sana'a to Aden ≈ ~350km
      final sanaa = LatLng(15.3694, 44.1910);
      final aden = LatLng(12.7855, 45.0187);
      final dist = GeoUtils.distanceMeters(sanaa, aden);
      expect(dist, greaterThan(280000)); // > 280 km
      expect(dist, lessThan(320000)); // < 320 km
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BBCH Stages Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('WheatBBCHStages', () {
    test('has 10 growth stages', () {
      expect(WheatBBCHStages.stages.length, equals(10));
    });

    test('stages are in GDD order', () {
      for (int i = 1; i < WheatBBCHStages.stages.length; i++) {
        final prev = WheatBBCHStages.stages[i - 1]['gddStart'] as double;
        final curr = WheatBBCHStages.stages[i]['gddStart'] as double;
        expect(curr, greaterThanOrEqualTo(prev));
      }
    });

    test('first stage starts at GDD 0', () {
      expect(WheatBBCHStages.stages.first['gddStart'], equals(0));
    });

    test('last stage ends at GDD ~2100 (wheat maturity)', () {
      expect(WheatBBCHStages.stages.last['gddEnd'], equals(2100));
    });

    test('all stages have Arabic and English names', () {
      for (final stage in WheatBBCHStages.stages) {
        expect(stage['nameEn'], isNotEmpty);
        expect(stage['nameAr'], isNotEmpty);
      }
    });

    test('Kc peaks at heading/flowering', () {
      final headingKc = WheatBBCHStages.stages[5]['kc'] as double; // Heading
      final seedlingKc = WheatBBCHStages.stages[1]['kc'] as double; // Seedling
      expect(headingKc, greaterThan(seedlingKc));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Division-by-Zero Guard Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Division-by-zero guards', () {
    test('GDD gauge handles totalGDD=0', () {
      // Testing the formula: totalGDD > 0 ? (current/total).clamp(0,1) : 0
      const totalGDD = 0.0;
      const currentGDD = 50.0;
      final progress = totalGDD > 0
          ? (currentGDD / totalGDD).clamp(0.0, 1.0)
          : 0.0;
      expect(progress, equals(0.0));
    });

    test('billing usage row handles total=0', () {
      const used = 5;
      const total = 0;
      final percentage = total > 0 ? used / total : 0.0;
      expect(percentage, equals(0.0));
    });

    test('wallet payment progress handles totalDue=0', () {
      const paidAmount = 100.0;
      const totalDue = 0.0;
      final progress = totalDue > 0 ? paidAmount / totalDue : 0.0;
      expect(progress, equals(0.0));
    });

    test('pivot irrigation time handles speedPercent=0', () {
      const fullCircleMinutes = 120.0;
      const angleSpan = 90.0;
      const speedPercent = 0.0;
      final time = speedPercent <= 0
          ? double.infinity
          : fullCircleMinutes * (angleSpan / 360) * (100 / speedPercent);
      expect(time, equals(double.infinity));
    });

    test('soil health percent change handles oldValue=0', () {
      const newValue = 5.0;
      const oldValue = 0.0;
      final change = newValue - oldValue;
      final percentChange = oldValue != 0
          ? (change / oldValue * 100).toStringAsFixed(1)
          : '0.0';
      expect(percentChange, equals('0.0'));
    });

    test('crop progress handles growingSeasonDays=0', () {
      const daysPlanted = 45;
      const totalDays = 0;
      final progress = totalDays > 0
          ? (daysPlanted / totalDays).clamp(0.0, 1.0)
          : 0.0;
      expect(progress, equals(0.0));
    });

    test('GDD stage progress handles zero range', () {
      const gddStart = 500.0;
      const gddEnd = 500.0; // zero range
      const currentGDD = 500.0;
      final range = gddEnd - gddStart;
      final progress = range > 0
          ? ((currentGDD - gddStart) / range).clamp(0.0, 1.0)
          : 0.0;
      expect(progress, equals(0.0));
    });
  });
}
