/// SAHOOL Equipment Feature
/// ميزة المعدات في سهول
///
/// Equipment tracking, maintenance, and fuel logging
/// تتبع المعدات والصيانة وتسجيل الوقود
library;

// Data
export 'data/equipment_api.dart';
export 'data/equipment_local_db.dart';
export 'data/equipment_models.dart';
export 'data/equipment_repository.dart';

// Domain
export 'domain/models/equipment.dart';
export 'domain/models/equipment_status.dart';
export 'domain/models/fuel_log.dart';
export 'domain/models/maintenance_record.dart';
export 'domain/models/usage_log.dart';

// Presentation - Screens
export 'presentation/screens/equipment_details_screen.dart';
export 'presentation/screens/fuel_log_screen.dart';
export 'presentation/screens/schedule_maintenance_screen.dart';

// Presentation - Widgets
export 'presentation/widgets/equipment_card.dart';
export 'presentation/widgets/fuel_gauge.dart';
export 'presentation/widgets/maintenance_timeline.dart';
export 'presentation/widgets/qr_scanner_widget.dart';
export 'presentation/widgets/status_indicator.dart';
export 'presentation/widgets/usage_chart.dart';

// Providers
export 'providers/equipment_providers.dart';
export 'state/equipment_providers.dart';

// UI
export 'ui/equipment_location_map_screen.dart';
export 'ui/equipment_screen.dart';
