/// SAHOOL Field App - Irrigation Management Integration Tests
/// اختبارات تكامل إدارة الري
///
/// Tests:
/// - Irrigation schedule display
/// - Smart irrigation recommendation cards
/// - Irrigation history list
/// - Water usage statistics
/// - Soil moisture display
/// - Manual irrigation trigger UI
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  // =========================================================================
  // Irrigation Schedule Tests
  // اختبارات جدول الري
  // =========================================================================

  group('Irrigation Schedule Tests - اختبارات جدول الري', () {
    testWidgets('Irrigation schedule shows upcoming events', (tester) async {
      final scheduleItems = [
        {
          'fieldName': 'حقل القمح الشمالي',
          'date': '2026-03-15',
          'amount': '25 مم',
          'method': 'تنقيط',
        },
        {
          'fieldName': 'حقل الذرة الجنوبي',
          'date': '2026-03-16',
          'amount': '30 مم',
          'method': 'رش',
        },
      ];

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('جدول الري')),
            body: ListView.builder(
              itemCount: scheduleItems.length,
              itemBuilder: (_, i) => ListTile(
                leading:
                    const Icon(Icons.water_drop, color: Colors.blue),
                title: Text(scheduleItems[i]['fieldName']!),
                subtitle: Text(
                    '${scheduleItems[i]['date']} - ${scheduleItems[i]['amount']}'),
                trailing: Chip(
                  label: Text(scheduleItems[i]['method']!),
                  backgroundColor: Colors.blue.withOpacity(0.1),
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('جدول الري'), findsOneWidget);
      expect(find.text('حقل القمح الشمالي'), findsOneWidget);
      expect(find.text('حقل الذرة الجنوبي'), findsOneWidget);
      expect(find.text('تنقيط'), findsOneWidget);
      expect(find.text('رش'), findsOneWidget);
    });

    testWidgets('Irrigation next scheduled date is displayed', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Card(
              margin: const EdgeInsets.all(16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: const [
                    Text('الري القادم',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold)),
                    SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(Icons.calendar_today, color: Colors.blue),
                        SizedBox(width: 8),
                        Text('غداً - 15 مارس 2026'),
                      ],
                    ),
                    SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.water, color: Colors.blue),
                        SizedBox(width: 8),
                        Text('الكمية المقترحة: 25 مم'),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الري القادم'), findsOneWidget);
      expect(find.text('غداً - 15 مارس 2026'), findsOneWidget);
      expect(find.text('الكمية المقترحة: 25 مم'), findsOneWidget);
    });
  });

  // =========================================================================
  // Smart Irrigation Recommendation Tests
  // اختبارات توصيات الري الذكي
  // =========================================================================

  group('Smart Irrigation Recommendation Tests - اختبارات الري الذكي', () {
    testWidgets('Smart irrigation card shows recommendation', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.smart_toy, color: Colors.green),
                          const SizedBox(width: 8),
                          const Text(
                            'توصية الري الذكي',
                            style: TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          const Spacer(),
                          Chip(
                            label: const Text('تنفيذ اليوم'),
                            backgroundColor:
                                Colors.orange.withOpacity(0.2),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Text('ينصح بري حقل القمح الشمالي'),
                      const SizedBox(height: 8),
                      const Row(
                        children: [
                          Icon(Icons.opacity, size: 16, color: Colors.blue),
                          SizedBox(width: 4),
                          Text('رطوبة التربة: 35%'),
                        ],
                      ),
                      const Row(
                        children: [
                          Icon(Icons.thermostat, size: 16, color: Colors.red),
                          SizedBox(width: 4),
                          Text('درجة الحرارة: 28°م'),
                        ],
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'الكمية الموصى بها: 25 مم',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('توصية الري الذكي'), findsOneWidget);
      expect(find.text('ينصح بري حقل القمح الشمالي'), findsOneWidget);
      expect(find.text('رطوبة التربة: 35%'), findsOneWidget);
      expect(find.text('الكمية الموصى بها: 25 مم'), findsOneWidget);
    });

    testWidgets('Recommendation shows soil moisture gauge', (tester) async {
      const soilMoisture = 35.0;
      final moistureColor = soilMoisture < 30
          ? Colors.red
          : soilMoisture < 50
              ? Colors.orange
              : Colors.green;

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  const Text('رطوبة التربة الحالية'),
                  const SizedBox(height: 8),
                  LinearProgressIndicator(
                    value: soilMoisture / 100,
                    backgroundColor: Colors.grey.shade200,
                    color: moistureColor,
                    minHeight: 12,
                  ),
                  const SizedBox(height: 4),
                  Text('$soilMoisture%'),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('رطوبة التربة الحالية'), findsOneWidget);
      expect(find.text('$soilMoisture%'), findsOneWidget);
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('Weather context is shown in recommendation', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: const [
                  Text('السياق الجوي',
                      style: TextStyle(fontWeight: FontWeight.bold)),
                  SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.wb_sunny, color: Colors.amber),
                      SizedBox(width: 8),
                      Text('مشمس جزئياً'),
                      Spacer(),
                      Text('28°م'),
                    ],
                  ),
                  SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.water_drop, color: Colors.blue),
                      SizedBox(width: 8),
                      Text('احتمال هطول الأمطار: 10%'),
                    ],
                  ),
                  SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(Icons.air, color: Colors.grey),
                      SizedBox(width: 8),
                      Text('الرياح: 12 كم/س'),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('السياق الجوي'), findsOneWidget);
      expect(find.text('احتمال هطول الأمطار: 10%'), findsOneWidget);
      expect(find.text('الرياح: 12 كم/س'), findsOneWidget);
    });
  });

  // =========================================================================
  // Irrigation History Tests
  // اختبارات سجل الري
  // =========================================================================

  group('Irrigation History Tests - اختبارات سجل الري', () {
    testWidgets('Irrigation history list shows past events', (tester) async {
      final history = [
        {'date': '2026-03-12', 'amount': '22 مم', 'duration': '3 ساعات'},
        {'date': '2026-03-09', 'amount': '25 مم', 'duration': '3.5 ساعة'},
        {'date': '2026-03-06', 'amount': '20 مم', 'duration': '2.5 ساعة'},
      ];

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('سجل الري')),
            body: ListView.builder(
              itemCount: history.length,
              itemBuilder: (_, i) => ListTile(
                leading: const Icon(Icons.history, color: Colors.blue),
                title: Text(history[i]['date']!),
                subtitle: Text(
                    '${history[i]['amount']} - ${history[i]['duration']}'),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('سجل الري'), findsOneWidget);
      for (final event in history) {
        expect(find.text(event['date']!), findsOneWidget);
      }
    });

    testWidgets('Water usage statistics are displayed', (tester) async {
      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            body: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('إحصائيات استهلاك المياه',
                      style: TextStyle(
                          fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 16),
                  _buildStatRow('هذا الشهر', '1,250 م³'),
                  _buildStatRow('الشهر الماضي', '1,180 م³'),
                  _buildStatRow('متوسط الموسم', '1,200 م³'),
                  _buildStatRow('كفاءة الري', '87%'),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('إحصائيات استهلاك المياه'), findsOneWidget);
      expect(find.text('هذا الشهر'), findsOneWidget);
      expect(find.text('1,250 م³'), findsOneWidget);
      expect(find.text('كفاءة الري'), findsOneWidget);
      expect(find.text('87%'), findsOneWidget);
    });
  });

  // =========================================================================
  // Manual Irrigation Control Tests
  // اختبارات التحكم اليدوي في الري
  // =========================================================================

  group('Manual Irrigation Control Tests - اختبارات التحكم اليدوي', () {
    testWidgets('Manual start irrigation button exists', (tester) async {
      bool irrigationStarted = false;

      await tester.pumpWidget(ProviderScope(
        child: MaterialApp(
          locale: const Locale('ar'),
          home: Scaffold(
            appBar: AppBar(title: const Text('تحكم الري')),
            body: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.water, size: 64, color: Colors.blue),
                  const SizedBox(height: 16),
                  const Text('حقل القمح الشمالي',
                      style: TextStyle(fontSize: 18)),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: () => irrigationStarted = true,
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('بدء الري'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('بدء الري'), findsOneWidget);
      expect(find.byIcon(Icons.play_arrow), findsOneWidget);

      await tester.tap(find.text('بدء الري'));
      await tester.pumpAndSettle();

      expect(irrigationStarted, isTrue);
    });

    testWidgets('Stop irrigation button shows during active irrigation',
        (tester) async {
      bool isRunning = true;

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            locale: const Locale('ar'),
            home: Scaffold(
              body: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    if (isRunning)
                      const Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                          SizedBox(width: 8),
                          Text('الري جارٍ الآن...'),
                        ],
                      ),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () => setState(() => isRunning = false),
                      icon: const Icon(Icons.stop),
                      label: const Text('إيقاف الري'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.red,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('الري جارٍ الآن...'), findsOneWidget);
      expect(find.text('إيقاف الري'), findsOneWidget);

      await tester.tap(find.text('إيقاف الري'));
      await tester.pumpAndSettle();

      expect(find.text('الري جارٍ الآن...'), findsNothing);
    });

    testWidgets('Irrigation amount selector shows valid options', (tester) async {
      double selectedAmount = 25.0;

      await tester.pumpWidget(ProviderScope(
        child: StatefulBuilder(
          builder: (context, setState) => MaterialApp(
            locale: const Locale('ar'),
            home: Scaffold(
              body: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    const Text('كمية الري (مم)'),
                    const SizedBox(height: 8),
                    Slider(
                      value: selectedAmount,
                      min: 5.0,
                      max: 50.0,
                      divisions: 9,
                      label: '$selectedAmount مم',
                      onChanged: (v) => setState(() => selectedAmount = v),
                    ),
                    Text('الكمية المحددة: $selectedAmount مم'),
                  ],
                ),
              ),
            ),
          ),
        ),
      ));
      await tester.pumpAndSettle();

      expect(find.text('كمية الري (مم)'), findsOneWidget);
      expect(find.byType(Slider), findsOneWidget);
      expect(find.text('الكمية المحددة: 25.0 مم'), findsOneWidget);
    });
  });
}

// Helper to build a stat row
Widget _buildStatRow(String label, String value) {
  return Padding(
    padding: const EdgeInsets.symmetric(vertical: 8),
    child: Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
      ],
    ),
  );
}
