/// Core Routing Exports
///
/// This file provides a single entry point for all routing-related functionality.
/// Import this file to access app router and deep link handling.
///
/// Example:
/// ```dart
/// import 'package:sahool_field_app/core/routing/routing.dart';
///
/// // Initialize router and deep links
/// await AppRouter.initializeDeepLinks();
///
/// // Use router in MaterialApp
/// MaterialApp.router(
///   routerConfig: AppRouter.router,
///   ...
/// );
/// ```

library routing;

export 'app_router.dart';
export 'deep_link_handler.dart';
