/// Report Viewer Screen - شاشة عرض التقرير
/// Display generated report with charts and export options
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_data.dart';
import '../../domain/models/report_template.dart';
import '../../domain/models/chart_config.dart';
import '../widgets/chart_widget.dart';
import '../widgets/report_data_table.dart';
import '../widgets/export_button.dart';
import '../../state/reports_providers.dart';
import 'report_share_screen.dart';

/// Report Viewer Screen
/// شاشة عرض التقرير
class ReportViewerScreen extends ConsumerStatefulWidget {
  final String? reportId;
  final ReportData? report;

  const ReportViewerScreen({
    super.key,
    this.reportId,
    this.report,
  }) : assert(reportId != null || report != null);

  @override
  ConsumerState<ReportViewerScreen> createState() => _ReportViewerScreenState();
}

class _ReportViewerScreenState extends ConsumerState<ReportViewerScreen> {
  bool _isExporting = false;

  @override
  Widget build(BuildContext context) {
    // Use provided report or fetch from repository
    final reportData = widget.report;

    if (reportData != null) {
      return _buildReportView(reportData);
    }

    // Fetch report by ID
    final reportAsync = ref.watch(reportByIdProvider(widget.reportId!));

    return reportAsync.when(
      data: (report) {
        if (report == null) {
          return _buildNotFoundView();
        }
        return _buildReportView(report);
      },
      loading: () => Scaffold(
        appBar: AppBar(
          title: const Text('جاري التحميل...'),
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
        ),
        body: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, stack) => _buildErrorView(error.toString()),
    );
  }

  Widget _buildReportView(ReportData report) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(report.titleAr),
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              icon: const Icon(Icons.share),
              onPressed: () => _shareReport(report),
            ),
            PopupMenuButton<String>(
              icon: const Icon(Icons.more_vert),
              onSelected: (value) => _handleMenuAction(value, report),
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'pdf',
                  child: ListTile(
                    leading: Icon(Icons.picture_as_pdf),
                    title: Text('تصدير PDF'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
                const PopupMenuItem(
                  value: 'excel',
                  child: ListTile(
                    leading: Icon(Icons.table_chart),
                    title: Text('تصدير Excel'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
                const PopupMenuItem(
                  value: 'share',
                  child: ListTile(
                    leading: Icon(Icons.send),
                    title: Text('مشاركة'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
              ],
            ),
          ],
        ),
        body: report.isGenerating
            ? _buildGeneratingView()
            : report.hasError
                ? _buildReportErrorView(report)
                : _buildReportContent(report),
        bottomNavigationBar: _buildBottomBar(report),
      ),
    );
  }

  Widget _buildGeneratingView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(),
          const SizedBox(height: 24),
          Text(
            'جاري توليد التقرير...',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[700],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'قد يستغرق هذا بضع ثوانٍ',
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildReportErrorView(ReportData report) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            'فشل في توليد التقرير',
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: Colors.grey[700],
            ),
          ),
          if (report.errorMessage != null) ...[
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                report.errorMessage!,
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey[500]),
              ),
            ),
          ],
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => Navigator.pop(context),
            icon: const Icon(Icons.arrow_back),
            label: const Text('العودة'),
          ),
        ],
      ),
    );
  }

  Widget _buildReportContent(ReportData report) {
    return RefreshIndicator(
      onRefresh: () async {
        if (widget.reportId != null) {
          ref.invalidate(reportByIdProvider(widget.reportId!));
        }
      },
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Report header
            _buildReportHeader(report),
            const SizedBox(height: 16),

            // Summary stats
            if (report.summaryStats.isNotEmpty) ...[
              _buildSummaryStats(report),
              const SizedBox(height: 24),
            ],

            // Report sections
            ...report.visibleSections.map((section) => _buildSection(section)),

            // Footer
            const SizedBox(height: 32),
            _buildReportFooter(report),
          ],
        ),
      ),
    );
  }

  Widget _buildReportHeader(ReportData report) {
    return Card(
      elevation: 0,
      color: SahoolColors.primary.withValues(alpha: 0.05),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: SahoolColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Icon(
                    _getTemplateIcon(report.template.type),
                    color: SahoolColors.primary,
                    size: 24,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        report.template.nameAr,
                        style: const TextStyle(
                          color: SahoolColors.primary,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        report.filter.dateRange.formattedAr,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                if (report.isOffline)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: Colors.orange.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.offline_bolt, size: 14, color: Colors.orange[700]),
                        const SizedBox(width: 4),
                        Text(
                          'محلي',
                          style: TextStyle(
                            fontSize: 11,
                            color: Colors.orange[700],
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryStats(ReportData report) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'ملخص التقرير',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.8,
          ),
          itemCount: report.summaryStats.length,
          itemBuilder: (context, index) {
            final stat = report.summaryStats[index];
            return _buildStatCard(stat);
          },
        ),
      ],
    );
  }

  Widget _buildStatCard(SummaryStat stat) {
    final color = stat.colorHex != null
        ? Color(int.parse(stat.colorHex!.replaceFirst('#', '0xFF')))
        : SahoolColors.primary;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                if (stat.iconName != null)
                  Icon(
                    _getIconByName(stat.iconName!),
                    color: color,
                    size: 18,
                  ),
                const Spacer(),
                if (stat.changePercent != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: (stat.isPositiveChange ?? true)
                          ? Colors.green.withValues(alpha: 0.1)
                          : Colors.red.withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          (stat.isPositiveChange ?? true)
                              ? Icons.arrow_upward
                              : Icons.arrow_downward,
                          size: 10,
                          color: (stat.isPositiveChange ?? true)
                              ? Colors.green
                              : Colors.red,
                        ),
                        Text(
                          '${stat.changePercent!.abs().toStringAsFixed(1)}%',
                          style: TextStyle(
                            fontSize: 10,
                            color: (stat.isPositiveChange ?? true)
                                ? Colors.green
                                : Colors.red,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.baseline,
                  textBaseline: TextBaseline.alphabetic,
                  children: [
                    Text(
                      stat.value,
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                    ),
                    if (stat.unit != null) ...[
                      const SizedBox(width: 4),
                      Text(
                        stat.unit!,
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ],
                ),
                Text(
                  stat.labelAr,
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(ReportSection section) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          section.titleAr,
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        if (section.type == 'chart' && section.chartConfig != null)
          _buildChartSection(section.chartConfig!)
        else if (section.type == 'table' && section.data['table'] != null)
          _buildTableSection(section.data['table'] as Map<String, dynamic>)
        else if (section.type == 'text')
          _buildTextSection(section.data)
        else
          _buildGenericSection(section),
        const SizedBox(height: 24),
      ],
    );
  }

  Widget _buildChartSection(ChartConfig config) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: ChartWidget(config: config),
      ),
    );
  }

  Widget _buildTableSection(Map<String, dynamic> tableData) {
    final table = ReportTableData.fromJson(tableData);
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ReportDataTable(data: table),
    );
  }

  Widget _buildTextSection(Map<String, dynamic> data) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          data['content']?.toString() ?? '',
          style: TextStyle(color: Colors.grey[700]),
        ),
      ),
    );
  }

  Widget _buildGenericSection(ReportSection section) {
    return Card(
      elevation: 1,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Text(
          'محتوى القسم: ${section.type}',
          style: TextStyle(color: Colors.grey[500]),
        ),
      ),
    );
  }

  Widget _buildReportFooter(ReportData report) {
    return Center(
      child: Column(
        children: [
          Divider(color: Colors.grey[200]),
          const SizedBox(height: 8),
          Text(
            'تم توليد التقرير: ${_formatDateTime(report.generatedAt)}',
            style: TextStyle(fontSize: 12, color: Colors.grey[500]),
          ),
          if (report.isOffline) ...[
            const SizedBox(height: 4),
            Text(
              'تم التوليد بدون اتصال',
              style: TextStyle(fontSize: 11, color: Colors.orange[600]),
            ),
          ],
          const SizedBox(height: 16),
          Text(
            'SAHOOL - منصة الذكاء الزراعي',
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[400],
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBottomBar(ReportData report) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            Expanded(
              child: ExportButton(
                report: report,
                format: ExportFormat.pdf,
                isLoading: _isExporting,
                onExport: () => _exportReport(report, ExportFormat.pdf),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ExportButton(
                report: report,
                format: ExportFormat.excel,
                isLoading: _isExporting,
                onExport: () => _exportReport(report, ExportFormat.excel),
              ),
            ),
            const SizedBox(width: 12),
            IconButton(
              onPressed: () => _shareReport(report),
              icon: const Icon(Icons.share),
              style: IconButton.styleFrom(
                backgroundColor: SahoolColors.primary.withValues(alpha: 0.1),
                foregroundColor: SahoolColors.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildNotFoundView() {
    return Scaffold(
      appBar: AppBar(
        title: const Text('التقرير غير موجود'),
        backgroundColor: SahoolColors.primary,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey[300]),
            const SizedBox(height: 16),
            Text(
              'التقرير غير موجود',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.arrow_back),
              label: const Text('العودة'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorView(String error) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('خطأ'),
        backgroundColor: SahoolColors.primary,
        foregroundColor: Colors.white,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
            const SizedBox(height: 16),
            Text(
              'حدث خطأ',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 32),
              child: Text(
                error,
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey[500]),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.arrow_back),
              label: const Text('العودة'),
            ),
          ],
        ),
      ),
    );
  }

  void _handleMenuAction(String action, ReportData report) {
    switch (action) {
      case 'pdf':
        _exportReport(report, ExportFormat.pdf);
        break;
      case 'excel':
        _exportReport(report, ExportFormat.excel);
        break;
      case 'share':
        _shareReport(report);
        break;
    }
  }

  Future<void> _exportReport(ReportData report, ExportFormat format) async {
    if (_isExporting) return;

    setState(() => _isExporting = true);

    try {
      final repository = ref.read(reportsRepositoryProvider);
      String? filePath;

      if (format == ExportFormat.pdf) {
        filePath = await repository.exportToPdf(report);
      } else if (format == ExportFormat.excel) {
        filePath = await repository.exportToExcel(report);
      }

      if (filePath != null && mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('تم حفظ التقرير: $filePath'),
            backgroundColor: SahoolColors.success,
            action: SnackBarAction(
              label: 'مشاركة',
              textColor: Colors.white,
              onPressed: () => Share.shareXFiles([XFile(filePath!)]),
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل في تصدير التقرير: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isExporting = false);
      }
    }
  }

  void _shareReport(ReportData report) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReportShareScreen(report: report),
      ),
    );
  }

  IconData _getTemplateIcon(ReportType type) {
    switch (type) {
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

  IconData _getIconByName(String name) {
    const icons = {
      'eco': Icons.eco,
      'favorite': Icons.favorite,
      'water_drop': Icons.water_drop,
      'task_alt': Icons.task_alt,
      'check_circle': Icons.check_circle,
      'trending_up': Icons.trending_up,
      'trending_down': Icons.trending_down,
      'pending': Icons.pending,
      'warning': Icons.warning,
      'show_chart': Icons.show_chart,
      'analytics': Icons.analytics,
      'swap_vert': Icons.swap_vert,
      'speed': Icons.speed,
      'savings': Icons.savings,
      'event': Icons.event,
      'thermostat': Icons.thermostat,
      'opacity': Icons.opacity,
      'air': Icons.air,
      'account_balance': Icons.account_balance,
      'verified': Icons.verified,
      'payments': Icons.payments,
      'percent': Icons.percent,
    };
    return icons[name] ?? Icons.info;
  }

  String _formatDateTime(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
