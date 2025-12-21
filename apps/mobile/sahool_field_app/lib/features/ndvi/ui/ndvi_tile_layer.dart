import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../domain/ndvi_colormap.dart';

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

    return Opacity(
      opacity: config.opacity,
      child: TileLayer(
        urlTemplate: config.urlTemplate,
        additionalOptions: {
          if (config.apiKey != null) 'apiKey': config.apiKey!,
        },
        tileSize: config.tileSize.toDouble(),
        minZoom: config.minZoom.toDouble(),
        maxZoom: config.maxZoom.toDouble(),
        backgroundColor: Colors.transparent,
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
          polygons: fields.map((field) {
            final color = NdviColormap.getColor(
              field.ndviValue,
              stops: NdviColormap.yemenStops,
            );

            return Polygon(
              points: field.boundary,
              color: color.withOpacity(0.4),
              borderColor: color,
              borderStrokeWidth: borderWidth,
              isFilled: true,
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

        // Tap detection layer (using markers at centroids)
        if (onTap != null)
          MarkerLayer(
            markers: fields.map((field) {
              final centroid = _calculateCentroid(field.boundary);
              return Marker(
                point: centroid,
                width: 1,
                height: 1,
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
