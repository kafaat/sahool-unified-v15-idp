import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Core
import '../constants/navigation_constants.dart';

// Features - Auth & Onboarding
import '../../features/splash/ui/splash_screen.dart';
import '../../features/auth/ui/role_selection_screen.dart';
import '../../features/auth/ui/login_screen.dart';

// Features - Main Layout
import '../../features/main_layout/main_layout.dart';
import '../../features/home/presentation/screens/home_dashboard.dart';

// Features - Field Management
import '../../features/map_home/ui/map_screen.dart';
import '../../features/fields/presentation/screens/fields_list_screen.dart';
import '../../features/fields/presentation/screens/field_details_screen.dart';
import '../../features/field_hub/ui/field_dashboard.dart';

// Features - Precision Agriculture
import '../../features/vra/screens/vra_list_screen.dart';
import '../../features/vra/screens/vra_detail_screen.dart';
import '../../features/vra/screens/vra_create_screen.dart';
import '../../features/gdd/screens/gdd_dashboard_screen.dart';
import '../../features/gdd/screens/gdd_chart_screen.dart';
import '../../features/gdd/screens/gdd_settings_screen.dart';
import '../../features/spray/screens/spray_dashboard_screen.dart';
import '../../features/spray/screens/spray_calendar_screen.dart';
import '../../features/spray/screens/spray_log_screen.dart';
import '../../features/rotation/screens/rotation_plan_screen.dart';
import '../../features/rotation/screens/rotation_calendar_screen.dart';
import '../../features/rotation/screens/crop_compatibility_screen.dart';
import '../../features/profitability/screens/profitability_dashboard_screen.dart';
import '../../features/profitability/screens/crop_profitability_screen.dart';
import '../../features/profitability/screens/season_summary_screen.dart';

// Features - Inventory & Resources
import '../../features/inventory/ui/inventory_list_screen.dart';
import '../../features/inventory/ui/item_detail_screen.dart';
import '../../features/inventory/ui/add_item_screen.dart';

// Features - AI & Chat
import '../../features/chat/presentation/screens/conversations_screen.dart';
import '../../features/chat/presentation/screens/chat_screen.dart';
import '../../features/advisor/ui/advisor_screen.dart';
import '../../features/scanner/ui/scanner_screen.dart';
import '../../features/scouting/ui/scouting_screen.dart';

// Features - Satellite & Monitoring
import '../../features/satellite/presentation/screens/satellite_dashboard_screen.dart';
import '../../features/satellite/presentation/screens/ndvi_detail_screen.dart';
import '../../features/satellite/presentation/screens/phenology_screen.dart';
import '../../features/satellite/presentation/screens/weather_screen.dart' as sat_weather;

// Features - Other
import '../../features/alerts/ui/alerts_screen.dart';
import '../../features/profile/ui/profile_screen.dart';
import '../../features/sync/ui/sync_screen.dart';
import '../../features/weather/presentation/screens/weather_screen.dart';
import '../../features/tasks/presentation/tasks_list_screen.dart';
import '../../features/crop_health/presentation/screens/crop_health_dashboard.dart';
import '../../features/notifications/presentation/screens/notifications_screen.dart';
import '../../features/marketplace/marketplace_screen.dart';

/// SAHOOL App Router Configuration
/// تكوين مسارات التطبيق باستخدام go_router
class AppRouter {
  static final GlobalKey<NavigatorState> _rootNavigatorKey =
      GlobalKey<NavigatorState>(debugLabel: 'root');
  static final GlobalKey<NavigatorState> _shellNavigatorKey =
      GlobalKey<NavigatorState>(debugLabel: 'shell');

  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/home',
    debugLogDiagnostics: true,

    routes: [
      // ═══════════════════════════════════════════════════════════════════════
      // Onboarding & Auth Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/splash',
        name: 'splash',
        builder: (context, state) => const SplashScreen(),
      ),

      GoRoute(
        path: '/role-selection',
        name: 'role-selection',
        builder: (context, state) => const RoleSelectionScreen(),
      ),

      GoRoute(
        path: '/login',
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Main App Shell (with Bottom Navigation)
      // ═══════════════════════════════════════════════════════════════════════

      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) => MainLayout(child: child),
        routes: [
          // Home Dashboard
          GoRoute(
            path: '/home',
            name: 'home',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: HomeDashboard(),
            ),
          ),

          // Fields List
          GoRoute(
            path: '/fields',
            name: 'fields',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: FieldsListScreen(),
            ),
          ),

          // Monitor/Map Screen
          GoRoute(
            path: '/monitor',
            name: 'monitor',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: MapScreen(),
            ),
          ),

          // Market/Marketplace
          GoRoute(
            path: '/market',
            name: 'market',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: MarketplaceScreen(),
            ),
          ),

          // Profile
          GoRoute(
            path: '/profile',
            name: 'profile',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: ProfileScreen(),
            ),
          ),
        ],
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Field Details Routes (outside shell for full-screen experience)
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/field/:id',
        name: 'field-details',
        builder: (context, state) {
          final fieldId = state.pathParameters['id']!;
          return FieldDetailsScreen(fieldId: fieldId);
        },
      ),

      GoRoute(
        path: '/field/:id/dashboard',
        name: 'field-dashboard',
        builder: (context, state) {
          return const FieldDashboard();
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // VRA (Variable Rate Application) Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/vra',
        name: 'vra',
        builder: (context, state) => const VraListScreen(),
      ),

      GoRoute(
        path: '/vra/create',
        name: 'vra-create',
        builder: (context, state) => const VraCreateScreen(),
      ),

      GoRoute(
        path: '/vra/:id',
        name: 'vra-detail',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return VraDetailScreen(vraId: id);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // GDD (Growing Degree Days) Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/gdd',
        name: 'gdd',
        builder: (context, state) => const GddDashboardScreen(),
      ),

      GoRoute(
        path: '/gdd/settings',
        name: 'gdd-settings',
        builder: (context, state) => const GddSettingsScreen(),
      ),

      GoRoute(
        path: '/gdd/:fieldId',
        name: 'gdd-chart',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return GddChartScreen(fieldId: fieldId);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Spray Timing Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/spray',
        name: 'spray',
        builder: (context, state) => const SprayDashboardScreen(),
      ),

      GoRoute(
        path: '/spray/calendar',
        name: 'spray-calendar',
        builder: (context, state) => const SprayCalendarScreen(),
      ),

      GoRoute(
        path: '/spray/log',
        name: 'spray-log',
        builder: (context, state) => const SprayLogScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Crop Rotation Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/rotation',
        name: 'rotation',
        builder: (context, state) => const RotationCalendarScreen(),
      ),

      GoRoute(
        path: '/rotation/compatibility',
        name: 'rotation-compatibility',
        builder: (context, state) => const CropCompatibilityScreen(),
      ),

      GoRoute(
        path: '/rotation/:fieldId',
        name: 'rotation-plan',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return RotationPlanScreen(fieldId: fieldId);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Profitability Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/profitability',
        name: 'profitability',
        builder: (context, state) => const ProfitabilityDashboardScreen(),
      ),

      GoRoute(
        path: '/profitability/season',
        name: 'profitability-season',
        builder: (context, state) => const SeasonSummaryScreen(),
      ),

      GoRoute(
        path: '/profitability/:fieldId',
        name: 'profitability-detail',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return CropProfitabilityScreen(fieldId: fieldId);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Inventory Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/inventory',
        name: 'inventory',
        builder: (context, state) => const InventoryListScreen(),
      ),

      GoRoute(
        path: '/inventory/add',
        name: 'inventory-add',
        builder: (context, state) => const AddItemScreen(),
      ),

      GoRoute(
        path: '/inventory/:id',
        name: 'inventory-detail',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return ItemDetailScreen(itemId: id);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Chat / AI Advisor Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/chat',
        name: 'chat',
        builder: (context, state) => const ConversationsScreen(),
      ),

      GoRoute(
        path: '/chat/:conversationId',
        name: 'chat-conversation',
        builder: (context, state) {
          final conversationId = state.pathParameters['conversationId']!;
          return ChatScreen(conversationId: conversationId);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Satellite Imagery Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/satellite',
        name: 'satellite',
        builder: (context, state) => const SatelliteDashboardScreen(),
      ),

      GoRoute(
        path: '/satellite/phenology',
        name: 'satellite-phenology',
        builder: (context, state) => const PhenologyScreen(),
      ),

      GoRoute(
        path: '/satellite/weather',
        name: 'satellite-weather',
        builder: (context, state) => const sat_weather.WeatherScreen(fieldId: ''),
      ),

      GoRoute(
        path: '/satellite/:fieldId',
        name: 'satellite-field',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return NdviDetailScreen(fieldId: fieldId);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // AI Tools Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/advisor',
        name: 'advisor',
        builder: (context, state) => const AdvisorScreen(),
      ),

      GoRoute(
        path: '/scanner',
        name: 'scanner',
        builder: (context, state) => const ScannerScreen(),
      ),

      GoRoute(
        path: '/scouting',
        name: 'scouting',
        builder: (context, state) => const ScoutingScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Other Feature Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/weather',
        name: 'weather',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return WeatherScreen(fieldId: args?['fieldId'] ?? '');
        },
      ),

      GoRoute(
        path: '/tasks',
        name: 'tasks',
        builder: (context, state) => const TasksListScreen(),
      ),

      GoRoute(
        path: '/crop-health',
        name: 'crop-health',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return CropHealthDashboard(fieldId: args?['fieldId'] ?? '');
        },
      ),

      GoRoute(
        path: '/alerts',
        name: 'alerts',
        builder: (context, state) => const AlertsScreen(),
      ),

      GoRoute(
        path: '/notifications',
        name: 'notifications',
        builder: (context, state) => const NotificationsScreen(),
      ),

      GoRoute(
        path: '/map',
        name: 'map',
        builder: (context, state) => const MapScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Utility Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/sync',
        name: 'sync',
        builder: (context, state) => const SyncScreen(),
      ),
    ],

    // Error handling
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              'الصفحة غير موجودة',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 8),
            Text(
              state.uri.path,
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('العودة للرئيسية'),
            ),
          ],
        ),
      ),
    ),
  );
}
