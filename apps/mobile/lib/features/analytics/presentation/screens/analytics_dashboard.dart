import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// شاشة لوحة الإحصائيات والتحليلات
/// Analytics Dashboard Screen
class AnalyticsDashboard extends ConsumerStatefulWidget {
  const AnalyticsDashboard({super.key});

  @override
  ConsumerState<AnalyticsDashboard> createState() => _AnalyticsDashboardState();
}

class _AnalyticsDashboardState extends ConsumerState<AnalyticsDashboard>
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
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الإحصائيات'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: const [
              Tab(text: 'نظرة عامة', icon: Icon(Icons.dashboard)),
              Tab(text: 'الإنتاج', icon: Icon(Icons.agriculture)),
              Tab(text: 'التقارير', icon: Icon(Icons.assessment)),
            ],
          ),
        ),
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildOverviewTab(),
            _buildProductionTab(),
            _buildReportsTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewTab() {
    return RefreshIndicator(
      onRefresh: () async {},
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // بطاقات الإحصائيات السريعة
            _buildQuickStats(),
            const SizedBox(height: 24),

            // ملخص الحقول
            Text(
              'ملخص الحقول',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            _buildFieldsSummary(),
            const SizedBox(height: 24),

            // صحة المحاصيل
            Text(
              'صحة المحاصيل',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            _buildHealthOverview(),
            const SizedBox(height: 24),

            // المهام
            Text(
              'ملخص المهام',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            _buildTasksSummary(),
          ],
        ),
      ),
    );
  }

  Widget _buildQuickStats() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildStatCard(
          title: 'إجمالي الحقول',
          value: '12',
          icon: Icons.landscape,
          color: const Color(0xFF367C2B),
          trend: '+2',
          trendUp: true,
        ),
        _buildStatCard(
          title: 'المساحة الكلية',
          value: '450 هكتار',
          icon: Icons.square_foot,
          color: Colors.blue,
        ),
        _buildStatCard(
          title: 'المهام المعلقة',
          value: '8',
          icon: Icons.task_alt,
          color: Colors.orange,
          trend: '-3',
          trendUp: false,
        ),
        _buildStatCard(
          title: 'التنبيهات',
          value: '3',
          icon: Icons.warning,
          color: Colors.red,
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required String title,
    required String value,
    required IconData icon,
    required Color color,
    String? trend,
    bool? trendUp,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Icon(icon, color: color, size: 28),
                if (trend != null)
                  Container(
                    padding:
                        const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: (trendUp ?? false)
                          ? Colors.green.withOpacity(0.1)
                          : Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          (trendUp ?? false)
                              ? Icons.arrow_upward
                              : Icons.arrow_downward,
                          size: 12,
                          color: (trendUp ?? false) ? Colors.green : Colors.red,
                        ),
                        Text(
                          trend,
                          style: TextStyle(
                            fontSize: 11,
                            color:
                                (trendUp ?? false) ? Colors.green : Colors.red,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value,
                  style: TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
                Text(
                  title,
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFieldsSummary() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildFieldRow('حقل القمح الشمالي', '45 هكتار', 0.85, 'قمح'),
            const Divider(),
            _buildFieldRow('حقل الذرة الغربي', '60 هكتار', 0.72, 'ذرة'),
            const Divider(),
            _buildFieldRow('حقل الشعير', '35 هكتار', 0.45, 'شعير'),
            const Divider(),
            _buildFieldRow('حقل البرسيم', '50 هكتار', 0.90, 'برسيم'),
            const SizedBox(height: 12),
            TextButton.icon(
              onPressed: () {},
              icon: const Icon(Icons.visibility),
              label: const Text('عرض كل الحقول'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFieldRow(
      String name, String area, double health, String crop) {
    final healthColor = _getHealthColor(health);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF367C2B).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.grass, color: Color(0xFF367C2B)),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  '$area • $crop',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: healthColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '${(health * 100).toInt()}%',
              style: TextStyle(
                color: healthColor,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthOverview() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildHealthIndicator('ممتاز', 4, const Color(0xFF2E7D32)),
                _buildHealthIndicator('جيد', 5, const Color(0xFF4CAF50)),
                _buildHealthIndicator('متوسط', 2, const Color(0xFFFF9800)),
                _buildHealthIndicator('ضعيف', 1, const Color(0xFFF44336)),
              ],
            ),
            const SizedBox(height: 16),
            // شريط التقدم المجمع
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: Row(
                children: [
                  Expanded(
                    flex: 4,
                    child: Container(
                      height: 24,
                      color: const Color(0xFF2E7D32),
                    ),
                  ),
                  Expanded(
                    flex: 5,
                    child: Container(
                      height: 24,
                      color: const Color(0xFF4CAF50),
                    ),
                  ),
                  Expanded(
                    flex: 2,
                    child: Container(
                      height: 24,
                      color: const Color(0xFFFF9800),
                    ),
                  ),
                  Expanded(
                    flex: 1,
                    child: Container(
                      height: 24,
                      color: const Color(0xFFF44336),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHealthIndicator(String label, int count, Color color) {
    return Column(
      children: [
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Center(
            child: Text(
              '$count',
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: const TextStyle(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildTasksSummary() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildTaskTypeRow('ري', 5, Icons.water_drop, Colors.blue),
            const Divider(),
            _buildTaskTypeRow('تسميد', 3, Icons.eco, Colors.green),
            const Divider(),
            _buildTaskTypeRow('رش', 2, Icons.pest_control, Colors.orange),
            const Divider(),
            _buildTaskTypeRow('تفقد', 4, Icons.search, Colors.purple),
          ],
        ),
      ),
    );
  }

  Widget _buildTaskTypeRow(
      String type, int count, IconData icon, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              type,
              style: const TextStyle(fontWeight: FontWeight.w500),
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              '$count مهام',
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductionTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // إحصائيات الإنتاج
          Text(
            'إنتاج الموسم الحالي',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _buildProductionStats(),
          const SizedBox(height: 24),

          // مقارنة المواسم
          Text(
            'مقارنة المواسم',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _buildSeasonComparison(),
          const SizedBox(height: 24),

          // المحاصيل
          Text(
            'توزيع المحاصيل',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 12),
          _buildCropDistribution(),
        ],
      ),
    );
  }

  Widget _buildProductionStats() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildProductionStat('الإنتاج المتوقع', '2,450 طن', Icons.inventory),
                _buildProductionStat('المحصود', '1,200 طن', Icons.agriculture),
                _buildProductionStat('الباقي', '1,250 طن', Icons.schedule),
              ],
            ),
            const SizedBox(height: 16),
            // شريط التقدم
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('نسبة الإنجاز'),
                    Text(
                      '49%',
                      style: TextStyle(
                        color: const Color(0xFF367C2B),
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                LinearProgressIndicator(
                  value: 0.49,
                  backgroundColor: Colors.grey[200],
                  valueColor: const AlwaysStoppedAnimation(Color(0xFF367C2B)),
                  minHeight: 8,
                  borderRadius: BorderRadius.circular(4),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductionStat(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: const Color(0xFF367C2B), size: 28),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildSeasonComparison() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildSeasonRow('2024', 2200, 2450),
            const SizedBox(height: 12),
            _buildSeasonRow('2023', 2100, 2100),
            const SizedBox(height: 12),
            _buildSeasonRow('2022', 1950, 1950),
          ],
        ),
      ),
    );
  }

  Widget _buildSeasonRow(String year, int actual, int target) {
    final percentage = (actual / target * 100).toInt();
    return Column(
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              year,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '$actual / $target طن',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: actual / target,
          backgroundColor: Colors.grey[200],
          valueColor: AlwaysStoppedAnimation(
            percentage >= 100 ? Colors.green : const Color(0xFF367C2B),
          ),
          minHeight: 8,
          borderRadius: BorderRadius.circular(4),
        ),
      ],
    );
  }

  Widget _buildCropDistribution() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildCropRow('قمح', 180, Colors.amber),
            const Divider(),
            _buildCropRow('ذرة', 120, Colors.yellow[700]!),
            const Divider(),
            _buildCropRow('شعير', 80, Colors.orange),
            const Divider(),
            _buildCropRow('برسيم', 70, Colors.green),
          ],
        ),
      ),
    );
  }

  Widget _buildCropRow(String crop, int hectares, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            width: 12,
            height: 12,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(3),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(crop),
          ),
          Text(
            '$hectares هكتار',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  Widget _buildReportsTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        _buildReportCard(
          title: 'تقرير الإنتاج الشهري',
          description: 'ملخص إنتاج الشهر الحالي',
          icon: Icons.analytics,
          date: 'ديسمبر 2024',
        ),
        _buildReportCard(
          title: 'تقرير صحة المحاصيل',
          description: 'تحليل NDVI لجميع الحقول',
          icon: Icons.health_and_safety,
          date: 'أسبوعي',
        ),
        _buildReportCard(
          title: 'تقرير استهلاك المياه',
          description: 'كميات الري ونسبة التوفير',
          icon: Icons.water_drop,
          date: 'ديسمبر 2024',
        ),
        _buildReportCard(
          title: 'تقرير الأسمدة',
          description: 'استخدام الأسمدة والتكاليف',
          icon: Icons.eco,
          date: 'ديسمبر 2024',
        ),
        _buildReportCard(
          title: 'تقرير المهام',
          description: 'إنجاز المهام وأداء الفريق',
          icon: Icons.task,
          date: 'أسبوعي',
        ),
      ],
    );
  }

  Widget _buildReportCard({
    required String title,
    required String description,
    required IconData icon,
    required String date,
  }) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFF367C2B).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: const Color(0xFF367C2B)),
        ),
        title: Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SizedBox(height: 4),
            Text(description),
            const SizedBox(height: 4),
            Text(
              date,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[500],
              ),
            ),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.download),
          onPressed: () {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('جاري تحميل $title...'),
                backgroundColor: const Color(0xFF367C2B),
              ),
            );
          },
        ),
      ),
    );
  }

  Color _getHealthColor(double value) {
    if (value >= 0.8) return const Color(0xFF2E7D32);
    if (value >= 0.6) return const Color(0xFF4CAF50);
    if (value >= 0.4) return const Color(0xFFFF9800);
    return const Color(0xFFF44336);
  }
}
