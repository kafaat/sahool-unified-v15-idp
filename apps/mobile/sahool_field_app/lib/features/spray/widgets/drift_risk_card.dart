/// Drift Risk Card Widget - بطاقة خطر الانجراف
/// Displays drift risk assessment for spray operations
library;

import 'package:flutter/material.dart';

import '../models/spray_models.dart';

/// Drift Risk Assessment Card
/// Displays comprehensive drift risk information based on weather conditions
class DriftRiskCard extends StatelessWidget {
  final WeatherCondition weather;
  final String locale;
  final VoidCallback? onTap;

  const DriftRiskCard({
    super.key,
    required this.weather,
    this.locale = 'ar',
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = locale == 'ar';
    final riskLevel = weather.driftRiskLevel;
    final riskScore = weather.driftRiskScore;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: DecoratedBox(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                _getRiskColor(riskLevel).withValues(alpha: 0.1),
                _getRiskColor(riskLevel).withValues(alpha: 0.05),
              ],
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Icon(
                          Icons.warning_amber_rounded,
                          color: _getRiskColor(riskLevel),
                          size: 24,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          isArabic ? 'خطر الانجراف' : 'Drift Risk',
                          style: theme.textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    _buildRiskBadge(riskLevel, theme, isArabic),
                  ],
                ),
                const SizedBox(height: 16),

                // Risk Score Progress Bar
                _buildRiskProgressBar(riskScore, theme),
                const SizedBox(height: 8),
                Text(
                  isArabic
                      ? 'مستوى الخطر: $riskScore/100'
                      : 'Risk Level: $riskScore/100',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withValues(alpha: 0.6),
                  ),
                ),

                const SizedBox(height: 16),
                const Divider(),
                const SizedBox(height: 12),

                // Risk Factors
                Text(
                  isArabic ? 'عوامل الخطر:' : 'Risk Factors:',
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
                ),
                const SizedBox(height: 8),

                // Wind Speed Factor
                _buildRiskFactor(
                  icon: Icons.air,
                  label: isArabic ? 'سرعة الرياح' : 'Wind Speed',
                  value: '${weather.windSpeed.toStringAsFixed(1)} km/h',
                  riskContribution: _getWindRiskContribution(weather.windSpeed),
                  theme: theme,
                  isArabic: isArabic,
                ),

                // Temperature Factor
                _buildRiskFactor(
                  icon: Icons.thermostat,
                  label: isArabic ? 'درجة الحرارة' : 'Temperature',
                  value: '${weather.temperature.toStringAsFixed(1)}°C',
                  riskContribution:
                      _getTempRiskContribution(weather.temperature),
                  theme: theme,
                  isArabic: isArabic,
                ),

                // Humidity Factor
                _buildRiskFactor(
                  icon: Icons.water_drop,
                  label: isArabic ? 'الرطوبة' : 'Humidity',
                  value: '${weather.humidity.toStringAsFixed(0)}%',
                  riskContribution:
                      _getHumidityRiskContribution(weather.humidity),
                  theme: theme,
                  isArabic: isArabic,
                ),

                const SizedBox(height: 16),

                // Recommendations
                _buildRecommendation(riskLevel, theme, isArabic),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRiskBadge(DriftRiskLevel level, ThemeData theme, bool isArabic) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getRiskColor(level),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getRiskIcon(level),
            color: Colors.white,
            size: 16,
          ),
          const SizedBox(width: 6),
          Text(
            level.getName(locale),
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskProgressBar(int score, ThemeData theme) {
    final color = score >= 60
        ? Colors.red
        : score >= 30
            ? Colors.orange
            : Colors.green;

    return ClipRRect(
      borderRadius: BorderRadius.circular(8),
      child: LinearProgressIndicator(
        value: score / 100,
        minHeight: 10,
        backgroundColor: theme.colorScheme.surfaceContainerHighest,
        valueColor: AlwaysStoppedAnimation<Color>(color),
      ),
    );
  }

  Widget _buildRiskFactor({
    required IconData icon,
    required String label,
    required String value,
    required String riskContribution,
    required ThemeData theme,
    required bool isArabic,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 18, color: theme.colorScheme.primary),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              label,
              style: theme.textTheme.bodyMedium,
            ),
          ),
          Text(
            value,
            style: theme.textTheme.bodyMedium?.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(width: 8),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: _getRiskContributionColor(riskContribution),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Text(
              riskContribution,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 10,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendation(
      DriftRiskLevel level, ThemeData theme, bool isArabic) {
    String recommendation;
    IconData icon;
    MaterialColor color;

    switch (level) {
      case DriftRiskLevel.low:
        recommendation = isArabic
            ? 'ظروف آمنة للرش. يمكنك المتابعة مع اتخاذ الاحتياطات القياسية.'
            : 'Safe conditions for spraying. Proceed with standard precautions.';
        icon = Icons.check_circle;
        color = Colors.green;
        break;
      case DriftRiskLevel.medium:
        recommendation = isArabic
            ? 'كن حذرًا عند الرش. استخدم فوهات ذات قطرات أكبر وقلل من الضغط.'
            : 'Use caution when spraying. Use larger droplet nozzles and reduce pressure.';
        icon = Icons.warning_amber;
        color = Colors.orange;
        break;
      case DriftRiskLevel.high:
        recommendation = isArabic
            ? 'يُنصح بتأجيل الرش. خطر انجراف المبيدات مرتفع جدًا.'
            : 'Recommend postponing spray. Drift risk is too high.';
        icon = Icons.cancel;
        color = Colors.red;
        break;
    }

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              recommendation,
              style: theme.textTheme.bodySmall?.copyWith(
                color: color.shade700,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getRiskColor(DriftRiskLevel level) {
    switch (level) {
      case DriftRiskLevel.low:
        return Colors.green;
      case DriftRiskLevel.medium:
        return Colors.orange;
      case DriftRiskLevel.high:
        return Colors.red;
    }
  }

  IconData _getRiskIcon(DriftRiskLevel level) {
    switch (level) {
      case DriftRiskLevel.low:
        return Icons.check_circle;
      case DriftRiskLevel.medium:
        return Icons.warning;
      case DriftRiskLevel.high:
        return Icons.dangerous;
    }
  }

  String _getWindRiskContribution(double windSpeed) {
    if (windSpeed >= 20) return 'HIGH';
    if (windSpeed >= 15) return 'MED';
    if (windSpeed >= 10) return 'LOW';
    return 'MIN';
  }

  String _getTempRiskContribution(double temperature) {
    if (temperature > 30) return 'HIGH';
    if (temperature > 25) return 'MED';
    if (temperature < 10) return 'LOW';
    return 'MIN';
  }

  String _getHumidityRiskContribution(double humidity) {
    if (humidity < 40) return 'HIGH';
    if (humidity < 50) return 'MED';
    if (humidity < 60) return 'LOW';
    return 'MIN';
  }

  Color _getRiskContributionColor(String contribution) {
    switch (contribution) {
      case 'HIGH':
        return Colors.red;
      case 'MED':
        return Colors.orange;
      case 'LOW':
        return Colors.yellow.shade700;
      default:
        return Colors.green;
    }
  }
}

/// Compact Drift Risk Indicator
/// A small indicator for use in lists or compact spaces
class CompactDriftRiskIndicator extends StatelessWidget {
  final WeatherCondition weather;
  final String locale;

  const CompactDriftRiskIndicator({
    super.key,
    required this.weather,
    this.locale = 'ar',
  });

  @override
  Widget build(BuildContext context) {
    final riskLevel = weather.driftRiskLevel;
    final riskScore = weather.driftRiskScore;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: _getRiskColor(riskLevel).withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: _getRiskColor(riskLevel).withValues(alpha: 0.5),
        ),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.warning_amber_rounded,
            size: 14,
            color: _getRiskColor(riskLevel),
          ),
          const SizedBox(width: 4),
          Text(
            '$riskScore%',
            style: TextStyle(
              color: _getRiskColor(riskLevel),
              fontWeight: FontWeight.bold,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Color _getRiskColor(DriftRiskLevel level) {
    switch (level) {
      case DriftRiskLevel.low:
        return Colors.green;
      case DriftRiskLevel.medium:
        return Colors.orange;
      case DriftRiskLevel.high:
        return Colors.red;
    }
  }
}
