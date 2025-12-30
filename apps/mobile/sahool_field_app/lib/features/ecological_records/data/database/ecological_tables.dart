import 'package:drift/drift.dart';

/// Ecological Records Database Tables
/// جداول قاعدة بيانات السجلات البيئية
///
/// This file defines Drift database tables for storing ecological agriculture
/// records in the Sahool Field mobile app. All records support offline-first
/// operation with eventual sync to the backend.
///
/// Tables:
/// - BiodiversityRecords: Biodiversity surveys and species monitoring
/// - SoilHealthRecords: Soil health assessments and testing
/// - WaterConservationRecords: Water usage and conservation tracking
/// - FarmPracticeRecords: Ecological farming practices

// ============================================================
// Biodiversity Records Table - سجلات التنوع البيولوجي
// ============================================================

/// Stores biodiversity surveys including species counts, insect surveys,
/// pollinator monitoring, and habitat assessments.
/// يخزن مسوحات التنوع البيولوجي بما في ذلك عدد الأنواع ومسوحات الحشرات
/// ومراقبة الملقحات وتقييمات الموائل
@TableIndex(name: 'biodiversity_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'biodiversity_field_idx', columns: {#fieldId})
@TableIndex(name: 'biodiversity_survey_date_idx', columns: {#surveyDate})
@TableIndex(name: 'biodiversity_synced_idx', columns: {#synced})
class BiodiversityRecords extends Table {
  /// Unique identifier - معرف فريد
  TextColumn get id => text()();

  /// Tenant ID for multi-tenancy - معرف المستأجر للتعدد
  TextColumn get tenantId => text()();

  /// Field ID where survey was conducted - معرف الحقل حيث تم إجراء المسح
  TextColumn get fieldId => text()();

  /// Date of the survey - تاريخ المسح
  DateTimeColumn get surveyDate => dateTime()();

  /// Type of survey: species_count, insect_survey, pollinator_monitoring, habitat_assessment
  /// نوع المسح: عدد الأنواع، مسح الحشرات، مراقبة الملقحات، تقييم الموائل
  TextColumn get surveyType => text()();

  /// Total species count (optional) - إجمالي عدد الأنواع (اختياري)
  IntColumn get speciesCount => integer().nullable()();

  /// Insect diversity index (optional) - مؤشر تنوع الحشرات (اختياري)
  IntColumn get insectDiversity => integer().nullable()();

  /// Pollinator count (optional) - عدد الملقحات (اختياري)
  IntColumn get pollinatorCount => integer().nullable()();

  /// Habitat features as JSON array (e.g., hedgerows, ponds, wildflower strips)
  /// ميزات الموائل كمصفوفة JSON (مثل: التحوطات، البرك، شرائط الزهور البرية)
  TextColumn get habitatFeatures => text()();

  /// Additional notes - ملاحظات إضافية
  TextColumn get notes => text().nullable()();

  /// Photo paths as JSON array - مسارات الصور كمصفوفة JSON
  TextColumn get photos => text()();

  /// Record creation timestamp - وقت إنشاء السجل
  DateTimeColumn get createdAt => dateTime()();

  /// Sync status - حالة المزامنة
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

// ============================================================
// Soil Health Records Table - سجلات صحة التربة
// ============================================================

/// Stores soil health assessments including nutrient levels, pH, organic matter,
/// and overall health scores.
/// يخزن تقييمات صحة التربة بما في ذلك مستويات المغذيات والحموضة والمادة العضوية
/// ودرجات الصحة الإجمالية
@TableIndex(name: 'soil_health_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'soil_health_field_idx', columns: {#fieldId})
@TableIndex(name: 'soil_health_sample_date_idx', columns: {#sampleDate})
@TableIndex(name: 'soil_health_synced_idx', columns: {#synced})
class SoilHealthRecords extends Table {
  /// Unique identifier - معرف فريد
  TextColumn get id => text()();

  /// Tenant ID for multi-tenancy - معرف المستأجر للتعدد
  TextColumn get tenantId => text()();

  /// Field ID where sample was taken - معرف الحقل حيث تم أخذ العينة
  TextColumn get fieldId => text()();

  /// Date of soil sample - تاريخ عينة التربة
  DateTimeColumn get sampleDate => dateTime()();

  /// Sample depth in centimeters - عمق العينة بالسنتيمتر
  RealColumn get sampleDepth => real()();

  /// Organic matter percentage (optional) - نسبة المادة العضوية (اختياري)
  RealColumn get organicMatter => real().nullable()();

  /// Soil pH level (optional) - مستوى حموضة التربة (اختياري)
  RealColumn get ph => real().nullable()();

  /// Nitrogen level in ppm (optional) - مستوى النيتروجين بالجزء في المليون (اختياري)
  RealColumn get nitrogen => real().nullable()();

  /// Phosphorus level in ppm (optional) - مستوى الفوسفور بالجزء في المليون (اختياري)
  RealColumn get phosphorus => real().nullable()();

  /// Potassium level in ppm (optional) - مستوى البوتاسيوم بالجزء في المليون (اختياري)
  RealColumn get potassium => real().nullable()();

  /// Soil texture: clay, loam, sandy, etc. (optional) - قوام التربة: طينية، طميية، رملية، إلخ (اختياري)
  TextColumn get texture => text().nullable()();

  /// Overall health score 0-100 (optional) - درجة الصحة الإجمالية 0-100 (اختياري)
  IntColumn get healthScore => integer().nullable()();

  /// Additional notes - ملاحظات إضافية
  TextColumn get notes => text().nullable()();

  /// Record creation timestamp - وقت إنشاء السجل
  DateTimeColumn get createdAt => dateTime()();

  /// Sync status - حالة المزامنة
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

// ============================================================
// Water Conservation Records Table - سجلات الحفاظ على المياه
// ============================================================

/// Stores water usage and conservation tracking including irrigation methods,
/// water sources, and efficiency metrics.
/// يخزن استخدام المياه وتتبع الحفاظ عليها بما في ذلك طرق الري
/// ومصادر المياه ومقاييس الكفاءة
@TableIndex(name: 'water_conservation_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'water_conservation_field_idx', columns: {#fieldId})
@TableIndex(name: 'water_conservation_record_date_idx', columns: {#recordDate})
@TableIndex(name: 'water_conservation_synced_idx', columns: {#synced})
class WaterConservationRecords extends Table {
  /// Unique identifier - معرف فريد
  TextColumn get id => text()();

  /// Tenant ID for multi-tenancy - معرف المستأجر للتعدد
  TextColumn get tenantId => text()();

  /// Field ID where water was used - معرف الحقل حيث تم استخدام المياه
  TextColumn get fieldId => text()();

  /// Date of water usage record - تاريخ سجل استخدام المياه
  DateTimeColumn get recordDate => dateTime()();

  /// Water usage in cubic meters - استخدام المياه بالمتر المكعب
  RealColumn get waterUsageCubicMeters => real()();

  /// Water source: well, canal, rainwater, mixed - مصدر المياه: بئر، قناة، مياه الأمطار، مختلط
  TextColumn get waterSource => text()();

  /// Irrigation method: drip, sprinkler, flood, rainfed - طريقة الري: بالتنقيط، الرش، الغمر، بعلي
  TextColumn get irrigationMethod => text()();

  /// Efficiency percentage 0-100 (optional) - نسبة الكفاءة 0-100 (اختياري)
  RealColumn get efficiencyPercent => real().nullable()();

  /// Conservation practices as JSON array (e.g., mulching, drip irrigation)
  /// ممارسات الحفاظ على المياه كمصفوفة JSON (مثل: التغطية، الري بالتنقيط)
  TextColumn get conservationPractices => text()();

  /// Additional notes - ملاحظات إضافية
  TextColumn get notes => text().nullable()();

  /// Record creation timestamp - وقت إنشاء السجل
  DateTimeColumn get createdAt => dateTime()();

  /// Sync status - حالة المزامنة
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}

// ============================================================
// Farm Practice Records Table - سجلات الممارسات الزراعية
// ============================================================

/// Stores ecological farming practices including composting, cover cropping,
/// no-till farming, and companion planting with effectiveness tracking.
/// يخزن الممارسات الزراعية البيئية بما في ذلك التسميد، الزراعة التغطية،
/// الزراعة بدون حرث، والزراعة المرافقة مع تتبع الفعالية
@TableIndex(name: 'farm_practice_tenant_idx', columns: {#tenantId})
@TableIndex(name: 'farm_practice_field_idx', columns: {#fieldId})
@TableIndex(name: 'farm_practice_type_idx', columns: {#practiceType})
@TableIndex(name: 'farm_practice_status_idx', columns: {#status})
@TableIndex(name: 'farm_practice_synced_idx', columns: {#synced})
class FarmPracticeRecords extends Table {
  /// Unique identifier - معرف فريد
  TextColumn get id => text()();

  /// Tenant ID for multi-tenancy - معرف المستأجر للتعدد
  TextColumn get tenantId => text()();

  /// Field ID where practice is applied - معرف الحقل حيث يتم تطبيق الممارسة
  TextColumn get fieldId => text()();

  /// Practice type: composting, cover_cropping, no_till, companion_planting, etc.
  /// نوع الممارسة: التسميد، الزراعة التغطية، بدون حرث، الزراعة المرافقة، إلخ
  TextColumn get practiceType => text()();

  /// Start date of the practice - تاريخ بدء الممارسة
  DateTimeColumn get startDate => dateTime()();

  /// Status: planned, in_progress, completed, paused - الحالة: مخطط، قيد التنفيذ، مكتمل، متوقف
  TextColumn get status => text()();

  /// Area where practice is applied in dunums (optional) - المساحة المطبقة بالدونم (اختياري)
  RealColumn get areaAppliedDunums => real().nullable()();

  /// Effectiveness rating 1-5 stars (optional) - تقييم الفعالية 1-5 نجوم (اختياري)
  IntColumn get effectivenessRating => integer().nullable()();

  /// Benefits as JSON array (e.g., improved soil, reduced pests)
  /// الفوائد كمصفوفة JSON (مثل: تحسين التربة، تقليل الآفات)
  TextColumn get benefits => text()();

  /// Challenges as JSON array (e.g., labor intensive, initial cost)
  /// التحديات كمصفوفة JSON (مثل: كثيفة العمالة، التكلفة الأولية)
  TextColumn get challenges => text()();

  /// Additional notes - ملاحظات إضافية
  TextColumn get notes => text().nullable()();

  /// Record creation timestamp - وقت إنشاء السجل
  DateTimeColumn get createdAt => dateTime()();

  /// Sync status - حالة المزامنة
  BoolColumn get synced => boolean().withDefault(const Constant(false))();

  @override
  Set<Column> get primaryKey => {id};
}
