import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Core
import '../constants/navigation_constants.dart';

// Features - Auth & Onboarding
import '../../features/splash/ui/splash_screen.dart';
import '../../features/auth/ui/role_selection_screen.dart';
import '../../features/auth/ui/login_screen.dart';
import '../../features/auth/ui/forgot_password_screen.dart';
import '../../features/auth/ui/reset_password_screen.dart';
import '../../features/auth/ui/biometric_settings_screen.dart';

// Features - Main Layout
import '../../features/main_layout/main_layout.dart';
import '../../features/home/presentation/screens/home_dashboard.dart';

// Features - Field Management
import '../../features/map_home/ui/map_screen.dart';
import '../../features/fields/presentation/screens/fields_list_screen.dart';
import '../../features/fields/presentation/screens/field_details_screen.dart';
import '../../features/fields/domain/entities/field_entity.dart';
import '../../features/field/ui/field_form_screen.dart';
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
import '../../features/satellite/presentation/screens/weather_screen.dart'
    as sat_weather;

// Features - Other
import '../../features/alerts/ui/alerts_screen.dart';
import '../../features/profile/ui/profile_screen.dart';
import '../../features/sync/ui/sync_screen.dart';
import '../../features/weather/presentation/screens/weather_screen.dart';
import '../../features/tasks/presentation/tasks_list_screen.dart';
import '../../features/crop_health/presentation/screens/crop_health_dashboard.dart';
import '../../features/notifications/presentation/screens/notifications_screen.dart';
import '../../features/marketplace/marketplace_screen.dart';

// Features - Astronomical Calendar
import '../../features/astronomical/presentation/screens/astronomical_screen.dart';

// Features - Pivot Irrigation - الري المحوري
import '../../features/pivot_irrigation/pivot_irrigation.dart';

// Note: crops and gamification features don't have screens in sahool_field_app

// Features - IoT
import '../../features/iot/ui/iot_control_screen.dart';

// Features - Lab (Sample Tracking)
import '../../features/lab/ui/sample_tracking_screen.dart';

// Features - Offline Maps
import '../../features/maps/presentation/screens/field_map_screen.dart';

// Features - Onboarding
import '../../features/onboarding/ui/onboarding_screen.dart';

// Features - Payment & Wallet
import '../../features/payment/presentation/payment_screen.dart';
import '../../features/wallet/wallet_screen.dart';

// Features - Research
import '../../features/research/ui/experiments_list_screen.dart';
import '../../features/research/ui/researcher_task_screen.dart';
import '../../features/research/ui/daily_observation_screen.dart';

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
    debugLogDiagnostics: kDebugMode, // Only enable in debug builds

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

      GoRoute(
        path: '/forgot-password',
        name: 'forgot-password',
        builder: (context, state) => const ForgotPasswordScreen(),
      ),

      GoRoute(
        path: '/reset-password',
        name: 'reset-password',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return ResetPasswordScreen(
            token: args?['token'] ?? '',
            identifier: args?['identifier'],
          );
        },
      ),

      GoRoute(
        path: '/biometric-settings',
        name: 'biometric-settings',
        builder: (context, state) => const BiometricSettingsScreen(),
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
        path: '/fields/create',
        name: 'field-create',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return FieldFormScreen(
            tenantId: args?['tenantId'] as String?,
          );
        },
      ),

      GoRoute(
        path: '/field/:id',
        name: 'field-details',
        builder: (context, state) {
          final fieldId = state.pathParameters['id']!;
          final field = state.extra as FieldEntity?;
          return FieldDetailsScreen(field: field, fieldId: fieldId);
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
        builder: (context, state) => const VRAListScreen(),
      ),

      GoRoute(
        path: '/vra/create',
        name: 'vra-create',
        builder: (context, state) => const VRACreateScreen(),
      ),

      GoRoute(
        path: '/vra/:id',
        name: 'vra-detail',
        builder: (context, state) {
          final id = state.pathParameters['id']!;
          return VRADetailScreen(prescriptionId: id);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // GDD (Growing Degree Days) Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/gdd',
        name: 'gdd',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return GDDDashboardScreen(
            fieldId: args?['fieldId'] ?? '',
            fieldName: args?['fieldName'],
          );
        },
      ),

      GoRoute(
        path: '/gdd/settings',
        name: 'gdd-settings',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return GDDSettingsScreen(fieldId: args?['fieldId'] ?? '');
        },
      ),

      GoRoute(
        path: '/gdd/:fieldId',
        name: 'gdd-chart',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return GDDChartScreen(fieldId: fieldId);
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Spray Timing Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/spray',
        name: 'spray',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return SprayDashboardScreen(fieldId: args?['fieldId'] ?? '');
        },
      ),

      GoRoute(
        path: '/spray/calendar',
        name: 'spray-calendar',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return SprayCalendarScreen(fieldId: args?['fieldId'] ?? '');
        },
      ),

      GoRoute(
        path: '/spray/log',
        name: 'spray-log',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return SprayLogScreen(fieldId: args?['fieldId'] ?? '');
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Crop Rotation Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/rotation',
        name: 'rotation',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return RotationCalendarScreen(fieldId: args?['fieldId']);
        },
      ),

      GoRoute(
        path: '/rotation/compatibility',
        name: 'rotation-compatibility',
        builder: (context, state) => const CropCompatibilityScreen(),
      ),

      GoRoute(
        path: '/rotation/:fieldId/plan',
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
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return ProfitabilityDashboardScreen(
            farmId: args?['farmId'] ?? '',
            season: args?['season'] ?? '',
          );
        },
      ),

      GoRoute(
        path: '/profitability/season',
        name: 'profitability-season',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return SeasonSummaryScreen(
            farmId: args?['farmId'] ?? '',
            season: args?['season'] ?? '',
          );
        },
      ),

      GoRoute(
        path: '/profitability/:fieldId',
        name: 'profitability-detail',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return CropProfitabilityScreen(profitabilityId: fieldId);
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
        builder: (context, state) => SatelliteDashboardScreen(
          fieldId: state.uri.queryParameters['fieldId'] ?? '',
          fieldName: state.uri.queryParameters['fieldName'] ?? '',
        ),
      ),

      GoRoute(
        path: '/satellite/phenology',
        name: 'satellite-phenology',
        builder: (context, state) => PhenologyScreen(
          fieldId: state.uri.queryParameters['fieldId'] ?? '',
          fieldName: state.uri.queryParameters['fieldName'] ?? '',
        ),
      ),

      GoRoute(
        path: '/satellite/weather',
        name: 'satellite-weather',
        builder: (context, state) => sat_weather.WeatherScreen(
          fieldId: state.uri.queryParameters['fieldId'] ?? '',
          fieldName: state.uri.queryParameters['fieldName'] ?? '',
        ),
      ),

      GoRoute(
        path: '/satellite/:fieldId',
        name: 'satellite-field',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return NdviDetailScreen(
            fieldId: fieldId,
            fieldName: state.uri.queryParameters['fieldName'] ?? '',
          );
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

      // ═══════════════════════════════════════════════════════════════════════
      // Astronomical Calendar Route - التقويم الفلكي
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/astronomical',
        name: 'astronomical',
        builder: (context, state) => const AstronomicalScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Pivot Irrigation Routes - مسارات الري المحوري
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: NavigationConstants.pivotIrrigation,
        name: 'pivot-irrigation',
        builder: (context, state) => const PivotDashboardScreen(
          pivotId: 'default',
          fieldId: 'default',
        ),
      ),

      GoRoute(
        path: '/pivot-irrigation/:pivotId',
        name: 'pivot-dashboard',
        builder: (context, state) {
          final pivotId = state.pathParameters['pivotId']!;
          final fieldId = state.uri.queryParameters['fieldId'] ?? 'default';
          return PivotDashboardScreen(pivotId: pivotId, fieldId: fieldId);
        },
      ),

      GoRoute(
        path: '/pivot-irrigation/setup/:fieldId',
        name: 'pivot-setup',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          return PivotSetupScreen(
            fieldId: fieldId,
            onSave: (config) {
              context.pop();
            },
          );
        },
      ),

      GoRoute(
        path: '/pivot-irrigation/:pivotId/sectors',
        name: 'pivot-sectors',
        builder: (context, state) {
          final pivotId = state.pathParameters['pivotId']!;
          // Create a default configuration for direct navigation
          final defaultConfig = PivotConfiguration(
            id: pivotId,
            fieldId: 'default',
            name: 'Pivot $pivotId',
            centerLat: 0,
            centerLng: 0,
            lengthMeters: 400,
            spansCount: 7,
            areaHectares: 50.0,
            flowRateLph: 450000,
          );
          return SectorManagementScreen(
            pivotConfig: defaultConfig,
            onConfigUpdate: (_) {
              context.pop();
            },
          );
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // IoT Route - التحكم بأجهزة إنترنت الأشياء
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/iot',
        name: 'iot',
        builder: (context, state) => const IoTControlScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Lab Route - تتبع العينات المخبرية
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/lab',
        name: 'lab',
        builder: (context, state) => const SampleTrackingScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Offline Maps Route - الخرائط غير المتصلة
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/maps/:fieldId',
        name: 'maps',
        builder: (context, state) {
          final fieldId = state.pathParameters['fieldId']!;
          final args = state.extra as Map<String, dynamic>?;
          return FieldMapScreen(
            fieldId: fieldId,
            fieldName: args?['fieldName'] as String?,
            initialCenter: args?['initialCenter'] as Map<String, dynamic>?,
          );
        },
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Onboarding Route - مسار التعريف بالتطبيق
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        builder: (context, state) => const OnboardingScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Payment & Wallet Routes - الدفع والمحفظة
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/payment/:walletId',
        name: 'payment',
        builder: (context, state) {
          final walletId = state.pathParameters['walletId']!;
          return PaymentScreen(walletId: walletId);
        },
      ),

      GoRoute(
        path: '/wallet',
        name: 'wallet',
        builder: (context, state) => const WalletScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Research Routes - التجارب البحثية
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/research',
        name: 'research',
        builder: (context, state) => const ExperimentsListScreen(),
      ),

      GoRoute(
        path: '/research/task',
        name: 'research-task',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return ResearcherTaskScreen(
            taskId: args?['taskId'] as String?,
            plotCode: args?['plotCode'] as String?,
            experimentName: args?['experimentName'] as String?,
          );
        },
      ),

      GoRoute(
        path: '/research/observation',
        name: 'research-observation',
        builder: (context, state) {
          final args = state.extra as Map<String, dynamic>?;
          return DailyObservationScreen(
            experimentId: args?['experimentId'] as String?,
            plotCode: args?['plotCode'] as String?,
          );
        },
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
