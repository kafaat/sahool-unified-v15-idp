import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../crop_health/presentation/providers/crop_health_provider.dart';
import '../../../weather/presentation/providers/weather_provider.dart';
import '../../../notifications/presentation/providers/notification_provider.dart';
import '../widgets/quick_stats_card.dart';
import '../widgets/weather_widget.dart';
import '../widgets/field_card.dart';
import '../widgets/action_summary_widget.dart';
import '../widgets/alert_banner.dart';

/// شاشة الرئيسية الموحدة
/// Unified Home Dashboard
class HomeDashboard extends ConsumerStatefulWidget {
  const HomeDashboard({super.key});

  @override
  ConsumerState<HomeDashboard> createState() => _HomeDashboardState();
}

class _HomeDashboardState extends ConsumerState<HomeDashboard> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    _loadInitialData();
  }

  void _loadInitialData() {
    Future.microtask(() {
      ref.read(notificationsProvider.notifier).loadNotifications();
      // Load weather and crop health for default field
      // ref.read(weatherProvider.notifier).loadWeather('default_field');
    });
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = ref.watch(unreadCountProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Row(
            children: [
              Image.asset(
                'assets/images/sahool_logo.png',
                height: 32,
                errorBuilder: (_, __, ___) => const Icon(Icons.agriculture),
              ),
              const SizedBox(width: 8),
              const Text('سهول'),
            ],
          ),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // أيقونة الإشعارات
            Stack(
              children: [
                IconButton(
                  icon: const Icon(Icons.notifications_outlined),
                  onPressed: () => _navigateToNotifications(),
                ),
                if (unreadCount > 0)
                  Positioned(
                    right: 8,
                    top: 8,
                    child: Container(
                      padding: const EdgeInsets.all(4),
                      decoration: BoxDecoration(
                        color: Colors.red,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      constraints: const BoxConstraints(
                        minWidth: 18,
                        minHeight: 18,
                      ),
                      child: Text(
                        unreadCount > 9 ? '9+' : '$unreadCount',
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
              ],
            ),
            // القائمة
            IconButton(
              icon: const Icon(Icons.menu),
              onPressed: () => _showDrawer(),
            ),
          ],
        ),
        body: _buildBody(),
        bottomNavigationBar: _buildBottomNav(),
        floatingActionButton: FloatingActionButton(
          onPressed: () => _showQuickActions(),
          backgroundColor: const Color(0xFF367C2B),
          child: const Icon(Icons.add, color: Colors.white),
        ),
        floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
      ),
    );
  }

  Widget _buildBody() {
    switch (_currentIndex) {
      case 0:
        return _buildHomeTab();
      case 1:
        return _buildFieldsTab();
      case 2:
        return _buildMapTab();
      case 3:
        return _buildSettingsTab();
      default:
        return _buildHomeTab();
    }
  }

  Widget _buildHomeTab() {
    return RefreshIndicator(
      onRefresh: () async {
        _loadInitialData();
      },
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // شريط التنبيهات
            const AlertBanner(),

            const SizedBox(height: 16),

            // ويدجت الطقس
            const WeatherWidget(),

            const SizedBox(height: 24),

            // إحصائيات سريعة
            Text(
              'نظرة سريعة',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            const QuickStatsCard(),

            const SizedBox(height: 24),

            // ملخص الإجراءات
            Text(
              'الإجراءات المطلوبة',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 12),
            const ActionSummaryWidget(),

            const SizedBox(height: 24),

            // الحقول
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'حقولي',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                TextButton(
                  onPressed: () => setState(() => _currentIndex = 1),
                  child: const Text('عرض الكل'),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildFieldsList(),

            const SizedBox(height: 80), // مساحة للـ FAB
          ],
        ),
      ),
    );
  }

  Widget _buildFieldsList() {
    // Demo fields - في الإنتاج ستكون من API
    final demoFields = [
      {
        'id': 'field_1',
        'name': 'حقل القمح الشمالي',
        'area': 45.5,
        'crop': 'قمح',
        'health': 0.78,
      },
      {
        'id': 'field_2',
        'name': 'حقل الشعير الغربي',
        'area': 32.0,
        'crop': 'شعير',
        'health': 0.85,
      },
      {
        'id': 'field_3',
        'name': 'حقل البرسيم',
        'area': 28.5,
        'crop': 'برسيم',
        'health': 0.65,
      },
    ];

    return Column(
      children: demoFields
          .take(3)
          .map(
            (field) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: FieldCard(
                fieldId: field['id'] as String,
                name: field['name'] as String,
                areaHectares: field['area'] as double,
                cropType: field['crop'] as String,
                healthScore: field['health'] as double,
                onTap: () => _navigateToField(field['id'] as String),
              ),
            ),
          )
          .toList(),
    );
  }

  Widget _buildFieldsTab() {
    return const Center(
      child: Text('قائمة الحقول'),
    );
  }

  Widget _buildMapTab() {
    return const Center(
      child: Text('خريطة الحقول'),
    );
  }

  Widget _buildSettingsTab() {
    return const Center(
      child: Text('الإعدادات'),
    );
  }

  Widget _buildBottomNav() {
    return BottomAppBar(
      shape: const CircularNotchedRectangle(),
      notchMargin: 8,
      child: SizedBox(
        height: 60,
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            _buildNavItem(0, Icons.home, 'الرئيسية'),
            _buildNavItem(1, Icons.landscape, 'الحقول'),
            const SizedBox(width: 48), // مساحة للـ FAB
            _buildNavItem(2, Icons.map, 'الخريطة'),
            _buildNavItem(3, Icons.settings, 'الإعدادات'),
          ],
        ),
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    final isSelected = _currentIndex == index;
    return InkWell(
      onTap: () => setState(() => _currentIndex = index),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            color: isSelected ? const Color(0xFF367C2B) : Colors.grey,
          ),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: isSelected ? const Color(0xFF367C2B) : Colors.grey,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ],
      ),
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
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'إجراء سريع',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildQuickAction(
                      icon: Icons.camera_alt,
                      label: 'تصوير الحقل',
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: Open camera
                      },
                    ),
                    _buildQuickAction(
                      icon: Icons.add_location,
                      label: 'إضافة حقل',
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: Add field
                      },
                    ),
                    _buildQuickAction(
                      icon: Icons.note_add,
                      label: 'ملاحظة جديدة',
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: Add note
                      },
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildQuickAction(
                      icon: Icons.water_drop,
                      label: 'تسجيل ري',
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: Log irrigation
                      },
                    ),
                    _buildQuickAction(
                      icon: Icons.eco,
                      label: 'تسجيل تسميد',
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: Log fertilization
                      },
                    ),
                    _buildQuickAction(
                      icon: Icons.bug_report,
                      label: 'تسجيل مشكلة',
                      onTap: () {
                        Navigator.pop(context);
                        // TODO: Report issue
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuickAction({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        width: 80,
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF367C2B).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: const Color(0xFF367C2B)),
            ),
            const SizedBox(height: 8),
            Text(
              label,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  void _showDrawer() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: DraggableScrollableSheet(
          initialChildSize: 0.6,
          minChildSize: 0.3,
          maxChildSize: 0.9,
          expand: false,
          builder: (context, scrollController) => SingleChildScrollView(
            controller: scrollController,
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // رأس المستخدم
                  Row(
                    children: [
                      const CircleAvatar(
                        radius: 30,
                        backgroundColor: Color(0xFF367C2B),
                        child: Icon(Icons.person, color: Colors.white, size: 32),
                      ),
                      const SizedBox(width: 16),
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'أحمد المزارع',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          Text(
                            'مزرعة الخير',
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                      ),
                    ],
                  ),

                  const Divider(height: 32),

                  // القائمة
                  _buildMenuTile(
                    icon: Icons.person,
                    title: 'الملف الشخصي',
                    onTap: () {},
                  ),
                  _buildMenuTile(
                    icon: Icons.analytics,
                    title: 'التقارير',
                    onTap: () {},
                  ),
                  _buildMenuTile(
                    icon: Icons.history,
                    title: 'السجل',
                    onTap: () {},
                  ),
                  _buildMenuTile(
                    icon: Icons.help,
                    title: 'المساعدة',
                    onTap: () {},
                  ),
                  _buildMenuTile(
                    icon: Icons.info,
                    title: 'حول التطبيق',
                    onTap: () {},
                  ),
                  const Divider(),
                  _buildMenuTile(
                    icon: Icons.logout,
                    title: 'تسجيل الخروج',
                    color: Colors.red,
                    onTap: () {},
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildMenuTile({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
    Color? color,
  }) {
    return ListTile(
      leading: Icon(icon, color: color ?? const Color(0xFF367C2B)),
      title: Text(title, style: TextStyle(color: color)),
      trailing: const Icon(Icons.chevron_left, size: 20),
      onTap: onTap,
    );
  }

  void _navigateToNotifications() {
    // TODO: Navigate to notifications screen
  }

  void _navigateToField(String fieldId) {
    // TODO: Navigate to field details
  }
}
