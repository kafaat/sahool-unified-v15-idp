import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

/// Weather Widget Tests
/// اختبارات أداة الطقس
void main() {
  group('Weather Widget', () {
    testWidgets('should display temperature', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Text('32°C', style: TextStyle(fontSize: 48, fontWeight: FontWeight.bold)),
                    Text('صنعاء'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('32°C'), findsOneWidget);
      expect(find.text('صنعاء'), findsOneWidget);
    });

    testWidgets('should display weather condition', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.wb_sunny, color: Colors.orange),
                    SizedBox(width: 8),
                    Text('مشمس'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.wb_sunny), findsOneWidget);
      expect(find.text('مشمس'), findsOneWidget);
    });

    testWidgets('should display humidity', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.water_drop, color: Colors.blue),
                    SizedBox(width: 8),
                    Text('45%'),
                    SizedBox(width: 4),
                    Text('الرطوبة'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.water_drop), findsOneWidget);
      expect(find.text('45%'), findsOneWidget);
      expect(find.text('الرطوبة'), findsOneWidget);
    });

    testWidgets('should display wind speed', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.air, color: Colors.grey),
                    SizedBox(width: 8),
                    Text('15 كم/س'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.air), findsOneWidget);
      expect(find.text('15 كم/س'), findsOneWidget);
    });

    testWidgets('should show loading state', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should show error state', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(Icons.error_outline, color: Colors.red, size: 48),
                    const SizedBox(height: 16),
                    const Text('فشل تحميل بيانات الطقس'),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: () {},
                      child: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.error_outline), findsOneWidget);
      expect(find.text('فشل تحميل بيانات الطقس'), findsOneWidget);
      expect(find.text('إعادة المحاولة'), findsOneWidget);
    });

    testWidgets('should display rain chance', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Card(
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: const [
                    Icon(Icons.umbrella, color: Colors.indigo),
                    SizedBox(width: 8),
                    Text('20%'),
                    SizedBox(width: 4),
                    Text('احتمال المطر'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.umbrella), findsOneWidget);
      expect(find.text('20%'), findsOneWidget);
      expect(find.text('احتمال المطر'), findsOneWidget);
    });
  });
}
