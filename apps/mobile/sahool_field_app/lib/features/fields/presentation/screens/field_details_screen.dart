import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/field_entity.dart';

/// شاشة تفاصيل الحقل
/// Field Details Screen
class FieldDetailsScreen extends ConsumerStatefulWidget {
  final FieldEntity field;

  const FieldDetailsScreen({super.key, required this.field});

  @override
  ConsumerState<FieldDetailsScreen> createState() => _FieldDetailsScreenState();
}

class _FieldDetailsScreenState extends ConsumerState<FieldDetailsScreen>
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
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: NestedScrollView(
          headerSliverBuilder: (context, innerBoxIsScrolled) => [
            _buildSliverAppBar(),
          ],
          body: TabBarView(
            controller: _tabController,
            children: [
              _buildOverviewTab(),
              _buildHealthTab(),
              _buildTasksTab(),
              _buildHistoryTab(),
            ],
          ),
        ),
        floatingActionButton: _buildSpeedDial(),
      ),
    );
  }

  Widget _buildSliverAppBar() {
    return SliverAppBar(
      expandedHeight: 280,
      pinned: true,
      backgroundColor: const Color(0xFF367C2B),
      foregroundColor: Colors.white,
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: const BoxDecoration(
            gradient: LinearGradient(
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
              colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
            ),
          ),
          child: SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(16, 60, 16, 16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Field header
                  Row(
                    children: [
                      Container(
                        width: 70,
                        height: 70,
                        decoration: BoxDecoration(
                          color: Colors.white.withOpacity(0.2),
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: Center(
                          child: Text(
                            widget.field.cropEmoji,
                            style: const TextStyle(fontSize: 40),
                          ),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              widget.field.name,
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 22,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 4),
                            Row(
                              children: [
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.white.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    widget.field.cropType,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: _getStatusColor(widget.field.status)
                                        .withOpacity(0.3),
                                    borderRadius: BorderRadius.circular(12),
                                  ),
                                  child: Text(
                                    widget.field.status.arabicLabel,
                                    style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 12,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 20),

                  // Quick stats
                  Row(
                    children: [
                      _buildQuickStat(
                        icon: Icons.square_foot,
                        value: '${widget.field.areaHectares.toStringAsFixed(1)}',
                        label: 'هكتار',
                      ),
                      const SizedBox(width: 24),
                      _buildQuickStat(
                        icon: Icons.grass,
                        value: widget.field.ndviValue?.toStringAsFixed(2) ?? '-',
                        label: 'NDVI',
                      ),
                      const SizedBox(width: 24),
                      _buildQuickStat(
                        icon: Icons.favorite,
                        value: '${(widget.field.healthScore * 100).round()}%',
                        label: 'الصحة',
                      ),
                      const SizedBox(width: 24),
                      _buildQuickStat(
                        icon: Icons.water_drop,
                        value: widget.field.ndwiValue?.toStringAsFixed(2) ?? '-',
                        label: 'NDWI',
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
      bottom: TabBar(
        controller: _tabController,
        indicatorColor: Colors.white,
        labelColor: Colors.white,
        unselectedLabelColor: Colors.white70,
        tabs: const [
          Tab(text: 'نظرة عامة', icon: Icon(Icons.dashboard, size: 20)),
          Tab(text: 'الصحة', icon: Icon(Icons.eco, size: 20)),
          Tab(text: 'المهام', icon: Icon(Icons.task, size: 20)),
          Tab(text: 'السجل', icon: Icon(Icons.history, size: 20)),
        ],
      ),
      actions: [
        IconButton(
          icon: const Icon(Icons.map),
          onPressed: () => _openMap(),
          tooltip: 'الخريطة',
        ),
        PopupMenuButton<String>(
          icon: const Icon(Icons.more_vert),
          onSelected: _handleMenuAction,
          itemBuilder: (context) => [
            const PopupMenuItem(value: 'edit', child: Text('تعديل')),
            const PopupMenuItem(value: 'share', child: Text('مشاركة')),
            const PopupMenuItem(value: 'export', child: Text('تصدير')),
            const PopupMenuItem(
              value: 'delete',
              child: Text('حذف', style: TextStyle(color: Colors.red)),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildQuickStat({
    required IconData icon,
    required String value,
    required String label,
  }) {
    return Column(
      children: [
        Icon(icon, color: Colors.white.withOpacity(0.8), size: 20),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            color: Colors.white.withOpacity(0.7),
            fontSize: 11,
          ),
        ),
      ],
    );
  }

  Widget _buildOverviewTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Info cards
          _buildSectionTitle('معلومات الحقل'),
          _buildInfoCard(),

          const SizedBox(height: 24),

          // Growth progress
          if (widget.field.plantingDate != null) ...[
            _buildSectionTitle('تقدم النمو'),
            _buildGrowthProgressCard(),
            const SizedBox(height: 24),
          ],

          // Weather summary
          _buildSectionTitle('ملخص الطقس'),
          _buildWeatherCard(),

          const SizedBox(height: 24),

          // Recent activity
          _buildSectionTitle('النشاط الأخير'),
          _buildRecentActivity(),

          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 18,
          fontWeight: FontWeight.bold,
          color: Color(0xFF367C2B),
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildInfoRow(Icons.landscape, 'نوع التربة', widget.field.soilType ?? 'غير محدد'),
            const Divider(),
            _buildInfoRow(Icons.water_drop, 'نظام الري', widget.field.irrigationType ?? 'غير محدد'),
            if (widget.field.lastIrrigation != null) ...[
              const Divider(),
              _buildInfoRow(
                Icons.schedule,
                'آخر ري',
                _formatDate(widget.field.lastIrrigation!),
              ),
            ],
            if (widget.field.plantingDate != null) ...[
              const Divider(),
              _buildInfoRow(
                Icons.eco,
                'تاريخ الزراعة',
                _formatDate(widget.field.plantingDate!),
              ),
            ],
            if (widget.field.expectedHarvest != null) ...[
              const Divider(),
              _buildInfoRow(
                Icons.agriculture,
                'موعد الحصاد المتوقع',
                _formatDate(widget.field.expectedHarvest!),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: const Color(0xFF367C2B), size: 22),
          const SizedBox(width: 12),
          Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const Spacer(),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
        ],
      ),
    );
  }

  Widget _buildGrowthProgressCard() {
    final daysSincePlanting = widget.field.daysSincePlanting ?? 0;
    final daysUntilHarvest = widget.field.daysUntilHarvest ?? 0;
    final totalDays = daysSincePlanting + daysUntilHarvest;
    final progress = totalDays > 0 ? daysSincePlanting / totalDays : 0.0;

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('منذ الزراعة'),
                    Text(
                      '$daysSincePlanting يوم',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                        color: Color(0xFF367C2B),
                      ),
                    ),
                  ],
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    const Text('حتى الحصاد'),
                    Text(
                      '$daysUntilHarvest يوم',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 20,
                        color: Colors.orange,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            const SizedBox(height: 16),
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.grey[200],
                valueColor: const AlwaysStoppedAnimation(Color(0xFF367C2B)),
                minHeight: 12,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '${(progress * 100).round()}% من دورة النمو',
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildWeatherCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.wb_sunny, color: Colors.orange, size: 48),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '28°C',
                    style: TextStyle(
                      fontSize: 28,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  Text(
                    'مشمس جزئياً',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Row(
                  children: [
                    const Icon(Icons.water_drop, size: 16, color: Colors.blue),
                    const SizedBox(width: 4),
                    Text('45%', style: TextStyle(color: Colors.grey[600])),
                  ],
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.air, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text('12 كم/س', style: TextStyle(color: Colors.grey[600])),
                  ],
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildActivityItem(
            icon: Icons.water_drop,
            color: Colors.blue,
            title: 'تم الري',
            subtitle: 'ري بالمحور - 45 دقيقة',
            time: 'منذ ساعتين',
          ),
          const Divider(height: 1),
          _buildActivityItem(
            icon: Icons.eco,
            color: Colors.green,
            title: 'قياس NDVI',
            subtitle: 'القيمة: 0.72',
            time: 'أمس',
          ),
          const Divider(height: 1),
          _buildActivityItem(
            icon: Icons.task_alt,
            color: Colors.orange,
            title: 'مهمة مكتملة',
            subtitle: 'تفقد الآفات',
            time: 'منذ يومين',
          ),
        ],
      ),
    );
  }

  Widget _buildActivityItem({
    required IconData icon,
    required Color color,
    required String title,
    required String subtitle,
    required String time,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text(subtitle),
      trailing: Text(
        time,
        style: TextStyle(color: Colors.grey[500], fontSize: 12),
      ),
    );
  }

  Widget _buildHealthTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Health score card
          _buildHealthScoreCard(),
          const SizedBox(height: 24),

          // Indices
          _buildSectionTitle('المؤشرات'),
          _buildIndicesCard(),
          const SizedBox(height: 24),

          // Recommendations
          _buildSectionTitle('التوصيات'),
          _buildRecommendationsCard(),

          const SizedBox(height: 80),
        ],
      ),
    );
  }

  Widget _buildHealthScoreCard() {
    final healthColor = _getHealthColor(widget.field.healthScore);

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            SizedBox(
              width: 150,
              height: 150,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 150,
                    height: 150,
                    child: CircularProgressIndicator(
                      value: widget.field.healthScore,
                      strokeWidth: 12,
                      backgroundColor: Colors.grey[200],
                      valueColor: AlwaysStoppedAnimation(healthColor),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${(widget.field.healthScore * 100).round()}%',
                        style: TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: healthColor,
                        ),
                      ),
                      Text(
                        widget.field.healthLabel,
                        style: TextStyle(
                          color: healthColor,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildIndicesCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildIndexRow('NDVI', widget.field.ndviValue ?? 0, Colors.green),
            const Divider(),
            _buildIndexRow('NDWI', widget.field.ndwiValue ?? 0, Colors.blue),
            const Divider(),
            _buildIndexRow('NDRE', 0.28, Colors.orange),
          ],
        ),
      ),
    );
  }

  Widget _buildIndexRow(String name, double value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Text(
            name,
            style: const TextStyle(fontWeight: FontWeight.w600),
          ),
          const Spacer(),
          SizedBox(
            width: 120,
            child: LinearProgressIndicator(
              value: (value + 1) / 2, // Normalize -1 to 1 range
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation(color),
              minHeight: 8,
              borderRadius: BorderRadius.circular(4),
            ),
          ),
          const SizedBox(width: 12),
          Text(
            value.toStringAsFixed(2),
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationsCard() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildRecommendationItem(
            icon: Icons.water_drop,
            color: Colors.blue,
            title: 'زيادة الري',
            description: 'قيمة NDWI منخفضة، يُنصح بزيادة معدل الري',
            priority: 'متوسط',
          ),
          const Divider(height: 1),
          _buildRecommendationItem(
            icon: Icons.eco,
            color: Colors.green,
            title: 'تسميد نيتروجيني',
            description: 'لتحسين مؤشر NDVI',
            priority: 'منخفض',
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationItem({
    required IconData icon,
    required Color color,
    required String title,
    required String description,
    required String priority,
  }) {
    return ListTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: color, size: 20),
      ),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text(description, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      trailing: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.orange.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Text(
          priority,
          style: const TextStyle(fontSize: 10, color: Colors.orange),
        ),
      ),
    );
  }

  Widget _buildTasksTab() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.task_alt, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            'لا توجد مهام حالياً',
            style: TextStyle(fontSize: 18, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          ElevatedButton.icon(
            onPressed: () {},
            icon: const Icon(Icons.add),
            label: const Text('إضافة مهمة'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF367C2B),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHistoryTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: 10,
      itemBuilder: (context, index) {
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: CircleAvatar(
              backgroundColor: const Color(0xFF367C2B).withOpacity(0.1),
              child: const Icon(Icons.history, color: Color(0xFF367C2B)),
            ),
            title: Text('نشاط ${10 - index}'),
            subtitle: Text('منذ ${index + 1} أيام'),
            trailing: const Icon(Icons.chevron_left),
          ),
        );
      },
    );
  }

  Widget _buildSpeedDial() {
    return FloatingActionButton.extended(
      onPressed: () => _showQuickActions(),
      backgroundColor: const Color(0xFF367C2B),
      icon: const Icon(Icons.flash_on),
      label: const Text('إجراء سريع'),
    );
  }

  void _showQuickActions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Padding(
                padding: EdgeInsets.all(16),
                child: Text(
                  'إجراءات سريعة',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.blue,
                  child: Icon(Icons.water_drop, color: Colors.white),
                ),
                title: const Text('تسجيل ري'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.green,
                  child: Icon(Icons.eco, color: Colors.white),
                ),
                title: const Text('تسجيل تسميد'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.orange,
                  child: Icon(Icons.camera_alt, color: Colors.white),
                ),
                title: const Text('التقاط صورة'),
                onTap: () => Navigator.pop(context),
              ),
              ListTile(
                leading: const CircleAvatar(
                  backgroundColor: Colors.purple,
                  child: Icon(Icons.note_add, color: Colors.white),
                ),
                title: const Text('إضافة ملاحظة'),
                onTap: () => Navigator.pop(context),
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  void _openMap() {
    Navigator.pushNamed(context, '/map', arguments: {'fieldId': widget.field.id});
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'edit':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تعديل الحقل - قريباً')),
        );
        break;
      case 'share':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('مشاركة - قريباً')),
        );
        break;
      case 'export':
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('تصدير - قريباً')),
        );
        break;
      case 'delete':
        _showDeleteConfirmation();
        break;
    }
  }

  void _showDeleteConfirmation() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف الحقل'),
        content: Text('هل أنت متأكد من حذف "${widget.field.name}"؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pop(context);
            },
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }

  Color _getHealthColor(double score) {
    if (score >= 0.8) return const Color(0xFF2E7D32);
    if (score >= 0.6) return const Color(0xFF4CAF50);
    if (score >= 0.4) return Colors.orange;
    return Colors.red;
  }

  Color _getStatusColor(FieldStatus status) {
    switch (status) {
      case FieldStatus.active:
        return Colors.green;
      case FieldStatus.fallow:
        return Colors.grey;
      case FieldStatus.preparing:
        return Colors.blue;
      case FieldStatus.harvested:
        return Colors.orange;
      case FieldStatus.inactive:
        return Colors.red;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
