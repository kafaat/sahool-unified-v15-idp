import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

/// SAHOOL Field Dashboard - لوحة القيادة الزراعية
/// تعرض المؤشرات الحيوية بأسلوب عدادات السيارة
class FieldDashboard extends StatelessWidget {
  const FieldDashboard({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      appBar: AppBar(
        title: const Text('لوحة القيادة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {},
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await Future.delayed(const Duration(seconds: 1));
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // بطاقة الترحيب
            _buildWelcomeCard(),

            const SizedBox(height: 20),

            // بطاقة الحالة الرئيسية (NDVI)
            _buildHealthCard(),

            const SizedBox(height: 20),

            // عنوان المؤشرات
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'المؤشرات الحيوية',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                TextButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.arrow_forward, size: 18),
                  label: const Text('عرض الكل'),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // شبكة العدادات
            _buildMetricsGrid(),

            const SizedBox(height: 20),

            // التنبيهات العاجلة
            _buildAlertsSection(),

            const SizedBox(height: 20),

            // المهام القادمة
            _buildTasksSection(),

            const SizedBox(height: 20),

            // الطقس الأسبوعي
            _buildWeatherForecast(),

            const SizedBox(height: 100), // مسافة للـ FAB
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {},
        icon: const Icon(Icons.add),
        label: const Text('مهمة جديدة'),
      ),
    );
  }

  /// بطاقة الترحيب
  Widget _buildWelcomeCard() {
    final hour = DateTime.now().hour;
    String greeting;
    IconData greetingIcon;

    if (hour < 12) {
      greeting = 'صباح الخير';
      greetingIcon = Icons.wb_sunny;
    } else if (hour < 17) {
      greeting = 'مساء الخير';
      greetingIcon = Icons.wb_cloudy;
    } else {
      greeting = 'مساء الخير';
      greetingIcon = Icons.nights_stay;
    }

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.largeRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: SahoolColors.warning.withOpacity(0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(greetingIcon, color: Colors.orange[700], size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  greeting,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'لديك 3 مهام اليوم',
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: SahoolColors.success.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 8,
                  height: 8,
                  decoration: const BoxDecoration(
                    color: SahoolColors.success,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                const Text(
                  'متصل',
                  style: TextStyle(
                    color: SahoolColors.success,
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// بطاقة صحة المحصول الرئيسية
  Widget _buildHealthCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: SahoolColors.primaryGradient,
        borderRadius: SahoolRadius.xlargeRadius,
        boxShadow: SahoolShadows.colored(SahoolColors.primary),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.eco, color: Colors.white70, size: 20),
                    const SizedBox(width: 8),
                    Text(
                      'صحة المحصول',
                      style: TextStyle(color: Colors.white.withOpacity(0.8), fontSize: 14),
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                const Text(
                  'ممتازة',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 12),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      const Icon(Icons.satellite_alt, color: Colors.white, size: 16),
                      const SizedBox(width: 6),
                      const Text(
                        'NDVI: 0.78',
                        style: TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'آخر تحديث: منذ ساعتين',
                  style: TextStyle(color: Colors.white.withOpacity(0.6), fontSize: 12),
                ),
              ],
            ),
          ),
          // الدائرة التقدمية
          SizedBox(
            height: 100,
            width: 100,
            child: Stack(
              alignment: Alignment.center,
              children: [
                SizedBox(
                  height: 100,
                  width: 100,
                  child: CircularProgressIndicator(
                    value: 0.78,
                    backgroundColor: Colors.white.withOpacity(0.2),
                    valueColor: const AlwaysStoppedAnimation(Colors.white),
                    strokeWidth: 10,
                  ),
                ),
                const Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '78%',
                      style: TextStyle(
                        color: Colors.white,
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'الصحة',
                      style: TextStyle(color: Colors.white70, fontSize: 12),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  /// شبكة المؤشرات
  Widget _buildMetricsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 1.2,
      children: [
        _buildMetricCard(
          'رطوبة التربة',
          '35%',
          Icons.water_drop,
          SahoolColors.info,
          trend: -5,
          unit: '%',
        ),
        _buildMetricCard(
          'النيتروجين',
          'منخفض',
          Icons.grass,
          SahoolColors.warning,
          showWarning: true,
        ),
        _buildMetricCard(
          'الطقس',
          '32°',
          Icons.wb_sunny,
          Colors.amber,
          subtitle: 'مشمس',
        ),
        _buildMetricCard(
          'التراكم الحراري',
          '1,200',
          Icons.thermostat,
          SahoolColors.danger,
          unit: 'GDD',
        ),
      ],
    );
  }

  Widget _buildMetricCard(
    String title,
    String value,
    IconData icon,
    Color color, {
    int? trend,
    String? unit,
    String? subtitle,
    bool showWarning = false,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.largeRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(icon, color: color, size: 24),
              ),
              if (showWarning)
                Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(
                    color: SahoolColors.warning.withOpacity(0.2),
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.warning_amber,
                    color: SahoolColors.warning,
                    size: 16,
                  ),
                ),
              if (trend != null)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: trend > 0
                        ? SahoolColors.success.withOpacity(0.1)
                        : SahoolColors.danger.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        trend > 0 ? Icons.arrow_upward : Icons.arrow_downward,
                        size: 12,
                        color: trend > 0 ? SahoolColors.success : SahoolColors.danger,
                      ),
                      Text(
                        '${trend.abs()}%',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: trend > 0 ? SahoolColors.success : SahoolColors.danger,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const Spacer(),
          Row(
            crossAxisAlignment: CrossAxisAlignment.baseline,
            textBaseline: TextBaseline.alphabetic,
            children: [
              Text(
                value,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (unit != null)
                Text(
                  ' $unit',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            subtitle ?? title,
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// قسم التنبيهات
  Widget _buildAlertsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              children: [
                const Text(
                  'التنبيهات',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: SahoolColors.danger,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Text(
                    '2',
                    style: TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            TextButton(onPressed: () {}, child: const Text('عرض الكل')),
          ],
        ),
        const SizedBox(height: 12),
        _buildAlertItem(
          'نقص النيتروجين',
          'حقل القمح الشمالي يحتاج تسميد',
          Icons.eco,
          SahoolColors.warning,
          'منذ 3 ساعات',
        ),
        const SizedBox(height: 8),
        _buildAlertItem(
          'موعد الري',
          'حقل الذرة يحتاج ري خلال 6 ساعات',
          Icons.water_drop,
          SahoolColors.info,
          'منذ ساعة',
        ),
      ],
    );
  }

  Widget _buildAlertItem(String title, String subtitle, IconData icon, Color color, String time) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: SahoolRadius.mediumRadius,
        border: Border.all(color: color.withOpacity(0.3)),
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 24),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 4),
                Text(subtitle, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(time, style: TextStyle(color: Colors.grey[500], fontSize: 10)),
              const SizedBox(height: 8),
              Icon(Icons.chevron_left, color: Colors.grey[400]),
            ],
          ),
        ],
      ),
    );
  }

  /// قسم المهام
  Widget _buildTasksSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'المهام القادمة',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        const SizedBox(height: 12),
        _buildTaskItem('ري حقل الذرة', 'اليوم 2:00 م', Icons.water_drop, false),
        _buildTaskItem('فحص الآفات', 'غداً 8:00 ص', Icons.bug_report, false),
        _buildTaskItem('تسميد القمح', 'تم', Icons.eco, true),
      ],
    );
  }

  Widget _buildTaskItem(String title, String time, IconData icon, bool completed) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: completed ? SahoolColors.success.withOpacity(0.05) : Colors.white,
        borderRadius: SahoolRadius.mediumRadius,
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        children: [
          Container(
            width: 24,
            height: 24,
            decoration: BoxDecoration(
              color: completed ? SahoolColors.success : Colors.transparent,
              shape: BoxShape.circle,
              border: Border.all(
                color: completed ? SahoolColors.success : Colors.grey[400]!,
                width: 2,
              ),
            ),
            child: completed ? const Icon(Icons.check, color: Colors.white, size: 16) : null,
          ),
          const SizedBox(width: 12),
          Icon(icon, color: completed ? Colors.grey[400] : SahoolColors.primary, size: 20),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              title,
              style: TextStyle(
                decoration: completed ? TextDecoration.lineThrough : null,
                color: completed ? Colors.grey[500] : SahoolColors.textDark,
              ),
            ),
          ),
          Text(
            time,
            style: TextStyle(
              color: completed ? Colors.grey[400] : SahoolColors.textSecondary,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  /// توقعات الطقس
  Widget _buildWeatherForecast() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'توقعات الطقس',
          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
        ),
        const SizedBox(height: 12),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: SahoolRadius.largeRadius,
            boxShadow: SahoolShadows.small,
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildWeatherDay('اليوم', Icons.wb_sunny, '32°', '22°'),
              _buildWeatherDay('غداً', Icons.wb_cloudy, '28°', '20°'),
              _buildWeatherDay('الأربعاء', Icons.grain, '25°', '18°'),
              _buildWeatherDay('الخميس', Icons.wb_sunny, '30°', '21°'),
              _buildWeatherDay('الجمعة', Icons.wb_sunny, '33°', '23°'),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildWeatherDay(String day, IconData icon, String high, String low) {
    return Column(
      children: [
        Text(day, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
        const SizedBox(height: 8),
        Icon(icon, color: Colors.amber, size: 28),
        const SizedBox(height: 8),
        Text(high, style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(low, style: TextStyle(color: Colors.grey[500], fontSize: 12)),
      ],
    );
  }
}
