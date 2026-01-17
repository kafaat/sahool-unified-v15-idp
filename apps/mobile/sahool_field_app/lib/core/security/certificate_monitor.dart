import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'certificate_pinning_service.dart';
import 'certificate_config.dart';
import 'certificate_tools.dart';

/// Certificate Monitor Widget
/// واجهة مراقبة الشهادات
///
/// Debug-only widget to monitor certificate pinning status
/// Only shown in debug mode for security monitoring
class CertificateMonitorWidget extends StatefulWidget {
  final CertificatePinningService? pinningService;

  const CertificateMonitorWidget({
    Key? key,
    this.pinningService,
  }) : super(key: key);

  @override
  State<CertificateMonitorWidget> createState() =>
      _CertificateMonitorWidgetState();
}

class _CertificateMonitorWidgetState extends State<CertificateMonitorWidget> {
  bool _isExpanded = false;
  Map<String, List<CertificatePin>>? _pins;
  List<ExpiringPin>? _expiringPins;
  List<String>? _validationIssues;

  @override
  void initState() {
    super.initState();
    _loadCertificateStatus();
  }

  void _loadCertificateStatus() {
    if (widget.pinningService == null) return;

    // Get configured pins (you'd need to expose this from the service)
    // For now, use the config
    _pins = CertificateConfig.getProductionPins();
    _expiringPins = widget.pinningService!.getExpiringPins(daysThreshold: 60);
    _validationIssues = CertificateRotationHelper.validatePinConfiguration(_pins!);

    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    if (!kDebugMode) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.all(8),
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.security, color: Colors.blue),
            title: const Text('Certificate Pinning Status'),
            subtitle: Text(
              widget.pinningService != null ? 'Enabled' : 'Disabled',
              style: TextStyle(
                color: widget.pinningService != null
                    ? Colors.green
                    : Colors.orange,
                fontWeight: FontWeight.bold,
              ),
            ),
            trailing: IconButton(
              icon: Icon(_isExpanded ? Icons.expand_less : Icons.expand_more),
              onPressed: () {
                setState(() {
                  _isExpanded = !_isExpanded;
                });
              },
            ),
          ),
          if (_isExpanded) ...[
            const Divider(),
            _buildStatusSection(),
          ],
        ],
      ),
    );
  }

  Widget _buildStatusSection() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Validation Issues
          if (_validationIssues != null && _validationIssues!.isNotEmpty) ...[
            _buildSectionHeader('⚠️ Configuration Issues', Colors.orange),
            ..._validationIssues!.map((issue) => _buildIssueItem(issue)),
            const SizedBox(height: 16),
          ],

          // Expiring Pins
          if (_expiringPins != null && _expiringPins!.isNotEmpty) ...[
            _buildSectionHeader('⏰ Expiring Soon', Colors.orange),
            ..._expiringPins!.map((pin) => _buildExpiringPinItem(pin)),
            const SizedBox(height: 16),
          ],

          // Configured Domains
          if (_pins != null && _pins!.isNotEmpty) ...[
            _buildSectionHeader('🔒 Configured Domains', Colors.blue),
            ..._pins!.entries.map((entry) => _buildDomainItem(entry)),
          ],

          const SizedBox(height: 16),

          // Action Buttons
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _refreshStatus,
                  icon: const Icon(Icons.refresh, size: 18),
                  label: const Text('Refresh'),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: _testCertificates,
                  icon: const Icon(Icons.network_check, size: 18),
                  label: const Text('Test'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Text(
        title,
        style: TextStyle(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: color,
        ),
      ),
    );
  }

  Widget _buildIssueItem(String issue) {
    return Padding(
      padding: const EdgeInsets.only(left: 16, bottom: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('• ', style: TextStyle(color: Colors.orange)),
          Expanded(
            child: Text(
              issue,
              style: const TextStyle(fontSize: 12),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildExpiringPinItem(ExpiringPin pin) {
    return Padding(
      padding: const EdgeInsets.only(left: 16, bottom: 8),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            pin.domain,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
          ),
          Text(
            'Expires in ${pin.daysUntilExpiry} days',
            style: TextStyle(
              fontSize: 11,
              color: pin.daysUntilExpiry < 30 ? Colors.red : Colors.orange,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDomainItem(MapEntry<String, List<CertificatePin>> entry) {
    final validPins = entry.value.where((p) => !p.isExpired).length;
    final totalPins = entry.value.length;

    return Padding(
      padding: const EdgeInsets.only(left: 16, bottom: 8),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  entry.key,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 12,
                  ),
                ),
                Text(
                  '$validPins/$totalPins pins valid',
                  style: TextStyle(
                    fontSize: 11,
                    color: validPins > 0 ? Colors.green : Colors.red,
                  ),
                ),
              ],
            ),
          ),
          Icon(
            validPins > 0 ? Icons.check_circle : Icons.error,
            color: validPins > 0 ? Colors.green : Colors.red,
            size: 16,
          ),
        ],
      ),
    );
  }

  void _refreshStatus() {
    _loadCertificateStatus();
  }

  void _testCertificates() async {
    // Show loading dialog
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => const AlertDialog(
        content: Row(
          children: [
            CircularProgressIndicator(),
            SizedBox(width: 16),
            Text('Testing certificates...'),
          ],
        ),
      ),
    );

    try {
      // Test production endpoints
      final urls = [
        'https://api.sahool.app',
        'https://api-staging.sahool.app',
      ];

      final results = await getCertificateInfoBatch(urls);

      // Close loading dialog
      if (mounted) Navigator.of(context).pop();

      // Show results
      _showTestResults(results);
    } catch (e) {
      if (mounted) {
        Navigator.of(context).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error testing certificates: $e')),
        );
      }
    }
  }

  void _showTestResults(List<CertificateInfo> results) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Certificate Test Results'),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: results.map((info) {
              return Padding(
                padding: const EdgeInsets.only(bottom: 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      info.host,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Valid: ${info.isValid ? "✅" : "❌"}',
                      style: const TextStyle(fontSize: 12),
                    ),
                    Text(
                      'Expires: ${info.daysUntilExpiry} days',
                      style: const TextStyle(fontSize: 12),
                    ),
                    Text(
                      'SHA-256: ${info.sha256Fingerprint.substring(0, 20)}...',
                      style: const TextStyle(fontSize: 10),
                    ),
                  ],
                ),
              );
            }).toList(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () {
              // Copy configuration code
              final buffer = StringBuffer();
              for (final info in results) {
                buffer.writeln("'${info.host}': [");
                buffer.writeln('  CertificatePin(');
                buffer.writeln('    type: PinType.sha256,');
                buffer.writeln("    value: '${info.sha256Fingerprint}',");
                buffer.writeln('    expiryDate: DateTime(${info.validUntil.year}, ${info.validUntil.month}, ${info.validUntil.day}),');
                buffer.writeln('  ),');
                buffer.writeln('],');
              }

              if (kDebugMode) {
                debugPrint('=== Certificate Configuration ===');
                debugPrint(buffer.toString());
              }

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Configuration copied to debug console'),
                ),
              );
            },
            child: const Text('Copy Config'),
          ),
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}

/// Certificate Status Service
/// خدمة حالة الشهادات
///
/// Background service to monitor certificate status
class CertificateStatusService {
  final CertificatePinningService? pinningService;
  final Function(List<ExpiringPin>)? onExpiringPinsDetected;
  final Function(List<String>)? onValidationIssues;

  CertificateStatusService({
    this.pinningService,
    this.onExpiringPinsDetected,
    this.onValidationIssues,
  });

  /// Check certificate status
  /// Should be called periodically (e.g., daily)
  Future<CertificateStatus> checkStatus() async {
    if (pinningService == null) {
      return CertificateStatus(
        isEnabled: false,
        hasIssues: false,
      );
    }

    // Get expiring pins
    final expiringPins = pinningService!.getExpiringPins(daysThreshold: 30);

    // Validate configuration
    final pins = CertificateConfig.getProductionPins();
    final issues = CertificateRotationHelper.validatePinConfiguration(pins);

    // Notify callbacks
    if (expiringPins.isNotEmpty) {
      onExpiringPinsDetected?.call(expiringPins);
    }

    if (issues.isNotEmpty) {
      onValidationIssues?.call(issues);
    }

    return CertificateStatus(
      isEnabled: true,
      hasIssues: issues.isNotEmpty,
      expiringPins: expiringPins,
      validationIssues: issues,
    );
  }

  /// Log certificate status (for monitoring)
  void logStatus(CertificateStatus status) {
    if (!kDebugMode) return;

    debugPrint('═══════════════════════════════════════');
    debugPrint('Certificate Pinning Status');
    debugPrint('═══════════════════════════════════════');
    debugPrint('Enabled: ${status.isEnabled}');
    debugPrint('Has Issues: ${status.hasIssues}');
    debugPrint('Expiring Pins: ${status.expiringPins.length}');
    debugPrint('Validation Issues: ${status.validationIssues.length}');

    if (status.expiringPins.isNotEmpty) {
      debugPrint('\n⚠️ Expiring Soon:');
      for (final pin in status.expiringPins) {
        debugPrint('  - ${pin.domain}: ${pin.daysUntilExpiry} days');
      }
    }

    if (status.validationIssues.isNotEmpty) {
      debugPrint('\n❌ Issues:');
      for (final issue in status.validationIssues) {
        debugPrint('  - $issue');
      }
    }

    debugPrint('═══════════════════════════════════════\n');
  }
}

/// Certificate status data class
class CertificateStatus {
  final bool isEnabled;
  final bool hasIssues;
  final List<ExpiringPin> expiringPins;
  final List<String> validationIssues;

  CertificateStatus({
    required this.isEnabled,
    required this.hasIssues,
    this.expiringPins = const [],
    this.validationIssues = const [],
  });

  bool get hasExpiringPins => expiringPins.isNotEmpty;
  bool get needsAttention => hasIssues || hasExpiringPins;
}
