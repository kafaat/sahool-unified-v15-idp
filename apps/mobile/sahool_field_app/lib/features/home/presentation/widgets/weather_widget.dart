import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../weather/presentation/providers/weather_provider.dart';
import '../../../weather/domain/entities/weather_entities.dart';

/// ويدجت الطقس المصغر للصفحة الرئيسية
/// Weather widget for home page with offline caching support
class WeatherWidget extends ConsumerStatefulWidget {
  final String? location;
  final VoidCallback? onTap;

  const WeatherWidget({
    super.key,
    this.location,
    this.onTap,
  });

  @override
  ConsumerState<WeatherWidget> createState() => _WeatherWidgetState();
}

class _WeatherWidgetState extends ConsumerState<WeatherWidget> {
  @override
  void initState() {
    super.initState();
    // Set the location for home weather
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (widget.location != null) {
        ref.read(homeWeatherLocationProvider.notifier).state = widget.location;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final weatherAsync = ref.watch(homeWeatherProvider);
    final alertsCount = ref.watch(weatherAlertsCountProvider);

    return weatherAsync.when(
      loading: () => _buildLoadingWidget(),
      error: (_, __) => _buildErrorWidget(),
      data: (data) => data != null
          ? _buildWeatherCard(data, alertsCount.valueOrNull ?? 0)
          : _buildErrorWidget(),
    );
  }

  Widget _buildLoadingWidget() {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
          ),
        ),
        padding: const EdgeInsets.all(20),
        height: 160,
        child: const Center(
          child: CircularProgressIndicator(
            color: Colors.white,
            strokeWidth: 2,
          ),
        ),
      ),
    );
  }

  Widget _buildErrorWidget() {
    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(16),
          gradient: const LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
          ),
        ),
        padding: const EdgeInsets.all(20),
        height: 160,
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.cloud_off, color: Colors.white60, size: 32),
              const SizedBox(height: 8),
              const Text(
                'لا تتوفر بيانات الطقس',
                style: TextStyle(color: Colors.white70, fontSize: 14),
              ),
              const SizedBox(height: 8),
              TextButton(
                onPressed: () => ref.refresh(homeWeatherProvider),
                child: const Text(
                  'إعادة المحاولة',
                  style: TextStyle(color: Colors.white),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWeatherCard(WeatherData data, int alertsCount) {
    final current = data.current;
    final location = widget.location ?? 'الرياض';

    return GestureDetector(
      onTap: widget.onTap,
      child: Card(
        elevation: 3,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: const LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
            ),
          ),
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              // الطقس الحالي
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.location_on,
                            color: Colors.white70, size: 16),
                        const SizedBox(width: 4),
                        Text(
                          location,
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.8),
                            fontSize: 14,
                          ),
                        ),
                        if (alertsCount > 0) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 2),
                            decoration: BoxDecoration(
                              color: Colors.orange,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.warning_amber,
                                    color: Colors.white, size: 12),
                                const SizedBox(width: 2),
                                Text(
                                  '$alertsCount',
                                  style: const TextStyle(
                                      color: Colors.white, fontSize: 10),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          current.temperature.round().toString(),
                          style: const TextStyle(
                            fontSize: 48,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        const Text(
                          '°C',
                          style: TextStyle(
                            fontSize: 20,
                            color: Colors.white70,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          current.icon,
                          style: const TextStyle(fontSize: 48),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      current.conditionAr,
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 16,
                      ),
                    ),
                  ],
                ),
              ),

              // تفاصيل إضافية
              Container(
                height: 100,
                width: 1,
                color: Colors.white24,
              ),
              const SizedBox(width: 16),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildWeatherDetail(
                    icon: Icons.water_drop,
                    value: '${current.humidity}%',
                    label: 'رطوبة',
                  ),
                  const SizedBox(height: 12),
                  _buildWeatherDetail(
                    icon: Icons.air,
                    value: '${current.windSpeed.round()} km/h',
                    label: 'رياح',
                  ),
                  const SizedBox(height: 12),
                  if (current.uvIndex != null)
                    _buildWeatherDetail(
                      icon: Icons.wb_sunny,
                      value: current.uvIndex!.round().toString(),
                      label: 'UV',
                    )
                  else
                    _buildWeatherDetail(
                      icon: Icons.thermostat,
                      value: '${current.feelsLike.round()}°',
                      label: 'شعور',
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWeatherDetail({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Row(
      children: [
        Icon(icon, color: Colors.white60, size: 16),
        const SizedBox(width: 8),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
              style: const TextStyle(
                color: Colors.white60,
                fontSize: 10,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
