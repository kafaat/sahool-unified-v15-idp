import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'memory_manager.dart';
import 'metrics_collector.dart';
import 'performance_monitor.dart';
import 'api_tracker.dart';

/// SAHOOL Performance Overlay (Debug Only)
/// لوحة مراقبة الأداء (للتطوير فقط)
///
/// Features:
/// - Real-time FPS display
/// - Memory usage indicator
/// - API response times
/// - Screen transition times
/// - Expandable detailed view
///
/// Only visible in debug/profile mode.
///
/// Usage:
/// ```dart
/// MaterialApp(
///   builder: (context, child) {
///     return PerformanceOverlay(
///       child: child!,
///       enabled: kDebugMode,
///     );
///   },
/// )
/// ```

class PerformanceOverlay extends StatefulWidget {
  final Widget child;
  final bool enabled;
  final PerformanceOverlayPosition position;
  final ApiTimingTracker? apiTracker;

  const PerformanceOverlay({
    super.key,
    required this.child,
    this.enabled = true,
    this.position = PerformanceOverlayPosition.topRight,
    this.apiTracker,
  });

  @override
  State<PerformanceOverlay> createState() => _PerformanceOverlayState();
}

enum PerformanceOverlayPosition {
  topLeft,
  topRight,
  bottomLeft,
  bottomRight,
}

class _PerformanceOverlayState extends State<PerformanceOverlay> {
  bool _expanded = false;
  Timer? _refreshTimer;

  // Cached values for display
  double _fps = 60;
  MemoryInfo? _memoryInfo;
  ApiRecentStats? _apiStats;
  StartupMetrics? _startupMetrics;

  @override
  void initState() {
    super.initState();
    if (widget.enabled && !kReleaseMode) {
      _startRefreshTimer();
      _fetchInitialData();
    }
  }

  void _fetchInitialData() {
    _startupMetrics = PerformanceMonitor.instance.getStartupMetrics();
  }

  void _startRefreshTimer() {
    _refreshTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;

      setState(() {
        _fps = PerformanceMonitor.instance.currentFps;
        _memoryInfo = MemoryManager.instance.getMemoryInfo();
        _apiStats = widget.apiTracker?.getRecentStats();
      });
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    // Only show in debug/profile mode
    if (!widget.enabled || kReleaseMode) {
      return widget.child;
    }

    return Stack(
      children: [
        widget.child,
        Positioned(
          top: _position.top,
          bottom: _position.bottom,
          left: _position.left,
          right: _position.right,
          child: SafeArea(
            child: _expanded
                ? _buildExpandedOverlay()
                : _buildCompactOverlay(),
          ),
        ),
      ],
    );
  }

  ({double? top, double? bottom, double? left, double? right}) get _position {
    switch (widget.position) {
      case PerformanceOverlayPosition.topLeft:
        return (top: 8.0, bottom: null, left: 8.0, right: null);
      case PerformanceOverlayPosition.topRight:
        return (top: 8.0, bottom: null, left: null, right: 8.0);
      case PerformanceOverlayPosition.bottomLeft:
        return (top: null, bottom: 8.0, left: 8.0, right: null);
      case PerformanceOverlayPosition.bottomRight:
        return (top: null, bottom: 8.0, left: null, right: 8.0);
    }
  }

  Widget _buildCompactOverlay() {
    final fpsColor = _getFpsColor(_fps);

    return GestureDetector(
      onTap: () => setState(() => _expanded = true),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.7),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.speed, size: 14, color: fpsColor),
            const SizedBox(width: 4),
            Text(
              '${_fps.toStringAsFixed(0)} FPS',
              style: TextStyle(
                color: fpsColor,
                fontSize: 12,
                fontWeight: FontWeight.bold,
                fontFamily: 'monospace',
              ),
            ),
            if (_memoryInfo != null) ...[
              const SizedBox(width: 8),
              Text(
                _memoryInfo!.imageCacheSizeFormatted,
                style: const TextStyle(
                  color: Colors.white70,
                  fontSize: 10,
                  fontFamily: 'monospace',
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildExpandedOverlay() {
    return GestureDetector(
      onTap: () => setState(() => _expanded = false),
      child: Container(
        width: 280,
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.black.withValues(alpha: 0.85),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: Colors.white24),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildHeader(),
            const Divider(color: Colors.white24, height: 16),
            _buildFpsSection(),
            const SizedBox(height: 8),
            _buildMemorySection(),
            if (_apiStats != null) ...[
              const SizedBox(height: 8),
              _buildApiSection(),
            ],
            if (_startupMetrics != null) ...[
              const SizedBox(height: 8),
              _buildStartupSection(),
            ],
            const Divider(color: Colors.white24, height: 16),
            _buildActions(),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      children: [
        const Icon(Icons.analytics, color: Colors.white, size: 18),
        const SizedBox(width: 8),
        const Text(
          'Performance Monitor',
          style: TextStyle(
            color: Colors.white,
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
        const Spacer(),
        GestureDetector(
          onTap: () => setState(() => _expanded = false),
          child: const Icon(Icons.close, color: Colors.white54, size: 18),
        ),
      ],
    );
  }

  Widget _buildFpsSection() {
    final stats = PerformanceMonitor.instance.getFrameRateStats();
    final fpsColor = _getFpsColor(_fps);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Frame Rate',
          style: TextStyle(color: Colors.white70, fontSize: 10),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            _buildMetricBox(
              _fps.toStringAsFixed(0),
              'FPS',
              fpsColor,
            ),
            const SizedBox(width: 8),
            _buildMetricBox(
              '${stats.averageFrameTime.inMilliseconds}',
              'ms/frame',
              Colors.white,
            ),
            const SizedBox(width: 8),
            _buildMetricBox(
              '${stats.droppedFrames}',
              'dropped',
              stats.droppedFrames > 10 ? Colors.orange : Colors.white,
            ),
          ],
        ),
        const SizedBox(height: 4),
        _buildProgressBar(
          value: (_fps / 60).clamp(0, 1),
          color: fpsColor,
        ),
      ],
    );
  }

  Widget _buildMemorySection() {
    if (_memoryInfo == null) return const SizedBox.shrink();

    final usage = _memoryInfo!.imageCacheUsagePercent / 100;
    final usageColor = usage > 0.8
        ? Colors.red
        : usage > 0.5
            ? Colors.orange
            : Colors.green;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Memory (Image Cache)',
          style: TextStyle(color: Colors.white70, fontSize: 10),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            _buildMetricBox(
              _memoryInfo!.imageCacheSizeFormatted,
              'used',
              usageColor,
            ),
            const SizedBox(width: 8),
            _buildMetricBox(
              '${_memoryInfo!.imageCacheCount}',
              'images',
              Colors.white,
            ),
            const SizedBox(width: 8),
            _buildMetricBox(
              '${_memoryInfo!.imageCacheUsagePercent.toStringAsFixed(0)}%',
              'usage',
              usageColor,
            ),
          ],
        ),
        const SizedBox(height: 4),
        _buildProgressBar(
          value: usage,
          color: usageColor,
        ),
      ],
    );
  }

  Widget _buildApiSection() {
    final stats = _apiStats!;
    final errorColor = stats.errorRate > 0.1
        ? Colors.red
        : stats.errorRate > 0
            ? Colors.orange
            : Colors.green;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'API Performance (Recent)',
          style: TextStyle(color: Colors.white70, fontSize: 10),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            _buildMetricBox(
              '${stats.averageDurationMs}',
              'avg ms',
              stats.averageDurationMs > 1000 ? Colors.orange : Colors.white,
            ),
            const SizedBox(width: 8),
            _buildMetricBox(
              '${stats.p95DurationMs}',
              'p95 ms',
              stats.p95DurationMs > 2000 ? Colors.orange : Colors.white,
            ),
            const SizedBox(width: 8),
            _buildMetricBox(
              '${stats.errorCount}',
              'errors',
              errorColor,
            ),
          ],
        ),
        if (stats.totalRequests > 0) ...[
          const SizedBox(height: 4),
          Text(
            '${stats.totalRequests} requests, ${(stats.errorRate * 100).toStringAsFixed(1)}% error rate',
            style: const TextStyle(color: Colors.white54, fontSize: 10),
          ),
        ],
      ],
    );
  }

  Widget _buildStartupSection() {
    if (_startupMetrics == null) return const SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Startup Performance',
          style: TextStyle(color: Colors.white70, fontSize: 10),
        ),
        const SizedBox(height: 4),
        Row(
          children: [
            if (_startupMetrics!.timeToFirstFrame != null)
              _buildMetricBox(
                '${_startupMetrics!.timeToFirstFrame!.inMilliseconds}',
                'first frame',
                Colors.white,
              ),
            if (_startupMetrics!.timeToStartupComplete != null) ...[
              const SizedBox(width: 8),
              _buildMetricBox(
                '${_startupMetrics!.timeToStartupComplete!.inMilliseconds}',
                'ready',
                _startupMetrics!.timeToStartupComplete!.inMilliseconds > 3000
                    ? Colors.orange
                    : Colors.green,
              ),
            ],
          ],
        ),
      ],
    );
  }

  Widget _buildMetricBox(String value, String label, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          value,
          style: TextStyle(
            color: color,
            fontSize: 16,
            fontWeight: FontWeight.bold,
            fontFamily: 'monospace',
          ),
        ),
        Text(
          label,
          style: const TextStyle(
            color: Colors.white54,
            fontSize: 9,
          ),
        ),
      ],
    );
  }

  Widget _buildProgressBar({required double value, required Color color}) {
    return Container(
      height: 4,
      decoration: BoxDecoration(
        color: Colors.white12,
        borderRadius: BorderRadius.circular(2),
      ),
      child: FractionallySizedBox(
        alignment: Alignment.centerLeft,
        widthFactor: value.clamp(0, 1),
        child: Container(
          decoration: BoxDecoration(
            color: color,
            borderRadius: BorderRadius.circular(2),
          ),
        ),
      ),
    );
  }

  Widget _buildActions() {
    return Row(
      children: [
        _buildActionButton(
          icon: Icons.cleaning_services,
          label: 'Clear Cache',
          onTap: () {
            MemoryManager.instance.clearMemory();
            setState(() {
              _memoryInfo = MemoryManager.instance.getMemoryInfo();
            });
          },
        ),
        const SizedBox(width: 8),
        _buildActionButton(
          icon: Icons.refresh,
          label: 'Refresh',
          onTap: () {
            setState(() {
              _fps = PerformanceMonitor.instance.currentFps;
              _memoryInfo = MemoryManager.instance.getMemoryInfo();
              _apiStats = widget.apiTracker?.getRecentStats();
            });
          },
        ),
        const SizedBox(width: 8),
        _buildActionButton(
          icon: Icons.bug_report,
          label: 'Export',
          onTap: _showExportDialog,
        ),
      ],
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.white12,
          borderRadius: BorderRadius.circular(4),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 12, color: Colors.white70),
            const SizedBox(width: 4),
            Text(
              label,
              style: const TextStyle(color: Colors.white70, fontSize: 10),
            ),
          ],
        ),
      ),
    );
  }

  void _showExportDialog() {
    final summary = PerformanceMonitor.instance.getSummary();
    final metricsJson = PerformanceMonitor.instance.metricsCollector.exportAsJson();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Performance Data'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('Frame Rate: ${summary.frameRateStats}'),
              const SizedBox(height: 8),
              Text('Memory: ${summary.memoryInfo}'),
              const SizedBox(height: 8),
              Text('Startup: ${summary.startupMetrics}'),
              const SizedBox(height: 16),
              const Text(
                'Full metrics exported to debug console.',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              debugPrint('=== SAHOOL Performance Metrics ===');
              debugPrint(metricsJson);
              debugPrint('=== End Metrics ===');
              Navigator.of(context).pop();
            },
            child: const Text('Export to Console'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }

  Color _getFpsColor(double fps) {
    if (fps >= 55) return Colors.green;
    if (fps >= 45) return Colors.orange;
    return Colors.red;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Performance Dashboard (Full Screen)
// ═══════════════════════════════════════════════════════════════════════════

/// Full-screen performance dashboard for detailed analysis
class PerformanceDashboard extends StatefulWidget {
  final ApiTimingTracker? apiTracker;

  const PerformanceDashboard({
    super.key,
    this.apiTracker,
  });

  @override
  State<PerformanceDashboard> createState() => _PerformanceDashboardState();
}

class _PerformanceDashboardState extends State<PerformanceDashboard> {
  Timer? _refreshTimer;
  PerformanceSummary? _summary;
  Map<String, MetricStats> _apiStats = {};
  Map<String, MetricStats> _dbStats = {};

  @override
  void initState() {
    super.initState();
    _refresh();
    _refreshTimer = Timer.periodic(const Duration(seconds: 2), (_) => _refresh());
  }

  void _refresh() {
    if (!mounted) return;
    setState(() {
      _summary = PerformanceMonitor.instance.getSummary();
      _apiStats = PerformanceMonitor.instance.metricsCollector.getApiStats();
      _dbStats = PerformanceMonitor.instance.metricsCollector.getDatabaseStats();
    });
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (kReleaseMode) {
      return const Scaffold(
        body: Center(
          child: Text('Performance Dashboard is only available in debug mode'),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Performance Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
          ),
          IconButton(
            icon: const Icon(Icons.cleaning_services),
            onPressed: () {
              MemoryManager.instance.clearMemory(aggressive: true);
              _refresh();
            },
          ),
        ],
      ),
      body: _summary == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () async => _refresh(),
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  _buildSectionCard(
                    title: 'Startup Performance',
                    icon: Icons.rocket_launch,
                    child: _buildStartupContent(),
                  ),
                  const SizedBox(height: 16),
                  _buildSectionCard(
                    title: 'Frame Rate',
                    icon: Icons.speed,
                    child: _buildFrameRateContent(),
                  ),
                  const SizedBox(height: 16),
                  _buildSectionCard(
                    title: 'Memory Usage',
                    icon: Icons.memory,
                    child: _buildMemoryContent(),
                  ),
                  const SizedBox(height: 16),
                  _buildSectionCard(
                    title: 'API Performance',
                    icon: Icons.api,
                    child: _buildApiContent(),
                  ),
                  const SizedBox(height: 16),
                  _buildSectionCard(
                    title: 'Database Queries',
                    icon: Icons.storage,
                    child: _buildDatabaseContent(),
                  ),
                  const SizedBox(height: 16),
                  _buildSectionCard(
                    title: 'Screen Transitions',
                    icon: Icons.swap_horiz,
                    child: _buildScreenTransitionsContent(),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildSectionCard({
    required String title,
    required IconData icon,
    required Widget child,
  }) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, size: 20),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const Divider(),
            child,
          ],
        ),
      ),
    );
  }

  Widget _buildStartupContent() {
    final startup = _summary?.startupMetrics;
    if (startup == null) {
      return const Text('No startup data available');
    }

    return Column(
      children: [
        _buildMetricRow(
          'Time to First Frame',
          '${startup.timeToFirstFrame?.inMilliseconds ?? "N/A"} ms',
        ),
        _buildMetricRow(
          'Time to Ready',
          '${startup.timeToStartupComplete?.inMilliseconds ?? "N/A"} ms',
        ),
      ],
    );
  }

  Widget _buildFrameRateContent() {
    final fps = _summary!.frameRateStats;
    return Column(
      children: [
        _buildMetricRow('Current FPS', fps.currentFps.toStringAsFixed(1)),
        _buildMetricRow('Avg Frame Time', '${fps.averageFrameTime.inMilliseconds} ms'),
        _buildMetricRow('Dropped Frames', '${fps.droppedFrames} / ${fps.totalFrames}'),
        _buildMetricRow(
          'Drop Rate',
          '${(fps.droppedFrameRatio * 100).toStringAsFixed(1)}%',
        ),
      ],
    );
  }

  Widget _buildMemoryContent() {
    final mem = _summary!.memoryInfo;
    return Column(
      children: [
        _buildMetricRow('Image Cache Size', mem.imageCacheSizeFormatted),
        _buildMetricRow('Cached Images', '${mem.imageCacheCount}'),
        _buildMetricRow(
          'Cache Usage',
          '${mem.imageCacheUsagePercent.toStringAsFixed(1)}%',
        ),
      ],
    );
  }

  Widget _buildApiContent() {
    if (_apiStats.isEmpty) {
      return const Text('No API metrics collected yet');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _apiStats.entries.take(10).map((entry) {
        final stats = entry.value;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                entry.key,
                style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 12),
              ),
              Row(
                children: [
                  _buildSmallStat('avg', '${stats.average.toStringAsFixed(0)}ms'),
                  _buildSmallStat('p95', '${stats.p95.toStringAsFixed(0)}ms'),
                  _buildSmallStat('count', '${stats.count}'),
                ],
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildDatabaseContent() {
    if (_dbStats.isEmpty) {
      return const Text('No database metrics collected yet');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: _dbStats.entries.take(10).map((entry) {
        final stats = entry.value;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 4),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  entry.key,
                  style: const TextStyle(fontSize: 12),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Text(
                '${stats.average.toStringAsFixed(1)}ms (${stats.count}x)',
                style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
              ),
            ],
          ),
        );
      }).toList(),
    );
  }

  Widget _buildScreenTransitionsContent() {
    final transitions = _summary!.screenTransitions;
    if (transitions.isEmpty) {
      return const Text('No screen transitions recorded');
    }

    return Column(
      children: transitions.entries.map((entry) {
        return _buildMetricRow(
          entry.key,
          '${entry.value.inMilliseconds} ms',
        );
      }).toList(),
    );
  }

  Widget _buildMetricRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.w500,
              fontFamily: 'monospace',
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSmallStat(String label, String value) {
    return Container(
      margin: const EdgeInsets.only(right: 12),
      child: Row(
        children: [
          Text(
            '$label: ',
            style: const TextStyle(fontSize: 10, color: Colors.grey),
          ),
          Text(
            value,
            style: const TextStyle(fontSize: 10, fontFamily: 'monospace'),
          ),
        ],
      ),
    );
  }
}
