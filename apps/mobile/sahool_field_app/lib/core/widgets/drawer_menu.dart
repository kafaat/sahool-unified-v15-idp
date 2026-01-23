import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants/navigation_constants.dart';
import '../config/theme.dart';

/// Navigation Drawer for SAHOOL App
/// القائمة الجانبية للتنقل في تطبيق سهول
class SahoolDrawerMenu extends ConsumerWidget {
  const SahoolDrawerMenu({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Drawer(
      child: Container(
        color: Colors.white,
        child: SafeArea(
          child: Column(
            children: [
              _buildHeader(context),
              Expanded(
                child: ListView(
                  padding: EdgeInsets.zero,
                  children: [
                    _buildMainNavigation(context),
                    const Divider(height: 1),
                    _buildFeatureGroups(context),
                    const Divider(height: 1),
                    _buildUtilities(context),
                    const SizedBox(height: 16),
                  ],
                ),
              ),
              _buildFooter(context),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topRight,
          end: Alignment.bottomLeft,
          colors: [
            SahoolTheme.primary,
            SahoolTheme.primary.withOpacity(0.8),
          ],
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 64,
                height: 64,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
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
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'مزرعة الخير',
                      style: TextStyle(
                        color: Colors.white.withOpacity(0.9),
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
              IconButton(
                icon: const Icon(Icons.edit_rounded, color: Colors.white),
                onPressed: () {
                  Navigator.pop(context);
                  context.push(NavigationConstants.profile);
                },
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _buildStatCard(context, '12', 'حقل'),
              const SizedBox(width: 12),
              _buildStatCard(context, '5', 'مهام نشطة'),
              const SizedBox(width: 12),
              _buildStatCard(context, '3', 'تنبيهات'),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatCard(BuildContext context, String value, String label) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.2),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Column(
          children: [
            Text(
              value,
              style: const TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                color: Colors.white.withOpacity(0.9),
                fontSize: 11,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMainNavigation(BuildContext context) {
    return Column(
      children: [
        _buildDrawerItem(
          context,
          key: 'home',
          route: NavigationConstants.home,
          isMain: true,
        ),
        _buildDrawerItem(
          context,
          key: 'fields',
          route: NavigationConstants.fields,
          isMain: true,
        ),
        _buildDrawerItem(
          context,
          key: 'monitor',
          route: NavigationConstants.monitor,
          isMain: true,
        ),
        _buildDrawerItem(
          context,
          key: 'market',
          route: NavigationConstants.market,
          isMain: true,
        ),
      ],
    );
  }

  Widget _buildFeatureGroups(BuildContext context) {
    return Column(
      children: NavigationConstants.featureGroups.map((group) {
        return _buildFeatureGroup(context, group);
      }).toList(),
    );
  }

  Widget _buildFeatureGroup(BuildContext context, FeatureGroup group) {
    return ExpansionTile(
      leading: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: SahoolTheme.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(
          group.icon,
          color: SahoolTheme.primary,
          size: 22,
        ),
      ),
      title: Text(
        NavigationConstants.getLabel(group.title),
        style: const TextStyle(
          fontWeight: FontWeight.w600,
          fontSize: 15,
        ),
      ),
      children: group.features.map((featureKey) {
        return _buildFeatureItem(context, featureKey);
      }).toList(),
    );
  }

  Widget _buildFeatureItem(BuildContext context, String featureKey) {
    final route = _getRouteForFeature(featureKey);
    return ListTile(
      contentPadding: const EdgeInsets.only(left: 24, right: 72),
      leading: Container(
        width: 36,
        height: 36,
        decoration: BoxDecoration(
          color: NavigationConstants.getColor(featureKey).withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(
          NavigationConstants.getIcon(featureKey),
          color: NavigationConstants.getColor(featureKey),
          size: 20,
        ),
      ),
      title: Text(
        NavigationConstants.getLabel(featureKey),
        style: const TextStyle(fontSize: 14),
      ),
      onTap: () {
        Navigator.pop(context);
        if (route != null) {
          context.push(route);
        }
      },
    );
  }

  Widget _buildDrawerItem(
    BuildContext context, {
    required String key,
    required String route,
    bool isMain = false,
    String? badge,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 4),
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: isMain
              ? SahoolTheme.primary.withOpacity(0.1)
              : NavigationConstants.getColor(key).withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          NavigationConstants.getIcon(key),
          color: isMain
              ? SahoolTheme.primary
              : NavigationConstants.getColor(key),
          size: 24,
        ),
      ),
      title: Text(
        NavigationConstants.getLabel(key),
        style: const TextStyle(
          fontWeight: FontWeight.w600,
          fontSize: 15,
        ),
      ),
      trailing: badge != null
          ? Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                badge,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            )
          : Icon(
              Icons.chevron_left_rounded,
              color: Colors.grey[400],
            ),
      onTap: () {
        Navigator.pop(context);
        context.go(route);
      },
    );
  }

  Widget _buildUtilities(BuildContext context) {
    return Column(
      children: [
        const Padding(
          padding: EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          child: Align(
            alignment: Alignment.centerRight,
            child: Text(
              'أدوات مساعدة',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: Colors.grey,
              ),
            ),
          ),
        ),
        _buildUtilityItem(
          context,
          icon: Icons.notifications_rounded,
          title: NavigationConstants.getLabel('notifications'),
          route: NavigationConstants.notifications,
          badge: '3',
        ),
        _buildUtilityItem(
          context,
          icon: Icons.sync_rounded,
          title: NavigationConstants.getLabel('sync'),
          route: NavigationConstants.sync,
        ),
        _buildUtilityItem(
          context,
          icon: Icons.settings_rounded,
          title: NavigationConstants.getLabel('settings'),
          route: NavigationConstants.settings,
        ),
        _buildUtilityItem(
          context,
          icon: Icons.help_rounded,
          title: NavigationConstants.getLabel('help'),
          route: '/help',
        ),
        _buildUtilityItem(
          context,
          icon: Icons.info_rounded,
          title: NavigationConstants.getLabel('about'),
          route: '/about',
        ),
      ],
    );
  }

  Widget _buildUtilityItem(
    BuildContext context, {
    required IconData icon,
    required String title,
    required String route,
    String? badge,
  }) {
    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 20),
      leading: Icon(icon, color: Colors.grey[700], size: 22),
      title: Text(
        title,
        style: const TextStyle(fontSize: 14),
      ),
      trailing: badge != null
          ? Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.red,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                badge,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
              ),
            )
          : Icon(
              Icons.chevron_left_rounded,
              color: Colors.grey[400],
            ),
      onTap: () {
        Navigator.pop(context);
        context.push(route);
      },
    );
  }

  Widget _buildFooter(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(color: Colors.grey[200]!),
        ),
      ),
      child: ListTile(
        contentPadding: EdgeInsets.zero,
        leading: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: Colors.red.withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: const Icon(
            Icons.logout_rounded,
            color: Colors.red,
          ),
        ),
        title: Text(
          NavigationConstants.getLabel('logout'),
          style: const TextStyle(
            color: Colors.red,
            fontWeight: FontWeight.w600,
          ),
        ),
        onTap: () {
          _showLogoutDialog(context);
        },
      ),
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('تسجيل الخروج'),
          content: const Text('هل أنت متأكد من تسجيل الخروج؟'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                Navigator.pop(context);
                context.go(NavigationConstants.login);
              },
              child: const Text(
                'تسجيل الخروج',
                style: TextStyle(color: Colors.red),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String? _getRouteForFeature(String featureKey) {
    final routeMap = {
      'vra': NavigationConstants.vra,
      'gdd': NavigationConstants.gdd,
      'spray': NavigationConstants.spray,
      'rotation': NavigationConstants.rotation,
      'profitability': NavigationConstants.profitability,
      'fields': NavigationConstants.fields,
      'tasks': NavigationConstants.tasks,
      'crop_health': NavigationConstants.cropHealth,
      'satellite': NavigationConstants.satellite,
      'weather': NavigationConstants.weather,
      'alerts': NavigationConstants.alerts,
      'map': NavigationConstants.map,
      'inventory': NavigationConstants.inventory,
      'market': NavigationConstants.market,
      'chat': NavigationConstants.chat,
      'advisor': NavigationConstants.advisor,
      'scanner': NavigationConstants.scanner,
      'scouting': NavigationConstants.scouting,
    };
    return routeMap[featureKey];
  }
}
