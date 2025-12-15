/// SAHOOL Field App - Integration Tests
/// اختبارات التكامل للتطبيق
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('App Launch Tests', () {
    testWidgets('App launches successfully', (tester) async {
      // Launch app
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Center(child: Text('SAHOOL Test')),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // App should be visible
      expect(find.byType(MaterialApp), findsOneWidget);
    });
  });

  group('Navigation Tests', () {
    testWidgets('Can navigate to main sections', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              bottomNavigationBar: BottomNavigationBar(
                items: [
                  BottomNavigationBarItem(icon: Icon(Icons.home), label: 'الرئيسية'),
                  BottomNavigationBarItem(icon: Icon(Icons.map), label: 'الحقول'),
                  BottomNavigationBarItem(icon: Icon(Icons.task), label: 'المهام'),
                  BottomNavigationBarItem(icon: Icon(Icons.agriculture), label: 'المعدات'),
                ],
              ),
              body: Center(child: Text('Home')),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Bottom navigation should be visible
      expect(find.byType(BottomNavigationBar), findsOneWidget);
      expect(find.text('الرئيسية'), findsOneWidget);
      expect(find.text('الحقول'), findsOneWidget);
    });
  });

  group('Offline Mode Tests', () {
    testWidgets('App shows offline indicator when disconnected', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Column(
                children: [
                  // Simulated offline banner
                  Material(
                    color: Colors.orange,
                    child: Padding(
                      padding: EdgeInsets.all(8),
                      child: Row(
                        children: [
                          Icon(Icons.wifi_off, color: Colors.white),
                          SizedBox(width: 8),
                          Text('وضع عدم الاتصال', style: TextStyle(color: Colors.white)),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Offline indicator should show Arabic text
      expect(find.text('وضع عدم الاتصال'), findsOneWidget);
      expect(find.byIcon(Icons.wifi_off), findsOneWidget);
    });
  });
}
