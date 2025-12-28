/// GDD Chart Screen - شاشة الرسم البياني لدرجات النمو الحراري
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/gdd_models.dart';
import '../providers/gdd_provider.dart';
import '../widgets/gdd_chart_widget.dart';

/// شاشة الرسم البياني لـ GDD
class GDDChartScreen extends ConsumerStatefulWidget {
  final String fieldId;

  const GDDChartScreen({
    super.key,
    required this.fieldId,
  });

  @override
  ConsumerState<GDDChartScreen> createState() => _GDDChartScreenState();
}

class _GDDChartScreenState extends ConsumerState<GDDChartScreen> {
  DateTime? _startDate;
  DateTime? _endDate;
  bool _showForecast = true;
  bool _showStages = true;
  ChartViewMode _viewMode = ChartViewMode.accumulated;

  @override
  void initState() {
    super.initState();
    // تعيين نطاق التاريخ الافتراضي (آخر 30 يوم)
    _endDate = DateTime.now();
    _startDate = _endDate!.subtract(const Duration(days: 30));
  }

  @override
  Widget build(BuildContext context) {
    final chartParams = GDDChartParams(
      fieldId: widget.fieldId,
      startDate: _startDate,
      endDate: _endDate,
      includeForecast: _showForecast,
      forecastDays: 7,
      includeStages: _showStages,
      limit: 365,
    );

    final chartDataAsync = ref.watch(gddChartDataProvider(chartParams));

    return Scaffold(
      appBar: AppBar(
        title: const Text('الرسم البياني - GDD'),
        actions: [
          // اختيار نطاق التاريخ
          IconButton(
            icon: const Icon(Icons.date_range),
            onPressed: () => _selectDateRange(context),
          ),
          // خيارات العرض
          PopupMenuButton<String>(
            icon: const Icon(Icons.more_vert),
            onSelected: (value) {
              setState(() {
                switch (value) {
                  case 'forecast':
                    _showForecast = !_showForecast;
                    break;
                  case 'stages':
                    _showStages = !_showStages;
                    break;
                  case 'view_accumulated':
                    _viewMode = ChartViewMode.accumulated;
                    break;
                  case 'view_daily':
                    _viewMode = ChartViewMode.daily;
                    break;
                }
              });
            },
            itemBuilder: (context) => [
              CheckedPopupMenuItem<String>(
                value: 'forecast',
                checked: _showForecast,
                child: const Text('عرض التوقعات'),
              ),
              CheckedPopupMenuItem<String>(
                value: 'stages',
                checked: _showStages,
                child: const Text('عرض مراحل النمو'),
              ),
              const PopupMenuDivider(),
              PopupMenuItem<String>(
                value: 'view_accumulated',
                child: Row(
                  children: [
                    if (_viewMode == ChartViewMode.accumulated)
                      const Icon(Icons.check, size: 20),
                    if (_viewMode != ChartViewMode.accumulated)
                      const SizedBox(width: 20),
                    const SizedBox(width: 8),
                    const Text('GDD المتراكم'),
                  ],
                ),
              ),
              PopupMenuItem<String>(
                value: 'view_daily',
                child: Row(
                  children: [
                    if (_viewMode == ChartViewMode.daily)
                      const Icon(Icons.check, size: 20),
                    if (_viewMode != ChartViewMode.daily)
                      const SizedBox(width: 20),
                    const SizedBox(width: 8),
                    const Text('GDD اليومي'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(gddChartDataProvider);
        },
        child: chartDataAsync.when(
          data: (chartData) => _buildChart(context, chartData),
          loading: () => const Center(child: CircularProgressIndicator()),
          error: (error, stack) => _buildErrorState(context, error),
        ),
      ),
    );
  }

  Widget _buildChart(BuildContext context, GDDChartData chartData) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // معلومات النطاق الزمني
          _buildDateRangeInfo(context),
          const SizedBox(height: 16),

          // الرسم البياني
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _viewMode == ChartViewMode.accumulated
                        ? 'GDD المتراكم'
                        : 'GDD اليومي',
                    style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                  const SizedBox(height: 16),
                  GDDChartWidget(
                    records: chartData.records,
                    forecasts: _showForecast ? chartData.forecasts : [],
                    stages: _showStages ? chartData.stages : [],
                    viewMode: _viewMode,
                    height: 300,
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // إحصائيات
          _buildStatistics(context, chartData),
          const SizedBox(height: 16),

          // مراحل النمو
          if (_showStages && chartData.stages.isNotEmpty) ...[
            _buildStagesLegend(context, chartData.stages),
            const SizedBox(height: 16),
          ],

          // التوقعات
          if (_showForecast && chartData.forecasts.isNotEmpty) ...[
            _buildForecastInfo(context, chartData.forecasts),
          ],
        ],
      ),
    );
  }

  Widget _buildDateRangeInfo(BuildContext context) {
    final dateFormat = DateFormat('dd MMM yyyy', Localizations.localeOf(context).languageCode);
    return Card(
      color: Theme.of(context).primaryColor.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Icon(Icons.date_range, color: Theme.of(context).primaryColor),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'الفترة الزمنية',
                    style: Theme.of(context).textTheme.bodySmall,
                  ),
                  Text(
                    '${dateFormat.format(_startDate!)} - ${dateFormat.format(_endDate!)}',
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ],
              ),
            ),
            TextButton.icon(
              onPressed: () => _selectDateRange(context),
              icon: const Icon(Icons.edit),
              label: const Text('تغيير'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatistics(BuildContext context, GDDChartData chartData) {
    if (chartData.records.isEmpty) {
      return const SizedBox.shrink();
    }

    final totalGDD = chartData.records.last.accumulatedGDD;
    final avgDaily = chartData.records.isNotEmpty
        ? chartData.records.map((r) => r.gddValue).reduce((a, b) => a + b) /
            chartData.records.length
        : 0.0;
    final maxDaily = chartData.records.isNotEmpty
        ? chartData.records.map((r) => r.gddValue).reduce((a, b) => a > b ? a : b)
        : 0.0;
    final minDaily = chartData.records.isNotEmpty
        ? chartData.records.map((r) => r.gddValue).reduce((a, b) => a < b ? a : b)
        : 0.0;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'إحصائيات',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const Divider(height: 24),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    context,
                    'المجموع',
                    totalGDD.toStringAsFixed(0),
                    Colors.blue,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    'متوسط يومي',
                    avgDaily.toStringAsFixed(1),
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
                    context,
                    'أقصى يومي',
                    maxDaily.toStringAsFixed(1),
                    Colors.orange,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    'أدنى يومي',
                    minDaily.toStringAsFixed(1),
                    Colors.purple,
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
    BuildContext context,
    String label,
    String value,
    Color color,
  ) {
    return Column(
      children: [
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey.shade600,
              ),
        ),
      ],
    );
  }

  Widget _buildStagesLegend(BuildContext context, List<GrowthStage> stages) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'مراحل النمو',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const Divider(height: 24),
            ...stages.map((stage) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Row(
                  children: [
                    Container(
                      width: 4,
                      height: 24,
                      color: _getStageColor(stage.stageNumber),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        stage.getName('ar'),
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                    Text(
                      '${stage.gddRequired.toStringAsFixed(0)} GDD',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey.shade600,
                          ),
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

  Widget _buildForecastInfo(BuildContext context, List<GDDForecast> forecasts) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.cloud, color: Theme.of(context).primaryColor),
                const SizedBox(width: 8),
                Text(
                  'التوقعات',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const Divider(height: 24),
            ...forecasts.take(7).map((forecast) {
              final dateFormat = DateFormat('EEEE dd MMM', Localizations.localeOf(context).languageCode);
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Row(
                  children: [
                    Expanded(
                      flex: 2,
                      child: Text(
                        dateFormat.format(forecast.forecastDate),
                        style: Theme.of(context).textTheme.bodyMedium,
                      ),
                    ),
                    Expanded(
                      child: Text(
                        '${forecast.forecastGDD.toStringAsFixed(1)} GDD',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              fontWeight: FontWeight.bold,
                            ),
                      ),
                    ),
                    Text(
                      '${forecast.tMinForecast.toStringAsFixed(0)}° - ${forecast.tMaxForecast.toStringAsFixed(0)}°',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey.shade600,
                          ),
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

  Widget _buildErrorState(BuildContext context, Object error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red.shade300,
            ),
            const SizedBox(height: 16),
            Text(
              'فشل في تحميل بيانات الرسم البياني',
              style: Theme.of(context).textTheme.titleMedium,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 8),
            Text(
              error.toString(),
              style: Theme.of(context).textTheme.bodySmall,
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: () {
                ref.invalidate(gddChartDataProvider);
              },
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _selectDateRange(BuildContext context) async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now().add(const Duration(days: 30)),
      initialDateRange: DateTimeRange(
        start: _startDate!,
        end: _endDate!,
      ),
      locale: const Locale('ar'),
      builder: (context, child) {
        return Theme(
          data: Theme.of(context).copyWith(
            colorScheme: Theme.of(context).colorScheme,
          ),
          child: child!,
        );
      },
    );

    if (picked != null) {
      setState(() {
        _startDate = picked.start;
        _endDate = picked.end;
      });
    }
  }

  Color _getStageColor(int stageNumber) {
    final colors = [
      Colors.green.shade300,
      Colors.blue.shade300,
      Colors.orange.shade300,
      Colors.purple.shade300,
      Colors.red.shade300,
      Colors.teal.shade300,
    ];
    return colors[stageNumber % colors.length];
  }
}

/// وضع عرض الرسم البياني
enum ChartViewMode {
  accumulated,
  daily,
}
