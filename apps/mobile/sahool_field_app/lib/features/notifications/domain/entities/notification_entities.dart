/// SAHOOL Notification Domain Entities
/// نماذج بيانات الإشعارات
library;

/// إشعار التطبيق
class AppNotification {
  final String id;
  final String type; // alert, action, weather, crop_health, system
  final String title;
  final String titleAr;
  final String body;
  final String bodyAr;
  final String? imageUrl;
  final Map<String, dynamic> data;
  final DateTime createdAt;
  final bool isRead;
  final String? actionUrl;

  const AppNotification({
    required this.id,
    required this.type,
    required this.title,
    required this.titleAr,
    required this.body,
    required this.bodyAr,
    this.imageUrl,
    required this.data,
    required this.createdAt,
    this.isRead = false,
    this.actionUrl,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String,
      type: json['type'] as String,
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? json['title'],
      body: json['body'] as String,
      bodyAr: json['body_ar'] as String? ?? json['body'],
      imageUrl: json['image_url'] as String?,
      data: Map<String, dynamic>.from(json['data'] ?? {}),
      createdAt: DateTime.parse(json['created_at'] as String),
      isRead: json['is_read'] as bool? ?? false,
      actionUrl: json['action_url'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type,
        'title': title,
        'title_ar': titleAr,
        'body': body,
        'body_ar': bodyAr,
        'image_url': imageUrl,
        'data': data,
        'created_at': createdAt.toIso8601String(),
        'is_read': isRead,
        'action_url': actionUrl,
      };

  AppNotification copyWith({
    String? id,
    String? type,
    String? title,
    String? titleAr,
    String? body,
    String? bodyAr,
    String? imageUrl,
    Map<String, dynamic>? data,
    DateTime? createdAt,
    bool? isRead,
    String? actionUrl,
  }) {
    return AppNotification(
      id: id ?? this.id,
      type: type ?? this.type,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      body: body ?? this.body,
      bodyAr: bodyAr ?? this.bodyAr,
      imageUrl: imageUrl ?? this.imageUrl,
      data: data ?? this.data,
      createdAt: createdAt ?? this.createdAt,
      isRead: isRead ?? this.isRead,
      actionUrl: actionUrl ?? this.actionUrl,
    );
  }

  String get typeIcon {
    switch (type) {
      case 'alert':
        return '⚠️';
      case 'action':
        return '📋';
      case 'weather':
        return '🌤️';
      case 'crop_health':
        return '🌱';
      case 'system':
        return '⚙️';
      default:
        return '🔔';
    }
  }

  String get typeLabel {
    switch (type) {
      case 'alert':
        return 'تنبيه';
      case 'action':
        return 'إجراء';
      case 'weather':
        return 'طقس';
      case 'crop_health':
        return 'صحة المحصول';
      case 'system':
        return 'نظام';
      default:
        return 'إشعار';
    }
  }

  String get timeAgo {
    final diff = DateTime.now().difference(createdAt);
    if (diff.inDays > 0) {
      return 'منذ ${diff.inDays} يوم';
    } else if (diff.inHours > 0) {
      return 'منذ ${diff.inHours} ساعة';
    } else if (diff.inMinutes > 0) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else {
      return 'الآن';
    }
  }
}

/// إعدادات الإشعارات
class NotificationSettings {
  final bool enabled;
  final bool alertsEnabled;
  final bool actionsEnabled;
  final bool weatherEnabled;
  final bool cropHealthEnabled;
  final bool systemEnabled;
  final bool soundEnabled;
  final bool vibrationEnabled;
  final String? quietHoursStart; // HH:mm
  final String? quietHoursEnd;

  const NotificationSettings({
    this.enabled = true,
    this.alertsEnabled = true,
    this.actionsEnabled = true,
    this.weatherEnabled = true,
    this.cropHealthEnabled = true,
    this.systemEnabled = true,
    this.soundEnabled = true,
    this.vibrationEnabled = true,
    this.quietHoursStart,
    this.quietHoursEnd,
  });

  factory NotificationSettings.fromJson(Map<String, dynamic> json) {
    return NotificationSettings(
      enabled: json['enabled'] as bool? ?? true,
      alertsEnabled: json['alerts_enabled'] as bool? ?? true,
      actionsEnabled: json['actions_enabled'] as bool? ?? true,
      weatherEnabled: json['weather_enabled'] as bool? ?? true,
      cropHealthEnabled: json['crop_health_enabled'] as bool? ?? true,
      systemEnabled: json['system_enabled'] as bool? ?? true,
      soundEnabled: json['sound_enabled'] as bool? ?? true,
      vibrationEnabled: json['vibration_enabled'] as bool? ?? true,
      quietHoursStart: json['quiet_hours_start'] as String?,
      quietHoursEnd: json['quiet_hours_end'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'enabled': enabled,
        'alerts_enabled': alertsEnabled,
        'actions_enabled': actionsEnabled,
        'weather_enabled': weatherEnabled,
        'crop_health_enabled': cropHealthEnabled,
        'system_enabled': systemEnabled,
        'sound_enabled': soundEnabled,
        'vibration_enabled': vibrationEnabled,
        'quiet_hours_start': quietHoursStart,
        'quiet_hours_end': quietHoursEnd,
      };

  NotificationSettings copyWith({
    bool? enabled,
    bool? alertsEnabled,
    bool? actionsEnabled,
    bool? weatherEnabled,
    bool? cropHealthEnabled,
    bool? systemEnabled,
    bool? soundEnabled,
    bool? vibrationEnabled,
    String? quietHoursStart,
    String? quietHoursEnd,
  }) {
    return NotificationSettings(
      enabled: enabled ?? this.enabled,
      alertsEnabled: alertsEnabled ?? this.alertsEnabled,
      actionsEnabled: actionsEnabled ?? this.actionsEnabled,
      weatherEnabled: weatherEnabled ?? this.weatherEnabled,
      cropHealthEnabled: cropHealthEnabled ?? this.cropHealthEnabled,
      systemEnabled: systemEnabled ?? this.systemEnabled,
      soundEnabled: soundEnabled ?? this.soundEnabled,
      vibrationEnabled: vibrationEnabled ?? this.vibrationEnabled,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
    );
  }
}

/// موضوع الإشعارات (للاشتراك)
class NotificationTopic {
  final String id;
  final String name;
  final String nameAr;
  final String description;
  final bool isSubscribed;

  const NotificationTopic({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.description,
    this.isSubscribed = false,
  });

  factory NotificationTopic.fromJson(Map<String, dynamic> json) {
    return NotificationTopic(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['name_ar'] as String? ?? json['name'],
      description: json['description'] as String,
      isSubscribed: json['is_subscribed'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'name_ar': nameAr,
        'description': description,
        'is_subscribed': isSubscribed,
      };

  NotificationTopic copyWith({
    String? id,
    String? name,
    String? nameAr,
    String? description,
    bool? isSubscribed,
  }) {
    return NotificationTopic(
      id: id ?? this.id,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      description: description ?? this.description,
      isSubscribed: isSubscribed ?? this.isSubscribed,
    );
  }
}
