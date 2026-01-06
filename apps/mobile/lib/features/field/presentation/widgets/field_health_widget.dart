import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'dart:math' as math;

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/entities/field.dart';
import '../../../tasks/providers/tasks_provider.dart';

/// Field Health Widget - Comprehensive health score display
/// ويدجت صحة الحقل - عرض شامل لدرجة الصحة
///
/// Features:
/// - Circular progress for overall health score
/// - Four mini indicators (NDVI, irrigation, tasks, weather)
/// - Trend indicator (arrow up/down/stable)
/// - Alert badge with count
/// - Tap to expand for details
/// - Recommendations list with quick actions
/// - Arabic/English support
/// - Dark mode support
class FieldHealthWidget extends ConsumerStatefulWidget {
  final Field field;
  final bool compact;

  const FieldHealthWidget({
    super.key,
    required this.field,
    this.compact = false,
  });

  @override
  ConsumerState<FieldHealthWidget> createState() => _FieldHealthWidgetState();
}

class _FieldHealthWidgetState extends ConsumerState<FieldHealthWidget>
    with SingleTickerProviderStateMixin {
  bool _isExpanded = false;
  late AnimationController _animationController;
  late Animation<double> _expandAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      duration: const Duration(milliseconds: 300),
      vsync: this,
    );
    _expandAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _toggleExpanded() {
    setState(() {
      _isExpanded = !_isExpanded;
      if (_isExpanded) {
        _animationController.forward();
      } else {
        _animationController.reverse();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final healthData = _calculateHealthData(widget.field);

    if (widget.compact) {
      return _buildCompactView(context, isDark, healthData);
    }

    return _buildFullView(context, isDark, healthData);
  }

  Widget _buildFullView(
    BuildContext context,
    bool isDark,
    FieldHealthData healthData,
  ) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: isDark ? SahoolColors.surfaceDark : Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: SahoolShadows.medium,
        border: healthData.hasAlerts
            ? Border.all(color: SahoolColors.warning, width: 2)
            : null,
      ),
      child: Column(
        children: [
          // Main Health Card
          InkWell(
            onTap: _toggleExpanded,
            borderRadius: BorderRadius.circular(20),
            child: Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                children: [
                  Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Circular Progress
                      _buildCircularProgress(healthData, isDark),
                      const SizedBox(width: 20),

                      // Details and Indicators
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            // Title and Alert Badge
                            Row(
                              children: [
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(
                                        'صحة الحقل / Field Health',
                                        style: TextStyle(
                                          fontSize: 12,
                                          color: isDark
                                              ? Colors.grey[400]
                                              : Colors.grey[600],
                                        ),
                                      ),
                                      const SizedBox(height: 4),
                                      Row(
                                        children: [
                                          Text(
                                            healthData.statusArabic,
                                            style: TextStyle(
                                              fontSize: 18,
                                              fontWeight: FontWeight.bold,
                                              color: healthData.color,
                                            ),
                                          ),
                                          const SizedBox(width: 8),
                                          _buildTrendIndicator(healthData),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                if (healthData.alertCount > 0)
                                  _buildAlertBadge(healthData.alertCount),
                              ],
                            ),
                            const SizedBox(height: 16),

                            // Mini Indicators Grid
                            _buildMiniIndicators(healthData, isDark),
                          ],
                        ),
                      ),
                    ],
                  ),

                  // Expand/Collapse Indicator
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _isExpanded
                            ? 'إخفاء التفاصيل / Hide Details'
                            : 'عرض التفاصيل / Show Details',
                        style: TextStyle(
                          fontSize: 12,
                          color: SahoolColors.primary.withOpacity(0.7),
                        ),
                      ),
                      const SizedBox(width: 4),
                      AnimatedRotation(
                        turns: _isExpanded ? 0.5 : 0,
                        duration: const Duration(milliseconds: 300),
                        child: Icon(
                          Icons.keyboard_arrow_down,
                          color: SahoolColors.primary.withOpacity(0.7),
                          size: 20,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Expandable Details Section
          SizeTransition(
            sizeFactor: _expandAnimation,
            child: _buildExpandedDetails(context, healthData, isDark),
          ),
        ],
      ),
    );
  }

  Widget _buildCompactView(
    BuildContext context,
    bool isDark,
    FieldHealthData healthData,
  ) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 4, vertical: 4),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isDark ? SahoolColors.surfaceDark : Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          // Compact Circular Progress
          SizedBox(
            width: 60,
            height: 60,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  width: 60,
                  height: 60,
                  child: CircularProgressIndicator(
                    value: healthData.score / 100,
                    backgroundColor: healthData.color.withOpacity(0.2),
                    valueColor: AlwaysStoppedAnimation<Color>(healthData.color),
                    strokeWidth: 5,
                  ),
                ),
                Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '${healthData.score}',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: healthData.color,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(width: 12),

          // Compact Info
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Text(
                      healthData.statusArabic,
                      style: TextStyle(
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        color: healthData.color,
                      ),
                    ),
                    const SizedBox(width: 4),
                    _buildTrendIndicator(healthData, small: true),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  'NDVI: ${healthData.ndviValue.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 11,
                    color: isDark ? Colors.grey[400] : Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),

          if (healthData.alertCount > 0)
            _buildAlertBadge(healthData.alertCount, small: true),
        ],
      ),
    );
  }

  Widget _buildCircularProgress(FieldHealthData healthData, bool isDark) {
    return SizedBox(
      width: 100,
      height: 100,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          SizedBox(
            width: 100,
            height: 100,
            child: CircularProgressIndicator(
              value: healthData.score / 100,
              backgroundColor: healthData.color.withOpacity(0.2),
              valueColor: AlwaysStoppedAnimation<Color>(healthData.color),
              strokeWidth: 8,
              strokeCap: StrokeCap.round,
            ),
          ),

          // Center content
          Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${healthData.score}',
                style: TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: healthData.color,
                ),
              ),
              Text(
                'درجة',
                style: TextStyle(
                  fontSize: 10,
                  color: isDark ? Colors.grey[400] : Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildTrendIndicator(FieldHealthData healthData, {bool small = false}) {
    IconData icon;
    Color color;

    switch (healthData.trend) {
      case HealthTrend.up:
        icon = Icons.trending_up_rounded;
        color = SahoolColors.success;
        break;
      case HealthTrend.down:
        icon = Icons.trending_down_rounded;
        color = SahoolColors.danger;
        break;
      case HealthTrend.stable:
        icon = Icons.trending_flat_rounded;
        color = SahoolColors.info;
        break;
    }

    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: small ? 4 : 6,
        vertical: small ? 2 : 3,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: small ? 12 : 14, color: color),
          SizedBox(width: small ? 2 : 4),
          Text(
            '${healthData.trendValue > 0 ? '+' : ''}${healthData.trendValue}%',
            style: TextStyle(
              fontSize: small ? 9 : 10,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertBadge(int count, {bool small = false}) {
    return Container(
      padding: EdgeInsets.symmetric(
        horizontal: small ? 6 : 8,
        vertical: small ? 3 : 4,
      ),
      decoration: BoxDecoration(
        color: SahoolColors.danger,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: SahoolColors.danger.withOpacity(0.3),
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.warning_rounded,
            size: small ? 12 : 14,
            color: Colors.white,
          ),
          SizedBox(width: small ? 3 : 4),
          Text(
            '$count',
            style: TextStyle(
              fontSize: small ? 10 : 11,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMiniIndicators(FieldHealthData healthData, bool isDark) {
    return Row(
      children: [
        Expanded(
          child: _buildMiniIndicator(
            icon: Icons.eco_rounded,
            label: 'NDVI',
            value: healthData.ndviValue.toStringAsFixed(2),
            color: healthData.ndviColor,
            isDark: isDark,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildMiniIndicator(
            icon: Icons.water_drop_rounded,
            label: 'ري',
            value: healthData.irrigationStatus,
            color: healthData.irrigationColor,
            isDark: isDark,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildMiniIndicator(
            icon: Icons.task_alt_rounded,
            label: 'مهام',
            value: '${healthData.pendingTasks}',
            color: healthData.tasksColor,
            isDark: isDark,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _buildMiniIndicator(
            icon: Icons.wb_sunny_rounded,
            label: 'طقس',
            value: healthData.weatherStatus,
            color: healthData.weatherColor,
            isDark: isDark,
          ),
        ),
      ],
    );
  }

  Widget _buildMiniIndicator({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
    required bool isDark,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: color.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        children: [
          Icon(icon, size: 20, color: color),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 8,
              color: isDark ? Colors.grey[400] : Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpandedDetails(
    BuildContext context,
    FieldHealthData healthData,
    bool isDark,
  ) {
    return Container(
      padding: const EdgeInsets.fromLTRB(20, 0, 20, 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Divider(height: 1),
          const SizedBox(height: 16),

          // Recommendations Section
          Text(
            'التوصيات / Recommendations',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: isDark ? Colors.white : SahoolColors.textDark,
            ),
          ),
          const SizedBox(height: 12),

          ...healthData.recommendations.map((rec) {
            return _buildRecommendationItem(context, rec, isDark);
          }).toList(),

          if (healthData.recommendations.isEmpty)
            _buildEmptyRecommendations(isDark),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem(
    BuildContext context,
    HealthRecommendation recommendation,
    bool isDark,
  ) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: recommendation.priority == RecommendationPriority.high
            ? SahoolColors.danger.withOpacity(0.05)
            : isDark
                ? Colors.grey[850]
                : Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: recommendation.priority == RecommendationPriority.high
              ? SahoolColors.danger.withOpacity(0.3)
              : isDark
                  ? Colors.grey[700]!
                  : Colors.grey[200]!,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _getRecommendationColor(recommendation).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  recommendation.icon,
                  size: 18,
                  color: _getRecommendationColor(recommendation),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            recommendation.titleArabic,
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: isDark ? Colors.white : SahoolColors.textDark,
                            ),
                          ),
                        ),
                        if (recommendation.priority == RecommendationPriority.high)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 6,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: SahoolColors.danger,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: const Text(
                              'عاجل',
                              style: TextStyle(
                                fontSize: 9,
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      recommendation.descriptionArabic,
                      style: TextStyle(
                        fontSize: 11,
                        color: isDark ? Colors.grey[400] : Colors.grey[600],
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),

          // Quick Action Button
          if (recommendation.canCreateTask) ...[
            const SizedBox(height: 10),
            InkWell(
              onTap: () => _createTaskFromRecommendation(context, recommendation),
              borderRadius: BorderRadius.circular(8),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(
                  color: SahoolColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: SahoolColors.primary.withOpacity(0.3),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.add_task_rounded,
                      size: 14,
                      color: SahoolColors.primary,
                    ),
                    const SizedBox(width: 6),
                    Text(
                      'إنشاء مهمة / Create Task',
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight: FontWeight.bold,
                        color: SahoolColors.primary,
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildEmptyRecommendations(bool isDark) {
    return Container(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          Icon(
            Icons.check_circle_outline_rounded,
            size: 48,
            color: SahoolColors.success.withOpacity(0.5),
          ),
          const SizedBox(height: 8),
          Text(
            'لا توجد توصيات حالياً',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: isDark ? Colors.grey[400] : Colors.grey[600],
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'الحقل في حالة جيدة',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? Colors.grey[500] : Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Color _getRecommendationColor(HealthRecommendation recommendation) {
    switch (recommendation.type) {
      case RecommendationType.irrigation:
        return Colors.blue;
      case RecommendationType.fertilization:
        return Colors.green;
      case RecommendationType.pestControl:
        return Colors.orange;
      case RecommendationType.monitoring:
        return SahoolColors.info;
      case RecommendationType.harvesting:
        return SahoolColors.harvestGold;
    }
  }

  Future<void> _createTaskFromRecommendation(
    BuildContext context,
    HealthRecommendation recommendation,
  ) async {
    try {
      // Navigate to task creation screen with pre-filled data
      final result = await context.push(
        '/tasks/create',
        extra: {
          'fieldId': widget.field.id,
          'title': recommendation.titleArabic,
          'description': recommendation.descriptionArabic,
          'priority': recommendation.priority == RecommendationPriority.high
              ? 'high'
              : 'medium',
        },
      );

      if (result == true && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: const Text('تم إنشاء المهمة بنجاح / Task created successfully'),
            backgroundColor: SahoolColors.success,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في إنشاء المهمة / Error: $e'),
            backgroundColor: SahoolColors.danger,
            behavior: SnackBarBehavior.floating,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        );
      }
    }
  }

  FieldHealthData _calculateHealthData(Field field) {
    // Calculate overall health score based on multiple factors
    final ndviScore = (field.ndvi * 100).round();
    final tasksScore = _calculateTasksScore(field.pendingTasks);
    final irrigationScore = _getIrrigationScore();
    final weatherScore = _getWeatherScore();

    // Weighted average: NDVI 50%, Tasks 20%, Irrigation 15%, Weather 15%
    final overallScore =
        (ndviScore * 0.5 + tasksScore * 0.2 + irrigationScore * 0.15 + weatherScore * 0.15)
            .round();

    // Determine status
    final status = _getHealthStatus(overallScore);
    final statusArabic = _getHealthStatusArabic(status);
    final color = _getHealthColor(status);

    // Calculate trend (mock data - in production, compare with historical data)
    final trend = _calculateTrend(field);
    final trendValue = _getTrendValue(trend);

    // Get alert count
    final alertCount = _getAlertCount(field, overallScore);

    // Generate recommendations
    final recommendations = _generateRecommendations(field, overallScore);

    return FieldHealthData(
      score: overallScore,
      ndviValue: field.ndvi,
      ndviColor: _getNdviColor(field.ndvi),
      irrigationStatus: _getIrrigationStatus(),
      irrigationColor: _getIrrigationColor(),
      pendingTasks: field.pendingTasks,
      tasksColor: _getTasksColor(field.pendingTasks),
      weatherStatus: _getWeatherStatusText(),
      weatherColor: _getWeatherStatusColor(),
      status: status,
      statusArabic: statusArabic,
      color: color,
      trend: trend,
      trendValue: trendValue,
      alertCount: alertCount,
      hasAlerts: alertCount > 0,
      recommendations: recommendations,
    );
  }

  int _calculateTasksScore(int pendingTasks) {
    if (pendingTasks == 0) return 100;
    if (pendingTasks <= 2) return 80;
    if (pendingTasks <= 5) return 60;
    return 40;
  }

  int _getIrrigationScore() {
    // Mock - in production, get from irrigation sensors/schedule
    return 85;
  }

  int _getWeatherScore() {
    // Mock - in production, get from weather API
    return 75;
  }

  FieldHealthStatus _getHealthStatus(int score) {
    if (score >= 80) return FieldHealthStatus.excellent;
    if (score >= 60) return FieldHealthStatus.good;
    if (score >= 40) return FieldHealthStatus.moderate;
    return FieldHealthStatus.poor;
  }

  String _getHealthStatusArabic(FieldHealthStatus status) {
    switch (status) {
      case FieldHealthStatus.excellent:
        return 'ممتاز';
      case FieldHealthStatus.good:
        return 'جيد';
      case FieldHealthStatus.moderate:
        return 'متوسط';
      case FieldHealthStatus.poor:
        return 'ضعيف';
    }
  }

  Color _getHealthColor(FieldHealthStatus status) {
    switch (status) {
      case FieldHealthStatus.excellent:
        return SahoolColors.healthExcellent;
      case FieldHealthStatus.good:
        return SahoolColors.healthGood;
      case FieldHealthStatus.moderate:
        return SahoolColors.healthModerate;
      case FieldHealthStatus.poor:
        return SahoolColors.healthPoor;
    }
  }

  Color _getNdviColor(double ndvi) {
    if (ndvi >= 0.6) return SahoolColors.healthExcellent;
    if (ndvi >= 0.4) return SahoolColors.healthModerate;
    return SahoolColors.healthPoor;
  }

  String _getIrrigationStatus() {
    // Mock - in production, get from irrigation system
    return 'جيد';
  }

  Color _getIrrigationColor() {
    // Mock - in production, get from irrigation system
    return Colors.blue;
  }

  Color _getTasksColor(int pendingTasks) {
    if (pendingTasks == 0) return SahoolColors.success;
    if (pendingTasks <= 2) return SahoolColors.info;
    if (pendingTasks <= 5) return SahoolColors.warning;
    return SahoolColors.danger;
  }

  String _getWeatherStatusText() {
    // Mock - in production, get from weather API
    return 'مناسب';
  }

  Color _getWeatherStatusColor() {
    // Mock - in production, get from weather API
    return SahoolColors.success;
  }

  HealthTrend _calculateTrend(Field field) {
    // Mock - in production, compare with historical data
    if (field.ndvi >= 0.6) return HealthTrend.up;
    if (field.ndvi >= 0.4) return HealthTrend.stable;
    return HealthTrend.down;
  }

  int _getTrendValue(HealthTrend trend) {
    // Mock - in production, calculate actual percentage change
    switch (trend) {
      case HealthTrend.up:
        return 5;
      case HealthTrend.stable:
        return 0;
      case HealthTrend.down:
        return -3;
    }
  }

  int _getAlertCount(Field field, int healthScore) {
    int count = 0;
    if (field.needsAttention) count++;
    if (field.pendingTasks > 5) count++;
    if (healthScore < 50) count++;
    return count;
  }

  List<HealthRecommendation> _generateRecommendations(Field field, int healthScore) {
    final recommendations = <HealthRecommendation>[];

    // NDVI-based recommendations
    if (field.ndvi < 0.4) {
      recommendations.add(
        HealthRecommendation(
          type: RecommendationType.irrigation,
          priority: RecommendationPriority.high,
          titleArabic: 'إجهاد مائي محتمل',
          titleEnglish: 'Potential Water Stress',
          descriptionArabic:
              'مؤشر NDVI منخفض. يُنصح بفحص نظام الري وزيادة التردد إذا لزم الأمر.',
          descriptionEnglish:
              'Low NDVI detected. Check irrigation system and increase frequency if needed.',
          icon: Icons.water_drop_rounded,
          canCreateTask: true,
        ),
      );
    } else if (field.ndvi < 0.6) {
      recommendations.add(
        HealthRecommendation(
          type: RecommendationType.monitoring,
          priority: RecommendationPriority.medium,
          titleArabic: 'مراقبة صحة النباتات',
          titleEnglish: 'Monitor Plant Health',
          descriptionArabic:
              'مؤشر NDVI متوسط. يُنصح بمراقبة النباتات بانتظام والتحقق من وجود آفات.',
          descriptionEnglish:
              'Moderate NDVI. Regular monitoring recommended to check for pests or diseases.',
          icon: Icons.visibility_rounded,
          canCreateTask: true,
        ),
      );
    }

    // Tasks-based recommendations
    if (field.pendingTasks > 3) {
      recommendations.add(
        HealthRecommendation(
          type: RecommendationType.monitoring,
          priority: RecommendationPriority.medium,
          titleArabic: 'مهام معلقة',
          titleEnglish: 'Pending Tasks',
          descriptionArabic:
              'يوجد ${field.pendingTasks} مهام معلقة. يُنصح بإكمالها في أقرب وقت للحفاظ على صحة الحقل.',
          descriptionEnglish:
              '${field.pendingTasks} pending tasks. Complete them soon to maintain field health.',
          icon: Icons.task_alt_rounded,
          canCreateTask: false,
        ),
      );
    }

    // Weather-based recommendations (mock)
    if (healthScore < 70) {
      recommendations.add(
        HealthRecommendation(
          type: RecommendationType.fertilization,
          priority: RecommendationPriority.low,
          titleArabic: 'تسميد موسمي',
          titleEnglish: 'Seasonal Fertilization',
          descriptionArabic:
              'يُنصح بإضافة سماد NPK لتعزيز نمو النباتات وتحسين مؤشر الصحة.',
          descriptionEnglish:
              'Apply NPK fertilizer to boost plant growth and improve health score.',
          icon: Icons.science_rounded,
          canCreateTask: true,
        ),
      );
    }

    return recommendations;
  }
}

// ============================================================================
// Data Models
// ============================================================================

class FieldHealthData {
  final int score;
  final double ndviValue;
  final Color ndviColor;
  final String irrigationStatus;
  final Color irrigationColor;
  final int pendingTasks;
  final Color tasksColor;
  final String weatherStatus;
  final Color weatherColor;
  final FieldHealthStatus status;
  final String statusArabic;
  final Color color;
  final HealthTrend trend;
  final int trendValue;
  final int alertCount;
  final bool hasAlerts;
  final List<HealthRecommendation> recommendations;

  FieldHealthData({
    required this.score,
    required this.ndviValue,
    required this.ndviColor,
    required this.irrigationStatus,
    required this.irrigationColor,
    required this.pendingTasks,
    required this.tasksColor,
    required this.weatherStatus,
    required this.weatherColor,
    required this.status,
    required this.statusArabic,
    required this.color,
    required this.trend,
    required this.trendValue,
    required this.alertCount,
    required this.hasAlerts,
    required this.recommendations,
  });
}

class HealthRecommendation {
  final RecommendationType type;
  final RecommendationPriority priority;
  final String titleArabic;
  final String titleEnglish;
  final String descriptionArabic;
  final String descriptionEnglish;
  final IconData icon;
  final bool canCreateTask;

  HealthRecommendation({
    required this.type,
    required this.priority,
    required this.titleArabic,
    required this.titleEnglish,
    required this.descriptionArabic,
    required this.descriptionEnglish,
    required this.icon,
    this.canCreateTask = false,
  });
}

enum FieldHealthStatus {
  excellent,
  good,
  moderate,
  poor,
}

enum HealthTrend {
  up,
  stable,
  down,
}

enum RecommendationType {
  irrigation,
  fertilization,
  pestControl,
  monitoring,
  harvesting,
}

enum RecommendationPriority {
  high,
  medium,
  low,
}
