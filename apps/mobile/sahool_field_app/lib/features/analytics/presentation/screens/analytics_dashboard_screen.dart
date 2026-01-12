/// Analytics Dashboard Screen - Main Analytics View
/// شاشة لوحة تحكم التحليلات - العرض الرئيسي للتحليلات
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../data/models/analytics_models.dart';
import '../providers/analytics_providers.dart';
import '../widgets/health_score_card.dart';
import '../widgets/risk_indicator.dart';
import '../widgets/yield_prediction_card.dart';
import '../widgets/trend_chart.dart';

/// Main analytics dashboard screen
/// شاشة لوحة تحكم التحليلات الرئيسية
class AnalyticsDashboardScreen extends ConsumerStatefulWidget {
  final String? fieldId;
  final String? fieldName;

  const AnalyticsDashboardScreen({
    super.key,
    this.fieldId,
    this.fieldName,
  });

  @override
  ConsumerState<AnalyticsDashboardScreen> createState() => _AnalyticsDashboardScreenState();
}

class _AnalyticsDashboardScreenState extends ConsumerState<AnalyticsDashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);

    // Load initial data
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadData();
    });
  }

  void _loadData() {
    if (widget.fieldId != null) {
      ref.read(analyticsDashboardProvider.notifier).loadFieldAnalytics(
            fieldId: widget.fieldId!,
            fieldName: widget.fieldName ?? 'الحقل',
            ndvi: 0.65,
            soilMoisture: 55,
            temperature: 28,
            humidity: 45,
            cropType: 'wheat',
            fieldArea: 2.5,
            rainfall: 15,
          );
    }
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(analyticsDashboardProvider);
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return Scaffold(
      appBar: AppBar(
        title: Text(
          isRtl ? 'التحليلات التنبؤية' : 'Predictive Analytics',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: state.isLoading ? null : _loadData,
            tooltip: isRtl ? 'تحديث' : 'Refresh',
          ),
          IconButton(
            icon: const Icon(Icons.compare_arrows),
            onPressed: () => _showComparisonDialog(context),
            tooltip: isRtl ? 'مقارنة الحقول' : 'Compare Fields',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          tabs: [
            Tab(
              icon: const Icon(Icons.health_and_safety),
              text: isRtl ? 'الصحة' : 'Health',
            ),
            Tab(
              icon: const Icon(Icons.trending_up),
              text: isRtl ? 'الإنتاجية' : 'Yield',
            ),
            Tab(
              icon: const Icon(Icons.warning_amber),
              text: isRtl ? 'المخاطر' : 'Risks',
            ),
          ],
        ),
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : state.error != null
              ? _buildErrorView(state.error!, isRtl)
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildHealthTab(state, theme, isRtl),
                    _buildYieldTab(state, theme, isRtl),
                    _buildRisksTab(state, theme, isRtl),
                  ],
                ),
    );
  }

  Widget _buildErrorView(String error, bool isRtl) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              isRtl ? 'حدث خطأ' : 'An error occurred',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(error, textAlign: TextAlign.center),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _loadData,
              icon: const Icon(Icons.refresh),
              label: Text(isRtl ? 'إعادة المحاولة' : 'Retry'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthTab(AnalyticsDashboardState state, ThemeData theme, bool isRtl) {
    final health = state.selectedFieldHealth;

    if (health == null) {
      return Center(
        child: Text(isRtl ? 'لا توجد بيانات' : 'No data available'),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => _loadData(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Overall Health Score
            HealthScoreCard(
              score: health.overallScore,
              status: health.status,
              statusNameAr: health.statusNameAr,
              trend: health.trend,
            ),

            const SizedBox(height: 24),

            // Health Components
            Text(
              isRtl ? 'مكونات الصحة' : 'Health Components',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),

            _buildHealthMetricsGrid(health, isRtl),

            const SizedBox(height: 24),

            // Recommendations
            if (health.recommendations.isNotEmpty) ...[
              Text(
                isRtl ? 'التوصيات' : 'Recommendations',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              ...health.recommendations.map((rec) => _buildRecommendationCard(rec, isRtl)),
            ],

            const SizedBox(height: 24),

            // Trend Chart
            Text(
              isRtl ? 'اتجاه الصحة' : 'Health Trend',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            const SizedBox(
              height: 200,
              child: TrendChart(
                metricName: 'health_score',
                fieldId: 'current',
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthMetricsGrid(FieldHealthScore health, bool isRtl) {
    final metrics = [
      _MetricData(
        name: isRtl ? 'الغطاء النباتي' : 'Vegetation',
        value: health.ndviScore,
        icon: Icons.grass,
        color: Colors.green,
      ),
      _MetricData(
        name: isRtl ? 'صحة التربة' : 'Soil Health',
        value: health.soilHealthScore,
        icon: Icons.terrain,
        color: Colors.brown,
      ),
      _MetricData(
        name: isRtl ? 'الإجهاد المائي' : 'Water Stress',
        value: health.waterStressScore,
        icon: Icons.water_drop,
        color: Colors.blue,
      ),
      _MetricData(
        name: isRtl ? 'مخاطر الآفات' : 'Pest Risk',
        value: health.pestRiskScore,
        icon: Icons.bug_report,
        color: Colors.orange,
      ),
      _MetricData(
        name: isRtl ? 'العناصر الغذائية' : 'Nutrients',
        value: health.nutrientScore,
        icon: Icons.science,
        color: Colors.purple,
      ),
    ];

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1.5,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: metrics.length,
      itemBuilder: (context, index) {
        final metric = metrics[index];
        return _buildMetricCard(metric);
      },
    );
  }

  Widget _buildMetricCard(_MetricData metric) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(metric.icon, color: metric.color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    metric.name,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const Spacer(),
            Row(
              children: [
                Expanded(
                  child: LinearProgressIndicator(
                    value: metric.value / 100,
                    backgroundColor: metric.color.withOpacity(0.2),
                    valueColor: AlwaysStoppedAnimation(metric.color),
                  ),
                ),
                const SizedBox(width: 8),
                Text(
                  '${metric.value.toStringAsFixed(0)}%',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: metric.color,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationCard(HealthRecommendation rec, bool isRtl) {
    final priorityColors = {
      RecommendationPriority.critical: Colors.red,
      RecommendationPriority.high: Colors.orange,
      RecommendationPriority.medium: Colors.amber,
      RecommendationPriority.low: Colors.green,
    };

    final priorityNames = {
      RecommendationPriority.critical: isRtl ? 'حرج' : 'Critical',
      RecommendationPriority.high: isRtl ? 'عالي' : 'High',
      RecommendationPriority.medium: isRtl ? 'متوسط' : 'Medium',
      RecommendationPriority.low: isRtl ? 'منخفض' : 'Low',
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: priorityColors[rec.priority]?.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getRecommendationIcon(rec.type),
            color: priorityColors[rec.priority],
          ),
        ),
        title: Text(
          isRtl ? rec.titleAr : rec.title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(isRtl ? rec.descriptionAr : rec.description),
        trailing: Chip(
          label: Text(
            priorityNames[rec.priority] ?? '',
            style: TextStyle(
              color: priorityColors[rec.priority],
              fontSize: 10,
            ),
          ),
          backgroundColor: priorityColors[rec.priority]?.withOpacity(0.1),
          side: BorderSide.none,
        ),
      ),
    );
  }

  IconData _getRecommendationIcon(RecommendationType type) {
    switch (type) {
      case RecommendationType.irrigation:
        return Icons.water_drop;
      case RecommendationType.fertilizer:
        return Icons.science;
      case RecommendationType.pestControl:
        return Icons.bug_report;
      case RecommendationType.harvest:
        return Icons.agriculture;
      case RecommendationType.planting:
        return Icons.spa;
      case RecommendationType.general:
        return Icons.lightbulb;
    }
  }

  Widget _buildYieldTab(AnalyticsDashboardState state, ThemeData theme, bool isRtl) {
    final yield = state.selectedYieldPrediction;

    if (yield == null) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.agriculture, size: 64, color: Colors.grey),
            const SizedBox(height: 16),
            Text(
              isRtl ? 'حدد نوع المحصول ومساحة الحقل' : 'Select crop type and field area',
              style: const TextStyle(color: Colors.grey),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => _loadData(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Yield Prediction Card
            YieldPredictionCard(prediction: yield),

            const SizedBox(height: 24),

            // Confidence Indicator
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isRtl ? 'مستوى الثقة' : 'Confidence Level',
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(
                          child: LinearProgressIndicator(
                            value: yield.confidence,
                            backgroundColor: Colors.grey.shade200,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Text(
                          '${(yield.confidence * 100).toStringAsFixed(0)}%',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Yield Factors
            if (yield.factors.isNotEmpty) ...[
              Text(
                isRtl ? 'العوامل المؤثرة' : 'Impact Factors',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              ...yield.factors.map((factor) => _buildFactorCard(factor, isRtl)),
            ],

            const SizedBox(height: 24),

            // Yield Range Chart
            Text(
              isRtl ? 'نطاق الإنتاجية المتوقع' : 'Expected Yield Range',
              style: theme.textTheme.titleLarge?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 12),
            SizedBox(
              height: 200,
              child: _buildYieldRangeChart(yield),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFactorCard(YieldFactor factor, bool isRtl) {
    final isPositive = factor.impact >= 0;
    final color = isPositive ? Colors.green : Colors.red;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(
          isPositive ? Icons.arrow_upward : Icons.arrow_downward,
          color: color,
        ),
        title: Text(
          isRtl ? factor.nameAr : factor.name,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(isRtl ? factor.descriptionAr : factor.description),
        trailing: Text(
          '${isPositive ? '+' : ''}${(factor.impact * 100).toStringAsFixed(0)}%',
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
      ),
    );
  }

  Widget _buildYieldRangeChart(YieldPrediction yield) {
    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.center,
        maxY: yield.maxYield * 1.1,
        barGroups: [
          BarChartGroupData(
            x: 0,
            barRods: [
              BarChartRodData(
                toY: yield.minYield,
                color: Colors.red.shade300,
                width: 40,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              ),
            ],
          ),
          BarChartGroupData(
            x: 1,
            barRods: [
              BarChartRodData(
                toY: yield.predictedYield,
                color: Colors.green,
                width: 40,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              ),
            ],
          ),
          BarChartGroupData(
            x: 2,
            barRods: [
              BarChartRodData(
                toY: yield.maxYield,
                color: Colors.blue.shade300,
                width: 40,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
              ),
            ],
          ),
        ],
        titlesData: FlTitlesData(
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (value, meta) {
                final labels = ['Min', 'Expected', 'Max'];
                return Padding(
                  padding: const EdgeInsets.only(top: 8),
                  child: Text(
                    labels[value.toInt()],
                    style: const TextStyle(fontSize: 12),
                  ),
                );
              },
            ),
          ),
        ),
        borderData: FlBorderData(show: false),
        gridData: const FlGridData(show: true, drawVerticalLine: false),
      ),
    );
  }

  Widget _buildRisksTab(AnalyticsDashboardState state, ThemeData theme, bool isRtl) {
    final assessment = state.selectedRiskAssessment;

    if (assessment == null) {
      return Center(
        child: Text(isRtl ? 'لا توجد بيانات' : 'No data available'),
      );
    }

    return RefreshIndicator(
      onRefresh: () async => _loadData(),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Overall Risk Score
            RiskIndicator(
              score: assessment.overallRiskScore,
              level: assessment.overallRiskLevel,
            ),

            const SizedBox(height: 24),

            // Risk List
            if (assessment.risks.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Icon(
                        Icons.check_circle,
                        size: 64,
                        color: Colors.green,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        isRtl ? 'لا توجد مخاطر كبيرة' : 'No significant risks',
                        style: theme.textTheme.titleLarge,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        isRtl
                            ? 'حقلك في حالة جيدة. استمر في المراقبة.'
                            : 'Your field is in good condition. Keep monitoring.',
                        textAlign: TextAlign.center,
                        style: const TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              )
            else ...[
              Text(
                isRtl ? 'المخاطر المحددة' : 'Identified Risks',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              ...assessment.risks.map((risk) => _buildRiskCard(risk, isRtl)),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildRiskCard(Risk risk, bool isRtl) {
    final levelColors = {
      RiskLevel.minimal: Colors.green,
      RiskLevel.low: Colors.lightGreen,
      RiskLevel.moderate: Colors.amber,
      RiskLevel.high: Colors.orange,
      RiskLevel.critical: Colors.red,
    };

    final levelNames = {
      RiskLevel.minimal: isRtl ? 'ضئيل' : 'Minimal',
      RiskLevel.low: isRtl ? 'منخفض' : 'Low',
      RiskLevel.moderate: isRtl ? 'متوسط' : 'Moderate',
      RiskLevel.high: isRtl ? 'عالي' : 'High',
      RiskLevel.critical: isRtl ? 'حرج' : 'Critical',
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: levelColors[risk.level]?.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getRiskIcon(risk.type),
            color: levelColors[risk.level],
          ),
        ),
        title: Text(
          isRtl ? risk.nameAr : risk.name,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Row(
          children: [
            Chip(
              label: Text(
                levelNames[risk.level] ?? '',
                style: TextStyle(
                  color: levelColors[risk.level],
                  fontSize: 10,
                ),
              ),
              backgroundColor: levelColors[risk.level]?.withOpacity(0.1),
              side: BorderSide.none,
              padding: EdgeInsets.zero,
            ),
            const SizedBox(width: 8),
            Text(
              '${(risk.probability * 100).toStringAsFixed(0)}% ${isRtl ? 'احتمالية' : 'probability'}',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isRtl ? risk.descriptionAr : risk.description,
                  style: const TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 16),
                Text(
                  isRtl ? 'خطوات التخفيف:' : 'Mitigation Steps:',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 8),
                ...(isRtl ? risk.mitigationStepsAr : risk.mitigationSteps).map(
                  (step) => Padding(
                    padding: const EdgeInsets.only(bottom: 4),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Icon(Icons.check_circle, size: 16, color: Colors.green),
                        const SizedBox(width: 8),
                        Expanded(child: Text(step)),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  IconData _getRiskIcon(RiskType type) {
    switch (type) {
      case RiskType.disease:
        return Icons.coronavirus;
      case RiskType.pest:
        return Icons.bug_report;
      case RiskType.drought:
        return Icons.water_drop_outlined;
      case RiskType.flood:
        return Icons.water;
      case RiskType.frost:
        return Icons.ac_unit;
      case RiskType.heatWave:
        return Icons.thermostat;
      case RiskType.nutrientDeficiency:
        return Icons.science;
      case RiskType.marketPrice:
        return Icons.trending_down;
      case RiskType.other:
        return Icons.warning;
    }
  }

  void _showComparisonDialog(BuildContext context) {
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(isRtl ? 'مقارنة الحقول' : 'Compare Fields'),
        content: Text(
          isRtl
              ? 'حدد حقولاً للمقارنة من قائمة الحقول'
              : 'Select fields to compare from the fields list',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: Text(isRtl ? 'حسناً' : 'OK'),
          ),
        ],
      ),
    );
  }
}

class _MetricData {
  final String name;
  final double value;
  final IconData icon;
  final Color color;

  const _MetricData({
    required this.name,
    required this.value,
    required this.icon,
    required this.color,
  });
}
