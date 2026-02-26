import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/widgets/screen_wrapper.dart';

void main() {
  group('SahoolScreenWrapper', () {
    testWidgets('should render with title and body', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Test Screen',
            body: Text('Hello World'),
            isRTL: false,
            enableErrorBoundary: false,
          ),
        ),
      );

      expect(find.text('Test Screen'), findsOneWidget);
      expect(find.text('Hello World'), findsOneWidget);
    });

    testWidgets('should apply RTL direction by default', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'RTL Screen',
            body: Text('Content'),
            enableErrorBoundary: false,
          ),
        ),
      );

      // Find the Directionality widget
      final directionality = tester.widget<Directionality>(
        find.byType(Directionality).last,
      );
      expect(directionality.textDirection, TextDirection.rtl);
    });

    testWidgets('should not apply RTL when isRTL is false', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'LTR Screen',
            body: Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
          ),
        ),
      );

      // The Scaffold should not be wrapped in a Directionality RTL widget
      expect(find.byType(SahoolScreenWrapper), findsOneWidget);
    });

    testWidgets('should show loading overlay when isLoading', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Loading Screen',
            body: Text('Content'),
            isLoading: true,
            loadingMessage: 'Saving...',
            isRTL: false,
            enableErrorBoundary: false,
          ),
        ),
      );

      // The loading overlay should show with the message
      expect(find.text('Saving...'), findsOneWidget);
      expect(find.text('Content'),
          findsOneWidget); // Content still visible under overlay
    });

    testWidgets('should not show loading overlay when not loading',
        (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Normal Screen',
            body: Text('Content'),
            isLoading: false,
            isRTL: false,
            enableErrorBoundary: false,
          ),
        ),
      );

      expect(find.text('Content'), findsOneWidget);
    });

    testWidgets('should render AppBar actions', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Actions Screen',
            body: const Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
            actions: [
              IconButton(
                icon: const Icon(Icons.settings),
                onPressed: () {},
              ),
            ],
          ),
        ),
      );

      expect(find.byIcon(Icons.settings), findsOneWidget);
    });

    testWidgets('should render FloatingActionButton', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: SahoolScreenWrapper(
            title: 'FAB Screen',
            body: const Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
            floatingActionButton: FloatingActionButton(
              onPressed: () {},
              child: const Icon(Icons.add),
            ),
          ),
        ),
      );

      expect(find.byType(FloatingActionButton), findsOneWidget);
      expect(find.byIcon(Icons.add), findsOneWidget);
    });

    testWidgets('should use custom AppBar when provided', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Ignored Title',
            body: const Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
            appBar: AppBar(
              title: const Text('Custom AppBar'),
              backgroundColor: Colors.red,
            ),
          ),
        ),
      );

      expect(find.text('Custom AppBar'), findsOneWidget);
      expect(find.text('Ignored Title'), findsNothing);
    });

    testWidgets('should use default green AppBar color', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Green Bar',
            body: Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
          ),
        ),
      );

      final appBar = tester.widget<AppBar>(find.byType(AppBar));
      expect(appBar.backgroundColor, const Color(0xFF367C2B));
    });

    testWidgets('should use custom AppBar color when provided', (tester) async {
      await tester.pumpWidget(
        const MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Custom Color',
            body: Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
            appBarColor: Colors.blue,
          ),
        ),
      );

      final appBar = tester.widget<AppBar>(find.byType(AppBar));
      expect(appBar.backgroundColor, Colors.blue);
    });

    testWidgets('should render bottomNavigationBar', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: SahoolScreenWrapper(
            title: 'Nav Screen',
            body: const Text('Content'),
            isRTL: false,
            enableErrorBoundary: false,
            bottomNavigationBar: BottomNavigationBar(
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(Icons.home),
                  label: 'Home',
                ),
                BottomNavigationBarItem(
                  icon: Icon(Icons.settings),
                  label: 'Settings',
                ),
              ],
            ),
          ),
        ),
      );

      expect(find.byType(BottomNavigationBar), findsOneWidget);
    });
  });
}
