/// Advisory Details Screen
/// شاشة تفاصيل التوصية
///
/// Shows detailed information about a specific advisory
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory.dart';
import '../../state/ai_advisor_providers.dart';
import '../widgets/feedback_buttons.dart';

class AdvisoryDetailsScreen extends ConsumerStatefulWidget {
  final String advisoryId;

  const AdvisoryDetailsScreen({
    super.key,
    required this.advisoryId,
  });

  @override
  ConsumerState<AdvisoryDetailsScreen> createState() => _AdvisoryDetailsScreenState();
}

class _AdvisoryDetailsScreenState extends ConsumerState<AdvisoryDetailsScreen> {
  @override
  Widget build(BuildContext context) {
    final asyncState = ref.watch(advisoryDetailsProvider(widget.advisoryId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('تفاصيل التوصية'),
        actions: [
          if (asyncState.valueOrNull != null)
            PopupMenuButton(
              itemBuilder: (context) => [
                const PopupMenuItem(
                  value: 'share',
                  child: Row(
                    children: [
                      Icon(Icons.share),
                      SizedBox(width: 8),
                      Text('مشاركة'),
                    ],
                  ),
                ),
                if (asyncState.valueOrNull!.status == AdvisoryStatus.pending) ...[
                  const PopupMenuItem(
                    value: 'apply',
                    child: Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green),
                        SizedBox(width: 8),
                        Text('تم التطبيق'),
                      ],
                    ),
                  ),
                  const PopupMenuItem(
                    value: 'dismiss',
                    child: Row(
                      children: [
                        Icon(Icons.cancel, color: Colors.orange),
                        SizedBox(width: 8),
                        Text('تجاهل'),
                      ],
                    ),
                  ),
                ],
              ],
              onSelected: (value) => _handleMenuAction(value, asyncState.valueOrNull!),
            ),
        ],
      ),
      body: asyncState.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, _) => _buildErrorState(error.toString()),
        data: (advisory) => advisory == null
            ? _buildErrorState(null)
            : _buildContent(advisory),
      ),
      bottomNavigationBar: asyncState.valueOrNull != null &&
              asyncState.valueOrNull!.status == AdvisoryStatus.pending
          ? _buildActionBar(asyncState.valueOrNull!)
          : null,
    );
  }

  Widget _buildErrorState(String? error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            error ?? 'حدث خطأ في تحميل التوصية',
            style: TextStyle(color: Colors.grey[600]),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              ref.invalidate(advisoryDetailsProvider(widget.advisoryId));
            },
            child: const Text('إعادة المحاولة'),
          ),
        ],
      ),
    );
  }

  Widget _buildContent(Advisory advisory) {
    final locale = Localizations.localeOf(context).languageCode;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header card
          _buildHeaderCard(advisory, locale),

          const SizedBox(height: 16),

          // Description
          _buildSection(
            title: 'التفاصيل',
            child: Text(
              advisory.getLocalizedDescription(locale),
              style: const TextStyle(
                fontSize: 15,
                height: 1.6,
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Actions
          if (advisory.actions.isNotEmpty)
            _buildSection(
              title: 'خطوات التنفيذ',
              child: Column(
                children: advisory.getLocalizedActions(locale)
                    .asMap()
                    .entries
                    .map((entry) => _buildActionItem(entry.key + 1, entry.value))
                    .toList(),
              ),
            ),

          const SizedBox(height: 16),

          // Timing
          if (advisory.timing != null) _buildTimingCard(advisory.timing!),

          const SizedBox(height: 16),

          // Economic impact
          if (advisory.economicImpact != null)
            _buildEconomicCard(advisory.economicImpact!, locale),

          const SizedBox(height: 16),

          // Context info
          _buildContextCard(advisory),

          const SizedBox(height: 16),

          // Feedback section
          _buildFeedbackSection(advisory),

          const SizedBox(height: 24),

          // Sources
          if (advisory.sources.isNotEmpty)
            _buildSection(
              title: 'المصادر',
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: advisory.sources
                    .map((source) => Padding(
                          padding: const EdgeInsets.only(bottom: 4),
                          child: Row(
                            children: [
                              Icon(Icons.link, size: 16, color: Colors.grey[600]),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  source,
                                  style: TextStyle(
                                    fontSize: 13,
                                    color: Colors.grey[600],
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ))
                    .toList(),
              ),
            ),

          // Confidence indicator
          _buildConfidenceIndicator(advisory.confidence),

          const SizedBox(height: 100), // Space for bottom bar
        ],
      ),
    );
  }

  Widget _buildHeaderCard(Advisory advisory, String locale) {
    final priorityColor = Color(int.parse(
      advisory.priorityColorHex.replaceFirst('#', '0xFF'),
    ));

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: priorityColor.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: priorityColor.withValues(alpha: 0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Type and priority badges
          Row(
            children: [
              _buildBadge(
                icon: _getTypeIcon(advisory.type),
                label: advisory.typeAr,
                color: SahoolTheme.primary,
              ),
              const SizedBox(width: 8),
              _buildBadge(
                icon: Icons.flag,
                label: advisory.priorityAr,
                color: priorityColor,
              ),
              const Spacer(),
              _buildStatusBadge(advisory.status),
            ],
          ),
          const SizedBox(height: 12),

          // Title
          Text(
            advisory.getLocalizedTitle(locale),
            style: const TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),

          // Field name
          if (advisory.fieldName != null) ...[
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(Icons.grass, size: 16, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(
                  advisory.fieldName!,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ],

          // Timestamp
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.access_time, size: 16, color: Colors.grey[600]),
              const SizedBox(width: 4),
              Text(
                DateFormat('dd/MM/yyyy HH:mm').format(advisory.createdAt),
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildBadge({
    required IconData icon,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge(AdvisoryStatus status) {
    Color color;
    String label;
    IconData icon;

    switch (status) {
      case AdvisoryStatus.pending:
        color = Colors.orange;
        label = 'قيد الانتظار';
        icon = Icons.hourglass_empty;
        break;
      case AdvisoryStatus.applied:
        color = Colors.green;
        label = 'مطبقة';
        icon = Icons.check_circle;
        break;
      case AdvisoryStatus.dismissed:
        color = Colors.grey;
        label = 'متجاهلة';
        icon = Icons.cancel;
        break;
      case AdvisoryStatus.expired:
        color = Colors.red;
        label = 'منتهية';
        icon = Icons.timer_off;
        break;
    }

    return _buildBadge(icon: icon, label: label, color: color);
  }

  Widget _buildSection({
    required String title,
    required Widget child,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: const TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 12),
        child,
      ],
    );
  }

  Widget _buildActionItem(int number, String action) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: SahoolTheme.primary.withValues(alpha: 0.1),
              shape: BoxShape.circle,
            ),
            alignment: Alignment.center,
            child: Text(
              '$number',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                color: SahoolTheme.primary,
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              action,
              style: const TextStyle(fontSize: 14, height: 1.5),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTimingCard(AdvisoryTiming timing) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.schedule, color: Colors.blue[700]),
              const SizedBox(width: 8),
              Text(
                'التوقيت المثالي',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.blue[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (timing.bestTimeOfDayAr != null)
            _buildTimingRow('أفضل وقت', timing.bestTimeOfDayAr!),
          if (timing.startTime != null)
            _buildTimingRow(
              'البداية',
              DateFormat('dd/MM HH:mm').format(timing.startTime!),
            ),
          if (timing.endTime != null)
            _buildTimingRow(
              'النهاية',
              DateFormat('dd/MM HH:mm').format(timing.endTime!),
            ),
          if (timing.weatherWindowAr != null)
            _buildTimingRow('نافذة الطقس', timing.weatherWindowAr!),
        ],
      ),
    );
  }

  Widget _buildTimingRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: TextStyle(
              fontSize: 14,
              color: Colors.blue[900],
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w600,
              color: Colors.blue[900],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEconomicCard(EconomicImpact impact, String locale) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.green[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.attach_money, color: Colors.green[700]),
              const SizedBox(width: 8),
              Text(
                'التأثير الاقتصادي',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.green[700],
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (impact.cost != null)
            _buildEconomicRow(
              'التكلفة',
              '${impact.cost!.toStringAsFixed(0)} ${impact.currency}',
              Colors.red[700]!,
            ),
          if (impact.expectedBenefit != null)
            _buildEconomicRow(
              'الفائدة المتوقعة',
              '${impact.expectedBenefit!.toStringAsFixed(0)} ${impact.currency}',
              Colors.green[700]!,
            ),
          if (impact.roi != null)
            _buildEconomicRow(
              'العائد على الاستثمار',
              '${impact.roi!.toStringAsFixed(0)}%',
              Colors.blue[700]!,
            ),
        ],
      ),
    );
  }

  Widget _buildEconomicRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              color: Colors.green[900],
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: valueColor,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildContextCard(Advisory advisory) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'معلومات إضافية',
            style: TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          if (advisory.cropType != null)
            _buildContextRow(
              Icons.eco,
              'المحصول',
              advisory.cropTypeAr ?? advisory.cropType!,
            ),
          if (advisory.weatherContext != null &&
              advisory.weatherContext!.isNotEmpty)
            _buildContextRow(
              Icons.cloud,
              'الطقس',
              (advisory.weatherContext!['condition_ar'] ?? 'متاح') as String,
            ),
          if (advisory.soilContext != null && advisory.soilContext!.isNotEmpty)
            _buildContextRow(
              Icons.landscape,
              'التربة',
              advisory.soilContext!['moisture'] != null
                  ? 'رطوبة ${advisory.soilContext!['moisture']}%'
                  : 'متاح',
            ),
        ],
      ),
    );
  }

  Widget _buildContextRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, size: 18, color: Colors.grey[600]),
          const SizedBox(width: 8),
          Text(
            '$label: ',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[700],
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackSection(Advisory advisory) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.amber[50],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'قيّم هذه التوصية',
            style: TextStyle(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'ساعدنا في تحسين التوصيات',
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 16),
          FeedbackButtons(
            advisoryId: advisory.id,
            initialFeedback: advisory.feedback,
            onFeedbackSubmitted: (feedback) {
              ref.read(feedbackSubmissionProvider.notifier)
                  .submitFeedback(feedback);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildConfidenceIndicator(double confidence) {
    final percentage = (confidence * 100).round();
    Color color;
    if (confidence >= 0.8) {
      color = Colors.green;
    } else if (confidence >= 0.6) {
      color = Colors.orange;
    } else {
      color = Colors.red;
    }

    return Padding(
      padding: const EdgeInsets.only(top: 16),
      child: Row(
        children: [
          Icon(Icons.verified, size: 18, color: color),
          const SizedBox(width: 8),
          Text(
            'مستوى الثقة: $percentage%',
            style: TextStyle(
              fontSize: 13,
              color: color,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildActionBar(Advisory advisory) {
    return Container(
      padding: EdgeInsets.only(
        left: 16,
        right: 16,
        top: 12,
        bottom: MediaQuery.of(context).padding.bottom + 12,
      ),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton(
              onPressed: () => _handleMenuAction('dismiss', advisory),
              child: const Text('تجاهل'),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            flex: 2,
            child: ElevatedButton.icon(
              onPressed: () => _handleMenuAction('apply', advisory),
              icon: const Icon(Icons.check),
              label: const Text('تم التطبيق'),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getTypeIcon(AdvisoryType type) {
    switch (type) {
      case AdvisoryType.irrigation:
        return Icons.water_drop;
      case AdvisoryType.fertilization:
        return Icons.eco;
      case AdvisoryType.pestControl:
        return Icons.pest_control;
      case AdvisoryType.diseaseControl:
        return Icons.healing;
      case AdvisoryType.harvest:
        return Icons.agriculture;
      case AdvisoryType.planting:
        return Icons.grass;
      case AdvisoryType.weather:
        return Icons.cloud;
      case AdvisoryType.general:
        return Icons.lightbulb;
    }
  }

  void _handleMenuAction(String action, Advisory advisory) {
    switch (action) {
      case 'share':
        final buffer = StringBuffer();
        buffer.writeln('━━━ ${advisory.titleAr} ━━━');
        buffer.writeln(advisory.title);
        buffer.writeln();
        buffer.writeln('النوع | Type: ${advisory.type.name}');
        buffer.writeln('الأولوية | Priority: ${advisory.priority.name}');
        buffer.writeln(
            'الثقة | Confidence: ${(advisory.confidence * 100).toStringAsFixed(0)}%');
              buffer.writeln();
        if (advisory.fieldName != null) {
          buffer.writeln('الحقل | Field: ${advisory.fieldName}');
        }
        if (advisory.cropTypeAr != null || advisory.cropType != null) {
          buffer.writeln(
              'المحصول | Crop: ${advisory.cropTypeAr ?? ''} ${advisory.cropType ?? ''}');
        }
        buffer.writeln();
        buffer.writeln('--- الوصف | Description ---');
        buffer.writeln(advisory.descriptionAr);
              buffer.writeln(advisory.description);
              if (advisory.actionsAr.isNotEmpty) {
          buffer.writeln();
          buffer.writeln('--- الإجراءات | Actions ---');
          for (var i = 0; i < advisory.actionsAr.length; i++) {
            buffer.writeln('${i + 1}. ${advisory.actionsAr[i]}');
          }
        }
        if (advisory.actions.isNotEmpty) {
          if (advisory.actionsAr.isEmpty) {
            buffer.writeln();
            buffer.writeln('--- Actions ---');
          }
          for (var i = 0; i < advisory.actions.length; i++) {
            buffer.writeln('${i + 1}. ${advisory.actions[i]}');
          }
        }
        if (advisory.timing != null) {
          buffer.writeln();
          buffer.writeln('التوقيت | Timing: ${advisory.timing}');
        }
        buffer.writeln();
        buffer.writeln('— SAHOOL سهول —');

        Clipboard.setData(ClipboardData(text: buffer.toString()));
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تم نسخ التوصية | Advisory copied'),
            ),
          );
        }
        break;
      case 'apply':
        ref.read(advisoriesProvider.notifier)
            .updateAdvisoryStatus(widget.advisoryId, AdvisoryStatus.applied);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم تعيين التوصية كمطبقة'),
            backgroundColor: Colors.green,
          ),
        );
        break;
      case 'dismiss':
        ref.read(advisoriesProvider.notifier)
            .updateAdvisoryStatus(widget.advisoryId, AdvisoryStatus.dismissed);
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('تم تجاهل التوصية'),
          ),
        );
        break;
    }
  }
}
