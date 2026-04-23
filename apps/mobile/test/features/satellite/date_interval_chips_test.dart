/// DateIntervalChips widget tests — pins the "every N days" cadence
/// selector that drives the filmstrip / composite / multi-compare
/// refetches across both the mobile map screen and the bottom sheet.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sahool_field_app/features/satellite/presentation/providers/filmstrip_provider.dart';
import 'package:sahool_field_app/features/satellite/widgets/date_interval_chips.dart';

void main() {
  Widget wrap(Widget child, {List<Override> overrides = const []}) {
    return ProviderScope(
      overrides: overrides,
      child: MaterialApp(
        home: Scaffold(body: child),
      ),
    );
  }

  testWidgets('renders the 4 canonical presets (3/7/14/30 days)', (tester) async {
    await tester.pumpWidget(wrap(const DateIntervalChips()));
    await tester.pumpAndSettle();

    expect(find.byKey(const Key('interval-step-3')), findsOneWidget);
    expect(find.byKey(const Key('interval-step-7')), findsOneWidget);
    expect(find.byKey(const Key('interval-step-14')), findsOneWidget);
    expect(find.byKey(const Key('interval-step-30')), findsOneWidget);
  });

  testWidgets('marks the default (weekly) as selected', (tester) async {
    await tester.pumpWidget(wrap(const DateIntervalChips()));
    await tester.pumpAndSettle();

    final weekly = tester.widget<ChoiceChip>(find.byKey(const Key('interval-step-7')));
    expect(weekly.selected, isTrue);
    final biweekly = tester.widget<ChoiceChip>(find.byKey(const Key('interval-step-14')));
    expect(biweekly.selected, isFalse);
  });

  testWidgets('tapping a chip writes through to intervalStepProvider', (tester) async {
    late ProviderContainer container;
    await tester.pumpWidget(
      ProviderScope(
        child: Consumer(
          builder: (ctx, ref, _) {
            container = ProviderScope.containerOf(ctx);
            return const MaterialApp(home: Scaffold(body: DateIntervalChips()));
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('interval-step-30')));
    await tester.pumpAndSettle();

    expect(container.read(intervalStepProvider), IntervalStep.monthly);
  });

  testWidgets('controlled mode — explicit value + onChanged bypass the provider',
      (tester) async {
    IntervalStep picked = IntervalStep.every3days;
    int callCount = 0;

    await tester.pumpWidget(
      wrap(
        DateIntervalChips(
          value: picked,
          onChanged: (v) {
            picked = v;
            callCount++;
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('interval-step-14')));
    await tester.pumpAndSettle();

    expect(callCount, 1);
    expect(picked, IntervalStep.biweekly);
  });

  testWidgets('does not fire onChanged when the active chip is re-tapped',
      (tester) async {
    int calls = 0;
    await tester.pumpWidget(
      wrap(
        DateIntervalChips(
          value: IntervalStep.weekly,
          onChanged: (_) => calls++,
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('interval-step-7')));
    await tester.pumpAndSettle();

    expect(calls, 0);
  });

  testWidgets('disabled=true suppresses every tap', (tester) async {
    int calls = 0;
    await tester.pumpWidget(
      wrap(
        DateIntervalChips(
          disabled: true,
          value: IntervalStep.weekly,
          onChanged: (_) => calls++,
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('interval-step-30')));
    await tester.pumpAndSettle();

    expect(calls, 0);
  });

  testWidgets('renders Arabic label by default and hides it when bilingual=false',
      (tester) async {
    await tester.pumpWidget(wrap(const DateIntervalChips()));
    await tester.pumpAndSettle();
    // weekly chip -> "1 week · أسبوع"
    expect(find.textContaining('أسبوع'), findsWidgets);

    await tester.pumpWidget(wrap(const DateIntervalChips(bilingual: false)));
    await tester.pumpAndSettle();
    expect(find.textContaining('أسبوع'), findsNothing);
  });

  test('IntervalStep.fromDays falls back to weekly on unknown input', () {
    expect(IntervalStep.fromDays(3), IntervalStep.every3days);
    expect(IntervalStep.fromDays(30), IntervalStep.monthly);
    expect(IntervalStep.fromDays(999), IntervalStep.weekly);
  });
}
