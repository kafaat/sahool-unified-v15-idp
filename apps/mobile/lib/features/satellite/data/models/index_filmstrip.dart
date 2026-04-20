/// Multi-date filmstrip / composite / compare models.
/// نماذج بيانات الشريط الزمني والتركيب والمقارنة متعددة التواريخ
///
/// Mirrors the Phase-3 backend endpoints:
///
///   GET  /v1/indices/{field_id}/{index_name}/filmstrip       → [IndexFilmstrip]
///   GET  /v1/indices/{field_id}/{index_name}/composite       → [IndexComposite]
///   POST /v1/indices/{field_id}/{index_name}/multi-date-compare → [MultiDateCompare]
///
/// Kept deliberately minimal: the widgets only render what they need,
/// anything the UI doesn't display is dropped on the floor — we don't
/// try to be a full schema mirror.
library;

import 'package:equatable/equatable.dart';

/// Bilingual health-status bucket returned by the three Phase-3
/// endpoints. Always has non-empty `en` and `ar` — the backend never
/// ships an unlabelled status.
class IndexStatus extends Equatable {
  final String key; // excellent | good | moderate | poor | unknown
  final String en;
  final String ar;

  const IndexStatus({required this.key, required this.en, required this.ar});

  factory IndexStatus.fromJson(Map<String, dynamic> json) {
    return IndexStatus(
      key: (json['key'] ?? 'unknown') as String,
      en: (json['en'] ?? '') as String,
      ar: (json['ar'] ?? '') as String,
    );
  }

  static const IndexStatus unknown = IndexStatus(
    key: 'unknown',
    en: 'Unknown',
    ar: 'غير معروف',
  );

  @override
  List<Object?> get props => [key, en, ar];
}

/// One frame in a filmstrip — designed for direct consumption by a
/// carousel widget.
class FilmstripFrame extends Equatable {
  final DateTime date;
  final String rasterUrl;
  final double? value;
  final IndexStatus status;
  final double? cloudCover;

  const FilmstripFrame({
    required this.date,
    required this.rasterUrl,
    required this.status,
    this.value,
    this.cloudCover,
  });

  factory FilmstripFrame.fromJson(Map<String, dynamic> json) {
    final raw = json['value'];
    final cloud = json['cloudCover'] ?? json['cloud_cover'];
    return FilmstripFrame(
      date: DateTime.tryParse((json['date'] ?? '') as String) ?? DateTime.now(),
      rasterUrl: (json['rasterUrl'] ?? json['raster_url'] ?? '') as String,
      status: json['status'] is Map
          ? IndexStatus.fromJson(json['status'] as Map<String, dynamic>)
          : IndexStatus.unknown,
      value: raw is num ? raw.toDouble() : null,
      cloudCover: cloud is num ? cloud.toDouble() : null,
    );
  }

  @override
  List<Object?> get props => [date, rasterUrl, value, status, cloudCover];
}

/// Colour-scale metadata — min/max/stops. Used to tint thumbnail
/// placeholders without needing to fetch raster bytes.
class IndexColorScale extends Equatable {
  final double min;
  final double max;
  final List<String> colors;

  const IndexColorScale({required this.min, required this.max, required this.colors});

  factory IndexColorScale.fromJson(Map<String, dynamic> json) {
    return IndexColorScale(
      min: ((json['min'] ?? -1) as num).toDouble(),
      max: ((json['max'] ?? 1) as num).toDouble(),
      colors: ((json['colors'] as List?) ?? const [])
          .whereType<String>()
          .toList(),
    );
  }

  /// Sample the ramp at a specific value. Returns null when [value] is
  /// null or the ramp is empty so callers can fall back to a neutral tile.
  String? sample(double? value) {
    if (value == null || colors.isEmpty || max <= min) return null;
    final clamped = value.clamp(min, max) as double;
    final ratio = (clamped - min) / (max - min);
    final idx = (ratio * colors.length).floor().clamp(0, colors.length - 1);
    return colors[idx];
  }

  @override
  List<Object?> get props => [min, max, colors];
}

/// Bilingual label pair, used for index descriptions.
class BilingualLabel extends Equatable {
  final String en;
  final String ar;

  const BilingualLabel({required this.en, required this.ar});

  factory BilingualLabel.fromJson(Map<String, dynamic> json) =>
      BilingualLabel(en: (json['en'] ?? '') as String, ar: (json['ar'] ?? '') as String);

  @override
  List<Object?> get props => [en, ar];
}

/// Full filmstrip response envelope.
class IndexFilmstrip extends Equatable {
  final String fieldId;
  final String indexName;
  final int stepDays;
  final IndexColorScale colorScale;
  final BilingualLabel label;
  final List<FilmstripFrame> frames;
  final String dataSource;

  const IndexFilmstrip({
    required this.fieldId,
    required this.indexName,
    required this.stepDays,
    required this.colorScale,
    required this.label,
    required this.frames,
    required this.dataSource,
  });

  factory IndexFilmstrip.fromJson(Map<String, dynamic> json) {
    return IndexFilmstrip(
      fieldId: (json['fieldId'] ?? json['field_id'] ?? '') as String,
      indexName: (json['indexName'] ?? json['index_name'] ?? '') as String,
      stepDays: ((json['stepDays'] ?? json['step_days'] ?? 7) as num).toInt(),
      colorScale: json['colorScale'] is Map
          ? IndexColorScale.fromJson(json['colorScale'] as Map<String, dynamic>)
          : const IndexColorScale(min: -1, max: 1, colors: []),
      label: json['label'] is Map
          ? BilingualLabel.fromJson(json['label'] as Map<String, dynamic>)
          : const BilingualLabel(en: '', ar: ''),
      frames: ((json['frames'] as List?) ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(FilmstripFrame.fromJson)
          .toList(),
      dataSource: (json['dataSource'] ?? json['data_source'] ?? 'simulated') as String,
    );
  }

  @override
  List<Object?> get props =>
      [fieldId, indexName, stepDays, colorScale, label, frames, dataSource];
}

/// One bucket in a composite response (`stat=median|mean`).
class CompositeWindow extends Equatable {
  final DateTime windowStart;
  final DateTime windowEnd;
  final int count;
  final double mean;
  final double median;
  final double min;
  final double max;
  final double p25;
  final double p75;
  final IndexStatus status;

  const CompositeWindow({
    required this.windowStart,
    required this.windowEnd,
    required this.count,
    required this.mean,
    required this.median,
    required this.min,
    required this.max,
    required this.p25,
    required this.p75,
    required this.status,
  });

  factory CompositeWindow.fromJson(Map<String, dynamic> json) {
    double num_(String key, [double fallback = 0]) {
      final raw = json[key];
      return raw is num ? raw.toDouble() : fallback;
    }

    return CompositeWindow(
      windowStart:
          DateTime.tryParse((json['window_start'] ?? '') as String) ?? DateTime.now(),
      windowEnd:
          DateTime.tryParse((json['window_end'] ?? '') as String) ?? DateTime.now(),
      count: ((json['count'] ?? 0) as num).toInt(),
      mean: num_('mean'),
      median: num_('median'),
      min: num_('min'),
      max: num_('max'),
      p25: num_('p25'),
      p75: num_('p75'),
      status: json['status'] is Map
          ? IndexStatus.fromJson(json['status'] as Map<String, dynamic>)
          : IndexStatus.unknown,
    );
  }

  @override
  List<Object?> get props =>
      [windowStart, windowEnd, count, mean, median, min, max, p25, p75, status];
}

/// Composite response envelope.
class IndexComposite extends Equatable {
  final String fieldId;
  final String indexName;
  final String stat; // 'median' | 'mean'
  final int stepDays;
  final List<CompositeWindow> windows;
  final String dataSource;

  const IndexComposite({
    required this.fieldId,
    required this.indexName,
    required this.stat,
    required this.stepDays,
    required this.windows,
    required this.dataSource,
  });

  factory IndexComposite.fromJson(Map<String, dynamic> json) {
    return IndexComposite(
      fieldId: (json['fieldId'] ?? '') as String,
      indexName: (json['indexName'] ?? '') as String,
      stat: (json['stat'] ?? 'median') as String,
      stepDays: ((json['stepDays'] ?? 7) as num).toInt(),
      windows: ((json['windows'] as List?) ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(CompositeWindow.fromJson)
          .toList(),
      dataSource: (json['dataSource'] ?? 'simulated') as String,
    );
  }

  @override
  List<Object?> get props => [fieldId, indexName, stat, stepDays, windows, dataSource];
}

/// One row in a multi-date-compare response.
class MultiDateCompareRow extends Equatable {
  final DateTime date;
  final double? value;
  final double? deltaFromPrevious;
  final IndexStatus status;

  const MultiDateCompareRow({
    required this.date,
    required this.status,
    this.value,
    this.deltaFromPrevious,
  });

  factory MultiDateCompareRow.fromJson(Map<String, dynamic> json) {
    final v = json['value'];
    final d = json['delta_from_previous'] ?? json['deltaFromPrevious'];
    return MultiDateCompareRow(
      date: DateTime.tryParse((json['date'] ?? '') as String) ?? DateTime.now(),
      value: v is num ? v.toDouble() : null,
      deltaFromPrevious: d is num ? d.toDouble() : null,
      status: json['status'] is Map
          ? IndexStatus.fromJson(json['status'] as Map<String, dynamic>)
          : IndexStatus.unknown,
    );
  }

  @override
  List<Object?> get props => [date, value, deltaFromPrevious, status];
}

/// Summary section of a multi-date-compare response.
class MultiDateCompareSummary extends Equatable {
  final int countDates;
  final int countWithData;
  final double? min;
  final double? max;
  final double? overallDelta;

  const MultiDateCompareSummary({
    required this.countDates,
    required this.countWithData,
    this.min,
    this.max,
    this.overallDelta,
  });

  factory MultiDateCompareSummary.fromJson(Map<String, dynamic> json) {
    double? num_(String k) {
      final raw = json[k];
      return raw is num ? raw.toDouble() : null;
    }

    return MultiDateCompareSummary(
      countDates: ((json['count_dates'] ?? 0) as num).toInt(),
      countWithData: ((json['count_with_data'] ?? 0) as num).toInt(),
      min: num_('min'),
      max: num_('max'),
      overallDelta: num_('overall_delta'),
    );
  }

  @override
  List<Object?> get props => [countDates, countWithData, min, max, overallDelta];
}

/// Multi-date compare response envelope.
class MultiDateCompare extends Equatable {
  final String fieldId;
  final String indexName;
  final List<String> dates;
  final List<MultiDateCompareRow> rows;
  final MultiDateCompareSummary summary;
  final String dataSource;

  const MultiDateCompare({
    required this.fieldId,
    required this.indexName,
    required this.dates,
    required this.rows,
    required this.summary,
    required this.dataSource,
  });

  factory MultiDateCompare.fromJson(Map<String, dynamic> json) {
    return MultiDateCompare(
      fieldId: (json['fieldId'] ?? '') as String,
      indexName: (json['indexName'] ?? '') as String,
      dates: ((json['dates'] as List?) ?? const []).whereType<String>().toList(),
      rows: ((json['rows'] as List?) ?? const [])
          .whereType<Map<String, dynamic>>()
          .map(MultiDateCompareRow.fromJson)
          .toList(),
      summary: json['summary'] is Map
          ? MultiDateCompareSummary.fromJson(json['summary'] as Map<String, dynamic>)
          : const MultiDateCompareSummary(countDates: 0, countWithData: 0),
      dataSource: (json['dataSource'] ?? 'simulated') as String,
    );
  }

  @override
  List<Object?> get props => [fieldId, indexName, dates, rows, summary, dataSource];
}
