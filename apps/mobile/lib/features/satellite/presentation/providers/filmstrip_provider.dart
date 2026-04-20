/// Filmstrip providers - مزوّدات شريط الصور
/// State management for the Phase-3 multi-date UX (filmstrip +
/// interval selector + composite/compare).
///
/// Parameterises `filmstripProvider` by (fieldId, indexName, stepDays)
/// so switching the interval or the active index is a hot cache-key
/// swap, not a re-mount. `selectedDateProvider` is the shared "which
/// date is active" bus that the map layer reads.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/models/index_filmstrip.dart';
import 'satellite_provider.dart';

/// Canonical cadence presets for [DateIntervalChips].
///
/// Matches the web `INTERVAL_PRESETS` chip group so mobile and web
/// users see identical options.
enum IntervalStep {
  every3days(3, '3 days', '٣ أيام'),
  weekly(7, '1 week', 'أسبوع'),
  biweekly(14, '2 weeks', 'أسبوعان'),
  monthly(30, '1 month', 'شهر');

  const IntervalStep(this.days, this.labelEn, this.labelAr);

  final int days;
  final String labelEn;
  final String labelAr;

  static IntervalStep fromDays(int days) {
    for (final step in values) {
      if (step.days == days) return step;
    }
    return IntervalStep.weekly;
  }
}

/// Currently-selected cadence. Shared across filmstrip + composite +
/// multi-date compare so the three views stay in sync.
final intervalStepProvider =
    StateProvider<IntervalStep>((ref) => IntervalStep.weekly);

/// Parameters for a single filmstrip fetch. Hashing by content, not
/// by instance — so Riverpod can de-dupe duplicate queries.
class FilmstripArgs {
  final String fieldId;
  final String indexName;
  final int stepDays;

  const FilmstripArgs({
    required this.fieldId,
    required this.indexName,
    this.stepDays = 7,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FilmstripArgs &&
          other.fieldId == fieldId &&
          other.indexName == indexName &&
          other.stepDays == stepDays;

  @override
  int get hashCode => Object.hash(fieldId, indexName, stepDays);
}

/// Fetches the filmstrip for (fieldId, indexName, stepDays). Re-uses
/// the existing `satelliteApiProvider` + auth token so the Phase-3
/// endpoints inherit the same Bearer forwarding as the rest of the app.
final filmstripProvider =
    FutureProvider.family.autoDispose<IndexFilmstrip, FilmstripArgs>(
  (ref, args) async {
    final api = ref.watch(satelliteApiProvider);
    return api.getIndexFilmstrip(
      args.fieldId,
      indexName: args.indexName,
      stepDays: args.stepDays,
    );
  },
);

/// Which date the map/chart view should show. `null` means "latest
/// available" — components fall back to the last frame in the
/// filmstrip. When the user taps a thumbnail, the sheet writes the
/// selection here and the primary map layer watches it.
final selectedDateProvider = StateProvider<DateTime?>((ref) => null);
