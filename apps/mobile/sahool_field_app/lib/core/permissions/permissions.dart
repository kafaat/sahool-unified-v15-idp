/// SAHOOL Runtime Permissions Module
/// نظام صلاحيات التشغيل للأندرويد 6.0+ و iOS
///
/// This module provides comprehensive runtime permission handling
/// for Android 6.0+ (API 23+) and iOS.
///
/// Features:
/// - Location permission management
/// - Camera permission management
/// - Storage/Photos permission management
/// - Notification permission management
/// - Permission status tracking with Riverpod
/// - Reusable permission UI widgets
/// - Permission rationale dialogs
/// - Settings navigation for permanently denied permissions
///
/// Setup Required:
/// 1. Add permission_handler: ^11.3.1 to pubspec.yaml
/// 2. Configure Android permissions in AndroidManifest.xml
/// 3. Configure iOS permissions in Info.plist
/// 4. Uncomment TODO sections in permission_service.dart
///
/// See README.md for detailed setup instructions.

library permissions;

// Core service
export 'permission_service.dart';

// State management
export 'permission_provider.dart';

// UI widgets
export 'permission_widgets.dart';
