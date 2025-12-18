// ============================================
// SAHOOL - Dashboard Screen
// الشاشة الرئيسية - لوحة التحكم
// ============================================

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../core/theme/john_deere_colors.dart';

// Dashboard Screen
class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _currentIndex = 0;

  final List<Widget> _pages = [
    const _HomeTab(),
    const _FieldsTab(),
    const _CalendarTab(),
    const _TasksTab(),
    const _SettingsTab(),
  ];

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: IndexedStack(
          index: _currentIndex,
          children: _pages,
        ),
        bottomNavigationBar: _buildBottomNav(),
        floatingActionButton: _buildFAB(),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      ),
    );
  }

  Widget _buildBottomNav() {
    return BottomAppBar(
      shape: const CircularNotchedRectangle(),
      notchMargin: 8,
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildNavItem(0, Icons.home_rounded, 'الرئيسية'),
          _buildNavItem(1, Icons.landscape_rounded, 'الحقول'),
          const SizedBox(width: 48), // Space for FAB
          _buildNavItem(3, Icons.task_alt_rounded, 'المهام'),
          _buildNavItem(4, Icons.settings_rounded, 'الإعدادات'),
        ],
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    final isSelected = _currentIndex == index;
    return InkWell(
      onTap: () => setState(() => _currentIndex = index),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              icon,
              color: isSelected 
                  ? JohnDeereColors.primary 
                  : JohnDeereColors.textSecondary,
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                color: isSelected 
                    ? JohnDeereColors.primary 
                    : JohnDeereColors.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFAB() {
    return FloatingActionButton(
      onPressed: () {
        setState(() => _currentIndex = 2); // Calendar tab
      },
      backgroundColor: _currentIndex == 2 
          ? JohnDeereColors.primary 
          : JohnDeereColors.secondary,
      child: Icon(
        Icons.calendar_month_rounded,
        color: _currentIndex == 2 
            ? Colors.white 
            : JohnDeereColors.textPrimary,
      ),
    );
  }
}

// ============================================
// HOME TAB - الرئيسية
// ============================================

class _HomeTab extends StatelessWidget {
  const _HomeTab();

  @override
  Widget build(BuildContext context) {
    return CustomScrollView(
      slivers: [
        // App Bar
        SliverAppBar(
          expandedHeight: 200,
          floating: false,
          pinned: true,
          flexibleSpace: FlexibleSpaceBar(
            title: const Text('سهول'),
            background: Container(
              decoration: const BoxDecoration(
                gradient: JohnDeereColors.primaryGradient,
              ),
              child: Stack(
                children: [
                  // Weather Summary
                  Positioned(
                    bottom: 60,
                    right: 16,
                    child: _buildWeatherWidget(),
                  ),
                  // Naw Info
                  Positioned(
                    bottom: 60,
                    left: 16,
                    child: _buildNawWidget(),
                  ),
                ],
              ),
            ),
          ),
          actions: [
            IconButton(
              icon: const Icon(Icons.notifications_outlined),
              onPressed: () {},
            ),
          ],
        ),

        // Quick Stats
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'نظرة سريعة',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    Expanded(child: _buildStatCard('الحقول', '12', Icons.landscape, JohnDeereColors.primary)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildStatCard('المهام', '5', Icons.task_alt, JohnDeereColors.warning)),
                  ],
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(child: _buildStatCard('التنبيهات', '3', Icons.warning_amber, JohnDeereColors.error)),
                    const SizedBox(width: 12),
                    Expanded(child: _buildStatCard('صحة المحاصيل', '87%', Icons.eco, JohnDeereColors.success)),
                  ],
                ),
              ],
            ),
          ),
        ),

        // Active Alerts
        SliverToBoxAdapter(
          child: _buildAlertsSection(),
        ),

        // Recommendations
        SliverToBoxAdapter(
          child: _buildRecommendationsSection(),
        ),

        // Recent Activity
        SliverToBoxAdapter(
          child: _buildRecentActivitySection(),
        ),

        const SliverToBoxAdapter(
          child: SizedBox(height: 100),
        ),
      ],
    );
  }

  Widget _buildWeatherWidget() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.wb_sunny, color: Colors.white, size: 32),
          SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '28°',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'صنعاء',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildNawWidget() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
      ),
      child: const Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.nightlight_round, color: Colors.white, size: 32),
          SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                'نوء الثريا',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                'متبقي 12 يوم',
                style: TextStyle(color: Colors.white70, fontSize: 12),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 14,
              color: color.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertsSection() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'التنبيهات النشطة',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
              TextButton(
                onPressed: () {},
                child: const Text('عرض الكل'),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _buildAlertItem(
            'تحذير طقس',
            'توقع أمطار غزيرة غداً',
            Icons.cloud,
            JohnDeereColors.warning,
          ),
          const SizedBox(height: 8),
          _buildAlertItem(
            'موعد الري',
            'حقل النخيل يحتاج للري',
            Icons.water_drop,
            JohnDeereColors.water,
          ),
        ],
      ),
    );
  }

  Widget _buildAlertItem(String title, String message, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: color.withOpacity(0.2),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  message,
                  style: TextStyle(
                    fontSize: 13,
                    color: JohnDeereColors.textSecondary,
                  ),
                ),
              ],
            ),
          ),
          Icon(Icons.chevron_left, color: JohnDeereColors.textSecondary),
        ],
      ),
    );
  }

  Widget _buildRecommendationsSection() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.auto_awesome, color: JohnDeereColors.primary),
              SizedBox(width: 8),
              Text(
                'توصيات الذكاء الاصطناعي',
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [
                  JohnDeereColors.primaryLight.withOpacity(0.2),
                  JohnDeereColors.primary.withOpacity(0.1),
                ],
              ),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: JohnDeereColors.primary.withOpacity(0.3)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: JohnDeereColors.primary,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: const Text(
                        'وكيل التقويم الفلكي',
                        style: TextStyle(color: Colors.white, fontSize: 12),
                      ),
                    ),
                    const Spacer(),
                    const Text(
                      'منذ ساعة',
                      style: TextStyle(fontSize: 12, color: JohnDeereColors.textSecondary),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  'نوء الثريا هو أفضل وقت لزراعة القطن والسمسم. ننصح بالبدء في تجهيز الأرض خلال الأسبوع القادم.',
                  style: TextStyle(fontSize: 15, height: 1.5),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    OutlinedButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.thumb_up_outlined, size: 18),
                      label: const Text('مفيد'),
                    ),
                    const SizedBox(width: 8),
                    TextButton.icon(
                      onPressed: () {},
                      icon: const Icon(Icons.more_horiz),
                      label: const Text('المزيد'),
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

  Widget _buildRecentActivitySection() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'النشاط الأخير',
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),
          _buildActivityItem('تم إكمال مهمة الري', 'حقل القمح', '10:30 ص', Icons.check_circle, JohnDeereColors.success),
          _buildActivityItem('تحليل NDVI جديد', 'حقل البن', 'أمس', Icons.satellite_alt, JohnDeereColors.info),
          _buildActivityItem('تنبيه آفات', 'حقل الطماطم', 'أمس', Icons.bug_report, JohnDeereColors.warning),
        ],
      ),
    );
  }

  Widget _buildActivityItem(String title, String subtitle, String time, IconData icon, Color color) {
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
            child: Icon(icon, color: color, size: 20),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
                Text(
                  subtitle,
                  style: const TextStyle(fontSize: 13, color: JohnDeereColors.textSecondary),
                ),
              ],
            ),
          ),
          Text(
            time,
            style: const TextStyle(fontSize: 12, color: JohnDeereColors.textSecondary),
          ),
        ],
      ),
    );
  }
}

// ============================================
// PLACEHOLDER TABS
// ============================================

class _FieldsTab extends StatelessWidget {
  const _FieldsTab();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الحقول')),
      body: const Center(child: Text('قائمة الحقول')),
    );
  }
}

class _CalendarTab extends StatelessWidget {
  const _CalendarTab();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('التقويم الفلكي')),
      body: const Center(child: Text('التقويم الفلكي اليمني')),
    );
  }
}

class _TasksTab extends StatelessWidget {
  const _TasksTab();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('المهام')),
      body: const Center(child: Text('قائمة المهام')),
    );
  }
}

class _SettingsTab extends StatelessWidget {
  const _SettingsTab();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الإعدادات')),
      body: const Center(child: Text('الإعدادات')),
    );
  }
}
