/// SAHOOL Crop Health Feature
/// ميزة صحة المحاصيل في سهول
///
/// Crop health diagnosis and monitoring dashboard
/// تشخيص ومراقبة صحة المحاصيل
library;

// Data
export 'data/models/diagnosis_models.dart';
export 'data/remote/crop_health_api.dart';
export 'data/repositories/crop_health_repository.dart';

// Domain
export 'domain/entities/crop_health_entities.dart';

// Presentation - Providers
export 'presentation/providers/crop_health_provider.dart';
export 'presentation/providers/crop_health_providers.dart';

// Presentation - Screens
export 'presentation/screens/crop_health_dashboard.dart';
export 'presentation/screens/zone_timeline_screen.dart';

// Presentation - Widgets
export 'presentation/widgets/action_list_tile.dart';
export 'presentation/widgets/diagnosis_summary_card.dart';
export 'presentation/widgets/health_chart_widget.dart';
export 'presentation/widgets/zone_selector.dart';
