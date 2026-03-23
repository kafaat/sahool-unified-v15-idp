import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/config/theme.dart';
import '../../state/settings_providers.dart';
import '../widgets/widgets.dart';

/// Account Settings Screen
/// شاشة إعدادات الحساب
class AccountSettingsScreen extends ConsumerWidget {
  const AccountSettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final profile = ref.watch(userProfileProvider);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Directionality(
      textDirection: TextDirection.rtl,
      child: Scaffold(
        backgroundColor: isDark ? Colors.black : Colors.grey[100],
        appBar: AppBar(
          backgroundColor: isDark ? Colors.grey[900] : Colors.white,
          elevation: 0,
          title: Text(
            'إعدادات الحساب',
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
            // Profile section
            SettingsSection(
              title: 'Profile',
              titleAr: 'الملف الشخصي',
              icon: Icons.person_outline,
              showDividers: true,
              children: [
                // Profile Picture
                _ProfilePictureTile(
                  avatarUrl: profile.avatarUrl,
                  name: profile.name,
                  onTap: () => _showAvatarOptions(context),
                ),
                SettingsTile(
                  title: 'Name',
                  titleAr: 'الاسم',
                  icon: Icons.badge_rounded,
                  subtitle: profile.name,
                  onTap: () => _showEditDialog(
                    context,
                    'الاسم',
                    profile.name,
                    (value) {
                      ref.read(userProfileProvider.notifier).updateProfile(
                            profile.copyWith(name: value),
                          );
                    },
                  ),
                ),
                SettingsTile(
                  title: 'Email',
                  titleAr: 'البريد الإلكتروني',
                  icon: Icons.email_rounded,
                  subtitle: profile.email ?? 'غير محدد',
                  onTap: () => _showEditDialog(
                    context,
                    'البريد الإلكتروني',
                    profile.email ?? '',
                    (value) {
                      ref.read(userProfileProvider.notifier).updateProfile(
                            profile.copyWith(email: value),
                          );
                    },
                    keyboardType: TextInputType.emailAddress,
                  ),
                ),
                SettingsTile(
                  title: 'Phone',
                  titleAr: 'رقم الهاتف',
                  icon: Icons.phone_rounded,
                  subtitle: profile.phone ?? 'غير محدد',
                  onTap: () => _showEditDialog(
                    context,
                    'رقم الهاتف',
                    profile.phone ?? '',
                    (value) {
                      ref.read(userProfileProvider.notifier).updateProfile(
                            profile.copyWith(phone: value),
                          );
                    },
                    keyboardType: TextInputType.phone,
                  ),
                ),
                SettingsTile(
                  title: 'Farm Name',
                  titleAr: 'اسم المزرعة',
                  icon: Icons.agriculture_rounded,
                  subtitle: profile.farmName ?? 'غير محدد',
                  onTap: () => _showEditDialog(
                    context,
                    'اسم المزرعة',
                    profile.farmName ?? '',
                    (value) {
                      ref.read(userProfileProvider.notifier).updateProfile(
                            profile.copyWith(farmName: value),
                          );
                    },
                  ),
                ),
              ],
            ),

            // Security section
            SettingsSection(
              title: 'Security',
              titleAr: 'الأمان',
              icon: Icons.security_outlined,
              showDividers: true,
              children: [
                SettingsTile(
                  title: 'Change Password',
                  titleAr: 'تغيير كلمة المرور',
                  icon: Icons.lock_rounded,
                  iconColor: SahoolTheme.warning,
                  onTap: () => _showChangePasswordDialog(context),
                ),
                SwitchSettingsTile(
                  title: 'Biometric Login',
                  titleAr: 'تسجيل الدخول بالبصمة',
                  icon: Icons.fingerprint_rounded,
                  iconColor: SahoolTheme.info,
                  value: profile.biometricEnabled,
                  dynamicSubtitle: (v) => v ? 'مفعّل' : 'معطّل',
                  onChanged: (value) {
                    ref.read(userProfileProvider.notifier).toggleBiometric(value);
                  },
                ),
                SettingsTile(
                  title: 'Two-Factor Authentication',
                  titleAr: 'المصادقة الثنائية',
                  icon: Icons.security_rounded,
                  iconColor: SahoolTheme.success,
                  subtitle: 'غير مفعّل',
                  onTap: () => _showTwoFactorSetup(context),
                ),
                SettingsTile(
                  title: 'Active Sessions',
                  titleAr: 'الجلسات النشطة',
                  icon: Icons.devices_rounded,
                  subtitle: 'جهاز واحد نشط',
                  onTap: () => _showActiveSessions(context),
                ),
              ],
            ),

            // Membership section
            SettingsSection(
              title: 'Membership',
              titleAr: 'العضوية',
              icon: Icons.card_membership_outlined,
              children: [
                _MembershipTile(tier: profile.tier),
                SettingsTile(
                  title: 'Upgrade Plan',
                  titleAr: 'ترقية الباقة',
                  icon: Icons.upgrade_rounded,
                  iconColor: SahoolTheme.primary,
                  onTap: () => _showUpgradeOptions(context),
                ),
              ],
            ),

            // Danger zone
            SettingsSection(
              title: 'Danger Zone',
              titleAr: 'منطقة الخطر',
              icon: Icons.warning_outlined,
              children: [
                DestructiveSettingsTile(
                  title: 'Delete Account',
                  titleAr: 'حذف الحساب',
                  icon: Icons.delete_forever_rounded,
                  onTap: () => _showDeleteAccountDialog(context),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  void _showAvatarOptions(BuildContext context) {
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
                'تغيير الصورة الشخصية',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            ListTile(
              leading: const Icon(Icons.camera_alt),
              title: const Text('التقاط صورة'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.photo_library),
              title: const Text('اختيار من المعرض'),
              onTap: () => Navigator.pop(context),
            ),
            ListTile(
              leading: const Icon(Icons.delete, color: SahoolTheme.error),
              title: const Text('إزالة الصورة', style: TextStyle(color: SahoolTheme.error)),
              onTap: () => Navigator.pop(context),
            ),
            SizedBox(height: MediaQuery.of(context).padding.bottom + 16),
          ],
        ),
      ),
    );
  }

  void _showEditDialog(
    BuildContext context,
    String title,
    String currentValue,
    ValueChanged<String> onSave, {
    TextInputType keyboardType = TextInputType.text,
  }) {
    final controller = TextEditingController(text: currentValue);

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('تعديل $title'),
        content: TextField(
          controller: controller,
          keyboardType: keyboardType,
          autofocus: true,
          decoration: InputDecoration(
            labelText: title,
            border: const OutlineInputBorder(),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              onSave(controller.text);
              Navigator.pop(context);
            },
            child: const Text('حفظ'),
          ),
        ],
      ),
    );
  }

  void _showChangePasswordDialog(BuildContext context) {
    final currentController = TextEditingController();
    final newController = TextEditingController();
    final confirmController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تغيير كلمة المرور'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: currentController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'كلمة المرور الحالية',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: newController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'كلمة المرور الجديدة',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: confirmController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: 'تأكيد كلمة المرور',
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
              // Validate and change password
              Navigator.pop(context);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('تم تغيير كلمة المرور بنجاح'),
                  backgroundColor: SahoolTheme.success,
                ),
              );
            },
            child: const Text('تغيير'),
          ),
        ],
      ),
    );
  }

  void _showTwoFactorSetup(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('المصادقة الثنائية'),
        content: const Text(
          'المصادقة الثنائية تضيف طبقة إضافية من الأمان لحسابك.\n\n'
          'ستحتاج إلى تطبيق مصادقة مثل Google Authenticator.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Start 2FA setup flow
            },
            child: const Text('تفعيل'),
          ),
        ],
      ),
    );
  }

  void _showActiveSessions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.5,
        minChildSize: 0.3,
        maxChildSize: 0.9,
        builder: (context, scrollController) => DecoratedBox(
          decoration: BoxDecoration(
            color: Theme.of(context).brightness == Brightness.dark
                ? Colors.grey[900]
                : Colors.white,
            borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
          ),
          child: Column(
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
                  'الجلسات النشطة',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              Expanded(
                child: ListView(
                  controller: scrollController,
                  children: const [
                    _SessionTile(
                      device: 'هذا الجهاز',
                      location: 'صنعاء، اليمن',
                      lastActive: 'نشط الآن',
                      isCurrent: true,
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showUpgradeOptions(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      isScrollControlled: true,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: BoxDecoration(
          color: Theme.of(context).brightness == Brightness.dark
              ? Colors.grey[900]
              : Colors.white,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
        ),
        child: Column(
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
                'ترقية الباقة',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
            ),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.all(16),
                children: const [
                  _PlanCard(
                    name: 'مبتدئ',
                    price: 'مجاني',
                    features: ['5 حقول', 'تقارير أساسية', 'دعم عبر البريد'],
                    isCurrentPlan: true,
                  ),
                  _PlanCard(
                    name: 'احترافي',
                    price: '99 ر.ي/شهر',
                    features: ['25 حقل', 'تقارير متقدمة', 'دعم فني', 'تنبيهات ذكية'],
                    isRecommended: true,
                  ),
                  _PlanCard(
                    name: 'مؤسسي',
                    price: '299 ر.ي/شهر',
                    features: ['حقول غير محدودة', 'تحليلات AI', 'دعم 24/7', 'API'],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showDeleteAccountDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Row(
          children: [
            Icon(Icons.warning_rounded, color: SahoolTheme.error),
            SizedBox(width: 8),
            Text('حذف الحساب'),
          ],
        ),
        content: const Text(
          'هذا الإجراء لا يمكن التراجع عنه!\n\n'
          'سيتم حذف جميع بياناتك بشكل دائم بما في ذلك:\n'
          '- الحقول والمزارع\n'
          '- التقارير والتحليلات\n'
          '- الإعدادات والتفضيلات\n\n'
          'هل أنت متأكد؟',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              // Confirm with password and delete
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
}

/// Profile Picture Tile
class _ProfilePictureTile extends StatelessWidget {
  final String? avatarUrl;
  final String name;
  final VoidCallback onTap;

  const _ProfilePictureTile({
    this.avatarUrl,
    required this.name,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 80,
                height: 80,
                decoration: BoxDecoration(
                  color: SahoolTheme.primary.withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: avatarUrl != null
                    ? ClipOval(
                        child: CachedNetworkImage(
                          imageUrl: avatarUrl!,
                          fit: BoxFit.cover,
                          errorWidget: (_, __, ___) => _buildPlaceholder(),
                        ),
                      )
                    : _buildPlaceholder(),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      'الصورة الشخصية',
                      style: TextStyle(
                        fontSize: 15,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'اضغط لتغيير الصورة',
                      style: TextStyle(
                        fontSize: 13,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              const Icon(Icons.camera_alt_rounded, color: SahoolTheme.primary),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Center(
      child: Text(
        name.isNotEmpty ? name[0].toUpperCase() : '?',
        style: const TextStyle(
          fontSize: 32,
          fontWeight: FontWeight.bold,
          color: SahoolTheme.primary,
        ),
      ),
    );
  }
}

/// Membership Tile
class _MembershipTile extends StatelessWidget {
  final String tier;

  const _MembershipTile({required this.tier});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: _getTierColors(),
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        children: [
          Icon(_getTierIcon(), color: Colors.white, size: 32),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'الباقة الحالية',
                  style: TextStyle(
                    color: Colors.white70,
                    fontSize: 12,
                  ),
                ),
                Text(
                  tier,
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  List<Color> _getTierColors() {
    switch (tier.toLowerCase()) {
      case 'enterprise':
      case 'مؤسسي':
        return [Colors.amber[700]!, Colors.amber[900]!];
      case 'professional':
      case 'احترافي':
        return [Colors.blue[600]!, Colors.blue[900]!];
      default:
        return [SahoolTheme.primary, SahoolTheme.primaryDark];
    }
  }

  IconData _getTierIcon() {
    switch (tier.toLowerCase()) {
      case 'enterprise':
      case 'مؤسسي':
        return Icons.diamond;
      case 'professional':
      case 'احترافي':
        return Icons.workspace_premium;
      default:
        return Icons.stars;
    }
  }
}

/// Session Tile
class _SessionTile extends StatelessWidget {
  final String device;
  final String location;
  final String lastActive;
  final bool isCurrent;

  const _SessionTile({
    required this.device,
    required this.location,
    required this.lastActive,
    this.isCurrent = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Container(
        width: 44,
        height: 44,
        decoration: BoxDecoration(
          color: isCurrent
              ? SahoolTheme.success.withOpacity(0.1)
              : Colors.grey.withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Icon(
          Icons.phone_android,
          color: isCurrent ? SahoolTheme.success : Colors.grey,
        ),
      ),
      title: Row(
        children: [
          Text(device),
          if (isCurrent) ...[
            const SizedBox(width: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: SahoolTheme.success.withOpacity(0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Text(
                'الحالي',
                style: TextStyle(
                  fontSize: 10,
                  color: SahoolTheme.success,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ],
      ),
      subtitle: Text('$location - $lastActive'),
      trailing: isCurrent
          ? null
          : IconButton(
              icon: const Icon(Icons.logout, color: SahoolTheme.error),
              onPressed: () {},
            ),
    );
  }
}

/// Plan Card
class _PlanCard extends StatelessWidget {
  final String name;
  final String price;
  final List<String> features;
  final bool isCurrentPlan;
  final bool isRecommended;

  const _PlanCard({
    required this.name,
    required this.price,
    required this.features,
    this.isCurrentPlan = false,
    this.isRecommended = false,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        border: Border.all(
          color: isRecommended
              ? SahoolTheme.primary
              : Colors.grey.withOpacity(0.3),
          width: isRecommended ? 2 : 1,
        ),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Column(
        children: [
          if (isRecommended)
            Container(
              width: double.infinity,
              padding: const EdgeInsets.symmetric(vertical: 4),
              decoration: const BoxDecoration(
                color: SahoolTheme.primary,
                borderRadius: BorderRadius.vertical(top: Radius.circular(14)),
              ),
              child: const Text(
                'الأكثر شعبية',
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: Colors.white,
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
              ),
            ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      name,
                      style: const TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    Text(
                      price,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: SahoolTheme.primary,
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                ...features.map((f) => Padding(
                      padding: const EdgeInsets.only(bottom: 6),
                      child: Row(
                        children: [
                          const Icon(
                            Icons.check_circle,
                            size: 16,
                            color: SahoolTheme.success,
                          ),
                          const SizedBox(width: 8),
                          Text(f, style: const TextStyle(fontSize: 13)),
                        ],
                      ),
                    )),
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: isCurrentPlan
                      ? const OutlinedButton(
                          onPressed: null,
                          child: Text('الباقة الحالية'),
                        )
                      : ElevatedButton(
                          onPressed: () {},
                          child: const Text('ترقية'),
                        ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
