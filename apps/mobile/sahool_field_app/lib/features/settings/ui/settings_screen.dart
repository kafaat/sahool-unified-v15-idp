import 'package:flutter/material.dart';
import '../../../core/theme/sahool_pro_theme.dart';

/// شاشة الإعدادات - تحكم كامل في المزامنة وتنزيل الخرائط
class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _backgroundSync = true;
  bool _dataSaverMode = false;
  String _selectedLanguage = 'العربية';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("الإعدادات"),
        backgroundColor: Colors.white,
        foregroundColor: SahoolProColors.deepJungle,
        elevation: 1,
      ),
      body: ListView(
        children: [
          // قسم المزامنة
          _buildSectionHeader("المزامنة والشبكة"),
          _SyncSettingTile(
            icon: Icons.sync,
            iconColor: SahoolProColors.johnGreen,
            title: "المزامنة في الخلفية",
            subtitle: _backgroundSync ? "مفعل - كل 15 دقيقة" : "معطل",
            value: _backgroundSync,
            onChanged: (v) => setState(() => _backgroundSync = v),
          ),
          _SyncSettingTile(
            icon: Icons.wifi_off,
            iconColor: SahoolProColors.tractorYellow,
            title: "وضع توفير البيانات",
            subtitle: "مزامنة الصور عبر WiFi فقط",
            value: _dataSaverMode,
            onChanged: (v) => setState(() => _dataSaverMode = v),
          ),

          // قسم حالة المزامنة
          _buildSectionHeader("حالة البيانات"),
          const _SyncStatusTile(
            title: "آخر مزامنة",
            value: "منذ 5 دقائق",
            icon: Icons.check_circle,
            iconColor: SahoolProColors.johnGreen,
          ),
          const _SyncStatusTile(
            title: "عمليات معلقة",
            value: "0 عمليات",
            icon: Icons.pending,
            iconColor: Colors.grey,
          ),

          // قسم الخرائط
          _buildSectionHeader("الخرائط (Offline)"),
          const _MapDownloadTile(
            regionName: "صنعاء وضواحيها",
            size: "150 MB",
            isDownloaded: true,
          ),
          const _MapDownloadTile(
            regionName: "إب وتعز",
            size: "120 MB",
            isDownloaded: false,
          ),
          ListTile(
            leading: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: SahoolProColors.johnGreen.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.download, color: SahoolProColors.johnGreen),
            ),
            title: const Text("تنزيل منطقة جديدة"),
            trailing: const Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () => _showRegionDownloadSheet(context),
          ),

          // قسم التخزين
          _buildSectionHeader("التخزين"),
          const _StorageInfoTile(),

          // قسم الحساب
          _buildSectionHeader("الحساب"),
          ListTile(
            leading: const Icon(Icons.language),
            title: const Text("اللغة / Language"),
            trailing: Text(
              _selectedLanguage,
              style: const TextStyle(color: Colors.grey),
            ),
            onTap: () => _showLanguageDialog(context),
          ),
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text("حول التطبيق"),
            subtitle: const Text("الإصدار 15.3.3"),
            onTap: () {},
          ),
          const SizedBox(height: 16),
          ListTile(
            leading: const Icon(Icons.logout, color: SahoolProColors.alertRed),
            title: const Text(
              "تسجيل الخروج",
              style: TextStyle(color: SahoolProColors.alertRed),
            ),
            onTap: () => _showLogoutConfirmation(context),
          ),
          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 24, 16, 8),
      child: Text(
        title,
        style: const TextStyle(
          fontWeight: FontWeight.bold,
          color: SahoolProColors.johnGreen,
          fontSize: 14,
        ),
      ),
    );
  }

  void _showRegionDownloadSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => const _RegionDownloadSheet(),
    );
  }

  void _showLanguageDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("اختر اللغة"),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            _LanguageOption(
              language: "العربية",
              isSelected: _selectedLanguage == 'العربية',
              onTap: () {
                setState(() => _selectedLanguage = 'العربية');
                Navigator.pop(context);
              },
            ),
            _LanguageOption(
              language: "English",
              isSelected: _selectedLanguage == 'English',
              onTap: () {
                setState(() => _selectedLanguage = 'English');
                Navigator.pop(context);
              },
            ),
          ],
        ),
      ),
    );
  }

  void _showLogoutConfirmation(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text("تسجيل الخروج"),
        content: const Text(
          "هل أنت متأكد من تسجيل الخروج؟\nسيتم حذف البيانات غير المتزامنة.",
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text("إلغاء"),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              Navigator.pushReplacementNamed(context, '/login');
            },
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolProColors.alertRed,
            ),
            child: const Text("تسجيل الخروج"),
          ),
        ],
      ),
    );
  }
}

class _SyncSettingTile extends StatelessWidget {
  final IconData icon;
  final Color iconColor;
  final String title;
  final String subtitle;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SyncSettingTile({
    required this.icon,
    required this.iconColor,
    required this.title,
    required this.subtitle,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: iconColor.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Icon(icon, color: iconColor),
      ),
      title: Text(title),
      subtitle: Text(subtitle),
      trailing: Switch(
        value: value,
        onChanged: onChanged,
        activeColor: SahoolProColors.johnGreen,
      ),
    );
  }
}

class _SyncStatusTile extends StatelessWidget {
  final String title;
  final String value;
  final IconData icon;
  final Color iconColor;

  const _SyncStatusTile({
    required this.title,
    required this.value,
    required this.icon,
    required this.iconColor,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: iconColor),
      title: Text(title),
      trailing: Text(
        value,
        style: TextStyle(
          color: Colors.grey[600],
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}

class _MapDownloadTile extends StatelessWidget {
  final String regionName;
  final String size;
  final bool isDownloaded;

  const _MapDownloadTile({
    required this.regionName,
    required this.size,
    required this.isDownloaded,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: Colors.blue.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: const Icon(Icons.map, color: Colors.blue),
      ),
      title: Text(regionName),
      subtitle: Text(size),
      trailing: isDownloaded
          ? const Icon(Icons.check_circle, color: SahoolProColors.johnGreen)
          : OutlinedButton(
              onPressed: () {},
              child: const Text("تنزيل"),
            ),
    );
  }
}

class _StorageInfoTile extends StatelessWidget {
  const _StorageInfoTile();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text("المستخدم: 320 MB"),
              Text(
                "المتاح: 2.1 GB",
                style: TextStyle(color: Colors.grey[600]),
              ),
            ],
          ),
          const SizedBox(height: 8),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: 0.15,
              backgroundColor: Colors.grey[200],
              valueColor: const AlwaysStoppedAnimation<Color>(
                SahoolProColors.johnGreen,
              ),
              minHeight: 8,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _StorageChip(label: "خرائط", size: "150 MB", color: Colors.blue),
              const SizedBox(width: 8),
              _StorageChip(label: "صور", size: "100 MB", color: Colors.orange),
              const SizedBox(width: 8),
              _StorageChip(label: "بيانات", size: "70 MB", color: Colors.green),
            ],
          ),
        ],
      ),
    );
  }
}

class _StorageChip extends StatelessWidget {
  final String label;
  final String size;
  final Color color;

  const _StorageChip({
    required this.label,
    required this.size,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 4),
          Text(
            "$label: $size",
            style: TextStyle(fontSize: 12, color: color),
          ),
        ],
      ),
    );
  }
}

class _RegionDownloadSheet extends StatelessWidget {
  const _RegionDownloadSheet();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            "تنزيل منطقة جديدة",
            style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          const Text(
            "حدد المنطقة على الخريطة أو اختر من القائمة:",
            style: TextStyle(color: Colors.grey),
          ),
          const SizedBox(height: 16),
          ListTile(
            leading: const Icon(Icons.location_on),
            title: const Text("الحديدة"),
            subtitle: const Text("~80 MB"),
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.location_on),
            title: const Text("عدن"),
            subtitle: const Text("~90 MB"),
            onTap: () => Navigator.pop(context),
          ),
          ListTile(
            leading: const Icon(Icons.location_on),
            title: const Text("مأرب"),
            subtitle: const Text("~60 MB"),
            onTap: () => Navigator.pop(context),
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: () => Navigator.pop(context),
              icon: const Icon(Icons.map),
              label: const Text("تحديد على الخريطة"),
            ),
          ),
        ],
      ),
    );
  }
}

class _LanguageOption extends StatelessWidget {
  final String language;
  final bool isSelected;
  final VoidCallback onTap;

  const _LanguageOption({
    required this.language,
    required this.isSelected,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      title: Text(language),
      trailing: isSelected
          ? const Icon(Icons.check, color: SahoolProColors.johnGreen)
          : null,
      onTap: onTap,
    );
  }
}
