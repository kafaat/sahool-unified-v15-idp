/// Virtual Sensors Providers - Riverpod State Management
/// موفرو المستشعرات الافتراضية - إدارة الحالة بـ Riverpod
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/virtual_sensor_models.dart';
import '../../data/repositories/virtual_sensors_repository.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Repository Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for VirtualSensorsRepository instance
/// موفر لنسخة مستودع المستشعرات الافتراضية
final virtualSensorsRepositoryProvider = Provider<VirtualSensorsRepository>((ref) {
  final repository = VirtualSensorsRepository();
  ref.onDispose(() => repository.dispose());
  return repository;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Service Availability
// توفر الخدمة
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for checking virtual sensors service availability
/// موفر للتحقق من توفر خدمة المستشعرات الافتراضية
final virtualSensorsAvailableProvider = FutureProvider<bool>((ref) async {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return repository.isServiceAvailable();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Reference Data Providers
// موفرو البيانات المرجعية
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for supported crops with Kc values
/// موفر المحاصيل المدعومة مع قيم Kc
final supportedCropsKcProvider = FutureProvider<List<CropKcOption>>((ref) async {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return repository.getSupportedCrops();
});

/// Provider for supported soil types
/// موفر أنواع التربة المدعومة
final soilTypesProvider = FutureProvider<List<SoilTypeInfo>>((ref) async {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return repository.getSoilTypes();
});

/// Provider for irrigation methods
/// موفر طرق الري
final irrigationMethodsProvider = FutureProvider<List<IrrigationMethodInfo>>((ref) async {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return repository.getIrrigationMethods();
});

// ═══════════════════════════════════════════════════════════════════════════════
// ET0 Calculation Provider
// موفر حساب التبخر-نتح المرجعي
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for ET0 calculation
/// موفر حساب ET0
final et0CalculationProvider =
    FutureProvider.family<ET0Response, WeatherInput>((ref, weather) async {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return repository.calculateET0(weather);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Crop ETc Calculation State
// حالة حساب التبخر-نتح للمحصول
// ═══════════════════════════════════════════════════════════════════════════════

/// Input parameters for ETc calculation
class CropETcParams {
  final WeatherInput weather;
  final String cropType;
  final GrowthStage growthStage;
  final double fieldAreaHectares;
  final int? daysInStage;

  const CropETcParams({
    required this.weather,
    required this.cropType,
    required this.growthStage,
    this.fieldAreaHectares = 1.0,
    this.daysInStage,
  });
}

/// Provider for crop ETc calculation
/// موفر حساب التبخر-نتح للمحصول
final cropETcProvider =
    FutureProvider.family<CropETcResponse, CropETcParams>((ref, params) async {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return repository.calculateCropETc(
    weather: params.weather,
    cropType: params.cropType,
    growthStage: params.growthStage,
    fieldAreaHectares: params.fieldAreaHectares,
    daysInStage: params.daysInStage,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Irrigation Recommendation State
// حالة توصية الري
// ═══════════════════════════════════════════════════════════════════════════════

/// State for irrigation recommendation
/// حالة توصية الري
class IrrigationState {
  final bool isLoading;
  final IrrigationRecommendation? recommendation;
  final QuickIrrigationCheck? quickCheck;
  final String? error;
  final String? errorAr;

  // Input parameters
  final String? selectedCropType;
  final GrowthStage? selectedGrowthStage;
  final SoilType? selectedSoilType;
  final IrrigationMethod? selectedIrrigationMethod;
  final double fieldAreaHectares;
  final DateTime? lastIrrigationDate;
  final double? lastIrrigationAmount;

  const IrrigationState({
    this.isLoading = false,
    this.recommendation,
    this.quickCheck,
    this.error,
    this.errorAr,
    this.selectedCropType,
    this.selectedGrowthStage,
    this.selectedSoilType,
    this.selectedIrrigationMethod,
    this.fieldAreaHectares = 1.0,
    this.lastIrrigationDate,
    this.lastIrrigationAmount,
  });

  IrrigationState copyWith({
    bool? isLoading,
    IrrigationRecommendation? recommendation,
    QuickIrrigationCheck? quickCheck,
    String? error,
    String? errorAr,
    String? selectedCropType,
    GrowthStage? selectedGrowthStage,
    SoilType? selectedSoilType,
    IrrigationMethod? selectedIrrigationMethod,
    double? fieldAreaHectares,
    DateTime? lastIrrigationDate,
    double? lastIrrigationAmount,
  }) {
    return IrrigationState(
      isLoading: isLoading ?? this.isLoading,
      recommendation: recommendation ?? this.recommendation,
      quickCheck: quickCheck ?? this.quickCheck,
      error: error,
      errorAr: errorAr,
      selectedCropType: selectedCropType ?? this.selectedCropType,
      selectedGrowthStage: selectedGrowthStage ?? this.selectedGrowthStage,
      selectedSoilType: selectedSoilType ?? this.selectedSoilType,
      selectedIrrigationMethod: selectedIrrigationMethod ?? this.selectedIrrigationMethod,
      fieldAreaHectares: fieldAreaHectares ?? this.fieldAreaHectares,
      lastIrrigationDate: lastIrrigationDate ?? this.lastIrrigationDate,
      lastIrrigationAmount: lastIrrigationAmount ?? this.lastIrrigationAmount,
    );
  }

  bool get hasRecommendation => recommendation != null;
  bool get hasError => error != null;
  bool get canCalculate =>
      selectedCropType != null &&
      selectedGrowthStage != null &&
      selectedSoilType != null &&
      selectedIrrigationMethod != null &&
      !isLoading;
}

/// Notifier for irrigation state
/// مُعلم حالة الري
class IrrigationNotifier extends StateNotifier<IrrigationState> {
  final VirtualSensorsRepository _repository;

  IrrigationNotifier(this._repository) : super(const IrrigationState());

  /// Select crop type
  /// اختيار نوع المحصول
  void selectCropType(String? cropType) {
    state = state.copyWith(selectedCropType: cropType);
  }

  /// Select growth stage
  /// اختيار مرحلة النمو
  void selectGrowthStage(GrowthStage? stage) {
    state = state.copyWith(selectedGrowthStage: stage);
  }

  /// Select soil type
  /// اختيار نوع التربة
  void selectSoilType(SoilType? soilType) {
    state = state.copyWith(selectedSoilType: soilType);
  }

  /// Select irrigation method
  /// اختيار طريقة الري
  void selectIrrigationMethod(IrrigationMethod? method) {
    state = state.copyWith(selectedIrrigationMethod: method);
  }

  /// Set field area
  /// تحديد مساحة الحقل
  void setFieldArea(double hectares) {
    state = state.copyWith(fieldAreaHectares: hectares);
  }

  /// Set last irrigation info
  /// تحديد معلومات آخر ري
  void setLastIrrigation(DateTime? date, double? amount) {
    state = state.copyWith(
      lastIrrigationDate: date,
      lastIrrigationAmount: amount,
    );
  }

  /// Get full irrigation recommendation
  /// الحصول على توصية الري الكاملة
  Future<IrrigationRecommendation?> getRecommendation(WeatherInput weather) async {
    if (state.selectedCropType == null ||
        state.selectedGrowthStage == null ||
        state.selectedSoilType == null ||
        state.selectedIrrigationMethod == null) {
      state = state.copyWith(
        error: 'Please fill all required fields',
        errorAr: 'يرجى ملء جميع الحقول المطلوبة',
      );
      return null;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final recommendation = await _repository.getIrrigationRecommendation(
        cropType: state.selectedCropType!,
        growthStage: state.selectedGrowthStage!,
        soilType: state.selectedSoilType!,
        irrigationMethod: state.selectedIrrigationMethod!,
        weather: weather,
        fieldAreaHectares: state.fieldAreaHectares,
        lastIrrigationDate: state.lastIrrigationDate,
        lastIrrigationAmount: state.lastIrrigationAmount,
      );

      state = state.copyWith(
        isLoading: false,
        recommendation: recommendation,
      );

      return recommendation;
    } catch (e) {
      final error = e is VirtualSensorsException ? e : VirtualSensorsException('$e');
      state = state.copyWith(
        isLoading: false,
        error: error.message,
        errorAr: error.messageAr,
      );
      return null;
    }
  }

  /// Quick irrigation check
  /// فحص سريع للري
  Future<QuickIrrigationCheck?> performQuickCheck({
    required int daysSinceIrrigation,
    required double temperature,
    double humidity = 50,
  }) async {
    if (state.selectedCropType == null || state.selectedGrowthStage == null) {
      state = state.copyWith(
        error: 'Please select crop type and growth stage',
        errorAr: 'يرجى اختيار نوع المحصول ومرحلة النمو',
      );
      return null;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final quickCheck = await _repository.quickIrrigationCheck(
        cropType: state.selectedCropType!,
        growthStage: state.selectedGrowthStage!,
        soilType: state.selectedSoilType ?? SoilType.loam,
        daysSinceIrrigation: daysSinceIrrigation,
        temperature: temperature,
        humidity: humidity,
      );

      state = state.copyWith(
        isLoading: false,
        quickCheck: quickCheck,
      );

      return quickCheck;
    } catch (e) {
      final error = e is VirtualSensorsException ? e : VirtualSensorsException('$e');
      state = state.copyWith(
        isLoading: false,
        error: error.message,
        errorAr: error.messageAr,
      );
      return null;
    }
  }

  /// Clear state
  /// مسح الحالة
  void clearState() {
    state = const IrrigationState();
  }

  /// Clear recommendation
  /// مسح التوصية
  void clearRecommendation() {
    state = state.copyWith(recommendation: null, quickCheck: null);
  }
}

/// Provider for irrigation state
/// موفر حالة الري
final irrigationProvider =
    StateNotifierProvider<IrrigationNotifier, IrrigationState>((ref) {
  final repository = ref.watch(virtualSensorsRepositoryProvider);
  return IrrigationNotifier(repository);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Water Balance State (for advanced tracking)
// حالة ميزان الماء (للتتبع المتقدم)
// ═══════════════════════════════════════════════════════════════════════════════

/// State for water balance tracking
/// حالة تتبع ميزان الماء
class WaterBalanceState {
  final String? fieldId;
  final double totalIrrigation;
  final double totalRainfall;
  final double totalEt;
  final double cumulativeBalance;
  final List<Map<String, dynamic>> dailyRecords;

  const WaterBalanceState({
    this.fieldId,
    this.totalIrrigation = 0,
    this.totalRainfall = 0,
    this.totalEt = 0,
    this.cumulativeBalance = 0,
    this.dailyRecords = const [],
  });

  WaterBalanceState copyWith({
    String? fieldId,
    double? totalIrrigation,
    double? totalRainfall,
    double? totalEt,
    double? cumulativeBalance,
    List<Map<String, dynamic>>? dailyRecords,
  }) {
    return WaterBalanceState(
      fieldId: fieldId ?? this.fieldId,
      totalIrrigation: totalIrrigation ?? this.totalIrrigation,
      totalRainfall: totalRainfall ?? this.totalRainfall,
      totalEt: totalEt ?? this.totalEt,
      cumulativeBalance: cumulativeBalance ?? this.cumulativeBalance,
      dailyRecords: dailyRecords ?? this.dailyRecords,
    );
  }
}

/// Notifier for water balance tracking
/// مُعلم تتبع ميزان الماء
class WaterBalanceNotifier extends StateNotifier<WaterBalanceState> {
  WaterBalanceNotifier() : super(const WaterBalanceState());

  /// Set field ID
  void setFieldId(String fieldId) {
    state = state.copyWith(fieldId: fieldId);
  }

  /// Add irrigation record
  /// إضافة سجل ري
  void addIrrigationRecord(DateTime date, double amountMm) {
    final newRecords = [
      ...state.dailyRecords,
      {
        'date': date.toIso8601String(),
        'type': 'irrigation',
        'amount_mm': amountMm,
      },
    ];

    state = state.copyWith(
      totalIrrigation: state.totalIrrigation + amountMm,
      cumulativeBalance: state.cumulativeBalance + amountMm,
      dailyRecords: newRecords,
    );
  }

  /// Add rainfall record
  /// إضافة سجل مطر
  void addRainfallRecord(DateTime date, double amountMm) {
    // Effective rainfall (80% of total)
    final effectiveRainfall = amountMm * 0.8;

    final newRecords = [
      ...state.dailyRecords,
      {
        'date': date.toIso8601String(),
        'type': 'rainfall',
        'amount_mm': amountMm,
        'effective_mm': effectiveRainfall,
      },
    ];

    state = state.copyWith(
      totalRainfall: state.totalRainfall + amountMm,
      cumulativeBalance: state.cumulativeBalance + effectiveRainfall,
      dailyRecords: newRecords,
    );
  }

  /// Add ET record
  /// إضافة سجل تبخر-نتح
  void addEtRecord(DateTime date, double etMm) {
    final newRecords = [
      ...state.dailyRecords,
      {
        'date': date.toIso8601String(),
        'type': 'et',
        'amount_mm': etMm,
      },
    ];

    state = state.copyWith(
      totalEt: state.totalEt + etMm,
      cumulativeBalance: state.cumulativeBalance - etMm,
      dailyRecords: newRecords,
    );
  }

  /// Reset balance
  /// إعادة تعيين الميزان
  void resetBalance() {
    state = const WaterBalanceState();
  }
}

/// Provider for water balance tracking
/// موفر تتبع ميزان الماء
final waterBalanceProvider =
    StateNotifierProvider<WaterBalanceNotifier, WaterBalanceState>((ref) {
  return WaterBalanceNotifier();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Derived/Computed Providers
// الموفرات المحسوبة
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for irrigation urgency color
/// موفر لون استعجال الري
final irrigationUrgencyColorProvider = Provider<String>((ref) {
  final state = ref.watch(irrigationProvider);
  final recommendation = state.recommendation;

  if (recommendation == null) return '#808080'; // Gray

  switch (recommendation.urgency) {
    case UrgencyLevel.none:
      return '#4CAF50'; // Green
    case UrgencyLevel.low:
      return '#8BC34A'; // Light Green
    case UrgencyLevel.medium:
      return '#FFC107'; // Amber
    case UrgencyLevel.high:
      return '#FF9800'; // Orange
    case UrgencyLevel.critical:
      return '#F44336'; // Red
  }
});

/// Provider for water deficit status
/// موفر حالة عجز الماء
final waterDeficitStatusProvider = Provider<Map<String, dynamic>>((ref) {
  final state = ref.watch(irrigationProvider);
  final recommendation = state.recommendation;

  if (recommendation == null) {
    return {
      'status': 'unknown',
      'status_ar': 'غير معروف',
      'depletion': 0.0,
    };
  }

  final depletion = recommendation.moistureDepletionPercent;

  if (depletion < 30) {
    return {
      'status': 'optimal',
      'status_ar': 'مثالي',
      'depletion': depletion,
    };
  } else if (depletion < 50) {
    return {
      'status': 'adequate',
      'status_ar': 'كافي',
      'depletion': depletion,
    };
  } else if (depletion < 70) {
    return {
      'status': 'moderate_stress',
      'status_ar': 'إجهاد متوسط',
      'depletion': depletion,
    };
  } else if (depletion < 85) {
    return {
      'status': 'high_stress',
      'status_ar': 'إجهاد عالي',
      'depletion': depletion,
    };
  } else {
    return {
      'status': 'critical',
      'status_ar': 'حرج',
      'depletion': depletion,
    };
  }
});
