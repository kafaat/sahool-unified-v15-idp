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
      summary: DiagnosisSummary.fromJson(json['summary'] as Map<String, dynamic>),
      actions: (json['actions'] as List)
          .map((a) => DiagnosisAction.fromJson(a as Map<String, dynamic>))
          .toList(),
      mapLayers: MapLayers.fromJson(json['map_layers'] as Map<String, dynamic>),
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
          .map((s) => TimelinePoint.fromJson(s as Map<String, dynamic>))
          .toList(),
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
