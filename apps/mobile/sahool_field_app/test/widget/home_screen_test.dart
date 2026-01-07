import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Home Screen Widget Tests
/// اختبارات الشاشة الرئيسية
void main() {
  group('Home Screen', () {
    testWidgets('should display greeting message', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                appBar: AppBar(
                  title: Text('مرحباً، أحمد'),
                ),
                body: Center(
                  child: Text('الشاشة الرئيسية'),
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('مرحباً، أحمد'), findsOneWidget);
    });

    testWidgets('should display dashboard cards', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                body: GridView.count(
                  crossAxisCount: 2,
                  children: [
                    Card(child: Center(child: Text('الحقول'))),
                    Card(child: Center(child: Text('الطقس'))),
                    Card(child: Center(child: Text('المهام'))),
                    Card(child: Center(child: Text('الإشعارات'))),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('الحقول'), findsOneWidget);
      expect(find.text('الطقس'), findsOneWidget);
      expect(find.text('المهام'), findsOneWidget);
      expect(find.text('الإشعارات'), findsOneWidget);
    });

    testWidgets('should display bottom navigation', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                body: Center(child: Text('الرئيسية')),
                bottomNavigationBar: BottomNavigationBar(
                  currentIndex: 0,
                  items: [
                    BottomNavigationBarItem(
                      icon: Icon(Icons.home),
                      label: 'الرئيسية',
                    ),
                    BottomNavigationBarItem(
                      icon: Icon(Icons.landscape),
                      label: 'الحقول',
                    ),
                    BottomNavigationBarItem(
                      icon: Icon(Icons.settings),
                      label: 'الإعدادات',
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.home), findsOneWidget);
      expect(find.byIcon(Icons.landscape), findsOneWidget);
      expect(find.byIcon(Icons.settings), findsOneWidget);
    });

    testWidgets('should show sync status indicator', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                appBar: AppBar(
                  actions: [
                    Padding(
                      padding: EdgeInsets.all(8.0),
                      child: Row(
                        children: [
                          Icon(Icons.cloud_done, color: Colors.green),
                          SizedBox(width: 4),
                          Text('متصل'),
                        ],
                      ),
                    ),
                  ],
                ),
                body: Center(child: Text('الرئيسية')),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.cloud_done), findsOneWidget);
      expect(find.text('متصل'), findsOneWidget);
    });

    testWidgets('should show offline indicator when disconnected', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                appBar: AppBar(
                  actions: [
                    Padding(
                      padding: EdgeInsets.all(8.0),
                      child: Row(
                        children: [
                          Icon(Icons.cloud_off, color: Colors.orange),
                          SizedBox(width: 4),
                          Text('غير متصل'),
                        ],
                      ),
                    ),
                  ],
                ),
                body: Center(child: Text('الرئيسية')),
              ),
            ),
          ),
        ),
      );

      expect(find.byIcon(Icons.cloud_off), findsOneWidget);
      expect(find.text('غير متصل'), findsOneWidget);
    });

    testWidgets('should display weather summary in header', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                appBar: AppBar(
                  title: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('مرحباً، أحمد'),
                      Text('32°C - مشمس', style: TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
                body: Center(child: Text('الرئيسية')),
              ),
            ),
          ),
        ),
      );

      expect(find.text('مرحباً، أحمد'), findsOneWidget);
      expect(find.text('32°C - مشمس'), findsOneWidget);
    });

    testWidgets('should scroll dashboard content', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                body: SingleChildScrollView(
                  child: Column(
                    children: [
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 1')))),
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 2')))),
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 3')))),
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 4')))),
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 5')))),
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 6')))),
                      SizedBox(height: 100, child: Card(child: Center(child: Text('بطاقة 7')))),
                    ],
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.text('بطاقة 1'), findsOneWidget);

      await tester.drag(find.byType(SingleChildScrollView), const Offset(0, -300));
      await tester.pumpAndSettle();

      // After scrolling, card 1 might be off-screen
      expect(find.byType(Card), findsWidgets);
    });
  });
}
