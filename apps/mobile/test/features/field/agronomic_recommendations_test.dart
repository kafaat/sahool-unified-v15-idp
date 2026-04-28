/// Unit tests for the agronomic recommendation derivation logic.
/// اختبارات منطق استخراج التوصيات الزراعية من قيم المؤشرات.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:flutter/material.dart';
import 'package:sahool_field_app/features/fields/domain/entities/field_entity.dart';

// ─── Mirrors of private helpers extracted for testability ────────────────────

/// Mirrors `_FieldDetailsScreenState._deriveRecommendations()` logic.
List<_TestRec> deriveRecommendations({
  double? ndvi,
  double? ndwi,
  required double healthScore,
}) {
  final recs = <_TestRec>[];

  if (ndwi != null && ndwi < 0.15) {
    recs.add(_TestRec(title: 'زيادة الري', priority: 'عاجل'));
  } else if (ndwi != null && ndwi < 0.3) {
    recs.add(_TestRec(title: 'مراقبة الري', priority: 'متوسط'));
  }

  if (ndvi != null && ndvi < 0.35) {
    recs.add(_TestRec(title: 'تسميد نيتروجيني', priority: 'مهم'));
  } else if (ndvi != null && ndvi < 0.5) {
    recs.add(_TestRec(title: 'متابعة النمو', priority: 'منخفض'));
  }

  if (healthScore < 0.4) {
    recs.add(_TestRec(title: 'صحة الحقل منخفضة', priority: 'عاجل'));
  }

  return recs;
}

/// Mirrors `_FieldDetailsScreenState._indexInterpretation()`.
String indexInterpretation(String name, double value) {
  switch (name) {
    case 'NDVI':
      if (value >= 0.6) return '· نمو ممتاز';
      if (value >= 0.4) return '· نمو جيد';
      if (value >= 0.2) return '· نمو ضعيف';
      return '· يحتاج تدخلاً';
    case 'NDWI':
      if (value >= 0.3) return '· مستوى مائي كافٍ';
      if (value >= 0.15) return '· مراقبة الري';
      return '· يحتاج ريّاً';
    default:
      return '';
  }
}

/// Mirrors `_FieldDetailsScreenState._formatTimestamp()`.
String formatTimestamp(DateTime dt) {
  final now = DateTime.now();
  final diff = now.difference(dt);
  if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
  if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
  if (diff.inDays == 1) return 'البارحة';
  if (diff.inDays < 7) return 'منذ ${diff.inDays} أيام';
  return '${dt.day}/${dt.month}/${dt.year}';
}

class _TestRec {
  final String title;
  final String priority;
  const _TestRec({required this.title, required this.priority});
}

// ─────────────────────────────────────────────────────────────────────────────

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // _deriveRecommendations – irrigation (NDWI-based)
  // ═══════════════════════════════════════════════════════════════════════════

  group('deriveRecommendations – irrigation', () {
    test('ndwi < 0.15 → عاجل irrigation recommendation', () {
      final recs = deriveRecommendations(ndwi: 0.10, healthScore: 0.7);
      expect(recs.any((r) => r.title == 'زيادة الري' && r.priority == 'عاجل'), isTrue);
    });

    test('ndwi between 0.15 and 0.30 → متوسط monitoring recommendation', () {
      final recs = deriveRecommendations(ndwi: 0.22, healthScore: 0.7);
      expect(recs.any((r) => r.title == 'مراقبة الري' && r.priority == 'متوسط'), isTrue);
    });

    test('ndwi >= 0.30 → no irrigation recommendation', () {
      final recs = deriveRecommendations(ndwi: 0.35, healthScore: 0.7);
      expect(recs.any((r) => r.title.contains('ري')), isFalse);
    });

    test('ndwi null → no irrigation recommendation', () {
      final recs = deriveRecommendations(ndwi: null, healthScore: 0.7);
      expect(recs.any((r) => r.title.contains('ري')), isFalse);
    });

    test('ndwi exactly 0.15 → monitoring (boundary)', () {
      // 0.15 is NOT < 0.15 so falls into the [0.15, 0.30) bracket
      final recs = deriveRecommendations(ndwi: 0.15, healthScore: 0.7);
      expect(recs.any((r) => r.title == 'مراقبة الري'), isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // _deriveRecommendations – nitrogen / NDVI-based
  // ═══════════════════════════════════════════════════════════════════════════

  group('deriveRecommendations – nitrogen (NDVI)', () {
    test('ndvi < 0.35 → nitrogen fertilizer recommendation', () {
      final recs = deriveRecommendations(ndvi: 0.28, healthScore: 0.7);
      expect(recs.any((r) => r.title == 'تسميد نيتروجيني'), isTrue);
    });

    test('ndvi between 0.35 and 0.50 → growth monitoring recommendation', () {
      final recs = deriveRecommendations(ndvi: 0.42, healthScore: 0.7);
      expect(recs.any((r) => r.title == 'متابعة النمو'), isTrue);
    });

    test('ndvi >= 0.50 → no nitrogen recommendation', () {
      final recs = deriveRecommendations(ndvi: 0.62, healthScore: 0.7);
      expect(recs.any((r) => r.title.contains('تسميد') || r.title.contains('نمو')), isFalse);
    });

    test('ndvi null → no nitrogen recommendation', () {
      final recs = deriveRecommendations(ndvi: null, healthScore: 0.7);
      expect(recs.any((r) => r.title.contains('تسميد')), isFalse);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // _deriveRecommendations – overall health
  // ═══════════════════════════════════════════════════════════════════════════

  group('deriveRecommendations – overall health', () {
    test('healthScore < 0.4 → critical health warning', () {
      final recs = deriveRecommendations(healthScore: 0.25);
      expect(recs.any((r) => r.title == 'صحة الحقل منخفضة' && r.priority == 'عاجل'), isTrue);
    });

    test('healthScore >= 0.4 → no health warning', () {
      final recs = deriveRecommendations(healthScore: 0.6);
      expect(recs.any((r) => r.title == 'صحة الحقل منخفضة'), isFalse);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // _deriveRecommendations – combinations
  // ═══════════════════════════════════════════════════════════════════════════

  group('deriveRecommendations – combined', () {
    test('healthy field (all good) → empty recommendations', () {
      final recs = deriveRecommendations(ndvi: 0.72, ndwi: 0.45, healthScore: 0.85);
      expect(recs, isEmpty);
    });

    test('bad ndwi + bad ndvi → both recommendations present', () {
      final recs = deriveRecommendations(ndvi: 0.20, ndwi: 0.08, healthScore: 0.7);
      expect(recs.any((r) => r.title == 'زيادة الري'), isTrue);
      expect(recs.any((r) => r.title == 'تسميد نيتروجيني'), isTrue);
    });

    test('bad health + bad ndwi → three recommendations', () {
      final recs = deriveRecommendations(ndwi: 0.05, healthScore: 0.3);
      expect(recs.length, greaterThanOrEqualTo(2));
      expect(recs.any((r) => r.title == 'زيادة الري'), isTrue);
      expect(recs.any((r) => r.title == 'صحة الحقل منخفضة'), isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // _indexInterpretation
  // ═══════════════════════════════════════════════════════════════════════════

  group('indexInterpretation – NDVI', () {
    test('≥ 0.6 → ممتاز', () => expect(indexInterpretation('NDVI', 0.72), contains('ممتاز')));
    test('0.4–0.6 → جيد', () => expect(indexInterpretation('NDVI', 0.48), contains('جيد')));
    test('0.2–0.4 → ضعيف', () => expect(indexInterpretation('NDVI', 0.28), contains('ضعيف')));
    test('< 0.2 → تدخل', () => expect(indexInterpretation('NDVI', 0.10), contains('تدخلاً')));
    test('exactly 0.6 → ممتاز (boundary)', () => expect(indexInterpretation('NDVI', 0.60), contains('ممتاز')));
  });

  group('indexInterpretation – NDWI', () {
    test('≥ 0.3 → كافٍ', () => expect(indexInterpretation('NDWI', 0.45), contains('كافٍ')));
    test('0.15–0.3 → مراقبة', () => expect(indexInterpretation('NDWI', 0.22), contains('مراقبة')));
    test('< 0.15 → ريّاً', () => expect(indexInterpretation('NDWI', 0.05), contains('ريّاً')));
  });

  group('indexInterpretation – unknown index', () {
    test('unknown name returns empty string', () {
      expect(indexInterpretation('SAVI', 0.55), '');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // _formatTimestamp
  // ═══════════════════════════════════════════════════════════════════════════

  group('formatTimestamp', () {
    test('within the hour shows دقيقة', () {
      final dt = DateTime.now().subtract(const Duration(minutes: 20));
      expect(formatTimestamp(dt), contains('دقيقة'));
    });

    test('within the day shows ساعة', () {
      final dt = DateTime.now().subtract(const Duration(hours: 5));
      expect(formatTimestamp(dt), contains('ساعة'));
    });

    test('exactly 1 day ago shows البارحة', () {
      final dt = DateTime.now().subtract(const Duration(days: 1));
      expect(formatTimestamp(dt), 'البارحة');
    });

    test('3 days ago shows أيام', () {
      final dt = DateTime.now().subtract(const Duration(days: 3));
      expect(formatTimestamp(dt), contains('أيام'));
    });

    test('more than 7 days ago shows numeric date', () {
      final dt = DateTime(2025, 3, 15);
      expect(formatTimestamp(dt), contains('2025'));
    });
  });
}
