/// IndexTimeSlider widget tests — pins the unified time-scrubber that
/// drives the active date across the map layer, legend, and inspector.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sahool_field_app/features/satellite/presentation/providers/filmstrip_provider.dart';
import 'package:sahool_field_app/features/satellite/widgets/index_time_slider.dart';

final _dates = [
  DateTime(2026, 1, 5),
  DateTime(2026, 2, 10),
  DateTime(2026, 3, 20),
  DateTime(2026, 4, 12),
];

Widget _wrap(Widget child, {List<Override> overrides = const []}) {
  return ProviderScope(
    overrides: overrides,
    child: MaterialApp(home: Scaffold(body: child)),
  );
}

void main() {
  testWidgets('renders empty state when dates is empty', (tester) async {
    await tester.pumpWidget(
      _wrap(IndexTimeSlider(dates: const [], onChanged: (_) {})),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('index-time-slider-empty')), findsOneWidget);
  });

  testWidgets('renders prev/next + slider when dates exist', (tester) async {
    await tester.pumpWidget(
      _wrap(IndexTimeSlider(dates: _dates, value: _dates[2])),
    );
    await tester.pumpAndSettle();
    expect(find.byKey(const Key('index-time-prev')), findsOneWidget);
    expect(find.byKey(const Key('index-time-next')), findsOneWidget);
    expect(find.byKey(const Key('index-time-range')), findsOneWidget);
  });

  testWidgets('disables prev at first date and next at last date',
      (tester) async {
    await tester.pumpWidget(
      _wrap(IndexTimeSlider(dates: _dates, value: _dates.first)),
    );
    await tester.pumpAndSettle();
    final prev =
        tester.widget<IconButton>(find.byKey(const Key('index-time-prev')));
    expect(prev.onPressed, isNull);

    await tester.pumpWidget(
      _wrap(IndexTimeSlider(dates: _dates, value: _dates.last)),
    );
    await tester.pumpAndSettle();
    final next =
        tester.widget<IconButton>(find.byKey(const Key('index-time-next')));
    expect(next.onPressed, isNull);
  });

  testWidgets('next button moves forward one acquisition', (tester) async {
    DateTime? latest;
    await tester.pumpWidget(
      _wrap(
        IndexTimeSlider(
          dates: _dates,
          value: _dates[1],
          onChanged: (d) => latest = d,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('index-time-next')));
    await tester.pumpAndSettle();
    expect(latest, _dates[2]);
  });

  testWidgets('prev button moves backward one acquisition', (tester) async {
    DateTime? latest;
    await tester.pumpWidget(
      _wrap(
        IndexTimeSlider(
          dates: _dates,
          value: _dates[2],
          onChanged: (d) => latest = d,
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('index-time-prev')));
    await tester.pumpAndSettle();
    expect(latest, _dates[1]);
  });

  testWidgets('writes through to selectedDateProvider when onChanged is null',
      (tester) async {
    late ProviderContainer container;
    await tester.pumpWidget(
      ProviderScope(
        child: Consumer(
          builder: (ctx, ref, _) {
            container = ProviderScope.containerOf(ctx);
            return MaterialApp(
              home: Scaffold(
                body: IndexTimeSlider(dates: _dates, value: _dates[1]),
              ),
            );
          },
        ),
      ),
    );
    await tester.pumpAndSettle();
    await tester.tap(find.byKey(const Key('index-time-next')));
    await tester.pumpAndSettle();
    expect(container.read(selectedDateProvider), _dates[2]);
  });

  testWidgets('unordered dates prop is sorted internally', (tester) async {
    DateTime? latest;
    final shuffled = [_dates[2], _dates[0], _dates[3], _dates[1]];
    await tester.pumpWidget(
      _wrap(
        IndexTimeSlider(
          dates: shuffled,
          value: _dates.first,
          onChanged: (d) => latest = d,
        ),
      ),
    );
    await tester.pumpAndSettle();
    // "Next" from the earliest date must go to the 2nd earliest, not
    // to whatever is next in the input array.
    await tester.tap(find.byKey(const Key('index-time-next')));
    await tester.pumpAndSettle();
    expect(latest, _dates[1]);
  });

  testWidgets('disabled=true suppresses all navigation', (tester) async {
    int calls = 0;
    await tester.pumpWidget(
      _wrap(
        IndexTimeSlider(
          dates: _dates,
          value: _dates[1],
          disabled: true,
          onChanged: (_) => calls++,
        ),
      ),
    );
    await tester.pumpAndSettle();
    // Both buttons must be disabled; tapping them is a no-op.
    final next =
        tester.widget<IconButton>(find.byKey(const Key('index-time-next')));
    final prev =
        tester.widget<IconButton>(find.byKey(const Key('index-time-prev')));
    expect(next.onPressed, isNull);
    expect(prev.onPressed, isNull);
    expect(calls, 0);
  });

  testWidgets('current date label updates as the selection changes',
      (tester) async {
    await tester.pumpWidget(
      _wrap(IndexTimeSlider(dates: _dates, value: _dates.first)),
    );
    await tester.pumpAndSettle();
    expect(
      (tester.widget<Text>(find.byKey(const Key('index-time-current'))).data),
      contains('Jan'),
    );

    await tester.pumpWidget(
      _wrap(IndexTimeSlider(dates: _dates, value: _dates.last)),
    );
    await tester.pumpAndSettle();
    expect(
      (tester.widget<Text>(find.byKey(const Key('index-time-current'))).data),
      contains('Apr'),
    );
  });
}
