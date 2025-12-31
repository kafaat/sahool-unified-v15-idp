import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/config/theme.dart';
import 'core/security/screen_security_service.dart';
import 'core/security/device_security_service.dart';
import 'core/security/security_warning_dialog.dart';
import 'features/home/presentation/screens/home_dashboard.dart';
import 'features/tasks/presentation/tasks_list_screen.dart';
import 'features/crop_health/presentation/screens/crop_health_dashboard.dart';
import 'features/weather/presentation/screens/weather_screen.dart';
import 'features/maps/presentation/screens/field_map_screen.dart';
import 'features/notifications/presentation/screens/notifications_screen.dart';
import 'features/marketplace/marketplace_screen.dart';
import 'features/wallet/wallet_screen.dart';
import 'features/community/ui/community_screen.dart';
import 'features/market/ui/sell_harvest_dialog.dart';

/// SAHOOL Field App
/// تطبيق سهول الميداني
class SahoolFieldApp extends ConsumerStatefulWidget {
  const SahoolFieldApp({super.key});

  @override
  ConsumerState<SahoolFieldApp> createState() => _SahoolFieldAppState();
}

class _SahoolFieldAppState extends ConsumerState<SahoolFieldApp> {
  @override
  void initState() {
    super.initState();
    // Set system UI overlay style
    SystemChrome.setSystemUIOverlayStyle(
      const SystemUiOverlayStyle(
        statusBarColor: Colors.transparent,
        statusBarIconBrightness: Brightness.light,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return SecureApp(
      autoEnable: true,
      child: MaterialApp(
        title: 'سهول',
        debugShowCheckedModeBanner: false,

        // Arabic RTL Support
        locale: const Locale('ar'),
        supportedLocales: const [
          Locale('ar'),
          Locale('en'),
        ],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],

        // Theme
        theme: SahoolTheme.light,
        darkTheme: SahoolTheme.dark,
        themeMode: ThemeMode.system,

        // Routes
        home: const MainAppShell(),
        onGenerateRoute: _generateRoute,
      ),
    );
  }

  Route<dynamic>? _generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/':
        return _buildRoute(const MainAppShell(), settings);
      case '/tasks':
        return _buildRoute(const TasksListScreen(), settings);
      case '/crop-health':
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(
          CropHealthDashboard(fieldId: args?['fieldId'] ?? ''),
          settings,
        );
      case '/weather':
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(
          WeatherScreen(fieldId: args?['fieldId'] ?? ''),
          settings,
        );
      case '/map':
        final args = settings.arguments as Map<String, dynamic>?;
        return _buildRoute(
          FieldMapScreen(fieldId: args?['fieldId'] ?? ''),
          settings,
        );
      case '/notifications':
        return _buildRoute(const NotificationsScreen(), settings);
      default:
        return _buildRoute(const MainAppShell(), settings);
    }
  }

  MaterialPageRoute _buildRoute(Widget page, RouteSettings settings) {
    return MaterialPageRoute(
      builder: (_) => page,
      settings: settings,
    );
  }
}

/// Main App Shell with Bottom Navigation
/// الهيكل الرئيسي للتطبيق مع التنقل السفلي
class MainAppShell extends ConsumerStatefulWidget {
  const MainAppShell({super.key});

  @override
  ConsumerState<MainAppShell> createState() => _MainAppShellState();
}

class _MainAppShellState extends ConsumerState<MainAppShell> {
  int _currentIndex = 0;
  bool _hasShownSecurityWarning = false;

  final List<Widget> _screens = [
    const HomeDashboard(),
    const MarketplaceScreen(),
    const WalletScreen(),
    const CommunityScreen(),
    const _MoreScreen(),
  ];

  @override
  void initState() {
    super.initState();
    // Check and show security warning if needed
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkAndShowSecurityWarning();
    });
  }

  /// Check device security and show warning if needed
  Future<void> _checkAndShowSecurityWarning() async {
    if (_hasShownSecurityWarning) return;

    try {
      final securityResult = await ref.read(deviceSecurityCheckProvider.future);

      // Only show warning dialog if there are warnings
      if (securityResult.recommendedAction == SecurityAction.warn &&
          mounted &&
          !_hasShownSecurityWarning) {
        _hasShownSecurityWarning = true;

        // Show warning dialog
        if (mounted) {
          await showSecurityWarningDialog(
            context: context,
            result: securityResult,
            isArabic: true,
            onContinue: () {
              // User chose to continue despite warning
              debugPrint('⚠️ User continued despite security warning');
            },
            onExit: () {
              // User chose to exit
              debugPrint('🔒 User exited due to security warning');
              // Close the app
              SystemNavigator.pop();
            },
          );
        }
      }
    } catch (e) {
      debugPrint('⚠️ Failed to check security warning: $e');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        body: IndexedStack(
          index: _currentIndex,
          children: _screens,
        ),
        bottomNavigationBar: _buildBottomNav(),
        floatingActionButton: _buildFAB(),
        floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      ),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: NavigationBar(
        height: 70,
        elevation: 0,
        selectedIndex: _currentIndex,
        onDestinationSelected: (index) => setState(() => _currentIndex = index),
        backgroundColor: Colors.white,
        indicatorColor: SahoolTheme.primary.withOpacity(0.1),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded, color: SahoolTheme.primary),
            label: 'الرئيسية',
          ),
          NavigationDestination(
            icon: Icon(Icons.storefront_outlined),
            selectedIcon: Icon(Icons.storefront_rounded, color: SahoolTheme.primary),
            label: 'السوق',
          ),
          NavigationDestination(
            icon: Icon(Icons.account_balance_wallet_outlined),
            selectedIcon: Icon(Icons.account_balance_wallet_rounded, color: SahoolTheme.primary),
            label: 'المحفظة',
          ),
          NavigationDestination(
            icon: Icon(Icons.forum_outlined),
            selectedIcon: Icon(Icons.forum_rounded, color: SahoolTheme.primary),
            label: 'المجتمع',
          ),
          NavigationDestination(
            icon: Icon(Icons.more_horiz_outlined),
            selectedIcon: Icon(Icons.more_horiz_rounded, color: SahoolTheme.primary),
            label: 'المزيد',
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem(int index, IconData icon, String label) {
    final isSelected = _currentIndex == index;
    return Expanded(
      child: InkWell(
        onTap: () => setState(() => _currentIndex = index),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              icon,
              color: isSelected ? SahoolTheme.primary : Colors.grey,
              size: 26,
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: isSelected ? SahoolTheme.primary : Colors.grey,
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget? _buildFAB() {
    // Different FABs based on current screen
    switch (_currentIndex) {
      case 0: // Home
        return FloatingActionButton(
          onPressed: _showQuickActions,
          backgroundColor: SahoolTheme.primary,
          child: const Icon(Icons.add, color: Colors.white, size: 28),
        );
      case 1: // Marketplace
        return FloatingActionButton.extended(
          onPressed: () => showSellHarvestDialog(context, ref),
          backgroundColor: SahoolTheme.primary,
          icon: const Icon(Icons.sell, color: Colors.white),
          label: const Text(
            'بيع محصولي',
            style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
          ),
        );
      default:
        return null;
    }
  }

  void _showQuickActions() {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey[300],
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  'إجراء سريع',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildQuickActionItem(
                      icon: Icons.camera_alt_rounded,
                      label: 'تصوير',
                      color: SahoolTheme.info,
                      onTap: () => Navigator.pop(context),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.add_location_rounded,
                      label: 'حقل جديد',
                      color: SahoolTheme.success,
                      onTap: () => Navigator.pop(context),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.assignment_add,
                      label: 'مهمة جديدة',
                      color: SahoolTheme.warning,
                      onTap: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 20),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildQuickActionItem(
                      icon: Icons.water_drop_rounded,
                      label: 'تسجيل ري',
                      color: Colors.blue,
                      onTap: () => Navigator.pop(context),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.eco_rounded,
                      label: 'تسجيل تسميد',
                      color: Colors.green,
                      onTap: () => Navigator.pop(context),
                    ),
                    _buildQuickActionItem(
                      icon: Icons.bug_report_rounded,
                      label: 'تقرير مشكلة',
                      color: Colors.red,
                      onTap: () => Navigator.pop(context),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionItem({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        width: 90,
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Container(
              width: 56,
              height: 56,
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(icon, color: color, size: 28),
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
}

/// Fields placeholder screen
class _FieldsPlaceholder extends StatelessWidget {
  const _FieldsPlaceholder();

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('حقولي'),
          backgroundColor: SahoolTheme.primary,
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.landscape, size: 80, color: Colors.grey[400]),
              const SizedBox(height: 16),
              Text(
                'قائمة الحقول',
                style: TextStyle(fontSize: 18, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// More screen with settings and options
class _MoreScreen extends StatelessWidget {
  const _MoreScreen();

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('المزيد'),
          backgroundColor: SahoolTheme.primary,
        ),
        body: ListView(
          children: [
            const SizedBox(height: 16),
            _buildUserHeader(context),
            const Divider(height: 32),
            _buildMenuItem(
              context,
              icon: Icons.notifications_rounded,
              title: 'الإشعارات',
              onTap: () => Navigator.pushNamed(context, '/notifications'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.map_rounded,
              title: 'الخريطة',
              onTap: () => Navigator.pushNamed(context, '/map'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.analytics_rounded,
              title: 'التقارير',
              onTap: () {},
            ),
            _buildMenuItem(
              context,
              icon: Icons.history_rounded,
              title: 'السجل',
              onTap: () {},
            ),
            const Divider(height: 32),
            _buildMenuItem(
              context,
              icon: Icons.settings_rounded,
              title: 'الإعدادات',
              onTap: () {},
            ),
            _buildMenuItem(
              context,
              icon: Icons.help_rounded,
              title: 'المساعدة',
              onTap: () {},
            ),
            _buildMenuItem(
              context,
              icon: Icons.info_rounded,
              title: 'حول التطبيق',
              subtitle: 'الإصدار 1.0.0',
              onTap: () {},
            ),
            const Divider(height: 32),
            _buildMenuItem(
              context,
              icon: Icons.logout_rounded,
              title: 'تسجيل الخروج',
              color: Colors.red,
              onTap: () {},
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  Widget _buildUserHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: SahoolTheme.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Icon(
              Icons.person_rounded,
              size: 36,
              color: SahoolTheme.primary,
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'أحمد المزارع',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  'مزرعة الخير',
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit_rounded),
            onPressed: () {},
            color: SahoolTheme.primary,
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    String? subtitle,
    Color? color,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: (color ?? SahoolTheme.primary).withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(icon, color: color ?? SahoolTheme.primary),
      ),
      title: Text(
        title,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: Icon(
        Icons.chevron_left_rounded,
        color: Colors.grey[400],
      ),
      onTap: onTap,
    );
  }
}
