import 'dart:convert';
import 'package:uuid/uuid.dart';

import '../../../../core/storage/database.dart' as db;
import '../../domain/entities/ecological_entities.dart';

/// مستودع السجلات الإيكولوجية - نمط Offline-First
/// Ecological Records Repository - Offline-first data access
///
/// يدير:
/// - سجلات التنوع البيولوجي
/// - سجلات صحة التربة
/// - سجلات الحفاظ على المياه
/// - سجلات الممارسات الزراعية
/// - بيانات لوحة المعلومات
class EcologicalRepository {
  final db.AppDatabase _db;
  final _uuid = const Uuid();

  EcologicalRepository({
    required db.AppDatabase database,
  }) : _db = database;

  // ============================================================
  // Biodiversity Records - سجلات التنوع البيولوجي
  // ============================================================

  /// الحصول على جميع سجلات التنوع البيولوجي
  /// Get all biodiversity records for tenant
  Future<List<BiodiversityRecord>> getAllBiodiversityRecords(
      String tenantId) async {
    final dbRecords = await _db.getAllBiodiversityRecords(tenantId);
    return dbRecords.map(_mapBiodiversityDbToEntity).toList();
  }

  /// مراقبة سجلات التنوع البيولوجي للحقل
  /// Watch biodiversity records for a field (live stream)
  Stream<List<BiodiversityRecord>> watchBiodiversityRecords(
    String tenantId,
    String fieldId,
  ) {
    return _db.watchBiodiversityRecords(tenantId, fieldId).map(
          (dbRecords) => dbRecords.map(_mapBiodiversityDbToEntity).toList(),
        );
  }

  /// حفظ سجل التنوع البيولوجي (Offline-First)
  /// Save biodiversity record with offline-first pattern
  Future<void> saveBiodiversityRecordOfflineFirst(
      BiodiversityRecord record) async {
    // 1. حفظ محلياً في قاعدة البيانات
    // Save to local database
    await _db.upsertBiodiversityRecord(
      db.BiodiversityRecordsCompanion.insert(
        id: record.id,
        farmId: record.farmId,
        tenantId: record.tenantId,
        surveyDate: record.surveyDate,
        surveyType: record.surveyType.value,
        speciesCount: db.Value(record.speciesCount),
        beneficialInsectCount: db.Value(record.beneficialInsectCount),
        pollinatorCount: db.Value(record.pollinatorCount),
        speciesObserved: record.speciesObserved.join(','),
        habitatFeatures: record.habitatFeatures.join(','),
        diversityIndex: db.Value(record.diversityIndex),
        habitatQualityScore: db.Value(record.habitatQualityScore),
        notes: db.Value(record.notes),
        notesAr: db.Value(record.notesAr),
        createdAt: record.createdAt,
        updatedAt: record.updatedAt,
      ),
    );

    // 2. إضافة إلى صندوق الإرسال للمزامنة
    // Add to outbox for sync
    await _db.queueOutboxItem(
      tenantId: record.tenantId,
      entityType: 'biodiversity_record',
      entityId: record.id,
      apiEndpoint: '/api/v1/ecological/biodiversity',
      method: 'POST',
      payload: jsonEncode(record.toJson()),
    );

    print('✅ سجل التنوع البيولوجي تم حفظه محلياً: ${record.id}');
  }

  /// تحويل من قاعدة البيانات إلى كيان
  /// Map database entity to domain entity
  BiodiversityRecord _mapBiodiversityDbToEntity(
      db.BiodiversityRecord dbRecord) {
    return BiodiversityRecord(
      id: dbRecord.id,
      farmId: dbRecord.farmId,
      tenantId: dbRecord.tenantId,
      surveyDate: dbRecord.surveyDate,
      surveyType: BiodiversitySurveyType.fromString(dbRecord.surveyType),
      speciesCount: dbRecord.speciesCount,
      beneficialInsectCount: dbRecord.beneficialInsectCount,
      pollinatorCount: dbRecord.pollinatorCount,
      speciesObserved: dbRecord.speciesObserved.isNotEmpty
          ? dbRecord.speciesObserved.split(',')
          : [],
      habitatFeatures: dbRecord.habitatFeatures.isNotEmpty
          ? dbRecord.habitatFeatures.split(',')
          : [],
      diversityIndex: dbRecord.diversityIndex,
      habitatQualityScore: dbRecord.habitatQualityScore,
      notes: dbRecord.notes,
      notesAr: dbRecord.notesAr,
      synced: dbRecord.synced,
      createdAt: dbRecord.createdAt,
      updatedAt: dbRecord.updatedAt,
    );
  }

  // ============================================================
  // Soil Health Records - سجلات صحة التربة
  // ============================================================

  /// الحصول على جميع سجلات صحة التربة
  /// Get all soil health records for tenant
  Future<List<SoilHealthRecord>> getAllSoilHealthRecords(
      String tenantId) async {
    final dbRecords = await _db.getAllSoilHealthRecords(tenantId);
    return dbRecords.map(_mapSoilHealthDbToEntity).toList();
  }

  /// مراقبة سجلات صحة التربة للحقل
  /// Watch soil health records for a field (live stream)
  Stream<List<SoilHealthRecord>> watchSoilHealthRecords(
    String tenantId,
    String fieldId,
  ) {
    return _db.watchSoilHealthRecords(tenantId, fieldId).map(
          (dbRecords) => dbRecords.map(_mapSoilHealthDbToEntity).toList(),
        );
  }

  /// حفظ سجل صحة التربة (Offline-First)
  /// Save soil health record with offline-first pattern
  Future<void> saveSoilHealthRecordOfflineFirst(
      SoilHealthRecord record) async {
    // 1. حفظ محلياً في قاعدة البيانات
    // Save to local database
    await _db.upsertSoilHealthRecord(
      db.SoilHealthRecordsCompanion.insert(
        id: record.id,
        fieldId: record.fieldId,
        tenantId: record.tenantId,
        sampleDate: record.sampleDate,
        sampleDepthCm: db.Value(record.sampleDepthCm),
        organicMatterPercent: db.Value(record.organicMatterPercent),
        soilTexture: db.Value(record.soilTexture),
        bulkDensity: db.Value(record.bulkDensity),
        waterInfiltrationRate: db.Value(record.waterInfiltrationRate),
        aggregateStability: db.Value(record.aggregateStability),
        earthwormCount: db.Value(record.earthwormCount),
        microbialBiomass: db.Value(record.microbialBiomass),
        respirationRate: db.Value(record.respirationRate),
        phLevel: db.Value(record.phLevel),
        ecLevel: db.Value(record.ecLevel),
        cecLevel: db.Value(record.cecLevel),
        healthScore: db.Value(record.healthScore),
        status: db.Value(record.status?.value),
        notes: db.Value(record.notes),
        notesAr: db.Value(record.notesAr),
        labReportUrl: db.Value(record.labReportUrl),
        createdAt: record.createdAt,
        updatedAt: record.updatedAt,
      ),
    );

    // 2. إضافة إلى صندوق الإرسال للمزامنة
    // Add to outbox for sync
    await _db.queueOutboxItem(
      tenantId: record.tenantId,
      entityType: 'soil_health_record',
      entityId: record.id,
      apiEndpoint: '/api/v1/ecological/soil-health',
      method: 'POST',
      payload: jsonEncode(record.toJson()),
    );

    print('✅ سجل صحة التربة تم حفظه محلياً: ${record.id}');
  }

  /// تحويل من قاعدة البيانات إلى كيان
  /// Map database entity to domain entity
  SoilHealthRecord _mapSoilHealthDbToEntity(db.SoilHealthRecord dbRecord) {
    return SoilHealthRecord(
      id: dbRecord.id,
      fieldId: dbRecord.fieldId,
      tenantId: dbRecord.tenantId,
      sampleDate: dbRecord.sampleDate,
      sampleDepthCm: dbRecord.sampleDepthCm,
      organicMatterPercent: dbRecord.organicMatterPercent,
      soilTexture: dbRecord.soilTexture,
      bulkDensity: dbRecord.bulkDensity,
      waterInfiltrationRate: dbRecord.waterInfiltrationRate,
      aggregateStability: dbRecord.aggregateStability,
      earthwormCount: dbRecord.earthwormCount,
      microbialBiomass: dbRecord.microbialBiomass,
      respirationRate: dbRecord.respirationRate,
      phLevel: dbRecord.phLevel,
      ecLevel: dbRecord.ecLevel,
      cecLevel: dbRecord.cecLevel,
      healthScore: dbRecord.healthScore,
      status: dbRecord.status != null
          ? SoilHealthStatus.fromString(dbRecord.status!)
          : null,
      notes: dbRecord.notes,
      notesAr: dbRecord.notesAr,
      labReportUrl: dbRecord.labReportUrl,
      synced: dbRecord.synced,
      createdAt: dbRecord.createdAt,
      updatedAt: dbRecord.updatedAt,
    );
  }

  // ============================================================
  // Water Conservation Records - سجلات الحفاظ على المياه
  // ============================================================

  /// الحصول على جميع سجلات المياه
  /// Get all water conservation records for tenant
  Future<List<WaterConservationRecord>> getAllWaterRecords(
      String tenantId) async {
    final dbRecords = await _db.getAllWaterRecords(tenantId);
    return dbRecords.map(_mapWaterDbToEntity).toList();
  }

  /// مراقبة سجلات المياه للحقل
  /// Watch water conservation records for a field (live stream)
  Stream<List<WaterConservationRecord>> watchWaterRecords(
    String tenantId,
    String fieldId,
  ) {
    return _db.watchWaterRecords(tenantId, fieldId).map(
          (dbRecords) => dbRecords.map(_mapWaterDbToEntity).toList(),
        );
  }

  /// حفظ سجل المياه (Offline-First)
  /// Save water conservation record with offline-first pattern
  Future<void> saveWaterRecordOfflineFirst(
      WaterConservationRecord record) async {
    // 1. حفظ محلياً في قاعدة البيانات
    // Save to local database
    await _db.upsertWaterRecord(
      db.WaterConservationRecordsCompanion.insert(
        id: record.id,
        farmId: record.farmId,
        fieldId: db.Value(record.fieldId),
        tenantId: record.tenantId,
        recordDate: record.recordDate,
        periodType: record.periodType,
        waterUsedLiters: db.Value(record.waterUsedLiters),
        waterSource: db.Value(record.waterSource),
        irrigationMethod: db.Value(record.irrigationMethod),
        waterPerHectare: db.Value(record.waterPerHectare),
        efficiencyPercentage: db.Value(record.efficiencyPercentage),
        comparisonToBaseline: db.Value(record.comparisonToBaseline),
        mulchingApplied: record.mulchingApplied,
        dripIrrigationUsed: record.dripIrrigationUsed,
        rainwaterHarvestedLiters: db.Value(record.rainwaterHarvestedLiters),
        notes: db.Value(record.notes),
        notesAr: db.Value(record.notesAr),
        createdAt: record.createdAt,
        updatedAt: record.updatedAt,
      ),
    );

    // 2. إضافة إلى صندوق الإرسال للمزامنة
    // Add to outbox for sync
    await _db.queueOutboxItem(
      tenantId: record.tenantId,
      entityType: 'water_conservation_record',
      entityId: record.id,
      apiEndpoint: '/api/v1/ecological/water-conservation',
      method: 'POST',
      payload: jsonEncode(record.toJson()),
    );

    print('✅ سجل الحفاظ على المياه تم حفظه محلياً: ${record.id}');
  }

  /// تحويل من قاعدة البيانات إلى كيان
  /// Map database entity to domain entity
  WaterConservationRecord _mapWaterDbToEntity(
      db.WaterConservationRecord dbRecord) {
    return WaterConservationRecord(
      id: dbRecord.id,
      farmId: dbRecord.farmId,
      fieldId: dbRecord.fieldId,
      tenantId: dbRecord.tenantId,
      recordDate: dbRecord.recordDate,
      periodType: dbRecord.periodType,
      waterUsedLiters: dbRecord.waterUsedLiters,
      waterSource: dbRecord.waterSource,
      irrigationMethod: dbRecord.irrigationMethod,
      waterPerHectare: dbRecord.waterPerHectare,
      efficiencyPercentage: dbRecord.efficiencyPercentage,
      comparisonToBaseline: dbRecord.comparisonToBaseline,
      mulchingApplied: dbRecord.mulchingApplied,
      dripIrrigationUsed: dbRecord.dripIrrigationUsed,
      rainwaterHarvestedLiters: dbRecord.rainwaterHarvestedLiters,
      notes: dbRecord.notes,
      notesAr: dbRecord.notesAr,
      synced: dbRecord.synced,
      createdAt: dbRecord.createdAt,
      updatedAt: dbRecord.updatedAt,
    );
  }

  // ============================================================
  // Farm Practice Records - سجلات الممارسات الزراعية
  // ============================================================

  /// الحصول على جميع سجلات الممارسات
  /// Get all practice records for tenant
  Future<List<FarmPracticeRecord>> getAllPracticeRecords(
      String tenantId) async {
    final dbRecords = await _db.getAllPracticeRecords(tenantId);
    return dbRecords.map(_mapPracticeDbToEntity).toList();
  }

  /// مراقبة سجلات الممارسات للحقل
  /// Watch practice records for a field (live stream)
  Stream<List<FarmPracticeRecord>> watchPracticeRecords(
    String tenantId,
    String fieldId,
  ) {
    return _db.watchPracticeRecords(tenantId, fieldId).map(
          (dbRecords) => dbRecords.map(_mapPracticeDbToEntity).toList(),
        );
  }

  /// حفظ سجل الممارسة (Offline-First)
  /// Save practice record with offline-first pattern
  Future<void> savePracticeRecordOfflineFirst(
      FarmPracticeRecord record) async {
    // 1. حفظ محلياً في قاعدة البيانات
    // Save to local database
    await _db.upsertPracticeRecord(
      db.FarmPracticeRecordsCompanion.insert(
        id: record.id,
        farmId: record.farmId,
        fieldId: db.Value(record.fieldId),
        tenantId: record.tenantId,
        practiceId: record.practiceId,
        practiceName: record.practiceName,
        practiceNameAr: db.Value(record.practiceNameAr),
        category: record.category,
        status: record.status.value,
        startDate: db.Value(record.startDate),
        implementationDate: db.Value(record.implementationDate),
        implementationNotes: db.Value(record.implementationNotes),
        implementationNotesAr: db.Value(record.implementationNotesAr),
        materialsUsed: record.materialsUsed.join(','),
        laborHours: db.Value(record.laborHours),
        costEstimate: db.Value(record.costEstimate),
        observedBenefits: record.observedBenefits.join(','),
        challenges: record.challenges.join(','),
        effectivenessRating: db.Value(record.effectivenessRating),
        globalgapControlPoints: record.globalgapControlPoints.join(','),
        createdAt: record.createdAt,
        updatedAt: record.updatedAt,
      ),
    );

    // 2. إضافة إلى صندوق الإرسال للمزامنة
    // Add to outbox for sync
    await _db.queueOutboxItem(
      tenantId: record.tenantId,
      entityType: 'farm_practice_record',
      entityId: record.id,
      apiEndpoint: '/api/v1/ecological/practices',
      method: 'POST',
      payload: jsonEncode(record.toJson()),
    );

    print('✅ سجل الممارسة الزراعية تم حفظه محلياً: ${record.id}');
  }

  /// تحويل من قاعدة البيانات إلى كيان
  /// Map database entity to domain entity
  FarmPracticeRecord _mapPracticeDbToEntity(db.FarmPracticeRecord dbRecord) {
    return FarmPracticeRecord(
      id: dbRecord.id,
      farmId: dbRecord.farmId,
      fieldId: dbRecord.fieldId,
      tenantId: dbRecord.tenantId,
      practiceId: dbRecord.practiceId,
      practiceName: dbRecord.practiceName,
      practiceNameAr: dbRecord.practiceNameAr,
      category: dbRecord.category,
      status: PracticeStatus.fromString(dbRecord.status),
      startDate: dbRecord.startDate,
      implementationDate: dbRecord.implementationDate,
      implementationNotes: dbRecord.implementationNotes,
      implementationNotesAr: dbRecord.implementationNotesAr,
      materialsUsed: dbRecord.materialsUsed.isNotEmpty
          ? dbRecord.materialsUsed.split(',')
          : [],
      laborHours: dbRecord.laborHours,
      costEstimate: dbRecord.costEstimate,
      observedBenefits: dbRecord.observedBenefits.isNotEmpty
          ? dbRecord.observedBenefits.split(',')
          : [],
      challenges:
          dbRecord.challenges.isNotEmpty ? dbRecord.challenges.split(',') : [],
      effectivenessRating: dbRecord.effectivenessRating,
      globalgapControlPoints: dbRecord.globalgapControlPoints.isNotEmpty
          ? dbRecord.globalgapControlPoints.split(',')
          : [],
      synced: dbRecord.synced,
      createdAt: dbRecord.createdAt,
      updatedAt: dbRecord.updatedAt,
    );
  }

  // ============================================================
  // Dashboard Data - بيانات لوحة المعلومات
  // ============================================================

  /// الحصول على بيانات لوحة المعلومات الإيكولوجية
  /// Get ecological dashboard data for a field
  Future<EcologicalDashboardData> getDashboardData(
    String tenantId,
    String fieldId,
  ) async {
    // جلب أحدث السجلات
    // Fetch latest records
    final biodiversityRecords =
        await _db.getBiodiversityRecordsForField(tenantId, fieldId);
    final soilHealthRecords =
        await _db.getSoilHealthRecordsForField(tenantId, fieldId);
    final waterRecords = await _db.getWaterRecordsForField(tenantId, fieldId);
    final practiceRecords =
        await _db.getPracticeRecordsForField(tenantId, fieldId);

    // تحويل إلى كيانات
    // Map to entities
    final biodiversityList =
        biodiversityRecords.map(_mapBiodiversityDbToEntity).toList();
    final soilHealthList =
        soilHealthRecords.map(_mapSoilHealthDbToEntity).toList();
    final waterList = waterRecords.map(_mapWaterDbToEntity).toList();
    final practiceList = practiceRecords.map(_mapPracticeDbToEntity).toList();

    // حساب الدرجات
    // Calculate scores
    final biodiversityScore = biodiversityList.isNotEmpty
        ? biodiversityList.first.calculatedScore
        : 0.0;

    final soilHealthScore = soilHealthList.isNotEmpty
        ? soilHealthList.first.calculatedHealthScore
        : 0.0;

    final waterEfficiencyScore = waterList.isNotEmpty
        ? (waterList.first.efficiencyPercentage ?? 0.0)
        : 0.0;

    // حساب عدد الممارسات المنفذة
    // Calculate implemented practices
    final implementedCount = practiceList
        .where((p) => p.status == PracticeStatus.implemented)
        .length;

    // حساب الدرجة الإجمالية (متوسط الدرجات الثلاث)
    // Calculate overall score (average of three scores)
    final overallScore =
        (biodiversityScore + soilHealthScore + waterEfficiencyScore) / 3;

    // آخر تحديث
    // Last update date
    DateTime? lastUpdated;
    final allDates = [
      ...biodiversityList.map((r) => r.updatedAt),
      ...soilHealthList.map((r) => r.updatedAt),
      ...waterList.map((r) => r.updatedAt),
      ...practiceList.map((r) => r.updatedAt),
    ];
    if (allDates.isNotEmpty) {
      allDates.sort((a, b) => b.compareTo(a));
      lastUpdated = allDates.first;
    }

    return EcologicalDashboardData(
      overallScore: overallScore,
      biodiversityScore: biodiversityScore,
      soilHealthScore: soilHealthScore,
      waterEfficiencyScore: waterEfficiencyScore,
      totalPractices: practiceList.length,
      implementedPractices: implementedCount,
      latestBiodiversityRecord:
          biodiversityList.isNotEmpty ? biodiversityList.first : null,
      latestSoilHealthRecord:
          soilHealthList.isNotEmpty ? soilHealthList.first : null,
      latestWaterRecord: waterList.isNotEmpty ? waterList.first : null,
      totalRecordsCount: biodiversityList.length +
          soilHealthList.length +
          waterList.length +
          practiceList.length,
      lastUpdated: lastUpdated,
    );
  }
}
