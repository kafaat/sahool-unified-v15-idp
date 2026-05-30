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

class _FarmDetailView extends ConsumerWidget {
  final FarmEntity farm;
  const _FarmDetailView({required this.farm});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final center = LatLng(
      farm.centerLat != 0.0 ? farm.centerLat : 15.3694,
      farm.centerLng != 0.0 ? farm.centerLng : 44.1910,
    );

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: const Color(0xFFF5F7F5),
        appBar: AppBar(
          title: Text(farm.name, style: const TextStyle(fontWeight: FontWeight.bold)),
          centerTitle: true,
          backgroundColor: Colors.white,
          foregroundColor: const Color(0xFF1A1A1A),
          elevation: 0,
          surfaceTintColor: Colors.transparent,
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
              // Satellite map showing farm location
              SizedBox(
                height: 220,
                child: FlutterMap(
                  options: MapOptions(
                    initialCenter: center,
                    initialZoom: 13,
                    interactionOptions: const InteractionOptions(flags: InteractiveFlag.all),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                      userAgentPackageName: 'com.sahool.app',
                      maxZoom: 19,
                    ),
                    MarkerLayer(
                      markers: [
                        Marker(
                          point: center,
                          width: 40,
                          height: 40,
                          child: Container(
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
                    _infoCard(Icons.location_on_rounded, 'الموقع', farm.location.isNotEmpty ? farm.location : '—'),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        Expanded(child: _infoCard(Icons.straighten_rounded, 'المساحة', '${farm.totalAreaHa.toStringAsFixed(1)} هـ')),
                        const SizedBox(width: 12),
                        Expanded(child: _infoCard(Icons.water_drop_rounded, 'مصدر المياه', farm.waterSource.isNotEmpty ? farm.waterSource : '—')),
                      ],
                    ),
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
                    Container(
                      width: double.infinity,
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.grey.shade200),
                      ),
                      child: Column(
                        children: [
                          Icon(Icons.grass_rounded, size: 48, color: Colors.grey[300]),
                          const SizedBox(height: 12),
                          Text('لا توجد حقول بعد', style: TextStyle(fontSize: 15, color: Colors.grey[600])),
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
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _infoCard(IconData icon, String label, String value) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Row(
        children: [
          Icon(icon, color: SahoolTheme.primary, size: 20),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(label, style: TextStyle(fontSize: 11, color: Colors.grey[600])),
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
