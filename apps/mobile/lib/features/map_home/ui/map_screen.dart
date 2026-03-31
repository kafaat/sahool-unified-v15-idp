import 'dart:async' show unawaited;
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:go_router/go_router.dart';
import 'package:latlong2/latlong.dart' hide Path;
import '../../../core/di/providers.dart';
import '../../../core/iam/iam_providers.dart';
import '../../../core/map/sahool_tile_provider.dart';
import '../../../core/theme/sahool_theme.dart';
import '../../../core/widgets/connectivity_widget.dart';
import '../../weather/presentation/providers/weather_provider.dart';
import '../../../core/ui/field_status_mapper.dart';
import '../../../core/ui/sync_indicator.dart';
import '../../field/domain/entities/field.dart';
import '../../ndvi/domain/spectral_index.dart';
import '../../tasks/ui/widgets/daily_tasks_sheet.dart';
import 'widgets/field_context_panel.dart';

/// SAHOOL Map Screen - "Cockpit View"
/// شاشة الخريطة الاحترافية بأسلوب غرفة العمليات
///
/// مستوحاة من John Deere Ops Center و Trimble
class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  int _selectedLayerIndex = 0;
  bool _isSearchExpanded = false;

  // حالة الاتصال والمزامنة - تُقرأ تفاعلياً من connectivityProvider في build

  late final MapController _mapController;
  String _searchQuery = '';
  String _activeFilter = 'الكل';

  // الحقل المحدد (null = لا يوجد حقل محدد)
  Field? _selectedField;

  /// Compute the active spectral index from the selected layer
  SpectralIndex get _activeSpectralIndex {
    switch (_selectedLayerIndex) {
      case 3:
        return SpectralIndex.ndwi;
      case 4:
        return SpectralIndex.evi;
      case 5:
        return SpectralIndex.savi;
      default:
        return SpectralIndex.ndvi;
    }
  }

  final List<MapLayerOption> _layers = [
    MapLayerOption('القمر الصناعي', Icons.satellite_alt, true),
    MapLayerOption('الخريطة', Icons.map, false),
    MapLayerOption('NDVI', Icons.grass, false),
    MapLayerOption('NDWI', Icons.water_drop, false),
    MapLayerOption('EVI', Icons.park, false),
    MapLayerOption('SAVI', Icons.landscape, false),
  ];

  @override
  void dispose() {
    _mapController.dispose();
    super.dispose();
  }

  // Fields loaded from repository via provider
  List<Field> _repoFields = [];

  @override
  void initState() {
    super.initState();
    _mapController = MapController();
    _loadFields();
  }

  Future<void> _loadFields() async {
    try {
      final tenant = ref.read(currentTenantProvider);
      final tenantId = tenant?.id ?? 'default';
      final repo = ref.read(fieldsRepoProvider);
      final fields = await repo.getAllFields(tenantId);
      if (mounted) {
        setState(() {
          _repoFields = fields;
        });
      }
    } catch (e) {
      // Silently fall back to empty list - fields will load on next refresh
    }
  }

  List<Field> get _filteredFields {
    var fields = _repoFields;
    // Apply status filter
    if (_activeFilter == 'نشط') {
      fields = fields.where((f) => f.healthStatus == FieldStatus.healthy).toList();
    } else if (_activeFilter == 'تنبيه') {
      fields = fields.where((f) => f.needsAttention).toList();
    } else if (_activeFilter == 'حصاد') {
      fields = fields.where((f) => f.ndvi >= 0.8).toList();
    }
    // Apply search query
    if (_searchQuery.isNotEmpty) {
      fields = fields.where((f) =>
          f.name.contains(_searchQuery) ||
          (f.cropType?.contains(_searchQuery) ?? false)).toList();
    }
    return fields;
  }

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
          if (_selectedField == null) const DailyTasksSheet(),

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

  /// Field center locations derived from actual field centroids or boundary centers.
  /// Falls back to Sanaa region default when no geospatial data is available.
  List<LatLng> get _fieldLocations {
    const defaultCenter = LatLng(15.3694, 44.1910);
    if (_repoFields.isEmpty) return [defaultCenter];
    return _repoFields.map((field) {
      // Use centroid if available
      if (field.centroid != null) return field.centroid!;
      // Fall back to boundary center if available
      if (field.boundary.isNotEmpty) {
        final avgLat = field.boundary.map((p) => p.latitude).reduce((a, b) => a + b) / field.boundary.length;
        final avgLng = field.boundary.map((p) => p.longitude).reduce((a, b) => a + b) / field.boundary.length;
        return LatLng(avgLat, avgLng);
      }
      // Last resort: default center
      return defaultCenter;
    }).toList();
  }

  /// الخريطة الحقيقية - FlutterMap
  Widget _buildMapPlaceholder() {
    // Determine tile URL based on selected layer
    final String tileUrl;
    // Is a spectral index layer active? (indices 2-5: NDVI, NDWI, EVI, SAVI)
    final bool isSpectralLayer = _selectedLayerIndex >= 2 && _selectedLayerIndex <= 5;
    switch (_selectedLayerIndex) {
      case 0: // Satellite
        tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
        break;
      case 2: // NDVI
      case 3: // NDWI
      case 4: // EVI
      case 5: // SAVI
        // Use satellite imagery as base for spectral overlays
        tileUrl = 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}';
        break;
      default: // Map
        tileUrl = 'https://tile.openstreetmap.org/{z}/{x}/{y}.png';
    }

    return FlutterMap(
      mapController: _mapController,
      options: MapOptions(
        initialCenter: _fieldLocations.isNotEmpty
            ? _fieldLocations.first
            : const LatLng(15.3694, 44.1910), // default: صنعاء
        initialZoom: 12,
        onTap: (tapPosition, point) {
          if (_selectedField != null) {
            setState(() => _selectedField = null);
          }
        },
      ),
      children: [
        // Base tile layer - switches based on selected layer
        TileLayer(
          urlTemplate: tileUrl,
          userAgentPackageName: 'com.sahool.field',
          maxZoom: 19,
          tileProvider: SahoolTileProvider(),
        ),

        // Spectral index colored polygons overlay (NDVI/NDWI/EVI/SAVI layers)
        if (isSpectralLayer)
          PolygonLayer(
            polygons: _filteredFields.asMap().entries.map((entry) {
              final idx = entry.key;
              final field = entry.value;
              if (idx >= _fieldLocations.length) return null;
              final loc = _fieldLocations[idx];
              final color = _getIndexColor(field.ndvi);
              // Create a small polygon around each field location
              const offset = 0.005;
              return Polygon(
                points: [
                  LatLng(loc.latitude - offset, loc.longitude - offset),
                  LatLng(loc.latitude - offset, loc.longitude + offset),
                  LatLng(loc.latitude + offset, loc.longitude + offset),
                  LatLng(loc.latitude + offset, loc.longitude - offset),
                ],
                color: color.withValues(alpha: 0.4),
                borderColor: color,
                borderStrokeWidth: 2,
                label: '${_activeSpectralIndex.code}: ${field.ndvi.toStringAsFixed(2)}',
                labelStyle: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  shadows: [Shadow(color: Colors.black54, blurRadius: 4)],
                ),
              );
            }).whereType<Polygon>().toList(),
          ),

        // Field markers
        MarkerLayer(
          markers: _buildFieldMarkers(),
        ),
      ],
    );
  }

  /// بناء قائمة markers محسّنة (تُحسب مرة واحدة ما لم يتغير التحديد)
  List<Marker> _buildFieldMarkers() {
    final fields = _filteredFields;
    return List.generate(fields.length, (index) {
      final field = fields[index];
      if (index >= _fieldLocations.length) return null;
      final location = _fieldLocations[index];
      return Marker(
        point: location,
        width: 150,
        height: 60,
        child: RepaintBoundary(
          child: _FieldMarkerWidget(
            key: ValueKey('marker-${field.id}'),
            field: field,
            isSelected: _selectedField?.id == field.id,
            onTap: () => _selectField(field),
          ),
        ),
      );
    }).whereType<Marker>().toList();
  }

  Color _getIndexColor(double value) {
    return SpectralColormap.getColor(_activeSpectralIndex, value);
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
      child: Builder(builder: (context) {
        final connectivity = ref.watch(connectivityProvider);
        return SyncIndicator(
          isOnline: connectivity.isOnline,
          pendingCount: connectivity.pendingSyncCount,
          onTap: () => context.push('/sync'),
        );
      }),
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
        clipBehavior: Clip.hardEdge,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        height: _isSearchExpanded ? 120 : 56,
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(28),
          boxShadow: SahoolShadows.large,
        ),
        child: SingleChildScrollView(
          physics: const NeverScrollableScrollPhysics(),
          child: Column(
            mainAxisSize: MainAxisSize.min,
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
                        onChanged: (value) => setState(() => _searchQuery = value),
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
                SizedBox(
                  height: 63,
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
      ),
    );
  }

  Widget _buildQuickFilter(String label, bool isSelected) {
    return FilterChip(
      label: Text(label),
      selected: _activeFilter == label,
      onSelected: (_) => setState(() => _activeFilter = label),
      selectedColor: SahoolColors.primary.withValues(alpha: 0.2),
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
          _buildMapControlButton(Icons.add, 'تكبير', () {
            final zoom = _mapController.camera.zoom;
            _mapController.move(_mapController.camera.center, zoom + 1);
          }),
          const SizedBox(height: 8),
          _buildMapControlButton(Icons.remove, 'تصغير', () {
            final zoom = _mapController.camera.zoom;
            _mapController.move(_mapController.camera.center, zoom - 1);
          }),
          const SizedBox(height: 16),
          _buildMapControlButton(Icons.my_location, 'موقعي', () {
            unawaited(_centerOnUserLocation());
          }, highlight: true),
          const SizedBox(height: 8),
          _buildMapControlButton(Icons.crop_free, 'إطار', () {
            // Fit all field markers into view
            if (_fieldLocations.isNotEmpty) {
              _mapController.fitCamera(
                CameraFit.coordinates(
                  coordinates: _fieldLocations,
                  padding: const EdgeInsets.all(50),
                ),
              );
            }
          }),
          const SizedBox(height: 8),
          _buildMapControlButton(Icons.route, 'مسار', () {}),
        ],
      ),
    );
  }

  Future<void> _centerOnUserLocation() async {
    try {
      final permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        await Geolocator.requestPermission();
      }
      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          timeLimit: Duration(seconds: 10),
        ),
      );
      _mapController.move(
        LatLng(position.latitude, position.longitude),
        14,
      );
    } catch (e) {
      // Fall back to first field location or default
      final center = _fieldLocations.isNotEmpty
          ? _fieldLocations.first
          : const LatLng(15.3694, 44.1910);
      _mapController.move(center, 14);
    }
  }

  Widget _buildMapControlButton(IconData icon, String tooltip, VoidCallback onPressed, {bool highlight = false}) {
    return DecoratedBox(
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
                    color: isSelected ? SahoolColors.primary.withValues(alpha: 0.1) : Colors.transparent,
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
                Expanded(child: _buildStatItem('حقول', '${_repoFields.length}', SahoolColors.success, Icons.grass)),
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

  int _getTotalTasks() => _repoFields.fold(0, (sum, f) => sum + f.pendingTasks);

  int _getCriticalCount() => _repoFields.where((f) => f.needsAttention).length;

  double _getAverageHealth() {
    if (_repoFields.isEmpty) return 0;
    return _repoFields.map((f) => f.ndvi).reduce((a, b) => a + b) / _repoFields.length;
  }

  Widget _buildWeatherBadge() {
    final weatherState = ref.watch(weatherProvider);
    final temp = weatherState.data?.current.temperature;
    final tempText = temp != null ? '${temp.round()}°C' : '--°C';

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
            tempText,
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
            color: color.withValues(alpha: 0.1),
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
        title: const Row(
          children: [
            Icon(Icons.add_task, color: SahoolColors.primary),
            SizedBox(width: 8),
            Text('إضافة مهمة'),
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
        title: const Row(
          children: [
            Icon(Icons.warning, color: SahoolColors.danger),
            SizedBox(width: 8),
            Text('طوارئ'),
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

/// Widget مستقل لعلامة الحقل - يتجنب إعادة البناء غير الضرورية
class _FieldMarkerWidget extends StatelessWidget {
  final Field field;
  final bool isSelected;
  final VoidCallback onTap;

  const _FieldMarkerWidget({
    super.key,
    required this.field,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
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
                          color: field.statusColor.withValues(alpha: 0.4),
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
                  Flexible(
                    child: Text(
                      field.name,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                        color: isSelected ? Colors.white : Colors.black87,
                      ),
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
