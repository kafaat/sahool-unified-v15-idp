/// SAHOOL Notification Preferences
/// تفضيلات الإشعارات
///
/// User preferences for notifications including:
/// - Notification type toggles
/// - Quiet hours settings
/// - Sound and vibration preferences
/// - Priority filtering

import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'firebase_messaging_service.dart';

/// Notification preferences model
class NotificationPreferences {
  // Type-specific preferences
  bool weatherAlerts;
  bool diseaseDetection;
  bool pestOutbreak;
  bool sprayWindow;
  bool harvestReminders;
  bool irrigationReminders;
  bool taskReminders;
  bool fieldUpdates;
  bool satelliteImages;
  bool cropHealth;
  bool marketPrices;
  bool paymentDue;
  bool lowStock;
  bool systemNotifications;

  // Quiet hours
  bool enableQuietHours;
  TimeOfDay quietHoursStart;
  TimeOfDay quietHoursEnd;

  // Sound and vibration
  bool enableSound;
  bool enableVibration;

  // Priority filtering
  NotificationPriority minimumPriority;

  // Badge and preview
  bool showBadge;
  bool showPreview;

  NotificationPreferences({
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
    // Check if type is enabled
    if (!isTypeEnabled(type)) return false;

    // Check priority threshold
    if (!meetsPriorityThreshold(priority)) return false;

    // Check quiet hours (critical notifications override quiet hours)
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
      weatherAlerts: json['weatherAlerts'] ?? true,
      diseaseDetection: json['diseaseDetection'] ?? true,
      pestOutbreak: json['pestOutbreak'] ?? true,
      sprayWindow: json['sprayWindow'] ?? true,
      harvestReminders: json['harvestReminders'] ?? true,
      irrigationReminders: json['irrigationReminders'] ?? true,
      taskReminders: json['taskReminders'] ?? true,
      fieldUpdates: json['fieldUpdates'] ?? true,
      satelliteImages: json['satelliteImages'] ?? true,
      cropHealth: json['cropHealth'] ?? true,
      marketPrices: json['marketPrices'] ?? true,
      paymentDue: json['paymentDue'] ?? true,
      lowStock: json['lowStock'] ?? false,
      systemNotifications: json['systemNotifications'] ?? true,
      enableQuietHours: json['enableQuietHours'] ?? false,
      quietHoursStart: json['quietHoursStart'] != null
          ? parseTime(json['quietHoursStart'])
          : const TimeOfDay(hour: 22, minute: 0),
      quietHoursEnd: json['quietHoursEnd'] != null
          ? parseTime(json['quietHoursEnd'])
          : const TimeOfDay(hour: 6, minute: 0),
      enableSound: json['enableSound'] ?? true,
      enableVibration: json['enableVibration'] ?? true,
      minimumPriority: NotificationPriority.values.firstWhere(
        (p) => p.name == json['minimumPriority'],
        orElse: () => NotificationPriority.low,
      ),
      showBadge: json['showBadge'] ?? true,
      showPreview: json['showPreview'] ?? true,
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
        debugPrint('❌ Failed to load preferences: $e');
        _preferences = NotificationPreferences();
      }
    } else {
      _preferences = NotificationPreferences();
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
    debugPrint('✅ Notification preferences saved');
  }

  /// Get current preferences
  NotificationPreferences getPreferences() {
    return _preferences ?? NotificationPreferences();
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
    await updatePreference((prefs) => NotificationPreferences(
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
          enableQuietHours: prefs.enableQuietHours,
          quietHoursStart: prefs.quietHoursStart,
          quietHoursEnd: prefs.quietHoursEnd,
          enableSound: prefs.enableSound,
          enableVibration: prefs.enableVibration,
          minimumPriority: prefs.minimumPriority,
          showBadge: prefs.showBadge,
          showPreview: prefs.showPreview,
        ));
  }

  /// Disable all notifications
  Future<void> disableAll() async {
    await updatePreference((prefs) => NotificationPreferences(
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
          enableQuietHours: prefs.enableQuietHours,
          quietHoursStart: prefs.quietHoursStart,
          quietHoursEnd: prefs.quietHoursEnd,
          enableSound: prefs.enableSound,
          enableVibration: prefs.enableVibration,
          minimumPriority: prefs.minimumPriority,
          showBadge: prefs.showBadge,
          showPreview: prefs.showPreview,
        ));
  }

  /// Reset to defaults
  Future<void> resetToDefaults() async {
    await savePreferences(NotificationPreferences());
  }
}

/// Notification preferences screen
class NotificationPreferencesScreen extends StatefulWidget {
  const NotificationPreferencesScreen({super.key});

  @override
  State<NotificationPreferencesScreen> createState() =>
      _NotificationPreferencesScreenState();
}

class _NotificationPreferencesScreenState
    extends State<NotificationPreferencesScreen> {
  late NotificationPreferences _prefs;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    _prefs = await NotificationPreferencesService.instance.loadPreferences();
    setState(() => _loading = false);
  }

  Future<void> _savePreferences() async {
    await NotificationPreferencesService.instance.savePreferences(_prefs);
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('تم حفظ الإعدادات')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('إعدادات الإشعارات'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              await NotificationPreferencesService.instance.resetToDefaults();
              await _loadPreferences();
            },
            tooltip: 'إعادة تعيين',
          ),
        ],
      ),
      body: ListView(
        children: [
          // Notification Types Section
          _buildSectionHeader('أنواع الإشعارات'),
          _buildSwitchTile(
            title: 'تنبيهات الطقس',
            subtitle: 'صقيع، عاصفة، فيضان',
            icon: Icons.wb_sunny,
            value: _prefs.weatherAlerts,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(weatherAlerts: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'كشف الأمراض',
            subtitle: 'تنبيهات الأمراض المكتشفة',
            icon: Icons.healing,
            value: _prefs.diseaseDetection,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(diseaseDetection: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'انتشار الآفات',
            subtitle: 'تنبيهات الآفات في منطقتك',
            icon: Icons.bug_report,
            value: _prefs.pestOutbreak,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(pestOutbreak: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'أوقات الرش',
            subtitle: 'إشعارات الظروف المثالية للرش',
            icon: Icons.water_drop,
            value: _prefs.sprayWindow,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(sprayWindow: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'تذكيرات الحصاد',
            subtitle: 'تذكيرات موسم الحصاد',
            icon: Icons.agriculture,
            value: _prefs.harvestReminders,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(harvestReminders: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'تذكيرات الري',
            subtitle: 'جدولة الري والتذكيرات',
            icon: Icons.water,
            value: _prefs.irrigationReminders,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(irrigationReminders: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'صور الأقمار',
            subtitle: 'صور جديدة وتحليل NDVI',
            icon: Icons.satellite_alt,
            value: _prefs.satelliteImages,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(satelliteImages: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'أسعار السوق',
            subtitle: 'تحديثات أسعار المحاصيل',
            icon: Icons.trending_up,
            value: _prefs.marketPrices,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(marketPrices: value));
              _savePreferences();
            },
          ),

          const Divider(),

          // Quiet Hours Section
          _buildSectionHeader('ساعات الهدوء'),
          _buildSwitchTile(
            title: 'تفعيل ساعات الهدوء',
            subtitle: 'لا إشعارات خلال هذه الساعات',
            icon: Icons.bedtime,
            value: _prefs.enableQuietHours,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(enableQuietHours: value));
              _savePreferences();
            },
          ),
          if (_prefs.enableQuietHours) ...[
            ListTile(
              leading: const Icon(Icons.nightlight),
              title: const Text('بداية الهدوء'),
              trailing: Text(_formatTime(_prefs.quietHoursStart)),
              onTap: () async {
                final time = await showTimePicker(
                  context: context,
                  initialTime: _prefs.quietHoursStart,
                );
                if (time != null) {
                  setState(() => _prefs = _prefs.copyWith(quietHoursStart: time));
                  _savePreferences();
                }
              },
            ),
            ListTile(
              leading: const Icon(Icons.wb_sunny),
              title: const Text('نهاية الهدوء'),
              trailing: Text(_formatTime(_prefs.quietHoursEnd)),
              onTap: () async {
                final time = await showTimePicker(
                  context: context,
                  initialTime: _prefs.quietHoursEnd,
                );
                if (time != null) {
                  setState(() => _prefs = _prefs.copyWith(quietHoursEnd: time));
                  _savePreferences();
                }
              },
            ),
          ],

          const Divider(),

          // Sound & Vibration
          _buildSectionHeader('الصوت والاهتزاز'),
          _buildSwitchTile(
            title: 'تفعيل الصوت',
            icon: Icons.volume_up,
            value: _prefs.enableSound,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(enableSound: value));
              _savePreferences();
            },
          ),
          _buildSwitchTile(
            title: 'تفعيل الاهتزاز',
            icon: Icons.vibration,
            value: _prefs.enableVibration,
            onChanged: (value) {
              setState(() => _prefs = _prefs.copyWith(enableVibration: value));
              _savePreferences();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
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
