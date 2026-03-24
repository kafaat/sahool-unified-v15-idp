import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/rotation_models.dart';
import '../providers/rotation_provider.dart';
import '../widgets/rotation_timeline_widget.dart';
import '../widgets/soil_health_chart.dart';
import 'rotation_calendar_screen.dart';
import 'crop_compatibility_screen.dart';

class RotationPlanScreen extends ConsumerStatefulWidget {
  final String fieldId;

  const RotationPlanScreen({
    super.key,
    required this.fieldId,
  });

  @override
  ConsumerState<RotationPlanScreen> createState() => _RotationPlanScreenState();
}

class _RotationPlanScreenState extends ConsumerState<RotationPlanScreen> {
  int _selectedYearIndex = 0;

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final planAsync = ref.watch(rotationPlanProvider(widget.fieldId));
    final soilHealthTrendAsync =
        ref.watch(soilHealthTrendProvider(widget.fieldId));

    return Scaffold(
      appBar: AppBar(
        title: Text(isArabic ? 'خطة الدورة الزراعية' : 'Crop Rotation Plan'),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_month),
            tooltip: isArabic ? 'عرض التقويم' : 'Calendar View',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) =>
                      RotationCalendarScreen(fieldId: widget.fieldId),
                ),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.grid_on),
            tooltip: isArabic ? 'مصفوفة التوافق' : 'Compatibility Matrix',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (context) => const CropCompatibilityScreen(),
                ),
              );
            },
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'generate') {
                _showGeneratePlanDialog();
              } else if (value == 'refresh') {
                ref.invalidate(rotationPlanProvider(widget.fieldId));
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'generate',
                child: Row(
                  children: [
                    const Icon(Icons.auto_awesome),
                    const SizedBox(width: 8),
                    Text(isArabic ? 'إنشاء خطة جديدة' : 'Generate New Plan'),
                  ],
                ),
              ),
              PopupMenuItem(
                value: 'refresh',
                child: Row(
                  children: [
                    const Icon(Icons.refresh),
                    const SizedBox(width: 8),
                    Text(isArabic ? 'تحديث' : 'Refresh'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: planAsync.when(
        data: (plan) => _buildPlanContent(plan, soilHealthTrendAsync),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.error_outline, size: 64, color: Colors.red),
              const SizedBox(height: 16),
              Text(isArabic ? 'خطأ في تحميل الخطة: $error' : 'Error loading plan: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ref.invalidate(rotationPlanProvider(widget.fieldId));
                },
                child: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlanContent(
    RotationPlan plan,
    AsyncValue<List<SoilHealth>> soilHealthTrendAsync,
  ) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Field header
          _buildFieldHeader(plan),

          // Timeline widget
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: RotationTimelineWidget(
              rotationYears: plan.rotationYears,
              selectedIndex: _selectedYearIndex,
              onYearSelected: (index) {
                setState(() {
                  _selectedYearIndex = index;
                });
              },
            ),
          ),

          // Year details
          if (_selectedYearIndex < plan.rotationYears.length)
            _buildYearDetails(plan.rotationYears[_selectedYearIndex]),

          // Soil health chart
          soilHealthTrendAsync.when(
            data: (trend) => Padding(
              padding: const EdgeInsets.all(16),
              child: SoilHealthChart(soilHealthData: trend),
            ),
            loading: () => const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(),
              ),
            ),
            error: (_, __) => const SizedBox.shrink(),
          ),

          // Rotation summary
          _buildRotationSummary(plan),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildFieldHeader(RotationPlan plan) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.green.shade50,
      child: Row(
        children: [
          const Icon(Icons.agriculture, size: 48, color: Colors.green),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  plan.fieldName,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _isArabic(context)
                      ? 'خطة دورة زراعية لمدة ${plan.totalYears} سنوات'
                      : '${plan.totalYears}-Year Rotation Plan',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _isArabic(context)
                      ? 'آخر تحديث: ${_formatDate(plan.updatedAt)}'
                      : 'Updated: ${_formatDate(plan.updatedAt)}',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildYearDetails(RotationYear year) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Year header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 6,
                  ),
                  decoration: BoxDecoration(
                    color: year.isCurrent
                        ? Colors.green
                        : year.isCompleted
                            ? Colors.grey
                            : Colors.blue,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    year.year.toString(),
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                if (year.isCurrent)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: Colors.orange,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      _isArabic(context) ? 'الحالي' : 'CURRENT',
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                const Spacer(),
                Text(
                  year.season,
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey.shade700,
                  ),
                ),
              ],
            ),

            const Divider(height: 24),

            // Crop information
            if (year.crop != null) ...[
              Row(
                children: [
                  Container(
                    width: 60,
                    height: 60,
                    decoration: BoxDecoration(
                      color: Colors.green.shade100,
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: const Icon(
                      Icons.grass,
                      size: 36,
                      color: Colors.green,
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          _isArabic(context)
                              ? (year.crop!.nameAr ?? year.crop!.nameEn)
                              : year.crop!.nameEn,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          _isArabic(context)
                              ? year.crop!.nameEn
                              : (year.crop!.nameAr ?? ''),
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.grey.shade600,
                          ),
                        ),
                        Text(
                          CropFamilyInfo.familyData[year.crop!.family]!.nameAr,
                          style: TextStyle(
                            fontSize: 14,
                            color: Colors.grey.shade500,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Dates
              if (year.plantingDate != null || year.harvestDate != null) ...[
                Row(
                  children: [
                    if (year.plantingDate != null) ...[
                      const Icon(Icons.calendar_today, size: 16),
                      const SizedBox(width: 4),
                      Text(_isArabic(context)
                          ? 'الزراعة: ${_formatDate(year.plantingDate!)}'
                          : 'Planting: ${_formatDate(year.plantingDate!)}'),
                    ],
                    const Spacer(),
                    if (year.harvestDate != null) ...[
                      const Icon(Icons.calendar_today, size: 16),
                      const SizedBox(width: 4),
                      Text(_isArabic(context)
                          ? 'الحصاد: ${_formatDate(year.harvestDate!)}'
                          : 'Harvest: ${_formatDate(year.harvestDate!)}'),
                    ],
                  ],
                ),
                const SizedBox(height: 8),
              ],

              // Yield
              if (year.yieldAmount != null) ...[
                Row(
                  children: [
                    const Icon(Icons.agriculture, size: 16, color: Colors.green),
                    const SizedBox(width: 4),
                    Text(_isArabic(context)
                        ? 'الإنتاج: ${year.yieldAmount!.toStringAsFixed(1)} طن/هكتار'
                        : 'Yield: ${year.yieldAmount!.toStringAsFixed(1)} tons/ha'),
                  ],
                ),
                const SizedBox(height: 8),
              ],

              // Growing days
              Row(
                children: [
                  const Icon(Icons.timelapse, size: 16),
                  const SizedBox(width: 4),
                  Text(_isArabic(context)
                      ? 'فترة النمو: ${year.crop!.growingDays} يوم'
                      : 'Growing period: ${year.crop!.growingDays} days'),
                ],
              ),
            ] else
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    _isArabic(context)
                        ? 'لا يوجد محصول مخطط لهذا العام'
                        : 'No crop planned for this year',
                    style: TextStyle(
                      fontSize: 16,
                      fontStyle: FontStyle.italic,
                    ),
                  ),
                ),
              ),

            // Soil health indicators
            if (year.soilHealthBefore != null) ...[
              const Divider(height: 24),
              Text(
                _isArabic(context)
                    ? 'تحليل صحة التربة (قبل الزراعة)'
                    : 'Soil Health (before planting)',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              _buildSoilHealthIndicators(year.soilHealthBefore!),
            ],

            if (year.soilHealthAfter != null) ...[
              const SizedBox(height: 16),
              Text(
                _isArabic(context)
                    ? 'تحليل صحة التربة (بعد الحصاد)'
                    : 'Soil Health (after harvest)',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              _buildSoilHealthIndicators(year.soilHealthAfter!),
            ],

            // Notes
            if (year.notes != null) ...[
              const Divider(height: 24),
              Text(
                _isArabic(context)
                    ? 'ملاحظات: ${year.notes}'
                    : 'Notes: ${year.notes}',
                style: TextStyle(
                  fontSize: 14,
                  color: Colors.grey.shade700,
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSoilHealthIndicators(SoilHealth health) {
    final isAr = _isArabic(context);
    return Column(
      children: [
        _buildHealthBar(isAr ? 'النيتروجين (N)' : 'Nitrogen (N)', health.nitrogen, Colors.blue),
        const SizedBox(height: 8),
        _buildHealthBar(isAr ? 'الفوسفور (P)' : 'Phosphorus (P)', health.phosphorus, Colors.orange),
        const SizedBox(height: 8),
        _buildHealthBar(isAr ? 'البوتاسيوم (K)' : 'Potassium (K)', health.potassium, Colors.purple),
        const SizedBox(height: 8),
        _buildHealthBar(isAr ? 'المادة العضوية' : 'Organic Matter', health.organicMatter, Colors.brown),
        const SizedBox(height: 8),
        _buildHealthBar(
            isAr ? 'الاحتفاظ بالماء' : 'Water Retention', health.waterRetention, Colors.lightBlue),
        const SizedBox(height: 8),
        Row(
          children: [
            Text(
              'pH: ${health.ph.toStringAsFixed(1)}',
              style: const TextStyle(fontSize: 14),
            ),
            const Spacer(),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: _getHealthLevelColor(health.overallScore),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                health.healthLevel,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHealthBar(String label, double value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            Expanded(
              child: Text(
                label,
                style: const TextStyle(fontSize: 14),
              ),
            ),
            Text(
              '${value.toStringAsFixed(0)}%',
              style: const TextStyle(
                fontSize: 14,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
        const SizedBox(height: 4),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value / 100,
            backgroundColor: Colors.grey.shade200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  Widget _buildRotationSummary(RotationPlan plan) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _isArabic(context) ? 'ملخص الدورة الزراعية' : 'Rotation Summary',
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryCard(
                    _isArabic(context) ? 'إجمالي السنوات' : 'Total Years',
                    plan.totalYears.toString(),
                    Icons.calendar_today,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildSummaryCard(
                    _isArabic(context) ? 'العائلات المستخدمة' : 'Families Used',
                    plan.familiesUsed.length.toString(),
                    Icons.category,
                    Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryCard(
                    _isArabic(context) ? 'المكتملة' : 'Completed',
                    plan.pastRotations.length.toString(),
                    Icons.check_circle,
                    Colors.grey,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildSummaryCard(
                    _isArabic(context) ? 'القادمة' : 'Upcoming',
                    plan.futureRotations.length.toString(),
                    Icons.upcoming,
                    Colors.orange,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSummaryCard(
      String label, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 32),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey.shade700,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Color _getHealthLevelColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.lightGreen;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  bool _isArabic(BuildContext context) {
    return Localizations.localeOf(context).languageCode == 'ar';
  }

  void _showGeneratePlanDialog() {
    int years = 5;
    bool prioritizeSoilHealth = true;
    bool includeNitrogenFixers = true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: Text(_isArabic(context) ? 'إنشاء خطة دورة زراعية' : 'Generate Rotation Plan'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_isArabic(context) ? 'عدد السنوات:' : 'Number of years:'),
              Slider(
                value: years.toDouble(),
                min: 3,
                max: 10,
                divisions: 7,
                label: years.toString(),
                onChanged: (value) {
                  setState(() {
                    years = value.toInt();
                  });
                },
              ),
              CheckboxListTile(
                title: Text(_isArabic(context) ? 'إعطاء الأولوية لصحة التربة' : 'Prioritize soil health'),
                value: prioritizeSoilHealth,
                onChanged: (value) {
                  setState(() {
                    prioritizeSoilHealth = value ?? true;
                  });
                },
              ),
              CheckboxListTile(
                title: Text(_isArabic(context) ? 'تضمين مثبتات النيتروجين' : 'Include nitrogen fixers'),
                value: includeNitrogenFixers,
                onChanged: (value) {
                  setState(() {
                    includeNitrogenFixers = value ?? true;
                  });
                },
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(_isArabic(context) ? 'إلغاء' : 'Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                ref.read(rotationPlanNotifierProvider.notifier).generatePlan(
                  widget.fieldId,
                  years,
                  {
                    'prioritizeSoilHealth': prioritizeSoilHealth,
                    'includeNitrogenFixers': includeNitrogenFixers,
                    'avoidSameFamily': true,
                    'rotationCycleYears': years,
                  },
                );
              },
              child: Text(_isArabic(context) ? 'إنشاء' : 'Generate'),
            ),
          ],
        ),
      ),
    );
  }
}
