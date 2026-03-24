/// SAHOOL ML Service - خدمة التعلم الآلي
///
/// Provides on-device ML inference capabilities for agricultural use cases.
/// Delegates heavy computation to backend services but supports lightweight
/// local inference for offline scenarios.
///
/// Features:
/// - Crop disease classification (image-based)
/// - NDVI health prediction from sensor data
/// - Irrigation timing prediction
/// - Offline model caching
library;


import 'package:flutter_riverpod/flutter_riverpod.dart';

/// ML prediction result
/// نتيجة التنبؤ بالتعلم الآلي
class MlPrediction {
  final String label;
  final String labelAr;
  final double confidence;
  final Map<String, dynamic> metadata;

  const MlPrediction({
    required this.label,
    required this.labelAr,
    required this.confidence,
    this.metadata = const {},
  });

  factory MlPrediction.fromJson(Map<String, dynamic> json) => MlPrediction(
        label: json['label'] as String? ?? '',
        labelAr: json['label_ar'] as String? ?? '',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        metadata: json['metadata'] as Map<String, dynamic>? ?? {},
      );

  Map<String, dynamic> toJson() => {
        'label': label,
        'label_ar': labelAr,
        'confidence': confidence,
        'metadata': metadata,
      };

  bool get isHighConfidence => confidence >= 0.8;
  bool get isMediumConfidence => confidence >= 0.5 && confidence < 0.8;
  bool get isLowConfidence => confidence < 0.5;
}

/// Disease detection result from image analysis
/// نتيجة اكتشاف المرض من تحليل الصورة
class DiseaseDetectionResult {
  final String diseaseName;
  final String diseaseNameAr;
  final double confidence;
  final String severity; // mild, moderate, severe
  final List<String> recommendations;
  final List<String> recommendationsAr;
  final String? affectedArea;

  const DiseaseDetectionResult({
    required this.diseaseName,
    required this.diseaseNameAr,
    required this.confidence,
    required this.severity,
    this.recommendations = const [],
    this.recommendationsAr = const [],
    this.affectedArea,
  });

  factory DiseaseDetectionResult.fromJson(Map<String, dynamic> json) =>
      DiseaseDetectionResult(
        diseaseName: json['disease_name'] as String? ?? 'Unknown',
        diseaseNameAr: json['disease_name_ar'] as String? ?? 'غير معروف',
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        severity: json['severity'] as String? ?? 'unknown',
        recommendations:
            (json['recommendations'] as List?)?.cast<String>() ?? [],
        recommendationsAr:
            (json['recommendations_ar'] as List?)?.cast<String>() ?? [],
        affectedArea: json['affected_area'] as String?,
      );
}

/// Irrigation prediction result
/// نتيجة التنبؤ بالري
class IrrigationPrediction {
  final bool shouldIrrigate;
  final double recommendedAmountMm;
  final DateTime? optimalTime;
  final double confidence;
  final String reason;
  final String reasonAr;

  const IrrigationPrediction({
    required this.shouldIrrigate,
    required this.recommendedAmountMm,
    this.optimalTime,
    required this.confidence,
    required this.reason,
    required this.reasonAr,
  });

  factory IrrigationPrediction.fromJson(Map<String, dynamic> json) =>
      IrrigationPrediction(
        shouldIrrigate: json['should_irrigate'] as bool? ?? false,
        recommendedAmountMm:
            (json['recommended_amount_mm'] as num?)?.toDouble() ?? 0.0,
        optimalTime: json['optimal_time'] != null
            ? DateTime.tryParse(json['optimal_time'] as String)
            : null,
        confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
        reason: json['reason'] as String? ?? '',
        reasonAr: json['reason_ar'] as String? ?? '',
      );
}

/// NDVI health classification from sensor data
/// تصنيف صحة NDVI من بيانات الاستشعار
enum NdviHealthClass {
  healthy('Healthy', 'صحي', 0.6),
  moderate('Moderate', 'معتدل', 0.4),
  stressed('Stressed', 'مجهد', 0.2),
  critical('Critical', 'حرج', 0.0);

  final String label;
  final String labelAr;
  final double minNdvi;

  const NdviHealthClass(this.label, this.labelAr, this.minNdvi);

  static NdviHealthClass fromNdvi(double ndvi) {
    if (ndvi >= 0.6) return healthy;
    if (ndvi >= 0.4) return moderate;
    if (ndvi >= 0.2) return stressed;
    return critical;
  }
}

/// ML Service for agricultural predictions
/// خدمة التعلم الآلي للتنبؤات الزراعية
class MlService {
  final Map<String, List<MlPrediction>> _cache = {};
  static const int _maxCacheSize = 50;

  /// Classify crop health from NDVI and sensor readings
  /// تصنيف صحة المحصول من قراءات NDVI والاستشعار
  NdviHealthClass classifyHealth({
    required double ndvi,
    double? soilMoisture,
    double? temperature,
  }) {
    var adjustedNdvi = ndvi;

    // Adjust NDVI based on environmental factors
    if (soilMoisture != null && soilMoisture < 20.0) {
      adjustedNdvi -= 0.05; // Low moisture penalty
    }
    if (temperature != null && temperature > 45.0) {
      adjustedNdvi -= 0.03; // Heat stress penalty
    }

    return NdviHealthClass.fromNdvi(adjustedNdvi.clamp(0.0, 1.0));
  }

  /// Predict irrigation need from sensor data (offline capable)
  /// التنبؤ بالحاجة للري من بيانات الاستشعار (يعمل بدون إنترنت)
  IrrigationPrediction predictIrrigation({
    required double soilMoisture,
    required double fieldCapacity,
    required double wiltingPoint,
    required double cropKc,
    double? et0,
  }) {
    const mad = 0.5; // Management Allowable Depletion
    final threshold = wiltingPoint + (fieldCapacity - wiltingPoint) * (1 - mad);
    final shouldIrrigate = soilMoisture <= threshold;

    double recommendedMm = 0;
    if (shouldIrrigate) {
      recommendedMm = (fieldCapacity - soilMoisture) * 10; // Convert to mm
    }

    final effectiveEt = (et0 ?? 5.0) * cropKc;
    final confidence = soilMoisture < wiltingPoint ? 0.95 : 0.8;

    return IrrigationPrediction(
      shouldIrrigate: shouldIrrigate,
      recommendedAmountMm: recommendedMm,
      confidence: confidence,
      reason: shouldIrrigate
          ? 'Soil moisture ($soilMoisture%) below threshold ($threshold%). '
              'ETc: ${effectiveEt.toStringAsFixed(1)} mm/day.'
          : 'Soil moisture adequate at $soilMoisture%.',
      reasonAr: shouldIrrigate
          ? 'رطوبة التربة ($soilMoisture%) أقل من الحد ($threshold%). '
              'التبخر: ${effectiveEt.toStringAsFixed(1)} مم/يوم.'
          : 'رطوبة التربة كافية عند $soilMoisture%.',
    );
  }

  /// Cache a prediction result
  void _cacheResult(String key, MlPrediction prediction) {
    _cache.putIfAbsent(key, () => []);
    _cache[key]!.add(prediction);
    if (_cache.length > _maxCacheSize) {
      _cache.remove(_cache.keys.first);
    }
  }

  /// Get cached predictions
  List<MlPrediction>? getCached(String key) => _cache[key];

  /// Clear prediction cache
  void clearCache() => _cache.clear();
}

/// Riverpod provider for ML service
final mlServiceProvider = Provider<MlService>((ref) => MlService());
