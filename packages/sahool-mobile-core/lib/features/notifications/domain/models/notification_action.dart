/// SAHOOL Notification Actions
/// إجراءات الإشعارات
///
/// Defines actions that can be taken from notifications
/// such as deep linking, quick actions, and responses
library;

import 'package:flutter/material.dart';

/// Type of notification action
enum NotificationActionType {
  /// Navigate to a specific screen
  deepLink,

  /// Open URL in browser
  openUrl,

  /// Execute a quick action (dismiss, snooze, etc.)
  quickAction,

  /// Mark task as done
  markDone,

  /// Snooze the notification
  snooze,

  /// Dismiss the notification
  dismiss,

  /// View details
  viewDetails,

  /// Reply to the notification
  reply,

  /// Call a phone number
  call,

  /// Navigate to field
  navigateToField,

  /// Start irrigation
  startIrrigation,

  /// Stop irrigation
  stopIrrigation,

  /// Acknowledge alert
  acknowledge,
}

/// Notification action model
/// نموذج إجراء الإشعار
class NotificationAction {
  /// Unique identifier
  final String id;

  /// Action type
  final NotificationActionType type;

  /// Display label (English)
  final String label;

  /// Display label (Arabic)
  final String labelAr;

  /// Icon for the action
  final IconData icon;

  /// Action color
  final Color? color;

  /// Route to navigate to (for deepLink)
  final String? route;

  /// URL to open (for openUrl)
  final String? url;

  /// Additional parameters for the action
  final Map<String, dynamic>? params;

  /// Whether this action should close the notification
  final bool closeOnAction;

  /// Whether this action requires confirmation
  final bool requiresConfirmation;

  const NotificationAction({
    required this.id,
    required this.type,
    required this.label,
    required this.labelAr,
    required this.icon,
    this.color,
    this.route,
    this.url,
    this.params,
    this.closeOnAction = true,
    this.requiresConfirmation = false,
  });

  /// Create from JSON
  factory NotificationAction.fromJson(Map<String, dynamic> json) {
    return NotificationAction(
      id: json['id'] as String,
      type: _parseActionType(json['type'] as String),
      label: json['label'] as String? ?? 'Action',
      labelAr: json['label_ar'] as String? ?? 'إجراء',
      icon: _parseIcon(json['icon'] as String?),
      color: json['color'] != null
          ? Color(int.parse(json['color'] as String, radix: 16))
          : null,
      route: json['route'] as String?,
      url: json['url'] as String?,
      params: json['params'] as Map<String, dynamic>?,
      closeOnAction: json['close_on_action'] as bool? ?? true,
      requiresConfirmation: json['requires_confirmation'] as bool? ?? false,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'type': type.name,
      'label': label,
      'label_ar': labelAr,
      'icon': icon.codePoint.toRadixString(16),
      'color': color?.value.toRadixString(16),
      'route': route,
      'url': url,
      'params': params,
      'close_on_action': closeOnAction,
      'requires_confirmation': requiresConfirmation,
    };
  }

  /// Copy with modifications
  NotificationAction copyWith({
    String? id,
    NotificationActionType? type,
    String? label,
    String? labelAr,
    IconData? icon,
    Color? color,
    String? route,
    String? url,
    Map<String, dynamic>? params,
    bool? closeOnAction,
    bool? requiresConfirmation,
  }) {
    return NotificationAction(
      id: id ?? this.id,
      type: type ?? this.type,
      label: label ?? this.label,
      labelAr: labelAr ?? this.labelAr,
      icon: icon ?? this.icon,
      color: color ?? this.color,
      route: route ?? this.route,
      url: url ?? this.url,
      params: params ?? this.params,
      closeOnAction: closeOnAction ?? this.closeOnAction,
      requiresConfirmation: requiresConfirmation ?? this.requiresConfirmation,
    );
  }

  static NotificationActionType _parseActionType(String value) {
    switch (value.toLowerCase()) {
      case 'deeplink':
      case 'deep_link':
        return NotificationActionType.deepLink;
      case 'openurl':
      case 'open_url':
        return NotificationActionType.openUrl;
      case 'quickaction':
      case 'quick_action':
        return NotificationActionType.quickAction;
      case 'markdone':
      case 'mark_done':
        return NotificationActionType.markDone;
      case 'snooze':
        return NotificationActionType.snooze;
      case 'dismiss':
        return NotificationActionType.dismiss;
      case 'viewdetails':
      case 'view_details':
        return NotificationActionType.viewDetails;
      case 'reply':
        return NotificationActionType.reply;
      case 'call':
        return NotificationActionType.call;
      case 'navigatetofield':
      case 'navigate_to_field':
        return NotificationActionType.navigateToField;
      case 'startirrigation':
      case 'start_irrigation':
        return NotificationActionType.startIrrigation;
      case 'stopirrigation':
      case 'stop_irrigation':
        return NotificationActionType.stopIrrigation;
      case 'acknowledge':
        return NotificationActionType.acknowledge;
      default:
        return NotificationActionType.viewDetails;
    }
  }

  static IconData _parseIcon(String? iconName) {
    switch (iconName?.toLowerCase()) {
      case 'check':
        return Icons.check;
      case 'close':
        return Icons.close;
      case 'snooze':
        return Icons.snooze;
      case 'open':
        return Icons.open_in_new;
      case 'call':
        return Icons.call;
      case 'navigation':
        return Icons.navigation;
      case 'water':
        return Icons.water_drop;
      case 'stop':
        return Icons.stop;
      case 'done':
        return Icons.done_all;
      case 'reply':
        return Icons.reply;
      default:
        return Icons.arrow_forward;
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is NotificationAction &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;
}

/// Predefined common actions
class CommonActions {
  static const NotificationAction viewDetails = NotificationAction(
    id: 'view_details',
    type: NotificationActionType.viewDetails,
    label: 'View Details',
    labelAr: 'عرض التفاصيل',
    icon: Icons.visibility,
    color: Colors.blue,
  );

  static const NotificationAction dismiss = NotificationAction(
    id: 'dismiss',
    type: NotificationActionType.dismiss,
    label: 'Dismiss',
    labelAr: 'تجاهل',
    icon: Icons.close,
    color: Colors.grey,
  );

  static const NotificationAction snooze30m = NotificationAction(
    id: 'snooze_30m',
    type: NotificationActionType.snooze,
    label: 'Snooze 30 min',
    labelAr: 'تأجيل 30 دقيقة',
    icon: Icons.snooze,
    color: Colors.orange,
    params: {'duration_minutes': 30},
  );

  static const NotificationAction snooze1h = NotificationAction(
    id: 'snooze_1h',
    type: NotificationActionType.snooze,
    label: 'Snooze 1 hour',
    labelAr: 'تأجيل ساعة',
    icon: Icons.snooze,
    color: Colors.orange,
    params: {'duration_minutes': 60},
  );

  static const NotificationAction markTaskDone = NotificationAction(
    id: 'mark_done',
    type: NotificationActionType.markDone,
    label: 'Mark as Done',
    labelAr: 'تم الإنجاز',
    icon: Icons.check_circle,
    color: Colors.green,
  );

  static const NotificationAction acknowledge = NotificationAction(
    id: 'acknowledge',
    type: NotificationActionType.acknowledge,
    label: 'Acknowledge',
    labelAr: 'تأكيد الاستلام',
    icon: Icons.thumb_up,
    color: Colors.green,
  );

  static const NotificationAction goToField = NotificationAction(
    id: 'go_to_field',
    type: NotificationActionType.navigateToField,
    label: 'Go to Field',
    labelAr: 'الذهاب للحقل',
    icon: Icons.navigation,
    color: Colors.blue,
  );

  static const NotificationAction startIrrigation = NotificationAction(
    id: 'start_irrigation',
    type: NotificationActionType.startIrrigation,
    label: 'Start Irrigation',
    labelAr: 'بدء الري',
    icon: Icons.play_arrow,
    color: Colors.blue,
    requiresConfirmation: true,
  );

  static const NotificationAction stopIrrigation = NotificationAction(
    id: 'stop_irrigation',
    type: NotificationActionType.stopIrrigation,
    label: 'Stop Irrigation',
    labelAr: 'إيقاف الري',
    icon: Icons.stop,
    color: Colors.red,
    requiresConfirmation: true,
  );
}
