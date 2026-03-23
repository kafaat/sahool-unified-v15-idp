/// Export Button Widget - ودجت زر التصدير
/// Reusable export button with format selection
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_data.dart';

/// Export Button Widget
/// ودجت زر التصدير
class ExportButton extends StatelessWidget {
  final ReportData report;
  final ExportFormat format;
  final bool isLoading;
  final VoidCallback onExport;
  final bool compact;

  const ExportButton({
    super.key,
    required this.report,
    required this.format,
    required this.isLoading,
    required this.onExport,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return _buildCompactButton();
    }

    return ElevatedButton.icon(
      onPressed: isLoading ? null : onExport,
      icon: isLoading
          ? const SizedBox(
              width: 16,
              height: 16,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : Icon(_getFormatIcon()),
      label: Text(_getFormatLabel()),
      style: ElevatedButton.styleFrom(
        backgroundColor: _getFormatColor().withOpacity(0.1),
        foregroundColor: _getFormatColor(),
        elevation: 0,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: _getFormatColor().withOpacity(0.3)),
        ),
      ),
    );
  }

  Widget _buildCompactButton() {
    return IconButton(
      onPressed: isLoading ? null : onExport,
      icon: isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : Icon(_getFormatIcon()),
      color: _getFormatColor(),
      style: IconButton.styleFrom(
        backgroundColor: _getFormatColor().withOpacity(0.1),
      ),
      tooltip: _getFormatLabel(),
    );
  }

  IconData _getFormatIcon() {
    switch (format) {
      case ExportFormat.pdf:
        return Icons.picture_as_pdf;
      case ExportFormat.excel:
        return Icons.table_chart;
      case ExportFormat.csv:
        return Icons.text_snippet;
      case ExportFormat.image:
        return Icons.image;
    }
  }

  String _getFormatLabel() {
    switch (format) {
      case ExportFormat.pdf:
        return 'PDF';
      case ExportFormat.excel:
        return 'Excel';
      case ExportFormat.csv:
        return 'CSV';
      case ExportFormat.image:
        return 'صورة';
    }
  }

  Color _getFormatColor() {
    switch (format) {
      case ExportFormat.pdf:
        return Colors.red;
      case ExportFormat.excel:
        return Colors.green;
      case ExportFormat.csv:
        return Colors.blue;
      case ExportFormat.image:
        return Colors.purple;
    }
  }
}

/// Export Menu Button
/// زر قائمة التصدير
class ExportMenuButton extends StatelessWidget {
  final ReportData report;
  final bool isLoading;
  final Function(ExportFormat) onExport;

  const ExportMenuButton({
    super.key,
    required this.report,
    required this.isLoading,
    required this.onExport,
  });

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<ExportFormat>(
      enabled: !isLoading,
      icon: isLoading
          ? const SizedBox(
              width: 24,
              height: 24,
              child: CircularProgressIndicator(strokeWidth: 2),
            )
          : const Icon(Icons.download),
      tooltip: 'تصدير',
      onSelected: onExport,
      itemBuilder: (context) => [
        _buildMenuItem(ExportFormat.pdf, 'PDF', Icons.picture_as_pdf, Colors.red),
        _buildMenuItem(ExportFormat.excel, 'Excel', Icons.table_chart, Colors.green),
        _buildMenuItem(ExportFormat.csv, 'CSV', Icons.text_snippet, Colors.blue),
      ],
    );
  }

  PopupMenuItem<ExportFormat> _buildMenuItem(
    ExportFormat format,
    String label,
    IconData icon,
    Color color,
  ) {
    return PopupMenuItem<ExportFormat>(
      value: format,
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Text(label),
        ],
      ),
    );
  }
}

/// Export Options Row
/// صف خيارات التصدير
class ExportOptionsRow extends StatelessWidget {
  final ReportData report;
  final bool isLoading;
  final Function(ExportFormat) onExport;

  const ExportOptionsRow({
    super.key,
    required this.report,
    required this.isLoading,
    required this.onExport,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _buildExportOption(
          ExportFormat.pdf,
          'PDF',
          Icons.picture_as_pdf,
          Colors.red,
        ),
        _buildExportOption(
          ExportFormat.excel,
          'Excel',
          Icons.table_chart,
          Colors.green,
        ),
        _buildExportOption(
          ExportFormat.csv,
          'CSV',
          Icons.text_snippet,
          Colors.blue,
        ),
      ],
    );
  }

  Widget _buildExportOption(
    ExportFormat format,
    String label,
    IconData icon,
    Color color,
  ) {
    return GestureDetector(
      onTap: isLoading ? null : () => onExport(format),
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: isLoading
                ? SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: color,
                    ),
                  )
                : Icon(icon, color: color, size: 24),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              color: Colors.grey[700],
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

/// Floating Export FAB
/// زر التصدير العائم
class ExportFab extends StatelessWidget {
  final VoidCallback onPressed;
  final bool isLoading;

  const ExportFab({
    super.key,
    required this.onPressed,
    this.isLoading = false,
  });

  @override
  Widget build(BuildContext context) {
    return FloatingActionButton.extended(
      onPressed: isLoading ? null : onPressed,
      backgroundColor: SahoolColors.primary,
      icon: isLoading
          ? const SizedBox(
              width: 20,
              height: 20,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: Colors.white,
              ),
            )
          : const Icon(Icons.download, color: Colors.white),
      label: Text(
        isLoading ? 'جاري التصدير...' : 'تصدير',
        style: const TextStyle(color: Colors.white),
      ),
    );
  }
}
