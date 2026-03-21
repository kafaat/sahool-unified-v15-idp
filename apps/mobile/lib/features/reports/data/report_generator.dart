/// Report Generator - مولد التقارير المحلي
/// Local PDF/Excel generation with Arabic support
library;

import 'dart:io';
import 'dart:convert';
import 'dart:math';
import 'package:path_provider/path_provider.dart';
import 'package:intl/intl.dart';
import '../domain/models/report_template.dart';
import '../domain/models/report_data.dart';
import '../domain/models/report_filter.dart';
import '../domain/models/chart_config.dart';

/// Report generator for offline report generation
/// مولد التقارير للعمل بدون اتصال
class ReportGenerator {
  final Random _random = Random();

  // ═══════════════════════════════════════════════════════════════════════════
  // Section Generation
  // توليد الأقسام
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate report sections based on template
  /// توليد أقسام التقرير بناءً على القالب
  Future<List<ReportSection>> generateSections({
    required ReportTemplate template,
    required ReportFilter filter,
  }) async {
    switch (template.type) {
      case ReportType.fieldPerformance:
        return _generateFieldPerformanceSections(filter);
      case ReportType.ndviTrend:
        return _generateNdviTrendSections(filter);
      case ReportType.irrigationSummary:
        return _generateIrrigationSummarySections(filter);
      case ReportType.taskCompletion:
        return _generateTaskCompletionSections(filter);
      case ReportType.weatherAnalysis:
        return _generateWeatherAnalysisSections(filter);
      case ReportType.costProfit:
        return _generateCostProfitSections(filter);
      case ReportType.yieldPrediction:
        return _generateYieldPredictionSections(filter);
    }
  }

  /// Generate summary statistics based on template
  /// توليد الإحصائيات الملخصة
  Future<List<SummaryStat>> generateSummaryStats({
    required ReportTemplate template,
    required ReportFilter filter,
  }) async {
    switch (template.type) {
      case ReportType.fieldPerformance:
        return _generateFieldPerformanceStats();
      case ReportType.ndviTrend:
        return _generateNdviTrendStats();
      case ReportType.irrigationSummary:
        return _generateIrrigationStats();
      case ReportType.taskCompletion:
        return _generateTaskCompletionStats();
      case ReportType.weatherAnalysis:
        return _generateWeatherStats();
      case ReportType.costProfit:
        return _generateCostProfitStats();
      case ReportType.yieldPrediction:
        return _generateYieldPredictionStats();
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Field Performance Report
  // تقرير أداء الحقل
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateFieldPerformanceSections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'performance_chart',
        title: 'Performance Overview',
        titleAr: 'نظرة عامة على الأداء',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.line,
          title: 'Field Health Trend',
          titleAr: 'اتجاه صحة الحقل',
          series: [
            ChartDataSeries(
              id: 'ndvi',
              name: 'NDVI',
              nameAr: 'مؤشر NDVI',
              colorHex: '#1B5E20',
              fillArea: true,
              dataPoints: _generateTimeSeriesData(filter.dateRange, 0.5, 0.9),
            ),
          ],
          xAxis: AxisConfig(title: 'Date', titleAr: 'التاريخ'),
          yAxis: AxisConfig(title: 'NDVI', titleAr: 'NDVI', min: 0, max: 1),
        ),
      ),
      ReportSection(
        id: 'health_distribution',
        title: 'Health Distribution',
        titleAr: 'توزيع الصحة',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.pie,
          title: 'Crop Health Status',
          titleAr: 'حالة صحة المحصول',
          series: [
            ChartDataSeries(
              id: 'health_dist',
              name: 'Health',
              nameAr: 'الصحة',
              colorHex: '#4CAF50',
              dataPoints: [
                ChartDataPoint(x: 'Excellent', y: 35, label: 'Excellent', labelAr: 'ممتاز', colorHex: '#2E7D32'),
                ChartDataPoint(x: 'Good', y: 40, label: 'Good', labelAr: 'جيد', colorHex: '#4CAF50'),
                ChartDataPoint(x: 'Moderate', y: 18, label: 'Moderate', labelAr: 'متوسط', colorHex: '#FF9800'),
                ChartDataPoint(x: 'Poor', y: 7, label: 'Poor', labelAr: 'ضعيف', colorHex: '#F44336'),
              ],
            ),
          ],
        ),
      ),
      ReportSection(
        id: 'performance_table',
        title: 'Detailed Performance',
        titleAr: 'الأداء التفصيلي',
        type: 'table',
        order: 3,
        data: {
          'table': ReportTableData(
            headers: ['Metric', 'Current', 'Previous', 'Change'],
            headersAr: ['المقياس', 'الحالي', 'السابق', 'التغيير'],
            rows: [
              ['NDVI Average', '0.72', '0.68', '+5.9%'],
              ['Stressed Areas', '12%', '18%', '-6%'],
              ['Water Usage', '2,450 m\u00B3', '2,680 m\u00B3', '-8.6%'],
              ['Tasks Completed', '45', '38', '+18.4%'],
            ],
          ).toJson(),
        },
      ),
    ];
  }

  List<SummaryStat> _generateFieldPerformanceStats() {
    return [
      SummaryStat(
        label: 'Average NDVI',
        labelAr: 'متوسط NDVI',
        value: '0.72',
        changePercent: 5.9,
        isPositiveChange: true,
        iconName: 'eco',
        colorHex: '#4CAF50',
      ),
      SummaryStat(
        label: 'Field Health',
        labelAr: 'صحة الحقل',
        value: '85%',
        changePercent: 3.2,
        isPositiveChange: true,
        iconName: 'favorite',
        colorHex: '#2E7D32',
      ),
      SummaryStat(
        label: 'Water Efficiency',
        labelAr: 'كفاءة المياه',
        value: '92%',
        changePercent: 8.6,
        isPositiveChange: true,
        iconName: 'water_drop',
        colorHex: '#1976D2',
      ),
      SummaryStat(
        label: 'Tasks Done',
        labelAr: 'المهام المنجزة',
        value: '45',
        changePercent: 18.4,
        isPositiveChange: true,
        iconName: 'task_alt',
        colorHex: '#FF8F00',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // NDVI Trend Report
  // تقرير اتجاه NDVI
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateNdviTrendSections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'ndvi_trend_chart',
        title: 'NDVI Trend Over Time',
        titleAr: 'اتجاه NDVI عبر الزمن',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.area,
          title: 'Vegetation Index Trend',
          titleAr: 'اتجاه مؤشر الغطاء النباتي',
          series: [
            ChartDataSeries(
              id: 'ndvi_main',
              name: 'NDVI',
              nameAr: 'NDVI',
              colorHex: '#1B5E20',
              fillArea: true,
              dataPoints: _generateTimeSeriesData(filter.dateRange, 0.4, 0.9),
            ),
            ChartDataSeries(
              id: 'ndvi_avg',
              name: 'Average',
              nameAr: 'المتوسط',
              colorHex: '#FF8F00',
              isDashed: true,
              dataPoints: _generateConstantLine(filter.dateRange, 0.65),
            ),
          ],
          xAxis: AxisConfig(title: 'Date', titleAr: 'التاريخ'),
          yAxis: AxisConfig(title: 'NDVI Value', titleAr: 'قيمة NDVI', min: 0, max: 1),
        ),
      ),
      ReportSection(
        id: 'ndvi_zone_comparison',
        title: 'Zone Comparison',
        titleAr: 'مقارنة المناطق',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.bar,
          title: 'NDVI by Zone',
          titleAr: 'NDVI حسب المنطقة',
          series: [
            ChartDataSeries(
              id: 'zones',
              name: 'Zones',
              nameAr: 'المناطق',
              colorHex: '#367C2B',
              dataPoints: [
                ChartDataPoint(x: 'Zone 1', y: 0.78, labelAr: 'المنطقة 1'),
                ChartDataPoint(x: 'Zone 2', y: 0.72, labelAr: 'المنطقة 2'),
                ChartDataPoint(x: 'Zone 3', y: 0.65, labelAr: 'المنطقة 3'),
                ChartDataPoint(x: 'Zone 4', y: 0.58, labelAr: 'المنطقة 4'),
              ],
            ),
          ],
        ),
      ),
    ];
  }

  List<SummaryStat> _generateNdviTrendStats() {
    return [
      SummaryStat(
        label: 'Current NDVI',
        labelAr: 'NDVI الحالي',
        value: '0.74',
        changePercent: 8.2,
        isPositiveChange: true,
        iconName: 'show_chart',
        colorHex: '#4CAF50',
      ),
      SummaryStat(
        label: 'Period Average',
        labelAr: 'متوسط الفترة',
        value: '0.68',
        iconName: 'analytics',
        colorHex: '#1976D2',
      ),
      SummaryStat(
        label: 'Peak Value',
        labelAr: 'القيمة القصوى',
        value: '0.82',
        iconName: 'trending_up',
        colorHex: '#2E7D32',
      ),
      SummaryStat(
        label: 'Variability',
        labelAr: 'التباين',
        value: '12%',
        iconName: 'swap_vert',
        colorHex: '#FF8F00',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Irrigation Summary Report
  // ملخص الري
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateIrrigationSummarySections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'water_usage_chart',
        title: 'Water Usage Trend',
        titleAr: 'اتجاه استهلاك المياه',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.bar,
          title: 'Daily Water Consumption',
          titleAr: 'الاستهلاك اليومي للمياه',
          series: [
            ChartDataSeries(
              id: 'water',
              name: 'Water (m\u00B3)',
              nameAr: 'المياه (م\u00B3)',
              colorHex: '#1976D2',
              dataPoints: _generateDailyData(filter.dateRange, 50, 150),
            ),
          ],
          yAxis: AxisConfig(title: 'Volume (m\u00B3)', titleAr: 'الحجم (م\u00B3)'),
        ),
      ),
      ReportSection(
        id: 'irrigation_efficiency',
        title: 'Irrigation Efficiency',
        titleAr: 'كفاءة الري',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.doughnut,
          title: 'Efficiency Breakdown',
          titleAr: 'تفصيل الكفاءة',
          series: [
            ChartDataSeries(
              id: 'efficiency',
              name: 'Efficiency',
              nameAr: 'الكفاءة',
              colorHex: '#4CAF50',
              dataPoints: [
                ChartDataPoint(x: 'Effective', y: 82, labelAr: 'فعال', colorHex: '#4CAF50'),
                ChartDataPoint(x: 'Evaporation', y: 10, labelAr: 'تبخر', colorHex: '#FF9800'),
                ChartDataPoint(x: 'Runoff', y: 5, labelAr: 'جريان', colorHex: '#F44336'),
                ChartDataPoint(x: 'Deep Percolation', y: 3, labelAr: 'تسرب عميق', colorHex: '#9E9E9E'),
              ],
            ),
          ],
        ),
      ),
      ReportSection(
        id: 'irrigation_schedule',
        title: 'Irrigation Schedule',
        titleAr: 'جدول الري',
        type: 'table',
        order: 3,
        data: {
          'table': ReportTableData(
            headers: ['Field', 'Method', 'Volume', 'Duration', 'Status'],
            headersAr: ['الحقل', 'الطريقة', 'الحجم', 'المدة', 'الحالة'],
            rows: [
              ['Field 1', 'Drip', '120 m\u00B3', '4h', 'Completed'],
              ['Field 2', 'Sprinkler', '200 m\u00B3', '3h', 'In Progress'],
              ['Field 3', 'Drip', '85 m\u00B3', '2.5h', 'Scheduled'],
            ],
          ).toJson(),
        },
      ),
    ];
  }

  List<SummaryStat> _generateIrrigationStats() {
    return [
      SummaryStat(
        label: 'Total Water Used',
        labelAr: 'إجمالي المياه',
        value: '2,450',
        unit: 'm\u00B3',
        changePercent: -8.6,
        isPositiveChange: true,
        iconName: 'water_drop',
        colorHex: '#1976D2',
      ),
      SummaryStat(
        label: 'Efficiency',
        labelAr: 'الكفاءة',
        value: '82%',
        changePercent: 5.3,
        isPositiveChange: true,
        iconName: 'speed',
        colorHex: '#4CAF50',
      ),
      SummaryStat(
        label: 'Cost Savings',
        labelAr: 'التوفير',
        value: '1,200',
        unit: 'SAR',
        iconName: 'savings',
        colorHex: '#2E7D32',
      ),
      SummaryStat(
        label: 'Events',
        labelAr: 'عمليات الري',
        value: '28',
        iconName: 'event',
        colorHex: '#FF8F00',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Task Completion Report
  // تقرير إنجاز المهام
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateTaskCompletionSections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'task_completion_chart',
        title: 'Task Completion Rate',
        titleAr: 'معدل إنجاز المهام',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.line,
          title: 'Daily Task Completion',
          titleAr: 'إنجاز المهام اليومي',
          series: [
            ChartDataSeries(
              id: 'completed',
              name: 'Completed',
              nameAr: 'مكتمل',
              colorHex: '#4CAF50',
              dataPoints: _generateDailyData(filter.dateRange, 3, 12),
            ),
            ChartDataSeries(
              id: 'created',
              name: 'Created',
              nameAr: 'منشأ',
              colorHex: '#1976D2',
              isDashed: true,
              dataPoints: _generateDailyData(filter.dateRange, 2, 10),
            ),
          ],
        ),
      ),
      ReportSection(
        id: 'task_distribution',
        title: 'Task Distribution by Type',
        titleAr: 'توزيع المهام حسب النوع',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.pie,
          title: 'Tasks by Category',
          titleAr: 'المهام حسب الفئة',
          series: [
            ChartDataSeries(
              id: 'task_types',
              name: 'Task Types',
              nameAr: 'أنواع المهام',
              colorHex: '#367C2B',
              dataPoints: [
                ChartDataPoint(x: 'Irrigation', y: 35, labelAr: 'الري', colorHex: '#1976D2'),
                ChartDataPoint(x: 'Fertilization', y: 25, labelAr: 'التسميد', colorHex: '#4CAF50'),
                ChartDataPoint(x: 'Spraying', y: 20, labelAr: 'الرش', colorHex: '#FF9800'),
                ChartDataPoint(x: 'Inspection', y: 20, labelAr: 'التفقد', colorHex: '#9C27B0'),
              ],
            ),
          ],
        ),
      ),
    ];
  }

  List<SummaryStat> _generateTaskCompletionStats() {
    return [
      SummaryStat(
        label: 'Completed',
        labelAr: 'مكتمل',
        value: '45',
        changePercent: 18.4,
        isPositiveChange: true,
        iconName: 'check_circle',
        colorHex: '#4CAF50',
      ),
      SummaryStat(
        label: 'Completion Rate',
        labelAr: 'نسبة الإنجاز',
        value: '89%',
        changePercent: 5.2,
        isPositiveChange: true,
        iconName: 'trending_up',
        colorHex: '#2E7D32',
      ),
      SummaryStat(
        label: 'Pending',
        labelAr: 'معلق',
        value: '8',
        changePercent: -12.5,
        isPositiveChange: true,
        iconName: 'pending',
        colorHex: '#FF8F00',
      ),
      SummaryStat(
        label: 'Overdue',
        labelAr: 'متأخر',
        value: '2',
        changePercent: -50,
        isPositiveChange: true,
        iconName: 'warning',
        colorHex: '#F44336',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Weather Analysis Report
  // تحليل الطقس
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateWeatherAnalysisSections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'temperature_chart',
        title: 'Temperature Trend',
        titleAr: 'اتجاه درجة الحرارة',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.area,
          title: 'Daily Temperature Range',
          titleAr: 'نطاق درجة الحرارة اليومي',
          series: [
            ChartDataSeries(
              id: 'temp_max',
              name: 'Max Temp',
              nameAr: 'الحرارة القصوى',
              colorHex: '#F44336',
              fillArea: true,
              dataPoints: _generateTimeSeriesData(filter.dateRange, 28, 38),
            ),
            ChartDataSeries(
              id: 'temp_min',
              name: 'Min Temp',
              nameAr: 'الحرارة الدنيا',
              colorHex: '#1976D2',
              fillArea: true,
              dataPoints: _generateTimeSeriesData(filter.dateRange, 15, 22),
            ),
          ],
          yAxis: AxisConfig(title: 'Temperature (\u00B0C)', titleAr: 'الحرارة (\u00B0م)'),
        ),
      ),
      ReportSection(
        id: 'rainfall_chart',
        title: 'Rainfall',
        titleAr: 'هطول الأمطار',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.bar,
          title: 'Daily Precipitation',
          titleAr: 'الهطول اليومي',
          series: [
            ChartDataSeries(
              id: 'rainfall',
              name: 'Rainfall (mm)',
              nameAr: 'الأمطار (مم)',
              colorHex: '#1976D2',
              dataPoints: _generateRainfallData(filter.dateRange),
            ),
          ],
        ),
      ),
    ];
  }

  List<SummaryStat> _generateWeatherStats() {
    return [
      SummaryStat(
        label: 'Avg Temperature',
        labelAr: 'متوسط الحرارة',
        value: '28',
        unit: '\u00B0C',
        iconName: 'thermostat',
        colorHex: '#FF8F00',
      ),
      SummaryStat(
        label: 'Total Rainfall',
        labelAr: 'إجمالي الأمطار',
        value: '45',
        unit: 'mm',
        iconName: 'water_drop',
        colorHex: '#1976D2',
      ),
      SummaryStat(
        label: 'Avg Humidity',
        labelAr: 'متوسط الرطوبة',
        value: '65%',
        iconName: 'opacity',
        colorHex: '#00BCD4',
      ),
      SummaryStat(
        label: 'Wind Speed',
        labelAr: 'سرعة الرياح',
        value: '12',
        unit: 'km/h',
        iconName: 'air',
        colorHex: '#9E9E9E',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cost/Profit Analysis Report
  // تحليل التكاليف والأرباح
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateCostProfitSections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'revenue_cost_chart',
        title: 'Revenue vs Cost',
        titleAr: 'الإيرادات مقابل التكاليف',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.bar,
          title: 'Monthly Financial Overview',
          titleAr: 'النظرة المالية الشهرية',
          series: [
            ChartDataSeries(
              id: 'revenue',
              name: 'Revenue',
              nameAr: 'الإيرادات',
              colorHex: '#4CAF50',
              stackGroup: 'financial',
              dataPoints: _generateMonthlyData(45000, 85000),
            ),
            ChartDataSeries(
              id: 'cost',
              name: 'Cost',
              nameAr: 'التكاليف',
              colorHex: '#F44336',
              stackGroup: 'financial',
              dataPoints: _generateMonthlyData(25000, 45000),
            ),
          ],
          yAxis: AxisConfig(title: 'Amount (SAR)', titleAr: 'المبلغ (ريال)'),
        ),
      ),
      ReportSection(
        id: 'cost_breakdown',
        title: 'Cost Breakdown',
        titleAr: 'تفصيل التكاليف',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.pie,
          title: 'Expense Categories',
          titleAr: 'فئات المصروفات',
          series: [
            ChartDataSeries(
              id: 'expenses',
              name: 'Expenses',
              nameAr: 'المصروفات',
              colorHex: '#367C2B',
              dataPoints: [
                ChartDataPoint(x: 'Labor', y: 35, labelAr: 'العمالة', colorHex: '#1976D2'),
                ChartDataPoint(x: 'Water', y: 20, labelAr: 'المياه', colorHex: '#00BCD4'),
                ChartDataPoint(x: 'Fertilizer', y: 18, labelAr: 'الأسمدة', colorHex: '#4CAF50'),
                ChartDataPoint(x: 'Equipment', y: 15, labelAr: 'المعدات', colorHex: '#FF9800'),
                ChartDataPoint(x: 'Other', y: 12, labelAr: 'أخرى', colorHex: '#9E9E9E'),
              ],
            ),
          ],
        ),
      ),
    ];
  }

  List<SummaryStat> _generateCostProfitStats() {
    return [
      SummaryStat(
        label: 'Total Revenue',
        labelAr: 'إجمالي الإيرادات',
        value: '185,000',
        unit: 'SAR',
        changePercent: 12.5,
        isPositiveChange: true,
        iconName: 'trending_up',
        colorHex: '#4CAF50',
      ),
      SummaryStat(
        label: 'Total Cost',
        labelAr: 'إجمالي التكاليف',
        value: '95,000',
        unit: 'SAR',
        changePercent: 5.2,
        isPositiveChange: false,
        iconName: 'trending_down',
        colorHex: '#F44336',
      ),
      SummaryStat(
        label: 'Net Profit',
        labelAr: 'صافي الربح',
        value: '90,000',
        unit: 'SAR',
        changePercent: 18.3,
        isPositiveChange: true,
        iconName: 'account_balance',
        colorHex: '#2E7D32',
      ),
      SummaryStat(
        label: 'Profit Margin',
        labelAr: 'هامش الربح',
        value: '48.6%',
        changePercent: 3.8,
        isPositiveChange: true,
        iconName: 'percent',
        colorHex: '#FF8F00',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Yield Prediction Report
  // تقرير توقع الإنتاج
  // ═══════════════════════════════════════════════════════════════════════════

  List<ReportSection> _generateYieldPredictionSections(ReportFilter filter) {
    return [
      ReportSection(
        id: 'yield_forecast_chart',
        title: 'Yield Forecast',
        titleAr: 'توقعات الإنتاج',
        type: 'chart',
        order: 1,
        chartConfig: ChartConfig(
          type: ChartType.combined,
          title: 'Predicted vs Historical Yield',
          titleAr: 'الإنتاج المتوقع مقابل التاريخي',
          series: [
            ChartDataSeries(
              id: 'historical',
              name: 'Historical',
              nameAr: 'تاريخي',
              colorHex: '#1976D2',
              dataPoints: [
                ChartDataPoint(x: '2021', y: 4.2),
                ChartDataPoint(x: '2022', y: 4.5),
                ChartDataPoint(x: '2023', y: 4.8),
                ChartDataPoint(x: '2024', y: 5.1),
              ],
            ),
            ChartDataSeries(
              id: 'predicted',
              name: 'Predicted',
              nameAr: 'متوقع',
              colorHex: '#4CAF50',
              isDashed: true,
              dataPoints: [
                ChartDataPoint(x: '2024', y: 5.1),
                ChartDataPoint(x: '2025', y: 5.4),
                ChartDataPoint(x: '2026', y: 5.7),
              ],
            ),
          ],
          yAxis: AxisConfig(title: 'Yield (ton/ha)', titleAr: 'الإنتاج (طن/هـ)'),
        ),
      ),
      ReportSection(
        id: 'yield_factors',
        title: 'Yield Influencing Factors',
        titleAr: 'العوامل المؤثرة على الإنتاج',
        type: 'chart',
        order: 2,
        chartConfig: ChartConfig(
          type: ChartType.bar,
          title: 'Factor Contribution',
          titleAr: 'مساهمة العوامل',
          series: [
            ChartDataSeries(
              id: 'factors',
              name: 'Impact',
              nameAr: 'التأثير',
              colorHex: '#367C2B',
              dataPoints: [
                ChartDataPoint(x: 'Soil Health', y: 85, labelAr: 'صحة التربة', colorHex: '#8B7355'),
                ChartDataPoint(x: 'Water', y: 90, labelAr: 'المياه', colorHex: '#1976D2'),
                ChartDataPoint(x: 'Weather', y: 75, labelAr: 'الطقس', colorHex: '#FF9800'),
                ChartDataPoint(x: 'Nutrition', y: 88, labelAr: 'التغذية', colorHex: '#4CAF50'),
              ],
            ),
          ],
        ),
      ),
    ];
  }

  List<SummaryStat> _generateYieldPredictionStats() {
    return [
      SummaryStat(
        label: 'Predicted Yield',
        labelAr: 'الإنتاج المتوقع',
        value: '5.4',
        unit: 'ton/ha',
        changePercent: 5.9,
        isPositiveChange: true,
        iconName: 'trending_up',
        colorHex: '#4CAF50',
      ),
      SummaryStat(
        label: 'Confidence',
        labelAr: 'الثقة',
        value: '87%',
        iconName: 'verified',
        colorHex: '#1976D2',
      ),
      SummaryStat(
        label: 'Est. Revenue',
        labelAr: 'الإيرادات المتوقعة',
        value: '185K',
        unit: 'SAR',
        iconName: 'payments',
        colorHex: '#2E7D32',
      ),
      SummaryStat(
        label: 'Harvest Date',
        labelAr: 'تاريخ الحصاد',
        value: 'May 15',
        iconName: 'event',
        colorHex: '#FF8F00',
      ),
    ];
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Data Generation Helpers
  // مساعدات توليد البيانات
  // ═══════════════════════════════════════════════════════════════════════════

  List<ChartDataPoint> _generateTimeSeriesData(DateRange range, double min, double max) {
    final points = <ChartDataPoint>[];
    var current = range.start;
    while (current.isBefore(range.end) || current.isAtSameMomentAs(range.end)) {
      final value = min + _random.nextDouble() * (max - min);
      points.add(ChartDataPoint(
        x: current.toIso8601String(),
        y: double.parse(value.toStringAsFixed(2)),
        label: DateFormat('MM/dd').format(current),
      ));
      current = current.add(const Duration(days: 1));
      if (points.length > 90) break; // Limit for performance
    }
    return points;
  }

  List<ChartDataPoint> _generateConstantLine(DateRange range, double value) {
    final points = <ChartDataPoint>[];
    var current = range.start;
    while (current.isBefore(range.end) || current.isAtSameMomentAs(range.end)) {
      points.add(ChartDataPoint(x: current.toIso8601String(), y: value));
      current = current.add(const Duration(days: 1));
      if (points.length > 90) break;
    }
    return points;
  }

  List<ChartDataPoint> _generateDailyData(DateRange range, double min, double max) {
    final points = <ChartDataPoint>[];
    var current = range.start;
    while (current.isBefore(range.end) || current.isAtSameMomentAs(range.end)) {
      final value = min + _random.nextDouble() * (max - min);
      points.add(ChartDataPoint(
        x: DateFormat('MM/dd').format(current),
        y: double.parse(value.toStringAsFixed(1)),
      ));
      current = current.add(const Duration(days: 1));
      if (points.length > 31) break;
    }
    return points;
  }

  List<ChartDataPoint> _generateRainfallData(DateRange range) {
    final points = <ChartDataPoint>[];
    var current = range.start;
    while (current.isBefore(range.end) || current.isAtSameMomentAs(range.end)) {
      // Most days have 0 rainfall
      final hasRain = _random.nextDouble() > 0.85;
      final value = hasRain ? _random.nextDouble() * 25 : 0;
      points.add(ChartDataPoint(
        x: DateFormat('MM/dd').format(current),
        y: double.parse(value.toStringAsFixed(1)),
      ));
      current = current.add(const Duration(days: 1));
      if (points.length > 31) break;
    }
    return points;
  }

  List<ChartDataPoint> _generateMonthlyData(double min, double max) {
    final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
    return months.map((month) {
      final value = min + _random.nextDouble() * (max - min);
      return ChartDataPoint(x: month, y: double.parse(value.toStringAsFixed(0)));
    }).toList();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Export Functions
  // دوال التصدير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate PDF report
  /// توليد تقرير PDF
  Future<String?> generatePdf(
    ReportData report, {
    bool includeArabic = true,
  }) async {
    // Note: PDF generation requires additional packages like pdf or printing
    // This is a placeholder implementation
    try {
      final directory = await getApplicationDocumentsDirectory();
      final fileName = '${report.title}_${_formatDateForFile(report.generatedAt)}.pdf';
      final filePath = '${directory.path}/reports/$fileName';

      // Create reports directory if needed
      final reportsDir = Directory('${directory.path}/reports');
      if (!await reportsDir.exists()) {
        await reportsDir.create(recursive: true);
      }

      // Create a simple text representation for now
      // In production, use a PDF library like 'pdf' package
      final content = _generateTextReport(report, includeArabic);
      final file = File(filePath.replaceAll('.pdf', '.txt'));
      await file.writeAsString(content);

      return file.path;
    } catch (e) {
      return null;
    }
  }

  /// Generate Excel report
  /// توليد تقرير Excel
  Future<String?> generateExcel(ReportData report) async {
    // Note: Excel generation requires additional packages like excel
    // This is a placeholder implementation
    try {
      final directory = await getApplicationDocumentsDirectory();
      final fileName = '${report.title}_${_formatDateForFile(report.generatedAt)}.csv';
      final filePath = '${directory.path}/reports/$fileName';

      // Create reports directory if needed
      final reportsDir = Directory('${directory.path}/reports');
      if (!await reportsDir.exists()) {
        await reportsDir.create(recursive: true);
      }

      final content = _generateCsvContent(report);
      final file = File(filePath);
      await file.writeAsString(content);

      return file.path;
    } catch (e) {
      return null;
    }
  }

  /// Generate CSV report
  /// توليد تقرير CSV
  Future<String?> generateCsv(ReportData report) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final fileName = '${report.title}_${_formatDateForFile(report.generatedAt)}.csv';
      final filePath = '${directory.path}/reports/$fileName';

      final reportsDir = Directory('${directory.path}/reports');
      if (!await reportsDir.exists()) {
        await reportsDir.create(recursive: true);
      }

      final content = _generateCsvContent(report);
      final file = File(filePath);
      await file.writeAsString(content);

      return file.path;
    } catch (e) {
      return null;
    }
  }

  /// Save exported file from server
  /// حفظ الملف المصدر من السيرفر
  Future<String?> saveExportedFile(List<int> bytes, String fileName) async {
    try {
      final directory = await getApplicationDocumentsDirectory();
      final filePath = '${directory.path}/reports/$fileName';

      final reportsDir = Directory('${directory.path}/reports');
      if (!await reportsDir.exists()) {
        await reportsDir.create(recursive: true);
      }

      final file = File(filePath);
      await file.writeAsBytes(bytes);

      return file.path;
    } catch (e) {
      return null;
    }
  }

  String _generateTextReport(ReportData report, bool includeArabic) {
    final buffer = StringBuffer();

    buffer.writeln('=' * 60);
    buffer.writeln(report.title);
    if (includeArabic) buffer.writeln(report.titleAr);
    buffer.writeln('=' * 60);
    buffer.writeln('Generated: ${DateFormat('yyyy-MM-dd HH:mm').format(report.generatedAt)}');
    buffer.writeln('Period: ${report.filter.dateRange.formatted}');
    buffer.writeln();

    // Summary stats
    buffer.writeln('SUMMARY');
    buffer.writeln('-' * 40);
    for (final stat in report.summaryStats) {
      buffer.writeln('${stat.label}: ${stat.value}${stat.unit ?? ''}');
      if (includeArabic) {
        buffer.writeln('  ${stat.labelAr}');
      }
    }
    buffer.writeln();

    // Sections
    for (final section in report.visibleSections) {
      buffer.writeln(section.title.toUpperCase());
      if (includeArabic) buffer.writeln(section.titleAr);
      buffer.writeln('-' * 40);

      if (section.type == 'table' && section.data['table'] != null) {
        final table = ReportTableData.fromJson(section.data['table'] as Map<String, dynamic>);
        buffer.writeln(table.headers.join('\t'));
        for (final row in table.rows) {
          buffer.writeln(row.join('\t'));
        }
      }
      buffer.writeln();
    }

    return buffer.toString();
  }

  String _generateCsvContent(ReportData report) {
    final buffer = StringBuffer();

    // Summary
    buffer.writeln('Summary Statistics');
    buffer.writeln('Metric,Value,Unit,Change');
    for (final stat in report.summaryStats) {
      buffer.writeln('${stat.label},${stat.value},${stat.unit ?? ''},${stat.changePercent ?? ''}');
    }
    buffer.writeln();

    // Table sections
    for (final section in report.tableSections) {
      if (section.data['table'] != null) {
        buffer.writeln(section.title);
        final table = ReportTableData.fromJson(section.data['table'] as Map<String, dynamic>);
        buffer.writeln(table.headers.join(','));
        for (final row in table.rows) {
          buffer.writeln(row.join(','));
        }
        buffer.writeln();
      }
    }

    return buffer.toString();
  }

  String _formatDateForFile(DateTime date) {
    return DateFormat('yyyyMMdd_HHmmss').format(date);
  }
}
