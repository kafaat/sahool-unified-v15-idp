import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/config/theme.dart';
import '../../data/farm_entity.dart';
import '../../domain/farm_providers.dart';

class FarmDetailScreen extends ConsumerWidget {
  final String farmId;
  const FarmDetailScreen({super.key, required this.farmId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final farmsAsync = ref.watch(farmsListProvider);

    return farmsAsync.when(
      loading: () => const Scaffold(body: Center(child: CircularProgressIndicator())),
      error: (e, _) => Scaffold(
        appBar: AppBar(title: const Text('المزرعة')),
        body: Center(child: Text('خطأ: $e')),
      ),
      data: (farms) {
        final farm = farms.where((f) => f.id == farmId).firstOrNull;
        if (farm == null) {
          return Scaffold(
            appBar: AppBar(title: const Text('المزرعة')),
            body: const Center(child: Text('المزرعة غير موجودة')),
          );
        }
        return _FarmDetailView(farm: farm);
      },
    );
  }
}

List<LatLng> _bboxToPolygon(List<double> bbox) {
  final minLng = bbox[0], minLat = bbox[1], maxLng = bbox[2], maxLat = bbox[3];
  return [
    LatLng(minLat, minLng),
    LatLng(minLat, maxLng),
    LatLng(maxLat, maxLng),
    LatLng(maxLat, minLng),
  ];
}


class _FarmDetailView extends ConsumerWidget {
  final FarmEntity farm;
  const _FarmDetailView({required this.farm});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final center = LatLng(
      farm.centerLat != 0.0 ? farm.centerLat : 15.3694,
      farm.centerLng != 0.0 ? farm.centerLng : 44.1910,
    );

    final double initialZoom = (farm.zoom ?? 13).toDouble();

    // Build polygon points from bbox
    List<LatLng>? polygonPoints;
    if (farm.bbox != null && farm.bbox!.length == 4) {
      polygonPoints = _bboxToPolygon(farm.bbox!);
    }

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(farm.name, style: const TextStyle(fontWeight: FontWeight.bold)),
          centerTitle: true,
          backgroundColor: Theme.of(context).colorScheme.surface,
          foregroundColor: Theme.of(context).colorScheme.onSurface,
          elevation: 0,
          surfaceTintColor: Colors.transparent,
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh_rounded),
              tooltip: 'تحديث',
              onPressed: () => ref.refresh(farmsListProvider),
            ),
          ],
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () => context.push('/fields/create', extra: {'farmId': farm.id}),
          backgroundColor: SahoolTheme.primary,
          foregroundColor: Colors.white,
          icon: const Icon(Icons.add_rounded),
          label: const Text('إضافة حقل'),
        ),
        body: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Satellite map showing farm location + optional polygon
              SizedBox(
                height: 220,
                child: FlutterMap(
                  options: MapOptions(
                    initialCenter: center,
                    initialZoom: initialZoom,
                    interactionOptions: const InteractionOptions(flags: InteractiveFlag.all),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                      userAgentPackageName: 'com.sahool.app',
                      maxZoom: 19,
                    ),
                    if (polygonPoints != null)
                      PolygonLayer(
                        polygons: [
                          Polygon(
                            points: polygonPoints,
                            color: SahoolTheme.primary.withValues(alpha: 0.20),
                            borderColor: SahoolTheme.primary,
                            borderStrokeWidth: 2.5,
                          ),
                        ],
                      ),
                    if (polygonPoints == null)
                      MarkerLayer(
                        markers: [
                          Marker(
                            point: center,
                            width: 40,
                            height: 40,
                            child: DecoratedBox(
                              decoration: BoxDecoration(
                                color: SahoolTheme.primary,
                                shape: BoxShape.circle,
                                border: Border.all(color: Colors.white, width: 2),
                              ),
                              child: const Icon(Icons.agriculture_rounded, color: Colors.white, size: 22),
                            ),
                          ),
                        ],
                      ),
                  ],
                ),
              ),

              // Farm info cards
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _infoCard(context, Icons.location_on_rounded, 'الموقع', (farm.location?.isNotEmpty == true) ? farm.location! : '—'),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(child: _infoCard(context, Icons.straighten_rounded, 'المساحة', '${farm.totalAreaHa.toStringAsFixed(1)} هـ')),
                        const SizedBox(width: 12),
                        Expanded(child: _infoCard(context, Icons.water_drop_rounded, 'مصدر المياه', (farm.waterSource?.isNotEmpty == true) ? farm.waterSource! : '—')),
                      ],
                    ),
                    // Second row: zoom + region (shown only when data is available)
                    if (farm.zoom != null || (farm.region != null && farm.region!.isNotEmpty)) ...[
                      const SizedBox(height: 12),
                      Row(
                        children: [
                          if (farm.zoom != null)
                            Expanded(
                              child: _infoCard(
                                context,
                                Icons.zoom_in_rounded,
                                'مستوى التكبير',
                                '${farm.zoom}',
                              ),
                            ),
                          if (farm.zoom != null && farm.region != null && farm.region!.isNotEmpty)
                            const SizedBox(width: 12),
                          if (farm.region != null && farm.region!.isNotEmpty)
                            Expanded(
                              child: _infoCard(
                                context,
                                Icons.map_rounded,
                                'المنطقة',
                                farm.region!,
                              ),
                            ),
                        ],
                      ),
                    ],
                    const SizedBox(height: 24),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('الحقول', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        TextButton.icon(
                          onPressed: () => context.push('/fields/create', extra: {'farmId': farm.id}),
                          icon: const Icon(Icons.add_rounded, size: 18),
                          label: const Text('إضافة حقل'),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Builder(
                      builder: (context) => Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Theme.of(context).colorScheme.surface,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Theme.of(context).colorScheme.outline.withValues(alpha: 0.3)),
                      ),
                      child: Column(
                        children: [
                          Icon(Icons.grass_rounded, size: 48, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.3)),
                          const SizedBox(height: 12),
                          Text('لا توجد حقول بعد', style: TextStyle(fontSize: 15, color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6))),
                          const SizedBox(height: 8),
                          ElevatedButton.icon(
                            onPressed: () => context.push('/fields/create', extra: {'farmId': farm.id}),
                            icon: const Icon(Icons.add_rounded, size: 18),
                            label: const Text('إضافة أول حقل'),
                            style: ElevatedButton.styleFrom(
                              backgroundColor: SahoolTheme.primary,
                              foregroundColor: Colors.white,
                            ),
                          ),
                        ],
                      ),
                    ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoCard(BuildContext context, IconData icon, String label, String value) {
    final cs = Theme.of(context).colorScheme;
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: cs.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: cs.outline.withValues(alpha: 0.3)),
      ),
      child: Row(
        children: [
          Icon(icon, color: SahoolTheme.primary, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: TextStyle(fontSize: 11, color: cs.onSurface.withValues(alpha: 0.6))),
                const SizedBox(height: 2),
                Text(value, style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
