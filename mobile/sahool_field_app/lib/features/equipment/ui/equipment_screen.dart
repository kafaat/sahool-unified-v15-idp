/// Equipment Screen - شاشة إدارة المعدات
/// متكاملة مع FastAPI Equipment Service
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../data/equipment_models.dart';
import '../providers/equipment_providers.dart';

/// شاشة إدارة المعدات والأصول الزراعية
/// مستوحاة من تصميم John Deere Operations Center
class EquipmentScreen extends ConsumerStatefulWidget {
  const EquipmentScreen({super.key});

  @override
  ConsumerState<EquipmentScreen> createState() => _EquipmentScreenState();
}

class _EquipmentScreenState extends ConsumerState<EquipmentScreen> {
  EquipmentType? _selectedType;

  @override
  Widget build(BuildContext context) {
    // Watch providers
    final filter = EquipmentFilter(type: _selectedType);
    final equipmentAsync = ref.watch(equipmentListProvider(filter));
    final statsAsync = ref.watch(equipmentStatsProvider);
    final alertsAsync = ref.watch(maintenanceAlertsProvider(false));

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: const Text("المعدات والأصول"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.qr_code_scanner),
            onPressed: () => _showQrScanner(context),
            tooltip: "مسح QR",
          ),
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddEquipment(context),
            tooltip: "إضافة معدة",
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.invalidate(equipmentListProvider);
          ref.invalidate(equipmentStatsProvider);
          ref.invalidate(maintenanceAlertsProvider);
        },
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            // 1. ملخص الحالة (Dashboard Row)
            _buildStatsRow(statsAsync),

            const SizedBox(height: 24),

            // 2. فلاتر الفئات
            _buildCategoryFilters(),

            const SizedBox(height: 24),

            // 3. قائمة المعدات
            const Text(
              "أسطول المعدات",
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 18,
                color: SahoolColors.forestGreen,
              ),
            ),
            const SizedBox(height: 16),

            // Equipment List
            _buildEquipmentList(equipmentAsync),

            const SizedBox(height: 24),

            // 4. تنبيهات الصيانة
            _buildMaintenanceAlerts(alertsAsync),

            const SizedBox(height: 80),
          ],
        ),
      ),
    );
  }

  Widget _buildStatsRow(AsyncValue<EquipmentStats> statsAsync) {
    return statsAsync.when(
      data: (stats) => Row(
        children: [
          Expanded(
            child: _StatusBox(
              icon: Icons.agriculture,
              count: stats.total.toString(),
              label: "معدات",
              color: SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _StatusBox(
              icon: Icons.check_circle,
              count: stats.operational.toString(),
              label: "جاهزة",
              color: Colors.green,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _StatusBox(
              icon: Icons.build,
              count: stats.maintenance.toString(),
              label: "صيانة",
              color: SahoolColors.harvestGold,
            ),
          ),
        ],
      ),
      loading: () => Row(
        children: [
          Expanded(child: _StatusBox(icon: Icons.agriculture, count: "-", label: "معدات", color: SahoolColors.forestGreen)),
          const SizedBox(width: 12),
          Expanded(child: _StatusBox(icon: Icons.check_circle, count: "-", label: "جاهزة", color: Colors.green)),
          const SizedBox(width: 12),
          Expanded(child: _StatusBox(icon: Icons.build, count: "-", label: "صيانة", color: SahoolColors.harvestGold)),
        ],
      ),
      error: (error, _) => Center(
        child: Text('خطأ في تحميل الإحصائيات', style: TextStyle(color: SahoolColors.danger)),
      ),
    );
  }

  Widget _buildCategoryFilters() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _CategoryChip(
            label: "الكل",
            icon: Icons.apps,
            isSelected: _selectedType == null,
            onTap: () => setState(() => _selectedType = null),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "جرارات",
            icon: Icons.agriculture,
            isSelected: _selectedType == EquipmentType.tractor,
            onTap: () => setState(() => _selectedType = EquipmentType.tractor),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "مضخات",
            icon: Icons.water,
            isSelected: _selectedType == EquipmentType.pump,
            onTap: () => setState(() => _selectedType = EquipmentType.pump),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "درونز",
            icon: Icons.flight,
            isSelected: _selectedType == EquipmentType.drone,
            onTap: () => setState(() => _selectedType = EquipmentType.drone),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "حاصدات",
            icon: Icons.grass,
            isSelected: _selectedType == EquipmentType.harvester,
            onTap: () => setState(() => _selectedType = EquipmentType.harvester),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "رشاشات",
            icon: Icons.rotate_right,
            isSelected: _selectedType == EquipmentType.pivot,
            onTap: () => setState(() => _selectedType = EquipmentType.pivot),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "حساسات",
            icon: Icons.sensors,
            isSelected: _selectedType == EquipmentType.sensor,
            onTap: () => setState(() => _selectedType = EquipmentType.sensor),
          ),
        ],
      ),
    );
  }

  Widget _buildEquipmentList(AsyncValue<List<Equipment>> equipmentAsync) {
    return equipmentAsync.when(
      data: (equipmentList) {
        if (equipmentList.isEmpty) {
          return Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                children: [
                  Icon(Icons.agriculture, size: 64, color: Colors.grey[300]),
                  const SizedBox(height: 16),
                  Text(
                    'لا توجد معدات',
                    style: TextStyle(color: Colors.grey[500], fontSize: 16),
                  ),
                ],
              ),
            ),
          );
        }

        return Column(
          children: equipmentList.map((equipment) {
            return Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: _EquipmentItem(
                equipment: equipment,
                onTap: () => _showEquipmentDetails(context, equipment),
              ),
            );
          }).toList(),
        );
      },
      loading: () => const Center(
        child: Padding(
          padding: EdgeInsets.all(32),
          child: CircularProgressIndicator(color: SahoolColors.forestGreen),
        ),
      ),
      error: (error, _) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            children: [
              Icon(Icons.error_outline, size: 48, color: SahoolColors.danger),
              const SizedBox(height: 16),
              Text(
                error.toString(),
                style: TextStyle(color: SahoolColors.danger),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 16),
              ElevatedButton.icon(
                onPressed: () => ref.invalidate(equipmentListProvider),
                icon: const Icon(Icons.refresh),
                label: const Text('إعادة المحاولة'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.forestGreen,
                  foregroundColor: Colors.white,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMaintenanceAlerts(AsyncValue<List<MaintenanceAlert>> alertsAsync) {
    return alertsAsync.when(
      data: (alerts) {
        if (alerts.isEmpty) {
          return const SizedBox.shrink();
        }

        return OrganicCard(
          color: SahoolColors.harvestGold.withOpacity(0.1),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: SahoolColors.harvestGold.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.warning_amber,
                      color: SahoolColors.harvestGold,
                      size: 20,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    "تنبيهات الصيانة (${alerts.length})",
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              ...alerts.take(5).map((alert) {
                final isLast = alert == alerts.take(5).last;
                return Column(
                  children: [
                    _MaintenanceAlertWidget(alert: alert),
                    if (!isLast) const Divider(height: 24),
                  ],
                );
              }),
            ],
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
    );
  }

  void _showEquipmentDetails(BuildContext context, Equipment equipment) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _EquipmentDetailsSheet(equipment: equipment),
    );
  }

  void _showQrScanner(BuildContext context) {
    // TODO: Integrate with mobile_scanner package
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text("سيتم فتح ماسح QR لتحديد المعدة"),
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _showAddEquipment(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => const _AddEquipmentSheet(),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Details Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════

class _EquipmentDetailsSheet extends ConsumerWidget {
  final Equipment equipment;

  const _EquipmentDetailsSheet({required this.equipment});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Header
          Row(
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: SahoolColors.paleOlive,
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Icon(
                  _getEquipmentIcon(equipment.equipmentType),
                  size: 40,
                  color: SahoolColors.forestGreen,
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
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      "${equipment.equipmentType.nameAr} • ${equipment.horsepower ?? '-'} حصان",
                      style: const TextStyle(color: Colors.grey),
                    ),
                    const SizedBox(height: 8),
                    StatusBadge(
                      label: equipment.status.nameAr,
                      color: _getStatusColor(equipment.status),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Stats Grid
          Row(
            children: [
              if (equipment.currentFuelPercent != null)
                Expanded(
                  child: _StatBox(
                    icon: Icons.local_gas_station,
                    value: "${equipment.currentFuelPercent!.toInt()}%",
                    label: "الوقود",
                    color: equipment.isLowFuel ? Colors.orange : Colors.green,
                  ),
                ),
              if (equipment.currentFuelPercent != null) const SizedBox(width: 12),
              Expanded(
                child: _StatBox(
                  icon: Icons.timer,
                  value: equipment.currentHours?.toStringAsFixed(0) ?? '-',
                  label: "ساعات التشغيل",
                  color: Colors.blue,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatBox(
                  icon: Icons.calendar_today,
                  value: equipment.year?.toString() ?? '-',
                  label: "سنة الصنع",
                  color: Colors.purple,
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),

          // Location
          if (equipment.locationName != null || equipment.currentLat != null)
            OrganicCard(
              color: SahoolColors.paleOlive.withOpacity(0.5),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: SahoolColors.forestGreen),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "الموقع الحالي",
                          style: TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        Text(
                          equipment.locationName ?? 'غير محدد',
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        if (equipment.currentLat != null && equipment.currentLon != null)
                          Text(
                            '${equipment.currentLat!.toStringAsFixed(4)}, ${equipment.currentLon!.toStringAsFixed(4)}',
                            style: const TextStyle(fontSize: 11, color: Colors.grey),
                          ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () {
                      // TODO: Navigate to map
                    },
                    child: const Text("عرض على الخريطة"),
                  ),
                ],
              ),
            ),

          // Maintenance Info
          if (equipment.needsMaintenanceSoon) ...[
            const SizedBox(height: 16),
            OrganicCard(
              color: SahoolColors.harvestGold.withOpacity(0.1),
              child: Row(
                children: [
                  const Icon(Icons.warning_amber, color: SahoolColors.harvestGold),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          "صيانة قادمة",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        if (equipment.nextMaintenanceAt != null)
                          Text(
                            'موعد الصيانة: ${_formatDate(equipment.nextMaintenanceAt!)}',
                            style: const TextStyle(fontSize: 12, color: Colors.grey),
                          ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],

          const Spacer(),

          // Actions
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    // TODO: Show history
                  },
                  icon: const Icon(Icons.history),
                  label: const Text("السجل"),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    side: const BorderSide(color: SahoolColors.forestGreen),
                    foregroundColor: SahoolColors.forestGreen,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: () {
                    Navigator.pop(context);
                    _showAddMaintenanceRecord(context, ref, equipment.equipmentId);
                  },
                  icon: const Icon(Icons.build),
                  label: const Text("صيانة"),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    side: const BorderSide(color: SahoolColors.harvestGold),
                    foregroundColor: SahoolColors.harvestGold,
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () async {
                    final controller = ref.read(equipmentControllerProvider.notifier);
                    final newStatus = equipment.status == EquipmentStatus.operational
                        ? EquipmentStatus.inactive
                        : EquipmentStatus.operational;
                    await controller.updateStatus(equipment.equipmentId, newStatus);
                    if (context.mounted) Navigator.pop(context);
                  },
                  icon: Icon(equipment.status == EquipmentStatus.operational
                      ? Icons.stop
                      : Icons.play_arrow),
                  label: Text(equipment.status == EquipmentStatus.operational
                      ? "إيقاف"
                      : "تشغيل"),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: equipment.status == EquipmentStatus.operational
                        ? Colors.red
                        : SahoolColors.forestGreen,
                    foregroundColor: Colors.white,
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _showAddMaintenanceRecord(BuildContext context, WidgetRef ref, String equipmentId) {
    // TODO: Implement maintenance record form
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('نموذج إضافة سجل الصيانة')),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Add Equipment Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════

class _AddEquipmentSheet extends ConsumerStatefulWidget {
  const _AddEquipmentSheet();

  @override
  ConsumerState<_AddEquipmentSheet> createState() => _AddEquipmentSheetState();
}

class _AddEquipmentSheetState extends ConsumerState<_AddEquipmentSheet> {
  final _nameController = TextEditingController();
  final _serialController = TextEditingController();
  EquipmentType _selectedType = EquipmentType.tractor;

  @override
  void dispose() {
    _nameController.dispose();
    _serialController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.7,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            "إضافة معدة جديدة",
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 24),
          TextField(
            controller: _nameController,
            decoration: InputDecoration(
              labelText: "اسم المعدة",
              hintText: "مثال: John Deere 8R",
              filled: true,
              fillColor: Colors.grey[100],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const SizedBox(height: 16),
          DropdownButtonFormField<EquipmentType>(
            value: _selectedType,
            decoration: InputDecoration(
              labelText: "نوع المعدة",
              filled: true,
              fillColor: Colors.grey[100],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
            items: EquipmentType.values.map((type) {
              return DropdownMenuItem(
                value: type,
                child: Text(type.nameAr),
              );
            }).toList(),
            onChanged: (value) {
              if (value != null) {
                setState(() => _selectedType = value);
              }
            },
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _serialController,
            decoration: InputDecoration(
              labelText: "الرقم التسلسلي",
              filled: true,
              fillColor: Colors.grey[100],
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: BorderSide.none,
              ),
            ),
          ),
          const Spacer(),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () async {
                if (_nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('الرجاء إدخال اسم المعدة')),
                  );
                  return;
                }

                // TODO: Call repository to create equipment
                Navigator.pop(context);
                ref.invalidate(equipmentListProvider);
                ref.invalidate(equipmentStatsProvider);
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: SahoolColors.forestGreen,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: const Text("إضافة المعدة", style: TextStyle(fontSize: 16)),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════

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
    case EquipmentType.other:
      return Icons.build;
  }
}

Color _getStatusColor(EquipmentStatus status) {
  switch (status) {
    case EquipmentStatus.operational:
      return SahoolColors.forestGreen;
    case EquipmentStatus.maintenance:
      return SahoolColors.harvestGold;
    case EquipmentStatus.inactive:
      return Colors.grey;
    case EquipmentStatus.repair:
      return SahoolColors.danger;
  }
}

class _StatusBox extends StatelessWidget {
  final IconData icon;
  final String count;
  final String label;
  final Color color;

  const _StatusBox({
    required this.icon,
    required this.count,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(
            count,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 20),
          ),
          Text(
            label,
            style: const TextStyle(fontSize: 12, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

class _CategoryChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _CategoryChip({
    required this.label,
    required this.icon,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: isSelected ? SahoolColors.forestGreen : Colors.white,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isSelected ? SahoolColors.forestGreen : Colors.grey.withOpacity(0.3),
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              size: 16,
              color: isSelected ? Colors.white : Colors.grey,
            ),
            const SizedBox(width: 6),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? Colors.white : Colors.grey[700],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _EquipmentItem extends StatelessWidget {
  final Equipment equipment;
  final VoidCallback onTap;

  const _EquipmentItem({
    required this.equipment,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final statusColor = _getStatusColor(equipment.status);

    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            // أيقونة/صورة المعدة
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: SahoolColors.paleOlive.withOpacity(0.5),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(
                _getEquipmentIcon(equipment.equipmentType),
                size: 32,
                color: SahoolColors.forestGreen,
              ),
            ),
            const SizedBox(width: 16),

            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          equipment.getDisplayName('ar'),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ),
                      StatusBadge(
                        label: equipment.status.nameAr,
                        color: statusColor,
                        isSmall: true,
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    equipment.equipmentType.nameAr,
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.location_on, size: 14, color: Colors.grey[400]),
                      const SizedBox(width: 4),
                      Text(
                        equipment.locationName ?? 'غير محدد',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const SizedBox(width: 16),
                      if (equipment.currentFuelPercent != null) ...[
                        Icon(
                          Icons.local_gas_station,
                          size: 14,
                          color: equipment.isLowFuel ? Colors.orange : Colors.green,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          "${equipment.currentFuelPercent!.toInt()}%",
                          style: TextStyle(
                            fontSize: 12,
                            color: equipment.isLowFuel ? Colors.orange : Colors.green,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                      const Spacer(),
                      Icon(Icons.timer, size: 14, color: Colors.grey[400]),
                      const SizedBox(width: 4),
                      Text(
                        "${equipment.currentHours?.toStringAsFixed(0) ?? '-'}h",
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(width: 8),
            const Icon(Icons.chevron_right, color: Colors.grey),
          ],
        ),
      ),
    );
  }
}

class _MaintenanceAlertWidget extends StatelessWidget {
  final MaintenanceAlert alert;

  const _MaintenanceAlertWidget({required this.alert});

  @override
  Widget build(BuildContext context) {
    final priorityColor = _getPriorityColor(alert.priority);

    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                alert.equipmentName,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                alert.getDescription('ar'),
                style: const TextStyle(color: Colors.grey, fontSize: 13),
              ),
            ],
          ),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            if (alert.dueAt != null)
              Text(
                alert.isOverdue
                    ? "متأخر ${DateTime.now().difference(alert.dueAt!).inDays} يوم"
                    : "بعد ${alert.dueAt!.difference(DateTime.now()).inDays} يوم",
                style: TextStyle(
                  fontSize: 12,
                  color: alert.isOverdue ? SahoolColors.danger : Colors.grey,
                  fontWeight: alert.isOverdue ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: priorityColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                alert.priority.nameAr,
                style: TextStyle(
                  fontSize: 10,
                  color: priorityColor,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Color _getPriorityColor(MaintenancePriority priority) {
    switch (priority) {
      case MaintenancePriority.low:
        return Colors.green;
      case MaintenancePriority.medium:
        return SahoolColors.harvestGold;
      case MaintenancePriority.high:
        return Colors.orange;
      case MaintenancePriority.critical:
        return SahoolColors.danger;
    }
  }
}

class _StatBox extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color color;

  const _StatBox({
    required this.icon,
    required this.value,
    required this.label,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 18,
              color: color,
            ),
          ),
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}
