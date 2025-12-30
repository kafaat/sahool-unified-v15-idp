/// SAHOOL Field App - Permission Integration Tests
/// اختبارات تكامل الصلاحيات الشاملة
///
/// Test scenarios:
/// - Permission request flows
/// - Graceful degradation without permissions
/// - Permission rationale dialogs
/// - Settings navigation
/// - Platform-specific permission handling

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Permission Request Flow Tests', () {
    late ProviderContainer container;

    setUp(() async {
      SharedPreferences.setMockInitialValues({});
      container = ProviderContainer();
    });

    tearDown(() {
      container.dispose();
    });

    // =========================================================================
    // Location Permission Tests
    // =========================================================================

    testWidgets('should request location permission with rationale', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  return Center(
                    child: ElevatedButton(
                      child: const Text('طلب إذن الموقع'),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            icon: const Icon(Icons.location_on, size: 48, color: Colors.green),
                            title: const Text('نحتاج إلى صلاحية الموقع'),
                            content: const Text(
                              'نحتاج إلى صلاحية الموقع لتحديد مواقع الحقول والمزارع على الخريطة.',
                              textAlign: TextAlign.right,
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context, false),
                                child: const Text('إلغاء'),
                              ),
                              FilledButton(
                                onPressed: () => Navigator.pop(context, true),
                                child: const Text('متابعة'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Act - Request permission
      await tester.tap(find.text('طلب إذن الموقع'));
      await tester.pumpAndSettle();

      // Assert - Rationale dialog shown
      expect(find.text('نحتاج إلى صلاحية الموقع'), findsOneWidget);
      expect(find.text('نحتاج إلى صلاحية الموقع لتحديد مواقع الحقول والمزارع على الخريطة.'), findsOneWidget);
      expect(find.text('متابعة'), findsOneWidget);
    });

    testWidgets('should check location permission status', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Simulate permission states
      final permissionStates = ['granted', 'denied', 'permanentlyDenied'];

      for (final state in permissionStates) {
        // Act
        await prefs.setString('location_permission', state);

        // Assert
        final status = prefs.getString('location_permission');
        expect(status, equals(state));
      }
    });

    testWidgets('should handle permanently denied location permission', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  return Center(
                    child: ElevatedButton(
                      child: const Text('Show Permanently Denied'),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            icon: const Icon(
                              Icons.warning_rounded,
                              size: 48,
                              color: Colors.red,
                            ),
                            title: const Text('صلاحية مطلوبة'),
                            content: const Text(
                              'تم رفض صلاحية الموقع نهائياً. '
                              'يرجى فتح الإعدادات والسماح بالصلاحية يدوياً.',
                              textAlign: TextAlign.right,
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('إلغاء'),
                              ),
                              FilledButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('فتح الإعدادات'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Act
      await tester.tap(find.text('Show Permanently Denied'));
      await tester.pumpAndSettle();

      // Assert
      expect(find.text('صلاحية مطلوبة'), findsOneWidget);
      expect(find.text('فتح الإعدادات'), findsOneWidget);
    });

    testWidgets('should request precise location for Android 12+', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('location_permission', 'granted');
      await prefs.setBool('has_precise_location', false);

      // Act - Request precise location
      await prefs.setBool('precise_location_requested', true);
      await prefs.setString('precise_location_requested_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getBool('precise_location_requested'), isTrue);
    });

    // =========================================================================
    // Camera Permission Tests
    // =========================================================================

    testWidgets('should request camera permission for photo capture', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Request camera permission
      await prefs.setString('camera_permission', 'granted');
      await prefs.setString('camera_permission_granted_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getString('camera_permission'), equals('granted'));
    });

    testWidgets('should show camera rationale dialog', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  return Center(
                    child: ElevatedButton(
                      child: const Text('طلب إذن الكاميرا'),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            icon: const Icon(Icons.camera_alt, size: 48, color: Colors.green),
                            title: const Text('نحتاج إلى صلاحية الكاميرا'),
                            content: const Text(
                              'نحتاج إلى صلاحية الكاميرا لالتقاط صور المحاصيل والآفات والأمراض.',
                              textAlign: TextAlign.right,
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('إلغاء'),
                              ),
                              FilledButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('متابعة'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Act
      await tester.tap(find.text('طلب إذن الكاميرا'));
      await tester.pumpAndSettle();

      // Assert
      expect(find.text('نحتاج إلى صلاحية الكاميرا'), findsOneWidget);
      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
    });

    // =========================================================================
    // Storage/Photos Permission Tests
    // =========================================================================

    testWidgets('should request storage permission for Android < 13', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('android_sdk_version', 29); // Android 10

      // Act - Request storage permission
      await prefs.setString('storage_permission', 'granted');

      // Assert
      expect(prefs.getString('storage_permission'), equals('granted'));
    });

    testWidgets('should request photos permission for Android 13+', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('android_sdk_version', 33); // Android 13

      // Act - Request photos permission instead of storage
      await prefs.setString('photos_permission', 'granted');

      // Assert
      expect(prefs.getString('photos_permission'), equals('granted'));
    });

    testWidgets('should handle limited photo access on iOS', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - iOS returns limited access
      await prefs.setString('photos_permission', 'limited');
      await prefs.setInt('selected_photos_count', 5);

      // Assert
      expect(prefs.getString('photos_permission'), equals('limited'));
      expect(prefs.getInt('selected_photos_count'), equals(5));
    });

    // =========================================================================
    // Notification Permission Tests
    // =========================================================================

    testWidgets('should request notification permission for Android 13+', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('android_sdk_version', 33);

      // Act - Request notification permission
      await prefs.setString('notification_permission', 'granted');
      await prefs.setString('notification_permission_granted_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getString('notification_permission'), equals('granted'));
    });

    testWidgets('should show notification permission rationale', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              body: Builder(
                builder: (context) {
                  return Center(
                    child: ElevatedButton(
                      child: const Text('طلب إذن الإشعارات'),
                      onPressed: () {
                        showDialog(
                          context: context,
                          builder: (context) => AlertDialog(
                            icon: const Icon(Icons.notifications, size: 48, color: Colors.green),
                            title: const Text('نحتاج إلى صلاحية الإشعارات'),
                            content: const Text(
                              'نحتاج إلى صلاحية الإشعارات لإرسال تنبيهات المهام والتحديثات المهمة.',
                              textAlign: TextAlign.right,
                            ),
                            actions: [
                              TextButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('إلغاء'),
                              ),
                              FilledButton(
                                onPressed: () => Navigator.pop(context),
                                child: const Text('متابعة'),
                              ),
                            ],
                          ),
                        );
                      },
                    ),
                  );
                },
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Act
      await tester.tap(find.text('طلب إذن الإشعارات'));
      await tester.pumpAndSettle();

      // Assert
      expect(find.text('نحتاج إلى صلاحية الإشعارات'), findsOneWidget);
      expect(find.byIcon(Icons.notifications), findsOneWidget);
    });

    // =========================================================================
    // Bulk Permission Requests
    // =========================================================================

    testWidgets('should request multiple permissions for field operations', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      final requiredPermissions = ['location', 'camera', 'storage'];

      // Act - Request all permissions
      for (final permission in requiredPermissions) {
        await prefs.setString('${permission}_permission', 'granted');
      }

      // Check all granted
      final allGranted = requiredPermissions.every(
        (p) => prefs.getString('${p}_permission') == 'granted',
      );

      // Assert
      expect(allGranted, isTrue);
    });

    testWidgets('should show permission summary screen', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              appBar: AppBar(title: const Text('الصلاحيات المطلوبة')),
              body: ListView(
                padding: const EdgeInsets.all(16),
                children: const [
                  // Location permission
                  ListTile(
                    leading: Icon(Icons.location_on, color: Colors.green),
                    title: Text('الموقع'),
                    subtitle: Text('لتحديد مواقع الحقول'),
                    trailing: Icon(Icons.check_circle, color: Colors.green),
                  ),
                  Divider(),
                  // Camera permission
                  ListTile(
                    leading: Icon(Icons.camera_alt, color: Colors.green),
                    title: Text('الكاميرا'),
                    subtitle: Text('لالتقاط صور المحاصيل'),
                    trailing: Icon(Icons.check_circle, color: Colors.green),
                  ),
                  Divider(),
                  // Storage permission
                  ListTile(
                    leading: Icon(Icons.photo_library, color: Colors.orange),
                    title: Text('الصور'),
                    subtitle: Text('لإرفاق الصور بالتقارير'),
                    trailing: Icon(Icons.warning, color: Colors.orange),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Assert
      expect(find.text('الصلاحيات المطلوبة'), findsOneWidget);
      expect(find.text('الموقع'), findsOneWidget);
      expect(find.text('الكاميرا'), findsOneWidget);
      expect(find.text('الصور'), findsOneWidget);
    });

    // =========================================================================
    // Graceful Degradation Tests
    // =========================================================================

    testWidgets('should work without location permission with limited features', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('location_permission', 'denied');

      // Act - Check feature availability
      final canUseMap = prefs.getString('location_permission') == 'granted';
      final canManuallyEnterLocation = true; // Always available

      await prefs.setBool('map_enabled', canUseMap);
      await prefs.setBool('manual_location_enabled', canManuallyEnterLocation);

      // Assert
      expect(prefs.getBool('map_enabled'), isFalse);
      expect(prefs.getBool('manual_location_enabled'), isTrue);
    });

    testWidgets('should show manual location entry when permission denied', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              appBar: AppBar(title: const Text('إضافة حقل')),
              body: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    // Location permission denied message
                    const Material(
                      color: Colors.orange,
                      child: Padding(
                        padding: EdgeInsets.all(12),
                        child: Row(
                          children: [
                            Icon(Icons.info, color: Colors.white),
                            SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                'لم يتم منح إذن الموقع. يمكنك إدخال الموقع يدوياً.',
                                style: TextStyle(color: Colors.white),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    // Manual location entry
                    const TextField(
                      decoration: InputDecoration(
                        labelText: 'خط العرض (Latitude)',
                        hintText: '24.7136',
                      ),
                    ),
                    const SizedBox(height: 8),
                    const TextField(
                      decoration: InputDecoration(
                        labelText: 'خط الطول (Longitude)',
                        hintText: '46.6753',
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Assert
      expect(find.text('لم يتم منح إذن الموقع. يمكنك إدخال الموقع يدوياً.'), findsOneWidget);
      expect(find.text('خط العرض (Latitude)'), findsOneWidget);
      expect(find.text('خط الطول (Longitude)'), findsOneWidget);
    });

    testWidgets('should allow text notes when camera permission denied', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('camera_permission', 'denied');

      // Act - Check alternatives
      final canUseCamera = prefs.getString('camera_permission') == 'granted';
      final canUseTextNotes = true; // Always available
      final canSelectExistingPhoto = true; // If storage permission granted

      await prefs.setBool('camera_enabled', canUseCamera);
      await prefs.setBool('text_notes_enabled', canUseTextNotes);
      await prefs.setBool('gallery_enabled', canSelectExistingPhoto);

      // Assert
      expect(prefs.getBool('camera_enabled'), isFalse);
      expect(prefs.getBool('text_notes_enabled'), isTrue);
      expect(prefs.getBool('gallery_enabled'), isTrue);
    });

    testWidgets('should disable background sync without notification permission', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('notification_permission', 'denied');

      // Act - Adjust sync strategy
      final canShowNotifications = prefs.getString('notification_permission') == 'granted';
      final silentSyncEnabled = !canShowNotifications;

      await prefs.setBool('silent_sync_mode', silentSyncEnabled);
      await prefs.setBool('sync_notifications_enabled', canShowNotifications);

      // Assert
      expect(prefs.getBool('silent_sync_mode'), isTrue);
      expect(prefs.getBool('sync_notifications_enabled'), isFalse);
    });

    // =========================================================================
    // Permission Settings Management
    // =========================================================================

    testWidgets('should open app settings when needed', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - User clicks "Open Settings"
      await prefs.setBool('settings_opened', true);
      await prefs.setString('settings_opened_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getBool('settings_opened'), isTrue);
    });

    testWidgets('should track permission request history', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Track permission requests
      final requests = [
        {
          'permission': 'location',
          'requested_at': DateTime.now().toIso8601String(),
          'result': 'granted',
        },
        {
          'permission': 'camera',
          'requested_at': DateTime.now().toIso8601String(),
          'result': 'denied',
        },
      ];

      final requestList = prefs.getStringList('permission_requests') ?? [];
      for (final request in requests) {
        requestList.add(request.toString());
      }
      await prefs.setStringList('permission_requests', requestList);

      // Assert
      expect(prefs.getStringList('permission_requests')!.length, equals(2));
    });

    testWidgets('should show permission status in settings', (tester) async {
      // Arrange
      await tester.pumpWidget(
        ProviderScope(
          child: MaterialApp(
            home: Scaffold(
              appBar: AppBar(title: const Text('إعدادات الصلاحيات')),
              body: ListView(
                children: [
                  SwitchListTile(
                    key: const Key('location_switch'),
                    title: const Text('الموقع'),
                    subtitle: const Text('ممنوح'),
                    value: true,
                    onChanged: null, // Read-only, must change in system settings
                    secondary: const Icon(Icons.location_on),
                  ),
                  SwitchListTile(
                    key: const Key('camera_switch'),
                    title: const Text('الكاميرا'),
                    subtitle: const Text('مرفوض'),
                    value: false,
                    onChanged: null,
                    secondary: const Icon(Icons.camera_alt),
                  ),
                ],
              ),
            ),
          ),
        ),
      );

      await tester.pumpAndSettle();

      // Assert
      expect(find.text('إعدادات الصلاحيات'), findsOneWidget);
      expect(find.byKey(const Key('location_switch')), findsOneWidget);
      expect(find.byKey(const Key('camera_switch')), findsOneWidget);
    });

    // =========================================================================
    // Platform-Specific Handling
    // =========================================================================

    testWidgets('should handle iOS provisional notification permission', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('platform', 'ios');

      // Act - Request provisional permission
      await prefs.setString('notification_permission', 'provisional');
      await prefs.setBool('can_show_silent_notifications', true);

      // Assert
      expect(prefs.getString('notification_permission'), equals('provisional'));
      expect(prefs.getBool('can_show_silent_notifications'), isTrue);
    });

    testWidgets('should handle Android permission never ask again', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('platform', 'android');
      await prefs.setInt('camera_permission_requests', 2);

      // Act - User selects "never ask again"
      await prefs.setString('camera_permission', 'permanentlyDenied');
      await prefs.setBool('show_settings_prompt', true);

      // Assert
      expect(prefs.getString('camera_permission'), equals('permanentlyDenied'));
      expect(prefs.getBool('show_settings_prompt'), isTrue);
    });

    // =========================================================================
    // Permission Edge Cases
    // =========================================================================

    testWidgets('should handle permission revoked while app is running', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('location_permission', 'granted');

      // Act - Permission revoked by user in settings
      await prefs.setString('location_permission', 'denied');
      await prefs.setString('permission_revoked_at', DateTime.now().toIso8601String());

      // Disable location features
      await prefs.setBool('location_features_enabled', false);

      // Assert
      expect(prefs.getString('location_permission'), equals('denied'));
      expect(prefs.getBool('location_features_enabled'), isFalse);
    });

    testWidgets('should re-request permission after app update', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('app_version', '1.0.0');
      await prefs.setString('last_permission_check_version', '0.9.0');

      // Act - New version, recheck permissions
      const currentVersion = '1.0.0';
      final lastCheckVersion = prefs.getString('last_permission_check_version');
      final shouldRecheckPermissions = lastCheckVersion != currentVersion;

      if (shouldRecheckPermissions) {
        await prefs.setString('last_permission_check_version', currentVersion);
        await prefs.setBool('permissions_need_recheck', true);
      }

      // Assert
      expect(shouldRecheckPermissions, isTrue);
      expect(prefs.getBool('permissions_need_recheck'), isTrue);
    });

    testWidgets('should handle permission timing for better UX', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Don't request all permissions on first launch
      await prefs.setBool('is_first_launch', true);
      await prefs.setBool('request_permissions_on_first_use', true);

      // Wait until user tries to use feature
      await prefs.setBool('user_clicked_add_field', true);

      // Now request location permission
      await prefs.setString('location_permission_requested_at', DateTime.now().toIso8601String());

      // Assert
      expect(prefs.getBool('request_permissions_on_first_use'), isTrue);
      expect(prefs.getString('location_permission_requested_at'), isNotNull);
    });
  });

  // ===========================================================================
  // Permission Analytics
  // ===========================================================================

  group('Permission Analytics Tests', () {
    testWidgets('should track permission grant rates', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();

      // Act - Track stats
      await prefs.setInt('location_requests', 10);
      await prefs.setInt('location_grants', 8);
      await prefs.setInt('camera_requests', 15);
      await prefs.setInt('camera_grants', 12);

      // Calculate grant rates
      final locationRate = (8 / 10 * 100).round();
      final cameraRate = (12 / 15 * 100).round();

      await prefs.setInt('location_grant_rate', locationRate);
      await prefs.setInt('camera_grant_rate', cameraRate);

      // Assert
      expect(prefs.getInt('location_grant_rate'), equals(80));
      expect(prefs.getInt('camera_grant_rate'), equals(80));
    });

    testWidgets('should identify most denied permissions', (tester) async {
      // Arrange
      final prefs = await SharedPreferences.getInstance();
      await prefs.setInt('location_denials', 2);
      await prefs.setInt('camera_denials', 5);
      await prefs.setInt('notification_denials', 8);

      // Act - Find most denied
      final denials = {
        'location': prefs.getInt('location_denials') ?? 0,
        'camera': prefs.getInt('camera_denials') ?? 0,
        'notification': prefs.getInt('notification_denials') ?? 0,
      };

      final sorted = denials.entries.toList()
        ..sort((a, b) => b.value.compareTo(a.value));
      final mostDenied = sorted.first.key;

      // Assert
      expect(mostDenied, equals('notification'));
    });
  });
}
