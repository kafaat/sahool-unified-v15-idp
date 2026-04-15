import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/field_hub/ui/field_dashboard.dart';

void main() {
  group('FieldDashboard', () {
    testWidgets('renders scaffold with Arabic title', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.text('لوحة القيادة'), findsOneWidget);
    });

    testWidgets('renders greeting based on time of day', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      // Should show either صباح الخير or مساء الخير
      final morning = find.text('صباح الخير');
      final evening = find.text('مساء الخير');
      expect(morning.evaluate().isNotEmpty || evening.evaluate().isNotEmpty, true);
    });

    testWidgets('renders health card with NDVI', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.text('صحة المحصول'), findsOneWidget);
      expect(find.text('NDVI: 0.78'), findsOneWidget);
      expect(find.text('ممتازة'), findsOneWidget);
      expect(find.text('78%'), findsOneWidget);
    });

    testWidgets('renders metrics grid with 4 indicators', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.text('المؤشرات الحيوية'), findsOneWidget);
      expect(find.text('رطوبة التربة'), findsOneWidget);
      expect(find.text('النيتروجين'), findsOneWidget);
      expect(find.text('1,200'), findsOneWidget); // GDD
    });

    testWidgets('renders alerts section after scrolling', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      // Scroll down to reach alerts
      await tester.dragUntilVisible(
        find.text('التنبيهات'),
        find.byType(ListView),
        const Offset(0, -300),
      );
      expect(find.text('التنبيهات'), findsOneWidget);
    });

    testWidgets('renders tasks section after scrolling', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      await tester.dragUntilVisible(
        find.text('المهام القادمة'),
        find.byType(ListView),
        const Offset(0, -300),
      );
      expect(find.text('المهام القادمة'), findsOneWidget);
    });

    testWidgets('renders weather forecast after scrolling', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      await tester.dragUntilVisible(
        find.text('توقعات الطقس'),
        find.byType(ListView),
        const Offset(0, -300),
      );
      expect(find.text('توقعات الطقس'), findsOneWidget);
    });

    testWidgets('renders FAB with new task label', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.text('مهمة جديدة'), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('renders notification and refresh buttons', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.byIcon(Icons.notifications_outlined), findsOneWidget);
      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('renders connection status badge', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.text('متصل'), findsOneWidget);
    });

    testWidgets('renders task count message', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: FieldDashboard(),
        ),
      );

      expect(find.text('لديك 3 مهام اليوم'), findsOneWidget);
    });
  });
}
