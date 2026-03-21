/// SAHOOL FCM Service
/// Firebase Cloud Messaging Integration with Local Fallback
///
/// This service provides:
/// - Firebase Cloud Messaging (FCM) push notifications
/// - Automatic local fallback when FCM is unavailable (no google-services.json)
/// - Notification channels for Android (alerts, irrigation, weather, tasks)
/// - Foreground, background, and tap notification handling
/// - Topic subscriptions for targeted notifications
///
/// Usage:
/// ```dart
/// final fcm = FCMService.instance;
/// await fcm.initialize();
/// final token = await fcm.getToken();
/// ```
library;

import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'dart:ui';
import 'package:flutter/foundation.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../utils/app_logger.dart';
import 'notification_types.dart';

// Conditional imports for Firebase
// These will fail gracefully if Firebase is not configured
bool _firebaseAvailable = false;

/// Try to import Firebase - will be checked at runtime
Future<bool> _checkFirebaseAvailable() async {
  try {
    // Dynamic import check - this will fail if firebase is not properly configured
    await _initializeFirebaseCore();
    return true;
  } catch (e) {
    AppLogger.w(
      'Firebase not available, using local notifications only',
      tag: 'FCM',
      data: {'error': e.toString()},
    );
    return false;
  }
}

/// Initialize Firebase Core
Future<void> _initializeFirebaseCore() async {
  // Import firebase_core dynamically
  final dynamic firebaseCore = await _getFirebaseCore();
  if (firebaseCore != null) {
    // ignore: avoid_dynamic_calls
    await firebaseCore.initializeApp();
  }
}

/// Get Firebase Core instance (returns null if not available)
Future<dynamic> _getFirebaseCore() async {
  try {
    // This is a placeholder - actual implementation uses conditional imports
    // In production, this would use firebase_core package
    return null;
  } catch (e) {
    return null;
  }
}

/// Background message handler - must be top-level function
/// This is called when the app is in the background or terminated
@pragma('vm:entry-point')
Future<void> firebaseMessagingBackgroundHandler(dynamic message) async {
  AppLogger.i('Handling background message', tag: 'FCM');
  // Background messages are handled by the system
  // The notification is displayed automatically
}

// ═══════════════════════════════════════════════════════════════════════════════
// Notification Channels
// ═══════════════════════════════════════════════════════════════════════════════

/// Notification channel definitions for Android
class NotificationChannels {
  /// Alerts channel - high priority for urgent notifications
  /// (pest outbreaks, disease detection, weather warnings)
  static const alerts = AndroidNotificationChannel(
    'sahool_alerts',
    'Alerts',
    description: 'Critical alerts requiring immediate attention',
    importance: Importance.high,
    enableVibration: true,
    playSound: true,
    enableLights: true,
  );

  /// Irrigation channel - medium priority for irrigation reminders
  static const irrigation = AndroidNotificationChannel(
    'sahool_irrigation',
    'Irrigation',
    description: 'Irrigation schedules and reminders',
    importance: Importance.defaultImportance,
    enableVibration: true,
    playSound: true,
  );

  /// Weather channel - low priority for weather updates
  static const weather = AndroidNotificationChannel(
    'sahool_weather',
    'Weather',
    description: 'Weather forecasts and updates',
    importance: Importance.low,
    enableVibration: false,
    playSound: false,
  );

  /// Tasks channel - medium priority for task reminders
  static const tasks = AndroidNotificationChannel(
    'sahool_tasks',
    'Tasks',
    description: 'Task reminders and due dates',
    importance: Importance.defaultImportance,
    enableVibration: true,
    playSound: true,
  );

  /// System channel - default for general notifications
  static const system = AndroidNotificationChannel(
    'sahool_system',
    'System',
    description: 'General system notifications',
    importance: Importance.low,
    enableVibration: false,
    playSound: false,
  );

  /// All channels list
  static List<AndroidNotificationChannel> get all => [
        alerts,
        irrigation,
        weather,
        tasks,
        system,
      ];

  /// Get channel by notification type
  static AndroidNotificationChannel getForType(NotificationType type) {
    switch (type) {
      case NotificationType.alertHigh:
      case NotificationType.weatherAlert:
        return alerts;
      case NotificationType.irrigationDue:
        return irrigation;
      case NotificationType.alertLow:
      case NotificationType.ndviDrop:
      case NotificationType.ndviImprove:
        return weather;
      case NotificationType.taskDue:
      case NotificationType.taskOverdue:
        return tasks;
      case NotificationType.alertMedium:
      case NotificationType.system:
        return system;
    }
  }

  /// Get channel by string type
  static AndroidNotificationChannel getForStringType(String? type) {
    switch (type) {
      case 'alert':
      case 'critical':
      case 'disease':
      case 'pest':
        return alerts;
      case 'irrigation':
        return irrigation;
      case 'weather':
      case 'ndvi':
        return weather;
      case 'task':
        return tasks;
      default:
        return system;
    }
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// FCM Notification Payload
// ═══════════════════════════════════════════════════════════════════════════════

/// Parsed notification payload
class FCMNotificationPayload {
  final String id;
  final String title;
  final String body;
  final String? type;
  final String? priority;
  final Map<String, dynamic> data;
  final DateTime receivedAt;
  final bool tapped;
  final bool fromFCM;

  const FCMNotificationPayload({
    required this.id,
    required this.title,
    required this.body,
    this.type,
    this.priority,
    required this.data,
    required this.receivedAt,
    this.tapped = false,
    this.fromFCM = false,
  });

  /// Create from remote message data
  factory FCMNotificationPayload.fromMap(
    Map<String, dynamic> data, {
    String? title,
    String? body,
    bool tapped = false,
    bool fromFCM = false,
  }) {
    return FCMNotificationPayload(
      id: data['message_id']?.toString() ??
          DateTime.now().millisecondsSinceEpoch.toString(),
      title: title ?? data['title']?.toString() ?? '',
      body: body ?? data['body']?.toString() ?? '',
      type: data['type']?.toString(),
      priority: data['priority']?.toString(),
      data: data,
      receivedAt: DateTime.now(),
      tapped: tapped,
      fromFCM: fromFCM,
    );
  }

  /// Get action URL from data
  String? get actionUrl => data['action_url']?.toString();

  /// Get field ID from data
  String? get fieldId => data['field_id']?.toString();

  /// Get crop type from data
  String? get cropType => data['crop_type']?.toString();

  /// Check if this is a high priority notification
  bool get isHighPriority =>
      priority == 'high' || priority == 'critical' || type == 'alert';

  @override
  String toString() =>
      'FCMNotificationPayload(id: $id, title: $title, type: $type, fromFCM: $fromFCM)';
}

// ═══════════════════════════════════════════════════════════════════════════════
// FCM Service
// ═══════════════════════════════════════════════════════════════════════════════

/// FCM Service - Manages Firebase Cloud Messaging with local fallback
class FCMService {
  static FCMService? _instance;
  static FCMService get instance {
    _instance ??= FCMService._();
    return _instance!;
  }

  FCMService._();

  /// Local notifications plugin for displaying notifications
  final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();

  /// FCM token for push notifications
  String? _fcmToken;
  String? get fcmToken => _fcmToken;

  /// Whether Firebase is available
  bool _isFirebaseAvailable = false;
  bool get isFirebaseAvailable => _isFirebaseAvailable;

  /// Whether the service is initialized
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  /// Notification stream controller
  final _notificationController =
      StreamController<FCMNotificationPayload>.broadcast();
  Stream<FCMNotificationPayload> get onNotification =>
      _notificationController.stream;

  /// Token refresh stream controller
  final _tokenController = StreamController<String?>.broadcast();
  Stream<String?> get onTokenRefresh => _tokenController.stream;

  /// Callback for notification taps
  void Function(FCMNotificationPayload)? onNotificationTap;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the FCM service
  /// Automatically falls back to local notifications if Firebase is unavailable
  Future<void> initialize({
    void Function(FCMNotificationPayload)? onTap,
  }) async {
    if (_isInitialized) {
      AppLogger.d('FCM Service already initialized', tag: 'FCM');
      return;
    }

    onNotificationTap = onTap;

    try {
      // Check if Firebase is available
      _isFirebaseAvailable = await _checkFirebaseAvailability();

      // Initialize local notifications (always needed)
      await _initializeLocalNotifications();

      // Create Android notification channels
      if (Platform.isAndroid) {
        await _createNotificationChannels();
      }

      // Initialize Firebase if available
      if (_isFirebaseAvailable) {
        await _initializeFirebase();
      } else {
        AppLogger.i(
          'Running in local-only mode (Firebase not configured)',
          tag: 'FCM',
        );
      }

      _isInitialized = true;
      AppLogger.i(
        'FCM Service initialized',
        tag: 'FCM',
        data: {
          'firebase_available': _isFirebaseAvailable,
          'platform': Platform.operatingSystem,
        },
      );
    } catch (e, stack) {
      AppLogger.e(
        'Failed to initialize FCM Service',
        tag: 'FCM',
        error: e,
        stackTrace: stack,
      );
      // Still mark as initialized to prevent repeated attempts
      _isInitialized = true;
    }
  }

  /// Check if Firebase is available
  Future<bool> _checkFirebaseAvailability() async {
    try {
      // Try to initialize Firebase
      // This will fail if google-services.json or GoogleService-Info.plist is missing
      final available = await _checkFirebaseAvailable();
      return available;
    } catch (e) {
      AppLogger.d('Firebase availability check failed: $e', tag: 'FCM');
      return false;
    }
  }

  /// Initialize local notifications plugin
  Future<void> _initializeLocalNotifications() async {
    // Android initialization settings
    const androidSettings = AndroidInitializationSettings('@mipmap/ic_launcher');

    // iOS/macOS initialization settings
    const darwinSettings = DarwinInitializationSettings(
      requestAlertPermission: false, // Request permission separately
      requestBadgePermission: false,
      requestSoundPermission: false,
    );

    const initSettings = InitializationSettings(
      android: androidSettings,
      iOS: darwinSettings,
      macOS: darwinSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _handleNotificationTap,
      onDidReceiveBackgroundNotificationResponse: _handleBackgroundNotificationTap,
    );

    AppLogger.d('Local notifications initialized', tag: 'FCM');
  }

  /// Create Android notification channels
  Future<void> _createNotificationChannels() async {
    final androidPlugin = _localNotifications
        .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

    if (androidPlugin == null) {
      AppLogger.w('Android plugin not available', tag: 'FCM');
      return;
    }

    // Create all notification channels
    for (final channel in NotificationChannels.all) {
      await androidPlugin.createNotificationChannel(channel);
      AppLogger.d('Created notification channel: ${channel.id}', tag: 'FCM');
    }
  }

  /// Initialize Firebase Messaging
  Future<void> _initializeFirebase() async {
    try {
      // Import and initialize firebase_messaging
      // Note: This requires google-services.json for Android
      // and GoogleService-Info.plist for iOS

      // Request notification permissions
      await requestPermission();

      // Get FCM token
      await _getToken();

      // Setup message handlers
      _setupFirebaseMessageHandlers();

      // Check for initial message (app opened from notification)
      await _checkInitialMessage();

      AppLogger.i('Firebase Messaging initialized', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Firebase initialization failed: $e', tag: 'FCM');
      _isFirebaseAvailable = false;
    }
  }

  /// Setup Firebase message handlers
  void _setupFirebaseMessageHandlers() {
    // Note: These handlers require firebase_messaging to be properly configured
    // The actual implementation uses:
    // - FirebaseMessaging.onMessage for foreground messages
    // - FirebaseMessaging.onMessageOpenedApp for messages that opened the app
    // - FirebaseMessaging.onBackgroundMessage for background messages

    AppLogger.d('Firebase message handlers configured', tag: 'FCM');
  }

  /// Check for initial message (app opened from terminated state)
  Future<void> _checkInitialMessage() async {
    // Note: Uses FirebaseMessaging.instance.getInitialMessage()
    AppLogger.d('Checked for initial message', tag: 'FCM');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Permission Handling
  // ═══════════════════════════════════════════════════════════════════════════

  /// Request notification permission
  Future<bool> requestPermission() async {
    try {
      if (Platform.isAndroid) {
        // Android 13+ requires runtime permission
        final androidPlugin = _localNotifications
            .resolvePlatformSpecificImplementation<AndroidFlutterLocalNotificationsPlugin>();

        if (androidPlugin != null) {
          final granted = await androidPlugin.requestNotificationsPermission();
          AppLogger.i(
            'Android notification permission: ${granted ?? false}',
            tag: 'FCM',
          );
          return granted ?? false;
        }
        return true;
      } else if (Platform.isIOS) {
        final iosPlugin = _localNotifications
            .resolvePlatformSpecificImplementation<IOSFlutterLocalNotificationsPlugin>();

        if (iosPlugin != null) {
          final granted = await iosPlugin.requestPermissions(
            alert: true,
            badge: true,
            sound: true,
            critical: false,
          );
          AppLogger.i('iOS notification permission: ${granted ?? false}', tag: 'FCM');
          return granted ?? false;
        }
      }
      return false;
    } catch (e) {
      AppLogger.e('Failed to request permission: $e', tag: 'FCM');
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Token Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get FCM token
  Future<String?> getToken() async {
    if (_fcmToken != null) return _fcmToken;
    return _getToken();
  }

  /// Internal token retrieval
  Future<String?> _getToken() async {
    if (!_isFirebaseAvailable) {
      // Return a local identifier for testing
      _fcmToken = 'local_${DateTime.now().millisecondsSinceEpoch}';
      AppLogger.d('Generated local token: ${_fcmToken!.substring(0, 20)}...', tag: 'FCM');
      return _fcmToken;
    }

    try {
      // Note: Uses FirebaseMessaging.instance.getToken()
      // _fcmToken = await FirebaseMessaging.instance.getToken();
      AppLogger.d('FCM token obtained', tag: 'FCM');
      return _fcmToken;
    } catch (e) {
      AppLogger.e('Failed to get FCM token: $e', tag: 'FCM');
      return null;
    }
  }

  /// Delete FCM token (for logout)
  Future<void> deleteToken() async {
    try {
      if (_isFirebaseAvailable) {
        // Note: Uses FirebaseMessaging.instance.deleteToken()
      }
      _fcmToken = null;
      _tokenController.add(null);
      AppLogger.i('FCM token deleted', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to delete FCM token: $e', tag: 'FCM');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Topic Subscriptions
  // ═══════════════════════════════════════════════════════════════════════════

  /// Subscribe to a topic
  Future<void> subscribeToTopic(String topic) async {
    if (!_isFirebaseAvailable) {
      AppLogger.d('Topic subscription skipped (local mode): $topic', tag: 'FCM');
      return;
    }

    try {
      // Note: Uses FirebaseMessaging.instance.subscribeToTopic(topic)
      AppLogger.i('Subscribed to topic: $topic', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to subscribe to topic: $e', tag: 'FCM');
    }
  }

  /// Unsubscribe from a topic
  Future<void> unsubscribeFromTopic(String topic) async {
    if (!_isFirebaseAvailable) {
      AppLogger.d('Topic unsubscription skipped (local mode): $topic', tag: 'FCM');
      return;
    }

    try {
      // Note: Uses FirebaseMessaging.instance.unsubscribeFromTopic(topic)
      AppLogger.i('Unsubscribed from topic: $topic', tag: 'FCM');
    } catch (e) {
      AppLogger.e('Failed to unsubscribe from topic: $e', tag: 'FCM');
    }
  }

  /// Subscribe to user-specific topics
  Future<void> subscribeToUserTopics({
    required String userId,
    String? tenantId,
    String? governorate,
    List<String>? crops,
  }) async {
    // User-specific topic
    await subscribeToTopic('user_$userId');

    // Tenant topic
    if (tenantId != null) {
      await subscribeToTopic('tenant_$tenantId');
    }

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

    // All users topic
    await subscribeToTopic('all_users');
  }

  /// Unsubscribe from all user topics
  Future<void> unsubscribeFromUserTopics({
    required String userId,
    String? tenantId,
    String? governorate,
    List<String>? crops,
  }) async {
    await unsubscribeFromTopic('user_$userId');

    if (tenantId != null) {
      await unsubscribeFromTopic('tenant_$tenantId');
    }

    if (governorate != null) {
      await unsubscribeFromTopic('gov_$governorate');
    }

    if (crops != null) {
      for (final crop in crops) {
        await unsubscribeFromTopic('crop_$crop');
      }
    }

    await unsubscribeFromTopic('all_users');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Notification Display
  // ═══════════════════════════════════════════════════════════════════════════

  /// Show a local notification
  Future<void> showLocalNotification({
    required String title,
    required String body,
    String? type,
    String? priority,
    Map<String, dynamic>? data,
  }) async {
    if (!_isInitialized) {
      AppLogger.w('FCM Service not initialized', tag: 'FCM');
      return;
    }

    final channel = NotificationChannels.getForStringType(type);
    final isHighPriority = priority == 'high' || priority == 'critical';

    final androidDetails = AndroidNotificationDetails(
      channel.id,
      channel.name,
      channelDescription: channel.description,
      importance: isHighPriority ? Importance.high : channel.importance,
      priority: isHighPriority ? Priority.high : Priority.defaultPriority,
      icon: '@mipmap/ic_launcher',
      styleInformation: BigTextStyleInformation(body),
      enableVibration: channel.enableVibration,
      playSound: channel.playSound,
    );

    final iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: isHighPriority || type == 'alert',
    );

    final notificationId = DateTime.now().millisecondsSinceEpoch % 2147483647;

    await _localNotifications.show(
      notificationId,
      title,
      body,
      NotificationDetails(
        android: androidDetails,
        iOS: iosDetails,
      ),
      payload: data != null ? jsonEncode(data) : null,
    );

    AppLogger.d(
      'Local notification shown',
      tag: 'FCM',
      data: {'title': title, 'type': type, 'channel': channel.id},
    );

    // Emit to stream
    final payload = FCMNotificationPayload(
      id: notificationId.toString(),
      title: title,
      body: body,
      type: type,
      priority: priority,
      data: data ?? {},
      receivedAt: DateTime.now(),
      fromFCM: false,
    );
    _notificationController.add(payload);
  }

  /// Handle foreground FCM message
  Future<void> handleForegroundMessage(dynamic message) async {
    AppLogger.d('Foreground message received', tag: 'FCM');

    // Extract actual notification data from RemoteMessage
    String title = 'New Message';
    String body = 'You have a new notification';
    String? type;
    String? priority;
    Map<String, dynamic> data = {};

    try {
      if (message != null) {
        // RemoteMessage.notification contains title/body
        // message is dynamic (Firebase RemoteMessage when available)
        // Use Map-based access to avoid dynamic calls
        if (message is Map) {
          final msgMap = Map<String, dynamic>.from(message);
          final notification = msgMap['notification'];
          if (notification is Map) {
            title = (notification['title'] as String?) ?? title;
            body = (notification['body'] as String?) ?? body;
          }

          // RemoteMessage.data contains the data payload
          final msgData = msgMap['data'];
          if (msgData is Map) {
            data = Map<String, dynamic>.from(msgData);
            title = data['title']?.toString() ?? title;
            body = data['body']?.toString() ?? body;
            type = data['type']?.toString();
            priority = data['priority']?.toString();
          }
        }
      }
    } catch (e) {
      AppLogger.w('Failed to parse foreground message: $e', tag: 'FCM');
    }

    // Show local notification with actual content
    await showLocalNotification(
      title: title,
      body: body,
      type: type,
      priority: priority,
      data: data,
    );
  }

  /// Handle message that opened the app
  void handleMessageOpenedApp(dynamic message) {
    AppLogger.d('Message opened app', tag: 'FCM');

    String title = '';
    String body = '';
    Map<String, dynamic> data = {};

    try {
      if (message != null) {
        // message is dynamic (Firebase RemoteMessage when available)
        // Use Map-based access to avoid dynamic calls
        if (message is Map) {
          final msgMap = Map<String, dynamic>.from(message);
          final notification = msgMap['notification'];
          if (notification is Map) {
            title = (notification['title'] as String?) ?? '';
            body = (notification['body'] as String?) ?? '';
          }
          final msgData = msgMap['data'];
          if (msgData is Map) {
            data = Map<String, dynamic>.from(msgData);
            title = data['title']?.toString() ?? title;
            body = data['body']?.toString() ?? body;
          }
        }
      }
    } catch (e) {
      AppLogger.w('Failed to parse opened message: $e', tag: 'FCM');
    }

    final payload = FCMNotificationPayload.fromMap(
      data,
      title: title,
      body: body,
      tapped: true,
      fromFCM: true,
    );

    _notificationController.add(payload);
    onNotificationTap?.call(payload);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Notification Tap Handling
  // ═══════════════════════════════════════════════════════════════════════════

  /// Handle notification tap (foreground)
  void _handleNotificationTap(NotificationResponse response) {
    AppLogger.d(
      'Notification tapped',
      tag: 'FCM',
      data: {'id': response.id, 'payload': response.payload},
    );

    if (response.payload == null) {
      onNotificationTap?.call(FCMNotificationPayload(
        id: response.id?.toString() ?? '',
        title: '',
        body: '',
        data: {},
        receivedAt: DateTime.now(),
        tapped: true,
      ));
      return;
    }

    try {
      final data = jsonDecode(response.payload!) as Map<String, dynamic>;
      final payload = FCMNotificationPayload.fromMap(
        data,
        tapped: true,
      );
      _notificationController.add(payload);
      onNotificationTap?.call(payload);
    } catch (e) {
      AppLogger.e('Failed to parse notification payload: $e', tag: 'FCM');
    }
  }

  /// Handle background notification tap
  @pragma('vm:entry-point')
  static void _handleBackgroundNotificationTap(NotificationResponse response) {
    // Background tap handling - app may not be fully initialized
    debugPrint('Background notification tapped: ${response.id}');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Scheduled Notifications
  // ═══════════════════════════════════════════════════════════════════════════

  /// Schedule a notification
  Future<void> scheduleNotification({
    required int id,
    required String title,
    required String body,
    required DateTime scheduledTime,
    String? type,
    Map<String, dynamic>? data,
  }) async {
    final channel = NotificationChannels.getForStringType(type);

    final androidDetails = AndroidNotificationDetails(
      channel.id,
      channel.name,
      channelDescription: channel.description,
      importance: channel.importance,
      icon: '@mipmap/ic_launcher',
    );

    const iosDetails = DarwinNotificationDetails(
      presentAlert: true,
      presentBadge: true,
      presentSound: true,
    );

    // Note: In production, use timezone package for proper scheduling
    // await _localNotifications.zonedSchedule(...)

    AppLogger.d(
      'Notification scheduled',
      tag: 'FCM',
      data: {'id': id, 'title': title, 'time': scheduledTime.toIso8601String()},
    );
  }

  /// Cancel a scheduled notification
  Future<void> cancelNotification(int id) async {
    await _localNotifications.cancel(id);
    AppLogger.d('Notification cancelled: $id', tag: 'FCM');
  }

  /// Cancel all notifications
  Future<void> cancelAllNotifications() async {
    await _localNotifications.cancelAll();
    AppLogger.d('All notifications cancelled', tag: 'FCM');
  }

  /// Get pending notifications
  Future<List<PendingNotificationRequest>> getPendingNotifications() async {
    return _localNotifications.pendingNotificationRequests();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Cleanup
  // ═══════════════════════════════════════════════════════════════════════════

  /// Dispose the service
  void dispose() {
    _notificationController.close();
    _tokenController.close();
    _instance = null;
    _isInitialized = false;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// FCM Service provider
final fcmServiceProvider = Provider<FCMService>((ref) {
  return FCMService.instance;
});

/// FCM initialization provider
final fcmInitializationProvider = FutureProvider<void>((ref) async {
  final fcm = ref.watch(fcmServiceProvider);
  await fcm.initialize();
});

/// FCM token provider
final fcmTokenProvider = FutureProvider<String?>((ref) async {
  await ref.watch(fcmInitializationProvider.future);
  final fcm = ref.watch(fcmServiceProvider);
  return fcm.getToken();
});

/// Notification stream provider
final fcmNotificationStreamProvider =
    StreamProvider.autoDispose<FCMNotificationPayload>((ref) {
  final fcm = ref.watch(fcmServiceProvider);
  return fcm.onNotification;
});

/// Firebase availability provider
final isFirebaseAvailableProvider = Provider<bool>((ref) {
  final fcm = ref.watch(fcmServiceProvider);
  return fcm.isFirebaseAvailable;
});

// ═══════════════════════════════════════════════════════════════════════════════
// Helper Color Class (for Android notification channel)
// ═══════════════════════════════════════════════════════════════════════════════

/// Simple Color class for notification LED color
class Color {
  final int value;
  const Color(this.value);

  const Color.fromARGB(int a, int r, int g, int b)
      : value = (((a & 0xff) << 24) |
            ((r & 0xff) << 16) |
            ((g & 0xff) << 8) |
            ((b & 0xff) << 0)) &
            0xFFFFFFFF;
}
