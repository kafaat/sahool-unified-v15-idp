/// SAHOOL Notification Integration Example
/// مثال تكامل الإشعارات
///
/// This file demonstrates how to integrate all notification services
/// في التطبيق الرئيسي (main.dart)

import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import 'push_notification_service.dart';
import 'local_notification_service.dart';
import 'notification_handler.dart';
import 'notification_types.dart';

/// Example: Initialize all notification services in main.dart
///
/// ```dart
/// void main() async {
///   WidgetsFlutterBinding.ensureInitialized();
///
///   // Initialize Firebase
///   await Firebase.initializeApp();
///
///   // Initialize notification services
///   await initializeNotificationServices();
///
///   runApp(MyApp());
/// }
/// ```
Future<void> initializeNotificationServices() async {
  // 1. Initialize Firebase Push Notifications
  final pushService = PushNotificationService.instance;
  await pushService.initialize();

  // 2. Initialize Local Notifications with tap handler
  final localService = LocalNotificationService();
  final handler = NotificationHandler();

  await localService.initialize(
    onTap: (payload) {
      // Handle notification tap
      handler.handleNotificationTap(payload);
    },
  );

  // 3. Request notification permissions
  await localService.requestPermission();

  debugPrint('✅ All notification services initialized');
}

/// Example: Initialize NotificationHandler with router
///
/// ```dart
/// class MyApp extends StatelessWidget {
///   @override
///   Widget build(BuildContext context) {
///     final router = AppRouter.router;
///
///     // Initialize notification handler with router
///     NotificationHandler().initialize(router);
///
///     return MaterialApp.router(
///       routerConfig: router,
///       // ... other configurations
///     );
///   }
/// }
/// ```

/// Example: Listen to push notifications
///
/// ```dart
/// class NotificationListener extends ConsumerWidget {
///   @override
///   Widget build(BuildContext context, WidgetRef ref) {
///     // Listen to notification stream
///     ref.listen(notificationStreamProvider, (previous, next) {
///       next.when(
///         data: (notification) {
///           if (notification.tapped) {
///             // User tapped on notification
///             NotificationHandler().handleNotificationTap(notification.data);
///           } else {
///             // Show in-app notification
///             _showInAppNotification(context, notification);
///           }
///         },
///         error: (error, stack) => debugPrint('Notification error: $error'),
///         loading: () {},
///       );
///     });
///
///     return YourWidget();
///   }
/// }
/// ```

/// Example: Subscribe to topics after login
///
/// ```dart
/// Future<void> onUserLogin(String userId, String? tenantId) async {
///   final pushService = PushNotificationService.instance;
///
///   // Subscribe to user-specific topics
///   await pushService.subscribeToUserTopics(userId, tenantId);
///
///   // Subscribe to additional topics
///   await pushService.subscribeToTopic('weather_alerts');
///   await pushService.subscribeToTopic('system_updates');
/// }
/// ```

/// Example: Send local notification for task reminder
///
/// ```dart
/// Future<void> scheduleTaskReminder({
///   required String taskId,
///   required String fieldId,
///   required String title,
///   required String description,
///   required DateTime reminderTime,
/// }) async {
///   final localService = LocalNotificationService();
///   final handler = NotificationHandler();
///
///   // Create payload for deep linking
///   final payload = handler.parsePayload(
///     handler.createTaskNotificationPayload(
///       taskId: taskId,
///       fieldId: fieldId,
///     ),
///   );
///
///   // Schedule notification
///   await localService.showScheduledNotification(
///     type: NotificationType.taskDue,
///     title: title,
///     body: description,
///     scheduledTime: reminderTime,
///     data: payload,
///   );
/// }
/// ```

/// Example: Show irrigation alert
///
/// ```dart
/// Future<void> showIrrigationAlert({
///   required String fieldId,
///   required String fieldName,
///   required String message,
/// }) async {
///   final localService = LocalNotificationService();
///   final handler = NotificationHandler();
///
///   final payload = handler.parsePayload(
///     handler.createIrrigationNotificationPayload(
///       fieldId: fieldId,
///       additionalData: {'fieldName': fieldName},
///     ),
///   );
///
///   await localService.showNotification(
///     type: NotificationType.irrigationDue,
///     title: 'تنبيه الري - $fieldName',
///     body: message,
///     data: payload,
///   );
/// }
/// ```

/// Example: Show weather alert
///
/// ```dart
/// Future<void> showWeatherAlert({
///   required String fieldId,
///   required String weatherType,
///   required String message,
/// }) async {
///   final localService = LocalNotificationService();
///   final handler = NotificationHandler();
///
///   final payload = handler.parsePayload(
///     handler.createWeatherNotificationPayload(
///       fieldId: fieldId,
///       additionalData: {
///         'weatherType': weatherType,
///         'severity': 'high',
///       },
///     ),
///   );
///
///   await localService.showNotification(
///     type: NotificationType.weatherAlert,
///     title: 'تحذير الطقس',
///     body: message,
///     data: payload,
///   );
/// }
/// ```

/// Example: Show sync progress notification
///
/// ```dart
/// Future<void> showSyncProgress(int current, int total) async {
///   final localService = LocalNotificationService();
///
///   await localService.showProgressNotification(
///     id: 999, // Use fixed ID for sync notification
///     title: 'جاري المزامنة...',
///     body: 'تم مزامنة $current من $total',
///     progress: current,
///     maxProgress: total,
///   );
///
///   // Cancel when complete
///   if (current == total) {
///     await Future.delayed(Duration(seconds: 2));
///     await localService.cancelById(999);
///   }
/// }
/// ```

/// Example: Handle FCM token refresh
///
/// ```dart
/// class TokenRefreshListener extends ConsumerWidget {
///   @override
///   Widget build(BuildContext context, WidgetRef ref) {
///     final pushService = PushNotificationService.instance;
///
///     // Listen to token refresh
///     pushService.onTokenRefresh.listen((token) {
///       // Send token to backend
///       _sendTokenToBackend(token);
///     });
///
///     return YourWidget();
///   }
///
///   Future<void> _sendTokenToBackend(String token) async {
///     // TODO: Send token to your backend API
///     debugPrint('Sending FCM token to backend: $token');
///   }
/// }
/// ```

/// Example: Clear all notifications on logout
///
/// ```dart
/// Future<void> onUserLogout() async {
///   final pushService = PushNotificationService.instance;
///   final localService = LocalNotificationService();
///
///   // Cancel all local notifications
///   await localService.cancelAll();
///
///   // Delete FCM token
///   await pushService.deleteToken();
///
///   // Clear badge
///   await localService.clearBadge();
/// }
/// ```

/// Example: NDVI change notification
///
/// ```dart
/// Future<void> showNdviChangeNotification({
///   required String fieldId,
///   required String fieldName,
///   required double oldValue,
///   required double newValue,
/// }) async {
///   final localService = LocalNotificationService();
///   final handler = NotificationHandler();
///
///   final isImprovement = newValue > oldValue;
///   final type = isImprovement
///       ? NotificationType.ndviImprove
///       : NotificationType.ndviDrop;
///
///   final payload = handler.parsePayload(
///     handler.createNdviNotificationPayload(
///       fieldId: fieldId,
///       additionalData: {
///         'oldValue': oldValue.toString(),
///         'newValue': newValue.toString(),
///       },
///     ),
///   );
///
///   await localService.showNotification(
///     type: type,
///     title: 'تغيير NDVI - $fieldName',
///     body: isImprovement
///         ? 'تحسن صحة المحصول من ${oldValue.toStringAsFixed(2)} إلى ${newValue.toStringAsFixed(2)}'
///         : 'انخفاض صحة المحصول من ${oldValue.toStringAsFixed(2)} إلى ${newValue.toStringAsFixed(2)}',
///     data: payload,
///   );
/// }
/// ```
