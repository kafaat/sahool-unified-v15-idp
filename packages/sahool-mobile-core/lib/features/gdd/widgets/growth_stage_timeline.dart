/// Growth Stage Timeline Widget - ويدجت المخطط الزمني لمراحل النمو
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../models/gdd_models.dart';
import '../providers/gdd_provider.dart';

/// ويدجت المخطط الزمني لمراحل النمو
class GrowthStageTimeline extends ConsumerWidget {
  final String fieldId;
  final double currentGDD;

  const GrowthStageTimeline({
    super.key,
    required this.fieldId,
    required this.currentGDD,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final stagesAsync = ref.watch(growthStagesProvider(fieldId));

    return stagesAsync.when(
      data: (stages) {
        if (stages.isEmpty) {
          return _buildEmptyState(context);
        }
        return _buildTimeline(context, stages);
      },
      loading: () => const Center(
        child: Padding(
          padding: EdgeInsets.all(16),
          child: CircularProgressIndicator(),
        ),
      ),
      error: (error, stack) => _buildErrorState(context, error),
    );
  }

  Widget _buildTimeline(BuildContext context, List<GrowthStage> stages) {
    return Column(
      children: stages.asMap().entries.map((entry) {
        final index = entry.key;
        final stage = entry.value;
        final isCompleted = currentGDD >= stage.gddEnd;
        final isCurrent = currentGDD >= stage.gddStart && currentGDD < stage.gddEnd;
        final isLast = index == stages.length - 1;

        return _buildStageItem(
          context,
          stage,
          isCompleted: isCompleted,
          isCurrent: isCurrent,
          isLast: isLast,
        );
      }).toList(),
    );
  }

  Widget _buildStageItem(
    BuildContext context,
    GrowthStage stage, {
    required bool isCompleted,
    required bool isCurrent,
    required bool isLast,
  }) {
    final stageProgress = isCurrent
        ? ((currentGDD - stage.gddStart) / (stage.gddEnd - stage.gddStart))
            .clamp(0.0, 1.0)
        : 0.0;

    return IntrinsicHeight(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // المؤشر العمودي
          Column(
            children: [
              // الدائرة
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: isCompleted
                      ? Colors.green
                      : isCurrent
                          ? Colors.blue
                          : Colors.grey.shade300,
                  border: Border.all(
                    color: isCompleted
                        ? Colors.green.shade700
                        : isCurrent
                            ? Colors.blue.shade700
                            : Colors.grey.shade400,
                    width: 2,
                  ),
                ),
                child: Center(
                  child: isCompleted
                      ? const Icon(
                          Icons.check,
                          color: Colors.white,
                          size: 20,
                        )
                      : isCurrent
                          ? Container(
                              width: 12,
                              height: 12,
                              decoration: const BoxDecoration(
                                color: Colors.white,
                                shape: BoxShape.circle,
                              ),
                            )
                          : Text(
                              '${stage.stageNumber}',
                              style: const TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                ),
              ),
              // الخط العمودي
              if (!isLast)
                Expanded(
                  child: Container(
                    width: 2,
                    color: isCompleted
                        ? Colors.green.shade300
                        : Colors.grey.shade300,
                  ),
                ),
            ],
          ),
          const SizedBox(width: 16),

          // المحتوى
          Expanded(
            child: Padding(
              padding: const EdgeInsets.only(bottom: 24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // اسم المرحلة
                  Text(
                    stage.getName('ar'),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                          color: isCompleted
                              ? Colors.green.shade700
                              : isCurrent
                                  ? Colors.blue.shade700
                                  : Colors.grey.shade700,
                        ),
                  ),
                  const SizedBox(height: 4),

                  // الوصف
                  if (stage.getDescription('ar') != null)
                    Text(
                      stage.getDescription('ar')!,
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.grey.shade600,
                          ),
                    ),
                  const SizedBox(height: 8),

                  // معلومات GDD
                  Row(
                    children: [
                      Icon(
                        Icons.thermostat,
                        size: 16,
                        color: Colors.grey.shade600,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '${stage.gddRequired.toStringAsFixed(0)} GDD',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              fontWeight: FontWeight.bold,
                              color: Colors.grey.shade700,
                            ),
                      ),
                      const SizedBox(width: 12),
                      Text(
                        '(${stage.gddStart.toStringAsFixed(0)} - ${stage.gddEnd.toStringAsFixed(0)})',
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                              color: Colors.grey.shade500,
                            ),
                      ),
                    ],
                  ),

                  // شريط التقدم للمرحلة الحالية
                  if (isCurrent) ...[
                    const SizedBox(height: 8),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.stretch,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              'التقدم',
                              style: Theme.of(context).textTheme.bodySmall,
                            ),
                            Text(
                              '${(stageProgress * 100).toStringAsFixed(0)}%',
                              style: Theme.of(context)
                                  .textTheme
                                  .bodySmall
                                  ?.copyWith(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.blue.shade700,
                                  ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(4),
                          child: LinearProgressIndicator(
                            value: stageProgress,
                            minHeight: 8,
                            backgroundColor: Colors.grey.shade200,
                            valueColor: AlwaysStoppedAnimation<Color>(
                              Colors.blue.shade400,
                            ),
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'باقي ${(stage.gddEnd - currentGDD).toStringAsFixed(0)} GDD',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Colors.grey.shade600,
                                  ),
                        ),
                      ],
                    ),
                  ],

                  // حالة الإكمال
                  if (isCompleted) ...[
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(
                          Icons.check_circle,
                          size: 16,
                          color: Colors.green.shade600,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          'مكتملة',
                          style:
                              Theme.of(context).textTheme.bodySmall?.copyWith(
                                    color: Colors.green.shade600,
                                    fontWeight: FontWeight.bold,
                                  ),
                        ),
                      ],
                    ),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            Icon(
              Icons.timeline,
              size: 48,
              color: Colors.grey.shade300,
            ),
            const SizedBox(height: 8),
            Text(
              'لا توجد مراحل نمو محددة',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey.shade600,
                  ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildErrorState(BuildContext context, Object error) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Icon(
            Icons.error_outline,
            size: 48,
            color: Colors.red.shade300,
          ),
          const SizedBox(height: 8),
          Text(
            'فشل في تحميل مراحل النمو',
            style: Theme.of(context).textTheme.bodyMedium,
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
