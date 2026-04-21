/// IndexPicker widget tests — pins the "switch the active overlay"
/// UX across the 6 mappable indices.
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:sahool_field_app/features/satellite/presentation/providers/filmstrip_provider.dart';
import 'package:sahool_field_app/features/satellite/widgets/index_picker.dart';

void main() {
  Widget wrap(Widget child, {List<Override> overrides = const []}) {
    return ProviderScope(
      overrides: overrides,
      child: MaterialApp(home: Scaffold(body: child)),
    );
  }

  testWidgets('renders all 6 mappable indices', (tester) async {
    await tester.pumpWidget(wrap(const IndexPicker()));
    await tester.pumpAndSettle();

    for (final idx in MappableIndex.values) {
      expect(
        find.byKey(Key('index-picker-${idx.apiName}')),
        findsOneWidget,
        reason: '${idx.apiName} chip missing',
      );
    }
  });

  testWidgets('marks NDVI as the default selection', (tester) async {
    await tester.pumpWidget(wrap(const IndexPicker()));
    await tester.pumpAndSettle();

    final ndviChip =
        tester.widget<ChoiceChip>(find.byKey(const Key('index-picker-ndvi')));
    final ndreChip =
        tester.widget<ChoiceChip>(find.byKey(const Key('index-picker-ndre')));
    expect(ndviChip.selected, isTrue);
    expect(ndreChip.selected, isFalse);
  });

  testWidgets('tapping a chip writes through to selectedIndexProvider',
      (tester) async {
    late ProviderContainer container;
    await tester.pumpWidget(
      ProviderScope(
        child: Consumer(
          builder: (ctx, ref, _) {
            container = ProviderScope.containerOf(ctx);
            return const MaterialApp(home: Scaffold(body: IndexPicker()));
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('index-picker-ndre')));
    await tester.pumpAndSettle();

    expect(container.read(selectedIndexProvider), MappableIndex.ndre);
  });

  testWidgets('controlled mode — explicit value + onChanged bypass the provider',
      (tester) async {
    MappableIndex picked = MappableIndex.ndvi;
    int calls = 0;
    await tester.pumpWidget(
      wrap(
        IndexPicker(
          value: picked,
          onChanged: (v) {
            picked = v;
            calls++;
          },
        ),
      ),
    );
    await tester.pumpAndSettle();

    // LAI is the 6th chip and sits past the 800-px test viewport width
    // (empirically at x≈1423). Scroll the horizontal chip strip so the
    // hit-test registers; without this, `tester.tap` logs
    // "Offset (…, …) is outside the bounds of the root of the render
    // tree" and silently drops the event.
    final laiChip = find.byKey(const Key('index-picker-lai'));
    await tester.ensureVisible(laiChip);
    await tester.pumpAndSettle();
    await tester.tap(laiChip);
    await tester.pumpAndSettle();

    expect(calls, 1);
    expect(picked, MappableIndex.lai);
  });

  testWidgets('does not fire onChanged when the active chip is tapped',
      (tester) async {
    int calls = 0;
    await tester.pumpWidget(
      wrap(
        IndexPicker(
          value: MappableIndex.ndvi,
          onChanged: (_) => calls++,
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('index-picker-ndvi')));
    await tester.pumpAndSettle();

    expect(calls, 0);
  });

  testWidgets('disabled=true suppresses every tap', (tester) async {
    int calls = 0;
    await tester.pumpWidget(
      wrap(
        IndexPicker(
          disabled: true,
          value: MappableIndex.ndvi,
          onChanged: (_) => calls++,
        ),
      ),
    );
    await tester.pumpAndSettle();

    await tester.tap(find.byKey(const Key('index-picker-ndre')));
    await tester.pumpAndSettle();

    expect(calls, 0);
  });

  testWidgets('bilingual=false hides the Arabic label', (tester) async {
    await tester.pumpWidget(wrap(const IndexPicker()));
    await tester.pumpAndSettle();
    expect(find.textContaining('كثافة'), findsOneWidget);

    await tester.pumpWidget(wrap(const IndexPicker(bilingual: false)));
    await tester.pumpAndSettle();
    expect(find.textContaining('كثافة'), findsNothing);
  });

  test('MappableIndex.fromName is case-insensitive and has a safe fallback', () {
    expect(MappableIndex.fromName('NDRE'), MappableIndex.ndre);
    expect(MappableIndex.fromName('lai'), MappableIndex.lai);
    expect(MappableIndex.fromName('bogus'), MappableIndex.ndvi);
  });
}
