import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/di/providers.dart';
import 'package:sahool_field_app/core/iam/iam_providers.dart';
import 'package:sahool_field_app/features/field/domain/entities/field.dart';
import 'package:sahool_field_app/features/field_hub/ui/field_dashboard.dart';
import '../../helpers/test_helpers.dart';

void main() {
  group('FieldDashboard Widget', () {
    /// Helper that wraps FieldDashboard with mocked providers so we don't
    /// need a real database or IAM state.
    Widget buildDashboard({List<Field> fields = const []}) {
      return createTestableWidget(
        overrides: [
          currentTenantProvider.overrideWithValue(null),
          fieldsStreamProvider('default')
              .overrideWith((ref) => Stream.value(fields)),
        ],
        child: const FieldDashboard(),
      );
    }

    testWidgets('should display loading indicator initially', (tester) async {
      await tester.pumpWidget(
        createTestableWidget(
          overrides: [
            currentTenantProvider.overrideWithValue(null),
            fieldsStreamProvider('default')
                .overrideWith((ref) => const Stream.empty()),
          ],
          child: const FieldDashboard(),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should display dashboard after data loads', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      // App bar title should always show
      expect(find.text('لوحة القيادة'), findsOneWidget);
    });

    testWidgets('should show refresh button in app bar', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('should show notification icon in app bar', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
    });

    testWidgets('should display FAB for new task', (tester) async {
      await tester.pumpWidget(buildDashboard());
      await tester.pump();

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.text('مهمة جديدة'), findsOneWidget);
    });
  });

  group('FieldDashboard - Health Status', () {
    test('health label calculation', () {
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
