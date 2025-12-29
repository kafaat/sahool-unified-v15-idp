import 'package:drift/drift.dart';
import '../../../../core/storage/database.dart';
import 'ecological_tables.dart';

part 'ecological_dao.g.dart';

@DriftAccessor(tables: [
  BiodiversityRecords,
  SoilHealthRecords,
  WaterConservationRecords,
  FarmPracticeRecords,
])
class EcologicalDao extends DatabaseAccessor<AppDatabase> with _$EcologicalDaoMixin {
  EcologicalDao(AppDatabase db) : super(db);

  // ═══════════════════════════════════════════════════════════════════════════
  // Biodiversity Records | سجلات التنوع البيولوجي
  // ═══════════════════════════════════════════════════════════════════════════

  Future<List<BiodiversityRecord>> getAllBiodiversityRecords(String tenantId) {
    return (select(biodiversityRecords)
      ..where((r) => r.tenantId.equals(tenantId))
      ..orderBy([(r) => OrderingTerm.desc(r.surveyDate)]))
      .get();
  }

  Stream<List<BiodiversityRecord>> watchBiodiversityRecords(String tenantId, String fieldId) {
    return (select(biodiversityRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.surveyDate)]))
      .watch();
  }

  Future<void> insertBiodiversityRecord(BiodiversityRecordsCompanion record) {
    return into(biodiversityRecords).insert(record);
  }

  Future<void> updateBiodiversityRecord(BiodiversityRecordsCompanion record) {
    return (update(biodiversityRecords)
      ..where((r) => r.id.equals(record.id.value)))
      .write(record);
  }

  Future<BiodiversityRecord?> getLatestBiodiversityRecord(String tenantId, String fieldId) {
    return (select(biodiversityRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.surveyDate)])
      ..limit(1))
      .getSingleOrNull();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Soil Health Records | سجلات صحة التربة
  // ═══════════════════════════════════════════════════════════════════════════

  Future<List<SoilHealthRecord>> getAllSoilHealthRecords(String tenantId) {
    return (select(soilHealthRecords)
      ..where((r) => r.tenantId.equals(tenantId))
      ..orderBy([(r) => OrderingTerm.desc(r.sampleDate)]))
      .get();
  }

  Stream<List<SoilHealthRecord>> watchSoilHealthRecords(String tenantId, String fieldId) {
    return (select(soilHealthRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.sampleDate)]))
      .watch();
  }

  Future<void> insertSoilHealthRecord(SoilHealthRecordsCompanion record) {
    return into(soilHealthRecords).insert(record);
  }

  Future<SoilHealthRecord?> getLatestSoilHealthRecord(String tenantId, String fieldId) {
    return (select(soilHealthRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.sampleDate)])
      ..limit(1))
      .getSingleOrNull();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Water Conservation Records | سجلات الحفاظ على المياه
  // ═══════════════════════════════════════════════════════════════════════════

  Future<List<WaterConservationRecord>> getAllWaterRecords(String tenantId) {
    return (select(waterConservationRecords)
      ..where((r) => r.tenantId.equals(tenantId))
      ..orderBy([(r) => OrderingTerm.desc(r.recordDate)]))
      .get();
  }

  Stream<List<WaterConservationRecord>> watchWaterRecords(String tenantId, String fieldId) {
    return (select(waterConservationRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.recordDate)]))
      .watch();
  }

  Future<void> insertWaterRecord(WaterConservationRecordsCompanion record) {
    return into(waterConservationRecords).insert(record);
  }

  Future<WaterConservationRecord?> getLatestWaterRecord(String tenantId, String fieldId) {
    return (select(waterConservationRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.recordDate)])
      ..limit(1))
      .getSingleOrNull();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Farm Practice Records | سجلات الممارسات الزراعية
  // ═══════════════════════════════════════════════════════════════════════════

  Future<List<FarmPracticeRecord>> getAllPracticeRecords(String tenantId) {
    return (select(farmPracticeRecords)
      ..where((r) => r.tenantId.equals(tenantId))
      ..orderBy([(r) => OrderingTerm.desc(r.startDate)]))
      .get();
  }

  Stream<List<FarmPracticeRecord>> watchPracticeRecords(String tenantId, String fieldId) {
    return (select(farmPracticeRecords)
      ..where((r) => r.tenantId.equals(tenantId) & r.fieldId.equals(fieldId))
      ..orderBy([(r) => OrderingTerm.desc(r.startDate)]))
      .watch();
  }

  Future<void> insertPracticeRecord(FarmPracticeRecordsCompanion record) {
    return into(farmPracticeRecords).insert(record);
  }

  Future<void> updatePracticeRecord(FarmPracticeRecordsCompanion record) {
    return (update(farmPracticeRecords)
      ..where((r) => r.id.equals(record.id.value)))
      .write(record);
  }

  Future<List<FarmPracticeRecord>> getActivePractices(String tenantId, String fieldId) {
    return (select(farmPracticeRecords)
      ..where((r) =>
          r.tenantId.equals(tenantId) &
          r.fieldId.equals(fieldId) &
          r.status.isIn(['planned', 'in_progress'])))
      .get();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Dashboard Queries | استعلامات لوحة التحكم
  // ═══════════════════════════════════════════════════════════════════════════

  Future<int> countBiodiversityRecords(String tenantId) async {
    final count = biodiversityRecords.id.count();
    final query = selectOnly(biodiversityRecords)
      ..addColumns([count])
      ..where(biodiversityRecords.tenantId.equals(tenantId));
    final result = await query.getSingle();
    return result.read(count) ?? 0;
  }

  Future<int> countSoilHealthRecords(String tenantId) async {
    final count = soilHealthRecords.id.count();
    final query = selectOnly(soilHealthRecords)
      ..addColumns([count])
      ..where(soilHealthRecords.tenantId.equals(tenantId));
    final result = await query.getSingle();
    return result.read(count) ?? 0;
  }

  Future<int> countWaterRecords(String tenantId) async {
    final count = waterConservationRecords.id.count();
    final query = selectOnly(waterConservationRecords)
      ..addColumns([count])
      ..where(waterConservationRecords.tenantId.equals(tenantId));
    final result = await query.getSingle();
    return result.read(count) ?? 0;
  }

  Future<int> countPracticeRecords(String tenantId) async {
    final count = farmPracticeRecords.id.count();
    final query = selectOnly(farmPracticeRecords)
      ..addColumns([count])
      ..where(farmPracticeRecords.tenantId.equals(tenantId));
    final result = await query.getSingle();
    return result.read(count) ?? 0;
  }
}
