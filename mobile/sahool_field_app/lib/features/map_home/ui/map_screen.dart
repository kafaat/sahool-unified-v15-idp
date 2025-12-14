import 'package:flutter/material.dart';
import '../../../core/theme/sahool_theme.dart';

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

  final List<MapLayerOption> _layers = [
    MapLayerOption('القمر الصناعي', Icons.satellite_alt, true),
    MapLayerOption('الخريطة', Icons.map, false),
    MapLayerOption('NDVI', Icons.grass, false),
    MapLayerOption('الرطوبة', Icons.water_drop, false),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Stack(
        children: [
          // 1. الخريطة (الطبقة الخلفية) - Placeholder
          _buildMapPlaceholder(),

          // 2. شريط البحث العائم (في الأعلى)
          _buildFloatingSearchBar(),

          // 3. أدوات التحكم الجانبية (مثل John Deere)
          _buildMapControls(),

          // 4. محدد الطبقات
          _buildLayerSelector(),

          // 5. بطاقة الملخص السفلية (Bottom Sheet)
          _buildSummaryCard(),

          // 6. زر الطوارئ/SOS (اختياري)
          _buildEmergencyButton(),
        ],
      ),
    );
  }

  /// الخريطة - Placeholder (استبدلها بـ FlutterMap لاحقاً)
  Widget _buildMapPlaceholder() {
    return Container(
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Color(0xFF87CEEB), // سماء
            Color(0xFF90EE90), // أرض خضراء
          ],
        ),
      ),
      child: Stack(
        children: [
          // شبكة وهمية للحقول
          ...List.generate(6, (index) {
            return Positioned(
              left: 30.0 + (index % 3) * 120,
              top: 200.0 + (index ~/ 3) * 150,
              child: _buildFieldMarker(
                'حقل ${index + 1}',
                index == 0 ? SahoolColors.healthExcellent :
                index == 3 ? SahoolColors.healthPoor : SahoolColors.healthGood,
              ),
            );
          }),
        ],
      ),
    );
  }

  /// علامة الحقل على الخريطة
  Widget _buildFieldMarker(String name, Color healthColor) {
    return GestureDetector(
      onTap: () => _showFieldDetails(name),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(20),
              boxShadow: SahoolShadows.medium,
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  width: 12,
                  height: 12,
                  decoration: BoxDecoration(
                    color: healthColor,
                    shape: BoxShape.circle,
                  ),
                ),
                const SizedBox(width: 6),
                Text(
                  name,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          CustomPaint(
            size: const Size(20, 10),
            painter: _TrianglePainter(),
          ),
        ],
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
    return Positioned(
      bottom: 24,
      left: 16,
      right: 16,
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
                Expanded(child: _buildStatItem('مهام', '3', SahoolColors.info, Icons.task_alt)),
                Expanded(child: _buildStatItem('تنبيهات', '1', SahoolColors.danger, Icons.warning_amber)),
                Expanded(child: _buildStatItem('حقول', '12', SahoolColors.success, Icons.grass)),
              ],
            ),
            const SizedBox(height: 16),
            // شريط التقدم
            Row(
              children: [
                const Text('تقدم اليوم', style: TextStyle(fontSize: 12, color: SahoolColors.textSecondary)),
                const SizedBox(width: 12),
                Expanded(
                  child: ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: 0.65,
                      backgroundColor: Colors.grey[200],
                      valueColor: const AlwaysStoppedAnimation(SahoolColors.primary),
                      minHeight: 8,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                const Text('65%', style: TextStyle(fontWeight: FontWeight.bold)),
              ],
            ),
          ],
        ),
      ),
    );
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
      bottom: 200,
      right: 16,
      child: Container(
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

  void _showFieldDetails(String fieldName) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(24),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
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
            Text(fieldName, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            const Text('قمح - 15 هكتار', style: TextStyle(color: SahoolColors.textSecondary)),
            const SizedBox(height: 20),
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.visibility),
                    label: const Text('عرض التفاصيل'),
                  ),
                ),
                const SizedBox(width: 12),
                OutlinedButton.icon(
                  onPressed: () {},
                  icon: const Icon(Icons.navigation),
                  label: const Text('اذهب'),
                ),
              ],
            ),
          ],
        ),
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
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.fill;

    final path = Path()
      ..moveTo(size.width / 2, size.height)
      ..lineTo(0, 0)
      ..lineTo(size.width, 0)
      ..close();

    canvas.drawPath(path, paint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
