import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/sahool_theme.dart';
import '../data/alerts_repository.dart';
import '../domain/alert_models.dart';

/// Alerts Screen - شاشة التنبيهات
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
    final alertsAsync = ref.watch(alertsProvider);

    return alertsAsync.when(
      loading: () => _buildScaffold(
        alerts: [],
        isLoading: true,
        child: const Center(child: CircularProgressIndicator()),
      ),
      error: (error, _) => _buildScaffold(
        alerts: [],
        isLoading: false,
        child: _buildErrorState(error.toString().replaceFirst('Exception: ', '')),
      ),
      data: (alerts) => _buildScaffold(
        alerts: alerts,
        isLoading: false,
        child: TabBarView(
          controller: _tabController,
          children: [
            _buildAlertsList(alerts),
            _buildAlertsList(alerts.where((a) => !a.isRead).toList()),
            _buildAlertsList(
                alerts.where((a) => a.type == AlertType.danger).toList()),
          ],
        ),
      ),
    );
  }

  Widget _buildScaffold({
    required List<AlertModel> alerts,
    required bool isLoading,
    required Widget child,
  }) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        title: const Text('التنبيهات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(alertsProvider),
            tooltip: 'تحديث',
          ),
          IconButton(
            icon: const Icon(Icons.done_all),
            onPressed: isLoading ? null : () => _markAllAsRead(alerts),
            tooltip: 'قراءة الكل',
          ),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () => _showFilterSheet(),
            tooltip: 'تصفية',
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
                  _buildBadge(alerts.length),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('غير مقروءة'),
                  const SizedBox(width: 6),
                  _buildBadge(alerts.where((a) => !a.isRead).length),
                ],
              ),
            ),
            const Tab(text: 'عاجلة'),
          ],
        ),
      ),
      body: child,
    );
  }

  Widget _buildErrorState(String message) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cloud_off, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600], fontSize: 16),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () => ref.invalidate(alertsProvider),
            icon: const Icon(Icons.refresh),
            label: const Text('إعادة المحاولة'),
          ),
        ],
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

  Widget _buildAlertsList(List<AlertModel> alerts) {
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
      onRefresh: () => ref.refresh(alertsProvider.future),
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

  void _onAlertTap(AlertModel alert) {
    // Optimistically update local state via a fresh read after acknowledge
    ref.read(alertsRepoProvider).acknowledgeAlert(alert.id).then((_) {
      ref.invalidate(alertsProvider);
    });
  }

  void _onAlertDismiss(AlertModel alert) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('تم حذف التنبيه'),
        action: SnackBarAction(
          label: 'تراجع',
          onPressed: () => ref.invalidate(alertsProvider),
        ),
      ),
    );
    ref.invalidate(alertsProvider);
  }

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetContext) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'تصفية التنبيهات',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const Divider(),
            ListTile(
              leading: const Icon(Icons.all_inclusive, color: SahoolColors.primary),
              title: const Text('جميع التنبيهات'),
              onTap: () {
                Navigator.pop(sheetContext);
                _tabController.animateTo(0);
              },
            ),
            ListTile(
              leading: Icon(AlertType.warning.icon, color: AlertType.warning.color),
              title: const Text('تحذيرات'),
              onTap: () {
                Navigator.pop(sheetContext);
              },
            ),
            ListTile(
              leading: Icon(AlertType.danger.icon, color: AlertType.danger.color),
              title: const Text('عاجلة'),
              onTap: () {
                Navigator.pop(sheetContext);
                _tabController.animateTo(2);
              },
            ),
            ListTile(
              leading: Icon(AlertType.info.icon, color: AlertType.info.color),
              title: const Text('معلوماتية'),
              onTap: () {
                Navigator.pop(sheetContext);
              },
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  void _markAllAsRead(List<AlertModel> alerts) {
    ref.read(alertsRepoProvider).acknowledgeAllAlerts().then((_) {
      ref.invalidate(alertsProvider);
    });
  }
}

class _AlertCard extends StatelessWidget {
  final AlertModel alert;
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
                : alert.type.color.withValues(alpha: 0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: alert.isRead
                  ? Colors.grey[200]!
                  : alert.type.color.withValues(alpha: 0.3),
            ),
            boxShadow: SahoolShadows.small,
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: alert.type.color.withValues(alpha: 0.1),
                  shape: BoxShape.circle,
                ),
                child:
                    Icon(alert.type.icon, color: alert.type.color, size: 24),
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
                              color: alert.type.color,
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
                    const SizedBox(height: 4),
                    Text(
                      alert.subtitle,
                      style:
                          TextStyle(color: Colors.grey[600], fontSize: 14),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _formatTime(alert.time),
                      style:
                          TextStyle(color: Colors.grey[400], fontSize: 12),
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

  String _formatTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}
