/// TFLite Helper - مساعد TFLite
///
/// TensorFlow Lite interpreter wrapper for on-device ML inference.
/// Provides image preprocessing, model loading, and post-processing utilities.
library;

import 'dart:async';
import 'dart:io';
import 'dart:isolate';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:flutter/services.dart';
import 'package:path_provider/path_provider.dart';

import '../../features/vision/domain/detection_model.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// TFLite Configuration - إعدادات TFLite
// ═══════════════════════════════════════════════════════════════════════════════

/// Configuration for TFLite model
/// إعدادات نموذج TFLite
class TFLiteConfig {
  /// Model asset path (e.g., 'assets/models/yolo26_pests.tflite')
  final String modelAssetPath;

  /// Labels asset path (e.g., 'assets/models/labels_pests.txt')
  final String labelsAssetPath;

  /// Arabic labels asset path
  final String labelsArAssetPath;

  /// Input image size (model expects square input)
  final int inputSize;

  /// Number of threads for inference
  final int numThreads;

  /// Use GPU delegate if available
  final bool useGpu;

  /// Use NNAPI delegate on Android
  final bool useNnapi;

  /// Confidence threshold for detections
  final double confidenceThreshold;

  /// Non-maximum suppression IoU threshold
  final double nmsIoUThreshold;

  /// Maximum number of detections to return
  final int maxDetections;

  const TFLiteConfig({
    required this.modelAssetPath,
    required this.labelsAssetPath,
    required this.labelsArAssetPath,
    this.inputSize = 640,
    this.numThreads = 4,
    this.useGpu = false,
    this.useNnapi = false,
    this.confidenceThreshold = 0.5,
    this.nmsIoUThreshold = 0.45,
    this.maxDetections = 100,
  });

  /// Default config for pest detection
  static const pestDetection = TFLiteConfig(
    modelAssetPath: 'assets/models/yolo26_pests.tflite',
    labelsAssetPath: 'assets/models/labels_pests.txt',
    labelsArAssetPath: 'assets/models/labels_pests_ar.txt',
    inputSize: 640,
    confidenceThreshold: 0.5,
  );

  /// Default config for disease detection
  static const diseaseDetection = TFLiteConfig(
    modelAssetPath: 'assets/models/yolo26_diseases.tflite',
    labelsAssetPath: 'assets/models/labels_diseases.txt',
    labelsArAssetPath: 'assets/models/labels_diseases_ar.txt',
    inputSize: 640,
    confidenceThreshold: 0.5,
  );

  /// Default config for plant counting
  static const plantCounting = TFLiteConfig(
    modelAssetPath: 'assets/models/yolo26_plants.tflite',
    labelsAssetPath: 'assets/models/labels_plants.txt',
    labelsArAssetPath: 'assets/models/labels_plants_ar.txt',
    inputSize: 640,
    confidenceThreshold: 0.4,
    maxDetections: 500,
  );
}

// ═══════════════════════════════════════════════════════════════════════════════
// Preprocessing Result - نتيجة المعالجة المسبقة
// ═══════════════════════════════════════════════════════════════════════════════

/// Result of image preprocessing
/// نتيجة المعالجة المسبقة للصورة
class PreprocessedImage {
  /// Normalized float tensor for model input
  final Float32List inputTensor;

  /// Original image width
  final int originalWidth;

  /// Original image height
  final int originalHeight;

  /// Scale factor X (for converting back to original coords)
  final double scaleX;

  /// Scale factor Y
  final double scaleY;

  /// Padding left (letterbox padding)
  final int padLeft;

  /// Padding top
  final int padTop;

  PreprocessedImage({
    required this.inputTensor,
    required this.originalWidth,
    required this.originalHeight,
    required this.scaleX,
    required this.scaleY,
    required this.padLeft,
    required this.padTop,
  });
}

// ═══════════════════════════════════════════════════════════════════════════════
// TFLite Helper Class - صف مساعد TFLite
// ═══════════════════════════════════════════════════════════════════════════════

/// TensorFlow Lite interpreter helper
/// مساعد مترجم TensorFlow Lite
class TFLiteHelper {
  final TFLiteConfig config;

  // Model state
  bool _isInitialized = false;
  String? _modelPath;
  List<String> _labels = [];
  List<String> _labelsAr = [];
  ModelInfo? _modelInfo;

  // Isolate for background processing
  Isolate? _inferenceIsolate;
  SendPort? _isolateSendPort;

  TFLiteHelper(this.config);

  /// Check if model is initialized
  bool get isInitialized => _isInitialized;

  /// Get model info
  ModelInfo? get modelInfo => _modelInfo;

  /// Get labels
  List<String> get labels => _labels;

  /// Get Arabic labels
  List<String> get labelsAr => _labelsAr;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization - التهيئة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the TFLite interpreter
  /// تهيئة مترجم TFLite
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Copy model from assets to local storage for faster access
      _modelPath = await _copyAssetToLocal(config.modelAssetPath);

      // Load labels
      _labels = await _loadLabels(config.labelsAssetPath);
      _labelsAr = await _loadLabels(config.labelsArAssetPath);

      // Build model info
      final modelFile = File(_modelPath!);
      _modelInfo = ModelInfo(
        name: _extractModelName(config.modelAssetPath),
        version: '26.0', // YOLO26
        inputSize: config.inputSize,
        numClasses: _labels.length,
        labels: _labels,
        labelsAr: _labelsAr,
        fileSizeBytes: await modelFile.length(),
        isQuantized: true,
        supportedTypes: _inferSupportedTypes(config.modelAssetPath),
      );

      _isInitialized = true;
    } catch (e) {
      throw TFLiteException(
        'Failed to initialize TFLite model',
        'فشل في تهيئة نموذج TFLite',
        cause: e,
      );
    }
  }

  /// Copy asset file to local storage
  Future<String> _copyAssetToLocal(String assetPath) async {
    final appDir = await getApplicationDocumentsDirectory();
    final fileName = assetPath.split('/').last;
    final localPath = '${appDir.path}/models/$fileName';
    final localFile = File(localPath);

    // Create directory if needed
    await localFile.parent.create(recursive: true);

    // Copy if not exists or outdated
    if (!await localFile.exists()) {
      final data = await rootBundle.load(assetPath);
      await localFile.writeAsBytes(data.buffer.asUint8List());
    }

    return localPath;
  }

  /// Load labels from asset
  Future<List<String>> _loadLabels(String assetPath) async {
    try {
      final content = await rootBundle.loadString(assetPath);
      return content
          .split('\n')
          .map((line) => line.trim())
          .where((line) => line.isNotEmpty)
          .toList();
    } catch (e) {
      // Return empty list if labels file not found
      return [];
    }
  }

  /// Extract model name from path
  String _extractModelName(String path) {
    final fileName = path.split('/').last;
    return fileName.replaceAll('.tflite', '');
  }

  /// Infer supported detection types from model name
  List<DetectionType> _inferSupportedTypes(String path) {
    final types = <DetectionType>[];
    final name = path.toLowerCase();

    if (name.contains('pest')) types.add(DetectionType.pest);
    if (name.contains('disease')) types.add(DetectionType.disease);
    if (name.contains('weed')) types.add(DetectionType.weed);
    if (name.contains('plant')) types.add(DetectionType.plant);
    if (name.contains('fruit')) types.add(DetectionType.fruit);
    if (name.contains('deficiency')) types.add(DetectionType.deficiency);

    return types.isEmpty ? [DetectionType.pest] : types;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Image Preprocessing - المعالجة المسبقة للصورة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Preprocess image for model input
  /// المعالجة المسبقة للصورة لإدخال النموذج
  Future<PreprocessedImage> preprocessImage(Uint8List imageBytes) async {
    // Decode image
    final codec = await ui.instantiateImageCodec(imageBytes);
    final frame = await codec.getNextFrame();
    final image = frame.image;

    final originalWidth = image.width;
    final originalHeight = image.height;

    // Calculate letterbox dimensions
    final scale = _calculateScale(originalWidth, originalHeight);
    final newWidth = (originalWidth * scale).round();
    final newHeight = (originalHeight * scale).round();
    final padLeft = (config.inputSize - newWidth) ~/ 2;
    final padTop = (config.inputSize - newHeight) ~/ 2;

    // Get image bytes
    final byteData = await image.toByteData(format: ui.ImageByteFormat.rawRgba);
    if (byteData == null) {
      throw TFLiteException(
        'Failed to get image bytes',
        'فشل في الحصول على بايتات الصورة',
      );
    }

    // Create input tensor with letterbox padding
    final inputTensor = Float32List(config.inputSize * config.inputSize * 3);

    // Fill with padding value (gray = 114/255)
    const padValue = 114.0 / 255.0;
    inputTensor.fillRange(0, inputTensor.length, padValue);

    // Copy and normalize image pixels
    final pixels = byteData.buffer.asUint8List();
    for (int y = 0; y < newHeight && y < config.inputSize - padTop; y++) {
      for (int x = 0; x < newWidth && x < config.inputSize - padLeft; x++) {
        // Source pixel (with scaling)
        final srcX = (x / scale).round().clamp(0, originalWidth - 1);
        final srcY = (y / scale).round().clamp(0, originalHeight - 1);
        final srcIdx = (srcY * originalWidth + srcX) * 4;

        // Destination position (with padding)
        final dstX = padLeft + x;
        final dstY = padTop + y;
        final dstIdx = (dstY * config.inputSize + dstX) * 3;

        // Normalize to 0-1 range
        inputTensor[dstIdx] = pixels[srcIdx] / 255.0; // R
        inputTensor[dstIdx + 1] = pixels[srcIdx + 1] / 255.0; // G
        inputTensor[dstIdx + 2] = pixels[srcIdx + 2] / 255.0; // B
      }
    }

    return PreprocessedImage(
      inputTensor: inputTensor,
      originalWidth: originalWidth,
      originalHeight: originalHeight,
      scaleX: scale,
      scaleY: scale,
      padLeft: padLeft,
      padTop: padTop,
    );
  }

  /// Calculate scale factor for letterbox resizing
  double _calculateScale(int width, int height) {
    return (config.inputSize / width).clamp(0.0, config.inputSize / height);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Post-processing - المعالجة اللاحقة
  // ═══════════════════════════════════════════════════════════════════════════

  /// Post-process model output to detections
  /// المعالجة اللاحقة لمخرجات النموذج إلى كشوفات
  List<Detection> postprocess(
    List<List<double>> rawOutput,
    PreprocessedImage preprocessed,
    DetectionSource source,
  ) {
    final detections = <Detection>[];

    // Parse raw output (format: [x_center, y_center, width, height, confidence, ...class_scores])
    for (final row in rawOutput) {
      if (row.length < 5 + _labels.length) continue;

      final confidence = row[4];
      if (confidence < config.confidenceThreshold) continue;

      // Find class with highest score
      int maxClassIdx = 0;
      double maxClassScore = 0.0;
      for (int i = 0; i < _labels.length; i++) {
        final score = row[5 + i] * confidence;
        if (score > maxClassScore) {
          maxClassScore = score;
          maxClassIdx = i;
        }
      }

      if (maxClassScore < config.confidenceThreshold) continue;

      // Convert to normalized coordinates
      final xCenter = row[0] / config.inputSize;
      final yCenter = row[1] / config.inputSize;
      final width = row[2] / config.inputSize;
      final height = row[3] / config.inputSize;

      // Remove letterbox padding effect
      final x = (xCenter - preprocessed.padLeft / config.inputSize) /
          preprocessed.scaleX;
      final y = (yCenter - preprocessed.padTop / config.inputSize) /
          preprocessed.scaleY;
      final w = width / preprocessed.scaleX;
      final h = height / preprocessed.scaleY;

      // Create detection
      detections.add(Detection(
        detectionId: _generateDetectionId(),
        className: _labels[maxClassIdx],
        classNameAr: maxClassIdx < _labelsAr.length
            ? _labelsAr[maxClassIdx]
            : _labels[maxClassIdx],
        detectionType: _inferDetectionType(_labels[maxClassIdx]),
        confidence: maxClassScore,
        bbox: BoundingBox(
          x: (x - w / 2).clamp(0.0, 1.0),
          y: (y - h / 2).clamp(0.0, 1.0),
          width: w.clamp(0.0, 1.0),
          height: h.clamp(0.0, 1.0),
        ),
        source: source,
        severity: _inferSeverity(maxClassScore),
        timestamp: DateTime.now(),
      ));
    }

    // Apply NMS
    return _applyNms(detections);
  }

  /// Apply Non-Maximum Suppression
  List<Detection> _applyNms(List<Detection> detections) {
    if (detections.isEmpty) return detections;

    // Sort by confidence (descending)
    final sorted = List<Detection>.from(detections)
      ..sort((a, b) => b.confidence.compareTo(a.confidence));

    final results = <Detection>[];
    final suppressed = List<bool>.filled(sorted.length, false);

    for (int i = 0; i < sorted.length; i++) {
      if (suppressed[i]) continue;

      results.add(sorted[i]);
      if (results.length >= config.maxDetections) break;

      for (int j = i + 1; j < sorted.length; j++) {
        if (suppressed[j]) continue;

        final iou = _calculateIoU(sorted[i].bbox, sorted[j].bbox);
        if (iou > config.nmsIoUThreshold) {
          suppressed[j] = true;
        }
      }
    }

    return results;
  }

  /// Calculate Intersection over Union
  double _calculateIoU(BoundingBox a, BoundingBox b) {
    final xA = (a.x > b.x) ? a.x : b.x;
    final yA = (a.y > b.y) ? a.y : b.y;
    final xB =
        ((a.x + a.width) < (b.x + b.width)) ? (a.x + a.width) : (b.x + b.width);
    final yB = ((a.y + a.height) < (b.y + b.height))
        ? (a.y + a.height)
        : (b.y + b.height);

    final intersectionArea =
        ((xB - xA) > 0 && (yB - yA) > 0) ? (xB - xA) * (yB - yA) : 0.0;
    final aArea = a.width * a.height;
    final bArea = b.width * b.height;
    final unionArea = aArea + bArea - intersectionArea;

    return unionArea > 0 ? intersectionArea / unionArea : 0.0;
  }

  /// Generate unique detection ID
  String _generateDetectionId() {
    return 'det_${DateTime.now().millisecondsSinceEpoch}_${_labels.hashCode}';
  }

  /// Infer detection type from class name
  DetectionType _inferDetectionType(String className) {
    final lower = className.toLowerCase();

    if (lower.contains('disease') ||
        lower.contains('blight') ||
        lower.contains('rust') ||
        lower.contains('mildew') ||
        lower.contains('rot') ||
        lower.contains('spot')) {
      return DetectionType.disease;
    }

    if (lower.contains('weed') || lower.contains('grass')) {
      return DetectionType.weed;
    }

    if (lower.contains('plant') ||
        lower.contains('seedling') ||
        lower.contains('crop')) {
      return DetectionType.plant;
    }

    if (lower.contains('fruit') ||
        lower.contains('berry') ||
        lower.contains('tomato')) {
      return DetectionType.fruit;
    }

    if (lower.contains('deficiency') || lower.contains('chlorosis')) {
      return DetectionType.deficiency;
    }

    // Default to pest
    return DetectionType.pest;
  }

  /// Infer severity from confidence
  DetectionSeverity? _inferSeverity(double confidence) {
    if (confidence > 0.9) return DetectionSeverity.critical;
    if (confidence > 0.75) return DetectionSeverity.high;
    if (confidence > 0.6) return DetectionSeverity.medium;
    return DetectionSeverity.low;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cleanup - التنظيف
  // ═══════════════════════════════════════════════════════════════════════════

  /// Dispose resources
  Future<void> dispose() async {
    _inferenceIsolate?.kill(priority: Isolate.immediate);
    _inferenceIsolate = null;
    _isolateSendPort = null;
    _isInitialized = false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Exception - استثناء
// ═══════════════════════════════════════════════════════════════════════════════

/// TFLite exception
/// استثناء TFLite
class TFLiteException implements Exception {
  final String message;
  final String messageAr;
  final Object? cause;

  TFLiteException(this.message, this.messageAr, {this.cause});

  @override
  String toString() =>
      'TFLiteException: $message${cause != null ? ' ($cause)' : ''}';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Image Utilities - أدوات الصورة
// ═══════════════════════════════════════════════════════════════════════════════

/// Image utility functions for ML preprocessing
/// دوال أدوات الصورة للمعالجة المسبقة للتعلم الآلي
class ImageUtils {
  /// Convert image file to bytes
  static Future<Uint8List> fileToBytes(File file) async {
    return file.readAsBytes();
  }

  /// Resize image maintaining aspect ratio
  static Future<Uint8List> resizeImage(
    Uint8List imageBytes,
    int maxSize,
  ) async {
    final codec = await ui.instantiateImageCodec(
      imageBytes,
      targetWidth: maxSize,
    );
    final frame = await codec.getNextFrame();
    final byteData =
        await frame.image.toByteData(format: ui.ImageByteFormat.png);
    return byteData!.buffer.asUint8List();
  }

  /// Rotate image if needed (based on EXIF)
  static Future<Uint8List> autoRotate(Uint8List imageBytes) async {
    // In a full implementation, this would read EXIF data and rotate accordingly
    // For now, return as-is
    return imageBytes;
  }

  /// Convert camera image to RGB bytes
  static Uint8List yuv420ToRgb(
    Uint8List yPlane,
    Uint8List uPlane,
    Uint8List vPlane,
    int width,
    int height,
    int yRowStride,
    int uvRowStride,
    int uvPixelStride,
  ) {
    final rgb = Uint8List(width * height * 3);

    for (int y = 0; y < height; y++) {
      for (int x = 0; x < width; x++) {
        final yIdx = y * yRowStride + x;
        final uvIdx = (y ~/ 2) * uvRowStride + (x ~/ 2) * uvPixelStride;

        final yVal = yPlane[yIdx];
        final uVal = uPlane[uvIdx];
        final vVal = vPlane[uvIdx];

        // YUV to RGB conversion
        final r = (yVal + 1.402 * (vVal - 128)).clamp(0, 255).toInt();
        final g = (yVal - 0.344 * (uVal - 128) - 0.714 * (vVal - 128))
            .clamp(0, 255)
            .toInt();
        final b = (yVal + 1.772 * (uVal - 128)).clamp(0, 255).toInt();

        final rgbIdx = (y * width + x) * 3;
        rgb[rgbIdx] = r;
        rgb[rgbIdx + 1] = g;
        rgb[rgbIdx + 2] = b;
      }
    }

    return rgb;
  }
}
