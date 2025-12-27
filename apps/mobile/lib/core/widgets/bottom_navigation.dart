import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../constants/navigation_constants.dart';
import '../config/theme.dart';

/// Bottom Navigation Bar for SAHOOL App
/// شريط التنقل السفلي لتطبيق سهول
class SahoolBottomNavigation extends ConsumerWidget {
  final int currentIndex;
  final int? notificationCount;

  const SahoolBottomNavigation({
    super.key,
    required this.currentIndex,
    this.notificationCount,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
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
      child: SafeArea(
        child: NavigationBar(
          height: 70,
          elevation: 0,
          selectedIndex: currentIndex,
          onDestinationSelected: (index) => _onItemTapped(context, index),
          backgroundColor: Colors.white,
          indicatorColor: SahoolTheme.primary.withOpacity(0.1),
          labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
          destinations: _buildDestinations(),
        ),
      ),
    );
  }

  List<NavigationDestination> _buildDestinations() {
    return [
      // Home
      NavigationDestination(
        icon: Icon(NavigationConstants.getIcon('home')),
        selectedIcon: Icon(
          NavigationConstants.getIcon('home'),
          color: SahoolTheme.primary,
        ),
        label: NavigationConstants.getLabel('home'),
      ),

      // Fields
      NavigationDestination(
        icon: Icon(NavigationConstants.getIcon('fields')),
        selectedIcon: Icon(
          NavigationConstants.getIcon('fields'),
          color: SahoolTheme.primary,
        ),
        label: NavigationConstants.getLabel('fields'),
      ),

      // Monitor
      NavigationDestination(
        icon: Icon(NavigationConstants.getIcon('monitor')),
        selectedIcon: Icon(
          NavigationConstants.getIcon('monitor'),
          color: SahoolTheme.primary,
        ),
        label: NavigationConstants.getLabel('monitor'),
      ),

      // Market
      NavigationDestination(
        icon: Icon(NavigationConstants.getIcon('market')),
        selectedIcon: Icon(
          NavigationConstants.getIcon('market'),
          color: SahoolTheme.primary,
        ),
        label: NavigationConstants.getLabel('market'),
      ),

      // Profile
      NavigationDestination(
        icon: _buildProfileIcon(),
        selectedIcon: Icon(
          NavigationConstants.getIcon('profile'),
          color: SahoolTheme.primary,
        ),
        label: NavigationConstants.getLabel('profile'),
      ),
    ];
  }

  Widget _buildProfileIcon() {
    if (notificationCount != null && notificationCount! > 0) {
      return Badge(
        label: Text(
          notificationCount! > 9 ? '9+' : '$notificationCount',
          style: const TextStyle(fontSize: 10),
        ),
        child: Icon(NavigationConstants.getIcon('profile')),
      );
    }
    return Icon(NavigationConstants.getIcon('profile'));
  }

  void _onItemTapped(BuildContext context, int index) {
    switch (index) {
      case 0:
        context.go(NavigationConstants.home);
        break;
      case 1:
        context.go(NavigationConstants.fields);
        break;
      case 2:
        context.go(NavigationConstants.monitor);
        break;
      case 3:
        context.go(NavigationConstants.market);
        break;
      case 4:
        context.go(NavigationConstants.profile);
        break;
    }
  }
}

/// Provider for current navigation index
final currentNavigationIndexProvider = StateProvider<int>((ref) => 0);

/// Provider for notification count
final notificationCountProvider = StateProvider<int>((ref) => 0);
