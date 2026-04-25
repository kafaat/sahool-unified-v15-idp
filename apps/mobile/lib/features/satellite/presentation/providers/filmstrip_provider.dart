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

/// The 6 indices the backend has raster tiles + colour ramps for.
/// Kept as a typed enum so pickers + legends + map overlays all
/// agree — any new index added on the backend goes here first.
///
/// Labels stay co-located with the enum so the picker widget doesn't
/// need a parallel copy map.
enum MappableIndex {
  ndvi('NDVI', 'كثافة الغطاء', 0xff22c55e),
  ndre('NDRE', 'الكلوروفيل', 0xff15803d),
  ndwi('NDWI', 'محتوى الماء', 0xff0ea5e9),
  evi('EVI', 'محسّن', 0xff65a30d),
  savi('SAVI', 'مُعدَّل للتربة', 0xffca8a04),
  lai('LAI', 'مساحة الأوراق', 0xff166534);

  const MappableIndex(this.labelEn, this.labelAr, this.swatchArgb);

  final String labelEn;
  final String labelAr;
  final int swatchArgb;

  String get apiName => name; // enum `name` is already lowercase

  static MappableIndex fromName(String raw) {
    for (final m in values) {
      if (m.name == raw.toLowerCase()) return m;
    }
    return MappableIndex.ndvi;
  }
}

/// Currently-selected mappable index. Drives the tile overlay picker,
/// the legend, the filmstrip, and the pixel-inspector popup label.
final selectedIndexProvider =
    StateProvider<MappableIndex>((ref) => MappableIndex.ndvi);

/// Parameters for an `IndexMapData` fetch. Content-equatable so
/// Riverpod de-dupes identical queries.
class IndexMapArgs {
  final String fieldId;
  final MappableIndex index;
  final DateTime? date;

  const IndexMapArgs({
    required this.fieldId,
    required this.index,
    this.date,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is IndexMapArgs &&
          other.fieldId == fieldId &&
          other.index == index &&
          other.date == date;

  @override
  int get hashCode => Object.hash(fieldId, index, date);
}

/// Raster-tile metadata for (fieldId, index, date).
final indexMapProvider =
    FutureProvider.family.autoDispose<IndexMapData, IndexMapArgs>(
  (ref, args) async {
    final api = ref.watch(satelliteApiProvider);
    return api.getIndexMap(
      args.fieldId,
      indexName: args.index.apiName,
      date: args.date,
    );
  },
);

/// A single clicked pixel. When set, the pixel-inspector sheet becomes
/// visible; setting back to null dismisses it.
class PixelProbe {
  final String fieldId;
  final double lat;
  final double lon;
  final DateTime? date;

  const PixelProbe({
    required this.fieldId,
    required this.lat,
    required this.lon,
    this.date,
  });

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PixelProbe &&
          other.fieldId == fieldId &&
          other.lat == lat &&
          other.lon == lon &&
          other.date == date;

  @override
  int get hashCode => Object.hash(fieldId, lat, lon, date);
}

/// Shared "which pixel is the user inspecting" bus. Null means no
/// inspection active.
final activePixelProbeProvider = StateProvider<PixelProbe?>((ref) => null);

/// Pixel inspection fetch keyed by probe. autoDispose so the query is
/// torn down the moment the user dismisses the sheet.
final pixelInspectionProvider = FutureProvider.autoDispose
    .family<PixelInspection, PixelProbe>((ref, probe) async {
  final api = ref.watch(satelliteApiProvider);
  return api.getPixelInspection(
    probe.fieldId,
    lat: probe.lat,
    lon: probe.lon,
    date: probe.date,
  );
});
