import 'dart:math' as math;
import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';

/// Download Progress Indicator - مؤشر تقدم التحميل
///
/// A circular progress indicator with animated effects
class DownloadProgressIndicator extends StatelessWidget {
  final double progress;
  final bool isPaused;
  final double pulseValue;
  final double size;
  final double strokeWidth;

  const DownloadProgressIndicator({
    super.key,
    required this.progress,
    this.isPaused = false,
    this.pulseValue = 0.0,
    this.size = 180,
    this.strokeWidth = 12,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: size,
      height: size,
      child: Stack(
        alignment: Alignment.center,
        children: [
          // Background circle
          Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.grey[100],
            ),
          ),

          // Pulse effect when downloading
          if (!isPaused && progress < 1.0)
            Transform.scale(
              scale: 1 + (pulseValue * 0.05),
              child: Container(
                width: size - strokeWidth * 2,
                height: size - strokeWidth * 2,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: SahoolColors.primary.withValues(alpha: 0.05 + pulseValue * 0.05),
                ),
              ),
            ),

          // Progress arc
          CustomPaint(
            size: Size(size, size),
            painter: _ProgressArcPainter(
              progress: progress,
              strokeWidth: strokeWidth,
              color: isPaused ? Colors.grey : SahoolColors.primary,
              backgroundColor: Colors.grey[300]!,
            ),
          ),

          // Center icon
          Container(
            width: size * 0.5,
            height: size * 0.5,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withValues(alpha: 0.1),
                  blurRadius: 8,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Icon(
              isPaused
                  ? Icons.pause
                  : progress >= 1.0
                      ? Icons.check
                      : Icons.download,
              size: size * 0.25,
              color: isPaused
                  ? Colors.grey
                  : progress >= 1.0
                      ? SahoolColors.success
                      : SahoolColors.primary,
            ),
          ),
        ],
      ),
    );
  }
}

/// Progress arc painter - رسام قوس التقدم
class _ProgressArcPainter extends CustomPainter {
  final double progress;
  final double strokeWidth;
  final Color color;
  final Color backgroundColor;

  _ProgressArcPainter({
    required this.progress,
    required this.strokeWidth,
    required this.color,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    // Background arc
    final backgroundPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, backgroundPaint);

    // Progress arc
    final progressPaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final sweepAngle = 2 * math.pi * progress;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2, // Start from top
      sweepAngle,
      false,
      progressPaint,
    );
  }

  @override
  bool shouldRepaint(_ProgressArcPainter oldDelegate) {
    return oldDelegate.progress != progress ||
        oldDelegate.color != color ||
        oldDelegate.backgroundColor != backgroundColor;
  }
}

/// Linear Download Progress - مؤشر تقدم خطي
class LinearDownloadProgress extends StatelessWidget {
  final double progress;
  final bool isPaused;
  final String? label;
  final bool showPercentage;

  const LinearDownloadProgress({
    super.key,
    required this.progress,
    this.isPaused = false,
    this.label,
    this.showPercentage = true,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = (progress * 100).round();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (label != null || showPercentage)
          Padding(
            padding: const EdgeInsets.only(bottom: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                if (label != null)
                  Text(
                    label!,
                    style: TextStyle(
                      color: Colors.grey[700],
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                if (showPercentage)
                  Text(
                    '$percentage%',
                    style: TextStyle(
                      color: isPaused ? Colors.grey : SahoolColors.primary,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
              ],
            ),
          ),

        // Progress bar
        ClipRRect(
          borderRadius: BorderRadius.circular(8),
          child: LinearProgressIndicator(
            value: progress,
            minHeight: 10,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation(
              isPaused ? Colors.grey : SahoolColors.primary,
            ),
          ),
        ),
      ],
    );
  }
}

/// Download Stats Card - بطاقة إحصائيات التحميل
class DownloadStatsCard extends StatelessWidget {
  final int totalTiles;
  final int downloadedTiles;
  final int skippedTiles;
  final int failedTiles;
  final Duration elapsed;
  final bool isPaused;

  const DownloadStatsCard({
    super.key,
    required this.totalTiles,
    required this.downloadedTiles,
    required this.skippedTiles,
    required this.failedTiles,
    required this.elapsed,
    this.isPaused = false,
  });

  @override
  Widget build(BuildContext context) {
    final processedTiles = downloadedTiles + skippedTiles + failedTiles;
    final progress = totalTiles > 0 ? processedTiles / totalTiles : 0.0;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Column(
        children: [
          // Progress bar
          LinearDownloadProgress(
            progress: progress,
            isPaused: isPaused,
            label: isPaused ? 'متوقف مؤقتاً' : 'جارٍ التحميل...',
          ),
          const SizedBox(height: 16),

          // Stats grid
          Row(
            children: [
              Expanded(
                child: _StatItem(
                  icon: Icons.grid_view,
                  label: 'الإجمالي',
                  value: '$totalTiles',
                  color: Colors.grey[700]!,
                ),
              ),
              Expanded(
                child: _StatItem(
                  icon: Icons.download_done,
                  label: 'تم تحميلها',
                  value: '$downloadedTiles',
                  color: SahoolColors.success,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _StatItem(
                  icon: Icons.skip_next,
                  label: 'تم تخطيها',
                  value: '$skippedTiles',
                  color: SahoolColors.info,
                ),
              ),
              Expanded(
                child: _StatItem(
                  icon: Icons.error_outline,
                  label: 'فشلت',
                  value: '$failedTiles',
                  color: SahoolColors.danger,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          _StatItem(
            icon: Icons.timer,
            label: 'الوقت المنقضي',
            value: _formatDuration(elapsed),
            color: Colors.grey[600]!,
            centered: true,
          ),
        ],
      ),
    );
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    final seconds = duration.inSeconds.remainder(60);

    if (hours > 0) {
      return '$hours:${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
    }
    return '${minutes.toString().padLeft(2, '0')}:${seconds.toString().padLeft(2, '0')}';
  }
}

/// Stat item widget - عنصر إحصائية
class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;
  final bool centered;

  const _StatItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
    this.centered = false,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment:
          centered ? MainAxisAlignment.center : MainAxisAlignment.start,
      children: [
        Icon(icon, size: 18, color: color),
        const SizedBox(width: 8),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
        const SizedBox(width: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}

/// Download Complete Badge - شارة اكتمال التحميل
class DownloadCompleteBadge extends StatelessWidget {
  final bool isSuccess;
  final double successRate;

  const DownloadCompleteBadge({
    super.key,
    required this.isSuccess,
    required this.successRate,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isSuccess
            ? SahoolColors.success.withValues(alpha: 0.1)
            : SahoolColors.warning.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSuccess ? Icons.check_circle : Icons.warning,
            color: isSuccess ? SahoolColors.success : SahoolColors.warning,
          ),
          const SizedBox(width: 12),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                isSuccess ? 'اكتمل التحميل' : 'اكتمل مع بعض الأخطاء',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color:
                      isSuccess ? SahoolColors.success : SahoolColors.warning,
                ),
              ),
              Text(
                'نسبة النجاح: ${(successRate * 100).toStringAsFixed(1)}%',
                style: TextStyle(
                  fontSize: 12,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
