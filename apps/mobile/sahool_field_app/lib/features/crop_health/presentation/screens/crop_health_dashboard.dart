import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';

import '../../domain/entities/crop_health_entities.dart';
import '../providers/crop_health_provider.dart';
import '../widgets/diagnosis_summary_card.dart';
import '../widgets/action_list_tile.dart';
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
    Future.microtask(() {
      ref
          .read(diagnosisProvider.notifier)
          .loadDiagnosis(widget.fieldId, DateTime.now());
      ref.read(zonesProvider.notifier).loadZones(widget.fieldId);
    });
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
              },
            ),
          ),
        ),

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
        SliverPadding(
          padding: const EdgeInsets.all(16),
          sliver: SliverList(
            delegate: SliverChildBuilderDelegate(
              (context, index) {
                final filteredActions = ref.watch(priorityFilteredActionsProvider);
                if (index >= filteredActions.length) return null;

                final action = filteredActions[index];
                return Padding(
                  padding: const EdgeInsets.only(bottom: 12),
                  child: ActionListTile(
                    action: action,
                    onTap: () => _showActionDetails(action),
                  ),
                );
              },
              childCount: ref.watch(priorityFilteredActionsProvider).length,
            ),
          ),
        ),

        // مساحة إضافية في الأسفل
        const SliverToBoxAdapter(
          child: SizedBox(height: 80),
        ),
      ],
    );
  }

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
      selectedColor: const Color(0xFF367C2B).withOpacity(0.2),
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
      selectedColor: const Color(0xFF367C2B).withOpacity(0.2),
      checkmarkColor: const Color(0xFF367C2B),
    );
  }

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
      await ref.read(diagnosisProvider.notifier).loadDiagnosis(widget.fieldId, picked);
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
                  color: Colors.green.withOpacity(0.1),
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
                  color: Colors.blue.withOpacity(0.1),
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
                            // TODO: Navigate to zone on map
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
                            // TODO: Mark as done
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

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
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
}
