import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../state/settings_providers.dart';
import '../widgets/widgets.dart';

/// Privacy Settings Screen
/// شاشة إعدادات الخصوصية
class PrivacySettingsScreen extends ConsumerWidget {
  const PrivacySettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final settings = ref.watch(appSettingsProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'الخصوصية',
            style: TextStyle(
              color: isDark ? Colors.white : Colors.black87,
              fontWeight: FontWeight.bold,
            ),
          ),
          centerTitle: true,
          leading: IconButton(
            icon: const Icon(Icons.arrow_forward_ios),
            color: isDark ? Colors.white : Colors.black87,
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: ListView(
          padding: const EdgeInsets.only(bottom: 32),
          children: [
            // Privacy notice
            Container(
              margin: const EdgeInsets.all(16),
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: SahoolTheme.info.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: SahoolTheme.info.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.privacy_tip_outlined,
                    color: SahoolTheme.info,
                    size: 32,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'خصوصيتك مهمة لنا',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 15,
                          ),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'نحن نجمع البيانات فقط لتحسين تجربتك. يمكنك التحكم في ما تشاركه.',
                          style: TextStyle(
                            fontSize: 13,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),

            // Data Collection Section
            SettingsSection(
              title: 'Data Collection',
              titleAr: 'جمع البيانات',
              icon: Icons.data_usage_outlined,
              showDividers: true,
              children: [
                DescriptiveSwitchTile(
                  titleAr: 'تحليلات الاستخدام',
                  description:
                      'يساعدنا جمع بيانات الاستخدام على فهم كيفية استخدامك للتطبيق وتحسين الميزات. لا نجمع بيانات شخصية.',
                  icon: Icons.analytics_rounded,
                  iconColor: SahoolTheme.info,
                  value: settings.analyticsEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setAnalyticsEnabled(value);
                  },
                ),
                DescriptiveSwitchTile(
                  titleAr: 'تقارير الأعطال',
                  description:
                      'إرسال تقارير الأعطال تلقائياً يساعدنا على إصلاح المشاكل بشكل أسرع. لا تتضمن التقارير بياناتك الشخصية.',
                  icon: Icons.bug_report_rounded,
                  iconColor: SahoolTheme.warning,
                  value: settings.crashReportingEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setCrashReportingEnabled(value);
                  },
                ),
                DescriptiveSwitchTile(
                  titleAr: 'جمع البيانات للتحسين',
                  description:
                      'السماح لنا بجمع بيانات مجهولة الهوية لتحسين خدماتنا ونصائحنا الزراعية.',
                  icon: Icons.science_rounded,
                  iconColor: SahoolTheme.success,
                  value: settings.dataCollectionEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setDataCollectionEnabled(value);
                  },
                ),
              ],
            ),

            // Location Section
            SettingsSection(
              title: 'Location',
              titleAr: 'الموقع',
              icon: Icons.location_on_outlined,
              children: [
                DescriptiveSwitchTile(
                  titleAr: 'مشاركة الموقع',
                  description:
                      'السماح بمشاركة موقع الحقول مع خدمات الطرف الثالث لتحسين التنبؤات الجوية وتحليل التربة.',
                  icon: Icons.share_location_rounded,
                  iconColor: Colors.orange,
                  value: settings.locationSharingEnabled,
                  onChanged: (value) {
                    ref.read(appSettingsProvider.notifier).setLocationSharingEnabled(value);
                  },
                ),
                SettingsTile(
                  title: 'Location Accuracy',
                  titleAr: 'دقة الموقع',
                  icon: Icons.gps_fixed_rounded,
                  subtitle: 'عالية الدقة',
                  onTap: () => _showLocationAccuracyDialog(context),
                ),
              ],
            ),

            // Third Party Section
            SettingsSection(
              title: 'Third Party Services',
              titleAr: 'خدمات الطرف الثالث',
              icon: Icons.extension_outlined,
              subtitle: 'التحكم في الخدمات الخارجية المرتبطة',
              showDividers: true,
              children: [
                _ThirdPartyServiceTile(
                  name: 'Google Analytics',
                  description: 'تحليل سلوك المستخدمين',
                  icon: Icons.analytics_outlined,
                  isEnabled: settings.analyticsEnabled,
                ),
                _ThirdPartyServiceTile(
                  name: 'Sentry',
                  description: 'مراقبة الأخطاء والأعطال',
                  icon: Icons.bug_report_outlined,
                  isEnabled: settings.crashReportingEnabled,
                ),
                const _ThirdPartyServiceTile(
                  name: 'Weather API',
                  description: 'بيانات الطقس والتنبؤات',
                  icon: Icons.cloud_outlined,
                  isEnabled: true,
                ),
                const _ThirdPartyServiceTile(
                  name: 'Satellite Imagery',
                  description: 'صور الأقمار الصناعية',
                  icon: Icons.satellite_alt_outlined,
                  isEnabled: true,
                ),
              ],
            ),

            // Data Management Section
            SettingsSection(
              title: 'Data Management',
              titleAr: 'إدارة البيانات',
              icon: Icons.folder_outlined,
              showDividers: true,
              children: [
                SettingsTile(
                  title: 'Download My Data',
                  titleAr: 'تنزيل بياناتي',
                  icon: Icons.download_rounded,
                  iconColor: SahoolTheme.info,
                  subtitle: 'تصدير نسخة من جميع بياناتك',
                  onTap: () => _showDownloadDataDialog(context),
                ),
                SettingsTile(
                  title: 'Delete All Data',
                  titleAr: 'حذف جميع البيانات',
                  icon: Icons.delete_sweep_rounded,
                  iconColor: SahoolTheme.error,
                  subtitle: 'حذف جميع بياناتك من خوادمنا',
                  onTap: () => _showDeleteDataDialog(context),
                ),
              ],
            ),

            // Legal Section
            SettingsSection(
              title: 'Legal',
              titleAr: 'قانوني',
              icon: Icons.gavel_outlined,
              showDividers: true,
              children: [
                SettingsTile(
                  title: 'Privacy Policy',
                  titleAr: 'سياسة الخصوصية',
                  icon: Icons.policy_rounded,
                  onTap: () => _openPrivacyPolicy(context),
                ),
                SettingsTile(
                  title: 'Terms of Service',
                  titleAr: 'شروط الخدمة',
                  icon: Icons.description_rounded,
                  onTap: () => _openTermsOfService(context),
                ),
                SettingsTile(
                  title: 'Data Processing Agreement',
                  titleAr: 'اتفاقية معالجة البيانات',
                  icon: Icons.handshake_rounded,
                  onTap: () => _openDPA(context),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showLocationAccuracyDialog(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => DecoratedBox(
        decoration: BoxDecoration(
          color: Theme.of(context).brightness == Brightness.dark
              ? Colors.grey[900]
              : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[400],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text(
                'دقة الموقع',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            const _LocationAccuracyOption(
              title: 'عالية الدقة',
              subtitle: 'GPS + شبكات (الأفضل للحقول)',
              isSelected: true,
            ),
            const _LocationAccuracyOption(
              title: 'منخفضة الطاقة',
              subtitle: 'شبكات فقط (يوفر البطارية)',
              isSelected: false,
            ),
            const _LocationAccuracyOption(
              title: 'تقريبية',
              subtitle: 'دقة أقل لحماية الخصوصية',
              isSelected: false,
            ),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  void _showDownloadDataDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تنزيل بياناتي'),
        content: const Text(
          'سنقوم بإعداد نسخة من جميع بياناتك.\n\n'
          'ستتلقى إشعاراً عندما يكون الملف جاهزاً للتنزيل (قد يستغرق ذلك حتى 24 ساعة).',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('تم طلب نسخة من بياناتك. سنرسل إشعاراً عند الجهوزية.'),
                  backgroundColor: SahoolTheme.success,
                ),
              );
            },
            child: const Text('طلب التنزيل'),
          ),
        ],
      ),
    );
  }

  void _showDeleteDataDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning_rounded, color: SahoolTheme.error),
            SizedBox(width: 8),
            Text('حذف جميع البيانات'),
          ],
        ),
        content: const Text(
          'تحذير: هذا الإجراء لا يمكن التراجع عنه!\n\n'
          'سيتم حذف جميع بياناتك من خوادمنا بما في ذلك:\n'
          '- بيانات الحقول والمزارع\n'
          '- سجل العمليات الزراعية\n'
          '- التقارير والتحليلات\n'
          '- الإعدادات والتفضيلات\n\n'
          'لن تتمكن من استعادة هذه البيانات.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _confirmDeleteData(context);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolTheme.error,
            ),
            child: const Text('متابعة'),
          ),
        ],
      ),
    );
  }

  void _confirmDeleteData(BuildContext context) {
    final controller = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تأكيد الحذف'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'للتأكيد، اكتب "حذف بياناتي" في الحقل أدناه:',
            ),
            const SizedBox(height: 16),
            TextField(
              controller: controller,
              decoration: const InputDecoration(
                hintText: 'حذف بياناتي',
                border: OutlineInputBorder(),
              ),
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
              if (controller.text == 'حذف بياناتي') {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم طلب حذف بياناتك. سيتم معالجة الطلب خلال 30 يوماً.'),
                    backgroundColor: SahoolTheme.warning,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolTheme.error,
            ),
            child: const Text('حذف نهائي'),
          ),
        ],
      ),
    );
  }

  void _openPrivacyPolicy(BuildContext context) {
    // Open privacy policy URL or show in-app
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فتح سياسة الخصوصية...')),
    );
  }

  void _openTermsOfService(BuildContext context) {
    // Open ToS URL or show in-app
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فتح شروط الخدمة...')),
    );
  }

  void _openDPA(BuildContext context) {
    // Open DPA URL or show in-app
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فتح اتفاقية معالجة البيانات...')),
    );
  }
}

/// Third Party Service Tile
class _ThirdPartyServiceTile extends StatelessWidget {
  final String name;
  final String description;
  final IconData icon;
  final bool isEnabled;

  const _ThirdPartyServiceTile({
    required this.name,
    required this.description,
    required this.icon,
    required this.isEnabled,
  });

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: (isEnabled ? SahoolTheme.success : Colors.grey)
                  .withValues(alpha: isDark ? 0.2 : 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(
              icon,
              color: isEnabled ? SahoolTheme.success : Colors.grey,
              size: 22,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: TextStyle(
                    fontSize: 15,
                    fontWeight: FontWeight.w500,
                    color: isDark ? Colors.white : Colors.black87,
                  ),
                ),
                Text(
                  description,
                  style: TextStyle(
                    fontSize: 13,
                    color: isDark ? Colors.grey[400] : Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: isEnabled
                  ? SahoolTheme.success.withValues(alpha: 0.1)
                  : Colors.grey.withValues(alpha: 0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              isEnabled ? 'نشط' : 'معطّل',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: isEnabled ? SahoolTheme.success : Colors.grey,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Location Accuracy Option
class _LocationAccuracyOption extends StatelessWidget {
  final String title;
  final String subtitle;
  final bool isSelected;

  const _LocationAccuracyOption({
    required this.title,
    required this.subtitle,
    required this.isSelected,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(
        isSelected ? Icons.radio_button_checked : Icons.radio_button_off,
        color: isSelected ? SahoolTheme.primary : Colors.grey,
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      onTap: () => Navigator.pop(context),
    );
  }
}
