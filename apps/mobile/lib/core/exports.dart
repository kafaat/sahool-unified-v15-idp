/// SAHOOL Core Exports
/// تصديرات الوحدات الأساسية
///
/// This file exports all core modules for easy import.
/// Use: import 'package:sahool_field_app/core/exports.dart';

// Animations - التحريكات
export 'animations/animations.dart';

// Config - التكوين
export 'config/theme.dart';
export 'config/env_config.dart';

// State Management - إدارة الحالة
export 'state/state_management.dart';

// UI Components - مكونات الواجهة
export 'ui/enhanced_widgets.dart' hide AnimatedListItem, ScaleIn, StaggeredAnimationList, HapticFeedbackType;

// Offline Support - دعم عدم الاتصال
export 'offline/offline.dart';
export 'offline/offline_ui_components.dart' hide SyncStatus;

// Performance - الأداء
export 'performance/performance_utils.dart';

// Notifications - الإشعارات
export 'notifications/notifications.dart';
export 'notifications/notification_ui_components.dart' hide NotificationBadge, NotificationAction, NotificationType;

// Localization - الترجمة
export 'l10n/locale_manager.dart';

// Error Handling - معالجة الأخطاء
export 'error/error.dart';

// Logging - التسجيل
export 'logging/logging.dart';

// Network - الشبكة
export 'sync/network_status.dart';

// Haptics - الردود اللمسية
export 'haptics/haptics.dart';

// Widgets - المكونات
export 'widgets/widgets.dart' hide SkeletonCard, SkeletonList, SkeletonGrid;
