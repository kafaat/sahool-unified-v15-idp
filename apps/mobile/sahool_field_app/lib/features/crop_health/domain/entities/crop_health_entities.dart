library;

/// SAHOOL Crop Health Domain Entities
/// نماذج صحة المحاصيل

/// مؤشرات الغطاء النباتي
class VegetationIndices {
  final double ndvi;
  final double evi;
  final double ndre;
  final double lci;
  final double ndwi;
  final double savi;

  const VegetationIndices({
    required this.ndvi,
    required this.evi,
    required this.ndre,
    required this.lci,
    required this.ndwi,
    required this.savi,
  });

  factory VegetationIndices.fromJson(Map<String, dynamic> json) {
    return VegetationIndices(
      ndvi: (json['ndvi'] as num).toDouble(),
      evi: (json['evi'] as num).toDouble(),
      ndre: (json['ndre'] as num).toDouble(),
      lci: (json['lci'] as num).toDouble(),
      ndwi: (json['ndwi'] as num).toDouble(),
      savi: (json['savi'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'ndvi': ndvi,
        'evi': evi,
        'ndre': ndre,
        'lci': lci,
        'ndwi': ndwi,
        'savi': savi,
      };

  VegetationIndices copyWith({
    double? ndvi,
    double? evi,
    double? ndre,
    double? lci,
    double? ndwi,
    double? savi,
  }) {
    return VegetationIndices(
      ndvi: ndvi ?? this.ndvi,
      evi: evi ?? this.evi,
      ndre: ndre ?? this.ndre,
      lci: lci ?? this.lci,
      ndwi: ndwi ?? this.ndwi,
      savi: savi ?? this.savi,
    );
  }

  /// حالة الصحة النباتية بناءً على NDVI
  String get healthStatus {
    if (ndvi >= 0.7) return 'excellent';
    if (ndvi >= 0.5) return 'good';
    if (ndvi >= 0.35) return 'moderate';
    if (ndvi >= 0.2) return 'poor';
    return 'critical';
  }

  String get healthStatusAr {
    switch (healthStatus) {
      case 'excellent':
        return 'ممتاز';
      case 'good':
        return 'جيد';
      case 'moderate':
        return 'متوسط';
      case 'poor':
        return 'ضعيف';
      case 'critical':
        return 'حرج';
      default:
        return 'غير معروف';
    }
  }
}

/// منطقة داخل الحقل
class Zone {
  final String zoneId;
  final String name;
  final String? nameAr;
  final double? areaHectares;
  final Map<String, dynamic>? geometry;

  const Zone({
    required this.zoneId,
    required this.name,
    this.nameAr,
    this.areaHectares,
    this.geometry,
  });

  factory Zone.fromJson(Map<String, dynamic> json) {
    return Zone(
      zoneId: json['zone_id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String?,
      areaHectares: (json['area_hectares'] as num?)?.toDouble(),
      geometry: json['geometry'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'zone_id': zoneId,
        'name': name,
        'name_ar': nameAr,
        'area_hectares': areaHectares,
        'geometry': geometry,
      };

  Zone copyWith({
    String? zoneId,
    String? name,
    String? nameAr,
    double? areaHectares,
    Map<String, dynamic>? geometry,
  }) {
    return Zone(
      zoneId: zoneId ?? this.zoneId,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      areaHectares: areaHectares ?? this.areaHectares,
      geometry: geometry ?? this.geometry,
    );
  }
}

/// إجراء موصى به
class DiagnosisAction {
  final String zoneId;
  final String type; // irrigation, fertilization, scouting, none
  final String priority; // P0, P1, P2, P3
  final String title;
  final String? titleEn;
  final String reason;
  final String? reasonEn;
  final Map<String, dynamic> evidence;
  final int? recommendedWindowHours;
  final String? recommendedDoseHint;
  final String? severity;

  const DiagnosisAction({
    required this.zoneId,
    required this.type,
    required this.priority,
    required this.title,
    this.titleEn,
    required this.reason,
    this.reasonEn,
    required this.evidence,
    this.recommendedWindowHours,
    this.recommendedDoseHint,
    this.severity,
  });

  factory DiagnosisAction.fromJson(Map<String, dynamic> json) {
    return DiagnosisAction(
      zoneId: json['zone_id'] as String,
      type: json['type'] as String,
      priority: json['priority'] as String,
      title: json['title'] as String,
      titleEn: json['title_en'] as String?,
      reason: json['reason'] as String,
      reasonEn: json['reason_en'] as String?,
      evidence: json['evidence'] as Map<String, dynamic>? ?? {},
      recommendedWindowHours: json['recommended_window_hours'] as int?,
      recommendedDoseHint: json['recommended_dose_hint'] as String?,
      severity: json['severity'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'zone_id': zoneId,
        'type': type,
        'priority': priority,
        'title': title,
        'title_en': titleEn,
        'reason': reason,
        'reason_en': reasonEn,
        'evidence': evidence,
        'recommended_window_hours': recommendedWindowHours,
        'recommended_dose_hint': recommendedDoseHint,
        'severity': severity,
      };

  DiagnosisAction copyWith({
    String? zoneId,
    String? type,
    String? priority,
    String? title,
    String? titleEn,
    String? reason,
    String? reasonEn,
    Map<String, dynamic>? evidence,
    int? recommendedWindowHours,
    String? recommendedDoseHint,
    String? severity,
  }) {
    return DiagnosisAction(
      zoneId: zoneId ?? this.zoneId,
      type: type ?? this.type,
      priority: priority ?? this.priority,
      title: title ?? this.title,
      titleEn: titleEn ?? this.titleEn,
      reason: reason ?? this.reason,
      reasonEn: reasonEn ?? this.reasonEn,
      evidence: evidence ?? this.evidence,
      recommendedWindowHours:
          recommendedWindowHours ?? this.recommendedWindowHours,
      recommendedDoseHint: recommendedDoseHint ?? this.recommendedDoseHint,
      severity: severity ?? this.severity,
    );
  }

  /// أيقونة نوع الإجراء
  String get typeIcon {
    switch (type) {
      case 'irrigation':
        return '💧';
      case 'fertilization':
        return '🌱';
      case 'scouting':
        return '🔍';
      default:
        return '✅';
    }
  }

  /// لون الأولوية
  String get priorityColor {
    switch (priority) {
      case 'P0':
        return '#EF4444'; // أحمر
      case 'P1':
        return '#F59E0B'; // برتقالي
      case 'P2':
        return '#3B82F6'; // أزرق
      default:
        return '#10B981'; // أخضر
    }
  }

  /// وصف الأولوية بالعربية
  String get priorityLabel {
    switch (priority) {
      case 'P0':
        return 'عاجل جداً';
      case 'P1':
        return 'مهم';
      case 'P2':
        return 'متوسط';
      default:
        return 'منخفض';
    }
  }
}

/// ملخص تشخيص الحقل
class DiagnosisSummary {
  final int zonesTotal;
  final int zonesCritical;
  final int zonesWarning;
  final int zonesOk;

  const DiagnosisSummary({
    required this.zonesTotal,
    required this.zonesCritical,
    required this.zonesWarning,
    required this.zonesOk,
  });

  factory DiagnosisSummary.fromJson(Map<String, dynamic> json) {
    return DiagnosisSummary(
      zonesTotal: json['zones_total'] as int,
      zonesCritical: json['zones_critical'] as int,
      zonesWarning: json['zones_warning'] as int,
      zonesOk: json['zones_ok'] as int,
    );
  }

  Map<String, dynamic> toJson() => {
        'zones_total': zonesTotal,
        'zones_critical': zonesCritical,
        'zones_warning': zonesWarning,
        'zones_ok': zonesOk,
      };

  DiagnosisSummary copyWith({
    int? zonesTotal,
    int? zonesCritical,
    int? zonesWarning,
    int? zonesOk,
  }) {
    return DiagnosisSummary(
      zonesTotal: zonesTotal ?? this.zonesTotal,
      zonesCritical: zonesCritical ?? this.zonesCritical,
      zonesWarning: zonesWarning ?? this.zonesWarning,
      zonesOk: zonesOk ?? this.zonesOk,
    );
  }
}

/// روابط طبقات الخريطة
class MapLayers {
  final String? ndviRasterUrl;
  final String? ndwiRasterUrl;
  final String? ndreRasterUrl;
  final String zonesGeojsonUrl;

  const MapLayers({
    this.ndviRasterUrl,
    this.ndwiRasterUrl,
    this.ndreRasterUrl,
    required this.zonesGeojsonUrl,
  });

  factory MapLayers.fromJson(Map<String, dynamic> json) {
    return MapLayers(
      ndviRasterUrl: json['ndvi_raster_url'] as String?,
      ndwiRasterUrl: json['ndwi_raster_url'] as String?,
      ndreRasterUrl: json['ndre_raster_url'] as String?,
      zonesGeojsonUrl: json['zones_geojson_url'] as String,
    );
  }

  Map<String, dynamic> toJson() => {
        'ndvi_raster_url': ndviRasterUrl,
        'ndwi_raster_url': ndwiRasterUrl,
        'ndre_raster_url': ndreRasterUrl,
        'zones_geojson_url': zonesGeojsonUrl,
      };

  MapLayers copyWith({
    String? ndviRasterUrl,
    String? ndwiRasterUrl,
    String? ndreRasterUrl,
    String? zonesGeojsonUrl,
  }) {
    return MapLayers(
      ndviRasterUrl: ndviRasterUrl ?? this.ndviRasterUrl,
      ndwiRasterUrl: ndwiRasterUrl ?? this.ndwiRasterUrl,
      ndreRasterUrl: ndreRasterUrl ?? this.ndreRasterUrl,
      zonesGeojsonUrl: zonesGeojsonUrl ?? this.zonesGeojsonUrl,
    );
  }
}

/// تشخيص كامل للحقل
class FieldDiagnosis {
  final String fieldId;
  final String date;
  final DiagnosisSummary summary;
  final List<DiagnosisAction> actions;
  final MapLayers mapLayers;

  const FieldDiagnosis({
    required this.fieldId,
    required this.date,
    required this.summary,
    required this.actions,
    required this.mapLayers,
  });

  factory FieldDiagnosis.fromJson(Map<String, dynamic> json) {
    return FieldDiagnosis(
      fieldId: json['field_id'] as String,
      date: json['date'] as String,
      summary: DiagnosisSummary.fromJson(json['summary']),
      actions: (json['actions'] as List)
          .map((a) => DiagnosisAction.fromJson(a))
          .toList(),
      mapLayers: MapLayers.fromJson(json['map_layers']),
    );
  }

  Map<String, dynamic> toJson() => {
        'field_id': fieldId,
        'date': date,
        'summary': summary.toJson(),
        'actions': actions.map((a) => a.toJson()).toList(),
        'map_layers': mapLayers.toJson(),
      };

  FieldDiagnosis copyWith({
    String? fieldId,
    String? date,
    DiagnosisSummary? summary,
    List<DiagnosisAction>? actions,
    MapLayers? mapLayers,
  }) {
    return FieldDiagnosis(
      fieldId: fieldId ?? this.fieldId,
      date: date ?? this.date,
      summary: summary ?? this.summary,
      actions: actions ?? this.actions,
      mapLayers: mapLayers ?? this.mapLayers,
    );
  }

  /// الإجراءات العاجلة (P0)
  List<DiagnosisAction> get urgentActions =>
      actions.where((a) => a.priority == 'P0').toList();

  /// الإجراءات المهمة (P1)
  List<DiagnosisAction> get importantActions =>
      actions.where((a) => a.priority == 'P1').toList();
}

/// نقطة في السلسلة الزمنية
class TimelinePoint {
  final String date;
  final double ndvi;
  final double? evi;
  final double? ndre;
  final double? ndwi;
  final double? lci;
  final double? savi;

  const TimelinePoint({
    required this.date,
    required this.ndvi,
    this.evi,
    this.ndre,
    this.ndwi,
    this.lci,
    this.savi,
  });

  factory TimelinePoint.fromJson(Map<String, dynamic> json) {
    return TimelinePoint(
      date: json['date'] as String,
      ndvi: (json['ndvi'] as num).toDouble(),
      evi: (json['evi'] as num?)?.toDouble(),
      ndre: (json['ndre'] as num?)?.toDouble(),
      ndwi: (json['ndwi'] as num?)?.toDouble(),
      lci: (json['lci'] as num?)?.toDouble(),
      savi: (json['savi'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() => {
        'date': date,
        'ndvi': ndvi,
        'evi': evi,
        'ndre': ndre,
        'ndwi': ndwi,
        'lci': lci,
        'savi': savi,
      };

  TimelinePoint copyWith({
    String? date,
    double? ndvi,
    double? evi,
    double? ndre,
    double? ndwi,
    double? lci,
    double? savi,
  }) {
    return TimelinePoint(
      date: date ?? this.date,
      ndvi: ndvi ?? this.ndvi,
      evi: evi ?? this.evi,
      ndre: ndre ?? this.ndre,
      ndwi: ndwi ?? this.ndwi,
      lci: lci ?? this.lci,
      savi: savi ?? this.savi,
    );
  }
}

/// السلسلة الزمنية للمنطقة
class ZoneTimeline {
  final String zoneId;
  final String fieldId;
  final List<TimelinePoint> series;

  const ZoneTimeline({
    required this.zoneId,
    required this.fieldId,
    required this.series,
  });

  factory ZoneTimeline.fromJson(Map<String, dynamic> json) {
    return ZoneTimeline(
      zoneId: json['zone_id'] as String,
      fieldId: json['field_id'] as String,
      series: (json['series'] as List)
          .map((s) => TimelinePoint.fromJson(s))
          .toList(),
    );
  }

  Map<String, dynamic> toJson() => {
        'zone_id': zoneId,
        'field_id': fieldId,
        'series': series.map((s) => s.toJson()).toList(),
      };

  ZoneTimeline copyWith({
    String? zoneId,
    String? fieldId,
    List<TimelinePoint>? series,
  }) {
    return ZoneTimeline(
      zoneId: zoneId ?? this.zoneId,
      fieldId: fieldId ?? this.fieldId,
      series: series ?? this.series,
    );
  }
}

/// مرحلة النمو
enum GrowthStage {
  seedling,
  rapid,
  mid,
  late;

  String get labelAr {
    switch (this) {
      case GrowthStage.seedling:
        return 'شتلة';
      case GrowthStage.rapid:
        return 'نمو سريع';
      case GrowthStage.mid:
        return 'منتصف الموسم';
      case GrowthStage.late:
        return 'نهاية الموسم';
    }
  }

  String get value => name;
}
