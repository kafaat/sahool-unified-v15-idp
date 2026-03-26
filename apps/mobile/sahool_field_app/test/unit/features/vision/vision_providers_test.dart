/// Vision Providers Unit Tests
/// اختبارات وحدات موفرات الرؤية
///
/// Tests DetectionHistoryNotifier, DetectionHistoryState, ModelStatus,
/// FieldDetectionSummary, and session management.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/vision/data/yolo26_service.dart';
import 'package:sahool_field_app/features/vision/domain/detection_model.dart';
import 'package:sahool_field_app/features/vision/presentation/providers/vision_providers.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Test Helpers
// ═══════════════════════════════════════════════════════════════════════════════

/// Create a sample Detection for testing
Detection _createDetection({
  String id = 'det_1',
  String className = 'Aphid',
  String classNameAr = 'من',
  DetectionType type = DetectionType.pest,
  double confidence = 0.85,
}) {
  return Detection(
    detectionId: id,
    className: className,
    classNameAr: classNameAr,
    detectionType: type,
    confidence: confidence,
    bbox: const BoundingBox(x: 0.1, y: 0.1, width: 0.2, height: 0.2),
    source: DetectionSource.onDevice,
  );
}

/// Create a sample DetectionResult for testing
DetectionResult _createDetectionResult({
  String id = 'result_1',
  List<Detection>? detections,
  String? fieldId,
  int processingTimeMs = 100,
}) {
  return DetectionResult(
    resultId: id,
    detections: detections ?? [_createDetection()],
    processingTimeMs: processingTimeMs,
    imageWidth: 640,
    imageHeight: 480,
    source: DetectionSource.onDevice,
    modelVersion: '26.0',
    fieldId: fieldId,
    timestamp: DateTime.now(),
  );
}

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionHistoryState
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionHistoryState', () {
    test('should have empty defaults', () {
      const state = DetectionHistoryState();

      expect(state.results, isEmpty);
      expect(state.sessions, isEmpty);
      expect(state.isLoading, isFalse);
      expect(state.totalDetections, 0);
      expect(state.countByType, isEmpty);
    });

    test('should calculate totalDetections from all results', () {
      final state = DetectionHistoryState(
        results: [
          _createDetectionResult(
            id: 'r1',
            detections: [
              _createDetection(id: 'd1'),
              _createDetection(id: 'd2'),
            ],
          ),
          _createDetectionResult(
            id: 'r2',
            detections: [
              _createDetection(id: 'd3'),
            ],
          ),
        ],
      );

      expect(state.totalDetections, 3);
    });

    test('should calculate countByType across all results', () {
      final state = DetectionHistoryState(
        results: [
          _createDetectionResult(
            id: 'r1',
            detections: [
              _createDetection(id: 'd1', type: DetectionType.pest),
              _createDetection(id: 'd2', type: DetectionType.disease),
            ],
          ),
          _createDetectionResult(
            id: 'r2',
            detections: [
              _createDetection(id: 'd3', type: DetectionType.pest),
              _createDetection(id: 'd4', type: DetectionType.weed),
            ],
          ),
        ],
      );

      final counts = state.countByType;
      expect(counts[DetectionType.pest], 2);
      expect(counts[DetectionType.disease], 1);
      expect(counts[DetectionType.weed], 1);
    });

    test('getResultsForField should filter by fieldId', () {
      final state = DetectionHistoryState(
        results: [
          _createDetectionResult(id: 'r1', fieldId: 'field_001'),
          _createDetectionResult(id: 'r2', fieldId: 'field_002'),
          _createDetectionResult(id: 'r3', fieldId: 'field_001'),
          _createDetectionResult(id: 'r4'), // no fieldId
        ],
      );

      final fieldResults = state.getResultsForField('field_001');
      expect(fieldResults, hasLength(2));
      expect(fieldResults.every((r) => r.fieldId == 'field_001'), isTrue);
    });

    test('getResultsForField should return empty when no matches', () {
      final state = DetectionHistoryState(
        results: [
          _createDetectionResult(id: 'r1', fieldId: 'field_001'),
        ],
      );

      final fieldResults = state.getResultsForField('field_999');
      expect(fieldResults, isEmpty);
    });

    test('copyWith should update specified fields only', () {
      const original = DetectionHistoryState(isLoading: false);

      final updated = original.copyWith(isLoading: true);
      expect(updated.isLoading, isTrue);
      expect(updated.results, isEmpty);
      expect(updated.sessions, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionHistoryNotifier
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionHistoryNotifier', () {
    late DetectionHistoryNotifier notifier;

    setUp(() {
      notifier = DetectionHistoryNotifier();
    });

    tearDown(() {
      notifier.dispose();
    });

    group('addResult', () {
      test('should add a result to the beginning of the list', () {
        // Arrange
        final result1 = _createDetectionResult(id: 'r1');
        final result2 = _createDetectionResult(id: 'r2');

        // Act
        notifier.addResult(result1);
        notifier.addResult(result2);

        // Assert
        expect(notifier.state.results, hasLength(2));
        expect(notifier.state.results.first.resultId, 'r2');
        expect(notifier.state.results.last.resultId, 'r1');
      });

      test('should enforce maximum 100 items in history', () {
        // Arrange & Act - add 105 results
        for (int i = 0; i < 105; i++) {
          notifier.addResult(_createDetectionResult(id: 'r_$i'));
        }

        // Assert
        expect(notifier.state.results, hasLength(100));
        // Most recent should be first
        expect(notifier.state.results.first.resultId, 'r_104');
        // Oldest that survived should be r_5 (items 0-4 were dropped)
        expect(notifier.state.results.last.resultId, 'r_5');
      });

      test('should maintain field associations', () {
        // Arrange & Act
        notifier.addResult(_createDetectionResult(
          id: 'r1',
          fieldId: 'field_A',
        ));
        notifier.addResult(_createDetectionResult(
          id: 'r2',
          fieldId: 'field_B',
        ));
        notifier.addResult(_createDetectionResult(
          id: 'r3',
          fieldId: 'field_A',
        ));

        // Assert
        final fieldAResults = notifier.state.getResultsForField('field_A');
        expect(fieldAResults, hasLength(2));
      });
    });

    group('startSession', () {
      test('should create a new session and add to state', () {
        // Act
        final session = notifier.startSession(fieldId: 'field_001');

        // Assert
        expect(session.sessionId, isNotEmpty);
        expect(session.fieldId, 'field_001');
        expect(session.isOngoing, isTrue);
        expect(session.startTime, isNotNull);
        expect(notifier.state.sessions, hasLength(1));
      });

      test('should add new session at beginning of list', () {
        // Act
        final session1 = notifier.startSession(fieldId: 'field_001');
        final session2 = notifier.startSession(fieldId: 'field_002');

        // Assert
        expect(notifier.state.sessions, hasLength(2));
        expect(notifier.state.sessions.first.sessionId, session2.sessionId);
        expect(notifier.state.sessions.last.sessionId, session1.sessionId);
      });

      test('should create session without fieldId', () {
        // Act
        final session = notifier.startSession();

        // Assert
        expect(session.fieldId, isNull);
        expect(session.isOngoing, isTrue);
      });
    });

    group('endSession', () {
      test('should set endTime on the specified session', () {
        // Arrange
        final session = notifier.startSession(fieldId: 'field_001');

        // Act
        notifier.endSession(session.sessionId);

        // Assert
        final updatedSession = notifier.state.sessions.first;
        expect(updatedSession.endTime, isNotNull);
        expect(updatedSession.isOngoing, isFalse);
        expect(updatedSession.duration, isNotNull);
      });

      test('should not modify other sessions', () {
        // Arrange
        final session1 = notifier.startSession(fieldId: 'field_001');
        notifier.startSession(fieldId: 'field_002');

        // Act
        notifier.endSession(session1.sessionId);

        // Assert
        // session2 is first (most recent), session1 is second
        final session2State = notifier.state.sessions.first;
        final session1State = notifier.state.sessions.last;

        expect(session2State.isOngoing, isTrue);
        expect(session1State.isOngoing, isFalse);
      });

      test('should be idempotent for non-existing sessionId', () {
        // Arrange
        notifier.startSession(fieldId: 'field_001');

        // Act - end a non-existing session
        notifier.endSession('non_existing_session');

        // Assert - original session should be unchanged
        expect(notifier.state.sessions.first.isOngoing, isTrue);
      });
    });

    group('addResultToSession', () {
      test('should add result to specified session and global history', () {
        // Arrange
        final session = notifier.startSession(fieldId: 'field_001');
        final result = _createDetectionResult(id: 'r1', fieldId: 'field_001');

        // Act
        notifier.addResultToSession(session.sessionId, result);

        // Assert
        final updatedSession = notifier.state.sessions.first;
        expect(updatedSession.results, hasLength(1));
        expect(updatedSession.imagesProcessed, 1);
        expect(updatedSession.totalDetections, 1);

        // Also added to global history
        expect(notifier.state.results, hasLength(1));
        expect(notifier.state.results.first.resultId, 'r1');
      });

      test('should accumulate results in session', () {
        // Arrange
        final session = notifier.startSession();
        final result1 = _createDetectionResult(
          id: 'r1',
          detections: [
            _createDetection(id: 'd1'),
            _createDetection(id: 'd2'),
          ],
        );
        final result2 = _createDetectionResult(
          id: 'r2',
          detections: [
            _createDetection(id: 'd3'),
          ],
        );

        // Act
        notifier.addResultToSession(session.sessionId, result1);
        notifier.addResultToSession(session.sessionId, result2);

        // Assert
        final updatedSession = notifier.state.sessions.first;
        expect(updatedSession.results, hasLength(2));
        expect(updatedSession.imagesProcessed, 2);
        expect(updatedSession.totalDetections, 3); // 2 + 1
      });

      test('should not modify other sessions when adding to one', () {
        // Arrange
        final session1 = notifier.startSession(fieldId: 'field_001');
        notifier.startSession(fieldId: 'field_002');
        final result = _createDetectionResult(id: 'r1');

        // Act
        notifier.addResultToSession(session1.sessionId, result);

        // Assert
        // session2 is first, session1 is second
        final session2State = notifier.state.sessions.first;
        expect(session2State.results, isEmpty);
        expect(session2State.imagesProcessed, 0);
      });
    });

    group('clearHistory', () {
      test('should clear all results and sessions', () {
        // Arrange
        notifier.addResult(_createDetectionResult(id: 'r1'));
        notifier.addResult(_createDetectionResult(id: 'r2'));
        notifier.startSession(fieldId: 'field_001');

        expect(notifier.state.results, hasLength(2));
        expect(notifier.state.sessions, hasLength(1));

        // Act
        notifier.clearHistory();

        // Assert
        expect(notifier.state.results, isEmpty);
        expect(notifier.state.sessions, isEmpty);
        expect(notifier.state.isLoading, isFalse);
      });

      test('should be safe to call on empty state', () {
        // Act
        notifier.clearHistory();

        // Assert
        expect(notifier.state.results, isEmpty);
        expect(notifier.state.sessions, isEmpty);
      });
    });

    group('clearFieldHistory', () {
      test('should remove only results and sessions for specified field', () {
        // Arrange
        notifier.addResult(_createDetectionResult(id: 'r1', fieldId: 'field_A'));
        notifier.addResult(_createDetectionResult(id: 'r2', fieldId: 'field_B'));
        notifier.addResult(_createDetectionResult(id: 'r3', fieldId: 'field_A'));
        notifier.addResult(_createDetectionResult(id: 'r4')); // no fieldId

        notifier.startSession(fieldId: 'field_A');
        notifier.startSession(fieldId: 'field_B');

        // Act
        notifier.clearFieldHistory('field_A');

        // Assert
        expect(notifier.state.results, hasLength(2)); // r2 and r4 remain
        expect(
          notifier.state.results.any((r) => r.fieldId == 'field_A'),
          isFalse,
        );
        expect(notifier.state.sessions, hasLength(1));
        expect(notifier.state.sessions.first.fieldId, 'field_B');
      });

      test('should not remove results without fieldId', () {
        // Arrange
        notifier.addResult(_createDetectionResult(id: 'r1')); // no fieldId
        notifier.addResult(_createDetectionResult(id: 'r2', fieldId: 'field_A'));

        // Act
        notifier.clearFieldHistory('field_A');

        // Assert
        expect(notifier.state.results, hasLength(1));
        expect(notifier.state.results.first.resultId, 'r1');
      });

      test('should be safe when field has no history', () {
        // Arrange
        notifier.addResult(_createDetectionResult(id: 'r1', fieldId: 'field_A'));

        // Act
        notifier.clearFieldHistory('field_non_existing');

        // Assert
        expect(notifier.state.results, hasLength(1));
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ModelStatus
  // ═══════════════════════════════════════════════════════════════════════════

  group('ModelStatus', () {
    test('should have default values of not loaded', () {
      const status = ModelStatus();

      expect(status.pestModelLoaded, isFalse);
      expect(status.diseaseModelLoaded, isFalse);
      expect(status.plantModelLoaded, isFalse);
      expect(status.pestModelInfo, isNull);
      expect(status.diseaseModelInfo, isNull);
      expect(status.plantModelInfo, isNull);
      expect(status.error, isNull);
    });

    test('anyModelLoaded should return true when at least one loaded', () {
      const status = ModelStatus(pestModelLoaded: true);
      expect(status.anyModelLoaded, isTrue);
    });

    test('anyModelLoaded should return false when none loaded', () {
      const status = ModelStatus();
      expect(status.anyModelLoaded, isFalse);
    });

    test('allModelsLoaded should return true when all loaded', () {
      const status = ModelStatus(
        pestModelLoaded: true,
        diseaseModelLoaded: true,
        plantModelLoaded: true,
      );
      expect(status.allModelsLoaded, isTrue);
    });

    test('allModelsLoaded should return false when partially loaded', () {
      const status = ModelStatus(
        pestModelLoaded: true,
        diseaseModelLoaded: true,
        plantModelLoaded: false,
      );
      expect(status.allModelsLoaded, isFalse);
    });

    test('totalClasses should sum all model class counts', () {
      const status = ModelStatus(
        pestModelLoaded: true,
        diseaseModelLoaded: true,
        plantModelLoaded: true,
        pestModelInfo: ModelInfo(
          name: 'pest',
          version: '1.0',
          inputSize: 640,
          numClasses: 22,
          labels: [],
          labelsAr: [],
        ),
        diseaseModelInfo: ModelInfo(
          name: 'disease',
          version: '1.0',
          inputSize: 640,
          numClasses: 34,
          labels: [],
          labelsAr: [],
        ),
        plantModelInfo: ModelInfo(
          name: 'plant',
          version: '1.0',
          inputSize: 320,
          numClasses: 1,
          labels: [],
          labelsAr: [],
        ),
      );

      expect(status.totalClasses, 57); // 22 + 34 + 1
    });

    test('totalClasses should handle null ModelInfo gracefully', () {
      const status = ModelStatus(
        pestModelLoaded: true,
        pestModelInfo: ModelInfo(
          name: 'pest',
          version: '1.0',
          inputSize: 640,
          numClasses: 22,
          labels: [],
          labelsAr: [],
        ),
      );

      expect(status.totalClasses, 22);
    });

    test('totalClasses should return 0 when no models loaded', () {
      const status = ModelStatus();
      expect(status.totalClasses, 0);
    });

    test('should store error message', () {
      const status = ModelStatus(
        error: 'Failed to load TFLite models',
      );

      expect(status.error, 'Failed to load TFLite models');
      expect(status.anyModelLoaded, isFalse);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // FieldDetectionSummary
  // ═══════════════════════════════════════════════════════════════════════════

  group('FieldDetectionSummary', () {
    test('should have default values', () {
      const summary = FieldDetectionSummary(fieldId: 'field_001');

      expect(summary.fieldId, 'field_001');
      expect(summary.totalScans, 0);
      expect(summary.totalDetections, 0);
      expect(summary.countByType, isEmpty);
      expect(summary.lastScanTime, isNull);
      expect(summary.topIssues, isEmpty);
    });

    test('should store all properties', () {
      final summary = FieldDetectionSummary(
        fieldId: 'field_002',
        totalScans: 15,
        totalDetections: 42,
        countByType: const {
          DetectionType.pest: 20,
          DetectionType.disease: 15,
          DetectionType.weed: 7,
        },
        lastScanTime: DateTime(2026, 2, 27),
        topIssues: const ['من', 'صدأ الأوراق', 'حشائش'],
      );

      expect(summary.fieldId, 'field_002');
      expect(summary.totalScans, 15);
      expect(summary.totalDetections, 42);
      expect(summary.countByType, hasLength(3));
      expect(summary.countByType[DetectionType.pest], 20);
      expect(summary.lastScanTime, isNotNull);
      expect(summary.topIssues, hasLength(3));
    });

    test('topIssues should reflect most frequent issues', () {
      const summary = FieldDetectionSummary(
        fieldId: 'field_003',
        topIssues: ['سوسة النخيل الحمراء', 'البياض الدقيقي', 'المن'],
      );

      expect(summary.topIssues.first, 'سوسة النخيل الحمراء');
      expect(summary.topIssues, hasLength(3));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionSettings
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionSettings', () {
    test('should have correct defaults', () {
      const settings = DetectionSettings();

      expect(settings.preferOnDevice, isTrue);
      expect(settings.confidenceThreshold, 0.5);
      expect(settings.enableFallback, isTrue);
      expect(settings.saveLocally, isTrue);
      expect(settings.maxImageSize, 2 * 1024 * 1024);
    });

    test('should support copyWith', () {
      const settings = DetectionSettings();

      final updated = settings.copyWith(
        confidenceThreshold: 0.7,
        preferOnDevice: false,
      );

      expect(updated.confidenceThreshold, 0.7);
      expect(updated.preferOnDevice, isFalse);
      expect(updated.enableFallback, isTrue); // unchanged
      expect(updated.saveLocally, isTrue); // unchanged
    });

    test('should create with custom values', () {
      const settings = DetectionSettings(
        preferOnDevice: false,
        confidenceThreshold: 0.8,
        enableFallback: false,
        saveLocally: false,
        maxImageSize: 5 * 1024 * 1024,
      );

      expect(settings.preferOnDevice, isFalse);
      expect(settings.confidenceThreshold, 0.8);
      expect(settings.enableFallback, isFalse);
      expect(settings.saveLocally, isFalse);
      expect(settings.maxImageSize, 5 * 1024 * 1024);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Integration scenario: Full detection workflow
  // ═══════════════════════════════════════════════════════════════════════════

  group('Detection workflow integration', () {
    late DetectionHistoryNotifier notifier;

    setUp(() {
      notifier = DetectionHistoryNotifier();
    });

    tearDown(() {
      notifier.dispose();
    });

    test('should support complete field scanning workflow', () {
      // Step 1: Start a session
      final session = notifier.startSession(fieldId: 'field_001');
      expect(notifier.state.sessions, hasLength(1));

      // Step 2: Add detection results to session
      final result1 = _createDetectionResult(
        id: 'r1',
        fieldId: 'field_001',
        detections: [
          _createDetection(id: 'd1', type: DetectionType.pest, className: 'Aphid', classNameAr: 'من'),
          _createDetection(id: 'd2', type: DetectionType.disease, className: 'Rust', classNameAr: 'صدأ'),
        ],
      );
      notifier.addResultToSession(session.sessionId, result1);

      final result2 = _createDetectionResult(
        id: 'r2',
        fieldId: 'field_001',
        detections: [
          _createDetection(id: 'd3', type: DetectionType.pest, className: 'Aphid', classNameAr: 'من'),
        ],
      );
      notifier.addResultToSession(session.sessionId, result2);

      // Step 3: Verify session state
      final updatedSession = notifier.state.sessions.first;
      expect(updatedSession.results, hasLength(2));
      expect(updatedSession.imagesProcessed, 2);
      expect(updatedSession.totalDetections, 3);

      // Step 4: Verify global history
      expect(notifier.state.results, hasLength(2));
      expect(notifier.state.totalDetections, 3);

      // Step 5: End session
      notifier.endSession(session.sessionId);
      expect(notifier.state.sessions.first.isOngoing, isFalse);

      // Step 6: Verify countByType
      final counts = notifier.state.countByType;
      expect(counts[DetectionType.pest], 2);
      expect(counts[DetectionType.disease], 1);

      // Step 7: Verify field-specific query
      final fieldResults = notifier.state.getResultsForField('field_001');
      expect(fieldResults, hasLength(2));
    });
  });
}
