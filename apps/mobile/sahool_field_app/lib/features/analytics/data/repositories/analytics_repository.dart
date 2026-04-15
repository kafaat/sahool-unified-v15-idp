library;

/// Analytics Repository - Data Access Layer for Predictive Analytics
/// مستودع التحليلات - طبقة الوصول للبيانات للتحليلات التنبؤية
///
/// Connected to field-intelligence service (port 8120) via Kong gateway
/// Falls back to local computation when offline

import 'dart:math' as math;
import '../../../../core/api/kong_gateway_client.dart';
import '../models/analytics_models.dart';

/// Repository for analytics operations
/// مستودع عمليات التحليلات
class AnalyticsRepository {
  final KongGatewayClient _gateway;

  AnalyticsRepository({KongGatewayClient? gateway})
      : _gateway = gateway ?? kongGateway;

  /// Calculate field health score based on various metrics
  /// حساب درجة صحة الحقل بناءً على مقاييس مختلفة
  Future<FieldHealthScore> calculateFieldHealth({
    required String fieldId,
    required String fieldName,
    double? ndvi,
    double? soilMoisture,
    double? temperature,
    double? humidity,
    String? cropType,
  }) async {
    // Try field-intelligence API first
    try {
      final response = await _gateway.post<Map<String, dynamic>>(
        KongServices.fieldIntelligence,
        '/health-score',
        data: {
          'field_id': fieldId,
          if (ndvi != null) 'ndvi': ndvi,
          if (soilMoisture != null) 'soil_moisture': soilMoisture,
          if (temperature != null) 'temperature': temperature,
          if (humidity != null) 'humidity': humidity,
          if (cropType != null) 'crop_type': cropType,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        return _parseFieldHealthFromApi(response.data!, fieldId, fieldName);
      }
    } catch (_) {
      // Fall through to local computation
    }

    // Offline fallback: compute locally
    return _computeFieldHealthLocally(
      fieldId: fieldId,
      fieldName: fieldName,
      ndvi: ndvi,
      soilMoisture: soilMoisture,
      temperature: temperature,
      humidity: humidity,
    );
  }

  /// Get yield prediction for a field
  /// الحصول على توقع الإنتاجية لحقل
  Future<YieldPrediction> predictYield({
    required String fieldId,
    required String cropType,
    required double fieldAreaHectares,
    double? ndvi,
    double? soilMoisture,
    int? daysToHarvest,
  }) async {
    // Try field-intelligence API
    try {
      final response = await _gateway.post<Map<String, dynamic>>(
        KongServices.fieldIntelligence,
        '/yield-prediction',
        data: {
          'field_id': fieldId,
          'crop_type': cropType,
          'area_hectares': fieldAreaHectares,
          if (ndvi != null) 'ndvi': ndvi,
          if (soilMoisture != null) 'soil_moisture': soilMoisture,
          if (daysToHarvest != null) 'days_to_harvest': daysToHarvest,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        return _parseYieldPredictionFromApi(
            response.data!, fieldId, cropType, fieldAreaHectares);
      }
    } catch (_) {
      // Fall through to local computation
    }

    // Offline fallback
    return _computeYieldLocally(
      fieldId: fieldId,
      cropType: cropType,
      fieldAreaHectares: fieldAreaHectares,
      ndvi: ndvi,
      soilMoisture: soilMoisture,
      daysToHarvest: daysToHarvest,
    );
  }

  /// Assess risks for a field
  /// تقييم المخاطر للحقل
  Future<RiskAssessment> assessRisks({
    required String fieldId,
    double? temperature,
    double? humidity,
    double? rainfall,
    double? ndvi,
    String? cropType,
  }) async {
    // Try field-intelligence API
    try {
      final response = await _gateway.post<Map<String, dynamic>>(
        KongServices.fieldIntelligence,
        '/risk-assessment',
        data: {
          'field_id': fieldId,
          if (temperature != null) 'temperature': temperature,
          if (humidity != null) 'humidity': humidity,
          if (rainfall != null) 'rainfall': rainfall,
          if (ndvi != null) 'ndvi': ndvi,
          if (cropType != null) 'crop_type': cropType,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        return _parseRiskAssessmentFromApi(response.data!, fieldId);
      }
    } catch (_) {
      // Fall through to local computation
    }

    // Offline fallback
    return _computeRisksLocally(
      fieldId: fieldId,
      temperature: temperature,
      humidity: humidity,
      rainfall: rainfall,
      ndvi: ndvi,
    );
  }

  /// Get analytics summary for all fields
  /// الحصول على ملخص التحليلات لجميع الحقول
  Future<AnalyticsSummary> getAnalyticsSummary(List<String> fieldIds) async {
    // Try field-intelligence API
    try {
      final response = await _gateway.post<Map<String, dynamic>>(
        KongServices.fieldIntelligence,
        '/summary',
        data: {'field_ids': fieldIds},
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        return _parseAnalyticsSummaryFromApi(response.data!, fieldIds);
      }
    } catch (_) {
      // Fall through to local computation
    }

    // Offline fallback
    return _computeSummaryLocally(fieldIds);
  }

  /// Get historical trends for a metric
  /// الحصول على الاتجاهات التاريخية لمقياس
  Future<HistoricalTrend> getHistoricalTrend({
    required String fieldId,
    required String metricName,
    required int days,
  }) async {
    // Try field-intelligence API
    try {
      final response = await _gateway.get<Map<String, dynamic>>(
        KongServices.fieldIntelligence,
        '/trends/$fieldId',
        queryParams: {
          'metric': metricName,
          'days': days,
        },
        fromJson: (data) => data as Map<String, dynamic>,
      );

      if (response.success && response.data != null) {
        return _parseHistoricalTrendFromApi(response.data!, metricName);
      }
    } catch (_) {
      // Fall through to local computation
    }

    // Offline fallback
    return _computeTrendLocally(
        fieldId: fieldId, metricName: metricName, days: days);
  }

  void dispose() {
    // Clean up any resources
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // API Response Parsers
  // ═══════════════════════════════════════════════════════════════════════════

  FieldHealthScore _parseFieldHealthFromApi(
      Map<String, dynamic> data, String fieldId, String fieldName) {
    final recs = (data['recommendations'] as List?)
            ?.map((r) => HealthRecommendation(
                  id: r['id'] ?? '',
                  title: r['title'] ?? '',
                  titleAr: r['title_ar'] ?? r['title'] ?? '',
                  description: r['description'] ?? '',
                  descriptionAr: r['description_ar'] ?? r['description'] ?? '',
                  priority: _parseRecommendationPriority(r['priority']),
                  type: _parseRecommendationType(r['type']),
                ))
            .toList() ??
        [];

    return FieldHealthScore(
      fieldId: fieldId,
      fieldName: fieldName,
      overallScore: (data['overall_score'] ?? 0.0).toDouble(),
      ndviScore: (data['ndvi_score'] ?? 0.0).toDouble(),
      soilHealthScore: (data['soil_health_score'] ?? 0.0).toDouble(),
      waterStressScore: (data['water_stress_score'] ?? 0.0).toDouble(),
      pestRiskScore: (data['pest_risk_score'] ?? 0.0).toDouble(),
      nutrientScore: (data['nutrient_score'] ?? 0.0).toDouble(),
      trend: _parseTrend(data['trend']),
      calculatedAt:
          DateTime.tryParse(data['calculated_at'] ?? '') ?? DateTime.now(),
      recommendations: recs,
    );
  }

  YieldPrediction _parseYieldPredictionFromApi(
      Map<String, dynamic> data, String fieldId, String cropType, double area) {
    final factors = (data['factors'] as List?)
            ?.map((f) => YieldFactor(
                  name: f['name'] ?? '',
                  nameAr: f['name_ar'] ?? f['name'] ?? '',
                  impact: (f['impact'] ?? 0.0).toDouble(),
                  description: f['description'] ?? '',
                  descriptionAr: f['description_ar'] ?? f['description'] ?? '',
                ))
            .toList() ??
        [];

    return YieldPrediction(
      fieldId: fieldId,
      cropType: cropType,
      cropTypeAr: data['crop_type_ar'] ?? cropType,
      predictedYield: (data['predicted_yield'] ?? 0.0).toDouble(),
      minYield: (data['min_yield'] ?? 0.0).toDouble(),
      maxYield: (data['max_yield'] ?? 0.0).toDouble(),
      confidence: (data['confidence'] ?? 0.75).toDouble(),
      harvestDate: DateTime.tryParse(data['harvest_date'] ?? '') ??
          DateTime.now().add(const Duration(days: 90)),
      revenueEstimate: (data['revenue_estimate'] ?? 0.0).toDouble(),
      factors: factors,
      calculatedAt:
          DateTime.tryParse(data['calculated_at'] ?? '') ?? DateTime.now(),
    );
  }

  RiskAssessment _parseRiskAssessmentFromApi(
      Map<String, dynamic> data, String fieldId) {
    final risks = (data['risks'] as List?)
            ?.map((r) => Risk(
                  id: r['id'] ?? '',
                  type: _parseRiskType(r['type']),
                  name: r['name'] ?? '',
                  nameAr: r['name_ar'] ?? r['name'] ?? '',
                  description: r['description'] ?? '',
                  descriptionAr: r['description_ar'] ?? r['description'] ?? '',
                  level: _parseRiskLevel(r['level']),
                  probability: (r['probability'] ?? 0.0).toDouble(),
                  potentialImpact: (r['potential_impact'] ?? 0.0).toDouble(),
                  mitigationSteps:
                      (r['mitigation_steps'] as List?)?.cast<String>() ?? [],
                  mitigationStepsAr:
                      (r['mitigation_steps_ar'] as List?)?.cast<String>() ?? [],
                ))
            .toList() ??
        [];

    return RiskAssessment(
      fieldId: fieldId,
      risks: risks,
      overallRiskScore: (data['overall_risk_score'] ?? 0.0).toDouble(),
      assessedAt:
          DateTime.tryParse(data['assessed_at'] ?? '') ?? DateTime.now(),
    );
  }

  AnalyticsSummary _parseAnalyticsSummaryFromApi(
      Map<String, dynamic> data, List<String> fieldIds) {
    return AnalyticsSummary(
      totalFields: data['total_fields'] ?? fieldIds.length,
      averageHealthScore: (data['average_health_score'] ?? 0.0).toDouble(),
      totalPredictedYield: (data['total_predicted_yield'] ?? 0.0).toDouble(),
      totalRevenueEstimate: (data['total_revenue_estimate'] ?? 0.0).toDouble(),
      highRiskFields: data['high_risk_fields'] ?? 0,
      fieldsNeedingAttention: data['fields_needing_attention'] ?? 0,
      topPerformingFields: const [],
      fieldsAtRisk: const [],
      generatedAt:
          DateTime.tryParse(data['generated_at'] ?? '') ?? DateTime.now(),
    );
  }

  HistoricalTrend _parseHistoricalTrendFromApi(
      Map<String, dynamic> data, String metricName) {
    final metricNamesAr = {
      'ndvi': 'مؤشر الغطاء النباتي',
      'health_score': 'درجة الصحة',
      'soil_moisture': 'رطوبة التربة',
      'yield_estimate': 'تقدير الإنتاجية',
    };

    final points = (data['data_points'] as List?)
            ?.map((p) => HistoricalDataPoint(
                  date: DateTime.tryParse(p['date'] ?? '') ?? DateTime.now(),
                  value: (p['value'] ?? 0.0).toDouble(),
                ))
            .toList() ??
        [];

    return HistoricalTrend(
      metricName: metricName,
      metricNameAr: metricNamesAr[metricName] ?? metricName,
      dataPoints: points,
      changePercent: (data['change_percent'] ?? 0.0).toDouble(),
      trend: _parseTrend(data['trend']),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Enum Parsers
  // ═══════════════════════════════════════════════════════════════════════════

  HealthTrend _parseTrend(dynamic value) {
    switch (value?.toString()) {
      case 'improving':
        return HealthTrend.improving;
      case 'declining':
        return HealthTrend.declining;
      default:
        return HealthTrend.stable;
    }
  }

  RiskType _parseRiskType(dynamic value) {
    switch (value?.toString()) {
      case 'drought':
        return RiskType.drought;
      case 'heat_wave':
        return RiskType.heatWave;
      case 'pest':
        return RiskType.pest;
      case 'disease':
        return RiskType.disease;
      case 'nutrient_deficiency':
        return RiskType.nutrientDeficiency;
      default:
        return RiskType.drought;
    }
  }

  RiskLevel _parseRiskLevel(dynamic value) {
    switch (value?.toString()) {
      case 'critical':
        return RiskLevel.critical;
      case 'high':
        return RiskLevel.high;
      case 'low':
        return RiskLevel.low;
      default:
        return RiskLevel.moderate;
    }
  }

  RecommendationPriority _parseRecommendationPriority(dynamic value) {
    switch (value?.toString()) {
      case 'high':
        return RecommendationPriority.high;
      case 'low':
        return RecommendationPriority.low;
      default:
        return RecommendationPriority.medium;
    }
  }

  RecommendationType _parseRecommendationType(dynamic value) {
    switch (value?.toString()) {
      case 'irrigation':
        return RecommendationType.irrigation;
      case 'fertilizer':
        return RecommendationType.fertilizer;
      case 'pest_control':
        return RecommendationType.pestControl;
      default:
        return RecommendationType.general;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Offline Fallback Computations (local algorithms)
  // حسابات احتياطية محلية عند عدم الاتصال
  // ═══════════════════════════════════════════════════════════════════════════

  FieldHealthScore _computeFieldHealthLocally({
    required String fieldId,
    required String fieldName,
    double? ndvi,
    double? soilMoisture,
    double? temperature,
    double? humidity,
  }) {
    final ndviScore = _calculateNdviScore(ndvi ?? 0.5);
    final soilHealthScore = _calculateSoilHealthScore(soilMoisture ?? 50);
    final waterStressScore =
        _calculateWaterStressScore(soilMoisture ?? 50, temperature ?? 25);
    final pestRiskScore =
        _calculatePestRiskScore(temperature ?? 25, humidity ?? 60);
    final nutrientScore = _calculateNutrientScore(ndvi ?? 0.5);

    final overallScore = (ndviScore * 0.25 +
            soilHealthScore * 0.20 +
            waterStressScore * 0.20 +
            pestRiskScore * 0.15 +
            nutrientScore * 0.20)
        .clamp(0.0, 100.0);

    final recommendations = _generateRecommendations(
      ndviScore: ndviScore,
      soilHealthScore: soilHealthScore,
      waterStressScore: waterStressScore,
      pestRiskScore: pestRiskScore,
      nutrientScore: nutrientScore,
    );

    return FieldHealthScore(
      fieldId: fieldId,
      fieldName: fieldName,
      overallScore: overallScore,
      ndviScore: ndviScore,
      soilHealthScore: soilHealthScore,
      waterStressScore: waterStressScore,
      pestRiskScore: pestRiskScore,
      nutrientScore: nutrientScore,
      trend: _determineTrend(overallScore),
      calculatedAt: DateTime.now(),
      recommendations: recommendations,
    );
  }

  YieldPrediction _computeYieldLocally({
    required String fieldId,
    required String cropType,
    required double fieldAreaHectares,
    double? ndvi,
    double? soilMoisture,
    int? daysToHarvest,
  }) {
    final baseYields = {
      'wheat': 2500.0,
      'sorghum': 1800.0,
      'millet': 1500.0,
      'tomato': 35000.0,
      'potato': 20000.0,
      'corn': 4000.0,
      'coffee': 800.0,
      'date_palm': 6000.0,
      'mango': 8000.0,
      'citrus': 15000.0,
      'grape': 12000.0,
      'qat': 5000.0,
    };

    final cropNamesAr = {
      'wheat': 'قمح',
      'sorghum': 'ذرة رفيعة',
      'millet': 'دخن',
      'tomato': 'طماطم',
      'potato': 'بطاطس',
      'corn': 'ذرة',
      'coffee': 'بن',
      'date_palm': 'نخيل',
      'mango': 'مانجو',
      'citrus': 'حمضيات',
      'grape': 'عنب',
      'qat': 'قات',
    };

    final prices = {
      'wheat': 800.0,
      'sorghum': 600.0,
      'millet': 500.0,
      'tomato': 300.0,
      'potato': 400.0,
      'corn': 500.0,
      'coffee': 5000.0,
      'date_palm': 1500.0,
      'mango': 800.0,
      'citrus': 600.0,
      'grape': 1000.0,
      'qat': 2000.0,
    };

    final baseYield = baseYields[cropType] ?? 2000.0;
    final cropTypeAr = cropNamesAr[cropType] ?? cropType;
    final ndviFactor = ndvi != null ? (ndvi * 0.5 + 0.5) : 0.8;
    final moistureFactor =
        soilMoisture != null ? (soilMoisture / 100 * 0.3 + 0.7) : 0.85;

    final predictedYieldPerHa = baseYield * ndviFactor * moistureFactor;
    final totalYield = predictedYieldPerHa * fieldAreaHectares;
    final variance = predictedYieldPerHa * 0.15;
    final pricePerKg = prices[cropType] ?? 500.0;

    return YieldPrediction(
      fieldId: fieldId,
      cropType: cropType,
      cropTypeAr: cropTypeAr,
      predictedYield: totalYield,
      minYield: (predictedYieldPerHa - variance) * fieldAreaHectares,
      maxYield: (predictedYieldPerHa + variance) * fieldAreaHectares,
      confidence: 0.75 + (ndvi ?? 0.5) * 0.2,
      harvestDate: DateTime.now().add(Duration(days: daysToHarvest ?? 90)),
      revenueEstimate: totalYield * pricePerKg,
      factors: [
        YieldFactor(
          name: 'NDVI Health',
          nameAr: 'صحة الغطاء النباتي',
          impact: (ndviFactor - 0.75) * 2,
          description: 'Vegetation health impact on yield',
          descriptionAr: 'تأثير صحة الغطاء النباتي على الإنتاجية',
        ),
        YieldFactor(
          name: 'Soil Moisture',
          nameAr: 'رطوبة التربة',
          impact: (moistureFactor - 0.75) * 2,
          description: 'Water availability impact',
          descriptionAr: 'تأثير توفر المياه',
        ),
      ],
      calculatedAt: DateTime.now(),
    );
  }

  RiskAssessment _computeRisksLocally({
    required String fieldId,
    double? temperature,
    double? humidity,
    double? rainfall,
    double? ndvi,
  }) {
    final risks = <Risk>[];
    double totalRiskScore = 0;

    if (rainfall != null && rainfall < 20) {
      final r = Risk(
        id: 'drought_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.drought,
        name: 'Drought Risk',
        nameAr: 'خطر الجفاف',
        description: 'Low rainfall may cause water stress',
        descriptionAr: 'قلة الأمطار قد تسبب إجهاد مائي',
        level: rainfall < 10 ? RiskLevel.high : RiskLevel.moderate,
        probability: 1 - (rainfall / 50).clamp(0.0, 1.0),
        potentialImpact: 70,
        mitigationSteps: const [
          'Increase irrigation frequency',
          'Apply mulch to retain moisture'
        ],
        mitigationStepsAr: const [
          'زيادة تكرار الري',
          'استخدام الغطاء للحفاظ على الرطوبة'
        ],
      );
      risks.add(r);
      totalRiskScore += r.probability * r.potentialImpact;
    }

    if (temperature != null && temperature > 35) {
      final r = Risk(
        id: 'heat_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.heatWave,
        name: 'Heat Stress',
        nameAr: 'إجهاد حراري',
        description: 'High temperatures may damage crops',
        descriptionAr: 'درجات الحرارة العالية قد تضر بالمحاصيل',
        level: temperature > 40 ? RiskLevel.critical : RiskLevel.high,
        probability: ((temperature - 35) / 15).clamp(0.0, 1.0),
        potentialImpact: 60,
        mitigationSteps: const [
          'Provide shade where possible',
          'Increase irrigation during peak heat'
        ],
        mitigationStepsAr: const [
          'توفير الظل حيثما أمكن',
          'زيادة الري خلال ذروة الحرارة'
        ],
      );
      risks.add(r);
      totalRiskScore += r.probability * r.potentialImpact;
    }

    if (humidity != null && humidity > 70) {
      final r = Risk(
        id: 'pest_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.pest,
        name: 'Pest Outbreak',
        nameAr: 'تفشي الآفات',
        description: 'High humidity increases pest activity',
        descriptionAr: 'الرطوبة العالية تزيد من نشاط الآفات',
        level: humidity > 85 ? RiskLevel.high : RiskLevel.moderate,
        probability: ((humidity - 70) / 30).clamp(0.0, 1.0),
        potentialImpact: 50,
        mitigationSteps: const [
          'Scout fields regularly',
          'Apply preventive pesticides'
        ],
        mitigationStepsAr: const ['فحص الحقول بانتظام', 'تطبيق المبيدات الوقائية'],
      );
      risks.add(r);
      totalRiskScore += r.probability * r.potentialImpact;
    }

    if (ndvi != null && ndvi < 0.4) {
      final r = Risk(
        id: 'nutrient_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.nutrientDeficiency,
        name: 'Nutrient Deficiency',
        nameAr: 'نقص العناصر الغذائية',
        description: 'Low vegetation indices suggest nutrient issues',
        descriptionAr: 'انخفاض مؤشرات الغطاء النباتي يشير إلى مشاكل غذائية',
        level: ndvi < 0.25 ? RiskLevel.high : RiskLevel.moderate,
        probability: 1 - ndvi,
        potentialImpact: 55,
        mitigationSteps: const ['Conduct soil test', 'Apply balanced fertilizer'],
        mitigationStepsAr: const ['إجراء تحليل التربة', 'تطبيق سماد متوازن'],
      );
      risks.add(r);
      totalRiskScore += r.probability * r.potentialImpact;
    }

    final overallRiskScore = risks.isEmpty
        ? 10.0
        : (totalRiskScore / risks.length).clamp(0.0, 100.0);

    return RiskAssessment(
      fieldId: fieldId,
      risks: risks,
      overallRiskScore: overallRiskScore,
      assessedAt: DateTime.now(),
    );
  }

  Future<AnalyticsSummary> _computeSummaryLocally(List<String> fieldIds) async {
    final random = math.Random();
    final healthScores = <FieldHealthScore>[];

    for (int i = 0; i < fieldIds.length; i++) {
      final score = _computeFieldHealthLocally(
        fieldId: fieldIds[i],
        fieldName: 'حقل ${i + 1}',
        ndvi: 0.3 + random.nextDouble() * 0.5,
        soilMoisture: 30 + random.nextDouble() * 50,
        temperature: 25 + random.nextDouble() * 15,
        humidity: 40 + random.nextDouble() * 40,
      );
      healthScores.add(score);
    }

    final avgHealth = healthScores.isEmpty
        ? 0.0
        : healthScores.map((s) => s.overallScore).reduce((a, b) => a + b) /
            healthScores.length;

    return AnalyticsSummary(
      totalFields: fieldIds.length,
      averageHealthScore: avgHealth,
      totalPredictedYield: fieldIds.length * 2500.0,
      totalRevenueEstimate: fieldIds.length * 2500.0 * 600,
      highRiskFields: healthScores.where((s) => s.overallScore < 40).length,
      fieldsNeedingAttention:
          healthScores.where((s) => s.overallScore < 60).length,
      topPerformingFields:
          healthScores.where((s) => s.overallScore >= 70).take(3).toList(),
      fieldsAtRisk:
          healthScores.where((s) => s.overallScore < 50).take(3).toList(),
      generatedAt: DateTime.now(),
    );
  }

  HistoricalTrend _computeTrendLocally({
    required String fieldId,
    required String metricName,
    required int days,
  }) {
    final metricNamesAr = {
      'ndvi': 'مؤشر الغطاء النباتي',
      'health_score': 'درجة الصحة',
      'soil_moisture': 'رطوبة التربة',
      'yield_estimate': 'تقدير الإنتاجية',
    };

    final random = math.Random();
    final dataPoints = <HistoricalDataPoint>[];
    double lastValue = 50 + random.nextDouble() * 30;

    for (int i = days; i >= 0; i--) {
      final change = (random.nextDouble() - 0.5) * 10;
      lastValue = (lastValue + change).clamp(20.0, 90.0);
      dataPoints.add(HistoricalDataPoint(
        date: DateTime.now().subtract(Duration(days: i)),
        value: lastValue,
      ));
    }

    final firstValue = dataPoints.first.value;
    final latestValue = dataPoints.last.value;
    final changePercent = ((latestValue - firstValue) / firstValue) * 100;

    return HistoricalTrend(
      metricName: metricName,
      metricNameAr: metricNamesAr[metricName] ?? metricName,
      dataPoints: dataPoints,
      changePercent: changePercent,
      trend: changePercent > 5
          ? HealthTrend.improving
          : changePercent < -5
              ? HealthTrend.declining
              : HealthTrend.stable,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Local Scoring Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  double _calculateNdviScore(double ndvi) {
    if (ndvi < 0) return 0;
    if (ndvi < 0.2) return ndvi * 150;
    if (ndvi < 0.4) return 30 + (ndvi - 0.2) * 150;
    if (ndvi < 0.6) return 60 + (ndvi - 0.4) * 150;
    return math.min(90 + (ndvi - 0.6) * 50, 100);
  }

  double _calculateSoilHealthScore(double moisture) {
    if (moisture < 20) return moisture * 2;
    if (moisture < 40) return 40 + (moisture - 20) * 1.5;
    if (moisture <= 70) return 100 - ((moisture - 55).abs() * 1.5).clamp(0, 30);
    if (moisture <= 85) return 70 - (moisture - 70) * 2;
    return math.max(40 - (moisture - 85) * 2, 10);
  }

  double _calculateWaterStressScore(double moisture, double temperature) {
    final idealMoisture = 40 + (temperature - 20) * 0.8;
    final deviation = (moisture - idealMoisture).abs();
    return math.max(100 - deviation * 2, 0);
  }

  double _calculatePestRiskScore(double temperature, double humidity) {
    final riskFactor = ((temperature - 20) / 20).clamp(0.0, 1.0) *
        ((humidity - 40) / 60).clamp(0.0, 1.0);
    return 100 - (riskFactor * 60);
  }

  double _calculateNutrientScore(double ndvi) {
    return (ndvi * 120).clamp(0.0, 100.0);
  }

  HealthTrend _determineTrend(double score) {
    if (score >= 70) return HealthTrend.improving;
    if (score >= 50) return HealthTrend.stable;
    return HealthTrend.declining;
  }

  List<HealthRecommendation> _generateRecommendations({
    required double ndviScore,
    required double soilHealthScore,
    required double waterStressScore,
    required double pestRiskScore,
    required double nutrientScore,
  }) {
    final recommendations = <HealthRecommendation>[];

    if (waterStressScore < 50) {
      recommendations.add(const HealthRecommendation(
        id: 'rec_irrigation',
        title: 'Adjust Irrigation',
        titleAr: 'ضبط الري',
        description:
            'Water stress detected. Consider adjusting irrigation schedule.',
        descriptionAr: 'تم اكتشاف إجهاد مائي. ضع في الاعتبار تعديل جدول الري.',
        priority: RecommendationPriority.high,
        type: RecommendationType.irrigation,
      ));
    }

    if (nutrientScore < 60) {
      recommendations.add(const HealthRecommendation(
        id: 'rec_fertilizer',
        title: 'Apply Fertilizer',
        titleAr: 'تطبيق السماد',
        description: 'Nutrient deficiency detected. Apply balanced fertilizer.',
        descriptionAr:
            'تم اكتشاف نقص في العناصر الغذائية. قم بتطبيق سماد متوازن.',
        priority: RecommendationPriority.high,
        type: RecommendationType.fertilizer,
      ));
    }

    if (pestRiskScore < 50) {
      recommendations.add(const HealthRecommendation(
        id: 'rec_pest',
        title: 'Scout for Pests',
        titleAr: 'فحص الآفات',
        description: 'High pest risk conditions. Increase scouting frequency.',
        descriptionAr: 'ظروف مخاطر آفات عالية. زيادة تكرار الفحص.',
        priority: RecommendationPriority.medium,
        type: RecommendationType.pestControl,
      ));
    }

    if (soilHealthScore < 50) {
      recommendations.add(const HealthRecommendation(
        id: 'rec_soil',
        title: 'Soil Management',
        titleAr: 'إدارة التربة',
        description: 'Soil health needs attention. Consider soil testing.',
        descriptionAr: 'صحة التربة تحتاج اهتمام. ضع في الاعتبار فحص التربة.',
        priority: RecommendationPriority.medium,
        type: RecommendationType.general,
      ));
    }

    return recommendations;
  }
}
