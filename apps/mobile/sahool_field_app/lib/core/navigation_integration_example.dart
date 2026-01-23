/// NAVIGATION INTEGRATION EXAMPLES
/// أمثلة على دمج نظام التنقل
///
/// This file provides examples of how to use the new navigation system
/// in your Flutter app.

import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

// Import navigation components
import 'constants/navigation_constants.dart';
import 'widgets/feature_grid.dart';
import 'widgets/drawer_menu.dart';
import 'widgets/bottom_navigation.dart';

// ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 1: Home Screen with Feature Grid
// ═══════════════════════════════════════════════════════════════════════

class HomeScreenExample extends StatelessWidget {
  const HomeScreenExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('سهول'),
          actions: [
            IconButton(
              icon: const Icon(Icons.notifications_outlined),
              onPressed: () => context.push(NavigationConstants.notifications),
            ),
          ],
        ),
        drawer: const SahoolDrawerMenu(),
        body: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Welcome Header
              _buildWelcomeHeader(context),

              const SizedBox(height: 24),

              // Quick Actions
              _buildQuickActions(context),

              const SizedBox(height: 24),

              // Precision Agriculture Features
              FeatureSection(
                title: 'الزراعة الدقيقة',
                subtitle: 'أدوات متقدمة لتحسين الإنتاج',
                icon: Icons.agriculture_rounded,
                features: const [
                  FeatureItem(key: 'vra', route: '/vra'),
                  FeatureItem(key: 'gdd', route: '/gdd'),
                  FeatureItem(key: 'spray', route: '/spray'),
                  FeatureItem(key: 'rotation', route: '/rotation'),
                  FeatureItem(key: 'profitability', route: '/profitability'),
                ],
                onViewAll: () => context.push('/features/precision'),
              ),

              const SizedBox(height: 24),

              // All Features Grid
              const Padding(
                padding: EdgeInsets.symmetric(horizontal: 16),
                child: Text(
                  'جميع الميزات',
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const FeatureGrid(),

              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildWelcomeHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [Colors.green.shade700, Colors.green.shade500],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'مرحباً بك، أحمد',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'لديك 5 مهام اليوم',
            style: TextStyle(
              fontSize: 16,
              color: Colors.white.withOpacity(0.9),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        children: [
          QuickActionCard(
            title: 'المهام النشطة',
            subtitle: 'عرض جميع المهام المطلوبة اليوم',
            icon: Icons.checklist_rounded,
            color: Colors.blue,
            badge: '5',
            onTap: () => context.push(NavigationConstants.tasks),
          ),
          const SizedBox(height: 12),
          QuickActionCard(
            title: 'التنبيهات',
            subtitle: 'تحقق من التنبيهات الهامة',
            icon: Icons.notifications_active_rounded,
            color: Colors.orange,
            badge: '3',
            onTap: () => context.push(NavigationConstants.alerts),
          ),
          const SizedBox(height: 12),
          QuickActionCard(
            title: 'المستشار الذكي',
            subtitle: 'احصل على استشارة فورية',
            icon: Icons.chat_bubble_rounded,
            color: Colors.cyan,
            onTap: () => context.push(NavigationConstants.chat),
          ),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 2: Using Navigation Constants
// ═══════════════════════════════════════════════════════════════════════

class NavigationExample extends StatelessWidget {
  const NavigationExample({super.key});

  void _navigateToFeature(BuildContext context, String feature) {
    // Navigate to any feature using constants
    switch (feature) {
      case 'vra':
        context.push(NavigationConstants.vra);
        break;
      case 'gdd':
        context.push(NavigationConstants.gdd);
        break;
      case 'spray':
        context.push(NavigationConstants.spray);
        break;
      case 'rotation':
        context.push(NavigationConstants.rotation);
        break;
      case 'profitability':
        context.push(NavigationConstants.profitability);
        break;
      case 'inventory':
        context.push(NavigationConstants.inventory);
        break;
      case 'chat':
        context.push(NavigationConstants.chat);
        break;
      case 'satellite':
        context.push(NavigationConstants.satellite);
        break;
    }
  }

  void _navigateWithParameters(BuildContext context) {
    // Navigate with path parameters
    final fieldId = '123';

    // GDD for specific field
    context.push('/gdd/$fieldId');

    // VRA detail
    context.push('/vra/456');

    // Satellite for specific field
    context.push('/satellite/$fieldId');

    // Chat conversation
    context.push('/chat/conversation-789');
  }

  @override
  Widget build(BuildContext context) {
    return Container();
  }
}

// ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 3: Using Bottom Navigation with Badge
// ═══════════════════════════════════════════════════════════════════════

class BadgeExample extends ConsumerWidget {
  const BadgeExample({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Update notification count from your data source
    Future<void> updateNotificationCount() async {
      // Fetch from API or local database
      final count = 5; // Example count
      ref.read(notificationCountProvider.notifier).state = count;
    }

    return ElevatedButton(
      onPressed: updateNotificationCount,
      child: const Text('Update Notifications'),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 4: Custom Feature Section
// ═══════════════════════════════════════════════════════════════════════

class CustomFeatureSectionExample extends StatelessWidget {
  const CustomFeatureSectionExample({super.key});

  @override
  Widget build(BuildContext context) {
    return FeatureSection(
      title: 'إدارة الحقول',
      subtitle: 'تتبع وإدارة جميع حقولك',
      icon: Icons.landscape_rounded,
      features: const [
        FeatureItem(
          key: 'fields',
          route: '/fields',
        ),
        FeatureItem(
          key: 'satellite',
          route: '/satellite',
        ),
        FeatureItem(
          key: 'crop_health',
          route: '/crop-health',
        ),
        FeatureItem(
          key: 'weather',
          route: '/weather',
        ),
      ],
      onViewAll: () => context.push('/features/field-management'),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 5: Accessing Labels and Icons Programmatically
// ═══════════════════════════════════════════════════════════════════════

class DynamicFeatureExample extends StatelessWidget {
  const DynamicFeatureExample({super.key});

  @override
  Widget build(BuildContext context) {
    return ListView(
      children: [
        _buildFeatureItem('vra'),
        _buildFeatureItem('gdd'),
        _buildFeatureItem('spray'),
        _buildFeatureItem('rotation'),
      ],
    );
  }

  Widget _buildFeatureItem(String featureKey) {
    return ListTile(
      leading: Icon(
        NavigationConstants.getIcon(featureKey),
        color: NavigationConstants.getColor(featureKey),
      ),
      title: Text(NavigationConstants.getLabel(featureKey)),
      subtitle: Text(
        NavigationConstants.arabicLabels['${featureKey}_desc'] ?? '',
      ),
      onTap: () {
        // Handle tap
      },
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// EXAMPLE 6: Using Drawer Menu
// ═══════════════════════════════════════════════════════════════════════

class DrawerExample extends StatelessWidget {
  const DrawerExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('سهول'),
        // Menu icon automatically added by Scaffold when drawer is present
      ),
      drawer: const SahoolDrawerMenu(), // Simply add the drawer
      body: const Center(
        child: Text('Main Content'),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════
// USAGE NOTES
// ═══════════════════════════════════════════════════════════════════════

/*
1. NAVIGATION ROUTES
   - All routes are defined in NavigationConstants
   - Use context.push() or context.go() with route constants
   - Parameters are passed via path: '/vra/:id' or '/gdd/:fieldId'

2. ARABIC LABELS
   - All labels are in NavigationConstants.arabicLabels
   - Access via NavigationConstants.getLabel('key')
   - Supports RTL text direction automatically

3. FEATURE ICONS
   - Icons defined in NavigationConstants.featureIcons
   - Access via NavigationConstants.getIcon('key')
   - Each feature has a unique color in featureColors

4. BOTTOM NAVIGATION
   - 5 main tabs: Home, Fields, Monitor, Market, Profile
   - Supports badge indicators for notifications
   - Auto-highlights current route

5. DRAWER MENU
   - Features organized by category
   - User profile section at top
   - Expandable sections for feature groups
   - Settings and logout at bottom

6. FEATURE GRID
   - Displays feature cards in grid or horizontal list
   - Compact mode for smaller spaces
   - Automatic icon and color from constants

7. PROVIDERS
   - notificationCountProvider: for badge count
   - currentNavigationIndexProvider: for active tab

8. INTEGRATION
   - Import required components
   - Wrap with Directionality for RTL
   - Use SahoolDrawerMenu and SahoolBottomNavigation
   - FeatureGrid and FeatureSection for content
*/
