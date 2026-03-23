/// Vision Feature Providers
/// موفرو ميزة الرؤية
///
/// Riverpod providers for vision/detection state management.
library;

import 'dart:typed_data';

import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../data/yolo26_service.dart';
import '../../domain/detection_model.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Re-exports from yolo26_service
// ═══════════════════════════════════════════════════════════════════════════════

// These are already defined in yolo26_service.dart:
// - yolo26ServiceProvider
// - onDeviceModelAvailableProvider
// - detectionSettingsProvider

// ═══════════════════════════════════════════════════════════════════════════════
// Detection History Provider
// موفر سجل الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// State for detection history
/// حالة سجل الكشف
class DetectionHistoryState {
  final List<DetectionResult> results;
  final List<DetectionSession> sessions;
  final bool isLoading;

  const DetectionHistoryState({
    this.results = const [],
    this.sessions = const [],
    this.isLoading = false,
  });

  DetectionHistoryState copyWith({
    List<DetectionResult>? results,
    List<DetectionSession>? sessions,
    bool? isLoading,
  }) {
    return DetectionHistoryState(
      results: results ?? this.results,
      sessions: sessions ?? this.sessions,
      isLoading: isLoading ?? this.isLoading,
    );
  }

  /// Get results for a specific field
  List<DetectionResult> getResultsForField(String fieldId) {
    return results.where((r) => r.fieldId == fieldId).toList();
  }

  /// Get total detection count
  int get totalDetections {
    return results.fold(0, (sum, r) => sum + r.totalDetections);
  }

  /// Get count by detection type
  Map<DetectionType, int> get countByType {
    final counts = <DetectionType, int>{};
    for (final result in results) {
      for (final detection in result.detections) {
        counts[detection.detectionType] =
            (counts[detection.detectionType] ?? 0) + 1;
      }
    }
    return counts;
  }
}

/// Notifier for detection history
/// مُعلم سجل الكشف
class DetectionHistoryNotifier extends StateNotifier<DetectionHistoryState> {
  int _sessionCounter = 0;

  DetectionHistoryNotifier() : super(const DetectionHistoryState());

  /// Add a detection result to history
  void addResult(DetectionResult result) {
    state = state.copyWith(
      results: [result, ...state.results].take(100).toList(), // Keep last 100
    );
  }

  /// Start a new detection session
  DetectionSession startSession({String? fieldId}) {
    _sessionCounter++;
    final session = DetectionSession(
      sessionId: '${DateTime.now().millisecondsSinceEpoch}_$_sessionCounter',
      fieldId: fieldId,
      startTime: DateTime.now(),
    );

    state = state.copyWith(
      sessions: [session, ...state.sessions],
    );

    return session;
  }

  /// End a detection session
  void endSession(String sessionId) {
    final updatedSessions = state.sessions.map((s) {
      if (s.sessionId == sessionId) {
        return DetectionSession(
          sessionId: s.sessionId,
          fieldId: s.fieldId,
          startTime: s.startTime,
          endTime: DateTime.now(),
          results: s.results,
          imagesProcessed: s.imagesProcessed,
          totalDetections: s.totalDetections,
          notes: s.notes,
          latitude: s.latitude,
          longitude: s.longitude,
        );
      }
      return s;
    }).toList();

    state = state.copyWith(sessions: updatedSessions);
  }

  /// Add result to session
  void addResultToSession(String sessionId, DetectionResult result) {
    final updatedSessions = state.sessions.map((s) {
      if (s.sessionId == sessionId) {
        return DetectionSession(
          sessionId: s.sessionId,
          fieldId: s.fieldId,
          startTime: s.startTime,
          endTime: s.endTime,
          results: [...s.results, result],
          imagesProcessed: s.imagesProcessed + 1,
          totalDetections: s.totalDetections + result.totalDetections,
          notes: s.notes,
          latitude: s.latitude,
          longitude: s.longitude,
        );
      }
      return s;
    }).toList();

    state = state.copyWith(sessions: updatedSessions);
    addResult(result);
  }

  /// Clear all history
  void clearHistory() {
    state = const DetectionHistoryState();
  }

  /// Clear results for a specific field
  void clearFieldHistory(String fieldId) {
    state = state.copyWith(
      results: state.results.where((r) => r.fieldId != fieldId).toList(),
      sessions: state.sessions.where((s) => s.fieldId != fieldId).toList(),
    );
  }
}

/// Provider for detection history
/// موفر سجل الكشف
final detectionHistoryProvider =
    StateNotifierProvider<DetectionHistoryNotifier, DetectionHistoryState>(
        (ref) {
  return DetectionHistoryNotifier();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Quick Detection Provider
// موفر الكشف السريع
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for quick pest detection
/// موفر الكشف السريع عن الآفات
final quickPestDetectionProvider = FutureProvider.family<List<Detection>,
    ({Uint8List imageBytes, String? fieldId})>((ref, params) async {
  final service = ref.watch(yolo26ServiceProvider);
  return service.detectPests(
    params.imageBytes,
    fieldId: params.fieldId,
  );
});

/// Provider for quick disease detection
/// موفر الكشف السريع عن الأمراض
final quickDiseaseDetectionProvider = FutureProvider.family<List<Detection>,
    ({Uint8List imageBytes, String? fieldId})>((ref, params) async {
  final service = ref.watch(yolo26ServiceProvider);
  return service.detectDiseases(
    params.imageBytes,
    fieldId: params.fieldId,
  );
});

/// Provider for quick plant counting
/// موفر العد السريع للنباتات
final quickPlantCountProvider = FutureProvider.family<
    PlantCountResult,
    ({
      Uint8List imageBytes,
      String? fieldId,
      double? imageAreaM2
    })>((ref, params) async {
  final service = ref.watch(yolo26ServiceProvider);
  return service.countPlantsDetailed(
    params.imageBytes,
    fieldId: params.fieldId,
    imageAreaM2: params.imageAreaM2,
  );
});

// ═══════════════════════════════════════════════════════════════════════════════
// Model Status Provider
// موفر حالة النموذج
// ═══════════════════════════════════════════════════════════════════════════════

/// Model status information
/// معلومات حالة النموذج
class ModelStatus {
  final bool pestModelLoaded;
  final bool diseaseModelLoaded;
  final bool plantModelLoaded;
  final ModelInfo? pestModelInfo;
  final ModelInfo? diseaseModelInfo;
  final ModelInfo? plantModelInfo;
  final String? error;

  const ModelStatus({
    this.pestModelLoaded = false,
    this.diseaseModelLoaded = false,
    this.plantModelLoaded = false,
    this.pestModelInfo,
    this.diseaseModelInfo,
    this.plantModelInfo,
    this.error,
  });

  bool get anyModelLoaded =>
      pestModelLoaded || diseaseModelLoaded || plantModelLoaded;

  bool get allModelsLoaded =>
      pestModelLoaded && diseaseModelLoaded && plantModelLoaded;

  int get totalClasses {
    int total = 0;
    if (pestModelInfo != null) total += pestModelInfo!.numClasses;
    if (diseaseModelInfo != null) total += diseaseModelInfo!.numClasses;
    if (plantModelInfo != null) total += plantModelInfo!.numClasses;
    return total;
  }
}

/// Provider for model status
/// موفر حالة النموذج
final modelStatusProvider = FutureProvider<ModelStatus>((ref) async {
  final service = ref.watch(yolo26ServiceProvider);

  try {
    final available = await service.isOnDeviceAvailable();

    if (!available) {
      return ModelStatus(
        error: service.initError ?? 'النماذج غير متاحة',
      );
    }

    final modelInfos = service.modelInfos;

    return ModelStatus(
      pestModelLoaded: modelInfos['pest'] != null,
      diseaseModelLoaded: modelInfos['disease'] != null,
      plantModelLoaded: modelInfos['plant'] != null,
      pestModelInfo: modelInfos['pest'],
      diseaseModelInfo: modelInfos['disease'],
      plantModelInfo: modelInfos['plant'],
    );
  } catch (e) {
    return ModelStatus(error: e.toString());
  }
});

// ═══════════════════════════════════════════════════════════════════════════════
// Field Detection Summary Provider
// موفر ملخص كشف الحقل
// ═══════════════════════════════════════════════════════════════════════════════

/// Summary of detections for a field
/// ملخص الكشوفات للحقل
class FieldDetectionSummary {
  final String fieldId;
  final int totalScans;
  final int totalDetections;
  final Map<DetectionType, int> countByType;
  final DateTime? lastScanTime;
  final List<String> topIssues;

  const FieldDetectionSummary({
    required this.fieldId,
    this.totalScans = 0,
    this.totalDetections = 0,
    this.countByType = const {},
    this.lastScanTime,
    this.topIssues = const [],
  });
}

/// Provider for field detection summary
/// موفر ملخص كشف الحقل
final fieldDetectionSummaryProvider =
    Provider.family<FieldDetectionSummary, String>((ref, fieldId) {
  final history = ref.watch(detectionHistoryProvider);
  final fieldResults = history.getResultsForField(fieldId);

  if (fieldResults.isEmpty) {
    return FieldDetectionSummary(fieldId: fieldId);
  }

  final countByType = <DetectionType, int>{};
  final issueCount = <String, int>{};

  for (final result in fieldResults) {
    for (final detection in result.detections) {
      countByType[detection.detectionType] =
          (countByType[detection.detectionType] ?? 0) + 1;

      // Track issue frequency
      issueCount[detection.classNameAr] =
          (issueCount[detection.classNameAr] ?? 0) + 1;
    }
  }

  // Sort issues by frequency
  final sortedIssues = issueCount.entries.toList()
    ..sort((a, b) => b.value.compareTo(a.value));

  return FieldDetectionSummary(
    fieldId: fieldId,
    totalScans: fieldResults.length,
    totalDetections: fieldResults.fold(0, (sum, r) => sum + r.totalDetections),
    countByType: countByType,
    lastScanTime: fieldResults.first.timestamp,
    topIssues: sortedIssues.take(5).map((e) => e.key).toList(),
  );
});
