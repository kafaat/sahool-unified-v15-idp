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

  bool _isArabic(BuildContext context) {
    return Localizations.localeOf(context).languageCode == 'ar';
  }

  @override
  Widget build(BuildContext context) {
    final isArabic = _isArabic(context);
    final diagnosisState = ref.watch(diagnosisProvider);
    final zonesState = ref.watch(zonesProvider);
    final selectedDate = ref.watch(selectedDateProvider);

    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.fieldName ?? (isArabic ? 'صحة المحاصيل' : 'Crop Health')),
          backgroundColor: const Color(0xFF367C2B), // John Deere Green
          foregroundColor: Colors.white,
          actions: [
            // تاريخ التشخيص
            IconButton(
              icon: const Icon(Icons.calendar_today),
              onPressed: () => _selectDate(context),
              tooltip: isArabic ? 'اختر التاريخ' : 'Select Date',
            ),
            // تصدير VRT
            IconButton(
              icon: const Icon(Icons.download),
              onPressed: diagnosisState.diagnosis != null
                  ? () => _showExportOptions(context)
                  : null,
              tooltip: isArabic ? 'تصدير VRT' : 'Export VRT',
            ),
            // تحديث
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: () => _refreshData(),
              tooltip: isArabic ? 'تحديث' : 'Refresh',
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
                      : Center(child: Text(isArabic ? 'لا توجد بيانات' : 'No data available')),
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
              _isArabic(context)
                  ? 'الإجراءات المطلوبة (${diagnosis.actions.length})'
                  : 'Required Actions (${diagnosis.actions.length})',
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
              _buildFilterChip(_isArabic(context) ? 'الكل' : 'All', null, currentFilter),
              const SizedBox(width: 8),
              _buildFilterChip(_isArabic(context) ? '💧 ري' : '💧 Irrigation', 'irrigation', currentFilter),
              const SizedBox(width: 8),
              _buildFilterChip(_isArabic(context) ? '🌱 تسميد' : '🌱 Fertilization', 'fertilization', currentFilter),
              const SizedBox(width: 8),
              _buildFilterChip(_isArabic(context) ? '🔍 تفقد' : '🔍 Scouting', 'scouting', currentFilter),
            ],
          ),
        ),

        const SizedBox(height: 8),

        // فلتر الأولوية
        SingleChildScrollView(
          scrollDirection: Axis.horizontal,
          child: Row(
            children: [
              _buildPriorityChip(_isArabic(context) ? 'الكل' : 'All', null, priorityFilter),
              const SizedBox(width: 8),
              _buildPriorityChip(_isArabic(context) ? '🔴 عاجل' : '🔴 Urgent', 'P0', priorityFilter),
              const SizedBox(width: 8),
              _buildPriorityChip(_isArabic(context) ? '🟠 مهم' : '🟠 Important', 'P1', priorityFilter),
              const SizedBox(width: 8),
              _buildPriorityChip(_isArabic(context) ? '🔵 متوسط' : '🔵 Medium', 'P2', priorityFilter),
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
              label: Text(_isArabic(context) ? 'إعادة المحاولة' : 'Retry'),
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
      locale: Locale(_isArabic(context) ? 'ar' : 'en'),
    );

    if (picked != null) {
      ref.read(selectedDateProvider.notifier).state = picked;
      await ref.read(diagnosisProvider.notifier).loadDiagnosis(widget.fieldId, picked);
    }
  }

  void _showExportOptions(BuildContext context) {
    final isAr = _isArabic(context);
    showModalBottomSheet(
      context: context,
      builder: (context) => Directionality(
        textDirection: isAr ? TextDirection.rtl : TextDirection.ltr,
        child: SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.water_drop, color: Colors.blue),
                title: Text(isAr ? 'تصدير خريطة الري' : 'Export Irrigation Map'),
                subtitle: Text(isAr ? 'VRT للمناطق التي تحتاج ري' : 'VRT for zones needing irrigation'),
                onTap: () {
                  Navigator.pop(context);
                  _exportVrt('irrigation');
                },
              ),
              ListTile(
                leading: const Icon(Icons.eco, color: Colors.green),
                title: Text(isAr ? 'تصدير خريطة التسميد' : 'Export Fertilization Map'),
                subtitle: Text(isAr ? 'VRT للمناطق التي تحتاج تسميد' : 'VRT for zones needing fertilization'),
                onTap: () {
                  Navigator.pop(context);
                  _exportVrt('fertilization');
                },
              ),
              ListTile(
                leading: const Icon(Icons.map, color: Colors.orange),
                title: Text(isAr ? 'تصدير كل الإجراءات' : 'Export All Actions'),
                subtitle: Text(isAr ? 'GeoJSON شامل لجميع التوصيات' : 'Complete GeoJSON for all recommendations'),
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
        SnackBar(
          content: Text(_isArabic(context) ? 'لا توجد بيانات للتصدير' : 'No data to export'),
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
