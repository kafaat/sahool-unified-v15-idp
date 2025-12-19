import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../core/theme/sahool_pro_theme.dart';
import '../../../core/di/providers.dart';
import '../../shared/widgets/sahool_metrics_card.dart';
import '../../field/ui/logic/drawing_provider.dart';
import '../../polygon_editor/polygon_editor.dart';
import '../logic/sync_provider.dart';

/// SAHOOL Pro Home Screen - The Cockpit
/// شاشة رئيسية بتصميم John Deere Operations Center
class ProHomeScreen extends ConsumerStatefulWidget {
  const ProHomeScreen({super.key});

  @override
  ConsumerState<ProHomeScreen> createState() => _ProHomeScreenState();
}

class _ProHomeScreenState extends ConsumerState<ProHomeScreen> {
  final MapController _mapController = MapController();
  final PolygonEditorState _editorState = PolygonEditorState();

  String? _selectedFieldId;
  int _selectedLayerIndex = 0;
  bool _isDrawingMode = false;

  // Tenant ID (في التطبيق الحقيقي يأتي من Auth)
  static const String _tenantId = 'tenant_001';

  final List<_MapLayer> _layers = [
    _MapLayer('القمر الصناعي', Icons.satellite_alt,
      'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'),
    _MapLayer('الخريطة', Icons.map,
      'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
  ];

  @override
  void dispose() {
    _mapController.dispose();
    _editorState.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final fieldsAsync = ref.watch(fieldsStreamProvider(_tenantId));
    final syncStatus = ref.watch(syncStatusUiProvider);
    final pendingCount = ref.watch(pendingOperationsProvider).valueOrNull ?? 0;
    final drawingState = ref.watch(drawingProvider);

    return Scaffold(
      body: Stack(
        children: [
          // ═══════════════════════════════════════════════════════════
          // 1. الخريطة (الخلفية)
          // ═══════════════════════════════════════════════════════════
          Positioned.fill(
            child: FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: const LatLng(15.3694, 44.1910), // صنعاء
                initialZoom: 14,
                onTap: (tapPosition, point) {
                  if (drawingState.isDrawing) {
                    // في وضع الرسم، أضف نقطة
                    ref.read(drawingProvider.notifier).addPoint(point);
                  } else {
                    // إلغاء التحديد
                    setState(() => _selectedFieldId = null);
                  }
                },
              ),
              children: [
                // طبقة الخريطة الأساسية
                TileLayer(
                  urlTemplate: _layers[_selectedLayerIndex].url,
                  userAgentPackageName: 'com.kafaat.sahool',
                  maxZoom: 19,
                ),

                // طبقة التسميات (فوق القمر الصناعي)
                if (_selectedLayerIndex == 0)
                  TileLayer(
                    urlTemplate: 'https://stamen-tiles.a.ssl.fastly.net/toner-labels/{z}/{x}/{y}.png',
                    userAgentPackageName: 'com.kafaat.sahool',
                    backgroundColor: Colors.transparent,
                  ),

                // طبقة الحقول من قاعدة البيانات
                fieldsAsync.when(
                  data: (fields) => PolygonLayer(
                    polygons: fields.map((f) {
                      final isSelected = f.id == _selectedFieldId;
                      final isSynced = f.synced;

                      return Polygon(
                        points: f.boundary,
                        color: isSelected
                            ? SahoolProColors.tractorYellow.withOpacity(0.4)
                            : (isSynced
                                ? SahoolProColors.johnGreen.withOpacity(0.3)
                                : SahoolProColors.warningOrange.withOpacity(0.3)),
                        borderColor: isSelected
                            ? Colors.white
                            : (isSynced
                                ? SahoolProColors.johnGreen
                                : SahoolProColors.warningOrange),
                        borderStrokeWidth: isSelected ? 4 : 2,
                        isDotted: !isSynced,
                        label: f.name,
                        labelStyle: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontSize: 12,
                          shadows: [
                            Shadow(blurRadius: 4, color: Colors.black),
                          ],
                        ),
                      );
                    }).toList(),
                  ),
                  loading: () => const PolygonLayer(polygons: []),
                  error: (_, __) => const PolygonLayer(polygons: []),
                ),

                // طبقة الرسم الحالي (عند تفعيل وضع الرسم)
                if (drawingState.isDrawing) ...[
                  // الخطوط
                  PolylineLayer(
                    polylines: [
                      if (drawingState.points.length >= 2)
                        Polyline(
                          points: [
                            ...drawingState.points,
                            if (drawingState.points.isNotEmpty)
                              drawingState.points.first,
                          ],
                          color: SahoolProColors.tractorYellow,
                          strokeWidth: 3,
                          isDotted: true,
                        ),
                    ],
                  ),
                  // نقاط الزوايا
                  MarkerLayer(
                    markers: drawingState.points.asMap().entries.map((e) {
                      final index = e.key;
                      final point = e.value;
                      return Marker(
                        point: point,
                        width: 24,
                        height: 24,
                        child: Container(
                          decoration: BoxDecoration(
                            color: Colors.white,
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: SahoolProColors.tractorYellow,
                              width: 3,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.3),
                                blurRadius: 4,
                              ),
                            ],
                          ),
                          child: Center(
                            child: Text(
                              '${index + 1}',
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: SahoolProColors.johnGreen,
                              ),
                            ),
                          ),
                        ),
                      );
                    }).toList(),
                  ),
                ],

                // علامات للنقر على الحقول
                fieldsAsync.maybeWhen(
                  data: (fields) => MarkerLayer(
                    markers: fields.map((f) {
                      final centroid = _calculateCentroid(f.boundary);
                      return Marker(
                        point: centroid,
                        width: 80,
                        height: 40,
                        child: GestureDetector(
                          onTap: () => setState(() => _selectedFieldId = f.id),
                          child: Container(color: Colors.transparent),
                        ),
                      );
                    }).toList(),
                  ),
                  orElse: () => const MarkerLayer(markers: []),
                ),
              ],
            ),
          ),

          // ═══════════════════════════════════════════════════════════
          // 2. الشريط العلوي (Operations Header)
          // ═══════════════════════════════════════════════════════════
          Positioned(
            top: MediaQuery.of(context).padding.top + 12,
            left: 16,
            right: 16,
            child: _buildHeader(syncStatus, pendingCount),
          ),

          // ═══════════════════════════════════════════════════════════
          // 3. أدوات التحكم (يمين الشاشة)
          // ═══════════════════════════════════════════════════════════
          Positioned(
            right: 16,
            top: MediaQuery.of(context).padding.top + 90,
            child: _buildMapControls(),
          ),

          // ═══════════════════════════════════════════════════════════
          // 4. محدد الطبقات (يسار الشاشة)
          // ═══════════════════════════════════════════════════════════
          Positioned(
            left: 16,
            top: MediaQuery.of(context).padding.top + 90,
            child: _buildLayerSelector(),
          ),

          // ═══════════════════════════════════════════════════════════
          // 5. لوحة المعلومات السفلية
          // ═══════════════════════════════════════════════════════════
          if (!drawingState.isDrawing)
            Positioned(
              bottom: 24,
              left: 16,
              right: 16,
              child: _selectedFieldId == null
                  ? _buildDashboardSummary(fieldsAsync)
                  : _buildFieldDetailCard(),
            ),

          // ═══════════════════════════════════════════════════════════
          // 6. أدوات الرسم (تظهر فقط في وضع الرسم)
          // ═══════════════════════════════════════════════════════════
          if (drawingState.isDrawing)
            Positioned(
              bottom: 24,
              left: 16,
              right: 16,
              child: _buildDrawingControls(drawingState),
            ),
        ],
      ),
    );
  }

  // ───────────────────────────────────────────────────────────────────
  // Widgets المساعدة
  // ───────────────────────────────────────────────────────────────────

  Widget _buildHeader(SyncStatus syncStatus, int pendingCount) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: SahoolProShadows.medium,
      ),
      child: Row(
        children: [
          // حالة الطقس المصغرة
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  const Icon(Icons.wb_sunny, size: 18, color: Colors.orange),
                  const SizedBox(width: 4),
                  Text(
                    '32°C',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                  ),
                ],
              ),
              Text(
                'صنعاء، اليمن',
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      color: SahoolProColors.textMedium,
                    ),
              ),
            ],
          ),

          const Spacer(),

          // شعار التطبيق
          Text(
            'SAHOOL OPS',
            style: TextStyle(
              color: SahoolProColors.textLight,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.5,
              fontSize: 12,
            ),
          ),

          const Spacer(),

          // حالة المزامنة
          _buildSyncBadge(syncStatus, pendingCount),
        ],
      ),
    );
  }

  Widget _buildSyncBadge(SyncStatus status, int count) {
    Color color;
    IconData icon;

    switch (status) {
      case SyncStatus.synced:
        color = SahoolProColors.statusSynced;
        icon = Icons.cloud_done;
        break;
      case SyncStatus.syncing:
        color = SahoolProColors.tractorYellow;
        icon = Icons.sync;
        break;
      case SyncStatus.offline:
        color = SahoolProColors.statusOffline;
        icon = Icons.cloud_off;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: color),
          if (count > 0) ...[
            const SizedBox(width: 4),
            Text(
              '$count',
              style: TextStyle(
                color: color,
                fontWeight: FontWeight.bold,
                fontSize: 13,
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildMapControls() {
    return Column(
      children: [
        _buildMapTool(Icons.add, 'تكبير', () {
          _mapController.move(
            _mapController.camera.center,
            _mapController.camera.zoom + 1,
          );
        }),
        const SizedBox(height: 8),
        _buildMapTool(Icons.remove, 'تصغير', () {
          _mapController.move(
            _mapController.camera.center,
            _mapController.camera.zoom - 1,
          );
        }),
        const SizedBox(height: 16),
        _buildMapTool(Icons.my_location, 'موقعي', () {
          // في التطبيق الحقيقي، نستخدم geolocator
        }, highlight: true),
        const SizedBox(height: 20),

        // زر إضافة حقل
        FloatingActionButton(
          heroTag: 'add_field',
          onPressed: () {
            ref.read(drawingProvider.notifier).startDrawing();
          },
          backgroundColor: SahoolProColors.johnGreen,
          child: const Icon(Icons.add_location_alt, size: 28),
        ),
      ],
    );
  }

  Widget _buildMapTool(IconData icon, String tooltip, VoidCallback onPressed,
      {bool highlight = false}) {
    return Container(
      decoration: BoxDecoration(
        color: highlight ? SahoolProColors.johnGreen : Colors.white,
        borderRadius: BorderRadius.circular(10),
        boxShadow: SahoolProShadows.small,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(10),
          child: SizedBox(
            width: 44,
            height: 44,
            child: Icon(
              icon,
              color: highlight ? Colors.white : SahoolProColors.textMedium,
              size: 22,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildLayerSelector() {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: SahoolProShadows.small,
      ),
      child: Column(
        children: _layers.asMap().entries.map((entry) {
          final index = entry.key;
          final layer = entry.value;
          final isSelected = index == _selectedLayerIndex;

          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: GestureDetector(
              onTap: () => setState(() => _selectedLayerIndex = index),
              child: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: isSelected
                      ? SahoolProColors.johnGreen.withOpacity(0.1)
                      : Colors.transparent,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  layer.icon,
                  color: isSelected
                      ? SahoolProColors.johnGreen
                      : SahoolProColors.textLight,
                  size: 22,
                ),
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildDashboardSummary(AsyncValue<List<dynamic>> fieldsAsync) {
    final fieldCount = fieldsAsync.valueOrNull?.length ?? 0;

    return Row(
      children: [
        Expanded(
          child: SahoolMetricsCard(
            label: 'المهام',
            value: '3',
            icon: Icons.playlist_add_check,
            activeColor: Colors.blue,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: SahoolMetricsCard(
            label: 'تنبيهات',
            value: '1',
            icon: Icons.warning_amber,
            activeColor: SahoolProColors.alertRed,
          ),
        ),
        const SizedBox(width: 10),
        Expanded(
          child: SahoolMetricsCard(
            label: 'الحقول',
            value: '$fieldCount',
            icon: Icons.grid_view,
            activeColor: SahoolProColors.johnGreen,
          ),
        ),
      ],
    );
  }

  Widget _buildFieldDetailCard() {
    // في التطبيق الحقيقي، نجلب البيانات من الـ ID
    return SahoolFieldStatusCard(
      fieldName: 'المزرعة الشمالية',
      cropType: 'قمح',
      areaHa: 2.4,
      ndvi: 0.72,
      isSynced: true,
      pendingTasks: 2,
      onClose: () => setState(() => _selectedFieldId = null),
    );
  }

  Widget _buildDrawingControls(DrawingState drawingState) {
    final areaHa = drawingState.isValid
        ? GeoUtils.calculateAreaHectares(drawingState.points)
        : 0.0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolProShadows.large,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // معلومات الرسم
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              _buildDrawingInfo(
                icon: Icons.location_on,
                label: '${drawingState.pointCount} نقاط',
                color: SahoolProColors.johnGreen,
              ),
              const SizedBox(width: 20),
              if (drawingState.isValid)
                _buildDrawingInfo(
                  icon: Icons.straighten,
                  label: '${areaHa.toStringAsFixed(2)} هكتار',
                  color: SahoolProColors.tractorYellow,
                ),
            ],
          ),
          const SizedBox(height: 16),

          // أزرار التحكم
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _buildDrawingButton(
                icon: Icons.close,
                label: 'إلغاء',
                color: SahoolProColors.alertRed,
                onPressed: () {
                  ref.read(drawingProvider.notifier).cancelDrawing();
                },
              ),
              _buildDrawingButton(
                icon: Icons.undo,
                label: 'تراجع',
                color: SahoolProColors.warningOrange,
                onPressed: drawingState.points.isEmpty
                    ? null
                    : () {
                        ref.read(drawingProvider.notifier).undoLastPoint();
                      },
              ),
              _buildDrawingButton(
                icon: Icons.check,
                label: 'حفظ',
                color: SahoolProColors.johnGreen,
                isPrimary: true,
                onPressed: drawingState.isValid
                    ? () => _saveField(drawingState.points)
                    : null,
              ),
            ],
          ),

          const SizedBox(height: 8),
          Text(
            drawingState.isValid
                ? 'اضغط حفظ لإنشاء الحقل'
                : 'انقر على الخريطة لإضافة ${3 - drawingState.pointCount} نقاط',
            style: TextStyle(
              fontSize: 12,
              color: SahoolProColors.textLight,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawingInfo({
    required IconData icon,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDrawingButton({
    required IconData icon,
    required String label,
    required Color color,
    VoidCallback? onPressed,
    bool isPrimary = false,
  }) {
    final isEnabled = onPressed != null;

    return GestureDetector(
      onTap: onPressed,
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.4,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: EdgeInsets.all(isPrimary ? 14 : 10),
              decoration: BoxDecoration(
                color: isPrimary && isEnabled ? color : color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: isPrimary && isEnabled ? Colors.white : color,
                size: isPrimary ? 26 : 22,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: isEnabled ? color : SahoolProColors.textLight,
                fontWeight: FontWeight.w600,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _saveField(List<LatLng> points) async {
    final fieldName = await showDialog<String>(
      context: context,
      builder: (context) => _FieldNameDialog(),
    );

    if (fieldName == null || fieldName.isEmpty) return;

    try {
      final repo = ref.read(fieldsRepoProvider);
      await repo.createField(
        tenantId: _tenantId,
        name: fieldName,
        boundary: points,
      );

      ref.read(drawingProvider.notifier).cancelDrawing();

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 8),
                Text('تم حفظ "$fieldName" بنجاح!'),
              ],
            ),
            backgroundColor: SahoolProColors.johnGreen,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في الحفظ: $e'),
            backgroundColor: SahoolProColors.alertRed,
          ),
        );
      }
    }
  }

  LatLng _calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return const LatLng(0, 0);
    double lat = 0, lng = 0;
    for (final p in points) {
      lat += p.latitude;
      lng += p.longitude;
    }
    return LatLng(lat / points.length, lng / points.length);
  }
}

class _MapLayer {
  final String name;
  final IconData icon;
  final String url;

  _MapLayer(this.name, this.icon, this.url);
}

class _FieldNameDialog extends StatefulWidget {
  @override
  State<_FieldNameDialog> createState() => _FieldNameDialogState();
}

class _FieldNameDialogState extends State<_FieldNameDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.grass, color: SahoolProColors.johnGreen),
          const SizedBox(width: 8),
          const Text('اسم الحقل'),
        ],
      ),
      content: TextField(
        controller: _controller,
        autofocus: true,
        decoration: const InputDecoration(
          hintText: 'أدخل اسم الحقل...',
          prefixIcon: Icon(Icons.edit),
        ),
        onSubmitted: (value) {
          if (value.isNotEmpty) Navigator.pop(context, value);
        },
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_controller.text.isNotEmpty) {
              Navigator.pop(context, _controller.text);
            }
          },
          child: const Text('حفظ'),
        ),
      ],
    );
  }
}
