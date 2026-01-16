# SAHOOL Push Notifications Infrastructure

# بنية الإشعارات الفورية لسهول

## Overview / نظرة عامة

This directory contains the complete push notifications infrastructure for the SAHOOL mobile application, including Firebase Cloud Messaging (FCM) integration, local notifications, and deep linking capabilities.

يحتوي هذا المجلد على البنية التحتية الكاملة للإشعارات الفورية لتطبيق سهول المحمول، بما في ذلك تكامل Firebase Cloud Messaging (FCM) والإشعارات المحلية وقدرات الروابط العميقة.

## Files / الملفات

### Core Services / الخدمات الأساسية

1. **notification_service.dart**
   - Main notification service for handling push notifications
   - Abstract interface with implementation
   - خدمة الإشعارات الرئيسية لمعالجة الإشعارات الفورية

2. **push_notification_service.dart**
   - Firebase Cloud Messaging (FCM) integration
   - Background and foreground message handling
   - Topic subscriptions and token management
   - تكامل Firebase Cloud Messaging
   - معالجة الرسائل في الخلفية والواجهة
   - اشتراكات المواضيع وإدارة الرموز

3. **local_notification_service.dart**
   - Local notifications using flutter_local_notifications
   - Support for different notification channels (tasks, weather, alerts)
   - Scheduled notifications
   - Progress notifications
   - الإشعارات المحلية باستخدام flutter_local_notifications
   - دعم قنوات الإشعارات المختلفة (المهام، الطقس، التنبيهات)

4. **notification_handler.dart**
   - Handle notification tap actions
   - Deep linking to specific screens based on notification data
   - Parse and build notification payloads
   - معالجة إجراءات النقر على الإشعارات
   - الروابط العميقة للشاشات المحددة

### Supporting Files / الملفات الداعمة

5. **notification_types.dart**
   - Notification type enumerations
   - Channel configurations
   - أنواع الإشعارات
   - إعدادات القنوات

6. **notification_settings.dart**
   - User notification preferences
   - Settings management
   - إعدادات إشعارات المستخدم

7. **notifications.dart**
   - Export file for all notification services
   - ملف التصدير لجميع خدمات الإشعارات

## Notification Channels / قنوات الإشعارات

The app supports the following notification channels:

### 1. Alerts / التنبيهات

- **Channel ID**: `alerts`
- **Priority**: High
- **Use Case**: Farm and field alerts, urgent notifications
- **الاستخدام**: تنبيهات المزرعة والحقول

### 2. Tasks / المهام

- **Channel ID**: `tasks`
- **Priority**: Default
- **Use Case**: Task reminders and due dates
- **الاستخدام**: تذكيرات المهام والمواعيد النهائية

### 3. NDVI

- **Channel ID**: `ndvi`
- **Priority**: Default
- **Use Case**: Crop health changes and NDVI updates
- **الاستخدام**: تغييرات صحة المحصول وتحديثات NDVI

### 4. Irrigation / الري

- **Channel ID**: `irrigation`
- **Priority**: High
- **Use Case**: Irrigation scheduling and reminders
- **الاستخدام**: جدولة الري والتذكيرات

### 5. Weather / الطقس

- **Channel ID**: `weather`
- **Priority**: High
- **Use Case**: Weather alerts and warnings
- **الاستخدام**: تحذيرات الطقس والتنبيهات

### 6. System / النظام

- **Channel ID**: `system`
- **Priority**: Low
- **Use Case**: Sync notifications and system updates
- **الاستخدام**: إشعارات المزامنة وتحديثات النظام

## Setup / الإعداد

### 1. Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  flutter_local_notifications: ^18.0.1
  firebase_core: ^3.8.1
  firebase_messaging: ^15.1.5
```

### 2. Firebase Configuration

1. Add `google-services.json` to `android/app/`
2. Add `GoogleService-Info.plist` to `ios/Runner/`
3. Configure Firebase in your Firebase Console

### 3. Android Configuration

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
<uses-permission android:name="android.permission.VIBRATE" />

<application>
    <!-- FCM default channel -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_channel_id"
        android:value="sahool_main" />

    <!-- FCM default icon -->
    <meta-data
        android:name="com.google.firebase.messaging.default_notification_icon"
        android:resource="@mipmap/ic_launcher" />
</application>
```

### 4. iOS Configuration

Add to `ios/Runner/Info.plist`:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>remote-notification</string>
</array>
```

## Usage / الاستخدام

### Initialize Services

```dart
void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Firebase
  await Firebase.initializeApp();

  // Initialize Push Notifications
  final pushService = PushNotificationService.instance;
  await pushService.initialize();

  // Initialize Local Notifications
  final localService = LocalNotificationService();
  final handler = NotificationHandler();

  await localService.initialize(
    onTap: (payload) => handler.handleNotificationTap(payload),
  );

  runApp(MyApp());
}
```

### Initialize Notification Handler

```dart
class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final router = AppRouter.router;

    // Initialize handler with router for deep linking
    NotificationHandler().initialize(router);

    return MaterialApp.router(
      routerConfig: router,
    );
  }
}
```

### Show Local Notification

```dart
final localService = LocalNotificationService();
final handler = NotificationHandler();

await localService.showNotification(
  type: NotificationType.irrigationDue,
  title: 'وقت الري',
  body: 'حان موعد ري حقل الطماطم',
  data: handler.parsePayload(
    handler.createIrrigationNotificationPayload(fieldId: 'field123'),
  ),
);
```

### Schedule Notification

```dart
await localService.showScheduledNotification(
  type: NotificationType.taskDue,
  title: 'مهمة قادمة',
  body: 'فحص آفات القطن',
  scheduledTime: DateTime.now().add(Duration(hours: 2)),
  data: handler.parsePayload(
    handler.createTaskNotificationPayload(
      taskId: 'task123',
      fieldId: 'field456',
    ),
  ),
);
```

### Subscribe to Topics

```dart
final pushService = PushNotificationService.instance;

// Subscribe to user topics
await pushService.subscribeToUserTopics(userId, tenantId);

// Subscribe to specific topics
await pushService.subscribeToTopic('weather_alerts');
await pushService.subscribeToTopic('system_updates');
```

### Handle Token Refresh

```dart
PushNotificationService.instance.onTokenRefresh.listen((token) {
  // Send token to backend
  _sendTokenToBackend(token);
});
```

## Deep Linking / الروابط العميقة

The notification handler supports deep linking to various screens:

### Supported Routes

- `/field/:id` - Field details
- `/field/:id?taskId=xxx` - Field with specific task
- `/alerts` - Alerts screen
- `/map` - Map screen
- `/sync` - Sync screen
- `/advisor` - AI Advisor

### Payload Structure

```json
{
  "type": "irrigation",
  "action": "open_irrigation",
  "fieldId": "field123",
  "targetId": "alert456",
  "timestamp": "2024-12-24T10:00:00.000Z"
}
```

## Testing / الاختبار

### Test Local Notification

```dart
// Show immediate test notification
await localService.showNotification(
  type: NotificationType.system,
  title: 'اختبار',
  body: 'هذا إشعار تجريبي',
);
```

### Test Push Notification

Use Firebase Console to send test messages:

1. Go to Firebase Console > Cloud Messaging
2. Click "Send test message"
3. Enter FCM token
4. Send message

## Troubleshooting / استكشاف الأخطاء

### Common Issues

1. **Notifications not showing**
   - Check permissions are granted
   - Verify notification channels are created
   - Check Android notification settings

2. **FCM token not received**
   - Verify Firebase configuration
   - Check internet connection
   - Verify google-services.json is correct

3. **Deep linking not working**
   - Verify router is initialized in NotificationHandler
   - Check payload structure
   - Verify routes exist in app_router.dart

## Best Practices / أفضل الممارسات

1. Always request permissions before showing notifications
2. Use appropriate channels for different notification types
3. Include meaningful payload data for deep linking
4. Handle notification taps gracefully
5. Clear notifications when user logs out
6. Subscribe to topics after successful login
7. Unsubscribe from topics on logout

## Example Implementation

See `notification_integration_example.dart` for comprehensive examples of:

- Service initialization
- Local notifications
- Push notifications
- Deep linking
- Topic subscriptions
- Progress notifications
- And more...

## Support

For issues or questions:

- Check Firebase documentation: https://firebase.google.com/docs/cloud-messaging
- Flutter local notifications: https://pub.dev/packages/flutter_local_notifications
- SAHOOL project documentation

---

Built with ❤️ for SAHOOL Agricultural Platform
