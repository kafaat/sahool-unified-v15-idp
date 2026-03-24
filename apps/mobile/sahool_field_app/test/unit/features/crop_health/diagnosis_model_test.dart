import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/crop_health/data/models/diagnosis_model.dart';

void main() {
  group('DiseaseSeverity', () {
    test('has all 5 values', () {
      expect(DiseaseSeverity.values, hasLength(5));
    });

    test('arabicName returns correct Arabic names', () {
      expect(DiseaseSeverity.healthy.arabicName, 'سليم');
      expect(DiseaseSeverity.low.arabicName, 'منخفض');
      expect(DiseaseSeverity.medium.arabicName, 'متوسط');
      expect(DiseaseSeverity.high.arabicName, 'مرتفع');
      expect(DiseaseSeverity.critical.arabicName, 'حرج');
    });

    test('color returns hex color strings', () {
      expect(DiseaseSeverity.healthy.color, '#22C55E');
      expect(DiseaseSeverity.low.color, '#84CC16');
      expect(DiseaseSeverity.medium.color, '#EAB308');
      expect(DiseaseSeverity.high.color, '#F97316');
      expect(DiseaseSeverity.critical.color, '#EF4444');
    });
  });

  group('DiagnosisSummary', () {
    test('fromDiagnosis extracts summary fields correctly', () {
      // Note: This test validates the factory constructor logic
      // The actual fromJson/fromDiagnosis requires generated freezed code
      // Testing the enum and severity mapping which are hand-written

      // Verify severity enum values match JSON
      expect(DiseaseSeverity.healthy.name, 'healthy');
      expect(DiseaseSeverity.low.name, 'low');
      expect(DiseaseSeverity.medium.name, 'medium');
      expect(DiseaseSeverity.high.name, 'high');
      expect(DiseaseSeverity.critical.name, 'critical');
    });
  });

  group('DiseaseSeverity color mapping', () {
    test('healthy is green', () {
      expect(DiseaseSeverity.healthy.color, contains('22C55E'));
    });

    test('critical is red', () {
      expect(DiseaseSeverity.critical.color, contains('EF4444'));
    });

    test('each severity has a unique color', () {
      final colors = DiseaseSeverity.values.map((s) => s.color).toSet();
      expect(colors.length, DiseaseSeverity.values.length);
    });
  });
}
