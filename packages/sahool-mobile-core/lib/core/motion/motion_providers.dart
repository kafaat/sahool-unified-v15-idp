// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Motion Providers
// مزودو الحركة - Riverpod providers لتأثيرات الحركة
// ═══════════════════════════════════════════════════════════════════════════

import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'motion_service.dart';
import 'motion_preferences.dart';
import 'parallax_controller.dart';
import 'tilt_effect.dart';

// ─────────────────────────────────────────────────────────────────────────────
// MOTION SERVICE PROVIDER
// ─────────────────────────────────────────────────────────────────────────────

/// Provider for the motion service singleton
/// مزود خدمة الحركة
final motionServiceProvider = Provider<MotionService>((ref) {
  return MotionService.instance;
});

/// Provider for current motion data stream
/// مزود تدفق بيانات الحركة الحالية
final motionDataStreamProvider = StreamProvider<MotionData>((ref) {
  final service = ref.watch(motionServiceProvider);
  return service.motionStream;
});

/// Provider for current motion data
/// مزود بيانات الحركة الحالية
final motionDataProvider = Provider<MotionData>((ref) {
  final service = ref.watch(motionServiceProvider);
  return service.currentData;
});

/// Provider for motion service active state
/// مزود حالة نشاط خدمة الحركة
final motionServiceActiveProvider = Provider<bool>((ref) {
  final service = ref.watch(motionServiceProvider);
  return service.isActive;
});

// ─────────────────────────────────────────────────────────────────────────────
// MOTION PREFERENCES PROVIDERS
// ─────────────────────────────────────────────────────────────────────────────

/// Provider for motion preferences service
/// مزود خدمة تفضيلات الحركة
final motionPreferencesServiceProvider = Provider<MotionPreferencesService>((ref) {
  return MotionPreferencesService.instance;
});

/// Provider for current motion preferences
/// مزود تفضيلات الحركة الحالية
final motionPreferencesProvider = Provider<MotionPreferences>((ref) {
  final service = ref.watch(motionPreferencesServiceProvider);
  return service.preferences;
});

/// Provider for motion effects enabled state
/// مزود حالة تفعيل تأثيرات الحركة
final motionEffectsEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.motionEffectsEnabled;
});

/// Provider for reduced motion state
/// مزود حالة تقليل الحركة
final reduceMotionProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.reduceMotion;
});

/// Provider for motion intensity
/// مزود شدة الحركة
final motionIntensityProvider = Provider<double>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.effectiveIntensity;
});

/// Provider for battery saver mode
/// مزود وضع توفير البطارية
final batteryMotionSaverProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.batterySaverMode;
});

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX CONTROLLER PROVIDERS
// ─────────────────────────────────────────────────────────────────────────────

/// Provider for parallax controller
/// مزود متحكم المنظور
final parallaxControllerProvider = Provider<ParallaxController>((ref) {
  final motionService = ref.watch(motionServiceProvider);
  final prefs = ref.watch(motionPreferencesProvider);

  final controller = ParallaxController(
    motionService: motionService,
    config: prefs.toParallaxConfig(),
  );

  ref.onDispose(() {
    controller.dispose();
  });

  return controller;
});

/// Provider for current parallax offset
/// مزود إزاحة المنظور الحالية
final parallaxOffsetProvider = Provider<ParallaxOffset>((ref) {
  final controller = ref.watch(parallaxControllerProvider);
  return controller.currentOffset;
});

/// Provider for parallax offset stream
/// مزود تدفق إزاحة المنظور
final parallaxOffsetStreamProvider = StreamProvider<ParallaxOffset>((ref) {
  final controller = ref.watch(parallaxControllerProvider);
  return controller.offsetStream;
});

// ─────────────────────────────────────────────────────────────────────────────
// EFFECT-SPECIFIC PROVIDERS
// ─────────────────────────────────────────────────────────────────────────────

/// Provider for parallax effect enabled
/// مزود تفعيل تأثير المنظور
final parallaxEffectEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.enableParallax && prefs.isEffectivelyEnabled;
});

/// Provider for tilt effect enabled
/// مزود تفعيل تأثير الميلان
final tiltEffectEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.enableTilt && prefs.isEffectivelyEnabled;
});

/// Provider for float effect enabled
/// مزود تفعيل تأثير الطفو
final floatEffectEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.enableFloat && prefs.isEffectivelyEnabled;
});

/// Provider for wave effect enabled
/// مزود تفعيل تأثير الموجة
final waveEffectEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.enableWave && prefs.isEffectivelyEnabled;
});

/// Provider for shake detection enabled
/// مزود تفعيل كشف الاهتزاز
final shakeDetectionEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.enableShakeDetection && prefs.isEffectivelyEnabled;
});

/// Provider for haptics enabled
/// مزود تفعيل ردود الفعل اللمسية
final hapticsEnabledProvider = Provider<bool>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.enableHaptics;
});

// ─────────────────────────────────────────────────────────────────────────────
// CONFIG PROVIDERS
// ─────────────────────────────────────────────────────────────────────────────

/// Provider for parallax config based on preferences
/// مزود إعدادات المنظور بناءً على التفضيلات
final parallaxConfigProvider = Provider<ParallaxConfig>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.toParallaxConfig();
});

/// Provider for tilt config based on preferences
/// مزود إعدادات الميلان بناءً على التفضيلات
final tiltConfigProvider = Provider<TiltConfig>((ref) {
  final prefs = ref.watch(motionPreferencesProvider);
  return prefs.toTiltConfig();
});

// ─────────────────────────────────────────────────────────────────────────────
// INITIALIZATION
// ─────────────────────────────────────────────────────────────────────────────

/// Initialize motion system
/// تهيئة نظام الحركة
Future<void> initializeMotionSystem(WidgetRef ref) async {
  // Initialize preferences service
  await MotionPreferencesService.instance.initialize();

  // Start motion service if enabled
  final prefs = MotionPreferencesService.instance.preferences;
  if (prefs.motionEffectsEnabled) {
    await MotionService.instance.start();
  }
}

/// Dispose motion system
/// التخلص من نظام الحركة
Future<void> disposeMotionSystem() async {
  await MotionService.instance.stop();
}
