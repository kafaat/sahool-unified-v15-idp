/// Crop Profitability Screen - شاشة ربحية المحصول
/// Individual crop analysis with detailed metrics
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/profitability_models.dart';
import '../providers/profitability_provider.dart';
import '../widgets/cost_breakdown_widget.dart';
import '../widgets/profit_chart_widget.dart';

class CropProfitabilityScreen extends ConsumerStatefulWidget {
  final String profitabilityId;

  const CropProfitabilityScreen({
    super.key,
    required this.profitabilityId,
  });

  @override
  ConsumerState<CropProfitabilityScreen> createState() =>
      _CropProfitabilityScreenState();
}

class _CropProfitabilityScreenState extends ConsumerState<CropProfitabilityScreen> {
  final String locale = 'ar';

  @override
  void initState() {
    super.initState();
    // Load profitability data
    Future.microtask(() {
      ref
          .read(profitabilityProvider.notifier)
          .getProfitabilityById(widget.profitabilityId);
    });
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final profitabilityState = ref.watch(profitabilityProvider);
    final currencyFormat = NumberFormat('#,##0', 'ar');

    return Scaffold(
      appBar: AppBar(
        title: Text(
          locale == 'ar' ? 'تحليل ربحية المحصول' : 'Crop Profitability',
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () => _shareReport(profitabilityState.data),
            tooltip: locale == 'ar' ? 'مشاركة' : 'Share',
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf),
            onPressed: () => _exportPdf(profitabilityState.data),
            tooltip: locale == 'ar' ? 'تصدير PDF' : 'Export PDF',
          ),
        ],
      ),
      body: profitabilityState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : profitabilityState.error != null
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
                            ? profitabilityState.errorAr ??
                                profitabilityState.error!
                            : profitabilityState.error!,
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
              : profitabilityState.data == null
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
                          // Header Card
                          _buildHeaderCard(profitabilityState.data!),
                          const SizedBox(height: 16),

                          // Key Metrics
                          _buildKeyMetricsGrid(
                            profitabilityState.data!,
                            currencyFormat,
                          ),
                          const SizedBox(height: 16),

                          // Revenue vs Costs Chart
                          RevenueVsCostsChart(
                            profitability: profitabilityState.data!,
                            locale: locale,
                          ),
                          const SizedBox(height: 16),

                          // ROI Card
                          _buildRoiCard(profitabilityState.data!, currencyFormat),
                          const SizedBox(height: 16),

                          // Break-Even Analysis
                          if (profitabilityState.data!.breakEvenAnalysis != null)
                            _buildBreakEvenCard(
                              profitabilityState.data!.breakEvenAnalysis!,
                              currencyFormat,
                            ),
                          const SizedBox(height: 16),

                          // Cost Breakdown
                          CostBreakdownWidget(
                            costsByType: profitabilityState.data!.getCostsByType(),
                            totalCosts: profitabilityState.data!.totalCosts,
                            locale: locale,
                          ),
                          const SizedBox(height: 16),

                          // Detailed Cost List
                          DetailedCostListWidget(
                            costs: profitabilityState.data!.costs,
                            locale: locale,
                          ),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildHeaderCard(CropProfitability profitability) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat('yyyy-MM-dd', locale);

    return Card(
      elevation: 2,
      color: theme.colorScheme.primaryContainer.withOpacity(0.3),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.agriculture,
                  color: theme.colorScheme.primary,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        profitability.getCropName(locale),
                        style: theme.textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        profitability.getFieldName(locale),
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: Colors.grey.shade700,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Divider(),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildInfoItem(
                  locale == 'ar' ? 'الموسم' : 'Season',
                  profitability.getSeason(locale),
                ),
                _buildInfoItem(
                  locale == 'ar' ? 'المساحة' : 'Area',
                  '${profitability.area.toStringAsFixed(2)} ${locale == 'ar' ? 'هكتار' : 'ha'}',
                ),
                _buildInfoItem(
                  locale == 'ar' ? 'الإنتاجية' : 'Yield',
                  '${profitability.yield.toStringAsFixed(2)} ${locale == 'ar' ? 'طن/هكتار' : 't/ha'}',
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _buildInfoItem(
                  locale == 'ar' ? 'تاريخ البدء' : 'Start Date',
                  dateFormat.format(profitability.startDate),
                ),
                if (profitability.endDate != null)
                  _buildInfoItem(
                    locale == 'ar' ? 'تاريخ الانتهاء' : 'End Date',
                    dateFormat.format(profitability.endDate!),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoItem(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey,
              ),
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.w500,
              ),
        ),
      ],
    );
  }

  Widget _buildKeyMetricsGrid(
    CropProfitability profitability,
    NumberFormat currencyFormat,
  ) {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildMetricCard(
          title: locale == 'ar' ? 'إجمالي الإيرادات' : 'Total Revenue',
          value: currencyFormat.format(profitability.totalRevenue),
          subtitle: locale == 'ar' ? 'ريال يمني' : 'YER',
          icon: Icons.attach_money,
          color: Colors.green,
        ),
        _buildMetricCard(
          title: locale == 'ar' ? 'إجمالي التكاليف' : 'Total Costs',
          value: currencyFormat.format(profitability.totalCosts),
          subtitle: locale == 'ar' ? 'ريال يمني' : 'YER',
          icon: Icons.money_off,
          color: Colors.red,
        ),
        _buildMetricCard(
          title: locale == 'ar' ? 'صافي الربح' : 'Net Profit',
          value: currencyFormat.format(profitability.netProfit),
          subtitle: locale == 'ar' ? 'ريال يمني' : 'YER',
          icon: profitability.isProfitable ? Icons.trending_up : Icons.trending_down,
          color: profitability.isProfitable ? Colors.green : Colors.orange,
        ),
        _buildMetricCard(
          title: locale == 'ar' ? 'هامش الربح' : 'Profit Margin',
          value: '${profitability.profitMargin.toStringAsFixed(1)}%',
          subtitle: locale == 'ar' ? 'نسبة مئوية' : 'Percentage',
          icon: Icons.percent,
          color: Colors.blue,
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
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                Icon(icon, color: color, size: 18),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    title,
                    style: Theme.of(context).textTheme.bodySmall,
                    overflow: TextOverflow.ellipsis,
                    maxLines: 2,
                  ),
                ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: color,
                      ),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  subtitle,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRoiCard(CropProfitability profitability, NumberFormat currencyFormat) {
    final theme = Theme.of(context);

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.analytics, color: Colors.purple),
                const SizedBox(width: 8),
                Text(
                  locale == 'ar' ? 'العائد على الاستثمار' : 'Return on Investment',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Center(
              child: Container(
                padding: const EdgeInsets.all(24),
                decoration: BoxDecoration(
                  color: Colors.purple.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Column(
                  children: [
                    Text(
                      '${profitability.roi.toStringAsFixed(1)}%',
                      style: theme.textTheme.displaySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.purple,
                      ),
                    ),
                    Text(
                      'ROI',
                      style: theme.textTheme.bodyMedium?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                Column(
                  children: [
                    Text(
                      currencyFormat.format(profitability.revenuePerHectare),
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.green,
                      ),
                    ),
                    Text(
                      locale == 'ar' ? 'إيرادات/هكتار' : 'Revenue/ha',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
                Column(
                  children: [
                    Text(
                      currencyFormat.format(profitability.costPerHectare),
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.red,
                      ),
                    ),
                    Text(
                      locale == 'ar' ? 'تكاليف/هكتار' : 'Costs/ha',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
                Column(
                  children: [
                    Text(
                      currencyFormat.format(profitability.profitPerHectare),
                      style: theme.textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                    Text(
                      locale == 'ar' ? 'ربح/هكتار' : 'Profit/ha',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.grey,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBreakEvenCard(
    BreakEvenAnalysis breakEven,
    NumberFormat currencyFormat,
  ) {
    final theme = Theme.of(context);
    final safetyMargin = breakEven.getSafetyMargin();

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.balance, color: Colors.orange),
                const SizedBox(width: 8),
                Text(
                  locale == 'ar' ? 'تحليل نقطة التعادل' : 'Break-Even Analysis',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            _buildBreakEvenRow(
              locale == 'ar' ? 'كمية التعادل' : 'Break-Even Quantity',
              '${breakEven.breakEvenQuantity.toStringAsFixed(2)} ${breakEven.getUnit(locale)}',
            ),
            const SizedBox(height: 8),
            _buildBreakEvenRow(
              locale == 'ar' ? 'إيرادات التعادل' : 'Break-Even Revenue',
              '${currencyFormat.format(breakEven.breakEvenRevenue)} ${locale == 'ar' ? 'ريال' : 'YER'}',
            ),
            const SizedBox(height: 8),
            _buildBreakEvenRow(
              locale == 'ar' ? 'هامش الأمان' : 'Safety Margin',
              '${safetyMargin.toStringAsFixed(1)}%',
              color: safetyMargin > 0 ? Colors.green : Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBreakEvenRow(String label, String value, {Color? color}) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodyMedium,
        ),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
        ),
      ],
    );
  }

  void _shareReport(CropProfitability? profitability) {
    if (profitability == null) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          locale == 'ar' ? 'مشاركة التقرير...' : 'Sharing report...',
        ),
      ),
    );
  }

  void _exportPdf(CropProfitability? profitability) {
    if (profitability == null) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          locale == 'ar' ? 'تصدير PDF...' : 'Exporting PDF...',
        ),
      ),
    );
  }

  void _refresh() {
    ref
        .read(profitabilityProvider.notifier)
        .getProfitabilityById(widget.profitabilityId);
  }
}
