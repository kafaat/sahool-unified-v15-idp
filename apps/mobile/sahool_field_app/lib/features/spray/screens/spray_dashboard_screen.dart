/// Spray Dashboard Screen - شاشة لوحة مستشار الرش
/// لوحة معلومات الرش الرئيسية
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../models/spray_models.dart';
import '../providers/spray_provider.dart';
import '../widgets/weather_card_widget.dart';
import '../widgets/spray_window_card.dart';

class SprayDashboardScreen extends ConsumerStatefulWidget {
  final String fieldId;

  const SprayDashboardScreen({
    Key? key,
    required this.fieldId,
  }) : super(key: key);

  @override
  ConsumerState<SprayDashboardScreen> createState() => _SprayDashboardScreenState();
}

class _SprayDashboardScreenState extends ConsumerState<SprayDashboardScreen> {
  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final locale = Localizations.localeOf(context).languageCode;
    final isArabic = locale == 'ar';

    return Scaffold(
      appBar: AppBar(
        title: Text(isArabic ? 'مستشار الرش' : 'Spray Advisor'),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_today),
            onPressed: () {
              // Navigate to calendar view
              // Navigator.push(context, MaterialPageRoute(
              //   builder: (_) => SprayCalendarScreen(fieldId: widget.fieldId),
              // ));
            },
          ),
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              // Navigate to logs
              // Navigator.push(context, MaterialPageRoute(
              //   builder: (_) => SprayLogScreen(fieldId: widget.fieldId),
              // ));
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(currentWeatherProvider);
          ref.invalidate(sprayWindowsProvider);
          ref.invalidate(sprayRecommendationsProvider);
        },
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Current Weather Conditions
              _buildCurrentWeatherSection(theme, isArabic),
              const SizedBox(height: 16),
              // Spray Windows Timeline (Next 7 Days)
              _buildSprayWindowsSection(theme, isArabic),
              const SizedBox(height: 16),
              // Active Recommendations
              _buildRecommendationsSection(theme, isArabic),
              const SizedBox(height: 16),
              // Quick Actions
              _buildQuickActionsSection(theme, isArabic),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          // Navigate to spray log form
          // Navigator.push(context, MaterialPageRoute(
          //   builder: (_) => SprayLogFormScreen(fieldId: widget.fieldId),
          // ));
        },
        icon: const Icon(Icons.add),
        label: Text(isArabic ? 'تسجيل رش' : 'Log Spray'),
      ),
    );
  }

  Widget _buildCurrentWeatherSection(ThemeData theme, bool isArabic) {
    final weatherAsync = ref.watch(currentWeatherProvider(widget.fieldId));

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'الطقس الحالي' : 'Current Weather',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          weatherAsync.when(
            data: (weather) => WeatherCardWidget(
              weather: weather,
              locale: _locale,
              onTap: () {
                // Show weather details
                _showWeatherDetailsDialog(weather);
              },
            ),
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(32.0),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, stack) => Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 48,
                      color: theme.colorScheme.error,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      isArabic ? 'فشل في جلب بيانات الطقس' : 'Failed to load weather data',
                      style: theme.textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () => ref.invalidate(currentWeatherProvider),
                      child: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSprayWindowsSection(ThemeData theme, bool isArabic) {
    final windowsAsync = ref.watch(sprayWindowsProvider(
      SprayWindowParams(fieldId: widget.fieldId, days: 7),
    ));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isArabic ? 'نوافذ الرش (7 أيام)' : 'Spray Windows (7 Days)',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              TextButton.icon(
                onPressed: () {
                  // Navigate to calendar view
                },
                icon: const Icon(Icons.calendar_month, size: 18),
                label: Text(isArabic ? 'عرض الكل' : 'View All'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        windowsAsync.when(
          data: (windows) {
            if (windows.isEmpty) {
              return Padding(
                padding: const EdgeInsets.all(32.0),
                child: Center(
                  child: Column(
                    children: [
                      Icon(
                        Icons.calendar_today,
                        size: 48,
                        color: theme.colorScheme.onSurface.withOpacity(0.3),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        isArabic ? 'لا توجد نوافذ رش متاحة' : 'No spray windows available',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface.withOpacity(0.6),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }

            // Show only next 3 windows
            final nextWindows = windows.take(3).toList();

            return Column(
              children: nextWindows.map((window) {
                return SprayWindowCard(
                  window: window,
                  locale: _locale,
                  onTap: () => _showWindowDetailsDialog(window),
                );
              }).toList(),
            );
          },
          loading: () => const Center(
            child: Padding(
              padding: EdgeInsets.all(32.0),
              child: CircularProgressIndicator(),
            ),
          ),
          error: (error, stack) => Padding(
            padding: const EdgeInsets.all(16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 48,
                      color: theme.colorScheme.error,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      isArabic ? 'فشل في جلب نوافذ الرش' : 'Failed to load spray windows',
                      style: theme.textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () => ref.invalidate(sprayWindowsProvider),
                      child: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationsSection(ThemeData theme, bool isArabic) {
    final recommendationsAsync = ref.watch(sprayRecommendationsProvider(
      SprayRecommendationFilter(
        fieldId: widget.fieldId,
        status: RecommendationStatus.active,
      ),
    ));

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                isArabic ? 'التوصيات النشطة' : 'Active Recommendations',
                style: theme.textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              TextButton.icon(
                onPressed: () {
                  // Navigate to all recommendations
                },
                icon: const Icon(Icons.list, size: 18),
                label: Text(isArabic ? 'عرض الكل' : 'View All'),
              ),
            ],
          ),
        ),
        const SizedBox(height: 12),
        recommendationsAsync.when(
          data: (recommendations) {
            if (recommendations.isEmpty) {
              return Padding(
                padding: const EdgeInsets.all(32.0),
                child: Center(
                  child: Column(
                    children: [
                      Icon(
                        Icons.check_circle_outline,
                        size: 48,
                        color: theme.colorScheme.onSurface.withOpacity(0.3),
                      ),
                      const SizedBox(height: 16),
                      Text(
                        isArabic ? 'لا توجد توصيات نشطة' : 'No active recommendations',
                        style: theme.textTheme.bodyMedium?.copyWith(
                          color: theme.colorScheme.onSurface.withOpacity(0.6),
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }

            return ListView.builder(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: recommendations.length,
              itemBuilder: (context, index) {
                final recommendation = recommendations[index];
                return _buildRecommendationCard(recommendation, theme, isArabic);
              },
            );
          },
          loading: () => const Center(
            child: Padding(
              padding: EdgeInsets.all(32.0),
              child: CircularProgressIndicator(),
            ),
          ),
          error: (error, stack) => Padding(
            padding: const EdgeInsets.all(16),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Icon(
                      Icons.error_outline,
                      size: 48,
                      color: theme.colorScheme.error,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      isArabic ? 'فشل في جلب التوصيات' : 'Failed to load recommendations',
                      style: theme.textTheme.bodyMedium,
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () => ref.invalidate(sprayRecommendationsProvider),
                      child: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationCard(SprayRecommendation recommendation, ThemeData theme, bool isArabic) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: () {
          // Navigate to recommendation details
        },
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: _getSprayTypeColor(recommendation.sprayType).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      recommendation.sprayType.getName(_locale),
                      style: TextStyle(
                        color: _getSprayTypeColor(recommendation.sprayType),
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const Spacer(),
                  if (recommendation.priority >= 4)
                    Icon(Icons.priority_high, color: Colors.red, size: 20),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                recommendation.getTitle(_locale),
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                recommendation.getDescription(_locale),
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurface.withOpacity(0.7),
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              if (recommendation.recommendedProduct != null) ...[
                const SizedBox(height: 8),
                const Divider(),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.science, size: 16, color: theme.colorScheme.primary),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        recommendation.recommendedProduct!.getDisplayName(_locale),
                        style: theme.textTheme.bodySmall,
                      ),
                    ),
                  ],
                ),
              ],
              if (recommendation.nextOptimalWindow != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.schedule, size: 16, color: Colors.green),
                    const SizedBox(width: 8),
                    Text(
                      '${isArabic ? 'النافذة التالية: ' : 'Next window: '}${_formatWindowTime(recommendation.nextOptimalWindow!)}',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: Colors.green.shade700,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionsSection(ThemeData theme, bool isArabic) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'إجراءات سريعة' : 'Quick Actions',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  icon: Icons.add_circle,
                  label: isArabic ? 'تسجيل رش' : 'Log Spray',
                  color: Colors.blue,
                  onTap: () {
                    // Navigate to spray log form
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  icon: Icons.calendar_month,
                  label: isArabic ? 'عرض التقويم' : 'View Calendar',
                  color: Colors.green,
                  onTap: () {
                    // Navigate to calendar
                  },
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  icon: Icons.history,
                  label: isArabic ? 'سجل الرش' : 'Spray History',
                  color: Colors.orange,
                  onTap: () {
                    // Navigate to logs
                  },
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  icon: Icons.science,
                  label: isArabic ? 'المنتجات' : 'Products',
                  color: Colors.purple,
                  onTap: () {
                    // Navigate to products
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionCard({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 28),
              ),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w500,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getSprayTypeColor(SprayType type) {
    switch (type) {
      case SprayType.herbicide:
        return Colors.green;
      case SprayType.fungicide:
        return Colors.orange;
      case SprayType.insecticide:
        return Colors.red;
      case SprayType.foliar:
        return Colors.blue;
    }
  }

  String _formatWindowTime(SprayWindow window) {
    final format = DateFormat('HH:mm');
    return format.format(window.startTime);
  }

  void _showWeatherDetailsDialog(WeatherCondition weather) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_locale == 'ar' ? 'تفاصيل الطقس' : 'Weather Details'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow(
              _locale == 'ar' ? 'الحالة' : 'Condition',
              weather.getCondition(_locale),
            ),
            _buildDetailRow(
              _locale == 'ar' ? 'درجة الحرارة' : 'Temperature',
              '${weather.temperature}°C',
            ),
            _buildDetailRow(
              _locale == 'ar' ? 'الرطوبة' : 'Humidity',
              '${weather.humidity}%',
            ),
            _buildDetailRow(
              _locale == 'ar' ? 'سرعة الرياح' : 'Wind Speed',
              '${weather.windSpeed} km/h',
            ),
            _buildDetailRow(
              _locale == 'ar' ? 'اتجاه الرياح' : 'Wind Direction',
              weather.getWindDirection(_locale),
            ),
            _buildDetailRow(
              _locale == 'ar' ? 'احتمالية المطر' : 'Rain Probability',
              '${weather.rainProbability}%',
            ),
            if (weather.pressure != null)
              _buildDetailRow(
                _locale == 'ar' ? 'الضغط الجوي' : 'Pressure',
                '${weather.pressure} hPa',
              ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(_locale == 'ar' ? 'إغلاق' : 'Close'),
          ),
        ],
      ),
    );
  }

  void _showWindowDetailsDialog(SprayWindow window) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(_locale == 'ar' ? 'تفاصيل نافذة الرش' : 'Spray Window Details'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SprayWindowCard(window: window, locale: _locale),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text(_locale == 'ar' ? 'إغلاق' : 'Close'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value),
        ],
      ),
    );
  }
}
