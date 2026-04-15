/// Pivot Irrigation Feature - Valley Style
/// ميزة الري المحوري - بأسلوب فالي
///
/// This module provides comprehensive center pivot irrigation management
/// similar to Valley Irrigation systems, including:
/// - Pivot visualization with sectors and VRI zones
/// - Control panel for pivot operation
/// - Sector management and configuration
/// - Sector drawing tool for custom sector shapes
/// - VRI zone grid editor at span/tower level
/// - Real-time status monitoring
/// - Scheduling and automation
/// - Performance statistics
///
/// Usage:
/// ```dart
/// import 'package:sahool_mobile_core/features/pivot_irrigation/pivot_irrigation.dart';
///
/// // Navigate to pivot dashboard
/// Navigator.push(
///   context,
///   MaterialPageRoute(
///     builder: (context) => PivotDashboardScreen(
///       pivotId: 'pivot_001',
///       fieldId: 'field_001',
///     ),
///   ),
/// );
///
/// // Setup new pivot with sector drawing
/// Navigator.push(
///   context,
///   MaterialPageRoute(
///     builder: (context) => PivotSetupScreen(
///       fieldId: 'field_001',
///       onSave: (config) => print('Saved: ${config.name}'),
///     ),
///   ),
/// );
/// ```
library;

// Domain Models
export 'domain/models/pivot_models.dart';
export 'domain/models/span_zone_models.dart';

// Presentation Widgets
export 'presentation/widgets/pivot_visualization.dart';
export 'presentation/widgets/pivot_control_panel.dart';
export 'presentation/widgets/sector_drawing_tool.dart';
export 'presentation/widgets/vri_zone_grid_editor.dart';

// Presentation Screens
export 'presentation/screens/pivot_dashboard_screen.dart';
export 'presentation/screens/sector_management_screen.dart';
export 'presentation/screens/pivot_setup_screen.dart';
