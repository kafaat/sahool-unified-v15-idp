import 'package:flutter/material.dart';
import '../../../../core/ui/field_status_mapper.dart';
import '../../../field/domain/entities/field.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../analytics/domain/entities/field_history.dart';
import '../../../analytics/ui/widgets/ndvi_trend_chart.dart';

/// Field Context Panel - لوحة معلومات الحقل
///
/// تظهر عند الضغط على حقل في الخريطة
/// توفر نظرة سريعة + أزرار الإجراءات + تحليل تاريخي
class FieldContextPanel extends StatefulWidget {
  final Field field;
  final VoidCallback onClose;
  final VoidCallback onDetails;
  final VoidCallback? onAddTask;
  final VoidCallback? onNavigate;

  const FieldContextPanel({
    super.key,
    required this.field,
    required this.onClose,
    required this.onDetails,
    this.onAddTask,
    this.onNavigate,
  });

  @override
  State<FieldContextPanel> createState() => _FieldContextPanelState();
}

class _FieldContextPanelState extends State<FieldContextPanel> {
  bool _showAnalytics = false;

  // Mock History Data (بيانات وهمية للتجربة)
  List<NdviRecord> get _mockHistory => [
        NdviRecord(
          date: DateTime.now().subtract(const Duration(days: 28)),
          value: 0.35 + (widget.field.ndvi * 0.2),
        ),
        NdviRecord(
          date: DateTime.now().subtract(const Duration(days: 21)),
          value: 0.42 + (widget.field.ndvi * 0.15),
        ),
        NdviRecord(
          date: DateTime.now().subtract(const Duration(days: 14)),
          value: 0.50 + (widget.field.ndvi * 0.1),
        ),
        NdviRecord(
          date: DateTime.now().subtract(const Duration(days: 7)),
          value: widget.field.ndvi * 0.9,
        ),
        NdviRecord(
          date: DateTime.now().subtract(const Duration(days: 3)),
          value: widget.field.ndvi * 0.95,
        ),
        NdviRecord(
          date: DateTime.now(),
          value: widget.field.ndvi,
        ),
      ];

  FieldAnalytics get _analytics => FieldAnalytics(
        fieldId: widget.field.id,
        history: _mockHistory,
        yieldForecast: widget.field.ndvi * 4.5,
      );

  @override
  Widget build(BuildContext context) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeOutCubic,
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.15),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Drag handle
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header: Name + Status + Close
                _buildHeader(),

                const SizedBox(height: 16),

                // Content: Summary or Analytics
                AnimatedSwitcher(
                  duration: const Duration(milliseconds: 300),
                  transitionBuilder: (child, animation) {
                    return FadeTransition(
                      opacity: animation,
                      child: SizeTransition(
                        sizeFactor: animation,
                        child: child,
                      ),
                    );
                  },
                  child: _showAnalytics
                      ? _buildAnalyticsView()
                      : _buildSummaryView(),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Status indicator circle
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: widget.field.statusBackgroundColor,
            shape: BoxShape.circle,
          ),
          child: Icon(
            widget.field.statusIcon,
            color: widget.field.statusColor,
            size: 24,
          ),
        ),
        const SizedBox(width: 12),

        // Name and crop type
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                widget.field.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.grass, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    widget.field.cropType,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Icon(Icons.square_foot, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    widget.field.areaFormatted,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        // Close button
        IconButton(
          onPressed: widget.onClose,
          icon: const Icon(Icons.close),
          style: IconButton.styleFrom(
            backgroundColor: Colors.grey[100],
          ),
        ),
      ],
    );
  }

  /// العرض الأصلي (الملخص)
  Widget _buildSummaryView() {
    return Column(
      key: const ValueKey('summary'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Quick Stats Row
        _buildStatsRow(),

        const SizedBox(height: 16),

        // NDVI Progress Bar
        _buildNdviBar(),

        const SizedBox(height: 20),

        // Action Buttons
        _buildActions(),
      ],
    );
  }

  /// عرض التحليل (الرسم البياني)
  Widget _buildAnalyticsView() {
    return Column(
      key: const ValueKey('analytics'),
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Trend header
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'تحليل الأداء (30 يوم)',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey[800],
                fontSize: 14,
              ),
            ),
            TrendIndicator(
              trend: _analytics.trend,
              changeRate: _analytics.changeRate,
            ),
          ],
        ),

        const SizedBox(height: 12),

        // Chart
        SizedBox(
          height: 180,
          child: NdviTrendChart(
            history: _mockHistory,
            showDots: true,
          ),
        ),

        const SizedBox(height: 12),

        // Stats summary
        Row(
          children: [
            _buildStatChip(
              'المتوسط',
              _analytics.averageNdvi.toStringAsFixed(2),
              Icons.show_chart,
            ),
            const SizedBox(width: 8),
            _buildStatChip(
              'الذروة',
              _analytics.peakRecord?.value.toStringAsFixed(2) ?? '-',
              Icons.arrow_upward,
            ),
            const SizedBox(width: 8),
            _buildStatChip(
              'التوقع',
              '${_analytics.yieldForecast.toStringAsFixed(1)} طن/هـ',
              Icons.eco,
            ),
          ],
        ),

        const SizedBox(height: 16),

        // Back button
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: () => setState(() => _showAnalytics = false),
                icon: const Icon(Icons.arrow_back),
                label: const Text('عودة للملخص'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: widget.onDetails,
                icon: const Icon(Icons.open_in_full),
                label: const Text('تفاصيل كاملة'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildStatsRow() {
    return Row(
      children: [
        // Status badge
        _buildBadge(
          label: widget.field.statusText,
          color: widget.field.statusColor,
          textColor: Colors.white,
          icon: widget.field.statusIcon,
        ),

        const SizedBox(width: 8),

        // NDVI badge
        _buildBadge(
          label: 'NDVI ${widget.field.ndviFormatted}',
          color: widget.field.statusBackgroundColor,
          textColor: widget.field.statusColor,
        ),

        const Spacer(),

        // Pending tasks (if any)
        if (widget.field.pendingTasks > 0)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.orange.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.task_alt, size: 14, color: Colors.orange),
                const SizedBox(width: 4),
                Text(
                  '${widget.field.pendingTasks} مهام',
                  style: const TextStyle(
                    color: Colors.orange,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildNdviBar() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'مؤشر صحة المحصول',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
            Text(
              widget.field.ndviPercentage,
              style: TextStyle(
                color: widget.field.statusColor,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: widget.field.ndvi,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation(widget.field.statusColor),
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  Widget _buildActions() {
    return Row(
      children: [
        // Primary action: Analytics
        Expanded(
          flex: 2,
          child: ElevatedButton.icon(
            onPressed: () => setState(() => _showAnalytics = true),
            icon: const Icon(Icons.show_chart),
            label: const Text('تحليل الأداء'),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),

        const SizedBox(width: 12),

        // Secondary action: Add Task
        _buildIconAction(
          icon: Icons.add_task,
          onTap: widget.onAddTask,
          tooltip: 'إضافة مهمة',
        ),

        const SizedBox(width: 8),

        // Navigate to field
        _buildIconAction(
          icon: Icons.navigation,
          onTap: widget.onNavigate,
          tooltip: 'الانتقال للحقل',
        ),
      ],
    );
  }

  Widget _buildIconAction({
    required IconData icon,
    VoidCallback? onTap,
    required String tooltip,
  }) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: Colors.grey[700]),
        ),
      ),
    );
  }

  Widget _buildBadge({
    required String label,
    required Color color,
    required Color textColor,
    IconData? icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: textColor),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: TextStyle(
              color: textColor,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatChip(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 8),
        decoration: BoxDecoration(
          color: Colors.grey[100],
          borderRadius: BorderRadius.circular(10),
        ),
        child: Column(
          children: [
            Icon(icon, size: 16, color: SahoolColors.primary),
            const SizedBox(height: 4),
            Text(
              value,
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
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
      ),
    );
  }
}

/// Animated wrapper for the context panel
class AnimatedFieldContextPanel extends StatelessWidget {
  final Field? field;
  final VoidCallback onClose;
  final VoidCallback onDetails;
  final VoidCallback? onAddTask;

  const AnimatedFieldContextPanel({
    super.key,
    required this.field,
    required this.onClose,
    required this.onDetails,
    this.onAddTask,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      transitionBuilder: (Widget child, Animation<double> animation) {
        return SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, 1),
            end: Offset.zero,
          ).animate(CurvedAnimation(
            parent: animation,
            curve: Curves.easeOutCubic,
          )),
          child: child,
        );
      },
      child: field != null
          ? FieldContextPanel(
              key: ValueKey(field!.id),
              field: field!,
              onClose: onClose,
              onDetails: onDetails,
              onAddTask: onAddTask,
            )
          : const SizedBox.shrink(),
    );
  }
}
