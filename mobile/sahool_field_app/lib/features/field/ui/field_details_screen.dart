import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة تفاصيل الحقل - The Field Hub
/// تعرض كل شيء عن الحقل في مكان واحد
class FieldDetailsScreen extends StatelessWidget {
  final String fieldId;
  final String fieldName;

  const FieldDetailsScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 3,
      child: Scaffold(
        backgroundColor: SahoolColors.warmCream,
        appBar: AppBar(
          title: Text(fieldName),
          backgroundColor: Colors.white,
          foregroundColor: SahoolColors.forestGreen,
          elevation: 0,
          actions: [
            IconButton(
              icon: const Icon(Icons.edit_outlined),
              onPressed: () {
                Navigator.pushNamed(context, '/field-form');
              },
            ),
            IconButton(
              icon: const Icon(Icons.more_vert),
              onPressed: () => _showOptionsMenu(context),
            ),
          ],
          bottom: TabBar(
            indicatorSize: TabBarIndicatorSize.label,
            indicatorColor: SahoolColors.forestGreen,
            indicatorWeight: 3,
            labelColor: SahoolColors.forestGreen,
            unselectedLabelColor: Colors.grey,
            labelStyle: const TextStyle(fontWeight: FontWeight.bold),
            tabs: const [
              Tab(text: "نظرة عامة"),
              Tab(text: "الصحة (NDVI)"),
              Tab(text: "السجل"),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildOverviewTab(context),
            _buildHealthTab(context),
            _buildHistoryTab(context),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () {
            Navigator.pushNamed(context, '/scouting');
          },
          backgroundColor: SahoolColors.harvestGold,
          icon: const Icon(Icons.add_a_photo, color: Colors.white),
          label: const Text(
            "كشف ميداني",
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  void _showOptionsMenu(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.share, color: SahoolColors.forestGreen),
              title: const Text("مشاركة التقرير"),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.download, color: SahoolColors.forestGreen),
              title: const Text("تصدير البيانات"),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.delete_outline, color: SahoolColors.danger),
              title: const Text("حذف الحقل", style: TextStyle(color: SahoolColors.danger)),
              onTap: () => Navigator.pop(context),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOverviewTab(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          // 1. بطاقة المحصول الرئيسية
          SizedBox(
            height: 180,
            child: OrganicCard(
              color: SahoolColors.forestGreen,
              isPrimary: true,
              child: Row(
                children: [
                  Expanded(
                    flex: 2,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const StatusBadge(
                          label: "مرحلة النمو",
                          color: Colors.white,
                          icon: Icons.grass,
                        ),
                        const Spacer(),
                        const Text(
                          "قمح شتوي",
                          style: TextStyle(
                            fontSize: 24,
                            fontWeight: FontWeight.bold,
                            color: Colors.white,
                          ),
                        ),
                        Text(
                          "متبقي 45 يوم للحصاد",
                          style: TextStyle(color: Colors.white.withOpacity(0.8)),
                        ),
                        const Spacer(),
                        // شريط التقدم
                        Container(
                          height: 6,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: Colors.white24,
                            borderRadius: BorderRadius.circular(3),
                          ),
                          child: FractionallySizedBox(
                            alignment: Alignment.centerRight,
                            widthFactor: 0.7,
                            child: Container(
                              decoration: BoxDecoration(
                                color: SahoolColors.harvestGold,
                                borderRadius: BorderRadius.circular(3),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 16),
                  // دائرة إحصائية
                  Expanded(
                    child: Container(
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white24, width: 4),
                        color: Colors.white10,
                      ),
                      child: const Center(
                        child: Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text(
                              "78%",
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 24,
                              ),
                            ),
                            Text(
                              "اكتمال",
                              style: TextStyle(
                                color: Colors.white70,
                                fontSize: 10,
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
          ),

          const SizedBox(height: 16),

          // 2. شبكة الخصائص (Grid)
          Row(
            children: [
              Expanded(
                child: _DetailItem(
                  icon: Icons.aspect_ratio,
                  label: "المساحة",
                  value: "2.5 هكتار",
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _DetailItem(
                  icon: Icons.water_drop,
                  label: "الري",
                  value: "تنقيط",
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _DetailItem(
                  icon: Icons.calendar_today,
                  label: "الزراعة",
                  value: "15 أكتوبر",
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 3. إحصائيات سريعة
          Row(
            children: [
              Expanded(
                child: _StatCard(
                  icon: Icons.thermostat,
                  label: "درجة الحرارة",
                  value: "24°C",
                  color: SahoolColors.harvestGold,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _StatCard(
                  icon: Icons.water_drop,
                  label: "رطوبة التربة",
                  value: "45%",
                  color: Colors.blue,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // 4. التوصيات الذكية
          OrganicCard(
            color: Colors.blue.shade50,
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.smart_toy, color: Colors.blue),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "توصية الذكاء الاصطناعي",
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        "الرطوبة منخفضة في القطاع الجنوبي. يُنصح بزيادة الري 20% الليلة.",
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.blue.shade800,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 16),

          // 5. المهام القادمة
          OrganicCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text(
                      "المهام القادمة",
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    TextButton(
                      onPressed: () {},
                      child: const Text("عرض الكل"),
                    ),
                  ],
                ),
                const Divider(),
                _TaskItem(
                  title: "ري القطاع الشمالي",
                  time: "اليوم 6:00 م",
                  icon: Icons.water_drop,
                  color: Colors.blue,
                ),
                _TaskItem(
                  title: "رش المبيدات",
                  time: "غداً 7:00 ص",
                  icon: Icons.bug_report,
                  color: SahoolColors.danger,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHealthTab(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // بطاقة NDVI الرئيسية
        OrganicCard(
          child: Column(
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        "مؤشر NDVI",
                        style: TextStyle(color: Colors.grey),
                      ),
                      Text(
                        "0.72",
                        style: TextStyle(
                          fontSize: 36,
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.forestGreen,
                        ),
                      ),
                    ],
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 12,
                      vertical: 6,
                    ),
                    decoration: BoxDecoration(
                      color: SahoolColors.sageGreen.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.trending_up, color: SahoolColors.sageGreen, size: 16),
                        SizedBox(width: 4),
                        Text(
                          "+5%",
                          style: TextStyle(
                            color: SahoolColors.sageGreen,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              // شريط مؤشر الصحة
              Container(
                height: 8,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(4),
                  gradient: const LinearGradient(
                    colors: [
                      Colors.red,
                      Colors.orange,
                      Colors.yellow,
                      Colors.lightGreen,
                      Colors.green,
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              const Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text("ضعيف", style: TextStyle(fontSize: 10, color: Colors.grey)),
                  Text("ممتاز", style: TextStyle(fontSize: 10, color: Colors.grey)),
                ],
              ),
            ],
          ),
        ),

        const SizedBox(height: 16),

        // صورة NDVI
        ClipRRect(
          borderRadius: BorderRadius.circular(20),
          child: Container(
            height: 250,
            color: SahoolColors.paleOlive,
            child: const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.satellite_alt, size: 48, color: SahoolColors.sageGreen),
                  SizedBox(height: 8),
                  Text(
                    "صورة NDVI القمر الصناعي",
                    style: TextStyle(color: SahoolColors.forestGreen),
                  ),
                  Text(
                    "آخر تحديث: منذ 3 أيام",
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
        ),

        const SizedBox(height: 16),

        const Text(
          "تحليل الصحة النباتية",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        const SizedBox(height: 8),

        // تفاصيل المناطق
        _ZoneHealthCard(
          zoneName: "القطاع الشمالي",
          ndvi: 0.78,
          status: "ممتاز",
          color: SahoolColors.sageGreen,
        ),
        _ZoneHealthCard(
          zoneName: "القطاع الجنوبي",
          ndvi: 0.52,
          status: "يحتاج مراقبة",
          color: SahoolColors.harvestGold,
        ),
        _ZoneHealthCard(
          zoneName: "القطاع الغربي",
          ndvi: 0.35,
          status: "إجهاد مائي",
          color: SahoolColors.danger,
        ),
      ],
    );
  }

  Widget _buildHistoryTab(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text(
          "سجل العمليات",
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        const SizedBox(height: 16),
        _HistoryItem(
          date: "اليوم",
          title: "ري - القطاع الشمالي",
          subtitle: "30 دقيقة • 500 لتر",
          icon: Icons.water_drop,
          color: Colors.blue,
        ),
        _HistoryItem(
          date: "أمس",
          title: "كشف ميداني",
          subtitle: "تم تسجيل 2 ملاحظات",
          icon: Icons.search,
          color: SahoolColors.forestGreen,
        ),
        _HistoryItem(
          date: "منذ 3 أيام",
          title: "رش مبيدات",
          subtitle: "مبيد فطري • 2 لتر/هكتار",
          icon: Icons.bug_report,
          color: SahoolColors.harvestGold,
        ),
        _HistoryItem(
          date: "منذ أسبوع",
          title: "تسميد",
          subtitle: "NPK 20-20-20 • 50 كجم",
          icon: Icons.science,
          color: Colors.purple,
        ),
      ],
    );
  }
}

class _DetailItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailItem({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.1)),
      ),
      child: Column(
        children: [
          Icon(icon, color: SahoolColors.sageGreen),
          const SizedBox(height: 8),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
          Text(
            label,
            style: const TextStyle(fontSize: 10, color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              Text(
                label,
                style: const TextStyle(fontSize: 10, color: Colors.grey),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _TaskItem extends StatelessWidget {
  final String title;
  final String time;
  final IconData icon;
  final Color color;

  const _TaskItem({
    required this.title,
    required this.time,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color, size: 18),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
                Text(
                  time,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
          const Icon(Icons.chevron_left, color: Colors.grey),
        ],
      ),
    );
  }
}

class _ZoneHealthCard extends StatelessWidget {
  final String zoneName;
  final double ndvi;
  final String status;
  final Color color;

  const _ZoneHealthCard({
    required this.zoneName,
    required this.ndvi,
    required this.status,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 40,
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(zoneName, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text(status, style: TextStyle(fontSize: 12, color: color)),
              ],
            ),
          ),
          Text(
            ndvi.toStringAsFixed(2),
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }
}

class _HistoryItem extends StatelessWidget {
  final String date;
  final String title;
  final String subtitle;
  final IconData icon;
  final Color color;

  const _HistoryItem({
    required this.date,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Column(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(icon, color: color, size: 20),
              ),
              Container(
                width: 2,
                height: 40,
                color: Colors.grey.withOpacity(0.2),
              ),
            ],
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  date,
                  style: const TextStyle(fontSize: 10, color: Colors.grey),
                ),
                const SizedBox(height: 4),
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
