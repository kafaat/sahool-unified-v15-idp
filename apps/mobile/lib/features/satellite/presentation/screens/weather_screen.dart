/// Weather Screen - شاشة الطقس
/// 7-day weather forecast with charts and alerts
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:fl_chart/fl_chart.dart';
import '../providers/satellite_provider.dart';
import '../../widgets/weather_card.dart';

class WeatherScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String fieldName;

  const WeatherScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  ConsumerState<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends ConsumerState<WeatherScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(satelliteWeatherProvider.notifier).loadWeather(widget.fieldId);
    });
  }

  Future<void> _refreshWeather() async {
    await ref.read(satelliteWeatherProvider.notifier).refreshWeather(widget.fieldId);
  }

  @override
  Widget build(BuildContext context) {
    final weatherState = ref.watch(satelliteWeatherProvider);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text(
          isArabic ? 'توقعات الطقس' : 'Weather Forecast',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF367C2B),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: weatherState.when(
        data: (weather) => RefreshIndicator(
          onRefresh: _refreshWeather,
          color: const Color(0xFF367C2B),
          child: _buildWeatherContent(weather, isArabic),
        ),
        loading: () => const Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
          ),
        ),
        error: (error, stack) => _buildErrorState(error.toString(), isArabic),
      ),
    );
  }

  Widget _buildErrorState(String error, bool isArabic) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.cloud_off, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(error, textAlign: TextAlign.center),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshWeather,
              icon: const Icon(Icons.refresh),
              label: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherContent(dynamic weather, bool isArabic) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Current weather summary
        _buildCurrentWeather(weather, isArabic),
        const SizedBox(height: 16),

        // Temperature chart
        _buildTemperatureChart(weather.forecast, isArabic),
        const SizedBox(height: 16),

        // Precipitation chart
        _buildPrecipitationChart(weather.forecast, isArabic),
        const SizedBox(height: 16),

        // ET0 and irrigation need
        _buildIrrigationInfo(weather, isArabic),
        const SizedBox(height: 16),

        // 7-day forecast cards
        _buildForecastCards(weather.forecast, isArabic),
      ],
    );
  }

  Widget _buildCurrentWeather(dynamic weather, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF367C2B), Color(0xFF4CAF50)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        children: [
          Text(
            isArabic ? 'الطقس الحالي' : 'Current Weather',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '${weather.temperature.toStringAsFixed(1)}°C',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 48,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            isArabic ? weather.conditionAr : weather.condition,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 18,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildWeatherStat(
                Icons.thermostat,
                '${weather.minTemp.toStringAsFixed(0)}° / ${weather.maxTemp.toStringAsFixed(0)}°',
                isArabic ? 'الحد الأدنى / الأعلى' : 'Min / Max',
              ),
              _buildWeatherStat(
                Icons.water_drop,
                '${weather.humidity.toStringAsFixed(0)}%',
                isArabic ? 'الرطوبة' : 'Humidity',
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildWeatherStat(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white70,
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildTemperatureChart(List<dynamic> forecast, bool isArabic) {
    if (forecast.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'درجات الحرارة (7 أيام)' : 'Temperature (7 Days)',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 150,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(show: true),
                titlesData: FlTitlesData(show: false),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: forecast
                        .asMap()
                        .entries
                        .map((e) => FlSpot(
                              e.key.toDouble(),
                              e.value.tempMax.toDouble(),
                            ))
                        .toList(),
                    isCurved: true,
                    color: Colors.orange,
                    barWidth: 3,
                    dotData: FlDotData(show: true),
                  ),
                  LineChartBarData(
                    spots: forecast
                        .asMap()
                        .entries
                        .map((e) => FlSpot(
                              e.key.toDouble(),
                              e.value.tempMin.toDouble(),
                            ))
                        .toList(),
                    isCurved: true,
                    color: Colors.blue,
                    barWidth: 3,
                    dotData: FlDotData(show: true),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildLegend(Colors.orange, isArabic ? 'الحد الأعلى' : 'Max'),
              const SizedBox(width: 16),
              _buildLegend(Colors.blue, isArabic ? 'الحد الأدنى' : 'Min'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildPrecipitationChart(List<dynamic> forecast, bool isArabic) {
    if (forecast.isEmpty) return const SizedBox.shrink();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'الأمطار (ملم)' : 'Precipitation (mm)',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: 150,
            child: BarChart(
              BarChartData(
                gridData: FlGridData(show: true),
                titlesData: FlTitlesData(show: false),
                borderData: FlBorderData(show: false),
                barGroups: forecast
                    .asMap()
                    .entries
                    .map((e) => BarChartGroupData(
                          x: e.key,
                          barRods: [
                            BarChartRodData(
                              toY: e.value.precipitation.toDouble(),
                              color: const Color(0xFF2196F3),
                              width: 20,
                              borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                            ),
                          ],
                        ))
                    .toList(),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLegend(Color color, String label) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[700],
          ),
        ),
      ],
    );
  }

  Widget _buildIrrigationInfo(dynamic weather, bool isArabic) {
    final irrigationNeed = weather.getIrrigationNeed();

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Row(
        children: [
          Icon(Icons.water, size: 40, color: Colors.blue[700]),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isArabic ? 'احتياج الري' : 'Irrigation Need',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.blue[700],
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${irrigationNeed.toStringAsFixed(1)} ${isArabic ? 'ملم/يوم' : 'mm/day'}',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[900],
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '${isArabic ? 'التبخر' : 'ET0'}: ${weather.et0.toStringAsFixed(1)} mm/day',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.blue[700],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildForecastCards(List<dynamic> forecast, bool isArabic) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isArabic ? 'توقعات 7 أيام' : '7-Day Forecast',
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        ...forecast.map((day) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: _buildDayCard(day, isArabic),
            )),
      ],
    );
  }

  Widget _buildDayCard(dynamic day, bool isArabic) {
    final dayName = _getDayName(day.date, isArabic);

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Text(
              dayName,
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          Icon(_getWeatherIcon(day.condition), color: const Color(0xFF367C2B)),
          const SizedBox(width: 12),
          Text(
            '${day.tempMin.toStringAsFixed(0)}° / ${day.tempMax.toStringAsFixed(0)}°',
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
            ),
          ),
          if (day.precipitation > 0) ...[
            const SizedBox(width: 12),
            Icon(Icons.water_drop, size: 16, color: Colors.blue[700]),
            const SizedBox(width: 4),
            Text(
              '${day.precipitation.toStringAsFixed(0)}mm',
              style: TextStyle(
                fontSize: 12,
                color: Colors.blue[700],
              ),
            ),
          ],
        ],
      ),
    );
  }

  String _getDayName(DateTime date, bool isArabic) {
    final days = isArabic
        ? ['الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']
        : ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    return days[date.weekday % 7];
  }

  IconData _getWeatherIcon(String condition) {
    switch (condition.toLowerCase()) {
      case 'sunny':
      case 'clear':
        return Icons.wb_sunny;
      case 'cloudy':
        return Icons.cloud;
      case 'rainy':
      case 'rain':
        return Icons.water_drop;
      default:
        return Icons.wb_cloudy;
    }
  }
}
