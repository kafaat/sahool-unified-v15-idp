import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/config/theme.dart';
import '../../core/widgets/bottom_navigation.dart';
import '../../core/widgets/drawer_menu.dart';

/// Main Layout - الهيكل الرئيسي مع شريط التنقل السفلي
class MainLayout extends ConsumerWidget {
  final Widget child;

  const MainLayout({super.key, required this.child});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentIndex = _calculateSelectedIndex(context);
    final notificationCount = ref.watch(notificationCountProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        drawer: const SahoolDrawerMenu(),
        body: child,
        bottomNavigationBar: SahoolBottomNavigation(
          currentIndex: currentIndex,
          notificationCount: notificationCount,
        ),
        floatingActionButton: _buildFAB(context, currentIndex),
        floatingActionButtonLocation: FloatingActionButtonLocation.endFloat,
      ),
    );
  }

  /// Builds FAB based on current tab
  /// زر الإجراء العائم حسب الشاشة الحالية
  Widget? _buildFAB(BuildContext context, int currentIndex) {
    switch (currentIndex) {
      case 0: // Home - quick actions
        return FloatingActionButton(
          onPressed: () => _showQuickActions(context),
          backgroundColor: SahoolTheme.primary,
          child: const Icon(Icons.add, color: Colors.white, size: 28),
        );
      default:
        return null;
    }
  }

  /// Shows quick action bottom sheet with real navigation
  /// عرض الإجراءات السريعة مع التنقل الفعلي
  void _showQuickActions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (sheetContext) => Directionality(
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
                  style: Theme.of(sheetContext).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _buildQuickActionItem(
                      context: context,
                      sheetContext: sheetContext,
                      icon: Icons.camera_alt_rounded,
                      label: 'تصوير',
                      color: SahoolTheme.info,
                      route: '/scanner',
                    ),
                    _buildQuickActionItem(
                      context: context,
                      sheetContext: sheetContext,
                      icon: Icons.add_location_rounded,
                      label: 'حقل جديد',
                      color: SahoolTheme.success,
                      route: '/field-form',
                    ),
                    _buildQuickActionItem(
                      context: context,
                      sheetContext: sheetContext,
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
                      context: context,
                      sheetContext: sheetContext,
                      icon: Icons.water_drop_rounded,
                      label: 'تسجيل ري',
                      color: Colors.blue,
                      route: '/irrigation',
                    ),
                    _buildQuickActionItem(
                      context: context,
                      sheetContext: sheetContext,
                      icon: Icons.eco_rounded,
                      label: 'تسجيل تسميد',
                      color: Colors.green,
                      route: '/spray',
                    ),
                    _buildQuickActionItem(
                      context: context,
                      sheetContext: sheetContext,
                      icon: Icons.bug_report_rounded,
                      label: 'تقرير مشكلة',
                      color: Colors.red,
                      route: '/alerts',
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
    required BuildContext context,
    required BuildContext sheetContext,
    required IconData icon,
    required String label,
    required Color color,
    required String route,
  }) {
    return InkWell(
      onTap: () {
        Navigator.pop(sheetContext); // Close bottom sheet
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

  int _calculateSelectedIndex(BuildContext context) {
    final location = GoRouterState.of(context).uri.path;
    if (location.startsWith('/home')) return 0;
    if (location.startsWith('/fields')) return 1;
    if (location.startsWith('/monitor')) return 2;
    if (location.startsWith('/market')) return 3;
    if (location.startsWith('/profile')) return 4;
    return 0;
  }
}

