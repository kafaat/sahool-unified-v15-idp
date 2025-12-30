import 'package:flutter/material.dart';
import 'device_security_service.dart';

/// SAHOOL Security Warning Dialog
/// حوار تحذير الأمان
///
/// Dialog to show security warnings when device has non-critical security issues
/// Shows when SecurityAction is 'warn' instead of 'block'

/// Show security warning dialog
/// عرض حوار تحذير الأمان
Future<void> showSecurityWarningDialog({
  required BuildContext context,
  required DeviceSecurityResult result,
  bool isArabic = true,
  VoidCallback? onContinue,
  VoidCallback? onExit,
}) async {
  return showDialog(
    context: context,
    barrierDismissible: false,
    builder: (context) => SecurityWarningDialog(
      result: result,
      isArabic: isArabic,
      onContinue: onContinue,
      onExit: onExit,
    ),
  );
}

/// Security Warning Dialog Widget
class SecurityWarningDialog extends StatelessWidget {
  final DeviceSecurityResult result;
  final bool isArabic;
  final VoidCallback? onContinue;
  final VoidCallback? onExit;

  const SecurityWarningDialog({
    super.key,
    required this.result,
    this.isArabic = true,
    this.onContinue,
    this.onExit,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: AlertDialog(
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(20),
        ),
        title: Row(
          children: [
            Icon(
              Icons.warning_rounded,
              color: Colors.orange.shade700,
              size: 32,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                isArabic ? 'تحذير أمني' : 'Security Warning',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Colors.orange.shade700,
                ),
              ),
            ),
          ],
        ),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Main warning message
              Text(
                isArabic ? result.messageAr : result.messageEn,
                style: const TextStyle(
                  fontSize: 16,
                  color: Colors.black87,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 16),

              // Divider
              const Divider(),
              const SizedBox(height: 12),

              // Threat details
              Text(
                isArabic ? 'المشاكل المكتشفة:' : 'Issues Detected:',
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: Colors.black87,
                ),
              ),
              const SizedBox(height: 8),

              ...result.threats.map((threat) => Padding(
                    padding: const EdgeInsets.only(bottom: 6.0),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(
                          _getSeverityIcon(threat.severity),
                          size: 18,
                          color: _getSeverityColor(threat.severity),
                        ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            isArabic ? threat.messageAr : threat.messageEn,
                            style: const TextStyle(
                              fontSize: 13,
                              color: Colors.black87,
                            ),
                          ),
                        ),
                      ],
                    ),
                  )),

              const SizedBox(height: 16),

              // Warning info
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.orange.shade50,
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.orange.shade200),
                ),
                child: Row(
                  children: [
                    Icon(
                      Icons.info_outline,
                      color: Colors.orange.shade700,
                      size: 20,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        isArabic
                            ? 'يمكنك الاستمرار، لكن قد تكون بياناتك معرضة للخطر.'
                            : 'You may continue, but your data may be at risk.',
                        style: TextStyle(
                          fontSize: 12,
                          color: Colors.orange.shade900,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        actions: [
          // Exit button
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              if (onExit != null) {
                onExit!();
              }
            },
            child: Text(
              isArabic ? 'خروج' : 'Exit',
              style: const TextStyle(
                fontSize: 16,
                color: Colors.grey,
              ),
            ),
          ),

          // Continue button
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop();
              if (onContinue != null) {
                onContinue!();
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: Colors.orange.shade700,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(8),
              ),
            ),
            child: Text(
              isArabic ? 'الاستمرار على مسؤوليتي' : 'Continue at My Risk',
              style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  IconData _getSeverityIcon(ThreatSeverity severity) {
    switch (severity) {
      case ThreatSeverity.low:
        return Icons.info_outline;
      case ThreatSeverity.medium:
        return Icons.warning_amber_rounded;
      case ThreatSeverity.high:
        return Icons.error_outline;
      case ThreatSeverity.critical:
        return Icons.dangerous_outlined;
    }
  }

  Color _getSeverityColor(ThreatSeverity severity) {
    switch (severity) {
      case ThreatSeverity.low:
        return Colors.blue.shade700;
      case ThreatSeverity.medium:
        return Colors.orange.shade700;
      case ThreatSeverity.high:
        return Colors.deepOrange.shade700;
      case ThreatSeverity.critical:
        return Colors.red.shade700;
    }
  }
}

/// Simplified security warning snackbar for quick notifications
/// شريط تحذير سريع
void showSecurityWarningSnackbar({
  required BuildContext context,
  required String message,
  bool isArabic = true,
  Duration duration = const Duration(seconds: 5),
}) {
  final snackBar = SnackBar(
    content: Row(
      children: [
        Icon(
          Icons.warning_rounded,
          color: Colors.white,
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            message,
            style: const TextStyle(
              fontSize: 14,
              color: Colors.white,
            ),
          ),
        ),
      ],
    ),
    backgroundColor: Colors.orange.shade700,
    behavior: SnackBarBehavior.floating,
    duration: duration,
    action: SnackBarAction(
      label: isArabic ? 'حسناً' : 'OK',
      textColor: Colors.white,
      onPressed: () {
        ScaffoldMessenger.of(context).hideCurrentSnackBar();
      },
    ),
  );

  ScaffoldMessenger.of(context).showSnackBar(snackBar);
}
