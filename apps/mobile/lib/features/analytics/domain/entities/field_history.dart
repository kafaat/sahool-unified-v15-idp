/// Field History Domain Entities
/// كيانات تاريخ الحقل - Domain Layer نظيف (بدون Flutter)
///
/// يمثل السجل التاريخي لصحة الحقل عبر الزمن

/// سجل قراءة NDVI واحدة
class NdviRecord {
  /// تاريخ القراءة
  final DateTime date;

  /// قيمة NDVI (0.0 إلى 1.0)
  final double value;

  const NdviRecord({
    required this.date,
    required this.value,
  });

  /// إنشاء من JSON
  factory NdviRecord.fromJson(Map<String, dynamic> json) {
    return NdviRecord(
      date: DateTime.parse(json['date'] as String),
      value: (json['value'] as num).toDouble(),
    );
  }

  /// تحويل إلى JSON
  Map<String, dynamic> toJson() => {
        'date': date.toIso8601String(),
        'value': value,
      };

  /// هل القراءة صحية؟ (NDVI > 0.6)
  bool get isHealthy => value >= 0.6;

  /// هل القراءة حرجة؟ (NDVI < 0.3)
  bool get isCritical => value < 0.3;

  /// تصنيف القراءة
  NdviLevel get level {
    if (value >= 0.7) return NdviLevel.excellent;
    if (value >= 0.5) return NdviLevel.good;
    if (value >= 0.3) return NdviLevel.moderate;
    return NdviLevel.poor;
  }

  @override
  String toString() => 'NdviRecord($date: $value)';
}

/// مستويات NDVI
enum NdviLevel {
  /// ممتاز (0.7+)
  excellent,

  /// جيد (0.5 - 0.7)
  good,

  /// متوسط (0.3 - 0.5)
  moderate,

  /// ضعيف (< 0.3)
  poor,
}

/// تحليلات الحقل الكاملة
class FieldAnalytics {
  /// معرف الحقل
  final String fieldId;

  /// السجل التاريخي
  final List<NdviRecord> history;

  /// توقع الإنتاجية (طن/هكتار)
  final double yieldForecast;

  /// الفترة الزمنية (بالأيام)
  final int periodDays;

  const FieldAnalytics({
    required this.fieldId,
    required this.history,
    required this.yieldForecast,
    this.periodDays = 30,
  });

  /// هل الاتجاه العام إيجابي؟
  bool get isImproving {
    if (history.length < 2) return false;

    // مقارنة آخر قراءة بمتوسط القراءات السابقة
    final last = history.last.value;
    final previousAvg = history
            .sublist(0, history.length - 1)
            .map((e) => e.value)
            .reduce((a, b) => a + b) /
        (history.length - 1);

    return last >= previousAvg;
  }

  /// معدل التغير (نسبة مئوية)
  double get changeRate {
    if (history.length < 2) return 0;

    final first = history.first.value;
    final last = history.last.value;

    if (first == 0) return 0;
    return ((last - first) / first) * 100;
  }

  /// متوسط NDVI
  double get averageNdvi {
    if (history.isEmpty) return 0;
    return history.map((e) => e.value).reduce((a, b) => a + b) / history.length;
  }

  /// أعلى قراءة
  NdviRecord? get peakRecord {
    if (history.isEmpty) return null;
    return history.reduce((a, b) => a.value > b.value ? a : b);
  }

  /// أدنى قراءة
  NdviRecord? get lowestRecord {
    if (history.isEmpty) return null;
    return history.reduce((a, b) => a.value < b.value ? a : b);
  }

  /// الاتجاه العام
  TrendDirection get trend {
    if (history.length < 3) return TrendDirection.stable;

    final changePercent = changeRate;
    if (changePercent > 5) return TrendDirection.improving;
    if (changePercent < -5) return TrendDirection.declining;
    return TrendDirection.stable;
  }

  /// إنشاء من JSON
  factory FieldAnalytics.fromJson(Map<String, dynamic> json) {
    return FieldAnalytics(
      fieldId: json['field_id'] as String,
      history: (json['history'] as List)
          .map((e) => NdviRecord.fromJson(e as Map<String, dynamic>))
          .toList(),
      yieldForecast: (json['yield_forecast'] as num).toDouble(),
      periodDays: json['period_days'] as int? ?? 30,
    );
  }

  /// تحويل إلى JSON
  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'history': history.map((e) => e.toJson()).toList(),
        'yield_forecast': yieldForecast,
        'period_days': periodDays,
      };

  @override
  String toString() =>
      'FieldAnalytics($fieldId: ${history.length} records, trend: ${trend.name})';
}

/// اتجاه التغير
enum TrendDirection {
  /// تحسن
  improving,

  /// استقرار
  stable,

  /// تراجع
  declining,
}
