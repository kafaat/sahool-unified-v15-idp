import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../../../core/di/providers.dart';
import '../logic/sync_provider.dart';

/// شاشة سهول الرئيسية - تصميم Bento Grid العضوي
/// Organic Dashboard with Bento Grid Layout
class HomeScreen extends ConsumerWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // مراقبة البيانات
    final fieldsAsync = ref.watch(fieldsStreamProvider);
    final syncStatus = ref.watch(syncStatusUiProvider);
    final pendingCount = ref.watch(pendingOperationsProvider).valueOrNull ?? 0;

    return Scaffold(
      backgroundColor: SahoolColors.warmCream,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // 1. الرأس (الترحيب + الطقس)
              _buildHeader(context, syncStatus, pendingCount),

              const SizedBox(height: 32),

              // 2. شبكة بينتو (Bento Grid Layout)
              // البطاقة الكبيرة: الخريطة
              SizedBox(
                height: 320,
                child: OrganicCard(
                  padding: EdgeInsets.zero,
                  child: Stack(
                    children: [
                      // الخريطة
                      ClipRRect(
                        borderRadius: BorderRadius.circular(28),
                        child: _buildMap(fieldsAsync),
                      ),
                      // تراكب المعلومات (Overlay)
                      Positioned(
                        bottom: 16,
                        left: 16,
                        right: 16,
                        child: Container(
                          padding: const EdgeInsets.all(12),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.9),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Row(
                            children: [
                              const CircleAvatar(
                                radius: 4,
                                backgroundColor: SahoolColors.forestGreen,
                              ),
                              const SizedBox(width: 8),
                              const Text(
                                "الحقل الشمالي • قمح",
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 12,
                                ),
                              ),
                              const Spacer(),
                              const StatusBadge(
                                label: "نشط",
                                color: SahoolColors.forestGreen,
                                icon: Icons.sensors,
                              ),
                            ],
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // الصف الثاني: بطاقتين (المهام + الإنتاجية)
              Row(
                children: [
                  // بطاقة المهام (لون مميز)
                  Expanded(
                    child: SizedBox(
                      height: 160,
                      child: OrganicCard(
                        color: SahoolColors.harvestGold,
                        isPrimary: true,
                        onTap: () {
                          // الانتقال لصفحة المهام
                        },
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.2),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Icons.checklist,
                                color: Colors.white,
                              ),
                            ),
                            const Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  "5 مهام",
                                  style: TextStyle(
                                    fontSize: 24,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.white,
                                  ),
                                ),
                                Text(
                                  "تنتظر التنفيذ اليوم",
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.white70,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),

                  // بطاقة الإنتاجية/الري
                  Expanded(
                    child: SizedBox(
                      height: 160,
                      child: OrganicCard(
                        onTap: () {
                          // الانتقال لصفحة التحليلات
                        },
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Icon(
                                  Icons.water_drop,
                                  color: Colors.blue,
                                ),
                                Text(
                                  "الري",
                                  style: TextStyle(
                                    color: Colors.grey[600],
                                    fontSize: 12,
                                  ),
                                ),
                              ],
                            ),
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Row(
                                  children: [
                                    const Text(
                                      "45%",
                                      style: TextStyle(
                                        fontSize: 24,
                                        fontWeight: FontWeight.bold,
                                        color: SahoolColors.forestGreen,
                                      ),
                                    ),
                                    const SizedBox(width: 4),
                                    Icon(
                                      Icons.arrow_upward,
                                      size: 14,
                                      color: Colors.grey[400],
                                    ),
                                  ],
                                ),
                                Text(
                                  "رطوبة التربة ممتازة",
                                  style: TextStyle(
                                    fontSize: 12,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // الصف الثالث: بطاقات إضافية
              Row(
                children: [
                  // بطاقة صحة المحصول
                  Expanded(
                    child: SizedBox(
                      height: 120,
                      child: OrganicCard(
                        onTap: () {},
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Icon(
                                  Icons.eco,
                                  color: SahoolColors.sageGreen,
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 8,
                                    vertical: 2,
                                  ),
                                  decoration: BoxDecoration(
                                    color: SahoolColors.sageGreen.withOpacity(0.2),
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: const Text(
                                    "NDVI",
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: SahoolColors.sageGreen,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  "0.72",
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: SahoolColors.forestGreen,
                                  ),
                                ),
                                Text(
                                  "صحة ممتازة",
                                  style: TextStyle(
                                    fontSize: 11,
                                    color: Colors.grey,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(width: 16),

                  // بطاقة الطقس
                  Expanded(
                    child: SizedBox(
                      height: 120,
                      child: OrganicCard(
                        onTap: () {},
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Icon(
                                  Icons.wb_sunny,
                                  color: SahoolColors.harvestGold,
                                ),
                                Text(
                                  "اليوم",
                                  style: TextStyle(
                                    fontSize: 10,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ],
                            ),
                            const Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(
                                  "24°C",
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                    color: SahoolColors.forestGreen,
                                  ),
                                ),
                                Text(
                                  "مشمس جزئياً",
                                  style: TextStyle(
                                    fontSize: 11,
                                    color: Colors.grey,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // الصف الرابع: بطاقة عريضة (المجتمع/تنبيهات)
              SizedBox(
                height: 100,
                child: OrganicCard(
                  onTap: () {},
                  child: Row(
                    children: [
                      Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          color: SahoolColors.paleOlive,
                          borderRadius: BorderRadius.circular(18),
                        ),
                        child: const Icon(
                          Icons.person,
                          color: SahoolColors.forestGreen,
                          size: 30,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              "رسالة من المهندس سالم",
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              "يرجى فحص مضخة الحقل C غداً...",
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                      const Icon(
                        Icons.arrow_forward_ios,
                        size: 16,
                        color: SahoolColors.sageGreen,
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 80), // مساحة للتمرير
            ],
          ),
        ),
      ),

      // شريط التنقل السفلي العائم (Floating Bottom Bar)
      bottomNavigationBar: FloatingNavBar(
        currentIndex: 0,
        onTap: (index) {
          // التنقل بين الصفحات
          if (index == -1) {
            // إضافة حقل جديد
          }
        },
      ),
    );
  }

  // --- Helper Widgets ---

  Widget _buildHeader(BuildContext context, SyncStatus status, int count) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              "صباح الخير،",
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                    color: Colors.grey,
                  ),
            ),
            Text(
              "المزارع أحمد",
              style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.w900,
                    color: SahoolColors.forestGreen,
                  ),
            ),
          ],
        ),

        // كبسولة الطقس والمزامنة
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(24),
            border: Border.all(color: Colors.grey.withOpacity(0.1)),
          ),
          child: Row(
            children: [
              // أيقونة المزامنة
              if (status == SyncStatus.syncing)
                const Padding(
                  padding: EdgeInsets.only(left: 8),
                  child: SizedBox(
                    width: 12,
                    height: 12,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  ),
                ),
              if (status == SyncStatus.offline)
                const Icon(Icons.cloud_off, size: 20, color: Colors.grey),
              if (status == SyncStatus.synced)
                const Icon(
                  Icons.cloud_queue,
                  size: 20,
                  color: SahoolColors.forestGreen,
                ),

              Container(
                height: 20,
                width: 1,
                color: Colors.grey[300],
                margin: const EdgeInsets.symmetric(horizontal: 8),
              ),

              // الطقس
              const Icon(
                Icons.wb_sunny_rounded,
                color: SahoolColors.harvestGold,
                size: 20,
              ),
              const SizedBox(width: 4),
              const Text(
                "24°",
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildMap(AsyncValue<List<dynamic>> fieldsAsync) {
    return FlutterMap(
      options: const MapOptions(
        initialCenter: LatLng(15.3694, 44.1910),
        initialZoom: 13,
      ),
      children: [
        TileLayer(
          urlTemplate:
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          userAgentPackageName: 'com.kafaat.sahool',
        ),
        fieldsAsync.when(
          data: (fields) => PolygonLayer(
            polygons: fields
                .map(
                  (f) => Polygon(
                    points: f.boundary,
                    color: SahoolColors.harvestGold.withOpacity(0.4),
                    borderColor: Colors.white,
                    borderStrokeWidth: 2,
                    isFilled: true,
                  ),
                )
                .toList(),
          ),
          loading: () => const MarkerLayer(markers: []),
          error: (_, __) => const MarkerLayer(markers: []),
        ),
      ],
    );
  }
}
