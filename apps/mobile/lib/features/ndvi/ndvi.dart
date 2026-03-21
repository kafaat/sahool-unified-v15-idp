/// SAHOOL NDVI & Spectral Index Analysis Module
///
/// تحليل مؤشرات الأقمار الصناعية الطيفية (NDVI, NDWI, EVI, SAVI, NDRE, LAI)
///
/// Features:
/// - Multi-index support (SpectralIndex enum, SpectralColormap)
/// - NDVI value classification (NdviValue, NdviHealthCategory)
/// - Professional colormaps for all indices
/// - Health indicator widgets (circular gauge, badge, legend)
/// - Multi-index map tile layer and polygon overlay
/// - Index selector and layer control widgets
/// - Time series trend analysis

library;

// Domain
export 'domain/ndvi_value.dart';
export 'domain/ndvi_colormap.dart';
export 'domain/spectral_index.dart';

// UI
export 'ui/ndvi_health_indicator.dart';
export 'ui/ndvi_tile_layer.dart';
