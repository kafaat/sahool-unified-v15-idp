import 'dart:async';
import 'package:flutter/material.dart';

import '../../../../core/maps/offline/region_manager.dart';
import '../../../../core/maps/offline/tile_downloader.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../widgets/download_progress_indicator.dart';

/// Download Progress Screen - شاشة تقدم التحميل
///
/// Features:
/// - Real-time progress display - عرض التقدم في الوقت الفعلي
/// - Pause/Resume support - دعم الإيقاف والاستمرار
/// - Cancel option - خيار الإلغاء
/// - Download statistics - إحصائيات التحميل
class DownloadProgressScreen extends StatefulWidget {
  final RegionManager regionManager;
  final MapRegion region;
  final int minZoom;
  final int maxZoom;
  final VoidCallback? onComplete;

  const DownloadProgressScreen({
    super.key,
    required this.regionManager,
    required this.region,
    required this.minZoom,
    required this.maxZoom,
    this.onComplete,
  });

  @override
  State<DownloadProgressScreen> createState() => _DownloadProgressScreenState();
}

class _DownloadProgressScreenState extends State<DownloadProgressScreen>
    with TickerProviderStateMixin {
  DownloadProgress? _progress;
  DownloadResult? _result;
  bool _isPaused = false;
  bool _isCancelled = false;
  StreamSubscription<DownloadProgress>? _progressSubscription;
  late AnimationController _pulseController;
  DateTime? _startTime;
  Duration _elapsed = Duration.zero;
  Timer? _elapsedTimer;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1500),
    )..repeat(reverse: true);

    _startDownload();
  }

  @override
  void dispose() {
    _progressSubscription?.cancel();
    _pulseController.dispose();
    _elapsedTimer?.cancel();
    super.dispose();
  }

  void _startDownload() {
    setState(() {
      _startTime = DateTime.now();
      _elapsed = Duration.zero;
    });

    // Start elapsed timer
    _elapsedTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!_isPaused && mounted) {
        setState(() {
          _elapsed = DateTime.now().difference(_startTime!);
        });
      }
    });

    // Subscribe to progress updates
    _progressSubscription =
        widget.regionManager.downloadProgressStream.listen((progress) {
      if (mounted) {
        setState(() {
          _progress = progress;
        });
      }
    });

    // Start the download
    widget.regionManager
        .downloadRegion(
      region: widget.region,
      minZoom: widget.minZoom,
      maxZoom: widget.maxZoom,
      onProgress: (progress) {
        // Progress is also handled via stream
      },
    )
        .then((result) {
      if (mounted) {
        setState(() {
          _result = result;
        });
        _elapsedTimer?.cancel();

        if (result.isSuccess && !result.cancelled) {
          widget.onComplete?.call();
        }
      }
    });
  }

  void _togglePause() {
    setState(() {
      _isPaused = !_isPaused;
    });

    if (_isPaused) {
      widget.regionManager.pauseDownload();
    } else {
      widget.regionManager.resumeDownload();
    }
  }

  Future<void> _cancelDownload() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إلغاء التحميل'),
        content: const Text(
          'هل أنت متأكد من إلغاء التحميل؟\n'
          'سيتم حذف البيانات التي تم تحميلها.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('لا'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.danger,
            ),
            child: const Text('نعم، إلغاء'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      widget.regionManager.cancelDownload();
      setState(() {
        _isCancelled = true;
      });
      if (mounted) {
        Navigator.pop(context);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: _result != null,
      onPopInvokedWithResult: (didPop, result) {
        if (!didPop && _result == null) {
          _showExitConfirmation();
        }
      },
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            _result != null ? 'اكتمل التحميل' : 'جارٍ التحميل',
          ),
          centerTitle: true,
          automaticallyImplyLeading: _result != null,
          leading: _result == null
              ? IconButton(
                  icon: const Icon(Icons.close),
                  onPressed: _cancelDownload,
                )
              : null,
        ),
        body: SafeArea(
          child: _result != null ? _buildResultView() : _buildProgressView(),
        ),
      ),
    );
  }

  Widget _buildProgressView() {
    final progress = _progress;
    final progressPercent =
        progress != null ? (progress.progress * 100).round() : 0;

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const Spacer(),

          // Region info
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: SahoolColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.map,
                    color: SahoolColors.primary,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        widget.region.nameAr,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 18,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        widget.region.nameEn,
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'تكبير ${widget.minZoom}-${widget.maxZoom}',
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 40),

          // Progress indicator
          AnimatedBuilder(
            animation: _pulseController,
            builder: (context, child) {
              return DownloadProgressIndicator(
                progress: progress?.progress ?? 0.0,
                isPaused: _isPaused,
                pulseValue: _pulseController.value,
              );
            },
          ),
          const SizedBox(height: 32),

          // Progress percentage
          Text(
            '$progressPercent%',
            style: const TextStyle(
              fontSize: 48,
              fontWeight: FontWeight.bold,
              color: SahoolColors.primary,
            ),
          ),
          const SizedBox(height: 8),

          // Status text
          Text(
            _isPaused
                ? 'متوقف مؤقتاً'
                : progress != null
                    ? 'جارٍ تحميل البلاطات...'
                    : 'جارٍ التحضير...',
            style: TextStyle(
              fontSize: 16,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 32),

          // Statistics
          if (progress != null)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                children: [
                  _buildStatRow(
                    'البلاطات',
                    '${progress.processedTiles} / ${progress.totalTiles}',
                    Icons.grid_view,
                  ),
                  const Divider(),
                  _buildStatRow(
                    'المُحملة',
                    '${progress.downloadedTiles}',
                    Icons.download_done,
                    color: SahoolColors.success,
                  ),
                  const Divider(),
                  _buildStatRow(
                    'موجودة مسبقاً',
                    '${progress.skippedTiles}',
                    Icons.skip_next,
                    color: SahoolColors.info,
                  ),
                  const Divider(),
                  _buildStatRow(
                    'فشلت',
                    '${progress.failedTiles}',
                    Icons.error_outline,
                    color: SahoolColors.danger,
                  ),
                  const Divider(),
                  _buildStatRow(
                    'الوقت المنقضي',
                    _formatDuration(_elapsed),
                    Icons.timer,
                  ),
                ],
              ),
            ),

          const Spacer(),

          // Control buttons
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _togglePause,
                  icon: Icon(_isPaused ? Icons.play_arrow : Icons.pause),
                  label: Text(_isPaused ? 'استمرار' : 'إيقاف'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _cancelDownload,
                  icon: const Icon(Icons.cancel),
                  label: const Text('إلغاء'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: SahoolColors.danger,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildResultView() {
    final result = _result!;
    final isSuccess = result.isSuccess;

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const Spacer(),

          // Result icon
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: (isSuccess ? SahoolColors.success : SahoolColors.warning)
                  .withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              isSuccess ? Icons.check_circle : Icons.warning,
              size: 80,
              color: isSuccess ? SahoolColors.success : SahoolColors.warning,
            ),
          ),
          const SizedBox(height: 24),

          // Result title
          Text(
            isSuccess ? 'تم التحميل بنجاح!' : 'تم التحميل مع بعض الأخطاء',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),

          // Region name
          Text(
            widget.region.nameAr,
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 32),

          // Statistics
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                _buildResultStatRow(
                  'إجمالي البلاطات',
                  '${result.totalTiles}',
                  Icons.grid_view,
                ),
                const SizedBox(height: 12),
                _buildResultStatRow(
                  'تم تحميلها',
                  '${result.downloaded}',
                  Icons.download_done,
                  color: SahoolColors.success,
                ),
                const SizedBox(height: 12),
                _buildResultStatRow(
                  'موجودة مسبقاً',
                  '${result.skipped}',
                  Icons.skip_next,
                  color: SahoolColors.info,
                ),
                if (result.failed > 0) ...[
                  const SizedBox(height: 12),
                  _buildResultStatRow(
                    'فشلت',
                    '${result.failed}',
                    Icons.error_outline,
                    color: SahoolColors.danger,
                  ),
                ],
                const SizedBox(height: 12),
                _buildResultStatRow(
                  'نسبة النجاح',
                  '${(result.successRate * 100).toStringAsFixed(1)}%',
                  Icons.analytics,
                  color: isSuccess ? SahoolColors.success : SahoolColors.warning,
                ),
                const SizedBox(height: 12),
                _buildResultStatRow(
                  'الوقت الإجمالي',
                  _formatDuration(_elapsed),
                  Icons.timer,
                ),
              ],
            ),
          ),

          const Spacer(),

          // Done button
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: () {
                Navigator.pop(context);
              },
              icon: const Icon(Icons.check),
              label: const Text('تم'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatRow(String label, String value, IconData icon,
      {Color? color}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Icon(icon, size: 18, color: color ?? Colors.grey[600]),
          const SizedBox(width: 8),
          Text(
            label,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const Spacer(),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildResultStatRow(String label, String value, IconData icon,
      {Color? color}) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: (color ?? Colors.grey).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(icon, size: 20, color: color ?? Colors.grey[600]),
        ),
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
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            color: color,
          ),
        ),
      ],
    );
  }

  String _formatDuration(Duration duration) {
    final hours = duration.inHours;
    final minutes = duration.inMinutes.remainder(60);
    final seconds = duration.inSeconds.remainder(60);

    if (hours > 0) {
      return '$hoursس $minutesد $secondsث';
    } else if (minutes > 0) {
      return '$minutesد $secondsث';
    } else {
      return '$secondsث';
    }
  }

  Future<void> _showExitConfirmation() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إلغاء التحميل'),
        content: const Text(
          'التحميل لم يكتمل بعد. هل تريد الإلغاء؟',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('لا، استمر'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context, true),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.danger,
            ),
            child: const Text('نعم، إلغاء'),
          ),
        ],
      ),
    );

    if (confirmed == true && mounted) {
      widget.regionManager.cancelDownload();
      Navigator.pop(context);
    }
  }
}
