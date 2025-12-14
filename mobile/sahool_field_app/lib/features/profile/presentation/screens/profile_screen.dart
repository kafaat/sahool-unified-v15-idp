import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

/// شاشة الملف الشخصي والإعدادات
/// Profile & Settings Screen
class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  bool _darkMode = false;
  bool _notificationsEnabled = true;
  bool _locationEnabled = true;
  String _language = 'ar';

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('الملف الشخصي'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
        ),
        body: SingleChildScrollView(
          child: Column(
            children: [
              // رأس الملف الشخصي
              _buildProfileHeader(),
              const SizedBox(height: 16),

              // الإحصائيات السريعة
              _buildQuickStats(),
              const SizedBox(height: 16),

              // إعدادات الحساب
              _buildSectionTitle('إعدادات الحساب'),
              _buildAccountSettings(),
              const SizedBox(height: 16),

              // إعدادات التطبيق
              _buildSectionTitle('إعدادات التطبيق'),
              _buildAppSettings(),
              const SizedBox(height: 16),

              // إعدادات الإشعارات
              _buildSectionTitle('الإشعارات'),
              _buildNotificationSettings(),
              const SizedBox(height: 16),

              // الدعم والمساعدة
              _buildSectionTitle('الدعم والمساعدة'),
              _buildSupportSection(),
              const SizedBox(height: 16),

              // تسجيل الخروج
              _buildLogoutButton(),
              const SizedBox(height: 32),

              // معلومات التطبيق
              _buildAppInfo(),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: const BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [Color(0xFF367C2B), Color(0xFF2D6623)],
        ),
      ),
      child: Column(
        children: [
          // صورة الملف الشخصي
          Stack(
            children: [
              CircleAvatar(
                radius: 50,
                backgroundColor: Colors.white,
                child: const Icon(
                  Icons.person,
                  size: 50,
                  color: Color(0xFF367C2B),
                ),
              ),
              Positioned(
                bottom: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: const BoxDecoration(
                    color: Colors.white,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(
                    Icons.camera_alt,
                    size: 20,
                    color: Color(0xFF367C2B),
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),

          // اسم المستخدم
          const Text(
            'أحمد محمد',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 4),

          // الدور
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.2),
              borderRadius: BorderRadius.circular(20),
            ),
            child: const Text(
              'مدير المزرعة',
              style: TextStyle(
                color: Colors.white,
                fontSize: 14,
              ),
            ),
          ),
          const SizedBox(height: 8),

          // البريد الإلكتروني
          const Text(
            'ahmed@sahool.sa',
            style: TextStyle(
              color: Colors.white70,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickStats() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: _buildStatItem('الحقول', '12', Icons.landscape),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatItem('المهام', '28', Icons.task_alt),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatItem('التنبيهات', '3', Icons.notifications),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, IconData icon) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Icon(icon, color: const Color(0xFF367C2B), size: 28),
            const SizedBox(height: 8),
            Text(
              value,
              style: const TextStyle(
                fontSize: 20,
                fontWeight: FontWeight.bold,
              ),
            ),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Align(
        alignment: Alignment.centerRight,
        child: Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: Color(0xFF367C2B),
          ),
        ),
      ),
    );
  }

  Widget _buildAccountSettings() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSettingsTile(
            icon: Icons.person_outline,
            title: 'تعديل الملف الشخصي',
            onTap: () => _showEditProfile(),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.lock_outline,
            title: 'تغيير كلمة المرور',
            onTap: () => _showChangePassword(),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.phone_android,
            title: 'رقم الهاتف',
            subtitle: '+966 50 XXX XXXX',
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildAppSettings() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSwitchTile(
            icon: Icons.dark_mode,
            title: 'الوضع الداكن',
            value: _darkMode,
            onChanged: (value) => setState(() => _darkMode = value),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.language,
            title: 'اللغة',
            subtitle: _language == 'ar' ? 'العربية' : 'English',
            onTap: () => _showLanguageDialog(),
          ),
          const Divider(height: 1),
          _buildSwitchTile(
            icon: Icons.location_on_outlined,
            title: 'تفعيل الموقع',
            value: _locationEnabled,
            onChanged: (value) => setState(() => _locationEnabled = value),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.storage,
            title: 'مسح ذاكرة التخزين المؤقت',
            onTap: () => _clearCache(),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationSettings() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSwitchTile(
            icon: Icons.notifications_outlined,
            title: 'تفعيل الإشعارات',
            value: _notificationsEnabled,
            onChanged: (value) => setState(() => _notificationsEnabled = value),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.warning_outlined,
            title: 'إشعارات التنبيهات',
            subtitle: 'تنبيهات الطقس والصحة',
            onTap: () {},
            trailing: Switch(
              value: true,
              onChanged: (v) {},
              activeColor: const Color(0xFF367C2B),
            ),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.task_outlined,
            title: 'إشعارات المهام',
            subtitle: 'تذكير بالمهام المعلقة',
            onTap: () {},
            trailing: Switch(
              value: true,
              onChanged: (v) {},
              activeColor: const Color(0xFF367C2B),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSupportSection() {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSettingsTile(
            icon: Icons.help_outline,
            title: 'مركز المساعدة',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.chat_outlined,
            title: 'تواصل معنا',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.bug_report_outlined,
            title: 'الإبلاغ عن مشكلة',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.star_outline,
            title: 'تقييم التطبيق',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.privacy_tip_outlined,
            title: 'سياسة الخصوصية',
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildSettingsTile({
    required IconData icon,
    required String title,
    String? subtitle,
    required VoidCallback onTap,
    Widget? trailing,
  }) {
    return ListTile(
      leading: Icon(icon, color: const Color(0xFF367C2B)),
      title: Text(title),
      subtitle: subtitle != null ? Text(subtitle) : null,
      trailing: trailing ?? const Icon(Icons.chevron_left),
      onTap: onTap,
    );
  }

  Widget _buildSwitchTile({
    required IconData icon,
    required String title,
    required bool value,
    required ValueChanged<bool> onChanged,
  }) {
    return ListTile(
      leading: Icon(icon, color: const Color(0xFF367C2B)),
      title: Text(title),
      trailing: Switch(
        value: value,
        onChanged: onChanged,
        activeColor: const Color(0xFF367C2B),
      ),
    );
  }

  Widget _buildLogoutButton() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ElevatedButton.icon(
        onPressed: () => _showLogoutDialog(),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red,
          foregroundColor: Colors.white,
          minimumSize: const Size(double.infinity, 50),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        icon: const Icon(Icons.logout),
        label: const Text('تسجيل الخروج'),
      ),
    );
  }

  Widget _buildAppInfo() {
    return Column(
      children: [
        Image.asset(
          'assets/images/sahool_logo.png',
          height: 40,
          errorBuilder: (context, error, stackTrace) => const Icon(
            Icons.agriculture,
            size: 40,
            color: Color(0xFF367C2B),
          ),
        ),
        const SizedBox(height: 8),
        const Text(
          'SAHOOL Field App',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF367C2B),
          ),
        ),
        Text(
          'الإصدار 1.0.0',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  void _showEditProfile() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
            left: 16,
            right: 16,
            top: 16,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'تعديل الملف الشخصي',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                initialValue: 'أحمد محمد',
                decoration: const InputDecoration(
                  labelText: 'الاسم',
                  prefixIcon: Icon(Icons.person_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                initialValue: 'ahmed@sahool.sa',
                decoration: const InputDecoration(
                  labelText: 'البريد الإلكتروني',
                  prefixIcon: Icon(Icons.email_outlined),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('تم حفظ التغييرات'),
                      backgroundColor: Color(0xFF367C2B),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF367C2B),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: const Text('حفظ'),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  void _showChangePassword() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
            left: 16,
            right: 16,
            top: 16,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                'تغيير كلمة المرور',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'كلمة المرور الحالية',
                  prefixIcon: Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'كلمة المرور الجديدة',
                  prefixIcon: Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'تأكيد كلمة المرور',
                  prefixIcon: Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('تم تغيير كلمة المرور'),
                      backgroundColor: Color(0xFF367C2B),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF367C2B),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: const Text('تغيير'),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  void _showLanguageDialog() {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('اختر اللغة'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              RadioListTile<String>(
                title: const Text('العربية'),
                value: 'ar',
                groupValue: _language,
                onChanged: (value) {
                  setState(() => _language = value!);
                  Navigator.pop(context);
                },
                activeColor: const Color(0xFF367C2B),
              ),
              RadioListTile<String>(
                title: const Text('English'),
                value: 'en',
                groupValue: _language,
                onChanged: (value) {
                  setState(() => _language = value!);
                  Navigator.pop(context);
                },
                activeColor: const Color(0xFF367C2B),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _clearCache() {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
          title: const Text('مسح ذاكرة التخزين المؤقت'),
          content: const Text('هل أنت متأكد من مسح ذاكرة التخزين المؤقت؟'),
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
                    content: Text('تم مسح ذاكرة التخزين المؤقت'),
                    backgroundColor: Color(0xFF367C2B),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
              ),
              child: const Text('مسح'),
            ),
          ],
        ),
      ),
    );
  }

  void _showLogoutDialog() {
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: TextDirection.rtl,
        child: AlertDialog(
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
                // TODO: Implement logout
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
              ),
              child: const Text('تسجيل الخروج'),
            ),
          ],
        ),
      ),
    );
  }
}
