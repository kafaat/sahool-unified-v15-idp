import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/config/theme.dart';
import '../../data/yemen_locations.dart';
import '../../domain/farm_providers.dart';

enum _FarmDrawMode { polygon, rectangle }

/// Farm creation wizard — 3-step Stepper
/// معالج إنشاء مزرعة جديد
class FarmCreationScreen extends ConsumerStatefulWidget {
  const FarmCreationScreen({super.key});

  @override
  ConsumerState<FarmCreationScreen> createState() => _FarmCreationScreenState();
}

class _FarmCreationScreenState extends ConsumerState<FarmCreationScreen> {
  int _currentStep = 0;
  bool _isSubmitting = false;

  // Step 0 state
  final _nameController = TextEditingController();
  String? _selectedGovernorate;
  String? _selectedDistrict;
  final _formKey = GlobalKey<FormState>();

  // Step 1 state
  String? _selectedWaterSource;
  final List<String> _waterSources = ['آبار', 'أمطار', 'سدود', 'فيضانات', 'ينابيع', 'أنهار'];
  final Map<String, IconData> _waterSourceIcons = {
    'آبار': Icons.water_outlined,
    'أمطار': Icons.grain_rounded,
    'سدود': Icons.water_rounded,
    'فيضانات': Icons.waves_rounded,
    'ينابيع': Icons.hot_tub_rounded,
    'أنهار': Icons.water_drop_rounded,
  };

  // Step 2 state — map polygon drawing
  final List<LatLng> _polygonPoints = [];
  final MapController _mapController = MapController();
  double _computedAreaHa = 0.0;
  LatLng _farmCenter = const LatLng(15.3694, 44.1910); // default Yemen
  bool _mapFlyPending = false;
  _FarmDrawMode _farmDrawMode = _FarmDrawMode.polygon;
  LatLng? _rectFirstCorner; // for rectangle mode

  @override
  void dispose() {
    _nameController.dispose();
    _mapController.dispose();
    super.dispose();
  }

  // ── Area calculation ──────────────────────────────────────────────────────

  double _calculateArea(List<LatLng> polygon) {
    final n = polygon.length;
    if (n < 3) return 0.0;

    double sum = 0.0;
    for (int i = 0; i < n; i++) {
      final current = polygon[i];
      final next = polygon[(i + 1) % n];
      sum += current.longitude * next.latitude - next.longitude * current.latitude;
    }

    final centerLat = polygon.map((p) => p.latitude).reduce((a, b) => a + b) / n;
    final rawArea = sum.abs() / 2;
    final areaM2 = rawArea * 111320 * 111320 * cos(centerLat * pi / 180);
    return areaM2 / 10000;
  }

  List<double> _calculateBbox(List<LatLng> points) {
    final lngs = points.map((p) => p.longitude).toList();
    final lats = points.map((p) => p.latitude).toList();
    return [
      lngs.reduce(min), // minLng
      lats.reduce(min), // minLat
      lngs.reduce(max), // maxLng
      lats.reduce(max), // maxLat
    ];
  }

  void _addPoint(LatLng point) {
    if (_farmDrawMode == _FarmDrawMode.rectangle) {
      if (_rectFirstCorner == null) {
        setState(() => _rectFirstCorner = point);
      } else {
        final a = _rectFirstCorner!;
        final b = point;
        final pts = [
          a,
          LatLng(a.latitude, b.longitude),
          b,
          LatLng(b.latitude, a.longitude),
        ];
        setState(() {
          _polygonPoints.clear();
          _polygonPoints.addAll(pts);
          _rectFirstCorner = null;
          _computedAreaHa = _calculateArea(_polygonPoints);
        });
      }
    } else {
      setState(() {
        _rectFirstCorner = null;
        _polygonPoints.add(point);
        _computedAreaHa = _calculateArea(_polygonPoints);
      });
    }
  }

  void _removeLastPoint() {
    if (_farmDrawMode == _FarmDrawMode.rectangle) {
      _clearPolygon();
    } else {
      if (_polygonPoints.isEmpty) return;
      setState(() {
        _polygonPoints.removeLast();
        _computedAreaHa = _calculateArea(_polygonPoints);
      });
    }
  }

  void _clearPolygon() {
    setState(() {
      _polygonPoints.clear();
      _rectFirstCorner = null;
      _computedAreaHa = 0.0;
    });
  }

  // ── Navigation ────────────────────────────────────────────────────────────

  void _onStepContinue() {
    if (_currentStep == 0) {
      if (!_formKey.currentState!.validate()) return;
    } else if (_currentStep == 1) {
      if (_selectedWaterSource == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('الرجاء اختيار مصدر المياه')),
        );
        return;
      }
      // Flag the map to fly to the selected governorate center on step 2 open
      _mapFlyPending = true;
    }
    if (_currentStep < 2) {
      setState(() => _currentStep++);
    }
  }

  void _onStepCancel() {
    if (_currentStep > 0) setState(() => _currentStep--);
  }

  // ── Submit ────────────────────────────────────────────────────────────────

  Future<void> _submit() async {
    final name = _nameController.text.trim();
    if (name.isEmpty || _selectedGovernorate == null || _selectedWaterSource == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('يرجى إكمال جميع الحقول المطلوبة')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      // Determine center: bbox center if polygon drawn, else governorate center
      final LatLng center;
      if (_polygonPoints.length >= 3) {
        final bbox = _calculateBbox(_polygonPoints);
        center = LatLng(
          (bbox[1] + bbox[3]) / 2, // midLat
          (bbox[0] + bbox[2]) / 2, // midLng
        );
      } else {
        center = _farmCenter;
      }

      final data = <String, dynamic>{
        'name': name,
        'nameAr': name,
        'region': _selectedGovernorate ?? '',
        'regionAr': _selectedGovernorate ?? '',
        'location':
            '$_selectedGovernorate${_selectedDistrict != null ? " - $_selectedDistrict" : ""}',
        'locationAr':
            '$_selectedGovernorate${_selectedDistrict != null ? " - $_selectedDistrict" : ""}',
        'waterSource': _selectedWaterSource,
        'waterSourceAr': _selectedWaterSource,
        'totalAreaHectares': _computedAreaHa > 0 ? _computedAreaHa : 0.0,
        'status': 'active',
        'centerLat': center.latitude,
        'centerLng': center.longitude,
        'zoom': _mapController.camera.zoom.round(),
        if (_polygonPoints.length >= 3) 'bbox': _calculateBbox(_polygonPoints),
      };

      final api = ref.read(farmApiProvider);
      await api.createFarm(data);

      ref.invalidate(farmsListProvider);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم إنشاء المزرعة بنجاح'),
            backgroundColor: Colors.green,
          ),
        );
        context.go('/farms');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('حدث خطأ: ${e.toString()}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  // ── Build ─────────────────────────────────────────────────────────────────

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        appBar: AppBar(
          title: const Text(
            'إضافة مزرعة جديدة',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          centerTitle: true,
          backgroundColor: Theme.of(context).colorScheme.surface,
          foregroundColor: Theme.of(context).colorScheme.onSurface,
          elevation: 0,
          surfaceTintColor: Colors.transparent,
          leading: IconButton(
            icon: const Icon(Icons.arrow_back_ios_new_rounded),
            onPressed: () => context.pop(),
          ),
        ),
        body: Stepper(
          currentStep: _currentStep,
          onStepContinue: _onStepContinue,
          onStepCancel: _onStepCancel,
          controlsBuilder: _buildStepControls,
          steps: [
            _buildStep0(),
            _buildStep1(),
            _buildStep2(),
          ],
        ),
      ),
    );
  }

  Widget _buildStepControls(BuildContext context, ControlsDetails details) {
    final isLastStep = _currentStep == 2;
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Row(
        children: [
          if (isLastStep)
            Expanded(
              child: ElevatedButton(
                onPressed: _isSubmitting ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: _isSubmitting
                    ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Text('حفظ المزرعة', style: TextStyle(fontSize: 15)),
              ),
            )
          else
            Expanded(
              child: ElevatedButton(
                onPressed: details.onStepContinue,
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolTheme.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('التالي', style: TextStyle(fontSize: 15)),
              ),
            ),
          if (_currentStep > 0) ...[
            const SizedBox(width: 12),
            Expanded(
              child: OutlinedButton(
                onPressed: details.onStepCancel,
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
                child: const Text('السابق'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  // ── Step 0: Basic Info ────────────────────────────────────────────────────

  Step _buildStep0() {
    return Step(
      title: const Text('معلومات أساسية'),
      isActive: _currentStep >= 0,
      state: _currentStep > 0 ? StepState.complete : StepState.indexed,
      content: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Farm name
            TextFormField(
              controller: _nameController,
              textDirection: TextDirection.rtl,
              decoration: InputDecoration(
                labelText: 'اسم المزرعة *',
                hintText: 'مثال: مزرعة الأمل',
                prefixIcon: const Icon(Icons.agriculture_rounded),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'اسم المزرعة مطلوب';
                }
                return null;
              },
            ),
            const SizedBox(height: 16),

            // Governorate dropdown
            DropdownButtonFormField<String>(
              initialValue: _selectedGovernorate,
              decoration: InputDecoration(
                labelText: 'المحافظة *',
                prefixIcon: const Icon(Icons.location_city_rounded),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
              ),
              hint: const Text('اختر المحافظة'),
              items: YemenLocations.governorates
                  .map((gov) => DropdownMenuItem<String>(
                        value: gov['name'] as String,
                        child: Text(gov['name'] as String),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _selectedGovernorate = value;
                  _selectedDistrict = null;
                  if (value != null) {
                    final c = YemenLocations.getCenter(value);
                    if (c != null) {
                      _farmCenter = LatLng(c['lat']!, c['lng']!);
                      // If already on step 2, fly the map there immediately
                      if (_currentStep == 2) {
                        _mapController.move(_farmCenter, 10);
                      }
                    }
                  }
                });
              },
              validator: (value) => value == null ? 'اختيار المحافظة مطلوب' : null,
            ),
            const SizedBox(height: 16),

            // District dropdown — only shown after governorate is selected
            if (_selectedGovernorate != null)
              DropdownButtonFormField<String>(
                initialValue: _selectedDistrict,
                decoration: InputDecoration(
                  labelText: 'المديرية',
                  prefixIcon: const Icon(Icons.place_rounded),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  filled: true,
                  fillColor: Theme.of(context).colorScheme.surfaceContainerHighest,
                ),
                hint: const Text('اختر المديرية'),
                items: YemenLocations.getDistricts(_selectedGovernorate!)
                    .map((d) => DropdownMenuItem<String>(value: d, child: Text(d)))
                    .toList(),
                onChanged: (value) => setState(() => _selectedDistrict = value),
              ),
          ],
        ),
      ),
    );
  }

  // ── Step 1: Water Source ──────────────────────────────────────────────────

  Step _buildStep1() {
    return Step(
      title: const Text('تفاصيل المزرعة'),
      isActive: _currentStep >= 1,
      state: _currentStep > 1 ? StepState.complete : StepState.indexed,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'مصدر المياه',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
          ),
          const SizedBox(height: 4),
          Text(
            'اختر مصدر الري الرئيسي للمزرعة',
            style: TextStyle(fontSize: 13, color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
          GridView.count(
            crossAxisCount: 3,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 10,
            mainAxisSpacing: 10,
            childAspectRatio: 1.1,
            children: _waterSources.map((source) {
              final isSelected = _selectedWaterSource == source;
              return GestureDetector(
                onTap: () => setState(() => _selectedWaterSource = source),
                child: AnimatedContainer(
                  duration: const Duration(milliseconds: 180),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? SahoolTheme.primary.withValues(alpha: 0.12)
                        : Theme.of(context).colorScheme.surfaceContainerHighest,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isSelected ? SahoolTheme.primary : Colors.grey.shade600,
                      width: isSelected ? 2 : 1,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        _waterSourceIcons[source] ?? Icons.water_drop_rounded,
                        color: isSelected ? SahoolTheme.primary : Colors.grey[400],
                        size: 28,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        source,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          color: isSelected
                              ? SahoolTheme.primary
                              : Theme.of(context).colorScheme.onSurface,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  // ── Step 2: Map Boundary (satellite) ─────────────────────────────────────

  Step _buildStep2() {
    // Fly to center after map is mounted when transitioning to this step
    if (_mapFlyPending) {
      _mapFlyPending = false;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) {
          _mapController.move(_farmCenter, 10);
        }
      });
    }

    return Step(
      title: const Text('حدود المزرعة على الخريطة'),
      isActive: _currentStep >= 2,
      state: StepState.indexed,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Instructions banner
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.withValues(alpha: 0.18),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline_rounded,
                    color: Colors.blue, size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    _farmDrawMode == _FarmDrawMode.rectangle
                        ? 'انقر مرتين لرسم مستطيل حول المزرعة'
                        : 'اضغط على الخريطة لإضافة نقاط حدود المزرعة',
                    style: const TextStyle(fontSize: 13, color: Colors.blue),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),

          // Map
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: SizedBox(
              height: 380,
              child: Stack(
                children: [
                  // ── Map ────────────────────────────────────────────────
                  FlutterMap(
                    mapController: _mapController,
                    options: MapOptions(
                      initialCenter: _farmCenter,
                      initialZoom: 10,
                      onTap: (_, latLng) => _addPoint(latLng),
                    ),
                    children: [
                      // ESRI satellite tile layer
                      TileLayer(
                        urlTemplate:
                            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                        userAgentPackageName: 'com.sahool.app',
                        maxZoom: 19,
                      ),

                      // Outline polyline (polygon mode)
                      if (_farmDrawMode == _FarmDrawMode.polygon &&
                          _polygonPoints.length >= 2)
                        PolylineLayer(
                          polylines: [
                            Polyline(
                              points: [
                                ..._polygonPoints,
                                if (_polygonPoints.length >= 3)
                                  _polygonPoints.first,
                              ],
                              color: SahoolTheme.primary.withValues(alpha: 0.8),
                              strokeWidth: 2.5,
                            ),
                          ],
                        ),

                      // Filled polygon when ≥3 points
                      if (_polygonPoints.length >= 3)
                        PolygonLayer(
                          polygons: [
                            Polygon(
                              points: _polygonPoints,
                              color: SahoolTheme.primary.withValues(alpha: 0.15),
                              borderColor: SahoolTheme.primary,
                              borderStrokeWidth: 2,
                            ),
                          ],
                        ),

                      // Vertex markers
                      if (_polygonPoints.isNotEmpty)
                        MarkerLayer(
                          markers: _farmDrawMode == _FarmDrawMode.rectangle
                              ? [
                                  _buildCornerMarker(_polygonPoints[0], 'A'),
                                  _buildCornerMarker(_polygonPoints[2], 'B'),
                                ]
                              : _polygonPoints.asMap().entries.map((entry) {
                                  final i = entry.key;
                                  final p = entry.value;
                                  return Marker(
                                    point: p,
                                    width: 24,
                                    height: 24,
                                    child: DecoratedBox(
                                      decoration: BoxDecoration(
                                        color: i == 0
                                            ? Colors.orange
                                            : SahoolTheme.primary,
                                        shape: BoxShape.circle,
                                        border: Border.all(
                                            color: Colors.white, width: 2),
                                      ),
                                      child: Center(
                                        child: Text(
                                          '${i + 1}',
                                          style: const TextStyle(
                                            color: Colors.white,
                                            fontSize: 9,
                                            fontWeight: FontWeight.bold,
                                          ),
                                        ),
                                      ),
                                    ),
                                  );
                                }).toList(),
                        ),

                      // First corner marker (rectangle mode, awaiting 2nd tap)
                      if (_farmDrawMode == _FarmDrawMode.rectangle &&
                          _rectFirstCorner != null)
                        MarkerLayer(
                          markers: [
                            Marker(
                              point: _rectFirstCorner!,
                              width: 30,
                              height: 30,
                              child: Container(
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.orange.withValues(alpha: 0.9),
                                  border:
                                      Border.all(color: Colors.white, width: 2),
                                ),
                                child: const Icon(Icons.add,
                                    color: Colors.white, size: 16),
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),

                  // ── Drawing toolbar (top-center) ───────────────────────
                  Positioned(
                    top: 10,
                    left: 0,
                    right: 0,
                    child: Center(
                      child: Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 6),
                        decoration: BoxDecoration(
                          color: Colors.black.withValues(alpha: 0.75),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: Colors.white24),
                        ),
                        child: Row(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            _farmDrawToolButton(
                              icon: Icons.polyline_rounded,
                              label: 'مضلع',
                              mode: _FarmDrawMode.polygon,
                            ),
                            const SizedBox(width: 6),
                            _farmDrawToolButton(
                              icon: Icons.crop_square_rounded,
                              label: 'مستطيل',
                              mode: _FarmDrawMode.rectangle,
                            ),
                            if (_polygonPoints.isNotEmpty ||
                                _rectFirstCorner != null) ...[
                              const SizedBox(width: 6),
                              const SizedBox(
                                height: 24,
                                child: VerticalDivider(
                                    color: Colors.white24, width: 1),
                              ),
                              const SizedBox(width: 6),
                              GestureDetector(
                                onTap: _removeLastPoint,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 5),
                                  decoration: BoxDecoration(
                                    color:
                                        Colors.orange.withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(
                                        color: Colors.orange
                                            .withValues(alpha: 0.5)),
                                  ),
                                  child: const Icon(Icons.undo_rounded,
                                      color: Colors.orange, size: 16),
                                ),
                              ),
                              const SizedBox(width: 4),
                              GestureDetector(
                                onTap: _clearPolygon,
                                child: Container(
                                  padding: const EdgeInsets.symmetric(
                                      horizontal: 8, vertical: 5),
                                  decoration: BoxDecoration(
                                    color: Colors.red.withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(6),
                                    border: Border.all(
                                        color:
                                            Colors.red.withValues(alpha: 0.5)),
                                  ),
                                  child: const Icon(Icons.delete_outline,
                                      color: Colors.red, size: 16),
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ),

                  // ── Top-right overlay: Point count badge ───────────────
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.black54,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        _farmDrawMode == _FarmDrawMode.rectangle
                            ? (_rectFirstCorner != null
                                ? 'انقر للزاوية B'
                                : _polygonPoints.length >= 3
                                    ? '✓ مستطيل'
                                    : 'انقر للزاوية A')
                            : '${_polygonPoints.length} نقطة',
                        style: const TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: Colors.white),
                      ),
                    ),
                  ),

                  // ── Bottom-center overlay: Area badge (≥3 pts) ─────────
                  if (_polygonPoints.length >= 3)
                    Positioned(
                      bottom: 12,
                      left: 0,
                      right: 0,
                      child: Center(
                        child: Container(
                          padding: const EdgeInsets.symmetric(
                              horizontal: 14, vertical: 7),
                          decoration: BoxDecoration(
                            color: SahoolTheme.primary,
                            borderRadius: BorderRadius.circular(20),
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withValues(alpha: 0.2),
                                blurRadius: 6,
                                offset: const Offset(0, 2),
                              ),
                            ],
                          ),
                          child: Text(
                            '${_computedAreaHa.toStringAsFixed(2)} هـ',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Area summary card below map
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.surfaceContainerHighest,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey.shade600),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.straighten_rounded,
                        color: SahoolTheme.primary, size: 20),
                    SizedBox(width: 8),
                    Text(
                      'المساحة المحسوبة',
                      style: TextStyle(fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
                Text(
                  _polygonPoints.length >= 3
                      ? '${_computedAreaHa.toStringAsFixed(2)} هـ'
                      : '— هـ',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                    color: SahoolTheme.primary,
                  ),
                ),
              ],
            ),
          ),
          if (_polygonPoints.length < 3)
            Padding(
              padding: const EdgeInsets.only(top: 8),
              child: Text(
                _farmDrawMode == _FarmDrawMode.rectangle
                    ? 'انقر مرتين على الخريطة لرسم مستطيل'
                    : 'أضف 3 نقاط على الأقل لحساب المساحة',
                style: TextStyle(fontSize: 12, color: Colors.grey[500]),
              ),
            ),
        ],
      ),
    );
  }

  Widget _farmDrawToolButton({
    required IconData icon,
    required String label,
    required _FarmDrawMode mode,
  }) {
    final isActive = _farmDrawMode == mode;
    return GestureDetector(
      onTap: () {
        if (_farmDrawMode != mode) {
          _clearPolygon();
          setState(() => _farmDrawMode = mode);
        }
      },
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: isActive ? SahoolTheme.primary : Colors.white.withValues(alpha: 0.08),
          borderRadius: BorderRadius.circular(7),
          border: Border.all(
            color: isActive ? SahoolTheme.primary : Colors.white30,
          ),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon,
                color: isActive ? Colors.white : Colors.white70, size: 15),
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

  Marker _buildCornerMarker(LatLng point, String label) {
    return Marker(
      point: point,
      width: 26,
      height: 26,
      child: Container(
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: SahoolTheme.primary,
          border: Border.all(color: Colors.white, width: 2),
        ),
        child: Center(
          child: Text(
            label,
            style: const TextStyle(
                color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
          ),
        ),
      ),
    );
  }
}
