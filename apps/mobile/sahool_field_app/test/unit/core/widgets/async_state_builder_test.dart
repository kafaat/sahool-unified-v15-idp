import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/widgets/async_state_builder.dart';

/// Helper to wrap widget with MaterialApp for testing
Widget _wrapWithApp(Widget child) {
  return MaterialApp(
    home: Scaffold(body: child),
    locale: const Locale('ar'),
    localizationsDelegates: const [
      DefaultMaterialLocalizations.delegate,
      DefaultWidgetsLocalizations.delegate,
    ],
  );
}

void main() {
  group('AsyncStateBuilder', () {
    testWidgets('should show loading state when isLoading and no data',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: true,
          data: null,
          dataBuilder: (data) => Text('Data: ${data.length}'),
          loadingBuilder: () => const Text('Loading...'),
          wrapWithErrorBoundary: false,
        ),
      ));

      expect(find.text('Loading...'), findsOneWidget);
      expect(find.text('Data: 0'), findsNothing);
    });

    testWidgets('should show data state when data is available',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: false,
          data: const ['a', 'b', 'c'],
          dataBuilder: (data) => Text('Data: ${data.length}'),
          wrapWithErrorBoundary: false,
        ),
      ));

      expect(find.text('Data: 3'), findsOneWidget);
    });

    testWidgets('should show error state when error and no data',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: false,
          error: 'Something went wrong',
          data: null,
          dataBuilder: (data) => Text('Data: ${data.length}'),
          errorBuilder: (error, retry) => Text('Error: $error'),
          wrapWithErrorBoundary: false,
        ),
      ));

      expect(find.text('Error: Something went wrong'), findsOneWidget);
    });

    testWidgets('should show empty state when data is empty list',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: false,
          data: const [],
          dataBuilder: (data) => Text('Data: ${data.length}'),
          emptyBuilder: () => const Text('No data found'),
          wrapWithErrorBoundary: false,
        ),
      ));

      expect(find.text('No data found'), findsOneWidget);
    });

    testWidgets('should show data over error when data exists', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: false,
          error: 'Some error',
          data: const ['item'],
          dataBuilder: (data) => Text('Data: ${data.length}'),
          errorBuilder: (error, retry) => Text('Error: $error'),
          wrapWithErrorBoundary: false,
        ),
      ));

      // Data takes priority over error when data exists
      expect(find.text('Data: 1'), findsOneWidget);
      expect(find.text('Error: Some error'), findsNothing);
    });

    testWidgets('should show refresh indicator over data when refreshing',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: false,
          isRefreshing: true,
          data: const ['item'],
          dataBuilder: (data) => Text('Data: ${data.length}'),
          wrapWithErrorBoundary: false,
        ),
      ));

      // Data should still be visible
      expect(find.text('Data: 1'), findsOneWidget);
      // LinearProgressIndicator should be shown
      expect(find.byType(LinearProgressIndicator), findsOneWidget);
    });

    testWidgets('should use custom isEmpty function', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<Map<String, int>>(
          isLoading: false,
          data: const {},
          isEmpty: (data) => data.isEmpty,
          dataBuilder: (data) => Text('Data: ${data.length}'),
          emptyBuilder: () => const Text('Map is empty'),
          wrapWithErrorBoundary: false,
        ),
      ));

      expect(find.text('Map is empty'), findsOneWidget);
    });

    testWidgets('should show default loading when no loadingBuilder',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<String>(
          isLoading: true,
          data: null,
          dataBuilder: (data) => Text(data),
          wrapWithErrorBoundary: false,
        ),
      ));

      // Default SahoolShimmerList should be rendered
      await tester.pump(const Duration(milliseconds: 100));
      // Just verify it doesn't crash
      expect(find.byType(AsyncStateBuilder<String>), findsOneWidget);
    });

    testWidgets('should pass retry callback to error builder', (tester) async {
      bool retried = false;

      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<String>(
          isLoading: false,
          error: 'fail',
          data: null,
          dataBuilder: (data) => Text(data),
          errorBuilder: (error, retry) => ElevatedButton(
            onPressed: retry,
            child: const Text('Retry'),
          ),
          onRetry: () => retried = true,
          wrapWithErrorBoundary: false,
        ),
      ));

      await tester.tap(find.text('Retry'));
      expect(retried, true);
    });

    testWidgets('should handle loading with empty list data', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        AsyncStateBuilder<List<String>>(
          isLoading: true,
          data: const [],
          dataBuilder: (data) => Text('Data: ${data.length}'),
          loadingBuilder: () => const Text('Loading...'),
          wrapWithErrorBoundary: false,
        ),
      ));

      // Empty list + loading = show loading
      expect(find.text('Loading...'), findsOneWidget);
    });
  });

  group('AsyncStateSliver', () {
    testWidgets('should show data in sliver context', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        CustomScrollView(
          slivers: [
            AsyncStateSliver<List<String>>(
              isLoading: false,
              data: const ['a', 'b'],
              dataBuilder: (data) => SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) => Text(data[index]),
                  childCount: data.length,
                ),
              ),
            ),
          ],
        ),
      ));

      expect(find.text('a'), findsOneWidget);
      expect(find.text('b'), findsOneWidget);
    });

    testWidgets('should show loading in sliver context', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        CustomScrollView(
          slivers: [
            AsyncStateSliver<String>(
              isLoading: true,
              data: null,
              dataBuilder: (data) => SliverToBoxAdapter(child: Text(data)),
              loadingBuilder: () => const Text('Sliver Loading'),
            ),
          ],
        ),
      ));

      expect(find.text('Sliver Loading'), findsOneWidget);
    });

    testWidgets('should show error in sliver context', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        CustomScrollView(
          slivers: [
            AsyncStateSliver<String>(
              isLoading: false,
              error: 'Sliver error',
              data: null,
              dataBuilder: (data) => SliverToBoxAdapter(child: Text(data)),
              errorBuilder: (error, retry) => Text('Error: $error'),
            ),
          ],
        ),
      ));

      expect(find.text('Error: Sliver error'), findsOneWidget);
    });
  });
}
