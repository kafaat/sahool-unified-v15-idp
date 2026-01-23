/// Spray Window Card Widget - بطاقة نافذة الرش
/// عرض معلومات نافذة الرش المثلى
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../models/spray_models.dart';

class SprayWindowCard extends StatelessWidget {
  final SprayWindow window;
  final String locale;
  final VoidCallback? onTap;

  const SprayWindowCard({
    Key? key,
    required this.window,
    this.locale = 'ar',
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = locale == 'ar';

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(16),
            gradient: LinearGradient(
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
              colors: [
                _getStatusColor(window.status).withOpacity(0.1),
                _getStatusColor(window.status).withOpacity(0.05),
              ],
            ),
            border: Border.all(
              color: _getStatusColor(window.status),
              width: 2,
            ),
          ),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header: Status Badge & Time Range
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _buildStatusBadge(theme, isArabic),
                    _buildConfidenceScore(theme),
                  ],
                ),
                const SizedBox(height: 12),
                // Time Range
                Row(
                  children: [
                    Icon(
                      Icons.schedule,
                      size: 20,
                      color: theme.colorScheme.primary,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        _formatTimeRange(isArabic),
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                // Duration
                Text(
                  _formatDuration(isArabic),
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurface.withOpacity(0.6),
                  ),
                ),
                const SizedBox(height: 12),
                const Divider(),
                const SizedBox(height: 12),
                // Weather Conditions Summary
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildConditionChip(
                      icon: Icons.thermostat,
                      label: '${window.weatherCondition.temperature.toStringAsFixed(0)}°C',
                      theme: theme,
                    ),
                    _buildConditionChip(
                      icon: Icons.water_drop,
                      label: '${window.weatherCondition.humidity.toStringAsFixed(0)}%',
                      theme: theme,
                    ),
                    _buildConditionChip(
                      icon: Icons.air,
                      label: '${window.weatherCondition.windSpeed.toStringAsFixed(0)} km/h',
                      theme: theme,
                    ),
                    _buildConditionChip(
                      icon: Icons.umbrella,
                      label: '${window.weatherCondition.rainProbability.toStringAsFixed(0)}%',
                      theme: theme,
                    ),
                  ],
                ),
                // Reason (if available)
                if (window.getReason(locale) != null) ...[
                  const SizedBox(height: 12),
                  const Divider(),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Icon(
                        Icons.info_outline,
                        size: 16,
                        color: theme.colorScheme.primary,
                      ),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          window.getReason(locale)!,
                          style: theme.textTheme.bodySmall?.copyWith(
                            fontStyle: FontStyle.italic,
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
                // Warnings (if any)
                if (window.getWarnings(locale).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  ...window.getWarnings(locale).map((warning) => Padding(
                        padding: const EdgeInsets.only(bottom: 4),
                        child: Row(
                          children: [
                            Icon(
                              Icons.warning_amber,
                              size: 16,
                              color: Colors.orange,
                            ),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                warning,
                                style: theme.textTheme.bodySmall?.copyWith(
                                  color: Colors.orange.shade700,
                                ),
                              ),
                            ),
                          ],
                        ),
                      )),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatusBadge(ThemeData theme, bool isArabic) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getStatusColor(window.status),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            _getStatusIcon(window.status),
            color: Colors.white,
            size: 16,
          ),
          const SizedBox(width: 6),
          Text(
            window.status.getName(locale),
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

  Widget _buildConfidenceScore(ThemeData theme) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: theme.colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.check_circle,
            color: theme.colorScheme.primary,
            size: 16,
          ),
          const SizedBox(width: 4),
          Text(
            '${window.confidenceScore}%',
            style: TextStyle(
              color: theme.colorScheme.primary,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConditionChip({
    required IconData icon,
    required String label,
    required ThemeData theme,
  }) {
    return Column(
      children: [
        Icon(icon, size: 18, color: theme.colorScheme.primary),
        const SizedBox(height: 4),
        Text(
          label,
          style: theme.textTheme.bodySmall?.copyWith(
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Color _getStatusColor(SprayWindowStatus status) {
    switch (status) {
      case SprayWindowStatus.optimal:
        return Colors.green;
      case SprayWindowStatus.caution:
        return Colors.orange;
      case SprayWindowStatus.avoid:
        return Colors.red;
    }
  }

  IconData _getStatusIcon(SprayWindowStatus status) {
    switch (status) {
      case SprayWindowStatus.optimal:
        return Icons.check_circle;
      case SprayWindowStatus.caution:
        return Icons.warning;
      case SprayWindowStatus.avoid:
        return Icons.cancel;
    }
  }

  String _formatTimeRange(bool isArabic) {
    final dateFormat = DateFormat(isArabic ? 'dd MMM yyyy' : 'MMM dd, yyyy', isArabic ? 'ar' : 'en');
    final timeFormat = DateFormat('HH:mm');

    final startDate = dateFormat.format(window.startTime);
    final startTime = timeFormat.format(window.startTime);
    final endTime = timeFormat.format(window.endTime);

    if (window.startTime.day == window.endTime.day) {
      return '$startDate • $startTime - $endTime';
    } else {
      final endDate = dateFormat.format(window.endTime);
      return '$startDate $startTime - $endDate $endTime';
    }
  }

  String _formatDuration(bool isArabic) {
    final hours = window.durationHours;
    if (isArabic) {
      return hours == 1 ? 'ساعة واحدة' : '$hours ساعات';
    } else {
      return hours == 1 ? '1 hour' : '$hours hours';
    }
  }
}

/// Compact Timeline Item for Calendar View
class SprayWindowTimelineItem extends StatelessWidget {
  final SprayWindow window;
  final String locale;
  final VoidCallback? onTap;

  const SprayWindowTimelineItem({
    Key? key,
    required this.window,
    this.locale = 'ar',
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isArabic = locale == 'ar';
    final statusColor = _getStatusColor(window.status);

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          children: [
            // Timeline indicator
            Column(
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: statusColor,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: statusColor,
                      width: 2,
                    ),
                  ),
                ),
                if (!window.isExpired)
                  Container(
                    width: 2,
                    height: 40,
                    color: statusColor.withOpacity(0.3),
                  ),
              ],
            ),
            const SizedBox(width: 16),
            // Content
            Expanded(
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: statusColor.withOpacity(0.3),
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          _formatTime(window.startTime),
                          style: theme.textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          window.status.getName(locale),
                          style: TextStyle(
                            color: statusColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 11,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.thermostat, size: 14, color: theme.colorScheme.onSurface.withOpacity(0.6)),
                        const SizedBox(width: 4),
                        Text(
                          '${window.weatherCondition.temperature.toStringAsFixed(0)}°C',
                          style: theme.textTheme.bodySmall,
                        ),
                        const SizedBox(width: 12),
                        Icon(Icons.air, size: 14, color: theme.colorScheme.onSurface.withOpacity(0.6)),
                        const SizedBox(width: 4),
                        Text(
                          '${window.weatherCondition.windSpeed.toStringAsFixed(0)} km/h',
                          style: theme.textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getStatusColor(SprayWindowStatus status) {
    switch (status) {
      case SprayWindowStatus.optimal:
        return Colors.green;
      case SprayWindowStatus.caution:
        return Colors.orange;
      case SprayWindowStatus.avoid:
        return Colors.red;
    }
  }

  String _formatTime(DateTime time) {
    final hour = time.hour;
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
