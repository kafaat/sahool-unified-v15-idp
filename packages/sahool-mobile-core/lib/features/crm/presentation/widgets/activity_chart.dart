/// Activity Chart Widget
/// مخطط النشاط
///
/// Displays activity analytics in chart format
library;

import 'package:flutter/material.dart';

import '../../domain/models/activity_log.dart';

/// Activity Summary Card
/// بطاقة ملخص النشاط
class ActivitySummaryCard extends StatelessWidget {
  final FarmerAnalytics analytics;
  final VoidCallback? onViewDetails;

  const ActivitySummaryCard({
    super.key,
    required this.analytics,
    this.onViewDetails,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Text(
                  'ملخص النشاط',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                if (onViewDetails != null)
                  TextButton(
                    onPressed: onViewDetails,
                    child: const Text('عرض التفاصيل'),
                  ),
              ],
            ),

            const SizedBox(height: 16),

            // Stats grid
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'إجمالي التفاعلات',
                    analytics.totalInteractions.toString(),
                    Icons.touch_app,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'المكالمات',
                    analytics.callCount.toString(),
                    Icons.phone,
                    Colors.green,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    'الزيارات',
                    analytics.visitCount.toString(),
                    Icons.location_on,
                    Colors.orange,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    'الرسائل',
                    analytics.messageCount.toString(),
                    Icons.chat,
                    Colors.purple,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),

            // Interaction by type chart
            _buildInteractionChart(),

            const SizedBox(height: 16),

            // Additional stats
            Row(
              children: [
                Expanded(
                  child: _buildMetricCard(
                    'نسبة النجاح',
                    '${analytics.winRate.toStringAsFixed(0)}%',
                    analytics.winRate >= 50 ? Colors.green : Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildMetricCard(
                    'متوسط الاستجابة',
                    '${analytics.avgResponseDays} يوم',
                    analytics.avgResponseDays <= 3 ? Colors.green : Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildInteractionChart() {
    if (analytics.interactionByType.isEmpty) {
      return const SizedBox.shrink();
    }

    final total = analytics.interactionByType.values.reduce((a, b) => a + b);
    if (total == 0) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'توزيع التفاعلات',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 12),
        ...analytics.interactionByType.entries.map((entry) {
          final percentage = (entry.value / total * 100).round();
          return Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: _buildProgressBar(
              entry.key,
              entry.value,
              percentage,
              _getTypeColor(entry.key),
            ),
          );
        }),
      ],
    );
  }

  Widget _buildProgressBar(
    String label,
    int value,
    int percentage,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              _getTypeLabel(label),
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
            Text(
              '$value ($percentage%)',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.w600,
                color: Colors.grey[700],
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
    );
  }

  Widget _buildMetricCard(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey[300]!),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }

  String _getTypeLabel(String type) {
    switch (type.toLowerCase()) {
      case 'call':
        return 'مكالمات';
      case 'visit':
        return 'زيارات';
      case 'whatsapp':
        return 'واتساب';
      case 'sms':
        return 'رسائل نصية';
      case 'email':
        return 'بريد إلكتروني';
      case 'meeting':
        return 'اجتماعات';
      case 'note':
        return 'ملاحظات';
      default:
        return type;
    }
  }

  Color _getTypeColor(String type) {
    switch (type.toLowerCase()) {
      case 'call':
        return Colors.blue;
      case 'visit':
        return Colors.green;
      case 'whatsapp':
        return const Color(0xFF25D366);
      case 'sms':
        return Colors.purple;
      case 'email':
        return Colors.red;
      case 'meeting':
        return Colors.indigo;
      case 'note':
        return Colors.grey;
      default:
        return Colors.teal;
    }
  }
}

/// CRM Stats Overview Card
/// بطاقة نظرة عامة على إحصائيات CRM
class CrmStatsOverviewCard extends StatelessWidget {
  final CrmStats stats;
  final VoidCallback? onViewFarmers;
  final VoidCallback? onViewFollowUps;
  final VoidCallback? onViewOpportunities;

  const CrmStatsOverviewCard({
    super.key,
    required this.stats,
    this.onViewFarmers,
    this.onViewFollowUps,
    this.onViewOpportunities,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Text(
              'نظرة عامة',
              style: theme.textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
            ),

            const SizedBox(height: 16),

            // Main stats
            Row(
              children: [
                Expanded(
                  child: _buildStatTile(
                    'المزارعين',
                    stats.totalFarmers.toString(),
                    '${stats.newFarmersThisMonth} جديد هذا الشهر',
                    Icons.people,
                    Colors.blue,
                    onViewFarmers,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildStatTile(
                    'التفاعلات',
                    stats.totalInteractions.toString(),
                    '${stats.interactionsThisWeek} هذا الأسبوع',
                    Icons.touch_app,
                    Colors.green,
                    null,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildAlertTile(
                    'المتابعات',
                    stats.pendingFollowUps.toString(),
                    '${stats.overdueFollowUps} متأخرة',
                    Icons.event,
                    stats.overdueFollowUps > 0 ? Colors.red : Colors.orange,
                    onViewFollowUps,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),

            // Pipeline stats
            Text(
              'خط الأنابيب',
              style: theme.textTheme.titleSmall?.copyWith(
                fontWeight: FontWeight.w600,
              ),
            ),

            const SizedBox(height: 12),

            Row(
              children: [
                Expanded(
                  child: _buildPipelineItem(
                    'فرص مفتوحة',
                    stats.openOpportunities.toString(),
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildPipelineItem(
                    'قيمة الأنابيب',
                    _formatCurrency(stats.pipelineValue),
                    Colors.green,
                  ),
                ),
                Expanded(
                  child: _buildPipelineItem(
                    'معدل التحويل',
                    '${stats.conversionRate.toStringAsFixed(0)}%',
                    Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatTile(
    String label,
    String value,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback? onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(icon, color: color, size: 32),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    label,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  Text(
                    value,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: color,
                    ),
                  ),
                  Text(
                    subtitle,
                    style: TextStyle(
                      fontSize: 10,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            ),
            if (onTap != null)
              Icon(Icons.chevron_left, color: Colors.grey[400]),
          ],
        ),
      ),
    );
  }

  Widget _buildAlertTile(
    String label,
    String value,
    String subtitle,
    IconData icon,
    Color color,
    VoidCallback? onTap,
  ) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withValues(alpha: 0.3)),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            Text(
              subtitle,
              style: TextStyle(
                fontSize: 10,
                color: color,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPipelineItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: Colors.grey[600],
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  String _formatCurrency(double amount) {
    if (amount >= 1000000) {
      return '${(amount / 1000000).toStringAsFixed(1)}M';
    } else if (amount >= 1000) {
      return '${(amount / 1000).toStringAsFixed(1)}K';
    }
    return amount.toStringAsFixed(0);
  }
}
