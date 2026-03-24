// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Motion Module
// وحدة الحركة - تصدير جميع مكونات تأثيرات الحركة
// ═══════════════════════════════════════════════════════════════════════════
//
// This module provides gyroscope-based parallax effects, tilt effects,
// and motion-responsive widgets for the SAHOOL mobile app.
//
// هذه الوحدة توفر تأثيرات المنظور القائمة على الجيروسكوب وتأثيرات الميلان
// والودجات المستجيبة للحركة لتطبيق ساهول للجوال.
//
// ## Quick Start
//
// 1. Initialize the motion system in your app's main():
// ```dart
// await MotionPreferencesService.instance.initialize();
// await MotionService.instance.start();
// ```
//
// 2. Wrap your screen with ParallaxContainer:
// ```dart
// ParallaxContainer(
//   screenId: 'home',
//   child: YourScreen(),
// )
// ```
//
// 3. Use motion widgets:
// ```dart
// ParallaxLayer(
//   depth: ParallaxDepthLayers.midBackground,
//   child: YourBackgroundWidget(),
// )
//
// TiltCard(
//   config: TiltConfig.card,
//   child: YourCardContent(),
// )
//
// FloatEffect(
//   config: FloatConfig.gentle,
//   child: YourFloatingWidget(),
// )
// ```
//
// ## Features
//
// - **Motion Service**: Gyroscope/accelerometer integration with smoothing
// - **Parallax Effects**: Multi-layer depth-based movement
// - **Tilt Effects**: 3D card tilting with dynamic shadows and glare
// - **Float/Wave/Shake**: Additional motion-responsive effects
// - **Accessibility**: Reduced motion support, battery saver mode
// - **Preferences**: User-configurable settings with persistence
//
// ## Usage with Riverpod
//
// ```dart
// final prefs = ref.watch(motionPreferencesProvider);
// final parallaxEnabled = ref.watch(parallaxEffectEnabledProvider);
// ```
//
// ═══════════════════════════════════════════════════════════════════════════

// Core motion service
export 'motion_service.dart';

// Parallax effects
export 'parallax_controller.dart';
export 'parallax_layer.dart';

// Tilt effects
export 'tilt_effect.dart';

// Additional motion effects
export 'motion_effects.dart';

// Preferences and accessibility
export 'motion_preferences.dart';

// Riverpod providers
export 'motion_providers.dart';

// Example implementations (for reference)
export 'motion_examples.dart';
