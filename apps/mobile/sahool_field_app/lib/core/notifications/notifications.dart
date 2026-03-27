/// SAHOOL Notifications Core
/// ملفات الإشعارات الأساسية
///
/// Includes:
/// يشمل:
/// - Local notification service (الإشعارات المحلية)
/// - Notification types and channels (أنواع وقنوات الإشعارات)
/// - Notification settings and preferences (إعدادات الإشعارات)
/// - Notification handler for navigation (معالج التنقل للإشعارات)
/// - Notification providers for Riverpod (مزودات الإشعارات)
library;

export 'notification_types.dart';
export 'notification_service.dart';
export 'local_notification_service.dart' hide NotificationTapCallback;
export 'notification_settings.dart';
export 'notification_preferences.dart';
export 'notification_handler.dart';
export 'notification_provider.dart';
export 'notification_manager.dart'
    hide
        notificationManagerProvider,
        notificationInitializedProvider,
        notificationStreamProvider;
export 'push_notification_service.dart'
    hide subscribedTopicsProvider;
