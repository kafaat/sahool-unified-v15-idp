import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../domain/ndvi_colormap.dart';
import '../domain/spectral_index.dart';

/// NDVI Tile Layer Configuration
/// Supports COG (Cloud Optimized GeoTIFF) and standard XYZ tiles
class NdviTileConfig {
  /// Tile URL template
  /// Use {z}, {x}, {y} for tile coordinates
  /// Use {field_id} for field-specific tiles
  final String urlTemplate;

  /// API key if required
  final String? apiKey;

  /// Additional headers
  final Map<String, String>? headers;

  /// Tile size (default 256)
  final int tileSize;

  /// Opacity (0.0 - 1.0)
  final double opacity;

  /// Min/Max zoom levels
  final int minZoom;
  final int maxZoom;

  const NdviTileConfig({
    required this.urlTemplate,
    this.apiKey,
    this.headers,
    this.tileSize = 256,
    this.opacity = 0.7,
    this.minZoom = 10,
    this.maxZoom = 18,
  });

  /// Default Sentinel Hub NDVI tiles
  static NdviTileConfig sentinelHub({required String apiKey}) {
    return NdviTileConfig(
      urlTemplate: 'https://services.sentinel-hub.com/ogc/wms/'
          '?SERVICE=WMS&VERSION=1.3.0&REQUEST=GetMap'
          '&LAYERS=NDVI&FORMAT=image/png&TRANSPARENT=true'
          '&WIDTH=256&HEIGHT=256&CRS=EPSG:4326'
          '&BBOX={bbox}',
      apiKey: apiKey,
      headers: {
        'Authorization': 'Bearer $apiKey',
      },
    );
  }

  /// Local SAHOOL backend tiles
  static NdviTileConfig sahoolBackend({required String baseUrl}) {
    return NdviTileConfig(
      urlTemplate: '$baseUrl/api/v1/ndvi/tiles/{z}/{x}/{y}.png',
    );
  }
}

/// NDVI Tile Layer Widget for FlutterMap
class NdviTileLayerWidget extends StatelessWidget {
  final NdviTileConfig config;
  final bool visible;

  const NdviTileLayerWidget({
    super.key,
    required this.config,
    this.visible = true,
  });

  @override
  Widget build(BuildContext context) {
    if (!visible) return const SizedBox.shrink();

    return AnimatedOpacity(
      opacity: config.opacity,
      duration: const Duration(milliseconds: 300),
      child: TileLayer(
        urlTemplate: config.urlTemplate,
        additionalOptions: {
          if (config.apiKey != null) 'apiKey': config.apiKey!,
        },
        tileDimension: config.tileSize,  // Updated from deprecated tileSize
        minZoom: config.minZoom.toDouble(),
        maxZoom: config.maxZoom.toDouble(),
        errorTileCallback: (tile, error, stackTrace) {
          // Silent fail for missing tiles
        },
      ),
    );
  }
}

/// NDVI Polygon Overlay - Colors field polygons based on NDVI value
class NdviPolygonLayer extends StatelessWidget {
  final List<NdviFieldData> fields;
  final bool showLabels;
  final double borderWidth;
  final void Function(String fieldId)? onTap;

  const NdviPolygonLayer({
    super.key,
    required this.fields,
    this.showLabels = true,
    this.borderWidth = 2,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        // Polygon layer
        PolygonLayer(
          polygons: fields.map<Polygon>((field) {
            final color = NdviColormap.getColor(
              field.ndviValue,
              stops: NdviColormap.yemenStops,
            );

            return Polygon(
              points: field.boundary,
              color: color.withValues(alpha: 0.4),
              borderColor: color,
              borderStrokeWidth: borderWidth,
              label: showLabels ? field.name : null,
              labelStyle: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                shadows: [
                  Shadow(
                    color: Colors.black54,
                    blurRadius: 4,
                  ),
                ],
              ),
            );
          }).toList(),
        ),

        // Tap detection layer (using sized markers at centroids)
        if (onTap != null)
          MarkerLayer(
            markers: fields.map((field) {
              final centroid = _calculateCentroid(field.boundary);
              return Marker(
                point: centroid,
                width: 80,
                height: 80,
                child: GestureDetector(
                  onTap: () => onTap!(field.id),
                  behavior: HitTestBehavior.translucent,
                  child: const SizedBox.expand(),
                ),
              );
            }).toList(),
          ),
      ],
    );
  }

  LatLng _calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return const LatLng(0, 0);
    double sumLat = 0, sumLng = 0;
    for (final p in points) {
      sumLat += p.latitude;
      sumLng += p.longitude;
    }
    return LatLng(sumLat / points.length, sumLng / points.length);
  }
}

/// Field data with NDVI value
class NdviFieldData {
  final String id;
  final String name;
  final List<LatLng> boundary;
  final double ndviValue;
  final DateTime? lastUpdated;

  const NdviFieldData({
    required this.id,
    required this.name,
    required this.boundary,
    required this.ndviValue,
    this.lastUpdated,
  });
}

/// Multi-Index Polygon Overlay - Colors field polygons based on any spectral index
class IndexPolygonLayer extends StatelessWidget {
  final List<IndexFieldData> fields;
  final SpectralIndex index;
  final bool showLabels;
  final double borderWidth;
  final void Function(String fieldId)? onTap;

  const IndexPolygonLayer({
    super.key,
    required this.fields,
    this.index = SpectralIndex.ndvi,
    this.showLabels = true,
    this.borderWidth = 2,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        PolygonLayer(
          polygons: fields.map<Polygon>((field) {
            final value = field.values[index] ?? 0.0;
            final color = SpectralColormap.getColor(index, value);

            return Polygon(
              points: field.boundary,
              color: color.withValues(alpha: 0.4),
              borderColor: color,
              borderStrokeWidth: borderWidth,
              label: showLabels
                  ? '${index.code}: ${value.toStringAsFixed(2)}'
                  : null,
              labelStyle: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                shadows: [
                  Shadow(color: Colors.black54, blurRadius: 4),
                ],
              ),
            );
          }).toList(),
        ),
        if (onTap != null)
          MarkerLayer(
            markers: fields.map((field) {
              final centroid = _calculateCentroid(field.boundary);
              return Marker(
                point: centroid,
                width: 80,
                height: 80,
                child: GestureDetector(
                  onTap: () => onTap!(field.id),
                  behavior: HitTestBehavior.translucent,
                  child: const SizedBox.expand(),
                ),
              );
            }).toList(),
          ),
      ],
    );
  }

  LatLng _calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return const LatLng(0, 0);
    double sumLat = 0, sumLng = 0;
    for (final p in points) {
      sumLat += p.latitude;
      sumLng += p.longitude;
    }
    return LatLng(sumLat / points.length, sumLng / points.length);
  }
}

/// Field data with multiple spectral index values
class IndexFieldData {
  final String id;
  final String name;
  final List<LatLng> boundary;
  final Map<SpectralIndex, double> values;
  final DateTime? lastUpdated;

  const IndexFieldData({
    required this.id,
    required this.name,
    required this.boundary,
    required this.values,
    this.lastUpdated,
  });

  /// Get value for a specific index
  double getValue(SpectralIndex index) => values[index] ?? 0.0;
}

/// Multi-Index Layer Control - supports switching between spectral indices
class IndexLayerControl extends StatelessWidget {
  final SpectralIndex selectedIndex;
  final ValueChanged<SpectralIndex> onIndexChanged;
  final bool isVisible;
  final ValueChanged<bool> onVisibilityChanged;
  final double opacity;
  final ValueChanged<double>? onOpacityChanged;

  const IndexLayerControl({
    super.key,
    required this.selectedIndex,
    required this.onIndexChanged,
    required this.isVisible,
    required this.onVisibilityChanged,
    this.opacity = 0.7,
    this.onOpacityChanged,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Toggle row
            Row(
              children: [
                Icon(
                  selectedIndex.icon,
                  color: isVisible
                      ? SpectralColormap.getColor(selectedIndex, 0.6)
                      : Colors.grey,
                  size: 20,
                ),
                const SizedBox(width: 8),
                Text(
                  isArabic
                      ? 'طبقة ${selectedIndex.code}'
                      : '${selectedIndex.code} Layer',
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                const Spacer(),
                Switch(
                  value: isVisible,
                  onChanged: onVisibilityChanged,
                  activeColor: SpectralColormap.getColor(selectedIndex, 0.6),
                ),
              ],
            ),

            // Index selector chips
            if (isVisible) ...[
              const SizedBox(height: 8),
              Wrap(
                spacing: 6,
                runSpacing: 4,
                children: SpectralIndex.values.map((idx) {
                  final isSelected = idx == selectedIndex;
                  final chipColor = SpectralColormap.getColor(idx, 0.6);
                  return ChoiceChip(
                    label: Text(
                      idx.code,
                      style: TextStyle(
                        fontSize: 11,
                        fontWeight:
                            isSelected ? FontWeight.bold : FontWeight.normal,
                        color: isSelected ? Colors.white : chipColor,
                      ),
                    ),
                    selected: isSelected,
                    selectedColor: chipColor,
                    backgroundColor: chipColor.withValues(alpha: 0.1),
                    onSelected: (_) => onIndexChanged(idx),
                    avatar: Icon(idx.icon, size: 14,
                        color: isSelected ? Colors.white : chipColor),
                    visualDensity: VisualDensity.compact,
                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                  );
                }).toList(),
              ),
            ],

            // Opacity slider
            if (isVisible && onOpacityChanged != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  Text(
                    isArabic ? 'الشفافية' : 'Opacity',
                    style: const TextStyle(fontSize: 12),
                  ),
                  Expanded(
                    child: Slider(
                      value: opacity,
                      onChanged: onOpacityChanged,
                      activeColor:
                          SpectralColormap.getColor(selectedIndex, 0.6),
                      min: 0.1,
                      max: 1.0,
                    ),
                  ),
                  Text(
                    '${(opacity * 100).toInt()}%',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ],

            // Legend
            if (isVisible) ...[
              const SizedBox(height: 8),
              Text(
                isArabic ? selectedIndex.nameAr : selectedIndex.name,
                style: const TextStyle(
                    fontSize: 11, fontWeight: FontWeight.w500),
              ),
              const SizedBox(height: 4),
              Container(
                height: 12,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(6),
                  gradient: LinearGradient(
                    colors: SpectralColormap.generateGradient(selectedIndex,
                        steps: 20),
                  ),
                ),
              ),
              const SizedBox(height: 2),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    selectedIndex.minValue.toStringAsFixed(1),
                    style: TextStyle(fontSize: 9, color: Colors.grey[600]),
                  ),
                  Text(
                    selectedIndex.maxValue.toStringAsFixed(1),
                    style: TextStyle(fontSize: 9, color: Colors.grey[600]),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}

/// NDVI Map Layer Control
class NdviLayerControl extends StatelessWidget {
  final bool isNdviVisible;
  final ValueChanged<bool> onVisibilityChanged;
  final double opacity;
  final ValueChanged<double>? onOpacityChanged;

  const NdviLayerControl({
    super.key,
    required this.isNdviVisible,
    required this.onVisibilityChanged,
    this.opacity = 0.7,
    this.onOpacityChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  Icons.grass,
                  color: isNdviVisible ? Colors.green : Colors.grey,
                  size: 20,
                ),
                const SizedBox(width: 8),
                const Text(
                  'طبقة NDVI',
                  style: TextStyle(fontWeight: FontWeight.w600),
                ),
                const Spacer(),
                Switch(
                  value: isNdviVisible,
                  onChanged: onVisibilityChanged,
                  activeColor: Colors.green,
                ),
              ],
            ),
            if (isNdviVisible && onOpacityChanged != null) ...[
              const SizedBox(height: 8),
              Row(
                children: [
                  const Text('الشفافية', style: TextStyle(fontSize: 12)),
                  Expanded(
                    child: Slider(
                      value: opacity,
                      onChanged: onOpacityChanged,
                      activeColor: Colors.green,
                      min: 0.1,
                      max: 1.0,
                    ),
                  ),
                  Text(
                    '${(opacity * 100).toInt()}%',
                    style: const TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }
}
