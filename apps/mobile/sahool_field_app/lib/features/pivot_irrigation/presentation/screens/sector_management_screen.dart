/// Sector Management Screen - Valley Style
/// شاشة إدارة القطاعات - بأسلوب فالي
library;

import 'package:flutter/material.dart';
import '../../domain/models/pivot_models.dart';

/// Sector management screen for configuring pivot sectors
/// شاشة إدارة القطاعات لتهيئة قطاعات المحوري
class SectorManagementScreen extends StatefulWidget {
  final PivotConfiguration pivotConfig;
  final Function(PivotConfiguration) onConfigUpdate;

  const SectorManagementScreen({
    super.key,
    required this.pivotConfig,
    required this.onConfigUpdate,
  });

  @override
  State<SectorManagementScreen> createState() => _SectorManagementScreenState();
}

class _SectorManagementScreenState extends State<SectorManagementScreen> {
  late PivotConfiguration _config;
  int _selectedSectorIndex = -1;

  @override
  void initState() {
    super.initState();
    _config = widget.pivotConfig;
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('إدارة القطاعات | Sector Management'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            IconButton(
              icon: const Icon(Icons.add_circle_outline),
              onPressed: _addSector,
              tooltip: 'إضافة قطاع',
            ),
            IconButton(
              icon: const Icon(Icons.save),
              onPressed: _saveChanges,
              tooltip: 'حفظ',
            ),
          ],
        ),
        body: Row(
          children: [
            // Sector list
            SizedBox(
              width: 280,
              child: _buildSectorList(),
            ),

            const VerticalDivider(width: 1),

            // Sector details
            Expanded(
              child: _selectedSectorIndex >= 0
                  ? _buildSectorDetails()
                  : _buildEmptyState(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectorList() {
    return Column(
      children: [
        // Header
        Container(
          padding: const EdgeInsets.all(16),
          color: Colors.grey[100],
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'القطاعات',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Text(
                '${_config.sectors.length} قطاع',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
        ),

        // Reorderable list
        Expanded(
          child: ReorderableListView.builder(
            itemCount: _config.sectors.length,
            onReorder: _reorderSectors,
            itemBuilder: (context, index) {
              final sector = _config.sectors[index];
              final isSelected = index == _selectedSectorIndex;

              return Material(
                key: ValueKey(sector.id),
                color: isSelected
                    ? const Color(0xFF367C2B).withValues(alpha: 0.1)
                    : null,
                child: ListTile(
                  leading: Container(
                    width: 36,
                    height: 36,
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
                  title: Text(
                    sector.nameAr.isNotEmpty
                        ? sector.nameAr
                        : 'قطاع ${sector.sectorNumber}',
                  ),
                  subtitle: Text(
                    '${sector.startAngle.toInt()}° - ${sector.endAngle.toInt()}°',
                    style: const TextStyle(fontSize: 12),
                  ),
                  trailing: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      if (!sector.isEnabled)
                        const Icon(Icons.block, color: Colors.red, size: 18),
                      const Icon(Icons.drag_handle, color: Colors.grey),
                    ],
                  ),
                  selected: isSelected,
                  onTap: () {
                    setState(() => _selectedSectorIndex = index);
                  },
                ),
              );
            },
          ),
        ),

        // Quick actions
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.grey[100],
            border: Border(top: BorderSide(color: Colors.grey[300]!)),
          ),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              TextButton.icon(
                onPressed: _enableAllSectors,
                icon: const Icon(Icons.check_circle, size: 18),
                label: const Text('تفعيل الكل'),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.green,
                ),
              ),
              TextButton.icon(
                onPressed: _disableAllSectors,
                icon: const Icon(Icons.block, size: 18),
                label: const Text('تعطيل الكل'),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.red,
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildSectorDetails() {
    final sector = _config.sectors[_selectedSectorIndex];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: _hexToColor(sector.color),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    '${sector.sectorNumber}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 24,
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
                      'قطاع ${sector.sectorNumber}',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      'الزاوية: ${sector.startAngle.toInt()}° - ${sector.endAngle.toInt()}°',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
              // Enable/Disable toggle
              Column(
                children: [
                  Switch(
                    value: sector.isEnabled,
                    onChanged: (value) => _updateSector(
                      sector.copyWith(isEnabled: value),
                    ),
                    activeColor: const Color(0xFF367C2B),
                  ),
                  Text(
                    sector.isEnabled ? 'مفعل' : 'معطل',
                    style: TextStyle(
                      color: sector.isEnabled ? Colors.green : Colors.red,
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ],
          ),

          const Divider(height: 32),

          // Sector name
          _buildTextField(
            label: 'اسم القطاع | Sector Name',
            value: sector.nameAr,
            onChanged: (value) => _updateSector(
              sector.copyWith(nameAr: value),
            ),
          ),

          const SizedBox(height: 20),

          // Angle range
          Row(
            children: [
              Expanded(
                child: _buildNumberField(
                  label: 'زاوية البداية | Start Angle',
                  value: sector.startAngle,
                  suffix: '°',
                  min: 0,
                  max: 359,
                  onChanged: (value) => _updateSector(
                    sector.copyWith(startAngle: value),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildNumberField(
                  label: 'زاوية النهاية | End Angle',
                  value: sector.endAngle,
                  suffix: '°',
                  min: 1,
                  max: 360,
                  onChanged: (value) => _updateSector(
                    sector.copyWith(endAngle: value),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Speed control
          _buildSliderField(
            label: 'السرعة | Speed',
            value: sector.speedPercent,
            min: 50,
            max: 100,
            suffix: '%',
            color: Colors.blue,
            onChanged: (value) => _updateSector(
              sector.copyWith(speedPercent: value),
            ),
          ),

          const SizedBox(height: 20),

          // Irrigation depth
          _buildSliderField(
            label: 'عمق الري | Irrigation Depth',
            value: sector.irrigationDepthMm,
            min: 10,
            max: 50,
            suffix: 'mm',
            color: Colors.cyan,
            onChanged: (value) => _updateSector(
              sector.copyWith(irrigationDepthMm: value),
            ),
          ),

          const SizedBox(height: 20),

          // Application rate
          _buildSliderField(
            label: 'معدل التطبيق | Application Rate',
            value: sector.applicationRateMmHr,
            min: 3,
            max: 15,
            suffix: 'mm/hr',
            color: Colors.orange,
            onChanged: (value) => _updateSector(
              sector.copyWith(applicationRateMmHr: value),
            ),
          ),

          const SizedBox(height: 20),

          // Crop type
          _buildDropdownField(
            label: 'نوع المحصول | Crop Type',
            value: sector.cropType,
            items: const [
              ('wheat', 'قمح | Wheat'),
              ('barley', 'شعير | Barley'),
              ('alfalfa', 'برسيم | Alfalfa'),
              ('corn', 'ذرة | Corn'),
              ('vegetables', 'خضروات | Vegetables'),
              ('fallow', 'بور | Fallow'),
            ],
            onChanged: (value) => _updateSector(
              sector.copyWith(cropType: value ?? ''),
            ),
          ),

          const SizedBox(height: 20),

          // Soil type
          _buildDropdownField(
            label: 'نوع التربة | Soil Type',
            value: sector.soilType,
            items: const [
              ('sandy', 'رملية | Sandy'),
              ('loamy', 'طينية | Loamy'),
              ('clay', 'صلصالية | Clay'),
              ('silty', 'طميية | Silty'),
            ],
            onChanged: (value) => _updateSector(
              sector.copyWith(soilType: value ?? ''),
            ),
          ),

          const SizedBox(height: 20),

          // Color picker
          _buildColorPicker(
            label: 'لون القطاع | Sector Color',
            value: sector.color,
            onChanged: (value) => _updateSector(
              sector.copyWith(color: value),
            ),
          ),

          const SizedBox(height: 32),

          // Delete button
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => _deleteSector(sector),
              icon: const Icon(Icons.delete_outline),
              label: const Text('حذف القطاع | Delete Sector'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                side: const BorderSide(color: Colors.red),
                padding: const EdgeInsets.symmetric(vertical: 16),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.pie_chart_outline, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'اختر قطاعاً للتعديل',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'Select a sector to edit',
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField({
    required String label,
    required String value,
    required Function(String) onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: TextEditingController(text: value),
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildNumberField({
    required String label,
    required double value,
    required String suffix,
    required double min,
    required double max,
    required Function(double) onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.grey[700],
            fontSize: 13,
          ),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: TextEditingController(text: value.toInt().toString()),
          keyboardType: TextInputType.number,
          decoration: InputDecoration(
            suffixText: suffix,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
          onChanged: (text) {
            final parsed = double.tryParse(text);
            if (parsed != null && parsed >= min && parsed <= max) {
              onChanged(parsed);
            }
          },
        ),
      ],
    );
  }

  Widget _buildSliderField({
    required String label,
    required double value,
    required double min,
    required double max,
    required String suffix,
    required Color color,
    required Function(double) onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey[700],
              ),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: color.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                '${value.toStringAsFixed(1)} $suffix',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        SliderTheme(
          data: SliderTheme.of(context).copyWith(
            activeTrackColor: color,
            inactiveTrackColor: color.withValues(alpha: 0.2),
            thumbColor: color,
            overlayColor: color.withValues(alpha: 0.1),
            trackHeight: 8,
          ),
          child: Slider(
            value: value,
            min: min,
            max: max,
            onChanged: onChanged,
          ),
        ),
      ],
    );
  }

  Widget _buildDropdownField({
    required String label,
    required String value,
    required List<(String, String)> items,
    required Function(String?) onChanged,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: value.isNotEmpty ? value : null,
          decoration: InputDecoration(
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            contentPadding: const EdgeInsets.symmetric(
              horizontal: 16,
              vertical: 12,
            ),
          ),
          items: items
              .map((item) => DropdownMenuItem(
                    value: item.$1,
                    child: Text(item.$2),
                  ))
              .toList(),
          onChanged: onChanged,
        ),
      ],
    );
  }

  Widget _buildColorPicker({
    required String label,
    required String value,
    required Function(String) onChanged,
  }) {
    final colors = [
      '#4CAF50',
      '#8BC34A',
      '#CDDC39',
      '#FFC107',
      '#FF9800',
      '#FF5722',
      '#E91E63',
      '#9C27B0',
      '#673AB7',
      '#3F51B5',
      '#2196F3',
      '#00BCD4',
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: colors.map((color) {
            final isSelected = color.toLowerCase() == value.toLowerCase();
            return GestureDetector(
              onTap: () => onChanged(color),
              child: Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: _hexToColor(color),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: isSelected ? Colors.black : Colors.transparent,
                    width: 3,
                  ),
                ),
                child: isSelected
                    ? const Icon(Icons.check, color: Colors.white)
                    : null,
              ),
            );
          }).toList(),
        ),
      ],
    );
  }

  void _updateSector(PivotSector updatedSector) {
    setState(() {
      final sectors = List<PivotSector>.from(_config.sectors);
      sectors[_selectedSectorIndex] = updatedSector;
      _config = _config.copyWith(sectors: sectors);
    });
  }

  void _addSector() {
    final newSectorNumber = _config.sectors.length + 1;
    final lastAngle =
        _config.sectors.isNotEmpty ? _config.sectors.last.endAngle : 0.0;
    final sectorSpan = 360.0 / (newSectorNumber);

    final newSector = PivotSector(
      id: 'sector_$newSectorNumber',
      sectorNumber: newSectorNumber,
      nameAr: 'قطاع $newSectorNumber',
      startAngle: lastAngle,
      endAngle: (lastAngle + sectorSpan).clamp(0, 360),
      color: '#4CAF50',
    );

    setState(() {
      _config = _config.copyWith(
        sectors: [..._config.sectors, newSector],
      );
      _selectedSectorIndex = _config.sectors.length - 1;
    });
  }

  void _deleteSector(PivotSector sector) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف القطاع | Delete Sector'),
        content: Text(
          'هل أنت متأكد من حذف قطاع ${sector.sectorNumber}؟\n'
          'Are you sure you want to delete sector ${sector.sectorNumber}?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء | Cancel'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                final sectors = List<PivotSector>.from(_config.sectors)
                  ..removeWhere((s) => s.id == sector.id);
                _config = _config.copyWith(sectors: sectors);
                _selectedSectorIndex = -1;
              });
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('حذف | Delete'),
          ),
        ],
      ),
    );
  }

  void _reorderSectors(int oldIndex, int newIndex) {
    setState(() {
      if (newIndex > oldIndex) newIndex--;
      final sectors = List<PivotSector>.from(_config.sectors);
      final item = sectors.removeAt(oldIndex);
      sectors.insert(newIndex, item);

      // Update sector numbers
      for (int i = 0; i < sectors.length; i++) {
        sectors[i] = sectors[i].copyWith(sectorNumber: i + 1);
      }

      _config = _config.copyWith(sectors: sectors);

      // Update selection
      if (_selectedSectorIndex == oldIndex) {
        _selectedSectorIndex = newIndex;
      } else if (_selectedSectorIndex > oldIndex &&
          _selectedSectorIndex <= newIndex) {
        _selectedSectorIndex--;
      } else if (_selectedSectorIndex < oldIndex &&
          _selectedSectorIndex >= newIndex) {
        _selectedSectorIndex++;
      }
    });
  }

  void _enableAllSectors() {
    setState(() {
      final sectors =
          _config.sectors.map((s) => s.copyWith(isEnabled: true)).toList();
      _config = _config.copyWith(sectors: sectors);
    });
  }

  void _disableAllSectors() {
    setState(() {
      final sectors =
          _config.sectors.map((s) => s.copyWith(isEnabled: false)).toList();
      _config = _config.copyWith(sectors: sectors);
    });
  }

  void _saveChanges() {
    widget.onConfigUpdate(_config);
    Navigator.pop(context);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم حفظ التغييرات | Changes saved'),
        backgroundColor: Color(0xFF367C2B),
      ),
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }
}
