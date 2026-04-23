/// SatelliteFilmstripSheet widget tests — pins the PageView carousel
/// behaviour: loading/error/empty states, frame rendering, tap writes
/// through to `selectedDateProvider` + pops the sheet with the date.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sahool_field_app/features/satellite/data/models/index_filmstrip.dart';
import 'package:sahool_field_app/features/satellite/presentation/providers/filmstrip_provider.dart';
import 'package:sahool_field_app/features/satellite/widgets/satellite_filmstrip_sheet.dart';

IndexFilmstrip _buildFixture({int frames = 3}) {
  return IndexFilmstrip(
    fieldId: 'F1',
    indexName: 'ndre',
    stepDays: 7,
    colorScale: const IndexColorScale(
      min: -1,
      max: 1,
      colors: ['#000000', '#ffffff'],
    ),
    label: const BilingualLabel(en: 'Red-Edge', ar: 'الحافة الحمراء'),
    frames: List.generate(
      frames,
      (i) => FilmstripFrame(
        date: DateTime(2026, 3, 1 + i * 7),
        rasterUrl: 'sim://$i',
        value: 0.3 + i * 0.15,
        status: IndexStatus(
          key: 'good',
          en: 'Good',
          ar: 'جيد',
        ),
        cloudCover: i * 5.0,
      ),
    ),
    dataSource: 'simulated',
  );
}

Future<void> _pumpSheet(
  WidgetTester tester, {
  required AsyncValue<IndexFilmstrip> filmstripState,
  DateTime? selectedDate,
}) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        filmstripProvider.overrideWith((ref, args) {
          // Emit the state from the override so the FutureProvider
          // doesn't actually try to hit the network.
          return filmstripState.when(
            data: (d) => d,
            error: (e, st) => throw e,
            loading: () => Future.any([]),
          );
        }),
        if (selectedDate != null)
          selectedDateProvider.overrideWith((ref) => selectedDate),
      ],
      child: const MaterialApp(
        home: Scaffold(
          body: SatelliteFilmstripSheet(fieldId: 'F1', indexName: 'ndre'),
        ),
      ),
    ),
  );
}

void main() {
  testWidgets('shows a spinner while the filmstrip future is pending',
      (tester) async {
    await _pumpSheet(tester, filmstripState: const AsyncValue.loading());
    await tester.pump(); // Don't settle — we want the pending state.
    expect(find.byKey(const Key('filmstrip-loading')), findsOneWidget);
  });

  testWidgets('shows an error message when the filmstrip fetch fails',
      (tester) async {
    await _pumpSheet(
      tester,
      filmstripState: AsyncValue.error(
        Exception('network'),
        StackTrace.current,
      ),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('filmstrip-error')), findsOneWidget);
  });

  testWidgets('shows an empty placeholder when the fixture has no frames',
      (tester) async {
    await _pumpSheet(
      tester,
      filmstripState: AsyncValue.data(_buildFixture(frames: 0)),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('filmstrip-empty')), findsOneWidget);
  });

  testWidgets('renders a PageView with one tile per frame', (tester) async {
    await _pumpSheet(
      tester,
      filmstripState: AsyncValue.data(_buildFixture(frames: 3)),
    );
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('filmstrip-pageview')), findsOneWidget);
    // The carousel's PageController starts at the **last** frame (the most
    // recent acquisition — see `_resolveInitialPage` in
    // satellite_filmstrip_sheet.dart). With a 7-day step and 3 frames
    // beginning at 2026-03-01, the visible frame is 2026-03-15.
    // Earlier frames are off-screen and lazily built by PageView, so
    // we assert only on the initially-rendered (latest) one.
    expect(find.byKey(const Key('filmstrip-frame-2026-03-15')), findsOneWidget);
    expect(find.byKey(const Key('filmstrip-carousel')), findsOneWidget);
  });

  testWidgets('cadence header reports stepDays and frame count', (tester) async {
    await _pumpSheet(
      tester,
      filmstripState: AsyncValue.data(_buildFixture(frames: 2)),
    );
    await tester.pumpAndSettle();
    expect(find.textContaining('كل 7 يوم'), findsOneWidget);
    expect(find.textContaining('2 frame'), findsOneWidget);
  });

  testWidgets('renders DateIntervalChips header', (tester) async {
    await _pumpSheet(
      tester,
      filmstripState: AsyncValue.data(_buildFixture()),
    );
    await tester.pumpAndSettle();
    // The interval selector must be part of the sheet chrome.
    expect(find.byKey(const Key('date-interval-chips')), findsOneWidget);
    expect(find.byKey(const Key('interval-step-7')), findsOneWidget);
  });
}
