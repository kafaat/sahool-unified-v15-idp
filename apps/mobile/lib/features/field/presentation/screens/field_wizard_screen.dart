import 'dart:math' show cos, pi;

import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../farm/domain/farm_providers.dart';
import '../../domain/field_wizard_notifier.dart';
import '../../domain/field_wizard_state.dart';

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

  void _addPoint(LatLng point) {
    setState(() => _points.add(point));
    final area = _calcAreaHa(_points);
    ref.read(fieldWizardProvider.notifier).updatePolygon(
          List.from(_points),
          area,
        );
  }

  void _clearPoints() {
    setState(() => _points.clear());
    ref.read(fieldWizardProvider.notifier).updatePolygon([], 0.0);
  }

  void _removeLastPoint() {
    if (_points.isEmpty) return;
    setState(() => _points.removeLast());
    final area = _calcAreaHa(_points);
    ref.read(fieldWizardProvider.notifier).updatePolygon(
          List.from(_points),
          area,
        );
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
            // شريط التقدم العلوي
            _buildStepIndicator(state.currentStep),

            // عرض الخطأ إن وجد
            if (state.error != null)
              Container(
                width: double.infinity,
                color: SahoolColors.danger.withValues(alpha: 0.1),
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                child: Row(
                  children: [
                    const Icon(Icons.error_outline,
                        color: SahoolColors.danger, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.error!,
                        style: const TextStyle(
                          color: SahoolColors.danger,
                          fontSize: 13,
                        ),
                      ),
                    ),
                  ],
                ),
              ),

            // محتوى الخطوة الحالية
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: _buildStepContent(state),
              ),
            ),

            // أزرار التنقل
            _buildNavigationButtons(state),
          ],
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────
  // شريط التقدم
  // ─────────────────────────────────────────────────────────────

  Widget _buildStepIndicator(int currentStep) {
    final steps = ['الموقع', 'المعلومات', 'الموسم', 'المحصول', 'التربة', 'الري'];
    return Container(
      color: Colors.white,
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
                              : Colors.grey[300],
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
                                    : Colors.grey[600],
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
                              : Colors.grey[500],
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
      color: Colors.white,
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

  Widget _buildMap() {
    return ClipRRect(
      borderRadius: BorderRadius.circular(12),
      child: SizedBox(
        height: 350,
        child: Stack(
          children: [
            FlutterMap(
              mapController: _mapController,
              options: MapOptions(
                initialCenter: const LatLng(15.5, 44.0), // اليمن
                initialZoom: 7,
                onTap: (_, latlng) => _addPoint(latlng),
              ),
              children: [
                TileLayer(
                  urlTemplate:
                      'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                  userAgentPackageName: 'com.sahool.app',
                ),
                // خطوط بين النقاط
                if (_points.length >= 2)
                  PolylineLayer(
                    polylines: [
                      Polyline(
                        points: [
                          ..._points,
                          if (_points.length >= 3) _points.first,
                        ],
                        color: SahoolColors.primary,
                        strokeWidth: 2.0,
                      ),
                    ],
                  ),
                // طبقة المضلع المملوء
                if (_points.length >= 3)
                  PolygonLayer(
                    polygons: [
                      Polygon(
                        points: _points,
                        color: SahoolColors.primary.withValues(alpha: 0.2),
                        borderColor: SahoolColors.primary,
                        borderStrokeWidth: 2.0,
                      ),
                    ],
                  ),
                // علامات النقاط
                MarkerLayer(
                  markers: _points.asMap().entries.map((entry) {
                    final i = entry.key;
                    final p = entry.value;
                    return Marker(
                      point: p,
                      width: 24,
                      height: 24,
                      child: GestureDetector(
                        onTap: () {
                          // إزالة النقطة عند الضغط عليها
                          setState(() => _points.removeAt(i));
                          final area = _calcAreaHa(_points);
                          ref
                              .read(fieldWizardProvider.notifier)
                              .updatePolygon(List.from(_points), area);
                        },
                        child: Container(
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: i == 0
                                ? SahoolColors.danger
                                : SahoolColors.primary,
                            border: Border.all(
                                color: Colors.white, width: 2),
                          ),
                          child: Center(
                            child: Text(
                              '${i + 1}',
                              style: const TextStyle(
                                  color: Colors.white, fontSize: 9),
                            ),
                          ),
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ],
            ),
            // تلميح
            Positioned(
              top: 8,
              right: 8,
              child: Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(
                  color: Colors.black54,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Text(
                  'انقر لإضافة نقطة',
                  style: TextStyle(color: Colors.white, fontSize: 11),
                ),
              ),
            ),
          ],
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
            color: Colors.grey[100],
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: Colors.grey[300]!),
          ),
          child: Row(
            children: [
              const Icon(Icons.straighten,
                  color: SahoolColors.primary, size: 22),
              const SizedBox(width: 12),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'المساحة',
                    style: TextStyle(
                      color: SahoolColors.textSecondary,
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
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey[300]!),
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
                      ? SahoolColors.textDark
                      : Colors.grey[500],
                ),
              ),
            ),
            if (value != null)
              GestureDetector(
                onTap: () => onPick(null),
                child: const Icon(Icons.clear,
                    color: Colors.grey, size: 18),
              ),
            if (value == null)
              const Icon(Icons.calendar_today,
                  color: Colors.grey, size: 18),
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
            style: const TextStyle(
              color: SahoolColors.textSecondary,
              fontSize: 13,
            ),
          ),
          Expanded(
            child: Text(
              value,
              style: const TextStyle(
                color: SahoolColors.textDark,
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
            : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isSelected ? SahoolColors.primary : Colors.grey[300]!,
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
                  : SahoolColors.textDark,
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
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: SahoolColors.textDark,
          ),
        ),
      ],
    );
  }
}
