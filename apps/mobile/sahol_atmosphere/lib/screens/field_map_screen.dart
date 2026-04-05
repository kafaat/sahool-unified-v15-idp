// ═══════════════════════════════════════════════════════════════════════════════════════
// SAHOOL ATMOSPHERE - Field Map Screen
// شاشة خريطة الحقول
// ═══════════════════════════════════════════════════════════════════════════════════════
//
// Features:
// - Interactive field map with flutter_map
// - NDVI-based field coloring
// - Glassmorphism UI overlays
// - Field selection with details panel
//
// ═══════════════════════════════════════════════════════════════════════════════════════

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../theme/atmosphere_theme.dart';
import '../models/field_model.dart';

/// Field Map Screen
/// شاشة خريطة الحقول
class FieldMapScreen extends StatefulWidget {
  const FieldMapScreen({super.key});

  @override
  State<FieldMapScreen> createState() => _FieldMapScreenState();
}

class _FieldMapScreenState extends State<FieldMapScreen> {
  final MapController _mapController = MapController();

  /// Currently selected field
  FieldModel? _selectedField;

  /// Map layer type
  bool _showSatellite = true;

  /// Show NDVI overlay
  bool _showNdviLayer = true;

  /// Yemen map center (Sanaa area)
  static const LatLng _yemenCenter = LatLng(15.3694, 44.1910);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AtmosphereColors.bgGradient,
        ),
        child: SafeArea(
          child: Stack(
            children: [
              // Map
              _buildMap(),

              // Top Bar
              _buildTopBar(),

              // Layer Controls
              Positioned(
                top: 80,
                right: AtmosphereSpacing.md,
                child: _buildLayerControls(),
              ),

              // Selected Field Panel
              if (_selectedField != null)
                Positioned(
                  bottom: 0,
                  left: 0,
                  right: 0,
                  child: _buildFieldPanel(_selectedField!),
                ),

              // Legend
              if (_showNdviLayer)
                Positioned(
                  bottom: _selectedField != null ? 220 : AtmosphereSpacing.xl,
                  left: AtmosphereSpacing.md,
                  child: _buildLegend(),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMap() {
    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: _yemenCenter,
        initialZoom: 14.0,
        minZoom: 10.0,
        maxZoom: 18.0,
        onTap: (tapPosition, point) {
          // Deselect field when tapping on map
          if (_selectedField != null) {
            setState(() => _selectedField = null);
            HapticFeedback.lightImpact();
          }
        },
      ),
      children: [
        // Base Tile Layer
        TileLayer(
          urlTemplate: _showSatellite
              ? 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
              : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'app.sahool.atmosphere',
          maxZoom: 18,
        ),

        // Field Polygons Layer
        PolygonLayer(
          polygons: SampleFields.all.map((field) {
            final isSelected = _selectedField?.id == field.id;
            final color = _getFieldColor(field);

            return Polygon(
              points: field.boundary,
              color: color.withOpacity(_showNdviLayer ? 0.6 : 0.3),
              borderColor: isSelected ? Colors.white : color,
              borderStrokeWidth: isSelected ? 3.0 : 1.5,
            );
          }).toList(),
        ),

        // Field Markers Layer
        MarkerLayer(
          markers: SampleFields.all
              .map((field) {
                if (field.center == null) return null;
                return Marker(
                  point: field.center!,
                  width: 80,
                  height: 40,
                  child: GestureDetector(
                    onTap: () {
                      setState(() => _selectedField = field);
                      HapticFeedback.mediumImpact();
                    },
                    child: _buildFieldMarker(field),
                  ),
                );
              })
              .whereType<Marker>()
              .toList(),
        ),
      ],
    );
  }

  Widget _buildFieldMarker(FieldModel field) {
    final color = _getFieldColor(field);
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: AtmosphereSpacing.sm,
        vertical: AtmosphereSpacing.xs,
      ),
      decoration: BoxDecoration(
        color: AtmosphereColors.bgSecondary.withOpacity(0.9),
        borderRadius: BorderRadius.circular(AtmosphereRadius.sm),
        border: Border.all(color: color, width: 1.5),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.3),
            blurRadius: 8,
          ),
        ],
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            field.cropType.emoji,
            style: const TextStyle(fontSize: 14),
          ),
          const SizedBox(width: 4),
          Flexible(
            child: Text(
              field.areaFormatted,
              style: AtmosphereTypography.labelSmall.copyWith(
                color: Colors.white,
                fontSize: 10,
              ),
              overflow: TextOverflow.ellipsis,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTopBar() {
    return Container(
      margin: const EdgeInsets.all(AtmosphereSpacing.md),
      padding: const EdgeInsets.symmetric(
        horizontal: AtmosphereSpacing.md,
        vertical: AtmosphereSpacing.sm,
      ),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: BorderRadius.circular(AtmosphereRadius.lg),
        border: Border.all(
          color: AtmosphereColors.glassBorder,
        ),
      ),
      child: Row(
        children: [
          IconButton(
            icon: const Icon(Icons.arrow_back),
            color: AtmosphereColors.textPrimary,
            onPressed: () {
              HapticFeedback.lightImpact();
              Navigator.of(context).pop();
            },
          ),
          const Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  'خريطة الحقول',
                  style: AtmosphereTypography.headlineMedium,
                ),
                Text(
                  'FIELD MAP',
                  style: AtmosphereTypography.labelSmall,
                ),
              ],
            ),
          ),
          IconButton(
            icon: const Icon(Icons.my_location),
            color: AtmosphereColors.success,
            onPressed: () {
              HapticFeedback.lightImpact();
              _mapController.move(_yemenCenter, 14.0);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildLayerControls() {
    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.sm),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: BorderRadius.circular(AtmosphereRadius.md),
        border: Border.all(
          color: AtmosphereColors.glassBorder,
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Satellite toggle
          _buildLayerButton(
            icon: Icons.satellite_alt,
            isActive: _showSatellite,
            tooltip: 'قمر صناعي',
            onTap: () {
              setState(() => _showSatellite = !_showSatellite);
              HapticFeedback.lightImpact();
            },
          ),
          const SizedBox(height: AtmosphereSpacing.sm),

          // NDVI toggle
          _buildLayerButton(
            icon: Icons.eco,
            isActive: _showNdviLayer,
            tooltip: 'NDVI',
            onTap: () {
              setState(() => _showNdviLayer = !_showNdviLayer);
              HapticFeedback.lightImpact();
            },
          ),
          const SizedBox(height: AtmosphereSpacing.sm),

          // Zoom in
          _buildLayerButton(
            icon: Icons.add,
            isActive: false,
            tooltip: 'تكبير',
            onTap: () {
              _mapController.move(
                _mapController.camera.center,
                _mapController.camera.zoom + 1,
              );
              HapticFeedback.lightImpact();
            },
          ),
          const SizedBox(height: AtmosphereSpacing.sm),

          // Zoom out
          _buildLayerButton(
            icon: Icons.remove,
            isActive: false,
            tooltip: 'تصغير',
            onTap: () {
              _mapController.move(
                _mapController.camera.center,
                _mapController.camera.zoom - 1,
              );
              HapticFeedback.lightImpact();
            },
          ),
        ],
      ),
    );
  }

  Widget _buildLayerButton({
    required IconData icon,
    required bool isActive,
    required String tooltip,
    required VoidCallback onTap,
  }) {
    return Tooltip(
      message: tooltip,
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: isActive
                ? AtmosphereColors.success.withOpacity(0.2)
                : Colors.transparent,
            borderRadius: BorderRadius.circular(AtmosphereRadius.sm),
            border: Border.all(
              color: isActive
                  ? AtmosphereColors.success
                  : AtmosphereColors.glassBorder,
            ),
          ),
          child: Icon(
            icon,
            color: isActive
                ? AtmosphereColors.success
                : AtmosphereColors.textSecondary,
            size: 20,
          ),
        ),
      ),
    );
  }

  Widget _buildFieldPanel(FieldModel field) {
    final color = _getFieldColor(field);

    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.lg),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(AtmosphereRadius.xl),
          topRight: Radius.circular(AtmosphereRadius.xl),
        ),
        border: Border.all(
          color: color.withOpacity(0.3),
        ),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.2),
            blurRadius: 20,
            offset: const Offset(0, -4),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Handle bar
          Container(
            width: 40,
            height: 4,
            margin: const EdgeInsets.only(bottom: AtmosphereSpacing.md),
            decoration: BoxDecoration(
              color: AtmosphereColors.textMuted,
              borderRadius: BorderRadius.circular(2),
            ),
          ),

          // Header
          Row(
            children: [
              Text(
                field.cropType.emoji,
                style: const TextStyle(fontSize: 32),
              ),
              const SizedBox(width: AtmosphereSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      field.nameAr,
                      style: AtmosphereTypography.headlineLarge,
                    ),
                    Text(
                      field.nameEn.toUpperCase(),
                      style: AtmosphereTypography.labelSmall,
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: AtmosphereSpacing.md,
                  vertical: AtmosphereSpacing.sm,
                ),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(AtmosphereRadius.full),
                  border: Border.all(color: color.withOpacity(0.5)),
                ),
                child: Text(
                  '${field.healthPercent}%',
                  style: AtmosphereTypography.headlineMedium.copyWith(
                    color: color,
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: AtmosphereSpacing.lg),

          // Stats Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem(
                icon: Icons.straighten,
                value: field.areaFormatted,
                label: 'المساحة',
              ),
              _buildStatItem(
                icon: Icons.water_drop,
                value: '${field.moisturePercent}%',
                label: 'الرطوبة',
                color: _getMoistureColor(field.moisturePercent),
              ),
              _buildStatItem(
                icon: Icons.thermostat,
                value: '${field.temperatureCelsius}°C',
                label: 'الحرارة',
                color: _getTemperatureColor(field.temperatureCelsius),
              ),
              _buildStatItem(
                icon: Icons.wb_sunny,
                value: '${field.sunlightPercent}%',
                label: 'الإضاءة',
                color: AtmosphereColors.warning,
              ),
            ],
          ),

          const SizedBox(height: AtmosphereSpacing.lg),

          // Action Button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton(
              onPressed: () {
                HapticFeedback.mediumImpact();
                // TODO(P1): Navigate to field details screen with field data
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تفاصيل الحقل قيد التطوير | Field details coming soon'),
                    duration: Duration(seconds: 2),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: color.withOpacity(0.2),
                foregroundColor: color,
                padding: const EdgeInsets.all(AtmosphereSpacing.md),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(AtmosphereRadius.md),
                  side: BorderSide(color: color.withOpacity(0.5)),
                ),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.open_in_new, size: 18),
                  const SizedBox(width: AtmosphereSpacing.sm),
                  Text(
                    'فتح التفاصيل',
                    style: AtmosphereTypography.labelLarge.copyWith(
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String value,
    required String label,
    Color? color,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: color ?? AtmosphereColors.textSecondary,
          size: 24,
        ),
        const SizedBox(height: AtmosphereSpacing.xs),
        Text(
          value,
          style: AtmosphereTypography.headlineSmall.copyWith(
            color: color ?? AtmosphereColors.textPrimary,
          ),
        ),
        const SizedBox(height: 2),
        Text(
          label,
          style: AtmosphereTypography.bodySmall,
        ),
      ],
    );
  }

  Widget _buildLegend() {
    return Container(
      padding: const EdgeInsets.all(AtmosphereSpacing.sm),
      decoration: BoxDecoration(
        gradient: AtmosphereColors.glassGradient,
        borderRadius: BorderRadius.circular(AtmosphereRadius.md),
        border: Border.all(
          color: AtmosphereColors.glassBorder,
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'NDVI',
            style: AtmosphereTypography.labelSmall.copyWith(
              color: AtmosphereColors.success,
            ),
          ),
          const SizedBox(height: AtmosphereSpacing.sm),
          _buildLegendItem(AtmosphereColors.success, 'صحي (>0.6)'),
          _buildLegendItem(AtmosphereColors.warning, 'متوسط (0.4-0.6)'),
          _buildLegendItem(AtmosphereColors.alert, 'حرج (<0.4)'),
        ],
      ),
    );
  }

  Widget _buildLegendItem(Color color, String label) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 16,
            height: 16,
            decoration: BoxDecoration(
              color: color.withOpacity(0.6),
              borderRadius: BorderRadius.circular(4),
              border: Border.all(color: color),
            ),
          ),
          const SizedBox(width: AtmosphereSpacing.sm),
          Text(
            label,
            style: AtmosphereTypography.bodySmall.copyWith(fontSize: 11),
          ),
        ],
      ),
    );
  }

  /// Get field color based on NDVI
  Color _getFieldColor(FieldModel field) {
    switch (field.healthStatus) {
      case FieldHealthStatus.healthy:
        return AtmosphereColors.success;
      case FieldHealthStatus.stressed:
        return AtmosphereColors.warning;
      case FieldHealthStatus.critical:
        return AtmosphereColors.alert;
      case FieldHealthStatus.unknown:
        return AtmosphereColors.textMuted;
    }
  }

  Color _getMoistureColor(int moisture) {
    if (moisture > 60) return AtmosphereColors.info;
    if (moisture > 40) return AtmosphereColors.success;
    if (moisture > 25) return AtmosphereColors.warning;
    return AtmosphereColors.alert;
  }

  Color _getTemperatureColor(int temp) {
    if (temp > 35) return AtmosphereColors.alert;
    if (temp > 30) return AtmosphereColors.warning;
    if (temp > 20) return AtmosphereColors.success;
    return AtmosphereColors.info;
  }
}
