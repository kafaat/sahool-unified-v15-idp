/// Report Share Screen - شاشة مشاركة التقرير
/// Share reports via email, WhatsApp, and other platforms
library;

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../domain/models/report_data.dart';
import '../../state/reports_providers.dart';

/// Report Share Screen
/// شاشة مشاركة التقرير
class ReportShareScreen extends ConsumerStatefulWidget {
  final ReportData report;

  const ReportShareScreen({
    super.key,
    required this.report,
  });

  @override
  ConsumerState<ReportShareScreen> createState() => _ReportShareScreenState();
}

class _ReportShareScreenState extends ConsumerState<ReportShareScreen> {
  ExportFormat _selectedFormat = ExportFormat.pdf;
  bool _isExporting = false;
  String? _exportedFilePath;
  final _emailController = TextEditingController();
  final _messageController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _messageController.text = _getDefaultMessage();
  }

  String _getDefaultMessage() {
    return '''
مرحباً،

أرسل لك تقرير "${widget.report.titleAr}"
الفترة: ${widget.report.filter.dateRange.formattedAr}
تاريخ التوليد: ${_formatDate(widget.report.generatedAt)}

تحياتي،
منصة سهول للذكاء الزراعي
''';
  }

  @override
  void dispose() {
    _emailController.dispose();
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('مشاركة التقرير'),
          backgroundColor: SahoolColors.primary,
          foregroundColor: Colors.white,
        ),
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Report summary
              _buildReportSummary(),
              const SizedBox(height: 24),

              // Export format selection
              _buildFormatSelection(),
              const SizedBox(height: 24),

              // Share options
              _buildShareOptions(),
              const SizedBox(height: 24),

              // Email sharing
              _buildEmailSection(),
              const SizedBox(height: 24),

              // Custom message
              _buildMessageSection(),
              const SizedBox(height: 32),

              // Action buttons
              _buildActionButtons(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildReportSummary() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: SahoolColors.primary.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: const Icon(
                Icons.description,
                color: SahoolColors.primary,
                size: 28,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.report.titleAr,
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 16,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    widget.report.filter.dateRange.formattedAr,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Icon(
                        Icons.access_time,
                        size: 14,
                        color: Colors.grey[500],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        _formatDate(widget.report.generatedAt),
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.grey[500],
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFormatSelection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'صيغة الملف',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: _buildFormatCard(
                ExportFormat.pdf,
                'PDF',
                Icons.picture_as_pdf,
                Colors.red,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildFormatCard(
                ExportFormat.excel,
                'Excel',
                Icons.table_chart,
                Colors.green,
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: _buildFormatCard(
                ExportFormat.csv,
                'CSV',
                Icons.text_snippet,
                Colors.blue,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildFormatCard(
    ExportFormat format,
    String label,
    IconData icon,
    Color color,
  ) {
    final isSelected = _selectedFormat == format;

    return GestureDetector(
      onTap: () => setState(() => _selectedFormat = format),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: isSelected ? color.withOpacity(0.1) : Colors.grey[100],
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: isSelected ? color : Colors.transparent,
            width: 2,
          ),
        ),
        child: Column(
          children: [
            Icon(
              icon,
              color: isSelected ? color : Colors.grey[600],
              size: 32,
            ),
            const SizedBox(height: 8),
            Text(
              label,
              style: TextStyle(
                color: isSelected ? color : Colors.grey[600],
                fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildShareOptions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'طريقة المشاركة',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _buildShareOption(
              'واتساب',
              Icons.chat,
              const Color(0xFF25D366),
              _shareViaWhatsApp,
            ),
            _buildShareOption(
              'بريد',
              Icons.email,
              Colors.red,
              _shareViaEmail,
            ),
            _buildShareOption(
              'المزيد',
              Icons.share,
              Colors.grey,
              _shareGeneric,
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildShareOption(
    String label,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return GestureDetector(
      onTap: _isExporting ? null : onTap,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 28),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              color: Colors.grey[700],
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEmailSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'إرسال بالبريد الإلكتروني',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _emailController,
          keyboardType: TextInputType.emailAddress,
          decoration: InputDecoration(
            hintText: 'أدخل البريد الإلكتروني',
            prefixIcon: const Icon(Icons.email),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildMessageSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'رسالة مرفقة (اختياري)',
          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                fontWeight: FontWeight.bold,
              ),
        ),
        const SizedBox(height: 12),
        TextField(
          controller: _messageController,
          maxLines: 5,
          decoration: InputDecoration(
            hintText: 'أضف رسالة مع التقرير...',
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        if (_isExporting) ...[
          const LinearProgressIndicator(),
          const SizedBox(height: 16),
          Text(
            'جاري تجهيز التقرير...',
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
        ],
        Row(
          children: [
            Expanded(
              child: OutlinedButton.icon(
                onPressed: _isExporting ? null : () => Navigator.pop(context),
                icon: const Icon(Icons.close),
                label: const Text('إلغاء'),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              flex: 2,
              child: ElevatedButton.icon(
                onPressed: _isExporting ? null : _exportAndShare,
                icon: const Icon(Icons.send),
                label: const Text('تصدير ومشاركة'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),
          ],
        ),
      ],
    );
  }

  Future<String?> _exportReport() async {
    if (_exportedFilePath != null) return _exportedFilePath;

    setState(() => _isExporting = true);

    try {
      final repository = ref.read(reportsRepositoryProvider);
      String? filePath;

      switch (_selectedFormat) {
        case ExportFormat.pdf:
          filePath = await repository.exportToPdf(widget.report);
          break;
        case ExportFormat.excel:
          filePath = await repository.exportToExcel(widget.report);
          break;
        case ExportFormat.csv:
          filePath = await repository.exportToCsv(widget.report);
          break;
        default:
          filePath = await repository.exportToPdf(widget.report);
      }

      _exportedFilePath = filePath;
      return filePath;
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('فشل في تصدير التقرير: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
      return null;
    } finally {
      if (mounted) {
        setState(() => _isExporting = false);
      }
    }
  }

  Future<void> _shareViaWhatsApp() async {
    final filePath = await _exportReport();
    if (filePath == null) return;

    final message = _messageController.text;
    final encodedMessage = Uri.encodeComponent(message);
    final whatsappUrl = 'whatsapp://send?text=$encodedMessage';

    try {
      // First share the file
      await Share.shareXFiles(
        [XFile(filePath)],
        text: message,
      );
    } catch (e) {
      // Try opening WhatsApp with just the message
      if (await canLaunchUrl(Uri.parse(whatsappUrl))) {
        await launchUrl(Uri.parse(whatsappUrl));
      } else {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('تطبيق واتساب غير مثبت'),
              backgroundColor: Colors.orange,
            ),
          );
        }
      }
    }
  }

  Future<void> _shareViaEmail() async {
    final filePath = await _exportReport();
    if (filePath == null) return;

    final email = _emailController.text.trim();
    final message = _messageController.text;
    final subject = 'تقرير: ${widget.report.titleAr}';

    if (email.isNotEmpty) {
      final mailtoUrl = Uri(
        scheme: 'mailto',
        path: email,
        query: 'subject=${Uri.encodeComponent(subject)}&body=${Uri.encodeComponent(message)}',
      );

      if (await canLaunchUrl(mailtoUrl)) {
        await launchUrl(mailtoUrl);
      }
    }

    // Also share the file
    await Share.shareXFiles(
      [XFile(filePath)],
      subject: subject,
      text: message,
    );
  }

  Future<void> _shareGeneric() async {
    final filePath = await _exportReport();
    if (filePath == null) return;

    await Share.shareXFiles(
      [XFile(filePath)],
      subject: 'تقرير: ${widget.report.titleAr}',
      text: _messageController.text,
    );
  }

  Future<void> _exportAndShare() async {
    await _shareGeneric();
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }
}
