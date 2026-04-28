import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart' hide Path;

import '../../../core/map/sahool_tile_provider.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/geo/geojson.dart';
import '../../polygon_editor/domain/polygon_editor_state.dart';
import '../../polygon_editor/ui/polygon_editor_widget.dart';
import '../../polygon_editor/utils/geo_utils.dart';

/// شاشة رسم حدود الحقل على الخريطة
///
/// تُفتح من [FieldFormScreen] لتمكين المستخدم من رسم
/// حدود الحقل بالضغط على الخريطة. تُعيد قائمة [LatLng]
/// عبر GoRouter عند الحفظ.
class FieldBoundaryDrawScreen extends ConsumerStatefulWidget {
  /// الحدود الحالية (إذا كانت في وضع التعديل)
  final List<LatLng> existingBoundary;

  const FieldBoundaryDrawScreen({
    super.key,
    this.existingBoundary = const [],
  });

  @override
  ConsumerState<FieldBoundaryDrawScreen> createState() =>
      _FieldBoundaryDrawScreenState();
}

class _FieldBoundaryDrawScreenState
    extends ConsumerState<FieldBoundaryDrawScreen> {
  late final MapController _mapController;
  late final PolygonEditorState _editorState;

  bool _isLocating = false;

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _editorState = PolygonEditorState();

    // تحميل الحدود الحالية (وضع التعديل)
    if (widget.existingBoundary.length >= 3) {
      _editorState.loadPolygon(widget.existingBoundary, closed: true);
    } else {
      _editorState.startDrawing();
    }

    // التنقل إلى موقع المستخدم تلقائياً
    WidgetsBinding.instance.addPostFrameCallback((_) => _goToMyLocation());
  }

  @override
  void dispose() {
    _mapController.dispose();
    _editorState.dispose();
    super.dispose();
  }

  Future<void> _goToMyLocation() async {
    if (!mounted) return;
    setState(() => _isLocating = true);
    try {
      final permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        await Geolocator.requestPermission();
      }
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );
      if (mounted) {
        _mapController.move(
          LatLng(position.latitude, position.longitude),
          16,
        );
      }
    } catch (e) {
      AppLogger.w(
        'Could not get current location',
        tag: 'FieldBoundaryDraw',
        data: {'error': e.toString()},
      );
    } finally {
      if (mounted) setState(() => _isLocating = false);
    }
  }

  void _onMapTap(TapPosition tapPosition, LatLng point) {
    if (!_editorState.isDrawing) return;
    _editorState.addPoint(point);
  }

  void _save() {
    final points = List<LatLng>.from(_editorState.points);

    // Full geometric validation before returning
    final error = GeoJson.validatePolygon(points);
    if (error != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(error),
          backgroundColor: Colors.red.shade700,
          duration: const Duration(seconds: 4),
        ),
      );
      return;
    }

    context.pop(points);
  }

  void _cancel() {
    context.pop(null);
  }

  double get _areaHa =>
      _editorState.pointCount >= 3
          ? GeoUtils.calculateAreaHectares(_editorState.points)
          : 0;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // ─── الخريطة الأساسية ───────────────────────────────────
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: const LatLng(15.3694, 44.1910),
              initialZoom: 14,
              onTap: _onMapTap,
            ),
            children: [
              TileLayer(
                urlTemplate:
                    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                userAgentPackageName: 'com.sahool.field',
                maxZoom: 22,
                tileProvider: SahoolTileProvider(),
              ),
              // ─── محرر المضلعات ──────────────────────────────────
              ListenableBuilder(
                listenable: _editorState,
                builder: (context, _) {
                  return PolygonEditorWidget(
                    mapController: _mapController,
                    editorState: _editorState,
                    polygonColor: SahoolColors.success,
                  );
                },
              ),
            ],
          ),

          // ─── شريط الأدوات العلوي ────────────────────────────────
          _buildTopBar(),

          // ─── شريط المعلومات والأزرار السفلي ─────────────────────
          ListenableBuilder(
            listenable: _editorState,
            builder: (context, _) => _buildBottomBar(),
          ),

          // ─── زر الموقع الحالي ────────────────────────────────────
          _buildLocationButton(),
        ],
      ),
    );
  }

  Widget _buildTopBar() {
    return Positioned(
      top: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        child: Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.black.withValues(alpha: 0.75),
            borderRadius: BorderRadius.circular(16),
          ),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.arrow_back, color: Colors.white),
                onPressed: _cancel,
                tooltip: 'إلغاء',
              ),
              const Expanded(
                child: Text(
                  'رسم حدود الحقل',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              IconButton(
                icon: const Icon(Icons.delete_outline, color: Colors.redAccent),
                onPressed: _editorState.hasPoints
                    ? () => _editorState.clear()
                    : null,
                tooltip: 'مسح الكل',
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildBottomBar() {
    final pointCount = _editorState.pointCount;
    final isValid = pointCount >= 3;

    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      child: SafeArea(
        child: Container(
          margin: const EdgeInsets.all(12),
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Colors.black.withValues(alpha: 0.8),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // ─── معلومات المضلع ──────────────────────────────
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  _infoChip(
                    Icons.location_on,
                    '$pointCount نقطة',
                    SahoolColors.info,
                  ),
                  if (isValid) ...[
                    const SizedBox(width: 12),
                    _infoChip(
                      Icons.straighten,
                      '${_areaHa.toStringAsFixed(2)} هكتار',
                      SahoolColors.success,
                    ),
                  ],
                ],
              ),
              const SizedBox(height: 14),

              // ─── أزرار التحكم ────────────────────────────────
              Row(
                children: [
                  // تراجع
                  _ActionButton(
                    icon: Icons.undo,
                    label: 'تراجع',
                    color: SahoolColors.warning,
                    onPressed: _editorState.canUndo
                        ? () => _editorState.undo()
                        : null,
                  ),
                  const SizedBox(width: 8),
                  // إعادة
                  _ActionButton(
                    icon: Icons.redo,
                    label: 'إعادة',
                    color: SahoolColors.warning,
                    onPressed: _editorState.canRedo
                        ? () => _editorState.redo()
                        : null,
                  ),
                  const Spacer(),
                  // حفظ الحدود
                  ElevatedButton.icon(
                    onPressed: isValid ? _save : null,
                    icon: const Icon(Icons.check_circle_outline),
                    label: const Text('تأكيد الحدود'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor:
                          isValid ? SahoolColors.success : Colors.grey,
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(
                          horizontal: 20, vertical: 12),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 10),

              // ─── تعليمات ─────────────────────────────────────
              Text(
                isValid
                    ? 'اضغط "تأكيد الحدود" لحفظ مساحة الحقل'
                    : 'انقر على الخريطة لإضافة ${3 - pointCount} نقاط على الأقل',
                textAlign: TextAlign.center,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[400],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLocationButton() {
    return Positioned(
      right: 16,
      bottom: 200,
      child: FloatingActionButton.small(
        heroTag: 'my_location_fab',
        onPressed: _isLocating ? null : _goToMyLocation,
        backgroundColor: Colors.white,
        foregroundColor: SahoolColors.primary,
        tooltip: 'موقعي الحالي',
        child: _isLocating
            ? const SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2),
              )
            : const Icon(Icons.my_location),
      ),
    );
  }

  Widget _infoChip(IconData icon, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 15, color: color),
          const SizedBox(width: 5),
          Text(
            label,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }
}

/// زر إجراء في شريط الأدوات السفلي
class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback? onPressed;

  const _ActionButton({
    required this.icon,
    required this.label,
    required this.color,
    this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    final enabled = onPressed != null;
    return Opacity(
      opacity: enabled ? 1 : 0.4,
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
          decoration: BoxDecoration(
            color: color.withValues(alpha: 0.12),
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: color.withValues(alpha: 0.3)),
          ),
          child: Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 18, color: color),
              const SizedBox(width: 4),
              Text(label,
                  style: TextStyle(
                      color: color,
                      fontSize: 12,
                      fontWeight: FontWeight.w600)),
            ],
          ),
        ),
      ),
    );
  }
}
