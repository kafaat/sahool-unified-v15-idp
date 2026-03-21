/// Report Builder Screen - شاشة بناء التقرير
/// Configure filters and generate reports
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/auth/secure_storage_service.dart';
import '../../domain/models/report_template.dart';
import '../../domain/models/report_filter.dart';
import '../widgets/filter_chips_widget.dart';
import '../widgets/date_range_picker_widget.dart';
import '../../state/reports_providers.dart';
import 'report_viewer_screen.dart';

/// Report Builder Screen
/// شاشة بناء وتكوين التقرير
class ReportBuilderScreen extends ConsumerStatefulWidget {
  final ReportTemplate template;

  const ReportBuilderScreen({
    super.key,
    required this.template,
  });

  @override
  ConsumerState<ReportBuilderScreen> createState() => _ReportBuilderScreenState();
}

class _ReportBuilderScreenState extends ConsumerState<ReportBuilderScreen> {
  late ReportFilter _filter;
  final _titleController = TextEditingController();
  bool _isGenerating = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _filter = ReportFilter(
      dateRangePreset: _getDefaultPreset(),
      dateRange: _getDefaultPreset().toDateRange(),
    );
  }

  DateRangePreset _getDefaultPreset() {
    final days = widget.template.defaultDateRangeDays;
    if (days <= 7) return DateRangePreset.last7Days;
    if (days <= 30) return DateRangePreset.last30Days;
    if (days <= 90) return DateRangePreset.last90Days;
    return DateRangePreset.thisYear;
  }

  @override
  void dispose() {
    _titleController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text('إنشاء ${widget.template.nameAr}'),
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Template info
              _buildTemplateHeader(),
              const SizedBox(height: 24),

              // Custom title
              _buildTitleSection(),
              const SizedBox(height: 24),

              // Date range selection
              _buildDateRangeSection(),
              const SizedBox(height: 24),

              // Field filter (if supported)
              if (widget.template.supportsFieldFilter) ...[
                _buildFieldFilterSection(),
                const SizedBox(height: 24),
              ],

              // Additional filters based on template
              _buildAdditionalFilters(),
              const SizedBox(height: 24),

              // Options
              _buildOptionsSection(),
              const SizedBox(height: 32),

              // Error message
              if (_errorMessage != null) ...[
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.red.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.error, color: Colors.red),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          _errorMessage!,
                          style: const TextStyle(color: Colors.red),
                        ),
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

              // Generate button
              _buildGenerateButton(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTemplateHeader() {
    return Card(
      elevation: 0,
      color: SahoolColors.primary.withOpacity(0.05),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: SahoolColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(
                _getTemplateIcon(widget.template.type),
                color: SahoolColors.primary,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.template.nameAr,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.template.descriptionAr,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ),
            if (widget.template.supportsOffline)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.green.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Icon(
                  Icons.offline_bolt,
                  color: Colors.green,
                  size: 20,
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTitleSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'عنوان التقرير (اختياري)',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: _titleController,
          decoration: InputDecoration(
            hintText: widget.template.nameAr,
            prefixIcon: const Icon(Icons.edit),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildDateRangeSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'الفترة الزمنية',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        DateRangePickerWidget(
          selectedPreset: _filter.dateRangePreset,
          dateRange: _filter.dateRange,
          onPresetChanged: (preset) {
            setState(() {
              _filter = _filter.copyWith(
                dateRangePreset: preset,
                dateRange: preset.toDateRange(),
              );
            });
          },
          onDateRangeChanged: (range) {
            setState(() {
              _filter = _filter.copyWith(
                dateRangePreset: DateRangePreset.custom,
                dateRange: range,
              );
            });
          },
        ),
      ],
    );
  }

  Widget _buildFieldFilterSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'تصفية الحقول',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 8),
        FilterChipsWidget(
          selectedIds: _filter.fieldIds,
          filterType: FilterType.field,
          onSelectionChanged: (ids) {
            setState(() {
              _filter = _filter.copyWith(fieldIds: ids);
            });
          },
        ),
        const SizedBox(height: 8),
        Text(
          _filter.fieldIds.isEmpty
              ? 'سيتم تضمين جميع الحقول'
              : 'تم اختيار ${_filter.fieldIds.length} حقل',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildAdditionalFilters() {
    final filters = <Widget>[];

    // Task type filter for task completion report
    if (widget.template.type == ReportType.taskCompletion) {
      filters.add(_buildTaskTypeFilter());
    }

    // Crop type filter if applicable
    if (widget.template.optionalFields.contains('crop_type')) {
      filters.add(_buildCropTypeFilter());
    }

    if (filters.isEmpty) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'خيارات إضافية',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        ...filters,
      ],
    );
  }

  Widget _buildTaskTypeFilter() {
    final taskTypes = [
      {'id': null, 'name': 'جميع المهام'},
      {'id': 'irrigation', 'name': 'الري'},
      {'id': 'fertilization', 'name': 'التسميد'},
      {'id': 'spraying', 'name': 'الرش'},
      {'id': 'inspection', 'name': 'التفقد'},
      {'id': 'harvest', 'name': 'الحصاد'},
    ];

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: DropdownButtonFormField<String?>(
        value: _filter.taskType,
        decoration: InputDecoration(
          labelText: 'نوع المهمة',
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        items: taskTypes
            .map((type) => DropdownMenuItem<String?>(
                  value: type['id'],
                  child: Text(type['name'] as String),
                ))
            .toList(),
        onChanged: (value) {
          setState(() {
            _filter = _filter.copyWith(taskType: value);
          });
        },
      ),
    );
  }

  Widget _buildCropTypeFilter() {
    final cropTypes = [
      {'id': null, 'name': 'جميع المحاصيل'},
      {'id': 'wheat', 'name': 'قمح'},
      {'id': 'barley', 'name': 'شعير'},
      {'id': 'corn', 'name': 'ذرة'},
      {'id': 'alfalfa', 'name': 'برسيم'},
      {'id': 'tomato', 'name': 'طماطم'},
      {'id': 'date_palm', 'name': 'نخيل'},
    ];

    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: DropdownButtonFormField<String?>(
        value: _filter.cropType,
        decoration: InputDecoration(
          labelText: 'نوع المحصول',
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        items: cropTypes
            .map((type) => DropdownMenuItem<String?>(
                  value: type['id'],
                  child: Text(type['name'] as String),
                ))
            .toList(),
        onChanged: (value) {
          setState(() {
            _filter = _filter.copyWith(cropType: value);
          });
        },
      ),
    );
  }

  Widget _buildOptionsSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'إعدادات التقرير',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        Card(
          elevation: 1,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          child: Column(
            children: [
              SwitchListTile(
                title: const Text('مقارنة مع الفترة السابقة'),
                subtitle: const Text('إظهار التغيير مقارنة بالفترة السابقة'),
                value: _filter.compareWithPrevious,
                activeColor: SahoolColors.primary,
                onChanged: (value) {
                  setState(() {
                    _filter = _filter.copyWith(compareWithPrevious: value);
                  });
                },
              ),
              const Divider(height: 1),
              ListTile(
                title: const Text('ترتيب البيانات'),
                trailing: DropdownButton<String>(
                  value: _filter.sortBy ?? 'date',
                  underline: const SizedBox(),
                  items: const [
                    DropdownMenuItem(value: 'date', child: Text('التاريخ')),
                    DropdownMenuItem(value: 'name', child: Text('الاسم')),
                    DropdownMenuItem(value: 'value', child: Text('القيمة')),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _filter = _filter.copyWith(sortBy: value);
                    });
                  },
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildGenerateButton() {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: _isGenerating ? null : _generateReport,
        style: ElevatedButton.styleFrom(
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        child: _isGenerating
            ? const SizedBox(
                width: 24,
                height: 24,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: Colors.white,
                ),
              )
            : const Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.play_arrow),
                  SizedBox(width: 8),
                  Text(
                    'توليد التقرير',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
      ),
    );
  }

  Future<void> _generateReport() async {
    setState(() {
      _isGenerating = true;
      _errorMessage = null;
    });

    try {
      final repository = ref.read(reportsRepositoryProvider);
      final customTitle = _titleController.text.trim().isNotEmpty
          ? _titleController.text.trim()
          : null;

      final report = await repository.generateReport(
        template: widget.template,
        filter: _filter,
        tenantId: await ref.read(secureStorageProvider).getTenantId() ?? 'default',
        customTitle: customTitle,
      );

      if (mounted) {
        // Navigate to viewer
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => ReportViewerScreen(report: report),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
        });
      }
    } finally {
      if (mounted) {
        setState(() => _isGenerating = false);
      }
    }
  }

  IconData _getTemplateIcon(ReportType type) {
    switch (type) {
      case ReportType.fieldPerformance:
        return Icons.landscape;
      case ReportType.ndviTrend:
        return Icons.show_chart;
      case ReportType.irrigationSummary:
        return Icons.water_drop;
      case ReportType.taskCompletion:
        return Icons.task_alt;
      case ReportType.weatherAnalysis:
        return Icons.cloud;
      case ReportType.costProfit:
        return Icons.account_balance;
      case ReportType.yieldPrediction:
        return Icons.trending_up;
    }
  }
}
