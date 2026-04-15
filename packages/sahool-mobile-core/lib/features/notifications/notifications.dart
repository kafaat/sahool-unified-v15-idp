/// SAHOOL Notifications Feature
/// ميزة الإشعارات في سهول
///
/// Notification center with settings and actionable alerts
/// مركز الإشعارات مع الإعدادات والتنبيهات القابلة للتنفيذ
library;

// Data
export 'data/notifications_api.dart';
export 'data/notifications_local_db.dart';
export 'data/notifications_repository.dart';
export 'data/remote/notification_api.dart';
export 'data/services/notification_service.dart';

// Domain
export 'domain/entities/notification_entities.dart';
export 'domain/models/notification.dart';
export 'domain/models/notification_action.dart';
export 'domain/models/notification_category.dart';
export 'domain/models/notification_settings.dart';

// Root-level
export 'notification_badge.dart';
export 'notification_provider.dart';

// Presentation
export 'presentation/providers/notification_provider.dart';
export 'presentation/screens/notification_details_screen.dart';
export 'presentation/screens/notification_settings_screen.dart';
export 'presentation/screens/notifications_center_screen.dart';
export 'presentation/screens/notifications_screen.dart';
export 'presentation/widgets/actionable_notification.dart';
export 'presentation/widgets/grouped_notification_list.dart';
export 'presentation/widgets/notification_badge.dart';
export 'presentation/widgets/notification_card.dart';
export 'presentation/widgets/notification_filter.dart';

// State
export 'state/notifications_controller.dart';
export 'state/notifications_providers.dart';
