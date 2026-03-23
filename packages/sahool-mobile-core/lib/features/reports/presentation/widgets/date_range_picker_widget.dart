/// Date Range Picker Widget - ودجت اختيار نطاق التاريخ
/// Reusable date range picker with preset options
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_filter.dart';

/// Date Range Picker Widget
/// ودجت اختيار نطاق التاريخ
class DateRangePickerWidget extends StatefulWidget {
  final DateRangePreset selectedPreset;
  final DateRange dateRange;
  final Function(DateRangePreset) onPresetChanged;
  final Function(DateRange) onDateRangeChanged;
  final bool showPresets;
  final bool compactMode;

  const DateRangePickerWidget({
    super.key,
    required this.selectedPreset,
    required this.dateRange,
    required this.onPresetChanged,
    required this.onDateRangeChanged,
    this.showPresets = true,
    this.compactMode = false,
  });

  @override
  State<DateRangePickerWidget> createState() => _DateRangePickerWidgetState();
}

class _DateRangePickerWidgetState extends State<DateRangePickerWidget> {
  late DateRangePreset _selectedPreset;
  late DateRange _dateRange;

  final List<DateRangePreset> _commonPresets = [
    DateRangePreset.last7Days,
    DateRangePreset.last30Days,
    DateRangePreset.thisMonth,
    DateRangePreset.last90Days,
    DateRangePreset.thisYear,
    DateRangePreset.custom,
  ];

  @override
  void initState() {
    super.initState();
    _selectedPreset = widget.selectedPreset;
    _dateRange = widget.dateRange;
  }

  @override
  void didUpdateWidget(DateRangePickerWidget oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.selectedPreset != widget.selectedPreset) {
      _selectedPreset = widget.selectedPreset;
    }
    if (oldWidget.dateRange != widget.dateRange) {
      _dateRange = widget.dateRange;
    }
  }

  void _selectPreset(DateRangePreset preset) {
    setState(() {
      _selectedPreset = preset;
      if (preset != DateRangePreset.custom) {
        _dateRange = preset.toDateRange();
      }
    });
    widget.onPresetChanged(preset);
    if (preset != DateRangePreset.custom) {
      widget.onDateRangeChanged(_dateRange);
    }
  }

  Future<void> _showCustomDatePicker() async {
    final picked = await showDateRangePicker(
      context: context,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      initialDateRange: DateTimeRange(
        start: _dateRange.start,
        end: _dateRange.end,
      ),
      locale: const Locale('ar'),
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: Theme(
            data: Theme.of(context).copyWith(
              colorScheme: const ColorScheme.light(
                primary: SahoolColors.primary,
                onPrimary: Colors.white,
                surface: Colors.white,
                onSurface: SahoolColors.textDark,
              ),
            ),
            child: child!,
          ),
        );
      },
    );

    if (picked != null) {
      final newRange = DateRange(
        start: picked.start,
        end: picked.end,
      );
      setState(() {
        _selectedPreset = DateRangePreset.custom;
        _dateRange = newRange;
      });
      widget.onPresetChanged(DateRangePreset.custom);
      widget.onDateRangeChanged(newRange);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (widget.compactMode) {
      return _buildCompactPicker();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Preset chips
        if (widget.showPresets) ...[
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _commonPresets.map((preset) {
              final isSelected = _selectedPreset == preset;
              return ChoiceChip(
                label: Text(preset.displayNameAr),
                selected: isSelected,
                onSelected: (_) => preset == DateRangePreset.custom
                    ? _showCustomDatePicker()
                    : _selectPreset(preset),
                selectedColor: SahoolColors.primary.withValues(alpha: 0.2),
                labelStyle: TextStyle(
                  color: isSelected ? SahoolColors.primary : Colors.grey[700],
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  fontSize: 12,
                ),
              );
            }).toList(),
          ),
          const SizedBox(height: 16),
        ],

        // Selected range display
        _buildDateRangeDisplay(),
      ],
    );
  }

  Widget _buildCompactPicker() {
    return InkWell(
      onTap: _showCustomDatePicker,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          border: Border.all(color: Colors.grey[300]!),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          children: [
            Icon(Icons.calendar_today, color: Colors.grey[600], size: 20),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    _selectedPreset.displayNameAr,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    _dateRange.formattedAr,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 12,
                    ),
                  ),
                ],
              ),
            ),
            Icon(Icons.arrow_drop_down, color: Colors.grey[600]),
          ],
        ),
      ),
    );
  }

  Widget _buildDateRangeDisplay() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.primary.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: SahoolColors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          // Start date
          Expanded(
            child: _buildDateColumn(
              label: 'من',
              date: _dateRange.start,
              onTap: () => _pickSingleDate(true),
            ),
          ),
          Container(
            width: 40,
            alignment: Alignment.center,
            child: Icon(
              Icons.arrow_forward,
              color: SahoolColors.primary.withValues(alpha: 0.5),
            ),
          ),
          // End date
          Expanded(
            child: _buildDateColumn(
              label: 'إلى',
              date: _dateRange.end,
              onTap: () => _pickSingleDate(false),
            ),
          ),
          // Duration
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            decoration: BoxDecoration(
              color: SahoolColors.primary.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              children: [
                Text(
                  '${_dateRange.days}',
                  style: const TextStyle(
                    color: SahoolColors.primary,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
                const Text(
                  'يوم',
                  style: TextStyle(
                    color: SahoolColors.primary,
                    fontSize: 11,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDateColumn({
    required String label,
    required DateTime date,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8),
      child: Padding(
        padding: const EdgeInsets.all(8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 11,
              ),
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Icon(
                  Icons.calendar_today,
                  size: 14,
                  color: SahoolColors.primary,
                ),
                const SizedBox(width: 6),
                Text(
                  _formatDate(date),
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
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

  Future<void> _pickSingleDate(bool isStartDate) async {
    final picked = await showDatePicker(
      context: context,
      initialDate: isStartDate ? _dateRange.start : _dateRange.end,
      firstDate: DateTime(2020),
      lastDate: DateTime.now().add(const Duration(days: 365)),
      locale: const Locale('ar'),
      builder: (context, child) {
        return Directionality(
          textDirection: TextDirection.rtl,
          child: Theme(
            data: Theme.of(context).copyWith(
              colorScheme: const ColorScheme.light(
                primary: SahoolColors.primary,
                onPrimary: Colors.white,
              ),
            ),
            child: child!,
          ),
        );
      },
    );

    if (picked != null) {
      DateRange newRange;
      if (isStartDate) {
        newRange = DateRange(
          start: picked,
          end: picked.isAfter(_dateRange.end) ? picked : _dateRange.end,
        );
      } else {
        newRange = DateRange(
          start: picked.isBefore(_dateRange.start) ? picked : _dateRange.start,
          end: picked,
        );
      }

      setState(() {
        _selectedPreset = DateRangePreset.custom;
        _dateRange = newRange;
      });
      widget.onPresetChanged(DateRangePreset.custom);
      widget.onDateRangeChanged(newRange);
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}

/// Quick Date Range Selector
/// محدد سريع لنطاق التاريخ
class QuickDateRangeSelector extends StatelessWidget {
  final DateRangePreset selectedPreset;
  final Function(DateRangePreset) onPresetChanged;

  const QuickDateRangeSelector({
    super.key,
    required this.selectedPreset,
    required this.onPresetChanged,
  });

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: DateRangePreset.values
            .where((p) => p != DateRangePreset.allTime)
            .map((preset) {
          final isSelected = selectedPreset == preset;
          return Padding(
            padding: const EdgeInsets.only(left: 8),
            child: ChoiceChip(
              label: Text(preset.displayNameAr),
              selected: isSelected,
              onSelected: (_) => onPresetChanged(preset),
              selectedColor: SahoolColors.primary.withValues(alpha: 0.2),
              labelStyle: TextStyle(
                color: isSelected ? SahoolColors.primary : Colors.grey[700],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                fontSize: 11,
              ),
              padding: const EdgeInsets.symmetric(horizontal: 8),
            ),
          );
        }).toList(),
      ),
    );
  }
}
