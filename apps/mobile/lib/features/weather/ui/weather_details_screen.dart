import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';

/// شاشة تفاصيل الطقس - Weather Details
/// عرض التوقعات بالساعة واليوم مع تأثيرها على الزراعة
class WeatherDetailsScreen extends StatefulWidget {
  const WeatherDetailsScreen({super.key});

  @override
  State<WeatherDetailsScreen> createState() => _WeatherDetailsScreenState();
}

class _WeatherDetailsScreenState extends State<WeatherDetailsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      body: CustomScrollView(
        slivers: [
          // App Bar with Weather Hero
          SliverAppBar(
            expandedHeight: 280,
            pinned: true,
            backgroundColor: SahoolColors.forestGreen,
            foregroundColor: Colors.white,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    colors: [
                      SahoolColors.forestGreen,
                      Color(0xFF1E4D2B),
                    ],
                    begin: Alignment.topCenter,
                    end: Alignment.bottomCenter,
                  ),
                ),
                child: SafeArea(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 40),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Icon(
                              Icons.wb_sunny,
                              size: 64,
                              color: SahoolColors.harvestGold,
                            ),
                            const SizedBox(width: 16),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  "32°",
                                  style: TextStyle(
                                    fontSize: 72,
                                    fontWeight: FontWeight.w300,
                                    color: Colors.white,
                                    height: 1,
                                  ),
                                ),
                                Text(
                                  "مشمس",
                                  style: TextStyle(
                                    fontSize: 20,
                                    color: Colors.white.withOpacity(0.9),
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.location_on, size: 16, color: Colors.white70),
                            const SizedBox(width: 4),
                            Text(
                              "الحقل الشمالي • صنعاء",
                              style: TextStyle(
                                color: Colors.white.withOpacity(0.8),
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 24),
                        // Quick Stats
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                          children: [
                            _WeatherStat(icon: Icons.water_drop, value: "45%", label: "رطوبة"),
                            _WeatherStat(icon: Icons.air, value: "12 كم/س", label: "الرياح"),
                            _WeatherStat(icon: Icons.thermostat, value: "24°", label: "الشعور"),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),
            title: const Text("الطقس"),
            actions: [
              IconButton(
                icon: const Icon(Icons.notifications_none),
                onPressed: () => _showAlertSettings(context),
              ),
            ],
          ),

          // Tab Bar
          SliverPersistentHeader(
            pinned: true,
            delegate: _SliverTabBarDelegate(
              TabBar(
                controller: _tabController,
                labelColor: SahoolColors.forestGreen,
                unselectedLabelColor: Colors.grey,
                indicatorColor: SahoolColors.forestGreen,
                tabs: const [
                  Tab(text: "بالساعة"),
                  Tab(text: "الأسبوع"),
                ],
              ),
            ),
          ),

          // Content
          SliverFillRemaining(
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildHourlyTab(),
                _buildWeeklyTab(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHourlyTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Hourly Forecast
        const Text(
          "توقعات الساعات القادمة",
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 16),
        SizedBox(
          height: 120,
          child: ListView(
            scrollDirection: Axis.horizontal,
            children: const [
              _HourlyItem(time: "الآن", temp: "32°", icon: Icons.wb_sunny, isNow: true),
              _HourlyItem(time: "2 م", temp: "34°", icon: Icons.wb_sunny),
              _HourlyItem(time: "3 م", temp: "33°", icon: Icons.wb_sunny),
              _HourlyItem(time: "4 م", temp: "31°", icon: Icons.cloud),
              _HourlyItem(time: "5 م", temp: "29°", icon: Icons.cloud),
              _HourlyItem(time: "6 م", temp: "27°", icon: Icons.nights_stay),
              _HourlyItem(time: "7 م", temp: "25°", icon: Icons.nights_stay),
              _HourlyItem(time: "8 م", temp: "24°", icon: Icons.nights_stay),
            ],
          ),
        ),

        const SizedBox(height: 32),

        // Agricultural Insights
        const Text(
          "التأثير الزراعي",
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 16),
        _InsightCard(
          icon: Icons.water_drop,
          title: "الري",
          insight: "وقت مناسب للري الصباحي قبل الساعة 10",
          status: InsightStatus.good,
        ),
        const SizedBox(height: 12),
        _InsightCard(
          icon: Icons.bug_report,
          title: "الرش",
          insight: "تجنب الرش - سرعة الرياح مرتفعة",
          status: InsightStatus.warning,
        ),
        const SizedBox(height: 12),
        _InsightCard(
          icon: Icons.grass,
          title: "الحصاد",
          insight: "ظروف ممتازة للحصاد حتى الساعة 4",
          status: InsightStatus.good,
        ),

        const SizedBox(height: 32),

        // Detailed Metrics
        const Text(
          "قياسات تفصيلية",
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 16),
        OrganicCard(
          child: Column(
            children: [
              _MetricRow(label: "درجة الحرارة القصوى", value: "35°C", icon: Icons.arrow_upward),
              const Divider(height: 24),
              _MetricRow(label: "درجة الحرارة الدنيا", value: "22°C", icon: Icons.arrow_downward),
              const Divider(height: 24),
              _MetricRow(label: "الرطوبة النسبية", value: "45%", icon: Icons.water_drop),
              const Divider(height: 24),
              _MetricRow(label: "سرعة الرياح", value: "12 كم/س", icon: Icons.air),
              const Divider(height: 24),
              _MetricRow(label: "اتجاه الرياح", value: "شمال شرق", icon: Icons.explore),
              const Divider(height: 24),
              _MetricRow(label: "الضغط الجوي", value: "1013 hPa", icon: Icons.speed),
              const Divider(height: 24),
              _MetricRow(label: "مؤشر الأشعة فوق البنفسجية", value: "8 (عالي)", icon: Icons.wb_sunny),
              const Divider(height: 24),
              _MetricRow(label: "نقطة الندى", value: "18°C", icon: Icons.opacity),
            ],
          ),
        ),

        const SizedBox(height: 80),
      ],
    );
  }

  Widget _buildWeeklyTab() {
    return ListView(
      padding: const EdgeInsets.all(20),
      children: [
        // Weekly Forecast
        const Text(
          "توقعات الأسبوع",
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 16),
        const _DayForecast(day: "اليوم", high: "35°", low: "22°", icon: Icons.wb_sunny, isToday: true),
        const _DayForecast(day: "غداً", high: "33°", low: "21°", icon: Icons.cloud),
        const _DayForecast(day: "الثلاثاء", high: "30°", low: "20°", icon: Icons.grain, rain: "40%"),
        const _DayForecast(day: "الأربعاء", high: "28°", low: "19°", icon: Icons.thunderstorm, rain: "70%"),
        const _DayForecast(day: "الخميس", high: "29°", low: "18°", icon: Icons.cloud),
        const _DayForecast(day: "الجمعة", high: "31°", low: "20°", icon: Icons.wb_sunny),
        const _DayForecast(day: "السبت", high: "32°", low: "21°", icon: Icons.wb_sunny),

        const SizedBox(height: 32),

        // Weekly Agricultural Planning
        const Text(
          "تخطيط الأسبوع الزراعي",
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: SahoolColors.forestGreen,
          ),
        ),
        const SizedBox(height: 16),
        OrganicCard(
          color: SahoolColors.harvestGold.withOpacity(0.1),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: SahoolColors.harvestGold.withOpacity(0.2),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.lightbulb,
                      color: SahoolColors.harvestGold,
                    ),
                  ),
                  const SizedBox(width: 12),
                  const Text(
                    "توصيات الأسبوع",
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              _WeeklyTip(
                icon: Icons.water_drop,
                tip: "يُنصح بتقليل الري يوم الأربعاء بسبب الأمطار المتوقعة",
              ),
              const SizedBox(height: 12),
              _WeeklyTip(
                icon: Icons.bug_report,
                tip: "فرصة جيدة للرش الوقائي اليوم وغداً (رياح خفيفة)",
              ),
              const SizedBox(height: 12),
              _WeeklyTip(
                icon: Icons.agriculture,
                tip: "أفضل أيام الحصاد: اليوم، غداً، والجمعة",
              ),
            ],
          ),
        ),

        const SizedBox(height: 24),

        // Rain Probability Chart
        OrganicCard(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text(
                "احتمالية الأمطار",
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _RainBar(day: "اليوم", percent: 10),
                  _RainBar(day: "غداً", percent: 20),
                  _RainBar(day: "الثلا", percent: 40),
                  _RainBar(day: "الأرب", percent: 70),
                  _RainBar(day: "الخمي", percent: 30),
                  _RainBar(day: "الجمع", percent: 5),
                  _RainBar(day: "السبت", percent: 0),
                ],
              ),
            ],
          ),
        ),

        const SizedBox(height: 80),
      ],
    );
  }

  void _showAlertSettings(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.6,
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
              "تنبيهات الطقس",
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            _AlertToggle(
              title: "تنبيه الصقيع",
              subtitle: "عند انخفاض الحرارة تحت 5°C",
              isEnabled: true,
            ),
            _AlertToggle(
              title: "تنبيه الحرارة العالية",
              subtitle: "عند ارتفاع الحرارة فوق 40°C",
              isEnabled: true,
            ),
            _AlertToggle(
              title: "تنبيه الأمطار",
              subtitle: "عند توقع أمطار خلال 24 ساعة",
              isEnabled: false,
            ),
            _AlertToggle(
              title: "تنبيه الرياح",
              subtitle: "عند تجاوز سرعة الرياح 30 كم/س",
              isEnabled: true,
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

class _SliverTabBarDelegate extends SliverPersistentHeaderDelegate {
  final TabBar tabBar;

  _SliverTabBarDelegate(this.tabBar);

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return Container(
      color: Colors.white,
      child: tabBar,
    );
  }

  @override
  double get maxExtent => tabBar.preferredSize.height;

  @override
  double get minExtent => tabBar.preferredSize.height;

  @override
  bool shouldRebuild(covariant SliverPersistentHeaderDelegate oldDelegate) => false;
}

class _WeatherStat extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;

  const _WeatherStat({
    required this.icon,
    required this.value,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: Colors.white70, size: 20),
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
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

class _HourlyItem extends StatelessWidget {
  final String time;
  final String temp;
  final IconData icon;
  final bool isNow;

  const _HourlyItem({
    required this.time,
    required this.temp,
    required this.icon,
    this.isNow = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 70,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      decoration: BoxDecoration(
        color: isNow ? SahoolColors.forestGreen : Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          Text(
            time,
            style: TextStyle(
              fontSize: 12,
              color: isNow ? Colors.white70 : Colors.grey,
            ),
          ),
          Icon(
            icon,
            color: isNow ? SahoolColors.harvestGold : SahoolColors.harvestGold,
            size: 28,
          ),
          Text(
            temp,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: isNow ? Colors.white : Colors.black87,
            ),
          ),
        ],
      ),
    );
  }
}

enum InsightStatus { good, warning, danger }

class _InsightCard extends StatelessWidget {
  final IconData icon;
  final String title;
  final String insight;
  final InsightStatus status;

  const _InsightCard({
    required this.icon,
    required this.title,
    required this.insight,
    required this.status,
  });

  @override
  Widget build(BuildContext context) {
    Color statusColor;
    switch (status) {
      case InsightStatus.good:
        statusColor = SahoolColors.forestGreen;
        break;
      case InsightStatus.warning:
        statusColor = SahoolColors.harvestGold;
        break;
      case InsightStatus.danger:
        statusColor = SahoolColors.danger;
        break;
    }

    return OrganicCard(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Container(
            width: 44,
            height: 44,
            decoration: BoxDecoration(
              color: statusColor.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Icon(icon, color: statusColor),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  insight,
                  style: TextStyle(fontSize: 13, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              color: statusColor,
              shape: BoxShape.circle,
            ),
          ),
        ],
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _MetricRow({
    required this.label,
    required this.value,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.grey),
        const SizedBox(width: 12),
        Expanded(
          child: Text(label, style: const TextStyle(color: Colors.grey)),
        ),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }
}

class _DayForecast extends StatelessWidget {
  final String day;
  final String high;
  final String low;
  final IconData icon;
  final String? rain;
  final bool isToday;

  const _DayForecast({
    required this.day,
    required this.high,
    required this.low,
    required this.icon,
    this.rain,
    this.isToday = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
      decoration: BoxDecoration(
        color: isToday ? SahoolColors.forestGreen.withOpacity(0.1) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: isToday
            ? Border.all(color: SahoolColors.forestGreen.withOpacity(0.3))
            : null,
      ),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(
              day,
              style: TextStyle(
                fontWeight: isToday ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ),
          Icon(icon, color: SahoolColors.harvestGold),
          const SizedBox(width: 12),
          if (rain != null) ...[
            Icon(Icons.water_drop, size: 14, color: Colors.blue[300]),
            const SizedBox(width: 4),
            Text(
              rain!,
              style: TextStyle(fontSize: 12, color: Colors.blue[400]),
            ),
          ],
          const Spacer(),
          Text(
            high,
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(width: 16),
          Text(
            low,
            style: const TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }
}

class _WeeklyTip extends StatelessWidget {
  final IconData icon;
  final String tip;

  const _WeeklyTip({
    required this.icon,
    required this.tip,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: SahoolColors.forestGreen),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            tip,
            style: const TextStyle(height: 1.4),
          ),
        ),
      ],
    );
  }
}

class _RainBar extends StatelessWidget {
  final String day;
  final int percent;

  const _RainBar({
    required this.day,
    required this.percent,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          "$percent%",
          style: TextStyle(
            fontSize: 10,
            color: percent > 50 ? Colors.blue : Colors.grey,
            fontWeight: percent > 50 ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        const SizedBox(height: 4),
        Container(
          width: 24,
          height: 80,
          decoration: BoxDecoration(
            color: Colors.grey[200],
            borderRadius: BorderRadius.circular(12),
          ),
          child: Align(
            alignment: Alignment.bottomCenter,
            child: Container(
              width: 24,
              height: 80 * (percent / 100),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    Colors.blue[300]!,
                    Colors.blue[500]!,
                  ],
                  begin: Alignment.topCenter,
                  end: Alignment.bottomCenter,
                ),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          day,
          style: const TextStyle(fontSize: 9, color: Colors.grey),
        ),
      ],
    );
  }
}

class _AlertToggle extends StatefulWidget {
  final String title;
  final String subtitle;
  final bool isEnabled;

  const _AlertToggle({
    required this.title,
    required this.subtitle,
    required this.isEnabled,
  });

  @override
  State<_AlertToggle> createState() => _AlertToggleState();
}

class _AlertToggleState extends State<_AlertToggle> {
  late bool _isEnabled;

  @override
  void initState() {
    super.initState();
    _isEnabled = widget.isEnabled;
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        border: Border(
          bottom: BorderSide(color: Colors.grey[200]!),
        ),
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.title,
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                Text(
                  widget.subtitle,
                  style: const TextStyle(fontSize: 12, color: Colors.grey),
                ),
              ],
            ),
          ),
          Switch(
            value: _isEnabled,
            onChanged: (value) => setState(() => _isEnabled = value),
            activeColor: SahoolColors.forestGreen,
          ),
        ],
      ),
    );
  }
}
