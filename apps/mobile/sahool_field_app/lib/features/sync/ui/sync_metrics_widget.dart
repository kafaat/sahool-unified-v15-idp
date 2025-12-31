import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../../../core/sync/sync_metrics_service.dart';

/// Sync Metrics Widget - Displays comprehensive sync health and metrics
/// واجهة عرض إحصائيات المزامنة
class SyncMetricsWidget extends ConsumerWidget {
  final bool showDebugInfo;
  final bool isCompact;

  const SyncMetricsWidget({
    super.key,
    this.showDebugInfo = false,
    this.isCompact = false,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final metricsAsync = ref.watch(syncMetricsProvider);

    return metricsAsync.when(
      data: (metrics) => isCompact
          ? _CompactMetricsView(metrics: metrics)
          : _FullMetricsView(
              metrics: metrics,
              showDebugInfo: showDebugInfo,
            ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(
        child: Text('خطأ في تحميل الإحصائيات: $error'),
      ),
    );
  }
}

/// Compact view for dashboard/quick view
class _CompactMetricsView extends StatelessWidget {
  final SyncMetrics metrics;

  const _CompactMetricsView({required this.metrics});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'حالة المزامنة',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                _buildHealthIndicator(metrics),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatColumn(
                  'العمليات',
                  metrics.totalOperations.toString(),
                  Icons.sync,
                ),
                _buildStatColumn(
                  'النجاح',
                  '${(metrics.successRate * 100).toStringAsFixed(1)}%',
                  Icons.check_circle,
                  color: Colors.green,
                ),
                _buildStatColumn(
                  'التعارضات',
                  metrics.conflictCount.toString(),
                  Icons.warning,
                  color: metrics.conflictCount > 0 ? Colors.orange : null,
                ),
                _buildStatColumn(
                  'قيد الانتظار',
                  metrics.currentQueueDepth.toString(),
                  Icons.queue,
                ),
              ],
            ),
            if (metrics.lastSyncTime != null) ...[
              const SizedBox(height: 12),
              Text(
                'آخر مزامنة: ${_formatRelativeTime(metrics.lastSyncTime!)}',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatColumn(String label, String value, IconData icon, {Color? color}) {
    return Column(
      children: [
        Icon(icon, color: color ?? Colors.blue, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildHealthIndicator(SyncMetrics metrics) {
    final healthColor = _getHealthColor(metrics);
    final healthText = _getHealthText(metrics);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: healthColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: healthColor),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.circle, color: healthColor, size: 12),
          const SizedBox(width: 6),
          Text(
            healthText,
            style: TextStyle(
              color: healthColor,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Color _getHealthColor(SyncMetrics metrics) {
    if (metrics.successRate < 0.8) return Colors.red;
    if (metrics.conflictCount > 5) return Colors.orange;
    if (metrics.currentQueueDepth > 10) return Colors.yellow;
    return Colors.green;
  }

  String _getHealthText(SyncMetrics metrics) {
    if (metrics.successRate < 0.8) return 'يحتاج انتباه';
    if (metrics.conflictCount > 5) return 'تعارضات';
    if (metrics.currentQueueDepth > 10) return 'جاري المزامنة';
    return 'صحي';
  }

  String _formatRelativeTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inMinutes < 1) return 'الآن';
    if (difference.inMinutes < 60) return 'منذ ${difference.inMinutes} دقيقة';
    if (difference.inHours < 24) return 'منذ ${difference.inHours} ساعة';
    return 'منذ ${difference.inDays} يوم';
  }
}

/// Full metrics view with charts and detailed statistics
class _FullMetricsView extends ConsumerWidget {
  final SyncMetrics metrics;
  final bool showDebugInfo;

  const _FullMetricsView({
    required this.metrics,
    required this.showDebugInfo,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final dailyMetrics = ref.watch(dailyMetricsProvider);

    return SingleChildScrollView(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Overall Health Card
            _buildOverallHealthCard(context),
            const SizedBox(height: 16),

            // Performance Metrics
            _buildPerformanceMetricsCard(context),
            const SizedBox(height: 16),

            // Historical Trends
            if (dailyMetrics.isNotEmpty) ...[
              _buildHistoricalTrendsCard(context, dailyMetrics),
              const SizedBox(height: 16),
            ],

            // Conflict Analysis
            if (metrics.conflictCount > 0) ...[
              _buildConflictAnalysisCard(context),
              const SizedBox(height: 16),
            ],

            // Retry Statistics
            if (metrics.retryStatistics.totalRetries > 0) ...[
              _buildRetryStatisticsCard(context),
              const SizedBox(height: 16),
            ],

            // Queue Depth Chart
            if (metrics.queueDepthHistory.isNotEmpty) ...[
              _buildQueueDepthChart(context),
              const SizedBox(height: 16),
            ],

            // Recent Operations
            if (metrics.operationHistory.isNotEmpty) ...[
              _buildRecentOperationsCard(context),
              const SizedBox(height: 16),
            ],

            // Debug Information
            if (showDebugInfo) ...[
              _buildDebugInfoCard(context, ref),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildOverallHealthCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'الصحة العامة',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    'إجمالي العمليات',
                    metrics.totalOperations.toString(),
                    Icons.sync_alt,
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildMetricTile(
                    'معدل النجاح',
                    '${(metrics.successRate * 100).toStringAsFixed(1)}%',
                    Icons.check_circle,
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                Expanded(
                  child: _buildMetricTile(
                    'فشل',
                    metrics.failedOperations.toString(),
                    Icons.error,
                    Colors.red,
                  ),
                ),
                Expanded(
                  child: _buildMetricTile(
                    'تعارضات',
                    metrics.conflictCount.toString(),
                    Icons.warning,
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

  Widget _buildPerformanceMetricsCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'مقاييس الأداء',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildPerformanceRow(
              'متوسط وقت المزامنة',
              '${(metrics.averageDuration / 1000).toStringAsFixed(2)}s',
              Icons.timer,
            ),
            const SizedBox(height: 8),
            _buildPerformanceRow(
              'متوسط حجم البيانات',
              _formatBytes(metrics.averagePayloadSize.toInt()),
              Icons.data_usage,
            ),
            const SizedBox(height: 8),
            _buildPerformanceRow(
              'إجمالي النطاق الترددي',
              _formatBytes(metrics.totalBandwidthBytes),
              Icons.cloud_upload,
            ),
            const SizedBox(height: 8),
            _buildPerformanceRow(
              'عمق قائمة الانتظار الحالي',
              metrics.currentQueueDepth.toString(),
              Icons.queue,
            ),
            const SizedBox(height: 8),
            _buildPerformanceRow(
              'متوسط عمق قائمة الانتظار',
              metrics.averageQueueDepth.toStringAsFixed(1),
              Icons.trending_up,
            ),
            const SizedBox(height: 8),
            _buildPerformanceRow(
              'ذروة قائمة الانتظار',
              metrics.peakQueueDepth.toString(),
              Icons.arrow_upward,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHistoricalTrendsCard(BuildContext context, List<DailyMetrics> dailyMetrics) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'الاتجاهات التاريخية (آخر 7 أيام)',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                _buildHistoricalChart(dailyMetrics),
              ),
            ),
            const SizedBox(height: 16),
            _buildLegend(),
          ],
        ),
      ),
    );
  }

  Widget _buildConflictAnalysisCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'تحليل التعارضات',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...metrics.conflictResolutions.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(_getConflictResolutionText(entry.key)),
                    Text(
                      '${entry.value}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildRetryStatisticsCard(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'إحصائيات إعادة المحاولة',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Text(
              'إجمالي إعادة المحاولات: ${metrics.retryStatistics.totalRetries}',
              style: const TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 12),
            ...metrics.retryStatistics.retryAttemptsByCount.entries.map((entry) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 4.0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('المحاولة ${entry.key}'),
                    Text(
                      '${entry.value}',
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildQueueDepthChart(BuildContext context) {
    final recentSamples = metrics.queueDepthHistory.length > 100
        ? metrics.queueDepthHistory.sublist(metrics.queueDepthHistory.length - 100)
        : metrics.queueDepthHistory;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'عمق قائمة الانتظار بمرور الوقت',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 200,
              child: LineChart(
                _buildQueueDepthChartData(recentSamples),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentOperationsCard(BuildContext context) {
    final recentOps = metrics.operationHistory.length > 10
        ? metrics.operationHistory.sublist(metrics.operationHistory.length - 10)
        : metrics.operationHistory;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'العمليات الأخيرة',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            ...recentOps.reversed.map((op) {
              return ListTile(
                leading: Icon(
                  op.success ? Icons.check_circle : Icons.error,
                  color: op.success ? Colors.green : Colors.red,
                ),
                title: Text('${_getOperationTypeText(op.type)} - ${op.entityType}'),
                subtitle: Text(
                  '${_formatDuration(op.duration)}${op.wasConflict ? ' (تعارض)' : ''}',
                ),
                trailing: Text(
                  DateFormat('HH:mm').format(op.endTime),
                  style: TextStyle(color: Colors.grey[600]),
                ),
              );
            }).toList(),
          ],
        ),
      ),
    );
  }

  Widget _buildDebugInfoCard(BuildContext context, WidgetRef ref) {
    final service = ref.watch(syncMetricsServiceProvider);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'معلومات التصحيح',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                IconButton(
                  icon: const Icon(Icons.copy),
                  onPressed: () {
                    final json = service.exportMetricsAsString();
                    Clipboard.setData(ClipboardData(text: json));
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(content: Text('تم نسخ البيانات')),
                    );
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            Text('آخر مزامنة: ${metrics.lastSyncTime ?? 'لا يوجد'}'),
            Text('عمليات نشطة: ${metrics.activeOperations.length}'),
            Text('سجل العمليات: ${metrics.operationHistory.length}'),
            Text('عينات قائمة الانتظار: ${metrics.queueDepthHistory.length}'),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () async {
                await service.resetMetrics();
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('تم إعادة تعيين الإحصائيات')),
                );
              },
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة تعيين الإحصائيات'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricTile(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
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
            label,
            style: const TextStyle(fontSize: 12),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildPerformanceRow(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.blue),
        const SizedBox(width: 12),
        Expanded(child: Text(label)),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Widget _buildLegend() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        _buildLegendItem('العمليات', Colors.blue),
        const SizedBox(width: 16),
        _buildLegendItem('النجاح', Colors.green),
        const SizedBox(width: 16),
        _buildLegendItem('الفشل', Colors.red),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color) {
    return Row(
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 4),
        Text(label, style: const TextStyle(fontSize: 12)),
      ],
    );
  }

  LineChartData _buildHistoricalChart(List<DailyMetrics> dailyMetrics) {
    return LineChartData(
      gridData: FlGridData(show: true),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(
          sideTitles: SideTitles(showTitles: true, reservedSize: 40),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(
            showTitles: true,
            getTitlesWidget: (value, meta) {
              if (value.toInt() < 0 || value.toInt() >= dailyMetrics.length) {
                return const Text('');
              }
              final date = dailyMetrics[value.toInt()].date;
              return Text(
                DateFormat('MM/dd').format(date),
                style: const TextStyle(fontSize: 10),
              );
            },
          ),
        ),
        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
      ),
      borderData: FlBorderData(show: true),
      lineBarsData: [
        // Total operations
        LineChartBarData(
          spots: dailyMetrics.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.totalOperations.toDouble());
          }).toList(),
          isCurved: true,
          color: Colors.blue,
          barWidth: 2,
          dotData: FlDotData(show: false),
        ),
        // Successful operations
        LineChartBarData(
          spots: dailyMetrics.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.successfulOperations.toDouble());
          }).toList(),
          isCurved: true,
          color: Colors.green,
          barWidth: 2,
          dotData: FlDotData(show: false),
        ),
        // Failed operations
        LineChartBarData(
          spots: dailyMetrics.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.failedOperations.toDouble());
          }).toList(),
          isCurved: true,
          color: Colors.red,
          barWidth: 2,
          dotData: FlDotData(show: false),
        ),
      ],
    );
  }

  LineChartData _buildQueueDepthChartData(List<QueueDepthSample> samples) {
    return LineChartData(
      gridData: FlGridData(show: true),
      titlesData: FlTitlesData(
        leftTitles: AxisTitles(
          sideTitles: SideTitles(showTitles: true, reservedSize: 40),
        ),
        bottomTitles: AxisTitles(
          sideTitles: SideTitles(showTitles: false),
        ),
        rightTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
        topTitles: AxisTitles(sideTitles: SideTitles(showTitles: false)),
      ),
      borderData: FlBorderData(show: true),
      lineBarsData: [
        LineChartBarData(
          spots: samples.asMap().entries.map((entry) {
            return FlSpot(entry.key.toDouble(), entry.value.depth.toDouble());
          }).toList(),
          isCurved: true,
          color: Colors.purple,
          barWidth: 2,
          dotData: FlDotData(show: false),
        ),
      ],
    );
  }

  String _formatBytes(int bytes) {
    if (bytes < 1024) return '$bytes B';
    if (bytes < 1024 * 1024) return '${(bytes / 1024).toStringAsFixed(2)} KB';
    return '${(bytes / (1024 * 1024)).toStringAsFixed(2)} MB';
  }

  String _formatDuration(Duration duration) {
    if (duration.inSeconds < 1) return '${duration.inMilliseconds}ms';
    if (duration.inMinutes < 1) return '${duration.inSeconds}s';
    return '${duration.inMinutes}m ${duration.inSeconds % 60}s';
  }

  String _getOperationTypeText(SyncOperationType type) {
    switch (type) {
      case SyncOperationType.upload:
        return 'رفع';
      case SyncOperationType.download:
        return 'تحميل';
      case SyncOperationType.conflict:
        return 'تعارض';
    }
  }

  String _getConflictResolutionText(ConflictResolution resolution) {
    switch (resolution) {
      case ConflictResolution.serverWins:
        return 'السيرفر يفوز';
      case ConflictResolution.localWins:
        return 'المحلي يفوز';
      case ConflictResolution.merged:
        return 'دمج';
      case ConflictResolution.manual:
        return 'يدوي';
    }
  }
}
