import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/config/theme.dart';
import '../../data/yemen_locations.dart';
import '../../domain/farm_providers.dart';

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

  // Default center: Yemen
  static const _defaultCenter = LatLng(15.3694, 44.1910);

  @override
  void dispose() {
    _nameController.dispose();
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
    // Convert from degrees² to hectares using approximate spherical formula
    final areaM2 = rawArea * 111320 * 111320 * cos(centerLat * pi / 180);
    return areaM2 / 10000;
  }

  void _addPoint(LatLng point) {
    setState(() {
      _polygonPoints.add(point);
      _computedAreaHa = _calculateArea(_polygonPoints);
    });
  }

  void _clearPolygon() {
    setState(() {
      _polygonPoints.clear();
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
      final center = _polygonPoints.isNotEmpty
          ? LatLng(
              _polygonPoints.map((p) => p.latitude).reduce((a, b) => a + b) / _polygonPoints.length,
              _polygonPoints.map((p) => p.longitude).reduce((a, b) => a + b) / _polygonPoints.length,
            )
          : (_selectedGovernorate != null
              ? () {
                  final c = YemenLocations.getCenter(_selectedGovernorate!);
                  return c != null ? LatLng(c['lat']!, c['lng']!) : _defaultCenter;
                }()
              : _defaultCenter);

      final data = <String, dynamic>{
        'name': name,
        'location': '$_selectedGovernorate${_selectedDistrict != null ? ' - $_selectedDistrict' : ''}',
        'location_ar': '$_selectedGovernorate${_selectedDistrict != null ? ' - $_selectedDistrict' : ''}',
        'total_area_ha': _computedAreaHa > 0 ? _computedAreaHa : 1.0,
        'water_source': _selectedWaterSource,
        'center_lat': center.latitude,
        'center_lng': center.longitude,
        if (_polygonPoints.length >= 3)
          'polygon_coords': _polygonPoints
              .map((p) => [p.longitude, p.latitude])
              .toList(),
        'status': 'active',
      };

      final api = ref.read(farmApiProvider);
      await api.createFarm(data);

      ref.refresh(farmsListProvider);

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
        backgroundColor: const Color(0xFFF5F7F5),
        appBar: AppBar(
          title: const Text(
            'إضافة مزرعة جديدة',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          centerTitle: true,
          backgroundColor: Colors.white,
          foregroundColor: const Color(0xFF1A1A1A),
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
                fillColor: Colors.white,
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
              value: _selectedGovernorate,
              decoration: InputDecoration(
                labelText: 'المحافظة *',
                prefixIcon: const Icon(Icons.location_city_rounded),
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Colors.white,
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
                  // Pan map to governorate center
                  if (value != null) {
                    final center = YemenLocations.getCenter(value);
                    if (center != null) {
                      _mapController.move(
                        LatLng(center['lat']!, center['lng']!),
                        10,
                      );
                    }
                  }
                });
              },
              validator: (value) => value == null ? 'اختيار المحافظة مطلوب' : null,
            ),
            const SizedBox(height: 16),

            // District dropdown
            if (_selectedGovernorate != null)
              DropdownButtonFormField<String>(
                value: _selectedDistrict,
                decoration: InputDecoration(
                  labelText: 'المديرية',
                  prefixIcon: const Icon(Icons.place_rounded),
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  filled: true,
                  fillColor: Colors.white,
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

  // ── Step 1: Farm Details ──────────────────────────────────────────────────

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
                        : Colors.white,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: isSelected ? SahoolTheme.primary : Colors.grey.shade300,
                      width: isSelected ? 2 : 1,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(
                        _waterSourceIcons[source] ?? Icons.water_drop_rounded,
                        color: isSelected ? SahoolTheme.primary : Colors.grey[600],
                        size: 28,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        source,
                        style: TextStyle(
                          fontSize: 13,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          color: isSelected ? SahoolTheme.primary : const Color(0xFF1A1A1A),
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

  // ── Step 2: Map Boundary ──────────────────────────────────────────────────

  Step _buildStep2() {
    return Step(
      title: const Text('حدود المزرعة على الخريطة'),
      isActive: _currentStep >= 2,
      state: StepState.indexed,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Instructions
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Row(
              children: [
                const Icon(Icons.info_outline_rounded, color: Colors.blue, size: 18),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'اضغط على الخريطة لإضافة نقاط حدود المزرعة',
                    style: TextStyle(fontSize: 13, color: Colors.blue),
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
                  FlutterMap(
                      mapController: _mapController,
                      options: MapOptions(
                        initialCenter: _selectedGovernorate != null
                            ? () {
                                final c = YemenLocations.getCenter(_selectedGovernorate!);
                                return c != null
                                    ? LatLng(c['lat']!, c['lng']!)
                                    : _defaultCenter;
                              }()
                            : _defaultCenter,
                        initialZoom: 10,
                        onTap: (tapPosition, latLng) => _addPoint(latLng),
                      ),
                      children: [
                        TileLayer(
                          urlTemplate:
                              'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                          userAgentPackageName: 'com.sahool.app',
                          maxZoom: 19,
                        ),
                        if (_polygonPoints.isNotEmpty)
                          PolylineLayer(
                            polylines: [
                              Polyline(
                                points: [
                                  ..._polygonPoints,
                                  if (_polygonPoints.length >= 2) _polygonPoints.first,
                                ],
                                color: SahoolTheme.primary,
                                strokeWidth: 2.5,
                              ),
                            ],
                          ),
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
                        MarkerLayer(
                          markers: _polygonPoints.asMap().entries.map((entry) {
                            final i = entry.key;
                            final p = entry.value;
                            return Marker(
                              point: p,
                              width: 24,
                              height: 24,
                              child: Container(
                                decoration: BoxDecoration(
                                  color: i == 0 ? Colors.orange : SahoolTheme.primary,
                                  shape: BoxShape.circle,
                                  border: Border.all(color: Colors.white, width: 2),
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
                      ],
                    ),

                  // Clear button
                  Positioned(
                    top: 10,
                    left: 10,
                    child: Material(
                      borderRadius: BorderRadius.circular(8),
                      color: Colors.white,
                      elevation: 2,
                      child: InkWell(
                        borderRadius: BorderRadius.circular(8),
                        onTap: _clearPolygon,
                        child: const Padding(
                          padding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.clear_rounded, size: 18, color: Colors.red),
                              SizedBox(width: 4),
                              Text('مسح', style: TextStyle(fontSize: 13, color: Colors.red)),
                            ],
                          ),
                        ),
                      ),
                    ),
                  ),

                  // Point count badge
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(8),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withValues(alpha: 0.1),
                            blurRadius: 4,
                          ),
                        ],
                      ),
                      child: Text(
                        '${_polygonPoints.length} نقطة',
                        style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Area display
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: Colors.grey.shade200),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Row(
                  children: [
                    Icon(Icons.straighten_rounded, color: SahoolTheme.primary, size: 20),
                    const SizedBox(width: 8),
                    const Text(
                      'المساحة المحسوبة',
                      style: TextStyle(fontWeight: FontWeight.w500),
                    ),
                  ],
                ),
                Text(
                  _polygonPoints.length >= 3
                      ? '${_computedAreaHa.toStringAsFixed(2)} هـ'
                      : '— هـ',
                  style: TextStyle(
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
                'أضف 3 نقاط على الأقل لحساب المساحة',
                style: TextStyle(fontSize: 12, color: Colors.grey[500]),
              ),
            ),
        ],
      ),
    );
  }
}
