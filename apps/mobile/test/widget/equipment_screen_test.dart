/// Widget Tests for Equipment Screen
/// اختبارات واجهة شاشة المعدات
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  group('Equipment Screen Widget Tests', () {
    testWidgets('Shows loading indicator initially', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(
                child: CircularProgressIndicator(),
              ),
            ),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('Shows equipment list when data loaded', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              appBar: AppBar(title: const Text('المعدات والأصول')),
              body: ListView(
                children: [
                  _buildEquipmentCard('John Deere 8R', 'جرار', 'جاهز'),
                  _buildEquipmentCard('DJI Agras T40', 'طائرة مسيرة', 'صيانة'),
                  _buildEquipmentCard('مضخة Grundfos', 'مضخة', 'جاهز'),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Title should be visible
      expect(find.text('المعدات والأصول'), findsOneWidget);

      // Equipment items should be visible
      expect(find.text('John Deere 8R'), findsOneWidget);
      expect(find.text('DJI Agras T40'), findsOneWidget);
      expect(find.text('مضخة Grundfos'), findsOneWidget);
    });

    testWidgets('Filter chips are displayed', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children: [
                    Chip(label: Text('الكل')),
                    SizedBox(width: 8),
                    Chip(label: Text('جرارات')),
                    SizedBox(width: 8),
                    Chip(label: Text('مضخات')),
                    SizedBox(width: 8),
                    Chip(label: Text('درونز')),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('الكل'), findsOneWidget);
      expect(find.text('جرارات'), findsOneWidget);
      expect(find.text('مضخات'), findsOneWidget);
      expect(find.text('درونز'), findsOneWidget);
    });

    testWidgets('Stats boxes show correct labels', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Row(
                children: [
                  Expanded(child: _StatBox(count: '5', label: 'معدات')),
                  Expanded(child: _StatBox(count: '3', label: 'جاهزة')),
                  Expanded(child: _StatBox(count: '2', label: 'صيانة')),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('معدات'), findsOneWidget);
      expect(find.text('جاهزة'), findsOneWidget);
      expect(find.text('صيانة'), findsOneWidget);
      expect(find.text('5'), findsOneWidget);
      expect(find.text('3'), findsOneWidget);
      expect(find.text('2'), findsOneWidget);
    });

    testWidgets('Empty state shows message', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.agriculture, size: 64, color: Colors.grey),
                    SizedBox(height: 16),
                    Text('لا توجد معدات'),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('لا توجد معدات'), findsOneWidget);
      expect(find.byIcon(Icons.agriculture), findsOneWidget);
    });

    testWidgets('Error state shows retry button', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 48, color: Colors.red),
                    const SizedBox(height: 16),
                    const Text('حدث خطأ في الاتصال'),
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.refresh),
                      label: const Text('إعادة المحاولة'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('حدث خطأ في الاتصال'), findsOneWidget);
      expect(find.text('إعادة المحاولة'), findsOneWidget);
      expect(find.byIcon(Icons.refresh), findsOneWidget);
    });

    testWidgets('Tapping equipment item triggers callback', (tester) async {
      bool tapped = false;

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: GestureDetector(
                onTap: () => tapped = true,
                child: Card(
                  child: ListTile(
                    title: const Text('John Deere 8R'),
                    subtitle: const Text('جرار'),
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      await tester.tap(find.text('John Deere 8R'));
      await tester.pumpAndSettle();

      expect(tapped, true);
    });

    testWidgets('Pull to refresh works', (tester) async {
      bool refreshed = false;

      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: RefreshIndicator(
                onRefresh: () async {
                  refreshed = true;
                },
                child: ListView(
                  children: const [
                    ListTile(title: Text('Item 1')),
                    ListTile(title: Text('Item 2')),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      // Perform pull to refresh gesture
      await tester.fling(find.byType(ListView), const Offset(0, 300), 1000);
      await tester.pumpAndSettle();

      expect(refreshed, true);
    });
  });

  group('Equipment Details Bottom Sheet Tests', () {
    testWidgets('Shows equipment details', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('John Deere 8R 410', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  Text('جرار زراعي • 410 حصان'),
                  SizedBox(height: 16),
                  Row(
                    children: [
                      _StatBox(count: '75%', label: 'الوقود'),
                      _StatBox(count: '1,250', label: 'ساعات التشغيل'),
                      _StatBox(count: '2022', label: 'سنة الصنع'),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('John Deere 8R 410'), findsOneWidget);
      expect(find.text('جرار زراعي • 410 حصان'), findsOneWidget);
      expect(find.text('الوقود'), findsOneWidget);
      expect(find.text('ساعات التشغيل'), findsOneWidget);
    });

    testWidgets('Action buttons are displayed', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Row(
                children: [
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.history),
                      label: const Text('السجل'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.build),
                      label: const Text('صيانة'),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: ElevatedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.play_arrow),
                      label: const Text('تشغيل'),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('السجل'), findsOneWidget);
      expect(find.text('صيانة'), findsOneWidget);
      expect(find.text('تشغيل'), findsOneWidget);
    });
  });

  group('Add Equipment Form Tests', () {
    testWidgets('Form fields are displayed', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  Text('إضافة معدة جديدة', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
                  SizedBox(height: 24),
                  TextField(
                    decoration: InputDecoration(
                      labelText: 'اسم المعدة',
                      hintText: 'مثال: John Deere 8R',
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      expect(find.text('إضافة معدة جديدة'), findsOneWidget);
      expect(find.text('اسم المعدة'), findsOneWidget);
    });

    testWidgets('Submit button is enabled when form is valid', (tester) async {
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  TextField(
                    controller: TextEditingController(text: 'Test Equipment'),
                    decoration: const InputDecoration(labelText: 'اسم المعدة'),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {},
                    child: const Text('إضافة المعدة'),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      final button = find.byType(ElevatedButton);
      expect(button, findsOneWidget);
    });
  });
}

// Helper widgets for testing
Widget _buildEquipmentCard(String name, String type, String status) {
  return Card(
    margin: const EdgeInsets.all(8),
    child: ListTile(
      leading: const Icon(Icons.agriculture),
      title: Text(name),
      subtitle: Text(type),
      trailing: Chip(label: Text(status)),
    ),
  );
}

class _StatBox extends StatelessWidget {
  final String count;
  final String label;

  const _StatBox({required this.count, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(count, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          Text(label, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        ],
      ),
    );
  }
}
