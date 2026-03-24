/// Sector Drawing Tool - أداة رسم القطاعات
/// Interactive tool for drawing and editing pivot sectors on a circular field
library;

import 'dart:math' as math;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../domain/models/pivot_models.dart';

/// Sector drawing tool widget
/// أداة رسم القطاعات التفاعلية
class SectorDrawingTool extends StatefulWidget {
  /// Initial sectors (optional)
  final List<PivotSector>? initialSectors;

  /// Pivot configuration for reference
  final PivotConfiguration? pivotConfig;

  /// Called when sectors change
  final Function(List<PivotSector>) onSectorsChanged;

  /// Widget size
  final double? size;

  /// Enable drawing mode
  final bool drawingEnabled;

  /// Show angle labels
  final bool showAngleLabels;

  /// Minimum sector angle in degrees
  final double minSectorAngle;

  const SectorDrawingTool({
    super.key,
    this.initialSectors,
    this.pivotConfig,
    required this.onSectorsChanged,
    this.size,
    this.drawingEnabled = true,
    this.showAngleLabels = true,
    this.minSectorAngle = 15,
  });

  @override
  State<SectorDrawingTool> createState() => _SectorDrawingToolState();
}

class _SectorDrawingToolState extends State<SectorDrawingTool> {
  late List<PivotSector> _sectors;
  int? _selectedSectorIndex;
  int? _draggingHandleIndex; // 0 = start, 1 = end
  Offset? _dragStart;
  bool _isAddingNewSector = false;
  double? _newSectorStartAngle;

  // Default sector colors
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

  @override
  void initState() {
    super.initState();
    _sectors = widget.initialSectors?.toList() ?? [];
  }

  @override
  void didUpdateWidget(SectorDrawingTool oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.initialSectors != oldWidget.initialSectors) {
      _sectors = widget.initialSectors?.toList() ?? [];
    }
  }

  @override
  Widget build(BuildContext context) {
    final size = widget.size ?? MediaQuery.of(context).size.width - 32;

    return Column(
      children: [
        // Drawing canvas
        GestureDetector(
          onTapDown: widget.drawingEnabled ? _handleTapDown : null,
          onPanStart: widget.drawingEnabled ? _handlePanStart : null,
          onPanUpdate: widget.drawingEnabled ? _handlePanUpdate : null,
          onPanEnd: widget.drawingEnabled ? _handlePanEnd : null,
          child: SizedBox(
            width: size,
            height: size,
            child: CustomPaint(
              size: Size(size, size),
              painter: _SectorDrawingPainter(
                sectors: _sectors,
                selectedSectorIndex: _selectedSectorIndex,
                draggingHandleIndex: _draggingHandleIndex,
                showAngleLabels: widget.showAngleLabels,
                isAddingNewSector: _isAddingNewSector,
                newSectorStartAngle: _newSectorStartAngle,
                drawingEnabled: widget.drawingEnabled,
              ),
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Control buttons
        if (widget.drawingEnabled) _buildControls(),

        const SizedBox(height: 12),

        // Sector list
        if (_sectors.isNotEmpty) _buildSectorList(),
      ],
    );
  }

  Widget _buildControls() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceEvenly,
        children: [
          // Add sector button
          _ControlButton(
            icon: Icons.add_circle_outline,
            label: 'إضافة قطاع',
            onPressed: _startAddingSector,
            isActive: _isAddingNewSector,
            activeColor: Colors.green,
          ),

          // Equal division button
          _ControlButton(
            icon: Icons.grid_view,
            label: 'تقسيم متساوي',
            onPressed: () => _showEqualDivisionDialog(),
          ),

          // Clear all button
          _ControlButton(
            icon: Icons.delete_outline,
            label: 'مسح الكل',
            onPressed: _sectors.isEmpty ? null : _clearAllSectors,
            activeColor: Colors.red,
          ),

          // Undo button
          _ControlButton(
            icon: Icons.undo,
            label: 'تراجع',
            onPressed: _sectors.isEmpty ? null : _undoLastSector,
          ),
        ],
      ),
    );
  }

  Widget _buildSectorList() {
    return Container(
      constraints: const BoxConstraints(maxHeight: 200),
      child: ListView.builder(
        shrinkWrap: true,
        itemCount: _sectors.length,
        itemBuilder: (context, index) {
          final sector = _sectors[index];
          final isSelected = index == _selectedSectorIndex;

          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            color: isSelected ? const Color(0xFF367C2B).withValues(alpha: 0.1) : null,
            child: ListTile(
              dense: true,
              leading: Container(
                width: 32,
                height: 32,
                decoration: BoxDecoration(
                  color: _hexToColor(sector.color),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Center(
                  child: Text(
                    '${sector.sectorNumber}',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                    ),
                  ),
                ),
              ),
              title: Text(
                'قطاع ${sector.sectorNumber}',
                style: const TextStyle(fontSize: 14),
              ),
              subtitle: Text(
                '${sector.startAngle.toInt()}° → ${sector.endAngle.toInt()}° (${(sector.endAngle - sector.startAngle).toInt()}°)',
                style: const TextStyle(fontSize: 11),
              ),
              trailing: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    icon: const Icon(Icons.edit, size: 18),
                    onPressed: () => _editSector(index),
                    tooltip: 'تعديل',
                  ),
                  IconButton(
                    icon: const Icon(Icons.delete, size: 18, color: Colors.red),
                    onPressed: () => _deleteSector(index),
                    tooltip: 'حذف',
                  ),
                ],
              ),
              onTap: () {
                setState(() {
                  _selectedSectorIndex = isSelected ? null : index;
                });
              },
            ),
          );
        },
      ),
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Gesture Handlers
  // ═══════════════════════════════════════════════════════════════════════════

  void _handleTapDown(TapDownDetails details) {
    final size = widget.size ?? MediaQuery.of(context).size.width - 32;
    final center = Offset(size / 2, size / 2);
    final radius = size / 2 * 0.85;

    final tapOffset = details.localPosition - center;
    final distance = tapOffset.distance;

    // Check if tap is within the circle
    if (distance > radius + 20) return;

    final angle = _offsetToAngle(tapOffset);

    if (_isAddingNewSector) {
      // First tap sets start angle
      if (_newSectorStartAngle == null) {
        setState(() {
          _newSectorStartAngle = angle;
        });
        HapticFeedback.lightImpact();
      } else {
        // Second tap sets end angle and creates sector
        _createSector(_newSectorStartAngle!, angle);
        setState(() {
          _isAddingNewSector = false;
          _newSectorStartAngle = null;
        });
        HapticFeedback.mediumImpact();
      }
    } else {
      // Check if tapping on a sector
      _selectSectorAtAngle(angle);
    }
  }

  void _handlePanStart(DragStartDetails details) {
    if (_selectedSectorIndex == null) return;

    final size = widget.size ?? MediaQuery.of(context).size.width - 32;
    final center = Offset(size / 2, size / 2);
    final tapOffset = details.localPosition - center;
    final angle = _offsetToAngle(tapOffset);

    final sector = _sectors[_selectedSectorIndex!];

    // Check if near start or end handle
    const handleThreshold = 10.0;
    final startDiff = _angleDifference(angle, sector.startAngle).abs();
    final endDiff = _angleDifference(angle, sector.endAngle).abs();

    if (startDiff < handleThreshold) {
      setState(() {
        _draggingHandleIndex = 0;
        _dragStart = details.localPosition;
      });
    } else if (endDiff < handleThreshold) {
      setState(() {
        _draggingHandleIndex = 1;
        _dragStart = details.localPosition;
      });
    }
  }

  void _handlePanUpdate(DragUpdateDetails details) {
    if (_selectedSectorIndex == null || _draggingHandleIndex == null) return;

    final size = widget.size ?? MediaQuery.of(context).size.width - 32;
    final center = Offset(size / 2, size / 2);
    final dragOffset = details.localPosition - center;
    final newAngle = _offsetToAngle(dragOffset);

    setState(() {
      final sector = _sectors[_selectedSectorIndex!];

      if (_draggingHandleIndex == 0) {
        // Dragging start handle
        final newStartAngle = _snapAngle(newAngle);
        if (_isValidAngleChange(sector, newStartAngle, sector.endAngle)) {
          _sectors[_selectedSectorIndex!] = sector.copyWith(
            startAngle: newStartAngle,
          );
        }
      } else {
        // Dragging end handle
        final newEndAngle = _snapAngle(newAngle);
        if (_isValidAngleChange(sector, sector.startAngle, newEndAngle)) {
          _sectors[_selectedSectorIndex!] = sector.copyWith(
            endAngle: newEndAngle,
          );
        }
      }
    });

    widget.onSectorsChanged(_sectors);
  }

  void _handlePanEnd(DragEndDetails details) {
    if (_draggingHandleIndex != null) {
      HapticFeedback.lightImpact();
    }
    setState(() {
      _draggingHandleIndex = null;
      _dragStart = null;
    });
    widget.onSectorsChanged(_sectors);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Sector Operations
  // ═══════════════════════════════════════════════════════════════════════════

  void _startAddingSector() {
    setState(() {
      _isAddingNewSector = !_isAddingNewSector;
      _newSectorStartAngle = null;
      _selectedSectorIndex = null;
    });
  }

  void _createSector(double startAngle, double endAngle) {
    // Normalize angles
    if (endAngle < startAngle) {
      // Swap if end is before start
      final temp = startAngle;
      startAngle = endAngle;
      endAngle = temp;
    }

    // Ensure minimum angle
    if ((endAngle - startAngle).abs() < widget.minSectorAngle) {
      endAngle = startAngle + widget.minSectorAngle;
    }

    final newSector = PivotSector(
      id: 'sector_${DateTime.now().millisecondsSinceEpoch}',
      sectorNumber: _sectors.length + 1,
      nameAr: 'قطاع ${_sectors.length + 1}',
      startAngle: startAngle,
      endAngle: endAngle,
      color: _defaultColors[_sectors.length % _defaultColors.length],
    );

    setState(() {
      _sectors.add(newSector);
      _selectedSectorIndex = _sectors.length - 1;
    });

    widget.onSectorsChanged(_sectors);
  }

  void _deleteSector(int index) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف القطاع؟'),
        content: Text('هل تريد حذف قطاع ${_sectors[index].sectorNumber}؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _sectors.removeAt(index);
                _renumberSectors();
                if (_selectedSectorIndex == index) {
                  _selectedSectorIndex = null;
                } else if (_selectedSectorIndex != null &&
                    _selectedSectorIndex! > index) {
                  _selectedSectorIndex = _selectedSectorIndex! - 1;
                }
              });
              widget.onSectorsChanged(_sectors);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }

  void _editSector(int index) {
    final sector = _sectors[index];

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => _SectorEditSheet(
        sector: sector,
        onSave: (updatedSector) {
          setState(() {
            _sectors[index] = updatedSector;
          });
          widget.onSectorsChanged(_sectors);
          Navigator.pop(context);
        },
      ),
    );
  }

  void _clearAllSectors() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('مسح جميع القطاعات؟'),
        content: const Text('سيتم حذف جميع القطاعات. هل أنت متأكد؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              setState(() {
                _sectors.clear();
                _selectedSectorIndex = null;
              });
              widget.onSectorsChanged(_sectors);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.red,
              foregroundColor: Colors.white,
            ),
            child: const Text('مسح الكل'),
          ),
        ],
      ),
    );
  }

  void _undoLastSector() {
    if (_sectors.isEmpty) return;

    setState(() {
      _sectors.removeLast();
      if (_selectedSectorIndex != null &&
          _selectedSectorIndex! >= _sectors.length) {
        _selectedSectorIndex = _sectors.isEmpty ? null : _sectors.length - 1;
      }
    });
    widget.onSectorsChanged(_sectors);
  }

  void _showEqualDivisionDialog() {
    int sectorCount = 8;

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setDialogState) => AlertDialog(
          title: const Text('تقسيم متساوي'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('اختر عدد القطاعات:'),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  IconButton(
                    icon: const Icon(Icons.remove_circle),
                    onPressed: sectorCount > 2
                        ? () => setDialogState(() => sectorCount--)
                        : null,
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 24,
                      vertical: 12,
                    ),
                    decoration: BoxDecoration(
                      color: const Color(0xFF367C2B).withValues(alpha: 0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '$sectorCount',
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF367C2B),
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.add_circle),
                    onPressed: sectorCount < 16
                        ? () => setDialogState(() => sectorCount++)
                        : null,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                'كل قطاع: ${(360 / sectorCount).toStringAsFixed(1)}°',
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                _createEqualSectors(sectorCount);
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
                foregroundColor: Colors.white,
              ),
              child: const Text('تطبيق'),
            ),
          ],
        ),
      ),
    );
  }

  void _createEqualSectors(int count) {
    final sectorAngle = 360.0 / count;

    setState(() {
      _sectors = List.generate(count, (i) {
        return PivotSector(
          id: 'sector_${i + 1}',
          sectorNumber: i + 1,
          nameAr: 'قطاع ${i + 1}',
          startAngle: i * sectorAngle,
          endAngle: (i + 1) * sectorAngle,
          color: _defaultColors[i % _defaultColors.length],
        );
      });
      _selectedSectorIndex = null;
    });

    widget.onSectorsChanged(_sectors);
    HapticFeedback.mediumImpact();
  }

  void _selectSectorAtAngle(double angle) {
    for (int i = 0; i < _sectors.length; i++) {
      final sector = _sectors[i];
      if (angle >= sector.startAngle && angle <= sector.endAngle) {
        setState(() {
          _selectedSectorIndex = (_selectedSectorIndex == i) ? null : i;
        });
        HapticFeedback.selectionClick();
        return;
      }
    }
    setState(() {
      _selectedSectorIndex = null;
    });
  }

  void _renumberSectors() {
    for (int i = 0; i < _sectors.length; i++) {
      _sectors[i] = _sectors[i].copyWith(
        sectorNumber: i + 1,
        nameAr: 'قطاع ${i + 1}',
      );
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  double _offsetToAngle(Offset offset) {
    final angle = math.atan2(offset.dy, offset.dx) * 180 / math.pi;
    return (angle + 90 + 360) % 360; // Normalize to 0-360, 0 at top
  }

  double _angleDifference(double a, double b) {
    var diff = (a - b) % 360;
    if (diff > 180) diff -= 360;
    if (diff < -180) diff += 360;
    return diff;
  }

  double _snapAngle(double angle) {
    // Snap to 5-degree increments
    return (angle / 5).round() * 5.0;
  }

  bool _isValidAngleChange(PivotSector sector, double start, double end) {
    // Ensure minimum angle
    if ((end - start).abs() < widget.minSectorAngle) return false;
    // Ensure end > start
    if (end <= start) return false;
    return true;
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Custom Painter
// ═══════════════════════════════════════════════════════════════════════════

class _SectorDrawingPainter extends CustomPainter {
  final List<PivotSector> sectors;
  final int? selectedSectorIndex;
  final int? draggingHandleIndex;
  final bool showAngleLabels;
  final bool isAddingNewSector;
  final double? newSectorStartAngle;
  final bool drawingEnabled;

  _SectorDrawingPainter({
    required this.sectors,
    this.selectedSectorIndex,
    this.draggingHandleIndex,
    required this.showAngleLabels,
    required this.isAddingNewSector,
    this.newSectorStartAngle,
    required this.drawingEnabled,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 * 0.85;

    // Draw background circle
    _drawBackgroundCircle(canvas, center, radius);

    // Draw sectors
    _drawSectors(canvas, center, radius);

    // Draw center point
    _drawCenterPoint(canvas, center);

    // Draw angle markers
    if (showAngleLabels) {
      _drawAngleMarkers(canvas, center, radius);
    }

    // Draw new sector preview
    if (isAddingNewSector && newSectorStartAngle != null) {
      _drawNewSectorPreview(canvas, center, radius);
    }

    // Draw handles for selected sector
    if (selectedSectorIndex != null && drawingEnabled) {
      _drawSectorHandles(canvas, center, radius);
    }

    // Draw instructions
    if (drawingEnabled) {
      _drawInstructions(canvas, center, radius);
    }
  }

  void _drawBackgroundCircle(Canvas canvas, Offset center, double radius) {
    // Outer circle
    final bgPaint = Paint()
      ..color = Colors.grey[200]!
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, radius, bgPaint);

    // Border
    final borderPaint = Paint()
      ..color = Colors.grey[400]!
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawCircle(center, radius, borderPaint);

    // Grid lines
    final gridPaint = Paint()
      ..color = Colors.grey[300]!
      ..strokeWidth = 1;

    for (int i = 0; i < 8; i++) {
      final angle = i * 45 * math.pi / 180 - math.pi / 2;
      final start = Offset(
        center.dx + 20 * math.cos(angle),
        center.dy + 20 * math.sin(angle),
      );
      final end = Offset(
        center.dx + radius * math.cos(angle),
        center.dy + radius * math.sin(angle),
      );
      canvas.drawLine(start, end, gridPaint);
    }
  }

  void _drawSectors(Canvas canvas, Offset center, double radius) {
    for (int i = 0; i < sectors.length; i++) {
      final sector = sectors[i];
      final isSelected = i == selectedSectorIndex;

      final startAngle = _degreesToRadians(sector.startAngle - 90);
      final sweepAngle = _degreesToRadians(sector.endAngle - sector.startAngle);

      // Sector fill
      final color = _hexToColor(sector.color);
      final sectorPaint = Paint()
        ..color = isSelected ? color : color.withValues(alpha: 0.7)
        ..style = PaintingStyle.fill;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        sectorPaint,
      );

      // Sector border
      final borderPaint = Paint()
        ..color = isSelected ? Colors.black : Colors.white
        ..style = PaintingStyle.stroke
        ..strokeWidth = isSelected ? 3 : 2;

      canvas.drawArc(
        Rect.fromCircle(center: center, radius: radius),
        startAngle,
        sweepAngle,
        true,
        borderPaint,
      );

      // Sector number label
      _drawSectorLabel(canvas, center, radius, sector);
    }
  }

  void _drawSectorLabel(
    Canvas canvas,
    Offset center,
    double radius,
    PivotSector sector,
  ) {
    final midAngle = _degreesToRadians(
      (sector.startAngle + sector.endAngle) / 2 - 90,
    );
    final labelRadius = radius * 0.6;

    final labelOffset = Offset(
      center.dx + labelRadius * math.cos(midAngle),
      center.dy + labelRadius * math.sin(midAngle),
    );

    final textPainter = TextPainter(
      text: TextSpan(
        text: '${sector.sectorNumber}',
        style: const TextStyle(
          color: Colors.white,
          fontSize: 16,
          fontWeight: FontWeight.bold,
          shadows: [Shadow(blurRadius: 3, color: Colors.black54)],
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

  void _drawCenterPoint(Canvas canvas, Offset center) {
    // Outer ring
    final outerPaint = Paint()
      ..color = Colors.grey[700]!
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, 15, outerPaint);

    // Inner dot
    final innerPaint = Paint()
      ..color = const Color(0xFF367C2B)
      ..style = PaintingStyle.fill;
    canvas.drawCircle(center, 8, innerPaint);
  }

  void _drawAngleMarkers(Canvas canvas, Offset center, double radius) {
    const angles = [0, 45, 90, 135, 180, 225, 270, 315];
    final labels = ['0°', '45°', '90°', '135°', '180°', '225°', '270°', '315°'];

    for (int i = 0; i < angles.length; i++) {
      final angle = _degreesToRadians(angles[i] - 90);
      final labelRadius = radius + 15;

      final labelOffset = Offset(
        center.dx + labelRadius * math.cos(angle),
        center.dy + labelRadius * math.sin(angle),
      );

      final textPainter = TextPainter(
        text: TextSpan(
          text: labels[i],
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 10,
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
  }

  void _drawSectorHandles(Canvas canvas, Offset center, double radius) {
    if (selectedSectorIndex == null || selectedSectorIndex! >= sectors.length) {
      return;
    }

    final sector = sectors[selectedSectorIndex!];
    const handleRadius = 12.0;

    // Start handle
    final startAngle = _degreesToRadians(sector.startAngle - 90);
    final startHandle = Offset(
      center.dx + radius * math.cos(startAngle),
      center.dy + radius * math.sin(startAngle),
    );

    final startHandlePaint = Paint()
      ..color = draggingHandleIndex == 0 ? Colors.orange : Colors.blue
      ..style = PaintingStyle.fill;
    canvas.drawCircle(startHandle, handleRadius, startHandlePaint);

    // End handle
    final endAngle = _degreesToRadians(sector.endAngle - 90);
    final endHandle = Offset(
      center.dx + radius * math.cos(endAngle),
      center.dy + radius * math.sin(endAngle),
    );

    final endHandlePaint = Paint()
      ..color = draggingHandleIndex == 1 ? Colors.orange : Colors.green
      ..style = PaintingStyle.fill;
    canvas.drawCircle(endHandle, handleRadius, endHandlePaint);

    // Handle borders
    final borderPaint = Paint()
      ..color = Colors.white
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2;
    canvas.drawCircle(startHandle, handleRadius, borderPaint);
    canvas.drawCircle(endHandle, handleRadius, borderPaint);
  }

  void _drawNewSectorPreview(Canvas canvas, Offset center, double radius) {
    if (newSectorStartAngle == null) return;

    final startAngle = _degreesToRadians(newSectorStartAngle! - 90);

    // Draw start line
    final startLinePaint = Paint()
      ..color = Colors.green
      ..strokeWidth = 3
      ..style = PaintingStyle.stroke;

    canvas.drawLine(
      center,
      Offset(
        center.dx + radius * math.cos(startAngle),
        center.dy + radius * math.sin(startAngle),
      ),
      startLinePaint,
    );

    // Draw start point
    final startPoint = Offset(
      center.dx + radius * math.cos(startAngle),
      center.dy + radius * math.sin(startAngle),
    );
    canvas.drawCircle(
      startPoint,
      8,
      Paint()..color = Colors.green,
    );
  }

  void _drawInstructions(Canvas canvas, Offset center, double radius) {
    if (!isAddingNewSector) return;

    String text;
    if (newSectorStartAngle == null) {
      text = 'انقر لتحديد بداية القطاع';
    } else {
      text = 'انقر لتحديد نهاية القطاع';
    }

    final textPainter = TextPainter(
      text: TextSpan(
        text: text,
        style: TextStyle(
          color: Colors.grey[700],
          fontSize: 12,
          fontWeight: FontWeight.bold,
          backgroundColor: Colors.white.withValues(alpha: 0.8),
        ),
      ),
      textDirection: TextDirection.rtl,
    );

    textPainter.layout();
    textPainter.paint(
      canvas,
      Offset(
        center.dx - textPainter.width / 2,
        center.dy + radius + 35,
      ),
    );
  }

  double _degreesToRadians(double degrees) => degrees * math.pi / 180;

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }

  @override
  bool shouldRepaint(covariant _SectorDrawingPainter oldDelegate) {
    return oldDelegate.sectors != sectors ||
        oldDelegate.selectedSectorIndex != selectedSectorIndex ||
        oldDelegate.draggingHandleIndex != draggingHandleIndex ||
        oldDelegate.newSectorStartAngle != newSectorStartAngle ||
        oldDelegate.isAddingNewSector != isAddingNewSector;
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Widgets
// ═══════════════════════════════════════════════════════════════════════════

class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback? onPressed;
  final bool isActive;
  final Color? activeColor;

  const _ControlButton({
    required this.icon,
    required this.label,
    this.onPressed,
    this.isActive = false,
    this.activeColor,
  });

  @override
  Widget build(BuildContext context) {
    final color = activeColor ?? const Color(0xFF367C2B);
    final isEnabled = onPressed != null;

    return GestureDetector(
      onTap: onPressed,
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.4,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isActive ? color : color.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                color: isActive ? Colors.white : color,
                size: 20,
              ),
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

class _SectorEditSheet extends StatefulWidget {
  final PivotSector sector;
  final Function(PivotSector) onSave;

  const _SectorEditSheet({
    required this.sector,
    required this.onSave,
  });

  @override
  State<_SectorEditSheet> createState() => _SectorEditSheetState();
}

class _SectorEditSheetState extends State<_SectorEditSheet> {
  late TextEditingController _nameController;
  late double _startAngle;
  late double _endAngle;
  late String _color;

  static const List<String> _colors = [
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

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.sector.nameAr);
    _startAngle = widget.sector.startAngle;
    _endAngle = widget.sector.endAngle;
    _color = widget.sector.color;
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Padding(
        padding: EdgeInsets.only(
          left: 20,
          right: 20,
          top: 20,
          bottom: MediaQuery.of(context).viewInsets.bottom + 20,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
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

            // Title
            Text(
              'تعديل قطاع ${widget.sector.sectorNumber}',
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 20),

            // Name field
            TextField(
              controller: _nameController,
              decoration: InputDecoration(
                labelText: 'اسم القطاع',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Angle fields
            Row(
              children: [
                Expanded(
                  child: TextField(
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: 'زاوية البداية',
                      suffixText: '°',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    controller: TextEditingController(
                      text: _startAngle.toInt().toString(),
                    ),
                    onChanged: (value) {
                      final parsed = double.tryParse(value);
                      if (parsed != null) {
                        setState(() => _startAngle = parsed.clamp(0, 359));
                      }
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: TextField(
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: 'زاوية النهاية',
                      suffixText: '°',
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                    controller: TextEditingController(
                      text: _endAngle.toInt().toString(),
                    ),
                    onChanged: (value) {
                      final parsed = double.tryParse(value);
                      if (parsed != null) {
                        setState(() => _endAngle = parsed.clamp(1, 360));
                      }
                    },
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Color picker
            const Text(
              'لون القطاع',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: _colors.map((color) {
                final isSelected = color.toLowerCase() == _color.toLowerCase();
                return GestureDetector(
                  onTap: () => setState(() => _color = color),
                  child: Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      color: _hexToColor(color),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(
                        color: isSelected ? Colors.black : Colors.transparent,
                        width: 3,
                      ),
                    ),
                    child: isSelected
                        ? const Icon(Icons.check, color: Colors.white, size: 20)
                        : null,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 24),

            // Save button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  widget.onSave(widget.sector.copyWith(
                    nameAr: _nameController.text,
                    startAngle: _startAngle,
                    endAngle: _endAngle,
                    color: _color,
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
                child: const Text('حفظ التغييرات'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Color _hexToColor(String hex) {
    hex = hex.replaceFirst('#', '');
    if (hex.length == 6) hex = 'FF$hex';
    return Color(int.parse(hex, radix: 16));
  }
}
