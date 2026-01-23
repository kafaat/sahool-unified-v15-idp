import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../../../core/accessibility/semantics_helper.dart';
import '../../../core/di/providers.dart';
import '../logic/sync_provider.dart';

/// شاشة سهول الرئيسية - تصميم Bento Grid العضوي
/// Organic Dashboard with Bento Grid Layout
///
/// Accessibility Features:
/// - Semantic labels for screen readers
/// - Proper heading hierarchy
/// - Focus management
/// - Live region announcements
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
              // 1. الرأس (الترحيب + الطقس) - Header with welcome and weather
              Semantics(
                header: true,
                label: 'شاشة الرئيسية، لوحة التحكم الزراعية',
                child: _buildHeader(context, syncStatus, pendingCount),
              ),

              const SizedBox(height: 32),

              // 2. شبكة بينتو (Bento Grid Layout)
              // البطاقة الكبيرة: الخريطة - Large map card
              Semantics(
                label: SahoolSemantics.mapView,
                hint: 'اضغط لفتح الخريطة التفصيلية',
                button: true,
                child: SizedBox(
                  height: 320,
                  child: OrganicCard(
                    padding: EdgeInsets.zero,
                    child: Stack(
                      children: [
                        // الخريطة - Map
                        ClipRRect(
                          borderRadius: BorderRadius.circular(28),
                          child: ExcludeSemantics(
                            // Exclude map tiles from semantics as they're decorative
                            child: _buildMap(fieldsAsync),
                          ),
                        ),
                        // تراكب المعلومات (Overlay) - Info overlay
                        Positioned(
                          bottom: 16,
                          left: 16,
                          right: 16,
                          child: Semantics(
                            label: 'الحقل الشمالي، قمح، نشط',
                            child: Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.white.withOpacity(0.9),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Row(
                                children: [
                                  ExcludeSemantics(
                                    child: const CircleAvatar(
                                      radius: 4,
                                      backgroundColor: SahoolColors.forestGreen,
                                    ),
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
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // الصف الثاني: بطاقتين (المهام + الإنتاجية)
              // Second row: Tasks and Irrigation cards
              Row(
                children: [
                  // بطاقة المهام (لون مميز) - Tasks card with accent color
                  Expanded(
                    child: Semantics(
                      label: SahoolSemantics.tasksCard,
                      hint: '5 مهام تنتظر التنفيذ اليوم، اضغط لعرض المهام',
                      button: true,
                      child: SizedBox(
                        height: 160,
                        child: OrganicCard(
                          color: SahoolColors.harvestGold,
                          isPrimary: true,
                          onTap: () {
                            // الانتقال لصفحة المهام
                            AnnouncementHelper.announceNavigation(context, 'المهام');
                          },
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              ExcludeSemantics(
                                child: Container(
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
                  ),
                  const SizedBox(width: 16),

                  // بطاقة الإنتاجية/الري - Irrigation card
                  Expanded(
                    child: Semantics(
                      label: SahoolSemantics.irrigationCard,
                      hint: 'رطوبة التربة 45%، ممتازة، اضغط لعرض التفاصيل',
                      button: true,
                      child: SizedBox(
                        height: 160,
                        child: OrganicCard(
                          onTap: () {
                            // الانتقال لصفحة التحليلات
                            AnnouncementHelper.announceNavigation(context, 'التحليلات');
                          },
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Semantics(
                                    label: 'أيقونة الري',
                                    excludeSemantics: true,
                                    child: const Icon(
                                      Icons.water_drop,
                                      color: Colors.blue,
                                    ),
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
                                      ExcludeSemantics(
                                        child: Icon(
                                          Icons.arrow_upward,
                                          size: 14,
                                          color: Colors.grey[400],
                                        ),
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
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // الصف الثالث: بطاقات إضافية
              // Third row: Crop health and weather cards
              Row(
                children: [
                  // بطاقة صحة المحصول - Crop health card
                  Expanded(
                    child: Semantics(
                      label: '${SahoolSemantics.fieldHealth}، ${SahoolSemantics.ndviValue} 0.72',
                      hint: 'صحة ممتازة، اضغط لعرض تفاصيل صحة المحصول',
                      button: true,
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
                                  ExcludeSemantics(
                                    child: const Icon(
                                      Icons.eco,
                                      color: SahoolColors.sageGreen,
                                    ),
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
                  ),
                  const SizedBox(width: 16),

                  // بطاقة الطقس - Weather card
                  Expanded(
                    child: Semantics(
                      label: SahoolSemantics.weatherInfo,
                      hint: '${SahoolSemantics.temperature} 24 درجة مئوية، مشمس جزئياً',
                      button: true,
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
                                  ExcludeSemantics(
                                    child: const Icon(
                                      Icons.wb_sunny,
                                      color: SahoolColors.harvestGold,
                                    ),
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
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // الصف الرابع: بطاقة عريضة (المجتمع/تنبيهات)
              // Fourth row: Wide message card
              Semantics(
                label: SahoolSemantics.messageCard,
                hint: 'رسالة من المهندس سالم، يرجى فحص مضخة الحقل C غداً، اضغط لفتح الرسالة',
                button: true,
                child: SizedBox(
                  height: 100,
                  child: OrganicCard(
                    onTap: () {},
                    child: Row(
                      children: [
                        ExcludeSemantics(
                          child: Container(
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
                        ExcludeSemantics(
                          child: const Icon(
                            Icons.arrow_forward_ios,
                            size: 16,
                            color: SahoolColors.sageGreen,
                          ),
                        ),
                      ],
                    ),
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
    // Build sync status label for accessibility
    String syncLabel;
    switch (status) {
      case SyncStatus.syncing:
        syncLabel = SahoolSemantics.syncing;
        break;
      case SyncStatus.offline:
        syncLabel = SahoolSemantics.offline;
        break;
      case SyncStatus.synced:
        syncLabel = SahoolSemantics.synced;
        break;
    }

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Welcome text with heading semantics
        MergeSemantics(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                "صباح الخير،",
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.grey,
                    ),
              ),
              Semantics(
                header: true,
                child: Text(
                  "المزارع أحمد",
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.w900,
                        color: SahoolColors.forestGreen,
                      ),
                ),
              ),
            ],
          ),
        ),

        // كبسولة الطقس والمزامنة - Weather and sync capsule
        Semantics(
          label: '${SahoolSemantics.syncStatus}: $syncLabel، ${SahoolSemantics.temperature}: 24 درجة',
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(24),
              border: Border.all(color: Colors.grey.withOpacity(0.1)),
            ),
            child: Row(
              children: [
                // أيقونة المزامنة - Sync icon
                ExcludeSemantics(
                  child: Builder(
                    builder: (context) {
                      if (status == SyncStatus.syncing) {
                        return const Padding(
                          padding: EdgeInsets.only(left: 8),
                          child: SizedBox(
                            width: 12,
                            height: 12,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        );
                      } else if (status == SyncStatus.offline) {
                        return const Icon(Icons.cloud_off, size: 20, color: Colors.grey);
                      } else {
                        return const Icon(
                          Icons.cloud_queue,
                          size: 20,
                          color: SahoolColors.forestGreen,
                        );
                      }
                    },
                  ),
                ),

                ExcludeSemantics(
                  child: Container(
                    height: 20,
                    width: 1,
                    color: Colors.grey[300],
                    margin: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                ),

                // الطقس - Weather
                ExcludeSemantics(
                  child: const Icon(
                    Icons.wb_sunny_rounded,
                    color: SahoolColors.harvestGold,
                    size: 20,
                  ),
                ),
                const SizedBox(width: 4),
                const Text(
                  "24°",
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
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
