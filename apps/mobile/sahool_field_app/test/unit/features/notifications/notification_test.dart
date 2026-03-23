import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:sahool_field_app/features/notifications/data/services/notification_service.dart';
import 'package:sahool_field_app/features/notifications/domain/entities/notification_entities.dart';
import 'package:sahool_field_app/features/notifications/presentation/providers/notification_provider.dart';

// ═══════════════════════════════════════════════════════════════════════════════
// Mocks
// ═══════════════════════════════════════════════════════════════════════════════

class MockNotificationService extends Mock implements NotificationService {}

class _FakeNotificationSettings extends Fake implements NotificationSettings {}

class _FakeAppNotification extends Fake implements AppNotification {}

void main() {
  setUpAll(() {
    registerFallbackValue(_FakeNotificationSettings());
    registerFallbackValue(_FakeAppNotification());
  });
  // ═══════════════════════════════════════════════════════════════════════════
  // AppNotification Entity Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('AppNotification', () {
    late DateTime testTime;

    setUp(() {
      testTime = DateTime(2026, 2, 27, 10, 0, 0);
    });

    AppNotification createNotification({
      String id = 'notif-001',
      String type = 'alert',
      bool isRead = false,
    }) {
      return AppNotification(
        id: id,
        type: type,
        title: 'Test Alert',
        titleAr: 'تنبيه تجريبي',
        body: 'This is a test notification',
        bodyAr: 'هذا إشعار تجريبي',
        data: const {'field_id': 'field-001'},
        createdAt: testTime,
        isRead: isRead,
        actionUrl: '/alerts/001',
      );
    }

    test('should create instance with all required fields', () {
      final notification = createNotification();

      expect(notification.id, 'notif-001');
      expect(notification.type, 'alert');
      expect(notification.title, 'Test Alert');
      expect(notification.titleAr, 'تنبيه تجريبي');
      expect(notification.body, 'This is a test notification');
      expect(notification.bodyAr, 'هذا إشعار تجريبي');
      expect(notification.data['field_id'], 'field-001');
      expect(notification.createdAt, testTime);
      expect(notification.isRead, isFalse);
      expect(notification.actionUrl, '/alerts/001');
      expect(notification.imageUrl, isNull);
    });

    test('should default isRead to false', () {
      final notification = AppNotification(
        id: 'notif-002',
        type: 'system',
        title: 'Update',
        titleAr: 'تحديث',
        body: 'System update available',
        bodyAr: 'تحديث النظام متاح',
        data: const {},
        createdAt: testTime,
      );

      expect(notification.isRead, isFalse);
    });

    group('typeIcon', () {
      test('should return alert icon for alert type', () {
        final n = createNotification(type: 'alert');
        expect(n.typeIcon, contains('⚠'));
      });

      test('should return action icon for action type', () {
        final n = createNotification(type: 'action');
        expect(n.typeIcon, contains('📋'));
      });

      test('should return weather icon for weather type', () {
        final n = createNotification(type: 'weather');
        expect(n.typeIcon, contains('🌤'));
      });

      test('should return crop health icon for crop_health type', () {
        final n = createNotification(type: 'crop_health');
        expect(n.typeIcon, contains('🌱'));
      });

      test('should return system icon for system type', () {
        final n = createNotification(type: 'system');
        expect(n.typeIcon, contains('⚙'));
      });

      test('should return default bell icon for unknown type', () {
        final n = createNotification(type: 'unknown');
        expect(n.typeIcon, contains('🔔'));
      });
    });

    group('typeLabel', () {
      test('should return Arabic label for alert', () {
        final n = createNotification(type: 'alert');
        expect(n.typeLabel, 'تنبيه');
      });

      test('should return Arabic label for action', () {
        final n = createNotification(type: 'action');
        expect(n.typeLabel, 'إجراء');
      });

      test('should return Arabic label for weather', () {
        final n = createNotification(type: 'weather');
        expect(n.typeLabel, 'طقس');
      });

      test('should return Arabic label for crop_health', () {
        final n = createNotification(type: 'crop_health');
        expect(n.typeLabel, 'صحة المحصول');
      });

      test('should return Arabic label for system', () {
        final n = createNotification(type: 'system');
        expect(n.typeLabel, 'نظام');
      });

      test('should return default Arabic label for unknown type', () {
        final n = createNotification(type: 'unknown');
        expect(n.typeLabel, 'إشعار');
      });
    });

    group('copyWith', () {
      test('should create copy with isRead changed', () {
        final original = createNotification(isRead: false);
        final read = original.copyWith(isRead: true);

        expect(read.id, original.id);
        expect(read.type, original.type);
        expect(read.title, original.title);
        expect(read.isRead, isTrue);
      });

      test('should create copy with new type', () {
        final original = createNotification(type: 'alert');
        final updated = original.copyWith(type: 'system');

        expect(updated.type, 'system');
        expect(updated.title, original.title);
      });
    });

    group('fromJson / toJson', () {
      test('should deserialize from JSON correctly', () {
        final json = {
          'id': 'notif-003',
          'type': 'weather',
          'title': 'Rain Alert',
          'title_ar': 'تنبيه مطر',
          'body': 'Rain expected tomorrow',
          'body_ar': 'أمطار متوقعة غدا',
          'image_url': 'https://example.com/rain.png',
          'data': {'severity': 'moderate'},
          'created_at': '2026-02-27T10:00:00.000',
          'is_read': true,
          'action_url': '/weather/alert/003',
        };

        final notification = AppNotification.fromJson(json);

        expect(notification.id, 'notif-003');
        expect(notification.type, 'weather');
        expect(notification.titleAr, 'تنبيه مطر');
        expect(notification.imageUrl, 'https://example.com/rain.png');
        expect(notification.isRead, isTrue);
        expect(notification.actionUrl, '/weather/alert/003');
      });

      test('should fallback title_ar to title when missing', () {
        final json = {
          'id': 'notif-004',
          'type': 'system',
          'title': 'Update Available',
          'body': 'New version',
          'data': {},
          'created_at': '2026-02-27T10:00:00.000',
        };

        final notification = AppNotification.fromJson(json);
        expect(notification.titleAr, 'Update Available');
        expect(notification.bodyAr, 'New version');
      });

      test('should handle null data field', () {
        final json = {
          'id': 'notif-005',
          'type': 'system',
          'title': 'Test',
          'body': 'Test body',
          'created_at': '2026-02-27T10:00:00.000',
        };

        final notification = AppNotification.fromJson(json);
        expect(notification.data, isEmpty);
      });

      test('should roundtrip through JSON', () {
        final original = createNotification();
        final json = original.toJson();
        final restored = AppNotification.fromJson(json);

        expect(restored.id, original.id);
        expect(restored.type, original.type);
        expect(restored.title, original.title);
        expect(restored.titleAr, original.titleAr);
        expect(restored.body, original.body);
        expect(restored.isRead, original.isRead);
        expect(restored.actionUrl, original.actionUrl);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NotificationSettings Entity Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NotificationSettings', () {
    test('should have all defaults set to true', () {
      const settings = NotificationSettings();

      expect(settings.enabled, isTrue);
      expect(settings.alertsEnabled, isTrue);
      expect(settings.actionsEnabled, isTrue);
      expect(settings.weatherEnabled, isTrue);
      expect(settings.cropHealthEnabled, isTrue);
      expect(settings.systemEnabled, isTrue);
      expect(settings.soundEnabled, isTrue);
      expect(settings.vibrationEnabled, isTrue);
      expect(settings.quietHoursStart, isNull);
      expect(settings.quietHoursEnd, isNull);
    });

    test('should create with custom values', () {
      const settings = NotificationSettings(
        enabled: false,
        alertsEnabled: true,
        actionsEnabled: false,
        weatherEnabled: false,
        cropHealthEnabled: true,
        systemEnabled: false,
        soundEnabled: false,
        vibrationEnabled: false,
        quietHoursStart: '22:00',
        quietHoursEnd: '06:00',
      );

      expect(settings.enabled, isFalse);
      expect(settings.alertsEnabled, isTrue);
      expect(settings.actionsEnabled, isFalse);
      expect(settings.weatherEnabled, isFalse);
      expect(settings.soundEnabled, isFalse);
      expect(settings.quietHoursStart, '22:00');
      expect(settings.quietHoursEnd, '06:00');
    });

    group('copyWith', () {
      test('should toggle enabled', () {
        const original = NotificationSettings();
        final updated = original.copyWith(enabled: false);

        expect(updated.enabled, isFalse);
        expect(updated.alertsEnabled, isTrue); // Unchanged
        expect(updated.soundEnabled, isTrue); // Unchanged
      });

      test('should toggle individual category', () {
        const original = NotificationSettings();
        final updated = original.copyWith(weatherEnabled: false);

        expect(updated.weatherEnabled, isFalse);
        expect(updated.alertsEnabled, isTrue); // Unchanged
      });

      test('should set quiet hours', () {
        const original = NotificationSettings();
        final updated = original.copyWith(
          quietHoursStart: '23:00',
          quietHoursEnd: '07:00',
        );

        expect(updated.quietHoursStart, '23:00');
        expect(updated.quietHoursEnd, '07:00');
      });
    });

    group('fromJson / toJson', () {
      test('should deserialize from JSON', () {
        final json = {
          'enabled': true,
          'alerts_enabled': false,
          'actions_enabled': true,
          'weather_enabled': false,
          'crop_health_enabled': true,
          'system_enabled': false,
          'sound_enabled': true,
          'vibration_enabled': false,
          'quiet_hours_start': '21:00',
          'quiet_hours_end': '05:00',
        };

        final settings = NotificationSettings.fromJson(json);

        expect(settings.enabled, isTrue);
        expect(settings.alertsEnabled, isFalse);
        expect(settings.actionsEnabled, isTrue);
        expect(settings.weatherEnabled, isFalse);
        expect(settings.systemEnabled, isFalse);
        expect(settings.vibrationEnabled, isFalse);
        expect(settings.quietHoursStart, '21:00');
        expect(settings.quietHoursEnd, '05:00');
      });

      test('should use defaults for missing JSON fields', () {
        final json = <String, dynamic>{};

        final settings = NotificationSettings.fromJson(json);

        expect(settings.enabled, isTrue);
        expect(settings.alertsEnabled, isTrue);
        expect(settings.soundEnabled, isTrue);
        expect(settings.vibrationEnabled, isTrue);
      });

      test('should roundtrip through JSON', () {
        const original = NotificationSettings(
          enabled: true,
          alertsEnabled: false,
          weatherEnabled: false,
          soundEnabled: false,
        );

        final json = original.toJson();
        final restored = NotificationSettings.fromJson(json);

        expect(restored.enabled, original.enabled);
        expect(restored.alertsEnabled, original.alertsEnabled);
        expect(restored.weatherEnabled, original.weatherEnabled);
        expect(restored.soundEnabled, original.soundEnabled);
        expect(restored.vibrationEnabled, original.vibrationEnabled);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NotificationTopic Entity Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NotificationTopic', () {
    test('should create instance with all fields', () {
      const topic = NotificationTopic(
        id: 'topic-001',
        name: 'Weather Alerts',
        nameAr: 'تنبيهات الطقس',
        description: 'Get notified about weather changes',
        isSubscribed: true,
      );

      expect(topic.id, 'topic-001');
      expect(topic.name, 'Weather Alerts');
      expect(topic.nameAr, 'تنبيهات الطقس');
      expect(topic.isSubscribed, isTrue);
    });

    test('should default isSubscribed to false', () {
      const topic = NotificationTopic(
        id: 'topic-002',
        name: 'Market Prices',
        nameAr: 'أسعار السوق',
        description: 'Market price updates',
      );

      expect(topic.isSubscribed, isFalse);
    });

    test('should roundtrip through JSON', () {
      const original = NotificationTopic(
        id: 'topic-003',
        name: 'Pest Alerts',
        nameAr: 'تنبيهات الآفات',
        description: 'Pest outbreak notifications',
        isSubscribed: true,
      );

      final json = original.toJson();
      final restored = NotificationTopic.fromJson(json);

      expect(restored.id, original.id);
      expect(restored.name, original.name);
      expect(restored.nameAr, original.nameAr);
      expect(restored.isSubscribed, original.isSubscribed);
    });

    test('should support copyWith for subscription toggle', () {
      const topic = NotificationTopic(
        id: 'topic-004',
        name: 'Irrigation',
        nameAr: 'الري',
        description: 'Irrigation schedule updates',
        isSubscribed: false,
      );

      final subscribed = topic.copyWith(isSubscribed: true);

      expect(subscribed.id, topic.id);
      expect(subscribed.isSubscribed, isTrue);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NotificationsNotifier Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NotificationsNotifier', () {
    late MockNotificationService mockService;
    late NotificationsNotifier notifier;

    final testNotification = AppNotification(
      id: 'notif-001',
      type: 'alert',
      title: 'Test Alert',
      titleAr: 'تنبيه تجريبي',
      body: 'Test body',
      bodyAr: 'نص تجريبي',
      data: const {},
      createdAt: DateTime(2026, 2, 27),
      isRead: false,
    );

    final readNotification = AppNotification(
      id: 'notif-002',
      type: 'weather',
      title: 'Weather Update',
      titleAr: 'تحديث الطقس',
      body: 'Rain expected',
      bodyAr: 'أمطار متوقعة',
      data: const {},
      createdAt: DateTime(2026, 2, 26),
      isRead: true,
    );

    setUp(() {
      mockService = MockNotificationService();
      notifier = NotificationsNotifier(mockService);
    });

    test('should have initial empty state', () {
      expect(notifier.state.isLoading, isFalse);
      expect(notifier.state.notifications, isEmpty);
      expect(notifier.state.unreadCount, 0);
      expect(notifier.state.error, isNull);
    });

    group('loadNotifications', () {
      test('should load notifications and update state', () async {
        // Arrange
        when(() => mockService.getLocalNotifications())
            .thenAnswer((_) async => [testNotification, readNotification]);
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 1);

        // Act
        await notifier.loadNotifications();

        // Assert
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.notifications.length, 2);
        expect(notifier.state.unreadCount, 1);
        expect(notifier.state.error, isNull);
      });

      test('should handle empty notification list', () async {
        // Arrange
        when(() => mockService.getLocalNotifications())
            .thenAnswer((_) async => []);
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 0);

        // Act
        await notifier.loadNotifications();

        // Assert
        expect(notifier.state.notifications, isEmpty);
        expect(notifier.state.unreadCount, 0);
      });

      test('should set error state on failure', () async {
        // Arrange
        when(() => mockService.getLocalNotifications())
            .thenThrow(Exception('Storage error'));

        // Act
        await notifier.loadNotifications();

        // Assert
        expect(notifier.state.isLoading, isFalse);
        expect(notifier.state.error, isNotNull);
        expect(notifier.state.error, contains('Storage error'));
      });
    });

    group('addNotification', () {
      test('should save notification and reload', () async {
        // Arrange
        when(() => mockService.saveNotification(any()))
            .thenAnswer((_) async {});
        when(() => mockService.getLocalNotifications())
            .thenAnswer((_) async => [testNotification]);
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 1);

        // Act
        await notifier.addNotification(testNotification);

        // Assert
        verify(() => mockService.saveNotification(testNotification)).called(1);
        expect(notifier.state.notifications.length, 1);
      });
    });

    group('markAsRead', () {
      test('should mark notification as read and reload', () async {
        // Arrange
        when(() => mockService.markAsRead(any())).thenAnswer((_) async {});
        when(() => mockService.getLocalNotifications())
            .thenAnswer((_) async => [readNotification]);
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 0);

        // Act
        await notifier.markAsRead('notif-001');

        // Assert
        verify(() => mockService.markAsRead('notif-001')).called(1);
        expect(notifier.state.unreadCount, 0);
      });
    });

    group('markAllAsRead', () {
      test('should mark all as read and reload', () async {
        // Arrange
        when(() => mockService.markAllAsRead()).thenAnswer((_) async {});
        when(() => mockService.getLocalNotifications()).thenAnswer(
          (_) async => [
            testNotification.copyWith(isRead: true),
            readNotification,
          ],
        );
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 0);

        // Act
        await notifier.markAllAsRead();

        // Assert
        verify(() => mockService.markAllAsRead()).called(1);
        expect(notifier.state.unreadCount, 0);
      });
    });

    group('deleteNotification', () {
      test('should delete notification and reload', () async {
        // Arrange
        when(() => mockService.deleteNotification(any()))
            .thenAnswer((_) async {});
        when(() => mockService.getLocalNotifications())
            .thenAnswer((_) async => []);
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 0);

        // Act
        await notifier.deleteNotification('notif-001');

        // Assert
        verify(() => mockService.deleteNotification('notif-001')).called(1);
        expect(notifier.state.notifications, isEmpty);
      });
    });

    group('clearAll', () {
      test('should clear all notifications and reload', () async {
        // Arrange
        when(() => mockService.clearAllNotifications())
            .thenAnswer((_) async {});
        when(() => mockService.getLocalNotifications())
            .thenAnswer((_) async => []);
        when(() => mockService.getUnreadCount()).thenAnswer((_) async => 0);

        // Act
        await notifier.clearAll();

        // Assert
        verify(() => mockService.clearAllNotifications()).called(1);
        expect(notifier.state.notifications, isEmpty);
        expect(notifier.state.unreadCount, 0);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SettingsNotifier Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SettingsNotifier', () {
    late MockNotificationService mockService;
    late SettingsNotifier notifier;

    setUp(() {
      mockService = MockNotificationService();
      // Mock getSettings to return default settings (called in constructor)
      when(() => mockService.getSettings())
          .thenReturn(const NotificationSettings());
      notifier = SettingsNotifier(mockService);
    });

    test('should load initial settings from service', () {
      expect(notifier.state.settings.enabled, isTrue);
      expect(notifier.state.settings.alertsEnabled, isTrue);
      expect(notifier.state.settings.soundEnabled, isTrue);
      verify(() => mockService.getSettings()).called(1);
    });

    group('toggleEnabled', () {
      test('should toggle master enabled and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleEnabled(false);

        // Assert
        expect(notifier.state.settings.enabled, isFalse);
        verify(() => mockService.saveSettings(any())).called(1);
      });
    });

    group('toggleAlerts', () {
      test('should toggle alerts and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleAlerts(false);

        // Assert
        expect(notifier.state.settings.alertsEnabled, isFalse);
        expect(notifier.state.settings.weatherEnabled, isTrue); // Unchanged
      });
    });

    group('toggleActions', () {
      test('should toggle actions and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleActions(false);

        // Assert
        expect(notifier.state.settings.actionsEnabled, isFalse);
      });
    });

    group('toggleWeather', () {
      test('should toggle weather and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleWeather(false);

        // Assert
        expect(notifier.state.settings.weatherEnabled, isFalse);
      });
    });

    group('toggleCropHealth', () {
      test('should toggle crop health and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleCropHealth(false);

        // Assert
        expect(notifier.state.settings.cropHealthEnabled, isFalse);
      });
    });

    group('toggleSound', () {
      test('should toggle sound and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleSound(false);

        // Assert
        expect(notifier.state.settings.soundEnabled, isFalse);
      });
    });

    group('toggleVibration', () {
      test('should toggle vibration and save', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        // Act
        await notifier.toggleVibration(false);

        // Assert
        expect(notifier.state.settings.vibrationEnabled, isFalse);
      });
    });

    group('updateSettings', () {
      test('should save complete settings object', () async {
        // Arrange
        when(() => mockService.saveSettings(any()))
            .thenAnswer((_) async {});

        const newSettings = NotificationSettings(
          enabled: true,
          alertsEnabled: false,
          actionsEnabled: false,
          weatherEnabled: false,
          cropHealthEnabled: true,
          systemEnabled: false,
          soundEnabled: false,
          vibrationEnabled: false,
          quietHoursStart: '22:00',
          quietHoursEnd: '06:00',
        );

        // Act
        await notifier.updateSettings(newSettings);

        // Assert
        expect(notifier.state.settings.alertsEnabled, isFalse);
        expect(notifier.state.settings.actionsEnabled, isFalse);
        expect(notifier.state.settings.weatherEnabled, isFalse);
        expect(notifier.state.settings.cropHealthEnabled, isTrue);
        expect(notifier.state.settings.quietHoursStart, '22:00');
        expect(notifier.state.settings.quietHoursEnd, '06:00');
        verify(() => mockService.saveSettings(newSettings)).called(1);
      });
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NotificationsState Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NotificationsState', () {
    test('should have default values', () {
      const state = NotificationsState();

      expect(state.isLoading, isFalse);
      expect(state.notifications, isEmpty);
      expect(state.unreadCount, 0);
      expect(state.error, isNull);
    });

    test('should support copyWith', () {
      const original = NotificationsState();

      final updated = original.copyWith(
        isLoading: true,
        unreadCount: 5,
      );

      expect(updated.isLoading, isTrue);
      expect(updated.unreadCount, 5);
      expect(updated.notifications, isEmpty); // Unchanged
      expect(updated.error, isNull); // Unchanged
    });

    test('should clear error with copyWith', () {
      final withError = const NotificationsState().copyWith(
        error: 'Something went wrong',
      );

      expect(withError.error, 'Something went wrong');

      final cleared = withError.copyWith(error: null);
      expect(cleared.error, isNull);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // SettingsState Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('SettingsState', () {
    test('should have default values', () {
      const state = SettingsState();

      expect(state.isLoading, isFalse);
      expect(state.settings.enabled, isTrue);
      expect(state.error, isNull);
    });

    test('should support copyWith for settings update', () {
      const original = SettingsState();

      final updated = original.copyWith(
        settings: const NotificationSettings(enabled: false),
      );

      expect(updated.settings.enabled, isFalse);
      expect(updated.isLoading, isFalse);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Unread Count Computation Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('Unread count computation', () {
    late MockNotificationService mockService;
    late NotificationsNotifier notifier;

    setUp(() {
      mockService = MockNotificationService();
      notifier = NotificationsNotifier(mockService);
    });

    test('should compute correct unread count from service', () async {
      // Arrange
      final notifications = [
        AppNotification(
          id: 'n1',
          type: 'alert',
          title: 'Alert 1',
          titleAr: 'تنبيه 1',
          body: 'Body 1',
          bodyAr: 'نص 1',
          data: const {},
          createdAt: DateTime(2026, 2, 27),
          isRead: false,
        ),
        AppNotification(
          id: 'n2',
          type: 'weather',
          title: 'Weather',
          titleAr: 'طقس',
          body: 'Body 2',
          bodyAr: 'نص 2',
          data: const {},
          createdAt: DateTime(2026, 2, 26),
          isRead: true,
        ),
        AppNotification(
          id: 'n3',
          type: 'system',
          title: 'System',
          titleAr: 'نظام',
          body: 'Body 3',
          bodyAr: 'نص 3',
          data: const {},
          createdAt: DateTime(2026, 2, 25),
          isRead: false,
        ),
      ];

      when(() => mockService.getLocalNotifications())
          .thenAnswer((_) async => notifications);
      when(() => mockService.getUnreadCount()).thenAnswer((_) async => 2);

      // Act
      await notifier.loadNotifications();

      // Assert
      expect(notifier.state.unreadCount, 2);
      expect(notifier.state.notifications.length, 3);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Filtering Tests (simulating filteredNotificationsProvider logic)
  // ═══════════════════════════════════════════════════════════════════════════

  group('Notification filtering by type', () {
    test('should filter notifications by type', () {
      // Arrange
      final notifications = [
        AppNotification(
          id: 'n1',
          type: 'alert',
          title: 'Alert',
          titleAr: 'تنبيه',
          body: '',
          bodyAr: '',
          data: const {},
          createdAt: DateTime(2026, 2, 27),
        ),
        AppNotification(
          id: 'n2',
          type: 'weather',
          title: 'Weather',
          titleAr: 'طقس',
          body: '',
          bodyAr: '',
          data: const {},
          createdAt: DateTime(2026, 2, 26),
        ),
        AppNotification(
          id: 'n3',
          type: 'alert',
          title: 'Alert 2',
          titleAr: 'تنبيه 2',
          body: '',
          bodyAr: '',
          data: const {},
          createdAt: DateTime(2026, 2, 25),
        ),
      ];

      // Act - filter by 'alert' type
      final alertNotifications =
          notifications.where((n) => n.type == 'alert').toList();

      // Assert
      expect(alertNotifications.length, 2);
      expect(alertNotifications.every((n) => n.type == 'alert'), isTrue);
    });

    test('should return all notifications when filter is null', () {
      final notifications = [
        AppNotification(
          id: 'n1',
          type: 'alert',
          title: 'Alert',
          titleAr: 'تنبيه',
          body: '',
          bodyAr: '',
          data: const {},
          createdAt: DateTime(2026, 2, 27),
        ),
        AppNotification(
          id: 'n2',
          type: 'weather',
          title: 'Weather',
          titleAr: 'طقس',
          body: '',
          bodyAr: '',
          data: const {},
          createdAt: DateTime(2026, 2, 26),
        ),
      ];

      // null filter returns all
      String? filter;
      final filtered = filter == null
          ? notifications
          : notifications.where((n) => n.type == filter).toList();

      expect(filtered.length, 2);
    });

    test('should return empty when filter matches no notifications', () {
      final notifications = [
        AppNotification(
          id: 'n1',
          type: 'alert',
          title: 'Alert',
          titleAr: 'تنبيه',
          body: '',
          bodyAr: '',
          data: const {},
          createdAt: DateTime(2026, 2, 27),
        ),
      ];

      final filtered =
          notifications.where((n) => n.type == 'weather').toList();

      expect(filtered, isEmpty);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // NotificationService.parseFirebaseMessage Tests
  // ═══════════════════════════════════════════════════════════════════════════

  group('NotificationService.parseFirebaseMessage', () {
    late NotificationService service;

    setUp(() {
      service = NotificationService();
    });

    test('should parse full Firebase message', () {
      final message = {
        'notification': {
          'title': 'Rain Alert',
          'body': 'Heavy rain expected',
          'image': 'https://example.com/rain.png',
        },
        'data': {
          'id': 'fcm-001',
          'type': 'weather',
          'title_ar': 'تنبيه مطر',
          'body_ar': 'أمطار غزيرة متوقعة',
          'action_url': '/weather/alert',
        },
      };

      final notification = service.parseFirebaseMessage(message);

      expect(notification.id, 'fcm-001');
      expect(notification.type, 'weather');
      expect(notification.title, 'Rain Alert');
      expect(notification.body, 'Heavy rain expected');
      expect(notification.imageUrl, 'https://example.com/rain.png');
      expect(notification.actionUrl, '/weather/alert');
      expect(notification.isRead, isFalse);
    });

    test('should handle message with only data payload', () {
      final message = {
        'data': {
          'id': 'fcm-002',
          'type': 'alert',
          'title': 'Field Alert',
          'body': 'Pest detected',
        },
      };

      final notification = service.parseFirebaseMessage(message);

      expect(notification.id, 'fcm-002');
      expect(notification.type, 'alert');
      expect(notification.title, 'Field Alert');
      expect(notification.body, 'Pest detected');
    });

    test('should handle minimal message with defaults', () {
      final message = <String, dynamic>{
        'data': <String, dynamic>{},
      };

      final notification = service.parseFirebaseMessage(message);

      expect(notification.type, 'system');
      expect(notification.isRead, isFalse);
      expect(notification.id, isNotEmpty);
    });
  });
}
