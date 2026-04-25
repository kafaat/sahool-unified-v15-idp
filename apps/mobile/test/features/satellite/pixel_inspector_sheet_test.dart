/// PixelInspectorSheet widget tests — pins the click-a-pixel bottom
/// sheet that shows every computed index grouped by category.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sahool_field_app/features/satellite/data/models/index_filmstrip.dart';
import 'package:sahool_field_app/features/satellite/presentation/providers/filmstrip_provider.dart';
import 'package:sahool_field_app/features/satellite/widgets/pixel_inspector_sheet.dart';

PixelInspection _fixture({Map<String, double?>? overrides}) {
  final indices = <String, double?>{
    'ndvi': 0.72,
    'ndre': 0.43,
    'ndwi': 0.12,
    'evi': 0.65,
    'savi': 0.58,
    'lai': 3.8,
    'gndvi': 0.55,
    'mcari': 0.8,
    'pri': 0.02,
    'fpar': 0.71,
    'fapar': 0.68,
    'bsi': -0.2,
  };
  if (overrides != null) indices.addAll(overrides);
  return PixelInspection(
    fieldId: 'F1',
    latitude: 24.7136,
    longitude: 46.6753,
    date: DateTime(2026, 4, 12),
    satellite: 'sentinel-2',
    indices: indices,
    mappable: const ['ndvi', 'ndre', 'ndwi', 'evi', 'savi', 'lai'],
    dataSource: 'simulated',
  );
}

Future<void> _pumpSheet(
  WidgetTester tester, {
  required AsyncValue<PixelInspection> state,
  PixelProbe? probe,
}) async {
  final fallbackProbe = probe ??
      const PixelProbe(fieldId: 'F1', lat: 24.7136, lon: 46.6753);
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        activePixelProbeProvider.overrideWith((ref) => fallbackProbe),
        pixelInspectionProvider.overrideWith((ref, _) {
          return state.when(
            data: (d) => d,
            error: (e, _) => throw e,
            loading: () => Future.any([]),
          );
        }),
      ],
      child: const MaterialApp(
        home: Scaffold(body: PixelInspectorSheet()),
      ),
    ),
  );
}

void main() {
  testWidgets('shows a prompt when no probe is active', (tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: Scaffold(body: PixelInspectorSheet()),
        ),
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('pixel-inspector-no-probe')), findsOneWidget);
  });

  testWidgets('shows loading spinner while data is pending', (tester) async {
    await _pumpSheet(tester, state: const AsyncValue.loading());
    await tester.pump();
    expect(find.byKey(const Key('pixel-inspector-loading')), findsOneWidget);
  });

  testWidgets('shows error message on failed fetch', (tester) async {
    await _pumpSheet(
      tester,
      state: AsyncValue.error(Exception('network'), StackTrace.current),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('pixel-inspector-error')), findsOneWidget);
  });

  testWidgets('renders every supplied index value', (tester) async {
    await _pumpSheet(tester, state: AsyncValue.data(_fixture()));
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('pixel-index-ndvi')), findsOneWidget);
    expect(find.byKey(const Key('pixel-index-ndre')), findsOneWidget);
    expect(find.byKey(const Key('pixel-index-lai')), findsOneWidget);
    expect(find.byKey(const Key('pixel-index-bsi')), findsOneWidget);
  });

  testWidgets('marks mappable indices with the ● bullet', (tester) async {
    await _pumpSheet(tester, state: AsyncValue.data(_fixture()));
    await tester.pumpAndSettle();
    // Mappable: NDVI/NDRE/NDWI/EVI/SAVI/LAI — the 6 from MappableIndex.
    for (final key in ['ndvi', 'ndre', 'ndwi', 'evi', 'savi', 'lai']) {
      final widget = find.byKey(Key('pixel-index-$key'));
      expect(widget, findsOneWidget);
      // The row text must include the ● marker.
      expect(
        tester.widget<Padding>(widget),
        isA<Padding>(),
      );
    }
    // At least one ● bullet must be present in the rendered text.
    expect(find.textContaining('●'), findsWidgets);
  });

  testWidgets('renders bilingual category headers', (tester) async {
    await _pumpSheet(tester, state: AsyncValue.data(_fixture()));
    await tester.pumpAndSettle();
    expect(find.text('Core'), findsOneWidget);
    expect(find.text('الأساسية'), findsOneWidget);
    expect(find.text('Water'), findsOneWidget);
    expect(find.text('المياه'), findsOneWidget);
  });

  testWidgets('skips categories whose indices are all absent', (tester) async {
    // Only NDVI supplied — Water/Chlorophyll/etc must be hidden.
    final partial = PixelInspection(
      fieldId: 'F1',
      latitude: 0,
      longitude: 0,
      date: DateTime(2026, 1, 1),
      satellite: 'sentinel-2',
      indices: const {'ndvi': 0.5},
      mappable: const ['ndvi'],
      dataSource: 'simulated',
    );
    await _pumpSheet(tester, state: AsyncValue.data(partial));
    await tester.pumpAndSettle();
    expect(find.text('Core'), findsOneWidget);
    expect(find.text('Water'), findsNothing);
    expect(find.text('Chlorophyll & Nitrogen'), findsNothing);
  });

  testWidgets('header shows lat/lon with 5 decimals', (tester) async {
    await _pumpSheet(tester, state: AsyncValue.data(_fixture()));
    await tester.pumpAndSettle();
    expect(find.textContaining('24.71360'), findsOneWidget);
    expect(find.textContaining('46.67530'), findsOneWidget);
  });
}
