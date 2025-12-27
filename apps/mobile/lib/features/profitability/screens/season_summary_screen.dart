/// Season Summary Screen - شاشة ملخص الموسم
/// Overview of all crops performance in a season
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/profitability_models.dart';
import '../providers/profitability_provider.dart';
import '../widgets/profit_chart_widget.dart';

class SeasonSummaryScreen extends ConsumerStatefulWidget {
  final String farmId;
  final String season;

  const SeasonSummaryScreen({
    super.key,
    required this.farmId,
    required this.season,
  });

  @override
  ConsumerState<SeasonSummaryScreen> createState() => _SeasonSummaryScreenState();
}

class _SeasonSummaryScreenState extends ConsumerState<SeasonSummaryScreen> {
  final String locale = 'ar';
  String _sortBy = 'profit'; // profit, roi, revenue, cost

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
          locale == 'ar' ? 'ملخص الموسم' : 'Season Summary',
        ),
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.sort),
            tooltip: locale == 'ar' ? 'ترتيب حسب' : 'Sort by',
            onSelected: (value) {
              setState(() {
                _sortBy = value;
              });
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'profit',
                child: Text(locale == 'ar' ? 'الربح' : 'Profit'),
              ),
              PopupMenuItem(
                value: 'roi',
                child: Text(locale == 'ar' ? 'ROI' : 'ROI'),
              ),
              PopupMenuItem(
                value: 'revenue',
                child: Text(locale == 'ar' ? 'الإيرادات' : 'Revenue'),
              ),
              PopupMenuItem(
                value: 'cost',
                child: Text(locale == 'ar' ? 'التكاليف' : 'Costs'),
              ),
            ],
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf),
            onPressed: () => _exportPdf(seasonState.data),
            tooltip: locale == 'ar' ? 'تصدير PDF' : 'Export PDF',
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
                          // Season Overview
                          _buildSeasonOverview(seasonState.data!, currencyFormat),
                          const SizedBox(height: 16),

                          // Revenue per Hectare Chart
                          if (seasonState.data!.crops.isNotEmpty)
                            RevenuePerHectareChart(
                              crops: seasonState.data!.crops,
                              locale: locale,
                            ),
                          const SizedBox(height: 16),

                          // Crops Performance Table
                          _buildCropsTable(seasonState.data!, currencyFormat),
                          const SizedBox(height: 16),

                          // Rankings
                          _buildRankingsCard(seasonState.data!, currencyFormat),
                        ],
                      ),
                    ),
    );
  }

  Widget _buildSeasonOverview(SeasonSummary summary, NumberFormat currencyFormat) {
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
                  Icons.calendar_today,
                  color: theme.colorScheme.primary,
                ),
                const SizedBox(width: 8),
                Text(
                  summary.getSeason(locale),
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              summary.getFarmName(locale),
              style: theme.textTheme.bodyMedium?.copyWith(
                color: Colors.grey.shade700,
              ),
            ),
            const SizedBox(height: 16),
            const Divider(),
            const SizedBox(height: 16),
            GridView.count(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              crossAxisCount: 2,
              crossAxisSpacing: 12,
              mainAxisSpacing: 12,
              childAspectRatio: 2,
              children: [
                _buildOverviewItem(
                  locale == 'ar' ? 'عدد الحقول' : 'Fields',
                  '${summary.fieldsCount}',
                  Icons.grid_on,
                  Colors.blue,
                ),
                _buildOverviewItem(
                  locale == 'ar' ? 'المساحة الكلية' : 'Total Area',
                  '${summary.totalArea.toStringAsFixed(2)} ${locale == 'ar' ? 'هكتار' : 'ha'}',
                  Icons.crop_landscape,
                  Colors.green,
                ),
                _buildOverviewItem(
                  locale == 'ar' ? 'بداية الموسم' : 'Start Date',
                  dateFormat.format(summary.startDate),
                  Icons.event_available,
                  Colors.purple,
                ),
                _buildOverviewItem(
                  locale == 'ar' ? 'نهاية الموسم' : 'End Date',
                  summary.endDate != null
                      ? dateFormat.format(summary.endDate!)
                      : locale == 'ar'
                          ? 'مستمر'
                          : 'Ongoing',
                  Icons.event_busy,
                  Colors.orange,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewItem(String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  label,
                  style: Theme.of(context).textTheme.bodySmall,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  value,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCropsTable(SeasonSummary summary, NumberFormat currencyFormat) {
    final theme = Theme.of(context);
    final sortedCrops = _getSortedCrops(summary.crops);

    return Card(
      elevation: 2,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.table_chart),
                const SizedBox(width: 8),
                Text(
                  locale == 'ar' ? 'أداء المحاصيل' : 'Crops Performance',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
          const Divider(height: 1),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: DataTable(
              columns: [
                DataColumn(
                  label: Text(
                    locale == 'ar' ? 'المحصول' : 'Crop',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                DataColumn(
                  label: Text(
                    locale == 'ar' ? 'المساحة' : 'Area',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                DataColumn(
                  label: Text(
                    locale == 'ar' ? 'الإيرادات' : 'Revenue',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  numeric: true,
                ),
                DataColumn(
                  label: Text(
                    locale == 'ar' ? 'التكاليف' : 'Costs',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  numeric: true,
                ),
                DataColumn(
                  label: Text(
                    locale == 'ar' ? 'الربح' : 'Profit',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  numeric: true,
                ),
                DataColumn(
                  label: Text(
                    locale == 'ar' ? 'هامش الربح' : 'Margin',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  numeric: true,
                ),
                DataColumn(
                  label: Text(
                    'ROI',
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                  numeric: true,
                ),
              ],
              rows: sortedCrops.map((crop) {
                return DataRow(
                  cells: [
                    DataCell(
                      Text(crop.getCropName(locale)),
                      onTap: () => _navigateToCropDetails(crop),
                    ),
                    DataCell(
                      Text('${crop.area.toStringAsFixed(1)} ${locale == 'ar' ? 'هكتار' : 'ha'}'),
                    ),
                    DataCell(
                      Text(
                        currencyFormat.format(crop.totalRevenue),
                        style: const TextStyle(color: Colors.green),
                      ),
                    ),
                    DataCell(
                      Text(
                        currencyFormat.format(crop.totalCosts),
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                    DataCell(
                      Text(
                        currencyFormat.format(crop.netProfit),
                        style: TextStyle(
                          color: crop.isProfitable ? Colors.green : Colors.orange,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                    DataCell(
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: crop.isProfitable
                              ? Colors.green.withOpacity(0.1)
                              : Colors.orange.withOpacity(0.1),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Text(
                          '${crop.profitMargin.toStringAsFixed(1)}%',
                          style: TextStyle(
                            color: crop.isProfitable ? Colors.green : Colors.orange,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                    ),
                    DataCell(
                      Text(
                        '${crop.roi.toStringAsFixed(1)}%',
                        style: const TextStyle(
                          color: Colors.blue,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                  onSelectChanged: (_) => _navigateToCropDetails(crop),
                );
              }).toList(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRankingsCard(SeasonSummary summary, NumberFormat currencyFormat) {
    final theme = Theme.of(context);
    final topProfitCrops = summary.getTopCropsByProfit(limit: 3);
    final topRoiCrops = summary.getTopCropsByRoi(limit: 3);

    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.emoji_events, color: Colors.amber),
                const SizedBox(width: 8),
                Text(
                  locale == 'ar' ? 'التصنيفات' : 'Rankings',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        locale == 'ar' ? 'الأعلى ربحاً' : 'Top by Profit',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.green,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ...topProfitCrops.asMap().entries.map((entry) {
                        final index = entry.key;
                        final crop = entry.value;
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Row(
                            children: [
                              Container(
                                width: 24,
                                height: 24,
                                decoration: BoxDecoration(
                                  color: _getMedalColor(index),
                                  shape: BoxShape.circle,
                                ),
                                child: Center(
                                  child: Text(
                                    '${index + 1}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  crop.getCropName(locale),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Text(
                                currencyFormat.format(crop.netProfit),
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ],
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        locale == 'ar' ? 'الأعلى ROI' : 'Top by ROI',
                        style: theme.textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(height: 12),
                      ...topRoiCrops.asMap().entries.map((entry) {
                        final index = entry.key;
                        final crop = entry.value;
                        return Padding(
                          padding: const EdgeInsets.only(bottom: 8),
                          child: Row(
                            children: [
                              Container(
                                width: 24,
                                height: 24,
                                decoration: BoxDecoration(
                                  color: _getMedalColor(index),
                                  shape: BoxShape.circle,
                                ),
                                child: Center(
                                  child: Text(
                                    '${index + 1}',
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  crop.getCropName(locale),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                              Text(
                                '${crop.roi.toStringAsFixed(1)}%',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
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

  Color _getMedalColor(int index) {
    switch (index) {
      case 0:
        return const Color(0xFFFFD700); // Gold
      case 1:
        return const Color(0xFFC0C0C0); // Silver
      case 2:
        return const Color(0xFFCD7F32); // Bronze
      default:
        return Colors.grey;
    }
  }

  List<CropProfitability> _getSortedCrops(List<CropProfitability> crops) {
    final sorted = List<CropProfitability>.from(crops);
    switch (_sortBy) {
      case 'profit':
        sorted.sort((a, b) => b.netProfit.compareTo(a.netProfit));
        break;
      case 'roi':
        sorted.sort((a, b) => b.roi.compareTo(a.roi));
        break;
      case 'revenue':
        sorted.sort((a, b) => b.totalRevenue.compareTo(a.totalRevenue));
        break;
      case 'cost':
        sorted.sort((a, b) => b.totalCosts.compareTo(a.totalCosts));
        break;
    }
    return sorted;
  }

  void _navigateToCropDetails(CropProfitability crop) {
    Navigator.of(context).pushNamed(
      '/profitability/crop',
      arguments: crop.profitabilityId,
    );
  }

  void _exportPdf(SeasonSummary? summary) {
    if (summary == null) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          locale == 'ar' ? 'تصدير PDF...' : 'Exporting PDF...',
        ),
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
