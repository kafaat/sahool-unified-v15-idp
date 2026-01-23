/// Crop Rotation Feature Entry Point
///
/// This file provides the main entry points for the Crop Rotation feature.
/// The rotation feature helps farmers plan optimal crop rotations to:
/// - Improve soil health
/// - Break pest and disease cycles
/// - Optimize nutrient utilization
/// - Maximize yields
///
/// Usage Example:
/// ```dart
/// // Navigate to rotation plan screen
/// Navigator.push(
///   context,
///   MaterialPageRoute(
///     builder: (context) => RotationPlanScreen(fieldId: 'field_123'),
///   ),
/// );
///
/// // Navigate to compatibility matrix
/// Navigator.push(
///   context,
///   MaterialPageRoute(
///     builder: (context) => CropCompatibilityScreen(),
///   ),
/// );
/// ```

export 'models/rotation_models.dart';
export 'services/rotation_service.dart';
export 'providers/rotation_provider.dart';
export 'screens/rotation_plan_screen.dart';
export 'screens/rotation_calendar_screen.dart';
export 'screens/crop_compatibility_screen.dart';
export 'widgets/rotation_timeline_widget.dart';
export 'widgets/soil_health_chart.dart';
