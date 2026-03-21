/// SAHOOL Firebase Messaging Service
/// خدمة رسائل Firebase
///
/// Enhanced Firebase Cloud Messaging integration for SAHOOL platform
/// Complements the existing push_notification_service.dart with additional features

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import '../utils/app_logger.dart';

/// Notification types matching backend
enum SAHOOLNotificationType {
  weatherAlert('weather_alert'),
  lowStock('low_stock'),
  diseaseDetected('disease_detected'),
  sprayWindow('spray_window'),
  harvestReminder('harvest_reminder'),
  paymentDue('payment_due'),
  fieldUpdate('field_update'),
  satelliteReady('satellite_ready'),
  pestOutbreak('pest_outbreak'),
  irrigationReminder('irrigation_reminder'),
  marketPrice('market_price'),
  cropHealth('crop_health'),
  taskReminder('task_reminder'),
  system('system');

  final String value;
  const SAHOOLNotificationType(this.value);

  static SAHOOLNotificationType fromString(String value) {
    return SAHOOLNotificationType.values.firstWhere(
      (type) => type.value == value,
      orElse: () => SAHOOLNotificationType.system,
    );
  }

  /// Get notification channel ID for Android
  String get channelId {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
      case SAHOOLNotificationType.diseaseDetected:
      case SAHOOLNotificationType.pestOutbreak:
        return 'sahool_alerts';
      case SAHOOLNotificationType.taskReminder:
      case SAHOOLNotificationType.harvestReminder:
      case SAHOOLNotificationType.irrigationReminder:
        return 'sahool_tasks';
      case SAHOOLNotificationType.fieldUpdate:
      case SAHOOLNotificationType.satelliteReady:
      case SAHOOLNotificationType.cropHealth:
        return 'sahool_field_updates';
      case SAHOOLNotificationType.paymentDue:
      case SAHOOLNotificationType.marketPrice:
        return 'sahool_financial';
      case SAHOOLNotificationType.sprayWindow:
        return 'sahool_operations';
      case SAHOOLNotificationType.lowStock:
        return 'sahool_inventory';
      default:
        return 'sahool_main';
    }
  }

  /// Get notification channel name (Arabic)
  String get channelName {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
      case SAHOOLNotificationType.diseaseDetected:
      case SAHOOLNotificationType.pestOutbreak:
        return 'التنبيهات العاجلة';
      case SAHOOLNotificationType.taskReminder:
      case SAHOOLNotificationType.harvestReminder:
      case SAHOOLNotificationType.irrigationReminder:
        return 'المهام والتذكيرات';
      case SAHOOLNotificationType.fieldUpdate:
      case SAHOOLNotificationType.satelliteReady:
      case SAHOOLNotificationType.cropHealth:
        return 'تحديثات الحقل';
      case SAHOOLNotificationType.paymentDue:
      case SAHOOLNotificationType.marketPrice:
        return 'المالية والأسواق';
      case SAHOOLNotificationType.sprayWindow:
        return 'العمليات الزراعية';
      case SAHOOLNotificationType.lowStock:
        return 'المخزون';
      default:
        return 'إشعارات سهول';
    }
  }

  /// Check if notification is urgent
  bool get isUrgent {
    return this == SAHOOLNotificationType.weatherAlert ||
        this == SAHOOLNotificationType.diseaseDetected ||
        this == SAHOOLNotificationType.pestOutbreak ||
        this == SAHOOLNotificationType.sprayWindow;
  }

  /// Get notification icon
  String get icon {
    switch (this) {
      case SAHOOLNotificationType.weatherAlert:
        return '⚠️';
      case SAHOOLNotificationType.diseaseDetected:
        return '🦠';
      case SAHOOLNotificationType.pestOutbreak:
        return '🐛';
      case SAHOOLNotificationType.sprayWindow:
        return '💨';
      case SAHOOLNotificationType.harvestReminder:
        return '🌾';
      case SAHOOLNotificationType.irrigationReminder:
        return '💧';
      case SAHOOLNotificationType.satelliteReady:
        return '🛰️';
      case SAHOOLNotificationType.fieldUpdate:
        return '🌱';
      case SAHOOLNotificationType.cropHealth:
        return '🌿';
      case SAHOOLNotificationType.marketPrice:
        return '📈';
      case SAHOOLNotificationType.paymentDue:
        return '💰';
      case SAHOOLNotificationType.lowStock:
        return '📦';
      default:
        return 'ℹ️';
    }
  }
}

/// Notification priority
enum NotificationPriority {
  low,
  medium,
  high,
  critical;

  static NotificationPriority fromString(String? value) {
    switch (value) {
      case 'critical':
        return NotificationPriority.critical;
      case 'high':
        return NotificationPriority.high;
      case 'medium':
        return NotificationPriority.medium;
      case 'low':
        return NotificationPriority.low;
      default:
        return NotificationPriority.medium;
    }
  }
}

/// Parsed notification payload
class SAHOOLNotificationPayload {
  final String id;
  final SAHOOLNotificationType type;
  final NotificationPriority priority;
  final String title;
  final String body;
  final Map<String, dynamic> data;
  final DateTime receivedAt;
  final bool tapped;

  const SAHOOLNotificationPayload({
    required this.id,
    required this.type,
    required this.priority,
    required this.title,
    required this.body,
    required this.data,
    required this.receivedAt,
    this.tapped = false,
  });

  factory SAHOOLNotificationPayload.fromRemoteMessage(
    RemoteMessage message, {
    bool tapped = false,
  }) {
    return SAHOOLNotificationPayload(
      id: message.messageId ?? DateTime.now().millisecondsSinceEpoch.toString(),
      type: SAHOOLNotificationType.fromString((message.data['type'] as String?) ?? 'system'),
      priority: NotificationPriority.fromString(message.data['priority'] as String?),
      title: message.notification?.title ?? '',
      body: message.notification?.body ?? '',
      data: message.data,
      receivedAt: DateTime.now(),
      tapped: tapped,
    );
  }

  /// Get action URL from data
  String? get actionUrl => data['action_url'] as String?;

  /// Get field ID from data
  String? get fieldId => data['field_id'] as String?;

  /// Get crop type from data
  String? get cropType => data['crop_type'] as String?;

  /// Get extra data as JSON
  Map<String, dynamic>? get extra {
    final extraStr = data['extra'] as String?;
    if (extraStr == null) return null;
    try {
      return jsonDecode(extraStr) as Map<String, dynamic>;
    } catch (e) {
      return null;
    }
  }
}

/// Firebase Messaging Service
/// Manages FCM integration with enhanced features
class FirebaseMessagingService {
  static FirebaseMessagingService? _instance;
  static FirebaseMessagingService get instance {
    _instance ??= FirebaseMessagingService._();
    return _instance!;
  }

  FirebaseMessagingService._();

  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  final _notificationStreamController =
      StreamController<SAHOOLNotificationPayload>.broadcast();
  Stream<SAHOOLNotificationPayload> get onNotification =>
      _notificationStreamController.stream;

  final _tokenRefreshController = StreamController<String>.broadcast();
  Stream<String> get onTokenRefresh => _tokenRefreshController.stream;

  bool _initialized = false;

  /// Initialize Firebase Messaging
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Request permissions
      await requestPermission();

      // Initialize local notifications
      await _initializeLocalNotifications();

      // Setup message handlers
      _setupMessageHandlers();

      // Get FCM token
      await _getToken();

      // Listen for token refresh
      _messaging.onTokenRefresh.listen((token) {
        _fcmToken = token;
        _tokenRefreshController.add(token);
        AppLogger.i('FCM token refreshed', tag: 'FCM');
      });

      _initialized = true;
      AppLogger.i('Firebase Messaging Service initialized', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to initialize Firebase Messaging: $e', tag: 'FCM', error: e);
    }
  }

  /// Request notification permissions
  Future<bool> requestPermission() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      announcement: false,
      badge: true,
      carPlay: false,
      criticalAlert: false,
      provisional: false,
      sound: true,
    );

    final authorized = settings.authorizationStatus == AuthorizationStatus.authorized;
    AppLogger.i('Notification permission: ${settings.authorizationStatus}', tag: 'FCM');
    return authorized;
  }

  /// Initialize local notifications
  Future<void> _initializeLocalNotifications() async {
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');

    final iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
    );

    final settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _handleNotificationTap,
    );

    // Create Android notification channels
    if (Platform.isAndroid) {
      await _createNotificationChannels();
    }
  }

  /// Create Android notification channels
  Future<void> _createNotificationChannels() async {
    final androidPlugin = _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

    if (androidPlugin == null) return;

    // Define all notification channels
    final channels = [
      const AndroidNotificationChannel(
        'sahool_alerts',
        'التنبيهات العاجلة',
        description: 'تنبيهات الطقس والأمراض والآفات',
        importance: Importance.max,
        enableVibration: true,
        playSound: true,
      ),
      const AndroidNotificationChannel(
        'sahool_tasks',
        'المهام والتذكيرات',
        description: 'تذكيرات المهام والحصاد والري',
        importance: Importance.high,
      ),
      const AndroidNotificationChannel(
        'sahool_field_updates',
        'تحديثات الحقل',
        description: 'تحديثات صحة المحصول وصور الأقمار',
        importance: Importance.defaultImportance,
      ),
      const AndroidNotificationChannel(
        'sahool_financial',
        'المالية والأسواق',
        description: 'الدفعات وأسعار الأسواق',
        importance: Importance.defaultImportance,
      ),
      const AndroidNotificationChannel(
        'sahool_operations',
        'العمليات الزراعية',
        description: 'أوقات الرش والعمليات',
        importance: Importance.high,
      ),
      const AndroidNotificationChannel(
        'sahool_inventory',
        'المخزون',
        description: 'إشعارات المخزون',
        importance: Importance.low,
      ),
      const AndroidNotificationChannel(
        'sahool_main',
        'إشعارات سهول',
        description: 'إشعارات عامة',
        importance: Importance.defaultImportance,
      ),
    ];

    for (final channel in channels) {
      await androidPlugin.createNotificationChannel(channel);
    }
  }

  /// Setup message handlers
  void _setupMessageHandlers() {
    // Foreground messages
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Message opened app
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);

    // Check initial message
    _checkInitialMessage();
  }

  /// Handle foreground message
  Future<void> _handleForegroundMessage(RemoteMessage message) async {
    AppLogger.d('Foreground message: ${message.messageId}', tag: 'FCM');

    // Show local notification
    await _showLocalNotification(message);

    // Emit to stream
    _emitNotification(message);
  }

  /// Handle message that opened the app
  void _handleMessageOpenedApp(RemoteMessage message) {
    AppLogger.d('Message opened app: ${message.messageId}', tag: 'FCM');
    _emitNotification(message, tapped: true);
  }

  /// Check for initial message
  Future<void> _checkInitialMessage() async {
    final initialMessage = await _messaging.getInitialMessage();
    if (initialMessage != null) {
      AppLogger.d('Initial message: ${initialMessage.messageId}', tag: 'FCM');
      _emitNotification(initialMessage, tapped: true);
    }
  }

  /// Show local notification
  Future<void> _showLocalNotification(RemoteMessage message) async {
    final notification = message.notification;
    if (notification == null) return;

    final type = SAHOOLNotificationType.fromString((message.data['type'] as String?) ?? '');
    final priority = NotificationPriority.fromString(message.data['priority'] as String?);

    final androidDetails = AndroidNotificationDetails(
      type.channelId,
      type.channelName,
      importance: type.isUrgent || priority == NotificationPriority.critical
          ? Importance.max
          : Importance.defaultImportance,
      priority: type.isUrgent || priority == NotificationPriority.critical
          ? Priority.high
          : Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
      styleInformation: BigTextStyleInformation(
        notification.body ?? '',
        htmlFormatBigText: true,
        contentTitle: notification.title,
        htmlFormatContentTitle: true,
      ),
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: type.isUrgent || priority == NotificationPriority.critical,
    );

    await _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      NotificationDetails(android: androidDetails, iOS: iosDetails),
      payload: jsonEncode(message.data),
    );
  }

  /// Emit notification to stream
  void _emitNotification(RemoteMessage message, {bool tapped = false}) {
    final payload = SAHOOLNotificationPayload.fromRemoteMessage(
      message,
      tapped: tapped,
    );
    _notificationStreamController.add(payload);
  }

  /// Handle notification tap
  void _handleNotificationTap(NotificationResponse response) {
    if (response.payload == null) return;

    try {
      final data = jsonDecode(response.payload!) as Map<String, dynamic>;
      final type = SAHOOLNotificationType.fromString((data['type'] as String?) ?? '');
      final priority = NotificationPriority.fromString(data['priority'] as String?);

      final payload = SAHOOLNotificationPayload(
        id: response.id?.toString() ?? '',
        type: type,
        priority: priority,
        title: '',
        body: '',
        data: data,
        receivedAt: DateTime.now(),
        tapped: true,
      );

      _notificationStreamController.add(payload);
    } catch (e) {
      AppLogger.e('Failed to parse notification payload: $e', tag: 'FCM', error: e);
    }
  }

  /// Get FCM token
  Future<String?> getToken() async {
    if (_fcmToken != null) return _fcmToken;
    return await _getToken();
  }

  Future<String?> _getToken() async {
    try {
      _fcmToken = await _messaging.getToken();
      if (_fcmToken != null) {
        AppLogger.d('FCM Token obtained (${_fcmToken!.length} chars)', tag: 'FCM');
      }
      return _fcmToken;
    } catch (e) {
      AppLogger.e('Failed to get FCM token: $e', tag: 'FCM', error: e);
      return null;
    }
  }

  /// Subscribe to topic
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _messaging.subscribeToTopic(topic);
      AppLogger.d('Subscribed to topic: $topic', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to subscribe to topic: $e', tag: 'FCM', error: e);
    }
  }

  /// Unsubscribe from topic
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _messaging.unsubscribeFromTopic(topic);
      AppLogger.d('Unsubscribed from topic: $topic', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to unsubscribe from topic: $e', tag: 'FCM', error: e);
    }
  }

  /// Subscribe to user-specific topics
  Future<void> subscribeToUserTopics({
    required String userId,
    required String? governorate,
    List<String>? crops,
  }) async {
    // User-specific topic
    await subscribeToTopic('user_$userId');

    // Governorate topic
    if (governorate != null) {
      await subscribeToTopic('gov_$governorate');
    }

    // Crop topics
    if (crops != null) {
      for (final crop in crops) {
        await subscribeToTopic('crop_$crop');
      }
    }

    // All farmers topic
    await subscribeToTopic('all_farmers');
  }

  /// Unsubscribe from all user topics
  Future<void> unsubscribeFromAllTopics({
    required String userId,
    String? governorate,
    List<String>? crops,
  }) async {
    await unsubscribeFromTopic('user_$userId');

    if (governorate != null) {
      await unsubscribeFromTopic('gov_$governorate');
    }

    if (crops != null) {
      for (final crop in crops) {
        await unsubscribeFromTopic('crop_$crop');
      }
    }

    await unsubscribeFromTopic('all_farmers');
  }

  /// Delete FCM token
  Future<void> deleteToken() async {
    try {
      await _messaging.deleteToken();
      _fcmToken = null;
      AppLogger.i('FCM token deleted', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to delete FCM token: $e', tag: 'FCM', error: e);
    }
  }

  /// Dispose
  void dispose() {
    _notificationStreamController.close();
    _tokenRefreshController.close();
  }
}
