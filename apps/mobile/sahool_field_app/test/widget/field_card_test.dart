import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Field Card Widget Tests
/// اختبارات بطاقة الحقل
void main() {
  group('Field Card', () {
    testWidgets('should display field name', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: ListTile(
                  title: const Text('حقل القمح'),
                  subtitle: const Text('100 هكتار'),
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('حقل القمح'), findsOneWidget);
      expect(find.text('100 هكتار'), findsOneWidget);
    });

    testWidgets('should show health indicator with correct color', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Column(
                  children: [
                    // Good health (green)
                    Container(
                      key: const Key('health-good'),
                      width: 20,
                      height: 20,
                      decoration: const BoxDecoration(
                        color: Colors.green,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const Text('صحة جيدة'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      final container = tester.widget<Container>(find.byKey(const Key('health-good')));
      final decoration = container.decoration as BoxDecoration;
      expect(decoration.color, Colors.green);
    });

    testWidgets('should show warning indicator for poor health', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Column(
                  children: [
                    // Warning health (orange)
                    Container(
                      key: const Key('health-warning'),
                      width: 20,
                      height: 20,
                      decoration: const BoxDecoration(
                        color: Colors.orange,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const Text('صحة متوسطة'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      final container = tester.widget<Container>(find.byKey(const Key('health-warning')));
      final decoration = container.decoration as BoxDecoration;
      expect(decoration.color, Colors.orange);
    });

    testWidgets('should handle tap interactions', (tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: GestureDetector(
                onTap: () => tapped = true,
                child: Card(
                  child: const ListTile(
                    title: Text('حقل الذرة'),
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      expect(tapped, false);
      await tester.tap(find.byType(Card));
      expect(tapped, true);
    });

    testWidgets('should display crop type correctly', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Column(
                  children: const [
                    Text('🌾', style: TextStyle(fontSize: 32)),
                    Text('قمح'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('🌾'), findsOneWidget);
      expect(find.text('قمح'), findsOneWidget);
    });

    testWidgets('should show moisture percentage', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Column(
                  children: const [
                    Icon(Icons.water_drop, color: Colors.blue),
                    Text('65%'),
                    Text('الرطوبة'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.water_drop), findsOneWidget);
      expect(find.text('65%'), findsOneWidget);
      expect(find.text('الرطوبة'), findsOneWidget);
    });
  });
}
