/// Usage Chart Widget - مخطط الاستخدام
/// Visual charts for equipment usage data
library;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/usage_log.dart';

/// Usage Hours Bar Chart
class UsageHoursChart extends StatelessWidget {
  final List<DailyUsage> dailyUsage;
  final double height;
  final bool showLabels;
  final int maxDays;

  const UsageHoursChart({
    super.key,
    required this.dailyUsage,
    this.height = 150,
    this.showLabels = true,
    this.maxDays = 7,
  });

  @override
  Widget build(BuildContext context) {
    final displayData = dailyUsage.take(maxDays).toList().reversed.toList();

    if (displayData.isEmpty) {
      return _buildEmptyState();
    }

    final maxHours = displayData.map((d) => d.hours).reduce((a, b) => a > b ? a : b);
    final normalizedMax = maxHours > 0 ? maxHours : 1;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: SahoolColors.forestGreen.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.bar_chart,
                color: SahoolColors.forestGreen,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'ساعات الاستخدام',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Chart
        SizedBox(
          height: height,
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: displayData.map((data) {
              final barHeight = (data.hours / normalizedMax) * (height - 30);
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      // Value label
                      Text(
                        data.hours.toStringAsFixed(1),
                        style: const TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.forestGreen,
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Bar
                      Container(
                        height: barHeight > 0 ? barHeight : 4,
                        decoration: const BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.bottomCenter,
                            end: Alignment.topCenter,
                            colors: [
                              SahoolColors.forestGreen,
                              SahoolColors.sageGreen,
                            ],
                          ),
                          borderRadius: BorderRadius.vertical(
                            top: Radius.circular(4),
                          ),
                        ),
                      ),
                      const SizedBox(height: 4),
                      // Day label
                      if (showLabels)
                        Text(
                          _getDayLabel(data.date),
                          style: TextStyle(
                            fontSize: 9,
                            color: Colors.grey[600],
                          ),
                        ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildEmptyState() {
    return SizedBox(
      height: height,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.bar_chart_outlined,
              size: 48,
              color: Colors.grey[300],
            ),
            const SizedBox(height: 8),
            Text(
              'لا توجد بيانات استخدام',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getDayLabel(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date).inDays;

    if (diff == 0) return 'اليوم';
    if (diff == 1) return 'أمس';

    const days = ['أحد', 'اثنين', 'ثلاثاء', 'أربعاء', 'خميس', 'جمعة', 'سبت'];
    return days[date.weekday % 7];
  }
}

/// Activity Distribution Chart
class ActivityDistributionChart extends StatelessWidget {
  final Map<String, double> hoursByActivity;
  final double size;

  const ActivityDistributionChart({
    super.key,
    required this.hoursByActivity,
    this.size = 150,
  });

  @override
  Widget build(BuildContext context) {
    if (hoursByActivity.isEmpty) {
      return _buildEmptyState();
    }

    final total = hoursByActivity.values.reduce((a, b) => a + b);
    final sortedEntries = hoursByActivity.entries.toList()
      ..sort((a, b) => b.value.compareTo(a.value));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.blue.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.pie_chart,
                color: Colors.blue,
                size: 20,
              ),
            ),
            const SizedBox(width: 12),
            const Text(
              'توزيع النشاطات',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Simple distribution bars
        ...sortedEntries.map((entry) {
          final percentage = (entry.value / total) * 100;
          final color = _getActivityColor(entry.key);
          final activityName = _getActivityName(entry.key);

          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: color,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        activityName,
                        style: const TextStyle(fontSize: 12),
                      ),
                    ),
                    Text(
                      '${entry.value.toStringAsFixed(1)}h',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '${percentage.toStringAsFixed(0)}%',
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                ClipRRect(
                  borderRadius: BorderRadius.circular(4),
                  child: LinearProgressIndicator(
                    value: percentage / 100,
                    backgroundColor: Colors.grey[200],
                    valueColor: AlwaysStoppedAnimation<Color>(color),
                    minHeight: 6,
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildEmptyState() {
    return SizedBox(
      height: size,
      child: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.pie_chart_outline,
              size: 48,
              color: Colors.grey[300],
            ),
            const SizedBox(height: 8),
            Text(
              'لا توجد بيانات نشاطات',
              style: TextStyle(
                color: Colors.grey[500],
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getActivityName(String activity) {
    final type = FieldActivityType.values.firstWhere(
      (t) => t.value == activity,
      orElse: () => FieldActivityType.other,
    );
    return type.nameAr;
  }

  Color _getActivityColor(String activity) {
    final type = FieldActivityType.values.firstWhere(
      (t) => t.value == activity,
      orElse: () => FieldActivityType.other,
    );

    switch (type) {
      case FieldActivityType.plowing:
        return Colors.brown;
      case FieldActivityType.seeding:
        return SahoolColors.forestGreen;
      case FieldActivityType.spraying:
        return Colors.blue;
      case FieldActivityType.harvesting:
        return SahoolColors.harvestGold;
      case FieldActivityType.irrigation:
        return Colors.cyan;
      case FieldActivityType.fertilizing:
        return Colors.green;
      case FieldActivityType.weeding:
        return Colors.lime;
      case FieldActivityType.transport:
        return Colors.orange;
      case FieldActivityType.other:
        return Colors.grey;
    }
  }
}

/// Usage Summary Card
class UsageSummaryCard extends StatelessWidget {
  final UsageSummary summary;

  const UsageSummaryCard({
    super.key,
    required this.summary,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            SahoolColors.forestGreen,
            SahoolColors.forestGreen.withValues(alpha: 0.8),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.analytics, color: Colors.white, size: 24),
              const SizedBox(width: 8),
              const Text(
                'ملخص الاستخدام',
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.white.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  _formatPeriod(),
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              _buildMetric(
                Icons.timer,
                summary.totalHours.toStringAsFixed(1),
                'ساعة',
              ),
              _buildMetric(
                Icons.local_gas_station,
                summary.totalFuel.toStringAsFixed(0),
                'لتر',
              ),
              _buildMetric(
                Icons.square_foot,
                summary.totalArea.toStringAsFixed(1),
                'هكتار',
              ),
              _buildMetric(
                Icons.play_circle,
                summary.sessionCount.toString(),
                'جلسة',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMetric(IconData icon, String value, String unit) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, color: Colors.white.withValues(alpha: 0.8), size: 20),
          const SizedBox(height: 8),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 18,
            ),
          ),
          Text(
            unit,
            style: TextStyle(
              color: Colors.white.withValues(alpha: 0.7),
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  String _formatPeriod() {
    final days = summary.periodEnd.difference(summary.periodStart).inDays;
    if (days <= 7) return 'آخر أسبوع';
    if (days <= 30) return 'آخر شهر';
    if (days <= 90) return 'آخر 3 أشهر';
    return 'آخر سنة';
  }
}

/// Hours Counter Widget
class HoursCounter extends StatelessWidget {
  final double hours;
  final double? maxHours;
  final String label;
  final bool showProgress;

  const HoursCounter({
    super.key,
    required this.hours,
    this.maxHours,
    this.label = 'ساعات التشغيل',
    this.showProgress = true,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.timer, color: SahoolColors.forestGreen, size: 20),
            const SizedBox(width: 8),
            Text(
              label,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Row(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              hours.toStringAsFixed(0),
              style: const TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: SahoolColors.forestGreen,
              ),
            ),
            const Padding(
              padding: EdgeInsets.only(bottom: 6),
              child: Text(
                ' ساعة',
                style: TextStyle(
                  fontSize: 14,
                  color: SahoolColors.forestGreen,
                ),
              ),
            ),
            if (maxHours != null) ...[
              const Spacer(),
              Text(
                'من ${maxHours!.toStringAsFixed(0)}',
                style: TextStyle(
                  color: Colors.grey[500],
                  fontSize: 12,
                ),
              ),
            ],
          ],
        ),
        if (showProgress && maxHours != null) ...[
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: hours / maxHours!,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(
                hours / maxHours! > 0.9
                    ? SahoolColors.danger
                    : hours / maxHours! > 0.75
                        ? SahoolColors.harvestGold
                        : SahoolColors.forestGreen,
              ),
              minHeight: 8,
            ),
          ),
          if (hours / maxHours! > 0.9) ...[
            const SizedBox(height: 4),
            const Row(
              children: [
                Icon(Icons.warning, color: SahoolColors.danger, size: 14),
                SizedBox(width: 4),
                Text(
                  'يقترب من موعد الصيانة',
                  style: TextStyle(
                    color: SahoolColors.danger,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ],
        ],
      ],
    );
  }
}
