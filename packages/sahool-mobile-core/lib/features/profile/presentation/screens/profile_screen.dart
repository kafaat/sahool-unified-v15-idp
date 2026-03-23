import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import '../../../../core/services/auth_service.dart';
import '../providers/profile_provider.dart';

/// شاشة الملف الشخصي والإعدادات
/// Profile & Settings Screen
class ProfileScreen extends ConsumerStatefulWidget {
  const ProfileScreen({super.key});

  @override
  ConsumerState<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends ConsumerState<ProfileScreen> {
  bool _notificationsEnabled = true;
  bool _locationEnabled = true;
  final ImagePicker _imagePicker = ImagePicker();
  final _editFormKey = GlobalKey<FormState>();

  bool get _isArabic {
    final profile = ref.read(profileProvider);
    return profile.language == 'ar';
  }

  @override
  Widget build(BuildContext context) {
    final profile = ref.watch(profileProvider);

    final isArabic = profile.language == 'ar';

    return Directionality(
      textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        appBar: AppBar(
          title: Text(isArabic ? 'الملف الشخصي' : 'Profile'),
          backgroundColor: const Color(0xFF367C2B),
          foregroundColor: Colors.white,
          actions: [
            if (profile.error != null)
              IconButton(
                icon: const Icon(Icons.refresh),
                tooltip: isArabic ? 'إعادة المحاولة' : 'Retry',
                onPressed: () =>
                    ref.read(profileProvider.notifier).loadProfile(),
              ),
          ],
        ),
        body: profile.isLoading
            ? const Center(child: CircularProgressIndicator())
            : profile.error != null && profile.userId.isEmpty
                ? _buildErrorState(profile.error!, isArabic)
                : SingleChildScrollView(
                    child: Column(
                      children: [
                        // رأس الملف الشخصي
                        _buildProfileHeader(profile),
                        const SizedBox(height: 16),

                        // الإحصائيات السريعة
                        _buildQuickStats(profile, isArabic),
                        const SizedBox(height: 16),

                        // إعدادات الحساب
                        _buildSectionTitle(isArabic ? 'إعدادات الحساب' : 'Account Settings'),
                        _buildAccountSettings(isArabic),
                        const SizedBox(height: 16),

                        // إعدادات التطبيق
                        _buildSectionTitle(isArabic ? 'إعدادات التطبيق' : 'App Settings'),
                        _buildAppSettings(isArabic),
                        const SizedBox(height: 16),

                        // إعدادات الإشعارات
                        _buildSectionTitle(isArabic ? 'الإشعارات' : 'Notifications'),
                        _buildNotificationSettings(isArabic),
                        const SizedBox(height: 16),

                        // الدعم والمساعدة
                        _buildSectionTitle(isArabic ? 'الدعم والمساعدة' : 'Support & Help'),
                        _buildSupportSection(isArabic),
                        const SizedBox(height: 16),

                        // تسجيل الخروج
                        _buildLogoutButton(isArabic),
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

  Widget _buildErrorState(String message, bool isArabic) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.cloud_off, size: 64, color: Colors.grey[300]),
          const SizedBox(height: 16),
          Text(
            message,
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600], fontSize: 16),
          ),
          const SizedBox(height: 24),
          ElevatedButton.icon(
            onPressed: () =>
                ref.read(profileProvider.notifier).loadProfile(),
            icon: const Icon(Icons.refresh),
            label: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF367C2B),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProfileHeader(ProfileState profile) {
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
                backgroundImage: profile.avatarUrl != null
                    ? NetworkImage(profile.avatarUrl!)
                    : null,
                child: profile.avatarUrl == null
                    ? const Icon(
                        Icons.person,
                        size: 50,
                        color: Color(0xFF367C2B),
                      )
                    : null,
              ),
              Positioned(
                bottom: 0,
                right: 0,
                child: GestureDetector(
                  onTap: () => _showImagePickerSheet(context),
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
              ),
            ],
          ),
          const SizedBox(height: 16),

          // اسم المستخدم
          Text(
            profile.userNameAr.isNotEmpty ? profile.userNameAr : profile.userName,
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.white,
            ),
          ),
          const SizedBox(height: 4),

          // المزرعة
          if (profile.farmNameAr.isNotEmpty || profile.farmName.isNotEmpty)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Text(
                profile.farmNameAr.isNotEmpty
                    ? profile.farmNameAr
                    : profile.farmName,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 14,
                ),
              ),
            ),
          const SizedBox(height: 8),

          // البريد الإلكتروني
          if (profile.email.isNotEmpty)
            Text(
              profile.email,
              style: const TextStyle(
                color: Colors.white70,
                fontSize: 14,
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildQuickStats(ProfileState profile, bool isArabic) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        children: [
          Expanded(
            child: _buildStatItem(
              isArabic ? 'الحقول' : 'Fields',
              profile.fieldsCount.toString(),
              Icons.landscape,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatItem(
              isArabic ? 'المهام' : 'Tasks',
              profile.tasksCompleted.toString(),
              Icons.task_alt,
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: _buildStatItem(
              isArabic ? 'الإنجازات' : 'Achievements',
              profile.achievementsCount.toString(),
              Icons.emoji_events,
            ),
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

  Widget _buildAccountSettings(bool isArabic) {
    final profile = ref.watch(profileProvider);
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSettingsTile(
            icon: Icons.person_outline,
            title: isArabic ? 'تعديل الملف الشخصي' : 'Edit Profile',
            onTap: () => _showEditProfile(),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.lock_outline,
            title: isArabic ? 'تغيير كلمة المرور' : 'Change Password',
            onTap: () => _showChangePassword(),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.phone_android,
            title: isArabic ? 'رقم الهاتف' : 'Phone Number',
            subtitle: profile.phone.isNotEmpty
                ? profile.phone
                : (isArabic ? 'لم يتم التعيين' : 'Not set'),
            onTap: () {},
          ),
        ],
      ),
    );
  }

  Widget _buildAppSettings(bool isArabic) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSettingsTile(
            icon: Icons.settings,
            title: isArabic ? 'الإعدادات' : 'Settings',
            subtitle: isArabic
                ? 'المظهر، اللغة، والمزيد'
                : 'Appearance, language, and more',
            onTap: () => context.push('/settings'),
          ),
          const Divider(height: 1),
          _buildSwitchTile(
            icon: Icons.location_on_outlined,
            title: isArabic ? 'تفعيل الموقع' : 'Enable Location',
            value: _locationEnabled,
            onChanged: (value) => setState(() => _locationEnabled = value),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.storage,
            title: isArabic ? 'مسح ذاكرة التخزين المؤقت' : 'Clear Cache',
            onTap: () => _clearCache(),
          ),
        ],
      ),
    );
  }

  Widget _buildNotificationSettings(bool isArabic) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSwitchTile(
            icon: Icons.notifications_outlined,
            title: isArabic ? 'تفعيل الإشعارات' : 'Enable Notifications',
            value: _notificationsEnabled,
            onChanged: (value) => setState(() => _notificationsEnabled = value),
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.warning_outlined,
            title: isArabic ? 'إشعارات التنبيهات' : 'Alert Notifications',
            subtitle: isArabic ? 'تنبيهات الطقس والصحة' : 'Weather & health alerts',
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
            title: isArabic ? 'إشعارات المهام' : 'Task Notifications',
            subtitle: isArabic ? 'تذكير بالمهام المعلقة' : 'Pending task reminders',
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

  Widget _buildSupportSection(bool isArabic) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Column(
        children: [
          _buildSettingsTile(
            icon: Icons.help_outline,
            title: isArabic ? 'مركز المساعدة' : 'Help Center',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.chat_outlined,
            title: isArabic ? 'تواصل معنا' : 'Contact Us',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.bug_report_outlined,
            title: isArabic ? 'الإبلاغ عن مشكلة' : 'Report a Problem',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.star_outline,
            title: isArabic ? 'تقييم التطبيق' : 'Rate the App',
            onTap: () {},
          ),
          const Divider(height: 1),
          _buildSettingsTile(
            icon: Icons.privacy_tip_outlined,
            title: isArabic ? 'سياسة الخصوصية' : 'Privacy Policy',
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

  Widget _buildLogoutButton(bool isArabic) {
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
        label: Text(isArabic ? 'تسجيل الخروج' : 'Sign Out'),
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
          'الإصدار 16.0.0',
          style: TextStyle(
            fontSize: 12,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  void _showEditProfile() {
    final profile = ref.read(profileProvider);
    final isArabic = profile.language == 'ar';
    final nameController = TextEditingController(
      text: profile.userNameAr.isNotEmpty ? profile.userNameAr : profile.userName,
    );
    final phoneController = TextEditingController(text: profile.phone);
    final farmController = TextEditingController(
      text: profile.farmNameAr.isNotEmpty ? profile.farmNameAr : profile.farmName,
    );

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetContext) => Directionality(
        textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
        child: Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(sheetContext).viewInsets.bottom,
            left: 16,
            right: 16,
            top: 16,
          ),
          child: Form(
            key: _editFormKey,
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  isArabic ? 'تعديل الملف الشخصي' : 'Edit Profile',
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: nameController,
                  decoration: InputDecoration(
                    labelText: isArabic ? 'الاسم' : 'Name',
                    prefixIcon: const Icon(Icons.person_outline),
                  ),
                  validator: (value) {
                    if (value == null || value.trim().isEmpty) {
                      return isArabic ? 'الاسم مطلوب' : 'Name is required';
                    }
                    if (value.trim().length < 2) {
                      return isArabic
                          ? 'الاسم يجب أن يكون حرفين على الأقل'
                          : 'Name must be at least 2 characters';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: phoneController,
                  keyboardType: TextInputType.phone,
                  decoration: InputDecoration(
                    labelText: isArabic ? 'رقم الهاتف' : 'Phone Number',
                    prefixIcon: const Icon(Icons.phone_outlined),
                  ),
                  validator: (value) {
                    if (value != null && value.trim().isNotEmpty) {
                      final phoneRegex = RegExp(r'^\+?[0-9\s\-]{7,15}$');
                      if (!phoneRegex.hasMatch(value.trim())) {
                        return isArabic
                            ? 'رقم الهاتف غير صالح'
                            : 'Invalid phone number';
                      }
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),
                TextFormField(
                  controller: farmController,
                  decoration: InputDecoration(
                    labelText: isArabic ? 'اسم المزرعة' : 'Farm Name',
                    prefixIcon: const Icon(Icons.agriculture_outlined),
                  ),
                ),
                const SizedBox(height: 24),
                ElevatedButton(
                  onPressed: () {
                    if (_editFormKey.currentState?.validate() ?? false) {
                      Navigator.pop(sheetContext);
                      ref.read(profileProvider.notifier).updateProfile(
                        userName: nameController.text.trim(),
                        phone: phoneController.text.trim(),
                        farmName: farmController.text.trim(),
                      );
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(isArabic
                              ? 'جارٍ حفظ التغييرات...'
                              : 'Saving changes...'),
                          backgroundColor: const Color(0xFF367C2B),
                        ),
                      );
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF367C2B),
                    minimumSize: const Size(double.infinity, 50),
                  ),
                  child: Text(isArabic ? 'حفظ' : 'Save'),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _showChangePassword() {
    final isArabic = _isArabic;
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Directionality(
        textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
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
              Text(
                isArabic ? 'تغيير كلمة المرور' : 'Change Password',
                style: const TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                obscureText: true,
                decoration: InputDecoration(
                  labelText: isArabic ? 'كلمة المرور الحالية' : 'Current Password',
                  prefixIcon: const Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                obscureText: true,
                decoration: InputDecoration(
                  labelText: isArabic ? 'كلمة المرور الجديدة' : 'New Password',
                  prefixIcon: const Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                obscureText: true,
                decoration: InputDecoration(
                  labelText: isArabic ? 'تأكيد كلمة المرور' : 'Confirm Password',
                  prefixIcon: const Icon(Icons.lock_outline),
                ),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(context);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(isArabic
                          ? 'تم تغيير كلمة المرور'
                          : 'Password changed'),
                      backgroundColor: const Color(0xFF367C2B),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF367C2B),
                  minimumSize: const Size(double.infinity, 50),
                ),
                child: Text(isArabic ? 'تغيير' : 'Change'),
              ),
              const SizedBox(height: 32),
            ],
          ),
        ),
      ),
    );
  }

  void _showImagePickerSheet(BuildContext ctx) {
    final isArabic = _isArabic;
    showModalBottomSheet(
      context: ctx,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (sheetContext) => Directionality(
        textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.symmetric(vertical: 16),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  isArabic ? 'تغيير الصورة الشخصية' : 'Change Profile Photo',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                ListTile(
                  leading: const Icon(Icons.camera_alt, color: Color(0xFF367C2B)),
                  title: Text(isArabic ? 'التقاط صورة' : 'Take Photo'),
                  onTap: () async {
                    Navigator.pop(sheetContext);
                    final image = await _imagePicker.pickImage(
                      source: ImageSource.camera,
                      maxWidth: 800,
                      maxHeight: 800,
                      imageQuality: 85,
                    );
                    if (image != null) {
                      ref.read(profileProvider.notifier).uploadAvatar(image.path);
                    }
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.photo_library, color: Color(0xFF367C2B)),
                  title: Text(isArabic ? 'اختيار من المعرض' : 'Choose from Gallery'),
                  onTap: () async {
                    Navigator.pop(sheetContext);
                    final image = await _imagePicker.pickImage(
                      source: ImageSource.gallery,
                      maxWidth: 800,
                      maxHeight: 800,
                      imageQuality: 85,
                    );
                    if (image != null) {
                      ref.read(profileProvider.notifier).uploadAvatar(image.path);
                    }
                  },
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _clearCache() {
    final isArabic = _isArabic;
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
        child: AlertDialog(
          title: Text(isArabic ? 'مسح ذاكرة التخزين المؤقت' : 'Clear Cache'),
          content: Text(isArabic
              ? 'هل أنت متأكد من مسح ذاكرة التخزين المؤقت؟'
              : 'Are you sure you want to clear the cache?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(isArabic ? 'إلغاء' : 'Cancel'),
            ),
            ElevatedButton(
              onPressed: () {
                Navigator.pop(context);
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(isArabic
                        ? 'تم مسح ذاكرة التخزين المؤقت'
                        : 'Cache cleared'),
                    backgroundColor: const Color(0xFF367C2B),
                  ),
                );
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: const Color(0xFF367C2B),
              ),
              child: Text(isArabic ? 'مسح' : 'Clear'),
            ),
          ],
        ),
      ),
    );
  }

  void _showLogoutDialog() {
    final isArabic = _isArabic;
    showDialog(
      context: context,
      builder: (context) => Directionality(
        textDirection: isArabic ? TextDirection.rtl : TextDirection.ltr,
        child: AlertDialog(
          title: Text(isArabic ? 'تسجيل الخروج' : 'Sign Out'),
          content: Text(isArabic
              ? 'هل أنت متأكد من تسجيل الخروج؟'
              : 'Are you sure you want to sign out?'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: Text(isArabic ? 'إلغاء' : 'Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await ref.read(authProvider.notifier).logout();
                if (context.mounted) {
                  Navigator.of(context).popUntil((route) => route.isFirst);
                }
              },
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.red,
              ),
              child: Text(isArabic ? 'تسجيل الخروج' : 'Sign Out'),
            ),
          ],
        ),
      ),
    );
  }
}
