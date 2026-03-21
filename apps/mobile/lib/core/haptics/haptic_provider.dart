/// SAHOOL Haptic Feedback Providers
/// مزودات الاهتزاز للتغذية اللمسية
///
/// Riverpod providers for haptic feedback management:
/// - HapticService provider
/// - HapticConfig state management
/// - Initialization provider
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'haptic_config.dart';
import 'haptic_patterns.dart';
import 'haptic_service.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Haptic Service Provider
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for the HapticService singleton
/// مزود خدمة الاهتزاز
final hapticServiceProvider = Provider<HapticService>((ref) {
  return HapticService.instance;
});

// ═══════════════════════════════════════════════════════════════════════════
// Haptic Initialization Provider
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for haptic service initialization
/// مزود تهيئة خدمة الاهتزاز
final hapticInitializationProvider = FutureProvider<void>((ref) async {
  final service = ref.read(hapticServiceProvider);
  await service.initialize();
});

// ═══════════════════════════════════════════════════════════════════════════
// Haptic Config Provider
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for haptic configuration state
/// مزود حالة إعدادات الاهتزاز
final hapticConfigProvider =
    StateNotifierProvider<HapticConfigNotifier, HapticConfig>((ref) {
  return HapticConfigNotifier(ref);
});

/// State notifier for haptic configuration
/// مُخطر حالة إعدادات الاهتزاز
class HapticConfigNotifier extends StateNotifier<HapticConfig> {
  final Ref _ref;

  HapticConfigNotifier(this._ref) : super(const HapticConfig()) {
    _loadConfig();
  }

  /// Load configuration from storage
  Future<void> _loadConfig() async {
    await HapticConfigStorage.instance.initialize();
    state = HapticConfigStorage.instance.config;
  }

  /// Update the haptic configuration
  Future<void> updateConfig(HapticConfig config) async {
    state = config;
    await _ref.read(hapticServiceProvider).updateConfig(config);
  }

  /// Toggle haptic feedback enabled/disabled
  Future<void> toggleEnabled() async {
    final newConfig = state.copyWith(enabled: !state.enabled);
    await updateConfig(newConfig);
  }

  /// Set intensity level
  Future<void> setIntensity(HapticIntensity intensity) async {
    final newConfig = state.copyWith(intensity: intensity);
    await updateConfig(newConfig);
  }

  /// Toggle battery saver mode
  Future<void> toggleBatterySaverMode() async {
    final newConfig = state.copyWith(batterySaverMode: !state.batterySaverMode);
    await updateConfig(newConfig);
  }

  /// Set battery saver threshold
  Future<void> setBatterySaverThreshold(int threshold) async {
    final newConfig = state.copyWith(batterySaverThreshold: threshold);
    await updateConfig(newConfig);
  }

  /// Toggle category enabled
  Future<void> toggleCategory(HapticCategory category) async {
    HapticConfig newConfig;
    switch (category) {
      case HapticCategory.button:
        newConfig = state.copyWith(enableForButtons: !state.enableForButtons);
        break;
      case HapticCategory.list:
        newConfig = state.copyWith(enableForLists: !state.enableForLists);
        break;
      case HapticCategory.form:
        newConfig = state.copyWith(enableForForms: !state.enableForForms);
        break;
      case HapticCategory.navigation:
        newConfig =
            state.copyWith(enableForNavigation: !state.enableForNavigation);
        break;
      case HapticCategory.notification:
        newConfig = state.copyWith(
            enableForNotifications: !state.enableForNotifications);
        break;
      case HapticCategory.gesture:
        newConfig = state.copyWith(enableForGestures: !state.enableForGestures);
        break;
      case HapticCategory.slider:
        newConfig = state.copyWith(enableForSliders: !state.enableForSliders);
        break;
      case HapticCategory.other:
        return; // No toggle for other category
    }
    await updateConfig(newConfig);
  }

  /// Set category enabled
  Future<void> setCategoryEnabled(HapticCategory category, bool enabled) async {
    HapticConfig newConfig;
    switch (category) {
      case HapticCategory.button:
        newConfig = state.copyWith(enableForButtons: enabled);
        break;
      case HapticCategory.list:
        newConfig = state.copyWith(enableForLists: enabled);
        break;
      case HapticCategory.form:
        newConfig = state.copyWith(enableForForms: enabled);
        break;
      case HapticCategory.navigation:
        newConfig = state.copyWith(enableForNavigation: enabled);
        break;
      case HapticCategory.notification:
        newConfig = state.copyWith(enableForNotifications: enabled);
        break;
      case HapticCategory.gesture:
        newConfig = state.copyWith(enableForGestures: enabled);
        break;
      case HapticCategory.slider:
        newConfig = state.copyWith(enableForSliders: enabled);
        break;
      case HapticCategory.other:
        return;
    }
    await updateConfig(newConfig);
  }

  /// Set pattern intensity override
  Future<void> setPatternIntensity(
    HapticPattern pattern,
    HapticIntensity intensity,
  ) async {
    final newOverrides = Map<HapticPattern, HapticIntensity>.from(
      state.patternOverrides,
    );

    if (intensity == state.intensity) {
      // Remove override if it matches global intensity
      newOverrides.remove(pattern);
    } else {
      newOverrides[pattern] = intensity;
    }

    final newConfig = state.copyWith(patternOverrides: newOverrides);
    await updateConfig(newConfig);
  }

  /// Clear all pattern overrides
  Future<void> clearPatternOverrides() async {
    final newConfig = state.copyWith(
      patternOverrides: const {},
    );
    await updateConfig(newConfig);
  }

  /// Set cooldown time
  Future<void> setCooldown(int cooldownMs) async {
    final newConfig = state.copyWith(cooldownMs: cooldownMs);
    await updateConfig(newConfig);
  }

  /// Reset to default configuration
  Future<void> resetToDefaults() async {
    await updateConfig(const HapticConfig());
  }

  /// Apply minimal configuration
  Future<void> applyMinimalConfig() async {
    await updateConfig(HapticConfig.minimalConfig);
  }

  /// Apply battery saver configuration
  Future<void> applyBatterySaverConfig() async {
    await updateConfig(HapticConfig.batterySaverConfig);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Convenience Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for whether haptics are enabled
/// مزود لمعرفة ما إذا كان الاهتزاز مفعلاً
final hapticEnabledProvider = Provider<bool>((ref) {
  final config = ref.watch(hapticConfigProvider);
  return config.enabled;
});

/// Provider for haptic intensity
/// مزود لشدة الاهتزاز
final hapticIntensityProvider = Provider<HapticIntensity>((ref) {
  final config = ref.watch(hapticConfigProvider);
  return config.intensity;
});

/// Provider for battery saver mode
/// مزود لوضع توفير البطارية
final hapticBatterySaverProvider = Provider<bool>((ref) {
  final config = ref.watch(hapticConfigProvider);
  return config.batterySaverMode;
});

/// Provider for category enabled state
/// مزود لحالة تفعيل الفئة
final hapticCategoryEnabledProvider =
    Provider.family<bool, HapticCategory>((ref, category) {
  final config = ref.watch(hapticConfigProvider);
  return config.shouldTriggerForCategory(category);
});

// ═══════════════════════════════════════════════════════════════════════════
// Action Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for triggering haptic feedback
/// مزود لتشغيل الاهتزاز
final triggerHapticProvider = Provider<
    Future<void> Function(HapticPattern, {HapticCategory? category})>((ref) {
  final service = ref.read(hapticServiceProvider);
  return (pattern, {category}) =>
      service.trigger(pattern, category: category ?? HapticCategory.other);
});

/// Provider for common haptic actions
/// مزود للإجراءات الشائعة للاهتزاز
final hapticActionsProvider = Provider<HapticActions>((ref) {
  return HapticActions(ref.read(hapticServiceProvider));
});

/// Helper class for common haptic actions
/// فئة مساعدة للإجراءات الشائعة للاهتزاز
class HapticActions {
  final HapticService _service;

  HapticActions(this._service);

  void lightTap() => _service.lightTap();
  void mediumTap() => _service.mediumTap();
  void heavyTap() => _service.heavyTap();
  void success() => _service.success();
  void warning() => _service.warning();
  void error() => _service.error();
  void notification() => _service.notification();
  void buttonTap({bool isDestructive = false}) =>
      _service.buttonTap(isDestructive: isDestructive);
  void listItemTap() => _service.listItemTap();
  void navigationTap() => _service.navigationTap();
  void pullToRefresh() => _service.pullToRefresh();
  void swipeAction() => _service.swipeAction();
  void sliderTick() => _service.sliderTick();
}
