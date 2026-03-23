import 'package:flutter/material.dart';
import '../../domain/entities/weather_entities.dart';

/// بطاقة تنبيه الطقس
class WeatherAlertCard extends StatelessWidget {
  final WeatherAlert alert;
  final VoidCallback? onTap;

  const WeatherAlertCard({
    super.key,
    required this.alert,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getSeverityColor();
    final icon = _getSeverityIcon();

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: color, width: 2),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // الرأس
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(icon, color: color, size: 24),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          alert.titleAr,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                fontWeight: FontWeight.bold,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: color,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            _getSeverityLabel(),
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 12),

              // الوصف
              Text(
                alert.description,
                style: Theme.of(context).textTheme.bodyMedium,
              ),

              const SizedBox(height: 12),

              // الوقت
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.schedule, size: 16, color: Colors.grey),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'من ${_formatDateTime(alert.startTime)} إلى ${_formatDateTime(alert.endTime)}',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[600],
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              // الوقت المتبقي
              if (alert.endTime.isAfter(DateTime.now())) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    Icon(Icons.timer, size: 14, color: color),
                    const SizedBox(width: 4),
                    Text(
                      'ينتهي خلال ${_getRemainingTime()}',
                      style: TextStyle(
                        fontSize: 12,
                        color: color,
                        fontWeight: FontWeight.bold,
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

  Color _getSeverityColor() {
    switch (alert.severity) {
      case 'warning':
        return Colors.red;
      case 'watch':
        return Colors.orange;
      case 'advisory':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _getSeverityIcon() {
    switch (alert.severity) {
      case 'warning':
        return Icons.warning;
      case 'watch':
        return Icons.visibility;
      case 'advisory':
        return Icons.info;
      default:
        return Icons.notifications;
    }
  }

  String _getSeverityLabel() {
    switch (alert.severity) {
      case 'warning':
        return 'تحذير';
      case 'watch':
        return 'مراقبة';
      case 'advisory':
        return 'إرشادي';
      default:
        return alert.severity;
    }
  }

  String _formatDateTime(DateTime dt) {
    return '${dt.day}/${dt.month} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
  }

  String _getRemainingTime() {
    final remaining = alert.endTime.difference(DateTime.now());
    if (remaining.inDays > 0) {
      return '${remaining.inDays} يوم';
    } else if (remaining.inHours > 0) {
      return '${remaining.inHours} ساعة';
    } else {
      return '${remaining.inMinutes} دقيقة';
    }
  }
}
