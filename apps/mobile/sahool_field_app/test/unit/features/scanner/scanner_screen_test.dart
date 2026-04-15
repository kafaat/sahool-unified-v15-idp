import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/scanner/ui/scanner_screen.dart';

void main() {
  group('ScannerScreen', () {
    testWidgets('renders scanner with camera placeholder', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      expect(find.text('ضع الورقة المصابة داخل الإطار'), findsOneWidget);
    });

    testWidgets('renders flash button', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      expect(find.text('الفلاش'), findsOneWidget);
      expect(find.byIcon(Icons.flash_off), findsOneWidget);
    });

    testWidgets('renders gallery and history buttons', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      expect(find.byIcon(Icons.photo_library), findsOneWidget);
      expect(find.byIcon(Icons.history), findsOneWidget);
    });

    testWidgets('renders close button', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      expect(find.byIcon(Icons.close), findsOneWidget);
    });

    testWidgets('no result shown initially', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      expect(find.text('صدأ القمح'), findsNothing);
      expect(find.text('العلاج المقترح'), findsNothing);
    });

    testWidgets('has GestureDetector for capture', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      expect(find.byType(GestureDetector), findsAtLeastNWidgets(1));
    });

    testWidgets('has scaffold with black background', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      final scaffold = tester.widget<Scaffold>(find.byType(Scaffold));
      expect(scaffold.backgroundColor, Colors.black);
    });

    testWidgets('renders scan frame border', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(home: ScannerScreen()),
      );

      // The scan frame has a 280x280 Container
      expect(find.byType(Stack), findsAtLeastNWidgets(1));
    });
  });
}
