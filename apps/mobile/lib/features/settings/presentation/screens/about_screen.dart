import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../../core/config/theme.dart';
import '../widgets/widgets.dart';

/// About Screen
/// شاشة حول التطبيق
class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  static const String appVersion = '16.0.0';
  static const String buildNumber = '2026.01.23';
  static const String appName = 'سهول';
  static const String appNameEn = 'SAHOOL';
  static const String companyName = 'كفاءات';
  static const String companyNameEn = 'KAFAAT';

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'حول التطبيق',
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
            // App Logo and Info
            _AppLogoSection(),

            // Version Info
            const SettingsSection(
              title: 'Version',
              titleAr: 'معلومات الإصدار',
              icon: Icons.info_outline,
              showDividers: true,
              children: [
                _InfoTile(
                  label: 'الإصدار',
                  value: appVersion,
                  icon: Icons.numbers,
                ),
                _InfoTile(
                  label: 'رقم البناء',
                  value: buildNumber,
                  icon: Icons.build,
                ),
                _InfoTile(
                  label: 'النظام',
                  value: 'Android 14 / iOS 17',
                  icon: Icons.phone_android,
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
                  title: 'Terms of Service',
                  titleAr: 'شروط الخدمة',
                  icon: Icons.description_rounded,
                  onTap: () => _showLegalDocument(context, 'شروط الخدمة'),
                ),
                SettingsTile(
                  title: 'Privacy Policy',
                  titleAr: 'سياسة الخصوصية',
                  icon: Icons.privacy_tip_rounded,
                  onTap: () => _showLegalDocument(context, 'سياسة الخصوصية'),
                ),
                SettingsTile(
                  title: 'Open Source Licenses',
                  titleAr: 'تراخيص المصادر المفتوحة',
                  icon: Icons.code_rounded,
                  onTap: () => _showLicenses(context),
                ),
              ],
            ),

            // Support Section
            SettingsSection(
              title: 'Support',
              titleAr: 'الدعم',
              icon: Icons.support_outlined,
              showDividers: true,
              children: [
                SettingsTile(
                  title: 'Contact Support',
                  titleAr: 'تواصل مع الدعم',
                  icon: Icons.headset_mic_rounded,
                  iconColor: SahoolTheme.info,
                  subtitle: 'support@sahool.app',
                  onTap: () => _contactSupport(context),
                ),
                SettingsTile(
                  title: 'Report a Bug',
                  titleAr: 'الإبلاغ عن مشكلة',
                  icon: Icons.bug_report_rounded,
                  iconColor: SahoolTheme.warning,
                  onTap: () => _reportBug(context),
                ),
                SettingsTile(
                  title: 'Request a Feature',
                  titleAr: 'اقتراح ميزة',
                  icon: Icons.lightbulb_rounded,
                  iconColor: SahoolTheme.success,
                  onTap: () => _requestFeature(context),
                ),
              ],
            ),

            // Rate & Share
            SettingsSection(
              title: 'Share',
              titleAr: 'المشاركة',
              icon: Icons.share_outlined,
              showDividers: true,
              children: [
                SettingsTile(
                  title: 'Rate App',
                  titleAr: 'قيّم التطبيق',
                  icon: Icons.star_rounded,
                  iconColor: Colors.amber,
                  subtitle: 'ساعدنا بتقييمك على المتجر',
                  onTap: () => _rateApp(context),
                ),
                SettingsTile(
                  title: 'Share App',
                  titleAr: 'شارك التطبيق',
                  icon: Icons.share_rounded,
                  iconColor: SahoolTheme.primary,
                  subtitle: 'أخبر أصدقاءك عن سهول',
                  onTap: () => _shareApp(context),
                ),
              ],
            ),

            // Social Media
            SettingsSection(
              title: 'Follow Us',
              titleAr: 'تابعنا',
              icon: Icons.public_outlined,
              children: [
                _SocialMediaRow(),
              ],
            ),

            // Developer Credits
            SettingsSection(
              title: 'Credits',
              titleAr: 'الفريق',
              icon: Icons.people_outline,
              children: [
                _CreditsTile(),
              ],
            ),

            // Copyright
            const SizedBox(height: 24),
            Center(
              child: Column(
                children: [
                  Text(
                    'صنع بـ ❤️ في اليمن',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey[600],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'جميع الحقوق محفوظة $companyName 2026',
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[500],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
  }

  void _showLegalDocument(BuildContext context, String title) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => _LegalDocumentScreen(title: title),
      ),
    );
  }

  void _showLicenses(BuildContext context) {
    showLicensePage(
      context: context,
      applicationName: appName,
      applicationVersion: appVersion,
      applicationIcon: const Icon(
        Icons.grass_rounded,
        size: 64,
        color: SahoolTheme.primary,
      ),
    );
  }

  void _contactSupport(BuildContext context) {
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
                'تواصل مع الدعم',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.email, color: SahoolTheme.info),
              title: const Text('البريد الإلكتروني'),
              subtitle: const Text('support@sahool.app'),
              onTap: () {
                Clipboard.setData(const ClipboardData(text: 'support@sahool.app'));
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('تم نسخ البريد الإلكتروني')),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.phone, color: SahoolTheme.success),
              title: const Text('الهاتف'),
              subtitle: const Text('+967 1 234 567'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.chat, color: SahoolTheme.primary),
              title: const Text('الدردشة المباشرة'),
              subtitle: const Text('متاح من 9 ص - 5 م'),
              onTap: () => Navigator.pop(context),
            ),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  void _reportBug(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('الإبلاغ عن مشكلة'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('صف المشكلة التي واجهتها:'),
            SizedBox(height: 16),
            TextField(
              maxLines: 4,
              decoration: InputDecoration(
                hintText: 'اكتب وصفاً تفصيلياً...',
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
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('شكراً! تم إرسال التقرير'),
                  backgroundColor: SahoolTheme.success,
                ),
              );
            },
            child: const Text('إرسال'),
          ),
        ],
      ),
    );
  }

  void _requestFeature(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('اقتراح ميزة'),
        content: const Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text('ما الميزة التي تود رؤيتها في التطبيق؟'),
            SizedBox(height: 16),
            TextField(
              maxLines: 4,
              decoration: InputDecoration(
                hintText: 'اكتب اقتراحك...',
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
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('شكراً! تم إرسال اقتراحك'),
                  backgroundColor: SahoolTheme.success,
                ),
              );
            },
            child: const Text('إرسال'),
          ),
        ],
      ),
    );
  }

  void _rateApp(BuildContext context) {
    // Open app store page
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فتح صفحة التطبيق في المتجر...')),
    );
  }

  void _shareApp(BuildContext context) {
    // Share app link
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('فتح المشاركة...')),
    );
  }
}

/// App Logo Section
class _AppLogoSection extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          // Logo
          Container(
            width: 100,
            height: 100,
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                begin: Alignment.topRight,
                end: Alignment.bottomLeft,
                colors: [
                  SahoolTheme.primary,
                  SahoolTheme.primaryDark,
                ],
              ),
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  color: SahoolTheme.primary.withOpacity(0.4),
                  blurRadius: 20,
                  offset: const Offset(0, 10),
                ),
              ],
            ),
            child: const Icon(
              Icons.grass_rounded,
              size: 56,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 20),
          // App Name
          const Text(
            'سهول',
            style: TextStyle(
              fontSize: 32,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'SAHOOL',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
              letterSpacing: 2,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            'منصة الذكاء الزراعي الوطنية',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 16),
          // Version badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(
              color: SahoolTheme.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'الإصدار ${AboutScreen.appVersion}',
              style: TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: SahoolTheme.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }
}

/// Info Tile
class _InfoTile extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;

  const _InfoTile({
    required this.label,
    required this.value,
    required this.icon,
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
              color: SahoolTheme.primary.withOpacity(isDark ? 0.2 : 0.1),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Icon(icon, color: SahoolTheme.primary, size: 22),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Text(
              label,
              style: TextStyle(
                fontSize: 15,
                color: isDark ? Colors.white : Colors.black87,
              ),
            ),
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 14,
              color: isDark ? Colors.grey[400] : Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

/// Social Media Row
class _SocialMediaRow extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return const Padding(
      padding: EdgeInsets.all(16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          _SocialButton(icon: Icons.language, label: 'الموقع'),
          SizedBox(width: 16),
          _SocialButton(icon: Icons.facebook, label: 'فيسبوك', color: Colors.blue),
          SizedBox(width: 16),
          _SocialButton(icon: Icons.camera_alt, label: 'إنستغرام', color: Colors.pink),
          SizedBox(width: 16),
          _SocialButton(icon: Icons.code, label: 'يوتيوب', color: Colors.red),
        ],
      ),
    );
  }
}

/// Social Button
class _SocialButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color? color;

  const _SocialButton({
    required this.icon,
    required this.label,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final effectiveColor = color ?? SahoolTheme.primary;

    return GestureDetector(
      onTap: () {},
      child: Column(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              color: effectiveColor.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: effectiveColor),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

/// Credits Tile
class _CreditsTile extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text(
            'تم تطوير هذا التطبيق بواسطة فريق كفاءات',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey[600],
            ),
          ),
          const SizedBox(height: 12),
          const Wrap(
            alignment: WrapAlignment.center,
            spacing: 8,
            runSpacing: 8,
            children: [
              _TechBadge(label: 'Flutter'),
              _TechBadge(label: 'Riverpod'),
              _TechBadge(label: 'Dart'),
              _TechBadge(label: 'SQLite'),
              _TechBadge(label: 'MapLibre'),
            ],
          ),
        ],
      ),
    );
  }
}

/// Tech Badge
class _TechBadge extends StatelessWidget {
  final String label;

  const _TechBadge({required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: Colors.grey.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.grey.withOpacity(0.2)),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 12,
          color: Colors.grey[700],
        ),
      ),
    );
  }
}

/// Legal Document Screen
class _LegalDocumentScreen extends StatelessWidget {
  final String title;

  const _LegalDocumentScreen({required this.title});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            title,
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
        body: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Text(
            _getSampleLegalText(title),
            style: TextStyle(
              fontSize: 14,
              height: 1.8,
              color: isDark ? Colors.grey[300] : Colors.grey[800],
            ),
          ),
        ),
      ),
    );
  }

  String _getSampleLegalText(String title) {
    return '''
$title

آخر تحديث: يناير 2026

1. مقدمة
مرحباً بك في تطبيق سهول. باستخدامك لهذا التطبيق، فإنك توافق على الالتزام بهذه الشروط والأحكام.

2. استخدام الخدمة
يجب استخدام التطبيق للأغراض الزراعية المشروعة فقط. يُحظر استخدام التطبيق لأي غرض غير قانوني.

3. الخصوصية
نحن نأخذ خصوصيتك على محمل الجد. يرجى مراجعة سياسة الخصوصية الخاصة بنا لمزيد من المعلومات.

4. البيانات
أنت تحتفظ بملكية بياناتك. نحن نستخدم بياناتك فقط لتحسين خدماتنا وتقديم نصائح زراعية أفضل.

5. المسؤولية
النصائح الزراعية المقدمة هي إرشادية فقط. يجب عليك دائماً استشارة خبير زراعي محلي للحصول على نصائح محددة.

6. التحديثات
قد نقوم بتحديث هذه الشروط من وقت لآخر. سنخطرك بأي تغييرات جوهرية.

7. الاتصال
للأسئلة حول هذه الشروط، يرجى التواصل معنا على:
support@sahool.app

شكراً لاستخدامك تطبيق سهول!
    ''';
  }
}
