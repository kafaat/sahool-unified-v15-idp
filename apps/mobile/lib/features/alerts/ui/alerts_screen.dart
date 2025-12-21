import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

/// Alerts Screen - شاشة التنبيهات
class AlertsScreen extends StatefulWidget {
  const AlertsScreen({super.key});

  @override
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  final List<_Alert> _alerts = [
    _Alert(
      id: '1',
      title: 'نقص النيتروجين',
      subtitle: 'حقل القمح الشمالي يحتاج تسميد عاجل',
      type: AlertType.warning,
      time: DateTime.now().subtract(const Duration(hours: 2)),
      isRead: false,
    ),
    _Alert(
      id: '2',
      title: 'موعد الري',
      subtitle: 'حقل الذرة يحتاج ري خلال 4 ساعات',
      type: AlertType.info,
      time: DateTime.now().subtract(const Duration(hours: 5)),
      isRead: false,
    ),
    _Alert(
      id: '3',
      title: 'تنبيه آفات',
      subtitle: 'رصد حشرات في حقل البن - يرجى الفحص',
      type: AlertType.danger,
      time: DateTime.now().subtract(const Duration(days: 1)),
      isRead: true,
    ),
    _Alert(
      id: '4',
      title: 'تحديث NDVI',
      subtitle: 'تم تحديث بيانات صحة المحاصيل',
      type: AlertType.success,
      time: DateTime.now().subtract(const Duration(days: 2)),
      isRead: true,
    ),
  ];

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
    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        title: const Text('التنبيهات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.done_all),
            onPressed: () => _markAllAsRead(),
            tooltip: 'قراءة الكل',
          ),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {},
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
                  _buildBadge(_alerts.length),
                ],
              ),
            ),
            Tab(
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text('غير مقروءة'),
                  const SizedBox(width: 6),
                  _buildBadge(_alerts.where((a) => !a.isRead).length),
                ],
              ),
            ),
            const Tab(text: 'عاجلة'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildAlertsList(_alerts),
          _buildAlertsList(_alerts.where((a) => !a.isRead).toList()),
          _buildAlertsList(_alerts.where((a) => a.type == AlertType.danger).toList()),
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

  Widget _buildAlertsList(List<_Alert> alerts) {
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

    return ListView.builder(
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
    );
  }

  void _onAlertTap(_Alert alert) {
    setState(() {
      final index = _alerts.indexWhere((a) => a.id == alert.id);
      if (index != -1) {
        _alerts[index] = alert.copyWith(isRead: true);
      }
    });
  }

  void _onAlertDismiss(_Alert alert) {
    setState(() {
      _alerts.removeWhere((a) => a.id == alert.id);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: const Text('تم حذف التنبيه'),
        action: SnackBarAction(
          label: 'تراجع',
          onPressed: () {
            setState(() {
              _alerts.add(alert);
            });
          },
        ),
      ),
    );
  }

  void _markAllAsRead() {
    setState(() {
      for (var i = 0; i < _alerts.length; i++) {
        _alerts[i] = _alerts[i].copyWith(isRead: true);
      }
    });
  }
}

class _AlertCard extends StatelessWidget {
  final _Alert alert;
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
            color: alert.isRead ? Colors.white : alert.type.color.withOpacity(0.05),
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: alert.isRead ? Colors.grey[200]! : alert.type.color.withOpacity(0.3),
            ),
            boxShadow: SahoolShadows.small,
          ),
          child: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: alert.type.color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(alert.type.icon, color: alert.type.color, size: 24),
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
                              fontWeight: alert.isRead ? FontWeight.normal : FontWeight.bold,
                              fontSize: 16,
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 4),
                    Text(
                      alert.subtitle,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 14,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      _formatTime(alert.time),
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

  String _formatTime(DateTime time) {
    final diff = DateTime.now().difference(time);
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} دقيقة';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} ساعة';
    return 'منذ ${diff.inDays} يوم';
  }
}

enum AlertType {
  info(Icons.info, SahoolColors.info),
  warning(Icons.warning_amber, SahoolColors.warning),
  danger(Icons.error, SahoolColors.danger),
  success(Icons.check_circle, SahoolColors.success);

  final IconData icon;
  final Color color;

  const AlertType(this.icon, this.color);
}

class _Alert {
  final String id;
  final String title;
  final String subtitle;
  final AlertType type;
  final DateTime time;
  final bool isRead;

  _Alert({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.type,
    required this.time,
    required this.isRead,
  });

  _Alert copyWith({bool? isRead}) {
    return _Alert(
      id: id,
      title: title,
      subtitle: subtitle,
      type: type,
      time: time,
      isRead: isRead ?? this.isRead,
    );
  }
}
