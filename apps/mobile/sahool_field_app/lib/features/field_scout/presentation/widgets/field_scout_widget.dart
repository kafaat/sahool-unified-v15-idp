import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/scout_session.dart';
import '../providers/field_scout_provider.dart';

/// SAHOOL Field Scout Widget
/// واجهة مسح الحقول الذكي
///
/// Features:
/// - Live GPS tracking display
/// - Quick checkpoint buttons
/// - Issue reporting
/// - Camera integration
/// - Session summary

class FieldScoutWidget extends ConsumerWidget {
  final String fieldId;
  final String fieldName;

  const FieldScoutWidget({
    super.key,
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scoutState = ref.watch(fieldScoutProvider);

    return Card(
      margin: const EdgeInsets.all(16),
      child: scoutState.hasActiveSession
          ? _ActiveSessionView(state: scoutState)
          : _StartSessionView(
              fieldId: fieldId,
              fieldName: fieldName,
            ),
    );
  }
}

/// عرض بدء الجلسة
class _StartSessionView extends ConsumerWidget {
  final String fieldId;
  final String fieldName;

  const _StartSessionView({
    required this.fieldId,
    required this.fieldName,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(
            Icons.explore,
            size: 64,
            color: Colors.green,
          ),
          const SizedBox(height: 16),
          Text(
            'مسح الحقل الذكي',
            style: Theme.of(context).textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            fieldName,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 24),
          const Text(
            'ابدأ جلسة مسح لتتبع مسارك، تسجيل الملاحظات، والتقاط الصور مع تحديد المواقع',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 24),
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () => _startSession(context, ref),
              icon: const Icon(Icons.play_arrow),
              label: const Text('بدء المسح'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _startSession(BuildContext context, WidgetRef ref) {
    ref.read(fieldScoutProvider.notifier).startSession(
      fieldId: fieldId,
      fieldName: fieldName,
      scouterId: 'current_user_id', // Get from auth
      scouterName: 'المستخدم الحالي', // Get from auth
    );
  }
}

/// عرض الجلسة النشطة
class _ActiveSessionView extends ConsumerWidget {
  final FieldScoutState state;

  const _ActiveSessionView({required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final session = state.currentSession!;

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        // Header
        _SessionHeader(session: session, isTracking: state.isTracking),

        const Divider(height: 1),

        // Stats
        _SessionStats(session: session),

        const Divider(height: 1),

        // Quick Actions
        _QuickActions(state: state),

        const Divider(height: 1),

        // Control Buttons
        _ControlButtons(session: session),
      ],
    );
  }
}

/// رأس الجلسة
class _SessionHeader extends StatelessWidget {
  final ScoutSession session;
  final bool isTracking;

  const _SessionHeader({
    required this.session,
    required this.isTracking,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      color: isTracking ? Colors.green.shade50 : Colors.orange.shade50,
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: isTracking ? Colors.green : Colors.orange,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(
              isTracking ? Icons.gps_fixed : Icons.gps_off,
              color: Colors.white,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  session.fieldName,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                Text(
                  isTracking ? 'جاري التتبع...' : 'متوقف مؤقتاً',
                  style: TextStyle(
                    color: isTracking ? Colors.green : Colors.orange,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          _DurationDisplay(startedAt: session.startedAt),
        ],
      ),
    );
  }
}

/// عرض المدة
class _DurationDisplay extends StatelessWidget {
  final DateTime startedAt;

  const _DurationDisplay({required this.startedAt});

  @override
  Widget build(BuildContext context) {
    return StreamBuilder(
      stream: Stream.periodic(const Duration(seconds: 1)),
      builder: (context, snapshot) {
        final duration = DateTime.now().difference(startedAt);
        final hours = duration.inHours;
        final minutes = duration.inMinutes % 60;
        final seconds = duration.inSeconds % 60;

        return Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
          decoration: BoxDecoration(
            color: Colors.black87,
            borderRadius: BorderRadius.circular(16),
          ),
          child: Text(
            hours > 0
                ? '$hours:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}'
                : '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}',
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontFamily: 'monospace',
            ),
          ),
        );
      },
    );
  }
}

/// إحصائيات الجلسة
class _SessionStats extends StatelessWidget {
  final ScoutSession session;

  const _SessionStats({required this.session});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _StatItem(
            icon: Icons.location_on,
            value: '${session.checkpoints.length}',
            label: 'نقاط',
          ),
          _StatItem(
            icon: Icons.warning,
            value: '${session.issuesCount}',
            label: 'مشاكل',
            color: session.issuesCount > 0 ? Colors.orange : null,
          ),
          _StatItem(
            icon: Icons.straighten,
            value: '${(session.distanceMeters / 1000).toStringAsFixed(1)}',
            label: 'كم',
          ),
          _StatItem(
            icon: Icons.camera_alt,
            value: '${session.checkpoints.where((c) => c.hasPhotos).length}',
            label: 'صور',
          ),
        ],
      ),
    );
  }
}

/// عنصر إحصائية
class _StatItem extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;
  final Color? color;

  const _StatItem({
    required this.icon,
    required this.value,
    required this.label,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color ?? Colors.grey),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }
}

/// الإجراءات السريعة
class _QuickActions extends ConsumerWidget {
  final FieldScoutState state;

  const _QuickActions({required this.state});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'إجراءات سريعة',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _QuickActionButton(
                  icon: Icons.add_location,
                  label: 'نقطة تفتيش',
                  color: Colors.blue,
                  onPressed: () => _addQuickCheckpoint(ref),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _QuickActionButton(
                  icon: Icons.warning_amber,
                  label: 'تسجيل مشكلة',
                  color: Colors.orange,
                  onPressed: () => _showIssueDialog(context, ref),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _QuickActionButton(
                  icon: Icons.camera_alt,
                  label: 'التقاط صورة',
                  color: Colors.purple,
                  onPressed: () => _capturePhoto(context, ref),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  void _addQuickCheckpoint(WidgetRef ref) {
    if (state.currentLocation == null) return;
    ref.read(fieldScoutProvider.notifier).addQuickCheckpoint(
      state.currentLocation!,
    );
  }

  void _showIssueDialog(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => _IssueReportSheet(state: state),
    );
  }

  void _capturePhoto(BuildContext context, WidgetRef ref) {
    // In real implementation, open camera
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فتح الكاميرا...')),
    );
  }
}

/// زر إجراء سريع
class _QuickActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback onPressed;

  const _QuickActionButton({
    required this.icon,
    required this.label,
    required this.color,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: color.withOpacity(0.1),
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 12),
          child: Column(
            children: [
              Icon(icon, color: color),
              const SizedBox(height: 4),
              Text(
                label,
                style: TextStyle(
                  fontSize: 11,
                  color: color,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// أزرار التحكم
class _ControlButtons extends ConsumerWidget {
  final ScoutSession session;

  const _ControlButtons({required this.session});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final isPaused = session.status == ScoutSessionStatus.paused;

    return Padding(
      padding: const EdgeInsets.all(16),
      child: Row(
        children: [
          Expanded(
            child: OutlinedButton.icon(
              onPressed: () => _cancelSession(context, ref),
              icon: const Icon(Icons.close),
              label: const Text('إلغاء'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                side: const BorderSide(color: Colors.red),
              ),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: isPaused
                ? ElevatedButton.icon(
                    onPressed: () => ref.read(fieldScoutProvider.notifier).resumeSession(),
                    icon: const Icon(Icons.play_arrow),
                    label: const Text('استئناف'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.blue,
                      foregroundColor: Colors.white,
                    ),
                  )
                : OutlinedButton.icon(
                    onPressed: () => ref.read(fieldScoutProvider.notifier).pauseSession(),
                    icon: const Icon(Icons.pause),
                    label: const Text('إيقاف'),
                  ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: ElevatedButton.icon(
              onPressed: () => _endSession(context, ref),
              icon: const Icon(Icons.check),
              label: const Text('إنهاء'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green,
                foregroundColor: Colors.white,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _cancelSession(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إلغاء المسح'),
        content: const Text('هل أنت متأكد من إلغاء جلسة المسح الحالية؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('لا'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ref.read(fieldScoutProvider.notifier).cancelSession();
            },
            child: const Text('نعم، إلغاء'),
          ),
        ],
      ),
    );
  }

  void _endSession(BuildContext context, WidgetRef ref) async {
    final session = await ref.read(fieldScoutProvider.notifier).endSession();
    if (context.mounted) {
      _showSessionSummary(context, session);
    }
  }

  void _showSessionSummary(BuildContext context, ScoutSession session) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => _SessionSummarySheet(session: session),
    );
  }
}

/// نافذة تسجيل مشكلة
class _IssueReportSheet extends ConsumerStatefulWidget {
  final FieldScoutState state;

  const _IssueReportSheet({required this.state});

  @override
  ConsumerState<_IssueReportSheet> createState() => _IssueReportSheetState();
}

class _IssueReportSheetState extends ConsumerState<_IssueReportSheet> {
  IssueCategory? _selectedCategory;
  IssueSeverity _selectedSeverity = IssueSeverity.medium;
  final _descriptionController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) => Container(
        padding: const EdgeInsets.all(20),
        child: ListView(
          controller: scrollController,
          children: [
            const Text(
              'تسجيل مشكلة',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),

            // Category selection
            const Text('نوع المشكلة'),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: IssueCategory.values.map((category) {
                final isSelected = _selectedCategory == category;
                return ChoiceChip(
                  label: Text(_getCategoryLabel(category)),
                  selected: isSelected,
                  onSelected: (selected) {
                    setState(() => _selectedCategory = selected ? category : null);
                  },
                );
              }).toList(),
            ),
            const SizedBox(height: 20),

            // Severity selection
            const Text('الشدة'),
            const SizedBox(height: 8),
            SegmentedButton<IssueSeverity>(
              segments: IssueSeverity.values.map((severity) {
                return ButtonSegment(
                  value: severity,
                  label: Text(_getSeverityLabel(severity)),
                );
              }).toList(),
              selected: {_selectedSeverity},
              onSelectionChanged: (selection) {
                setState(() => _selectedSeverity = selection.first);
              },
            ),
            const SizedBox(height: 20),

            // Description
            TextField(
              controller: _descriptionController,
              maxLines: 3,
              decoration: const InputDecoration(
                labelText: 'الوصف',
                hintText: 'اكتب وصفاً للمشكلة...',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 20),

            // Submit button
            ElevatedButton(
              onPressed: _selectedCategory != null ? _submitIssue : null,
              child: const Text('تسجيل المشكلة'),
            ),
          ],
        ),
      ),
    );
  }

  String _getCategoryLabel(IssueCategory category) {
    return switch (category) {
      IssueCategory.pest => 'آفة',
      IssueCategory.disease => 'مرض',
      IssueCategory.weed => 'أعشاب ضارة',
      IssueCategory.nutrient => 'نقص غذائي',
      IssueCategory.water => 'مشكلة مائية',
      IssueCategory.soil => 'مشكلة تربة',
      IssueCategory.weather => 'ضرر مناخي',
      IssueCategory.mechanical => 'ضرر ميكانيكي',
      IssueCategory.other => 'أخرى',
    };
  }

  String _getSeverityLabel(IssueSeverity severity) {
    return switch (severity) {
      IssueSeverity.low => 'بسيط',
      IssueSeverity.medium => 'متوسط',
      IssueSeverity.high => 'عالي',
      IssueSeverity.critical => 'حرج',
    };
  }

  void _submitIssue() {
    if (widget.state.currentLocation == null) return;

    ref.read(fieldScoutProvider.notifier).addIssueCheckpoint(
      location: widget.state.currentLocation!,
      category: _selectedCategory!,
      severity: _selectedSeverity,
      description: _descriptionController.text,
    );

    Navigator.pop(context);
  }

  @override
  void dispose() {
    _descriptionController.dispose();
    super.dispose();
  }
}

/// نافذة ملخص الجلسة
class _SessionSummarySheet extends StatelessWidget {
  final ScoutSession session;

  const _SessionSummarySheet({required this.session});

  @override
  Widget build(BuildContext context) {
    final summary = session.summary!;

    return DraggableScrollableSheet(
      initialChildSize: 0.8,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (context, scrollController) => Container(
        padding: const EdgeInsets.all(20),
        child: ListView(
          controller: scrollController,
          children: [
            Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.green, size: 32),
                const SizedBox(width: 12),
                const Expanded(
                  child: Text(
                    'تم إنهاء المسح',
                    style: TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: const Icon(Icons.close),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Health Status
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: _getHealthColor(summary.overallHealthStatus).withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  Icon(
                    _getHealthIcon(summary.overallHealthStatus),
                    color: _getHealthColor(summary.overallHealthStatus),
                    size: 32,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'حالة الحقل',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey,
                          ),
                        ),
                        Text(
                          summary.overallHealthStatus ?? 'غير محدد',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: _getHealthColor(summary.overallHealthStatus),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Stats Grid
            GridView.count(
              crossAxisCount: 2,
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              childAspectRatio: 2,
              mainAxisSpacing: 12,
              crossAxisSpacing: 12,
              children: [
                _SummaryStatCard(
                  icon: Icons.timer,
                  label: 'المدة',
                  value: '${summary.duration.inMinutes} دقيقة',
                ),
                _SummaryStatCard(
                  icon: Icons.straighten,
                  label: 'المسافة',
                  value: '${(summary.distanceMeters / 1000).toStringAsFixed(2)} كم',
                ),
                _SummaryStatCard(
                  icon: Icons.location_on,
                  label: 'نقاط التفتيش',
                  value: '${summary.totalCheckpoints}',
                ),
                _SummaryStatCard(
                  icon: Icons.warning,
                  label: 'المشاكل',
                  value: '${summary.issuesFound}',
                  color: summary.issuesFound > 0 ? Colors.orange : null,
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Recommendations
            if (summary.recommendations.isNotEmpty) ...[
              const Text(
                'التوصيات',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
              const SizedBox(height: 8),
              ...summary.recommendations.map((rec) => Padding(
                padding: const EdgeInsets.symmetric(vertical: 4),
                child: Row(
                  children: [
                    const Icon(Icons.check, color: Colors.green, size: 20),
                    const SizedBox(width: 8),
                    Expanded(child: Text(rec)),
                  ],
                ),
              )),
            ],
            const SizedBox(height: 20),

            // Action buttons
            ElevatedButton.icon(
              onPressed: () {
                // Share or save report
                Navigator.pop(context);
              },
              icon: const Icon(Icons.share),
              label: const Text('مشاركة التقرير'),
            ),
          ],
        ),
      ),
    );
  }

  Color _getHealthColor(String? status) {
    if (status == null) return Colors.grey;
    if (status.contains('ممتاز')) return Colors.green;
    if (status.contains('جيد')) return Colors.lightGreen;
    if (status.contains('متوسط')) return Colors.orange;
    if (status.contains('سيء')) return Colors.deepOrange;
    return Colors.red;
  }

  IconData _getHealthIcon(String? status) {
    if (status == null) return Icons.help;
    if (status.contains('ممتاز')) return Icons.sentiment_very_satisfied;
    if (status.contains('جيد')) return Icons.sentiment_satisfied;
    if (status.contains('متوسط')) return Icons.sentiment_neutral;
    if (status.contains('سيء')) return Icons.sentiment_dissatisfied;
    return Icons.sentiment_very_dissatisfied;
  }
}

/// بطاقة إحصائية الملخص
class _SummaryStatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? color;

  const _SummaryStatCard({
    required this.icon,
    required this.label,
    required this.value,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Icon(icon, color: color ?? Colors.grey),
          const SizedBox(width: 8),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                label,
                style: const TextStyle(
                  fontSize: 12,
                  color: Colors.grey,
                ),
              ),
              Text(
                value,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
