import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:uuid/uuid.dart';
import '../../../../core/utils/app_logger.dart';
import '../../../../core/offline/offline_sync_engine.dart';
import '../../domain/models/scout_session.dart';

/// SAHOOL Field Scout Provider
/// مزود مسح الحقول الذكي
///
/// Features:
/// - Session management
/// - GPS tracking
/// - Checkpoint creation
/// - AI integration
/// - Offline support

class FieldScoutNotifier extends StateNotifier<FieldScoutState> {
  final Ref _ref;
  final _uuid = const Uuid();
  Timer? _trackingTimer;
  StreamSubscription? _locationSubscription;

  FieldScoutNotifier(this._ref) : super(const FieldScoutState());

  // ═══════════════════════════════════════════════════════════════════════════
  // إدارة الجلسة
  // ═══════════════════════════════════════════════════════════════════════════

  /// بدء جلسة مسح جديدة
  Future<ScoutSession> startSession({
    required String fieldId,
    required String fieldName,
    required String scouterId,
    required String scouterName,
  }) async {
    final session = ScoutSession(
      id: _uuid.v4(),
      fieldId: fieldId,
      fieldName: fieldName,
      scouterId: scouterId,
      scouterName: scouterName,
      startedAt: DateTime.now(),
      status: ScoutSessionStatus.active,
      checkpoints: [],
      trackPoints: [],
    );

    state = state.copyWith(
      currentSession: session,
      isTracking: true,
      error: null,
    );

    // Start GPS tracking
    _startTracking();

    AppLogger.i('Scout session started: ${session.id}', tag: 'SCOUT');
    return session;
  }

  /// إيقاف مؤقت للجلسة
  void pauseSession() {
    if (state.currentSession == null) return;

    _stopTracking();

    state = state.copyWith(
      currentSession: state.currentSession!.copyWith(
        status: ScoutSessionStatus.paused,
      ),
      isTracking: false,
    );

    AppLogger.i('Scout session paused', tag: 'SCOUT');
  }

  /// استئناف الجلسة
  void resumeSession() {
    if (state.currentSession == null) return;

    _startTracking();

    state = state.copyWith(
      currentSession: state.currentSession!.copyWith(
        status: ScoutSessionStatus.active,
      ),
      isTracking: true,
    );

    AppLogger.i('Scout session resumed', tag: 'SCOUT');
  }

  /// إنهاء الجلسة
  Future<ScoutSession> endSession() async {
    if (state.currentSession == null) {
      throw Exception('No active session');
    }

    _stopTracking();

    final summary = _generateSummary(state.currentSession!);
    final completedSession = state.currentSession!.copyWith(
      status: ScoutSessionStatus.completed,
      endedAt: DateTime.now(),
      summary: summary,
    );

    // Save to offline sync engine
    await OfflineSyncEngine.instance.enqueueCreate(
      entityType: 'scout_session',
      data: completedSession.toJson(),
      priority: SyncPriority.high,
    );

    state = state.copyWith(
      currentSession: null,
      lastCompletedSession: completedSession,
      isTracking: false,
    );

    AppLogger.i('Scout session completed: ${completedSession.id}', tag: 'SCOUT');
    return completedSession;
  }

  /// إلغاء الجلسة
  void cancelSession() {
    if (state.currentSession == null) return;

    _stopTracking();

    state = state.copyWith(
      currentSession: null,
      isTracking: false,
    );

    AppLogger.i('Scout session cancelled', tag: 'SCOUT');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // نقاط التفتيش
  // ═══════════════════════════════════════════════════════════════════════════

  /// إضافة نقطة تفتيش
  Future<ScoutCheckpoint> addCheckpoint({
    required GeoPoint location,
    required CheckpointType type,
    String? note,
    List<String>? photoUrls,
    IssueDetails? issue,
    Map<String, dynamic>? measurements,
  }) async {
    if (state.currentSession == null) {
      throw Exception('No active session');
    }

    final checkpoint = ScoutCheckpoint(
      id: _uuid.v4(),
      location: location,
      timestamp: DateTime.now(),
      type: type,
      note: note,
      photoUrls: photoUrls ?? [],
      issue: issue,
      measurements: measurements,
    );

    final updatedCheckpoints = [
      ...state.currentSession!.checkpoints,
      checkpoint,
    ];

    state = state.copyWith(
      currentSession: state.currentSession!.copyWith(
        checkpoints: updatedCheckpoints,
      ),
    );

    AppLogger.d('Checkpoint added: ${checkpoint.type.name}', tag: 'SCOUT');
    return checkpoint;
  }

  /// إضافة نقطة تفتيش سريعة (بدون تفاصيل)
  Future<ScoutCheckpoint> addQuickCheckpoint(GeoPoint location) async {
    return addCheckpoint(
      location: location,
      type: CheckpointType.routine,
    );
  }

  /// إضافة نقطة مشكلة
  Future<ScoutCheckpoint> addIssueCheckpoint({
    required GeoPoint location,
    required IssueCategory category,
    required IssueSeverity severity,
    required String description,
    List<String>? photoUrls,
    double? affectedAreaPercent,
  }) async {
    final issue = IssueDetails(
      category: category,
      severity: severity,
      description: description,
      affectedAreaPercent: affectedAreaPercent,
    );

    return addCheckpoint(
      location: location,
      type: CheckpointType.issue,
      photoUrls: photoUrls,
      issue: issue,
    );
  }

  /// حذف نقطة تفتيش
  void removeCheckpoint(String checkpointId) {
    if (state.currentSession == null) return;

    final updatedCheckpoints = state.currentSession!.checkpoints
        .where((c) => c.id != checkpointId)
        .toList();

    state = state.copyWith(
      currentSession: state.currentSession!.copyWith(
        checkpoints: updatedCheckpoints,
      ),
    );

    AppLogger.d('Checkpoint removed: $checkpointId', tag: 'SCOUT');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // تتبع GPS
  // ═══════════════════════════════════════════════════════════════════════════

  void _startTracking() {
    // In real implementation, use geolocator package
    _trackingTimer = Timer.periodic(
      const Duration(seconds: 5),
      (_) => _recordTrackPoint(),
    );
  }

  void _stopTracking() {
    _trackingTimer?.cancel();
    _trackingTimer = null;
    _locationSubscription?.cancel();
    _locationSubscription = null;
  }

  Future<void> _recordTrackPoint() async {
    if (state.currentSession == null) return;

    try {
      // Use geolocator to get real GPS coordinates
      // Import: import 'package:geolocator/geolocator.dart';
      // final position = await Geolocator.getCurrentPosition(
      //   desiredAccuracy: LocationAccuracy.high,
      // );
      // final newPoint = GeoPoint(
      //   latitude: position.latitude,
      //   longitude: position.longitude,
      //   accuracy: position.accuracy,
      //   timestamp: DateTime.now(),
      // );

      // TODO: Replace with Geolocator.getCurrentPosition() once geolocator
      // permission flow is integrated. For now, skip recording if no real
      // location is available.
      final currentLocation = state.currentLocation;
      if (currentLocation == null) {
        AppLogger.w('No GPS location available for track point', tag: 'SCOUT');
        return;
      }

      final newPoint = GeoPoint(
        latitude: currentLocation.latitude,
        longitude: currentLocation.longitude,
        accuracy: currentLocation.accuracy,
        timestamp: DateTime.now(),
      );

      final updatedTrackPoints = [
        ...state.currentSession!.trackPoints,
        newPoint,
      ];

      state = state.copyWith(
        currentSession: state.currentSession!.copyWith(
          trackPoints: updatedTrackPoints,
        ),
        currentLocation: newPoint,
      );
    } catch (e) {
      AppLogger.w('Failed to record track point: $e', tag: 'SCOUT');
    }
  }

  /// تحديث الموقع الحالي
  void updateCurrentLocation(GeoPoint location) {
    state = state.copyWith(currentLocation: location);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // تحليل AI
  // ═══════════════════════════════════════════════════════════════════════════

  /// تحليل صورة بالذكاء الاصطناعي
  /// TODO: Wire to yolo26-vision-service POST /api/v1/detect/disease
  /// or crop-intelligence-service for real AI analysis.
  Future<AIAnalysis> analyzeImage(String imagePath) async {
    state = state.copyWith(isAnalyzing: true);

    try {
      // TODO: Replace with actual API call to vision service:
      // final response = await _apiClient.post(
      //   '/api/v1/detect/disease',
      //   data: FormData.fromMap({
      //     'image': await MultipartFile.fromFile(imagePath),
      //     'field_id': state.currentSession?.fieldId,
      //   }),
      // );
      // final analysis = AIAnalysis.fromJson(response.data);

      // Placeholder: return a pending analysis indicating the service is not yet connected
      final analysis = AIAnalysis(
        modelVersion: 'pending',
        confidence: 0.0,
        detectedIssue: 'تحليل غير متاح - خدمة الذكاء الاصطناعي غير متصلة',
        category: IssueCategory.other,
        severity: IssueSeverity.low,
        suggestions: [
          'سيتم تحليل الصورة عند الاتصال بالخادم',
          'يمكنك إضافة ملاحظاتك يدوياً',
        ],
        analyzedAt: DateTime.now(),
      );

      state = state.copyWith(
        isAnalyzing: false,
        lastAnalysis: analysis,
      );

      AppLogger.i('AI analysis pending - service not connected', tag: 'SCOUT_AI');
      return analysis;
    } catch (e) {
      state = state.copyWith(
        isAnalyzing: false,
        error: e.toString(),
      );
      rethrow;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الملخص
  // ═══════════════════════════════════════════════════════════════════════════

  ScoutSessionSummary _generateSummary(ScoutSession session) {
    final issuesByCategory = <IssueCategory, int>{};
    final issuesBySeverity = <IssueSeverity, int>{};
    int photosCount = 0;

    for (final checkpoint in session.checkpoints) {
      photosCount += checkpoint.photoUrls.length;

      if (checkpoint.issue != null) {
        final category = checkpoint.issue!.category;
        final severity = checkpoint.issue!.severity;

        issuesByCategory[category] = (issuesByCategory[category] ?? 0) + 1;
        issuesBySeverity[severity] = (issuesBySeverity[severity] ?? 0) + 1;
      }
    }

    // Determine overall health status
    String healthStatus;
    if (issuesBySeverity[IssueSeverity.critical] != null) {
      healthStatus = 'حرج - يحتاج تدخل فوري';
    } else if (issuesBySeverity[IssueSeverity.high] != null) {
      healthStatus = 'سيء - يحتاج اهتمام';
    } else if (issuesBySeverity[IssueSeverity.medium] != null) {
      healthStatus = 'متوسط - مراقبة مطلوبة';
    } else if (session.issuesCount > 0) {
      healthStatus = 'جيد - مشاكل بسيطة';
    } else {
      healthStatus = 'ممتاز - لا مشاكل';
    }

    return ScoutSessionSummary(
      totalCheckpoints: session.checkpoints.length,
      issuesFound: session.issuesCount,
      photosCount: photosCount,
      distanceMeters: session.distanceMeters,
      duration: session.duration,
      fieldCoveragePercent: _estimateCoverage(session),
      issuesByCategory: issuesByCategory,
      issuesBySeverity: issuesBySeverity,
      overallHealthStatus: healthStatus,
      recommendations: _generateRecommendations(issuesByCategory),
    );
  }

  double _estimateCoverage(ScoutSession session) {
    // Simple estimation based on distance and checkpoints
    // In real implementation, calculate based on field polygon
    if (session.trackPoints.isEmpty) return 0;
    return (session.distanceMeters / 100).clamp(0, 100);
  }

  List<String> _generateRecommendations(Map<IssueCategory, int> issues) {
    final recommendations = <String>[];

    if (issues[IssueCategory.pest] != null) {
      recommendations.add('تطبيق مبيد حشري مناسب');
    }
    if (issues[IssueCategory.disease] != null) {
      recommendations.add('فحص الأمراض بدقة ومعالجتها');
    }
    if (issues[IssueCategory.weed] != null) {
      recommendations.add('إزالة الأعشاب الضارة');
    }
    if (issues[IssueCategory.water] != null) {
      recommendations.add('مراجعة نظام الري');
    }
    if (issues[IssueCategory.nutrient] != null) {
      recommendations.add('فحص التربة وتطبيق سماد مناسب');
    }

    if (recommendations.isEmpty) {
      recommendations.add('استمر في المراقبة الدورية');
    }

    return recommendations;
  }

  @override
  void dispose() {
    _stopTracking();
    super.dispose();
  }
}

/// حالة مسح الحقول
class FieldScoutState {
  final ScoutSession? currentSession;
  final ScoutSession? lastCompletedSession;
  final GeoPoint? currentLocation;
  final bool isTracking;
  final bool isAnalyzing;
  final AIAnalysis? lastAnalysis;
  final String? error;

  const FieldScoutState({
    this.currentSession,
    this.lastCompletedSession,
    this.currentLocation,
    this.isTracking = false,
    this.isAnalyzing = false,
    this.lastAnalysis,
    this.error,
  });

  bool get hasActiveSession => currentSession != null;

  FieldScoutState copyWith({
    ScoutSession? currentSession,
    ScoutSession? lastCompletedSession,
    GeoPoint? currentLocation,
    bool? isTracking,
    bool? isAnalyzing,
    AIAnalysis? lastAnalysis,
    String? error,
  }) {
    return FieldScoutState(
      currentSession: currentSession ?? this.currentSession,
      lastCompletedSession: lastCompletedSession ?? this.lastCompletedSession,
      currentLocation: currentLocation ?? this.currentLocation,
      isTracking: isTracking ?? this.isTracking,
      isAnalyzing: isAnalyzing ?? this.isAnalyzing,
      lastAnalysis: lastAnalysis ?? this.lastAnalysis,
      error: error,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

final fieldScoutProvider = StateNotifierProvider.autoDispose<FieldScoutNotifier, FieldScoutState>((ref) {
  return FieldScoutNotifier(ref);
});

final currentScoutSessionProvider = Provider.autoDispose<ScoutSession?>((ref) {
  return ref.watch(fieldScoutProvider).currentSession;
});

final isScoutingProvider = Provider.autoDispose<bool>((ref) {
  return ref.watch(fieldScoutProvider).hasActiveSession;
});
