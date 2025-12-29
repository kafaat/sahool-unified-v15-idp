/// مزودات Riverpod للسجلات الإيكولوجية
/// Ecological Records Riverpod Providers
///
/// إدارة حالة السجلات البيئية والاستدامة
/// State management for environmental and sustainability records

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/storage/database.dart';
import '../../domain/entities/ecological_entities.dart';

// ============================================================
// Core Providers
// ============================================================

/// مزود قاعدة البيانات
/// Database provider
final databaseProvider = Provider<AppDatabase>((ref) {
  return AppDatabase();
});

/// مزود معرف المزرعة المحددة
/// Selected farm ID provider
final selectedFarmIdProvider = StateProvider<String?>((ref) => null);

/// مزود معرف الحقل المحدد
/// Selected field ID provider
final selectedFieldIdProvider = StateProvider<String?>((ref) => null);

/// مزود التاريخ المحدد
/// Selected date provider
final selectedDateProvider = StateProvider<DateTime>((ref) => DateTime.now());

// ============================================================
// Repository Provider (Placeholder - to be implemented)
// ============================================================

/// مزود مستودع السجلات الإيكولوجية
/// Ecological repository provider
///
/// ملاحظة: يحتاج إلى تنفيذ EcologicalRepository
/// Note: Requires EcologicalRepository implementation
// final ecologicalRepositoryProvider = Provider<EcologicalRepository>((ref) {
//   final db = ref.watch(databaseProvider);
//   return EcologicalRepository(db);
// });

// ============================================================
// Biodiversity State & Provider
// ============================================================

/// حالة سجلات التنوع البيولوجي
/// Biodiversity records state
class BiodiversityState {
  final bool isLoading;
  final List<BiodiversityRecord> records;
  final String? error;

  const BiodiversityState({
    this.isLoading = false,
    this.records = const [],
    this.error,
  });

  BiodiversityState copyWith({
    bool? isLoading,
    List<BiodiversityRecord>? records,
    String? error,
  }) {
    return BiodiversityState(
      isLoading: isLoading ?? this.isLoading,
      records: records ?? this.records,
      error: error,
    );
  }
}

/// مدير حالة التنوع البيولوجي
/// Biodiversity state notifier
class BiodiversityNotifier extends StateNotifier<BiodiversityState> {
  // final EcologicalRepository _repository;

  BiodiversityNotifier(
    // this._repository,
  ) : super(const BiodiversityState());

  /// تحميل سجلات التنوع البيولوجي
  /// Load biodiversity records
  Future<void> loadRecords({String? farmId}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // TODO: Implement repository call
      // final records = await _repository.getBiodiversityRecords(farmId: farmId);

      // Mock data for now
      final records = <BiodiversityRecord>[];

      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل سجلات التنوع البيولوجي: ${e.toString()}',
      );
    }
  }

  /// إضافة سجل تنوع بيولوجي جديد
  /// Add new biodiversity record
  Future<void> addRecord(BiodiversityRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.insertBiodiversityRecord(record);

      await loadRecords(farmId: record.farmId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل إضافة سجل التنوع البيولوجي: ${e.toString()}',
      );
    }
  }

  /// تحديث سجل تنوع بيولوجي
  /// Update biodiversity record
  Future<void> updateRecord(BiodiversityRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.updateBiodiversityRecord(record);

      await loadRecords(farmId: record.farmId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل تحديث سجل التنوع البيولوجي: ${e.toString()}',
      );
    }
  }

  /// حذف سجل تنوع بيولوجي
  /// Delete biodiversity record
  Future<void> deleteRecord(String recordId) async {
    try {
      // TODO: Implement repository call
      // await _repository.deleteBiodiversityRecord(recordId);

      state = state.copyWith(
        records: state.records.where((r) => r.id != recordId).toList(),
      );
    } catch (e) {
      state = state.copyWith(
        error: 'فشل حذف سجل التنوع البيولوجي: ${e.toString()}',
      );
    }
  }

  /// مسح الحالة
  /// Clear state
  void clear() {
    state = const BiodiversityState();
  }
}

/// مزود حالة التنوع البيولوجي
/// Biodiversity state provider
final biodiversityProvider =
    StateNotifierProvider<BiodiversityNotifier, BiodiversityState>((ref) {
  // final repository = ref.watch(ecologicalRepositoryProvider);
  return BiodiversityNotifier(
    // repository,
  );
});

// ============================================================
// Soil Health State & Provider
// ============================================================

/// حالة سجلات صحة التربة
/// Soil health records state
class SoilHealthState {
  final bool isLoading;
  final List<SoilHealthRecord> records;
  final String? error;

  const SoilHealthState({
    this.isLoading = false,
    this.records = const [],
    this.error,
  });

  SoilHealthState copyWith({
    bool? isLoading,
    List<SoilHealthRecord>? records,
    String? error,
  }) {
    return SoilHealthState(
      isLoading: isLoading ?? this.isLoading,
      records: records ?? this.records,
      error: error,
    );
  }
}

/// مدير حالة صحة التربة
/// Soil health state notifier
class SoilHealthNotifier extends StateNotifier<SoilHealthState> {
  // final EcologicalRepository _repository;

  SoilHealthNotifier(
    // this._repository,
  ) : super(const SoilHealthState());

  /// تحميل سجلات صحة التربة
  /// Load soil health records
  Future<void> loadRecords({String? fieldId}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // TODO: Implement repository call
      // final records = await _repository.getSoilHealthRecords(fieldId: fieldId);

      final records = <SoilHealthRecord>[];

      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل سجلات صحة التربة: ${e.toString()}',
      );
    }
  }

  /// إضافة سجل صحة تربة جديد
  /// Add new soil health record
  Future<void> addRecord(SoilHealthRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.insertSoilHealthRecord(record);

      await loadRecords(fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل إضافة سجل صحة التربة: ${e.toString()}',
      );
    }
  }

  /// تحديث سجل صحة التربة
  /// Update soil health record
  Future<void> updateRecord(SoilHealthRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.updateSoilHealthRecord(record);

      await loadRecords(fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل تحديث سجل صحة التربة: ${e.toString()}',
      );
    }
  }

  /// حذف سجل صحة التربة
  /// Delete soil health record
  Future<void> deleteRecord(String recordId) async {
    try {
      // TODO: Implement repository call
      // await _repository.deleteSoilHealthRecord(recordId);

      state = state.copyWith(
        records: state.records.where((r) => r.id != recordId).toList(),
      );
    } catch (e) {
      state = state.copyWith(
        error: 'فشل حذف سجل صحة التربة: ${e.toString()}',
      );
    }
  }

  /// مسح الحالة
  /// Clear state
  void clear() {
    state = const SoilHealthState();
  }
}

/// مزود حالة صحة التربة
/// Soil health state provider
final soilHealthProvider =
    StateNotifierProvider<SoilHealthNotifier, SoilHealthState>((ref) {
  // final repository = ref.watch(ecologicalRepositoryProvider);
  return SoilHealthNotifier(
    // repository,
  );
});

// ============================================================
// Water Conservation State & Provider
// ============================================================

/// حالة سجلات الحفاظ على المياه
/// Water conservation records state
class WaterConservationState {
  final bool isLoading;
  final List<WaterConservationRecord> records;
  final String? error;

  const WaterConservationState({
    this.isLoading = false,
    this.records = const [],
    this.error,
  });

  WaterConservationState copyWith({
    bool? isLoading,
    List<WaterConservationRecord>? records,
    String? error,
  }) {
    return WaterConservationState(
      isLoading: isLoading ?? this.isLoading,
      records: records ?? this.records,
      error: error,
    );
  }
}

/// مدير حالة الحفاظ على المياه
/// Water conservation state notifier
class WaterConservationNotifier extends StateNotifier<WaterConservationState> {
  // final EcologicalRepository _repository;

  WaterConservationNotifier(
    // this._repository,
  ) : super(const WaterConservationState());

  /// تحميل سجلات الحفاظ على المياه
  /// Load water conservation records
  Future<void> loadRecords({String? farmId, String? fieldId}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // TODO: Implement repository call
      // final records = await _repository.getWaterConservationRecords(
      //   farmId: farmId,
      //   fieldId: fieldId,
      // );

      final records = <WaterConservationRecord>[];

      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل سجلات الحفاظ على المياه: ${e.toString()}',
      );
    }
  }

  /// إضافة سجل حفاظ على المياه جديد
  /// Add new water conservation record
  Future<void> addRecord(WaterConservationRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.insertWaterConservationRecord(record);

      await loadRecords(farmId: record.farmId, fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل إضافة سجل الحفاظ على المياه: ${e.toString()}',
      );
    }
  }

  /// تحديث سجل الحفاظ على المياه
  /// Update water conservation record
  Future<void> updateRecord(WaterConservationRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.updateWaterConservationRecord(record);

      await loadRecords(farmId: record.farmId, fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل تحديث سجل الحفاظ على المياه: ${e.toString()}',
      );
    }
  }

  /// حذف سجل الحفاظ على المياه
  /// Delete water conservation record
  Future<void> deleteRecord(String recordId) async {
    try {
      // TODO: Implement repository call
      // await _repository.deleteWaterConservationRecord(recordId);

      state = state.copyWith(
        records: state.records.where((r) => r.id != recordId).toList(),
      );
    } catch (e) {
      state = state.copyWith(
        error: 'فشل حذف سجل الحفاظ على المياه: ${e.toString()}',
      );
    }
  }

  /// مسح الحالة
  /// Clear state
  void clear() {
    state = const WaterConservationState();
  }
}

/// مزود حالة الحفاظ على المياه
/// Water conservation state provider
final waterConservationProvider =
    StateNotifierProvider<WaterConservationNotifier, WaterConservationState>(
        (ref) {
  // final repository = ref.watch(ecologicalRepositoryProvider);
  return WaterConservationNotifier(
    // repository,
  );
});

// ============================================================
// Farm Practices State & Provider
// ============================================================

/// حالة سجلات الممارسات الزراعية
/// Farm practices records state
class FarmPracticesState {
  final bool isLoading;
  final List<FarmPracticeRecord> records;
  final String? error;

  const FarmPracticesState({
    this.isLoading = false,
    this.records = const [],
    this.error,
  });

  FarmPracticesState copyWith({
    bool? isLoading,
    List<FarmPracticeRecord>? records,
    String? error,
  }) {
    return FarmPracticesState(
      isLoading: isLoading ?? this.isLoading,
      records: records ?? this.records,
      error: error,
    );
  }
}

/// مدير حالة الممارسات الزراعية
/// Farm practices state notifier
class FarmPracticesNotifier extends StateNotifier<FarmPracticesState> {
  // final EcologicalRepository _repository;

  FarmPracticesNotifier(
    // this._repository,
  ) : super(const FarmPracticesState());

  /// تحميل سجلات الممارسات الزراعية
  /// Load farm practices records
  Future<void> loadRecords({String? farmId, String? fieldId}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // TODO: Implement repository call
      // final records = await _repository.getFarmPracticeRecords(
      //   farmId: farmId,
      //   fieldId: fieldId,
      // );

      final records = <FarmPracticeRecord>[];

      state = state.copyWith(isLoading: false, records: records);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل سجلات الممارسات الزراعية: ${e.toString()}',
      );
    }
  }

  /// إضافة سجل ممارسة زراعية جديدة
  /// Add new farm practice record
  Future<void> addRecord(FarmPracticeRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.insertFarmPracticeRecord(record);

      await loadRecords(farmId: record.farmId, fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل إضافة سجل الممارسة الزراعية: ${e.toString()}',
      );
    }
  }

  /// تحديث سجل الممارسة الزراعية
  /// Update farm practice record
  Future<void> updateRecord(FarmPracticeRecord record) async {
    try {
      // TODO: Implement repository call
      // await _repository.updateFarmPracticeRecord(record);

      await loadRecords(farmId: record.farmId, fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل تحديث سجل الممارسة الزراعية: ${e.toString()}',
      );
    }
  }

  /// تحديث حالة الممارسة
  /// Update practice status
  Future<void> updateStatus({
    required String recordId,
    required PracticeStatus status,
  }) async {
    try {
      final record = state.records.firstWhere((r) => r.id == recordId);
      final updated = record.copyWith(status: status);

      // TODO: Implement repository call
      // await _repository.updateFarmPracticeRecord(updated);

      await loadRecords(farmId: record.farmId, fieldId: record.fieldId);
    } catch (e) {
      state = state.copyWith(
        error: 'فشل تحديث حالة الممارسة: ${e.toString()}',
      );
    }
  }

  /// حذف سجل الممارسة الزراعية
  /// Delete farm practice record
  Future<void> deleteRecord(String recordId) async {
    try {
      // TODO: Implement repository call
      // await _repository.deleteFarmPracticeRecord(recordId);

      state = state.copyWith(
        records: state.records.where((r) => r.id != recordId).toList(),
      );
    } catch (e) {
      state = state.copyWith(
        error: 'فشل حذف سجل الممارسة الزراعية: ${e.toString()}',
      );
    }
  }

  /// مسح الحالة
  /// Clear state
  void clear() {
    state = const FarmPracticesState();
  }
}

/// مزود حالة الممارسات الزراعية
/// Farm practices state provider
final farmPracticesProvider =
    StateNotifierProvider<FarmPracticesNotifier, FarmPracticesState>((ref) {
  // final repository = ref.watch(ecologicalRepositoryProvider);
  return FarmPracticesNotifier(
    // repository,
  );
});

// ============================================================
// Ecological Dashboard State & Provider
// ============================================================

/// حالة لوحة التحكم الإيكولوجية
/// Ecological dashboard state
class EcologicalDashboardState {
  final bool isLoading;

  // النتائج (0-100)
  // Scores (0-100)
  final int overallScore;
  final int biodiversityScore;
  final int soilHealthScore;
  final int waterEfficiencyScore;
  final int practicesScore;

  // السجلات الأخيرة
  // Recent records
  final List<dynamic> recentRecords;

  final String? error;

  const EcologicalDashboardState({
    this.isLoading = false,
    this.overallScore = 0,
    this.biodiversityScore = 0,
    this.soilHealthScore = 0,
    this.waterEfficiencyScore = 0,
    this.practicesScore = 0,
    this.recentRecords = const [],
    this.error,
  });

  EcologicalDashboardState copyWith({
    bool? isLoading,
    int? overallScore,
    int? biodiversityScore,
    int? soilHealthScore,
    int? waterEfficiencyScore,
    int? practicesScore,
    List<dynamic>? recentRecords,
    String? error,
  }) {
    return EcologicalDashboardState(
      isLoading: isLoading ?? this.isLoading,
      overallScore: overallScore ?? this.overallScore,
      biodiversityScore: biodiversityScore ?? this.biodiversityScore,
      soilHealthScore: soilHealthScore ?? this.soilHealthScore,
      waterEfficiencyScore: waterEfficiencyScore ?? this.waterEfficiencyScore,
      practicesScore: practicesScore ?? this.practicesScore,
      recentRecords: recentRecords ?? this.recentRecords,
      error: error,
    );
  }
}

/// مدير حالة لوحة التحكم الإيكولوجية
/// Ecological dashboard state notifier
class EcologicalDashboardNotifier
    extends StateNotifier<EcologicalDashboardState> {
  final Ref _ref;

  EcologicalDashboardNotifier(this._ref)
      : super(const EcologicalDashboardState());

  /// تحميل بيانات لوحة التحكم
  /// Load dashboard data
  Future<void> loadDashboard({String? farmId}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // الحصول على البيانات من المزودات الأخرى
      // Get data from other providers
      final biodiversityState = _ref.read(biodiversityProvider);
      final soilHealthState = _ref.read(soilHealthProvider);
      final waterState = _ref.read(waterConservationProvider);
      final practicesState = _ref.read(farmPracticesProvider);

      // حساب النتائج
      // Calculate scores
      final biodivScore = _calculateBiodiversityScore(biodiversityState.records);
      final soilScore = _calculateSoilHealthScore(soilHealthState.records);
      final waterScore = _calculateWaterEfficiencyScore(waterState.records);
      final practicesScore = _calculatePracticesScore(practicesState.records);

      // حساب النتيجة الإجمالية
      // Calculate overall score
      final overall = ((biodivScore + soilScore + waterScore + practicesScore) / 4).round();

      // جمع السجلات الأخيرة
      // Collect recent records
      final recentRecords = <dynamic>[
        ...biodiversityState.records.take(2),
        ...soilHealthState.records.take(2),
        ...waterState.records.take(2),
        ...practicesState.records.take(2),
      ];

      state = state.copyWith(
        isLoading: false,
        overallScore: overall,
        biodiversityScore: biodivScore,
        soilHealthScore: soilScore,
        waterEfficiencyScore: waterScore,
        practicesScore: practicesScore,
        recentRecords: recentRecords,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل لوحة التحكم: ${e.toString()}',
      );
    }
  }

  /// حساب درجة التنوع البيولوجي
  /// Calculate biodiversity score
  int _calculateBiodiversityScore(List<BiodiversityRecord> records) {
    if (records.isEmpty) return 0;

    final scores = records.map((r) => r.calculatedScore).toList();
    final avg = scores.reduce((a, b) => a + b) / scores.length;

    return avg.round();
  }

  /// حساب درجة صحة التربة
  /// Calculate soil health score
  int _calculateSoilHealthScore(List<SoilHealthRecord> records) {
    if (records.isEmpty) return 0;

    final scores = records.map((r) => r.calculatedHealthScore).toList();
    final avg = scores.reduce((a, b) => a + b) / scores.length;

    return avg.round();
  }

  /// حساب درجة كفاءة المياه
  /// Calculate water efficiency score
  int _calculateWaterEfficiencyScore(List<WaterConservationRecord> records) {
    if (records.isEmpty) return 0;

    final efficiencyScores = records
        .where((r) => r.efficiencyPercentage != null)
        .map((r) => r.efficiencyPercentage!)
        .toList();

    if (efficiencyScores.isEmpty) return 0;

    final avg = efficiencyScores.reduce((a, b) => a + b) / efficiencyScores.length;

    return avg.round();
  }

  /// حساب درجة الممارسات
  /// Calculate practices score
  int _calculatePracticesScore(List<FarmPracticeRecord> records) {
    if (records.isEmpty) return 0;

    final implementedCount = records
        .where((r) => r.status == PracticeStatus.implemented)
        .length;

    final effectivenessScores = records
        .where((r) => r.effectivenessRating != null)
        .map((r) => r.effectivenessPercentage)
        .toList();

    if (effectivenessScores.isEmpty) return 0;

    final avg = effectivenessScores.reduce((a, b) => a + b) / effectivenessScores.length;

    // مكافأة للممارسات المنفذة
    // Bonus for implemented practices
    final implementationBonus = (implementedCount / records.length * 20).round();

    return (avg + implementationBonus).clamp(0, 100).toInt();
  }

  /// تحديث لوحة التحكم
  /// Refresh dashboard
  Future<void> refresh({String? farmId}) async {
    // تحميل البيانات من جميع المزودات
    // Load data from all providers
    await Future.wait([
      _ref.read(biodiversityProvider.notifier).loadRecords(farmId: farmId),
      _ref.read(soilHealthProvider.notifier).loadRecords(),
      _ref.read(waterConservationProvider.notifier).loadRecords(farmId: farmId),
      _ref.read(farmPracticesProvider.notifier).loadRecords(farmId: farmId),
    ]);

    await loadDashboard(farmId: farmId);
  }

  /// مسح الحالة
  /// Clear state
  void clear() {
    state = const EcologicalDashboardState();
  }
}

/// مزود لوحة التحكم الإيكولوجية
/// Ecological dashboard provider
final ecologicalDashboardProvider = StateNotifierProvider<
    EcologicalDashboardNotifier, EcologicalDashboardState>((ref) {
  return EcologicalDashboardNotifier(ref);
});

// ============================================================
// Form State Providers
// ============================================================

/// حالة نموذج التنوع البيولوجي
/// Biodiversity form state
class BiodiversityFormState {
  final bool isSaving;
  final String? error;
  final BiodiversityRecord? record;

  const BiodiversityFormState({
    this.isSaving = false,
    this.error,
    this.record,
  });

  BiodiversityFormState copyWith({
    bool? isSaving,
    String? error,
    BiodiversityRecord? record,
  }) {
    return BiodiversityFormState(
      isSaving: isSaving ?? this.isSaving,
      error: error,
      record: record ?? this.record,
    );
  }
}

/// مدير حالة نموذج التنوع البيولوجي
/// Biodiversity form notifier
class BiodiversityFormNotifier extends StateNotifier<BiodiversityFormState> {
  BiodiversityFormNotifier() : super(const BiodiversityFormState());

  void setRecord(BiodiversityRecord? record) {
    state = state.copyWith(record: record);
  }

  void clear() {
    state = const BiodiversityFormState();
  }
}

/// مزود نموذج التنوع البيولوجي
/// Biodiversity form provider
final biodiversityFormProvider =
    StateNotifierProvider<BiodiversityFormNotifier, BiodiversityFormState>(
        (ref) {
  return BiodiversityFormNotifier();
});

/// حالة نموذج صحة التربة
/// Soil health form state
class SoilHealthFormState {
  final bool isSaving;
  final String? error;
  final SoilHealthRecord? record;

  const SoilHealthFormState({
    this.isSaving = false,
    this.error,
    this.record,
  });

  SoilHealthFormState copyWith({
    bool? isSaving,
    String? error,
    SoilHealthRecord? record,
  }) {
    return SoilHealthFormState(
      isSaving: isSaving ?? this.isSaving,
      error: error,
      record: record ?? this.record,
    );
  }
}

/// مدير حالة نموذج صحة التربة
/// Soil health form notifier
class SoilHealthFormNotifier extends StateNotifier<SoilHealthFormState> {
  SoilHealthFormNotifier() : super(const SoilHealthFormState());

  void setRecord(SoilHealthRecord? record) {
    state = state.copyWith(record: record);
  }

  void clear() {
    state = const SoilHealthFormState();
  }
}

/// مزود نموذج صحة التربة
/// Soil health form provider
final soilHealthFormProvider =
    StateNotifierProvider<SoilHealthFormNotifier, SoilHealthFormState>((ref) {
  return SoilHealthFormNotifier();
});

/// حالة نموذج سجل المياه
/// Water record form state
class WaterRecordFormState {
  final bool isSaving;
  final String? error;
  final WaterConservationRecord? record;

  const WaterRecordFormState({
    this.isSaving = false,
    this.error,
    this.record,
  });

  WaterRecordFormState copyWith({
    bool? isSaving,
    String? error,
    WaterConservationRecord? record,
  }) {
    return WaterRecordFormState(
      isSaving: isSaving ?? this.isSaving,
      error: error,
      record: record ?? this.record,
    );
  }
}

/// مدير حالة نموذج سجل المياه
/// Water record form notifier
class WaterRecordFormNotifier extends StateNotifier<WaterRecordFormState> {
  WaterRecordFormNotifier() : super(const WaterRecordFormState());

  void setRecord(WaterConservationRecord? record) {
    state = state.copyWith(record: record);
  }

  void clear() {
    state = const WaterRecordFormState();
  }
}

/// مزود نموذج سجل المياه
/// Water record form provider
final waterRecordFormProvider =
    StateNotifierProvider<WaterRecordFormNotifier, WaterRecordFormState>(
        (ref) {
  return WaterRecordFormNotifier();
});

/// حالة نموذج الممارسة
/// Practice form state
class PracticeFormState {
  final bool isSaving;
  final String? error;
  final FarmPracticeRecord? record;

  const PracticeFormState({
    this.isSaving = false,
    this.error,
    this.record,
  });

  PracticeFormState copyWith({
    bool? isSaving,
    String? error,
    FarmPracticeRecord? record,
  }) {
    return PracticeFormState(
      isSaving: isSaving ?? this.isSaving,
      error: error,
      record: record ?? this.record,
    );
  }
}

/// مدير حالة نموذج الممارسة
/// Practice form notifier
class PracticeFormNotifier extends StateNotifier<PracticeFormState> {
  PracticeFormNotifier() : super(const PracticeFormState());

  void setRecord(FarmPracticeRecord? record) {
    state = state.copyWith(record: record);
  }

  void clear() {
    state = const PracticeFormState();
  }
}

/// مزود نموذج الممارسة
/// Practice form provider
final practiceFormProvider =
    StateNotifierProvider<PracticeFormNotifier, PracticeFormState>((ref) {
  return PracticeFormNotifier();
});

// ============================================================
// Derived Providers - مزودات مشتقة
// ============================================================

/// السجلات الأخيرة للتنوع البيولوجي (آخر 5)
/// Recent biodiversity records (last 5)
final recentBiodiversityProvider = Provider<List<BiodiversityRecord>>((ref) {
  final state = ref.watch(biodiversityProvider);
  return state.records.take(5).toList();
});

/// السجلات الأخيرة لصحة التربة (آخر 5)
/// Recent soil health records (last 5)
final recentSoilHealthProvider = Provider<List<SoilHealthRecord>>((ref) {
  final state = ref.watch(soilHealthProvider);
  return state.records.take(5).toList();
});

/// السجلات الأخيرة للحفاظ على المياه (آخر 5)
/// Recent water conservation records (last 5)
final recentWaterConservationProvider =
    Provider<List<WaterConservationRecord>>((ref) {
  final state = ref.watch(waterConservationProvider);
  return state.records.take(5).toList();
});

/// الممارسات الأخيرة (آخر 5)
/// Recent practices (last 5)
final recentPracticesProvider = Provider<List<FarmPracticeRecord>>((ref) {
  final state = ref.watch(farmPracticesProvider);
  return state.records.take(5).toList();
});

/// الممارسات النشطة (قيد التنفيذ)
/// Active practices (in progress)
final activePracticesProvider = Provider<List<FarmPracticeRecord>>((ref) {
  final state = ref.watch(farmPracticesProvider);
  return state.records
      .where((r) =>
          r.status == PracticeStatus.inProgress ||
          r.status == PracticeStatus.planned)
      .toList();
});

/// الممارسات المكتملة
/// Completed practices
final completedPracticesProvider = Provider<List<FarmPracticeRecord>>((ref) {
  final state = ref.watch(farmPracticesProvider);
  return state.records
      .where((r) => r.status == PracticeStatus.implemented)
      .toList();
});

/// الممارسات الداعمة لـ GlobalGAP
/// GlobalGAP supporting practices
final globalGapPracticesProvider = Provider<List<FarmPracticeRecord>>((ref) {
  final state = ref.watch(farmPracticesProvider);
  return state.records.where((r) => r.supportsGlobalGap).toList();
});

/// سجلات المياه عالية الكفاءة (> 70%)
/// High efficiency water records (> 70%)
final efficientWaterRecordsProvider =
    Provider<List<WaterConservationRecord>>((ref) {
  final state = ref.watch(waterConservationProvider);
  return state.records.where((r) => r.isEfficient).toList();
});

/// سجلات التربة بحالة ممتازة أو جيدة
/// Soil records with excellent or good status
final healthySoilRecordsProvider = Provider<List<SoilHealthRecord>>((ref) {
  final state = ref.watch(soilHealthProvider);
  return state.records
      .where((r) =>
          r.calculatedStatus == SoilHealthStatus.excellent ||
          r.calculatedStatus == SoilHealthStatus.good)
      .toList();
});

/// سجلات التنوع البيولوجي حسب النوع
/// Biodiversity records by survey type
final biodiversityByTypeProvider =
    Provider.family<List<BiodiversityRecord>, BiodiversitySurveyType>(
        (ref, type) {
  final state = ref.watch(biodiversityProvider);
  return state.records.where((r) => r.surveyType == type).toList();
});

/// إحصائيات سريعة - عدد السجلات
/// Quick stats - record counts
final recordCountsProvider = Provider<Map<String, int>>((ref) {
  final biodivCount = ref.watch(biodiversityProvider).records.length;
  final soilCount = ref.watch(soilHealthProvider).records.length;
  final waterCount = ref.watch(waterConservationProvider).records.length;
  final practicesCount = ref.watch(farmPracticesProvider).records.length;

  return {
    'biodiversity': biodivCount,
    'soilHealth': soilCount,
    'waterConservation': waterCount,
    'practices': practicesCount,
    'total': biodivCount + soilCount + waterCount + practicesCount,
  };
});

/// إحصائيات الاستدامة - متوسط النتائج
/// Sustainability stats - average scores
final sustainabilityStatsProvider = Provider<Map<String, double>>((ref) {
  final dashboard = ref.watch(ecologicalDashboardProvider);

  return {
    'overall': dashboard.overallScore.toDouble(),
    'biodiversity': dashboard.biodiversityScore.toDouble(),
    'soilHealth': dashboard.soilHealthScore.toDouble(),
    'waterEfficiency': dashboard.waterEfficiencyScore.toDouble(),
    'practices': dashboard.practicesScore.toDouble(),
  };
});
