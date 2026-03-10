/// Crops Feature Providers - Riverpod State Management
/// موفرو ميزة المحاصيل - إدارة الحالة بـ Riverpod
///
/// Manages active crops, growth stages, health indicators,
/// and crop recommendations for the farmer dashboard.
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../../../core/http/api_client.dart';
import '../../../../core/utils/app_logger.dart';
import '../../data/models/crop_model.dart';
import '../../data/remote/crops_api.dart';
import '../../data/repositories/crops_repository.dart';

// =============================================================================
// Active Crop Instance (field-specific)
// نسخة المحصول النشط (خاصة بالحقل)
// =============================================================================

/// Represents an active crop planted in a specific field
/// يمثل محصول نشط مزروع في حقل محدد
class ActiveCrop {
  final String id;
  final String fieldId;
  final String fieldName;
  final Crop crop;
  final String variety;
  final String growthStage;
  final String growthStageAr;
  final double ndviValue;
  final DateTime plantingDate;
  final DateTime? expectedHarvestDate;
  final double areaHectares;
  final String healthStatus;
  final String healthStatusAr;

  const ActiveCrop({
    required this.id,
    required this.fieldId,
    required this.fieldName,
    required this.crop,
    this.variety = '',
    required this.growthStage,
    required this.growthStageAr,
    this.ndviValue = 0.0,
    required this.plantingDate,
    this.expectedHarvestDate,
    required this.areaHectares,
    this.healthStatus = 'good',
    this.healthStatusAr = 'جيد',
  });

  /// Days since planting
  int get daysSincePlanting => DateTime.now().difference(plantingDate).inDays;

  /// Days to harvest (estimated)
  int? get daysToHarvest {
    if (expectedHarvestDate == null) return null;
    final days = expectedHarvestDate!.difference(DateTime.now()).inDays;
    return days > 0 ? days : 0;
  }
}

// =============================================================================
// State
// الحالة
// =============================================================================

/// Crops management state
/// حالة إدارة المحاصيل
class CropsState {
  final List<ActiveCrop> activeCrops;
  final bool isLoading;
  final String? error;
  final String? selectedCropId;

  const CropsState({
    this.activeCrops = const [],
    this.isLoading = false,
    this.error,
    this.selectedCropId,
  });

  CropsState copyWith({
    List<ActiveCrop>? activeCrops,
    bool? isLoading,
    String? error,
    String? selectedCropId,
  }) {
    return CropsState(
      activeCrops: activeCrops ?? this.activeCrops,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      selectedCropId: selectedCropId ?? this.selectedCropId,
    );
  }

  ActiveCrop? get selectedCrop {
    if (selectedCropId == null) return null;
    try {
      return activeCrops.firstWhere((c) => c.id == selectedCropId);
    } catch (_) {
      return null;
    }
  }
}

// =============================================================================
// StateNotifier
// مُعلم الحالة
// =============================================================================

/// Crops state notifier - manages crop lifecycle
/// مُعلم حالة المحاصيل - يدير دورة حياة المحاصيل
class CropsNotifier extends StateNotifier<CropsState> {
  final ApiClient? _apiClient;

  CropsNotifier({ApiClient? apiClient})
      : _apiClient = apiClient,
        super(const CropsState()) {
    loadCrops();
  }

  /// Load active crops from API with fallback to mock data
  /// تحميل المحاصيل النشطة من الخادم مع بيانات احتياطية
  Future<void> loadCrops() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      // Try fetching active crops from the API
      if (_apiClient != null) {
        try {
          final response = await _apiClient.get('/api/v1/crops/active');
          final List<dynamic> data =
              response is List ? response : (response['data'] as List? ?? []);

          if (data.isNotEmpty) {
            final crops = data
                .map((json) => _activeCropFromJson(json as Map<String, dynamic>))
                .toList();
            AppLogger.i('Loaded active crops from API',
                tag: 'CropsNotifier', data: {'count': crops.length});
            state = state.copyWith(activeCrops: crops, isLoading: false);
            return;
          }
        } catch (e) {
          AppLogger.w(
            'Failed to fetch active crops from API, falling back to mock data',
            tag: 'CropsNotifier',
            error: e,
          );
        }
      }

      // Fallback to mock data when API is unavailable or returns empty
      await Future.delayed(const Duration(milliseconds: 400));
      final crops = _getMockActiveCrops();
      state = state.copyWith(activeCrops: crops, isLoading: false);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  /// Parse an ActiveCrop from API JSON response
  /// تحويل بيانات JSON إلى محصول نشط
  ActiveCrop _activeCropFromJson(Map<String, dynamic> json) {
    return ActiveCrop(
      id: json['id'] as String? ?? '',
      fieldId: json['field_id'] as String? ?? '',
      fieldName: json['field_name'] as String? ?? '',
      crop: Crop.fromJson(json['crop'] as Map<String, dynamic>? ?? {}),
      variety: json['variety'] as String? ?? '',
      growthStage: json['growth_stage'] as String? ?? '',
      growthStageAr: json['growth_stage_ar'] as String? ?? '',
      ndviValue: (json['ndvi_value'] as num?)?.toDouble() ?? 0.0,
      plantingDate: DateTime.tryParse(json['planting_date'] as String? ?? '') ??
          DateTime.now(),
      expectedHarvestDate:
          DateTime.tryParse(json['expected_harvest_date'] as String? ?? ''),
      areaHectares: (json['area_hectares'] as num?)?.toDouble() ?? 0.0,
      healthStatus: json['health_status'] as String? ?? 'good',
      healthStatusAr: json['health_status_ar'] as String? ?? 'جيد',
    );
  }

  /// Add a new crop to a field
  /// إضافة محصول جديد لحقل
  Future<void> addCrop({
    required String fieldId,
    required String fieldName,
    required Crop crop,
    String variety = '',
    required double areaHectares,
  }) async {
    final activeCrop = ActiveCrop(
      id: 'crop_${DateTime.now().millisecondsSinceEpoch}',
      fieldId: fieldId,
      fieldName: fieldName,
      crop: crop,
      variety: variety,
      growthStage: 'Germination',
      growthStageAr: 'إنبات',
      plantingDate: DateTime.now(),
      expectedHarvestDate:
          DateTime.now().add(Duration(days: crop.growingSeasonDays)),
      areaHectares: areaHectares,
      healthStatus: 'good',
      healthStatusAr: 'جيد',
    );

    state = state.copyWith(
      activeCrops: [activeCrop, ...state.activeCrops],
    );
  }

  /// Update growth stage for a crop
  /// تحديث مرحلة النمو لمحصول
  void updateGrowthStage(
      String cropId, String stage, String stageAr) {
    final updated = state.activeCrops.map((c) {
      if (c.id == cropId) {
        return ActiveCrop(
          id: c.id,
          fieldId: c.fieldId,
          fieldName: c.fieldName,
          crop: c.crop,
          variety: c.variety,
          growthStage: stage,
          growthStageAr: stageAr,
          ndviValue: c.ndviValue,
          plantingDate: c.plantingDate,
          expectedHarvestDate: c.expectedHarvestDate,
          areaHectares: c.areaHectares,
          healthStatus: c.healthStatus,
          healthStatusAr: c.healthStatusAr,
        );
      }
      return c;
    }).toList();

    state = state.copyWith(activeCrops: updated);
  }

  /// Select a crop for detail view
  /// تحديد محصول لعرض التفاصيل
  void selectCrop(String? cropId) {
    state = state.copyWith(selectedCropId: cropId);
  }

  /// Get recommendations for a specific crop from advisory service
  /// الحصول على التوصيات لمحصول محدد من خدمة الاستشارات
  Future<List<String>> getRecommendations(String cropId) async {
    // Try fetching recommendations from the advisory API
    if (_apiClient != null) {
      try {
        final response = await _apiClient.get(
          '/api/v1/advisory/recommendations',
          queryParameters: {'crop_id': cropId},
        );
        final List<dynamic> data =
            response is List ? response : (response['data'] as List? ?? []);

        if (data.isNotEmpty) {
          final recommendations = data.map((item) {
            if (item is String) return item;
            if (item is Map) {
              final en = item['text'] ?? item['message'] ?? '';
              final ar = item['text_ar'] ?? item['message_ar'] ?? '';
              return ar.toString().isNotEmpty ? '$en | $ar' : en.toString();
            }
            return item.toString();
          }).toList();

          AppLogger.i('Loaded recommendations from advisory API',
              tag: 'CropsNotifier',
              data: {'crop_id': cropId, 'count': recommendations.length});
          return recommendations;
        }
      } catch (e) {
        AppLogger.w(
          'Failed to fetch recommendations from advisory API, using defaults',
          tag: 'CropsNotifier',
          error: e,
        );
      }
    }

    // Fallback to default recommendations when API is unavailable
    return _getMockRecommendations(cropId);
  }

  /// Default recommendations when advisory service is unavailable
  /// التوصيات الافتراضية عند عدم توفر خدمة الاستشارات
  List<String> _getMockRecommendations(String cropId) {
    return [
      'Irrigation recommended tomorrow morning | ينصح بالري غدا صباحا',
      'Apply nitrogen fertilizer this week | تطبيق سماد نيتروجيني هذا الاسبوع',
      'Monitor for aphids | مراقبة حشرات المن',
    ];
  }

  List<ActiveCrop> _getMockActiveCrops() {
    return [
      ActiveCrop(
        id: 'crop_1',
        fieldId: 'field_1',
        fieldName: 'Field 1 | الحقل 1',
        crop: const Crop(
          code: 'WHEAT',
          nameEn: 'Wheat',
          nameAr: 'قمح',
          scientificName: 'Triticum aestivum',
          category: CropCategory.cereals,
          growthHabit: GrowthHabit.annual,
          growingSeasonDays: 150,
          optimalTempMin: 10,
          optimalTempMax: 25,
          waterRequirement: WaterRequirement.medium,
          baseYieldTonHa: 3.5,
        ),
        variety: 'Sakha 95',
        growthStage: 'Tillering',
        growthStageAr: 'التفريع',
        ndviValue: 0.72,
        plantingDate: DateTime.now().subtract(const Duration(days: 45)),
        expectedHarvestDate: DateTime.now().add(const Duration(days: 105)),
        areaHectares: 5.2,
        healthStatus: 'healthy',
        healthStatusAr: 'صحي',
      ),
      ActiveCrop(
        id: 'crop_2',
        fieldId: 'field_2',
        fieldName: 'Field 2 | الحقل 2',
        crop: const Crop(
          code: 'TOMATO',
          nameEn: 'Tomato',
          nameAr: 'طماطم',
          scientificName: 'Solanum lycopersicum',
          category: CropCategory.vegetables,
          growthHabit: GrowthHabit.annual,
          growingSeasonDays: 120,
          optimalTempMin: 18,
          optimalTempMax: 30,
          waterRequirement: WaterRequirement.high,
          baseYieldTonHa: 40.0,
        ),
        variety: 'Hybrid 1077',
        growthStage: 'Flowering',
        growthStageAr: 'الإزهار',
        ndviValue: 0.45,
        plantingDate: DateTime.now().subtract(const Duration(days: 60)),
        expectedHarvestDate: DateTime.now().add(const Duration(days: 60)),
        areaHectares: 2.0,
        healthStatus: 'stressed',
        healthStatusAr: 'مجهد',
      ),
      ActiveCrop(
        id: 'crop_3',
        fieldId: 'field_3',
        fieldName: 'Field 3 | الحقل 3',
        crop: const Crop(
          code: 'BARLEY',
          nameEn: 'Barley',
          nameAr: 'شعير',
          scientificName: 'Hordeum vulgare',
          category: CropCategory.cereals,
          growthHabit: GrowthHabit.annual,
          growingSeasonDays: 130,
          optimalTempMin: 8,
          optimalTempMax: 22,
          waterRequirement: WaterRequirement.low,
          baseYieldTonHa: 2.8,
        ),
        variety: 'Arivat',
        growthStage: 'Heading',
        growthStageAr: 'طرد السنابل',
        ndviValue: 0.65,
        plantingDate: DateTime.now().subtract(const Duration(days: 80)),
        expectedHarvestDate: DateTime.now().add(const Duration(days: 50)),
        areaHectares: 3.8,
        healthStatus: 'good',
        healthStatusAr: 'جيد',
      ),
    ];
  }
}

// =============================================================================
// Providers
// الموفرون
// =============================================================================

/// API client provider for crops feature
/// موفر عميل الخادم لميزة المحاصيل
final cropsApiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient();
});

/// Main crops state provider
/// الموفر الرئيسي لحالة المحاصيل
final cropsProvider =
    StateNotifierProvider<CropsNotifier, CropsState>((ref) {
  final apiClient = ref.watch(cropsApiClientProvider);
  return CropsNotifier(apiClient: apiClient);
});
