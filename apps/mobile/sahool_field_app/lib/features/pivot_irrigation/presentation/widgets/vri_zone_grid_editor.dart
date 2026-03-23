/// VRI Zone Grid Editor - محرر شبكة مناطق VRI
/// Visual editor for configuring VRI zones at span/tower level
library;

import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../domain/models/span_zone_models.dart';

/// VRI Zone Grid Editor Widget
/// محرر شبكة مناطق VRI المرئي
class VRIZoneGridEditor extends StatefulWidget {
  /// Initial zone grid
  final VRIZoneGrid? initialGrid;

  /// Number of spans/towers
  final int spanCount;

  /// Number of angular divisions
  final int angularDivisions;

  /// Pivot ID
  final String pivotId;

  /// Called when grid changes
  final Function(VRIZoneGrid) onGridChanged;

  /// Widget size
  final double? size;

  /// Enable editing
  final bool editingEnabled;

  const VRIZoneGridEditor({
    super.key,
    this.initialGrid,
    required this.spanCount,
    required this.angularDivisions,
    required this.pivotId,
    required this.onGridChanged,
    this.size,
    this.editingEnabled = true,
  });

  @override
  State<VRIZoneGridEditor> createState() => _VRIZoneGridEditorState();
}

class _VRIZoneGridEditorState extends State<VRIZoneGridEditor> {
  late VRIZoneGrid _grid;
  final Set<String> _selectedZones = {};
  double _currentRate = 100;
  bool _isMultiSelectMode = false;

  @override
  void initState() {
    super.initState();
    _grid = widget.initialGrid ??
        VRIZoneGridBuilder.createUniformGrid(
          pivotId: widget.pivotId,
          spanCount: widget.spanCount,
          angularDivisions: widget.angularDivisions,
        );
  }

  @override
  Widget build(BuildContext context) {
    final size = widget.size ?? MediaQuery.of(context).size.width - 32;

    return Column(
      children: [
        // Grid visualization
        GestureDetector(
          onTapDown: widget.editingEnabled ? _handleTapDown : null,
          onPanStart: widget.editingEnabled ? _handlePanStart : null,
          onPanUpdate: widget.editingEnabled ? _handlePanUpdate : null,
          onPanEnd: widget.editingEnabled ? _handlePanEnd : null,
          child: SizedBox(
            width: size,
            height: size,
            child: CustomPaint(
              size: Size(size, size),
              painter: _VRIGridPainter(
                grid: _grid,
                selectedZones: _selectedZones,
              ),
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Controls
        if (widget.editingEnabled) ...[
          _buildRateSelector(),
          const SizedBox(height: 12),
          _buildQuickActions(),
          const SizedBox(height: 12),
        ],

        // Statistics
        _buildStatistics(),

        // Legend
        const SizedBox(height: 12),
        _buildLegend(),
      ],
    );
  }

  Widget _buildRateSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'معدل التطبيق | Application Rate',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _getRateColor(_currentRate),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Text(
                  '${_currentRate.toInt()}%',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          SliderTheme(
            data: SliderTheme.of(context).copyWith(
              activeTrackColor: _getRateColor(_currentRate),
              inactiveTrackColor: _getRateColor(_currentRate).withOpacity(0.3),
              thumbColor: _getRateColor(_currentRate),
              trackHeight: 8,
            ),
            child: Slider(
              value: _currentRate,
              min: 0,
              max: 150,
              divisions: 30,
              onChanged: (value) {
                setState(() => _currentRate = value);
              },
            ),
          ),
          // Quick rate buttons
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [0, 50, 75, 100, 125, 150].map((rate) {
              final isSelected = _currentRate == rate;
              return GestureDetector(
                onTap: () => setState(() => _currentRate = rate.toDouble()),
                child: Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: isSelected
                        ? _getRateColor(rate.toDouble())
                        : Colors.white,
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(
                      color: _getRateColor(rate.toDouble()),
                    ),
                  ),
                  child: Text(
                    rate == 0 ? 'إيقاف' : '$rate%',
                    style: TextStyle(
                      fontSize: 11,
                      color: isSelected
                          ? Colors.white
                          : _getRateColor(rate.toDouble()),
                      fontWeight:
                          isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _ActionButton(
          icon: Icons.select_all,
          label: 'تحديد الكل',
          onPressed: _selectAllZones,
        ),
        _ActionButton(
          icon: Icons.deselect,
          label: 'إلغاء التحديد',
          onPressed: _clearSelection,
        ),
        _ActionButton(
          icon: Icons.format_paint,
          label: 'تطبيق على المحدد',
          onPressed: _selectedZones.isNotEmpty ? _applyRateToSelected : null,
          color: const Color(0xFF367C2B),
        ),
        _ActionButton(
          icon: Icons.restart_alt,
          label: 'إعادة ضبط',
          onPressed: _resetGrid,
          color: Colors.orange,
        ),
      ],
    );
  }

  Widget _buildStatistics() {
    final stats = VRIZoneStatistics.fromGrid(_grid);

    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF367C2B).withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _StatItem(
            icon: Icons.grid_on,
            label: 'المناطق',
            value: '${stats.totalZones}',
          ),
          _StatItem(
            icon: Icons.speed,
            label: 'المتوسط',
            value: '${stats.avgApplicationRate.toInt()}%',
          ),
          _StatItem(
            icon: Icons.water_drop,
            label: 'التوفير',
            value: '${stats.waterSavingsPercent.toInt()}%',
            color: Colors.blue,
          ),
          _StatItem(
            icon: Icons.block,
            label: 'متوقف',
            value: '${stats.offZones}',
            color: Colors.grey,
          ),
        ],
      ),
    );
  }

  Widget _buildLegend() {
    final items = [
      ('إيقاف', 0.0, Colors.grey),
      ('منخفض', 70.0, Colors.orange),
      ('عادي', 100.0, Colors.green),
      ('مرتفع', 130.0, Colors.blue),
    ];

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: items.map((item) {
        return Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 16,
              height: 16,
              decoration: BoxDecoration(
                color: item.$3,
                borderRadius: BorderRadius.circular(4),
              ),
            ),
            const SizedBox(width: 4),
            Text(
              item.$1,
              style: const TextStyle(fontSize: 11),
            ),
          ],
        );
      }).toList(),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Gesture Handlers
  // ═══════════════════════════════════════════════════════════════════════════

  void _handleTapDown(TapDownDetails details) {
    final size = widget.size ?? MediaQuery.of(context).size.width - 32;
    final zone = _getZoneAtPosition(details.localPosition, size);

    if (zone != null) {
      final zoneId = '${zone.spanNumber - 1}_${zone.zoneNumber - 1}';

      setState(() {
        if (_selectedZones.contains(zoneId)) {
          _selectedZones.remove(zoneId);
        } else {
          _selectedZones.add(zoneId);
        }
      });

      HapticFeedback.selectionClick();
    }
  }

  void _handlePanStart(DragStartDetails details) {
    _isMultiSelectMode = true;
  }

  void _handlePanUpdate(DragUpdateDetails details) {
    if (!_isMultiSelectMode) return;

    final size = widget.size ?? MediaQuery.of(context).size.width - 32;
    final zone = _getZoneAtPosition(details.localPosition, size);

    if (zone != null) {
      final zoneId = '${zone.spanNumber - 1}_${zone.zoneNumber - 1}';

      if (!_selectedZones.contains(zoneId)) {
        setState(() {
          _selectedZones.add(zoneId);
        });
        HapticFeedback.selectionClick();
      }
    }
  }

  void _handlePanEnd(DragEndDetails details) {
    _isMultiSelectMode = false;
  }

  SpanZone? _getZoneAtPosition(Offset position, double size) {
    final center = Offset(size / 2, size / 2);
    final maxRadius = size / 2 * 0.9;
    final minRadius = size / 2 * 0.15;

    final offset = position - center;
    final distance = offset.distance;

    // Check if within the ring
    if (distance < minRadius || distance > maxRadius) return null;

    // Calculate span index
    final spanWidth = (maxRadius - minRadius) / widget.spanCount;
    final spanIndex = ((distance - minRadius) / spanWidth).floor();

    if (spanIndex < 0 || spanIndex >= widget.spanCount) return null;

    // Calculate angle
    final angle =
        (math.atan2(offset.dy, offset.dx) * 180 / math.pi + 90 + 360) % 360;

    // Find zone at this angle
    if (spanIndex < _grid.grid.length) {
      for (final zone in _grid.grid[spanIndex]) {
        if (angle >= zone.startAngle && angle < zone.endAngle) {
          return zone;
        }
      }
    }

    return null;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Actions
  // ═══════════════════════════════════════════════════════════════════════════

  void _selectAllZones() {
    setState(() {
      _selectedZones.clear();
      for (int span = 0; span < _grid.spanCount; span++) {
        for (int angle = 0; angle < _grid.angularDivisions; angle++) {
          _selectedZones.add('${span}_$angle');
        }
      }
    });
  }

  void _clearSelection() {
    setState(() {
      _selectedZones.clear();
    });
  }

  void _applyRateToSelected() {
    if (_selectedZones.isEmpty) return;

    final newGrid = List<List<SpanZone>>.from(
      _grid.grid
          .map((span) => span.map((z) {
                final zoneId = '${z.spanNumber - 1}_${z.zoneNumber - 1}';
                if (_selectedZones.contains(zoneId)) {
                  return z.copyWith(
                    applicationRatePercent: _currentRate,
                    color: _getRateColorHex(_currentRate),
                  );
                }
                return z;
              }).toList())
          .toList(),
    );

    setState(() {
      _grid = _grid.copyWith(
        grid: newGrid,
        updatedAt: DateTime.now(),
      );
      _selectedZones.clear();
    });

    widget.onGridChanged(_grid);
    HapticFeedback.mediumImpact();
  }

  void _resetGrid() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إعادة ضبط الشبكة؟'),
        content: const Text('سيتم إعادة جميع المناطق إلى 100%'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _grid = VRIZoneGridBuilder.createUniformGrid(
                  pivotId: widget.pivotId,
                  spanCount: widget.spanCount,
                  angularDivisions: widget.angularDivisions,
                );
                _selectedZones.clear();
              });
              widget.onGridChanged(_grid);
            },
            child: const Text('إعادة ضبط'),
          ),
        ],
      ),
    );
  }

  Color _getRateColor(double rate) {
    if (rate <= 0) return Colors.grey;
    if (rate < 70) return Colors.orange;
    if (rate < 90) return Colors.amber;
    if (rate <= 110) return Colors.green;
    if (rate <= 130) return Colors.blue;
    return Colors.indigo;
  }

  String _getRateColorHex(double rate) {
    if (rate <= 0) return '#9E9E9E';
    if (rate < 70) return '#FF9800';
    if (rate < 90) return '#FFC107';
    if (rate <= 110) return '#4CAF50';
    if (rate <= 130) return '#2196F3';
    return '#3F51B5';
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Grid Painter
// ═══════════════════════════════════════════════════════════════════════════

class _VRIGridPainter extends CustomPainter {
  final VRIZoneGrid grid;
  final Set<String> selectedZones;

  _VRIGridPainter({
    required this.grid,
    required this.selectedZones,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final maxRadius = size.width / 2 * 0.9;
    final minRadius = size.width / 2 * 0.15;

    // Draw background
    _drawBackground(canvas, center, maxRadius);

    // Draw zones
    _drawZones(canvas, center, minRadius, maxRadius);

    // Draw center
    _drawCenter(canvas, center, minRadius);

    // Draw span labels
    _drawSpanLabels(canvas, center, minRadius, maxRadius);

    // Draw angle markers
    _drawAngleMarkers(canvas, center, maxRadius);
  }

  void _drawBackground(Canvas canvas, Offset center, double radius) {
    final bgPaint = Paint()
      ..color = Colors.grey[200]!
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius, bgPaint);
  }

  void _drawZones(
      Canvas canvas, Offset center, double minRadius, double maxRadius) {
    final spanWidth = (maxRadius - minRadius) / grid.spanCount;

    for (int spanIndex = 0; spanIndex < grid.grid.length; spanIndex++) {
      final innerRadius = minRadius + spanIndex * spanWidth;
      final outerRadius = innerRadius + spanWidth;

      for (final zone in grid.grid[spanIndex]) {
        final startAngle = _degreesToRadians(zone.startAngle - 90);
        final sweepAngle = _degreesToRadians(zone.endAngle - zone.startAngle);

        // Zone fill
        final zoneColor = _hexToColor(zone.color);
        final zonePaint = Paint()
          ..color = zoneColor
          ..style = PaintingStyle.fill;

        final path = Path();
        path.moveTo(
          center.dx + innerRadius * math.cos(startAngle),
          center.dy + innerRadius * math.sin(startAngle),
        );
        path.arcTo(
          Rect.fromCircle(center: center, radius: outerRadius),
          startAngle,
          sweepAngle,
          false,
        );
        path.arcTo(
          Rect.fromCircle(center: center, radius: innerRadius),
          startAngle + sweepAngle,
          -sweepAngle,
          false,
        );
        path.close();

        canvas.drawPath(path, zonePaint);

        // Zone border
        final borderPaint = Paint()
          ..color = Colors.white
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1;
        canvas.drawPath(path, borderPaint);

        // Selection highlight
        final zoneId = '${zone.spanNumber - 1}_${zone.zoneNumber - 1}';
        if (selectedZones.contains(zoneId)) {
          final highlightPaint = Paint()
            ..color = Colors.black.withOpacity(0.3)
            ..style = PaintingStyle.stroke
            ..strokeWidth = 3;
          canvas.drawPath(path, highlightPaint);
        }

        // Rate label for larger zones
        if (zone.endAngle - zone.startAngle >= 20) {
          _drawZoneLabel(canvas, center, innerRadius, outerRadius, zone);
        }
      }
    }
  }

  void _drawZoneLabel(
    Canvas canvas,
    Offset center,
    double innerRadius,
    double outerRadius,
    SpanZone zone,
  ) {
    final midAngle =
        _degreesToRadians((zone.startAngle + zone.endAngle) / 2 - 90);
    final midRadius = (innerRadius + outerRadius) / 2;

    final labelOffset = Offset(
      center.dx + midRadius * math.cos(midAngle),
      center.dy + midRadius * math.sin(midAngle),
    );

    final rate = zone.applicationRatePercent;
    final text = rate == 0 ? 'X' : '${rate.toInt()}';

    final textPainter = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: rate == 0 ? Colors.red : Colors.white,
          fontSize: 10,
          fontWeight: FontWeight.bold,
          shadows: const [Shadow(blurRadius: 2, color: Colors.black54)],
        ),
      ),
      textDirection: TextDirection.ltr,
    );

    textPainter.layout();
    textPainter.paint(
      canvas,
      labelOffset - Offset(textPainter.width / 2, textPainter.height / 2),
    );
  }

  void _drawCenter(Canvas canvas, Offset center, double radius) {
    final centerPaint = Paint()
      ..color = Colors.grey[700]!
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius - 2, centerPaint);

    final dotPaint = Paint()
      ..color = const Color(0xFF367C2B)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, 8, dotPaint);
  }

  void _drawSpanLabels(
      Canvas canvas, Offset center, double minRadius, double maxRadius) {
    final spanWidth = (maxRadius - minRadius) / grid.spanCount;

    for (int i = 0; i < grid.spanCount; i++) {
      final radius = minRadius + (i + 0.5) * spanWidth;
      final labelOffset = Offset(center.dx + radius, center.dy - 5);

      final textPainter = TextPainter(
        text: TextSpan(
          text: 'T${i + 1}',
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 8,
            fontWeight: FontWeight.bold,
          ),
        ),
        textDirection: TextDirection.ltr,
      );

      textPainter.layout();
      textPainter.paint(canvas, labelOffset);
    }
  }

  void _drawAngleMarkers(Canvas canvas, Offset center, double radius) {
    final markerPaint = Paint()
      ..color = Colors.grey[400]!
      ..strokeWidth = 1;

    for (int deg = 0; deg < 360; deg += 45) {
      final angle = _degreesToRadians(deg - 90);
      final start = Offset(
        center.dx + (radius - 5) * math.cos(angle),
        center.dy + (radius - 5) * math.sin(angle),
      );
      final end = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );
      canvas.drawLine(start, end, markerPaint);
    }
  }

  double _degreesToRadians(double degrees) => degrees * math.pi / 180;

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }

  @override
  bool shouldRepaint(covariant _VRIGridPainter oldDelegate) {
    return oldDelegate.grid != grid ||
        oldDelegate.selectedZones != selectedZones;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════

class _ActionButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;
  final Color? color;

  const _ActionButton({
    required this.icon,
    required this.label,
    this.onPressed,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final buttonColor = color ?? Colors.grey[700]!;
    final isEnabled = onPressed != null;

    return GestureDetector(
      onTap: onPressed,
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.4,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: buttonColor.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(icon, color: buttonColor, size: 20),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                color: isEnabled ? Colors.grey[700] : Colors.grey[400],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color? color;

  const _StatItem({
    required this.icon,
    required this.label,
    required this.value,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final itemColor = color ?? const Color(0xFF367C2B);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: itemColor, size: 18),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: itemColor,
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
    );
  }
}
