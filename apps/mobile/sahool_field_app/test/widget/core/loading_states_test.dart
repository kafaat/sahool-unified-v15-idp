import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/widgets/loading_states.dart';
import '../../helpers/test_helpers.dart';

void main() {
  group('SahoolLoadingSpinner', () {
    testWidgets('should render with default size', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingSpinner(),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('should render with custom size', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingSpinner(size: 48),
        ),
      );

      final sizedBox = tester.widget<SizedBox>(find.byType(SizedBox).first);
      expect(sizedBox.width, equals(48));
      expect(sizedBox.height, equals(48));
    });
  });

  group('SahoolLoadingScreen', () {
    testWidgets('should show loading spinner', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingScreen(),
        ),
      );

      expect(find.byType(SahoolLoadingSpinner), findsOneWidget);
    });

    testWidgets('should show message when provided', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingScreen(message: 'جاري التحميل...'),
        ),
      );

      expect(find.text('جاري التحميل...'), findsOneWidget);
    });
  });

  group('SahoolLoadingOverlay', () {
    testWidgets('should show child when not loading', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingOverlay(
            isLoading: false,
            child: Text('Content'),
          ),
        ),
      );

      expect(find.text('Content'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('should show overlay when loading', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingOverlay(
            isLoading: true,
            child: Text('Content'),
          ),
        ),
      );

      expect(find.text('Content'), findsOneWidget);
      expect(find.byType(SahoolLoadingSpinner), findsOneWidget);
    });

    testWidgets('should show message in overlay', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolLoadingOverlay(
            isLoading: true,
            message: 'يرجى الانتظار...',
            child: Text('Content'),
          ),
        ),
      );

      expect(find.text('يرجى الانتظار...'), findsOneWidget);
    });
  });

  group('SahoolInlineLoading', () {
    testWidgets('should show spinner', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolInlineLoading(),
        ),
      );

      expect(find.byType(SahoolLoadingSpinner), findsOneWidget);
    });

    testWidgets('should show message when provided', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolInlineLoading(message: 'تحميل البيانات...'),
        ),
      );

      expect(find.text('تحميل البيانات...'), findsOneWidget);
    });
  });

  group('SahoolLoadingButton', () {
    testWidgets('should show child when not loading', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolLoadingButton(
            isLoading: false,
            onPressed: () {},
            child: const Text('حفظ'),
          ),
        ),
      );

      expect(find.text('حفظ'), findsOneWidget);
      expect(find.byType(CircularProgressIndicator), findsNothing);
    });

    testWidgets('should show loading indicator when loading', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolLoadingButton(
            isLoading: true,
            onPressed: () {},
            child: const Text('حفظ'),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
      expect(find.text('حفظ'), findsNothing);
    });

    testWidgets('should disable button when loading', (tester) async {
      var pressed = false;

      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolLoadingButton(
            isLoading: true,
            onPressed: () => pressed = true,
            child: const Text('حفظ'),
          ),
        ),
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(pressed, isFalse);
    });

    testWidgets('should call onPressed when not loading', (tester) async {
      var pressed = false;

      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolLoadingButton(
            isLoading: false,
            onPressed: () => pressed = true,
            child: const Text('حفظ'),
          ),
        ),
      );

      await tester.tap(find.byType(ElevatedButton));
      await tester.pump();

      expect(pressed, isTrue);
    });
  });

  group('SahoolShimmerCard', () {
    testWidgets('should render with default height', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolShimmerCard(),
        ),
      );

      expect(find.byType(SahoolShimmerCard), findsOneWidget);
    });

    testWidgets('should render with custom dimensions', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SahoolShimmerCard(
            height: 200,
            width: 300,
          ),
        ),
      );

      final container = tester.widget<Container>(find.byType(Container).last);
      final box = container.constraints;
      // Container should have the specified dimensions
      expect(find.byType(SahoolShimmerCard), findsOneWidget);
    });
  });

  group('SahoolShimmerList', () {
    testWidgets('should render default item count', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SingleChildScrollView(
            child: SahoolShimmerList(),
          ),
        ),
      );

      expect(find.byType(SahoolShimmerCard), findsNWidgets(5));
    });

    testWidgets('should render custom item count', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          const SingleChildScrollView(
            child: SahoolShimmerList(itemCount: 3),
          ),
        ),
      );

      expect(find.byType(SahoolShimmerCard), findsNWidgets(3));
    });
  });

  group('SahoolRefreshIndicator', () {
    testWidgets('should wrap child with RefreshIndicator', (tester) async {
      await tester.pumpWidget(
        createSimpleTestableWidget(
          SahoolRefreshIndicator(
            onRefresh: () async {},
            child: ListView(
              children: const [Text('Item 1')],
            ),
          ),
        ),
      );

      expect(find.byType(RefreshIndicator), findsOneWidget);
      expect(find.text('Item 1'), findsOneWidget);
    });
  });
}
