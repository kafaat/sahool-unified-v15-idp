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
    Key? key,
    required this.fieldId,
  }) : super(key: key);

  @override
  ConsumerState<RotationPlanScreen> createState() => _RotationPlanScreenState();
}

class _RotationPlanScreenState extends ConsumerState<RotationPlanScreen> {
  int _selectedYearIndex = 0;

  @override
  Widget build(BuildContext context) {
    final planAsync = ref.watch(rotationPlanProvider(widget.fieldId));
    final soilHealthTrendAsync =
        ref.watch(soilHealthTrendProvider(widget.fieldId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Crop Rotation Plan'),
        actions: [
          IconButton(
            icon: const Icon(Icons.calendar_month),
            tooltip: 'Calendar View',
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
            tooltip: 'Compatibility Matrix',
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
              const PopupMenuItem(
                value: 'generate',
                child: Row(
                  children: [
                    Icon(Icons.auto_awesome),
                    SizedBox(width: 8),
                    Text('Generate New Plan'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'refresh',
                child: Row(
                  children: [
                    Icon(Icons.refresh),
                    SizedBox(width: 8),
                    Text('Refresh'),
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
              Text('Error loading plan: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  ref.invalidate(rotationPlanProvider(widget.fieldId));
                },
                child: const Text('Retry'),
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
                  '${plan.totalYears}-Year Rotation Plan',
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey.shade700,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Updated: ${_formatDate(plan.updatedAt)}',
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
                    child: const Text(
                      'CURRENT',
                      style: TextStyle(
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
                          year.crop!.nameEn,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          year.crop!.nameAr,
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
                      Text('Planting: ${_formatDate(year.plantingDate!)}'),
                    ],
                    const Spacer(),
                    if (year.harvestDate != null) ...[
                      const Icon(Icons.calendar_today, size: 16),
                      const SizedBox(width: 4),
                      Text('Harvest: ${_formatDate(year.harvestDate!)}'),
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
                    Text('Yield: ${year.yieldAmount!.toStringAsFixed(1)} tons/ha'),
                  ],
                ),
                const SizedBox(height: 8),
              ],

              // Growing days
              Row(
                children: [
                  const Icon(Icons.timelapse, size: 16),
                  const SizedBox(width: 4),
                  Text('Growing period: ${year.crop!.growingDays} days'),
                ],
              ),
            ] else
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(16),
                  child: Text(
                    'No crop planned for this year',
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
              const Text(
                'Soil Health (before planting)',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              _buildSoilHealthIndicators(year.soilHealthBefore!),
            ],

            if (year.soilHealthAfter != null) ...[
              const SizedBox(height: 16),
              const Text(
                'Soil Health (after harvest)',
                style: TextStyle(
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
                'Notes: ${year.notes}',
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
    return Column(
      children: [
        _buildHealthBar('Nitrogen (N)', health.nitrogen, Colors.blue),
        const SizedBox(height: 8),
        _buildHealthBar('Phosphorus (P)', health.phosphorus, Colors.orange),
        const SizedBox(height: 8),
        _buildHealthBar('Potassium (K)', health.potassium, Colors.purple),
        const SizedBox(height: 8),
        _buildHealthBar('Organic Matter', health.organicMatter, Colors.brown),
        const SizedBox(height: 8),
        _buildHealthBar(
            'Water Retention', health.waterRetention, Colors.lightBlue),
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
            const Text(
              'Rotation Summary',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildSummaryCard(
                    'Total Years',
                    plan.totalYears.toString(),
                    Icons.calendar_today,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildSummaryCard(
                    'Families Used',
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
                    'Completed',
                    plan.pastRotations.length.toString(),
                    Icons.check_circle,
                    Colors.grey,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildSummaryCard(
                    'Upcoming',
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
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
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

  void _showGeneratePlanDialog() {
    int years = 5;
    bool prioritizeSoilHealth = true;
    bool includeNitrogenFixers = true;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Generate Rotation Plan'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Text('Number of years:'),
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
                title: const Text('Prioritize soil health'),
                value: prioritizeSoilHealth,
                onChanged: (value) {
                  setState(() {
                    prioritizeSoilHealth = value ?? true;
                  });
                },
              ),
              CheckboxListTile(
                title: const Text('Include nitrogen fixers'),
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
              child: const Text('Cancel'),
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
              child: const Text('Generate'),
            ),
          ],
        ),
      ),
    );
  }
}
