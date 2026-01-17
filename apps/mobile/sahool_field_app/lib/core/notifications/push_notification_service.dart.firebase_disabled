import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';
import '../auth/secure_storage_service.dart';

/// SAHOOL Push Notification Service
/// خدمة الإشعارات الفورية
///
/// Features:
/// - Firebase Cloud Messaging (FCM)
/// - Local notifications
/// - Background message handling
/// - Topic subscriptions
/// - Notification channels (Android)

// Background message handler - must be top-level
@pragma('vm:entry-point')
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  AppLogger.i('Background message: ${message.messageId}', tag: 'FCM');

  // Handle background notification
  await PushNotificationService._handleBackgroundMessage(message);
}

class PushNotificationService {
  static PushNotificationService? _instance;
  static PushNotificationService get instance {
    _instance ??= PushNotificationService._();
    return _instance!;
  }

  PushNotificationService._();

  final FirebaseMessaging _fcm = FirebaseMessaging.instance;
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  final _notificationController = StreamController<NotificationPayload>.broadcast();
  Stream<NotificationPayload> get onNotification => _notificationController.stream;

  final _tokenController = StreamController<String>.broadcast();
  Stream<String> get onTokenRefresh => _tokenController.stream;

  bool _isInitialized = false;

  /// تهيئة خدمة الإشعارات
  Future<void> initialize() async {
    if (_isInitialized) return;

    try {
      // Request permission
      await _requestPermission();

      // Initialize local notifications
      await _initializeLocalNotifications();

      // Set up message handlers
      _setupMessageHandlers();

      // Get FCM token
      await _getToken();

      // Listen for token refresh
      _fcm.onTokenRefresh.listen((token) {
        _fcmToken = token;
        _tokenController.add(token);
        AppLogger.i('FCM token refreshed', tag: 'FCM');
      });

      _isInitialized = true;
      AppLogger.i('Push notification service initialized', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to initialize push notifications', tag: 'FCM', error: e);
    }
  }

  /// طلب إذن الإشعارات
  Future<bool> _requestPermission() async {
    final settings = await _fcm.requestPermission(
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

  /// تهيئة الإشعارات المحلية
  Future<void> _initializeLocalNotifications() async {
    // Android settings
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS settings
    final iosSettings = DarwinInitializationSettings(
      requestAlertPermission: true,
      requestBadgePermission: true,
      requestSoundPermission: true,
      onDidReceiveLocalNotification: (id, title, body, payload) async {
        // Handle iOS foreground notification (iOS < 10)
      },
    );

    final settings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      settings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
      onDidReceiveBackgroundNotificationResponse: _onBackgroundNotificationTapped,
    );

    // Create Android notification channels
    if (Platform.isAndroid) {
      await _createNotificationChannels();
    }
  }

  /// إنشاء قنوات الإشعارات (Android)
  Future<void> _createNotificationChannels() async {
    final androidPlugin = _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

    if (androidPlugin == null) return;

    // Main channel
    await androidPlugin.createNotificationChannel(
      const AndroidNotificationChannel(
        'sahool_main',
        'إشعارات سهول',
        description: 'إشعارات التطبيق الرئيسية',
        importance: Importance.high,
      ),
    );

    // Alerts channel
    await androidPlugin.createNotificationChannel(
      const AndroidNotificationChannel(
        'sahool_alerts',
        'التنبيهات',
        description: 'تنبيهات الحقول والري',
        importance: Importance.max,
        enableVibration: true,
        playSound: true,
      ),
    );

    // Tasks channel
    await androidPlugin.createNotificationChannel(
      const AndroidNotificationChannel(
        'sahool_tasks',
        'المهام',
        description: 'تذكيرات المهام',
        importance: Importance.defaultImportance,
      ),
    );

    // Sync channel
    await androidPlugin.createNotificationChannel(
      const AndroidNotificationChannel(
        'sahool_sync',
        'المزامنة',
        description: 'حالة المزامنة',
        importance: Importance.low,
      ),
    );
  }

  /// إعداد معالجات الرسائل
  void _setupMessageHandlers() {
    // Background handler
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Foreground handler
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Message opened app
    FirebaseMessaging.onMessageOpenedApp.listen(_handleMessageOpenedApp);

    // Check for initial message (app opened from terminated state)
    _checkInitialMessage();
  }

  /// معالجة الرسائل في الواجهة
  Future<void> _handleForegroundMessage(RemoteMessage message) async {
    AppLogger.i('Foreground message: ${message.messageId}', tag: 'FCM');

    // Show local notification
    await _showLocalNotification(message);

    // Emit to stream
    _emitNotification(message);
  }

  /// معالجة فتح التطبيق من الإشعار
  void _handleMessageOpenedApp(RemoteMessage message) {
    AppLogger.i('Message opened app: ${message.messageId}', tag: 'FCM');
    _emitNotification(message, tapped: true);
  }

  /// التحقق من رسالة البدء
  Future<void> _checkInitialMessage() async {
    final initialMessage = await _fcm.getInitialMessage();
    if (initialMessage != null) {
      AppLogger.i('Initial message: ${initialMessage.messageId}', tag: 'FCM');
      _emitNotification(initialMessage, tapped: true);
    }
  }

  /// معالجة الرسائل في الخلفية
  static Future<void> _handleBackgroundMessage(RemoteMessage message) async {
    // This is called from the background handler
    // Store notification for later processing if needed
  }

  /// عرض إشعار محلي
  Future<void> _showLocalNotification(RemoteMessage message) async {
    final notification = message.notification;
    final android = message.notification?.android;
    final data = message.data;

    if (notification == null) return;

    // Determine channel based on notification type
    final channel = _getChannelForType(data['type'] as String?);

    await _localNotifications.show(
      notification.hashCode,
      notification.title,
      notification.body,
      NotificationDetails(
        android: AndroidNotificationDetails(
          channel.id,
          channel.name,
          channelDescription: channel.description,
          importance: channel.importance,
          priority: Priority.high,
          icon: android?.smallIcon ?? '@mipmap/ic_launcher',
        ),
        iOS: const DarwinNotificationDetails(
          presentAlert: true,
          presentBadge: true,
          presentSound: true,
        ),
      ),
      payload: jsonEncode(data),
    );
  }

  /// الحصول على القناة المناسبة
  AndroidNotificationChannel _getChannelForType(String? type) {
    switch (type) {
      case 'alert':
      case 'irrigation':
      case 'weather':
        return const AndroidNotificationChannel(
          'sahool_alerts',
          'التنبيهات',
          importance: Importance.max,
        );
      case 'task':
        return const AndroidNotificationChannel(
          'sahool_tasks',
          'المهام',
          importance: Importance.defaultImportance,
        );
      case 'sync':
        return const AndroidNotificationChannel(
          'sahool_sync',
          'المزامنة',
          importance: Importance.low,
        );
      default:
        return const AndroidNotificationChannel(
          'sahool_main',
          'إشعارات سهول',
          importance: Importance.high,
        );
    }
  }

  /// إرسال الإشعار للـ Stream
  void _emitNotification(RemoteMessage message, {bool tapped = false}) {
    final payload = NotificationPayload(
      id: message.messageId ?? '',
      title: message.notification?.title ?? '',
      body: message.notification?.body ?? '',
      data: message.data,
      tapped: tapped,
      receivedAt: DateTime.now(),
    );
    _notificationController.add(payload);
  }

  /// معالجة الضغط على الإشعار
  void _onNotificationTapped(NotificationResponse response) {
    if (response.payload == null) return;

    try {
      final data = jsonDecode(response.payload!) as Map<String, dynamic>;
      final payload = NotificationPayload(
        id: response.id?.toString() ?? '',
        title: '',
        body: '',
        data: data.cast<String, String>(),
        tapped: true,
        receivedAt: DateTime.now(),
      );
      _notificationController.add(payload);
    } catch (e) {
      AppLogger.e('Failed to parse notification payload', tag: 'FCM', error: e);
    }
  }

  /// الحصول على الـ Token
  Future<String?> _getToken() async {
    try {
      _fcmToken = await _fcm.getToken();
      if (_fcmToken != null) {
        AppLogger.d('FCM Token: ${_fcmToken!.substring(0, 20)}...', tag: 'FCM');
      }
      return _fcmToken;
    } catch (e) {
      AppLogger.e('Failed to get FCM token', tag: 'FCM', error: e);
      return null;
    }
  }

  /// الاشتراك في موضوع
  Future<void> subscribeToTopic(String topic) async {
    try {
      await _fcm.subscribeToTopic(topic);
      AppLogger.i('Subscribed to topic: $topic', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to subscribe to topic', tag: 'FCM', error: e);
    }
  }

  /// إلغاء الاشتراك من موضوع
  Future<void> unsubscribeFromTopic(String topic) async {
    try {
      await _fcm.unsubscribeFromTopic(topic);
      AppLogger.i('Unsubscribed from topic: $topic', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to unsubscribe from topic', tag: 'FCM', error: e);
    }
  }

  /// الاشتراك في مواضيع المستخدم
  Future<void> subscribeToUserTopics(String userId, String? tenantId) async {
    await subscribeToTopic('user_$userId');
    if (tenantId != null) {
      await subscribeToTopic('tenant_$tenantId');
    }
    await subscribeToTopic('all_users');
  }

  /// إلغاء اشتراكات المستخدم
  Future<void> unsubscribeFromUserTopics(String userId, String? tenantId) async {
    await unsubscribeFromTopic('user_$userId');
    if (tenantId != null) {
      await unsubscribeFromTopic('tenant_$tenantId');
    }
  }

  /// حذف الـ Token
  Future<void> deleteToken() async {
    try {
      await _fcm.deleteToken();
      _fcmToken = null;
      AppLogger.i('FCM token deleted', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to delete FCM token', tag: 'FCM', error: e);
    }
  }

  /// إغلاق الخدمة
  void dispose() {
    _notificationController.close();
    _tokenController.close();
  }
}

/// Background notification tap handler
@pragma('vm:entry-point')
void _onBackgroundNotificationTapped(NotificationResponse response) {
  // Handle background notification tap
}

/// حمولة الإشعار
class NotificationPayload {
  final String id;
  final String title;
  final String body;
  final Map<String, dynamic> data;
  final bool tapped;
  final DateTime receivedAt;

  const NotificationPayload({
    required this.id,
    required this.title,
    required this.body,
    required this.data,
    required this.tapped,
    required this.receivedAt,
  });

  String? get type => data['type'] as String?;
  String? get targetId => data['targetId'] as String?;
  String? get action => data['action'] as String?;

  @override
  String toString() => 'NotificationPayload(id: $id, title: $title, type: $type)';
}

/// Provider للخدمة
final pushNotificationServiceProvider = Provider<PushNotificationService>((ref) {
  return PushNotificationService.instance;
});

/// Provider للإشعارات
final notificationStreamProvider = StreamProvider<NotificationPayload>((ref) {
  return PushNotificationService.instance.onNotification;
});
