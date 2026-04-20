/// Regression tests for the Phase-3 Dart models.
/// نماذج Phase-3: اختبارات التحليل من JSON
///
/// Pins:
///   * Backend camelCase + snake_case compatibility.
///   * `IndexColorScale.sample` ramp behaviour incl. clamping and
///     empty/degenerate scales.
///   * `IndexStatus.unknown` fallback when status is missing.
///   * Empty filmstrip / compare payloads don't blow up fromJson.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/satellite/data/models/index_filmstrip.dart';

void main() {
  group('IndexColorScale.sample', () {
    const ramp = IndexColorScale(
      min: 0,
      max: 1,
      colors: ['#000000', '#444444', '#888888', '#ffffff'],
    );

    test('returns null for null input', () {
      expect(ramp.sample(null), isNull);
    });

    test('maps values into the correct bucket', () {
      expect(ramp.sample(0.0), '#000000');
      expect(ramp.sample(0.3), '#444444');
      expect(ramp.sample(0.6), '#888888');
      // Upper edge hits the last bucket, not out-of-range.
      expect(ramp.sample(1.0), '#ffffff');
    });

    test('clamps out-of-range values', () {
      expect(ramp.sample(-5.0), '#000000');
      expect(ramp.sample(17.0), '#ffffff');
    });

    test('returns null for degenerate ranges or empty ramps', () {
      const empty = IndexColorScale(min: 0, max: 1, colors: []);
      expect(empty.sample(0.5), isNull);

      const inverted = IndexColorScale(min: 1, max: 0, colors: ['#fff']);
      expect(inverted.sample(0.5), isNull);
    });
  });

  group('FilmstripFrame.fromJson', () {
    test('accepts camelCase backend shape', () {
      final frame = FilmstripFrame.fromJson({
        'date': '2026-04-12',
        'rasterUrl': 'sim://ndvi/2026-04-12',
        'value': 0.67,
        'status': {'key': 'excellent', 'en': 'Excellent', 'ar': 'ممتاز'},
        'cloudCover': 3.5,
      });
      expect(frame.date, DateTime.parse('2026-04-12'));
      expect(frame.rasterUrl, 'sim://ndvi/2026-04-12');
      expect(frame.value, 0.67);
      expect(frame.status.key, 'excellent');
      expect(frame.cloudCover, 3.5);
    });

    test('accepts snake_case legacy shape', () {
      final frame = FilmstripFrame.fromJson({
        'date': '2026-04-12',
        'raster_url': 'sim://ndvi/legacy',
        'value': 0.3,
        'cloud_cover': 12.0,
      });
      expect(frame.rasterUrl, 'sim://ndvi/legacy');
      expect(frame.cloudCover, 12.0);
    });

    test('falls back to IndexStatus.unknown when status is missing', () {
      final frame = FilmstripFrame.fromJson({'date': '2026-04-12'});
      expect(frame.status, IndexStatus.unknown);
      expect(frame.status.en, 'Unknown');
      expect(frame.status.ar, 'غير معروف');
    });

    test('accepts null value without crashing', () {
      final frame = FilmstripFrame.fromJson({
        'date': '2026-04-12',
        'rasterUrl': '',
        'value': null,
      });
      expect(frame.value, isNull);
    });
  });

  group('IndexFilmstrip.fromJson', () {
    test('decodes an empty frame list', () {
      final strip = IndexFilmstrip.fromJson({
        'fieldId': 'F1',
        'indexName': 'ndvi',
        'stepDays': 7,
        'colorScale': {'min': -1, 'max': 1, 'colors': []},
        'label': {'en': 'NDVI', 'ar': 'NDVI'},
        'frames': [],
        'dataSource': 'simulated',
      });
      expect(strip.frames, isEmpty);
      expect(strip.stepDays, 7);
      expect(strip.label.en, 'NDVI');
    });

    test('decodes a full 3-frame filmstrip', () {
      final strip = IndexFilmstrip.fromJson({
        'fieldId': 'F1',
        'indexName': 'ndre',
        'stepDays': 14,
        'colorScale': {'min': -1, 'max': 1, 'colors': ['#ff0000', '#00ff00']},
        'label': {'en': 'Red-Edge', 'ar': 'الحافة الحمراء'},
        'frames': [
          {
            'date': '2026-03-01',
            'rasterUrl': 'sim://1',
            'value': 0.3,
            'status': {'key': 'moderate', 'en': 'Moderate', 'ar': 'متوسط'},
          },
          {
            'date': '2026-03-15',
            'rasterUrl': 'sim://2',
            'value': 0.6,
            'status': {'key': 'excellent', 'en': 'Excellent', 'ar': 'ممتاز'},
          },
        ],
        'dataSource': 'simulated',
      });
      expect(strip.frames, hasLength(2));
      expect(strip.frames.last.status.key, 'excellent');
      expect(strip.colorScale.colors, ['#ff0000', '#00ff00']);
    });
  });

  group('CompositeWindow.fromJson', () {
    test('decodes a full bucket including p25/p75', () {
      final w = CompositeWindow.fromJson({
        'window_start': '2026-01-01',
        'window_end': '2026-01-07',
        'count': 5,
        'mean': 0.6,
        'median': 0.61,
        'min': 0.4,
        'max': 0.75,
        'p25': 0.52,
        'p75': 0.68,
        'status': {'key': 'excellent', 'en': 'Excellent', 'ar': 'ممتاز'},
      });
      expect(w.count, 5);
      expect(w.median, 0.61);
      expect(w.p25, 0.52);
      expect(w.p75, 0.68);
      expect(w.status.key, 'excellent');
    });
  });

  group('MultiDateCompare.fromJson', () {
    test('decodes rows with nullable delta', () {
      final cmp = MultiDateCompare.fromJson({
        'fieldId': 'F1',
        'indexName': 'ndvi',
        'dates': ['2026-01-01', '2026-02-01'],
        'rows': [
          {
            'date': '2026-01-01',
            'value': 0.5,
            'delta_from_previous': null,
            'status': {'key': 'good', 'en': 'Good', 'ar': 'جيد'},
          },
          {
            'date': '2026-02-01',
            'value': 0.7,
            'delta_from_previous': 0.2,
            'status': {'key': 'excellent', 'en': 'Excellent', 'ar': 'ممتاز'},
          },
        ],
        'summary': {
          'count_dates': 2,
          'count_with_data': 2,
          'min': 0.5,
          'max': 0.7,
          'overall_delta': 0.2,
        },
        'dataSource': 'simulated',
      });
      expect(cmp.rows, hasLength(2));
      expect(cmp.rows.first.deltaFromPrevious, isNull);
      expect(cmp.rows.last.deltaFromPrevious, 0.2);
      expect(cmp.summary.overallDelta, 0.2);
    });

    test('survives a summary payload with only the required fields', () {
      final cmp = MultiDateCompare.fromJson({
        'fieldId': 'F1',
        'indexName': 'ndvi',
        'dates': [],
        'rows': [],
        'summary': {'count_dates': 0, 'count_with_data': 0},
        'dataSource': 'simulated',
      });
      expect(cmp.summary.min, isNull);
      expect(cmp.summary.overallDelta, isNull);
    });
  });
}
