/// Pivot Dashboard Screen - Valley Style
/// شاشة لوحة تحكم المحوري - بأسلوب فالي
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/models/pivot_models.dart';
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

  // Demo data - في الإنتاج تأتي من API
  late PivotConfiguration _pivotConfig;
  late PivotStatus _pivotStatus;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 4, vsync: this);
    _loadDemoData();
  }

  void _loadDemoData() {
    // Demo pivot configuration
    _pivotConfig = PivotConfiguration(
      id: widget.pivotId,
      fieldId: widget.fieldId ?? 'field_001',
      name: 'المحوري الرئيسي',
      nameAr: 'المحوري الرئيسي',
      centerLat: 24.7136,
      centerLng: 46.6753,
      lengthMeters: 400,
      overhangMeters: 15,
      spansCount: 7,
      rotationDirection: RotationDirection.clockwise,
      areaHectares: 50.3,
      pivotType: PivotType.fullCircle,
      flowRateLph: 450000,
      operatingPressureBar: 2.8,
      hasVRI: true,
      hasEndGun: true,
      hasCornerSystem: false,
      sectors: _generateDemoSectors(),
      vriZones: _generateDemoVRIZones(),
      createdAt: DateTime.now().subtract(const Duration(days: 365)),
    );

    _pivotStatus = PivotStatus(
      pivotId: widget.pivotId,
      currentAngle: 127.5,
      operatingStatus: PivotOperatingStatus.running,
      direction: PivotDirection.forward,
      speedPercent: 85,
      timerHours: 12,
      elapsedMinutes: 245,
      currentFlowRateLph: 425000,
      currentPressureBar: 2.7,
      endGunActive: true,
      cornerSystemActive: false,
      waterAppliedM3: 1250,
      energyConsumedKwh: 180,
      estimatedCompletionTime: DateTime.now().add(const Duration(hours: 8)),
      lastUpdated: DateTime.now(),
      activeAlerts: [
        PivotAlert(
          id: 'alert_001',
          pivotId: widget.pivotId,
          alertType: PivotAlertType.lowPressure,
          severity: AlertSeverity.warning,
          message: 'Pressure dropped below optimal range',
          messageAr: 'انخفض الضغط عن المستوى الأمثل',
          timestamp: DateTime.now().subtract(const Duration(minutes: 15)),
        ),
      ],
    );
  }

  List<PivotSector> _generateDemoSectors() {
    final colors = [
      '#4CAF50', '#8BC34A', '#CDDC39', '#FFC107',
      '#FF9800', '#FF5722', '#4CAF50', '#8BC34A',
    ];
    final ndviValues = [0.75, 0.68, 0.72, 0.55, 0.62, 0.78, 0.71, 0.65];

    return List.generate(8, (i) {
      return PivotSector(
        id: 'sector_${i + 1}',
        sectorNumber: i + 1,
        name: 'Sector ${i + 1}',
        nameAr: 'قطاع ${i + 1}',
        startAngle: i * 45.0,
        endAngle: (i + 1) * 45.0,
        irrigationDepthMm: 25,
        applicationRateMmHr: 6.5,
        isEnabled: true,
        speedPercent: 100 - (i * 5),
        cropType: 'wheat',
        soilType: 'loamy',
        ndviValue: ndviValues[i],
        soilMoisturePercent: 45 + i * 3,
        color: colors[i],
      );
    });
  }

  List<VRIZone> _generateDemoVRIZones() {
    return [
      const VRIZone(
        id: 'vri_001',
        name: 'High Need Zone',
        nameAr: 'منطقة احتياج عالي',
        coordinates: [],
        rateMultiplier: 1.3,
        targetSoilMoisturePercent: 70,
        zoneType: VRIZoneType.highNeed,
        color: '#2196F3',
      ),
      const VRIZone(
        id: 'vri_002',
        name: 'Low Need Zone',
        nameAr: 'منطقة احتياج منخفض',
        coordinates: [],
        rateMultiplier: 0.7,
        targetSoilMoisturePercent: 50,
        zoneType: VRIZoneType.lowNeed,
        color: '#FF9800',
      ),
    ];
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(_pivotConfig.name),
              Text(
                '${_pivotConfig.areaHectares.toStringAsFixed(1)} هكتار',
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
            if (_pivotConfig.hasVRI)
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
            _buildDashboardTab(),
            _buildSectorsTab(),
            _buildScheduleTab(),
            _buildStatisticsTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildDashboardTab() {
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
                          if (_pivotConfig.hasVRI)
                            _buildToggleChip('VRI', _showVRI, () {
                              setState(() => _showVRI = !_showVRI);
                            }),
                        ],
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  PivotVisualization(
                    config: _pivotConfig,
                    status: _pivotStatus,
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
          _buildQuickStats(),

          const SizedBox(height: 16),

          // Control panel
          PivotControlPanel(
            config: _pivotConfig,
            status: _pivotStatus,
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

  Widget _buildQuickStats() {
    return Row(
      children: [
        Expanded(
          child: _StatCard(
            icon: Icons.speed,
            label: 'السرعة',
            value: '${_pivotStatus.speedPercent.toInt()}%',
            color: Colors.blue,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            icon: Icons.location_on,
            label: 'الموقع',
            value: '${_pivotStatus.currentAngle.toStringAsFixed(0)}°',
            color: Colors.orange,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            icon: Icons.water_drop,
            label: 'المياه',
            value: '${_pivotStatus.waterAppliedM3.toStringAsFixed(0)} م³',
            color: Colors.cyan,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: _StatCard(
            icon: Icons.timer,
            label: 'المتبقي',
            value: _formatRemainingTime(),
            color: Colors.purple,
          ),
        ),
      ],
    );
  }

  String _formatRemainingTime() {
    final remaining = _pivotStatus.timerHours * 60 - _pivotStatus.elapsedMinutes;
    if (remaining <= 0) return '0:00';
    final hours = (remaining / 60).floor();
    final mins = (remaining % 60).floor();
    return '$hours:${mins.toString().padLeft(2, '0')}';
  }

  Widget _buildSectorsTab() {
    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _pivotConfig.sectors.length,
      itemBuilder: (context, index) {
        final sector = _pivotConfig.sectors[index];
        return _SectorTile(
          sector: sector,
          onTap: () => _showSectorDetails(sector),
          onToggle: (enabled) => _toggleSector(sector, enabled),
        );
      },
    );
  }

  Widget _buildScheduleTab() {
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

  Widget _buildStatisticsTab() {
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
          Row(
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
              const SizedBox(width: 12),
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

          Row(
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
              const SizedBox(width: 12),
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
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            _EfficiencyRow(
                              label: 'توزيع المياه',
                              value: 92,
                              color: Colors.blue,
                            ),
                            const SizedBox(height: 8),
                            _EfficiencyRow(
                              label: 'استهلاك الطاقة',
                              value: 85,
                              color: Colors.orange,
                            ),
                            const SizedBox(height: 8),
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
    // في الإنتاج، يتم إرسال الأمر للسيرفر
    debugPrint('Command: ${command.commandType}');

    // Update local state for demo
    setState(() {
      switch (command.commandType) {
        case PivotCommandType.start:
        case PivotCommandType.resume:
          _pivotStatus = _pivotStatus.copyWith(
            operatingStatus: PivotOperatingStatus.running,
          );
          break;
        case PivotCommandType.pause:
          _pivotStatus = _pivotStatus.copyWith(
            operatingStatus: PivotOperatingStatus.paused,
          );
          break;
        case PivotCommandType.stop:
        case PivotCommandType.emergencyStop:
          _pivotStatus = _pivotStatus.copyWith(
            operatingStatus: PivotOperatingStatus.stopped,
          );
          break;
        case PivotCommandType.setSpeed:
          _pivotStatus = _pivotStatus.copyWith(
            speedPercent: command.speedPercent ?? _pivotStatus.speedPercent,
          );
          break;
        case PivotCommandType.setDirection:
          _pivotStatus = _pivotStatus.copyWith(
            direction: command.direction ?? _pivotStatus.direction,
          );
          break;
        case PivotCommandType.toggleEndGun:
          _pivotStatus = _pivotStatus.copyWith(
            endGunActive: command.endGunEnabled ?? !_pivotStatus.endGunActive,
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
    setState(() {
      final index = _pivotConfig.sectors.indexWhere((s) => s.id == sector.id);
      if (index != -1) {
        final updatedSectors = List<PivotSector>.from(_pivotConfig.sectors);
        updatedSectors[index] = sector.copyWith(isEnabled: enabled);
        _pivotConfig = _pivotConfig.copyWith(sectors: updatedSectors);
      }
    });
  }

  void _openSettings() {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => SectorManagementScreen(
          pivotConfig: _pivotConfig,
          onConfigUpdate: (config) {
            setState(() => _pivotConfig = config);
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
                    color: color.withOpacity(0.1),
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
                  color: _ndviColor(sector.ndviValue!).withOpacity(0.2),
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
                        color: const Color(0xFF367C2B).withOpacity(0.1),
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
                        color: Colors.blue.withOpacity(0.1),
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
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
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
