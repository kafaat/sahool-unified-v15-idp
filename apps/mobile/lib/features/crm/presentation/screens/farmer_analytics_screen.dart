/// Farmer Analytics Screen
/// شاشة تحليلات المزارع
///
/// Displays analytics and insights for a specific farmer
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../domain/models/activity_log.dart';
import '../../domain/models/interaction.dart';
import '../../state/crm_providers.dart';

/// Farmer Analytics Screen
/// شاشة عرض تحليلات المزارع
class FarmerAnalyticsScreen extends ConsumerWidget {
  final String farmerId;
  final String farmerName;

  const FarmerAnalyticsScreen({
    super.key,
    required this.farmerId,
    required this.farmerName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final analyticsAsync = ref.watch(farmerAnalyticsProvider(farmerId));

    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('التحليلات'),
            Text(
              farmerName,
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.normal,
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.invalidate(farmerAnalyticsProvider(farmerId)),
          ),
        ],
      ),
      body: analyticsAsync.when(
        data: (analytics) => _buildAnalyticsContent(context, analytics),
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildError(context, ref, error),
      ),
    );
  }

  Widget _buildAnalyticsContent(BuildContext context, FarmerAnalytics analytics) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Engagement Score Card
          _buildEngagementScoreCard(context, analytics),

          const SizedBox(height: 16),

          // Key Metrics Grid
          _buildKeyMetricsGrid(context, analytics),

          const SizedBox(height: 24),

          // Interaction Distribution
          _buildSectionTitle('توزيع التفاعلات'),
          const SizedBox(height: 12),
          _buildInteractionDistributionCard(context, analytics),

          const SizedBox(height: 24),

          // Outcome Analysis
          _buildSectionTitle('تحليل النتائج'),
          const SizedBox(height: 12),
          _buildOutcomeAnalysisCard(context, analytics),

          const SizedBox(height: 24),

          // Activity Timeline
          _buildSectionTitle('النشاط عبر الزمن'),
          const SizedBox(height: 12),
          _buildActivityTimelineCard(context, analytics),

          const SizedBox(height: 24),

          // Response Patterns
          _buildSectionTitle('أنماط الاستجابة'),
          const SizedBox(height: 12),
          _buildResponsePatternsCard(context, analytics),

          const SizedBox(height: 24),

          // Recommendations
          _buildSectionTitle('التوصيات'),
          const SizedBox(height: 12),
          _buildRecommendationsCard(context, analytics),

          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildEngagementScoreCard(BuildContext context, FarmerAnalytics analytics) {
    final score = analytics.engagementScore;
    final color = _getScoreColor(score);
    final label = _getScoreLabel(score);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Row(
          children: [
            // Score Circle
            SizedBox(
              width: 100,
              height: 100,
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 100,
                    height: 100,
                    child: CircularProgressIndicator(
                      value: score / 100,
                      strokeWidth: 10,
                      backgroundColor: Colors.grey[200],
                      valueColor: AlwaysStoppedAnimation<Color>(color),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        '${score.toInt()}',
                        style: TextStyle(
                          fontSize: 28,
                          fontWeight: FontWeight.bold,
                          color: color,
                        ),
                      ),
                      Text(
                        label,
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(width: 20),

            // Score Details
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'معدل التفاعل',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    _getEngagementDescription(score),
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 12),
                  _buildScoreLegend(),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreLegend() {
    return Row(
      children: [
        _buildLegendItem('ضعيف', Colors.red, '0-30'),
        const SizedBox(width: 8),
        _buildLegendItem('متوسط', Colors.orange, '31-60'),
        const SizedBox(width: 8),
        _buildLegendItem('جيد', Colors.green, '61-100'),
      ],
    );
  }

  Widget _buildLegendItem(String label, Color color, String range) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 8,
          height: 8,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 10,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildKeyMetricsGrid(BuildContext context, FarmerAnalytics analytics) {
    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      mainAxisSpacing: 12,
      crossAxisSpacing: 12,
      childAspectRatio: 1.5,
      children: [
        _buildMetricCard(
          icon: Icons.touch_app,
          label: 'إجمالي التفاعلات',
          value: '${analytics.totalInteractions}',
          color: Colors.blue,
        ),
        _buildMetricCard(
          icon: Icons.calendar_today,
          label: 'آخر تفاعل',
          value: analytics.daysSinceLastInteraction != null
              ? 'منذ ${analytics.daysSinceLastInteraction} يوم'
              : 'لا يوجد',
          color: Colors.purple,
        ),
        _buildMetricCard(
          icon: Icons.timer,
          label: 'متوسط المدة',
          value: analytics.averageInteractionDuration != null
              ? '${analytics.averageInteractionDuration!.toInt()} دقيقة'
              : '-',
          color: Colors.teal,
        ),
        _buildMetricCard(
          icon: Icons.check_circle,
          label: 'معدل النجاح',
          value: '${(analytics.successRate * 100).toInt()}%',
          color: Colors.green,
        ),
      ],
    );
  }

  Widget _buildMetricCard({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Row(
              children: [
                Icon(icon, size: 18, color: color),
                const SizedBox(width: 6),
                Text(
                  label,
                  style: TextStyle(
                    fontSize: 11,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
            const Spacer(),
            Text(
              value,
              style: const TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInteractionDistributionCard(
      BuildContext context, FarmerAnalytics analytics) {
    final distribution = analytics.interactionsByType;

    if (distribution.isEmpty) {
      return _buildEmptyCard('لا توجد تفاعلات لعرض التوزيع');
    }

    final total = distribution.values.fold(0, (a, b) => a + b);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Bar Chart
            ...distribution.entries.map((entry) {
              final type = InteractionType.values.firstWhere(
                (t) => t.name == entry.key,
                orElse: () => InteractionType.note,
              );
              final percentage = entry.value / total;
              final typeInfo = _getInteractionTypeInfo(type);

              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Row(
                  children: [
                    SizedBox(
                      width: 80,
                      child: Row(
                        children: [
                          Icon(typeInfo.icon, size: 16, color: typeInfo.color),
                          const SizedBox(width: 4),
                          Flexible(
                            child: Text(
                              typeInfo.label,
                              style: const TextStyle(fontSize: 11),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Stack(
                        children: [
                          Container(
                            height: 20,
                            decoration: BoxDecoration(
                              color: Colors.grey[200],
                              borderRadius: BorderRadius.circular(4),
                            ),
                          ),
                          FractionallySizedBox(
                            widthFactor: percentage,
                            child: Container(
                              height: 20,
                              decoration: BoxDecoration(
                                color: typeInfo.color,
                                borderRadius: BorderRadius.circular(4),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    SizedBox(
                      width: 40,
                      child: Text(
                        '${entry.value}',
                        style: const TextStyle(fontWeight: FontWeight.w600),
                        textAlign: TextAlign.end,
                      ),
                    ),
                  ],
                ),
              );
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildOutcomeAnalysisCard(
      BuildContext context, FarmerAnalytics analytics) {
    final outcomes = analytics.interactionsByOutcome;

    if (outcomes.isEmpty) {
      return _buildEmptyCard('لا توجد بيانات كافية للتحليل');
    }

    final total = outcomes.values.fold(0, (a, b) => a + b);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Pie chart representation as horizontal bars
            ...outcomes.entries.map((entry) {
              final outcome = InteractionOutcome.values.firstWhere(
                (o) => o.name == entry.key,
                orElse: () => InteractionOutcome.pending,
              );
              final percentage = entry.value / total;
              final outcomeInfo = _getOutcomeInfo(outcome);

              return Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Container(
                      width: 12,
                      height: 12,
                      decoration: BoxDecoration(
                        color: outcomeInfo.color,
                        shape: BoxShape.circle,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        outcomeInfo.label,
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                    Text(
                      '${(percentage * 100).toInt()}%',
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 13,
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      '(${entry.value})',
                      style: TextStyle(
                        color: Colors.grey[500],
                        fontSize: 12,
                      ),
                    ),
                  ],
                ),
              );
            }),

            const Divider(height: 24),

            // Summary stats
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildOutcomeStat(
                  'الإيجابية',
                  _calculatePositiveOutcomes(outcomes, total),
                  Colors.green,
                ),
                _buildOutcomeStat(
                  'المحايدة',
                  _calculateNeutralOutcomes(outcomes, total),
                  Colors.grey,
                ),
                _buildOutcomeStat(
                  'السلبية',
                  _calculateNegativeOutcomes(outcomes, total),
                  Colors.red,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOutcomeStat(String label, double percentage, Color color) {
    return Column(
      children: [
        Text(
          '${(percentage * 100).toInt()}%',
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Widget _buildActivityTimelineCard(
      BuildContext context, FarmerAnalytics analytics) {
    final monthlyActivity = analytics.monthlyActivity;

    if (monthlyActivity.isEmpty) {
      return _buildEmptyCard('لا توجد بيانات نشاط');
    }

    final maxValue = monthlyActivity.values.fold<num>(0, (a, b) => (b as num) > a ? b : a);

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Simple bar chart for last 6 months
            SizedBox(
              height: 150,
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.end,
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: monthlyActivity.entries.take(6).map((entry) {
                  final heightFactor = maxValue > 0 ? (entry.value as num) / maxValue : 0.0;
                  return Column(
                    mainAxisAlignment: MainAxisAlignment.end,
                    children: [
                      Text(
                        '${entry.value}',
                        style: const TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Container(
                        width: 30,
                        height: (100 * heightFactor).toDouble(),
                        decoration: BoxDecoration(
                          color: const Color(0xFF367C2B),
                          borderRadius: BorderRadius.circular(4),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _formatMonthKey(entry.key),
                        style: TextStyle(
                          fontSize: 10,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  );
                }).toList(),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResponsePatternsCard(
      BuildContext context, FarmerAnalytics analytics) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            _buildPatternRow(
              'أفضل وقت للتواصل',
              analytics.preferredContactTime ?? 'غير محدد',
              Icons.schedule,
            ),
            const Divider(height: 24),
            _buildPatternRow(
              'القناة المفضلة',
              analytics.preferredChannel ?? 'غير محدد',
              Icons.chat,
            ),
            const Divider(height: 24),
            _buildPatternRow(
              'معدل الاستجابة',
              '${(analytics.responseRate * 100).toInt()}%',
              Icons.reply,
            ),
            const Divider(height: 24),
            _buildPatternRow(
              'متوسط وقت الاستجابة',
              analytics.averageResponseTime != null
                  ? '${analytics.averageResponseTime!.toInt()} ساعة'
                  : 'غير محدد',
              Icons.timer_outlined,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPatternRow(String label, String value, IconData icon) {
    return Row(
      children: [
        Icon(icon, size: 20, color: Colors.grey[600]),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: TextStyle(
              color: Colors.grey[700],
            ),
          ),
        ),
        Text(
          value,
          style: const TextStyle(
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationsCard(
      BuildContext context, FarmerAnalytics analytics) {
    final recommendations = _generateRecommendations(analytics);

    if (recommendations.isEmpty) {
      return _buildEmptyCard('لا توجد توصيات حالية');
    }

    return Card(
      child: Column(
        children: recommendations.map((rec) {
          return ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: rec.color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(rec.icon, color: rec.color, size: 20),
            ),
            title: Text(
              rec.title,
              style: const TextStyle(fontSize: 14),
            ),
            subtitle: Text(
              rec.description,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          );
        }).toList(),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Text(
      title,
      style: const TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.bold,
      ),
    );
  }

  Widget _buildEmptyCard(String message) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Center(
          child: Text(
            message,
            style: TextStyle(
              color: Colors.grey[500],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildError(BuildContext context, WidgetRef ref, Object error) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            error.toString(),
            style: TextStyle(color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () => ref.invalidate(farmerAnalyticsProvider(farmerId)),
            child: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  // Helper methods

  Color _getScoreColor(double score) {
    if (score >= 61) return Colors.green;
    if (score >= 31) return Colors.orange;
    return Colors.red;
  }

  String _getScoreLabel(double score) {
    if (score >= 61) return 'جيد';
    if (score >= 31) return 'متوسط';
    return 'ضعيف';
  }

  String _getEngagementDescription(double score) {
    if (score >= 80) {
      return 'مستوى تفاعل ممتاز. المزارع نشط ومتجاوب بشكل كبير.';
    }
    if (score >= 60) {
      return 'مستوى تفاعل جيد. يمكن تحسينه بزيادة التواصل المنتظم.';
    }
    if (score >= 40) {
      return 'مستوى تفاعل متوسط. يحتاج لمزيد من المتابعة والتواصل.';
    }
    if (score >= 20) {
      return 'مستوى تفاعل ضعيف. يُنصح بتغيير استراتيجية التواصل.';
    }
    return 'مستوى تفاعل منخفض جداً. قد يحتاج لتدخل خاص.';
  }

  _InteractionTypeInfo _getInteractionTypeInfo(InteractionType type) {
    switch (type) {
      case InteractionType.call:
        return _InteractionTypeInfo('مكالمة', Icons.phone, Colors.blue);
      case InteractionType.visit:
        return _InteractionTypeInfo('زيارة', Icons.location_on, Colors.orange);
      case InteractionType.whatsapp:
        return _InteractionTypeInfo(
            'واتساب', Icons.chat, const Color(0xFF25D366));
      case InteractionType.sms:
        return _InteractionTypeInfo('رسالة', Icons.sms, Colors.purple);
      case InteractionType.email:
        return _InteractionTypeInfo('بريد', Icons.email, Colors.red);
      case InteractionType.meeting:
        return _InteractionTypeInfo('اجتماع', Icons.groups, Colors.indigo);
      case InteractionType.note:
        return _InteractionTypeInfo('ملاحظة', Icons.note, Colors.grey);
      default:
        return _InteractionTypeInfo('أخرى', Icons.touch_app, Colors.grey);
    }
  }

  _OutcomeInfo _getOutcomeInfo(InteractionOutcome outcome) {
    switch (outcome) {
      case InteractionOutcome.successful:
        return _OutcomeInfo('ناجح', Colors.green);
      case InteractionOutcome.interested:
        return _OutcomeInfo('مهتم', Colors.blue);
      case InteractionOutcome.noAnswer:
        return _OutcomeInfo('لم يرد', Colors.grey);
      case InteractionOutcome.busy:
        return _OutcomeInfo('مشغول', Colors.orange);
      case InteractionOutcome.rescheduled:
        return _OutcomeInfo('أعيد جدولته', Colors.purple);
      case InteractionOutcome.notInterested:
        return _OutcomeInfo('غير مهتم', Colors.red);
      case InteractionOutcome.converted:
        return _OutcomeInfo('تم التحويل', Colors.teal);
      case InteractionOutcome.pending:
        return _OutcomeInfo('معلق', Colors.amber);
      case InteractionOutcome.cancelled:
        return _OutcomeInfo('ملغي', Colors.red[300]!);
    }
  }

  double _calculatePositiveOutcomes(
      Map<String, int> outcomes, int total) {
    if (total == 0) return 0;
    final positive = (outcomes['successful'] ?? 0) +
        (outcomes['interested'] ?? 0) +
        (outcomes['converted'] ?? 0);
    return positive / total;
  }

  double _calculateNeutralOutcomes(
      Map<String, int> outcomes, int total) {
    if (total == 0) return 0;
    final neutral = (outcomes['noAnswer'] ?? 0) +
        (outcomes['busy'] ?? 0) +
        (outcomes['rescheduled'] ?? 0) +
        (outcomes['pending'] ?? 0);
    return neutral / total;
  }

  double _calculateNegativeOutcomes(
      Map<String, int> outcomes, int total) {
    if (total == 0) return 0;
    final negative = (outcomes['notInterested'] ?? 0) +
        (outcomes['cancelled'] ?? 0);
    return negative / total;
  }

  String _formatMonthKey(String key) {
    // Expecting format: "2024-01"
    final parts = key.split('-');
    if (parts.length != 2) return key;

    final months = [
      'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
      'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ];

    final monthIndex = int.tryParse(parts[1]);
    if (monthIndex == null || monthIndex < 1 || monthIndex > 12) return key;

    return months[monthIndex - 1].substring(0, 3);
  }

  List<_Recommendation> _generateRecommendations(FarmerAnalytics analytics) {
    final recommendations = <_Recommendation>[];

    // Check engagement score
    if (analytics.engagementScore < 30) {
      recommendations.add(_Recommendation(
        title: 'زيادة وتيرة التواصل',
        description: 'مستوى التفاعل منخفض، يُنصح بتكثيف التواصل',
        icon: Icons.trending_up,
        color: Colors.orange,
      ));
    }

    // Check days since last interaction
    if (analytics.daysSinceLastInteraction != null &&
        analytics.daysSinceLastInteraction! > 30) {
      recommendations.add(_Recommendation(
        title: 'متابعة فورية',
        description: 'لم يتم التواصل منذ ${analytics.daysSinceLastInteraction} يوم',
        icon: Icons.warning,
        color: Colors.red,
      ));
    }

    // Check success rate
    if (analytics.successRate < 0.3) {
      recommendations.add(_Recommendation(
        title: 'مراجعة استراتيجية التواصل',
        description: 'معدل النجاح منخفض، قد يحتاج لنهج مختلف',
        icon: Icons.psychology,
        color: Colors.purple,
      ));
    }

    // Check response rate
    if (analytics.responseRate < 0.5) {
      recommendations.add(_Recommendation(
        title: 'تجربة قنوات أخرى',
        description: 'معدل الاستجابة ضعيف، جرب قناة تواصل مختلفة',
        icon: Icons.swap_horiz,
        color: Colors.blue,
      ));
    }

    // Positive recommendation if doing well
    if (analytics.engagementScore >= 70 && analytics.successRate >= 0.7) {
      recommendations.add(_Recommendation(
        title: 'أداء ممتاز',
        description: 'استمر على نفس النهج في التواصل',
        icon: Icons.thumb_up,
        color: Colors.green,
      ));
    }

    return recommendations;
  }
}

/// Helper class for interaction type info
class _InteractionTypeInfo {
  final String label;
  final IconData icon;
  final Color color;

  _InteractionTypeInfo(this.label, this.icon, this.color);
}

/// Helper class for outcome info
class _OutcomeInfo {
  final String label;
  final Color color;

  _OutcomeInfo(this.label, this.color);
}

/// Helper class for recommendations
class _Recommendation {
  final String title;
  final String description;
  final IconData icon;
  final Color color;

  _Recommendation({
    required this.title,
    required this.description,
    required this.icon,
    required this.color,
  });
}
