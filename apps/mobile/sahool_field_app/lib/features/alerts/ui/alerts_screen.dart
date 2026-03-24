import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../smart_alerts/presentation/providers/smart_alerts_provider.dart';

/// Alerts Screen - شاشة التنبيهات
/// Connected to alert-service via Kong gateway
class AlertsScreen extends ConsumerStatefulWidget {
  const AlertsScreen({super.key});

  @override
  ConsumerState<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends ConsumerState<AlertsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final alertsState = ref.watch(allAlertsProvider);

    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        title: const Text('التنبيهات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.done_all),
            onPressed: () => _markAllAsRead(ref),
            tooltip: 'قراءة الكل',
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(allAlertsProvider),
            tooltip: 'تحديث',
          ),
        ],
        bottom: TabBar(
          controller: _tabController,
          labelColor: SahoolColors.primary,
          unselectedLabelColor: Colors.grey,
          indicatorColor: SahoolColors.primary,
          tabs: [
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('الكل'),
                  const SizedBox(width: 6),
                  alertsState.when(
                    data: (alerts) => _buildBadge(alerts.length),
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('غير مقروءة'),
                  const SizedBox(width: 6),
                  alertsState.when(
                    data: (alerts) =>
                        _buildBadge(alerts.where((a) => !a.isRead).length),
                    loading: () => const SizedBox.shrink(),
                    error: (_, __) => const SizedBox.shrink(),
                  ),
                ],
              ),
            ),
            const Tab(text: 'عاجلة'),
          ],
        ),
      ),
      body: alertsState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildErrorState(error.toString()),
        data: (alerts) => TabBarView(
          controller: _tabController,
          children: [
            _buildAlertsList(alerts),
            _buildAlertsList(alerts.where((a) => !a.isRead).toList()),
            _buildAlertsList(alerts
                .where((a) => a.severity == AlertSeverity.critical)
                .toList()),
          ],
        ),
      ),
    );
  }

  Widget _buildBadge(int count) {
    if (count == 0) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: SahoolColors.danger,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Text(
        count.toString(),
        style: const TextStyle(color: Colors.white, fontSize: 10),
      ),
    );
  }

  Widget _buildErrorState(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cloud_off, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            'تعذر تحميل التنبيهات',
            style: TextStyle(color: Colors.grey[600], fontSize: 16),
          ),
          const SizedBox(height: 8),
          TextButton.icon(
            onPressed: () => ref.invalidate(allAlertsProvider),
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertsList(List<SmartAlert> alerts) {
    if (alerts.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.notifications_off, size: 64, color: Colors.grey[300]),
            const SizedBox(height: 16),
            Text(
              'لا توجد تنبيهات',
              style: TextStyle(color: Colors.grey[600], fontSize: 16),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(allAlertsProvider);
        await ref.read(allAlertsProvider.future);
      },
      child: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: alerts.length,
        itemBuilder: (context, index) {
          final alert = alerts[index];
          return _AlertCard(
            alert: alert,
            onTap: () => _onAlertTap(alert),
            onDismiss: () => _onAlertDismiss(alert),
          );
        },
      ),
    );
  }

  void _onAlertTap(SmartAlert alert) {
    // Acknowledge the alert via API
    ref.read(acknowledgeAlertProvider(
      (alertId: alert.id, userId: 'current_user'),
    ));
  }

  void _onAlertDismiss(SmartAlert alert) {
    ref.read(dismissAlertProvider(
      (alertId: alert.id, userId: 'current_user'),
    ));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم رفض التنبيه')),
    );
  }

  void _markAllAsRead(WidgetRef ref) {
    final alerts = ref.read(allAlertsProvider).valueOrNull ?? [];
    for (final alert in alerts) {
      if (!alert.isRead) {
        ref.read(acknowledgeAlertProvider(
          (alertId: alert.id, userId: 'current_user'),
        ));
      }
    }
  }
}

class _AlertCard extends StatelessWidget {
  final SmartAlert alert;
  final VoidCallback onTap;
  final VoidCallback onDismiss;

  const _AlertCard({
    required this.alert,
    required this.onTap,
    required this.onDismiss,
  });

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: Key(alert.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismiss(),
      background: Container(
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.only(left: 20),
        decoration: BoxDecoration(
          color: SahoolColors.danger,
          borderRadius: BorderRadius.circular(16),
        ),
        child: const Icon(Icons.delete, color: Colors.white),
      ),
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          margin: const EdgeInsets.only(bottom: 12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: alert.isRead
                ? Colors.white
                : _getSeverityColor(alert.severity).withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: alert.isRead
                  ? Colors.grey[200]!
                  : _getSeverityColor(alert.severity).withValues(alpha: 0.3),
            ),
            boxShadow: SahoolShadows.small,
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _getSeverityColor(alert.severity).withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  _getTypeIcon(alert.type),
                  color: _getSeverityColor(alert.severity),
                  size: 24,
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        if (!alert.isRead)
                          Container(
                            width: 8,
                            height: 8,
                            margin: const EdgeInsets.only(left: 8),
                            decoration: BoxDecoration(
                              color: _getSeverityColor(alert.severity),
                              shape: BoxShape.circle,
                            ),
                          ),
                        Expanded(
                          child: Text(
                            alert.title,
                            style: TextStyle(
                              fontWeight: alert.isRead
                                  ? FontWeight.normal
                                  : FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ],
                    ),
                    if (alert.message != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        alert.message!,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                    const SizedBox(height: 8),
                    Text(
                      alert.timeAgo,
                      style: TextStyle(
                        color: Colors.grey[400],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              ),
              Icon(Icons.chevron_left, color: Colors.grey[400]),
            ],
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
        return SahoolColors.warning;
      case AlertSeverity.info:
        return SahoolColors.info;
      case AlertSeverity.success:
        return SahoolColors.success;
    }
  }

  IconData _getTypeIcon(AlertType type) {
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
}
