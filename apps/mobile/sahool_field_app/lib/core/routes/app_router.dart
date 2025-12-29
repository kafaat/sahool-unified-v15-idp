import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Features
import '../../features/splash/ui/splash_screen.dart';
import '../../features/auth/ui/role_selection_screen.dart';
import '../../features/auth/ui/login_screen.dart';
import '../../features/main_layout/main_layout.dart';
import '../../features/map_home/ui/map_screen.dart';
import '../../features/fields/presentation/screens/fields_list_screen.dart';
import '../../features/fields/presentation/screens/field_details_screen.dart';
import '../../features/field_hub/ui/field_dashboard.dart';
import '../../features/alerts/ui/alerts_screen.dart';
import '../../features/profile/ui/profile_screen.dart';
import '../../features/advisor/ui/advisor_screen.dart';
import '../../features/scanner/ui/scanner_screen.dart';
import '../../features/scouting/ui/scouting_screen.dart';
import '../../features/sync/ui/sync_screen.dart';
import '../../features/ecological_records/presentation/screens/ecological_dashboard_screen.dart';
import '../../features/ecological_records/presentation/screens/biodiversity_record_screen.dart';
import '../../features/ecological_records/presentation/screens/soil_health_record_screen.dart';
import '../../features/ecological_records/presentation/screens/water_record_screen.dart';
import '../../features/ecological_records/presentation/screens/practice_record_screen.dart';

/// SAHOOL App Router Configuration
/// تكوين مسارات التطبيق باستخدام go_router
class AppRouter {
  static final GlobalKey<NavigatorState> _rootNavigatorKey =
      GlobalKey<NavigatorState>(debugLabel: 'root');
  static final GlobalKey<NavigatorState> _shellNavigatorKey =
      GlobalKey<NavigatorState>(debugLabel: 'shell');

  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/splash',
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
          // Map Screen (Home)
          GoRoute(
            path: '/map',
            name: 'map',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: MapScreen(),
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

          // Alerts
          GoRoute(
            path: '/alerts',
            name: 'alerts',
            pageBuilder: (context, state) => const NoTransitionPage(
              child: AlertsScreen(),
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
      // Utility Routes
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/sync',
        name: 'sync',
        builder: (context, state) => const SyncScreen(),
      ),

      // ═══════════════════════════════════════════════════════════════════════
      // Ecological Records Routes
      // مسارات السجلات البيئية
      // ═══════════════════════════════════════════════════════════════════════

      GoRoute(
        path: '/ecological',
        name: 'ecological-dashboard',
        builder: (context, state) => const EcologicalDashboardScreen(),
      ),

      GoRoute(
        path: '/ecological/biodiversity',
        name: 'biodiversity-record',
        builder: (context, state) => const BiodiversityRecordScreen(),
      ),

      GoRoute(
        path: '/ecological/soil-health',
        name: 'soil-health-record',
        builder: (context, state) => const SoilHealthRecordScreen(),
      ),

      GoRoute(
        path: '/ecological/water',
        name: 'water-record',
        builder: (context, state) => const WaterRecordScreen(),
      ),

      GoRoute(
        path: '/ecological/practice',
        name: 'practice-record',
        builder: (context, state) => const PracticeRecordScreen(),
      ),

      // Field-specific ecological dashboard
      GoRoute(
        path: '/field/:id/ecological',
        name: 'field-ecological',
        builder: (context, state) {
          final fieldId = state.pathParameters['id']!;
          return EcologicalDashboardScreen(fieldId: fieldId);
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
              onPressed: () => context.go('/map'),
              child: const Text('العودة للرئيسية'),
            ),
          ],
        ),
      ),
    ),
  );
}
