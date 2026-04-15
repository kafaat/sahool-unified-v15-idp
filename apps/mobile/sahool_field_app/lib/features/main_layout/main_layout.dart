import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/auth/auth_service.dart';
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

    // Listen for session expiry / forced logout and redirect to login
    ref.listen<AuthState>(authStateProvider, (previous, next) {
      if (previous?.status == next.status) return;
      if (next.status == AuthStatus.sessionExpired ||
          (previous?.status == AuthStatus.authenticated &&
              next.status == AuthStatus.unauthenticated)) {
        final router = GoRouter.of(context);
        final reason = next.error ?? 'انتهت صلاحية الجلسة';
        WidgetsBinding.instance.addPostFrameCallback((_) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(reason),
              backgroundColor: Colors.orange,
              behavior: SnackBarBehavior.floating,
            ),
          );
          router.go('/login');
        });
      }
    });

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        drawer: const SahoolDrawerMenu(),
        body: child,
        bottomNavigationBar: SahoolBottomNavigation(
          currentIndex: currentIndex,
          notificationCount: notificationCount,
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
