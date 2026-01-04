import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'device_integrity_service.dart';

/// Device Security Screen
/// شاشة أمان الجهاز
///
/// Displayed when device security check fails
/// Shows information about detected security threats
/// Provides option to exit the app or (in warn mode) continue with warning

class DeviceSecurityScreen extends StatelessWidget {
  final SecurityCheckResult securityResult;
  final bool isBlocked;
  final VoidCallback? onContinueAnyway;

  const DeviceSecurityScreen({
    super.key,
    required this.securityResult,
    required this.isBlocked,
    this.onContinueAnyway,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        backgroundColor: _getThreatLevelColor(securityResult.threatLevel),
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Security Icon
                Icon(
                  _getThreatLevelIcon(securityResult.threatLevel),
                  size: 100,
                  color: Colors.white,
                ),
                const SizedBox(height: 32),

                // Title
                Text(
                  isBlocked
                      ? (isArabic ? 'الجهاز غير آمن' : 'Unsafe Device')
                      : (isArabic ? 'تحذير أمني' : 'Security Warning'),
                  style: const TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                    fontFamily: 'IBMPlexSansArabic',
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),

                // Description
                Text(
                  isBlocked
                      ? (isArabic
                          ? 'عذراً، لا يمكن تشغيل التطبيق على هذا الجهاز'
                          : 'Sorry, this app cannot run on this device')
                      : (isArabic
                          ? 'تم اكتشاف مشاكل أمنية على جهازك'
                          : 'Security issues detected on your device'),
                  style: const TextStyle(
                    fontSize: 16,
                    color: Colors.white70,
                    fontFamily: 'IBMPlexSansArabic',
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),

                // Detected Threats
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(
                      color: Colors.white.withOpacity(0.2),
                      width: 1,
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isArabic ? 'التهديدات المكتشفة:' : 'Detected Threats:',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                      const SizedBox(height: 12),
                      ...securityResult.detectedThreats.map((threat) {
                        return Padding(
                          padding: const EdgeInsets.symmetric(vertical: 4),
                          child: Row(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Icon(
                                Icons.warning_amber_rounded,
                                size: 20,
                                color: Colors.white,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: Text(
                                  _translateThreat(threat, isArabic),
                                  style: const TextStyle(
                                    fontSize: 14,
                                    color: Colors.white,
                                    fontFamily: 'IBMPlexSansArabic',
                                  ),
                                ),
                              ),
                            ],
                          ),
                        );
                      }).toList(),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // Security Information
                Container(
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Column(
                    children: [
                      Icon(
                        Icons.info_outline,
                        color: Colors.white,
                        size: 24,
                      ),
                      const SizedBox(height: 8),
                      Text(
                        isArabic
                            ? 'لماذا يتم حظر التطبيق؟'
                            : 'Why is the app blocked?',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        isArabic
                            ? 'تم اكتشاف أن جهازك معدّل (روت أو جلبريك). الأجهزة المعدلة تشكل خطراً أمنياً على بياناتك الزراعية الحساسة.'
                            : 'Your device has been modified (rooted or jailbroken). Modified devices pose a security risk to your sensitive agricultural data.',
                        style: const TextStyle(
                          fontSize: 14,
                          color: Colors.white70,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 32),

                // Actions
                if (isBlocked) ...[
                  // Exit Button (for blocked mode)
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: () {
                        SystemNavigator.pop(); // Exit the app
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: _getThreatLevelColor(securityResult.threatLevel),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        isArabic ? 'إغلاق التطبيق' : 'Exit App',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                    ),
                  ),
                ] else ...[
                  // Continue Anyway Button (for warn mode)
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: onContinueAnyway,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.white,
                        foregroundColor: _getThreatLevelColor(securityResult.threatLevel),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                      ),
                      child: Text(
                        isArabic ? 'المتابعة على مسؤوليتي' : 'Continue Anyway',
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: TextButton(
                      onPressed: () {
                        SystemNavigator.pop(); // Exit the app
                      },
                      style: TextButton.styleFrom(
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: Text(
                        isArabic ? 'إغلاق التطبيق' : 'Exit App',
                        style: const TextStyle(
                          fontSize: 16,
                          fontFamily: 'IBMPlexSansArabic',
                        ),
                      ),
                    ),
                  ),
                ],

                const SizedBox(height: 24),

                // Device Info (for debugging)
                if (securityResult.deviceInfo.isNotEmpty)
                  Text(
                    '${securityResult.deviceInfo['platform']} - ${securityResult.deviceInfo['model'] ?? 'Unknown'}',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.white.withOpacity(0.5),
                      fontFamily: 'IBMPlexSansArabic',
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  /// Get color based on threat level
  Color _getThreatLevelColor(SecurityThreatLevel level) {
    switch (level) {
      case SecurityThreatLevel.critical:
        return const Color(0xFF8B0000); // Dark red
      case SecurityThreatLevel.high:
        return const Color(0xFFD32F2F); // Red
      case SecurityThreatLevel.medium:
        return const Color(0xFFFF9800); // Orange
      case SecurityThreatLevel.low:
        return const Color(0xFFFFA726); // Light orange
      case SecurityThreatLevel.none:
        return const Color(0xFF2E7D32); // Green
    }
  }

  /// Get icon based on threat level
  IconData _getThreatLevelIcon(SecurityThreatLevel level) {
    switch (level) {
      case SecurityThreatLevel.critical:
      case SecurityThreatLevel.high:
        return Icons.block;
      case SecurityThreatLevel.medium:
        return Icons.warning_amber_rounded;
      case SecurityThreatLevel.low:
        return Icons.info_outline;
      case SecurityThreatLevel.none:
        return Icons.check_circle_outline;
    }
  }

  /// Translate threat message to Arabic
  String _translateThreat(String threat, bool isArabic) {
    if (!isArabic) return threat;

    final translations = {
      'Debug mode active': 'وضع التطوير نشط',
      'Running on Android emulator': 'يعمل على محاكي أندرويد',
      'Running on iOS simulator': 'يعمل على محاكي iOS',
      'Android device is rooted': 'جهاز أندرويد به صلاحيات روت',
      'iOS device is jailbroken': 'جهاز iOS مكسور الحماية (جلبريك)',
      'Developer options enabled': 'خيارات المطور مفعّلة',
      'Frida or hooking framework detected': 'تم اكتشاف أدوات اختراق',
    };

    for (var entry in translations.entries) {
      if (threat.contains(entry.key)) {
        return entry.value;
      }
    }

    return threat;
  }
}
