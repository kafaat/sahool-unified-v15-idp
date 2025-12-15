import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة إدارة المهام والعمليات الزراعية
/// تصميم Kanban مبسط مع تقسيم "اليوم" و "القادم"
class TasksScreen extends StatefulWidget {
  const TasksScreen({super.key});

  @override
  State<TasksScreen> createState() => _TasksScreenState();
}

class _TasksScreenState extends State<TasksScreen> {
  String _selectedFilter = 'all';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      appBar: AppBar(
        title: const Text("المهام والعمليات"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.forestGreen,
        elevation: 0,
        actions: [
          PopupMenuButton<String>(
            icon: const Icon(Icons.filter_list),
            onSelected: (value) => setState(() => _selectedFilter = value),
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'all', child: Text('جميع المهام')),
              const PopupMenuItem(value: 'pending', child: Text('قيد الانتظار')),
              const PopupMenuItem(value: 'completed', child: Text('مكتملة')),
              const PopupMenuItem(value: 'high', child: Text('أولوية عالية')),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 1. ملخص الإنجاز (Header Card)
            _buildProgressCard(context),

            const SizedBox(height: 24),

            // 2. فلاتر سريعة
            _buildQuickFilters(),

            const SizedBox(height: 24),

            // 3. مهام اليوم (Today's Tasks)
            _buildSectionHeader("مهام اليوم", Icons.today),
            const SizedBox(height: 12),
            _TaskCard(
              title: "ري الحقل الشمالي",
              subtitle: "القطاع C • مضخة رقم 2",
              time: "08:00 ص",
              priority: TaskPriority.high,
              taskType: TaskType.irrigation,
              isCompleted: false,
              onToggle: () {},
              onTap: () => _showTaskDetails(context),
            ),
            const SizedBox(height: 12),
            _TaskCard(
              title: "فحص الحشرات",
              subtitle: "مزرعة الطماطم • فحص وقائي",
              time: "10:30 ص",
              priority: TaskPriority.medium,
              taskType: TaskType.scouting,
              isCompleted: true,
              onToggle: () {},
              onTap: () => _showTaskDetails(context),
            ),
            const SizedBox(height: 12),
            _TaskCard(
              title: "جمع عينات التربة",
              subtitle: "الحقل الجنوبي • تحليل المغذيات",
              time: "02:00 م",
              priority: TaskPriority.medium,
              taskType: TaskType.sampling,
              isCompleted: false,
              onToggle: () {},
              onTap: () => _showTaskDetails(context),
            ),

            const SizedBox(height: 24),

            // 4. المهام القادمة (Upcoming)
            _buildSectionHeader("غداً والقادم", Icons.upcoming),
            const SizedBox(height: 12),
            _TaskCard(
              title: "تسميد التربة (NPK)",
              subtitle: "الحقل الجنوبي • 50 كجم/هكتار",
              time: "غداً",
              priority: TaskPriority.low,
              taskType: TaskType.fertilization,
              isCompleted: false,
              onToggle: () {},
              onTap: () => _showTaskDetails(context),
            ),
            const SizedBox(height: 12),
            _TaskCard(
              title: "صيانة نظام الري",
              subtitle: "فحص الفلاتر والصمامات",
              time: "بعد غد",
              priority: TaskPriority.medium,
              taskType: TaskType.maintenance,
              isCompleted: false,
              onToggle: () {},
              onTap: () => _showTaskDetails(context),
            ),
            const SizedBox(height: 12),
            _TaskCard(
              title: "رش مبيد فطري",
              subtitle: "الحقل الشرقي • وقائي",
              time: "الخميس",
              priority: TaskPriority.high,
              taskType: TaskType.spraying,
              isCompleted: false,
              onToggle: () {},
              onTap: () => _showTaskDetails(context),
            ),

            const SizedBox(height: 100), // Space for FAB
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _showAddTaskSheet(context),
        backgroundColor: SahoolColors.forestGreen,
        icon: const Icon(Icons.add_task, color: Colors.white),
        label: const Text("مهمة جديدة", style: TextStyle(color: Colors.white)),
      ),
    );
  }

  Widget _buildProgressCard(BuildContext context) {
    return SizedBox(
      height: 140,
      child: OrganicCard(
        color: SahoolColors.forestGreen,
        isPrimary: true,
        child: Row(
          children: [
            Expanded(
              flex: 3,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text(
                    "إنجاز الأسبوع",
                    style: TextStyle(color: Colors.white.withOpacity(0.8)),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    "12 / 15",
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    "مهمة مكتملة",
                    style: TextStyle(color: Colors.white.withOpacity(0.9)),
                  ),
                ],
              ),
            ),
            Expanded(
              flex: 2,
              child: Center(
                child: SizedBox(
                  width: 80,
                  height: 80,
                  child: Stack(
                    alignment: Alignment.center,
                    children: [
                      SizedBox(
                        width: 80,
                        height: 80,
                        child: CircularProgressIndicator(
                          value: 0.8,
                          strokeWidth: 8,
                          backgroundColor: Colors.white.withOpacity(0.2),
                          valueColor: const AlwaysStoppedAnimation(
                            SahoolColors.harvestGold,
                          ),
                        ),
                      ),
                      Text(
                        "80%",
                        style: Theme.of(context).textTheme.titleLarge?.copyWith(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickFilters() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _FilterChip(
            label: "الكل",
            icon: Icons.list,
            isSelected: _selectedFilter == 'all',
            onTap: () => setState(() => _selectedFilter = 'all'),
          ),
          const SizedBox(width: 8),
          _FilterChip(
            label: "ري",
            icon: Icons.water_drop,
            isSelected: _selectedFilter == 'irrigation',
            onTap: () => setState(() => _selectedFilter = 'irrigation'),
          ),
          const SizedBox(width: 8),
          _FilterChip(
            label: "تسميد",
            icon: Icons.eco,
            isSelected: _selectedFilter == 'fertilization',
            onTap: () => setState(() => _selectedFilter = 'fertilization'),
          ),
          const SizedBox(width: 8),
          _FilterChip(
            label: "رش",
            icon: Icons.blur_on,
            isSelected: _selectedFilter == 'spraying',
            onTap: () => setState(() => _selectedFilter = 'spraying'),
          ),
          const SizedBox(width: 8),
          _FilterChip(
            label: "صيانة",
            icon: Icons.build,
            isSelected: _selectedFilter == 'maintenance',
            onTap: () => setState(() => _selectedFilter = 'maintenance'),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, IconData icon) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Row(
          children: [
            Icon(icon, size: 20, color: SahoolColors.forestGreen),
            const SizedBox(width: 8),
            Text(
              title,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: SahoolColors.forestGreen,
              ),
            ),
          ],
        ),
        TextButton(
          onPressed: () {},
          child: const Text("عرض الكل"),
        ),
      ],
    );
  }

  void _showTaskDetails(BuildContext context) {
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
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.water_drop,
                    color: Colors.blue,
                    size: 28,
                  ),
                ),
                const SizedBox(width: 16),
                const Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "ري الحقل الشمالي",
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        "القطاع C • مضخة رقم 2",
                        style: TextStyle(color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 24),
            _DetailRow(icon: Icons.schedule, label: "الوقت", value: "08:00 ص - 10:00 ص"),
            _DetailRow(icon: Icons.person, label: "المسؤول", value: "أحمد محمد"),
            _DetailRow(icon: Icons.location_on, label: "الموقع", value: "الحقل الشمالي - القطاع C"),
            _DetailRow(icon: Icons.water, label: "كمية المياه", value: "500 م³"),
            const Spacer(),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.edit),
                    label: const Text("تعديل"),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      side: const BorderSide(color: SahoolColors.forestGreen),
                      foregroundColor: SahoolColors.forestGreen,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () => Navigator.pop(context),
                    icon: const Icon(Icons.check),
                    label: const Text("إكمال"),
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

  void _showAddTaskSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.85,
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
              "مهمة جديدة",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            TextField(
              decoration: InputDecoration(
                labelText: "عنوان المهمة",
                hintText: "مثال: ري الحقل الشمالي",
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
                labelText: "نوع المهمة",
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              items: const [
                DropdownMenuItem(value: 'irrigation', child: Text('ري')),
                DropdownMenuItem(value: 'fertilization', child: Text('تسميد')),
                DropdownMenuItem(value: 'spraying', child: Text('رش')),
                DropdownMenuItem(value: 'scouting', child: Text('كشف ميداني')),
                DropdownMenuItem(value: 'maintenance', child: Text('صيانة')),
                DropdownMenuItem(value: 'harvest', child: Text('حصاد')),
              ],
              onChanged: (value) {},
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              decoration: InputDecoration(
                labelText: "الحقل",
                filled: true,
                fillColor: Colors.grey[100],
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                  borderSide: BorderSide.none,
                ),
              ),
              items: const [
                DropdownMenuItem(value: 'north', child: Text('الحقل الشمالي')),
                DropdownMenuItem(value: 'south', child: Text('الحقل الجنوبي')),
                DropdownMenuItem(value: 'east', child: Text('الحقل الشرقي')),
              ],
              onChanged: (value) {},
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      labelText: "التاريخ",
                      hintText: "اختر التاريخ",
                      filled: true,
                      fillColor: Colors.grey[100],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      suffixIcon: const Icon(Icons.calendar_today),
                    ),
                    readOnly: true,
                    onTap: () {},
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    decoration: InputDecoration(
                      labelText: "الوقت",
                      hintText: "اختر الوقت",
                      filled: true,
                      fillColor: Colors.grey[100],
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide.none,
                      ),
                      suffixIcon: const Icon(Icons.access_time),
                    ),
                    readOnly: true,
                    onTap: () {},
                  ),
                ),
              ],
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
                child: const Text("إضافة المهمة", style: TextStyle(fontSize: 16)),
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

enum TaskPriority { high, medium, low }
enum TaskType { irrigation, fertilization, spraying, scouting, maintenance, sampling, harvest }

class _FilterChip extends StatelessWidget {
  final String label;
  final IconData icon;
  final bool isSelected;
  final VoidCallback onTap;

  const _FilterChip({
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

class _TaskCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final String time;
  final TaskPriority priority;
  final TaskType taskType;
  final bool isCompleted;
  final VoidCallback onToggle;
  final VoidCallback onTap;

  const _TaskCard({
    required this.title,
    required this.subtitle,
    required this.time,
    required this.priority,
    required this.taskType,
    required this.isCompleted,
    required this.onToggle,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    Color priorityColor;
    switch (priority) {
      case TaskPriority.high:
        priorityColor = SahoolColors.danger;
        break;
      case TaskPriority.medium:
        priorityColor = SahoolColors.harvestGold;
        break;
      case TaskPriority.low:
        priorityColor = SahoolColors.info;
        break;
    }

    IconData typeIcon;
    Color typeColor;
    switch (taskType) {
      case TaskType.irrigation:
        typeIcon = Icons.water_drop;
        typeColor = Colors.blue;
        break;
      case TaskType.fertilization:
        typeIcon = Icons.eco;
        typeColor = Colors.green;
        break;
      case TaskType.spraying:
        typeIcon = Icons.blur_on;
        typeColor = Colors.purple;
        break;
      case TaskType.scouting:
        typeIcon = Icons.search;
        typeColor = Colors.orange;
        break;
      case TaskType.maintenance:
        typeIcon = Icons.build;
        typeColor = Colors.grey;
        break;
      case TaskType.sampling:
        typeIcon = Icons.science;
        typeColor = Colors.teal;
        break;
      case TaskType.harvest:
        typeIcon = Icons.agriculture;
        typeColor = SahoolColors.harvestGold;
        break;
    }

    return GestureDetector(
      onTap: onTap,
      child: OrganicCard(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Row(
          children: [
            // Task Type Icon
            Container(
              width: 44,
              height: 44,
              decoration: BoxDecoration(
                color: typeColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(typeIcon, color: typeColor, size: 22),
            ),
            const SizedBox(width: 14),

            // Task Info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 15,
                      decoration: isCompleted ? TextDecoration.lineThrough : null,
                      color: isCompleted ? Colors.grey : Colors.black87,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
            ),

            // Time & Priority
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  time,
                  style: const TextStyle(
                    fontWeight: FontWeight.w600,
                    fontSize: 12,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 6),
                Container(
                  width: 10,
                  height: 10,
                  decoration: BoxDecoration(
                    color: priorityColor,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ),

            const SizedBox(width: 12),

            // Checkbox
            GestureDetector(
              onTap: onToggle,
              child: Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  color: isCompleted ? SahoolColors.forestGreen : Colors.transparent,
                  border: Border.all(
                    color: isCompleted ? SahoolColors.forestGreen : Colors.grey,
                    width: 2,
                  ),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: isCompleted
                    ? const Icon(Icons.check, size: 18, color: Colors.white)
                    : null,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 12),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey),
          const SizedBox(width: 12),
          Text(label, style: const TextStyle(color: Colors.grey)),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }
}
