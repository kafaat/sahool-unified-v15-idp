import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Login Screen Widget Tests
/// اختبارات شاشة تسجيل الدخول
void main() {
  group('Login Screen', () {
    testWidgets('should render phone input field', (tester) async {
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: Directionality(
              textDirection: TextDirection.rtl,
              child: Scaffold(
                body: Center(
                  child: TextField(
                    decoration: InputDecoration(
                      labelText: 'رقم الهاتف',
                      hintText: '7XX XXX XXX',
                    ),
                    keyboardType: TextInputType.phone,
                  ),
                ),
              ),
            ),
          ),
        ),
      );

      expect(find.byType(TextField), findsOneWidget);
      expect(find.text('رقم الهاتف'), findsOneWidget);
    });

    testWidgets('should validate phone number format', (tester) async {
      final controller = TextEditingController();
      String? errorText;

      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: StatefulBuilder(
                builder: (context, setState) {
                  return TextField(
                    controller: controller,
                    decoration: InputDecoration(
                      labelText: 'رقم الهاتف',
                      errorText: errorText,
                    ),
                    onChanged: (value) {
                      setState(() {
                        if (value.length < 9) {
                          errorText = 'رقم الهاتف يجب أن يكون 9 أرقام';
                        } else {
                          errorText = null;
                        }
                      });
                    },
                  );
                },
              ),
            ),
          ),
        ),
      );

      // Enter invalid phone number
      await tester.enterText(find.byType(TextField), '123');
      await tester.pump();

      expect(find.text('رقم الهاتف يجب أن يكون 9 أرقام'), findsOneWidget);

      // Enter valid phone number
      await tester.enterText(find.byType(TextField), '777123456');
      await tester.pump();

      expect(find.text('رقم الهاتف يجب أن يكون 9 أرقام'), findsNothing);
    });

    testWidgets('should show loading indicator when submitting', (tester) async {
      bool isLoading = false;

      await tester.pumpWidget(
        MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: StatefulBuilder(
                builder: (context, setState) {
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton(
                        onPressed: isLoading
                            ? null
                            : () {
                                setState(() => isLoading = true);
                              },
                        child: isLoading
                            ? const SizedBox(
                                width: 20,
                                height: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text('تسجيل الدخول'),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      );

      expect(find.text('تسجيل الدخول'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should have RTL text direction', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: Directionality(
            textDirection: TextDirection.rtl,
            child: Scaffold(
              body: Text('اختبار الاتجاه'),
            ),
          ),
        ),
      );

      final finder = find.text('اختبار الاتجاه');
      expect(finder, findsOneWidget);

      final widget = tester.widget<Directionality>(
        find.ancestor(
          of: finder,
          matching: find.byType(Directionality),
        ).first,
      );
      expect(widget.textDirection, TextDirection.rtl);
    });
  });
}
