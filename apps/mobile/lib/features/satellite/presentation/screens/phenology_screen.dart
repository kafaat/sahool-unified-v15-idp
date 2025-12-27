/// Phenology Screen - شاشة مراحل النمو
/// Crop growth stage tracking and timeline
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../providers/satellite_provider.dart';
import '../../widgets/phenology_timeline.dart';

class PhenologyScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String fieldName;

  const PhenologyScreen({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  ConsumerState<PhenologyScreen> createState() => _PhenologyScreenState();
}

class _PhenologyScreenState extends ConsumerState<PhenologyScreen> {
  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      ref.read(phenologyProvider.notifier).loadPhenology(widget.fieldId);
    });
  }

  Future<void> _refreshPhenology() async {
    await ref.read(phenologyProvider.notifier).refreshPhenology(widget.fieldId);
  }

  @override
  Widget build(BuildContext context) {
    final phenologyState = ref.watch(phenologyProvider);
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      backgroundColor: Colors.grey[100],
      appBar: AppBar(
        title: Text(
          isArabic ? 'مراحل النمو' : 'Growth Stages',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: const Color(0xFF367C2B),
        foregroundColor: Colors.white,
        elevation: 0,
      ),
      body: phenologyState.when(
        data: (phenology) => RefreshIndicator(
          onRefresh: _refreshPhenology,
          color: const Color(0xFF367C2B),
          child: _buildPhenologyContent(phenology, isArabic),
        ),
        loading: () => const Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Color(0xFF367C2B)),
          ),
        ),
        error: (error, stack) => _buildErrorState(error.toString(), isArabic),
      ),
    );
  }

  Widget _buildErrorState(String error, bool isArabic) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(error, textAlign: TextAlign.center),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: _refreshPhenology,
              icon: const Icon(Icons.refresh),
              label: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                foregroundColor: Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPhenologyContent(dynamic phenology, bool isArabic) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        // Current stage card
        _buildCurrentStageCard(phenology, isArabic),
        const SizedBox(height: 16),

        // Progress timeline
        PhenologyTimeline(
          stages: phenology.stages,
          currentStage: phenology.currentStage,
        ),
        const SizedBox(height: 16),

        // Harvest countdown
        if (phenology.daysToHarvest != null)
          _buildHarvestCountdown(phenology.daysToHarvest!, isArabic),
        const SizedBox(height: 16),

        // Current stage tasks
        if (phenology.currentTasks.isNotEmpty)
          _buildTasksCard(phenology.currentTasks, phenology.currentTasksAr, isArabic),
        const SizedBox(height: 16),

        // Crop info
        _buildCropInfo(phenology, isArabic),
      ],
    );
  }

  Widget _buildCurrentStageCard(dynamic phenology, bool isArabic) {
    final progress = phenology.completionPercentage;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            Color(int.parse(phenology.currentStage.colorHex.replaceFirst('#', '0xFF'))),
            Color(int.parse(phenology.currentStage.colorHex.replaceFirst('#', '0xFF'))).withOpacity(0.7),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'المرحلة الحالية' : 'Current Stage',
            style: const TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            phenology.currentStage.getLabel(isArabic),
            style: const TextStyle(
              color: Colors.white,
              fontSize: 28,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isArabic ? 'أيام في المرحلة' : 'Days in Stage',
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 12,
                      ),
                    ),
                    Text(
                      phenology.daysInCurrentStage.toString(),
                      style: const TextStyle(
                        color: Colors.white,
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              if (phenology.daysToNextStage != null)
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isArabic ? 'باقي للمرحلة التالية' : 'Days to Next',
                        style: const TextStyle(
                          color: Colors.white70,
                          fontSize: 12,
                        ),
                      ),
                      Text(
                        phenology.daysToNextStage.toString(),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),
          LinearProgressIndicator(
            value: progress / 100,
            backgroundColor: Colors.white.withOpacity(0.3),
            valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
            minHeight: 8,
          ),
          const SizedBox(height: 8),
          Text(
            '${progress.toStringAsFixed(0)}% ${isArabic ? 'مكتمل' : 'Complete'}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHarvestCountdown(int days, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.orange[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.orange[200]!),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.orange,
              borderRadius: BorderRadius.circular(8),
            ),
            child: const Icon(Icons.agriculture, color: Colors.white, size: 32),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isArabic ? 'العد التنازلي للحصاد' : 'Harvest Countdown',
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.orange[900],
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  '$days ${isArabic ? 'يوم متبقي' : 'days remaining'}',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange[900],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTasksCard(List<String> tasks, List<String> tasksAr, bool isArabic) {
    final displayTasks = isArabic ? tasksAr : tasks;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.task_alt, color: Color(0xFF367C2B)),
              const SizedBox(width: 8),
              Text(
                isArabic ? 'مهام المرحلة الحالية' : 'Current Stage Tasks',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...displayTasks.map((task) => Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      margin: const EdgeInsets.only(top: 4),
                      width: 8,
                      height: 8,
                      decoration: const BoxDecoration(
                        color: Color(0xFF367C2B),
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        task,
                        style: const TextStyle(fontSize: 14),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }

  Widget _buildCropInfo(dynamic phenology, bool isArabic) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'معلومات المحصول' : 'Crop Information',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 16),
          _buildInfoRow(
            isArabic ? 'نوع المحصول' : 'Crop Type',
            isArabic ? phenology.cropTypeAr : phenology.cropType,
            Icons.grass,
          ),
          const Divider(height: 24),
          _buildInfoRow(
            isArabic ? 'تاريخ الزراعة' : 'Planting Date',
            _formatDate(phenology.plantingDate, isArabic),
            Icons.calendar_today,
          ),
          if (phenology.expectedHarvestDate != null) ...[
            const Divider(height: 24),
            _buildInfoRow(
              isArabic ? 'الحصاد المتوقع' : 'Expected Harvest',
              _formatDate(phenology.expectedHarvestDate!, isArabic),
              Icons.event_available,
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: const Color(0xFF367C2B)),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
              const SizedBox(height: 4),
              Text(
                value,
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  String _formatDate(DateTime date, bool isArabic) {
    final months = isArabic
        ? ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر']
        : ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    return '${date.day} ${months[date.month - 1]} ${date.year}';
  }
}
