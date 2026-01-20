/// Equipment Screen - شاشة إدارة المعدات
/// متكاملة مع FastAPI Equipment Service
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../../../core/widgets/barcode_scanner_widget.dart';
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

  void _showQrScanner(BuildContext context) async {
    final result = await BarcodeScannerScreen.scan(
      context,
      title: 'مسح رمز المعدة',
      subtitle: 'وجّه الكاميرا نحو رمز QR أو الباركود الموجود على المعدة',
    );

    if (result != null && context.mounted) {
      // البحث عن المعدة بالرمز الممسوح
      final equipmentId = result.value;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('تم المسح: $equipmentId'),
          backgroundColor: SahoolColors.forestGreen,
          behavior: SnackBarBehavior.floating,
          action: SnackBarAction(
            label: 'عرض',
            textColor: Colors.white,
            onPressed: () {
              // يمكن إضافة منطق عرض تفاصيل المعدة هنا
            },
          ),
        ),
      );
    }
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
                      if (equipment.currentLat != null && equipment.currentLon != null) {
                        Navigator.pop(context);
                        _showEquipmentLocationMap(context, equipment);
                      } else {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('موقع المعدة غير متوفر'),
                            backgroundColor: Colors.orange,
                          ),
                        );
                      }
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
                    Navigator.pop(context);
                    _showEquipmentHistory(context, equipment);
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
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _AddMaintenanceRecordSheet(equipmentId: equipmentId),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  void _showEquipmentLocationMap(BuildContext context, Equipment equipment) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _EquipmentLocationMapSheet(equipment: equipment),
    );
  }

  void _showEquipmentHistory(BuildContext context, Equipment equipment) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _EquipmentHistorySheet(equipment: equipment),
    );
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
  bool _isSubmitting = false;

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
              onPressed: _isSubmitting ? null : () async {
                if (_nameController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('الرجاء إدخال اسم المعدة'),
                      backgroundColor: Colors.orange,
                    ),
                  );
                  return;
                }

                setState(() => _isSubmitting = true);

                try {
                  final controller = ref.read(equipmentControllerProvider.notifier);
                  final success = await controller.createEquipment(
                    name: _nameController.text,
                    nameAr: _nameController.text,
                    type: _selectedType,
                    serialNumber: _serialController.text.isNotEmpty
                        ? _serialController.text
                        : null,
                  );

                  if (mounted) {
                    if (success) {
                      Navigator.pop(context);
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('تم إضافة المعدة بنجاح'),
                          backgroundColor: Colors.green,
                        ),
                      );
                    } else {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text('فشل في إضافة المعدة'),
                          backgroundColor: Colors.red,
                        ),
                      );
                    }
                  }
                } catch (e) {
                  if (mounted) {
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('حدث خطأ: $e'),
                        backgroundColor: Colors.red,
                      ),
                    );
                  }
                } finally {
                  if (mounted) {
                    setState(() => _isSubmitting = false);
                  }
                }
              },
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
                backgroundColor: SahoolColors.forestGreen,
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isSubmitting
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Text("إضافة المعدة", style: TextStyle(fontSize: 16)),
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

// ═══════════════════════════════════════════════════════════════════════════
// Add Maintenance Record Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════

class _AddMaintenanceRecordSheet extends ConsumerStatefulWidget {
  final String equipmentId;

  const _AddMaintenanceRecordSheet({required this.equipmentId});

  @override
  ConsumerState<_AddMaintenanceRecordSheet> createState() =>
      _AddMaintenanceRecordSheetState();
}

class _AddMaintenanceRecordSheetState
    extends ConsumerState<_AddMaintenanceRecordSheet> {
  final _descriptionController = TextEditingController();
  final _costController = TextEditingController();
  final _notesController = TextEditingController();
  final _technicianController = TextEditingController();

  MaintenanceType _selectedType = MaintenanceType.generalService;
  DateTime _maintenanceDate = DateTime.now();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _descriptionController.dispose();
    _costController.dispose();
    _notesController.dispose();
    _technicianController.dispose();
    super.dispose();
  }

  Future<void> _selectDate() async {
    final picked = await showDatePicker(
      context: context,
      initialDate: _maintenanceDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
      locale: const Locale('ar'),
    );
    if (picked != null) {
      setState(() => _maintenanceDate = picked);
    }
  }

  Future<void> _submitRecord() async {
    if (_descriptionController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('الرجاء إدخال وصف الصيانة'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final controller = ref.read(equipmentControllerProvider.notifier);
      // Build description with notes if provided
      final fullDescription = _notesController.text.isNotEmpty
          ? '${_descriptionController.text}\n\nملاحظات: ${_notesController.text}'
          : _descriptionController.text;

      await controller.addMaintenanceRecord(
        widget.equipmentId,
        maintenanceType: _selectedType,
        description: fullDescription,
        descriptionAr: _descriptionController.text,
        performedBy: _technicianController.text.isNotEmpty
            ? _technicianController.text
            : null,
        cost: double.tryParse(_costController.text),
      );

      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم إضافة سجل الصيانة بنجاح'),
            backgroundColor: Colors.green,
          ),
        );
        ref.invalidate(equipmentListProvider);
        ref.invalidate(maintenanceAlertsProvider);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('حدث خطأ: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSubmitting = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: MediaQuery.of(context).size.height * 0.85,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Handle
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: SahoolColors.harvestGold.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.build,
                    color: SahoolColors.harvestGold,
                  ),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "إضافة سجل صيانة",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 20,
                        ),
                      ),
                      Text(
                        "تسجيل عملية صيانة جديدة",
                        style: TextStyle(color: Colors.grey, fontSize: 14),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),

          const Divider(height: 32),

          // Form
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // نوع الصيانة
                  const Text(
                    "نوع الصيانة",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: MaintenanceType.values.map((type) {
                      final isSelected = _selectedType == type;
                      return ChoiceChip(
                        label: Text(type.nameAr),
                        selected: isSelected,
                        onSelected: (selected) {
                          if (selected) {
                            setState(() => _selectedType = type);
                          }
                        },
                        selectedColor: SahoolColors.harvestGold.withOpacity(0.2),
                        labelStyle: TextStyle(
                          color: isSelected
                              ? SahoolColors.harvestGold
                              : Colors.grey[700],
                          fontWeight:
                              isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      );
                    }).toList(),
                  ),

                  const SizedBox(height: 24),

                  // تاريخ الصيانة
                  const Text(
                    "تاريخ الصيانة",
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                  ),
                  const SizedBox(height: 12),
                  InkWell(
                    onTap: _selectDate,
                    borderRadius: BorderRadius.circular(12),
                    child: Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        border: Border.all(color: Colors.grey[300]!),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.calendar_today,
                              color: SahoolColors.forestGreen),
                          const SizedBox(width: 12),
                          Text(
                            "${_maintenanceDate.day}/${_maintenanceDate.month}/${_maintenanceDate.year}",
                            style: const TextStyle(fontSize: 16),
                          ),
                          const Spacer(),
                          const Icon(Icons.arrow_drop_down, color: Colors.grey),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // وصف الصيانة
                  TextFormField(
                    controller: _descriptionController,
                    maxLines: 2,
                    decoration: InputDecoration(
                      labelText: "وصف الصيانة *",
                      hintText: "مثال: تغيير زيت المحرك وفلتر الهواء",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      prefixIcon: const Icon(Icons.description),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // اسم الفني
                  TextFormField(
                    controller: _technicianController,
                    decoration: InputDecoration(
                      labelText: "اسم الفني",
                      hintText: "اسم فني الصيانة",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      prefixIcon: const Icon(Icons.person),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // التكلفة
                  TextFormField(
                    controller: _costController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: "التكلفة (ريال)",
                      hintText: "0.00",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      prefixIcon: const Icon(Icons.attach_money),
                    ),
                  ),

                  const SizedBox(height: 16),

                  // ملاحظات إضافية
                  TextFormField(
                    controller: _notesController,
                    maxLines: 3,
                    decoration: InputDecoration(
                      labelText: "ملاحظات إضافية",
                      hintText: "أي ملاحظات أخرى...",
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                      prefixIcon: const Icon(Icons.note),
                    ),
                  ),

                  const SizedBox(height: 32),
                ],
              ),
            ),
          ),

          // Submit Button
          Padding(
            padding: const EdgeInsets.all(24),
            child: SizedBox(
              width: double.infinity,
              height: 56,
              child: ElevatedButton.icon(
                onPressed: _isSubmitting ? null : _submitRecord,
                icon: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.save),
                label: Text(
                  _isSubmitting ? "جاري الحفظ..." : "حفظ سجل الصيانة",
                  style: const TextStyle(fontSize: 16),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.harvestGold,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Equipment Location Map Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════

class _EquipmentLocationMapSheet extends StatelessWidget {
  final Equipment equipment;

  const _EquipmentLocationMapSheet({required this.equipment});

  @override
  Widget build(BuildContext context) {
    final lat = equipment.currentLat ?? 0.0;
    final lon = equipment.currentLon ?? 0.0;
    final location = LatLng(lat, lon);

    return Container(
      height: MediaQuery.of(context).size.height * 0.75,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Handle
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: SahoolColors.forestGreen.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.location_on,
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
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      Text(
                        equipment.locationName ?? 'موقع المعدة',
                        style: const TextStyle(color: Colors.grey, fontSize: 14),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),

          const Divider(height: 24),

          // Map
          Expanded(
            child: ClipRRect(
              borderRadius: const BorderRadius.only(
                bottomLeft: Radius.circular(24),
                bottomRight: Radius.circular(24),
              ),
              child: FlutterMap(
                options: MapOptions(
                  initialCenter: location,
                  initialZoom: 15,
                ),
                children: [
                  TileLayer(
                    urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                    userAgentPackageName: 'com.sahool.field',
                    maxZoom: 19,
                  ),
                  MarkerLayer(
                    markers: [
                      Marker(
                        point: location,
                        width: 80,
                        height: 80,
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: SahoolColors.forestGreen,
                                borderRadius: BorderRadius.circular(12),
                                boxShadow: [
                                  BoxShadow(
                                    color: SahoolColors.forestGreen.withOpacity(0.4),
                                    blurRadius: 8,
                                    spreadRadius: 2,
                                  ),
                                ],
                              ),
                              child: Icon(
                                _getEquipmentIcon(equipment.equipmentType),
                                color: Colors.white,
                                size: 24,
                              ),
                            ),
                            CustomPaint(
                              size: const Size(16, 8),
                              painter: _MapMarkerTrianglePainter(
                                color: SahoolColors.forestGreen,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),

          // Coordinates Info
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.grey[50],
              borderRadius: const BorderRadius.vertical(
                bottom: Radius.circular(24),
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.gps_fixed, size: 16, color: Colors.grey),
                const SizedBox(width: 8),
                Text(
                  '${lat.toStringAsFixed(6)}, ${lon.toStringAsFixed(6)}',
                  style: const TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 13,
                    color: Colors.grey,
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

/// Triangle painter for map marker
class _MapMarkerTrianglePainter extends CustomPainter {
  final Color color;

  _MapMarkerTrianglePainter({required this.color});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    final path = Path()
      ..moveTo(size.width / 2, size.height)
      ..lineTo(0, 0)
      ..lineTo(size.width, 0)
      ..close();

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _MapMarkerTrianglePainter oldDelegate) =>
      color != oldDelegate.color;
}

// ═══════════════════════════════════════════════════════════════════════════
// Equipment History Bottom Sheet
// ═══════════════════════════════════════════════════════════════════════════

class _EquipmentHistorySheet extends ConsumerWidget {
  final Equipment equipment;

  const _EquipmentHistorySheet({required this.equipment});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final historyAsync = ref.watch(maintenanceHistoryProvider(equipment.equipmentId));

    return Container(
      height: MediaQuery.of(context).size.height * 0.8,
      decoration: const BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      child: Column(
        children: [
          // Handle
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 12),
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          // Header
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: SahoolColors.forestGreen.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.history,
                    color: SahoolColors.forestGreen,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "سجل الصيانة والاستخدام",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      Text(
                        equipment.getDisplayName('ar'),
                        style: const TextStyle(color: Colors.grey, fontSize: 14),
                      ),
                    ],
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
          ),

          const Divider(height: 24),

          // Content
          Expanded(
            child: historyAsync.when(
              data: (records) {
                if (records.isEmpty) {
                  return _buildEmptyState();
                }
                return _buildHistoryList(records);
              },
              loading: () => const Center(
                child: CircularProgressIndicator(
                  color: SahoolColors.forestGreen,
                ),
              ),
              error: (error, _) => _buildErrorState(error, ref),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.history,
              size: 64,
              color: Colors.grey[300],
            ),
            const SizedBox(height: 16),
            Text(
              'لا يوجد سجل صيانة',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'سيظهر هنا سجل الصيانة والاستخدام للمعدة',
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[500],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(Object error, WidgetRef ref) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.error_outline,
              size: 48,
              color: SahoolColors.danger,
            ),
            const SizedBox(height: 16),
            Text(
              'حدث خطأ في جلب السجل',
              style: TextStyle(
                fontSize: 16,
                color: Colors.grey[700],
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () => ref.invalidate(
                maintenanceHistoryProvider(equipment.equipmentId),
              ),
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
    );
  }

  Widget _buildHistoryList(List<MaintenanceRecord> records) {
    return ListView.separated(
      padding: const EdgeInsets.fromLTRB(24, 0, 24, 24),
      itemCount: records.length,
      separatorBuilder: (context, index) => const SizedBox(height: 12),
      itemBuilder: (context, index) {
        final record = records[index];
        return _HistoryRecordItem(record: record);
      },
    );
  }
}

class _HistoryRecordItem extends StatelessWidget {
  final MaintenanceRecord record;

  const _HistoryRecordItem({required this.record});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Row
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _getMaintenanceTypeColor(record.maintenanceType).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getMaintenanceTypeIcon(record.maintenanceType),
                  size: 20,
                  color: _getMaintenanceTypeColor(record.maintenanceType),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      record.maintenanceType.nameAr,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 15,
                      ),
                    ),
                    Text(
                      _formatDate(record.performedAt),
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              if (record.cost != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: SahoolColors.harvestGold.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${record.cost!.toStringAsFixed(0)} ريال',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: SahoolColors.harvestGold,
                    ),
                  ),
                ),
            ],
          ),

          // Description
          if (record.getDescription('ar').isNotEmpty) ...[
            const SizedBox(height: 12),
            Text(
              record.getDescription('ar'),
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[700],
              ),
            ),
          ],

          // Performed By
          if (record.performedBy != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.person_outline, size: 14, color: Colors.grey[500]),
                const SizedBox(width: 4),
                Text(
                  record.performedBy!,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ],

          // Parts Replaced
          if (record.partsReplaced != null && record.partsReplaced!.isNotEmpty) ...[
            const SizedBox(height: 8),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: record.partsReplaced!.map((part) {
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    part,
                    style: const TextStyle(
                      fontSize: 11,
                      color: Colors.blue,
                    ),
                  ),
                );
              }).toList(),
            ),
          ],
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  Color _getMaintenanceTypeColor(MaintenanceType type) {
    switch (type) {
      case MaintenanceType.oilChange:
        return Colors.amber;
      case MaintenanceType.filterChange:
        return Colors.blue;
      case MaintenanceType.tireCheck:
        return Colors.grey;
      case MaintenanceType.batteryCheck:
        return Colors.green;
      case MaintenanceType.calibration:
        return Colors.purple;
      case MaintenanceType.generalService:
        return SahoolColors.forestGreen;
      case MaintenanceType.repair:
        return SahoolColors.danger;
      case MaintenanceType.other:
        return Colors.grey;
    }
  }

  IconData _getMaintenanceTypeIcon(MaintenanceType type) {
    switch (type) {
      case MaintenanceType.oilChange:
        return Icons.oil_barrel;
      case MaintenanceType.filterChange:
        return Icons.filter_alt;
      case MaintenanceType.tireCheck:
        return Icons.tire_repair;
      case MaintenanceType.batteryCheck:
        return Icons.battery_charging_full;
      case MaintenanceType.calibration:
        return Icons.tune;
      case MaintenanceType.generalService:
        return Icons.build;
      case MaintenanceType.repair:
        return Icons.handyman;
      case MaintenanceType.other:
        return Icons.more_horiz;
    }
  }
}
