import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:path_provider/path_provider.dart';

import '../../domain/entities/crop_health_entities.dart';
import '../providers/crop_health_provider.dart';
import '../widgets/diagnosis_summary_card.dart';
import '../widgets/action_list_tile.dart';
import '../widgets/health_chart_widget.dart';
import '../widgets/zone_selector.dart';

/// شاشة لوحة تحكم صحة المحاصيل
/// NDVI Dashboard with Diagnosis
class CropHealthDashboard extends ConsumerStatefulWidget {
  final String fieldId;
  final String? fieldName;

  const CropHealthDashboard({
    super.key,
    required this.fieldId,
    this.fieldName,
  });

  @override
  ConsumerState<CropHealthDashboard> createState() =>
      _CropHealthDashboardState();
}

class _CropHealthDashboardState extends ConsumerState<CropHealthDashboard> {
  @override
  void initState() {
    super.initState();
    // تحميل البيانات عند فتح الشاشة
    Future.microtask(() async {
      final now = DateTime.now();
      ref.read(selectedDateProvider.notifier).state = now;
      ref.read(selectedPeriodDaysProvider.notifier).state = 1;
      await ref.read(diagnosisProvider.notifier).loadDiagnosis(widget.fieldId, now);
      await ref.read(zonesProvider.notifier).loadZones(widget.fieldId);
      _loadTimelineForCurrentPeriod();
    });
  }

  /// تحميل السلسلة الزمنية للمنطقة الأولى (أو المحددة) بناءً على الفترة الزمنية.
  void _loadTimelineForCurrentPeriod() {
    final zones = ref.read(zonesProvider).zones;
    final endDate = ref.read(selectedDateProvider);
    final periodDays = ref.read(selectedPeriodDaysProvider);
    final startDate = endDate.subtract(Duration(days: periodDays - 1));
    // Prefer the explicitly selected zone; fall back to the first available.
    final selectedZone = ref.read(selectedZoneIdProvider);
    final zoneId = selectedZone ?? (zones.isNotEmpty ? zones.first.zoneId : null);
    if (zoneId != null) {
      ref.read(timelineProvider.notifier).loadTimeline(
            widget.fieldId,
            zoneId,
            from: startDate,
            to: endDate,
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    final diagnosisState = ref.watch(diagnosisProvider);
    final zonesState = ref.watch(zonesProvider);
    final selectedDate = ref.watch(selectedDateProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.fieldName ?? 'صحة المحاصيل'),
          backgroundColor: const Color(0xFF367C2B), // John Deere Green
          foregroundColor: Colors.white,
          actions: [
            // تاريخ التشخيص
            IconButton(
              icon: const Icon(Icons.calendar_today),
              onPressed: () => _selectDate(context),
              tooltip: 'اختر التاريخ',
            ),
            // تصدير VRT
            IconButton(
              icon: const Icon(Icons.download),
              onPressed: diagnosisState.diagnosis != null
                  ? () => _showExportOptions(context)
                  : null,
              tooltip: 'تصدير VRT',
            ),
            // تحديث
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => _refreshData(),
              tooltip: 'تحديث',
            ),
          ],
        ),
        body: RefreshIndicator(
          onRefresh: _refreshData,
          child: diagnosisState.isLoading
              ? const Center(child: CircularProgressIndicator())
              : diagnosisState.error != null
                  ? _buildErrorView(diagnosisState.error!)
                  : diagnosisState.diagnosis != null
                      ? _buildDashboard(diagnosisState.diagnosis!)
                      : const Center(child: Text('لا توجد بيانات')),
        ),
      ),
    );
  }

  Widget _buildDashboard(FieldDiagnosis diagnosis) {
    return CustomScrollView(
      slivers: [
        // بطاقة الملخص
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: DiagnosisSummaryCard(summary: diagnosis.summary),
          ),
        ),

        // اختيار المنطقة
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: ZoneSelector(
              zones: ref.watch(zonesProvider).zones,
              selectedZoneId: ref.watch(selectedZoneIdProvider),
              onZoneSelected: (zoneId) {
                ref.read(selectedZoneIdProvider.notifier).state = zoneId;
                // إعادة تحميل السلسلة الزمنية عند تغيير المنطقة
                final endDate = ref.read(selectedDateProvider);
                final periodDays = ref.read(selectedPeriodDaysProvider);
                final startDate = endDate.subtract(Duration(days: periodDays - 1));
                ref.read(timelineProvider.notifier).loadTimeline(
                      widget.fieldId,
                      zoneId,
                      from: startDate,
                      to: endDate,
                    );
              },
            ),
          ),
        ),

        // أزرار الفترة الزمنية السريعة
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 0),
            child: _buildPeriodPresets(),
          ),
        ),

        const SliverToBoxAdapter(child: SizedBox(height: 8)),

        // رسم NDVI الزمني
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: _buildNdviTrendSection(),
          ),
        ),

        const SliverToBoxAdapter(child: SizedBox(height: 8)),

        // فلتر الإجراءات
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: _buildActionFilters(),
          ),
        ),

        // قائمة الإجراءات
        SliverToBoxAdapter(
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Text(
              'الإجراءات المطلوبة (${diagnosis.actions.length})',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
          ),
        ),

        // قائمة الإجراءات
        Consumer(
          builder: (context, ref, _) {
            final filteredActions = ref.watch(priorityFilteredActionsProvider);
            if (filteredActions.isEmpty) {
              return SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(32),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.check_circle_outline, size: 48, color: Colors.green[300]),
                      const SizedBox(height: 12),
                      const Text(
                        'لا توجد إجراءات للفترة المحددة',
                        style: TextStyle(color: Colors.grey),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
              );
            }
            return SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildBuilderDelegate(
                  (context, index) {
                    final action = filteredActions[index];
                    return Padding(
                      padding: const EdgeInsets.only(bottom: 12),
                      child: ActionListTile(
                        action: action,
                        onTap: () => _showActionDetails(action),
                      ),
                    );
                  },
                  childCount: filteredActions.length,
                ),
              ),
            );
          },
        ),

        // مساحة إضافية في الأسفل
        const SliverToBoxAdapter(
          child: SizedBox(height: 80),
        ),
      ],
    );
  }

  // ─── NDVI Trend Section ───────────────────────────────────────────────────

  /// قسم السلسلة الزمنية لـ NDVI مع اتجاه التغير.
  Widget _buildNdviTrendSection() {
    final timelineState = ref.watch(timelineProvider);
    final periodDays = ref.watch(selectedPeriodDaysProvider);

    // اليوم الواحد لا يُنتج سلسلة زمنية — أظهر placeholder بدلاً من إخفاء القسم
    // كلياً لتجنب قفزة التخطيط عند تغيير الفترة.
    if (periodDays <= 1) {
      return Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Row(
            children: [
              Icon(Icons.show_chart, color: Colors.grey.shade400),
              const SizedBox(width: 12),
              Expanded(
                child: Text(
                  'اختر فترة أسبوع أو أطول لعرض اتجاه NDVI الزمني',
                  style: TextStyle(color: Colors.grey.shade500),
                ),
              ),
            ],
          ),
        ),
      );
    }

    if (timelineState.isLoading) {
      return const Card(
        elevation: 2,
        child: Padding(
          padding: EdgeInsets.all(24),
          child: Center(child: CircularProgressIndicator()),
        ),
      );
    }

    final series = timelineState.timeline?.series ?? [];

    // Filter out any points whose date field cannot be parsed — fail visibly
    // rather than silently substituting DateTime.now() which would corrupt the chart.
    // Log a warning so data-quality issues are visible in debug builds.
    final dataPoints = series
        .map((p) {
          final dt = DateTime.tryParse(p.date);
          if (dt == null) {
            debugPrint('[CropHealth] Skipping NDVI point: unparseable date "${p.date}"');
            return null;
          }
          return HealthDataPoint(date: dt, value: p.ndvi);
        })
        .whereType<HealthDataPoint>()
        .toList();

    if (dataPoints.isEmpty) {
      return Card(
        elevation: 2,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        child: const Padding(
          padding: EdgeInsets.all(24),
          child: Center(
            child: Text(
              'لا توجد بيانات NDVI للفترة المحددة',
              style: TextStyle(color: Colors.grey),
            ),
          ),
        ),
      );
    }

    final trend = _computeTrend(dataPoints);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Text(
              'اتجاه NDVI',
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(width: 8),
            _buildTrendBadge(trend),
          ],
        ),
        const SizedBox(height: 8),
        HealthChartWidget(
          dataPoints: dataPoints,
          title: 'NDVI — ${_periodLabel(periodDays)} (حسب البيانات المتاحة)',
          lineColor: const Color(0xFF367C2B),
        ),
      ],
    );
  }

  /// حساب اتجاه NDVI باستخدام متوسط نقاط البداية والنهاية
  /// لتقليل تأثير الضجيج على الإشارة الاتجاهية.
  ///
  /// Window size degrades gradually with series length:
  ///   length ≥ 6  → window = 3  (full noise-dampening)
  ///   length = 4–5 → window = 2  (partial dampening)
  ///   length = 2–3 → window = 1  (avg of first 1 vs avg of last 1,
  ///                                mathematically equivalent to first-vs-last
  ///                                but uses the same code path for consistency)
  ///
  /// Formula: window = (length ~/ 2).clamp(1, 3)
  ///
  /// Confidence is `(length / 10).clamp(0.0, 1.0)` — series shorter than
  /// 10 points cannot fully resolve trend from cloud noise; the badge
  /// displays a low-confidence notice below 0.5 (< 5 satellite passes).
  _NdviTrendResult _computeTrend(List<HealthDataPoint> points) {
    if (points.length < 2) {
      return const _NdviTrendResult(_NdviTrend.stable, 0.0);
    }

    double _avg(Iterable<HealthDataPoint> pts) {
      final values = pts.map((p) => p.value).toList();
      return values.reduce((a, b) => a + b) / values.length;
    }

    // Gradual window: half the series length, capped at 3.
    final windowSize = (points.length ~/ 2).clamp(1, 3);
    final startAvg = _avg(points.take(windowSize));
    final endAvg = _avg(points.reversed.take(windowSize));

    // Confidence: normalized series length (10+ passes = full confidence).
    final confidence = (points.length / 10).clamp(0.0, 1.0);

    final delta = endAvg - startAvg;
    if (delta > 0.05) return _NdviTrendResult(_NdviTrend.improving, confidence);
    if (delta < -0.05) return _NdviTrendResult(_NdviTrend.declining, confidence);
    return _NdviTrendResult(_NdviTrend.stable, confidence);
  }

  Widget _buildTrendBadge(_NdviTrendResult result) {
    final (icon, label, color) = switch (result.direction) {
      _NdviTrend.improving => (Icons.trending_up, '↑ تحسّن', Colors.green),
      _NdviTrend.declining => (Icons.trending_down, '↓ تراجع', Colors.red),
      _NdviTrend.stable => (Icons.trending_flat, '→ مستقر', Colors.orange),
    };
    // Show a low-confidence notice when fewer than 5 satellite passes are
    // available (confidence < 0.5).  This prevents farmers from acting on a
    // 2-point "trend" as if it were a statistically reliable signal.
    final confidenceLabel = result.confidence < 0.5 ? ' (ثقة منخفضة)' : '';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.4)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            '$label$confidenceLabel',
            style: TextStyle(fontSize: 12, color: color, fontWeight: FontWeight.bold),
          ),
        ],
      ),
    );
  }

  String _periodLabel(int days) => switch (days) {
        7 => 'آخر 7 أيام',
        30 => 'آخر 30 يوم',
        90 => 'آخر 3 أشهر',
        _ => 'اليوم',
      };

  Widget _buildActionFilters() {
    final currentFilter = ref.watch(actionFilterProvider);
    final priorityFilter = ref.watch(priorityFilterProvider);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // فلتر نوع الإجراء
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildFilterChip('الكل', null, currentFilter),
              const SizedBox(width: 8),
              _buildFilterChip('💧 ري', 'irrigation', currentFilter),
              const SizedBox(width: 8),
              _buildFilterChip('🌱 تسميد', 'fertilization', currentFilter),
              const SizedBox(width: 8),
              _buildFilterChip('🔍 تفقد', 'scouting', currentFilter),
            ],
          ),
        ),

        const SizedBox(height: 8),

        // فلتر الأولوية
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildPriorityChip('الكل', null, priorityFilter),
              const SizedBox(width: 8),
              _buildPriorityChip('🔴 عاجل', 'P0', priorityFilter),
              const SizedBox(width: 8),
              _buildPriorityChip('🟠 مهم', 'P1', priorityFilter),
              const SizedBox(width: 8),
              _buildPriorityChip('🔵 متوسط', 'P2', priorityFilter),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildFilterChip(String label, String? value, String? current) {
    final isSelected = current == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        ref.read(actionFilterProvider.notifier).state = value;
      },
      selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.2),
      checkmarkColor: const Color(0xFF367C2B),
    );
  }

  Widget _buildPriorityChip(String label, String? value, String? current) {
    final isSelected = current == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {
        ref.read(priorityFilterProvider.notifier).state = value;
      },
      selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.2),
      checkmarkColor: const Color(0xFF367C2B),
    );
  }

  /// Period preset quick-select row.
  /// أزرار الفترة الزمنية السريعة (اليوم / أسبوع / شهر / 3 أشهر).
  Widget _buildPeriodPresets() {
    final selectedDate = ref.watch(selectedDateProvider);
    final selectedPeriodDays = ref.watch(selectedPeriodDaysProvider);
    final now = DateTime.now();

    // (label, endDate, periodDays)
    final presets = <(String, DateTime, int)>[
      ('اليوم', now, 1),
      ('أسبوع', now, 7),
      ('شهر', now, 30),
      ('3 أشهر', now, 90),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Icon(Icons.history_toggle_off, size: 16, color: Color(0xFF367C2B)),
            const SizedBox(width: 6),
            Text(
              selectedPeriodDays == 1
                  ? 'التاريخ: ${_formatDate(selectedDate)}'
                  : 'الفترة: آخر $selectedPeriodDays يوم (حتى ${_formatDate(selectedDate)})',
              style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.w600,
                color: Color(0xFF367C2B),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: presets.map((preset) {
              final (label, endDate, days) = preset;
              final isActive = selectedPeriodDays == days;
              return Padding(
                padding: const EdgeInsets.only(left: 8),
                child: ChoiceChip(
                  label: Text(label),
                  selected: isActive,
                  selectedColor: const Color(0xFF367C2B).withValues(alpha: 0.15),
                  labelStyle: TextStyle(
                    color: isActive ? const Color(0xFF367C2B) : Colors.grey[700],
                    fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                    fontSize: 13,
                  ),
                  onSelected: (_) async {
                    ref.read(selectedDateProvider.notifier).state = endDate;
                    ref.read(selectedPeriodDaysProvider.notifier).state = days;
                    // تحميل التشخيص للتاريخ المحدد
                    await ref
                        .read(diagnosisProvider.notifier)
                        .loadDiagnosis(widget.fieldId, endDate);
                    // تحميل السلسلة الزمنية للفترة المحددة
                    _loadTimelineForCurrentPeriod();
                  },
                ),
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  String _formatDate(DateTime dt) =>
      '${dt.day.toString().padLeft(2, '0')}/${dt.month.toString().padLeft(2, '0')}/${dt.year}';

  Widget _buildErrorView(String error) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.red),
            const SizedBox(height: 16),
            Text(
              error,
              textAlign: TextAlign.center,
              style: const TextStyle(color: Colors.red),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshData,
              icon: const Icon(Icons.refresh),
              label: const Text('إعادة المحاولة'),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _refreshData() async {
    final date = ref.read(selectedDateProvider);
    await ref.read(diagnosisProvider.notifier).loadDiagnosis(widget.fieldId, date);
    await ref.read(zonesProvider.notifier).loadZones(widget.fieldId);
    _loadTimelineForCurrentPeriod();
  }

  Future<void> _selectDate(BuildContext context) async {
    final currentDate = ref.read(selectedDateProvider);
    final picked = await showDatePicker(
      context: context,
      initialDate: currentDate,
      firstDate: DateTime.now().subtract(const Duration(days: 365)),
      lastDate: DateTime.now(),
      locale: const Locale('ar'),
    );

    if (picked != null) {
      ref.read(selectedDateProvider.notifier).state = picked;
      ref.read(selectedPeriodDaysProvider.notifier).state = 1;
      await ref.read(diagnosisProvider.notifier).loadDiagnosis(widget.fieldId, picked);
      _loadTimelineForCurrentPeriod();
    }
  }

  void _showExportOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.water_drop, color: Colors.blue),
                title: const Text('تصدير خريطة الري'),
                subtitle: const Text('VRT للمناطق التي تحتاج ري'),
                onTap: () {
                  Navigator.pop(context);
                  _exportVrt('irrigation');
                },
              ),
              ListTile(
                leading: const Icon(Icons.eco, color: Colors.green),
                title: const Text('تصدير خريطة التسميد'),
                subtitle: const Text('VRT للمناطق التي تحتاج تسميد'),
                onTap: () {
                  Navigator.pop(context);
                  _exportVrt('fertilization');
                },
              ),
              ListTile(
                leading: const Icon(Icons.map, color: Colors.orange),
                title: const Text('تصدير كل الإجراءات'),
                subtitle: const Text('GeoJSON شامل لجميع التوصيات'),
                onTap: () {
                  Navigator.pop(context);
                  _exportVrt('all');
                },
              ),
            ],
          ),
        ),
      ),
    );
  }

  Future<void> _exportVrt(String actionType) async {
    final diagnosisState = ref.read(diagnosisProvider);
    final zonesState = ref.read(zonesProvider);
    final date = ref.read(selectedDateProvider);

    if (diagnosisState.diagnosis == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('لا توجد بيانات للتصدير'),
          backgroundColor: Colors.orange,
        ),
      );
      return;
    }

    // Show loading indicator
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 16),
            Text('جاري تصدير VRT ($actionType)...'),
          ],
        ),
        backgroundColor: const Color(0xFF367C2B),
        duration: const Duration(seconds: 2),
      ),
    );

    try {
      final diagnosis = diagnosisState.diagnosis!;
      final zones = zonesState.zones ?? [];

      // Filter actions based on type
      List<DiagnosisAction> actionsToExport;
      if (actionType == 'all') {
        actionsToExport = diagnosis.actions;
      } else {
        actionsToExport =
            diagnosis.actions.where((a) => a.type == actionType).toList();
      }

      // Build GeoJSON FeatureCollection
      final features = <Map<String, dynamic>>[];

      for (final action in actionsToExport) {
        // Find zone geometry
        final zone = zones.where((z) => z.zoneId == action.zoneId).firstOrNull;
        final geometry = zone?.geometry ?? _defaultGeometry(action.zoneId);

        features.add({
          'type': 'Feature',
          'properties': {
            'zone_id': action.zoneId,
            'zone_name': zone?.nameAr ?? zone?.name ?? action.zoneId,
            'action_type': action.type,
            'action_type_ar': _getActionTypeAr(action.type),
            'priority': action.priority,
            'priority_label': action.priorityLabel,
            'title': action.title,
            'reason': action.reason,
            'severity': action.severity,
            'recommended_dose': action.recommendedDoseHint,
            'recommended_window_hours': action.recommendedWindowHours,
            'evidence': action.evidence,
            'export_date': DateTime.now().toIso8601String(),
            'diagnosis_date': diagnosis.date,
          },
          'geometry': geometry,
        });
      }

      final geojson = {
        'type': 'FeatureCollection',
        'name': 'SAHOOL_VRT_${actionType}_${diagnosis.date}',
        'crs': {
          'type': 'name',
          'properties': {'name': 'urn:ogc:def:crs:EPSG::4326'},
        },
        'features': features,
        'metadata': {
          'field_id': diagnosis.fieldId,
          'field_name': widget.fieldName,
          'export_type': actionType,
          'diagnosis_date': diagnosis.date,
          'total_zones': diagnosis.summary.zonesTotal,
          'critical_zones': diagnosis.summary.zonesCritical,
          'warning_zones': diagnosis.summary.zonesWarning,
          'ok_zones': diagnosis.summary.zonesOk,
          'exported_actions_count': actionsToExport.length,
          'generated_by': 'SAHOOL Field App',
          'generated_at': DateTime.now().toIso8601String(),
        },
      };

      // Save to file
      final directory = await getApplicationDocumentsDirectory();
      final fileName =
          'sahool_vrt_${actionType}_${diagnosis.date.replaceAll('-', '')}.geojson';
      final file = File('${directory.path}/$fileName');
      await file.writeAsString(
        const JsonEncoder.withIndent('  ').convert(geojson),
      );

      if (mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        _showExportSuccess(file.path, fileName, actionsToExport.length);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل التصدير: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  void _showExportSuccess(String filePath, String fileName, int actionsCount) {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          title: Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(Icons.check_circle, color: Colors.green),
              ),
              const SizedBox(width: 12),
              const Text('تم التصدير بنجاح'),
            ],
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildInfoRow('اسم الملف:', fileName),
              const SizedBox(height: 8),
              _buildInfoRow('عدد الإجراءات:', '$actionsCount'),
              const SizedBox(height: 8),
              _buildInfoRow('الموقع:', 'مجلد التطبيق'),
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.blue.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.info_outline, color: Colors.blue, size: 20),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        'يمكنك استخدام هذا الملف مع أنظمة VRT أو برامج GIS',
                        style: TextStyle(fontSize: 13, color: Colors.blue),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إغلاق'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey)),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.w500),
          ),
        ),
      ],
    );
  }

  String _getActionTypeAr(String type) {
    switch (type) {
      case 'irrigation':
        return 'ري';
      case 'fertilization':
        return 'تسميد';
      case 'scouting':
        return 'استكشاف';
      default:
        return 'أخرى';
    }
  }

  Map<String, dynamic> _defaultGeometry(String zoneId) {
    // Default placeholder geometry for zones without geometry data
    return {
      'type': 'Polygon',
      'coordinates': [
        [
          [0, 0],
          [0, 0.001],
          [0.001, 0.001],
          [0.001, 0],
          [0, 0],
        ]
      ],
    };
  }

  void _showActionDetails(DiagnosisAction action) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: DraggableScrollableSheet(
          initialChildSize: 0.6,
          maxChildSize: 0.9,
          minChildSize: 0.3,
          expand: false,
          builder: (context, scrollController) => SingleChildScrollView(
            controller: scrollController,
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // الأيقونة والعنوان
                  Row(
                    children: [
                      Text(
                        action.typeIcon,
                        style: const TextStyle(fontSize: 32),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              action.title,
                              style: Theme.of(context).textTheme.titleLarge,
                            ),
                            Text(
                              action.priorityLabel,
                              style: TextStyle(
                                color: Color(int.parse(
                                    action.priorityColor.replaceFirst('#', '0xFF'))),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),

                  const Divider(height: 32),

                  // السبب
                  Text(
                    'السبب',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(action.reason),

                  const SizedBox(height: 24),

                  // الأدلة
                  Text(
                    'الأدلة',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  ...action.evidence.entries.map((e) => Padding(
                        padding: const EdgeInsets.symmetric(vertical: 4),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(e.key.toUpperCase()),
                            Text(
                              e.value is num
                                  ? (e.value as num).toStringAsFixed(2)
                                  : e.value.toString(),
                              style: const TextStyle(fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                      )),

                  const SizedBox(height: 24),

                  // التوصيات
                  if (action.recommendedWindowHours != null) ...[
                    _buildInfoRow(
                      'النافذة الزمنية',
                      '${action.recommendedWindowHours} ساعة',
                    ),
                  ],
                  if (action.recommendedDoseHint != null) ...[
                    _buildInfoRow(
                      'كمية الجرعة',
                      _getDoseLabel(action.recommendedDoseHint!),
                    ),
                  ],

                  const SizedBox(height: 32),

                  // أزرار الإجراء
                  Row(
                    children: [
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () {
                            Navigator.pop(context);
                            _navigateToZoneOnMap(action.zoneId);
                          },
                          icon: const Icon(Icons.map),
                          label: const Text('عرض على الخريطة'),
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () {
                            Navigator.pop(context);
                            _markActionAsDone(action);
                          },
                          icon: const Icon(Icons.check),
                          label: const Text('تم التنفيذ'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF367C2B),
                          ),
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
    );
  }

  String _getDoseLabel(String hint) {
    switch (hint) {
      case 'low':
        return 'منخفضة';
      case 'medium':
        return 'متوسطة';
      case 'high':
        return 'عالية';
      default:
        return hint;
    }
  }

  /// Navigate to map screen and focus on the specified zone
  void _navigateToZoneOnMap(String zoneId) {
    final zonesState = ref.read(zonesProvider);
    final zone = zonesState.zones.where((z) => z.zoneId == zoneId).firstOrNull;

    context.push('/map', extra: {
      'zoneId': zoneId,
      'zoneName': zone?.nameAr ?? zone?.name ?? zoneId,
      'geometry': zone?.geometry,
      'fieldId': widget.fieldId,
      'fieldName': widget.fieldName,
    });
  }

  /// Mark an action as completed
  Future<void> _markActionAsDone(DiagnosisAction action) async {
    // Show loading indicator
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.white,
              ),
            ),
            const SizedBox(width: 16),
            Text('جاري تحديث الإجراء: ${action.title}...'),
          ],
        ),
        backgroundColor: const Color(0xFF367C2B),
        duration: const Duration(seconds: 30), // Long duration, will be dismissed
      ),
    );

    try {
      // Call the provider to mark the action as completed
      await ref.read(diagnosisProvider.notifier).markActionCompleted(
            widget.fieldId,
            action.zoneId,
            action.type,
          );

      if (mounted) {
        // Hide loading and show success
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('تم تنفيذ: ${action.title}'),
                ),
              ],
            ),
            backgroundColor: Colors.green,
            duration: const Duration(seconds: 3),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        // Hide loading and show error
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.error_outline, color: Colors.white),
                const SizedBox(width: 12),
                Expanded(
                  child: Text('فشل تحديث الإجراء: ${e.toString()}'),
                ),
              ],
            ),
            backgroundColor: Colors.red,
            duration: const Duration(seconds: 4),
            action: SnackBarAction(
              label: 'إعادة المحاولة',
              textColor: Colors.white,
              onPressed: () => _markActionAsDone(action),
            ),
          ),
        );
      }
    }
  }
}

/// اتجاه تغير NDVI عبر الفترة الزمنية.
enum _NdviTrend { improving, declining, stable }

/// نتيجة تحليل الاتجاه تجمع بين الاتجاه ومستوى الثقة.
///
/// [confidence] is normalized to [0.0, 1.0] using `series.length / 10`:
///   - 2 points  → 0.2 (very low)
///   - 5 points  → 0.5 (moderate)
///   - 10+ points → 1.0 (full confidence)
///
/// The UI shows a low-confidence notice when [confidence] < 0.5 (fewer than
/// 5 satellite passes), because a 2–4-point series cannot reliably distinguish
/// a real trend from cloud-induced noise even with window averaging.
class _NdviTrendResult {
  final _NdviTrend direction;
  final double confidence;
  const _NdviTrendResult(this.direction, this.confidence);
}
