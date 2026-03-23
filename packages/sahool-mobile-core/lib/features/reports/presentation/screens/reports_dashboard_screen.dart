/// Reports Dashboard Screen - شاشة لوحة التقارير
/// Main entry point for the reports feature
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_template.dart';
import '../../domain/models/report_data.dart';
import '../../state/reports_providers.dart';
import 'report_builder_screen.dart';
import 'report_viewer_screen.dart';

/// Reports Dashboard Screen
/// شاشة لوحة التقارير الرئيسية
class ReportsDashboardScreen extends ConsumerStatefulWidget {
  const ReportsDashboardScreen({super.key});

  @override
  ConsumerState<ReportsDashboardScreen> createState() => _ReportsDashboardScreenState();
}

class _ReportsDashboardScreenState extends ConsumerState<ReportsDashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('التقارير'),
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: const [
              Tab(text: 'قوالب التقارير', icon: Icon(Icons.dashboard)),
              Tab(text: 'التقارير السابقة', icon: Icon(Icons.history)),
            ],
          ),
        ),
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildTemplatesTab(),
            _buildHistoryTab(),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () => _showQuickReportDialog(context),
          backgroundColor: SahoolColors.primary,
          icon: const Icon(Icons.add, color: Colors.white),
          label: const Text('تقرير جديد', style: TextStyle(color: Colors.white)),
        ),
      ),
    );
  }

  Widget _buildTemplatesTab() {
    final templatesAsync = ref.watch(reportTemplatesProvider);

    return templatesAsync.when(
      data: (templates) => RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(reportTemplatesProvider);
        },
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Featured templates
              Text(
                'القوالب الشائعة',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 12),
              _buildFeaturedTemplates(templates.take(3).toList()),
              const SizedBox(height: 24),

              // All templates by category
              Text(
                'جميع القوالب',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
              ),
              const SizedBox(height: 12),
              _buildAllTemplates(templates),
            ],
          ),
        ),
      ),
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => _buildErrorState(error.toString()),
    );
  }

  Widget _buildFeaturedTemplates(List<ReportTemplate> templates) {
    return SizedBox(
      height: 180,
      child: ListView.separated(
        scrollDirection: Axis.horizontal,
        itemCount: templates.length,
        separatorBuilder: (_, __) => const SizedBox(width: 12),
        itemBuilder: (context, index) {
          final template = templates[index];
          return SizedBox(
            width: 280,
            child: _buildFeaturedCard(template),
          );
        },
      ),
    );
  }

  Widget _buildFeaturedCard(ReportTemplate template) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: () => _navigateToBuilder(template),
        borderRadius: BorderRadius.circular(16),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              colors: [
                SahoolColors.primary,
                SahoolColors.primary.withOpacity(0.8),
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Icon(
                      _getTemplateIcon(template.type),
                      color: Colors.white,
                      size: 28,
                    ),
                  ),
                  const Spacer(),
                  if (template.isPremium)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: SahoolColors.harvestGold,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'PRO',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    template.nameAr,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    template.descriptionAr,
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.85),
                      fontSize: 12,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAllTemplates(List<ReportTemplate> templates) {
    return ListView.separated(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: templates.length,
      separatorBuilder: (_, __) => const SizedBox(height: 8),
      itemBuilder: (context, index) {
        final template = templates[index];
        return ReportTemplateCard(
          template: template,
          onTap: () => _navigateToBuilder(template),
        );
      },
    );
  }

  Widget _buildHistoryTab() {
    final historyAsync = ref.watch(reportHistoryProvider);

    return historyAsync.when(
      data: (history) {
        if (history.isEmpty) {
          return _buildEmptyHistoryState();
        }
        return RefreshIndicator(
          onRefresh: () async {
            ref.invalidate(reportHistoryProvider);
          },
          child: ListView.separated(
            padding: const EdgeInsets.all(16),
            itemCount: history.length,
            separatorBuilder: (_, __) => const SizedBox(height: 8),
            itemBuilder: (context, index) {
              final entry = history[index];
              return ReportHistoryCard(
                entry: entry,
                onTap: () => _viewReport(entry.reportId),
              );
            },
          ),
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => _buildErrorState(error.toString()),
    );
  }

  Widget _buildEmptyHistoryState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.history,
            size: 80,
            color: Colors.grey[300],
          ),
          const SizedBox(height: 16),
          Text(
            'لا توجد تقارير سابقة',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'أنشئ تقريراً جديداً للبدء',
            style: TextStyle(
              color: Colors.grey[500],
            ),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => _tabController.animateTo(0),
            icon: const Icon(Icons.add),
            label: const Text('إنشاء تقرير'),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: Colors.red[300],
          ),
          const SizedBox(height: 16),
          Text(
            'حدث خطأ',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[700],
              fontWeight: FontWeight.bold,
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
            onPressed: () {
              ref.invalidate(reportTemplatesProvider);
              ref.invalidate(reportHistoryProvider);
            },
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  void _navigateToBuilder(ReportTemplate template) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReportBuilderScreen(template: template),
      ),
    );
  }

  void _viewReport(String reportId) {
    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => ReportViewerScreen(reportId: reportId),
      ),
    );
  }

  void _showQuickReportDialog(BuildContext context) {
    final templates = ref.read(reportTemplatesProvider).valueOrNull ?? [];

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
        ),
        padding: const EdgeInsets.all(16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Center(
              child: Container(
                width: 40,
                height: 4,
                margin: const EdgeInsets.only(bottom: 16),
                decoration: BoxDecoration(
                  color: Colors.grey[300],
                  borderRadius: BorderRadius.circular(2),
                ),
              ),
            ),
            const Text(
              'اختر نوع التقرير',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            ...templates.take(5).map((template) => ListTile(
                  leading: Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: SahoolColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Icon(
                      _getTemplateIcon(template.type),
                      color: SahoolColors.primary,
                    ),
                  ),
                  title: Text(template.nameAr),
                  subtitle: Text(
                    template.descriptionAr,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  trailing: template.isPremium
                      ? Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: SahoolColors.harvestGold.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: const Text(
                            'PRO',
                            style: TextStyle(
                              color: SahoolColors.harvestGold,
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        )
                      : const Icon(Icons.chevron_left),
                  onTap: () {
                    Navigator.pop(context);
                    _navigateToBuilder(template);
                  },
                )),
            const SizedBox(height: 16),
          ],
        ),
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
}

/// Report Template Card Widget
class ReportTemplateCard extends StatelessWidget {
  final ReportTemplate template;
  final VoidCallback onTap;

  const ReportTemplateCard({
    super.key,
    required this.template,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: SahoolColors.primary.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Icon(
                  _getIcon(),
                  color: SahoolColors.primary,
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            template.nameAr,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                        if (template.isPremium)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: SahoolColors.harvestGold.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: const Text(
                              'PRO',
                              style: TextStyle(
                                color: SahoolColors.harvestGold,
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      template.descriptionAr,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 13,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        if (template.supportsOffline) ...[
                          Icon(Icons.offline_bolt, size: 14, color: Colors.grey[500]),
                          const SizedBox(width: 4),
                          Text(
                            'يعمل بدون اتصال',
                            style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                          ),
                          const SizedBox(width: 12),
                        ],
                        Icon(Icons.calendar_today, size: 14, color: Colors.grey[500]),
                        const SizedBox(width: 4),
                        Text(
                          '${template.defaultDateRangeDays} يوم',
                          style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_left, color: Colors.grey),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getIcon() {
    switch (template.type) {
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

/// Report History Card Widget
class ReportHistoryCard extends StatelessWidget {
  final ReportHistoryEntry entry;
  final VoidCallback onTap;

  const ReportHistoryCard({
    super.key,
    required this.entry,
    required this.onTap,
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
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: SahoolColors.sageGreen.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  _getIcon(),
                  color: SahoolColors.forestGreen,
                  size: 20,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      entry.title,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.access_time, size: 12, color: Colors.grey[500]),
                        const SizedBox(width: 4),
                        Text(
                          _formatDate(entry.generatedAt),
                          style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                        ),
                        if (entry.isOffline) ...[
                          const SizedBox(width: 8),
                          Icon(Icons.offline_bolt, size: 12, color: Colors.grey[500]),
                          const SizedBox(width: 2),
                          Text(
                            'محلي',
                            style: TextStyle(fontSize: 12, color: Colors.grey[500]),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              const Icon(Icons.chevron_left, color: Colors.grey, size: 20),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getIcon() {
    switch (entry.templateType) {
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
