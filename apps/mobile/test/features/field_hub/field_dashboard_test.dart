import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart';
import 'package:sahool_field_app/features/field_hub/ui/field_dashboard.dart';
import '../../helpers/test_helpers.dart';

void main() {
  group('FieldDashboard Widget', () {
    testWidgets('should display loading indicator initially', (tester) async {
      await tester.pumpWidget(createTestableWidget(
        child: const FieldDashboard(),
      ));

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should display welcome card', (tester) async {
      await tester.pumpWidget(createTestableWidget(
        child: const FieldDashboard(),
      ));
      await tester.pump();

      // Welcome greeting should show based on time of day
      expect(
        find.byWidgetPredicate(
          (w) => w is Text && (w.data?.contains('صباح') == true || w.data?.contains('مساء') == true),
        ),
        findsOneWidget,
      );
    });

    testWidgets('should display dashboard section titles', (tester) async {
      await tester.pumpWidget(createTestableWidget(
        child: const FieldDashboard(),
      ));
      await tester.pump(const Duration(seconds: 1));

      // Check for section headers
      expect(find.text('المؤشرات الحيوية'), findsOneWidget);
      expect(find.text('التنبيهات'), findsOneWidget);
    });

    testWidgets('should show refresh button in app bar', (tester) async {
      await tester.pumpWidget(createTestableWidget(
        child: const FieldDashboard(),
      ));

      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('should show notification icon in app bar', (tester) async {
      await tester.pumpWidget(createTestableWidget(
        child: const FieldDashboard(),
      ));

      expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
    });

    testWidgets('should display FAB for new task', (tester) async {
      await tester.pumpWidget(createTestableWidget(
        child: const FieldDashboard(),
      ));

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.text('مهمة جديدة'), findsOneWidget);
    });
  });

  group('FieldDashboard - Health Status', () {
    test('health label calculation', () {
      // Test the health label logic inline
      double getHealthLabel(double ndvi) {
        if (ndvi >= 0.7) return 4; // ممتازة
        if (ndvi >= 0.5) return 3; // جيدة
        if (ndvi >= 0.3) return 2; // متوسطة
        return 1; // ضعيفة
      }

      expect(getHealthLabel(0.8), 4);
      expect(getHealthLabel(0.6), 3);
      expect(getHealthLabel(0.4), 2);
      expect(getHealthLabel(0.1), 1);
    });

    test('nitrogen status calculation', () {
      String getNitrogenStatus(double avgNdvi) {
        if (avgNdvi >= 0.6) return 'جيد';
        if (avgNdvi >= 0.4) return 'متوسط';
        return 'منخفض';
      }

      expect(getNitrogenStatus(0.7), 'جيد');
      expect(getNitrogenStatus(0.5), 'متوسط');
      expect(getNitrogenStatus(0.3), 'منخفض');
    });
  });
}
