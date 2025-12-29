/// كيانات السجلات الإيكولوجية
/// Ecological Records Domain Entities
///
/// كيانات نظيفة للسجلات البيئية والاستدامة

/// نوع سجل الممارسة
enum PracticeStatus {
  planned,    // مخطط لها
  inProgress, // جاري التنفيذ
  implemented, // تم التنفيذ
  paused,     // متوقف
  abandoned,  // متروك
  ;

  String get value {
    switch (this) {
      case PracticeStatus.planned:
        return 'planned';
      case PracticeStatus.inProgress:
        return 'in_progress';
      case PracticeStatus.implemented:
        return 'implemented';
      case PracticeStatus.paused:
        return 'paused';
      case PracticeStatus.abandoned:
        return 'abandoned';
    }
  }

  static PracticeStatus fromString(String value) {
    switch (value) {
      case 'planned':
        return PracticeStatus.planned;
      case 'in_progress':
        return PracticeStatus.inProgress;
      case 'implemented':
        return PracticeStatus.implemented;
      case 'paused':
        return PracticeStatus.paused;
      case 'abandoned':
        return PracticeStatus.abandoned;
      default:
        return PracticeStatus.planned;
    }
  }
}

/// نوع مسح التنوع البيولوجي
enum BiodiversitySurveyType {
  speciesCount,       // عدد الأنواع
  habitatAssessment,  // تقييم الموئل
  beneficialInsects,  // الحشرات النافعة
  soilOrganisms,      // كائنات التربة
  general,            // عام
  ;

  String get value {
    switch (this) {
      case BiodiversitySurveyType.speciesCount:
        return 'species_count';
      case BiodiversitySurveyType.habitatAssessment:
        return 'habitat_assessment';
      case BiodiversitySurveyType.beneficialInsects:
        return 'beneficial_insects';
      case BiodiversitySurveyType.soilOrganisms:
        return 'soil_organisms';
      case BiodiversitySurveyType.general:
        return 'general';
    }
  }

  static BiodiversitySurveyType fromString(String value) {
    switch (value) {
      case 'species_count':
        return BiodiversitySurveyType.speciesCount;
      case 'habitat_assessment':
        return BiodiversitySurveyType.habitatAssessment;
      case 'beneficial_insects':
        return BiodiversitySurveyType.beneficialInsects;
      case 'soil_organisms':
        return BiodiversitySurveyType.soilOrganisms;
      case 'general':
        return BiodiversitySurveyType.general;
      default:
        return BiodiversitySurveyType.general;
    }
  }
}

/// حالة صحة التربة
enum SoilHealthStatus {
  poor,      // ضعيف
  fair,      // مقبول
  good,      // جيد
  excellent, // ممتاز
  ;

  String get value {
    switch (this) {
      case SoilHealthStatus.poor:
        return 'poor';
      case SoilHealthStatus.fair:
        return 'fair';
      case SoilHealthStatus.good:
        return 'good';
      case SoilHealthStatus.excellent:
        return 'excellent';
    }
  }

  static SoilHealthStatus fromString(String value) {
    switch (value) {
      case 'poor':
        return SoilHealthStatus.poor;
      case 'fair':
        return SoilHealthStatus.fair;
      case 'good':
        return SoilHealthStatus.good;
      case 'excellent':
        return SoilHealthStatus.excellent;
      default:
        return SoilHealthStatus.fair;
    }
  }
}

/// سجل التنوع البيولوجي
class BiodiversityRecord {
  final String id;
  final String farmId;
  final String tenantId;
  final DateTime surveyDate;
  final BiodiversitySurveyType surveyType;

  // العدّات
  final int? speciesCount;
  final int? beneficialInsectCount;
  final int? pollinatorCount;

  // تفاصيل
  final List<String> speciesObserved;
  final List<String> habitatFeatures;

  // التقييم
  final double? diversityIndex;
  final double? habitatQualityScore;

  // ملاحظات
  final String? notes;
  final String? notesAr;

  // البيانات الوصفية
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;

  const BiodiversityRecord({
    required this.id,
    required this.farmId,
    required this.tenantId,
    required this.surveyDate,
    required this.surveyType,
    this.speciesCount,
    this.beneficialInsectCount,
    this.pollinatorCount,
    this.speciesObserved = const [],
    this.habitatFeatures = const [],
    this.diversityIndex,
    this.habitatQualityScore,
    this.notes,
    this.notesAr,
    this.synced = false,
    required this.createdAt,
    required this.updatedAt,
  });

  /// درجة التنوع المحسوبة
  double get calculatedScore {
    if (habitatQualityScore != null) return habitatQualityScore!;
    if (speciesCount == null) return 0;
    // تقدير بسيط: كل نوع يساوي 5 نقاط، بحد أقصى 100
    return (speciesCount! * 5).clamp(0, 100).toDouble();
  }

  /// تحويل إلى JSON للـ API
  /// Convert to JSON for API
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'farm_id': farmId,
      'tenant_id': tenantId,
      'survey_date': surveyDate.toIso8601String(),
      'survey_type': surveyType.value,
      'species_count': speciesCount,
      'beneficial_insect_count': beneficialInsectCount,
      'pollinator_count': pollinatorCount,
      'species_observed': speciesObserved,
      'habitat_features': habitatFeatures,
      'diversity_index': diversityIndex,
      'habitat_quality_score': habitatQualityScore,
      'notes': notes,
      'notes_ar': notesAr,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  BiodiversityRecord copyWith({
    String? id,
    String? farmId,
    String? tenantId,
    DateTime? surveyDate,
    BiodiversitySurveyType? surveyType,
    int? speciesCount,
    int? beneficialInsectCount,
    int? pollinatorCount,
    List<String>? speciesObserved,
    List<String>? habitatFeatures,
    double? diversityIndex,
    double? habitatQualityScore,
    String? notes,
    String? notesAr,
    bool? synced,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return BiodiversityRecord(
      id: id ?? this.id,
      farmId: farmId ?? this.farmId,
      tenantId: tenantId ?? this.tenantId,
      surveyDate: surveyDate ?? this.surveyDate,
      surveyType: surveyType ?? this.surveyType,
      speciesCount: speciesCount ?? this.speciesCount,
      beneficialInsectCount: beneficialInsectCount ?? this.beneficialInsectCount,
      pollinatorCount: pollinatorCount ?? this.pollinatorCount,
      speciesObserved: speciesObserved ?? this.speciesObserved,
      habitatFeatures: habitatFeatures ?? this.habitatFeatures,
      diversityIndex: diversityIndex ?? this.diversityIndex,
      habitatQualityScore: habitatQualityScore ?? this.habitatQualityScore,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// سجل صحة التربة
class SoilHealthRecord {
  final String id;
  final String fieldId;
  final String tenantId;
  final DateTime sampleDate;
  final int? sampleDepthCm;

  // الخصائص الفيزيائية
  final double? organicMatterPercent;
  final String? soilTexture;
  final double? bulkDensity;
  final double? waterInfiltrationRate;
  final double? aggregateStability;

  // المؤشرات البيولوجية
  final int? earthwormCount;
  final double? microbialBiomass;
  final double? respirationRate;

  // الخصائص الكيميائية
  final double? phLevel;
  final double? ecLevel;
  final double? cecLevel;

  // التقييم العام
  final double? healthScore;
  final SoilHealthStatus? status;

  // ملاحظات
  final String? notes;
  final String? notesAr;
  final String? labReportUrl;

  // البيانات الوصفية
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;

  const SoilHealthRecord({
    required this.id,
    required this.fieldId,
    required this.tenantId,
    required this.sampleDate,
    this.sampleDepthCm,
    this.organicMatterPercent,
    this.soilTexture,
    this.bulkDensity,
    this.waterInfiltrationRate,
    this.aggregateStability,
    this.earthwormCount,
    this.microbialBiomass,
    this.respirationRate,
    this.phLevel,
    this.ecLevel,
    this.cecLevel,
    this.healthScore,
    this.status,
    this.notes,
    this.notesAr,
    this.labReportUrl,
    this.synced = false,
    required this.createdAt,
    required this.updatedAt,
  });

  /// حساب درجة الصحة المحسوبة
  double get calculatedHealthScore {
    if (healthScore != null) return healthScore!;

    double score = 50; // قيمة افتراضية

    // المادة العضوية
    if (organicMatterPercent != null) {
      if (organicMatterPercent! >= 3) score += 15;
      else if (organicMatterPercent! >= 2) score += 10;
      else if (organicMatterPercent! >= 1) score += 5;
    }

    // الديدان
    if (earthwormCount != null) {
      if (earthwormCount! >= 10) score += 15;
      else if (earthwormCount! >= 5) score += 10;
      else if (earthwormCount! >= 1) score += 5;
    }

    // درجة الحموضة
    if (phLevel != null) {
      if (phLevel! >= 6 && phLevel! <= 7.5) score += 10;
      else if (phLevel! >= 5.5 && phLevel! <= 8) score += 5;
    }

    return score.clamp(0, 100);
  }

  /// الحالة المحسوبة
  SoilHealthStatus get calculatedStatus {
    if (status != null) return status!;
    final score = calculatedHealthScore;
    if (score >= 80) return SoilHealthStatus.excellent;
    if (score >= 60) return SoilHealthStatus.good;
    if (score >= 40) return SoilHealthStatus.fair;
    return SoilHealthStatus.poor;
  }

  /// تحويل إلى JSON للـ API
  /// Convert to JSON for API
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'field_id': fieldId,
      'tenant_id': tenantId,
      'sample_date': sampleDate.toIso8601String(),
      'sample_depth_cm': sampleDepthCm,
      'organic_matter_percent': organicMatterPercent,
      'soil_texture': soilTexture,
      'bulk_density': bulkDensity,
      'water_infiltration_rate': waterInfiltrationRate,
      'aggregate_stability': aggregateStability,
      'earthworm_count': earthwormCount,
      'microbial_biomass': microbialBiomass,
      'respiration_rate': respirationRate,
      'ph_level': phLevel,
      'ec_level': ecLevel,
      'cec_level': cecLevel,
      'health_score': healthScore,
      'status': status?.value,
      'notes': notes,
      'notes_ar': notesAr,
      'lab_report_url': labReportUrl,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  SoilHealthRecord copyWith({
    String? id,
    String? fieldId,
    String? tenantId,
    DateTime? sampleDate,
    int? sampleDepthCm,
    double? organicMatterPercent,
    String? soilTexture,
    double? bulkDensity,
    double? waterInfiltrationRate,
    double? aggregateStability,
    int? earthwormCount,
    double? microbialBiomass,
    double? respirationRate,
    double? phLevel,
    double? ecLevel,
    double? cecLevel,
    double? healthScore,
    SoilHealthStatus? status,
    String? notes,
    String? notesAr,
    String? labReportUrl,
    bool? synced,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return SoilHealthRecord(
      id: id ?? this.id,
      fieldId: fieldId ?? this.fieldId,
      tenantId: tenantId ?? this.tenantId,
      sampleDate: sampleDate ?? this.sampleDate,
      sampleDepthCm: sampleDepthCm ?? this.sampleDepthCm,
      organicMatterPercent: organicMatterPercent ?? this.organicMatterPercent,
      soilTexture: soilTexture ?? this.soilTexture,
      bulkDensity: bulkDensity ?? this.bulkDensity,
      waterInfiltrationRate: waterInfiltrationRate ?? this.waterInfiltrationRate,
      aggregateStability: aggregateStability ?? this.aggregateStability,
      earthwormCount: earthwormCount ?? this.earthwormCount,
      microbialBiomass: microbialBiomass ?? this.microbialBiomass,
      respirationRate: respirationRate ?? this.respirationRate,
      phLevel: phLevel ?? this.phLevel,
      ecLevel: ecLevel ?? this.ecLevel,
      cecLevel: cecLevel ?? this.cecLevel,
      healthScore: healthScore ?? this.healthScore,
      status: status ?? this.status,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      labReportUrl: labReportUrl ?? this.labReportUrl,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// سجل الحفاظ على المياه
class WaterConservationRecord {
  final String id;
  final String farmId;
  final String? fieldId;
  final String tenantId;
  final DateTime recordDate;
  final String periodType; // daily, weekly, monthly, seasonal

  // استخدام المياه
  final double? waterUsedLiters;
  final String? waterSource;
  final String? irrigationMethod;

  // مقاييس الكفاءة
  final double? waterPerHectare;
  final double? efficiencyPercentage;
  final double? comparisonToBaseline;

  // ممارسات الحفاظ
  final bool mulchingApplied;
  final bool dripIrrigationUsed;
  final double? rainwaterHarvestedLiters;

  // ملاحظات
  final String? notes;
  final String? notesAr;

  // البيانات الوصفية
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;

  const WaterConservationRecord({
    required this.id,
    required this.farmId,
    this.fieldId,
    required this.tenantId,
    required this.recordDate,
    required this.periodType,
    this.waterUsedLiters,
    this.waterSource,
    this.irrigationMethod,
    this.waterPerHectare,
    this.efficiencyPercentage,
    this.comparisonToBaseline,
    this.mulchingApplied = false,
    this.dripIrrigationUsed = false,
    this.rainwaterHarvestedLiters,
    this.notes,
    this.notesAr,
    this.synced = false,
    required this.createdAt,
    required this.updatedAt,
  });

  /// هل الكفاءة جيدة؟
  bool get isEfficient => (efficiencyPercentage ?? 0) >= 70;

  /// نسبة التوفير
  double get savingsPercentage => comparisonToBaseline ?? 0;

  /// تحويل إلى JSON للـ API
  /// Convert to JSON for API
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'farm_id': farmId,
      'field_id': fieldId,
      'tenant_id': tenantId,
      'record_date': recordDate.toIso8601String(),
      'period_type': periodType,
      'water_used_liters': waterUsedLiters,
      'water_source': waterSource,
      'irrigation_method': irrigationMethod,
      'water_per_hectare': waterPerHectare,
      'efficiency_percentage': efficiencyPercentage,
      'comparison_to_baseline': comparisonToBaseline,
      'mulching_applied': mulchingApplied,
      'drip_irrigation_used': dripIrrigationUsed,
      'rainwater_harvested_liters': rainwaterHarvestedLiters,
      'notes': notes,
      'notes_ar': notesAr,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  WaterConservationRecord copyWith({
    String? id,
    String? farmId,
    String? fieldId,
    String? tenantId,
    DateTime? recordDate,
    String? periodType,
    double? waterUsedLiters,
    String? waterSource,
    String? irrigationMethod,
    double? waterPerHectare,
    double? efficiencyPercentage,
    double? comparisonToBaseline,
    bool? mulchingApplied,
    bool? dripIrrigationUsed,
    double? rainwaterHarvestedLiters,
    String? notes,
    String? notesAr,
    bool? synced,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return WaterConservationRecord(
      id: id ?? this.id,
      farmId: farmId ?? this.farmId,
      fieldId: fieldId ?? this.fieldId,
      tenantId: tenantId ?? this.tenantId,
      recordDate: recordDate ?? this.recordDate,
      periodType: periodType ?? this.periodType,
      waterUsedLiters: waterUsedLiters ?? this.waterUsedLiters,
      waterSource: waterSource ?? this.waterSource,
      irrigationMethod: irrigationMethod ?? this.irrigationMethod,
      waterPerHectare: waterPerHectare ?? this.waterPerHectare,
      efficiencyPercentage: efficiencyPercentage ?? this.efficiencyPercentage,
      comparisonToBaseline: comparisonToBaseline ?? this.comparisonToBaseline,
      mulchingApplied: mulchingApplied ?? this.mulchingApplied,
      dripIrrigationUsed: dripIrrigationUsed ?? this.dripIrrigationUsed,
      rainwaterHarvestedLiters: rainwaterHarvestedLiters ?? this.rainwaterHarvestedLiters,
      notes: notes ?? this.notes,
      notesAr: notesAr ?? this.notesAr,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// سجل الممارسة الإيكولوجية
class FarmPracticeRecord {
  final String id;
  final String farmId;
  final String? fieldId;
  final String tenantId;

  // تفاصيل الممارسة
  final String practiceId;
  final String practiceName;
  final String? practiceNameAr;
  final String category;

  // التنفيذ
  final PracticeStatus status;
  final DateTime? startDate;
  final DateTime? implementationDate;

  // التفاصيل
  final String? implementationNotes;
  final String? implementationNotesAr;
  final List<String> materialsUsed;
  final double? laborHours;
  final double? costEstimate;

  // النتائج
  final List<String> observedBenefits;
  final List<String> challenges;
  final int? effectivenessRating; // 1-5

  // ربط GlobalGAP
  final List<String> globalgapControlPoints;

  // البيانات الوصفية
  final bool synced;
  final DateTime createdAt;
  final DateTime updatedAt;

  const FarmPracticeRecord({
    required this.id,
    required this.farmId,
    this.fieldId,
    required this.tenantId,
    required this.practiceId,
    required this.practiceName,
    this.practiceNameAr,
    required this.category,
    required this.status,
    this.startDate,
    this.implementationDate,
    this.implementationNotes,
    this.implementationNotesAr,
    this.materialsUsed = const [],
    this.laborHours,
    this.costEstimate,
    this.observedBenefits = const [],
    this.challenges = const [],
    this.effectivenessRating,
    this.globalgapControlPoints = const [],
    this.synced = false,
    required this.createdAt,
    required this.updatedAt,
  });

  /// هل الممارسة مكتملة؟
  bool get isCompleted => status == PracticeStatus.implemented;

  /// هل تدعم GlobalGAP؟
  bool get supportsGlobalGap => globalgapControlPoints.isNotEmpty;

  /// تقييم الفعالية كنسبة مئوية
  int get effectivenessPercentage => (effectivenessRating ?? 0) * 20;

  /// تحويل إلى JSON للـ API
  /// Convert to JSON for API
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'farm_id': farmId,
      'field_id': fieldId,
      'tenant_id': tenantId,
      'practice_id': practiceId,
      'practice_name': practiceName,
      'practice_name_ar': practiceNameAr,
      'category': category,
      'status': status.value,
      'start_date': startDate?.toIso8601String(),
      'implementation_date': implementationDate?.toIso8601String(),
      'implementation_notes': implementationNotes,
      'implementation_notes_ar': implementationNotesAr,
      'materials_used': materialsUsed,
      'labor_hours': laborHours,
      'cost_estimate': costEstimate,
      'observed_benefits': observedBenefits,
      'challenges': challenges,
      'effectiveness_rating': effectivenessRating,
      'globalgap_control_points': globalgapControlPoints,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  FarmPracticeRecord copyWith({
    String? id,
    String? farmId,
    String? fieldId,
    String? tenantId,
    String? practiceId,
    String? practiceName,
    String? practiceNameAr,
    String? category,
    PracticeStatus? status,
    DateTime? startDate,
    DateTime? implementationDate,
    String? implementationNotes,
    String? implementationNotesAr,
    List<String>? materialsUsed,
    double? laborHours,
    double? costEstimate,
    List<String>? observedBenefits,
    List<String>? challenges,
    int? effectivenessRating,
    List<String>? globalgapControlPoints,
    bool? synced,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return FarmPracticeRecord(
      id: id ?? this.id,
      farmId: farmId ?? this.farmId,
      fieldId: fieldId ?? this.fieldId,
      tenantId: tenantId ?? this.tenantId,
      practiceId: practiceId ?? this.practiceId,
      practiceName: practiceName ?? this.practiceName,
      practiceNameAr: practiceNameAr ?? this.practiceNameAr,
      category: category ?? this.category,
      status: status ?? this.status,
      startDate: startDate ?? this.startDate,
      implementationDate: implementationDate ?? this.implementationDate,
      implementationNotes: implementationNotes ?? this.implementationNotes,
      implementationNotesAr: implementationNotesAr ?? this.implementationNotesAr,
      materialsUsed: materialsUsed ?? this.materialsUsed,
      laborHours: laborHours ?? this.laborHours,
      costEstimate: costEstimate ?? this.costEstimate,
      observedBenefits: observedBenefits ?? this.observedBenefits,
      challenges: challenges ?? this.challenges,
      effectivenessRating: effectivenessRating ?? this.effectivenessRating,
      globalgapControlPoints: globalgapControlPoints ?? this.globalgapControlPoints,
      synced: synced ?? this.synced,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }
}

/// بيانات لوحة المعلومات الإيكولوجية
/// Ecological Dashboard Data
class EcologicalDashboardData {
  final double overallScore;
  final double biodiversityScore;
  final double soilHealthScore;
  final double waterEfficiencyScore;
  final int totalPractices;
  final int implementedPractices;

  final BiodiversityRecord? latestBiodiversityRecord;
  final SoilHealthRecord? latestSoilHealthRecord;
  final WaterConservationRecord? latestWaterRecord;

  final int totalRecordsCount;
  final DateTime? lastUpdated;

  const EcologicalDashboardData({
    required this.overallScore,
    required this.biodiversityScore,
    required this.soilHealthScore,
    required this.waterEfficiencyScore,
    required this.totalPractices,
    required this.implementedPractices,
    this.latestBiodiversityRecord,
    this.latestSoilHealthRecord,
    this.latestWaterRecord,
    required this.totalRecordsCount,
    this.lastUpdated,
  });

  /// نسبة تنفيذ الممارسات
  /// Practice implementation percentage
  double get practiceImplementationRate {
    if (totalPractices == 0) return 0;
    return (implementedPractices / totalPractices * 100);
  }

  /// هل البيانات محدثة؟ (آخر 30 يوم)
  /// Is data fresh? (within last 30 days)
  bool get isFresh {
    if (lastUpdated == null) return false;
    return DateTime.now().difference(lastUpdated!).inDays <= 30;
  }
}
