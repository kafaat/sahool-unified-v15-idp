import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/scouting/ui/scouting_screen.dart';

// Mock GoRouter to avoid dependency issues
class _MockGoRouter extends StatelessWidget {
  final Widget child;
  const _MockGoRouter({required this.child});

  @override
  Widget build(BuildContext context) => MaterialApp(home: child);
}

void main() {
  group('ScoutingScreen', () {
    testWidgets('renders with initial state', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      expect(find.text('تقرير ميداني'), findsOneWidget);
      expect(find.text('نوع المشكلة'), findsOneWidget);
    });

    testWidgets('renders 4 category tiles', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      expect(find.text('حشرات'), findsOneWidget);
      expect(find.text('فطريات'), findsOneWidget);
      expect(find.text('جفاف'), findsOneWidget);
      expect(find.text('نقص غذائي'), findsOneWidget);
    });

    testWidgets('renders category icons', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      expect(find.byIcon(Icons.bug_report), findsOneWidget);
      expect(find.byIcon(Icons.spa), findsOneWidget);
      expect(find.byIcon(Icons.water_drop), findsAtLeastNWidgets(1));
      expect(find.byIcon(Icons.eco), findsAtLeastNWidgets(1));
    });

    testWidgets('submit button is disabled initially', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      expect(find.text('إرسال'), findsOneWidget);
      // No إرسال التقرير button until issue is selected
      expect(find.text('إرسال التقرير'), findsNothing);
    });

    testWidgets('selecting category shows issue options', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      // Tap حشرات
      await tester.tap(find.text('حشرات'));
      await tester.pumpAndSettle();

      // Should show step 2 and insect issues
      expect(find.text('تفاصيل المشكلة'), findsOneWidget);
      expect(find.text('من'), findsOneWidget);
      expect(find.text('دودة'), findsOneWidget);
      expect(find.text('جراد'), findsOneWidget);
    });

    testWidgets('selecting fungi category shows fungi issues', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      await tester.tap(find.text('فطريات'));
      await tester.pumpAndSettle();

      expect(find.text('صدأ'), findsOneWidget);
      expect(find.text('بياض'), findsOneWidget);
      expect(find.text('تعفن'), findsOneWidget);
    });

    testWidgets('changing category shows new issues', (tester) async {
      await tester.pumpWidget(
        const _MockGoRouter(child: ScoutingScreen()),
      );

      // Select حشرات
      await tester.tap(find.text('حشرات'));
      await tester.pumpAndSettle();
      expect(find.text('من'), findsOneWidget);

      // Change to جفاف
      await tester.tap(find.text('جفاف'));
      await tester.pumpAndSettle();
      expect(find.text('ذبول'), findsOneWidget);
      expect(find.text('اصفرار'), findsOneWidget);
    });
  });
}
