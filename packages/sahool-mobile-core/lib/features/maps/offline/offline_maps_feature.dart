/// Offline Maps Feature - ميزة الخرائط المحلية
///
/// Provides UI components for managing offline maps:
/// - Screens for downloading and managing regions
/// - Widgets for progress display and storage management
///
/// Usage:
/// ```dart
/// import 'package:sahool_mobile_core/features/maps/offline/offline_maps_feature.dart';
///
/// // Navigate to offline regions management
/// Navigator.push(
///   context,
///   MaterialPageRoute(builder: (_) => const OfflineRegionsScreen()),
/// );
/// ```
library;

// Screens
export 'screens/offline_regions_screen.dart';
export 'screens/download_region_screen.dart';
export 'screens/download_progress_screen.dart';

// Widgets
export 'widgets/region_card.dart';
export 'widgets/download_progress_indicator.dart';
export 'widgets/storage_usage_bar.dart';
export 'widgets/region_selector.dart';
