/// Unit tests for NDVI trend direction computation and multi-index
/// recommendation correlation logic extracted from CropHealthDashboard
/// and FieldDetailsScreen.
///
/// اختبارات وحدات لحساب اتجاه NDVI والتوصيات المتعددة المؤشرات.
library;

import 'package:flutter_test/flutter_test.dart';

// ─── Trend direction logic (mirrors _CropHealthDashboardState helpers) ────

/// Mirrors the app's threshold: >0.05 = improving, <-0.05 = declining.
enum NdviTrend { improving, declining, stable }

NdviTrend computeTrend(List<double> ndviSeries) {
  if (ndviSeries.length < 2) return NdviTrend.stable;
  final delta = ndviSeries.last - ndviSeries.first;
  if (delta > 0.05) return NdviTrend.improving;
  if (delta < -0.05) return NdviTrend.declining;
  return NdviTrend.stable;
}

// ─── Multi-index recommendation logic (mirrors _deriveRecommendations) ─────

enum RecommendationType { irrigationPriority, irrigationMonitor, fertilize, followUp, lowHealth, snapshotNotice, none }

class Recommendation {
  final RecommendationType type;
  final String priority; // 'عاجل' | 'مهم' | 'متوسط' | 'منخفض' | 'معلومة'
  const Recommendation(this.type, this.priority);
}

/// Pure extraction of the recommendation logic — no Flutter widgets.
List<Recommendation> deriveRecommendations({
  double? ndvi,
  double? ndwi,
  required double health,
}) {
  final recs = <Recommendation>[];
  final waterStress = ndwi != null && ndwi < 0.2;
  final lowNdvi = ndvi != null && ndvi < 0.4;

  // Multi-index: both signals → irrigation priority over fertilization
  if (waterStress && lowNdvi) {
    recs.add(const Recommendation(RecommendationType.irrigationPriority, 'عاجل'));
  } else if (waterStress) {
    recs.add(const Recommendation(RecommendationType.irrigationPriority, 'عاجل'));
  } else if (ndwi != null && ndwi < 0.35) {
    recs.add(const Recommendation(RecommendationType.irrigationMonitor, 'متوسط'));
  }

  if (!waterStress) {
    if (ndvi != null && ndvi < 0.35) {
      recs.add(const Recommendation(RecommendationType.fertilize, 'مهم'));
    } else if (ndvi != null && ndvi < 0.5) {
      recs.add(const Recommendation(RecommendationType.followUp, 'منخفض'));
    }
  }

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
  // NDVI Trend Direction Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('computeTrend', () {
    test('empty series returns stable', () {
      expect(computeTrend([]), NdviTrend.stable);
    });

    test('single point returns stable', () {
      expect(computeTrend([0.5]), NdviTrend.stable);
    });

    test('delta exactly 0.05 is stable (not improving)', () {
      expect(computeTrend([0.30, 0.35]), NdviTrend.stable);
    });

    test('delta exactly -0.05 is stable (not declining)', () {
      expect(computeTrend([0.60, 0.55]), NdviTrend.stable);
    });

    test('delta > 0.05 is improving', () {
      expect(computeTrend([0.30, 0.40]), NdviTrend.improving);
    });

    test('large positive delta is improving', () {
      expect(computeTrend([0.20, 0.75]), NdviTrend.improving);
    });

    test('delta < -0.05 is declining', () {
      expect(computeTrend([0.70, 0.60]), NdviTrend.declining);
    });

    test('large negative delta is declining', () {
      expect(computeTrend([0.80, 0.10]), NdviTrend.declining);
    });

    test('uses first and last values only (ignores middle)', () {
      // Even though mid-series drops, delta = last - first = +0.20 → improving
      expect(computeTrend([0.40, 0.10, 0.60]), NdviTrend.improving);
    });

    test('flat series is stable', () {
      expect(computeTrend([0.55, 0.55, 0.55, 0.55]), NdviTrend.stable);
    });

    test('boundary: delta just above +0.05 is improving', () {
      expect(computeTrend([0.30, 0.3501]), NdviTrend.improving);
    });

    test('boundary: delta just below -0.05 is declining', () {
      expect(computeTrend([0.60, 0.5499]), NdviTrend.declining);
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
      // fertilize must NOT appear because water stress is present
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

  group('deriveRecommendations — fertilization (no water stress)', () {
    test('NDVI<0.35 with good NDWI → fertilize', () {
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.50, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, contains(RecommendationType.fertilize));
    });

    test('fertilize priority is مهم', () {
      final recs = deriveRecommendations(ndvi: 0.30, ndwi: 0.50, health: 0.7);
      final f = recs.firstWhere((r) => r.type == RecommendationType.fertilize);
      expect(f.priority, 'مهم');
    });

    test('NDVI between 0.35 and 0.5 → followUp (not fertilize)', () {
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
      // NDWI<0.2 → waterStress=true → fertilize branch skipped
      final recs = deriveRecommendations(ndvi: 0.25, ndwi: 0.10, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.fertilize)));
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

    test('null ndwi → no irrigation recs even if ndvi is low', () {
      final recs = deriveRecommendations(ndvi: 0.25, ndwi: null, health: 0.7);
      final types = recs.map((r) => r.type).toList();
      expect(types, isNot(contains(RecommendationType.irrigationPriority)));
      expect(types, isNot(contains(RecommendationType.irrigationMonitor)));
      // fertilize is ok (no water stress)
      expect(types, contains(RecommendationType.fertilize));
    });
  });
}
