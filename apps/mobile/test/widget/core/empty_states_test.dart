import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/widgets/empty_states.dart';
import '../../helpers/test_helpers.dart';

void main() {
  group('SahoolEmptyState', () {
    testWidgets('should display icon, title, and message', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolEmptyState(
            icon: Icons.inbox,
            title: 'عنوان فارغ',
            message: 'رسالة فارغة',
          ),
        ),
      );

      expect(find.byIcon(Icons.inbox), findsOneWidget);
      expect(find.text('عنوان فارغ'), findsOneWidget);
      expect(find.text('رسالة فارغة'), findsOneWidget);
    });

    testWidgets('should show action button when onAction provided', (tester) async {
      var buttonPressed = false;

      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolEmptyState(
            icon: Icons.add,
            title: 'Test',
            actionLabel: 'إضافة',
            onAction: () => buttonPressed = true,
          ),
        ),
      );

      expect(find.text('إضافة'), findsOneWidget);

      await tester.tap(find.text('إضافة'));
      await tester.pump();

      expect(buttonPressed, isTrue);
    });

    testWidgets('should not show action button when onAction is null', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolEmptyState(
            icon: Icons.inbox,
            title: 'Test',
          ),
        ),
      );

      expect(find.byType(ElevatedButton), findsNothing);
    });
  });

  group('Predefined Empty States', () {
    testWidgets('NoFieldsEmptyState should display correct content', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const NoFieldsEmptyState(),
        ),
      );

      expect(find.text('لا توجد حقول بعد'), findsOneWidget);
      expect(find.byIcon(Icons.grass_rounded), findsOneWidget);
    });

    testWidgets('NoTasksEmptyState should display correct content', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const NoTasksEmptyState(),
        ),
      );

      expect(find.text('لا توجد مهام'), findsOneWidget);
      expect(find.byIcon(Icons.task_alt_rounded), findsOneWidget);
    });

    testWidgets('NoAlertsEmptyState should display correct content', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const NoAlertsEmptyState(),
        ),
      );

      expect(find.text('لا توجد تنبيهات'), findsOneWidget);
      expect(find.byIcon(Icons.notifications_none_rounded), findsOneWidget);
    });

    testWidgets('NoSearchResultsEmptyState should show search query', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const NoSearchResultsEmptyState(
            searchQuery: 'قمح',
          ),
        ),
      );

      expect(find.text('لا توجد نتائج'), findsOneWidget);
      expect(find.textContaining('قمح'), findsOneWidget);
    });

    testWidgets('OfflineEmptyState should display offline message', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const OfflineEmptyState(),
        ),
      );

      expect(find.text('أنت غير متصل'), findsOneWidget);
      expect(find.byIcon(Icons.cloud_off_rounded), findsOneWidget);
    });

    testWidgets('ComingSoonEmptyState should show feature name', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const ComingSoonEmptyState(
            featureName: 'الواقع المعزز',
          ),
        ),
      );

      expect(find.text('قريباً'), findsOneWidget);
      expect(find.textContaining('الواقع المعزز'), findsOneWidget);
    });
  });

  group('SahoolCompactEmptyState', () {
    testWidgets('should display icon and message', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolCompactEmptyState(
            icon: Icons.list,
            message: 'لا توجد عناصر',
          ),
        ),
      );

      expect(find.byIcon(Icons.list), findsOneWidget);
      expect(find.text('لا توجد عناصر'), findsOneWidget);
    });

    testWidgets('should show action when provided', (tester) async {
      var pressed = false;

      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolCompactEmptyState(
            icon: Icons.add,
            message: 'Test',
            actionLabel: 'إضافة عنصر',
            onAction: () => pressed = true,
          ),
        ),
      );

      expect(find.text('إضافة عنصر'), findsOneWidget);

      await tester.tap(find.text('إضافة عنصر'));
      await tester.pump();

      expect(pressed, isTrue);
    });
  });
}
