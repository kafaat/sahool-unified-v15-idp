/// Pivot Dashboard Screen - Valley Style
/// شاشة لوحة تحكم المحوري - بأسلوب فالي
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/pivot_models.dart';
import '../providers/pivot_provider.dart';
import '../widgets/pivot_visualization.dart';
import '../widgets/pivot_control_panel.dart';
import 'sector_management_screen.dart';

/// Main pivot irrigation dashboard
/// لوحة تحكم الري المحوري الرئيسية
class PivotDashboardScreen extends ConsumerStatefulWidget {
  final String pivotId;
  final String? fieldId;

  const PivotDashboardScreen({
    super.key,
    required this.pivotId,
    this.fieldId,
  });

  @override
  ConsumerState<PivotDashboardScreen> createState() => _PivotDashboardScreenState();
}

class _PivotDashboardScreenState extends ConsumerState<PivotDashboardScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  bool _showNDVI = false;
  bool _showVRI = false;

  /// Local overrides applied on top of provider data (for commands & sector edits)
  PivotStatus? _statusOverride;
  PivotConfiguration? _configOverride;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  /// Helper to get pivot params for the provider
  PivotParams get _pivotParams =>
      PivotParams(pivotId: widget.pivotId, fieldId: widget.fieldId);

  @override
  Widget build(BuildContext context) {
    // Watch the provider - tries API first, falls back to demo data
    // يراقب المزود - يحاول API أولاً ثم يرجع للبيانات التجريبية
    final pivotAsync = ref.watch(pivotDataProvider(_pivotParams));

    return pivotAsync.when(
      loading: () => Directionality(
        textDirection: TextDirection.rtl,
        child: Scaffold(
          backgroundColor: const Color(0xFF367C2B),
          body: const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                CircularProgressIndicator(color: Colors.white),
                SizedBox(height: 16),
                Text('جاري تحميل بيانات المحوري...',
                    style: TextStyle(color: Colors.white, fontSize: 16)),
              ],
            ),
          ),
        ),
      ),
      error: (err, _) => Directionality(
        textDirection: TextDirection.rtl,
        child: Scaffold(
          body: Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Icon(Icons.error_outline, size: 64, color: Colors.red),
                const SizedBox(height: 16),
                Text('خطأ في تحميل البيانات: $err',
                    textAlign: TextAlign.center),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () =>
                      ref.refresh(pivotDataProvider(_pivotParams)),
                  child: const Text('إعادة المحاولة'),
                ),
              ],
            ),
          ),
        ),
      ),
      data: (pivotData) => _buildScreen(
        _configOverride ?? pivotData.config,
        _statusOverride ?? pivotData.status,
      ),
    );
  }

  Widget _buildScreen(PivotConfiguration pivotConfig, PivotStatus pivotStatus) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(pivotConfig.name),
              Text(
                '${pivotConfig.areaHectares.toStringAsFixed(1)} هكتار',
                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.normal),
              ),
            ],
          ),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            // NDVI toggle
            IconButton(
              icon: Icon(_showNDVI ? Icons.grass : Icons.grass_outlined),
              onPressed: () => setState(() => _showNDVI = !_showNDVI),
              tooltip: 'NDVI',
            ),
            // VRI toggle
            if (pivotConfig.hasVRI)
              IconButton(
                icon: Icon(_showVRI ? Icons.layers : Icons.layers_outlined),
                onPressed: () => setState(() => _showVRI = !_showVRI),
                tooltip: 'VRI',
              ),
            // Settings
            IconButton(
              icon: const Icon(Icons.settings),
              onPressed: () => _openSettings(),
              tooltip: 'الإعدادات',
            ),
          ],
          bottom: TabBar(
            controller: _tabController,
            indicatorColor: Colors.white,
            labelColor: Colors.white,
            unselectedLabelColor: Colors.white70,
            tabs: const [
              Tab(icon: Icon(Icons.dashboard), text: 'لوحة التحكم'),
              Tab(icon: Icon(Icons.pie_chart), text: 'القطاعات'),
              Tab(icon: Icon(Icons.schedule), text: 'الجدولة'),
              Tab(icon: Icon(Icons.analytics), text: 'الإحصائيات'),
            ],
          ),
        ),
        body: TabBarView(
          controller: _tabController,
          children: [
            _buildDashboardTab(pivotConfig, pivotStatus),
            _buildSectorsTab(pivotConfig, pivotStatus),
            _buildScheduleTab(pivotConfig, pivotStatus),
            _buildStatisticsTab(pivotConfig, pivotStatus),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardTab(PivotConfiguration pivotConfig, PivotStatus pivotStatus) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Pivot visualization
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'عرض المحوري | Pivot View',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                      Row(
                        children: [
                          _buildToggleChip('NDVI', _showNDVI, () {
                            setState(() => _showNDVI = !_showNDVI);
                          }),
                          const SizedBox(width: 8),
                          if (pivotConfig.hasVRI)
                            _buildToggleChip('VRI', _showVRI, () {
                              setState(() => _showVRI = !_showVRI);
                            }),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  PivotVisualization(
                    config: pivotConfig,
                    status: pivotStatus,
                    showNDVI: _showNDVI,
                    showVRIZones: _showVRI,
                    animate: true,
                    onSectorTap: (sector) => _showSectorDetails(sector),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Quick stats row
          _buildQuickStats(pivotStatus),

          const SizedBox(height: 16),

          // Control panel
          PivotControlPanel(
            config: pivotConfig,
            status: pivotStatus,
            onCommand: _handleCommand,
            isConnected: true,
          ),
        ],
      ),
    );
  }

  Widget _buildToggleChip(String label, bool isActive, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive ? Colors.green : Colors.grey[200],
          borderRadius: BorderRadius.circular(16),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isActive ? Colors.white : Colors.grey[600],
            fontSize: 12,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }

  Widget _buildQuickStats(PivotStatus pivotStatus) {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.speed,
            label: 'السرعة',
            value: '${pivotStatus.speedPercent.toInt()}%',
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            icon: Icons.location_on,
            label: 'الموقع',
            value: '${pivotStatus.currentAngle.toStringAsFixed(0)}°',
            color: Colors.orange,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            icon: Icons.water_drop,
            label: 'المياه',
            value: '${pivotStatus.waterAppliedM3.toStringAsFixed(0)} م³',
            color: Colors.cyan,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            icon: Icons.timer,
            label: 'المتبقي',
            value: _formatRemainingTime(pivotStatus),
            color: Colors.purple,
          ),
        ),
      ],
    );
  }

  String _formatRemainingTime(PivotStatus pivotStatus) {
    final remaining = pivotStatus.timerHours * 60 - pivotStatus.elapsedMinutes;
    if (remaining <= 0) return '0:00';
    final hours = (remaining / 60).floor();
    final mins = (remaining % 60).floor();
    return '$hours:${mins.toString().padLeft(2, '0')}';
  }

  Widget _buildSectorsTab(PivotConfiguration pivotConfig, PivotStatus pivotStatus) {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: pivotConfig.sectors.length,
      itemBuilder: (context, index) {
        final sector = pivotConfig.sectors[index];
        return _SectorTile(
          sector: sector,
          onTap: () => _showSectorDetails(sector),
          onToggle: (enabled) => _toggleSector(sector, enabled),
        );
      },
    );
  }

  Widget _buildScheduleTab(PivotConfiguration pivotConfig, PivotStatus pivotStatus) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.schedule, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'جدولة الري | Irrigation Schedule',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'قريباً...',
            style: TextStyle(color: Colors.grey[500]),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('جدولة الري المحوري - قريباً'),
                  duration: Duration(seconds: 2),
                ),
              );
            },
            icon: const Icon(Icons.add),
            label: const Text('إضافة جدول جديد'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF367C2B),
              foregroundColor: Colors.white,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatisticsTab(PivotConfiguration pivotConfig, PivotStatus pivotStatus) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Period selector
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: ['اليوم', 'الأسبوع', 'الشهر', 'الموسم']
                    .map((period) => ChoiceChip(
                          label: Text(period),
                          selected: period == 'الأسبوع',
                          onSelected: (selected) {},
                          selectedColor: const Color(0xFF367C2B),
                          labelStyle: TextStyle(
                            color: period == 'الأسبوع' ? Colors.white : Colors.black87,
                          ),
                        ))
                    .toList(),
              ),
            ),
          ),

          const SizedBox(height: 16),

          // Stats cards
          const Row(
            children: [
              Expanded(
                child: _BigStatCard(
                  icon: Icons.water_drop,
                  label: 'إجمالي المياه',
                  value: '12,500',
                  unit: 'م³',
                  color: Colors.blue,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _BigStatCard(
                  icon: Icons.bolt,
                  label: 'الطاقة المستهلكة',
                  value: '1,850',
                  unit: 'kWh',
                  color: Colors.orange,
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          const Row(
            children: [
              Expanded(
                child: _BigStatCard(
                  icon: Icons.timer,
                  label: 'ساعات التشغيل',
                  value: '168',
                  unit: 'ساعة',
                  color: Colors.green,
                ),
              ),
              SizedBox(width: 12),
              Expanded(
                child: _BigStatCard(
                  icon: Icons.loop,
                  label: 'الدورات الكاملة',
                  value: '14',
                  unit: 'دورة',
                  color: Colors.purple,
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Efficiency card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Row(
                    children: [
                      Icon(Icons.analytics, color: Color(0xFF367C2B)),
                      SizedBox(width: 8),
                      Text(
                        'كفاءة الري | Irrigation Efficiency',
                        style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      Expanded(
                        child: Column(
                          children: [
                            const Text('الكفاءة الحالية'),
                            const SizedBox(height: 8),
                            Stack(
                              alignment: Alignment.center,
                              children: [
                                SizedBox(
                                  width: 80,
                                  height: 80,
                                  child: CircularProgressIndicator(
                                    value: 0.87,
                                    strokeWidth: 8,
                                    backgroundColor: Colors.grey[200],
                                    valueColor: const AlwaysStoppedAnimation<Color>(
                                      Color(0xFF367C2B),
                                    ),
                                  ),
                                ),
                                const Text(
                                  '87%',
                                  style: TextStyle(
                                    fontSize: 20,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),
                      const Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _EfficiencyRow(
                              label: 'توزيع المياه',
                              value: 92,
                              color: Colors.blue,
                            ),
                            SizedBox(height: 8),
                            _EfficiencyRow(
                              label: 'استهلاك الطاقة',
                              value: 85,
                              color: Colors.orange,
                            ),
                            SizedBox(height: 8),
                            _EfficiencyRow(
                              label: 'وقت التشغيل',
                              value: 78,
                              color: Colors.green,
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _handleCommand(PivotControlCommand command) {
    // Send to API (fire-and-forget) then update local override for immediate feedback
    final repo = ref.read(pivotRepositoryProvider);
    repo.sendCommand(widget.pivotId, command);

    // Apply optimistic local state override
    final currentStatus = _statusOverride ??
        ref.read(pivotDataProvider(_pivotParams)).valueOrNull?.status;
    if (currentStatus == null) return;

    setState(() {
      switch (command.commandType) {
        case PivotCommandType.start:
        case PivotCommandType.resume:
          _statusOverride = currentStatus.copyWith(
            operatingStatus: PivotOperatingStatus.running,
          );
          break;
        case PivotCommandType.pause:
          _statusOverride = currentStatus.copyWith(
            operatingStatus: PivotOperatingStatus.paused,
          );
          break;
        case PivotCommandType.stop:
        case PivotCommandType.emergencyStop:
          _statusOverride = currentStatus.copyWith(
            operatingStatus: PivotOperatingStatus.stopped,
          );
          break;
        case PivotCommandType.setSpeed:
          _statusOverride = currentStatus.copyWith(
            speedPercent: command.speedPercent ?? currentStatus.speedPercent,
          );
          break;
        case PivotCommandType.setDirection:
          _statusOverride = currentStatus.copyWith(
            direction: command.direction ?? currentStatus.direction,
          );
          break;
        case PivotCommandType.toggleEndGun:
          _statusOverride = currentStatus.copyWith(
            endGunActive:
                command.endGunEnabled ?? !currentStatus.endGunActive,
          );
          break;
        default:
          break;
      }
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('تم تنفيذ الأمر: ${command.commandType.name}'),
        backgroundColor: const Color(0xFF367C2B),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  void _showSectorDetails(PivotSector sector) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => SectorDetailsSheet(
        sector: sector,
        onSave: (updatedSector) {
          // Update sector
          Navigator.pop(context);
        },
      ),
    );
  }

  void _toggleSector(PivotSector sector, bool enabled) {
    final currentConfig = _configOverride ??
        ref.read(pivotDataProvider(_pivotParams)).valueOrNull?.config;
    if (currentConfig == null) return;

    setState(() {
      final index =
          currentConfig.sectors.indexWhere((s) => s.id == sector.id);
      if (index != -1) {
        final updatedSectors =
            List<PivotSector>.from(currentConfig.sectors);
        updatedSectors[index] = sector.copyWith(isEnabled: enabled);
        _configOverride = currentConfig.copyWith(sectors: updatedSectors);
      }
    });
  }

  void _openSettings() {
    final currentConfig = _configOverride ??
        ref.read(pivotDataProvider(_pivotParams)).valueOrNull?.config;
    if (currentConfig == null) return;

    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SectorManagementScreen(
          pivotConfig: currentConfig,
          onConfigUpdate: (config) {
            setState(() => _configOverride = config);
          },
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════

class _StatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _StatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          children: [
            Icon(icon, color: color, size: 24),
            const SizedBox(height: 4),
            Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
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
      ),
    );
  }
}

class _BigStatCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final String unit;
  final Color color;

  const _BigStatCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.unit,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(icon, color: color, size: 20),
                ),
                const SizedBox(width: 8),
                Text(
                  label,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 12,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  value,
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 4),
                Text(
                  unit,
                  style: TextStyle(
                    color: Colors.grey[600],
                    fontSize: 14,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _SectorTile extends StatelessWidget {
  final PivotSector sector;
  final VoidCallback onTap;
  final Function(bool) onToggle;

  const _SectorTile({
    required this.sector,
    required this.onTap,
    required this.onToggle,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: _hexToColor(sector.color),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Center(
            child: Text(
              '${sector.sectorNumber}',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ),
        title: Text(sector.nameAr.isNotEmpty ? sector.nameAr : 'قطاع ${sector.sectorNumber}'),
        subtitle: Row(
          children: [
            Text('${sector.startAngle.toInt()}° - ${sector.endAngle.toInt()}°'),
            const SizedBox(width: 8),
            if (sector.ndviValue != null)
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: _ndviColor(sector.ndviValue!).withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'NDVI: ${sector.ndviValue!.toStringAsFixed(2)}',
                  style: TextStyle(
                    fontSize: 10,
                    color: _ndviColor(sector.ndviValue!),
                  ),
                ),
              ),
          ],
        ),
        trailing: Switch(
          value: sector.isEnabled,
          onChanged: onToggle,
          activeColor: const Color(0xFF367C2B),
        ),
        onTap: onTap,
      ),
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }

  Color _ndviColor(double ndvi) {
    if (ndvi < 0.3) return Colors.red;
    if (ndvi < 0.5) return Colors.orange;
    if (ndvi < 0.7) return Colors.yellow[700]!;
    return Colors.green;
  }
}

class _EfficiencyRow extends StatelessWidget {
  final String label;
  final int value;
  final Color color;

  const _EfficiencyRow({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(
            label,
            style: const TextStyle(fontSize: 12),
          ),
        ),
        const SizedBox(width: 8),
        SizedBox(
          width: 60,
          child: LinearProgressIndicator(
            value: value / 100,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation<Color>(color),
          ),
        ),
        const SizedBox(width: 8),
        Text(
          '$value%',
          style: TextStyle(
            fontSize: 12,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}

/// Sector details bottom sheet
class SectorDetailsSheet extends StatefulWidget {
  final PivotSector sector;
  final Function(PivotSector) onSave;

  const SectorDetailsSheet({
    super.key,
    required this.sector,
    required this.onSave,
  });

  @override
  State<SectorDetailsSheet> createState() => _SectorDetailsSheetState();
}

class _SectorDetailsSheetState extends State<SectorDetailsSheet> {
  late double _speedPercent;
  late double _irrigationDepth;

  @override
  void initState() {
    super.initState();
    _speedPercent = widget.sector.speedPercent;
    _irrigationDepth = widget.sector.irrigationDepthMm;
  }

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.6,
      minChildSize: 0.4,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: SingleChildScrollView(
            controller: scrollController,
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Handle bar
                Center(
                  child: Container(
                    width: 40,
                    height: 4,
                    decoration: BoxDecoration(
                      color: Colors.grey[300],
                      borderRadius: BorderRadius.circular(2),
                    ),
                  ),
                ),
                const SizedBox(height: 20),

                // Header
                Row(
                  children: [
                    Container(
                      width: 50,
                      height: 50,
                      decoration: BoxDecoration(
                        color: _hexToColor(widget.sector.color),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Center(
                        child: Text(
                          '${widget.sector.sectorNumber}',
                          style: const TextStyle(
                            color: Colors.white,
                            fontWeight: FontWeight.bold,
                            fontSize: 20,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'قطاع ${widget.sector.sectorNumber}',
                            style: const TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          Text(
                            '${widget.sector.startAngle.toInt()}° - ${widget.sector.endAngle.toInt()}°',
                            style: TextStyle(color: Colors.grey[600]),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                const Divider(height: 32),

                // NDVI & Soil Moisture
                if (widget.sector.ndviValue != null ||
                    widget.sector.soilMoisturePercent != null)
                  Row(
                    children: [
                      if (widget.sector.ndviValue != null)
                        Expanded(
                          child: _InfoCard(
                            icon: Icons.grass,
                            label: 'NDVI',
                            value: widget.sector.ndviValue!.toStringAsFixed(2),
                            color: _ndviColor(widget.sector.ndviValue!),
                          ),
                        ),
                      if (widget.sector.ndviValue != null &&
                          widget.sector.soilMoisturePercent != null)
                        const SizedBox(width: 12),
                      if (widget.sector.soilMoisturePercent != null)
                        Expanded(
                          child: _InfoCard(
                            icon: Icons.water_drop,
                            label: 'رطوبة التربة',
                            value: '${widget.sector.soilMoisturePercent!.toInt()}%',
                            color: Colors.blue,
                          ),
                        ),
                    ],
                  ),

                const SizedBox(height: 20),

                // Speed control
                Text(
                  'سرعة القطاع | Sector Speed',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: Slider(
                        value: _speedPercent,
                        min: 50,
                        max: 100,
                        divisions: 10,
                        label: '${_speedPercent.toInt()}%',
                        onChanged: (value) {
                          setState(() => _speedPercent = value);
                        },
                        activeColor: const Color(0xFF367C2B),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: const Color(0xFF367C2B).withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${_speedPercent.toInt()}%',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF367C2B),
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 20),

                // Irrigation depth
                Text(
                  'عمق الري | Irrigation Depth',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.grey[700],
                  ),
                ),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: Slider(
                        value: _irrigationDepth,
                        min: 10,
                        max: 50,
                        divisions: 8,
                        label: '${_irrigationDepth.toInt()} mm',
                        onChanged: (value) {
                          setState(() => _irrigationDepth = value);
                        },
                        activeColor: Colors.blue,
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: Colors.blue.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${_irrigationDepth.toInt()} mm',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.blue,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 24),

                // Save button
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () {
                      widget.onSave(widget.sector.copyWith(
                        speedPercent: _speedPercent,
                        irrigationDepthMm: _irrigationDepth,
                      ));
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF367C2B),
                      foregroundColor: Colors.white,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    child: const Text(
                      'حفظ التغييرات | Save Changes',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }

  Color _ndviColor(double ndvi) {
    if (ndvi < 0.3) return Colors.red;
    if (ndvi < 0.5) return Colors.orange;
    if (ndvi < 0.7) return Colors.yellow[700]!;
    return Colors.green;
  }
}

class _InfoCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _InfoCard({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color),
          const SizedBox(height: 8),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
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
      ),
    );
  }
}
