/// Unit tests for NDVI trend direction computation and multi-index
/// recommendation correlation logic extracted from CropHealthDashboard
/// and FieldDetailsScreen.
///
/// اختبارات وحدات لحساب اتجاه NDVI والتوصيات المتعددة المؤشرات.
library;

import 'package:flutter_test/flutter_test.dart';

// ─── Trend direction logic (mirrors _CropHealthDashboardState._computeTrend) ─

/// Mirrors the app's threshold: >0.05 = improving, <-0.05 = declining.
enum NdviTrend { improving, declining, stable }

/// Mirrors `_computeTrend` in the dashboard.
/// Window size degrades gradually: `(length ~/ 2).clamp(1, 3)`.
///   length ≥ 6 → 3   length 4–5 → 2   length 2–3 → 1
NdviTrend computeTrend(List<double> ndviSeries) {
  if (ndviSeries.length < 2) return NdviTrend.stable;

  double avg(Iterable<double> values) {
    final list = values.toList();
    return list.reduce((a, b) => a + b) / list.length;
  }

  // Gradual degradation — never collapses abruptly to last-vs-first.
  final windowSize = (ndviSeries.length ~/ 2).clamp(1, 3);
  final startAvg = avg(ndviSeries.take(windowSize));
  final endAvg = avg(ndviSeries.reversed.take(windowSize));

  final delta = endAvg - startAvg;
  if (delta > 0.05) return NdviTrend.improving;
  if (delta < -0.05) return NdviTrend.declining;
  return NdviTrend.stable;
}

// ─── Multi-index recommendation logic (mirrors _deriveRecommendations) ─────

enum RecommendationType {
  irrigationPriority,
  irrigationMonitor,
  fertilize,
  followUp,
  scouting, // ambiguous stress — field inspection required
  lowHealth,
  snapshotNotice,
  none,
}

class Recommendation {
  final RecommendationType type;
  final String priority; // 'عاجل' | 'مهم' | 'متوسط' | 'منخفض' | 'معلومة'
  const Recommendation(this.type, this.priority);
}

/// Pure extraction of the recommendation logic — no Flutter widgets.
/// Mirrors the production logic in field_details_screen.dart
/// `_deriveRecommendations()`.
List<Recommendation> deriveRecommendations({
  double? ndvi,
  double? ndwi,
  required double health,
}) {
  final recs = <Recommendation>[];
  final waterStress = ndwi != null && ndwi < 0.2;
  final lowNdvi = ndvi != null && ndvi < 0.4;

  // ── Irrigation signals ────────────────────────────────────────────────
  if (waterStress && lowNdvi) {
    recs.add(const Recommendation(RecommendationType.irrigationPriority, 'عاجل'));
  } else if (waterStress) {
    recs.add(const Recommendation(RecommendationType.irrigationPriority, 'عاجل'));
  } else if (ndwi != null && ndwi < 0.35) {
    recs.add(const Recommendation(RecommendationType.irrigationMonitor, 'متوسط'));
  }

  // ── Fertilization / scouting (no water stress) ────────────────────────
  // Nitrogen is only suggested when moisture is comfortably above the
  // irrigation-monitoring threshold (ndwi > 0.3). Borderline moisture
  // with low NDVI is ambiguous — route to field scouting first.
  final bool moistureOk = ndwi == null || ndwi > 0.3;
  if (!waterStress && moistureOk) {
    if (ndvi != null && ndvi < 0.35) {
      recs.add(const Recommendation(RecommendationType.fertilize, 'مهم'));
    } else if (ndvi != null && ndvi < 0.5) {
      recs.add(const Recommendation(RecommendationType.followUp, 'منخفض'));
    }
  } else if (!waterStress && !moistureOk) {
    // ndwi is between 0.2 and 0.3 — borderline moisture + low ndvi
    if (ndvi != null && ndvi < 0.4) {
      recs.add(const Recommendation(RecommendationType.scouting, 'مهم'));
    }
  }

  // ── Overall health ────────────────────────────────────────────────────
  if (health < 0.4) {
    recs.add(const Recommendation(RecommendationType.lowHealth, 'عاجل'));
  }

  // Snapshot honesty notice — always present
  recs.add(const Recommendation(RecommendationType.snapshotNotice, 'معلومة'));
  return recs;
}

// ─────────────────────────────────────────────────────────────────────────────

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Trend Direction Tests (3-point moving-average algorithm)
  // ═══════════════════════════════════════════════════════════════════════════

  group('computeTrend — edge cases', () {
    test('empty series returns stable', () {
      expect(computeTrend([]), NdviTrend.stable);
    });

    test('single point returns stable', () {
      expect(computeTrend([0.5]), NdviTrend.stable);
    });

    test('flat series is stable', () {
      expect(computeTrend([0.55, 0.55, 0.55, 0.55]), NdviTrend.stable);
    });
  });

  group('computeTrend — short series (length 2–3, window=1)', () {
    // length=2 → window=(2~/2).clamp(1,3)=1
    // length=3 → window=(3~/2).clamp(1,3)=1
    // Equivalent to first-vs-last for these very short series.

    test('delta exactly +0.05 is stable (not improving)', () {
      expect(computeTrend([0.30, 0.35]), NdviTrend.stable);
    });

    test('delta exactly -0.05 is stable (not declining)', () {
      expect(computeTrend([0.60, 0.55]), NdviTrend.stable);
    });

    test('delta > 0.05 → improving', () {
      expect(computeTrend([0.30, 0.40]), NdviTrend.improving);
    });

    test('large positive delta → improving', () {
      expect(computeTrend([0.20, 0.75]), NdviTrend.improving);
    });

    test('delta < -0.05 → declining', () {
      expect(computeTrend([0.70, 0.60]), NdviTrend.declining);
    });

    test('large negative delta → declining', () {
      expect(computeTrend([0.80, 0.10]), NdviTrend.declining);
    });

    test('boundary: delta just above +0.05 → improving', () {
      // 0.3501 - 0.30 = 0.0501, just above the 0.05 threshold.
      expect(computeTrend([0.30, 0.3501]), NdviTrend.improving);
    });

    test('boundary: delta just below -0.05 → declining', () {
      // 0.5499 - 0.60 = -0.0501, just below -0.05.
      expect(computeTrend([0.60, 0.5499]), NdviTrend.declining);
    });
  });

  group('computeTrend — intermediate series (length 4–5, window=2)', () {
    // length=4 → window=(4~/2).clamp(1,3)=2
    // length=5 → window=(5~/2).clamp(1,3)=2
    // Uses 2-point averages — more noise-resilient than raw first-vs-last.

    test('4-point monotone increase → improving', () {
      // startAvg=avg([0.30,0.36])=0.33, endAvg=avg([0.60,0.52])=0.56, delta=+0.23
      expect(computeTrend([0.30, 0.36, 0.52, 0.60]), NdviTrend.improving);
    });

    test('4-point spike at start dampened: endpoint spike does not dominate', () {
      // Raw last-first: 0.42 - 0.80 = -0.38 → declining (misleading)
      // 2-pt avg: startAvg=avg([0.80,0.35])=0.575, endAvg=avg([0.42,0.38])=0.40
      // delta = -0.175 → declining (correct — series IS declining after spike)
      // This proves window=2 still catches the true trend even with 4 points.
      expect(computeTrend([0.80, 0.35, 0.38, 0.42]), NdviTrend.declining);
    });

    test('4-point flat with noise → stable', () {
      // startAvg=avg([0.50,0.52])=0.51, endAvg=avg([0.51,0.49])=0.50, delta=-0.01
      expect(computeTrend([0.50, 0.52, 0.51, 0.49]), NdviTrend.stable);
    });

    test('5-point monotone increase → improving', () {
      // window=2: startAvg=avg([0.30,0.36])=0.33, endAvg=avg([0.60,0.52])=0.56
      // delta = +0.23 → improving
      expect(computeTrend([0.30, 0.36, 0.42, 0.52, 0.60]), NdviTrend.improving);
    });

    test('5-point declining trend → declining', () {
      // startAvg=avg([0.70,0.65])=0.675, endAvg=avg([0.45,0.40])=0.425, delta=-0.25
      expect(computeTrend([0.70, 0.65, 0.55, 0.45, 0.40]), NdviTrend.declining);
    });
  });

  group('computeTrend — non-monotonic series (noise robustness, window=3)', () {
    // ── Series of length >= 6 uses 3-point averages ──

    test('spike at start dampened to stable: 3-pt avg neutralises single-point outlier', () {
      // Series: big spike at t0, then drop, then gradual recovery.
      // Raw first-vs-last: 0.45 - 0.65 = -0.20 → declining (misleading).
      // 3-pt avg: startAvg=(0.65+0.30+0.31)/3=0.42, endAvg=(0.35+0.40+0.45)/3=0.40
      // delta = -0.02 → stable — the 3-point window correctly absorbs the
      // spike so the series is not misclassified as strongly declining.
      expect(computeTrend([0.65, 0.30, 0.31, 0.35, 0.40, 0.45]), NdviTrend.stable);
    });

    test('non-monotonic series [0.3,0.5,0.35] → stable (not improving)', () {
      // length=3 → window=(3~/2).clamp(1,3)=1 → equivalent to first-vs-last.
      // start=0.30, end=0.35 → delta=+0.05 → stable (not > 0.05).
      expect(computeTrend([0.30, 0.50, 0.35]), NdviTrend.stable);
    });

    test('noisy but overall declining (6 points) → declining', () {
      // startAvg = (0.70+0.68+0.72)/3 = 0.7000
      // endAvg   = (0.55+0.52+0.50)/3 = 0.5233
      // delta = -0.177 → declining
      expect(computeTrend([0.70, 0.68, 0.72, 0.55, 0.52, 0.50]), NdviTrend.declining);
    });

    test('noisy but overall improving (6 points) → improving', () {
      // startAvg = (0.30+0.28+0.32)/3 = 0.30
      // endAvg   = (0.55+0.58+0.60)/3 = 0.577
      // delta = +0.277 → improving
      expect(computeTrend([0.30, 0.28, 0.32, 0.55, 0.58, 0.60]), NdviTrend.improving);
    });

    test('mid-series spike on otherwise stable trend → stable', () {
      // startAvg = (0.50+0.51+0.49)/3 = 0.5000
      // endAvg   = (0.48+0.51+0.52)/3 = 0.5033
      // delta = +0.003 → stable (spike in middle is ignored)
      expect(computeTrend([0.50, 0.51, 0.49, 0.90, 0.48, 0.51, 0.52]),
          NdviTrend.stable);
    });

    test('7-point steady increase → improving', () {
      expect(
        computeTrend([0.20, 0.25, 0.30, 0.40, 0.50, 0.60, 0.70]),
        NdviTrend.improving,
      );
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Multi-Index Recommendation Correlation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('deriveRecommendations — always includes snapshot notice', () {
    test('notice is always the last recommendation', () {
      final recs = deriveRecommendations(ndvi: 0.8, ndwi: 0.5, health: 0.9);
      expect(recs.last.type, RecommendationType.snapshotNotice);
    });
  });

  group('deriveRecommendations — irrigation priority', () {
    test('both NDWI<0.2 and NDVI<0.4 → irrigationPriority (not fertilize)', () {
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.15, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.irrigationPriority));
      expect(types, isNot(contains(RecommendationType.fertilize)));
    });

    test('NDWI=0.15 alone (ndvi healthy) → irrigationPriority', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.15, health: 0.7);
      expect(recs.first.type, RecommendationType.irrigationPriority);
    });

    test('NDWI=0.19 (just below 0.2) → irrigationPriority', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.19, health: 0.7);
      expect(recs.first.type, RecommendationType.irrigationPriority);
    });

    test('NDWI=0.20 (at boundary, not below) → no irrigation priority', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.20, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.irrigationPriority)));
    });

    test('irrigationPriority priority is عاجل', () {
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.10, health: 0.7);
      final irr = recs.firstWhere((r) => r.type == RecommendationType.irrigationPriority);
      expect(irr.priority, 'عاجل');
    });
  });

  group('deriveRecommendations — irrigation monitor', () {
    test('NDWI between 0.2 and 0.35 → irrigationMonitor', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.28, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.irrigationMonitor));
    });

    test('irrigationMonitor priority is متوسط', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.28, health: 0.7);
      final m = recs.firstWhere((r) => r.type == RecommendationType.irrigationMonitor);
      expect(m.priority, 'متوسط');
    });

    test('NDWI=0.35 (at boundary) → no irrigationMonitor', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.35, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.irrigationMonitor)));
    });
  });

  group('deriveRecommendations — fertilization nitrogen gate (ndwi > 0.3)', () {
    test('NDVI<0.35 with NDWI>0.3 → fertilize', () {
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.50, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.fertilize));
    });

    test('fertilize priority is مهم', () {
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.50, health: 0.7);
      final f = recs.firstWhere((r) => r.type == RecommendationType.fertilize);
      expect(f.priority, 'مهم');
    });

    test('NDVI between 0.35 and 0.5 with NDWI>0.3 → followUp (not fertilize)', () {
      final recs = deriveRecommendations(ndvi: 0.45, ndwi: 0.50, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.followUp));
      expect(types, isNot(contains(RecommendationType.fertilize)));
    });

    test('NDVI>=0.5 → no fertilize or followUp', () {
      final recs = deriveRecommendations(ndvi: 0.65, ndwi: 0.50, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.fertilize)));
      expect(types, isNot(contains(RecommendationType.followUp)));
    });

    test('water stress suppresses fertilize even if NDVI is low', () {
      final recs = deriveRecommendations(ndvi: 0.25, ndwi: 0.10, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.fertilize)));
    });

    // ── Nitrogen gate: ambiguous moisture (0.2 ≤ ndwi ≤ 0.3) ─────────────
    test('NDVI<0.4 and NDWI between 0.2-0.3 → scouting (not fertilize)', () {
      // NDWI=0.25 is not water-stress but also not comfortably moist.
      // Low NDVI here is ambiguous — should route to field scouting.
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.25, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.scouting));
      expect(types, isNot(contains(RecommendationType.fertilize)));
    });

    test('NDWI=0.30 (at boundary) → still triggers scouting not fertilize', () {
      // ndwi = 0.30 is NOT > 0.30 so moistureOk is false → scouting path.
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.30, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.scouting));
      expect(types, isNot(contains(RecommendationType.fertilize)));
    });

    test('NDWI just above 0.30 → fertilize (moisture is comfortable)', () {
      // ndwi = 0.301 → moistureOk = true → fertilize branch.
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.301, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.fertilize));
      expect(types, isNot(contains(RecommendationType.scouting)));
    });

    test('NDVI>=0.4 with borderline NDWI → no scouting (ndvi not low enough)', () {
      // lowNdvi = false, so scouting condition (ndvi < 0.4) is not met.
      final recs = deriveRecommendations(ndvi: 0.55, ndwi: 0.25, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.scouting)));
    });
  });

  group('deriveRecommendations — low health', () {
    test('health < 0.4 → lowHealth added', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.50, health: 0.3);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.lowHealth));
    });

    test('health = 0.4 (boundary) → no lowHealth', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.50, health: 0.4);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.lowHealth)));
    });

    test('lowHealth priority is عاجل', () {
      final recs = deriveRecommendations(ndvi: 0.70, ndwi: 0.50, health: 0.2);
      final lh = recs.firstWhere((r) => r.type == RecommendationType.lowHealth);
      expect(lh.priority, 'عاجل');
    });
  });

  group('deriveRecommendations — null index handling', () {
    test('null ndvi and null ndwi → only snapshot notice returned', () {
      final recs = deriveRecommendations(ndvi: null, ndwi: null, health: 0.7);
      expect(recs, hasLength(1));
      expect(recs.first.type, RecommendationType.snapshotNotice);
    });

    test('null ndwi with low ndvi → fertilize (moisture unknown = treated as ok)', () {
      // When ndwi is null, moistureOk = (null == null || null > 0.3) = true.
      // So nitrogen gate passes and fertilize fires.
      final recs = deriveRecommendations(ndvi: 0.25, ndwi: null, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.irrigationPriority)));
      expect(types, isNot(contains(RecommendationType.irrigationMonitor)));
      expect(types, contains(RecommendationType.fertilize));
    });
  });
}

