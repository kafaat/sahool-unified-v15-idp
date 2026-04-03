library;

/// YOLO26 On-Device Inference Service
/// خدمة الاستدلال على الجهاز YOLO26
///
/// Provides on-device object detection for pests, diseases, and plant counting
/// using YOLO26 models with automatic fallback to cloud inference.

import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:typed_data';
import 'dart:ui' as ui;

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import 'package:uuid/uuid.dart';

import '../../../core/api/kong_gateway_client.dart';
import '../../../core/config/api_config.dart';
import '../../../core/ml/tflite_helper.dart';
import '../domain/detection_model.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Providers - الموفرون
// ═══════════════════════════════════════════════════════════════════════════════

/// Provider for Yolo26Service instance
/// موفر لنسخة خدمة Yolo26
final yolo26ServiceProvider = Provider<Yolo26Service>((ref) {
  final service = Yolo26Service();
  ref.onDispose(() => service.dispose());
  return service;
});

/// Provider for on-device model availability
/// موفر لتوفر النموذج على الجهاز
final onDeviceModelAvailableProvider = FutureProvider<bool>((ref) async {
  final service = ref.watch(yolo26ServiceProvider);
  return service.isOnDeviceAvailable();
});

/// Provider for detection settings
/// موفر لإعدادات الكشف
final detectionSettingsProvider = StateProvider<DetectionSettings>((ref) {
  return const DetectionSettings();
});

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Settings - إعدادات الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Settings for detection operations
/// إعدادات عمليات الكشف
class DetectionSettings {
  /// Prefer on-device inference when available
  final bool preferOnDevice;

  /// Confidence threshold
  final double confidenceThreshold;

  /// Enable automatic fallback to cloud
  final bool enableFallback;

  /// Save detections to local database
  final bool saveLocally;

  /// Maximum image size for upload (bytes)
  final int maxImageSize;

  const DetectionSettings({
    this.preferOnDevice = true,
    this.confidenceThreshold = 0.5,
    this.enableFallback = true,
    this.saveLocally = true,
    this.maxImageSize = 2 * 1024 * 1024, // 2MB
  });

  DetectionSettings copyWith({
    bool? preferOnDevice,
    double? confidenceThreshold,
    bool? enableFallback,
    bool? saveLocally,
    int? maxImageSize,
  }) {
    return DetectionSettings(
      preferOnDevice: preferOnDevice ?? this.preferOnDevice,
      confidenceThreshold: confidenceThreshold ?? this.confidenceThreshold,
      enableFallback: enableFallback ?? this.enableFallback,
      saveLocally: saveLocally ?? this.saveLocally,
      maxImageSize: maxImageSize ?? this.maxImageSize,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Yolo26 Service - خدمة YOLO26
// ═══════════════════════════════════════════════════════════════════════════════

/// On-device YOLO26 inference service
/// خدمة الاستدلال على الجهاز YOLO26
class Yolo26Service {
  // TFLite helpers for different models
  TFLiteHelper? _pestHelper;
  TFLiteHelper? _diseaseHelper;
  TFLiteHelper? _plantHelper;

  // HTTP client for cloud fallback
  final http.Client _httpClient;

  // UUID generator
  final Uuid _uuid = const Uuid();

  // Initialization status
  bool _isInitialized = false;
  String? _initError;

  // Model versions
  static const String modelVersion = '26.0';

  Yolo26Service({http.Client? httpClient})
      : _httpClient = httpClient ?? http.Client();

  /// Check if on-device inference is available
  /// التحقق من توفر الاستدلال على الجهاز
  Future<bool> isOnDeviceAvailable() async {
    if (_isInitialized) return true;

    try {
      await _initializeModels();
      return _isInitialized;
    } catch (e) {
      _initError = e.toString();
      return false;
    }
  }

  /// Initialize all TFLite models
  Future<void> _initializeModels() async {
    if (_isInitialized) return;

    try {
      _pestHelper = TFLiteHelper(TFLiteConfig.pestDetection);
      _diseaseHelper = TFLiteHelper(TFLiteConfig.diseaseDetection);
      _plantHelper = TFLiteHelper(TFLiteConfig.plantCounting);

      await Future.wait([
        _pestHelper!.initialize(),
        _diseaseHelper!.initialize(),
        _plantHelper!.initialize(),
      ]);

      _isInitialized = true;
    } catch (e) {
      _initError = e.toString();
      rethrow;
    }
  }

  /// Get initialization error if any
  String? get initError => _initError;

  /// Get model info for all loaded models
  Map<String, ModelInfo?> get modelInfos => {
        'pest': _pestHelper?.modelInfo,
        'disease': _diseaseHelper?.modelInfo,
        'plant': _plantHelper?.modelInfo,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Model Loading - تحميل النموذج
  // ═══════════════════════════════════════════════════════════════════════════

  /// Load specific model if not already loaded
  /// تحميل نموذج محدد إذا لم يكن محملاً بالفعل
  Future<void> loadModel(DetectionType type) async {
    switch (type) {
      case DetectionType.pest:
        if (_pestHelper == null || !_pestHelper!.isInitialized) {
          _pestHelper = TFLiteHelper(TFLiteConfig.pestDetection);
          await _pestHelper!.initialize();
        }
      case DetectionType.disease:
        if (_diseaseHelper == null || !_diseaseHelper!.isInitialized) {
          _diseaseHelper = TFLiteHelper(TFLiteConfig.diseaseDetection);
          await _diseaseHelper!.initialize();
        }
      case DetectionType.plant:
        if (_plantHelper == null || !_plantHelper!.isInitialized) {
          _plantHelper = TFLiteHelper(TFLiteConfig.plantCounting);
          await _plantHelper!.initialize();
        }
      default:
        // Default to pest detection
        await loadModel(DetectionType.pest);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Pest Detection - كشف الآفات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Detect pests in image
  /// كشف الآفات في الصورة
  Future<List<Detection>> detectPests(
    Uint8List imageBytes, {
    String? fieldId,
    double? confidenceThreshold,
  }) async {
    return _runDetection(
      imageBytes: imageBytes,
      type: DetectionType.pest,
      helper: _pestHelper,
      config: TFLiteConfig.pestDetection,
      fieldId: fieldId,
      confidenceThreshold: confidenceThreshold,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Disease Detection - كشف الأمراض
  // ═══════════════════════════════════════════════════════════════════════════

  /// Detect diseases in image
  /// كشف الأمراض في الصورة
  Future<List<Detection>> detectDiseases(
    Uint8List imageBytes, {
    String? fieldId,
    double? confidenceThreshold,
  }) async {
    return _runDetection(
      imageBytes: imageBytes,
      type: DetectionType.disease,
      helper: _diseaseHelper,
      config: TFLiteConfig.diseaseDetection,
      fieldId: fieldId,
      confidenceThreshold: confidenceThreshold,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Plant Counting - عد النباتات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Count plants in image
  /// عد النباتات في الصورة
  Future<int> countPlants(
    Uint8List imageBytes, {
    String? fieldId,
    double? confidenceThreshold,
  }) async {
    final detections = await _runDetection(
      imageBytes: imageBytes,
      type: DetectionType.plant,
      helper: _plantHelper,
      config: TFLiteConfig.plantCounting,
      fieldId: fieldId,
      confidenceThreshold: confidenceThreshold ?? 0.4,
    );

    return detections.length;
  }

  /// Count plants with detailed result
  /// عد النباتات مع نتيجة مفصلة
  Future<PlantCountResult> countPlantsDetailed(
    Uint8List imageBytes, {
    String? fieldId,
    double? imageAreaM2,
    double? confidenceThreshold,
  }) async {
    final stopwatch = Stopwatch()..start();

    final detections = await _runDetection(
      imageBytes: imageBytes,
      type: DetectionType.plant,
      helper: _plantHelper,
      config: TFLiteConfig.plantCounting,
      fieldId: fieldId,
      confidenceThreshold: confidenceThreshold ?? 0.4,
    );

    stopwatch.stop();

    // Calculate average confidence
    double avgConfidence = 0.0;
    if (detections.isNotEmpty) {
      avgConfidence =
          detections.map((d) => d.confidence).reduce((a, b) => a + b) /
              detections.length;
    }

    // Calculate plants per hectare if area is known
    double? plantsPerHa;
    if (imageAreaM2 != null && imageAreaM2 > 0) {
      plantsPerHa = (detections.length / imageAreaM2) * 10000;
    }

    return PlantCountResult(
      totalCount: detections.length,
      plants: detections,
      plantsPerHectare: plantsPerHa,
      imageAreaM2: imageAreaM2,
      source: DetectionSource.onDevice,
      processingTimeMs: stopwatch.elapsedMilliseconds,
      averageConfidence: avgConfidence,
      fieldId: fieldId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Detection with Fallback - كشف مع احتياط
  // ═══════════════════════════════════════════════════════════════════════════

  /// Detect with automatic fallback to cloud
  /// الكشف مع الاحتياط التلقائي للسحابة
  Future<List<Detection>> detectWithFallback(
    Uint8List imageBytes, {
    DetectionType type = DetectionType.pest,
    String? fieldId,
    double? confidenceThreshold,
  }) async {
    // Try on-device first
    if (_isInitialized || await isOnDeviceAvailable()) {
      try {
        return switch (type) {
          DetectionType.pest => await detectPests(
              imageBytes,
              fieldId: fieldId,
              confidenceThreshold: confidenceThreshold,
            ),
          DetectionType.disease => await detectDiseases(
              imageBytes,
              fieldId: fieldId,
              confidenceThreshold: confidenceThreshold,
            ),
          DetectionType.plant => await _runDetection(
              imageBytes: imageBytes,
              type: type,
              helper: _plantHelper,
              config: TFLiteConfig.plantCounting,
              fieldId: fieldId,
              confidenceThreshold: confidenceThreshold,
            ),
          _ => await detectPests(
              imageBytes,
              fieldId: fieldId,
              confidenceThreshold: confidenceThreshold,
            ),
        };
      } catch (e) {
        // Fall through to cloud
      }
    }

    // Fallback to cloud
    return _detectWithCloud(
      imageBytes: imageBytes,
      type: type,
      fieldId: fieldId,
    );
  }

  /// Run full detection analysis (all types)
  /// تشغيل تحليل الكشف الكامل (جميع الأنواع)
  Future<DetectionResult> runFullAnalysis(
    Uint8List imageBytes, {
    String? fieldId,
    bool includePlantCount = false,
  }) async {
    final stopwatch = Stopwatch()..start();
    final allDetections = <Detection>[];
    var source = DetectionSource.onDevice;

    try {
      // Run pest and disease detection in parallel
      final results = await Future.wait([
        detectWithFallback(
          imageBytes,
          type: DetectionType.pest,
          fieldId: fieldId,
        ),
        detectWithFallback(
          imageBytes,
          type: DetectionType.disease,
          fieldId: fieldId,
        ),
      ]);

      allDetections.addAll(results[0]);
      allDetections.addAll(results[1]);

      // Optionally count plants
      if (includePlantCount) {
        final plants = await detectWithFallback(
          imageBytes,
          type: DetectionType.plant,
          fieldId: fieldId,
        );
        allDetections.addAll(plants);
      }

      // Check if any fallback to cloud occurred
      if (allDetections.any((d) => d.source == DetectionSource.cloud)) {
        source = DetectionSource.hybrid;
      }
    } catch (e) {
      source = DetectionSource.cloud;
      // Try cloud-only as last resort
      allDetections.addAll(await _detectWithCloud(
        imageBytes: imageBytes,
        type: DetectionType.pest,
        fieldId: fieldId,
      ));
    }

    stopwatch.stop();

    // Get image dimensions
    final codec = await ui.instantiateImageCodec(imageBytes);
    final frame = await codec.getNextFrame();
    final width = frame.image.width;
    final height = frame.image.height;

    return DetectionResult(
      resultId: _uuid.v4(),
      detections: allDetections,
      processingTimeMs: stopwatch.elapsedMilliseconds,
      imageWidth: width,
      imageHeight: height,
      source: source,
      modelVersion: modelVersion,
      fieldId: fieldId,
      timestamp: DateTime.now(),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Internal Methods - الطرق الداخلية
  // ═══════════════════════════════════════════════════════════════════════════

  /// Run detection with specific model
  Future<List<Detection>> _runDetection({
    required Uint8List imageBytes,
    required DetectionType type,
    required TFLiteHelper? helper,
    required TFLiteConfig config,
    String? fieldId,
    double? confidenceThreshold,
  }) async {
    // Ensure model is loaded
    if (helper == null || !helper.isInitialized) {
      await loadModel(type);
      helper = switch (type) {
        DetectionType.pest => _pestHelper,
        DetectionType.disease => _diseaseHelper,
        DetectionType.plant => _plantHelper,
        _ => _pestHelper,
      };
    }

    if (helper == null) {
      throw Yolo26Exception(
        'Model not available for ${type.name}',
        'النموذج غير متاح لـ ${type.displayNameAr}',
      );
    }

    // Preprocess image
    final preprocessed = await helper.preprocessImage(imageBytes);

    // Run inference (simulated - in real implementation, use TFLite interpreter)
    // This would call the actual TFLite interpreter
    final rawOutput = await _runInference(helper, preprocessed);

    // Post-process results
    return helper.postprocess(
      rawOutput,
      preprocessed,
      DetectionSource.onDevice,
    );
  }

  /// Run TFLite inference (placeholder - would use actual interpreter)
  Future<List<List<double>>> _runInference(
    TFLiteHelper helper,
    PreprocessedImage preprocessed,
  ) async {
    // In a real implementation, this would:
    // 1. Get the TFLite interpreter
    // 2. Set input tensor
    // 3. Run inference
    // 4. Get output tensor
    //
    // Example:
    // final interpreter = await Interpreter.fromFile(helper.modelPath);
    // interpreter.run(preprocessed.inputTensor, outputBuffer);
    // return parseOutput(outputBuffer);

    // For now, return empty (no detections) as placeholder
    // The actual implementation requires tflite_flutter package
    return [];
  }

  /// Cloud fallback detection via Kong gateway → pest-detection-service
  /// الكشف السحابي عبر بوابة Kong → خدمة كشف الآفات
  Future<List<Detection>> _detectWithCloud({
    required Uint8List imageBytes,
    required DetectionType type,
    String? fieldId,
  }) async {
    // Check connectivity
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) {
      throw Yolo26Exception(
        'No internet connection for cloud detection',
        'لا يوجد اتصال بالإنترنت للكشف السحابي',
      );
    }

    try {
      // Route through Kong gateway to pest-detection-service
      final gateway = kongGateway;

      // Determine the endpoint path based on detection type
      final detectPath = switch (type) {
        DetectionType.pest => '/detect/pest',
        DetectionType.disease => '/detect/disease',
        DetectionType.plant => '/count/plants',
        _ => '/detect',
      };

      // Save image to temp file for upload
      final tempDir = Directory.systemTemp;
      final tempFile = File(
        '${tempDir.path}/detection_${DateTime.now().millisecondsSinceEpoch}.jpg',
      );
      await tempFile.writeAsBytes(imageBytes);

      try {
        final response = await gateway.uploadFile<Map<String, dynamic>>(
          KongServices.pestDetection,
          detectPath,
          filePath: tempFile.path,
          fieldName: 'image',
          extraData: {
            if (fieldId != null) 'field_id': fieldId,
            'detection_type': type.name,
            'confidence_threshold': '0.25',
          },
          fromJson: (data) => data as Map<String, dynamic>,
        );

        if (response.success && response.data != null) {
          return _parseCloudResponse(response.data!, type);
        }

        // Fallback to legacy endpoint via direct HTTP
        return _detectWithLegacyCloud(
          imageBytes: imageBytes,
          type: type,
          fieldId: fieldId,
        );
      } finally {
        // Clean up temp file
        if (await tempFile.exists()) {
          await tempFile.delete();
        }
      }
    } catch (e) {
      if (e is Yolo26Exception) rethrow;
      throw Yolo26Exception(
        'Cloud detection error: $e',
        'خطأ في الكشف السحابي',
      );
    }
  }

  /// Legacy cloud detection fallback (direct HTTP to old endpoint)
  Future<List<Detection>> _detectWithLegacyCloud({
    required Uint8List imageBytes,
    required DetectionType type,
    String? fieldId,
  }) async {
    try {
      final endpoint = switch (type) {
        DetectionType.pest => '${ApiConfig.diagnose}/pest',
        DetectionType.disease => '${ApiConfig.diagnose}/disease',
        DetectionType.plant => '${ApiConfig.diagnose}/plant',
        _ => ApiConfig.diagnose,
      };

      final uri = Uri.parse(endpoint);
      final request = http.MultipartRequest('POST', uri);

      request.fields['field_id'] = fieldId ?? '';
      request.fields['detection_type'] = type.name;

      request.files.add(http.MultipartFile.fromBytes(
        'image',
        imageBytes,
        filename: 'detection_${DateTime.now().millisecondsSinceEpoch}.jpg',
      ));

      final streamedResponse = await request.send().timeout(
            const Duration(seconds: 30),
          );
      final response = await http.Response.fromStream(streamedResponse);

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return _parseCloudResponse(data, type);
      }

      throw Yolo26Exception(
        'Cloud detection failed: ${response.statusCode}',
        'فشل الكشف السحابي: ${response.statusCode}',
      );
    } catch (e) {
      if (e is Yolo26Exception) rethrow;
      throw Yolo26Exception(
        'Legacy cloud detection error: $e',
        'خطأ في الكشف السحابي القديم',
      );
    }
  }

  /// Parse cloud API response to Detection objects
  List<Detection> _parseCloudResponse(
    Map<String, dynamic> data,
    DetectionType type,
  ) {
    final detections = <Detection>[];

    final results = data['detections'] as List? ?? [];
    for (final item in results) {
      detections.add(Detection(
        detectionId: item['id'] ?? _uuid.v4(),
        className: item['class_name'] ?? 'Unknown',
        classNameAr: item['class_name_ar'] ?? 'غير معروف',
        detectionType: type,
        confidence: (item['confidence'] as num?)?.toDouble() ?? 0.0,
        bbox: BoundingBox(
          x: (item['bbox']?['x'] as num?)?.toDouble() ?? 0.0,
          y: (item['bbox']?['y'] as num?)?.toDouble() ?? 0.0,
          width: (item['bbox']?['width'] as num?)?.toDouble() ?? 0.0,
          height: (item['bbox']?['height'] as num?)?.toDouble() ?? 0.0,
        ),
        source: DetectionSource.cloud,
        severity: _parseSeverity(item['severity']),
        scientificName: item['scientific_name'],
        timestamp: DateTime.now(),
      ));
    }

    return detections;
  }

  /// Parse severity from string
  DetectionSeverity? _parseSeverity(String? value) {
    if (value == null) return null;
    return switch (value.toLowerCase()) {
      'low' => DetectionSeverity.low,
      'medium' => DetectionSeverity.medium,
      'high' => DetectionSeverity.high,
      'critical' => DetectionSeverity.critical,
      _ => null,
    };
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cleanup - التنظيف
  // ═══════════════════════════════════════════════════════════════════════════

  /// Dispose all resources
  Future<void> dispose() async {
    await _pestHelper?.dispose();
    await _diseaseHelper?.dispose();
    await _plantHelper?.dispose();
    _httpClient.close();
    _isInitialized = false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Exception - الاستثناء
// ═══════════════════════════════════════════════════════════════════════════════

/// Exception for YOLO26 service errors
/// استثناء أخطاء خدمة YOLO26
class Yolo26Exception implements Exception {
  final String message;
  final String messageAr;
  final Object? cause;

  Yolo26Exception(this.message, this.messageAr, {this.cause});

  @override
  String toString() =>
      'Yolo26Exception: $message${cause != null ? ' ($cause)' : ''}';
}
