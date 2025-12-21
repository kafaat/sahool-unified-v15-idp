import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/crop_health_entities.dart';
import '../providers/crop_health_provider.dart';

/// شاشة السلسلة الزمنية للمنطقة
class ZoneTimelineScreen extends ConsumerStatefulWidget {
  final String fieldId;
  final String zoneId;
  final String? zoneName;

  const ZoneTimelineScreen({
    super.key,
    required this.fieldId,
    required this.zoneId,
    this.zoneName,
  });

  @override
  ConsumerState<ZoneTimelineScreen> createState() => _ZoneTimelineScreenState();
}

class _ZoneTimelineScreenState extends ConsumerState<ZoneTimelineScreen> {
  String _selectedIndex = 'ndvi';

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(timelineProvider.notifier).loadTimeline(
            widget.fieldId,
            widget.zoneId,
          );
    });
  }

  @override
  Widget build(BuildContext context) {
    final timelineState = ref.watch(timelineProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: Text(widget.zoneName ?? 'السلسلة الزمنية'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
        ),
        body: timelineState.isLoading
            ? const Center(child: CircularProgressIndicator())
            : timelineState.error != null
                ? Center(child: Text(timelineState.error!))
                : timelineState.timeline != null
                    ? _buildTimeline(timelineState.timeline!)
                    : const Center(child: Text('لا توجد بيانات')),
      ),
    );
  }

  Widget _buildTimeline(ZoneTimeline timeline) {
    return Column(
      children: [
        // اختيار المؤشر
        Padding(
          padding: const EdgeInsets.all(16),
          child: _buildIndexSelector(),
        ),

        // الرسم البياني
        Expanded(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: _buildChart(timeline),
          ),
        ),

        // جدول البيانات
        Expanded(
          child: _buildDataTable(timeline),
        ),
      ],
    );
  }

  Widget _buildIndexSelector() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildIndexChip('NDVI', 'ndvi', Colors.green),
          const SizedBox(width: 8),
          _buildIndexChip('NDWI', 'ndwi', Colors.blue),
          const SizedBox(width: 8),
          _buildIndexChip('NDRE', 'ndre', Colors.orange),
          const SizedBox(width: 8),
          _buildIndexChip('EVI', 'evi', Colors.purple),
          const SizedBox(width: 8),
          _buildIndexChip('SAVI', 'savi', Colors.brown),
        ],
      ),
    );
  }

  Widget _buildIndexChip(String label, String value, Color color) {
    final isSelected = _selectedIndex == value;
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (_) => setState(() => _selectedIndex = value),
      selectedColor: color.withOpacity(0.2),
      checkmarkColor: color,
      labelStyle: TextStyle(
        color: isSelected ? color : Colors.grey[700],
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
      ),
    );
  }

  Widget _buildChart(ZoneTimeline timeline) {
    if (timeline.series.isEmpty) {
      return const Center(child: Text('لا توجد بيانات كافية للرسم'));
    }

    // Simple chart using CustomPaint
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'تطور ${_selectedIndex.toUpperCase()}',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: CustomPaint(
                painter: _ChartPainter(
                  data: timeline.series,
                  selectedIndex: _selectedIndex,
                  color: _getIndexColor(_selectedIndex),
                ),
                size: Size.infinite,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _getIndexColor(String index) {
    switch (index) {
      case 'ndvi':
        return Colors.green;
      case 'ndwi':
        return Colors.blue;
      case 'ndre':
        return Colors.orange;
      case 'evi':
        return Colors.purple;
      case 'savi':
        return Colors.brown;
      default:
        return Colors.grey;
    }
  }

  Widget _buildDataTable(ZoneTimeline timeline) {
    return Card(
      margin: const EdgeInsets.all(16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: SingleChildScrollView(
        child: DataTable(
          columns: const [
            DataColumn(label: Text('التاريخ')),
            DataColumn(label: Text('NDVI')),
            DataColumn(label: Text('NDWI')),
            DataColumn(label: Text('NDRE')),
          ],
          rows: timeline.series.map((point) {
            return DataRow(cells: [
              DataCell(Text(point.date)),
              DataCell(Text(point.ndvi.toStringAsFixed(2))),
              DataCell(Text(point.ndwi?.toStringAsFixed(2) ?? '-')),
              DataCell(Text(point.ndre?.toStringAsFixed(2) ?? '-')),
            ]);
          }).toList(),
        ),
      ),
    );
  }
}

/// رسام الرسم البياني
class _ChartPainter extends CustomPainter {
  final List<TimelinePoint> data;
  final String selectedIndex;
  final Color color;

  _ChartPainter({
    required this.data,
    required this.selectedIndex,
    required this.color,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (data.isEmpty) return;

    final paint = Paint()
      ..color = color
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    final fillPaint = Paint()
      ..color = color.withOpacity(0.1)
      ..style = PaintingStyle.fill;

    final dotPaint = Paint()
      ..color = color
      ..style = PaintingStyle.fill;

    // الحصول على القيم
    final values = data.map((p) {
      switch (selectedIndex) {
        case 'ndvi':
          return p.ndvi;
        case 'ndwi':
          return p.ndwi ?? 0;
        case 'ndre':
          return p.ndre ?? 0;
        case 'evi':
          return p.evi ?? 0;
        case 'savi':
          return p.savi ?? 0;
        default:
          return p.ndvi;
      }
    }).toList();

    // حساب الحدود
    double minValue = -1;
    double maxValue = 1;

    // تحويل إلى نقاط
    final points = <Offset>[];
    for (var i = 0; i < values.length; i++) {
      final x = (i / (values.length - 1)) * size.width;
      final y = size.height - ((values[i] - minValue) / (maxValue - minValue)) * size.height;
      points.add(Offset(x, y));
    }

    // رسم الخط
    if (points.length > 1) {
      final path = Path()..moveTo(points.first.dx, points.first.dy);
      for (var i = 1; i < points.length; i++) {
        path.lineTo(points[i].dx, points[i].dy);
      }
      canvas.drawPath(path, paint);

      // رسم التعبئة
      final fillPath = Path.from(path)
        ..lineTo(points.last.dx, size.height)
        ..lineTo(points.first.dx, size.height)
        ..close();
      canvas.drawPath(fillPath, fillPaint);
    }

    // رسم النقاط
    for (final point in points) {
      canvas.drawCircle(point, 6, dotPaint);
      canvas.drawCircle(
        point,
        4,
        Paint()..color = Colors.white,
      );
    }

    // رسم خطوط المرجع
    final gridPaint = Paint()
      ..color = Colors.grey[300]!
      ..strokeWidth = 1;

    // خط الصفر
    final zeroY = size.height - ((0 - minValue) / (maxValue - minValue)) * size.height;
    canvas.drawLine(
      Offset(0, zeroY),
      Offset(size.width, zeroY),
      gridPaint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}
