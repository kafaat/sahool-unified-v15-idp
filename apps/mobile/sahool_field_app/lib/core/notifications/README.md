# SAHOOL Notifications System

# نظام إشعارات سهول

## Overview / نظرة عامة

This directory contains the complete notifications infrastructure for the SAHOOL mobile application, including local notifications, scheduled notifications, and the structure for push notifications when Firebase is enabled.

يحتوي هذا المجلد على البنية التحتية الكاملة للإشعارات لتطبيق سهول المحمول، بما في ذلك الإشعارات المحلية والمجدولة وهيكل الإشعارات الفورية عند تفعيل Firebase.

## Current Status / الحالة الحالية

- **Local Notifications**: Fully functional
- **Scheduled Notifications**: Fully functional
- **Push Notifications (Firebase)**: Disabled (structure ready for when Firebase is added)

- **الإشعارات المحلية**: تعمل بالكامل
- **الإشعارات المجدولة**: تعمل بالكامل
- **الإشعارات الفورية (Firebase)**: معطلة (الهيكل جاهز لإضافة Firebase)

## Files / الملفات

### Core Services / الخدمات الأساسية

| File | Description | الوصف |
|------|-------------|--------|
| `notification_manager.dart` | Central notification manager (unified interface) | مدير الإشعارات المركزي |
| `notification_service.dart` | Abstract notification service with implementation | خدمة الإشعارات المجردة مع التنفيذ |
| `local_notification_service.dart` | Local notifications using flutter_local_notifications | الإشعارات المحلية |
| `push_notification_service.dart` | Push notification service (local mode when Firebase disabled) | خدمة الإشعارات الفورية |
| `notification_handler.dart` | Notification tap handling and deep linking | معالجة النقر على الإشعارات والروابط العميقة |

### Configuration / الإعدادات

| File | Description | الوصف |
|------|-------------|--------|
| `notification_types.dart` | Notification types, channels, and priorities | أنواع الإشعارات والقنوات والأولويات |
| `notification_settings.dart` | User notification settings (per SharedPreferences) | إعدادات إشعارات المستخدم |
| `notification_preferences.dart` | Notification preferences model and service | نموذج وخدمة تفضيلات الإشعارات |

### Providers / المزودات

| File | Description | الوصف |
|------|-------------|--------|
| `notification_provider.dart` | Riverpod providers for notifications | مزودات Riverpod للإشعارات |
| `notifications.dart` | Barrel export file | ملف التصدير |

### Disabled Files / الملفات المعطلة

Files with `.firebase_disabled` extension are templates for when Firebase is enabled:

- `firebase_messaging_service.dart.firebase_disabled`
- `push_notification_service.dart.firebase_disabled`
- `notification_integration_example.dart.firebase_disabled`

## Notification Channels / قنوات الإشعارات (Android)

| Channel ID | Name (AR) | Priority | Use Case |
|------------|-----------|----------|----------|
| `sahool_alerts` | التنبيهات العاجلة | Max | Weather, disease, pest alerts |
| `sahool_tasks` | المهام والتذكيرات | High | Task, harvest, irrigation reminders |
| `sahool_field_updates` | تحديثات الحقل | Default | Satellite images, crop health |
| `sahool_financial` | المالية والأسواق | Default | Payments, market prices |
| `sahool_operations` | العمليات الزراعية | High | Spray window, operations |
| `sahool_inventory` | المخزون | Low | Inventory alerts |
| `sahool_main` | إشعارات سهول | Default | General notifications |
| `sahool_sync` | المزامنة | Low | Sync progress |

## Quick Start / البدء السريع

### 1. Initialization (in main.dart)

```dart
import 'core/notifications/notification_manager.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize notification system
  await NotificationManager.instance.initialize();
  await NotificationManager.instance.requestPermission();

  runApp(MyApp());
}
```

### 2. Show a Local Notification

```dart
import 'package:sahool_field_app/core/notifications/notifications.dart';

// Show immediate notification
await NotificationManager.instance.showNotification(
  title: 'تنبيه الري',
  body: 'حان موعد ري حقل الطماطم',
  type: SAHOOLNotificationType.irrigationReminder,
  priority: NotificationPriority.high,
  data: {'field_id': 'field123'},
);
```

### 3. Schedule a Notification

```dart
// Schedule notification for later
await NotificationManager.instance.scheduleNotification(
  title: 'مهمة قادمة',
  body: 'فحص آفات القطن غداً',
  scheduledTime: DateTime.now().add(Duration(hours: 24)),
  type: SAHOOLNotificationType.taskReminder,
  data: {'task_id': 'task456', 'field_id': 'field123'},
);
```

### 4. Using Riverpod Providers

```dart
// In a ConsumerWidget:
@override
Widget build(BuildContext context, WidgetRef ref) {
  // Watch notification initialization
  final notificationInit = ref.watch(notificationInitializedProvider);

  // Watch incoming notifications
  final notifications = ref.watch(notificationStreamProvider);

  // Use notification actions
  final notificationActions = ref.read(notificationActionsProvider.notifier);

  await notificationActions.showNotification(
    title: 'عنوان الإشعار',
    body: 'محتوى الإشعار',
  );
}
```

### 5. Cancel Notifications

```dart
// Cancel specific notification
await NotificationManager.instance.cancelNotification(notificationId);

// Cancel all notifications
await NotificationManager.instance.cancelAllNotifications();

// Get pending notifications
final pending = await NotificationManager.instance.getPendingNotifications();
```

## Notification Types / أنواع الإشعارات

```dart
enum SAHOOLNotificationType {
  weatherAlert,        // تنبيه طقس
  diseaseDetected,     // كشف مرض
  pestOutbreak,        // انتشار آفة
  sprayWindow,         // وقت الرش
  harvestReminder,     // تذكير الحصاد
  irrigationReminder,  // تذكير الري
  taskReminder,        // تذكير مهمة
  fieldUpdate,         // تحديث الحقل
  satelliteReady,      // صور الأقمار جاهزة
  cropHealth,          // صحة المحصول
  marketPrice,         // أسعار السوق
  paymentDue,          // دفعة مستحقة
  lowStock,            // مخزون منخفض
  system,              // إشعار نظام
}
```

## Priority Levels / مستويات الأولوية

```dart
enum NotificationPriority {
  low,      // منخفض - for informational notifications
  medium,   // متوسط - default priority
  high,     // عالي - important notifications
  critical, // حرج - urgent notifications (ignore quiet hours)
}
```

## User Preferences / تفضيلات المستخدم

Users can configure:

- Enable/disable specific notification types
- Quiet hours (no notifications during sleep)
- Sound and vibration settings
- Minimum priority threshold
- Badge and preview settings

```dart
// Get current preferences
final prefs = NotificationPreferencesService.instance.getPreferences();

// Update preferences
await NotificationPreferencesService.instance.updatePreference(
  (prefs) => prefs.copyWith(
    enableQuietHours: true,
    quietHoursStart: TimeOfDay(hour: 22, minute: 0),
    quietHoursEnd: TimeOfDay(hour: 6, minute: 0),
  ),
);
```

## Handling Notification Taps / معالجة النقر على الإشعارات

```dart
// Initialize handler with navigator key
NotificationHandler.instance.initialize(navigatorKey);

// Listen to notification taps
NotificationHandler.instance.onNotification.listen((payload) {
  // Handle notification tap
  print('Notification tapped: ${payload.type}');
  print('Field ID: ${payload.fieldId}');
});
```

## Enabling Firebase Push Notifications / تفعيل إشعارات Firebase

When you're ready to enable Firebase:

1. Uncomment Firebase dependencies in `pubspec.yaml`:
   ```yaml
   firebase_core: ^3.8.1
   firebase_messaging: ^15.1.5
   ```

2. Add Firebase configuration files:
   - `android/app/google-services.json`
   - `ios/Runner/GoogleService-Info.plist`

3. Set `firebaseEnabled = true` in `push_notification_service.dart`:
   ```dart
   class PushNotificationConfig {
     static const bool firebaseEnabled = true;
   }
   ```

4. Rename `.firebase_disabled` files back to `.dart`

5. Update `notifications.dart` to export Firebase services

## Android Configuration / إعدادات أندرويد

Add to `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
<uses-permission android:name="android.permission.VIBRATE"/>
<uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED"/>
<uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM"/>
```

## iOS Configuration / إعدادات iOS

Add to `ios/Runner/Info.plist`:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>remote-notification</string>
</array>
```

## Testing / الاختبار

```dart
// Test immediate notification
await NotificationManager.instance.showNotification(
  title: 'Test Notification',
  body: 'This is a test notification',
  type: SAHOOLNotificationType.system,
);

// Test scheduled notification (5 seconds from now)
await NotificationManager.instance.scheduleNotification(
  title: 'Scheduled Test',
  body: 'This notification was scheduled',
  scheduledTime: DateTime.now().add(Duration(seconds: 5)),
);

// Simulate push notification (for testing without Firebase)
await PushNotificationService.instance.simulatePushNotification(
  title: 'Simulated Push',
  body: 'This simulates a push notification',
  type: SAHOOLNotificationType.weatherAlert,
);
```

## Troubleshooting / استكشاف الأخطاء

### Notifications not showing

1. Check permissions are granted:
   ```dart
   final enabled = await NotificationManager.instance.areNotificationsEnabled();
   ```

2. Verify notification channels are created (Android)

3. Check Android app notification settings

### Scheduled notifications not working

1. Ensure `SCHEDULE_EXACT_ALARM` permission is granted (Android 12+)

2. Verify scheduled time is in the future

3. Check that the app is not battery-optimized

### Deep linking not working

1. Verify NotificationHandler is initialized with navigator key

2. Check payload contains correct route data

3. Verify routes exist in app_router.dart

## Best Practices / أفضل الممارسات

1. Always request permissions before showing notifications
2. Use appropriate channels for different notification types
3. Include meaningful payload data for deep linking
4. Handle notification taps gracefully
5. Clear notifications when user logs out
6. Respect user preferences (quiet hours, disabled types)
7. Use progress notifications for long-running operations

---

Built for SAHOOL Agricultural Platform
تم بناؤه لمنصة سهول الزراعية
