/// SAHOOL Haptic Feedback Service
/// خدمة الاهتزاز للتغذية اللمسية
///
/// Singleton service that handles all haptic feedback in the app.
/// Features:
/// - Platform-specific handling (iOS/Android)
/// - User preference respect
/// - Battery saver mode
/// - Cooldown to prevent spam
/// - Pattern-based feedback
library;

import 'dart:async';
import 'dart:io';

import 'package:flutter/services.dart';

import '../utils/app_logger.dart';
import 'haptic_config.dart';
import 'haptic_patterns.dart';

/// Singleton haptic feedback service
/// خدمة الاهتزاز المفردة
class HapticService {
  // ═══════════════════════════════════════════════════════════════════════════
  // Singleton Pattern
  // ═══════════════════════════════════════════════════════════════════════════

  static HapticService? _instance;
  static HapticService get instance {
    _instance ??= HapticService._();
    return _instance!;
  }

  HapticService._();

  // ═══════════════════════════════════════════════════════════════════════════
  // State
  // ═══════════════════════════════════════════════════════════════════════════

  HapticConfig _config = const HapticConfig();
  DateTime _lastHaptic = DateTime.now();
  bool _isInBatterySaverMode = false;
  bool _initialized = false;

  /// Current configuration
  HapticConfig get config => _config;

  /// Whether the service is initialized
  bool get isInitialized => _initialized;

  /// Whether haptics are currently enabled
  bool get isEnabled => _config.enabled && !(_config.batterySaverMode && _isInBatterySaverMode);

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the haptic service
  Future<void> initialize() async {
    if (_initialized) return;

    try {
      // Load saved configuration
      await HapticConfigStorage.instance.initialize();
      _config = HapticConfigStorage.instance.config;

      // Check battery status if needed
      if (_config.batterySaverMode) {
        await _checkBatteryStatus();
      }

      _initialized = true;
      AppLogger.i('Haptic service initialized', tag: 'HAPTIC');
    } catch (e) {
      AppLogger.e('Failed to initialize haptic service', tag: 'HAPTIC', error: e);
      _initialized = true; // Still mark as initialized to prevent retry loops
    }
  }

  /// Update configuration
  Future<void> updateConfig(HapticConfig config) async {
    _config = config;
    await HapticConfigStorage.instance.save(config);

    if (_config.batterySaverMode) {
      await _checkBatteryStatus();
    }

    AppLogger.i('Haptic config updated', tag: 'HAPTIC', data: {
      'enabled': config.enabled,
      'intensity': config.intensity.name,
    });
  }

  /// Check and update battery saver status
  Future<void> _checkBatteryStatus() async {
    // Battery check would require a platform channel or battery_plus package
    // For now, we'll assume normal operation
    // In a full implementation, this would query the device battery level
    _isInBatterySaverMode = false;
  }

  /// Update battery saver mode status
  void setBatterySaverMode(bool enabled) {
    _isInBatterySaverMode = enabled;
    AppLogger.d(
      'Battery saver mode ${enabled ? "enabled" : "disabled"}',
      tag: 'HAPTIC',
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Core Haptic Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Trigger haptic feedback with a specific pattern
  Future<void> trigger(
    HapticPattern pattern, {
    HapticCategory category = HapticCategory.other,
    bool force = false,
  }) async {
    if (!_shouldTrigger(pattern, category, force)) return;

    final definition = HapticPatterns.getDefinition(pattern);
    final intensity = _getEffectiveIntensity(pattern);

    if (intensity == HapticIntensity.off) return;

    _lastHaptic = DateTime.now();

    try {
      if (definition.useSystemFeedback && definition.systemFeedbackType != null) {
        await _triggerSystemHaptic(definition.systemFeedbackType!);
      } else if (definition.vibrationPattern != null) {
        await _triggerCustomVibration(definition.vibrationPattern!, intensity);
      } else {
        // Fallback to medium impact
        await _triggerSystemHaptic(HapticFeedbackType.mediumImpact);
      }

      AppLogger.d(
        'Haptic triggered: ${pattern.name}',
        tag: 'HAPTIC',
        data: {'intensity': intensity.name},
      );
    } catch (e) {
      AppLogger.e('Failed to trigger haptic', tag: 'HAPTIC', error: e);
    }
  }

  /// Trigger system haptic feedback
  Future<void> _triggerSystemHaptic(HapticFeedbackType type) async {
    switch (type) {
      case HapticFeedbackType.lightImpact:
        await HapticFeedback.lightImpact();
        break;
      case HapticFeedbackType.mediumImpact:
        await HapticFeedback.mediumImpact();
        break;
      case HapticFeedbackType.heavyImpact:
        await HapticFeedback.heavyImpact();
        break;
      case HapticFeedbackType.selectionClick:
        await HapticFeedback.selectionClick();
        break;
      case HapticFeedbackType.vibrate:
        await HapticFeedback.vibrate();
        break;
    }
  }

  /// Trigger custom vibration pattern
  Future<void> _triggerCustomVibration(
    List<int> pattern,
    HapticIntensity intensity,
  ) async {
    // Custom vibration requires platform channels or vibration package
    // For now, we simulate with multiple system haptics
    // A full implementation would use the Vibration package

    if (Platform.isIOS) {
      // iOS doesn't support custom patterns, use best approximation
      for (int i = 0; i < pattern.length; i += 2) {
        if (i > 0) {
          await Future.delayed(Duration(milliseconds: pattern[i]));
        }
        if (i + 1 < pattern.length) {
          await _selectSystemHapticForIntensity(intensity);
        }
      }
    } else {
      // Android - simulate pattern
      for (int i = 0; i < pattern.length; i += 2) {
        if (i > 0) {
          await Future.delayed(Duration(milliseconds: pattern[i]));
        }
        if (i + 1 < pattern.length) {
          await _selectSystemHapticForIntensity(intensity);
        }
      }
    }
  }

  /// Select appropriate system haptic based on intensity
  Future<void> _selectSystemHapticForIntensity(HapticIntensity intensity) async {
    switch (intensity) {
      case HapticIntensity.off:
        break;
      case HapticIntensity.light:
        await HapticFeedback.lightImpact();
        break;
      case HapticIntensity.medium:
        await HapticFeedback.mediumImpact();
        break;
      case HapticIntensity.strong:
        await HapticFeedback.heavyImpact();
        break;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Convenience Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Light tap feedback (selection, toggle)
  Future<void> lightTap() => trigger(HapticPattern.lightTap);

  /// Medium tap feedback (button press)
  Future<void> mediumTap() => trigger(HapticPattern.mediumTap);

  /// Heavy tap feedback (important action)
  Future<void> heavyTap() => trigger(HapticPattern.heavyTap);

  /// Success feedback (task complete)
  Future<void> success() => trigger(HapticPattern.success);

  /// Warning feedback (alert)
  Future<void> warning() => trigger(HapticPattern.warning);

  /// Error feedback (validation fail)
  Future<void> error() => trigger(HapticPattern.error);

  /// Notification feedback (new alert)
  Future<void> notification() =>
      trigger(HapticPattern.notification, category: HapticCategory.notification);

  /// Scroll feedback (list boundaries)
  Future<void> scroll() =>
      trigger(HapticPattern.scroll, category: HapticCategory.list);

  /// Drag feedback (drag & drop)
  Future<void> drag() =>
      trigger(HapticPattern.drag, category: HapticCategory.gesture);

  /// Selection changed feedback
  Future<void> selectionChanged() =>
      trigger(HapticPattern.selectionChanged, category: HapticCategory.list);

  /// Impact feedback (collisions)
  Future<void> impact() => trigger(HapticPattern.impact);

  /// Tick feedback (slider increments)
  Future<void> tick() =>
      trigger(HapticPattern.tick, category: HapticCategory.slider);

  /// Soft feedback (subtle interactions)
  Future<void> soft() => trigger(HapticPattern.soft);

  /// Rigid feedback (rigid interactions)
  Future<void> rigid() => trigger(HapticPattern.rigid);

  // ═══════════════════════════════════════════════════════════════════════════
  // Category-Specific Methods
  // ═══════════════════════════════════════════════════════════════════════════

  /// Button tap feedback
  Future<void> buttonTap({bool isDestructive = false}) {
    return trigger(
      isDestructive ? HapticPattern.heavyTap : HapticPattern.mediumTap,
      category: HapticCategory.button,
    );
  }

  /// List item tap feedback
  Future<void> listItemTap() {
    return trigger(HapticPattern.lightTap, category: HapticCategory.list);
  }

  /// List item long press feedback
  Future<void> listItemLongPress() {
    return trigger(HapticPattern.mediumTap, category: HapticCategory.list);
  }

  /// Navigation tab tap feedback
  Future<void> navigationTap() {
    return trigger(HapticPattern.lightTap, category: HapticCategory.navigation);
  }

  /// Form field validation success
  Future<void> formValidationSuccess() {
    return trigger(HapticPattern.soft, category: HapticCategory.form);
  }

  /// Form field validation error
  Future<void> formValidationError() {
    return trigger(HapticPattern.error, category: HapticCategory.form);
  }

  /// Form submission success
  Future<void> formSubmissionSuccess() {
    return trigger(HapticPattern.success, category: HapticCategory.form);
  }

  /// Pull to refresh activated
  Future<void> pullToRefresh() {
    return trigger(HapticPattern.mediumTap, category: HapticCategory.gesture);
  }

  /// Swipe action triggered
  Future<void> swipeAction() {
    return trigger(HapticPattern.lightTap, category: HapticCategory.gesture);
  }

  /// Slider value changed
  Future<void> sliderTick() {
    return trigger(HapticPattern.tick, category: HapticCategory.slider);
  }

  /// Slider reached boundary
  Future<void> sliderBoundary() {
    return trigger(HapticPattern.impact, category: HapticCategory.slider);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Private Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Check if haptic should be triggered
  bool _shouldTrigger(HapticPattern pattern, HapticCategory category, bool force) {
    if (force) return true;

    // Check global enabled
    if (!_config.enabled) return false;

    // Check category enabled
    if (!_config.shouldTriggerForCategory(category)) return false;

    // Check battery saver
    if (_config.batterySaverMode && _isInBatterySaverMode) {
      // In battery saver, only allow critical feedback
      if (pattern != HapticPattern.error && pattern != HapticPattern.warning) {
        return false;
      }
    }

    // Check cooldown
    final elapsed = DateTime.now().difference(_lastHaptic).inMilliseconds;
    if (elapsed < _config.cooldownMs) return false;

    return true;
  }

  /// Get effective intensity considering config and overrides
  HapticIntensity _getEffectiveIntensity(HapticPattern pattern) {
    if (_config.batterySaverMode && _isInBatterySaverMode) {
      // Reduce intensity in battery saver mode
      final baseIntensity = _config.getEffectiveIntensity(pattern);
      if (baseIntensity.index > HapticIntensity.light.index) {
        return HapticIntensity.light;
      }
      return baseIntensity;
    }

    return _config.getEffectiveIntensity(pattern);
  }
}

/// Global convenience function for haptic feedback
/// دالة مريحة للاهتزاز
Future<void> haptic(HapticPattern pattern, {HapticCategory? category}) {
  return HapticService.instance.trigger(
    pattern,
    category: category ?? HapticCategory.other,
  );
}

/// Extension on BuildContext for easy haptic access
/// إضافة للسياق للوصول السهل للاهتزاز
extension HapticContext on Object {
  /// Get haptic service instance
  HapticService get haptics => HapticService.instance;
}
