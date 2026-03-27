/// SAHOOL Notification Model (Extended)
/// نموذج الإشعار المحسن
///
/// Extended notification model with support for:
/// - Categories and priorities
/// - Actions and deep linking
/// - Grouping and threading
/// - Read/unread status
/// - Offline support
library;

import 'notification_category.dart';
import 'notification_action.dart';

/// Notification status
enum NotificationStatus {
  /// New, unread notification
  unread,

  /// Has been read
  read,

  /// Archived by user
  archived,

  /// Deleted (soft delete)
  deleted,

  /// Snoozed until a later time
  snoozed,
}

/// Notification model
/// نموذج الإشعار
class AppNotification {
  /// Unique identifier
  final String id;

  /// Server-side ID
  final String? remoteId;

  /// Tenant ID for multi-tenancy
  final String tenantId;

  /// User ID this notification belongs to
  final String userId;

  /// Notification category
  final NotificationCategory category;

  /// Priority level
  final NotificationPriority priority;

  /// Title (English)
  final String title;

  /// Title (Arabic)
  final String titleAr;

  /// Message body (English)
  final String body;

  /// Message body (Arabic)
  final String bodyAr;

  /// Short summary for list views
  final String? summary;

  /// Short summary (Arabic)
  final String? summaryAr;

  /// Current status
  final NotificationStatus status;

  /// Available actions
  final List<NotificationAction> actions;

  /// Primary action (default tap action)
  final NotificationAction? primaryAction;

  /// Group ID for threading related notifications
  final String? groupId;

  /// Group title
  final String? groupTitle;

  /// Related entity type (field, task, etc.)
  final String? relatedEntityType;

  /// Related entity ID
  final String? relatedEntityId;

  /// Image URL for rich notifications
  final String? imageUrl;

  /// Icon name override
  final String? iconName;

  /// Additional data payload
  final Map<String, dynamic>? data;

  /// When the notification was created
  final DateTime createdAt;

  /// When the notification was read
  final DateTime? readAt;

  /// When the notification expires
  final DateTime? expiresAt;

  /// When snoozed until
  final DateTime? snoozedUntil;

  /// Whether synced with server
  final bool synced;

  /// Source of notification (push, local, websocket)
  final String source;

  const AppNotification({
    required this.id,
    this.remoteId,
    required this.tenantId,
    required this.userId,
    required this.category,
    this.priority = NotificationPriority.normal,
    required this.title,
    required this.titleAr,
    required this.body,
    required this.bodyAr,
    this.summary,
    this.summaryAr,
    this.status = NotificationStatus.unread,
    this.actions = const [],
    this.primaryAction,
    this.groupId,
    this.groupTitle,
    this.relatedEntityType,
    this.relatedEntityId,
    this.imageUrl,
    this.iconName,
    this.data,
    required this.createdAt,
    this.readAt,
    this.expiresAt,
    this.snoozedUntil,
    this.synced = false,
    this.source = 'local',
  });

  /// Check if notification is unread
  bool get isUnread => status == NotificationStatus.unread;

  /// Check if notification is read
  bool get isRead => status == NotificationStatus.read;

  /// Check if notification is archived
  bool get isArchived => status == NotificationStatus.archived;

  /// Check if notification is snoozed
  bool get isSnoozed =>
      status == NotificationStatus.snoozed &&
      snoozedUntil != null &&
      snoozedUntil!.isAfter(DateTime.now());

  /// Check if notification has expired
  bool get isExpired =>
      expiresAt != null && expiresAt!.isBefore(DateTime.now());

  /// Check if notification is critical
  bool get isCritical => priority == NotificationPriority.critical;

  /// Check if notification is high priority
  bool get isHighPriority =>
      priority == NotificationPriority.high ||
      priority == NotificationPriority.critical;

  /// Check if notification has actions
  bool get hasActions => actions.isNotEmpty || primaryAction != null;

  /// Check if notification is related to an entity
  bool get hasRelatedEntity =>
      relatedEntityType != null && relatedEntityId != null;

  /// Get display title based on locale
  String getTitle(bool isArabic) => isArabic ? titleAr : title;

  /// Get display body based on locale
  String getBody(bool isArabic) => isArabic ? bodyAr : body;

  /// Get display summary based on locale
  String? getSummary(bool isArabic) => isArabic ? summaryAr : summary;

  /// Get age of notification
  Duration get age => DateTime.now().difference(createdAt);

  /// Get formatted age string
  String get ageString {
    final duration = age;
    if (duration.inMinutes < 1) {
      return 'Just now';
    } else if (duration.inMinutes < 60) {
      return '${duration.inMinutes}m ago';
    } else if (duration.inHours < 24) {
      return '${duration.inHours}h ago';
    } else if (duration.inDays < 7) {
      return '${duration.inDays}d ago';
    } else {
      return '${(duration.inDays / 7).floor()}w ago';
    }
  }

  /// Get formatted age string in Arabic
  String get ageStringAr {
    final duration = age;
    if (duration.inMinutes < 1) {
      return 'الآن';
    } else if (duration.inMinutes < 60) {
      return 'منذ ${duration.inMinutes} دقيقة';
    } else if (duration.inHours < 24) {
      return 'منذ ${duration.inHours} ساعة';
    } else if (duration.inDays < 7) {
      return 'منذ ${duration.inDays} يوم';
    } else {
      return 'منذ ${(duration.inDays / 7).floor()} أسبوع';
    }
  }

  /// Create from JSON
  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'] as String,
      remoteId: json['remote_id'] as String?,
      tenantId: json['tenant_id'] as String? ?? '',
      userId: json['user_id'] as String? ?? '',
      category: NotificationCategoryExtension.fromString(
              json['category'] as String?) ??
          NotificationCategory.system,
      priority:
          NotificationPriorityExtension.fromValue(json['priority'] as int? ?? 2),
      title: json['title'] as String? ?? '',
      titleAr: json['title_ar'] as String? ?? json['title'] as String? ?? '',
      body: json['body'] as String? ?? '',
      bodyAr: json['body_ar'] as String? ?? json['body'] as String? ?? '',
      summary: json['summary'] as String?,
      summaryAr: json['summary_ar'] as String?,
      status: _parseStatus(json['status'] as String?),
      actions: (json['actions'] as List<dynamic>?)
              ?.map((a) =>
                  NotificationAction.fromJson(a as Map<String, dynamic>))
              .toList() ??
          [],
      primaryAction: json['primary_action'] != null
          ? NotificationAction.fromJson(
              json['primary_action'] as Map<String, dynamic>)
          : null,
      groupId: json['group_id'] as String?,
      groupTitle: json['group_title'] as String?,
      relatedEntityType: json['related_entity_type'] as String?,
      relatedEntityId: json['related_entity_id'] as String?,
      imageUrl: json['image_url'] as String?,
      iconName: json['icon_name'] as String?,
      data: json['data'] as Map<String, dynamic>?,
      createdAt: json['created_at'] != null
          ? DateTime.parse(json['created_at'] as String)
          : DateTime.now(),
      readAt: json['read_at'] != null
          ? DateTime.parse(json['read_at'] as String)
          : null,
      expiresAt: json['expires_at'] != null
          ? DateTime.parse(json['expires_at'] as String)
          : null,
      snoozedUntil: json['snoozed_until'] != null
          ? DateTime.parse(json['snoozed_until'] as String)
          : null,
      synced: json['synced'] as bool? ?? false,
      source: json['source'] as String? ?? 'api',
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'remote_id': remoteId,
      'tenant_id': tenantId,
      'user_id': userId,
      'category': category.name,
      'priority': priority.value,
      'title': title,
      'title_ar': titleAr,
      'body': body,
      'body_ar': bodyAr,
      'summary': summary,
      'summary_ar': summaryAr,
      'status': status.name,
      'actions': actions.map((a) => a.toJson()).toList(),
      'primary_action': primaryAction?.toJson(),
      'group_id': groupId,
      'group_title': groupTitle,
      'related_entity_type': relatedEntityType,
      'related_entity_id': relatedEntityId,
      'image_url': imageUrl,
      'icon_name': iconName,
      'data': data,
      'created_at': createdAt.toIso8601String(),
      'read_at': readAt?.toIso8601String(),
      'expires_at': expiresAt?.toIso8601String(),
      'snoozed_until': snoozedUntil?.toIso8601String(),
      'synced': synced,
      'source': source,
    };
  }

  /// Copy with modifications
  AppNotification copyWith({
    String? id,
    String? remoteId,
    String? tenantId,
    String? userId,
    NotificationCategory? category,
    NotificationPriority? priority,
    String? title,
    String? titleAr,
    String? body,
    String? bodyAr,
    String? summary,
    String? summaryAr,
    NotificationStatus? status,
    List<NotificationAction>? actions,
    NotificationAction? primaryAction,
    String? groupId,
    String? groupTitle,
    String? relatedEntityType,
    String? relatedEntityId,
    String? imageUrl,
    String? iconName,
    Map<String, dynamic>? data,
    DateTime? createdAt,
    DateTime? readAt,
    DateTime? expiresAt,
    DateTime? snoozedUntil,
    bool? synced,
    String? source,
  }) {
    return AppNotification(
      id: id ?? this.id,
      remoteId: remoteId ?? this.remoteId,
      tenantId: tenantId ?? this.tenantId,
      userId: userId ?? this.userId,
      category: category ?? this.category,
      priority: priority ?? this.priority,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      body: body ?? this.body,
      bodyAr: bodyAr ?? this.bodyAr,
      summary: summary ?? this.summary,
      summaryAr: summaryAr ?? this.summaryAr,
      status: status ?? this.status,
      actions: actions ?? this.actions,
      primaryAction: primaryAction ?? this.primaryAction,
      groupId: groupId ?? this.groupId,
      groupTitle: groupTitle ?? this.groupTitle,
      relatedEntityType: relatedEntityType ?? this.relatedEntityType,
      relatedEntityId: relatedEntityId ?? this.relatedEntityId,
      imageUrl: imageUrl ?? this.imageUrl,
      iconName: iconName ?? this.iconName,
      data: data ?? this.data,
      createdAt: createdAt ?? this.createdAt,
      readAt: readAt ?? this.readAt,
      expiresAt: expiresAt ?? this.expiresAt,
      snoozedUntil: snoozedUntil ?? this.snoozedUntil,
      synced: synced ?? this.synced,
      source: source ?? this.source,
    );
  }

  /// Mark as read
  AppNotification markAsRead() {
    return copyWith(
      status: NotificationStatus.read,
      readAt: DateTime.now(),
    );
  }

  /// Mark as unread
  AppNotification markAsUnread() {
    return copyWith(
      status: NotificationStatus.unread,
      readAt: null,
    );
  }

  /// Archive notification
  AppNotification archive() {
    return copyWith(status: NotificationStatus.archived);
  }

  /// Snooze notification
  AppNotification snooze(Duration duration) {
    return copyWith(
      status: NotificationStatus.snoozed,
      snoozedUntil: DateTime.now().add(duration),
    );
  }

  static NotificationStatus _parseStatus(String? value) {
    if (value == null) return NotificationStatus.unread;
    switch (value.toLowerCase()) {
      case 'read':
        return NotificationStatus.read;
      case 'archived':
        return NotificationStatus.archived;
      case 'deleted':
        return NotificationStatus.deleted;
      case 'snoozed':
        return NotificationStatus.snoozed;
      default:
        return NotificationStatus.unread;
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AppNotification &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() =>
      'AppNotification($id: $title, category: ${category.name}, status: ${status.name})';
}

/// Grouped notifications by date
class NotificationGroup {
  final DateTime date;
  final String title;
  final String titleAr;
  final List<AppNotification> notifications;

  const NotificationGroup({
    required this.date,
    required this.title,
    required this.titleAr,
    required this.notifications,
  });

  int get unreadCount =>
      notifications.where((n) => n.status == NotificationStatus.unread).length;

  bool get hasUnread => unreadCount > 0;
}

/// Grouped notifications by category
class CategoryNotificationGroup {
  final NotificationCategory category;
  final List<AppNotification> notifications;

  const CategoryNotificationGroup({
    required this.category,
    required this.notifications,
  });

  int get unreadCount =>
      notifications.where((n) => n.status == NotificationStatus.unread).length;

  bool get hasUnread => unreadCount > 0;
}
