import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/advisor/ui/advisor_screen.dart';
import '../../helpers/test_helpers.dart';

void main() {
  group('AdvisorScreen Widget', () {
    testWidgets('should display app bar with title', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.text('المستشار الذكي'), findsOneWidget);
    });

    testWidgets('should display initial welcome message', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.textContaining('مرحباً'), findsOneWidget);
      expect(find.textContaining('المستشار الزراعي الذكي'), findsOneWidget);
    });

    testWidgets('should show quick suggestion chips', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.text('متى أروي الحقل؟'), findsOneWidget);
      expect(find.text('الحقل يحتاج تسميد؟'), findsOneWidget);
      expect(find.text('رأيت آفة غريبة'), findsOneWidget);
    });

    testWidgets('should have text input field', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.byType(TextField), findsOneWidget);
      expect(find.text('اكتب رسالتك...'), findsOneWidget);
    });

    testWidgets('should have send button', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.byIcon(Icons.send), findsOneWidget);
    });

    testWidgets('should have microphone button', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.byIcon(Icons.mic), findsOneWidget);
    });

    testWidgets('should have camera button', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
    });

    testWidgets('should show connection status', (tester) async {
      await tester.pumpWidget(createSimpleTestableWidget(
        const AdvisorScreen(),
      ));

      expect(find.text('متصل'), findsOneWidget);
    });
  });
}
