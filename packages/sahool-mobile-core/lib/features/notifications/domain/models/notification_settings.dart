/// SAHOOL Notification Settings Model
/// نموذج إعدادات الإشعارات
///
/// Configurable notification preferences including:
/// - Per-category toggles
/// - Quiet hours
/// - Sound and vibration settings
library;

import 'notification_category.dart';

/// Notification settings model
/// نموذج إعدادات الإشعارات
class NotificationSettingsModel {
  /// Whether notifications are enabled globally
  final bool enabled;

  /// Per-category settings
  final Map<NotificationCategory, CategorySettings> categorySettings;

  /// Quiet hours configuration
  final QuietHoursSettings quietHours;

  /// Sound settings
  final SoundSettings soundSettings;

  /// Badge settings
  final BadgeSettings badgeSettings;

  /// Preview settings
  final PreviewSettings previewSettings;

  const NotificationSettingsModel({
    this.enabled = true,
    this.categorySettings = const {},
    this.quietHours = const QuietHoursSettings(),
    this.soundSettings = const SoundSettings(),
    this.badgeSettings = const BadgeSettings(),
    this.previewSettings = const PreviewSettings(),
  });

  /// Get default settings with all categories enabled
  factory NotificationSettingsModel.defaultSettings() {
    return NotificationSettingsModel(
      enabled: true,
      categorySettings: {
        for (final category in NotificationCategory.values)
          category: const CategorySettings(),
      },
      quietHours: const QuietHoursSettings(),
      soundSettings: const SoundSettings(),
      badgeSettings: const BadgeSettings(),
      previewSettings: const PreviewSettings(),
    );
  }

  /// Check if a specific category is enabled
  bool isCategoryEnabled(NotificationCategory category) {
    if (!enabled) return false;
    return categorySettings[category]?.enabled ?? true;
  }

  /// Check if sound is enabled for category
  bool isSoundEnabledForCategory(NotificationCategory category) {
    if (!soundSettings.enabled) return false;
    return categorySettings[category]?.soundEnabled ?? soundSettings.enabled;
  }

  /// Check if vibration is enabled for category
  bool isVibrationEnabledForCategory(NotificationCategory category) {
    if (!soundSettings.vibrationEnabled) return false;
    return categorySettings[category]?.vibrationEnabled ??
        soundSettings.vibrationEnabled;
  }

  /// Check if currently in quiet hours
  bool get isInQuietHours {
    if (!quietHours.enabled) return false;

    final now = DateTime.now();
    final currentHour = now.hour;
    final currentMinute = now.minute;
    final currentTime = currentHour * 60 + currentMinute;

    final startTime = quietHours.startHour * 60 + quietHours.startMinute;
    final endTime = quietHours.endHour * 60 + quietHours.endMinute;

    if (startTime <= endTime) {
      // Same day (e.g., 14:00 - 16:00)
      return currentTime >= startTime && currentTime < endTime;
    } else {
      // Crosses midnight (e.g., 22:00 - 07:00)
      return currentTime >= startTime || currentTime < endTime;
    }
  }

  /// Check if notification should be shown based on all settings
  bool shouldShowNotification(NotificationCategory category, bool isCritical) {
    // Always show critical notifications
    if (isCritical) return true;

    // Check global enable
    if (!enabled) return false;

    // Check category enable
    if (!isCategoryEnabled(category)) return false;

    // Check quiet hours (except for alerts which bypass quiet hours)
    if (isInQuietHours && category != NotificationCategory.alerts) {
      return false;
    }

    return true;
  }

  /// Create from JSON
  factory NotificationSettingsModel.fromJson(Map<String, dynamic> json) {
    return NotificationSettingsModel(
      enabled: json['enabled'] as bool? ?? true,
      categorySettings: _parseCategorySettings(
        json['category_settings'] as Map<String, dynamic>?,
      ),
      quietHours: json['quiet_hours'] != null
          ? QuietHoursSettings.fromJson(
              json['quiet_hours'] as Map<String, dynamic>)
          : const QuietHoursSettings(),
      soundSettings: json['sound_settings'] != null
          ? SoundSettings.fromJson(
              json['sound_settings'] as Map<String, dynamic>)
          : const SoundSettings(),
      badgeSettings: json['badge_settings'] != null
          ? BadgeSettings.fromJson(
              json['badge_settings'] as Map<String, dynamic>)
          : const BadgeSettings(),
      previewSettings: json['preview_settings'] != null
          ? PreviewSettings.fromJson(
              json['preview_settings'] as Map<String, dynamic>)
          : const PreviewSettings(),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'category_settings': {
        for (final entry in categorySettings.entries)
          entry.key.name: entry.value.toJson(),
      },
      'quiet_hours': quietHours.toJson(),
      'sound_settings': soundSettings.toJson(),
      'badge_settings': badgeSettings.toJson(),
      'preview_settings': previewSettings.toJson(),
    };
  }

  /// Copy with modifications
  NotificationSettingsModel copyWith({
    bool? enabled,
    Map<NotificationCategory, CategorySettings>? categorySettings,
    QuietHoursSettings? quietHours,
    SoundSettings? soundSettings,
    BadgeSettings? badgeSettings,
    PreviewSettings? previewSettings,
  }) {
    return NotificationSettingsModel(
      enabled: enabled ?? this.enabled,
      categorySettings: categorySettings ?? this.categorySettings,
      quietHours: quietHours ?? this.quietHours,
      soundSettings: soundSettings ?? this.soundSettings,
      badgeSettings: badgeSettings ?? this.badgeSettings,
      previewSettings: previewSettings ?? this.previewSettings,
    );
  }

  /// Update category settings
  NotificationSettingsModel updateCategorySettings(
    NotificationCategory category,
    CategorySettings settings,
  ) {
    return copyWith(
      categorySettings: {
        ...categorySettings,
        category: settings,
      },
    );
  }

  static Map<NotificationCategory, CategorySettings> _parseCategorySettings(
    Map<String, dynamic>? json,
  ) {
    if (json == null) return {};

    final result = <NotificationCategory, CategorySettings>{};
    for (final entry in json.entries) {
      final category = NotificationCategoryExtension.fromString(entry.key);
      if (category != null) {
        result[category] = CategorySettings.fromJson(
          entry.value as Map<String, dynamic>,
        );
      }
    }
    return result;
  }
}

/// Per-category settings
/// إعدادات كل فئة
class CategorySettings {
  /// Whether this category is enabled
  final bool enabled;

  /// Whether sound is enabled
  final bool soundEnabled;

  /// Whether vibration is enabled
  final bool vibrationEnabled;

  /// Whether to show preview
  final bool showPreview;

  /// Custom notification sound (null for default)
  final String? customSound;

  const CategorySettings({
    this.enabled = true,
    this.soundEnabled = true,
    this.vibrationEnabled = true,
    this.showPreview = true,
    this.customSound,
  });

  factory CategorySettings.fromJson(Map<String, dynamic> json) {
    return CategorySettings(
      enabled: json['enabled'] as bool? ?? true,
      soundEnabled: json['sound_enabled'] as bool? ?? true,
      vibrationEnabled: json['vibration_enabled'] as bool? ?? true,
      showPreview: json['show_preview'] as bool? ?? true,
      customSound: json['custom_sound'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'sound_enabled': soundEnabled,
      'vibration_enabled': vibrationEnabled,
      'show_preview': showPreview,
      'custom_sound': customSound,
    };
  }

  CategorySettings copyWith({
    bool? enabled,
    bool? soundEnabled,
    bool? vibrationEnabled,
    bool? showPreview,
    String? customSound,
  }) {
    return CategorySettings(
      enabled: enabled ?? this.enabled,
      soundEnabled: soundEnabled ?? this.soundEnabled,
      vibrationEnabled: vibrationEnabled ?? this.vibrationEnabled,
      showPreview: showPreview ?? this.showPreview,
      customSound: customSound ?? this.customSound,
    );
  }
}

/// Quiet hours settings
/// إعدادات ساعات الهدوء
class QuietHoursSettings {
  /// Whether quiet hours are enabled
  final bool enabled;

  /// Start hour (0-23)
  final int startHour;

  /// Start minute (0-59)
  final int startMinute;

  /// End hour (0-23)
  final int endHour;

  /// End minute (0-59)
  final int endMinute;

  /// Days of week enabled (0=Sunday, 6=Saturday)
  final List<int> enabledDays;

  /// Whether critical alerts bypass quiet hours
  final bool allowCritical;

  const QuietHoursSettings({
    this.enabled = false,
    this.startHour = 22,
    this.startMinute = 0,
    this.endHour = 7,
    this.endMinute = 0,
    this.enabledDays = const [0, 1, 2, 3, 4, 5, 6],
    this.allowCritical = true,
  });

  /// Get formatted start time
  String get startTimeFormatted =>
      '${startHour.toString().padLeft(2, '0')}:${startMinute.toString().padLeft(2, '0')}';

  /// Get formatted end time
  String get endTimeFormatted =>
      '${endHour.toString().padLeft(2, '0')}:${endMinute.toString().padLeft(2, '0')}';

  factory QuietHoursSettings.fromJson(Map<String, dynamic> json) {
    return QuietHoursSettings(
      enabled: json['enabled'] as bool? ?? false,
      startHour: json['start_hour'] as int? ?? 22,
      startMinute: json['start_minute'] as int? ?? 0,
      endHour: json['end_hour'] as int? ?? 7,
      endMinute: json['end_minute'] as int? ?? 0,
      enabledDays: (json['enabled_days'] as List<dynamic>?)
              ?.map((e) => e as int)
              .toList() ??
          const [0, 1, 2, 3, 4, 5, 6],
      allowCritical: json['allow_critical'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'start_hour': startHour,
      'start_minute': startMinute,
      'end_hour': endHour,
      'end_minute': endMinute,
      'enabled_days': enabledDays,
      'allow_critical': allowCritical,
    };
  }

  QuietHoursSettings copyWith({
    bool? enabled,
    int? startHour,
    int? startMinute,
    int? endHour,
    int? endMinute,
    List<int>? enabledDays,
    bool? allowCritical,
  }) {
    return QuietHoursSettings(
      enabled: enabled ?? this.enabled,
      startHour: startHour ?? this.startHour,
      startMinute: startMinute ?? this.startMinute,
      endHour: endHour ?? this.endHour,
      endMinute: endMinute ?? this.endMinute,
      enabledDays: enabledDays ?? this.enabledDays,
      allowCritical: allowCritical ?? this.allowCritical,
    );
  }
}

/// Sound settings
/// إعدادات الصوت
class SoundSettings {
  /// Whether sound is enabled
  final bool enabled;

  /// Whether vibration is enabled
  final bool vibrationEnabled;

  /// Sound volume (0.0 - 1.0)
  final double volume;

  /// Custom sound URI
  final String? customSoundUri;

  const SoundSettings({
    this.enabled = true,
    this.vibrationEnabled = true,
    this.volume = 1.0,
    this.customSoundUri,
  });

  factory SoundSettings.fromJson(Map<String, dynamic> json) {
    return SoundSettings(
      enabled: json['enabled'] as bool? ?? true,
      vibrationEnabled: json['vibration_enabled'] as bool? ?? true,
      volume: (json['volume'] as num?)?.toDouble() ?? 1.0,
      customSoundUri: json['custom_sound_uri'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'vibration_enabled': vibrationEnabled,
      'volume': volume,
      'custom_sound_uri': customSoundUri,
    };
  }

  SoundSettings copyWith({
    bool? enabled,
    bool? vibrationEnabled,
    double? volume,
    String? customSoundUri,
  }) {
    return SoundSettings(
      enabled: enabled ?? this.enabled,
      vibrationEnabled: vibrationEnabled ?? this.vibrationEnabled,
      volume: volume ?? this.volume,
      customSoundUri: customSoundUri ?? this.customSoundUri,
    );
  }
}

/// Badge settings
/// إعدادات الشارة
class BadgeSettings {
  /// Whether to show badge on app icon
  final bool showBadge;

  /// Whether to include read notifications in count
  final bool includeRead;

  /// Maximum badge count to display
  final int maxCount;

  const BadgeSettings({
    this.showBadge = true,
    this.includeRead = false,
    this.maxCount = 99,
  });

  factory BadgeSettings.fromJson(Map<String, dynamic> json) {
    return BadgeSettings(
      showBadge: json['show_badge'] as bool? ?? true,
      includeRead: json['include_read'] as bool? ?? false,
      maxCount: json['max_count'] as int? ?? 99,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'show_badge': showBadge,
      'include_read': includeRead,
      'max_count': maxCount,
    };
  }

  BadgeSettings copyWith({
    bool? showBadge,
    bool? includeRead,
    int? maxCount,
  }) {
    return BadgeSettings(
      showBadge: showBadge ?? this.showBadge,
      includeRead: includeRead ?? this.includeRead,
      maxCount: maxCount ?? this.maxCount,
    );
  }
}

/// Preview settings
/// إعدادات المعاينة
class PreviewSettings {
  /// Whether to show notification content preview
  final bool showPreview;

  /// Whether to show sender/source
  final bool showSender;

  /// Whether to show notification image
  final bool showImage;

  /// Preview text length limit
  final int maxPreviewLength;

  const PreviewSettings({
    this.showPreview = true,
    this.showSender = true,
    this.showImage = true,
    this.maxPreviewLength = 100,
  });

  factory PreviewSettings.fromJson(Map<String, dynamic> json) {
    return PreviewSettings(
      showPreview: json['show_preview'] as bool? ?? true,
      showSender: json['show_sender'] as bool? ?? true,
      showImage: json['show_image'] as bool? ?? true,
      maxPreviewLength: json['max_preview_length'] as int? ?? 100,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'show_preview': showPreview,
      'show_sender': showSender,
      'show_image': showImage,
      'max_preview_length': maxPreviewLength,
    };
  }

  PreviewSettings copyWith({
    bool? showPreview,
    bool? showSender,
    bool? showImage,
    int? maxPreviewLength,
  }) {
    return PreviewSettings(
      showPreview: showPreview ?? this.showPreview,
      showSender: showSender ?? this.showSender,
      showImage: showImage ?? this.showImage,
      maxPreviewLength: maxPreviewLength ?? this.maxPreviewLength,
    );
  }
}
