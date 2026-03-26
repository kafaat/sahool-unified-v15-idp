/// SAHOOL Satellite Feature
/// ميزة الأقمار الصناعية في سهول
///
/// Satellite imagery, NDVI, phenology, and weather analysis
/// صور الأقمار الصناعية، NDVI، الفينولوجيا، وتحليل الطقس
library;

// Data - Models
export 'data/models/field_health.dart';
export 'data/models/ndvi_data.dart';
export 'data/models/phenology_data.dart';
export 'data/models/weather_data.dart';

// Data
export 'data/remote/satellite_api.dart';
export 'data/repositories/satellite_repository.dart';

// Presentation
export 'presentation/providers/satellite_provider.dart';
export 'presentation/screens/ndvi_detail_screen.dart';
export 'presentation/screens/phenology_screen.dart';
export 'presentation/screens/satellite_dashboard_screen.dart';
export 'presentation/screens/satellite_history_screen.dart';
export 'presentation/screens/weather_screen.dart';

// Widgets
export 'widgets/health_indicator.dart';
export 'widgets/ndvi_chart.dart';
export 'widgets/phenology_timeline.dart';
export 'widgets/satellite_map_overlay.dart';
export 'widgets/weather_card.dart';
