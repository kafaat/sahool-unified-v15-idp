import 'package:flutter/material.dart';
import 'package:flutter/semantics.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/theme/organic_widgets.dart';
import '../../../core/accessibility/semantics_helper.dart';
import '../../../core/di/providers.dart';
import '../logic/sync_provider.dart';
import '../logic/home_providers.dart';
import '../../weather/presentation/providers/weather_provider.dart';
import '../../tasks/providers/tasks_provider.dart' hide apiClientProvider;

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
    final apiClient = ref.watch(apiClientProvider);
    final fieldsAsync = ref.watch(fieldsStreamProvider(apiClient.tenantId as String));
    final syncStatus = ref.watch(syncStatusUiProvider);
    final pendingCount = ref.watch(pendingOperationsProvider).valueOrNull ?? 0;

    // Live data from providers
    final weatherState = ref.watch(weatherProvider);
    final pendingTasks = ref.watch(pendingTasksProvider);
    final ndvi = ref.watch(averageNdviProvider);
    final fieldsData = ref.watch(dashboardFieldsProvider);

    // Derived values
    final taskCount = pendingTasks.length;
    final weatherTemp = weatherState.data?.current.temperature.round();
    final weatherCondition = weatherState.data?.current.conditionAr ?? '—';
    final ndviDisplay = ndvi != null ? ndvi.toStringAsFixed(2) : '—';
    final ndviHealth = ndvi != null
        ? SahoolSemantics.getHealthLabel(ndvi)
        : 'لا توجد بيانات';

    // Soil moisture from first field (simplified; in production use sensor data)
    final soilMoisture = fieldsData.when(
      data: (fields) {
        if (fields.isEmpty) return '—';
        final first = fields.first;
        // Use NDVI as a rough proxy if no soil sensor
        return first.ndviCurrent != null
            ? '${(first.ndviCurrent! * 70).round()}%'
            : '—';
      },
      loading: () => '...',
      error: (_, __) => '—',
    );

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
                child: _buildHeader(context, syncStatus, pendingCount, weatherTemp),
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
                    onTap: () => context.push('/monitor'),
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
                          child: _buildMapOverlay(fieldsData),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 16),

              // الصف الثاني: بطاقتين (المهام + الري)
              // Second row: Tasks and Irrigation cards
              Row(
                children: [
                  // بطاقة المهام (لون مميز) - Tasks card with accent color
                  Expanded(
                    child: Semantics(
                      label: SahoolSemantics.tasksCard,
                      hint: '$taskCount مهام تنتظر التنفيذ اليوم، اضغط لعرض المهام',
                      button: true,
                      child: SizedBox(
                        height: 160,
                        child: OrganicCard(
                          color: SahoolColors.harvestGold,
                          isPrimary: true,
                          onTap: () {
                            context.push('/tasks');
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
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    "$taskCount مهام",
                                    style: const TextStyle(
                                      fontSize: 24,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                  const Text(
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
                      hint: 'رطوبة التربة $soilMoisture، اضغط لعرض التفاصيل',
                      button: true,
                      child: SizedBox(
                        height: 160,
                        child: OrganicCard(
                          onTap: () {
                            context.push('/irrigation');
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
                                      Text(
                                        soilMoisture,
                                        style: const TextStyle(
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
                                    soilMoisture == '—' ? 'لا توجد بيانات' : 'رطوبة التربة',
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
                      label: '${SahoolSemantics.fieldHealth}، ${SahoolSemantics.ndviValue} $ndviDisplay',
                      hint: '$ndviHealth، اضغط لعرض تفاصيل صحة المحصول',
                      button: true,
                      child: SizedBox(
                        height: 120,
                        child: OrganicCard(
                          onTap: () => context.push('/crop-health'),
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
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    ndviDisplay,
                                    style: const TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                      color: SahoolColors.forestGreen,
                                    ),
                                  ),
                                  Text(
                                    ndviHealth,
                                    style: const TextStyle(
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
                      hint: '${SahoolSemantics.temperature} ${weatherTemp ?? "—"} درجة مئوية، $weatherCondition',
                      button: true,
                      child: SizedBox(
                        height: 120,
                        child: OrganicCard(
                          onTap: () => context.push('/weather'),
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
                              Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    weatherTemp != null ? "$weatherTemp°C" : "—",
                                    style: const TextStyle(
                                      fontSize: 20,
                                      fontWeight: FontWeight.bold,
                                      color: SahoolColors.forestGreen,
                                    ),
                                  ),
                                  Text(
                                    weatherCondition,
                                    style: const TextStyle(
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
                hint: 'اضغط للدخول للمحادثات',
                button: true,
                child: SizedBox(
                  height: 100,
                  child: OrganicCard(
                    onTap: () => context.push('/chat'),
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
                              Icons.chat_bubble_outline,
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
                                "المحادثات والخبراء",
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              Text(
                                "تواصل مع الخبراء الزراعيين",
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
          switch (index) {
            case 0:
              // Already on home
              break;
            case 1:
              context.go('/monitor');
              break;
            case 2:
              context.push('/fields/new');
              break;
            case 3:
              context.go('/market');
              break;
            case 4:
              context.go('/profile');
              break;
          }
        },
      ),
    );
  }

  // --- Helper Widgets ---

  Widget _buildHeader(BuildContext context, SyncStatus status, int count, int? weatherTemp) {
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
                _getGreeting(),
                style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                      color: Colors.grey,
                    ),
              ),
              Semantics(
                header: true,
                child: Text(
                  "المزارع",
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
          label: '${SahoolSemantics.syncStatus}: $syncLabel، ${SahoolSemantics.temperature}: ${weatherTemp ?? "—"} درجة',
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
                Text(
                  weatherTemp != null ? "$weatherTemp°" : "—",
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  String _getGreeting() {
    final hour = DateTime.now().hour;
    if (hour < 12) return 'صباح الخير،';
    if (hour < 17) return 'مساء الخير،';
    return 'مساء النور،';
  }

  Widget _buildMapOverlay(AsyncValue<List<dynamic>> fieldsData) {
    return fieldsData.when(
      data: (fields) {
        if (fields.isEmpty) {
          return Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.9),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              "لا توجد حقول مسجلة",
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          );
        }
        final first = fields.first;
        return Semantics(
          label: '${first.name}، ${first.cropType ?? ""}، ${first.status ?? "نشط"}',
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
                Text(
                  "${first.name} • ${first.cropType ?? '—'}",
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                const Spacer(),
                StatusBadge(
                  label: (first.status as String?) ?? "نشط",
                  color: SahoolColors.forestGreen,
                  icon: Icons.sensors,
                ),
              ],
            ),
          ),
        );
      },
      loading: () => const SizedBox.shrink(),
      error: (_, __) => const SizedBox.shrink(),
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
                    points: (f.boundary as List).cast<LatLng>(),
                    color: SahoolColors.harvestGold.withOpacity(0.4),
                    borderColor: Colors.white,
                    borderStrokeWidth: 2,
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
