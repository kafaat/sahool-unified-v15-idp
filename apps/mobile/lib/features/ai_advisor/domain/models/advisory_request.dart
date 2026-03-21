/// AI Advisory Request Model
/// نموذج طلب التوصية من المستشار الذكي
///
/// Represents a request to the AI Advisory system
library;

import 'package:flutter/foundation.dart';
import 'advisory.dart';

/// Request type enum
/// نوع الطلب
enum AdvisoryRequestType {
  question,       // سؤال عام
  diagnosis,      // تشخيص
  recommendation, // توصية
  analysis,       // تحليل
}

/// AI Advisory Request Model
/// نموذج طلب المستشار الذكي
@immutable
class AdvisoryRequest {
  /// Unique request ID
  final String? id;

  /// Request type
  final AdvisoryRequestType type;

  /// User's question or query (in Arabic or English)
  final String query;

  /// Field ID for context (optional)
  final String? fieldId;

  /// Field name for display
  final String? fieldName;

  /// Crop type for context (optional)
  final String? cropType;

  /// Focus area (irrigation, fertilization, pest_control, etc.)
  final AdvisoryType? focusArea;

  /// Image path for diagnosis (optional)
  final String? imagePath;

  /// Whether to include weather data
  final bool includeWeather;

  /// Whether to include soil data
  final bool includeSoil;

  /// Whether to include crop health data
  final bool includeCropHealth;

  /// Preferred language for response
  final String language;

  /// User's location for weather context
  final AdvisoryLocation? location;

  /// Additional context parameters
  final Map<String, dynamic>? additionalContext;

  /// Timestamp of request
  final DateTime createdAt;

  const AdvisoryRequest({
    this.id,
    required this.type,
    required this.query,
    this.fieldId,
    this.fieldName,
    this.cropType,
    this.focusArea,
    this.imagePath,
    this.includeWeather = true,
    this.includeSoil = true,
    this.includeCropHealth = true,
    this.language = 'ar',
    this.location,
    this.additionalContext,
    DateTime? createdAt,
  }) : createdAt = createdAt ?? const _DefaultDateTime();

  /// Create a question request
  factory AdvisoryRequest.question({
    required String query,
    String? fieldId,
    String? fieldName,
    String? cropType,
    String language = 'ar',
    AdvisoryLocation? location,
  }) {
    return AdvisoryRequest(
      type: AdvisoryRequestType.question,
      query: query,
      fieldId: fieldId,
      fieldName: fieldName,
      cropType: cropType,
      language: language,
      location: location,
      createdAt: DateTime.now(),
    );
  }

  /// Create a diagnosis request (with image)
  factory AdvisoryRequest.diagnosis({
    required String imagePath,
    String? query,
    String? fieldId,
    String? fieldName,
    String? cropType,
    String language = 'ar',
    AdvisoryLocation? location,
  }) {
    return AdvisoryRequest(
      type: AdvisoryRequestType.diagnosis,
      query: query ?? 'ما هذا المرض أو الآفة؟',
      imagePath: imagePath,
      fieldId: fieldId,
      fieldName: fieldName,
      cropType: cropType,
      language: language,
      location: location,
      createdAt: DateTime.now(),
    );
  }

  /// Create a recommendation request
  factory AdvisoryRequest.recommendation({
    required AdvisoryType focusArea,
    String? query,
    String? fieldId,
    String? fieldName,
    String? cropType,
    String language = 'ar',
    AdvisoryLocation? location,
  }) {
    return AdvisoryRequest(
      type: AdvisoryRequestType.recommendation,
      query: query ?? _getDefaultQuery(focusArea),
      focusArea: focusArea,
      fieldId: fieldId,
      fieldName: fieldName,
      cropType: cropType,
      language: language,
      location: location,
      createdAt: DateTime.now(),
    );
  }

  /// Create a field analysis request
  factory AdvisoryRequest.analysis({
    required String fieldId,
    String? fieldName,
    String? cropType,
    String language = 'ar',
  }) {
    return AdvisoryRequest(
      type: AdvisoryRequestType.analysis,
      query: 'تحليل شامل للحقل',
      fieldId: fieldId,
      fieldName: fieldName,
      cropType: cropType,
      language: language,
      createdAt: DateTime.now(),
    );
  }

  /// Convert to JSON for API
  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type.name,
    'query': query,
    'field_id': fieldId,
    'field_name': fieldName,
    'crop_type': cropType,
    'focus_area': focusArea?.name,
    'image_path': imagePath,
    'include_weather': includeWeather,
    'include_soil': includeSoil,
    'include_crop_health': includeCropHealth,
    'language': language,
    'location': location?.toJson(),
    'additional_context': additionalContext,
    'created_at': createdAt.toIso8601String(),
  };

  /// Create from JSON
  factory AdvisoryRequest.fromJson(Map<String, dynamic> json) {
    return AdvisoryRequest(
      id: json['id'] as String?,
      type: _parseRequestType(json['type'] as String?),
      query: json['query'] as String? ?? '',
      fieldId: json['field_id'] as String?,
      fieldName: json['field_name'] as String?,
      cropType: json['crop_type'] as String?,
      focusArea: json['focus_area'] != null
          ? _parseFocusArea(json['focus_area'] as String)
          : null,
      imagePath: json['image_path'] as String?,
      includeWeather: json['include_weather'] as bool? ?? true,
      includeSoil: json['include_soil'] as bool? ?? true,
      includeCropHealth: json['include_crop_health'] as bool? ?? true,
      language: json['language'] as String? ?? 'ar',
      location: json['location'] != null
          ? AdvisoryLocation.fromJson(json['location'] as Map<String, dynamic>)
          : null,
      additionalContext: json['additional_context'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
    );
  }

  /// Copy with
  AdvisoryRequest copyWith({
    String? id,
    AdvisoryRequestType? type,
    String? query,
    String? fieldId,
    String? fieldName,
    String? cropType,
    AdvisoryType? focusArea,
    String? imagePath,
    bool? includeWeather,
    bool? includeSoil,
    bool? includeCropHealth,
    String? language,
    AdvisoryLocation? location,
    Map<String, dynamic>? additionalContext,
    DateTime? createdAt,
  }) {
    return AdvisoryRequest(
      id: id ?? this.id,
      type: type ?? this.type,
      query: query ?? this.query,
      fieldId: fieldId ?? this.fieldId,
      fieldName: fieldName ?? this.fieldName,
      cropType: cropType ?? this.cropType,
      focusArea: focusArea ?? this.focusArea,
      imagePath: imagePath ?? this.imagePath,
      includeWeather: includeWeather ?? this.includeWeather,
      includeSoil: includeSoil ?? this.includeSoil,
      includeCropHealth: includeCropHealth ?? this.includeCropHealth,
      language: language ?? this.language,
      location: location ?? this.location,
      additionalContext: additionalContext ?? this.additionalContext,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  /// Check if request requires image upload
  bool get requiresImage => type == AdvisoryRequestType.diagnosis;

  /// Get request type label in Arabic
  String get typeAr {
    switch (type) {
      case AdvisoryRequestType.question:
        return 'سؤال';
      case AdvisoryRequestType.diagnosis:
        return 'تشخيص';
      case AdvisoryRequestType.recommendation:
        return 'توصية';
      case AdvisoryRequestType.analysis:
        return 'تحليل';
    }
  }

  @override
  String toString() => 'AdvisoryRequest($type: $query)';
}

/// Location model for advisory context
/// نموذج الموقع للسياق
@immutable
class AdvisoryLocation {
  final double latitude;
  final double longitude;
  final String? name;
  final String? nameAr;

  const AdvisoryLocation({
    required this.latitude,
    required this.longitude,
    this.name,
    this.nameAr,
  });

  factory AdvisoryLocation.fromJson(Map<String, dynamic> json) {
    return AdvisoryLocation(
      latitude: (json['latitude'] as num).toDouble(),
      longitude: (json['longitude'] as num).toDouble(),
      name: json['name'] as String?,
      nameAr: json['name_ar'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
    'latitude': latitude,
    'longitude': longitude,
    'name': name,
    'name_ar': nameAr,
  };
}

/// Quick question template
/// قالب سؤال سريع
@immutable
class QuickQuestion {
  final String id;
  final String textEn;
  final String textAr;
  final AdvisoryRequestType type;
  final AdvisoryType? focusArea;
  final String icon;

  const QuickQuestion({
    required this.id,
    required this.textEn,
    required this.textAr,
    required this.type,
    this.focusArea,
    required this.icon,
  });

  String getText(String locale) => locale == 'ar' ? textAr : textEn;

  /// Predefined quick questions
  static const List<QuickQuestion> predefined = [
    QuickQuestion(
      id: 'irrigation_when',
      textEn: 'When should I irrigate?',
      textAr: 'متى أسقي؟',
      type: AdvisoryRequestType.recommendation,
      focusArea: AdvisoryType.irrigation,
      icon: 'water_drop',
    ),
    QuickQuestion(
      id: 'fertilizer_what',
      textEn: 'What fertilizer do I need?',
      textAr: 'ما السماد المناسب؟',
      type: AdvisoryRequestType.recommendation,
      focusArea: AdvisoryType.fertilization,
      icon: 'compost',
    ),
    QuickQuestion(
      id: 'crop_health',
      textEn: 'Is my crop healthy?',
      textAr: 'هل محصولي سليم؟',
      type: AdvisoryRequestType.analysis,
      focusArea: AdvisoryType.diseaseControl,
      icon: 'healing',
    ),
    QuickQuestion(
      id: 'harvest_time',
      textEn: 'When should I harvest?',
      textAr: 'متى موعد الحصاد؟',
      type: AdvisoryRequestType.recommendation,
      focusArea: AdvisoryType.harvest,
      icon: 'agriculture',
    ),
    QuickQuestion(
      id: 'pest_problem',
      textEn: 'How to control pests?',
      textAr: 'كيف أكافح الآفات؟',
      type: AdvisoryRequestType.recommendation,
      focusArea: AdvisoryType.pestControl,
      icon: 'pest_control',
    ),
    QuickQuestion(
      id: 'weather_impact',
      textEn: 'How will weather affect my crop?',
      textAr: 'كيف سيؤثر الطقس على محصولي؟',
      type: AdvisoryRequestType.analysis,
      focusArea: AdvisoryType.weather,
      icon: 'cloud',
    ),
  ];
}

// Helper class for default DateTime
class _DefaultDateTime implements DateTime {
  const _DefaultDateTime();

  @override
  dynamic noSuchMethod(Invocation invocation) => DateTime.now();
}

// Helper functions

AdvisoryRequestType _parseRequestType(String? type) {
  switch (type?.toLowerCase()) {
    case 'diagnosis':
      return AdvisoryRequestType.diagnosis;
    case 'recommendation':
      return AdvisoryRequestType.recommendation;
    case 'analysis':
      return AdvisoryRequestType.analysis;
    case 'question':
    default:
      return AdvisoryRequestType.question;
  }
}

AdvisoryType _parseFocusArea(String focus) {
  switch (focus.toLowerCase()) {
    case 'irrigation':
      return AdvisoryType.irrigation;
    case 'fertilization':
    case 'fertilizer':
      return AdvisoryType.fertilization;
    case 'pest_control':
    case 'pestcontrol':
      return AdvisoryType.pestControl;
    case 'disease_control':
    case 'diseasecontrol':
      return AdvisoryType.diseaseControl;
    case 'harvest':
      return AdvisoryType.harvest;
    case 'planting':
      return AdvisoryType.planting;
    case 'weather':
      return AdvisoryType.weather;
    default:
      return AdvisoryType.general;
  }
}

String _getDefaultQuery(AdvisoryType type) {
  switch (type) {
    case AdvisoryType.irrigation:
      return 'متى وكم يجب أن أروي؟';
    case AdvisoryType.fertilization:
      return 'ما السماد المناسب وكم الكمية؟';
    case AdvisoryType.pestControl:
      return 'كيف أكافح الآفات؟';
    case AdvisoryType.diseaseControl:
      return 'كيف أعالج الأمراض؟';
    case AdvisoryType.harvest:
      return 'متى موعد الحصاد المثالي؟';
    case AdvisoryType.planting:
      return 'متى وكيف أزرع؟';
    case AdvisoryType.weather:
      return 'ما تأثير الطقس على المحصول؟';
    case AdvisoryType.general:
      return 'أريد نصيحة زراعية';
  }
}
