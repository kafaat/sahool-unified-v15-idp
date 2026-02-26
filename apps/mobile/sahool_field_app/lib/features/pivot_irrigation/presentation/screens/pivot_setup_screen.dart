/// Pivot Setup Screen - شاشة إعداد المحوري
/// Configure pivot irrigation system with optional sector drawing
library;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../domain/models/pivot_models.dart';
import '../widgets/sector_drawing_tool.dart';
import '../widgets/pivot_visualization.dart';

/// Pivot setup/configuration screen
/// شاشة إعداد وتهيئة المحوري
class PivotSetupScreen extends StatefulWidget {
  /// Existing pivot to edit (null for new pivot)
  final PivotConfiguration? existingPivot;

  /// Field ID to associate with
  final String fieldId;

  /// Field center coordinates
  final double? fieldCenterLat;
  final double? fieldCenterLng;

  /// Callback when pivot is saved
  final Function(PivotConfiguration) onSave;

  const PivotSetupScreen({
    super.key,
    this.existingPivot,
    required this.fieldId,
    this.fieldCenterLat,
    this.fieldCenterLng,
    required this.onSave,
  });

  @override
  State<PivotSetupScreen> createState() => _PivotSetupScreenState();
}

class _PivotSetupScreenState extends State<PivotSetupScreen> {
  late PageController _pageController;
  int _currentPage = 0;

  // Form controllers
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _nameController;
  late TextEditingController _lengthController;
  late TextEditingController _overhangController;
  late TextEditingController _spansController;
  late TextEditingController _flowRateController;
  late TextEditingController _pressureController;

  // Configuration values
  PivotType _pivotType = PivotType.fullCircle;
  RotationDirection _rotationDirection = RotationDirection.clockwise;
  bool _hasEndGun = false;
  bool _hasVRI = false;
  bool _hasCornerSystem = false;

  // Sector configuration
  bool _useCustomSectors = false;
  List<PivotSector> _sectors = [];
  int _defaultSectorCount = 8;

  @override
  void initState() {
    super.initState();
    _pageController = PageController();

    // Initialize from existing pivot or defaults
    final existing = widget.existingPivot;
    _nameController = TextEditingController(
      text: existing?.name ?? 'المحوري الجديد',
    );
    _lengthController = TextEditingController(
      text: existing?.lengthMeters.toString() ?? '400',
    );
    _overhangController = TextEditingController(
      text: existing?.overhangMeters.toString() ?? '0',
    );
    _spansController = TextEditingController(
      text: existing?.spansCount.toString() ?? '7',
    );
    _flowRateController = TextEditingController(
      text: existing?.flowRateLph.toString() ?? '450000',
    );
    _pressureController = TextEditingController(
      text: existing?.operatingPressureBar.toString() ?? '2.5',
    );

    if (existing != null) {
      _pivotType = existing.pivotType;
      _rotationDirection = existing.rotationDirection;
      _hasEndGun = existing.hasEndGun;
      _hasVRI = existing.hasVRI;
      _hasCornerSystem = existing.hasCornerSystem;
      _sectors = existing.sectors.toList();
      _useCustomSectors = existing.sectors.isNotEmpty;
    }
  }

  @override
  void dispose() {
    _pageController.dispose();
    _nameController.dispose();
    _lengthController.dispose();
    _overhangController.dispose();
    _spansController.dispose();
    _flowRateController.dispose();
    _pressureController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(
            widget.existingPivot != null ? 'تعديل المحوري' : 'إعداد محوري جديد',
          ),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            if (_currentPage > 0)
              TextButton(
                onPressed: _goToPreviousPage,
                child: const Text(
                  'السابق',
                  style: TextStyle(color: Colors.white),
                ),
              ),
          ],
        ),
        body: Column(
          children: [
            // Progress indicator
            _buildProgressIndicator(),

            // Page content
            Expanded(
              child: PageView(
                controller: _pageController,
                physics: const NeverScrollableScrollPhysics(),
                onPageChanged: (page) {
                  setState(() => _currentPage = page);
                },
                children: [
                  _buildBasicInfoPage(),
                  _buildTechnicalPage(),
                  _buildSectorConfigPage(),
                  _buildPreviewPage(),
                ],
              ),
            ),

            // Navigation buttons
            _buildNavigationButtons(),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressIndicator() {
    final steps = ['المعلومات', 'التقنية', 'القطاعات', 'المعاينة'];

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16),
      color: Colors.grey[100],
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: List.generate(steps.length, (index) {
          final isActive = index == _currentPage;
          final isCompleted = index < _currentPage;

          return Column(
            children: [
              Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: isActive
                      ? const Color(0xFF367C2B)
                      : (isCompleted ? Colors.green[300] : Colors.grey[300]),
                  shape: BoxShape.circle,
                ),
                child: Center(
                  child: isCompleted
                      ? const Icon(Icons.check, color: Colors.white, size: 18)
                      : Text(
                          '${index + 1}',
                          style: TextStyle(
                            color: isActive ? Colors.white : Colors.grey[600],
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                ),
              ),
              const SizedBox(height: 4),
              Text(
                steps[index],
                style: TextStyle(
                  fontSize: 11,
                  color: isActive ? const Color(0xFF367C2B) : Colors.grey[600],
                  fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                ),
              ),
            ],
          );
        }),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Page 1: Basic Information
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildBasicInfoPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'المعلومات الأساسية',
              style: TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'أدخل المعلومات الأساسية للمحوري',
              style: TextStyle(color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),

            // Pivot name
            TextFormField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: 'اسم المحوري',
                hintText: 'مثال: المحوري الرئيسي',
                prefixIcon: const Icon(Icons.label),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              validator: (value) {
                if (value == null || value.isEmpty) {
                  return 'الرجاء إدخال اسم المحوري';
                }
                return null;
              },
            ),
            const SizedBox(height: 20),

            // Pivot type
            const Text(
              'نوع المحوري',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildTypeChip(
                  PivotType.fullCircle,
                  'دائرة كاملة',
                  Icons.circle_outlined,
                ),
                _buildTypeChip(
                  PivotType.partialCircle,
                  'دائرة جزئية',
                  Icons.pie_chart_outline,
                ),
                _buildTypeChip(
                  PivotType.corner,
                  'زاوية',
                  Icons.crop_square,
                ),
                _buildTypeChip(
                  PivotType.linear,
                  'خطي',
                  Icons.linear_scale,
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Pivot dimensions
            Row(
              children: [
                Expanded(
                  child: TextFormField(
                    controller: _lengthController,
                    keyboardType: TextInputType.number,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    decoration: InputDecoration(
                      labelText: 'طول الذراع',
                      suffixText: 'متر',
                      prefixIcon: const Icon(Icons.straighten),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'مطلوب';
                      }
                      final length = double.tryParse(value);
                      if (length == null || length < 50 || length > 800) {
                        return '50-800 متر';
                      }
                      return null;
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextFormField(
                    controller: _spansController,
                    keyboardType: TextInputType.number,
                    inputFormatters: [FilteringTextInputFormatter.digitsOnly],
                    decoration: InputDecoration(
                      labelText: 'عدد الأبراج',
                      prefixIcon: const Icon(Icons.account_tree),
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'مطلوب';
                      }
                      final spans = int.tryParse(value);
                      if (spans == null || spans < 1 || spans > 20) {
                        return '1-20';
                      }
                      return null;
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 20),

            // Rotation direction
            const Text(
              'اتجاه الدوران',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildDirectionButton(
                    RotationDirection.clockwise,
                    'مع عقارب الساعة',
                    Icons.rotate_right,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: _buildDirectionButton(
                    RotationDirection.counterclockwise,
                    'عكس عقارب الساعة',
                    Icons.rotate_left,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 24),

            // Calculated area display
            _buildAreaDisplay(),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeChip(PivotType type, String label, IconData icon) {
    final isSelected = _pivotType == type;

    return ChoiceChip(
      label: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon,
            size: 18,
            color: isSelected ? Colors.white : Colors.grey[600],
          ),
          const SizedBox(width: 6),
          Text(label),
        ],
      ),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setState(() => _pivotType = type);
        }
      },
      selectedColor: const Color(0xFF367C2B),
      labelStyle: TextStyle(
        color: isSelected ? Colors.white : Colors.black87,
      ),
    );
  }

  Widget _buildDirectionButton(
    RotationDirection direction,
    String label,
    IconData icon,
  ) {
    final isSelected = _rotationDirection == direction;

    return Material(
      color: isSelected
          ? const Color(0xFF367C2B).withOpacity(0.1)
          : Colors.grey[100],
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: () => setState(() => _rotationDirection = direction),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(
              color: isSelected ? const Color(0xFF367C2B) : Colors.grey[300]!,
              width: isSelected ? 2 : 1,
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                size: 32,
                color: isSelected ? const Color(0xFF367C2B) : Colors.grey[600],
              ),
              const SizedBox(height: 8),
              Text(
                label,
                style: TextStyle(
                  fontSize: 12,
                  color:
                      isSelected ? const Color(0xFF367C2B) : Colors.grey[600],
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAreaDisplay() {
    final length = double.tryParse(_lengthController.text) ?? 0;
    final overhang = double.tryParse(_overhangController.text) ?? 0;
    final totalRadius = length + overhang;
    final area = 3.14159 * totalRadius * totalRadius / 10000; // hectares

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: const Color(0xFF367C2B).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: const Color(0xFF367C2B).withOpacity(0.3)),
      ),
      child: Row(
        children: [
          const Icon(Icons.crop_free, color: Color(0xFF367C2B)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'المساحة المقدرة',
                  style: TextStyle(fontSize: 12),
                ),
                Text(
                  '${area.toStringAsFixed(1)} هكتار',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: Color(0xFF367C2B),
                  ),
                ),
              ],
            ),
          ),
          Text(
            '${(area * 2.47).toStringAsFixed(1)} فدان',
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Page 2: Technical Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildTechnicalPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'الإعدادات التقنية',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'إعدادات التشغيل والميزات الإضافية',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 24),

          // Flow rate
          TextFormField(
            controller: _flowRateController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: 'معدل التدفق',
              suffixText: 'لتر/ساعة',
              prefixIcon: const Icon(Icons.water_drop),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Pressure
          TextFormField(
            controller: _pressureController,
            keyboardType: const TextInputType.numberWithOptions(decimal: true),
            decoration: InputDecoration(
              labelText: 'ضغط التشغيل',
              suffixText: 'بار',
              prefixIcon: const Icon(Icons.compress),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Overhang
          TextFormField(
            controller: _overhangController,
            keyboardType: TextInputType.number,
            decoration: InputDecoration(
              labelText: 'امتداد المدفع الطرفي',
              suffixText: 'متر',
              prefixIcon: const Icon(Icons.expand),
              helperText: 'المسافة الإضافية التي يغطيها المدفع الطرفي',
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Feature toggles
          const Text(
            'الميزات الإضافية',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          _buildFeatureToggle(
            'المدفع الطرفي | End Gun',
            'يضيف تغطية إضافية في نهاية الذراع',
            Icons.water,
            _hasEndGun,
            (value) => setState(() => _hasEndGun = value),
          ),
          const SizedBox(height: 8),

          _buildFeatureToggle(
            'الري متغير المعدل | VRI',
            'تطبيق كميات مختلفة من المياه حسب المنطقة',
            Icons.tune,
            _hasVRI,
            (value) => setState(() => _hasVRI = value),
          ),
          const SizedBox(height: 8),

          _buildFeatureToggle(
            'نظام الزوايا | Corner System',
            'لري الزوايا في الحقول المربعة',
            Icons.crop_square,
            _hasCornerSystem,
            (value) => setState(() => _hasCornerSystem = value),
          ),
        ],
      ),
    );
  }

  Widget _buildFeatureToggle(
    String title,
    String description,
    IconData icon,
    bool value,
    Function(bool) onChanged,
  ) {
    return Container(
      decoration: BoxDecoration(
        color:
            value ? const Color(0xFF367C2B).withOpacity(0.1) : Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: value ? const Color(0xFF367C2B) : Colors.grey[300]!,
        ),
      ),
      child: SwitchListTile(
        value: value,
        onChanged: onChanged,
        activeColor: const Color(0xFF367C2B),
        secondary: Icon(
          icon,
          color: value ? const Color(0xFF367C2B) : Colors.grey[600],
        ),
        title: Text(
          title,
          style: TextStyle(
            fontWeight: value ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        subtitle: Text(
          description,
          style: const TextStyle(fontSize: 12),
        ),
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Page 3: Sector Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildSectorConfigPage() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'تهيئة القطاعات',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'اختر طريقة تقسيم القطاعات',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 24),

          // Sector mode toggle
          Row(
            children: [
              Expanded(
                child: _buildModeButton(
                  'تقسيم تلقائي',
                  'قطاعات متساوية',
                  Icons.grid_view,
                  !_useCustomSectors,
                  () => setState(() => _useCustomSectors = false),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildModeButton(
                  'رسم يدوي',
                  'قطاعات مخصصة',
                  Icons.draw,
                  _useCustomSectors,
                  () => setState(() => _useCustomSectors = true),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          if (_useCustomSectors)
            // Custom sector drawing tool
            SectorDrawingTool(
              initialSectors: _sectors,
              onSectorsChanged: (sectors) {
                setState(() => _sectors = sectors);
              },
              drawingEnabled: true,
              showAngleLabels: true,
            )
          else
            // Automatic sector division
            _buildAutomaticSectorConfig(),
        ],
      ),
    );
  }

  Widget _buildModeButton(
    String title,
    String subtitle,
    IconData icon,
    bool isSelected,
    VoidCallback onTap,
  ) {
    return Material(
      color: isSelected
          ? const Color(0xFF367C2B).withOpacity(0.1)
          : Colors.grey[100],
      borderRadius: BorderRadius.circular(12),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            border: Border.all(
              color: isSelected ? const Color(0xFF367C2B) : Colors.grey[300]!,
              width: isSelected ? 2 : 1,
            ),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            children: [
              Icon(
                icon,
                size: 36,
                color: isSelected ? const Color(0xFF367C2B) : Colors.grey[600],
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: isSelected ? const Color(0xFF367C2B) : Colors.black87,
                ),
              ),
              Text(
                subtitle,
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey[600],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAutomaticSectorConfig() {
    return Column(
      children: [
        // Sector count selector
        const Text(
          'عدد القطاعات',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(
              icon: const Icon(Icons.remove_circle, size: 36),
              onPressed: _defaultSectorCount > 2
                  ? () => setState(() => _defaultSectorCount--)
                  : null,
              color: const Color(0xFF367C2B),
            ),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              decoration: BoxDecoration(
                color: const Color(0xFF367C2B).withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Text(
                '$_defaultSectorCount',
                style: const TextStyle(
                  fontSize: 32,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF367C2B),
                ),
              ),
            ),
            IconButton(
              icon: const Icon(Icons.add_circle, size: 36),
              onPressed: _defaultSectorCount < 16
                  ? () => setState(() => _defaultSectorCount++)
                  : null,
              color: const Color(0xFF367C2B),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          'كل قطاع: ${(360 / _defaultSectorCount).toStringAsFixed(1)}°',
          style: TextStyle(color: Colors.grey[600]),
        ),
        const SizedBox(height: 24),

        // Preview
        SizedBox(
          height: 250,
          child: PivotVisualization(
            config: _buildPreviewConfig(),
            showArm: false,
            animate: false,
          ),
        ),
      ],
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Page 4: Preview
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildPreviewPage() {
    final config = _buildFinalConfig();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'معاينة المحوري',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'راجع الإعدادات قبل الحفظ',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 24),

          // Pivot visualization
          Center(
            child: PivotVisualization(
              config: config,
              showArm: true,
              animate: true,
              size: 280,
            ),
          ),
          const SizedBox(height: 24),

          // Summary card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildSummaryRow('الاسم', config.name),
                  _buildSummaryRow('الطول', '${config.lengthMeters} متر'),
                  _buildSummaryRow('عدد الأبراج', '${config.spansCount}'),
                  _buildSummaryRow(
                    'المساحة',
                    '${config.areaHectares.toStringAsFixed(1)} هكتار',
                  ),
                  _buildSummaryRow('عدد القطاعات', '${config.sectors.length}'),
                  _buildSummaryRow(
                    'معدل التدفق',
                    '${config.flowRateLph.toStringAsFixed(0)} ل/س',
                  ),
                  const Divider(),
                  _buildSummaryRow(
                    'المدفع الطرفي',
                    config.hasEndGun ? 'نعم ✓' : 'لا',
                  ),
                  _buildSummaryRow(
                    'VRI',
                    config.hasVRI ? 'نعم ✓' : 'لا',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(color: Colors.grey[600])),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Navigation
  // ═══════════════════════════════════════════════════════════════════════════

  Widget _buildNavigationButtons() {
    final isLastPage = _currentPage == 3;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: SafeArea(
        child: Row(
          children: [
            if (_currentPage > 0)
              Expanded(
                child: OutlinedButton(
                  onPressed: _goToPreviousPage,
                  child: const Text('السابق'),
                ),
              ),
            if (_currentPage > 0) const SizedBox(width: 12),
            Expanded(
              flex: 2,
              child: ElevatedButton(
                onPressed: isLastPage ? _savePivot : _goToNextPage,
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF367C2B),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: Text(isLastPage ? 'حفظ المحوري' : 'التالي'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _goToNextPage() {
    if (_currentPage == 0 && !_formKey.currentState!.validate()) {
      return;
    }

    _pageController.nextPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void _goToPreviousPage() {
    _pageController.previousPage(
      duration: const Duration(milliseconds: 300),
      curve: Curves.easeInOut,
    );
  }

  void _savePivot() {
    final config = _buildFinalConfig();
    widget.onSave(config);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('تم حفظ المحوري بنجاح'),
        backgroundColor: Color(0xFF367C2B),
      ),
    );

    Navigator.pop(context);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Config Builders
  // ═══════════════════════════════════════════════════════════════════════════

  PivotConfiguration _buildPreviewConfig() {
    final length = double.tryParse(_lengthController.text) ?? 400;
    final sectorAngle = 360.0 / _defaultSectorCount;

    return PivotConfiguration(
      id: 'preview',
      fieldId: widget.fieldId,
      name: _nameController.text,
      centerLat: widget.fieldCenterLat ?? 0,
      centerLng: widget.fieldCenterLng ?? 0,
      lengthMeters: length,
      spansCount: int.tryParse(_spansController.text) ?? 7,
      rotationDirection: _rotationDirection,
      areaHectares: 3.14159 * length * length / 10000,
      pivotType: _pivotType,
      flowRateLph: double.tryParse(_flowRateController.text) ?? 450000,
      sectors: List.generate(_defaultSectorCount, (i) {
        return PivotSector(
          id: 'sector_${i + 1}',
          sectorNumber: i + 1,
          startAngle: i * sectorAngle,
          endAngle: (i + 1) * sectorAngle,
          color: _defaultColors[i % _defaultColors.length],
        );
      }),
    );
  }

  PivotConfiguration _buildFinalConfig() {
    final length = double.tryParse(_lengthController.text) ?? 400;
    final overhang = double.tryParse(_overhangController.text) ?? 0;
    final totalRadius = length + overhang;

    // Build sectors
    List<PivotSector> sectors;
    if (_useCustomSectors && _sectors.isNotEmpty) {
      sectors = _sectors;
    } else {
      final sectorAngle = 360.0 / _defaultSectorCount;
      sectors = List.generate(_defaultSectorCount, (i) {
        return PivotSector(
          id: 'sector_${i + 1}',
          sectorNumber: i + 1,
          nameAr: 'قطاع ${i + 1}',
          startAngle: i * sectorAngle,
          endAngle: (i + 1) * sectorAngle,
          color: _defaultColors[i % _defaultColors.length],
        );
      });
    }

    return PivotConfiguration(
      id: widget.existingPivot?.id ??
          'pivot_${DateTime.now().millisecondsSinceEpoch}',
      fieldId: widget.fieldId,
      name: _nameController.text,
      nameAr: _nameController.text,
      centerLat: widget.fieldCenterLat ?? 0,
      centerLng: widget.fieldCenterLng ?? 0,
      lengthMeters: length,
      overhangMeters: overhang,
      spansCount: int.tryParse(_spansController.text) ?? 7,
      rotationDirection: _rotationDirection,
      areaHectares: 3.14159 * totalRadius * totalRadius / 10000,
      pivotType: _pivotType,
      flowRateLph: double.tryParse(_flowRateController.text) ?? 450000,
      operatingPressureBar: double.tryParse(_pressureController.text) ?? 2.5,
      hasEndGun: _hasEndGun,
      hasVRI: _hasVRI,
      hasCornerSystem: _hasCornerSystem,
      sectors: sectors,
      createdAt: widget.existingPivot?.createdAt ?? DateTime.now(),
      updatedAt: DateTime.now(),
    );
  }

  static const List<String> _defaultColors = [
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
}
