/// Report Card Widget - ودجت بطاقة التقرير
/// Reusable card component for displaying report items
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_template.dart';
import '../../domain/models/report_data.dart';

/// Report Card Widget
/// ودجت بطاقة التقرير
class ReportCard extends StatelessWidget {
  final ReportData report;
  final VoidCallback? onTap;
  final VoidCallback? onShare;
  final VoidCallback? onDelete;

  const ReportCard({
    super.key,
    required this.report,
    this.onTap,
    this.onShare,
    this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: _getStatusColor().withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      _getTemplateIcon(),
                      color: _getStatusColor(),
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          report.titleAr,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          report.template.nameAr,
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  _buildStatusBadge(),
                ],
              ),
              const SizedBox(height: 16),

              // Date range
              Row(
                children: [
                  Icon(Icons.calendar_today, size: 14, color: Colors.grey[500]),
                  const SizedBox(width: 6),
                  Text(
                    report.filter.dateRange.formattedAr,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 8),

              // Generation info
              Row(
                children: [
                  Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                  const SizedBox(width: 6),
                  Text(
                    _formatDate(report.generatedAt),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                  if (report.isOffline) ...[
                    const SizedBox(width: 12),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 6,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.orange.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          Icon(
                            Icons.offline_bolt,
                            size: 12,
                            color: Colors.orange[700],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            'محلي',
                            style: TextStyle(
                              fontSize: 10,
                              color: Colors.orange[700],
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ],
              ),

              // Summary stats preview
              if (report.summaryStats.isNotEmpty) ...[
                const SizedBox(height: 16),
                const Divider(height: 1),
                const SizedBox(height: 12),
                _buildStatsPreview(),
              ],

              // Action buttons
              if (onShare != null || onDelete != null) ...[
                const SizedBox(height: 12),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (onShare != null)
                      IconButton(
                        icon: const Icon(Icons.share, size: 20),
                        onPressed: onShare,
                        color: SahoolColors.primary,
                      ),
                    if (onDelete != null)
                      IconButton(
                        icon: const Icon(Icons.delete_outline, size: 20),
                        onPressed: onDelete,
                        color: Colors.red,
                      ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getStatusColor().withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getStatusIcon(),
            size: 12,
            color: _getStatusColor(),
          ),
          const SizedBox(width: 4),
          Text(
            _getStatusText(),
            style: TextStyle(
              fontSize: 10,
              color: _getStatusColor(),
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsPreview() {
    final previewStats = report.summaryStats.take(3).toList();
    return Row(
      children: previewStats
          .map((stat) => Expanded(
                child: Column(
                  children: [
                    Text(
                      stat.value,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      stat.labelAr,
                      style: TextStyle(
                        fontSize: 10,
                        color: Colors.grey[600],
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],
                ),
              ))
          .toList(),
    );
  }

  IconData _getTemplateIcon() {
    switch (report.template.type) {
      case ReportType.fieldPerformance:
        return Icons.landscape;
      case ReportType.ndviTrend:
        return Icons.show_chart;
      case ReportType.irrigationSummary:
        return Icons.water_drop;
      case ReportType.taskCompletion:
        return Icons.task_alt;
      case ReportType.weatherAnalysis:
        return Icons.cloud;
      case ReportType.costProfit:
        return Icons.account_balance;
      case ReportType.yieldPrediction:
        return Icons.trending_up;
    }
  }

  Color _getStatusColor() {
    switch (report.status) {
      case ReportStatus.ready:
        return SahoolColors.success;
      case ReportStatus.generating:
        return SahoolColors.info;
      case ReportStatus.failed:
        return SahoolColors.danger;
      case ReportStatus.draft:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon() {
    switch (report.status) {
      case ReportStatus.ready:
        return Icons.check_circle;
      case ReportStatus.generating:
        return Icons.hourglass_empty;
      case ReportStatus.failed:
        return Icons.error;
      case ReportStatus.draft:
        return Icons.edit;
    }
  }

  String _getStatusText() {
    switch (report.status) {
      case ReportStatus.ready:
        return 'جاهز';
      case ReportStatus.generating:
        return 'قيد التوليد';
      case ReportStatus.failed:
        return 'فشل';
      case ReportStatus.draft:
        return 'مسودة';
    }
  }

  String _formatDate(DateTime date) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inMinutes < 60) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else if (diff.inHours < 24) {
      return 'منذ ${diff.inHours} ساعة';
    } else if (diff.inDays < 7) {
      return 'منذ ${diff.inDays} يوم';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}

/// Mini Report Card for list views
/// بطاقة تقرير مصغرة للقوائم
class MiniReportCard extends StatelessWidget {
  final ReportData report;
  final VoidCallback? onTap;

  const MiniReportCard({
    super.key,
    required this.report,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: SahoolColors.primary.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getIcon(),
                  color: SahoolColors.primary,
                  size: 18,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      report.titleAr,
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        fontSize: 14,
                      ),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 2),
                    Text(
                      report.filter.dateRange.formattedAr,
                      style: TextStyle(
                        fontSize: 11,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_left, size: 18, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getIcon() {
    switch (report.template.type) {
      case ReportType.fieldPerformance:
        return Icons.landscape;
      case ReportType.ndviTrend:
        return Icons.show_chart;
      case ReportType.irrigationSummary:
        return Icons.water_drop;
      case ReportType.taskCompletion:
        return Icons.task_alt;
      case ReportType.weatherAnalysis:
        return Icons.cloud;
      case ReportType.costProfit:
        return Icons.account_balance;
      case ReportType.yieldPrediction:
        return Icons.trending_up;
    }
  }
}
