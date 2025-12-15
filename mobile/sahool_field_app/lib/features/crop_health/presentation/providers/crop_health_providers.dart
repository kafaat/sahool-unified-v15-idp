/// Crop Health Providers - Riverpod State Management
/// موفرو صحة المحاصيل - إدارة الحالة بـ Riverpod
library;

import 'dart:io';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../data/models/diagnosis_models.dart';
import '../../data/repositories/crop_health_repository.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Repository Provider
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for CropHealthRepository instance
/// موفر لنسخة مستودع صحة المحاصيل
final cropHealthRepositoryProvider = Provider<CropHealthRepository>((ref) {
  final repository = CropHealthRepository();
  ref.onDispose(() => repository.dispose());
  return repository;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Service Availability
// توفر الخدمة
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for checking AI service availability
/// موفر للتحقق من توفر خدمة الذكاء الاصطناعي
final aiServiceAvailableProvider = FutureProvider<bool>((ref) async {
  final repository = ref.watch(cropHealthRepositoryProvider);
  return repository.isServiceAvailable();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Crop & Disease Data
// بيانات المحاصيل والأمراض
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for supported crops
/// موفر المحاصيل المدعومة
final supportedCropsProvider = FutureProvider<List<CropOption>>((ref) async {
  final repository = ref.watch(cropHealthRepositoryProvider);
  return repository.getSupportedCrops();
});

/// Provider for diseases list
/// موفر قائمة الأمراض
final diseasesProvider =
    FutureProvider.family<List<DiseaseInfo>, String?>((ref, cropType) async {
  final repository = ref.watch(cropHealthRepositoryProvider);
  return repository.getDiseases(cropType: cropType);
});

/// Provider for treatment details
/// موفر تفاصيل العلاج
final treatmentDetailsProvider =
    FutureProvider.family<Map<String, dynamic>, String>((ref, diseaseId) async {
  final repository = ref.watch(cropHealthRepositoryProvider);
  return repository.getTreatmentDetails(diseaseId);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Diagnosis State
// حالة التشخيص
// ═══════════════════════════════════════════════════════════════════════════════

/// State for diagnosis process
/// حالة عملية التشخيص
class DiagnosisState {
  final bool isLoading;
  final DiagnosisResult? result;
  final String? error;
  final String? errorAr;
  final File? selectedImage;
  final String? selectedCropType;
  final String? fieldId;
  final List<DiagnosisHistoryItem> history;

  const DiagnosisState({
    this.isLoading = false,
    this.result,
    this.error,
    this.errorAr,
    this.selectedImage,
    this.selectedCropType,
    this.fieldId,
    this.history = const [],
  });

  DiagnosisState copyWith({
    bool? isLoading,
    DiagnosisResult? result,
    String? error,
    String? errorAr,
    File? selectedImage,
    String? selectedCropType,
    String? fieldId,
    List<DiagnosisHistoryItem>? history,
  }) {
    return DiagnosisState(
      isLoading: isLoading ?? this.isLoading,
      result: result ?? this.result,
      error: error,
      errorAr: errorAr,
      selectedImage: selectedImage ?? this.selectedImage,
      selectedCropType: selectedCropType ?? this.selectedCropType,
      fieldId: fieldId ?? this.fieldId,
      history: history ?? this.history,
    );
  }

  bool get hasResult => result != null;
  bool get hasError => error != null;
  bool get canDiagnose => selectedImage != null && !isLoading;
}

/// Notifier for diagnosis state
/// مُعلم حالة التشخيص
class DiagnosisNotifier extends StateNotifier<DiagnosisState> {
  final CropHealthRepository _repository;

  DiagnosisNotifier(this._repository) : super(const DiagnosisState());

  /// Select image for diagnosis
  /// اختيار صورة للتشخيص
  void selectImage(File image) {
    state = state.copyWith(selectedImage: image, result: null, error: null);
  }

  /// Select crop type
  /// اختيار نوع المحصول
  void selectCropType(String? cropType) {
    state = state.copyWith(selectedCropType: cropType);
  }

  /// Set field ID
  /// تعيين معرف الحقل
  void setFieldId(String? fieldId) {
    state = state.copyWith(fieldId: fieldId);
  }

  /// Run diagnosis on selected image
  /// تشغيل التشخيص على الصورة المحددة
  Future<DiagnosisResult?> diagnose({String? symptoms}) async {
    if (state.selectedImage == null) {
      state = state.copyWith(
        error: 'Please select an image first',
        errorAr: 'يرجى اختيار صورة أولاً',
      );
      return null;
    }

    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _repository.diagnoseFromImage(
        state.selectedImage!,
        fieldId: state.fieldId,
        cropType: state.selectedCropType,
        symptoms: symptoms,
      );

      // Add to history
      final historyItem = DiagnosisHistoryItem(
        diagnosisId: result.diagnosisId,
        diseaseName: result.diseaseName,
        diseaseNameAr: result.diseaseNameAr,
        confidence: result.confidence,
        severity: result.severity,
        timestamp: result.timestamp,
        fieldId: state.fieldId,
        imagePath: state.selectedImage?.path,
      );

      state = state.copyWith(
        isLoading: false,
        result: result,
        history: [historyItem, ...state.history],
      );

      return result;
    } catch (e) {
      final error = e is CropHealthException ? e : CropHealthException('$e');
      state = state.copyWith(
        isLoading: false,
        error: error.message,
        errorAr: error.messageAr,
      );
      return null;
    }
  }

  /// Diagnose from camera capture
  /// التشخيص من التقاط الكاميرا
  Future<DiagnosisResult?> diagnoseFromBytes(
    List<int> imageBytes,
    String filename,
  ) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final result = await _repository.diagnoseFromBytes(
        imageBytes,
        filename,
        fieldId: state.fieldId,
        cropType: state.selectedCropType,
      );

      state = state.copyWith(
        isLoading: false,
        result: result,
      );

      return result;
    } catch (e) {
      final error = e is CropHealthException ? e : CropHealthException('$e');
      state = state.copyWith(
        isLoading: false,
        error: error.message,
        errorAr: error.messageAr,
      );
      return null;
    }
  }

  /// Clear current diagnosis
  /// مسح التشخيص الحالي
  void clearDiagnosis() {
    state = state.copyWith(
      result: null,
      selectedImage: null,
      error: null,
    );
  }

  /// Clear history
  /// مسح السجل
  void clearHistory() {
    state = state.copyWith(history: []);
  }

  /// Mark diagnosis as resolved
  /// تحديد التشخيص كمحلول
  void markAsResolved(String diagnosisId) {
    final updatedHistory = state.history.map((item) {
      if (item.diagnosisId == diagnosisId) {
        return DiagnosisHistoryItem(
          diagnosisId: item.diagnosisId,
          diseaseName: item.diseaseName,
          diseaseNameAr: item.diseaseNameAr,
          confidence: item.confidence,
          severity: item.severity,
          timestamp: item.timestamp,
          fieldId: item.fieldId,
          imagePath: item.imagePath,
          isResolved: true,
        );
      }
      return item;
    }).toList();

    state = state.copyWith(history: updatedHistory);
  }
}

/// Provider for diagnosis state
/// موفر حالة التشخيص
final diagnosisProvider =
    StateNotifierProvider<DiagnosisNotifier, DiagnosisState>((ref) {
  final repository = ref.watch(cropHealthRepositoryProvider);
  return DiagnosisNotifier(repository);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Batch Diagnosis
// تشخيص الدفعات
// ═══════════════════════════════════════════════════════════════════════════════

/// State for batch diagnosis
/// حالة تشخيص الدفعة
class BatchDiagnosisState {
  final bool isLoading;
  final List<File> selectedImages;
  final BatchDiagnosisResult? result;
  final String? error;
  final double progress; // 0.0 to 1.0

  const BatchDiagnosisState({
    this.isLoading = false,
    this.selectedImages = const [],
    this.result,
    this.error,
    this.progress = 0,
  });

  BatchDiagnosisState copyWith({
    bool? isLoading,
    List<File>? selectedImages,
    BatchDiagnosisResult? result,
    String? error,
    double? progress,
  }) {
    return BatchDiagnosisState(
      isLoading: isLoading ?? this.isLoading,
      selectedImages: selectedImages ?? this.selectedImages,
      result: result ?? this.result,
      error: error,
      progress: progress ?? this.progress,
    );
  }
}

/// Notifier for batch diagnosis
/// مُعلم تشخيص الدفعة
class BatchDiagnosisNotifier extends StateNotifier<BatchDiagnosisState> {
  final CropHealthRepository _repository;

  BatchDiagnosisNotifier(this._repository) : super(const BatchDiagnosisState());

  /// Add images for batch processing
  /// إضافة صور للمعالجة الدفعية
  void addImages(List<File> images) {
    final current = [...state.selectedImages, ...images];
    if (current.length > 20) {
      state = state.copyWith(
        error: 'Maximum 20 images allowed',
        selectedImages: current.take(20).toList(),
      );
    } else {
      state = state.copyWith(selectedImages: current, error: null);
    }
  }

  /// Remove image from batch
  /// إزالة صورة من الدفعة
  void removeImage(int index) {
    final updated = [...state.selectedImages]..removeAt(index);
    state = state.copyWith(selectedImages: updated);
  }

  /// Clear all images
  /// مسح جميع الصور
  void clearImages() {
    state = state.copyWith(selectedImages: [], result: null, error: null);
  }

  /// Run batch diagnosis
  /// تشغيل التشخيص الدفعي
  Future<BatchDiagnosisResult?> runBatchDiagnosis({String? fieldId}) async {
    if (state.selectedImages.isEmpty) {
      state = state.copyWith(error: 'No images selected');
      return null;
    }

    state = state.copyWith(isLoading: true, error: null, progress: 0);

    try {
      final result = await _repository.batchDiagnose(
        state.selectedImages,
        fieldId: fieldId,
      );

      state = state.copyWith(
        isLoading: false,
        result: result,
        progress: 1.0,
      );

      return result;
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
      return null;
    }
  }
}

/// Provider for batch diagnosis
/// موفر التشخيص الدفعي
final batchDiagnosisProvider =
    StateNotifierProvider<BatchDiagnosisNotifier, BatchDiagnosisState>((ref) {
  final repository = ref.watch(cropHealthRepositoryProvider);
  return BatchDiagnosisNotifier(repository);
});

// ═══════════════════════════════════════════════════════════════════════════════
// Expert Review
// مراجعة الخبير
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for requesting expert review
/// موفر لطلب مراجعة الخبير
final expertReviewProvider = FutureProvider.family<ExpertReviewResponse,
    ({String diagnosisId, File image, String? notes, String urgency})>(
  (ref, params) async {
    final repository = ref.watch(cropHealthRepositoryProvider);
    return repository.requestExpertReview(
      params.diagnosisId,
      params.image,
      farmerNotes: params.notes,
      urgency: params.urgency,
    );
  },
);
