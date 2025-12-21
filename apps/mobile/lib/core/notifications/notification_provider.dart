/// SAHOOL Notification Provider
/// مزود الإشعارات

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'notification_service.dart';

/// Provider for NotificationService
final notificationServiceProvider = Provider<NotificationService>((ref) {
  return NotificationServiceImpl();
});

/// Provider for notification initialization state
final notificationInitializedProvider = FutureProvider<bool>((ref) async {
  final service = ref.watch(notificationServiceProvider);
  await service.initialize();
  final granted = await service.requestPermission();
  return granted;
});
