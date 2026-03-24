import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_gen/gen_l10n/app_localizations.dart';
import 'core/config/theme.dart';
import 'core/routes/app_router.dart';
import 'core/deeplink/deeplink_handler.dart';
import 'core/auth/auth_service.dart';

/// GoRouter provider with authentication guard
/// مزود GoRouter مع حماية المصادقة
final appRouterProvider = Provider<GoRouter>((ref) {
  return createAppRouter(ref);
});

/// Create GoRouter with authentication redirect guard
/// إنشاء GoRouter مع إعادة التوجيه للمصادقة
GoRouter createAppRouter(Ref ref) {
  // Routes that don't require authentication
  final publicRoutes = [
    '/splash',
    '/login',
    '/role-selection',
    '/forgot-password',
    '/reset-password',
    '/verify-otp',
    '/biometric-settings',
  ];

  return GoRouter(
    navigatorKey: GlobalKey<NavigatorState>(debugLabel: 'root'),
    initialLocation: '/splash',
    debugLogDiagnostics: kDebugMode, // Only enable in debug builds
    routes: AppRouter.router.configuration.routes,

    // Authentication redirect guard
    // حماية التوجيه للمصادقة
    redirect: (BuildContext context, GoRouterState state) async {
      final isPublicRoute = publicRoutes.any(
        (route) => state.matchedLocation.startsWith(route),
      );

      // Check if user is authenticated
      final authService = ref.read(authServiceProvider);
      final isLoggedIn = await authService.isLoggedIn();

      // Allow access to public routes
      if (isPublicRoute) {
        // If logged in and trying to access login page, redirect to home
        if (isLoggedIn && state.matchedLocation == '/login') {
          return '/home';
        }
        return null;
      }

      // If not logged in and trying to access protected route, redirect to login
      if (!isLoggedIn) {
        // Store the intended destination for after login
        final redirectPath = Uri.encodeComponent(state.matchedLocation);
        return '/login?redirect=$redirectPath';
      }

      // No redirect needed - user is authenticated
      return null;
    },
  );
}

/// SAHOOL Field App with GoRouter Integration
/// تطبيق سهول الميداني مع تكامل GoRouter
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
    // Get router from provider
    final router = ref.watch(appRouterProvider);

    // Set router on deep link handler
    final deepLinkNotifier = ref.read(deepLinkProvider.notifier);
    deepLinkNotifier.setRouter(router);

    return DeepLinkHandler(
      autoHandle: true,
      child: MaterialApp.router(
        title: 'سهول',
        debugShowCheckedModeBanner: false,

        // Arabic RTL Support
        locale: const Locale('ar'),
        supportedLocales: const [
          Locale('ar'),
          Locale('en'),
        ],
        localizationsDelegates: const [
          AppLocalizations.delegate,
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],

        // Theme
        theme: SahoolTheme.light,
        darkTheme: SahoolTheme.dark,
        themeMode: ThemeMode.system,

        // GoRouter configuration
        routerConfig: router,
      ),
    );
  }
}

// NOTE: MainAppShell is now replaced by GoRouter's ShellRoute and MainLayout
// The navigation is handled in core/routes/app_router.dart
// الملاحظة: تم استبدال MainAppShell بـ ShellRoute من GoRouter وMainLayout
// يتم التعامل مع التنقل في core/routes/app_router.dart

/// More screen with settings and options - uses GoRouter for navigation
/// شاشة المزيد مع الإعدادات والخيارات - تستخدم GoRouter للتنقل
class MoreScreen extends StatelessWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(l10n.moreMenu),
          backgroundColor: SahoolTheme.primary,
        ),
        body: ListView(
          children: [
            const SizedBox(height: 16),
            _buildUserHeader(context, l10n),
            const Divider(height: 32),
            _buildMenuItem(
              context,
              icon: Icons.notifications_rounded,
              title: l10n.notifications,
              onTap: () => context.push('/notifications'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.map_rounded,
              title: l10n.theMap,
              onTap: () => context.push('/map'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.analytics_rounded,
              title: l10n.theReports,
              onTap: () => context.push('/satellite'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.history_rounded,
              title: l10n.theHistory,
              onTap: () => context.push('/tasks'),
            ),
            const Divider(height: 32),
            _buildMenuItem(
              context,
              icon: Icons.sync_rounded,
              title: l10n.theSync,
              onTap: () => context.push('/sync'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.settings_rounded,
              title: l10n.settings,
              onTap: () => context.push('/profile'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.help_rounded,
              title: l10n.theHelp,
              onTap: () => context.push('/advisor'),
            ),
            _buildMenuItem(
              context,
              icon: Icons.info_rounded,
              title: l10n.aboutApp,
              subtitle: l10n.versionNumber('16.0.0'),
              onTap: () {
                showAboutDialog(
                  context: context,
                  applicationName: l10n.appName,
                  applicationVersion: '16.0.0',
                  applicationIcon: const Icon(
                    Icons.agriculture,
                    size: 48,
                    color: SahoolTheme.primary,
                  ),
                  applicationLegalese: l10n.allRightsReservedKafaat,
                );
              },
            ),
            const Divider(height: 32),
            _buildMenuItem(
              context,
              icon: Icons.logout_rounded,
              title: l10n.logout,
              color: Colors.red,
              onTap: () {
                _showLogoutConfirmation(context, l10n);
              },
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }

  void _showLogoutConfirmation(BuildContext context, AppLocalizations l10n) {
    showDialog(
      context: context,
      builder: (dialogContext) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: Text(l10n.logoutConfirmationTitle),
          content: Text(l10n.logoutConfirmationMessage),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext),
              child: Text(l10n.cancel),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(dialogContext); // Close dialog
                context.go('/login'); // Navigate to login using GoRouter
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
                foregroundColor: Colors.white,
              ),
              child: Text(l10n.logout),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUserHeader(BuildContext context, AppLocalizations l10n) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: SahoolTheme.primary.withValues(alpha: 0.1),
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
                  l10n.farmerName,
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  l10n.farmNameExample,
                  style: TextStyle(color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.edit_rounded),
            onPressed: () => context.push('/profile'),
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
          color: (color ?? SahoolTheme.primary).withValues(alpha: 0.1),
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

/// Quick Actions Bottom Sheet Widget - uses GoRouter for navigation
/// ورقة الإجراءات السريعة السفلية - تستخدم GoRouter للتنقل
class QuickActionsSheet extends StatelessWidget {
  const QuickActionsSheet({super.key});

  @override
  Widget build(BuildContext context) {
    return Directionality(
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
                    context,
                    icon: Icons.camera_alt_rounded,
                    label: 'تصوير',
                    color: SahoolTheme.info,
                    route: '/scanner',
                  ),
                  _buildQuickActionItem(
                    context,
                    icon: Icons.add_location_rounded,
                    label: 'حقل جديد',
                    color: SahoolTheme.success,
                    route: '/fields',
                  ),
                  _buildQuickActionItem(
                    context,
                    icon: Icons.assignment_add,
                    label: 'مهمة جديدة',
                    color: SahoolTheme.warning,
                    route: '/tasks',
                  ),
                ],
              ),
              const SizedBox(height: 20),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildQuickActionItem(
                    context,
                    icon: Icons.water_drop_rounded,
                    label: 'تسجيل ري',
                    color: Colors.blue,
                    route: '/pivot-irrigation',
                  ),
                  _buildQuickActionItem(
                    context,
                    icon: Icons.eco_rounded,
                    label: 'تسجيل تسميد',
                    color: Colors.green,
                    route: '/vra',
                  ),
                  _buildQuickActionItem(
                    context,
                    icon: Icons.bug_report_rounded,
                    label: 'تقرير مشكلة',
                    color: Colors.red,
                    route: '/scouting',
                  ),
                ],
              ),
              const SizedBox(height: 16),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildQuickActionItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Color color,
    required String route,
  }) {
    return InkWell(
      onTap: () {
        Navigator.pop(context); // Close the bottom sheet
        context.push(route); // Navigate using GoRouter
      },
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
                color: color.withValues(alpha: 0.1),
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

/// Show the quick actions bottom sheet
/// إظهار ورقة الإجراءات السريعة السفلية
void showQuickActionsSheet(BuildContext context) {
  showModalBottomSheet(
    context: context,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
    ),
    builder: (context) => const QuickActionsSheet(),
  );
}
