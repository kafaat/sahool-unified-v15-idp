/// SAHOOL Field Feature
/// ميزة الحقل في سهول
///
/// Field management, health monitoring, and zone visualization
/// إدارة الحقول ومراقبة الصحة وعرض المناطق
library;

// Data
export 'data/remote/fields_api.dart';
export 'data/repo/fields_repo.dart';

// Domain
export 'domain/entities/field.dart';

// Presentation - Widgets
export 'presentation/widgets/field_health_widget.dart';
export 'presentation/widgets/zones_map_layer.dart';

// UI
export 'ui/field_details_screen.dart';
export 'ui/field_form_screen.dart';
export 'ui/logic/drawing_provider.dart';
export 'ui/scouting_screen.dart';
export 'ui/widgets/drawing_controls.dart';
