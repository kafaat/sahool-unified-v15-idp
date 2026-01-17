import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/theme/sahool_theme.dart';

/// Profile Screen - الملف الشخصي والإعدادات
class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SahoolColors.background,
      body: CustomScrollView(
        slivers: [
          // Profile header
          SliverAppBar(
            expandedHeight: 200,
            pinned: true,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: SahoolColors.primaryGradient,
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(height: 20),
                      // Avatar
                      Container(
                        width: 80,
                        height: 80,
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 3),
                          boxShadow: SahoolShadows.medium,
                        ),
                        child: const Icon(
                          Icons.person,
                          size: 40,
                          color: SahoolColors.primary,
                        ),
                      ),
                      const SizedBox(height: 12),
                      const Text(
                        'أحمد محمد',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'مزارع • صنعاء',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.8),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            actions: [
              IconButton(
                icon: const Icon(Icons.edit, color: Colors.white),
                onPressed: () {},
              ),
            ],
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  // Stats
                  _buildStatsRow(),
                  const SizedBox(height: 24),

                  // Settings sections
                  _buildSection(
                    title: 'الحساب',
                    items: [
                      _SettingItem(
                        icon: Icons.person_outline,
                        title: 'معلومات الحساب',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.phone_android,
                        title: 'رقم الهاتف',
                        subtitle: '+967 7XX XXX XXX',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.security,
                        title: 'الأمان والخصوصية',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.fingerprint,
                        title: 'تسجيل الدخول بالبصمة',
                        subtitle: 'الوصول السريع والآمن',
                        onTap: () => context.push('/biometric-settings'),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  _buildSection(
                    title: 'التطبيق',
                    items: [
                      _SettingItem(
                        icon: Icons.notifications_outlined,
                        title: 'إعدادات التنبيهات',
                        onTap: () {},
                        trailing: Switch(
                          value: true,
                          onChanged: (_) {},
                          activeColor: SahoolColors.primary,
                        ),
                      ),
                      _SettingItem(
                        icon: Icons.language,
                        title: 'اللغة',
                        subtitle: 'العربية',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.dark_mode_outlined,
                        title: 'الوضع الليلي',
                        onTap: () {},
                        trailing: Switch(
                          value: false,
                          onChanged: (_) {},
                          activeColor: SahoolColors.primary,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  _buildSection(
                    title: 'البيانات',
                    items: [
                      _SettingItem(
                        icon: Icons.cloud_sync,
                        title: 'مركز المزامنة',
                        subtitle: '5 عمليات معلقة',
                        onTap: () => context.push('/sync'),
                        showBadge: true,
                      ),
                      _SettingItem(
                        icon: Icons.download_outlined,
                        title: 'الخرائط المحملة',
                        subtitle: '45 MB',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.delete_outline,
                        title: 'مسح البيانات المؤقتة',
                        onTap: () => _showClearCacheDialog(context),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),

                  _buildSection(
                    title: 'الدعم',
                    items: [
                      _SettingItem(
                        icon: Icons.help_outline,
                        title: 'مركز المساعدة',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.chat_bubble_outline,
                        title: 'تواصل معنا',
                        onTap: () {},
                      ),
                      _SettingItem(
                        icon: Icons.info_outline,
                        title: 'حول التطبيق',
                        subtitle: 'الإصدار 15.3.0',
                        onTap: () => _showAboutDialog(context),
                      ),
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Logout button
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => _showLogoutDialog(context),
                      icon: const Icon(Icons.logout, color: SahoolColors.danger),
                      label: const Text(
                        'تسجيل الخروج',
                        style: TextStyle(color: SahoolColors.danger),
                      ),
                      style: OutlinedButton.styleFrom(
                        side: const BorderSide(color: SahoolColors.danger),
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                    ),
                  ),

                  const SizedBox(height: 32),

                  // Footer
                  Text(
                    'SAHOOL v15.3.0\nPowered by KAFAAT',
                    style: TextStyle(
                      color: Colors.grey[400],
                      fontSize: 12,
                    ),
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 100),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatsRow() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: SahoolShadows.small,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildStatItem('12', 'حقل'),
          _buildDivider(),
          _buildStatItem('48', 'مهمة مكتملة'),
          _buildDivider(),
          _buildStatItem('156', 'يوم نشط'),
        ],
      ),
    );
  }

  Widget _buildStatItem(String value, String label) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: SahoolColors.primary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            color: Colors.grey[600],
            fontSize: 12,
          ),
        ),
      ],
    );
  }

  Widget _buildDivider() {
    return Container(
      width: 1,
      height: 40,
      color: Colors.grey[200],
    );
  }

  Widget _buildSection({
    required String title,
    required List<_SettingItem> items,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.only(right: 8, bottom: 12),
          child: Text(
            title,
            style: TextStyle(
              color: Colors.grey[600],
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(16),
            boxShadow: SahoolShadows.small,
          ),
          child: Column(
            children: items.asMap().entries.map((entry) {
              final index = entry.key;
              final item = entry.value;
              return Column(
                children: [
                  _buildSettingTile(item),
                  if (index < items.length - 1)
                    Divider(height: 1, indent: 56, color: Colors.grey[200]),
                ],
              );
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildSettingTile(_SettingItem item) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: SahoolColors.primary.withOpacity(0.1),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Icon(item.icon, color: SahoolColors.primary, size: 22),
      ),
      title: Text(item.title),
      subtitle: item.subtitle != null
          ? Text(
              item.subtitle!,
              style: TextStyle(color: Colors.grey[500], fontSize: 12),
            )
          : null,
      trailing: item.trailing ??
          (item.showBadge
              ? Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                      decoration: BoxDecoration(
                        color: SahoolColors.danger,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Text(
                        '5',
                        style: TextStyle(color: Colors.white, fontSize: 10),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Icon(Icons.chevron_left, color: Colors.grey[400]),
                  ],
                )
              : Icon(Icons.chevron_left, color: Colors.grey[400])),
      onTap: item.onTap,
    );
  }

  void _showLogoutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تسجيل الخروج'),
        content: const Text('هل أنت متأكد من تسجيل الخروج؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.go('/splash');
            },
            style: ElevatedButton.styleFrom(backgroundColor: SahoolColors.danger),
            child: const Text('خروج'),
          ),
        ],
      ),
    );
  }

  void _showClearCacheDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('مسح البيانات المؤقتة'),
        content: const Text('سيتم حذف الملفات المؤقتة. البيانات المحفوظة لن تتأثر.'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('تم مسح البيانات المؤقتة')),
              );
            },
            child: const Text('مسح'),
          ),
        ],
      ),
    );
  }

  void _showAboutDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: SahoolColors.primary.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.eco, color: SahoolColors.primary),
            ),
            const SizedBox(width: 12),
            const Text('SAHOOL'),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('منصة الزراعة الذكية'),
            const SizedBox(height: 16),
            Text('الإصدار: 15.3.0', style: TextStyle(color: Colors.grey[600])),
            Text('Build: 2024.12.14', style: TextStyle(color: Colors.grey[600])),
            const SizedBox(height: 16),
            const Text('© 2024 KAFAAT'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('حسناً'),
          ),
        ],
      ),
    );
  }
}

class _SettingItem {
  final IconData icon;
  final String title;
  final String? subtitle;
  final VoidCallback onTap;
  final Widget? trailing;
  final bool showBadge;

  _SettingItem({
    required this.icon,
    required this.title,
    this.subtitle,
    required this.onTap,
    this.trailing,
    this.showBadge = false,
  });
}
