import 'package:flutter_test/flutter_test.dart';

/// Tests for crops feature models and state management
void main() {
  group('Crop Types', () {
    test('should define common SAHOOL crop types', () {
      final cropTypes = {
        'wheat': 'قمح',
        'barley': 'شعير',
        'date_palm': 'نخيل',
        'tomato': 'طماطم',
        'cucumber': 'خيار',
        'corn': 'ذرة',
        'alfalfa': 'برسيم',
        'sorghum': 'ذرة رفيعة',
      };

      expect(cropTypes, hasLength(8));
      expect(cropTypes['wheat'], 'قمح');
      expect(cropTypes['date_palm'], 'نخيل');
    });

    test('should define growth stages', () {
      final wheatStages = [
        'germination',
        'seedling',
        'tillering',
        'stem_extension',
        'heading',
        'flowering',
        'grain_filling',
        'ripening',
        'harvest',
      ];

      expect(wheatStages, hasLength(9));
      expect(wheatStages.first, 'germination');
      expect(wheatStages.last, 'harvest');
    });
  });

  group('Crop Health Classification', () {
    test('should classify NDVI to health status', () {
      String classifyHealth(double ndvi) {
        if (ndvi >= 0.6) return 'healthy';
        if (ndvi >= 0.4) return 'moderate';
        if (ndvi >= 0.2) return 'stressed';
        return 'critical';
      }

      expect(classifyHealth(0.75), 'healthy');
      expect(classifyHealth(0.50), 'moderate');
      expect(classifyHealth(0.30), 'stressed');
      expect(classifyHealth(0.10), 'critical');
    });

    test('should return Arabic health labels', () {
      final healthLabelsAr = {
        'healthy': 'صحي',
        'moderate': 'معتدل',
        'stressed': 'مجهد',
        'critical': 'حرج',
      };

      expect(healthLabelsAr['healthy'], 'صحي');
      expect(healthLabelsAr['critical'], 'حرج');
    });
  });

  group('Crop Water Requirements', () {
    test('should calculate crop water need (ETc)', () {
      // ETc = ET0 × Kc
      double calculateETc(double et0, double kc) => et0 * kc;

      // Wheat tillering stage: Kc = 1.15, ET0 = 6.5 mm/day
      expect(calculateETc(6.5, 1.15), closeTo(7.475, 0.001));

      // Date palm: Kc = 0.95, ET0 = 8.0 mm/day
      expect(calculateETc(8.0, 0.95), closeTo(7.6, 0.001));
    });

    test('should calculate gross irrigation need', () {
      double grossNeed(double etc, double efficiency) => etc / efficiency;

      // Drip irrigation (85% efficiency)
      expect(grossNeed(7.475, 0.85), closeTo(8.794, 0.001));

      // Flood irrigation (60% efficiency)
      expect(grossNeed(7.475, 0.60), closeTo(12.458, 0.001));
    });
  });
}
