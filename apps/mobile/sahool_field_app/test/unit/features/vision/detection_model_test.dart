/// Vision Detection Model Unit Tests
/// اختبارات وحدات نماذج الكشف للرؤية
///
/// Tests Detection, DetectionResult, DetectionSession, PlantCountResult,
/// ModelInfo, BoundingBox, and all related enums.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/vision/domain/detection_model.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionType enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionType enum', () {
    test('should have all expected values', () {
      expect(DetectionType.values, hasLength(6));
      expect(DetectionType.values, containsAll([
        DetectionType.pest,
        DetectionType.disease,
        DetectionType.weed,
        DetectionType.plant,
        DetectionType.fruit,
        DetectionType.deficiency,
      ]));
    });

    test('should have correct English display names', () {
      expect(DetectionType.pest.displayName, 'Pest');
      expect(DetectionType.disease.displayName, 'Disease');
      expect(DetectionType.weed.displayName, 'Weed');
      expect(DetectionType.plant.displayName, 'Plant');
      expect(DetectionType.fruit.displayName, 'Fruit');
      expect(DetectionType.deficiency.displayName, 'Nutrient Deficiency');
    });

    test('should have correct Arabic display names', () {
      expect(DetectionType.pest.displayNameAr, 'آفة');
      expect(DetectionType.disease.displayNameAr, 'مرض');
      expect(DetectionType.weed.displayNameAr, 'حشائش');
      expect(DetectionType.plant.displayNameAr, 'نبات');
      expect(DetectionType.fruit.displayNameAr, 'ثمرة');
      expect(DetectionType.deficiency.displayNameAr, 'نقص عنصر غذائي');
    });

    test('should have icon for each type', () {
      for (final type in DetectionType.values) {
        expect(type.icon, isNotEmpty);
      }
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionSeverity enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionSeverity enum', () {
    test('should have all expected values', () {
      expect(DetectionSeverity.values, hasLength(4));
      expect(DetectionSeverity.values, containsAll([
        DetectionSeverity.low,
        DetectionSeverity.medium,
        DetectionSeverity.high,
        DetectionSeverity.critical,
      ]));
    });

    test('should have correct English display names', () {
      expect(DetectionSeverity.low.displayName, 'Low');
      expect(DetectionSeverity.medium.displayName, 'Medium');
      expect(DetectionSeverity.high.displayName, 'High');
      expect(DetectionSeverity.critical.displayName, 'Critical');
    });

    test('should have correct Arabic display names', () {
      expect(DetectionSeverity.low.displayNameAr, 'منخفض');
      expect(DetectionSeverity.medium.displayNameAr, 'متوسط');
      expect(DetectionSeverity.high.displayNameAr, 'مرتفع');
      expect(DetectionSeverity.critical.displayNameAr, 'حرج');
    });

    test('should have color hex for each severity', () {
      expect(DetectionSeverity.low.colorHex, '#22C55E');
      expect(DetectionSeverity.medium.colorHex, '#EAB308');
      expect(DetectionSeverity.high.colorHex, '#F97316');
      expect(DetectionSeverity.critical.colorHex, '#EF4444');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionSource enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionSource enum', () {
    test('should have all expected values', () {
      expect(DetectionSource.values, hasLength(3));
      expect(DetectionSource.values, containsAll([
        DetectionSource.onDevice,
        DetectionSource.cloud,
        DetectionSource.hybrid,
      ]));
    });

    test('should have correct English display names', () {
      expect(DetectionSource.onDevice.displayName, 'On-Device');
      expect(DetectionSource.cloud.displayName, 'Cloud');
      expect(DetectionSource.hybrid.displayName, 'Hybrid');
    });

    test('should have correct Arabic display names', () {
      expect(DetectionSource.onDevice.displayNameAr, 'على الجهاز');
      expect(DetectionSource.cloud.displayNameAr, 'سحابي');
      expect(DetectionSource.hybrid.displayNameAr, 'هجين');
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // BoundingBox model
  // ═══════════════════════════════════════════════════════════════════════════

  group('BoundingBox model', () {
    test('should create BoundingBox with all properties', () {
      const bbox = BoundingBox(
        x: 0.1,
        y: 0.2,
        width: 0.3,
        height: 0.4,
      );

      expect(bbox.x, 0.1);
      expect(bbox.y, 0.2);
      expect(bbox.width, 0.3);
      expect(bbox.height, 0.4);
    });

    test('should calculate centerX correctly', () {
      const bbox = BoundingBox(x: 0.2, y: 0.3, width: 0.4, height: 0.2);
      expect(bbox.centerX, closeTo(0.4, 0.001));
    });

    test('should calculate centerY correctly', () {
      const bbox = BoundingBox(x: 0.2, y: 0.3, width: 0.4, height: 0.2);
      expect(bbox.centerY, closeTo(0.4, 0.001));
    });

    test('should calculate area correctly', () {
      const bbox = BoundingBox(x: 0.0, y: 0.0, width: 0.5, height: 0.4);
      expect(bbox.area, closeTo(0.2, 0.001));
    });

    test('should convert to pixel coordinates', () {
      const bbox = BoundingBox(x: 0.1, y: 0.2, width: 0.3, height: 0.4);
      final pixels = bbox.toPixels(640, 480);

      expect(pixels['x'], 64);
      expect(pixels['y'], 96);
      expect(pixels['width'], 192);
      expect(pixels['height'], 192);
    });

    test('should serialize to JSON and back', () {
      const bbox = BoundingBox(x: 0.15, y: 0.25, width: 0.35, height: 0.45);
      final json = bbox.toJson();

      expect(json['x'], 0.15);
      expect(json['y'], 0.25);
      expect(json['width'], 0.35);
      expect(json['height'], 0.45);

      final restored = BoundingBox.fromJson(json);
      expect(restored, equals(bbox));
    });

    test('should have value equality', () {
      const bbox1 = BoundingBox(x: 0.1, y: 0.2, width: 0.3, height: 0.4);
      const bbox2 = BoundingBox(x: 0.1, y: 0.2, width: 0.3, height: 0.4);
      expect(bbox1, equals(bbox2));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Detection model
  // ═══════════════════════════════════════════════════════════════════════════

  group('Detection model', () {
    late Detection detection;

    setUp(() {
      detection = Detection(
        detectionId: 'det_001',
        className: 'Red Palm Weevil',
        classNameAr: 'سوسة النخيل الحمراء',
        detectionType: DetectionType.pest,
        confidence: 0.92,
        bbox: const BoundingBox(x: 0.1, y: 0.2, width: 0.3, height: 0.3),
        source: DetectionSource.onDevice,
        severity: DetectionSeverity.critical,
        scientificName: 'Rhynchophorus ferrugineus',
        metadata: const {'region': 'trunk'},
        timestamp: DateTime(2026, 2, 27),
      );
    });

    test('should create Detection with all properties', () {
      expect(detection.detectionId, 'det_001');
      expect(detection.className, 'Red Palm Weevil');
      expect(detection.classNameAr, 'سوسة النخيل الحمراء');
      expect(detection.detectionType, DetectionType.pest);
      expect(detection.confidence, 0.92);
      expect(detection.source, DetectionSource.onDevice);
      expect(detection.severity, DetectionSeverity.critical);
      expect(detection.scientificName, 'Rhynchophorus ferrugineus');
      expect(detection.metadata, {'region': 'trunk'});
    });

    test('should create Detection with minimal properties', () {
      const minimal = Detection(
        detectionId: 'det_minimal',
        className: 'Unknown Pest',
        classNameAr: 'آفة غير معروفة',
        detectionType: DetectionType.pest,
        confidence: 0.55,
        bbox: BoundingBox(x: 0.0, y: 0.0, width: 0.1, height: 0.1),
        source: DetectionSource.cloud,
      );

      expect(minimal.severity, isNull);
      expect(minimal.scientificName, isNull);
      expect(minimal.metadata, isEmpty);
      expect(minimal.timestamp, isNull);
    });

    test('should format confidence as percentage', () {
      expect(detection.confidencePercent, '92.0%');

      const lowConf = Detection(
        detectionId: 'det_low',
        className: 'Aphid',
        classNameAr: 'من',
        detectionType: DetectionType.pest,
        confidence: 0.333,
        bbox: BoundingBox(x: 0.0, y: 0.0, width: 0.1, height: 0.1),
        source: DetectionSource.cloud,
      );
      expect(lowConf.confidencePercent, '33.3%');
    });

    test('isHighConfidence should return true for confidence > 0.7', () {
      expect(detection.isHighConfidence, isTrue);

      const lowConf = Detection(
        detectionId: 'det_low',
        className: 'Aphid',
        classNameAr: 'من',
        detectionType: DetectionType.pest,
        confidence: 0.65,
        bbox: BoundingBox(x: 0.0, y: 0.0, width: 0.1, height: 0.1),
        source: DetectionSource.cloud,
      );
      expect(lowConf.isHighConfidence, isFalse);
    });

    test('isHighConfidence should return false for confidence exactly 0.7', () {
      const exactConf = Detection(
        detectionId: 'det_exact',
        className: 'Whitefly',
        classNameAr: 'ذبابة بيضاء',
        detectionType: DetectionType.pest,
        confidence: 0.7,
        bbox: BoundingBox(x: 0.0, y: 0.0, width: 0.1, height: 0.1),
        source: DetectionSource.onDevice,
      );
      expect(exactConf.isHighConfidence, isFalse);
    });

    test('should have correct displayLabel', () {
      expect(detection.displayLabel, 'Red Palm Weevil (92.0%)');
    });

    test('should have correct displayLabelAr', () {
      expect(detection.displayLabelAr, 'سوسة النخيل الحمراء (92.0%)');
    });

    test('should serialize to JSON and back', () {
      final json = detection.toJson();

      expect(json['detectionId'], 'det_001');
      expect(json['className'], 'Red Palm Weevil');
      expect(json['detectionType'], 'pest');
      expect(json['confidence'], 0.92);
      expect(json['source'], 'on_device');

      final restored = Detection.fromJson(json);
      expect(restored.detectionId, detection.detectionId);
      expect(restored.className, detection.className);
      expect(restored.confidence, detection.confidence);
      expect(restored.detectionType, detection.detectionType);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionResult model
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionResult model', () {
    late DetectionResult result;
    late List<Detection> detections;

    setUp(() {
      detections = [
        const Detection(
          detectionId: 'det_1',
          className: 'Aphid',
          classNameAr: 'من',
          detectionType: DetectionType.pest,
          confidence: 0.85,
          bbox: BoundingBox(x: 0.1, y: 0.1, width: 0.2, height: 0.2),
          source: DetectionSource.onDevice,
        ),
        const Detection(
          detectionId: 'det_2',
          className: 'Leaf Rust',
          classNameAr: 'صدأ الأوراق',
          detectionType: DetectionType.disease,
          confidence: 0.78,
          bbox: BoundingBox(x: 0.4, y: 0.3, width: 0.25, height: 0.25),
          source: DetectionSource.onDevice,
        ),
        const Detection(
          detectionId: 'det_3',
          className: 'Whitefly',
          classNameAr: 'ذبابة بيضاء',
          detectionType: DetectionType.pest,
          confidence: 0.65,
          bbox: BoundingBox(x: 0.6, y: 0.5, width: 0.15, height: 0.15),
          source: DetectionSource.onDevice,
        ),
        const Detection(
          detectionId: 'det_4',
          className: 'Wheat Seedling',
          classNameAr: 'شتلة قمح',
          detectionType: DetectionType.plant,
          confidence: 0.92,
          bbox: BoundingBox(x: 0.2, y: 0.6, width: 0.1, height: 0.2),
          source: DetectionSource.onDevice,
        ),
      ];

      result = DetectionResult(
        resultId: 'result_001',
        detections: detections,
        processingTimeMs: 120,
        imageWidth: 640,
        imageHeight: 480,
        source: DetectionSource.onDevice,
        modelVersion: '26.0',
        fieldId: 'field_001',
        imagePath: '/path/to/image.jpg',
        timestamp: DateTime(2026, 2, 27),
      );
    });

    test('should create DetectionResult with all properties', () {
      expect(result.resultId, 'result_001');
      expect(result.detections, hasLength(4));
      expect(result.processingTimeMs, 120);
      expect(result.imageWidth, 640);
      expect(result.imageHeight, 480);
      expect(result.source, DetectionSource.onDevice);
      expect(result.modelVersion, '26.0');
      expect(result.fieldId, 'field_001');
      expect(result.imagePath, '/path/to/image.jpg');
    });

    test('isSuccess should return true when no error', () {
      expect(result.isSuccess, isTrue);
    });

    test('isSuccess should return false when error present', () {
      const errorResult = DetectionResult(
        resultId: 'result_err',
        detections: [],
        processingTimeMs: 0,
        imageWidth: 640,
        imageHeight: 480,
        source: DetectionSource.onDevice,
        modelVersion: '26.0',
        error: 'Model inference failed',
      );

      expect(errorResult.isSuccess, isFalse);
    });

    test('totalDetections should return correct count', () {
      expect(result.totalDetections, 4);
    });

    test('countByType should return correct breakdown', () {
      final counts = result.countByType;

      expect(counts[DetectionType.pest], 2);
      expect(counts[DetectionType.disease], 1);
      expect(counts[DetectionType.plant], 1);
      expect(counts[DetectionType.weed], isNull);
    });

    test('getByType should filter detections by type', () {
      final pests = result.getByType(DetectionType.pest);
      expect(pests, hasLength(2));
      expect(pests.every((d) => d.detectionType == DetectionType.pest), isTrue);

      final diseases = result.getByType(DetectionType.disease);
      expect(diseases, hasLength(1));
      expect(diseases.first.className, 'Leaf Rust');

      final weeds = result.getByType(DetectionType.weed);
      expect(weeds, isEmpty);
    });

    test('pests getter should return only pest detections', () {
      expect(result.pests, hasLength(2));
      expect(result.pests.map((d) => d.className), containsAll(['Aphid', 'Whitefly']));
    });

    test('diseases getter should return only disease detections', () {
      expect(result.diseases, hasLength(1));
      expect(result.diseases.first.className, 'Leaf Rust');
    });

    test('plants getter should return only plant detections', () {
      expect(result.plants, hasLength(1));
      expect(result.plants.first.className, 'Wheat Seedling');
    });

    test('highConfidenceDetections should return only > 0.7 confidence', () {
      final highConf = result.highConfidenceDetections;
      expect(highConf, hasLength(3)); // 0.85, 0.78, 0.92 are > 0.7
      expect(highConf.every((d) => d.confidence > 0.7), isTrue);
    });

    test('should create result with empty detections', () {
      const empty = DetectionResult(
        resultId: 'result_empty',
        detections: [],
        processingTimeMs: 50,
        imageWidth: 640,
        imageHeight: 480,
        source: DetectionSource.onDevice,
        modelVersion: '26.0',
      );

      expect(empty.totalDetections, 0);
      expect(empty.countByType, isEmpty);
      expect(empty.pests, isEmpty);
      expect(empty.diseases, isEmpty);
      expect(empty.highConfidenceDetections, isEmpty);
    });

    test('should serialize to JSON and back', () {
      final json = result.toJson();

      expect(json['resultId'], 'result_001');
      expect(json['processingTimeMs'], 120);
      expect(json['imageWidth'], 640);
      expect(json['detections'], isList);
      expect(json['modelVersion'], '26.0');

      final restored = DetectionResult.fromJson(json);
      expect(restored.resultId, result.resultId);
      expect(restored.detections, hasLength(4));
      expect(restored.processingTimeMs, 120);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // DetectionSession model
  // ═══════════════════════════════════════════════════════════════════════════

  group('DetectionSession model', () {
    test('should create ongoing session', () {
      final session = DetectionSession(
        sessionId: 'session_001',
        fieldId: 'field_001',
        startTime: DateTime(2026, 2, 27, 10, 0, 0),
      );

      expect(session.sessionId, 'session_001');
      expect(session.fieldId, 'field_001');
      expect(session.endTime, isNull);
      expect(session.isOngoing, isTrue);
      expect(session.duration, isNull);
      expect(session.results, isEmpty);
      expect(session.imagesProcessed, 0);
      expect(session.totalDetections, 0);
    });

    test('should create completed session with duration', () {
      final session = DetectionSession(
        sessionId: 'session_002',
        fieldId: 'field_001',
        startTime: DateTime(2026, 2, 27, 10, 0, 0),
        endTime: DateTime(2026, 2, 27, 10, 30, 0),
        imagesProcessed: 15,
        totalDetections: 42,
      );

      expect(session.isOngoing, isFalse);
      expect(session.duration, equals(const Duration(minutes: 30)));
      expect(session.imagesProcessed, 15);
      expect(session.totalDetections, 42);
    });

    test('should track results and summarize by type', () {
      final session = DetectionSession(
        sessionId: 'session_003',
        startTime: DateTime(2026, 2, 27, 10, 0, 0),
        results: [
          const DetectionResult(
            resultId: 'r1',
            detections: [
              Detection(
                detectionId: 'd1',
                className: 'Aphid',
                classNameAr: 'من',
                detectionType: DetectionType.pest,
                confidence: 0.9,
                bbox: BoundingBox(x: 0.1, y: 0.1, width: 0.2, height: 0.2),
                source: DetectionSource.onDevice,
              ),
              Detection(
                detectionId: 'd2',
                className: 'Rust',
                classNameAr: 'صدأ',
                detectionType: DetectionType.disease,
                confidence: 0.8,
                bbox: BoundingBox(x: 0.3, y: 0.3, width: 0.2, height: 0.2),
                source: DetectionSource.onDevice,
              ),
            ],
            processingTimeMs: 100,
            imageWidth: 640,
            imageHeight: 480,
            source: DetectionSource.onDevice,
            modelVersion: '26.0',
          ),
          const DetectionResult(
            resultId: 'r2',
            detections: [
              Detection(
                detectionId: 'd3',
                className: 'Locust',
                classNameAr: 'جراد',
                detectionType: DetectionType.pest,
                confidence: 0.95,
                bbox: BoundingBox(x: 0.5, y: 0.5, width: 0.3, height: 0.3),
                source: DetectionSource.onDevice,
              ),
            ],
            processingTimeMs: 80,
            imageWidth: 640,
            imageHeight: 480,
            source: DetectionSource.onDevice,
            modelVersion: '26.0',
          ),
        ],
        imagesProcessed: 2,
        totalDetections: 3,
      );

      final summary = session.summaryByType;
      expect(summary[DetectionType.pest], 2);
      expect(summary[DetectionType.disease], 1);
      expect(summary.containsKey(DetectionType.weed), isFalse);
    });

    test('should support GPS coordinates', () {
      final session = DetectionSession(
        sessionId: 'session_gps',
        startTime: DateTime.now(),
        latitude: 15.3694,
        longitude: 44.1910,
        notes: 'Northeast corner of field',
      );

      expect(session.latitude, closeTo(15.3694, 0.0001));
      expect(session.longitude, closeTo(44.1910, 0.0001));
      expect(session.notes, 'Northeast corner of field');
    });

    test('should serialize to JSON and back', () {
      final session = DetectionSession(
        sessionId: 'session_json',
        fieldId: 'field_json',
        startTime: DateTime(2026, 2, 27, 10, 0, 0),
        endTime: DateTime(2026, 2, 27, 10, 15, 0),
        imagesProcessed: 5,
        totalDetections: 12,
        notes: 'Test session',
      );

      final json = session.toJson();
      expect(json['sessionId'], 'session_json');
      expect(json['fieldId'], 'field_json');
      expect(json['imagesProcessed'], 5);

      final restored = DetectionSession.fromJson(json);
      expect(restored.sessionId, session.sessionId);
      expect(restored.fieldId, session.fieldId);
      expect(restored.imagesProcessed, 5);
    });

    test('summaryByType should return empty map for empty session', () {
      final session = DetectionSession(
        sessionId: 'empty_session',
        startTime: DateTime.now(),
      );

      expect(session.summaryByType, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // PlantCountResult model
  // ═══════════════════════════════════════════════════════════════════════════

  group('PlantCountResult model', () {
    test('should create PlantCountResult with all properties', () {
      const result = PlantCountResult(
        totalCount: 150,
        plants: [],
        plantsPerHectare: 45000.0,
        imageAreaM2: 33.3,
        source: DetectionSource.onDevice,
        processingTimeMs: 250,
        averageConfidence: 0.87,
        fieldId: 'field_001',
      );

      expect(result.totalCount, 150);
      expect(result.plantsPerHectare, closeTo(45000.0, 0.1));
      expect(result.imageAreaM2, closeTo(33.3, 0.1));
      expect(result.source, DetectionSource.onDevice);
      expect(result.processingTimeMs, 250);
      expect(result.averageConfidence, closeTo(0.87, 0.01));
      expect(result.fieldId, 'field_001');
    });

    test('should create PlantCountResult with optional fields null', () {
      const result = PlantCountResult(
        totalCount: 0,
        plants: [],
        source: DetectionSource.cloud,
        processingTimeMs: 100,
      );

      expect(result.totalCount, 0);
      expect(result.plantsPerHectare, isNull);
      expect(result.imageAreaM2, isNull);
      expect(result.averageConfidence, isNull);
      expect(result.fieldId, isNull);
    });

    test('should contain plant detections', () {
      const plants = [
        Detection(
          detectionId: 'p1',
          className: 'Wheat Plant',
          classNameAr: 'نبتة قمح',
          detectionType: DetectionType.plant,
          confidence: 0.88,
          bbox: BoundingBox(x: 0.1, y: 0.1, width: 0.05, height: 0.08),
          source: DetectionSource.onDevice,
        ),
        Detection(
          detectionId: 'p2',
          className: 'Wheat Plant',
          classNameAr: 'نبتة قمح',
          detectionType: DetectionType.plant,
          confidence: 0.91,
          bbox: BoundingBox(x: 0.3, y: 0.2, width: 0.05, height: 0.08),
          source: DetectionSource.onDevice,
        ),
      ];

      const result = PlantCountResult(
        totalCount: 2,
        plants: plants,
        source: DetectionSource.onDevice,
        processingTimeMs: 150,
        averageConfidence: 0.895,
      );

      expect(result.plants, hasLength(2));
      expect(result.totalCount, 2);
    });

    test('should serialize to JSON and back', () {
      const result = PlantCountResult(
        totalCount: 10,
        plants: [],
        plantsPerHectare: 30000.0,
        imageAreaM2: 3.33,
        source: DetectionSource.onDevice,
        processingTimeMs: 200,
        averageConfidence: 0.85,
      );

      final json = result.toJson();
      expect(json['totalCount'], 10);
      expect(json['plantsPerHectare'], 30000.0);

      final restored = PlantCountResult.fromJson(json);
      expect(restored.totalCount, 10);
      expect(restored.plantsPerHectare, closeTo(30000.0, 0.1));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ModelInfo model
  // ═══════════════════════════════════════════════════════════════════════════

  group('ModelInfo model', () {
    test('should create ModelInfo with all properties', () {
      const info = ModelInfo(
        name: 'yolo26-pest-v1',
        version: '26.0',
        inputSize: 640,
        numClasses: 22,
        labels: ['aphid', 'whitefly', 'locust'],
        labelsAr: ['من', 'ذبابة بيضاء', 'جراد'],
        fileSizeBytes: 49000000,
        isQuantized: true,
        supportedTypes: [DetectionType.pest],
      );

      expect(info.name, 'yolo26-pest-v1');
      expect(info.version, '26.0');
      expect(info.inputSize, 640);
      expect(info.numClasses, 22);
      expect(info.labels, hasLength(3));
      expect(info.labelsAr, hasLength(3));
      expect(info.fileSizeBytes, 49000000);
      expect(info.isQuantized, isTrue);
      expect(info.supportedTypes, [DetectionType.pest]);
    });

    test('should have default isQuantized as true', () {
      const info = ModelInfo(
        name: 'yolo26-disease-v1',
        version: '26.0',
        inputSize: 640,
        numClasses: 34,
        labels: [],
        labelsAr: [],
      );

      expect(info.isQuantized, isTrue);
      expect(info.fileSizeBytes, isNull);
      expect(info.supportedTypes, isEmpty);
    });

    test('should serialize to JSON and back', () {
      const info = ModelInfo(
        name: 'yolo26-plant-v1',
        version: '26.0',
        inputSize: 320,
        numClasses: 1,
        labels: ['plant'],
        labelsAr: ['نبات'],
        isQuantized: false,
      );

      final json = info.toJson();
      expect(json['name'], 'yolo26-plant-v1');
      expect(json['inputSize'], 320);
      expect(json['numClasses'], 1);

      final restored = ModelInfo.fromJson(json);
      expect(restored.name, info.name);
      expect(restored.numClasses, 1);
    });
  });
}
