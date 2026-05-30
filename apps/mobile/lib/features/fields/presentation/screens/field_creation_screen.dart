import 'dart:math';
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../../../core/di/providers.dart';
import '../../../../core/config/theme.dart';

// Crop type options — (value, Arabic label)
const _cropTypes = [
  ('wheat', 'قمح'),
  ('barley', 'شعير'),
  ('corn', 'ذرة'),
  ('rice', 'أرز'),
  ('tomato', 'طماطم'),
  ('potato', 'بطاطا'),
  ('onion', 'بصل'),
  ('garlic', 'ثوم'),
  ('cucumber', 'خيار'),
  ('pepper', 'فلفل'),
  ('eggplant', 'باذنجان'),
  ('watermelon', 'بطيخ'),
  ('melon', 'شمام'),
  ('grape', 'عنب'),
  ('date_palm', 'نخيل'),
  ('olive', 'زيتون'),
  ('citrus', 'حمضيات'),
  ('alfalfa', 'برسيم'),
  ('sorghum', 'ذرة رفيعة'),
  ('other', 'أخرى'),
];

const _irrigationTypes = [
  ('drip', 'تنقيط', Icons.water_drop_rounded),
  ('flood', 'غمر', Icons.waves_rounded),
  ('sprinkler', 'رشاش', Icons.shower_rounded),
  ('rainfed', 'بعلي', Icons.grain_rounded),
  ('pivot', 'محوري', Icons.rotate_right_rounded),
];

const _soilTypes = [
  ('clay', 'طيني'),
  ('sandy', 'رملي'),
  ('loamy', 'طمي'),
  ('silty', 'غريني'),
  ('saline', 'ملحي'),
];

class FieldCreationScreen extends ConsumerStatefulWidget {
  final String? farmId;
  const FieldCreationScreen({super.key, this.farmId});

  @override
  ConsumerState<FieldCreationScreen> createState() =>
      _FieldCreationScreenState();
}

class _FieldCreationScreenState extends ConsumerState<FieldCreationScreen> {
  int _currentStep = 0;
  bool _isSubmitting = false;

  // Step 0
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  String? _selectedCropType;
  String? _selectedIrrigationType;
  String? _selectedSoilType;

  // Step 1
  DateTime? _plantingDate;
  DateTime? _expectedHarvestDate;

  // Step 2 — map
  final List<LatLng> _polygonPoints = [];
  final MapController _mapController = MapController();
  double _computedAreaHa = 0.0;
  static const _defaultCenter = LatLng(15.3694, 44.1910);

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  double _calculateArea(List<LatLng> polygon) {
    final n = polygon.length;
    if (n < 3) return 0.0;
    double sum = 0.0;
    for (int i = 0; i < n; i++) {
      final cur = polygon[i];
      final next = polygon[(i + 1) % n];
      sum += cur.longitude * next.latitude - next.longitude * cur.latitude;
    }
    final centerLat =
        polygon.map((p) => p.latitude).reduce((a, b) => a + b) / n;
    final areaM2 =
        (sum.abs() / 2) * 111320 * 111320 * cos(centerLat * pi / 180);
    return areaM2 / 10000;
  }

  void _addPoint(LatLng point) {
    setState(() {
      _polygonPoints.add(point);
      _computedAreaHa = _calculateArea(_polygonPoints);
    });
  }

  void _undoLastPoint() {
    if (_polygonPoints.isEmpty) return;
    setState(() {
      _polygonPoints.removeLast();
      _computedAreaHa = _calculateArea(_polygonPoints);
    });
  }

  void _clearPolygon() {
    setState(() {
      _polygonPoints.clear();
      _computedAreaHa = 0.0;
    });
  }

  void _onStepContinue() {
    if (_currentStep == 0) {
      if (!_formKey.currentState!.validate()) return;
      if (_selectedCropType == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('يرجى اختيار نوع المحصول')),
        );
        return;
      }
      if (_selectedIrrigationType == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('يرجى اختيار نوع الري')),
        );
        return;
      }
      if (_selectedSoilType == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('يرجى اختيار نوع التربة')),
        );
        return;
      }
    }
    if (_currentStep < 2) setState(() => _currentStep++);
  }

  void _onStepCancel() {
    if (_currentStep > 0) setState(() => _currentStep--);
  }

  Future<void> _submit() async {
    if (_polygonPoints.length < 3) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
            content: Text('يرجى رسم حدود الحقل (3 نقاط على الأقل)')),
      );
      return;
    }
    setState(() => _isSubmitting = true);
    try {
      final apiClient = ref.read(apiClientProvider);
      // Build closed GeoJSON ring
      final coords = [
        ..._polygonPoints.map((p) => [p.longitude, p.latitude]),
        [_polygonPoints.first.longitude, _polygonPoints.first.latitude],
      ];

      final body = <String, dynamic>{
        'name': _nameController.text.trim(),
        'cropType': _selectedCropType,
        'irrigationType': _selectedIrrigationType,
        'soilType': _selectedSoilType,
        if (widget.farmId != null) 'farmId': widget.farmId,
        'coordinates':
            _polygonPoints.map((p) => [p.longitude, p.latitude]).toList(),
        'boundary': {
          'type': 'Polygon',
          'coordinates': [coords],
        },
        if (_plantingDate != null)
          'plantingDate': _plantingDate!.toIso8601String(),
        if (_expectedHarvestDate != null)
          'expectedHarvest': _expectedHarvestDate!.toIso8601String(),
      };

      await apiClient.post('/api/v1/fields', body);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم إنشاء الحقل بنجاح'),
            backgroundColor: Colors.green,
          ),
        );
        if (widget.farmId != null) {
          context.go('/farms/${widget.farmId}');
        } else {
          context.go('/fields');
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('حدث خطأ: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: const Color(0xFFF5F7F5),
        appBar: AppBar(
          title: const Text(
            'إضافة حقل جديد',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          centerTitle: true,
          backgroundColor: Colors.white,
          foregroundColor: const Color(0xFF1A1A1A),
          elevation: 0,
          surfaceTintColor: Colors.transparent,
        ),
        body: Stepper(
          currentStep: _currentStep,
          onStepContinue: _onStepContinue,
          onStepCancel: _onStepCancel,
          controlsBuilder: _buildControls,
          steps: [_buildStep0(), _buildStep1(), _buildStep2()],
        ),
      ),
    );
  }

  Widget _buildControls(BuildContext context, ControlsDetails details) {
    final isLastStep = _currentStep == 2;
    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Row(
        children: [
          Expanded(
            child: ElevatedButton(
              onPressed: isLastStep
                  ? (_isSubmitting ? null : _submit)
                  : details.onStepContinue,
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12)),
              ),
              child: isLastStep
                  ? (_isSubmitting
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white),
                        )
                      : const Text('حفظ الحقل'))
                  : const Text('التالي'),
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
                      borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('السابق'),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Step _buildStep0() {
    return Step(
      title: const Text('معلومات الحقل'),
      isActive: _currentStep >= 0,
      state: _currentStep > 0 ? StepState.complete : StepState.indexed,
      content: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: 'اسم الحقل *',
                hintText: 'مثال: حقل القمح الشمالي',
                prefixIcon: const Icon(Icons.grass_rounded),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Colors.white,
              ),
              validator: (v) =>
                  (v == null || v.trim().isEmpty) ? 'اسم الحقل مطلوب' : null,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: _selectedCropType,
              decoration: InputDecoration(
                labelText: 'نوع المحصول *',
                prefixIcon: const Icon(Icons.eco_rounded),
                border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12)),
                filled: true,
                fillColor: Colors.white,
              ),
              hint: const Text('اختر المحصول'),
              items: _cropTypes
                  .map((t) =>
                      DropdownMenuItem(value: t.$1, child: Text(t.$2)))
                  .toList(),
              onChanged: (v) => setState(() => _selectedCropType = v),
            ),
            const SizedBox(height: 16),
            const Text('نوع الري *',
                style:
                    TextStyle(fontWeight: FontWeight.w500, fontSize: 13)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _irrigationTypes.map((t) {
                final selected = _selectedIrrigationType == t.$1;
                return FilterChip(
                  label: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(t.$3,
                          size: 16,
                          color: selected ? Colors.white : Colors.grey[600]),
                      const SizedBox(width: 4),
                      Text(t.$2),
                    ],
                  ),
                  selected: selected,
                  onSelected: (_) =>
                      setState(() => _selectedIrrigationType = t.$1),
                  selectedColor: SahoolTheme.primary,
                  labelStyle:
                      TextStyle(color: selected ? Colors.white : null),
                  checkmarkColor: Colors.white,
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            const Text('نوع التربة *',
                style:
                    TextStyle(fontWeight: FontWeight.w500, fontSize: 13)),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _soilTypes.map((t) {
                final selected = _selectedSoilType == t.$1;
                return FilterChip(
                  label: Text(t.$2),
                  selected: selected,
                  onSelected: (_) =>
                      setState(() => _selectedSoilType = t.$1),
                  selectedColor: SahoolTheme.primary,
                  labelStyle:
                      TextStyle(color: selected ? Colors.white : null),
                  checkmarkColor: Colors.white,
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Step _buildStep1() {
    return Step(
      title: const Text('مواعيد الزراعة (اختياري)'),
      isActive: _currentStep >= 1,
      state: _currentStep > 1 ? StepState.complete : StepState.indexed,
      content: Column(
        children: [
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.calendar_today_rounded),
            title: const Text('تاريخ الزراعة'),
            subtitle: Text(_plantingDate != null
                ? '${_plantingDate!.day}/${_plantingDate!.month}/${_plantingDate!.year}'
                : 'اختياري'),
            trailing: _plantingDate != null
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () => setState(() => _plantingDate = null),
                  )
                : const Icon(Icons.chevron_left_rounded),
            onTap: () async {
              final date = await showDatePicker(
                context: context,
                initialDate: DateTime.now(),
                firstDate: DateTime(2020),
                lastDate: DateTime(2030),
              );
              if (date != null) setState(() => _plantingDate = date);
            },
          ),
          const Divider(),
          ListTile(
            contentPadding: EdgeInsets.zero,
            leading: const Icon(Icons.event_rounded),
            title: const Text('تاريخ الحصاد المتوقع'),
            subtitle: Text(_expectedHarvestDate != null
                ? '${_expectedHarvestDate!.day}/${_expectedHarvestDate!.month}/${_expectedHarvestDate!.year}'
                : 'اختياري'),
            trailing: _expectedHarvestDate != null
                ? IconButton(
                    icon: const Icon(Icons.clear),
                    onPressed: () =>
                        setState(() => _expectedHarvestDate = null),
                  )
                : const Icon(Icons.chevron_left_rounded),
            onTap: () async {
              final date = await showDatePicker(
                context: context,
                initialDate: _plantingDate ??
                    DateTime.now().add(const Duration(days: 90)),
                firstDate: DateTime(2020),
                lastDate: DateTime(2030),
              );
              if (date != null) setState(() => _expectedHarvestDate = date);
            },
          ),
        ],
      ),
    );
  }

  Step _buildStep2() {
    return Step(
      title: const Text('حدود الحقل على الخريطة'),
      isActive: _currentStep >= 2,
      state: StepState.indexed,
      content: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.blue.withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Row(
              children: [
                Icon(Icons.info_outline_rounded,
                    color: Colors.blue, size: 18),
                SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'اضغط على الخريطة لإضافة نقاط حدود الحقل',
                    style: TextStyle(fontSize: 13, color: Colors.blue),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: SizedBox(
              height: 380,
              child: Stack(
                children: [
                  FlutterMap(
                    mapController: _mapController,
                    options: MapOptions(
                      initialCenter: _defaultCenter,
                      initialZoom: 13,
                      onTap: (_, latLng) => _addPoint(latLng),
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
                                if (_polygonPoints.length >= 2)
                                  _polygonPoints.first,
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
                              color: SahoolTheme.primary
                                  .withValues(alpha: 0.15),
                              borderColor: SahoolTheme.primary,
                              borderStrokeWidth: 2,
                            ),
                          ],
                        ),
                      MarkerLayer(
                        markers: _polygonPoints
                            .asMap()
                            .entries
                            .map(
                              (e) => Marker(
                                point: e.value,
                                width: 22,
                                height: 22,
                                child: Container(
                                  decoration: BoxDecoration(
                                    color: e.key == 0
                                        ? Colors.orange
                                        : SahoolTheme.primary,
                                    shape: BoxShape.circle,
                                    border: Border.all(
                                        color: Colors.white, width: 2),
                                  ),
                                  child: Center(
                                    child: Text(
                                      '${e.key + 1}',
                                      style: const TextStyle(
                                        color: Colors.white,
                                        fontSize: 9,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ),
                              ),
                            )
                            .toList(),
                      ),
                    ],
                  ),
                  // Undo / Clear buttons
                  Positioned(
                    top: 10,
                    left: 10,
                    child: Column(
                      children: [
                        Material(
                          borderRadius: BorderRadius.circular(8),
                          color: Colors.white,
                          elevation: 2,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(8),
                            onTap: _undoLastPoint,
                            child: const Padding(
                              padding: EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.undo_rounded,
                                      size: 18, color: Colors.orange),
                                  SizedBox(width: 4),
                                  Text('تراجع',
                                      style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.orange)),
                                ],
                              ),
                            ),
                          ),
                        ),
                        const SizedBox(height: 8),
                        Material(
                          borderRadius: BorderRadius.circular(8),
                          color: Colors.white,
                          elevation: 2,
                          child: InkWell(
                            borderRadius: BorderRadius.circular(8),
                            onTap: _clearPolygon,
                            child: const Padding(
                              padding: EdgeInsets.symmetric(
                                  horizontal: 12, vertical: 8),
                              child: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.clear_rounded,
                                      size: 18, color: Colors.red),
                                  SizedBox(width: 4),
                                  Text('مسح',
                                      style: TextStyle(
                                          fontSize: 12,
                                          color: Colors.red)),
                                ],
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Point counter badge
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                          horizontal: 10, vertical: 6),
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
                        style: const TextStyle(
                            fontSize: 12, fontWeight: FontWeight.w600),
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
                    Icon(Icons.straighten_rounded,
                        color: SahoolTheme.primary, size: 20),
                    const SizedBox(width: 8),
                    const Text('المساحة المحسوبة',
                        style: TextStyle(fontWeight: FontWeight.w500)),
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
