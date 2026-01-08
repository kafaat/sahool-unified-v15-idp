/// Health Zones Map Layer Widget
/// طبقة خريطة مناطق الصحة النباتية
///
/// Displays field zones as colored polygons on a map based on health status (NDVI)
/// Features:
/// - Color-coded zones: Green (>0.6), Yellow (0.4-0.6), Red (<0.4)
/// - Zone labels with NDVI values
/// - Tap to show zone details popup
/// - Zone selection with animation
/// - Bilingual support (Arabic/English)

library;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';

/// Zone health data model
class ZoneHealth {
  final String id;
  final String name;
  final String nameAr;
  final double ndvi;
  final double areaHectares;
  final List<LatLng> boundary;
  final String? trend; // 'up', 'down', 'stable'
  final List<String>? recommendations;
  final List<String>? recommendationsAr;
  final DateTime? lastUpdated;

  const ZoneHealth({
    required this.id,
    required this.name,
    required this.nameAr,
    required this.ndvi,
    required this.areaHectares,
    required this.boundary,
    this.trend,
    this.recommendations,
    this.recommendationsAr,
    this.lastUpdated,
  });

  /// Get health status based on NDVI
  HealthStatus get healthStatus {
    if (ndvi > 0.6) return HealthStatus.healthy;
    if (ndvi >= 0.4) return HealthStatus.moderate;
    return HealthStatus.critical;
  }

  /// Get display name based on locale
  String getDisplayName(bool isArabic) => isArabic ? nameAr : name;

  /// Get recommendations based on locale
  List<String> getRecommendations(bool isArabic) {
    if (isArabic && recommendationsAr != null) return recommendationsAr!;
    return recommendations ?? [];
  }
}

/// Health status enum
enum HealthStatus {
  healthy,
  moderate,
  critical,
}

/// Zones Map Layer Widget
class ZonesMapLayer extends StatefulWidget {
  /// List of zones to display
  final List<ZoneHealth> zones;

  /// Currently selected zone
  final ZoneHealth? selectedZone;

  /// Callback when zone is tapped
  final void Function(ZoneHealth zone)? onZoneTapped;

  /// Map controller (optional, for external map control)
  final MapController? mapController;

  /// Initial map center
  final LatLng? initialCenter;

  /// Initial zoom level
  final double initialZoom;

  /// Show zone labels
  final bool showLabels;

  /// Show loading state
  final bool isLoading;

  /// Enable zone selection
  final bool enableSelection;

  const ZonesMapLayer({
    super.key,
    required this.zones,
    this.selectedZone,
    this.onZoneTapped,
    this.mapController,
    this.initialCenter,
    this.initialZoom = 14.0,
    this.showLabels = true,
    this.isLoading = false,
    this.enableSelection = true,
  });

  @override
  State<ZonesMapLayer> createState() => _ZonesMapLayerState();
}

class _ZonesMapLayerState extends State<ZonesMapLayer>
    with SingleTickerProviderStateMixin {
  late MapController _mapController;
  ZoneHealth? _hoveredZone;
  late AnimationController _animationController;
  late Animation<double> _pulseAnimation;

  @override
  void initState() {
    super.initState();
    _mapController = widget.mapController ?? MapController();

    // Animation for selected zone pulse effect
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _pulseAnimation = Tween<double>(begin: 1.0, end: 1.2).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeInOut),
    );

    // Fit bounds after first frame
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _fitBounds();
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    if (widget.mapController == null) {
      _mapController.dispose();
    }
    super.dispose();
  }

  @override
  void didUpdateWidget(ZonesMapLayer oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.zones != widget.zones) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        _fitBounds();
      });
    }
  }

  /// Fit map to show all zones
  void _fitBounds() {
    if (widget.zones.isEmpty) return;

    double minLat = double.infinity;
    double maxLat = -double.infinity;
    double minLng = double.infinity;
    double maxLng = -double.infinity;

    for (final zone in widget.zones) {
      for (final point in zone.boundary) {
        if (point.latitude < minLat) minLat = point.latitude;
        if (point.latitude > maxLat) maxLat = point.latitude;
        if (point.longitude < minLng) minLng = point.longitude;
        if (point.longitude > maxLng) maxLng = point.longitude;
      }
    }

    if (minLat != double.infinity && maxLat != -double.infinity) {
      final bounds = LatLngBounds(
        LatLng(minLat, minLng),
        LatLng(maxLat, maxLng),
      );

      _mapController.fitCamera(
        CameraFit.bounds(
          bounds: bounds,
          padding: const EdgeInsets.all(50),
        ),
      );
    }
  }

  /// Get color based on health status
  Color _getHealthColor(HealthStatus status, {bool isSelected = false}) {
    final baseColor = switch (status) {
      HealthStatus.healthy => SahoolColors.sageGreen,
      HealthStatus.moderate => SahoolColors.harvestGold,
      HealthStatus.critical => SahoolColors.danger,
    };

    return isSelected ? baseColor : baseColor.withOpacity(0.7);
  }

  /// Get health status label in Arabic
  String _getHealthStatusLabel(HealthStatus status, bool isArabic) {
    if (isArabic) {
      return switch (status) {
        HealthStatus.healthy => 'صحي',
        HealthStatus.moderate => 'متوسط',
        HealthStatus.critical => 'حرج',
      };
    } else {
      return switch (status) {
        HealthStatus.healthy => 'Healthy',
        HealthStatus.moderate => 'Moderate',
        HealthStatus.critical => 'Critical',
      };
    }
  }

  /// Calculate centroid of a polygon
  LatLng _calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return const LatLng(0, 0);

    double sumLat = 0;
    double sumLng = 0;

    for (final point in points) {
      sumLat += point.latitude;
      sumLng += point.longitude;
    }

    return LatLng(
      sumLat / points.length,
      sumLng / points.length,
    );
  }

  /// Show zone details popup
  void _showZoneDetails(BuildContext context, ZoneHealth zone) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => _ZoneDetailsPopup(
        zone: zone,
        isArabic: isArabic,
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    // Loading state
    if (widget.isLoading) {
      return Container(
        decoration: BoxDecoration(
          color: SahoolColors.paleOlive,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const CircularProgressIndicator(
                color: SahoolColors.forestGreen,
              ),
              const SizedBox(height: 16),
              Text(
                isArabic ? 'جاري تحميل المناطق...' : 'Loading zones...',
                style: const TextStyle(color: SahoolColors.forestGreen),
              ),
            ],
          ),
        ),
      );
    }

    // Empty state
    if (widget.zones.isEmpty) {
      return Container(
        decoration: BoxDecoration(
          color: SahoolColors.paleOlive,
          borderRadius: BorderRadius.circular(20),
        ),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.layers_outlined,
                size: 64,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 16),
              Text(
                isArabic ? 'لا توجد مناطق لعرضها' : 'No zones to display',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                isArabic
                    ? 'قم بإنشاء مناطق للحقل أولاً'
                    : 'Create zones for the field first',
                style: TextStyle(
                  color: Colors.grey[500],
                  fontSize: 12,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ClipRRect(
      borderRadius: BorderRadius.circular(20),
      child: Stack(
        children: [
          // Map
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: widget.initialCenter ??
                  _calculateCentroid(widget.zones.first.boundary),
              initialZoom: widget.initialZoom,
              interactionOptions: const InteractionOptions(
                flags: InteractiveFlag.all & ~InteractiveFlag.rotate,
              ),
            ),
            children: [
              // Base tile layer
              TileLayer(
                urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.sahool.unified',
              ),

              // Zones polygon layer
              PolygonLayer(
                polygons: widget.zones.map((zone) {
                  final isSelected =
                      widget.enableSelection && widget.selectedZone?.id == zone.id;
                  final color = _getHealthColor(
                    zone.healthStatus,
                    isSelected: isSelected,
                  );

                  return Polygon(
                    points: zone.boundary,
                    color: color.withOpacity(isSelected ? 0.5 : 0.3),
                    borderColor: color,
                    borderStrokeWidth: isSelected ? 3 : 2,
                    isFilled: true,
                  );
                }).toList(),
              ),

              // Zone labels layer
              if (widget.showLabels)
                MarkerLayer(
                  markers: widget.zones.map((zone) {
                    final center = _calculateCentroid(zone.boundary);
                    final isSelected = widget.enableSelection &&
                        widget.selectedZone?.id == zone.id;

                    return Marker(
                      point: center,
                      width: 120,
                      height: 60,
                      child: GestureDetector(
                        onTap: widget.enableSelection
                            ? () {
                                if (widget.onZoneTapped != null) {
                                  widget.onZoneTapped!(zone);
                                }
                                _showZoneDetails(context, zone);
                              }
                            : null,
                        child: AnimatedBuilder(
                          animation: _pulseAnimation,
                          builder: (context, child) {
                            final scale =
                                isSelected ? _pulseAnimation.value : 1.0;
                            return Transform.scale(
                              scale: scale,
                              child: child,
                            );
                          },
                          child: Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 12,
                              vertical: 8,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.95),
                              borderRadius: BorderRadius.circular(12),
                              border: Border.all(
                                color: _getHealthColor(zone.healthStatus),
                                width: isSelected ? 2.5 : 1.5,
                              ),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.15),
                                  blurRadius: 8,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Text(
                                  zone.getDisplayName(isArabic),
                                  style: const TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: SahoolColors.forestGreen,
                                  ),
                                  textAlign: TextAlign.center,
                                  maxLines: 1,
                                  overflow: TextOverflow.ellipsis,
                                ),
                                const SizedBox(height: 2),
                                Text(
                                  'NDVI: ${zone.ndvi.toStringAsFixed(2)}',
                                  style: TextStyle(
                                    fontSize: 10,
                                    fontWeight: FontWeight.w600,
                                    color: _getHealthColor(zone.healthStatus),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
            ],
          ),

          // Legend
          Positioned(
            top: 16,
            left: isArabic ? null : 16,
            right: isArabic ? 16 : null,
            child: _ZoneLegend(isArabic: isArabic),
          ),

          // Zoom controls
          Positioned(
            bottom: 16,
            left: isArabic ? null : 16,
            right: isArabic ? 16 : null,
            child: _ZoomControls(mapController: _mapController),
          ),
        ],
      ),
    );
  }
}

/// Zone details popup
class _ZoneDetailsPopup extends StatelessWidget {
  final ZoneHealth zone;
  final bool isArabic;

  const _ZoneDetailsPopup({
    required this.zone,
    required this.isArabic,
  });

  IconData _getTrendIcon(String? trend) {
    return switch (trend) {
      'up' => Icons.trending_up,
      'down' => Icons.trending_down,
      _ => Icons.trending_flat,
    };
  }

  Color _getTrendColor(String? trend) {
    return switch (trend) {
      'up' => SahoolColors.sageGreen,
      'down' => SahoolColors.danger,
      _ => Colors.grey,
    };
  }

  String _getTrendLabel(String? trend, bool isArabic) {
    if (isArabic) {
      return switch (trend) {
        'up' => 'تحسن',
        'down' => 'تراجع',
        _ => 'مستقر',
      };
    } else {
      return switch (trend) {
        'up' => 'Improving',
        'down' => 'Declining',
        _ => 'Stable',
      };
    }
  }

  @override
  Widget build(BuildContext context) {
    final statusLabel = switch (zone.healthStatus) {
      HealthStatus.healthy => isArabic ? 'صحي' : 'Healthy',
      HealthStatus.moderate => isArabic ? 'متوسط' : 'Moderate',
      HealthStatus.critical => isArabic ? 'حرج' : 'Critical',
    };

    final statusColor = switch (zone.healthStatus) {
      HealthStatus.healthy => SahoolColors.sageGreen,
      HealthStatus.moderate => SahoolColors.harvestGold,
      HealthStatus.critical => SahoolColors.danger,
    };

    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(28),
      ),
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with status badge
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        zone.getDisplayName(isArabic),
                        style: const TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: SahoolColors.forestGreen,
                        ),
                      ),
                      const SizedBox(height: 4),
                      StatusBadge(
                        label: statusLabel,
                        color: statusColor,
                        icon: Icons.circle,
                      ),
                    ],
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: () => Navigator.pop(context),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Metrics grid
            Row(
              children: [
                Expanded(
                  child: _MetricBox(
                    icon: Icons.grass,
                    label: 'NDVI',
                    value: zone.ndvi.toStringAsFixed(2),
                    color: statusColor,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _MetricBox(
                    icon: Icons.aspect_ratio,
                    label: isArabic ? 'المساحة' : 'Area',
                    value:
                        '${zone.areaHectares.toStringAsFixed(1)} ${isArabic ? 'هكتار' : 'ha'}',
                    color: SahoolColors.forestGreen,
                  ),
                ),
              ],
            ),

            if (zone.trend != null) ...[
              const SizedBox(height: 12),
              _MetricBox(
                icon: _getTrendIcon(zone.trend),
                label: isArabic ? 'الاتجاه' : 'Trend',
                value: _getTrendLabel(zone.trend, isArabic),
                color: _getTrendColor(zone.trend),
                fullWidth: true,
              ),
            ],

            const SizedBox(height: 24),
            const Divider(),
            const SizedBox(height: 16),

            // Recommendations
            Text(
              isArabic ? 'التوصيات' : 'Recommendations',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
                color: SahoolColors.forestGreen,
              ),
            ),
            const SizedBox(height: 12),

            ...zone.getRecommendations(isArabic).isNotEmpty
                ? zone.getRecommendations(isArabic).map((rec) => Padding(
                      padding: const EdgeInsets.only(bottom: 8),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Icon(
                            Icons.check_circle,
                            color: SahoolColors.sageGreen,
                            size: 20,
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Text(
                              rec,
                              style: const TextStyle(fontSize: 14),
                            ),
                          ),
                        ],
                      ),
                    ))
                : [
                    Center(
                      child: Text(
                        isArabic
                            ? 'لا توجد توصيات حالياً'
                            : 'No recommendations available',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],

            if (zone.lastUpdated != null) ...[
              const SizedBox(height: 16),
              Center(
                child: Text(
                  isArabic
                      ? 'آخر تحديث: ${_formatDate(zone.lastUpdated!, isArabic)}'
                      : 'Last updated: ${_formatDate(zone.lastUpdated!, isArabic)}',
                  style: TextStyle(
                    color: Colors.grey[500],
                    fontSize: 12,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  String _formatDate(DateTime date, bool isArabic) {
    final now = DateTime.now();
    final diff = now.difference(date);

    if (diff.inDays == 0) {
      return isArabic ? 'اليوم' : 'Today';
    } else if (diff.inDays == 1) {
      return isArabic ? 'أمس' : 'Yesterday';
    } else if (diff.inDays < 7) {
      return isArabic ? 'منذ ${diff.inDays} أيام' : '${diff.inDays} days ago';
    } else {
      return '${date.day}/${date.month}/${date.year}';
    }
  }
}

/// Metric display box
class _MetricBox extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final bool fullWidth;

  const _MetricBox({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    this.fullWidth = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: fullWidth ? double.infinity : null,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment:
            fullWidth ? CrossAxisAlignment.center : CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
            ),
          ),
        ],
      ),
    );
  }
}

/// Zone legend widget
class _ZoneLegend extends StatelessWidget {
  final bool isArabic;

  const _ZoneLegend({required this.isArabic});

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      padding: const EdgeInsets.all(12),
      borderRadius: 16,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'الحالة الصحية' : 'Health Status',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: SahoolColors.forestGreen,
            ),
          ),
          const SizedBox(height: 8),
          _LegendItem(
            color: SahoolColors.sageGreen,
            label: isArabic ? 'صحي (>0.6)' : 'Healthy (>0.6)',
          ),
          const SizedBox(height: 4),
          _LegendItem(
            color: SahoolColors.harvestGold,
            label: isArabic ? 'متوسط (0.4-0.6)' : 'Moderate (0.4-0.6)',
          ),
          const SizedBox(height: 4),
          _LegendItem(
            color: SahoolColors.danger,
            label: isArabic ? 'حرج (<0.4)' : 'Critical (<0.4)',
          ),
        ],
      ),
    );
  }
}

/// Legend item
class _LegendItem extends StatelessWidget {
  final Color color;
  final String label;

  const _LegendItem({
    required this.color,
    required this.label,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(4),
            border: Border.all(color: Colors.white, width: 1.5),
          ),
        ),
        const SizedBox(width: 6),
        Text(
          label,
          style: const TextStyle(
            fontSize: 11,
            color: SahoolColors.forestGreen,
          ),
        ),
      ],
    );
  }
}

/// Zoom controls widget
class _ZoomControls extends StatelessWidget {
  final MapController mapController;

  const _ZoomControls({required this.mapController});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        _ZoomButton(
          icon: Icons.add,
          onPressed: () {
            final camera = mapController.camera;
            mapController.move(camera.center, camera.zoom + 1);
          },
        ),
        const SizedBox(height: 8),
        _ZoomButton(
          icon: Icons.remove,
          onPressed: () {
            final camera = mapController.camera;
            mapController.move(camera.center, camera.zoom - 1);
          },
        ),
      ],
    );
  }
}

/// Zoom button widget
class _ZoomButton extends StatelessWidget {
  final IconData icon;
  final VoidCallback onPressed;

  const _ZoomButton({
    required this.icon,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: IconButton(
        icon: Icon(icon, size: 20),
        color: SahoolColors.forestGreen,
        onPressed: onPressed,
        padding: EdgeInsets.zero,
      ),
    );
  }
}
