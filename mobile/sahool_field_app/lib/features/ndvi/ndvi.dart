/// SAHOOL NDVI Analysis Module
///
/// تحليل مؤشر صحة النباتات (NDVI)
///
/// Features:
/// - NDVI value classification (NdviValue, NdviHealthCategory)
/// - Professional colormap (NdviColormap) for visualization
/// - Health indicator widgets (circular gauge, badge, legend)
/// - Map tile layer integration
/// - Time series trend analysis

library ndvi;

// Domain
export 'domain/ndvi_value.dart';
export 'domain/ndvi_colormap.dart';

// UI
export 'ui/ndvi_health_indicator.dart';
export 'ui/ndvi_tile_layer.dart';
