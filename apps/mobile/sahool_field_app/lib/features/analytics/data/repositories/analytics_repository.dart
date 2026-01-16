/// Analytics Repository - Data Access Layer for Predictive Analytics
/// مستودع التحليلات - طبقة الوصول للبيانات للتحليلات التنبؤية
library;

import 'dart:math' as math;
import '../models/analytics_models.dart';

/// Repository for analytics operations
/// مستودع عمليات التحليلات
class AnalyticsRepository {
  // In production, this would use ApiClient for server communication
  // في الإنتاج، سيستخدم ApiClient للتواصل مع الخادم

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
    // Simulate API call delay
    await Future.delayed(const Duration(milliseconds: 500));

    // Calculate component scores
    final ndviScore = _calculateNdviScore(ndvi ?? 0.5);
    final soilHealthScore = _calculateSoilHealthScore(soilMoisture ?? 50);
    final waterStressScore = _calculateWaterStressScore(soilMoisture ?? 50, temperature ?? 25);
    final pestRiskScore = _calculatePestRiskScore(temperature ?? 25, humidity ?? 60);
    final nutrientScore = _calculateNutrientScore(ndvi ?? 0.5);

    // Weighted average for overall score
    final overallScore = (ndviScore * 0.25 +
            soilHealthScore * 0.20 +
            waterStressScore * 0.20 +
            pestRiskScore * 0.15 +
            nutrientScore * 0.20)
        .clamp(0.0, 100.0);

    // Generate recommendations based on scores
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
    await Future.delayed(const Duration(milliseconds: 500));

    // Base yields for Yemen crops (kg/hectare)
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

    final baseYield = baseYields[cropType] ?? 2000.0;
    final cropTypeAr = cropNamesAr[cropType] ?? cropType;

    // Adjust based on NDVI and conditions
    final ndviFactor = ndvi != null ? (ndvi * 0.5 + 0.5) : 0.8;
    final moistureFactor = soilMoisture != null ? (soilMoisture / 100 * 0.3 + 0.7) : 0.85;

    final predictedYieldPerHa = baseYield * ndviFactor * moistureFactor;
    final totalYield = predictedYieldPerHa * fieldAreaHectares;

    // Calculate variance
    final variance = predictedYieldPerHa * 0.15;
    final minYield = (predictedYieldPerHa - variance) * fieldAreaHectares;
    final maxYield = (predictedYieldPerHa + variance) * fieldAreaHectares;

    // Estimate harvest date
    final harvestDate = DateTime.now().add(Duration(days: daysToHarvest ?? 90));

    // Price estimates (YER per kg)
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

    final pricePerKg = prices[cropType] ?? 500.0;
    final revenueEstimate = totalYield * pricePerKg;

    // Generate yield factors
    final factors = <YieldFactor>[
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
    ];

    return YieldPrediction(
      fieldId: fieldId,
      cropType: cropType,
      cropTypeAr: cropTypeAr,
      predictedYield: totalYield,
      minYield: minYield,
      maxYield: maxYield,
      confidence: 0.75 + (ndvi ?? 0.5) * 0.2,
      harvestDate: harvestDate,
      revenueEstimate: revenueEstimate,
      factors: factors,
      calculatedAt: DateTime.now(),
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
    await Future.delayed(const Duration(milliseconds: 500));

    final risks = <Risk>[];
    double totalRiskScore = 0;

    // Drought risk
    if (rainfall != null && rainfall < 20) {
      final droughtRisk = Risk(
        id: 'drought_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.drought,
        name: 'Drought Risk',
        nameAr: 'خطر الجفاف',
        description: 'Low rainfall may cause water stress',
        descriptionAr: 'قلة الأمطار قد تسبب إجهاد مائي',
        level: rainfall < 10 ? RiskLevel.high : RiskLevel.moderate,
        probability: 1 - (rainfall / 50).clamp(0.0, 1.0),
        potentialImpact: 70,
        mitigationSteps: [
          'Increase irrigation frequency',
          'Apply mulch to retain moisture',
          'Consider drought-resistant varieties',
        ],
        mitigationStepsAr: [
          'زيادة تكرار الري',
          'استخدام الغطاء للحفاظ على الرطوبة',
          'النظر في الأصناف المقاومة للجفاف',
        ],
      );
      risks.add(droughtRisk);
      totalRiskScore += droughtRisk.probability * droughtRisk.potentialImpact;
    }

    // Heat wave risk
    if (temperature != null && temperature > 35) {
      final heatRisk = Risk(
        id: 'heat_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.heatWave,
        name: 'Heat Stress',
        nameAr: 'إجهاد حراري',
        description: 'High temperatures may damage crops',
        descriptionAr: 'درجات الحرارة العالية قد تضر بالمحاصيل',
        level: temperature > 40 ? RiskLevel.critical : RiskLevel.high,
        probability: ((temperature - 35) / 15).clamp(0.0, 1.0),
        potentialImpact: 60,
        mitigationSteps: [
          'Provide shade where possible',
          'Increase irrigation during peak heat',
          'Avoid field work during midday',
        ],
        mitigationStepsAr: [
          'توفير الظل حيثما أمكن',
          'زيادة الري خلال ذروة الحرارة',
          'تجنب العمل الحقلي في منتصف النهار',
        ],
      );
      risks.add(heatRisk);
      totalRiskScore += heatRisk.probability * heatRisk.potentialImpact;
    }

    // Pest risk based on humidity
    if (humidity != null && humidity > 70) {
      final pestRisk = Risk(
        id: 'pest_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.pest,
        name: 'Pest Outbreak',
        nameAr: 'تفشي الآفات',
        description: 'High humidity increases pest activity',
        descriptionAr: 'الرطوبة العالية تزيد من نشاط الآفات',
        level: humidity > 85 ? RiskLevel.high : RiskLevel.moderate,
        probability: ((humidity - 70) / 30).clamp(0.0, 1.0),
        potentialImpact: 50,
        mitigationSteps: [
          'Scout fields regularly',
          'Apply preventive pesticides',
          'Remove crop residues',
        ],
        mitigationStepsAr: [
          'فحص الحقول بانتظام',
          'تطبيق المبيدات الوقائية',
          'إزالة بقايا المحاصيل',
        ],
      );
      risks.add(pestRisk);
      totalRiskScore += pestRisk.probability * pestRisk.potentialImpact;
    }

    // Disease risk
    if (humidity != null && temperature != null && humidity > 60 && temperature > 20 && temperature < 30) {
      final diseaseRisk = Risk(
        id: 'disease_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.disease,
        name: 'Disease Pressure',
        nameAr: 'ضغط الأمراض',
        description: 'Conditions favor fungal diseases',
        descriptionAr: 'الظروف تفضل الأمراض الفطرية',
        level: RiskLevel.moderate,
        probability: 0.5,
        potentialImpact: 45,
        mitigationSteps: [
          'Apply fungicides preventively',
          'Improve air circulation',
          'Avoid overhead irrigation',
        ],
        mitigationStepsAr: [
          'تطبيق مبيدات الفطريات وقائياً',
          'تحسين دوران الهواء',
          'تجنب الري العلوي',
        ],
      );
      risks.add(diseaseRisk);
      totalRiskScore += diseaseRisk.probability * diseaseRisk.potentialImpact;
    }

    // Nutrient deficiency risk based on NDVI
    if (ndvi != null && ndvi < 0.4) {
      final nutrientRisk = Risk(
        id: 'nutrient_${DateTime.now().millisecondsSinceEpoch}',
        type: RiskType.nutrientDeficiency,
        name: 'Nutrient Deficiency',
        nameAr: 'نقص العناصر الغذائية',
        description: 'Low vegetation indices suggest nutrient issues',
        descriptionAr: 'انخفاض مؤشرات الغطاء النباتي يشير إلى مشاكل غذائية',
        level: ndvi < 0.25 ? RiskLevel.high : RiskLevel.moderate,
        probability: 1 - ndvi,
        potentialImpact: 55,
        mitigationSteps: [
          'Conduct soil test',
          'Apply balanced fertilizer',
          'Consider foliar feeding',
        ],
        mitigationStepsAr: [
          'إجراء تحليل التربة',
          'تطبيق سماد متوازن',
          'النظر في التغذية الورقية',
        ],
      );
      risks.add(nutrientRisk);
      totalRiskScore += nutrientRisk.probability * nutrientRisk.potentialImpact;
    }

    // Normalize overall risk score
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

  /// Get analytics summary for all fields
  /// الحصول على ملخص التحليلات لجميع الحقول
  Future<AnalyticsSummary> getAnalyticsSummary(List<String> fieldIds) async {
    await Future.delayed(const Duration(milliseconds: 500));

    // Simulate aggregated data
    final random = math.Random();
    final healthScores = <FieldHealthScore>[];

    for (int i = 0; i < fieldIds.length; i++) {
      final score = await calculateFieldHealth(
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
        : healthScores.map((s) => s.overallScore).reduce((a, b) => a + b) / healthScores.length;

    final highRiskFields = healthScores.where((s) => s.overallScore < 40).length;
    final needingAttention = healthScores.where((s) => s.overallScore < 60).length;

    return AnalyticsSummary(
      totalFields: fieldIds.length,
      averageHealthScore: avgHealth,
      totalPredictedYield: fieldIds.length * 2500.0,
      totalRevenueEstimate: fieldIds.length * 2500.0 * 600,
      highRiskFields: highRiskFields,
      fieldsNeedingAttention: needingAttention,
      topPerformingFields: healthScores.where((s) => s.overallScore >= 70).take(3).toList(),
      fieldsAtRisk: healthScores.where((s) => s.overallScore < 50).take(3).toList(),
      generatedAt: DateTime.now(),
    );
  }

  /// Get historical trends for a metric
  /// الحصول على الاتجاهات التاريخية لمقياس
  Future<HistoricalTrend> getHistoricalTrend({
    required String fieldId,
    required String metricName,
    required int days,
  }) async {
    await Future.delayed(const Duration(milliseconds: 300));

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

  // Private helper methods

  double _calculateNdviScore(double ndvi) {
    // NDVI ranges from -1 to 1, healthy vegetation: 0.2-0.8
    if (ndvi < 0) return 0;
    if (ndvi < 0.2) return ndvi * 150; // 0-30
    if (ndvi < 0.4) return 30 + (ndvi - 0.2) * 150; // 30-60
    if (ndvi < 0.6) return 60 + (ndvi - 0.4) * 150; // 60-90
    return math.min(90 + (ndvi - 0.6) * 50, 100); // 90-100
  }

  double _calculateSoilHealthScore(double moisture) {
    // Optimal soil moisture: 40-70%
    if (moisture < 20) return moisture * 2;
    if (moisture < 40) return 40 + (moisture - 20) * 1.5;
    if (moisture <= 70) return 100 - ((moisture - 55).abs() * 1.5).clamp(0, 30);
    if (moisture <= 85) return 70 - (moisture - 70) * 2;
    return math.max(40 - (moisture - 85) * 2, 10);
  }

  double _calculateWaterStressScore(double moisture, double temperature) {
    // Higher temps need more moisture
    final idealMoisture = 40 + (temperature - 20) * 0.8;
    final deviation = (moisture - idealMoisture).abs();
    return math.max(100 - deviation * 2, 0);
  }

  double _calculatePestRiskScore(double temperature, double humidity) {
    // Pests thrive in warm, humid conditions
    // Return health score (inverse of pest risk)
    final riskFactor = ((temperature - 20) / 20).clamp(0.0, 1.0) *
        ((humidity - 40) / 60).clamp(0.0, 1.0);
    return 100 - (riskFactor * 60); // Higher score = lower pest risk
  }

  double _calculateNutrientScore(double ndvi) {
    // Low NDVI often indicates nutrient deficiency
    return (ndvi * 120).clamp(0.0, 100.0);
  }

  HealthTrend _determineTrend(double score) {
    // In real implementation, compare with historical data
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
        description: 'Water stress detected. Consider adjusting irrigation schedule.',
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
        descriptionAr: 'تم اكتشاف نقص في العناصر الغذائية. قم بتطبيق سماد متوازن.',
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

  void dispose() {
    // Clean up any resources
  }
}
