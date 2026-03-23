import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../state/settings_providers.dart';
import '../../state/settings_controller.dart';
import '../widgets/widgets.dart';
import 'account_settings_screen.dart';
import 'notification_settings_screen.dart';
import 'appearance_settings_screen.dart';
import 'privacy_settings_screen.dart';
import 'sync_settings_screen.dart';
import 'about_screen.dart';
import 'help_screen.dart';

/// Main Settings Screen - Settings Hub
/// شاشة الإعدادات الرئيسية - مركز الإعدادات
class SettingsScreen extends ConsumerStatefulWidget {
  const SettingsScreen({super.key});

  @override
  ConsumerState<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends ConsumerState<SettingsScreen> {
  final TextEditingController _searchController = TextEditingController();
  bool _isSearching = false;

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(userProfileProvider);
    final settings = ref.watch(appSettingsProvider);
    final syncStatus = ref.watch(syncStatusProvider);
    final storageInfo = ref.watch(storageInfoProvider);
    final searchQuery = ref.watch(settingsSearchQueryProvider);

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: Theme.of(context).brightness == Brightness.dark
            ? Colors.black
            : Colors.grey[100],
        appBar: _buildAppBar(context),
        body: _isSearching && searchQuery.isNotEmpty
            ? _buildSearchResults(searchQuery)
            : _buildSettingsList(context, profile, settings, syncStatus, storageInfo),
      ),
    );
  }

  PreferredSizeWidget _buildAppBar(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    if (_isSearching) {
      return AppBar(
        backgroundColor: isDark ? Colors.grey[900] : Colors.white,
        elevation: 0,
        leading: IconButton(
          icon: const Icon(Icons.arrow_forward_ios),
          onPressed: () {
            setState(() => _isSearching = false);
            _searchController.clear();
            ref.read(settingsSearchQueryProvider.notifier).state = '';
          },
        ),
        title: TextField(
          controller: _searchController,
          autofocus: true,
          decoration: InputDecoration(
            hintText: 'ابحث في الإعدادات...',
            border: InputBorder.none,
            hintStyle: TextStyle(color: Colors.grey[500]),
          ),
          onChanged: (value) {
            ref.read(settingsSearchQueryProvider.notifier).state = value;
          },
        ),
        actions: [
          if (_searchController.text.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.clear),
              onPressed: () {
                _searchController.clear();
                ref.read(settingsSearchQueryProvider.notifier).state = '';
              },
            ),
        ],
      );
    }

    return AppBar(
      backgroundColor: isDark ? Colors.grey[900] : Colors.white,
      elevation: 0,
      title: Text(
        'الإعدادات',
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
      actions: [
        IconButton(
          icon: const Icon(Icons.search),
          color: isDark ? Colors.white : Colors.black87,
          onPressed: () => setState(() => _isSearching = true),
        ),
      ],
    );
  }

  Widget _buildSettingsList(
    BuildContext context,
    UserProfile profile,
    AppSettings settings,
    SyncStatus syncStatus,
    StorageInfo storageInfo,
  ) {
    return ListView(
      padding: const EdgeInsets.only(bottom: 32),
      children: [
        // Profile Header
        ProfileHeader(
          name: profile.name,
          email: profile.email,
          farmName: profile.farmName,
          avatarUrl: profile.avatarUrl,
          tier: profile.tier,
          isVerified: profile.isVerified,
          onEditPressed: () => _navigateTo(context, const AccountSettingsScreen()),
        ),

        // Account Section
        SettingsSection(
          title: 'Account',
          titleAr: 'الحساب',
          icon: Icons.person_outline,
          children: [
            SettingsTile(
              title: 'Account Settings',
              titleAr: 'إعدادات الحساب',
              icon: Icons.person_rounded,
              subtitle: 'الملف الشخصي، كلمة المرور، البصمة',
              onTap: () => _navigateTo(context, const AccountSettingsScreen()),
            ),
          ],
        ),

        // Appearance Section
        SettingsSection(
          title: 'Appearance',
          titleAr: 'المظهر',
          icon: Icons.palette_outlined,
          showDividers: true,
          children: [
            SettingsTile(
              title: 'Appearance',
              titleAr: 'المظهر',
              icon: Icons.brightness_6_rounded,
              subtitle: settings.themeModeDisplayAr,
              onTap: () => _navigateTo(context, const AppearanceSettingsScreen()),
            ),
            SettingsValueTile(
              title: 'Language',
              titleAr: 'اللغة',
              value: settings.languageDisplayAr,
              icon: Icons.language_rounded,
              onTap: () => _showLanguageDialog(context),
            ),
          ],
        ),

        // Notifications Section
        SettingsSection(
          title: 'Notifications',
          titleAr: 'الإشعارات',
          icon: Icons.notifications_outlined,
          children: [
            SwitchSettingsTile(
              title: 'Notifications',
              titleAr: 'الإشعارات',
              icon: Icons.notifications_rounded,
              value: settings.notificationsEnabled,
              dynamicSubtitle: (v) => v ? 'مفعّلة' : 'معطّلة',
              onChanged: (value) {
                ref.read(appSettingsProvider.notifier).setNotificationsEnabled(value);
              },
            ),
            SettingsTile(
              title: 'Notification Settings',
              titleAr: 'إعدادات الإشعارات',
              icon: Icons.tune_rounded,
              subtitle: 'الفئات، ساعات الهدوء، الأصوات',
              enabled: settings.notificationsEnabled,
              onTap: () => _navigateTo(context, const NotificationSettingsScreen()),
            ),
          ],
        ),

        // Privacy Section
        SettingsSection(
          title: 'Privacy',
          titleAr: 'الخصوصية',
          icon: Icons.privacy_tip_outlined,
          children: [
            SettingsTile(
              title: 'Privacy Settings',
              titleAr: 'إعدادات الخصوصية',
              icon: Icons.shield_rounded,
              subtitle: 'مشاركة البيانات، التحليلات، الموقع',
              onTap: () => _navigateTo(context, const PrivacySettingsScreen()),
            ),
          ],
        ),

        // Sync & Storage Section
        SettingsSection(
          title: 'Sync & Storage',
          titleAr: 'المزامنة والتخزين',
          icon: Icons.sync_outlined,
          showDividers: true,
          children: [
            SettingsTile(
              title: 'Sync Settings',
              titleAr: 'إعدادات المزامنة',
              icon: Icons.sync_rounded,
              iconColor: syncStatus.isSyncing ? SahoolTheme.warning : SahoolTheme.success,
              subtitle: syncStatus.isSyncing ? 'جاري المزامنة...' : syncStatus.lastSyncDisplayAr,
              onTap: () => _navigateTo(context, const SyncSettingsScreen()),
            ),
            SettingsTile(
              title: 'Storage',
              titleAr: 'التخزين',
              icon: Icons.storage_rounded,
              subtitle: 'المستخدم: ${storageInfo.usedFormatted} من ${storageInfo.totalFormatted}',
              onTap: () => _navigateTo(context, const SyncSettingsScreen()),
            ),
          ],
        ),

        // Maps & Units Section
        SettingsSection(
          title: 'Maps & Units',
          titleAr: 'الخرائط والوحدات',
          icon: Icons.map_outlined,
          showDividers: true,
          children: [
            SettingsValueTile(
              title: 'Default Map View',
              titleAr: 'عرض الخريطة الافتراضي',
              value: _getMapViewDisplayAr(settings.defaultMapView),
              icon: Icons.map_rounded,
              onTap: () => _showMapViewDialog(context),
            ),
            SettingsValueTile(
              title: 'Measurement System',
              titleAr: 'نظام القياس',
              value: settings.measurementSystemDisplayAr,
              icon: Icons.straighten_rounded,
              onTap: () => _showMeasurementDialog(context),
            ),
          ],
        ),

        // Support Section
        SettingsSection(
          title: 'Support',
          titleAr: 'الدعم',
          icon: Icons.help_outline,
          showDividers: true,
          children: [
            SettingsTile(
              title: 'Help',
              titleAr: 'المساعدة',
              icon: Icons.help_rounded,
              subtitle: 'الأسئلة الشائعة، دليل الاستخدام',
              onTap: () => _navigateTo(context, const HelpScreen()),
            ),
            SettingsTile(
              title: 'About',
              titleAr: 'حول التطبيق',
              icon: Icons.info_rounded,
              subtitle: 'الإصدار 16.0.0',
              onTap: () => _navigateTo(context, const AboutScreen()),
            ),
          ],
        ),

        // Actions Section
        SettingsSection(
          title: 'Actions',
          titleAr: 'إجراءات',
          children: [
            SettingsTile(
              title: 'Export Settings',
              titleAr: 'تصدير الإعدادات',
              icon: Icons.upload_rounded,
              iconColor: SahoolTheme.info,
              showArrow: false,
              onTap: () => _exportSettings(context),
            ),
            SettingsTile(
              title: 'Import Settings',
              titleAr: 'استيراد الإعدادات',
              icon: Icons.download_rounded,
              iconColor: SahoolTheme.info,
              showArrow: false,
              onTap: () => _importSettings(context),
            ),
            SettingsTile(
              title: 'Reset to Defaults',
              titleAr: 'إعادة تعيين الافتراضي',
              icon: Icons.restore_rounded,
              iconColor: SahoolTheme.warning,
              showArrow: false,
              onTap: () => _showResetDialog(context),
            ),
            DestructiveSettingsTile(
              title: 'Logout',
              titleAr: 'تسجيل الخروج',
              icon: Icons.logout_rounded,
              onTap: () => _showLogoutDialog(context),
            ),
          ],
        ),

        // Version info at bottom
        const SizedBox(height: 24),
        Center(
          child: Text(
            'سهول الإصدار 16.0.0\nبناء 2026.01',
            textAlign: TextAlign.center,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[500],
            ),
          ),
        ),
        const SizedBox(height: 16),
      ],
    );
  }

  Widget _buildSearchResults(String query) {
    final searchItems = _getSearchableItems();
    final results = searchItems.where((item) {
      return item.titleAr.contains(query) ||
          item.title.toLowerCase().contains(query.toLowerCase()) ||
          (item.keywords?.any((k) => k.contains(query)) ?? false);
    }).toList();

    if (results.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.search_off, size: 64, color: Colors.grey[400]),
            const SizedBox(height: 16),
            Text(
              'لا توجد نتائج لـ "$query"',
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: results.length,
      itemBuilder: (context, index) {
        final item = results[index];
        return Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: SettingsTile(
            title: item.title,
            titleAr: item.titleAr,
            icon: item.icon,
            subtitle: item.section,
            onTap: item.onTap,
          ),
        );
      },
    );
  }

  List<_SearchableSettingsItem> _getSearchableItems() {
    return [
      _SearchableSettingsItem(
        title: 'Profile',
        titleAr: 'الملف الشخصي',
        icon: Icons.person_rounded,
        section: 'الحساب',
        keywords: ['اسم', 'بريد', 'هاتف', 'صورة'],
        onTap: () => _navigateTo(context, const AccountSettingsScreen()),
      ),
      _SearchableSettingsItem(
        title: 'Theme',
        titleAr: 'السمة',
        icon: Icons.brightness_6_rounded,
        section: 'المظهر',
        keywords: ['فاتح', 'داكن', 'تلقائي', 'وضع'],
        onTap: () => _navigateTo(context, const AppearanceSettingsScreen()),
      ),
      _SearchableSettingsItem(
        title: 'Language',
        titleAr: 'اللغة',
        icon: Icons.language_rounded,
        section: 'المظهر',
        keywords: ['عربي', 'انجليزي', 'arabic', 'english'],
        onTap: () => _showLanguageDialog(context),
      ),
      _SearchableSettingsItem(
        title: 'Notifications',
        titleAr: 'الإشعارات',
        icon: Icons.notifications_rounded,
        section: 'الإشعارات',
        keywords: ['تنبيهات', 'رسائل', 'صوت'],
        onTap: () => _navigateTo(context, const NotificationSettingsScreen()),
      ),
      _SearchableSettingsItem(
        title: 'Privacy',
        titleAr: 'الخصوصية',
        icon: Icons.shield_rounded,
        section: 'الخصوصية',
        keywords: ['بيانات', 'موقع', 'تحليلات'],
        onTap: () => _navigateTo(context, const PrivacySettingsScreen()),
      ),
      _SearchableSettingsItem(
        title: 'Sync',
        titleAr: 'المزامنة',
        icon: Icons.sync_rounded,
        section: 'المزامنة',
        keywords: ['مزامنة', 'تحديث', 'خلفية', 'واي فاي'],
        onTap: () => _navigateTo(context, const SyncSettingsScreen()),
      ),
      _SearchableSettingsItem(
        title: 'Storage',
        titleAr: 'التخزين',
        icon: Icons.storage_rounded,
        section: 'التخزين',
        keywords: ['مساحة', 'ذاكرة', 'كاش', 'حذف'],
        onTap: () => _navigateTo(context, const SyncSettingsScreen()),
      ),
      _SearchableSettingsItem(
        title: 'Help',
        titleAr: 'المساعدة',
        icon: Icons.help_rounded,
        section: 'الدعم',
        keywords: ['مساعدة', 'أسئلة', 'دعم'],
        onTap: () => _navigateTo(context, const HelpScreen()),
      ),
      _SearchableSettingsItem(
        title: 'About',
        titleAr: 'حول',
        icon: Icons.info_rounded,
        section: 'الدعم',
        keywords: ['إصدار', 'نسخة', 'معلومات'],
        onTap: () => _navigateTo(context, const AboutScreen()),
      ),
    ];
  }

  void _navigateTo(BuildContext context, Widget screen) {
    Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => screen),
    );
  }

  void _showLanguageDialog(BuildContext context) {
    final currentLang = ref.read(appSettingsProvider).languageCode;

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
                'اختر اللغة',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            _buildLanguageOption('ar', 'العربية', currentLang == 'ar'),
            _buildLanguageOption('en', 'English', currentLang == 'en'),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  Widget _buildLanguageOption(String code, String label, bool isSelected) {
    return ListTile(
      title: Text(label),
      trailing: isSelected
          ? const Icon(Icons.check_circle, color: SahoolTheme.primary)
          : null,
      onTap: () {
        ref.read(appSettingsProvider.notifier).setLanguage(code);
        Navigator.pop(context);
      },
    );
  }

  void _showMapViewDialog(BuildContext context) {
    final currentView = ref.read(appSettingsProvider).defaultMapView;

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
                'عرض الخريطة',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            _buildMapViewOption('satellite', 'القمر الصناعي', Icons.satellite_alt, currentView == 'satellite'),
            _buildMapViewOption('terrain', 'التضاريس', Icons.terrain, currentView == 'terrain'),
            _buildMapViewOption('street', 'الشوارع', Icons.map, currentView == 'street'),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  Widget _buildMapViewOption(String value, String label, IconData icon, bool isSelected) {
    return ListTile(
      leading: Icon(icon, color: isSelected ? SahoolTheme.primary : Colors.grey),
      title: Text(label),
      trailing: isSelected
          ? const Icon(Icons.check_circle, color: SahoolTheme.primary)
          : null,
      onTap: () {
        ref.read(appSettingsProvider.notifier).setDefaultMapView(value);
        Navigator.pop(context);
      },
    );
  }

  void _showMeasurementDialog(BuildContext context) {
    final currentSystem = ref.read(appSettingsProvider).measurementSystem;

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
                'نظام القياس',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            ListTile(
              title: const Text('متري'),
              subtitle: const Text('كيلومتر، هكتار، درجة مئوية'),
              trailing: currentSystem == 'metric'
                  ? const Icon(Icons.check_circle, color: SahoolTheme.primary)
                  : null,
              onTap: () {
                ref.read(appSettingsProvider.notifier).setMeasurementSystem('metric');
                Navigator.pop(context);
              },
            ),
            ListTile(
              title: const Text('إمبريالي'),
              subtitle: const Text('ميل، فدان، فهرنهايت'),
              trailing: currentSystem == 'imperial'
                  ? const Icon(Icons.check_circle, color: SahoolTheme.primary)
                  : null,
              onTap: () {
                ref.read(appSettingsProvider.notifier).setMeasurementSystem('imperial');
                Navigator.pop(context);
              },
            ),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  String _getMapViewDisplayAr(String view) {
    switch (view) {
      case 'satellite':
        return 'القمر الصناعي';
      case 'terrain':
        return 'التضاريس';
      case 'street':
        return 'الشوارع';
      default:
        return view;
    }
  }

  Future<void> _exportSettings(BuildContext context) async {
    final controller = ref.read(settingsControllerProvider);
    final path = await controller.exportSettings();

    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(
            path != null
                ? 'تم تصدير الإعدادات إلى: $path'
                : 'فشل تصدير الإعدادات',
          ),
          backgroundColor: path != null ? SahoolTheme.success : SahoolTheme.error,
        ),
      );
    }
  }

  Future<void> _importSettings(BuildContext context) async {
    // In real implementation, use file picker to select JSON file
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('اختر ملف الإعدادات للاستيراد'),
      ),
    );
  }

  void _showResetDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('إعادة تعيين الإعدادات'),
        content: const Text(
          'هل تريد إعادة جميع الإعدادات إلى القيم الافتراضية؟\n\nلن يتم حذف بياناتك.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await ref.read(settingsControllerProvider).resetToDefaults();
              if (mounted) {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('تم إعادة تعيين الإعدادات'),
                    backgroundColor: SahoolTheme.success,
                  ),
                );
              }
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolTheme.warning,
            ),
            child: const Text('إعادة تعيين'),
          ),
        ],
      ),
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تسجيل الخروج'),
        content: const Text(
          'هل أنت متأكد من تسجيل الخروج؟\n\nسيتم الاحتفاظ بالبيانات المحلية.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // In real implementation, perform logout
              Navigator.of(context).popUntil((route) => route.isFirst);
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolTheme.error,
            ),
            child: const Text('تسجيل الخروج'),
          ),
        ],
      ),
    );
  }
}

/// Searchable settings item model
class _SearchableSettingsItem {
  final String title;
  final String titleAr;
  final IconData icon;
  final String section;
  final List<String>? keywords;
  final VoidCallback onTap;

  _SearchableSettingsItem({
    required this.title,
    required this.titleAr,
    required this.icon,
    required this.section,
    this.keywords,
    required this.onTap,
  });
}
