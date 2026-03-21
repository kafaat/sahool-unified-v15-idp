/// SAHOOL Core Module
/// الوحدة الأساسية للتطبيق
///
/// تصدير جميع مكونات النواة في مكان واحد

// Configuration
export 'config/env_config.dart';
export 'config/config.dart';

// Theme
export 'theme/sahool_theme.dart';

// Utilities
export 'utils/app_logger.dart';

// Logging (Structured Logging System)
export 'logging/logging.dart' hide LogLevel, LoggerMixin;

// Widgets
export 'widgets/widgets.dart';

// HTTP
export 'http/api_client.dart';

// Network
export 'network/api_result.dart';

// Sync
export 'sync/sync_engine.dart';
export 'sync/network_status.dart';

// Auth
export 'auth/auth_service.dart';
export 'auth/secure_storage_service.dart';
export 'auth/biometric_service.dart';

// Performance
export 'performance/performance.dart';
export 'performance/performance_utils.dart' hide MemoryInfo;

// Map
export 'map/map.dart' hide CacheStats;

// Notifications
export 'notifications/notifications.dart';
export 'notifications/notification_ui_components.dart' hide NotificationBadge, NotificationAction, NotificationType, NotificationListItem;

// Offline Sync
export 'offline/offline.dart' hide SyncStatus, SyncResult;
export 'offline/offline_ui_components.dart' hide SyncStatus;

// Voice Commands
export 'voice/voice.dart';

// Deep Linking
export 'deeplink/deeplink_handler.dart';

// State Management - إدارة الحالة
export 'state/state_management.dart';

// UI Components - مكونات الواجهة المحسنة
export 'ui/enhanced_widgets.dart' hide ConnectivityBanner, AnimatedListItem, SahoolRefreshIndicator, ScaleIn, SlideIn;

// Localization - الترجمة
export 'l10n/locale_manager.dart';

// Animations - التحريكات
export 'animations/animations.dart' hide SkeletonCard, SkeletonList, SkeletonGrid;
