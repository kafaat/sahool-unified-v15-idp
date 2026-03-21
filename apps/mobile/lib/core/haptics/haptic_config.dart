/// SAHOOL Haptic Feedback Configuration
/// إعدادات الاهتزاز للتغذية اللمسية
///
/// Provides configuration options for haptic feedback including:
/// - Enable/disable haptics
/// - Intensity levels
/// - Pattern customization
/// - Battery saver mode support
library;

import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'haptic_patterns.dart';

/// Haptic intensity level
/// مستوى شدة الاهتزاز
enum HapticIntensity {
  /// Off - No haptic feedback
  /// مغلق - بدون اهتزاز
  off,

  /// Light intensity (40% of defined)
  /// شدة خفيفة (40% من المحدد)
  light,

  /// Medium intensity (70% of defined)
  /// شدة متوسطة (70% من المحدد)
  medium,

  /// Strong intensity (100% of defined)
  /// شدة قوية (100% من المحدد)
  strong,
}

/// Extension to get intensity multiplier
extension HapticIntensityExtension on HapticIntensity {
  /// Get the intensity multiplier (0.0 to 1.0)
  double get multiplier {
    switch (this) {
      case HapticIntensity.off:
        return 0.0;
      case HapticIntensity.light:
        return 0.4;
      case HapticIntensity.medium:
        return 0.7;
      case HapticIntensity.strong:
        return 1.0;
    }
  }

  /// Get display name in English
  String get name {
    switch (this) {
      case HapticIntensity.off:
        return 'Off';
      case HapticIntensity.light:
        return 'Light';
      case HapticIntensity.medium:
        return 'Medium';
      case HapticIntensity.strong:
        return 'Strong';
    }
  }

  /// Get display name in Arabic
  String get nameAr {
    switch (this) {
      case HapticIntensity.off:
        return 'مغلق';
      case HapticIntensity.light:
        return 'خفيف';
      case HapticIntensity.medium:
        return 'متوسط';
      case HapticIntensity.strong:
        return 'قوي';
    }
  }
}

/// Haptic feedback configuration model
/// نموذج إعدادات الاهتزاز
class HapticConfig {
  /// Whether haptic feedback is enabled globally
  final bool enabled;

  /// Global intensity level
  final HapticIntensity intensity;

  /// Whether to respect system haptic settings
  final bool respectSystemSettings;

  /// Whether to reduce haptics when battery saver is on
  final bool batterySaverMode;

  /// Minimum battery level to enable full haptics (0-100)
  final int batterySaverThreshold;

  /// Pattern-specific overrides (pattern -> intensity)
  final Map<HapticPattern, HapticIntensity> patternOverrides;

  /// Whether to enable haptics for buttons
  final bool enableForButtons;

  /// Whether to enable haptics for list interactions
  final bool enableForLists;

  /// Whether to enable haptics for forms
  final bool enableForForms;

  /// Whether to enable haptics for navigation
  final bool enableForNavigation;

  /// Whether to enable haptics for notifications
  final bool enableForNotifications;

  /// Whether to enable haptics for gestures (swipe, drag)
  final bool enableForGestures;

  /// Whether to enable haptics for sliders
  final bool enableForSliders;

  /// Custom cooldown between haptic events in milliseconds
  final int cooldownMs;

  const HapticConfig({
    this.enabled = true,
    this.intensity = HapticIntensity.medium,
    this.respectSystemSettings = true,
    this.batterySaverMode = true,
    this.batterySaverThreshold = 20,
    this.patternOverrides = const {},
    this.enableForButtons = true,
    this.enableForLists = true,
    this.enableForForms = true,
    this.enableForNavigation = true,
    this.enableForNotifications = true,
    this.enableForGestures = true,
    this.enableForSliders = true,
    this.cooldownMs = 50,
  });

  /// Create a copy with modifications
  HapticConfig copyWith({
    bool? enabled,
    HapticIntensity? intensity,
    bool? respectSystemSettings,
    bool? batterySaverMode,
    int? batterySaverThreshold,
    Map<HapticPattern, HapticIntensity>? patternOverrides,
    bool? enableForButtons,
    bool? enableForLists,
    bool? enableForForms,
    bool? enableForNavigation,
    bool? enableForNotifications,
    bool? enableForGestures,
    bool? enableForSliders,
    int? cooldownMs,
  }) {
    return HapticConfig(
      enabled: enabled ?? this.enabled,
      intensity: intensity ?? this.intensity,
      respectSystemSettings: respectSystemSettings ?? this.respectSystemSettings,
      batterySaverMode: batterySaverMode ?? this.batterySaverMode,
      batterySaverThreshold:
          batterySaverThreshold ?? this.batterySaverThreshold,
      patternOverrides: patternOverrides ?? this.patternOverrides,
      enableForButtons: enableForButtons ?? this.enableForButtons,
      enableForLists: enableForLists ?? this.enableForLists,
      enableForForms: enableForForms ?? this.enableForForms,
      enableForNavigation: enableForNavigation ?? this.enableForNavigation,
      enableForNotifications:
          enableForNotifications ?? this.enableForNotifications,
      enableForGestures: enableForGestures ?? this.enableForGestures,
      enableForSliders: enableForSliders ?? this.enableForSliders,
      cooldownMs: cooldownMs ?? this.cooldownMs,
    );
  }

  /// Get effective intensity for a pattern considering overrides
  HapticIntensity getEffectiveIntensity(HapticPattern pattern) {
    if (!enabled) return HapticIntensity.off;
    return patternOverrides[pattern] ?? intensity;
  }

  /// Check if haptic feedback should be triggered for a category
  bool shouldTriggerForCategory(HapticCategory category) {
    if (!enabled) return false;

    switch (category) {
      case HapticCategory.button:
        return enableForButtons;
      case HapticCategory.list:
        return enableForLists;
      case HapticCategory.form:
        return enableForForms;
      case HapticCategory.navigation:
        return enableForNavigation;
      case HapticCategory.notification:
        return enableForNotifications;
      case HapticCategory.gesture:
        return enableForGestures;
      case HapticCategory.slider:
        return enableForSliders;
      case HapticCategory.other:
        return true;
    }
  }

  /// Convert to JSON for storage
  Map<String, dynamic> toJson() {
    return {
      'enabled': enabled,
      'intensity': intensity.name,
      'respectSystemSettings': respectSystemSettings,
      'batterySaverMode': batterySaverMode,
      'batterySaverThreshold': batterySaverThreshold,
      'patternOverrides': patternOverrides.map(
        (key, value) => MapEntry(key.name, value.name),
      ),
      'enableForButtons': enableForButtons,
      'enableForLists': enableForLists,
      'enableForForms': enableForForms,
      'enableForNavigation': enableForNavigation,
      'enableForNotifications': enableForNotifications,
      'enableForGestures': enableForGestures,
      'enableForSliders': enableForSliders,
      'cooldownMs': cooldownMs,
    };
  }

  /// Create from JSON
  factory HapticConfig.fromJson(Map<String, dynamic> json) {
    final overridesJson =
        json['patternOverrides'] as Map<String, dynamic>? ?? {};
    final patternOverrides = <HapticPattern, HapticIntensity>{};

    for (final entry in overridesJson.entries) {
      final pattern = HapticPattern.values.firstWhere(
        (p) => p.name == entry.key,
        orElse: () => HapticPattern.lightTap,
      );
      final intensity = HapticIntensity.values.firstWhere(
        (i) => i.name == entry.value,
        orElse: () => HapticIntensity.medium,
      );
      patternOverrides[pattern] = intensity;
    }

    return HapticConfig(
      enabled: json['enabled'] as bool? ?? true,
      intensity: HapticIntensity.values.firstWhere(
        (i) => i.name == json['intensity'],
        orElse: () => HapticIntensity.medium,
      ),
      respectSystemSettings: json['respectSystemSettings'] as bool? ?? true,
      batterySaverMode: json['batterySaverMode'] as bool? ?? true,
      batterySaverThreshold: json['batterySaverThreshold'] as int? ?? 20,
      patternOverrides: patternOverrides,
      enableForButtons: json['enableForButtons'] as bool? ?? true,
      enableForLists: json['enableForLists'] as bool? ?? true,
      enableForForms: json['enableForForms'] as bool? ?? true,
      enableForNavigation: json['enableForNavigation'] as bool? ?? true,
      enableForNotifications: json['enableForNotifications'] as bool? ?? true,
      enableForGestures: json['enableForGestures'] as bool? ?? true,
      enableForSliders: json['enableForSliders'] as bool? ?? true,
      cooldownMs: json['cooldownMs'] as int? ?? 50,
    );
  }

  /// Default configuration
  static const HapticConfig defaultConfig = HapticConfig();

  /// Minimal configuration (only essential feedback)
  static const HapticConfig minimalConfig = HapticConfig(
    intensity: HapticIntensity.light,
    enableForLists: false,
    enableForGestures: false,
    enableForSliders: false,
    cooldownMs: 100,
  );

  /// Battery saver configuration
  static const HapticConfig batterySaverConfig = HapticConfig(
    intensity: HapticIntensity.light,
    enableForLists: false,
    enableForGestures: false,
    enableForSliders: false,
    enableForNavigation: false,
    cooldownMs: 200,
  );

  /// Disabled configuration
  static const HapticConfig disabledConfig = HapticConfig(
    enabled: false,
  );

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is HapticConfig &&
        other.enabled == enabled &&
        other.intensity == intensity &&
        other.respectSystemSettings == respectSystemSettings &&
        other.batterySaverMode == batterySaverMode &&
        other.batterySaverThreshold == batterySaverThreshold &&
        mapEquals(other.patternOverrides, patternOverrides) &&
        other.enableForButtons == enableForButtons &&
        other.enableForLists == enableForLists &&
        other.enableForForms == enableForForms &&
        other.enableForNavigation == enableForNavigation &&
        other.enableForNotifications == enableForNotifications &&
        other.enableForGestures == enableForGestures &&
        other.enableForSliders == enableForSliders &&
        other.cooldownMs == cooldownMs;
  }

  @override
  int get hashCode {
    return Object.hash(
      enabled,
      intensity,
      respectSystemSettings,
      batterySaverMode,
      batterySaverThreshold,
      patternOverrides,
      enableForButtons,
      enableForLists,
      enableForForms,
      enableForNavigation,
      enableForNotifications,
      enableForGestures,
      enableForSliders,
      cooldownMs,
    );
  }
}

/// Categories for haptic feedback usage
/// فئات استخدام الاهتزاز
enum HapticCategory {
  button,
  list,
  form,
  navigation,
  notification,
  gesture,
  slider,
  other,
}

/// Haptic configuration storage service
/// خدمة تخزين إعدادات الاهتزاز
class HapticConfigStorage {
  static const String _storageKey = 'haptic_config';
  static HapticConfigStorage? _instance;

  HapticConfigStorage._();

  static HapticConfigStorage get instance {
    _instance ??= HapticConfigStorage._();
    return _instance!;
  }

  SharedPreferences? _prefs;
  HapticConfig? _cachedConfig;

  /// Initialize the storage
  Future<void> initialize() async {
    _prefs = await SharedPreferences.getInstance();
    await load();
  }

  /// Load configuration from storage
  Future<HapticConfig> load() async {
    if (_prefs == null) {
      await initialize();
    }

    final json = _prefs!.getString(_storageKey);
    if (json != null) {
      try {
        _cachedConfig = HapticConfig.fromJson(
          jsonDecode(json) as Map<String, dynamic>,
        );
      } catch (e) {
        debugPrint('Failed to load haptic config: $e');
        _cachedConfig = const HapticConfig();
      }
    } else {
      _cachedConfig = const HapticConfig();
    }

    return _cachedConfig!;
  }

  /// Save configuration to storage
  Future<void> save(HapticConfig config) async {
    if (_prefs == null) {
      await initialize();
    }

    _cachedConfig = config;
    await _prefs!.setString(_storageKey, jsonEncode(config.toJson()));
  }

  /// Get current configuration (cached)
  HapticConfig get config => _cachedConfig ?? const HapticConfig();

  /// Reset to defaults
  Future<void> reset() async {
    await save(const HapticConfig());
  }
}
