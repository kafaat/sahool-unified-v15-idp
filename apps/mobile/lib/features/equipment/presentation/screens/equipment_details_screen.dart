/// Equipment Details Screen - شاشة تفاصيل المعدة
/// Comprehensive equipment details with tabs
library;
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../../state/equipment_providers.dart';
import '../widgets/fuel_gauge.dart';
import '../widgets/status_indicator.dart';
import '../widgets/maintenance_timeline.dart';
import '../widgets/usage_chart.dart';
import 'fuel_log_screen.dart';
import 'schedule_maintenance_screen.dart';

/// Equipment Details Screen
class EquipmentDetailsScreen extends ConsumerStatefulWidget {
  final String equipmentId;

  const EquipmentDetailsScreen({
    super.key,
    required this.equipmentId,
  });

  @override
  ConsumerState<EquipmentDetailsScreen> createState() =>
      _EquipmentDetailsScreenState();
}

class _EquipmentDetailsScreenState
    extends ConsumerState<EquipmentDetailsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final equipmentAsync = ref.watch(equipmentDetailsProvider(widget.equipmentId));

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      body: equipmentAsync.when(
        data: (equipment) => _buildContent(context, equipment),
        loading: () => const Center(
          child: CircularProgressIndicator(color: SahoolColors.forestGreen),
        ),
        error: (error, _) => Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Icon(Icons.error_outline, size: 48, color: SahoolColors.danger),
              const SizedBox(height: 16),
              Text(
                error.toString(),
                style: const TextStyle(color: SahoolColors.danger),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () =>
                    ref.invalidate(equipmentDetailsProvider(widget.equipmentId)),
                icon: const Icon(Icons.refresh),
                label: const Text('إعادة المحاولة'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, Equipment equipment) {
    return NestedScrollView(
      headerSliverBuilder: (context, innerBoxIsScrolled) {
        return [
          // App Bar
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            backgroundColor: SahoolColors.forestGreen,
            foregroundColor: Colors.white,
            flexibleSpace: FlexibleSpaceBar(
              background: _buildHeader(equipment),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.qr_code),
                onPressed: () => _showQRCode(context, equipment),
                tooltip: 'عرض QR',
              ),
              PopupMenuButton<String>(
                onSelected: (value) => _handleMenuAction(value, equipment),
                itemBuilder: (context) => [
                  const PopupMenuItem(
                    value: 'edit',
                    child: ListTile(
                      leading: Icon(Icons.edit),
                      title: Text('تعديل'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'location',
                    child: ListTile(
                      leading: Icon(Icons.location_on),
                      title: Text('تحديث الموقع'),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'delete',
                    child: ListTile(
                      leading: Icon(Icons.delete, color: Colors.red),
                      title: Text('حذف', style: TextStyle(color: Colors.red)),
                      contentPadding: EdgeInsets.zero,
                    ),
                  ),
                ],
              ),
            ],
            bottom: TabBar(
              controller: _tabController,
              indicatorColor: Colors.white,
              labelColor: Colors.white,
              unselectedLabelColor: Colors.white70,
              tabs: const [
                Tab(text: 'نظرة عامة', icon: Icon(Icons.dashboard, size: 20)),
                Tab(text: 'صيانة', icon: Icon(Icons.build, size: 20)),
                Tab(text: 'وقود', icon: Icon(Icons.local_gas_station, size: 20)),
                Tab(text: 'استخدام', icon: Icon(Icons.timer, size: 20)),
              ],
            ),
          ),
        ];
      },
      body: TabBarView(
        controller: _tabController,
        children: [
          _OverviewTab(equipment: equipment),
          _MaintenanceTab(equipmentId: equipment.equipmentId),
          _FuelTab(equipmentId: equipment.equipmentId),
          _UsageTab(equipmentId: equipment.equipmentId),
        ],
      ),
    );
  }

  Widget _buildHeader(Equipment equipment) {
    return DecoratedBox(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [SahoolColors.forestGreen, Color(0xFF1E3D2F)],
        ),
      ),
      child: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.end,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: Colors.white.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Icon(
                      _getEquipmentIcon(equipment.equipmentType),
                      color: Colors.white,
                      size: 30,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          equipment.getDisplayName('ar'),
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${equipment.equipmentType.nameAr} ${equipment.brand != null ? "• ${equipment.brand}" : ""}',
                          style: TextStyle(
                            color: Colors.white.withValues(alpha: 0.8),
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
                  StatusIndicator(
                    status: equipment.status,
                    size: 14,
                    showLabel: true,
                    animated: true,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getEquipmentIcon(EquipmentType type) {
    switch (type) {
      case EquipmentType.tractor:
        return Icons.agriculture;
      case EquipmentType.pump:
        return Icons.water;
      case EquipmentType.drone:
        return Icons.flight;
      case EquipmentType.harvester:
        return Icons.grass;
      case EquipmentType.sprayer:
        return Icons.shower;
      case EquipmentType.pivot:
        return Icons.rotate_right;
      case EquipmentType.sensor:
        return Icons.sensors;
      case EquipmentType.vehicle:
        return Icons.local_shipping;
      case EquipmentType.iotDevice:
        return Icons.router;
      case EquipmentType.other:
        return Icons.build;
    }
  }

  void _showQRCode(BuildContext context, Equipment equipment) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'رمز QR للمعدة',
              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
            ),
            const SizedBox(height: 24),
            Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(Icons.qr_code_2, size: 150),
            ),
            const SizedBox(height: 16),
            Text(
              equipment.qrCode ?? equipment.equipmentId,
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
            const SizedBox(height: 24),
          ],
        ),
      ),
    );
  }

  void _handleMenuAction(String action, Equipment equipment) {
    switch (action) {
      case 'edit':
        // Navigate to edit screen
        break;
      case 'location':
        // Update location
        break;
      case 'delete':
        _confirmDelete(context, equipment);
        break;
    }
  }

  void _confirmDelete(BuildContext context, Equipment equipment) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تأكيد الحذف'),
        content: Text(
            'هل أنت متأكد من حذف "${equipment.getDisplayName('ar')}"؟\nهذا الإجراء لا يمكن التراجع عنه.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          TextButton(
            onPressed: () async {
              Navigator.pop(context);
              final controller = ref.read(equipmentControllerProvider.notifier);
              await controller.deleteEquipment(equipment.equipmentId);
              if (mounted) Navigator.pop(context);
            },
            style: TextButton.styleFrom(foregroundColor: SahoolColors.danger),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }
}

/// Overview Tab
class _OverviewTab extends StatelessWidget {
  final Equipment equipment;

  const _OverviewTab({required this.equipment});

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Quick Stats
        Row(
          children: [
            if (equipment.currentFuelPercent != null)
              Expanded(
                child: OrganicCard(
                  child: FuelGauge(
                    fuelPercent: equipment.currentFuelPercent!,
                    size: 100,
                    capacity: equipment.fuelCapacityLiters,
                  ),
                ),
              ),
            if (equipment.currentFuelPercent != null) const SizedBox(width: 12),
            Expanded(
              child: OrganicCard(
                child: HoursCounter(
                  hours: equipment.currentHours ?? 0,
                  maxHours: equipment.nextMaintenanceHours,
                  showProgress: equipment.nextMaintenanceHours != null,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 16),

        // Equipment Details
        OrganicCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                'معلومات المعدة',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 16),
              _buildDetailRow('النوع', equipment.equipmentType.nameAr),
              _buildDetailRow('الماركة', equipment.brand ?? '-'),
              _buildDetailRow('الموديل', equipment.model ?? '-'),
              _buildDetailRow('الرقم التسلسلي', equipment.serialNumber ?? '-'),
              _buildDetailRow('سنة الصنع', equipment.year?.toString() ?? '-'),
              if (equipment.horsepower != null)
                _buildDetailRow('القوة', '${equipment.horsepower} حصان'),
              if (equipment.purchasePrice != null)
                _buildDetailRow(
                    'سعر الشراء', '${equipment.purchasePrice!.toStringAsFixed(0)} ريال'),
            ],
          ),
        ),
        const SizedBox(height: 16),

        // Location
        if (equipment.hasLocation || equipment.locationName != null)
          OrganicCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.location_on, color: SahoolColors.forestGreen),
                    SizedBox(width: 8),
                    Text(
                      'الموقع',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                Text(equipment.locationName ?? 'غير محدد'),
                if (equipment.hasLocation)
                  Text(
                    equipment.locationString,
                    style: TextStyle(color: Colors.grey[500], fontSize: 12),
                  ),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      // Navigate to map
                    },
                    icon: const Icon(Icons.map),
                    label: const Text('عرض على الخريطة'),
                  ),
                ),
              ],
            ),
          ),

        // Alerts
        if (equipment.needsMaintenanceSoon || equipment.isLowFuel) ...[
          const SizedBox(height: 16),
          OrganicCard(
            color: SahoolColors.harvestGold.withValues(alpha: 0.1),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Row(
                  children: [
                    Icon(Icons.warning_amber, color: SahoolColors.harvestGold),
                    SizedBox(width: 8),
                    Text(
                      'تنبيهات',
                      style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                if (equipment.needsMaintenanceSoon)
                  _buildAlertItem(
                    Icons.build,
                    'صيانة قادمة',
                    equipment.nextMaintenanceAt != null
                        ? 'موعد الصيانة: ${_formatDate(equipment.nextMaintenanceAt!)}'
                        : 'يقترب من موعد الصيانة',
                  ),
                if (equipment.isLowFuel)
                  _buildAlertItem(
                    Icons.local_gas_station,
                    'الوقود منخفض',
                    '${equipment.currentFuelPercent!.toInt()}% متبقي',
                  ),
              ],
            ),
          ),
        ],
        const SizedBox(height: 80),
      ],
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: TextStyle(color: Colors.grey[600]),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertItem(IconData icon, String title, String subtitle) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: SahoolColors.harvestGold, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                Text(
                  subtitle,
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

/// Maintenance Tab
class _MaintenanceTab extends ConsumerWidget {
  final String equipmentId;

  const _MaintenanceTab({required this.equipmentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(equipmentMaintenanceHistoryProvider(equipmentId));

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(equipmentMaintenanceHistoryProvider(equipmentId));
      },
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Schedule maintenance button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) =>
                        ScheduleMaintenanceScreen(equipmentId: equipmentId),
                  ),
                );
              },
              icon: const Icon(Icons.add),
              label: const Text('جدولة صيانة جديدة'),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.harvestGold,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Maintenance history
          historyAsync.when(
            data: (records) => MaintenanceTimeline(
              records: records,
              maxItems: 20,
            ),
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, _) => Center(
              child: Text(error.toString()),
            ),
          ),
        ],
      ),
    );
  }
}

/// Fuel Tab
class _FuelTab extends ConsumerWidget {
  final String equipmentId;

  const _FuelTab({required this.equipmentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final fuelLogsAsync = ref.watch(equipmentFuelLogsSimpleProvider(equipmentId));

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(equipmentFuelLogsSimpleProvider(equipmentId));
      },
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Add fuel log button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) =>
                        FuelLogScreen(equipmentId: equipmentId),
                  ),
                );
              },
              icon: const Icon(Icons.add),
              label: const Text('تسجيل تعبئة وقود'),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.forestGreen,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Fuel logs
          fuelLogsAsync.when(
            data: (logs) {
              if (logs.isEmpty) {
                return Center(
                  child: Padding(
                    padding: const EdgeInsets.all(32),
                    child: Column(
                      children: [
                        Icon(Icons.local_gas_station,
                            size: 48, color: Colors.grey[300]),
                        const SizedBox(height: 16),
                        Text(
                          'لا يوجد سجل وقود',
                          style: TextStyle(color: Colors.grey[500]),
                        ),
                      ],
                    ),
                  ),
                );
              }

              return Column(
                children: logs.map((log) {
                  return Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      children: [
                        const Icon(
                          Icons.local_gas_station,
                          color: SahoolColors.forestGreen,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                log.formattedQuantity,
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                '${log.timestamp.day}/${log.timestamp.month}/${log.timestamp.year}',
                                style: TextStyle(
                                  color: Colors.grey[500],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                        Text(
                          log.formattedCost,
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      ],
                    ),
                  );
                }).toList(),
              );
            },
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(32),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (error, _) => Center(child: Text(error.toString())),
          ),
        ],
      ),
    );
  }
}

/// Usage Tab
class _UsageTab extends ConsumerWidget {
  final String equipmentId;

  const _UsageTab({required this.equipmentId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final usageLogsAsync = ref.watch(equipmentUsageLogsSimpleProvider(equipmentId));
    final usageSummaryAsync = ref.watch(equipmentUsageSummaryProvider(equipmentId));

    return RefreshIndicator(
      onRefresh: () async {
        ref.invalidate(equipmentUsageLogsSimpleProvider(equipmentId));
        ref.invalidate(equipmentUsageSummaryProvider(equipmentId));
      },
      child: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Usage summary
          usageSummaryAsync.when(
            data: (summary) => UsageSummaryCard(summary: summary),
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 24),

          // Usage chart
          usageSummaryAsync.when(
            data: (summary) {
              if (summary.dailyBreakdown != null &&
                  summary.dailyBreakdown!.isNotEmpty) {
                return OrganicCard(
                  child: UsageHoursChart(
                    dailyUsage: summary.dailyBreakdown!,
                  ),
                );
              }
              return const SizedBox.shrink();
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 24),

          // Activity distribution
          usageSummaryAsync.when(
            data: (summary) {
              if (summary.hoursByActivity.isNotEmpty) {
                return OrganicCard(
                  child: ActivityDistributionChart(
                    hoursByActivity: summary.hoursByActivity,
                  ),
                );
              }
              return const SizedBox.shrink();
            },
            loading: () => const SizedBox.shrink(),
            error: (_, __) => const SizedBox.shrink(),
          ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}
