/// SAHOOL Vision Detection Models
/// نماذج الكشف لرؤية سهول
///
/// On-device YOLO26 object detection models for pest, disease,
/// and plant counting with offline-first support.
library;

// ═══════════════════════════════════════════════════════════════════════════════
// Enums - التعدادات
// ═══════════════════════════════════════════════════════════════════════════════

/// Detection source - cloud vs on-device
/// مصدر الكشف - سحابي أو على الجهاز
enum DetectionSource {
  onDevice,
  cloud,
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
  pest,
  disease,
  weed,
  plant,
  fruit,
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
  low,
  medium,
  high,
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
class BoundingBox {
  /// X coordinate of top-left corner (normalized 0-1)
  /// إحداثي X للزاوية العلوية اليسرى (مُطَبَّع 0-1)
  final double x;

  /// Y coordinate of top-left corner (normalized 0-1)
  /// إحداثي Y للزاوية العلوية اليسرى (مُطَبَّع 0-1)
  final double y;

  /// Width of bounding box (normalized 0-1)
  /// عرض إطار الحدود (مُطَبَّع 0-1)
  final double width;

  /// Height of bounding box (normalized 0-1)
  /// ارتفاع إطار الحدود (مُطَبَّع 0-1)
  final double height;

  const BoundingBox({
    required this.x,
    required this.y,
    required this.width,
    required this.height,
  });

  factory BoundingBox.fromJson(Map<String, dynamic> json) {
    return BoundingBox(
      x: (json['x'] as num).toDouble(),
      y: (json['y'] as num).toDouble(),
      width: (json['width'] as num).toDouble(),
      height: (json['height'] as num).toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'x': x,
      'y': y,
      'width': width,
      'height': height,
    };
  }

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

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is BoundingBox &&
          runtimeType == other.runtimeType &&
          x == other.x &&
          y == other.y &&
          width == other.width &&
          height == other.height;

  @override
  int get hashCode => Object.hash(x, y, width, height);

  @override
  String toString() =>
      'BoundingBox(x: $x, y: $y, width: $width, height: $height)';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Model - نموذج الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Single detection result
/// نتيجة كشف واحدة
class Detection {
  /// Unique detection ID
  /// معرف الكشف الفريد
  final String detectionId;

  /// Class name in English
  /// اسم الفئة بالإنجليزية
  final String className;

  /// Class name in Arabic
  /// اسم الفئة بالعربية
  final String classNameAr;

  /// Detection type (pest, disease, etc.)
  /// نوع الكشف (آفة، مرض، إلخ)
  final DetectionType detectionType;

  /// Confidence score (0-1)
  /// درجة الثقة (0-1)
  final double confidence;

  /// Bounding box
  /// إطار الحدود
  final BoundingBox bbox;

  /// Source of detection (on-device or cloud)
  /// مصدر الكشف (على الجهاز أو سحابي)
  final DetectionSource source;

  /// Severity level if applicable
  /// مستوى الشدة إن وجد
  final DetectionSeverity? severity;

  /// Scientific name (Latin)
  /// الاسم العلمي (لاتيني)
  final String? scientificName;

  /// Additional metadata
  /// بيانات إضافية
  final Map<String, dynamic> metadata;

  /// Timestamp of detection
  /// وقت الكشف
  final DateTime? timestamp;

  const Detection({
    required this.detectionId,
    required this.className,
    required this.classNameAr,
    required this.detectionType,
    required this.confidence,
    required this.bbox,
    required this.source,
    this.severity,
    this.scientificName,
    this.metadata = const {},
    this.timestamp,
  });

  factory Detection.fromJson(Map<String, dynamic> json) {
    return Detection(
      detectionId: json['detectionId'] as String,
      className: json['className'] as String,
      classNameAr: json['classNameAr'] as String,
      detectionType: _detectionTypeFromJson(json['detectionType'] as String),
      confidence: (json['confidence'] as num).toDouble(),
      bbox: BoundingBox.fromJson(json['bbox'] as Map<String, dynamic>),
      source: _detectionSourceFromJson(json['source'] as String),
      severity: json['severity'] != null
          ? _detectionSeverityFromJson(json['severity'] as String)
          : null,
      scientificName: json['scientificName'] as String?,
      metadata: (json['metadata'] as Map<String, dynamic>?) ?? const {},
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'detectionId': detectionId,
      'className': className,
      'classNameAr': classNameAr,
      'detectionType': _detectionTypeToJson(detectionType),
      'confidence': confidence,
      'bbox': bbox.toJson(),
      'source': _detectionSourceToJson(source),
      if (severity != null) 'severity': _detectionSeverityToJson(severity!),
      if (scientificName != null) 'scientificName': scientificName,
      'metadata': metadata,
      if (timestamp != null) 'timestamp': timestamp!.toIso8601String(),
    };
  }

  /// Format confidence as percentage
  String get confidencePercent => '${(confidence * 100).toStringAsFixed(1)}%';

  /// Check if detection is high confidence (>70%)
  bool get isHighConfidence => confidence > 0.7;

  /// Get display label with confidence
  String get displayLabel => '$className ($confidencePercent)';

  /// Get Arabic display label with confidence
  String get displayLabelAr => '$classNameAr ($confidencePercent)';

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Detection &&
          runtimeType == other.runtimeType &&
          detectionId == other.detectionId &&
          className == other.className &&
          classNameAr == other.classNameAr &&
          detectionType == other.detectionType &&
          confidence == other.confidence &&
          bbox == other.bbox &&
          source == other.source &&
          severity == other.severity &&
          scientificName == other.scientificName &&
          timestamp == other.timestamp;

  @override
  int get hashCode => Object.hash(
        detectionId,
        className,
        classNameAr,
        detectionType,
        confidence,
        bbox,
        source,
        severity,
        scientificName,
        timestamp,
      );

  @override
  String toString() =>
      'Detection(detectionId: $detectionId, className: $className, confidence: $confidence)';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Result - نتيجة الكشف الكاملة
// ═══════════════════════════════════════════════════════════════════════════════

/// Complete detection result for an image
/// نتيجة الكشف الكاملة للصورة
class DetectionResult {
  /// Unique result ID
  /// معرف النتيجة الفريد
  final String resultId;

  /// List of detections
  /// قائمة الكشوفات
  final List<Detection> detections;

  /// Processing time in milliseconds
  /// وقت المعالجة بالمللي ثانية
  final int processingTimeMs;

  /// Image width in pixels
  /// عرض الصورة بالبكسل
  final int imageWidth;

  /// Image height in pixels
  /// ارتفاع الصورة بالبكسل
  final int imageHeight;

  /// Detection source
  /// مصدر الكشف
  final DetectionSource source;

  /// Model version used
  /// إصدار النموذج المستخدم
  final String modelVersion;

  /// Field ID if associated
  /// معرف الحقل إن وجد
  final String? fieldId;

  /// Image path (local)
  /// مسار الصورة (محلي)
  final String? imagePath;

  /// Timestamp
  /// الوقت
  final DateTime? timestamp;

  /// Device info
  /// معلومات الجهاز
  final String? deviceInfo;

  /// Error message if any
  /// رسالة الخطأ إن وجدت
  final String? error;

  const DetectionResult({
    required this.resultId,
    required this.detections,
    required this.processingTimeMs,
    required this.imageWidth,
    required this.imageHeight,
    required this.source,
    required this.modelVersion,
    this.fieldId,
    this.imagePath,
    this.timestamp,
    this.deviceInfo,
    this.error,
  });

  factory DetectionResult.fromJson(Map<String, dynamic> json) {
    return DetectionResult(
      resultId: json['resultId'] as String,
      detections: (json['detections'] as List<dynamic>)
          .map((e) => Detection.fromJson(e as Map<String, dynamic>))
          .toList(),
      processingTimeMs: json['processingTimeMs'] as int,
      imageWidth: json['imageWidth'] as int,
      imageHeight: json['imageHeight'] as int,
      source: _detectionSourceFromJson(json['source'] as String),
      modelVersion: json['modelVersion'] as String,
      fieldId: json['fieldId'] as String?,
      imagePath: json['imagePath'] as String?,
      timestamp: json['timestamp'] != null
          ? DateTime.parse(json['timestamp'] as String)
          : null,
      deviceInfo: json['deviceInfo'] as String?,
      error: json['error'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'resultId': resultId,
      'detections': detections.map((d) => d.toJson()).toList(),
      'processingTimeMs': processingTimeMs,
      'imageWidth': imageWidth,
      'imageHeight': imageHeight,
      'source': _detectionSourceToJson(source),
      'modelVersion': modelVersion,
      if (fieldId != null) 'fieldId': fieldId,
      if (imagePath != null) 'imagePath': imagePath,
      if (timestamp != null) 'timestamp': timestamp!.toIso8601String(),
      if (deviceInfo != null) 'deviceInfo': deviceInfo,
      if (error != null) 'error': error,
    };
  }

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

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DetectionResult &&
          runtimeType == other.runtimeType &&
          resultId == other.resultId;

  @override
  int get hashCode => resultId.hashCode;

  @override
  String toString() =>
      'DetectionResult(resultId: $resultId, detections: ${detections.length})';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Plant Count Result - نتيجة عد النباتات
// ═══════════════════════════════════════════════════════════════════════════════

/// Plant counting result
/// نتيجة عد النباتات
class PlantCountResult {
  /// Total plant count
  /// عدد النباتات الكلي
  final int totalCount;

  /// Individual plant detections
  /// الكشوفات الفردية للنباتات
  final List<Detection> plants;

  /// Estimated plants per hectare
  /// النباتات المقدرة للهكتار
  final double? plantsPerHectare;

  /// Image area in square meters (if known)
  /// مساحة الصورة بالمتر المربع (إن عُرفت)
  final double? imageAreaM2;

  /// Detection source
  /// مصدر الكشف
  final DetectionSource source;

  /// Processing time in milliseconds
  /// وقت المعالجة بالمللي ثانية
  final int processingTimeMs;

  /// Confidence in count (average of detections)
  /// الثقة في العدد (متوسط الكشوفات)
  final double? averageConfidence;

  /// Field ID if associated
  /// معرف الحقل إن وجد
  final String? fieldId;

  const PlantCountResult({
    required this.totalCount,
    required this.plants,
    this.plantsPerHectare,
    this.imageAreaM2,
    required this.source,
    required this.processingTimeMs,
    this.averageConfidence,
    this.fieldId,
  });

  factory PlantCountResult.fromJson(Map<String, dynamic> json) {
    return PlantCountResult(
      totalCount: json['totalCount'] as int,
      plants: (json['plants'] as List<dynamic>)
          .map((e) => Detection.fromJson(e as Map<String, dynamic>))
          .toList(),
      plantsPerHectare: (json['plantsPerHectare'] as num?)?.toDouble(),
      imageAreaM2: (json['imageAreaM2'] as num?)?.toDouble(),
      source: _detectionSourceFromJson(json['source'] as String),
      processingTimeMs: json['processingTimeMs'] as int,
      averageConfidence: (json['averageConfidence'] as num?)?.toDouble(),
      fieldId: json['fieldId'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'totalCount': totalCount,
      'plants': plants.map((p) => p.toJson()).toList(),
      if (plantsPerHectare != null) 'plantsPerHectare': plantsPerHectare,
      if (imageAreaM2 != null) 'imageAreaM2': imageAreaM2,
      'source': _detectionSourceToJson(source),
      'processingTimeMs': processingTimeMs,
      if (averageConfidence != null) 'averageConfidence': averageConfidence,
      if (fieldId != null) 'fieldId': fieldId,
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PlantCountResult &&
          runtimeType == other.runtimeType &&
          totalCount == other.totalCount &&
          processingTimeMs == other.processingTimeMs;

  @override
  int get hashCode => Object.hash(totalCount, processingTimeMs);

  @override
  String toString() =>
      'PlantCountResult(totalCount: $totalCount, plants: ${plants.length})';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Model Info - معلومات النموذج
// ═══════════════════════════════════════════════════════════════════════════════

/// Information about loaded ML model
/// معلومات عن النموذج المحمّل
class ModelInfo {
  /// Model name
  /// اسم النموذج
  final String name;

  /// Model version
  /// إصدار النموذج
  final String version;

  /// Input image size
  /// حجم صورة الإدخال
  final int inputSize;

  /// Number of classes
  /// عدد الفئات
  final int numClasses;

  /// List of class labels
  /// قائمة تسميات الفئات
  final List<String> labels;

  /// List of Arabic class labels
  /// قائمة تسميات الفئات بالعربية
  final List<String> labelsAr;

  /// Model file size in bytes
  /// حجم ملف النموذج بالبايت
  final int? fileSizeBytes;

  /// Whether model is quantized
  /// هل النموذج مكمّم
  final bool isQuantized;

  /// Supported detection types
  /// أنواع الكشف المدعومة
  final List<DetectionType> supportedTypes;

  const ModelInfo({
    required this.name,
    required this.version,
    required this.inputSize,
    required this.numClasses,
    required this.labels,
    required this.labelsAr,
    this.fileSizeBytes,
    this.isQuantized = true,
    this.supportedTypes = const [],
  });

  factory ModelInfo.fromJson(Map<String, dynamic> json) {
    return ModelInfo(
      name: json['name'] as String,
      version: json['version'] as String,
      inputSize: json['inputSize'] as int,
      numClasses: json['numClasses'] as int,
      labels: (json['labels'] as List<dynamic>).cast<String>(),
      labelsAr: (json['labelsAr'] as List<dynamic>).cast<String>(),
      fileSizeBytes: json['fileSizeBytes'] as int?,
      isQuantized: json['isQuantized'] as bool? ?? true,
      supportedTypes: (json['supportedTypes'] as List<dynamic>?)
              ?.map((e) => _detectionTypeFromJson(e as String))
              .toList() ??
          const [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'version': version,
      'inputSize': inputSize,
      'numClasses': numClasses,
      'labels': labels,
      'labelsAr': labelsAr,
      if (fileSizeBytes != null) 'fileSizeBytes': fileSizeBytes,
      'isQuantized': isQuantized,
      'supportedTypes':
          supportedTypes.map((t) => _detectionTypeToJson(t)).toList(),
    };
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ModelInfo &&
          runtimeType == other.runtimeType &&
          name == other.name &&
          version == other.version &&
          inputSize == other.inputSize &&
          numClasses == other.numClasses;

  @override
  int get hashCode => Object.hash(name, version, inputSize, numClasses);

  @override
  String toString() =>
      'ModelInfo(name: $name, version: $version, numClasses: $numClasses)';
}

// ═══════════════════════════════════════════════════════════════════════════════
// Detection Session - جلسة الكشف
// ═══════════════════════════════════════════════════════════════════════════════

/// Session tracking multiple detections
/// جلسة تتبع كشوفات متعددة
class DetectionSession {
  /// Session ID
  /// معرف الجلسة
  final String sessionId;

  /// Field ID
  /// معرف الحقل
  final String? fieldId;

  /// Session start time
  /// وقت بدء الجلسة
  final DateTime startTime;

  /// Session end time (null if ongoing)
  /// وقت انتهاء الجلسة (فارغ إذا جارية)
  final DateTime? endTime;

  /// All detection results in session
  /// جميع نتائج الكشف في الجلسة
  final List<DetectionResult> results;

  /// Total images processed
  /// إجمالي الصور المعالجة
  final int imagesProcessed;

  /// Total detections found
  /// إجمالي الكشوفات
  final int totalDetections;

  /// Notes from user
  /// ملاحظات المستخدم
  final String? notes;

  /// GPS coordinates if captured
  /// إحداثيات GPS إن التُقطت
  final double? latitude;
  final double? longitude;

  const DetectionSession({
    required this.sessionId,
    this.fieldId,
    required this.startTime,
    this.endTime,
    this.results = const [],
    this.imagesProcessed = 0,
    this.totalDetections = 0,
    this.notes,
    this.latitude,
    this.longitude,
  });

  factory DetectionSession.fromJson(Map<String, dynamic> json) {
    return DetectionSession(
      sessionId: json['sessionId'] as String,
      fieldId: json['fieldId'] as String?,
      startTime: DateTime.parse(json['startTime'] as String),
      endTime: json['endTime'] != null
          ? DateTime.parse(json['endTime'] as String)
          : null,
      results: (json['results'] as List<dynamic>?)
              ?.map((e) => DetectionResult.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      imagesProcessed: json['imagesProcessed'] as int? ?? 0,
      totalDetections: json['totalDetections'] as int? ?? 0,
      notes: json['notes'] as String?,
      latitude: (json['latitude'] as num?)?.toDouble(),
      longitude: (json['longitude'] as num?)?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'sessionId': sessionId,
      if (fieldId != null) 'fieldId': fieldId,
      'startTime': startTime.toIso8601String(),
      if (endTime != null) 'endTime': endTime!.toIso8601String(),
      'results': results.map((r) => r.toJson()).toList(),
      'imagesProcessed': imagesProcessed,
      'totalDetections': totalDetections,
      if (notes != null) 'notes': notes,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
    };
  }

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

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is DetectionSession &&
          runtimeType == other.runtimeType &&
          sessionId == other.sessionId;

  @override
  int get hashCode => sessionId.hashCode;

  @override
  String toString() =>
      'DetectionSession(sessionId: $sessionId, fieldId: $fieldId)';
}

// ═══════════════════════════════════════════════════════════════════════════════
// JSON Helpers - مساعدات JSON
// ═══════════════════════════════════════════════════════════════════════════════

DetectionType _detectionTypeFromJson(String value) {
  return switch (value) {
    'pest' => DetectionType.pest,
    'disease' => DetectionType.disease,
    'weed' => DetectionType.weed,
    'plant' => DetectionType.plant,
    'fruit' => DetectionType.fruit,
    'deficiency' => DetectionType.deficiency,
    _ => DetectionType.pest,
  };
}

String _detectionTypeToJson(DetectionType type) {
  return switch (type) {
    DetectionType.pest => 'pest',
    DetectionType.disease => 'disease',
    DetectionType.weed => 'weed',
    DetectionType.plant => 'plant',
    DetectionType.fruit => 'fruit',
    DetectionType.deficiency => 'deficiency',
  };
}

DetectionSource _detectionSourceFromJson(String value) {
  return switch (value) {
    'on_device' => DetectionSource.onDevice,
    'cloud' => DetectionSource.cloud,
    'hybrid' => DetectionSource.hybrid,
    _ => DetectionSource.onDevice,
  };
}

String _detectionSourceToJson(DetectionSource source) {
  return switch (source) {
    DetectionSource.onDevice => 'on_device',
    DetectionSource.cloud => 'cloud',
    DetectionSource.hybrid => 'hybrid',
  };
}

DetectionSeverity _detectionSeverityFromJson(String value) {
  return switch (value) {
    'low' => DetectionSeverity.low,
    'medium' => DetectionSeverity.medium,
    'high' => DetectionSeverity.high,
    'critical' => DetectionSeverity.critical,
    _ => DetectionSeverity.low,
  };
}

String _detectionSeverityToJson(DetectionSeverity severity) {
  return switch (severity) {
    DetectionSeverity.low => 'low',
    DetectionSeverity.medium => 'medium',
    DetectionSeverity.high => 'high',
    DetectionSeverity.critical => 'critical',
  };
}
