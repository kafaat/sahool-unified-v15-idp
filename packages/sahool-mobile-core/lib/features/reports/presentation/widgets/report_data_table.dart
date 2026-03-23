/// Report Data Table Widget - ودجت جدول بيانات التقرير
/// Reusable data table component for reports
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_data.dart';

/// Report Data Table Widget
/// ودجت جدول بيانات التقرير
class ReportDataTable extends StatefulWidget {
  final ReportTableData data;
  final bool showTotals;
  final bool isScrollable;
  final Function(int columnIndex, bool ascending)? onSort;

  const ReportDataTable({
    super.key,
    required this.data,
    this.showTotals = true,
    this.isScrollable = true,
    this.onSort,
  });

  @override
  State<ReportDataTable> createState() => _ReportDataTableState();
}

class _ReportDataTableState extends State<ReportDataTable> {
  int? _sortColumnIndex;
  bool _sortAscending = true;
  late List<List<String>> _sortedRows;

  @override
  void initState() {
    super.initState();
    _sortedRows = List.from(widget.data.rows);
  }

  @override
  void didUpdateWidget(ReportDataTable oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.data != widget.data) {
      _sortedRows = List.from(widget.data.rows);
      _sortColumnIndex = null;
      _sortAscending = true;
    }
  }

  void _sort(int columnIndex) {
    if (!widget.data.sortableColumns.contains(columnIndex)) return;

    setState(() {
      if (_sortColumnIndex == columnIndex) {
        _sortAscending = !_sortAscending;
      } else {
        _sortColumnIndex = columnIndex;
        _sortAscending = true;
      }

      _sortedRows.sort((a, b) {
        final aValue = a[columnIndex];
        final bValue = b[columnIndex];

        // Try numeric comparison first
        final aNum = double.tryParse(aValue.replaceAll(RegExp(r'[^0-9.-]'), ''));
        final bNum = double.tryParse(bValue.replaceAll(RegExp(r'[^0-9.-]'), ''));

        int result;
        if (aNum != null && bNum != null) {
          result = aNum.compareTo(bNum);
        } else {
          result = aValue.compareTo(bValue);
        }

        return _sortAscending ? result : -result;
      });
    });

    widget.onSort?.call(columnIndex, _sortAscending);
  }

  @override
  Widget build(BuildContext context) {
    if (widget.data.headers.isEmpty || widget.data.rows.isEmpty) {
      return _buildEmptyState();
    }

    final table = SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: DataTable(
        columnSpacing: 24,
        headingRowColor: WidgetStateProperty.all(
          SahoolColors.primary.withOpacity(0.05),
        ),
        headingTextStyle: const TextStyle(
          fontWeight: FontWeight.bold,
          color: SahoolColors.textDark,
        ),
        dataTextStyle: TextStyle(
          color: Colors.grey[700],
          fontSize: 13,
        ),
        border: TableBorder(
          horizontalInside: BorderSide(
            color: Colors.grey.withOpacity(0.1),
          ),
        ),
        sortColumnIndex: _sortColumnIndex,
        sortAscending: _sortAscending,
        columns: _buildColumns(),
        rows: _buildRows(),
      ),
    );

    if (widget.isScrollable) {
      return ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: table,
      );
    }

    return table;
  }

  List<DataColumn> _buildColumns() {
    return widget.data.headersAr.asMap().entries.map((entry) {
      final index = entry.key;
      final header = entry.value;
      final isSortable = widget.data.sortableColumns.contains(index);

      return DataColumn(
        label: Expanded(
          child: Text(
            header,
            textAlign: TextAlign.right,
          ),
        ),
        onSort: isSortable ? (columnIndex, ascending) => _sort(columnIndex) : null,
      );
    }).toList();
  }

  List<DataRow> _buildRows() {
    final rows = <DataRow>[];

    // Data rows
    for (int i = 0; i < _sortedRows.length; i++) {
      final row = _sortedRows[i];
      rows.add(DataRow(
        color: i.isEven
            ? WidgetStateProperty.all(Colors.white)
            : WidgetStateProperty.all(Colors.grey.withOpacity(0.03)),
        cells: row.map((cell) => DataCell(
              Text(
                cell,
                textAlign: TextAlign.right,
              ),
            )).toList(),
      ));
    }

    // Totals row
    if (widget.showTotals && widget.data.totals != null) {
      rows.add(DataRow(
        color: WidgetStateProperty.all(
          SahoolColors.primary.withOpacity(0.1),
        ),
        cells: widget.data.totals!.map((cell) => DataCell(
              Text(
                cell,
                textAlign: TextAlign.right,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.primary,
                ),
              ),
            )).toList(),
      ));
    }

    return rows;
  }

  Widget _buildEmptyState() {
    return Container(
      height: 150,
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.table_chart, size: 48, color: Colors.grey[400]),
            const SizedBox(height: 8),
            Text(
              'لا توجد بيانات للعرض',
              style: TextStyle(color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }
}

/// Compact Table Widget for smaller data sets
/// ودجت جدول مضغوط
class CompactReportTable extends StatelessWidget {
  final List<String> headers;
  final List<String> headersAr;
  final List<List<String>> rows;

  const CompactReportTable({
    super.key,
    required this.headers,
    required this.headersAr,
    required this.rows,
  });

  @override
  Widget build(BuildContext context) {
    if (rows.isEmpty) {
      return const SizedBox.shrink();
    }

    return DecoratedBox(
      decoration: BoxDecoration(
        border: Border.all(color: Colors.grey.withOpacity(0.2)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Column(
          children: [
            // Header row
            Container(
              color: SahoolColors.primary.withOpacity(0.05),
              padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 16),
              child: Row(
                children: headersAr
                    .map((h) => Expanded(
                          child: Text(
                            h,
                            style: const TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 12,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ))
                    .toList(),
              ),
            ),
            // Data rows
            ...rows.asMap().entries.map((entry) {
              final index = entry.key;
              final row = entry.value;
              return Container(
                color: index.isEven ? Colors.white : Colors.grey.withOpacity(0.03),
                padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 16),
                child: Row(
                  children: row
                      .map((cell) => Expanded(
                            child: Text(
                              cell,
                              style: TextStyle(
                                fontSize: 12,
                                color: Colors.grey[700],
                              ),
                              textAlign: TextAlign.center,
                            ),
                          ))
                      .toList(),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}
