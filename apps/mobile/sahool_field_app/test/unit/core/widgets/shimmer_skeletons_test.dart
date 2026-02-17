import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/widgets/shimmer_skeletons.dart';

/// Helper to wrap widget with MaterialApp for testing
Widget _wrapWithApp(Widget child) {
  return MaterialApp(
    home: Scaffold(body: child),
  );
}

void main() {
  group('FieldCardSkeleton', () {
    testWidgets('should render full layout by default', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const FieldCardSkeleton(),
      ));

      // Should render without errors
      expect(find.byType(FieldCardSkeleton), findsOneWidget);
    });

    testWidgets('should render compact layout when isCompact is true',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const FieldCardSkeleton(isCompact: true),
      ));

      expect(find.byType(FieldCardSkeleton), findsOneWidget);
    });
  });

  group('FieldsListSkeleton', () {
    testWidgets('should render list of field card skeletons', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const FieldsListSkeleton(itemCount: 3),
      ));

      expect(find.byType(FieldsListSkeleton), findsOneWidget);
      expect(find.byType(FieldCardSkeleton), findsNWidgets(3));
    });

    testWidgets('should render grid when isGridView is true', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const FieldsListSkeleton(itemCount: 4, isGridView: true),
      ));

      expect(find.byType(GridView), findsOneWidget);
      expect(find.byType(FieldCardSkeleton), findsNWidgets(4));
    });

    testWidgets('should default to 5 items', (tester) async {
      // Use a tall surface to ensure all skeleton items are rendered
      tester.view.physicalSize = const Size(800, 3000);
      tester.view.devicePixelRatio = 1.0;
      addTearDown(tester.view.resetPhysicalSize);
      addTearDown(tester.view.resetDevicePixelRatio);

      await tester.pumpWidget(_wrapWithApp(
        const FieldsListSkeleton(),
      ));

      expect(find.byType(FieldCardSkeleton), findsNWidgets(5));
    });
  });

  group('TaskCardSkeleton', () {
    testWidgets('should render without errors', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const TaskCardSkeleton(),
      ));

      expect(find.byType(TaskCardSkeleton), findsOneWidget);
    });
  });

  group('TasksListSkeleton', () {
    testWidgets('should render list of task card skeletons', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const TasksListSkeleton(itemCount: 4),
      ));

      expect(find.byType(TasksListSkeleton), findsOneWidget);
      expect(find.byType(TaskCardSkeleton), findsNWidgets(4));
    });

    testWidgets('should default to 6 items', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const TasksListSkeleton(),
      ));

      expect(find.byType(TaskCardSkeleton), findsNWidgets(6));
    });
  });

  group('EquipmentCardSkeleton', () {
    testWidgets('should render without errors', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const EquipmentCardSkeleton(),
      ));

      expect(find.byType(EquipmentCardSkeleton), findsOneWidget);
    });
  });

  group('EquipmentListSkeleton', () {
    testWidgets('should render list of equipment card skeletons',
        (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const EquipmentListSkeleton(itemCount: 3),
      ));

      expect(find.byType(EquipmentListSkeleton), findsOneWidget);
      expect(find.byType(EquipmentCardSkeleton), findsNWidgets(3));
    });

    testWidgets('should default to 5 items', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const EquipmentListSkeleton(),
      ));

      expect(find.byType(EquipmentCardSkeleton), findsNWidgets(5));
    });
  });

  group('StatsBarSkeleton', () {
    testWidgets('should render with default 3 stat items', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const StatsBarSkeleton(),
      ));

      expect(find.byType(StatsBarSkeleton), findsOneWidget);
    });

    testWidgets('should render with custom item count', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const StatsBarSkeleton(itemCount: 4),
      ));

      expect(find.byType(StatsBarSkeleton), findsOneWidget);
    });
  });

  group('DetailScreenSkeleton', () {
    testWidgets('should render with default 3 sections', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const SingleChildScrollView(
          child: DetailScreenSkeleton(),
        ),
      ));

      expect(find.byType(DetailScreenSkeleton), findsOneWidget);
    });

    testWidgets('should render with custom section count', (tester) async {
      await tester.pumpWidget(_wrapWithApp(
        const SingleChildScrollView(
          child: DetailScreenSkeleton(sectionCount: 5),
        ),
      ));

      expect(find.byType(DetailScreenSkeleton), findsOneWidget);
    });
  });
}
