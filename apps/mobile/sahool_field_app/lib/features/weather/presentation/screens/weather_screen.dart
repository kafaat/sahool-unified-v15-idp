import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/weather_entities.dart';
import '../providers/weather_provider.dart';
import '../widgets/current_weather_card.dart';
import '../widgets/hourly_forecast_list.dart';
import '../widgets/daily_forecast_list.dart';
import '../widgets/weather_alert_card.dart';
import '../widgets/agricultural_impact_card.dart';

/// شاشة الطقس
/// Weather Dashboard Screen
class WeatherScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String? fieldName;

  const WeatherScreen({
    super.key,
    required this.fieldId,
    this.fieldName,
  });

  @override
  ConsumerState<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends ConsumerState<WeatherScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);

    // تحميل البيانات
    Future.microtask(() {
      ref.read(weatherProvider.notifier).loadWeather(widget.fieldId);
      ref.read(alertsProvider.notifier).loadAlerts(widget.fieldId);
      ref.read(impactsProvider.notifier).loadImpacts(widget.fieldId);
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final weatherState = ref.watch(weatherProvider);
    final alertsState = ref.watch(alertsProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.fieldName ?? 'الطقس'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // شارة التنبيهات
            if (alertsState.activeAlerts > 0)
              Stack(
                children: [
                  IconButton(
                    icon: const Icon(Icons.notifications),
                    onPressed: () => _tabController.animateTo(2),
                  ),
                  Positioned(
                    right: 8,
                    top: 8,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Text(
                        '${alertsState.activeAlerts}',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ],
              ),
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _refreshData,
            ),
          ],
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: const [
              Tab(text: 'الطقس', icon: Icon(Icons.wb_sunny)),
              Tab(text: 'التوصيات', icon: Icon(Icons.agriculture)),
              Tab(text: 'التنبيهات', icon: Icon(Icons.warning)),
            ],
          ),
        ),
        body: weatherState.isLoading
            ? const Center(child: CircularProgressIndicator())
            : weatherState.error != null
                ? _buildErrorView(weatherState.error!)
                : TabBarView(
                    controller: _tabController,
                    children: [
                      _buildWeatherTab(weatherState.data!),
                      _buildRecommendationsTab(),
                      _buildAlertsTab(),
                    ],
                  ),
      ),
    );
  }

  Widget _buildWeatherTab(WeatherData data) {
    return RefreshIndicator(
      onRefresh: _refreshData,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // الطقس الحالي
            CurrentWeatherCard(weather: data.current),

            const SizedBox(height: 24),

            // التوقعات الساعية
            Text(
              'التوقعات الساعية',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            HourlyForecastList(forecasts: data.hourly),

            const SizedBox(height: 24),

            // التوقعات اليومية
            Text(
              'التوقعات الأسبوعية',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            DailyForecastList(forecasts: data.daily),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationsTab() {
    final impactsState = ref.watch(impactsProvider);
    final filteredImpacts = ref.watch(filteredImpactsProvider);

    if (impactsState.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (impactsState.error != null) {
      return _buildErrorView(impactsState.error!);
    }

    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          // فلتر الحالة
          _buildStatusFilter(),

          const SizedBox(height: 16),

          // قائمة التأثيرات
          if (filteredImpacts.isEmpty)
            const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: Column(
                  children: [
                    Icon(Icons.check_circle, size: 64, color: Colors.green),
                    SizedBox(height: 16),
                    Text('لا توجد توصيات حالياً'),
                  ],
                ),
              ),
            )
          else
            ...filteredImpacts.map(
              (impact) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: AgriculturalImpactCard(impact: impact),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildStatusFilter() {
    final currentFilter = ref.watch(impactFilterProvider);

    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildFilterChip('الكل', null, currentFilter),
          const SizedBox(width: 8),
          _buildFilterChip('مناسب', 'favorable', currentFilter, Colors.green),
          const SizedBox(width: 8),
          _buildFilterChip('حذر', 'caution', currentFilter, Colors.orange),
          const SizedBox(width: 8),
          _buildFilterChip('غير مناسب', 'unfavorable', currentFilter, Colors.red),
        ],
      ),
    );
  }

  Widget _buildFilterChip(
    String label,
    String? value,
    String? current, [
    Color? color,
  ]) {
    final isSelected = current == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        ref.read(impactFilterProvider.notifier).state = value;
      },
      selectedColor: (color ?? const Color(0xFF367C2B)).withOpacity(0.2),
      checkmarkColor: color ?? const Color(0xFF367C2B),
    );
  }

  Widget _buildAlertsTab() {
    final alertsState = ref.watch(alertsProvider);

    if (alertsState.isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (alertsState.error != null) {
      return _buildErrorView(alertsState.error!);
    }

    final activeAlerts = alertsState.alerts
        .where((a) => a.endTime.isAfter(DateTime.now()))
        .toList();

    if (activeAlerts.isEmpty) {
      return const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.check_circle, size: 64, color: Colors.green),
              SizedBox(height: 16),
              Text(
                'لا توجد تنبيهات حالياً',
                style: TextStyle(fontSize: 18),
              ),
              SizedBox(height: 8),
              Text(
                'الطقس مستقر',
                style: TextStyle(color: Colors.grey),
              ),
            ],
          ),
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: _refreshData,
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: activeAlerts.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: WeatherAlertCard(alert: activeAlerts[index]),
          );
        },
      ),
    );
  }

  Widget _buildErrorView(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.red),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshData,
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _refreshData() async {
    await Future.wait([
      ref.read(weatherProvider.notifier).loadWeather(widget.fieldId),
      ref.read(alertsProvider.notifier).loadAlerts(widget.fieldId),
      ref.read(impactsProvider.notifier).loadImpacts(widget.fieldId),
    ]);
  }
}
