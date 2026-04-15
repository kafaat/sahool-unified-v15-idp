/// SAHOOL Haptic Feedback System
/// نظام الاهتزاز للتغذية اللمسية
///
/// A comprehensive haptic feedback system for the SAHOOL mobile app.
/// نظام شامل للاهتزاز لتطبيق سهول الجوال.
///
/// Features:
/// - Multiple vibration patterns
/// - User preference support
/// - Platform-specific handling
/// - Battery saver mode
/// - Riverpod state management
///
/// Usage:
/// ```dart
/// // Import the haptics module
/// import 'package:sahool_field_app/core/haptics/haptics.dart';
///
/// // Trigger haptic feedback
/// HapticService.instance.lightTap();
///
/// // Use haptic widgets
/// HapticButton(
///   onPressed: () => print('Tapped'),
///   child: Text('Click me'),
/// );
///
/// // Add haptic to existing widget
/// MyWidget().withHaptics(onTap: () => doSomething());
///
/// // With Riverpod
/// final haptics = ref.read(hapticActionsProvider);
/// haptics.success();
/// ```

library;

export 'haptic_config.dart';
export 'haptic_feedback_widget.dart';
export 'haptic_patterns.dart';
export 'haptic_provider.dart';
export 'haptic_service.dart';
