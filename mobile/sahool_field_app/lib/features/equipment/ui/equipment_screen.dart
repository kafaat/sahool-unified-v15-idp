import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة إدارة المعدات والأصول الزراعية
/// مستوحاة من تصميم John Deere Operations Center
class EquipmentScreen extends StatefulWidget {
  const EquipmentScreen({super.key});

  @override
  State<EquipmentScreen> createState() => _EquipmentScreenState();
}

class _EquipmentScreenState extends State<EquipmentScreen> {
  String _selectedCategory = 'all';

  @override
  Widget build(BuildContext context) {
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
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // 1. ملخص الحالة (Dashboard Row)
          Row(
            children: [
              Expanded(
                child: _StatusBox(
                  icon: Icons.agriculture,
                  count: "5",
                  label: "معدات",
                  color: SahoolColors.forestGreen,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatusBox(
                  icon: Icons.check_circle,
                  count: "3",
                  label: "جاهزة",
                  color: Colors.green,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatusBox(
                  icon: Icons.build,
                  count: "2",
                  label: "صيانة",
                  color: SahoolColors.harvestGold,
                ),
              ),
            ],
          ),

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

          _EquipmentItem(
            name: "John Deere 8R 410",
            type: "جرار زراعي",
            status: EquipmentStatus.operational,
            location: "الحقل الشمالي",
            fuelLevel: 75,
            hoursUsed: 1250,
            imageAsset: Icons.agriculture,
            onTap: () => _showEquipmentDetails(context),
          ),
          const SizedBox(height: 16),
          _EquipmentItem(
            name: "DJI Agras T40",
            type: "طائرة رش زراعية",
            status: EquipmentStatus.maintenance,
            location: "الورشة",
            fuelLevel: 100,
            hoursUsed: 320,
            imageAsset: Icons.flight,
            onTap: () => _showEquipmentDetails(context),
          ),
          const SizedBox(height: 16),
          _EquipmentItem(
            name: "مضخة غاطسة Grundfos",
            type: "نظام ري",
            status: EquipmentStatus.operational,
            location: "البئر رقم 1",
            fuelLevel: null,
            hoursUsed: 8500,
            imageAsset: Icons.water,
            onTap: () => _showEquipmentDetails(context),
          ),
          const SizedBox(height: 16),
          _EquipmentItem(
            name: "حاصدة New Holland",
            type: "آلة حصاد",
            status: EquipmentStatus.inactive,
            location: "المخزن",
            fuelLevel: 40,
            hoursUsed: 890,
            imageAsset: Icons.grass,
            onTap: () => _showEquipmentDetails(context),
          ),
          const SizedBox(height: 16),
          _EquipmentItem(
            name: "رشاش محوري Valley",
            type: "نظام ري محوري",
            status: EquipmentStatus.operational,
            location: "الحقل الجنوبي",
            fuelLevel: null,
            hoursUsed: 15000,
            imageAsset: Icons.rotate_right,
            onTap: () => _showEquipmentDetails(context),
          ),

          const SizedBox(height: 24),

          // 4. تنبيهات الصيانة
          _buildMaintenanceAlerts(),

          const SizedBox(height: 80),
        ],
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
            isSelected: _selectedCategory == 'all',
            onTap: () => setState(() => _selectedCategory = 'all'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "جرارات",
            icon: Icons.agriculture,
            isSelected: _selectedCategory == 'tractors',
            onTap: () => setState(() => _selectedCategory = 'tractors'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "ري",
            icon: Icons.water,
            isSelected: _selectedCategory == 'irrigation',
            onTap: () => setState(() => _selectedCategory = 'irrigation'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "درونز",
            icon: Icons.flight,
            isSelected: _selectedCategory == 'drones',
            onTap: () => setState(() => _selectedCategory = 'drones'),
          ),
          const SizedBox(width: 8),
          _CategoryChip(
            label: "حصاد",
            icon: Icons.grass,
            isSelected: _selectedCategory == 'harvest',
            onTap: () => setState(() => _selectedCategory = 'harvest'),
          ),
        ],
      ),
    );
  }

  Widget _buildMaintenanceAlerts() {
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
              const Text(
                "تنبيهات الصيانة",
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          _MaintenanceAlert(
            equipment: "John Deere 8R",
            alert: "تغيير زيت المحرك",
            dueIn: "بعد 50 ساعة",
            priority: "متوسط",
          ),
          const Divider(height: 24),
          _MaintenanceAlert(
            equipment: "DJI Agras T40",
            alert: "فحص البطارية",
            dueIn: "متأخر 2 يوم",
            priority: "عالي",
          ),
        ],
      ),
    );
  }

  void _showEquipmentDetails(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
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
                  child: const Icon(
                    Icons.agriculture,
                    size: 40,
                    color: SahoolColors.forestGreen,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "John Deere 8R 410",
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const Text(
                        "جرار زراعي • 410 حصان",
                        style: TextStyle(color: Colors.grey),
                      ),
                      const SizedBox(height: 8),
                      StatusBadge(
                        label: "جاهز للعمل",
                        color: SahoolColors.forestGreen,
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
                Expanded(
                  child: _StatBox(
                    icon: Icons.local_gas_station,
                    value: "75%",
                    label: "الوقود",
                    color: Colors.orange,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _StatBox(
                    icon: Icons.timer,
                    value: "1,250",
                    label: "ساعات التشغيل",
                    color: Colors.blue,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _StatBox(
                    icon: Icons.speed,
                    value: "12",
                    label: "كم/س",
                    color: Colors.green,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Location
            OrganicCard(
              color: SahoolColors.paleOlive.withOpacity(0.5),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: SahoolColors.forestGreen),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          "الموقع الحالي",
                          style: TextStyle(color: Colors.grey, fontSize: 12),
                        ),
                        Text(
                          "الحقل الشمالي - القطاع C",
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                  TextButton(
                    onPressed: () {},
                    child: const Text("عرض على الخريطة"),
                  ),
                ],
              ),
            ),

            const Spacer(),

            // Actions
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () {},
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
                    onPressed: () {},
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
                    onPressed: () {},
                    icon: const Icon(Icons.play_arrow),
                    label: const Text("تشغيل"),
                    style: ElevatedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      backgroundColor: SahoolColors.forestGreen,
                      foregroundColor: Colors.white,
                    ),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showQrScanner(BuildContext context) {
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
      builder: (context) => Container(
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
            DropdownButtonFormField<String>(
              decoration: InputDecoration(
                labelText: "نوع المعدة",
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              items: const [
                DropdownMenuItem(value: 'tractor', child: Text('جرار')),
                DropdownMenuItem(value: 'pump', child: Text('مضخة')),
                DropdownMenuItem(value: 'drone', child: Text('درون')),
                DropdownMenuItem(value: 'harvester', child: Text('حاصدة')),
                DropdownMenuItem(value: 'sprayer', child: Text('رشاش')),
              ],
              onChanged: (value) {},
            ),
            const SizedBox(height: 16),
            TextField(
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
                onPressed: () => Navigator.pop(context),
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
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════

enum EquipmentStatus { operational, maintenance, inactive }

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
  final String name;
  final String type;
  final String location;
  final EquipmentStatus status;
  final IconData imageAsset;
  final int? fuelLevel;
  final int hoursUsed;
  final VoidCallback onTap;

  const _EquipmentItem({
    required this.name,
    required this.type,
    required this.location,
    required this.status,
    required this.imageAsset,
    required this.fuelLevel,
    required this.hoursUsed,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    String statusText;

    switch (status) {
      case EquipmentStatus.operational:
        statusColor = SahoolColors.forestGreen;
        statusText = "جاهز";
        break;
      case EquipmentStatus.maintenance:
        statusColor = SahoolColors.harvestGold;
        statusText = "صيانة";
        break;
      case EquipmentStatus.inactive:
        statusColor = Colors.grey;
        statusText = "متوقف";
        break;
    }

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
              child: Icon(imageAsset, size: 32, color: SahoolColors.forestGreen),
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
                          name,
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ),
                      StatusBadge(label: statusText, color: statusColor, isSmall: true),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    type,
                    style: const TextStyle(color: Colors.grey, fontSize: 13),
                  ),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.location_on, size: 14, color: Colors.grey[400]),
                      const SizedBox(width: 4),
                      Text(
                        location,
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                      const SizedBox(width: 16),
                      if (fuelLevel != null) ...[
                        Icon(
                          Icons.local_gas_station,
                          size: 14,
                          color: fuelLevel! > 30 ? Colors.green : Colors.orange,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          "$fuelLevel%",
                          style: TextStyle(
                            fontSize: 12,
                            color: fuelLevel! > 30 ? Colors.green : Colors.orange,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ],
                      const Spacer(),
                      Icon(Icons.timer, size: 14, color: Colors.grey[400]),
                      const SizedBox(width: 4),
                      Text(
                        "${hoursUsed}h",
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

class _MaintenanceAlert extends StatelessWidget {
  final String equipment;
  final String alert;
  final String dueIn;
  final String priority;

  const _MaintenanceAlert({
    required this.equipment,
    required this.alert,
    required this.dueIn,
    required this.priority,
  });

  @override
  Widget build(BuildContext context) {
    final isOverdue = dueIn.contains("متأخر");

    return Row(
      children: [
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                equipment,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                alert,
                style: const TextStyle(color: Colors.grey, fontSize: 13),
              ),
            ],
          ),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              dueIn,
              style: TextStyle(
                fontSize: 12,
                color: isOverdue ? SahoolColors.danger : Colors.grey,
                fontWeight: isOverdue ? FontWeight.bold : FontWeight.normal,
              ),
            ),
            const SizedBox(height: 4),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: isOverdue
                    ? SahoolColors.danger.withOpacity(0.1)
                    : SahoolColors.harvestGold.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                priority,
                style: TextStyle(
                  fontSize: 10,
                  color: isOverdue ? SahoolColors.danger : SahoolColors.harvestGold,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ],
    );
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
