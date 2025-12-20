import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../providers/smart_alerts_provider.dart';

/// SAHOOL Smart Alerts Center
/// مركز التنبيهات الذكية
///
/// Features:
/// - Real-time alerts from IoT sensors
/// - Weather-based alerts
/// - NDVI drop notifications
/// - Actionable recommendations

class SmartAlertsCenter extends ConsumerWidget {
  final int maxAlerts;
  final bool showViewAll;

  const SmartAlertsCenter({
    super.key,
    this.maxAlerts = 5,
    this.showViewAll = true,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final alertsState = ref.watch(smartAlertsProvider);

    return alertsState.when(
      loading: () => const _AlertsLoading(),
      error: (error, _) => _AlertsError(error: error.toString()),
      data: (alerts) => _AlertsList(
        alerts: alerts.take(maxAlerts).toList(),
        showViewAll: showViewAll && alerts.length > maxAlerts,
        totalCount: alerts.length,
      ),
    );
  }
}

/// Alerts List
class _AlertsList extends StatelessWidget {
  final List<SmartAlert> alerts;
  final bool showViewAll;
  final int totalCount;

  const _AlertsList({
    required this.alerts,
    required this.showViewAll,
    required this.totalCount,
  });

  @override
  Widget build(BuildContext context) {
    if (alerts.isEmpty) {
      return const _NoAlertsWidget();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Header
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Row(
                children: [
                  const Icon(
                    Icons.notifications_active_rounded,
                    color: SahoolColors.forestGreen,
                    size: 22,
                  ),
                  const SizedBox(width: 8),
                  const Text(
                    'التنبيهات الذكية',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  if (totalCount > 0) ...[
                    const SizedBox(width: 8),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 8,
                        vertical: 2,
                      ),
                      decoration: BoxDecoration(
                        color: SahoolColors.danger.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        '$totalCount',
                        style: const TextStyle(
                          color: SahoolColors.danger,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
              if (showViewAll)
                TextButton(
                  onPressed: () {
                    // Navigate to all alerts
                  },
                  child: const Text('عرض الكل'),
                ),
            ],
          ),
        ),

        const SizedBox(height: 12),

        // Alerts
        ...alerts.map((alert) => _AlertCard(alert: alert)),
      ],
    );
  }
}

/// Alert Card
class _AlertCard extends StatelessWidget {
  final SmartAlert alert;

  const _AlertCard({required this.alert});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border(
          right: BorderSide(
            color: _getSeverityColor(alert.severity),
            width: 4,
          ),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () => _handleAlertTap(context, alert),
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header Row
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: _getSeverityColor(alert.severity).withOpacity(0.1),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        _getAlertIcon(alert.type),
                        color: _getSeverityColor(alert.severity),
                        size: 20,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            alert.title,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            alert.source,
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Text(
                      alert.timeAgo,
                      style: TextStyle(
                        color: Colors.grey[400],
                        fontSize: 11,
                      ),
                    ),
                  ],
                ),

                // Message
                if (alert.message != null) ...[
                  const SizedBox(height: 12),
                  Text(
                    alert.message!,
                    style: TextStyle(
                      color: Colors.grey[700],
                      fontSize: 13,
                    ),
                  ),
                ],

                // Action
                if (alert.action != null) ...[
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      TextButton.icon(
                        onPressed: () => _handleAction(context, alert),
                        icon: Icon(
                          _getActionIcon(alert.action!.type),
                          size: 16,
                        ),
                        label: Text(alert.action!.label),
                        style: TextButton.styleFrom(
                          foregroundColor: SahoolColors.primary,
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                          backgroundColor: SahoolColors.primary.withOpacity(0.1),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(20),
                          ),
                        ),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ),
      ),
    );
  }

  Color _getSeverityColor(AlertSeverity severity) {
    switch (severity) {
      case AlertSeverity.critical:
        return SahoolColors.danger;
      case AlertSeverity.warning:
        return Colors.orange;
      case AlertSeverity.info:
        return SahoolColors.info;
      case AlertSeverity.success:
        return SahoolColors.success;
    }
  }

  IconData _getAlertIcon(AlertType type) {
    switch (type) {
      case AlertType.irrigation:
        return Icons.water_drop_rounded;
      case AlertType.weather:
        return Icons.wb_sunny_rounded;
      case AlertType.ndvi:
        return Icons.eco_rounded;
      case AlertType.sensor:
        return Icons.sensors_rounded;
      case AlertType.task:
        return Icons.task_alt_rounded;
      case AlertType.pest:
        return Icons.bug_report_rounded;
      case AlertType.system:
        return Icons.info_rounded;
    }
  }

  IconData _getActionIcon(AlertActionType type) {
    switch (type) {
      case AlertActionType.irrigate:
        return Icons.water_drop_outlined;
      case AlertActionType.inspect:
        return Icons.search_rounded;
      case AlertActionType.createTask:
        return Icons.add_task_rounded;
      case AlertActionType.viewDetails:
        return Icons.visibility_rounded;
      case AlertActionType.dismiss:
        return Icons.close_rounded;
    }
  }

  void _handleAlertTap(BuildContext context, SmartAlert alert) {
    // Navigate to alert details or related screen
  }

  void _handleAction(BuildContext context, SmartAlert alert) {
    // Execute the action
  }
}

/// No Alerts Widget
class _NoAlertsWidget extends StatelessWidget {
  const _NoAlertsWidget();

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: SahoolColors.success.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: SahoolColors.success.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: const Icon(
              Icons.check_circle_rounded,
              color: SahoolColors.success,
              size: 28,
            ),
          ),
          const SizedBox(width: 16),
          const Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'لا توجد تنبيهات',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                SizedBox(height: 4),
                Text(
                  'كل شيء على ما يرام! حقولك في حالة جيدة',
                  style: TextStyle(
                    color: Colors.grey,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Loading State
class _AlertsLoading extends StatelessWidget {
  const _AlertsLoading();

  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(16),
      child: Center(
        child: CircularProgressIndicator(),
      ),
    );
  }
}

/// Error State
class _AlertsError extends StatelessWidget {
  final String error;

  const _AlertsError({required this.error});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.red.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          const Icon(Icons.error_outline, color: Colors.red),
          const SizedBox(width: 12),
          const Expanded(
            child: Text('تعذر تحميل التنبيهات'),
          ),
          TextButton(
            onPressed: () {},
            child: const Text('إعادة'),
          ),
        ],
      ),
    );
  }
}
