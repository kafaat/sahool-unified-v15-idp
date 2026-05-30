/// Satellite Weather Tab - تبويب الطقس
library;

import 'dart:math' show Random;
import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteWeatherTab extends StatefulWidget {
  final String fieldId;

  const SatelliteWeatherTab({super.key, required this.fieldId});

  @override
  State<SatelliteWeatherTab> createState() => _SatelliteWeatherTabState();
}

class _SatelliteWeatherTabState extends State<SatelliteWeatherTab> {
  bool _loading = false;

  // Mock current conditions
  final double _temp = 28.0;
  final int _humidity = 55;
  final double _wind = 12.0;
  final double _precipitation = 0.0;

  // Mock 8-day forecast
  late final List<_DayForecast> _forecast;

  @override
  void initState() {
    super.initState();
    _forecast = _generateMockForecast();
  }

  List<_DayForecast> _generateMockForecast() {
    final rng = Random(99);
    final dayNames = ['اليوم', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت', 'الأحد', 'الاثنين'];
    final conditions = ['sunny', 'partly_cloudy', 'cloudy', 'sunny', 'partly_cloudy', 'rainy', 'sunny', 'sunny'];
    return List.generate(8, (i) {
      final high = 26 + rng.nextInt(8);
      final low = high - 8 - rng.nextInt(5);
      return _DayForecast(
        day: dayNames[i],
        condition: conditions[i],
        high: high,
        low: low,
        rainProbability: conditions[i] == 'rainy' ? 70 + rng.nextInt(25) : rng.nextInt(20),
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(SahoolColors.primary),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildCurrentConditions(),
          const SizedBox(height: 16),
          _buildForecastSection(),
        ],
      ),
    );
  }

  Widget _buildCurrentConditions() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [
            SahoolColors.primary,
            SahoolColors.sahoolGreen,
          ],
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'الأحوال الجوية الحالية',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 13,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                '${_temp.toStringAsFixed(0)}°',
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 56,
                  fontWeight: FontWeight.bold,
                  height: 1,
                ),
              ),
              const SizedBox(width: 8),
              const Padding(
                padding: EdgeInsets.only(bottom: 10),
                child: Text(
                  'مشمس جزئياً',
                  style: TextStyle(color: Colors.white70, fontSize: 16),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildCurrentStat(Icons.water_drop_outlined, '$_humidity%', 'الرطوبة'),
              _buildCurrentStat(Icons.air, '${_wind.toStringAsFixed(0)} كم/س', 'الرياح'),
              _buildCurrentStat(Icons.umbrella, '${_precipitation.toStringAsFixed(0)} مم', 'الأمطار'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildCurrentStat(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 14,
          ),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white60, fontSize: 11),
        ),
      ],
    );
  }

  Widget _buildForecastSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'توقعات 8 أيام',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
        ),
        const SizedBox(height: 10),
        SizedBox(
          height: 140,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: _forecast.length,
            itemBuilder: (_, i) => _buildForecastCard(_forecast[i]),
          ),
        ),
      ],
    );
  }

  Widget _buildForecastCard(_DayForecast day) {
    return Container(
      width: 90,
      margin: const EdgeInsets.only(left: 8),
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 6,
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            day.day,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
            textAlign: TextAlign.center,
          ),
          Icon(
            _conditionIcon(day.condition),
            color: _conditionColor(day.condition),
            size: 28,
          ),
          Column(
            children: [
              Text(
                '${day.high}° / ${day.low}°',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 2),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.water_drop, size: 10, color: Colors.blue[400]),
                  const SizedBox(width: 2),
                  Text(
                    '${day.rainProbability}%',
                    style: TextStyle(fontSize: 10, color: Colors.blue[600]),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  IconData _conditionIcon(String condition) {
    switch (condition) {
      case 'sunny':
        return Icons.wb_sunny;
      case 'partly_cloudy':
        return Icons.wb_cloudy;
      case 'cloudy':
        return Icons.cloud;
      case 'rainy':
        return Icons.umbrella;
      default:
        return Icons.wb_sunny;
    }
  }

  Color _conditionColor(String condition) {
    switch (condition) {
      case 'sunny':
        return Colors.amber;
      case 'partly_cloudy':
        return Colors.blueGrey;
      case 'cloudy':
        return Colors.grey;
      case 'rainy':
        return Colors.blue;
      default:
        return Colors.amber;
    }
  }
}

class _DayForecast {
  final String day;
  final String condition;
  final int high;
  final int low;
  final int rainProbability;

  const _DayForecast({
    required this.day,
    required this.condition,
    required this.high,
    required this.low,
    required this.rainProbability,
  });
}
