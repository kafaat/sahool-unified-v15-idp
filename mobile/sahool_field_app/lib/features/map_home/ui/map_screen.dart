import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/ui/field_status_mapper.dart';
import '../../../core/ui/sync_indicator.dart';
import '../../field/domain/entities/field.dart';
import '../../tasks/ui/widgets/daily_tasks_sheet.dart';
import 'widgets/field_context_panel.dart';

/// SAHOOL Map Screen - "Cockpit View"
/// شاشة الخريطة الاحترافية بأسلوب غرفة العمليات
///
/// مستوحاة من John Deere Ops Center و Trimble
class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  int _selectedLayerIndex = 0;
  bool _isSearchExpanded = false;

  // حالة الاتصال (للتجربة)
  bool _isOnline = true;
  int _pendingSync = 3;

  // الحقل المحدد (null = لا يوجد حقل محدد)
  Field? _selectedField;

  final List<MapLayerOption> _layers = [
    MapLayerOption('القمر الصناعي', Icons.satellite_alt, true),
    MapLayerOption('الخريطة', Icons.map, false),
    MapLayerOption('NDVI', Icons.grass, false),
    MapLayerOption('الرطوبة', Icons.water_drop, false),
  ];

  // بيانات وهمية للحقول (Mock Data)
  final List<Field> _mockFields = [
    const Field(
      id: '1',
      name: 'القطعة الشمالية',
      cropType: 'قمح',
      areaHa: 2.4,
      ndvi: 0.78,
      status: FieldStatus.healthy,
      pendingTasks: 1,
    ),
    const Field(
      id: '2',
      name: 'حقل الذرة',
      cropType: 'ذرة',
      areaHa: 3.1,
      ndvi: 0.65,
      status: FieldStatus.healthy,
      pendingTasks: 0,
    ),
    const Field(
      id: '3',
      name: 'البستان الغربي',
      cropType: 'عنب',
      areaHa: 1.8,
      ndvi: 0.52,
      status: FieldStatus.stressed,
      pendingTasks: 2,
    ),
    const Field(
      id: '4',
      name: 'حقل الطماطم',
      cropType: 'طماطم',
      areaHa: 0.9,
      ndvi: 0.35,
      status: FieldStatus.critical,
      pendingTasks: 4,
    ),
    const Field(
      id: '5',
      name: 'المنطقة الجنوبية',
      cropType: 'برسيم',
      areaHa: 4.2,
      ndvi: 0.71,
      status: FieldStatus.healthy,
      pendingTasks: 0,
    ),
    const Field(
      id: '6',
      name: 'حقل البطاطا',
      cropType: 'بطاطا',
      areaHa: 1.5,
      ndvi: 0.48,
      status: FieldStatus.stressed,
      pendingTasks: 1,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 1. ✅ الخريطة تملأ الشاشة بالكامل (Positioned.fill)
          Positioned.fill(
            child: _buildMapPlaceholder(),
          ),

          // 2. شريط البحث العائم (في الأعلى)
          _buildFloatingSearchBar(),

          // 3. أدوات التحكم الجانبية (مثل John Deere)
          _buildMapControls(),

          // 4. محدد الطبقات
          _buildLayerSelector(),

          // 5. Sync Indicator (جديد)
          _buildSyncIndicator(),

          // 6. زر الطوارئ/SOS
          _buildEmergencyButton(),

          // 7. لوحة المهام المنزلقة (تظهر فقط عندما لا يكون هناك حقل محدد)
          if (_selectedField == null) DailyTasksSheet(),

          // 8. لوحة تفاصيل الحقل (تغطي الشاشة عند تحديد حقل)
          if (_selectedField != null) _buildFieldContextPanel(),
        ],
      ),
    );
  }

  /// لوحة تفاصيل الحقل
  Widget _buildFieldContextPanel() {
    return Positioned(
      bottom: 0,
      left: 0,
      right: 0,
      child: AnimatedSwitcher(
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
        child: FieldContextPanel(
          key: ValueKey('panel-${_selectedField!.id}'),
          field: _selectedField!,
          onClose: () => setState(() => _selectedField = null),
          onDetails: () {
            context.push('/field/${_selectedField!.id}');
          },
          onAddTask: () {
            _showAddTaskDialog();
          },
        ),
      ),
    );
  }

  // إحداثيات وهمية للحقول (اليمن - صنعاء)
  final List<LatLng> _fieldLocations = const [
    LatLng(15.3694, 44.1910), // القطعة الشمالية
    LatLng(15.3550, 44.2050), // حقل الذرة
    LatLng(15.3800, 44.1750), // البستان الغربي
    LatLng(15.3450, 44.1850), // حقل الطماطم
    LatLng(15.3300, 44.2100), // المنطقة الجنوبية
    LatLng(15.3600, 44.1600), // حقل البطاطا
  ];

  /// الخريطة الحقيقية - FlutterMap
  Widget _buildMapPlaceholder() {
    return FlutterMap(
      options: MapOptions(
        initialCenter: const LatLng(15.3694, 44.1910), // صنعاء
        initialZoom: 12,
        onTap: (tapPosition, point) {
          // إلغاء التحديد عند الضغط على مكان فارغ
          if (_selectedField != null) {
            setState(() => _selectedField = null);
          }
        },
      ),
      children: [
        // طبقة الخرائط الأساسية
        TileLayer(
          urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
          userAgentPackageName: 'com.sahool.field',
          maxZoom: 19,
        ),

        // طبقة علامات الحقول
        MarkerLayer(
          markers: List.generate(_mockFields.length, (index) {
            final field = _mockFields[index];
            final location = _fieldLocations[index];
            return Marker(
              point: location,
              width: 150,
              height: 60,
              child: _buildFieldMarker(field),
            );
          }),
        ),
      ],
    );
  }

  /// علامة الحقل على الخريطة
  Widget _buildFieldMarker(Field field) {
    final isSelected = _selectedField?.id == field.id;

    return GestureDetector(
      onTap: () => _selectField(field),
      child: AnimatedScale(
        scale: isSelected ? 1.1 : 1.0,
        duration: const Duration(milliseconds: 200),
        child: Column(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
              decoration: BoxDecoration(
                color: isSelected ? field.statusColor : Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: isSelected
                    ? [
                        BoxShadow(
                          color: field.statusColor.withOpacity(0.4),
                          blurRadius: 12,
                          spreadRadius: 2,
                        ),
                      ]
                    : SahoolShadows.medium,
                border: isSelected
                    ? Border.all(color: Colors.white, width: 2)
                    : null,
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 12,
                    height: 12,
                    decoration: BoxDecoration(
                      color: isSelected ? Colors.white : field.statusColor,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    field.name,
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      color: isSelected ? Colors.white : Colors.black87,
                    ),
                  ),
                  if (field.pendingTasks > 0) ...[
                    const SizedBox(width: 6),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                      decoration: BoxDecoration(
                        color: isSelected ? Colors.white : Colors.orange,
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        '${field.pendingTasks}',
                        style: TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? field.statusColor : Colors.white,
                        ),
                      ),
                    ),
                  ],
                ],
              ),
            ),
            CustomPaint(
              size: const Size(20, 10),
              painter: _TrianglePainter(
                color: isSelected ? field.statusColor : Colors.white,
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// تحديد حقل
  void _selectField(Field field) {
    setState(() {
      _selectedField = _selectedField?.id == field.id ? null : field;
      _isSearchExpanded = false;
    });
  }

  /// Sync Indicator
  Widget _buildSyncIndicator() {
    return Positioned(
      top: MediaQuery.of(context).padding.top + 80,
      right: 70,
      child: SyncIndicator(
        isOnline: _isOnline,
        pendingCount: _pendingSync,
        onTap: () => context.push('/sync'),
      ),
    );
  }

  /// شريط البحث العائم
  Widget _buildFloatingSearchBar() {
    return Positioned(
      top: MediaQuery.of(context).padding.top + 16,
      left: 16,
      right: 16,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        padding: const EdgeInsets.symmetric(horizontal: 16),
        height: _isSearchExpanded ? 120 : 56,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(28),
          boxShadow: SahoolShadows.large,
        ),
        child: Column(
          children: [
            SizedBox(
              height: 56,
              child: Row(
                children: [
                  const Icon(Icons.search, color: SahoolColors.textSecondary),
                  const SizedBox(width: 12),
                  Expanded(
                    child: TextField(
                      decoration: const InputDecoration(
                        hintText: 'ابحث عن حقل أو منطقة...',
                        border: InputBorder.none,
                        contentPadding: EdgeInsets.zero,
                      ),
                      onTap: () => setState(() => _isSearchExpanded = true),
                    ),
                  ),
                  IconButton(
                    icon: Icon(
                      _isSearchExpanded ? Icons.close : Icons.filter_list,
                      color: SahoolColors.primary,
                    ),
                    onPressed: () => setState(() => _isSearchExpanded = !_isSearchExpanded),
                  ),
                ],
              ),
            ),
            if (_isSearchExpanded) ...[
              const Divider(height: 1),
              Expanded(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceAround,
                  children: [
                    _buildQuickFilter('الكل', true),
                    _buildQuickFilter('نشط', false),
                    _buildQuickFilter('تنبيه', false),
                    _buildQuickFilter('حصاد', false),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildQuickFilter(String label, bool isSelected) {
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) {},
      selectedColor: SahoolColors.primary.withOpacity(0.2),
      checkmarkColor: SahoolColors.primary,
    );
  }

  /// أدوات التحكم الجانبية
  Widget _buildMapControls() {
    return Positioned(
      right: 16,
      top: MediaQuery.of(context).padding.top + 90,
      child: Column(
        children: [
          _buildMapControlButton(Icons.add, 'تكبير', () {}),
          const SizedBox(height: 8),
          _buildMapControlButton(Icons.remove, 'تصغير', () {}),
          const SizedBox(height: 16),
          _buildMapControlButton(Icons.my_location, 'موقعي', () {}, highlight: true),
          const SizedBox(height: 8),
          _buildMapControlButton(Icons.crop_free, 'إطار', () {}),
          const SizedBox(height: 8),
          _buildMapControlButton(Icons.route, 'مسار', () {}),
        ],
      ),
    );
  }

  Widget _buildMapControlButton(IconData icon, String tooltip, VoidCallback onPressed, {bool highlight = false}) {
    return Container(
      decoration: BoxDecoration(
        color: highlight ? SahoolColors.primary : Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: SahoolShadows.medium,
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onPressed,
          borderRadius: BorderRadius.circular(12),
          child: SizedBox(
            height: 48,
            width: 48,
            child: Icon(
              icon,
              color: highlight ? Colors.white : SahoolColors.primary,
            ),
          ),
        ),
      ),
    );
  }

  /// محدد الطبقات
  Widget _buildLayerSelector() {
    return Positioned(
      left: 16,
      top: MediaQuery.of(context).padding.top + 90,
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: SahoolShadows.medium,
        ),
        child: Column(
          children: _layers.asMap().entries.map((entry) {
            final index = entry.key;
            final layer = entry.value;
            final isSelected = index == _selectedLayerIndex;

            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: GestureDetector(
                onTap: () => setState(() => _selectedLayerIndex = index),
                child: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: isSelected ? SahoolColors.primary.withOpacity(0.1) : Colors.transparent,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Icon(
                    layer.icon,
                    color: isSelected ? SahoolColors.primary : SahoolColors.textSecondary,
                    size: 24,
                  ),
                ),
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  /// بطاقة الملخص السفلية
  Widget _buildSummaryCard() {
    return Padding(
      key: const ValueKey('summary'),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: SahoolShadows.large,
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'ملخص اليوم',
                  style: TextStyle(fontWeight: FontWeight.bold, fontSize: 18),
                ),
                _buildWeatherBadge(),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(child: _buildStatItem('مهام', '${_getTotalTasks()}', SahoolColors.info, Icons.task_alt)),
                Expanded(child: _buildStatItem('تنبيهات', '${_getCriticalCount()}', SahoolColors.danger, Icons.warning_amber)),
                Expanded(child: _buildStatItem('حقول', '${_mockFields.length}', SahoolColors.success, Icons.grass)),
              ],
            ),
            const SizedBox(height: 16),
            // شريط التقدم
            Row(
              children: [
                const Text('صحة الحقول', style: TextStyle(fontSize: 12, color: SahoolColors.textSecondary)),
                const SizedBox(width: 12),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: _getAverageHealth(),
                      backgroundColor: Colors.grey[200],
                      valueColor: const AlwaysStoppedAnimation(SahoolColors.primary),
                      minHeight: 8,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Text('${(_getAverageHealth() * 100).toInt()}%', style: const TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
  }

  int _getTotalTasks() => _mockFields.fold(0, (sum, f) => sum + f.pendingTasks);

  int _getCriticalCount() => _mockFields.where((f) => f.needsAttention).length;

  double _getAverageHealth() {
    if (_mockFields.isEmpty) return 0;
    return _mockFields.map((f) => f.ndvi).reduce((a, b) => a + b) / _mockFields.length;
  }

  Widget _buildWeatherBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        gradient: SahoolColors.warningGradient,
        borderRadius: BorderRadius.circular(20),
        boxShadow: SahoolShadows.colored(SahoolColors.warning),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.wb_sunny, size: 18, color: Colors.orange[900]),
          const SizedBox(width: 6),
          Text(
            '32°C',
            style: TextStyle(fontWeight: FontWeight.bold, color: Colors.orange[900]),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color, IconData icon) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: color),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  /// زر الطوارئ
  Widget _buildEmergencyButton() {
    return Positioned(
      bottom: _selectedField != null ? 280 : 200,
      right: 16,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 300),
        decoration: BoxDecoration(
          gradient: const LinearGradient(
            colors: [Color(0xFFFF5252), SahoolColors.danger],
          ),
          shape: BoxShape.circle,
          boxShadow: SahoolShadows.colored(SahoolColors.danger),
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: () => _showEmergencyDialog(),
            borderRadius: BorderRadius.circular(28),
            child: const SizedBox(
              height: 56,
              width: 56,
              child: Icon(Icons.sos, color: Colors.white, size: 28),
            ),
          ),
        ),
      ),
    );
  }

  void _showAddTaskDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            const Icon(Icons.add_task, color: SahoolColors.primary),
            const SizedBox(width: 8),
            const Text('إضافة مهمة'),
          ],
        ),
        content: Text('إضافة مهمة جديدة لحقل "${_selectedField?.name}"'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إضافة'),
          ),
        ],
      ),
    );
  }

  void _showEmergencyDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Icon(Icons.warning, color: SahoolColors.danger),
            const SizedBox(width: 8),
            const Text('طوارئ'),
          ],
        ),
        content: const Text('هل تريد الإبلاغ عن حالة طوارئ في الحقل؟'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('إلغاء')),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: SahoolColors.danger),
            onPressed: () => Navigator.pop(context),
            child: const Text('إبلاغ'),
          ),
        ],
      ),
    );
  }
}

/// خيار طبقة الخريطة
class MapLayerOption {
  final String name;
  final IconData icon;
  final bool isDefault;

  MapLayerOption(this.name, this.icon, this.isDefault);
}

/// رسام المثلث للعلامات
class _TrianglePainter extends CustomPainter {
  final Color color;

  _TrianglePainter({this.color = Colors.white});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    final path = Path()
      ..moveTo(size.width / 2, size.height)
      ..lineTo(0, 0)
      ..lineTo(size.width, 0)
      ..close();

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant _TrianglePainter oldDelegate) => color != oldDelegate.color;
}
