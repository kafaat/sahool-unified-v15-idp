import 'package:flutter/foundation.dart';

/// SAHOOL Scout Session Models
/// نماذج جلسة مسح الحقول
///
/// يشمل:
/// - جلسة المسح
/// - نقطة التفتيش
/// - الملاحظة
/// - المسار

/// جلسة مسح الحقل
class ScoutSession {
  final String id;
  final String fieldId;
  final String fieldName;
  final String scouterId;
  final String scouterName;
  final DateTime startedAt;
  final DateTime? endedAt;
  final ScoutSessionStatus status;
  final List<ScoutCheckpoint> checkpoints;
  final List<GeoPoint> trackPoints;
  final ScoutSessionSummary? summary;
  final Map<String, dynamic>? metadata;

  const ScoutSession({
    required this.id,
    required this.fieldId,
    required this.fieldName,
    required this.scouterId,
    required this.scouterName,
    required this.startedAt,
    this.endedAt,
    required this.status,
    this.checkpoints = const [],
    this.trackPoints = const [],
    this.summary,
    this.metadata,
  });

  Duration get duration {
    final end = endedAt ?? DateTime.now();
    return end.difference(startedAt);
  }

  double get distanceMeters {
    if (trackPoints.length < 2) return 0;

    double total = 0;
    for (int i = 1; i < trackPoints.length; i++) {
      total += trackPoints[i - 1].distanceTo(trackPoints[i]);
    }
    return total;
  }

  int get issuesCount => checkpoints.where((c) => c.hasIssue).length;

  ScoutSession copyWith({
    String? id,
    String? fieldId,
    String? fieldName,
    String? scouterId,
    String? scouterName,
    DateTime? startedAt,
    DateTime? endedAt,
    ScoutSessionStatus? status,
    List<ScoutCheckpoint>? checkpoints,
    List<GeoPoint>? trackPoints,
    ScoutSessionSummary? summary,
    Map<String, dynamic>? metadata,
  }) {
    return ScoutSession(
      id: id ?? this.id,
      fieldId: fieldId ?? this.fieldId,
      fieldName: fieldName ?? this.fieldName,
      scouterId: scouterId ?? this.scouterId,
      scouterName: scouterName ?? this.scouterName,
      startedAt: startedAt ?? this.startedAt,
      endedAt: endedAt ?? this.endedAt,
      status: status ?? this.status,
      checkpoints: checkpoints ?? this.checkpoints,
      trackPoints: trackPoints ?? this.trackPoints,
      summary: summary ?? this.summary,
      metadata: metadata ?? this.metadata,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'fieldId': fieldId,
    'fieldName': fieldName,
    'scouterId': scouterId,
    'scouterName': scouterName,
    'startedAt': startedAt.toIso8601String(),
    'endedAt': endedAt?.toIso8601String(),
    'status': status.name,
    'checkpoints': checkpoints.map((c) => c.toJson()).toList(),
    'trackPoints': trackPoints.map((p) => p.toJson()).toList(),
    'summary': summary?.toJson(),
    'metadata': metadata,
  };

  factory ScoutSession.fromJson(Map<String, dynamic> json) => ScoutSession(
    id: json['id'] as String,
    fieldId: json['fieldId'] as String,
    fieldName: json['fieldName'] as String,
    scouterId: json['scouterId'] as String,
    scouterName: json['scouterName'] as String,
    startedAt: DateTime.parse(json['startedAt'] as String),
    endedAt: json['endedAt'] != null
        ? DateTime.parse(json['endedAt'] as String)
        : null,
    status: ScoutSessionStatus.values.byName(json['status'] as String),
    checkpoints: (json['checkpoints'] as List?)
        ?.map((c) => ScoutCheckpoint.fromJson(c as Map<String, dynamic>))
        .toList() ?? [],
    trackPoints: (json['trackPoints'] as List?)
        ?.map((p) => GeoPoint.fromJson(p as Map<String, dynamic>))
        .toList() ?? [],
    summary: json['summary'] != null
        ? ScoutSessionSummary.fromJson(json['summary'] as Map<String, dynamic>)
        : null,
    metadata: json['metadata'] as Map<String, dynamic>?,
  );
}

/// حالة جلسة المسح
enum ScoutSessionStatus {
  active,
  paused,
  completed,
  cancelled,
}

/// نقطة تفتيش
class ScoutCheckpoint {
  final String id;
  final GeoPoint location;
  final DateTime timestamp;
  final CheckpointType type;
  final String? note;
  final List<String> photoUrls;
  final IssueDetails? issue;
  final AIAnalysis? aiAnalysis;
  final Map<String, dynamic>? measurements;

  const ScoutCheckpoint({
    required this.id,
    required this.location,
    required this.timestamp,
    required this.type,
    this.note,
    this.photoUrls = const [],
    this.issue,
    this.aiAnalysis,
    this.measurements,
  });

  bool get hasIssue => issue != null;
  bool get hasPhotos => photoUrls.isNotEmpty;
  bool get hasAIAnalysis => aiAnalysis != null;

  Map<String, dynamic> toJson() => {
    'id': id,
    'location': location.toJson(),
    'timestamp': timestamp.toIso8601String(),
    'type': type.name,
    'note': note,
    'photoUrls': photoUrls,
    'issue': issue?.toJson(),
    'aiAnalysis': aiAnalysis?.toJson(),
    'measurements': measurements,
  };

  factory ScoutCheckpoint.fromJson(Map<String, dynamic> json) => ScoutCheckpoint(
    id: json['id'] as String,
    location: GeoPoint.fromJson(json['location'] as Map<String, dynamic>),
    timestamp: DateTime.parse(json['timestamp'] as String),
    type: CheckpointType.values.byName(json['type'] as String),
    note: json['note'] as String?,
    photoUrls: (json['photoUrls'] as List?)?.cast<String>() ?? [],
    issue: json['issue'] != null
        ? IssueDetails.fromJson(json['issue'] as Map<String, dynamic>)
        : null,
    aiAnalysis: json['aiAnalysis'] != null
        ? AIAnalysis.fromJson(json['aiAnalysis'] as Map<String, dynamic>)
        : null,
    measurements: json['measurements'] as Map<String, dynamic>?,
  );
}

/// نوع نقطة التفتيش
enum CheckpointType {
  routine,       // فحص روتيني
  issue,         // مشكلة مكتشفة
  sample,        // عينة
  measurement,   // قياس
  photo,         // صورة فقط
  boundary,      // حدود الحقل
}

/// تفاصيل المشكلة
class IssueDetails {
  final IssueCategory category;
  final IssueSeverity severity;
  final String description;
  final double? affectedAreaPercent;
  final List<String> recommendations;

  const IssueDetails({
    required this.category,
    required this.severity,
    required this.description,
    this.affectedAreaPercent,
    this.recommendations = const [],
  });

  Map<String, dynamic> toJson() => {
    'category': category.name,
    'severity': severity.name,
    'description': description,
    'affectedAreaPercent': affectedAreaPercent,
    'recommendations': recommendations,
  };

  factory IssueDetails.fromJson(Map<String, dynamic> json) => IssueDetails(
    category: IssueCategory.values.byName(json['category'] as String),
    severity: IssueSeverity.values.byName(json['severity'] as String),
    description: json['description'] as String,
    affectedAreaPercent: json['affectedAreaPercent'] as double?,
    recommendations: (json['recommendations'] as List?)?.cast<String>() ?? [],
  );
}

/// فئة المشكلة
enum IssueCategory {
  pest,           // آفة
  disease,        // مرض
  weed,           // أعشاب ضارة
  nutrient,       // نقص غذائي
  water,          // مشكلة مائية
  soil,           // مشكلة تربة
  weather,        // ضرر مناخي
  mechanical,     // ضرر ميكانيكي
  other,          // أخرى
}

/// شدة المشكلة
enum IssueSeverity {
  low,
  medium,
  high,
  critical,
}

/// تحليل الذكاء الاصطناعي
class AIAnalysis {
  final String modelVersion;
  final double confidence;
  final String? detectedIssue;
  final IssueCategory? category;
  final IssueSeverity? severity;
  final List<String> suggestions;
  final DateTime analyzedAt;

  const AIAnalysis({
    required this.modelVersion,
    required this.confidence,
    this.detectedIssue,
    this.category,
    this.severity,
    this.suggestions = const [],
    required this.analyzedAt,
  });

  Map<String, dynamic> toJson() => {
    'modelVersion': modelVersion,
    'confidence': confidence,
    'detectedIssue': detectedIssue,
    'category': category?.name,
    'severity': severity?.name,
    'suggestions': suggestions,
    'analyzedAt': analyzedAt.toIso8601String(),
  };

  factory AIAnalysis.fromJson(Map<String, dynamic> json) => AIAnalysis(
    modelVersion: json['modelVersion'] as String,
    confidence: (json['confidence'] as num).toDouble(),
    detectedIssue: json['detectedIssue'] as String?,
    category: json['category'] != null
        ? IssueCategory.values.byName(json['category'] as String)
        : null,
    severity: json['severity'] != null
        ? IssueSeverity.values.byName(json['severity'] as String)
        : null,
    suggestions: (json['suggestions'] as List?)?.cast<String>() ?? [],
    analyzedAt: DateTime.parse(json['analyzedAt'] as String),
  );
}

/// نقطة جغرافية
class GeoPoint {
  final double latitude;
  final double longitude;
  final double? altitude;
  final double? accuracy;
  final DateTime? timestamp;

  const GeoPoint({
    required this.latitude,
    required this.longitude,
    this.altitude,
    this.accuracy,
    this.timestamp,
  });

  /// حساب المسافة بين نقطتين (بالمتر)
  double distanceTo(GeoPoint other) {
    // Haversine formula
    const double earthRadius = 6371000; // meters
    final double lat1Rad = latitude * (3.14159265359 / 180);
    final double lat2Rad = other.latitude * (3.14159265359 / 180);
    final double deltaLat = (other.latitude - latitude) * (3.14159265359 / 180);
    final double deltaLon = (other.longitude - longitude) * (3.14159265359 / 180);

    final double a = (sin(deltaLat / 2) * sin(deltaLat / 2)) +
        (cos(lat1Rad) * cos(lat2Rad) * sin(deltaLon / 2) * sin(deltaLon / 2));
    final double c = 2 * atan2(sqrt(a), sqrt(1 - a));

    return earthRadius * c;
  }

  // Math functions
  static double sin(double x) => _sin(x);
  static double cos(double x) => _cos(x);
  static double sqrt(double x) => _sqrt(x);
  static double atan2(double y, double x) => _atan2(y, x);

  static double _sin(double x) {
    // Taylor series approximation
    x = x % (2 * 3.14159265359);
    double result = x;
    double term = x;
    for (int i = 1; i <= 10; i++) {
      term *= -x * x / ((2 * i) * (2 * i + 1));
      result += term;
    }
    return result;
  }

  static double _cos(double x) => _sin(x + 3.14159265359 / 2);

  static double _sqrt(double x) {
    if (x <= 0) return 0;
    double guess = x / 2;
    for (int i = 0; i < 20; i++) {
      guess = (guess + x / guess) / 2;
    }
    return guess;
  }

  static double _atan2(double y, double x) {
    if (x > 0) return _atan(y / x);
    if (x < 0 && y >= 0) return _atan(y / x) + 3.14159265359;
    if (x < 0 && y < 0) return _atan(y / x) - 3.14159265359;
    if (x == 0 && y > 0) return 3.14159265359 / 2;
    if (x == 0 && y < 0) return -3.14159265359 / 2;
    return 0;
  }

  static double _atan(double x) {
    // Taylor series approximation
    double result = 0;
    double term = x;
    for (int i = 0; i < 50; i++) {
      result += (i % 2 == 0 ? 1 : -1) * term / (2 * i + 1);
      term *= x * x;
    }
    return result;
  }

  Map<String, dynamic> toJson() => {
    'latitude': latitude,
    'longitude': longitude,
    'altitude': altitude,
    'accuracy': accuracy,
    'timestamp': timestamp?.toIso8601String(),
  };

  factory GeoPoint.fromJson(Map<String, dynamic> json) => GeoPoint(
    latitude: (json['latitude'] as num).toDouble(),
    longitude: (json['longitude'] as num).toDouble(),
    altitude: (json['altitude'] as num?)?.toDouble(),
    accuracy: (json['accuracy'] as num?)?.toDouble(),
    timestamp: json['timestamp'] != null
        ? DateTime.parse(json['timestamp'] as String)
        : null,
  );
}

/// ملخص جلسة المسح
class ScoutSessionSummary {
  final int totalCheckpoints;
  final int issuesFound;
  final int photosCount;
  final double distanceMeters;
  final Duration duration;
  final double fieldCoveragePercent;
  final Map<IssueCategory, int> issuesByCategory;
  final Map<IssueSeverity, int> issuesBySeverity;
  final String? overallHealthStatus;
  final List<String> recommendations;

  const ScoutSessionSummary({
    required this.totalCheckpoints,
    required this.issuesFound,
    required this.photosCount,
    required this.distanceMeters,
    required this.duration,
    required this.fieldCoveragePercent,
    this.issuesByCategory = const {},
    this.issuesBySeverity = const {},
    this.overallHealthStatus,
    this.recommendations = const [],
  });

  Map<String, dynamic> toJson() => {
    'totalCheckpoints': totalCheckpoints,
    'issuesFound': issuesFound,
    'photosCount': photosCount,
    'distanceMeters': distanceMeters,
    'durationMinutes': duration.inMinutes,
    'fieldCoveragePercent': fieldCoveragePercent,
    'issuesByCategory': issuesByCategory.map((k, v) => MapEntry(k.name, v)),
    'issuesBySeverity': issuesBySeverity.map((k, v) => MapEntry(k.name, v)),
    'overallHealthStatus': overallHealthStatus,
    'recommendations': recommendations,
  };

  factory ScoutSessionSummary.fromJson(Map<String, dynamic> json) => ScoutSessionSummary(
    totalCheckpoints: json['totalCheckpoints'] as int,
    issuesFound: json['issuesFound'] as int,
    photosCount: json['photosCount'] as int,
    distanceMeters: (json['distanceMeters'] as num).toDouble(),
    duration: Duration(minutes: json['durationMinutes'] as int),
    fieldCoveragePercent: (json['fieldCoveragePercent'] as num).toDouble(),
    issuesByCategory: (json['issuesByCategory'] as Map<String, dynamic>?)
        ?.map((k, v) => MapEntry(IssueCategory.values.byName(k), v as int)) ?? {},
    issuesBySeverity: (json['issuesBySeverity'] as Map<String, dynamic>?)
        ?.map((k, v) => MapEntry(IssueSeverity.values.byName(k), v as int)) ?? {},
    overallHealthStatus: json['overallHealthStatus'] as String?,
    recommendations: (json['recommendations'] as List?)?.cast<String>() ?? [],
  );
}
