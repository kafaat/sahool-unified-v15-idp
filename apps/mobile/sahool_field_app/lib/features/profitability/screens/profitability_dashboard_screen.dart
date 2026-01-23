/// Profitability Dashboard Screen - شاشة لوحة معلومات الربحية
/// Main dashboard showing overall profitability metrics
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/profitability_models.dart';
import '../providers/profitability_provider.dart';
import '../widgets/cost_breakdown_widget.dart';
import '../widgets/profit_chart_widget.dart';

class ProfitabilityDashboardScreen extends ConsumerStatefulWidget {
  final String farmId;
  final String season;

  const ProfitabilityDashboardScreen({
    super.key,
    required this.farmId,
    required this.season,
  });

  @override
  ConsumerState<ProfitabilityDashboardScreen> createState() =>
      _ProfitabilityDashboardScreenState();
}

class _ProfitabilityDashboardScreenState
    extends ConsumerState<ProfitabilityDashboardScreen> {
  final String locale = 'ar';

  @override
  void initState() {
    super.initState();
    // Load season summary
    Future.microtask(() {
      ref.read(seasonSummaryProvider.notifier).getSeasonSummary(
            farmId: widget.farmId,
            season: widget.season,
          );
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final seasonState = ref.watch(seasonSummaryProvider);
    final currencyFormat = NumberFormat('#,##0', 'ar');

    return Scaffold(
      appBar: AppBar(
        title: Text(
          locale == 'ar' ? 'تحليل الربحية' : 'Profitability Analysis',
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: _showFilterDialog,
            tooltip: locale == 'ar' ? 'تصفية' : 'Filter',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
            tooltip: locale == 'ar' ? 'تحديث' : 'Refresh',
          ),
        ],
      ),
      body: seasonState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : seasonState.error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        Icons.error_outline,
                        size: 64,
                        color: theme.colorScheme.error,
                      ),
                      const SizedBox(height: 16),
                      Text(
                        locale == 'ar'
                            ? seasonState.errorAr ?? seasonState.error!
                            : seasonState.error!,
                        style: theme.textTheme.bodyLarge,
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _refresh,
                        icon: const Icon(Icons.refresh),
                        label: Text(locale == 'ar' ? 'إعادة المحاولة' : 'Retry'),
                      ),
                    ],
                  ),
                )
              : seasonState.data == null
                  ? Center(
                      child: Text(
                        locale == 'ar' ? 'لا توجد بيانات' : 'No data available',
                        style: theme.textTheme.bodyLarge,
                      ),
                    )
                  : RefreshIndicator(
                      onRefresh: () async => _refresh(),
                      child: ListView(
                        padding: const EdgeInsets.all(16),
                        children: [
                          // Summary Cards
                          _buildSummaryCards(seasonState.data!, currencyFormat),
                          const SizedBox(height: 16),

                          // Profit Margin
                          _buildProfitMarginCard(seasonState.data!, currencyFormat),
                          const SizedBox(height: 16),

                          // Top Performing Crops
                          _buildTopCropsCard(seasonState.data!),
                          const SizedBox(height: 16),

                          // Cost Breakdown
                          if (seasonState.data!.costsByCategory.isNotEmpty)
                            _buildCostBreakdownCard(seasonState.data!),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildSummaryCards(SeasonSummary summary, NumberFormat currencyFormat) {
    return Row(
      children: [
        Expanded(
          child: _buildMetricCard(
            title: locale == 'ar' ? 'إجمالي الإيرادات' : 'Total Revenue',
            value: '${currencyFormat.format(summary.totalRevenue)}',
            subtitle: locale == 'ar' ? 'ريال يمني' : 'YER',
            icon: Icons.trending_up,
            color: Colors.green,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: _buildMetricCard(
            title: locale == 'ar' ? 'إجمالي التكاليف' : 'Total Costs',
            value: '${currencyFormat.format(summary.totalCosts)}',
            subtitle: locale == 'ar' ? 'ريال يمني' : 'YER',
            icon: Icons.trending_down,
            color: Colors.red,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color color,
  }) {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 20),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.bodySmall,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              value,
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
            ),
            Text(
              subtitle,
              style: Theme.of(context).textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfitMarginCard(SeasonSummary summary, NumberFormat currencyFormat) {
    final theme = Theme.of(context);
    final isProfitable = summary.netProfit > 0;

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  isProfitable ? Icons.check_circle : Icons.warning,
                  color: isProfitable ? Colors.green : Colors.orange,
                  size: 24,
                ),
                const SizedBox(width: 8),
                Text(
                  locale == 'ar' ? 'صافي الربح' : 'Net Profit',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${currencyFormat.format(summary.netProfit)} ${locale == 'ar' ? 'ريال' : 'YER'}',
                      style: theme.textTheme.headlineSmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: isProfitable ? Colors.green : Colors.orange,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      locale == 'ar' ? 'صافي الربح' : 'Net Profit',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: isProfitable
                        ? Colors.green.withOpacity(0.1)
                        : Colors.orange.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${summary.profitMargin.toStringAsFixed(1)}%',
                    style: theme.textTheme.titleLarge?.copyWith(
                      fontWeight: FontWeight.bold,
                      color: isProfitable ? Colors.green : Colors.orange,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            LinearProgressIndicator(
              value: summary.profitMargin / 100,
              backgroundColor: Colors.grey.shade300,
              color: isProfitable ? Colors.green : Colors.orange,
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  locale == 'ar' ? 'هامش الربح' : 'Profit Margin',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
                ),
                Text(
                  locale == 'ar'
                      ? 'متوسط ROI: ${summary.avgRoi.toStringAsFixed(1)}%'
                      : 'Avg ROI: ${summary.avgRoi.toStringAsFixed(1)}%',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: Colors.grey,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTopCropsCard(SeasonSummary summary) {
    final theme = Theme.of(context);
    final topCrops = summary.getTopCropsByProfit(limit: 5);
    final currencyFormat = NumberFormat('#,##0', 'ar');

    return Card(
      elevation: 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.star, color: Colors.amber),
                const SizedBox(width: 8),
                Text(
                  locale == 'ar' ? 'أفضل المحاصيل' : 'Top Performing Crops',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: topCrops.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final crop = topCrops[index];
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: Colors.green.withOpacity(0.1),
                  child: Text(
                    '${index + 1}',
                    style: const TextStyle(
                      color: Colors.green,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Text(crop.getCropName(locale)),
                subtitle: Text(
                  '${locale == 'ar' ? 'المساحة' : 'Area'}: ${crop.area.toStringAsFixed(2)} ${locale == 'ar' ? 'هكتار' : 'ha'}',
                ),
                trailing: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text(
                      '${currencyFormat.format(crop.netProfit)} ${locale == 'ar' ? 'ريال' : 'YER'}',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    Text(
                      '${crop.profitMargin.toStringAsFixed(1)}%',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
                onTap: () => _navigateToCropDetails(crop),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildCostBreakdownCard(SeasonSummary summary) {
    // Convert string keys to CostType enum
    final costsByType = <CostType, double>{};
    summary.costsByCategory.forEach((key, value) {
      final costType = CostType.values.firstWhere(
        (e) => e.value == key,
        orElse: () => CostType.other,
      );
      costsByType[costType] = value;
    });

    return CostBreakdownWidget(
      costsByType: costsByType,
      totalCosts: summary.totalCosts,
      locale: locale,
    );
  }

  void _navigateToCropDetails(CropProfitability crop) {
    Navigator.of(context).pushNamed(
      '/profitability/crop',
      arguments: crop.profitabilityId,
    );
  }

  void _showFilterDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(locale == 'ar' ? 'تصفية' : 'Filter'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Add filter options here
            Text(locale == 'ar' ? 'قريباً...' : 'Coming soon...'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(locale == 'ar' ? 'إلغاء' : 'Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              _refresh();
            },
            child: Text(locale == 'ar' ? 'تطبيق' : 'Apply'),
          ),
        ],
      ),
    );
  }

  void _refresh() {
    ref.read(seasonSummaryProvider.notifier).getSeasonSummary(
          farmId: widget.farmId,
          season: widget.season,
        );
  }
}
