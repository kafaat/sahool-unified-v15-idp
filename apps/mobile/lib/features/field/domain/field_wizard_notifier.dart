import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/di/providers.dart';
import '../../../core/http/api_client.dart';
import 'field_wizard_state.dart';

/// منطق معالج إنشاء الحقل
class FieldWizardNotifier extends StateNotifier<FieldWizardState> {
  final ApiClient? _apiClient;

  FieldWizardNotifier(this._apiClient) : super(const FieldWizardState());

  void updateFarmId(String farmId) {
    state = state.copyWith(farmId: farmId, clearError: true);
  }

  void updatePolygon(List<LatLng> points, double area) {
    state = state.copyWith(polygonPoints: points, area: area, clearError: true);
  }

  void updateName(String name) {
    state = state.copyWith(name: name, clearError: true);
  }

  void updateSeason({String? name, DateTime? planting, DateTime? harvest}) {
    state = state.copyWith(
      seasonName: name,
      plantingDate: planting,
      harvestDate: harvest,
      clearError: true,
    );
  }

  void updateSeasonName(String? name) {
    if (name == null || name.isEmpty) {
      state = state.copyWith(clearSeasonName: true);
    } else {
      state = state.copyWith(seasonName: name, clearError: true);
    }
  }

  void updatePlantingDate(DateTime? date) {
    if (date == null) {
      state = state.copyWith(clearPlantingDate: true);
    } else {
      state = state.copyWith(plantingDate: date, clearError: true);
    }
  }

  void updateHarvestDate(DateTime? date) {
    if (date == null) {
      state = state.copyWith(clearHarvestDate: true);
    } else {
      state = state.copyWith(harvestDate: date, clearError: true);
    }
  }

  void updateCrop(String crop, {String? previous}) {
    if (previous == null || previous == 'لا يوجد') {
      state = state.copyWith(cropType: crop, clearPreviousCrop: true, clearError: true);
    } else {
      state = state.copyWith(cropType: crop, previousCrop: previous, clearError: true);
    }
  }

  void updatePreviousCrop(String? crop) {
    if (crop == null || crop == 'لا يوجد') {
      state = state.copyWith(clearPreviousCrop: true);
    } else {
      state = state.copyWith(previousCrop: crop);
    }
  }

  void updateSoil(String type) {
    state = state.copyWith(soilType: type, clearError: true);
  }

  void updateIrrigation(String type) {
    state = state.copyWith(irrigationType: type, clearError: true);
  }

  void goToStep(int step) {
    state = state.copyWith(currentStep: step, clearError: true);
  }

  /// التحقق من صحة بيانات الخطوة الحالية
  String? validateStep(int step) {
    switch (step) {
      case 0: // الموقع
        if (state.farmId == null || state.farmId!.isEmpty) {
          return 'يرجى اختيار المزرعة';
        }
        if (state.polygonPoints.length < 3) {
          return 'يرجى رسم حدود الحقل (3 نقاط على الأقل)';
        }
        return null;
      case 1: // المعلومات
        if (state.name.trim().isEmpty) {
          return 'يرجى إدخال اسم الحقل';
        }
        if (state.name.trim().length < 2) {
          return 'يجب أن يكون الاسم حرفين على الأقل';
        }
        if (state.name.trim().length > 255) {
          return 'يجب أن يكون الاسم أقل من 255 حرفاً';
        }
        return null;
      case 2: // الموسم — اختياري
      case 3: // المحصول — اختياري
      case 4: // التربة — اختياري
      case 5: // الري — اختياري
        return null;
      default:
        return null;
    }
  }

  bool nextStep() {
    final error = validateStep(state.currentStep);
    if (error != null) {
      state = state.copyWith(error: error);
      return false;
    }
    if (state.currentStep < 5) {
      state = state.copyWith(currentStep: state.currentStep + 1, clearError: true);
    }
    return true;
  }

  void prevStep() {
    if (state.currentStep > 0) {
      state = state.copyWith(currentStep: state.currentStep - 1, clearError: true);
    }
  }

  /// إرسال بيانات الحقل إلى الخادم
  Future<bool> submit(BuildContext context) async {
    if (_apiClient == null) {
      state = state.copyWith(error: 'خطأ في الاتصال بالخادم');
      return false;
    }

    state = state.copyWith(isSubmitting: true, clearError: true);

    try {
      // بناء بيانات GeoJSON للإرسال
      final coordinates = state.polygonPoints
          .map((p) => [p.longitude, p.latitude])
          .toList();
      // إغلاق المضلع
      if (coordinates.isNotEmpty) {
        coordinates.add(coordinates.first);
      }

      final body = {
        'type': 'Feature',
        'geometry': {
          'type': 'Polygon',
          'coordinates': [coordinates],
        },
        'properties': {
          'name': state.name.trim(),
          if (state.farmId != null) 'farm_id': state.farmId,
          'area_hectares': state.area,
          if (state.cropType.isNotEmpty) 'crop_type': state.cropType,
          if (state.previousCrop != null) 'previous_crop': state.previousCrop,
          if (state.soilType.isNotEmpty) 'soil_type': state.soilType,
          if (state.irrigationType.isNotEmpty) 'irrigation_type': state.irrigationType,
          if (state.seasonName != null) 'season_name': state.seasonName,
          if (state.plantingDate != null)
            'planting_date': state.plantingDate!.toIso8601String(),
          if (state.harvestDate != null)
            'expected_harvest': state.harvestDate!.toIso8601String(),
        },
      };

      await _apiClient!.post('/api/v1/fields', body);
      state = state.copyWith(isSubmitting: false);
      return true;
    } catch (e) {
      state = state.copyWith(
        isSubmitting: false,
        error: 'فشل إنشاء الحقل: $e',
      );
      return false;
    }
  }
}

/// مزوّد حالة معالج الحقل — autoDispose يعيد التهيئة في كل فتح
final fieldWizardProvider =
    StateNotifierProvider.autoDispose<FieldWizardNotifier, FieldWizardState>(
  (ref) {
    final apiClient = ref.read(apiClientProvider);
    return FieldWizardNotifier(apiClient);
  },
);
