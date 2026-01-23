import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'websocket_service.dart';
import '../notifications/notification_service.dart';
import '../utils/app_logger.dart';

/// Event handler for WebSocket events
/// معالج الأحداث لأحداث WebSocket
class WebSocketEventHandler {
  final NotificationService notificationService;

  WebSocketEventHandler({
    required this.notificationService,
  });

  /// Handle WebSocket event
  /// معالجة حدث WebSocket
  Future<void> handleEvent(WebSocketEvent event) async {
    AppLogger.info('Handling WebSocket event: ${event.eventType ?? event.type}');

    switch (event.eventType) {
      // Field events
      case 'field.updated':
        await _handleFieldUpdated(event);
        break;
      case 'field.created':
        await _handleFieldCreated(event);
        break;

      // Weather events
      case 'weather.alert':
        await _handleWeatherAlert(event);
        break;
      case 'weather.updated':
        await _handleWeatherUpdated(event);
        break;

      // Satellite events
      case 'satellite.ready':
        await _handleSatelliteReady(event);
        break;
      case 'satellite.processing':
        await _handleSatelliteProcessing(event);
        break;
      case 'satellite.failed':
        await _handleSatelliteFailed(event);
        break;

      // NDVI events
      case 'ndvi.updated':
        await _handleNdviUpdated(event);
        break;
      case 'ndvi.analysis.ready':
        await _handleNdviAnalysisReady(event);
        break;

      // Inventory events
      case 'inventory.low_stock':
        await _handleLowStock(event);
        break;
      case 'inventory.out_of_stock':
        await _handleOutOfStock(event);
        break;
      case 'inventory.updated':
        await _handleInventoryUpdated(event);
        break;

      // Crop health events
      case 'crop.disease.detected':
        await _handleDiseaseDetected(event);
        break;
      case 'crop.pest.detected':
        await _handlePestDetected(event);
        break;
      case 'crop.health.alert':
        await _handleHealthAlert(event);
        break;

      // Spray events
      case 'spray.window.optimal':
        await _handleSprayWindow(event);
        break;
      case 'spray.window.warning':
        await _handleSprayWarning(event);
        break;
      case 'spray.scheduled':
        await _handleSprayScheduled(event);
        break;

      // Chat events
      case 'chat.message':
        await _handleChatMessage(event);
        break;

      // Task events
      case 'task.created':
      case 'task.updated':
      case 'task.completed':
        await _handleTaskEvent(event);
        break;
      case 'task.overdue':
        await _handleTaskOverdue(event);
        break;

      // IoT events
      case 'iot.alert':
        await _handleIotAlert(event);
        break;
      case 'iot.offline':
        await _handleIotOffline(event);
        break;

      default:
        AppLogger.debug('Unhandled event type: ${event.eventType}');
    }
  }

  // Field Events
  Future<void> _handleFieldUpdated(WebSocketEvent event) async {
    // Update local cache, trigger UI refresh
    AppLogger.info('Field updated: ${event.data?['field_id']}');
  }

  Future<void> _handleFieldCreated(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'New Field Created',
      titleAr: 'تم إنشاء حقل جديد',
      body: event.message ?? 'A new field has been created',
      bodyAr: event.messageAr ?? 'تم إنشاء حقل جديد',
      data: event.data ?? {},
    );
  }

  // Weather Events
  Future<void> _handleWeatherAlert(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Weather Alert',
      titleAr: 'تنبيه طقس',
      body: event.message ?? 'Important weather alert',
      bodyAr: event.messageAr ?? 'تنبيه طقس مهم',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  Future<void> _handleWeatherUpdated(WebSocketEvent event) async {
    // Update weather cache silently
    AppLogger.info('Weather updated');
  }

  // Satellite Events
  Future<void> _handleSatelliteReady(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Satellite Imagery Ready',
      titleAr: 'صور الأقمار الصناعية جاهزة',
      body: event.message ?? 'New satellite imagery is available',
      bodyAr: event.messageAr ?? 'صور جديدة من الأقمار الصناعية متاحة',
      data: event.data ?? {},
    );
  }

  Future<void> _handleSatelliteProcessing(WebSocketEvent event) async {
    // Show processing status in UI
    AppLogger.info('Satellite imagery processing');
  }

  Future<void> _handleSatelliteFailed(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Satellite Processing Failed',
      titleAr: 'فشلت معالجة الأقمار الصناعية',
      body: event.message ?? 'Failed to process satellite imagery',
      bodyAr: event.messageAr ?? 'فشلت معالجة صور الأقمار الصناعية',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  // NDVI Events
  Future<void> _handleNdviUpdated(WebSocketEvent event) async {
    // Update NDVI data in cache
    AppLogger.info('NDVI updated for field: ${event.data?['field_id']}');
  }

  Future<void> _handleNdviAnalysisReady(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'NDVI Analysis Ready',
      titleAr: 'تحليل NDVI جاهز',
      body: event.message ?? 'NDVI analysis completed',
      bodyAr: event.messageAr ?? 'اكتمل تحليل NDVI',
      data: event.data ?? {},
    );
  }

  // Inventory Events
  Future<void> _handleLowStock(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Low Stock Alert',
      titleAr: 'تنبيه مخزون منخفض',
      body: event.message ?? 'Stock is running low',
      bodyAr: event.messageAr ?? 'المخزون منخفض',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  Future<void> _handleOutOfStock(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Out of Stock',
      titleAr: 'نفاد المخزون',
      body: event.message ?? 'Item is out of stock',
      bodyAr: event.messageAr ?? 'نفاد المخزون',
      data: event.data ?? {},
      priority: NotificationPriority.critical,
    );
  }

  Future<void> _handleInventoryUpdated(WebSocketEvent event) async {
    // Update inventory cache
    AppLogger.info('Inventory updated');
  }

  // Crop Health Events
  Future<void> _handleDiseaseDetected(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Disease Detected',
      titleAr: 'تم اكتشاف مرض',
      body: event.message ?? 'Disease detected in crop',
      bodyAr: event.messageAr ?? 'تم اكتشاف مرض في المحصول',
      data: event.data ?? {},
      priority: NotificationPriority.critical,
    );
  }

  Future<void> _handlePestDetected(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Pest Detected',
      titleAr: 'تم اكتشاف آفة',
      body: event.message ?? 'Pest detected in crop',
      bodyAr: event.messageAr ?? 'تم اكتشاف آفة في المحصول',
      data: event.data ?? {},
      priority: NotificationPriority.critical,
    );
  }

  Future<void> _handleHealthAlert(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Crop Health Alert',
      titleAr: 'تنبيه صحة المحصول',
      body: event.message ?? 'Crop health issue detected',
      bodyAr: event.messageAr ?? 'تم اكتشاف مشكلة في صحة المحصول',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  // Spray Events
  Future<void> _handleSprayWindow(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Optimal Spray Window',
      titleAr: 'وقت الرش المثالي',
      body: event.message ?? 'Optimal time for spraying',
      bodyAr: event.messageAr ?? 'وقت مثالي للرش',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  Future<void> _handleSprayWarning(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Spray Warning',
      titleAr: 'تحذير الرش',
      body: event.message ?? 'Spray window warning',
      bodyAr: event.messageAr ?? 'تحذير وقت الرش',
      data: event.data ?? {},
      priority: NotificationPriority.medium,
    );
  }

  Future<void> _handleSprayScheduled(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Spray Scheduled',
      titleAr: 'تم جدولة الرش',
      body: event.message ?? 'Spray operation scheduled',
      bodyAr: event.messageAr ?? 'تم جدولة عملية الرش',
      data: event.data ?? {},
    );
  }

  // Chat Events
  Future<void> _handleChatMessage(WebSocketEvent event) async {
    // Don't show notification if user is in the chat room
    // This should be handled by the chat UI
    AppLogger.info('Chat message received');
  }

  // Task Events
  Future<void> _handleTaskEvent(WebSocketEvent event) async {
    final eventType = event.eventType ?? '';
    String title = 'Task Updated';
    String titleAr = 'تم تحديث المهمة';

    if (eventType.contains('created')) {
      title = 'New Task';
      titleAr = 'مهمة جديدة';
    } else if (eventType.contains('completed')) {
      title = 'Task Completed';
      titleAr = 'تمت المهمة';
    }

    await notificationService.showNotification(
      title: title,
      titleAr: titleAr,
      body: event.message ?? 'Task has been updated',
      bodyAr: event.messageAr ?? 'تم تحديث المهمة',
      data: event.data ?? {},
    );
  }

  Future<void> _handleTaskOverdue(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Task Overdue',
      titleAr: 'مهمة متأخرة',
      body: event.message ?? 'A task is overdue',
      bodyAr: event.messageAr ?? 'مهمة متأخرة',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  // IoT Events
  Future<void> _handleIotAlert(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Sensor Alert',
      titleAr: 'تنبيه من المستشعر',
      body: event.message ?? 'Sensor alert',
      bodyAr: event.messageAr ?? 'تنبيه من المستشعر',
      data: event.data ?? {},
      priority: NotificationPriority.high,
    );
  }

  Future<void> _handleIotOffline(WebSocketEvent event) async {
    await notificationService.showNotification(
      title: 'Sensor Offline',
      titleAr: 'المستشعر غير متصل',
      body: event.message ?? 'Sensor went offline',
      bodyAr: event.messageAr ?? 'المستشعر غير متصل',
      data: event.data ?? {},
      priority: NotificationPriority.medium,
    );
  }
}

/// Event handler provider
final webSocketEventHandlerProvider = Provider<WebSocketEventHandler>((ref) {
  final notificationService = ref.watch(notificationServiceProvider);
  return WebSocketEventHandler(notificationService: notificationService);
});

/// Widget to automatically handle WebSocket events
class WebSocketEventListener extends ConsumerWidget {
  final Widget child;

  const WebSocketEventListener({
    Key? key,
    required this.child,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final eventHandler = ref.watch(webSocketEventHandlerProvider);

    // Listen to all WebSocket events
    ref.listen(
      webSocketEventsProvider,
      (previous, next) {
        next.whenData((event) {
          eventHandler.handleEvent(event);
        });
      },
    );

    return child;
  }
}

/// Notification priority enum
enum NotificationPriority {
  low,
  medium,
  high,
  critical,
}

/// Extension for NotificationService to support our priority
extension NotificationServiceExtension on NotificationService {
  Future<void> showNotification({
    required String title,
    required String titleAr,
    required String body,
    required String bodyAr,
    required Map<String, dynamic> data,
    NotificationPriority priority = NotificationPriority.medium,
  }) async {
    // Implement notification display
    // This is a placeholder - actual implementation depends on your NotificationService
    AppLogger.info('Notification: $title - $body');
  }
}
