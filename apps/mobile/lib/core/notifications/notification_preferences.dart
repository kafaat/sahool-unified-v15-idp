/// SAHOOL Notification Preferences
/// تفضيلات الإشعارات
///
/// User preferences for notifications including:
/// - Notification type toggles
/// - Quiet hours settings
/// - Sound and vibration preferences
/// - Priority filtering
library;

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../utils/app_logger.dart';
import 'firebase_messaging_service.dart';

/// Notification preferences model
class NotificationPreferences {
  // Type-specific preferences
  final bool weatherAlerts;
  final bool diseaseDetection;
  final bool pestOutbreak;
  final bool sprayWindow;
  final bool harvestReminders;
  final bool irrigationReminders;
  final bool taskReminders;
  final bool fieldUpdates;
  final bool satelliteImages;
  final bool cropHealth;
  final bool marketPrices;
  final bool paymentDue;
  final bool lowStock;
  final bool systemNotifications;

  // Quiet hours
  final bool enableQuietHours;
  final TimeOfDay quietHoursStart;
  final TimeOfDay quietHoursEnd;

  // Sound and vibration
  final bool enableSound;
  final bool enableVibration;

  // Priority filtering
  final NotificationPriority minimumPriority;

  // Badge and preview
  final bool showBadge;
  final bool showPreview;

  const NotificationPreferences({
    this.weatherAlerts = true,
    this.diseaseDetection = true,
    this.pestOutbreak = true,
    this.sprayWindow = true,
    this.harvestReminders = true,
    this.irrigationReminders = true,
    this.taskReminders = true,
    this.fieldUpdates = true,
    this.satelliteImages = true,
    this.cropHealth = true,
    this.marketPrices = true,
    this.paymentDue = true,
    this.lowStock = false,
    this.systemNotifications = true,
    this.enableQuietHours = false,
    this.quietHoursStart = const TimeOfDay(hour: 22, minute: 0),
    this.quietHoursEnd = const TimeOfDay(hour: 6, minute: 0),
    this.enableSound = true,
    this.enableVibration = true,
    this.minimumPriority = NotificationPriority.low,
    this.showBadge = true,
    this.showPreview = true,
  });

  /// Check if notification type is enabled
  bool isTypeEnabled(SAHOOLNotificationType type) {
    switch (type) {
      case SAHOOLNotificationType.weatherAlert:
        return weatherAlerts;
      case SAHOOLNotificationType.diseaseDetected:
        return diseaseDetection;
      case SAHOOLNotificationType.pestOutbreak:
        return pestOutbreak;
      case SAHOOLNotificationType.sprayWindow:
        return sprayWindow;
      case SAHOOLNotificationType.harvestReminder:
        return harvestReminders;
      case SAHOOLNotificationType.irrigationReminder:
        return irrigationReminders;
      case SAHOOLNotificationType.taskReminder:
        return taskReminders;
      case SAHOOLNotificationType.fieldUpdate:
        return fieldUpdates;
      case SAHOOLNotificationType.satelliteReady:
        return satelliteImages;
      case SAHOOLNotificationType.cropHealth:
        return cropHealth;
      case SAHOOLNotificationType.marketPrice:
        return marketPrices;
      case SAHOOLNotificationType.paymentDue:
        return paymentDue;
      case SAHOOLNotificationType.lowStock:
        return lowStock;
      case SAHOOLNotificationType.system:
        return systemNotifications;
    }
  }

  /// Check if in quiet hours
  bool isInQuietHours() {
    if (!enableQuietHours) return false;

    final now = TimeOfDay.now();
    final nowMinutes = now.hour * 60 + now.minute;
    final startMinutes = quietHoursStart.hour * 60 + quietHoursStart.minute;
    final endMinutes = quietHoursEnd.hour * 60 + quietHoursEnd.minute;

    // Handle quiet hours that span midnight
    if (startMinutes > endMinutes) {
      return nowMinutes >= startMinutes || nowMinutes <= endMinutes;
    } else {
      return nowMinutes >= startMinutes && nowMinutes <= endMinutes;
    }
  }

  /// Check if priority meets minimum
  bool meetsPriorityThreshold(NotificationPriority priority) {
    final priorityValues = {
      NotificationPriority.low: 0,
      NotificationPriority.medium: 1,
      NotificationPriority.high: 2,
      NotificationPriority.critical: 3,
    };

    return priorityValues[priority]! >= priorityValues[minimumPriority]!;
  }

  /// Should show notification based on preferences
  bool shouldShowNotification(
    SAHOOLNotificationType type,
    NotificationPriority priority,
  ) {
    if (!isTypeEnabled(type)) return false;
    if (!meetsPriorityThreshold(priority)) return false;
    if (isInQuietHours() && priority != NotificationPriority.critical) {
      return false;
    }
    return true;
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'weatherAlerts': weatherAlerts,
      'diseaseDetection': diseaseDetection,
      'pestOutbreak': pestOutbreak,
      'sprayWindow': sprayWindow,
      'harvestReminders': harvestReminders,
      'irrigationReminders': irrigationReminders,
      'taskReminders': taskReminders,
      'fieldUpdates': fieldUpdates,
      'satelliteImages': satelliteImages,
      'cropHealth': cropHealth,
      'marketPrices': marketPrices,
      'paymentDue': paymentDue,
      'lowStock': lowStock,
      'systemNotifications': systemNotifications,
      'enableQuietHours': enableQuietHours,
      'quietHoursStart': '${quietHoursStart.hour}:${quietHoursStart.minute}',
      'quietHoursEnd': '${quietHoursEnd.hour}:${quietHoursEnd.minute}',
      'enableSound': enableSound,
      'enableVibration': enableVibration,
      'minimumPriority': minimumPriority.name,
      'showBadge': showBadge,
      'showPreview': showPreview,
    };
  }

  /// Create from JSON
  factory NotificationPreferences.fromJson(Map<String, dynamic> json) {
    TimeOfDay parseTime(String timeStr) {
      final parts = timeStr.split(':');
      return TimeOfDay(
        hour: int.parse(parts[0]),
        minute: int.parse(parts[1]),
      );
    }

    return NotificationPreferences(
      weatherAlerts: (json['weatherAlerts'] as bool?) ?? true,
      diseaseDetection: (json['diseaseDetection'] as bool?) ?? true,
      pestOutbreak: (json['pestOutbreak'] as bool?) ?? true,
      sprayWindow: (json['sprayWindow'] as bool?) ?? true,
      harvestReminders: (json['harvestReminders'] as bool?) ?? true,
      irrigationReminders: (json['irrigationReminders'] as bool?) ?? true,
      taskReminders: (json['taskReminders'] as bool?) ?? true,
      fieldUpdates: (json['fieldUpdates'] as bool?) ?? true,
      satelliteImages: (json['satelliteImages'] as bool?) ?? true,
      cropHealth: (json['cropHealth'] as bool?) ?? true,
      marketPrices: (json['marketPrices'] as bool?) ?? true,
      paymentDue: (json['paymentDue'] as bool?) ?? true,
      lowStock: (json['lowStock'] as bool?) ?? false,
      systemNotifications: (json['systemNotifications'] as bool?) ?? true,
      enableQuietHours: (json['enableQuietHours'] as bool?) ?? false,
      quietHoursStart: json['quietHoursStart'] != null
          ? parseTime(json['quietHoursStart'] as String)
          : const TimeOfDay(hour: 22, minute: 0),
      quietHoursEnd: json['quietHoursEnd'] != null
          ? parseTime(json['quietHoursEnd'] as String)
          : const TimeOfDay(hour: 6, minute: 0),
      enableSound: (json['enableSound'] as bool?) ?? true,
      enableVibration: (json['enableVibration'] as bool?) ?? true,
      minimumPriority: NotificationPriority.values.firstWhere(
        (p) => p.name == json['minimumPriority'],
        orElse: () => NotificationPriority.low,
      ),
      showBadge: (json['showBadge'] as bool?) ?? true,
      showPreview: (json['showPreview'] as bool?) ?? true,
    );
  }

  /// Create a copy with modifications
  NotificationPreferences copyWith({
    bool? weatherAlerts,
    bool? diseaseDetection,
    bool? pestOutbreak,
    bool? sprayWindow,
    bool? harvestReminders,
    bool? irrigationReminders,
    bool? taskReminders,
    bool? fieldUpdates,
    bool? satelliteImages,
    bool? cropHealth,
    bool? marketPrices,
    bool? paymentDue,
    bool? lowStock,
    bool? systemNotifications,
    bool? enableQuietHours,
    TimeOfDay? quietHoursStart,
    TimeOfDay? quietHoursEnd,
    bool? enableSound,
    bool? enableVibration,
    NotificationPriority? minimumPriority,
    bool? showBadge,
    bool? showPreview,
  }) {
    return NotificationPreferences(
      weatherAlerts: weatherAlerts ?? this.weatherAlerts,
      diseaseDetection: diseaseDetection ?? this.diseaseDetection,
      pestOutbreak: pestOutbreak ?? this.pestOutbreak,
      sprayWindow: sprayWindow ?? this.sprayWindow,
      harvestReminders: harvestReminders ?? this.harvestReminders,
      irrigationReminders: irrigationReminders ?? this.irrigationReminders,
      taskReminders: taskReminders ?? this.taskReminders,
      fieldUpdates: fieldUpdates ?? this.fieldUpdates,
      satelliteImages: satelliteImages ?? this.satelliteImages,
      cropHealth: cropHealth ?? this.cropHealth,
      marketPrices: marketPrices ?? this.marketPrices,
      paymentDue: paymentDue ?? this.paymentDue,
      lowStock: lowStock ?? this.lowStock,
      systemNotifications: systemNotifications ?? this.systemNotifications,
      enableQuietHours: enableQuietHours ?? this.enableQuietHours,
      quietHoursStart: quietHoursStart ?? this.quietHoursStart,
      quietHoursEnd: quietHoursEnd ?? this.quietHoursEnd,
      enableSound: enableSound ?? this.enableSound,
      enableVibration: enableVibration ?? this.enableVibration,
      minimumPriority: minimumPriority ?? this.minimumPriority,
      showBadge: showBadge ?? this.showBadge,
      showPreview: showPreview ?? this.showPreview,
    );
  }
}

/// Notification preferences service
class NotificationPreferencesService {
  static const _prefsKey = 'notification_preferences';
  static NotificationPreferencesService? _instance;

  static NotificationPreferencesService get instance {
    _instance ??= NotificationPreferencesService._();
    return _instance!;
  }

  NotificationPreferencesService._();

  NotificationPreferences? _preferences;
  SharedPreferences? _sharedPrefs;

  /// Initialize the service
  Future<void> initialize() async {
    _sharedPrefs = await SharedPreferences.getInstance();
    await loadPreferences();
  }

  /// Load preferences from storage
  Future<NotificationPreferences> loadPreferences() async {
    if (_sharedPrefs == null) {
      await initialize();
    }

    final json = _sharedPrefs!.getString(_prefsKey);
    if (json != null) {
      try {
        _preferences = NotificationPreferences.fromJson(
          jsonDecode(json) as Map<String, dynamic>,
        );
      } catch (e) {
        AppLogger.e('Failed to load notification preferences', tag: 'NotificationPrefs', error: e);
        _preferences = const NotificationPreferences();
      }
    } else {
      _preferences = const NotificationPreferences();
    }

    return _preferences!;
  }

  /// Save preferences to storage
  Future<void> savePreferences(NotificationPreferences preferences) async {
    if (_sharedPrefs == null) {
      await initialize();
    }

    _preferences = preferences;
    await _sharedPrefs!.setString(_prefsKey, jsonEncode(preferences.toJson()));
    AppLogger.d('Notification preferences saved', tag: 'NotificationPrefs');
  }

  /// Get current preferences
  NotificationPreferences getPreferences() {
    return _preferences ?? const NotificationPreferences();
  }

  /// Update a specific preference
  Future<void> updatePreference(
    NotificationPreferences Function(NotificationPreferences) update,
  ) async {
    final current = getPreferences();
    final updated = update(current);
    await savePreferences(updated);
  }

  /// Enable all notifications
  Future<void> enableAll() async {
    await updatePreference((prefs) => prefs.copyWith(
          weatherAlerts: true,
          diseaseDetection: true,
          pestOutbreak: true,
          sprayWindow: true,
          harvestReminders: true,
          irrigationReminders: true,
          taskReminders: true,
          fieldUpdates: true,
          satelliteImages: true,
          cropHealth: true,
          marketPrices: true,
          paymentDue: true,
          lowStock: true,
          systemNotifications: true,
        ));
  }

  /// Disable all notifications
  Future<void> disableAll() async {
    await updatePreference((prefs) => prefs.copyWith(
          weatherAlerts: false,
          diseaseDetection: false,
          pestOutbreak: false,
          sprayWindow: false,
          harvestReminders: false,
          irrigationReminders: false,
          taskReminders: false,
          fieldUpdates: false,
          satelliteImages: false,
          cropHealth: false,
          marketPrices: false,
          paymentDue: false,
          lowStock: false,
          systemNotifications: false,
        ));
  }

  /// Reset to defaults
  Future<void> resetToDefaults() async {
    await savePreferences(const NotificationPreferences());
  }
}

// =============================================================================
// Riverpod Providers
// =============================================================================

/// Notification preferences state notifier
class NotificationPrefsNotifier extends StateNotifier<NotificationPreferences> {
  final NotificationPreferencesService _service;

  NotificationPrefsNotifier(this._service)
      : super(const NotificationPreferences()) {
    _load();
  }

  Future<void> _load() async {
    state = await _service.loadPreferences();
  }

  Future<void> update(NotificationPreferences Function(NotificationPreferences) updater) async {
    state = updater(state);
    await _service.savePreferences(state);
  }

  Future<void> resetToDefaults() async {
    state = const NotificationPreferences();
    await _service.savePreferences(state);
  }
}

/// Notification preferences provider
final notificationPrefsProvider =
    StateNotifierProvider.autoDispose<NotificationPrefsNotifier, NotificationPreferences>((ref) {
  return NotificationPrefsNotifier(NotificationPreferencesService.instance);
});

/// Notification preferences screen (Riverpod-powered, zero setState)
class NotificationPreferencesScreen extends ConsumerWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final prefs = ref.watch(notificationPrefsProvider);
    final notifier = ref.read(notificationPrefsProvider.notifier);

    return Scaffold(
      appBar: AppBar(
        title: const Text('إعدادات الإشعارات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => notifier.resetToDefaults(),
            tooltip: 'إعادة تعيين',
          ),
        ],
      ),
      body: ListView(
        children: [
          // Notification Types Section
          _buildSectionHeader(context, 'أنواع الإشعارات'),
          _buildSwitchTile(
            title: 'تنبيهات الطقس',
            subtitle: 'صقيع، عاصفة، فيضان',
            icon: Icons.wb_sunny,
            value: prefs.weatherAlerts,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(weatherAlerts: value)),
          ),
          _buildSwitchTile(
            title: 'كشف الأمراض',
            subtitle: 'تنبيهات الأمراض المكتشفة',
            icon: Icons.healing,
            value: prefs.diseaseDetection,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(diseaseDetection: value)),
          ),
          _buildSwitchTile(
            title: 'انتشار الآفات',
            subtitle: 'تنبيهات الآفات في منطقتك',
            icon: Icons.bug_report,
            value: prefs.pestOutbreak,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(pestOutbreak: value)),
          ),
          _buildSwitchTile(
            title: 'أوقات الرش',
            subtitle: 'إشعارات الظروف المثالية للرش',
            icon: Icons.water_drop,
            value: prefs.sprayWindow,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(sprayWindow: value)),
          ),
          _buildSwitchTile(
            title: 'تذكيرات الحصاد',
            subtitle: 'تذكيرات موسم الحصاد',
            icon: Icons.agriculture,
            value: prefs.harvestReminders,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(harvestReminders: value)),
          ),
          _buildSwitchTile(
            title: 'تذكيرات الري',
            subtitle: 'جدولة الري والتذكيرات',
            icon: Icons.water,
            value: prefs.irrigationReminders,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(irrigationReminders: value)),
          ),
          _buildSwitchTile(
            title: 'صور الأقمار',
            subtitle: 'صور جديدة وتحليل NDVI',
            icon: Icons.satellite_alt,
            value: prefs.satelliteImages,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(satelliteImages: value)),
          ),
          _buildSwitchTile(
            title: 'أسعار السوق',
            subtitle: 'تحديثات أسعار المحاصيل',
            icon: Icons.trending_up,
            value: prefs.marketPrices,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(marketPrices: value)),
          ),

          const Divider(),

          // Quiet Hours Section
          _buildSectionHeader(context, 'ساعات الهدوء'),
          _buildSwitchTile(
            title: 'تفعيل ساعات الهدوء',
            subtitle: 'لا إشعارات خلال هذه الساعات',
            icon: Icons.bedtime,
            value: prefs.enableQuietHours,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(enableQuietHours: value)),
          ),
          if (prefs.enableQuietHours) ...[
            ListTile(
              leading: const Icon(Icons.nightlight),
              title: const Text('بداية الهدوء'),
              trailing: Text(_formatTime(prefs.quietHoursStart)),
              onTap: () async {
                final time = await showTimePicker(
                  context: context,
                  initialTime: prefs.quietHoursStart,
                );
                if (time != null) {
                  await notifier.update((p) => p.copyWith(quietHoursStart: time));
                }
              },
            ),
            ListTile(
              leading: const Icon(Icons.wb_sunny),
              title: const Text('نهاية الهدوء'),
              trailing: Text(_formatTime(prefs.quietHoursEnd)),
              onTap: () async {
                final time = await showTimePicker(
                  context: context,
                  initialTime: prefs.quietHoursEnd,
                );
                if (time != null) {
                  await notifier.update((p) => p.copyWith(quietHoursEnd: time));
                }
              },
            ),
          ],

          const Divider(),

          // Sound & Vibration
          _buildSectionHeader(context, 'الصوت والاهتزاز'),
          _buildSwitchTile(
            title: 'تفعيل الصوت',
            icon: Icons.volume_up,
            value: prefs.enableSound,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(enableSound: value)),
          ),
          _buildSwitchTile(
            title: 'تفعيل الاهتزاز',
            icon: Icons.vibration,
            value: prefs.enableVibration,
            onChanged: (value) =>
                notifier.update((p) => p.copyWith(enableVibration: value)),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(BuildContext context, String title) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Theme.of(context).primaryColor,
            ),
      ),
    );
  }

  Widget _buildSwitchTile({
    required String title,
    String? subtitle,
    required IconData icon,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return SwitchListTile(
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      secondary: Icon(icon),
      value: value,
      onChanged: onChanged,
    );
  }

  String _formatTime(TimeOfDay time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
