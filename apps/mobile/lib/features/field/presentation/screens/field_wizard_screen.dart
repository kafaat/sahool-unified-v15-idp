import 'dart:math';

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../farm/data/farm_entity.dart';
import '../../../farm/domain/farm_providers.dart';
import '../../domain/field_wizard_notifier.dart';
import '../../domain/field_wizard_state.dart';

enum _DrawMode { polygon, rectangle, circle }

/// معالج إنشاء حقل جديد - 6 خطوات
class FieldWizardScreen extends ConsumerStatefulWidget {
  const FieldWizardScreen({super.key});

  @override
  ConsumerState<FieldWizardScreen> createState() => _FieldWizardScreenState();
}

class _FieldWizardScreenState extends ConsumerState<FieldWizardScreen> {
  // نقاط المضلع المرسومة في الخطوة الأولى
  final List<LatLng> _points = [];
  final MapController _mapController = MapController();

  _DrawMode _drawMode = _DrawMode.polygon;
  LatLng? _firstCorner; // للمستطيل والدائرة: النقطة الأولى
  bool _polygonClosed = false; // المضلع مغلق (تم النقر على النقطة الأولى)

  // حساب مساحة المضلع بالهكتار (صيغة الحبال)
  double _calcAreaHa(List<LatLng> pts) {
    if (pts.length < 3) return 0;
    double area = 0;
    for (int i = 0; i < pts.length; i++) {
      final j = (i + 1) % pts.length;
      area += pts[i].longitude * pts[j].latitude;
      area -= pts[j].longitude * pts[i].latitude;
    }
    final centerLat =
        pts.map((p) => p.latitude).reduce((a, b) => a + b) / pts.length;
    return (area.abs() / 2) *
        111320 *
        111320 *
        cos(centerLat * pi / 180) /
        10000;
  }

  void _onMapTap(LatLng point) {
    if (_drawMode == _DrawMode.rectangle) {
      // Rectangle mode: 2-click bbox
      if (_firstCorner == null) {
        setState(() => _firstCorner = point);
      } else {
        final a = _firstCorner!;
        final b = point;
        final pts = [
          a,
          LatLng(a.latitude, b.longitude),
          b,
          LatLng(b.latitude, a.longitude),
        ];
        setState(() {
          _points..clear()..addAll(pts);
          _firstCorner = null;
        });
        final area = _calcAreaHa(_points);
        ref.read(fieldWizardProvider.notifier).updatePolygon(List.from(_points), area);
      }
    } else if (_drawMode == _DrawMode.circle) {
      // Circle mode: first click = center, second click = radius point
      if (_firstCorner == null) {
        setState(() => _firstCorner = point);
      } else {
        final center = _firstCorner!;
        final radiusM = _haversineDistance(center, point);
        final circlePts = _circleToPolygon(center, radiusM);
        setState(() {
          _points..clear()..addAll(circlePts);
          _firstCorner = null;
        });
        final area = _calcAreaHa(_points);
        ref.read(fieldWizardProvider.notifier).updatePolygon(List.from(_points), area);
      }
    } else {
      // Polygon mode: multipoint — click to add vertices, click near first to close
      if (_polygonClosed) return; // shape already closed, ignore taps
      if (_points.length >= 3) {
        final first = _points.first;
        final distDeg = (point.latitude - first.latitude).abs() +
            (point.longitude - first.longitude).abs();
        if (distDeg < 0.0004) {
          // Tapped near first vertex → close polygon
          setState(() => _polygonClosed = true);
          return;
        }
      }
      setState(() {
        _firstCorner = null;
        _points.add(point);
      });
      if (_points.length >= 3) {
        final area = _calcAreaHa(_points);
        ref.read(fieldWizardProvider.notifier).updatePolygon(List.from(_points), area);
      }
    }
  }

  void _clearPoints() {
    setState(() {
      _points.clear();
      _firstCorner = null;
      _polygonClosed = false;
    });
    ref.read(fieldWizardProvider.notifier).updatePolygon([], 0.0);
  }

  void _removeLastPoint() {
    if (_drawMode == _DrawMode.rectangle || _drawMode == _DrawMode.circle) {
      _clearPoints();
    } else {
      // Polygon: if closed, re-open first (don't remove a vertex)
      if (_polygonClosed) {
        setState(() => _polygonClosed = false);
        return;
      }
      if (_points.isEmpty) return;
      setState(() => _points.removeLast());
      if (_points.length >= 3) {
        ref.read(fieldWizardProvider.notifier).updatePolygon(List.from(_points), _calcAreaHa(_points));
      } else {
        ref.read(fieldWizardProvider.notifier).updatePolygon([], 0.0);
      }
    }
  }

  /// Haversine distance in metres between two LatLng points
  double _haversineDistance(LatLng a, LatLng b) {
    const R = 6371000.0;
    final lat1 = a.latitude * pi / 180;
    final lat2 = b.latitude * pi / 180;
    final dLat = (b.latitude - a.latitude) * pi / 180;
    final dLng = (b.longitude - a.longitude) * pi / 180;
    final sinHalfDLat = sin(dLat / 2);
    final sinHalfDLng = sin(dLng / 2);
    final c = 2 *
        asin(sqrt(sinHalfDLat * sinHalfDLat +
            cos(lat1) * cos(lat2) * sinHalfDLng * sinHalfDLng));
    return R * c;
  }

  /// Approximate a circle as a 64-vertex polygon
  List<LatLng> _circleToPolygon(LatLng center, double radiusM,
      {int sides = 64}) {
    final List<LatLng> pts = [];
    for (int i = 0; i < sides; i++) {
      final angle = 2 * pi * i / sides;
      final dLat = radiusM * cos(angle) / 111320;
      final dLng = radiusM *
          sin(angle) /
          (111320 * cos(center.latitude * pi / 180));
      pts.add(LatLng(center.latitude + dLat, center.longitude + dLng));
    }
    return pts;
  }

  void _flyToFarm(FarmEntity farm) {
    double lat = farm.centerLat;
    double lng = farm.centerLng;
    final zoom = (farm.zoom ?? 14).toDouble();

    if (lat == 0.0 && lng == 0.0) {
      final bbox = farm.bbox;
      if (bbox != null && bbox.length == 4) {
        lat = (bbox[1] + bbox[3]) / 2;
        lng = (bbox[0] + bbox[2]) / 2;
      }
    }

    if (lat != 0.0 || lng != 0.0) {
      _mapController.move(LatLng(lat, lng), zoom);
    }
  }

  void _onNextStep() {
    final ok = ref.read(fieldWizardProvider.notifier).nextStep();
    if (!ok) {
      // الخطأ يظهر من الحالة — لا حاجة لإجراء إضافي
    }
  }

  void _onPrevStep() {
    ref.read(fieldWizardProvider.notifier).prevStep();
  }

  Future<void> _submit() async {
    final notifier = ref.read(fieldWizardProvider.notifier);
    final ok = await notifier.submit(context);
    if (ok && mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('تم إنشاء الحقل بنجاح'),
          backgroundColor: SahoolColors.success,
        ),
      );
      Navigator.of(context).pop(true);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(fieldWizardProvider);

    // Step 0: full-screen satellite map
    if (state.currentStep == 0) {
      return _buildFullScreenMapStep(state);
    }

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: SahoolColors.background,
        appBar: AppBar(
          title: const Text('إنشاء حقل جديد'),
          centerTitle: true,
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          titleTextStyle: const TextStyle(
            color: Colors.white,
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        body: Column(
          children: [
            _buildStepIndicator(state.currentStep),
            if (state.error != null)
              Container(
                width: double.infinity,
                color: SahoolColors.danger.withValues(alpha: 0.1),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline, color: SahoolColors.danger, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.error!,
                        style: const TextStyle(color: SahoolColors.danger, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: _buildStepContent(state),
              ),
            ),
            _buildNavigationButtons(state),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // الخريطة الشاملة للشاشة — الخطوة 1
  // ─────────────────────────────────────────────────────────────

  Widget _buildFullScreenMapStep(FieldWizardState state) {
    final farmsAsync = ref.watch(farmsListProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: Colors.black,
        body: Stack(
          children: [
            // ── Satellite map fills the screen ────────────────────
            Positioned.fill(child: _buildSatelliteMap()),

            // ── Top overlay: back button, status, stepper, farm selector ──
            Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: SafeArea(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Padding(
                      padding: const EdgeInsets.fromLTRB(8, 4, 8, 4),
                      child: Row(
                        children: [
                          _mapOverlayButton(
                            icon: Icons.arrow_back,
                            onTap: () => Navigator.of(context).pop(),
                          ),
                          const SizedBox(width: 8),
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              decoration: BoxDecoration(
                                color: Colors.black.withValues(alpha: 0.65),
                                borderRadius: BorderRadius.circular(10),
                              ),
                              child: Text(
                                _drawMode == _DrawMode.rectangle
                                    ? (_firstCorner == null
                                        ? 'انقر لتحديد الزاوية الأولى'
                                        : _points.isNotEmpty
                                            ? 'المساحة: ${state.area.toStringAsFixed(2)} هـ'
                                            : 'انقر لتحديد الزاوية المقابلة')
                                    : (_points.isEmpty
                                        ? 'انقر لإضافة نقاط حدود الحقل'
                                        : _points.length < 3
                                            ? 'أضف نقطتين أخريين على الأقل (${_points.length}/3)'
                                            : 'المساحة: ${state.area.toStringAsFixed(2)} هـ'),
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontWeight: FontWeight.bold,
                                  fontSize: 15,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    _buildStepIndicatorOverlay(state.currentStep),
                    // Farm selector
                    Padding(
                      padding: const EdgeInsets.fromLTRB(8, 4, 8, 0),
                      child: farmsAsync.maybeWhen(
                        data: (farms) => farms.isEmpty
                            ? const SizedBox.shrink()
                            : _buildFarmOverlayChip(farms, state),
                        orElse: () => const SizedBox.shrink(),
                      ),
                    ),
                  ],
                ),
              ),
            ),

            // ── Error message ─────────────────────────────────────
            if (state.error != null)
              Positioned(
                top: 230,
                left: 8,
                right: 8,
                child: Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: SahoolColors.danger.withValues(alpha: 0.9),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error_outline,
                          color: Colors.white, size: 18),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          state.error!,
                          style: const TextStyle(
                              color: Colors.white, fontSize: 13),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

            // ── Drawing toolbar (center-top, below safe area) ─────
            Positioned(
              top: 210,
              left: 0,
              right: 0,
              child: Center(child: _buildDrawingToolbar()),
            ),

            // ── Bottom panel ──────────────────────────────────────
            Positioned(
              bottom: 0,
              left: 0,
              right: 0,
              child: SafeArea(
                child: _buildMapBottomPanel(state),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _mapOverlayButton({required IconData icon, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        width: 40,
        height: 40,
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.65),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(icon, color: Colors.white, size: 22),
      ),
    );
  }

  Widget _buildStepIndicatorOverlay(int currentStep) {
    final steps = ['الموقع', 'المعلومات', 'الموسم', 'المحصول', 'التربة', 'الري'];
    return Container(
      margin: const EdgeInsets.fromLTRB(8, 0, 8, 4),
      padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.6),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: List.generate(steps.length, (i) {
          final isCompleted = i < currentStep;
          final isActive = i == currentStep;
          return Expanded(
            child: GestureDetector(
              onTap: isCompleted
                  ? () => ref.read(fieldWizardProvider.notifier).goToStep(i)
                  : null,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isCompleted
                          ? SahoolColors.primary
                          : isActive
                              ? SahoolColors.secondary
                              : Colors.white24,
                    ),
                    child: Center(
                      child: isCompleted
                          ? const Icon(Icons.check, color: Colors.white, size: 14)
                          : Text(
                              '${i + 1}',
                              style: TextStyle(
                                color: isActive ? Colors.white : Colors.white54,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ),
                  const SizedBox(height: 3),
                  Text(
                    steps[i],
                    style: TextStyle(
                      fontSize: 9,
                      color: isActive || isCompleted ? Colors.white : Colors.white54,
                      fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          );
        }),
      ),
    );
  }

  Widget _buildFarmOverlayChip(List<FarmEntity> farms, FieldWizardState state) {
    final selectedFarm = farms.cast<FarmEntity?>().firstWhere(
      (f) => f!.id == state.farmId,
      orElse: () => null,
    );
    final label = selectedFarm != null
        ? (selectedFarm.nameAr ?? selectedFarm.name)
        : 'اختر المزرعة';

    return GestureDetector(
      onTap: () => showModalBottomSheet<void>(
        context: context,
        backgroundColor: const Color(0xFF1E1E1E),
        shape: const RoundedRectangleBorder(
          borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
        ),
        builder: (_) => Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'اختر المزرعة',
                style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16),
              ),
            ),
            ...farms.map((f) => ListTile(
                  title: Text(
                    f.nameAr ?? f.name,
                    style: const TextStyle(color: Colors.white),
                  ),
                  leading: const Icon(Icons.agriculture, color: SahoolColors.primary),
                  selected: f.id == state.farmId,
                  selectedColor: SahoolColors.primary,
                  onTap: () {
                    ref.read(fieldWizardProvider.notifier).updateFarmId(f.id);
                    Navigator.pop(context);
                    _flyToFarm(f);
                  },
                )),
            const SizedBox(height: 16),
          ],
        ),
      ),
      child: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.72),
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: state.farmId != null
                ? SahoolColors.primary
                : Colors.white30,
            width: state.farmId != null ? 1.5 : 1.0,
          ),
        ),
        child: Row(
          children: [
            Icon(
              Icons.agriculture,
              color: state.farmId != null ? SahoolColors.primary : Colors.white54,
              size: 20,
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Text(
                label,
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 15,
                  fontWeight: state.farmId != null
                      ? FontWeight.bold
                      : FontWeight.normal,
                ),
              ),
            ),
            const Icon(Icons.expand_more, color: Colors.white54, size: 20),
          ],
        ),
      ),
    );
  }

  Widget _buildDrawingToolbar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.75),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.white24),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _drawToolButton(
            icon: Icons.polyline_rounded,
            label: 'مضلع',
            mode: _DrawMode.polygon,
          ),
          const SizedBox(width: 6),
          _drawToolButton(
            icon: Icons.crop_square_rounded,
            label: 'مستطيل',
            mode: _DrawMode.rectangle,
          ),
          const SizedBox(width: 6),
          _drawToolButton(
            icon: Icons.circle_outlined,
            label: 'دائرة',
            mode: _DrawMode.circle,
          ),
          if (_points.isNotEmpty || _firstCorner != null) ...[
            const SizedBox(width: 6),
            const SizedBox(
              height: 28,
              child: VerticalDivider(color: Colors.white24, width: 1),
            ),
            const SizedBox(width: 6),
            GestureDetector(
              onTap: _removeLastPoint,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.orange.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.withValues(alpha: 0.5)),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.undo_rounded, color: Colors.orange, size: 16),
                    SizedBox(width: 4),
                    Text('تراجع',
                        style: TextStyle(color: Colors.orange, fontSize: 11)),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 6),
            GestureDetector(
              onTap: _clearPoints,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: SahoolColors.danger.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(8),
                  border:
                      Border.all(color: SahoolColors.danger.withValues(alpha: 0.5)),
                ),
                child: const Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.delete_outline, color: SahoolColors.danger, size: 16),
                    SizedBox(width: 4),
                    Text('مسح',
                        style: TextStyle(color: SahoolColors.danger, fontSize: 11)),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _drawToolButton({
    required IconData icon,
    required String label,
    required _DrawMode mode,
  }) {
    final isActive = _drawMode == mode;
    return GestureDetector(
      onTap: () {
        if (_drawMode != mode) {
          _clearPoints();
          setState(() => _drawMode = mode);
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive
              ? SahoolColors.primary
              : Colors.white.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(
            color: isActive ? SahoolColors.primary : Colors.white30,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon,
                color: isActive ? Colors.white : Colors.white70, size: 16),
            const SizedBox(width: 4),
            Text(
              label,
              style: TextStyle(
                color: isActive ? Colors.white : Colors.white70,
                fontSize: 11,
                fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMapBottomPanel(FieldWizardState state) {
    final String statusText;
    if (_drawMode == _DrawMode.rectangle) {
      if (_firstCorner != null) {
        statusText = 'انقر لتحديد الزاوية المقابلة';
      } else if (_points.length >= 3) {
        statusText = '✓ المساحة: ${state.area.toStringAsFixed(2)} هـ';
      } else {
        statusText = 'انقر لتحديد الزاوية الأولى للمستطيل';
      }
    } else if (_drawMode == _DrawMode.circle) {
      if (_firstCorner != null) {
        statusText = 'انقر لتحديد نصف القطر';
      } else if (_points.length >= 3) {
        statusText = '✓ الدائرة: ${state.area.toStringAsFixed(2)} هـ';
      } else {
        statusText = 'انقر لتحديد مركز الدائرة';
      }
    } else {
      if (_points.isEmpty) {
        statusText = 'انقر على الخريطة لإضافة نقاط الحدود';
      } else if (_points.length < 3) {
        statusText = 'أضف ${3 - _points.length} نقاط إضافية على الأقل';
      } else if (_polygonClosed) {
        statusText = '✓ المضلع مغلق — المساحة: ${state.area.toStringAsFixed(2)} هـ';
      } else {
        statusText = '${_points.length} نقطة — انقر على النقطة الأولى لإغلاق المضلع';
      }
    }

    return Container(
      padding: const EdgeInsets.fromLTRB(12, 10, 12, 12),
      decoration: BoxDecoration(
        color: Colors.black.withValues(alpha: 0.72),
        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: Colors.white10,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(
                  _points.length >= 3
                      ? Icons.check_circle_outline
                      : Icons.edit_location_alt,
                  color: _points.length >= 3
                      ? SahoolColors.primary
                      : Colors.white54,
                  size: 16,
                ),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    statusText,
                    style: TextStyle(
                      color: _points.length >= 3
                          ? SahoolColors.primary
                          : Colors.white70,
                      fontSize: 12,
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: _onNextStep,
              icon: const Icon(Icons.arrow_back),
              label: const Text('التالي'),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // شريط التقدم
  // ─────────────────────────────────────────────────────────────

  Widget _buildStepIndicator(int currentStep) {
    final steps = ['الموقع', 'المعلومات', 'الموسم', 'المحصول', 'التربة', 'الري'];
    return Container(
      color: Theme.of(context).colorScheme.surface,
      padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
      child: Row(
        children: List.generate(steps.length, (i) {
          final isCompleted = i < currentStep;
          final isActive = i == currentStep;
          return Expanded(
            child: GestureDetector(
              onTap: isCompleted
                  ? () => ref
                      .read(fieldWizardProvider.notifier)
                      .goToStep(i)
                  : null,
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 28,
                    height: 28,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isCompleted
                          ? SahoolColors.primary
                          : isActive
                              ? SahoolColors.secondary
                              : Colors.grey[700],
                    ),
                    child: Center(
                      child: isCompleted
                          ? const Icon(Icons.check,
                              color: Colors.white, size: 16)
                          : Text(
                              '${i + 1}',
                              style: TextStyle(
                                color: isActive
                                    ? Colors.white
                                    : Colors.grey[400],
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    steps[i],
                    style: TextStyle(
                      fontSize: 10,
                      color: isActive
                          ? SahoolColors.primary
                          : isCompleted
                              ? SahoolColors.primary
                              : Colors.grey[400],
                      fontWeight: isActive
                          ? FontWeight.bold
                          : FontWeight.normal,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          );
        }),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // أزرار التنقل
  // ─────────────────────────────────────────────────────────────

  Widget _buildNavigationButtons(FieldWizardState state) {
    final isLast = state.currentStep == 5;
    return Container(
      color: Theme.of(context).colorScheme.surface,
      padding: const EdgeInsets.fromLTRB(16, 8, 16, 16),
      child: Row(
        children: [
          if (state.currentStep > 0)
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _onPrevStep,
                icon: const Icon(Icons.arrow_forward),
                label: const Text('رجوع'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: SahoolColors.primary,
                  side: const BorderSide(color: SahoolColors.primary),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                ),
              ),
            ),
          if (state.currentStep > 0) const SizedBox(width: 12),
          Expanded(
            flex: 2,
            child: ElevatedButton.icon(
              onPressed: state.isSubmitting
                  ? null
                  : isLast
                      ? _submit
                      : _onNextStep,
              icon: state.isSubmitting
                  ? const SizedBox(
                      width: 18,
                      height: 18,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : Icon(isLast ? Icons.save : Icons.arrow_back),
              label: Text(isLast ? 'حفظ الحقل' : 'التالي'),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolColors.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // توزيع الخطوات
  // ─────────────────────────────────────────────────────────────

  Widget _buildStepContent(FieldWizardState state) {
    switch (state.currentStep) {
      case 0:
        return _buildStep1Location(state);
      case 1:
        return _buildStep2Info(state);
      case 2:
        return _buildStep3Season(state);
      case 3:
        return _buildStep4Crop(state);
      case 4:
        return _buildStep5Soil(state);
      case 5:
        return _buildStep6Irrigation(state);
      default:
        return const SizedBox.shrink();
    }
  }

  // ─────────────────────────────────────────────────────────────
  // الخطوة 1: الموقع
  // ─────────────────────────────────────────────────────────────

  Widget _buildStep1Location(FieldWizardState state) {
    final farmsAsync = ref.watch(farmsListProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('اختر المزرعة', Icons.agriculture),
        const SizedBox(height: 8),
        farmsAsync.when(
          loading: () =>
              const Center(child: CircularProgressIndicator()),
          error: (_, __) => _noFarmsMessage(),
          data: (farms) {
            if (farms.isEmpty) return _noFarmsMessage();
            return DropdownButtonFormField<String>(
              value: state.farmId,
              decoration: const InputDecoration(
                labelText: 'المزرعة',
                prefixIcon: Icon(Icons.agriculture),
              ),
              hint: const Text('اختر المزرعة'),
              items: farms
                  .map((f) => DropdownMenuItem(
                        value: f.id,
                        child: Text(f.nameAr ?? f.name),
                      ))
                  .toList(),
              onChanged: (v) {
                if (v != null) {
                  ref
                      .read(fieldWizardProvider.notifier)
                      .updateFarmId(v);
                }
              },
            );
          },
        ),
        const SizedBox(height: 20),
        _sectionTitle('ارسم حدود الحقل', Icons.edit_location_alt),
        const SizedBox(height: 4),
        Text(
          'انقر على الخريطة لإضافة نقاط الحدود',
          style: TextStyle(color: Colors.grey[600], fontSize: 13),
        ),
        const SizedBox(height: 8),
        _buildMap(),
        const SizedBox(height: 8),
        Row(
          children: [
            TextButton.icon(
              onPressed: _clearPoints,
              icon: const Icon(Icons.clear, color: SahoolColors.danger),
              label: const Text(
                'مسح الحدود',
                style: TextStyle(color: SahoolColors.danger),
              ),
            ),
            const Spacer(),
            if (_points.isNotEmpty)
              TextButton.icon(
                onPressed: _removeLastPoint,
                icon: const Icon(Icons.undo, color: SahoolColors.primary),
                label: const Text('تراجع'),
              ),
          ],
        ),
        if (_points.length >= 3)
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: SahoolColors.primary.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                  color: SahoolColors.primary.withValues(alpha: 0.3)),
            ),
            child: Row(
              children: [
                const Icon(Icons.straighten,
                    color: SahoolColors.primary, size: 20),
                const SizedBox(width: 8),
                Text(
                  'المساحة المحسوبة: ${state.area.toStringAsFixed(2)} هـ',
                  style: const TextStyle(
                    color: SahoolColors.primary,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          )
        else
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Text(
              'النقاط المضافة: ${_points.length} / 3 على الأقل',
              style: TextStyle(color: Colors.grey[500], fontSize: 12),
            ),
          ),
      ],
    );
  }

  Widget _noFarmsMessage() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.orange.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.orange.withValues(alpha: 0.3)),
      ),
      child: const Row(
        children: [
          Icon(Icons.warning_amber_rounded, color: Colors.orange),
          SizedBox(width: 8),
          Expanded(
            child: Text(
              'لا توجد مزارع — أضف مزرعة أولاً',
              style: TextStyle(color: Colors.orange),
            ),
          ),
        ],
      ),
    );
  }

  /// الخريطة الشاملة للشاشة — بلاط القمر الصناعي
  Widget _buildSatelliteMap() {
    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: const LatLng(15.5, 44.0),
        initialZoom: 7,
        onTap: (_, latlng) => _onMapTap(latlng),
      ),
      children: [
        TileLayer(
          urlTemplate:
              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
          userAgentPackageName: 'com.sahool.app',
          maxNativeZoom: 18,
        ),
        // ── Filled polygon / circle (≥3 points) ─────────────────
        if (_points.length >= 3)
          PolygonLayer(
            polygons: [
              Polygon(
                points: _points,
                color: (_drawMode == _DrawMode.circle
                        ? Colors.blue
                        : SahoolColors.primary)
                    .withValues(alpha: 0.22),
                borderColor: _drawMode == _DrawMode.circle
                    ? Colors.blue
                    : SahoolColors.primary,
                borderStrokeWidth: 2.5,
              ),
            ],
          ),
        // ── Polyline while drawing polygon (connects dots live) ──
        if (_drawMode == _DrawMode.polygon && _points.length >= 2)
          PolylineLayer(
            polylines: [
              Polyline(
                points: [
                  ..._points,
                  if (_polygonClosed) _points.first,
                ],
                color: SahoolColors.primary.withValues(alpha: 0.7),
                strokeWidth: 2.0,
              ),
            ],
          ),
        // ── Vertex markers ───────────────────────────────────────
        if (_points.isNotEmpty && _drawMode != _DrawMode.circle)
          MarkerLayer(
            markers: _drawMode == _DrawMode.rectangle
                ? [
                    _cornerMarker(_points[0], 'A'),
                    _cornerMarker(_points[2], 'B'),
                  ]
                : _points.asMap().entries.map((entry) {
                    final i = entry.key;
                    final p = entry.value;
                    // First vertex gets a special "tap-to-close" style when ≥3 pts
                    final isFirst = i == 0;
                    final canClose = isFirst && _points.length >= 3 && !_polygonClosed;
                    final size = canClose ? 32.0 : 26.0;
                    return Marker(
                      point: p,
                      width: size,
                      height: size,
                      child: Container(
                        decoration: BoxDecoration(
                          shape: BoxShape.circle,
                          color: _polygonClosed
                              ? Colors.green
                              : canClose
                                  ? Colors.green.shade600
                                  : isFirst
                                      ? Colors.orange
                                      : SahoolColors.primary,
                          border: Border.all(
                            color: Colors.white,
                            width: canClose ? 3 : 2,
                          ),
                          boxShadow: canClose
                              ? [
                                  BoxShadow(
                                    color: Colors.green.withValues(alpha: 0.5),
                                    blurRadius: 8,
                                    spreadRadius: 2,
                                  )
                                ]
                              : [],
                        ),
                        child: Center(
                          child: canClose
                              ? const Icon(Icons.close_rounded,
                                  color: Colors.white, size: 14)
                              : Text(
                                  '${i + 1}',
                                  style: const TextStyle(
                                      color: Colors.white,
                                      fontSize: 9,
                                      fontWeight: FontWeight.bold),
                                ),
                        ),
                      ),
                    );
                  }).toList(),
          ),
        // ── Circle center marker (waiting for radius click) ──────
        if (_drawMode == _DrawMode.circle && _firstCorner != null && _points.isEmpty)
          MarkerLayer(
            markers: [
              Marker(
                point: _firstCorner!,
                width: 34,
                height: 34,
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.blue.withValues(alpha: 0.9),
                    border: Border.all(color: Colors.white, width: 2),
                    boxShadow: [
                      BoxShadow(
                        color: Colors.blue.withValues(alpha: 0.4),
                        blurRadius: 8,
                        spreadRadius: 2,
                      )
                    ],
                  ),
                  child: const Icon(Icons.add_location_alt_rounded,
                      color: Colors.white, size: 18),
                ),
              ),
            ],
          ),
        // ── Rectangle first-corner pending marker ────────────────
        if (_drawMode == _DrawMode.rectangle && _firstCorner != null)
          MarkerLayer(
            markers: [
              Marker(
                point: _firstCorner!,
                width: 30,
                height: 30,
                child: Container(
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    color: Colors.orange.withValues(alpha: 0.9),
                    border: Border.all(color: Colors.white, width: 2),
                  ),
                  child: const Icon(Icons.add, color: Colors.white, size: 16),
                ),
              ),
            ],
          ),
      ],
    );
  }

  /// خريطة مدمجة (350px) — للخطوة الأولى في المسار العادي (fallback)
  Widget _buildMap() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: SizedBox(
        height: 350,
        child: _buildSatelliteMap(),
      ),
    );
  }

  Marker _cornerMarker(LatLng point, String label) {
    return Marker(
      point: point,
      width: 26,
      height: 26,
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: SahoolColors.primary,
          border: Border.all(color: Colors.white, width: 2),
        ),
        child: Center(
          child: Text(
            label,
            style: const TextStyle(
                color: Colors.white,
                fontSize: 9,
                fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // الخطوة 2: المعلومات
  // ─────────────────────────────────────────────────────────────

  Widget _buildStep2Info(FieldWizardState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('معلومات الحقل', Icons.info_outline),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: state.name,
          decoration: const InputDecoration(
            labelText: 'اسم الحقل *',
            hintText: 'أدخل اسم الحقل',
            prefixIcon: Icon(Icons.label_outline),
          ),
          textDirection: TextDirection.rtl,
          onChanged: (v) =>
              ref.read(fieldWizardProvider.notifier).updateName(v),
        ),
        const SizedBox(height: 16),
        Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surfaceContainerHighest,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[700]!),
          ),
          child: Row(
            children: [
              const Icon(Icons.straighten,
                  color: SahoolColors.primary, size: 22),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'المساحة',
                    style: TextStyle(
                      color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
                      fontSize: 12,
                    ),
                  ),
                  Text(
                    '${state.area.toStringAsFixed(2)} هكتار',
                    style: const TextStyle(
                      color: SahoolColors.primary,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────────
  // الخطوة 3: الموسم
  // ─────────────────────────────────────────────────────────────

  Widget _buildStep3Season(FieldWizardState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('الموسم الزراعي (اختياري)', Icons.calendar_today),
        const SizedBox(height: 16),
        TextFormField(
          initialValue: state.seasonName,
          decoration: const InputDecoration(
            labelText: 'اسم الموسم',
            hintText: 'موسم قمح 2024',
            prefixIcon: Icon(Icons.label_outline),
          ),
          textDirection: TextDirection.rtl,
          onChanged: (v) =>
              ref.read(fieldWizardProvider.notifier).updateSeasonName(v),
        ),
        const SizedBox(height: 16),
        _buildDatePickerField(
          label: 'تاريخ الزراعة',
          icon: Icons.event_available,
          value: state.plantingDate,
          onPick: (date) =>
              ref.read(fieldWizardProvider.notifier).updatePlantingDate(date),
        ),
        const SizedBox(height: 12),
        _buildDatePickerField(
          label: 'تاريخ الحصاد المتوقع',
          icon: Icons.event_note,
          value: state.harvestDate,
          onPick: (date) =>
              ref.read(fieldWizardProvider.notifier).updateHarvestDate(date),
        ),
      ],
    );
  }

  Widget _buildDatePickerField({
    required String label,
    required IconData icon,
    required DateTime? value,
    required ValueChanged<DateTime?> onPick,
  }) {
    return InkWell(
      onTap: () async {
        final picked = await showDatePicker(
          context: context,
          initialDate: value ?? DateTime.now(),
          firstDate: DateTime(2020),
          lastDate: DateTime(2030),
          locale: const Locale('ar'),
        );
        onPick(picked);
      },
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding:
            const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        decoration: BoxDecoration(
          color: Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[700]!),
        ),
        child: Row(
          children: [
            Icon(icon, color: SahoolColors.primary, size: 22),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                value != null
                    ? '${value.year}/${value.month.toString().padLeft(2, '0')}/${value.day.toString().padLeft(2, '0')}'
                    : label,
                style: TextStyle(
                  color: value != null
                      ? Theme.of(context).colorScheme.onSurface
                      : Colors.grey[400],
                ),
              ),
            ),
            if (value != null)
              GestureDetector(
                onTap: () => onPick(null),
                child: Icon(Icons.clear,
                    color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6), size: 18),
              ),
            if (value == null)
              Icon(Icons.calendar_today,
                  color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6), size: 18),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // الخطوة 4: المحصول
  // ─────────────────────────────────────────────────────────────

  static const _crops = [
    'قمح', 'شعير', 'ذرة', 'أرز', 'دخن', 'طماطم', 'بطاطس', 'بصل',
    'ثوم', 'خيار', 'فلفل', 'باذنجان', 'نخيل تمر', 'موز', 'مانجو',
    'حمضيات', 'عنب', 'قهوة', 'قطن', 'عباد الشمس', 'سمسم', 'بطيخ',
    'كوسا', 'فول', 'عدس',
  ];

  Widget _buildStep4Crop(FieldWizardState state) {
    final previousCrops = ['لا يوجد', ..._crops];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('نوع المحصول (اختياري)', Icons.grass),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          value: state.cropType.isEmpty ? null : state.cropType,
          decoration: const InputDecoration(
            labelText: 'المحصول الحالي',
            prefixIcon: Icon(Icons.grass),
          ),
          hint: const Text('اختر المحصول'),
          items: _crops
              .map((c) =>
                  DropdownMenuItem(value: c, child: Text(c)))
              .toList(),
          onChanged: (v) {
            if (v != null) {
              ref
                  .read(fieldWizardProvider.notifier)
                  .updateCrop(v,
                      previous: state.previousCrop);
            }
          },
        ),
        const SizedBox(height: 16),
        DropdownButtonFormField<String>(
          value: state.previousCrop ?? 'لا يوجد',
          decoration: const InputDecoration(
            labelText: 'المحصول السابق',
            prefixIcon: Icon(Icons.history),
          ),
          items: previousCrops
              .map((c) =>
                  DropdownMenuItem(value: c, child: Text(c)))
              .toList(),
          onChanged: (v) {
            ref
                .read(fieldWizardProvider.notifier)
                .updatePreviousCrop(v);
          },
        ),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────────
  // الخطوة 5: التربة
  // ─────────────────────────────────────────────────────────────

  static const _soilTypes = [
    ('طينية', '🏔️'),
    ('رملية', '🏜️'),
    ('طميية', '🌱'),
    ('غرينية', '💧'),
    ('خثية', '🌿'),
    ('طباشيرية', '⚪'),
    ('أخرى', '❓'),
  ];

  Widget _buildStep5Soil(FieldWizardState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('نوع التربة (اختياري)', Icons.layers),
        const SizedBox(height: 16),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: _soilTypes.map((soil) {
            final isSelected = state.soilType == soil.$1;
            return GestureDetector(
              onTap: () =>
                  ref.read(fieldWizardProvider.notifier).updateSoil(
                        isSelected ? '' : soil.$1,
                      ),
              child: _selectionCard(
                label: soil.$1,
                emoji: soil.$2,
                isSelected: isSelected,
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  // ─────────────────────────────────────────────────────────────
  // الخطوة 6: الري
  // ─────────────────────────────────────────────────────────────

  static const _irrigationTypes = [
    ('تنقيط', '💧'),
    ('رش', '🌧️'),
    ('غمر', '🌊'),
    ('يدوي', '✋'),
    ('أخرى', '❓'),
  ];

  Widget _buildStep6Irrigation(FieldWizardState state) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _sectionTitle('نوع الري (اختياري)', Icons.water_drop),
        const SizedBox(height: 16),
        Wrap(
          spacing: 10,
          runSpacing: 10,
          children: _irrigationTypes.map((irr) {
            final isSelected = state.irrigationType == irr.$1;
            return GestureDetector(
              onTap: () => ref
                  .read(fieldWizardProvider.notifier)
                  .updateIrrigation(isSelected ? '' : irr.$1),
              child: _selectionCard(
                label: irr.$1,
                emoji: irr.$2,
                isSelected: isSelected,
              ),
            );
          }).toList(),
        ),
        const SizedBox(height: 24),
        // ملخص قبل الحفظ
        _buildSummaryCard(state),
      ],
    );
  }

  Widget _buildSummaryCard(FieldWizardState state) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.primary.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
            color: SahoolColors.primary.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'ملخص بيانات الحقل',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: SahoolColors.primary,
              fontSize: 15,
            ),
          ),
          const SizedBox(height: 12),
          _summaryRow('الاسم', state.name.isEmpty ? '—' : state.name),
          _summaryRow('المساحة', '${state.area.toStringAsFixed(2)} هـ'),
          if (state.cropType.isNotEmpty)
            _summaryRow('المحصول', state.cropType),
          if (state.soilType.isNotEmpty)
            _summaryRow('التربة', state.soilType),
          if (state.irrigationType.isNotEmpty)
            _summaryRow('الري', state.irrigationType),
          if (state.seasonName != null)
            _summaryRow('الموسم', state.seasonName!),
        ],
      ),
    );
  }

  Widget _summaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: TextStyle(
              color: Theme.of(context).colorScheme.onSurface.withValues(alpha: 0.6),
              fontSize: 13,
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: TextStyle(
                color: Theme.of(context).colorScheme.onSurface,
                fontWeight: FontWeight.w500,
                fontSize: 13,
              ),
            ),
          ),
        ],
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // مساعدات مشتركة
  // ─────────────────────────────────────────────────────────────

  Widget _selectionCard({
    required String label,
    required String emoji,
    required bool isSelected,
  }) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 150),
      width: 100,
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isSelected
            ? SahoolColors.primary.withValues(alpha: 0.1)
            : Theme.of(context).colorScheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSelected ? SahoolColors.primary : Colors.grey[600]!,
          width: isSelected ? 2.0 : 1.0,
        ),
        boxShadow: isSelected
            ? [
                BoxShadow(
                  color: SahoolColors.primary.withValues(alpha: 0.15),
                  blurRadius: 6,
                  offset: const Offset(0, 2),
                )
              ]
            : [],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(emoji, style: const TextStyle(fontSize: 28)),
          const SizedBox(height: 6),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              color: isSelected
                  ? SahoolColors.primary
                  : Theme.of(context).colorScheme.onSurface,
            ),
            textAlign: TextAlign.center,
          ),
          if (isSelected)
            const Padding(
              padding: EdgeInsets.only(top: 4),
              child: Icon(Icons.check_circle,
                  color: SahoolColors.primary, size: 16),
            ),
        ],
      ),
    );
  }

  Widget _sectionTitle(String title, IconData icon) {
    return Row(
      children: [
        Icon(icon, color: SahoolColors.primary, size: 20),
        const SizedBox(width: 8),
        Text(
          title,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.onSurface,
          ),
        ),
      ],
    );
  }
}
