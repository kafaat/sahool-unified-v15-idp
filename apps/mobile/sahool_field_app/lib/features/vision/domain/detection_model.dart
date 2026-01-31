/// SAHOOL Vision Detection Models
/// نماذج الكشف لرؤية سهول
///
/// On-device YOLO26 object detection models for pest, disease,
/// and plant counting with offline-first support.
library;

import 'package:freezed_annotation/freezed_annotation.dart';

part 'detection_model.freezed.dart';
part 'detection_model.g.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Enums - التعدادات
// ═══════════════════════════════════════════════════════════════════════════════

/// Detection source - cloud vs on-device
/// مصدر الكشف - سحابي أو على الجهاز
enum DetectionSource {
  @JsonValue('on_device')
  onDevice,
  @JsonValue('cloud')
  cloud,
  @JsonValue('hybrid')
  hybrid;

  String get displayName => switch (this) {
        onDevice => 'On-Device',
        cloud => 'Cloud',
        hybrid => 'Hybrid',
      };

  String get displayNameAr => switch (this) {
        onDevice => 'على الجهاز',
        cloud => 'سحابي',
        hybrid => 'هجين',
      };
}

/// Detection type - نوع الكشف
enum DetectionType {
  @JsonValue('pest')
  pest,
  @JsonValue('disease')
  disease,
  @JsonValue('weed')
  weed,
  @JsonValue('plant')
  plant,
  @JsonValue('fruit')
  fruit,
  @JsonValue('deficiency')
  deficiency;

  String get displayName => switch (this) {
        pest => 'Pest',
        disease => 'Disease',
        weed => 'Weed',
        plant => 'Plant',
        fruit => 'Fruit',
        deficiency => 'Nutrient Deficiency',
      };

  String get displayNameAr => switch (this) {
        pest => 'آفة',
        disease => 'مرض',
        weed => 'حشائش',
        plant => 'نبات',
        fruit => 'ثمرة',
        deficiency => 'نقص عنصر غذائي',
      };

  String get icon => switch (this) {
        pest => '🐛',
        disease => '🦠',
        weed => '🌿',
        plant => '🌱',
        fruit => '🍎',
        deficiency => '⚠️',
      };
}

/// Severity level for detections
/// مستوى الشدة للكشوفات
enum DetectionSeverity {
  @JsonValue('low')
  low,
  @JsonValue('medium')
  medium,
  @JsonValue('high')
  high,
  @JsonValue('critical')
  critical;

  String get displayName => switch (this) {
        low => 'Low',
        medium => 'Medium',
        high => 'High',
        critical => 'Critical',
      };

  String get displayNameAr => switch (this) {
        low => 'منخفض',
        medium => 'متوسط',
        high => 'مرتفع',
        critical => 'حرج',
      };

  String get colorHex => switch (this) {
        low => '#22C55E',
        medium => '#EAB308',
        high => '#F97316',
        critical => '#EF4444',
      };
}

// ═══════════════════════════════════════════════════════════════════════════════
// Bounding Box - إطار الحدود
// ═══════════════════════════════════════════════════════════════════════════════

/// Bounding box for object detection
/// إطار الحدود للكشف عن الكائنات
@freezed
class BoundingBox with _$BoundingBox {
  const factory BoundingBox({
    /// X coordinate of top-left corner (normalized 0-1)
    /// إحداثي X للزاوية العلوية اليسرى (مُطَبَّع 0-1)
    required double x,

    /// Y coordinate of top-left corner (normalized 0-1)
    /// إحداثي Y للزاوية العلوية اليسرى (مُطَبَّع 0-1)
    required double y,

    /// Width of bounding box (normalized 0-1)
    /// عرض إطار الحدود (مُطَبَّع 0-1)
    required double width,

    /// Height of bounding box (normalized 0-1)
    /// ارتفاع إطار الحدود (مُطَبَّع 0-1)
    required double height,
  }) = _BoundingBox;

  const BoundingBox._();

  factory BoundingBox.fromJson(Map<String, dynamic> json) =>
      _$BoundingBoxFromJson(json);

  /// Center X coordinate
  double get centerX => x + width / 2;

  /// Center Y coordinate
  double get centerY => y + height / 2;

  /// Area of bounding box (normalized)
  double get area => width * height;

  /// Convert to pixel coordinates
  /// تحويل لإحداثيات البكسل
  Map<String, int> toPixels(int imageWidth, int imageHeight) {
    return {
      'x': (x * imageWidth).round(),
      'y': (y * imageHeight).round(),
      'width': (width * imageWidth).round(),
      'height': (height * imageHeight).round(),
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Model - نموذج الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Single detection result
/// نتيجة كشف واحدة
@freezed
class Detection with _$Detection {
  const factory Detection({
    /// Unique detection ID
    /// معرف الكشف الفريد
    required String detectionId,

    /// Class name in English
    /// اسم الفئة بالإنجليزية
    required String className,

    /// Class name in Arabic
    /// اسم الفئة بالعربية
    required String classNameAr,

    /// Detection type (pest, disease, etc.)
    /// نوع الكشف (آفة، مرض، إلخ)
    required DetectionType detectionType,

    /// Confidence score (0-1)
    /// درجة الثقة (0-1)
    required double confidence,

    /// Bounding box
    /// إطار الحدود
    required BoundingBox bbox,

    /// Source of detection (on-device or cloud)
    /// مصدر الكشف (على الجهاز أو سحابي)
    required DetectionSource source,

    /// Severity level if applicable
    /// مستوى الشدة إن وجد
    DetectionSeverity? severity,

    /// Scientific name (Latin)
    /// الاسم العلمي (لاتيني)
    String? scientificName,

    /// Additional metadata
    /// بيانات إضافية
    @Default({}) Map<String, dynamic> metadata,

    /// Timestamp of detection
    /// وقت الكشف
    DateTime? timestamp,
  }) = _Detection;

  const Detection._();

  factory Detection.fromJson(Map<String, dynamic> json) =>
      _$DetectionFromJson(json);

  /// Format confidence as percentage
  String get confidencePercent => '${(confidence * 100).toStringAsFixed(1)}%';

  /// Check if detection is high confidence (>70%)
  bool get isHighConfidence => confidence > 0.7;

  /// Get display label with confidence
  String get displayLabel => '$className ($confidencePercent)';

  /// Get Arabic display label with confidence
  String get displayLabelAr => '$classNameAr ($confidencePercent)';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Result - نتيجة الكشف الكاملة
// ═══════════════════════════════════════════════════════════════════════════════

/// Complete detection result for an image
/// نتيجة الكشف الكاملة للصورة
@freezed
class DetectionResult with _$DetectionResult {
  const factory DetectionResult({
    /// Unique result ID
    /// معرف النتيجة الفريد
    required String resultId,

    /// List of detections
    /// قائمة الكشوفات
    required List<Detection> detections,

    /// Processing time in milliseconds
    /// وقت المعالجة بالمللي ثانية
    required int processingTimeMs,

    /// Image width in pixels
    /// عرض الصورة بالبكسل
    required int imageWidth,

    /// Image height in pixels
    /// ارتفاع الصورة بالبكسل
    required int imageHeight,

    /// Detection source
    /// مصدر الكشف
    required DetectionSource source,

    /// Model version used
    /// إصدار النموذج المستخدم
    required String modelVersion,

    /// Field ID if associated
    /// معرف الحقل إن وجد
    String? fieldId,

    /// Image path (local)
    /// مسار الصورة (محلي)
    String? imagePath,

    /// Timestamp
    /// الوقت
    DateTime? timestamp,

    /// Device info
    /// معلومات الجهاز
    String? deviceInfo,

    /// Error message if any
    /// رسالة الخطأ إن وجدت
    String? error,
  }) = _DetectionResult;

  const DetectionResult._();

  factory DetectionResult.fromJson(Map<String, dynamic> json) =>
      _$DetectionResultFromJson(json);

  /// Check if detection was successful
  bool get isSuccess => error == null;

  /// Total count of detections
  int get totalDetections => detections.length;

  /// Count by detection type
  Map<DetectionType, int> get countByType {
    final counts = <DetectionType, int>{};
    for (final detection in detections) {
      counts[detection.detectionType] =
          (counts[detection.detectionType] ?? 0) + 1;
    }
    return counts;
  }

  /// Get detections by type
  List<Detection> getByType(DetectionType type) {
    return detections.where((d) => d.detectionType == type).toList();
  }

  /// Get high confidence detections only
  List<Detection> get highConfidenceDetections {
    return detections.where((d) => d.isHighConfidence).toList();
  }

  /// Get pests only
  List<Detection> get pests => getByType(DetectionType.pest);

  /// Get diseases only
  List<Detection> get diseases => getByType(DetectionType.disease);

  /// Get plants only
  List<Detection> get plants => getByType(DetectionType.plant);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Plant Count Result - نتيجة عد النباتات
// ═══════════════════════════════════════════════════════════════════════════════

/// Plant counting result
/// نتيجة عد النباتات
@freezed
class PlantCountResult with _$PlantCountResult {
  const factory PlantCountResult({
    /// Total plant count
    /// عدد النباتات الكلي
    required int totalCount,

    /// Individual plant detections
    /// الكشوفات الفردية للنباتات
    required List<Detection> plants,

    /// Estimated plants per hectare
    /// النباتات المقدرة للهكتار
    double? plantsPerHectare,

    /// Image area in square meters (if known)
    /// مساحة الصورة بالمتر المربع (إن عُرفت)
    double? imageAreaM2,

    /// Detection source
    /// مصدر الكشف
    required DetectionSource source,

    /// Processing time in milliseconds
    /// وقت المعالجة بالمللي ثانية
    required int processingTimeMs,

    /// Confidence in count (average of detections)
    /// الثقة في العدد (متوسط الكشوفات)
    double? averageConfidence,

    /// Field ID if associated
    /// معرف الحقل إن وجد
    String? fieldId,
  }) = _PlantCountResult;

  factory PlantCountResult.fromJson(Map<String, dynamic> json) =>
      _$PlantCountResultFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Model Info - معلومات النموذج
// ═══════════════════════════════════════════════════════════════════════════════

/// Information about loaded ML model
/// معلومات عن النموذج المحمّل
@freezed
class ModelInfo with _$ModelInfo {
  const factory ModelInfo({
    /// Model name
    /// اسم النموذج
    required String name,

    /// Model version
    /// إصدار النموذج
    required String version,

    /// Input image size
    /// حجم صورة الإدخال
    required int inputSize,

    /// Number of classes
    /// عدد الفئات
    required int numClasses,

    /// List of class labels
    /// قائمة تسميات الفئات
    required List<String> labels,

    /// List of Arabic class labels
    /// قائمة تسميات الفئات بالعربية
    required List<String> labelsAr,

    /// Model file size in bytes
    /// حجم ملف النموذج بالبايت
    int? fileSizeBytes,

    /// Whether model is quantized
    /// هل النموذج مكمّم
    @Default(true) bool isQuantized,

    /// Supported detection types
    /// أنواع الكشف المدعومة
    @Default([]) List<DetectionType> supportedTypes,
  }) = _ModelInfo;

  factory ModelInfo.fromJson(Map<String, dynamic> json) =>
      _$ModelInfoFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Session - جلسة الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Session tracking multiple detections
/// جلسة تتبع كشوفات متعددة
@freezed
class DetectionSession with _$DetectionSession {
  const factory DetectionSession({
    /// Session ID
    /// معرف الجلسة
    required String sessionId,

    /// Field ID
    /// معرف الحقل
    String? fieldId,

    /// Session start time
    /// وقت بدء الجلسة
    required DateTime startTime,

    /// Session end time (null if ongoing)
    /// وقت انتهاء الجلسة (فارغ إذا جارية)
    DateTime? endTime,

    /// All detection results in session
    /// جميع نتائج الكشف في الجلسة
    @Default([]) List<DetectionResult> results,

    /// Total images processed
    /// إجمالي الصور المعالجة
    @Default(0) int imagesProcessed,

    /// Total detections found
    /// إجمالي الكشوفات
    @Default(0) int totalDetections,

    /// Notes from user
    /// ملاحظات المستخدم
    String? notes,

    /// GPS coordinates if captured
    /// إحداثيات GPS إن التُقطت
    @JsonKey(name: 'latitude') double? latitude,
    @JsonKey(name: 'longitude') double? longitude,
  }) = _DetectionSession;

  const DetectionSession._();

  factory DetectionSession.fromJson(Map<String, dynamic> json) =>
      _$DetectionSessionFromJson(json);

  /// Session duration
  Duration? get duration {
    if (endTime == null) return null;
    return endTime!.difference(startTime);
  }

  /// Check if session is ongoing
  bool get isOngoing => endTime == null;

  /// Get summary of detections by type
  Map<DetectionType, int> get summaryByType {
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
